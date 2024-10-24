from samples.file_system_example.messages import error_priority, generate_message
from samples.file_system_example.objects import FileSystemMock
from samples.file_system_example.state import State, FileSystemState, load_file_system_state
from samples.file_system_example.vocabulary import vocabulary, in_scope_initialize, in_scope
from perplexity.messages import respond_to_mrs_tree
from perplexity.plurals import all_plural_groups_stream, VariableCriteria, GlobalCriteria
from perplexity.state import LoadException
from perplexity.user_interface import UserInterface


def Example18_reset():
    return FileSystemState(FileSystemMock([(False, "/Desktop", {}),
                                           (False, "/Documents", {}),
                                           (True, "/Documents/file1.txt", {"size": 1000000})],
                                          "/Documents"))


def Example18():
    Test_main(Example18a_reset)


def Example18a_reset():
    return FileSystemState(FileSystemMock([(False, "/Desktop", {}),
                                           (False, "/Documents", {}),
                                           (True, "/Documents/file1.txt", {"size": 2000000}),
                                           (True, "/Documents/file2.txt", {"size": 1000000})],
                                          "/Documents"))


def Example18a():
    Test_main(Example18a_reset)


def Example19_reset():
    return FileSystemState(FileSystemMock([(True, "/documents/file1.txt", {"size": 1000000}),
                                           (False, "/Desktop", {})],
                                          "/documents"))


def Example19():
    Test_main(Example19_reset)


def Example20_reset():
    return FileSystemState(FileSystemMock([(True, "/documents/file1.txt", {"size": 1000}),
                                           (False, "/Desktop", {})],
                                          "/Desktop"))


def Example20():
    Test_main(Example20_reset)


def Example21_reset():
    return FileSystemState(FileSystemMock([(True, "/documents/file1.txt", {"size": 1000}),
                                           (False, "/Desktop", {}),
                                           (True, "/Desktop/file2.txt", {"size": 10000000}),
                                           (True, "/Desktop/file3.txt", {"size": 1000})],
                                          "/Desktop"))


def Example21():
    Test_main(Example21_reset)


def Example22_reset():
    return FileSystemState(FileSystemMock([(True, "/documents/file1.txt", {"size": 1000}),
                                           (False, "/Desktop", {"size": 10000000}),
                                           (True, "/Desktop/file2.txt", {"size": 10000000}),
                                           (True, "/Desktop/file3.txt", {"size": 1000})],
                                          "/Desktop"))


def Example22():
    Test_main(Example22_reset)


def Example23_reset():
    return FileSystemState(FileSystemMock([
                                           (True, "/documents/file1.txt", {"size": 1000}),
                                           (False, "/Desktop", {"size": 10000000}),
                                           (True, "/Desktop/the yearly budget.txt", {"size": 10000000}),
                                           (True, "/Desktop/blue", {"size": 1000})],
                                          "/Desktop"))


def Example23():
    Test_main(Example23_reset)


def Example24_reset():
    return FileSystemState(FileSystemMock([(True, "/temp/59.txt", {"size": 1000}),
                                           (True, "/documents/file1.txt", {"size": 1000}),
                                           (False, "/Desktop", {"size": 10000000}),
                                           (True, "/Desktop/the yearly budget.txt", {"size": 10000000}),
                                           (True, "/Desktop/blue", {"size": 1000})],
                                          "/Desktop"))


def Example24():
    Test_main(Example24_reset)


def Example25_reset():
    return FileSystemState(FileSystemMock([(True, "/temp/59.txt", {"size": 1000}),
                                           (True, "/documents/file1.txt", {"size": 1000}),
                                           (True, "/Desktop/the yearly budget.txt", {"size": 10000000}),
                                           (True, "/Desktop/blue", {"size": 10000000}),
                                           (False, "/Desktop", {"size": 10000000})],
                                           "/Desktop"))


def Example25():
    Test_main(Example25_reset)


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
    Test_main(Example26_reset)


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
    Test_main(Example27_reset)


def Example27a_reset():
    return FileSystemState(FileSystemMock([(True, "/59.txt", {"size": 1000}),
                                           (True, "/documents/file1.txt", {"size": 1000}),
                                           (False, "/Desktop", {"size": 10000000}),
                                           (True, "/Desktop/the yearly budget.txt", {"size": 10000000}),
                                           (True, "/Desktop/bigfile.txt", {"size": 20000000}),
                                           (True, "/Desktop/bigfile2.txt", {"size": 20000000}),
                                           (True, "/Desktop/bigfile3.txt", {"size": 20000000}),
                                           (True, "/Desktop/blue", {"size": 10000000}),
                                           (True, "/Desktop/green", {"size": 10000000})],
                                           "/Desktop"))


def Example27a():
    Test_main(Example27a_reset)


