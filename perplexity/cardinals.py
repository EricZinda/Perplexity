import sys

from file_system_example.objects import Measurement
from perplexity.execution import report_error
from perplexity.utilities import is_plural
from importlib import import_module


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
        if cardinal_group_values_count > 1:
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

