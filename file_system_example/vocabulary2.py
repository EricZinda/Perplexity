from file_system_example.objects import File, Folder, Megabyte, Actor
from file_system_example.state import DeleteOperation
from perplexity.determiners import determiner_solution_groups_helper
from perplexity.execution import report_error, call, execution_context
from perplexity.predications import combinatorial_style_predication, lift_style_predication, in_style_predication, \
    individual_only_style_predication_1, VariableValueSetSize, discrete_variable_set_generator, quantifier_raw
from perplexity.set_utilities import count_set, Measurement
from perplexity.tree import is_index_predication
from perplexity.utilities import is_plural_from_tree_info
from perplexity.variable_binding import VariableValueType
from perplexity.vocabulary import Vocabulary, Predication, EventOption, PluralType

vocabulary = Vocabulary()


@Predication(vocabulary, names=["_the_q"])
def the_q(state, x_variable_binding, h_rstr, h_body):
    is_plural = is_plural_from_tree_info(execution_context().tree_info, x_variable_binding.variable.name)
    if is_plural:
        # Phrases like "the children" could be any number of rstr values
        max_rstr = float('inf')

    else:
        max_rstr = 1

    state = state.set_variable_data(x_variable_binding.variable.name,
                                    quantifier=["number_constraint", "vocabulary2.the_q_group", [1, max_rstr, False]])

    yield from quantifier_raw(state, x_variable_binding, h_rstr, h_body)


# Several meanings:
# 1. Means "this" which only succeeds for rstrs that are the single in scope x set and there are no others that are in scope
#       "put the two keys in the lock": should only work if there are only two keys in scope:
#       run the rstr, run the cardinal (potentially fail), the run the body (potentially fail)
# 2. Means "the one and only" which only succeeds if the rstr is a single set and there are no other sets
#       same approach
def the_q_group(execution_context, previous_variable_name, variable_name, predication, all_rstr, solution_group, combinatorial, is_last_determiner):
    is_plural = is_plural_from_tree_info(execution_context.tree_info, variable_name)

    def criteria(rstr_value_list):
        if not is_plural and len(all_rstr) > 1:
            execution_context.report_error(["moreThan1", ["AtPredication", predication.args[2], variable_name]], force=True)
            return False

        elif len(all_rstr) != len(rstr_value_list):
            execution_context.report_error(["notTrueForAll", ["AtPredication", predication.args[2], variable_name]], force=True)
            return False

        else:
            return True

    yield from determiner_solution_groups_helper(execution_context, previous_variable_name, variable_name, solution_group, criteria, combinatorial, is_last_determiner)


@Predication(vocabulary, names=["_a_q"])
def a_q(state, x_variable_binding, h_rstr, h_body):
    state = state.set_variable_data(x_variable_binding.variable.name,
                                    quantifier=["number_constraint", "default", [1, 1, False]])

    yield from quantifier_raw(state, x_variable_binding, h_rstr, h_body)


@Predication(vocabulary, names=["udef_q", "which_q", "_which_q", "pronoun_q"])
def generic_q(state, x_variable_binding, h_rstr, h_body):
    state = state.set_variable_data(x_variable_binding.variable.name,
                                    quantifier=["number_constraint", "default", [1, float('inf'), False]])

    yield from quantifier_raw(state, x_variable_binding, h_rstr, h_body)


def variable_is_megabyte(binding):
    return binding.value is not None and len(binding.value) == 1 and isinstance(binding.value[0], Megabyte)


def value_is_measure(value):
    return value is not None and len(value) == 1 and isinstance(value[0], Measurement)


# 10 mb should not generate a set of 10 1mbs
# special case this.  Turns a megabyte into a *measure* which is a set of megabytes
@Predication(vocabulary, names=["card"])
def card_megabytes(state, c_count, e_introduced_binding, x_target_binding):
    if variable_is_megabyte(x_target_binding):
        yield state.set_x(x_target_binding.variable.name,
                          [Measurement(x_target_binding.value[0], int(c_count))],
                          value_type=VariableValueType.set)


@Predication(vocabulary, names=["card"], handles=[("DeterminerDegreeLimiter", EventOption.optional)])
def card_normal(state, c_count, e_introduced_binding, x_target_binding):
    if not variable_is_megabyte(x_target_binding):
        if e_introduced_binding.value is not None and "DeterminerDegreeLimiter" in e_introduced_binding.value:
            card_is_exactly = e_introduced_binding.value["DeterminerDegreeLimiter"]["Value"]["Only"]
        else:
            card_is_exactly = False

        yield state.set_variable_data(x_target_binding.variable.name,
                                      determiner=["number_constraint", "default", [int(c_count), int(c_count), card_is_exactly]])


