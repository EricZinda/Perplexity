import importlib
import logging
import os
import platform
import sys
from delphin import ace
from delphin.codecs import simplemrs

from perplexity.execution import ExecutionContext, MessageException
from perplexity.print_tree import create_draw_tree, TreeRenderer
from perplexity.test_manager import TestManager, TestIterator, TestFolderIterator
from perplexity.tree import find_predication, tree_from_assignments
from perplexity.tree_algorithm_zinda2020 import valid_hole_assignments
from perplexity.utilities import sentence_force, module_name, import_function_from_names


def no_error_priority(error):
    if error is None:
        return 0
    else:
        return 1


class UserInterface(object):
    def __init__(self, reset, vocabulary, response_function, error_priority_function=no_error_priority):
        self.max_holes = 13
        self.reset = reset
        self.state = reset()
        self.execution_context = ExecutionContext(vocabulary)
        self.response_function = response_function
        self.error_priority_function = error_priority_function
        self.interaction_record = None
        self.records = None
        self.test_manager = TestManager()
        self.user_input = None

    # response_function gets passed three arguments:
    #   response_function(mrs, solutions, error)
    # It must use them to return a string to say to the user
    # Builds up a record of what happened so diagnostics
    # can be printed later
    def interact_once(self, force_input=None):
        if force_input is None:
            # input() pauses the program and waits for the user to
            # type input and hit enter, and then returns it
            self.user_input = str(input("? "))
        else:
            self.user_input = force_input

        command_result = self.handle_command(self.user_input)
        if command_result is True:
            return

        self.interaction_record = {"UserInput": self.user_input,
                                   "Mrss": [],
                                   "ChosenMrsIndex": None,
                                   "ChosenTreeIndex": None,
                                   "ChosenResponse": None,
                                   "ChosenError": None}

        if command_result is not None:
            print(command_result)
            self.interaction_record["ChosenResponse"] = command_result

        else:
            self.test_manager.record_session_data("last_phrase", self.user_input)

        # self.records is a list if we are recording commands
        if isinstance(self.records, list):
            self.records.append(self.interaction_record)
            print(f"Recorded ({len(self.records)} items).")

        if command_result is not None:
            return

        # Loop through each MRS and each tree that can be
        # generated from it...
        for mrs in self.mrss_from_phrase(self.user_input):
            # print(simplemrs.encode(mrs, indent=True))
            mrs_record = {"Mrs": mrs,
                          "UnknownWords": self.unknown_words(mrs),
                          "Trees": []}
            self.interaction_record["Mrss"].append(mrs_record)

            if len(mrs_record["UnknownWords"]) > 0:
                unknown_words_error = [0, ["unknownWords", mrs_record["UnknownWords"]]]
                tree_record = {"Tree": None,
                               "Solutions": [],
                               "Error": unknown_words_error,
                               "ResponseMessage": self.response_function(None, [], unknown_words_error)}
                mrs_record["Trees"].append(tree_record)
                self.evaluate_best_response()

            else:
                for tree in self.trees_from_mrs(mrs):
                    tree_record = {"Tree": tree,
                                   "Solutions": [],
                                   "Error": None,
                                   "ResponseMessage": None}
                    mrs_record["Trees"].append(tree_record)

                    # Collect all the solutions for this tree against the
                    # current world state
                    tree_info = {"Index": mrs.index,
                                 "Variables": mrs.variables,
                                 "Tree": tree}

                    for item in self.execution_context.solve_mrs_tree(self.state, tree_info):
                        pipeline_logger.debug(f"solution: {item}")
                        tree_record["Solutions"].append(item)

                    # Determine the response to it
                    tree_record["Error"] = self.execution_context.error()
                    pipeline_logger.debug(f"{len(tree_record['Solutions'])} solutions, error: {tree_record['Error']}")
                    tree_record["ResponseMessage"] = self.response_function(tree_info, tree_record["Solutions"], tree_record["Error"])
                    if len(tree_record["Solutions"]) > 0:
                        # If there were solutions, this is our answer,
                        # return it and stop looking
                        self.evaluate_best_response()

                        # This worked, apply the results to the current world state if it was a command
                        if sentence_force(tree_info["Variables"]) == "comm":
                            try:
                                self.apply_solutions_to_state(tree_record["Solutions"])

                            except MessageException as error:
                                response = self.response_function(tree_info, [], [0, error.message_object()])
                                tree_record["ResponseMessage"] += f"\n{str(response)}"

                        print(tree_record["ResponseMessage"])
                        return

                    else:
                        # This failed, remember it if it is the "best" failure
                        # which we currently define as the first one
                        self.evaluate_best_response()

        # If we got here, nothing worked: print out the best failure
        print(self.interaction_record["ChosenResponse"])

    def evaluate_best_response(self):
        current_mrs_index = len(self.interaction_record["Mrss"]) - 1
        current_tree_index = len(self.interaction_record["Mrss"][current_mrs_index]["Trees"]) - 1
        tree_record = self.interaction_record["Mrss"][current_mrs_index]["Trees"][current_tree_index]

        # If there was a success, return it as the best answer
        if len(tree_record["Solutions"]) > 0 or \
                (self.error_priority_function(tree_record["Error"]) > self.error_priority_function(self.interaction_record["ChosenError"])):
            self.interaction_record["ChosenMrsIndex"] = current_mrs_index
            self.interaction_record["ChosenTreeIndex"] = current_tree_index
            self.interaction_record["ChosenError"] = tree_record["Error"]
            self.interaction_record["ChosenResponse"] = tree_record["ResponseMessage"]
            pipeline_logger.debug(f"Recording best answer: {self.interaction_record['ChosenResponse']}")

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

    def print_diagnostics(self, all):
        if self.interaction_record is not None:
            print(f"User Input: {self.interaction_record['UserInput']}")
            print(f"{len(self.interaction_record['Mrss'])} Parses")

            for mrs_index in range(0, len(self.interaction_record["Mrss"])):
                if all or mrs_index == self.interaction_record["ChosenMrsIndex"]:
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

                    self.print_diagnostics_trees(all, mrs_index, chosen_tree, mrs_record)

    def print_diagnostics_trees(self, all, parse_number, chosen_tree, mrs_record):
        if len(mrs_record["Trees"]) == 1 and mrs_record["Trees"][0]["Tree"] is None:
            # The trees aren't generated if we don't know terms for performance
            # reasons (since we won't be evaluating anything)
            tree_generator = [{"Tree": tree,
                               "Solutions": [],
                               "Error": None,
                               "ResponseMessage": None} for tree in self.trees_from_mrs(mrs_record["Mrs"])]
        else:
            tree_generator = mrs_record["Trees"]

        tree_index = 0
        for tree in tree_generator:
            if all or chosen_tree == tree_index:
                extra = "CHOSEN " if chosen_tree == tree_index else ""
                print(f"\n-- {extra}Parse #{parse_number}, {extra}Tree #{tree_index}: \n")
                draw_tree = create_draw_tree(mrs_record["Mrs"], tree["Tree"])
                renderer = TreeRenderer()
                renderer.print_tree(draw_tree)
                print(f"\nText Tree: {tree['Tree']}")
                if len(tree['Solutions']) > 0:
                    for solution in tree['Solutions']:
                        print(f"Solution: {str(solution)}")

                else:
                    print(f"Error: {tree['Error']}")

                print(f"Response:\n{tree['ResponseMessage']}")

            tree_index += 1

    def unknown_words(self, mrs):
        unknown_words = []
        phrase_type = sentence_force(mrs.variables)
        for predication in mrs.predications:
            argument_types = []
            for argument_item in predication.args.items():
                if argument_item[0] == "CARG":
                    argument_types.append("c")
                else:
                    argument_types.append(argument_item[1][0])
            predications = list(self.execution_context.vocabulary.predications(predication.predicate, argument_types, phrase_type))
            if len(predications) == 0:
                # This predication is not implemented
                unknown_words.append((predication.predicate,
                                      argument_types,
                                      phrase_type,
                                      # Record if at least one form is understood for
                                      # better error messages
                                      self.execution_context.vocabulary.version_exists(predication.predicate)))

        if len(unknown_words) > 0:
            pipeline_logger.debug(f"Unknown predications: {unknown_words}")

        return unknown_words

    def apply_solutions_to_state(self, solutions):
        # Collect all of the operations that were done
        all_operations = []
        for solution in solutions:
            all_operations += solution.get_operations()

        # Now apply all the operations to the original state object and
        # print it to prove it happened
        self.state = self.state.apply_operations(all_operations, False)
        logger.debug(f"Final state: {self.state.objects}")

    def mrss_from_phrase(self, phrase):
        # Don't print errors to the screen
        f = open(os.devnull, 'w')

        # Create an instance of the ACE parser and ask to give <= 100 MRS documents
        with ace.ACEParser(self.erg_file(), cmdargs=['-n', '100'], stderr=f) as parser:
            ace_response = parser.interact(phrase)
            pipeline_logger.debug(f"{len(ace_response['results'])} parse options for {phrase}")

        for parse_index in range(0, len(ace_response.results())):
            # Keep track of the original phrase on the object
            mrs = ace_response.result(parse_index).mrs()
            mrs.surface = phrase
            pipeline_logger.debug(f"Parse {parse_index}: {mrs}")
            yield mrs

    def trees_from_mrs(self, mrs):
        # Create a dict of predications using their labels as each key
        # for easy access when building trees
        # Note that a single label could represent multiple predications
        # in conjunction so we need a list for each label
        mrs_predication_dict = {}
        for predication in mrs.predications:
            if predication.label not in mrs_predication_dict.keys():
                mrs_predication_dict[predication.label] = []
            mrs_predication_dict[predication.label].append(predication)

        # Iteratively return well-formed trees from the MRS
        for holes_assignments in valid_hole_assignments(mrs, self.max_holes):
            # valid_hole_assignments can return None if the grammar returns something
            # that doesn't have the same number of holes and floaters (which is a grammar bug)
            if holes_assignments is not None:
                # Now we have the assignments of labels to holes, but we need
                # to actually build the *tree* using that information
                well_formed_tree = tree_from_assignments(mrs.top,
                                                         holes_assignments,
                                                         mrs_predication_dict,
                                                         mrs)
                pipeline_logger.debug(f"Tree: {well_formed_tree}")
                yield well_formed_tree

    def erg_file(self):
        if sys.platform == "linux":
            ergFile = "erg-2020-ubuntu-perplexity.dat"

        elif sys.platform == "darwin":
            # Mac returns darwin for both M1 and Intel silicon, need to dig deeper
            unameResult = platform.uname()

            if "ARM" in unameResult.version:
                # M1 silicon
                ergFile = "erg-2020-osx-m1-perplexity.dat"

            else:
                # Intel silicon
                ergFile = "erg-2020-osx-perplexity.dat"

        else:
            ergFile = "erg-2020-ubuntu-perplexity.dat"

        return ergFile


