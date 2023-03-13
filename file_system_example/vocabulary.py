import copy
import enum
import itertools
import logging
from file_system_example.objects import File, Folder, Actor, Container, QuotedText, Megabyte
from file_system_example.state import DeleteOperation, ChangeDirectoryOperation, CopyOperation
from perplexity.cardinals import split_cardinal_rstr, cardinal_group_outgoing_solutions, \
    cardinal_variable_set_incoming_next_this_cardinal_group, yield_all_cardinal_group_solutions, \
    unique_solution_if_index, Measurement, create_cardinal_group_generator
from perplexity.utilities import at_least_one_generator, is_plural
from perplexity.variable_binding import VariableBinding
from perplexity.execution import call, report_error, execution_context, \
    create_solution_id, create_variable_set_cache, VariableSetRestart, get_parent_variable_set_cache, \
    set_variable_set_cache, get_this_variable_set_cache, get_cardinal_group_cache
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


@Predication(vocabulary, names=["_the_q_cardinal"])
def the_q_cardinal(state, x_variable_binding, h_rstr, h_body):
    if x_variable_binding.variable.is_collective:
        find_next_cardinal_group = True
        cardinal_group_solution = None
        while find_next_cardinal_group:
            # Loop through all the elements of this variable set
            variable_set_solutions = []
            for variable_set_item in call(state, h_rstr):
                # We have an element of a cardinal group
                body_solutions = []
                try:
                    for body_solution in call(state, h_body):
                        body_solutions.append(body_solution)

                except VariableSetRestart as error:
                    if error.child_cardinal_variable == x_variable_binding.variable.name:
                        raise

                    else:
                        # Somehow tell card_scope() to restart this group
                        # Somehow tell the child to find the next group
                        # and keep us in same group
                        find_next_cardinal_group = True
                        break

                if len(body_solutions) > 0:
                    variable_set_solutions.append(body_solutions)

                else:
                    # One item didn't work, tell the parent to retry
                    # The current variable set and we will try another
                    # group
                    raise VariableSetRestart(x_variable_binding.variable.name)

            # All the variable_set items worked, thus this group worked
            if cardinal_group_solution is None:
                cardinal_group_solution = variable_set_solutions
                # Somehow tell the child to try the next group
                find_next_cardinal_group = True

            else:
                # Fail because there was more than on cardinal set that worked
                # report_error()
                return

# @Predication(vocabulary, names=["_the_q_cardinal"])
# def the_q_cardinal(state, x_variable_binding, h_rstr, h_body):
#     if x_variable_binding.variable.is_collective:
#         x_variable_set_items = x_variable_binding.variable.variable_set_items
#         variable_set_solutions = []
#         for item in x_variable_set_items:
#             body_solutions = []
#             for body_solution in call(state.set_x(x_variable_binding.variable.name, item), h_body):
#                 body_solutions.append(body_solution)
#
#             if len(body_solutions) > 0:
#                 variable_set_solutions.append(body_solutions)
#             else:
#                 return
#
#         # ??? Need to ensure no other the_s ran
#         for variable_set_solution in variable_set_solutions:
#             for body_solution in variable_set_solution:
#                 yield body_solution
#     else:
#         yield from this_q_dem(x_variable_binding, h_rstr, h_body)


# @Predication(vocabulary, names=["_the_q"])
# def the_q(state, x_variable_binding, h_rstr, h_body):
#     rstr_single_solution = None
#     current_variable_set = None
#     if x_variable_binding.variable.is_collective:
#         for solution in call(state, h_rstr):
#             x_variable_binding = solution.get_binding(x_variable_binding.variable.name)
#             if current_variable_set is None or x_variable_binding.variable.variable_set_id == current_variable_set:
#                 # Now see if that solution works in the BODY
#                 try:
#                     for body_solution in call(rstr_single_solution, h_body):
#                         yield body_solution
#                 except VariableSetRestart:
#                     # A child asked us to retry which means a child had a variable_set that didn't completely work against this set
#                     # So: the alternatives we have so far are right, but we need to restart the variable set (this keeps the same group to allow the child to cache things there)
#                     # Tell the rstr to retry
#                     this_variable_set_cache["NextSolution"] = True
#                     break
#
#             else:
#                 # More than one variable set, fail

