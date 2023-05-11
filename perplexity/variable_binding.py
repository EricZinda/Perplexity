import enum


class VariableValueType(enum.Enum):
    none = 0
    combinatoric = 1
    set = 2


class VariableData(object):
    # These are the defaults if a variable has never been set
    def __init__(self, name, value_type=VariableValueType.none, determiner=None, quantifier=None):
        self.name = name
        self.value_type = value_type
        self.determiner = determiner
        self.quantifier = quantifier

    def __repr__(self):
        return f"{self.name}({self.value_type})"

    def copy_with_changes(self, value_type=None, determiner=None, quantifier=None):
        return VariableData(self.name,
                            value_type=value_type if value_type is not None else self.value_type,
                            determiner=determiner if determiner is not None else self.determiner,
                            quantifier=quantifier if quantifier is not None else self.quantifier)


# Use None in variable_data to represent a value
# That is not bound to an actual variable
class VariableBinding(object):
    def __init__(self, variable_data, value):
        self.value = value
        self.variable = variable_data

    def __repr__(self):
        return f"{self.variable}={self.value}"


