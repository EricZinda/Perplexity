from perplexity.execution import TreeSolver, ExecutionContext
import perplexity.messages
from perplexity.state import State
from perplexity.system_vocabulary import system_vocabulary
from perplexity.tree import DisjunctionInterpretationGenerator, TreePredication, set_disjunction_lineage
from perplexity.user_interface import default_error_priority
from perplexity.utilities import at_least_one_generator, ShowLogging
from perplexity.vocabulary import Predication

vocabulary = system_vocabulary()


def error_priority(error_info):
    system_priority = perplexity.messages.error_priority(error_info)
    if system_priority is not None:
        return system_priority
    else:
        # Must be a message from our code
        error_constant = error_info.error[0]
        priority = perplexity.messages.error_priority_dict["defaultPriority"]
        priority += (error_info.error_phase - 1) * perplexity.messages.error_priority_dict["success"]
        return priority


def test_solution_groups(tree_info, state=None):
    state = State([] if state is None else state)
    solver = TreeSolver.create_top_level_solver(vocabulary, error_priority, None, None)
    for tree_record in solver.tree_solutions(state, tree_info):
        if tree_record["SolutionGroupGenerator"] is not None:
            print("Tree")
            for solution_group in tree_record["SolutionGroupGenerator"]:
                print("SolutionGroup")
                for solution in solution_group:
                    print(solution)


def test_tree(tree_info, state=None):
    execution_context = ExecutionContext(vocabulary, error_priority_function=default_error_priority)
    tree_solver = TreeSolver(execution_context)
    interpretation_list = list(tree_solver.mrs_tree_interpretations(tree_info))
    assert len(interpretation_list) == 1
    interpretation_dict = interpretation_list[0]

    state = State([] if state is None else state)

    interpretation_solver = TreeSolver.InterpretationSolver(execution_context, timeout=None, start_time=None)
    interpretation_solution_generator = interpretation_solver.solve_tree_interpretation(state, tree_info, interpretation_dict)
    interpretation_disjunction_generator = DisjunctionInterpretationGenerator(interpretation_solver, interpretation_solution_generator)
    interpretation_solver.set_disjunction_interpretation_generator(interpretation_disjunction_generator)

    result = ""
    for disjunction_interpretation in interpretation_disjunction_generator:
        result += f"Interpretation: {disjunction_interpretation.lineage}\n"
        disjunction_interpretation_solutions = at_least_one_generator(disjunction_interpretation)
        if disjunction_interpretation_solutions:
            for solution in disjunction_interpretation_solutions:
                result += f"{str(solution)}\n"
        else:
            result += f"{disjunction_interpretation.lineage} interpretation has error: {disjunction_interpretation.state.error_info.error}\n"

    return result


@Predication(vocabulary,
             names=["fail_with_error"])
def fail_with_error(context, state, x_binding):
    context.report_error(["errorText", "Test"])

    if False:
        yield None


def one_predication_zero_disjunction_fails():
    tree = TreePredication(0, "fail_with_error", ["x1"], ["ARG0"])
    variables = {"x1": {"SF": "prop"}}
    return test_tree({"Index": "x1",
                      "Variables": variables,
                      "Tree": tree})


@Predication(vocabulary,
             names=["zero_disjunction_success"])
def zero_disjunction_success(context, state, x_binding):
    state1 = state.set_x(x_binding.variable.name, ("disjunction_1",))
    yield state1


def one_predication_zero_disjunction_success():
    tree = TreePredication(0, "zero_disjunction_success", ["x1"], ["ARG0"])
    variables = {"x1": {"SF": "prop"}}
    return test_tree({"Index": "x1",
                      "Variables": variables,
                      "Tree": tree})


@Predication(vocabulary,
             names=["one_disjunction_success"])
def one_disjunction_success(context, state, x_binding):
    state1 = state.set_x(x_binding.variable.name, ("disjunction_1",))
    yield set_disjunction_lineage(state1, context, "1")


