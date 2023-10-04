import copy
import enum
import logging
import inflect
from perplexity.tree import walk_tree_predications_until, is_last_fw_seq, rewrite_tree_predications, \
    find_predication_from_introduced
from perplexity.utilities import parse_predication_name


class PluralMode(enum.Enum):
    plural = 0,
    singular = 1,
    as_is = 2


def is_plural_word(word):
    # Returns false if word is already singular
    return p.singular_noun(word) is not False


def change_to_plural_mode(singular_word, plural_mode):
    if plural_mode == PluralMode.singular:
        return singular_word
    elif plural_mode == PluralMode.plural:
        return p.plural(singular_word)
    else:
        return singular_word


def english_for_delphin_variable(failure_index, variable, tree_info, plural=None, determiner=None, reverse_pronouns=False):
    def record_predications_until_failure_index(predication, index_by_ref, nlg_data, local_tree_info):
        nonlocal tree_info
        # Once we have hit the index where the failure happened, stop
        if predication.index == failure_index:
            logger.debug(f"(stop and ignore) error predication index {predication.index}: {predication.name}")
            # Stop recursing by returning the predication
            return predication

        else:
            logger.debug(f"(refine NLG) error predication index {predication.index}: {predication.name}")

            if predication.name == "neg":
                if find_predication_from_introduced(predication.args[1], variable) is not None:
                    # the variable is introduced in this subtree so it should not have "not" added
                    def neg_nlg_func(predication, index_by_ref):
                        return record_predications_until_failure_index(predication, index_by_ref, nlg_data, local_tree_info)

                    return rewrite_tree_predications(predication.args[1], neg_nlg_func, index_by_ref)

                else:
                    neg_nlg_data = {"Quantifier": "<none>",
                                    "Topic": ""}
                    nlg_data["NotScope"] = neg_nlg_data

                    subtree_info = copy.deepcopy(local_tree_info)
                    subtree_info["Tree"] = predication.args[1]

                    def neg_nlg_func(predication, index_by_ref):
                        return record_predications_until_failure_index(predication, index_by_ref, neg_nlg_data, subtree_info)

                    value = rewrite_tree_predications(predication.args[1], neg_nlg_func, index_by_ref)
                    return value

            else:
                # See if this predication can contribute anything to the
                # description of the variable we are describing. If so,
                # collect it in nlg_data
                refine_nlg_with_predication(local_tree_info, variable, predication, nlg_data)
                return None

    nlg_data = {"ReversePronouns": reverse_pronouns}

    # WalkTreeUntil() walks the predications in mrs["Tree"] and calls
    # the function record_predications_until_failure_index(), until hits the
    # failure_index position
    index_by_ref = [0]

    def initial_nlg_data(predication, index_by_ref):
        return record_predications_until_failure_index(predication, index_by_ref, nlg_data, tree_info)

    rewrite_tree_predications(tree_info["Tree"], initial_nlg_data, index_by_ref)

    # Take the data we gathered and convert to English
    logger.debug(f"NLG data for {variable}: {nlg_data}")
    return convert_to_english(nlg_data, plural, determiner)


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
                if parsed_predication["Pos"] == "c" and parsed_predication["Lemma"] == "and":
                    string_list = []
                    string_list.append(english_for_delphin_variable(1000, predication.args[1], tree_info))
                    string_list.append(english_for_delphin_variable(1000, predication.args[2], tree_info))
                    nlg_data["Topic"] = f"'{', '.join(string_list)}' (both)"

                else:
                    nlg_data["Topic"] = parsed_predication["Lemma"].replace("+", " ")

            else:
                # Some abstract predications *should* contribute to the
                # English description of a variable
                if parsed_predication["Lemma"] == "pron":
                    nlg_data["Topic"] = pronoun_from_variable(tree_info, variable, nlg_data["ReversePronouns"])

                elif parsed_predication["Lemma"] == "quoted":
                    nlg_data["Topic"] = predication.args[0].replace("\\>root111", "/").replace("\\>", "/")

                elif parsed_predication["Lemma"] in ["place", "thing"]:
                    nlg_data["Topic"] = parsed_predication["Lemma"]

                elif parsed_predication["Lemma"] == "fw_seq":
                    string_list = []
                    for arg_index in range(1, len(predication.arg_names)):
                        if predication.args[arg_index][0] == "i":
                            # Use 1000 to make sure we go through the whole tree
                            string_list.append(english_for_delphin_variable(1000, predication.args[arg_index], tree_info))

                        elif predication.args[arg_index][0] == "x":
                            # Use 1000 to make sure we go through the whole tree
                            string_list.append(english_for_delphin_variable(1000, predication.args[arg_index], tree_info))

                    # If the only thing consuming the introduced variable are other fw_seq predications
                    # Then this is not the final fw_seq, so don't put quotes around it
                    if is_last_fw_seq(tree_info["Tree"], predication):
                        nlg_data["Topic"] = f"'{' '.join(string_list)}'"
                    else:
                        nlg_data["Topic"] = f"{' '.join(string_list)}"

                elif parsed_predication["Lemma"] == "implicit_conj":
                    string_list = []
                    string_list.append(english_for_delphin_variable(1000, predication.args[1], tree_info))
                    string_list.append(english_for_delphin_variable(1000, predication.args[2], tree_info))
                    nlg_data["Topic"] = f"'{', '.join(string_list)}'"

                elif parsed_predication["Lemma"] == "card" and predication.arg_types[2] == "i":
                    if "Modifiers" not in nlg_data:
                        nlg_data["Modifiers"] = []

                    nlg_data["Modifiers"].append(predication.args[0])

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

    elif parsed_predication["Lemma"] == "loc_nonsp" and predication.args[1] == variable:

        if "PostModifiers" not in nlg_data:
            nlg_data["PostModifiers"] = []

        nlg_data["PostModifiers"].append("that is " + english_for_delphin_variable(1000, predication.args[2], tree_info))


pronouns = {1: {"sg": "I",
                "pl": "we"},
            2: {"sg": "you",
                "pl": "you"},
            3: {"sg": "he/she",
                "pl": "they"}
            }

reversed_pronouns = {1: {"sg": "you",
                         "pl": "you"},
                     2: {"sg": "I",
                         "pl": "we"},
                     3: {"sg": "he/she",
                         "pl": "they"}
                     }


def pronoun_from_variable(tree_info, variable, reverse_pronouns):
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

    return reversed_pronouns[person][number] if reverse_pronouns else pronouns[person][number]


# Takes the information gathered in the nlg_data dictionary
# and converts it, in a very simplistic way, to English
def convert_to_english(nlg_data, plural=None, determiner=None):
    phrase = ""

    if determiner is not None:
        lower_determiner = determiner.lower()
        if lower_determiner in ["a", "an"]:
            nlg_data["Quantifier"] = "a"
        elif lower_determiner == "the":
            nlg_data["Quantifier"] = "the"
        elif lower_determiner in ["bare", ""]:
            nlg_data["Quantifier"] = "<none>"

    if "Quantifier" in nlg_data:
        if nlg_data["Quantifier"] != "<none>":
            phrase += nlg_data["Quantifier"] + " "

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

    if "NotScope" in nlg_data:
        not_english = convert_to_english(nlg_data["NotScope"])
        if len(not_english.strip()):
            phrase += "not " + not_english

    return phrase.strip()


logger = logging.getLogger('Generation')
pipeline_logger = logging.getLogger('Pipeline')
p = inflect.engine()
