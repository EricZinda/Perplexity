# Much code and approach taken from https://github.com/rinslow/fstring
import logging
import re
import inspect
from delphin.codecs import simplemrs
from perplexity.generation import english_for_delphin_variable, PluralMode, is_plural_word, change_to_plural_mode
from perplexity.generation_mrs import english_for_variable_using_mrs
from perplexity.tree import MrsParser, find_predication_from_introduced, find_predication_conjunction_from_introduced
from perplexity.utilities import ShowLogging

INDICATOR_PATTERN = re.compile(r"(\{[^{}]+?\})", re.MULTILINE | re.UNICODE)


# Elements of an s-string have the format {determiner variable:format} or {determiner "string":format}
#
# - variable is interpreted as a variable that contains a string representing a DELPH-IN variable
# - *variable is interpreted as a variable that contains a raw *singular form* word
# - "string" is interpreted as a raw string that is in *singular form*
#
# The variable value can be a list in order to specify something richer:
#   ["AtPredication", TreePredication, variable]: Evaluate variable English meaning at the index specified by TreePredication
#   ["AfterFullPhrase", variable]: Evaluate variable English meaning after the whole tree
#
# determiner: put "a", "an", "the" or "bare" as the first word in {} like {a arg1}
#
# format: how to shape the word represented by "string" or variable
#   Capitalize: Capitalize the article if there is one OR use "Bare" as the article
#   Format Specifiers: after ":" put:
#       sg : singular
#       pl : plural
#       <nothing>: leave as-is
#       <var: match the singular or plural of whatever DELPH-IN variable contains
#       <*noun_var: ditto but for a variable containing a *noun* that is not a DELPH-IN variable
#       <"dogs": ditto but for a *noun* string literal

# meaning_at_index: which predication index in the Tree should mark the end of converting to English
#   @variable: variable holds the index that should be used
#
# Examples:
# g("{the arg2:sg}
# g("{arg2} {'is': <arg2} not {arg1}", tree_info["Tree"])
# g("{arg2:sg} {arg2:pl}

# g("{the x6:sg} x6=water
# g("{arg2} {'is': <arg2} not {arg1}", tree_info["Tree"])
# g("{arg2:sg} {arg2:pl}
#
# returns a SStringFormat object
def s(origin, tree_info=None, reverse_pronouns=False):
    return sstringify(origin, tree_info, reverse_pronouns=reverse_pronouns)


def sstringify(origin, tree_info=None, reverse_pronouns=False):
    # This is a really dirty hack that I need to find a better, cleaner,
    # more stable and better performance solution for.
    sstringified = re.sub(r"(?:{{)+?", "\x15", origin)[::-1]
    sstringified = re.sub(r"(?:}})+?", "\x16", sstringified)[::-1]

    if "{}" in sstringified:
        raise SyntaxError("fstring: empty expression not allowed")

    offset = 0
    for char in sstringified:
        if char == "{":
            offset += 1
        elif char == "}":
            offset -= 1

    if offset != 0:
        raise SyntaxError("f-string: unbalanced curly braces'")

    for match in INDICATOR_PATTERN.findall(sstringified):
        indicator = match[1:-1]
        format_object = parse_s_string_element(indicator)
        value = format_object.format(tree_info, reverse_pronouns=reverse_pronouns)
        if value is None:
            value = "<unknown>"
        sstringified = sstringified.replace(match, str(value))

    return sstringified.replace("\x15", "{").replace("\x16", "}")


