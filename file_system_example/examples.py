from file_system_example.messages import respond_to_mrs_tree
from file_system_example.objects import Folder, File, Actor
from file_system_example.state import State
from file_system_example.vocabulary import folder_n_of, vocabulary
from perplexity.execution import ExecutionContext, call, execution_context
from perplexity.generation import english_for_delphin_variable

##########################
# Helpers that allow the examples to use
# old interfaces in the early parts of the docs
##########################
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

# List all folders
def Example1():
    state = State([Folder(name="Desktop"),
                   Folder(name="Documents"),
                   File(name="file1.txt"),
                   File(name="file2.txt")])

    for item in folder_n_of(state, "x1", None):
        print(item.variables)

    print("\nThe original `state` object is not changed:")
    print(state.variables)


# List folders using call_predication
def Example2():
    state = State([Folder(name="Desktop"),
                   Folder(name="Documents"),
                   File(name="file1.txt"),
                   File(name="file2.txt")])

    for item in call_predication(state,
                                 ["_folder_n_of", "x1", "i1"]):
        print(item.variables)


# "Large files" using a conjunction
def Example3():
    state = State([Folder(name="Desktop"),
                   Folder(name="Documents"),
                   File(name="file1.txt", size=100),
                   File(name="file2.txt", size=2000000)])
    
    mrs = [["_large_a_1", "e1", "x1"], ["_file_n_of", "x1", "i1"]]
    
    for item in call(state, mrs):
        print(item.variables)


# "a" large file in a world with two large files
def Example4():
    # Note that both files are "large" now
    state = State([Folder(name="Desktop"),
                   Folder(name="Documents"),
                   File(name="file1.txt", size=2000000),
                   File(name="file2.txt", size=2000000)])

    mrs = ["_a_q", "x3", ["_file_n_of", "x3", "i1"], ["_large_a_1", "e2", "x3"]]

    for item in call(state, mrs):
        print(item.variables)


# Evaluate the proposition: "a file is large" when there is one
def Example5():
    state = State([Folder(name="Desktop"),
                   Folder(name="Documents"),
                   File(name="file1.txt", size=2000000),
                   File(name="file2.txt", size=2000000)])
    
    # Start with an empty dictionary
    mrs = {}

    # Set its "index" key to the value "e1"
    mrs["Index"] = "e1"

    # Set its "Variables" key to *another* dictionary with
    # two keys: "x1" and "e1". Each of those has a "value" of
    # yet another dictionary that holds the properties of the variables
    mrs["Variables"] = {"x1": {"NUM": "pl"},
                        "e1": {"SF": "prop"}}

    # Set the "Tree" key to the scope-resolved MRS tree, using our format
    mrs["Tree"] = [["_a_q", "x1", ["_file_n_of", "x1", "i1"], ["_large_a_1", "e1", "x1"]]]

    print(solve_and_respond(state, mrs))


# Evaluate the proposition: "a file is large" when there isn't a large one
def Example5_1():
    state = State([Folder(name="Desktop"),
                   Folder(name="Documents"),
                   File(name="file1.txt", size=200),
                   File(name="file2.txt", size=200)])
    # Start with an empty dictionary
    mrs = {}

    # Set its "index" key to the value "e1"
    mrs["Index"] = "e1"

    # Set its "Variables" key to *another* dictionary with
    # two keys: "x1" and "e1". Each of those has a "value" of
    # yet another dictionary that holds the properties of the variables
    mrs["Variables"] = {"x1": {"NUM": "pl"},
                        "e1": {"SF": "prop"}}

    # Set the "Tree" key to the scope-resolved MRS tree, using our format
    mrs["Tree"] = [["_a_q", "x1", ["_file_n_of", "x1", "i1"], ["_large_a_1", "e1", "x1"]]]

    print(solve_and_respond(state, mrs))


# Evaluate the proposition: "a file is large" when there isn't a large one
def Example5_2():
    state = State([Folder(name="Desktop"),
                   Folder(name="Documents")])
    # Start with an empty dictionary
    mrs = {}
    # Set its "index" key to the value "e1"
    mrs["Index"] = "e1"
    # Set its "Variables" key to *another* dictionary with
    # two keys: "x1" and "e1". Each of those has a "value" of
    # yet another dictionary that holds the properties of the variables
    mrs["Variables"] = {"x1": {"NUM": "pl"},
                        "e1": {"SF": "prop"}}
    # Set the "Tree" key to the scope-resolved MRS tree, using our format
    mrs["Tree"] = [["_a_q", "x1", ["_file_n_of", "x1", "i1"], ["_large_a_1", "e1", "x1"]]]

    print(solve_and_respond(state, mrs))


