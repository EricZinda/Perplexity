import enum
import itertools
from perplexity.execution import get_variable_metadata, call, set_variable_execution_data, report_error
from perplexity.set_utilities import count_set
from perplexity.tree import TreePredication
from perplexity.utilities import at_least_one_generator
from perplexity.vocabulary import ValueSize


# Used for words like "large" and "small" that always force an answer to be individuals when used predicatively
# Ensures that solutions are sets (not combinatoric) and only passes through
# individuals, even if it is given a combinatoric
def individual_style_predication_1(state, binding, bound_predication_function, unbound_predication_function, greater_than_one_error):
    if binding.value is None:
        # Unbound
        for unbound_value in unbound_predication_function():
            yield state.set_x(binding.variable.name, (unbound_value, ), False)

    elif binding.variable.combinatoric is False:
        # if it is > 1 item the predication_function should fail since it is individual_style
        if len(binding.value) > 1:
            report_error(greater_than_one_error)
            return
        else:
            # Pass sets through,
            iterator = [binding.value]

    else:
        # If it is combinatoric, only pass through individuals
        iterator = [(value, ) for value in binding.value]

    for value in iterator:
        if bound_predication_function(value[0]):
            yield state.set_x(binding.variable.name, value, False)


# "'lift' style" means that:
# - a group behaves differently than an individual (like "men lifted a table")
# - thus the predication_function is called with sets of things
def lift_style_predication_2(state, binding1, binding2,
                             both_bound_prediction_function, binding1_unbound_predication_function, binding2_unbound_predication_function, all_unbound_predication_function=None,
                             binding1_set_size=ValueSize.all, binding2_set_size=ValueSize.all):

    # If nobody needs collective don't do it since it is expensive
    binding1_metadata = get_variable_metadata(binding1.variable.name)
    if binding1_metadata["ValueSize"] == ValueSize.exactly_one:
        binding1_set_size = ValueSize.exactly_one

    binding2_metadata = get_variable_metadata(binding2.variable.name)
    if binding2_metadata["ValueSize"] == ValueSize.exactly_one:
        binding2_set_size = ValueSize.exactly_one

    if binding1.value is None and binding2.value is None:
        if all_unbound_predication_function is None:
            report_error(["beMoreSpecific"], force=True)

        else:
            yield from all_unbound_predication_function()

    elif binding1.value is None:
        if binding1_unbound_predication_function is None:
            report_error(["beMoreSpecific"], force=True)
        else:
            assert False, "not yet implemented"

    elif binding2.value is None:
        if binding2_unbound_predication_function is None:
            report_error(["beMoreSpecific"], force=True)
        else:
            assert False, "not yet implemented"

    else:
        # See if everything in binding1_set has the
        # prediction_function relationship to binding2_set
        for binding1_set_type, binding1_set in discrete_variable_set_generator(binding1, binding1_set_size):
            for binding2_set_type, binding2_set in discrete_variable_set_generator(binding2, binding2_set_size):
                # See if everything in binding1_set has the
                # prediction_function relationship to binding2_set
                success = both_bound_prediction_function(binding1_set, binding2_set)
                if success:
                    yield state.set_x(binding1.variable.name, binding1_set, binding1_set_type) \
                        .set_x(binding2.variable.name, binding2_set, binding2_set_type)


# "'in' style" means that:
# - {a, b} predicate {x, y} can be checked (or do something) as {a} predicate {x}, {a} predicate {y}, etc.
# - that collective and distributive are both ok, but nothing special happens (unlike lift)
# - that the any combinatoric terms will be turned into single set terms (coll or dist)
#
# both_bound_function() is called if binding1 and binding2 are bound, etc.
def in_style_predication_2(state, binding1, binding2,
                           both_bound_function, binding1_unbound_predication_function, binding2_unbound_predication_function, all_unbound_predication_function=None,
                           binding1_set_size=ValueSize.all, binding2_set_size=ValueSize.all):
    # If nobody needs collective don't do it since it is expensive
    binding1_metadata = get_variable_metadata(binding1.variable.name)
    if binding1_metadata["ValueSize"] == ValueSize.exactly_one:
        binding1_set_size = ValueSize.exactly_one

    binding2_metadata = get_variable_metadata(binding2.variable.name)
    if binding2_metadata["ValueSize"] == ValueSize.exactly_one:
        binding2_set_size = ValueSize.exactly_one

    if binding1.value is None and binding2.value is None:
        if all_unbound_predication_function is None:
            report_error(["beMoreSpecific"], force=True)

        else:
            yield from all_unbound_predication_function()

    elif binding1.value is None or binding2.value is None:
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
                                                        False)

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


# "Combinatorial Style Predication" means: a predication that, when applied to a set, can be true
# for any chosen subset of the set. So, it gives a combinatorial answer.
# combinatorial_style_predication will preserve (or create) a combinatorial set if possible, it may
# not be possible if the incoming value is already forced to be a specific (non-combinatorial) set,
# for example
def combinatorial_style_predication_1(state, binding, bound_function, unbound_function):
    if binding.value is None:
        at_least_one = at_least_one_generator(unbound_function())
        if at_least_one is not None:
            yield state.set_x(binding.variable.name, tuple(at_least_one), True)

    else:
        if binding.variable.combinatoric is False:
            # This is a single set that needs to be kept intact
            # and succeed or fail as a unit
            all_must_succeed = True
            value_type = False

        else:
            all_must_succeed = False
            value_type = True

        values = []
        for value in binding.value:
            if bound_function(value):
                values.append(value)
            elif all_must_succeed:
                # One didn't work, so fail
                return

        if len(values) > 0:
            yield state.set_x(binding.variable.name, tuple(values), value_type)


# Yields each possible variable set from binding based on what type of value it is
# "discrete" means it will generate specific all possible sets (i.e. not yield a combinatoric value)
def discrete_variable_set_generator(binding, set_size):
    if binding.variable.combinatoric is False:
        binding_value = binding.value
        if set_size == ValueSize.all or \
           (set_size == ValueSize.more_than_one and count_set(binding_value) > 1) or \
           (set_size == ValueSize.exactly_one and count_set(binding_value) == 1):
            # This is a single set that needs to be kept intact
            yield False, binding.value

        return

    else:
        # Generate all possible sets
        assert binding.variable.combinatoric

        min_set_size = 2 if set_size == ValueSize.more_than_one else 1
        max_set_size = 1 if set_size == ValueSize.exactly_one else len(binding.value)

        for value_set_size in range(min_set_size, max_set_size + 1):
            for value_set in itertools.combinations(binding.value, value_set_size):
                yield False, value_set


def discrete_variable_individual_generator(binding):
    if binding.variable.combinatoric is False:
        # This is a single set that needs to be kept intact
        yield False, binding.value
        return

    else:
        # Generate all possible sets of 1
        assert binding.variable.combinatoric

        min_set_size = 1
        max_set_size = 1

        for value_set_size in range(min_set_size, max_set_size + 1):
            for value_set in itertools.combinations(binding.value, value_set_size):
                yield False, value_set


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

    if not reverse and len(rstr_values) == 0:
        # If the rstr was actually run (i.e. not reversed) and produced no values:
        # Ignore whatever error the RSTR produced, this is a better one
        report_error(["doesntExist", ["AtPredication", h_body, x_variable_binding.variable.name]], force=True)
