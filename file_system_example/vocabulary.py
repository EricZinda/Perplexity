from file_system_example.objects import File, Folder, Megabyte, Actor, QuotedText
from file_system_example.state import DeleteOperation, ChangeDirectoryOperation, CopyOperation
# from perplexity.OpenAI import StartOpenAIBooleanRequest, CompleteOpenAIRequest
from perplexity.plurals import GlobalCriteria, VariableCriteria
from perplexity.execution import report_error, execution_context
from perplexity.predications import combinatorial_predication_1, lift_style_predication_2, in_style_predication_2, \
    individual_style_predication_1, discrete_variable_generator
from perplexity.response import RespondOperation
from perplexity.set_utilities import Measurement
from perplexity.sstring import s
from perplexity.system_vocabulary import system_vocabulary, quantifier_raw
from perplexity.tree import used_predicatively, is_this_last_fw_seq, find_predication
from perplexity.utilities import sentence_force
from perplexity.variable_binding import VariableBinding
from perplexity.virtual_arguments import scopal_argument
from perplexity.vocabulary import Predication, EventOption, ValueSize, override_predications


vocabulary = system_vocabulary()
override_predications(vocabulary, "user", ["card__cex__"])

# Constants for creating virtual arguments from scopal arguments
locative_preposition_end_location = {"LocativePreposition": {"Value": {"EndLocation": VariableBinding}}}


def in_scope_initialize(state):
    # Some tests don't use the file system object so everything is in scope
    if not hasattr(state, "user"):
        return None

    current_directory = state.user().current_directory()
    # We are looking at the contained items in the user's current directory
    # which is *not* the object in the binding. So: we need contained_items()
    # to report an error that is not variable related, so we pass it None
    contained_binding = VariableBinding(None, current_directory)
    contained_items = set(current_directory.contained_items(contained_binding.variable))
    return {"ContainedItems": contained_items, "CurrentDirectory": current_directory}


def in_scope(initial_data, state, value):
    # Some tests don't use the file system object so everything is in scope
    if initial_data is None:
        return True

    if value in initial_data["ContainedItems"] or value == initial_data["CurrentDirectory"]:
        return True
    # else:
    #     report_error(["valueIsNotInScope", value])
    #     return False


@Predication(vocabulary, names=["solution_group__in_p_loc"])
def in_p_loc_fail(state_list, has_more, e_introduced_binding_list, x_actor_binding_list, x_location_binding_list):
    test_binding = state_list[0].get_binding("test_solution_group")
    if test_binding.value is not None and test_binding.value[0] == "failAll":
        report_error(["beMoreSpecific"], force=True)
        yield []


@Predication(vocabulary, names=["solution_group__copy_v_1"])
def fail_to_copy(state_list, has_more, e_introduced_binding_list, x_actor_group_variable_values, x_what_group_variable_values):
    test_binding = state_list[0].get_binding("test_solution_group")
    if test_binding.value is not None and test_binding.value[0] == "fakeValues":
        for x_what_binding in x_what_group_variable_values.solution_values:
            x_what_binding_value = x_what_binding.value[0]
            if hasattr(x_what_binding_value, "name") and x_what_binding_value.name == '/documents/file5.txt':
                yield [state_list[0].record_operations([RespondOperation("I cannot copy that")])]


@Predication(vocabulary, names=["solution_group"])
def solution_group(state_list, has_more, variable_constraints):
    test_binding = state_list[0].get_binding("test_solution_group")
    if test_binding.value is not None:
        if test_binding.value[0] == "cannotAnswer":
            yield [state_list[0].record_operations([RespondOperation("I cannot respond to this")])]

        elif test_binding.value[0] == "fakeValues":
            tree = state_list[0].get_binding("tree").value[0]
            sentence_force_type = sentence_force(tree["Variables"])
            if sentence_force_type == "ques":
                # See if this is a "WH" type question
                wh_predication = find_predication(tree["Tree"], "_which_q")
                if wh_predication is None:
                    wh_predication = find_predication(tree["Tree"], "which_q")
                    if wh_predication is None:
                        return

                wh_variable = wh_predication.introduced_variable()
                new_group = []
                index = 0
                for state in state_list:
                    new_group.append(state.set_x(wh_variable, ( "fakefile" + str(index),)))
                    index += 1
                yield new_group
                yield True


