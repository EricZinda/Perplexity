import copy
import enum
import functools
import inspect
import itertools
import json
import logging
import perplexity.plurals
import os
from typing import NamedTuple
import re
import perplexity.execution
import perplexity.tree
from perplexity.transformer import build_transformed_tree, TransformerMatch
from perplexity.utilities import parse_predication_name, system_added_state_arg, system_added_arg_count, \
    system_added_context_arg, system_added_group_arg_count
from perplexity.variable_binding import VariableBinding


class EventOption(enum.Enum):
    optional = 1
    required = 2


# Used to indicate when the value of something should be only one or more than one
#
# Can be set on arguments for a predication to indicate what
# kind of plural it handles. Helps the system remove alternatives: When
# no predications have a special handling of sets > 1, don't generate them
class ValueSize(enum.Enum):
    exactly_one = 1  # default
    more_than_one = 2
    all = 3


def override_predications(vocabulary, library, name_list):
    vocabulary.override_predications(library, name_list)


def Transform(vocabulary):
    def PredicationDecorator(function_to_decorate):
        vocabulary.add_transform(function_to_decorate())

    return PredicationDecorator


# Converts phrases that have alternative words separated by "|"
# into a list that is either strings or lists of alternative words so the alternatives can be
# created by generate_alternative_examples()
#
# "foo|bar|goo is a word|other" --> [["foo", "bar", "goo"], " is a ", ["word", "other"]]
# "foo|bar is a word|other"
# "foo|bar is a word"
# "foo is a world|bar"
#
#
# Algorithm:
# If there are previous parts, this is a post
# If there are remaining parts, this is a pre
# If the part is a single word and a pre and post, it is a middle
#
# Start at the beginning
#
# If there is an existing group:
#   If this is a middle:
#       add sole word to group and continue
#   elif this is a post:
#       add post word to group
#       start a new group
#
# If there is not an existing group:
#   If this is a pre:
#       start a group with the pre word
def build_phrase_list(alternative_parts):
    phrase_list = []
    len_parts = len(alternative_parts)
    current_group = None
    for index in range(len_parts):
        stripped_part = alternative_parts[index]

        # Parse into words
        regex = r"[a-zA-z0-9]{1,}"
        test_str = alternative_parts[index]
        match_list = list(re.findall(regex, test_str, re.MULTILINE))

        is_post = index > 0
        if is_post:
            # If there are previous parts, this is a post, the first word is the post
            post_word = match_list[0]

        is_pre = index < len_parts - 1
        if is_pre:
            # If there are remaining parts, this is a pre, the last word is the pre
            pre_word = match_list[-1]

        # If the part is a single word and a pre and post, it is a middle
        is_middle = len(match_list) == 1 and is_pre and is_post

        # Now build the part minus the pre or post words
        if is_middle:
            stripped_part = ""
        else:
            if is_pre:
                stripped_part = stripped_part[:stripped_part.rfind(pre_word)]
            if is_post:
                stripped_part = stripped_part[stripped_part.find(post_word) + len(post_word):]

        if current_group:
            if is_middle:
                current_group.append(pre_word)
                continue
            elif is_post:
                current_group.append(post_word)
                current_group = None

        # If there is not an existing group:
        if not current_group:
            if is_pre:
                # start a group with the pre word
                current_group = [pre_word]
                phrase_list.append(stripped_part)
                phrase_list.append(current_group)

    phrase_list.append(stripped_part)
    return phrase_list


# Generate actual examples given a phrase_list which is a list
# of either strings or lists. For every item in phrase_list which is a list
# It will generate examples that have every combination of items in phrase_list
# which are lists.  For example,
# ["There", ["is", "can be"], ["a dog", "a cat]]
# generates:
# "There is a dog"
# "There is a cat"
# "There can be a dog"
# "There can be a cat"
def generate_alternative_examples(phrase_list):
    if isinstance(phrase_list[0], str):
        if len(phrase_list) > 1:
            for remaining in generate_alternative_examples(phrase_list[1:]):
                yield f"{phrase_list[0]}{remaining}"
        else:
            yield f"{phrase_list[0]}"

    else:
        for alternative in phrase_list[0]:
            if len(phrase_list) > 1:
                for remaining in generate_alternative_examples(phrase_list[1:]):
                    yield f"{alternative}{remaining}"
            else:
                yield f"{alternative}"


