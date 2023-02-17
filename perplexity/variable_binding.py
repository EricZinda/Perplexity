class VariableData(object):
    def __init__(self, name, cardinal_id=None, cardinal_item_id=None, is_collective=False):
        self.name = name
        self.cardinal_id = cardinal_id
        self.cardinal_item_id = cardinal_item_id
        self.is_collective = is_collective

    def __repr__(self):
        if self.cardinal_id is not None:
            return f"{self.name}({self.cardinal_id}->{self.cardinal_item_id})[{'coll' if self.is_collective else 'dist'}]"

        else:
            return f"{self.name}"


# Use None in variable_data to represent a value
# That is not bound to an actual variable
class VariableBinding(object):
    def __init__(self, variable_data, value):
        self.value = value
        self.variable = variable_data

    def __repr__(self):
        return f"{self.variable}={self.value}"


