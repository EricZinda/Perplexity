import copy
import itertools
import sys
from perplexity.execution import report_error
from perplexity.set_utilities import all_nonempty_subsets, all_combinations_with_elements_from_all, append_if_unique, \
    count_set
from perplexity.utilities import is_plural
from importlib import import_module
from perplexity.variable_binding import VariableValueType


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
        return PluralDeterminer(binding.variable.name, h_body)

    else:
        return SingularDeterminer(binding.variable.name, h_body)


# Ensure that solutions_with_rstr_orig is broken up into a set of solution groups that are not combinatoric
# in any way
# max_answer_count is the maximum number of individual items that will ever be used. None means all
#   So, for "2 boys", it should be 2 since it must be no more than 2
#   but for "boys" it has to be None since it could be a huge set of boys
# combinatorial is True when any combination of the solutions can be used, otherwise, the exact set must be true
def determiner_solution_groups_helper(variable_name, max_answer_count, solutions_orig, cardinal_criteria, solution_group_combinatorial=False):
    # First: Build a list of the set values variable_name has, and which solutions go with each set
    # If variable_name is a combinatorial variable it means that any combination of values in it are true, so as long as one
    #   remains at the end, the solution group is still valid.
    #       For solution_group_combinatorial=true, it is the equivalent of breaking it into N more alternative
    #           solutions with each solution having one of the combinations of possible values
    #       For solution_group_combinatorial=false, it means as long as one of the values in the final answer it is valid

    # If variable_name is combinatoric, all of its alternative combinations get added to set_solution_alternatives_list
    set_solution_alternatives_list = []
    # If not, it gets added, as is, to set_solution_list
    set_solution_list = []
    for solution in solutions_orig:
        binding = solution.get_binding(variable_name)
        if binding.variable.value_type == VariableValueType.combinatoric:
            binding_alternatives = []
            for subset in all_nonempty_subsets(binding.value):
                binding_alternatives.append(solution.set_x(variable_name, subset, VariableValueType.set))
            set_solution_alternatives_list.append(binding_alternatives)
        else:
            set_solution_list.append(solution)

    # Now, the combination of set_solution_alternatives_list together with set_solution_list contain all the alternative assignments
    # of variable_name.
    # Next, make final_alternatives_list contain the merged list
    if solution_group_combinatorial:
        alternative = set_solution_list
        for alternatives in set_solution_alternatives_list:
            alternative.extend(alternatives)
        final_alternatives_list = [alternative]

    else:
        final_alternatives_list = []
        if len(set_solution_alternatives_list) != 0:
            for alternative_list in all_combinations_with_elements_from_all(set_solution_alternatives_list):
                alternative = []
                # First add all the solutions that are shared between the alternatives
                # because they weren't combinatorial
                if len(set_solution_list) > 0:
                    alternative.append(copy.deepcopy(set_solution_list))
                # Then add this combinatorial alternative
                alternative += alternative_list
                final_alternatives_list.append(alternative)

        if len(final_alternatives_list) == 0:
            final_alternatives_list = [solutions_orig]

    for solutions in final_alternatives_list:
        # Get all the unique values assigned to this variable, and collect the solutions that go with them
        variable_assignments = []
        for solution_index in range(len(solutions)):
            binding_value = solutions[solution_index].get_binding(variable_name).value
            # TODO: find a better way to remove duplicates, support hashing objects and use set?
            unique = True
            for variable_assignment in variable_assignments:
                if binding_value == variable_assignment[0]:
                    variable_assignment[1].append(solution_index)
                    unique = False
                    break

            if unique:
                variable_assignments.append((binding_value, [solution_index]))

        if max_answer_count is None:
            max_answer_count = len(variable_assignments)

        if solution_group_combinatorial:
            combinations_of_lists = []
            # Then get all the combinations of those sets that meet the criteria
            # largest set of lists that can add up to self.count is where every list is 1 item long
            for combination_size in range(1, max_answer_count + 1):
                for combination in itertools.combinations(variable_assignments, combination_size):
                    # combination is a list of 2 element lists
                    unique_values = []
                    for lst in [item[0] for item in combination]:
                        for item in lst:
                            if item not in unique_values:
                                unique_values.append(item)

                    if cardinal_criteria(unique_values):
                        # # Finally, return all possible combinations of solutions that contained the assignments
                        # # which means returning all combinations of every non-empty subset of all the lists
                        # # Each combination in combinations_of_lists is a list of 2 element lists:
                        # #   0 is a list of variable assignments
                        # #   1 is a list of solutions that had that assignment
                        # for combination in combinations_of_lists:
                        for possible_solution in all_combinations_with_elements_from_all([combination_item[1] for combination_item in combination]):
                            # print(f"combination: {combination}\n   solution:")
                            combination_solutions = []
                            for index in possible_solution:
                                # print(f"   {solutions_with_rstr[index][0]}")
                                combination_solutions.append(solutions[index])

                            yield combination_solutions

        else:
            unique_values = []
            for lst in [item[0] for item in variable_assignments]:
                for item in lst:
                    if item not in unique_values:
                        unique_values.append(item)

            if cardinal_criteria(unique_values):
                yield solutions

            else:
                continue


