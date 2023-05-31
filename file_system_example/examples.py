from file_system_example.messages import error_priority, generate_message
from file_system_example.objects import Folder, File, Actor, FileSystemMock
from file_system_example.state import State, FileSystemState
from file_system_example.vocabulary import vocabulary
from perplexity.execution import ExecutionContext, call, execution_context
from perplexity.generation import english_for_delphin_variable
from perplexity.messages import respond_to_mrs_tree
from perplexity.plurals import all_plural_groups_stream, VariableCriteria, GlobalCriteria
from perplexity.tree import TreePredication
from perplexity.user_interface import UserInterface
from perplexity.utilities import ShowLogging


def solve_and_respond(state, mrs):
    context = ExecutionContext(vocabulary)
    solutions = list(context.solve_mrs_tree(state, mrs))
    return respond_to_mrs_tree(mrs, solutions, context.error())


def call_predication(*args, **kwargs):
    # default to proposition for early documentation
    yield from execution_context()._call_predication(*args, **kwargs)


##########################



# List folders using call_predication
def Example2():
    state = State([Folder(name="Desktop"),
                   Folder(name="Documents"),
                   File(name="file1.txt"),
                   File(name="file2.txt")])

    for item in call_predication(state,
                                 TreePredication(0, "_folder_n_of", ["x1", "i1"])
                                 ):
        print(item.variables)


# "Large files" using a conjunction
def Example3():
    state = State([Folder(name="Desktop"),
                   Folder(name="Documents"),
                   File(name="file1.txt", size=100),
                   File(name="file2.txt", size=2000000)])
    
    tree = [TreePredication(0, "_large_a_1", ["e1", "x1"]),
            TreePredication(1, "_file_n_of", ["x1", "i1"])]
    
    for item in call(state, tree):
        print(item.variables)


# "a" large file in a world with two large files
def Example4():
    # Note that both files are "large" now
    state = State([Folder(name="Desktop"),
                   Folder(name="Documents"),
                   File(name="file1.txt", size=2000000),
                   File(name="file2.txt", size=2000000)])

    tree = TreePredication(0, "_a_q", ["x3",
                                       TreePredication(1, "_file_n_of", ["x3", "i1"]),
                                       TreePredication(2, "_large_a_1", ["e2", "x3"])])

    for item in call(state, tree):
        print(item.variables)


# Evaluate the proposition: "a file is large" when there is one
def Example5():
    state = State([Folder(name="Desktop"),
                   Folder(name="Documents"),
                   File(name="file1.txt", size=2000000),
                   File(name="file2.txt", size=2000000)])
    
    # Start with an empty dictionary
    tree_info = {}

    # Set its "index" key to the value "e1"
    tree_info["Index"] = "e1"

    # Set its "Variables" key to *another* dictionary with
    # two keys: "x1" and "e1". Each of those has a "value" of
    # yet another dictionary that holds the properties of the variables
    tree_info["Variables"] = {"x1": {"NUM": "pl"},
                              "e1": {"SF": "prop"}}

    # Set the "Tree" key to the scope-resolved MRS tree, using our format
    tree_info["Tree"] = TreePredication(0, "_a_q", ["x1",
                                                    TreePredication(1, "_file_n_of", ["x1", "i1"]),
                                                    TreePredication(2, "_large_a_1", ["e1", "x1"])])

    print(solve_and_respond(state, tree_info))


# Evaluate the proposition: "a file is large" when there isn't a large one
def Example5_1():
    state = State([Folder(name="Desktop"),
                   Folder(name="Documents"),
                   File(name="file1.txt", size=200),
                   File(name="file2.txt", size=200)])
    # Start with an empty dictionary
    tree_info = {}

    # Set its "index" key to the value "e1"
    tree_info["Index"] = "e1"

    # Set its "Variables" key to *another* dictionary with
    # two keys: "x1" and "e1". Each of those has a "value" of
    # yet another dictionary that holds the properties of the variables
    tree_info["Variables"] = {"x1": {"NUM": "pl"},
                        "e1": {"SF": "prop"}}

    # Set the "Tree" key to the scope-resolved MRS tree, using our format
    tree_info["Tree"] = TreePredication(0, "_a_q", ["x1",
                                                    TreePredication(1, "_file_n_of", ["x1", "i1"]),
                                                    TreePredication(2, "_large_a_1", ["e1", "x1"])])

    print(solve_and_respond(state, tree_info))


# Evaluate the proposition: "a file is large" when there isn't any files
def Example5_2():
    state = State([Folder(name="Desktop"),
                   Folder(name="Documents")])
    # Start with an empty dictionary
    tree_info = {}
    # Set its "index" key to the value "e1"
    tree_info["Index"] = "e1"
    # Set its "Variables" key to *another* dictionary with
    # two keys: "x1" and "e1". Each of those has a "value" of
    # yet another dictionary that holds the properties of the variables
    tree_info["Variables"] = {"x1": {"NUM": "pl"},
                        "e1": {"SF": "prop"}}
    # Set the "Tree" key to the scope-resolved MRS tree, using our format
    tree_info["Tree"] = TreePredication(0, "_a_q", ["x1",
                                                    TreePredication(1, "_file_n_of", ["x1", "i1"]),
                                                    TreePredication(2, "_large_a_1", ["e1", "x1"])])

    print(solve_and_respond(state, tree_info))


# Evaluate the proposition: "which file is large?"
def Example6():
    state = State([Folder(name="Desktop"),
                   Folder(name="Documents"),
                   File(name="file1.txt", size=2000000),
                   File(name="file2.txt", size=1000000)])

    tree_info = {}
    tree_info["Index"] = "e1"
    tree_info["Variables"] = {"x1": {"NUM": "sg"},
                        "e1": {"SF": "ques"}}
    tree_info["Tree"] = TreePredication(0, "_which_q", ["x1",
                                                        TreePredication(1, "_file_n_of", ["x1", "i1"]),
                                                        TreePredication(2, "_large_a_1", ["e1", "x1"])])

    print(solve_and_respond(state, tree_info))


# Evaluate the proposition: "which file is very small?"
def Example6a():
    state = State([Folder(name="Desktop"),
                   Folder(name="Documents"),
                   File(name="file1.txt", size=20000000),
                   File(name="file2.txt", size=1000000)])

    tree_info = {}
    tree_info["Index"] = "e1"
    tree_info["Variables"] = {"x1": {"NUM": "sg"},
                        "e1": {"SF": "ques"}}
    tree_info["Tree"] = TreePredication(0, "_which_q", ["x1",
                                                        TreePredication(1, "_file_n_of", ["x1", "i1"]),
                                                        [TreePredication(2, "_very_x_deg", ["e2", "e1"]),
                                                         TreePredication(3, "_small_a_1", ["e1", "x1"])]])

    print(solve_and_respond(state, tree_info))


# Evaluate the proposition: "which file is very large?"
def Example6b():
    state = State([Folder(name="Desktop"),
                   Folder(name="Documents"),
                   File(name="file1.txt", size=20000000),
                   File(name="file2.txt", size=1000000)])

    tree_info = {}
    tree_info["Index"] = "e1"
    tree_info["Variables"] = {"x1": {"NUM": "sg"},
                        "e1": {"SF": "ques"}}
    tree_info["Tree"] = TreePredication(0, "_which_q", ["x1",
                                                        TreePredication(1, "_file_n_of", ["x1", "i1"]),
                                                        [TreePredication(2, "_very_x_deg", ["e2", "e1"]),
                                                         TreePredication(3, "_large_a_1", ["e1", "x1"])]])

    print(solve_and_respond(state, tree_info))


# Delete a large file when there are some
def Example7():
    state = State([Actor(name="Computer", person=2),
                   Folder(name="Desktop"),
                   Folder(name="Documents"),
                   File(name="file1.txt", size=2000000),
                   File(name="file2.txt", size=1000000)])
    tree_info = {}
    tree_info["Index"] = "e2"
    tree_info["Variables"] = {"x3": {"PERS": 2},
                              "e2": {"SF": "comm"}}
    tree_info["Tree"] = TreePredication(0, "pronoun_q", ["x3",
                                                         TreePredication(1, "pron", ["x3"]),
                                                         TreePredication(2, "_a_q", ["x8",
                                                                                     [TreePredication(3, "_large_a_1", ["e1", "x1"]),
                                                                                      TreePredication(4, "_file_n_of", ["x1", "i1"])],
                                                                                      TreePredication(5, "_delete_v_1", ["e2", "x3", "x1"])])])

    print(solve_and_respond(state, tree_info))


# delete you
def Example8():
    state = State([Actor(name="Computer", person=2),
                   Folder(name="Desktop"),
                   Folder(name="Documents"),
                   File(name="file1.txt", size=2000000),
                   File(name="file2.txt", size=1000000)])

    tree_info = {}
    tree_info["Index"] = "e2"
    tree_info["Variables"] = {"x3": {"PERS": 2},
                              "x8": {"PERS": 2},
                              "e2": {"SF": "comm"}}
    tree_info["Tree"] = TreePredication(0, "pronoun_q", ["x3",
                                                         TreePredication(1, "pron", ["x3"]),
                                                         TreePredication(2, "pronoun_q", ["x8",
                                                                                          TreePredication(3, "pron", ["x8"]),
                                                                                          TreePredication(4, "_delete_v_1",["e2", "x3", "x8"])])])

    print(solve_and_respond(state, tree_info))


# Delete a large file when there are no large files
def Example9():
    state = State([Actor(name="Computer", person=2),
                   Folder(name="Desktop"),
                   Folder(name="Documents"),
                   File(name="file1.txt", size=10),
                   File(name="file2.txt", size=10)])

    tree_info = {}
    tree_info["Index"] = "e2"
    tree_info["Variables"] = {"x3": {"PERS": 2},
                              "e2": {"SF": "comm"}}
    tree_info["Tree"] = TreePredication(0, "pronoun_q", ["x3",
                                                         TreePredication(1, "pron", ["x3"]),
                                                         TreePredication(2, "_a_q", ["x1",
                                                                                     [TreePredication(3, "_large_a_1", ["e1", "x1"]),
                                                                                      TreePredication(4, "_file_n_of", ["x1", "i1"])],
                                                                                     TreePredication(5, "_delete_v_1", ["e2", "x3", "x1"])])])

    print(solve_and_respond(state, tree_info))


# Evaluate the proposition: "a file is large" when there are no *large* files
def Example10():
    state = State([Folder(name="Desktop"),
                   Folder(name="Documents"),
                   File(name="file1.txt", size=1000000),
                   File(name="file2.txt", size=1000000)])
    tree_info = {}
    tree_info["Index"] = "e1"
    tree_info["Variables"] = {"x1": {"NUM": "pl"},
                        "e1": {"SF": "prop"}}

    tree_info["Tree"] = TreePredication(0, "_a_q", ["x1",
                                                    TreePredication(1, "_file_n_of", ["x1", "i1"]),
                                                    TreePredication(2, "_large_a_1", ["e1", "x1"])])

    print(solve_and_respond(state, tree_info))


# Evaluate the proposition: "a file is large" when there are no files, period
def Example11():
    state = State([Folder(name="Desktop"),
                   Folder(name="Documents")])
    tree_info = {}
    tree_info["Index"] = "e1"
    tree_info["Variables"] = {"x1": {"NUM": "pl"},
                        "e1": {"SF": "prop"}}
    tree_info["Tree"] = TreePredication(0, "_a_q", ["x1",
                                                    TreePredication(1, "_file_n_of", ["x1", "i1"]),
                                                    TreePredication(2, "_large_a_1", ["e1", "x1"])])

    print(solve_and_respond(state, tree_info))


def Example12():
    tree_info = {}
    tree_info["Tree"] = TreePredication(0, "_a_q", ["x1",
                                                    TreePredication(1, "_file_n_of", ["x1", "i1"]),
                                                    TreePredication(2, "_large_a_1", ["e1", "x1"])])

    print(english_for_delphin_variable(0, "x1", tree_info))
    print(english_for_delphin_variable(1, "x1", tree_info))
    print(english_for_delphin_variable(2, "x1", tree_info))
    
    
# "he/she" deletes a large file
def Example13():
    state = State([Actor(name="Computer", person=2),
                   Folder(name="Desktop"),
                   Folder(name="Documents"),
                   File(name="file1.txt", size=2000000),
                   File(name="file2.txt", size=1000000)])
    tree_info = {}
    tree_info["Index"] = "e2"
    tree_info["Variables"] = {"x3": {"PERS": 3},
                              "e2": {"SF": "prop"}}

    tree_info["Tree"] = TreePredication(0, "pronoun_q", ["x3",
                                                         TreePredication(1, "pron", ["x3"]),
                                                         TreePredication(2, "_a_q", ["x1",
                                                                                     [TreePredication(3, "_large_a_1", ["e1", "x1"]),
                                                                                      TreePredication(4, "_file_n_of", ["x1", "i1"])],
                                                                                     TreePredication(5, "_delete_v_1", ["e2", "x3", "x1"])])])

    print(solve_and_respond(state, tree_info))

    
# Evaluate the proposition: "which file is large?" if there are no files
def Example14():
    state = State([Folder(name="Desktop"),
                   Folder(name="Documents")])
    tree_info = {}
    tree_info["Index"] = "e1"
    tree_info["Variables"] = {"x1": {"NUM": "sg"},
                              "e1": {"SF": "ques"}}
    tree_info["Tree"] = TreePredication(0, "_which_q", ["x1",
                                                        TreePredication(1, "_file_n_of", ["x1", "i1"]),
                                                        TreePredication(2, "_large_a_1", ["e1", "x1"])])

    print(solve_and_respond(state, tree_info))


# "A file is large" when there isn't a file in the system
def Example15():
    state = State([Folder(name="Desktop"),
                   Folder(name="Documents")])
    tree_info = {}
    tree_info["Index"] = "e1"
    tree_info["Variables"] = {"x1": {"NUM": "pl"},
                        "e1": {"SF": "prop"}}
    tree_info["Tree"] = TreePredication(0, "_a_q", ["x1",
                                                    TreePredication(1, "_file_n_of", ["x1", "i1"]),
                                                    TreePredication(2, "_large_a_1", ["e1", "x1"])])

    print(solve_and_respond(state, tree_info))


def Example16_reset():
    return State([Actor(name="Computer", person=2),
                  Folder(name="Desktop"),
                  Folder(name="Documents"),
                  File(name="file1.txt", size=2000000)])


def Example16():
    # ShowLogging("Pipeline")
    user_interface = UserInterface(Example16_reset, vocabulary, generate_message, respond_to_mrs_tree)

    while True:
        user_interface.interact_once()
        print()


def Example17():
    def reset():
        return State([Folder(name="Desktop"),
                      Folder(name="Documents")])

    user_interface = UserInterface(reset, vocabulary, generate_message, None)

    for mrs in user_interface.mrss_from_phrase("every book is in a cave"):
        for tree in user_interface.trees_from_mrs(mrs):
            print(tree)


def Example18_reset():
    return State([Actor(name="Computer", person=2),
                  Folder(name="Desktop"),
                  Folder(name="Documents"),
                  File(name="file1.txt", size=1000000)
                  ])


def Example18a_reset():
    return State([Actor(name="Computer", person=2),
                  Folder(name="Desktop"),
                  Folder(name="Documents"),
                  File(name="file1.txt", size=20000000),
                  File(name="file2.txt", size=1000000)])


def Example18():
    # ShowLogging("Pipeline")
    user_interface = UserInterface(Example18_reset, vocabulary, generate_message, error_priority, respond_to_mrs_tree)

    while True:
        user_interface.interact_once()
        print()


def Example19_reset():
    return FileSystemState(FileSystemMock([(True, "/documents/file1.txt", {"size": 1000000}),
                                           (False, "/Desktop", {})],
                                          "/documents"))


def Example19():
    # ShowLogging("Pipeline")
    user_interface = UserInterface(Example19_reset, vocabulary, generate_message, error_priority, respond_to_mrs_tree)

    while True:
        user_interface.interact_once()
        print()


def Example20_reset():
    return FileSystemState(FileSystemMock([(True, "/documents/file1.txt", {"size": 1000}),
                                           (False, "/Desktop", {})],
                                          "/Desktop"))


def Example20():
    user_interface = UserInterface(Example20_reset, vocabulary, generate_message, error_priority, respond_to_mrs_tree)

    while True:
        user_interface.interact_once()
        print()


def Example21_reset():
    return FileSystemState(FileSystemMock([(True, "/documents/file1.txt", {"size": 1000}),
                                           (False, "/Desktop", {}),
                                           (True, "/Desktop/file2.txt", {"size": 10000000}),
                                           (True, "/Desktop/file3.txt", {"size": 1000})],
                                          "/Desktop"))


def Example21():
    user_interface = UserInterface(Example21_reset, vocabulary, generate_message, error_priority, respond_to_mrs_tree)

    while True:
        user_interface.interact_once()
        print()


def Example22_reset():
    return FileSystemState(FileSystemMock([(True, "/documents/file1.txt", {"size": 1000}),
                                           (False, "/Desktop", {"size": 10000000}),
                                           (True, "/Desktop/file2.txt", {"size": 10000000}),
                                           (True, "/Desktop/file3.txt", {"size": 1000})],
                                          "/Desktop"))


def Example22():
    user_interface = UserInterface(Example22_reset, vocabulary, generate_message, error_priority, respond_to_mrs_tree)

    while True:
        user_interface.interact_once()
        print()


def Example23_reset():
    return FileSystemState(FileSystemMock([
                                           (True, "/documents/file1.txt", {"size": 1000}),
                                           (False, "/Desktop", {"size": 10000000}),
                                           (True, "/Desktop/the yearly budget.txt", {"size": 10000000}),
                                           (True, "/Desktop/blue", {"size": 1000})],
                                          "/Desktop"))


def Example23():
    user_interface = UserInterface(Example23_reset, vocabulary, generate_message, error_priority, respond_to_mrs_tree)

    while True:
        user_interface.interact_once()
        print()


def Example24_reset():
    return FileSystemState(FileSystemMock([(True, "/temp/59.txt", {"size": 1000}),
                                           (True, "/documents/file1.txt", {"size": 1000}),
                                           (False, "/Desktop", {"size": 10000000}),
                                           (True, "/Desktop/the yearly budget.txt", {"size": 10000000}),
                                           (True, "/Desktop/blue", {"size": 1000})],
                                          "/Desktop"))


def Example24():
    user_interface = UserInterface(Example24_reset, vocabulary, generate_message, error_priority, respond_to_mrs_tree)

    while True:
        user_interface.interact_once()
        print()


def Example25_reset():
    return FileSystemState(FileSystemMock([(True, "/temp/59.txt", {"size": 1000}),
                                           (True, "/documents/file1.txt", {"size": 1000}),
                                           (False, "/Desktop", {"size": 10000000}),
                                           (True, "/Desktop/the yearly budget.txt", {"size": 10000000}),
                                           (True, "/Desktop/blue", {"size": 10000000})],
                                          "/Desktop"))


def Example25():
    user_interface = UserInterface(Example25_reset, vocabulary, generate_message, error_priority, respond_to_mrs_tree)

    while True:
        user_interface.interact_once()
        print()


def Example26_reset():
    return FileSystemState(FileSystemMock([(True, "/temp/59.txt", {"size": 1000}),
                                           (True, "/documents/file1.txt", {"size": 1000}),
                                           (False, "/Desktop", {"size": 10000000}),
                                           (True, "/Desktop/the yearly budget.txt", {"size": 10000000}),
                                           (True, "/Desktop/bigfile.txt", {"size": 20000000}),
                                           (True, "/Desktop/bigfile2.txt", {"size": 20000000}),
                                           (True, "/Desktop/blue", {"size": 10000000})],
                                          "/Desktop"))


def Example26():
    user_interface = UserInterface(Example26_reset, vocabulary, generate_message, error_priority, respond_to_mrs_tree)

    while True:
        user_interface.interact_once()
        print()


def Example27_reset():
    return FileSystemState(FileSystemMock([(True, "/temp/59.txt", {"size": 1000}),
                                           (True, "/documents/file1.txt", {"size": 1000}),
                                           (False, "/Desktop", {"size": 10000000}),
                                           (True, "/Desktop/the yearly budget.txt", {"size": 10000000}),
                                           (True, "/Desktop/bigfile.txt", {"size": 20000000}),
                                           (True, "/Desktop/bigfile2.txt", {"size": 20000000}),
                                           (True, "/Desktop/bigfile3.txt", {"size": 20000000}),
                                           (True, "/Desktop/blue", {"size": 10000000}),
                                           (True, "/Desktop/green", {"size": 10000000})],
                                           "/Desktop"))


def Example27():
    user_interface = UserInterface(Example27_reset, vocabulary, generate_message, error_priority, respond_to_mrs_tree)

    while True:
        user_interface.interact_once()
        print()


def Example28_reset():
    return FileSystemState(FileSystemMock([(True, "/temp/59.txt", {"size": 1000}),
                                           (True, "/documents/file1.txt", {"size": 1000}),
                                           (False, "/Desktop", {"size": 10000000}),
                                           (True, "/Desktop/the yearly budget.txt", {"size": 10000000}),
                                           (True, "/Desktop/bigfile.txt", {"size": 20000000}),
                                           (True, "/Desktop/bigfile2.txt", {"size": 20000000}),
                                           (True, "/Desktop/bigfile3.txt", {"size": 20000000}),
                                           (True, "/Desktop/blue", {"size": 10000000})],
                                          "/Desktop"))


def Example28():
    user_interface = UserInterface(Example28_reset, vocabulary, generate_message, error_priority, respond_to_mrs_tree)

    while True:
        user_interface.interact_once()
        print()


def Example29_reset():
    return FileSystemState(FileSystemMock([(True, "/Desktop/file2.txt", {"size": 10000000}),
                                           (True, "/Desktop/file3.txt", {"size": 10000000})],
                                          "/Desktop"))


def Example29():
    user_interface = UserInterface(Example29_reset, vocabulary, generate_message, error_priority, respond_to_mrs_tree)

    while True:
        user_interface.interact_once()
        print()


def Example30_reset():
    return FileSystemState(FileSystemMock([(True, "/Desktop/file2.txt", {"size": 10000000}),
                                           (True, "/Desktop/file3.txt", {"size": 10000000}),
                                           (True, "/documents/file4.txt", {"size": 10000000}),
                                           (True, "/documents/file5.txt", {"size": 10000000})],
                                           "/Desktop"))


def Example30():
    user_interface = UserInterface(Example30_reset, vocabulary, generate_message, error_priority, respond_to_mrs_tree)

    while True:
        user_interface.interact_once()
        print()


def Example31_reset():
    return FileSystemState(FileSystemMock([(True, "/Desktop/file4.txt", {"size": 10000000, "link": 1}),
                                           (True, "/Desktop/file5.txt", {"size": 10000000, "link": 2}),
                                           (True, "/documents/file4.txt", {"size": 10000000, "link": 1}),
                                           (True, "/documents/file5.txt", {"size": 10000000, "link": 2})],
                                           "/Desktop"))


def Example31():
    user_interface = UserInterface(Example31_reset, vocabulary, generate_message, error_priority, respond_to_mrs_tree)

    while True:
        user_interface.interact_once()
        print()


def Example32_reset():
    return FileSystemState(FileSystemMock([(True, "/Desktop/file2.txt", {"size": 10000000}),
                                           (True, "/documents/file5.txt", {"size": 10000000})],
                                           "/Desktop"))


def Example32():
    user_interface = UserInterface(Example32_reset, vocabulary, generate_message, error_priority, respond_to_mrs_tree)

    while True:
        user_interface.interact_once()
        print()


def Example33_reset():
    file_list = [(True, f"/documents/file{str(index)}.txt", {"size": 10000000}) for index in range(100)]
    return FileSystemState(FileSystemMock(file_list,
                                           "/documents"))


def Example33():
    user_interface = UserInterface(Example33_reset, vocabulary, generate_message, error_priority, respond_to_mrs_tree)

    while True:
        user_interface.interact_once()
        print()


def Example33_performance_test():
    user_interface = UserInterface(Example33_reset, vocabulary, generate_message, error_priority, respond_to_mrs_tree)
    user_interface.interact_once(force_input="which files are large?")


def Example34_reset():
    return FileSystemState(FileSystemMock([(True, "/Desktop/file1.txt", {"size": 10000000}),
                                           (True, "/Desktop/file2.txt", {"size": 10000000}),
                                           (True, "/documents/file3.txt", {"size": 10000000}),
                                           (True, "/documents/file4.txt", {"size": 10000000})
                                           ],
                                           "/Desktop"))


def Example34():
    user_interface = UserInterface(Example34_reset, vocabulary, generate_message, error_priority, respond_to_mrs_tree)

    while True:
        user_interface.interact_once()
        print()


def Example35_reset():
    return FileSystemState(FileSystemMock([(True, "/Desktop/file4.txt", {"size": 10000000, "link": 1}),
                                           (True, "/foo/file4.txt", {"size": 10000000, "link": 1}),
                                           (True, "/bar/file5.txt", {"size": 10000000, "link": 2}),
                                           (True, "/go/file5.txt", {"size": 10000000, "link": 2})],
                                           "/Desktop"))


def Example35():
    user_interface = UserInterface(Example35_reset, vocabulary, generate_message, error_priority, respond_to_mrs_tree)

    while True:
        user_interface.interact_once()
        print()


def Example36_reset():
    return FileSystemState(FileSystemMock([(True, "/Desktop/file2.txt", {"size": 10000000}),
                                           (True, "/Desktop/file3.txt", {"size": 10000}),
                                           (True, "/documents/file4.txt", {"size": 10000000}),
                                           (True, "/documents/file5.txt", {"size": 10000})],
                                           "/Desktop"))


