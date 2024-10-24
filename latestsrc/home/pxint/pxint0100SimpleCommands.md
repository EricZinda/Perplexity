{% raw %}## Simple Commands
It is finally time to implement a "command" so that users can actually *do* something with the system we are building. We're going to implement the "delete" command.

We'll start with the MRS for "delete a large file", which has a few new predications to deal with:
```
[ TOP: h0
INDEX: e2
RELS: < 
[ pronoun_q LBL: h4 ARG0: x3 [ x PERS: 2 PT: zero ] RSTR: h5 BODY: h6 ]
[ pron LBL: h7 ARG0: x3 [ x PERS: 2 PT: zero ] ]
[ _a_q LBL: h9 ARG0: x8 [ x PERS: 3 NUM: sg IND: + ] RSTR: h10 BODY: h11 ]
[ _large_a_1 LBL: h12 ARG0: e13 [ e SF: prop TENSE: untensed MOOD: indicative PROG: bool PERF: - ] ARG1: x8 ]
[ _file_n_of LBL: h12 ARG0: x8 [ x PERS: 3 NUM: sg IND: + ] ARG1: i14 ]
[ _delete_v_1 LBL: h1 ARG0: e2 [ e SF: comm TENSE: pres MOOD: indicative PROG: - PERF: - ] ARG1: x3 ARG2: x8 ]
>
HCONS: < h0 qeq h1 h5 qeq h7 h10 qeq h12 > ]

                                               ┌── _large_a_1(e13,x8)
                                   ┌────── and(0,1)
               ┌────── pron(x3)    │             │
               │                   │             └ _file_n_of(x8,i14)
pronoun_q(x3,RSTR,BODY)            │
                    └─ _a_q(x8,RSTR,BODY)
                                        └─ _delete_v_1(e2,x3,x8)
```
The sentence force for this sentence is `SF: comm` meaning "command", determined the same way we [described in a previous section](https://blog.inductorsoftware.com/Perplexity/home/pxint/pxint0080SimplePropositions).

### Pronouns: pron and pronoun_q
The first two new predicates we encounter are: `pron(x3)` and `pronoun_q(x3,RSTR,BODY)` and they often work together as they do here. 

`pron(x)` needs to fill `x` with an object that represents what the specified pronoun is *referring to*. It does this by looking at the [properties](https://blog.inductorsoftware.com/Perplexity/home/mrscon/devhowto0010MRS) for the `x` variable to determine if the pronoun is "you" (`PERS: 2` -- second person), "him/her"(`PERS: 3` -- third person), etc. and sets the variable to be whatever make sense in the current context and matches the properties.

There were not any pronouns in our command, "delete a large file", so where did the `pron` predication come from? In this case, the pronoun is an *implied* "you" since it is a command. I.e "(You) delete a large file".  Because we are not including the notion of other people in the file system, the only pronouns we probably care to understand are "you" ("can you delete the file?" or the implied case above) and maybe "I" ("I want to delete a file"). For now, let's just do "you" and fail otherwise. 

To implement it, we'll need to create a new class to represent "actors" in the system, and then create an instance of it that represents the computer by adding it to the `State` object. We'll say that "the computer" is who should be returned when the user says "You" (second person) by setting the `Actor` object's `person` property to `2`. The example below has the new `Actor` object and  the `State` object filled with one:

```
# Represents something that can "do" things, like a computer
# or a human (or a dog, etc)
class Actor(UniqueObject):
    def __init__(self, name, person):
        super().__init__()
        self.name = name
        self.person = person

    def __repr__(self):
        return f"Actor(name={self.name}, person={self.person})"
        
        
def Example9():
    state = State([Actor(name="Computer", person=2),
                   Folder(name="Desktop"),
                   Folder(name="Documents"),
                   File(name="file1.txt", size=2000000),
                   File(name="file2.txt", size=1000000)])

...
```

(Why `Actor` derives from `UniqueObject` will be explained later in this topic.)

The `pron` implementation will look for an `Actor` object in the system with the same `person` value as the `pron` predication's `x` variable. To make sure the MRS is available for `pron` to inspect, we will create a "fake" mrs variable called `mrs` that is set to the MRS. Then any predication can inspect it. `pron` will retrieve it to do its work:

```
@Predication(vocabulary, name="pron")
def pron(state, x_who):
    mrs = state.get_binding("mrs").value[0]
    person = mrs["Variables"][x_who]["PERS"]
    for item in state.all_individuals():
        if isinstance(item, Actor) and item.person == person:
            yield state.set_x(x_who, (item, ))
            break
    

def Example9():
    state = State([Actor(name="Computer", person=2),
                   Folder(name="Desktop"),
                   Folder(name="Documents"),
                   File(name="file1.txt", size=2000000),
                   File(name="file2.txt", size=1000000)])

    mrs = {}
    mrs["Index"] = "e2"
    mrs["Variables"] = {"x3": {"PERS": 2},
                        "x8": {},
                        "e2": {"SF": "comm"},
                        "e13": {}}

    mrs["RELS"] = TreePredication(0, "pronoun_q", ["x3",
                                                   TreePredication(1, "pron", ["x3"]),
                                                   TreePredication(0, "_a_q", ["x8",
                                                                               [TreePredication(1, "_file_n_of", ["x8", "i1"]), TreePredication(2, "_large_a_1", ["e1", "x8"])],
                                                                               TreePredication(3, "_delete_v_1", ["e2", "x3", "x8"])])]
                                     )

    state = state.set_x("mrs", (mrs,))
    respond_to_mrs(state, mrs)
```

`pronoun_q` is just a simple, default quantifier predication that doesn't *do* anything except introduce the variable that `pron` uses. It acts just like `which_q` did in the [Simple Questions topic  ](https://blog.inductorsoftware.com/Perplexity/home/pxint/pxint0090SimpleQuestions). So, `pronoun_q` will use the `default_quantifer` we [defined in that topic](https://blog.inductorsoftware.com/Perplexity/home/pxint/pxint0090SimpleQuestions):

```
# This is just used as a way to provide a scope for a
# pronoun, so it only needs the default behavior
@Predication(vocabulary, name="pronoun_q")
def pronoun_q(state, x, h_rstr, h_body):
    yield from default_quantifier(state, x, h_rstr, h_body)
```

### Verbs and State Changes: delete_v_1
The last new predication is `_delete_v_1`. `_delete_v_1` is the first "real" verb we've dealt with. The others so far have been "implied" "to be" verbs for a phrase like "a file is large", and they don't show up in the MRS as described previously. A verb looks like every other predication: it has a name and arguments. And, because verbs can be modified by words like adverbs (e.g. "*permanently* delete the file"), it introduces an event to hang modifiers on. Like many verbs, the second argument represents the "actor": the person or thing doing the deleting. The final argument is what to delete.

Because our world state is simply a list of Python objects, the logic for deleting something is going to be trivial: remove the thing from the list. In fact, implementing what we are doing here in a real file system interface would be trivial as well: delete the file. However, we would have to decide what to do if a user command like "delete *every* file" fails to delete one of them for some reason. We'll ignore that in our example and just remove the files from the `State` object's list of state. We can safely do this, even though other predications may still be iterating over them, because our `State` object is immutable ([as described previously](https://blog.inductorsoftware.com/Perplexity/home/pxint/pxint0020PythonBasics)) and we will keep it that way by returning a new `State` object when something is deleted, just like we already do for setting variables.

We do have a problem, though. As you'll see later, we will encounter phrases like "delete *every* file", which have a different solution (i.e. state object) for each file that gets deleted. Each solution will have only *one* of the files deleted.  In order to end up with a single world state that has *all* the files deleted, we'll have to merge them together at the end somehow.

The solution is to create the concept of an "operation" class which does "something" to the state. We will build different operation classes that do different things over time (rename, copy, etc). If a command succeeds with multiple solutions, we can collect all of the operations from the solutions apply *all of them* to a *single* state object at the end. In fact, this is a good way to implement our system in general: build up a set of operations based on what the user says and, when we have the final, solved MRS, actually apply them to the file system. We won't be taking that final step here, but we would need to in order to handle all quantifiers. More on that in the section on Plurals.

We'll start by building some new mechanics into the `State` object to handle operations and create the `DeleteOperation` class:

```
class State(object):
    def __init__(self, objects):
        
        ...
        
        # Remember all the operations applied to the state object
        self.operations = []
    
    ...
    
    # Call to apply a list of operations to
    # a new State object
    def apply_operations(self, operation_list):
        newState = copy.deepcopy(self)
        for operation in operation_list:
            operation.apply_to(newState)
            newState.operations.append(operation)

        return newState

    def get_operations(self):
        return copy.deepcopy(self.operations)
        
        
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
```

An "operation" in our system is simply an object that has an `apply_to()` method that does something to the `State` object it is passed. The `DeleteOperation` operation class deletes any object in the system by removing it from the `State` object's list of objects. It uses a `unique_id` property to compare objects since they may have come from different `State` objects and will thus be copies and just comparing the objects will fail. This could be implemented in many ways and one approach is described at the very end of this section.

> This is a case where our "immutable" `State` class is actually being changed. That's OK, though, because only the `State` class will be asking it to do this, and only on a fresh `State` object that isn't in use yet.

When an operation is applied to the `State` class, we'll remember what happened by adding the operation to the new `State` object's list of operations.  Then, once we've collected all the solutions to a problem like "delete every file", we can gather the operations from each of the solutions using the `get_operations()` method, and apply them, as a group, to the original state. This will give us a new state object that combines them all. You'll see this at the end of this section.

So now we can finally implement the verb `delete_v_1`:

```
@Predication(vocabulary, name="_delete_v_1")
def delete_v_1(state, e_introduced, x_actor, x_what):
    # We only know how to delete things from the
    # computer's perspective
    x_actor_value = state.get_binding(x_actor).value
    if x_actor_value is not None and len(x_actor_value) == 1 and isinstance(x_actor_value[0], Actor) and x_actor_value[0].name == "Computer":
        x_what_value = state.get_binding(x_what).value
        
        # Only handle deleting one object at a time, don't support "together"
        if len(x_what_value) == 1:
            yield state.apply_operations([DeleteOperation(x_what_value[0])])
```

`delete_v_1` first checks to make sure the actor is "Computer". That's because the user could have said "Bill deletes a file" and we'd prefer the system to say "I don't know who Bill is" than to just delete the file. We should only delete the file when *the computer* is told to delete it. 

Then, we use our new `apply_operations()` method to do the deleting and return the new state object with the object gone.

Finally, we need to add a new clause to `respond_to_mrs()` to handle *commands*. It will simply say "Done!" if the command worked. It will also collect up all of the operations that happened and apply them to a single state object. This isn't really necessary for this example since we are only deleting one file, but is necessary for phrases like "delete every file":

```
def respond_to_mrs(state, mrs):    
    ...
    
        elif force == "comm":
        # This was a command so, if it works, just say so
        # We'll get better errors and messages in upcoming sections
        if len(solutions) > 0:
            # Collect all the operations that were done
            all_operations = []
            for solution in solutions:
                all_operations += solution.get_operations()

            # Now apply all the operations to the original state object and
            # print it to prove it happened
            final_state = state.apply_operations(all_operations)

            print("Done!")
            print(final_state.objects)
        else:
            print("Couldn't do that.")
```

Now we can run an example for "delete a large file":

```
def Example9():
    state = State([Actor(name="Computer", person=2),
                   Folder(name="Desktop"),
                   Folder(name="Documents"),
                   File(name="file1.txt", size=2000000),
                   File(name="file2.txt", size=1000000)])

    mrs = {}
    mrs["Index"] = "e2"
    mrs["Variables"] = {"x3": {"PERS": 2},
                        "x8": {},
                        "e2": {"SF": "comm"},
                        "e13": {}}

    mrs["RELS"] = TreePredication(0, "pronoun_q", ["x3",
                                                   TreePredication(1, "pron", ["x3"]),
                                                   TreePredication(0, "_a_q", ["x8",
                                                                               [TreePredication(1, "_file_n_of", ["x8", "i1"]), TreePredication(2, "_large_a_1", ["e1", "x8"])],
                                                                               TreePredication(3, "_delete_v_1", ["e2", "x3", "x8"])])]
                                     )

    state = state.set_x("mrs", (mrs,))
    respond_to_mrs(state, mrs)
    
# Outputs:
Done!
[Actor(name=Computer, person=2), Folder(Desktop), Folder(Documents), File(file2.txt, 1000000)]
```

You can see by the output that the only large file in the system was deleted: "file1.txt".

There are a couple of interesting things about what we've done. The code for `delete_v_1` will delete *anything*, so the phrase "delete you" will actually work! Of course, it will then mess up the system because every command after that will not be able to find the implied "you". This is part of the magic and the challenge of implementing MRS predications, if you implement them right, they can be very general and allow constructions that you hadn't thought of.

## Identity
Because the system is built around immutable state, we will sometimes end up with two `State` objects and need to be able to find the same object contained in either one.  This happened in the implementation of the `DeleteOperation`. We need a way to compare objects *across* state objects. The easiest way is to give all the objects in the system a globally unique id that can be easily compared. In the example above, we created a base class, `UniqueObject` that does this and derived everything from it:

```
class UniqueObject(object):
    def __init__(self):
        self.unique_id = uuid.uuid4()
        
class File(UniqueObject):
    def __init__(self, name, size=0):
        super().__init__()
        self.name = name
        self.size = size

    def __repr__(self):
        return f"File({self.name}, {self.size})"


class Folder(UniqueObject):
    def __init__(self, name):
        super().__init__()
        self.name = name

    def __repr__(self):
        return f"Folder({self.name})"
```

Then the caller can just compare the `.unique_id` property, like we did in `DeleteOperation`:

```
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
```

> Comprehensive source for the completed tutorial is available [here](https://github.com/EricZinda/Perplexity/tree/main/samples/hello_world)

Last update: 2024-10-24 by Eric Zinda [[edit](https://github.com/EricZinda/Perplexity/edit/main/docs/pxint/pxint0100SimpleCommands.md)]{% endraw %}