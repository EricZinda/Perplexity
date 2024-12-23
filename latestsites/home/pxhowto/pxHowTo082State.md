{% raw %}## Building a Custom State Object
We are getting to the point where the examples need to get richer and hard-coding the state of the world or using the base `State` object is not going to be good enough. We need to step back and think about how to model the file system state in a more robust way.  Even if you aren't building an interface to a file system, many of the concerns and solutions described below could be useful to you.  Designing how your state object works is a key design decision when building a Perplexity application.

## The Perplexity State object

The default `State` object only has a small amount of code for manipulating *application* state, the rest of its implementation manipulates MRS variables. It is literally just one method: `all_individuals()` and we used it in the [Action Verbs topic](https://blog.inductorsoftware.com/Perplexity/home/pxhowto/pxHowTo070ActionVerbs). Here it is again:

```
class State(object):
    def __init__(self, objects):

        ...

        self.objects = objects

    ...
    
    def all_individuals(self):
        for item in self.objects:
            yield item

    ...
```

The only reason it even has this basic implementation is because the system implementation of `in_scope` needs it to determine which objects are ["proximate"](https://en.wikipedia.org/wiki/Obviative) to the user. So, outside of that, we are free to implement our system state in any way we like *as long as it remains immutable*. Any methods we implement that make changes must follow the pattern used by `set_x()` and `add_to_e()` and return a copy with the change instead of modifying the object directly. This is key for making the [solver backtracking algorithm](https://blog.inductorsoftware.com/Perplexity/home/devcon/devcon0010MRSSolver) work.

So, we'll need to add a notion of files and folders to `State`, and provide some ways to query the system about them. But all of this will *only* be used by the code we write to implement our custom predications.  Perplexity will completely ignore it.

## Identity
Because the system is built around immutable state, we will sometimes end up with two `State` objects and need to be able to find the same object contained in either one. We need a way to compare objects *across* state objects. The easiest way is to give all the objects in the system a globally unique id that can be easily compared. We'll create a base class, `UniqueObject` that does this and derive everything from it:

```
class UniqueObject(object):
    def __init__(self):
        self.unique_id = uuid.uuid4()
```

## Containment and Location
One of the main concepts in a file system is "containment" - folders contain files, files contain text, etc. We'll want to model this in a general way so that words like "in" or "contains" can work across objects. We'll do this by having two methods that objects can implement:

```
# Implement by yielding all objects that this object contains
def contained_items(self, variable_data):
    ...

# Implement by yielding all the places that this object "is" 
def all_locations(self, variable_data):
    ...
```

## Files and Folders
Because users may talk about files or folders that don't exist yet, or that may need to be created, we need the `File` and `Folder` object to be able to represent files and folders that don't actually exist. So, these objects will have a small amount of information in them and call to a `FileSystem` object for the rest (we'll implement that object in the next section). 

It is very important that these objects implement `__hash__` since that allows them to be in sets and dictionaries which are required by Perplexity. `__repr__` is just a method that makes debugging nicer. Checking if things are equal is also required by Perplexity, which is why `__eq__` is implemented. As described above, `contained_items` and `all_locations` are implemented in both to support predications that involve containment. The rest of the methods are helpers.

[Note that the `File` object also has a simplistic notion of a "linked file" (as in Unix) so that we can show the system answering questions about things that are in more than one place.]

```
class File(UniqueObject):
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


class Folder(UniqueObject):
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

    def exists(self):
        return self.file_system.exists(self.name, is_file=False)
```

## FileSystem
We'll be using a fake `FileSystem` object for the examples so that we can inject the files and folders that we want to test, but the class is built to allow it to be implemented on top of a real file system as well. There are a lot of implementation details in this class that aren't important for understanding how the system works -- you can see the full implementation [here](https://github.com/EricZinda/Perplexity/blob/18a75c346c4d12385768cf0daa57380cf187fc4c/samples/file_system_example/objects.py#L248). For our purposes, the important parts are the constructor and the implementation of `all_individuals()`:

```
# Allows mocking up a file system for testing
class FileSystemMock(State):
    # current = the user's current directory as a string
    #
    # file_list must be in the form:
    # [(True, "/dir1/dir2/filename.txt", {"size": 1000} # Set to True for a file
    #  (False, "/dir3/dir4" # Set to False for a directory
    # ]
    # Adds the entire path of each directory as individual directories
    # in the file system
    def __init__(self, file_list, current):

        ...


    def all_individuals(self):

        ...
```

The constructor allows us to create a mock file system with whatever files and folders we want, as well as setting a "current" directory.  It is used like this:

```
FileSystemMock([(True, "/documents/file1.txt", {"size": 1000}),
                (False, "/Desktop", {"size": 10000000}),
                (True, "/Desktop/file2.txt", {"size": 10000000}),
                (True, "/Desktop/file3.txt", {"size": 1000})],
                "/Desktop"))
```

It takes a list of tuples that describe files and folders. The first element of the tuple is `True` if the item is a file, `False` if folder. Sizes can be provided for each.  The last argument is the folder that is the "current" directory.

## Actor
We will encounter phrases that have an explicit person like "where am I?" as well as an implied person like "delete a file" (i.e. "[you] delete a file"). Either case generates predications that need "actors" to be modelled in the system:

```
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

    def __repr__(self):
        return f"Actor(name={self.name}, person={self.person})"

    def all_locations(self, variable_data):
        if self.person == 1:
            # Return the locations for the user "me"
            yield self.current_directory()
            yield from self.current_directory().all_locations(variable_data)

    def current_directory(self):
        return self.file_system.current_directory()
```

An `Actor` has a `person` property that indicates what pronoun role it plays: 1 means "first person pronoun" like "I" or "me", 2 means second person pronoun, which is always "the computer" in this system, etc. It also has a `FileSystem` member so it can find its "current directory". Finally, it has the `all_locations()` method so we can find out where the `Actor` is.

## FileSystemState
The last step is to create a new `State` object that uses the `FileSystem` object that we'll actually use in the samples. We need to derive this from the Perplexity `State` object so that it can be used in the system, and we need to implement the `State.all_individuals()` method so that `in_scope` will work. Note that all individuals needs to return both actors and file system objects since they are all the objects in the system.

Note that there is also a `save()` method that uses [Python "pickling"](https://docs.python.org/3/library/pickle.html) to save the state of the world, which is a simple way of saving a simple set of objects like these.

```
# The state representation used by the file system example
# note that the core system doesn't care at all what this object
# looks like. It is only the predications that interact with it
class FileSystemState(State):
    def __init__(self, file_system, current_user=None, actors=None):
        super().__init__([])
        self.file_system = file_system
        self.current_user = file_system_example.objects.Actor(name="User", person=1, file_system=file_system) if current_user is None else current_user
        self.actors = [self.current_user,
                       file_system_example.objects.Actor(name="Computer", person=2, file_system=file_system)] if actors is None else actors

    def save(self, file):
        pickle.dump(self.file_system, file, 5)
        pickle.dump(self.current_user, file, 5)
        pickle.dump(self.actors, file, 5)

    def all_individuals(self):
        yield from self.file_system.all_individuals()
        yield from self.actors

    def user(self):
        return self.current_user
```

The base `State` class will handle doing copies of the object when `set_x` or `add_to_e` are called. We don't need to do anything special to handle the object being copied because the objects have all been carefully built to support the Python `copy.deepcopy()` method. They also all derive from `UniqueObject` so they can be compared across objects. 

## Using FileSystemState
To use the object, we modify the `hello_world.py` `reset()` function to return the new `FileSystemState` object instead of the default `State` object, like this:

```
... 

vocabulary = Vocabulary()


def reset():
    # return State([])

    return FileSystemState(FileSystemMock([(True, "/documents/file1.txt", {"size": 1000}),
                                           (False, "/Desktop", {"size": 10000000}),
                                           (True, "/Desktop/file2.txt", {"size": 10000000}),
                                           (True, "/Desktop/file3.txt", {"size": 1000})],
                                           "/Desktop"))

```

That change will ensure that our `FileSystemState` object is used by the solver in every call to one of our predications. That, and modifying the predications to start using the new state, is all that is needed.

# Example
Only the `_file_n_of`, `_folder_n_of`, `_large_a_1`, `delete_v_1_comm` and `pron` predications need to be updated to use the new objects.  The `DeleteOperation` class needs to be updated as well. These are all relatively minor changes, and the final functions are listed below:

```
@Predication(vocabulary, names=["_file_n_of"])
def file_n_of(context, state, x_binding, i_binding):
    def bound_variable(value):
        if isinstance(value, File):
            return True
        else:
            context.report_error(["valueIsNotX", value, x_binding.variable.name])
            return False

    def unbound_variable():
        for item in state.all_individuals():
            if bound_variable(item):
                yield item

    yield from combinatorial_predication_1(context,
                                           state,
                                           x_binding,
                                           bound_variable,
                                           unbound_variable)


# true for both sets and individuals as long as everything
# in the set is a file
@Predication(vocabulary, names=["_folder_n_of"])
def folder_n_of(context, state, x_binding, i_binding):
    def bound_variable(value):
        if isinstance(value, Folder):
            return True
        else:
            context.report_error(["valueIsNotX", value, x_binding.variable.name])
            return False

    def unbound_variable():
        for item in state.all_individuals():
            if bound_variable(item):
                yield item

    yield from combinatorial_predication_1(context,
                                           state,
                                           x_binding,
                                           bound_variable,
                                           unbound_variable)


@Predication(vocabulary,
             names=["_large_a_1"],
             handles=[("DegreeMultiplier", EventOption.optional)])
def large_a_1(context, state, e_introduced_binding, x_target_binding):
    # See if any modifiers have changed *how* large we should be
    degree_multiplier = degree_multiplier_from_event(context, state, e_introduced_binding)

    # "large" is being used "predicatively" as in "the dogs are large". This needs to force
    # the individuals to be separate (i.e. not part of a group)
    def criteria_bound(value):
        if hasattr(value, 'size') and value.size > degree_multiplier * 1000000:
            return True

        else:
            context.report_error(["adjectiveDoesntApply", "large", x_target_binding.variable.name])
            return False

    def unbound_values():
        # Find all large things
        for value in state.all_individuals():
            if hasattr(value, 'size') and value.size > degree_multiplier * 1000000:
                yield value

    yield from combinatorial_predication_1(context,
                                           state,
                                           x_target_binding,
                                           criteria_bound,
                                           unbound_values)


# Delete only works on individual values: i.e. there is no semantic for deleting
# things "together" which would probably imply a transaction or something
@Predication(vocabulary, names=["_delete_v_1"])
def delete_v_1_comm(context, state, e_introduced_binding, x_actor_binding, x_what_binding):
    # We only know how to delete things from the
    # computer's perspective
    if x_actor_binding.value[0].name == "Computer":
        def criteria(value):
            # Only allow deleting files and folders that exist
            if isinstance(value, (File, Folder)) and value.exists():
                return True

            else:
                context.report_error(["cantDo", "delete", x_what_binding.variable.name])

        def unbound_what():
            context.report_error(["cantDo", "delete", x_what_binding.variable.name])

        for new_state in individual_style_predication_1(context,
                                                        state,
                                                        x_what_binding,
                                                        criteria,
                                                        unbound_what,
                                                        ["cantDeleteSet", x_what_binding.variable.name]):
            yield new_state.record_operations([DeleteOperation(new_state.get_binding(x_what_binding.variable.name))])

    else:
        context.report_error(["dontKnowActor", x_actor_binding.variable.name])


# Delete any object in the system
class DeleteOperation(object):
    def __init__(self, binding_to_delete):
        self.binding_to_delete = binding_to_delete

    def apply_to(self, state):
        state.file_system.delete_item(self.binding_to_delete)


@Predication(vocabulary, names=["pron"])
def pron(context, state, x_who_binding):
    person = int(state.get_binding("tree").value[0]["Variables"][x_who_binding.variable.name]["PERS"])

    def bound_variable(value):
        return isinstance(value, Actor) and value.person == person

    def unbound_variable():
        for item in state.all_individuals():
            if bound_variable(item):
                yield item

    yield from combinatorial_predication_1(context, state, x_who_binding, bound_variable, unbound_variable)
```

With those changes, all the examples from before still work the same but now use the new objects:

```
python ./hello_world.py
? a file is large
Yes, that is true.

? which file is large?
(File(name=/documents/file2.txt, size=10000000),)

? what file is very large?
a file is not large

? a file is very large
a file is not large

? delete a large file
Done!

? a file is large
a file is not large
```

> Comprehensive source for the completed tutorial is available [here](https://github.com/EricZinda/Perplexity/tree/main/samples/hello_world)

Last update: 2024-10-25 by Eric Zinda [[edit](https://github.com/EricZinda/Perplexity/edit/main/docs/pxHowTo/pxHowTo082State.md)]{% endraw %}