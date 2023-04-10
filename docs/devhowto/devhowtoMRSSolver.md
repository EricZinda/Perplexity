> It is important to understand [what MRS is](devhowtoMRS) and what [a well-formed MRS tree is](devhowtoWellFormedTree) before reading this section. Visit those links first to understand the basic concepts.

A [well-formed MRS tree](devhowtoWellFormedTree) can be thought of as an *equation* that can be solved against the current state of the world. Recall that predications are of the form: `_table_n_1(x)` or `compound(e,x,x)`. Just like functions in mathematics or programming languages, they have a name and a set of arguments. They are `true` when their arguments are set to values that *are* or *mean* what the predication means. So if we set `x = 'a cat'`, `_table_n_1(x)` will be `false`. If we set it to `x = 'the brown table'`, it will be `true`. How `a cat` or `the brown table` are actually represented doesn't matter as long as the predication can interpret it. It could be a string or an object of some kind.

A group of multiple predications, such as `large(x), file(x)` will only be `true` if `x` is set to values that make all the predications `true`. In this example, `x` must be set to something that is `a large file`.

So, solving a well-formed tree is a matter of finding values for the variables that make all the predications `true`.

Here's a simple example. Let's solve `large(x), file(x)` in a world with 3 objects in it:
~~~
a folder
a small file
a large file
~~~
`x` variables in an MRS represent "individuals" or "things in the world". So, we need to find the values of `x` that make both the predications in `large(x), file(x)` be `true`. 

While this is trivial to solve by looking at it, once the world contains a million objects, we need a systematic approach.

## Simple MRS Solver Algorithm
[todo: add theoretical background here]
A simple approach to solving a simple list of predications like the above example is to try all the items in the world, in every variable, backtracking when one doesn't work.

Let's use a slightly more interesting example, "large file in folder":

~~~
formula: large(x), file(x), folder(y), in(x, y)

world:
a folder
a small file
a large file
[a large file] is in [a folder]
~~~
[It is important to note that these are not real MRS or well-formed tree examples yet!  We are building up to that.]

To make the simple algorithm work we need to introduce a notion of "variable scope" to the formula. Variable scope shows where a variable is introduced and which predications can use it. 

Scope is represented by a function: `scope(variable, predication_list)`. The function states that `variable` can be used by all the predications in `predication_list`. And, since `scope()` itself is a predication, more variables can be defined in `predication_list`. This allows us to represent our formula using scoping, like this:

~~~
formula: scope(x, [large(x), file(x), 
                                      scope(y, [folder(y), in(x, y)])
                  ])
~~~
The formula is formatted to make it easier to see the nesting.

The basic algorithm is to recursively evaluate the `scope()` predications:

> Evaluating a `scope()` means:
> - Assign a world value to the scope's variable
> - Evaluate its `predication_list` using that value (see below for how)
> - If the list is `false`, try the next world value
> - If `true`, the `scope()` predication is `true`
> 
> Evaluating a `predication_list` means:
> - Evaluate the first predication in the list using the current values of all variables in scope
> - If `true`, try the next predication in the list
> - If `false`, the list is `false`
> - If all the predications are `true`, the list is `true`

So, working through the example:

|action|formula|
|---|---|
|Initial formula |    scope(x, [large(x), file(x), scope(y, [folder(y), in(x, y)])]) |
|set x='a folder' |    scope('a folder', [large('a folder'), file('a folder'), scope(y, [folder(y), in('a folder', y)])]) |
|first item in list is `false`|    ... large('a folder')...|
|backtrack: set x='a small file' |    scope('a small file', [large('a small file'), file('a small file'), scope(y, [folder(y), in('a small file', y)])]) |
|first item in list is `false`|    ... large('a small file')...|
|backtrack: set x='a large file' |    scope('a large file', [large('a large file'), file('a large file'), scope(y, [folder(y), in('a large file', y)])]) |
|first item in list is `true`|    ... large('a large file')...|
|second item in list is `true`|    ... file('a large file')...|
|third item in list is `scope()`, set y='a folder'|    ...  scope('a folder', [folder('a folder'), in('a large file', 'a folder')])|
|first item in `scope(y, ...) is `true`|    ... folder('a folder')...|
|second item in `scope(y, ...) is `true`|    ... in('a large file', 'a folder')...|
|thus: `scope(y, ...)` is `true` for y='a folder'|    ...  scope('a folder', [folder('a folder'), in('a large file', 'a folder')])|
|thus: `scope(x, ...)` is `true` for x='a large file' and y='a folder'|scope('a large file', [large('a large file'), file('a large file'), scope('a folder', [folder('a folder'), in('a large file', 'a folder')])])|

