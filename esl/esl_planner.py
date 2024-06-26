import copy
import numbers
from esl import gtpyhop
from esl.esl_planner_description import add_declarations, convert_to_english, oxford_comma
from esl.worldstate import sort_of, AddRelOp, ResponseStateOp, location_of_type, has_type, \
    AddBillOp, DeleteRelOp, \
    find_unused_item, ResetOrderAndBillOp, object_to_store, \
    find_unused_instances_from_concept, rel_subjects_greater_or_equal, noop_criteria, rel_objects, \
    ResetOrderAndBillForPersonOp, rel_subjects, ESLConcept, orderable_concepts, requestable_concepts_by_sort, \
    CancelOrderItemOp, rel_all_instances
from perplexity.predications import is_concept, Concept
from perplexity.response import RespondOperation, ResponseLocation, NoopOperation, get_reprompt_operation
from perplexity.set_utilities import Measurement
from perplexity.sstring import s
from perplexity.state import SetXOperation
from perplexity.utilities import at_least_one_generator

domain_name = __name__
the_domain = gtpyhop.Domain(domain_name)


###############################################################################
# Helpers

def unique_group_variable_values(what_group):
    all = list()
    for what in what_group:
        for what_item in what:
            if what_item not in all:
                all.append(what_item)
    return all


def are_group_items(items):
    return isinstance(items, list)


def all_are_players(who_multiple):
    return all(who in ["user", "son1"] for who in who_multiple)


def count_entities(value_group):
    if value_group is None:
        return None

    count = 0
    for item in value_group:
        if isinstance(item, Measurement):
            if isinstance(item.count, numbers.Number):
                count += item.count
        else:
            count += 1

    return count


###############################################################################
# Methods: Approaches to doing something that return a new list of something


# We either have one solution with a collective "who" or one or more solutions with distributive single "who"
# Tables are special in that, in addition to having a count ("2 tables") they can be ("for 2")
def get_table_at_entrance(state, context, who_group, table_group, table_count_constraint):
    # This method is designed for players, who are not yet at a table
    if any([(not all_are_players(who_value) or location_of_type(state, who_value, "table"))
            for who_value in who_group]):
        return

    # If they explicitly asked for > 1 table or
    # if there are more than one solution, it means that the player and their son are asking to be at two tables
    if table_count_constraint != 1 or len(who_group) > 1:
        # The user is asking for more than one table
        stop_plan_with_error(state, context, "Johnny: Hey, let's sit together alright?")

    # At this point we know there is only one solution
    # satisfy_want_group_group guarantees that the who_group will contain values (i.e. sets of one or more)
    # and table_group will contain individuals
    who_value = who_group[0]
    table = table_group[0]

    # Evaluate the noun to make sure we understand all the terms that were used with it
    # If we get back a state, it means the user said something that made sense
    # and they at least meant "a table" of some kind
    instances = at_least_one_generator(table.instances(context, state))
    if instances is None:
        return

    else:
        # Check to see if the user specified a table "for x (i.e. 2)"
        # This needs to be done against the concept (not the instance) because there is no way, after the fact, to know
        # if the way they asked for the table specified how many people it should have or if it just happened to have
        # that many
        for_value = None
        for_capacity = table.find_criteria(rel_subjects_greater_or_equal, "maxCapacity", None)
        for_possession = table.find_criteria(noop_criteria, "targetPossession", None)
        if for_possession is not None:
            for_value = for_possession[2]
        elif for_capacity is not None:
            for_value = for_capacity[2]

    # If they say "we want a table" (because we means 2 in this scenario) or "table for 2" the size is implied
    if for_value is not None and not isinstance(for_value, tuple) and isinstance(for_value, numbers.Number):
        # "... table for N"
        for_count = for_value
    elif for_value is not None and isinstance(for_value, (list, tuple)) and all_are_players(for_value):
        # "... table for my son and I together"
        # "... table for me"
        for_count = len(for_value)
    else:
        if for_value is not None:
            return [('respond', context, "I'm not sure what that means.")]
        else:
            if len(who_value) > 1:
                # "We want a table"
                for_count = len(who_value)
            else:
                # "I want a table", "Do you have a table?", "I want a table for my son"
                for_count = None

    if for_count == 2:
        unused_table = at_least_one_generator(find_unused_instances_from_concept(context, state, table))
        if unused_table is not None:
            return [('respond',
                     context,
                     "Host: Perfect! Please come right this way. The host shows you to a wooden table with a checkered tablecloth. "
                     "A minute goes by, then your waiter arrives.\nWaiter: Hi there!"),
                    ('add_rel', context, "user", "at", unused_table.first_item),
                    ('add_rel', context, "son1", "at", unused_table.first_item),
                    ('set_response_state', context, "anticipate_dish")]
        else:
            return [('respond', context, "I'm sorry, we don't have any tables left...")]

    elif for_count is not None:
        # They specified how big
        if for_count < 2:
            stop_plan_with_error(state, context, "Johnny: Hey! That's not enough seats!")
        elif for_count > 2:
            stop_plan_with_error(state, context, "Host: Sorry, we don't have a table with that many seats.")

    else:
        # didn't specify size
        return [('set_response_state', context, "anticipate_party_size")]


