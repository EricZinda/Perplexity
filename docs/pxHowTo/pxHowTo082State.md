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

## Containment
One of the main concepts in a file system is "containment" - folders contain files, files contain text, etc. We'll want to model this in a general way so that words like "in" or "contains" can work across objects. We'll do this by creating a `Container` base class that derives from the `UniqueObject` base class:

~~~
class Container(UniqueObject):
    def __init__(self):
        super().__init__()

    def contained_items(self):
        if False:
            yield None
~~~

Note that `contained_items()` has to include an `if` statement that will never work to force Python to make it act like a generator, even though it is never going to return anything by default. This is just a quirk of Python.

## Files and Folders

~~~
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
~~~