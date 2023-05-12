As described in the conceptual overview, Perplexity uses [backtracking]() to find the solutions to a well-formed MRS Tree.

### Predications
Every predication in an MRS is implemented by building a Python [generator function]() 

The predication for "file" (as in "a file is large") in the ERG is:
~~~
_file_n_of(x3,i8)
~~~
To implement this in the Perplexity Python library, 

~~~
def file_n_of(state, x_binding, i_binding):

...
~~~

`state` is an object that represents the current state of this world when the predication is called. It holds the current value of all the MRS variables at this point in the solver backtracking process.  Because of backtracking, the same predication can be called many times with different states as the solver attempts to find a solution to the MRS. 

`x_binding` and `i_binding` hold all the information about the variables that `_file_n_of` has. All of this information can be obtained directly from the `state` object as well, but the engine conveniently pulls them out and passes them as arguments to cut down on boilerplate code that the developer needs to write. 

Recall that the job of a predication is to "be true" when its arguments "are set to values that are (or mean) what the predication means".  So, `file_n_of` should be `true` if `x_binding` and `i_binding` have values that mean "file" in the world it is implementing.

Because Perplexity Python predications are generators, `true` is indicated by yielding a `state` object. `false` is indicating by returning without yielding anything.

Here's a simple example. We'll keep it simple by saying this program will only have 1 file in it, called `file1.txt`:
~~~
def file_n_of(state, x_binding, i_binding):
    if x_binding.value is not None and x_binding.value[0] == "file1.txt":
        yield state
~~~
[i_binding is ignored, describe this]

Bindings have a `value` property that returns the current variable's value, which is always a list. So this function retrieves the first item in the list (there will always be at least one if the variable has a value) and checks to see if it is the one file we have in our world. If so, it `yields` the state object it was passed. Nothing changed in the `state` object -- we just inspected it -- so it can just be yielded, as is. The solver will sometimes call predications with values set like this.

Sometimes, especially for predications early in the tree order, the engine will be looking for the function to provide a list of all `file_n` objects as opposed to checking if an object is a file. It indicates this by leaving one or more variables "unbound", which means: `binding.value is None`.  This indicates to the function that it should `yield` all the things in the world that are a `file`, like this:

~~~
def file_n_of(state, x_binding, i_binding):
    if x_binding.value is None:
        yield state.set_x("file1.txt", VariableValueType.set)
    elif x_binding.value[0] == "file1.txt":
        yield state
~~~
In this case we ....
Since our world only has one file in it, we've just hard-coded it here.

## Combinatorial Variables
Sets of files are still files. So, it needs all combinations.

Recall from [the section]() that Perplexity represents items operating together as a set. Because users of the system may ask questions like "Are file1.txt and file2.txt 20 mb?" (meaning are they 20mb *together*), predications need to return *all combinations* of things that make them true.

Let's add 2 more files to our example: `file2.txt` and `file3.txt`

~~~
blah blah
~~~
This pattern happens a lot...so the function can say "all combinations of this list are files", like this:
~~~
blah blah
~~~

Because a variable can be a set or combinatorial, we also need to be prepared to be asked if a combinatorial variable is a `file_n`, the code can get complicated quickly. So we have a helper:

~~~
def file_n_of(state, x_binding, i_binding):
    def bound_variable(value):
        return isinstance(value, File)

    def unbound_variable():
        for item in state.all_individuals():
            if bound_variable(item):
                yield item

    yield from combinatorial_style_predication_1(state, x_binding, bound_variable, unbound_variable)
~~~

## Adding Predications to the Vocabulary
~~~
@Predication(vocabulary, names=["_file_n_of"])
def file_n_of(state, x_binding, i_binding):
    def bound_variable(value):
        return isinstance(value, File)

    def unbound_variable():
        for item in state.all_individuals():
            if bound_variable(item):
                yield item

    yield from combinatorial_style_predication_1(state, x_binding, bound_variable, unbound_variable)
~~~

## Implementing large_a()
todo