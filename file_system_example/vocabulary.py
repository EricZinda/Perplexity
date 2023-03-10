import copy
import enum
import itertools
import logging
from file_system_example.objects import File, Folder, Actor, Container, QuotedText, Megabyte
from file_system_example.state import DeleteOperation, ChangeDirectoryOperation, CopyOperation
from perplexity.cardinals import split_cardinal_rstr, cardinal_group_outgoing_solutions, \
    cardinal_variable_set_incoming_next_this_cardinal_group, yield_all_cardinal_group_solutions, \
    unique_solution_if_index, Measurement
from perplexity.utilities import at_least_one_generator, is_plural
from perplexity.variable_binding import VariableBinding
from perplexity.execution import call, report_error, execution_context, call_with_group, group_context, \
    create_solution_id, create_variable_set_cache, VariableSetRestart
from perplexity.tree import TreePredication, is_this_last_fw_seq, find_predications_using_variable_ARG1, \
    predication_from_index, find_predication_from_introduced
from perplexity.virtual_arguments import scopal_argument
from perplexity.vocabulary import Vocabulary, Predication, EventOption, DeclareArg, CollectiveBehavior, \
    PredicationProperty

vocabulary = Vocabulary()

# Constants for creating virtual arguments from scopal arguments
locative_preposition_end_location = {"LocativePreposition": {"Value": {"EndLocation": VariableBinding}}}


@Predication(vocabulary, names=["_go_v_1"], handles=[("DirectionalPreposition", EventOption.required)])
def go_v_1_comm(state, e_introduced_binding, x_actor_binding):
    x_location_binding = e_introduced_binding.value["DirectionalPreposition"]["Value"]["EndLocation"]

    # Only allow moving to folders
    if isinstance(x_location_binding.value, Folder):
        yield state.apply_operations([ChangeDirectoryOperation(x_location_binding)])

    else:
        if hasattr(x_location_binding.value, "exists") and x_location_binding.value.exists():
            report_error(["cantDo", "change directory to", x_location_binding.variable.name])

        else:
            report_error(["notFound", x_location_binding.variable.name])


@Predication(vocabulary, names=["_to_p_dir"])
def to_p_dir(state, e_introduced, e_target_binding, x_location_binding):
    preposition_info = {
        "EndLocation": x_location_binding
    }

    yield state.add_to_e(e_target_binding.variable.name, "DirectionalPreposition", {"Value": preposition_info, "Originator": execution_context().current_predication_index()})


@Predication(vocabulary, names=["_delete_v_1", "_erase_v_1"])
def delete_v_1_comm(state, e_introduced_binding, x_actor_binding, x_what_binding):
    # We only know how to delete things from the
    # computer's perspective
    if x_actor_binding.value.name == "Computer":
        # Only allow deleting files and folders
        if isinstance(x_what_binding.value, (File, Folder)):
            yield state.apply_operations([DeleteOperation(x_what_binding)])

        else:
            report_error(["cantDo", "delete", x_what_binding.variable.name])

    else:
        report_error(["dontKnowActor", x_actor_binding.variable.name])


# "copy" where the user did not say where to copy to, assume current directory
@Predication(vocabulary, names=["_copy_v_1"])
def copy_v_1_comm(state, e_introduced_binding, x_actor_binding, x_what_binding):
    # We only know how to copy things from the
    # computer's perspective
    if x_actor_binding.value.name == "Computer":
        # Only allow copying files and folders
        if isinstance(x_what_binding.value, (File, Folder)):
            yield state.apply_operations([CopyOperation(None, x_what_binding, None)])

        else:
            report_error(["cantDo", "copy", x_what_binding.variable.name])

    else:
        report_error(["dontKnowActor", x_actor_binding.variable.name])


