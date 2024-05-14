import copy
import json
import logging
import os
import sys
import time
import traceback
import uuid
from perplexity.utilities import module_name, import_function_from_names, running_under_debugger
from perplexity.world_registry import world_information


# Just a simple iterator that must return
# a new test item each time it is asked
# TestIterators must return test items when iterated
# "test items" are JSON objects in a format like this:
#
# {
#     "WorldName": "esl",
#     "TestItems": [
#         {
#             "Command": "/reset",
#             "Expected": "state reset.",
#             "Tree": null,
#             "Enabled": true,
#             "ID": "8290fec8-aff8-48b7-94db-2f58512c0e27"
#         },
#
#         ...
#
# They must also support the "update_test()" method
class TestIterator(object):
    def __init__(self, test_manager, test_path_and_file, resume=False):
        print(f"**** Running test: {test_path_and_file}...\n")
        relative_path = os.path.relpath(test_path_and_file, start=test_manager.test_root_folder)
        split_path = os.path.split(relative_path)
        self.test_folder = split_path[0]
        self.test_name, _ = os.path.splitext(split_path[1])

        self.resume = resume
        self.test_manager = test_manager
        self.test_path_and_file = test_path_and_file

        if resume:
            self.target_index = test_manager.get_session_data("LastTestResetIndex")

        with open(test_path_and_file, "r") as file:
            self.test = json.loads(file.read())

        self.world_name = self.test["WorldName"]

        # Make sure all IDs are unique!
        ids = {}
        for test_item in self.test["TestItems"]:
            if test_item["ID"] in ids:
                test_item["ID"] = str(uuid.uuid4())
            else:
                ids[test_item["ID"]] = True

        if len(ids) != len(self.test["TestItems"]):
            with open(self.test_path_and_file, "w") as file:
                file.write(json.dumps(self.test, indent=4))

        self.index = 0

    def __iter__(self):
        test_items = self.test["TestItems"]
        self.test_manager.record_session_data("LastTest", self.test_path_and_file)
        if not self.resume:
            self.test_manager.record_session_data("LastTestResetIndex", 0)

        while self.index < len(test_items):
            current_index = self.index
            self.index += 1
            test_item = test_items[current_index]

            if self.resume:
                if self.target_index is not None and current_index < self.target_index:
                    continue
                else:
                    self.resume = False

            if test_item["Enabled"]:
                if not self.resume:
                    if test_item["Command"].startswith("/new") or test_item["Command"].startswith("/reset"):
                        self.test_manager.record_session_data("LastTestResetIndex", current_index)

                yield test_item

    def test_from_id(self, id):
        for item_index in range(0, len(self.test["TestItems"])):
            if self.test["TestItems"][item_index]["ID"] == id:
                return self.test["TestItems"][item_index]

    def update_test(self, id, new_item):
        for item_index in range(0, len(self.test["TestItems"])):
            if self.test["TestItems"][item_index]["ID"] == id:
                self.test["TestItems"][item_index] = new_item
                with open(self.test_path_and_file, "w") as file:
                    file.write(json.dumps(self.test, indent=4))
                return

        assert False, f"Test ID '{id}' not found"


# This is a test iterator that loops through all tests
# in a folder, and returns the test items within each test
class TestFolderIterator(object):
    def __init__(self, test_manager, test_folder, resume=False):
        self.test_folder = test_folder
        self.test_path_and_file = None
        self.test_manager = test_manager
        self.test_name = None
        self.world_name = None
        self.resume = resume
        self.record_time = False
        if self.resume:
            self.current_test = test_manager.get_session_data("LastTest")

    def __iter__(self):
        for filename in sorted(os.listdir(self.test_manager.full_test_path(self.test_folder))):
            if filename.lower().endswith(".tst"):
                self.record_time = not running_under_debugger()
                self.test_path_and_file = os.path.join(self.test_manager.full_test_path(self.test_folder), filename)
                if self.resume:
                    if self.current_test is not None and self.test_path_and_file.lower() != self.current_test.lower():
                        continue

                self.current_test = self.test_path_and_file
                self.test_iterator = TestIterator(self.test_manager, self.current_test, resume=self.resume)
                self.test_name = self.test_iterator.test_name
                self.world_name = self.test_iterator.world_name
                self.resume = False
                testStartTime = time.perf_counter()
                yield from self.test_iterator
                elapsed = round(time.perf_counter() - testStartTime, 5)
                if self.record_time:
                    self.test_manager.update_test_info(self.test_path_and_file, {"ElapsedTime": elapsed})

    def update_test(self, id, new_item):
        self.test_iterator.update_test(id, new_item)


