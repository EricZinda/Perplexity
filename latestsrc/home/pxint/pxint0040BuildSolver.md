{% raw %}## Converting MRS Text to Python Function Calls
Now it is time to start working through the code that *calls* the [Predication Contract](https://blog.inductorsoftware.com/Perplexity/home/pxint/pxint0010PredicationContract): the solver.  The algorithm we'll use was described in the ["Backtracking" conceptual topic](https://blog.inductorsoftware.com/Perplexity/home/devcon/devcon0010MRSSolver).

To be able to solve an MRS, we first need a way to convert from the MRS predicate names to actual Python function calls. This section describes how.

We'll use a simple Python representation that allows easy conversion from a raw MRS document: each predication will be represented by a Python class called `TreePredication` that just records the basic information about the predication:

```
class TreePredication(object):
    def __init__(self, index, name, args):
        self.index = index
        self.name = name
        self.args = args
```
`index` is a number representing the order that the predication is called when solving the MRS using a depth-first search. All the rest of the arguments are pulled directly from the MRS formalism.

To convert this representation into a Python function and call it, we need a mapping from the string predication name (e.g. `"_folder_n_of"`) to the function and module that implements the logic for it. 

We'll start by building a `Vocabulary` class that will store all of the mappings. You add a mapping with `add_predication()` and find a mapping with `predication()`. Note that both the name and the arguments of a predicate that have to match to get a proper mapping:

```
class Vocabulary(object):
    def __init__(self):
        self.name_function_map = {}

    def get_signature(self, name, args):
        return f"{name}({','.join(args)})"

    def add_predication(self, name, args, module, function):
        signature = self.get_signature(name, arg_types_from_names(args))
        self.name_function_map[signature] = (module, function)

    def predication(self, tree_predication):
        signature = self.get_signature(tree_predication.name, arg_types_from_names(tree_predication.args))
        return self.name_function_map.get(signature, None)
```

Then we need to find a way to populate the mappings. We'll do this using a Python feature called "decorators". It isn't important to understand *how* it works (but if you want to: [read this section](https://blog.inductorsoftware.com/Perplexity/home/pxint/pxint03000PythonDecorators)). For our purposes, just understand that by writing the code below:

```
def arg_types_from_names(args):
    type_list = []
    for arg_name in args:
        # Allow single character arguments like "x" and "e"
        # OR the format: "x_actor", "xActor", etc
        arg_type = arg_name[0]
        if arg_type not in ["u", "i", "p", "e", "x", "h", "c"]:
            raise Exception(
                f"unknown argument type of {arg_type}'")

        type_list.append(arg_type)

    return type_list


# Decorator that adds maps a DELPH-IN predicate to a Python function
def Predication(vocabulary, name=None):

    def arg_types_from_function(function):
        arg_spec = inspect.getfullargspec(function)

        # Skip the first arg since it should always be "state"
        arg_list = arg_types_from_names(arg_spec.args[1:])

        return arg_list

    def predication_decorator(function_to_decorate):
        arg_list = arg_types_from_function(function_to_decorate)

        vocabulary.add_predication(name,
                                   arg_list,
                                   function_to_decorate.__module__,
                                   function_to_decorate.__name__)

        return function_to_decorate

    return predication_decorator
```

We can now write code like this:

```
# You can create global variables in Python
# by just setting their values outside the scope
# of any function, like this:
vocabulary = Vocabulary()

@Predication(vocabulary, name="_folder_n_of")
def folder_n_of(state, x_target, i_ignored):
    # ... implementation of folder_n_of goes here ...
```

The `@Predication(...)` "decoration" above the function runs code at file load time that sticks the Python function (i.e. `def folder_n_of(...)`) and the predication name (i.e. `_folder_n_of`) into the global instance of the `Vocabulary` class it is passed. 

The global `vocabulary` instance will record the mapping between all the functions decorated with `@Predication(vocabulary, name=...)` and the predications they are implementing. With that, we can now build a `call_predication()` function that uses `vocabulary` to map the name of the predicate, plus the list of arguments, to an actual Python function and call it:

```
# Takes a TreePredication object, maps it to a Python function and calls it
def call_predication(vocabulary, state, predication):
    # Look up the actual Python module and
    # function name given a string like "folder_n_of".
    # "vocabulary.Predication" returns a two-item list,
    # where item[0] is the module and item[1] is the function
    module_function = vocabulary.predication(predication)

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
    predication_args = predication.args
    function_args = [state] + predication_args

    # You call a function "pointer" and pass it arguments
    # that are a list by using "function(*function_args)"
    # So: this is actually calling our function (which
    # returns an iterator and thus we can iterate over it)
    for next_state in function(*function_args):
        yield next_state
```

Now we can write an example and run it:

```
# List folders using call_predication
def Example2():
    state = State([Folder(name="Desktop"),
                   Folder(name="Documents"),
                   File(name="file1.txt"),
                   File(name="file2.txt")])

    for item in call_predication(vocabulary,
                                 state,
                                 TreePredication(0, "_folder_n_of", ["x1", "i1"])):
        print(item.variables)
        
# calling Example2() prints:
{'x1': x1=(Folder(Desktop),)}
{'x1': x1=(Folder(Documents),)}
```

`Example2` calls `call_predication()` with the `vocabulary` object we've built and populated using the `Predication` decorator along with a `State` object.  `call_predication` then does the mapping of the predication name `_folder_n_of` to the actual Python function we've written, and performs the "contract" on it.  I.e. calls it with the specified arguments and expects that it will yield values that are true.

The reason it prints out the two folders in our world is that we left all the arguments to `_folder_n_of` unbound. The contract says that, in that case, it should yield all the things in the world that "are a folder", thus the behavior.

With this in place, we can tackle more complicated groups of predications such as conjunctions in the [next section](https://blog.inductorsoftware.com/Perplexity/home/pxint/pxint0050Conjunctions).

> Comprehensive source for the completed tutorial is available [here](https://github.com/EricZinda/Perplexity/tree/main/samples/hello_world)

Last update: 2024-10-28 by Eric Zinda [[edit](https://github.com/EricZinda/Perplexity/edit/main/docs/pxint/pxint0040BuildSolver.md)]{% endraw %}