# "copy" where the user specifies where to copy "from". Assume "to" is current directory since it isn't specified
# This is really only different from the locative "_in_p_loc(e15,x8,x16), _copy_v_1(e2,x3,x8)" version if:
# a) The from directory doesn't exist
# b) The thing to copy has a relative path because our "current directory" for the file will be different
@Predication(vocabulary, names=["_copy_v_1"], handles=[("StativePreposition", EventOption.required)])
def stative_copy_v_1_comm(state, e_introduced_binding, x_actor_binding, x_what_binding):
    if "EndLocation" not in e_introduced_binding.value["StativePreposition"]["Value"]:
        report_error(["formNotUnderstood", "missing", "stative preposition end value"])

    x_copy_from_location_binding = e_introduced_binding.value["StativePreposition"]["Value"]["EndLocation"]

    # We only know how to copy things from the
    # computer's perspective
    if x_actor_binding.value.name == "Computer":
        # We only know how to copy something "from" a folder
        if isinstance(x_copy_from_location_binding.value, Folder):
            # Only allow copying files and folders
            if isinstance(x_what_binding.value, (File, Folder)):
                yield state.apply_operations([CopyOperation(x_copy_from_location_binding, x_what_binding, None)])

            else:
                report_error(["cantDo", "copy", x_what_binding.variable.name])

        else:
            report_error(["cantDo", "copy from", x_what_binding.variable.name])

    else:
        report_error(["dontKnowActor", x_actor_binding.variable.name])


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


# See if the value in binding is "in scope"
def in_scope(state, binding):
    # In scope if binding.value is the folder the user is in
    user = state.user()
    if user.current_directory() == binding.value:
        return True

    # In scope if binding.value is a file in the directory the user is in
    # We are looking at the contained items in the user's current directory
    # which is *not* the object in the binding. So: we need contained_items()
    # to report an error that is not variable related, so we pass it None
    contained_binding = VariableBinding(None, user.current_directory())
    for file in user.current_directory().contained_items(contained_binding):
        if file == binding.value:
            return True


@Predication(vocabulary, names=["_this_q_dem", "_this_q_dem_cardinal"])
def this_q_dem(state, x_variable_binding, h_rstr, h_body):
    # Run the RSTR which should fill in the variable with an item
    rstr_single_solution = None
    for solution in call(state, h_rstr):
        x_variable_binding = solution.get_binding(x_variable_binding.variable.name)
        if in_scope(solution, x_variable_binding):
            if rstr_single_solution is None:
                rstr_single_solution = solution

            else:
                # Make sure there is only one since "this" shouldn't be ambiguous
                report_error(["moreThanOneInScope", ["AtPredication", h_body, x_variable_binding.variable.name]], force=True)
                return

    if rstr_single_solution is not None:
        # Now see if that solution works in the BODY
        body_found = False
        for body_solution in call(rstr_single_solution, h_body):
            yield body_solution

    else:
        # Ignore whatever error the RSTR produced, this is a better one
        # Report the variable's English representation as it would be in the BODY
        report_error(["doesntExist", ["AtPredication", h_body, x_variable_binding.variable.name]], force=True)


@Predication(vocabulary, names=["_a_q", "_a_q_cardinal"])
def a_q(state, x_variable_binding, h_rstr, h_body):
    # Run the RSTR which should fill in the variable with an item
    rstr_found = False
    for solution in call(state, h_rstr):
        rstr_found = True

        # Now see if that solution works in the BODY
        body_found = False
        for body_solution in call(solution, h_body):
            yield body_solution
            body_found = True

        if body_found:
            # If it works, stop looking. This one is the single arbitrary item we are looking for
            break

    if not rstr_found:
        # Ignore whatever error the RSTR produced, this is a better one
        # Report the variable's English representation as it would be in the BODY
        report_error(["doesntExist", ["AtPredication", h_body, x_variable_binding.variable.name]], force=True)


@Predication(vocabulary, names=["pron"])
def pron(state, x_who_binding):
    if x_who_binding.value is None:
        iterator = state.all_individuals()

    else:
        iterator = [x_who_binding.value]

    person = int(state.get_binding("tree").value["Variables"][x_who_binding.variable.name]["PERS"])
    for value in iterator:
        if isinstance(value, Actor) and value.person == person:
            yield state.set_x(x_who_binding.variable.name, value)
            break

        else:
            report_error(["dontKnowPronoun", x_who_binding.variable.name])


@Predication(vocabulary, names=["_megabyte_n_1"], properties={"Measurement": True})
def megabyte_n_1(state, x_binding, u_binding):
    if x_binding.value is None:
        yield state.set_x(x_binding.variable.name, Megabyte())

    else:
        if x_binding.value == Megabyte():
            yield state

        else:
            report_error(["xIsNotY", x_binding.value, "megabyte"])


