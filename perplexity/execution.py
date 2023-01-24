import contextvars
import logging
import sys
from perplexity.utilities import sentence_force


class ExecutionContext(object):
    def __init__(self, vocabulary):
        self.vocabulary = vocabulary
        self._error = None
        self._error_predication_index = -1
        self._predication_index = -1
        self._phrase_type = None

    def __enter__(self):
        self.old_context_token = set_execution_context(self)

    def __exit__(self, exc_type, exc_val, exc_tb):
        reset_execution_context(self.old_context_token)

    def solve_mrs_tree(self, state, tree_info):
        with self:
            self._error = None
            self._error_predication_index = -1
            self._predication_index = 0
            self._phrase_type = sentence_force(tree_info["Variables"])
            yield from self.call(state.set_x("tree", tree_info), tree_info["Tree"])

    def call(self, state, term):
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
                for nextState in self.call(state, term[0]):
                    # Note the [1:] syntax which means "return a list
                    # of everything but the first item"
                    yield from self.call(nextState, term[1:])

        else:
            # Keep track of how deep in the tree this
            # predication is
            last_predication_index = self._predication_index
            self._predication_index = term.index

            # The first thing in the list was not a list
            # so we assume it is just a term like
            # ["_large_a_1", "e1", "x1"]
            # evaluate it using CallPredication
            yield from self._call_predication(state, term)

            # Restore it since we are recursing
            self._predication_index = last_predication_index

    # Do not use directly.
    # Use Call() instead so that the predication index is set properly
    # The format we're using is:
    # ["folder_n_of", "x1"]
    #   The first item is the predication name
    #   The rest of the items are the arguments
    def _call_predication(self, state, predication):
        logger.debug(f"call {self._predication_index}: {predication}({str(state)}) [{self._phrase_type}]")

        # [list] + [list] will return a new, combined list
        # in Python. This is how we add the state object
        # onto the front of the argument list
        function_args = [state] + predication.args

        # Look up the actual Python module and
        # function name given a string like "folder_n_of".
        # "vocabulary.Predication" returns a two-item list,
        # where item[0] is the module and item[1] is the function
        for module_function in self.vocabulary.predications(predication.name,
                                                            predication.arg_types,
                                                            self._phrase_type):
            # sys.modules[] is a built-in Python list that allows you
            # to access actual Python Modules given a string name
            module = sys.modules[module_function[0]]

            # Functions are modeled as properties of modules in Python
            # and getattr() allows you to retrieve a property.
            # So: this is how we get the "function pointer" to the
            # predication function we wrote in Python
            function = getattr(module, module_function[1])

            # You call a function "pointer" and pass it arguments
            # that are a list by using "function(*function_args)"
            # So: this is actually calling our function (which
            # returns an iterator and thus we can iterate over it)
            success = False
            for next_state in function(*function_args):
                success = True
                yield next_state

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

    def report_error(self, error, force=False):
        if force or self._error_predication_index < self._predication_index:
            self._error = error
            self._error_predication_index = self._predication_index

    def error(self):
        return [self._error_predication_index, self._error]

    def current_predication_index(self):
        return self._predication_index


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


logger = logging.getLogger('Execution')
pipeline_logger = logging.getLogger('Pipeline')
