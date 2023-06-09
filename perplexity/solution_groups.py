import copy
import inspect
import logging
import sys
from math import inf

from perplexity.execution import execution_context
from perplexity.plurals import determiner_from_binding, quantifier_from_binding, \
    all_plural_groups_stream, VariableCriteria, GlobalCriteria, plural_groups_stream_initial_stats
from perplexity.tree import gather_quantifier_order, gather_predication_metadata, find_predication_from_introduced
from perplexity.utilities import at_least_one_generator


# Yields solutions in a single solution group
# asks its solution_group_generator to give it more than the initial group
# when necessary
class SingleGroupGenerator(object):
    def __init__(self, group_id, solution_group_generator, group_list):
        self.group_id = group_id
        self.solution_group_generator = solution_group_generator
        self.group_list = group_list
        self.last_yielded_index = -1

    def __iter__(self):
        return self

    def __next__(self):
        if self.last_yielded_index == len(self.group_list) - 1:
            # If no variable has a between(N, inf) constraint,
            # Just stop now and the caller will get a subset solution group for the answer they care about
            # Note that it may not be *minimal*, might be a subset, and might be maximal.
            # If it does have an between(N, inf) constraint, return them all
            if not self.solution_group_generator.variable_has_inf_max:
                raise StopIteration

            # See if we can get more items
            elif not self.solution_group_generator.next_solution_in_group(self.group_id):
                raise StopIteration

        self.last_yielded_index += 1
        return self.group_list[self.last_yielded_index]


# yields a generator that yields solutions in a minimal solution group as quickly as it is found
# but will continue returning solutions until it is maximal if requested. The idea is to make it easy
# to see if there is at least one solution for yes/no questions and propositions (thus the quick minimal solution)
# but allow other types of phrases to get all answers in a group if needed
#
# When a group is yielded from all_plural_groups_stream(), it has an id which is a "lineage"
# If that lineage is just one group away from an existing group, it should be yielded from that group
# Otherwise it should create a new group
#
# A yielded SingleSolutionGroupGenerator will "follow" the first lineage that matches it
class SolutionGroupGenerator(object):
    def __init__(self, all_plural_groups_stream, variable_has_inf_max):
        self.all_plural_groups_stream = all_plural_groups_stream
        self.variable_has_inf_max = variable_has_inf_max
        self.solution_groups = {}
        self.current_solution_group_index = -1
        self.complete = False

    def __iter__(self):
        return self

    def __next__(self):
        self.current_solution_group_index += 1
        if self.current_solution_group_index > len(self.solution_groups) - 1:
            # Caller is asking for the next group and we don't have one yet
            if not self.next_solution_in_group(""):
                self.complete = True
                raise StopIteration

        return list(self.solution_groups.values())[self.current_solution_group_index]

    # Returns true if there is another solution found for group.id == current_id
    # If current_id == "" then returns true if there is a new group created
    def next_solution_in_group(self, current_id):
        while True:
            try:
                next_group, next_id = next(self.all_plural_groups_stream)

            except StopIteration:
                self.complete = True
                return False

            colon_index = next_id.rfind(":")
            if colon_index == -1:
                parent_id = ""
            else:
                parent_id = next_id[:colon_index]

            if next_id in self.solution_groups:
                existing_solution_group_id = next_id
            elif parent_id in self.solution_groups:
                existing_solution_group_id = parent_id
            else:
                existing_solution_group_id = ""

            if existing_solution_group_id == "":
                # There wasn't an existing solution group, start tracking this as a new one
                self.solution_groups[next_id] = SingleGroupGenerator(next_id, self, next_group)

            else:
                # This is an update to an existing solution group
                existing_solution_group = self.solution_groups[existing_solution_group_id]
                existing_solution_group.group_list = next_group
                existing_solution_group.group_id = next_id
                # Update the index of this updated solution group
                self.solution_groups.pop(existing_solution_group_id)
                self.solution_groups[next_id] = existing_solution_group

            if existing_solution_group_id == current_id:
                return True

    def has_multiple_groups(self):
        if len(self.solution_groups) > 1:
            return True
        elif self.complete:
            return False
        else:
            return self.next_solution_in_group("")


