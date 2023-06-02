import enum
import itertools
from perplexity.execution import get_variable_metadata, call, set_variable_execution_data, report_error
from perplexity.set_utilities import count_set
from perplexity.tree import TreePredication
from perplexity.utilities import at_least_one_generator
from perplexity.vocabulary import ValueSize


class VariableStyle(enum.Enum):
    # this size is semantically relevant
    semantic = 1
    # this size is accepted, but treated as the semantic style
    ignored = 2
    # this size is not supported - should fail
    unsupported = 3


class VariableDescriptor(object):
    def __init__(self, individual, group):
        assert individual == VariableStyle.semantic or group == VariableStyle.semantic, "at least one of individual or group must be semantic"
        self.individual = individual
        self.group = group

    def individual_check_only(self):
        return self.individual == VariableStyle.semantic and \
               (self.group == VariableStyle.ignored or self.group == VariableStyle.unsupported)

    def combinatoric_size(self, binding):
        binding_metadata = get_variable_metadata(binding.variable.name)
        individual_consumed = binding_metadata["ValueSize"] == ValueSize.exactly_one or binding_metadata["ValueSize"] == ValueSize.all
        combinatorial_exactly_one = self.individual == VariableStyle.semantic or \
                                    (self.individual == VariableStyle.ignored and individual_consumed)

        group_consumed = binding_metadata["ValueSize"] == ValueSize.more_than_one or binding_metadata["ValueSize"] == ValueSize.all
        combinatorial_more_than_one = self.group == VariableStyle.semantic or \
                                      (self.group == VariableStyle.ignored and group_consumed)

        if combinatorial_exactly_one and combinatorial_more_than_one:
            return ValueSize.all
        else:
            return ValueSize.exactly_one if combinatorial_exactly_one else ValueSize.more_than_one

    def discrete_size(self):
        group_supported = self.group == VariableStyle.semantic or self.group == VariableStyle.ignored
        individual_supported = self.individual == VariableStyle.semantic or self.individual == VariableStyle.ignored
        if group_supported and individual_supported:
            return ValueSize.all
        else:
            return ValueSize.exactly_one if individual_supported else ValueSize.more_than_one


# Yields each possible variable set from binding based on what type of value it is
# "discrete" means it will generate all possible specific sets, one by one (i.e. not yield a combinatoric value)
# variable_size is the only sizes that should be generated or allowed
def discrete_variable_generator(value, combinatoric, variable_size):
    if combinatoric is False:
        # Fail immediately if we don't support it
        if (len(value) == 1 and variable_size == ValueSize.more_than_one) or \
                (len(value) > 1 and variable_size == ValueSize.exactly_one):
            report_error()

        else:
            yield value

    else:
        # Generate all possible sets
        min_set_size = 2 if variable_size == ValueSize.more_than_one else 1
        max_set_size = 1 if variable_size == ValueSize.exactly_one else len(value)

        for value_set_size in range(min_set_size, max_set_size + 1):
            for value_set in itertools.combinations(value, value_set_size):
                yield value_set


def predication_1(state, binding,
                  bound_function, unbound_function,
                  binding_descriptor=None):

    if binding.value is None:
        # Unbound
        for unbound_value in unbound_function():
            yield state.set_x(binding.variable.name, unbound_value, combinatoric=False)

    else:
        # Build a generator that only generates the discrete values for the binding that are valid for the descriptor,
        # failing for a value (but continuing to iterate) if the binding can't handle the size of a particular value
        if binding.variable.combinatoric:
            binding_generator = discrete_variable_generator(binding.value, binding.variable.combinatoric,
                                                            binding_descriptor.combinatoric_size(binding))
        else:
            binding_generator = discrete_variable_generator(binding.value, binding.variable.combinatoric,
                                                            binding_descriptor.discrete_size())

        for value in binding_generator:
            if bound_function(value):
                yield state.set_x(binding.variable.name, value, False)


