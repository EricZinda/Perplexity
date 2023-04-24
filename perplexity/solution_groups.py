import copy
import itertools
import logging
import sys
from importlib import import_module
from math import inf
from perplexity.determiners3 import determiner_from_binding, quantifier_from_binding, \
    all_plural_groups_stream, VariableCriteria, GlobalCriteria
from perplexity.tree import find_quantifier_from_variable, gather_quantifier_order


# Filter the unquantified solutions by recursively filtering them by each quantified variable
# There is an implicit "uber quantifier" on the front of all phrases that tells you how many of the solutions to return
# All should just return 1, except for which
# TODO: Intelligently choosing the initial cardinal could greatly reduce the combinations processed...
def solution_groups(execution_context, solutions, all_solutions):
    if len(solutions) > 0:
        execution_context.clear_error()

        # Go through each variable that has a quantifier in order
        declared_criteria_list = [data for data in declared_determiner_infos(execution_context, solutions[0])]
        optimized_criteria_list = list(optimize_determiner_infos(declared_criteria_list))

        for group in all_plural_groups_stream(execution_context, solutions, optimized_criteria_list):
            if groups_logger.isEnabledFor(logging.DEBUG):
                groups_logger.debug(f"Found answer: {group}")
            yield group
            if not all_solutions:
                return


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


# Is passed a list of VariableCriteria
def optimize_determiner_infos(determiner_info_list_orig):
    determiner_info_list = copy.deepcopy(determiner_info_list_orig)

    # Not an optimization but semantic
    # convert "the 2" into a single constraint so it can ensure there are really only 2
    # Assume that the dict will retain ordering
    new_info_list = []
    info_by_variable = {}
    for determiner_info in determiner_info_list:
        if determiner_info.variable_name not in info_by_variable:
            info_by_variable[determiner_info.variable_name] = []
        info_by_variable[determiner_info.variable_name].append(determiner_info)

    for variable_info_list in info_by_variable.values():
        if len(variable_info_list) == 2:
            first_info = variable_info_list[0]
            second_info = variable_info_list[1]
            if second_info.global_criteria == GlobalCriteria.all_rstr_meet_criteria:
                assert second_info.min_size == 1 and second_info.max_size == float(inf)
                combined_info = copy.deepcopy(second_info)
                combined_info.min_size = first_info.min_size
                combined_info.max_size = first_info.max_size
                new_info_list.append(combined_info)
                continue

        new_info_list.extend(variable_info_list)
    determiner_info_list = new_info_list

    # Optimization: Walking back from the end:
    #     delete all last determiners in a row that are number_constraint(1, inf, False)
    new_info_list = []
    remove_determiners = True
    for determiner_info in reversed(determiner_info_list):
        if remove_determiners and determiner_info.min_size == 1 and determiner_info.max_size == float(inf) and determiner_info.global_criteria is None:
            continue

        else:
            remove_determiners = False
            new_info_list.append(determiner_info)

    determiner_info_list = reversed(new_info_list)

    return determiner_info_list


groups_logger = logging.getLogger('SolutionGroups')