# @Predication(vocabulary, names=["_the_q"])
def the_q(state, x_variable_binding, h_rstr, h_body):
    yield from this_q_dem(state, x_variable_binding, h_rstr, h_body)


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
            report_error(["xIsNotYValue", x_binding.value, "megabyte"])


@Predication(vocabulary)
def card(state, c_count, e_introduced_binding, x_target_binding):
    assert False


class NoMoreVariableSets(Exception):
    pass


class NoMoreCardinalGroups(Exception):
    pass


# card_with_scope has a current group and set.
# card_with_scope iterates through all the cardinal groups for a cardinal
# It has two incoming "arguments" ("NextCardinalGroup" and "NextVariableSet")
# That tell it to move to the next item in either.
# If you just iterate it with those two arguments set to false, it iterates its current variable set
# starting with the first variable set item
#
# The quantifier that owns this cardinal communicates with it by using the
# variable_set_cache associated with this x_target_binding
# "NextVariableSet" = True: to get the next current variable set
# "NextCardinalGroup" = True: to find next cardinal group
@Predication(vocabulary)
def card_with_scope(state, c_count, e_introduced_binding, x_target_binding, h_scope):
    variable_name = x_target_binding.variable.name
    c_count_value = int(c_count)
    parent_variable_set_cache = get_parent_variable_set_cache(variable_name)

    next_cardinal_group = False
    next_variable_set = False
    if parent_variable_set_cache["ChildCardinals"][variable_name].get("NextCardinalGroup", False):
        cardinal_logger.debug(f'var:{variable_name}: card_with_scope -> NextCardinalGroup=True')
        parent_variable_set_cache["ChildCardinals"][variable_name]["NextCardinalGroup"] = False
        next_cardinal_group = True

    elif parent_variable_set_cache["ChildCardinals"][variable_name].get("NextVariableSet", False):
        cardinal_logger.debug(f'var:{variable_name}: card_with_scope -> NextVariableSet=True')
        parent_variable_set_cache["ChildCardinals"][variable_name]["NextVariableSet"] = False
        next_variable_set = True

    # Each cardinal group (and associated generator) are created for a parent *variable set*
    # If this is the first time we've seen this parent_set, create a new cardinal group
    new_parent_variable_set = "CardinalGroupGenerator" not in parent_variable_set_cache["ChildCardinals"][variable_name]
    if new_parent_variable_set:
        cardinal_logger.debug(f'var:{variable_name}: card_with_scope -> New parent variable set: creating new generator')
        cardinal_group_generator = create_cardinal_group_generator(state,
                                                                   parent_variable_set_cache["ChildIsCollective"],
                                                                   variable_name,
                                                                   h_scope,
                                                                   c_count_value)

        parent_variable_set_cache["ChildCardinals"][variable_name]["CardinalGroupGenerator"] = cardinal_group_generator
        next_cardinal_group = True

    else:
        cardinal_logger.debug(f'var:{variable_name}: card_with_scope -> Same parent variable set: using existing generator')
        cardinal_group_generator = parent_variable_set_cache["ChildCardinals"][variable_name]["CardinalGroupGenerator"]

    if next_cardinal_group:
        try:
            this_cardinal_group = next(cardinal_group_generator)
            parent_variable_set_cache["ChildCardinals"][variable_name]["CurrentCardinalGroup"] = this_cardinal_group
            parent_variable_set_cache["ChildCardinals"][variable_name]["CurrentVariableSetInfoIndex"] = -1
            next_variable_set = True
            cardinal_logger.debug(f'var:{variable_name}: card_with_scope -> Next cardinal group selected: {this_cardinal_group}')

        except StopIteration:
            # No more groups, fail
            cardinal_logger.debug(f'var:{variable_name}: card_with_scope -> FAIL, No more cardinal groups')
            raise NoMoreCardinalGroups

    else:
        this_cardinal_group = parent_variable_set_cache["ChildCardinals"][variable_name]["CurrentCardinalGroup"]
        cardinal_logger.debug(f'var:{variable_name}: card_with_scope -> Using existing cardinal group: {this_cardinal_group}')

    if next_variable_set:
        parent_variable_set_cache["ChildCardinals"][variable_name]["CurrentVariableSetInfoIndex"] += 1
        variable_set_info_index = parent_variable_set_cache["ChildCardinals"][variable_name]["CurrentVariableSetInfoIndex"]
        if variable_set_info_index < len(this_cardinal_group.cardinal_group_items):
            this_variable_set_info = this_cardinal_group.cardinal_group_items[variable_set_info_index]
            # Because this is a new variable set, create a new cache
            set_variable_set_cache(variable_name, create_variable_set_cache(variable_name=variable_name, child_is_collective=False, variable_set_id=this_variable_set_info[0]))
            cardinal_logger.debug(f'var:{variable_name}: card_with_scope -> Next variable set: {this_variable_set_info[1]}')

        else:
            # No more variable sets, fail
            cardinal_logger.debug(f'var:{variable_name}: card_with_scope -> No more variable sets')
            raise NoMoreVariableSets

    else:
        if parent_variable_set_cache["ChildCardinals"][variable_name]["RestartGroup"]:
            parent_variable_set_cache["ChildCardinals"][variable_name]["RestartGroup"] = False
            cardinal_logger.debug(f'var:{variable_name}: card_with_scope -> Restarting with variable set 0')
            variable_set_info_index = 0

        else:
            variable_set_info_index = parent_variable_set_cache["ChildCardinals"][variable_name]["CurrentVariableSetInfoIndex"]
            cardinal_logger.debug(f'var:{variable_name}: card_with_scope -> Using existing variable set index {variable_set_info_index}')

        this_variable_set_info = this_cardinal_group.cardinal_group_items[variable_set_info_index]
        cardinal_logger.debug(f'var:{variable_name}: card_with_scope -> Variable set is {this_variable_set_info[1]}')

    # Now yield each item in the variable set
    variable_set_id = this_variable_set_info[0]
    variable_set = this_variable_set_info[1]

    for variable_set_item_index in range(0, len(variable_set)):
        cardinal_logger.debug(f'var:{variable_name}: card_with_scope -> Checking variable set item {variable_set_item_index}: {variable_set[variable_set_item_index]}')
        yield state.set_x(x_target_binding.variable.name, variable_set[variable_set_item_index],
                          cardinal_group_id=this_cardinal_group.cardinal_group_id,
                          variable_set_id=variable_set_id,
                          variable_set_item_id=variable_set_item_index,
                          is_collective=this_cardinal_group.is_collective,
                          used_collective=this_cardinal_group.used_collective,
                          variable_set_items=variable_set)