def variable_is_megabyte(binding):
    return binding.value is not None and len(binding.value) == 1 and isinstance(binding.value[0], Megabyte)


def value_is_measure(value):
    return value is not None and len(value) == 1 and isinstance(value[0], Measurement)


@Predication(vocabulary, names=["card"])
def card_selector(state, c_count, e_introduced_binding, x_target_binding):
    if variable_is_megabyte(x_target_binding):
        # 10 mb should not generate a set of 10 1mbs
        # special case this.  Turns a megabyte into a *measure* which is a set of megabytes
        yield state.set_x(x_target_binding.variable.name,
                          (Measurement(x_target_binding.value[0], int(c_count)), ),
                          combinatoric=False)
    else:
        if e_introduced_binding.value is not None and "DeterminerDegreeLimiter" in e_introduced_binding.value:
            card_is_exactly = e_introduced_binding.value["DeterminerDegreeLimiter"]["Value"]["Only"]
        else:
            card_is_exactly = False

        yield state.set_variable_data(x_target_binding.variable.name,
                                      determiner=VariableCriteria(execution_context().current_predication(),
                                                                  x_target_binding.variable.name,
                                                                  min_size=int(c_count),
                                                                  max_size=int(c_count),
                                                                  global_criteria=GlobalCriteria.exactly if card_is_exactly else None))



# true for both sets and individuals as long as everything
# in the set is a file
def folder_n_of(state, x_binding, i_binding):
    def bound_variable(value):
        if isinstance(value, Folder):
            return True
        else:
            report_error(["valueIsNotX", value, x_binding.variable.name])
            return False

    def unbound_variable():
        for item in state.all_individuals():
            if isinstance(item, Folder):
                yield item

    yield from combinatorial_predication_1(state, x_binding, bound_variable, unbound_variable)


def file_n_of(state, x_binding, i_binding):
    def bound_variable(value):
        if isinstance(value, File):
            return True
        else:
            report_error(["valueIsNotX", value, x_binding.variable.name])
            return False

    def unbound_variable():
        for item in state.all_individuals():
            if isinstance(item, File):
                yield item

    yield from combinatorial_predication_1(state, x_binding, bound_variable, unbound_variable)


nouns_handled_directly = ["file", "folder", "place"]


def handles_noun(state, noun_lemma):
    return True


@Predication(vocabulary, names=["match_all_n"], matches_lemma_function=handles_noun)
def noun_n_selector_2(noun_type, state, x_binding, i_binding):
    if noun_type == "folder":
        yield from folder_n_of(state, x_binding, i_binding)
    elif noun_type == "file":
        yield from file_n_of(state, x_binding, i_binding)
    else:
        yield from noun_n_2(noun_type, state, x_binding, i_binding)


# Simple example of using match_all that doesn't do anything except
# make sure we don't say "I don't know the word 'book'"
# @Predication(vocabulary, names=["match_all_n"], matches_lemma_function=handles_noun)
def noun_n_2(noun_type, state, x_binding, i_binding):
    if noun_type == "book":
        yield state.set_x(x_binding.variable.name, ("book1",))
    elif noun_type not in nouns_handled_directly:
        yield state.set_x(x_binding.variable.name, (noun_type,))

    if False:
        yield None


@Predication(vocabulary, names=["match_all_n"], matches_lemma_function=handles_noun)
def noun_n_1(noun_type, state, x_binding):
    if x_binding.value is None and noun_type not in nouns_handled_directly:
        yield state.set_x(x_binding.variable.name, (noun_type,))


@Predication(vocabulary, names=["_please_v_1"])
def please_v_1(state, e_binding, i_binding_1, i_binding_2):
    # Just ignore
    yield state


@Predication(vocabulary, names=["_megabyte_n_1"])
def megabyte_n_1(state, x_binding, u_binding):
    def bound_variable(value):
        if isinstance(value, Megabyte):
            return True
        else:
            report_error(["valueIsNotX", value, x_binding.variable.name])
            return False

    def unbound_variable():
        yield Megabyte()

    yield from combinatorial_predication_1(state, x_binding, bound_variable, unbound_variable)


