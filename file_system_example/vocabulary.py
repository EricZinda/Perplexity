import copy
import enum
import itertools
import logging
from file_system_example.objects import File, Folder, Actor, Container, QuotedText
from file_system_example.state import DeleteOperation, ChangeDirectoryOperation, CopyOperation
from perplexity.cardinals import split_cardinal_rstr
from perplexity.utilities import at_least_one_generator
from perplexity.variable_binding import VariableBinding
from perplexity.execution import call, report_error, execution_context, call_with_group, group_context, \
    create_solution_id, create_variable_set_cache, VariableSetRestart
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


class CardinalGroup(object):
    def __init__(self, is_collective, cardinal_group_id, cardinal_group_items):
        self.is_collective = is_collective
        self.cardinal_group_id = cardinal_group_id
        self.cardinal_group_items = cardinal_group_items


def create_cardinal_group_generator(state, is_collective, variable_name, h_rstr, count):
    def binding_from_call():
        for rstr_state in call(state, h_rstr):
            yield rstr_state.get_binding(variable_name).value

    def next_cardinal_group():
        for cardinal_group_elements in itertools.combinations(binding_from_call(), count):
            if is_collective:
                yield CardinalGroup(is_collective, create_solution_id(), [tuple([str(create_solution_id()), cardinal_group_elements])])
            else:
                yield CardinalGroup(is_collective, create_solution_id(), [tuple([str(create_solution_id()), [element]]) for element in cardinal_group_elements])

    yield from next_cardinal_group()


def yield_all_cardinal_group_solutions(this_predicate_index, cardinal_group_id, cardinal_group_solutions):
    cardinal_logger.debug(f'Pred:{this_predicate_index}, CrdGrpID:{cardinal_group_id} -> SUCC: start returning all answers')

    count = 0
    for variable_set_coll_or_dist_solutions in cardinal_group_solutions:
        for variable_set_solution_alternatives in variable_set_coll_or_dist_solutions:
            for variable_set_item_solutions in variable_set_solution_alternatives:
                for variable_set_item_solution_alternatives in variable_set_item_solutions:
                    for variable_set_item_solution_alternative in variable_set_item_solution_alternatives:
                        count += 1
                        yield variable_set_item_solution_alternative

    cardinal_logger.debug(f'Pred:{this_predicate_index}, CrdGrpID:{cardinal_group_id} -> SUCC: stop returning all answers: {count}')


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


# Get the next this_cardinal_group because we have a new parent variable_set OR
# Because the parent asked us to to get alternative answers OR
# Because the current cardinal group didn't work for the parent_variable_set and we threw an
#   exception asking to start the set over so we can try another
def cardinal_variable_set_incoming_next_this_cardinal_group(this_predicate_index, state, h_body,
                                                            new_parent_variable_set, parent_variable_set_next_solution, parent_variable_set_cache,
                                                            variable_name, h_rstr, c_count_value):
    if new_parent_variable_set:
        # Create a new cardinal group generator that matches coll or dist
        # Cache it so we can use it next time. This must be set even if we fail so that
        # parents know there are child cardinals
        cardinal_group_generator = create_cardinal_group_generator(state, parent_variable_set_cache["ChildIsCollective"], variable_name, h_rstr, c_count_value)
        parent_variable_set_cache["ChildCardinals"][this_predicate_index] = {}
        parent_variable_set_cache["ChildCardinals"][this_predicate_index]["CardinalGroupGenerator"] = cardinal_group_generator

    else:
        assert parent_variable_set_next_solution
        # Use the existing cached generator
        # Set parent_variable_set_next_solution = False so we don't do it again
        cardinal_group_generator = parent_variable_set_cache["ChildCardinals"][this_predicate_index]["CardinalGroupGenerator"]
        parent_variable_set_cache["NextSolution"] = False

    # Find one this_cardinal_group solution that works,
    # Then, subsequent calls will try it on other elements of the
    # parent variable_set
    cardinal_group_solutions = []
    while len(cardinal_group_solutions) == 0:
        try:
            this_cardinal_group = next(cardinal_group_generator)
            cardinal_logger.debug(f'Pred:{this_predicate_index}, CrdGrpID:{this_cardinal_group.cardinal_group_id} -> [{"New parent variable set" if new_parent_variable_set else "Next solution"}] New {"coll" if this_cardinal_group.is_collective else "dist"} Cardinal Group -> {this_cardinal_group.cardinal_group_items}')

        except StopIteration:
            cardinal_logger.debug(f'Pred:{this_predicate_index}, -> FAIL, No more cardinal groups available')
            return

        # Get the solutions to it
        cardinal_group_solutions = cardinal_group_outgoing_solutions(this_predicate_index, state, variable_name, h_body, this_cardinal_group)
        if len(cardinal_group_solutions) == 0:
            # This cardinal group didn't work, try the next one
            continue

        else:
            # This cardinal group worked, cache it so we can try against other items in the parent_variable_set
            # and return all the answers
            parent_variable_set_cache["ChildCardinals"][this_predicate_index]["CurrentCardinalGroup"] = this_cardinal_group
            yield from yield_all_cardinal_group_solutions(this_predicate_index, this_cardinal_group.cardinal_group_id, cardinal_group_solutions)


