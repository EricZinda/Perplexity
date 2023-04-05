from perplexity.execution import set_variable_execution_data, call
from perplexity.set_utilities import append_if_unique
from perplexity.utilities import is_plural_from_tree_info


# Get all undetermined, unquantified answers
def quantifier_raw(state, x_variable_binding, h_rstr, h_body):
    variable_name = x_variable_binding.variable.name
    rstr_values = []
    for rstr_solution in call(state, h_rstr):
        rstr_values.extend(rstr_solution.get_binding(variable_name).value)
        for body_solution in call(rstr_solution, h_body):
            yield body_solution

    set_variable_execution_data(variable_name, "AllRstrValues", rstr_values)


def _which_q_impl(execution_context, variable_name, h_body, solution_group):
    yield solution_group


def udef_q_impl(execution_context, variable_name, h_body, solution_group):
    yield solution_group


# Several meanings:
# 1. Means "this" which only succeeds for rstrs that are the single in scope x set and there are no others that are in scope
#       "put the two keys in the lock": should only work if there are only two keys in scope:
#       run the rstr, run the cardinal (potentially fail), the run the body (potentially fail)
# 2. Means "the one and only" which only succeeds if the rstr is a single set and there are no other sets
#       same approach
def _the_q_impl(execution_context, variable_name, h_body, solution_group):
    all_unique_values = execution_context.get_variable_execution_data(variable_name)["AllRstrValues"]
    is_plural = is_plural_from_tree_info(execution_context.tree_info, variable_name)
    used_unique_values = []
    for solution in solution_group:
        binding = solution.get_binding(variable_name)
        append_if_unique(used_unique_values, binding.value)

    if not is_plural and len(all_unique_values) > 1:
        execution_context.report_error(["moreThan1", ["AtPredication", h_body, variable_name]], force=True)

    elif len(all_unique_values) != len(used_unique_values):
        execution_context.report_error(["notTrueForAll", ["AtPredication", h_body, variable_name]], force=True)

    else:
        yield solution_group


# Solution groups are never combinatoric due to the solution_groups_helper
# so we can just see if there is more than one "a"
def _a_q_impl(execution_context, variable_name, h_body, solution_group):
    found_item = None
    for solution in solution_group:
        binding = solution.get_binding(variable_name)
        if found_item is None:
            found_item = binding.value

        elif found_item == binding.value:
            continue

        else:
            # More than one "a", so fails
            return

    yield solution_group

