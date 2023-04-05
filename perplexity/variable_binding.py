import enum


class VariableValueType(enum.Enum):
    none = 0
    combinatoric = 1
    set = 2


class VariableData(object):
    # These are the defaults if a variable has never been set
    def __init__(self, name, value_type=VariableValueType.none, determiner=None, used_collective=False):
        self.name = name
        self.value_type = value_type
        self.determiner = determiner
        self.used_collective = used_collective

    def __repr__(self):
        return f"{self.name}({self.value_type}{':coll' if self.used_collective else ''})"

    def copy_with_changes(self, value_type=None, determiner=None, used_collective=None):
        return VariableData(self.name,
                            value_type=value_type if value_type is not None else self.value_type,
                            determiner=determiner if determiner is not None else self.determiner,
                            used_collective=used_collective if used_collective is not None else self.used_collective)


# Use None in variable_data to represent a value
# That is not bound to an actual variable
class VariableBinding(object):
    def __init__(self, variable_data, value):
        self.value = value
        self.variable = variable_data

    def __repr__(self):
        return f"{self.variable}={self.value}"