# "Combinatorial Style Predication" means: a predication that, when applied to a set, can be true
# for any chosen subset of the set. So, it gives a combinatorial answer.
#
# Its binding is always of type VariableDescriptor(individual=semantic, group=ignored)
#
# combinatorial_style_predication will preserve (or create) a combinatorial set if possible, it may
# not be possible if the incoming value is already forced to be a specific (non-combinatorial) set,
# for example
def combinatorial_predication_1(state, binding, bound_function, unbound_function):
    if binding.value is None:
        # Unbound
        at_least_one = at_least_one_generator(unbound_function())
        if at_least_one is not None:
            yield state.set_x(binding.variable.name, tuple(at_least_one), True)

    else:
        if binding.variable.combinatoric is False:
            # This is a single set that needs to be kept intact
            # and succeed or fail as a unit
            all_must_succeed = True
            combinatoric = False

        else:
            all_must_succeed = False
            combinatoric = True

        values = []
        for value in binding.value:
            if bound_function(value):
                values.append(value)

            elif all_must_succeed:
                # One didn't work, so fail
                return

        if len(values) > 0:
            yield state.set_x(binding.variable.name, tuple(values), combinatoric)


# binding1_descriptor terms:
# semantic: this size is semantically relevant
# ignored_sizes: this size is accepted, but treated as the semantic style
# unsupported: this size is not supported - should fail
#
# Each variable has to say if:
# exactly_one = semantic | ignored | unsupported
# more_than_one = semantic | ignored | unsupported
#
# examples:
#   large(x = {"exactly_one": semantic, "more_than_one": unsupported})
#   met(x = {"exactly_one": unsupported, "more_than_one": semantic})
#   in(x = {"exactly_one": semantic, "more_than_one": ignored})
#   lift(x = {"exactly_one": semantic, "more_than_one": semantic})
#
# Combinatorial variables:
#   should always generate semantic sizes
#   should generate ignored if other predications need them
#   should never generate unsupported
#
# TODO: BUG: if the user doesn't *also* declare it, upstream predications may not generate it.
#       Should be able to assert this at runtime?
def predication_2(state, binding1, binding2,
                  both_bound_function, binding1_unbound_predication_function, binding2_unbound_predication_function, all_unbound_predication_function=None,
                  binding1_descriptor=None,
                  binding2_descriptor=None):

    # Build a generator that only generates the discrete values for the binding that are valid for these descriptors,
    # failing for a value (but continuing to iterate) if the binding can't handle the size of a particular value
    if binding1.variable.combinatoric:
        binding1_generator = discrete_variable_generator(binding1.value, binding1.variable.combinatoric, binding1_descriptor.combinatoric_size(binding1))
    else:
        binding1_generator = discrete_variable_generator(binding1.value, binding1.variable.combinatoric, binding1_descriptor.discrete_size())

    # The binding2 generator needs to be a function because it can be iterated over multiple times
    # and needs a way to reset
    if binding2.variable.combinatoric:
        def binding2_generator_creator_combinatoric():
            return discrete_variable_generator(binding2.value, binding2.variable.combinatoric,
                                               binding2_descriptor.combinatoric_size(binding2))

        binding2_generator_reset = binding2_generator_creator_combinatoric

    else:
        def binding2_generator_creator_discrete():
            return discrete_variable_generator(binding2.value, binding2.variable.combinatoric, binding2_descriptor.discrete_size())

        binding2_generator_reset = binding2_generator_creator_discrete

    # If binding_descriptor.group == VariableStyle.unsupported no sets > 1 will even show up, and this means that
    # an individual_check is the same as a group check so we don't need to consider that case
    binding1_individual_check = binding1_descriptor.individual == VariableStyle.semantic and binding1_descriptor.group == VariableStyle.ignored
    binding2_individual_check = binding2_descriptor.individual == VariableStyle.semantic and binding2_descriptor.group == VariableStyle.ignored

    # At this point the generators will *only* generate sets that the binding_descriptor has said the binding can handle
    # so we only need to decide how to check if the relation is true
    if binding1.value is None and binding2.value is None:
        if all_unbound_predication_function is None:
            report_error(["beMoreSpecific"], force=True)

        else:
            yield from all_unbound_predication_function()

    elif binding1.value is None or binding2.value is None:
        # Only one binding is unbound remember which is which
        bound_binding_generator = binding2_generator_reset() if binding1.value is None else binding1_generator
        bound_binding_individual_check = binding2_individual_check if binding1.value is None else binding1_individual_check
        bound_binding = binding2 if binding1.value is None else binding1
        unbound_predication_function = binding1_unbound_predication_function if binding1.value is None else binding2_unbound_predication_function
        unbound_binding = binding1 if binding1.value is None else binding2
        unbound_binding_descriptor = binding1_descriptor if binding1.value is None else binding2_descriptor
        unbound_binding_variable_size = unbound_binding_descriptor.discrete_size()

        # This is a "what is in X" type question, that's why it is unbound
        for bound_set in bound_binding_generator:
            # Check each item in bound_set individually if there is no set semantic
            bound_binding_item_generator = [(x,) for x in bound_set] if bound_binding_individual_check else [bound_set]

            # This could be something like in([mary, john], X) (where are mary and john together)
            # We are trying to build all the X sets that are true of [mary, john]
            # Thus, bound_set could have more than one item, in which case we need to find the intersection of answers
            # Do the intersection of answers from every item in the set to see end up with a single set
            # where mary and john are *together*
            # This is a dict() because order matters for things like location
            intersection_last = dict()
            intersection_new = dict()
            first_bound_value = True
            for bound_value in bound_binding_item_generator:
                # Get all the unbound items that are true for this bound item
                # These items will be sets of 1 or more items that represent a place that
                # one of the bound items is "in at the same time"
                # if the unbound argument is individual
                # Each bound_value generates a set of alternatives for which it is true
                # Every alternatives that is true for everyone gets put into a set
                # As long as a bound_value contains one of the alternatives that is true for everyone
                # we keep going.
                # As soon as one bound value does not have a shared value, we abort and none are true
                # Then: All combinations of the set are returned
                for unbound_set in unbound_predication_function(bound_value):
                    assert unbound_binding_descriptor.group == VariableStyle.semantic or \
                           (unbound_binding_descriptor.group == VariableStyle.ignored and len(unbound_set) == 1), \
                           "Values yielded from the unbound function must be a set of 1 item only since unbound_binding_descriptor.group == VariableStyle.ignored"

                    if first_bound_value:
                        # All of the unbound items from the first bound item succeed
                        # Since there is nothing to intersect with yet
                        intersection_new[unbound_set] = None

                    elif unbound_set in intersection_last:
                        # At least one unbound value for this bound value worked
                        # intersection_new contains the unbound values that have
                        # worked for all the bound values
                        intersection_new[unbound_set] = None

                first_bound_value = False
                if len(intersection_new) == 0:
                    intersection_last = intersection_new
                    break
                else:
                    intersection_last = intersection_new
                    intersection_new = {}

            if len(intersection_last) > 0:
                # Now we have a set of sets that have the relation for all elements of bound_set
                #
                # If the unbound variable is group=semantic: Mary might be in [home, park] and each unbound value returned it true for all items in the list,
                #                                                return them one by one
                # If the unbound variable is group=ignore: We should only get single values and we intersect them all to create a group,
                #                                           Do the intersection of answers from every item in the set to see end up with a single set
                #                                           where mary and john are *together*
                #                                           all combinations of the final group are answers
                if unbound_binding_descriptor.group == VariableStyle.semantic:
                    # Each of the items in intersection_all is a set for which all bound value is true, return them one by one
                    for group_semantic_item in intersection_last.keys():
                        yield state.set_x(bound_binding.variable.name,
                                          bound_set,
                                          combinatoric=False).set_x(unbound_binding.variable.name,
                                                                    group_semantic_item,
                                                                    combinatoric=False)
                else:
                    # unbound_binding_descriptor.group == VariableStyle.ignore
                    # Each of the items in intersection_all is true for all bound values, return all combinations
                    flattened_solutions = tuple(x[0] for x in intersection_last.keys())
                    for alternative in discrete_variable_generator(flattened_solutions, True, unbound_binding_variable_size):
                        yield state.set_x(bound_binding.variable.name,
                                          bound_set,
                                          combinatoric=False).set_x(unbound_binding.variable.name,
                                                                    alternative,
                                                                    combinatoric=False)

    else:
        # To make it easy for a developer we will do the "cartesian product check" if descriptor.group == VariableStyle.ignored by calling the check
        # function with every pair of individuals. Otherwise, we call the passed in function with the entire set
        if binding1.value is not None and binding2.value is not None:
            # See if everything in binding1_set has the prediction_function relationship to everything in binding2_set
            for binding1_set in binding1_generator:
                binding1_item_generator = [(x,) for x in binding1_set] if binding1_individual_check else [binding1_set]

                for binding2_set in binding2_generator_reset():
                    binding2_item_generator = [(x,) for x in binding2_set] if binding2_individual_check else [binding2_set]

                    sets_fail = False
                    for binding1_item in binding1_item_generator:
                        for binding2_item in binding2_item_generator:
                            if not both_bound_function(binding1_item, binding2_item):
                                sets_fail = True
                                break
                        if sets_fail:
                            break

                    if not sets_fail:
                        # Even if we checked individually, return the set as an intact set
                        yield state.set_x(binding1.variable.name,
                                          binding1_set,
                                          combinatoric=False).set_x(binding2.variable.name,
                                                                    binding2_set,
                                                                    combinatoric=False)


