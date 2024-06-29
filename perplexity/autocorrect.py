import json
import logging
import os
import re

from perplexity import world_registry


def autocorrect(autocorrect_file, phrase):
    phrase = phrase.strip()
    if autocorrect_file is None:
        pipeline_logger.debug(f"No autocorrect file loaded")
        return phrase

    else:
        autocorrectMap = autocorrect_file["Map"]

        def lookupAlternative(match):
            alternatives = autocorrectMap[match]
            pipeline_logger.debug(f"Autocorrecting to: {alternatives}")
            if len(alternatives) == 1:
                return alternatives[list(alternatives)[0]]
            else:
                # The only time there should be more than one alternative is if there is a
                # sentence and non-sentence version
                assert "sentence" in alternatives
                isSentence = phrase.lower().strip() == match.lower().strip()
                if isSentence:
                    return alternatives["sentence"]
                else:
                    for item in alternatives.items():
                        if item[0] != "sentence":
                            return item[1]

        def translate(match):
            return lookupAlternative(match.group(0))

        def translateInsensitive(match):
            return lookupAlternative(match.group(0).lower())

        if "Re" in autocorrect_file:
            phrase = autocorrect_file["Re"].sub(translate, phrase)

        if "InsensitiveRe" in autocorrect_file:
            return autocorrect_file["InsensitiveRe"].sub(translateInsensitive, phrase)
        else:
            return phrase


def get_cased_path(path, filename):
    for file in os.listdir(path):
        casedPath = os.path.join(path, file)
        if os.path.isfile(casedPath) and file.lower() == filename:
            return casedPath

    return os.path.join(path, filename)


def get_autocorrect(world_name):
    scriptPath = os.path.dirname(os.path.realpath(__file__))
    with open(get_cased_path(scriptPath, f"sharedautocorrect.txt")) as file:
        autocorrect = json.loads(file.read())

    world_path = world_registry.world_path(world_name)

    autocorrectPath = get_cased_path(world_path, f"{world_name}autocorrect.txt")
    if os.path.exists(autocorrectPath):
        pipeline_logger.debug(f"Loading autocorrect: {autocorrectPath}")
        with open(autocorrectPath) as file:
            autocorrect.update(json.loads(file.read()))
    else:
        pipeline_logger.debug(f"No game specific autocorrect at: {autocorrectPath}")

    regexString = ""
    stringStart = ""
    regexInsensitiveString = ""
    insensitiveStringStart = ""
    for item in autocorrect.items():
        key = item[0]
        for replacement in item[1].items():
            replacementType = replacement[0]
            if replacementType == "initial word":
                # \b means word break so we don't match partials
                regexInsensitiveString += '{}^\\s*{}\\b'.format(insensitiveStringStart, re.escape(key))
                insensitiveStringStart = "|"
            elif replacementType == "word":
                # \b means word break so we don't match partials
                regexString += f'{stringStart}\\b{re.escape(key)}\\b'
                stringStart = "|"
            elif replacementType == "caseInsensitiveWords":
                regexInsensitiveString += "{}{}".format(insensitiveStringStart, re.escape(key))
                insensitiveStringStart = "|"
            elif replacementType == "unquotedCaseInsensitiveWords":
                # (?<!")was the(?!")
                regexInsensitiveString += "{}(?<!['\"]){}(?![\"'])".format(insensitiveStringStart, re.escape(key))
                insensitiveStringStart = "|"
            elif replacementType == "sentence":
                regexString += '{}^{}$'.format(stringStart, re.escape(key))
                stringStart = "|"
            else:
                raise Exception(f"Unknown autocorrect type {replacementType}")

    autocorrectRe = re.compile(regexString) if regexString != "" else None
    autocorrectInsensitiveRe = re.compile("{}".format(regexInsensitiveString), re.IGNORECASE) if regexInsensitiveString != "" else None

    autocorrect_file = {"Map": autocorrect}
    if autocorrectRe:
        autocorrect_file["Re"] = autocorrectRe
    if autocorrectInsensitiveRe:
        autocorrect_file["InsensitiveRe"] = autocorrectInsensitiveRe

    return autocorrect_file


pipeline_logger = logging.getLogger('Pipeline')
