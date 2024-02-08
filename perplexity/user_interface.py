import json
import logging
import os
import pickle
import sys

import perplexity.messages
from delphin.codecs import simplemrs
from perplexity.execution import MessageException, TreeSolver, ExecutionContext
from perplexity.print_tree import create_draw_tree, TreeRenderer
from perplexity.state import apply_solutions_to_state, LoadException
from perplexity.test_manager import TestManager, TestIterator, TestFolderIterator
from perplexity.tree import find_predications, find_predications_with_arg_types, \
    MrsParser, tree_contains_predication, TreePredication, get_wh_question_variable
from perplexity.user_state import GetStateDirectoryName
from perplexity.utilities import sentence_force, module_name, import_function_from_names
from perplexity.world_registry import world_information


def no_error_priority(error):
    if error is None:
        return 0
    else:
        return 1


def load_ui(path_and_filename):
    with open(path_and_filename, "rb") as file:
        metadata = pickle.load(file)
        world_info = world_information(metadata.get("WorldName", None))
        if world_info is None:
            raise LoadException
        else:
            ui_function = import_function_from_names(world_info["WorldModule"], world_info["WorldUIFunction"])
            return ui_function(metadata, file)


class UserInterface(object):
    def __init__(self, world_name, reset, vocabulary,
                 message_function=perplexity.messages.generate_message,
                 error_priority_function=no_error_priority,
                 response_function=perplexity.messages.respond_to_mrs_tree,
                 scope_init_function=None,
                 scope_function=None,
                 loaded_state=None):
        self.max_holes = 14

        self.world_name = world_name
        self.reset = None
        self.vocabulary = None
        self.scope_function = None
        self.scope_init_function = None
        self.response_function = None
        self.message_function = None
        self.error_priority_function = None
        self.state = None
        if loaded_state is None:
            loaded_state = reset()
        self.load_ui(loaded_state, reset, vocabulary, message_function, error_priority_function, response_function, scope_init_function, scope_function)

        self.interaction_record = None
        self.records = None
        self.test_manager = TestManager()
        self.user_input = None
        self.last_system_command = None
        self.run_mrs_index = None
        self.run_tree_index = None
        self.show_all_answers = False
        self.run_all_parses = False
        self.mrs_parser = MrsParser(self.max_holes)
        self.log_tests = False
        self.new_ui = None

    def load_ui(self, state, reset, vocabulary, message_function=perplexity.messages.generate_message, error_priority_function=no_error_priority, response_function=perplexity.messages.respond_to_mrs_tree, scope_init_function=None, scope_function=None):
        self.reset = reset
        self.vocabulary = vocabulary
        self.message_function = message_function
        self.error_priority_function = error_priority_function
        self.response_function = response_function
        self.scope_function = scope_function
        self.scope_init_function = scope_init_function

        self.state = state

    def save(self, path_and_filename):
        with open(path_and_filename, "wb") as file:
            pickle.dump({"WorldName": self.world_name, "Version": 1}, file, 5)
            self.state.save(file)

    def chosen_tree_record(self):
        chosen_mrs_index = self.interaction_record["ChosenMrsIndex"]
        chosen_tree_index = self.interaction_record["ChosenTreeIndex"]
        if chosen_mrs_index is None:
            return None
        else:
            return self.interaction_record["Mrss"][chosen_mrs_index]["Trees"][chosen_tree_index]

    def new_mrs_record(self, mrs=None, unknown_words=None):
        return {"Mrs": mrs,
                "UnknownWords": unknown_words,
                "Trees": []}

    def default_loop(self):
        command_line_commands = sys.argv[1:] if len(sys.argv) > 1 else []
        while True:
            command = command_line_commands.pop(0) if len(command_line_commands) > 0 else None
            if command == "exit":
                os._exit(0)
            else:
                self.interact_once(force_input=command)
                if self.new_ui:
                    # The user gave a command to load a new UI
                    return self.new_ui
            print()

    def interact_once(self, force_input=None):
        if force_input is None:
            # input() pauses the program and waits for the user to
            # type input and hit enter, and then returns it
            self.user_input = str(input("? "))
        else:
            self.user_input = force_input

        command_result = self.handle_command(self.user_input)
        if command_result is not None:
            self.test_manager.record_session_data("last_system_command", self.user_input)

        if command_result is True:
            return

        self.interaction_record = {"UserInput": self.user_input,
                                   "Mrss": [],
                                   "ChosenMrsIndex": None,
                                   "ChosenTreeIndex": None}

        if command_result is not None:
            self.test_manager.record_session_data("last_system_command", self.user_input)
            mrs_record = self.new_mrs_record()
            self.interaction_record["Mrss"].append(mrs_record)
            tree_record = TreeSolver.new_error_tree_record(response_generator=[command_result])
            mrs_record["Trees"].append(tree_record)
            self.interaction_record["ChosenMrsIndex"] = 0
            self.interaction_record["ChosenTreeIndex"] = 0
            print(command_result)

        else:
            self.test_manager.record_session_data("last_phrase", self.user_input)

        # self.records is a list if we are recording commands
        if isinstance(self.records, list):
            self.records.append(self.interaction_record)
            print(f"Recorded ({len(self.records)} items).")

        if command_result is not None:
            return

        # Do any corrections or fixup on the text
        self.user_input = self.autocorrect(self.user_input)
        self.interaction_record["UserInput"] = self.user_input

        # Loop through each MRS and each tree that can be
        # generated from it...
        mrs_index = -1
        for mrs in self.mrs_parser.mrss_from_phrase(self.user_input):
            mrs_index += 1
            if self.run_mrs_index is not None and self.run_mrs_index != mrs_index:
                continue

            unknown, contingent = self.unknown_words(mrs, self.state)
            mrs_record = self.new_mrs_record(mrs=mrs, unknown_words=unknown)
            self.interaction_record["Mrss"].append(mrs_record)

            if len(mrs_record["UnknownWords"]) > 0:
                unknown_words_error = ExecutionContext.blank_error(predication_index=0, error=["unknownWords", mrs_record["UnknownWords"]])
                tree_record = TreeSolver.new_error_tree_record(error=unknown_words_error,
                                                               response_generator=self.response_function(self.vocabulary, self.message_function, None, [], unknown_words_error),
                                                               tree_index=0 if len(mrs_record["Trees"]) == 0 else mrs_record["Trees"][-1]["TreeIndex"] + 1)
                mrs_record["Trees"].append(tree_record)
                self.evaluate_best_response(has_solution_group=False)

            else:
                # Loop through all the "official" DELPH-IN trees using the official predications
                tree_generated = False
                for tree_orig in self.mrs_parser.trees_from_mrs(mrs):
                    tree_generated = True
                    tree_info_orig = {"Index": mrs.index,
                                      "Variables": mrs.variables,
                                      "Tree": tree_orig,
                                      "MRS": self.mrs_parser.mrs_to_string(mrs)}

                    # Now loop through any tree modifications that have been built for this application
                    alternate_tree_generated = False
                    for tree_info in self.vocabulary.alternate_trees(self.state, tree_info_orig, len(contingent) == 0):
                        # At this point we have locked down which predications should be used and that won't change
                        # However: there might be multiple interpretations of these predications as well as disjunctions
                        # that cause various solution sets to be created. Each will be in its own tree_record
                        alternate_tree_generated = True
                        tree_index = 0 if len(mrs_record["Trees"]) == 0 else mrs_record["Trees"][-1]["TreeIndex"] + 1

                        # TODO: Figure out how to count this for tree index purposes properly
                        # Make sure the contingent words were removed by a transformer
                        if len(contingent) > 0:
                            if tree_contains_predication(tree_info["Tree"], [x[0] for x in contingent]):
                                # It is still there, fail this tree
                                tree_record = TreeSolver.new_tree_record(tree=tree_info["Tree"], tree_index=tree_index, error=f"One or more of these words not transformed out of tree: {[x[0] for x in contingent]}")
                                mrs_record["Trees"].append(tree_record)
                                continue

                        # Try the state from each frame that is available
                        # Used to loop through different frames, for now this is turned off
                        # until we decide if is necessary again since it is expensive
                        # was: for frame_state in self.state.frames():
                        wh_phrase_variable = perplexity.tree.get_wh_question_variable(tree_info)
                        for frame_state in [self.state]:
                            pipeline_logger.debug(f"Evaluating against frame '{frame_state.frame_name}'")

                            tree_solver = TreeSolver.create_top_level_solver(self.vocabulary, self.scope_function, self.scope_init_function)
                            for tree_record in tree_solver.tree_solutions(frame_state,
                                                                          tree_info,
                                                                          self.response_function,
                                                                          self.message_function,
                                                                          tree_index,
                                                                          self.run_tree_index,
                                                                          find_all_solution_groups=self.show_all_answers,
                                                                          wh_phrase_variable=wh_phrase_variable):
                                mrs_record["Trees"].append(tree_record)

                                solution_group_generator = tree_record["SolutionGroupGenerator"]
                                if solution_group_generator is not None:
                                    # There were solutions, so this is our answer.
                                    # Return it and stop looking
                                    self.evaluate_best_response(has_solution_group=True)

                                    # Go through all the responses in this solution group
                                    had_operations = False
                                    response, solution_group = next(tree_record["ResponseGenerator"])
                                    # Because this worked, we need to apply any Operations that were added to
                                    # any solution to the current world state.
                                    try:
                                        has_more_func = solution_group_generator.has_at_least_one_more
                                        operation_responses, new_state = apply_solutions_to_state(self.state, has_more_func, [solution for solution in solution_group])
                                        self.state = new_state

                                    except MessageException as error:
                                        response = self.response_function(self.vocabulary, self.message_function, tree_info, [], [0, error.message_object()])
                                        tree_record["ResponseMessage"] += f"\n{str(response)}"
                                        operation_responses = []

                                    if len(operation_responses) > 0:
                                        had_operations = True
                                        operation_responses.sort(key=lambda tup: tup[0])
                                        response = "\n".join(item[1] for item in operation_responses)

                                    elif response is None:
                                        this_sentence_force = sentence_force(tree_info["Variables"])
                                        if this_sentence_force == "comm":
                                            # Only give a "Done!" message if it was a command and there were no responses given
                                            response = "Done!"

                                        elif this_sentence_force == "prop" or this_sentence_force == "prop-or-ques":
                                            response = "Yes, that is true."

                                        else:
                                            response = "(no response)"

                                    tree_record["ResponseMessage"] += response
                                    print(response)

                                    # Only show if the developer didn't provide a custom message
                                    if not had_operations:
                                        more_message = self.generate_more_message(tree_info, solution_group_generator)
                                        if more_message is not None:
                                            tree_record["ResponseMessage"] += more_message
                                            print(more_message)

                                    if not self.run_all_parses:
                                        return

                                else:
                                    # This failed, remember it if it is the "best" failure
                                    # which we currently define as the first one
                                    self.evaluate_best_response(has_solution_group=False)

                    if len(contingent) > 0 and not alternate_tree_generated:
                        unknown_words_error = ExecutionContext.blank_error(predication_index=0, error=["unknownWords", contingent])
                        tree_record = TreeSolver.new_error_tree_record(error=unknown_words_error,
                                                                       response_generator=self.response_function(self.vocabulary, self.message_function, None, [], unknown_words_error),
                                                                       tree_index=0 if len(mrs_record["Trees"]) == 0 else mrs_record["Trees"][-1]["TreeIndex"] + 1)
                        mrs_record["Trees"].append(tree_record)
                        self.evaluate_best_response(has_solution_group=False)

        # If we got here, nothing worked: print out the best failure
        chosen_record = self.chosen_tree_record()
        if chosen_record is None:
            print("Sorry, did you mean to say something?")

        else:
            response, _ = next(chosen_record["ResponseGenerator"])
            if response is None:
                response = "(no error specified)"
            chosen_record["ResponseMessage"] += response
            print(response)

    def generate_more_message(self, tree, solution_groups):
        if solution_groups is None:
            return

        else:
            try:
                if next(solution_groups):
                    return "(there are more)"

            except StopIteration:
                pass

    # WORKAROUND: ERG doesn't properly quote all strings with "/" so convert to "\"
    def convert_slashes_until(self, stop_char, start_index, phrase):
        new_phrase = ""
        index = start_index
        while index < len(phrase):
            test_char = phrase[index]
            index += 1

            if test_char == "/":
                new_phrase += "\\>"
            elif test_char == stop_char:
                break
            else:
                new_phrase += test_char

        if new_phrase.strip() == "\\>":
            new_phrase = "\\>root111"

        return index, new_phrase + stop_char

    def autocorrect(self, phrase):
        final_phrase = ""
        index = 0
        while index < len(phrase):
            final_phrase += phrase[index]
            if phrase[index] in ["'", "\""]:
                index, new_phrase = self.convert_slashes_until(phrase[index], index + 1, phrase)
                final_phrase += new_phrase
            else:
                index += 1

        return final_phrase

    def evaluate_best_response(self, has_solution_group):
        current_mrs_index = len(self.interaction_record["Mrss"]) - 1
        current_tree_index = len(self.interaction_record["Mrss"][current_mrs_index]["Trees"]) - 1
        tree_record = self.interaction_record["Mrss"][current_mrs_index]["Trees"][current_tree_index]
        chosen_record = self.chosen_tree_record()
        chosen_error = chosen_record["Error"] if chosen_record is not None else None
        # If there was a success, return it as the best answer
        if has_solution_group or \
                (self.error_priority_function(tree_record["Error"]) > self.error_priority_function(chosen_error)):
            self.interaction_record["ChosenMrsIndex"] = current_mrs_index
            self.interaction_record["ChosenTreeIndex"] = current_tree_index
            pipeline_logger.debug(f"Recording best answer: MRSIndex {current_mrs_index}, TreeIndex: {current_tree_index}, Error: {tree_record['Error'] if not has_solution_group is None else 'none'}")

    # Commands always start with "/", followed by a string of characters and then
    # a space. Any arguments are after the space and their format is command specific.
    # For example:
    #   /show all
    # If it returns:
    # True: Command was handled and should not be recorded
    # None: Was not a command
    # Str: The string that should be recorded for the command
    def handle_command(self, text):
        try:
            text = text.strip()
            if len(text) > 0:
                if text[0] == "/":
                    text = text[1:]
                    items = text.split()
                    if len(items) > 0:
                        command = items[0].strip().lower()
                        command_info = command_data.get(command, None)
                        if command_info is not None:
                            return command_info["Function"](self, " ".join(text.split()[1:]))

                        else:
                            print("Don't know that command ...")
                            return True

        except Exception as error:
            print(str(error))
            return True

        return None

    def print_diagnostics(self, all, first_tree_only):
        if self.interaction_record is not None:
            print(f"User Input: {self.interaction_record['UserInput']}")
            print(f"{len(self.interaction_record['Mrss'])} Parses")

            for mrs_index in range(0, len(self.interaction_record["Mrss"])):
                if all or self.interaction_record["ChosenMrsIndex"] is None or mrs_index == self.interaction_record["ChosenMrsIndex"]:
                    extra = "CHOSEN " if mrs_index == self.interaction_record["ChosenMrsIndex"] else ""
                    print(f"\n***** {extra}Parse #{mrs_index}:")
                    mrs_record = self.interaction_record["Mrss"][mrs_index]
                    mrs = mrs_record['Mrs']
                    print(f"Sentence Force: {sentence_force(mrs.variables)}")
                    print(simplemrs.encode(mrs, indent=True))

                    if all:
                        chosen_tree = None
                    else:
                        chosen_tree = self.interaction_record["ChosenTreeIndex"]

                    self.print_diagnostics_trees(all, mrs_index, chosen_tree, mrs_record, first_tree_only)

    def print_diagnostics_trees(self, all, parse_number, chosen_tree, mrs_record, first_tree_only):
        # is_system_command_record = len(mrs_record["Trees"]) == 1 and mrs_record["Mrs"] is None and "ErrorTree" in mrs_record["Trees"][0]
        is_ungenerated_tree = len(mrs_record["Trees"]) == 1 and mrs_record["Mrs"] is not None and "ErrorTree" in mrs_record["Trees"][0]
        if is_ungenerated_tree:
            # The trees aren't generated if we don't know terms for performance
            # reasons (since we won't be evaluating anything)
            tree_generator = []
            for tree in self.mrs_parser.trees_from_mrs(mrs_record["Mrs"]):
                tree_generator.append(TreeSolver.new_tree_record(tree=tree, error=mrs_record["Trees"][0]["Error"], response_generator=mrs_record["Trees"][0]["ResponseGenerator"], response_message=mrs_record["Trees"][0]["ResponseMessage"]))

        else:
            tree_generator = mrs_record["Trees"]

        tree_index = 0
        for tree_info in tree_generator:
            if first_tree_only and tree_index > 0:
                return

            if all or chosen_tree == tree_index:
                extra = "CHOSEN " if chosen_tree == tree_index else ""
                print(f"\n-- {extra}Parse #{parse_number}, {extra}Tree #{tree_index}: \n")
                draw_tree = create_draw_tree(mrs_record["Mrs"], tree_info["Tree"])
                renderer = TreeRenderer()
                renderer.print_tree(draw_tree)
                print(f"\nText Tree: {tree_info['Tree']}")
                print(f"\nInterpretation: {tree_info['Interpretation']}")
                if tree_info['SolutionGroups'] is not None:
                    for solution_group in tree_info['SolutionGroups']:
                        print(f"\nSolution group:")
                        for solution in solution_group:
                            print(f"{str(solution)}")
                    print()

                else:
                    print(f"Error: {tree_info['Error']}")

                if tree_info['ResponseMessage'] == "" and tree_info['ResponseGenerator'] is not None:
                    tree_info['ResponseMessage'] = ""
                    for response in tree_info['ResponseGenerator']:
                        tree_info['ResponseMessage'] += str(response)
                print(f"Response:\n{tree_info['ResponseMessage']}")

            tree_index += 1

    def unknown_words(self, mrs, state):
        unknown_words = []
        contingent_words = []
        phrase_type = sentence_force(mrs.variables)
        for predication in mrs.predications:
            argument_types = []
            for argument_item in predication.args.items():
                if argument_item[0] == "CARG":
                    argument_types.append("c")
                else:
                    argument_types.append(argument_item[1][0])

            if self.vocabulary.unknown_word(state, predication.predicate, argument_types, phrase_type):
                # BUT: if a transformer might remove it, return it as "contingent" so we can see if it did
                tree_predication = TreePredication(0, predication.predicate, list(predication.args.values()), arg_names=list(predication.args.keys()), mrs_predication=predication)
                if self.vocabulary.is_potentially_removed(tree_predication):
                    contingent_words.append((predication.predicate,
                                          argument_types,
                                          phrase_type,
                                          # Record if at least one form is understood for
                                          # better error messages
                                          self.vocabulary.version_exists(predication.predicate)))

                else:
                    # If there aren't any implementations for this predication, or they are all match_all and don't implement it...
                    # This predication is not implemented
                    unknown_words.append((predication.predicate,
                                          argument_types,
                                          phrase_type,
                                          # Record if at least one form is understood for
                                          # better error messages
                                          self.vocabulary.version_exists(predication.predicate)))

        if len(unknown_words) > 0:
            pipeline_logger.debug(f"Unknown predications: {unknown_words}")

        return unknown_words, contingent_words


