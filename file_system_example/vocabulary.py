import copy
import enum
import itertools
import logging
from file_system_example.objects import File, Folder, Actor, Container, QuotedText
from file_system_example.state import DeleteOperation, ChangeDirectoryOperation, CopyOperation
from perplexity.cardinals import split_cardinal_rstr
from perplexity.utilities import at_least_one_generator
from perplexity.variable_binding import VariableBinding
from perplexity.execution import call, report_error, execution_context, call_with_group, group_context, create_cardinal_set, \
    RetrySetException, create_solution_id
from perplexity.tree import TreePredication, is_this_last_fw_seq, find_predications_using_variable_ARG1, \
    predication_from_index
from perplexity.virtual_arguments import scopal_argument
from perplexity.vocabulary import Vocabulary, Predication, EventOption

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


# Contract of aggregate adjective is fail immediately if the aggregate isn't true
# otherwise iteratively return the answers
@Predication(vocabulary)
def card(state, c_count, e_introduced_binding, x_target_binding):
    pass


def create_combinator(state, variable_name, h_rstr, count):
    def binding_from_call():
        for rstr_state in call(state, h_rstr):
            yield rstr_state.get_binding(variable_name).value

    return itertools.combinations(binding_from_call(), count)


# rewrite: default_q(x, [cardinal(x, ...), other()], body)
# to: cardinal(x, [other()], default_q(x, thing(x), body)
# to: cardinal(..., default_q(x, base_rstr, body)
@Predication(vocabulary)
def card_with_scope(state, c_count, e_introduced_binding, x_target_binding, h_rstr, h_body):
    c_count_value = int(c_count)
    this_predicate_index = execution_context().current_predication_index()

    # Get the current cardinal group (we only care about the closest group)
    # This defines the boundaries of the set we are operating against
    # And changes when we have a new set from the parent
    # It will also tell us what mode we should be operating in
    parent_group = group_context()

    has_child_cardinals = False
    for child_is_collective in [False]:
        has_current_set = this_predicate_index in parent_group["ChildCardinals"] and parent_group["ChildCardinals"][this_predicate_index]["CurrentSet"] is not None
        next_solution_for_parent_set = "NextSolution" in parent_group and parent_group["NextSolution"] is True
        if has_current_set and next_solution_for_parent_set:
            # The parent is asking us to find another set that works with its current set
            # Clear out our current one so we get a new one
            has_current_set = False
            parent_group["ChildCardinals"][this_predicate_index]["CurrentSet"] = None
            cardinal_logger.debug(f'CardinalID:{parent_group["CardinalID"]}, coll:{parent_group["ChildIsCollective"]}, Predicate:{this_predicate_index} -> Parent requested next solution')

        if has_current_set:
            # We have already found and stashed a set of solutions for this
            # parent group. See if they still apply to this item
            this_card_info = parent_group["ChildCardinals"][this_predicate_index]
            cardinal_logger.debug(f'SolutionID:{this_card_info["SolutionID"]}, CardinalID:{parent_group["CardinalID"]}, coll:{parent_group["ChildIsCollective"]}, Predicate:{this_predicate_index} -> Test existing set: {this_card_info["CurrentSet"]}')
            has_child_cardinals, subset_solutions_list_list = card_apply_set(state, child_is_collective, parent_group["ChildIsCollective"], this_card_info["SolutionID"], parent_group["CardinalID"], x_target_binding.variable.name, this_card_info["CurrentSet"], h_body)

            if len(subset_solutions_list_list) == 0:
                # The existing set did not ALL work for the new item
                # Set our set to None so we find a new set
                parent_group["ChildCardinals"][this_predicate_index]["CurrentSet"] = None

                # and throw an exception to make the caller retry each one from the beginning with the current rstr_generator
                # and the set that worked
                raise RetrySetException()

            else:
                # This set worked again for this body
                for subset_solutions_list in subset_solutions_list_list:
                    for subset_solutions in subset_solutions_list:
                        for subset_solution in subset_solutions:
                            for solution in subset_solution:
                                yield solution

        else:
            # Find the next, or first, set for this cardinal and see if it works in the binding
            # Since this is a new solution, create a new solution id
            solution_id = create_solution_id()
            if this_predicate_index in parent_group["ChildCardinals"] and "Combinator" in parent_group["ChildCardinals"][this_predicate_index]:
                log_message = "Next set"
                this_card_info = parent_group["ChildCardinals"][this_predicate_index]
                combinator = parent_group["ChildCardinals"][this_predicate_index]["Combinator"]

            else:
                log_message = "First set"
                this_card_info = dict()
                parent_group["ChildCardinals"][this_predicate_index] = this_card_info

                # Create a new combinator to return all combinations of items from this rstr
                combinator = create_combinator(state, x_target_binding.variable.name, h_rstr, c_count_value)
                parent_group["ChildCardinals"][this_predicate_index]["Combinator"] = combinator

            cardinal_logger.debug(f'SolutionID:{solution_id}, CardinalID:{parent_group["CardinalID"]}, coll:{parent_group["ChildIsCollective"]}, Predicate:{this_predicate_index} -> {log_message}')

            # Find one solution set that works for this body
            while True:
                try:
                    binding_set = next(combinator)
                    cardinal_logger.debug(f'SolutionID:{solution_id}, CardinalID:{parent_group["CardinalID"]}, coll:{parent_group["ChildIsCollective"]}, Predicate:{this_predicate_index} -> Check new set: {binding_set}')

                except StopIteration:
                    # No more sets available, fail
                    cardinal_logger.debug(f'SolutionID:{solution_id}, CardinalID:{parent_group["CardinalID"]}, coll:{parent_group["ChildIsCollective"]}, Predicate:{this_predicate_index} -> No more sets available, fail')
                    return

                has_child_cardinals, subset_solutions_list_list = card_apply_set(state, child_is_collective, parent_group["ChildIsCollective"], solution_id, parent_group["CardinalID"], x_target_binding.variable.name, binding_set, h_body)

                if len(subset_solutions_list_list) > 0:
                    # We found a set that works for this item
                    # set our set to this one
                    this_card_info["CurrentSet"] = binding_set
                    this_card_info["SolutionID"] = solution_id

                    for subset_solutions_list in subset_solutions_list_list:
                        for subset_solutions in subset_solutions_list:
                            for subset_solution in subset_solutions:
                                for solution in subset_solution:
                                    yield solution

                    break

        # If there are no child cardinals don't do dist and coll alternatives because it
        # creates invalid duplicates
        if not has_child_cardinals:
            break


