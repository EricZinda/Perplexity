## `loc_nonsp(e,x_actor,x_location)` Overview
`loc_nonsp` ("nonspecific location") is true when `x_location` represents a "place" where `x_actor` "is" or "is at" but doesn't get more specific than that. It shows up in phrases like:

- "Where am I?" -> no relationship other than I "am" somewhere
- "Where is the stick?" -> no relationship other than the stick "is" somewhere
- "The dog barks every day" -> No relationship to day other than it "happens" every day

It *would not* show up in phrases that more specifically locate something, such as:

- The stick is on the table. -> locates the stick in a place on the location
- He arrives before/at 10am. -> locates the arrival before/at a certain time

More information is available in the [ERG reference](https://blog.inductorsoftware.com/docsproto/erg/ErgSemantics_ImplicitLocatives/).

In this topic, we'll implement the `loc_nonsp` and `place_n` predications to make the phrase "Where am I?" work:

~~~
[ "where am i"
  TOP: h0
  INDEX: e2 [ e SF: ques TENSE: pres MOOD: indicative PROG: - PERF: - ]
  RELS: < [ loc_nonsp<0:5> LBL: h1 ARG0: e2 ARG1: x3 [ x PERS: 1 NUM: sg IND: + PT: std ] ARG2: x4 [ x PERS: 3 NUM: sg ] ]
          [ place_n<0:5> LBL: h5 ARG0: x4 ]
          [ which_q<0:5> LBL: h6 ARG0: x4 RSTR: h7 BODY: h8 ]
          [ pron<9:10> LBL: h9 ARG0: x3 ]
          [ pronoun_q<9:10> LBL: h10 ARG0: x3 RSTR: h11 BODY: h12 ] >
  HCONS: < h0 qeq h1 h7 qeq h5 h11 qeq h9 > ]

               ┌────── pron(x3)
pronoun_q(x3,RSTR,BODY)             ┌────── place_n(x4)
                    └─ which_q(x4,RSTR,BODY)
                                         └─ loc_nonsp(e2,x3,x4)
~~~

### `place_n(x)`: Representing Places
As with "Where am I?", a predication that often appears with `loc_nonsp` is `place_n` when the location being referred to is inferred by the system to be a place.

What are the "places" in a file system? They are all the objects where something else can be located, some obvious ones:
- `file`: text can be located in a file, "where is the text 'summary of costs'?"
- `folder`: files can be in a folder, "where is the file foo.txt?"

For this particular system, a good proxy for "place" might be anything that something can be "in", aka a "container". We'll want easy ways to:

- Find all the containers
- Find all the containers that contain a particular thing

First we'll do it very simplistically, we can optimize later. We'll represent this in an object-oriented way by creating a container base class and deriving anything that can be a "place" from that class. Then we can check to see if an object is a "place" by seeing if it derives from `Container`:

~~~
class Container(UniqueObject):
    def __init__(self):
        super().__init__()
        
class Folder(Container):
    ...

class File(Container):
    ...
    
@Predication(vocabulary)
def place_n(state, x):
    x_value = state.get_variable(x)

    if x_value is None:
        iterator = state.all_individuals()
    else:
        iterator = [x_value]

    for item in iterator:
        # Any object is a "place" as long as it can
        # contain things
        if isinstance(item, Container):
            yield state.set_x(x, item)
~~~

### `loc_nonsp(e,x,x)`: Representing Generic Location
As described above, `loc_nonsp(e,x_actor,x_location)` is true when `x_location` represents a "place" where `x_actor` "is" or "is at" but doesn't get more specific than that. Basically, it is the "generic location" of `x_actor`. This means we'll need to have the objects in the system able to return their "location". Note that a given file or folder has many "locations":

- It is located in a folder
- It is also located in the parent folder
- It is also located in the parent of the parent folder
- etc.

We'll need objects to return *all* of these locations to truly implement this predication. If we implement a function called `all_locations()` in the `Folder` object, we can then use it from the other objects:
~~~
class Folder(Container):
    
    ...
    
    def all_locations(self):
        path = Path(self.name)
        for item in path.parents:
            yield Folder(item)


class File(Container):
    
    ...
    
    def all_locations(self):
        folder = Folder(pathlib.Path(self.name))
        yield folder
        yield from folder.all_locations()
~~~

We also need the `Actor` object to have a location so the user can ask "where am I?". To do this we'll use a new object called `FileSystem` that we'll show next. For now, here's the `Actor` object, now with the ability to provide its location:

~~~     
class Actor(UniqueObject):
    def __init__(self, file_system, name, person):
        
        ...
        
        self.file_system = file_system
        self.current_directory = self.file_system.current_directory()
        
    ...
    
    def all_locations(self):
        if self.person == 1:
            # Return the locations for the user "me"
            yield self.current_directory
            yield from self.current_directory.all_locations()
~~~

Now we can implement `loc_nonsp` by calling `all_locations()` on any `x_actor` to get its "generic location" and compare it against `x_location` to see if `x_location` is the location of `x_actor`:

~~~
@Predication(vocabulary)
def loc_nonsp(state, e_introduced, x_actor, x_location):
    x_actor_value = state.get_variable(x_actor)
    x_location_value = state.get_variable(x_location)

    if x_actor_value is not None:
        if hasattr(x_actor_value, "all_locations"):
            if x_location_value is None:
                # This is a "where is X?" type query since no location specified
                for location in x_actor_value.all_locations():
                    yield state.set_x(x_location, location)
            else:
                # The system is asking if a location of x_actor is x_location,
                # so check the list exhaustively until we find a match, then stop
                for location in x_actor_value.all_locations():
                    if location == x_location_value:
                        # Variables are already set,
                        # no need to set them again, just return the state
                        yield state
                        break
    else:
        # For now, return errors for cases where x_actor is unbound
        pass
    
    report_error(["thingHasNoLocation", x_actor, x_location])
~~~

### The `FileSystem` object
Before we run an example to test the system, let's go through the new `FileSystem` object that we'll be building on for the rest of the tutorial. 

To implement "Where am I?", we'll need a notion of current directory which we'll implement with the `FileSystem.current_directory()` method. We'll also need to implement `FileSystem.all_individuals()` which will literally return every file and folder in the system. Clearly not going to be a fast operation! We'll be working on several ways of avoiding it.  

For now, we'll only be implementing the `FileSystemMock` class, which is a "mock" (i.e. fake) file system that we can pre-populate for testing.  It derives from `FileSystem` so it can be used anywhere that expects a `FileSystem` object, but will only return folders and files that we give it. We'll leave the real file system object unimplemented for now:

~~~
# The "real" file system is not implemented for now
# the Python "pass" command does nothing
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
    # [(True, "/dir1/dir2/filename.txt" # Set to True for a file
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
                self.files[item[1]] = {}
                root_path = os.path.dirname(item[1])
            else:
                # This is a directory
                root_path = item[1]

            # Add all of the parent directories from the item
            self.directories[root_path] = {}
            for new_path in Path(root_path).parents:
                self.directories[new_path] = {}

    def current_directory(self):
        return Folder(self.current)

    def all_individuals(self):
        for item in self.directories.items():
            yield Folder(name=item[0])

        for item in self.files.items():
            yield File(name=item[0])
~~~

Now we can implement `Example20()` using `FileSystemMock` to create a fake file system and interact with it:

~~~
def Example20_reset():
    return FileSystemState(FileSystemMock([(True, "/documents/file1.txt"),
                                           (False, "/Desktop")],
                                          "/Desktop"))


def Example20():
    user_interface = UserInterface(Example20_reset, vocabulary, respond_to_mrs_tree)

    while True:
        user_interface.interact_once()
        print()


# Running Example20 gives:
? where am i
Folder(name=/, size=0)
Folder(name=/Desktop, size=0)

? /show
User Input: where am i
1 Parses

***** CHOSEN Parse #0:
Sentence Force: ques
[ "where am i"
  TOP: h0
  INDEX: e2 [ e SF: ques TENSE: pres MOOD: indicative PROG: - PERF: - ]
  RELS: < [ loc_nonsp<0:5> LBL: h1 ARG0: e2 ARG1: x3 [ x PERS: 1 NUM: sg IND: + PT: std ] ARG2: x4 [ x PERS: 3 NUM: sg ] ]
          [ place_n<0:5> LBL: h5 ARG0: x4 ]
          [ which_q<0:5> LBL: h6 ARG0: x4 RSTR: h7 BODY: h8 ]
          [ pron<9:10> LBL: h9 ARG0: x3 ]
          [ pronoun_q<9:10> LBL: h10 ARG0: x3 RSTR: h11 BODY: h12 ] >
  HCONS: < h0 qeq h1 h7 qeq h5 h11 qeq h9 > ]

Unknown words: []

-- CHOSEN Parse #0, CHOSEN Tree #0: 

               ┌────── pron(x3)
pronoun_q(x3,RSTR,BODY)             ┌────── place_n(x4)
                    └─ which_q(x4,RSTR,BODY)
                                         └─ loc_nonsp(e2,x3,x4)

[['pronoun_q', 'x3', [['pron', 'x3']], [['which_q', 'x4', [['place_n', 'x4']], [['loc_nonsp', 'e2', 'x3', 'x4']]]]]]
Solution: x3 = Actor(name=User, person=1), x4 = Folder(name=/, size=0)
Solution: x3 = Actor(name=User, person=1), x4 = Folder(name=/Desktop, size=0)
Response: 
Folder(name=/, size=0)
Folder(name=/Desktop, size=0)
~~~

The system responded with all the locations where the user "is", namely the `/` folder and the `/Desktop` folder. There are two things we need to improve here: 

First, It would be nicer to respond to "Where am I?" with something like "in /Desktop", since exhaustively listing all the folders probably isn't what the user wants.  

Even more importantly: It isn't obvious from the output, but the query literally finds every `place` in the world (i.e. *every* file and folder) and calls `loc_nonsp` with each one. If we turn on tracing and run it again, you can see `call 5: ['loc_nonsp', ...` being called with `x4` (i.e. `x_location`) being set to every file and folder in our test data before the solution is returned: 

~~~
? where am i
Execution 2023-01-18 12:10:39,395: call 1: ['pronoun_q', 'x3', [['pron', 'x3']], [['which_q', 'x4', [['place_n', 'x4']], [['loc_nonsp', 'e2', 'x3', 'x4']]]]]() [ques]
Execution 2023-01-18 12:10:39,395: call 2: ['pron', 'x3']() [ques]
Execution 2023-01-18 12:10:39,396: call 3: ['which_q', 'x4', [['place_n', 'x4']], [['loc_nonsp', 'e2', 'x3', 'x4']]](x3 = Actor(name=User, person=1)) [ques]
Execution 2023-01-18 12:10:39,396: call 4: ['place_n', 'x4'](x3 = Actor(name=User, person=1)) [ques]
Execution 2023-01-18 12:10:39,396: call 5: ['loc_nonsp', 'e2', 'x3', 'x4'](x3 = Actor(name=User, person=1), x4 = Folder(name=/documents, size=0)) [ques]
Execution 2023-01-18 12:10:39,397: call 5: ['loc_nonsp', 'e2', 'x3', 'x4'](x3 = Actor(name=User, person=1), x4 = Folder(name=/, size=0)) [ques]
Execution 2023-01-18 12:10:39,397: call 5: ['loc_nonsp', 'e2', 'x3', 'x4'](x3 = Actor(name=User, person=1), x4 = Folder(name=/Desktop, size=0)) [ques]
Execution 2023-01-18 12:10:39,398: call 5: ['loc_nonsp', 'e2', 'x3', 'x4'](x3 = Actor(name=User, person=1), x4 = File(name=/documents/file1.txt, size=None)) [ques]
Folder(name=/, size=0)
Folder(name=/Desktop, size=0)
~~~

Works OK with our small data set but clearly not going to work with a real file system.  In the next two sections we'll address both of these issues.