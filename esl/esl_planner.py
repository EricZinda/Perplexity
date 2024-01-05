import numbers

from esl import gtpyhop
from esl.esl_planner_description import add_declarations, convert_to_english
from esl.worldstate import sort_of, AddRelOp, ResponseStateOp, location_of_type, has_type, \
    rel_subjects, is_instance, AddBillOp, DeleteRelOp, \
    find_unused_item, ResetOrderAndBillOp, object_to_store, \
    find_unused_instances_from_concept, rel_subjects_greater_or_equal, noop_criteria
from perplexity.predications import is_concept
from perplexity.response import RespondOperation, ResponseLocation
from perplexity.set_utilities import Measurement
from perplexity.sstring import s
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
        stop_plan_with_error(context, "Johnny: Hey, let's sit together alright?" + state.get_reprompt())

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
            return [('respond', context, "I'm not sure what that means." + state.get_reprompt())]
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
                     "A minute goes by, then your waiter arrives.\nWaiter: Hi there, can I get you something to eat?"),
                    ('add_rel', context, "user", "at", unused_table.first_item),
                    ('add_rel', context, "son1", "at", unused_table.first_item),
                    ('set_response_state', context, "something_to_eat")]
        else:
            return [('respond', context, "I'm sorry, we don't have any tables left..." + state.get_reprompt())]

    elif for_count is not None:
        # They specified how big
        if for_count < 2:
            stop_plan_with_error(context, "Johnny: Hey! That's not enough seats!" + state.get_reprompt())
        elif for_count > 2:
            stop_plan_with_error(context, "Host: Sorry, we don't have a table with that many seats" + state.get_reprompt())

    else:
        # didn't specify size
        return [('respond', context, "How many in your party?"),
                ('set_response_state', context, "anticipate_party_size")]


def get_table_repeat(state, context, who_group, table_group, table_count_constraint):
    if any([(all_are_players(who_value) and location_of_type(state, who_value, "table")) for who_value in who_group]):
        if table_count_constraint != 1:
            return [('respond', context, "I suspect you want to sit together." + state.get_reprompt())]
        else:
            return [('respond', context, "Um... You're at a table." + state.get_reprompt())]


gtpyhop.declare_task_methods('get_table', get_table_at_entrance, get_table_repeat)


# To simplify: If anyone isn't seated we fail any request for getting a menu
def get_menu_at_entrance_who_group(state, context, who_group, menu_size_constraint):
    for who_value in who_group:
        if not all_are_players(who_value):
            # This method can't handle what the user said
            return
        else:
            for who in who_value:
                if not location_of_type(state, who, "table"):
                    return [('respond', context, "Sorry, you must be seated to get a menu" + state.get_reprompt())]


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
        stop_plan_with_error(context, "Waiter: Our policy is to give one menu to every customer ..." + state.get_reprompt())
    else:
        for who_index in range(len(who_group)):
            who_value = who_group[who_index]
            if len(who_value) > 1:
                stop_plan_with_error(context, "Waiter: Our policy is to give one menu to every customer ..." + state.get_reprompt())

            # At this point we know we are dealing with a single person
            # and the constraint is either "1" (which we will interpret as "one per person")
            # or N, where N is the number of individuals which we interpret the same
            who = who_value[0]
            if has_type(state, who, "menu"):
                tasks += [('respond',
                           context,
                           "Oh, I already gave you a menu. You look and see that there is a menu in front of you.\nSteak -- $10\nRoasted Chicken -- $7\nGrilled Salmon -- $12\n" + state.get_reprompt())]

            else:
                # Find an unused menu
                unused_menu = find_unused_item(state, "menu")
                if unused_menu:
                    tasks += [('add_rel', context, who, "have", unused_menu),
                              ('respond',
                               context,
                               "Waiter: Oh, I forgot to give you the menu? Here it is. The waiter walks off.\nSteak -- $10\nRoasted Chicken -- $7\nGrilled Salmon -- $12\nYou read the menu and then the waiter returns.\nWaiter: What can I get you?"),
                              ('set_response_state', context, "anticipate_dish")]
                else:
                    tasks += [('respond',
                               context,
                               "I'm sorry, we're all out of menus." + state.get_reprompt())]

    if len(tasks) > 0:
        return tasks


