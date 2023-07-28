import numbers

from esl import gtpyhop
from esl.esl_planner_description import add_declarations
from esl.worldstate import sort_of, AddRelOp, ResponseStateOp, location_of_type, rel_check, has_type, all_instances, \
    rel_subjects, is_instance, instance_of_what, AddBillOp, DeleteRelOp, noun_structure, rel_subjects_objects, \
    find_unused_item
from perplexity.execution import report_error
from perplexity.predications import Concept, is_concept
from perplexity.response import RespondOperation
from perplexity.set_utilities import Measurement
from perplexity.solution_groups import GroupVariableValues
from perplexity.utilities import at_least_one_generator

domain_name = __name__
the_domain = gtpyhop.Domain(domain_name)


###############################################################################
# Methods: Approaches to doing something that return a new list of something

# def do_nothing(state,p,y):
#     if is_a(p,'person') and is_a(y,'location'):
#         x = state.loc[p]
#         if x == y:
#             return []
#
# def travel_by_foot(state,p,y):
#     if is_a(p,'person') and is_a(y,'location'):
#         x = state.loc[p]
#         if x != y and distance(x,y) <= 2:
#             return [('walk',p,x,y)]
#
# def travel_by_taxi(state,p,y):
#     if is_a(p,'person') and is_a(y,'location'):
#         x = state.loc[p]
#         if x != y and state.cash[p] >= taxi_rate(distance(x,y)):
#             return [('call_taxi',p,x), ('ride_taxi',p,y), ('pay_driver',p,y)]

###############################################################################
# Actions: Update state to a new value

# def walk(state, p, x, y):
#     if is_a(p, 'person') and is_a(x, 'location') and is_a(y, 'location') and x != y:
#         if state.loc[p] == x:
#             state.loc[p] = y
#             return state
#
#
# def call_taxi(state, p, x):
#     if is_a(p, 'person') and is_a(x, 'location'):
#         state.loc['taxi1'] = x
#         state.loc[p] = 'taxi1'
#         return state
#
#
# def ride_taxi(state, p, y):
#     # if p is a person, p is in a taxi, and y is a location:
#     if is_a(p, 'person') and is_a(state.loc[p], 'taxi') and is_a(y, 'location'):
#         taxi = state.loc[p]
#         x = state.loc[taxi]
#         if is_a(x, 'location') and x != y:
#             state.loc[taxi] = y
#             state.owe[p] = taxi_rate(distance(x, y))
#             return state
#
#
# def pay_driver(state, p, y):
#     if is_a(p, 'person'):
#         if state.cash[p] >= state.owe[p]:
#             state.cash[p] = state.cash[p] - state.owe[p]
#             state.owe[p] = 0
#             state.loc[p] = y
#             return state

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



###############################################################################
# Methods: Approaches to doing something that return a new list of something

def get_menu_at_entrance(state, who):
    if all_are_players(who) and not location_of_type(state, who[0], "table"):
        return [('respond', "Sorry, you must be seated to get a menu")]

def get_menu_seated(state, who):
    if all_are_players(who) and location_of_type(state, who[0], "table"):
        tasks = []
        for who_singular in who:
            if has_type(state, who_singular, "menu"):
                tasks += [('respond',
                            "Oh, I already gave you a menu. You look and see that there is a menu in front of you.\nSteak -- $10\nRoasted Chicken -- $7\nGrilled Salmon -- $12\n" + state.get_reprompt())]
            else:
                # Find an unused menu
                unused_menu = find_unused_item(state, "menu")
                if unused_menu:
                    tasks += [('add_rel', who_singular, "have", unused_menu),
                              ('respond',
                               "Waiter: Oh, I forgot to give you the menu? Here it is. The waiter walks off.\nSteak -- $10\nRoasted Chicken -- $7\nGrilled Salmon -- $12\nYou read the menu and then the waiter returns.\nWaiter: What can I get you?"),
                              ('set_response_state', "anticipate_dish")]
                else:
                    tasks += [('respond',
                             "I'm sorry, we're all out of menus." + state.get_reprompt())]
        if len(tasks) > 0:
            return tasks



gtpyhop.declare_task_methods('get_menu', get_menu_at_entrance, get_menu_seated)

