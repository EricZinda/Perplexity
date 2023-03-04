import contextvars
import copy
import itertools
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


# First figure out the order of the "tree of cardinals" from child to parent
# The order of them is simply the number of ids that compose an individual answer_set_id
# Since these are built like 0:4:5.
# It won't change for the answers so we can just do it on the first one
# TODO: For now we are assuming it is a straight line, not a tree
def cardinal_tree(solutions, reverse=True):
    tree_info = solutions[0].get_binding("tree")
    variables = tree_info.value["Variables"]
    cardinal_list = []
    for variable_name in variables:
        binding = solutions[0].get_binding(variable_name)
        if binding.variable.variable_set_id is not None:
            cardinal_id_parts = binding.variable.variable_set_id.split(":")
            cardinal_list.append((len(cardinal_id_parts), variable_name))

    cardinal_list.sort(reverse=reverse)
    return [item[1] for item in cardinal_list]



# If you say: "which two files are in two folders?" and we consider the parse
# in the order: dist(folder), dist(file):
# - the engine might pick a folder cardinal group that contains two variable sets of 1 (since it is dist).
# - then it will list all combinations of two files that are in each as alternatives
#
# If there are a bunch of these, a human might answer "there are a lot of these" and require the person to say "what are all the groups of two files that are in two folders"
# Or we could say:
# in folder 1 separately are: (1 and 2), (3 and 4), ...
# in folder 2 separately are: (5 and 6), ....
# in folder 1 together are: ...
# def cardinal_tree_to_english(cardinal_order, cardinal_tree, variable):
#     this_variable = cardinal_order[0]
#     response = ""
#     for type in ["dist", "coll"]:
#         if type in cardinal_tree:
#             type_description = "together" if type == "coll" else "separately"
#             for cardinal_group in cardinal_tree[type].items():
#                 for answer_set_info in cardinal_group[1].values():
#                     answer_set_items = [str(item) for item in answer_set_info["VariableSet"].values()]
#                     answer = ", ".join(answer_set_items) + f" {type_description}"
#                     if variable == this_variable:
#                         response += answer + "\n"
#                     else:
#                         response += answer + " -> " + cardinal_tree_to_english(cardinal_order[1:], answer_set_info["ChildGroups"], variable)
#
#     return response


# Prints the English for a single answer.Takes a list of cardinal groups
# Every cardinal group level needs to print at a new indent
# Even variableset needs to print on its own line at that indent
# They all need descriptors
# Need blanks between variable sets
# Stop recuring after we hit the cardinal that contains the variable we are looking for
def cardinal_answer_to_english(variable, cardinal_variables, cardinal_answer_list, indent_level=0):
    indent = " " * indent_level
    cardinal_group_answer = []
    for cardinal_group in cardinal_answer_list:
        # If this is coll, print on same line and say together
        type_description = " together" if cardinal_group["Type"] == "coll" else ""
        variable_set_answer = []
        for variable_set_info in cardinal_group["VariableSets"]:
            variable_set_items = [str(item) for item in variable_set_info["VariableSetItems"].values()]
            answer = indent + ", ".join(variable_set_items) + f'{type_description}\n'
            if len(variable_set_info["ChildGroups"]) > 0 and variable != cardinal_variables[0]:
                answer += cardinal_answer_to_english(variable, cardinal_variables[1:], variable_set_info["ChildGroups"], indent_level + 5) + "\n"

            variable_set_answer.append(answer)
        cardinal_group_answer.append("".join(variable_set_answer))
    return ("\n" if cardinal_answer_list[0]["Type"] == "dist" else "").join(cardinal_group_answer)

# A parent sends a *variable set* to a child,
# and the child solves it against that child's *cardinal group*.
# So, as we consider each child as we recurse down the child chain,
# we group the whole child cardinal group since that whole child cardinal group (*not* the child variable set)
# is part of the answer for the parent *variable set*.
#
#   Build a tree with the first cardinal at the root and the childmost cardinal at the leaves
#   that looks like: Group->coll/dist->answerset->group->coll/dist->answerset ...
# Algorithm:
#   Loop through the solutions and the variables in tree order
#       Put each variable in the right spot in the tree using the binding
#           information of the variable to know which
#           cardinal group/variable set/variable set item it is
def cardinal_answer_list(solutions):
    cardinal_order = cardinal_tree(solutions, reverse=False)
    answer_tree = {"VariableOrder": cardinal_order}
    for solution in solutions:
        add_solution_to_tree(cardinal_order, answer_tree, solution)

    for variation in itertools.product(["coll", "dist"], repeat=len(cardinal_order)):
        answer = specific_coll_dist_variation(answer_tree, variation)
        if answer is not None:
            yield {"CardinalVariables": cardinal_order, "Answer": answer}


# The cardinal tree starts like this:
# coll/dist->Group->answerset->coll/dist->Group->answerset ...
#
# We just want to flatten out the coll/dist nodes.  Each cardinal group for each variable is a new answer
#
#
# Group->answerset->Group->answerset ...

# We walk the cardinal tree and flatten it into individual cardinal solutions by returning every different combination
# of coll/dist nodes for the tree.
# So the tree of nodes:
# answerset     ->  coll    ->  group1  ->  answerset1   ->  coll    ->  group1  ->
#       -> coll -> dist
#       -> dist -> coll
#       -> coll -> coll
#
# answerset ->  group1  ->  answerset1  ->  group1  ->