# Find one set of answers to the set passed in
def card_apply_set(state, child_is_collective, is_collective, solution_id, cardinal_id, variable_name, initial_set_values, h_body):
    if is_collective:
        # If we are collective, there is one subset that contains N items
        subsets = [initial_set_values]
    else:
        # If we are distributive, there are N subsets of 1 item
        subsets = [[item] for item in initial_set_values]

    # Make sure all the subsets succeed
    # This collects a list of solutions for every subset
    # If we succeed it should have the same number of items as we do subsets
    subset_solutions_list_list = []
    has_child_cardinals = False
    for subsets_index in range(0, len(subsets)):
        # This is the list of solutions for this subset
        subset_solutions_list = []
        subset_values = subsets[subsets_index]

        # We are sending all items in this subset to any children in the body
        # So, let the child know they will be operating against a set of items
        # by creating a group. Also tell them if they, themselves, should be coll or dist
        # Each subset gets its own cardinalID to indicate it is a unique set
        group = create_cardinal_set(child_is_collective)

        # We need to find all the answers for this subset, there may be more than one
        find_next_solution = True
        while find_next_solution:
            find_next_solution = False
            cardinal_logger.debug(f'SolutionID:{solution_id}, CardinalID:{cardinal_id}, coll:{is_collective}, Predicate:{execution_context().current_predication_index()} -> Find next solution for {subset_values}')

            # Allow a child to ask for a restart to find an alternative
            restart_once = True
            while restart_once:
                restart_once = False

                # See if all items in the subset work in the body
                subset_solutions = []
                for subset_values_index in range(0, len(subset_values)):
                    binding_value = subset_values[subset_values_index]
                    if is_collective:
                        cardinal_item_id = subset_values_index
                    else:
                        cardinal_item_id = subsets_index
                    body_states = []
                    cardinal_logger.debug(f'SolutionID:{solution_id}, CardinalID:{cardinal_id}, coll:{is_collective}, Predicate:{execution_context().current_predication_index()} -> Checking: {variable_name}={binding_value}')
                    new_state = state.set_x(variable_name, binding_value, solution_id, cardinal_id, cardinal_item_id, is_collective)
                    try:
                        for body_state in call_with_group(group, new_state, h_body):
                            body_states.append(body_state)

                    except RetrySetException:
                        # One of the children wants us to do the loop again *with the same items* so they
                        # can try new values
                        restart_once = True
                        cardinal_logger.debug(f'SolutionID:{solution_id}, CardinalID:{cardinal_id}, coll:{is_collective}, Predicate:{execution_context().current_predication_index()} -> Child requested retry of {subset_values}')
                        break

                    if len(group["ChildCardinals"]) > 0:
                        has_child_cardinals = True

                    if len(body_states) > 0:
                        # This item (binding_value) from the subset worked in the body
                        subset_solutions.append(body_states)

                    else:
                        # This item did not work, and unless they all work, things fail
                        # so: fail this *solution* (there may be others for this set that did work)
                        subset_solutions = []
                        cardinal_logger.debug(f'SolutionID:{solution_id}, CardinalID:{cardinal_id}, coll:{is_collective}, Predicate:{execution_context().current_predication_index()} -> Subset item {binding_value} failed, subset fails: {subset_values}')
                        if solution_id == 1 and cardinal_id == "1":
                            print("ere")
                        break

                    group["NextSolution"] = False

                if restart_once:
                    continue

                if len(subset_solutions) > 0:
                    # All items in this subset worked in the body
                    # Continue and make sure the other subsets do too
                    cardinal_logger.debug(
                        f'SolutionID:{solution_id}, CardinalID:{cardinal_id}, coll:{is_collective}, Predicate:{execution_context().current_predication_index()} -> Subset succeeded: {subset_values}')
                    subset_solutions_list.append(subset_solutions)
                    if has_child_cardinals:
                        find_next_solution = True
                        group["NextSolution"] = True

        # Collect all of the solutions for this subset
        if len(subset_solutions_list) > 0:
            subset_solutions_list_list.append(subset_solutions_list)

    if len(subset_solutions_list_list) == len(subsets):
        # All items in all subsets worked
        cardinal_logger.debug(f'SolutionID:{solution_id}, CardinalID:{cardinal_id}, coll:{is_collective}, Predicate:{execution_context().current_predication_index()} -> Set succeeded: {initial_set_values}')
        return has_child_cardinals, subset_solutions_list_list

    else:
        cardinal_logger.debug(f'SolutionID:{solution_id}, CardinalID:{cardinal_id}, coll:{is_collective}, Predicate:{execution_context().current_predication_index()} -> Set failed: {initial_set_values}')
        return has_child_cardinals, []
