import copy
import difflib
import logging
import os
import re
import sys
import inflect
from delphin.mrs import EP, MRS, is_well_formed, is_connected, has_intrinsic_variable_property, plausibly_scopes, \
    has_complete_intrinsic_variables, has_unique_intrinsic_variables
from perplexity.response import PluralMode
from perplexity.tree import MrsParser, walk_tree_predications_until, rewrite_tree_predications, TreePredication, \
    find_predication_from_introduced
from perplexity.utilities import parse_predication_name


class RespondOperation(object):
    def __init__(self, response):
        self.response = response

    def apply_to(self, state):
        pass

    def response_string(self):
        return self.response


uncountable_nouns = {"butter",
                     "cash",
                     "music", "art", "love", "happiness"
                     "advice", "information", "news"
                     "furniture", "luggage"
                     "rice", "sugar", "butter", 'water'
                     "electricity", "gas", 'power'
                     'money', 'currency', 'water'
                     }


def article_for_fragment(fragment, is_definite):
    fragment = fragment.strip()
    if is_definite:
        return "the"

    else:
        if fragment in uncountable_nouns:
            return ""
        elif fragment[0] in ["a", "e", "i", "o", "u", "y"]:
            return "an "
        else:
            return "a "


# def article_for_fragment(fragment, is_definite):
#     fragment = fragment.strip()
#     if is_definite:
#         the_fragment_string = f"get the {fragment}"
#         if fragment_parses(the_fragment_string):
#             return the_fragment_string
#
#     else:
#         if fragment[0] in ["a", "e", "i", "o", "u", "y"]:
#             article_list = ["an ", "", "a "]
#         else:
#             article_list = ["a ", "", "an "]
#
#         for article in article_list:
#             a_fragment_string = f"get {article}{fragment}"
#             if fragment_parses(a_fragment_string):
#                 return a_fragment_string
# def fragment_parses(fragment):
#     mrs_parser = MrsParser()
#     for mrs in mrs_parser.mrss_from_phrase(fragment):
#         return True
#     return False


def fragment_mrs(fragment):
    mrs_parser = MrsParser()

    # parse the fragment and find the first MRS that has a single unknown_x(e,x)
    target_mrs = None
    for mrs in mrs_parser.mrss_from_phrase(fragment):
        unknown_count = 0
        for predication in mrs.predications:
            if predication.predicate == "unknown" and len(predication.args) == 2:
                unknown_count += 1
                if unknown_count > 1:
                    break
        if unknown_count == 1:
            target_mrs = mrs
            break

    if target_mrs is None:
        return None

    return target_mrs


def diff_generator(original, generated):
    d = difflib.Differ()
    diff_list = [x for x in d.compare(original.split(), generated.split())]
    accumulator = [[], []]
    for next_diff in diff_list:
        if next_diff[0] == "?":
            pass
        elif next_diff[0] == "+":
            accumulator[0].append(next_diff[2:])
        elif next_diff[0] == "-":
            accumulator[1].append(next_diff[2:])
        else:
            if len(accumulator[0]) > 0 or len(accumulator[1]) > 0:
                yield " ".join(accumulator[0]), " ".join(accumulator[1])
                accumulator = [[], []]

    if len(accumulator[0]) > 0 or len(accumulator[1]) > 0:
        yield " ".join(accumulator[0]), " ".join(accumulator[1])


def compare_generated_output(original, generated):
    # Basic cleaning of input
    original = original.strip(" .?!")
    generated = generated.strip(" .?!")

    diffs = []
    for subtractions, additions in diff_generator(original.lower(), generated.lower()):
        # twenty-forth round trips to twenty forth
        if len(subtractions) == len(additions) and additions.replace("-", " ") == subtractions:
            continue

        if additions.isdigit() and inflect_engine.number_to_words(additions) == subtractions or \
            subtractions.isdigit() and inflect_engine.number_to_words(subtractions) == additions:
            continue

        diffs.append(f"{additions} <--> {subtractions}")

    return diffs


def find_quantifier_from_variable(term, variable_name):
    def match_variable(predication):
        predication_data = parse_predication_name(predication.name)
        if predication_data["Pos"] == "q" and predication.args[0] == variable_name:
            return predication
        else:
            return None

    return walk_tree_predications_until(term, match_variable)


def create_fragment(mrs, tree, variable):
    pass