def Example28_reset():
    return FileSystemState(FileSystemMock([(True, "/temp/59.txt", {"size": 1000}),
                                           (True, "/documents/file1.txt", {"size": 1000}),
                                           (True, "/Desktop/the yearly budget.txt", {"size": 10000000}),
                                           (True, "/Desktop/bigfile.txt", {"size": 20000000}),
                                           (True, "/Desktop/bigfile2.txt", {"size": 20000000}),
                                           (True, "/Desktop/bigfile3.txt", {"size": 20000000}),
                                           (True, "/Desktop/blue", {"size": 10000000})],
                                          "/Desktop"))


def Example28():
    Test_main(Example28_reset)


def Example29_reset():
    return FileSystemState(FileSystemMock([(True, "/Desktop/file2.txt", {"size": 10000000}),
                                           (True, "/Desktop/file3.txt", {"size": 10000000})],
                                          "/Desktop"))


def Example29():
    Test_main(Example29_reset)


def Example30_reset():
    return FileSystemState(FileSystemMock([(True, "/Desktop/file2.txt", {"size": 10000000}),
                                           (True, "/Desktop/file3.txt", {"size": 10000000}),
                                           (True, "/documents/file4.txt", {"size": 10000000}),
                                           (True, "/documents/file5.txt", {"size": 10000000})],
                                           "/Desktop"))


def Example30():
    Test_main(Example30_reset)


def Example31_reset():
    return FileSystemState(FileSystemMock([(True, "/Desktop/file4.txt", {"size": 10000000, "link": 1}),
                                           (True, "/Desktop/file5.txt", {"size": 10000000, "link": 2}),
                                           (True, "/documents/file4.txt", {"size": 10000000, "link": 1}),
                                           (True, "/documents/file5.txt", {"size": 10000000, "link": 2})],
                                           "/Desktop"))


def Example31():
    Test_main(Example31_reset)


def Example32_reset():
    return FileSystemState(FileSystemMock([(True, "/Desktop/file2.txt", {"size": 10000000}),
                                           (True, "/documents/file5.txt", {"size": 10000000})],
                                           "/Desktop"))


def Example32():
    Test_main(Example32_reset)


def Example33_reset():
    file_list = [(True, f"/documents/file{str(index)}.txt", {"size": 10000000}) for index in range(20)]
    # file_list = [(True, f"/documents/file{str(index)}.txt", {"size": 10000000}) for index in range(100)]
    return FileSystemState(FileSystemMock(file_list,
                                           "/documents"))


def Example33():
    Test_main(Example33_reset)


def Example33a_reset():
    file_list = []
    for folder_index in range(30):
        file_list += [(True, f"/documents{folder_index}/file{folder_index}_{str(index)}.txt", {"size": 10000000}) for index in range(2)]
    return FileSystemState(FileSystemMock(file_list,
                                           "/documents"))


def Example33a():
    Test_main(Example33a_reset)


# def Example33_performance_test():
#     user_interface = UserInterface("example", Example33_reset, vocabulary, generate_message, error_priority, respond_to_mrs_tree, scope_function=in_scope, scope_init_function=in_scope_initialize)
#     user_interface.interact_once(force_input="which files are large?")


def Example34_reset():
    return FileSystemState(FileSystemMock([(True, "/Desktop/file1.txt", {"size": 10000000}),
                                           (True, "/Desktop/file2.txt", {"size": 10000000}),
                                           (True, "/documents/file3.txt", {"size": 10000000}),
                                           (True, "/documents/file4.txt", {"size": 10000000})
                                           ],
                                           "/Desktop"))


def Example34():
    Test_main(Example34_reset)


def Example35_reset():
    return FileSystemState(FileSystemMock([(True, "/Desktop/file4.txt", {"size": 10000000, "link": 1}),
                                           (True, "/foo/file4.txt", {"size": 10000000, "link": 1}),
                                           (True, "/bar/file5.txt", {"size": 10000000, "link": 2}),
                                           (True, "/go/file5.txt", {"size": 10000000, "link": 2})],
                                           "/Desktop"))


def Example35():
    Test_main(Example35_reset)


def Example36_reset():
    return FileSystemState(FileSystemMock([(True, "/Desktop/file2.txt", {"size": 10000000}),
                                           (True, "/Desktop/file3.txt", {"size": 10000}),
                                           (True, "/documents/file4.txt", {"size": 10000000}),
                                           (True, "/documents/file5.txt", {"size": 10000})],
                                           "/Desktop"))


def Example36():
    Test_main(Example36_reset)


def Example37_reset():
    return FileSystemState(FileSystemMock([(True, "/Desktop/file2.txt", {"size": 10000000})
                                           ],
                                           "/Desktop"))


def Example37():
    Test_main(Example37_reset)


