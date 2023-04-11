import copy
import itertools
import logging
import sys
from perplexity.set_utilities import all_nonempty_subsets, all_combinations_with_elements_from_all, append_if_unique, \
    count_set, all_nonempty_subsets_stream
from perplexity.utilities import is_plural, at_least_one_generator
from importlib import import_module
from perplexity.variable_binding import VariableValueType
from perplexity.vocabulary import PluralType


# For phrases like "files are large" or "only 2 files are large" we need a gate around
# the quantifier that only returns answers if they meet some criteria
# Note that the thing being counted is the actual rstr values,
# so rstr_x = [a, b] would count as 2
def determiner_from_binding(state, h_body, binding):
    if binding.variable.determiner is not None:
        module_class_name = binding.variable.determiner[0]
        module_path, class_name = module_class_name.rsplit('.', 1)
        if module_path != "determiners":
            module = import_module(module_path)

        else:
            module = sys.modules[__name__]

        class_constructor = getattr(module, class_name)
        return class_constructor(*([binding.variable.name, h_body] + binding.variable.determiner[1]))

    elif is_plural(state, binding.variable.name):
        # Plural determiner
        return BetweenDeterminer(binding.variable.name, h_body, 1, float('inf'), False)

    else:
        # Singular determiner
        return BetweenDeterminer(binding.variable.name, h_body, 1, 1, False)


# Return an iterator that yields lists of solutions ("a solution list") without combinatorial variables.
# These are lists of solutions because: If variable_name is a combinatorial variable it means that any combination
#   of values in it are true, so as long as one from the group remains at the end, the solution group is still valid.
#       For solution_group_combinatorial=true, it is the equivalent of breaking it into N more alternative
#           solutions with each solution having one of the combinations of possible values
#       For solution_group_combinatorial=false, it means that the solutions can't be broken up and must all be true.
#           But: the combinatorial variable means that *any* of the combinations for that variable can be true
#           if we just include all combinations in the non-combinatorial list, it will require them all to be true which isn't right
#           so instead we have to try every alternative by generating an entire new answer list for each alternative
# If it is not a combinatorial value, it gets added, as is, to set_solution_list
def solution_list_alternatives_without_combinatorial_variables(execution_context, variable_name, max_answer_count, solutions_orig,
                                                               cardinal_criteria, solution_group_combinatorial=False):
    variable_metadata = execution_context.get_variable_metadata(variable_name)
    variable_plural_type = variable_metadata["PluralType"]

    # set_solution_alternatives_list contains all the alternatives for
    # a combinatoric variable. set_solution_list contains all values that were not combinatoric
    set_solution_alternatives_list = []
    set_solution_list = []

    for solution in solutions_orig:
        binding = solution.get_binding(variable_name)
        if binding.variable.value_type == VariableValueType.combinatoric:
            # If variable_name is combinatoric, all of its appropriate alternative combinations
            # get added to set_solution_alternatives_list
            # Thus, if the variable_plural_type is collective, we only add sets > 1, etc
            min_size = 1
            max_size = None
            if variable_plural_type == PluralType.distributive:
                max_size = 1

            elif variable_plural_type == PluralType.collective:
                min_size = 2

            else:
                assert variable_plural_type == PluralType.all

            def binding_alternative_generator():
                for subset in all_nonempty_subsets_stream(binding.value, min_size=min_size, max_size=max_size):
                    yield solution.set_x(variable_name, subset, VariableValueType.set)

            binding_alternatives = binding_alternative_generator()
            set_solution_alternatives_list.append(binding_alternatives)

        else:
            set_solution_list.append(solution)

    # Flatten out the list of lists
    if len(set_solution_alternatives_list) > 0:
        determiner_logger.debug(f"Found {len(set_solution_alternatives_list)} combinatoric answers")
        set_solution_alternatives_list = itertools.chain.from_iterable(set_solution_alternatives_list)

    # Now the combination of set_solution_alternatives_list together with set_solution_list contain
    # all the alternative assignments of variable_name. Next, yield each combined alternative
    if solution_group_combinatorial:

        def combinatorial_solution_group_generator():
            for item in itertools.chain.from_iterable([set_solution_list, set_solution_alternatives_list]):
                determiner_logger.debug(f"Combinatorial answer: {item}")
                yield item
            # yield from itertools.chain.from_iterable([set_solution_list, set_solution_alternatives_list])

        yield combinatorial_solution_group_generator()

    else:
        determiner_logger.debug(f"Answers are not combinatorial")
        # See comments at top of function for what this is doing
        set_solution_alternatives_list = at_least_one_generator(set_solution_alternatives_list)
        alternative_yielded = False
        if set_solution_alternatives_list is not None:
            for alternative_list in all_combinations_with_elements_from_all(set_solution_alternatives_list):
                # First add all the solutions that are shared between the alternatives
                # because they weren't combinatorial
                # Then add this combinatorial alternative
                def combinatorial_solution_group_generator():
                    yield from itertools.chain.from_iterable([copy.deepcopy(set_solution_list), alternative_list])

                yield combinatorial_solution_group_generator()
                alternative_yielded = True

        if not alternative_yielded:
            yield solutions_orig


# Convert each list of solutions into a list of (binding_value, [solutions]) pairs
# where binding_value has one rstr value and [solutions] is a list of
# all solutions that have that value.
def unique_rstr_solution_list_generator(variable_name, solutions_list):
    variable_assignments = []
    for solution_index in range(len(solutions_list)):
        binding_value = solutions_list[solution_index].get_binding(variable_name).value
        # TODO: find a better way to remove duplicates, support hashing objects and use set?
        unique = True
        for variable_assignment in variable_assignments:
            if binding_value == variable_assignment[0]:
                variable_assignment[1].append(solution_index)
                unique = False
                break

        if unique:
            unique_solution = (binding_value, [solution_index])
            variable_assignments.append(unique_solution)
            yield unique_solution