def mrs_fragment_from_variable(mrs, tree, variable, determiner=None):
    def rewrite_tree_without_fragment_body(predication, index_by_ref):
        nonlocal pruned_body
        nonlocal mrs
        nonlocal new_eps
        nonlocal new_variables
        new_variables.add(predication.mrs_predication.label)
        for arg_item in predication.mrs_predication.args.items():
            if arg_item[0] != "CARG":
                new_variables.add(arg_item[1])

        predication_data = parse_predication_name(predication.name)
        if predication_data["Pos"] == "q" and predication.args[0] == variable:
            predication_copy = copy.deepcopy(predication)
            predication_copy.index = index_by_ref[0]
            index_by_ref[0] += 1

            predication_copy.args[1] = rewrite_tree_predications(predication_copy.args[1], rewrite_tree_without_fragment_body, index_by_ref)
            pruned_body = predication_copy.args[2]
            # Assuming the index was introduced by something that got pruned,
            # that's why we can reuse it as ARG0
            index_predication = find_predication_from_introduced(pruned_body, mrs.index)
            if not index_predication:
                pruned_body = None
            else:
                if determiner in ["a", "an"] or predication.mrs_predication.predicate in ["_which_q", "which_q"]:
                    if "NUM" not in mrs.variables[variable] or mrs.variables[variable]["NUM"] == "sg":
                        predication.mrs_predication.predicate = "_a_q"
                    else:
                        # Indefinite article with plural is no article
                        predication.mrs_predication.predicate = "udef_q"

                elif determiner == "the":
                    predication.mrs_predication.predicate = "_the_q"
                elif determiner == "":
                    predication.mrs_predication.predicate = "udef_q"

                new_eps.append(predication.mrs_predication)

                unknown_ep = EP(predicate="unknown", label=index_predication.mrs_predication.label, args={"ARG0": mrs.index, "ARG": variable})
                new_eps.append(unknown_ep)
                new_variables.add(mrs.index)
                new_variables.add(variable)
                new_variables.add(unknown_ep.label)
                predication_copy.args[2] = TreePredication(index_by_ref[0], "unknown", [variable], ["ARG0"], unknown_ep)
                index_by_ref[0] += 1
                return predication_copy

        else:
            # Convert "which(x, thing(x), ...) to _a_q_(x, _thing_n_of-about(), ...) so it will generate
            if predication.name == "thing":
                predication.mrs_predication.predicate = "_thing_n_of-about"
                predication.mrs_predication.args["ARG1"] = 'i99'

            new_eps.append(predication.mrs_predication)

    def used_hcons(old_hcons, new_eps):
        new_hcons = []
        for hcon in old_hcons:
            assert hcon.relation == "qeq"
            found_lo = False
            found_hi = False
            for ep in new_eps:
                if hcon.hi == "h0":
                    found_hi = True
                if hcon.lo == ep.label:
                    found_lo = True
                for arg_item in ep.args.items():
                    if arg_item[1] == hcon.hi:
                        found_hi = True
                        break
            if found_hi and found_lo:
                new_hcons.append(hcon)

        return new_hcons

    # Walk the tree until we find the quantifier that scopes `variable`
    # Add every EP to the list as they are encountered
    index_by_ref = [0]
    pruned_body = None
    new_eps = []
    new_variables = set(["h0"])
    new_tree = rewrite_tree_predications(tree, rewrite_tree_without_fragment_body, index_by_ref)
    if pruned_body is None:
        # This tree is not in a form we know how to prune
        return None

    else:
        # Now build the new MRS
        new_hcons = used_hcons(mrs.hcons, new_eps)
        new_variables_values = {"h0": mrs.variables["h0"]}
        for var_item in mrs.variables.items():
            if var_item[0] in new_variables:
                new_variables_values[var_item[0]] = var_item[1]

        # Always set the sentence force of the index variable to be proposition
        # Get rid of any other properties in it
        new_variables_values[mrs.index] = {"SF": "prop"}
        new_mrs = MRS(top=mrs.top, index=mrs.index, rels=new_eps, hcons=new_hcons, variables=new_variables_values)
        assert has_complete_intrinsic_variables(new_mrs)
        assert has_unique_intrinsic_variables(new_mrs)
        assert has_intrinsic_variable_property(new_mrs)
        assert plausibly_scopes(new_mrs)
        return new_mrs


def best_generation_index(mrs, original_text):
    generate_parser = MrsParser(generate_root="root_frag")
    new_mrs_string = generate_parser.mrs_to_string(mrs)
    index = 0
    matches = []
    for generated_phrase in generate_parser.phrase_from_simple_mrs(new_mrs_string):
        diff_list = compare_generated_output(original_text, generated_phrase)
        if len(diff_list) == 0:
            # Exact match! Stop now, not going to get better
            return index
        matches.append([len(diff_list), generated_phrase, diff_list, index])
        index += 1

    if len(matches) > 0:
        def sort_key(value):
            return value[0]
        matches.sort(key=sort_key)
        return matches[0][3], matches[0][1]

    else:
        return None, None


