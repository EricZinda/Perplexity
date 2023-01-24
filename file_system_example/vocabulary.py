import logging
from file_system_example.objects import File, Folder, Actor, Container, QuotedText
from file_system_example.state import DeleteOperation, FileSystemState
from perplexity.execution import ExecutionContext, call, report_error, execution_context
from perplexity.tree import TreePredication
from perplexity.vocabulary import Vocabulary, Predication, EventOption

vocabulary = Vocabulary()


# TODO: delete_v_1 doesn't actually meet the contract since it doesn't allow free variables
@Predication(vocabulary, names=["_delete_v_1", "_erase_v_1"])
def delete_v_1_comm(state, e_introduced, x_actor, x_what):
    # We only know how to delete things from the
    # computer's perspective
    if state.get_variable(x_actor).name == "Computer":
        x_what_value = state.get_variable(x_what)

        # If this is text, make sure it actually exists
        if isinstance(x_what_value, QuotedText):
            actual_item = state.file_system.item_from_path(x_what_value.name)
            if actual_item is not None:
                yield state.apply_operations([DeleteOperation(x_what_value)])
            else:
                report_error(["notFound", x_what])
        else:
            # Only allow deleting files and folders or
            # textual names of files
            if isinstance(x_what_value, (File, Folder, QuotedText)):
                yield state.apply_operations([DeleteOperation(x_what_value)])

            else:
                report_error(["cantDo", "delete", x_what])

    else:
        report_error(["dontKnowActor", x_actor])


# This is a helper function that any predication that can
# be "very'd" can use to understand just how "very'd" it is
def degree_multiplier_from_event(state, e_introduced):
    # if a "very" is modifying this event, use that value
    # otherwise, return 1
    e_introduced_value = state.get_variable(e_introduced)
    if e_introduced_value is None or "DegreeMultiplier" not in e_introduced_value:
        degree_multiplier = 1

    else:
        degree_multiplier = e_introduced_value["DegreeMultiplier"]["Value"]

    return degree_multiplier


def in_scope(state, obj):
    # If it is the folder the user is in
    user = state.user()
    if user.current_directory == obj:
        return True

    # If it is a file in the directory the user is in
    for file in user.current_directory.contained_items():
        if file == obj:
            return True


@Predication(vocabulary, names=["_this_q_dem"])
def this_q_dem(state, x_variable, h_rstr, h_body):
    # Run the RSTR which should fill in the variable with an item
    rstr_single_solution = None
    for solution in call(state, h_rstr):
        if in_scope(solution, solution.get_variable(x_variable)):
            if rstr_single_solution is None:
                rstr_single_solution = solution

            else:
                # Make sure there is only one since "this" shouldn't be ambiguous
                report_error(["moreThanOneInScope", ["AtPredication", h_body, x_variable]], force=True)
                return

    if rstr_single_solution is not None:
        # Now see if that solution works in the BODY
        body_found = False
        for body_solution in call(rstr_single_solution, h_body):
            yield body_solution

    else:
        # Ignore whatever error the RSTR produced, this is a better one
        # Report the variable's English representation as it would be in the BODY
        report_error(["doesntExist", ["AtPredication", h_body, x_variable]], force=True)


@Predication(vocabulary, names=["_a_q"])
def a_q(state, x_variable, h_rstr, h_body):
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
        report_error(["doesntExist", ["AtPredication", h_body, x_variable]], force=True)


@Predication(vocabulary, names=["pron"])
def pron(state, x_who):
    x_who_value = state.get_variable(x_who)
    if x_who_value is None:
        iterator = state.all_individuals()
    else:
        iterator = [x_who_value]

    person = int(state.get_variable("tree")["Variables"][x_who]["PERS"])
    for item in iterator:
        if isinstance(item, Actor) and item.person == person:
            yield state.set_x(x_who, item)
            break
        else:
            report_error(["dontKnowPronoun", x_who])


# Many quantifiers are simply markers and should use this as
# the default behavior

# Many quantifiers are simply markers and should use this as
# the default behavior
@Predication(vocabulary, names=["pronoun_q"])
def default_quantifier(state, x_variable, h_rstr_orig, h_body_orig, reverse=False):
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
            report_error(["doesntExist", ["AtPredication", h_body, x_variable]], force=True)


