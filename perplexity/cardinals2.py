import sys

from perplexity.cardinals import cardinal_from_binding
from perplexity.execution import call
from perplexity.tree import find_quantifier_from_variable


def quantifier_raw(state, x_variable_binding, h_rstr, h_body):
    # First get all uncardinalized, unquantified answers
    solutions_with_rstr = []
    for rstr_solution in call(state, h_rstr):
        for body_solution in call(rstr_solution, h_body):
            yield body_solution


def variable_with_cardinal(state):
    tree_info = state.get_binding("tree").value[0]
    variables = tree_info["Variables"]
    tree = tree_info["Tree"]

    for variable_name in variables.keys():
        if variable_name[0] == "x":
            binding = state.get_binding(variable_name)
            if binding.variable.cardinal is not None:
                quantifier_predication = find_quantifier_from_variable(tree, variable_name)
                module = sys.modules[__name__]
                quantifier_function = getattr(module, quantifier_predication.name + "_impl")
                yield variable_name, cardinal_from_binding(state, None, binding), quantifier_function


def solution_groups(solutions_with_rstr):
    # Go through each variable that has a cardinal in any order.
    cardinal_list = [data for data in variable_with_cardinal(solutions_with_rstr[0][0])]
    yield from filter_solutions_for_next_cardinal(cardinal_list, solutions_with_rstr)


def filter_solutions_for_next_cardinal(cardinal_list, solutions_with_rstr):
    if len(cardinal_list) == 0:
        yield solutions_with_rstr

    else:
        variable_name = cardinal_list[0][0]
        cardinal = cardinal_list[0][1]
        quantifier = cardinal_list[0][2]

        # Call that cardinal to get groups of solutions that meet it
        for cardinal_solution_group in cardinal.solution_groups(solutions_with_rstr):
            # Then call the quantifier to further filter those groups into quantified groups that meet it
            #   The quantifier needs to yield groups of the solution that match it.  For example "a_q" needs to yield every one.
            for quantified_cardinal_solution_group in quantifier(variable_name, cardinal_solution_group):
                # Pass the filtered groups down to the next one
                yield from filter_solutions_for_next_cardinal(cardinal_list[1:], quantified_cardinal_solution_group)


def _which_q_impl(variable_name, cardinal_solution_group):
    yield cardinal_solution_group


def udef_q_impl(variable_name, cardinal_solution_group):
    yield cardinal_solution_group


def final_answers(solutions):
    all_solutions = []
    for group in solution_groups([[solution, []] for solution in solutions]):
        all_solutions += [item[0] for item in group]

    return all_solutions
