import copy
import inspect
import os
import sys
import uuid
from delphin import ace
from perplexity.tree_algorithm_zinda2020 import valid_hole_assignments
from perplexity.utilities import ShowLogging, parse_predication_name
from perplexity.erg import erg_file


class UniqueObject(object):
    def __init__(self):
        self.unique_id = uuid.uuid4()


# Represents something that can "do" things, like a computer
# or a human (or a dog, etc)
class Actor(UniqueObject):
    def __init__(self, name, person):
        super().__init__()
        self.name = name
        self.person = person

    def __repr__(self):
        return f"Actor(name={self.name}, person={self.person})"


class TreePredication(object):
    def __init__(self, index, name, args):
        self.index = index
        self.name = name
        self.args = args

    def __repr__(self):
        return f"{self.name}({','.join([str(x) for x in self.args])})"


# walk_tree_predications_until() is a helper function that just walks
# the tree represented by "term". For every predication found,
# it calls func(found_predication)
# If func returns anything besides "None", it quits and
# returns that value
def walk_tree_predications_until(term, func):
    if isinstance(term, list):
        # This is a conjunction, recurse through the
        # items in it
        for item in term:
            result = walk_tree_predications_until(item, func)
            if result is not None:
                return result

    else:
        # This is a single term, call func with it if it is a predication
        if isinstance(term, TreePredication):
            result = func(term)
            if result is not None:
                return result

            # If func didn't say to quit, see if any of its terms are scopal
            # i.e. are predications themselves
            for arg in term.args:
                if not isinstance(arg, str):
                    result = walk_tree_predications_until(arg, func)
                    if result is not None:
                        return result

    return None


# Walk the tree represented by "term" and
# return the predication that matches
# "predicate_name" or "None" if none is found
def find_predication(term, predication_name):
    if isinstance(predication_name, list):
        predication_names = predication_name
    else:
        predication_names = [predication_name]

    # This function gets called for every predication
    # in the tree. It is a private function since it is
    # only used here
    def match_predication_name(predication):
        if predication.name in predication_names:
            return predication
        else:
            return None

    # Pass our private function to WalkTreeUntil as
    # a way to filter through the tree to find
    # predication_name
    return walk_tree_predications_until(term, match_predication_name)


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
        if isinstance(arg_name, (TreePredication, list)):
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


class File(UniqueObject):
    def __init__(self, name, size=0):
        super().__init__()
        self.name = name
        self.size = size

    def __repr__(self):
        return f"File({self.name}, {self.size})"


class Folder(UniqueObject):
    def __init__(self, name):
        super().__init__()
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

        # Remember all the operations applied to the state object
        self.operations = []

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

    # Call to apply a list of operations to
    # a new State object
    def apply_operations(self, operation_list):
        newState = copy.deepcopy(self)
        for operation in operation_list:
            operation.apply_to(newState)
            newState.operations.append(operation)

        return newState

    def get_operations(self):
        return copy.deepcopy(self.operations)


# Delete any object in the system
class DeleteOperation(object):
    def __init__(self, object_to_delete):
        self.object_to_delete = object_to_delete

    def apply_to(self, state):
        for index in range(0, len(state.objects)):
            # Use the `unique_id` property to compare objects since they
            # may have come from different `State` objects and will thus be copies
            if state.objects[index].unique_id == self.object_to_delete.unique_id:
                state.objects.pop(index)
                break


@Predication(vocabulary, name="_delete_v_1")
def delete_v_1(state, e_introduced, x_actor, x_what):
    # We only know how to delete things from the
    # computer's perspective
    x_actor_value = state.get_binding(x_actor).value
    if x_actor_value is not None and len(x_actor_value) == 1 and isinstance(x_actor_value[0], Actor) and x_actor_value[0].name == "Computer":
        x_what_value = state.get_binding(x_what).value

        # Only handle deleting one object at a time, don't support "together"
        if len(x_what_value) == 1:
            yield state.apply_operations([DeleteOperation(x_what_value[0])])


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
        if isinstance(item, File):
            if item.size > 1000:
                # state.SetX() returns a *new* state that
                # is a copy of the old one with just that one
                # variable set to a new value
                # Variable bindings are always tuples so we set
                # this one using the tuple syntax: (item, )
                new_state = state.set_x(x, (item, ))
                yield new_state
            else:
                context().report_error(["notLarge", item])


