class VariableData(object):
    # These are the defaults if a variable has never been set
    def __init__(self, name, is_collective=None, cardinal=None):
        self.name = name
        self.is_collective = is_collective
        self.cardinal = cardinal

    def __repr__(self):
        return f"{self.name}"

    def copy_with_changes(self, is_collective=None, cardinal=None):
        return VariableData(self.name,
                            is_collective=is_collective if is_collective is not None else self.is_collective,
                            cardinal=cardinal if cardinal is not None else self.cardinal)


# Use None in variable_data to represent a value
# That is not bound to an actual variable
class VariableBinding(object):
    def __init__(self, variable_data, value):
        self.value = value
        self.variable = variable_data

    def __repr__(self):
        return f"{self.variable}={self.value}"


