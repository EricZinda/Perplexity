import copy
import logging
from math import inf
from perplexity.determiners4 import determiner_from_binding, quantifier_from_binding, \
    all_plural_groups_stream, VariableCriteria, GlobalCriteria, plural_groups_stream_initial_stats
from perplexity.tree import gather_quantifier_order
from perplexity.utilities import at_least_one_generator


# Filter the unquantified solutions by recursively filtering them by each quantified variable
# There is an implicit "uber quantifier" on the front of all phrases that tells you how many of the solutions to return
# All should just return 1, except for which
# TODO: Intelligently choosing the initial cardinal could greatly reduce the combinations processed...
def solution_groups(execution_context, solutions_orig, this_sentence_force, wh_question_variable, tree_info):
    solutions = at_least_one_generator(solutions_orig)

    if solutions:
        # Go through each variable that has a quantifier in order and gather and optimize the criteria list
        declared_criteria_list = [data for data in declared_determiner_infos(execution_context, solutions.first_item)]
        optimized_criteria_list = list(optimize_determiner_infos(declared_criteria_list, this_sentence_force, wh_question_variable))

        # variable_has_inf_max means at least one variable has (N, inf) which means we need to go all the way to the end to get the maximal
        # solution. Otherwise, we can just stop when we have a solution
        # all_constraints_are_open means they are all that way
        variable_metadata, initial_stats_group, has_global_constraint, variable_has_inf_max, all_constraints_are_open = plural_groups_stream_initial_stats(
            execution_context, optimized_criteria_list)
        has_multiple_groups = False

        def combine_one_solution_group():
            nonlocal has_multiple_groups
            chosen_solution_id = None
            for group in all_plural_groups_stream(execution_context, solutions, optimized_criteria_list, variable_metadata, initial_stats_group, has_global_constraint):
                if chosen_solution_id is None:
                    chosen_solution_id = group[1]
                    for solution in group[0]:
                        yield solution

                elif chosen_solution_id == group[1]:
                    yield group[0][-1]

                else:
                    has_multiple_groups = True
                    if not variable_has_inf_max:
                        return

        one_group = at_least_one_generator(combine_one_solution_group())
        if one_group is not None:
            yield one_group

            # If there are multiple solution groups, we need to add one more (fake) group
            # and yield it so that the caller thinks there are multiple answers and will give a message
            # to the user
            if has_multiple_groups:
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