@Predication(vocabulary)
def card(state, c_count, e_introduced_binding, x_target_binding):
    assert False


# rewrite: default_q(x, [cardinal(x, ...), other()], body)
# to: cardinal(x, [other()], default_q(x, thing(x), body)
# to: cardinal(..., default_q(x, base_rstr, body)
@Predication(vocabulary, names=["card_with_scope"])
def cardinal_variable_set_incoming(state, c_count, e_introduced_binding, x_target_binding, h_rstr, h_body):
    c_count_value = int(c_count)
    this_predicate_index = execution_context().current_predication_index()
    parent_variable_set_cache = group_context()

    new_parent_variable_set = this_predicate_index not in parent_variable_set_cache["ChildCardinals"]
    parent_variable_set_next_solution = "NextSolution" in parent_variable_set_cache and parent_variable_set_cache["NextSolution"] is True
    if new_parent_variable_set or parent_variable_set_next_solution:
        yield from cardinal_variable_set_incoming_next_this_cardinal_group(this_predicate_index, state, h_body,
                                                                           new_parent_variable_set, parent_variable_set_next_solution, parent_variable_set_cache,
                                                                           x_target_binding.variable.name, h_rstr, c_count_value)

    else:
        # Continue going through the parent_variable_set: this is the next item in the set
        # We need to use the same this_cardinal_group that we used for the other elements of the set
        # and try it on this_cardinal_group
        if "CurrentCardinalGroup" not in parent_variable_set_cache["ChildCardinals"][this_predicate_index]:
            # This means that we ran out of this cardinal groups, but something between the previous cardinal
            # group and this one is trying alternatives.  They should just all fail
            return

        this_cardinal_group = parent_variable_set_cache["ChildCardinals"][this_predicate_index]["CurrentCardinalGroup"]
        cardinal_logger.debug(f'Pred:{this_predicate_index}, CrdGrpID:{this_cardinal_group.cardinal_group_id} -> cached Cardinal Group -> {this_cardinal_group.cardinal_group_items}')

        cardinal_group_solutions = cardinal_group_outgoing_solutions(this_predicate_index, state, x_target_binding.variable.name, h_body, this_cardinal_group)
        if len(cardinal_group_solutions) == 0:
            # This cardinal group didn't work. Because we've already worked through at least one item in the
            # parent_variable_set, we can't just immediately try another this_cardinal_group
            # Instead, ask the parent to variable_set_restart so it will start from the beginning of its variable_set
            # and we can find a new this_cardinal_group but where we left off in the generator
            cardinal_logger.debug(f'Pred:{this_predicate_index}, CrdGrpID:{this_cardinal_group.cardinal_group_id} -> VariableSetRestart: FAIL Cardinal Group -> {this_cardinal_group.cardinal_group_items}')
            parent_variable_set_cache["NextSolution"] = True
            raise VariableSetRestart

        else:
            yield from yield_all_cardinal_group_solutions(this_predicate_index, this_cardinal_group.cardinal_group_id, cardinal_group_solutions)


# Many quantifiers are simply markers and should use this as
# the default behavior
@Predication(vocabulary, names=["pronoun_q_cardinal", "proper_q_cardinal", "udef_q_cardinal", "pronoun_q", "proper_q", "udef_q"])
def default_quantifier(state, x_variable_binding, h_rstr_orig, h_body_orig, reverse=False):
    h_rstr = h_body_orig if reverse else h_rstr_orig
    h_body = h_rstr_orig if reverse else h_body_orig

    # Find every solution to RSTR
    rstr_found = False
    for solution in call(state, h_rstr):
        rstr_found = True

        # And return it if it is true in the BODY
        for body_solution in call(solution, h_body):
            yield body_solution

    if not rstr_found:
        # Ignore whatever error the RSTR produced, this is a better one
        if not reverse:
            report_error(["doesntExist", ["AtPredication", h_body, x_variable_binding.variable.name]], force=True)


def rstr_reorderable(rstr):
    return isinstance(rstr, TreePredication) and rstr.name in ["place_n", "thing"]