# This is the class that implements the bulk of the
# testing behavior
class TestManager(object):
    def __init__(self, root_directory=None):
        # Default location for tests is under the directory
        # where this file lives
        self.test_root_folder = root_directory if root_directory is not None \
            else os.path.join(os.path.dirname(os.path.realpath(__file__)), "tests")
        if not os.path.exists(self.test_root_folder):
            os.makedirs(self.test_root_folder)
        self.current_world_name = None
        self.load_session_data()
        self.final_ui = None

    def full_test_path(self, test_name):
        return os.path.join(self.test_root_folder, test_name)

    def run_tests(self, test_iterator, initial_ui):
        if initial_ui.log_tests:
            scriptPath = os.path.dirname(os.path.realpath(__file__))
            testFile = os.path.join(scriptPath, "testresults.txt")
            if os.path.exists(testFile):
                os.remove(testFile)
            testResultsFile = open(testFile, "w")
            print(f"Logging test results to: {testFile}")

        else:
            testResultsFile = None

        print("\n**** Begin Testing...\n")
        testItemStartTime = time.perf_counter()
        test_ui = None
        conjunct_input = None
        conjunct_mrs_index = None
        conjunct_tree_index = None
        next_conjuncts = None
        for test_item in test_iterator:
            if test_iterator.world_name != self.current_world_name or test_ui is None:
                # World changed, load the new world
                world_info = world_information(test_iterator.world_name)
                if world_info is None:
                    print(f"World {test_iterator.world_name} is not registered as a world")
                    return
                else:
                    test_ui_function = import_function_from_names(world_info["WorldModule"], world_info["WorldUIFunction"])
                    test_ui = test_ui_function()
                    self.current_world_name = test_iterator.world_name

            try:
                if test_item['Command'] in ["/next_conjunct"]:
                    # This is a test item meant to test the next conjuct of a phrase that includes a conjunction
                    print(f"\nTest: Next conjunct of: '{conjunct_input}'")
                    if next_conjuncts is None:
                        # There is no conjuct to be "next"
                        result = "There is no conjuct to be 'next''"
                        interaction_response = ""
                        interaction_tree = None

                    else:
                        test_ui.interact_once(force_input=conjunct_input,
                                              conjunct_mrs_index=conjunct_mrs_index,
                                              conjunct_tree_index=conjunct_tree_index,
                                              next_conjuncts=next_conjuncts)

                        interaction_response, interaction_tree, result = self.get_result_from_interaction(test_iterator,
                                                                                                            test_item,
                                                                                                            test_ui.interaction_record)
                        # Assume there are only ever 2 conjunctions and end now
                        conjunct_mrs_index = None
                        conjunct_tree_index = None
                        next_conjuncts = None

                else:
                    if next_conjuncts is not None:
                        # There are unhandled conjuncts from the previous statement
                        print(f"**** HALTING: There are unhandled conjuncts from the previous statement. Please add tests with a command of '/next_conjunct' to handle them")
                        break

                    print(f"\nTest: {test_item['Command']}")

                    itemStartTime = time.perf_counter()
                    test_ui.interact_once(test_item["Command"])
                    elapsed = round(time.perf_counter() - itemStartTime, 5)
                    logger.debug(f"Test timing: {elapsed}")

                    record = test_ui.chosen_interpretation_record()
                    conjunct_input = test_ui.user_input
                    if record is not None and "SelectedConjuncts" in record and record["SelectedConjuncts"] is not None and record["SelectedConjuncts"][0] == 0:
                        # This phrase generated conjuncts, remember them
                        next_conjuncts = [1]
                        conjunct_mrs_index = test_ui.interaction_record["ChosenMrsIndex"]
                        conjunct_tree_index = test_ui.interaction_record["Mrss"][test_ui.interaction_record["ChosenMrsIndex"]]["Interpretations"][test_ui.interaction_record["ChosenInterpretationIndex"]]["TreeIndex"]

                    else:
                        conjunct_mrs_index = None
                        conjunct_tree_index = None
                        next_conjuncts = None

                    interaction_response, interaction_tree, result = self.get_result_from_interaction(test_iterator, test_item, test_ui.interaction_record)

            except Exception as error:
                print(f"**** HALTING: Exception in test run: {error}")
                traceback.print_tb(error.__traceback__, file=sys.stdout)
                break

            if result is not None:
                # Don't record this timing since a test item failed
                test_iterator.record_time = False
                if testResultsFile:
                    # if silent, just log result
                    self.log_test_result(testResultsFile,
                                         test_iterator.test_folder,
                                         test_iterator.test_name,
                                         test_item["ID"],
                                         test_ui.interaction_record["UserInput"],
                                         interaction_response,
                                         interaction_tree)

                else:
                    # otherwise interactively resolve
                    prompt = self.get_prompt(test_iterator, test_item, interaction_response, interaction_tree)
                    if prompt is not None:
                        print(prompt)
                        if not self.resolve_result(test_iterator, test_item, interaction_response, interaction_tree):
                            print(f"Breaking during {test_iterator.test_folder}:{test_iterator.test_name} -> TestID: {test_item['ID']}")
                            break

        elapsed = round(time.perf_counter() - testItemStartTime, 5)
        self.final_ui = test_ui
        print(f"\n**** Testing Complete. Elapsed time: {elapsed}\n")

    def resolve_tests(self):
        script_path = os.path.dirname(os.path.realpath(__file__))
        test_file = os.path.join(script_path, "testresults.txt")
        iterator_cache = {}
        if os.path.exists(test_file):
            test_results_file = open(test_file, "r")
            print(f"Resolving test results in: {test_file}")

            while True:
                entry_string = test_results_file.readline()
                if entry_string == "":
                    break
                entry = json.loads(entry_string)
                key = (entry["FolderName"], entry["TestName"])
                if key in iterator_cache:
                    test_iterator = iterator_cache[key]

                else:
                    test_iterator = TestIterator(self, os.path.join(self.test_root_folder, entry["FolderName"], entry["TestName"] + ".tst"))
                    iterator_cache[key] = test_iterator
                prompt = self.get_prompt(test_iterator, test_iterator.test_from_id(entry["TestID"]), entry["InteractionResponse"], entry["InteractionTree"])
                if prompt is not None:
                    print(f"**** Test ID: {entry['TestID']}")
                    print(entry["UserInput"])
                    print(entry["InteractionResponse"])
                    print(prompt)
                    self.resolve_result(test_iterator, test_iterator.test_from_id(entry["TestID"]), entry["InteractionResponse"], entry["InteractionTree"])

        else:
            print(f"No results to resolve.")

    def log_test_result(self, file, folder_name, test_name, test_id, user_input, interaction_response, interaction_tree):
        entry = {"FolderName": folder_name, "TestName": test_name, "TestID": test_id, "UserInput": user_input, "InteractionResponse": interaction_response, "InteractionTree": str(interaction_tree)}
        file.write(json.dumps(entry, indent=None))
        file.write("\n")
        file.flush()

    def resolve_result(self, test_iterator, test_item, interaction_response, interaction_tree):
        while True:
            answer = input(f"(<enter>)ignore, (b)reak to end testing, (u)pdate test, (a) add alternative correct result, (d)isable test\n")
            if answer == "":
                return True

            elif answer == "u":
                updated_test = copy.deepcopy(test_item)
                updated_test["Expected"] = interaction_response
                updated_test["Tree"] = str(interaction_tree)
                test_iterator.update_test(updated_test["ID"], updated_test)
                return True

            elif answer == "d":
                updated_test = copy.deepcopy(test_item)
                updated_test["Enabled"] = False
                test_iterator.update_test(updated_test["ID"], updated_test)
                return True

            elif answer == "b":
                return False

            elif answer == "a":
                updated_test = copy.deepcopy(test_item)
                if isinstance(updated_test["Expected"], list):
                    new_expected = updated_test["Expected"] + [interaction_response]
                else:
                    new_expected = [updated_test["Expected"], interaction_response]

                updated_test["Expected"] = new_expected
                updated_test["Tree"] = str(interaction_tree)
                test_iterator.update_test(updated_test["ID"], updated_test)
                return True

            else:
                print(f"'{answer}' is not a valid option")

    def get_result_from_interaction(self, test_iterator, test_item, interaction_mrs_record):
        chosen_mrs_index = interaction_mrs_record["ChosenMrsIndex"]
        chosen_interpretation_index = interaction_mrs_record["ChosenInterpretationIndex"]
        interaction_record = interaction_mrs_record["Mrss"][chosen_mrs_index]["Interpretations"][chosen_interpretation_index] if chosen_mrs_index is not None and chosen_interpretation_index is not None else None
        interaction_response = interaction_record["ResponseMessage"] if interaction_record is not None else None
        interaction_tree = interaction_record["Tree"] if interaction_record is not None else None
        return interaction_response, interaction_tree, self.get_prompt(test_iterator, test_item, interaction_response, interaction_tree)

    def get_prompt(self, test_iterator, test_item, interaction_response, interaction_tree):
        prompt = None
        if isinstance(test_item["Expected"], list):
            if interaction_response not in test_item["Expected"]:
                prompt = f"\nExpected (one of): \n{test_item['Expected']}"
        elif test_item["Expected"] != interaction_response:
            prompt = f"\nExpected: \n{test_item['Expected']}"
        elif not (test_item["Tree"] is None and interaction_tree is None) and test_item["Tree"] != str(interaction_tree):
            prompt = f"\nPrevious Tree: {test_item['Tree']}\nNew Tree: {str(interaction_tree)}"

        return prompt

    def check_result(self, test_iterator, test_item, interaction_mrs_record):
        chosen_mrs_index = interaction_mrs_record["ChosenMrsIndex"]
        chosen_interpretation_index = interaction_mrs_record["ChosenInterpretationIndex"]
        interaction_record = interaction_mrs_record["Mrss"][chosen_mrs_index]["Interpretations"][chosen_interpretation_index] if chosen_mrs_index is not None and chosen_interpretation_index is not None else None
        interaction_response = interaction_record["ResponseMessage"] if interaction_record is not None else None
        interaction_tree = interaction_record["Tree"] if interaction_record is not None else None

        prompt = None
        if isinstance(test_item["Expected"], list):
            if interaction_response not in test_item["Expected"]:
                prompt = f"\nExpected (one of): {test_item['Expected']}"
        elif test_item["Expected"] != interaction_response:
            prompt = f"\nExpected: {test_item['Expected']}"
        elif not (test_item["Tree"] is None and interaction_tree is None) and test_item["Tree"] != str(interaction_tree):
            prompt = f"\nPrevious Tree: {test_item['Tree']}\nNew Tree: {str(interaction_tree)}"

        if prompt is not None:
            print(prompt)

            while True:
                answer = input(f"(<enter>)ignore, (b)reak to end testing, (u)pdate test, (a) add alternative correct result, (d)isable test\n")
                if answer == "":
                    return True

                elif answer == "u":
                    updated_test = copy.deepcopy(test_item)
                    updated_test["Expected"] = interaction_response
                    updated_test["Tree"] = str(interaction_tree)
                    test_iterator.update_test(updated_test["ID"], updated_test)
                    return True

                elif answer == "d":
                    updated_test = copy.deepcopy(test_item)
                    updated_test["Enabled"] = False
                    test_iterator.update_test(updated_test["ID"], updated_test)
                    return True

                elif answer == "b":
                    return False

                elif answer == "a":
                    updated_test = copy.deepcopy(test_item)
                    if isinstance(updated_test["Expected"], list):
                        new_expected = updated_test["Expected"] + [interaction_response]
                    else:
                        new_expected = [updated_test["Expected"], interaction_response]

                    updated_test["Expected"] = new_expected
                    updated_test["Tree"] = str(interaction_tree)
                    test_iterator.update_test(updated_test["ID"], updated_test)
                    return True

                else:
                    print(f"'{answer}' is not a valid option")

        return True

    def update_test_info(self, test_path_and_file, new_items):
        with open(test_path_and_file, "r") as file:
            test = json.loads(file.read())
            test.update(new_items)
        with open(self.full_test_path(test_path_and_file), "w") as file:
            file.write(json.dumps(test, indent=4))

    def append_test(self, test_name, interaction_records):
        test_path_and_file = self.full_test_path(test_name + ".tst")
        with open(test_path_and_file, "r") as file:
            test = json.loads(file.read())
            self._add_to_test(test, interaction_records)
        with open(self.full_test_path(test_name + ".tst"), "w") as file:
            file.write(json.dumps(test, indent=4))

    def create_test(self, ui, test_name, interaction_records):
        # Remember the name of the module and function
        # that created the state for the test
        # reset_module = module_name(reset)
        # reset_function = reset.__name__

        # Make sure we have the directory structure to hold the test
        test_name_parts = os.path.split(test_name)
        full_path = self.full_test_path(test_name_parts[0])
        if not os.path.exists(full_path):
            os.mkdir(full_path)

        test = {"WorldName": ui.world_name,
                "TestItems": []}

        self._add_to_test(test, interaction_records)
        with open(self.full_test_path(test_name + ".tst"), "w") as file:
            file.write(json.dumps(test, indent=4))

        print(f"Created test '{test_name}'")

    def _add_to_test(self, test, interaction_records):
        if interaction_records is not None:
            test_items = test["TestItems"]
            for interaction_record in interaction_records:
                chosen_mrs_index = interaction_record["ChosenMrsIndex"]
                chosen_interpretation_index = interaction_record["ChosenInterpretationIndex"]
                tree_record = interaction_record["Mrss"][chosen_mrs_index]["Interpretations"][chosen_interpretation_index] if chosen_mrs_index is not None and chosen_interpretation_index is not None else None
                if "SelectedConjuncts" in tree_record and tree_record["SelectedConjuncts"] is not None and tree_record["SelectedConjuncts"][0] > 0:
                    command = "/next_conjuct"
                else:
                    command = interaction_record["UserInput"]

                test_items.append({"Command": command,
                                   "Expected": tree_record["ResponseMessage"] if tree_record is not None else None,
                                   "Tree": str(tree_record["Tree"] if tree_record is not None else None),
                                   "Enabled": True,
                                   "ID": str(uuid.uuid4())
                                   })

    # Used to hold arbitrary information about the
    # session, across runs
    def session_data_path(self):
        return self.full_test_path("session_info.json")

    def load_session_data(self):
        if os.path.exists(self.session_data_path()):
            with open(self.session_data_path(), "r") as file:
                self.session_data = json.loads(file.read())
        else:
            self.session_data = {}

    def record_session_data(self, key, value):
        self.session_data[key] = value
        with open(self.session_data_path(), "w") as file:
            file.write(json.dumps(self.session_data, indent=4))

    def get_session_data(self, key):
        return self.session_data.get(key, None)


logger = logging.getLogger('Testing')
