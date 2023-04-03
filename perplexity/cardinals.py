import copy
import itertools
import sys

from file_system_example.objects import Measurement
from perplexity.execution import report_error
from perplexity.set_utilities import all_nonempty_subsets, all_combinations_with_elements_from_all
from perplexity.utilities import is_plural
from importlib import import_module

from perplexity.variable_binding import VariableValueType


def yield_all(set_or_answer):
    if isinstance(set_or_answer, (list, tuple)):
        for item in set_or_answer:
            yield from yield_all(item)
    else:
        yield set_or_answer


def count_set(rstr_value):
    if isinstance(rstr_value, (list, tuple)):
        if len(rstr_value) == 1 and isinstance(rstr_value[0], Measurement):
            return rstr_value[0].count
        else:
            return len(rstr_value)

    else:
        if isinstance(rstr_value, Measurement):
            return rstr_value.count
        else:
            return 1


# For phrases like "files are large" or "only 2 files are large" we need a gate around
# the quantifier that only returns answers if they meet some criteria
# Note that the thing being counted is the actual rstr values,
# so rstr_x = [a, b] would count as 2
def cardinal_from_binding(state, h_body, binding):
    if binding.variable.cardinal is not None:
        module_class_name = binding.variable.cardinal[0]
        module_path, class_name = module_class_name.rsplit('.', 1)
        if module_path != "cardinals":
            module = import_module(module_path)

        else:
            module = sys.modules[__name__]

        class_constructor = getattr(module, class_name)
        return class_constructor(*([binding.variable.name, h_body] + binding.variable.cardinal[1]))

    elif is_plural(state, binding.variable.name):
        return PluralCardinal(binding.variable.name, h_body)

    else:
        return SingularCardinal(binding.variable.name, h_body)


# Ensure that solutions_with_rstr_orig is broken up into a set of solution groups that are not combinatoric
# in any way
# max_answer_count is the maximum number of individual items that will ever be used. None means all
#   So, for "2 boys", it should be 2 since it must be no more than 2
#   but for "boys" it has to be None since it could be a huge set of boys
# combinatorial is True when any combination of the solutions can be used, otherwise, the exact set must be true
def solution_groups_helper(variable_name, max_answer_count, solutions_with_rstr_orig, cardinal_criteria, solution_group_combinatorial=False):
    # If variable_name is a combinatorial variable it means that any combination of values in it are true, so as long as one
    #   remains at the end, the solution group is still valid.
    #       For solution_group_combinatorial=true, it is the equivalent of breaking it into N more alternative
    #           solutions with each solution having one of the combinations of possible values
    #       For solution_group_combinatorial=false, it means as long as one of the values in the final answer it is valid
    # Turn each combinatorial solution into a list of set solutions
    set_solution_alternatives_list = []
    set_solution_list = []
    for solution in solutions_with_rstr_orig:
        binding = solution[0].get_binding(variable_name)
        if binding.variable.value_type == VariableValueType.combinatoric:
            binding_alternatives = []
            for subset in all_nonempty_subsets(binding.value):
                binding_alternatives.append([solution[0].set_x(variable_name, subset, VariableValueType.set), solution[1]])
            set_solution_alternatives_list.append(binding_alternatives)
        else:
            set_solution_list.append(solution)

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
            final_alternatives_list = [solutions_with_rstr_orig]

    for solutions_with_rstr in final_alternatives_list:
        # Get all the unique values assigned to this variable, and collect the solutions that go with them
        variable_assignments = []
        for solution_index in range(len(solutions_with_rstr)):
            binding_value = solutions_with_rstr[solution_index][0].get_binding(variable_name).value
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
                        combinations_of_lists.append(combination)

            # Finally, return all possible combinations of solutions that contained the assignments
            # which means returning all combinations of every non-empty subset of all the lists
            # Each combination in combinations_of_lists is a list of 2 element lists:
            #   0 is a list of variable assignments
            #   1 is a list of solutions that had that assignment
            for combination in combinations_of_lists:
                for possible_solution in all_combinations_with_elements_from_all([combination_item[1] for combination_item in combination]):
                    # print(f"combination: {combination}\n   solution:")
                    combination_solutions = []
                    for index in possible_solution:
                        # print(f"   {solutions_with_rstr[index][0]}")
                        combination_solutions.append(solutions_with_rstr[index])

                    yield combination_solutions

        else:
            unique_values = []
            for lst in [item[0] for item in variable_assignments]:
                for item in lst:
                    if item not in unique_values:
                        unique_values.append(item)

            if cardinal_criteria(unique_values):
                yield solutions_with_rstr

            else:
                continue


class SingularCardinal(object):
    def __init__(self, variable_name, h_body):
        self.variable_name = variable_name
        self.h_body = h_body

    def meets_criteria(self, cardinal_group_values, cardinal_scoped_to_initial_rstr):
        return True

    def solution_groups(self, execution_context, solutions_with_rstr, combinatorial=False):
        def criteria(rstr_value_list):
            return count_set(rstr_value_list) == 1

        yield from solution_groups_helper(self.variable_name, None, solutions_with_rstr, criteria, combinatorial)


