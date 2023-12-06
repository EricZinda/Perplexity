import numbers

from esl import gtpyhop
from esl.esl_planner_description import add_declarations
from esl.worldstate import sort_of, AddRelOp, ResponseStateOp, location_of_type, has_type, \
    rel_subjects, is_instance, AddBillOp, DeleteRelOp, \
    find_unused_item, ResetOrderAndBillOp,  object_to_store, \
    find_unused_instances_from_concept
from perplexity.predications import is_concept
from perplexity.response import RespondOperation
from perplexity.set_utilities import Measurement
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
def get_menu_at_entrance(state, context, who_list, min_size):
    if all_are_players(who_list) and not location_of_type(state, who_list[0], "table"):
        return [('respond', context, "Sorry, you must be seated to get a menu" + state.get_reprompt())]


def get_menu_seated_who_list(state, context, who_list, min_size):
    if not isinstance(who_list, list):
        return

    if all_are_players(who_list) and location_of_type(state, who_list[0], "table"):
        if len(who_list) < min_size:
            tasks = [('respond',
                      context,
                      "That seems like an excessive number of menus ...\n")]
        else:
            tasks = []

        for who_singular in who_list:
            tasks.append(('get_menu', context, who_singular, 1))

    if len(tasks) > 0:
        return tasks