# The list of phrase properties much match one of the declarations
def missing_properties(declaration_list, phrase):
    if phrase not in declaration_list:
        return phrase


cached_files = {}


def expand_properties(original_properties):
    if original_properties is not None:
        if not isinstance(original_properties, (list, tuple)):
            original_properties = [original_properties]
        final_properties = []
        for property_template in original_properties:
            for property_combination in itertools.product(
                    *[x if isinstance(x, (list, tuple)) else [x] for x in property_template.values()]):
                final_properties.append(dict(zip(property_template.keys(), property_combination)))
        return final_properties


def store_atomically(path, data):
    tmppath = path + ".tmp"
    with open(tmppath, "w") as output:
        output.write(data)
        output.flush()
        # https://stackoverflow.com/questions/7433057/is-rename-without-fsync-safe
        os.fsync(output.fileno())

    os.replace(tmppath, path)


def put_saved_metadata(decorated_function, metadata):
    all_metadata = get_all_metadata_from_function_file(decorated_function)
    all_metadata[decorated_function.__name__] = metadata
    store_atomically(meta_file_path(decorated_function), json.dumps(all_metadata, indent=4))


def get_saved_metadata(decorated_function):
    cached_file = get_all_metadata_from_function_file(decorated_function)
    return cached_file.get(decorated_function.__name__, {})


def get_all_metadata_from_function_file(decorated_function):
    python_meta_file = meta_file_path(decorated_function)
    if python_meta_file not in cached_files:
        if not os.path.exists(python_meta_file):
            cached_files[python_meta_file] = {}
        else:
            with open(python_meta_file, "r") as file:
                try:
                    cached_files[python_meta_file] = json.loads(file.read())
                except Exception as e:
                    print(f"Error loading {python_meta_file}: {str(e)}")
                    raise 
    return cached_files[python_meta_file]


cached_function_file_times = {}
cached_meta_file_times = {}


def metadata_changed(decorated_function):
    function_file = os.path.abspath(inspect.getfile(decorated_function))
    if function_file not in cached_function_file_times:
        function_file_time = os.path.getmtime(function_file)
        cached_function_file_times[function_file] = function_file_time
    else:
        function_file_time = cached_function_file_times[function_file]

    python_meta_file = function_file + ".plex"
    if os.path.exists(python_meta_file):
        if python_meta_file not in cached_meta_file_times:
            meta_modification_time = os.path.getmtime(python_meta_file)
            cached_meta_file_times[python_meta_file] = meta_modification_time
        else:
            meta_modification_time = cached_meta_file_times[python_meta_file]

        return meta_modification_time <= function_file_time

    else:
        return True


def meta_file_path(decorated_function):
    return os.path.abspath(inspect.getfile(decorated_function)) + ".plex"


# Initial phrase definition format is:
# [("This is a phrase.", ),
#  ("This is another phrase.", )
# ]
#
# Fully specified phrase definition format is:
# [("This is a phrase.", {'SF': 'ques', 'TENSE': 'past', 'MOOD': 'indicative', 'PROG': '-', 'PERF': '-'}),
#  ("This is another phrase.", {'SF': 'ques', 'TENSE': 'past', 'MOOD': 'indicative', 'PROG': '-', 'PERF': '-'})
# ]
def collect_properties(func, phrase_dict):
    properties = []
    if phrase_dict is not None:
        for item in phrase_dict.items():
            if item[1] is not None:
                if item[1] not in properties:
                    properties.append(item[1])

    return properties


