from esl.worldstate import instance_of_what, sort_of, rel_check, object_to_store, location_of_type, \
    has_item_of_type, is_type, is_instance, rel_objects, all_instances_and_spec, all_specializations
from perplexity.predications import is_concept
from perplexity.set_utilities import Measurement
from perplexity.sstring import s

task_methods = []


def describe_list_analyze(state, context, what_group):
    # See how many of the items we are describing are "specials" or "menu items"
    analysis = {"Specials": [],
                "MenuItems": [],
                "Bills": [],
                "Instances": [],
                "Others": [],
                "UniqueItems": set()}

    for item_value in what_group:
        for item in item_value:
            if item not in analysis["UniqueItems"]:
                analysis["UniqueItems"].add(item)
                store_object = object_to_store(item)
                if is_instance(state, store_object):
                    analysis["Instances"].append(store_object)
                if sort_of(state, store_object, "special"):
                    analysis["Specials"].append(store_object)
                elif sort_of(state, store_object, ["food", "menu"]):
                    analysis["MenuItems"].append(store_object)
                elif sort_of(state, store_object, "bill"):
                    analysis["Bills"].append(store_object)
                else:
                    analysis["Others"].append(store_object)

    return [('describe_analyzed', context, analysis)]


task_methods.append(['describe', describe_list_analyze])


# If we're asked questions about the menu or specials at the entrance
# tell them to be seated
def describe_analyzed_at_entrance(state, context, analysis):
    if location_of_type(state, "user", "table"):
        return

    new_methods = []
    if len(analysis["Specials"]) > 0 or len(analysis["MenuItems"]) > 0:
        new_methods.append(('respond', context, "Host: If you'd like to hear about our menu items, you'll need to have a seat." + state.get_reprompt()))

    elif len(analysis["Bills"]) > 0:
        new_methods.append(('respond', context, "Waiter: Let's talk about the bill once you've finished eating." + state.get_reprompt()))

    else:
        for item in analysis["Others"]:
            if isinstance(item, Measurement) and item.measurement_type == "dollar":
                new_methods.append(('respond', context, "Host: Let's talk about prices once you've been seated." + state.get_reprompt()))

            else:
                new_methods.insert(0, ('describe_item', context, item))
                new_methods.append(('respond', context, state.get_reprompt()))

    return new_methods


# Handle describing specials in a detailed way in case the user
# ask something like "do you have vegetarian dishes?" before they ask what the specials are
# Any question that includes an answer that is special should trigger the waiter asking if
# if the user wants to hear the detailed description of specials
def describe_analyzed_at_table(state, context, analysis):
    if not location_of_type(state, "user", "table"):
        return

    new_methods = []

    # Has the player already heard the long description of the specials?
    heard_specials = not rel_check(state, "user", "heardSpecials", "false")
    has_menu = any(menu_holder in ["son1", "user"] for menu_holder in has_item_of_type(state, "menu"))

    # no special behavior if there are instances
    if len(analysis["Instances"]) > 0:
        return [('describe_item', context, list(analysis["UniqueItems"]))]

    if len(analysis["MenuItems"]) > 0 and not has_menu:
        # Describe the menu if the user hasn't heard it and they ask a question
        # that results in any number of menu items being generated
        new_methods += [("get_menu", context, [["user"]], 1),
                        ('reprompt', context)]
        return new_methods

    analysis_specials_count = len(analysis["Specials"])
    if analysis_specials_count > 0:
        if not heard_specials:
            # If we are being ask to describe any specials and the user hasn't heard of them yet,
            # give the special, detailed description
            new_methods.append(('respond', context, "Waiter: Ah, I forgot to tell you about our specials. Today we have tomato soup, green salad, and smoked pork." + state.get_reprompt()))
            new_methods.append(('delete_rel', context, "user", "heardSpecials", "false"))
            new_methods.append(('add_rel', context, "user", "heardSpecials", "true"))
            return new_methods

        elif analysis_specials_count == len(analysis["UniqueItems"]):
            # Subtract 1 to account for the generic concept "special"
            if analysis_specials_count - 1 == len([x for x in all_specializations(state, "special")]):
                # We are responding with *only* specials, and in fact *all* of them, and have already heard
                # the long version, give a terser response
                new_methods.append(('respond',
                                    context,
                                    "Waiter: So again, we have tomato soup, green salad, and smoked pork."),
                                   ('reprompt', context))
                return new_methods

    rel = list(state.all_rel("have"))
    for i in analysis.keys():
        if not i == "UniqueItems":
            for j in analysis[i]:
                if j in all_instances_and_spec(state, "thing"):
                    if ("restaurant", j) in rel:
                        new_methods.append(('describe_item', context, j))
                else:
                    j = object_to_store(j)
                    if j in all_instances_and_spec(state, "thing"):
                        if ("restaurant", j) in rel:
                            new_methods.append(('describe_item', context, j))
                    else:
                        new_methods.append(('describe_item', context, j))

    return new_methods + [('respond_has_more', context, "(among others)", True),
                          ('reprompt', context)]


task_methods.append(['describe_analyzed', describe_analyzed_at_entrance, describe_analyzed_at_table])


# Handles a list by returning a count
def describe_item_list(state, context, whats):
    if isinstance(whats, list):
        english_count = {}
        for what in whats:
            english = convert_to_english(state, what)
            if english not in english_count:
                english_count[english] = 1
            else:
                english_count[english] += 1

        new_tasks = []
        for item in english_count.items():
            if item[1] == 1:
                new_tasks.append(('respond', context, item[0]))
            else:
                new_tasks.append(('respond', context, f"{item[1]} {item[0]}"))

        new_tasks.append(('respond_has_more', context, "(among others)", True))

        return new_tasks


def describe_item(state, context, what):
    if not isinstance(what, list):
        new_tasks = [('respond', context, convert_to_english(state, what))]
        new_tasks.append(('respond_has_more', context, "(among others)", True))

        return new_tasks


task_methods.append(['describe_item', describe_item_list, describe_item])


def oxford_comma(words):
    if isinstance(words, str):
        return words
    if len(words) == 1:
        return words[0]
    elif len(words) == 2:
        return '{} and {}'.format(words[0], words[1])
    else:
        return '{}, and {}'.format(', '.join(words[:-1]), words[-1])

def convert_to_english(state, what):
    if is_concept(what):
        return what.concept_name

    if is_type(state, what):
        return what

    elif isinstance(what, Measurement):
        if what.measurement_type == "":
            return s("{*what.count}")
        else:
            return s("{*what.count} {*what.measurement_type:<*what.count}")

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
