import copy
import enum
import itertools
import json

from perplexity.execution import get_variable_metadata, report_error, execution_context
import perplexity.plurals
from perplexity.set_utilities import all_nonempty_subsets, product_stream
from perplexity.utilities import at_least_one_generator
from perplexity.vocabulary import ValueSize


def is_concept(o):
    return hasattr(o, "is_concept") and o.is_concept()

class Concept(object):
    def __init__(self, concept_name, dict_modifications = None):
        self.concept_name = concept_name
        self._modifiers = {"noun": concept_name}
        self._hash = None
        if dict_modifications is not None:
            self._modifiers.update(dict_modifications)

    def __repr__(self):
        return f"concept({self._modifiers})"

    # The only required property is that objects which compare equal have the same hash value
    # But: objects with the same hash aren't required to be equal
    # It must remain the same for the lifetime of the object
    def __hash__(self):
        if self._hash is None:
            # TODO: Make this more efficient
            self._hash = hash(self.concept_name)

        return self._hash

    def __eq__(self, other):
        return isinstance(other, Concept) and self._hash == other._hash and self._modifiers == other._modifiers

    def is_concept(self):
        return True

    def modifiers(self):
        # Make a copy since this object must be immutable due to
        # the fact that hash is based on the modifiers
        return copy.deepcopy(self._modifiers)

    def update_modifiers(self, dict_modifications):
        modified = copy.deepcopy(self)
        modified._modifiers.update(dict_modifications)
        modified._hash = None
        return modified


# Return a new variable_constraints object that is the intersection of what the constraints
# on the variable are, intersected with what is available
# Find a value that is true for available_constraints that is also true for variable_constraints
# Works because the solution group has been checked to make sure it is valid for the whole range that
# variable_constraints defines
# This gets called when a variable holds a concept and a constraint and we want to see if we can fulfil it
# with instances.
# Theory: we are talking about both concepts ("I'd like the menu", "I'd like the 2 menus", "I'd like a menu"
# and instances "I'd like 2 menus" (instances),
# Returns:
#   True if the user is talking about concepts and the concept count meets the constraints
#   False if the same for instances
#   None

def meets_constraint(variable_constraints, concept_count, concept_in_scope_count, instance_count, instance_in_scope_count, check_concepts, variable):
    if variable_constraints.global_criteria == perplexity.plurals.GlobalCriteria.all_rstr_meet_criteria:
        # This means the entire set of things must meet the variable constraints
        if check_concepts:
            # If this is a concept check we only ever check the concept_in_scope_count here because the user
            # said something with "the" like "the menu" and this only makes sense for concepts that are
            # in scope not the generic version of "menu"
            check_count = concept_in_scope_count
        else:
            check_count = instance_count
    else:
        if check_concepts:
            # Because we are not dealing with all_rstr_meet_criteria, the phrase was something like "we want menus"
            # Which is talking about abstract menus which implies:
            # 1. There is a single concept of "menu" that is obvious
            # 2. There are enough instances of it to fulfil the request
            if concept_count == 1:
                check_count = instance_count
            else:
                report_error(["moreThan", ["AfterFullPhrase", variable], 1], force=True)
        else:
            check_count = instance_count

    # Otherwise we are talking about instances as in "I'd like a/2/a few menus"
    # Constraints with no global criteria just get merged to most restrictive
    if check_count >= variable_constraints.min_size:
        # As long as we meet the min size we can fulfil the request
        return True

    else:
        report_error(["lessThan", ["AfterFullPhrase", variable], variable_constraints.min_size], force=True)

    return False




# how a particular VariableDescriptor handles
# a individual or group
class VariableStyle(enum.Enum):
    # this size is semantically relevant
    semantic = 1
    # this size is accepted but not semantically different than the semantic style
    ignored = 2
    # this size is not supported - should fail
    unsupported = 3


# Describes the semantic for a particular argument of a predication:
# Whether individuals or groups have a special semantic meaning, are allowed
# but ignored, or are unsupported
#
# Examples:
#   large:  VariableDescriptor(individual=VariableStyle.semantic, group=VariableStyle.unsupported)
#   met:    VariableDescriptor(individual=VariableStyle.unsupported, group=VariableStyle.semantic)
#   in:     VariableDescriptor(individual=VariableStyle.semantic, group=VariableStyle.ignored), VariableDescriptor(individual=VariableStyle.semantic, group=VariableStyle.ignored)
#   lift:   VariableDescriptor(individual=VariableStyle.semantic, group=VariableStyle.semantic), VariableDescriptor(individual=VariableStyle.semantic, group=VariableStyle.semantic)
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


