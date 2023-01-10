import logging

from perplexity.generation import english_for_delphin_variable
from perplexity.tree import find_predicate
from perplexity.utilities import parse_predication_name, sentence_force_from_tree_info


# Implements the response for a given tree
def respond_to_mrs_tree(tree, solutions, error):
    if tree is None:
        message = generate_message(None, error)
        return message

    sentence_force_type = sentence_force_from_tree_info(tree)
    if sentence_force_type == "prop":
        # This was a proposition, so the user only expects
        # a confirmation or denial of what they said.
        # The phrase was "true" if there was at least one answer
        if len(solutions) > 0:
            return "Yes, that is true."
        else:
            message = generate_message(tree, error)
            return message

    elif sentence_force_type == "ques":
        # See if this is a "WH" type question
        wh_predication = find_predicate(tree["Tree"], "_which_q")
        if wh_predication is None:
            # This was a simple question, so the user only expects
            # a yes or no.
            # The phrase was "true" if there was at least one answer
            if len(solutions) > 0:
                return "Yes."
            else:
                message = generate_message(tree, error)
                return message
        else:
            # This was a "WH" question
            # return the values of the variable asked about
            # from the solution
            # The phrase was "true" if there was at least one answer
            if len(solutions) > 0:
                wh_variable = wh_predication[1]
                message = ""
                for solution in solutions:
                    message += str(solution.get_variable(wh_variable)) + "\n"

                return message
            else:
                message = generate_message(tree, error)
                return message

    elif sentence_force_type == "comm":
        # This was a command so, if it works, just say so
        # We'll get better errors and messages in upcoming sections
        if len(solutions) > 0:
            return "Done!"
        else:
            message = generate_message(tree, error)
            return message


# Generates all the responses that predications can return when an error
# occurs
#
# error_term is of the form: [index, error] where "error" is another
# list like: ["name", arg1, arg2, ...]. The first item is the error
# constant (i.e. its name). What the args mean depends on the error
def generate_message(mrs, error_term):
    error_predicate_index = error_term[0]
    error_arguments = error_term[1]
    error_constant = error_arguments[0]

    if error_constant == "xIsNotY":
        arg1 = english_for_delphin_variable(error_predicate_index, error_arguments[1], mrs)
        arg2 = error_arguments[2]
        return f"{arg1} is not {arg2}"

    elif error_constant == "adjectiveDoesntApply":
        arg1 = error_arguments[1]
        arg2 = english_for_delphin_variable(error_predicate_index, error_arguments[2], mrs)
        return f"{arg2} is not {arg1}"

    elif error_constant == "doesntExist":
        arg1 = english_for_delphin_variable(error_predicate_index, error_arguments[1], mrs)
        return f"There isn't '{arg1}' in the system"

    elif error_constant == "dontKnowPronoun":
        arg1 = english_for_delphin_variable(error_predicate_index, error_arguments[1], mrs)
        return f"I don't know who '{arg1}' is"

    elif error_constant == "dontKnowActor":
        arg1 = english_for_delphin_variable(error_predicate_index, error_arguments[1], mrs)
        return f"I don't know who '{arg1}' is"

    elif error_constant == "cantDo":
        arg1 = error_arguments[1]
        arg2 = english_for_delphin_variable(error_predicate_index, error_arguments[2], mrs)
        return f"I can't {arg1} {arg2}"

    elif error_constant == "unknownWords":
        lemmas_unknown = []
        lemmas_form_known = []
        for unknown_predication in error_arguments[1]:
            parsed_predicate = parse_predication_name(unknown_predication[0])
            if unknown_predication[3]:
                lemmas_form_known.append(parsed_predicate["Lemma"])
            else:
                lemmas_unknown.append(parsed_predicate["Lemma"])

        answers = []
        if len(lemmas_unknown) > 0:
            answers.append(f"I don't know the words: {', '.join(lemmas_unknown)}")

        if len(lemmas_form_known) > 0:
            answers.append(f"I don't know the way you used: {', '.join(lemmas_form_known)}")

        return " and ".join(answers)

    else:
        return error_term


pipeline_logger = logging.getLogger('Pipeline')
