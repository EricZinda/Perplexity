import copy
import logging
import file_system_example.objects
from perplexity.state import State


# The state representation used by the file system example
# note that the core system doesn't care at all what this object
# looks like. It is only the predications that interact with it
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
        state.file_system.delete_item(self.binding_to_delete)


class CopyOperation(object):
    def __init__(self, from_directory_binding, binding_from_copy, binding_to_copy):
        self.from_directory_binding = from_directory_binding
        self.binding_from_copy = binding_from_copy
        self.binding_to_copy = binding_to_copy

    def apply_to(self, state):
        state.file_system.copy_item(self.from_directory_binding, self.binding_from_copy, self.binding_to_copy)


class ChangeDirectoryOperation(object):
    def __init__(self, folder_binding):
        self.folder_binding = folder_binding

    def apply_to(self, state):
        state.file_system.change_directory(self.folder_binding)


pipeline_logger = logging.getLogger('Pipeline')
