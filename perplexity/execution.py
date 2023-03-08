import contextvars
import copy
import itertools
import logging
import sys
# Use this form to avoid circular dependency, then use perplexity.cardinals.function() when calling
import perplexity.cardinals
from perplexity.utilities import sentence_force, has_cardinals

# Allows code to throw an exception that should get converted
# to a user visible message
class MessageException(Exception):
    def __init__(self, message_name, message_args):
        self.message_name = message_name
        self.message_args = message_args

    def message_object(self):
        return [self.message_name] + self.message_args


class VariableSetRestart(Exception):
    pass


next_solution_id = 1
next_group_id = 1


def create_solution_id():
    global next_solution_id
    value = next_solution_id
    next_solution_id += 1
    return value


def create_variable_set_cache(variable_set_id, child_is_collective):
    parent_solution = group_context()
    parent_variable_set_id = parent_solution[
        "VariableSetID"] if parent_solution is not None and "VariableSetID" in parent_solution else None

    return {"ChildIsCollective": child_is_collective,
            "ChildCardinals": {},
            "VariableSetID": ((parent_variable_set_id + ":") if parent_variable_set_id is not None else "") + str(
                variable_set_id)}


class ExecutionContext(object):
    def __init__(self, vocabulary):
        self.vocabulary = vocabulary
        self._error = None
        self._error_predication_index = -1
        self._predication_index = -1
        self.phrase_type = None

    def __enter__(self):
        self.old_context_token = set_execution_context(self)

    def __exit__(self, exc_type, exc_val, exc_tb):
        reset_execution_context(self.old_context_token)

    def solve_mrs_tree(self, state, tree_info):
        logger.debug(f"solve MRS {tree_info['Tree']}")

        with self:
            set_group_context(None)
            self._error = None
            self._error_predication_index = -1
            self._predication_index = 0
            self.phrase_type = sentence_force(tree_info["Variables"])

            # To make cardinals work, run this as if it were a distributive cardinal group that has one variable set in it with one element
            # Conveniently, we need to set the state to have the variable "tree" it it, so pretend like this cardinal group is setting that value
            # since cardinal_group_outgoing_solutions will fail if there are no items in the variable set
            root_cardinal_group = perplexity.cardinals.CardinalGroup(is_collective=False, cardinal_group_id=0, cardinal_group_items=[tuple([str(0), [tree_info]])])
            cardinal_group_solutions = perplexity.cardinals.cardinal_group_outgoing_solutions(this_predicate_index=0, state=state, variable_name="tree", h_body=tree_info["Tree"], this_cardinal_group=root_cardinal_group)

            if len(cardinal_group_solutions) > 0:
                # This cardinal group worked
                yield from perplexity.cardinals.yield_all_cardinal_group_solutions(this_predicate_index=0, cardinal_group_id=root_cardinal_group.cardinal_group_id, cardinal_group_solutions=cardinal_group_solutions)

    def call_with_group(self, group, state, term, normalize=False):
        try:
            call_generator = call(state, term, normalize)
            while True:
                try:
                    old_context_token = set_group_context(group)
                    next_state = next(call_generator)
                    reset_group_context(old_context_token)
                    old_context_token = None

                    yield next_state

                except StopIteration:
                    return

        finally:
            if old_context_token is not None:
                reset_group_context(old_context_token)

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
            self._predication_index = term.index

            try:
                # The first thing in the list was not a list
                # so we assume it is just a term like
                # ["_large_a_1", "e1", "x1"]
                # evaluate it using CallPredication
                yield from self._call_predication(state, term, normalize)

            except:
                # Restore it since we are recursing and an exception
                # has removed all forward progress
                self._predication_index = last_predication_index
                raise

    # Do not use directly.
    # Use Call() instead so that the predication index is set properly
    # The format we're using is:
    # ["folder_n_of", "x1"]
    #   The first item is the predication name
    #   The rest of the items are the arguments
    def _call_predication(self, state, predication, normalize=False):
        logger.debug(f"call {self._predication_index}: {predication}({str(state)}) [{self.phrase_type}]")

        dynamic_arg_types = []
        bindings = []
        for arg_index in range(0, len(predication.args)):
            if predication.arg_types[arg_index] in ["c", "h"]:
                bindings.append(predication.args[arg_index])

            else:
                bindings.append(state.get_binding(predication.args[arg_index]))

            arg_type = predication.arg_types[arg_index]
            # THis isn't necessary because we are removing duplicates
            # if arg_type == "x" and state.get_binding(predication.args[arg_index]).variable.is_collective:
            #     dynamic_arg_types.append(arg_type + "_set")
            #
            # else:
            #     dynamic_arg_types.append(arg_type)
            dynamic_arg_types.append(arg_type)

        # [list] + [list] will return a new, combined list
        # in Python. This is how we add the state object
        # onto the front of the argument list
        function_args = [state] + bindings

        # Look up the actual Python module and
        # function name given a string like "folder_n_of".
        # "vocabulary.Predication" returns a two-item list,
        # where item[0] is the module and item[1] is the function
        for module_function in self.vocabulary.predications(predication.name,
                                                            dynamic_arg_types,
                                                            self.phrase_type if normalize is False else "norm"):
            # sys.modules[] is a built-in Python list that allows you
            # to access actual Python Modules given a string name
            module = sys.modules[module_function[0]]

            # Functions are modeled as properties of modules in Python
            # and getattr() allows you to retrieve a property.
            # So: this is how we get the "function pointer" to the
            # predication function we wrote in Python
            function = getattr(module, module_function[1])

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


_group_context = contextvars.ContextVar('Group Context')


def set_group_context(new_context):
    global _group_context
    return _group_context.set(new_context)


# Get the token from set_execution_context
def reset_group_context(old_context_token):
    global _group_context
    return _group_context.reset(old_context_token)


def group_context():
    return _group_context.get()


# Helpers used by predications just to make the code easier to read
# so they don't all have to say execution_context().call(*args, **kwargs)
def call(*args, **kwargs):
    yield from execution_context().call(*args, **kwargs)


def call_with_group(*args, **kwargs):
    yield from execution_context().call_with_group(*args, **kwargs)


def report_error(error, force=False):
    execution_context().report_error(error, force)


logger = logging.getLogger('Execution')
pipeline_logger = logging.getLogger('Pipeline')
