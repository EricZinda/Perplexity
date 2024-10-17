

def solve_and_respond(state, mrs):
    context = ExecutionContext(vocabulary)
    solutions = list(context.solve_mrs_tree(state, mrs))
    return respond_to_mrs_tree(state, mrs, solutions, context.error())

# # List folders using call_predication
# def Example2():
#     state = State([Folder(name="Desktop"),
#                    Folder(name="Documents"),
#                    File(name="file1.txt"),
#                    File(name="file2.txt")])
#
#     for item in call_predication(state,
#                                  TreePredication(0, "_folder_n_of", ["x1", "i1"])
#                                  ):
#         print(item.variables)
#
#
# # "Large files" using a conjunction
# def Example3():
#     state = State([Folder(name="Desktop"),
#                    Folder(name="Documents"),
#                    File(name="file1.txt", size=100),
#                    File(name="file2.txt", size=2000000)])
#
#     tree = [TreePredication(0, "_large_a_1", ["e1", "x1"]),
#             TreePredication(1, "_file_n_of", ["x1", "i1"])]
#
#     for item in call(state, tree):
#         print(item.variables)
#
#
# # "a" large file in a world with two large files
# def Example4():
#     # Note that both files are "large" now
#     state = State([Folder(name="Desktop"),
#                    Folder(name="Documents"),
#                    File(name="file1.txt", size=2000000),
#                    File(name="file2.txt", size=2000000)])
#
#     tree = TreePredication(0, "_a_q", ["x3",
#                                        TreePredication(1, "_file_n_of", ["x3", "i1"]),
#                                        TreePredication(2, "_large_a_1", ["e2", "x3"])])
#
#     for item in call(state, tree):
#         print(item.variables)
#
#
# # Evaluate the proposition: "a file is large" when there is one
# def Example5():
#     state = State([Folder(name="Desktop"),
#                    Folder(name="Documents"),
#                    File(name="file1.txt", size=2000000),
#                    File(name="file2.txt", size=2000000)])
#
#     # Start with an empty dictionary
#     tree_info = {}
#
#     # Set its "index" key to the value "e1"
#     tree_info["Index"] = "e1"
#
#     # Set its "Variables" key to *another* dictionary with
#     # two keys: "x1" and "e1". Each of those has a "value" of
#     # yet another dictionary that holds the properties of the variables
#     tree_info["Variables"] = {"x1": {"NUM": "pl"},
#                               "e1": {"SF": "prop"}}
#
#     # Set the "Tree" key to the scope-resolved MRS tree, using our format
#     tree_info["Tree"] = TreePredication(0, "_a_q", ["x1",
#                                                     TreePredication(1, "_file_n_of", ["x1", "i1"]),
#                                                     TreePredication(2, "_large_a_1", ["e1", "x1"])])
#
#     print(solve_and_respond(state, tree_info))
#
#
# # Evaluate the proposition: "a file is large" when there isn't a large one
# def Example5_1():
#     state = State([Folder(name="Desktop"),
#                    Folder(name="Documents"),
#                    File(name="file1.txt", size=200),
#                    File(name="file2.txt", size=200)])
#     # Start with an empty dictionary
#     tree_info = {}
#
#     # Set its "index" key to the value "e1"
#     tree_info["Index"] = "e1"
#
#     # Set its "Variables" key to *another* dictionary with
#     # two keys: "x1" and "e1". Each of those has a "value" of
#     # yet another dictionary that holds the properties of the variables
#     tree_info["Variables"] = {"x1": {"NUM": "pl"},
#                         "e1": {"SF": "prop"}}
#
#     # Set the "Tree" key to the scope-resolved MRS tree, using our format
#     tree_info["Tree"] = TreePredication(0, "_a_q", ["x1",
#                                                     TreePredication(1, "_file_n_of", ["x1", "i1"]),
#                                                     TreePredication(2, "_large_a_1", ["e1", "x1"])])
#
#     print(solve_and_respond(state, tree_info))
#
#
# # Evaluate the proposition: "a file is large" when there isn't any files
# def Example5_2():
#     state = State([Folder(name="Desktop"),
#                    Folder(name="Documents")])
#     # Start with an empty dictionary
#     tree_info = {}
#     # Set its "index" key to the value "e1"
#     tree_info["Index"] = "e1"
#     # Set its "Variables" key to *another* dictionary with
#     # two keys: "x1" and "e1". Each of those has a "value" of
#     # yet another dictionary that holds the properties of the variables
#     tree_info["Variables"] = {"x1": {"NUM": "pl"},
#                         "e1": {"SF": "prop"}}
#     # Set the "Tree" key to the scope-resolved MRS tree, using our format
#     tree_info["Tree"] = TreePredication(0, "_a_q", ["x1",
#                                                     TreePredication(1, "_file_n_of", ["x1", "i1"]),
#                                                     TreePredication(2, "_large_a_1", ["e1", "x1"])])
#
#     print(solve_and_respond(state, tree_info))
#
#
# # Evaluate the proposition: "which file is large?"
# def Example6():
#     state = State([Folder(name="Desktop"),
#                    Folder(name="Documents"),
#                    File(name="file1.txt", size=2000000),
#                    File(name="file2.txt", size=1000000)])
#
#     tree_info = {}
#     tree_info["Index"] = "e1"
#     tree_info["Variables"] = {"x1": {"NUM": "sg"},
#                         "e1": {"SF": "ques"}}
#     tree_info["Tree"] = TreePredication(0, "_which_q", ["x1",
#                                                         TreePredication(1, "_file_n_of", ["x1", "i1"]),
#                                                         TreePredication(2, "_large_a_1", ["e1", "x1"])])
#
#     print(solve_and_respond(state, tree_info))
#
#
# # Evaluate the proposition: "which file is very small?"
# def Example6a():
#     state = State([Folder(name="Desktop"),
#                    Folder(name="Documents"),
#                    File(name="file1.txt", size=20000000),
#                    File(name="file2.txt", size=1000000)])
#
#     tree_info = {}
#     tree_info["Index"] = "e1"
#     tree_info["Variables"] = {"x1": {"NUM": "sg"},
#                         "e1": {"SF": "ques"}}
#     tree_info["Tree"] = TreePredication(0, "_which_q", ["x1",
#                                                         TreePredication(1, "_file_n_of", ["x1", "i1"]),
#                                                         [TreePredication(2, "_very_x_deg", ["e2", "e1"]),
#                                                          TreePredication(3, "_small_a_1", ["e1", "x1"])]])
#
#     print(solve_and_respond(state, tree_info))
#
#
# # Evaluate the proposition: "which file is very large?"
# def Example6b():
#     state = State([Folder(name="Desktop"),
#                    Folder(name="Documents"),
#                    File(name="file1.txt", size=20000000),
#                    File(name="file2.txt", size=1000000)])
#
#     tree_info = {}
#     tree_info["Index"] = "e1"
#     tree_info["Variables"] = {"x1": {"NUM": "sg"},
#                         "e1": {"SF": "ques"}}
#     tree_info["Tree"] = TreePredication(0, "_which_q", ["x1",
#                                                         TreePredication(1, "_file_n_of", ["x1", "i1"]),
#                                                         [TreePredication(2, "_very_x_deg", ["e2", "e1"]),
#                                                          TreePredication(3, "_large_a_1", ["e1", "x1"])]])
#
#     print(solve_and_respond(state, tree_info))
#
#
# # Delete a large file when there are some
# def Example7():
#     state = State([Actor(name="Computer", person=2),
#                    Folder(name="Desktop"),
#                    Folder(name="Documents"),
#                    File(name="file1.txt", size=2000000),
#                    File(name="file2.txt", size=1000000)])
#     tree_info = {}
#     tree_info["Index"] = "e2"
#     tree_info["Variables"] = {"x3": {"PERS": 2},
#                               "e2": {"SF": "comm"}}
#     tree_info["Tree"] = TreePredication(0, "pronoun_q", ["x3",
#                                                          TreePredication(1, "pron", ["x3"]),
#                                                          TreePredication(2, "_a_q", ["x8",
#                                                                                      [TreePredication(3, "_large_a_1", ["e1", "x1"]),
#                                                                                       TreePredication(4, "_file_n_of", ["x1", "i1"])],
#                                                                                       TreePredication(5, "_delete_v_1", ["e2", "x3", "x1"])])])
#
#     print(solve_and_respond(state, tree_info))
#
#
# # delete you
# def Example8():
#     state = State([Actor(name="Computer", person=2),
#                    Folder(name="Desktop"),
#                    Folder(name="Documents"),
#                    File(name="file1.txt", size=2000000),
#                    File(name="file2.txt", size=1000000)])
#
#     tree_info = {}
#     tree_info["Index"] = "e2"
#     tree_info["Variables"] = {"x3": {"PERS": 2},
#                               "x8": {"PERS": 2},
#                               "e2": {"SF": "comm"}}
#     tree_info["Tree"] = TreePredication(0, "pronoun_q", ["x3",
#                                                          TreePredication(1, "pron", ["x3"]),
#                                                          TreePredication(2, "pronoun_q", ["x8",
#                                                                                           TreePredication(3, "pron", ["x8"]),
#                                                                                           TreePredication(4, "_delete_v_1",["e2", "x3", "x8"])])])
#
#     print(solve_and_respond(state, tree_info))
#
#
# # Delete a large file when there are no large files
# def Example9():
#     state = State([Actor(name="Computer", person=2),
#                    Folder(name="Desktop"),
#                    Folder(name="Documents"),
#                    File(name="file1.txt", size=10),
#                    File(name="file2.txt", size=10)])
#
#     tree_info = {}
#     tree_info["Index"] = "e2"
#     tree_info["Variables"] = {"x3": {"PERS": 2},
#                               "e2": {"SF": "comm"}}
#     tree_info["Tree"] = TreePredication(0, "pronoun_q", ["x3",
#                                                          TreePredication(1, "pron", ["x3"]),
#                                                          TreePredication(2, "_a_q", ["x1",
#                                                                                      [TreePredication(3, "_large_a_1", ["e1", "x1"]),
#                                                                                       TreePredication(4, "_file_n_of", ["x1", "i1"])],
#                                                                                      TreePredication(5, "_delete_v_1", ["e2", "x3", "x1"])])])
#
#     print(solve_and_respond(state, tree_info))
#
#
# # Evaluate the proposition: "a file is large" when there are no *large* files
# def Example10():
#     state = State([Folder(name="Desktop"),
#                    Folder(name="Documents"),
#                    File(name="file1.txt", size=1000000),
#                    File(name="file2.txt", size=1000000)])
#     tree_info = {}
#     tree_info["Index"] = "e1"
#     tree_info["Variables"] = {"x1": {"NUM": "pl"},
#                         "e1": {"SF": "prop"}}
#
#     tree_info["Tree"] = TreePredication(0, "_a_q", ["x1",
#                                                     TreePredication(1, "_file_n_of", ["x1", "i1"]),
#                                                     TreePredication(2, "_large_a_1", ["e1", "x1"])])
#
#     print(solve_and_respond(state, tree_info))
#
#
# # Evaluate the proposition: "a file is large" when there are no files, period
# def Example11():
#     state = State([Folder(name="Desktop"),
#                    Folder(name="Documents")])
#     tree_info = {}
#     tree_info["Index"] = "e1"
#     tree_info["Variables"] = {"x1": {"NUM": "pl"},
#                         "e1": {"SF": "prop"}}
#     tree_info["Tree"] = TreePredication(0, "_a_q", ["x1",
#                                                     TreePredication(1, "_file_n_of", ["x1", "i1"]),
#                                                     TreePredication(2, "_large_a_1", ["e1", "x1"])])
#
#     print(solve_and_respond(state, tree_info))
#
#
# def Example12():
#     tree_info = {}
#     tree_info["Tree"] = TreePredication(0, "_a_q", ["x1",
#                                                     TreePredication(1, "_file_n_of", ["x1", "i1"]),
#                                                     TreePredication(2, "_large_a_1", ["e1", "x1"])])
#
#     print(english_for_delphin_variable(0, "x1", tree_info))
#     print(english_for_delphin_variable(1, "x1", tree_info))
#     print(english_for_delphin_variable(2, "x1", tree_info))
#
#
# # "he/she" deletes a large file
# def Example13():
#     state = State([Actor(name="Computer", person=2),
#                    Folder(name="Desktop"),
#                    Folder(name="Documents"),
#                    File(name="file1.txt", size=2000000),
#                    File(name="file2.txt", size=1000000)])
#     tree_info = {}
#     tree_info["Index"] = "e2"
#     tree_info["Variables"] = {"x3": {"PERS": 3},
#                               "e2": {"SF": "prop"}}
#
#     tree_info["Tree"] = TreePredication(0, "pronoun_q", ["x3",
#                                                          TreePredication(1, "pron", ["x3"]),
#                                                          TreePredication(2, "_a_q", ["x1",
#                                                                                      [TreePredication(3, "_large_a_1", ["e1", "x1"]),
#                                                                                       TreePredication(4, "_file_n_of", ["x1", "i1"])],
#                                                                                      TreePredication(5, "_delete_v_1", ["e2", "x3", "x1"])])])
#
#     print(solve_and_respond(state, tree_info))
#
#
# # Evaluate the proposition: "which file is large?" if there are no files
# def Example14():
#     state = State([Folder(name="Desktop"),
#                    Folder(name="Documents")])
#     tree_info = {}
#     tree_info["Index"] = "e1"
#     tree_info["Variables"] = {"x1": {"NUM": "sg"},
#                               "e1": {"SF": "ques"}}
#     tree_info["Tree"] = TreePredication(0, "_which_q", ["x1",
#                                                         TreePredication(1, "_file_n_of", ["x1", "i1"]),
#                                                         TreePredication(2, "_large_a_1", ["e1", "x1"])])
#
#     print(solve_and_respond(state, tree_info))
#
#
# # "A file is large" when there isn't a file in the system
# def Example15():
#     state = State([Folder(name="Desktop"),
#                    Folder(name="Documents")])
#     tree_info = {}
#     tree_info["Index"] = "e1"
#     tree_info["Variables"] = {"x1": {"NUM": "pl"},
#                         "e1": {"SF": "prop"}}
#     tree_info["Tree"] = TreePredication(0, "_a_q", ["x1",
#                                                     TreePredication(1, "_file_n_of", ["x1", "i1"]),
#                                                     TreePredication(2, "_large_a_1", ["e1", "x1"])])
#
#     print(solve_and_respond(state, tree_info))
#
#
# def Example16_reset():
#     return State([Actor(name="Computer", person=2),
#                   Folder(name="Desktop"),
#                   Folder(name="Documents"),
#                   File(name="file1.txt", size=2000000)])
#
#
# def Example16():
#     Test_main(Example16_reset)
#
#     # # ShowLogging("Pipeline")
#     # user_interface = UserInterface("example", Example16_reset, vocabulary, generate_message, respond_to_mrs_tree)
#     #
#     # while True:
#     #     user_interface.interact_once()
#     #     print()
#
#
# def Example17():
#     def reset():
#         return State([Folder(name="Desktop"),
#                       Folder(name="Documents")])
#
#     user_interface = UserInterface("example", reset, vocabulary, generate_message, None)
#
#     for mrs in user_interface.mrss_from_phrase("every book is in a cave"):
#         for tree in user_interface.trees_from_mrs(mrs):
#             print(tree)
#
#