def Example38_reset():
    state = FileSystemState(FileSystemMock([(True, "/Desktop/file2.txt", {"size": 10000000}),
                                           (True, "/Desktop/file3.txt", {"size": 10000}),
                                           (True, "/documents/file4.txt", {"size": 10000000}),
                                           (True, "/documents/file5.txt", {"size": 10000})],
                                           "/Desktop"))
    return state.set_x("test_solution_group", ("cannotAnswer", ))


def Example38():
    Test_main(Example38_reset)


def Example39_reset():
    state = FileSystemState(FileSystemMock([(True, "/Desktop/file2.txt", {"size": 10000000}),
                                           (True, "/Desktop/file3.txt", {"size": 10000}),
                                           (True, "/documents/file4.txt", {"size": 10000000}),
                                           (True, "/documents/file5.txt", {"size": 10000})],
                                           "/Desktop"))

    return state.set_x("test_solution_group", ("fakeValues", ))


def Example39():
    Test_main(Example39_reset)


def Example40_reset():
    state = FileSystemState(FileSystemMock([(True, "/Desktop/file2.txt", {"size": 10000000}),
                                           (True, "/Desktop/file3.txt", {"size": 10000}),
                                           (True, "/documents/file4.txt", {"size": 10000000}),
                                           (True, "/documents/file5.txt", {"size": 10000})],
                                           "/Desktop"))

    return state.set_x("test_solution_group", ("fakeValues", ))


def Example40():
    Test_main(Example40_reset)


def Example41_reset():
    state = FileSystemState(FileSystemMock([(True, "/Desktop/file2.txt", {"size": 10000000}),
                                           (True, "/Desktop/file3.txt", {"size": 10000}),
                                           (True, "/documents/file4.txt", {"size": 10000000}),
                                           (True, "/documents/file5.txt", {"size": 10000})],
                                           "/Desktop"))

    return state.set_x("test_solution_group", ("failAll", ))


def Example41():
    Test_main(Example41_reset)


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


def Example_main_reset():
    return FileSystemState(FileSystemMock([(True, "/Desktop/file2.txt", {"size": 10000000}),
                                           (True, "/Desktop/file3.txt", {"size": 10000}),
                                           (True, "/documents/file4.txt", {"size": 10000000}),
                                           (True, "/documents/file5.txt", {"size": 10000})],
                                           "/Desktop"))


def Example_main():
    user_interface = Example_ui()
    while user_interface:
        user_interface = user_interface.default_loop()


def Test_main(reset_function):
    user_interface = UserInterface(world_name="example",
                                   reset_function=reset_function,
                                   vocabulary=vocabulary,
                                   message_function=generate_message,
                                   error_priority_function=error_priority,
                                   response_function=respond_to_mrs_tree,
                                   scope_init_function=in_scope_initialize,
                                   scope_function=in_scope)

    while user_interface:
        user_interface = user_interface.default_loop()


def Example_ui(loading_info=None, file=None, user_output=None, debug_output=None):
    loaded_state = None
    if loading_info is not None:
        if loading_info.get("Version", None) != 1:
            raise LoadException()

        if file is not None:
            loaded_state = load_file_system_state(file)

    user_interface = UserInterface(world_name="example",
                                   reset_function=Example_main_reset,
                                   vocabulary=vocabulary,
                                   message_function=generate_message,
                                   error_priority_function=error_priority,
                                   response_function=respond_to_mrs_tree,
                                   scope_init_function=in_scope_initialize,
                                   scope_function=in_scope,
                                   loaded_state=loaded_state,
                                   user_output=user_output,
                                   debug_output=debug_output)
    return user_interface


if __name__ == '__main__':
    # ShowLogging("Pipeline")
    # ShowLogging("SolutionGroups")
    # ShowLogging("Execution")
    # ShowLogging("Generation")
    # ShowLogging("UserInterface")
    # ShowLogging("SString")
    # ShowLogging("Determiners")

    # Early examples need a context to set the vocabulary since
    # respond_to_mrs hadn't been built yet
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
    Example24()
    # Example25()
    # Example26()
    # Example27()
    # Example27a()
    # Example28()
    # Example29()
    # Example30()
    # Example31()
    # Example32()
    # Example33()
    # Example33a()
    # Example33_performance_test()
    # Example34()
    # Example35()
    # Example36()
    # Example37()
    # Example38()
    # Example39()
    # Example40()
    # Example41()
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


    # Demo: Do with pipeline on

    # Example28()
    # Example26()
    # /soln all
    # which file is in this folder? -> what is singular, thus: there are more
    # which files are in this folder?
    # Which 2 files are in 2 folders? -> cumulative reading
    # /show
    # which 2 files are in 2 folders together? -> show the parse that worked
    # /show

    Example_main()