# Used for words like "large" and "small" that always force an answer to be individuals when used predicatively
# Ensures that solutions are discrete (not combinatoric) and only passes through
# individuals, even if it is given a combinatoric
def individual_style_predication_1(state, binding, bound_predication_function, unbound_predication_function, greater_than_one_error):
    def bound_function(value_set):
        return bound_predication_function(value_set[0])

    def unbound_function():
        for item in unbound_predication_function():
            yield (item, )

    yield from predication_1(state, binding,
                             bound_function, unbound_function,
                             VariableDescriptor(individual=VariableStyle.semantic, group=VariableStyle.unsupported))


# "'lift' style" means that:
# - a group behaves differently than an individual (like "men lifted a table")
# - thus the predication_function is called with sets of things
def lift_style_predication_2(state, binding1, binding2,
                             both_bound_prediction_function, binding1_unbound_predication_function, binding2_unbound_predication_function, all_unbound_predication_function=None,
                             binding1_set_size=ValueSize.all, binding2_set_size=ValueSize.all):

    yield from predication_2(state, binding1, binding2,
                             both_bound_prediction_function,
                             binding1_unbound_predication_function,
                             binding2_unbound_predication_function,
                             all_unbound_predication_function,
                             VariableDescriptor(individual=VariableStyle.semantic, group=VariableStyle.semantic),
                             VariableDescriptor(individual=VariableStyle.semantic, group=VariableStyle.semantic))


