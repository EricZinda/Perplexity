# Returns a dict:
# {
#     "Surface" : True | False
#     "Lemma" : "go"...
#     "Pos" : "v"...
#     "PredicateRaw":
#     "Sense": "dir"...
# }
import logging
import sys


def parse_predication_name(name):
    result = {"PredicateRaw": name}

    if name[0] == "_":
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
            # if we don't have a lemma yet
            if "Lemma" in result and item in ["q", "p", "n", "v", "j", "a", "r"]:
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


def sentence_force(mrs):
    index_variable = mrs["Index"]
    return mrs["Variables"][index_variable]["SF"]


def ShowLogging(name, level=logging.DEBUG):
    logger = logging.getLogger(name)
    logger.setLevel(level)
    formatter = logging.Formatter('%(name)s %(asctime)s: %(message)s')
    file_handler = logging.StreamHandler(sys.stdout)
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)


pipeline_logger = logging.getLogger('Pipeline')
