import logging

from perplexity.tree import walk_tree_until, index_of_predication
from perplexity.utilities import parse_predication_name


# Given the index where an error happened and a variable,
# return what that variable "is" up to that point, in English
def english_for_delphin_variable(failure_index, variable, mrs):
    if isinstance(variable, list):
        if variable[0] == "AtPredication":
            failure_index = index_of_predication(mrs, variable[1])
            variable = variable[2]

    # Integers can't be passed by reference in Python, so we need to pass
    # the current index in a list so it can be changed as we iterate
    current_predication_index = [1]

    # This function will be called for every predication in the MRS
    # as we walk it in execution order
    def record_predications_until_failure_index(predication):
        logger.debug(f"error predication index {current_predication_index[0]}: {predication[0]}")

        # Once we have hit the index where the failure happened, stop
        if current_predication_index[0] == failure_index:
            return False
        else:
            # See if this predication can contribute anything to the
            # description of the variable we are describing. If so,
            # collect it in nlg_data
            refine_nlg_with_predication(mrs, variable, predication, nlg_data)
            current_predication_index[0] = current_predication_index[0] + 1
            return None

    nlg_data = {}

    # WalkTreeUntil() walks the predications in mrs["Tree"] and calls
    # the function record_predications_until_failure_index(), until hits the
    # failure_index position
    walk_tree_until(mrs["Tree"], record_predications_until_failure_index)

    # Take the data we gathered and convert to English
    logger.debug(f"NLG data for {variable}: {nlg_data}")
    return convert_to_english(nlg_data)


# See if this predication in any way contributes words to
# the variable specified. Put whatever it contributes in nlg_data
def refine_nlg_with_predication(mrs, variable, predication, nlg_data):
    # Parse the name of the predication to find out its
    # part of speech (POS) which could be a noun ("n"),
    # quantifier ("q"), etc.
    parsed_predication = parse_predication_name(predication[0])

    # If the predication has this variable as its first argument,
    # it either *introduces* it, or is quantifying it
    if predication[1] == variable:
        if parsed_predication["Pos"] == "q":
            if parsed_predication["Surface"] is True:
                if parsed_predication["Lemma"] not in ["which"]:
                    # It is quantifying it
                    nlg_data["Quantifier"] = parsed_predication["Lemma"]
            else:
                nlg_data["Quantifier"] = "<none>"

        else:
            if parsed_predication["Surface"] is True:
                # It is introducing it, thus it is the "main" description
                # of the variable, usually a noun predication
                nlg_data["Topic"] = parsed_predication["Lemma"]
            else:
                # Some abstract predications *should* contribute to the
                # English description of a variable
                if parsed_predication["Lemma"] == "pron":
                    nlg_data["Topic"] = pronoun_from_variable(mrs, variable)

    # Assume that adjectives that take the variable as their first argument
    # are adding an adjective modifier to the phrase
    elif parsed_predication["Pos"] == "a" and predication[2] == variable:
        if "Modifiers" not in nlg_data:
            nlg_data["Modifiers"] = []

        nlg_data["Modifiers"].append(parsed_predication["Lemma"])


pronouns = {1: {"sg": "I",
                "pl": "we"},
            2: {"sg": "you",
                "pl": "you"},
            3: {"sg": "he/she",
                "pl": "they"}
            }


def pronoun_from_variable(mrs, variable):
    mrs_variable = mrs["Variables"][variable]
    if "PERS" in mrs_variable:
        person = int(mrs_variable["PERS"])
    else:
        person = 1

    if "NUM" in mrs_variable:
        number = mrs_variable["NUM"]
    else:
        # "sg" is singular in MRS
        number = "sg"

    return pronouns[person][number]


# Takes the information gathered in the nlg_data dictionary
# and converts it, in a very simplistic way, to English
def convert_to_english(nlg_data):
    phrase = ""

    if "Quantifier" in nlg_data:
        if nlg_data["Quantifier"] != "<none>":
            phrase += nlg_data["Quantifier"] + " "
    else:
        phrase += "a "

    if "Modifiers" in nlg_data:
        # " ".join() takes a list and turns it into a string
        # with the string " " between each item
        phrase += " ".join(nlg_data["Modifiers"]) + " "

    if "Topic" in nlg_data:
        phrase += nlg_data["Topic"]
    else:
        phrase += "thing"

    return phrase


logger = logging.getLogger('Generation')
pipeline_logger = logging.getLogger('Pipeline')