def count_entities(value_group):
    if value_group is None:
        return None

    count = 0
    for item in value_group:
        if is_concept(item):
            card = noun_structure(item, "card")
            if card is not None:
                count += card
            else:
                count += 1
        elif isinstance(item, Measurement):
            if isinstance(item.count, numbers.Number):
                count += item.count
        else:
            count += 1

    return count

# Tables are special in that, in addition to having a count ("2 tables") they can be ("for 2")
def get_table_at_entrance(state, who_multiple, table):
    if all_are_players(who_multiple) and \
        not location_of_type(state, who_multiple[0], "table"):
        # If the count of table is > 1, fail
        table_count = noun_structure(table, "card")
        if table_count is not None and table_count != 1:
            return [('respond', "Johnny: Hey, let's sit together alright?")]
        for_structure = noun_structure(table, "for")
        for_count = count_entities(for_structure)
        # If they say "we want a table" or "table for 2" the size is implied
        if len(who_multiple) == 2 or for_count == 2:
            unused_table = find_unused_item(state, "table")
            if unused_table is not None:
                return [('respond',
                         "Host: Perfect! Please come right this way. The host shows you to a wooden table with a checkered tablecloth. "
                         "A minute goes by, then your waiter arrives.\nWaiter: Hi there, can I get you something to eat?"),
                        ('add_rel', "user", "at", unused_table),
                        ('add_rel', "son1", "at", unused_table),
                        ('set_response_state', "something_to_eat")]
            else:
                return [('respond', "I'm sorry, we don't have any tables left...")]

        elif for_count is not None:
            # They specified how big
            if for_count < 2:
                return [('respond', "Johnny: Hey! That's not enough seats!")]
            elif for_count > 2:
                return [('respond', "Host: Sorry, we don't have a table with that many seats")]

        else:
            # didn't specify size
            return [('respond', "How many in your party?"),
                    ('set_response_state', "anticipate_party_size")]


def get_table_repeat(state, who_multiple, table):
    if all_are_players(who_multiple) and \
            location_of_type(state, who_multiple[0], "table"):
        return [('respond', "Um... You're at a table." + state.get_reprompt())]


gtpyhop.declare_task_methods('get_table', get_table_at_entrance, get_table_repeat)


def get_bill_at_entrance(state, who_multiple):
    if all_are_players(who_multiple) and \
        not location_of_type(state, who_multiple[0], "table"):
        return [('respond', "But... you haven't got any food yet!" + state.get_reprompt())]


def get_bill_at_table(state, who_multiple):
    if all_are_players(who_multiple):
        for i in state.all_rel("valueOf"):
            if i[1] == "bill1":
                total = i[0]
                if state.sys["responseState"] == "done_ordering":
                    return [('respond',  f"Your total is f{str(total)} dollars. Would you like to pay by cash or card?"),
                            ('set_response_state', "way_to_pay")]
                else:
                    return [('respond', "But... you haven't got any food yet!" + state.get_reprompt())]


gtpyhop.declare_task_methods('get_bill', get_bill_at_entrance, get_bill_at_table)


# order_food methods are all passed single objects, not tuples
# so we don't have to check
def order_food_at_entrance(state, who, what):
    if all_are_players([who]) and not location_of_type(state, who, "table"):
        return [('respond', "Sorry, you must be seated to order")]


def order_food_price_unknown(state, who, what):
    if all_are_players([who]) and location_of_type(state, who, "table"):
        if (what, "user") in state.all_rel("priceUnknownTo"):
            return [('respond', "Son: Wait, let's not order that before we know how much it costs." + state.get_reprompt())]


def order_food_too_expensive(state, who, what):
    if all_are_players([who]) and location_of_type(state, who, "table"):
        assert what in state.sys["prices"]
        if state.sys["prices"][what] + state.bill_total() > 15:
            return [('respond', f"Son: Wait, we already spent ${str(state.bill_total())} so if we get that, we won't be able to pay for it with $15.{state.get_reprompt()}")]


def order_food_out_of_stock(state, who, what):
    if all_are_players([who]) and location_of_type(state, who, "table"):
        for item in state.all_rel("ordered"):
            if item[1] == what:
                return [('respond',
                         "Sorry, you got the last one of those. We don't have any more. Can I get you something else?" + state.get_reprompt())]


