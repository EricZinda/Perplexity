# Variables in solutions will have these properties set on the binding:
# - cardinal_solution_id: for a given cardinal, all solutions that are in a given coll or dist set have the same cardinal_solution_id
# - cardinal_item_id: the index of this element of the *cardinal_solution_id* or None if there is no set
# - cardinal_id: the "set" the answer is a part of or None if there is no set
# - is_collective: True if this variable is acting in collective mode
# - used_collective: True if the processing of the variable acts differently for collective and distributive modes
#                       Note that this only needs to be set on answers that actually processed the collective mode as a unit
class VariableData(object):
    def __init__(self, name, cardinal_solution_id=None, cardinal_id=None, cardinal_item_id=None, is_collective=False, used_collective=False):
        self.name = name
        self.cardinal_solution_id = cardinal_solution_id
        self.cardinal_id = cardinal_id
        self.cardinal_item_id = cardinal_item_id
        self.is_collective = is_collective
        self.used_collective = used_collective

    def __repr__(self):
        if self.cardinal_id is not None:
            return f"{self.name}#{self.cardinal_solution_id}({self.cardinal_id}->{self.cardinal_item_id})[{'coll' if self.is_collective else 'dist'}]"

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