def command_run_all_parses(ui, arg):
    turn_on = bool(arg) if len(arg) > 0 else True
    print(f"Run all parses is now {turn_on}")
    ui.run_all_parses = turn_on
    return True


def command_show(ui, arg):
    parts = arg.split(",")
    all = False
    first_tree_only = False

    if len(parts) >= 1:
        all = parts[0].lower() == "all"

    if len(parts) >= 2:
        first_tree_only = bool(parts[1])

    if len(parts) >= 3:
        print("Don't know that argument set")
        return True

    ui.print_diagnostics(all, first_tree_only)
    return True


def command_repeat_system_command(ui, arg):
    if "last_system_command" in ui.test_manager.session_data:
        repeat_phrase = ui.test_manager.session_data["last_system_command"]
        ui.user_input = repeat_phrase
        print(f"Repeat: {repeat_phrase}")
        return ui.handle_command(repeat_phrase)

    else:
        print("No last command to repeat")

    return None


def command_repeat(ui, arg):
    repeat_phrase = ui.test_manager.session_data["last_phrase"]
    print(f"Repeat: {repeat_phrase}")
    ui.user_input = repeat_phrase
    return None


def command_record_test(ui, arg):
    turn_on = bool(arg) if len(arg) > 0 else True
    ui.records = [] if turn_on else None
    print(f"Recording is now {turn_on}")
    return True


