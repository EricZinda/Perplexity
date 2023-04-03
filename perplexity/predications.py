import enum
import itertools

from perplexity.cardinals import count_set
from perplexity.variable_binding import VariableValueType


class VariableValueSetSize(enum.Enum):
    all = 0
    more_than_one = 1
    exactly_one = 2


# Yields each possible variable set from binding based on what type of value it is
# "discrete" means it will generate specific all possible sets (i.e. not yield a combinatoric value)
def discrete_variable_set_generator(binding, set_size):
    if binding.variable.value_type == VariableValueType.set:
        binding_value = binding.value
        if set_size == VariableValueSetSize.all or \
           (set_size == VariableValueSetSize.more_than_one and count_set(binding_value) > 1) or \
           (set_size == VariableValueSetSize.exactly_one and count_set(binding_value) == 1):
            # This is a single set that needs to be kept intact
            yield VariableValueType.set, binding.value

        return

    else:
        # Generate all possible sets
        assert binding.variable.value_type == VariableValueType.combinatoric

        min_set_size = 2 if set_size == VariableValueSetSize.more_than_one else 1
        max_set_size = 1 if set_size == VariableValueSetSize.exactly_one else len(binding.value)

        for value_set_size in range(min_set_size, max_set_size + 1):
            for value_set in itertools.combinations(binding.value, value_set_size):
                yield VariableValueType.set, value_set


def discrete_variable_individual_generator(binding):
    if binding.variable.value_type == VariableValueType.set:
        # This is a single set that needs to be kept intact
        yield VariableValueType.set, binding.value
        return

    else:
        # Generate all possible sets of 1
        assert binding.variable.value_type == VariableValueType.combinatoric

        min_set_size = 1
        max_set_size = 1

        for value_set_size in range(min_set_size, max_set_size + 1):
            for value_set in itertools.combinations(binding.value, value_set_size):
                yield VariableValueType.set, value_set


# Ensures that solutions are sets (not combinatoric) and only passes through
# individual sets if it is given a combinatoric
def individual_only_style_predication_1(state, binding, prediction_function):
    if binding.variable.value_type == VariableValueType.set:
        # Pass sets through, if it is > 1 item the predication_function should fail
        iterator = [binding.value]
    else:
        # If it is combinatoric, only pass through individuals
        iterator = [[value] for value in binding.value]

    for value in iterator:
        if prediction_function(value):
            yield state.set_x(binding.variable.name, value, VariableValueType.set)


# "'lift' style" means that:
# - a group behaves differently than an individual (like "men lifted a table")
# - thus the predication_function is called with sets of things
def lift_style_predication(state, binding1, binding2, prediction_function, binding1_set_size=VariableValueSetSize.all, binding2_set_size=VariableValueSetSize.all):
    # See if everything in binding1_set has the
    # prediction_function relationship to binding2_set
    for binding1_set_type, binding1_set in discrete_variable_set_generator(binding1, binding1_set_size):
        for binding2_set_type, binding2_set in discrete_variable_set_generator(binding2, binding2_set_size):
            # See if everything in binding1_set has the
            # prediction_function relationship to binding2_set
            success, set1_used_collective, set2_used_collective = prediction_function(binding1_set, binding2_set)
            if success:
                set1_used_collective = set1_used_collective if len(binding1_set) > 1 else False
                set2_used_collective = set2_used_collective if len(binding2_set) > 1 else False

                yield state.set_x(binding1.variable.name, binding1_set, binding1_set_type, used_collective=set1_used_collective) \
                    .set_x(binding2.variable.name,binding2_set,binding2_set_type, used_collective=set2_used_collective)


# "'in' style" means that:
# - {a, b} predicate {x, y} can be checked as a predicate x, a predicate y, etc.
# - that collective and distributive are both ok, but nothing special happens (unlike lift)
# - that the any combinatoric terms will be turned into single set terms (coll or dist)
def in_style_predication(state, binding1, binding2, prediction_function, binding1_set_size=VariableValueSetSize.all, binding2_set_size=VariableValueSetSize.all):
    # See if everything in binding1_set has the
    # prediction_function relationship to binding2_set
    for binding1_set_type, binding1_set in discrete_variable_set_generator(binding1, binding1_set_size):
        for binding2_set_type, binding2_set in discrete_variable_set_generator(binding2, binding2_set_size):
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


# "Combinatorial Style" means: preserve (or create) a combinatorial set if possible
def combinatorial_style_predication(state, binding, all_individuals_generator, predication_function):
    if binding.variable.value_type == VariableValueType.set:
        # This is a single set that needs to be kept intact
        # and succeed or fail as a unit
        all_must_succeed = True
        value_type = VariableValueType.set

    else:
        all_must_succeed = False
        value_type = VariableValueType.combinatoric

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
        yield state.set_x(binding.variable.name, values, value_type)
