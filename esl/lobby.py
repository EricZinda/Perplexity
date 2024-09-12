import logging
import os
import perplexity.messages
from perplexity.response import RespondOperation, ResponseLocation
from perplexity.state import LoadException, State
from perplexity.system_vocabulary import system_vocabulary
from perplexity.user_interface import UserInterface
from perplexity.vocabulary import Predication
from perplexity.world_registry import LoadWorldOperation

vocabulary = system_vocabulary()

# "Say 'restart' to try again
#
# Only allow:
# "restart"
@Predication(vocabulary,
             names=["_restart_v_1"],
             phrases={
                 "restart":  {'SF': 'prop-or-ques', 'TENSE': 'tensed', 'MOOD': 'indicative', 'PROG': '-', 'PERF': '-'}
             },
             properties=[ {'SF': 'prop-or-ques', 'TENSE': 'tensed', 'MOOD': 'indicative', 'PROG': '-', 'PERF': '-'}]
             )
def _restart_v_1(context, state, e_binding, i_binding_1, i_binding_2):
    yield state.record_operations([LoadWorldOperation("esl"),
                                   RespondOperation("Restarting ...", location=ResponseLocation.first, show_if_last_phrase=True)])


def in_scope_initialize(state):
    return {}


def in_scope(initial_data, context, state, value):
    return False


error_priority_dict = {
    "defaultPriority": 1000,
    # This is just used when sorting to indicate no error, i.e. success.
    # Nothing should be higher because higher is used for phase 2 errors
    "success": 10000000
}


def error_priority(error_string):
    system_priority = perplexity.messages.error_priority(error_string)
    if system_priority is not None:
        return system_priority
    else:
        # Must be a message from our code
        error_constant = error_string[1][0]
        priority = error_priority_dict.get(error_constant, error_priority_dict["defaultPriority"])
        priority += error_string[2] * error_priority_dict["success"]
        return priority


# Generates all the responses that predications can
# return when an error occurs
def generate_custom_message(state, tree_info, error_term):
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

    # See if the system can handle converting the error
    # to a message first except for those we are overriding
    # Override these
    if error_constant == "unknownWords":
        return "Let's try that again ..."

    else:
        system_message = perplexity.messages.generate_message(tree_info, error_term)
        if system_message is not None:
            return system_message

    # No custom message, just return the raw error for debugging
    return str(error_term)


def reset():
    initial_state = State([])
    return initial_state


class EslEvents(object):
    def interaction_end(self, ui, interaction_records, last_phrase_response):
        if last_phrase_response == "":
            return [(perplexity.response.ResponseLocation.last, default_message)]

    def world_new(self):
        return [(perplexity.response.ResponseLocation.first, default_message)]


default_message = "Say 'restart' to try again."


def ui(loading_info=None, file=None, user_output=None, debug_output=None):
    scriptPath = os.path.dirname(os.path.realpath(__file__))
    best_parses_file = os.path.join(scriptPath, "lobby.bestparse")
    loaded_state = None
    if loading_info is not None:
        if loading_info.get("Version", None) != 1:
            raise LoadException()

        if file is not None:
            loaded_state = load_world_state(file)

        message = ""

    else:
        message = ""

    vocabulary.synonyms = {
    }

    ui = UserInterface("lobby",
                       reset,
                       vocabulary,
                       message_function=generate_custom_message,
                       error_priority_function=error_priority,
                       scope_function=in_scope,
                       scope_init_function=in_scope_initialize,
                       loaded_state=loaded_state,
                       user_output=user_output,
                       debug_output=debug_output,
                       best_parses_file=best_parses_file,
                       events=EslEvents())

    ui.user_output(message)
    return ui


def hello_world():
    user_interface = ui()
    user_interface.user_output(user_interface.output_sorted_responses(user_interface.events.world_new()))

    while user_interface:
        user_interface = user_interface.default_loop()


pipeline_logger = logging.getLogger('Pipeline')


if __name__ == '__main__':
    # ShowLogging("Pipeline")
    # ShowLogging("ChatGPT")
    # ShowLogging("Testing")
    # ShowLogging("Execution")
    # ShowLogging("Generation")
    # ShowLogging("SString")
    # ShowLogging("UserInterface")
    # ShowLogging("Determiners")
    # ShowLogging("SolutionGroups")
    # ShowLogging("Transformer")

    hello_world()