@Predication(vocabulary)
def place_n(state, x_binding):
    def bound_variable(value):
        # Any object is a "place" as long as it can contain things
        if hasattr(value, "contained_items"):
            return True
        else:
            report_error(["valueIsNotX", value, x_binding.variable.name])
            return False

    def unbound_variable():
        for item in state.all_individuals():
            if hasattr(item, "contained_items"):
                yield item

    yield from combinatorial_predication_1(state, x_binding, bound_variable, unbound_variable)


@Predication(vocabulary, names=["_very_x_deg"])
def very_x_deg(state, e_introduced_binding, e_target_binding):
    # First see if we have been "very'd"!
    initial_degree_multiplier = degree_multiplier_from_event(state, e_introduced_binding)

    # We'll interpret "very" as meaning "one order of magnitude larger"
    yield state.add_to_e(e_target_binding.variable.name, "DegreeMultiplier", {"Value": initial_degree_multiplier * 10, "Originator": execution_context().current_predication_index()})


# "large_a" means that each individual thing in a combinatoric argument is large
# BUT: if you ask if large([a, b]) of a set as an index, it will fail
@Predication(vocabulary, names=["_large_a_1"], handles=[("DegreeMultiplier", EventOption.optional)])
def large_a_1(state, e_introduced_binding, x_target_binding):
    # See if any modifiers have changed *how* large we should be
    degree_multiplier = degree_multiplier_from_event(state, e_introduced_binding)

    if used_predicatively(state):
        # "large" is being used "predicatively" as in "the dogs are large". This needs to force
        # the individuals to be separate (i.e. not part of a group)
        def criteria_predicatively(value):
            if hasattr(value, 'size') and value.size > degree_multiplier * 1000000:
                return True

            else:
                report_error(["adjectiveDoesntApply", "large", x_target_binding.variable.name])
                return False

        def unbound_values_predicatively():
            # Find all large things
            for value in state.all_individuals():
                if hasattr(value, 'size') and value.size > degree_multiplier * 1000000:
                    yield value

        yield from individual_style_predication_1(state,
                                                  x_target_binding,
                                                  criteria_predicatively,
                                                  unbound_values_predicatively,
                                                  ["adjectiveDoesntApply", "large", x_target_binding.variable.name])

    else:
        # "large" is being used "attributively" as in "the large dogs are meeting" which doesn't force
        # dogs to be grouped or individual, but *does* require that each, individually, is large
        def bound_variable(value):
            if hasattr(value, 'size') and value.size > degree_multiplier * 1000000:
                return True

            else:
                report_error(["adjectiveDoesntApply", "large", x_target_binding.variable.name])
                return False

        def unbound_variable():
            for item in state.all_individuals():
                if bound_variable(item):
                    yield item

        yield from combinatorial_predication_1(state, x_target_binding, bound_variable, unbound_variable)


# Arbitrarily decide that "small" means a size <= 1,000,000
# Remember that "hasattr()" checks if an object has
# a property
@Predication(vocabulary, names=["_small_a_1"], handles=[("DegreeMultiplier", EventOption.optional)])
def small_a_1(state, e_introduced_binding, x_target_binding):
    # See if any modifiers have changed *how* small we should be
    degree_multiplier = 1 / degree_multiplier_from_event(state, e_introduced_binding)

    if used_predicatively(state):
        # "small" is being used "predicatively" as in "the dogs are small". This needs to force
        # the individuals to be separate (i.e. not part of a group)
        def criteria_predicatively(value):
            if hasattr(value, 'size') and value.size <= degree_multiplier * 1000000:
                return True

            else:
                report_error(["adjectiveDoesntApply", "small", x_target_binding.variable.name])
                return False

        def unbound_values_predicatively():
            # Find all large things
            for value in state.all_individuals():
                if hasattr(value, 'size') and value.size <= degree_multiplier * 1000000:
                    yield value

        yield from individual_style_predication_1(state,
                                                  x_target_binding,
                                                  criteria_predicatively,
                                                  unbound_values_predicatively,
                                                  ["adjectiveDoesntApply", "small", x_target_binding.variable.name])

    else:
        # "small" is being used "attributively" as in "the small dogs are meeting" which doesn't force
        # dogs to be grouped or individual, but *does* require that each, individually, is small
        def bound_variable(value):
            if hasattr(value, 'size') and value.size <= degree_multiplier * 1000000:
                return True

            else:
                report_error(["adjectiveDoesntApply", "small", x_target_binding.variable.name])
                return False

        def unbound_variable():
            for item in state.all_individuals():
                if bound_variable(item):
                    yield item

        yield from combinatorial_predication_1(state, x_target_binding, bound_variable, unbound_variable)


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


