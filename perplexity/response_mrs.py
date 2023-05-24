import difflib
import logging
import os
import pathlib
import re
import sys

from perplexity.tree import MrsParser


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


def compare_generation_output(original, generated):
    diffs = "   "
    for subtractions, additions in diff_generator(original.lower(), generated.lower()):
        # twenty-forth round trips to twenty forth
        if len(subtractions) == len(additions) and additions.replace("-", " ") == subtractions:
            continue

        diffs += f"{additions} <--> {subtractions} | "

    if len(diffs.strip()) > 0:
        return f"{generated}\n" + diffs
    else:
        return True


# Find the MRS for phrase that round trips through ACE Generation
def template_mrs(mrs_parser, phrase, placeholder):
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
            if predication.predicate.endswith("_u_unknown") or predication.predicate == "unknown":
                # Also, unknown() doesn't generate?
                trace_report += f"Can't generate due to: {predication.predicate}\n"
                generate = False
                break

        this_generated = []
        if generate:
            for generated_phrases in mrs_parser.phrase_from_simple_mrs(mrs_string):
                this_generated += generated_phrases
                for index in range(len(generated_phrases)):
                    compare_result = compare_generation_output(phrase, generated_phrases[index])
                    if compare_result is True:
                        logger.info(f"MRS {mrs_index}, GEN {index}: Found round trip: {mrs}\n")
                        return index, generated_phrases[index], mrs

                    else:
                        trace_report += f"MRS {mrs_index}, GEN {index}: {compare_result}\n"

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
        index, generated_phrase, mrs = template_mrs(mrs_parser, sentence, "")
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


if __name__ == '__main__':
    path = os.path.dirname(os.path.realpath(__file__))
    log_file_path = os.path.join(path, "test_log.txt")

    logger = logging.getLogger("response")
    logger.setLevel(logging.DEBUG)
    formatter = logging.Formatter('%(message)s')

    stdout_handler = logging.StreamHandler(sys.stdout)
    stdout_handler.setLevel(logging.DEBUG)
    stdout_handler.setFormatter(formatter)

    file_handler = logging.FileHandler(log_file_path)
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(formatter)

    logger.addHandler(file_handler)
    logger.addHandler(stdout_handler)


    # https://www.english-corpora.org/coca/
    # Samples: https://www.corpusdata.org/formats.asp
    # https://storage.googleapis.com/books/ngrams/books/datasetsv3.html

    # Feedback
    # May of the parses are close like (no contraction of is not and isn't)(different punctuation):
    #   Anyway, he was a philosophy major and the job market isn't exactly crying out for those, so he decided to become a rock legend.
    #   Anyway he was a philosophy major and the job market is not exactly crying out for those, so he decided to become a rock legend.
    #   --> Might be a matter of not doing all the parses, need to to them all
    #
    # It is very slow to generate all the parses to find the template: has to be at compile time
    # It does mean that converting the nouns might be challenging.  Need to cache those? Or pregenerate?

    with open(log_file_path, "a") as file:
        mrs_parser = MrsParser(log_file=file)
        start_index = 0
        for sentence in test_sentences(start_index):
            logger.info(f"\n\n***** sentence {start_index} *****")
            round_trip(mrs_parser, sentence)
            start_index += 1

    # print(article_for_fragment("dog", False))
    # print(article_for_fragment("friend that doesn't show up on time", False))
    # print(article_for_fragment("water", False))
    # print(article_for_fragment("scissors", False))
    # print(article_for_fragment("rain", False))
    # print(article_for_fragment("novels", False))
