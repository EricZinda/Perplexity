## Predications with Multiple X Arguments
Logic gets more complicated when there is more than one `x` type argument because there are many cases to handle. The predication for "in" from "a file is in a folder" is:

~~~
_in_p_loc(e1,x1,x2)
~~~
Ignoring the event argument `e2` for the moment, there are two `x` arguments. The predicate checks whether `x1` is "in" `x2` (whatever that means in the application). Because of combinatorial values (described in [the previous topic]()), if the predication is called with two combinatorial arguments that have two values each, like this:

~~~
_in_p_loc(e1,[file1, file2],[folder1, folder2])
~~~

It will need to check all combinations of the first argument with the second, and yield any that are true, like this:

~~~
check: [file1] in [folder1]?
check: [file1] in [folder2]?
check: [file2] in [folder1]?
check: [file2] in [folder2]?
check: [file1, file2] in [folder1]?
check: [file1, file2] in [folder2]?
check: [file1, file2] in [folder1, folder2]?
~~~
We can reduce the combinations that need to be checked by remembering that, when a variable has a set of more than one item, it means "together".  So, "[file1, file2] in [folder1]?" means "are file1 and file2 in folder1 *together*?", For files, at least, saying two files are in a folder "together" is no different than saying they are in a folder "separately". If `file1` is in `folder1` and `file2` is in `folder2`, then they are both in there separately *and* together. Note that the meaning of "in" in this case also doesn't *exclude* someone saying "together" or "separately". It is perfectly fine to say "are file1 and file2 in folder2 together", it just doesn't add anything to the meaning.

This observation allows us to simplify the number of checks down to this:

~~~
check: [file1] in [folder1]?
check: [file1] in [folder2]?
check: [file2] in [folder1]?
check: [file2] in [folder2]?
~~~

If those are all true, then these must be too (without having to check):

~~~
check: [file1, file2] in [folder1]?
check: [file1, file2] in [folder2]?
check: [file1, file2] in [folder1, folder2]?
~~~

This observation can greatly reduce the number of checks needed. If there are 10 files in `x1`, checking all combinations for even one folder would take `n^10 - 1 = 1023` checks! If we only check them individually, it only takes 10.

It should be noted that, even though we can avoid the checks for many sets, in theory we still have to yield all the possible combinations. In the next topic we'll walk through how to avoid this for many cases as well.

The logic for checking if variables have combinatorial values, doing the optimization above, and yielding the right values can be long and repetative. So, the library has a function that performs the right logic and only requires the caller to implement the `check()` function, like this:

~~~
@Predication(vocabulary, names=["_in_p_loc"])
def in_p_loc(state, e_introduced_binding, x_actor_binding, x_location_binding):
    def check_item_in_item(item1, item2):
        return is_item_in_item(item1, item2)
    
    ...

    yield from in_style_predication(state, x_actor_binding, x_location_binding, check_item_in_item, ...)
~~~

[The example excludes some arguments that will be described next and uses a made up function `is_item_in_item(item1, item2)` to do the checking since its logic is application specific.]

The function is called `in_style_predication()` because it uses the behavior of "in" as a template.  Any predication that is associative like "in" can use this same helper to implement the logic efficiently.

### Unbound Arguments
As discussed in the [previous section](), arguments to a predication aren't always set (i.e. *bound*) as in the above example. When they are missing, the predication needs to yield all possible values for them that make the predication `true`. This allows predications to use more optimal logic for finding answers that simply trying every possible combination. 

To support unbound arguments, `in_style_predication()` has two additional functions it supports: one for the first argument being unbound and one for the second. There is a final argument that is rarely used for when both are unbound. If it isn't set, the system reports the error `beMoreSpecific` since the user said something that is really broad like "what is in anything?".

Presumably the system we are building would have an efficient way to return things in something else (or vice versa) so the example below uses fake functions that represent this:

~~~
@Predication(vocabulary, names=["_in_p_loc"])
def in_p_loc(state, e_introduced_binding, x_actor_binding, x_location_binding):
    def check_item_in_item(item1, item2):
        return is_item_in_item(item1, item2)
    
    def all_item1_in_item2(item2):
        yield from all_contained_in(item2)

    def all_item2_containing_item1(item1):
        yield from all_containing(item1)

    yield from in_style_predication(state, x_actor_binding, x_location_binding, check_item_in_item, all_item1_in_item2, all_item2_containing_item1)
~~~

As before, `in_style_predication()` does all the work to make sure that the two new functions are only passed single values even if the incoming values are combinatorial.