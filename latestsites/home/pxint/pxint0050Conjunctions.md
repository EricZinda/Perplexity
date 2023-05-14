{% raw %}#### Solving Conjuctions of Predications
There are two ways to group predications together in an MRS: as a "conjunction" (i.e. a logical "and") or by using "scopal arguments". Scopal arguments allow passing *a predication* as an argument to another predication, much like lambda functions do in many programming languages. This is how you built up a tree of predications in a well-formed tree. Now that we have a textual representation and a way to execute it, we can start resolving these more complex structures.

To handle a logical "and" or "conjunction" of predications, we'll perform a depth-first search of the answers from each predication, evaluated in order. This means: take the variables set by the first predication, pass them to the second predication, and collect the successful result. Once you've iterated through all of them, you have the set of things that are true for all of the predications in the conjunction for that world.

For an example such as: `_large_a_1(e,x) and _file_n_of(x)` (to indicate a "large file"):
1. Start with empty variables and call the first predication using our predication contract: `_large_a_1`. 
2. If it succeeds, take the resulting variable assignments and call `_file_n_of` with those assignments. Since there are no more predications, if it succeeds, that result is the first answer.
3. Then "backtrack" by going to step 2 and call `_file_n_of` again to get the next answer. 
4. When `_file_n_of` finally fails, backtrack to step 1 and call `_large_a_1` for its next value and do it all again. 
5. When you have exhausted them all, you have a set of answers (in this case values for `x` and `e`) that represent all the "large files" in that world.

This works because the first predication (`_large_a_1(e,x)`) is called with *unbound variables*, and because of our predication contract, this means it will iterate through all the "large" things in the world, whether they are files, folders, beach balls, or whatever. When it returns, `x` is set to whatever it selected and the next predication (`file_n_of`) will only succeed if the item is a *file*, So, if we get all the way through, we have a "large file".  The "backtracking" behavior allows us to iterate through all the objects in the world to find all the "large files".

We'll implement this logic generally by creating a `Call()` function. It expects our text-based format, either as a single predication or a list of predications, like this:
```
["_large_a_1", "e1", "x1"]
OR
[["_large_a_1", "e1", "x1"], ["_file_n_of", "x1"]]
```

It will use the `CallPredication()` function we defined in the previous section to call the individual predications. 

In the code for `Call()` below, note that there is a new Python construct: `yield from`.  Where `yield` expects an actual object to yield as its argument, `yield from` says "call the function I'm giving you and yield whatever *that function* yields".

```
def Call(vocabulary, state, term):
    # If "term" is an empty list, we have solved all
    # predications in the conjunction, return the final answer.
    # "len()" is a built-in Python function that returns the
    # length of a list
    if len(term) == 0:
        yield state
    else:
        # See if the first thing in the list is actually a list
        # like [["_large_a_1", "e1", "x1"], ["_file_n_of", "x1"]]
        # If so, we have a conjunction
        if isinstance(term[0], list):
            # This is a list of predications, so they should
            # treated as a conjunction.
            # Call each one and pass the state it returns
            # to the next one, recursively
            for nextState in Call(vocabulary, state, term[0]):
                # Note the [1:] syntax which means "return a list
                # of everything but the first item"
                yield from Call(vocabulary, nextState, term[1:])

        else:
            # The first thing in the list was not a list
            # so we assume it is just a term like
            # ["_large_a_1", "e1", "x1"]
            # evaluate it using CallPredication
            yield from CallPredication(vocabulary, state, term)
```

It is worth making sure you understand how this function works since it is the core of our evaluator. 

A scope-resolved MRS is a *tree*, so to solve it, we do a single call to `Call()` and pass the whole tree as `term`. But: this function only evaluates either single predications or conjunctions, what makes it able to solve a tree? The trick is that predications can have other predications as arguments (i.e. "scopal arguments"). This builds a tree and the predications with scopal arguments are responsible for solving the scopal arguments. How this all works is described in the next topic.

To finish this up, let's implement the predications needed to make the example run and run it:

```
@Predication(vocabulary, name="_file_n_of")
def file_n_of(state, x):
    x_value = state.GetVariable(x)
    if x_value is None:
        iterator = state.AllIndividuals()
    else:
        iterator = [x_value]

    for item in iterator:
        if isinstance(item, File):
            new_state = state.SetX(x, item)
            yield new_state


@Predication(vocabulary, name="_large_a_1")
def large_a_1(state, e_introduced, x_target):
    x_target_value = state.GetVariable(x)
    if x_target_value is None:
        iterator = state.AllIndividuals()
    else:
        iterator = [x_target_value]

    for item in iterator:
        # Arbitrarily decide that "large" means a size greater
        # than 1,000,000 
        # remember that "hasattr()" checks if an object has
        # a property
        if hasattr(item, 'size') and item.size > 1000000:
            new_state = state.SetX(x_target, item)
            yield new_state

    
def Example3():
    state = State([Folder(name="Desktop"),
                   Folder(name="Documents"),
                   File(name="file1.txt", size=100),
                   File(name="file2.txt", size=2000000)])
    mrs = [["_large_a_1", "e1", "x1"], ["_file_n_of", "x1"]]
    for item in Call(vocabulary, state, mrs):
        print(item.variables)
        
        
# Prints:
# File(name="file2.txt", size=2000000)
```

Now we have evaluated our first (very small) MRS document. Once we implement scopal arguments in the next topic, we'll be able to handle full well-formed trees.

> Comprehensive source for the completed tutorial is available [here](https://github.com/EricZinda/Perplexity).


Last update: 2023-05-14 by EricZinda [[edit](https://github.com/EricZinda/Perplexity/edit/main/docs/pxint/pxint0050Conjunctions.md)]{% endraw %}