## Action Verbs
All of the predications we've dealt with so far have just been used to ask questions like "Is a file large?" or make propositions like "A file is large." (which is just a kind of question in terms of the kind of response a person would expect). Now it is time to implement "action verbs" -- verbs that actually *do* something to the system. Let's implement "delete".

"Delete" goes beyond asking questions about the state of the system. To implement it, we need to actually *modify* the state of the system. So far, we've only been using the `State` object to inspect and modify the state of MRS variables in the system. With "delete" we need to actually modify the state of the file system, too. Since the current state of all parts of the system is represented by the `state` object, we'll end up calling a method on that object in some form to delete a file. And, just like the `add_to_e()` or `set_x()` methods, the new method will need to return a new `state` object with that file deleted, and we'll `yield` the answer. 

If the user says, "delete a file", this MRS and tree are produced (among others):

~~~
[ "delete a file"
  TOP: h0
  INDEX: e2 [ e SF: comm TENSE: pres MOOD: indicative PROG: - PERF: - ]
  RELS: < [ pronoun_q<0:13> LBL: h4 ARG0: x3 [ x PERS: 2 PT: zero ] RSTR: h5 BODY: h6 ]
          [ pron<0:13> LBL: h7 ARG0: x3 ]
          [ _delete_v_1<0:6> LBL: h1 ARG0: e2 ARG1: x3 ARG2: x8 [ x PERS: 3 NUM: sg IND: + ] ]
          [ _a_q<7:8> LBL: h9 ARG0: x8 RSTR: h10 BODY: h11 ]
          [ _file_n_of<9:13> LBL: h12 ARG0: x8 ARG1: i13 ] >
  HCONS: < h0 qeq h1 h5 qeq h7 h10 qeq h12 > ]


               ┌────── pron(x3)
pronoun_q(x3,RSTR,BODY)          ┌────── _file_n_of(x8,i13)
                    └─ _a_q(x8,RSTR,BODY)
                                      └─ _delete_v_1(e2,x3,x8)
~~~

Let's ignore the pronoun related predications and focus on `_delete_v_1(e2,x3,x8)`. We're not going to handle any modifiers to it either, so we can ignore `e2` and `x3` (since `x3` represents the pronoun). That leaves `x8` which is the thing the user wants to delete. So, now we could try implementing the predication like the other single `x` predications we've built and call the `combinatorial_style_predication_1()` helper. The problem is, `_delete_v_1` is not combinatorial.

Combinatorial predications are those that when applied to a set, can be true for any chosen subset of the set. Delete, however doesn't make sense for a set of items "together".  Deleting items together sounds dangerously like "deleting them in a transaction".  Really, delete can only apply to one item at a time, it shouldn't support a "together" semantic unless it can really enforce it somehow. So, it will use a different helper called, `individual_style_predication_1` which ensures that only single individuals make it through, like this:

~~~
@Predication(vocabulary, names=["_delete_v_1"])
def delete_v_1_comm(state, e_introduced_binding, x_actor_binding, x_what_binding):
    def criteria(value):
        # Only allow deleting files and folders that exist
        # value will not be a tuple since individual_style_predication_1() was used
        if value in ["file1.txt", "file2.txt", "file3.txt"]:
            return True

        else:
            report_error(["cantDo", "delete", x_what_binding.variable.name])

    def unbound_what():
        report_error(["cantDo", "delete", x_what_binding.variable.name])

    yield from individual_style_predication_1(state, x_what_binding,
                                                        criteria, unbound_what,
                                                        ["cantXYTogether", "delete", x_what_binding.variable.name])
~~~
Note that `individual_style_predication_1()` has an extra argument at the end which is the error to report if it gets called with a set of more than one item.

So, this does *some* of the work we need: it will actually succeed if the user asks to delete a file or folder, and it won't allow phrases like "delete everything" that would produce an unbound `x8`. However, it won't actually *delete anything* because there isn't any code to do the deleting. 

`individual_style_predication_1()` yields a `state` object when `delete_v_1_comm` is successful. So, we could start by doing the actual delete when that functions yields a value, because it means everything has been checked and is `true`.