# Loop through each phrase:
# - If it has a set of properties, see if it matches any of the MRS properties
# - If not, or if it doesn't match the properties, print out the properties generated
# Use the transforms that are available at the time this is called
#   TODO: Should probably fail if more transformers get loaded later because they could break this analysis
# Ignores vocabulary
def check_phrases(func, vocabulary, predicates, phrase_dict):
    success = True
    found_predicates = set()
    properties_list = []
    mrs_parser = perplexity.tree.MrsParser()
    for phrase_item in phrase_dict.items():
        phrase_declaration = phrase_item[0]
        # If phrase has "word1|word2" in it, split into N examples
        alternatives = phrase_declaration.split("|")
        if len(alternatives) == 1:
            alternative_list = [phrase_declaration]
        else:
            phrase_list = build_phrase_list(alternatives)
            alternative_list = list(generate_alternative_examples(phrase_list))

        for phrase in alternative_list:
            print(f"   parsing example: '{phrase}' ...")
            specified_properties = phrase_item[1]
            non_matching_examples = []
            found_properties_match = False
            for mrs in mrs_parser.mrss_from_phrase(phrase):
                # Just remember one of every alternate tree for this MRS as an example
                # to show in errors
                heads = [x for x in perplexity.tree.syntactic_heads_characteristic_variables(mrs)]
                example_trees = {}
                for tree_orig in mrs_parser.trees_from_mrs(mrs):
                    tree_info_orig = {"Tree": tree_orig,
                                      "Variables": mrs.variables,
                                      "SyntacticHeads": heads}
                    for tree_info in vocabulary.alternate_trees(None, tree_info_orig, yield_original=True):
                        # For each tree that has one of the predicates in it, collect the properties
                        # for the *verb introduced event* variable
                        found = perplexity.tree.find_predication(tree_info["Tree"], predicates)
                        if found is not None:
                            assert found.arg_types[0] == "e", f"verb '{found}' doesn't have event as arg 0"

                            # Get the properties provided for the verb event
                            tree_properties = tree_info["Variables"][found.args[0]]
                            if tree_properties == specified_properties:
                                found_predicates.add(found.name)
                                if tree_properties not in properties_list:
                                    properties_list.append(tree_properties)

                                found_properties_match = True
                                break

                            else:
                                key = tree_info.get("Transformed", None)
                                if key not in example_trees:
                                    example_trees[key] = [tree_info["Tree"], tree_properties]
                        else:
                            non_matching_examples.append(
                                [tree_info["Tree"], f"Did not contain predicates listed for this function: {predicates}"])

                if found_properties_match:
                    break

                else:
                    if len(example_trees) == 0:
                        non_matching_examples.append([tree_orig, f"Did not contain predicates listed for this function: {predicates}"])
                    else:
                        non_matching_examples += example_trees.values()

            if not found_properties_match:
                success = False
                # Either properties weren't specified or none matched it, tell the user what we found
                print(f"      '{specified_properties}' did not match properties in any of the following parses:")
                for example in non_matching_examples:
                    print(f"      {example[0]}: {example[1]}")

    return success, found_predicates, properties_list


