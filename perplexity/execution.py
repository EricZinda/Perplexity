import contextvars
import logging
import sys
import perplexity.tree
from perplexity.utilities import sentence_force


# Allows code to throw an exception that should get converted
# to a user visible message
class MessageException(Exception):
    def __init__(self, message_name, message_args):
        self.message_name = message_name
        self.message_args = message_args

    def message_object(self):
        return [self.message_name] + self.message_args


class ExecutionContext(object):
    def __init__(self, vocabulary):
        self.vocabulary = vocabulary
        self._error = None
        self._error_predication_index = -1
        self._error_was_forced = False
        self._predication_index = -1
        self._predication = None
        self._phrase_type = None
        self._variable_execution_data = {}
        self.tree_info = None
        self._variable_metadata = None

    def __enter__(self):
        self.old_context_token = set_execution_context(self)

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.old_context_token is not None:
            reset_execution_context(self.old_context_token)
            self.old_context_token = None

    def solve_mrs_tree(self, state, tree_info):
        with self:
            self.clear_error()
            self._predication_index = 0
            self._phrase_type = sentence_force(tree_info["Variables"])
            self.tree_info = tree_info
            self.gather_tree_metadata()

            yield from self.call(state.set_x("tree", (tree_info, ), False), tree_info["Tree"])

    def gather_tree_metadata(self):
        self._variable_metadata = perplexity.tree.gather_predication_metadata(self.vocabulary, self.tree_info)

    def call(self, state, term, normalize=False):
        # See if the term is actually a list
        # If so, we have a conjunction
        if isinstance(term, list):
            # If "term" is an empty list, we have solved all
            # predications in the conjunction, return the final answer.
            # "len()" is a built-in Python function that returns the
            # length of a list
            if len(term) == 0:
                yield state

            else:
                # This is a list of predications, so they should
                # treated as a conjunction.
                # Call each one and pass the state it returns
                # to the next one, recursively
                for nextState in self.call(state, term[0], normalize):
                    # Note the [1:] syntax which means "return a list
                    # of everything but the first item"
                    yield from self.call(nextState, term[1:], normalize)

        else:
            # Keep track of how deep in the tree this
            # predication is
            last_predication_index = self._predication_index
            last_predication = self._predication
            self._predication_index = term.index
            self._predication = term

            # The first thing in the list was not a list
            # so we assume it is just a term like
            # ["_large_a_1", "e1", "x1"]
            # evaluate it using CallPredication
            yield from self._call_predication(state, term, normalize)

            # Restore it since we are recursing
            self._predication_index = last_predication_index
            self._predication = last_predication

    # Do not use directly.
    # Use Call() instead so that the predication index is set properly
    # The format we're using is:
    # ["folder_n_of", "x1"]
    #   The first item is the predication name
    #   The rest of the items are the arguments
    def _call_predication(self, state, predication, normalize=False):
        if logger.isEnabledFor(logging.DEBUG):
            logger.debug(f"call {self._predication_index}: {predication}({str(state)}) [{self._phrase_type}]")

        bindings = []
        for arg_index in range(0, len(predication.args)):
            if predication.arg_types[arg_index] in ["c", "h"]:
                bindings.append(predication.args[arg_index])

            else:
                bindings.append(state.get_binding(predication.args[arg_index]))

        # [list] + [list] will return a new, combined list
        # in Python. This is how we add the state object
        # onto the front of the argument list
        function_args = [state] + bindings

        # Look up the actual Python module and
        # function name given a string like "folder_n_of".
        # "vocabulary.Predication" returns a two-item list,
        # where item[0] is the module and item[1] is the function
        for module_function in self.vocabulary.predications(predication.name,
                                                            predication.arg_types,
                                                            self._phrase_type if normalize is False else "norm"):
            # sys.modules[] is a built-in Python list that allows you
            # to access actual Python Modules given a string name
            module = sys.modules[module_function[0]]

            # Functions are modeled as properties of modules in Python
            # and getattr() allows you to retrieve a property.
            # So: this is how we get the "function pointer" to the
            # predication function we wrote in Python
            function = getattr(module, module_function[1])

            # See if the system wants us to tack any arguments to the front
            if module_function[2] is not None:
                function_args = module_function[2] + function_args

            # If a MessageException happens during execution,
            # convert it to an error
            try:
                # You call a function "pointer" and pass it arguments
                # that are a list by using "function(*function_args)"
                # So: this is actually calling our function (which
                # returns an iterator and thus we can iterate over it)
                success = False
                for next_state in function(*function_args):
                    success = True
                    yield next_state

            except MessageException as error:
                self.report_error(error.message_object())

            # If an implementation works, don't call any others
            if success:
                break

    # Replace scopal arguments with an "h" and simply
    # return the others
    def arg_types_from_call(self, predication):
        arg_types = []
        for arg_index in range(0, len(predication.args)):
            if predication.arg_names is not None:
                arg_name = predication.arg_names[arg_index]

            arg = predication.args[arg_index]
            if arg_name is not None and arg_name == "CARG":
                arg_types.append("c")
            else:
                if isinstance(arg, str):
                    arg_types.append(arg[0])
                else:
                    arg_types.append("h")

        return arg_types

    def clear_error(self):
        self._error = None
        self._error_was_forced = False
        self._error_predication_index = -1

    def report_error_for_index(self, predication_index, error, force=False):
        if force or (not self._error_was_forced and self._error_predication_index < predication_index):
            self._error = error
            self._error_predication_index = predication_index
            if force:
                self._error_was_forced = True

    def report_error(self, error, force=False):
        self.report_error_for_index(self._predication_index, error, force)

    def error(self):
        return [self._error_predication_index, self._error]

    def current_predication_index(self):
        return self._predication_index

    def current_predication(self):
        return self._predication

    def set_variable_execution_data(self, variable_name, key, value):
        if variable_name not in self._variable_execution_data:
            self._variable_execution_data[variable_name] = {}

        self._variable_execution_data[variable_name][key] = value

    def get_variable_execution_data(self, variable_name):
        return self._variable_execution_data.get(variable_name, {})

    def get_variable_metadata(self, variable_name):
        return self._variable_metadata.get(variable_name, {})


# ContextVars is a thread-safe way to set the execution context
# used by the predications
_execution_context = contextvars.ContextVar('Execution Context')


# Returns a token that can be used by
# reset_execution_context to reset to what it was
# before
def set_execution_context(new_context):
    global _execution_context
    return _execution_context.set(new_context)


# Get the token from set_execution_context
def reset_execution_context(old_context_token):
    global _execution_context
    return _execution_context.reset(old_context_token)


def execution_context():
    return _execution_context.get()


# Helpers used by predications just to make the code easier to read
# so they don't all have to say execution_context().call(*args, **kwargs)
def call(*args, **kwargs):
    yield from execution_context().call(*args, **kwargs)


def report_error(error, force=False):
    execution_context().report_error(error, force)


def set_variable_execution_data(variable_name, key, value):
    execution_context().set_variable_execution_data(variable_name, key, value)


def get_variable_execution_data(variable_name):
    return execution_context().get_variable_execution_data(variable_name)


def get_variable_metadata(variable_name):
    return execution_context().get_variable_metadata(variable_name)


logger = logging.getLogger('Execution')
pipeline_logger = logging.getLogger('Pipeline')
