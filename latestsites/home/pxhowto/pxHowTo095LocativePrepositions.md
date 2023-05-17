{% raw %}## Verbs and Locative Prepositions
Locative prepositions like "in" specify the location of something, but they can be used in several different ways. We'll examine them via the phrase:

> copy "foo" in "/documents"


There are 171 different parses that the ERG provides since there is a lot of ambiguity in this phrase.  Here, we'll focus on the parses that use "copy" as a verb along with "in" as a preposition. Shown below are 4 different patterns (aka *phenomena*) that appear. They are listed showing the form of the "in" and "copy" predications, along with their interpretation:

1. `_in_p_loc(e15,x8,x16), _copy_v_1(e2,x3,x8)`: Copy the 'foo' that is in 'documents' [where to copy *to* is not specified]
   
   This version of "in" has already been implemented in the [In-style Predications topic](https://blog.inductorsoftware.com/Perplexity/home/pxhowto/pxHowTo030InStylePredications) and doesn't need modification. It takes two `x` arguments and restricts them: `x8` must be something that is "in" `x16`. This is a "locative" form of the "in" preposition that specifies where something is.  So, `in_p_loc` indicates where to find `x8` (in `x16`), and `copy_v_1` simply needs to copy `x8`...somewhere.  *Where* is not specified.
2. `_in_p_state(e13,e2,x14), _copy_v_1(e2,x3,x8)`: Copy 'foo', and do the copy from within '/documents' [*where* to copy and where 'foo' *is* are not specified]
   
   This reading has a version of "in" that takes the `e2` event for its second arg, and `e2` is introduced by `_copy_v_1`. As described in the [Directional Prepositions topic](https://blog.inductorsoftware.com/Perplexity/home/pxhowto/pxHowTo090Prepositions), this means that `in_p_state` is providing information to `_copy_v_1` about how to go about copying. But, unlike directional prepositions described in that topic, `_state` in the predication name indicates that the preposition is used in a "stative" sense. This means it is specifying where the verb is *taking place*. So this phrase says that the "copying" should be done "in the location specified by `x4`".  Where to copy *to* is not specified.
3. `_copy_v_1(e2,x3,x8,_in_p_loc(e15,x8,x16))`: Copy 'foo' such that it ends up in '/documents'
   
   This version of `_copy_v_1` has a scopal argument which contains the "in" preposition. As discussed in the [MRS Overview](https://blog.inductorsoftware.com/Perplexity/home/mrscon/devhowto0010MRS), scopal arguments occur when the predication needs to do something special with the branch of the tree it is passed.  In this case, `_copy_v_1` is being asked to change the world such that the branch it is being passed (i.e. `_in_p_loc(e15,x8,x16)`) is `true`. Since `x8` is "foo" and `x16` is "/documents", `_copy_v_1` should make "foo" be "in" "/documents".
4. (not used in this example) `_preposition_p_dir(e,e1,x), verb_v(e1, ...)`
   
   There is another variation of the predication for "in" that the ERG doesn't generate for this example, but was shown in [the topic on `go_v_1`](https://blog.inductorsoftware.com/Perplexity/home/pxhowto/pxHowTo070ActionVerbs). Look at the two interpretations of "the mouse is running under the table":
   
   (stative) Just like example 1 above: The mouse staying under the table and running around there:

```
                ┌────── _mouse_n_1(x3)
    _the_q(x3,RSTR,BODY)            ┌────── _table_n_1(x9)
                    └─ _the_q(x9,RSTR,BODY)    ┌── _under_p_state(e8,e2,x9)
                                        └─ and(0,1)
                                                └ _run_v_1(e2,x3)
```

(directional) Just like [`to_p_dir` in the topic on `go_v_1`](https://blog.inductorsoftware.com/Perplexity/home/pxhowto/pxHowTo070ActionVerbs): The mouse moving from some other spot in the room on a path that takes it under the table:

```
                ┌────── _table_n_1(x9)
    _the_q(x9,RSTR,BODY)            ┌────── _mouse_n_1(x3)
                    └─ _the_q(x3,RSTR,BODY)    ┌── _under_p_dir(e8,e2,x9)
                                        └─ and(0,1)
                                                └ _run_v_1(e2,x3)
```

So, we've seen 4 ways that MRS can use a locative preposition with a verb that takes a direction:

1. (locative) `preposition_p_loc(e,x1,x2), verb_v(..., x1)`: The verb should do what it does with whatever the preposition put in `x1`
2. (stative) `_preposition_p_state(e,e1,x2), verb_v(e1, ...)`: The actor or verb is happening at the place indicated by whatever the preposition put in `x2`
3. (scopal) `verb_v(..., preposition_p_loc(e,x,x))`: The verb should make this preposition true via what it does
4. (directional) `_preposition_p_dir(e,e1,x), verb_v(e1, ...)`: The actor or verb are happening in that direction

We already have the locative version of "in" (#1) [implemented](https://blog.inductorsoftware.com/Perplexity/home/pxhowto/pxHowTo030InStylePredications), so let's start there.

### 1. `_in_p_loc(e15,x8,x16), _copy_v_1(e2,x3,x8)`: Copy the 'foo' that is in 'documents'
Here is the version of `_in_p_loc` that we implemented in the section on [In-style Predications](https://blog.inductorsoftware.com/Perplexity/home/pxhowto/pxHowTo030InStylePredications), but updated using the new `FileSystemState` object instead of placeholder methods:

```
@Predication(vocabulary, names=["_in_p_loc"])
def in_p_loc(state, e_introduced_binding, x_actor_binding, x_location_binding):
    def item_in_item(item1, item2):
        # x_actor is "in" x_location if x_location contains it
        found_location = False
        if hasattr(item2, "contained_items"):
            for item in item2.contained_items(x_location_binding.variable):
                if item1 == item:
                    found_location = True
                    break

        if not found_location:
            report_error(["thingHasNoLocation", x_actor_binding.variable.name, x_location_binding.variable.name])

        return found_location

    def location_unbound_values(actor_value):
        # This is a "what is actor in?" type query since no location specified (x_location_binding was unbound)
        # Order matters, so all_locations needs to return the best answer first
        if hasattr(actor_value, "all_locations"):
            for location in actor_value.all_locations(x_actor_binding.variable):
                yield location

        report_error(["thingHasNoLocation", x_actor_binding.variable.name, x_location_binding.variable.name])

    def actor_unbound_values(location_value):
        # This is a "what is in x?" type query since no actor specified (x_actor_binding was unbound)
        # Order matters, so all_locations needs to return the best answer first
        if hasattr(location_value, "contained_items"):
            for actor in location_value.contained_items(x_location_binding.variable):
                yield actor
        else:
            report_error(["thingIsNotContainer", x_location_binding.variable.name])

    yield from in_style_predication_2(state, x_actor_binding, x_location_binding, item_in_item, actor_unbound_values, location_unbound_values)

    report_error(["thingHasNoLocation", x_actor_binding.variable.name, x_location_binding.variable.name])
```

To make this work:

> copy "file1.txt" in "/documents"


... we only need to implement `_copy_v_1(e,x,x)`.  It will work very much [like `_delete_v_1`]():

```
# "copy" where the user did not say where to copy to, assume current directory
@Predication(vocabulary, names=["_copy_v_1"])
def copy_v_1_comm(state, e_introduced_binding, x_actor_binding, x_what_binding):
    # We only know how to copy things from the
    # computer's perspective
    if x_actor_binding.value.name == "Computer":
        # Only allow copying files and folders
        if isinstance(x_what_binding.value, (File, Folder)):
            yield state.apply_operations([CopyOperation(None, x_what_binding, None)])

        else:
            report_error(["cantDo", "copy", x_what_binding.variable.name])

    else:
        report_error(["dontKnowActor", x_actor_binding.variable.name])
        
        
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
```

Now we can copy a file:
```
? what is in this folder?
File(name=/Desktop/the yearly budget.txt, size=10000000)
File(name=/Desktop/blue, size=1000)

? copy "file1.txt" in "/documents"
Done!

? what is in this folder?
File(name=/Desktop/the yearly budget.txt, size=10000000)
File(name=/Desktop/blue, size=1000)
File(name=/Desktop/file1.txt, size=1000)
```

In this case, "copy 'file1.txt' in '/documents'" is interpreted as "copy the file '/documents/file1.txt' to my current directory" since "in" is interpreted as applying to where the file is and where to copy *to* isn't specified.

### 2. `_in_p_state(e13,e2,x14), _copy_v_1(e2,x3,x8)`: Copy 'foo', and do the copy from within '/documents'

Next up we'll tackle the stative version of "in". Recall that "stative" means where the verb is "happening" and so it tells `_copy_v_1` where to do the copying *from*.

This will work exactly the same as the previous example if there is a relative file name. That is because "doing the copy from within 'documents'" sets the current directory to "/documents" and the previous inteprets the file itself "in" documents. Both approaches resolve to the same file. However, an absolute file name should work here (since current directory is not used when calculating an absolute file name) but should *not* work in the above example (since the absolute path won't be "in" that directory).

Here's the code for stative "in" and a version of "copy" that uses it:

```
@Predication(vocabulary, names=["_in_p_state"])
def in_p_state(state, e_introduced_binding, e_target_binding, x_location_binding):
    preposition_info = {
        "EndLocation": x_location_binding
    }

    yield state.add_to_e(e_target_binding.variable.name, "StativePreposition", {"Value": preposition_info, "Originator": execution_context().current_predication_index()})


# "copy" where the user specifies where to copy "from". Assume "to" is current directory since it isn't specified
# This is really only different from the locative "_in_p_loc(e15,x8,x16), _copy_v_1(e2,x3,x8)" version if:
# a) The from directory doesn't exist
# b) The thing to copy has a relative path because our "current directory" for the file will be different
@Predication(vocabulary, names=["_copy_v_1"], handles=[("StativePreposition", EventOption.required)])
def stative_copy_v_1_comm(state, e_introduced_binding, x_actor_binding, x_what_binding):
    x_copy_from_location_binding = e_introduced_binding.value["StativePreposition"]["Value"]["EndLocation"]

    # We only know how to copy things from the
    # computer's perspective
    if x_actor_binding.value.name == "Computer":
        # We only know how to copy something "from" a folder
        if isinstance(x_copy_from_location_binding.value, Folder):
            # Only allow copying files and folders
            if isinstance(x_what_binding.value, (File, Folder)):
                yield state.apply_operations([CopyOperation(x_copy_from_location_binding, x_what_binding, None)])

            else:
                report_error(["cantDo", "copy", x_what_binding.variable.name])

        else:
            report_error(["cantDo", "copy from", x_what_binding.variable.name])

    else:
        report_error(["dontKnowActor", x_actor_binding.variable.name])
```
We're using the same pattern in `_in_p_state` that we used for `_in_p_dir` in a previous topic: the preposition is just adding its information to the event it is passed, and the verb that introduced that event consumes the information to do its job.

`FileSystemMock.copy_item()` only changed to use a "copy from" directory to set the base of a relative file name:

```
class FileSystemMock(FileSystem):
    
    ...
    
    def copy_item(self, from_directory_binding, from_binding, to_binding):
        if from_directory_binding is not None:
            # PurePath will only attach the from_directory_binding.value.name to the front if
            # if from_binding.value is relative, otherwise it is ignored
            from_path = str(pathlib.PurePath(from_directory_binding.value.name, from_binding.value.name))
        else:
            from_path = from_binding.value.name
```

With that in place, we can try two different phrases.  One that will work with the locative "in" we implemented first, and one that will only work with the stative "in". Since the system will stop once an MRS succeeds, and since the parse for the locative "in" gets executed first, we'll be able to see if the locative "in" really doesn't work (and the new one does):
```
? copy "file1.txt" in "/documents"
Done!

? /show

...

                           ┌── quoted(\\>documents,i21)
               ┌────── and(0,1)
               │             └ fw_seq(x16,i21)
               │                                                        ┌──── _in_p_loc(e15,x8,x16)
proper_q(x16,RSTR,BODY)                                                 │
                    │                                                   │ ┌── quoted(file1.txt,i13)
                    │                                       ┌────── and(0,1,2)
                    │                 ┌────── pron(x3)      │               │
                    │                 │                     │               └ fw_seq(x8,i13)
                    └─ pronoun_q(x3,RSTR,BODY)              │
                                           └─ proper_q(x8,RSTR,BODY)
                                                                 └─ _copy_v_1(e2,x3,x8)

...

? copy "/Desktop/blue" in "/documents"
Done!

? /show

...

                           ┌── quoted(\\>documents,i21)
               ┌────── and(0,1)
               │             └ fw_seq(x16,i21)
proper_q(x16,RSTR,BODY)                                                 ┌── quoted(\\>Desktop\\>blue,i13)
                    │                                       ┌────── and(0,1)
                    │                 ┌────── pron(x3)      │             └ fw_seq(x8,i13)
                    └─ pronoun_q(x3,RSTR,BODY)              │
                                           └─ proper_q(x8,RSTR,BODY)
                                                                 │      ┌── _in_p_state(e15,e2,x16)
                                                                 └─ and(0,1)
                                                                          └ _copy_v_1(e2,x3,x8)
                                                                          
...
```

Now we have two interpretations of "in" working, let's move on to the third which is more involved.

### 3. `_copy_v_1(e2,x3,x8,_in_p_loc(e15,x8,x16))`: Copy 'foo' such that it ends up in '/documents'

This version of `_copy_v_1` takes a scopal argument which contains the "in" preposition. As discussed in the topic on scopal arguments, scopal arguments occur in places where the predication needs to do something special with the branch of the tree it is passed.  In this case, `_copy_v_1` is being asked to "make `_in_p_loc(e15,x8,x16)` be true", meaning: change the world such that `_in_p_loc(e15,x8,x16)`. Since `x8` is "foo" and `x16` is "/documents", `_copy_v_1` should make "foo" be "in /documents".

Here are two other examples of verbs taking scopal arguments to illustrate:
```
put the vase on the table

            ┌────── _vase_n_1(x8)
_the_q(x8,RSTR,BODY)             ┌────── _table_n_1(x16)
                 └─ _the_q(x16,RSTR,BODY)               ┌────── pron(x3)
                                      └─ pronoun_q(x3,RSTR,BODY)                    ┌─ _on_p_loc(e15,x8,x16)
                                                             └─ _put_v_1(e2,x3,x8,ARG3)
                                                             
paint the tree green

            ┌────── _tree_n_of(x8,i14)
_the_q(x8,RSTR,BODY)               ┌────── pron(x3)
                 └─ pronoun_q(x3,RSTR,BODY)                      ┌─ _green_a_2(e16,x8)
                                        └─ _paint_v_1(e2,x3,x8,ARG3)
```

In all these cases, the verb using a scopal argument because they all examples of a phrase taking something in the world and changing it. This type of scenario needs a scopal argument because a normal predication would attempt to find a "foo" that *is* in "/documents" ... and that is not true yet. The scopal argument doesn't get evaluated normally (as we'll see below), so it avoids this problem.

So, verbs with scopal arguments have to do what they do in such a way that their scopal argument becomes true. This can all seem wonderfully abstract if you try to imagine how to write code which "paints x in a way that makes any possible thing true", but the approach we're going to take here is much more concrete: Break down each scenario we are focused on for a given verb and implement that.

For example, for "copy 'foo' in '/documents'", the scopal argument is a locative preposition:

```
                          ┌── quoted(foo,i14)
              ┌────── and(0,1)
              │             └ fw_seq(x8,i14)
proper_q(x8,RSTR,BODY)                           ┌── quoted(/documents,i23)
                   │                 ┌────── and(0,1)
                   │                 │             └ fw_seq(x18,i23)
                   └─ proper_q(x18,RSTR,BODY)
                                          │                 ┌────── pron(x3)
                                          └─ pronoun_q(x3,RSTR,BODY)                     ┌─ _in_p_loc(e17,x8,x18)
                                                                 └─ _copy_v_1(e2,x3,x8,ARG3)
```

So, we can implement a version of `_copy_v_1` that knows how to deal with locative prepositions. If we do it carefully, it will work with all kind of locative prepositions. 

Here's how: Note that the following examples all have the same structure even though they use different locative prepositions, only the preposition is different:

```
> copy "foo" into "/documents"

                          ┌── quoted(foo,i14)
              ┌────── and(0,1)
              │             └ fw_seq(x8,i14)
proper_q(x8,RSTR,BODY)                           ┌── quoted(/documents,i23)
                   │                 ┌────── and(0,1)
                   │                 │             └ fw_seq(x18,i23)
                   └─ proper_q(x18,RSTR,BODY)
                                          │                 ┌────── pron(x3)
                                          └─ pronoun_q(x3,RSTR,BODY)                     ┌─ _into_p(e17,x8,x18)
                                                                 └─ _copy_v_1(e2,x3,x8,ARG3)


> copy "foo" above "/documents"

                          ┌── quoted(foo,i14)
              ┌────── and(0,1)
              │             └ fw_seq(x8,i14)
proper_q(x8,RSTR,BODY)                           ┌── quoted(/documents,i23)
                   │                 ┌────── and(0,1)
                   │                 │             └ fw_seq(x18,i23)
                   └─ proper_q(x18,RSTR,BODY)
                                          │                 ┌────── pron(x3)
                                          └─ pronoun_q(x3,RSTR,BODY)                     ┌─ _above_p(e17,x8,x18)
                                                                 └─ _copy_v_1(e2,x3,x8,ARG3)
```

We need a mechanism that converts scopal predications into a generic form so all of the examples above can be handled in the same way. This form should allow `_copy_v_1` to avoid special casing every single locative preposition.

To do this, we can't just `call()` with the scopal argument `_in_p_loc(e17,x8,x18)` (as we do for quantifiers) -- it will fail since it isn't true yet. "foo" is not yet *in* "/documents". Even if it did work, it wouldn't be in a general form. 

Let's call the form we want: *"normalization"* (this is not a DELPH-IN term, it is being invented here as an concept used for implementation). "Normalizing" a predication will put it into a more general (or canonical) form to reduce whole classes of similar predications (like locative prepositions) into a single form the code can handle the same. Here are a couple of examples to clarify:

- Normalizing a locative preposition would put it in into a form that contains the thing being located and the place it is being located to. Note that this is *not* necessarily just the two arguments of a locative preposition, as is. `_above_p(e17,x8,x18)`, for example, would need to record the place (or places) "above" `x18` instead of `x18` itself.
- Normalizing an adjective like `_green_a_2(e16,x8)` might be as simple as recording the adjective and the thing it is applied to, but it won't always come from predications that are of the form `adjective(e,x)`. "paint the tree lit" (for a Christmas tree, perhaps) generates the "adjective" `_light_v_cause(e16,i17,x8)` which is a form of verb being *used* as an adjective.

So, we'll need to implement another version of each predication that knows how to normalize itself. We'll ask it to put this normalized form into its own introduced event (since it is just information about itself) so that predications like `_copy_v_1` can inspect it and decide what to do. And, just like we use the `_comm` postfix on predications that implement commands (as opposed to questions), we'll invent a new postfix called `_norm` to indicate that this version of the predication should only be used when it is asked to normalize.  Like this:

```
@Predication(vocabulary, names=["_in_p_loc"])
def in_p_loc_norm(state, e_introduced_binding, x_actor_binding, x_location_binding):
    preposition_info = {
        "EndLocation": x_location_binding
    }
    yield state.add_to_e(e_introduced_binding.variable.name, "LocativePreposition", {"Value": preposition_info, "Originator": execution_context().current_predication_index()})
```

In this example, we've decided the normalized form of a locative preposition in an event should have the key `LocativePreposition` and this JSON value:

```
{
    "LeftSide": x_actor_binding,
    "EndLocation": x_location_binding
}
```

... which indicates the "left side" of the locative preposition (i.e. the first, or left argument) and the place where that thing should end up.  Note that this normalized form allows the inspector to ignore what the preposition actually *is* and just deal with "the place the left side should end up", thus allowing the copy code to be generalized.

Next, we need a way for `copy_v_1` to normalize its scopal argument. We can add a `normalize` argument to `ExecutionContext._call_predication()` that simply asks to call predications of type "norm" when it is set. That, along with allowing "norm" as a kind of predication in the `Predication` decorator, is all that is needed:

```
class ExecutionContext(object):
    
    ...
    
    def _call_predication(self, state, predication, normalize=False):
    
    ...
    
            for module_function in self.vocabulary.predications(predication.name,
                                                            predication.arg_types,
                                                            self._phrase_type if normalize is False else "norm"):
    
    ...
```

The next problem is that the scopal argument for `copy_v_1` could be a whole tree. For example:

> copy "blue" in the folder under "/documents"


... generates a more complicated scopal argument:

```
                                                                    ┌── quoted(/documents,i29)
            ┌────── _blue_a_1(x8,i14)                   ┌────── and(0,1)
udef_q(x8,RSTR,BODY)             ┌────── _folder_n_of(x1│,i22)        └ fw_seq(x24,i29)
                 └─ _the_q(x17,RSTR,BODY)               │
                                      └─ proper_q(x24,RSTR,BODY)
                                                             │                 ┌────── pron(x3)                    ┌── _under_p_state(e23,e16,x24)
                                                             └─ pronoun_q(x3,RSTR,BODY)                     ┌─ and(0,1)
                                                                                    └─ _copy_v_1(e2,x3,x8,ARG3)      └ _in_p_loc(e16,x8,x17)
```

So we need a way to somehow figure out which of the predications in the scopal argument introduce the event that holds the "LocativePreposition" value we care about.  Because `_copy_v_1` has an argument (`x8`) which indicates what it should copy, we can assume any predications in the scopal arg that modify `x8` are the ones saying where `x8` should go.  We can write a helper that returns those events:

```
# Determine which events modify this individual
def scopal_events_modifying_individual(x_individual, h_scopal):
    events = []
    for predication in find_predications_using_variable_ARG1(h_scopal, x_individual):
        if predication.arg_types[0] == "e":
            events.append(predication.args[0])

    return events
```

And now we are finally ready to write the `_copy_v_1` verb itself! Be forewarned that there is a lot of "mechanism" to fish the right things out of the right places. We'll fix that next. But first, let's see the raw code and understand what it does:

```
@Predication(vocabulary, names=["_copy_v_1"])
def locative_copy_v_1_comm(state, e_introduced_binding, x_actor_binding, x_what_binding, h_where):

    # We only know how to copy things from the
    # computer's perspective
    if x_actor_binding.value.name == "Computer":

        # Only allow copying files and folders
        if isinstance(x_what_binding.value, (File, Folder)):
        
            # Determine which events in the scopal argument will hold
            # the LocativePreposition
            where_events = scopal_events_modifying_individual(x_what_binding.variable.name, h_where)
            found_locative_preposition = False
            if len(where_events) > 0:

                # Normalize the tree, which could return multiple solutions like any call()
                for solution in call(state, h_where, normalize=True):
                    
                    # Get the value for each event and see if it holds a 
                    # LocativePreposition
                    for where_event in where_events:
                        e_where_binding = solution.get_binding(where_event)
                        if "LocativePreposition" in e_where_binding.value:
                            
                            # found the information in the event, copy "in" that location
                            found_locative_preposition = True
                            
                            # Only allow copying into folders
                            to_location_binding = e_where_binding.value["LocativePreposition"]["Value"]["EndLocation"]
                            if isinstance(to_location_binding.value, Folder):
                                yield state.apply_operations([CopyOperation(None, x_what_binding, to_location_binding)])

                            else:
                                report_error(["cantDo", "copy", to_location_binding.variable.name])

            if not found_locative_preposition:
                # Fail since we don't know what kind of scopal argument this is
                report_error(["formNotUnderstood", "missing", "LocativePreposition"])

        else:
            report_error(["cantDo", "copy", x_what_binding.variable.name])

    else:
        report_error(["dontKnowActor", x_actor_binding.variable.name])
```

Before we simplify the code, let's try out some scenarios to make sure it works.  Remember that we have two other interpretations of "copy 'file1.txt' in '/documents'" that are implemented already. In fact, those two interpretations are returned first by the ERG. So, any phrase that succeeds with one of those won't exercise this new code.  The phrase "copy 'blue' in '/documents'" will only work using the latest `copy_v_1`, so we'll use that:

```
? what is in '/documents'?
File(name=/documents/file1.txt, size=1000)


? what is in this folder?
File(name=/Desktop/the yearly budget.txt, size=10000000)
File(name=/Desktop/blue, size=1000)


? copy 'blue' in '/documents'
Done!

? /show

...

                          ┌── quoted(blue,i14)
              ┌────── and(0,1)
              │             └ fw_seq(x8,i14)
proper_q(x8,RSTR,BODY)                           ┌── quoted(/documents,i23)
                   │                 ┌────── and(0,1)
                   │                 │             └ fw_seq(x18,i23)
                   └─ proper_q(x18,RSTR,BODY)
                                          │                 ┌────── pron(x3)
                                          └─ pronoun_q(x3,RSTR,BODY)                     ┌─ _in_p_loc(e17,x8,x18)
                                                                 └─ _copy_v_1(e2,x3,x8,ARG3)

...

? what is in '/documents'?
File(name=/documents/file1.txt, size=1000)
File(name=/documents/blue, size=1000)
```

Just to make sure that the expected parse is, in fact, what worked, `/show` was executed so we could see the successful tree used and validate it.

Because this code will be the same for all predications that deal with scopal arguments, we can simplify it by writing some helpers.

### Simplifying Scopal Argument Predications
To reduce the amount of ceremony required to deal with a scopal argument, we'll add the notion of a "virtual argument" to our predications (this is not a DELPH-IN concept, it is just for this Python tutorial). This is a way of declaring what information is needed from an event and having the system pull it out and pass it as an argument instead of fishing it out directly.  It should save a lot of code when dealing with scopal arguments.

In our example, this is the code we are trying to remove:

```
def locative_copy_v_1_comm(state, e_introduced_binding, x_actor_binding, x_what_binding, h_where):
   
   ...
   
            # Determine which events in the scopal argument will hold
            # the LocativePreposition
            where_events = scopal_events_modifying_individual(x_what_binding.variable.name, h_where)
            found_locative_preposition = False
            if len(where_events) > 0:
                # Normalize the tree, which could return multiple solutions like any call()
                for solution in call(state, h_where, normalize=True):
                    # Get the value for each event and see if it holds a
                    # LocativePreposition
                    for where_event in where_events:
                        e_where_binding = solution.get_binding(where_event)
                        if "LocativePreposition" in e_where_binding.value:
                            # found the information in the event, copy "in" that location
                            found_locative_preposition = True

                            ...
                            
            if not found_locative_preposition:
                # Fail since we don't know what kind of scopal argument this is
                report_error(["formNotUnderstood", "missing", "LocativePreposition"])
```

To declare that a predication should have a virtual argument added, we'll add a `virtual_arguments` parameter to the `Predication` decorator. This will tell the system what information should be found and added as the virtual argument (i.e. one which isn't normally on this ERG predication).  Below is the same `locative_copy_v_1_comm()` function, but now using this new approach. You can see that it adds a new virtual `scopal_argument` that is `EventOption.required`, and then passes everything the system will need to know to fish out the argument:

- `scopal_index=3`: the *index* of the scopal argument -- i.e. the forth argument passed in (but this is 3 since it is a zero-based index) (`h_where`)
- `event_for_arg_index=2`: the index of the argument that holds the instance we are trying to locate using the locative preposition (`x_what_binding`)
- `event_value_pattern=locative_preposition_end_location`: holds a pattern that can be used to find the value required in an event

This is all the information that the above code needed to find and retrieve the locative preposition value. Then, at runtime, if the information is available, it is passed in a new (aka virtual) argument at the end of the predication. This virtual argument is called `where_binding_generator` below. Note that this is a *generator* of values and not a single value since there might be more than one locative preposition found (e.g. "copy 'foo' in "\documents" and in "\root"):

```
@Predication(vocabulary, names=["_copy_v_1"], virtual_args=[(scopal_argument(scopal_index=3, event_for_arg_index=2, event_value_pattern=locative_preposition_end_location), EventOption.required)])
def locative_copy_v_1_comm(state, e_introduced_binding, x_actor_binding, x_what_binding, h_where, where_binding_generator):
    # We only know how to copy things from the
    # computer's perspective
    if x_actor_binding.value.name == "Computer":
        # Only allow copying files and folders
        if isinstance(x_what_binding.value, (File, Folder)):
            # We are guaranteed at least one x_where_binding since
            # this is a required virtual_arg
            for x_where_binding in where_binding_generator:
                if isinstance(x_where_binding.value, Folder):
                    yield state.apply_operations([CopyOperation(None, x_what_binding, x_where_binding)])

                else:
                    report_error(["cantDo", "copy", x_where_binding.variable.name])

        else:
            report_error(["cantDo", "copy", x_what_binding.variable.name])

    else:
        report_error(["dontKnowActor", x_actor_binding.variable.name])
```

The last to describe is the `event_value_pattern` argument. It is set to a constant declared elsewhere in the file:

```
# Constants for creating virtual arguments from scopal arguments
locative_preposition_end_location = {"LocativePreposition": {"Value": {"EndLocation": VariableBinding}}}
```

The virtual argument code needs to be told what value to pull out from the event.  The pattern shown above is a JSON object that "looks" like the part of the event we want to find.  The last value is an actual Python type, and this describes the kind of thing we expect to find. So, the pattern `locative_preposition_end_location` above will cause the system to look for:

```
event["LocativePreposition"]["Value"]["EndLocation"]
```

... and make sure the value there is a `VariableBinding`.

The code below is not important for understanding the semantics of the ERG or DELPH-IN, it is really just to enable the syntactic sugar above.  But here it is for the curious:
```
# Return a virtual argument for a predication from a scopal argument
# This will be a generator since there could be more than one found
def scopal_argument(scopal_index, event_for_arg_index, event_value_pattern):
    # Return the actual argument created from the args passed to the predication
    # at runtime and the information originally passed into the scopal_argument function
    def scopal_argument_generator(args):
        # This is the actual generator that loops through the scopal argument
        def possibly_empty_generator():
            # Get the arguments we'll need from the runtime arguments
            x_what_binding = args[event_for_arg_index + 1]
            h_scopal_arg = args[scopal_index + 1]
            state = args[0]

            # Determine which events in the scopal argument we need
            scopal_events = scopal_events_modifying_individual(x_what_binding.variable.name, h_scopal_arg)
            if len(scopal_events) > 0:
                # Normalize the tree, which could return multiple solutions like any call()
                for solution in call(state, h_scopal_arg, normalize=True):
                    # Get the value for each event and see if it holds
                    # the pattern being searched for
                    for scopal_event in scopal_events:
                        found_binding = solution.get_binding(scopal_event)
                        if found_binding.value is not None:
                            found_value = event_value_from_pattern(found_binding.value, event_value_pattern)
                            if found_value is not None:
                                yield found_value

        # Make sure there is at least one value found
        # Otherwise this predication won't be able to execute
        # so an error should be reported
        generator = at_least_one_generator(possibly_empty_generator())
        if generator is None:
            report_error(["formNotUnderstood", "missing",  next(iter(event_value_pattern))])

        else:
            return generator

    return scopal_argument_generator


# Use the pattern in pattern_dict to find a value in event_dict
# The pattern is a nested set of dicts, where the last value is an
# expected type (which could be object if any value is OK):
#
# pattern example: {"LocativePreposition": {"EndLocation": VariableBinding}}
def event_value_from_pattern(event_dict, pattern_dict):
    # Get the first key from pattern_dict
    key = next(iter(pattern_dict))

    if key in event_dict:
        next_event_level = event_dict[key]
        next_pattern_level = pattern_dict[key]
        if isinstance(next_pattern_level, dict):
            return event_value_from_pattern(next_event_level, next_pattern_level)
        elif isinstance(next_event_level, next_pattern_level):
            return next_event_level

    return None


# Determine which events modify this individual
def scopal_events_modifying_individual(x_individual, h_scopal):
    events = []
    for predication in find_predications_using_variable_ARG1(h_scopal, x_individual):
        if predication.arg_types[0] == "e":
            events.append(predication.args[0])

    return events
```

> Comprehensive source for the completed tutorial is available [here](https://github.com/EricZinda/Perplexity).


Last update: 2023-05-17 by EricZinda [[edit](https://github.com/EricZinda/Perplexity/edit/main/docs/pxHowTo/pxHowTo095LocativePrepositions.md)]{% endraw %}