# Create a generator that yields solutions in a minimal solution group as quickly as it is found
# but will continue returning solutions until it is maximal if requested. The idea is to make it easy
# to see if there is at least one solution for yes/no questions and propositions (thus the quick minimal solution)
# but allow other types of phrases to get all answers in a group if needed
#
# It also provides a method to see if there is at least one other solution group available
#
# This will only actually generate a single solution group.
class SingleSolutionGroupGenerator(object):
    def __init__(self, all_plural_groups_stream, variable_has_inf_max):
        self.all_plural_groups_stream = all_plural_groups_stream
        self.variable_has_inf_max = variable_has_inf_max
        self.current_group_generator = None
        self.chosen_solution_id = None
        self._has_multiple_groups = False

    def __iter__(self):
        return self

    def __next__(self):
        if self.current_group_generator is not None:
            # Keep returning solutions from the current solution group
            try:
                next_solution = next(self.current_group_generator)
                return next_solution

            except StopIteration:
                self.current_group_generator = None

        if self.all_plural_groups_stream is None:
            raise StopIteration

        # Search for another solution group that descends from this solution group
        # and return solutions from it
        while True:
            try:
                group = next(self.all_plural_groups_stream)

            except StopIteration:
                self.all_plural_groups_stream = None
                raise

            if self.chosen_solution_id is None:
                # We haven't chosen a solution_id yet, so start with this one
                self.chosen_solution_id = group[1]
                self.current_group_generator = iter(group[0])
                return self.__next__()

            elif group[1].startswith(self.chosen_solution_id):
                # This group was created by adding a solution to our chosen solution group
                # so it is just "a little more". We need to use this as our new ID so we don't accidentally
                # return other alternative groups that have this same new solution added to them
                self.chosen_solution_id = group[1]
                return group[0][-1]

            else:
                # This solution group is not a descendant of the one we are tracking so we should skip it
                # But: remember that there are multiple solution groups so we can say "there are more"
                self._has_multiple_groups = True

                # If no variable has a between(N, inf) constraint,
                # Just stop now and the caller will get a subset solution group for the answer they care about
                # Note that it may not be *minimal*, might be a subset, and might be maximal.
                # If it does have an between(N, inf) constraint, return them all
                if not self.variable_has_inf_max:
                    raise StopIteration

    # See if this generator has more solution groups than just its chosen group available
    def has_multiple_groups(self):
        if self._has_multiple_groups:
            return True

        else:
            if self.all_plural_groups_stream is None:
                # No more solutions to iterate through
                return False

            else:
                # Keep working through solutions until we find another group
                # Or the end of all solutions
                while True:
                    try:
                        group = next(self.all_plural_groups_stream)
                        if not group[1].startswith(self.chosen_solution_id):
                            return True

                    except StopIteration:
                        return False


