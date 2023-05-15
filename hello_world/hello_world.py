from perplexity.execution import report_error
from perplexity.generation import english_for_delphin_variable
from perplexity.state import State
from perplexity.user_interface import UserInterface
from perplexity.vocabulary import Vocabulary
import perplexity.messages


vocabulary = Vocabulary()


def file_n_of(state, x_binding, i_binding):
    if x_binding.value is None:
        yield state.set_x(("file1.txt", ))
    elif x_binding.value[0] == "file1.txt":
        yield state
    else:
        report_error(["notAThing", x_binding.value, x_binding.variable.name])
        return False


# Generates all the responses that predications can
# return when an error occurs
def generate_custom_message(tree_info, error_term):
    # See if the system can handle converting the error
    # to a message first
    system_message = perplexity.messages.generate_message(tree_info, error_term)
    if system_message is not None:
        return system_message

    # error_term is of the form: [index, error] where "error" is another
    # list like: ["name", arg1, arg2, ...]. The first item is the error
    # constant (i.e. its name). What the args mean depends on the error
    error_predicate_index = error_term[0]
    error_arguments = error_term[1]
    error_constant = error_arguments[0] if error_arguments is not None else "no error set"

    if error_constant == "notAThing":
        arg1 = error_arguments[1]
        # english_for_delphin_variable() converts a variable name like 'x3' into the english words
        # that it represented in the MRS
        arg2 = english_for_delphin_variable(error_predicate_index, error_arguments[2], tree_info)
        return f"{arg1} is not {arg2}"

    else:
        # No custom message, just return the raw error for debugging
        return str(error_term)


def reset():
    return State([])


def hello_world():
    user_interface = UserInterface(reset, vocabulary, generate_custom_message)

    while True:
        user_interface.interact_once()
        print()


if __name__ == '__main__':
    hello_world()