def order_food_at_table(state, who, what):
    if all_are_players([who]) and location_of_type(state, who, "table"):
        food_instance = find_unused_item(state, what)

        return [('respond', "Excellent Choice! Can I get you anything else?"),
                ('add_rel', who, "ordered", food_instance),
                ('add_bill', what),
                ('set_response_state', "anything_else")]


gtpyhop.declare_task_methods('order_food', order_food_at_entrance, order_food_price_unknown, order_food_out_of_stock, order_food_too_expensive, order_food_at_table)


# This task deals with lists that map to each other. I.e. the first who goes with the first what
# Its job is to analyze the top level solution group would could have a lot of different collections
# that need to be analyzed.  One or more people, one or more things wanted, etc.
# For concepts, it requires that the caller has made sure that wanted concepts are valid, meaning "I want the (conceptual) table"
# Should never get to this point
def satisfy_want_group_group(state, group_who, group_what):
    if not isinstance(group_who, list) or not isinstance(group_what, list): return

    # To support "we would like a table/the bill/etc" not going to every person,@Predication(vocabulary, names=["solution_group__be_v_id"])
    # def _be_v_id_group(state_list, has_more, e_introduced_binding_list, x_obj1_variable_group, x_obj2_variable_group):
    #     yield state_list
    # conceptual things like "the bill", or "a table" or "a menu" should be collapsed into a single item
    # and handled once if everyone wants the same thing
    unique_whats = unique_group_variable_values(group_what)
    if len(unique_whats) == 1:
        # Everybody wanted the same thing
        # Only need to check the first because: If one item in the group is a concept, they all are
        one_thing = unique_whats[0]
        if is_concept(one_thing):
            if one_thing.concept_name == "table":
                # Tables are special in that, in addition to having a count ("2 tables")
                # they can be "for 2" or "for my son and me"
                return [("get_table", unique_group_variable_values(group_who), one_thing)]
            elif one_thing.concept_name == "menu":
                return [("get_menu", unique_group_variable_values(group_who))]
            elif one_thing.concept_name == "bill":
                return [("get_bill", unique_group_variable_values(group_who))]

        else:
            # They are asking for a particular instance of something, which should never work: fail
            return

    # Otherwise, we don't care if someone "wants" something together or
    # separately (since it isn't semantically different) so we treat them as separate
    # and plan them one at a time
    tasks = []
    for index in range(len(group_who)):
        for who in group_who[index]:
            for what in group_what[index]:
                tasks.append(('satisfy_want', (who,), (what,)))

    return tasks


def satisfy_want(state, who, what):
    if len(who) > 1 or len(what) > 1: return

    if is_instance(state, what[0]): #TODO: Ask when could this be true
        # They are asking for a *particular instance of a table* (or whatever)
        # report an error if this is the best we can do
        return [('respond', "I'm sorry, we don't allow requesting specific things like that" + state.get_reprompt())]
    else:
        concept = what[0].concept_name
        if sort_of(state, concept, "menu"):
            return [('get_menu', who)]

        elif concept == "special":
            return [('describe_item',"special")]

        elif sort_of(state, concept, "table"):
            return [('get_menu', who[0])]

        elif sort_of(state, concept, "food"):
            return [('order_food', who[0], concept)]


# Last option should just report an error
def satisfy_want_fail(state, who, what):
    return [('respond', "Sorry, I'm not sure what to do about that")]


gtpyhop.declare_task_methods('satisfy_want', satisfy_want_group_group, satisfy_want, satisfy_want_fail)

###############################################################################
# Actions: Update state to a new value

def respond(state, message):
    return state.record_operations([RespondOperation(message)])


def add_rel(state, subject, rel, object):
    return state.record_operations([AddRelOp((subject, rel, object))])

def delete_rel(state, subject, rel, object):
    return state.record_operations([DeleteRelOp((subject, rel, object))])


def set_response_state(state, value):
    return state.record_operations([ResponseStateOp(value)])


def add_bill(state, wanted):
    return state.record_operations([AddBillOp(wanted)])


gtpyhop.declare_actions(respond, add_rel, delete_rel, set_response_state, add_bill)

add_declarations(gtpyhop)

# If it is "a table for 2" get both at the same table
# If it is I would like a table, ask how many
# If it is "we" would like a table, count the people and fail if it is > 2

def do_task(state, task):
    result, result_state = gtpyhop.find_plan(state, task)
    # print(result)
    return result_state


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