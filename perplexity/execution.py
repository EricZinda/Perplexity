import contextvars
import copy
import logging
import sys
import perplexity.tree
from perplexity.utilities import sentence_force, at_least_one_generator
from perplexity.vocabulary import ValueSize


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
        self._in_scope_initialize_function = None
        self._in_scope_initialize_data = None
        self._in_scope_function = None

    def __enter__(self):
        self.old_context_token = set_execution_context(self)

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.old_context_token is not None:
            reset_execution_context(self.old_context_token)
            self.old_context_token = None

    def resolve_fragment(self, state, tree_node, extra_variables=None, criteria_list=None):
        this_sentence_force = sentence_force(self.tree_info["Variables"])
        new_tree_info = copy.deepcopy(self.tree_info)
        if extra_variables is not None:
            new_tree_info["Variables"].update(extra_variables)

        new_tree_info["Tree"] = tree_node
        new_state = state.set_x("tree", (new_tree_info, ))
        wh_phrase_variable = None
        if this_sentence_force == "ques":
            predication = perplexity.tree.find_predication(self.tree_info["Tree"], "_which_q")
            if predication is not None:
                wh_phrase_variable = predication.args[0]

        solutions = self.call(new_state, tree_node)
        solutions_list = list(solutions)
        pipeline_logger.debug(f"Resolving fragment: {tree_node}")
        # TODO: suspect the interleaving of resolve_fragment() with normal MRS solving is causing a subtle bug since
        #         resolving it all up front doesn't have the bug. Fix that bug and then allow this to stream
        for group in perplexity.solution_groups.solution_groups(self, solutions_list, this_sentence_force, wh_phrase_variable, new_tree_info, all_groups=True, criteria_list=criteria_list):
            solutions = [x for x in group]
            if pipeline_logger.level == logging.DEBUG:
                nl = '\n'
                pipeline_logger.debug(
                    f"Found fragment solution group: {nl + '   ' + (nl + '   ').join([str(s) for s in solutions])}")
            yield solutions

        pipeline_logger.debug(f"Done Resolving fragment: {tree_node}")

    # Needs to be called in a: with ExecutionContext() block
    # so that the execution context is set up properly
    # and maintained while all the solution groups are generated
    def solve_mrs_tree(self, state, tree_info):
        self.clear_error()
        self._predication_index = 0
        self._phrase_type = sentence_force(tree_info["Variables"])
        self.tree_info = tree_info
        self.gather_tree_metadata()
        if self._in_scope_initialize_function is not None:
            self.in_scope_initialize_data = self._in_scope_initialize_function(state)

        for solution in self.call(state.set_x("tree", (tree_info, ), False), tree_info["Tree"]):
            yield solution

        pipeline_logger.debug(f"Error after tree evaluation: {self.get_error_info()}")

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
                # This is a list of predications, so they should be
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

        # Look up the actual Python module and
        # function name given a string like "folder_n_of".
        # "vocabulary.Predication" returns a two-item list,
        # where item[0] is the module and item[1] is the function
        for module_function in self.vocabulary.predications(predication.name,
                                                            predication.arg_types,
                                                            self._phrase_type if normalize is False else "norm"):
            # sys.modules[] is a built-in Python list that allows you
            # to access actual Python Modules given a string name
            module = sys.modules[module_function.module]

            # Functions are modeled as properties of modules in Python
            # and getattr() allows you to retrieve a property.
            # So: this is how we get the "function pointer" to the
            # predication function we wrote in Python
            function = getattr(module, module_function.function)

            # [list] + [list] will return a new, combined list
            # in Python. This is how we add the state object
            # onto the front of the argument list
            function_args = [state] + bindings

            # See if the system wants us to tack any arguments to the front
            if module_function.extra_arg is not None:
                function_args = module_function.extra_arg + function_args

            # If a MessageException happens during execution,
            # convert it to an error
            try:
                # You call a function "pointer" and pass it arguments
                # that are a list by using "function(*function_args)"
                # So: this is actually calling our function (which
                # returns an iterator and thus we can iterate over it)
                for next_state in function(*function_args):
                    tree_lineage_binding = next_state.get_binding("tree_lineage")
                    tree_lineage = "" if tree_lineage_binding.value is None else tree_lineage_binding.value[0]
                    yield next_state.set_x("tree_lineage", (f"{tree_lineage}.{module_function.id}",))

            except MessageException as error:
                self.report_error(error.message_object())

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

    def set_in_scope_function(self, func, initialize_func = None):
        self._in_scope_function = func
        self._in_scope_initialize_function = initialize_func

    # Test if an object is in scope, by default everything is
    def in_scope(self, state, thing):
        if self._in_scope_function is not None:
            return self._in_scope_function(self.in_scope_initialize_data, state, thing)
        else:
            return True

    def get_error_info(self):
        return self._error, self._error_was_forced, self._error_predication_index

    def set_error_info(self, error_info):
        if error_info is not None:
            self._error = error_info[0]
            self._error_was_forced = error_info[1]
            self._error_predication_index = error_info[2]

    def clear_error(self):
        self._error = None
        self._error_was_forced = False
        self._error_predication_index = -1

    def has_not_understood_error(self):
        # System errors that indicate the phrase can't be understood can't be replaced
        # since they aren't indicating a logical failure, they are indicating that the system didn't understand
        # predications like neg() need to know if a branch failed due to a real logical failure or not
        not_understood_failures = ["formNotUnderstood"]
        return self._error is not None and self._error[0] in not_understood_failures

    def report_error_for_index(self, predication_index, error, force=False):
        if not self.has_not_understood_error() and \
                (force or (not self._error_was_forced and self._error_predication_index < predication_index)):
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
        # TODO: This is a hack to enable metadata for eval(). Need to fix it
        return self._variable_metadata.get(variable_name, {"ValueSize": ValueSize.all})


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
