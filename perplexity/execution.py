import contextvars
import copy
import logging
import sys
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
    parent_variable_set_id = parent_solution["VariableSetID"] if parent_solution is not None and "VariableSetID" in parent_solution else None

    return {"ChildIsCollective": child_is_collective,
            "ChildCardinals": {},
            "VariableSetID": ((parent_variable_set_id + ":") if parent_variable_set_id is not None else "") + str(variable_set_id)}


def cardinal_tree(solutions):
    # First figure out the order of the "tree of cardinals" from child to parent
    # The order of them is simply the number of ids in the cardinal_group_id
    # It won't change for the answers so we can just do it on the first one
    # TODO: For now we are assuming it is a straight line, not a tree
    tree_info = solutions[0].get_binding("tree")
    variables = tree_info.value["Variables"]
    cardinal_list = []
    for variable_name in variables:
        binding = solutions[0].get_binding(variable_name)
        if binding.variable.variable_set_id is not None:
            cardinal_id_parts = binding.variable.variable_set_id.split(":")
            cardinal_list.append((len(cardinal_id_parts), variable_name))

    cardinal_list.sort(reverse=True)
    return [item[1] for item in cardinal_list]


# A cardinal picks a solution id for the set of answers it is doing (dist or coll) and sticks with it for that dist or coll
# The algorithm is: start with the child, each group of the same solution id of the deepest child is a single solution
def group_answer_sets(solutions):
    # First figure out the order of the "tree of cardinals" from child to parent
    cardinal_order = cardinal_tree(solutions)

    # If all solutions (dist and coll) for all cardinals succeeded then there would be a dist and coll at each level
    # It acts like a binary number: all answers that have the same number go together
    grouped_answers = {}
    for item in group_answer_sets2(cardinal_order, solutions, {}):
        key = []
        for variable in cardinal_order:
            key.append("coll" if item[variable][0].variable.is_collective else "dist")

        tuple_key = tuple(key)
        if tuple_key not in grouped_answers:
            grouped_answers[tuple_key] = []

        grouped_answers[tuple_key].append(item)

    for grouped_answer in grouped_answers.values():
        yield grouped_answer


def group_answer_sets2(cardinal_order, solutions, answers_orig):
    if len(cardinal_order) == 0:
        yield answers_orig

    else:
        current_variable = cardinal_order[0]

        # First group the cardinal groups
        cardinal_groups = {}
        for solution_index in range(0, len(solutions)):
            solution = solutions[solution_index]
            binding = solution.get_binding(current_variable)
            cardinal_group_id = binding.variable.cardinal_group_id
            if cardinal_group_id not in cardinal_groups:
                cardinal_groups[cardinal_group_id] = []

            cardinal_groups[cardinal_group_id].append((solution, binding))

        # Then recurse on each cardinal group
        for solutions_with_binding in cardinal_groups.values():
            solutions = [item[0] for item in solutions_with_binding]
            # Get rid of duplicates by using a key of variable_set_id + variable_set_id_item_id
            binding_ids = {}
            for solution_with_binding in solutions_with_binding:
                variable_set_id = solution_with_binding[1].variable.variable_set_id
                variable_set_id_item_id = solution_with_binding[1].variable.variable_set_item_id
                binding_ids[str(variable_set_id) + str(variable_set_id_item_id)] = solution_with_binding[1]

            bindings = [item for item in binding_ids.values()]
            is_collective = bindings[0].variable.is_collective

            if is_collective:
                answers = copy.copy(answers_orig)
                answers[current_variable] = bindings
                yield from group_answer_sets2(cardinal_order[1:], solutions, answers)

            else:
                for binding in bindings:
                    answers = copy.copy(answers_orig)
                    answers[current_variable] = [binding]
                    yield from group_answer_sets2(cardinal_order[1:], solutions, answers)


def create_answer_sets_from_variable(variable, solutions):
    for answer_set in group_answer_sets(solutions):
        yield [answer[variable] for answer in answer_set]


# This is only returning a single variable's answers so it doesn't need to deal with trees of answers, just potentially
# single answers and set answers for this variable
# def create_answer_sets_from_variable(variable, solutions):
#     answer_items = {}
#     for solution in solutions:
#         binding = solution.get_binding(variable)
#         if binding.variable.cardinal_id not in answer_items:
#             answer_items[binding.variable.cardinal_id] = []
#
#         answer_items[binding.variable.cardinal_id].append(binding.value)
#
#     if len(answer_items) == 1 and list(answer_items.keys())[0] is None:
#         # These are not sets, just need to deduplicate
#         return deduplicate(list(answer_items.values())[0])
#
#     else:
#         # Now we have all the (potentially duplicate) answers. Deduplicate.
#         final_answer_items = []
#         answer_items_list = list(answer_items.values())
#         for answer1_index in range(0, len(answer_items)):
#             found_duplicate = False
#             for answer2_index in range(answer1_index + 1, len(answer_items)):
#                 answer1_list = answer_items_list[answer1_index]
#                 answer2_list = answer_items_list[answer2_index]
#                 if lists_are_equal(answer1_list, answer2_list):
#                     found_duplicate = True
#                     break
#
#             if not found_duplicate:
#                 final_answer_items.append(answer1_list)
#
#         return final_answer_items


def deduplicate(list1):
    return [v1 for i, v1 in enumerate(list1) if not any((v1 == v2 for v2 in list1[:i]))]


def lists_are_equal(list1, list2):
    if len(list1) != len(list2):
        return False
    else:
        unique_list1 = [v1 for i, v1 in enumerate(list1) if not any((v1 == v2 for v2 in list2))]
        return len(unique_list1) == 0


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
            set_group_context(None)
            self._error = None
            self._error_predication_index = -1
            self._predication_index = 0
            self._phrase_type = sentence_force(tree_info["Variables"])

            for is_collective in [False, True]:
                initial_group = create_variable_set_cache(0, is_collective)
                try:
                    yield from self.call_with_group(initial_group, state.set_x("tree", tree_info), tree_info["Tree"])

                except VariableSetRestart:
                    # Ignore restart exceptions since there is no set we are
                    # generating that can be changed since we are the root
                    pass

                if len(initial_group["ChildCardinals"]) == 0:
                    break

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

            finally:
                # Restore it since we are recursing
                self._predication_index = last_predication_index

    # Do not use directly.
    # Use Call() instead so that the predication index is set properly
    # The format we're using is:
    # ["folder_n_of", "x1"]
    #   The first item is the predication name
    #   The rest of the items are the arguments
    def _call_predication(self, state, predication, normalize=False):
        logger.debug(f"call {self._predication_index}: {predication}({str(state)}) [{self._phrase_type}]")

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
                                                            self._phrase_type if normalize is False else "norm"):
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
