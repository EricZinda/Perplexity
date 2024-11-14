class VariableData(object):
    # These are the defaults if a variable has never been set
    def __init__(self, name, combinatoric=False, determiner=None, quantifier=None, combined_variables=None):
        self.name = name
        assert combinatoric is False
        self.combinatoric = combinatoric
        self.determiner = determiner
        self.quantifier = quantifier
        self.combined_variables = combined_variables

    def __repr__(self):
        if self.combinatoric:
            return f"{self.name}(combinatoric)"
        else:
            return f"{self.name}"

    def copy_with_changes(self, combinatoric=None, determiner=None, quantifier=None, combined_variables=None):
        return VariableData(self.name,
                            combinatoric=combinatoric if combinatoric is not None else self.combinatoric,
                            determiner=determiner if determiner is not None else self.determiner,
                            quantifier=quantifier if quantifier is not None else self.quantifier,
                            combined_variables=combined_variables if combined_variables is not None else self.combined_variables)


# Use None in variable_data to represent a value
# That is not bound to an actual variable
class VariableBinding(object):
    def __init__(self, variable_data, value):
        self.value = value
        self.variable = variable_data

    def __repr__(self):
        return f"{self.variable}={self.value}"


