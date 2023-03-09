# Variables in solutions will have these properties set on the binding:
# variable_set_id: a group of values that are treated as a whole, like a set-based variable. The group has a unique variable_set_id
# variable_set_item_id: one element of a variable set
# cardinal_group_id: A cardinal has a group of variable sets that it deals with called a cardinal group. For coll, it is a list of one set of N, for dist it is a list of N sets of 1
#                    it is a group of pairs of variable_set_id/[list of values]
# is_collective: True if this variable is acting in collective mode
# used_collective: True if the processing of the variable acts differently for collective and distributive modes
#                       Note that this only needs to be set on answers that actually processed the collective mode as a unit
# variable_set_items: the entire set of variable set items.  Used for verbs like "lift" that operate on the whole set
class VariableData(object):
    def __init__(self, name, cardinal_group_id=None, variable_set_id=None, variable_set_item_id=None, is_collective=False, used_collective=False, variable_set_items=None):
        self.name = name
        self.cardinal_group_id = cardinal_group_id
        self.variable_set_id = variable_set_id
        self.variable_set_item_id = variable_set_item_id
        self.is_collective = is_collective
        self.used_collective = used_collective
        self.variable_set_items = variable_set_items

    def __repr__(self):
        if self.variable_set_id is not None:
            used_collective_str = "+" if self.used_collective else ""
            return f"{self.name}#{self.cardinal_group_id}({self.variable_set_id}->{self.variable_set_item_id})[{'coll' + used_collective_str if self.is_collective else 'dist'}]"

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