def command_create_test(ui, arg):
    if len(arg) == 0:
        print(f"Please supply a test name.")

    else:
        ui.test_manager.create_test(ui, arg, ui.records)
        ui.records = None
        print(f"Recording is now off")

    return True


def command_append_test(ui, arg):
    if len(arg) == 0:
        print(f"Please supply a test name.")

    else:
        ui.test_manager.append_test(arg, ui.records)
        ui.records = None
        print(f"Recording is now off")

    return True


def command_run_test(ui, arg):
    if len(arg) == 0:
        print(f"Please supply a test name.")

    else:
        # Remember that we ran a single test not a folder
        ui.test_manager.record_session_data("LastTestFolder", "")
        test_iterator = TestIterator(ui.test_manager, ui.test_manager.full_test_path(arg + ".tst"))
        ui.test_manager.run_tests(test_iterator, ui)

    return True


def StringBooleanToBoolean(value):
    return value.lower() in ['true', '1', 't', 'y', 'yes']


def command_log_tests(ui, arg):
    if len(arg) == 0:
        value = not ui.log_tests
    else:
        value = StringBooleanToBoolean(arg)
    ui.log_tests = value
    print("Log Test Results is now {}".format(value))
    return True


def command_resolve_tests(ui, arg):
    ui.test_manager.resolve_tests()
    return True