def fragmentize_phrase(phrase):
    phrase = phrase[0].lower() + phrase[1:]
    return phrase.strip(".?!")


def english_for_variable_using_mrs(mrs_parser, mrs, tree, variable, plural=None, determiner=None):
    # Get the MRS fragment for the variable
    new_mrs = mrs_fragment_from_variable(mrs, tree, variable, determiner)
    if new_mrs is None:
        return None, None, None
    else:
        if plural is not None and plural != PluralMode.as_is:
            # mrs = copy.deepcopy(mrs)
            mrs.variables[variable]["NUM"] = "pl" if plural == PluralMode.plural else "sg"

        # Figure out which generated text best matches the original
        best_index, generated_text = best_generation_index(new_mrs, mrs.surface)
        return fragmentize_phrase(generated_text) if generated_text is not None else generated_text, best_index, new_mrs


def all_x_fragments(mrs_parser, phrase):
    # Get the best matching MRS for the phrase
    gen_index, _, mrs = round_trip_mrs(mrs_parser, phrase)
    if mrs is None:
        print(f"Couldn't round trip: {phrase}")
        return

    variables = []

    # Find all x variables
    for variable_item in mrs.variables.items():
        if variable_item[0][0] == "x":
            variables.append(variable_item[0])

    # Convert every x variable to english
    for variable in variables:
        print_variable = True
        for tree in mrs_parser.trees_from_mrs(mrs):
            if print_variable:
                print(f"\n{variable} --> {find_predication_from_introduced(tree, variable)}")
                print_variable = False

            generated_text, best_index, new_mrs = english_for_variable_using_mrs(mrs_parser, mrs, tree, variable)
            if generated_text is None:
                print(f"{variable} = <no result>. mrs fragment: {new_mrs}")
            else:
                print(f"{variable} = {generated_text} mrs fragment: {new_mrs}")

                generated_text, best_index, new_mrs = english_for_variable_using_mrs(mrs_parser, mrs, tree, variable, plural=False)
                if generated_text is None:
                    print(f"{variable}(sg) = <no result>. mrs fragment: {new_mrs}")
                else:
                    print(f"{variable}(sg) = {generated_text} mrs fragment: {new_mrs}")

                generated_text, best_index, new_mrs = english_for_variable_using_mrs(mrs_parser, mrs, tree, variable, plural=True)
                if generated_text is None:
                    print(f"{variable}(pl) = <no result>. mrs fragment: {new_mrs}")
                else:
                    print(f"{variable}(pl) = {generated_text} mrs fragment: {new_mrs}")

                generated_text, best_index, new_mrs = english_for_variable_using_mrs(mrs_parser, mrs, tree, variable, plural=False, determiner="a")
                if generated_text is None:
                    print(f"{variable}(a) = <no result>. mrs fragment: {new_mrs}")
                else:
                    print(f"{variable}(a) = {generated_text} mrs fragment: {new_mrs}")

                generated_text, best_index, new_mrs = english_for_variable_using_mrs(mrs_parser, mrs, tree, variable, plural=False, determiner="the")
                if generated_text is None:
                    print(f"{variable}(the, sg) = <no result>. mrs fragment: {new_mrs}")
                else:
                    print(f"{variable}(the, sg) = {generated_text} mrs fragment: {new_mrs}")

                generated_text, best_index, new_mrs = english_for_variable_using_mrs(mrs_parser, mrs, tree, variable, plural=True, determiner="the")
                if generated_text is None:
                    print(f"{variable}(the, pl) = <no result>. mrs fragment: {new_mrs}")
                else:
                    print(f"{variable}(the, pl) = {generated_text} mrs fragment: {new_mrs}")

        if print_variable:
            print(f"\n{variable} -> <no tree>")