# Becomes a list of nodes:
# coll  -> dist -> dist
# coll  -> coll -> dist
# coll  -> dist -> coll
# coll  -> coll -> coll
#
# Each node is a list of *alternatives* that were generated for that variable
# at that point in the query. Just like "which rock (x1) is in every cave (x2)" would generate
# a list of alternative assignments to x1 and x2 for every rock in every cave.
#
# returns Group(dist/coll)->variableset
# returns Group(dist/coll)->variableset

# At each node, we ask the child to return either a coll or
# this has two return two groups
# Takes an answer set and divides its child cardinal_groups into dist and coll and returns both
# We have to yield at the very end to get different answers
# All we are doing is skipping the dist/coll section of the tree
# Ends up with listofcardinalgroups(cardinalgroup(), cardinalgroup(), ...)
#
# The answer is a flat list, with one item for each cardinal in the list.
# Go through the whole solution N times.  Each time pick a  combinations of dist and coll for all the nodes
def specific_coll_dist_variation(answer_set_node, variation_list):
    coll_or_dist_type = variation_list[0]
    cardinal_groups = []
    if coll_or_dist_type not in answer_set_node:
        return None

    for cardinal_group in answer_set_node[coll_or_dist_type].values():
        new_cardinal_group = {"Type": coll_or_dist_type, "VariableSets": []}
        for variable_set in cardinal_group.values():
            if len(variation_list) > 1:
                new_child_cardinal_groups = specific_coll_dist_variation(variable_set["ChildGroups"], variation_list[1:])
                if new_child_cardinal_groups is None:
                    return None
                else:
                    new_cardinal_group["VariableSets"].append({"VariableSetItems": variable_set["VariableSet"], "ChildGroups": new_child_cardinal_groups})
            else:
                new_cardinal_group["VariableSets"].append({"VariableSetItems": variable_set["VariableSet"], "ChildGroups": []})

        cardinal_groups.append(new_cardinal_group)

    return cardinal_groups


def add_solution_to_tree(cardinal_order, answer_tree, solution):
    variable = cardinal_order[0]
    binding = solution.get_binding(variable)
    type_key = "coll" if binding.variable.is_collective else "dist"
    group_key = str(binding.variable.cardinal_group_id)
    variable_set_key = binding.variable.variable_set_id

    if type_key not in answer_tree:
        answer_tree[type_key] = {}

    if group_key not in answer_tree[type_key]:
        answer_tree[type_key][group_key] = {}

    if variable_set_key not in answer_tree[type_key][group_key]:
        answer_tree[type_key][group_key][variable_set_key] = {"ChildGroups": {}, "VariableSet": {}}

    # Use the variable_set_item_id to make sure we don't get duplicates
    answer_tree[type_key][group_key][variable_set_key]["VariableSet"][binding.variable.variable_set_item_id] = binding.value

    if len(cardinal_order) == 1:
        return
    else:
        add_solution_to_tree(cardinal_order[1:], answer_tree[type_key][group_key][variable_set_key]["ChildGroups"], solution)


# A cardinal picks a cardinal group id for the set of answers it is doing (dist or coll) and sticks with it for that dist or coll
# The algorithm is: start with the child, each group of the same cardinal group id of the deepest child is a single solution
# This routine groups all the answers by unique cardinal groups
def unique_cardinal_group_sets(solutions):
    # First figure out the order of the "tree of cardinals" from child to parent
    cardinal_order = cardinal_tree(solutions)


    # If all solutions (dist and coll) for all cardinals succeeded,
    # then there would be a dist and coll cardinal group for every cardinal variable.
    # And there could be multiple if there were more than one answer for a given answer set
    # It acts like a binary number: all answers that have the same number go together. Build a key like "coll, dist, coll"
    # and use that to group unique answers
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


# Build a dictionary:
#   key = variables that are cardinals
#   value = list of values in a single cardinal group id
#
# Recursively group the next variable in the cardinal order into a list of unique cardinal group answers for that variable
# Attach that list of answers to the answers_orig dict, keyed by the variable, and recurse with the next one
# At the very end, you have a dict that contains the c of lists that is the cardinal group for each cardinal in
# a single solution. Return that.
def group_answer_sets2(cardinal_order, solutions, answers_orig):
    if len(cardinal_order) == 0:
        yield answers_orig

    else:
        current_variable = cardinal_order[0]

        # First group the cardinal groups that exist for this variable
        cardinal_groups = {}
        for solution_index in range(0, len(solutions)):
            solution = solutions[solution_index]
            binding = solution.get_binding(current_variable)
            cardinal_group_id = binding.variable.cardinal_group_id
            if cardinal_group_id not in cardinal_groups:
                cardinal_groups[cardinal_group_id] = []

            cardinal_groups[cardinal_group_id].append((solution, binding))

        # Then recurse on each cardinal group sending only the *unique* values for this variable
        # but including *all* the solutions
        for solutions_with_binding in cardinal_groups.values():
            solutions = [item[0] for item in solutions_with_binding]

            # Get rid of duplicate values for this variable
            # by using a key of variable_set_id + variable_set_id_item_id
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
    for answer_set in unique_cardinal_group_sets(solutions):
        yield [answer[variable] for answer in answer_set]


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