#
# # rewrite: default_q(x, [cardinal(x, ...), other()], body)
# # to: cardinal(x, [other()], default_q(x, thing(x), body)
# # to: cardinal(..., default_q(x, base_rstr, body)
# @Predication(vocabulary)
# def card_with_scope(state, c_count, e_introduced_binding, x_target_binding, h_rstr, h_body):
#     c_count_value = int(c_count)
#     this_predicate_index = execution_context().current_predication_index()
#
#     # Get the current group (we only care about the closest group)
#     # This defines the set we are operating against
#     # It will also tell us what mode we should be operating in
#     parent_group = group_context()
#     this_is_collective = parent_group["Collective"]
#
#     # If there are no child cardinals don't do two alternatives because it
#     # creates invalid duplicates
#     has_child_cardinals = False
#
#     # Start with false so that we always do distributive mode since
#     # that is the default the predicates will implement
#     for child_is_collective in [True]: #[False, True]:
#         if this_predicate_index in parent_group["ChildCardinals"]:
#             # We have already found and stashed a set of solutions for this
#             # parent group. See if they still apply to this item
#             this_card_info = parent_group["ChildCardinals"][this_predicate_index]
#
#             cardinal_logger.debug(f"Parent_Cardinal_ID={parent_group['GroupID']} Child Predicate={this_predicate_index}, SolutionID={this_card_info['SolutionID']}, Collective={parent_group['Collective']}: Start, cache: {this_card_info['GroupItems']}")
#
#             has_child_cardinals, working_values, solution_sets, groups = card_from_rstr_generator(this_card_info["SolutionID"], this_is_collective, child_is_collective, c_count_value, x_target_binding, this_card_info["GroupItems"], state, this_card_info["RstrGenerator"], h_body)
#
#             if working_values is None:
#                 # There were no more items in the rstr, fail
#                 cardinal_logger.debug(
#                     f"Parent_Cardinal_ID={parent_group['GroupID']} Child Predicate={this_predicate_index}, SolutionID={this_card_info['SolutionID']}, Collective={parent_group['Collective']}: Fail, no more items")
#                 return
#
#             elif solution_sets is None:
#                 # The existing values set did not ALL work for the new item
#                 # We need to generate a new set that works for the past ones and the new one
#                 # We know the current set worked for all the old ones
#                 # and the new one failed at a certain one, so:
#                 # set this_group["GroupItems"] to the set that did work
#                 # and throw an exception to make the caller retry each one from the beginning with the current rstr_generator
#                 # and the set that worked
#                 this_card_info["GroupItems"] = working_values
#                 cardinal_logger.debug(
#                     f"Parent_Cardinal_ID={parent_group['GroupID']} Child Predicate={this_predicate_index}, SolutionID={this_card_info['SolutionID']}, Collective={parent_group['Collective']}: Restart, cache: {working_values}")
#
#                 raise RestartException()
#
#             else:
#                 # The existing values did ALL work for the new item, return them
#                 this_card_info["GroupItems"] = working_values
#                 cardinal_logger.debug(
#                     f"Parent_Cardinal_ID={parent_group['GroupID']} Child Predicate={this_predicate_index}, SolutionID={this_card_info['SolutionID']}, Collective={parent_group['Collective']}: All solutions worked with: {working_values}")
#
#                 for solution_set in solution_sets:
#                     for solution in solution_set:
#                         yield solution
#
#         else:
#             # Create the generator that will iteratively generate new RSTRs to try
#             # over subsequent calls to this cardinal
#             # RSTR doesn't need to be called with a group since cardinals will
#             # only be in the body
#             rstr_generator = call(state, h_rstr)
#
#             # each set of answers in coll or dist mode gets a different solutionid
#             # We get here when the parent is calling with a new group which means it is:
#             # - the first time we are being called for a solution when the parent is in in coll mode or
#             # - every time we are being called for a solution when the parent is in in dist mode
#             # This is a new solution
#             solution_id = create_solution_id()
#
#             cardinal_logger.debug(f"Parent_Cardinal_ID={parent_group['GroupID']} Child Predicate={this_predicate_index}, SolutionID={solution_id}, Collective={parent_group['Collective']}: Start, no cache")
#
#             # Get N solutions that apply to the state passed in
#             # Since this is a group we haven't seen, pass [] as the previous answers
#             has_child_cardinals, working_values, solution_sets, groups = card_from_rstr_generator(solution_id, this_is_collective, child_is_collective, c_count_value, x_target_binding, [], state, rstr_generator, h_body)
#             if working_values is None:
#                 cardinal_logger.debug(
#                     f"Parent_Cardinal_ID={parent_group['GroupID']} Child Predicate={this_predicate_index}, SolutionID={solution_id}, Collective={parent_group['Collective']}: Fail, no cache")
#
#                 # Couldn't find a set of N answers that applied in the whole dataset, no need to retry
#                 report_error(["cardNotFound", x_target_binding.variable.name, c_count_value, len(working_values) if working_values is not None else 0])
#
#             else:
#                 cardinal_logger.debug(
#                     f"Parent_Cardinal_ID={parent_group['GroupID']} Child Predicate={this_predicate_index}, SolutionID={solution_id}, Collective={parent_group['Collective']}: Success, cache: {working_values}")
#
#                 # Create a dict that remembers what we found that we can reuse next time
#                 this_card_info = dict()
#                 parent_group["ChildCardinals"][this_predicate_index] = this_card_info
#
#                 # rstr_generator contains an iterator that will give us more options if we need them, store that
#                 this_card_info["RstrGenerator"] = rstr_generator
#                 this_card_info["GroupItems"] = working_values
#                 this_card_info["SolutionID"] = solution_id
#                 for solution_set in solution_sets:
#                     for solution in solution_set:
#                         yield solution
#
#         # If there wasn't a child cardinal, don't try distributive mode
#         if not has_child_cardinals:
#             break
#
#
# # Confirms that existing_values_orig set of values that have already worked also work against
# # the value that just came in.  If existing_values_orig is not enough for this cardinal, finds new
# # ones and tests them
# # Will return when either we have been successful for this cardinal's whole set or failed
# def card_from_rstr_generator(solution_id, this_is_collective, child_is_collective, c_count_value, x_target_binding, existing_values_orig, state, rstr_generator, h_body):
#     restart_once = True
#     groups = []
#     has_child_cardinals = False
#
#     throw_if_not_match_existing = this_is_collective and len(existing_values_orig) == c_count_value
#
#     # The loop only goes again IF we get a restart exception
#     group = create_group(child_is_collective)
#     existing_values = copy.copy(existing_values_orig)
#     rstr_done = False
#     while restart_once:
#         # This loop needs to find a set of c_count_value x_target_binding items that meet the body
#         # It can get restarted if a child set didn't work
#         restart_once = False
#         solution_sets = []
#         new_values = []
#         if group["GroupID"] == "35:49":
#             print("here")
#
#         while True:
#             # This loop is iteratively building up a set of c_count_value x_target_binding items
#             # binding_value will hold the next rstr_item to try (which might be one we already tried)
#             if len(existing_values) > 0:
#                 binding_value = existing_values[0]
#                 existing_values.pop(0)
#                 rstr_state = state
#                 cardinal_logger.debug(
#                     f"SolutionID={solution_id}, coll={this_is_collective}: From cache: {x_target_binding.variable.name}={binding_value}")
#
#             else:
#                 if throw_if_not_match_existing:
#                     return has_child_cardinals, new_values, None, groups
#
#                 try:
#                     rstr_state = next(rstr_generator)
#
#                 except StopIteration:
#                     # We went through all the possible rstr values for this set,
#                     # time to end
#                     rstr_done = True
#                     break
#
#                 binding_value = rstr_state.get_binding(x_target_binding.variable.name).value
#                 cardinal_logger.debug(
#                     f"SolutionID={solution_id}, coll={this_is_collective}: From rstr: {x_target_binding.variable.name}={binding_value}")
#
#             try:
#                 # We now have a binding_value to test for the target binding
#                 # See if it is a duplicate (because rstr returned the same item twice), in which case we should
#                 # ignore it
#                 duplicate = False
#                 for new_value in new_values:
#                     if new_value == binding_value:
#                         # We already have this one
#                         duplicate = True
#                         break
#
#                 if duplicate:
#                     break
#
#                 if not this_is_collective:
#                     group = create_group(child_is_collective)
#
#                 body_states = []
#                 new_state = state.set_x(x_target_binding.variable.name, binding_value, solution_id, group["GroupID"], len(new_values), this_is_collective)
#                 for body_state in call_with_group(group, new_state, h_body):
#                     body_states.append(body_state)
#
#                 if len(group["ChildCardinals"]) > 0:
#                     has_child_cardinals = True
#
#                 if len(body_states) > 0:
#                     cardinal_logger.debug(
#                         f"SolutionID={solution_id}, coll={this_is_collective}: {x_target_binding.variable.name}={binding_value}: Success")
#
#                     # This rstr item (binding_value) worked in the body
#                     groups.append(group)
#                     new_values.append(binding_value)
#                     solution_sets.append(body_states)
#                     if len(new_values) == c_count_value:
#                         # We now have solutions for all the items
#                         # in this set against the member of a parent set
#                         return has_child_cardinals, new_values, solution_sets, groups
#
#                 else:
#                     cardinal_logger.debug(
#                         f"SolutionID={solution_id}, coll={this_is_collective}: {x_target_binding.variable.name}={binding_value}: Fail")
#
#                     # This one didn't work, continue
#                     pass
#
#             except RestartException as error:
#                 # One of the children wants us to do the loop again *with the same items* so they
#                 # can try new values on the *existing* solutions
#                 # The "same items" are whatever is in new_values *plus* whatever is in binding_value
#                 # since that one wasn't yet added to new_values since it failed
#                 existing_values = new_values + [binding_value]
#                 cardinal_logger.debug(
#                     f"SolutionID={solution_id}, coll={this_is_collective}: {x_target_binding.variable.name}={binding_value}: Child requested restart, using values: {existing_values}")
#
#                 restart_once = True
#                 break
#
#     if rstr_done:
#         cardinal_logger.debug(
#             f"SolutionID={solution_id}, coll={this_is_collective}: Fail, no more values")
#
#         return None, None, None, None
#
#     else:
#         cardinal_logger.debug(
#             f"SolutionID={solution_id}, coll={this_is_collective}: Fail, more rstr values available")
#
#         return has_child_cardinals, new_values, None, groups