def rstr_reorderable(rstr):
    return isinstance(rstr, TreePredication) and rstr.name in ["place_n", "thing"]


@Predication(vocabulary, names=["which_q", "_which_q"])
def which_q(state, x_variable, h_rstr, h_body):
    yield from default_quantifier(state, x_variable, h_rstr, h_body, reverse=rstr_reorderable(h_rstr))


@Predication(vocabulary, names=["_very_x_deg"])
def very_x_deg(state, e_introduced, e_target):
    # First see if we have been "very'd"!
    initial_degree_multiplier = degree_multiplier_from_event(state, e_introduced)

    # We'll interpret "very" as meaning "one order of magnitude larger"
    yield state.add_to_e(e_target, "DegreeMultiplier", {"Value": initial_degree_multiplier * 10, "Originator": execution_context().current_predication_index()})


@Predication(vocabulary, names=["_large_a_1"], handles=[("DegreeMultiplier", EventOption.optional)])
def large_a_1(state, e_introduced, x_target):
    x_target_value = state.get_variable(x_target)

    if x_target_value is None:
        iterator = state.all_individuals()
    else:
        iterator = [x_target_value]

    # See if any modifiers have changed *how* large
    # we should be
    degree_multiplier = degree_multiplier_from_event(state, e_introduced)

    for item in iterator:
        # Arbitrarily decide that "large" means a size greater
        # than 1,000,000 and apply any multipliers that other
        # predications set in the introduced event
        # Remember that "hasattr()" checks if an object has
        # a property
        if hasattr(item, 'size') and item.size > degree_multiplier * 1000000:
            new_state = state.set_x(x_target, item)
            yield new_state
        else:
            report_error(["adjectiveDoesntApply", "large", x_target])


@Predication(vocabulary, names=["_small_a_1"])
def small_a_1(state, e_introduced, x_target):
    x_target_value = state.get_variable(x_target)

    if x_target_value is None:
        iterator = state.all_individuals()
    else:
        iterator = [x_target_value]

    for item in iterator:
        # Arbitrarily decide that "small" means a size <= 1,000,000
        # Remember that "hasattr()" checks if an object has
        # a property
        if hasattr(item, 'size') and item.size <= 1000000:
            new_state = state.set_x(x_target, item)
            yield new_state
        else:
            report_error(["adjectiveDoesntApply", "small", x_target])


@Predication(vocabulary)
def thing(state, x):
    x_value = state.get_variable(x)

    if x_value is None:
        iterator = state.all_individuals()
    else:
        iterator = [x_value]

    for item in iterator:
        yield state.set_x(x, item)


@Predication(vocabulary)
def place_n(state, x):
    x_value = state.get_variable(x)

    if x_value is None:
        iterator = state.all_individuals()
    else:
        iterator = [x_value]

    for item in iterator:
        # Any object is a "place" as long as it can
        # contain things
        if isinstance(item, Container):
            yield state.set_x(x, item)


@Predication(vocabulary, names=["_in_p_loc"])
def in_p_loc(state, e_introduced, x_actor, x_location):
    x_actor_value = state.get_variable(x_actor)
    x_location_value = state.get_variable(x_location)

    if x_actor_value is not None:
        if x_location_value is not None:
            # x_actor is "in" x_location if x_location contains it
            for item in x_location_value.contained_items():
                if x_actor_value == item:
                    # Variables are already set,
                    # no need to set them again, just return the state
                    yield state
        else:
            # Need to find all the things that x_actor is "in"
            if hasattr(x_actor_value, "containers"):
                for item in x_actor_value.containers():
                    yield state.set_x(x_location, item)

    else:
        # Actor is unbound, this means "What is in X?" type of question
        # Whatever x_location "contains" is "in" it
        if hasattr(x_location_value, "contained_items"):
            for location in x_location_value.contained_items():
                yield state.set_x(x_actor, location)

    report_error(["thingHasNoLocation", x_actor, x_location])


@Predication(vocabulary)
def quoted(state, c_raw_text, i_text):
    # c_raw_text_value will always be set to a
    # raw string
    c_raw_text_value = c_raw_text
    i_text_value = state.get_variable(i_text)

    if i_text_value is None:
        yield state.set_x(i_text, QuotedText(c_raw_text_value))
    else:
        if isinstance(i_text_value, QuotedText) and i_text_value.name == c_raw_text:
            yield state


