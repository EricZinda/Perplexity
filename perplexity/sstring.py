# Much code and approach taken from https://github.com/rinslow/fstring
import re
import inspect
from perplexity.response import PluralMode
from perplexity.generation_mrs import english_for_variable_using_mrs, round_trip_mrs
from perplexity.tree import MrsParser, find_predication_from_introduced


INDICATOR_PATTERN = re.compile(r"(\{[^{}]+?\})", re.MULTILINE | re.UNICODE)


# Creates a formatted string using the format described in parse_s_string_element.
#
# Usage:
#     x = 6
#     y = 7
#     print fstring("x is {x} and y is {y}")
#     # Prints: x is 6 and y is 7
def sstringify(origin, mrs=None, tree=None):
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
        value = format_object.format(mrs, tree)
        if value is None:
            value = "<unknown>"
        sstringified = sstringified.replace(match, str(value))

    return sstringified.replace("\x15", "{").replace("\x16", "}")


class SStringFormat(object):
    def __init__(self, raw_variable=None, delphin_variable=None, string_literal=None, plural_template_variable=None, plural_template_literal=None, determiner=None, plural=None, initial_cap=None):
        self.delphin_variable = delphin_variable
        self.raw_variable = raw_variable
        self.string_literal = string_literal
        self.plural_template_variable = plural_template_variable
        self.plural_template_literal = plural_template_literal
        self.determiner = determiner
        self.plural = plural
        self.initial_cap = initial_cap

    def value_is_raw_variable(self):
        return self.raw_variable is not None

    def value_is_delphin_variable(self):
        return self.delphin_variable is not None

    def has_plural_template(self):
        return self.plural_template_literal or self.plural_template_variable

    def plural_template_is_delphin_variable(self):
        return self.plural_template_variable is not None

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

    def resolve_variable(self, variable):
        frame = self.get_frame_by_variable_name(variable, skip_to_level=4)
        try:
            return eval(variable, None, frame)  # pylint: disable=eval-used

        # This is to handle a multi-line string.
        # Once again, this is a dirty hack. I need to
        # Re-implement this using format()
        except SyntaxError:
            return eval(variable.replace("\n", ""), None, frame)  # pylint: disable=eval-used

    def format(self, mrs, tree):
        # First resolve the template if it exists
        if self.has_plural_template():
            if self.plural_template_is_delphin_variable():
                template_variable_name = self.resolve_variable(self.plural_template_variable)
                template_variable_properties = mrs.variables.get(template_variable_name, {})
                plural_string = template_variable_properties.get("NUM", None)
                resolved_plural = {"pl": PluralMode.plural, "sg": PluralMode.singular, None: PluralMode.as_is}[plural_string]

            else:
                assert False, "todo: look up plural based on word"

        else:
            resolved_plural = self.plural

        # Next resolve the variable
        if self.value_is_raw_variable():
            variable_value = self.resolve_variable(self.raw_variable)
            return variable_value

        if self.value_is_delphin_variable():
            variable_name = self.resolve_variable(self.delphin_variable)
            formatted_string, _, _ = english_for_variable_using_mrs(mrs_parser, mrs, tree, variable_name, plural=resolved_plural, determiner=self.determiner)
            # if formatted_string is None:
            #     return english_for_delphin_variable(failure_index, variable_name, tree_info, default_a_quantifier=True, singular_unquantified=False):
            #
            #     return english_for_variable_using_mrs()
            return formatted_string


# Elements of an s-string have the format {determiner variable:format} or {determiner "string":format}
#
# - variable is interpreted as a variable that contains a string representing a DELPH-IN variable
# - *variable is interpreted as a variable that contains a raw string
# - "string" is interpreted as a raw string
#
# determiner: put "a", "an", "the" or "bare" as the first word in {} like {a arg1}
#
# format: how to shape the word represented by "string" or variable
#   Capitalize: Capitalize the article if there is one OR use "Bare" as the article
#   Format Specifiers: after ":" put:
#       sg : singular
#       pl : plural
#       <nothing>: leave as-is
#       <var: match the singular or plural of whatever DELPH-IN var contains
#
# Examples:
# g("{the arg2:sg}
# g("{arg2} {'is': <arg2} not {arg1}", tree_info["Tree"])
# g("{arg2:sg} {arg2:pl}
#
# returns a SStringFormat object
def parse_s_string_element(raw_string):
    # Defaults are "leave as is" if nothing is specified
    determiner = None
    initial_cap = None
    plural = PluralMode.as_is
    plural_template_literal = None
    plural_template_variable = None
    string_literal = None
    delphin_variable = None
    raw_variable = None

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
        if format_raw == "sg":
            plural = PluralMode.singular
        elif format_raw == "pl":
            plural = PluralMode.plural
        elif format_raw == "":
            plural = PluralMode.as_is
        elif format_raw[0] == "<":
            plural_template_raw = format_raw[1:].strip()
            if plural_template_raw[0] in ["\"", "'"]:
                plural_template_literal = plural_template_raw[1:-1]
            else:
                plural_template_variable = plural_template_raw

        else:
            raise SyntaxError(f"s-string: '{format_raw}' is not a plural format.  Must be: 'sg', 'pl', pr '<var'")

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
                         determiner=determiner,
                         plural=plural,
                         initial_cap=initial_cap)


mrs_parser = MrsParser()


if __name__ == '__main__':
    # Bugs:
    # "The raging party in my house has started"
    # "Load the lofty goal"
    raw_text = "test"
    print(sstringify("raw text: {*raw_text}"))

    # Test Harness
    phrase = "what is a folder in?"
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
                    print(f"\n{variable} --> {find_predication_from_introduced(tree, variable)}")
                    print_variable = False

                print(sstringify("the singular: {the variable:sg}", mrs, tree))
                print(sstringify("a singular:   {a variable:sg}", mrs, tree))
                print(sstringify("the plural:   {the variable:pl}", mrs, tree))
                print(sstringify("Bare plural:  {Bare variable:pl}", mrs, tree))
                print(sstringify("bare singular: {variable:sg}", mrs, tree))
                print()

            if print_variable:
                print(f"\n{variable} -> <no tree>")

