from perplexity.predications import combinatorial_predication_1
from perplexity.state import State
from perplexity.system_vocabulary import system_vocabulary
from perplexity.user_interface import UserInterface
from perplexity.vocabulary import Predication
from perplexity.world_registry import register_world
import perplexity.messages


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


# Called to initialize or reset the micro-world state
def reset():
    return State([])


# Creates the micro-world interface on startup
# or if the user loads the world later
def ui():
    ui = UserInterface(world_name="SimplestExample",
                       reset_function=reset,
                       vocabulary=vocabulary)
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
            return s("{*arg1} is not {arg2}", tree_info)

        else:
            # No custom message, just return the raw error for debugging
            return str(error_term)


# Worlds need to be registered so the user can switch between them by name
# and so that the engine can search for their autocorrect and other cached files
# in the same directory where the ui() function resides
register_world(world_name="SimplestExample",
               module="hello_world_simplest",
               ui_function="ui")


if __name__ == '__main__':
    user_interface = ui()
    while user_interface:
        # The loop might return a different user interface
        # object if the user changes worlds
        user_interface = user_interface.default_loop()