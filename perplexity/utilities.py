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


def sentence_force_from_tree_info(tree_info):
    return sentence_force(tree_info["Index"], tree_info["Variables"])


def sentence_force(index_variable, variables):
    return variables[index_variable]["SF"]


def ShowLogging(name, level=logging.DEBUG):
    logger = logging.getLogger(name)
    logger.setLevel(level)
    formatter = logging.Formatter('%(name)s %(asctime)s: %(message)s')
    file_handler = logging.StreamHandler(sys.stdout)
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)


pipeline_logger = logging.getLogger('Pipeline')
