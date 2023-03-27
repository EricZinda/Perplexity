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
# This means that it doesn't actually return answers
# until yield_finish() is called because it needs to ensure that
# not more than 2 were successful
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


# yields each possible variable set from binding based on what type of value it is
# "discrete" means it will generate specific coll or dist groups
# If a variable is combinatoric it means it represents all combinations of values in that set
def discrete_variable_set_generator(binding):
    if binding.variable.value_type == VariableValueType.collective or binding.variable.value_type == VariableValueType.distributive:
        # This is a single set that needs to be kept intact
        yield binding.variable.value_type, binding.value
        return

    elif binding.variable.value_type == VariableValueType.combinatoric_collective:
        # Any groups we create need to be > 1 item and set to collective
        min_set_size = 2
        max_set_size = len(binding.value)
        value_type = VariableValueType.collective

    elif binding.variable.value_type == VariableValueType.combinatoric_distributive:
        # Create groups of maximum size 1 and set to distributive
        min_set_size = 1
        max_set_size = 1
        value_type = VariableValueType.distributive

    else:
        # binding.variable.value_type == VariableValueType.combinatoric_either:
        # TODO: Should never get here because the quantifier will set one or the other of coll/dist
        assert False

    for value_set_size in range(min_set_size, max_set_size + 1):
        for value_set in itertools.combinations(binding.value, value_set_size):
            yield value_type, value_set


# "'lift' style" means that:
# - coll behaves differently than dist (like "men lifted a table")
# - thus the predication_function is called with sets of things
def lift_style_predication(state, binding1, binding2, prediction_function):
    # See if everything in binding1_set has the
    # prediction_function relationship to binding2_set
    for binding1_set_type, binding1_set in discrete_variable_set_generator(binding1):
        for binding2_set_type, binding2_set in discrete_variable_set_generator(binding2):
            # See if everything in binding1_set has the
            # prediction_function relationship to binding2_set
            success, set1_used_collective, set2_used_collective = prediction_function(binding1_set, binding2_set)
            if success:
                set1_used_collective = set1_used_collective if is_collective_type(binding1_set_type) else False
                set2_used_collective = set2_used_collective if is_collective_type(binding2_set_type) else False

                yield state.set_x(binding1.variable.name, binding1_set, binding1_set_type, used_collective=set1_used_collective) \
                    .set_x(binding2.variable.name,binding2_set,binding2_set_type, used_collective=set2_used_collective)


# "'in' style" means that:
# - {a, b} predicate {x, y} can be checked as a predicate x, a predicate y, etc.
# - that collective and distributive are both ok, but nothing special happens (unlike lift)
# - that the any combinatoric terms will be turned into single set terms (coll or dist)
def in_style_predication(state, binding1, binding2, prediction_function):
    # See if everything in binding1_set has the
    # prediction_function relationship to binding2_set
    for binding1_set_type, binding1_set in discrete_variable_set_generator(binding1):
        for binding2_set_type, binding2_set in discrete_variable_set_generator(binding2):
            # See if everything in binding1_set has the
            # prediction_function relationship to binding2_set
            sets_fail = False
            for binding1_item in binding1_set:
                for binding2_item in binding2_set:
                    if not prediction_function(binding1_item, binding2_item):
                        sets_fail = True
                        break
                if sets_fail:
                    break

            if not sets_fail:
                yield state.set_x(binding1.variable.name,
                                  binding1_set,
                                  binding1_set_type).set_x(binding2.variable.name,
                                                           binding2_set,
                                                           binding2_set_type)


# combinatorial_style means: preserve (or create) a combinatorial set if possible
def combinatorial_style_predication(state, binding, all_individuals_generator, predication_function):
    all_must_succeed = False
    if binding.variable.value_type == VariableValueType.collective:
        # This is a single set that needs to be kept intact
        # and succeed or fail as a unit
        all_must_succeed = True

    elif binding.variable.value_type == VariableValueType.distributive:
        # This is a set of 1, no special handling
        pass

    elif binding.variable.value_type == VariableValueType.combinatoric_collective:
        # If any singular items fail, what to do?
        # Just return the successful set as combinatoric_collective
        pass

    elif binding.variable.value_type == VariableValueType.combinatoric_distributive:
        # This is a set of N that should be treated like a set of N sets of 1
        pass

    else:
        # binding.variable.value_type == VariableValueType.combinatoric_either:
        # Should never get here because the quantifier will set one or the other of coll/dist
        assert False

    if binding.value is None:
        # Unbound variable means the incoming set contains "all individuals"
        iterator = all_individuals_generator

    else:
        # x is set to a set of values, restrict them to just those that match the predication_function
        iterator = binding.value

    values = []
    for value in iterator:
        if predication_function(value):
            values.append(value)
        elif all_must_succeed:
            # One didn't work, so fail
            return

    if len(values) > 0:
        yield state.set_x(binding.variable.name, values, binding.variable.value_type)


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
