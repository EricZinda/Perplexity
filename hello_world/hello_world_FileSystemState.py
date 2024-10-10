import file_system_example.objects
from file_system_example.objects import File, Folder, Actor, FileSystemMock
from file_system_example.state import DeleteOperation, FileSystemState, ChangeDirectoryOperation
from perplexity.predications import combinatorial_predication_1, lift_style_predication_2, \
    individual_style_predication_1, in_style_predication_2, Concept
from perplexity.response import RespondOperation
from perplexity.sstring import s
from perplexity.system_vocabulary import system_vocabulary
from perplexity.user_interface import UserInterface
from perplexity.utilities import ShowLogging
from perplexity.vocabulary import Predication, ValueSize, EventOption
import perplexity.messages
from perplexity.world_registry import register_world


vocabulary = system_vocabulary()


@Predication(vocabulary,
             names=["_lift_v_cause"],
             arguments=[("e",), ("x", ValueSize.all), ("x", ValueSize.all)])
def lift(context, state, e_introduced_binding, x_actor_binding, x_item_binding):
    def check_items_lifting_items(item1, item2):
        if item1 == ("Elsa", "Seo-Yun") and len(item2) == 1 and item2[0] == "table1":
            return True
        else:
            context.report_error(["xIsNotYZ", x_actor_binding.variable.name, "lifting", x_item_binding.variable.name])

    def all_item1s_lifting_item2s(item2):
        if len(item2) == 1 and item2[0] == "table1":
            yield ("Elsa", "Seo-Yun")

    def all_item2s_being_lifted_by_item1s(item1):
        if item1 == ("Elsa", "Seo-Yun"):
            yield ("table1",)

    yield from lift_style_predication_2(context,
                                        state,
                                        x_actor_binding,
                                        x_item_binding,
                                        check_items_lifting_items,
                                        all_item1s_lifting_item2s,
                                        all_item2s_being_lifted_by_item1s)


@Predication(vocabulary, names=["_student_n_of"])
def student_n_of(context, state, x_binding, i_binding):
    def bound_variable(value):
        if value in ["Elsa", "Seo-Yun"]:
            return True
        else:
            context.report_error(["notAThing", x_binding.value, x_binding.variable.name])
            return False

    def unbound_variable():
        yield "Elsa"
        yield "Seo-Yun"

    yield from combinatorial_predication_1(context,
                                           state,
                                           x_binding,
                                           bound_variable,
                                           unbound_variable)


@Predication(vocabulary, names=["_table_n_1"])
def table_n_1(context, state, x_binding):
    def bound_variable(value):
        if value in ["table1"]:
            return True
        else:
            context.report_error(["notAThing", x_binding.value, x_binding.variable.name])
            return False

    def unbound_variable():
        yield "table1"

    yield from combinatorial_predication_1(context,
                                           state,
                                           x_binding,
                                           bound_variable,
                                           unbound_variable)


# This is a helper function that any predication that can
# be "very'd" can use to understand just how "very'd" it is
def degree_multiplier_from_event(context, state, e_introduced_binding):
    # if a "very" is modifying this event, use that value
    # otherwise, return 1
    if e_introduced_binding.value is None or \
            "DegreeMultiplier" not in e_introduced_binding.value:
        degree_multiplier = 1

    else:
        degree_multiplier = e_introduced_binding.value["DegreeMultiplier"]["Value"]

    return degree_multiplier


@Predication(vocabulary, names=["_very_x_deg"])
def very_x_deg(context, state, e_introduced_binding, e_target_binding):
    # We'll interpret every "very" as meaning "one order of magnitude larger"
    yield state.add_to_e(e_target_binding.variable.name,
                         "DegreeMultiplier",
                         {"Value": 10,
                          "Originator": context.current_predication_index()})