gtpyhop.declare_task_methods('get_menu', get_menu_at_entrance_who_group, get_menu_seated_who_group)


def order_food_at_entrance(state, context, who_group, what_group, what_count_constraint):
    if any([not all_are_players(who_value) for who_value in who_group]):
        return

    if any([not location_of_type(state, who_value, "table") for who_value in who_group]):
        return [('respond', context, "Sorry, you must be seated to order" + state.get_reprompt())]


# Convert a group of people and associated orders into individual tasks so that things like
# running out of food will work properly
def order_food_at_table(state, context, who_group, what_group, what_count_constraint):
    if not isinstance(who_group, (list, tuple, set)) or any([not all_are_players(who_value) for who_value in who_group]):
        return

    new_tasks = []
    assert len(who_group) == len(what_group)
    for index in range(len(who_group)):
        who_value = who_group[index]
        # "what" is already limited to single items by satisfy_want_group_group()
        what = what_group[index]
        if len(who_value) > 1:
            stop_plan_with_error(context, "Waiter: I'm sorry, we don't allow sharing orders")

        new_tasks.append(('order_food', context, who_value[0], what, what_count_constraint))

    new_tasks.append(('reprompt', context))
    return new_tasks


def order_food_at_table_per_person_per_item(state, context, who, what, what_count_constraint):
    if not isinstance(who, (list, tuple, set)) and not isinstance(what, (list, tuple, set)) and \
            all_are_players([who]) and location_of_type(state, who, "table"):
        food_instances = [x for x in find_unused_instances_from_concept(context, state, what)]
        if len(food_instances) < what_count_constraint:
            return [('respond', context, f"I'm sorry, we don't have enough {what} for your order.")]

        else:
            store_what = object_to_store(what)
            what_english = s("{Bare *convert_to_english(state, what):}")
            assert store_what in state.sys["prices"]
            if (store_what, "user") in state.all_rel("priceUnknownTo"):
                return [('respond', context, f"Son: Wait, let's not order {what_english} before we know how much it costs.")]

            elif state.sys["prices"][store_what] * what_count_constraint + state.bill_total() > 15:
                return [('respond', context, f"Son: Wait, we already spent ${str(state.bill_total())} so if we get {what_count_constraint} {what_english}, we won't be able to pay for it with $15.")]

            else:
                new_tasks = [('respond', context, f"Waiter: {what_english} is an excellent choice!")]
                order_count = 0
                for food_instance in food_instances:
                    if sort_of(state, [food_instance], "dish"):
                        new_tasks += [('add_rel', context, who, "ordered", food_instance),
                                      ('add_bill', context, what.concept_name)]
                    else:
                        return

                    order_count += 1
                    if order_count == what_count_constraint:
                        break

                new_tasks.append(('set_response_state', context, "anything_else"))
                return new_tasks


gtpyhop.declare_task_methods('order_food', order_food_at_entrance, order_food_at_table, order_food_at_table_per_person_per_item)


def complete_order(state, context):
    if state.sys["responseState"] == "anything_else":
        if not state.user_ordered_veg():
            return [("respond", context, "Johnny: Dad! I’m vegetarian, remember?? Why did you only order meat? \nMaybe they have some other dishes that aren’t on the menu… You tell the waiter to restart your order.\nWaiter: Ok, can I get you something else to eat?"),
                    ("set_response_state", context, "something_to_eat"),
                    ("reset_order_and_bill", context)]

        items = [i for i in state.all_rel("ordered")]

        if len(items) < 2:
            return [("respond",
                     context,
                     "You realize that you'll need at least two dishes for the two of you.\n Waiter: Can I get you something else to eat?"),
                    ("set_response_state", context, "something_to_eat")]

        item_str = " ".join([i for (x, i) in items])

        add_have_ops = []
        for i in items:
            add_have_ops += [("add_rel", context, i[0], "have", i[1])]

        return [("respond", context, "Ok, I'll be right back with your meal.\nA few minutes go by and the robot returns with " + item_str + ".\nThe food is good, but nothing extraordinary."),
                ("set_response_state", context, "done_ordering")] + add_have_ops
    elif state.sys["responseState"] == "something_to_eat":
        return [("respond", context, "Well if you aren't going to order anything, you'll have to leave the restaurant, so I'll ask you again: can I get you something to eat?")]
    else:
        return [("respond", context, "Waiter: Hmm. I didn't understand what you said." + state.get_reprompt())]