class SStringFormat(object):
    def __init__(self, raw_variable=None,
                 delphin_variable=None,
                 string_literal=None,
                 plural_template_delphin=None,
                 plural_template_variable=None,
                 plural_template_literal=None,
                 determiner=None,
                 plural=None,
                 initial_cap=None,
                 meaning_at_index_variable=None,
                 original_text=None):
        self.delphin_variable = delphin_variable
        self.raw_variable = raw_variable
        self.string_literal = string_literal
        self.plural_template_delphin = plural_template_delphin
        self.plural_template_variable = plural_template_variable
        self.plural_template_literal = plural_template_literal
        self.determiner = determiner
        self.plural = plural
        self.initial_cap = initial_cap
        self.meaning_at_index_variable = meaning_at_index_variable
        self.original_text = original_text

    def __repr__(self):
        variable = f"delphin({self.delphin_variable})" if self.value_is_delphin_variable() else f"raw({self.raw_variable})" if self.value_is_raw_variable() else f"'{self.string_literal}'"
        return f"{'CAP+' if self.initial_cap else ''}{self.determiner} {variable}:{self.plural}{('@' + self.meaning_at_index_variable) if self.meaning_at_index_variable is not None else ''}"

    def value_is_raw_variable(self):
        return self.raw_variable is not None

    def value_is_delphin_variable(self):
        return self.delphin_variable is not None

    def has_plural_template(self):
        return self.plural_template_literal or self.plural_template_variable or self.plural_template_delphin

    def plural_template_is_delphin_variable(self):
        return self.plural_template_delphin is not None

    # By default skip_to_level = 2 which means:
    # 0 skip this level
    # 1 skip the caller (since they wouldn't be trying to resolve their own variables)
    # 2 go to the caller of the caller
    def get_frame_by_variable_name(self, name, skip_to_level=2):
        frame = inspect.stack()[skip_to_level][0]
        while name not in frame.f_locals:
            frame = frame.f_back
            if frame is None:
                return dict()

        return frame.f_locals

    def resolve_variable(self, indicator_expression):
        # Lookup just the first variable name (i.e. foo) in an expression like foo.bar.goo
        initial_variable_name = next(iter(filter(None, re.split(r"(\w+)", indicator_expression))))
        frame = self.get_frame_by_variable_name(initial_variable_name, skip_to_level=4)
        try:
            # ... but then evaluate the whole expression
            return eval(indicator_expression, None, frame)  # pylint: disable=eval-used

        # This is to handle a multi-line string.
        # Once again, this is a dirty hack. I need to
        # Re-implement this using format()
        except SyntaxError:
            return eval(indicator_expression.replace("\n", ""), None, frame)  # pylint: disable=eval-used
        except NameError:
            if indicator_expression.find("@") != -1:
                raise SyntaxError(f"{indicator_expression} is not defined. Did you forget a ':'?")
            else:
                raise SyntaxError(f"{indicator_expression} is not defined")

    def _convert_complex_variable(self, variable_name):
        if isinstance(variable_name, list):
            sstring_logger.debug(f"sstring: variable is complex: '{variable_name}'")
            if variable_name[0] == "AtPredication":
                # Use the English for this variable as if the
                # error happened at the specified predication
                # instead of where it really happened
                if isinstance(variable_name[1], list):
                    specified_meaning_at_index_value = variable_name[1][-1].index
                else:
                    specified_meaning_at_index_value = variable_name[1].index
                sstring_logger.debug(f"sstring: error predication index is: {specified_meaning_at_index_value}")
                variable_name = variable_name[2]

            elif variable_name[0] == "AfterFullPhrase":
                specified_meaning_at_index_value = 100000000
                variable_name = variable_name[1]

            return variable_name, specified_meaning_at_index_value

        else:
            return variable_name, None

    def format(self, tree_info, reverse_pronouns=False):
        if tree_info is not None:
            mrs = simplemrs.loads(tree_info["MRS"])[0]
            tree = tree_info["Tree"]
            sstring_logger.debug(f"sstring: tree is: {tree.repr_with_indices()}")

        else:
            mrs = None
            tree = None

        sstring_logger.debug(f"sstring: original text is: '{self.original_text}'")
        # First resolve the template if it exists
        if self.has_plural_template():
            if self.plural_template_is_delphin_variable():
                template_variable_name = self.resolve_variable(self.plural_template_delphin)
                template_variable_name, _ = self._convert_complex_variable(template_variable_name)

                template_variable_properties = mrs.variables.get(template_variable_name, {})
                plural_string = template_variable_properties.get("NUM", None)

            else:
                if self.plural_template_variable:
                    plural_template_value = self.resolve_variable(self.plural_template_variable)
                else:
                    plural_template_value = self.plural_template_literal

                sstring_logger.debug(f"sstring: plural template is: {plural_template_value}")

                if str(plural_template_value).isnumeric():
                    plural_string = "pl" if float(plural_template_value) > 1 else "sg"
                else:
                    plural_string = "pl" if is_plural_word(plural_template_value) else "sg"

            resolved_plural = {"pl": PluralMode.plural, "sg": PluralMode.singular, None: PluralMode.as_is}[plural_string]

        else:
            resolved_plural = self.plural

        sstring_logger.debug(f"sstring: plural is: {resolved_plural}")

        # Next resolve the variable
        if self.value_is_delphin_variable():
            if tree_info is None:
                raise SyntaxError("sstringify must have a tree_info argument if a DELPH-IN variable is being used")

            variable_name = self.resolve_variable(self.delphin_variable)
            sstring_logger.debug(f"sstring: variable_name is '{variable_name}'")

            # If the variable value is not just a variable value, decode it
            specified_meaning_at_index_value = None
            variable_name, specified_meaning_at_index_value = self._convert_complex_variable(variable_name)

            # Now that we have the variable, resolve the meaning_at_index_variable
            conjunction_for_variable = find_predication_conjunction_from_introduced(tree, variable_name)
            if conjunction_for_variable is None:
                raise SyntaxError(f"Can't find predication for variable '{variable_name}'. Are you missing a '*'?")

            else:
                # Add 1 to the last predication in the conjunction since we want the meaning *after* the predication
                # introducing it has been successfully processed. This is because we want the word representing it
                # to have been processed by default
                meaning_at_index_default = conjunction_for_variable[-1].index + 1

            sstring_logger.debug(f"sstring: default meaning_at_index is '{meaning_at_index_default}'")
            if self.meaning_at_index_variable is None and specified_meaning_at_index_value is None:
                meaning_at_index_value = meaning_at_index_default
                sstring_logger.debug(f"sstring: meaning_at_index not specified, using default: '{meaning_at_index_value}'")

            elif specified_meaning_at_index_value is not None:
                meaning_at_index_value = int(specified_meaning_at_index_value)
                sstring_logger.debug(f"sstring: meaning_at_index specified by complex variable: {meaning_at_index_value}")

            else:
                meaning_at_index_value = self.resolve_variable(self.meaning_at_index_variable)
                sstring_logger.debug(f"sstring: meaning_at_index specified: '{meaning_at_index_value}'")

            formatted_string, _, _ = english_for_variable_using_mrs(mrs_parser, mrs, meaning_at_index_value, variable_name, tree, plural=resolved_plural, determiner=self.determiner, reverse_pronouns=reverse_pronouns)
            #
            # if meaning_at_index_value == meaning_at_index_default:
            #     # We only know how to use ACE if we are talking about a variable's meaning
            #     # from the point where it is introduced
            #     sstring_logger.debug(f"sstring: default meaning_at_index: trying MRS generation")
            #     formatted_string, _, _ = english_for_variable_using_mrs(mrs_parser, mrs, meaning_at_index_value, variable_name, tree, plural=resolved_plural, determiner=self.determiner)
            #
            # else:
            #     sstring_logger.debug(f"sstring: non-default meaning_at_index: only use fallback")
            #     formatted_string = None

            if formatted_string is not None:
                sstring_logger.debug(f"sstring MRS generated: {variable_name}[{self}]={formatted_string}")

            else:
                # If ACE can't be used, fall back to a simplistic approach
                sstring_logger.debug(f"sstring: MRS failed, try fallback")
                formatted_string = english_for_delphin_variable(meaning_at_index_value, variable_name, tree_info, plural=resolved_plural, determiner=self.determiner, reverse_pronouns=reverse_pronouns)
                sstring_logger.debug(f"sstring: Fallback generated: {variable_name}[{self}]={formatted_string}")

            return formatted_string

        else:
            if self.value_is_raw_variable():
                singular_variable_value = self.resolve_variable(self.raw_variable)
            else:
                singular_variable_value = self.string_literal

            return change_to_plural_mode(singular_variable_value, resolved_plural)


