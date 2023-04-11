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
        quantifier_list = [data for data in variable_determiner_quantifier_predication_rstr(execution_context, solutions[0])]
        for group in filter_solutions_for_next_quantifier(execution_context, quantifier_list, solutions, True):
            groups_logger.debug(f"Found answer: {group}")
            yield group
            if not all_solutions:
                return


def filter_solutions_for_next_quantifier(execution_context, quantifier_list, solutions, initial_cardinal=False):
    if len(quantifier_list) == 0:
        groups_logger.debug(f"Success: Final solutions: {solutions}")
        yield solutions

    else:
        variable_name = quantifier_list[0][0]
        determiner = quantifier_list[0][1]
        quantifier = quantifier_list[0][2]
        quantifier_predication = quantifier_list[0][3]
        all_rstr_values = quantifier_list[0][4]

        for determiner_solution_group in determiner.solution_groups(execution_context, solutions, initial_cardinal):
            groups_logger.debug(f"Success: Determiner: {determiner}")

            # Then call the quantifier to further filter those groups into quantified groups that meet it
            #   The quantifier needs to yield groups of the solution that match it.  For example "a_q" needs to yield every one.
            for quantified_cardinal_solution_group in quantifier(execution_context, variable_name, quantifier_predication.args[1], quantifier_predication.args[2], all_rstr_values, determiner_solution_group):
                groups_logger.debug(f"Success: Quantifier: {quantifier}")

                # Pass the filtered groups down to the next one
                yield from filter_solutions_for_next_quantifier(execution_context, quantifier_list[1:], quantified_cardinal_solution_group)


# Return each quantified variable, along with its cardinal and quantifier
# and unique rstr values
def variable_determiner_quantifier_predication_rstr(execution_context, state):
    tree_info = state.get_binding("tree").value[0]
    variables = tree_info["Variables"]
    tree = tree_info["Tree"]

    for variable_name in variables.keys():
        if variable_name[0] == "x":
            all_rstr_values = execution_context.get_variable_execution_data(variable_name)["AllRstrValues"]
            binding = state.get_binding(variable_name)
            cardinal = determiner_from_binding(state, None, binding)
            quantifier_predication = find_quantifier_from_variable(tree, variable_name)
            module = sys.modules["perplexity.quantifiers"]
            quantifier_function = getattr(module, quantifier_predication.name + "_group")
            yield variable_name, cardinal, quantifier_function, quantifier_predication, all_rstr_values


groups_logger = logging.getLogger('SolutionGroups')
