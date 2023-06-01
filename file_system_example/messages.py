import logging

import perplexity.messages
from perplexity.generation import english_for_delphin_variable
from perplexity.set_utilities import append_if_unique, in_equals
from perplexity.sstring import sstringify, s
from perplexity.tree import find_predication, predication_from_index, \
    find_predication_from_introduced
from perplexity.utilities import parse_predication_name, sentence_force, at_least_one_generator


# Generates all the responses that predications can
# return when an error occurs
def generate_message(tree_info, error_term):
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
    arg_length = len(error_arguments)
    arg1 = error_arguments[1] if arg_length > 1 else None
    arg2 = error_arguments[2] if arg_length > 2 else None
    arg3 = error_arguments[3] if arg_length > 3 else None

    if error_constant == "adjectiveDoesntApply":
        return s("{A arg2} {'is':<arg2} not {*arg1}", tree_info)

    elif error_constant == "cantDo":
        return s("I can't {*arg1:<'I'} {arg2}", tree_info)

    elif error_constant == "dontKnowActor":
        return s("I don't know who '{arg1}' is", tree_info)

    elif error_constant == "notFound":
        return s("{arg1} was not found", tree_info)

    elif error_constant == "thingHasNoLocation":
        return s("{arg1} is not in {arg2}", tree_info)

    elif error_constant == "thingIsNotContainer":
        return s("{arg1} can't contain things", tree_info)

    else:
        return str(error_term)


def error_priority(error_string):
    global error_priority_dict
    if error_string is None:
        return 0

    else:
        error_constant = error_string[1][0]
        priority = error_priority_dict.get(error_constant, error_priority_dict["defaultPriority"])
        if error_constant == "unknownWords":
            priority -= len(error_string[1][1])

        return priority


# Highest numbers are best errors to return
# The absolute value of number doesn't mean anything, they are just for sorting
# The defaultPriority key is the default value for errors that aren't explicitly listed
error_priority_dict = {
    # Unknown words error should only be shown if
    # there are no other errors, AND the number
    # of unknown words is subtracted from it so
    # lower constants should be defined below this:
    # "unknownWordsMin": 800,
    "unknownWords": 900,
    # Slightly better than not knowing the word at all
    "formNotUnderstood": 901,
    "defaultPriority": 1000,

    # This is just used when sorting to indicate no error, i.e. success.
    # Nothing should be higher
    "success": 10000000
}

pipeline_logger = logging.getLogger('Pipeline')
