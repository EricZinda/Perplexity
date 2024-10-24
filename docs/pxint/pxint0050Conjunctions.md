#### Solving Conjuctions of Predications
There are two ways to group predications together in an MRS: as a "conjunction" (i.e. a logical "and") or by using ["scopal arguments"](../mrscon/devhowto0010MRS#h-handle-variables-aka-scopal-arguments). Scopal arguments allow passing *a predication* as an argument to another predication, much like lambda functions do in many programming languages. This is how you built up a tree of predications in a [well-formed tree](../mrscon/devhowto0020WellFormedTree). Now that we have a textual representation and a way to execute it, we can start resolving these more complex structures.

To handle a logical "and" or "conjunction" of predications, we'll perform a depth-first search of the tree and call each predication in turn, *if* they succeed. We'll pass the state yielded by one predication to the next one. Once you've iterated through all of them, you have the set of things that are true for all the predications in the conjunction for that world.

For an example such as: `_large_a_1(e,x) and _file_n_of(x)` (to indicate a "large file"):
1. Start with unbound variables and call the first predication using our [predication contract](devhowtoPredicationContract): `_large_a_1`. 
2. If it succeeds, take the resulting variable assignments that were yielded and call `_file_n_of` with those assignments. Since there are no more predications, if it succeeds, that result is the first answer.
3. Then "backtrack" by going to step 2 and call `_file_n_of` again to get the next answer. 
4. When `_file_n_of` finally fails, backtrack to step 1 and call `_large_a_1` for its next value and do it all again. 
5. When you have exhausted them all, you have a set of answers (in this case values for `x` and `e`) that represent all the "large files" in that world.

This works because the first predication (`_large_a_1(e,x)`) is called with *unbound variables*, and because of our [predication contract](devhowtoPredicationContract), this means it will iterate through all the "large" things in the world, whether they are files, folders, beach balls, or whatever. When it returns, `x` is set to whatever it selected and the next predication (`file_n_of`) will only succeed if the item is a *file*, So, if we get all the way through, we have a "large file".  The "backtracking" behavior allows us to iterate through all the objects in the world to find all the "large files".

We'll implement this logic generally by creating a `call()` function. It will take the new `TreePredication` class, either as a single predication or a list of predications, and call the predications using the `call_predication()` function we [defined in the previous section](pxint0040BuildSolver). 


In the code for `call()` below, note that there is a new Python construct: `yield from`.  Where `yield` expects an actual object to yield as its argument, `yield from` says "call the function I'm giving you and yield whatever *that function* yields".

~~~
def call(vocabulary, state, term):
    # If "term" is an empty list, we have solved all
    # predications in the conjunction, return the final answer.
    # "len()" is a built-in Python function that returns the
    # length of a list
    if len(term) == 0:
        yield state
    else:
        # See if the first thing in the list is actually a list
        # If so, we have a conjunction
        if isinstance(term[0], list):
            # This is a list of predications, so they should
            # be treated as a conjunction.
            # call each one and pass the state it returns
            # to the next one, recursively
            for nextState in call(vocabulary, state, term[0]):
                # Note the [1:] syntax which means "return a list
                # of everything but the first item"
                yield from call(vocabulary, nextState, term[1:])

        else:
            # The first thing in the list was not a list
            # so we assume it is just a TreePredication term.
            # Evaluate it using call_predication
            yield from call_predication(vocabulary, state, term)
~~~

It is worth making sure you understand how this function works since it is the core of our evaluator:

When a list is passed to `call`, it is treated as a conjunction (i.e. "and"), and so each predication in the conjunction gets passed to `call` again, one after the other. If one fails, we stop iterating and see if there are other states yielded from the first predication and try again. If they all fail, the function stops searching. That is how "and" gets implemented, they all must succeed for the search to succeed.

When a single predication is passed to `call`, it just gets directly passed on to `call_predication()`.  Once it fails, we stop.

Now, a scope-resolved MRS is a *tree*, so to solve it, we do a single call to `call()` and pass the whole tree as `term`. But: this function only evaluates either single predications or conjunctions, what makes it able to solve a tree? The trick is that predications can have other predications as arguments (i.e. "scopal arguments"). The scopal arguments build the tree.  And: the predications with scopal arguments are themselves responsible for solving the scopal arguments. How scopal arguments do this is [described in the next topic](pxint0060ScopalArguments).

To finish this up, let's implement the last predication needed to make the example run and run it: `file_n_of`. It is an almost exact copy of `_folder_n_of`:
~~~
@Predication(vocabulary, name="_file_n_of")
def _file_n_of(state, x, i):
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
        if isinstance(item, File):
            # state.SetX() returns a *new* state that
            # is a copy of the old one with just that one
            # variable set to a new value
            # Variable bindings are always tuples so we set
            # this one using the tuple syntax: (item, )
            new_state = state.set_x(x, (item, ))
            yield new_state
~~~

Now we can run an example with "large files" in conjunction, by putting `_large_a_1` and `_file_n_of` in a list (indicating conjunction) and calling the `call()` method:

~~~
def Example3():
    state = State([Folder(name="Desktop"),
                   Folder(name="Documents"),
                   File(name="file1.txt", size=100),
                   File(name="file2.txt", size=2000000)])

    tree = [TreePredication(0, "_large_a_1", ["e1", "x1"]),
            TreePredication(1, "_file_n_of", ["x1", "i1"])]

    for item in call(vocabulary, state, tree):
        print(item.variables)
        
# Running Example3 results in:
{'x1': x1=(File(file2.txt, 2000000),)}
~~~

This shows that the only "large file" in the world is "file2.txt".

Now we have evaluated our first (very small) MRS document. Once we implement scopal arguments [in the next topic](pxint0060ScopalArguments), we'll be able to handle full well-formed trees.

> Comprehensive source for the completed tutorial is available [here](https://github.com/EricZinda/Perplexity).