import logging
import sys
from perplexity.determiners import determiner_from_binding
from perplexity.tree import find_quantifier_from_variable


# Filter the unquantified solutions by recursively filtering them by each quantified variable
# There is an implicit "uber quantifier" on the front of all phrases that tells you how many of the solutions to return
# All should just return 1, except for which
# TODO: Intelligently choosing the initial cardinal could greatly reduce the combinations processed...
def solution_groups(execution_context, solutions, all_solutions):
    if len(solutions) > 0:
        # Go through each variable that has a quantifier in any order.
        determiner_list = [data for data in determiner_generator(execution_context, solutions[0])]
        for group in filter_solutions_for_next_determiner(execution_context, determiner_list, solutions, True):
            groups_logger.debug(f"Found answer: {group}")
            yield group
            if not all_solutions:
                return


def determiner_generator(execution_context, state):
    tree_info = state.get_binding("tree").value[0]
    variables = tree_info["Variables"]
    tree = tree_info["Tree"]

    for variable_name in variables.keys():
        if variable_name[0] == "x":
            binding = state.get_binding(variable_name)
            cardinal = determiner_from_binding(state, None, binding)
            yield variable_name, cardinal, None, None

            all_rstr_values = execution_context.get_variable_execution_data(variable_name)["AllRstrValues"]
            quantifier_predication = find_quantifier_from_variable(tree, variable_name)
            module = sys.modules["perplexity.quantifiers"]
            quantifier_function = getattr(module, quantifier_predication.name + "_group")
            yield variable_name, quantifier_function, quantifier_predication, all_rstr_values


def filter_solutions_for_next_determiner(execution_context, determiner_list, solutions, initial_determiner=False):
    if len(determiner_list) == 0:
        groups_logger.debug(f"Success: Final solutions: {solutions}")
        yield solutions

    else:
        variable_name = determiner_list[0][0]
        determiner = determiner_list[0][1]
        quantifier_predication = determiner_list[0][2]
        all_rstr_values = determiner_list[0][3]

        # Quantifiers take slightly different arguments
        if quantifier_predication is not None:
            for quantified_cardinal_solution_group in determiner(execution_context, variable_name, quantifier_predication.args[1], quantifier_predication.args[2], all_rstr_values, solutions, initial_determiner):
                groups_logger.debug(f"Success: Quantifier: {determiner}")
                yield from filter_solutions_for_next_determiner(execution_context, determiner_list[1:], quantified_cardinal_solution_group)

        else:
            for determiner_solution_group in determiner.solution_groups(execution_context, solutions, initial_determiner):
                groups_logger.debug(f"Success: Determiner: {determiner}")
                yield from filter_solutions_for_next_determiner(execution_context, determiner_list[1:], determiner_solution_group)


groups_logger = logging.getLogger('SolutionGroups')