def get_table_repeat(state, context, who_group, table_group, table_count_constraint):
    if any([(all_are_players(who_value) and location_of_type(state, who_value, "table")) for who_value in who_group]):
        if table_count_constraint != 1:
            return [('respond', context, "Waiter: I suspect you want to sit together.")]
        else:
            return [('respond', context, "Waiter: Um... You're at a table.")]


gtpyhop.declare_task_methods('get_table', get_table_at_entrance, get_table_repeat)


# We want 2 menus
# We want 2 menus for my son and me
# We want menus
# I want a menu
def get_menu_seated_who_group(state, context, who_group, menu_size_constraint):
    # If any of the players are not at the table, the previous method would have succeeded
    # So, we don't need to check again
    if not isinstance(who_group, (list, tuple, set)) or any([not all_are_players(who_value) for who_value in who_group]):
        return

    tasks = []

    # min_size either needs to be "1" and interpreted as "one each" in which case "we want a menu"
    if menu_size_constraint != 1 and len(who_group) != menu_size_constraint:
        stop_plan_with_error(state, context, "Waiter: Our policy is to give one menu to every customer ...")

    else:
        for who_index in range(len(who_group)):
            who_value = who_group[who_index]
            if len(who_value) > 1:
                stop_plan_with_error(state, context, "Waiter: Our policy is to give one menu to every customer ...")

            # At this point we know we are dealing with a single person
            # and the constraint is either "1" (which we will interpret as "one per person")
            # or N, where N is the number of individuals which we interpret the same
            who = who_value[0]
            if has_type(state, who, "menu"):
                tasks += [('respond',
                           context,
                           s("Waiter: Oh, I already gave {bare *convert_to_english(state, who):} a menu. You can see that there is a menu in front of {bare *convert_to_english(state, who):}.")),
                          ('show_menu', context)]
            else:
                already_ordered = False
                for who_item in state.ordered_but_not_delivered():
                    if who == who_item[0] and sort_of(state, who_item[1], "menu"):
                        already_ordered = True
                        break
                if already_ordered:
                    tasks += [('respond',
                               context,
                               s("Waiter: You already ordered a menu for {bare *convert_to_english(state, who):}"))]
                else:
                    # Find an unused menu
                    unused_menu = find_unused_item(state, "menu")
                    if unused_menu:
                        # If they ask for a menu, immediately complete the order
                        tasks += [('add_rel', context, who, "ordered", unused_menu),
                                  ('set_response_state', context, "anticipate_dish"),
                                  ('respond',
                                   context,
                                   s("Waiter: Oh, I forgot to give {bare *convert_to_english(state, who):} the menu! I'll get {bare *convert_to_english(state, who):} one right away."))]
                    else:
                        tasks += [('respond',
                                   context,
                                   "Waiter: I'm sorry, we're all out of menus.")]

    if len(tasks) > 0:
        return tasks


gtpyhop.declare_task_methods('get_menu', get_menu_seated_who_group)


def show_menu(state, context):
    return [('respond_location',
             context,
             "\nThe menu says:\nSteak -- $10\nRoasted Chicken -- $7\nGrilled Salmon -- $12\n",
             ResponseLocation.last)]


gtpyhop.declare_task_methods('show_menu', show_menu)


def order_food_at_entrance(state, context, who_group, what_group, what_count_constraint):
    if any([not all_are_players(who_value) for who_value in who_group]):
        return

    if any([not location_of_type(state, who_value, "table") for who_value in who_group]):
        return [('respond', context, "Sorry, you must be seated to order.")]


