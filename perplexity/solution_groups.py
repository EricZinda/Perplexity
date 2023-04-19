import itertools
import logging
import sys
from importlib import import_module
from math import inf

from perplexity.determiners2 import determiner_from_binding, quantifier_from_binding, between_determiner
from perplexity.tree import find_quantifier_from_variable, gather_quantifier_order


# Filter the unquantified solutions by recursively filtering them by each quantified variable
# There is an implicit "uber quantifier" on the front of all phrases that tells you how many of the solutions to return
# All should just return 1, except for which
# TODO: Intelligently choosing the initial cardinal could greatly reduce the combinations processed...
def solution_groups(execution_context, solutions, all_solutions):
    if len(solutions) > 0:
        # Go through each variable that has a quantifier in any order.
        declared_determiner_info_list = [data for data in declared_determiner_infos(execution_context, solutions[0])]
        optimized_determiner_info_list = optimize_determiner_infos(declared_determiner_info_list)
        compiled_determiner_info_list = compile_determiner_infos(optimized_determiner_info_list)

        # Start with an `ordered_determiner_list` of numeric determiners (adjective and quantifier) and a `previous_determiner_group`
        # that starts as the set of all undetermined solutions. `previous_determiner_group` starts with
        # a single subset that contains all the solutions.
        previous_determiner_group = {None: solutions}
        for group in filter_solutions_for_next_determiner(execution_context, compiled_determiner_info_list, previous_determiner_group, True):
            if groups_logger.isEnabledFor(logging.DEBUG):
                groups_logger.debug(f"Found answer: {group}")
            yield from itertools.chain(group.values())
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
            all_rstr_values = execution_context.get_variable_execution_data(variable_name)["AllRstrValues"]
            yield [quantifier_constraint, quantifier_type, quantifier_constraint_args], variable_name, quantifier_predication, all_rstr_values


def optimize_determiner_infos(determiner_info_list):
    new_info_list = []

    # First optimization: Walking back from the end:
    #     delete all last determiners in a row that are number_constraint(1, inf, False)
    remove_determiners = True
    for determiner_info in reversed(determiner_info_list):
        constraint_info = determiner_info[0]
        constraint_name = constraint_info[0]
        constraint_type = constraint_info[1]
        constraint_args = constraint_info[2]

        if remove_determiners and constraint_name == "number_constraint" and constraint_type == "default" and constraint_args == [1, float(inf), False]:
            continue

        else:
            remove_determiners = False
            new_info_list.append(determiner_info)

    return reversed(new_info_list)
    # return determiner_info_list


# Converts from:
#   [[constraint_name, constraint_type, constraint_args], variable_name, predication, all_rstr]
# to:
#   [[function, extra_args], variable_name, predication, all_rstr]
def compile_determiner_infos(determiner_info_list):
    # Now we have an optimized list, actually compile it down to functions
    final_list = []
    for determiner_info in determiner_info_list:
        constraint_info = determiner_info[0]
        constraint_name = constraint_info[0]
        constraint_type = constraint_info[1]
        constraint_args = constraint_info[2]

        if constraint_name == "number_constraint" and constraint_type == "default":
            function = between_determiner
            extra_args = constraint_args

        else:
            # constraint_type must be in the form "module.function_name"
            module_path, function_name = constraint_type.rsplit('.', 1)
            if module_path != "solution_groups":
                module = import_module(module_path)

            else:
                module = sys.modules[__name__]

            function = getattr(module, function_name)
            extra_args = []

        final_list.append([[function, extra_args], determiner_info[1], determiner_info[2], determiner_info[3]])

    return final_list


def filter_solutions_for_next_determiner(execution_context, determiner_info_list, previous_determiner_group, initial_determiner=False):
    if len(determiner_info_list) == 0:
        if groups_logger.isEnabledFor(logging.DEBUG):
            groups_logger.debug(f"Success: Final solutions: {previous_determiner_group}")
        yield previous_determiner_group

    else:
        function_info = determiner_info_list[0][0]
        variable_name = determiner_info_list[0][1]
        predication = determiner_info_list[0][2]
        all_rstr_values = determiner_info_list[0][3]

        function = function_info[0]
        function_extra_args = function_info[1]

        function_args = (execution_context, variable_name, predication, all_rstr_values, previous_determiner_group, initial_determiner, len(determiner_info_list) == 1) + tuple(function_extra_args)
        for determiner_solution_group in function(*function_args):
            yield from filter_solutions_for_next_determiner(execution_context, determiner_info_list[1:], determiner_solution_group)


groups_logger = logging.getLogger('SolutionGroups')