@Predication(vocabulary, names=["_file_n_of"])
def file_n_of(context, state, x_binding, i_binding):
    def bound_variable(value):
        if isinstance(value, File):
            return True
        else:
            context.report_error(["valueIsNotX", value, x_binding.variable.name])
            return False

    def unbound_variable():
        for item in state.all_individuals():
            if bound_variable(item):
                yield item

    yield from combinatorial_predication_1(context,
                                           state,
                                           x_binding,
                                           bound_variable,
                                           unbound_variable)


# true for both sets and individuals as long as everything
# in the set is a file
@Predication(vocabulary, names=["_folder_n_of"])
def folder_n_of(context, state, x_binding, i_binding):
    def bound_variable(value):
        if isinstance(value, Folder):
            return True
        else:
            context.report_error(["valueIsNotX", value, x_binding.variable.name])
            return False

    def unbound_variable():
        for item in state.all_individuals():
            if bound_variable(item):
                yield item

    yield from combinatorial_predication_1(context,
                                           state,
                                           x_binding,
                                           bound_variable,
                                           unbound_variable)


@Predication(vocabulary,
             names=["_large_a_1"],
             handles=[("DegreeMultiplier", EventOption.optional)])
def large_a_1(context, state, e_introduced_binding, x_target_binding):
    # See if any modifiers have changed *how* large we should be
    degree_multiplier = degree_multiplier_from_event(context, state, e_introduced_binding)

    # "large" is being used "predicatively" as in "the dogs are large". This needs to force
    # the individuals to be separate (i.e. not part of a group)
    def criteria_bound(value):
        if hasattr(value, 'size') and value.size > degree_multiplier * 1000000:
            return True

        else:
            context.report_error(["adjectiveDoesntApply", "large", x_target_binding.variable.name])
            return False

    def unbound_values():
        # Find all large things
        for value in state.all_individuals():
            if hasattr(value, 'size') and value.size > degree_multiplier * 1000000:
                yield value

    yield from combinatorial_predication_1(context,
                                           state,
                                           x_target_binding,
                                           criteria_bound,
                                           unbound_values)


# Delete only works on individual values: i.e. there is no semantic for deleting
# things "together" which would probably imply a transaction or something
@Predication(vocabulary, names=["_delete_v_1"])
def delete_v_1_comm(context, state, e_introduced_binding, x_actor_binding, x_what_binding):
    # We only know how to delete things from the
    # computer's perspective
    if x_actor_binding.value[0].name == "Computer":
        def criteria(value):
            # Only allow deleting files and folders that exist
            if isinstance(value, (File, Folder)) and value.exists():
                return True

            else:
                context.report_error(["cantDo", "delete", x_what_binding.variable.name])

        def unbound_what():
            context.report_error(["cantDo", "delete", x_what_binding.variable.name])

        for new_state in individual_style_predication_1(context,
                                                        state,
                                                        x_what_binding,
                                                        criteria,
                                                        unbound_what,
                                                        ["cantDeleteSet", x_what_binding.variable.name]):
            yield new_state.apply_operations([DeleteOperation(new_state.get_binding(x_what_binding.variable.name))])

    else:
        context.report_error(["dontKnowActor", x_actor_binding.variable.name])


@Predication(vocabulary, names=["pron"])
def pron(context, state, x_who_binding):
    person = int(state.get_binding("tree").value[0]["Variables"][x_who_binding.variable.name]["PERS"])

    def bound_variable(value):
        return isinstance(value, Actor) and value.person == person

    def unbound_variable():
        for item in state.all_individuals():
            if bound_variable(item):
                yield item

    yield from combinatorial_predication_1(context, state, x_who_binding, bound_variable, unbound_variable)


@Predication(vocabulary)
def place_n(context, state, x_binding):
    def bound_variable(value):
        # Any object is a "place" as long as it can contain things
        if hasattr(value, "contained_items"):
            return True
        else:
            context.report_error(["valueIsNotX", value, x_binding.variable.name])
            return False

    def unbound_variable():
        for item in state.all_individuals():
            if bound_variable(item):
                yield item

    yield from combinatorial_predication_1(context,
                                           state,
                                           x_binding,
                                           bound_variable,
                                           unbound_variable)