def command_soln(ui, arg):
    if len(arg) == 0:
        ui.show_all_answers = not ui.show_all_answers
    else:
        ui.show_all_answers = arg.strip().lower() == "all"

    print(f"Show all solutions is now: {ui.show_all_answers}")

    return True


def command_run_parse(ui, arg):
    if arg.strip() == '':
        ui.run_mrs_index = None
        ui.run_tree_index = None
        print("Runparse is off")
        return True

    parts = arg.split(",")

    ui.run_mrs_index = int(parts[0])
    if len(parts) == 2:
        ui.run_tree_index = int(parts[1])

    return True


def command_run_folder(ui, arg):
    ui.test_manager.record_session_data("LastTestFolder", arg)
    test_iterator = TestFolderIterator(ui.test_manager, arg)
    ui.test_manager.run_tests(test_iterator, ui)

    return True


def command_resume_test(ui, arg):
    test_folder = ui.test_manager.get_session_data("LastTestFolder")
    if test_folder is None:
        print(f"Nothing to resume.")
        return True

    else:
        if test_folder == "":
            test_name = ui.test_manager.get_session_data("LastTest")
            if test_name is None:
                print("No test to resume.")
                return True

            else:
                print(f"**** Resuming test: {test_name}")
                test_iterator = TestIterator(ui.test_manager, test_name)

        else:
            print(f"**** Resuming test folder: {test_folder}")
            test_iterator = TestFolderIterator(ui.test_manager, test_folder, resume=True)

        ui.test_manager.run_tests(test_iterator, ui)
        return True