# Get all solutions for the entire this_cardinal_group
# The whole cardinal group must work or it fails
def cardinal_group_outgoing_solutions(this_predicate_index, state, variable_name, h_body, this_cardinal_group):
    cardinal_group_solutions = []
    cardinal_logger.debug(f'Pred:{this_predicate_index}, CrdGrpID:{this_cardinal_group.cardinal_group_id} -> Checking Cardinal Group: {this_cardinal_group.cardinal_group_items}')

    for variable_set_info in this_cardinal_group.cardinal_group_items:
        variable_set_id = variable_set_info[0]
        variable_set_coll_or_dist_solutions = []

        # Try the child in both coll and dist mode
        for is_child_collective in [False, True]:
            # Create a this_variable_set_cache to represent the variable_set
            this_variable_set_cache = create_variable_set_cache(variable_set_id, is_child_collective)
            has_child_cardinals, variable_set_solution_alternatives = cardinal_variable_set_outgoing_solutions(this_predicate_index, state, variable_name, h_body,
                                                                                                               this_cardinal_group,
                                                                                                               this_variable_set_cache, variable_set_info)
            if len(variable_set_solution_alternatives) > 0:
                variable_set_coll_or_dist_solutions.append(variable_set_solution_alternatives)

            # If there are not child cardinals, trying the other mode will just give duplicate answers
            if not has_child_cardinals:
                break

        if len(variable_set_coll_or_dist_solutions) == 0:
            # There were no coll or dist solutions:
            # fail since all variable sets in a cardinal group must succeed (in coll or dist mode)
            # for the cardinal to succeed
            cardinal_logger.debug(f'Pred:{this_predicate_index}, CrdGrpID:{this_cardinal_group.cardinal_group_id} -> FAIL Cardinal Group since variable set FAIL {variable_set_info}')
            return []

        else:
            cardinal_group_solutions.append(variable_set_coll_or_dist_solutions)

    cardinal_logger.debug(f'Pred:{this_predicate_index}, CrdGrpID:{this_cardinal_group.cardinal_group_id} -> SUCC Cardinal Group {this_cardinal_group.cardinal_group_items}')
    return cardinal_group_solutions


