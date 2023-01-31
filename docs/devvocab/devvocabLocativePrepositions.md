
If the user types the phrase:

> copy "foo" in "/documents"

There are 171 different parses that the ERG provides since there is a lot of ambiguity in this phrase.  Here, we'll focus on the three different primary interpretations of how the verb `copy` and the preposition `in` are being used.

"in" is a preposition that indicates location, so-called "locative prepositions". 


The ERG provides three different primary interpretations of the usage of `in` with `copy`:

1. `_in_p_state(e13,e2,x14), _copy_v_1(e2,x3,x8)`: copy 'foo', and do the copy from within '/documents' [*where* to copy and where 'foo' *is* are not specified]

This reading has a version of "in" that takes the `e2` event for its second arg, and `e2` is introduced by `_copy_v_1`. This means that `in_p_state` is providing information to `_copy_v_1` about the location where the copying takes place.  The `_state` in the name indicates that the preposition is used in a "stative" sense, which effectively means: specifying where the verb is taking place. So this phrase says that the "copying" should be done "in the location specified by `x4`".  Where to copy *to* is not specified.

2. `_in_p_loc(e15,x8,x16), _copy_v_1(e2,x3,x8)`: copy the 'foo' that is in 'documents' [where to copy is not specified]

This version of "in" doesn't modify an event, so it isn't modifying how the verb works. Instead, it takes two `x` arguments and restricts them: `x8` must be something that is "in" `x16`. Then, `copy_v_1` should copy `x8`...somewhere.  Where is not specified.

3. `_copy_v_1(e2,x3,x8,_in_p_loc(e15,x8,x16))`: copy 'foo' such that it ends up in '/documents'

This version of `_copy_v_1` takes a scopal argument which contains the "in" preposition. As discussed in the section on scopal arguments, they occur in places where the predication needs to do something special with the branch of the tree it is passed.  In this case, `_copy_v_1` is being asked to "make `_in_p_loc(e15,x8,x16)` be true", meaning: change the world such that `_in_p_loc(e15,x8,x16)`. Since `x8` is "foo" and `x16` is "/documents", `_copy_v_1` should make "foo" be "in" "/documents".

4. (not shown)

There is another variation of the predication for "in" but we'll need to use the phrase "the mouse is running under the table" to see it. 

The mouse staying under the table and running around there (stative):
~~~
            ┌────── _mouse_n_1(x3)
_the_q(x3,RSTR,BODY)            ┌────── _table_n_1(x9)
                 └─ _the_q(x9,RSTR,BODY)    ┌── _under_p_state(e8,e2,x9)
                                     └─ and(0,1)
                                              └ _run_v_1(e2,x3)
~~~

The mouse moving from some other spot in the room on a path that takes it under the table (directional):
~~~
            ┌────── _table_n_1(x9)
_the_q(x9,RSTR,BODY)            ┌────── _mouse_n_1(x3)
                 └─ _the_q(x3,RSTR,BODY)    ┌── _under_p_dir(e8,e2,x9)
                                     └─ and(0,1)
                                              └ _run_v_1(e2,x3)
~~~

So, we've seen 4 ways a locative preposition can be used with a verb that takes a direction:

1. (stative) `_preposition_p_state(e,e1,x), verb_v(e1, ...)`: The actor or verb are happening at that place
2. (locative) `preposition_p_loc(e,x1,x), verb_v(..., x1)`: The verb should do what it does with whatever the preposition put in `x1`
3. (scopal) `verb_v(..., preposition_p_loc(e,x,x))`: The verb should make this preposition true via what it does
4. (directional) `_preposition_p_dir(e,e1,x), verb_v(e1, ...)`: The actor or verb are happening in that direction

We already have the version of "in" for #2 implemented, so let's start there.

### "copy the 'foo' that is in '/documents'"
Here is the version of `_in_p_loc` that we implemented in a [previous section](devvocabIn_p_loc):

~~~
@Predication(vocabulary, names=["_in_p_loc"])
def in_p_loc(state, e_introduced_binding, x_actor_binding, x_location_binding):
    if x_actor_binding.value is not None:
        if x_location_binding.value is not None:
            # x_actor is "in" x_location if x_location contains it
            for item in x_location_binding.value.contained_items(x_location_binding.variable):
                if x_actor_binding.value == item:
                    # Variables are already set,
                    # no need to set them again, just return the state
                    yield state

        else:
            # Need to find all the things that x_actor is "in"
            if hasattr(x_actor_binding.value, "containers"):
                for item in x_actor_binding.value.containers(x_actor_binding.variable):
                    yield state.set_x(x_location_binding.variable.name, item)

    else:
        # Actor is unbound, this means "What is in X?" type of question
        # Whatever x_location "contains" is "in" it
        if hasattr(x_location_binding.value, "contained_items"):
            for location in x_location_binding.value.contained_items(x_location_binding.variable):
                yield state.set_x(x_actor_binding.variable.name, location)

    report_error(["thingHasNoLocation", x_actor_binding.variable.name, x_location_binding.variable.name])
~~~

To make this work:

> copy "file1.txt" in "/documents"

... we only need to implement `_copy_v_1(e,x,x)`.  It will work very much like `_delete_v_1` [](../devhowto/devhowtoSimpleCommands):

~~~
class CopyOperation(object):
    def __init__(self, binding_from_copy, binding_to_copy):
        self.binding_from_copy = binding_from_copy
        self.binding_to_copy = binding_to_copy

    def apply_to(self, state):
        if isinstance(state, FileSystemState):
            state.file_system.copy_item(self.binding_from_copy, self.binding_to_copy)
            
            
class FileSystemMock(FileSystem):

    ...
    
    def copy_item(self, from_binding, to_binding):
        if self.exists(from_binding.value.name, is_file=isinstance(from_binding.value, File)):
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

                new_item = copy.deepcopy(self.item_from_path(from_binding.value.name, is_file=isinstance(from_binding.value, File)))
                new_item.name = new_item_path
                self.items[str(new_item_path)] = new_item

            else:
                raise MessageException("notFound", [to_binding.variable.name])

        else:
            raise MessageException("notFound", [from_binding.variable.name])
~~~

Now we can copy a file:
~~~
? what is in this folder?
File(name=/Desktop/the yearly budget.txt, size=10000000)
File(name=/Desktop/blue, size=1000)

? copy "file1.txt" in "/documents"
Done!

? what is in this folder?
File(name=/Desktop/the yearly budget.txt, size=10000000)
File(name=/Desktop/blue, size=1000)
File(name=/Desktop/file1.txt, size=1000)
~~~

"copy 'file1.txt' in '/documents'" is interpreted as "copy the file '/documents/file1.txt' to my current directory" since #2 is the only scenario of the four we started with that has all the predications implemented:

2. `_in_p_loc(e15,x8,x16), _copy_v_1(e2,x3,x8)`: copy the 'foo' that is in 'documents' [where to copy is not specified]


