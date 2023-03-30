import itertools
import sys

from file_system_example.objects import Measurement
from perplexity.execution import report_error
from perplexity.utilities import is_plural
from importlib import import_module

from perplexity.variable_binding import VariableValueType, is_collective_type


def yield_all(set_or_answer):
    if isinstance(set_or_answer, (list, tuple)):
        for item in set_or_answer:
            yield from yield_all(item)
    else:
        yield set_or_answer


def count_rstr(rstr_value):
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
        return NoCardinal(binding.variable.name, h_body)


class NoCardinal(object):
    def __init__(self, variable_name, h_body):
        self.variable_name = variable_name
        self.h_body = h_body

    def meets_criteria(self, cardinal_group_values, cardinal_scoped_to_initial_rstr):
        return True


# class SingularCardinal(object):
#     def __init__(self, variable_name, h_body):
#         self.variable_name = variable_name
#         self.h_body = h_body
#
#     def meets_criteria(self, cardinal_group, cardinal_scoped_to_initial_rstr):
#         cardinal_group_values_count = count_rstr(cardinal_group.original_rstr_set if cardinal_scoped_to_initial_rstr else cardinal_group.cardinal_group_values())
#         if cardinal_group_values_count == 1:
#             return True
#
#         else:
#             error_location = ["AtPredication", self.h_body, self.variable_name] if cardinal_scoped_to_initial_rstr else ["AfterFullPhrase", self.variable_name]
#             report_error(["notSingular", error_location, self.variable_name], force=True)
#             return False


class PluralCardinal(object):
    def __init__(self, variable_name, h_body):
        self.variable_name = variable_name
        self.h_body = h_body

    def meets_criteria(self, cardinal_group, cardinal_scoped_to_initial_rstr):
        cardinal_group_values_count = count_rstr(cardinal_group.original_rstr_set if cardinal_scoped_to_initial_rstr else cardinal_group.cardinal_group_values())

        # "which rocks are in here?" - the speaker assumes it will return "this one rock"
        # (i.e. work even if there is only a single rock).
        # So: bare Plurals just assumes there is one.
        if cardinal_group_values_count > 0:
            return True

        else:
            error_location = ["AtPredication", self.h_body, self.variable_name] if cardinal_scoped_to_initial_rstr else ["AfterFullPhrase", self.variable_name]
            report_error(["notPlural", error_location, self.variable_name], force=True)
            return False


# card(2) means "exactly 2"
class CardCardinal(object):
    def __init__(self, variable_name, h_body, count):
        self.variable_name = variable_name
        self.h_body = h_body
        self.count = count

    def meets_criteria(self, cardinal_group, cardinal_scoped_to_initial_rstr):
        cardinal_group_values_count = count_rstr(cardinal_group.original_rstr_set if cardinal_scoped_to_initial_rstr else cardinal_group.cardinal_group_values())
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
    def solution_groups(self, solutions_with_rstr, combinatorial=False):
        # Get all the unique values assigned to this variable
        variable_assignments = []
        for solution_index in range(len(solutions_with_rstr)):
            binding_value = solutions_with_rstr[solution_index][0].get_binding(self.variable_name).value
            # TODO: find a better way to remove duplicates
            unique = True
            for variable_assignment in variable_assignments:
                if binding_value == variable_assignment[0]:
                    variable_assignment[1].append(solution_index)
                    unique = False
                    break

            if unique:
                variable_assignments.append((binding_value, [solution_index]))

        if combinatorial:
            combinations_of_lists = []
            # Then get all the combinations of those sets that add up to n
            # largest set of lists that can add up to self.count is where every list is 1 item long
            for combination_size in range(1, self.count + 1):
                for combination in itertools.combinations(variable_assignments, combination_size):
                    # combination is a list of 2 element lists
                    if sum(len(item[0]) for item in combination) == self.count:
                        combinations_of_lists.append(combination)

            # Finally, return all possible combinations of solutions that contained the assignments
            # which means returning all combinations of every non-empty subset of all the lists
            # Each combination in combinations_of_lists is a list of 2 element lists:
            #   0 is a list of variable assignments
            #   1 is a list of solutions that had that assignment
            for combination in combinations_of_lists:
                for possible_solution in all_combinations_with_elements_from_all([combination_item[1] for combination_item in combination]):
                    print(f"combination: {combination}\n   solution:")
                    combination_solutions = []
                    for index in possible_solution:
                        print(f"   {solutions_with_rstr[index][0]}")
                        combination_solutions.append(solutions_with_rstr[index])

                    yield combination_solutions

        else:
            if sum(len(item[0]) for item in variable_assignments) != self.count:
                return

            yield solutions_with_rstr


