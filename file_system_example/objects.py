import logging
import os
import pathlib
import uuid
from pathlib import Path
from file_system_example.variable_binding import VariableBinding


# Base class that objects derive from so that
# objects have a unique ID that is preserved even
# when they are copied
from perplexity.execution import MessageException


class UniqueObject(object):
    def __init__(self):
        self.unique_id = uuid.uuid4()


class Container(UniqueObject):
    def __init__(self):
        super().__init__()

    def contained_items(self):
        if False:
            yield None


# Derive from UniqueObject and call
# its __init__ method from this __init__
# method so we get the unique ID created
class Folder(Container):
    def __init__(self, name, size=0, file_system=None):
        super().__init__()
        self.name = name
        self.size = size
        self.file_system = file_system

    def __repr__(self):
        return f"Folder(name={self.name}, size={self.size})"

    def __eq__(self, obj):
        return isinstance(obj, Folder) and self.name == obj.name

    def __ne__(self, obj):
        return not self == obj

    def contained_items(self, variable_data):
        yield from self.file_system.contained_items(VariableBinding(variable_data, self))

    def all_locations(self, variable_data):
        if self.file_system.exists(self.name):
            path = pathlib.PurePath(self.name)
            for parent_path in path.parents:
                yield self.file_system.item_from_path(parent_path)

        else:
            raise MessageException("notFound", [variable_data.name])

    def containers(self, variable_data):
        yield from self.all_locations(variable_data)


class File(Container):
    def __init__(self, name, size=None, file_system=None):
        super().__init__()
        self.name = name
        self.size = size
        self.file_system = file_system

    def __repr__(self):
        return f"File(name={self.name}, size={self.size})"

    def __eq__(self, obj):
        return isinstance(obj, File) and self.name == obj.name

    def __ne__(self, obj):
        return not self == obj

    def all_locations(self, variable_data):
        if self.file_system.exists(self.name):
            folder = self.file_system.item_from_path(str(pathlib.PurePath(self.name).parent))
            yield folder
            yield from folder.all_locations(variable_data)

        else:
            raise MessageException("notFound", [variable_data.name])

    def contained_items(self, variable_data):
        yield from self.file_system.contained_items(VariableBinding(variable_data, self))

    def containers(self, variable_data):
        yield from self.all_locations(variable_data)


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

    def all_locations(self, variable_data):
        if self.person == 1:
            # Return the locations for the user "me"
            yield self.current_directory
            yield from self.current_directory.all_locations(variable_data)

    def containers(self, variable_data):
        yield from self.all_locations(variable_data)


class FileSystem(object):
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
        self.items = {}

        for item in file_list:
            if item[0]:
                # This is a file
                new_file = File(name=item[1], file_system=self)
                self.set_properties(new_file, item[2])
                self.items[item[1]] = new_file
                root_path = os.path.dirname(item[1])

            else:
                # This is a directory
                root_path = item[1]
                new_folder = Folder(root_path, file_system=self)
                self.set_properties(new_folder, item[2])
                self.items[root_path] = new_folder

            # Add all of the parent directories from the item,
            # but only if they haven't been added yet so we don't
            # erase any properties that have been specifically set
            # on them
            for new_path in [root_path] + list(pathlib.PurePath(root_path).parents):
                if new_path not in self.items:
                    self.items[new_path] = Folder(new_path, file_system=self)

        self.current = self.item_from_path(current)

    def set_properties(self, obj, props):
        for prop in props.items():
            if hasattr(obj, prop[0]):
                setattr(obj, prop[0], prop[1])

    def current_directory(self):
        return self.current

    def contained_items(self, folder_binding):
        if folder_binding.value.name in self.items:
            for item in self.items.items():
                if str(pathlib.PurePath(item[0]).parent) == folder_binding.value.name:
                    yield item[1]

        else:
            raise MessageException("notFound", [folder_binding.variable.name])

    # Will create a File object for a nonexistent path
    def item_from_path(self, path):
        if os.path.dirname(path) == "":
            path = str(pathlib.PurePath(self.current_directory().name, path))

        if path in self.items:
            return self.items[path]

        else:
            # Mock up a file object for the nonexistent path
            return File(path, file_system=self)

    def all_individuals(self, variable_data):
        for item in self.items.items():
            yield VariableBinding(variable_data, item[1])

    def exists(self, path):
        return path != "" and path in self.items

    def delete_item(self, delete_binding):
        if self.exists(delete_binding.value.name):
            self.items.pop(delete_binding.value.name)

        else:
            raise MessageException("notFound", [delete_binding.variable.name])


class QuotedText(object):
    def __init__(self, name):
        self.name = name

    def all_interpretations(self, state):
        # The yield the text converted to a file if possible
        if isinstance(state, FileSystemState):
            file_system_object = state.file_system.item_from_path(self.name)
            if file_system_object is not None:
                yield file_system_object

            else:
                # Create a file that doesn't exist
                # For when a user is copying a file to
                # a new location, for example
                yield File(name=self.name)

        # Always yield the text value last since the others
        # are probably what was meant and the first error
        # hit will be what is returned
        yield self


pipeline_logger = logging.getLogger('Pipeline')

# Added to end of file to resolve circular dependency
from file_system_example.state import FileSystemState