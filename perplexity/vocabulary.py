import enum
import inspect
import logging
import perplexity.execution
from perplexity.transformer import build_transformed_tree
from perplexity.utilities import parse_predication_name
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

def Predication(vocabulary, library=None, names=None, arguments=None, phrase_types=None, handles=None, virtual_args=None, matches_lemma_function=None):
    # Work around Python's odd handling of default arguments that are objects
    if handles is None:
        handles = []
    if virtual_args is None:
        virtual_args = []
    if library is None:
        library = "user"

    # handles = [(Name, EventOption), ...]
    # returns True or False, if False sets an error using report_error
    def ensure_handles_event(state, handles, event_binding):
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
                        perplexity.execution.report_error(["formNotUnderstood", "notHandled", item], force=True)
                        return False

            # Look at everything it handles and make sure the required things are there
            for item in handles:
                if item[1] == EventOption.required and (event_binding.value is None or item[0] not in event_binding.value):
                    perplexity.execution.report_error(["formNotUnderstood", "missing", item], force=True)
                    return False

        return True

    def arg_types_from_function(function):
        arg_spec = inspect.getfullargspec(function)

        # Skip the first arg since it should always be "state"
        arg_list = []
        for arg_index in range(1, len(arg_spec.args)):
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
        # wrapper_function() actually wraps the predication function
        # and is the real function called at runtime
        def wrapper_function(*args, **kwargs):
            # First make sure the function provided is a generator
            if not inspect.isgenerator(function_to_decorate) and not inspect.isgeneratorfunction(function_to_decorate):
                assert False, f"function {function_to_decorate.__name__} must be a generator"

            # First create any virtual args. This could fail and report an error
            if function_to_decorate.__name__ == "fpp_solution_group":
                print(1)
            if virtual_args is not None and len(virtual_args) > 0:
                new_args = create_virtual_arguments(args, virtual_args)
                if new_args is None:
                    # One of the args could not be created
                    # Assume it reported an error
                    return

                args = args + new_args

            # Make sure the event has a structure that will be properly
            # handled by the predication
            if is_solution_group or ensure_handles_event(args[0], handles, args[1]):
                yield from function_to_decorate(*args, **kwargs)

        predication_names = names if names is not None else [function_to_decorate.__name__]

        # Make sure match_all args are filled in right
        is_match_all = any(name.startswith("match_all_") for name in predication_names)
        valid_match_all = is_match_all and len(predication_names) == 1 and matches_lemma_function is not None
        assert not is_match_all or (is_match_all and valid_match_all)

        is_solution_group = any(name.startswith("solution_group") for name in predication_names)

        metadata = PredicationMetadata(library, argument_metadata(function_to_decorate, arguments), is_match_all, matches_lemma_function)
        final_arg_types = metadata.arg_types()
        final_phrase_types = phrase_types if phrase_types is not None else phrase_types_from_function(function_to_decorate)

        vocabulary.add_predication(metadata, function_to_decorate.__module__, function_to_decorate.__name__, predication_names, final_arg_types, final_phrase_types)

        return wrapper_function

    return PredicationDecorator


class PredicationMetadata(object):
    def __init__(self, library, args_metadata, match_all, matches_lemmas):
        self.args_metadata = args_metadata
        self._match_all = match_all
        self.matches_lemmas = matches_lemmas
        self.library = library

    def arg_types(self):
        return [arg_metadata["VariableType"] for arg_metadata in self.args_metadata]

    def is_match_all(self):
        return self._match_all


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
        predication_info = parse_predication_name(delphin_name)
        return predication_info["Lemma"], f"match_all_{predication_info['Pos']}__{''.join(arg_types)}__{phrase_type}"

    def version_exists(self, delphin_name):
        name_parts = parse_predication_name(delphin_name)
        return name_parts["Lemma"] in self.words

    def add_transform(self, transformer_root):
        for removed in transformer_root.removed_predications():
            self.transformer_removed.add(removed)
        self.transformers.append(transformer_root)

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
                    type_list.insert(0, (module, function))
                else:
                    type_list.append((module, function))

    def alternate_trees(self, state, tree_info, yield_original):
        for transformer_root in self.transformers:
            new_tree_info = build_transformed_tree(self, state, tree_info, transformer_root)
            if new_tree_info:
                yield new_tree_info

        if yield_original:
            yield tree_info

    def predications(self, name, arg_types, predication_type):
        name_key = self.name_key(name, arg_types, predication_type)
        if name_key in self.all:
            for module_function in self.all[name_key]:
                yield module_function + (None, )

        lemma, generic_key = self.generic_key(name, arg_types, predication_type)
        if generic_key in self.all:
            for module_function in self.all[generic_key]:
                yield module_function + ([lemma], )

    def unknown_word(self, state, predicate_name, argument_types, phrase_type):
        predications = list(self.predications(predicate_name, argument_types, phrase_type))
        all_metadata = [meta for meta in
                        self.metadata(predicate_name, argument_types)]
        if len(predications) == 0 or \
                (all(meta.is_match_all() for meta in all_metadata) and not self._in_match_all(state, predicate_name,
                                                                                             argument_types,
                                                                                             all_metadata)):
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