This example shows how iteratively assigning values to each variable in a scope,  recursively evaluating the predication lists within a scope, backtracking when there is a failure, will eventually find all the solutions to the formula (or prove that there are none). 

It works because we are effectively trying all values in all variables. It is better than literally just assigning all values to all variables, one by one, until we find the answer because backtracking eliminates whole branches in the search space. There are other optimizations that can be done, and we will do more as we go.

Before we can solve a real well-formed MRS tree, we need to account for more of the features that it has.

## Add Plurals To the Solver
If there were multiple large files in folders in the above example, the current approach would find them all as different solutions. So, using that approach, we could look at the formula as representing "large files in folders" since it will find multiple if they exist. But this only works because of how "in" behaves. If `a` and `b` are "in" a folder, `a` is in the folder and `b` is in the folder. There is no sense of them being in the folder "together" that needs to be represented.

This isn't true of all verbs, however. The verb "to lift" can distinguish the cases and mean very different things.  For example:

~~~
students lifted tables
~~~
...could mean: 
- Each student lifted a different table
- Two students lifted the same table
- Some combinations of students lifted some combinations of tables

To truly represent the semantics of the world properly, the algorithm needs to model when things are happening *together* or *separately*.

We can make a simple extension to the algorithm by assuming variables always contain a *set* of values, which are one or more things from the world. Predications must interpret a set that is > 1 as meaning "together".  A set of 1 item means "separately" or "alone".

Furthermore, the `scope()` predication now needs to assign *all possible sets of values* to its variable in order to explore the solution tree and find all the solutions. This can quickly become quite expensive, but there are optimizations we will explore. For now, we'll use the direct approach to understand the algorithm.

Let's work through the example, with a world where two students are lifting a table *together*:

~~~
formula: student(x), table(y), lift(x, y)
scoped formula: scope(x, [student(x), scope(y, [table(y), lift(x, y)])])

world:
  alice
  bob
  table1
  [alice, bob] lift [table1]
~~~
In the new approach, `x` and `y` are iteratively assigned all combinations of things in the world by their `scope()` predication, but the rest of the algorithm proceeds as before. Unlike `in()`, when `lift()` encounters a set of more than one item in either of its arguments, it has to check the world to see if the actors are lifting *together*, or if tables are being lifted *together*.

Summarizing the results in truth table form:

|assignment|formula result|
|---|---|
|x=[alice], y=[alice]| false|
|x=[alice], y=[bob]| false|
|x=[alice], y=[table1]| true|
|x=[alice], y=[alice, bob]| false|
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

In the new form, the solutions we get back are shown below, along with their meaning:

|assignment|formula result|
|---|---|
|x=[alice], y=[table1]| Alice lifted a table|
|x=[bob], y=[table1]| Bob lifted a table|
|x=[alice, bob], y=[table1]| Alice and Bob lifted a table together|

Thus, the algorithm gives us all the assignments of variables that make the formula true in the world. Note that it will successfully find all the interesting combinations in more complex scenarios, such as:
1. 5 students are all lifting the same tables
2. 5 students are all lifting different tables
3. 2 students are lifting one table and 2 are lifting another
4. 1 student is lifting one table and 1 is lifting another

etc.

But: Note that, except for situation #1 above, situations #2 through #4 are only properly represented by a *group* of solutions. There isn't a way to represent them as a single solution (i.e. a single row in the above table) in this model. In addition, while each solution (i.e. row) *does* represent a set of variable assignments that make the formula true, this is only because we aren't encoding any plurality of the nouns from the original phrase.  Currently, we are allowing both plural and singular in the formula. 

We'll address these issues next.

