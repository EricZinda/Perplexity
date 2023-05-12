import copy
import logging
import file_system_example.objects
from perplexity.state import State


# Optimized for the file system example
class FileSystemState(State):
    def __init__(self, file_system):
        super().__init__([])
        self.file_system = file_system
        self.current_user = file_system_example.objects.Actor(name="User", person=1, file_system=file_system)
        self.actors = [self.current_user,
                       file_system_example.objects.Actor(name="Computer", person=2, file_system=file_system)]

    def all_individuals(self):
        yield from self.file_system.all_individuals()
        yield from self.actors

    def user(self):
        return self.current_user


# Delete any object in the system
class DeleteOperation(object):
    def __init__(self, binding_to_delete):
        self.binding_to_delete = binding_to_delete

    def apply_to(self, state):
        if isinstance(state, FileSystemState):
            state.file_system.delete_item(self.binding_to_delete)

        else:
            for index in range(0, len(state.objects)):
                # Use the `unique_id` property to compare objects since they
                # may have come from different `State` objects and will thus be copies
                if state.objects[index].unique_id == self.binding_to_delete.unique_id:
                    state.objects.pop(index)
                    break


class CopyOperation(object):
    def __init__(self, from_directory_binding, binding_from_copy, binding_to_copy):
        self.from_directory_binding = from_directory_binding
        self.binding_from_copy = binding_from_copy
        self.binding_to_copy = binding_to_copy

    def apply_to(self, state):
        if isinstance(state, FileSystemState):
            state.file_system.copy_item(self.from_directory_binding, self.binding_from_copy, self.binding_to_copy)


class ChangeDirectoryOperation(object):
    def __init__(self, folder_binding):
        self.folder_binding = folder_binding

    def apply_to(self, state):
        state.file_system.change_directory(self.folder_binding)


pipeline_logger = logging.getLogger('Pipeline')
