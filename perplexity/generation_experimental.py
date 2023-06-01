import logging
import os
import re
import sys

from perplexity.generation_mrs import english_for_variable_using_mrs, compare_generated_output
from perplexity.tree import find_predication_from_introduced, MrsParser


def print_all_x_fragments(mrs_parser, phrase):
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
        meaning_at_index = None
        for tree in mrs_parser.trees_from_mrs(mrs):
            if print_variable:
                found_predication = find_predication_from_introduced(tree, variable)
                meaning_at_index = found_predication.index + 1
                print(f"\n{variable} --> {found_predication}")
                print_variable = False

            generated_text, best_index, new_mrs = english_for_variable_using_mrs(mrs_parser, mrs, meaning_at_index, variable, tree)
            if generated_text is None:
                print(f"{variable} = <no result>. [mrs fragment: {new_mrs}]")
            else:
                print(f"{variable} = {generated_text} [mrs fragment: {new_mrs}]")

                generated_text, best_index, new_mrs = english_for_variable_using_mrs(mrs_parser, mrs, meaning_at_index, variable, tree, plural=False)
                if generated_text is None:
                    print(f"{variable}(sg) = <no result>. [mrs fragment: {new_mrs}]")
                else:
                    print(f"{variable}(sg) = {generated_text} [mrs fragment: {new_mrs}]")

                generated_text, best_index, new_mrs = english_for_variable_using_mrs(mrs_parser, mrs, meaning_at_index, variable, tree, plural=True)
                if generated_text is None:
                    print(f"{variable}(pl) = <no result>. [mrs fragment: {new_mrs}]")
                else:
                    print(f"{variable}(pl) = {generated_text} [mrs fragment: {new_mrs}]")

                generated_text, best_index, new_mrs = english_for_variable_using_mrs(mrs_parser, mrs, meaning_at_index, variable, tree, plural=False, determiner="a")
                if generated_text is None:
                    print(f"{variable}(a) = <no result>. [mrs fragment: {new_mrs}]")
                else:
                    print(f"{variable}(a) = {generated_text} [mrs fragment: {new_mrs}]")

                generated_text, best_index, new_mrs = english_for_variable_using_mrs(mrs_parser, mrs, meaning_at_index, variable, tree, plural=False, determiner="the")
                if generated_text is None:
                    print(f"{variable}(the, sg) = <no result>. [mrs fragment: {new_mrs}]")
                else:
                    print(f"{variable}(the, sg) = {generated_text} [mrs fragment: {new_mrs}]")

                generated_text, best_index, new_mrs = english_for_variable_using_mrs(mrs_parser, mrs, meaning_at_index, variable, tree, plural=True, determiner="the")
                if generated_text is None:
                    print(f"{variable}(the, pl) = <no result>. [mrs fragment: {new_mrs}]")
                else:
                    print(f"{variable}(the, pl) = {generated_text} [mrs fragment: {new_mrs}]")

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

logger = logging.getLogger("SString")
logger.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(message)s')

stdout_handler = logging.StreamHandler(sys.stdout)
stdout_handler.setLevel(logging.DEBUG)
stdout_handler.setFormatter(formatter)
logger.addHandler(stdout_handler)

log_file_path = os.path.join(path, "test_log.txt")
file_handler = logging.FileHandler(log_file_path)
file_handler.setLevel(logging.DEBUG)
file_handler.setFormatter(formatter)

logger.addHandler(file_handler)

if __name__ == '__main__':
    # This tests a corpus. Choose a different start_index to start deeper in the corpus
    # https://www.english-corpora.org/coca/
    # Samples: https://www.corpusdata.org/formats.asp
    # https://storage.googleapis.com/books/ngrams/books/datasetsv3.html
    with open(log_file_path, "a") as file:
        mrs_parser = MrsParser(log_file=file)
        start_index = 50
        for sentence in test_sentences(start_index):
            logger.info(f"\n\n***** sentence {start_index} *****")
            round_trip(mrs_parser, sentence)
            start_index += 1

    mrs_parser = MrsParser()
    print_all_x_fragments(mrs_parser, "files are large.")