def Example36():
    user_interface = UserInterface(Example36_reset, vocabulary, generate_message, error_priority, respond_to_mrs_tree)

    while True:
        user_interface.interact_once()
        print()



def Example37_reset():
    return FileSystemState(FileSystemMock([(True, "/Desktop/file2.txt", {"size": 10000000})
                                           ],
                                           "/Desktop"))


def Example37():
    user_interface = UserInterface(Example37_reset, vocabulary, generate_message, error_priority, respond_to_mrs_tree)

    while True:
        user_interface.interact_once()
        print()

def build_solutions(spec):
    solutions = []
    for item in spec:
        state = State([])
        for var_item in item.items():
            state = state.set_x(var_item[0], var_item[1], False)
        solutions.append(state)

    return solutions


def execution_context_for_num_variables(var_nums, variable_execution_data):
    tree_info = {"Variables": {}}
    for lst in var_nums:
        tree_info["Variables"][lst[0]] = {"NUM": lst[1]}
    return ExecutionContextMock(tree_info, variable_execution_data)


class ExecutionContextMock(object):
    def __init__(self, tree_info, variable_execution_data):
        self.tree_info = tree_info
        self.variable_execution_data = variable_execution_data

    def get_variable_execution_data(self, variable_name):
        return self.variable_execution_data[variable_name]


def state_test():
    # # 1 collective
    # solutions = build_solutions([{"x1": ("a",), "x2": ("a",)}
    #                              ])
    # var_criteria = [VariableCriteria("x1", 1)]
    # for foo in all_nonempty_subsets_var_all_stream(solutions, var_criteria):
    #     print(str(foo) + "\n")
    # print("=============")
    #
    # # 1 collective
    # solutions = build_solutions([{"x1": ("a",), "x2": ("a",)},
    #                              {"x1": ("b",), "x2": ("c",)},
    #                              ])
    # var_criteria = [VariableCriteria("x1", 1)]
    # for foo in all_nonempty_subsets_var_all_stream(solutions, var_criteria):
    #     print(str(foo) + "\n")
    # print("=============")

    # # 2 students eat 2 pizzas only distributive
    # solutions = build_solutions([{"x1": ("a",), "x2": ("w", "x")},
    #                              {"x1": ("b",), "x2": ("y", "z")},
    #                              ])
    # var_criteria = [VariableCriteria("x1", 2, 2), VariableCriteria("x2", 2, 2)]
    # for foo in all_nonempty_subsets_var_all_stream(solutions, var_criteria):
    #     for solution in foo:
    #         print(solution)
    #     print()
    # print("=============")

    # # 2 students eat 2 pizzas only collective
    # solutions = build_solutions([{"x1": ("a", "b"), "x2": ("w", "x")}
    #                              ])
    # var_criteria = [VariableCriteria("x1", 2, 2), VariableCriteria("x2", 2, 2)]
    # for foo in all_nonempty_subsets_var_all_stream(solutions, var_criteria):
    #     for solution in foo:
    #         print(solution)
    #     print()
    # print("=============")

    # # 2 students eat 2 pizzas only cumulative
    # solutions = build_solutions([{"x1": ("a", ), "x2": ("w",)},
    #                              {"x1": ("b", ), "x2": ("x",)}
    #                              ])
    # var_criteria = [VariableCriteria("x1", 2, 2), VariableCriteria("x2", 2, 2)]
    # for foo in all_plural_groups_stream(solutions, var_criteria):
    #     for solution in foo:
    #         print(solution)
    #     print()
    # print("=============")

    # # Exactly 1 that has multiple (so fails)
    # solutions = build_solutions([{"x1": ("a", ), "x2": ("w",)},
    #                              {"x1": ("b",), "x2": ("w",)}
    #                              ])
    # var_criteria = [VariableCriteria("x1", 1, 1, GlobalCriteria.exactly)]
    # for foo in all_plural_groups_stream(None, solutions, var_criteria):
    #     for solution in foo:
    #         print(solution)
    #     print()
    # print("=============")

    # # Plural where all succeed
    # solutions = build_solutions([{"x1": ("a", ), "x2": ("w",)},
    #                              {"x1": ("b",), "x2": ("w",)}
    #                              ])
    # var_criteria = [VariableCriteria("x1", 1, 1, GlobalCriteria.all_rstr_meet_criteria)]
    # for foo in all_plural_groups_stream(execution_context_for_num_variables([("x1", "pl")], {"x1": {"AllRstrValues": ["a", "b"]}}), solutions, var_criteria):
    #     for solution in foo:
    #         print(solution)
    #     print()
    # print("=============")

    # Plural where not all succeed
    solutions = build_solutions([{"x1": ("a", ), "x2": ("w",)},
                                 {"x1": ("b",), "x2": ("w",)}
                                 ])
    var_criteria = [VariableCriteria("x1", 1, 1, GlobalCriteria.all_rstr_meet_criteria)]
    for foo in all_plural_groups_stream(execution_context_for_num_variables([("x1", "pl")], {"x1": {"AllRstrValues": ["a", "b", "c"]}}), solutions, var_criteria):
        for solution in foo:
            print(solution)
        print()
    print("=============")

    # # Singular where plural objects
    # solutions = build_solutions([{"x1": ("a", ), "x2": ("w",)},
    #                              {"x1": ("b",), "x2": ("w",)}
    #                              ])
    # var_criteria = [VariableCriteria("x1", 1, 1, GlobalCriteria.all_rstr_meet_criteria)]
    # for foo in all_plural_groups_stream(execution_context_for_num_variables([("x1", "sg")], {"x1": {"AllRstrValues": ["a", "b"]}}), solutions, var_criteria):
    #     for solution in foo:
    #         print(solution)
    #     print()
    # print("=============")


    # # Singular where single objects
    # solutions = build_solutions([{"x1": ("a", ), "x2": ("w",)}
    #                              ])
    # var_criteria = [VariableCriteria("x1", 1, 1, GlobalCriteria.all_rstr_meet_criteria)]
    # for foo in all_plural_groups_stream(execution_context_for_num_variables([("x1", "sg")], {"x1": {"AllRstrValues": ["a"]}}), solutions, var_criteria):
    #     for solution in foo:
    #         print(solution)
    #     print()
    # print("=============")

    # files are in folders (each file in the same folder)
    # Issue: (by design) returns the smallest combinations first
    # specs = []
    # for i in range(1000):
    #     specs.append({"x1": ("file" + str(i),), "x2": ("folder",)})
    # solutions = build_solutions(specs)
    # var_criteria = [VariableCriteria("x1", 1), VariableCriteria("x2", 1)]
    # for foo in all_nonempty_subsets_var_all_stream(solutions, var_criteria):
    #     print(str(foo) + "\n")
    # print("=============")