# "'in' style" means that:
# - {a, b} predicate {x, y} can be checked (or do something) as {a} predicate {x}, {a} predicate {y}, etc.
# - that collective and distributive are both ok, but nothing special happens (unlike lift)
# - that the any combinatoric terms will be turned into single set terms (coll or dist)
def in_style_predication_2(state, binding1, binding2,
                           both_bound_function, binding1_unbound_predication_function, binding2_unbound_predication_function, all_unbound_predication_function=None,
                           binding1_set_size=ValueSize.all, binding2_set_size=ValueSize.all):
    def both_bound_set(item1, item2):
        return both_bound_function(item1[0], item2[0])

    def binding1_unbound_predication_set_function(item2):
        for item in binding1_unbound_predication_function(item2[0]):
            yield tuple([item])

    def binding2_unbound_predication_set_function(item1):
        for item in binding2_unbound_predication_function(item1[0]):
            yield tuple([item])

    yield from predication_2(state, binding1, binding2,
                             both_bound_set,
                             binding1_unbound_predication_set_function,
                             binding2_unbound_predication_set_function,
                             all_unbound_predication_function,
                             VariableDescriptor(individual=VariableStyle.semantic, group=VariableStyle.ignored),
                             VariableDescriptor(individual=VariableStyle.semantic, group=VariableStyle.ignored))
