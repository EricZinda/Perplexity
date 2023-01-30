class VariableData(object):
    def __init__(self, name):
        self.name = name

    def __repr__(self):
        return f"{self.name}"


# Use None in variable_data to represent a value
# That is not bound to an actual variable
class VariableBinding(object):
    def __init__(self, variable_data, value):
        self.value = value
        self.variable = variable_data

    def __repr__(self):
        return f"{self.variable}={self.value}"