# Ensure that solutions_orig is broken up into a set of solution groups that are not combinatoric
# in any way
# max_answer_count is the maximum number of individual items that will ever be used.
#   So, for "2 boys", it should be 2 since it must be no more than 2
#   but for "boys" it has to be None since it could be a huge set of boys
# combinatorial is True when any combination of the solutions can be used, otherwise, the exact set must be true
def determiner_solution_groups_helper(execution_context, variable_name, solutions_orig, determiner_criteria, solution_group_combinatorial=False, max_answer_count=float('inf')):
    # Loop through solution lists that don't contain combinatorial variables
    for solutions_list_generator in solution_list_alternatives_without_combinatorial_variables(execution_context, variable_name, max_answer_count, solutions_orig, determiner_criteria, solution_group_combinatorial):
        # Unfortunately, we need to materialize each solutions list to find all the duplicates
        solutions_list = list(solutions_list_generator)
        determiner_logger.debug(f"Creating determiner solution list size: {len(solutions_list)}:")

        # Get all the unique values assigned to this variable, and collect the solutions that go with them
        unique_variable_assignments_generator = unique_rstr_solution_list_generator(variable_name, solutions_list)

        if solution_group_combinatorial:
            # Get all the combinations of the variable assignments that meet the criteria
            # largest set of lists that can add up to self.count is where every list is 1 item long
            for combination in all_nonempty_subsets_stream(unique_variable_assignments_generator, min_size=1, max_size=max_answer_count):
                # The variable assignments in a combination could have duplicates
                # Need to deduplicate them
                # combination is a list of 2 element lists
                unique_values = []
                for lst in [item[0] for item in combination]:
                    for item in lst:
                        if item not in unique_values:
                            unique_values.append(item)

                # Now see if it works for the determiner, which means the *values* meet the determiner
                # But each set of values might have multiple solutions that go with it, so this means
                # Any combination of them will also work
                if determiner_criteria(unique_values):
                    # Now we need to return all possible combinations of solutions that contained the assignments
                    # which means returning all combinations of the list of solutions that go with each rstr answer
                    # as long as there is at least one element from each
                    #
                    # 'combination' is a list of 2 element lists:
                    #   0 is a list of variable assignments
                    #   1 is a list of solutions that had that assignment
                    for possible_solution in all_combinations_with_elements_from_all([combination_item[1] for combination_item in combination]):
                        combination_solutions = []
                        for index in possible_solution:
                            combination_solutions.append(solutions_list[index])

                        yield combination_solutions

        else:
            # The variable assignments in a combination could have duplicates
            # Need to deduplicate them
            unique_values = []
            for lst in [item[0] for item in unique_variable_assignments_generator]:
                for item in lst:
                    if item not in unique_values:
                        unique_values.append(item)

            if determiner_criteria(unique_values):
                yield solutions_list

            else:
                continue


class BetweenDeterminer(object):
    # Set max to float('inf') to mean "no maximum"
    def __init__(self, variable_name, h_body, min_count, max_count, exactly=False):
        self.variable_name = variable_name
        self.h_body = h_body
        self.min_count = min_count
        self.max_count = max_count
        self.exactly = exactly

    # If combinatorial is False then this solution group *must* be true for all the
    # solutions passed in in order to keep the solution group true for the previous
    # quantifier
    def solution_groups(self, execution_context, solutions, combinatorial=False):
        def criteria(rstr_value_list):
            cardinal_group_values_count = count_set(rstr_value_list)
            error_location = ["AfterFullPhrase", self.variable_name]

            # Even though this *looks* like exactly, it is picking out solutions where there just happen to be
            # N files, so it isn't really
            if cardinal_group_values_count > self.max_count:
                execution_context.report_error_for_index(0, ["moreThan", error_location, self.max_count], force=True)
                return False

            elif cardinal_group_values_count < self.min_count:
                execution_context.report_error_for_index(0, ["lessThan", error_location, self.min_count], force=True)
                return False

            else:
                nonlocal group_rstr
                group_rstr = rstr_value_list
                return True

        if self.exactly:
            error_location = ["AfterFullPhrase", self.variable_name]

            # "Only/Exactly", much like the quantifier "the" does more than just group solutions into groups ("only 2 files are in the folder")
            # it also limits *all* the solutions to that number. So we need to go to the bitter end before we know that that are "only 2"
            # group_rstr is set in the criteria each time a rstr is checked
            group_rstr = []
            unique_rstrs = []
            groups = []
            for group in determiner_solution_groups_helper(execution_context, self.variable_name, solutions, criteria, combinatorial, self.max_count):
                for item in group_rstr:
                    append_if_unique(unique_rstrs, item)

                if len(unique_rstrs) > self.max_count:
                    execution_context.report_error_for_index(0, ["moreThan", error_location, self.max_count], force=True)
                    return

                else:
                    groups.append(group)

            if len(unique_rstrs) < self.min_count:
                execution_context.report_error_for_index(0, ["lessThan", error_location, self.min_count], force=True)
                return

            else:
                yield from groups

        else:
            yield from determiner_solution_groups_helper(execution_context, self.variable_name, solutions, criteria, combinatorial, self.max_count)


determiner_logger = logging.getLogger('Determiners')
