{% raw %}## Implementing a Predication
With that [Python background and overview of the `State` object](https://blog.inductorsoftware.com/Perplexity/home/pxint/pxint0020PythonBasics), we can now implement the [predication contract](https://blog.inductorsoftware.com/Perplexity/home/pxint/pxint0010PredicationContract) for a predication to see how it all works. Let's implement the `_folder_n_of` predication in Python.  

We will be passing an instance of the `State` object as the first argument to every predication so that it can access its arguments *and* the world state. The variables will be passed in as strings like `"x1"` or `"e12"`. To get their values, the code will look them up in the `State` object as shown below:
```
def folder_n_of(state, x):
    x_value = state.get_binding(x).value
    if x_value is None:
        # Variable is unbound:
        # iterate over all individuals in the world
        # using the iterator returned by state.AllIndividuals()
        iterator = state.all_individuals()
    else:
        # Variable is bound: create an iterator that will iterate
        # over just that one by creating a list and adding it as
        # the only element
        # Remember that we are ignoring the fact that bindings are tuples
        # in these examples so we assume there is only one value, and
        # just retrieve it
        iterator = [x_value[0]]

    # By converting both cases to an iterator, the code that
    # checks if x is "a folder" can be shared
    for item in iterator:
        # "isinstance" is a built-in function in Python that
        # checks if a variable is an
        # instance of the specified class
        if isinstance(item, Folder):
            # state.SetX() returns a *new* state that
            # is a copy of the old one with just that one
            # variable set to a new value
            # Variable bindings are always tuples so we set
            # this one using the tuple syntax: (item, )
            new_state = state.set_x(x, (item, ))
            yield new_state
```
First notice that we are not really taking advantage of our ["practical predication contract"](https://blog.inductorsoftware.com/Perplexity/home/pxint/pxint0010PredicationContract) in this code: we are literally just iterating through every object in the system. We can fix that later, but for the moment the examples are so small that it won't really matter.

Further on in the code, notice that the `folder_n_of` `yields` the new instance of the state object returned from setting `x` to a value.  This behavior (enforced by the`State` object) will allow our solver to pass around the same state object to a predication multiple times and get fresh values bound to the variables. Since we always make copies when setting a value, the solver can rely on a particular `State` object not being changed, even after it has been passed to a predication.

Now we can write a simple test to call our first predication:
```
def Example1():
    state = State([Folder(name="Desktop"),
                   Folder(name="Documents"),
                   File(name="file1.txt"),
                   File(name="file2.txt")])

    for item in folder_n_of(state, "x1"):
        print(item.variables)

    print("\nThe original `state` object is not changed:")
    print(state.variables)

# calling Example1() prints:
{'x1': x1=(Folder(Desktop),)}
{'x1': x1=(Folder(Documents),)}

The original `state` object is not changed:
{}
```

Again, it is important to note that the initial `state` variable will not actually be changed at the end of the `Example1()` function. In order to print out the folders that were found by the predication, we need to print the value of `x1` in the state *returned from the predication*. This is key to allowing us to call the same predication multiple times with the same `State` object to get different answers.

Now we have one predication that implements the predication contract: it will iteratively return all the "folders" in the world when called with an unbound variable as we did here. This is the basic pattern we'll use for all predications from here on out. 

Implementing an adjective works the same way, let's implement `_large_a_1` which is the predication for the adjective "large". We'll need to have a way to represent file sizes to do this first. We'll add an optional size to our `File` object:

```
class File:
    def __init__(self, name, size=0):
        self.name = name
        self.size = size

    def __repr__(self):
        return f"File({self.name}, {self.size})"
```

We can almost use an exact copy of our `_folder_n_of` code for `_large_a_1` because they both do the same thing: yield a value if they are true, and they are both just checking for a single thing on an object (or yielding all objects that "are" that thing). For "large", we'll arbitrarily decide that > 1000 bytes is "large", and that only files can be large:

```
@Predication(vocabulary, name="_large_a_1")
def large_a_1(state, e, x):
    x_value = state.get_binding(x).value
    if x_value is None:
        # Variable is unbound:
        # iterate over all individuals in the world
        # using the iterator returned by state.AllIndividuals()
        iterator = state.all_individuals()
    else:
        # Variable is bound: create an iterator that will iterate
        # over just that one by creating a list and adding it as
        # the only element
        # Remember that we are ignoring the fact that bindings are tuples
        # in these examples so we assume there is only one value, and
        # just retrieve it
        iterator = [x_value[0]]

    # By converting both cases to an iterator, the code that
    # checks if x is "a folder" can be shared
    for item in iterator:
        # "isinstance" is a built-in function in Python that
        # checks if a variable is an
        # instance of the specified class
        if isinstance(item, File) and item.size > 1000:
            # state.SetX() returns a *new* state that
            # is a copy of the old one with just that one
            # variable set to a new value
            # Variable bindings are always tuples so we set
            # this one using the tuple syntax: (item, )
            new_state = state.set_x(x, (item, ))
            yield new_state
```
Note that we are ignoring the `e` event variable. That only comes into play when other predications want to modify the behavior of "large" like "very large". We can safely ignore it for now.

Now we can run the same example that we used for folders, but call `large_a_1` instead:

```
def Example1a():
    state = State([Folder(name="Desktop"),
                   Folder(name="Documents"),
                   File(name="file1.txt", size=1000),
                   File(name="file2.txt", size=2000)])

    for item in large_a_1(state, "e1", "x1"):
        print(item.variables)
        
# Running Example1a results in:
{'x1': x1=(File(file2.txt, 2000),)}
```

Since the arguments to the predication are again unbound, this shows that the only large files in the world are "file2.txt".

With two predications implemented, We can start calling more than one predication and eventually deal with a whole MRS resolved tree. But first we need to write the code that actually calls the predications by building [the solver](https://blog.inductorsoftware.com/Perplexity/home/pxint/pxint0040BuildSolver).

> Comprehensive source for the completed tutorial is available [here](https://github.com/EricZinda/Perplexity/tree/main/samples/hello_world)

Last update: 2024-10-25 by Eric Zinda [[edit](https://github.com/EricZinda/Perplexity/edit/main/docs/pxint/pxint0030ImplementPredication.md)]{% endraw %}