## 
We are getting to the point where the examples need to get richer and the approach we've used so far of just hard-coding the state of the world or using the base `State` object is not going to be good enough for future examples. We need to step back and think about how to model the file system state in a more robust way.

## The Perplexity State object

The default `State` object only has a very small amount of code for manipulating *application* state, the rest of its implementation manipulates MRS variables. We used that code in the [Action Verbs topic][pxHowTo070ActionVerbs) Here it is again:

~~~
class State(object):
    def __init__(self, objects):

        ...

        self.objects = objects

    ...
    
    def all_individuals(self):
        for item in self.objects:
            yield item

    ...
~~~

The only reason it even has this basic implementation is because the system implementation of `thing(x)` needs to return all "things in the world" if it is called with an unbound `x`. So, outside of that, we are free to implement our system state in any way we like *as long as it remains immutable*. Any methods we implement that make changes must follow the pattern that `set_x()` and `add_to_e()` followed and return a copy of itself with the change instead of modifying the object directly. This is key for making the [solver backtracking algorithm](../devcon/devcon0010MRSSolver) work.

So, we'll need to add a notion of files and folders to `State`, and provide some ways of querying the system about them. We'll do that next.

## Identity
Because the system is built around immutable state, we will sometimes end up with two state objects and need to be able to find the same object in either one. We need a way to compare objects *across* state object. The easiest way to do this is by having all the objects in the system have a globally unique id that can be easily compared. We'll create a base class, `UniqueObject` that does this and derive everything from it:

~~~
class UniqueObject(object):
    def __init__(self):
        self.unique_id = uuid.uuid4()
~~~

## Containment and Location
One of the main concepts in a file system is "containment" - folders contain files, files contain text, etc. We'll want to model this in a general way so that words like "in" or "contains" can work across objects. We'll do this by having two methods that objects can implement:

~~~
# Implement by yielding all objects that this object contains
def contained_items(self, variable_data):
    ...

# Implement by yielding all the places that this object "is" 
def all_locations(self, variable_data):
    ...
~~~


## Files and Folders
Because users may talk about files or folders that don't exist yet, or that may need to be created, we need the `File` and `Folder` object to be able to represent files and folders that don't actually exist. So, these objects will have a small amount of information in them and call to a `FileSystem` object for the rest. We'll implement that object next. 

Note that the `File` object has a simplistic notion of a "linked file" (as in Unix) so that we can show the system answering questions about things that are in more than one place.

It is very important that these objects implement `__hash__` since that allows them to be in sets and dictionaries which are required by Perplexity. `__repr__` is just a method that makes debugging nicer. Checking if things are equal is also required by Perplexity, which is why `__eq__` is implemented.

~~~
class File(UniqueObject):
    def __init__(self, name, size=None, file_system=None, link=None):
        super().__init__()
        self.name = name
        self.size = size
        self.file_system = file_system
        self.link = link
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

    def all_locations(self, variable_data):
        if self.exists():
            folder = self.file_system.item_from_path(str(pathlib.PurePath(self.name).parent), is_file=False)
            yield folder
            yield from folder.all_locations(variable_data)

        else:
            raise MessageException("notFound", [variable_data.name])

    def contained_items(self, variable_data):
        yield from self.file_system.contained_items(self, variable_data)

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
~~~