# Evaluate the proposition: "which file is large?"
def Example6():
    state = State([Folder(name="Desktop"),
                   Folder(name="Documents"),
                   File(name="file1.txt", size=2000000),
                   File(name="file2.txt", size=1000000)])

    mrs = {}
    mrs["Index"] = "e1"
    mrs["Variables"] = {"x1": {"NUM": "sg"},
                        "e1": {"SF": "ques"}}
    mrs["Tree"] = [["_which_q", "x1", ["_file_n_of", "x1", "i1"], ["_large_a_1", "e1", "x1"]]]

    print(solve_and_respond(state, mrs))


# Evaluate the proposition: "which file is very small?"
def Example6a():
    state = State([Folder(name="Desktop"),
                   Folder(name="Documents"),
                   File(name="file1.txt", size=20000000),
                   File(name="file2.txt", size=1000000)])

    mrs = {}
    mrs["Index"] = "e1"
    mrs["Variables"] = {"x1": {"NUM": "sg"},
                        "e1": {"SF": "ques"}}
    mrs["Tree"] = [["_which_q", "x1", ["_file_n_of", "x1", "i1"], [["_very_x_deg", "e2", "e1"], ["_small_a_1", "e1", "x1"]]]]

    print(solve_and_respond(state, mrs))


# Evaluate the proposition: "which file is very large?"
def Example6b():
    state = State([Folder(name="Desktop"),
                   Folder(name="Documents"),
                   File(name="file1.txt", size=20000000),
                   File(name="file2.txt", size=1000000)])

    mrs = {}
    mrs["Index"] = "e1"
    mrs["Variables"] = {"x1": {"NUM": "sg"},
                        "e1": {"SF": "ques"}}
    mrs["Tree"] = [["_which_q", "x1", ["_file_n_of", "x1", "i1"], [["_very_x_deg", "e2", "e1"], ["_large_a_1", "e1", "x1"]]]]

    print(solve_and_respond(state, mrs))


# Delete a large file when there are some
def Example7():
    state = State([Actor(name="Computer", person=2),
                   Folder(name="Desktop"),
                   Folder(name="Documents"),
                   File(name="file1.txt", size=2000000),
                   File(name="file2.txt", size=1000000)])
    mrs = {}
    mrs["Index"] = "e2"
    mrs["Variables"] = {"x3": {"PERS": 2},
                        "e2": {"SF": "comm"}}
    mrs["Tree"] = [["pronoun_q", "x3", ["pron", "x3"], ["_a_q", "x8", [["_large_a_1", "e1", "x8"], ["_file_n_of", "x8", "i1"]], ["_delete_v_1", "e2", "x3", "x8"]]]]

    print(solve_and_respond(state, mrs))


# delete you
def Example8():
    state = State([Actor(name="Computer", person=2),
                   Folder(name="Desktop"),
                   Folder(name="Documents"),
                   File(name="file1.txt", size=2000000),
                   File(name="file2.txt", size=1000000)])

    mrs = {}
    mrs["Index"] = "e2"
    mrs["Variables"] = {"x3": {"PERS": 2},
                        "x8": {"PERS": 2},
                        "e2": {"SF": "comm"}}
    mrs["Tree"] = [["pronoun_q", "x3", ["pron", "x3"], ["pronoun_q", "x8", ["pron", "x8"], ["_delete_v_1", "e2", "x3", "x8"]]]]

    print(solve_and_respond(state, mrs))


# Delete a large file when there are no large files
def Example9():
    state = State([Actor(name="Computer", person=2),
                   Folder(name="Desktop"),
                   Folder(name="Documents"),
                   File(name="file1.txt", size=10),
                   File(name="file2.txt", size=10)])

    mrs = {}
    mrs["Index"] = "e2"
    mrs["Variables"] = {"x3": {"PERS": 2},
                        "e2": {"SF": "comm"}}
    mrs["Tree"] = [["pronoun_q", "x3", ["pron", "x3"], ["_a_q", "x8", [["_large_a_1", "e1", "x8"], ["_file_n_of", "x8"]], ["_delete_v_1", "e2", "x3", "x8"]]]]

    print(solve_and_respond(state, mrs))