def get_menu_seated_who(state, context, who_singular, min_size):
    if isinstance(who_singular, list):
        return

    tasks = []
    if has_type(state, who_singular, "menu"):
        tasks += [('respond',
                   context,
                   "Oh, I already gave you a menu. You look and see that there is a menu in front of you.\nSteak -- $10\nRoasted Chicken -- $7\nGrilled Salmon -- $12\n" + state.get_reprompt())]

    else:
        # Find an unused menu
        unused_menu = find_unused_item(state, "menu")
        if unused_menu:
            tasks += [('add_rel', context, who_singular, "have", unused_menu),
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


gtpyhop.declare_task_methods('get_menu', get_menu_at_entrance, get_menu_seated_who_list, get_menu_seated_who)


# Tables are special in that, in addition to having a count ("2 tables") they can be ("for 2")
def get_table_at_entrance(state, context, who_multiple, table, min_size):
    if all_are_players(who_multiple) and \
            not location_of_type(state, who_multiple[0], "table"):
        if min_size != 1:
            return [('respond', context, "Johnny: Hey, let's sit together alright?" + state.get_reprompt())]

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
            for_criteria = table.find_criteria(rel_subjects, "maxCapacity", None)
            for_value = for_criteria[2] if for_criteria is not None else None

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
                if len(who_multiple) > 1:
                    # "We want a table"
                    for_count = len(who_multiple)
                else:
                    # "I want a table", "Do you have a table?"
                    for_count = None

        if for_count == 2:
            if min_size > 1:
                return [('respond', context, "I suspect you want to sit together."+ state.get_reprompt())]
            else:
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
                return [('respond', context, "Host: Sorry, we don't have a table with that many seats"+ state.get_reprompt())]

        else:
            # didn't specify size
            return [('respond', context, "How many in your party?"),
                    ('set_response_state', context, "anticipate_party_size")]


def get_table_repeat(state, context, who_multiple, table, min_size):
    if all_are_players(who_multiple) and \
            location_of_type(state, who_multiple[0], "table"):
        if min_size != 1:
            return [('respond', context, "I suspect you want to sit together."+ state.get_reprompt())]
        else:
            return [('respond', context, "Um... You're at a table." + state.get_reprompt())]


gtpyhop.declare_task_methods('get_table', get_table_at_entrance, get_table_repeat)


def get_bill_at_table(state, context):
    for i in state.all_rel("valueOf"):
        if i[1] == "bill1":
            total = i[0]
            if state.sys["responseState"] in ["done_ordering", "way_to_pay"]:
                return [('respond', context, f"Your total is {str(total)} dollars. Would you like to pay by cash or card?"),
                        ('set_response_state', context, "way_to_pay")]
            else:
                return [('respond', context, "But... you haven't got any food yet!" + state.get_reprompt())]


gtpyhop.declare_task_methods('get_bill', get_bill_at_table)


# order_food methods are all passed single objects, not tuples
# so we don't have to check
def order_food_at_entrance(state, context, who, what):
    if all_are_players([who]) and not location_of_type(state, who, "table"):
        return [('respond', context, "Sorry, you must be seated to order"+ state.get_reprompt())]


def order_food_price_unknown(state, context, who, what):
    if all_are_players([who]) and location_of_type(state, who, "table"):
        if (object_to_store(what), "user") in state.all_rel("priceUnknownTo"):
            return [('respond', context, "Son: Wait, let's not order that before we know how much it costs." + state.get_reprompt())]


def order_food_too_expensive(state, context, who, what):
    if all_are_players([who]) and location_of_type(state, who, "table"):
        store_what = object_to_store(what)
        assert store_what in state.sys["prices"]
        if state.sys["prices"][store_what] + state.bill_total() > 15:
            return [('respond', context, f"Son: Wait, we already spent ${str(state.bill_total())} so if we get that, we won't be able to pay for it with $15.{state.get_reprompt()}")]


def order_food_out_of_stock(state, context, who, what):
    if all_are_players([who]) and location_of_type(state, who, "table"):
        store_what = object_to_store(what)
        for item in state.all_rel("ordered"):
            if item[1] == store_what:
                return [('respond',
                         context,
                         "Sorry, you got the last one of those. We don't have any more. Can I get you something else?" + state.get_reprompt())]


def order_food_at_table(state, context, who, what):
    if all_are_players([who]) and location_of_type(state, who, "table"):
        # Evaluate the "what" concept to make sure we understand all the terms that were used with it
        # The user could have said "steak" or "steak for 2" or "rare steak", etc
        # If we get back a state, it means the user said something that made sense
        # and they at least meant e.g. "a steak" of some kind, that exists in the system
        food_instances = [x for x in find_unused_instances_from_concept(context, state, what)]
        if len(food_instances) == 0:
            return
        else:
            new_tasks = [('respond', context, "Excellent Choice! Can I get you anything else?")]
            for food_instance in food_instances:
                if sort_of(state, [food_instance], "dish"):
                    new_tasks += [('add_rel', context, who, "ordered", food_instance),
                                  ('add_bill', context, what.concept_name)]
                else:
                    return
                break
            new_tasks.append(('set_response_state', context, "anything_else"))
            return new_tasks


gtpyhop.declare_task_methods('order_food', order_food_at_entrance, order_food_price_unknown, order_food_out_of_stock, order_food_too_expensive, order_food_at_table)


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


# This task deals with lists that map to each other. I.e. the first who goes with the first what
# Its job is to analyze the top level solution group would could have a lot of different collections
# that need to be analyzed.  One or more people, one or more things wanted, etc.
# For concepts, it requires that the caller has made sure that wanted concepts are valid, meaning "I want the (conceptual) table"
# Should never get to this point
def satisfy_want_group_group(state, context, group_who, group_what, min_size):
    if not isinstance(group_who, list) or not isinstance(group_what, list): return

    # To support "we would like a table/the bill/etc" not going to every person,@Predication(vocabulary, names=["solution_group__be_v_id"])
    # def _be_v_id_group(state_list, has_more, e_introduced_binding_list, x_obj1_variable_group, x_obj2_variable_group):
    #     yield state_list
    # conceptual things like "the bill", or "a table" or "a menu" should be collapsed into a single item
    # and handled once if everyone wants the same thing
    unique_whats = unique_group_variable_values(group_what)
    if len(unique_whats) == 1:
        # Everybody wanted the same kind of thing
        # Only need to check the first because: If one item in the group is a concept, they all are
        one_thing = unique_whats[0]
        if is_concept(one_thing):
            if one_thing.concept_name == "table":
                return [("get_table", context, unique_group_variable_values(group_who), one_thing, min_size)]
            elif one_thing.concept_name == "menu":
                return [("get_menu", context, unique_group_variable_values(group_who), min_size)]
            elif one_thing.concept_name in ["bill", "check"]:
                return [("get_bill", context)]

        else:
            # They are asking for a particular instance of something, which should never work: fail
            return

    # Otherwise, we don't care if someone "wants" something together or
    # separately (since it isn't semantically different) so we treat them as separate
    # and plan them one at a time
    tasks = []
    assert len(group_who) == len(group_what)
    for index in range(len(group_who)):
        for who in group_who[index]:
            for what in group_what[index]:
                tasks.append(('satisfy_want', context, who, what, min_size))

    return tasks


# Requires actual values not a list
def satisfy_want(state, context, who, what, min_size):
    # if len(who) != 1 or len(what) != 1: return
    if isinstance(who, (list, tuple, set)) or isinstance(who, (list, tuple, set)): return

    if is_instance(state, what):
        # They are asking for a *particular instance of a table* (or whatever)
        # report an error if this is the best we can do
        return [('respond', context, "I'm sorry, we don't allow requesting specific things like that" + state.get_reprompt())]
    else:
        actions = []
        for _ in range(min_size):
            concept = what.concept_name
            if sort_of(state, concept, "menu"):
                actions.append(('get_menu', context, who))

            elif concept == "special":
                actions.append(('describe_item', context, "special"))

            elif sort_of(state, concept, "table"):
                actions.append(('get_menu', context, who))

            elif sort_of(state, concept, "food"):
                actions.append(('order_food', context, who, what))

        return actions


# Last option should just report an error
def satisfy_want_fail(state, context, who, what, min_size):
    stop_plan_with_error(context, "Sorry, I'm not sure what to do about that" + state.get_reprompt())


gtpyhop.declare_task_methods('satisfy_want', satisfy_want_group_group, satisfy_want, satisfy_want_fail)


###############################################################################
# Actions: Update state to a new value
def respond(state, context, message):
    return state.apply_operations([RespondOperation(message)])


def add_rel(state, context, subject, rel, object):
    return state.apply_operations([AddRelOp((subject, rel, object))])


def delete_rel(state, context, subject, rel, object):
    return state.apply_operations([DeleteRelOp((subject, rel, object))])


def set_response_state(state, context, value):
    return state.apply_operations([ResponseStateOp(value)])


def add_bill(state, context, wanted):
    return state.apply_operations([AddBillOp(wanted)])


def reset_order_and_bill(state, context):
    return state.apply_operations([ResetOrderAndBillOp()])


gtpyhop.declare_actions(respond, add_rel, delete_rel, set_response_state, add_bill, reset_order_and_bill)

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