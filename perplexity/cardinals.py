import copy

from perplexity.execution import report_error
from perplexity.tree import rewrite_tree_predications, TreePredication, find_predications_in_list_in_list, \
    split_predications_consuming_event

# Rewrite the cardinal to a form that takes scope
from perplexity.utilities import parse_predication_name, is_plural


def yield_coll_or_dist(state, binding, value_set):
    if len(value_set) == 0:
        return

    if binding.variable.is_collective:
        yield state.set_x(binding.variable.name, value_set)

    else:
        for value in value_set:
            yield state.set_x(binding.variable.name, value)


def yield_all(set_or_answer):
    if isinstance(set_or_answer, list):
        for item in set_or_answer:
            yield from yield_all(item)
    else:
        yield set_or_answer


# For phrases like "files are large" or "only 2 files are large" we need a gate around
# the quantifier that only returns answers if they meet some criteria
# Note that the thing being counted is the actual rstr values, so [a, b] would count as
# 2
def gate_func_from_binding(state, binding):
    if is_plural(state, binding.variable.name):
        return plural_gate
    else:
        return no_gate


def no_gate(rstr_value, answers, gate_info, finish=False):
    yield from yield_all(answers)


def plural_gate(rstr_value, answers, gate_info, finish=False):
    if len(gate_info.keys()) == 0:
        gate_info["Gate"] = "plural_gate"
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
                gate_info["Answers"] = []

