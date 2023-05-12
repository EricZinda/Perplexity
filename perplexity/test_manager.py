import copy
import json
import os
import sys
import traceback
import uuid
from perplexity.utilities import module_name

# Just a simple iterator that must return
# a new test item each time it is asked
# TestIterators must return test items when iterated
# "test items" are JSON objects in a format like this:
#
# {
#     "ResetModule": "examples",
#     "ResetFunction": "Example16_reset",
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
    def __init__(self, test_path_and_file):
        self.test_path_and_file = test_path_and_file
        with open(test_path_and_file, "r") as file:
            self.test = json.loads(file.read())

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

        while self.index < len(test_items):
            self.index += 1
            test_item = test_items[self.index - 1]
            if test_item["Enabled"]:
                yield test_item

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
    def __init__(self, test_folder):
        self.test_folder = test_folder

    def __iter__(self):
        for filename in os.listdir(self.test_folder):
            if filename.lower().endswith(".tst"):
                self.test_iterator = TestIterator(os.path.join(self.test_folder, filename))
                yield from self.test_iterator

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

        self.load_session_data()

    def full_test_path(self, test_name):
        return os.path.join(self.test_root_folder, test_name)

    def run_tests(self, test_iterator, ui):
        print("\n**** Begin Testing...\n")
        for test_item in test_iterator:
            print(f"\nTest: {test_item['Command']}")
            try:
                ui.interact_once(test_item["Command"])

            except Exception as error:
                print(f"**** HALTING: Exception in test run: {error}")
                traceback.print_tb(error.__traceback__, file=sys.stdout)
                break

            if not self.check_result(test_iterator, test_item, ui.interaction_record):
                print("**** Cancel test run")
                break
        print("\n**** Testing Complete.\n")

    def check_result(self, test_iterator, test_item, interaction_mrs_record):
        chosen_mrs_index = interaction_mrs_record["ChosenMrsIndex"]
        chosen_tree_index = interaction_mrs_record["ChosenTreeIndex"]
        interaction_record = interaction_mrs_record["Mrss"][chosen_mrs_index]["Trees"][chosen_tree_index]

        prompt = None
        if test_item["Expected"] != interaction_record["ResponseMessage"]:
            prompt = f"\nExpected: {test_item['Expected']}"
        elif not (test_item["Tree"] is None and interaction_record["Tree"] is None) and test_item["Tree"] != str(interaction_record["Tree"]):
            prompt = f"\nPrevious Tree: {test_item['Tree']}\nNew Tree: {str(interaction_record['Tree'])}"

        if prompt is not None:
            print(prompt)

            while True:
                answer = input(f"(<enter>)ignore, (b)reak to end testing, (u)pdate test, (d)isable test\n")
                if answer == "":
                    return True

                elif answer == "u":
                    updated_test = copy.deepcopy(test_item)
                    updated_test["Expected"] = interaction_record['ResponseMessage']
                    updated_test["Tree"] = str(interaction_record["Tree"])
                    test_iterator.update_test(updated_test["ID"], updated_test)
                    return True

                elif answer == "d":
                    updated_test = copy.deepcopy(test_item)
                    updated_test["Enabled"] = False
                    test_iterator.update_test(updated_test["ID"], updated_test)
                    return True

                elif answer == "b":
                    return False

                else:
                    print(f"'{answer}' is not a valid option")

        return True

    def append_test(self, test_name, interaction_records):
        test_path_and_file = self.full_test_path(test_name + ".tst")
        with open(test_path_and_file, "r") as file:
            test = json.loads(file.read())
            self._add_to_test(test, interaction_records)
        with open(self.full_test_path(test_name + ".tst"), "w") as file:
            file.write(json.dumps(test, indent=4))

    def create_test(self, reset, test_name, interaction_records):
        # Remember the name of the module and function
        # that created the state for the test
        reset_module = module_name(reset)
        reset_function = reset.__name__

        test_name_parts = os.path.split(test_name)
        full_path = self.full_test_path(test_name_parts[0])
        if not os.path.exists(full_path):
            os.mkdir(full_path)

        test = {"ResetModule": reset_module,
                "ResetFunction": reset_function,
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
                chosen_tree_index = interaction_record["ChosenTreeIndex"]
                tree_record = interaction_record["Mrss"][chosen_mrs_index]["Trees"][chosen_tree_index]
                test_items.append({"Command": interaction_record["UserInput"],
                                   "Expected": tree_record["ResponseMessage"],
                                   "Tree": str(tree_record["Tree"]),
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

    def session_data(self, key):
        return self.session_data.get(key, None)
