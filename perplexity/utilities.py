import enum
import importlib
import inspect
import logging
import sys
import re

# Constants that define indices for arguments added to predications
# automatically by the system
system_added_context_arg = 0
system_added_state_arg = 1
system_added_arg_count = 2
system_added_group_arg_count = 2


# A given interaction can span multiple phrases ("I want a sandwich. He wants a steak.") and potentially
# multiple worlds ("I want a sandwich. Quit. He wants a steak").
# Each record (i.e. phrase) can contain a phrase to output if it is the last record in the interaction for that world
# - "NewWorld" exists on a record if a new UI was created in that interaction
# - "InteractionEnd" exists on a record when the world had extra text to add at the end of an interaction
#       and this interaction represents the end
# - "NewWorldResponse" happens when a new world was created and that world had something to say at startup
def output_interaction_records(interaction_records):
    string_output_list = []
    last_phrase_response = None
    for interaction_record_index in range(len(interaction_records)):
        interaction_record = interaction_records[interaction_record_index]
        chosen_mrs_index = interaction_record["ChosenMrsIndex"]
        if chosen_mrs_index is None:
            continue

        # There was at least a parse
        chosen_interpretation_index = interaction_record["ChosenInterpretationIndex"]
        chosen_interpretation = interaction_record["Mrss"][chosen_mrs_index]["Interpretations"][chosen_interpretation_index]

        # Output the main message
        string_output_list.append(chosen_interpretation["ResponseMessage"])

        if "LastPhraseResponse" in chosen_interpretation and chosen_interpretation["LastPhraseResponse"] is not None:
            last_phrase_response = chosen_interpretation["LastPhraseResponse"]

        if "NewWorld" in chosen_interpretation:
            # Only output LastPhraseResponse if this was the last output for this world
            if last_phrase_response is not None:
                string_output_list.append(last_phrase_response)
                last_phrase_response = None

        if "InteractionEnd" in chosen_interpretation and chosen_interpretation["InteractionEnd"] is not None:
                string_output_list.append(chosen_interpretation["InteractionEnd"])

        # Print any introduction text from the new world if there was one
        if "NewWorldResponse" in chosen_interpretation:
            if chosen_interpretation["NewWorldResponse"] is not None:
                string_output_list.append(chosen_interpretation["NewWorldResponse"])

    # Only output LastPhraseResponse if this was the last output for this world
    if last_phrase_response is not None:
        string_output_list.append(last_phrase_response)
        last_phrase_response = None

    return "\n".join(string_output_list)


def running_under_debugger():
    # This is a hack to see if we're running under the debugger
    # https://stackoverflow.com/questions/38634988/check-if-program-runs-in-debug-mode
    gettrace = getattr(sys, 'gettrace', None)
    if gettrace is None:
        print('No sys.gettrace')
        return False

    elif gettrace is not None and gettrace():
        # running under debugger, don't time out
        return True


def get_function(module_function):
    module = sys.modules[module_function[0]]
    function = getattr(module, module_function[1])
    return function


# Returns a dict:
# {
#     "Surface" : True | False
#     "Lemma" : "go"...
#     "Pos" : "v"...
#     "PredicateRaw":
#     "Sense": "dir"...
# }
def parse_predication_name(name):
    result = {"PredicateRaw": name}

    if name[0] == "_":
        params = name.split("/")
        if len(params) > 1:
            name = params[0]

        params = name[1:].split("_")
        result["Surface"] = True

    else:
        params = name.split("_")
        result["Surface"] = False

    # From this point forward, everything up to the POS is the lemma
    # and everything after the POS is the sense
    got_pos = False
    for item in params:
        if not got_pos:
            # some words like "a" look like a POS so don't get tricked
            # From wiki entry: RmrsPos
            # Label	Explanation	Example	Comment
            # n := u	noun	banana_n_1	WordNet n
            # v := u	verb	bark_v_1	WordNet v
            # a := u	adjective or adverb (i.e. supertype of j and r)	fast_a_1
            # j := a	adjective	 	WordNet a
            # r := a	adverb	 	WordNet r
            # s := n, s:= v	verbal noun (used in Japanese and Korean)	benkyou_s_1
            # c := u	conjunction	and_c_1
            # p := u	adposition (preposition, postposition)	from_p_1, kara_p_1 (から_p_1)
            # q := u	quantifier (needs to be distinguished for scoping code)	this_q_1
            # x := u	other closed class	ahem_x_1
            # u	unknown
            if "Lemma" in result and item in ["n", "v", "a", "j", "r", "s", "c", "p", "q", "x", "u"]:
                result["Pos"] = item
                got_pos = True
            else:
                # Keep adding to the lemma until we find POS (if it exists)
                # e.g. d_fw_seq_end_z__xx
                result["Lemma"] = item if "Lemma" not in result else f"{result['Lemma']}_{item}"
        else:
            result["Sense"] = item if "Sense" not in result else f"{result['Sense']}_{item}"

    if "Lemma" not in result:
        result["Lemma"] = "#unknown#"

    if "Pos" not in result:
        # u for unknown
        result["Pos"] = "u"

    return result


def sentence_force(variables):
    for variable in variables.items():
        if "SF" in variable[1]:
            return variable[1]["SF"]


def ShowLogging(name, level=logging.DEBUG):
    logger = logging.getLogger(name)
    logger.setLevel(level)
    formatter = logging.Formatter('%(name)s %(asctime)s: %(message)s')
    file_handler = logging.StreamHandler(sys.stdout)
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)