# Group the unquantified solutions into "solution groups" that meet the criteria on each variable.
# Designed to return the minimal solution that meets the criteria as quickly as possible.
#
# If the criteria has any between(N, inf) criteria, it will keep streaming answers until the end
# If not, it will stop after the first (minimal) solution is found.
#
# A second solution group will be returned, if it exists, but will be bogus. It is just there so that the caller can see there is one. This is
# to reduce the cost of generating the answer
#
# Allows the developer to choose which solution group to return
#   if they return [], it means "skip this solution group" and we'll try the next one
# yields an iterator that returns solution groups
# TODO: Intelligently choosing the initial cardinal could greatly reduce the combinations processed...
def solution_groups(execution_context, solutions_orig, this_sentence_force, wh_question_variable, tree_info):
    solutions = at_least_one_generator(solutions_orig)

    if solutions:
        # Go through each variable that has a quantifier in order and gather and optimize the criteria list
        declared_criteria_list = [data for data in declared_determiner_infos(execution_context, solutions.first_item)]
        optimized_criteria_list = list(optimize_determiner_infos(declared_criteria_list, this_sentence_force, wh_question_variable))

        # variable_has_inf_max means at least one variable has (N, inf) which means we need to go all the way to the end to get the maximal
        # solution. Otherwise, we can just stop when we have a solution and return a minimal solution
        variable_metadata, initial_stats_group, has_global_constraint, variable_has_inf_max = plural_groups_stream_initial_stats(execution_context, optimized_criteria_list)
        groups_stream = all_plural_groups_stream(execution_context, solutions, optimized_criteria_list, variable_metadata,
                                                 initial_stats_group, has_global_constraint, variable_has_inf_max)
        group_generator = SolutionGroupGenerator(groups_stream, variable_has_inf_max)
        at_least_one_group = at_least_one_generator(group_generator)
        if at_least_one_group is not None:
            # First see if there is a solution_group handler that should be called
            handlers, index_predication = find_solution_group_handlers(execution_context, this_sentence_force, tree_info)
            for next_group in at_least_one_group:
                created_solution_group, has_more, group_list = run_handlers(handlers, next_group, index_predication)
                if created_solution_group is None:
                    # No solution group handlers, or none handled it or failed: just do the default behavior
                    yield group_list

                    # If there are multiple solution groups, we need to add one more (fake) group
                    # and yield it so that the caller thinks there are multiple answers and will give a message
                    # to the user. The answers aren't shown so it can be anything
                    if group_generator.has_multiple_groups():
                        yield True

                    return

                elif isinstance(created_solution_group, list) and len(created_solution_group) == 0:
                    # Handler said to skip this group
                    continue

                else:
                    # Yield the group the handler generated
                    yield created_solution_group
                    if has_more:
                        yield True

                    return


def run_handlers(handlers, group, index_predication):
    created_solution_group = None
    has_more = False
    if len(handlers) > 0:
        state_list = list(group)
        for is_predication_handler in handlers:
            handler_function = is_predication_handler[1]
            if is_predication_handler[0]:
                # This is a predication-style solution group handler
                # Build up an arg structure to call the predication with that
                # has the same arguments as the normal predication but has a list for each argument that represents the solution group
                handler_args = []
                for _ in range(len(index_predication.args)):
                    handler_args.append([])

                for state in state_list:
                    for arg_index in range(len(index_predication.args)):
                        if index_predication.argument_types()[arg_index] == "c" or index_predication.argument_types()[arg_index] == "h":
                            handler_args[arg_index].append(index_predication.args[arg_index])
                        else:
                            handler_args[arg_index].append(state.get_binding(index_predication.args[arg_index]))
                handler_args = [state_list] + handler_args

            else:
                handler_args = (state_list,)

            for next_solution_group in handler_function(*handler_args):
                if created_solution_group is None:
                    created_solution_group = next_solution_group
                    if len(created_solution_group) == 0:
                        # handler said to fail
                        break
                else:
                    has_more = True
                    break

            # First solution_group handler that yields, wins
            if created_solution_group:
                break

        return created_solution_group, has_more, state_list

    else:
        return None, None, group

# returns predication_handlers, global_handlers
# with just an array of functions in each
def find_solution_group_handlers(execution_context, this_sentence_force, tree_info):
    def get_function(module_function):
        module = sys.modules[module_function[0]]
        function = getattr(module, module_function[1])
        return function

    handlers = []
    index_predication = find_predication_from_introduced(tree_info["Tree"], tree_info["Index"])
    for module_function in execution_context.vocabulary.predications("solution_group_" + index_predication.name, index_predication.argument_types(), this_sentence_force):
        handlers.append([True, get_function(module_function)])

    for module_function in execution_context.vocabulary.predications("solution_group", [], this_sentence_force):
        handlers.append([False, get_function(module_function)])

    return handlers, index_predication