def command_reset(ui, arg):
    ui.state = ui.reset()
    return f"State reset using {module_name(ui.reset)}.{ui.reset.__name__}()."


def command_new(ui, arg):
    arg_parts = arg.split(".")
    if len(arg_parts) < 2:
        print("reset function must be in the form: module_name.function_name")
        return True

    ui.reset = import_function_from_names(".".join(arg_parts[0:-1]), arg_parts[-1])
    return command_reset(ui, arg)


def command_save(ui, arg):
    if arg is None or arg == "":
        path = GetStateDirectoryName("default")
        if not os.path.exists(path):
            os.makedirs(path)
        arg = os.path.join(path, "state.p8y")
    ui.save(arg)
    print(f"World saved at: {arg}")
    return True


def command_load(ui, arg):
    if arg is None or arg == "":
        path = GetStateDirectoryName("default")
        arg = os.path.join(path, "state.p8y")
        if not os.path.exists(arg):
            print("There is no saved state")

    ui.new_ui = load_ui(arg)
    print(f"World loaded from: {arg}")
    return True


def command_help(ui, arg):
    helpText = "\nCommands start with /:\n"

    category = None
    for descKey in command_data.keys():
        if command_data[descKey]["Category"] != category:
            category = command_data[descKey]["Category"]
            helpText += f"\n****** {category} ******\n"

        helpText += "/" + descKey + " " + command_data[descKey]["Description"] + " -> e.g. " + command_data[descKey]["Example"] + "\n"
    print(helpText)
    return True