def plural_from_tree_info(tree_info, variable_name):
    variables = tree_info["Variables"]
    for variable in variables.items():
        if variable[0] == variable_name:
            if "NUM" in variable[1]:
                return variable[1]["NUM"]


def is_plural(state, variable_name):
    return plural_from_tree_info(state.get_binding("tree").value[0], variable_name) == "pl"


# Get the actual module name even if it is the
# initial python file run, which gets the module
# name "__main__"
def module_name(obj):
    name = obj.__module__

    if "__main__" in name:
        # get parent modules of object
        mod_obj = inspect.getmodule(obj)  # type: module

        # from the filename of the module, get its name'
        mod_suffix = inspect.getmodulename(inspect.getmodule(obj).__file__)

        # join parent to child with a .
        name = '.'.join([mod_obj.__package__, mod_suffix]) if (mod_obj.__package__ != "" and mod_obj.__package__ is not None) else mod_suffix

    return name


# Takes a pair of module and function names as strings and
# imports the module and returns the function
def import_function_from_names(module_name, function_name):
    importlib.import_module(module_name)
    module = sys.modules[module_name]
    function = getattr(module, function_name)
    return function


# This takes a generator and, if the generator returns at least
# one item, returns a generator that will return that item and any others
# If the passed generator does not return any items, it returns None
def at_least_one_generator(generator):
    if isinstance(generator, (list, tuple)):
        generator = iter(generator)

    try:
        first_item = next(generator)

    except StopIteration:
        return None

    return AtLeastOneIterator(first_item, generator)


class AtLeastOneIterator(object):
    def __init__(self, first_item, generator):
        self.first_item = first_item
        self.generator = generator

    def __iter__(self):
        return self

    def __next__(self):
        if self.first_item is not None:
            item = self.first_item
            self.first_item = None
            return item

        else:
            return next(self.generator)

    def has_at_least_one_more(self):
        if self.first_item:
            return True
        else:
            try:
                self.first_item = next(self.generator)
                return True

            except StopIteration:
                return False


def yield_all(set_or_answer):
    if isinstance(set_or_answer, (list, tuple)):
        for item in set_or_answer:
            yield from yield_all(item)
    else:
        yield set_or_answer


# From: https://stackoverflow.com/questions/4576077/how-can-i-split-a-text-into-sentences
def split_into_sentences(text: str):
    """
    Split the text into sentences.

    If the text contains substrings "<prd>" or "<stop>", they would lead
    to incorrect splitting because they are used as markers for splitting.

    :param text: text to be split into sentences
    :type text: str

    :return: list of sentences
    :rtype: list[str]
    """
    if text is None:
        return [None]

    alphabets = "([A-Za-z])"
    prefixes = "(Mr|St|Mrs|Ms|Dr)[.]"
    suffixes = "(Inc|Ltd|Jr|Sr|Co)"
    starters = "(Mr|Mrs|Ms|Dr|Prof|Capt|Cpt|Lt|He\s|She\s|It\s|They\s|Their\s|Our\s|We\s|But\s|However\s|That\s|This\s|Wherever)"
    acronyms = "([A-Z][.][A-Z][.](?:[A-Z][.])?)"
    websites = "[.](com|net|org|io|gov|edu|me)"
    digits = "([0-9])"
    multiple_dots = r'\.{2,}'

    text = " " + text + "  "
    text = text.replace("\n"," ")
    text = re.sub(prefixes,"\\1<prd>",text)
    text = re.sub(websites,"<prd>\\1",text)
    text = re.sub(digits + "[.]" + digits,"\\1<prd>\\2",text)
    text = re.sub(multiple_dots, lambda match: "<prd>" * len(match.group(0)) + "<stop>", text)
    if "Ph.D" in text: text = text.replace("Ph.D.","Ph<prd>D<prd>")
    if "e.g." in text: text = text.replace("e.g.", "e<prd>g<prd>")
    if "i.e." in text: text = text.replace("i.e.", "i<prd>e<prd>")
    text = re.sub("\s" + alphabets + "[.] "," \\1<prd> ",text)
    text = re.sub(acronyms+" "+starters,"\\1<stop> \\2",text)
    text = re.sub(alphabets + "[.]" + alphabets + "[.]" + alphabets + "[.]","\\1<prd>\\2<prd>\\3<prd>",text)
    text = re.sub(alphabets + "[.]" + alphabets + "[.]","\\1<prd>\\2<prd>",text)
    text = re.sub(" "+suffixes+"[.] "+starters," \\1<stop> \\2",text)
    text = re.sub(" "+suffixes+"[.]"," \\1<prd>",text)
    text = re.sub(" " + alphabets + "[.]"," \\1<prd>",text)
    if "”" in text: text = text.replace(".”","”.")
    if "\"" in text: text = text.replace(".\"","\".")
    if "!" in text: text = text.replace("!\"","\"!")
    if "?" in text: text = text.replace("?\"","\"?")
    text = text.replace(".",".<stop>")
    text = text.replace("?","?<stop>")
    text = text.replace("!","!<stop>")
    text = text.replace("<prd>",".")
    sentences = text.split("<stop>")
    sentences = [s.strip() for s in sentences]
    if sentences and not sentences[-1]: sentences = sentences[:-1]
    return sentences


pipeline_logger = logging.getLogger('Pipeline')


if __name__ == '__main__':
    print(split_into_sentences("Ok.  I will order the Steak.  My son will have the green salad please.") )
    print()
    print(split_into_sentences("hello. table for two, please"))
    print()
    print(split_into_sentences("I would like a hamburger.  My son would like something vegetarian."))
    print()
