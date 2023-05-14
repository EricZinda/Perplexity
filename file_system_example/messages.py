import logging

import perplexity.messages
from perplexity.generation import english_for_delphin_variable
from perplexity.set_utilities import append_if_unique, in_equals
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

    if error_constant == "adjectiveDoesntApply":
        arg1 = error_arguments[1]
        arg2 = english_for_delphin_variable(error_predicate_index, error_arguments[2], tree_info)
        return f"{arg2} is not {arg1}"

    elif error_constant == "cantDo":
        arg1 = error_arguments[1]
        arg2 = english_for_delphin_variable(error_predicate_index, error_arguments[2], tree_info)
        return f"I can't {arg1} {arg2}"

    elif error_constant == "dontKnowActor":
        arg1 = english_for_delphin_variable(error_predicate_index, error_arguments[1], tree_info)
        arg1 = arg1.strip("'\"")
        return f"I don't know who '{arg1}' is"

    elif error_constant == "notFound":
        arg1 = english_for_delphin_variable(error_predicate_index, error_arguments[1], tree_info)
        arg1 = arg1.strip("'\"")
        return f"'{arg1}' was not found"

    elif error_constant == "thingHasNoLocation":
        arg1 = english_for_delphin_variable(error_predicate_index, error_arguments[1], tree_info)
        arg2 = english_for_delphin_variable(error_predicate_index, error_arguments[2], tree_info)
        return f"{arg1} is not in {arg2}"

    elif error_constant == "thingIsNotContainer":
        arg1 = english_for_delphin_variable(error_predicate_index, error_arguments[1], tree_info)
        return f"{arg1} can't contain things"

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