gtpyhop.declare_task_methods('complete_order', complete_order)


def get_bill_at_table(state, context, who_group, what_count_constraint):
    if not isinstance(who_group, (list, tuple, set)) or any([not all_are_players(x) for x in who_group]):
        return

    if len(who_group) > 1:
        stop_plan_with_error(context, "Waiter: There is only one bill ..." + state.get_reprompt())

    for i in state.all_rel("valueOf"):
        if i[1] == "bill1":
            total = i[0]
            if state.sys["responseState"] in ["done_ordering", "way_to_pay"]:
                return [('respond', context, f"Your total is {str(total)} dollars. Would you like to pay by cash or card?"),
                        ('set_response_state', context, "way_to_pay")]
            else:
                return [('respond', context, "But... you haven't got any food yet!" + state.get_reprompt())]


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
    task_dict = {}
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

        # TODO: find a better way to determine what "what" is
        concept = what.concept_name
        if sort_of(state, concept, "menu"):
            if "get_menu" not in task_dict:
                task_dict["get_menu"] = [[]]
            task_dict["get_menu"][0].append(who_list)

        # elif concept == "special":
        #     if "describe_item" not in task_dict:
        #         task_dict["describe_item"] = []
        #     task_dict["describe_item"].append("special")

        elif sort_of(state, concept, "table"):
            if "get_table" not in task_dict:
                task_dict["get_table"] = [[], []]
            task_dict["get_table"][0].append(who_list)
            task_dict["get_table"][1].append(what)

        elif sort_of(state, concept, "food"):
            if "order_food" not in task_dict:
                task_dict["order_food"] = [[], []]
            task_dict["order_food"][0].append(who_list)
            task_dict["order_food"][1].append(what)

        elif sort_of(state, concept, ["bill", "check"]):
            if "get_bill" not in task_dict:
                task_dict["get_bill"] = [[]]
            task_dict["get_bill"][0].append(who_list)

    # If what_size_constraint > 1, then all the solutions in the group should be about the same kind of thing
    # because the phrase must have been something like "we want two menus/steaks"
    if what_size_constraint > 1 and len(task_dict) > 1:
        # Not all items are the same and there is a constraint > 1 ...
        # unclear what to do (or even what scenario would cause this)
        return

    # Now run the different tasks for the different kind of things that are wanted
    tasks = []
    for task_group in task_dict.items():
        tasks.append(tuple([task_group[0], context] + task_group[1] + [what_size_constraint]))

    if len(tasks) > 0:
        return tasks


# Last option should just report an error
def satisfy_want_fail(state, context, who, what, min_size):
    stop_plan_with_error(context, "Sorry, I'm not sure what to do about that" + state.get_reprompt())


gtpyhop.declare_task_methods('satisfy_want', satisfy_want_group_group, satisfy_want_fail)


###############################################################################
# Actions: Update state to a new value
def respond(state, context, message):
    return state.apply_operations([RespondOperation(message)])


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


def reset_order_and_bill(state, context):
    return state.apply_operations([ResetOrderAndBillOp()])


def reprompt(state, context):
    return state.apply_operations([RespondOperation(state.get_reprompt(return_first=False), location=ResponseLocation.last)])


gtpyhop.declare_actions(respond, respond_has_more, add_rel, delete_rel, set_response_state, add_bill, reset_order_and_bill, reprompt)

add_declarations(gtpyhop)


class ExitNowException(Exception):
    pass


# If the intuition is to succeed with a failure message like "I couldn't do that!"
# But there might be alternatives that can work, use this. It stops the planner immediately
# but records a high priority error so that, if nothing else works, that error will get shown
def stop_plan_with_error(context, error_text):
    context.report_error(["understoodFailureMessage", error_text], force=True)
    raise ExitNowException()


# If it is "a table for 2" get both at the same table
# If it is I would like a table, ask how many
# If it is "we" would like a table, count the people and fail if it is > 2
def do_task(state, task):
    try:
        result, result_state = gtpyhop.find_plan(state, task)
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