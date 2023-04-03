import sys
from perplexity.cardinals import cardinal_from_binding
from perplexity.execution import call
from perplexity.tree import find_quantifier_from_variable


# Return each quantified variable, along with its cardinal and quantifier
def variable_cardinal_quantifier(state):
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
            yield variable_name, cardinal, quantifier_function


# Filter the unquantified solutions by recursively filtering them by each quantified variable
# TODO: Intelligently choosing the initial cardinal could greatly reduce the combinations processed...
def solution_groups(execution_context, solutions_with_rstr):
    if len(solutions_with_rstr) > 0:
        # Go through each variable that has a quantifier in any order.
        quantifier_list = [data for data in variable_cardinal_quantifier(solutions_with_rstr[0][0])]
        yield from filter_solutions_for_next_quantifier(execution_context, quantifier_list, solutions_with_rstr, True)


def filter_solutions_for_next_quantifier(execution_context, quantifier_list, solutions_with_rstr, initial_cardinal=False):
    if len(quantifier_list) == 0:
        yield solutions_with_rstr

    else:
        variable_name = quantifier_list[0][0]
        cardinal = quantifier_list[0][1]
        quantifier = quantifier_list[0][2]

        # Call that cardinal to get groups of solutions that meet it
        for cardinal_solution_group in cardinal.solution_groups(execution_context, solutions_with_rstr, initial_cardinal):
            # Then call the quantifier to further filter those groups into quantified groups that meet it
            #   The quantifier needs to yield groups of the solution that match it.  For example "a_q" needs to yield every one.
            for quantified_cardinal_solution_group in quantifier(variable_name, cardinal_solution_group):
                # Pass the filtered groups down to the next one
                yield from filter_solutions_for_next_quantifier(execution_context, quantifier_list[1:], quantified_cardinal_solution_group)


def quantifier_raw(state, x_variable_binding, h_rstr, h_body):
    # First get all uncardinalized, unquantified answers
    for rstr_solution in call(state, h_rstr):
        for body_solution in call(rstr_solution, h_body):
            yield body_solution


def _which_q_impl(variable_name, cardinal_solution_group):
    yield cardinal_solution_group


def udef_q_impl(variable_name, cardinal_solution_group):
    yield cardinal_solution_group


# Solution groups are never combinatoric due to the solution_groups_helper
# so we can just see if there is more than one "a"
def _a_q_impl(variable_name, cardinal_solution_group):
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
