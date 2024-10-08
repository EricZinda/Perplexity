from perplexity.predications import combinatorial_predication_1, lift_style_predication_2
from perplexity.state import State
from perplexity.system_vocabulary import system_vocabulary
from perplexity.user_interface import UserInterface
from perplexity.vocabulary import Predication, ValueSize, EventOption
from perplexity.world_registry import register_world
import perplexity.messages
import perplexity.sstring

vocabulary = system_vocabulary()


@Predication(vocabulary, names=["_file_n_of"])
def file_n_of(context, state, x_binding, i_binding):
    def bound_variable(value):
        if value in ["file1.txt", "file2.txt", "file3.txt"]:
            return True
        else:
            context.report_error(["notAThing", x_binding.value, x_binding.variable.name])
            return False

    def unbound_variable():
        yield "file1.txt"
        yield "file2.txt"
        yield "file3.txt"

    yield from combinatorial_predication_1(context,
                                           state,
                                           x_binding,
                                           bound_variable,
                                           unbound_variable)


@Predication(vocabulary, names=["_large_a_1"])
def large_a_1(context, state, e_introduced_binding, x_target_binding):
    def criteria_bound(value):
        if value == "file2.txt":
            return True

        else:
            context.report_error(["adjectiveDoesntApply", "large", x_target_binding.variable.name])
            return False

    def unbound_values():
        # Find all large things
        yield "file2.txt"

    yield from combinatorial_predication_1(context,
                                           state,
                                           x_target_binding,
                                           criteria_bound,
                                           unbound_values)


@Predication(vocabulary,
             names=["_lift_v_cause"],
             arguments=[("e",), ("x", ValueSize.all), ("x", ValueSize.all)])
def lift(context, state, e_introduced_binding, x_actor_binding, x_item_binding):
    def check_items_lifting_items(item1, item2):
        if item1 == ("Elsa", "Seo-Yun") and len(item2) == 1 and item2[0] == "table1":
            return True
        else:
            context.report_error(["xIsNotYZ", x_actor_binding.variable.name, "lifting", x_item_binding.variable.name])

    def all_item1s_lifting_item2s(item2):
        if len(item2) == 1 and item2[0] == "table1":
            yield ("Elsa", "Seo-Yun")

    def all_item2s_being_lifted_by_item1s(item1):
        if item1 == ("Elsa", "Seo-Yun"):
            yield ("table1",)

    yield from lift_style_predication_2(context,
                                        state,
                                        x_actor_binding,
                                        x_item_binding,
                                        check_items_lifting_items,
                                        all_item1s_lifting_item2s,
                                        all_item2s_being_lifted_by_item1s)


@Predication(vocabulary, names=["_student_n_of"])
def student_n_of(context, state, x_binding, i_binding):
    def bound_variable(value):
        if value in ["Elsa", "Seo-Yun"]:
            return True
        else:
            context.report_error(["notAThing", x_binding.value, x_binding.variable.name])
            return False

    def unbound_variable():
        yield "Elsa"
        yield "Seo-Yun"

    yield from combinatorial_predication_1(context, state, x_binding, bound_variable, unbound_variable)


@Predication(vocabulary, names=["_table_n_1"])
def table_n_1(context, state, x_binding):
    def bound_variable(value):
        if value in ["table1"]:
            return True
        else:
            context.report_error(["notAThing", x_binding.value, x_binding.variable.name])
            return False

    def unbound_variable():
        yield "table1"

    yield from combinatorial_predication_1(context, state, x_binding, bound_variable, unbound_variable)


# This is a helper function that any predication that can
# be "very'd" can use to understand just how "very'd" it is
def degree_multiplier_from_event(context, state, e_introduced_binding):
    # if a "very" is modifying this event, use that value
    # otherwise, return 1
    if e_introduced_binding.value is None or \
            "DegreeMultiplier" not in e_introduced_binding.value:
        degree_multiplier = 1

    else:
        degree_multiplier = e_introduced_binding.value["DegreeMultiplier"]["Value"]

    return degree_multiplier


@Predication(vocabulary, names=["_very_x_deg"])
def very_x_deg(context, state, e_introduced_binding, e_target_binding):
    # We'll interpret every "very" as meaning "one order of magnitude larger"
    yield state.add_to_e(e_target_binding.variable.name,
                         "DegreeMultiplier",
                         {"Value": 10,
                          "Originator": context.current_predication_index()})



@Predication(vocabulary,
             names=["_large_a_1"],
             handles=[("DegreeMultiplier", EventOption.optional)])
def large_a_1_very(context, state, e_introduced_binding, x_target_binding):
    # See if any modifiers have changed *how* large we should be
    degree_multiplier = degree_multiplier_from_event(context, state, e_introduced_binding)

    def criteria_bound(value):
        if degree_multiplier == 1 and value == "file2.txt":
            return True

        else:
            context.report_error(["adjectiveDoesntApply", "large", x_target_binding.variable.name])
            return False

    def unbound_values():
        if criteria_bound("file2.txt"):
            yield "file2.txt"

    yield from combinatorial_predication_1(context, state, x_target_binding, criteria_bound, unbound_values)


# Called to initialize or reset the micro-world state
def reset():
    return State([])


# Creates the micro-world interface on startup
# or if the user loads the world later
def ui():
    ui = UserInterface(world_name="SimplestExample",
                       reset_function=reset,
                       vocabulary=vocabulary,
                       message_function=generate_custom_message)
    return ui


# Generates all the responses that predications can
# return when an error occurs
def generate_custom_message(state, tree_info, error_term):
    # See if the system can handle converting the error
    # to a message first
    system_message = perplexity.messages.generate_message(state, tree_info, error_term)
    if system_message is not None:
        return system_message

    else:
        # error_term is of the form: [index, error] where "error" is another
        # list like: ["name", arg1, arg2, ...]. The first item is the error
        # constant (i.e. its name). What the args mean depends on the error
        error_predicate_index = error_term[0]
        error_arguments = error_term[1]
        error_constant = error_arguments[0] if error_arguments is not None else "no error set"
        arg_length = len(error_arguments) if error_arguments is not None else 0
        arg1 = error_arguments[1] if arg_length > 1 else None
        arg2 = error_arguments[2] if arg_length > 2 else None
        arg3 = error_arguments[3] if arg_length > 3 else None
        arg4 = error_arguments[4] if arg_length > 4 else None

        if error_constant == "notAThing":
            # s() acts like a Python "f string" but also
            # converts a variable name like 'x3' into the english words
            # that it represented in the MRS. The "*" in {*arg1} tells
            # it to use the value of arg1 directly without converting it
            # (described below)
            return perplexity.sstring.s("{*arg1} is not {arg2}", tree_info)

        elif error_constant == "adjectiveDoesntApply":
            return perplexity.sstring.s("{arg2} is not {*arg1}", tree_info)

        else:
            # No custom message, just return the raw error for debugging
            return str(error_term)


# Worlds need to be registered so the user can switch between them by name
# and so that the engine can search for their autocorrect and other cached files
# in the same directory where the ui() function resides
register_world(world_name="SimplestExample",
               module="hello_world_pre_FileSystemState",
               ui_function="ui")


if __name__ == '__main__':
    user_interface = ui()
    while user_interface:
        # The loop might return a different user interface
        # object if the user changes worlds
        user_interface = user_interface.default_loop()