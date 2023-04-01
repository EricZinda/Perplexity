from file_system_example.messages import respond_to_mrs_tree, error_priority
from file_system_example.objects import Folder, File, Actor, FileSystemMock
from file_system_example.state import State, FileSystemState
from file_system_example.vocabulary2 import vocabulary
from perplexity.execution import ExecutionContext, call, execution_context
from perplexity.generation import english_for_delphin_variable

##########################
# Helpers that allow the examples to use
# old interfaces in the early parts of the docs
##########################
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
    user_interface = UserInterface(Example16_reset, vocabulary, respond_to_mrs_tree)

    while True:
        user_interface.interact_once()
        print()


def Example17():
    def reset():
        return State([Folder(name="Desktop"),
                      Folder(name="Documents")])

    user_interface = UserInterface(reset, vocabulary, None)

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
    user_interface = UserInterface(Example18_reset, vocabulary, respond_to_mrs_tree)

    while True:
        user_interface.interact_once()
        print()


def Example19_reset():
    return FileSystemState(FileSystemMock([(True, "/documents/file1.txt", {"size": 1000000}),
                                           (False, "/Desktop", {})],
                                          "/documents"))


def Example19():
    # ShowLogging("Pipeline")
    user_interface = UserInterface(Example19_reset, vocabulary, respond_to_mrs_tree)

    while True:
        user_interface.interact_once()
        print()


def Example20_reset():
    return FileSystemState(FileSystemMock([(True, "/documents/file1.txt", {"size": 1000}),
                                           (False, "/Desktop", {})],
                                          "/Desktop"))


def Example20():
    user_interface = UserInterface(Example20_reset, vocabulary, respond_to_mrs_tree, error_priority)

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
    user_interface = UserInterface(Example21_reset, vocabulary, respond_to_mrs_tree, error_priority)

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
    user_interface = UserInterface(Example22_reset, vocabulary, respond_to_mrs_tree, error_priority)

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
    user_interface = UserInterface(Example23_reset, vocabulary, respond_to_mrs_tree, error_priority)

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
    user_interface = UserInterface(Example24_reset, vocabulary, respond_to_mrs_tree, error_priority)

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
    user_interface = UserInterface(Example25_reset, vocabulary, respond_to_mrs_tree, error_priority)

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
    user_interface = UserInterface(Example26_reset, vocabulary, respond_to_mrs_tree, error_priority)

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
    user_interface = UserInterface(Example27_reset, vocabulary, respond_to_mrs_tree, error_priority)

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
    user_interface = UserInterface(Example28_reset, vocabulary, respond_to_mrs_tree, error_priority)

    while True:
        user_interface.interact_once()
        print()


def Example29_reset():
    return FileSystemState(FileSystemMock([(True, "/Desktop/file2.txt", {"size": 10000000}),
                                           (True, "/Desktop/file3.txt", {"size": 10000000})],
                                          "/Desktop"))


def Example29():
    user_interface = UserInterface(Example29_reset, vocabulary, respond_to_mrs_tree, error_priority)

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
    user_interface = UserInterface(Example30_reset, vocabulary, respond_to_mrs_tree, error_priority)

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
    user_interface = UserInterface(Example31_reset, vocabulary, respond_to_mrs_tree, error_priority)

    while True:
        user_interface.interact_once()
        print()


def Example32_reset():
    return FileSystemState(FileSystemMock([(True, "/Desktop/file2.txt", {"size": 10000000}),
                                           (True, "/documents/file5.txt", {"size": 10000000})],
                                           "/Desktop"))


def Example32():
    user_interface = UserInterface(Example32_reset, vocabulary, respond_to_mrs_tree, error_priority)

    while True:
        user_interface.interact_once()
        print()


if __name__ == '__main__':
    ShowLogging("Execution")
    ShowLogging("Generation")
    ShowLogging("UserInterface")
    ShowLogging("Pipeline")

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
    Example20()
    # Example21()
    # Example22()
    # Example24()
    # Example25()
    # Example26()
    # Example27()
    # Example28()
    # Example29()
    # Example30()
    # Example31()
    # Example32()