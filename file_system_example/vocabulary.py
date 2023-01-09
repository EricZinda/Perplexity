import logging

from file_system_example.objects import File, DeleteOperation, Folder, Actor
from perplexity.execution import ExecutionContext, call, report_error
from perplexity.vocabulary import Vocabulary, Predication

vocabulary = Vocabulary()


# TODO: delete_v_1 doesn't actually meet the contract since it doesn't allow free variables
@Predication(vocabulary, name="_delete_v_1", synonyms=["_erase_v_1"])
def delete_v_1(state, e_introduced, x_actor, x_what):
    # We only know how to delete things from the
    # computer's perspective
    if state.get_variable(x_actor).name == "Computer":
        x_what_value = state.get_variable(x_what)

        # Only allow deleting files and folders
        if isinstance(x_what_value, (File, Folder)):
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
        degree_multiplier = e_introduced_value["DegreeMultiplier"]

    return degree_multiplier


@Predication(vocabulary, name="_a_q")
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


@Predication(vocabulary, name="pron")
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


# This is just used as a way to provide a scope for a
# pronoun, so it only needs the default behavior
@Predication(vocabulary, name="pronoun_q")
def pronoun_q(state, x, h_rstr, h_body):
    yield from default_quantifier(state, x, h_rstr, h_body)


@Predication(vocabulary, name="_which_q")
def which_q(state, x_variable, h_rstr, h_body):
    yield from default_quantifier(state, x_variable, h_rstr, h_body)


# Many quantifiers are simply markers and should use this as
# the default behavior
def default_quantifier(state, x_variable, h_rstr, h_body):
    # Find every solution to RSTR
    rstr_found = False
    for solution in call(state, h_rstr):
        rstr_found = True

        # And return it if it is true in the BODY
        for body_solution in call(solution, h_body):
            yield body_solution

    if not rstr_found:
        # Ignore whatever error the RSTR produced, this is a better one
        report_error(["doesntExist", ["AtPredication", h_body, x_variable]], force=True)


@Predication(vocabulary, "_very_x_deg")
def very_x_deg(state, e_introduced, e_target):
    # First see if we have been "very'd"!
    initial_degree_multiplier = degree_multiplier_from_event(state, e_introduced)

    # We'll interpret "very" as meaning "one order of magnitude larger"
    yield state.add_to_e(e_target, "DegreeMultiplier", initial_degree_multiplier * 10)


@Predication(vocabulary, name="_large_a_1")
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


@Predication(vocabulary, name="_file_n_of")
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


@Predication(vocabulary, name="_folder_n_of")
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