# Confirm that the phrases declarations match the properties
# If they do (or there are just properties), return the properties
# Otherwise, Assert
def check_properties(vocabulary, function_to_decorate, names, metadata, phrases, properties, properties_from):
    # If phrases are specified, gather the properties from them
    # If they are valid, save them in metadata
    if phrases:
        if metadata.get("Phrases", []) != phrases:
            print(f"Generating phrase properties for {function_to_decorate}...")
            check_success, found_predicates, phrases_properties_list = check_phrases(function_to_decorate, vocabulary, names, phrases)
            if len(found_predicates) < len(names):
                assert False, f"No examples generated the predicate[s]: {', '.join(set(names).difference(found_predicates))}"
            elif not check_success:
                assert False, f"One or more phrases failed to match properties for its MRSs"

            metadata["Phrases"] = phrases

        else:
            phrases_properties_list = collect_properties(function_to_decorate, phrases)

    else:
        metadata.pop("Phrases", None)
        phrases_properties_list = None

    # Gather the properties declaration
    assert not (properties_from and properties), f"{function_to_decorate} has both a properties= and a properties_from= declaration"
    if properties_from:
        assert hasattr(properties_from, "_delphin_properties"), f"properties_from on {function_to_decorate} references a function with no properties specified"
        properties_to_use = properties_from._delphin_properties
        metadata["PropertiesFrom"] = f"{function_to_decorate.__name__}"
        metadata.pop("Properties", None)
    else:
        metadata.pop("PropertiesFrom", None)
        if properties:
            properties_to_use = expand_properties(properties)
            metadata["Properties"] = properties_to_use
            metadata.pop("PropertiesFrom", None)

        else:
            metadata.pop("Properties", None)
            properties_to_use = None

    # If we have both a properties declaration and phrases,
    # make sure their properties match
    if phrases_properties_list:
        nl = "\n"
        if not properties_to_use or (len(phrases_properties_list) != len(properties_to_use)):
            assert False, f"On {function_to_decorate}\nThe declared properties:\n{nl.join(str(x) for x in properties_to_use) if properties_to_use is not None else 'None'}\n\ndon't match the properties declared by the phrases:\n{nl.join(str(x) for x in phrases_properties_list)}"
        else:
            # Make sure they match
            for phrases_properties in phrases_properties_list:
                if phrases_properties not in properties_to_use:
                    assert False, f"On {function_to_decorate}\nThe declared properties:\n{nl.join(str(x) for x in properties_to_use) if properties_to_use is not None else 'None'}\n\ndon't match the properties declared by the phrases:\n{nl.join(str(x) for x in phrases_properties_list)}"
            for properties_used in properties_to_use:
                if properties_used not in phrases_properties_list:
                    assert False, f"On {function_to_decorate}\nThe declared properties:\n{nl.join(str(x) for x in properties_to_use) if properties_to_use is not None else 'None'}\n\ndon't match the properties declared by the phrases:\n{nl.join(str(x) for x in phrases_properties_list)}"

    # If we got here, everything checks out and the metadata has
    # been updated to match the declaration
    return properties_to_use


