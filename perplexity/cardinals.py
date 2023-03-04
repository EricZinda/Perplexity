import copy
import itertools

from perplexity.tree import find_predications_in_list, walk_tree_predications_until, split_predications_consuming_event


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
    coll_dist_options = [["dist"]] * len(cardinal_order)
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