@Predication(vocabulary, names=["_in_p_state"])
def in_p_state(state, e_introduced_binding, e_target_binding, x_location_binding):
    preposition_info = {
        "EndLocation": x_location_binding
    }

    yield state.add_to_e(e_target_binding.variable.name, "StativePreposition", {"Value": preposition_info, "Originator": execution_context().current_predication_index()})


def default_locative_preposition_norm(state, e_introduced_binding, x_actor_binding, x_location_binding):
    preposition_info = {
        "LeftSide": x_actor_binding,
        "EndLocation": x_location_binding
    }
    yield state.add_to_e(e_introduced_binding.variable.name, "LocativePreposition", {"Value": preposition_info, "Originator": execution_context().current_predication_index()})


@Predication(vocabulary, names=["_in_p_loc"])
def in_p_loc_norm(state, e_introduced_binding, x_actor_binding, x_location_binding):
    yield from default_locative_preposition_norm(state, e_introduced_binding, x_actor_binding, x_location_binding)


# @Predication(vocabulary, names=["_in_p_loc"])
# def in_p_loc_open_ai(state, e_introduced_binding, x_actor_binding, x_location_binding):
#     if x_actor_binding.value is not None and x_location_binding.value is not None and \
#         len(x_actor_binding.value) == 1 and len(x_location_binding.value) == 1 and \
#             isinstance(x_actor_binding.value[0], str) and isinstance(x_location_binding.value[0], str):
#         request_text = s("{'is':<x_actor_binding.variable.name} {x_actor_binding.variable.name} sometimes in {x_location_binding.variable.name}?", state.get_binding("tree").value[0])
#         print(f"Asking ChatGPT: {request_text}")
#         request_info = StartOpenAIBooleanRequest("test", "in_loc_predication", request_text)
#         result = CompleteOpenAIRequest(request_info, wait=10)
#         if result == "true":
#             yield state
#         elif result is None:
#             report_error(["dontKnowRightNow"])
#         else:
#             report_error(["thingHasNoLocation", x_actor_binding.variable.name, x_location_binding.variable.name])

@Predication(vocabulary, names=["_in_p_loc"])
def in_p_loc(state, e_introduced_binding, x_actor_binding, x_location_binding):
    def item_in_item(item1, item2):
        # x_actor is "in" x_location if x_location contains it
        found_location = False
        if hasattr(item2, "contained_items"):
            for item in item2.contained_items(x_location_binding.variable):
                if item1 == item:
                    found_location = True
                    break

        if not found_location:
            report_error(["thingHasNoLocation", x_actor_binding.variable.name, x_location_binding.variable.name])

        return found_location

    def location_unbound_values(actor_value):
        # This is a "what is actor in?" type query since no location specified (x_location_binding was unbound)
        # Order matters, so all_locations needs to return the best answer first
        found_location = False
        if hasattr(actor_value, "all_locations"):
            for location in actor_value.all_locations(x_actor_binding.variable):
                found_location = True
                yield location
        if not found_location:
            report_error(["thingHasNoLocation", x_actor_binding.variable.name, x_location_binding.variable.name])

    def actor_unbound_values(location_value):
        # This is a "what is in x?" type query since no actor specified (x_actor_binding was unbound)
        # Order matters, so all_locations needs to return the best answer first
        if hasattr(location_value, "contained_items"):
            for actor in location_value.contained_items(x_location_binding.variable):
                yield actor
            report_error(["thingHasNoLocation", x_actor_binding.variable.name, x_location_binding.variable.name])
        else:
            report_error(["thingIsNotContainer", x_location_binding.variable.name])

    for new_state in in_style_predication_2(state, x_actor_binding, x_location_binding, item_in_item, actor_unbound_values, location_unbound_values):
        yield new_state


