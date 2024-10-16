import copy
import inspect
import sys

from perplexity.utilities import ShowLogging


class TreePredication(object):
    def __init__(self, index, name, args):
        self.index = index
        self.name = name
        self.args = args

    def __repr__(self):
        return f"{self.name}({','.join([str(x) for x in self.args])})"


class Vocabulary(object):
    def __init__(self):
        self.name_function_map = {}

    def get_signature(self, name, args):
        return f"{name}({','.join(args)})"

    def add_predication(self, name, args, module, function):
        signature = self.get_signature(name, arg_types_from_names(args))
        self.name_function_map[signature] = (module, function)

    def predication(self, tree_predication):
        signature = self.get_signature(tree_predication.name, arg_types_from_names(tree_predication.args))
        return self.name_function_map.get(signature, None)


vocabulary = Vocabulary()


def arg_types_from_names(args):
    type_list = []
    for arg_name in args:
        # Allow single character arguments like "x" and "e"
        # OR the format: "x_actor", "xActor", etc
        if isinstance(arg_name, TreePredication):
            type_list.append("h")
        else:
            arg_type = arg_name[0]
            if arg_type not in ["u", "i", "p", "e", "x", "h", "c"]:
                raise Exception(
                    f"unknown argument type of {arg_type}'")

            type_list.append(arg_type)

    return type_list


# Decorator that adds maps a DELPH-IN predicate to a Python function
def Predication(vocabulary, name=None):

    def arg_types_from_function(function):
        arg_spec = inspect.getfullargspec(function)

        # Skip the first arg since it should always be "state"
        arg_list = arg_types_from_names(arg_spec.args[1:])

        return arg_list

    def predication_decorator(function_to_decorate):
        arg_list = arg_types_from_function(function_to_decorate)

        vocabulary.add_predication(name,
                                   arg_list,
                                   function_to_decorate.__module__,
                                   function_to_decorate.__name__)

        return function_to_decorate

    return predication_decorator


class File:
    def __init__(self, name, size=0):
        self.name = name
        self.size = size

    def __repr__(self):
        return f"File({self.name}, {self.size})"


class Folder:
    def __init__(self, name):
        self.name = name

    def __repr__(self):
        return f"Folder({self.name})"


# Use None in variable_data to represent a value
# That is not bound to an actual variable
class VariableBinding(object):
    def __init__(self, variable_data, value):
        self.value = value
        self.variable = variable_data

    def __repr__(self):
        return f"{self.variable}={self.value}"


class VariableData(object):
    def __init__(self, name):
        self.name = name

    def __repr__(self):
        return f"{self.name}"


# "class" declares an object-oriented class in Python
# The parenthesis after the "State" class name surround
# the object the class derives from (object)
class State(object):
    # All class methods are indented under the
    # class and take "self" as their first argument.
    # "self" represents the class instance.

    # "__init__" is a special method name that
    # indicates the constructor, which is called to create
    # a new instance of the class. Arguments beyond "self"
    # get passed to the function when the instance is created
    def __init__(self, objects):
        # Class member variables are created by
        # simply assigning to them
        self.variables = dict()  # an empty dictionary

        # "objects" are passed to us as an argument
        # by whoever creates an instance of the class
        self.objects = objects

    # A standard "class method" is just a function definition,
    # indented properly, with "self" as the first argument

    # This is how predications will access the current value
    # of MRS variables like "x1" and "e1"
    def get_binding(self, variable_name):
        # "get()" is one way to access a value in a dictionary.
        # The second argument is what to return if the
        # key doesn't exist.  "VariableBinding" is the class that
        # represents a variable binding in Perplexity
        return self.variables.get(variable_name, VariableBinding(VariableData(variable_name), None))

    # This is how predications will set the value
    # of an "x" variable (or another type of variable
    # that is acting like an unquantified "x" variable)
    def set_x(self, variable_name, item):
        # Make a *copy* of the entire object using the built-in Python
        # class called "copy", we pass it "self" so it copies this
        # instance of the object
        new_state = copy.deepcopy(self)

        # Now we have a new "State" object with the same
        # world state that we can modify.

        # Find a common mistakes early: item must always be a tuple
        # since x values are sets
        assert item is None or isinstance(item, tuple)

        if variable_name in new_state.variables:
            # Need to copy the item so that if the list is changed it won't affect
            # the state which is supposed to be immutable
            variable_data = copy.deepcopy(new_state.variables[variable_name].variable)
        else:
            variable_data = VariableData(variable_name)

        new_state.variables[variable_name] = VariableBinding(variable_data, copy.deepcopy(item))

        # "return" returns to the caller the new state with
        # that one variable set to a new value
        return new_state

    def add_to_e(self, event_name, key, value):
        newState = copy.deepcopy(self)
        e_binding = newState.get_binding(event_name)
        if e_binding.value is None:
            e_binding = VariableBinding(VariableData(event_name), dict())
            newState.variables[event_name] = e_binding

        e_binding.value[key] = value
        return newState

    # This is an iterator (described above) that returns
    # all the objects in the world bound to the specified variable
    def all_individuals(self):
        for item in self.objects:
            yield item


