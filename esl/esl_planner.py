from esl import gtpyhop
from esl.worldstate import sort_of, AddRelOp, ResponseStateOp
from perplexity.response import RespondOperation

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

def unique_values(what_list):
    all_set = set()
    for what in what_list:
        all_set.update(what)
    return list(all_set)


def are_group_items(items):
    return isinstance(items, list)

###############################################################################
# Methods: Approaches to doing something that return a new list of something

def get_menu_at_entrance(state, who):
    if len(who) > 1: return
    if who[0] in ["user", "son1"]:
        if "at" not in state.rel.keys() or (who[0], "table") not in state.rel["at"]:
            return [('respond', "Sorry, you must be seated to order")]

gtpyhop.declare_task_methods('get_menu', get_menu_at_entrance)


def get_table_at_entrance(state, who_multiple):
    if all(who in ["user", "son1"] for who in who_multiple):
        if len(who_multiple) == 2:
            return [('respond',
                     "Host: Perfect! Please come right this way. The host shows you to a wooden table with a checkered tablecloth. "
                     "A minute goes by, then your waiter arrives.\nWaiter: Hi there, can I get you something to eat?"),
                    ('add_rel', "user", "at", "table"),
                    ('set_response_state', "something_to_eat")]


gtpyhop.declare_task_methods('get_table', get_table_at_entrance)


# This task deals with a group, and group items must be in a list
def satisfy_want_group(state, group_who, group_what):
    if not are_group_items(group_who) or not are_group_items(group_what): return

    # Things like the bill, or a table should be collapsed into a single item if they are the same
    unique_whats = unique_values(group_what)
    if len(unique_whats) == 1:
        # Everybody wanted the same thing
        wanted_item = unique_whats[0]
        if sort_of(state, wanted_item, "table"):
            return [("get_table", unique_values(group_who))]

    # Otherwise, we don't care if someone "wants" something together or
    # separately so we treat them as separate
    tasks = []
    for index in range(len(group_who)):
        for who in group_who[index]:
            for what in group_what[index]:
                tasks.append(('satisfy_want', (who,), (what,)))

    return tasks


def satisfy_want(state, who, what):
    if are_group_items(who) or are_group_items(what): return
    if len(who) > 1 or len(what) > 1: return
    if sort_of(state, what[0], "menu"):
        return [('get_menu', who)]


# Last option should just report an error
def satisfy_want_fail(state, who, what):
    return [('respond', "Sorry, I'm not sure what to do about that")]


gtpyhop.declare_task_methods('satisfy_want', satisfy_want, satisfy_want_group, satisfy_want_fail)

###############################################################################
# Actions: Update state to a new value

def respond(state, message):
    return state.record_operations([RespondOperation(message)])


def add_rel(state, subject, rel, object):
    return state.record_operations([AddRelOp((subject, rel, object))])


def set_response_state(state, value):
    return state.record_operations([ResponseStateOp("something_to_eat")])

gtpyhop.declare_actions(respond, add_rel, set_response_state)

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
    result, result_state = gtpyhop.find_plan(state1, [('travel', 'alice', 'park')])

    # The result will be a list of actions that must be taken to accomplish the task
    # handle_world_event() is the top level thing that happened
    # The operations like AddRelOp, AddBillOp get added to the state, it seems like these might just be able to be done directly in the planner?
    #       They were just a lightweight HTN anyway
    #       The task is "get a menu"
    # TODO:
    #   because our state object can be copied, we should just be able to use it directly
    #   Need to update find_plan to return new state object so we can use it if it worked
    #       The only thing that should update state is an action