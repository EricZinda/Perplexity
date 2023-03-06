import copy
import itertools
import logging
from perplexity.tree import find_predications_in_list, walk_tree_predications_until, split_predications_consuming_event
from perplexity.execution import create_variable_set_cache, call_with_group, VariableSetRestart, create_solution_id, \
    call


# Split a potential cardinal predicate into pieces:
#   new_cardinal: just the bare cardinal predication with "_with_scope" appended
#   cardinal_modifiers: a list of all the modifiers of the cardinal
#   remaining_predications: any terms that were not cardinal-impacting.  i.e. the "bare rstr".
#       If it is not a cardinal, just return all of term
def split_cardinal_rstr(term):
    # Get the list of all cardinal-impacting terms in term
    cardinal_impacting_terms = ["_a+few_a_1", "card", "ord", "much-many", "several"]
    cardinal_impacting_list = find_predications_in_list(term, cardinal_impacting_terms)

    if len(cardinal_impacting_list) > 0:
        # TODO: This assumes the cardinal is at position 0 which is wrong
        # Figure out if there are any modifiers modifying the cardinal itself
        # such as "only"
        cardinal_modifiers, remaining_predications = split_predications_consuming_event(term, cardinal_impacting_list[0].introduced_variable())

        new_cardinal = copy.deepcopy(cardinal_impacting_list[0])
        new_cardinal.name = new_cardinal.name + "_with_scope"

    else:
        new_cardinal = None
        cardinal_modifiers = []
        remaining_predications = term

    return new_cardinal, cardinal_modifiers, remaining_predications


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


# Prints the English for a single answer.Takes a list of cardinal groups
# Every cardinal group level needs to print at a new indent
# Even variableset needs to print on its own line at that indent
# They all need descriptors
# Need blanks between variable sets
# Stop recuring after we hit the cardinal that contains the variable we are looking for
def cardinal_answer_to_english(variable, cardinal_variables, cardinal_answer_list, indent_level=0):
    indent = " " * indent_level
    cardinal_group_answer = []
    for cardinal_group in cardinal_answer_list:
        # If this is coll, print on same line and say together
        type_description = " together" if cardinal_group["Type"] == "coll" else ""
        variable_set_answer = []
        for variable_set_info in cardinal_group["VariableSets"]:
            variable_set_items = [str(item) for item in variable_set_info["VariableSetItems"].values()]
            answer = indent + ", ".join(variable_set_items) + f'{type_description}\n'
            if len(variable_set_info["ChildGroups"]) > 0 and variable != cardinal_variables[0]:
                answer += cardinal_answer_to_english(variable, cardinal_variables[1:], variable_set_info["ChildGroups"],
                                                     indent_level + 5) + "\n"

            variable_set_answer.append(answer)
        cardinal_group_answer.append("".join(variable_set_answer))
    return ("\n" if cardinal_answer_list[0]["Type"] == "dist" else "").join(cardinal_group_answer)


# Convert the raw list of answers from a query to a list that groups them
# into answers that take into account variable sets.
# Returns each different cardinal-based answer
def cardinal_answer_list(solutions):
    # Get the order the cardinals were run in so we can build
    # the tree properly, then build it.
    cardinal_order = cardinal_tree(solutions, reverse=False)
    answer_tree = {"VariableOrder": cardinal_order}
    for solution in solutions:
        add_solution_to_tree(cardinal_order, answer_tree, solution)

    # Now pull apart individual answers from all the possible unique combinations
    # of collective and distributive cardinal answers

    # Only choose the collective version of solutions where one of the predications
    # actually paid attention
    coll_dist_options = [["dist"] for _ in range(0, len(cardinal_order))]
    for solution in solutions:
        for variable_index in range(0, len(cardinal_order)):
            if solution.get_binding(cardinal_order[variable_index]).variable.used_collective and len(coll_dist_options[variable_index]) == 1:
                coll_dist_options[variable_index].append("coll")

    # TODO: build this into a proper recursive algorithm and quit brute forcing it
    for variation in itertools.product(*coll_dist_options):
        answer = specific_coll_dist_variation(answer_tree, variation)
        if answer is not None:
            yield {"CardinalVariables": cardinal_order, "Answer": answer}


