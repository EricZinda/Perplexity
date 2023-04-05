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
        quantifier_list = [data for data in variable_determiner_quantifier_predication(solutions[0])]
        for group in filter_solutions_for_next_quantifier(execution_context, quantifier_list, solutions, True):
            yield group
            if not all_solutions:
                return


def filter_solutions_for_next_quantifier(execution_context, quantifier_list, solutions, initial_cardinal=False):
    if len(quantifier_list) == 0:
        yield solutions

    else:
        variable_name = quantifier_list[0][0]
        determiner = quantifier_list[0][1]
        quantifier = quantifier_list[0][2]
        quantifier_predication = quantifier_list[0][3]

        for determiner_solution_group in determiner.solution_groups(execution_context, solutions, initial_cardinal):
            # Then call the quantifier to further filter those groups into quantified groups that meet it
            #   The quantifier needs to yield groups of the solution that match it.  For example "a_q" needs to yield every one.
            for quantified_cardinal_solution_group in quantifier(execution_context, variable_name, quantifier_predication.args[2], determiner_solution_group):
                # Pass the filtered groups down to the next one
                yield from filter_solutions_for_next_quantifier(execution_context, quantifier_list[1:], quantified_cardinal_solution_group)


# Return each quantified variable, along with its cardinal and quantifier
def variable_determiner_quantifier_predication(state):
    tree_info = state.get_binding("tree").value[0]
    variables = tree_info["Variables"]
    tree = tree_info["Tree"]

    for variable_name in variables.keys():
        if variable_name[0] == "x":
            binding = state.get_binding(variable_name)
            cardinal = determiner_from_binding(state, None, binding)
            quantifier_predication = find_quantifier_from_variable(tree, variable_name)
            module = sys.modules["perplexity.quantifiers"]
            quantifier_function = getattr(module, quantifier_predication.name + "_impl")
            yield variable_name, cardinal, quantifier_function, quantifier_predication

# # After a set of answers is generated, terms that support both coll and dist will generate both options
# # just in case other predications use either of them.  But, if nobody ends up using them, they are just duplicates
# # remove them here
# def remove_duplicates(solutions):
#     if len(solutions) == 0:
#         return []
#
#     # Go through each variable in all solutions and see if it is coll or dist and used dist
#     variables = solutions[0].get_binding("tree").value[0]["Variables"]
#     variable_names = [variable_name for variable_name in variables if variable_name[0] == "x"]
#     variable_states = {}
#     for solution in solutions:
#         for variable_name in variable_names:
#             if variable_name not in variable_states:
#                 variable_states[variable_name] = {"Coll": False, "Dist": False, "UsedColl": False}
#             binding = solution.get_binding(variable_name)
#             if binding.variable.value_type == VariableValueType.set:
#                 if count_set(binding.value) > 1:
#                     variable_states[variable_name]["Coll"] = True
#                 else:
#                     variable_states[variable_name]["Dist"] = True
#
#             else:
#                 if count_set(binding.value) > 1:
#                     variable_states[variable_name]["Coll"] = True
#                     variable_states[variable_name]["Dist"] = True
#                 else:
#                     variable_states[variable_name]["Dist"] = True
#
#             if binding.variable.used_collective:
#                 variable_states[variable_name]["UsedColl"] = True
#
#     # The final plural just generates duplicates if it goes through both coll and dist
#     # If a variable has only coll or only dist answers keep it
#     # If a variable has both coll and dist: if coll_used only keep the dist
#     # An answer is kept if it is UsedColl
#     unique_solutions = []
#     for solution in solutions:
#         duplicate = False
#         for variable_name in variable_names:
#             # If a variable has only coll or only dist answers keep all of whichever it has
#             if variable_states[variable_name]["Coll"] != variable_states[variable_name]["Dist"]:
#                 continue
#
#             # If a solution has a variable that used coll, keep that
#             if solution.get_binding(variable_name).variable.used_collective:
#                 continue
#
#             # Otherwise, keep it if it is dist
#             if count_set(solution.get_binding(variable_name).value) == 1:
#                 continue
#
#             duplicate = True
#             break
#
#         if not duplicate:
#             unique_solutions.append(solution)
#
#     return unique_solutions