def command_debug_tree(ui, arg):
    predication_name = None
    if arg != "":
        parts = arg.split("(")
        predication_name = parts[0]
        arg_parts = parts[1].split(",")
        arg_parts[-1] = arg_parts[-1].strip(")")

        predication_args = []
        for part in arg_parts:
            clean_arg = part.strip()
            if clean_arg in ["_", "None", "none", ""]:
                predication_args.append("_")
            else:
                predication_args.append(clean_arg)

        print(f"searching for trees containing predication: {predication_name}({','.join(predication_args)})\n")

    if ui.interaction_record is not None:
        for mrs_index in range(0, len(ui.interaction_record["Mrss"])):
            mrs_record = ui.interaction_record["Mrss"][mrs_index]

            if len(mrs_record["Trees"]) == 1 and mrs_record["Trees"][0]["Tree"] is None:
                # The trees aren't generated if we don't know terms for performance
                # reasons (since we won't be evaluating anything)
                tree_generator = [{"Tree": tree,
                                   "Solutions": [],
                                   "Error": None,
                                   "ResponseMessage": None} for tree in ui.mrs_parser.trees_from_mrs(mrs_record["Mrs"])]
            else:
                tree_generator = mrs_record["Trees"]

            for tree_info in tree_generator:
                if predication_name is not None:
                    if len(find_predications_with_arg_types(tree_info["Tree"], predication_name, predication_args)):
                        print(f"Found in parse #{mrs_index}:\n")
                        draw_tree = create_draw_tree(mrs_record["Mrs"], tree_info["Tree"])
                        renderer = TreeRenderer()
                        renderer.print_tree(draw_tree)
                        print(f"\nText Tree: {tree_info['Tree']}\n")

                    break
                else:
                    print(f"QUOTED: {str(find_predications(tree_info['Tree'], 'quoted'))}")

    return True


