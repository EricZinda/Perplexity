import logging
from perplexity.generation import english_for_delphin_variable
from perplexity.tree import find_predicate, predication_from_index, \
    find_predicate_from_introduced
from perplexity.utilities import parse_predication_name, sentence_force_from_tree_info


# Implements the response for a given tree
def respond_to_mrs_tree(tree, solutions, error):
    # Tree can be None if we didn't have one of the
    # words in the vocabulary
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
            wh_predication = find_predicate(tree["Tree"], "which_q")

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
            # This was a "WH" question. Return the values of the variable
            # asked about from the solution
            # The phrase was "true" if there was at least one answer
            if len(solutions) > 0:
                # Build an error term that we can use to call generate_message
                # to get the response
                index_predication = find_predicate_from_introduced(tree["Tree"], tree["Index"])
                wh_variable = wh_predication[1]
                answer_items = []
                for solution in solutions:
                    answer_items.append(solution.get_variable(wh_variable))

                message = generate_message(tree, [-1, ["answerWithList", index_predication, answer_items]])
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
def generate_message(tree_info, error_term):
    error_predicate_index = error_term[0]
    error_arguments = error_term[1]
    error_constant = error_arguments[0]

    if error_constant == "xIsNotY":
        arg1 = english_for_delphin_variable(error_predicate_index, error_arguments[1], tree_info)
        arg2 = error_arguments[2]
        return f"{arg1} is not {arg2}"

    elif error_constant == "adjectiveDoesntApply":
        arg1 = error_arguments[1]
        arg2 = english_for_delphin_variable(error_predicate_index, error_arguments[2], tree_info)
        return f"{arg2} is not {arg1}"

    elif error_constant == "doesntExist":
        arg1 = english_for_delphin_variable(error_predicate_index, error_arguments[1], tree_info)
        return f"There isn't '{arg1}' in the system"

    elif error_constant == "dontKnowPronoun":
        arg1 = english_for_delphin_variable(error_predicate_index, error_arguments[1], tree_info)
        return f"I don't know who '{arg1}' is"

    elif error_constant == "dontKnowActor":
        arg1 = english_for_delphin_variable(error_predicate_index, error_arguments[1], tree_info)
        return f"I don't know who '{arg1}' is"

    elif error_constant == "cantDo":
        arg1 = error_arguments[1]
        arg2 = english_for_delphin_variable(error_predicate_index, error_arguments[2], tree_info)
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

    elif error_constant == "formNotUnderstood":
        predication = predication_from_index(tree_info, error_predicate_index)
        parsed_predicate = parse_predication_name(predication[0])

        if error_arguments[1] == "notHandled":
            # The event had something that the predication didn't know how to handle
            # See if there is information about where it came from
            if "Originator" in error_arguments[2][1]:
                originator_index = error_arguments[2][1]["Originator"]
                originator_predication = predication_from_index(tree_info, originator_index)
                parsed_originator = parse_predication_name(originator_predication[0])
                return f"I don't understand the way you are using '{parsed_originator['Lemma']}' with '{parsed_predicate['Lemma']}'"

        return f"I don't understand the way you are using: {parsed_predicate['Lemma']}"

    elif error_constant == "moreThanOneInScope":
        arg1 = english_for_delphin_variable(error_predicate_index, error_arguments[1], tree_info)
        return f"There is more than one '{arg1}' where you are"

    elif error_constant == "answerWithList":
        answer_predication = error_arguments[1]
        answer_items = error_arguments[2]

        if len(answer_items) > 0:
            message = ""

            if answer_predication[0] == "loc_nonsp":
                # if "loc_nonsp" is the "verb", it means the phrase was
                # "Where is YYY?", so only return the "best" answer, which
                # is the most specific one
                best_answer = ""
                for answer_item in answer_items:
                    current_answer = str(answer_item.name)
                    if len(current_answer) > len(best_answer):
                        best_answer = current_answer
                message = f"in {best_answer}"

            else:
                for answer_item in answer_items:
                    message += str(answer_item) + "\n"

            return message
        else:
            return ""

    else:
        return error_term


pipeline_logger = logging.getLogger('Pipeline')