@Predication(vocabulary, name="_a_q")
def a_q(state, x, h_rstr, h_body):
    for rstr_solution in call(vocabulary, state, h_rstr):
        for body_solution in call(vocabulary, rstr_solution, h_body):
            yield body_solution
            return


@Predication(vocabulary, name="_which_q")
def which_q(state, x_variable, h_rstr, h_body):
    yield from default_quantifier(state, x_variable, h_rstr, h_body)


def default_quantifier(state, x_variable, h_rstr, h_body):
    # Find every solution to RSTR
    for solution in call(vocabulary, state, h_rstr):
        # And return it if it is true in the BODY
        for body_solution in call(vocabulary, solution, h_body):
            yield body_solution


@Predication(vocabulary, name="pron")
def pron(state, x_who):
    mrs = state.get_binding("mrs").value[0]
    person = mrs["Variables"][x_who]["PERS"]
    for item in state.all_individuals():
        if isinstance(item, Actor) and item.person == person:
            yield state.set_x(x_who, (item, ))
            break


# This is just used as a way to provide a scope for a
# pronoun, so it only needs the default behavior
@Predication(vocabulary, name="pronoun_q")
def pronoun_q(state, x, h_rstr, h_body):
    yield from default_quantifier(state, x, h_rstr, h_body)


# Get the SF property of the Index of the MRS
def sentence_force(mrs):
    if "Index" in mrs:
        if mrs["Index"] in mrs["Variables"]:
            if "SF" in mrs["Variables"][mrs["Index"]]:
                return mrs["Variables"][mrs["Index"]]["SF"]


def respond_to_mrs(state, mrs):
    # Collect all the solutions to the MRS against the
    # current world state
    solutions = []
    for item in call(vocabulary, state, mrs["RELS"]):
        solutions.append(item)

    error = generate_message(state, context().deepest_error()) if len(solutions) == 0 else None
    force = sentence_force(mrs)
    if force == "prop":
        # This was a proposition, so the user only expects
        # a confirmation or denial of what they said.
        # The phrase was "true" if there was at least one answer
        if len(solutions) > 0:
            print("Yes, that is true.")
        else:
            print(f"No, that isn't correct:{error}")

    elif force == "ques":
        # See if this is a "WH" type question
        wh_predication = find_predication(mrs["RELS"], "_which_q")
        if wh_predication is None:
            # This was a simple question, so the user only expects
            # a yes or no.
            # The phrase was "true" if there was at least one answer
            if len(solutions) > 0:
                print("Yes.")
            else:
                print(f"No, {error}")
        else:
            # This was a "WH" question
            # return the values of the variable asked about
            # from the solution
            # The phrase was "true" if there was at least one answer
            if len(solutions) > 0:
                wh_variable = wh_predication.args[0]
                for solutions in solutions:
                    print(solutions.get_binding(wh_variable).value)
            else:
                print(f"{error}")

    elif force == "comm":
        # This was a command so, if it works, just say so
        # We'll get better errors and messages in upcoming sections
        if len(solutions) > 0:
            # Collect all the operations that were done
            all_operations = []
            for solution in solutions:
                all_operations += solution.get_operations()

            # Now apply all the operations to the original state object and
            # print it to prove it happened
            final_state = state.apply_operations(all_operations)

            print("Done!")
            print(final_state.objects)
        else:
            print(f"Couldn't do that: {error}")


class ExecutionContext(object):
    def __init__(self):
        self._error = None
        self._error_predication_index = -1
        self._predication_index = -1

    def deepest_error(self):
        return self._error

    def report_error(self, error):
        if self._error_predication_index < self._predication_index:
            self._error = error
            self._error_predication_index = self._predication_index

    def call(self, vocabulary, state, term):
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
                for nextState in self.call(vocabulary, state, term[0]):
                    # Note the [1:] syntax which means "return a list
                    # of everything but the first item"
                    yield from self.call(vocabulary, nextState, term[1:])

        else:
            # The first thing in the list was not a list
            # so we assume it is just a TreePredication term.
            # Evaluate it using call_predication
            last_predication_index = self._predication_index
            self._predication_index += 1

            yield from self.call_predication(vocabulary, state, term)

            # Restore it since we are recursing
            self._predication_index = last_predication_index

    # Takes a TreePredication object, maps it to a Python function and calls it
    def call_predication(self, vocabulary, state, predication):
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