# Many quantifiers are simply markers and should use this as
# the default behavior
@Predication(vocabulary, names=["base_q"])
def default_quantifier_base(state, x_variable_binding, h_rstr_orig, h_body_orig, reverse=False):
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


# If we are rewriting the tree the error reporting will get messed up
# We need to properly rewrite the tree and put the new form in state?
# rewrite: default_q(x, [cardinal(x, ...), other()], body)
# to: cardinal(x, [other()], default_q(x, thing(x), body)
# to: cardinal(..., default_q(x, base_rstr, body)
@Predication(vocabulary, names=["pronoun_q", "proper_q", "udef_q"])
def default_quantifier(state, x_variable_binding, h_rstr, h_body, reverse=False):
    cardinal_predication, cardinal_rstr, base_rstr = split_cardinal_rstr(h_rstr)
    if cardinal_predication is None:
        yield from default_quantifier_base(state, x_variable_binding, h_rstr, h_body, reverse)

    else:
        # Convert to the form: cardinal(x, [base_rstr], quantifier_q(x, thing(x), body)
        this_predication_index = execution_context().current_predication_index()
        this_predication = predication_from_index(state.get_binding("tree").value, this_predication_index)
        thing_predication = TreePredication(this_predication_index, "thing", [x_variable_binding.variable.name], ["ARG0"])
        base_quantifier = TreePredication(this_predication_index, "base_q", [this_predication.args[0], thing_predication, h_body], this_predication.arg_names)
        cardinal_predication.append_arg("RSTR", base_rstr)
        cardinal_predication.append_arg("BODY", base_quantifier)

        yield from call(state, cardinal_predication)


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
        yield state.set_x_from_binding(x_binding, value)


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


@Predication(vocabulary, names=["_in_p_loc"])
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
cardinal_logger = logging.getLogger('Cardinal')