class SingularDeterminer(object):
    def __init__(self, variable_name, h_body):
        self.variable_name = variable_name
        self.h_body = h_body

    def solution_groups(self, execution_context, solutions, combinatorial=False):
        def criteria(rstr_value_list):
            return count_set(rstr_value_list) == 1

        yield from determiner_solution_groups_helper(self.variable_name, None, solutions, criteria, combinatorial)


class PluralDeterminer(object):
    def __init__(self, variable_name, h_body):
        self.variable_name = variable_name
        self.h_body = h_body

    def solution_groups(self, execution_context, solutions, combinatorial=False):
        def criteria(rstr_value_list):
            return count_set(rstr_value_list) > 0

        yield from determiner_solution_groups_helper(self.variable_name, None, solutions, criteria, combinatorial)


class CardinalDeterminer(object):
    def __init__(self, variable_name, h_body, count, card_is_exactly):
        self.variable_name = variable_name
        self.h_body = h_body
        self.count = count
        self.exactly = card_is_exactly

    # If combinatorial is False then this solution group *must* be true for all the
    # solutions passed in in order to keep the solution group true for the previous
    # quantifier
    def solution_groups(self, execution_context, solutions, combinatorial=False, cardinal_scoped_to_initial_rstr=False):
        def criteria(rstr_value_list):
            cardinal_group_values_count = count_set(rstr_value_list)
            error_location = ["AtPredication", self.h_body,
                              self.variable_name] if cardinal_scoped_to_initial_rstr else ["AfterFullPhrase",
                                                                                           self.variable_name]

            if cardinal_group_values_count > self.count:
                execution_context.report_error_for_index(0, ["moreThan", error_location, self.count], force=True)
                return False

            elif cardinal_group_values_count < self.count:
                execution_context.report_error_for_index(0, ["lessThan", error_location, self.count], force=True)
                return False

            else:
                nonlocal group_rstr
                group_rstr = rstr_value_list
                return True

        if self.exactly:
            error_location = ["AtPredication", self.h_body,
                              self.variable_name] if cardinal_scoped_to_initial_rstr else ["AfterFullPhrase",
                                                                                           self.variable_name]

            # "Only/Exactly", much like the quantifier "the" does more than just group solutions into groups ("only 2 files are in the folder")
            # it also limits *all* the solutions to that number. So we need to go to the bitter end before we know that that are "only 2"
            group_rstr = []
            unique_rstrs = []
            groups = []
            for group in determiner_solution_groups_helper(self.variable_name, self.count, solutions, criteria, combinatorial):
                for item in group_rstr:
                    append_if_unique(unique_rstrs, item)

                if len(unique_rstrs) > self.count:
                    execution_context.report_error_for_index(0, ["moreThan", error_location, self.count], force=True)
                    return

                else:
                    groups.append(group)

            if len(unique_rstrs) < self.count:
                execution_context.report_error_for_index(0, ["lessThan", error_location, self.count], force=True)
                return

            else:
                yield from groups

        else:
            yield from determiner_solution_groups_helper(self.variable_name, self.count, solutions, criteria, combinatorial)


# For implementing things like "a few" where there is a number
# between 3 and, say 5
class BetweenDeterminer(object):
    def __init__(self, variable_name, h_body, min_count, max_count):
        self.variable_name = variable_name
        self.h_body = h_body
        self.min_count = min_count
        self.max_count = max_count

    # If combinatorial is False then this solution group *must* be true for all the
    # solutions passed in in order to keep the solution group true for the previous
    # quantifier
    def solution_groups(self, execution_context, solutions, combinatorial=False, cardinal_scoped_to_initial_rstr=False):
        def criteria(rstr_value_list):
            cardinal_group_values_count = count_set(rstr_value_list)
            error_location = ["AtPredication", self.h_body, self.variable_name] if cardinal_scoped_to_initial_rstr else ["AfterFullPhrase", self.variable_name]

            if cardinal_group_values_count > self.max_count:
                execution_context.report_error_for_index(0, ["moreThan", error_location, self.max_count], force=True)
                return False

            elif cardinal_group_values_count < self.min_count:
                execution_context.report_error_for_index(0, ["lessThan", error_location, self.min_count], force=True)
                return False

            else:
                return True

        yield from determiner_solution_groups_helper(self.variable_name, self.max_count, solutions, criteria, combinatorial)

