import logging

import perplexity.messages
from perplexity.generation import english_for_delphin_variable
from perplexity.set_utilities import append_if_unique, in_equals
from perplexity.tree import find_predication, predication_from_index, \
    find_predication_from_introduced
from perplexity.utilities import parse_predication_name, sentence_force, at_least_one_generator

# Implements the response for a given tree
# yields: response, solution_group that generated the response
# In scenarios where there is an open solution group (meaning like "files are ..." where there is an initial solution that will
# grow), this will yield once for every additional solution
def respond_to_mrs_tree(tree, solution_groups, error):
    # Tree can be None if we didn't have one of the
    # words in the vocabulary
    if tree is None:
        message = generate_message(None, error)
        yield message, None
        return

    sentence_force_type = sentence_force(tree["Variables"])
    if sentence_force_type == "prop":
        # This was a proposition, so the user only expects
        # a confirmation or denial of what they said.
        # The phrase was "true" if there was at least one answer
        if solution_groups is not None:
            yield "Yes, that is true.", next(solution_groups)
            return

        else:
            message = generate_message(tree, error)
            yield message, None
            return

    elif sentence_force_type == "ques":
        # See if this is a "WH" type question
        wh_predication = find_predication(tree["Tree"], "_which_q")
        if wh_predication is None:
            wh_predication = find_predication(tree["Tree"], "which_q")

        if wh_predication is None:
            # This was a simple question, so the user only expects
            # a yes or no.
            # The phrase was "true" if there was at least one answer
            if solution_groups is not None:
                yield "Yes.", next(solution_groups)
                return

            else:
                message = generate_message(tree, error)
                yield message, None
                return

        else:
            # This was a "WH" question. Return the values of the variable
            # asked about from the solution
            # The phrase was "true" if there was at least one answer
            if solution_groups is not None:
                # Build an error term that we can use to call generate_message
                # to get the response
                index_predication = find_predication_from_introduced(tree["Tree"], tree["Index"])
                wh_variable = wh_predication.introduced_variable()

                # Get unique items from all solutions
                answer_items = set()
                solution_group = next(solution_groups)
                response = ""
                for solution in solution_group:
                    binding = solution.get_binding(wh_variable)
                    if binding.variable.combinatoric:
                        value_set = ((value, ) for value in binding.value)
                        if value_set not in answer_items:
                            answer_items.add(value_set)
                            yield generate_message(tree, [-1, ["answerWithList", index_predication, [value_set]]]), [solution]

                    else:
                        if binding.value not in answer_items:
                            answer_items.add(binding.value)
                            yield generate_message(tree, [-1, ["answerWithList", index_predication, [binding.value]]]), [solution]

            else:
                message = generate_message(tree, error)
                yield message, None
                return

    elif sentence_force_type == "comm":
        # This was a command so, if it works, just say so
        # We'll get better errors and messages in upcoming sections
        if solution_groups is not None:
            yield "Done!", next(solution_groups)

        else:
            message = generate_message(tree, error)
            yield message, None


# Generates all the responses that predications can return when an error
# occurs
#
# error_term is of the form: [index, error] where "error" is another
# list like: ["name", arg1, arg2, ...]. The first item is the error
# constant (i.e. its name). What the args mean depends on the error
def generate_message(tree_info, error_term):
    system_message = perplexity.messages.generate_message(tree_info, error_term)
    if system_message is not None:
        return system_message

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

    elif error_constant == "xIsNotY":
        arg1 = english_for_delphin_variable(error_predicate_index, error_arguments[1], tree_info)
        arg2 = english_for_delphin_variable(error_predicate_index, error_arguments[2], tree_info)
        return f"{arg1} is not {arg2}"

    elif error_constant == "xIsNotYValue":
        arg1 = english_for_delphin_variable(error_predicate_index, error_arguments[1], tree_info)
        arg2 = error_arguments[2]
        return f"{arg1} is not {arg2}"

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