@Predication(vocabulary, names=["loc_nonsp"])
def loc_nonsp(context, state, e_introduced_binding, x_actor_binding, x_location_binding):
    def item_at_item(item1, item2):
        if hasattr(item1, "all_locations"):
            # Asking if a location of item1 is at item2
            for location in item1.all_locations(x_actor_binding.variable):
                if location == item2:
                    return True

        context.report_error(["thingHasNoLocation", x_actor_binding.variable.name, x_location_binding.variable.name])
        return False

    def location_unbound_values(actor_value):
        # This is a "where is actor?" type query since no location specified (x_location_binding was unbound)
        # Order matters, so all_locations needs to return the best answer first
        if hasattr(actor_value, "all_locations"):
            for location in actor_value.all_locations(x_actor_binding.variable):
                yield location

        context.report_error(["thingHasNoLocation", x_actor_binding.variable.name, x_location_binding.variable.name])

    def actor_unbound_values(location_value):
        # This is a "what is at x?" type query since no actor specified (x_actor_binding was unbound)
        # Order matters, so all_locations needs to return the best answer first
        if hasattr(location_value, "contained_items"):
            for actor in location_value.contained_items(x_location_binding.variable):
                yield actor

        context.report_error(["thingIsNotContainer", x_location_binding.variable.name])

    yield from in_style_predication_2(context,
                                      state,
                                      x_actor_binding,
                                      x_location_binding,
                                      item_at_item,
                                      actor_unbound_values,
                                      location_unbound_values)


@Predication(vocabulary, names=["_go_v_1"], handles=[("DirectionalPreposition", EventOption.required)])
def go_v_1_comm(context, state, e_introduced_binding, x_actor_binding):
    if x_actor_binding.value is None or len(x_actor_binding.value) > 1 or x_actor_binding.value[0].name != "Computer":
        context.report_error(["dontKnowActor", x_actor_binding.variable.name])
        return

    x_location_binding = e_introduced_binding.value["DirectionalPreposition"]["Value"]["EndLocation"]

    def bound_location(location_item):
        # Only allow moving to folders
        if isinstance(location_item, Folder):
            return True

        else:
            if hasattr(x_location_binding.value, "exists") and location_item.exists():
                context.report_error(["cantDo", "change directory to", x_location_binding.variable.name])

            else:
                context.report_error(["notFound", x_location_binding.variable.name])

    def unbound_location(location_item):
        # Location is unbound, ask them to be more specific
        context.report_error(["beMoreSpecific"])

    # go_v_1 effectively has two arguments since it has x_actor by default and requires x_location from a preposition
    for new_state in individual_style_predication_1(context,
                                                    state,
                                                    x_location_binding,
                                                    bound_location,
                                                    unbound_location,
                                                    ["cantDo", "go", x_location_binding.variable.name]):
        yield new_state.apply_operations([ChangeDirectoryOperation(new_state.get_binding(x_location_binding.variable.name))])


@Predication(vocabulary, names=["_to_p_dir"])
def to_p_dir(context, state, e_introduced, e_target_binding, x_location_binding):
    preposition_info = {
        "EndLocation": x_location_binding
    }

    yield state.add_to_e(e_target_binding.variable.name,
                         "DirectionalPreposition",
                         {"Value": preposition_info,
                          "Originator": context.current_predication_index()})


@Predication(vocabulary, names=["_command_n_1"])
def _command_n_1_concept(context, state, x_binding):
    def bound_variable(value):
        if isinstance(value, Concept) and value == Concept("command"):
            return True
        else:
            context.report_error(["valueIsNotX", value, x_binding.variable.name])
            return False

    def unbound_variable():
        yield Concept("command")

    yield from combinatorial_predication_1(context,
                                           state,
                                           x_binding,
                                           bound_variable,
                                           unbound_variable)


