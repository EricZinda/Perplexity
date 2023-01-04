import copy


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

    # A standard "class method" is just a function definition,
    # indented properly, with "self" as the first argument

    # This is how predications will access the current value
    # of MRS variables like "x1" and "e1"
    def get_variable(self, variable_name):
        # "get()" is one way to access a value in a dictionary.
        # The second argument, "None", is what to return if the
        # key doesn't exist.  "None" is a built-in value in Python
        # like "null"
        return self.variables.get(variable_name, None)

    # This is how predications will set the value
    # of an "x" variable
    def set_x(self, variable_name, item):
        # Make a *copy* of the entire object using the built-in Python
        # class called "copy", we pass it "self" so it copies this
        # instance of the object
        new_state = copy.deepcopy(self)

        # Now we have a new "State" object with the same
        # world state that we can modify.

        # Dictionaries hold name/value pairs.
        # This is how you assign values to keys in dictionaries
        new_state.variables[variable_name] = item

        # "return" returns to the caller the new state with
        # that one variable set to a new value
        return new_state

    def add_to_e(self, eventName, key, value):
        newState = copy.deepcopy(self)
        if newState.get_variable(eventName) is None:
            newState.variables[eventName] = dict()

        newState.variables[eventName][key] = value
        return newState

    # This is an iterator (described above) that returns
    # all the objects in the world
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
