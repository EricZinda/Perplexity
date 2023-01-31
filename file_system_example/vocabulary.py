import logging
from file_system_example.objects import File, Folder, Actor, Container, QuotedText
from file_system_example.state import DeleteOperation, ChangeDirectoryOperation
from perplexity.variable_binding import VariableBinding
from perplexity.execution import call, report_error, execution_context
from perplexity.tree import TreePredication, is_this_last_fw_seq
from perplexity.vocabulary import Vocabulary, Predication, EventOption

vocabulary = Vocabulary()


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


# TODO: delete_v_1 doesn't actually meet the contract since it doesn't allow free variables
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


@Predication(vocabulary, names=["_this_q_dem"])
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


@Predication(vocabulary, names=["_a_q"])
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


# Many quantifiers are simply markers and should use this as
# the default behavior

# Many quantifiers are simply markers and should use this as
# the default behavior
@Predication(vocabulary, names=["pronoun_q"])
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


@Predication(vocabulary, names=["which_q", "_which_q"])
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


@Predication(vocabulary, names=["_in_p_loc"])
def in_p_loc(state, e_introduced_binding, x_actor_binding, x_location_binding):
    if x_actor_binding.value is not None:
        if x_location_binding.value is not None:
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


def yield_from_fw_seq(state, variable_data, value):
    if is_this_last_fw_seq(state):
        if hasattr(value, "all_interpretations"):
            # Get all the interpretations of the quoted text
            # and return them iteratively
            for interpretation in value.all_interpretations(state):
                yield state.set_x(variable_data.name, interpretation)
        else:
            yield value

    else:
        yield state.set_x(variable_data.name, value)


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
        if x_phrase_binding.value is None:
            yield from yield_from_fw_seq(state, x_phrase_binding.variable, i_part_binding.value)

        else:
            if hasattr(i_part_binding.value, "all_interpretations"):
                # Get all the interpretations of the quoted text
                # and check them iteratively
                for interpretation in i_part_binding.value.all_interpretations(state):
                    if interpretation == x_phrase_binding.value:
                        yield state


@Predication(vocabulary, names=["fw_seq"])
def fw_seq2(state, x_phrase_binding, i_part1_binding, i_part2_binding):
    if isinstance(i_part1_binding.value, QuotedText) and isinstance(i_part2_binding.value, QuotedText):
        combined_value = QuotedText(" ".join([i_part1_binding.value.name, i_part2_binding.value.name]))
        if x_phrase_binding.value is None:
            yield from yield_from_fw_seq(state, x_phrase_binding.variable, combined_value)


@Predication(vocabulary, names=["fw_seq"])
def fw_seq3(state, x_phrase_binding, x_part1_binding, i_part2_binding):
    if isinstance(x_part1_binding.value, QuotedText) and isinstance(i_part2_binding.value, QuotedText):
        combined_value = QuotedText(" ".join([x_part1_binding.value.name, i_part2_binding.value.name]))
        if x_phrase_binding.value is None:
            yield from yield_from_fw_seq(state, x_phrase_binding.variable, combined_value)


@Predication(vocabulary)
def proper_q(state, x_variable_binding, h_rstr, h_body):
    yield from default_quantifier(state, x_variable_binding, h_rstr, h_body)


@Predication(vocabulary)
def loc_nonsp(state, e_introduced_binding, x_actor_binding, x_location_binding):
    if x_actor_binding.value is not None:
        if hasattr(x_actor_binding.value, "all_locations"):
            if x_location_binding.value is None:
                # This is a "where is X?" type query since no location specified
                for location in x_actor_binding.value.all_locations(x_actor_binding.variable):
                    yield state.set_x(x_location_binding.variable.name, location)

            else:
                # The system is asking if a location of x_actor is x_location,
                # so check the list exhaustively until we find a match, then stop
                for location in x_actor_binding.value.all_locations(x_actor_binding.variable):
                    if location == x_location_binding.value:
                        # Variables are already set,
                        # no need to set them again, just return the state
                        yield state
                        break

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