@Predication(vocabulary, names=["loc_nonsp"])
def loc_nonsp(state, e_introduced_binding, x_actor_binding, x_location_binding):
    # Don't use this version if we are dealing with a size
    if x_location_binding.value is not None and value_is_measure(x_location_binding.value):
        return

    def item_at_item(item1, item2):
        if hasattr(item1, "all_locations"):
            # Asking if a location of item1 is at item2
            for location in item1.all_locations(x_actor_binding.variable):
                if location == item2:
                    return True

        report_error(["thingHasNoLocation", x_actor_binding.variable.name, x_location_binding.variable.name])
        return False

    def location_unbound_values(actor_value):
        # This is a "where is actor?" type query since no location specified (x_location_binding was unbound)
        # Order matters, so all_locations needs to return the best answer first
        if hasattr(actor_value, "all_locations"):
            for location in actor_value.all_locations(x_actor_binding.variable):
                yield location

        report_error(["thingHasNoLocation", x_actor_binding.variable.name, x_location_binding.variable.name])

    def actor_unbound_values(location_value):
        # This is a "what is at x?" type query since no actor specified (x_actor_binding was unbound)
        # Order matters, so all_locations needs to return the best answer first
        if hasattr(location_value, "contained_items"):
            for actor in location_value.contained_items(x_location_binding.variable):
                yield actor

        report_error(["thingIsNotContainer", x_location_binding.variable.name])

    for new_state in in_style_predication_2(state, x_actor_binding, x_location_binding, item_at_item, actor_unbound_values, location_unbound_values):
        yield new_state


# handles size only
# loc_nonsp will add up the size of files if a collective set of actors comes in, so declare that as handling them differently
# we treat megabytes as a group, all added up, which is different than separately (a megabyte as a time) so ditto
@Predication(vocabulary, names=["loc_nonsp"], arguments=[("e",), ("x", ValueSize.all), ("x", ValueSize.all)], handles=[("DeterminerSetLimiter", EventOption.optional)])
def loc_nonsp_size(state, e_introduced_binding, x_actor_binding, x_size_binding):
    if x_size_binding.value is None:
        return

    def both_bound_criteria(actor_set, size_set):
        if value_is_measure(size_set):
            if x_size_binding.variable.combinatoric:
                # we only deal with x megabytes as a set because dist(10 mb) is 1 mb and nobody means 10 individual megabyte when they say "2 files are 10mb"
                report_error(["formNotUnderstood", "missing", "collective"])
                return False

            # Try to add up all combinations of x_actor_binding
            # to total size_set[0]
            total = 0
            for actor in actor_set:
                if not hasattr(actor, "size_measurement"):
                    report_error(["xIsNotY", x_actor_binding.variable.name, x_size_binding.variable.name])
                    return False
                else:
                    total += actor.size_measurement().count

            if size_set[0].count == total:
                return True

            else:
                report_error(["xIsNotY", x_actor_binding.variable.name, x_size_binding.variable.name])
                return False

        else:
            return False

    def actor_unbound_criteria(size_set):
        if False:
            yield None
        assert False

    def size_unbound_criteria(actor_set):
        if False:
            yield None
        assert False

    # If a cardinal limiter like "together" is acting on this verb, it is unclear
    # if it is for x_actor or x_size, so we have to try both
    if e_introduced_binding.value is not None and "DeterminerSetLimiter" in e_introduced_binding.value:
        set_size = e_introduced_binding.value["DeterminerSetLimiter"]["Value"]["ValueSetSize"]
        yield from lift_style_predication_2(state, x_actor_binding, x_size_binding, both_bound_criteria, None, None, None, set_size, ValueSize.all)
        yield from lift_style_predication_2(state, x_actor_binding, x_size_binding, both_bound_criteria, None, None, None, ValueSize.all, set_size)

    else:
        yield from lift_style_predication_2(state, x_actor_binding, x_size_binding, both_bound_criteria, None, None, None, ValueSize.all, ValueSize.all)


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


# together_p(e,x) forces x to have values > 1 item
# So it needs to declare that its x variable will have sets of > 1 variable
# Otherwise, it won't get passed sets > 1 if its variables are bound
@Predication(vocabulary, names=["_together_p"], arguments=[("e",), ("x", ValueSize.more_than_one)])
def together_p(state, e_introduced_binding, x_target_binding):
    for x_target_value in discrete_variable_generator(x_target_binding.value, x_target_binding.variable.combinatoric, ValueSize.more_than_one):
        yield state.set_x(x_target_binding.variable.name, x_target_value, False)