# First figure out the order of the "tree of cardinals" from child to parent
# The order of them is simply the number of ids that compose an individual answer_set_id
# Since these are built like 0:4:5.
# It won't change for the answers so we can just do it on the first one
# TODO: For now we are assuming it is a straight line, not a tree
def cardinal_tree(solutions, reverse=True):
    tree_info = solutions[0].get_binding("tree")
    variables = tree_info.value["Variables"]
    cardinal_list = []
    for variable_name in variables:
        binding = solutions[0].get_binding(variable_name)
        if binding.variable.variable_set_id is not None:
            cardinal_id_parts = binding.variable.variable_set_id.split(":")
            cardinal_list.append((len(cardinal_id_parts), variable_name))

    cardinal_list.sort(reverse=reverse)
    return [item[1] for item in cardinal_list]


# A parent sends a *variable set* to a child,
# and the child solves it against that child's *cardinal group*.
# So, as we consider each child as we recurse down the child chain,
# we group the whole child cardinal group since that whole child cardinal group (*not* the child variable set)
# is part of the answer for the parent *variable set*.
# I.e. solutions look like: cardinal group -> variable set -> cardinal group -> variable set
#
# Algorithm:
# Build a tree with the first cardinal at the root and the childmost cardinal at the leaves
#   Loop through the solutions and the variables in tree order
#       Put each variable in the right spot in the tree using the binding
#           information of the variable to know which
#           cardinal group/variable set/variable set item it is
def add_solution_to_tree(cardinal_order, answer_tree, solution):
    variable = cardinal_order[0]
    binding = solution.get_binding(variable)
    type_key = "coll" if binding.variable.is_collective else "dist"
    group_key = str(binding.variable.cardinal_group_id)
    variable_set_key = binding.variable.variable_set_id

    if type_key not in answer_tree:
        answer_tree[type_key] = {}

    if group_key not in answer_tree[type_key]:
        answer_tree[type_key][group_key] = {}

    if variable_set_key not in answer_tree[type_key][group_key]:
        answer_tree[type_key][group_key][variable_set_key] = {"ChildGroups": {}, "VariableSet": {}}

    # Use the variable_set_item_id to make sure we don't get duplicates
    answer_tree[type_key][group_key][variable_set_key]["VariableSet"][
        binding.variable.variable_set_item_id] = binding.value

    if len(cardinal_order) == 1:
        return

    else:
        add_solution_to_tree(cardinal_order[1:], answer_tree[type_key][group_key][variable_set_key]["ChildGroups"],
                             solution)


# We walk the cardinal tree and flatten it into individual cardinal solutions by returning every different combination
# of coll/dist nodes for the tree.
#
# Each cardinal group node has is a list of variable set *alternatives* that were generated for that variable
# at that point in the query. Just like "which rock (x1) is in every cave (x2)" would generate
# a list of alternative assignments to x1 and x2 for every rock in every cave.
#
# This routine only returns one answer: The caller chooses which type (coll or dist) should be chosen for each cardinal
# The answer is a tree, where each level of the tree represents each cardinal in the list.
def specific_coll_dist_variation(answer_set_node, variation_list):
    coll_or_dist_type = variation_list[0]
    cardinal_groups = []
    if coll_or_dist_type not in answer_set_node:
        return None

    for cardinal_group in answer_set_node[coll_or_dist_type].values():
        new_cardinal_group = {"Type": coll_or_dist_type, "VariableSets": []}
        for variable_set in cardinal_group.values():
            if len(variation_list) > 1:
                new_child_cardinal_groups = specific_coll_dist_variation(variable_set["ChildGroups"],
                                                                         variation_list[1:])
                if new_child_cardinal_groups is None:
                    return None
                else:
                    new_cardinal_group["VariableSets"].append(
                        {"VariableSetItems": variable_set["VariableSet"], "ChildGroups": new_child_cardinal_groups})
            else:
                new_cardinal_group["VariableSets"].append(
                    {"VariableSetItems": variable_set["VariableSet"], "ChildGroups": []})

        cardinal_groups.append(new_cardinal_group)

    return cardinal_groups


cardinal_logger = logging.getLogger('Cardinal')

