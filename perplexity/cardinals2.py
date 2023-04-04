import sys
from perplexity.cardinals import cardinal_from_binding
from perplexity.execution import call, set_variable_execution_data, get_variable_execution_data, report_error
from perplexity.set_utilities import append_if_unique
from perplexity.tree import find_quantifier_from_variable


# Return each quantified variable, along with its cardinal and quantifier
from perplexity.utilities import is_plural_from_tree_info


def variable_cardinal_quantifier_predication(state):
    tree_info = state.get_binding("tree").value[0]
    variables = tree_info["Variables"]
    tree = tree_info["Tree"]

    for variable_name in variables.keys():
        if variable_name[0] == "x":
            binding = state.get_binding(variable_name)
            cardinal = cardinal_from_binding(state, None, binding)
            quantifier_predication = find_quantifier_from_variable(tree, variable_name)
            module = sys.modules[__name__]
            quantifier_function = getattr(module, quantifier_predication.name + "_impl")
            yield variable_name, cardinal, quantifier_function, quantifier_predication


# Filter the unquantified solutions by recursively filtering them by each quantified variable
# TODO: Intelligently choosing the initial cardinal could greatly reduce the combinations processed...
def solution_groups(execution_context, solutions_with_rstr):
    if len(solutions_with_rstr) > 0:
        # Go through each variable that has a quantifier in any order.
        quantifier_list = [data for data in variable_cardinal_quantifier_predication(solutions_with_rstr[0][0])]
        yield from filter_solutions_for_next_quantifier(execution_context, quantifier_list, solutions_with_rstr, True)


def filter_solutions_for_next_quantifier(execution_context, quantifier_list, solutions_with_rstr, initial_cardinal=False):
    if len(quantifier_list) == 0:
        yield solutions_with_rstr

    else:
        variable_name = quantifier_list[0][0]
        cardinal = quantifier_list[0][1]
        quantifier = quantifier_list[0][2]
        quantifier_predication = quantifier_list[0][3]

        # Call that cardinal to get groups of solutions that meet it
        for cardinal_solution_group in cardinal.solution_groups(execution_context, solutions_with_rstr, initial_cardinal):
            # Then call the quantifier to further filter those groups into quantified groups that meet it
            #   The quantifier needs to yield groups of the solution that match it.  For example "a_q" needs to yield every one.
            for quantified_cardinal_solution_group in quantifier(execution_context, variable_name, quantifier_predication.args[2], cardinal_solution_group):
                # Pass the filtered groups down to the next one
                yield from filter_solutions_for_next_quantifier(execution_context, quantifier_list[1:], quantified_cardinal_solution_group)


def quantifier_raw(state, x_variable_binding, h_rstr, h_body):
    # First get all uncardinalized, unquantified answers
    variable_name = x_variable_binding.variable.name
    rstr_values = []
    for rstr_solution in call(state, h_rstr):
        rstr_values.extend(rstr_solution.get_binding(variable_name).value)
        for body_solution in call(rstr_solution, h_body):
            yield body_solution

    set_variable_execution_data(variable_name, "AllRstrValues", rstr_values)


def _which_q_impl(execution_context, variable_name, h_body, cardinal_solution_group):
    yield cardinal_solution_group


def udef_q_impl(execution_context, variable_name, h_body, cardinal_solution_group):
    yield cardinal_solution_group


# Several meanings:
# 1. Means "this" which only succeeds for rstrs that are the single in scope x set and there are no others that are in scope
#       "put the two keys in the lock": should only work if there are only two keys in scope:
#       run the rstr, run the cardinal (potentially fail), the run the body (potentially fail)
# 2. Means "the one and only" which only succeeds if the rstr is a single set and there are no other sets
#       same approach
def _the_q_impl(execution_context, variable_name, h_body, cardinal_solution_group):
    all_unique_values = execution_context.get_variable_execution_data(variable_name)["AllRstrValues"]
    is_plural = is_plural_from_tree_info(execution_context.tree_info, variable_name)
    used_unique_values = []
    for solution_rstr in cardinal_solution_group:
        binding = solution_rstr[0].get_binding(variable_name)
        append_if_unique(used_unique_values, binding.value)

    if not is_plural and len(all_unique_values) > 1:
        execution_context.report_error(["moreThan1", ["AtPredication", h_body, variable_name]], force=True)

    elif len(all_unique_values) != len(used_unique_values):
        execution_context.report_error(["notTrueForAll", ["AtPredication", h_body, variable_name]], force=True)

    else:
        yield cardinal_solution_group


# Solution groups are never combinatoric due to the solution_groups_helper
# so we can just see if there is more than one "a"
def _a_q_impl(execution_context, variable_name, h_body, cardinal_solution_group):
    found_item = None
    for solution_rstr in cardinal_solution_group:
        binding = solution_rstr[0].get_binding(variable_name)
        if found_item is None:
            found_item = binding.value

        elif found_item == binding.value:
            continue

        else:
            # More than one "a", so fails
            return

    yield cardinal_solution_group


def final_answer_groups(execution_context, solutions):
    all_solution_groups = []
    for group in solution_groups(execution_context, [[solution, []] for solution in solutions]):
        all_solution_groups.append([solution_info[0] for solution_info in group])

    return all_solution_groups