# Many quantifiers are simply markers and should use this as
# the default behavior
@Predication(vocabulary, names=["pronoun_q", "proper_q", "udef_q"])
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


# The quantifier gets an incoming variable set and tries to find a single cardinal group that works for it
# If the incoming variable set is true for all variable sets in its group, the quantifier is true for its cardinal group.
#   BUT: Each variable set it is true for is a different "set based answer"
# Because the parent cardinal is testing a variable set *iteratively*,
# We need to remember the "current" cardinal group *for that set* so we can reuse it for each element of the set
# We track this in the parent_variable_set_cache
# If it succeeds, the parent will ask for alternative groups that work against that set as well
@Predication(vocabulary, names=["pronoun_q_cardinal", "proper_q_cardinal", "udef_q_cardinal"])
def default_quantifier_cardinal(state, x_variable_binding, h_rstr_orig, h_body_orig, reverse=False):
    h_rstr = h_body_orig if reverse else h_rstr_orig
    h_body = h_rstr_orig if reverse else h_body_orig

    # parent_variable_set_cache holds the cached information about
    # which group and set we are currently on since a cardinal group goes with a parent *set*.
    # The cardinal always starts iterating with the
    # first variable set item in its current set
    parent_variable_set_cache = get_parent_variable_set_cache(x_variable_binding.variable.name)
    if x_variable_binding.variable.name not in parent_variable_set_cache["ChildCardinals"]:
        parent_variable_set_cache["ChildCardinals"][x_variable_binding.variable.name] = {}

    try:
        cardinal_logger.debug(f'var:{x_variable_binding.variable.name}: card_quantifier -> Find next cardinal group that succeeds...')

        # Now we have a group to to work with, see if it works for this
        # incoming variable set item. If any item of the set fails, it will
        # raise VariableSetRestart which our parent group will catch and
        # retry the parent variable set from the beginning.
        # It will also set this_variable_set_cache["NextCardinalGroup"] = True
        # To make sure we try a new group
        this_cardinal_group_solution = quantifier_incoming_variable_set_item_test_this_cardinal_group(parent_variable_set_cache,
                                                                                                       state,
                                                                                                       x_variable_binding.variable.name,
                                                                                                       h_rstr,
                                                                                                       h_body)
        if this_cardinal_group_solution is None:
            # The group did not work for this incoming variable set item,
            # since we may have already tested some variable set items in the incoming set,
            # ask the parent to restart so we can find a new group
            cardinal_logger.debug(
                f'var:{x_variable_binding.variable.name}: card_quantifier -> FAIL, This cardinal group didn\'t work for this variable set item, ask parent to retry its set')
            raise VariableSetRestart(x_variable_binding.variable.name)

        else:
            # The group worked for this variable set item,
            # Succeed, and the next variable set item will come through
            cardinal_logger.debug(f'var:{x_variable_binding.variable.name}: card_quantifier -> SUCC, this cardinal group worked for this variable set item, return it')
            yield from yield_all(this_cardinal_group_solution)

    except NoMoreCardinalGroups:
        # There are no more cardinal groups to try,
        # so there are no more answers to the parent variable set
        cardinal_logger.debug(f'var:{x_variable_binding.variable.name}: card_quantifier -> Ran out of cardinal groups, stop looking')
        raise


