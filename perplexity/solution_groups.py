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
        # Go through each variable that has a quantifier in order
        declared_determiner_info_list = [data for data in declared_determiner_infos(execution_context, solutions[0])]
        optimized_determiner_info_list = optimize_determiner_infos(declared_determiner_info_list)
        compiled_determiner_info_list = compile_determiner_infos(optimized_determiner_info_list)
        var_criteria = []
        for info in compiled_determiner_info_list:
            criteria_constructor = info[0][0]
            args = info[0][1]
            var_criteria.append(criteria_constructor(*args))

        for group in all_plural_groups_stream(execution_context, solutions, var_criteria):
            if groups_logger.isEnabledFor(logging.DEBUG):
                groups_logger.debug(f"Found answer: {group}")
            yield group
            if not all_solutions:
                return


# Return the infos in the order they will be executed in
def declared_determiner_infos(execution_context, state):
    tree_info = state.get_binding("tree").value[0]
    tree = tree_info["Tree"]

    variables = gather_quantifier_order(tree_info)
    for variable_name in variables:
        if variable_name[0] == "x":
            binding = state.get_binding(variable_name)

            # First get the determiner
            determiner_all = determiner_from_binding(state, binding)
            if determiner_all is not None:
                determiner_constraint, determiner_type, determiner_constraint_args = determiner_all
                yield [determiner_constraint, determiner_type, determiner_constraint_args], variable_name, None, None

            # Then get the quantifier
            quantifier_constraint, quantifier_type, quantifier_constraint_args = quantifier_from_binding(state, binding)
            quantifier_predication = find_quantifier_from_variable(tree, variable_name)
            yield [quantifier_constraint, quantifier_type, quantifier_constraint_args], variable_name, quantifier_predication


#   [[constraint_name, constraint_type, constraint_args], variable_name, predication]
def optimize_determiner_infos(determiner_info_list_orig):
    determiner_info_list = copy.deepcopy(determiner_info_list_orig)

    # Not an optimization but semantic
    # convert "the 2" into a single constraint so it can ensure there are really only 2
    # Assume that the dict will retain ordering
    new_info_list = []
    info_by_variable = {}
    for determiner_info in determiner_info_list:
        if determiner_info[1] not in info_by_variable:
            info_by_variable[determiner_info[1]] = []
        info_by_variable[determiner_info[1]].append(determiner_info)

    for variable_info_list in info_by_variable.values():
        if len(variable_info_list) == 2:
            first_info_args = variable_info_list[0][0][2]
            second_info_args = variable_info_list[1][0][2]
            if second_info_args[2] == GlobalCriteria.all_rstr_meet_criteria:
                assert second_info_args[0] == 1 and second_info_args[1] == float(inf)
                first_info_constraint = variable_info_list[0][0][0]
                assert first_info_constraint == "number_constraint"
                combined_info = copy.deepcopy(variable_info_list[1])
                combined_info_args = combined_info[0][2]
                combined_info_args[0] = first_info_args[0]
                combined_info_args[1] = first_info_args[1]
                new_info_list.append(combined_info)
                continue
        new_info_list.extend(variable_info_list)
    determiner_info_list = new_info_list

    # Optimization: Walking back from the end:
    #     delete all last determiners in a row that are number_constraint(1, inf, False)
    new_info_list = []
    remove_determiners = True
    for determiner_info in reversed(determiner_info_list):
        constraint_info = determiner_info[0]
        constraint_name = constraint_info[0]
        constraint_type = constraint_info[1]
        constraint_args = constraint_info[2]

        if remove_determiners and constraint_name == "number_constraint" and constraint_type == "default" and constraint_args == [1, float(inf), None]:
            continue

        else:
            remove_determiners = False
            new_info_list.append(determiner_info)

    determiner_info_list = reversed(new_info_list)

    return determiner_info_list


# Converts from:
#   [[constraint_name, constraint_type, constraint_args], variable_name, predication]
# to:
#   [[constructor function, constraint_args], variable_name, predication]
def compile_determiner_infos(determiner_info_list):
    # Now we have an optimized list, actually compile it down to functions
    final_list = []
    for determiner_info in determiner_info_list:
        constraint_info = determiner_info[0]
        constraint_name = constraint_info[0]
        constraint_type = constraint_info[1]
        constraint_args = constraint_info[2]
        variable_name = determiner_info[1]
        predication = determiner_info[2]

        if constraint_name == "number_constraint" and constraint_type == "default":
            constructor = VariableCriteria
            extra_args = (predication, variable_name,) + tuple(constraint_args)

        else:
            assert False
            # # constraint_type must be in the form "module.function_name"
            # module_path, function_name = constraint_type.rsplit('.', 1)
            # if module_path != "solution_groups":
            #     module = import_module(module_path)
            #
            # else:
            #     module = sys.modules[__name__]
            #
            # constructor = getattr(module, function_name)
            # extra_args = []

        final_list.append([[constructor, extra_args], determiner_info[1]])

    return final_list


groups_logger = logging.getLogger('SolutionGroups')