def command_debug_mrs(ui, arg):
    if ui.interaction_record is not None:
        for mrs_index in range(0, len(ui.interaction_record["Mrss"])):
            found =[]
            mrs_record = ui.interaction_record["Mrss"][mrs_index]
            for predication in mrs_record["Mrs"].predications:
                if predication.predicate == "quoted" or predication.predicate == "fw_seq":
                    found.append(predication)

            print(found)

    return True


logger = logging.getLogger('UserInterface')
pipeline_logger = logging.getLogger('Pipeline')
command_data = {
    "help": {"Function": command_help, "Category": "General",
             "Description": "Get list of commands", "Example": "/help"},
    "r": {"Function": command_repeat, "Category": "General",
            "Description": "Repeat the last phrase",
            "Example": "/r"},
    "s": {"Function": command_repeat_system_command, "Category": "General",
            "Description": "Repeat the last system command (i.e. the /command)",
            "Example": "/s"},
    "new": {"Function": command_new, "Category": "General",
            "Description": "Calls the passed function to get the new state to use",
            "Example": "/new examples.Example18_reset"},
    "reset": {"Function": command_reset, "Category": "General",
              "Description": "Resets to the initial state",
              "Example": "/reset"},
    "save": {"Function": command_save, "Category": "General",
              "Description": "Saves the current world state to the ./data/default directory. If given a path, saves to that path instead.",
              "Example": "/save"},
    "load": {"Function": command_load, "Category": "General",
             "Description": "Loads the current world state from the ./data/default directory. If given a path, loads from that path instead.",
             "Example": "/load"},
    "show": {"Function": command_show, "Category": "Parsing",
             "Description": "Shows tracing information from last command. Add 'all' to see all interpretations, 1 to see only first trees",
             "Example": "/show or /show all or /show all, 1"},
    "soln": {"Function": command_soln, "Category": "Parsing",
             "Description": "Retrieves all solutions when parsing so they can be shown with /show. Add 'all' to see all solutions, anything else toggles the current setting",
             "Example": "/soln or /soln all"},
    "runall": {"Function": command_run_all_parses, "Category": "Parsing",
                  "Description": "Runs all parses, doesn't stop after success",
                  "Example": "/runall 1 OR /runall True"},
    "runparse": {"Function": command_run_parse, "Category": "Parsing",
                  "Description": "Only runs the identified parse index and optional tree index. Pass no arguments to turn off",
                  "Example": "/runparse 1 OR /runparse 1, 0"},
    "debugtree": {"Function": command_debug_tree, "Category": "Parsing",
                  "Description": "Shows tracing information about the tree. give a predication query after to only show trees that match it. Use '_' to mean 'anything' for an argument or the predication name",
                  "Example": "/debugtree OR /debugtree which(x,h,h) OR /debugtree _(e,x,_,h)"},
    "debugmrs": {"Function": command_debug_mrs, "Category": "Parsing",
                  "Description": "Shows tracing information about the mrs",
                  "Example": "/debugmrs"},
    "recordtest": {"Function": command_record_test, "Category": "Testing",
                   "Description": "Starts recording a test. Finish with /createtest or /appendtest", "Example": "/record"},
    "createtest": {"Function": command_create_test, "Category": "Testing",
                   "Description": "Creates a test using name you specify based on the interactions recorded by /record",
                   "Example": "/createtest Foo"},
    "appendtest": {"Function": command_append_test, "Category": "Testing",
                   "Description": "Appends the interactions recorded by /record to an existing test",
                   "Example": "/appendtest Foo"},
    "runtest": {"Function": command_run_test, "Category": "Testing",
                "Description": "Runs a test",
                "Example": "/runtest subdirectory/foo"},
    "resolvetests": {"Function": command_resolve_tests, "Category": "Testing",
                "Description": "Resolves all the test results stored in 'testresults.txt'",
                "Example": "/resolvetests"},
    "logtests": {"Function": command_log_tests, "Category": "Testing",
                "Description": "Logs test results to the file 'testresults.txt'",
                "Example": "/logtests true"},
    "runfolder": {"Function": command_run_folder, "Category": "Testing", "WebSafe": False,
                  "Description": "Runs all tests in a directory",
                  "Example": "/runfolder foldername"},
    "resume": {"Function": command_resume_test, "Category": "Testing", "WebSafe": False,
                  "Description": "Resume running the last test (or sequence of tests in a folder) at the last reset before it was stopped",
                  "Example": "/resume"}
    }
