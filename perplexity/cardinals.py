import copy

from perplexity.tree import find_predications_in_list, walk_tree_predications_until


# Return all of the predications named predication_name
def split_related(term, primary_predication):
    def find(predication):
        introduced_index = predication.introduced_variable_index()
        for arg_index in range(0, len(predication.arg_types)):
            if predication.arg_types[arg_index] not in ["c", "h"]:
                if predication.args[arg_index] == target_variable:
                    if arg_index != introduced_index:
                        found_predications.append(predication)
                    return

        remaining_predications.append(predication)

    target_variable = primary_predication.introduced_variable()
    found_predications = []
    remaining_predications = []

    walk_tree_predications_until(term, find)
    return found_predications, remaining_predications


# Rebuild the rstr and return:
# The bare rstr without the cardinal stuff
# the cardinal stuff with the bare rstr as an argument
def split_cardinal_rstr(term):
    # See if there are any cardinals
    cardinal_list = find_predications_in_list(term, ["_a+few_a_1", "card", "ord", "much-many", "several"])

    if len(cardinal_list) > 0:
        # Figure out if there are any modifiers modifying the event
        # such as "only"
        cardinal_modifiers, remaining_predications = split_related(term, cardinal_list[0])

        new_cardinal = copy.deepcopy(cardinal_list[0])
        new_cardinal.name = new_cardinal.name + "_with_scope"
        cardinal_clause = cardinal_modifiers + [new_cardinal]

    else:
        new_cardinal = None
        cardinal_clause = []
        remaining_predications = term

    return new_cardinal, cardinal_clause, remaining_predications