@Predication(vocabulary, name="_file_n_of")
def _file_n_of(state, x, i):
    x_value = state.get_binding(x).value
    if x_value is None:
        # Variable is unbound:
        # iterate over all individuals in the world
        # using the iterator returned by state.AllIndividuals()
        iterator = state.all_individuals()
    else:
        # Variable is bound: create an iterator that will iterate
        # over just that one by creating a list and adding it as
        # the only element
        # Remember that we are ignoring the fact that bindings are tuples
        # in these examples so we assume there is only one value, and
        # just retrieve it
        iterator = [x_value[0]]

    # By converting both cases to an iterator, the code that
    # checks if x is "a folder" can be shared
    for item in iterator:
        # "isinstance" is a built-in function in Python that
        # checks if a variable is an
        # instance of the specified class
        if isinstance(item, File):
            # state.SetX() returns a *new* state that
            # is a copy of the old one with just that one
            # variable set to a new value
            # Variable bindings are always tuples so we set
            # this one using the tuple syntax: (item, )
            new_state = state.set_x(x, (item, ))
            yield new_state


@Predication(vocabulary, name="_folder_n_of")
def folder_n_of(state, x, i):
    x_value = state.get_binding(x).value
    if x_value is None:
        # Variable is unbound:
        # iterate over all individuals in the world
        # using the iterator returned by state.AllIndividuals()
        iterator = state.all_individuals()
    else:
        # Variable is bound: create an iterator that will iterate
        # over just that one by creating a list and adding it as
        # the only element
        # Remember that we are ignoring the fact that bindings are tuples
        # in these examples so we assume there is only one value, and
        # just retrieve it
        iterator = [x_value[0]]

    # By converting both cases to an iterator, the code that
    # checks if x is "a folder" can be shared
    for item in iterator:
        # "isinstance" is a built-in function in Python that
        # checks if a variable is an
        # instance of the specified class
        if isinstance(item, Folder):
            # state.SetX() returns a *new* state that
            # is a copy of the old one with just that one
            # variable set to a new value
            # Variable bindings are always tuples so we set
            # this one using the tuple syntax: (item, )
            new_state = state.set_x(x, (item, ))
            yield new_state


@Predication(vocabulary, name="_large_a_1")
def large_a_1(state, e, x):
    x_value = state.get_binding(x).value
    if x_value is None:
        # Variable is unbound:
        # iterate over all individuals in the world
        # using the iterator returned by state.AllIndividuals()
        iterator = state.all_individuals()
    else:
        # Variable is bound: create an iterator that will iterate
        # over just that one by creating a list and adding it as
        # the only element
        # Remember that we are ignoring the fact that bindings are tuples
        # in these examples so we assume there is only one value, and
        # just retrieve it
        iterator = [x_value[0]]

    # By converting both cases to an iterator, the code that
    # checks if x is "a folder" can be shared
    for item in iterator:
        # "isinstance" is a built-in function in Python that
        # checks if a variable is an
        # instance of the specified class
        if isinstance(item, File) and item.size > 1000:
            # state.SetX() returns a *new* state that
            # is a copy of the old one with just that one
            # variable set to a new value
            # Variable bindings are always tuples so we set
            # this one using the tuple syntax: (item, )
            new_state = state.set_x(x, (item, ))
            yield new_state


@Predication(vocabulary, name="_a_q")
def a_q(state, x, h_rstr, h_body):
    for rstr_solution in call(vocabulary, state, h_rstr):
        for body_solution in call(vocabulary, rstr_solution, h_body):
            yield body_solution
            return


