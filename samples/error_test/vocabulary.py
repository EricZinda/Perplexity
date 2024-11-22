from perplexity.state import LoadException, State
import perplexity.system_vocabulary
from perplexity.user_interface import UserInterface
from perplexity.utilities import ShowLogging
from perplexity.vocabulary import Predication


vocabulary = perplexity.system_vocabulary.system_vocabulary()


@Predication(vocabulary, names=["_no_a_1"])
def _no_a_1(context, state, i_binding, h_binding):
    yield state


@Predication(vocabulary,
             names=["unknown"],
             phrases={
                "no?": {'SF': 'ques'}
             },
             properties=[{'SF': 'ques'}])
def unknown_question(context, state, e_binding, u_binding):
    if False:
        yield None


@Predication(vocabulary,
             names=["solution_group_unknown"],
             properties_from=unknown_question,
             handles_interpretations=unknown_question)
def unknown_question_group(context, state_list, e_introduced_list, u_variable_group):
    if False:
        yield None


@Predication(vocabulary,
             names=["unknown"],
             phrases={
                "no": {'SF': 'prop'}
             },
             properties=[{'SF': 'prop'}])
def unknown(context, state, e_binding, u_binding):
    if False:
        yield None


# Make sure that reporting an error from a solution group handler, actually gets through
# the system, even if there are other solution group handlers
# Saying 'No' to this world should attempt to run 2 solution group handlers
# (unknown_question_group and unknown_group, in that order).  The first will fail with
# formNotUnderstood since it is a question, but that shouldn't stop the second from reporting its error
@Predication(vocabulary,
             names=["solution_group_unknown"],
             properties_from=unknown,
             handles_interpretations=unknown)
def unknown_group(context, state_list, e_introduced_list, u_variable_group):
    context.report_error(["errorText", "Test"])
    if False:
        yield None


def error_test_reset():
    return State(objects=[])


def error_test_main():
    user_interface = error_test_ui()
    while user_interface:
        user_interface = user_interface.default_loop()


def error_test_ui(loading_info=None, file=None, user_output=None, debug_output=None):
    if loading_info is not None:
        if loading_info.get("Version", None) != 1:
            raise LoadException()

        if file is not None:
            raise LoadException()

    user_interface = UserInterface("error_test",
                                   error_test_reset,
                                   vocabulary,
                                   user_output=user_output,
                                   debug_output=debug_output)
    return user_interface


if __name__ == '__main__':
    ShowLogging("Pipeline")

    error_test_main()