def command_show(ui, arg):
    all = arg.lower() == "all"
    ui.print_diagnostics(all)
    return True


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
        ui.test_manager.create_test(ui.reset, arg, ui.records)
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
        test_iterator = TestIterator(ui.test_manager.full_test_path(arg + ".tst"))

        # Set the state to the state function the test requires
        # and reset it
        ui.reset = import_function_from_names(test_iterator.test["ResetModule"], test_iterator.test["ResetFunction"])
        print(command_reset(ui, arg))

        # Now run the tests in that state
        ui.test_manager.run_tests(test_iterator, ui)

    return True


def command_run_folder(ui, arg):
    if len(arg) == 0:
        print(f"Please supply a folder name.")

    else:
        test_iterator = TestFolderIterator(ui.test_manager.full_test_path(arg))
        ui.test_manager.run_tests(test_iterator, ui)

    return True


def command_reset(ui, arg):
    ui.state = ui.reset()
    return f"State reset using {module_name(ui.reset)}.{ui.reset.__name__}()."


def command_new(ui, arg):
    arg_parts = arg.split(".")
    if len(arg_parts) != 2:
        print("reset function must be in the form: module_name.function_name")
        return True

    ui.reset = import_function_from_names(arg_parts[0], arg_parts[1])
    return command_reset(ui, arg)


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


logger = logging.getLogger('UserInterface')
pipeline_logger = logging.getLogger('Pipeline')
command_data = {
    "help": {"Function": command_help, "Category": "General",
             "Description": "Get list of commands", "Example": "/help"},
    "r": {"Function": command_repeat, "Category": "General",
            "Description": "Repeat the last phrase",
            "Example": "/r"},
    "new": {"Function": command_new, "Category": "General",
            "Description": "Calls the passed function to get the new state to use",
            "Example": "/new examples.Example18_reset"},
    "reset": {"Function": command_reset, "Category": "General",
              "Description": "Resets to the initial state",
              "Example": "/reset"},
    "show": {"Function": command_show, "Category": "Parsing",
             "Description": "Shows tracing information from last command. Add 'all' to see all interpretations",
             "Example": "/show or /show all"},
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
    "runfolder": {"Function": command_run_folder, "Category": "Testing", "WebSafe": False,
                  "Description": "Runs all tests in a directory",
                  "Example": "/runfolder foldername"}
}