import enum
import inspect
import logging
import perplexity.execution
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


def Predication(vocabulary, names=None, arguments=None, phrase_types=None, handles=[], virtual_args=[]):
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
                        perplexity.execution.report_error(["formNotUnderstood", "notHandled", item])
                        return False

            # Look at everything it handles and make sure the required things are there
            for item in handles:
                if item[1] == EventOption.required and (event_binding.value is None or item[0] not in event_binding.value):
                    perplexity.execution.report_error(["formNotUnderstood", "missing", item])
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
            if index_type in ["prop", "ques", "comm", "norm"]:
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
            # First create any virtual args. This could fail and report an error
            if virtual_args is not None and len(virtual_args) > 0:
                new_args = create_virtual_arguments(args, virtual_args)
                if new_args is None:
                    # One of the args could not be created
                    # Assume it reported an error
                    return

                args = args + new_args

            # Make sure the event has a structure that will be properly
            # handled by the predication
            if ensure_handles_event(args[0], handles, args[1]):
                yield from function_to_decorate(*args, **kwargs)

        metadata = PredicationMetadata(argument_metadata(function_to_decorate, arguments))
        predication_names = names if names is not None else [function_to_decorate.__name__]
        final_arg_types = metadata.arg_types()
        final_phrase_types = phrase_types if phrase_types is not None else phrase_types_from_function(function_to_decorate)
        vocabulary.add_predication(metadata, function_to_decorate.__module__, function_to_decorate.__name__, predication_names, final_arg_types, final_phrase_types)

        return wrapper_function

    return PredicationDecorator


class PredicationMetadata(object):
    def __init__(self, args_metadata):
        self.args_metadata = args_metadata

    def arg_types(self):
        return [arg_metadata["VariableType"] for arg_metadata in self.args_metadata]


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

    def metadata(self, delphin_name, arg_types):
        return self._metadata[self.name_key(delphin_name, arg_types, "")]

    def name_key(self, delphin_name, arg_types, phrase_type):
        return f"{delphin_name}__{''.join(arg_types)}__{phrase_type}"

    def version_exists(self, delphin_name):
        name_parts = parse_predication_name(delphin_name)
        return name_parts["Lemma"] in self.words

    def add_predication(self, predication_metadata, module, function, delphin_names, arg_types, phrase_types, first=False):
        if len(phrase_types) == 0:
            phrase_types = ["comm", "ques", "prop", "norm"]

        for delphin_name in delphin_names:
            metadata_key = self.name_key(delphin_name, arg_types, "")
            if metadata_key not in self._metadata:
                self._metadata[metadata_key] = []

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

    def predications(self, name, arg_types, predication_type):
        name_key = self.name_key(name, arg_types, predication_type)
        if name_key in self.all:
            for functionName in self.all[name_key]:
                yield functionName


pipeline_logger = logging.getLogger('Pipeline')
