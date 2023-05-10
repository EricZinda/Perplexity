import copy
import logging
from math import inf
from perplexity.determiners4 import determiner_from_binding, quantifier_from_binding, \
    all_plural_groups_stream, VariableCriteria, GlobalCriteria, plural_groups_stream_initial_stats
from perplexity.tree import gather_quantifier_order
from perplexity.utilities import at_least_one_generator


# Create a generator that yields solutions in a minimal solution group as quickly as it is found
# but will continue returning solutions until it is maximal if requested. The idea is to make it easy
# to see if there is at least one solution for yes/no questions and propositions (thus the quick minimal solution)
# but allow other types of phrases to get all answers in a group if needed
#
# It also provides a method to see if there is at least one other solution group available
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
            # Keep returning solutions from the original solution group
            try:
                next_solution = next(self.current_group_generator)
                return next_solution

            except StopIteration:
                self.current_group_generator = None

        if self.all_plural_groups_stream is None:
            raise StopIteration

        # Search for another solution group that descends from this solution group
        # and return the new solution from it
        while True:
            try:
                group = next(self.all_plural_groups_stream)

            except StopIteration:
                self.all_plural_groups_stream = None
                raise

            if self.chosen_solution_id is None:
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
                # Remember that there are multiple solution groups so we can say "there are more"
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
        group_generator = SingleSolutionGroupGenerator(groups_stream, variable_has_inf_max)
        one_group = at_least_one_generator(group_generator)
        if one_group is not None:
            yield one_group

            # If there are multiple solution groups, we need to add one more (fake) group
            # and yield it so that the caller thinks there are multiple answers and will give a message
            # to the user. The answers aren't shown so it can be anything
            if group_generator.has_multiple_groups():
                yield True


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
            yield quantifier_from_binding(state, binding)


def reduce_variable_determiners(variable_info_list, this_sentence_force, wh_question_variable):
    min = 0
    max = float(inf)
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
            if constraint.min_size > min:
                min = constraint.min_size
                predication = constraint.predication

            if constraint.max_size < max:
                max = constraint.max_size
                predication = constraint.predication

    if exactly_constraint is not None:
        assert exactly_constraint.min_size >= min and exactly_constraint.max_size <= max
        min = exactly_constraint.min_size
        max = exactly_constraint.max_size
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

    return [VariableCriteria(predication, variable_info_list[0].variable_name, min, max, global_criteria=global_constraint)]


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