@Predication(vocabulary, names=["which_q", "which_q_cardinal", "_which_q", "_which_q_cardinal"])
def which_q(state, x_variable_binding, h_rstr, h_body):
    yield from default_quantifier(state, x_variable_binding, h_rstr, h_body, reverse=rstr_reorderable(h_rstr))


@Predication(vocabulary, names=["_very_x_deg"])
def very_x_deg(state, e_introduced_binding, e_target_binding):
    # First see if we have been "very'd"!
    initial_degree_multiplier = degree_multiplier_from_event(state, e_introduced_binding)

    # We'll interpret "very" as meaning "one order of magnitude larger"
    yield state.add_to_e(e_target_binding.variable.name, "DegreeMultiplier", {"Value": initial_degree_multiplier * 10, "Originator": execution_context().current_predication_index()})


@Predication(vocabulary, names=["_large_a_1"], handles=[("DegreeMultiplier", EventOption.optional)])
def large_a_1(state, e_introduced_binding, x_target_binding):
    if x_target_binding.value is None:
        iterator = state.all_individuals()
    else:
        iterator = [x_target_binding.value]

    # See if any modifiers have changed *how* large
    # we should be
    degree_multiplier = degree_multiplier_from_event(state, e_introduced_binding)

    for value in iterator:
        # Arbitrarily decide that "large" means a size greater
        # than 1,000,000 and apply any multipliers that other
        # predications set in the introduced event
        # Remember that "hasattr()" checks if an object has
        # a property
        if hasattr(value, 'size') and value.size > degree_multiplier * 1000000:
            yield state.set_x(x_target_binding.variable.name, value)

        else:
            report_error(["adjectiveDoesntApply", "large", x_target_binding.variable.name])


@Predication(vocabulary, names=["_small_a_1"])
def small_a_1(state, e_introduced_binding, x_target_binding):
    if x_target_binding.value is None:
        iterator = state.all_individuals()

    else:
        iterator = [x_target_binding.value]

    for value in iterator:
        # Arbitrarily decide that "small" means a size <= 1,000,000
        # Remember that "hasattr()" checks if an object has
        # a property
        if hasattr(value, 'size') and value.size <= 1000000:
            new_state = state.set_x(x_target_binding.variable.name, value)
            yield new_state

        else:
            report_error(["adjectiveDoesntApply", "small", x_target_binding.variable.name])


@Predication(vocabulary)
def thing(state, x_binding):
    if x_binding.value is None:
        iterator = state.all_individuals()
    else:
        iterator = [x_binding.value]

    for value in iterator:
        yield state.set_x(x_binding.variable.name, value)


@Predication(vocabulary)
def place_n(state, x_binding):
    if x_binding.value is None:
        iterator = state.all_individuals()

    else:
        iterator = [x_binding.value]

    for value in iterator:
        # Any object is a "place" as long as it can
        # contain things
        if isinstance(value, Container):
            yield state.set_x(x_binding.variable.name, value)


@Predication(vocabulary, names=["_together_p"])
def together_p(state, e_introduced_binding, x_target_binding):
    yield from force_bindings_to_collective(state, [x_target_binding])



# This version doesn't add information to the target event, it just affects cardinal groupings
# together_p_state just acts like a restriction on all x args on its target predication
# it ensures that at least one of them is collective
#
# Two children ate two pizzas together could mean:
# 1. each child ate two pizzas at the same time
# 2. two children together ate two pizzas
# or both
# So, "together_p_state" needs to force the x variables in its target to have all combinations
# of coll/dist settings where there is at least one coll
# HOWEVER, it should only do this for variables that are "cardinal-bearing", meaning: those that are plurals
# otherwise, it will force things like "you" to be plural when the speaker didn't say it
@Predication(vocabulary, names=["_together_p_state"])
def together_p_state(state, e_introduced_binding, e_target_binding):
    # Figure out which x variables are on e_target_binding
    target_predication = find_predication_from_introduced(state.get_binding("tree").value["Tree"], e_target_binding.variable.name)
    target_x_args = target_predication.x_args()
    target_x_bindings = [state.get_binding(x_arg) for x_arg in target_x_args]
    yield from force_bindings_to_collective(state, target_x_bindings)