@Predication(vocabulary, names=["_command_n_1"])
def _command_n_1(context, state, x_binding):
    def bound_variable(value):
        if isinstance(value, file_system_example.objects.FileCommand):
            return True
        else:
            context.report_error(["valueIsNotX", value, x_binding.variable.name])
            return False

    def unbound_variable():
        for item in state.all_individuals():
            if bound_variable(item):
                yield item

    yield from combinatorial_predication_1(context,
                                           state,
                                           x_binding,
                                           bound_variable,
                                           unbound_variable)


@Predication(vocabulary,
             names=["_have_v_1"],
             phrases={"What commands do you have?": {'SF': 'ques', 'TENSE': 'pres', 'MOOD': 'indicative', 'PROG': '-', 'PERF': '-'},
                      "You have commands.": {'SF': 'prop', 'TENSE': 'pres', 'MOOD': 'indicative', 'PROG': '-', 'PERF': '-'}
                      },
             properties={'SF': ['ques', 'prop'], 'TENSE': 'pres', 'MOOD': 'indicative', 'PROG': '-', 'PERF': '-'}
             )
def _have_v_1_concept(context, state, e_introduced_binding, x_actor_binding, x_target_binding):
    def actor_have_target(item1, item2):
        if isinstance(item2, Concept) and item2 == Concept("command"):
            return True
        else:
            context.report_error(["doNotHave", x_actor_binding.variable.name, x_target_binding.variable.name])
            return False

    def all_actors_having_target(item2):
        if False:
            yield None

    def all_targets_had_by_actor(item1):
        if False:
            yield None

    if x_actor_binding.value is not None and len(x_actor_binding.value) == 1 and x_actor_binding.value[0] == Actor(name="Computer", person=2):
        yield from in_style_predication_2(context,
                                          state,
                                          x_actor_binding,
                                          x_target_binding,
                                          actor_have_target,
                                          all_actors_having_target,
                                          all_targets_had_by_actor)

    else:
        context.report_error(["doNotHave", x_actor_binding.variable.name, x_target_binding.variable.name])
        return False


@Predication(vocabulary,
             names=["_have_v_1"],
             phrases={"What commands do you have?": {'SF': 'ques', 'TENSE': 'pres', 'MOOD': 'indicative', 'PROG': '-', 'PERF': '-'},
                      "You have commands.": {'SF': 'prop', 'TENSE': 'pres', 'MOOD': 'indicative', 'PROG': '-', 'PERF': '-'}
                      },
             properties={'SF': ['ques', 'prop'], 'TENSE': 'pres', 'MOOD': 'indicative', 'PROG': '-', 'PERF': '-'}
             )
def _have_v_1(context, state, e_introduced_binding, x_actor_binding, x_target_binding):
    def actor_have_target(item1, item2):
        if isinstance(item2, file_system_example.objects.FileCommand):
            return True
        else:
            context.report_error(["doNotHave", x_actor_binding.variable.name, x_target_binding.variable.name])
            return False

    def all_actors_having_target(item2):
        if False:
            yield None

    def all_targets_had_by_actor(item1):
        if False:
            yield None

    if x_actor_binding.value is not None and len(x_actor_binding.value) == 1 and x_actor_binding.value[0] == Actor(name="Computer", person=2):
        yield from in_style_predication_2(context,
                                          state,
                                          x_actor_binding,
                                          x_target_binding,
                                          actor_have_target,
                                          all_actors_having_target,
                                          all_targets_had_by_actor)

    else:
        context.report_error(["doNotHave", x_actor_binding.variable.name, x_target_binding.variable.name])
        return False


@Predication(vocabulary,
             names=["solution_group__have_v_1"],
             handles_interpretation=_have_v_1_concept)
def _have_v_1_group(context, state_list, e_introduced_binding_list, x_actor_variable_group, x_target_variable_group):
    yield [state_list[0].record_operations([RespondOperation("You can use the following commands: copy and go")])]


