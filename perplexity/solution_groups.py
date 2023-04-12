import logging
import sys
from perplexity.determiners import determiner_from_binding, quantifier_from_binding, between_determiner
from perplexity.tree import find_quantifier_from_variable


# Filter the unquantified solutions by recursively filtering them by each quantified variable
# There is an implicit "uber quantifier" on the front of all phrases that tells you how many of the solutions to return
# All should just return 1, except for which
# TODO: Intelligently choosing the initial cardinal could greatly reduce the combinations processed...
def solution_groups(execution_context, solutions, all_solutions):
    if len(solutions) > 0:
        # Go through each variable that has a quantifier in any order.
        determiner_info_list = [data for data in all_determiner_infos(execution_context, solutions[0])]
        for group in filter_solutions_for_next_determiner(execution_context, determiner_info_list, solutions, True):
            groups_logger.debug(f"Found answer: {group}")
            yield group
            if not all_solutions:
                return


def all_determiner_infos(execution_context, state):
    tree_info = state.get_binding("tree").value[0]
    variables = tree_info["Variables"]
    tree = tree_info["Tree"]

    for variable_name in variables.keys():
        if variable_name[0] == "x":
            binding = state.get_binding(variable_name)
            determiner_type, determiner_args = determiner_from_binding(state, binding)
            if determiner_type == "number_constraint":
                yield [determiner_type, determiner_args], variable_name, between_determiner, determiner_args, None, None

            else:
                assert False

            all_rstr_values = execution_context.get_variable_execution_data(variable_name)["AllRstrValues"]
            quantifier_predication = find_quantifier_from_variable(tree, variable_name)
            quantifier_constraint, quantifier_function, quantifier_args = quantifier_from_binding(state, binding)
            if quantifier_constraint[0] == "number_constraint":
                yield quantifier_constraint, variable_name, quantifier_function, quantifier_args, quantifier_predication, all_rstr_values

            else:
                assert False


def filter_solutions_for_next_determiner(execution_context, determiner_info_list, solutions, initial_determiner=False):
    if len(determiner_info_list) == 0:
        groups_logger.debug(f"Success: Final solutions: {solutions}")
        yield solutions

    else:
        determiner_info = determiner_info_list[0]
        variable_name = determiner_info[1]
        determiner_function = determiner_info[2]
        determiner_args = determiner_info[3]
        predication = determiner_info[4]
        all_rstr_values = determiner_info[5]

        determiner_args = (execution_context, variable_name, predication, all_rstr_values, solutions, initial_determiner) + tuple(determiner_args)
        for determined_solution_group in determiner_function(*determiner_args):
            groups_logger.debug(f"Success: Determiner: {determiner_function}")
            yield from filter_solutions_for_next_determiner(execution_context, determiner_info_list[1:], determined_solution_group)


groups_logger = logging.getLogger('SolutionGroups')