def yield_all(variable_set_solutions):
    for variable_set_item_solutions in variable_set_solutions:
        for body_solutions in variable_set_item_solutions:
            for body_solution in body_solutions:
                yield body_solution


# For a single incoming variable set item from a parent variable set:
# Get all solutions for each variable set in this_cardinal_group
# All variable sets in the whole cardinal group must work or it fails
def quantifier_incoming_variable_set_item_test_this_cardinal_group(parent_variable_set_cache, state, variable_name, h_rstr, h_body):
    cardinal_logger.debug(f'var:{variable_name}: card_quantifier -> See if cardinal group succeeds, start at first variable set')
    parent_variable_set_cache["ChildCardinals"][variable_name]["RestartGroup"] = True

    variable_set_solutions = []
    next_variable_set = True
    while next_variable_set:
        cardinal_logger.debug(f'var:{variable_name}: card_quantifier -> Check the next variable set...')
        try:
            variable_set_item_solutions = quantifier_variable_set_outgoing(parent_variable_set_cache, state, variable_name, h_rstr, h_body)
            if len(variable_set_item_solutions) == 0:
                # This variable set failed against the parent state
                # So, we fail the group
                cardinal_logger.debug(f'var:{variable_name}: card_quantifier -> FAIL, Variable set failed so group fails')
                return

            else:
                variable_set_solutions.append(variable_set_item_solutions)

            parent_variable_set_cache["ChildCardinals"][variable_name]["NextVariableSet"] = True

        except NoMoreVariableSets:
            next_variable_set = False

    cardinal_logger.debug(f'var:{variable_name}: card_quantifier -> SUCC, all variable sets succeeded: successful cardinal group')
    return variable_set_solutions