def force_bindings_to_collective(state, target_x_bindings):
    # First see if any of the variables are already collective and just force them to be used
    # in the answer by setting used_collective=True
    found_collective = False
    for binding in target_x_bindings:
        if binding.variable.is_collective:
            found_collective = True
            break

    if found_collective:
        for collective_binding in target_x_bindings:
            if collective_binding.variable.is_collective:
                # if it forces coll, it should mark them as processed (or they won't get selected as a unique answer since dist is the default)
                state = state.set_x(collective_binding.variable.name, collective_binding.value,
                                    used_collective=True)

        yield state

    else:
        # None of the target variables are collective, but one of them might not have bee
        # set to coll/dist yet, and together() is here to set that value to collective.
        # Here's why it will only be one:
        # IF the predication it targets has N variables, then it *must* be the case that
        #   the target predication is in the tree under the quantifiers that declare those variables.
        #   This means that at most one of the ones that are plural should be left "uncardinalized"
        #   because it is either in the rstr or body of all the cardinals and those have set that value
        #   (BUT this requires that cardinalization is set *before* the rstr is run).
        #   Furthermore, this one variable would be the one that is quantified by the quantifier that
        #   the target predication is in the rstr of (if it is in the body it will be set and not uncardinalized)
        #   In the rstr, when we are looking for a value, we only set variable_binding.is_collective
        #   and leave the others unset to indicate this is what mode that variable is in.
        uncardinalized_binding = None
        for target_x_binding in target_x_bindings:
            if is_plural(state, target_x_binding.variable.name) and target_x_binding.variable.is_collective is None:
                assert uncardinalized_binding is None
                uncardinalized_binding = target_x_binding

        if uncardinalized_binding is not None:
            state = state.set_x(uncardinalized_binding.variable.name, uncardinalized_binding.value,
                                is_collective=True,
                                used_collective=True)
            yield state

        else:
            # If it id not find an existing collective binding and there isn't one to
            # set then "together" cant be run
            report_error(["formNotUnderstood", "missing", "collective"])
            return


# @Predication(vocabulary, names=["_together_p_state"])
# def together_p_state(state, e_introduced_binding, e_target_binding):
#     # There is no value for this stative preposition since there is not an end location
#     yield state.add_to_e(e_target_binding.variable.name, "StativePreposition", {"Value": None, "Preposition": "together", "Originator": execution_context().current_predication_index()})


@Predication(vocabulary, names=["_in_p_state"])
def in_p_state(state, e_introduced_binding, e_target_binding, x_location_binding):
    yield from default_p_state("in", state, e_introduced_binding, e_target_binding, x_location_binding)


def default_p_state(preposition, state, e_introduced_binding, e_target_binding, x_location_binding):
    preposition_info = {
        "EndLocation": x_location_binding
    }

    yield state.add_to_e(e_target_binding.variable.name, "StativePreposition", {"Value": preposition_info, "Preposition": preposition, "Originator": execution_context().current_predication_index()})


def default_locative_preposition_norm(state, e_introduced_binding, x_actor_binding, x_location_binding):
    preposition_info = {
        "LeftSide": x_actor_binding,
        "EndLocation": x_location_binding
    }
    yield state.add_to_e(e_introduced_binding.variable.name, "LocativePreposition", {"Value": preposition_info, "Originator": execution_context().current_predication_index()})


@Predication(vocabulary, names=["_in_p_loc"])
def in_p_loc_norm(state, e_introduced_binding, x_actor_binding, x_location_binding):
    yield from default_locative_preposition_norm(state, e_introduced_binding, x_actor_binding, x_location_binding)


@Predication(vocabulary, names=["_copy_v_1"], virtual_args=[(scopal_argument(scopal_index=3, event_for_arg_index=2, event_value_pattern=locative_preposition_end_location), EventOption.required)])
def locative_copy_v_1_comm(state, e_introduced_binding, x_actor_binding, x_what_binding, h_where, where_binding_generator):
    # We only know how to copy things from the
    # computer's perspective
    if x_actor_binding.value.name == "Computer":
        # Only allow copying files and folders
        if isinstance(x_what_binding.value, (File, Folder)):
            # We are guaranteed at least one x_where_binding since
            # this is a required virtual_arg
            for x_where_binding in where_binding_generator:
                if isinstance(x_where_binding.value, Folder):
                    yield state.apply_operations([CopyOperation(None, x_what_binding, x_where_binding)])

                else:
                    report_error(["cantDo", "copy", x_where_binding.variable.name])

        else:
            report_error(["cantDo", "copy", x_what_binding.variable.name])

    else:
        report_error(["dontKnowActor", x_actor_binding.variable.name])