@Predication(vocabulary, names=["_a+few_a_1"])
def a_few_a_1(state, e_introduced_binding, x_target_binding):
    yield state.set_variable_data(x_target_binding.variable.name,
                                  determiner=["number_constraint", "default", [3, 5, False]])


# true for both sets and individuals as long as everything
# in the set is a file
@Predication(vocabulary, names=["_file_n_of"])
def file_n_of(state, x_binding, i_binding):
    def criteria(value):
        return isinstance(value, File)

    yield from combinatorial_style_predication(state, x_binding, state.all_individuals(), criteria)


# true for both sets and individuals as long as everything
# in the set is a file
@Predication(vocabulary, names=["_folder_n_of"])
def folder_n_of(state, x_binding, i_binding):
    def criteria(value):
        return isinstance(value, Folder)

    yield from combinatorial_style_predication(state, x_binding, state.all_individuals(), criteria)


@Predication(vocabulary, names=["_megabyte_n_1"])
def megabyte_n_1(state, x_binding, u_binding):
    def criteria(value):
        return isinstance(value, Megabyte)

    yield from combinatorial_style_predication(state, x_binding, [Megabyte()], criteria)


@Predication(vocabulary)
def thing(state, x_binding):
    def criteria(_):
        return True

    yield from combinatorial_style_predication(state, x_binding, state.all_individuals(), criteria)


# "large_a" means that each individual thing in a combinatoric argument is large
# BUT: if you ask if large([a, b]) of a set as an index, it will fail
@Predication(vocabulary, names=["_large_a_1"], handles=[("DegreeMultiplier", EventOption.optional)])
def large_a_1(state, e_introduced_binding, x_target_binding):
    # See if any modifiers have changed *how* large we should be
    degree_multiplier = degree_multiplier_from_event(state, e_introduced_binding)

    if is_index_predication(state):
        def criteria_index(value):
            if len(value) > 1:
                report_error(["adjectiveDoesntApply", "large", x_target_binding.variable.name])
            else:
                if hasattr(value[0], 'size') and value[0].size > degree_multiplier * 1000000:
                    return True

                else:
                    report_error(["adjectiveDoesntApply", "large", x_target_binding.variable.name])
                    return False

        yield from individual_only_style_predication_1(state, x_target_binding, criteria_index)

    else:
        def criteria(value):
            if hasattr(value, 'size') and value.size > degree_multiplier * 1000000:
                return True

            else:
                report_error(["adjectiveDoesntApply", "large", x_target_binding.variable.name])
                return False

        yield from combinatorial_style_predication(state, x_target_binding, state.all_individuals(), criteria)


# This is a helper function that any predication that can
# be "very'd" can use to understand just how "very'd" it is
def degree_multiplier_from_event(state, e_introduced_binding):
    # if a "very" is modifying this event, use that value
    # otherwise, return 1
    if e_introduced_binding.value is None or "DegreeMultiplier" not in e_introduced_binding.value:
        degree_multiplier = 1

    else:
        degree_multiplier = e_introduced_binding.value["DegreeMultiplier"]["Value"]

    return degree_multiplier


@Predication(vocabulary, names=["_in_p_loc"])
def in_p_loc(state, e_introduced_binding, x_actor_binding, x_location_binding):
    if x_actor_binding.value is not None:
        if x_location_binding.value is not None:
            def item_in_item(item1, item2):
                # x_actor is "in" x_location if x_location contains it
                found_location = False
                for item in item2.contained_items(x_location_binding.variable):
                    if item1 == item:
                        found_location = True
                        break
                if not found_location:
                    report_error(["thingHasNoLocation", x_actor_binding.variable.name, x_location_binding.variable.name])

                return found_location

            yield from in_style_predication(state, x_actor_binding, x_location_binding, item_in_item)

    report_error(["thingHasNoLocation", x_actor_binding.variable.name, x_location_binding.variable.name])


