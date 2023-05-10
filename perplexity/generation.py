import logging
from perplexity.tree import walk_tree_predications_until, find_predications_using_variable, is_last_fw_seq
from perplexity.utilities import parse_predication_name


# Given the index where an error happened and a variable,
# return what that variable "is" up to that point, in English
def english_for_delphin_variable(failure_index, variable, tree_info, default_a_quantifier=True):
    if isinstance(variable, list):
        if variable[0] == "AtPredication":
            # Use the English for this variable as if the
            # error happened at the specified predication
            # instead of where it really happened
            failure_index = variable[1].index
            logger.debug(f"error predication index is: {failure_index}")
            variable = variable[2]

        elif variable[0] == "AfterFullPhrase":
            failure_index = 100000000
            variable = variable[1]

    # This function will be called for every predication in the MRS
    # as we walk it in execution order
    def record_predications_until_failure_index(predication):
        # Once we have hit the index where the failure happened, stop
        if predication.index == failure_index:
            logger.debug(f"(stop and ignore) error predication index {predication.index}: {predication.name}")
            return False
        else:
            logger.debug(f"(refine NLG) error predication index {predication.index}: {predication.name}")

            # See if this predication can contribute anything to the
            # description of the variable we are describing. If so,
            # collect it in nlg_data
            refine_nlg_with_predication(tree_info, variable, predication, nlg_data)
            return None

    nlg_data = {}

    # WalkTreeUntil() walks the predications in mrs["Tree"] and calls
    # the function record_predications_until_failure_index(), until hits the
    # failure_index position
    walk_tree_predications_until(tree_info["Tree"], record_predications_until_failure_index)

    # Take the data we gathered and convert to English
    logger.debug(f"NLG data for {variable}: {nlg_data}")
    return convert_to_english(nlg_data, default_a_quantifier)


# See if this predication in any way contributes words to
# the variable specified. Put whatever it contributes in nlg_data
def refine_nlg_with_predication(tree_info, variable, predication, nlg_data):
    # Parse the name of the predication to find out its
    # part of speech (POS) which could be a noun ("n"),
    # quantifier ("q"), etc.
    parsed_predication = parse_predication_name(predication.name)

    # If the predication has this variable as its first argument,
    # it either *introduces* it, or is quantifying it
    if predication.introduced_variable() == variable:
        if parsed_predication["Pos"] == "q":
            if parsed_predication["Surface"] is True:
                if parsed_predication["Lemma"] not in ["which"]:
                    # It is quantifying it
                    nlg_data["Quantifier"] = parsed_predication["Lemma"].replace("+", " ")
            else:
                nlg_data["Quantifier"] = "<none>"

        else:
            if parsed_predication["Surface"] is True:
                # It is introducing it, thus it is the "main" description
                # of the variable, usually a noun predication
                nlg_data["Topic"] = parsed_predication["Lemma"].replace("+", " ")
            else:
                # Some abstract predications *should* contribute to the
                # English description of a variable
                if parsed_predication["Lemma"] == "pron":
                    nlg_data["Topic"] = pronoun_from_variable(tree_info, variable)

                elif parsed_predication["Lemma"] == "quoted":
                    nlg_data["Topic"] = predication.args[0].replace("\\\\>root111", "/").replace("\\\\>", "/")

                elif parsed_predication["Lemma"] in ["place", "thing"]:
                    nlg_data["Topic"] = parsed_predication["Lemma"]

                elif parsed_predication["Lemma"] == "fw_seq":
                    string_list = []
                    for arg_index in range(1, len(predication.arg_names)):
                        if predication.args[arg_index][0] == "i":
                            # Use 1000 to make sure we go through the whole tree
                            string_list.append(english_for_delphin_variable(1000, predication.args[arg_index], tree_info, default_a_quantifier=False))

                        elif predication.args[arg_index][0] == "x":
                            # Use 1000 to make sure we go through the whole tree
                            string_list.append(english_for_delphin_variable(1000, predication.args[arg_index], tree_info, default_a_quantifier=False))

                    # If the only thing consuming the introduced variable are other fw_seq predications
                    # Then this is not the final fw_seq, so don't put quotes around it
                    if is_last_fw_seq(tree_info["Tree"], predication):
                        nlg_data["Topic"] = f"'{' '.join(string_list)}'"
                    else:
                        nlg_data["Topic"] = f"{' '.join(string_list)}"

    # Assume that adjectives that take the variable as their first argument
    # are adding an adjective modifier to the phrase
    elif parsed_predication["Pos"] == "a" and predication.args[1] == variable:
        if "Modifiers" not in nlg_data:
            nlg_data["Modifiers"] = []

        nlg_data["Modifiers"].append(parsed_predication["Lemma"].replace("+", " "))

    elif parsed_predication["Pos"] == "p" and predication.args[1] == variable:
        if "PostModifiers" not in nlg_data:
            nlg_data["PostModifiers"] = []

        if len(predication.args) == 3:
            prep_english = english_for_delphin_variable(99, predication.args[2], tree_info)
            nlg_data["PostModifiers"].append(parsed_predication["Lemma"].replace("+", " ") + " " + prep_english)
        elif len(predication.args) == 2:
            nlg_data["PostModifiers"].append(parsed_predication["Lemma"].replace("+", " "))
        else:
            return

    elif parsed_predication["Lemma"] == "card" and predication.args[2] == variable:
        if "Modifiers" not in nlg_data:
            nlg_data["Modifiers"] = []

        nlg_data["Modifiers"].append(predication.args[0])


pronouns = {1: {"sg": "I",
                "pl": "we"},
            2: {"sg": "you",
                "pl": "you"},
            3: {"sg": "he/she",
                "pl": "they"}
            }


def pronoun_from_variable(tree_info, variable):
    mrs_variable = tree_info["Variables"][variable]
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
def convert_to_english(nlg_data, default_a_quantifier):
    phrase = ""

    if "Quantifier" in nlg_data:
        if nlg_data["Quantifier"] != "<none>":
            phrase += nlg_data["Quantifier"] + " "
    elif default_a_quantifier:
        phrase += "a "

    if "Modifiers" in nlg_data:
        # " ".join() takes a list and turns it into a string
        # with the string " " between each item
        phrase += " ".join(nlg_data["Modifiers"]) + " "

    if "Topic" in nlg_data:
        phrase += nlg_data["Topic"] + " "
    else:
        phrase += "thing "

    if "PostModifiers" in nlg_data:
        phrase += " ".join(nlg_data["PostModifiers"]) + " "

    return phrase.strip()


logger = logging.getLogger('Generation')
pipeline_logger = logging.getLogger('Pipeline')
