{% raw %}## Converting MRS Text to Python Function Calls
Now it is time to start working through the code that *calls* the [Predication Contract](https://blog.inductorsoftware.com/Perplexity/home/pxint/pxint0010PredicationContract): the solver.  The algorithm we'll use was describe in the ["Backtracking" conceptual topic](https://blog.inductorsoftware.com/Perplexity/home/devcon/devcon0010MRSSolver).

To be able to solve an MRS we first need a way to convert from the MRS text representation to actual Python function calls. This section describes how.

We'll use a simple Python representation that allows easy conversion from a raw MRS document: each predication will be represented by a Python class called `TreePredication` that just records the basic information about the predication:

```
class TreePredication(object):
    def __init__(self, index, name, args, arg_names=None):
        self.index = index
        self.name = name
        self.args = args
        self.arg_names = arg_names
```
`index` is a number representing the order in when the predication is called when solving the MRS, all the rest of the arguments are pulled directly from the MRS format.

To convert this representation into a Python function and call it, we need a mapping from the string predication name (e.g. `"_folder_n_of"`) to the function and module where the function lives. We'll do this using a Python feature called "decorators". It isn't important to understand *how* it works (but if you want to: [read this section](https://blog.inductorsoftware.com/Perplexity/home/pxint/pxint03000PythonDecorators)). For our purposes, just understand that by writing two small Python classes we can now write code like this:
```
# You can create global variables in Python
# by just setting their values outside the scope
# of any function, like this:
vocabulary = Vocabulary()

@Predication(vocabulary, name="_folder_n_of")
def folder_n_of(state, x_target):
    # ... implementation of folder_n_of goes here ...
```

The `@Predication(...)` "decoration" above the function runs code that sticks the Python function (i.e. `def folder_n_of(...)`) and the predication name (i.e. `_folder_n_of`) into the global instance of the `Vocabulary` class it is given. 

Note that the function name can be arbitrarily different than the predication name. In this case, we've removed the leading "_", but we could have done something more radical, like this:

```
vocabulary = Vocabulary()

@Predication(vocabulary, name="_folder_n_of")
def my_folder_predication(state, x_target):
    # ... implementation of folder_n_of goes here ...
```

Either way, the global `vocabulary` instance will record the mapping between all of the functions decorated with `@Predication(vocabulary, name=...)` and the predication they are implementing. With that, we can now build a `CallPredication()` function that uses `vocabulary` to map the string name of the predicate, plus the list of arguments, to an actual Python function and execute the contract on it:

```
# The format we're using is:
# ["folder_n_of", "x1"]
#   The first item is the predication name
#   The rest of the items are the arguments
def CallPredication(vocabulary, state, predication):
    # The [0] syntax returns the first item in a list
    predication_name = predication.name

    # The [1:] syntax returns a new list that starts from
    # the first item and goes until the end of the list
    predication_args = predication.args

    # Look up the actual Python module and
    # function name given a string like "folder_n_of".
    # "vocabulary.Predication" returns a two-item list,
    # where item[0] is the module and item[1] is the function
    module_function = vocabulary.Predication(predication_name)

    # sys.modules[] is a built-in Python list that allows you
    # to access actual Python Modules given a string name
    module = sys.modules[module_function[0]]

    # Functions are modeled as properties of modules in Python
    # and getattr() allows you to retrieve a property.
    # So: this is how we get the "function pointer" to the
    # predication function we wrote in Python
    function = getattr(module, module_function[1])

    # [list] + [list] will return a new, combined list
    # in Python. This is how we add the state object
    # onto the front of the argument list
    function_args = [state] + predication_args

    # You call a function "pointer" and pass it arguments
    # that are a list by using "function(*function_args)"
    # So: this is actually calling our function (which
    # returns an iterator and thus we can iterate over it)
    for next_state in function(*function_args):
        yield next_state

```

TODO: Update example to include code running

With this in place, we can tackle more complicated groups of predications such as conjunctions in the [next section](https://blog.inductorsoftware.com/Perplexity/home/pxint/pxint0050Conjunctions).

> Comprehensive source for the completed tutorial is available [here](https://github.com/EricZinda/Perplexity).

Last update: 2023-05-14 by EricZinda [[edit](https://github.com/EricZinda/Perplexity/edit/main/docs/pxint/pxint0040BuildSolver.md)]{% endraw %}