# helpers to make the early samples work
def call(vocabulary, state, term):
    yield from context().call(vocabulary, state, term)


def call_predication(self, vocabulary, state, predication):
    yield from context().call_predication(vocabulary, state, predication)


# Create a global execution context
execution_context = ExecutionContext()


# Helper to access the global context so code is isolated from
# how we manage it
def context():
    return execution_context


def mrss_from_phrase(phrase):
    # Don't print errors to the screen
    f = open(os.devnull, 'w')

    # Create an instance of the ACE parser and ask to give <= 25 MRS documents
    with ace.ACEParser(erg_file(), cmdargs=['-n', '25'], stderr=f) as parser:
        ace_response = parser.interact(phrase)

    for parse_result in ace_response.results():
        yield parse_result.mrs()


def trees_from_mrs(mrs):
    # Create a dict of predications using their labels as each key
    # for easy access when building trees
    # Note that a single label could represent multiple predications
    # in conjunction so we need a list for each label
    mrs_predication_dict = {}
    for predication in mrs.predications:
        if predication.label not in mrs_predication_dict.keys():
            mrs_predication_dict[predication.label] = []
        mrs_predication_dict[predication.label].append(predication)

    # Iteratively return well-formed trees from the MRS
    for new_mrs, holes_assignments in valid_hole_assignments(mrs, max_holes=12, required_root_label=None):
        # valid_hole_assignments can return None if the grammar returns something
        # that doesn't have the same number of holes and floaters (which is a grammar bug)
        if holes_assignments is not None:
            # Now we have the assignments of labels to holes, but we need
            # to actually build the *tree* using that information
            well_formed_tree = tree_from_assignments(mrs.top,
                                                     holes_assignments,
                                                     mrs_predication_dict,
                                                     mrs)
            yield well_formed_tree


def tree_from_assignments(hole_label, assignments, predication_dict, mrs, index=None):
    if index is None:
        # Use a list so the value will get modified during recursion
        index = [0]

    # Get the list of predications that should fill in the hole
    # represented by labelName
    if hole_label in assignments.keys():
        predication_list = predication_dict[assignments[hole_label]]
    else:
        predication_list = predication_dict[hole_label]

    # predication_list is a list because multiple items might
    # have the same key and should be put in conjunction (i.e. be and'd together)
    conjunction_list = []
    for predication in predication_list:
        predication_name = predication.predicate

        # Recurse through this predication's arguments
        # and look for any scopal arguments to recursively convert
        args = []
        for arg_name in predication.args.keys():
            original_arg = predication.args[arg_name]

            # CARG arguments contain strings that are never
            # variables, they are constants
            if arg_name in ["CARG"]:
                final_arg = original_arg
            else:
                argType = original_arg[0]
                if argType == "h":
                    final_arg = tree_from_assignments(original_arg, assignments, predication_dict, mrs, index)
                else:
                    final_arg = original_arg

            args.append(final_arg)

        conjunction_list.append(TreePredication(index=index[0], name=predication_name, args=args))
        index[0] += 1

    return conjunction_list


def generate_message(state, error):
    # "error" is a list like: ["name", arg1, arg2, ...]. The first item is the error
    # constant (i.e. its name). What the args mean depends on the error.
    error_constant = error[0] if error is not None else "no error set"
    arg_length = len(error) if error is not None else 0
    arg1 = error[1] if arg_length > 1 else None
    arg2 = error[2] if arg_length > 2 else None
    arg3 = error[3] if arg_length > 3 else None

    if error_constant == "notAThing":
        return f"a '{arg1}' is not a '{arg2}'"

    elif error_constant == "notLarge":
        return f"'{arg1}' is not large"

    else:
        return str(error)


