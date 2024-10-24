## Solving an MRS
> It is important to understand [what MRS is](../mrscon/devhowto0010MRS) and what [a well-formed MRS tree is](../mrscon/devhowto0020WellFormedTree) before reading this section. Visit those links first to understand the basic concepts.

A [well-formed MRS tree](../mrscon/devhowto0020WellFormedTree) can be thought of as an *equation* that is `true` or `false` depending on the values of its variables. Recall that predications are of the form: `_table_n_1(x)` or `compound(e,x,x)`. Just like functions in mathematics or programming languages, they have a name and a set of arguments. They are `true` when their arguments are set to values that *are* or *mean* what the predication means. 

So:

- If we set `x = 'a cat'` then `_table_n_1(x)` will be `false`
- If we set `x = 'the brown table'` then `_table_n_1(x)` will be `true`

`_table_n_1(x)` means: "the object in `x` is `a table`". It might *also* be many other things, like `brown` or `large` or `missing`, etc. But as long as it is at least `a table`, `_table_n_1(x)` is `true`.

How `a cat` or `the brown table` are actually *represented* doesn't matter as long as the predication can interpret it. It could be a string or an object of some kind.

A group of multiple predications separated by commas means they are "in conjunction", which means the commas should be treated as `and`. So,`large(x), file(x)` will only be `true` if `x` is set to values that make all the predications `true`. In this example, `x` must be set to something that is `a large file`. Again, `x` could be `a large yellow file` or `a large file of paperwork`, but each predication just tests for some property of `x` and is `true` as long as that property is `true`, regardless of its other properties.

*Solving* a well-formed tree means finding values for the variables that make all the predications `true`.

Here's a simple example. Let's solve `large(x), file(x)` in a world with 3 objects in it:
~~~
a folder
a small file
a large file
~~~
`x` variables in an MRS represent "individuals" or "things in the world". So, we need to find which are the individuals from the world that, when put into `x`, make both the predications in `large(x), file(x)` be `true`. 

While this is trivial to solve by looking at it, once the world contains a million objects we will need a more systematic approach.

## A Backtracking MRS Solver
We can look at solving an MRS as a [constraint satisfaction problem](https://en.wikipedia.org/wiki/Constraint_satisfaction_problem) which is a well-studied class of problems that have a finite set of constraints over variables. In the MRS case, the constraints are the predications:
- `large(x)` constrains `x` to only be those objects that are `large`
- `file(x)` constrains `x` to only be those objects that are a `file`
- `large(x), file(x)` constrains `x` to be a `large file`

One simple approach to solving constraint satisfaction problems (like finding the solutions to an MRS) is to use ["backtracking"](https://en.wikipedia.org/wiki/Backtracking). The simplest backtracking algorithm is to:

- Traverse the predications from the well-formed MRS tree, depth-first
- When an unassigned variable in a predication is encountered: 
  1) Assign it the first item in the world
  2) Mark it as a `backtrack point`
- If a predication is `false`:
  1) "backtrack" to the nearest `backtrack point` and retry with the next item in the world
  2) If there are no more items to retry with, backtrack further to the next `backtrack point` and try again. 

This will try all items in the world, in all variables, until it finds all solutions. Backtracking allows the search space to be pruned to avoid whole sets of assignments that can't possibly work, thus improving the performance vs. a full search of all possibilities.

Let's use the backtracking algorithm to solve a slightly more interesting example, "large file in folder":

[It is important to note that these are not real MRS or well-formed tree examples yet!  That will come soon.]
~~~
formula: large(x), file(x), folder(y), in(x, y)

world individuals:
a folder
a small file
a large file

world facts:
[a large file] is in [a folder]
~~~
The "world individuals" above are the only objects that exist in the world. `x` values in the MRS will hold these as values.

The "world facts" above are facts about the relationships between things in the world that predications such as `in(x, y)` can refer to to see if they are `true`.

As above, it doesn't matter how either of these is actually represented in a program, as long as the predications know how to find and interpret them. We'll be building an example of such a system in the [How-To section](../pxHowTo/pxHowTo010Overview).

To make the backtracking algorithm more explicit, and to make the formula more like real MRS predications, we need to introduce a notion of "variable scope". Variable scope shows where a variable is introduced and which predications can use it. 

