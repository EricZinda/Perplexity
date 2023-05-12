from perplexity.generation import english_for_delphin_variable
from perplexity.tree import predication_from_index
from perplexity.utilities import parse_predication_name


def generate_message(tree_info, error_term):
    error_predicate_index = error_term[0]
    error_arguments = error_term[1]
    error_constant = error_arguments[0] if error_arguments is not None else "no error set"

    if error_constant == "answerWithList":
        answer_items = error_arguments[2]

        if len(answer_items) > 0:
            message = "\n".join([str(answer_item) for answer_item in answer_items])
            return message
        else:
            return ""

    elif error_constant == "beMoreSpecific":
        return f"Could you be more specific?"

    elif error_constant == "doesntExist":
        arg1 = english_for_delphin_variable(error_predicate_index, error_arguments[1], tree_info)
        arg1 = arg1.strip("'\"")
        return f"There isn't '{arg1}' in the system"

    elif error_constant == "formNotUnderstood":
        predication = predication_from_index(tree_info, error_predicate_index)
        parsed_predicate = parse_predication_name(predication.name)

        if error_arguments[1] == "notHandled":
            # The event had something that the predication didn't know how to handle
            # See if there is information about where it came from
            if "Originator" in error_arguments[2][1]:
                originator_index = error_arguments[2][1]["Originator"]
                originator_predication = predication_from_index(tree_info, originator_index)
                parsed_originator = parse_predication_name(originator_predication.name)
                return f"I don't understand the way you are using '{parsed_originator['Lemma']}' with '{parsed_predicate['Lemma']}'"

        return f"I don't understand the way you are using: {parsed_predicate['Lemma']}"

    elif error_constant == "lessThan":
        arg1 = english_for_delphin_variable(error_predicate_index, error_arguments[1], tree_info, default_a_quantifier=False)
        arg2 = error_arguments[2]
        return f"There are less than {arg2} {arg1}"

    elif error_constant == "moreThan":
        arg1 = english_for_delphin_variable(error_predicate_index, error_arguments[1], tree_info, default_a_quantifier=False)
        return f"There are more than {arg1}"

    elif error_constant == "moreThan1":
        arg1 = english_for_delphin_variable(error_predicate_index, error_arguments[1], tree_info, default_a_quantifier=False)
        return f"There is more than one {arg1}"

    elif error_constant == "moreThanN":
        arg1 = english_for_delphin_variable(error_predicate_index, error_arguments[1], tree_info, default_a_quantifier=False)
        arg2 = error_arguments[2]
        return f"There is more than {arg2} {arg1}"

    elif error_constant == "notTrueForAll":
        arg1 = english_for_delphin_variable(error_predicate_index, error_arguments[1], tree_info, default_a_quantifier=False)
        return f"That isn't true for all {arg1}"

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
        return None