@Predication(vocabulary, names=["fw_seq"])
def fw_seq1(state, x_phrase, i_part):
    x_phrase_value = state.get_variable(x_phrase)
    i_part_value = state.get_variable(i_part)
    if i_part_value is None:
        if x_phrase_value is None:
            # This should never happen since it basically means
            # "return all possible strings"
            assert False
        else:
            yield state.set_x(i_part, x_phrase_value)
    else:
        if x_phrase_value is None:
            yield state.set_x(x_phrase, i_part_value)

        elif x_phrase_value == i_part_value:
            yield state


@Predication(vocabulary, names=["fw_seq"])
def fw_seq2(state, x_phrase, i_part1, i_part2):
    x_phrase_value = state.get_variable(x_phrase)
    i_part1_value = state.get_variable(i_part1)
    i_part2_value = state.get_variable(i_part2)

    if isinstance(i_part1_value, QuotedText) and isinstance(i_part2_value, QuotedText):
        combined_value = QuotedText(" ".join([i_part1_value.name, i_part2_value.name]))
        if x_phrase_value is None:
            yield state.set_x(x_phrase, combined_value)

        elif isinstance(x_phrase_value, QuotedText) and x_phrase_value.name == combined_value.name:
            yield state


@Predication(vocabulary, names=["fw_seq"])
def fw_seq3(state, x_phrase, x_part1, i_part2):
    x_phrase_value = state.get_variable(x_phrase)
    x_part1_value = state.get_variable(x_part1)
    i_part2_value = state.get_variable(i_part2)

    if isinstance(x_part1_value, QuotedText) and isinstance(i_part2_value, QuotedText):
        combined_value = QuotedText(" ".join([x_part1_value.name, i_part2_value.name]))
        if x_phrase_value is None:
            yield state.set_x(x_phrase, combined_value)

        elif isinstance(x_phrase_value, QuotedText) and x_phrase_value.name == combined_value.name:
            yield state


@Predication(vocabulary)
def proper_q(state, x_variable, h_rstr, h_body):
    yield from default_quantifier(state, x_variable, h_rstr, h_body)


@Predication(vocabulary)
def loc_nonsp(state, e_introduced, x_actor, x_location):
    x_actor_value = state.get_variable(x_actor)
    x_location_value = state.get_variable(x_location)

    if x_actor_value is not None:
        if hasattr(x_actor_value, "all_locations"):
            if x_location_value is None:
                # This is a "where is X?" type query since no location specified
                for location in x_actor_value.all_locations():
                    yield state.set_x(x_location, location)
            else:
                # The system is asking if a location of x_actor is x_location,
                # so check the list exhaustively until we find a match, then stop
                for location in x_actor_value.all_locations():
                    if location == x_location_value:
                        # Variables are already set,
                        # no need to set them again, just return the state
                        yield state
                        break
    else:
        # For now, return errors for cases where x_actor is unbound
        pass

    report_error(["thingHasNoLocation", x_actor, x_location])


@Predication(vocabulary, names=["_file_n_of"])
def file_n_of(state, x, i):
    x_value = state.get_variable(x)
    if x_value is None:
        iterator = state.all_individuals()
    else:
        iterator = [x_value]

    for item in iterator:
        if isinstance(item, File):
            new_state = state.set_x(x, item)
            yield new_state
        else:
            report_error(["xIsNotY", x, "file"])


@Predication(vocabulary, names=["_folder_n_of"])
def folder_n_of(state, x, i):
    x_value = state.get_variable(x)
    if x_value is None:
        # Variable is unbound:
        # iterate over all individuals in the world
        # using the iterator returned by state.all_individuals()
        iterator = state.all_individuals()

    else:
        # Variable is bound: create an iterator that will iterate
        # over just that one by creating a list and adding it as
        # the only element
        iterator = [x_value]

    # By converting both cases to an iterator, the code that
    # checks if x is "a folder" can be shared
    for item in iterator:
        # "isinstance" is a built-in function in Python that
        # checks if a variable is an
        # instance of the specified class
        if isinstance(item, Folder):
            # state.set_x() returns a *new* state that
            # is a copy of the old one with just that one
            # variable set to a new value
            new_state = state.set_x(x, item)
            yield new_state

        else:
            report_error(["xIsNotY", x, "folder"])


pipeline_logger = logging.getLogger('Pipeline')
