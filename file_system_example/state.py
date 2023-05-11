import copy
import logging
from file_system_example.objects import Actor
from perplexity.variable_binding import VariableBinding, VariableData, VariableValueType


# The state representation used by the file system example
# note that the core system doesn't care at all what this object
# looks like. It is only the predications that interact with it
#
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

    # Defines what the default printed output of a state object is
    def __repr__(self):
        return ", ".join([str(variable_item[1]) for variable_item in self.variables.items() if variable_item[0] != 'tree'])

    # A standard "class method" is just a function definition,
    # indented properly, with "self" as the first argument

    # This is how predications will access the current value
    # of MRS variables like "x1" and "e1"
    def get_binding(self, variable_name):
        # "get()" is one way to access a value in a dictionary.
        # The second argument, "None", is what to return if the
        # key doesn't exist.  "None" is a built-in value in Python
        # like "null"
        value = self.variables.get(variable_name, None)
        if value is None:
            return VariableBinding(VariableData(variable_name), None)
        else:
            return value

    def set_variable_data(self, variable_name, determiner=None, used_collective=None, quantifier=None):
        binding = self.get_binding(variable_name)
        return self.set_x(variable_name, binding.value, binding.variable.value_type, determiner=determiner, used_collective=used_collective, quantifier=quantifier)

    # This is how predications will set the value
    # of an "x" variable (or another type of variable
    # that is acting like an unquantified "x" variable)
    def set_x(self, variable_name, item, value_type: VariableValueType, determiner=None, used_collective=None, quantifier=None):
        # Make a *copy* of the entire object using the built-in Python
        # class called "copy", we pass it "self" so it copies this
        # instance of the object
        new_state = copy.deepcopy(self)

        # Now we have a new "State" object with the same
        # world state that we can modify.

        # Find a common mistakes early
        assert not isinstance(item, VariableBinding)
        assert item is None or isinstance(item, tuple)
        if variable_name in new_state.variables:
            initial_variable_data = new_state.variables[variable_name].variable
        else:
            initial_variable_data = VariableData(variable_name, value_type)

        variable_data = initial_variable_data.copy_with_changes(value_type=value_type,
                                                                determiner=determiner,
                                                                used_collective=used_collective,
                                                                quantifier=quantifier)

        # Need to copy the item so that if the list is changed it won't affect
        # the state which is supposed to be immutable
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


# Optimized for the file system example
class FileSystemState(State):
    def __init__(self, file_system):
        super().__init__([])
        self.file_system = file_system
        self.current_user = Actor(name="User", person=1, file_system=file_system)
        self.actors = [self.current_user,
                       Actor(name="Computer", person=2, file_system=file_system)]

    def all_individuals(self):
        yield from self.file_system.all_individuals()
        yield from self.actors

    def user(self):
        return self.current_user


# Delete any object in the system
class DeleteOperation(object):
    def __init__(self, binding_to_delete):
        self.binding_to_delete = binding_to_delete

    def apply_to(self, state):
        if isinstance(state, FileSystemState):
            state.file_system.delete_item(self.binding_to_delete)

        else:
            for index in range(0, len(state.objects)):
                # Use the `unique_id` property to compare objects since they
                # may have come from different `State` objects and will thus be copies
                if state.objects[index].unique_id == self.binding_to_delete.unique_id:
                    state.objects.pop(index)
                    break


class CopyOperation(object):
    def __init__(self, from_directory_binding, binding_from_copy, binding_to_copy):
        self.from_directory_binding = from_directory_binding
        self.binding_from_copy = binding_from_copy
        self.binding_to_copy = binding_to_copy

    def apply_to(self, state):
        if isinstance(state, FileSystemState):
            state.file_system.copy_item(self.from_directory_binding, self.binding_from_copy, self.binding_to_copy)


class ChangeDirectoryOperation(object):
    def __init__(self, folder_binding):
        self.folder_binding = folder_binding

    def apply_to(self, state):
        state.file_system.change_directory(self.folder_binding)


pipeline_logger = logging.getLogger('Pipeline')
