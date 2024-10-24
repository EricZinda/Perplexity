import logging
import samples.file_system_example.objects
from perplexity.state import State
import pickle


def load_file_system_state(file):
    file_system = pickle.load(file)
    current_user = pickle.load(file)
    actors = pickle.load(file)
    return FileSystemState(file_system,current_user, actors)


# The state representation used by the file system example
# note that the core system doesn't care at all what this object
# looks like. It is only the predications that interact with it
class FileSystemState(State):
    def __init__(self, file_system, current_user=None, actors=None):
        super().__init__([])
        self.file_system = file_system
        self.current_user = samples.file_system_example.objects.Actor(name="User", person=1, file_system=file_system) if current_user is None else current_user
        self.actors = [self.current_user,
                       samples.file_system_example.objects.Actor(name="Computer", person=2, file_system=file_system)] if actors is None else actors
        self.commands = [samples.file_system_example.objects.FileCommand("copy"), samples.file_system_example.objects.FileCommand("go")]

    def save(self, file):
        pickle.dump(self.file_system, file, 5)
        pickle.dump(self.current_user, file, 5)
        pickle.dump(self.actors, file, 5)

    def all_individuals(self):
        yield from self.file_system.all_individuals()
        yield from self.actors
        yield from self.commands

    def user(self):
        return self.current_user


class CreateOperation(object):
    def __init__(self, binding_to_create, file_name):
        self.binding_to_create = binding_to_create
        self.file_name = file_name

    def apply_to(self, state):
        state.file_system.create_item(self.binding_to_create, self.file_name)


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