# Takes a TreePredication object, maps it to a Python function and calls it
def call_predication(vocabulary, state, predication):
    # Look up the actual Python module and
    # function name given a string like "folder_n_of".
    # "vocabulary.Predication" returns a two-item list,
    # where item[0] is the module and item[1] is the function
    module_function = vocabulary.predication(predication)

    if module_function is None:
        raise Exception(f"Implementation for Predication {predication} not found")

    # sys.modules[] is a built-in Python list that allows you
    # to access actual Python Modules given a string name
    module = sys.modules[module_function[0]]

    # Functions are modeled as properties of modules in Python
    # and getattr() allows you to retrieve a property.
    # So: this is how we get the "function pointer" to the
    # predication function we wrote in Python
    function = getattr(module, module_function[1])

    # [list] + [list] will return a new, combined list
    # in Python. This is how we add the state object
    # onto the front of the argument list
    predication_args = predication.args
    function_args = [state] + predication_args

    # You call a function "pointer" and pass it arguments
    # that are a list by using "function(*function_args)"
    # So: this is actually calling our function (which
    # returns an iterator and thus we can iterate over it)
    for next_state in function(*function_args):
        yield next_state


def call(vocabulary, state, term):
    # See if the first thing in the list is actually a list
    # If so, we have a conjunction
    if isinstance(term, list):
        # If "term" is an empty list, we have solved all
        # predications in the conjunction, return the final answer.
        # "len()" is a built-in Python function that returns the
        # length of a list
        if len(term) == 0:
            yield state
        else:
            # This is a list of predications, so they should
            # be treated as a conjunction.
            # call each one and pass the state it returns
            # to the next one, recursively
            for nextState in call(vocabulary, state, term[0]):
                # Note the [1:] syntax which means "return a list
                # of everything but the first item"
                yield from call(vocabulary, nextState, term[1:])

    else:
        # The first thing in the list was not a list
        # so we assume it is just a TreePredication term.
        # Evaluate it using call_predication
        yield from call_predication(vocabulary, state, term)


def Example0():
    state = State([Folder(name="Desktop"),
                   Folder(name="Documents"),
                   File(name="file1.txt"),
                   File(name="file2.txt")])


def Example1():
    state = State([Folder(name="Desktop"),
                   Folder(name="Documents"),
                   File(name="file1.txt"),
                   File(name="file2.txt")])

    for item in folder_n_of(state, "x1"):
        print(item.variables)

    print("\nThe original `state` object is not changed:")
    print(state.variables)


def Example1a():
    state = State([Folder(name="Desktop"),
                   Folder(name="Documents"),
                   File(name="file1.txt", size=1000),
                   File(name="file2.txt", size=2000)])

    for item in large_a_1(state, "e1", "x1"):
        print(item.variables)


# List folders using call_predication
def Example2():
    state = State([Folder(name="Desktop"),
                   Folder(name="Documents"),
                   File(name="file1.txt"),
                   File(name="file2.txt")])

    for item in call_predication(vocabulary,
                                 state,
                                 TreePredication(0, "_folder_n_of", ["x1", "i1"])):
        print(item.variables)


# "Large files" using a conjunction
def Example3():
    state = State([Folder(name="Desktop"),
                   Folder(name="Documents"),
                   File(name="file1.txt", size=100),
                   File(name="file2.txt", size=2000000)])

    tree = [TreePredication(0, "_large_a_1", ["e1", "x1"]),
            TreePredication(1, "_file_n_of", ["x1", "i1"])]

    for item in call(vocabulary, state, tree):
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

    for item in call(vocabulary, state, tree):
        print(item.variables)

# def solve_and_respond(state, mrs):
#     context = ExecutionContext(vocabulary)
#     solutions = list(context.solve_mrs_tree(state, mrs))
#     return respond_to_mrs_tree(state, mrs, solutions, context.error())

#

#
#

#
#

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




if __name__ == '__main__':
    ShowLogging("Pipeline")
    ShowLogging("SolutionGroups")
    # ShowLogging("Execution")
    # ShowLogging("Generation")
    # ShowLogging("UserInterface")
    # ShowLogging("SString")
    # ShowLogging("Determiners")

    # Early examples need a context to set the vocabulary since
    # respond_to_mrs hadn't been built yet
    # Example0()
    # Example1()
    # Example1a()
    # Example2()
    # Example3()
    Example4()
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