def parse_s_string_element(raw_string):
    # Defaults are "leave as is" if nothing is specified
    determiner = None
    initial_cap = None
    plural = PluralMode.as_is
    plural_template_literal = None
    plural_template_variable = None
    plural_template_delphin = None
    string_literal = None
    delphin_variable = None
    raw_variable = None
    meaning_at_index_variable = None

    # See if a determiner was specified
    # If so, use it to determine initial_cap and determiner
    space_index = raw_string.find(" ")
    if space_index > 0:
        determiner = raw_string[0:space_index].strip()
        if len(determiner) > 0:
            if determiner not in ["The", "the", "A", "a", "An", "an", "Bare", "bare"]:
                raise SyntaxError(f"s-string: '{determiner}' is not a valid determiner")
            else:
                initial_cap = determiner[0].isupper()
                if determiner in ["Bare", "bare"]:
                    determiner = ""
        else:
            determiner = None

    # Now parse the format, i.e. the "arg2:..." part
    word_format_raw = raw_string[(space_index + 1) if space_index != -1 else 0:]
    expression_parts = word_format_raw.split(":")
    if len(expression_parts) == 2:
        word_raw = expression_parts[0].strip()
        format_raw = expression_parts[1].strip()
        plural_index_raw = format_raw.split("@")
        if len(plural_index_raw) == 2:
            plural_raw = plural_index_raw[0]
            index_raw = plural_index_raw[1]
        else:
            plural_raw = plural_index_raw[0]
            index_raw = None

        # Deal with the plural indicator
        if plural_raw == "sg":
            plural = PluralMode.singular
        elif plural_raw == "pl":
            plural = PluralMode.plural
        elif plural_raw == "":
            plural = PluralMode.as_is
        elif plural_raw[0] == "<":
            plural_template_raw = plural_raw[1:].strip()
            if plural_template_raw[0] in ["\"", "'"]:
                plural_template_literal = plural_template_raw[1:-1]
            elif plural_template_raw[0] == "*":
                plural_template_variable = plural_template_raw[1:]
            else:
                plural_template_delphin = plural_template_raw
        else:
            raise SyntaxError(f"s-string: '{plural_raw}' is not a plural format.  Must be: 'sg', 'pl', pr '<var'")

        # Deal with the meaning_at_index indicator
        if index_raw is not None:
            meaning_at_index_variable = index_raw

    elif len(expression_parts) == 1:
        word_raw = word_format_raw.strip()

    else:
        raise SyntaxError(f"s-string: '{word_format_raw}' is not a valid format.  Some valid examples: {{the var:sg}} or {{value:<var}}")

    # Now deal with the word_raw part
    if word_raw[0] in ["\"", "'"]:
        string_literal = word_raw[1:-1]
    elif word_raw[0] == "*":
        raw_variable = word_raw[1:]
    else:
        delphin_variable = word_raw

    return SStringFormat(raw_variable=raw_variable,
                         delphin_variable=delphin_variable,
                         string_literal=string_literal,
                         plural_template_variable=plural_template_variable,
                         plural_template_literal=plural_template_literal,
                         plural_template_delphin=plural_template_delphin,
                         determiner=determiner,
                         plural=plural,
                         initial_cap=initial_cap,
                         meaning_at_index_variable=meaning_at_index_variable,
                         original_text=raw_string)