# Given the index where an error happened and a variable,
# return what that variable "is" up to that point (i.e. its "domain")
# in English
def english_for_delphin_variable(failure_index, variable, mrs):
    # Integers can't be passed by reference in Python, so we need to pass
    # the current index in a list so it can be changed as we iterate
    current_predication_index = [0]

    # This function will be called for every predication in the MRS
    # as we walk it in execution order
    def RecordPredicationsUntilFailureIndex(predication):
        # Once we have hit the index where the failure happened, stop
        if current_predication_index[0] == failure_index:
            return False
        else:
            # See if this predication can contribute anything to the
            # description of the variable we are describing. If so,
            # collect it in nlg_data
            refine_NLG_with_predication(variable, predication, nlg_data)
            current_predication_index[0] = current_predication_index[0] + 1
            return None

    nlg_data = {}

    # WalkTreeUntil() walks the predications in mrs["RELS"] and calls
    # the function RecordPredicationsUntilFailureIndex(), until hits the
    # failure_index position
    walk_tree_predications_until(mrs["RELS"], RecordPredicationsUntilFailureIndex)

    # Take the data we gathered and convert to English
    return convert_to_english(nlg_data)


# Takes the information gathered in the nlg_data dictionary
# and converts it, in a very simplistic way, to English
def convert_to_english(nlg_data):
    phrase = ""

    if "Quantifier" in nlg_data:
        phrase += nlg_data["Quantifier"] + " "
    else:
        phrase += "a "

    if "Topic" in nlg_data:
        phrase += nlg_data["Topic"]
    else:
        phrase += "thing"

    return phrase


# See if this predication in any way contributes words to
# the variable specified. Put whatever it contributes in nlg_data
def refine_NLG_with_predication(variable, predication, nlg_data):
    # Parse the name of the predication to find out its
    # part of speech (POS) which could be a noun ("n"),
    # quantifier ("q"), etc.
    parsed_predication = parse_predication_name(predication.name)

    # If the predication has this variable as its first argument,
    # it either *introduces* it, or is quantifying it
    if predication.args[0] == variable:
        if parsed_predication["Pos"] == "q":
            # It is quantifying it
            nlg_data["Quantifier"] = parsed_predication["Lemma"]
        else:
            # It is introducing it, thus it is the "main" description
            # of the variable, usually a noun predication
            nlg_data["Topic"] = parsed_predication["Lemma"]


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


def Example5():
    for mrs in mrss_from_phrase("2 files are large"):
        print(mrs)


def Example6():
    for mrs in mrss_from_phrase("2 files are large"):
        print(mrs)
        for tree in trees_from_mrs(mrs):
            print(tree)
        print()


# Evaluate the proposition: "a file is large"
def Example7():
    state = State([Folder(name="Desktop"),
                   Folder(name="Documents"),
                   File(name="file1.txt", size=2000000),
                   File(name="file2.txt", size=2000000)])

    # Start with an empty dictionary
    mrs = {}

    # Set its "index" key to the value "e2"
    mrs["Index"] = "e2"

    # Set its "Variables" key to *another* dictionary with
    # keys that represent the variables. Each of those has a "value" of
    # yet another dictionary that holds the properties of the variables
    # For now we'll just fill in the SF property
    mrs["Variables"] = {"x3": {},
                        "i1": {},
                        "e2": {"SF": "prop"}}

    # Set the "RELS" key to the scope-resolved MRS tree
    mrs["RELS"] = TreePredication(0, "_a_q", ["x3",
                                              TreePredication(1, "_file_n_of", ["x3", "i1"]),
                                              TreePredication(2, "_large_a_1", ["e2", "x3"])])

    respond_to_mrs(state, mrs)


