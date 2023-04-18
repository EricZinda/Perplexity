import logging
import os
import platform
import sys
import perplexity.solution_groups
from delphin import ace
from delphin.codecs import simplemrs
from perplexity.execution import ExecutionContext, MessageException
from perplexity.print_tree import create_draw_tree, TreeRenderer
from perplexity.test_manager import TestManager, TestIterator, TestFolderIterator
from perplexity.tree import tree_from_assignments, find_predications, find_predications_with_arg_types, find_predication
from perplexity.tree_algorithm_zinda2020 import valid_hole_assignments
from perplexity.utilities import sentence_force, module_name, import_function_from_names, at_least_one_generator


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
        self.last_system_command = None
        self.run_mrs_index = None
        self.run_tree_index = None
        self.show_all_answers = False

    def chosen_tree_record(self):
        chosen_mrs_index = self.interaction_record["ChosenMrsIndex"]
        chosen_tree_index = self.interaction_record["ChosenTreeIndex"]
        if chosen_mrs_index is None:
            return None
        else:
            return self.interaction_record["Mrss"][chosen_mrs_index]["Trees"][chosen_tree_index]

    # Errors are encoded in a fake tree
    def new_error_tree_record(self, error=None, response_generator=None):
        return self.new_tree_record(error=error, response_generator=response_generator, error_tree=True)

    def new_tree_record(self, tree=None, error=None, response_generator=None, response_message=None, error_tree=False):
        value = {"Tree": tree,
                 "SolutionGroups": None,
                 "Solutions": [],
                 "Error": error,
                 "ResponseGenerator": [] if response_generator is None else response_generator,
                 "ResponseMessage": "" if response_message is None else response_message}

        if error_tree:
            value["ErrorTree"] = True

        return value

    def new_mrs_record(self, mrs=None, unknown_words=None):
        return {"Mrs": mrs,
                "UnknownWords": unknown_words,
                "Trees": []}

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
            tree_record = self.new_error_tree_record(response_generator=[command_result])
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
        for mrs in self.mrss_from_phrase(self.user_input):
            mrs_index += 1
            tree_index = -1
            if self.run_mrs_index is not None and self.run_mrs_index != mrs_index:
                continue

            mrs_record = self.new_mrs_record(mrs=mrs, unknown_words=self.unknown_words(mrs))
            self.interaction_record["Mrss"].append(mrs_record)

            if len(mrs_record["UnknownWords"]) > 0:
                unknown_words_error = [0, ["unknownWords", mrs_record["UnknownWords"]]]
                tree_record = self.new_error_tree_record(error=unknown_words_error, response_generator=self.response_function(None, [], unknown_words_error))
                mrs_record["Trees"].append(tree_record)
                self.evaluate_best_response()

            else:
                for tree in self.trees_from_mrs(mrs):
                    tree_index += 1
                    if self.run_tree_index is not None and self.run_tree_index != tree_index:
                        continue

                    tree_record = self.new_tree_record(tree=tree)
                    mrs_record["Trees"].append(tree_record)

                    # Collect all the solutions for this tree against the
                    # current world state
                    tree_info = {"Index": mrs.index,
                                 "Variables": mrs.variables,
                                 "Tree": tree}

                    duplicate_solutions = []
                    for item in self.execution_context.solve_mrs_tree(self.state, tree_info):
                        if logger.isEnabledFor(logging.DEBUG):
                            pipeline_logger.debug(f"solution: {item}")
                        duplicate_solutions.append(item)

                    # pipeline_logger.debug(f"Removing duplicates from {len(duplicate_solutions)} solutions ...")
                    # duplicate_solutions = perplexity.determiners.remove_duplicates(duplicate_solutions)
                    pipeline_logger.debug(f"{len(duplicate_solutions)} undetermined solutions.")
                    is_wh_phrase = sentence_force(tree_info["Variables"]) == "ques" and find_predication(tree_info["Tree"], "_which_q")
                    if self.show_all_answers:
                        tree_record["SolutionGroups"] = list(perplexity.solution_groups.solution_groups(self.execution_context, duplicate_solutions, is_wh_phrase))
                        tree_record["Solutions"] = [solution for solution_group in tree_record["SolutionGroups"] for solution in solution_group]
                    else:
                        temp = perplexity.solution_groups.solution_groups(self.execution_context, duplicate_solutions, is_wh_phrase)
                        tree_record["SolutionGroups"] = at_least_one_generator(temp)

                    # Determine the response to it
                    tree_record["Error"] = self.execution_context.error()
                    tree_record["ResponseGenerator"] = self.response_function(tree_info, tree_record["SolutionGroups"], tree_record["Error"])
                    if tree_record["SolutionGroups"] is not None:
                        # If there were solutions, this is our answer,
                        # return it and stop looking
                        self.evaluate_best_response()

                        # This worked, apply the results to the current world state if it was a command
                        if sentence_force(tree_info["Variables"]) == "comm":
                            tree_record["SolutionGroups"] = [[solution for solution in group] for group in tree_record["SolutionGroups"]]

                            try:
                                self.apply_solutions_to_state([solution for group in tree_record["SolutionGroups"] for solution in group])

                            except MessageException as error:
                                response = self.response_function(tree_info, [], [0, error.message_object()])
                                tree_record["ResponseMessage"] += f"\n{str(response)}"

                        for response in tree_record["ResponseGenerator"]:
                            tree_record["ResponseMessage"] += response
                            print(response)

                        return

                    else:
                        # This failed, remember it if it is the "best" failure
                        # which we currently define as the first one
                        self.evaluate_best_response()

        # If we got here, nothing worked: print out the best failure
        chosen_record = self.chosen_tree_record()
        for response in chosen_record["ResponseGenerator"]:
            chosen_record["ResponseMessage"] += response
            print(response)

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

    def evaluate_best_response(self):
        current_mrs_index = len(self.interaction_record["Mrss"]) - 1
        current_tree_index = len(self.interaction_record["Mrss"][current_mrs_index]["Trees"]) - 1
        tree_record = self.interaction_record["Mrss"][current_mrs_index]["Trees"][current_tree_index]
        chosen_record = self.chosen_tree_record()
        chosen_error = chosen_record["Error"] if chosen_record is not None else None
        # If there was a success, return it as the best answer
        if tree_record["SolutionGroups"] is not None or \
                (self.error_priority_function(tree_record["Error"]) > self.error_priority_function(chosen_error)):
            self.interaction_record["ChosenMrsIndex"] = current_mrs_index
            self.interaction_record["ChosenTreeIndex"] = current_tree_index
            pipeline_logger.debug(f"Recording best answer: MRSIndex {current_mrs_index}, TreeIndex: {current_tree_index}, Error: {tree_record['Error'] if tree_record['SolutionGroups'] is None else 'none'}")

    # Commands always start with "/", followed by a string of characters and then
    # a space. Any arguments are after the space and their format is command specific.
    # For example:
    #   /show all
    # If it returns:
    # True: Command was handled and should not be recorded
    # None: Was not a command
    # Str: The string that should be recorded for the command
    def handle_command(self, text):
        # try:
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

        # except Exception as error:
        #     print(str(error))
        #     return True

        return None

    def print_diagnostics(self, all, first_tree_only):
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

                    self.print_diagnostics_trees(all, mrs_index, chosen_tree, mrs_record, first_tree_only)

    def print_diagnostics_trees(self, all, parse_number, chosen_tree, mrs_record, first_tree_only):
        # is_system_command_record = len(mrs_record["Trees"]) == 1 and mrs_record["Mrs"] is None and "ErrorTree" in mrs_record["Trees"][0]
        is_ungenerated_tree = len(mrs_record["Trees"]) == 1 and mrs_record["Mrs"] is not None and "ErrorTree" in mrs_record["Trees"][0]
        if is_ungenerated_tree:
            # The trees aren't generated if we don't know terms for performance
            # reasons (since we won't be evaluating anything)
            tree_generator = []
            for tree in self.trees_from_mrs(mrs_record["Mrs"]):
                tree_generator.append(self.new_tree_record(tree=tree, error=mrs_record["Trees"][0]["Error"], response_generator=mrs_record["Trees"][0]["ResponseGenerator"], response_message=mrs_record["Trees"][0]["ResponseMessage"]))

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
                if isinstance(tree_info['SolutionGroups'], list) and len(tree_info['SolutionGroups']) > 0:
                    print(f"\nSolution groups:")
                    for solution_group in tree_info['SolutionGroups']:
                        print(f"")
                        for solution in solution_group:
                            print(f"{str(solution)}")

                else:
                    print(f"Error: {tree_info['Error']}")

                if tree_info['ResponseMessage'] == "" and tree_info['ResponseGenerator'] is not None:
                    tree_info['ResponseMessage'] = ""
                    for response in tree_info['ResponseGenerator']:
                        tree_info['ResponseMessage'] += response
                print(f"Response:\n{tree_info['ResponseMessage']}")

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
        with ace.ACEParser(self.erg_file(), cmdargs=[], stderr=f) as parser:
        # with ace.ACEParser(self.erg_file(), cmdargs=['-n', '1000'], stderr=f) as parser:
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