Let's imagine that we added a `state.delete_object()` to the `State` object that actually deletes a file and yields a new state with that file deleted. That approach could look like this:

~~~
@Predication(vocabulary, names=["_delete_v_1"])
def delete_v_1_comm(state, e_introduced_binding, x_actor_binding, x_what_binding):
    def criteria(value):
        # Only allow deleting files and folders that exist
        # value will not be a tuple since individual_style_predication_1() was used
        if value in ["file1.txt", "file2.txt", "file3.txt"]:
            return True

        else:
            report_error(["cantDo", "delete", x_what_binding.variable.name])

    def unbound_what():
        report_error(["cantDo", "delete", x_what_binding.variable.name])

    for success_state in individual_style_predication_1(state, x_what_binding,
                                                        criteria, unbound_what,
                                                        ["cantXYTogether", "delete", x_what_binding.variable.name]):
        object_to_delete = success_state.get_binding(x_what_binding.variable.name).value[0]
        yield success_state.delete_object(object_to_delete)        
~~~

This works because: 

When `individual_style_predication_1()` yields a new state, it means this predication was successful. That happened because the `criteria()` function returned `true`. The new state has all of the MRS variables set to the value that made the predication `true`, which means that the `x_what_binding` variable should now be set to the thing being deleted. 

However, we need to be careful to ask for the value of the variable represented by `x_what_binding` *in the new state*. Remember that `state` objects are immutable, so we have to look at the copy being returned to get the new value of the variable.

So, we looked up the variable name from `x_what_binding` in the new state returned by `individual_style_predication_1()`, like this:

~~~
object_to_delete = success_state.get_binding(x_what_binding.variable.name).value[0]
~~~

This is basically the approach we are going to use, but we need some extra mechanisms to do it. The reason why is described next.

### Operations
Actions that modify anything in the world state besides an MRS variable are called an `Operation` in Perplexity.  They go beyond manipulating the MRS and actually affect the world the person is speaking about. Any predication like `_delete_v_1` that wants to modify the state of the world needs to use an `Operation`.

`Operations` are a way of recording what to do and then doing it later: Think of an `Operation` as a way to package up a method call into an object and then *later* ask it to execute. 

An `Operation` is simply a Python class that has a single method:

~~~
def apply_to(self, state):

    ...
~~~

The constructor (i.e. the `__init__` method) is what packages up all the information needed to perform the operation later. It just gathers up the required arguments and stores them in the class. When it is time to actually perform the operation, `apply_to()` is called, and the `state` object that it should be applied to is passed in.

Here is an example of what a `DeleteOperation` could look like:

~~~
class DeleteOperation(object):
    def __init__(self, value_to_delete):
        self.value_to_delete = value_to_delete

    def apply_to(self, state):
        state.file_system.delete_item(self.value_to_delete)
~~~
The `DeleteOperation` itself is very simple, it is really just remembering what to delete. When it is asked to `apply_to()`, it calls the method in the `state` object that actually deletes the file, in *that* state object (which might be different than the one it was added to).

To use the `DeleteOperation`, we create an instance of one and pass it to a method in the `State` object, like this:
~~~
operation = DeleteOperation(new_state.get_binding(x_what_binding.variable.name).value[0])
new_state.record_operations([operation])
~~~

The `State` object has a `record_operations()` method that takes a list of operations to record, but in this case we're only doing one. Those two lines of code record that we want to delete a particular file, but they don't actually *do* it yet.  Later, when we have the final solution group, we can gather all of the operations that were done to the solutions in the group and call `apply_operations()` on the one single state we want to represent the new world.

Doing things in this more roundabout way solves two problems. Recall that the solver builds a list of all solutions (conceptually) and then groups them into solution groups. We don't want files *actually being deleted* during this phase because some of the solutions might not be used! Furthermore, each solution in a group will only have a subset of the files deleted. Using operations allows us to both delay state changes as well as apply them to a single state which can represent the "new state of the world" once we know what to do.

Now we can write the basic implementation of "delete":

