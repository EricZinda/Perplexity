import contextvars
import sys


class ExecutionContext(object):
    def __init__(self, vocabulary):
        self.vocabulary = vocabulary
        self._error = None
        self._error_predication_index = -1
        self._predication_index = -1

    def __enter__(self):
        self.old_context_token = set_execution_context(self)

    def __exit__(self, exc_type, exc_val, exc_tb):
        reset_execution_context(self.old_context_token)

    def solve_mrs_tree(self, state, mrs):
        with self:
            self._error = None
            self._error_predication_index = -1
            self._predication_index = -1

            yield from self.call(state.set_x("tree", mrs), mrs["Tree"])

    def call(self, state, term):
        # Keep track of how deep in the tree this
        # predication is
        last_predication_index = self._predication_index
        self._predication_index += 1

        # If "term" is an empty list, we have solved all
        # predications in the conjunction, return the final answer.
        # "len()" is a built-in Python function that returns the
        # length of a list
        if len(term) == 0:
            yield state
        else:
            # See if the first thing in the list is actually a list
            # like [["_large_a_1", "e1", "x1"], ["_file_n_of", "x1"]]
            # If so, we have a conjunction
            if isinstance(term[0], list):
                # This is a list of predications, so they should
                # treated as a conjunction.
                # Call each one and pass the state it returns
                # to the next one, recursively
                for nextState in self.call(state, term[0]):
                    # Note the [1:] syntax which means "return a list
                    # of everything but the first item"
                    yield from self.call(nextState, term[1:])

            else:
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
        print(f"{self._predication_index}: {predication[0]}")
        # The [0] syntax returns the first item in a list
        predication_name = predication[0]

        # The [1:] syntax returns a new list that starts from
        # the first item and goes until the end of the list
        predication_args = predication[1:]

        # Look up the actual Python module and
        # function name given a string like "folder_n_of".
        # "vocabulary.Predication" returns a two-item list,
        # where item[0] is the module and item[1] is the function
        module_function = self.vocabulary.predication(predication_name)

        # sys.modules[] is a built-in Python list that allows you
        # to access actual Python Modules given a string name
        module = sys.modules[module_function[0]]

        # Functions are modeled as properties of modules in Python
        # and getattr() allows you to retrieve a property.
        # So: this is how we get the "function pointer" to the
        # predication function we wrote in Python
        function = getattr(module, module_function[1])

        # [list] + [list] will return a new, combined list
        # in Python. This is how we add the state object
        # onto the front of the argument list
        function_args = [state] + predication_args

        # You call a function "pointer" and pass it arguments
        # that are a list by using "function(*function_args)"
        # So: this is actually calling our function (which
        # returns an iterator and thus we can iterate over it)
        for next_state in function(*function_args):
            yield next_state

    def report_error(self, error, force=False):
        if force or self._error_predication_index < self._predication_index:
            self._error = error
            self._error_predication_index = self._predication_index

    def error(self):
        return [self._error_predication_index, self._error]


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
