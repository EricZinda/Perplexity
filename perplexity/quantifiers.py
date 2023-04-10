from perplexity.determiners import determiner_solution_groups_helper
from perplexity.execution import set_variable_execution_data, call
from perplexity.set_utilities import append_if_unique, count_set
from perplexity.utilities import is_plural_from_tree_info


# Yield all undetermined, unquantified answers
def quantifier_raw(state, x_variable_binding, h_rstr, h_body):
    variable_name = x_variable_binding.variable.name
    rstr_values = []
    for rstr_solution in call(state, h_rstr):
        rstr_values.extend(rstr_solution.get_binding(variable_name).value)
        for body_solution in call(rstr_solution, h_body):
            yield body_solution

    set_variable_execution_data(variable_name, "AllRstrValues", rstr_values)


def _which_q_group(execution_context, variable_name, h_rstr, h_body, all_rstr, solution_group, combinatorial=False):
    yield solution_group


def udef_q_group(execution_context, variable_name, h_rstr, h_body, all_rstr, solution_group, combinatorial=False):
    yield solution_group


def pronoun_q_group(execution_context, variable_name, h_rstr, h_body, all_rstr, solution_group, combinatorial=False):
    yield solution_group


# Several meanings:
# 1. Means "this" which only succeeds for rstrs that are the single in scope x set and there are no others that are in scope
#       "put the two keys in the lock": should only work if there are only two keys in scope:
#       run the rstr, run the cardinal (potentially fail), the run the body (potentially fail)
# 2. Means "the one and only" which only succeeds if the rstr is a single set and there are no other sets
#       same approach
def _the_q_group(execution_context, variable_name, h_rstr, h_body, all_rstr, solution_group, combinatorial=False):
    is_plural = is_plural_from_tree_info(execution_context.tree_info, variable_name)

    def criteria(rstr_value_list):
        if not is_plural and len(all_rstr) > 1:
            execution_context.report_error(["moreThan1", ["AtPredication", h_body, variable_name]], force=True)
            return False

        elif len(all_rstr) != len(rstr_value_list):
            execution_context.report_error(["notTrueForAll", ["AtPredication", h_body, variable_name]], force=True)
            return False

        else:
            return True

    yield from determiner_solution_groups_helper(execution_context, variable_name, None, solution_group, criteria, combinatorial)


def _a_q_group(execution_context, variable_name, h_rstr, h_body, all_rstr, solution_group, combinatorial=False):
    def criteria(rstr_value_list):
        return count_set(rstr_value_list) == 1

    yield from determiner_solution_groups_helper(execution_context, variable_name, None, solution_group, criteria, combinatorial)
