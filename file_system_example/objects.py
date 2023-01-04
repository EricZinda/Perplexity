import uuid


# Base class that objects derive from so that
# objects have a unique ID that is preserved even
# when they are copied
class UniqueObject(object):
    def __init__(self):
        self.unique_id = uuid.uuid4()


# Derive from UniqueObject and call
# its __init__ method from this __init__
# method so we get the unique ID created
class Folder(UniqueObject):
    def __init__(self, name, size=0):
        super().__init__()
        self.name = name
        self.size = size

    def __repr__(self):
        return f"Folder(name={self.name}, size={self.size})"


class File(UniqueObject):
    def __init__(self, name, size=None):
        super().__init__()
        self.name = name
        self.size = size

    def __repr__(self):
        return f"File(name={self.name}, size={self.size})"


# Represents something that can "do" things, like a computer
# or a human (or a dog, etc)
class Actor(UniqueObject):
    def __init__(self, name, person):
        super().__init__()
        self.name = name
        self.person = person

    def __repr__(self):
        return f"Actor(name={self.name}, person={self.person})"


# Delete any object in the system
class DeleteOperation(object):
    def __init__(self, object_to_delete):
        self.object_to_delete = object_to_delete

    def apply_to(self, state):
        for index in range(0, len(state.objects)):
            # Use the `unique_id` property to compare objects since they
            # may have come from different `State` objects and will thus be copies
            if state.objects[index].unique_id == self.object_to_delete.unique_id:
                state.objects.pop(index)
                break