# handles size only
# loc_nonsp will add up the size of files if a collective set of actors comes in, so declare that as handling them differently
# we treat megabytes as a group, all added up, which is different than separately (a megabyte as a time) so ditto
@Predication(vocabulary, names=["loc_nonsp"], arguments=[("e",), ("x", PluralType.all), ("x", PluralType.all)], handles=[("DeterminerSetLimiter", EventOption.optional)])
def loc_nonsp_size(state, e_introduced_binding, x_actor_binding, x_size_binding):
    def criteria(actor_set, size_set):
        if value_is_measure(size_set):
            if not x_size_binding.variable.value_type == VariableValueType.set:
                # we only deal with x megabytes as a set because dist(10 mb) is 1 mb and nobody means 10 individual megabyte when they say "2 files are 10mb"
                report_error(["formNotUnderstood", "missing", "collective"])
                return False, None, None

            # Try to add up all combinations of x_actor_binding
            # to total size_set[0]
            total = 0
            for actor in actor_set:
                if not hasattr(actor, "size_measurement"):
                    report_error(["xIsNotY", x_actor_binding.variable.name, x_size_binding.variable.name])
                    return False, None, None
                else:
                    total += actor.size_measurement().count

            if size_set[0].count == total:
                return True, True, True

            else:
                report_error(["xIsNotY", x_actor_binding.variable.name, x_size_binding.variable.name])
                return False, None, None

        else:
            return False, None, None

    if x_actor_binding.value is not None:
        if x_size_binding.value is not None:
            # If a cardinal limiter like "together" is acting on this verb, it is unclear
            # if it is for x_actor or x_size, so we have to try both
            if e_introduced_binding.value is not None and "DeterminerSetLimiter" in e_introduced_binding.value:
                set_size = e_introduced_binding.value["DeterminerSetLimiter"]["Value"]["ValueSetSize"]
            else:
                set_size = VariableValueSetSize.all

            yield from lift_style_predication(state, x_actor_binding, x_size_binding, criteria, set_size, VariableValueSetSize.all)
            yield from lift_style_predication(state, x_actor_binding, x_size_binding, criteria, VariableValueSetSize.all, set_size)


@Predication(vocabulary, names=["_only_x_deg"])
def only_x_deg_ee(state, e_introduced_binding, e_target_binding):
    info = {
        "Only": True
    }
    yield state.add_to_e(e_target_binding.variable.name, "DeterminerDegreeLimiter", {"Value": info, "Originator": execution_context().current_predication_index()})


# Used for prepositions like "together" or "separately" that modify how a verb should handle cardinality
def default_cardinal_set_limiter_norm(state, e_introduced_binding, e_target_binding, set_size):
    info = {
        "ValueSetSize": set_size
    }
    yield state.add_to_e(e_target_binding.variable.name, "DeterminerSetLimiter", {"Value": info, "Originator": execution_context().current_predication_index()})


@Predication(vocabulary, names=["_together_p"], arguments=[("e",), ("x", PluralType.collective)])
def together_p(state, e_introduced_binding, x_target_binding):
    for _, x_target_value in discrete_variable_set_generator(x_target_binding, VariableValueSetSize.more_than_one):
        yield state.set_x(x_target_binding.variable.name, x_target_value, VariableValueType.set, used_collective=True)


# Needed for "together, which 3 files are 3 mb?"
@Predication(vocabulary, names=["_together_p"])
def together_p_ee(state, e_introduced_binding, e_target_binding):
    yield from together_p_state(state, e_introduced_binding, e_target_binding)


@Predication(vocabulary, names=["_together_p_state"])
def together_p_state(state, e_introduced_binding, e_target_binding):
    yield from default_cardinal_set_limiter_norm(state, e_introduced_binding, e_target_binding, VariableValueSetSize.more_than_one)


# Delete only works on distributive values: i.e. there is no semantic for deleting
# things "together" which would probably imply
@Predication(vocabulary, names=["_delete_v_1", "_erase_v_1"])
def delete_v_1_comm(state, e_introduced_binding, x_actor_binding, x_what_binding):
    # We only know how to delete things from the
    # computer's perspective
    if x_actor_binding.value[0].name == "Computer":
        def criteria(value):
            if len(value) > 1:
                report_error(["cantDeleteSet", x_what_binding.variable.name])

            else:
                # Only allow deleting files and folders
                if isinstance(value[0], (File, Folder)):
                    return True

                else:
                    report_error(["cantDo", "delete", x_what_binding.variable.name])

        for new_state in individual_only_style_predication_1(state, x_what_binding, criteria):
            yield new_state.record_operations([DeleteOperation(new_state.get_binding(x_what_binding.variable.name))])

    else:
        report_error(["dontKnowActor", x_actor_binding.variable.name])


@Predication(vocabulary, names=["pron"])
def pron(state, x_who_binding):
    person = int(state.get_binding("tree").value[0]["Variables"][x_who_binding.variable.name]["PERS"])

    def criteria(value):
        return isinstance(value, Actor) and value.person == person

    yield from combinatorial_style_predication(state, x_who_binding, state.all_individuals(), criteria)