def Predication(vocabulary,
                library=None,
                names=None,
                arguments=None,
                phrase_types=None,
                handles=None,
                virtual_args=None,
                matches_lemma_function=None,
                phrases=None,
                properties=None,
                properties_from=None,
                handles_interpretations=None,
                handles_negation=False):
    # Work around Python's odd handling of default arguments that are objects
    if handles is None:
        handles = []
    if virtual_args is None:
        virtual_args = []
    if library is None:
        library = "user"
    if handles_interpretations is not None and not isinstance(handles_interpretations, (list, tuple)):
        handles_interpretations = (handles_interpretations,)

    if handles_interpretations is not None and properties_from is not None and properties_from not in handles_interpretations:
        # if handles_interpretation forces this handler to only be called for one interpretation, it doesn't make sense to use
        # properties from another
        assert False, f"Predication `properties_from={str(properties_from)}` must be None or match `handles_interpretation={str(handles_interpretations)}`"

    # handles = [(Name, EventOption), ...]
    # returns True or False, if False sets an error using report_error
    def ensure_handles_event(context, state, handles, event_binding):
        if isinstance(event_binding, VariableBinding) and event_binding.variable.name[0] == "e":
            # Look at everything in event and make sure it is handled
            if event_binding.value is not None:
                foundItem = False
                for item in event_binding.value.items():
                    for handledItem in handles:
                        if item[0] == handledItem[0]:
                            foundItem = True
                            break

                    if not foundItem:
                        context.report_error(["formNotUnderstood", "notHandled", item], force=True)
                        return False

            # Look at everything it handles and make sure the required things are there
            for item in handles:
                if item[1] == EventOption.required and (event_binding.value is None or item[0] not in event_binding.value):
                    context.report_error(["formNotUnderstood", "missing", item], force=True)
                    return False

        return True

    def arg_types_from_function(function):
        arg_spec = inspect.getfullargspec(function)

        # Skip the first two args since they should always be "context, state"
        arg_list = []
        for arg_index in range(2, len(arg_spec.args)):
            arg_name = arg_spec.args[arg_index]

            # Allow single character arguments like "x" and "e"
            # OR the format: "x_actor"
            if len(arg_name) == 1 or (len(arg_name) > 1 and arg_name[1] == "_"):
                arg_type = arg_name[0]
                if arg_type not in ["u", "i", "p", "e", "x", "h", "c"]:
                    raise Exception(f"Argument {arg_index} of predication {function.__name__} has an unknown argument type of {arg_type}'")

                arg_list.append(arg_type)

        return arg_list

    def argument_metadata(function_to_decorate, arg_spec_list):
        arg_list = []
        if arg_spec_list is None:
            arg_types = arg_types_from_function(function_to_decorate)
            for arg_type in arg_types:
                arg_metadata = {}
                arg_list.append(arg_metadata)
                arg_metadata["VariableType"] = arg_type
                if arg_type == "x":
                    arg_metadata["ValueSize"] = ValueSize.exactly_one

        else:
            for arg_spec in arg_spec_list:
                arg_metadata = {}
                arg_list.append(arg_metadata)
                arg_metadata["VariableType"] = arg_spec[0]
                arg_metadata["ValueSize"] = arg_spec[1] if len(arg_spec) > 1 else ValueSize.exactly_one

        return arg_list

    def phrase_types_from_function(function):
        segments = function.__name__.split("_")
        index_types = []
        for index_type in segments:
            if index_type in ["prop", "ques", "comm", "prop-or-ques", "norm"]:
                index_types.append(index_type)

        return index_types

    def create_virtual_arguments(args, virtual_args):
        new_args = []
        for virtual_arg in virtual_args:
            create_function = virtual_arg[0]
            new_arg = create_function(args)
            if new_arg is not None:
                new_args.append(new_arg)
            else:
                if virtual_arg[1] == EventOption.required:
                    # Couldn't create this arg, fail since it is required
                    # create_function should report an error
                    return None
                else:
                    new_args.append(None)

        return tuple(new_args)

    # Gets called when the function is first created
    # function_to_decorate is the function definition
    def PredicationDecorator(function_to_decorate):
        # First make sure the function provided is a generator
        if not inspect.isgenerator(function_to_decorate) and not inspect.isgeneratorfunction(function_to_decorate):
            assert False, f"function {function_to_decorate.__name__} must be a generator"

        predication_names = names if names is not None else [function_to_decorate.__name__]

        # Compare properties metadata with the cached version, if they are the same
        # don't bother checking again
        properties_to_use = None
        if metadata_changed(function_to_decorate):
            metadata = get_saved_metadata(function_to_decorate)
            check_declaration = metadata.get("Phrases", []) != phrases or metadata.get("Properties", []) != properties or metadata.get("PropertiesFrom") != (properties_from.__name__ if properties_from is not None else None)
            if check_declaration:
                properties_to_use = check_properties(vocabulary, function_to_decorate, names, metadata, phrases, properties, properties_from)
                put_saved_metadata(function_to_decorate, metadata)

        if not properties_to_use:
            properties_to_use = expand_properties(properties)

        # Attach properties to the function object as one way to make
        # properties_from= work, since inspect.getfile() doesn't work right
        # with decorators
        function_to_decorate._delphin_properties = properties_to_use

        # wrapper_function() actually wraps the predication function
        # and is the real function called at runtime
        @functools.wraps(function_to_decorate)
        def wrapper_function(*args, **kwargs):
            # First create any virtual args. This could fail and report an error
            if virtual_args is not None and len(virtual_args) > 0:
                new_args = create_virtual_arguments(args, virtual_args)
                if new_args is None:
                    # One of the args could not be created
                    # Assume it reported an error
                    return

                args = args + new_args

            state = args[system_added_state_arg + extra_arg_in_front_count][0] if is_solution_group else args[system_added_state_arg + extra_arg_in_front_count]
            tree_info = state.get_binding("tree").value[0]

            arg0_index = system_added_group_arg_count + extra_arg_in_front_count if is_solution_group else system_added_arg_count + extra_arg_in_front_count
            if isinstance(args[arg0_index], str):
                arg0_variable_name = args[arg0_index + 1].variable.name
            else:
                if isinstance(args[arg0_index], perplexity.plurals.GroupVariableValues):
                    arg0_variable_name = args[arg0_index].variable_constraints.variable_name
                elif isinstance(args[arg0_index], VariableBinding):
                    arg0_variable_name = args[arg0_index].variable.name
                else:
                    arg0_variable_name = None

            if properties_to_use:
                # Check the properties that the predication can handle vs. what the phrase has
                # Also collect all properties provided for the verb event
                phrase_properties = {}
                assert final_arg_types[0] == "e", f"verb '{function_to_decorate.__module__}.{function_to_decorate.__name__}' doesn't have an event as arg 0"
                phrase_properties.update(tree_info["Variables"][arg0_variable_name])
                if missing_properties(properties_to_use, phrase_properties):
                    pipeline_logger.debug(f"{function_to_decorate.__name__} --> Form Not Understood: {str(phrase_properties)} is not in {str(properties_to_use)}")
                    args[system_added_context_arg + extra_arg_in_front_count].report_error(["formNotUnderstood", function_to_decorate.__name__])
                    return

            # Any verb that has set properties must mark itself as "handles negation"
            # Same is true for any type of solution group
            if properties_to_use or is_solution_group:
                # Predications have to be written with negation in mind, so don't call it if it wasn't considered
                if perplexity.tree.is_introduced_variable_scoped_by_negation(state, arg0_variable_name):
                    if not handles_negation:
                        pipeline_logger.debug(f"{function_to_decorate.__name__} --> can't be called because it doesn't support negation")
                        args[system_added_context_arg + extra_arg_in_front_count].report_error(["formNotUnderstood", function_to_decorate.__name__])
                        return

            # Ensure that this solution group is designed for this interpretation
            # by comparing the interpretation used for the index_predication and the one
            # this solution group said it can handle
            if is_solution_group:
                if handles_interpretations is not None:
                    solution_interpretation = state.get_binding("interpretation").value[0]
                    index_predication = perplexity.tree.find_index_predication(tree_info)
                    solution_index_interpretation = solution_interpretation[index_predication.index]
                    found = False
                    for handles_item in handles_interpretations:
                        if handles_item.__module__ == solution_index_interpretation.module and handles_item.__name__ == solution_index_interpretation.function:
                            found = True
                            break

                    if not found:
                        pipeline_logger.debug(f"{function_to_decorate.__name__} --> solution group handler won't work for this solution")
                        args[system_added_context_arg + extra_arg_in_front_count].report_error(["formNotUnderstood", function_to_decorate.__name__])
                        return

            # Make sure the event has a structure that will be properly
            # handled by the predication
            if is_solution_group or ensure_handles_event(args[system_added_context_arg + extra_arg_in_front_count], args[system_added_state_arg + extra_arg_in_front_count], handles, args[system_added_arg_count + extra_arg_in_front_count]):
                yield from function_to_decorate(*args, **kwargs)

        # Make sure match_all args are filled in properly
        is_match_all = any((name.startswith("match_all_") or name.startswith("solution_group_match_all_")) for name in predication_names)
        extra_arg_in_front_count = 1 if is_match_all else 0
        valid_match_all = is_match_all and len(predication_names) == 1 and matches_lemma_function is not None
        assert not is_match_all or (is_match_all and valid_match_all)

        is_solution_group = any(name.startswith("solution_group") for name in predication_names)

        metadata = PredicationMetadata(function_to_decorate.__module__,
                                       function_to_decorate.__name__,
                                       library,
                                       argument_metadata(function_to_decorate, arguments),
                                       is_match_all,
                                       matches_lemma_function)
        final_arg_types = metadata.arg_types()
        final_phrase_types = phrase_types if phrase_types is not None else phrase_types_from_function(function_to_decorate)

        vocabulary.add_predication(metadata, function_to_decorate.__module__, function_to_decorate.__name__, predication_names, final_arg_types, final_phrase_types)

        return wrapper_function

    return PredicationDecorator