def one_predication_one_disjunction_success():
    tree = TreePredication(0, "one_disjunction_success", ["x1"], ["ARG0"])
    variables = {"x1": {"SF": "prop"}}
    return test_tree({"Index": "x1",
                      "Variables": variables,
                      "Tree": tree})


@Predication(vocabulary,
             names=["two_disjunctions_success"])
def two_disjunctions_success(context, state, x_binding):
    state1 = state.set_x(x_binding.variable.name, ("disjunction_1",))
    yield set_disjunction_lineage(state1, context, "1")

    state2 = state.set_x(x_binding.variable.name, ("disjunction_2",))
    yield set_disjunction_lineage(state2, context, "2")


def one_predication_two_disjunction_success():
    tree = TreePredication(0, "two_disjunctions_success", ["x1"], ["ARG0"])
    variables = {"x1": {"SF": "prop"}}
    return test_tree({"Index": "x1",
                      "Variables": variables,
                      "Tree": tree})


@Predication(vocabulary,
             names=["two_disjunctions_success_fail"])
def two_disjunctions_success_fail(context, state, x_binding):
    state1 = state.set_x(x_binding.variable.name, ("disjunction_1",))
    yield set_disjunction_lineage(state1, context, "1")

    context.report_error(["two_disjunctions_success_fail", "Fail"])


# The second failure doesn't actually create a disjunction value and so
# a new disjunction is not created. Thus we should only get one success and no failures
# (since there was no conjunction interpretation created
def one_predication_two_disjunction_success_fail():
    tree = TreePredication(0, "two_disjunctions_success_fail", ["x1"], ["ARG0"])
    variables = {"x1": {"SF": "prop"}}
    return test_tree({"Index": "x1",
                      "Variables": variables,
                      "Tree": tree})


@Predication(vocabulary,
             names=["predication1"])
def predication1(context, state, x_binding):
    values = state.objects
    for value in values["predication1"]:
        state1 = state.set_x(x_binding.variable.name, (value[0],))
        if value[1] is not None:
            state1 = set_disjunction_lineage(state1, context, value[1])
        yield state1

    context.report_error(["predication1", "Fail"])


@Predication(vocabulary,
             names=["predication1a"])
def predication1a(context, state, x_binding):
    values = state.objects
    for value in values["predication1a"]:
        state1 = state.set_x(x_binding.variable.name, (value[0],))
        if value[1] is not None:
            state1 = set_disjunction_lineage(state1, context, value[1])
        yield state1

    context.report_error(["predication1a", "Fail"])


@Predication(vocabulary,
             names=["predication2"])
def predication2(context, state, x_binding_1, x_binding_2):
    values = state.objects
    x1_value = x_binding_1.value[0]
    for value in values["predication2"]:
        if value[0][0] == x1_value:
            if x_binding_2.value is None:
                state1 = state.set_x(x_binding_2.variable.name, (value[0][1],))
                if value[1] is not None:
                    state1 = set_disjunction_lineage(state1, context, value[1])
                yield state1
            elif x_binding_2.value[0] == value[0][1]:
                yield state

    context.report_error(["predication2", "Fail", str(x_binding_1)])


@Predication(vocabulary,
             names=["predication3"])
def predication3(context, state, x_binding_1, x_binding_2, x_binding_3):
    values = state.objects
    x1_value = x_binding_1.value[0]
    x2_value = x_binding_2.value[0]
    for value in values["predication3"]:
        if value[0][0] == x1_value and value[0][1] == x2_value:
            state1 = state.set_x(x_binding_3.variable.name, (value[0][2],))
            if value[1] is not None:
                state1 = set_disjunction_lineage(state1, context, value[1])
            yield state1

    context.report_error(["predication3", "Fail", str(x_binding_1), str(x_binding_2)])


def pred1_succ_pred2_succconj_succconj():
    test_state = {
        "predication1": [
            ("predication1_1", None)
        ],
        "predication2": [
            (("predication1_1", "predication2_1_1"), "1"),
            (("predication1_1", "predication2_2_1"), "2")
        ]
    }

    tree = [TreePredication(0, "predication1", ["x1"], ["ARG0"]),
            TreePredication(1, "predication2", ["x1", "x2"], ["ARG0", "ARG1"])]
    variables = {"x1": {"SF": "prop"},
                 "x2": {}}

    return test_tree({"Index": "x1",
                      "Variables": variables,
                      "Tree": tree},
                      test_state)


