from esl.worldstate import is_instance, instance_of_what, sort_of, rel_check
from perplexity.predications import is_concept
from perplexity.set_utilities import Measurement
from perplexity.solution_groups import GroupVariableValues
from perplexity.sstring import s


# Handle describing specials in a detailed way in case the user
# ask something like "do you have vegetarian dishes?" before they ask what the specials are
# Any question that includes an answer that is special should trigger the waiter asking if
# if the user wants to hear the detailed description of specials
def describe_list(state, what_group):
    if not isinstance(what_group, list): return

    # Describe each item, and see how many of the items we are describing are "specials"
    has_special = 0
    new_methods = []
    unique_items = set()
    for item_value in what_group:
        for item in item_value:
            if item not in unique_items:
                unique_items.add(item)
                if sort_of(state, item if not is_concept(item) else item.concept_name, "special"):
                    has_special += 1
            new_methods.append(('describe', item))

    # Has the player already heard the long description of the specials?
    heard_specials = not rel_check(state, "user", "heardSpecials", "false")

    if has_special == len(unique_items) and not heard_specials:
        # If we are being ask to describe only specials, use the special, detailed description
        new_methods.clear()
        new_methods.append(('respond', "The specials are <description>"))
        new_methods.append(('delete_rel', "user", "heardSpecials", "false"))
        new_methods.append(('add_rel', "user", "heardSpecials", "true"))

    elif has_special > 0 and not heard_specials:
        # If not all the items are specials, and we haven't described them, we should first list the short them, then
        # ask if the user wants to hear the long description
        new_methods.append(('respond', "Would you like me to describe the specials?"))

    return new_methods


def describe_single_item(state, what):
    return [('respond', convert_to_english(state, what))]


def convert_to_english(state, what):
    if is_concept(what):
        return what.concept_name

    elif isinstance(what, Measurement):
        return s("{*what.count} {*what.measurement_type:<*what.count}")

    else:
        type = instance_of_what(state, what)
        return type if type is not None else "something"


def add_declarations(gtpyhop):
    gtpyhop.declare_task_methods('describe', describe_list, describe_single_item)