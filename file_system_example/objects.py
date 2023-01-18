import logging
import os
import pathlib
import uuid
from pathlib import Path


# Base class that objects derive from so that
# objects have a unique ID that is preserved even
# when they are copied
class UniqueObject(object):
    def __init__(self):
        self.unique_id = uuid.uuid4()


class Container(UniqueObject):
    def __init__(self):
        super().__init__()


# Derive from UniqueObject and call
# its __init__ method from this __init__
# method so we get the unique ID created
class Folder(Container):
    def __init__(self, name, size=0, contained_items=[]):
        super().__init__()
        self.name = name
        self.size = size
        self.contained_items = contained_items

    def __repr__(self):
        return f"Folder(name={self.name}, size={self.size})"

    def contains(self, item):
        return item in self.contained_items

    def all_locations(self):
        path = Path(self.name)
        for item in path.parents:
            yield Folder(item)

    def __eq__(self, obj):
        return isinstance(obj, Folder) and self.name == obj.name

    def __ne__(self, obj):
        return not self == obj


class File(Container):
    def __init__(self, name, size=None):
        super().__init__()
        self.name = name
        self.size = size

    def __repr__(self):
        return f"File(name={self.name}, size={self.size})"

    def all_locations(self):
        folder = Folder(pathlib.Path(self.name))
        yield folder
        yield from folder.all_locations()


# Represents something that can "do" things, like a computer
# or a human (or a dog, etc)
class Actor(UniqueObject):
    def __init__(self, name, person, file_system=None):
        super().__init__()
        self.name = name
        self.person = person
        self.file_system = file_system
        if file_system is not None:
            self.current_directory = self.file_system.current_directory()

    def __repr__(self):
        return f"Actor(name={self.name}, person={self.person})"

    def all_locations(self):
        if self.person == 1:
            # Return the locations for the user "me"
            yield self.current_directory
            yield from self.current_directory.all_locations()


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


class FileSystem(object):
    def __init__(self, file_list, current):
        pass

    # Return the current user directory
    def current_directory(self):
        pass

    # Return all directories and files
    # in the whole system
    def all_individuals(self):
        pass


# Allows mocking up a file system for testing
class FileSystemMock(FileSystem):

    # current = the user's current directory as a string
    #
    # file_list must be in the form:
    # [(True, "/dir1/dir2/filename.txt", {"size": 1000} # Set to True for a file
    #  (False, "/dir3/dir4" # Set to False for a directory
    # ]
    # Adds the entire path of each directory as individual directories
    # in the file system
    def __init__(self, file_list, current):
        self.current = current
        self.directories = {}
        self.files = {}

        for item in file_list:
            if item[0]:
                # This is a file
                new_file = File(name=item[1])
                self.set_properties(new_file, item[2])
                self.files[item[1]] = new_file
                root_path = os.path.dirname(item[1])

            else:
                # This is a directory
                root_path = item[1]
                new_folder = Folder(root_path)
                self.set_properties(new_folder, item[2])
                self.directories[root_path] = new_folder

            # Add all of the parent directories from the item
            # But only if they haven't been added yet so we don't
            # erase any properties that have been specifically set
            # on them
            for new_path in Path(root_path).parents:
                if new_path not in self.directories:
                    self.directories[new_path] = Folder(new_path)

    def set_properties(self, obj, props):
        for prop in props.items():
            if hasattr(obj, prop[0]):
                setattr(obj, prop[0], prop[1])

    def current_directory(self):
        return Folder(self.current)

    def all_individuals(self):
        for item in self.directories.items():
            yield Folder(name=item[0])

        for item in self.files.items():
            yield item[1]


pipeline_logger = logging.getLogger('Pipeline')