def pred1_succconj_succconj_pred2_fail():
    test_state = {
        "predication1": [
            ("predication1_1", "1"),
            ("predication1_2", "2"),
        ],
        "predication2": []
    }

    tree = [TreePredication(0, "predication1", ["x1"], ["ARG0"]),
            TreePredication(1, "predication2", ["x1", "x2"], ["ARG0", "ARG1"])]
    variables = {"x1": {"SF": "prop"},
                 "x2": {}}

    return test_tree({"Index": "x1",
                      "Variables": variables,
                      "Tree": tree},
                      test_state)


def pred1_p11cs_p12cs_pred2_p11cf_p12cs():
    test_state = {
        "predication1": [
            ("predication1_1", "1"),
            ("predication1_2", "2"),
        ],
        "predication2": [
            (("predication1_2", "predication2_1"), "1"),
        ]
    }

    tree = [TreePredication(0, "predication1", ["x1"], ["ARG0"]),
            TreePredication(1, "predication2", ["x1", "x2"], ["ARG0", "ARG1"])]
    variables = {"x1": {"SF": "prop"},
                 "x2": {}}

    return test_tree({"Index": "x1",
                      "Variables": variables,
                      "Tree": tree},
                      test_state)


def p11c_p12c__p11_p21_p12_p22__p11_p21_p31c_p12_p22_p32c():
    test_state = {
        "predication1": [
            ("predication1_1", "1"),
            ("predication1_2", "2"),
        ],
        "predication2": [
            (("predication1_1", "predication2_1"), None),
            (("predication1_2", "predication2_2"), None),
        ],
        "predication3": [
            (("predication1_1", "predication2_1", "predication3_1"), "1"),
            (("predication1_2", "predication2_2", "predication3_2"), "2"),
        ]
    }

    tree = [TreePredication(0, "predication1", ["x1"], ["ARG0"]),
            TreePredication(1, "predication2", ["x1", "x2"], ["ARG0", "ARG1"]),
            TreePredication(2, "predication3", ["x1", "x2", "x3"], ["ARG0", "ARG1", "ARG2"])]
    variables = {"x1": {"SF": "prop"},
                 "x2": {},
                 "x3": {}}

    return test_tree({"Index": "x1",
                      "Variables": variables,
                      "Tree": tree},
                      test_state)


def two_girls_have_an_ice_cream():
    test_state = {
        "predication1": [
            ("girl1", None),
            ("girl2", None),
        ],
        "predication1a": [
            ("icecream1", None),
            ("icecream2", None),
        ],
        "predication2": [
            (("girl1", "icecream1"), None),
            (("girl2", "icecream2"), None),
        ]
    }

    an_ice_cream = [TreePredication(2,
                                    "_a_q",
                                    ["x2",
                                     TreePredication(3, "predication1a", ["x2"], ["ARG0"]),
                                     TreePredication(4, "predication2", ["x1", "x2"], ["ARG0", "ARG1"])],
                                    ["ARG0", "RSTR", "BODY"])]

    tree = [TreePredication(0,
                            "udef_q",
                            ["x1",
                             TreePredication(1, "predication1", ["x1"], ["ARG0"]),
                             an_ice_cream],
                            ["ARG0", "RSTR", "BODY"])]
    variables = {"x1": {"SF": "prop"},
                 "x2": {"NUM": "sg"}}

    return test_solution_groups({"Index": "x1",
                      "Variables": variables,
                      "Tree": tree,
                      "SyntacticHeads": ["x1"]},
                      test_state)


if __name__ == '__main__':
    # ShowLogging("Pipeline")
    ShowLogging("SolutionGroups")
    # ShowLogging("Execution")
    # ShowLogging("Generation")
    # ShowLogging("UserInterface")
    # ShowLogging("SString")
    # ShowLogging("Determiners")

    print(two_girls_have_an_ice_cream())