We'll represent scope by a made-up function for now: `scope(variable, [predication_list])`. The function states that `variable` can be used by all the predications in `[predication_list]`. And, since `scope()` itself is a predication, more variables can be defined in `predication_list` using another `scope()`. This allows us to represent our formula using scoping, like this:

~~~
formula: scope(x, [large(x), file(x), 
                                      scope(y, [folder(y), in(x, y)])
                  ])
~~~
The formula is formatted to make it easier to see the nesting. You can see that this is just a flat way of representing a tree shaped like this:

~~~
                            ┌── large(x)
                            │ ┌── file(x) 
                ┌────── and(0,1,2)
                │               └── scope(y, predication_list)
scope(x, predication_list)                          │
                                                    └─ and(0,1)
                                                           │ └ in(x, y)
                                                           └ folder(y)
~~~
... where `and(...)` has been used to explicitly show the conjunctions (i.e. `and`s).


The backtracking algorithm does its job by recursively "evaluating" the `scope()` predications:

> Evaluating a `scope()` means:
> - Assign a world value to the scope's variable
> - Evaluate its `predication_list` using that value (see below for how)
> - If the list is `false`, restart the list using the next world value
> - If the list is `true`, the `scope()` predication is `true`
> 
> Evaluating a `predication_list` means:
> - Evaluate the first predication in the list using the current values of all variables in scope
> - If `true`, try the next predication in the list
> - If `false`, the list is `false`
> - If all the predications are `true`, the list is `true`

So, working through the example:

|Action|Formula|
|---|---|
|Start with initial formula |    scope(x, [large(x), file(x), scope(y, [folder(y), in(x, y)])]) |
|set x='a folder' (the first item in the world) |    scope('a folder', [large('a folder'), file('a folder'), scope(y, [folder(y), in('a folder', y)])]) |
|first item in list is `false`|    ... large('a folder')...|
|backtrack: set x='a small file' (the next item in the world) |    scope('a small file', [large('a small file'), file('a small file'), scope(y, [folder(y), in('a small file', y)])]) |
|first item in list is `false`|    ... large('a small file')...|
|backtrack: set x='a large file' |    scope('a large file', [large('a large file'), file('a large file'), scope(y, [folder(y), in('a large file', y)])]) |
|first item in list is `true`| ... large('a large file')...|
|second item in list is `true`| ... file('a large file')...|
|third item in list is `scope()`: set y='a folder' (the first item in the world)|    ...  scope('a folder', [folder('a folder'), in('a large file', 'a folder')])|
|first item in `scope(y, ...)` is `true`|    ... folder('a folder') ...|
|second item in `scope(y, ...)` is `true`|    ... in('a large file', 'a folder')...|
|thus: `scope(y, ...)` is `true` for y='a folder'|    ...  scope('a folder', [folder('a folder'), in('a large file', 'a folder')])|
|thus: `scope(x, ...)` is `true` for x='a large file' and y='a folder'|scope('a large file', [large('a large file'), file('a large file'), scope('a folder', [folder('a folder'), in('a large file', 'a folder')])])|

This example shows how:

- Iteratively assigning values to each variable in a scope and
- Evaluating the predication list within a scope and
- Backtracking when there is a failure

... will eventually find all the solutions to the formula (or prove that there are none). 

It works because we are effectively trying all values in all variables. But, it is better than literally just assigning all values to all variables, one by one, until we find the answer, because backtracking eliminates whole branches in the search space. There are other optimizations that can be done, and we will do more as we go, but the basic approach is straightforward.

At this point, it should be noted that there are other algorithms for solving constraint satisfaction problems. Furthermore, the MRS tree can sometimes be transformed into other forms, such as a predicate logic formula, and turned into a different kind of problem which can be solved using completely different approaches. This tutorial will be using the backtracking algorithm because it is simple, efficient enough for many problems, and has the nice property that it can handle all MRS formulas. It has the downside that it can be very inefficient in some cases. We'll work through some of those and find optimizations for some of the most egregious problems.

But, before we can solve a real well-formed MRS tree, we need to account for more of its features. First up is allowing the solver to represent things operating ["together"](devcon0020MRSSolverSets).