if __name__ == '__main__':
    # ShowLogging("Execution")
    # ShowLogging("Generation")
    # ShowLogging("UserInterface")
    # ShowLogging("Pipeline")/Users/ericzinda/Enlistments/Perplexity/venv/bin/python /Users/ericzinda/Enlistments/Perplexity/file_system_example/examples.py
    # ? /runfolder
    #
    # **** Begin Testing...
    #
    #
    # Test: /new examples.Example24_reset
    # State reset using examples.Example24_reset().
    #
    # Test: files are large
    # SString 2023-05-31 13:41:06,296: sstring: tree is: udef_q:0(x3,_file_n_of:1(x3,i8),_large_a_1:2(e2,x3))
    # SString 2023-05-31 13:41:06,297: sstring: original text is: '*arg2'
    # SString 2023-05-31 13:41:06,297: sstring: plural is: PluralMode.as_is
    # SString 2023-05-31 13:41:06,323: sstring: tree is: udef_q:0(x3,_file_n_of:1(x3,i8),_large_a_1:2(e2,x3))
    # SString 2023-05-31 13:41:06,323: sstring: original text is: 'bare arg1:sg@error_predicate_index'
    # SString 2023-05-31 13:41:06,323: sstring: plural is: PluralMode.singular
    # SString 2023-05-31 13:41:06,324: sstring: variable_name is '['AfterFullPhrase', 'x3']'
    # SString 2023-05-31 13:41:06,324: sstring: variable is complex: '['AfterFullPhrase', 'x3']'
    # SString 2023-05-31 13:41:06,324: sstring: default meaning_at_index is '2'
    # SString 2023-05-31 13:41:06,324: sstring: meaning_at_index specified by complex variable: 100000000
    # SString 2023-05-31 13:41:06,324: sstring: non-default meaning_at_index: only use fallback
    # SString 2023-05-31 13:41:06,324: sstring: MRS failed, try fallback
    # SString 2023-05-31 13:41:06,324: sstring: Fallback generated: x3[ delphin(arg1):PluralMode.singular@error_predicate_index]=large file
    # There are less than 2 large file
    #
    # Test: which files are large
    # SString 2023-05-31 13:41:06,552: sstring: tree is: _which_q:0(x3,_file_n_of:1(x3,i8),_large_a_1:2(e2,x3))
    # SString 2023-05-31 13:41:06,552: sstring: original text is: '*arg2'
    # SString 2023-05-31 13:41:06,552: sstring: plural is: PluralMode.as_is
    # SString 2023-05-31 13:41:06,554: sstring: tree is: _which_q:0(x3,_file_n_of:1(x3,i8),_large_a_1:2(e2,x3))
    # SString 2023-05-31 13:41:06,554: sstring: original text is: 'bare arg1:sg@error_predicate_index'
    # SString 2023-05-31 13:41:06,554: sstring: plural is: PluralMode.singular
    # SString 2023-05-31 13:41:06,555: sstring: variable_name is '['AfterFullPhrase', 'x3']'
    # SString 2023-05-31 13:41:06,555: sstring: variable is complex: '['AfterFullPhrase', 'x3']'
    # SString 2023-05-31 13:41:06,555: sstring: default meaning_at_index is '2'
    # SString 2023-05-31 13:41:06,555: sstring: meaning_at_index specified by complex variable: 100000000
    # SString 2023-05-31 13:41:06,555: sstring: non-default meaning_at_index: only use fallback
    # SString 2023-05-31 13:41:06,555: sstring: MRS failed, try fallback
    # SString 2023-05-31 13:41:06,555: sstring: Fallback generated: x3[ delphin(arg1):PluralMode.singular@error_predicate_index]=large file
    # There are less than 2 large file
    #
    # Test: /new examples.Example25_reset
    # State reset using examples.Example25_reset().
    #
    # Test: files are large
    # Yes, that is true.
    #
    # Test: which files are large
    # (File(name=/Desktop/the yearly budget.txt, size=10000000),)
    # (File(name=/Desktop/blue, size=10000000),)
    #
    # Test: /new examples.Example25_reset
    # State reset using examples.Example25_reset().
    #
    # Test: a file is large
    # Yes, that is true.
    # (there are more)
    #
    # Test: /new examples.Example20_reset
    # State reset using examples.Example20_reset().
    #
    # Test: a file is large
    # SString 2023-05-31 13:41:07,237: sstring: tree is: _a_q:0(x3,_file_n_of:1(x3,i8),_large_a_1:2(e2,x3))
    # SString 2023-05-31 13:41:07,237: sstring: original text is: 'A arg2'
    # SString 2023-05-31 13:41:07,237: sstring: plural is: PluralMode.as_is
    # SString 2023-05-31 13:41:07,238: sstring: variable_name is 'x3'
    # SString 2023-05-31 13:41:07,238: sstring: default meaning_at_index is '2'
    # SString 2023-05-31 13:41:07,238: sstring: meaning_at_index not specified, using default: '2'
    # SString 2023-05-31 13:41:07,238: sstring: default meaning_at_index: trying MRS generation
    # SString 2023-05-31 13:41:07,540: sstring MRS generated: x3[CAP+A delphin(arg2):PluralMode.as_is]=a file
    # SString 2023-05-31 13:41:07,541: sstring: tree is: _a_q:0(x3,_file_n_of:1(x3,i8),_large_a_1:2(e2,x3))
    # SString 2023-05-31 13:41:07,541: sstring: original text is: ''is':<arg2'
    # SString 2023-05-31 13:41:07,542: sstring: plural is: PluralMode.singular
    # SString 2023-05-31 13:41:07,542: sstring: tree is: _a_q:0(x3,_file_n_of:1(x3,i8),_large_a_1:2(e2,x3))
    # SString 2023-05-31 13:41:07,542: sstring: original text is: '*arg1'
    # SString 2023-05-31 13:41:07,542: sstring: plural is: PluralMode.as_is
    # a file is not large
    #
    # Test: /new examples.Example25_reset
    # State reset using examples.Example25_reset().
    #
    # Test: 1 file is large
    # Yes, that is true.
    # (there are more)
    #
    # Test: 2 files are large
    # Yes, that is true.
    #
    # Test: which 2 files are large
    # (File(name=/Desktop/the yearly budget.txt, size=10000000),)
    # (File(name=/Desktop/blue, size=10000000),)
    #
    # Test: 3 files are large
    # SString 2023-05-31 13:41:08,543: sstring: tree is: udef_q:0(x3,[_file_n_of:1(x3,i10), card:2(3,e9,x3)],_large_a_1:3(e2,x3))
    # SString 2023-05-31 13:41:08,543: sstring: original text is: '*arg2'
    # SString 2023-05-31 13:41:08,543: sstring: plural is: PluralMode.as_is
    # SString 2023-05-31 13:41:08,545: sstring: tree is: udef_q:0(x3,[_file_n_of:1(x3,i10), card:2(3,e9,x3)],_large_a_1:3(e2,x3))
    # SString 2023-05-31 13:41:08,545: sstring: original text is: 'bare arg1:sg@error_predicate_index'
    # SString 2023-05-31 13:41:08,545: sstring: plural is: PluralMode.singular
    # SString 2023-05-31 13:41:08,546: sstring: variable_name is '['AfterFullPhrase', 'x3']'
    # SString 2023-05-31 13:41:08,546: sstring: variable is complex: '['AfterFullPhrase', 'x3']'
    # SString 2023-05-31 13:41:08,546: sstring: default meaning_at_index is '2'
    # SString 2023-05-31 13:41:08,546: sstring: meaning_at_index specified by complex variable: 100000000
    # SString 2023-05-31 13:41:08,546: sstring: non-default meaning_at_index: only use fallback
    # SString 2023-05-31 13:41:08,546: sstring: MRS failed, try fallback
    # SString 2023-05-31 13:41:08,546: sstring: Fallback generated: x3[ delphin(arg1):PluralMode.singular@error_predicate_index]=3 large file
    # There are less than 3 3 large file
    #
    # Test: /new examples.Example25_reset
    # State reset using examples.Example25_reset().
    #
    # Test: 2 files are 20 mb
    # Yes, that is true.
    #
    # Test: 1 file is 20 megabytes
    # SString 2023-05-31 13:41:09,229: sstring: tree is: udef_q:0(x11,[_megabyte_n_1:1(x11,u18), card:2(20,e17,x11)],udef_q:3(x3,[_file_n_of:4(x3,i10), card:5(1,e9,x3)],loc_nonsp:6(e2,x3,x11)))
    # SString 2023-05-31 13:41:09,229: sstring: original text is: ''is':<arg1'
    # SString 2023-05-31 13:41:09,230: sstring: variable is complex: '['AfterFullPhrase', 'x3']'
    # SString 2023-05-31 13:41:09,230: sstring: plural is: PluralMode.singular
    # SString 2023-05-31 13:41:09,231: sstring: tree is: udef_q:0(x11,[_megabyte_n_1:1(x11,u18), card:2(20,e17,x11)],udef_q:3(x3,[_file_n_of:4(x3,i10), card:5(1,e9,x3)],loc_nonsp:6(e2,x3,x11)))
    # SString 2023-05-31 13:41:09,231: sstring: original text is: 'arg1:@error_predicate_index'
    # SString 2023-05-31 13:41:09,232: sstring: plural is: PluralMode.as_is
    # SString 2023-05-31 13:41:09,232: sstring: variable_name is '['AfterFullPhrase', 'x3']'
    # SString 2023-05-31 13:41:09,232: sstring: variable is complex: '['AfterFullPhrase', 'x3']'
    # SString 2023-05-31 13:41:09,232: sstring: default meaning_at_index is '5'
    # SString 2023-05-31 13:41:09,232: sstring: meaning_at_index specified by complex variable: 100000000
    # SString 2023-05-31 13:41:09,233: sstring: non-default meaning_at_index: only use fallback
    # SString 2023-05-31 13:41:09,233: sstring: MRS failed, try fallback
    # SString 2023-05-31 13:41:09,233: sstring: Fallback generated: x3[None delphin(arg1):PluralMode.as_is@error_predicate_index]=1 file that is 20 megabyte
    # SString 2023-05-31 13:41:09,258: sstring: tree is: udef_q:0(x3,[_file_n_of:1(x3,i10), card:2(1,e9,x3)],udef_q:3(x11,[_megabyte_n_1:4(x11,u18), card:5(20,e17,x11)],loc_nonsp:6(e2,x3,x11)))
    # SString 2023-05-31 13:41:09,258: sstring: original text is: ''is':<arg1'
    # SString 2023-05-31 13:41:09,259: sstring: variable is complex: '['AfterFullPhrase', 'x3']'
    # SString 2023-05-31 13:41:09,259: sstring: plural is: PluralMode.singular
    # SString 2023-05-31 13:41:09,260: sstring: tree is: udef_q:0(x3,[_file_n_of:1(x3,i10), card:2(1,e9,x3)],udef_q:3(x11,[_megabyte_n_1:4(x11,u18), card:5(20,e17,x11)],loc_nonsp:6(e2,x3,x11)))
    # SString 2023-05-31 13:41:09,260: sstring: original text is: 'arg1:@error_predicate_index'
    # SString 2023-05-31 13:41:09,260: sstring: plural is: PluralMode.as_is
    # SString 2023-05-31 13:41:09,261: sstring: variable_name is '['AfterFullPhrase', 'x3']'
    # SString 2023-05-31 13:41:09,261: sstring: variable is complex: '['AfterFullPhrase', 'x3']'
    # SString 2023-05-31 13:41:09,261: sstring: default meaning_at_index is '2'
    # SString 2023-05-31 13:41:09,261: sstring: meaning_at_index specified by complex variable: 100000000
    # SString 2023-05-31 13:41:09,261: sstring: non-default meaning_at_index: only use fallback
    # SString 2023-05-31 13:41:09,261: sstring: MRS failed, try fallback
    # SString 2023-05-31 13:41:09,261: sstring: Fallback generated: x3[None delphin(arg1):PluralMode.as_is@error_predicate_index]=1 file that is 20 megabyte
    # There is more than 1 file that is 20 megabyte
    #
    # Test: /new examples.Example26_reset
    # State reset using examples.Example26_reset().
    #
    # Test: which files are 20 mb?
    # (File(name=/Desktop/bigfile.txt, size=20000000),)
    # (File(name=/Desktop/bigfile2.txt, size=20000000),)
    # (File(name=/Desktop/the yearly budget.txt, size=10000000), File(name=/Desktop/blue, size=10000000))
    #
    # Test: together, which files are 20 mb
    # (File(name=/Desktop/the yearly budget.txt, size=10000000), File(name=/Desktop/blue, size=10000000))
    # (File(name=/Desktop/bigfile.txt, size=20000000),)
    # (File(name=/Desktop/bigfile2.txt, size=20000000),)
    #
    # Test: which files together are 20 mb
    # (File(name=/Desktop/the yearly budget.txt, size=10000000), File(name=/Desktop/blue, size=10000000))
    #
    # Test: /new examples.Example25_reset
    # State reset using examples.Example25_reset().
    #
    # Test: a few files are large
    # SString 2023-05-31 13:41:10,578: sstring: tree is: udef_q:0(x3,[_file_n_of:1(x3,i9), _a+few_a_1:2(e8,x3)],_large_a_1:3(e2,x3))
    # SString 2023-05-31 13:41:10,578: sstring: original text is: '*arg2'
    # SString 2023-05-31 13:41:10,578: sstring: plural is: PluralMode.as_is
    # SString 2023-05-31 13:41:10,580: sstring: tree is: udef_q:0(x3,[_file_n_of:1(x3,i9), _a+few_a_1:2(e8,x3)],_large_a_1:3(e2,x3))
    # SString 2023-05-31 13:41:10,580: sstring: original text is: 'bare arg1:sg@error_predicate_index'
    # SString 2023-05-31 13:41:10,580: sstring: plural is: PluralMode.singular
    # SString 2023-05-31 13:41:10,581: sstring: variable_name is '['AfterFullPhrase', 'x3']'
    # SString 2023-05-31 13:41:10,581: sstring: variable is complex: '['AfterFullPhrase', 'x3']'
    # SString 2023-05-31 13:41:10,581: sstring: default meaning_at_index is '2'
    # SString 2023-05-31 13:41:10,581: sstring: meaning_at_index specified by complex variable: 100000000
    # SString 2023-05-31 13:41:10,581: sstring: non-default meaning_at_index: only use fallback
    # SString 2023-05-31 13:41:10,581: sstring: MRS failed, try fallback
    # SString 2023-05-31 13:41:10,581: sstring: Fallback generated: x3[ delphin(arg1):PluralMode.singular@error_predicate_index]=a few large file
    # There are less than 3 a few large file
    #
    # Test: /new examples.Example26_reset
    # State reset using examples.Example26_reset().
    #
    # Test: a few files are large
    # Yes, that is true.
    # (there are more)
    #
    # Test: /new examples.Example27_reset
    # State reset using examples.Example27_reset().
    #
    # Test: a few files are large
    # Yes, that is true.
    # (there are more)
    #
    # Test: /new examples.Example25_reset
    # State reset using examples.Example25_reset().
    #
    # Test: the files are large
    # SString 2023-05-31 13:41:11,199: sstring: tree is: _the_q:0(x3,_file_n_of:1(x3,i8),_large_a_1:2(e2,x3))
    # SString 2023-05-31 13:41:11,199: sstring: original text is: 'arg1:@error_predicate_index'
    # SString 2023-05-31 13:41:11,199: sstring: plural is: PluralMode.as_is
    # SString 2023-05-31 13:41:11,200: sstring: variable_name is '['AtPredication', _large_a_1(e2,x3), 'x3']'
    # SString 2023-05-31 13:41:11,200: sstring: variable is complex: '['AtPredication', _large_a_1(e2,x3), 'x3']'
    # SString 2023-05-31 13:41:11,200: sstring: error predication index is: 2
    # SString 2023-05-31 13:41:11,200: sstring: default meaning_at_index is '2'
    # SString 2023-05-31 13:41:11,200: sstring: meaning_at_index specified by complex variable: 2
    # SString 2023-05-31 13:41:11,200: sstring: default meaning_at_index: trying MRS generation
    # SString 2023-05-31 13:41:11,356: sstring MRS generated: x3[None delphin(arg1):PluralMode.as_is@error_predicate_index]=the files
    # That isn't true for all the files
    #
    # Test: the large files are large
    # Yes, that is true.
    #
    # Test: the 2 large files are large
    # Yes, that is true.
    #
    # Test: the 3 files are large
    # SString 2023-05-31 13:41:12,050: sstring: tree is: _the_q:0(x3,[_file_n_of:1(x3,i10), card:2(3,e9,x3)],_large_a_1:3(e2,x3))
    # SString 2023-05-31 13:41:12,050: sstring: original text is: ''is':<arg1'
    # SString 2023-05-31 13:41:12,051: sstring: variable is complex: '['AtPredication', _large_a_1(e2,x3), 'x3']'
    # SString 2023-05-31 13:41:12,051: sstring: error predication index is: 3
    # SString 2023-05-31 13:41:12,051: sstring: plural is: PluralMode.plural
    # SString 2023-05-31 13:41:12,053: sstring: tree is: _the_q:0(x3,[_file_n_of:1(x3,i10), card:2(3,e9,x3)],_large_a_1:3(e2,x3))
    # SString 2023-05-31 13:41:12,053: sstring: original text is: 'arg1:@error_predicate_index'
    # SString 2023-05-31 13:41:12,053: sstring: plural is: PluralMode.as_is
    # SString 2023-05-31 13:41:12,054: sstring: variable_name is '['AtPredication', _large_a_1(e2,x3), 'x3']'
    # SString 2023-05-31 13:41:12,054: sstring: variable is complex: '['AtPredication', _large_a_1(e2,x3), 'x3']'
    # SString 2023-05-31 13:41:12,054: sstring: error predication index is: 3
    # SString 2023-05-31 13:41:12,054: sstring: default meaning_at_index is '2'
    # SString 2023-05-31 13:41:12,054: sstring: meaning_at_index specified by complex variable: 3
    # SString 2023-05-31 13:41:12,054: sstring: non-default meaning_at_index: only use fallback
    # SString 2023-05-31 13:41:12,054: sstring: MRS failed, try fallback
    # SString 2023-05-31 13:41:12,054: sstring: Fallback generated: x3[None delphin(arg1):PluralMode.as_is@error_predicate_index]=the 3 file
    # There are more than the 3 file
    #
    # Test: the file is large
    # SString 2023-05-31 13:41:12,243: sstring: tree is: _the_q:0(x3,_file_n_of:1(x3,i8),_large_a_1:2(e2,x3))
    # SString 2023-05-31 13:41:12,243: sstring: original text is: ''is':<*arg2'
    # SString 2023-05-31 13:41:12,244: sstring: plural template is: 1
    # SString 2023-05-31 13:41:12,244: sstring: plural is: PluralMode.singular
    # SString 2023-05-31 13:41:12,245: sstring: tree is: _the_q:0(x3,_file_n_of:1(x3,i8),_large_a_1:2(e2,x3))
    # SString 2023-05-31 13:41:12,245: sstring: original text is: '*arg2'
    # SString 2023-05-31 13:41:12,245: sstring: plural is: PluralMode.as_is
    # SString 2023-05-31 13:41:12,246: sstring: tree is: _the_q:0(x3,_file_n_of:1(x3,i8),_large_a_1:2(e2,x3))
    # SString 2023-05-31 13:41:12,247: sstring: original text is: 'bare arg1:@error_predicate_index'
    # SString 2023-05-31 13:41:12,247: sstring: plural is: PluralMode.as_is
    # SString 2023-05-31 13:41:12,247: sstring: variable_name is '['AtPredication', _large_a_1(e2,x3), 'x3']'
    # SString 2023-05-31 13:41:12,247: sstring: variable is complex: '['AtPredication', _large_a_1(e2,x3), 'x3']'
    # SString 2023-05-31 13:41:12,247: sstring: error predication index is: 2
    # SString 2023-05-31 13:41:12,248: sstring: default meaning_at_index is '2'
    # SString 2023-05-31 13:41:12,248: sstring: meaning_at_index specified by complex variable: 2
    # SString 2023-05-31 13:41:12,248: sstring: default meaning_at_index: trying MRS generation
    # SString 2023-05-31 13:41:12,438: sstring MRS generated: x3[ delphin(arg1):PluralMode.as_is@error_predicate_index]=file
    # There is more than 1 file
    #
    # Test: /new examples.Example28_reset
    # State reset using examples.Example28_reset().
    #
    # Test: a few files are 20 mb
    # Yes, that is true.
    # (there are more)
    #
    # Test: a few files are 30 mb
    # Yes, that is true.
    # (there are more)
    #
    # Test: /new examples.Example25_reset
    # State reset using examples.Example25_reset().
    #
    # Test: which files are in folders
    # (File(name=/temp/59.txt, size=1000),)
    # (File(name=/documents/file1.txt, size=1000),)
    # (File(name=/Desktop/the yearly budget.txt, size=10000000),)
    # (File(name=/Desktop/blue, size=10000000),)
    #
    # Test: which files are in a folder?
    # (File(name=/Desktop/the yearly budget.txt, size=10000000),)
    # (File(name=/Desktop/blue, size=10000000),)
    #
    # Test: /new examples.Example26_reset
    # State reset using examples.Example26_reset().
    #
    # Test: which 2 files are in a folder?
    # (File(name=/Desktop/the yearly budget.txt, size=10000000),)
    # (File(name=/Desktop/bigfile.txt, size=20000000),)
    # (there are more)
    #
    # Test: /new examples.Example26_reset
    # State reset using examples.Example26_reset().
    #
    # Test: which 2 files in a folder are 20 mb
    # (File(name=/Desktop/bigfile.txt, size=20000000),)
    # (File(name=/Desktop/bigfile2.txt, size=20000000),)
    # (there are more)
    #
    # Test: which 2 files in a folder together are 20 mb
    # (File(name=/Desktop/the yearly budget.txt, size=10000000), File(name=/Desktop/blue, size=10000000))
    #
    # Test: /new examples.Example25_reset
    # State reset using examples.Example25_reset().
    #
    # Test: the 2 files in a folder are 20 mb
    # SString 2023-05-31 13:41:15,830: sstring: tree is: _a_q:0(x12,_folder_n_of:1(x12,i17),udef_q:2(x18,[_megabyte_n_1:3(x18,u25), card:4(20,e24,x18)],_the_q:5(x3,[_file_n_of:6(x3,i10), _in_p_loc:7(e11,x3,x12), card:8(2,e9,x3)],loc_nonsp:9(e2,x3,x18))))
    # SString 2023-05-31 13:41:15,830: sstring: original text is: ''is':<arg1'
    # SString 2023-05-31 13:41:15,831: sstring: variable is complex: '['AtPredication', loc_nonsp(e2,x3,x18), 'x3']'
    # SString 2023-05-31 13:41:15,831: sstring: error predication index is: 9
    # SString 2023-05-31 13:41:15,831: sstring: plural is: PluralMode.plural
    # SString 2023-05-31 13:41:15,833: sstring: tree is: _a_q:0(x12,_folder_n_of:1(x12,i17),udef_q:2(x18,[_megabyte_n_1:3(x18,u25), card:4(20,e24,x18)],_the_q:5(x3,[_file_n_of:6(x3,i10), _in_p_loc:7(e11,x3,x12), card:8(2,e9,x3)],loc_nonsp:9(e2,x3,x18))))
    # SString 2023-05-31 13:41:15,833: sstring: original text is: 'arg1:@error_predicate_index'
    # SString 2023-05-31 13:41:15,833: sstring: plural is: PluralMode.as_is
    # SString 2023-05-31 13:41:15,834: sstring: variable_name is '['AtPredication', loc_nonsp(e2,x3,x18), 'x3']'
    # SString 2023-05-31 13:41:15,834: sstring: variable is complex: '['AtPredication', loc_nonsp(e2,x3,x18), 'x3']'
    # SString 2023-05-31 13:41:15,834: sstring: error predication index is: 9
    # SString 2023-05-31 13:41:15,834: sstring: default meaning_at_index is '7'
    # SString 2023-05-31 13:41:15,834: sstring: meaning_at_index specified by complex variable: 9
    # SString 2023-05-31 13:41:15,834: sstring: non-default meaning_at_index: only use fallback
    # SString 2023-05-31 13:41:15,834: sstring: MRS failed, try fallback
    # SString 2023-05-31 13:41:15,834: sstring: Fallback generated: x3[None delphin(arg1):PluralMode.as_is@error_predicate_index]=the 2 file in a folder
    # SString 2023-05-31 13:41:15,981: sstring: tree is: _a_q:0(x12,_folder_n_of:1(x12,i17),_the_q:2(x3,[_file_n_of:3(x3,i10), _in_p_loc:4(e11,x3,x12), card:5(2,e9,x3)],udef_q:6(x18,[_megabyte_n_1:7(x18,u25), card:8(20,e24,x18)],loc_nonsp:9(e2,x3,x18))))
    # SString 2023-05-31 13:41:15,981: sstring: original text is: ''is':<arg1'
    # SString 2023-05-31 13:41:15,982: sstring: variable is complex: '['AtPredication', udef_q(x18,[_megabyte_n_1(x18,u25), card(20,e24,x18)],loc_nonsp(e2,x3,x18)), 'x3']'
    # SString 2023-05-31 13:41:15,982: sstring: error predication index is: 6
    # SString 2023-05-31 13:41:15,982: sstring: plural is: PluralMode.plural
    # SString 2023-05-31 13:41:15,984: sstring: tree is: _a_q:0(x12,_folder_n_of:1(x12,i17),_the_q:2(x3,[_file_n_of:3(x3,i10), _in_p_loc:4(e11,x3,x12), card:5(2,e9,x3)],udef_q:6(x18,[_megabyte_n_1:7(x18,u25), card:8(20,e24,x18)],loc_nonsp:9(e2,x3,x18))))
    # SString 2023-05-31 13:41:15,984: sstring: original text is: 'arg1:@error_predicate_index'
    # SString 2023-05-31 13:41:15,984: sstring: plural is: PluralMode.as_is
    # SString 2023-05-31 13:41:15,985: sstring: variable_name is '['AtPredication', udef_q(x18,[_megabyte_n_1(x18,u25), card(20,e24,x18)],loc_nonsp(e2,x3,x18)), 'x3']'
    # SString 2023-05-31 13:41:15,985: sstring: variable is complex: '['AtPredication', udef_q(x18,[_megabyte_n_1(x18,u25), card(20,e24,x18)],loc_nonsp(e2,x3,x18)), 'x3']'
    # SString 2023-05-31 13:41:15,985: sstring: error predication index is: 6
    # SString 2023-05-31 13:41:15,985: sstring: default meaning_at_index is '4'
    # SString 2023-05-31 13:41:15,985: sstring: meaning_at_index specified by complex variable: 6
    # SString 2023-05-31 13:41:15,985: sstring: non-default meaning_at_index: only use fallback
    # SString 2023-05-31 13:41:15,985: sstring: MRS failed, try fallback
    # SString 2023-05-31 13:41:15,985: sstring: Fallback generated: x3[None delphin(arg1):PluralMode.as_is@error_predicate_index]=the 2 file in a folder
    # SString 2023-05-31 13:41:16,088: sstring: tree is: udef_q:0(x18,[_megabyte_n_1:1(x18,u25), card:2(20,e24,x18)],_a_q:3(x12,_folder_n_of:4(x12,i17),_the_q:5(x3,[_file_n_of:6(x3,i10), _in_p_loc:7(e11,x3,x12), card:8(2,e9,x3)],loc_nonsp:9(e2,x3,x18))))
    # SString 2023-05-31 13:41:16,089: sstring: original text is: ''is':<arg1'
    # SString 2023-05-31 13:41:16,089: sstring: variable is complex: '['AtPredication', loc_nonsp(e2,x3,x18), 'x3']'
    # SString 2023-05-31 13:41:16,089: sstring: error predication index is: 9
    # SString 2023-05-31 13:41:16,089: sstring: plural is: PluralMode.plural
    # SString 2023-05-31 13:41:16,091: sstring: tree is: udef_q:0(x18,[_megabyte_n_1:1(x18,u25), card:2(20,e24,x18)],_a_q:3(x12,_folder_n_of:4(x12,i17),_the_q:5(x3,[_file_n_of:6(x3,i10), _in_p_loc:7(e11,x3,x12), card:8(2,e9,x3)],loc_nonsp:9(e2,x3,x18))))
    # SString 2023-05-31 13:41:16,091: sstring: original text is: 'arg1:@error_predicate_index'
    # SString 2023-05-31 13:41:16,091: sstring: plural is: PluralMode.as_is
    # SString 2023-05-31 13:41:16,092: sstring: variable_name is '['AtPredication', loc_nonsp(e2,x3,x18), 'x3']'
    # SString 2023-05-31 13:41:16,092: sstring: variable is complex: '['AtPredication', loc_nonsp(e2,x3,x18), 'x3']'
    # SString 2023-05-31 13:41:16,092: sstring: error predication index is: 9
    # SString 2023-05-31 13:41:16,092: sstring: default meaning_at_index is '7'
    # SString 2023-05-31 13:41:16,092: sstring: meaning_at_index specified by complex variable: 9
    # SString 2023-05-31 13:41:16,092: sstring: non-default meaning_at_index: only use fallback
    # SString 2023-05-31 13:41:16,092: sstring: MRS failed, try fallback
    # SString 2023-05-31 13:41:16,092: sstring: Fallback generated: x3[None delphin(arg1):PluralMode.as_is@error_predicate_index]=the 2 file in a folder
    # SString 2023-05-31 13:41:16,191: sstring: tree is: udef_q:0(x18,[_megabyte_n_1:1(x18,u25), card:2(20,e24,x18)],_the_q:3(x3,_a_q:4(x12,_folder_n_of:5(x12,i17),[_file_n_of:6(x3,i10), _in_p_loc:7(e11,x3,x12), card:8(2,e9,x3)]),loc_nonsp:9(e2,x3,x18)))
    # SString 2023-05-31 13:41:16,191: sstring: original text is: ''is':<arg1'
    # SString 2023-05-31 13:41:16,192: sstring: variable is complex: '['AtPredication', loc_nonsp(e2,x3,x18), 'x3']'
    # SString 2023-05-31 13:41:16,192: sstring: error predication index is: 9
    # SString 2023-05-31 13:41:16,192: sstring: plural is: PluralMode.plural
    # SString 2023-05-31 13:41:16,194: sstring: tree is: udef_q:0(x18,[_megabyte_n_1:1(x18,u25), card:2(20,e24,x18)],_the_q:3(x3,_a_q:4(x12,_folder_n_of:5(x12,i17),[_file_n_of:6(x3,i10), _in_p_loc:7(e11,x3,x12), card:8(2,e9,x3)]),loc_nonsp:9(e2,x3,x18)))
    # SString 2023-05-31 13:41:16,194: sstring: original text is: 'arg1:@error_predicate_index'
    # SString 2023-05-31 13:41:16,194: sstring: plural is: PluralMode.as_is
    # SString 2023-05-31 13:41:16,195: sstring: variable_name is '['AtPredication', loc_nonsp(e2,x3,x18), 'x3']'
    # SString 2023-05-31 13:41:16,195: sstring: variable is complex: '['AtPredication', loc_nonsp(e2,x3,x18), 'x3']'
    # SString 2023-05-31 13:41:16,195: sstring: error predication index is: 9
    # SString 2023-05-31 13:41:16,195: sstring: default meaning_at_index is '7'
    # SString 2023-05-31 13:41:16,195: sstring: meaning_at_index specified by complex variable: 9
    # SString 2023-05-31 13:41:16,195: sstring: non-default meaning_at_index: only use fallback
    # SString 2023-05-31 13:41:16,195: sstring: MRS failed, try fallback
    # SString 2023-05-31 13:41:16,195: sstring: Fallback generated: x3[None delphin(arg1):PluralMode.as_is@error_predicate_index]=the 2 file in a folder
    # SString 2023-05-31 13:41:16,327: sstring: tree is: _the_q:0(x3,_a_q:1(x12,_folder_n_of:2(x12,i17),[_file_n_of:3(x3,i10), _in_p_loc:4(e11,x3,x12), card:5(2,e9,x3)]),udef_q:6(x18,[_megabyte_n_1:7(x18,u25), card:8(20,e24,x18)],loc_nonsp:9(e2,x3,x18)))
    # SString 2023-05-31 13:41:16,327: sstring: original text is: ''is':<arg1'
    # SString 2023-05-31 13:41:16,328: sstring: variable is complex: '['AtPredication', udef_q(x18,[_megabyte_n_1(x18,u25), card(20,e24,x18)],loc_nonsp(e2,x3,x18)), 'x3']'
    # SString 2023-05-31 13:41:16,328: sstring: error predication index is: 6
    # SString 2023-05-31 13:41:16,328: sstring: plural is: PluralMode.plural
    # SString 2023-05-31 13:41:16,330: sstring: tree is: _the_q:0(x3,_a_q:1(x12,_folder_n_of:2(x12,i17),[_file_n_of:3(x3,i10), _in_p_loc:4(e11,x3,x12), card:5(2,e9,x3)]),udef_q:6(x18,[_megabyte_n_1:7(x18,u25), card:8(20,e24,x18)],loc_nonsp:9(e2,x3,x18)))
    # SString 2023-05-31 13:41:16,330: sstring: original text is: 'arg1:@error_predicate_index'
    # SString 2023-05-31 13:41:16,330: sstring: plural is: PluralMode.as_is
    # SString 2023-05-31 13:41:16,330: sstring: variable_name is '['AtPredication', udef_q(x18,[_megabyte_n_1(x18,u25), card(20,e24,x18)],loc_nonsp(e2,x3,x18)), 'x3']'
    # SString 2023-05-31 13:41:16,331: sstring: variable is complex: '['AtPredication', udef_q(x18,[_megabyte_n_1(x18,u25), card(20,e24,x18)],loc_nonsp(e2,x3,x18)), 'x3']'
    # SString 2023-05-31 13:41:16,331: sstring: error predication index is: 6
    # SString 2023-05-31 13:41:16,331: sstring: default meaning_at_index is '4'
    # SString 2023-05-31 13:41:16,331: sstring: meaning_at_index specified by complex variable: 6
    # SString 2023-05-31 13:41:16,331: sstring: non-default meaning_at_index: only use fallback
    # SString 2023-05-31 13:41:16,331: sstring: MRS failed, try fallback
    # SString 2023-05-31 13:41:16,331: sstring: Fallback generated: x3[None delphin(arg1):PluralMode.as_is@error_predicate_index]=the 2 file in a folder
    # There are more than the 2 file in a folder
    #
    # Test: /new examples.Example31_reset
    # State reset using examples.Example31_reset().
    #
    # Test: which files are in 2 folders?
    # (File(name=/Desktop/file4.txt, size=10000000),)
    # (File(name=/Desktop/file5.txt, size=10000000),)
    # (there are more)
    #
    # Test: 1 file is in a folder together
    # SString 2023-05-31 13:41:16,937: sstring: tree is: _a_q:0(x11,[_folder_n_of:1(x11,i16), _together_p:2(e17,x11)],udef_q:3(x3,[_file_n_of:4(x3,i10), card:5(1,e9,x3)],_in_p_loc:6(e2,x3,x11)))
    # SString 2023-05-31 13:41:16,937: sstring: original text is: ''is':<arg1'
    # SString 2023-05-31 13:41:16,938: sstring: variable is complex: '['AfterFullPhrase', 'x11']'
    # SString 2023-05-31 13:41:16,938: sstring: plural is: PluralMode.singular
    # SString 2023-05-31 13:41:16,940: sstring: tree is: _a_q:0(x11,[_folder_n_of:1(x11,i16), _together_p:2(e17,x11)],udef_q:3(x3,[_file_n_of:4(x3,i10), card:5(1,e9,x3)],_in_p_loc:6(e2,x3,x11)))
    # SString 2023-05-31 13:41:16,940: sstring: original text is: 'arg1:@error_predicate_index'
    # SString 2023-05-31 13:41:16,940: sstring: plural is: PluralMode.as_is
    # SString 2023-05-31 13:41:16,940: sstring: variable_name is '['AfterFullPhrase', 'x11']'
    # SString 2023-05-31 13:41:16,941: sstring: variable is complex: '['AfterFullPhrase', 'x11']'
    # SString 2023-05-31 13:41:16,941: sstring: default meaning_at_index is '2'
    # SString 2023-05-31 13:41:16,941: sstring: meaning_at_index specified by complex variable: 100000000
    # SString 2023-05-31 13:41:16,941: sstring: non-default meaning_at_index: only use fallback
    # SString 2023-05-31 13:41:16,941: sstring: MRS failed, try fallback
    # SString 2023-05-31 13:41:16,941: sstring: Fallback generated: x11[None delphin(arg1):PluralMode.as_is@error_predicate_index]=a folder together
    # SString 2023-05-31 13:41:16,979: sstring: tree is: udef_q:0(x3,[_file_n_of:1(x3,i10), card:2(1,e9,x3)],_a_q:3(x11,[_folder_n_of:4(x11,i16), _together_p:5(e17,x11)],_in_p_loc:6(e2,x3,x11)))
    # SString 2023-05-31 13:41:16,979: sstring: original text is: ''is':<arg1'
    # SString 2023-05-31 13:41:16,980: sstring: variable is complex: '['AfterFullPhrase', 'x11']'
    # SString 2023-05-31 13:41:16,980: sstring: plural is: PluralMode.singular
    # SString 2023-05-31 13:41:16,981: sstring: tree is: udef_q:0(x3,[_file_n_of:1(x3,i10), card:2(1,e9,x3)],_a_q:3(x11,[_folder_n_of:4(x11,i16), _together_p:5(e17,x11)],_in_p_loc:6(e2,x3,x11)))
    # SString 2023-05-31 13:41:16,981: sstring: original text is: 'arg1:@error_predicate_index'
    # SString 2023-05-31 13:41:16,981: sstring: plural is: PluralMode.as_is
    # SString 2023-05-31 13:41:16,982: sstring: variable_name is '['AfterFullPhrase', 'x11']'
    # SString 2023-05-31 13:41:16,982: sstring: variable is complex: '['AfterFullPhrase', 'x11']'
    # SString 2023-05-31 13:41:16,982: sstring: default meaning_at_index is '5'
    # SString 2023-05-31 13:41:16,982: sstring: meaning_at_index specified by complex variable: 100000000
    # SString 2023-05-31 13:41:16,982: sstring: non-default meaning_at_index: only use fallback
    # SString 2023-05-31 13:41:16,982: sstring: MRS failed, try fallback
    # SString 2023-05-31 13:41:16,982: sstring: Fallback generated: x11[None delphin(arg1):PluralMode.as_is@error_predicate_index]=a folder together
    # SString 2023-05-31 13:41:16,980: sstring: tree is: _a_q:0(x11,_folder_n_of:1(x11,i16),udef_q:2(x3,[_file_n_of:3(x3,i10), card:4(1,e9,x3)],[_together_p:5(e17,x3), _in_p_loc:6(e2,x3,x11)]))
    # SString 2023-05-31 13:41:16,981: sstring: original text is: ''is':<arg1'
    # SString 2023-05-31 13:41:16,981: sstring: variable is complex: '['AfterFullPhrase', 'x3']'
    # SString 2023-05-31 13:41:16,981: sstring: plural is: PluralMode.singular
    # SString 2023-05-31 13:41:16,982: sstring: tree is: _a_q:0(x11,_folder_n_of:1(x11,i16),udef_q:2(x3,[_file_n_of:3(x3,i10), card:4(1,e9,x3)],[_together_p:5(e17,x3), _in_p_loc:6(e2,x3,x11)]))
    # SString 2023-05-31 13:41:16,983: sstring: original text is: 'arg1:@error_predicate_index'
    # SString 2023-05-31 13:41:16,983: sstring: plural is: PluralMode.as_is
    # SString 2023-05-31 13:41:16,983: sstring: variable_name is '['AfterFullPhrase', 'x3']'
    # SString 2023-05-31 13:41:16,983: sstring: variable is complex: '['AfterFullPhrase', 'x3']'
    # SString 2023-05-31 13:41:16,983: sstring: default meaning_at_index is '4'
    # SString 2023-05-31 13:41:16,983: sstring: meaning_at_index specified by complex variable: 100000000
    # SString 2023-05-31 13:41:16,984: sstring: non-default meaning_at_index: only use fallback
    # SString 2023-05-31 13:41:16,984: sstring: MRS failed, try fallback
    # SString 2023-05-31 13:41:16,984: sstring: Fallback generated: x3[None delphin(arg1):PluralMode.as_is@error_predicate_index]=1 file together in a folder
    # SString 2023-05-31 13:41:17,013: sstring: tree is: udef_q:0(x3,[_file_n_of:1(x3,i10), card:2(1,e9,x3)],_a_q:3(x11,_folder_n_of:4(x11,i16),[_together_p:5(e17,x3), _in_p_loc:6(e2,x3,x11)]))
    # SString 2023-05-31 13:41:17,013: sstring: original text is: ''is':<arg1'
    # SString 2023-05-31 13:41:17,014: sstring: variable is complex: '['AfterFullPhrase', 'x3']'
    # SString 2023-05-31 13:41:17,014: sstring: plural is: PluralMode.singular
    # SString 2023-05-31 13:41:17,015: sstring: tree is: udef_q:0(x3,[_file_n_of:1(x3,i10), card:2(1,e9,x3)],_a_q:3(x11,_folder_n_of:4(x11,i16),[_together_p:5(e17,x3), _in_p_loc:6(e2,x3,x11)]))
    # SString 2023-05-31 13:41:17,015: sstring: original text is: 'arg1:@error_predicate_index'
    # SString 2023-05-31 13:41:17,016: sstring: plural is: PluralMode.as_is
    # SString 2023-05-31 13:41:17,016: sstring: variable_name is '['AfterFullPhrase', 'x3']'
    # SString 2023-05-31 13:41:17,017: sstring: variable is complex: '['AfterFullPhrase', 'x3']'
    # SString 2023-05-31 13:41:17,017: sstring: default meaning_at_index is '2'
    # SString 2023-05-31 13:41:17,017: sstring: meaning_at_index specified by complex variable: 100000000
    # SString 2023-05-31 13:41:17,017: sstring: non-default meaning_at_index: only use fallback
    # SString 2023-05-31 13:41:17,017: sstring: MRS failed, try fallback
    # SString 2023-05-31 13:41:17,017: sstring: Fallback generated: x3[None delphin(arg1):PluralMode.as_is@error_predicate_index]=1 file together in a folder
    # There is more than a folder together
    #
    # Test: /new examples.Example26_reset
    # State reset using examples.Example26_reset().
    #
    # Test: which 2 large files are 20 mb
    # (File(name=/Desktop/bigfile.txt, size=20000000),)
    # (File(name=/Desktop/bigfile2.txt, size=20000000),)
    # (there are more)
    #
    # Test: the 4 large files are 20 mb
    # Yes, that is true.
    #
    # Test: /new examples.Example30_reset
    # State reset using examples.Example30_reset().
    #
    # Test: which 2 files are in 2 folders?
    # (File(name=/Desktop/file2.txt, size=10000000),)
    # (File(name=/documents/file4.txt, size=10000000),)
    # (there are more)
    #
    # Test: /new examples.Example31_reset
    # State reset using examples.Example31_reset().
    #
    # Test: which 2 files are in 2 folders
    # (File(name=/Desktop/file4.txt, size=10000000),)
    # (File(name=/Desktop/file5.txt, size=10000000),)
    # (there are more)
    #
    # Test: 4 files are in a folder
    # SString 2023-05-31 13:41:18,695: sstring: tree is: _a_q:0(x11,_folder_n_of:1(x11,i16),udef_q:2(x3,[_file_n_of:3(x3,i10), card:4(4,e9,x3)],_in_p_loc:5(e2,x3,x11)))
    # SString 2023-05-31 13:41:18,695: sstring: original text is: '*arg2'
    # SString 2023-05-31 13:41:18,695: sstring: plural is: PluralMode.as_is
    # SString 2023-05-31 13:41:18,697: sstring: tree is: _a_q:0(x11,_folder_n_of:1(x11,i16),udef_q:2(x3,[_file_n_of:3(x3,i10), card:4(4,e9,x3)],_in_p_loc:5(e2,x3,x11)))
    # SString 2023-05-31 13:41:18,697: sstring: original text is: 'bare arg1:sg@error_predicate_index'
    # SString 2023-05-31 13:41:18,697: sstring: plural is: PluralMode.singular
    # SString 2023-05-31 13:41:18,698: sstring: variable_name is '['AfterFullPhrase', 'x3']'
    # SString 2023-05-31 13:41:18,698: sstring: variable is complex: '['AfterFullPhrase', 'x3']'
    # SString 2023-05-31 13:41:18,698: sstring: default meaning_at_index is '4'
    # SString 2023-05-31 13:41:18,698: sstring: meaning_at_index specified by complex variable: 100000000
    # SString 2023-05-31 13:41:18,698: sstring: non-default meaning_at_index: only use fallback
    # SString 2023-05-31 13:41:18,698: sstring: MRS failed, try fallback
    # SString 2023-05-31 13:41:18,698: sstring: Fallback generated: x3[ delphin(arg1):PluralMode.singular@error_predicate_index]=4 file in a folder
    # SString 2023-05-31 13:41:18,735: sstring: tree is: udef_q:0(x3,[_file_n_of:1(x3,i10), card:2(4,e9,x3)],_a_q:3(x11,_folder_n_of:4(x11,i16),_in_p_loc:5(e2,x3,x11)))
    # SString 2023-05-31 13:41:18,735: sstring: original text is: '*arg2'
    # SString 2023-05-31 13:41:18,735: sstring: plural is: PluralMode.as_is
    # SString 2023-05-31 13:41:18,737: sstring: tree is: udef_q:0(x3,[_file_n_of:1(x3,i10), card:2(4,e9,x3)],_a_q:3(x11,_folder_n_of:4(x11,i16),_in_p_loc:5(e2,x3,x11)))
    # SString 2023-05-31 13:41:18,737: sstring: original text is: 'bare arg1:sg@error_predicate_index'
    # SString 2023-05-31 13:41:18,737: sstring: plural is: PluralMode.singular
    # SString 2023-05-31 13:41:18,738: sstring: variable_name is '['AfterFullPhrase', 'x3']'
    # SString 2023-05-31 13:41:18,738: sstring: variable is complex: '['AfterFullPhrase', 'x3']'
    # SString 2023-05-31 13:41:18,738: sstring: default meaning_at_index is '2'
    # SString 2023-05-31 13:41:18,738: sstring: meaning_at_index specified by complex variable: 100000000
    # SString 2023-05-31 13:41:18,738: sstring: non-default meaning_at_index: only use fallback
    # SString 2023-05-31 13:41:18,738: sstring: MRS failed, try fallback
    # SString 2023-05-31 13:41:18,738: sstring: Fallback generated: x3[ delphin(arg1):PluralMode.singular@error_predicate_index]=4 file in a folder
    # There are less than 4 4 file in a folder
    #
    # Test: /new examples.Example33_reset
    # State reset using examples.Example33_reset().
    #
    # Test: a few files are in a folder together
    # SString 2023-05-31 13:41:19,286: sstring: tree is: _a_q:0(x10,[_folder_n_of:1(x10,i15), _together_p:2(e16,x10)],udef_q:3(x3,[_file_n_of:4(x3,i9), _a+few_a_1:5(e8,x3)],_in_p_loc:6(e2,x3,x10)))
    # SString 2023-05-31 13:41:19,286: sstring: original text is: 'arg1'
    # SString 2023-05-31 13:41:19,286: sstring: plural is: PluralMode.as_is
    # SString 2023-05-31 13:41:19,287: sstring: variable_name is 'x3'
    # SString 2023-05-31 13:41:19,287: sstring: default meaning_at_index is '5'
    # SString 2023-05-31 13:41:19,287: sstring: meaning_at_index not specified, using default: '5'
    # SString 2023-05-31 13:41:19,287: sstring: default meaning_at_index: trying MRS generation
    # SString 2023-05-31 13:41:19,528: Nothing could be generated for: a few files are in a folder together: [ TOP: h0 INDEX: e2 [ e SF: prop ] RELS: < [ _a_q<19:20> LBL: h11 ARG0: x10 [ x PERS: 3 NUM: sg IND: + ] RSTR: h12 BODY: h13 ] [ _folder_n_of<21:27> LBL: h14 ARG0: x10 ARG1: i15 ] [ _together_p<28:36> LBL: h14 ARG0: e16 [ e SF: prop TENSE: untensed MOOD: indicative PROG: - PERF: - ] ARG1: x10 ] [ _file_n_of<6:11> LBL: h7 ARG0: x3 [ x PERS: 3 NUM: pl IND: + ] ARG1: i9 ] [ _a+few_a_1<0:5> LBL: h7 ARG0: e8 [ e SF: prop TENSE: untensed MOOD: indicative PROG: - PERF: - ] ARG1: x3 ] [ udef_q<0:11> LBL: h4 ARG0: x3 RSTR: h5 BODY: h6 ] [ unknown LBL: h1 ARG: x3 ARG0: e2 ] > HCONS: < h0 qeq h1 h5 qeq h7 h12 qeq h14 > ]
    # SString 2023-05-31 13:41:19,528: sstring: MRS failed, try fallback
    # SString 2023-05-31 13:41:19,528: sstring: Fallback generated: x3[None delphin(arg1):PluralMode.as_is]=file
    # SString 2023-05-31 13:41:19,530: sstring: tree is: _a_q:0(x10,[_folder_n_of:1(x10,i15), _together_p:2(e16,x10)],udef_q:3(x3,[_file_n_of:4(x3,i9), _a+few_a_1:5(e8,x3)],_in_p_loc:6(e2,x3,x10)))
    # SString 2023-05-31 13:41:19,530: sstring: original text is: 'arg2'
    # SString 2023-05-31 13:41:19,530: sstring: plural is: PluralMode.as_is
    # SString 2023-05-31 13:41:19,531: sstring: variable_name is 'x10'
    # SString 2023-05-31 13:41:19,531: sstring: default meaning_at_index is '2'
    # SString 2023-05-31 13:41:19,532: sstring: meaning_at_index not specified, using default: '2'
    # SString 2023-05-31 13:41:19,532: sstring: default meaning_at_index: trying MRS generation
    # SString 2023-05-31 13:41:19,734: sstring MRS generated: x10[None delphin(arg2):PluralMode.as_is]=a folder together
    # SString 2023-05-31 13:41:19,946: sstring: tree is: udef_q:0(x3,[_file_n_of:1(x3,i9), _a+few_a_1:2(e8,x3)],_a_q:3(x10,[_folder_n_of:4(x10,i15), _together_p:5(e16,x10)],_in_p_loc:6(e2,x3,x10)))
    # SString 2023-05-31 13:41:19,946: sstring: original text is: 'arg1'
    # SString 2023-05-31 13:41:19,946: sstring: plural is: PluralMode.as_is
    # SString 2023-05-31 13:41:19,947: sstring: variable_name is 'x3'
    # SString 2023-05-31 13:41:19,947: sstring: default meaning_at_index is '2'
    # SString 2023-05-31 13:41:19,947: sstring: meaning_at_index not specified, using default: '2'
    # SString 2023-05-31 13:41:19,947: sstring: default meaning_at_index: trying MRS generation
    # SString 2023-05-31 13:41:20,134: sstring MRS generated: x3[None delphin(arg1):PluralMode.as_is]=a few files
    # SString 2023-05-31 13:41:20,135: sstring: tree is: udef_q:0(x3,[_file_n_of:1(x3,i9), _a+few_a_1:2(e8,x3)],_a_q:3(x10,[_folder_n_of:4(x10,i15), _together_p:5(e16,x10)],_in_p_loc:6(e2,x3,x10)))
    # SString 2023-05-31 13:41:20,135: sstring: original text is: 'arg2'
    # SString 2023-05-31 13:41:20,136: sstring: plural is: PluralMode.as_is
    # SString 2023-05-31 13:41:20,136: sstring: variable_name is 'x10'
    # SString 2023-05-31 13:41:20,137: sstring: default meaning_at_index is '5'
    # SString 2023-05-31 13:41:20,137: sstring: meaning_at_index not specified, using default: '5'
    # SString 2023-05-31 13:41:20,137: sstring: default meaning_at_index: trying MRS generation
    # SString 2023-05-31 13:41:20,300: Nothing could be generated for: a few files are in a folder together: [ TOP: h0 INDEX: e2 [ e SF: prop ] RELS: < [ udef_q<0:11> LBL: h4 ARG0: x3 [ x PERS: 3 NUM: pl IND: + ] RSTR: h5 BODY: h6 ] [ _file_n_of<6:11> LBL: h7 ARG0: x3 ARG1: i9 ] [ _a+few_a_1<0:5> LBL: h7 ARG0: e8 [ e SF: prop TENSE: untensed MOOD: indicative PROG: - PERF: - ] ARG1: x3 ] [ _folder_n_of<21:27> LBL: h14 ARG0: x10 [ x PERS: 3 NUM: sg IND: + ] ARG1: i15 ] [ _together_p<28:36> LBL: h14 ARG0: e16 [ e SF: prop TENSE: untensed MOOD: indicative PROG: - PERF: - ] ARG1: x10 ] [ _a_q<19:20> LBL: h11 ARG0: x10 RSTR: h12 BODY: h13 ] [ unknown LBL: h1 ARG: x10 ARG0: e2 ] > HCONS: < h0 qeq h1 h5 qeq h7 h12 qeq h14 > ]
    # SString 2023-05-31 13:41:20,300: sstring: MRS failed, try fallback
    # SString 2023-05-31 13:41:20,300: sstring: Fallback generated: x10[None delphin(arg2):PluralMode.as_is]=a folder
    # Yes, that is true.
    # (there are more)
    #
    # Test: 4 files are in a folder
    # Yes, that is true.
    # (there are more)
    #
    # Test: which files are in a folder?
    # (File(name=/documents/file0.txt, size=10000000),)
    # (File(name=/documents/file1.txt, size=10000000),)
    # (File(name=/documents/file2.txt, size=10000000),)
    # (File(name=/documents/file3.txt, size=10000000),)
    # (File(name=/documents/file4.txt, size=10000000),)
    # (File(name=/documents/file5.txt, size=10000000),)
    # (File(name=/documents/file6.txt, size=10000000),)
    # (File(name=/documents/file7.txt, size=10000000),)
    # (File(name=/documents/file8.txt, size=10000000),)
    # (File(name=/documents/file9.txt, size=10000000),)
    # (File(name=/documents/file10.txt, size=10000000),)
    # (File(name=/documents/file11.txt, size=10000000),)
    # (File(name=/documents/file12.txt, size=10000000),)
    # (File(name=/documents/file13.txt, size=10000000),)
    # (File(name=/documents/file14.txt, size=10000000),)
    # (File(name=/documents/file15.txt, size=10000000),)
    # (File(name=/documents/file16.txt, size=10000000),)
    # (File(name=/documents/file17.txt, size=10000000),)
    # (File(name=/documents/file18.txt, size=10000000),)
    # (File(name=/documents/file19.txt, size=10000000),)
    # (File(name=/documents/file20.txt, size=10000000),)
    # (File(name=/documents/file21.txt, size=10000000),)
    # (File(name=/documents/file22.txt, size=10000000),)
    # (File(name=/documents/file23.txt, size=10000000),)
    # (File(name=/documents/file24.txt, size=10000000),)
    # (File(name=/documents/file25.txt, size=10000000),)
    # (File(name=/documents/file26.txt, size=10000000),)
    # (File(name=/documents/file27.txt, size=10000000),)
    # (File(name=/documents/file28.txt, size=10000000),)
    # (File(name=/documents/file29.txt, size=10000000),)
    # (File(name=/documents/file30.txt, size=10000000),)
    # (File(name=/documents/file31.txt, size=10000000),)
    # (File(name=/documents/file32.txt, size=10000000),)
    # (File(name=/documents/file33.txt, size=10000000),)
    # (File(name=/documents/file34.txt, size=10000000),)
    # (File(name=/documents/file35.txt, size=10000000),)
    # (File(name=/documents/file36.txt, size=10000000),)
    # (File(name=/documents/file37.txt, size=10000000),)
    # (File(name=/documents/file38.txt, size=10000000),)
    # (File(name=/documents/file39.txt, size=10000000),)
    # (File(name=/documents/file40.txt, size=10000000),)
    # (File(name=/documents/file41.txt, size=10000000),)
    # (File(name=/documents/file42.txt, size=10000000),)
    # (File(name=/documents/file43.txt, size=10000000),)
    # (File(name=/documents/file44.txt, size=10000000),)
    # (File(name=/documents/file45.txt, size=10000000),)
    # (File(name=/documents/file46.txt, size=10000000),)
    # (File(name=/documents/file47.txt, size=10000000),)
    # (File(name=/documents/file48.txt, size=10000000),)
    # (File(name=/documents/file49.txt, size=10000000),)
    # (File(name=/documents/file50.txt, size=10000000),)
    # (File(name=/documents/file51.txt, size=10000000),)
    # (File(name=/documents/file52.txt, size=10000000),)
    # (File(name=/documents/file53.txt, size=10000000),)
    # (File(name=/documents/file54.txt, size=10000000),)
    # (File(name=/documents/file55.txt, size=10000000),)
    # (File(name=/documents/file56.txt, size=10000000),)
    # (File(name=/documents/file57.txt, size=10000000),)
    # (File(name=/documents/file58.txt, size=10000000),)
    # (File(name=/documents/file59.txt, size=10000000),)
    # (File(name=/documents/file60.txt, size=10000000),)
    # (File(name=/documents/file61.txt, size=10000000),)
    # (File(name=/documents/file62.txt, size=10000000),)
    # (File(name=/documents/file63.txt, size=10000000),)
    # (File(name=/documents/file64.txt, size=10000000),)
    # (File(name=/documents/file65.txt, size=10000000),)
    # (File(name=/documents/file66.txt, size=10000000),)
    # (File(name=/documents/file67.txt, size=10000000),)
    # (File(name=/documents/file68.txt, size=10000000),)
    # (File(name=/documents/file69.txt, size=10000000),)
    # (File(name=/documents/file70.txt, size=10000000),)
    # (File(name=/documents/file71.txt, size=10000000),)
    # (File(name=/documents/file72.txt, size=10000000),)
    # (File(name=/documents/file73.txt, size=10000000),)
    # (File(name=/documents/file74.txt, size=10000000),)
    # (File(name=/documents/file75.txt, size=10000000),)
    # (File(name=/documents/file76.txt, size=10000000),)
    # (File(name=/documents/file77.txt, size=10000000),)
    # (File(name=/documents/file78.txt, size=10000000),)
    # (File(name=/documents/file79.txt, size=10000000),)
    # (File(name=/documents/file80.txt, size=10000000),)
    # (File(name=/documents/file81.txt, size=10000000),)
    # (File(name=/documents/file82.txt, size=10000000),)
    # (File(name=/documents/file83.txt, size=10000000),)
    # (File(name=/documents/file84.txt, size=10000000),)
    # (File(name=/documents/file85.txt, size=10000000),)
    # (File(name=/documents/file86.txt, size=10000000),)
    # (File(name=/documents/file87.txt, size=10000000),)
    # (File(name=/documents/file88.txt, size=10000000),)
    # (File(name=/documents/file89.txt, size=10000000),)
    # (File(name=/documents/file90.txt, size=10000000),)
    # (File(name=/documents/file91.txt, size=10000000),)
    # (File(name=/documents/file92.txt, size=10000000),)
    # (File(name=/documents/file93.txt, size=10000000),)
    # (File(name=/documents/file94.txt, size=10000000),)
    # (File(name=/documents/file95.txt, size=10000000),)
    # (File(name=/documents/file96.txt, size=10000000),)
    # (File(name=/documents/file97.txt, size=10000000),)
    # (File(name=/documents/file98.txt, size=10000000),)
    # (File(name=/documents/file99.txt, size=10000000),)
    #
    # Test: the 2 files are in 3 folders
    # SString 2023-05-31 13:41:24,801: sstring: tree is: udef_q:0(x11,[_folder_n_of:1(x11,i18), card:2(3,e17,x11)],_the_q:3(x3,[_file_n_of:4(x3,i10), card:5(2,e9,x3)],_in_p_loc:6(e2,x3,x11)))
    # SString 2023-05-31 13:41:24,801: sstring: original text is: ''is':<*arg2'
    # SString 2023-05-31 13:41:24,802: sstring: plural template is: 2
    # SString 2023-05-31 13:41:24,802: sstring: plural is: PluralMode.plural
    # SString 2023-05-31 13:41:24,804: sstring: tree is: udef_q:0(x11,[_folder_n_of:1(x11,i18), card:2(3,e17,x11)],_the_q:3(x3,[_file_n_of:4(x3,i10), card:5(2,e9,x3)],_in_p_loc:6(e2,x3,x11)))
    # SString 2023-05-31 13:41:24,804: sstring: original text is: '*arg2'
    # SString 2023-05-31 13:41:24,804: sstring: plural is: PluralMode.as_is
    # SString 2023-05-31 13:41:24,806: sstring: tree is: udef_q:0(x11,[_folder_n_of:1(x11,i18), card:2(3,e17,x11)],_the_q:3(x3,[_file_n_of:4(x3,i10), card:5(2,e9,x3)],_in_p_loc:6(e2,x3,x11)))
    # SString 2023-05-31 13:41:24,806: sstring: original text is: 'bare arg1:@error_predicate_index'
    # SString 2023-05-31 13:41:24,806: sstring: plural is: PluralMode.as_is
    # SString 2023-05-31 13:41:24,807: sstring: variable_name is '['AtPredication', _in_p_loc(e2,x3,x11), 'x3']'
    # SString 2023-05-31 13:41:24,807: sstring: variable is complex: '['AtPredication', _in_p_loc(e2,x3,x11), 'x3']'
    # SString 2023-05-31 13:41:24,807: sstring: error predication index is: 6
    # SString 2023-05-31 13:41:24,807: sstring: default meaning_at_index is '5'
    # SString 2023-05-31 13:41:24,807: sstring: meaning_at_index specified by complex variable: 6
    # SString 2023-05-31 13:41:24,807: sstring: non-default meaning_at_index: only use fallback
    # SString 2023-05-31 13:41:24,807: sstring: MRS failed, try fallback
    # SString 2023-05-31 13:41:24,807: sstring: Fallback generated: x3[ delphin(arg1):PluralMode.as_is@error_predicate_index]=2 file
    # SString 2023-05-31 13:41:24,948: sstring: tree is: _the_q:0(x3,[_file_n_of:1(x3,i10), card:2(2,e9,x3)],udef_q:3(x11,[_folder_n_of:4(x11,i18), card:5(3,e17,x11)],_in_p_loc:6(e2,x3,x11)))
    # SString 2023-05-31 13:41:24,948: sstring: original text is: ''is':<*arg2'
    # SString 2023-05-31 13:41:24,948: sstring: plural template is: 2
    # SString 2023-05-31 13:41:24,949: sstring: plural is: PluralMode.plural
    # SString 2023-05-31 13:41:24,950: sstring: tree is: _the_q:0(x3,[_file_n_of:1(x3,i10), card:2(2,e9,x3)],udef_q:3(x11,[_folder_n_of:4(x11,i18), card:5(3,e17,x11)],_in_p_loc:6(e2,x3,x11)))
    # SString 2023-05-31 13:41:24,950: sstring: original text is: '*arg2'
    # SString 2023-05-31 13:41:24,950: sstring: plural is: PluralMode.as_is
    # SString 2023-05-31 13:41:24,952: sstring: tree is: _the_q:0(x3,[_file_n_of:1(x3,i10), card:2(2,e9,x3)],udef_q:3(x11,[_folder_n_of:4(x11,i18), card:5(3,e17,x11)],_in_p_loc:6(e2,x3,x11)))
    # SString 2023-05-31 13:41:24,952: sstring: original text is: 'bare arg1:@error_predicate_index'
    # SString 2023-05-31 13:41:24,952: sstring: plural is: PluralMode.as_is
    # SString 2023-05-31 13:41:24,953: sstring: variable_name is '['AtPredication', udef_q(x11,[_folder_n_of(x11,i18), card(3,e17,x11)],_in_p_loc(e2,x3,x11)), 'x3']'
    # SString 2023-05-31 13:41:24,953: sstring: variable is complex: '['AtPredication', udef_q(x11,[_folder_n_of(x11,i18), card(3,e17,x11)],_in_p_loc(e2,x3,x11)), 'x3']'
    # SString 2023-05-31 13:41:24,953: sstring: error predication index is: 3
    # SString 2023-05-31 13:41:24,953: sstring: default meaning_at_index is '2'
    # SString 2023-05-31 13:41:24,953: sstring: meaning_at_index specified by complex variable: 3
    # SString 2023-05-31 13:41:24,953: sstring: non-default meaning_at_index: only use fallback
    # SString 2023-05-31 13:41:24,953: sstring: MRS failed, try fallback
    # SString 2023-05-31 13:41:24,953: sstring: Fallback generated: x3[ delphin(arg1):PluralMode.as_is@error_predicate_index]=2 file
    # There are more than 2 2 file
    #
    # Test: which 2 files in the folder are large?
    # SString 2023-05-31 13:41:30,830: sstring: tree is: _the_q:0(x12,_folder_n_of:1(x12,i17),_which_q:2(x3,[_file_n_of:3(x3,i10), _in_p_loc:4(e11,x3,x12), card:5(2,e9,x3)],_large_a_1:6(e2,x3)))
    # SString 2023-05-31 13:41:30,830: sstring: original text is: 'bare arg1'
    # SString 2023-05-31 13:41:30,830: sstring: plural is: PluralMode.as_is
    # SString 2023-05-31 13:41:30,831: sstring: variable_name is '['AtPredication', _which_q(x3,[_file_n_of(x3,i10), _in_p_loc(e11,x3,x12), card(2,e9,x3)],_large_a_1(e2,x3)), 'x12']'
    # SString 2023-05-31 13:41:30,831: sstring: variable is complex: '['AtPredication', _which_q(x3,[_file_n_of(x3,i10), _in_p_loc(e11,x3,x12), card(2,e9,x3)],_large_a_1(e2,x3)), 'x12']'
    # SString 2023-05-31 13:41:30,831: sstring: error predication index is: 2
    # SString 2023-05-31 13:41:30,831: sstring: default meaning_at_index is '2'
    # SString 2023-05-31 13:41:30,831: sstring: meaning_at_index specified by complex variable: 2
    # SString 2023-05-31 13:41:30,831: sstring: default meaning_at_index: trying MRS generation
    # SString 2023-05-31 13:41:30,977: sstring MRS generated: x12[ delphin(arg1):PluralMode.as_is]=folder
    # SString 2023-05-31 13:41:36,543: sstring: tree is: _which_q:0(x3,_the_q:1(x12,_folder_n_of:2(x12,i17),[_file_n_of:3(x3,i10), _in_p_loc:4(e11,x3,x12), card:5(2,e9,x3)]),_large_a_1:6(e2,x3))
    # SString 2023-05-31 13:41:36,543: sstring: original text is: 'bare arg1'
    # SString 2023-05-31 13:41:36,543: sstring: plural is: PluralMode.as_is
    # SString 2023-05-31 13:41:36,544: sstring: variable_name is '['AtPredication', [_file_n_of(x3,i10), _in_p_loc(e11,x3,x12), card(2,e9,x3)], 'x12']'
    # SString 2023-05-31 13:41:36,544: sstring: variable is complex: '['AtPredication', [_file_n_of(x3,i10), _in_p_loc(e11,x3,x12), card(2,e9,x3)], 'x12']'
    # SString 2023-05-31 13:41:36,544: sstring: error predication index is: 5
    # SString 2023-05-31 13:41:36,545: sstring: default meaning_at_index is '3'
    # SString 2023-05-31 13:41:36,545: sstring: meaning_at_index specified by complex variable: 5
    # SString 2023-05-31 13:41:36,545: sstring: non-default meaning_at_index: only use fallback
    # SString 2023-05-31 13:41:36,545: sstring: MRS failed, try fallback
    # SString 2023-05-31 13:41:36,545: sstring: Fallback generated: x12[ delphin(arg1):PluralMode.as_is]=folder
    # There is more than one folder
    #
    # Test: /new examples.Example26_reset
    # State reset using examples.Example26_reset().
    #
    # Test: 2 files are large
    # Yes, that is true.
    # (there are more)
    #
    # Test: only 2 files are large
    # SString 2023-05-31 13:41:37,151: sstring: tree is: udef_q:0(x3,[_file_n_of:1(x3,i11), _only_x_deg:2(e5,e6), card:3(2,e6,x3)],_large_a_1:4(e2,x3))
    # SString 2023-05-31 13:41:37,151: sstring: original text is: ''is':<*arg2'
    # SString 2023-05-31 13:41:37,152: sstring: plural template is: 2
    # SString 2023-05-31 13:41:37,152: sstring: plural is: PluralMode.plural
    # SString 2023-05-31 13:41:37,153: sstring: tree is: udef_q:0(x3,[_file_n_of:1(x3,i11), _only_x_deg:2(e5,e6), card:3(2,e6,x3)],_large_a_1:4(e2,x3))
    # SString 2023-05-31 13:41:37,153: sstring: original text is: '*arg2'
    # SString 2023-05-31 13:41:37,153: sstring: plural is: PluralMode.as_is
    # SString 2023-05-31 13:41:37,155: sstring: tree is: udef_q:0(x3,[_file_n_of:1(x3,i11), _only_x_deg:2(e5,e6), card:3(2,e6,x3)],_large_a_1:4(e2,x3))
    # SString 2023-05-31 13:41:37,155: sstring: original text is: 'bare arg1:@error_predicate_index'
    # SString 2023-05-31 13:41:37,155: sstring: plural is: PluralMode.as_is
    # SString 2023-05-31 13:41:37,156: sstring: variable_name is '['AfterFullPhrase', 'x3']'
    # SString 2023-05-31 13:41:37,156: sstring: variable is complex: '['AfterFullPhrase', 'x3']'
    # SString 2023-05-31 13:41:37,156: sstring: default meaning_at_index is '2'
    # SString 2023-05-31 13:41:37,156: sstring: meaning_at_index specified by complex variable: 100000000
    # SString 2023-05-31 13:41:37,156: sstring: non-default meaning_at_index: only use fallback
    # SString 2023-05-31 13:41:37,156: sstring: MRS failed, try fallback
    # SString 2023-05-31 13:41:37,156: sstring: Fallback generated: x3[ delphin(arg1):PluralMode.as_is@error_predicate_index]=2 large file
    # There are more than 2 2 large file
    #
    # Test: /new examples.Example21_reset
    # State reset using examples.Example21_reset().
    #
    # Test: delete a large file
    # Done!
    #
    # Test: which files are large?
    # SString 2023-05-31 13:41:37,586: sstring: tree is: _which_q:0(x3,_file_n_of:1(x3,i8),_large_a_1:2(e2,x3))
    # SString 2023-05-31 13:41:37,587: sstring: original text is: 'A arg2'
    # SString 2023-05-31 13:41:37,587: sstring: plural is: PluralMode.as_is
    # SString 2023-05-31 13:41:37,587: sstring: variable_name is 'x3'
    # SString 2023-05-31 13:41:37,588: sstring: default meaning_at_index is '2'
    # SString 2023-05-31 13:41:37,588: sstring: meaning_at_index not specified, using default: '2'
    # SString 2023-05-31 13:41:37,588: sstring: default meaning_at_index: trying MRS generation
    # SString 2023-05-31 13:41:37,742: sstring MRS generated: x3[CAP+A delphin(arg2):PluralMode.as_is]=files
    # SString 2023-05-31 13:41:37,743: sstring: tree is: _which_q:0(x3,_file_n_of:1(x3,i8),_large_a_1:2(e2,x3))
    # SString 2023-05-31 13:41:37,743: sstring: original text is: ''is':<arg2'
    # SString 2023-05-31 13:41:37,744: sstring: plural is: PluralMode.plural
    # SString 2023-05-31 13:41:37,745: sstring: tree is: _which_q:0(x3,_file_n_of:1(x3,i8),_large_a_1:2(e2,x3))
    # SString 2023-05-31 13:41:37,745: sstring: original text is: '*arg1'
    # SString 2023-05-31 13:41:37,745: sstring: plural is: PluralMode.as_is
    # files are not large
    #
    # Test: /new examples.Example34_reset
    # State reset using examples.Example34_reset().
    #
    # Test: which file is large
    # (File(name=/Desktop/file1.txt, size=10000000),)
    # (there are more)
    #
    # Test: /new examples.Example36_reset
    # State reset using examples.Example36_reset().
    #
    # Test: which 2 files in a folder are large?
    # SString 2023-05-31 13:41:38,201: sstring: tree is: _a_q:0(x12,_folder_n_of:1(x12,i17),_which_q:2(x3,[_file_n_of:3(x3,i10), _in_p_loc:4(e11,x3,x12), card:5(2,e9,x3)],_large_a_1:6(e2,x3)))
    # SString 2023-05-31 13:41:38,201: sstring: original text is: '*arg2'
    # SString 2023-05-31 13:41:38,202: sstring: plural is: PluralMode.as_is
    # SString 2023-05-31 13:41:38,203: sstring: tree is: _a_q:0(x12,_folder_n_of:1(x12,i17),_which_q:2(x3,[_file_n_of:3(x3,i10), _in_p_loc:4(e11,x3,x12), card:5(2,e9,x3)],_large_a_1:6(e2,x3)))
    # SString 2023-05-31 13:41:38,204: sstring: original text is: 'bare arg1:sg@error_predicate_index'
    # SString 2023-05-31 13:41:38,204: sstring: plural is: PluralMode.singular
    # SString 2023-05-31 13:41:38,204: sstring: variable_name is '['AfterFullPhrase', 'x3']'
    # SString 2023-05-31 13:41:38,204: sstring: variable is complex: '['AfterFullPhrase', 'x3']'
    # SString 2023-05-31 13:41:38,204: sstring: default meaning_at_index is '4'
    # SString 2023-05-31 13:41:38,205: sstring: meaning_at_index specified by complex variable: 100000000
    # SString 2023-05-31 13:41:38,205: sstring: non-default meaning_at_index: only use fallback
    # SString 2023-05-31 13:41:38,205: sstring: MRS failed, try fallback
    # SString 2023-05-31 13:41:38,205: sstring: Fallback generated: x3[ delphin(arg1):PluralMode.singular@error_predicate_index]=2 large file in a folder
    # (File(name=/Desktop/file2.txt, size=10000000),)
    # (File(name=/documents/file4.txt, size=10000000),)
    #
    # Test: /new examples.Example19_reset
    # State reset using examples.Example19_reset().
    #
    # Test: a file is large
    # SString 2023-05-31 13:41:38,418: sstring: tree is: _a_q:0(x3,_file_n_of:1(x3,i8),_large_a_1:2(e2,x3))
    # SString 2023-05-31 13:41:38,418: sstring: original text is: 'A arg2'
    # SString 2023-05-31 13:41:38,418: sstring: plural is: PluralMode.as_is
    # SString 2023-05-31 13:41:38,419: sstring: variable_name is 'x3'
    # SString 2023-05-31 13:41:38,419: sstring: default meaning_at_index is '2'
    # SString 2023-05-31 13:41:38,419: sstring: meaning_at_index not specified, using default: '2'
    # SString 2023-05-31 13:41:38,419: sstring: default meaning_at_index: trying MRS generation
    # SString 2023-05-31 13:41:38,607: sstring MRS generated: x3[CAP+A delphin(arg2):PluralMode.as_is]=a file
    # SString 2023-05-31 13:41:38,608: sstring: tree is: _a_q:0(x3,_file_n_of:1(x3,i8),_large_a_1:2(e2,x3))
    # SString 2023-05-31 13:41:38,608: sstring: original text is: ''is':<arg2'
    # SString 2023-05-31 13:41:38,609: sstring: plural is: PluralMode.singular
    # SString 2023-05-31 13:41:38,610: sstring: tree is: _a_q:0(x3,_file_n_of:1(x3,i8),_large_a_1:2(e2,x3))
    # SString 2023-05-31 13:41:38,610: sstring: original text is: '*arg1'
    # SString 2023-05-31 13:41:38,610: sstring: plural is: PluralMode.as_is
    # a file is not large
    #
    # Test: delete a large file
    # SString 2023-05-31 13:41:38,772: sstring: tree is: pronoun_q:0(x3,pron:1(x3),_a_q:2(x8,[_file_n_of:3(x8,i14), _large_a_1:4(e13,x8)],_delete_v_1:5(e2,x3,x8)))
    # SString 2023-05-31 13:41:38,772: sstring: original text is: 'a arg1:sg'
    # SString 2023-05-31 13:41:38,772: sstring: plural is: PluralMode.singular
    # SString 2023-05-31 13:41:38,773: sstring: variable_name is '['AtPredication', _delete_v_1(e2,x3,x8), 'x8']'
    # SString 2023-05-31 13:41:38,774: sstring: variable is complex: '['AtPredication', _delete_v_1(e2,x3,x8), 'x8']'
    # SString 2023-05-31 13:41:38,774: sstring: error predication index is: 5
    # SString 2023-05-31 13:41:38,774: sstring: default meaning_at_index is '4'
    # SString 2023-05-31 13:41:38,774: sstring: meaning_at_index specified by complex variable: 5
    # SString 2023-05-31 13:41:38,774: sstring: non-default meaning_at_index: only use fallback
    # SString 2023-05-31 13:41:38,774: sstring: MRS failed, try fallback
    # SString 2023-05-31 13:41:38,774: sstring: Fallback generated: x8[a delphin(arg1):PluralMode.singular]=a large file
    # SString 2023-05-31 13:41:38,779: sstring: tree is: _a_q:0(x8,[_file_n_of:1(x8,i14), _large_a_1:2(e13,x8)],pronoun_q:3(x3,pron:4(x3),_delete_v_1:5(e2,x3,x8)))
    # SString 2023-05-31 13:41:38,780: sstring: original text is: 'a arg1:sg'
    # SString 2023-05-31 13:41:38,780: sstring: plural is: PluralMode.singular
    # SString 2023-05-31 13:41:38,780: sstring: variable_name is '['AtPredication', pronoun_q(x3,pron(x3),_delete_v_1(e2,x3,x8)), 'x8']'
    # SString 2023-05-31 13:41:38,780: sstring: variable is complex: '['AtPredication', pronoun_q(x3,pron(x3),_delete_v_1(e2,x3,x8)), 'x8']'
    # SString 2023-05-31 13:41:38,780: sstring: error predication index is: 3
    # SString 2023-05-31 13:41:38,780: sstring: default meaning_at_index is '2'
    # SString 2023-05-31 13:41:38,781: sstring: meaning_at_index specified by complex variable: 3
    # SString 2023-05-31 13:41:38,781: sstring: non-default meaning_at_index: only use fallback
    # SString 2023-05-31 13:41:38,781: sstring: MRS failed, try fallback
    # SString 2023-05-31 13:41:38,781: sstring: Fallback generated: x8[a delphin(arg1):PluralMode.singular]=a large file
    # There isn't a large file in the system
    #
    # Test: which files are small?
    # SString 2023-05-31 13:41:38,949: sstring: tree is: _which_q:0(x3,_file_n_of:1(x3,i8),_small_a_1:2(e2,x3))
    # SString 2023-05-31 13:41:38,949: sstring: original text is: '*arg2'
    # SString 2023-05-31 13:41:38,949: sstring: plural is: PluralMode.as_is
    # SString 2023-05-31 13:41:38,951: sstring: tree is: _which_q:0(x3,_file_n_of:1(x3,i8),_small_a_1:2(e2,x3))
    # SString 2023-05-31 13:41:38,951: sstring: original text is: 'bare arg1:sg@error_predicate_index'
    # SString 2023-05-31 13:41:38,951: sstring: plural is: PluralMode.singular
    # SString 2023-05-31 13:41:38,952: sstring: variable_name is '['AfterFullPhrase', 'x3']'
    # SString 2023-05-31 13:41:38,952: sstring: variable is complex: '['AfterFullPhrase', 'x3']'
    # SString 2023-05-31 13:41:38,952: sstring: default meaning_at_index is '2'
    # SString 2023-05-31 13:41:38,952: sstring: meaning_at_index specified by complex variable: 100000000
    # SString 2023-05-31 13:41:38,952: sstring: non-default meaning_at_index: only use fallback
    # SString 2023-05-31 13:41:38,952: sstring: MRS failed, try fallback
    # SString 2023-05-31 13:41:38,952: sstring: Fallback generated: x3[ delphin(arg1):PluralMode.singular@error_predicate_index]=small file
    # There are less than 2 small file
    #
    # Test: which file is small?
    # (File(name=/documents/file1.txt, size=1000000),)
    #
    # Test: delete a file
    # Done!
    #
    # Test: a file is large
    # SString 2023-05-31 13:41:39,445: sstring: tree is: _a_q:0(x3,_file_n_of:1(x3,i8),_large_a_1:2(e2,x3))
    # SString 2023-05-31 13:41:39,445: sstring: original text is: 'a arg1:sg'
    # SString 2023-05-31 13:41:39,445: sstring: plural is: PluralMode.singular
    # SString 2023-05-31 13:41:39,446: sstring: variable_name is '['AtPredication', _large_a_1(e2,x3), 'x3']'
    # SString 2023-05-31 13:41:39,446: sstring: variable is complex: '['AtPredication', _large_a_1(e2,x3), 'x3']'
    # SString 2023-05-31 13:41:39,447: sstring: error predication index is: 2
    # SString 2023-05-31 13:41:39,447: sstring: default meaning_at_index is '2'
    # SString 2023-05-31 13:41:39,447: sstring: meaning_at_index specified by complex variable: 2
    # SString 2023-05-31 13:41:39,447: sstring: default meaning_at_index: trying MRS generation
    # SString 2023-05-31 13:41:39,657: sstring MRS generated: x3[a delphin(arg1):PluralMode.singular]=a file
    # There isn't a file in the system
    #
    # Test: which files are small?
    # SString 2023-05-31 13:41:39,815: sstring: tree is: _which_q:0(x3,_file_n_of:1(x3,i8),_small_a_1:2(e2,x3))
    # SString 2023-05-31 13:41:39,815: sstring: original text is: 'a arg1:sg'
    # SString 2023-05-31 13:41:39,815: sstring: plural is: PluralMode.singular
    # SString 2023-05-31 13:41:39,816: sstring: variable_name is '['AtPredication', _small_a_1(e2,x3), 'x3']'
    # SString 2023-05-31 13:41:39,816: sstring: variable is complex: '['AtPredication', _small_a_1(e2,x3), 'x3']'
    # SString 2023-05-31 13:41:39,816: sstring: error predication index is: 2
    # SString 2023-05-31 13:41:39,816: sstring: default meaning_at_index is '2'
    # SString 2023-05-31 13:41:39,816: sstring: meaning_at_index specified by complex variable: 2
    # SString 2023-05-31 13:41:39,816: sstring: default meaning_at_index: trying MRS generation
    # SString 2023-05-31 13:41:39,967: sstring MRS generated: x3[a delphin(arg1):PluralMode.singular]=a file
    # There isn't a file in the system
    #
    # Test: /reset
    # State reset using examples.Example19_reset().
    #
    # Test: there is a folder
    # I don't know the words: be
    #
    # Test: delete a folder
    # Done!
    # (there are more)
    #
    # Test: /new examples.Example18a_reset
    # State reset using examples.Example18a_reset().
    #
    # Test: a file is deleted
    # I don't know the way you used: delete
    #
    # Test: which file is very small?
    # SString 2023-05-31 13:41:40,746: sstring: tree is: _which_q:0(x3,_file_n_of:1(x3,i8),[_very_x_deg:2(e9,e2), _small_a_1:3(e2,x3)])
    # SString 2023-05-31 13:41:40,746: sstring: original text is: 'A arg2'
    # SString 2023-05-31 13:41:40,746: sstring: plural is: PluralMode.as_is
    # SString 2023-05-31 13:41:40,747: sstring: variable_name is 'x3'
    # SString 2023-05-31 13:41:40,747: sstring: default meaning_at_index is '2'
    # SString 2023-05-31 13:41:40,747: sstring: meaning_at_index not specified, using default: '2'
    # SString 2023-05-31 13:41:40,747: sstring: default meaning_at_index: trying MRS generation
    # SString 2023-05-31 13:41:40,897: sstring MRS generated: x3[CAP+A delphin(arg2):PluralMode.as_is]=a file
    # SString 2023-05-31 13:41:40,898: sstring: tree is: _which_q:0(x3,_file_n_of:1(x3,i8),[_very_x_deg:2(e9,e2), _small_a_1:3(e2,x3)])
    # SString 2023-05-31 13:41:40,898: sstring: original text is: ''is':<arg2'
    # SString 2023-05-31 13:41:40,899: sstring: plural is: PluralMode.singular
    # SString 2023-05-31 13:41:40,900: sstring: tree is: _which_q:0(x3,_file_n_of:1(x3,i8),[_very_x_deg:2(e9,e2), _small_a_1:3(e2,x3)])
    # SString 2023-05-31 13:41:40,900: sstring: original text is: '*arg1'
    # SString 2023-05-31 13:41:40,900: sstring: plural is: PluralMode.as_is
    # a file is not small
    #
    # Test: a file is deleted
    # I don't know the way you used: delete
    #
    # Test: delete you
    # I can't delete you
    #
    # Test: he deletes a file
    # I don't know the way you used: delete
    #
    # Test: /new examples.Example20_reset
    # State reset using examples.Example20_reset().
    #
    # Test: where am i
    # (Folder(name=/Desktop, size=0),)
    # (there are more)
    #
    # Test: /new examples.Example21_reset
    # State reset using examples.Example21_reset().
    #
    # Test: where am i
    # (Folder(name=/Desktop, size=0),)
    # (there are more)
    #
    # Test: where is this folder
    # (Folder(name=/, size=0),)
    #
    # Test: this folder is large
    # SString 2023-05-31 13:41:42,337: sstring: tree is: _this_q_dem:0(x3,_folder_n_of:1(x3,i8),_large_a_1:2(e2,x3))
    # SString 2023-05-31 13:41:42,337: sstring: original text is: 'A arg2'
    # SString 2023-05-31 13:41:42,337: sstring: plural is: PluralMode.as_is
    # SString 2023-05-31 13:41:42,338: sstring: variable_name is 'x3'
    # SString 2023-05-31 13:41:42,338: sstring: default meaning_at_index is '2'
    # SString 2023-05-31 13:41:42,338: sstring: meaning_at_index not specified, using default: '2'
    # SString 2023-05-31 13:41:42,338: sstring: default meaning_at_index: trying MRS generation
    # SString 2023-05-31 13:41:42,538: sstring MRS generated: x3[CAP+A delphin(arg2):PluralMode.as_is]=this folder
    # SString 2023-05-31 13:41:42,539: sstring: tree is: _this_q_dem:0(x3,_folder_n_of:1(x3,i8),_large_a_1:2(e2,x3))
    # SString 2023-05-31 13:41:42,539: sstring: original text is: ''is':<arg2'
    # SString 2023-05-31 13:41:42,540: sstring: plural is: PluralMode.singular
    # SString 2023-05-31 13:41:42,541: sstring: tree is: _this_q_dem:0(x3,_folder_n_of:1(x3,i8),_large_a_1:2(e2,x3))
    # SString 2023-05-31 13:41:42,541: sstring: original text is: '*arg1'
    # SString 2023-05-31 13:41:42,541: sstring: plural is: PluralMode.as_is
    # this folder is not large
    #
    # Test: /new examples.Example22_reset
    # State reset using examples.Example22_reset().
    #
    # Test: what is large?
    # (Folder(name=/Desktop, size=10000000),)
    # (there are more)
    #
    # Test: /reset
    # State reset using examples.Example22_reset().
    #
    # Test: what is in this folder?
    # (File(name=/Desktop/file2.txt, size=10000000),)
    # (there are more)
    #
    # Test: what am i in?
    # (Folder(name=/Desktop, size=10000000),)
    # (there are more)
    #
    # Test: is a file in this folder
    # Yes.
    # (there are more)
    #
    # Test: is a folder in this folder
    # SString 2023-05-31 13:41:43,891: sstring: tree is: _this_q_dem:0(x9,_folder_n_of:1(x9,i14),_a_q:2(x3,_folder_n_of:3(x3,i8),_in_p_loc:4(e2,x3,x9)))
    # SString 2023-05-31 13:41:43,891: sstring: original text is: 'arg1'
    # SString 2023-05-31 13:41:43,891: sstring: plural is: PluralMode.as_is
    # SString 2023-05-31 13:41:43,892: sstring: variable_name is 'x3'
    # SString 2023-05-31 13:41:43,892: sstring: default meaning_at_index is '4'
    # SString 2023-05-31 13:41:43,892: sstring: meaning_at_index not specified, using default: '4'
    # SString 2023-05-31 13:41:43,892: sstring: default meaning_at_index: trying MRS generation
    # SString 2023-05-31 13:41:44,044: Nothing could be generated for: is a folder in this folder: [ TOP: h0 INDEX: e2 [ e SF: prop ] RELS: < [ _this_q_dem<15:19> LBL: h10 ARG0: x9 [ x PERS: 3 NUM: sg IND: + ] RSTR: h11 BODY: h12 ] [ _folder_n_of<20:26> LBL: h13 ARG0: x9 ARG1: i14 ] [ _folder_n_of<5:11> LBL: h7 ARG0: x3 [ x PERS: 3 NUM: sg IND: + ] ARG1: i8 ] [ _a_q<3:4> LBL: h4 ARG0: x3 RSTR: h5 BODY: h6 ] [ unknown LBL: h1 ARG: x3 ARG0: e2 ] > HCONS: < h0 qeq h1 h5 qeq h7 h11 qeq h13 > ]
    # SString 2023-05-31 13:41:44,045: sstring: MRS failed, try fallback
    # SString 2023-05-31 13:41:44,045: sstring: Fallback generated: x3[None delphin(arg1):PluralMode.as_is]=a folder
    # SString 2023-05-31 13:41:44,046: sstring: tree is: _this_q_dem:0(x9,_folder_n_of:1(x9,i14),_a_q:2(x3,_folder_n_of:3(x3,i8),_in_p_loc:4(e2,x3,x9)))
    # SString 2023-05-31 13:41:44,046: sstring: original text is: 'arg2'
    # SString 2023-05-31 13:41:44,046: sstring: plural is: PluralMode.as_is
    # SString 2023-05-31 13:41:44,047: sstring: variable_name is 'x9'
    # SString 2023-05-31 13:41:44,047: sstring: default meaning_at_index is '2'
    # SString 2023-05-31 13:41:44,047: sstring: meaning_at_index not specified, using default: '2'
    # SString 2023-05-31 13:41:44,047: sstring: default meaning_at_index: trying MRS generation
    # SString 2023-05-31 13:41:44,249: sstring MRS generated: x9[None delphin(arg2):PluralMode.as_is]=this folder
    # SString 2023-05-31 13:41:44,262: sstring: tree is: _a_q:0(x3,_folder_n_of:1(x3,i8),_this_q_dem:2(x9,_folder_n_of:3(x9,i14),_in_p_loc:4(e2,x3,x9)))
    # SString 2023-05-31 13:41:44,262: sstring: original text is: 'arg1'
    # SString 2023-05-31 13:41:44,262: sstring: plural is: PluralMode.as_is
    # SString 2023-05-31 13:41:44,263: sstring: variable_name is 'x3'
    # SString 2023-05-31 13:41:44,263: sstring: default meaning_at_index is '2'
    # SString 2023-05-31 13:41:44,263: sstring: meaning_at_index not specified, using default: '2'
    # SString 2023-05-31 13:41:44,263: sstring: default meaning_at_index: trying MRS generation
    # SString 2023-05-31 13:41:44,415: sstring MRS generated: x3[None delphin(arg1):PluralMode.as_is]=a folder
    # SString 2023-05-31 13:41:44,417: sstring: tree is: _a_q:0(x3,_folder_n_of:1(x3,i8),_this_q_dem:2(x9,_folder_n_of:3(x9,i14),_in_p_loc:4(e2,x3,x9)))
    # SString 2023-05-31 13:41:44,417: sstring: original text is: 'arg2'
    # SString 2023-05-31 13:41:44,417: sstring: plural is: PluralMode.as_is
    # SString 2023-05-31 13:41:44,418: sstring: variable_name is 'x9'
    # SString 2023-05-31 13:41:44,418: sstring: default meaning_at_index is '4'
    # SString 2023-05-31 13:41:44,418: sstring: meaning_at_index not specified, using default: '4'
    # SString 2023-05-31 13:41:44,418: sstring: default meaning_at_index: trying MRS generation
    # SString 2023-05-31 13:41:44,573: Nothing could be generated for: is a folder in this folder: [ TOP: h0 INDEX: e2 [ e SF: prop ] RELS: < [ _a_q<3:4> LBL: h4 ARG0: x3 [ x PERS: 3 NUM: sg IND: + ] RSTR: h5 BODY: h6 ] [ _folder_n_of<5:11> LBL: h7 ARG0: x3 ARG1: i8 ] [ _folder_n_of<20:26> LBL: h13 ARG0: x9 [ x PERS: 3 NUM: sg IND: + ] ARG1: i14 ] [ _this_q_dem<15:19> LBL: h10 ARG0: x9 RSTR: h11 BODY: h12 ] [ unknown LBL: h1 ARG: x9 ARG0: e2 ] > HCONS: < h0 qeq h1 h5 qeq h7 h11 qeq h13 > ]
    # SString 2023-05-31 13:41:44,573: sstring: MRS failed, try fallback
    # SString 2023-05-31 13:41:44,573: sstring: Fallback generated: x9[None delphin(arg2):PluralMode.as_is]=this folder
    # a folder is not in this folder
    #
    # Test: which files are in this folder?
    # (File(name=/Desktop/file2.txt, size=10000000),)
    # (File(name=/Desktop/file3.txt, size=1000),)
    #
    # Test: /new examples.Example23_reset
    # State reset using examples.Example23_reset().
    #
    # Test: "blue" is in this folder
    # Yes, that is true.
    #
    # Test: what is in this 'blue'
    # SString 2023-05-31 13:41:45,674: sstring: tree is: which_q:0(x3,thing:1(x3),_this_q_dem:2(x8,[quoted:3(blue,i13), fw_seq:4(x8,i13)],_in_p_loc:5(e2,x3,x8)))
    # SString 2023-05-31 13:41:45,674: sstring: original text is: 'arg1'
    # SString 2023-05-31 13:41:45,674: sstring: plural is: PluralMode.as_is
    # SString 2023-05-31 13:41:45,675: sstring: variable_name is 'x3'
    # SString 2023-05-31 13:41:45,675: sstring: default meaning_at_index is '2'
    # SString 2023-05-31 13:41:45,676: sstring: meaning_at_index not specified, using default: '2'
    # SString 2023-05-31 13:41:45,676: sstring: default meaning_at_index: trying MRS generation
    # SString 2023-05-31 13:41:45,859: sstring MRS generated: x3[None delphin(arg1):PluralMode.as_is]=a thing
    # SString 2023-05-31 13:41:45,861: sstring: tree is: which_q:0(x3,thing:1(x3),_this_q_dem:2(x8,[quoted:3(blue,i13), fw_seq:4(x8,i13)],_in_p_loc:5(e2,x3,x8)))
    # SString 2023-05-31 13:41:45,861: sstring: original text is: 'arg2'
    # SString 2023-05-31 13:41:45,861: sstring: plural is: PluralMode.as_is
    # SString 2023-05-31 13:41:45,862: sstring: variable_name is 'x8'
    # SString 2023-05-31 13:41:45,862: sstring: default meaning_at_index is '5'
    # SString 2023-05-31 13:41:45,862: sstring: meaning_at_index not specified, using default: '5'
    # SString 2023-05-31 13:41:45,862: sstring: default meaning_at_index: trying MRS generation
    # SString 2023-05-31 13:41:46,023: Nothing could be generated for: what is in this 'blue': [ TOP: h0 INDEX: e2 [ e SF: prop ] RELS: < [ _a_q<0:4> LBL: h5 ARG0: x3 [ x PERS: 3 NUM: sg ] RSTR: h6 BODY: h7 ] [ _thing_n_of-about<0:4> LBL: h4 ARG0: x3 ARG1: i99 ] [ quoted<17:21> LBL: h12 ARG0: i13 CARG: "blue" ] [ fw_seq<-1:-1> LBL: h12 ARG0: x8 [ x PERS: 3 ] ARG1: i13 ] [ _this_q_dem<11:15> LBL: h9 ARG0: x8 RSTR: h10 BODY: h11 ] [ unknown LBL: h1 ARG: x8 ARG0: e2 ] > HCONS: < h0 qeq h1 h6 qeq h4 h10 qeq h12 > ]
    # SString 2023-05-31 13:41:46,024: sstring: MRS failed, try fallback
    # SString 2023-05-31 13:41:46,024: sstring: Fallback generated: x8[None delphin(arg2):PluralMode.as_is]=this 'blue'
    # SString 2023-05-31 13:41:46,038: sstring: tree is: _this_q_dem:0(x8,[quoted:1(blue,i13), fw_seq:2(x8,i13)],which_q:3(x3,thing:4(x3),_in_p_loc:5(e2,x3,x8)))
    # SString 2023-05-31 13:41:46,038: sstring: original text is: 'arg1'
    # SString 2023-05-31 13:41:46,038: sstring: plural is: PluralMode.as_is
    # SString 2023-05-31 13:41:46,039: sstring: variable_name is 'x3'
    # SString 2023-05-31 13:41:46,039: sstring: default meaning_at_index is '5'
    # SString 2023-05-31 13:41:46,039: sstring: meaning_at_index not specified, using default: '5'
    # SString 2023-05-31 13:41:46,039: sstring: default meaning_at_index: trying MRS generation
    # SString 2023-05-31 13:41:46,194: Nothing could be generated for: what is in this 'blue': [ TOP: h0 INDEX: e2 [ e SF: prop ] RELS: < [ _this_q_dem<11:15> LBL: h9 ARG0: x8 [ x PERS: 3 ] RSTR: h10 BODY: h11 ] [ quoted<17:21> LBL: h12 ARG0: i13 CARG: "blue" ] [ fw_seq<-1:-1> LBL: h12 ARG0: x8 ARG1: i13 ] [ _thing_n_of-about<0:4> LBL: h4 ARG0: x3 [ x PERS: 3 NUM: sg ] ARG1: i99 ] [ _a_q<0:4> LBL: h5 ARG0: x3 RSTR: h6 BODY: h7 ] [ unknown LBL: h1 ARG: x3 ARG0: e2 ] > HCONS: < h0 qeq h1 h6 qeq h4 h10 qeq h12 > ]
    # SString 2023-05-31 13:41:46,195: sstring: MRS failed, try fallback
    # SString 2023-05-31 13:41:46,195: sstring: Fallback generated: x3[None delphin(arg1):PluralMode.as_is]=thing
    # SString 2023-05-31 13:41:46,196: sstring: tree is: _this_q_dem:0(x8,[quoted:1(blue,i13), fw_seq:2(x8,i13)],which_q:3(x3,thing:4(x3),_in_p_loc:5(e2,x3,x8)))
    # SString 2023-05-31 13:41:46,196: sstring: original text is: 'arg2'
    # SString 2023-05-31 13:41:46,196: sstring: plural is: PluralMode.as_is
    # SString 2023-05-31 13:41:46,197: sstring: variable_name is 'x8'
    # SString 2023-05-31 13:41:46,197: sstring: default meaning_at_index is '3'
    # SString 2023-05-31 13:41:46,197: sstring: meaning_at_index not specified, using default: '3'
    # SString 2023-05-31 13:41:46,197: sstring: default meaning_at_index: trying MRS generation
    # SString 2023-05-31 13:41:46,335: Nothing could be generated for: what is in this 'blue': [ TOP: h0 INDEX: e2 [ e SF: prop ] RELS: < [ quoted<17:21> LBL: h12 ARG0: i13 CARG: "blue" ] [ fw_seq<-1:-1> LBL: h12 ARG0: x8 [ x PERS: 3 ] ARG1: i13 ] [ _this_q_dem<11:15> LBL: h9 ARG0: x8 RSTR: h10 BODY: h11 ] [ unknown LBL: h1 ARG: x8 ARG0: e2 ] > HCONS: < h0 qeq h1 h10 qeq h12 > ]
    # SString 2023-05-31 13:41:46,336: sstring: MRS failed, try fallback
    # SString 2023-05-31 13:41:46,336: sstring: Fallback generated: x8[None delphin(arg2):PluralMode.as_is]=this 'blue'
    # a thing is not in this 'blue'
    #
    # Test: delete "blue"
    # Done!
    #
    # Test: "blue" is in this folder
    # SString 2023-05-31 13:41:46,847: sstring: tree is: _this_q_dem:0(x10,_folder_n_of:1(x10,i15),proper_q:2(x3,[quoted:3(blue,i8), fw_seq:4(x3,i8)],_in_p_loc:5(e2,x3,x10)))
    # SString 2023-05-31 13:41:46,847: sstring: original text is: 'arg1'
    # SString 2023-05-31 13:41:46,847: sstring: plural is: PluralMode.as_is
    # SString 2023-05-31 13:41:46,848: sstring: variable_name is 'x3'
    # SString 2023-05-31 13:41:46,848: sstring: default meaning_at_index is '5'
    # SString 2023-05-31 13:41:46,848: sstring: meaning_at_index not specified, using default: '5'
    # SString 2023-05-31 13:41:46,848: sstring: default meaning_at_index: trying MRS generation
    # SString 2023-05-31 13:41:46,996: Nothing could be generated for: "blue" is in this folder: [ TOP: h0 INDEX: e2 [ e SF: prop ] RELS: < [ _this_q_dem<13:17> LBL: h11 ARG0: x10 [ x PERS: 3 NUM: sg IND: + ] RSTR: h12 BODY: h13 ] [ _folder_n_of<18:24> LBL: h14 ARG0: x10 ARG1: i15 ] [ quoted<1:5> LBL: h7 ARG0: i8 CARG: "blue" ] [ fw_seq<-1:-1> LBL: h7 ARG0: x3 [ x PERS: 3 NUM: sg ] ARG1: i8 ] [ proper_q<0:6> LBL: h4 ARG0: x3 RSTR: h5 BODY: h6 ] [ unknown LBL: h1 ARG: x3 ARG0: e2 ] > HCONS: < h0 qeq h1 h5 qeq h7 h12 qeq h14 > ]
    # SString 2023-05-31 13:41:46,996: sstring: MRS failed, try fallback
    # SString 2023-05-31 13:41:46,996: sstring: Fallback generated: x3[None delphin(arg1):PluralMode.as_is]='blue'
    # SString 2023-05-31 13:41:46,998: sstring: tree is: _this_q_dem:0(x10,_folder_n_of:1(x10,i15),proper_q:2(x3,[quoted:3(blue,i8), fw_seq:4(x3,i8)],_in_p_loc:5(e2,x3,x10)))
    # SString 2023-05-31 13:41:46,998: sstring: original text is: 'arg2'
    # SString 2023-05-31 13:41:46,998: sstring: plural is: PluralMode.as_is
    # SString 2023-05-31 13:41:46,999: sstring: variable_name is 'x10'
    # SString 2023-05-31 13:41:46,999: sstring: default meaning_at_index is '2'
    # SString 2023-05-31 13:41:46,999: sstring: meaning_at_index not specified, using default: '2'
    # SString 2023-05-31 13:41:46,999: sstring: default meaning_at_index: trying MRS generation
    # SString 2023-05-31 13:41:47,166: sstring MRS generated: x10[None delphin(arg2):PluralMode.as_is]=this folder
    # SString 2023-05-31 13:41:47,181: sstring: tree is: proper_q:0(x3,[quoted:1(blue,i8), fw_seq:2(x3,i8)],_this_q_dem:3(x10,_folder_n_of:4(x10,i15),_in_p_loc:5(e2,x3,x10)))
    # SString 2023-05-31 13:41:47,181: sstring: original text is: 'arg1'
    # SString 2023-05-31 13:41:47,181: sstring: plural is: PluralMode.as_is
    # SString 2023-05-31 13:41:47,182: sstring: variable_name is 'x3'
    # SString 2023-05-31 13:41:47,182: sstring: default meaning_at_index is '3'
    # SString 2023-05-31 13:41:47,182: sstring: meaning_at_index not specified, using default: '3'
    # SString 2023-05-31 13:41:47,182: sstring: default meaning_at_index: trying MRS generation
    # SString 2023-05-31 13:41:47,320: Nothing could be generated for: "blue" is in this folder: [ TOP: h0 INDEX: e2 [ e SF: prop ] RELS: < [ quoted<1:5> LBL: h7 ARG0: i8 CARG: "blue" ] [ fw_seq<-1:-1> LBL: h7 ARG0: x3 [ x PERS: 3 NUM: sg ] ARG1: i8 ] [ proper_q<0:6> LBL: h4 ARG0: x3 RSTR: h5 BODY: h6 ] [ unknown LBL: h1 ARG: x3 ARG0: e2 ] > HCONS: < h0 qeq h1 h5 qeq h7 > ]
    # SString 2023-05-31 13:41:47,321: sstring: MRS failed, try fallback
    # SString 2023-05-31 13:41:47,321: sstring: Fallback generated: x3[None delphin(arg1):PluralMode.as_is]='blue'
    # SString 2023-05-31 13:41:47,322: sstring: tree is: proper_q:0(x3,[quoted:1(blue,i8), fw_seq:2(x3,i8)],_this_q_dem:3(x10,_folder_n_of:4(x10,i15),_in_p_loc:5(e2,x3,x10)))
    # SString 2023-05-31 13:41:47,322: sstring: original text is: 'arg2'
    # SString 2023-05-31 13:41:47,322: sstring: plural is: PluralMode.as_is
    # SString 2023-05-31 13:41:47,323: sstring: variable_name is 'x10'
    # SString 2023-05-31 13:41:47,323: sstring: default meaning_at_index is '5'
    # SString 2023-05-31 13:41:47,323: sstring: meaning_at_index not specified, using default: '5'
    # SString 2023-05-31 13:41:47,324: sstring: default meaning_at_index: trying MRS generation
    # SString 2023-05-31 13:41:47,470: Nothing could be generated for: "blue" is in this folder: [ TOP: h0 INDEX: e2 [ e SF: prop ] RELS: < [ proper_q<0:6> LBL: h4 ARG0: x3 [ x PERS: 3 NUM: sg ] RSTR: h5 BODY: h6 ] [ quoted<1:5> LBL: h7 ARG0: i8 CARG: "blue" ] [ fw_seq<-1:-1> LBL: h7 ARG0: x3 ARG1: i8 ] [ _folder_n_of<18:24> LBL: h14 ARG0: x10 [ x PERS: 3 NUM: sg IND: + ] ARG1: i15 ] [ _this_q_dem<13:17> LBL: h11 ARG0: x10 RSTR: h12 BODY: h13 ] [ unknown LBL: h1 ARG: x10 ARG0: e2 ] > HCONS: < h0 qeq h1 h5 qeq h7 h12 qeq h14 > ]
    # SString 2023-05-31 13:41:47,470: sstring: MRS failed, try fallback
    # SString 2023-05-31 13:41:47,470: sstring: Fallback generated: x10[None delphin(arg2):PluralMode.as_is]=this folder
    # 'blue' is not in this folder
    #
    # Test: "the yearly budget.txt" is in this folder
    # Yes, that is true.
    #
    # Test: delete "the yearly budget.txt"
    # Done!
    #
    # Test: "the yearly budget.txt" is in this folder
    # SString 2023-05-31 13:41:48,345: sstring: tree is: _this_q_dem:0(x15,_folder_n_of:1(x15,i20),proper_q:2(x3,[quoted:3(budget.txt,i9), quoted:4(yearly,i11), quoted:5(the,i10), fw_seq:6(x8,i10,i11), fw_seq:7(x3,x8,i9)],_in_p_loc:8(e2,x3,x15)))
    # SString 2023-05-31 13:41:48,345: sstring: original text is: 'arg1'
    # SString 2023-05-31 13:41:48,345: sstring: plural is: PluralMode.as_is
    # SString 2023-05-31 13:41:48,346: sstring: variable_name is 'x3'
    # SString 2023-05-31 13:41:48,346: sstring: default meaning_at_index is '8'
    # SString 2023-05-31 13:41:48,346: sstring: meaning_at_index not specified, using default: '8'
    # SString 2023-05-31 13:41:48,346: sstring: default meaning_at_index: trying MRS generation
    # SString 2023-05-31 13:41:48,498: Nothing could be generated for: "the yearly budget.txt" is in this folder: [ TOP: h0 INDEX: e2 [ e SF: prop ] RELS: < [ _this_q_dem<30:34> LBL: h16 ARG0: x15 [ x PERS: 3 NUM: sg IND: + ] RSTR: h17 BODY: h18 ] [ _folder_n_of<35:41> LBL: h19 ARG0: x15 ARG1: i20 ] [ quoted<12:22> LBL: h7 ARG0: i9 CARG: "budget.txt" ] [ quoted<5:11> LBL: h7 ARG0: i11 CARG: "yearly" ] [ quoted<1:4> LBL: h7 ARG0: i10 CARG: "the" ] [ fw_seq<0:11> LBL: h7 ARG0: x8 ARG1: i10 ARG2: i11 ] [ fw_seq<0:23> LBL: h7 ARG0: x3 [ x PERS: 3 NUM: sg ] ARG1: x8 ARG2: i9 ] [ proper_q<0:23> LBL: h4 ARG0: x3 RSTR: h5 BODY: h6 ] [ unknown LBL: h1 ARG: x3 ARG0: e2 ] > HCONS: < h0 qeq h1 h5 qeq h7 h17 qeq h19 > ]
    # SString 2023-05-31 13:41:48,498: sstring: MRS failed, try fallback
    # SString 2023-05-31 13:41:48,499: sstring: Fallback generated: x3[None delphin(arg1):PluralMode.as_is]='the yearly budget.txt'
    # SString 2023-05-31 13:41:48,500: sstring: tree is: _this_q_dem:0(x15,_folder_n_of:1(x15,i20),proper_q:2(x3,[quoted:3(budget.txt,i9), quoted:4(yearly,i11), quoted:5(the,i10), fw_seq:6(x8,i10,i11), fw_seq:7(x3,x8,i9)],_in_p_loc:8(e2,x3,x15)))
    # SString 2023-05-31 13:41:48,500: sstring: original text is: 'arg2'
    # SString 2023-05-31 13:41:48,500: sstring: plural is: PluralMode.as_is
    # SString 2023-05-31 13:41:48,501: sstring: variable_name is 'x15'
    # SString 2023-05-31 13:41:48,501: sstring: default meaning_at_index is '2'
    # SString 2023-05-31 13:41:48,501: sstring: meaning_at_index not specified, using default: '2'
    # SString 2023-05-31 13:41:48,502: sstring: default meaning_at_index: trying MRS generation
    # SString 2023-05-31 13:41:48,649: sstring MRS generated: x15[None delphin(arg2):PluralMode.as_is]=this folder
    # SString 2023-05-31 13:41:48,673: sstring: tree is: proper_q:0(x3,[quoted:1(budget.txt,i9), quoted:2(yearly,i11), quoted:3(the,i10), fw_seq:4(x8,i10,i11), fw_seq:5(x3,x8,i9)],_this_q_dem:6(x15,_folder_n_of:7(x15,i20),_in_p_loc:8(e2,x3,x15)))
    # SString 2023-05-31 13:41:48,673: sstring: original text is: 'arg1'
    # SString 2023-05-31 13:41:48,673: sstring: plural is: PluralMode.as_is
    # SString 2023-05-31 13:41:48,674: sstring: variable_name is 'x3'
    # SString 2023-05-31 13:41:48,674: sstring: default meaning_at_index is '6'
    # SString 2023-05-31 13:41:48,674: sstring: meaning_at_index not specified, using default: '6'
    # SString 2023-05-31 13:41:48,674: sstring: default meaning_at_index: trying MRS generation
    # SString 2023-05-31 13:41:48,816: Nothing could be generated for: "the yearly budget.txt" is in this folder: [ TOP: h0 INDEX: e2 [ e SF: prop ] RELS: < [ quoted<12:22> LBL: h7 ARG0: i9 CARG: "budget.txt" ] [ quoted<5:11> LBL: h7 ARG0: i11 CARG: "yearly" ] [ quoted<1:4> LBL: h7 ARG0: i10 CARG: "the" ] [ fw_seq<0:11> LBL: h7 ARG0: x8 ARG1: i10 ARG2: i11 ] [ fw_seq<0:23> LBL: h7 ARG0: x3 [ x PERS: 3 NUM: sg ] ARG1: x8 ARG2: i9 ] [ proper_q<0:23> LBL: h4 ARG0: x3 RSTR: h5 BODY: h6 ] [ unknown LBL: h1 ARG: x3 ARG0: e2 ] > HCONS: < h0 qeq h1 h5 qeq h7 > ]
    # SString 2023-05-31 13:41:48,816: sstring: MRS failed, try fallback
    # SString 2023-05-31 13:41:48,817: sstring: Fallback generated: x3[None delphin(arg1):PluralMode.as_is]='the yearly budget.txt'
    # SString 2023-05-31 13:41:48,818: sstring: tree is: proper_q:0(x3,[quoted:1(budget.txt,i9), quoted:2(yearly,i11), quoted:3(the,i10), fw_seq:4(x8,i10,i11), fw_seq:5(x3,x8,i9)],_this_q_dem:6(x15,_folder_n_of:7(x15,i20),_in_p_loc:8(e2,x3,x15)))
    # SString 2023-05-31 13:41:48,818: sstring: original text is: 'arg2'
    # SString 2023-05-31 13:41:48,818: sstring: plural is: PluralMode.as_is
    # SString 2023-05-31 13:41:48,819: sstring: variable_name is 'x15'
    # SString 2023-05-31 13:41:48,819: sstring: default meaning_at_index is '8'
    # SString 2023-05-31 13:41:48,819: sstring: meaning_at_index not specified, using default: '8'
    # SString 2023-05-31 13:41:48,819: sstring: default meaning_at_index: trying MRS generation
    # SString 2023-05-31 13:41:49,086: Nothing could be generated for: "the yearly budget.txt" is in this folder: [ TOP: h0 INDEX: e2 [ e SF: prop ] RELS: < [ proper_q<0:23> LBL: h4 ARG0: x3 [ x PERS: 3 NUM: sg ] RSTR: h5 BODY: h6 ] [ quoted<12:22> LBL: h7 ARG0: i9 CARG: "budget.txt" ] [ quoted<5:11> LBL: h7 ARG0: i11 CARG: "yearly" ] [ quoted<1:4> LBL: h7 ARG0: i10 CARG: "the" ] [ fw_seq<0:11> LBL: h7 ARG0: x8 ARG1: i10 ARG2: i11 ] [ fw_seq<0:23> LBL: h7 ARG0: x3 ARG1: x8 ARG2: i9 ] [ _folder_n_of<35:41> LBL: h19 ARG0: x15 [ x PERS: 3 NUM: sg IND: + ] ARG1: i20 ] [ _this_q_dem<30:34> LBL: h16 ARG0: x15 RSTR: h17 BODY: h18 ] [ unknown LBL: h1 ARG: x15 ARG0: e2 ] > HCONS: < h0 qeq h1 h5 qeq h7 h17 qeq h19 > ]
    # SString 2023-05-31 13:41:49,086: sstring: MRS failed, try fallback
    # SString 2023-05-31 13:41:49,086: sstring: Fallback generated: x15[None delphin(arg2):PluralMode.as_is]=this folder
    # 'the yearly budget.txt' is not in this folder
    #
    # Test: what is "foo" in?
    # SString 2023-05-31 13:41:49,363: sstring: tree is: which_q:0(x5,thing:1(x5),proper_q:2(x3,[quoted:3(foo,i13), fw_seq:4(x3,i13)],_in_p_loc:5(e2,x3,x5)))
    # SString 2023-05-31 13:41:49,363: sstring: original text is: 'arg1'
    # SString 2023-05-31 13:41:49,363: sstring: plural is: PluralMode.as_is
    # SString 2023-05-31 13:41:49,364: sstring: variable_name is 'x3'
    # SString 2023-05-31 13:41:49,364: sstring: default meaning_at_index is '5'
    # SString 2023-05-31 13:41:49,364: sstring: meaning_at_index not specified, using default: '5'
    # SString 2023-05-31 13:41:49,364: sstring: default meaning_at_index: trying MRS generation
    # SString 2023-05-31 13:41:49,576: Nothing could be generated for: what is "foo" in?: [ TOP: h0 INDEX: e2 [ e SF: prop ] RELS: < [ which_q<0:4> LBL: h6 ARG0: x5 RSTR: h7 BODY: h8 ] [ _thing_n_of-about<0:4> LBL: h4 ARG0: x5 ARG1: i99 ] [ quoted<9:12> LBL: h12 ARG0: i13 CARG: "foo" ] [ fw_seq<-1:-1> LBL: h12 ARG0: x3 [ x PERS: 3 NUM: sg ] ARG1: i13 ] [ proper_q<8:13> LBL: h9 ARG0: x3 RSTR: h10 BODY: h11 ] [ unknown LBL: h1 ARG: x3 ARG0: e2 ] > HCONS: < h0 qeq h1 h7 qeq h4 h10 qeq h12 > ]
    # SString 2023-05-31 13:41:49,576: sstring: MRS failed, try fallback
    # SString 2023-05-31 13:41:49,577: sstring: Fallback generated: x3[None delphin(arg1):PluralMode.as_is]='foo'
    # SString 2023-05-31 13:41:49,578: sstring: tree is: which_q:0(x5,thing:1(x5),proper_q:2(x3,[quoted:3(foo,i13), fw_seq:4(x3,i13)],_in_p_loc:5(e2,x3,x5)))
    # SString 2023-05-31 13:41:49,578: sstring: original text is: 'arg2'
    # SString 2023-05-31 13:41:49,578: sstring: plural is: PluralMode.as_is
    # SString 2023-05-31 13:41:49,579: sstring: variable_name is 'x5'
    # SString 2023-05-31 13:41:49,579: sstring: default meaning_at_index is '2'
    # SString 2023-05-31 13:41:49,579: sstring: meaning_at_index not specified, using default: '2'
    # SString 2023-05-31 13:41:49,579: sstring: default meaning_at_index: trying MRS generation
    # SString 2023-05-31 13:41:49,767: sstring MRS generated: x5[None delphin(arg2):PluralMode.as_is]=a thing
    # SString 2023-05-31 13:41:49,778: sstring: tree is: proper_q:0(x3,[quoted:1(foo,i13), fw_seq:2(x3,i13)],which_q:3(x5,thing:4(x5),_in_p_loc:5(e2,x3,x5)))
    # SString 2023-05-31 13:41:49,778: sstring: original text is: 'arg1'
    # SString 2023-05-31 13:41:49,778: sstring: plural is: PluralMode.as_is
    # SString 2023-05-31 13:41:49,779: sstring: variable_name is 'x3'
    # SString 2023-05-31 13:41:49,779: sstring: default meaning_at_index is '3'
    # SString 2023-05-31 13:41:49,779: sstring: meaning_at_index not specified, using default: '3'
    # SString 2023-05-31 13:41:49,779: sstring: default meaning_at_index: trying MRS generation
    # SString 2023-05-31 13:41:49,917: Nothing could be generated for: what is "foo" in?: [ TOP: h0 INDEX: e2 [ e SF: prop ] RELS: < [ quoted<9:12> LBL: h12 ARG0: i13 CARG: "foo" ] [ fw_seq<-1:-1> LBL: h12 ARG0: x3 [ x PERS: 3 NUM: sg ] ARG1: i13 ] [ proper_q<8:13> LBL: h9 ARG0: x3 RSTR: h10 BODY: h11 ] [ unknown LBL: h1 ARG: x3 ARG0: e2 ] > HCONS: < h0 qeq h1 h10 qeq h12 > ]
    # SString 2023-05-31 13:41:49,918: sstring: MRS failed, try fallback
    # SString 2023-05-31 13:41:49,918: sstring: Fallback generated: x3[None delphin(arg1):PluralMode.as_is]='foo'
    # SString 2023-05-31 13:41:49,919: sstring: tree is: proper_q:0(x3,[quoted:1(foo,i13), fw_seq:2(x3,i13)],which_q:3(x5,thing:4(x5),_in_p_loc:5(e2,x3,x5)))
    # SString 2023-05-31 13:41:49,919: sstring: original text is: 'arg2'
    # SString 2023-05-31 13:41:49,919: sstring: plural is: PluralMode.as_is
    # SString 2023-05-31 13:41:49,921: sstring: variable_name is 'x5'
    # SString 2023-05-31 13:41:49,921: sstring: default meaning_at_index is '5'
    # SString 2023-05-31 13:41:49,921: sstring: meaning_at_index not specified, using default: '5'
    # SString 2023-05-31 13:41:49,921: sstring: default meaning_at_index: trying MRS generation
    # SString 2023-05-31 13:41:50,147: Nothing could be generated for: what is "foo" in?: [ TOP: h0 INDEX: e2 [ e SF: prop ] RELS: < [ proper_q<8:13> LBL: h9 ARG0: x3 [ x PERS: 3 NUM: sg ] RSTR: h10 BODY: h11 ] [ quoted<9:12> LBL: h12 ARG0: i13 CARG: "foo" ] [ fw_seq<-1:-1> LBL: h12 ARG0: x3 ARG1: i13 ] [ _thing_n_of-about<0:4> LBL: h4 ARG0: x5 ARG1: i99 ] [ _a_q<0:4> LBL: h6 ARG0: x5 RSTR: h7 BODY: h8 ] [ unknown LBL: h1 ARG: x5 ARG0: e2 ] > HCONS: < h0 qeq h1 h7 qeq h4 h10 qeq h12 > ]
    # SString 2023-05-31 13:41:50,148: sstring: MRS failed, try fallback
    # SString 2023-05-31 13:41:50,148: sstring: Fallback generated: x5[None delphin(arg2):PluralMode.as_is]=thing
    # 'foo' is not in a thing
    #
    # Test: what is in "foo"
    # 'foo' can't contain things
    #
    # Test: "foo" is in "/documents"
    # SString 2023-05-31 13:41:50,734: sstring: tree is: proper_q:0(x10,[quoted:1(\>documents,i15), fw_seq:2(x10,i15)],proper_q:3(x3,[quoted:4(foo,i8), fw_seq:5(x3,i8)],_in_p_loc:6(e2,x3,x10)))
    # SString 2023-05-31 13:41:50,735: sstring: original text is: 'arg1'
    # SString 2023-05-31 13:41:50,735: sstring: plural is: PluralMode.as_is
    # SString 2023-05-31 13:41:50,736: sstring: variable_name is 'x3'
    # SString 2023-05-31 13:41:50,736: sstring: default meaning_at_index is '6'
    # SString 2023-05-31 13:41:50,736: sstring: meaning_at_index not specified, using default: '6'
    # SString 2023-05-31 13:41:50,736: sstring: default meaning_at_index: trying MRS generation
    # SString 2023-05-31 13:41:50,892: Nothing could be generated for: "foo" is in "\>documents": [ TOP: h0 INDEX: e2 [ e SF: prop ] RELS: < [ proper_q<12:25> LBL: h11 ARG0: x10 [ x PERS: 3 NUM: sg ] RSTR: h12 BODY: h13 ] [ quoted<13:24> LBL: h14 ARG0: i15 CARG: "\\>documents" ] [ fw_seq<-1:-1> LBL: h14 ARG0: x10 ARG1: i15 ] [ quoted<1:4> LBL: h7 ARG0: i8 CARG: "foo" ] [ fw_seq<-1:-1> LBL: h7 ARG0: x3 [ x PERS: 3 NUM: sg ] ARG1: i8 ] [ proper_q<0:5> LBL: h4 ARG0: x3 RSTR: h5 BODY: h6 ] [ unknown LBL: h1 ARG: x3 ARG0: e2 ] > HCONS: < h0 qeq h1 h5 qeq h7 h12 qeq h14 > ]
    # SString 2023-05-31 13:41:50,892: sstring: MRS failed, try fallback
    # SString 2023-05-31 13:41:50,893: sstring: Fallback generated: x3[None delphin(arg1):PluralMode.as_is]='foo'
    # SString 2023-05-31 13:41:50,894: sstring: tree is: proper_q:0(x10,[quoted:1(\>documents,i15), fw_seq:2(x10,i15)],proper_q:3(x3,[quoted:4(foo,i8), fw_seq:5(x3,i8)],_in_p_loc:6(e2,x3,x10)))
    # SString 2023-05-31 13:41:50,894: sstring: original text is: 'arg2'
    # SString 2023-05-31 13:41:50,894: sstring: plural is: PluralMode.as_is
    # SString 2023-05-31 13:41:50,895: sstring: variable_name is 'x10'
    # SString 2023-05-31 13:41:50,895: sstring: default meaning_at_index is '3'
    # SString 2023-05-31 13:41:50,895: sstring: meaning_at_index not specified, using default: '3'
    # SString 2023-05-31 13:41:50,895: sstring: default meaning_at_index: trying MRS generation
    # SString 2023-05-31 13:41:51,109: Nothing could be generated for: "foo" is in "\>documents": [ TOP: h0 INDEX: e2 [ e SF: prop ] RELS: < [ quoted<13:24> LBL: h14 ARG0: i15 CARG: "\\>documents" ] [ fw_seq<-1:-1> LBL: h14 ARG0: x10 [ x PERS: 3 NUM: sg ] ARG1: i15 ] [ proper_q<12:25> LBL: h11 ARG0: x10 RSTR: h12 BODY: h13 ] [ unknown LBL: h1 ARG: x10 ARG0: e2 ] > HCONS: < h0 qeq h1 h12 qeq h14 > ]
    # SString 2023-05-31 13:41:51,109: sstring: MRS failed, try fallback
    # SString 2023-05-31 13:41:51,109: sstring: Fallback generated: x10[None delphin(arg2):PluralMode.as_is]='/documents'
    # SString 2023-05-31 13:41:51,127: sstring: tree is: proper_q:0(x3,[quoted:1(foo,i8), fw_seq:2(x3,i8)],proper_q:3(x10,[quoted:4(\>documents,i15), fw_seq:5(x10,i15)],_in_p_loc:6(e2,x3,x10)))
    # SString 2023-05-31 13:41:51,127: sstring: original text is: 'arg1'
    # SString 2023-05-31 13:41:51,127: sstring: plural is: PluralMode.as_is
    # SString 2023-05-31 13:41:51,128: sstring: variable_name is 'x3'
    # SString 2023-05-31 13:41:51,128: sstring: default meaning_at_index is '3'
    # SString 2023-05-31 13:41:51,128: sstring: meaning_at_index not specified, using default: '3'
    # SString 2023-05-31 13:41:51,128: sstring: default meaning_at_index: trying MRS generation
    # SString 2023-05-31 13:41:51,266: Nothing could be generated for: "foo" is in "\>documents": [ TOP: h0 INDEX: e2 [ e SF: prop ] RELS: < [ quoted<1:4> LBL: h7 ARG0: i8 CARG: "foo" ] [ fw_seq<-1:-1> LBL: h7 ARG0: x3 [ x PERS: 3 NUM: sg ] ARG1: i8 ] [ proper_q<0:5> LBL: h4 ARG0: x3 RSTR: h5 BODY: h6 ] [ unknown LBL: h1 ARG: x3 ARG0: e2 ] > HCONS: < h0 qeq h1 h5 qeq h7 > ]
    # SString 2023-05-31 13:41:51,266: sstring: MRS failed, try fallback
    # SString 2023-05-31 13:41:51,266: sstring: Fallback generated: x3[None delphin(arg1):PluralMode.as_is]='foo'
    # SString 2023-05-31 13:41:51,268: sstring: tree is: proper_q:0(x3,[quoted:1(foo,i8), fw_seq:2(x3,i8)],proper_q:3(x10,[quoted:4(\>documents,i15), fw_seq:5(x10,i15)],_in_p_loc:6(e2,x3,x10)))
    # SString 2023-05-31 13:41:51,268: sstring: original text is: 'arg2'
    # SString 2023-05-31 13:41:51,268: sstring: plural is: PluralMode.as_is
    # SString 2023-05-31 13:41:51,269: sstring: variable_name is 'x10'
    # SString 2023-05-31 13:41:51,269: sstring: default meaning_at_index is '6'
    # SString 2023-05-31 13:41:51,269: sstring: meaning_at_index not specified, using default: '6'
    # SString 2023-05-31 13:41:51,269: sstring: default meaning_at_index: trying MRS generation
    # SString 2023-05-31 13:41:51,411: Nothing could be generated for: "foo" is in "\>documents": [ TOP: h0 INDEX: e2 [ e SF: prop ] RELS: < [ proper_q<0:5> LBL: h4 ARG0: x3 [ x PERS: 3 NUM: sg ] RSTR: h5 BODY: h6 ] [ quoted<1:4> LBL: h7 ARG0: i8 CARG: "foo" ] [ fw_seq<-1:-1> LBL: h7 ARG0: x3 ARG1: i8 ] [ quoted<13:24> LBL: h14 ARG0: i15 CARG: "\\>documents" ] [ fw_seq<-1:-1> LBL: h14 ARG0: x10 [ x PERS: 3 NUM: sg ] ARG1: i15 ] [ proper_q<12:25> LBL: h11 ARG0: x10 RSTR: h12 BODY: h13 ] [ unknown LBL: h1 ARG: x10 ARG0: e2 ] > HCONS: < h0 qeq h1 h5 qeq h7 h12 qeq h14 > ]
    # SString 2023-05-31 13:41:51,411: sstring: MRS failed, try fallback
    # SString 2023-05-31 13:41:51,411: sstring: Fallback generated: x10[None delphin(arg2):PluralMode.as_is]='/documents'
    # 'foo' is not in '/documents'
    #
    # Test: where is "doesn't exist"
    # SString 2023-05-31 13:41:51,643: sstring: tree is: which_q:0(x4,place_n:1(x4),proper_q:2(x3,[quoted:3(exist,i14), quoted:4(doesn’t,i13), fw_seq:5(x3,i13,i14)],loc_nonsp:6(e2,x3,x4)))
    # SString 2023-05-31 13:41:51,644: sstring: original text is: 'arg1'
    # SString 2023-05-31 13:41:51,644: sstring: plural is: PluralMode.as_is
    # SString 2023-05-31 13:41:51,645: sstring: variable_name is 'x3'
    # SString 2023-05-31 13:41:51,645: sstring: default meaning_at_index is '6'
    # SString 2023-05-31 13:41:51,645: sstring: meaning_at_index not specified, using default: '6'
    # SString 2023-05-31 13:41:51,645: sstring: default meaning_at_index: trying MRS generation
    # SString 2023-05-31 13:41:51,795: Nothing could be generated for: where is "doesn't exist": [ TOP: h0 INDEX: e2 [ e SF: prop ] RELS: < [ which_q<0:5> LBL: h6 ARG0: x4 [ x PERS: 3 NUM: sg ] RSTR: h7 BODY: h8 ] [ place_n<0:5> LBL: h5 ARG0: x4 ] [ quoted<18:23> LBL: h12 ARG0: i14 CARG: "exist" ] [ quoted<10:17> LBL: h12 ARG0: i13 CARG: "doesn’t" ] [ fw_seq<9:24> LBL: h12 ARG0: x3 [ x PERS: 3 NUM: sg ] ARG1: i13 ARG2: i14 ] [ proper_q<9:24> LBL: h9 ARG0: x3 RSTR: h10 BODY: h11 ] [ unknown LBL: h1 ARG: x3 ARG0: e2 ] > HCONS: < h0 qeq h1 h7 qeq h5 h10 qeq h12 > ]
    # SString 2023-05-31 13:41:51,795: sstring: MRS failed, try fallback
    # SString 2023-05-31 13:41:51,796: sstring: Fallback generated: x3[None delphin(arg1):PluralMode.as_is]='doesn’t exist'
    # SString 2023-05-31 13:41:51,797: sstring: tree is: which_q:0(x4,place_n:1(x4),proper_q:2(x3,[quoted:3(exist,i14), quoted:4(doesn’t,i13), fw_seq:5(x3,i13,i14)],loc_nonsp:6(e2,x3,x4)))
    # SString 2023-05-31 13:41:51,797: sstring: original text is: 'arg2'
    # SString 2023-05-31 13:41:51,797: sstring: plural is: PluralMode.as_is
    # SString 2023-05-31 13:41:51,798: sstring: variable_name is 'x4'
    # SString 2023-05-31 13:41:51,798: sstring: default meaning_at_index is '2'
    # SString 2023-05-31 13:41:51,798: sstring: meaning_at_index not specified, using default: '2'
    # SString 2023-05-31 13:41:51,798: sstring: default meaning_at_index: trying MRS generation
    # SString 2023-05-31 13:41:51,939: Nothing could be generated for: where is "doesn't exist": [ TOP: h0 INDEX: e2 [ e SF: prop ] RELS: < [ place_n<0:5> LBL: h5 ARG0: x4 [ x PERS: 3 NUM: sg ] ] [ _a_q<0:5> LBL: h6 ARG0: x4 RSTR: h7 BODY: h8 ] [ unknown LBL: h1 ARG: x4 ARG0: e2 ] > HCONS: < h0 qeq h1 h7 qeq h5 > ]
    # SString 2023-05-31 13:41:51,940: sstring: MRS failed, try fallback
    # SString 2023-05-31 13:41:51,940: sstring: Fallback generated: x4[None delphin(arg2):PluralMode.as_is]=place
    # SString 2023-05-31 13:41:51,952: sstring: tree is: proper_q:0(x3,[quoted:1(exist,i14), quoted:2(doesn’t,i13), fw_seq:3(x3,i13,i14)],which_q:4(x4,place_n:5(x4),loc_nonsp:6(e2,x3,x4)))
    # SString 2023-05-31 13:41:51,952: sstring: original text is: 'arg1'
    # SString 2023-05-31 13:41:51,953: sstring: plural is: PluralMode.as_is
    # SString 2023-05-31 13:41:51,953: sstring: variable_name is 'x3'
    # SString 2023-05-31 13:41:51,953: sstring: default meaning_at_index is '4'
    # SString 2023-05-31 13:41:51,954: sstring: meaning_at_index not specified, using default: '4'
    # SString 2023-05-31 13:41:51,954: sstring: default meaning_at_index: trying MRS generation
    # SString 2023-05-31 13:41:52,226: Nothing could be generated for: where is "doesn't exist": [ TOP: h0 INDEX: e2 [ e SF: prop ] RELS: < [ quoted<18:23> LBL: h12 ARG0: i14 CARG: "exist" ] [ quoted<10:17> LBL: h12 ARG0: i13 CARG: "doesn’t" ] [ fw_seq<9:24> LBL: h12 ARG0: x3 [ x PERS: 3 NUM: sg ] ARG1: i13 ARG2: i14 ] [ proper_q<9:24> LBL: h9 ARG0: x3 RSTR: h10 BODY: h11 ] [ unknown LBL: h1 ARG: x3 ARG0: e2 ] > HCONS: < h0 qeq h1 h10 qeq h12 > ]
    # SString 2023-05-31 13:41:52,227: sstring: MRS failed, try fallback
    # SString 2023-05-31 13:41:52,227: sstring: Fallback generated: x3[None delphin(arg1):PluralMode.as_is]='doesn’t exist'
    # SString 2023-05-31 13:41:52,229: sstring: tree is: proper_q:0(x3,[quoted:1(exist,i14), quoted:2(doesn’t,i13), fw_seq:3(x3,i13,i14)],which_q:4(x4,place_n:5(x4),loc_nonsp:6(e2,x3,x4)))
    # SString 2023-05-31 13:41:52,229: sstring: original text is: 'arg2'
    # SString 2023-05-31 13:41:52,229: sstring: plural is: PluralMode.as_is
    # SString 2023-05-31 13:41:52,230: sstring: variable_name is 'x4'
    # SString 2023-05-31 13:41:52,230: sstring: default meaning_at_index is '6'
    # SString 2023-05-31 13:41:52,230: sstring: meaning_at_index not specified, using default: '6'
    # SString 2023-05-31 13:41:52,230: sstring: default meaning_at_index: trying MRS generation
    # SString 2023-05-31 13:41:52,376: Nothing could be generated for: where is "doesn't exist": [ TOP: h0 INDEX: e2 [ e SF: prop ] RELS: < [ proper_q<9:24> LBL: h9 ARG0: x3 [ x PERS: 3 NUM: sg ] RSTR: h10 BODY: h11 ] [ quoted<18:23> LBL: h12 ARG0: i14 CARG: "exist" ] [ quoted<10:17> LBL: h12 ARG0: i13 CARG: "doesn’t" ] [ fw_seq<9:24> LBL: h12 ARG0: x3 ARG1: i13 ARG2: i14 ] [ place_n<0:5> LBL: h5 ARG0: x4 [ x PERS: 3 NUM: sg ] ] [ _a_q<0:5> LBL: h6 ARG0: x4 RSTR: h7 BODY: h8 ] [ unknown LBL: h1 ARG: x4 ARG0: e2 ] > HCONS: < h0 qeq h1 h7 qeq h5 h10 qeq h12 > ]
    # SString 2023-05-31 13:41:52,377: sstring: MRS failed, try fallback
    # SString 2023-05-31 13:41:52,377: sstring: Fallback generated: x4[None delphin(arg2):PluralMode.as_is]=place
    # 'doesn’t exist' is not in place
    #
    # Test: /reset
    # State reset using examples.Example23_reset().
    #
    # Test: go to "/documents"
    # You are now in Folder(name=/documents, size=0)
    #
    # Test: what is in this folder?
    # (File(name=/documents/file1.txt, size=1000),)
    #
    # Test: go to "doesn't exist"
    # 'doesn’t exist' was not found
    #
    # Test: /reset
    # State reset using examples.Example23_reset().
    #
    # Test: what is in "/documents"
    # (File(name=/documents/file1.txt, size=1000),)
    #
    # Test: delete "file1.txt" in "/documents"
    # Done!
    #
    # Test: what is in "/documents"
    # SString 2023-05-31 13:41:54,055: sstring: tree is: which_q:0(x3,thing:1(x3),proper_q:2(x8,[quoted:3(\>documents,i13), fw_seq:4(x8,i13)],_in_p_loc:5(e2,x3,x8)))
    # SString 2023-05-31 13:41:54,055: sstring: original text is: 'arg1'
    # SString 2023-05-31 13:41:54,055: sstring: plural is: PluralMode.as_is
    # SString 2023-05-31 13:41:54,056: sstring: variable_name is 'x3'
    # SString 2023-05-31 13:41:54,056: sstring: default meaning_at_index is '2'
    # SString 2023-05-31 13:41:54,056: sstring: meaning_at_index not specified, using default: '2'
    # SString 2023-05-31 13:41:54,056: sstring: default meaning_at_index: trying MRS generation
    # SString 2023-05-31 13:41:54,341: sstring MRS generated: x3[None delphin(arg1):PluralMode.as_is]=a thing
    # SString 2023-05-31 13:41:54,342: sstring: tree is: which_q:0(x3,thing:1(x3),proper_q:2(x8,[quoted:3(\>documents,i13), fw_seq:4(x8,i13)],_in_p_loc:5(e2,x3,x8)))
    # SString 2023-05-31 13:41:54,342: sstring: original text is: 'arg2'
    # SString 2023-05-31 13:41:54,342: sstring: plural is: PluralMode.as_is
    # SString 2023-05-31 13:41:54,343: sstring: variable_name is 'x8'
    # SString 2023-05-31 13:41:54,343: sstring: default meaning_at_index is '5'
    # SString 2023-05-31 13:41:54,343: sstring: meaning_at_index not specified, using default: '5'
    # SString 2023-05-31 13:41:54,343: sstring: default meaning_at_index: trying MRS generation
    # SString 2023-05-31 13:41:54,498: Nothing could be generated for: what is in "\>documents": [ TOP: h0 INDEX: e2 [ e SF: prop ] RELS: < [ _a_q<0:4> LBL: h5 ARG0: x3 [ x PERS: 3 NUM: sg ] RSTR: h6 BODY: h7 ] [ _thing_n_of-about<0:4> LBL: h4 ARG0: x3 ARG1: i99 ] [ quoted<12:23> LBL: h12 ARG0: i13 CARG: "\\>documents" ] [ fw_seq<-1:-1> LBL: h12 ARG0: x8 [ x PERS: 3 NUM: sg ] ARG1: i13 ] [ proper_q<11:24> LBL: h9 ARG0: x8 RSTR: h10 BODY: h11 ] [ unknown LBL: h1 ARG: x8 ARG0: e2 ] > HCONS: < h0 qeq h1 h6 qeq h4 h10 qeq h12 > ]
    # SString 2023-05-31 13:41:54,498: sstring: MRS failed, try fallback
    # SString 2023-05-31 13:41:54,498: sstring: Fallback generated: x8[None delphin(arg2):PluralMode.as_is]='/documents'
    # SString 2023-05-31 13:41:54,511: sstring: tree is: proper_q:0(x8,[quoted:1(\>documents,i13), fw_seq:2(x8,i13)],which_q:3(x3,thing:4(x3),_in_p_loc:5(e2,x3,x8)))
    # SString 2023-05-31 13:41:54,511: sstring: original text is: 'arg1'
    # SString 2023-05-31 13:41:54,511: sstring: plural is: PluralMode.as_is
    # SString 2023-05-31 13:41:54,512: sstring: variable_name is 'x3'
    # SString 2023-05-31 13:41:54,512: sstring: default meaning_at_index is '5'
    # SString 2023-05-31 13:41:54,512: sstring: meaning_at_index not specified, using default: '5'
    # SString 2023-05-31 13:41:54,512: sstring: default meaning_at_index: trying MRS generation
    # SString 2023-05-31 13:41:54,668: Nothing could be generated for: what is in "\>documents": [ TOP: h0 INDEX: e2 [ e SF: prop ] RELS: < [ proper_q<11:24> LBL: h9 ARG0: x8 [ x PERS: 3 NUM: sg ] RSTR: h10 BODY: h11 ] [ quoted<12:23> LBL: h12 ARG0: i13 CARG: "\\>documents" ] [ fw_seq<-1:-1> LBL: h12 ARG0: x8 ARG1: i13 ] [ _thing_n_of-about<0:4> LBL: h4 ARG0: x3 [ x PERS: 3 NUM: sg ] ARG1: i99 ] [ _a_q<0:4> LBL: h5 ARG0: x3 RSTR: h6 BODY: h7 ] [ unknown LBL: h1 ARG: x3 ARG0: e2 ] > HCONS: < h0 qeq h1 h6 qeq h4 h10 qeq h12 > ]
    # SString 2023-05-31 13:41:54,669: sstring: MRS failed, try fallback
    # SString 2023-05-31 13:41:54,669: sstring: Fallback generated: x3[None delphin(arg1):PluralMode.as_is]=thing
    # SString 2023-05-31 13:41:54,670: sstring: tree is: proper_q:0(x8,[quoted:1(\>documents,i13), fw_seq:2(x8,i13)],which_q:3(x3,thing:4(x3),_in_p_loc:5(e2,x3,x8)))
    # SString 2023-05-31 13:41:54,670: sstring: original text is: 'arg2'
    # SString 2023-05-31 13:41:54,670: sstring: plural is: PluralMode.as_is
    # SString 2023-05-31 13:41:54,671: sstring: variable_name is 'x8'
    # SString 2023-05-31 13:41:54,671: sstring: default meaning_at_index is '3'
    # SString 2023-05-31 13:41:54,671: sstring: meaning_at_index not specified, using default: '3'
    # SString 2023-05-31 13:41:54,671: sstring: default meaning_at_index: trying MRS generation
    # SString 2023-05-31 13:41:54,811: Nothing could be generated for: what is in "\>documents": [ TOP: h0 INDEX: e2 [ e SF: prop ] RELS: < [ quoted<12:23> LBL: h12 ARG0: i13 CARG: "\\>documents" ] [ fw_seq<-1:-1> LBL: h12 ARG0: x8 [ x PERS: 3 NUM: sg ] ARG1: i13 ] [ proper_q<11:24> LBL: h9 ARG0: x8 RSTR: h10 BODY: h11 ] [ unknown LBL: h1 ARG: x8 ARG0: e2 ] > HCONS: < h0 qeq h1 h10 qeq h12 > ]
    # SString 2023-05-31 13:41:54,811: sstring: MRS failed, try fallback
    # SString 2023-05-31 13:41:54,811: sstring: Fallback generated: x8[None delphin(arg2):PluralMode.as_is]='/documents'
    # a thing is not in '/documents'
    #
    # Test: /reset
    # State reset using examples.Example23_reset().
    #
    # Test: what is in this folder?
    # (File(name=/Desktop/the yearly budget.txt, size=10000000),)
    # (there are more)
    #
    # Test: copy "file1.txt" in "/documents"
    # Done!
    #
    # Test: "file1.txt" is in this folder
    # Yes, that is true.
    #
    # Test: /reset
    # State reset using examples.Example23_reset().
    #
    # Test: what is in "\>root111"
    # (Folder(name=/documents, size=0),)
    # (there are more)
    #
    # Test: /new examples.Example24_reset
    # State reset using examples.Example24_reset().
    #
    # Test: copy "\>temp\>59.txt" in "\>documents"
    # SString 2023-05-31 13:41:57,184: sstring: tree is: proper_q:0(x16,[quoted:1(\>documents,i21), fw_seq:2(x16,i21)],pronoun_q:3(x3,pron:4(x3),proper_q:5(x8,[quoted:6(\>temp\>59.txt,i13), fw_seq:7(x8,i13), _in_p_loc:8(e15,x8,x16)],_copy_v_1:9(e2,x3,x8))))
    # SString 2023-05-31 13:41:57,184: sstring: original text is: 'a arg1:sg'
    # SString 2023-05-31 13:41:57,185: sstring: plural is: PluralMode.singular
    # SString 2023-05-31 13:41:57,185: sstring: variable_name is '['AtPredication', _copy_v_1(e2,x3,x8), 'x8']'
    # SString 2023-05-31 13:41:57,186: sstring: variable is complex: '['AtPredication', _copy_v_1(e2,x3,x8), 'x8']'
    # SString 2023-05-31 13:41:57,186: sstring: error predication index is: 9
    # SString 2023-05-31 13:41:57,186: sstring: default meaning_at_index is '8'
    # SString 2023-05-31 13:41:57,186: sstring: meaning_at_index specified by complex variable: 9
    # SString 2023-05-31 13:41:57,186: sstring: non-default meaning_at_index: only use fallback
    # SString 2023-05-31 13:41:57,186: sstring: MRS failed, try fallback
    # SString 2023-05-31 13:41:57,186: sstring: Fallback generated: x8[a delphin(arg1):PluralMode.singular]=a '/temp/59.txt' in '/documents'
    # SString 2023-05-31 13:41:57,220: sstring: tree is: proper_q:0(x16,[quoted:1(\>documents,i21), fw_seq:2(x16,i21)],proper_q:3(x8,[quoted:4(\>temp\>59.txt,i13), fw_seq:5(x8,i13), _in_p_loc:6(e15,x8,x16)],pronoun_q:7(x3,pron:8(x3),_copy_v_1:9(e2,x3,x8))))
    # SString 2023-05-31 13:41:57,220: sstring: original text is: 'a arg1:sg'
    # SString 2023-05-31 13:41:57,220: sstring: plural is: PluralMode.singular
    # SString 2023-05-31 13:41:57,221: sstring: variable_name is '['AtPredication', pronoun_q(x3,pron(x3),_copy_v_1(e2,x3,x8)), 'x8']'
    # SString 2023-05-31 13:41:57,221: sstring: variable is complex: '['AtPredication', pronoun_q(x3,pron(x3),_copy_v_1(e2,x3,x8)), 'x8']'
    # SString 2023-05-31 13:41:57,221: sstring: error predication index is: 7
    # SString 2023-05-31 13:41:57,221: sstring: default meaning_at_index is '6'
    # SString 2023-05-31 13:41:57,221: sstring: meaning_at_index specified by complex variable: 7
    # SString 2023-05-31 13:41:57,222: sstring: non-default meaning_at_index: only use fallback
    # SString 2023-05-31 13:41:57,222: sstring: MRS failed, try fallback
    # SString 2023-05-31 13:41:57,222: sstring: Fallback generated: x8[a delphin(arg1):PluralMode.singular]=a '/temp/59.txt' in '/documents'
    # SString 2023-05-31 13:41:57,274: sstring: tree is: pronoun_q:0(x3,pron:1(x3),proper_q:2(x16,[quoted:3(\>documents,i21), fw_seq:4(x16,i21)],proper_q:5(x8,[quoted:6(\>temp\>59.txt,i13), fw_seq:7(x8,i13), _in_p_loc:8(e15,x8,x16)],_copy_v_1:9(e2,x3,x8))))
    # SString 2023-05-31 13:41:57,274: sstring: original text is: 'a arg1:sg'
    # SString 2023-05-31 13:41:57,274: sstring: plural is: PluralMode.singular
    # SString 2023-05-31 13:41:57,275: sstring: variable_name is '['AtPredication', _copy_v_1(e2,x3,x8), 'x8']'
    # SString 2023-05-31 13:41:57,275: sstring: variable is complex: '['AtPredication', _copy_v_1(e2,x3,x8), 'x8']'
    # SString 2023-05-31 13:41:57,275: sstring: error predication index is: 9
    # SString 2023-05-31 13:41:57,275: sstring: default meaning_at_index is '8'
    # SString 2023-05-31 13:41:57,275: sstring: meaning_at_index specified by complex variable: 9
    # SString 2023-05-31 13:41:57,275: sstring: non-default meaning_at_index: only use fallback
    # SString 2023-05-31 13:41:57,275: sstring: MRS failed, try fallback
    # SString 2023-05-31 13:41:57,276: sstring: Fallback generated: x8[a delphin(arg1):PluralMode.singular]=a '/temp/59.txt' in '/documents'
    # SString 2023-05-31 13:41:57,323: sstring: tree is: pronoun_q:0(x3,pron:1(x3),proper_q:2(x8,proper_q:3(x16,[quoted:4(\>documents,i21), fw_seq:5(x16,i21)],[quoted:6(\>temp\>59.txt,i13), fw_seq:7(x8,i13), _in_p_loc:8(e15,x8,x16)]),_copy_v_1:9(e2,x3,x8)))
    # SString 2023-05-31 13:41:57,323: sstring: original text is: 'a arg1:sg'
    # SString 2023-05-31 13:41:57,324: sstring: plural is: PluralMode.singular
    # SString 2023-05-31 13:41:57,324: sstring: variable_name is '['AtPredication', _copy_v_1(e2,x3,x8), 'x8']'
    # SString 2023-05-31 13:41:57,324: sstring: variable is complex: '['AtPredication', _copy_v_1(e2,x3,x8), 'x8']'
    # SString 2023-05-31 13:41:57,324: sstring: error predication index is: 9
    # SString 2023-05-31 13:41:57,324: sstring: default meaning_at_index is '8'
    # SString 2023-05-31 13:41:57,324: sstring: meaning_at_index specified by complex variable: 9
    # SString 2023-05-31 13:41:57,325: sstring: non-default meaning_at_index: only use fallback
    # SString 2023-05-31 13:41:57,325: sstring: MRS failed, try fallback
    # SString 2023-05-31 13:41:57,325: sstring: Fallback generated: x8[a delphin(arg1):PluralMode.singular]=a '/temp/59.txt' in '/documents'
    # SString 2023-05-31 13:41:57,360: sstring: tree is: proper_q:0(x8,proper_q:1(x16,[quoted:2(\>documents,i21), fw_seq:3(x16,i21)],[quoted:4(\>temp\>59.txt,i13), fw_seq:5(x8,i13), _in_p_loc:6(e15,x8,x16)]),pronoun_q:7(x3,pron:8(x3),_copy_v_1:9(e2,x3,x8)))
    # SString 2023-05-31 13:41:57,360: sstring: original text is: 'a arg1:sg'
    # SString 2023-05-31 13:41:57,360: sstring: plural is: PluralMode.singular
    # SString 2023-05-31 13:41:57,361: sstring: variable_name is '['AtPredication', pronoun_q(x3,pron(x3),_copy_v_1(e2,x3,x8)), 'x8']'
    # SString 2023-05-31 13:41:57,361: sstring: variable is complex: '['AtPredication', pronoun_q(x3,pron(x3),_copy_v_1(e2,x3,x8)), 'x8']'
    # SString 2023-05-31 13:41:57,361: sstring: error predication index is: 7
    # SString 2023-05-31 13:41:57,361: sstring: default meaning_at_index is '6'
    # SString 2023-05-31 13:41:57,361: sstring: meaning_at_index specified by complex variable: 7
    # SString 2023-05-31 13:41:57,361: sstring: non-default meaning_at_index: only use fallback
    # SString 2023-05-31 13:41:57,362: sstring: MRS failed, try fallback
    # SString 2023-05-31 13:41:57,362: sstring: Fallback generated: x8[a delphin(arg1):PluralMode.singular]=a '/temp/59.txt' in '/documents'
    # Done!
    #
    # Test: "59.txt" is in this folder
    # Yes, that is true.
    #
    # Test: /new examples.Example23_reset
    # State reset using examples.Example23_reset().
    #
    # Test: what is in '\>documents'
    # (File(name=/documents/file1.txt, size=1000),)
    #
    # Test: what is in this folder?
    # (File(name=/Desktop/the yearly budget.txt, size=10000000),)
    # (there are more)
    #
    # Test: copy 'blue' in '\>documents'
    # SString 2023-05-31 13:41:59,002: sstring: tree is: proper_q:0(x16,[quoted:1(\>documents,i21), fw_seq:2(x16,i21)],pronoun_q:3(x3,pron:4(x3),proper_q:5(x8,[quoted:6(blue,i13), fw_seq:7(x8,i13), _in_p_loc:8(e15,x8,x16)],_copy_v_1:9(e2,x3,x8))))
    # SString 2023-05-31 13:41:59,002: sstring: original text is: 'a arg1:sg'
    # SString 2023-05-31 13:41:59,002: sstring: plural is: PluralMode.singular
    # SString 2023-05-31 13:41:59,003: sstring: variable_name is '['AtPredication', _copy_v_1(e2,x3,x8), 'x8']'
    # SString 2023-05-31 13:41:59,003: sstring: variable is complex: '['AtPredication', _copy_v_1(e2,x3,x8), 'x8']'
    # SString 2023-05-31 13:41:59,003: sstring: error predication index is: 9
    # SString 2023-05-31 13:41:59,003: sstring: default meaning_at_index is '8'
    # SString 2023-05-31 13:41:59,003: sstring: meaning_at_index specified by complex variable: 9
    # SString 2023-05-31 13:41:59,003: sstring: non-default meaning_at_index: only use fallback
    # SString 2023-05-31 13:41:59,003: sstring: MRS failed, try fallback
    # SString 2023-05-31 13:41:59,003: sstring: Fallback generated: x8[a delphin(arg1):PluralMode.singular]=a 'blue' in '/documents'
    # SString 2023-05-31 13:41:59,037: sstring: tree is: proper_q:0(x16,[quoted:1(\>documents,i21), fw_seq:2(x16,i21)],proper_q:3(x8,[quoted:4(blue,i13), fw_seq:5(x8,i13), _in_p_loc:6(e15,x8,x16)],pronoun_q:7(x3,pron:8(x3),_copy_v_1:9(e2,x3,x8))))
    # SString 2023-05-31 13:41:59,037: sstring: original text is: 'a arg1:sg'
    # SString 2023-05-31 13:41:59,037: sstring: plural is: PluralMode.singular
    # SString 2023-05-31 13:41:59,037: sstring: variable_name is '['AtPredication', pronoun_q(x3,pron(x3),_copy_v_1(e2,x3,x8)), 'x8']'
    # SString 2023-05-31 13:41:59,038: sstring: variable is complex: '['AtPredication', pronoun_q(x3,pron(x3),_copy_v_1(e2,x3,x8)), 'x8']'
    # SString 2023-05-31 13:41:59,038: sstring: error predication index is: 7
    # SString 2023-05-31 13:41:59,038: sstring: default meaning_at_index is '6'
    # SString 2023-05-31 13:41:59,038: sstring: meaning_at_index specified by complex variable: 7
    # SString 2023-05-31 13:41:59,038: sstring: non-default meaning_at_index: only use fallback
    # SString 2023-05-31 13:41:59,038: sstring: MRS failed, try fallback
    # SString 2023-05-31 13:41:59,038: sstring: Fallback generated: x8[a delphin(arg1):PluralMode.singular]=a 'blue' in '/documents'
    # SString 2023-05-31 13:41:59,089: sstring: tree is: pronoun_q:0(x3,pron:1(x3),proper_q:2(x16,[quoted:3(\>documents,i21), fw_seq:4(x16,i21)],proper_q:5(x8,[quoted:6(blue,i13), fw_seq:7(x8,i13), _in_p_loc:8(e15,x8,x16)],_copy_v_1:9(e2,x3,x8))))
    # SString 2023-05-31 13:41:59,089: sstring: original text is: 'a arg1:sg'
    # SString 2023-05-31 13:41:59,089: sstring: plural is: PluralMode.singular
    # SString 2023-05-31 13:41:59,090: sstring: variable_name is '['AtPredication', _copy_v_1(e2,x3,x8), 'x8']'
    # SString 2023-05-31 13:41:59,090: sstring: variable is complex: '['AtPredication', _copy_v_1(e2,x3,x8), 'x8']'
    # SString 2023-05-31 13:41:59,090: sstring: error predication index is: 9
    # SString 2023-05-31 13:41:59,090: sstring: default meaning_at_index is '8'
    # SString 2023-05-31 13:41:59,090: sstring: meaning_at_index specified by complex variable: 9
    # SString 2023-05-31 13:41:59,090: sstring: non-default meaning_at_index: only use fallback
    # SString 2023-05-31 13:41:59,090: sstring: MRS failed, try fallback
    # SString 2023-05-31 13:41:59,091: sstring: Fallback generated: x8[a delphin(arg1):PluralMode.singular]=a 'blue' in '/documents'
    # SString 2023-05-31 13:41:59,136: sstring: tree is: pronoun_q:0(x3,pron:1(x3),proper_q:2(x8,proper_q:3(x16,[quoted:4(\>documents,i21), fw_seq:5(x16,i21)],[quoted:6(blue,i13), fw_seq:7(x8,i13), _in_p_loc:8(e15,x8,x16)]),_copy_v_1:9(e2,x3,x8)))
    # SString 2023-05-31 13:41:59,136: sstring: original text is: 'a arg1:sg'
    # SString 2023-05-31 13:41:59,136: sstring: plural is: PluralMode.singular
    # SString 2023-05-31 13:41:59,137: sstring: variable_name is '['AtPredication', _copy_v_1(e2,x3,x8), 'x8']'
    # SString 2023-05-31 13:41:59,137: sstring: variable is complex: '['AtPredication', _copy_v_1(e2,x3,x8), 'x8']'
    # SString 2023-05-31 13:41:59,137: sstring: error predication index is: 9
    # SString 2023-05-31 13:41:59,137: sstring: default meaning_at_index is '8'
    # SString 2023-05-31 13:41:59,137: sstring: meaning_at_index specified by complex variable: 9
    # SString 2023-05-31 13:41:59,137: sstring: non-default meaning_at_index: only use fallback
    # SString 2023-05-31 13:41:59,137: sstring: MRS failed, try fallback
    # SString 2023-05-31 13:41:59,138: sstring: Fallback generated: x8[a delphin(arg1):PluralMode.singular]=a 'blue' in '/documents'
    # SString 2023-05-31 13:41:59,172: sstring: tree is: proper_q:0(x8,proper_q:1(x16,[quoted:2(\>documents,i21), fw_seq:3(x16,i21)],[quoted:4(blue,i13), fw_seq:5(x8,i13), _in_p_loc:6(e15,x8,x16)]),pronoun_q:7(x3,pron:8(x3),_copy_v_1:9(e2,x3,x8)))
    # SString 2023-05-31 13:41:59,172: sstring: original text is: 'a arg1:sg'
    # SString 2023-05-31 13:41:59,172: sstring: plural is: PluralMode.singular
    # SString 2023-05-31 13:41:59,173: sstring: variable_name is '['AtPredication', pronoun_q(x3,pron(x3),_copy_v_1(e2,x3,x8)), 'x8']'
    # SString 2023-05-31 13:41:59,173: sstring: variable is complex: '['AtPredication', pronoun_q(x3,pron(x3),_copy_v_1(e2,x3,x8)), 'x8']'
    # SString 2023-05-31 13:41:59,173: sstring: error predication index is: 7
    # SString 2023-05-31 13:41:59,173: sstring: default meaning_at_index is '6'
    # SString 2023-05-31 13:41:59,173: sstring: meaning_at_index specified by complex variable: 7
    # SString 2023-05-31 13:41:59,173: sstring: non-default meaning_at_index: only use fallback
    # SString 2023-05-31 13:41:59,173: sstring: MRS failed, try fallback
    # SString 2023-05-31 13:41:59,173: sstring: Fallback generated: x8[a delphin(arg1):PluralMode.singular]=a 'blue' in '/documents'
    # Done!
    #
    # Test: 'blue' is in '\>documents'
    # SString 2023-05-31 13:41:59,594: sstring: tree is: proper_q:0(x10,[quoted:1(\>documents,i15), fw_seq:2(x10,i15)],proper_q:3(x3,[quoted:4(blue,i8), fw_seq:5(x3,i8)],_in_p_loc:6(e2,x3,x10)))
    # SString 2023-05-31 13:41:59,594: sstring: original text is: 'arg1'
    # SString 2023-05-31 13:41:59,595: sstring: plural is: PluralMode.as_is
    # SString 2023-05-31 13:41:59,595: sstring: variable_name is 'x3'
    # SString 2023-05-31 13:41:59,595: sstring: default meaning_at_index is '6'
    # SString 2023-05-31 13:41:59,596: sstring: meaning_at_index not specified, using default: '6'
    # SString 2023-05-31 13:41:59,596: sstring: default meaning_at_index: trying MRS generation
    # SString 2023-05-31 13:41:59,791: Nothing could be generated for: 'blue' is in '\>documents': [ TOP: h0 INDEX: e2 [ e SF: prop ] RELS: < [ proper_q<13:26> LBL: h11 ARG0: x10 [ x PERS: 3 NUM: sg ] RSTR: h12 BODY: h13 ] [ quoted<14:25> LBL: h14 ARG0: i15 CARG: "\\>documents" ] [ fw_seq<-1:-1> LBL: h14 ARG0: x10 ARG1: i15 ] [ quoted<1:5> LBL: h7 ARG0: i8 CARG: "blue" ] [ fw_seq<-1:-1> LBL: h7 ARG0: x3 [ x PERS: 3 NUM: sg ] ARG1: i8 ] [ proper_q<0:6> LBL: h4 ARG0: x3 RSTR: h5 BODY: h6 ] [ unknown LBL: h1 ARG: x3 ARG0: e2 ] > HCONS: < h0 qeq h1 h5 qeq h7 h12 qeq h14 > ]
    # SString 2023-05-31 13:41:59,791: sstring: MRS failed, try fallback
    # SString 2023-05-31 13:41:59,792: sstring: Fallback generated: x3[None delphin(arg1):PluralMode.as_is]='blue'
    # SString 2023-05-31 13:41:59,793: sstring: tree is: proper_q:0(x10,[quoted:1(\>documents,i15), fw_seq:2(x10,i15)],proper_q:3(x3,[quoted:4(blue,i8), fw_seq:5(x3,i8)],_in_p_loc:6(e2,x3,x10)))
    # SString 2023-05-31 13:41:59,793: sstring: original text is: 'arg2'
    # SString 2023-05-31 13:41:59,793: sstring: plural is: PluralMode.as_is
    # SString 2023-05-31 13:41:59,794: sstring: variable_name is 'x10'
    # SString 2023-05-31 13:41:59,794: sstring: default meaning_at_index is '3'
    # SString 2023-05-31 13:41:59,794: sstring: meaning_at_index not specified, using default: '3'
    # SString 2023-05-31 13:41:59,794: sstring: default meaning_at_index: trying MRS generation
    # SString 2023-05-31 13:41:59,932: Nothing could be generated for: 'blue' is in '\>documents': [ TOP: h0 INDEX: e2 [ e SF: prop ] RELS: < [ quoted<14:25> LBL: h14 ARG0: i15 CARG: "\\>documents" ] [ fw_seq<-1:-1> LBL: h14 ARG0: x10 [ x PERS: 3 NUM: sg ] ARG1: i15 ] [ proper_q<13:26> LBL: h11 ARG0: x10 RSTR: h12 BODY: h13 ] [ unknown LBL: h1 ARG: x10 ARG0: e2 ] > HCONS: < h0 qeq h1 h12 qeq h14 > ]
    # SString 2023-05-31 13:41:59,933: sstring: MRS failed, try fallback
    # SString 2023-05-31 13:41:59,933: sstring: Fallback generated: x10[None delphin(arg2):PluralMode.as_is]='/documents'
    # SString 2023-05-31 13:41:59,964: sstring: tree is: proper_q:0(x3,[quoted:1(blue,i8), fw_seq:2(x3,i8)],proper_q:3(x10,[quoted:4(\>documents,i15), fw_seq:5(x10,i15)],_in_p_loc:6(e2,x3,x10)))
    # SString 2023-05-31 13:41:59,964: sstring: original text is: 'arg1'
    # SString 2023-05-31 13:41:59,964: sstring: plural is: PluralMode.as_is
    # SString 2023-05-31 13:41:59,965: sstring: variable_name is 'x3'
    # SString 2023-05-31 13:41:59,965: sstring: default meaning_at_index is '3'
    # SString 2023-05-31 13:41:59,965: sstring: meaning_at_index not specified, using default: '3'
    # SString 2023-05-31 13:41:59,965: sstring: default meaning_at_index: trying MRS generation
    # SString 2023-05-31 13:42:00,102: Nothing could be generated for: 'blue' is in '\>documents': [ TOP: h0 INDEX: e2 [ e SF: prop ] RELS: < [ quoted<1:5> LBL: h7 ARG0: i8 CARG: "blue" ] [ fw_seq<-1:-1> LBL: h7 ARG0: x3 [ x PERS: 3 NUM: sg ] ARG1: i8 ] [ proper_q<0:6> LBL: h4 ARG0: x3 RSTR: h5 BODY: h6 ] [ unknown LBL: h1 ARG: x3 ARG0: e2 ] > HCONS: < h0 qeq h1 h5 qeq h7 > ]
    # SString 2023-05-31 13:42:00,102: sstring: MRS failed, try fallback
    # SString 2023-05-31 13:42:00,103: sstring: Fallback generated: x3[None delphin(arg1):PluralMode.as_is]='blue'
    # SString 2023-05-31 13:42:00,104: sstring: tree is: proper_q:0(x3,[quoted:1(blue,i8), fw_seq:2(x3,i8)],proper_q:3(x10,[quoted:4(\>documents,i15), fw_seq:5(x10,i15)],_in_p_loc:6(e2,x3,x10)))
    # SString 2023-05-31 13:42:00,104: sstring: original text is: 'arg2'
    # SString 2023-05-31 13:42:00,104: sstring: plural is: PluralMode.as_is
    # SString 2023-05-31 13:42:00,105: sstring: variable_name is 'x10'
    # SString 2023-05-31 13:42:00,105: sstring: default meaning_at_index is '6'
    # SString 2023-05-31 13:42:00,105: sstring: meaning_at_index not specified, using default: '6'
    # SString 2023-05-31 13:42:00,105: sstring: default meaning_at_index: trying MRS generation
    # SString 2023-05-31 13:42:00,386: Nothing could be generated for: 'blue' is in '\>documents': [ TOP: h0 INDEX: e2 [ e SF: prop ] RELS: < [ proper_q<0:6> LBL: h4 ARG0: x3 [ x PERS: 3 NUM: sg ] RSTR: h5 BODY: h6 ] [ quoted<1:5> LBL: h7 ARG0: i8 CARG: "blue" ] [ fw_seq<-1:-1> LBL: h7 ARG0: x3 ARG1: i8 ] [ quoted<14:25> LBL: h14 ARG0: i15 CARG: "\\>documents" ] [ fw_seq<-1:-1> LBL: h14 ARG0: x10 [ x PERS: 3 NUM: sg ] ARG1: i15 ] [ proper_q<13:26> LBL: h11 ARG0: x10 RSTR: h12 BODY: h13 ] [ unknown LBL: h1 ARG: x10 ARG0: e2 ] > HCONS: < h0 qeq h1 h5 qeq h7 h12 qeq h14 > ]
    # SString 2023-05-31 13:42:00,386: sstring: MRS failed, try fallback
    # SString 2023-05-31 13:42:00,387: sstring: Fallback generated: x10[None delphin(arg2):PluralMode.as_is]='/documents'
    # 'blue' is not in '/documents'
    #
    # Expected: File(name=/documents/file1.txt, size=1000)
    # File(name=/documents/blue, size=1000)
    #
    # (<enter>)ignore, (b)reak to end testing, (u)pdate test, (d)isable test
    ShowLogging("SString")
    # ShowLogging("Determiners")
    # ShowLogging("SolutionGroups")

    # Early examples need a context to set the vocabulary since
    # respond_to_mrs hadn't been built yet
    with ExecutionContext(vocabulary):
        execution_context()._phrase_type = "prop"
        # Example1()
        # Example2()
        # Example3()
        # Example4()
        # Example5()
        # Example5_1()
        # Example5_2()
        # Example6()
    # Example6a()
    # Example6b()
    #     Example7()
    #     Example8()
    #     Example9()
    #     Example10()
    #     Example11()
    #     Example12()
    #     Example13()
    #     Example14()
    #     Example15()

    # Example16()
    # Example17()
    # Example18()
    # Example19()
    # Example20()
    # Example21()
    # Example22()
    # Example23()
    # Example24()
    Example25()
    # Example26()
    # Example27()
    # Example28()
    # Example29()
    # Example30()
    # Example31()
    # Example32()
    # Example33()
    # Example33_performance_test()
    # Example34()
    # Example35()
    # Example36()
    #
    # state_test()

    # import cProfile
    # cProfile.run('Example33_performance_test()', '/Users/ericzinda/Enlistments/perf.bin')
    # stats = pstats.Stats('/Users/ericzinda/Enlistments/perf.bin')
    # stats.sort_stats("tottime")
    # stats.print_stats(.05)

    # with open('/Users/ericzinda/Enlistments/perf.txt', 'w') as f:
    #     stats = pstats.Stats('/Users/ericzinda/Enlistments/perf.bin', stream=f)
    #     stats.get_stats_profile()
    #     stats.print_stats()

