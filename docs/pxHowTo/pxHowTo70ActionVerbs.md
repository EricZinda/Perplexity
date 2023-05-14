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

Let's ignore the pronoun related predications and focus on `_delete_v_1(e2,x3,x8)`. We're not going to handle any modifiers to it either, so we can ignore `e2` and `x3` (since it represents the pronoun). That leaves `x8` which is the thing the user wants to delete. So, now we could try implementing the predication like the other single `x` predications we've built and call the `combinatorial_style_predication_1()` helper, like this:

~~~
@Predication(vocabulary, names=["_delete_v_1"])
def delete_v_1_comm(state, e_introduced_binding, x_actor_binding, x_what_binding):
    def criteria(value):
        # Only allow deleting files and folders that exist
        if isinstance(value[0], (File, Folder)) and value[0].exists():
            return True

        else:
            report_error(["cantDo", "delete", x_what_binding.variable.name])

    def unbound_what():
        report_error(["cantDo", "delete", x_what_binding.variable.name])

    yield from combinatorial_style_predication_1(state, x_what_binding, criteria, unbound_what)
~~~

This does some of the work we need: it will actually succeed if the user asks to delete a file or folder, and it won't allow phrases like "delete everything" that would produce an unbound `x8`. However, it won't actually *delete anything* because there isn't any code to do the deleting. 

Since `combinatorial_style_predication_1()` yields a `state` object when `delete_v_1_comm` is successful, we could start by doing the actual delete when it yields a value. 

Let's imagine that we added a `state.delete_object()` to the `State` object that actually deletes a file and yields a new state with that file deleted. That approach could look like this:

~~~
@Predication(vocabulary, names=["_delete_v_1"])
def delete_v_1_comm(state, e_introduced_binding, x_actor_binding, x_what_binding):
    def criteria(value):
        # Only allow deleting files and folders that exist
        if isinstance(value[0], (File, Folder)) and value[0].exists():
            return True

        else:
            report_error(["cantDo", "delete", x_what_binding.variable.name])

    def unbound_what():
        report_error(["cantDo", "delete", x_what_binding.variable.name])

    for success_state in combinatorial_style_predication_1(state, x_what_binding, criteria, unbound_what):
        object_to_delete = success_state.get_binding(x_what_binding.variable.name).value[0]
        yield success_state.delete_object(object_to_delete)
~~~
This works because: 

When `combinatorial_style_predication_1()` yields a new state, it means this predication was successful. That happened because the `criteria()` function returned `true`. The new state has all of the MRS variables set to the value that made the predication `true`, which means that the `x_what_binding` variable should now be set to the thing being deleted. 

However, we need to be careful to ask for the value of the variable represented by `x_what_binding` *in the new state*. Remember that `state` objects are immutable, so we have to look at the copy being returned to get the new value of the variable.

So, we need to look up the variable name from `x_what_binding` in the new state returned by `combinatorial_style_predication_1`, like this:

~~~
object_to_delete = success_state.get_binding(x_what_binding.variable.name).value[0]
~~~

This is basically the approach we are going to use, but we need to use some extra mechanisms to do it for reasons described below.

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

This solves two problems. Recall that the solver builds a list of all solutions (conceptually) and then groups them into solution groups. We don't want files *actually being deleted* during this phase because some of the solutions might not be used! Furthermore, each solution in a group will only have a subset of the files deleted. Using operations allows us to both delay state changes as well as apply them to a single state which can represent the "new state of the world" once we know what to do.

Now we can write the basic implementation of "delete":

~~~
@Predication(vocabulary, names=["_delete_v_1"])
def delete_v_1_comm(state, e_introduced_binding, x_actor_binding, x_what_binding):
    def criteria(value):
        # Only allow deleting files and folders that exist
        if isinstance(value[0], (File, Folder)) and value[0].exists():
            return True

        else:
            report_error(["cantDo", "delete", x_what_binding.variable.name])

    def unbound_what():
        report_error(["cantDo", "delete", x_what_binding.variable.name])

    for success_state in combinatorial_style_predication_1(state, x_what_binding, criteria, unbound_what):
        object_to_delete = success_state.get_binding(x_what_binding.variable.name).value[0]
        operation = DeleteOperation(object_to_delete)
        yield success_state.record_operations([operation])
~~~

The final step that merges together all the operations and applies them to a single state is done by Perplexity automatically at the end of `interact_once()`

### TODO: Talk about pron(x)