class PluralCardinal(object):
    def __init__(self, variable_name, h_body):
        self.variable_name = variable_name
        self.h_body = h_body

    def meets_criteria(self, cardinal_group, cardinal_scoped_to_initial_rstr):
        cardinal_group_values_count = count_set(cardinal_group.original_rstr_set if cardinal_scoped_to_initial_rstr else cardinal_group.cardinal_group_values())

        # "which rocks are in here?" - the speaker assumes it will return "this one rock"
        # (i.e. work even if there is only a single rock).
        # So: bare Plurals just assumes there is one.
        if cardinal_group_values_count > 0:
            return True

        else:
            error_location = ["AtPredication", self.h_body, self.variable_name] if cardinal_scoped_to_initial_rstr else ["AfterFullPhrase", self.variable_name]
            report_error(["notPlural", error_location, self.variable_name], force=True)
            return False

    def solution_groups(self, execution_context, solutions_with_rstr, combinatorial=False):
        def criteria(rstr_value_list):
            return count_set(rstr_value_list) > 0

        yield from solution_groups_helper(self.variable_name, None, solutions_with_rstr, criteria, combinatorial)


# card(2) means "exactly 2"
class CardCardinal(object):
    def __init__(self, variable_name, h_body, count):
        self.variable_name = variable_name
        self.h_body = h_body
        self.count = count

    def meets_criteria(self, cardinal_group, cardinal_scoped_to_initial_rstr):
        cardinal_group_values_count = count_set(cardinal_group.original_rstr_set if cardinal_scoped_to_initial_rstr else cardinal_group.cardinal_group_values())
        error_location = ["AtPredication", self.h_body, self.variable_name] if cardinal_scoped_to_initial_rstr else ["AfterFullPhrase", self.variable_name]
        if cardinal_group_values_count > self.count:
            report_error(["moreThan", error_location, self.count], force=True)
            return False

        elif cardinal_group_values_count < self.count:
            report_error(["lessThan", error_location, self.count], force=True)
            return False

        else:
            return True

    # If combinatorial is False then this solution group *must* be true for all the
    # solutions passed in in order to keep the solution group true for the previous
    # quantifier
    def solution_groups(self, execution_context, solutions_with_rstr, combinatorial=False, cardinal_scoped_to_initial_rstr=False):
        def criteria(rstr_value_list):
            cardinal_group_values_count = count_set(rstr_value_list)
            error_location = ["AtPredication", self.h_body, self.variable_name] if cardinal_scoped_to_initial_rstr else ["AfterFullPhrase", self.variable_name]

            if cardinal_group_values_count > self.count:
                execution_context.report_error_for_index(0, ["moreThan", error_location, self.count], force=True)
                return False

            elif cardinal_group_values_count < self.count:
                execution_context.report_error_for_index(0, ["lessThan", error_location, self.count], force=True)
                return False

            else:
                return True

        yield from solution_groups_helper(self.variable_name, self.count, solutions_with_rstr, criteria, combinatorial)


# For implementing things like "a few" where there is a number
# between 3 and, say 5
class BetweenCardinal(object):
    def __init__(self, variable_name, h_body, min_count, max_count):
        self.variable_name = variable_name
        self.h_body = h_body
        self.min_count = min_count
        self.max_count = max_count

    def meets_criteria(self, cardinal_group, cardinal_scoped_to_initial_rstr):
        cardinal_group_values_count = count_set(cardinal_group.original_rstr_set if cardinal_scoped_to_initial_rstr else cardinal_group.cardinal_group_values())
        error_location = ["AtPredication", self.h_body, self.variable_name] if cardinal_scoped_to_initial_rstr else ["AfterFullPhrase", self.variable_name]
        if cardinal_group_values_count > self.max_count:
            report_error(["tooMany", error_location], force=True)
            return False

        elif cardinal_group_values_count < self.min_count:
            report_error(["notEnough", error_location], force=True)
            return False

        else:
            return True

    # If combinatorial is False then this solution group *must* be true for all the
    # solutions passed in in order to keep the solution group true for the previous
    # quantifier
    def solution_groups(self, execution_context, solutions_with_rstr, combinatorial=False, cardinal_scoped_to_initial_rstr=False):
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

        yield from solution_groups_helper(self.variable_name, self.max_count, solutions_with_rstr, criteria, combinatorial)


# After a set of answers is generated, terms that support both coll and dist will generate both options
# just in case other predications use either of them.  But, if nobody ends up using them, they are just duplicates
# remove them here
# def RemoveDuplicates(solutions):
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
#             if binding.variable.value_type in [VariableValueType.collective, VariableValueType.combinatoric_collective]:
#                 variable_states[variable_name]["Coll"] = True
#             else:
#                 variable_states[variable_name]["Dist"] = True
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
#             if solution.get_binding(variable_name).variable.value_type in [VariableValueType.distributive, VariableValueType.combinatoric_distributive]:
#                 continue
#
#             duplicate = True
#             break
#
#         if not duplicate:
#             unique_solutions.append(solution)
#
#     return unique_solutions


class CardinalGroup(object):
    def __init__(self, variable_name, is_collective, original_rstr_set, cardinal_group_set, solutions):
        assert not is_collective or (is_collective and len(solutions) == 1), \
            "collective cardinal groups can only have 1 solution"

        self.variable_name = variable_name
        self.is_collective = is_collective
        self.original_rstr_set = original_rstr_set
        self.cardinal_group_set = cardinal_group_set
        self.solutions = solutions

    def cardinal_group_values(self):
        return self.cardinal_group_set


if __name__ == '__main__':
    print(list(all_combinations_with_elements_from_all([[1], [2, 3], [4]])))
