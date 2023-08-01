from esl.worldstate import instance_of_what, sort_of, rel_check, object_to_store, rel_subjects, location_of_type, \
    has_item_of_type, is_type, is_instance, rel_objects
from perplexity.predications import is_concept
from perplexity.set_utilities import Measurement
from perplexity.sstring import s

task_methods = []

def describe_list_analyze(state, what_group):
    # See how many of the items we are describing are "specials" or "menu items"
    analysis = {"Specials": [],
                "MenuItems": [],
                "Bills": [],
                "Instances":[],
                "Others": [],
                "UniqueItems": set()}
    for item_value in what_group:
        for item in item_value:
            if item not in analysis["UniqueItems"]:
                analysis["UniqueItems"].add(item)
                store_object = object_to_store(item)
                # If the response is the actual 'special' type, then describe the specials
                # since we are talking about the whole class of them
                #if store_object
                if is_instance(state,store_object):
                    analysis["Instances"].append(store_object)
                if sort_of(state, store_object, "special"):
                    analysis["Specials"].append(store_object)
                elif sort_of(state, store_object, ["food", "menu"]):
                    analysis["MenuItems"].append(store_object)
                elif sort_of(state, store_object, "bill"):
                    analysis["Bills"].append(store_object)
                else:
                    analysis["Others"].append(store_object)

    return [('describe_analyzed', analysis)]


task_methods.append(['describe', describe_list_analyze])


# If we're asked questions about the menu or specials at the entrance
# tell them to be seated
def describe_analyzed_at_entrance(state, analysis):
    if location_of_type(state, "user", "table"): return

    new_methods = []
    if len(analysis["Specials"]) > 0 or len(analysis["MenuItems"]) > 0:
        new_methods.append(('respond', "If you'd like to hear about our menu items, you'll need to have a seat."))

    elif len(analysis["Bills"]) > 0:
        new_methods.append(('respond', "Let's talk about the bill once you've finished eating."))
    else:
        for item in analysis["Others"]:
            if isinstance(item, Measurement) and item.measurement_type == "dollar":
                new_methods.append(('respond', "Let's talk about prices once you've been seated."))
            else:
                new_methods.insert(0, ('describe_item', item))
    return new_methods


# Handle describing specials in a detailed way in case the user
# ask something like "do you have vegetarian dishes?" before they ask what the specials are
# Any question that includes an answer that is special should trigger the waiter asking if
# if the user wants to hear the detailed description of specials
def describe_analyzed_at_table(state, analysis):
    if not location_of_type(state, "user", "table"): return

    new_methods = []

    # Has the player already heard the long description of the specials?
    heard_specials = not rel_check(state, "user", "heardSpecials", "false")
    has_menu = any(menu_holder in ["son1", "user"] for menu_holder in has_item_of_type(state, "menu"))

    if len(analysis["Instances"]) > 0: # no special behavior if there are instances
        for i in analysis.keys():
            for j in analysis[i]:
                new_methods.append(('describe_item', j))
        return new_methods

    if len(analysis["MenuItems"]) > 0 and not has_menu:
        # If not all the items are menu items, and we haven't described them, we should first list the short version, then
        # ask if the user wants to hear the long description
        new_methods.append(("get_menu", ["user"]))
    elif len(analysis["Specials"]) > 0:
        if not heard_specials:
            # If we are being ask to describe only specials, use the special, detailed description
            new_methods.append(('respond', "Ah, I forgot to tell you about our specials. Today we have tomato soup, green salad, and smoked pork."))
            new_methods.append(('delete_rel', "user", "heardSpecials", "false"))
            new_methods.append(('add_rel', "user", "heardSpecials", "true"))
        else:
            new_methods.append(('respond',
                                "So again, those specials are tomato soup, green salad, and smoked pork."))

    else:
        for i in analysis.keys():
            for j in analysis[i]:
                new_methods.append(('describe_item', j))

    return new_methods


task_methods.append(['describe_analyzed', describe_analyzed_at_entrance, describe_analyzed_at_table])


def describe_item(state, what):
    return [('respond', convert_to_english(state, what))]


task_methods.append(['describe_item', describe_item])


def convert_to_english(state, what):
    if is_type(state, what):
        return what

    elif isinstance(what, Measurement):
        return s("{*what.count} {*what.measurement_type:<*what.count}")

    else:
        # if it is an instance, with a name, return that
        if is_instance(state, what):
            names = list(rel_objects(state, what, "hasName"))
            if len(names) > 0:
                return names[0]

        # Instances of commodities like steaks (i.e. steak1, steak2) that don't have
        # a name should always just return their type name
        type = instance_of_what(state, what)
        return type if type is not None else "something"


def add_declarations(gtpyhop):
    for methods in task_methods:
        gtpyhop.declare_task_methods(*methods)
