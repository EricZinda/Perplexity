import sys

from file_system_example.objects import Measurement
from perplexity.execution import report_error
from perplexity.utilities import is_plural
from importlib import import_module


class StopQuantifierException(Exception):
    def __init__(self):
        pass


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
    def __init__(self, variable, h_body):
        self.variable = variable
        self.h_body = h_body
        self.yielded_rstr_count = 0
        self.running_count = 0

    def criteria_met(self):
        return self.yielded_rstr_count > 0

    def yield_if_criteria_met(self, rstr_value, answers):
        self.running_count += count_rstr(rstr_value)
        yield from yield_all(answers)
        self.yielded_rstr_count += len(rstr_value)

    def yield_finish(self):
        # Force to be a generator
        if False:
            yield None

        return


class PluralCardinal(object):
    def __init__(self, variable, h_body):
        self.variable = variable
        self.h_body = h_body
        self.yielded_rstr_count = 0
        self.running_count = 0
        self.cached_answers = []

    def criteria_met(self):
        return self.running_count > 1

    def yield_if_criteria_met(self, rstr_value, answers):
        if len(answers) > 0:
            self.cached_answers += answers
            self.running_count += count_rstr(rstr_value)

            if self.criteria_met():
                # We've achieved "more than one", start returning answers
                yield from yield_all(self.cached_answers)
                self.yielded_rstr_count += len(rstr_value)
                self.cached_answers = []

    def yield_finish(self):
        # Force to be a generator
        if False:
            yield None

        if self.running_count == 0:
            # No rstrs worked, so don't return an error
            return

        elif not self.criteria_met():
            # If we got over 1, we already yielded them
            # So there is nothing to finish
            report_error(["notPlural"], force=True)


# card(2) means "exactly 2"
# This means that it doesn't actually return answers
# until yield_finish() is called because it needs to ensure that
# not more than 2 were successful
class CardCardinal(object):
    def __init__(self, variable, h_body, count):
        self.variable = variable
        self.h_body = h_body
        self.count = count
        self.yielded_rstr_count = 0
        self.running_count = 0
        self.cached_answers = []

    def criteria_met(self):
        return self.running_count == self.count

    def yield_if_criteria_met(self, rstr_value, answers):
        # Force to be a generator
        if False:
            yield None

        if len(answers) > 0:
            self.cached_answers += answers
            self.running_count += count_rstr(rstr_value)

            if self.running_count > self.count:
                # Stop at this point because "exactly 2" will fail
                # So don't keep returning answers
                raise StopQuantifierException

    def yield_finish(self):
        if self.criteria_met():
            yield from yield_all(self.cached_answers)

        else:
            if self.running_count == 0:
                # No rstrs worked, so don't return an error
                return

            elif self.running_count > self.count:
                report_error(["too many"], force=True)

            else:
                # If we got over 1, we already yielded them
                # So there is nothing to finish
                report_error(["notEnough"], force=True)


# For implementing things like "a few" where there is a number
# between 3 and, say 5
class BetweenCardinal(object):
    def __init__(self, variable, h_body, min_count, max_count):
        self.variable = variable
        self.h_body = h_body
        self.min_count = min_count
        self.max_count = max_count
        self.yielded_rstr_count = 0
        self.running_count = 0
        self.cached_answers = []

    def criteria_met(self):
        return self.min_count <= self.running_count <= self.max_count

    def yield_if_criteria_met(self, rstr_value, answers):
        # Force to be a generator
        if False:
            yield None

        if len(answers) > 0:
            self.cached_answers += answers
            self.running_count += count_rstr(rstr_value)

            if self.running_count > self.max_count:
                # Stop at this point because "exactly 2" will fail
                # So don't keep returning answers
                raise StopQuantifierException

    def yield_finish(self):
        if self.criteria_met():
            yield from yield_all(self.cached_answers)

        else:
            if self.running_count == 0:
                # No rstrs worked, so don't return an error
                return

            elif self.running_count > self.max_count:
                report_error(["too many"], force=True)

            else:
                # If we got over 1, we already yielded them
                # So there is nothing to finish
                report_error(["notEnough"], force=True)
