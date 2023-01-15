
# Just a simple iterator that must return
# a new test item each time it is asked
import copy
import json
import os
import uuid
from perplexity.utilities import module_name


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

    def full_test_path(self, test_name):
        return os.path.join(self.test_root_folder, test_name)

    def run_tests(self, test_iterator, ui):
        print("\n**** Begin Testing...\n")
        for test_item in test_iterator:
            print(f"\nTest: {test_item['Command']}")
            ui.interact_once(test_item["Command"])
            if not self.check_result(test_iterator, test_item, ui.interaction_record):
                print("**** Cancel test run")
                break
        print("\n**** Testing Complete.\n")

    def check_result(self, test_iterator, test_item, interaction_record):
        if test_item["Expected"] != interaction_record["ChosenResponse"]:
            print(f"\nExpected: {test_item['Expected']}")

            while True:
                answer = input(f"(<enter>)ignore, (b)reak to end testing, (u)pdate test, (d)isable test\n")
                if answer == "":
                    return True

                elif answer == "u":
                    updated_test = copy.deepcopy(test_item)
                    updated_test["Expected"] = interaction_record['ChosenResponse']
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
            for record in interaction_records:
                test_items.append({"Command": record["UserInput"],
                                   "Expected": record["ChosenResponse"],
                                   "Tree": None if (record["ChosenTreeIndex"] == -1 or record["ChosenTreeIndex"] is None) else str(record["Mrss"][record["ChosenMrsIndex"]]["Trees"][record["ChosenTreeIndex"]]["Tree"]),
                                   "Enabled": True,
                                   "ID": str(uuid.uuid4())
                                   })
