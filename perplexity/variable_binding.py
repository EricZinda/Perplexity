class VariableData(object):
    # These are the defaults if a variable has never been set
    def __init__(self, name, combinatoric=False, determiner=None, quantifier=None):
        self.name = name
        self.combinatoric = combinatoric
        self.determiner = determiner
        self.quantifier = quantifier

    def __repr__(self):
        if self.combinatoric:
            return f"{self.name}(combinatoric)"
        else:
            return f"{self.name}"

    def copy_with_changes(self, combinatoric=None, determiner=None, quantifier=None):
        return VariableData(self.name,
                            combinatoric=combinatoric if combinatoric is not None else self.combinatoric,
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


