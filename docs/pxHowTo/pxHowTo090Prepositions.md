## Directional Prepositions
Let's implement the verb "go" in `hello_world.py` to allow for moving around the file system in a simple way.

The phrase:

> go to a folder

... yields 4 parses, one of which is:

~~~
***** Parse #3:
Sentence Force: comm
[ "go to a folder"
  TOP: h0
  INDEX: e2 [ e SF: comm TENSE: pres MOOD: indicative PROG: - PERF: - ]
  RELS: < [ pronoun_q<0:14> LBL: h4 ARG0: x3 [ x PERS: 2 PT: zero ] RSTR: h5 BODY: h6 ]
          [ pron<0:14> LBL: h7 ARG0: x3 ]
          [ _go_v_1<0:2> LBL: h1 ARG0: e2 ARG1: x3 ]
          [ _to_p_dir<3:5> LBL: h1 ARG0: e8 [ e SF: prop TENSE: untensed MOOD: indicative PROG: - PERF: - ] ARG1: e2 ARG2: x9 [ x PERS: 3 NUM: sg IND: + ] ]
          [ _a_q<6:7> LBL: h10 ARG0: x9 RSTR: h11 BODY: h12 ]
          [ _folder_n_of<8:14> LBL: h13 ARG0: x9 ARG1: i14 ] >
  HCONS: < h0 qeq h1 h5 qeq h7 h11 qeq h13 > ]

-- CHOSEN Parse #0, CHOSEN Tree #0: 

          ┌────── _folder_n_of(x9,i14)
_a_q(x9,RSTR,BODY)               ┌────── pron(x3)
               └─ pronoun_q(x3,RSTR,BODY)    ┌── _to_p_dir(e8,e2,x9)
                                      └─ and(0,1)
                                               └ _go_v_1(e2,x3)
~~~

It introduces two additional predications we'll need to implement to make this work: `_to_p_dir` and `_go_v_1`.

`_to_p_dir` is a *directional* preposition.  Directional prepositions *usually* end with `_dir` and have the signature (`e`, `e_verb`, `x_location`).  `x_location` indicates the location the preposition is using, and `e_verb` indicates the event (often a verb) that this preposition should be attached to. They specify a particular direction in which to do something.  The fact that the predication takes an event as its second argument is a hint that the predication itself doesn't *do* anything except attach its information to the specified event so that something else can use it. Taking an event as an argument besides `ARG0` usually indicates the predication is modifying the event. So, it can be implemented like this:

~~~
@Predication(vocabulary, names=["_to_p_dir"])
def to_p_dir(state, e_introduced, e_target, x_location):
    x_location_binding = state.get_binding(x_location)

    preposition_info = {
        "EndLocation": x_location_binding
    }

    yield state.add_to_e(e_target, 
                         "DirectionalPreposition", 
                         {"Value": preposition_info, 
                          "Originator": execution_context().current_predication_index()})
~~~

This code just adds the location `x_location` to the `e_target` event under the key `DirectionalPreposition`. This allows the event that introduces it to consume it, as discussed in a [Event Predications topic](pxHowTo050EventPredications). The `Predication` class will ensure that the user will get a "don't understand" error if the predication that introduced the event doesn't know how to handle it, as discussed in that same topic.

Next, we need to implement `_go_v_1`, indicating that it *does* know how to handle that information, like this:

~~~
@Predication(vocabulary, 
             names=["_go_v_1"], 
             handles=[("DirectionalPreposition", EventOption.required)])
def go_v_1_comm(state, e_introduced_binding, x_actor_binding):
    x_location_binding = e_introduced_binding.value["DirectionalPreposition"]["Value"]["EndLocation"]

    def both_bound_function(actor_item, location_item):
        if actor_item.name == "Computer":
            # Only allow moving to folders
            if isinstance(location_item, Folder):
                return True

            else:
                if hasattr(x_location_binding.value, "exists") and location_item.exists():
                    report_error(["cantDo", "change directory to", x_location_binding.variable.name])

                else:
                    report_error(["notFound", x_location_binding.variable.name])

        else:
            report_error(["dontKnowActor", x_actor_binding.variable.name])

    def binding1_unbound_predication_function(location_item):
        # Actor is unbound, unclear when this would happen but report an error
        report_error(["dontKnowActor", x_actor_binding.variable.name])

    def binding2_unbound_predication_function(actor_item):
        # Location is unbound, ask them to be more specific
        report_error(["beMoreSpecific"])

    # go_v_1 effectively has two arguments since it has x_actor by default and requires x_location from a preposition
    for new_state in in_style_predication_2(state, 
                                            x_actor_binding, 
                                            x_location_binding,
                                            both_bound_function, 
                                            binding1_unbound_predication_function, 
                                            binding2_unbound_predication_function):
        yield new_state.apply_operations([ChangeDirectoryOperation(new_state.get_binding(x_location_binding.variable.name))])
~~~

The `handles=[]` clause on `Predication` tells the system that this predication *requires* a directional predication and the system ensures that it won't get called if it isn't there. That is why the code can just assume it is there and access the `EndLocation` key without checking for its existence first in this line:

~~~
x_location_binding = e_introduced_binding.value["DirectionalPreposition"]["Value"]["EndLocation"]
~~~
Note that the function has code to check if the object passed in actually exists or not so that it can return a more specialized error if the user asks to go somewhere that doesn't exist. Otherwise, they'd get the error "I can't go to X" if the folder doesn't exist, which is a little obtuse.

There is code for making sure the user didn't say "*he* goes to a folder", we only support "you".

And finally, we handle this as an action verb, just like we handled "delete" in the [Action Verbs topic](pxHowTo070ActionVerbs):

Like with "delete", 

Once the code pulls out the location, it needs a new operation to change directories (operations are discussed [here](../devhowto/devhowtoSimpleCommands)):

~~~
class ChangeDirectoryOperation(object):
    def __init__(self, folder_binding):
        self.folder_binding = folder_binding

    def apply_to(self, state):
        state.file_system.change_directory(self.folder_binding)
    
        
class FileSystemMock(FileSystem):

    ... 
    
    def change_directory(self, folder_binding):
        if self.exists(folder_binding.value.name):
            self.current = folder_binding.value

        else:
            raise MessageException("notFound", [folder_binding.variable.name])
~~~

Now, the system can change directories:

~~~
def Example23_reset():
    return FileSystemState(FileSystemMock([(True, "/documents/file1.txt", {"size": 1000}),
                                           (False, "/Desktop", {"size": 10000000}),
                                           (True, "/Desktop/the yearly budget.txt", {"size": 10000000}),
                                           (True, "/Desktop/blue", {"size": 1000})],
                                          "/Desktop"))


def Example23():
    user_interface = UserInterface(Example23_reset, vocabulary, respond_to_mrs_tree, error_priority)

    while True:
        user_interface.interact_once()
        print()
        
# Running Example23:
? go to "/documents"
Done!

? what is in this folder?
File(name=/documents/file1.txt, size=1000)

? go to "doesn't exist"
'doesn’t exist' was not found
~~~

> Comprehensive source for the completed tutorial is available [here](https://github.com/EricZinda/Perplexity).