# Get all alternative solutions to a particular outgoing variable_set
def cardinal_variable_set_outgoing_solutions(this_predicate_index, state, variable_name, h_body, this_cardinal_group, this_variable_set_cache, variable_set_info):
    variable_set = variable_set_info[1]

    # There could be multiple solutions to this whole set
    variable_set_solution_alternatives = []
    find_next_solution_to_variable_set = True
    has_child_cardinals = False
    while find_next_solution_to_variable_set:
        # Will contain a list, where each element is solutions to one
        # variable set item
        variable_set_item_solutions = []
        for variable_set_item_index in range(0, len(variable_set)):
            # Find a solution for this variable set in the cardinal group
            variable_set_item = variable_set[variable_set_item_index]

            cardinal_logger.debug(f'Pred:{this_predicate_index}, CrdGrpID:{this_cardinal_group.cardinal_group_id}, VarSetID: {this_variable_set_cache["VariableSetID"]} -> {"[Next solution] " if "NextSolution" in this_variable_set_cache and this_variable_set_cache["NextSolution"] else ""}Checking variable set item: {variable_set_item}')
            new_state = state.set_x(variable_name, variable_set_item, this_cardinal_group.cardinal_group_id,
                                    this_variable_set_cache["VariableSetID"], variable_set_item_index, this_cardinal_group.is_collective)
            try:
                variable_set_item_solution_alternatives = []
                for variable_set_item_solution in call_with_group(this_variable_set_cache, new_state, h_body):
                    variable_set_item_solution_alternatives.append(variable_set_item_solution)

                # Even if it fails, this gets set in children
                if len(this_variable_set_cache["ChildCardinals"]) > 0:
                    has_child_cardinals = True

            except VariableSetRestart:
                # A child asked us to retry which means a child had a variable_set that didn't completely work against this set
                # So: the alternatives we have so far are right, but we need to restart the variable set (this keeps the same group to allow the child to cache things there)
                cardinal_logger.debug(f'Pred:{this_predicate_index}, CrdGrpID:{this_cardinal_group.cardinal_group_id} -> Child requested VariableSetRestart')
                this_variable_set_cache["NextSolution"] = True
                break

            # if there were no solutions to this variable set item,
            # then there are no more alternatives
            if len(variable_set_item_solution_alternatives) == 0:
                find_next_solution_to_variable_set = False
                cardinal_logger.debug(f'Pred:{this_predicate_index}, CrdGrpID:{this_cardinal_group.cardinal_group_id}, VarSetID: {this_variable_set_cache["VariableSetID"]} -> FAIL Variable Set Item: {variable_set_item}')
                break

            else:
                cardinal_logger.debug(f'Pred:{this_predicate_index}, CrdGrpID:{this_cardinal_group.cardinal_group_id}, VarSetID: {this_variable_set_cache["VariableSetID"]} -> SUCC Variable Set Item: {variable_set_item}')
                variable_set_item_solutions.append(variable_set_item_solution_alternatives)

        # If variable_set_item_solutions == len(variable_set),
        # We have at least one solution that worked for all
        # the items in the variable set, so we have success for this variable set
        if len(variable_set_item_solutions) == len(variable_set):
            cardinal_logger.debug(f'Pred:{this_predicate_index}, CrdGrpID:{this_cardinal_group.cardinal_group_id}, VarSetID: {this_variable_set_cache["VariableSetID"]} -> SUCC Variable Set Alternative: {variable_set}')
            variable_set_solution_alternatives.append(variable_set_item_solutions)
        else:
            cardinal_logger.debug(f'Pred:{this_predicate_index}, CrdGrpID:{this_cardinal_group.cardinal_group_id}, VarSetID: {this_variable_set_cache["VariableSetID"]} -> FAIL Variable Set Alternative: {variable_set}')

        # If there are not cardinal children, there can't be more alternatives
        if not has_child_cardinals:
            cardinal_logger.debug(f'Pred:{this_predicate_index}, CrdGrpID:{this_cardinal_group.cardinal_group_id}, VarSetID: {this_variable_set_cache["VariableSetID"]} -> [No child cardinals] Stop checking Variable Set alternatives: {variable_set}')
            find_next_solution_to_variable_set = False

        else:
            # Tell the child cardinals to give us the next solution for this variable set
            cardinal_logger.debug(f'Pred:{this_predicate_index}, CrdGrpID:{this_cardinal_group.cardinal_group_id}, VarSetID: {this_variable_set_cache["VariableSetID"]} -> Check Variable Set alternatives: {variable_set}')
            this_variable_set_cache["NextSolution"] = True

    if len(variable_set_solution_alternatives) > 0:
        cardinal_logger.debug(f'Pred:{this_predicate_index}, CrdGrpID:{this_cardinal_group.cardinal_group_id}, VarSetID: {this_variable_set_cache["VariableSetID"]} -> SUCC Variable Set: variable set had at least one solution: {variable_set}')
    else:
        cardinal_logger.debug(f'Pred:{this_predicate_index}, CrdGrpID:{this_cardinal_group.cardinal_group_id}, VarSetID: {this_variable_set_cache["VariableSetID"]} -> FAIL Variable Set: variable set had no solutions: {variable_set}')

    return has_child_cardinals, variable_set_solution_alternatives


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


# Rewrite the cardinal to a form that takes scope
# Rewrite: quantifier_q(x, [cardinal(x, ...), cardinal_modifier()], body)
# To the form: [cardinal_modifier(), cardinal_with_scope(x, non_cardinal_rstr, base_quantifier_q(x, thing(x), body)]
# TODO: If we are rewriting the tree the error reporting will get messed up
#       We need to properly rewrite the tree and put the new form in state?
@Predication(vocabulary, names=["pronoun_q", "proper_q", "udef_q"])
def default_quantifier(state, x_variable_binding, h_rstr, h_body, reverse=False):
    cardinal_predication, cardinal_modifiers, non_cardinal_rstr = split_cardinal_rstr(h_rstr)
    if cardinal_predication is None:
        # Not a cardinal
        yield from default_quantifier_base(state, x_variable_binding, h_rstr, h_body, reverse)

    else:
        this_predication_index = execution_context().current_predication_index()
        this_predication = predication_from_index(state.get_binding("tree").value, this_predication_index)
        thing_predication = TreePredication(this_predication_index, "thing", [x_variable_binding.variable.name], ["ARG0"])

        base_quantifier = TreePredication(this_predication_index, "base_q", [this_predication.args[0], thing_predication, h_body], this_predication.arg_names)
        cardinal_predication.append_arg("RSTR", non_cardinal_rstr)
        cardinal_predication.append_arg("BODY", base_quantifier)

        yield from call(state, cardinal_modifiers + [cardinal_predication])


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