# Yields each possible variable set from binding based on what type of value it is
# "discrete" means it will generate all possible specific sets, one by one (i.e. not yield a combinatoric value)
# variable_size is the only sizes that should be generated or allowed
def discrete_variable_generator(value, combinatoric, variable_size):
    if combinatoric is False:
        # Fail immediately if we don't support it
        if (len(value) == 1 and variable_size == ValueSize.more_than_one) or \
                (len(value) > 1 and variable_size == ValueSize.exactly_one):
            report_error(["tooManyItemsTogether"])

        else:
            yield value

    else:
        # Generate all possible sets
        min_set_size = 2 if variable_size == ValueSize.more_than_one else 1
        max_set_size = 1 if variable_size == ValueSize.exactly_one else len(value)

        for value_set_size in range(min_set_size, max_set_size + 1):
            for value_set in itertools.combinations(value, value_set_size):
                yield value_set


# Main helper for a predication that takes 1 argument
def predication_1(state, binding, bound_function, unbound_function, binding_descriptor=None):
    if binding.value is None:
        # Unbound
        for unbound_value in unbound_function():
            yield state.set_x(binding.variable.name, unbound_value, combinatoric=False)

    else:
        # Build a generator that only generates the discrete values for the binding that are valid for the descriptor,
        # failing for a value (but continuing to iterate) if the binding can't handle the size of a particular value
        # if binding.variable.combinatoric:
        binding_generator = discrete_variable_generator(binding.value, binding.variable.combinatoric,
                                                        binding_descriptor.combinatoric_size(binding))

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


# Yield a state where each variable in combinatorial_x_values has been assigned
# one of the values that wasn't used, but in every combination *across* the variables
def all_combinations_of_states(original_state, combinatorial_x_values):
    if len(combinatorial_x_values) == 0:
        yield original_state
    else:
        combinatorial_x_variables_values = list(combinatorial_x_values.values())
        combinatorial_x_variables_names = list(combinatorial_x_values.keys())

        # Build a list of generators for each combinatorial x value that generates all
        # of the values that might be needed
        data_list = []
        for variable_index in range(len(combinatorial_x_variables_names)):
            binding_metadata = get_variable_metadata(combinatorial_x_variables_names[variable_index])
            variable_size = binding_metadata["ValueSize"]
            if variable_size == ValueSize.exactly_one:
                min_size = 1
                max_size = 1
            elif variable_size == ValueSize.more_than_one:
                min_size = 2
                max_size = len(combinatorial_x_variables_values[variable_index])
            else:
                min_size = 1
                max_size = len(combinatorial_x_variables_values[variable_index])

            data_list.append(iter(all_nonempty_subsets(combinatorial_x_variables_values[variable_index],
                                                       min_size=min_size,
                                                       max_size=max_size)))

        for combination in product_stream(*iter(data_list)):
            combination_list = list(combination)
            new_state = original_state
            for variable_index in range(len(combinatorial_x_variables_names)):
                new_state = new_state.set_x(combinatorial_x_variables_names[variable_index], combination_list[variable_index])
            yield new_state