# Find the MRS for phrase that round trips through ACE Generation
def round_trip_mrs(mrs_parser, phrase):
    # Todo: add these back at the end somehow, they prevent parsing
    trace_report = ""
    phrase = phrase.strip(":")

    all_generated = []
    mrs_index = 0
    for mrs in mrs_parser.mrss_from_phrase(phrase, True):
        mrs_index += 1
        mrs_string = mrs_parser.mrs_to_string(mrs)
        trace_report += f"\nMRS: {mrs_index}: {mrs}\n"
        generate = True
        for predication in mrs.predications:
            if predication.predicate.endswith("_u_unknown"):
                # Also, unknown() doesn't generate?
                trace_report += f"Can't generate due to: {predication.predicate}\n"
                generate = False
                break

        this_generated = []
        if generate:
            index = 0
            for generated_phrase in mrs_parser.phrase_from_simple_mrs(mrs_string):
                this_generated.append(generated_phrase)
                diffs = compare_generated_output(phrase, generated_phrase)
                if len(diffs) == 0:
                    logger.info(f"MRS {mrs_index}, GEN {index}: Found round trip: {mrs}\n")
                    return index, generated_phrase, mrs
                else:
                    newline = "\n"
                    trace_report += f"MRS {mrs_index}, GEN {index}: {newline.join(diffs)}\n"

                index += 1

        if len(this_generated) == 0:
            trace_report += f"MRS {mrs_index}: Nothing generated\n"

        else:
            trace_report += f"MRS {mrs_index}: No round trip found\n"
            all_generated += this_generated

    logger.debug(trace_report)
    return None, all_generated, None


def split_sentences(paragraph):
    return re.split("(?<=[.!?\"]) +", paragraph)


def round_trip(mrs_parser, paragraph):
    generated_paragraph = []
    for sentence in split_sentences(paragraph):
        logger.info(f"Phrase: {sentence}")
        index, generated_phrase, mrs = round_trip_mrs(mrs_parser, sentence)
        if index is None:
            cr = "\n"
            logger.debug(f"Couldn't find a clean round trip for: {sentence}")
        else:
            generated_paragraph.append((index, generated_phrase, mrs))

    return generated_paragraph


def test_sentences(start_index=0):
    path = os.path.dirname(os.path.realpath(__file__))
    with open(os.path.join(path, "text_fic.txt"), "r") as file:
        index = -1
        while True:
            document = file.readline()
            if not document:
                break
            else:
                document = document.strip()

            if len(document) > 0:
                document = document[10:]
                paragraphs = document.split(" <p> ")
                for paragraph in paragraphs:
                    for sentence in split_sentences(paragraph):
                        if sentence in ["\""]:
                            continue
                        if sentence.find("@ @ @ @ @ @ @ @ @ @") != -1:
                            continue
                        sentence = sentence.replace(" n't", "n't")
                        sentence = sentence.replace(" 'd", "'d")
                        sentence = sentence.replace(" n't", "n't")
                        sentence = sentence.replace(" 's", "'s")
                        sentence = sentence.replace(" .", ".")
                        sentence = sentence.replace(" ?", "?")
                        sentence = sentence.replace(" !", "!")
                        sentence = sentence.replace(" , ", ", ")
                        index += 1
                        if index < start_index:
                            continue

                        yield sentence


path = os.path.dirname(os.path.realpath(__file__))

logger = logging.getLogger("response")
logger.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(message)s')

stdout_handler = logging.StreamHandler(sys.stdout)
stdout_handler.setLevel(logging.DEBUG)
stdout_handler.setFormatter(formatter)
logger.addHandler(stdout_handler)

# log_file_path = os.path.join(path, "test_log.txt")
# file_handler = logging.FileHandler(log_file_path)
# file_handler.setLevel(logging.DEBUG)
# file_handler.setFormatter(formatter)
#
# logger.addHandler(file_handler)

inflect_engine = inflect.engine()


if __name__ == '__main__':
    # https://www.english-corpora.org/coca/
    # Samples: https://www.corpusdata.org/formats.asp
    # https://storage.googleapis.com/books/ngrams/books/datasetsv3.html


    # with open(log_file_path, "a") as file:
    #     mrs_parser = MrsParser(log_file=file)
    #     start_index = 0
    #     for sentence in test_sentences(start_index):
    #         logger.info(f"\n\n***** sentence {start_index} *****")
    #         round_trip(mrs_parser, sentence)
    #         start_index += 1

    mrs_parser = MrsParser()

    # result = round_trip(mrs_parser, "the two files in a folder are twenty mb.")
    # print(result)

    # "He was a philosophy major" generates a tree where: pronoun_q(x3,pron(x3),_a_q(x8,udef_q(x14,_philosophy_n_1(x14),[_major_n_1(x8), compound(e13,x8,x14)]),_be_v_id(e2,x3,x8)))
    all_x_fragments(mrs_parser, "files are large.")

    # english_for_variable(mrs_parser, )
    # all_x_fragments(mrs_parser, "He was a philosophy major.", "x12")

    # create_fragment(mrs_parser, "the two files in a folder are twenty mb.", "x12")

    # print(article_for_fragment("dog", False))
    # print(article_for_fragment("friend that doesn't show up on time", False))
    # print(article_for_fragment("water", False))
    # print(article_for_fragment("scissors", False))
    # print(article_for_fragment("rain", False))
    # print(article_for_fragment("novels", False))