# Needed for "together, which 3 files are 3 mb?"
@Predication(vocabulary, names=["_together_p"])
def together_p_ee(state, e_introduced_binding, e_target_binding):
    yield from together_p_state(state, e_introduced_binding, e_target_binding)


@Predication(vocabulary, names=["_together_p_state"])
def together_p_state(state, e_introduced_binding, e_target_binding):
    yield from default_cardinal_set_limiter_norm(state, e_introduced_binding, e_target_binding, ValueSize.more_than_one)


# Delete only works on individual values: i.e. there is no semantic for deleting
# things "together" which would probably imply a transaction or something
@Predication(vocabulary, names=["_delete_v_1", "_erase_v_1"])
def delete_v_1_comm(state, e_introduced_binding, x_actor_binding, x_what_binding):
    # We only know how to delete things from the
    # computer's perspective
    if x_actor_binding.value[0].name == "Computer":
        def criteria(value):
            # Only allow deleting files and folders that exist
            if isinstance(value, (File, Folder)) and value.exists():
                return True

            else:
                report_error(["cantDo", "delete", x_what_binding.variable.name])

        def unbound_what():
            report_error(["cantDo", "delete", x_what_binding.variable.name])

        for new_state in individual_style_predication_1(state,
                                                        x_what_binding,
                                                        criteria,
                                                        unbound_what,
                                                        ["cantDeleteSet", x_what_binding.variable.name]):
            yield new_state.apply_operations([DeleteOperation(new_state.get_binding(x_what_binding.variable.name))])

    else:
        report_error(["dontKnowActor", x_actor_binding.variable.name])


@Predication(vocabulary, names=["_go_v_1"], handles=[("DirectionalPreposition", EventOption.required)])
def go_v_1_comm(state, e_introduced_binding, x_actor_binding):
    if x_actor_binding.value is None or len(x_actor_binding.value) > 1 or x_actor_binding.value[0].name != "Computer":
        report_error(["dontKnowActor", x_actor_binding.variable.name])
        return

    x_location_binding = e_introduced_binding.value["DirectionalPreposition"]["Value"]["EndLocation"]

    def bound_location(location_item):
        # Only allow moving to folders
        if isinstance(location_item, Folder):
            return True

        else:
            if hasattr(x_location_binding.value, "exists") and location_item.exists():
                report_error(["cantDo", "change directory to", x_location_binding.variable.name])

            else:
                report_error(["notFound", x_location_binding.variable.name])

    def unbound_location(location_item):
        # Location is unbound, ask them to be more specific
        report_error(["beMoreSpecific"])

    # go_v_1 effectively has two arguments since it has x_actor by default and requires x_location from a preposition
    for new_state in individual_style_predication_1(state,
                                                    x_location_binding,
                                                    bound_location,
                                                    unbound_location,
                                                    ["cantDo", "go", x_location_binding.variable.name]):
        target_location_binding = new_state.get_binding(x_location_binding.variable.name)
        yield new_state.apply_operations([ChangeDirectoryOperation(target_location_binding),
                                          RespondOperation(f"You are now in {target_location_binding.value[0]}")])


@Predication(vocabulary, names=["_to_p_dir"])
def to_p_dir(state, e_introduced, e_target_binding, x_location_binding):
    preposition_info = {
        "EndLocation": x_location_binding
    }

    yield state.add_to_e(e_target_binding.variable.name, "DirectionalPreposition", {"Value": preposition_info, "Originator": execution_context().current_predication_index()})


# "copy" where the user did not say where to copy to, assume current directory
@Predication(vocabulary, names=["_copy_v_1"])
def copy_v_1_comm(state, e_introduced_binding, x_actor_binding, x_what_binding):
    def both_bound_function(actor_item, location_item):
        if actor_item.name == "Computer":
            # Only allow copying files and folders
            if isinstance(x_what_binding.value[0], (File, Folder)) and x_what_binding.value[0].exists():
                return True

            else:
                report_error(["cantDo", "copy", x_what_binding.variable.name])

        else:
            report_error(["dontKnowActor", x_actor_binding.variable.name])

    def binding1_unbound_predication_function(location_item):
        # Actor is unbound, unclear when this would happen but report an error
        report_error(["dontKnowActor", x_actor_binding.variable.name])

    def binding2_unbound_predication_function(actor_item):
        # Location is unbound, ask them to be more specific
        report_error(["beMoreSpecific"])

    for new_state in in_style_predication_2(state, x_actor_binding, x_what_binding,
                                            both_bound_function, binding1_unbound_predication_function, binding2_unbound_predication_function):
        yield new_state.apply_operations([CopyOperation(None, new_state.get_binding(x_what_binding.variable.name), None)])