mrs_parser = MrsParser()

sstring_logger = logging.getLogger('SString')

if __name__ == '__main__':
    ShowLogging("SString")
    ShowLogging("Generation")

    test = "a dog"
    print(sstringify("{the *test}"))

    # Bugs:
    # "The raging party in my house has started"
    # "Load the lofty goal"
    raw_text = "is"
    plural_word = "2"
    print(sstringify("raw text: {*raw_text:<*plural_word}"))

    print(sstringify("raw text: {*raw_text}"))


    # Test Harness
    from perplexity.generation_experimental import round_trip_mrs

    phrase = "which files in this folder are not large?"
    gen_index, _, mrs = round_trip_mrs(mrs_parser, phrase)
    if mrs is None:
        print(f"Couldn't round trip: {phrase}")

    else:
        # Find all x variables
        variables = []
        for variable_item in mrs.variables.items():
            if variable_item[0][0] == "x":
                variables.append(variable_item[0])

        # Convert every x variable to english
        for variable in variables:
            print_variable = True
            for tree in mrs_parser.trees_from_mrs(mrs):


                if print_variable:
                    print(f"\n{tree.repr_with_indices()}")
                    print(f"\n{variable} --> {find_predication_from_introduced(tree, variable)}")
                    print_variable = False

                after_tree = 999
                variable_after_phrase = ["AfterFullPhrase", variable]
                variable_before_phrase = ["AtPredication", tree, variable]
                tree_info = {"Index": mrs.index,
                             "Variables": mrs.variables,
                             "Tree": tree,
                             "MRS": mrs_parser.mrs_to_string(mrs)}

                test = ["AfterFullPhrase", 'x3']
                print(sstringify("{test}", tree_info))

                index_test = 4
                print(sstringify("raw default: {variable}", tree_info))
                print(sstringify("raw before tree using 'AtPredication': {variable_before_phrase}", tree_info))
                print(sstringify("raw after tree: {variable:@after_tree}", tree_info))
                print(sstringify("raw after tree using 'AfterFullPhrase': {variable_after_phrase}", tree_info))
                print(sstringify("the singular: {the variable:sg}", tree_info))
                print(sstringify("a singular:   {a variable:sg}", tree_info))
                print(sstringify("the plural:   {the variable:pl}", tree_info))
                print(sstringify("Bare plural:  {Bare variable:pl}", tree_info))
                print(sstringify("Bare original:  {bare variable}", tree_info))
                print(sstringify("bare singular: {variable:sg}", tree_info))
                print()

            if print_variable:
                print(f"\n{variable} -> <no tree>")

