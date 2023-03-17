from perplexity.execution import report_error
from perplexity.utilities import is_plural
from importlib import import_module


class StopQuantifierException(Exception):
    def __init__(self):
        pass


def yield_all(set_or_answer):
    if isinstance(set_or_answer, list):
        for item in set_or_answer:
            yield from yield_all(item)
    else:
        yield set_or_answer


# For phrases like "files are large" or "only 2 files are large" we need a gate around
# the quantifier that only returns answers if they meet some criteria
# Note that the thing being counted is the actual rstr values,
# so rstr_x = [a, b] would count as 2
def cardinal_from_binding(state, binding):
    if binding.variable.cardinal is not None:
        module_class_name = binding.variable.cardinal[0]
        module_path, class_name = module_class_name.rsplit('.', 1)
        module = import_module(module_path)
        class_constructor = getattr(module, class_name)
        return class_constructor(*binding.variable.cardinal[1])

    elif is_plural(state, binding.variable.name):
        return PluralCardinal()

    else:
        return NoCardinal()


class NoCardinal(object):
    def __init__(self):
        self.yielded_rstr_count = 0
        self.running_count = 0

    def criteria_met(self):
        return self.yielded_rstr_count > 0

    def yield_if_criteria_met(self, rstr_value, answers):
        if isinstance(rstr_value, list):
            self.running_count += len(rstr_value)
        else:
            self.running_count += 1

        yield from yield_all(answers)
        self.yielded_rstr_count += len(rstr_value)

    def yield_finish(self):
        # Force to be a generator
        if False:
            yield None

        return


class PluralCardinal(object):
    def __init__(self):
        self.yielded_rstr_count = 0
        self.running_count = 0
        self.cached_answers = []

    def criteria_met(self):
        return self.running_count > 1

    def yield_if_criteria_met(self, rstr_value, answers):
        if len(answers) > 0:
            self.cached_answers += answers
            if isinstance(rstr_value, list):
                self.running_count += len(rstr_value)
            else:
                self.running_count += 1

            if self.criteria_met():
                # We've achieved "more than one", start returning answers
                yield from yield_all(self.cached_answers)
                self.yielded_rstr_count += len(rstr_value)
                self.cached_answers = []

    def yield_finish(self):
        # Force to be a generator
        if False:
            yield None

        if not self.criteria_met():
            # If we got over 1, we already yielded them
            # So there is nothing to finish
            report_error(["notPlural"], force=True)


def plural_gate(rstr_value, answers, gate_info, finish=False):
    if len(gate_info.keys()) == 0:
        gate_info["Gate"] = "plural_gate"
        gate_info["YieldedRstrCount"] = 0
        gate_info["RunningCount"] = 0
        gate_info["Answers"] = []

    assert gate_info["Gate"] == "plural_gate"
    if finish:
        if gate_info["RunningCount"] <= 1:
            # If we got over 1, we already yielded them
            # So there is nothing to finish
            report_error(["notPlural"], force=True)

    else:
        if len(answers) > 0:
            gate_info["Answers"] += answers
            if isinstance(rstr_value, list):
                gate_info["RunningCount"] += len(rstr_value)
            else:
                gate_info["RunningCount"] += 1

            if gate_info["RunningCount"] > 1:
                # We've achieved "more than one" start returning answers
                yield from yield_all(gate_info["Answers"])
                gate_info["YieldedRstrCount"] += len(rstr_value)
                gate_info["Answers"] = []