# Given a list of lists, returns another list of lists
# with all combinations of items from the original lists
# ensuring there is always one item from every list
def all_combinations_with_elements_from_all(list_of_lists):
    # returns nonempty subsets of list items
    def non_empties(items):
        subsets = []
        n = len(items)
        for i in range(1, n + 1):
            subsets.extend(itertools.combinations(items, i))
        return subsets

    all_combinations_of_each_list = [non_empties(items) for items in list_of_lists]
    combs = [list(itertools.chain(*answer)) for answer in itertools.product(*all_combinations_of_each_list)]
    return combs


# For implementing things like "a few" where there is a number
# between 3 and, say 5
class BetweenCardinal(object):
    def __init__(self, variable_name, h_body, min_count, max_count):
        self.variable_name = variable_name
        self.h_body = h_body
        self.min_count = min_count
        self.max_count = max_count

    def meets_criteria(self, cardinal_group, cardinal_scoped_to_initial_rstr):
        cardinal_group_values_count = count_rstr(cardinal_group.original_rstr_set if cardinal_scoped_to_initial_rstr else cardinal_group.cardinal_group_values())
        error_location = ["AtPredication", self.h_body, self.variable_name] if cardinal_scoped_to_initial_rstr else ["AfterFullPhrase", self.variable_name]
        if cardinal_group_values_count > self.max_count:
            report_error(["tooMany", error_location], force=True)
            return False

        elif cardinal_group_values_count < self.min_count:
            report_error(["notEnough", error_location], force=True)
            return False

        else:
            return True


# After a set of answers is generated, terms that support both coll and dist will generate both options
# just in case other predications use either of them.  But, if nobody ends up using them, they are just duplicates
# remove them here
def RemoveDuplicates(solutions):
    if len(solutions) == 0:
        return []

    # Go through each variable in all solutions and see if it is coll or dist and used dist
    variables = solutions[0].get_binding("tree").value[0]["Variables"]
    variable_names = [variable_name for variable_name in variables if variable_name[0] == "x"]
    variable_states = {}
    for solution in solutions:
        for variable_name in variable_names:
            if variable_name not in variable_states:
                variable_states[variable_name] = {"Coll": False, "Dist": False, "UsedColl": False}
            binding = solution.get_binding(variable_name)
            if binding.variable.value_type in [VariableValueType.collective, VariableValueType.combinatoric_collective]:
                variable_states[variable_name]["Coll"] = True
            else:
                variable_states[variable_name]["Dist"] = True

            if binding.variable.used_collective:
                variable_states[variable_name]["UsedColl"] = True

    # The final plural just generates duplicates if it goes through both coll and dist
    # If a variable has only coll or only dist answers keep it
    # If a variable has both coll and dist: if coll_used only keep the dist
    # An answer is kept if it is UsedColl
    unique_solutions = []
    for solution in solutions:
        duplicate = False
        for variable_name in variable_names:
            # If a variable has only coll or only dist answers keep all of whichever it has
            if variable_states[variable_name]["Coll"] != variable_states[variable_name]["Dist"]:
                continue

            # If a solution has a variable that used coll, keep that
            if solution.get_binding(variable_name).variable.used_collective:
                continue

            # Otherwise, keep it if it is dist
            if solution.get_binding(variable_name).variable.value_type in [VariableValueType.distributive, VariableValueType.combinatoric_distributive]:
                continue

            duplicate = True
            break

        if not duplicate:
            unique_solutions.append(solution)

    return unique_solutions


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