# Return the infos in the order they will be executed in
def declared_determiner_infos(execution_context, state):
    tree_info = state.get_binding("tree").value[0]
    variables = gather_quantifier_order(tree_info)
    for variable_name in variables:
        if variable_name[0] == "x":
            binding = state.get_binding(variable_name)

            # First get the determiner
            determiner = determiner_from_binding(state, binding)
            if determiner is not None:
                yield determiner

            # Then get the quantifier
            quantifier_determiner = quantifier_from_binding(state, binding)
            if quantifier_determiner is not None:
                yield quantifier_determiner


def reduce_variable_determiners(variable_info_list, this_sentence_force, wh_question_variable):
    min_size = 0
    max_size = float(inf)
    global_constraint = None
    exactly_constraint = None
    all_rstr_constraint = None
    predication = None
    for constraint in variable_info_list:
        if constraint.global_criteria == GlobalCriteria.exactly:
            # If there is more than one "only" ... that should never happen. Unclear what words would cause it
            assert exactly_constraint is None
            exactly_constraint = constraint

        elif constraint.global_criteria == GlobalCriteria.all_rstr_meet_criteria:
            # ditto
            assert all_rstr_constraint is None
            all_rstr_constraint = constraint

        else:
            # Constraints with no global criteria just get merged to most restrictive
            if constraint.min_size > min_size:
                min_size = constraint.min_size
                predication = constraint.predication

            if constraint.max_size < max_size:
                max_size = constraint.max_size
                predication = constraint.predication

    if exactly_constraint is not None:
        assert exactly_constraint.min_size >= min_size and exactly_constraint.max_size <= max_size
        min_size = exactly_constraint.min_size
        max_size = exactly_constraint.max_size
        global_constraint = GlobalCriteria.exactly
        predication = exactly_constraint.predication

    if all_rstr_constraint is not None:
        if len(variable_info_list) > 1:
            # convert "the 2" into a single constraint so it can ensure there are really only 2
            # Should only ever be "the"
            assert all_rstr_constraint.min_size == 1 and all_rstr_constraint.max_size == float(inf)
            global_constraint = GlobalCriteria.all_rstr_meet_criteria
            predication = all_rstr_constraint.predication

        else:
            # This was the only constraint, use it
            return [all_rstr_constraint]

    if predication is None:
        predication = variable_info_list[0].predication

    return [VariableCriteria(predication, variable_info_list[0].variable_name, min_size, max_size, global_criteria=global_constraint)]


def reduce_determiner_infos(determiner_info_list_orig, this_sentence_force, wh_question_variable):
    determiner_info_list = copy.deepcopy(determiner_info_list_orig)
    info_by_variable = determiner_info_by_variable(determiner_info_list)
    reduced_determiner_infos = []
    for variable_info_list in info_by_variable.values():
        reduced_determiner_infos += reduce_variable_determiners(variable_info_list, this_sentence_force, wh_question_variable)

    return reduced_determiner_infos


def determiner_info_by_variable(determiner_info_list):
    info_by_variable = {}
    for determiner_info in determiner_info_list:
        if determiner_info.variable_name not in info_by_variable:
            info_by_variable[determiner_info.variable_name] = []
        info_by_variable[determiner_info.variable_name].append(determiner_info)

    return info_by_variable


# Is passed a list of VariableCriteria
def optimize_determiner_infos(determiner_info_list_orig, this_sentence_force, wh_question_variable):
    determiner_info_list = copy.deepcopy(determiner_info_list_orig)

    # First combine the determiners into 1 if possible
    determiner_info_list = reduce_determiner_infos(determiner_info_list, this_sentence_force, wh_question_variable)

    # Any constraint on a variable that is 1,inf is meaningless since it means "a value exists" which means that it has a value
    # but every variable must have a value, so it doesn't do anything, remove it
    new_info_list = []
    for determiner_info in determiner_info_list:
        if determiner_info.min_size == 1 and determiner_info.max_size == float(inf) and determiner_info.global_criteria is None:
            continue

        else:
            new_info_list.append(determiner_info)

    determiner_info_list = new_info_list

    return determiner_info_list


groups_logger = logging.getLogger('SolutionGroups')