# Evaluate the proposition: "which file is large?"
def Example8():
    state = State([Folder(name="Desktop"),
                   Folder(name="Documents"),
                   File(name="file1.txt", size=2000000),
                   File(name="file2.txt", size=100)])

    # Start with an empty dictionary
    mrs = {}

    # Set its "index" key to the value "e2"
    mrs["Index"] = "e2"

    # Set its "Variables" key to *another* dictionary with
    # keys that represent the variables. Each of those has a "value" of
    # yet another dictionary that holds the properties of the variables
    # For now we'll just fill in the SF property
    mrs["Variables"] = {"x3": {},
                        "i1": {},
                        "e2": {"SF": "ques"}}

    # Set the "RELS" key to the scope-resolved MRS tree
    mrs["RELS"] = TreePredication(0, "_which_q", ["x3",
                                                 TreePredication(1, "_file_n_of", ["x3", "i1"]),
                                                 TreePredication(2, "_large_a_1", ["e2", "x3"])])

    respond_to_mrs(state, mrs)


# Delete a large file
def Example9():
    state = State([Actor(name="Computer", person=2),
                   Folder(name="Desktop"),
                   Folder(name="Documents"),
                   File(name="file1.txt", size=2000000),
                   File(name="file2.txt", size=1000000)])

    mrs = {}
    mrs["Index"] = "e2"
    mrs["Variables"] = {"x3": {"PERS": 2},
                        "x8": {},
                        "e2": {"SF": "comm"},
                        "e13": {}}

    mrs["RELS"] = TreePredication(0, "pronoun_q", ["x3",
                                                   TreePredication(1, "pron", ["x3"]),
                                                   TreePredication(0, "_a_q", ["x8",
                                                                               [TreePredication(1, "_file_n_of", ["x8", "i1"]), TreePredication(2, "_large_a_1", ["e1", "x8"])],
                                                                               TreePredication(3, "_delete_v_1", ["e2", "x3", "x8"])])]
                                     )

    state = state.set_x("mrs", (mrs,))
    respond_to_mrs(state, mrs)


# Delete a large file
def Example10():
    state = State([Actor(name="Computer", person=2),
                   Folder(name="Desktop"),
                   Folder(name="Documents"),
                   File(name="file1.txt", size=2000000),
                   File(name="file2.txt", size=1000000)])

    mrs = {}
    mrs["Index"] = "e2"
    mrs["Variables"] = {"x3": {"PERS": 2},
                        "x8": {},
                        "e2": {"SF": "comm"},
                        "e13": {}}

    mrs["RELS"] = TreePredication(0, "pronoun_q", ["x3",
                                                   TreePredication(1, "pron", ["x3"]),
                                                   TreePredication(0, "_a_q", ["x8",
                                                                               [TreePredication(1, "_file_n_of", ["x8", "i1"]), TreePredication(2, "_large_a_1", ["e1", "x8"])],
                                                                               TreePredication(3, "_delete_v_1", ["e2", "x3", "x8"])])]
                                     )

    state = state.set_x("mrs", (mrs,))
    respond_to_mrs(state, mrs)


# Generating English for "Delete a large file"
def Example11():
    state = State([Actor(name="Computer", person=2),
                   Folder(name="Desktop"),
                   Folder(name="Documents"),
                   File(name="file1.txt", size=2000000),
                   File(name="file2.txt", size=1000000)])

    mrs = {}
    mrs["Index"] = "e2"
    mrs["Variables"] = {"x3": {"PERS": 2},
                        "x8": {},
                        "e2": {"SF": "comm"},
                        "e13": {}}

    mrs["RELS"] = TreePredication(0, "pronoun_q", ["x3",
                                                   TreePredication(1, "pron", ["x3"]),
                                                   TreePredication(2, "_a_q", ["x8",
                                                                               [TreePredication(3, "_file_n_of", ["x8", "i1"]), TreePredication(2, "_large_a_1", ["e1", "x8"])],
                                                                               TreePredication(4, "_delete_v_1", ["e2", "x3", "x8"])])]
                                     )

    # Set index to failure in _a_q
    print(english_for_delphin_variable(2, "x8", mrs))

    # Set index to failure in _file_n_of
    print(english_for_delphin_variable(3, "x8", mrs))

    # Set index to failure in _large_a_1
    print(english_for_delphin_variable(4, "x8", mrs))


# Running Example7 results in:


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
    # Example4()
    # Example5()
    # Example6()
    # Example7()
    # Example5_1
    # Example8()
    # Example9()
    Example11()
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