# "copy" where the user specifies where to copy "from". Assume "to" is current directory since it isn't specified
# This is really only different from the locative "_in_p_loc(e15,x8,x16), _copy_v_1(e2,x3,x8)" version if:
# a) The from directory doesn't exist
# b) The thing to copy has a relative path because our "current directory" for the file will be different
@Predication(vocabulary, names=["_copy_v_1"], handles=[("StativePreposition", EventOption.required)])
def copy_v_1_stative_comm(state, e_introduced_binding, x_actor_binding, x_what_binding):
    # TODO: Handle set based from locations
    x_copy_from_location_binding = e_introduced_binding.value["StativePreposition"]["Value"]["EndLocation"]
    if len(x_copy_from_location_binding.value) != 1:
        return

    if not isinstance(x_copy_from_location_binding.value[0], Folder):
        report_error(["cantDo", "copy from", x_what_binding.variable.name])
        return

    def both_bound_function(actor_item, location_item):
        if actor_item.name == "Computer":
            # We only know how to copy something "from" a folder
            if isinstance(x_what_binding.value[0], (File, Folder)) and x_what_binding.value[0].exists():
                return True

            else:
                report_error(["cantDo", "copy", x_what_binding.variable.name])

        else:
            report_error(["dontKnowActor", x_actor_binding.variable.name])

    def binding1_unbound_predication_function(location_item):
        # Actor is unbound, unclear when this would happen but report an error
        report_error(["dontKnowActor", x_actor_binding.variable.name])

    def binding2_unbound_predication_function(actor_item):
        # Location is unbound, ask them to be more specific
        report_error(["beMoreSpecific"])

    for new_state in in_style_predication_2(state, x_actor_binding, x_what_binding,
                                            both_bound_function, binding1_unbound_predication_function, binding2_unbound_predication_function):
        yield new_state.apply_operations([CopyOperation(x_copy_from_location_binding, new_state.get_binding(x_what_binding.variable.name), None)])


@Predication(vocabulary, names=["_copy_v_1"], virtual_args=[(scopal_argument(scopal_index=3, event_for_arg_index=2, event_value_pattern=locative_preposition_end_location), EventOption.required)])
def copy_v_1_locative_comm(state, e_introduced_binding, x_actor_binding, x_what_binding, h_where, where_binding_generator):
    # TODO: Handle set based from locations
    where_binding_list = list(where_binding_generator)
    if len(where_binding_list) != 1:
        return

    if not isinstance(where_binding_list[0].value[0], Folder) or not where_binding_list[0].value[0].exists():
        report_error(["cantDo", "copy to", x_what_binding.variable.name])
        return

    def both_bound_function(actor_item, what_item):
        if actor_item.name == "Computer":
            # We only know how to copy a file or folder
            if isinstance(what_item, (File, Folder)) and what_item.exists():
                return True

            else:
                report_error(["cantDo", "copy", x_what_binding.variable.name])

        else:
            report_error(["dontKnowActor", x_actor_binding.variable.name])

    def binding1_unbound_predication_function(location_item):
        # Actor is unbound, unclear when this would happen but report an error
        report_error(["dontKnowActor", x_actor_binding.variable.name])

    def binding2_unbound_predication_function(actor_item):
        # Location is unbound, ask them to be more specific
        report_error(["beMoreSpecific"])

    for new_state in in_style_predication_2(state, x_actor_binding, x_what_binding,
                                            both_bound_function, binding1_unbound_predication_function,
                                            binding2_unbound_predication_function):
        yield new_state.apply_operations([CopyOperation(None, new_state.get_binding(x_what_binding.variable.name), where_binding_list[0])])


