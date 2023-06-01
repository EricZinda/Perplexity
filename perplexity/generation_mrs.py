import copy
import difflib
import logging
import inflect
from delphin.mrs import EP, MRS, has_intrinsic_variable_property, plausibly_scopes, \
    has_complete_intrinsic_variables, has_unique_intrinsic_variables
from perplexity.generation import PluralMode
from perplexity.tree import MrsParser, rewrite_tree_predications, TreePredication, \
    find_predication_from_introduced
from perplexity.utilities import parse_predication_name


# Generator that yields the differences between an original and the ACE generated version of it
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


# Compare the original and ACE generated version of a text
# Ignore non-important differences and return a list of diffs
# if the list is [], they are effectively the same
def compare_generated_output(original, generated):
    # Basic cleaning of input
    original = original.strip(" .?!")
    generated = generated.strip(" .?!")

    diffs = []
    for subtractions, additions in diff_generator(original.lower(), generated.lower()):
        # twenty-forth round trips to twenty forth
        if len(subtractions) == len(additions) and additions.replace("-", " ") == subtractions:
            continue

        # Make numbers and their textual versions compare the same
        if additions.isdigit() and inflect_engine.number_to_words(additions) == subtractions or \
                subtractions.isdigit() and inflect_engine.number_to_words(subtractions) == additions:
            continue

        diffs.append(f"{additions} <--> {subtractions}")

    return diffs


# Given an MRS and Tree that represents a phrase, generate a
# new MRS that represents what variable means at the point in tree up to,
# but not including failure_index.  Modifies the original to match whatever plural or determiner
# specify.  If None, just leaves as-is
#
# returns the new MRS or None if an MRS wasn't able to be built that generates the fragment
def mrs_fragment_from_variable(mrs, failure_index, variable, tree, plural=None, determiner=None):
    def rewrite_tree_without_fragment_body(predication, index_by_ref):
        nonlocal pruned_body
        nonlocal mrs
        nonlocal new_eps
        nonlocal new_variables
        nonlocal plural
        nonlocal can_generate_fragment
        new_variables.add(predication.mrs_predication.label)
        for arg_item in predication.mrs_predication.args.items():
            if arg_item[0] != "CARG":
                new_variables.add(arg_item[1])

        predication_data = parse_predication_name(predication.name)
        if predication_data["Pos"] == "q" and predication.args[0] == variable:
            predication_copy = copy.deepcopy(predication)
            predication_copy.index = index_by_ref[0]
            index_by_ref[0] += 1

            # Remove any predications in the RSTR that are >= failure_index
            copy_rstr_arg_list = [predication_copy.args[1]] if not isinstance(predication_copy.args[1], list) else predication_copy.args[1]
            new_arg_list = []
            for pred in copy_rstr_arg_list:
                if pred.index < failure_index:
                    new_arg_list.append(pred)

            # We only know how to generate the fragment if the failure_index is between
            # the index of the quantifier that quantifiers the variable
            # and the index of the first predication in the body
            first_body_index = predication_copy.args[2].index if not isinstance(predication_copy.args[2], list) else predication_copy.args[2][0].index
            can_generate_fragment = predication_copy.index < failure_index <= first_body_index

            predication_copy.args[1] = rewrite_tree_predications(new_arg_list, rewrite_tree_without_fragment_body, index_by_ref)
            pruned_body = predication_copy.args[2]
            # Assuming the index was introduced by something that got pruned,
            # that's why we can reuse it as ARG0
            index_predication = find_predication_from_introduced(pruned_body, mrs.index)
            if not index_predication:
                pruned_body = None

            else:
                if determiner in ["a", "an"] or predication.mrs_predication.predicate in ["_which_q", "which_q"]:
                    will_be_plural = ("NUM" in mrs.variables[variable] and mrs.variables[variable]["NUM"] == "pl" and plural != PluralMode.singular) or \
                        plural == PluralMode.plural

                    if not will_be_plural:
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

    # Returns a the list of hcons that are still valid given
    # the list of new_eps
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
    can_generate_fragment = True
    # rewrite_tree_without_fragment_body will modify many of the above variables during
    # its processing
    rewrite_tree_predications(tree, rewrite_tree_without_fragment_body, index_by_ref)
    if pruned_body is None or not can_generate_fragment:
        # This tree or the failure_index is not in a form we know how to prune
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
        logger.debug(f"Nothing could be generated for: {original_text}: {new_mrs_string}")
        return None, None


def fragmentize_phrase(phrase):
    phrase = phrase[0].lower() + phrase[1:]
    return phrase.strip(".?!")


def english_for_variable_using_mrs(mrs_parser, mrs, failure_index, variable, tree, plural=None, determiner=None):
    # Get the MRS fragment for the variable
    new_mrs = mrs_fragment_from_variable(mrs, failure_index, variable, tree, plural, determiner)
    if new_mrs is None:
        return None, None, None

    else:
        if plural is not None and plural != PluralMode.as_is:
            mrs.variables[variable]["NUM"] = "pl" if plural == PluralMode.plural else "sg"

        # Figure out which generated text from the fragment best matches the original
        best_index, generated_text = best_generation_index(new_mrs, mrs.surface)
        return fragmentize_phrase(generated_text) if generated_text is not None else generated_text, best_index, new_mrs


inflect_engine = inflect.engine()
logger = logging.getLogger("SString")
