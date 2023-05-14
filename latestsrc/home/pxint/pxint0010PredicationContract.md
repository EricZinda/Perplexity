{% raw %}## The Predication Contract
> It is important to understand [what MRS is](https://blog.inductorsoftware.com/Perplexity/home/mrscon/devhowtoMRS) and what [a well-formed MRS tree is](https://blog.inductorsoftware.com/Perplexity/home/mrscon/devhowto0020WellFormedTree) before reading this section. Visit those links first to understand the basic concepts.


As discussed in [the "Backtracking" conceptual topic](https://blog.inductorsoftware.com/Perplexity/home/devcon/devcon0010MRSSolver), we'll be solving MRS well-formed trees using a backtracking approach. That topic discusses "calling" or "evaluating" predications without discussing exactly *how* this happens. This section will get specific.

As discussed previously, a [well-formed MRS tree](https://blog.inductorsoftware.com/Perplexity/home/mrscon/devhowto0020WellFormedTree) can be thought of as an *equation* that can be solved against a certain state of the world. One approach to solving an MRS is to walk the well-formed tree in depth-first order and iteratively find assignments of variables that make the MRS `true`, using [backtracking](https://blog.inductorsoftware.com/Perplexity/home/devcon/devcon0010MRSSolver) to try alternatives when they exist. This is the approach we'll be using. To solve an MRS tree using the backtracking approach, we need to code the predications to meet a specific contract that our backtracking solver will rely on. This is the "predication contract".

Recall that predications are of the form: `_table_n_1(x)` or `compound(e,x,x)`. Just like functions in mathematics or programming languages, they have a name and a set of arguments. We'll be treating the predications as classic programming language functions that can be "called" or "invoked".

For the purpose of defining the contract, we'll group predications into two types:
- *Regular Predications*: Declare something that must be `true` about their arguments. For example: `_table_n_1(x)` says that `x` must be a "table"
- *Quantifier Predications*: Act like a Regular Predication but also define the scope of a variable `x`. For example: `a_q(x, rstr, body)` declares a variable `x` that can now be used in its arguments. It *also* says that `x` must be an arbitrary, single object (since the quantifier is "a") that is true for the predications in the `rstr` and the `body`

### Idealized Contract
We'll start with an "idealized contract" because it clarifies how the backtracking solver works. It is "idealized" because it has relatively poor performance characteristics for large worlds. We'll tackle those characteristics with our "practical contract" next, but it is important to understand the fundamental approach first.

The contract is designed to "solve" an MRS for the variables defined in it, such as `x1`, `x2`, or `e1`. Our goal is to find all values of the variables that are `True` within a given world (i.e. find the "solutions"). The approach will be to call predications as functions and so we'll define the contract in terms of what these calls must look like. In the contract, the term `bound` means a variable is "set" or "provided", and `unbound` means it doesn't yet have a value:

> A Regular Predication is called with its arguments bound. If the predication's meaning is `true` given those arguments, it returns `True`. Otherwise, it returns `False`.
> 
> A Quantifier Predication is called with its arguments bound *except* the variable it provides scope for (its first argument). 
> 
> - It must then iteratively set its unbound first argument to every possible object in the world and call its other arguments with each binding. 
> - It then returns each solution (i.e. assignment of variables) for which the Quantifier Predication itself is true, given what was returned by its arguments and the quantification it is doing.
> 
> The "solution" to an MRS is the set of all variable assignments that resulted in the entire MRS tree being `true`


A few observations about the contract:
- What the variables *are* -- i.e. how the world is represented in the program -- is not defined in the contract. It doesn't care.
- Quantifier Predications only scope `x` variables. These are the only variables that represent "things in the world" (aka "individuals"), that we are solving for. Event (`e`) variables are handled differently since they are an implementation detail of the MRS that gets used by the predications. They are not relevant here and get described in a later section.
- This "idealized contract" has different requirements for Regular and Quantifier Predications. Regular Predications simply return `True` or `False`. Quantifier Predications return a set of answers consisting of variable assignments, iteratively. 

Let's walk through an example of each to clarify:

A Regular Predication example: If `table_n_1(x)` is called with `x` set to a value that is:
- `a big red table`, it should return `True` (it only verifies that it is a *table*, its other characteristics are ignored) 
- `a persian cat`, it should return `False`

A Quantifier Predication example: When `a_q(x, large_a_1(x), file(x))` is called, `x` will be unbound. It will internally set `x` to every object in the world and then call its arguments, applying the logic of the quantifier itself to the results. Each value of `x` for which that process is `true` should be returned, iteratively. 

So, if the world is:

```
a folder
a small file
a large file
```

... and we are solving:

```
a_q(x, large_a_1(x), file(x))
```

`a_q` would be called by the system with `x` unbound, and it would:

1. Set `x` to `a folder` (the first item in the world).
2. Call its first argument, `large_a_1(x)` using the contract. This will return `False`.
3. Since this attempt failed, try the next value: Set `x` to `a small file`.
4. Call its first argument, `large_a_1(x)` using the contract. This will return `False`.
5. Since this attempt failed, try the next value: Set `x` to `a large file`.
6. Call its first argument, `large_a_1(x)` using the contract. This will return `True`.
7. Since that succeeded, call the second argument `file(x)` using the contract. This will return `True`.
8. Since the quantifier "a" means "a single arbitrary item", the quantifier itself succeeds and it returns the first solution: {`x`=`a large file`}

This approach to solving an MRS works because every `x` variable in an MRS is scoped by a Quantifier Predication. It effectively tries every combination of objects in the world in every `x` variable. This is also why it is "idealized": the performance of this approach quickly becomes impractical.

As mentioned in the ["Representing Together" conceptual topic](https://blog.inductorsoftware.com/Perplexity/home/devcon/devcon0020MRSSolverSets), the values bound to all of the variables in these examples are actually *sets* represented as a `tuple` in Python, but the examples above and below gloss over this to keep things simple. 

### Practical Contract
The performance of the contract can be greatly improved. Let's imagine a world with thousands of files and folders. In this world, a user says:

> A large file is in the folder.


Which results in this as one of the well-formed MRS trees:

```
             ┌────── _folder_n_of(x10,i15) 
             │                             ┌── _large_a_1(e8,x3)
             │                 ┌────── and(0,1)
             │                 │             │
_the_q(x10,RSTR,BODY)          │             └ _file_n_of(x3,i9)
                  └─ _a_q(x3,RSTR,BODY)
                                    └─ _in_p_loc(e2,x3,x10)

```

Using the idealized contract, `x10` would be set to every one of the objects in the system by `the_q`, and, within that, `x3` would again be set to every one of the objects in the system by `_a_q`, resulting in a worst-case performance of `n^2`, where `n` is the number of objects in the system.

One optimization we can perform is to notice that the first thing a quantifier predication does is to iteratively set its scoped variable and call its first argument (`RSTR`)  like this pseudo-code:
```
for item in <everything in the world>:
    if rstr(item) is True:
        ...
```

So the `RSTR` predication of `_the_q` (which is `_folder_n_of` in this case) has to check every single object to see if it is "a folder". Given that any regular predication could end up in the `RSTR` of a quantifier predication, we can instead change the contract to allow regular predications to do the iteration themselves, possibly using indices or knowledge of how the world is represented to do it *much more quickly*, like this:

```
for item in rstr():
    ...
```

The `RSTR` regular predication can now be called with *unbound* arguments, and if so, it is responsible for finding the objects in the world that make it `true`, which it should be able to do much more efficiently.  This change effectively makes the contract the same for all predications at the cost of complicating the logic for regular predications a little. It is worth it for the performance improvement. 

So, the contract we'll use in the rest of the tutorial is the "practical contract":

> Calling any predication with *unbound* variables should return the unbound variables bound to values from the world that, together, make it `true`. Calling it again should return a different set of bindings that also make it `true`. Eventually, the predication will run out of things that can be `true` and should then stop returning bindings (i.e. fail). 
> 
> Calling any predication with *bound* variables should simply return the same values if `True` or fail if not. In other words, it should iterate at most once.


Let's go through our same example with the new contract. The world has these objects:

```
`a folder`
`a small file`
`a large file`
```

A Regular Predication example: 

If `_file_n_of(x)` is called with `x` bound to:
- `a folder`: it "fails" by not returning a solution
- `a small file`: it "succeeds" by returning a solution with the variable bound as it already is: {`x`=`a small file`}

If `_file_n_of(x)` is called with an unbound `x`, it:
1. Sets `x` to the first "file" in the world using whatever algorithm is most efficient, finding: `a small file` and returns {`x` = `a small file`}
2. Sets `x` to the next "file" in the world using whatever algorithm is most efficient, finding: `a large file` and returns {`x` = `a large file`}
3. Runs out of files and thus fails, meaning: stop returning solutions

The Quantifier Predication example is the same as before since we have simply started applying its contract to *all* predications now.

To help with performance of the system, the "practical contract" is the contract we will use for each predication we want the system to understand. 

### Final Performance Thoughts
Even with this optimization, the example MRS for something like "a large file is in the folder" will need to check each "large file" in the system to see if it is in "the" folder (where "the folder" might mean "current folder"), which could still be a lot of iterations. There are further optimizations that can be done by the solver and many will depend on the particular world you execute against. Optimizing performance of a system like this is an ongoing task.

There are other ways to solve an MRS for the variables that make it true. For example, some MRS's can be converted to classic logic statements "There exists an x such that..." and various solvers can be used to solve for the variables in it: TODO: List references here. In addition, there are many uses for MRS that don't involve solving for the variables at all TODO: List references here. However, the [backtracking approach](https://blog.inductorsoftware.com/Perplexity/home/devcon/devcon0010MRSSolver) is relatively straightforward and can be used for constrained worlds. It  allows us to explain the various aspects of DELPH-IN without getting too deep in complicated mathematics or logic.

### Conclusion
We've talked through the contract required on functions that implement a predication, but aren't yet ready to implement one. First, we need to describe a key object used in the implementation: [the `State` object](https://blog.inductorsoftware.com/Perplexity/home/pxint/pxint0020PythonBasics).

> Comprehensive source for the completed tutorial is available [here](https://github.com/EricZinda/Perplexity).


Last update: 2023-05-14 by EricZinda [[edit](https://github.com/EricZinda/Perplexity/edit/main/docs/pxint/pxint0010PredicationContract.md)]{% endraw %}