# what_size_constraint can apply to distributive OR collective.  I.e. what_size_constraint = 1 in
# "we want a menu" could mean (mySon, me) want (1 menu) or we each want one
# This version assumes  what_count_constraint is cumulative
def order_food_at_table_cumulative(state, context, who_group, what_group, what_count_constraint):
    if not isinstance(who_group, (list, tuple, set)) or any([not all_are_players(who_value) for who_value in who_group]):
        return

    assert len(who_group) == len(what_group)
    if what_count_constraint % len(who_group) != 0:
        # Can't be evenly distributed, don't do cumulative
        return

    new_tasks = []
    for index in range(len(who_group)):
        who_value = who_group[index]
        # "what" is already limited to single items by satisfy_want_group_group()
        what = what_group[index]
        if len(who_value) > 1:
            stop_plan_with_error(state, context, "Waiter: I'm sorry, we don't allow sharing orders")

        new_tasks.append(('order_food', context, who_value[0], what, what_count_constraint // len(who_group)))

    return new_tasks


# Convert a group of people and associated orders into individual tasks so that things like
# running out of food will work properly
def order_food_at_table_distributive(state, context, who_group, what_group, what_count_constraint):
    if not isinstance(who_group, (list, tuple, set)) or any([not all_are_players(who_value) for who_value in who_group]):
        return

    assert len(who_group) == len(what_group)
    new_tasks = []
    for index in range(len(who_group)):
        who_value = who_group[index]
        # "what" is already limited to single items by satisfy_want_group_group()
        what = what_group[index]
        if len(who_value) > 1:
            stop_plan_with_error(state, context, "Waiter: I'm sorry, we don't allow sharing orders")

        new_tasks.append(('order_food', context, who_value[0], what, what_count_constraint))

    return new_tasks


# `What` needs to be the string name of a type (not, for example, a concept)
def order_food_at_table_per_person_per_item(state, context, who, what, what_count_constraint):
    if not isinstance(who, (list, tuple, set)) and not isinstance(what, (list, tuple, set)) and \
            all_are_players([who]) and location_of_type(state, who, "table"):
        food_instances = [x for x in find_unused_instances_from_concept(context, state, ESLConcept(what))]
        if len(food_instances) < what_count_constraint:
            stop_plan_with_error(state, context, s("Waiter: I'm sorry, we don't have enough {bare *convert_to_english(state, what):} for your order."))

        else:
            what_english = s("{Bare *convert_to_english(state, what):}")
            assert what in state.sys["prices"]
            if (what, "user") in state.all_rel("priceUnknownTo"):
                return [('respond', context, f"Son: Wait, let's not order {what_english} before we know how much it costs.")]

            elif state.sys["prices"][what] * what_count_constraint + state.bill_total() > 20:
                return [('respond', context, f"Son: Wait, we already spent ${str(state.bill_total())} so if we get {what_count_constraint} {what_english}, we won't be able to pay for it with $20.")]

            else:
                new_tasks = [('respond', context, f"Waiter: {what_english} is an excellent choice!")]
                order_count = 0
                for food_instance in food_instances:
                    if sort_of(state, [food_instance], ["dish", "drink"]):
                        new_tasks += [('add_rel', context, who, "ordered", food_instance),
                                      ('add_bill', context, what)]
                    else:
                        return

                    order_count += 1
                    if order_count == what_count_constraint:
                        break

                new_tasks.append(('set_response_state', context, "anticipate_dish"))
                return new_tasks


gtpyhop.declare_task_methods('order_food', order_food_at_entrance, order_food_at_table_cumulative, order_food_at_table_distributive, order_food_at_table_per_person_per_item)


# Go and get all the things that were asked for
def go_away_and_come_back(state, context):
    tasks = [("respond", context, "Waiter: I'll be right back!\nA few minutes go by and the waiter returns.")]

    # If they ordered something, they now have it
    order_dict = {}
    for who_item in state.ordered_but_not_delivered():
        if who_item[0] not in order_dict:
            order_dict[who_item[0]] = []
        order_dict[who_item[0]].append(who_item[1])
        tasks += [("add_rel", context, who_item[0], "have", who_item[1])]

    # Now present it to them
    has_food = False
    for item in order_dict.items():
        if any([sort_of(state, x, "food")  for x in item]):
            has_food = True
        item_str = oxford_comma([convert_to_english(state, i) for i in item[1]])
        if isinstance(item[0], tuple):
            who_str = oxford_comma([convert_to_english(state, i) for i in item[0]])
            tasks.append(('respond', context, s('Waiter: Here is {a *who:} for {*who_str:}.')))
        else:
            tasks.append(('respond', context, s('Waiter: Here is {a *item_str:} for {bare *convert_to_english(state, item[0]):}.')))

    if has_food:
        tasks.append(('respond', context, "The food is good, but nothing extraordinary."))

    # If the menu was ordered, only read it out once, at the end
    for ordered in order_dict.values():
        if any([sort_of(state, item, "menu") for item in ordered]):
            tasks.append(('show_menu', context))
            break

    tasks.append(('reprompt', context))

    return tasks


gtpyhop.declare_task_methods('go_away_and_come_back', go_away_and_come_back)


def complete_order(state, context):
    if state.sys["responseState"] == "anticipate_dish":
        if state.only_ordered_not_delivered_water_or_menus():
            return [('go_away_and_come_back', context)]

        elif len([item for item in state.ordered_food()]) < 2:
            return [("respond",
                     context,
                     "You realize that you'll need at least two dishes for the two of you."),
                    ('reprompt', context)]

        elif not state.user_ordered_veg():
            return [("respond",
                     context,
                     "Johnny: Dad! I’m vegetarian, remember?? Why did you only order meat? \nMaybe they have some other dishes that aren’t on the menu? \nYou tell the waiter to ignore what you just ordered."),
                    ("reset_order_and_bill", context),
                    ("reprompt", context)]

        else:
            return [('go_away_and_come_back', context)]

    elif state.sys["responseState"] == "anticipate_dish":
        return [("respond",
                 context,
                 "Well if you aren't going to order anything, you'll have to leave the restaurant, so I'll ask you again: can I get you something to eat?")]

    else:
        return [("respond",
                 context,
                 "Waiter: Hmm. I didn't understand what you said."),
                ('reprompt', context)]


gtpyhop.declare_task_methods('complete_order', complete_order)


def get_bill_at_table(state, context, who_group, what_count_constraint):
    if not isinstance(who_group, (list, tuple, set)) or any([not all_are_players(x) for x in who_group]):
        return

    if len(who_group) > 1:
        stop_plan_with_error(state, context, "Waiter: There is only one bill ...")

    for i in state.all_rel("valueOf"):
        if i[1] == "bill1":
            total = i[0]
            if [x for x in state.ordered_but_not_delivered()]:
                return [('respond', context, "Waiter: Let's finish up this order before we get your bill.")]

            elif any([x for x in state.have_food()]) and (state.sys["responseState"] in ["anticipate_dish", "way_to_pay"]):
                return [('respond', context, f"Waiter: Your total is {str(total)} dollars."),
                        ('set_response_state', context, "way_to_pay"),
                        ('reprompt', context)]

            else:
                return [('respond', context, "Waiter: But... you haven't got any food yet!")]


gtpyhop.declare_task_methods('get_bill', get_bill_at_table)


# Decide how to divvy up orig_min_size between the group_who elements
def divide_size(group_who, orig_min_size):
    # Divide up min_size evenly among the group_who items
    # if that is possible, otherwise give everyone min_size items
    min_size = orig_min_size // len(group_who)
    if min_size > 0:
        remainder = orig_min_size % len(group_who)
    else:
        min_size = orig_min_size
        remainder = 0

    return min_size, remainder


# This is the top level method for any kind of "wanting" phrase. It is passed an iterable of iterables representing
# the solution group values of who and what
# This task deals with lists that map to each other. I.e. the first "who" goes with the first "what"
# Its job is to analyze the top level solution group. It could have a lot of different combinations
# that need to be analyzed.  One or more people, one or more things wanted, etc.
#
# Scenarios:
# I want a water and some menus
# I want a steak and a salmon / a table and a menu / a steak for me and a menu for my son
# We want a menu
# We want 2 menus
# We want 2 menus for my son and me
# We want 2 steaks and the check please!
# We want a steak, the soup and the check please!
#
# Requirements/Design:
# - Since it is unclear what wanting them "together" means, we force each solution in the group to have only one "what"
# - We only deal with wanting concepts, not particular items
# - what_size_constraint can apply to distributive OR collective.  I.e. what_size_constraint = 1 in
#   "we want a menu" could mean (mySon, me) want (1 menu) or we each want one
# - if what_size_constraint > 1, then all the solutions in the group should be about the same kind of thing
#   because the phrase must have been something like "we want two menus/steaks"
# For concepts, it requires that the caller has made sure that wanted concepts are valid, meaning "I want *the* (conceptual) table"
# should never get to this point
def satisfy_want_group_group(state, context, group_who, group_what, what_size_constraint):
    # Only need to check the first item since they will all be concepts or instances
    # Since that is the way solution groups work
    if not isinstance(group_who, (list, tuple, set)) or not isinstance(group_what, (list, tuple, set)) or not is_concept(group_what[0][0]):
        return

    # Iterate through each group_who / group_what pair
    assert len(group_what) == len(group_who)

    # At the front door we only handle getting a table and ignore the rest
    not_at_table = False
    for who in group_who:
        if not location_of_type(state, who, "table"):
            not_at_table = True
            break

    task_dict = {}
    ask_server_about = []
    for index in range(len(group_what)):
        what_list = group_what[index]
        if len(what_list) > 1:
            # Since it is unclear what wanting them "together" means, we force each solution to have only one "what"
            # If any has more than one we halt and let the system give us a different solution group
            return

        # At this point, "what" is a single item
        what = what_list[0]

        # If "I want x for somebody" we need to fixup the "who" to be "somebody"
        # Note that "somebody" could be "my son and me", i.e. more than one person
        target_criteria = what.find_criteria(noop_criteria, "targetPossession", None)
        if target_criteria is not None:
            who_list = target_criteria[2]
        else:
            who_list = group_who[index]

        # Now figure out what kind of thing this is by seeing what concepts it entails
        things_we_know = requestable_concepts_by_sort(state)

        # Now see if it is a thing we can give the speaker
        concept_analysis = {}
        _, instances_of_concepts = what.instances_of_concepts(context, state, things_we_know.keys())
        for item in instances_of_concepts.items():
            concept_category = things_we_know[item[0]][0]
            concept_name = things_we_know[item[0]][1]
            if concept_category not in concept_analysis:
                concept_analysis[concept_category] = {}

            if concept_name not in concept_analysis[concept_category]:
                concept_analysis[concept_category][concept_name] = 1
            else:
                concept_analysis[concept_category][concept_name] += 1

        # If we don't even know what this concept it, fail generally ("I want steel")
        if len(concept_analysis) == 0:
            return [('respond', context, s("Host: Sorry, I don't know how to give you that.")),
                    ('reprompt', context)]

        # If it entails things across the various classes we know ("I want something small" entails "the bill" and various "menu items") fail with a general message
        if len(concept_analysis) > 1:
            return [('respond', context, s("Host: Sorry, could you be more specific, that could be several different kinds of thing.")),
                    ('reprompt', context)]

        # At this point it is exactly one class of thing.
        # If it entails various concepts within that class ("I want something vegetarian" is only menu items) be more specific in the failure
        concept_subconcepts = next(iter(concept_analysis.items()))
        if len(concept_subconcepts[1]) > 1:
            return [('respond', context, s("Host: Sorry, I'm not sure which one you mean.")),
                    ('reprompt', context)]

        concept_name = concept_subconcepts[0]
        subconcept = next(iter(concept_subconcepts[1]))
        if concept_name == "table":
            if "get_table" not in task_dict:
                task_dict["get_table"] = [[], []]
            task_dict["get_table"][0].append(who_list)
            task_dict["get_table"][1].append(what)

        else:
            if not_at_table:
                ask_server_about.append(subconcept)

            else:
                if concept_name == "menu":
                    if "get_menu" not in task_dict:
                        task_dict["get_menu"] = [[]]
                    task_dict["get_menu"][0].append(who_list)

                elif concept_name == "dish":
                    if "order_food" not in task_dict:
                        task_dict["order_food"] = [[], []]
                    task_dict["order_food"][0].append(who_list)
                    task_dict["order_food"][1].append(subconcept)

                elif concept_name == "bill":
                    if "get_bill" not in task_dict:
                        task_dict["get_bill"] = [[]]
                    task_dict["get_bill"][0].append(who_list)

    # If what_size_constraint > 1, then all the solutions in the group should be about the same kind of thing
    # because the phrase must have been something like "we want two menus/steaks"
    if what_size_constraint > 1 and len(task_dict) > 1:
        # Not all items are the same and there is a constraint > 1 ...
        # unclear what to do (or even what scenario would cause this)
        return

    # Now we have a set of wants for different groups of people
    # Now run the different tasks for the different kind of things that are wanted
    tasks = []
    for task_group in task_dict.items():
        tasks.append(tuple([task_group[0], context] + task_group[1] + [what_size_constraint]))

    if ask_server_about:
        unique_items = set([convert_to_english(state, item) for item in ask_server_about])
        items = oxford_comma(list(unique_items))
        tasks.insert(0, ('respond', context, s("Host: Sorry, you'll need to talk to your waiter about {a *items:} when you have a table.")))

    if len(tasks) > 0:
        return tasks + [('reprompt', context)]


# Last option should just report an error
def satisfy_want_fail(state, context, who, what, min_size):
    stop_plan_with_error(state, context, "Waiter: Sorry, I'm not sure what to do about that.")


gtpyhop.declare_task_methods('satisfy_want', satisfy_want_group_group, satisfy_want_fail)


def cancel_group_group(state, context, group_who, group_what, what_size_constraint):
    # This will be actual instances that were ordered
    who_ordereditems = state.ordered_but_not_delivered()

    tasks = []
    canceled_by_person = {}
    for index in range(len(group_what)):
        what_list = group_what[index]
        if len(what_list) > 1:
            # Since it is unclear what cancelling them "together" means, we force each solution to have only one "what"
            # If any has more than one we halt and let the system give us a different solution group
            return

        # At this point, "what" is a single concept
        what = what_list[0]
        remaining_cancel = what_size_constraint

        # If "Can I cancel x for somebody" or "my x" we need to fixup the "who" to be "somebody"
        # Note that "somebody" could be "my son and me", i.e. more than one person
        target_criteria = what.find_criteria(noop_criteria, "targetPossession", None)
        if target_criteria is not None:
            who_list = target_criteria[2]
        else:
            who_list = group_who[index]

        # See if the customer wants to cancel any of the orders
        orders_to_cancel = what.instances(context, state, rel_all_instances(state, None, "order"))
        if len(orders_to_cancel) > 0:
            for order in orders_to_cancel:
                person = [item for item in rel_subjects(state, "have", order)]
                if len(person) == 1:
                    order_person = person[0]
                    if len([item for item in state.ordered_but_not_delivered(for_person=order_person)]) > 0:
                        if order_person not in canceled_by_person:
                            canceled_by_person[order_person] = []
                        canceled_by_person[order_person].append(order)
                        tasks.append(('reset_order_and_bill_for_person', context, order_person))
                    else:
                        # there was no order
                        person_name = convert_to_english(state, order_person)
                        tasks += [('respond', context,
                                     s("Waiter: Sorry, I don't believe there is an order for {*person_name:}."))]

            continue

        # If we have a "who" for an item, then we need to cancel that item for them
        # if there is no "who" it could be anyone
        found_what = False
        for who_ordereditem in who_ordereditems:
            # If what they said references this instance, cancel it
            if what.instances(context, state, [who_ordereditem[1]]):
                # Remember what we've canceled, organized by person so we can
                # tell the customer
                if who_ordereditem[0] not in canceled_by_person:
                    canceled_by_person[who_ordereditem[0]] = []
                canceled_by_person[who_ordereditem[0]].append(who_ordereditem[1])

                # Now actually cancel it
                tasks.append(('cancel_order_item', context, who_ordereditem[0], who_ordereditem[1]))
                found_what = True
                remaining_cancel -= 1
                if remaining_cancel == 0:
                    break

        if not found_what:
            item = convert_to_english(state, what)
            tasks += [('respond', context,
                         s("Waiter: Sorry, I don't believe I have that order."))]

        # Couldn't cancel everything so ...
        if remaining_cancel > 0:
            item = convert_to_english(state, what)
            if what_size_constraint > remaining_cancel:
                tasks.append(('respond', context, s("Waiter: Sorry, I don't believe you've ordered {*remaining_cancel:} of {the *item:} you want to cancel.")))
            else:
                # already given a message for this case
                pass

    if len(canceled_by_person) > 0:
        final = []
        for key_value in canceled_by_person.items():
            person = convert_to_english(state, key_value[0])
            if sort_of(state, key_value[1], "order"):
                final.append(s("the order for {*person:}"))
            else:
                items = oxford_comma([convert_to_english(state, item) for item in key_value[1]])
                final.append(s("{a *items:} from the order for {*person:}"))

        final_text = oxford_comma(final)
        tasks.insert(0, ('respond', context,
                         s("Waiter: I have removed {*final_text}.")))

    return tasks + [('reprompt', context)]


gtpyhop.declare_task_methods('cancel', cancel_group_group)


###############################################################################
# Actions: Update state to a new value
def respond(state, context, message):
    return state.apply_operations([RespondOperation(message)])


def respond_location(state, context, message, location):
    return state.apply_operations([RespondOperation(message, location=ResponseLocation.last)])


def respond_has_more(state, context, message, has_more):
    return state.apply_operations([RespondOperation(message, location=ResponseLocation.last, show_if_has_more=has_more)])


def add_rel(state, context, subject, rel, object):
    if isinstance(subject, (list, tuple)) and len(subject) == 1:
        subject = subject[0]
    return state.apply_operations([AddRelOp((subject, rel, object))])


def delete_rel(state, context, subject, rel, object):
    return state.apply_operations([DeleteRelOp((subject, rel, object))])


def set_response_state(state, context, value):
    return state.apply_operations([ResponseStateOp(value)])


def add_bill(state, context, wanted):
    return state.apply_operations([AddBillOp(wanted)])


def cancel_order_item(state, context, for_person, item):
    return state.apply_operations([CancelOrderItemOp(for_person, item)])


def reset_order_and_bill(state, context):
    return state.apply_operations([ResetOrderAndBillOp()])


def reset_order_and_bill_for_person(state, context, for_person):
    return state.apply_operations([ResetOrderAndBillForPersonOp(for_person)])


def reprompt(state, context):
    return state.apply_operations([get_reprompt_operation(state)])


def add_plan_local(state, context, name, value):
    current = state.get_binding("plan_locals").value
    if current is None:
        next_current = dict()
    else:
        next_current = copy.deepcopy(current)

    next_current[name] = value
    return state.apply_operations([SetXOperation("plan_locals", (next_current, ))])


gtpyhop.declare_actions(respond, respond_location, respond_has_more, add_rel, delete_rel, set_response_state, add_bill, cancel_order_item, reset_order_and_bill, reset_order_and_bill_for_person, reprompt, add_plan_local)

add_declarations(gtpyhop)


class ExitNowException(Exception):
    pass


# If the intuition is to succeed with a failure message like "I couldn't do that!"
# But there might be alternatives that can work, use this. It stops the planner immediately
# but records a high priority error so that, if nothing else works, that error will get shown
def stop_plan_with_error(state, context, error_text):
    context.report_error(["understoodFailureMessage", error_text + "\n" + state.get_reprompt()], force=True)
    raise ExitNowException()


# If it is "a table for 2" get both at the same table
# If it is I would like a table, ask how many
# If it is "we" would like a table, count the people and fail if it is > 2
def do_task(state, task):
    try:
        result, result_state = gtpyhop.find_plan(state, task)
        if result_state:
            # Clear out any local plan variables from this plan so they aren't
            # seen by the next plan
            result_state = result_state.set_x("plan_locals", None)

        # print(result)
        return result_state

    except ExitNowException:
        return None


gtpyhop.verbose = 0


if __name__ == '__main__':
    # If we've changed to some other domain, this will change us back.
    gtpyhop.current_domain = the_domain
    gtpyhop.print_domain()

    # state1 = state0.copy()

    expected = [('call_taxi', 'alice', 'home_a'), ('ride_taxi', 'alice', 'park'), ('pay_driver', 'alice', 'park')]

    print("-- If verbose=0, the planner will return the solution but print nothing.")
    # result, result_state = gtpyhop.find_plan(state1, [('travel', 'alice', 'park')])

    # The result will be a list of actions that must be taken to accomplish the task
    # handle_world_event() is the top level thing that happened
    # The operations like AddRelOp, AddBillOp get added to the state, it seems like these might just be able to be done directly in the planner?
    #       They were just a lightweight HTN anyway
    #       The task is "get a menu"
    # TODO:
    #   because our state object can be copied, we should just be able to use it directly
    #   Need to update find_plan to return new state object so we can use it if it worked
    #       The only thing that should update state is an action