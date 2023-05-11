import copy
import logging
import os
import pathlib
import uuid

from perplexity.set_utilities import Measurement
from perplexity.variable_binding import VariableBinding


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


class Megabyte(object):
    def __init__(self):
        self.units = "mb"
        self._hash = hash(self.units)

    def __hash__(self):
        return self._hash

    def __repr__(self):
        return self.units

    def __eq__(self, other):
        return hasattr(other, "measurement_type") and self.measurement_type() == other.measurement_type()

    def measurement_type(self):
        return self.units


# Derive from UniqueObject and call
# its __init__ method from this __init__
# method so we get the unique ID created
class Folder(Container):
    def __init__(self, name, size=0, file_system=None):
        super().__init__()
        self.name = name
        self.size = size
        self.file_system = file_system
        self._hash = hash(self.name)

    def __hash__(self):
        return self._hash

    def __repr__(self):
        return f"Folder(name={self.name}, size={self.size})"

    def __eq__(self, obj):
        return isinstance(obj, Folder) and str(self.name) == str(obj.name)

    def __ne__(self, obj):
        return not self == obj

    def contained_items(self, variable_data):
        yield from self.file_system.contained_items(self, variable_data)

    def all_locations(self, variable_data):
        if self.exists():
            path = pathlib.PurePath(self.name)
            for parent_path in path.parents:
                yield self.file_system.item_from_path(parent_path, is_file=False)

        else:
            raise MessageException("notFound", [variable_data.name])

    def can_interpret_as(self, value):
        return pathlib.PurePath(self.name).match(value)

    def containers(self, variable_data):
        yield from self.all_locations(variable_data)

    def exists(self):
        return self.file_system.exists(self.name, is_file=False)


class File(Container):
    def __init__(self, name, size=None, file_system=None, link=None):
        super().__init__()
        self.name = name
        self.size = size
        self.file_system = file_system
        self.link = link

        # If we assume link objects always have the same name, then if we only hash the name
        # link objects will have the same hash, but so will anything else with that name (which is OK)
        # Any other files in the system with the same name (including raw file specifiers) will
        # hash to the same value too.
        # This means that there could be collisions if there are lots of files with the same name
        # but it is unclear how else to do this
        self._hash = hash(self.file_name())

    def __repr__(self):
        return f"File(name={self.name}, size={self.size})"

    # The only required property is that objects which compare equal have the same hash value
    # But: objects with the same hash aren't required to be equal
    # It must remain the same for the lifetime of the object
    def __hash__(self):
        return self._hash

    def __eq__(self, obj):
        if isinstance(obj, File) and self._hash == obj._hash:
            if self.has_path() and obj.has_path():
                # If they both have a path, then the entire path must be ==
                # to make them ==
                # Unless there is a symbolic link, in which case the links must match
                self_name = self.name if self.link is None else self.link
                obj_name = obj.name if obj.link is None else obj.link
                return self_name == obj_name

            else:
                # If one or both of them doesn't have a path specified then it is a pure filename
                # which means it == the other object if the file name alone matches
                return self.file_name() == obj.file_name()

    def __ne__(self, obj):
        return not self == obj

    def all_locations(self, variable_data):
        if self.exists():
            folder = self.file_system.item_from_path(str(pathlib.PurePath(self.name).parent), is_file=False)
            yield folder
            yield from folder.all_locations(variable_data)

        else:
            raise MessageException("notFound", [variable_data.name])

    def contained_items(self, variable_data):
        yield from self.file_system.contained_items(self, variable_data)

    def containers(self, variable_data):
        yield from self.all_locations(variable_data)

    def exists(self):
        return self.file_system.exists(self.name, is_file=True)

    # False if there is no path specified at all
    # including "./". Indicates the object is a raw
    # file specifier
    def has_path(self):
        return os.path.dirname(self.name) != ""

    def file_name(self):
        return pathlib.PurePath(self.name).parts[-1]

    def can_interpret_as(self, value):
        return pathlib.PurePath(self.name).match(value)

    def size_measurement(self):
        return Measurement(Megabyte(), self.size/1000000)