@Predication(vocabulary, names=["_in_p_loc"], handles=[("StativePreposition", EventOption.optional)])
def in_p_loc(state, e_introduced_binding, x_actor_binding, x_location_binding):
    if x_actor_binding.value is not None:
        if x_location_binding.value is not None:
            if hasattr(x_location_binding.value, "contained_items"):
                # x_actor is "in" x_location if x_location contains it
                for item in x_location_binding.value.contained_items(x_location_binding.variable):
                    if x_actor_binding.value == item:
                        # Variables are already set,
                        # no need to set them again, just return the state
                        yield state

        else:
            # Need to find all the things that x_actor is "in"
            if hasattr(x_actor_binding.value, "containers"):
                for item in x_actor_binding.value.containers(x_actor_binding.variable):
                    yield state.set_x(x_location_binding.variable.name, item)

    else:
        # Actor is unbound, this means "What is in X?" type of question
        # Whatever x_location "contains" is "in" it
        if hasattr(x_location_binding.value, "contained_items"):
            for location in x_location_binding.value.contained_items(x_location_binding.variable):
                yield state.set_x(x_actor_binding.variable.name, location)

    report_error(["thingHasNoLocation", x_actor_binding.variable.name, x_location_binding.variable.name])


# c_raw_text_value will always be set to a raw string
@Predication(vocabulary)
def quoted(state, c_raw_text_value, i_text_binding):
    if i_text_binding.value is None:
        yield state.set_x(i_text_binding.variable.name, QuotedText(c_raw_text_value))

    else:
        if isinstance(i_text_binding.value, QuotedText) and i_text_binding.value.name == c_raw_text_value:
            yield state


# Yield all the solutions for fw_seq where value is bound
# and x_phrase_binding may or may not be
def yield_from_fw_seq(state, x_phrase_binding, value):
    if x_phrase_binding.value is None:
        # x has not be bound
        if is_this_last_fw_seq(state) and hasattr(value, "all_interpretations"):
            # Get all the interpretations of the quoted text
            # and bind them iteratively
            for interpretation in value.all_interpretations(state):
                yield state.set_x(x_phrase_binding.variable.name, interpretation)

            return

        yield state.set_x(x_phrase_binding.variable.name, value)

    else:
        # x has been bound, compare it to value
        if hasattr(value, "all_interpretations"):
            # Get all the interpretations of the object
            # and check them iteratively
            for interpretation in value.all_interpretations(state):
                if interpretation == x_phrase_binding.value:
                    yield state
        else:
            if value == x_phrase_binding.value:
                yield state


@Predication(vocabulary, names=["fw_seq"])
def fw_seq1(state, x_phrase_binding, i_part_binding):
    if i_part_binding.value is None:
        if x_phrase_binding.value is None:
            # This should never happen since it basically means
            # "return all possible strings"
            assert False

        else:
            yield state.set_x(i_part_binding.variable.name, x_phrase_binding.value)

    else:
        yield from yield_from_fw_seq(state, x_phrase_binding, i_part_binding.value)


@Predication(vocabulary, names=["fw_seq"])
def fw_seq2(state, x_phrase_binding, i_part1_binding, i_part2_binding):
    # Only succeed if part1 and part2 are set and are QuotedText instances to avoid
    # having to split x into pieces somehow
    if isinstance(i_part1_binding.value, QuotedText) and isinstance(i_part2_binding.value, QuotedText):
        combined_value = QuotedText(" ".join([i_part1_binding.value.name, i_part2_binding.value.name]))
        yield from yield_from_fw_seq(state, x_phrase_binding, combined_value)