# Only see if a single variable set from the current cardinal group is true
def quantifier_variable_set_outgoing(parent_variable_set_cache, state, variable_name, h_rstr, h_body):
    variable_set_item_solutions = []

    restart_variable_set = True
    while restart_variable_set:
        restart_variable_set = False

        # card_scope() will only iterate through the items in
        # one variable set and then fail
        try:
            for variable_set_item_state in call(state, h_rstr):
                body_solutions = []
                for body_solution in call(variable_set_item_state, h_body):
                    body_solutions.append(body_solution)

                if len(body_solutions) > 0:
                    # We had at least one solution to this variable set item
                    # so it succeeds
                    cardinal_logger.debug(f'var:{variable_name}: card_quantifier -> SUCC, found {len(body_solutions)} solutions for this variable set item')
                    variable_set_item_solutions.append(body_solutions)

                else:
                    # One variable set item didn't work, so this cardinal group fails
                    # Because we need to test all items of the parent variable set against the new group
                    # We need to ask the parent to retry its current variable set from the beginning
                    # Wwe will try another group when the quantifier predication is called again
                    cardinal_logger.debug(f'var:{variable_name}: card_quantifier -> FAIL, no solutions worked for this variable set item')
                    parent_variable_set_cache["ChildCardinals"][variable_name]["NextCardinalGroup"] = True
                    return []

        except VariableSetRestart as error:
            # Don't catch restarts that our own cardinal threw
            if error.child_cardinal_variable == variable_name:
                raise

            else:
                cardinal_logger.debug(f'var:{variable_name}: card_quantifier -> Child requested restart, retrying this variable set')
                # Restart from the first variable set item
                # which happens if we just call the rstr again
                variable_set_item_solutions = []
                restart_variable_set = True

    if len(variable_set_item_solutions) == 0:
        cardinal_logger.debug(f'var:{variable_name}: card_quantifier -> FAIL, variable set failed')

    else:
        cardinal_logger.debug(f'var:{variable_name}: card_quantifier -> SUCC, variable set succeeded')

    return variable_set_item_solutions


def root_mrs_evaluator(state, tree):
    restart_variable_set = True
    tree_solutions = []
    while restart_variable_set:
        restart_variable_set = False

        # Pretend we only have a single solution set of one item
        # for the tree
        try:
            for tree_solution in call(state, tree):
                tree_solutions.append(tree_solution)

            if len(tree_solutions) > 0:
                # We had at least one solution to this tree
                # so it succeeds
                cardinal_logger.debug(f'var:root -> SUCC, found {len(tree_solutions)} solutions for this tree')
                break

            else:
                # no more solutions
                cardinal_logger.debug(f'var:root -> no more solutions')

        except VariableSetRestart:
            cardinal_logger.debug(f'var:root -> card_quantifier -> Child requested restart, retrying variable set')
            # Restart from the first variable set item
            # which happens if we just call the rstr again
            tree_solutions = []
            restart_variable_set = True

        except NoMoreCardinalGroups:
            restart_variable_set = False

    if len(tree_solutions) == 0:
        cardinal_logger.debug(f'var:root -> FAIL, no solutions')
        cardinal_logger.debug(f'var:root -> card_quantifier -> No more cardinal groups, no more solutions')

    else:
        for solution in tree_solutions:
            yield solution


