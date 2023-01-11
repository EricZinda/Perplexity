import enum
import inspect
import logging

from perplexity.execution import report_error
from perplexity.utilities import parse_predication_name


class EventOption(enum.Enum):
    optional = 1
    required = 2


def Predication(vocabulary, names=None, arguments=None, phrase_types=None, handles=[]):
    # handles = [(Name, EventOption), ...]
    # returns True or False, if False sets an error using report_error
    def ensure_handles_event(state, handles, event):
        if event[0] == "e":
            eventState = state.get_variable(event)
            # Look at everything in event and make sure it is handled
            if eventState is not None:
                foundItem = False
                for item in eventState.items():
                    for handledItem in handles:
                        if item[0] == handledItem[0]:
                            foundItem = True
                            break

                    if not foundItem:
                        report_error(["formNotUnderstood", "notHandled", item])
                        return False

            # Look at everything it handles and make sure the required things are there
            for item in handles:
                if item[1] == EventOption.required and (eventState is None or item[0] not in eventState):
                    report_error(["formNotUnderstood", "missing", item])
                    return False

        return True

    def arguments_from_function(function):
        arg_spec = inspect.getfullargspec(function)

        # Skip the first arg since it should always be "state"
        arg_list = []
        for arg_index in range(1, len(arg_spec.args)):
            arg_name = arg_spec.args[arg_index]

            # Allow single character arguments like "x" and "e"
            # OR the format: "x_actor"
            if len(arg_name) == 1 or (len(arg_name) > 1 and arg_name[1] == "_"):
                arg_type = arg_name[0]
                if arg_type not in ["u", "i", "p", "e", "x", "h"]:
                    raise Exception(f"Argument {arg_index} of predication {function.__name__} has an unknown argument type of {arg_type}'")

                arg_list.append(arg_type)

        return arg_list

    def phrase_types_from_function(function):
        segments = function.__name__.split("_")
        index_types = []
        for index_type in segments:
            if index_type in ["prop", "ques", "comm"]:
                index_types.append(index_type)

        return index_types

    # Gets called when the function is first created
    # function_to_decorate is the function definition
    def PredicationDecorator(function_to_decorate):
        # wrapper_function() actually wraps the predication function
        # and is the real function called at runtime
        def wrapper_function(*args, **kwargs):
            # Make sure the event has a structure that will be properly
            # handled by the predication
            if ensure_handles_event(args[0], handles, args[1]):
                yield from function_to_decorate(*args, **kwargs)

        predication_names = names if names is not None else [function_to_decorate.__name__]
        final_arguments = arguments if arguments is not None else arguments_from_function(function_to_decorate)
        final_phrase_types = phrase_types if phrase_types is not None else phrase_types_from_function(function_to_decorate)
        vocabulary.add_predication(function_to_decorate.__module__, function_to_decorate.__name__, predication_names, final_arguments, final_phrase_types)

        return wrapper_function

    return PredicationDecorator


# The structure of self.all is:
#   {"erase_v_1__exx__comm": [(module, function), ...],
#    "erase_v_1__exx__ques": [(module, function), ...],
#    "delete_v_1__exx__comm": [(module, function), ...],
#    ... }
class Vocabulary(object):
    def __init__(self):
        self.all = dict()
        self.words = dict()

    def name_key(self, delphin_name, arg_types, phrase_type):
        return f"{delphin_name}__{''.join(arg_types)}__{phrase_type}"

    def version_exists(self, delphin_name):
        name_parts = parse_predication_name(delphin_name)
        return name_parts["Lemma"] in self.words

    def add_predication(self, module, function, delphin_names, arguments, phrase_types, first=False):
        if len(phrase_types) == 0:
            phrase_types = ["comm", "ques", "prop"]

        for delphin_name in delphin_names:
            name_parts = parse_predication_name(delphin_name)
            self.words[name_parts["Lemma"]] = delphin_name

            for phrase_type in phrase_types:
                name_key = self.name_key(delphin_name, arguments, phrase_type)
                if name_key not in self.all:
                    type_list = []
                    self.all[name_key] = type_list
                else:
                    type_list = self.all[name_key]

                if first:
                    type_list.insert(0, (module, function))
                else:
                    type_list.append((module, function))

    def predications(self, name, args, predication_type):
        name_key = self.name_key(name, args, predication_type)
        if name_key in self.all:
            for functionName in self.all[name_key]:
                yield functionName


pipeline_logger = logging.getLogger('Pipeline')