## Solution Groups
The above example glossed over an important point in the formula used. Plurality wasn't encoded in the formula:

~~~
student(x), table(y), lift(x, y)
~~~

... and so we really didn't have a formula that represented how English works. Given these solutions:

|assignment|formula result|
|---|---|
|x=[alice], y=[table1]| Alice lifted a table|
|x=[bob], y=[table1]| Bob lifted a table|
|x=[alice, bob], y=[table1]| Alice and Bob lifted a table together|

If the original phrase really was: "a student lifted a table", then the last solution where Bob and Alice (together) lifted a table shouldn't be there.  On the other hand, if it was "students lifted a table", the first a second answers can't stand alone because they each only represent one student, not "students". Furthermore, if it was "students lifted tables", none of the answers should be there since there is only one table. Encoding the plurality in the formula and representing it properly in the answers is essential for properly capturing meaning.

In MRS, plurality is encoded as a property of the variable, as described in the [MRS topic](devhowtoMRS#variable-properties). So, to encode plural students, a `[ x NUM: pl]` fragment would be in the MRS. We'll just put that at the top of our pseudo MRS in these simple examples to capture it from here on out:

~~~
[ x NUM: pl]
student(x), table(y), lift(x, y)
~~~

Now we need to deal with the fact that our list of solutions don't always stand alone. The first answer alone is *not* a solution to "students lifted a table" since Alice is only one student:

|assignment|formula result|
|---|---|
|x=[alice], y=[table1]| Alice lifted a table|
|x=[bob], y=[table1]| Bob lifted a table|
|x=[alice, bob], y=[table1]| Alice and Bob lifted a table together|

However, if we change our solver algorithm to allow *grouping*, and interpret a *group* of variable assignments as a solution (called a "solution group"), it does work:

solution group 1:

|assignment|formula result|
|---|---|
|x=[alice], y=[table1]| Alice lifted a table|
|x=[bob], y=[table1]| Bob lifted a table|

solution group 2:

|assignment|formula result|
|---|---|
|x=[alice, bob], y=[table1]| Alice and Bob lifted a table together|

Now each *solution group* properly represents the fact that "students" is *plural* by having more than one student in the solution. Thus, solution groups are needed to properly represent plural semantics in this solver.  This is how *distributive* ad *cumulative* readings are represented.

One way for our solver to group solutions is by performing a second pass over the individual solutions and grouping them, just like we just did. The algorithm is:

> Start with the flat list of solutions generated by the formula and a list of only the plural variables:
> - Pick the first plural variable
> - For each combination of the solutions where the list of items in the variable add up to more than 1, do the following:
>   - Recursively do the algorithm again with the next variable using the selected smaller set of solutions
> - After all variables have been tested, the group of solutions remaining is one solution group

Note that this does mean the list of solution groups can get quite large. If there were 3 students lifting a table, the solution groups would be:

|assignment|formula result|
|---|---|
|x=[alice], y=[table1]| Alice lifted a table|
|x=[bob], y=[table1]| Bob lifted a table|

|assignment|formula result|
|---|---|
|x=[alice], y=[table1]| Alice lifted a table|
|x=[sasha], y=[table1]| Sasha lifted a table|

|assignment|formula result|
|---|---|
|x=[bob], y=[table1]| Bob lifted a table|
|x=[sasha], y=[table1]| Sasha lifted a table|

|assignment|formula result|
|---|---|
|x=[alice], y=[table1]| Alice lifted a table|
|x=[bob], y=[table1]| Bob lifted a table|
|x=[sasha], y=[table1]| Sasha lifted a table|

|assignment|formula result|
|---|---|
|x=[alice, bob], y=[table1]| Alice and Bob lifted a table together|

|assignment|formula result|
|---|---|
|x=[alice, sasha], y=[table1]| Alice and Sasha lifted a table together|

|assignment|formula result|
|---|---|
|x=[bob, sasha], y=[table1]| Bob and Sasha lifted a table together|

|assignment|formula result|
|---|---|
|x=[alice, bob, sasha], y=[table1]| Alice, Bob and Sasha lifted a table together|

This represents all the different variable assignments that would make the formula true. Again, there are ways we can help to control the combinatorics, but keeping it simple helps in understanding the algorithm.

We're not done yet, however. Raw plurals like "students" are just one way plurals are encoded in language. There's a whole class of words that add nuance to the plurals that we need to handle next.

## Determiners (many, few, no, 2 or more, ...)
"Determiners" in linguistics classify number or quantity of a noun ("2 students", "a few students"), specificity of a noun ("the student", "a student", "this student"), along with other characteristics like possessiveness ("my student"), "interrogativeness" ("which student"), and forced "distributiveness" ("each student").  All determiners (except the possessive) are true or false based on the count of a particular noun. Because solutions come in a group in the solver, the determiners need to run in the second phase where they have access to a whole group. [todo: Need to describe better why possessives aren't a problem]

In the ERG, these predications come in two shapes:
- Quantifiers: always have the shape: `quantifier(variable, RSTR, SCOPE)`
- Adjectives: always have at least one `x` argument that will also be the `x` argument of a noun of some kind: `predicate(x)` 
[todo: is there a linguistic term for these non-quantifier determiners that I should be using?]

While they both operate at the solution group level and manipulate counts of nouns, they have different arguments because their semantics require them, as we'll see as we walk through each group.

### Adjective Determiners
Adjective determiners like "a few": `_a+few_a_1(e8,x3)`, "many": `much-many_a(e8,x3)`, "2, 3, ...": `card(2,e9,x3)`, all take a single `x` argument and are true based on some quantity-based criteria.  To see if they are true or not, they need to see "how many" of the variable there are, so they need access to a whole solution group.

To do this, they, along with predications that modify their behavior like "very" in "very few": `_very_x_deg(e8,e9), little-few_a(e9,x3)`, are pulled from the formula and evaluated on the second pass. We can do this by a simple adjustment to our second pass algorithm. Here it is, along with the modified part ~~struck through~~, and the replacement ***in bold italic***

> Start with the flat list of solutions generated by the formula and a list of only the plural variables:
> - Pick the first plural variable
> - For each combination of the solutions where the list of items in the variable ~~add up to more than 1~~***meet the criteria of the determiner***, do the following:
>   - Recursively do the algorithm again with the next variable using the selected smaller set of solutions
> - After all variables have been tested, the group of solutions remaining is one solution group

So, in effect, a bare plural like plain old "students" is really just an implicit `plural` determiner that has the criteria `> 1`.

Even though they are represented as having a regular `x` variable in the MRS, the solver needs to handle it specially by:
- Setting its variable to the union of its values across each solution group
- Calling it in phase 2 when it actually has a group.

That way, the adjective determiner can decide if the solution group meets its criteria or not. If it is false, the solution group is removed from the final list of solution groups.

Let's work this through with an example: "2 students ate 2 pizzas":

~~~
[ x NUM: pl]
[ y NUM: pl]
formula: card(2,x), pizza(x), card(2,y), student(y), eat(x,y)
~~~

#### Collective/Collective example:
Given this world of pizzas and students:

~~~
s1
s2
p1
p2
[s1, s2] eat [p1, p2]
~~~
For phase 1: The solver will first remove the adjective determiners and actually run the following formula which will return "student(s) that ate pizza(s)" in all combinations that are true in the world:
~~~
formula: pizza(x), student(y), eat(x,y)
~~~
Which results in 1 solution group:
- x=[s1, s2], y=[p1, p2]

For phase 2: the solver will run the phase 1 algorithm using the appropriate adjective determiner with each variable, like this:

- call `card(2, [s1, s2])` -> `true` since there are two students
- call `card(2, [p1, p2])` -> `true` since there are two pizzas

Thus, the 1 solution group is returned as a solution.

#### Distributive/Distributive example:
Given this world of pizzas and students:

~~~
s1
s2
p1
p2
[s1] eat [p1]
[s2] eat [p2]
~~~
Phase 1 Solution Groups:
- x=[s1], y=[p1]
- x=[s2], y=[p2]

Phase 2 Solution Groups:
- call `card(2, [s1, s2]])` -> `true` since there are two students
- call `card(2, [p1, p2])` -> `true` since there are two pizzas

You can see how any combination of pizzas and students in groups or not will be solutions, as long as they add up to 2 for each.

### Quantifier Determiners
Just like adjective determiners, the solver runs quantifier determiners in phase 2, for exactly the same reason: they operate across the whole solution group. So, like adjective determiner example, even though they are represented as having a regular `x` variable in the MRS, the solver needs to handle it specially by:

- Setting its variable to the union of its values across each solution group
- Calling it in phase 2 when it actually has a group.

Moreover, some quantifiers actually need to know what the rstr values were originally as well. So, the quantifier *also* needs to be passed the original set of RSTR values as an argument.

todo: Note that quantifiers can run with adjective determiners!

Quantifiers in MRS always have 3 arguments: `quantifier(x, RSTR, BODY)`:
- The first is the variable they are quantifying
- The second is a list of predications that defines "the set of things we are going to start with"
- The third is a list of predications that defines "something that needs to be true of some group of the RSTR set (depending on the quantifier)"

These can have some more complicated criteria. For example:
#### `a(x, student(x), study(x))`: "a student is studying"
`true` for a solution group that *only* has a single `x`.  Works just like `card(1, x)`.

#### `every(x, student(x), study(x)`: "every student is studying"
For `every`, it is not enough to look at the solution group because the group will only include the students that *are* studying. It needs to compare that list with the students that were true for `student(x)` *before* it was checked against the `BODY`. 

To do this, the solver needs to keep track of what the original `RSTR` values were for every `x` variable. Then, `every` can retrieve that list and compare to the solution.
[todo: talk about what happens when there are no students studying]

#### `the(x, student(x), study(x))`: There is 1 "obvious student we are talking about", and they are studying


## Add scopal arguments

## Optimizations
I'm trying to find algorithms for grouping solutions to an equation with n variables, The variable assignments are sets and the criterion are simple expressions involving `=><` and only one variable, although the grouping criteria may have a criterion on more than one variable. More detail below.

## Background:
I have a Python predicate-logic-like program that generates solutions to the variables in an equation, where the variable values are always a set of > 0:
- The elements of a set are always Python objects that support __eq__ and __hash__
- A set assigned to a variable always contains unique values (i.e. no duplicates)
- A given object can be repeated between variables in the same solution (i.e. the same object could be a member of another set that is assigned to another variable). 
- A given value can be repeated in the same variable in another solution to the same equation

Each equation contains an arbitarily long list of variables, but in practice this is no more than 10ish variables. A single solution is a list of assignments of sets to the variables, like this:
~~~
solution 1: x=[a, b], y=[c], z=[d, e, f, g]
~~~

The program generates all the solutions to the equation, like this:

~~~
solution 1: x=[a, b], y=[c], z=[d, e, f, g]
solution 2: x=[a, b], y=[a], z=[a]
...
solution n: x=[m], y=[n, o, p], z=[o, p]
~~~

The list of solutions to the equation can be quite large and can be generated in a "stream", meaning: conceptually there is a Python generator that can generate a new solution each time it is asked to and will stop when there are no more.

## Problem:
I need to generate efficient *groupings* of the solutions using a set of criterion.  
- Each criterion is a simple constraint about the total number of items assigned to a variable in a group. 
- Each criterion uses simple numeric rules involving `<,>,=` such as "at least n", "no more than y", "exactly n", etc. 
- The grouping criteria may contain multiple criterion, each about a different variable, so there may be constraints on several (or all) of the variables. 
- *efficient* means: Get the first answer quickly (sometimes I can stop after 1 answer) as well as get *all* answers quickly.

When counting items in a variable across a group, only unique items are counted. So a group that contains 2 solutions: 
~~~
x=[a]
x=[a,b]
~~~
... would only add up to 2 items since `a` is duplicated.

Some examples:
~~~
at_least_3(x), exactly_2(y) would be true for this group:
x=[a], y[a]
x=[b, c], y[a, b]

no_more_than_1(x), between_3_and_5(y) would be true for this group:
x=[a], y[a]
x=[a], y[b, c]
x=[a], y[d]
~~~

## My Questions:
What is the name of the problem I have (if there is one)? I *believe* that finding a group for a single variable that meets its criterion is a "Knapsack Problem" (specifically the Subset-Sum Problem (SSP)), but I'm not sure what the name is for the full problem since the set of items for each "knapsack" (i.e. variable) is different and constrained to what the group of solutions contains.  I would love to know that if anyone knows it.

Does anyone know of efficient ways to get the first answer and eventually of them? Preferrably in a way that takes advantage of the streaming nature of the answers. Meaning: start returning groups before all of the answers are generated.

The approach I'm using currently is: Start with the first variable `x` and iteratively find each group of solutions that meets the criterion on `x`. Take each set of solutions and see if it also meets the criterion on `y`, `z`, etc. without changing the group. If you get to the end successfully, you have a group that meets all the constraints.


### Streaming
### combinatoric variables

### predications optimized for combinatoric variables (like in)
### Phase 1 If nobody cares about collective values, don't generate them
If no predicate is collective aware, generating them wastes time.

So, if the predications declare up front what they *might* use, we can rule out some scenarios.

Predications declare in their arguments what they are distributive aware, collective aware, or both. 

If they, like `met` are collective *only*

In: coll neutral, dist aware
met: coll aware, dist unsupported
ran/large: coll unsupported, dist aware
loc_nonsp: coll aware, dist aware

two boys ran in a room together 
the running boys lifted the table

### Phase 2: 
"files are in folders"
    For phase 2 we generate all combinations of potential answers for the plural determiners
        Because nothing in "files are in folders" is collective aware, we shouldn't bother to generate those alternatives, and just stick to the distributive sets. We might need a distributive set for "files are in 2 folders": we need alternatives that mix the answers enough to find the "2 folders"
We can do this the same was as we did in 1: If there is nothing that needs
### If we look at the size of the variables, we might call in a different order

### For yes/no we only need to prove one answer, for wh we want to get the smallest set of answers?

## Plurals and Predication Behavior
Above, we've seen how `to lift` means something different when people are doing it *together* vs. *separately* and the predication needs to check for that distinction when deciding if the variable assignments mean `true`.

How should `in` behave in this algorithm? Take the following two phrases, when Alice and Bob are in the same living room:
1. Bob and Alice are in the same room
2. Bob and Alice are in the same room together

For the meaning of #2 where `together` applies to `in` (as opposed to applying to Bob and Alice being together), #1 and #2 are both true and mean the same thing. "together" in this case is transparent. "in" just ignores it. If "in" succeeds in the "together" case (even though it has no special meaning), it will generate truth values that look identical to the above `lift` example, but in some sense are duplicates, like this:

~~~
formula: student(x), room(y), in(x, y)
~~~
|assignment|formula result|
|---|---|
|x=[alice], y=[livingroom]| Alice is in the living room|
|x=[bob], y=[livingroom]| Bob is in the living room|
|x=[alice, bob], y=[livingroom]| Alice and Bob are in the living room together|

The last answer really means the same thing as the previous two since `in` doesn't distinguish like `lift` does. So, in one sense it is duplicate information. However, if a person said "Alice and Bob are in the living room together" and they *meant* that they are just both in the same room (vs. that they were next to each other), we want the system to respond with "That is true!".  Responding with anything else would just be confusing. So, `in` should respond as above.

Furthermore, some words just don't work with sets or individuals. Two examples:
- `met`, as in "students met"? `met` is an example of a verb that *requires* a set.  It *always* means together. So, `met(x)` must always be `false` if `x` only contains one item.
- `ran` as in "students ran"? `ran` is an example of a verb that *requires* an individual item. Each student must be running *separately* (even if they are all running at the same time). `ran` must always be `false` if `x` contains more than one item.

When talking about plurals in linguistics, sets of 1 are called `distributive` and sets of > 1 are called `collective`. So, `met` requires a collective argument, and `ran` requires a `distributive` argument.

We'll call predications like `in` that allow a collective argument but don't mean anything different by it a "collective neutral" predication. Words like `lift` are "collective aware".
[todo: is there a linguistic term for this that I should be using?]

So, now we have a solver that can deal with plurals properly, and allows predications to distinguish the various plural cases they encounter. There are a few more scenarios that need handling.