# @Predication(vocabulary, names=["_the_q_cardinal"])
# def the_q_cardinal(state, x_variable_binding, h_rstr, h_body):
#     if x_variable_binding.variable.is_collective:
#         find_next_cardinal_group = True
#         cardinal_group_solution = None
#         while find_next_cardinal_group:
#             # Loop through all the elements of this variable set
#             variable_set_solutions = []
#             for variable_set_item in call(state, h_rstr):
#                 # We have an element of a cardinal group
#                 body_solutions = []
#                 try:
#                     for body_solution in call(state, h_body):
#                         body_solutions.append(body_solution)
#
#                 except VariableSetRestart as error:
#                     if error.child_cardinal_variable == x_variable_binding.variable.name:
#                         raise
#
#                     else:
#                         # Somehow tell card_scope() to restart this group
#                         # Somehow tell the child to find the next group
#                         # and keep us in same group
#                         find_next_cardinal_group = True
#                         break
#
#                 if len(body_solutions) > 0:
#                     variable_set_solutions.append(body_solutions)
#
#                 else:
#                     # One item didn't work, tell the parent to retry
#                     # The current variable set and we will try another
#                     # group
#                     raise VariableSetRestart(x_variable_binding.variable.name)
#
#             # All the variable_set items worked, thus this group worked
#             if cardinal_group_solution is None:
#                 cardinal_group_solution = variable_set_solutions
#                 # Somehow tell the child to try the next group
#                 find_next_cardinal_group = True
#
#             else:
#                 # Fail because there was more than on cardinal set that worked
#                 # report_error()
#                 return


# rewrite: default_q(x, [cardinal(x, ...), other()], body)
# to: cardinal(x, [other()], default_q(x, thing(x), body)
# to: cardinal(..., default_q(x, base_rstr, body)
# @Predication(vocabulary, names=[])
# def card_variable_set_incoming(state, c_count, e_introduced_binding, x_target_binding, h_rstr, h_body):
#     c_count_value = int(c_count)
#     this_predicate_index = execution_context().current_predication_index()
#     parent_variable_set_cache = get_parent_variable_set_cache(x_target_binding.variable.name)
#
#     new_parent_variable_set = this_predicate_index not in parent_variable_set_cache["ChildCardinals"]
#     parent_variable_set_next_solution = "NextSolution" in parent_variable_set_cache and parent_variable_set_cache["NextSolution"] is True
#     if new_parent_variable_set or parent_variable_set_next_solution:
#         yield from cardinal_variable_set_incoming_next_this_cardinal_group(this_predicate_index, state, h_body,
#                                                                            new_parent_variable_set, parent_variable_set_next_solution, parent_variable_set_cache,
#                                                                            x_target_binding.variable.name, h_rstr, c_count_value)
#
#     else:
#         # Continue going through the parent_variable_set: this is the next item in the set
#         # We need to use the same this_cardinal_group that we used for the other elements of the set
#         # and try it on this_cardinal_group
#         if "CurrentCardinalGroup" not in parent_variable_set_cache["ChildCardinals"][this_predicate_index]:
#             # This means that we ran out of this cardinal groups, but something between the previous cardinal
#             # group and this one is trying alternatives.  They should just all fail
#             return
#
#         this_cardinal_group = parent_variable_set_cache["ChildCardinals"][this_predicate_index]["CurrentCardinalGroup"]
#         cardinal_logger.debug(f'Pred:{this_predicate_index}, CrdGrpID:{this_cardinal_group.cardinal_group_id} -> cached Cardinal Group -> {this_cardinal_group.cardinal_group_items}')
#
#         cardinal_group_solutions = cardinal_group_outgoing_solutions(this_predicate_index, state, x_target_binding.variable.name, h_body, this_cardinal_group)
#         if len(cardinal_group_solutions) == 0:
#             # This cardinal group didn't work. Because we've already worked through at least one item in the
#             # parent_variable_set, we can't just immediately try another this_cardinal_group
#             # Instead, ask the parent to variable_set_restart so it will start from the beginning of its variable_set
#             # and we can find a new this_cardinal_group but where we left off in the generator
#             cardinal_logger.debug(f'Pred:{this_predicate_index}, CrdGrpID:{this_cardinal_group.cardinal_group_id} -> VariableSetRestart: FAIL Cardinal Group -> {this_cardinal_group.cardinal_group_items}')
#             parent_variable_set_cache["NextSolution"] = True
#             raise VariableSetRestart
#
#         else:
#             yield from yield_all_cardinal_group_solutions(this_predicate_index, this_cardinal_group.cardinal_group_id, cardinal_group_solutions)