~~~
@Predication(vocabulary, names=["_delete_v_1"])
def delete_v_1_comm(state, e_introduced_binding, x_actor_binding, x_what_binding):
    def criteria(value):
        # Only allow deleting files and folders that exist
        # value will not be a tuple since individual_style_predication_1() was used
        if value in ["file1.txt", "file2.txt", "file3.txt"]:
            return True

        else:
            report_error(["cantDo", "delete", x_what_binding.variable.name])

    def unbound_what():
        report_error(["cantDo", "delete", x_what_binding.variable.name])

    for success_state in individual_style_predication_1(state, x_what_binding,
                                                        criteria, unbound_what,
                                                        ["cantXYTogether", "delete", x_what_binding.variable.name]):
        object_to_delete = success_state.get_binding(x_what_binding.variable.name).value[0]
        operation = DeleteOperation(object_to_delete)
        yield success_state.record_operations([operation])
~~~

The final step that merges together all the operations and applies them to a single state is done by Perplexity automatically at the end of `interact_once()`. That's where `DeleteOperation.apply_to()` gets called for every solution.


### TODO: Talk about pron(x)

## Example
To make this run for real, we need to quit using hard coded lists of files since we're going to be deleting them. It is time to use a real `State` object to track state. The built-in Perplexity `State` object has a very simple mechanism for tracking objects. In most cases, we would need to derive a new class from it to manage the state of an application, but our examples are simple enough that we can use it directly.

The important parts of the class for our purposes here are below. A list of objects can be passed in the constructor and `State` will return them from `all_individuals()`. It is very simple:
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

We'll need to update the relevant predications to start using this object, as well as initializing the `state` so that it has all the objects we need at startup. We need to change `file_n_of`, `large_a_1` and `delete_v_1_comm` to use the `state` object instead of hard-coding the list of files:

~~~
@Predication(vocabulary, names=["_file_n_of"])
def file_n_of(state, x_binding, i_binding):
    def bound_variable(value):
        if value in state.all_individuals():
            return True
        else:
            report_error(["notAThing", x_binding.value, x_binding.variable.name])
            return False

    def unbound_variable():
        yield from state.all_individuals()

    yield from combinatorial_style_predication_1(state, x_binding, bound_variable, unbound_variable)



@Predication(vocabulary,
             names=["_large_a_1"],
             handles=[("DegreeMultiplier", EventOption.optional)])
def large_a_1(state, e_introduced_binding, x_target_binding):
    # See if any modifiers have changed *how* large we should be
    degree_multiplier = degree_multiplier_from_event(state, e_introduced_binding)

    def criteria_bound(value):
        if degree_multiplier == 1 and value == "file2.txt" and "file2.txt" in state.all_individuals():
            return True

        else:
            report_error(["adjectiveDoesntApply", "large", x_target_binding.variable.name])
            return False

    def unbound_values():
        if criteria_bound("file2.txt"):
            yield "file2.txt"

    yield from combinatorial_style_predication_1(state, x_target_binding, criteria_bound, unbound_values)

@Predication(vocabulary, names=["_delete_v_1"])
def delete_v_1_comm(state, e_introduced_binding, x_actor_binding, x_what_binding):
    def criteria(value):
        # Only allow deleting files and folders that exist
        # value will not be a tuple since individual_style_predication_1() was used
        if value in state.all_individuals():
            return True

        else:
            report_error(["cantDo", "delete", x_what_binding.variable.name])

    def unbound_what():
        report_error(["cantDo", "delete", x_what_binding.variable.name])

    for success_state in individual_style_predication_1(state, x_what_binding,
                                                        criteria, unbound_what,
                                                        ["cantXYTogether", "delete", x_what_binding.variable.name]):
        object_to_delete = success_state.get_binding(x_what_binding.variable.name).value[0]
        operation = DeleteOperation(object_to_delete)
        yield success_state.record_operations([operation])
~~~

... and create our initial `State` object with the starting list of files:

~~~
def reset():
    return State(["file1.txt", "file2.txt", "file3.txt"])
~~~

With those changes, we can now test the system:

~~~
python hello_world.py
? a file is large
Yes, that is true.

? delete a large file
Done!

? a file is large
a file is not large
~~~
