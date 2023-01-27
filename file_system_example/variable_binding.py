class VariableData(object):
    def __init__(self, name):
        self.name = name

# Use None in variable_data to represent a value
# That is not bound to an actual variable
class VariableBinding(object):
    def __init__(self, variable_data, value):
        self.value = value
        self.variable = variable_data


def variable_binding_iterator(variable_data, iterator):
    for item in iterator:
        yield VariableBinding(variable_data, item)