# Generates all the responses that predications can
# return when an error occurs
def generate_custom_message(state, tree_info, error_term):
    # See if the system can handle converting the error
    # to a message first
    system_message = perplexity.messages.generate_message(state, tree_info, error_term)
    if system_message is not None:
        return system_message

    else:
        # error_term is of the form: [index, error] where "error" is another
        # list like: ["name", arg1, arg2, ...]. The first item is the error
        # constant (i.e. its name). What the args mean depends on the error
        error_predicate_index = error_term[0]
        error_arguments = error_term[1]
        error_constant = error_arguments[0] if error_arguments is not None else "no error set"
        arg_length = len(error_arguments) if error_arguments is not None else 0
        arg1 = error_arguments[1] if arg_length > 1 else None
        arg2 = error_arguments[2] if arg_length > 2 else None
        arg3 = error_arguments[3] if arg_length > 3 else None
        arg4 = error_arguments[4] if arg_length > 4 else None

        if error_constant == "adjectiveDoesntApply":
            return s("{A arg2} {'is':<arg2} not {*arg1}", tree_info)

        elif error_constant == "doNotHave":
            # s() converts a variable name like 'x3' into the english words
            # that it represented in the MRS
            return s("{arg1} do not have {arg2}", tree_info, reverse_pronouns=True)

        elif error_constant == "notAThing":
            # s() converts a variable name like 'x3' into the english words
            # that it represented in the MRS
            return s("{*arg1} is not {arg2}", tree_info)

        elif error_constant == "xIsNotYZ":
            return s("{arg1} is not {*arg2} {arg3}", tree_info)

        elif error_constant == "dontKnowActor":
            return s("I don't know who '{arg1}' is", tree_info)

        elif error_constant == "cantXYTogether":
            return s("I can't {*arg1} {arg2} *together*", tree_info)

        elif error_constant == "thingHasNoLocation":
            return s("{arg1} is not in {arg2}", tree_info)

        elif error_constant == "thingIsNotContainer":
            return s("{arg1} can't contain things", tree_info)

        else:
            # No custom message, just return the raw error for debugging
            return str(error_term)


def reset():
    # return FileSystemState(FileSystemMock([(True, "/documents/file1.txt", {"size": 1000}),
    #                                        (False, "/Desktop", {"size": 10000000}),
    #                                        (True, "/Desktop/file2.txt", {"size": 10000000}),
    #                                        (True, "/Desktop/file3.txt", {"size": 1000})],
    #                                        "/Desktop"))
    return FileSystemState(FileSystemMock([(True, "/documents/file1.txt", {"size": 1000}),
                                           (False, "/Desktop", {"size": 10000000}),
                                           (True, "/Desktop/the yearly budget.txt", {"size": 10000000}),
                                           (True, "/Desktop/blue", {"size": 1000})],
                                          "/Desktop"))

# Creates the micro-world interface on startup
# or if the user loads the world later
def ui():
    ui = UserInterface(world_name="SimplestExample",
                       reset_function=reset,
                       vocabulary=vocabulary,
                       message_function=generate_custom_message)
    return ui


# Worlds need to be registered so the user can switch between them by name
# and so that the engine can search for their autocorrect and other cached files
# in the same directory where the ui() function resides
register_world(world_name="SimplestExample",
               module="hello_world_FileSystemState",
               ui_function="ui")


if __name__ == '__main__':
    # ShowLogging("Pipeline")
    # ShowLogging("ChatGPT")
    # ShowLogging("Testing")
    # ShowLogging("Execution")
    # ShowLogging("Generation")
    # ShowLogging("SString")
    # ShowLogging("UserInterface")
    # ShowLogging("Determiners")
    # ShowLogging("SolutionGroups")
    # ShowLogging("Transformer")

    user_interface = ui()
    while user_interface:
        # The loop might return a different user interface
        # object if the user changes worlds
        user_interface = user_interface.default_loop()