@Predication(vocabulary, names=["pron"])
def pron(state, x_who_binding):
    person = int(state.get_binding("tree").value[0]["Variables"][x_who_binding.variable.name]["PERS"])

    def bound_variable(value):
        return isinstance(value, Actor) and value.person == person

    def unbound_variable():
        for item in state.all_individuals():
            if bound_variable(item):
                yield item

    yield from combinatorial_predication_1(state, x_who_binding, bound_variable, unbound_variable)


# c_raw_text_value will always be set to a raw string
@Predication(vocabulary)
def quoted(state, c_raw_text_value, i_text_binding):
    def bound_value(value):
        if isinstance(value, QuotedText) and value.name == c_raw_text_value:
            return True

        else:
            report_error(["xIsNotYValue", i_text_binding, c_raw_text_value])
            return False

    def unbound_values():
        yield QuotedText(c_raw_text_value)

    yield from individual_style_predication_1(state,
                                              i_text_binding,
                                              bound_value,
                                              unbound_values,
                                              ["unexpected"])


# Yield all the solutions for fw_seq where value is bound
# and x_phrase_binding may or may not be
def yield_from_fw_seq(state, x_phrase_binding, non_set_value):
    if x_phrase_binding.value is None:
        # x is not bound
        if is_this_last_fw_seq(state) and hasattr(non_set_value, "all_interpretations"):
            # Records that predication index X is a disjunction
            execution_context().set_disjunction()

            # Get all the interpretations of the quoted text
            # and bind them iteratively
            # Since these are *alternative* interpretations, they need to be in different lineages
            # just like if there were separate predication implementations yielding them
            interpretation_id = 0
            for interpretation in non_set_value.all_interpretations(state):
                interpretation_id += 1
                tree_lineage_binding = state.get_binding("tree_lineage")
                tree_lineage = "" if tree_lineage_binding.value is None else tree_lineage_binding.value[0]
                yield state.set_x(x_phrase_binding.variable.name, (interpretation, ), False).set_x("tree_lineage", (f"{tree_lineage}.{interpretation_id}",))

        else:
            yield state.set_x(x_phrase_binding.variable.name, (non_set_value,), False)

    else:
        # x is bound, compare it to value
        if hasattr(non_set_value, "all_interpretations"):
            # Get all the interpretations of the object
            # and check them iteratively
            for interpretation in non_set_value.all_interpretations(state):
                if interpretation == x_phrase_binding.value:
                    yield state

        else:
            if non_set_value == x_phrase_binding.value:
                yield state


@Predication(vocabulary, names=["fw_seq"])
def fw_seq1(state, x_phrase_binding, i_part_binding):
    if i_part_binding.value is None:
        # This should never happen since it basically means
        # "return all possible strings"
        assert x_phrase_binding.value is not None
        yield state.set_x(i_part_binding.variable.name, (x_phrase_binding.value, ), False)

    else:
        yield from yield_from_fw_seq(state, x_phrase_binding, i_part_binding.value[0])


@Predication(vocabulary, names=["fw_seq"])
def fw_seq2(state, x_phrase_binding, i_part1_binding, i_part2_binding):
    # Only succeed if part1 and part2 are bound and are QuotedText instances to avoid
    # having to split x into pieces somehow
    if i_part1_binding.value is not None and i_part2_binding.value is not None and \
        len(i_part1_binding.value) == 1 and len(i_part2_binding.value) == 1 and \
            isinstance(i_part1_binding.value[0], QuotedText) and isinstance(i_part2_binding.value[0], QuotedText):
        combined_value = QuotedText(" ".join([i_part1_binding.value[0].name, i_part2_binding.value[0].name]))
        yield from yield_from_fw_seq(state, x_phrase_binding, combined_value)


@Predication(vocabulary, names=["fw_seq"])
def fw_seq3(state, x_phrase_binding, x_part1_binding, i_part2_binding):
    # Only succeed if part1 and part2 are set and are QuotedText instances to avoid
    # having to split x into pieces somehow
    if x_part1_binding.value is not None and i_part2_binding.value is not None and \
        len(x_part1_binding.value) == 1 and len(i_part2_binding.value) == 1 and \
            isinstance(x_part1_binding.value[0], QuotedText) and isinstance(i_part2_binding.value[0], QuotedText):
        combined_value = QuotedText(" ".join([x_part1_binding.value[0].name, i_part2_binding.value[0].name]))
        yield from yield_from_fw_seq(state, x_phrase_binding, combined_value)