class PredicationMetadata(object):
    def __init__(self, module, function, library, args_metadata, match_all, matches_lemmas):
        self.module = module
        self.function = function
        self.args_metadata = args_metadata
        self._match_all = match_all
        self.matches_lemmas = matches_lemmas
        self.library = library

    def arg_types(self):
        return [arg_metadata["VariableType"] for arg_metadata in self.args_metadata]

    def is_match_all(self):
        return self._match_all


class VocabularyEntry(NamedTuple):
    module: str
    function: str
    extra_arg: list
    id: int


# The structure of self.all is:
#   {"erase_v_1__exx__comm": [(module, function), ...],
#    "erase_v_1__exx__ques": [(module, function), ...],
#    "delete_v_1__exx__comm": [(module, function), ...],
#    ... }
class Vocabulary(object):
    def __init__(self):
        self.all = dict()
        self.words = dict()
        # index each DELPH-IN predication by name
        # then have a list of Metadata objects for each implementation of it
        self._metadata = dict()
        self.transformers = []
        # Words that should not prevent trees from being built due to being unknown
        # because a transformer removes them
        self.transformer_removed = set()
        self.transformer_removed_wildcard = []
        # Give each module_function a unique number to identify it
        # which is len(type_list)
        self.next_implementation_id = 0
        self.synonyms = dict()

    def metadata(self, delphin_name, arg_types):
        metadata_list = []
        name_key = self.name_key(delphin_name, arg_types, "")
        if name_key in self._metadata:
            metadata_list += self._metadata[name_key]
        _, generic_key = self.generic_key(delphin_name, arg_types, "")
        if generic_key in self._metadata:
            metadata_list += self._metadata[generic_key]
        return metadata_list

    def name_key(self, delphin_name, arg_types, phrase_type):
        return f"{delphin_name}__{''.join(arg_types)}__{phrase_type}"

    def generic_key(self, delphin_name, arg_types, phrase_type):
        if delphin_name.startswith("solution_group__"):
            return None, None
        predication_info = parse_predication_name(delphin_name)
        return predication_info["Lemma"], f"match_all_{predication_info['Pos']}__{''.join(arg_types)}__{phrase_type}"

    def version_exists(self, delphin_name):
        name_parts = parse_predication_name(delphin_name)
        return name_parts["Lemma"] in self.words

    def add_transform(self, transformer_root):
        for removed in transformer_root.removed_predications():
            if isinstance(removed, TransformerMatch):
                self.transformer_removed_wildcard.append(removed)
            else:
                self.transformer_removed.add(removed)
        self.transformers.append(transformer_root)

    def is_potentially_removed(self, predication):
        if predication.name in self.transformer_removed:
            return True
        else:
            for match in self.transformer_removed_wildcard:
                if match.match(predication, set(), {}):
                    return True
            return False

    def override_predications(self, library, name_list):
        for name in name_list:
            self._metadata.pop(name, None)
            keys_to_remove = []
            for key in self.all:
                if key.startswith(name):
                    keys_to_remove.append(key)

            for key in keys_to_remove:
                self.all.pop(key, None)

    def add_predication(self, predication_metadata, module, function, delphin_names, arg_types, phrase_types, first=False):
        if len(phrase_types) == 0:
            phrase_types = ["comm", "ques", "prop", "prop-or-ques", "norm"]

        for delphin_name in delphin_names:
            metadata_key = self.name_key(delphin_name, arg_types, "")
            if metadata_key not in self._metadata:
                self._metadata[metadata_key] = []
            elif self._metadata[metadata_key][0].library != predication_metadata.library:
                assert False, f"Predication {metadata_key} already exists from library {self._metadata[metadata_key][0].library}. Use override('{predication_metadata.library}', ['{metadata_key}']) to hide it."
            self._metadata[metadata_key].append(predication_metadata)

            name_parts = parse_predication_name(delphin_name)
            self.words[name_parts["Lemma"]] = delphin_name

            for phrase_type in phrase_types:
                name_key = self.name_key(delphin_name, arg_types, phrase_type)
                if name_key not in self.all:
                    type_list = []
                    self.all[name_key] = type_list
                else:
                    type_list = self.all[name_key]

                if first:
                    type_list.insert(0, VocabularyEntry(module=module, function=function, id=self.next_implementation_id, extra_arg=None))
                else:
                    type_list.append(VocabularyEntry(module=module, function=function, id=self.next_implementation_id, extra_arg=None))
                self.next_implementation_id += 1

    # Perform any tree transforms that match AND only evaluate one of N conjuncts if the phrase
    # is a conjunction
    def alternate_trees(self, state, tree_info, yield_original, conjunct_index_list=None):
        for transformer_root in self.transformers:
            new_tree_info = build_transformed_tree(self, state, tree_info, transformer_root)
            if new_tree_info:
                # Run the rules from the start on this new tree
                found_next_tree = False
                for next_tree in self.alternate_trees(state, new_tree_info, False):
                    found_next_tree = True
                    yield self.select_tree_conjunct(next_tree, conjunct_index_list=conjunct_index_list)
                if not found_next_tree:
                    yield self.select_tree_conjunct(new_tree_info, conjunct_index_list=conjunct_index_list)

        if yield_original:
            yield self.select_tree_conjunct(tree_info, conjunct_index_list=conjunct_index_list)

    # Remove any conjunction terms like implicit_conj() as well as all but one of the verbs it points to
    # Which one is kept is indicated by conjunct_index_list
    def select_tree_conjunct(self, tree_info, conjunct_index_list=None):
        # Remove all the actual conjunctions
        conjunctions = perplexity.tree.find_predications(tree_info["Tree"], ["implicit_conj"])

        # Remove the ones that aren't joining two clauses
        conjunctions = [x for x in conjunctions if x.argument_types()[x.introduced_variable_index()] == "e"]
        if len(conjunctions) == 0:
            return tree_info

        remove_introduced_variables = [item.introduced_variable() for item in conjunctions]

        # Then remove all but one of their conjuncts too
        if conjunct_index_list is None:
            conjunct_index_list = [0] * len(conjunctions)
        assert (len(conjunct_index_list) == len(conjunctions))
        for index in range(len(conjunctions)):
            # Remove the non-introduced argument that wasn't chosen
            removed_conjunct_arg = 1 if conjunct_index_list[index] == 1 else 2
            remove_introduced_variables.append(conjunctions[index].args[removed_conjunct_arg])

        # Remove the implicit_conj and the conjuncts that weren't selected in conjunct_index_list
        # We assume all of those predications are in a conjunction (i.e. a list) so we just have to remove those items
        def rewrite_conjunctions(predication, index_by_ref):
            if isinstance(predication, list):
                new_conjunction = []
                for item in predication:
                    if item.introduced_variable() not in remove_introduced_variables:
                        new_conjunction.append(item)
                return new_conjunction

        index_by_ref = [0]
        new_tree = perplexity.tree.rewrite_tree_predications2(tree_info["Tree"], rewrite_conjunctions, index_by_ref)

        # Switch the index to be the chosen conjunct
        new_tree_info = copy.deepcopy(tree_info)
        new_tree_info["Tree"] = new_tree
        new_tree_info["SelectedConjuncts"] = conjunct_index_list
        if "Index" in new_tree_info and new_tree_info["Index"] in remove_introduced_variables:
            # The index was removed, revector it to whichever verb remains
            new_tree_info["Index"] = conjunctions[0].args[conjunct_index_list[0] + 1]

        pipeline_logger.debug(f"Tree Conjunct Option: {new_tree_info['Tree']}")
        return new_tree_info

    def predications(self, name, arg_types, predication_type):
        name_key = self.name_key(name, arg_types, predication_type)
        if name_key in self.all:
            for module_function in self.all[name_key]:
                yield module_function

        lemma, generic_key = self.generic_key(name, arg_types, predication_type)
        if generic_key in self.all:
            for module_function in self.all[generic_key]:
                yield VocabularyEntry(module=module_function.module, function=module_function.function, extra_arg=[lemma], id=module_function.id)

    def unknown_word(self, state, predicate_name, argument_types, phrase_type):
        predications = list(self.predications(predicate_name, argument_types, phrase_type))
        all_metadata = [meta for meta in
                        self.metadata(predicate_name, argument_types)]

        # It is unknown if we didn't find the word OR
        #
        all_are_match_all = all(meta.is_match_all() for meta in all_metadata)
        unmatched_match_all = all_are_match_all and not self._in_match_all(state, predicate_name, argument_types, all_metadata)
        if len(predications) == 0 or unmatched_match_all:
            return True

        else:
            return False

    def _in_match_all(self, state, predication_name, argument_types, metadata_list):
        for metadata in metadata_list:
            if metadata.is_match_all():
                predication_info = parse_predication_name(predication_name)
                if metadata.matches_lemmas(state, predication_info["Lemma"]):
                    return True

        else:
            return False


pipeline_logger = logging.getLogger('Pipeline')