# Evaluate the proposition: "a file is large" when there are no *large* files
def Example10():
    state = State([Folder(name="Desktop"),
                   Folder(name="Documents"),
                   File(name="file1.txt", size=1000000),
                   File(name="file2.txt", size=1000000)])
    mrs = {}
    mrs["Index"] = "e1"
    mrs["Variables"] = {"x1": {"NUM": "pl"},
                        "e1": {"SF": "prop"}}
    mrs["Tree"] = [["_a_q", "x1", ["_file_n_of", "x1", "i1"], ["_large_a_1", "e1", "x1"]]]

    print(solve_and_respond(state, mrs))


# Evaluate the proposition: "a file is large" when there are no files, period
def Example11():
    state = State([Folder(name="Desktop"),
                   Folder(name="Documents")])
    mrs = {}
    mrs["Index"] = "e1"
    mrs["Variables"] = {"x1": {"NUM": "pl"},
                        "e1": {"SF": "prop"}}
    mrs["Tree"] = [["_a_q", "x1", ["_file_n_of", "x1", "i1"], ["_large_a_1", "e1", "x1"]]]

    print(solve_and_respond(state, mrs))


def Example12():
    mrs = {"Tree": [["_a_q", "x1", ["_file_n_of", "x1", "i1"], ["_large_a_1", "e1", "x1"]]]}
    print(english_for_delphin_variable(1, "x1", mrs))
    print(english_for_delphin_variable(2, "x1", mrs))
    print(english_for_delphin_variable(3, "x1", mrs))
    
    
# "he/she" deletes a large file
def Example13():
    state = State([Actor(name="Computer", person=2),
                   Folder(name="Desktop"),
                   Folder(name="Documents"),
                   File(name="file1.txt", size=2000000),
                   File(name="file2.txt", size=1000000)])
    mrs = {}
    mrs["Index"] = "e2"
    mrs["Variables"] = {"x3": {"PERS": 3},
                        "e2": {"SF": "prop"}}
    mrs["Tree"] = [["pronoun_q", "x3", ["pron", "x3"],
                    ["_a_q", "x8", [["_large_a_1", "e1", "x8"], ["_file_n_of", "x8", "i1"]],
                     ["_delete_v_1", "e2", "x3", "x8"]]]]

    print(solve_and_respond(state, mrs))

    
# Evaluate the proposition: "which file is large?" if there are no files
def Example14():
    state = State([Folder(name="Desktop"),
                   Folder(name="Documents")])
    mrs = {}
    mrs["Index"] = "e1"
    mrs["Variables"] = {"x1": {"NUM": "sg"},
                        "e1": {"SF": "ques"}}
    mrs["Tree"] = [["_which_q", "x1", ["_file_n_of", "x1", "i1"], ["_large_a_1", "e1", "x1"]]]

    print(solve_and_respond(state, mrs))


# "A file is large" when there isn't a file in the system
def Example15():
    state = State([Folder(name="Desktop"),
                   Folder(name="Documents")])
    mrs = {}
    mrs["Index"] = "e1"
    mrs["Variables"] = {"x1": {"NUM": "pl"},
                        "e1": {"SF": "prop"}}
    mrs["Tree"] = [["_a_q", "x1", ["_file_n_of", "x1", "i1"], ["_large_a_1", "e1", "x1"]]]

    print(solve_and_respond(state, mrs))


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


if __name__ == '__main__':
    # ShowLogging("Execution")
    # ShowLogging("Generation")
    # ShowLogging("UserInterface")
    # ShowLogging("Pipeline")

    # Early examples need a context to set the vocabulary since
    # respond_to_mrs hadn't been built yet
    # with ExecutionContext(vocabulary):
    #     execution_context()._phrase_type = "prop"
    #     Example1()
    #     Example2()
    #     Example3()
    #     Example4()
    #     Example5()
    #     Example5_1()
    #     Example5_2()
    #     Example6()
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
    Example18()