# Main helper for a predication that takes 2 arguments
#
# There is a lot that gets done here automatically:
# 1. What combinations are used:
#   - Sets that are created by other predications are always passed through
#   - Sets get generated from combinatorial variables if this or other predications declare that they need them
#
# 2. How truth of a predication gets checked
#     - Predications that only semantically handle single values use "cartesian product checking" to check sets
#     - No matter how it is checked the variable sets are preserved
#
# 3. What kinds of sets a predication *can handle*:
#     - If this predication *can't handle* a size of set, an error will be generated automatically
# TODO: BUG: if the user doesn't *also* declare it, upstream predications may not generate it.
#       Should be able to assert this at runtime?
def predication_2(state, binding1, binding2,
                  both_bound_function, binding1_unbound_predication_function, binding2_unbound_predication_function, all_unbound_predication_function=None,
                  binding1_descriptor=None,
                  binding2_descriptor=None):
    # Build a generator that only generates the discrete values for the binding that are valid for these descriptors,
    # failing for a value (but continuing to iterate) if the binding can't handle the size of a particular value
    binding1_generator = discrete_variable_generator(binding1.value, binding1.variable.combinatoric, binding1_descriptor.combinatoric_size(binding1))

    # The binding2 generator needs to be a function because it can be iterated over multiple times
    # and needs a way to reset
    # if binding2.variable.combinatoric:
    def binding2_generator_creator_combinatoric():
        return discrete_variable_generator(binding2.value, binding2.variable.combinatoric,
                                           binding2_descriptor.combinatoric_size(binding2))

    binding2_generator_reset = binding2_generator_creator_combinatoric

    # If binding_descriptor.group == VariableStyle.unsupported no sets > 1 will even show up, and this means that
    # an individual_check is the same as a group check so we don't need to consider that case
    binding1_individual_check = binding1_descriptor.individual == VariableStyle.semantic and binding1_descriptor.group == VariableStyle.ignored
    binding2_individual_check = binding2_descriptor.individual == VariableStyle.semantic and binding2_descriptor.group == VariableStyle.ignored

    # At this point the generators will *only* be generating sets that the binding_descriptor has said the binding can handle
    # so we only need to decide how to check if the relation is true
    if binding1.value is None and binding2.value is None:
        if all_unbound_predication_function is None:
            report_error(["beMoreSpecific"], force=True)

        else:
            yield from all_unbound_predication_function()

    elif binding1.value is None or binding2.value is None:
        # Only one binding is unbound: remember which is which
        bound_binding_generator = binding2_generator_reset() if binding1.value is None else binding1_generator
        bound_binding_individual_check = binding2_individual_check if binding1.value is None else binding1_individual_check
        bound_binding = binding2 if binding1.value is None else binding1
        unbound_predication_function = binding1_unbound_predication_function if binding1.value is None else binding2_unbound_predication_function
        unbound_binding = binding1 if binding1.value is None else binding2
        unbound_binding_descriptor = binding1_descriptor if binding1.value is None else binding2_descriptor
        unbound_binding_variable_size = unbound_binding_descriptor.combinatoric_size(binding1) if binding1.value is None else unbound_binding_descriptor.combinatoric_size(binding2)

        # This is a "what is in X" type question, that's why it is unbound
        # This could be something like in([mary, john], X) (where mary and john are *together* in someplace)
        # We are trying to build all the X sets that are true of [mary, john]
        # Thus, bound_set could have more than one item, in which case we need to find the intersection of answers
        # Do the intersection of answers from every item in the set to see end up with a single set
        # where mary and john are *together*
        for bound_set in bound_binding_generator:
            # Check each item in bound_set individually if there is no set semantic
            bound_binding_item_generator = [(x,) for x in bound_set] if bound_binding_individual_check else [bound_set]

            # This is a dict() because order matters for things like location
            intersection_last = dict()
            intersection_new = dict()
            first_bound_value = True
            for bound_value in bound_binding_item_generator:
                # Get all the unbound items that are true for this bound_value
                # Each bound_value generates a group of unbound_sets for which it is true
                # Every unbound_set that is true for *everyone* gets put into a set
                # As long as a bound_value matches one of the unbound_sets that is true for everyone we keep going.
                # As soon as one bound value does not match any, we abort and none are true
                for unbound_set in unbound_predication_function(bound_value):
                    assert unbound_binding_descriptor.group == VariableStyle.semantic or \
                           (unbound_binding_descriptor.group == VariableStyle.ignored and len(unbound_set) == 1), \
                           "Values yielded from the unbound function must be a set of 1 item only since unbound_binding_descriptor.group == VariableStyle.ignored"

                    if first_bound_value:
                        # All of the unbound items from the first bound item succeed
                        # since there is nothing to intersect with yet
                        intersection_new[unbound_set] = None

                    elif unbound_set in intersection_last:
                        # At least one unbound value for this bound value worked.
                        # intersection_new records each unbound_set that this bound_value
                        # yielded which match something another bound_value yielded
                        intersection_new[unbound_set] = None

                first_bound_value = False
                if len(intersection_new) == 0:
                    intersection_last = intersection_new
                    break
                else:
                    intersection_last = intersection_new
                    intersection_new = {}

            if len(intersection_last) > 0:
                # Now we have a set of sets that have the predication relation for all elements of bound_set
                #
                # If the unbound variable is group=semantic: Mary might be in [home, park] and each unbound value returned it true for all items in the list,
                #                                                return items from the set one by one
                # If the unbound variable is group=ignore: We should only get single values and we intersect them all to create a group,
                #                                           Do the intersection of answers from every item in the set to see end up with a single set
                #                                           where mary and john are *together*. All combinations of the final group are answers
                if unbound_binding_descriptor.group == VariableStyle.semantic:
                    # Each of the items in intersection_last is a set for which all bound values is true, return them one by one
                    for group_semantic_item in intersection_last.keys():
                        yield state.set_x(bound_binding.variable.name,
                                          bound_set,
                                          combinatoric=False).set_x(unbound_binding.variable.name,
                                                                    group_semantic_item,
                                                                    combinatoric=False)
                else:
                    # unbound_binding_descriptor.group == VariableStyle.ignore
                    # Each of the items in intersection_last is true for all bound values, return all combinations
                    flattened_solutions = tuple(x[0] for x in intersection_last.keys())
                    for alternative in discrete_variable_generator(flattened_solutions, True, unbound_binding_variable_size):
                        yield state.set_x(bound_binding.variable.name,
                                          bound_set,
                                          combinatoric=False).set_x(unbound_binding.variable.name,
                                                                    alternative,
                                                                    combinatoric=False)

    else:
        # To make it easy for a developer we will do the "cartesian product check" if descriptor.group == VariableStyle.ignored
        # by calling the check function with every pair of individuals.
        # Otherwise, we call the passed in function with the entire set
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
# Ensures that solutions are discrete (not combinatoric) and only passes through individuals, even if it is given a combinatoric
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
# - that any combinatoric terms will be turned into single set terms (coll or dist)
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