@Predication(vocabulary, names=["fw_seq"])
def fw_seq3(state, x_phrase_binding, x_part1_binding, i_part2_binding):
    # Only succeed if part1 and part2 are set and are QuotedText instances to avoid
    # having to split x into pieces somehow
    if isinstance(x_part1_binding.value, QuotedText) and isinstance(i_part2_binding.value, QuotedText):
        combined_value = QuotedText(" ".join([x_part1_binding.value.name, i_part2_binding.value.name]))
        yield from yield_from_fw_seq(state, x_phrase_binding, combined_value)


# loc_nonsp will add up the size of files if a collective set of actors comes in, so declare that
@Predication(vocabulary, arguments=[DeclareArg("e"), DeclareArg("x", collective_behavior=CollectiveBehavior.different), DeclareArg("x")])
def loc_nonsp(state, e_introduced_binding, x_actor_binding, x_location_binding):
    if x_actor_binding.value is not None:
        if x_location_binding.value is not None:
            if isinstance(x_location_binding.value, Measurement):
                # asking to see if actor "is" a measurement, as in "is file 5 mb"
                if hasattr(x_actor_binding.value, "size_measurement"):
                    # Only works if actor has a measurement
                    if x_actor_binding.variable.is_collective:
                        # Collective: We need to see if all of the variables in this variable set add up to the value
                        # For simplicity, assume all measurements are in megabytes
                        x_actor_variable_set_items = x_actor_binding.variable.variable_set_items
                        total = 0
                        for item in x_actor_variable_set_items:
                            total += item.size_measurement().count

                        if x_location_binding.value.count == total:
                            yield state.set_x(x_actor_binding.variable.name, x_actor_binding.value,
                                              used_collective=True)

                        else:
                            report_error(["xIsNotY", x_actor_binding.variable.name, x_location_binding.value.count])
                            return

                    else:
                        # Distributive: each one must be this value
                        if x_location_binding.value == x_actor_binding.value.size_measurement():
                            yield state

                        else:
                            report_error(["xIsNotY", x_actor_binding.variable.name, x_location_binding.value.count])
                            return

            elif hasattr(x_actor_binding.value, "all_locations"):
                # The system is asking if a location of x_actor is x_location,
                # so check the list exhaustively until we find a match, then stop
                for location in x_actor_binding.value.all_locations(x_actor_binding.variable):
                    if location == x_location_binding.value:
                        # Variables are already set,
                        # no need to set them again, just return the state
                        yield state
                        break

        else:
            if hasattr(x_actor_binding.value, "all_locations"):
                # This is a "where is X?" type query since no location specified
                for location in x_actor_binding.value.all_locations(x_actor_binding.variable):
                    yield state.set_x(x_location_binding.variable.name, location)

    else:
        # For now, return errors for cases where x_actor is unbound
        pass

    report_error(["thingHasNoLocation", x_actor_binding.variable.name, x_location_binding.variable.name])


@Predication(vocabulary, names=["_file_n_of"])
def file_n_of(state, x_binding, i_binding):
    if x_binding.value is None:
        iterator = state.all_individuals()

    else:
        iterator = [x_binding.value]

    for value in iterator:
        if isinstance(value, File):
            new_state = state.set_x(x_binding.variable.name, value)
            yield new_state

        else:
            report_error(["xIsNotY", x_binding.variable.name, "file"])


@Predication(vocabulary, names=["_folder_n_of"])
def folder_n_of(state, x_binding, i_binding):
    if x_binding.value is None:
        # Variable is unbound:
        # iterate over all individuals in the world
        # using the iterator returned by state.all_individuals()
        iterator = state.all_individuals()

    else:
        # Variable is bound: create an iterator that will iterate
        # over just that one by creating a list and adding it as
        # the only element
        iterator = [x_binding.value]

    # By converting both cases to an iterator, the code that
    # checks if x is "a folder" can be shared
    for value in iterator:
        # "isinstance" is a built-in function in Python that
        # checks if a variable is an
        # instance of the specified class
        if isinstance(value, Folder):
            # state.set_x() returns a *new* state that
            # is a copy of the old one with just that one
            # variable set to a new value
            new_state = state.set_x(x_binding.variable.name, value)
            yield new_state

        else:
            report_error(["xIsNotY", x_binding.variable.name, "folder"])


pipeline_logger = logging.getLogger('Pipeline')
cardinal_logger = logging.getLogger('Cardinal')