# Represents something that can "do" things, like a computer
# or a human (or a dog, etc)
class Actor(UniqueObject):
    def __init__(self, name, person, file_system=None):
        super().__init__()
        self.name = name
        self.person = person
        self.file_system = file_system
        self._hash = hash((self.name, self.person))

    def __hash__(self):
        return self._hash

    def __eq__(self, other):
        if isinstance(other, Actor):
            return self._hash == other._hash

    def __ne__(self, other):
        return not self == other

    def __repr__(self):
        return f"Actor(name={self.name}, person={self.person})"

    def all_locations(self, variable_data):
        if self.person == 1:
            # Return the locations for the user "me"
            yield self.current_directory()
            yield from self.current_directory().all_locations(variable_data)

    def containers(self, variable_data):
        yield from self.all_locations(variable_data)

    def current_directory(self):
        return self.file_system.current_directory()


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
            for new_path in [root_path] + [str(x) for x in pathlib.PurePath(root_path).parents]:
                if new_path not in self.items:
                    self.items[new_path] = Folder(new_path, file_system=self)

            self._check_links()

        self.current = self.item_from_path(current, is_file=False)

    # Everything with the same link property must have the same file name
    # or else File.hash won't work
    def _check_links(self):
        links = {}
        for item in self.items.items():
            if hasattr(item[1], "link") and item[1].link is not None:
                if item[1].link in links:
                    assert item[1].file_name() == links[item[1].link].file_name()
                    continue
                else:
                    links[item[1].link] = item[1]

    def set_properties(self, obj, props):
        for prop in props.items():
            if hasattr(obj, prop[0]):
                setattr(obj, prop[0], prop[1])

    def current_directory(self):
        return self.current

    def contained_items(self, container, variable_data):
        path = self.add_current_directory(container.name)
        is_file = isinstance(container, File)
        if self.exists(path, is_file=is_file):
            for item in self.items.items():
                item_path = str(pathlib.PurePath(item[0]).parent)
                # item_path == item[0] when it is the root ("/")
                # don't say the root is in itself
                if item_path != item[0] and item_path == path:
                    yield item[1]

        else:
            raise MessageException("notFound", [variable_data.name])

    # Will create a File object for a nonexistent path
    def item_from_path(self, path, is_file=True):
        path = self.add_current_directory(path)

        if path in self.items:
            found_item = self.items[path]
            if isinstance(found_item, File) and is_file or isinstance(found_item, Folder) and not is_file:
                return found_item

        # Mock up an object for the nonexistent path
        if is_file:
            return File(path, file_system=self)
        else:
            return Folder(path, file_system=self)

    def add_current_directory(self, path):
        if os.path.dirname(path) == "":
            return str(pathlib.PurePath(self.current_directory().name, path))
        else:
            return path

    def all_individuals_interpreted_as(self, name):
        for item in self.all_individuals():
            if hasattr(item, "can_interpret_as") and item.can_interpret_as(name):
                yield item

    def all_individuals(self):
        links = {}
        for item in self.items.items():
            if hasattr(item[1], "link") and item[1].link is not None:
                if item[1].link in links:
                    continue
                else:
                    links[item[1].link] = item[0]

            yield item[1]

    def exists(self, path, is_file):
        path = self.add_current_directory(path)
        return path != "" and path in self.items and isinstance(self.items[path], File if is_file else Folder)

    def delete_item(self, delete_binding):
        path = self.add_current_directory(delete_binding.value[0].name)
        if self.exists(path, is_file=isinstance(delete_binding.value[0], File)):
            self.items.pop(path)

        else:
            raise MessageException("notFound", [delete_binding.variable.name])

    def copy_item(self, from_directory_binding, from_binding, to_binding):
        if from_directory_binding is not None:
            # PurePath will only attach the from_directory_binding.value.name to the front if
            # if from_binding.value is relative, otherwise it is ignored
            from_path = str(pathlib.PurePath(from_directory_binding.value.name, from_binding.value.name))
        else:
            from_path = from_binding.value.name

        if self.exists(from_path, is_file=isinstance(from_binding.value, File)):
            if to_binding is None:
                to_binding = VariableBinding(None, self.current_directory())

            if self.exists(to_binding.value.name, is_file=isinstance(to_binding.value, File)):
                item_name = pathlib.PurePath(from_binding.value.name).parts[-1]
                if isinstance(to_binding.value, Folder):
                    # "to" is a folder, use it as the new base for the file name
                    new_item_path = pathlib.PurePath(to_binding.value.name, item_name)

                else:
                    # "to" includes a file name, use the entire name as the name of the target
                    new_item_path = to_binding.value.name

                new_item = copy.deepcopy(self.item_from_path(from_path, is_file=isinstance(from_binding.value, File)))
                new_item.name = new_item_path
                self.items[str(new_item_path)] = new_item

            else:
                raise MessageException("notFound", [to_binding.variable.name])

        else:
            raise MessageException("notFound", [from_binding.variable.name])

    def change_directory(self, folder_binding):
        path = self.add_current_directory(folder_binding.value[0].name)
        if self.exists(path, is_file=False):
            self.current = self.item_from_path(path, is_file=False)

        else:
            raise MessageException("notFound", [folder_binding.variable.name])


class QuotedText(object):
    def __init__(self, name):
        self.name = name.replace("\\\\>root111", "/").replace("\\\\>", "/")

    def __repr__(self):
        return f"{self.name}"

    def all_interpretations(self, state):
        # Yield the text converted to a file or folder if possible
        # If one of them exists, return it first so that its errors
        # get priority
        yield from state.file_system.all_individuals_interpreted_as(self.name)

        # Always yield the text value last since the others
        # are probably what was meant and the first error
        # hit will be what is returned
        yield self


pipeline_logger = logging.getLogger('Pipeline')

# Added to end of file to resolve circular dependency
from file_system_example.state import FileSystemState