def rstr_reorderable(rstr):
    return isinstance(rstr, TreePredication) and rstr.name in ["place_n", "thing"]


@Predication(vocabulary, names=["which_q", "_which_q"])
def which_q(state, x_variable_binding, h_rstr, h_body):
    yield from default_quantifier(state, x_variable_binding, h_rstr, h_body, reverse=rstr_reorderable(h_rstr))


@Predication(vocabulary, names=["which_q_cardinal", "_which_q_cardinal"])
def which_q_cardinal(state, x_variable_binding, h_rstr, h_body):
    yield from default_quantifier_cardinal(state, x_variable_binding, h_rstr, h_body, reverse=rstr_reorderable(h_rstr))


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


# Needed for "together, which 3 files are 3 mb?"
@Predication(vocabulary, names=["_together_p"])
def together_p_ee(state, e_introduced_binding, e_target_binding):
    yield from together_p_state(state, e_introduced_binding, e_target_binding)


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


# handles size only
# loc_nonsp will add up the size of files if a collective set of actors comes in, so declare that as handling them differently
# we treat megabytes as a group, all added up, which is different than separately (a megabyte as a time) so ditto
@Predication(vocabulary, names=["loc_nonsp"], arguments=[DeclareArg("e"), DeclareArg("x", collective_behavior=CollectiveBehavior.different), DeclareArg("x", collective_behavior=CollectiveBehavior.different)])
def loc_nonsp_size(state, e_introduced_binding, x_actor_binding, x_size_binding):
    if x_actor_binding.value is not None:
        if x_size_binding.value is not None:
            if isinstance(x_size_binding.value, Measurement):
                # asking to see if actor "is" a measurement, as in "is file 5 mb"
                if hasattr(x_actor_binding.value, "size_measurement"):
                    if not x_size_binding.variable.is_collective:
                        # we only deal with x megabytes as coll because dist(10 mb) is 1 mb and nobody means 10 individual megabyte when they say "2 files are 10mb"
                        report_error(["formNotUnderstood", "missing", "collective"])
                        return

                    state = state.set_x(x_size_binding.variable.name, x_size_binding.value,
                                        used_collective=True)

                    # Only works if actor has a measurement
                    if x_actor_binding.variable.is_collective:
                        # Collective: We need to see if all of the variables in this variable set add up to the value
                        # For simplicity, assume all measurements are in megabytes
                        x_actor_variable_set_items = x_actor_binding.variable.variable_set_items
                        total = 0
                        for item in x_actor_variable_set_items:
                            total += item.size_measurement().count

                        if x_size_binding.value.count == total:
                            yield state.set_x(x_actor_binding.variable.name, x_actor_binding.value,
                                              used_collective=True)

                        else:
                            report_error(["xIsNotY", x_actor_binding.variable.name, x_size_binding.variable.name])
                            return

                    else:
                        # Distributive: each one must be this value
                        if x_size_binding.value == x_actor_binding.value.size_measurement():
                            yield state

                        else:
                            report_error(["xIsNotY", x_actor_binding.variable.name, x_size_binding.variable.name])
                            return

    else:
        # For now, return errors for cases where x_actor is unbound
        pass


# Just handles place locations
@Predication(vocabulary, names=["loc_nonsp"])
def loc_nonsp_place(state, e_introduced_binding, x_actor_binding, x_location_binding):
    if x_actor_binding.value is not None:
        if x_location_binding.value is not None:
            if hasattr(x_actor_binding.value, "all_locations"):
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
            report_error(["xIsNotYValue", x_binding.variable.name, "file"])


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
            report_error(["xIsNotYValue", x_binding.variable.name, "folder"])


pipeline_logger = logging.getLogger('Pipeline')
cardinal_logger = logging.getLogger('Cardinal')
