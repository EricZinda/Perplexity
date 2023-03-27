import enum


def is_collective_type(variable_value_type):
    return variable_value_type in [VariableValueType.combinatoric_collective, VariableValueType.collective]


class VariableValueType(enum.Enum):
    none = 0
    combinatoric_either = 1
    combinatoric_collective = 2
    combinatoric_distributive = 3
    collective = 4
    distributive = 5


class VariableData(object):
    # These are the defaults if a variable has never been set
    def __init__(self, name, value_type=VariableValueType.none, cardinal=None, used_collective=False):
        self.name = name
        self.value_type = value_type
        self.cardinal = cardinal
        self.used_collective = used_collective

    def __repr__(self):
        return f"{self.name}({self.value_type}{':coll' if self.used_collective else ''})"

    def copy_with_changes(self, value_type=None, cardinal=None, used_collective=None):
        return VariableData(self.name,
                            value_type=value_type if value_type is not None else self.value_type,
                            cardinal=cardinal if cardinal is not None else self.cardinal,
                            used_collective=used_collective if used_collective is not None else self.used_collective)


# Use None in variable_data to represent a value
# That is not bound to an actual variable
class VariableBinding(object):
    def __init__(self, variable_data, value):
        self.value = value
        self.variable = variable_data

    def __repr__(self):
        return f"{self.variable}={self.value}"