def command_soln(ui, arg):
    if len(arg) == 0:
        ui.show_all_answers = not ui.show_all_answers
    else:
        ui.show_all_answers = arg.strip().lower() == "all"

    print(f"Show all solutions is now: {ui.show_all_answers}")

    return True


def command_run_parse(ui, arg):
    parts = arg.split(",")
    if len(parts) == 0 or len(parts) > 2:
        print("Please supply a parseindex, treeindex or just a parseindex")

    ui.run_mrs_index = int(parts[0])
    if len(parts) == 2:
        ui.run_tree_index = int(parts[1])

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
                                   "ResponseMessage": None} for tree in ui.trees_from_mrs(mrs_record["Mrs"])]
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
    "show": {"Function": command_show, "Category": "Parsing",
             "Description": "Shows tracing information from last command. Add 'all' to see all interpretations, 1 to see only first trees",
             "Example": "/show or /show all or /show all, 1"},
    "soln": {"Function": command_soln, "Category": "Parsing",
             "Description": "Retrieves all solutions when parsing so they can be shown with /show. Add 'all' to see all solutions, anything else to only see what is required",
             "Example": "/soln or /soln all"},
    "runparse": {"Function": command_run_parse, "Category": "Parsing",
                  "Description": "Only runs the identified parse index and optional tree index",
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
    "runfolder": {"Function": command_run_folder, "Category": "Testing", "WebSafe": False,
                  "Description": "Runs all tests in a directory",
                  "Example": "/runfolder foldername"}
}