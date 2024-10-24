{% raw %}
## "Together" and "Separately" in the Solver
If there were multiple large files in folders, the formula we ended the [MRS Solver](https://blog.inductorsoftware.com/Perplexity/home/devcon/devcon0010MRSSolver) section with:

```
formula: large(x), file(x), folder(y), in(x, y)
```

... would find them all as different "solutions". Recall that a "solution" is an assignment of a single value to all variables, such as:

```
solution 1: x=file1, y=folder1
solution 2: x=file2, y=folder2
...
```

So, using that approach, we could look at the formula as representing the phrase: "large files in folders" since it will find multiple if they exist. But, this only works because of how "in" behaves. If `a` and `b` are "in" a folder, `a` is in the folder and `b` is in the folder. 

This isn't true of all verbs, however. The verb "to lift" can distinguish cases that mean very different things.  

For example:

```
students lifted a table
```
...*could* mean: 
1. Two students (together) lifted a table (at the same time)
2. Two students (separately) lifted a (different) table

We need to be able to capture the semantic of the students working together or separately in our solutions. Simply having single values assigned to variables can't do that.

### Handling Sets
To represent individuals operating "together" or "separately" we can make a simple extension to the algorithm: require that variables always contain a *set* of one or more things from the world. Predications can then interpret a set of greater than one element as meaning "together".  A set of one item can mean "separately" or "alone". 

This change allows the solver to represent a solution where Alice and Bob are lifting a table *together* like this: `lift([alice, bob], [table1])`. The fact that the first argument to `lift` is a set of two people means they are working together, which wasn't possible to represent before.

With this change, a `scope()` predication now needs to assign *all possible sets of values* to its variable in order to explore the solution tree and find all the solutions. This can quickly become quite expensive, but there are optimizations we will explore. For now, we'll use the direct approach to keep the algorithm simple.

Let's work through an example of a world where two students are lifting a table:

```
formula: student(x), table(y), lift(x, y)
scoped formula: scope(x, [student(x), scope(y, [table(y), lift(x, y)])])

world individuals:
  alice
  bob
  table1

world facts:
  [alice, bob] lift [table1]
```
To find all solutions, `x` and `y` now must be iteratively assigned all *combinations* of things in the world by their `scope()` predication, but the rest of the algorithm proceeds as before. 

Unlike `in()`, when `lift()` encounters a set of more than one item in either of its arguments, it has to check the world to see if the actors are lifting *together*, or if tables are being lifted *together*.

Summarizing the results in truth table form:

|assignment|formula result|
|---|---|
|x=[alice], y=[alice]| false|
|x=[alice], y=[bob]| false|
|x=[alice], y=[table1]| true|
|x=[alice], y=[alice, bob]| false|
|x=[alice], y=[alice, table1]| false|
|x=[alice], y=[bob, table1]| false|
|x=[alice], y=[alice, bob, table1]| false|
|x=[bob], y=[alice]| false|
|x=[bob], y=[bob]| false|
|x=[bob], y=[table1]| true|
|x=[bob], y=[alice, bob]| false|
|x=[bob], y=[alice, bob, table1]| false|
|x=[alice, bob], y=[alice]| false|
|x=[alice, bob], y=[bob]| false|
|x=[alice, bob], y=[table1]| true|
|...| etc.|

Observe how the variable assignments now contain sets (represented by `[]`), and every combination of world individuals (that is not the empty set) is tried. Not all combinations are shown for all variables because:

- The number of non-empty combinations of world individuals is `(2^n - 1)`: think about representing each individual as a binary bit saying whether the individual is included (1) or not (0). `n` individuals means `n` bits. `n` bits can represent `2^n` numbers. We subtract off the number that has all zeros since we don't want an empty set. In this case, that only means 7 combinations of individuals. 
- But: we also need all combinations of assignments of those individuals to `x` and `y`. That is a ["cartesian product"](https://en.wikipedia.org/wiki/Cartesian_product), which means we'd need to show `(2^n - 1) * (2^n - 1) = 49` assignments in the list. This can quickly become an unmanageable number, but there are some approaches to taming the combinatorics that we'll go through later.

In the new form, the solutions we get back (i.e. the variable assignments that make the formula  `true` in the above table) are shown below, along with their meaning:

|assignment|meaning|
|---|---|
|x=[alice], y=[table1]| Alice lifted a table|
|x=[bob], y=[table1]| Bob lifted a table|
|x=[alice, bob], y=[table1]| Alice and Bob lifted a table together|

Thus, the algorithm still gives us all the assignments of variables that make the formula `true` in the world, but now our formulation can express things operating together or separately.

However, we need something more to allow representing plurals in a phrase, as described in the [next section](https://blog.inductorsoftware.com/Perplexity/home/devcon/devcon0030MRSSolverSolutionGroups).

Last update: 2024-10-23 by Eric Zinda [[edit](https://github.com/EricZinda/Perplexity/edit/main/docs/devcon/devcon0020MRSSolverSets.md)]{% endraw %}