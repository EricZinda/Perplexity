{% raw %}## Implementing a Predication
With that [Python background and overview of the `State` object](), we can now implement the [predication contract](https://blog.inductorsoftware.com/Perplexity/home/pxint/pxint0010PredicationContract) for a predication to see how it all works. Let's implement the `_folder_n_of` predication in Python.  

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
First notice that we are not really taking advantage of our "practical predication contract" in this code: we are literally just iterating through every object in the system. We can fix that later, but for the moment the examples are so small that it won't really matter.

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

Since we are going to start calling more than one predication and eventually deal with a whole MRS resolved tree, we'll need a way to convert the MRS text representation into a set of Python function calls. That way, we won't have to manually convert them to Python like the above example. The next section describes how to do that.

> Comprehensive source for the completed tutorial is available [here](https://github.com/EricZinda/Perplexity).

Last update: 2024-10-18 by Eric Zinda [[edit](https://github.com/EricZinda/Perplexity/edit/main/docs/pxint/pxint0030ImplementPredication.md)]{% endraw %}