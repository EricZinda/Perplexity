import copy
import logging
from perplexity.response import RespondOperation, NoMoreSolutionGroups
from perplexity.set_utilities import DisjunctionValue
from perplexity.variable_binding import VariableBinding, VariableData


class LoadException(Exception):
    pass


def apply_solutions_to_state(state, has_more_func, solutions, record_operations=False):
    # Collect all the operations that were done
    responses = []
    last_phrase_response_operations = []
    last_solution_group = False
    all_operations = []
    has_more = None
    for solution in solutions:
        for operation in solution.get_operations():
            if isinstance(operation, RespondOperation):
                if operation.show_if_has_more and has_more is None:
                    # Only call the has_more_func if we will use it since it requires finding
                    # a second solution which could be expensive
                    has_more = has_more_func()

                if not operation.show_if_last_phrase:
                    response_string = operation.response_string(state=state, has_more=has_more)
                    if response_string is not None and response_string not in responses:
                        responses.append(response_string)

                else:
                    # This is an operation that is only meant to be shown if it is part of the last
                    # phrase in a series. Such as "No. I'll take something else.  Thank you."
                    # The caller has to decide if it is the last phrase or not, we just collect them here
                    last_phrase_response_operations.append(operation)
            elif isinstance(operation, NoMoreSolutionGroups):
                last_solution_group = True
            else:
                all_operations.append(operation)

    # Now apply all the operations to the original state object
    if pipeline_logger.level == logging.DEBUG:
        pipeline_logger.debug("State changes:\n" + "\n".join([("   " + str(x) if x is not None else "   None") for x in all_operations]))
        pipeline_logger.debug("\n".join([("   " + str(x) if x is not None else "   None") for x in responses]))
    new_state = state.apply_operations(all_operations, record_operations)

    # Now that we have the final state, get the string for the last operations if there is one
    last_phrase_responses = []
    if last_phrase_response_operations:
        for operation in last_phrase_response_operations:
            if operation.show_if_has_more and has_more is None:
                # Only call the has_more_func if we will use it since it requires finding
                # a second solution which could be expensive
                has_more = has_more_func()
            response_string = operation.response_string(state=new_state, has_more=has_more)
            if response_string not in last_phrase_responses:
                last_phrase_responses.append(response_string)

    return responses, last_phrase_responses, new_state, last_solution_group


class SetXOperation(object):
    def __init__(self, x_name, value):
        self._x_name = x_name
        self.value = value

    def apply_to(self, state):
        return state.set_x(self._x_name, self.value)


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

        self.frame_name = "default"

    # Defines what the default printed output of a state object is
    def __repr__(self):
        return ", ".join([str(variable_item[1]) for variable_item in self.variables.items() if variable_item[0] != 'tree'])

    def world_state_frame(self):
        return self

    # A standard "class method" is just a function definition,
    # indented properly, with "self" as the first argument

    # This is how predications will access the current value
    # of MRS variables like "x1" and "e1"
    def get_binding(self, variable_name):
        # Find a common mistakes early
        assert not isinstance(variable_name, VariableBinding)

        # "get()" is one way to access a value in a dictionary.
        # The second argument is what to return if the
        # key doesn't exist.  "VariableBinding" is the class that
        # represents a variable binding in Perplexity
        return self.variables.get(variable_name, VariableBinding(VariableData(variable_name), None))

    def set_variable_data(self, variable_name, determiner=None, quantifier=None, combined_variables=None):
        binding = self.get_binding(variable_name)
        return self.set_x(variable_name, binding.value, binding.variable.combinatoric, determiner=determiner, quantifier=quantifier, combined_variables=combined_variables)

    # This is how predications will set the value
    # of an "x" variable (or another type of variable
    # that is acting like an unquantified "x" variable)
    def set_x(self, variable_name, item, combinatoric=False, determiner=None, quantifier=None, combined_variables=None):
        # Make a *copy* of the entire object using the built-in Python
        # class called "copy", we pass it "self" so it copies this
        # instance of the object
        new_state = copy.deepcopy(self)

        # Now we have a new "State" object with the same
        # world state that we can modify.

        # Find a common mistakes early
        assert not isinstance(item, VariableBinding), "set_x value must be a tuple(), not a VariableBinding"
        assert not isinstance(item, DisjunctionValue), "TODO: helper functions like combinatorial_predication_1 should strip DisjunctionValue"
        if not (item is None or isinstance(item, tuple)):
            assert item is None or isinstance(item, tuple), "set_x value must be a tuple()"
        if variable_name in new_state.variables:
            initial_variable_data = new_state.variables[variable_name].variable
        else:
            initial_variable_data = VariableData(variable_name, combinatoric)

        variable_data = initial_variable_data.copy_with_changes(combinatoric=combinatoric,
                                                                determiner=determiner,
                                                                quantifier=quantifier,
                                                                combined_variables=combined_variables)

        # Need to copy the item so that if the list is changed it won't affect
        # the state which is supposed to be immutable
        new_state.variables[variable_name] = VariableBinding(variable_data, copy.deepcopy(item))

        # "return" returns to the caller the new state with
        # that one variable set to a new value
        return new_state

    def add_to_e(self, event_name, key, value):
        # Find a common mistakes early
        assert not isinstance(event_name, VariableBinding)

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
    def record_operations(self, operation_list):
        newState = copy.deepcopy(self)
        for operation in operation_list:
            newState.operations.append(operation)

        return newState

    # Call to apply a list of operations to
    # a new State object
    def apply_operations(self, operation_list, record_operations=True):
        newState = copy.deepcopy(self)
        for operation in operation_list:
            operation.apply_to(newState)
            if record_operations:
                newState.operations.append(operation)

        return newState

    def get_operations(self):
        return copy.deepcopy(self.operations)


pipeline_logger = logging.getLogger('Pipeline')
