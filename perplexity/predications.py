import enum
import itertools

from perplexity.execution import get_variable_metadata, call, set_variable_execution_data, report_error
from perplexity.set_utilities import count_set
from perplexity.tree import TreePredication
from perplexity.variable_binding import VariableValueType
from perplexity.vocabulary import PluralType


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


# Used for words like "large" and "small" that always force an answer to be individuals
# if used predicatively
# Ensures that solutions are sets (not combinatoric) and only passes through
# individuals, even if it is given a combinatoric
def force_individual_style_predication_1(state, binding, bound_predication_function, unbound_predication_function):
    if binding.value is None:
        # Unbound
        for unbound_value in unbound_predication_function():
            yield state.set_x(binding.variable.name, (unbound_value, ), VariableValueType.set)

    elif binding.variable.value_type == VariableValueType.set:
        # Pass sets through, if it is > 1 item the predication_function should fail
        iterator = [binding.value]

    else:
        # If it is combinatoric, only pass through individuals
        iterator = [(value, ) for value in binding.value]

    for value in iterator:
        if bound_predication_function(value):
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
                    .set_x(binding2.variable.name, binding2_set, binding2_set_type, used_collective=set2_used_collective)


# "'in' style" means that:
# - {a, b} predicate {x, y} can be checked as a predicate x, a predicate y, etc.
# - that collective and distributive are both ok, but nothing special happens (unlike lift)
# - that the any combinatoric terms will be turned into single set terms (coll or dist)
#
# both_bound_function() is called if binding1 and binding2 are bound, etc.
def in_style_predication(state, binding1, binding2,
                         both_bound_function, binding1_unbound_predication_function, binding2_unbound_predication_function,
                         binding1_set_size=VariableValueSetSize.all, binding2_set_size=VariableValueSetSize.all):
    # If nobody needs collective don't do it since it is expensive
    binding1_metadata = get_variable_metadata(binding1.variable.name)
    if binding1_metadata["PluralType"] == PluralType.distributive:
        binding1_set_size = VariableValueSetSize.exactly_one

    binding2_metadata = get_variable_metadata(binding2.variable.name)
    if binding2_metadata["PluralType"] == PluralType.distributive:
        binding2_set_size = VariableValueSetSize.exactly_one

    if binding1.value is None or binding2.value is None:
        # TODO: deal with when everything is unbound
        assert not(binding1.value is None and binding2.value is None)
        bound_binding = binding2 if binding1.value is None else binding1
        bound_set_size = binding2_set_size if binding1.value is None else binding1_set_size
        unbound_binding = binding1 if binding1.value is None else binding2
        unbound_predication_function = binding1_unbound_predication_function if binding1.value is None else binding2_unbound_predication_function

        # This is a "what is in X" type question, that's why it is unbound
        for bound_set_type, bound_set in discrete_variable_set_generator(bound_binding, bound_set_size):
            # this could be in([mary, john], X) (where are mary and john together)
            # thus, binding1_set could have more than one item, in which case we need to find the intersection of answers
            # Do the intersection of answers from every item in the set to see where mary and john are *together*
            first_value = True
            # Order matters, so use a dict.  That way we return the first value first
            intersection_all = {}
            for bound_value in bound_set:
                for unbound_value in unbound_predication_function(bound_value):
                    if first_value:
                        intersection_all[unbound_value] = None
                    else:
                        if unbound_value not in first_value:
                            return

                first_value = False

            # Now we have a non-zero intersection of values for all items in binding1_set
            for unbound_value in intersection_all.keys():
                yield state.set_x(bound_binding.variable.name,
                                  bound_set,
                                  bound_set_type).set_x(unbound_binding.variable.name,
                                                        (unbound_value, ),
                                                        VariableValueType.set)

    else:
        # See if everything in binding1_set has the
        # prediction_function relationship to binding2_set
        for binding1_set_type, binding1_set in discrete_variable_set_generator(binding1, binding1_set_size):
            for binding2_set_type, binding2_set in discrete_variable_set_generator(binding2, binding2_set_size):
                # See if everything in binding1_set has the
                # prediction_function relationship to binding2_set
                sets_fail = False
                for binding1_item in binding1_set:
                    for binding2_item in binding2_set:
                        if not both_bound_function(binding1_item, binding2_item):
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


# "Combinatorial Style Predication" means: a predication that, when applied to a set, will be true
# for any chosen subset of the set. So, it gives a combinatorial answer.
# combinatorial_style_predication will preserve (or create) a combinatorial set if possible, it may
# not be possible if the incoming value is already forced to be a specific (non-combinatorial) set,
# for example
def combinatorial_style_predication_1(state, binding, all_individuals_generator, predication_function):
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
        yield state.set_x(binding.variable.name, tuple(values), value_type)


def rstr_reorderable(rstr):
    return isinstance(rstr, TreePredication) and rstr.name in ["place_n", "thing"]


# Yield all undetermined, unquantified answers
def quantifier_raw(state, x_variable_binding, h_rstr_orig, h_body_orig, criteria_predication=None):
    reverse = rstr_reorderable(h_rstr_orig)
    h_rstr = h_body_orig if reverse else h_rstr_orig
    h_body = h_rstr_orig if reverse else h_body_orig

    variable_name = x_variable_binding.variable.name
    rstr_values = []
    for rstr_solution in call(state, h_rstr):
        if criteria_predication is not None:
            alternative_states = criteria_predication(rstr_solution, rstr_solution.get_binding(x_variable_binding.variable.name))
        else:
            alternative_states = [rstr_solution]

        for alternative_state in alternative_states:
            rstr_values.extend(alternative_state.get_binding(variable_name).value)
            for body_solution in call(alternative_state, h_body):
                yield body_solution

    set_variable_execution_data(variable_name, "AllRstrValues", rstr_values)

    if len(rstr_values) == 0:
        # Ignore whatever error the RSTR produced, this is a better one
        report_error(["doesntExist", ["AtPredication", h_body, x_variable_binding.variable.name]], force=True)
