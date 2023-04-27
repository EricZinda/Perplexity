### Solution Group Algorithm for Simple Plurals
The solver can group solutions by performing a second "grouping" pass over the initial set of individual solutions, like we just did above. 

The algorithm is:

> Evaluate the formula to get all individual solutions regardless of whether they are singular or plural. This will generate some (i.e. collective), but not all, plural answers due to the fact that variables can contain sets larger than 1. Using that flat list of solutions:
> - Pick a plural variable:
>   - For every combination of the solutions where the set of items assigned to that variable in the combination add up to more than 1, do the following:
>     - Recursively do the algorithm again with the next plural variable, using only the just selected set of solutions
> - After all plural variables have been tested, if they all succeeded, the group of solutions remaining is one solution group that represents a correct plural answer to the formula.
> 
> After all possible combinations of solutions have been tested, all plural answers to the formula have been found.

Note that this does mean the list of solution groups can be quite large but that is only because there can be many true solutions to a formula. 

For example, if there were 3 students (Alice, Bob, Sasha) lifting a table, the solution groups would be:

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

This represents all the different variable assignments that would make the formula true. Any of them *could be* what a speaker meant by "Students lifted a table" in that world. Again, there are ways we can help to control the combinatorics, but keeping it unoptimized makes the algorithm simpler to understand.

We're not done yet, however. Raw plurals like "students" are just one way plurals are encoded in language. There's a whole class of words that add nuance to the plurals that we need to handle next.

## Determiners (many, few, no, 2 or more, etc.)
"Determiners" in linguistics classify number or quantity of a noun ("2 students", "a few students"), specificity of a noun ("the student", "a student", "this student"), along with other characteristics like possessiveness ("my student?"), "interrogativeness" ("which student"), and forced "distributiveness" ("each student").  

All determiners (except the possessive) are `true` or `false` based on the *count* of a particular noun (and potentially other criteria). So, to properly group solutions, the determiners need to run in the second phase where they have access to all solutions. 

In the ERG, determiner predications come in two shapes:
- *Quantifiers* always have the shape: `quantifier(variable, RSTR, SCOPE)`. They perform the `scope()` function we've been doing explicitly so far, in addition to counting.
- *Adjectives* always have at least one `x` argument: `predicate(x)`. `x` will also be the `x` argument of a noun of some kind.

While they have different arguments, they both operate at the solution group level and manipulate counts of nouns. From the counting perspective they can be treated the same.

### Adjective Determiners
Adjective determiners like "a few": `_a+few_a_1(e8,x3)`, "many": `much-many_a(e8,x3)`, "2, 3, ...": `card(2,e9,x3)`, all take a single `x` argument and are `true` based on some quantity-based criteria.  To see if they are `true` or not, they need to see "how many" of their variable exist. Thus, they need access to a group of solutions.

To do this, they are pulled from the formula and only evaluated on the second pass. We can do this by a simple adjustment to our second pass algorithm. Here it is, along with the modified part ~~struck through~~, and the replacement ***in bold italic***

> Evaluate the formula to get all individual solutions regardless of whether they are singular or plural. This will generate some, but not all, plural answers due to the fact that variables can contain sets > 1. Using that flat list of solutions:
> - Pick a plural variable:
>   - For every combination of the solutions where the set of items assigned in the combination ~~add up to more than 1~~***meet the criteria of the determiner***, do the following:
>     - Recursively do the algorithm again, with the next plural variable, using only the just selected set of solutions
> - After all plural variables have been tested, if they all succeeded, the group of solutions remaining is one solution group that represents a correct plural answer to the formula.
> 
> After all possible combinations of solutions have been tested, all plural answers to the formula have been found.

So, in effect, a bare plural like plain old "students" is really just an implicit `plural(x)` determiner that means `> 1`. That is, in fact, how the solver will implement it.

Even though they are represented as having a regular `x` variable in the MRS, the solver actually handles them differently than other predications, by:
- Calling them in phase 2 when groups of solutions are available.
- Setting their `x` variable to the union of its values across each solution group being tested

That way, the adjective determiner can decide if a group of solutions meets its criteria or not. If so, the solution group is added to the final list of solution groups by the pass 2 code.

So, determiners get run in pass 2 and have slightly different arguments than are represented in the MRS.

Let's work through an example: "2 students ate 2 pizzas":

~~~
[ x NUM: pl]
[ y NUM: pl]
formula: card(2,x), pizza(x), card(2,y), student(y), eat(x,y)
~~~

#### Collective/Collective example
Given the following world of pizzas and students:

~~~
s1
s2
p1
p2
[s1, s2] eat [p1, p2]
~~~

##### Phase 1:
The solver will first remove the adjective determiners representing "2" and run the following modified formula:

~~~
formula: pizza(x), student(y), eat(x,y)
~~~

... which will return all combinations of "student(s) that ate pizza(s)" in this world. In this world,  `eat()` was only `true` for `s1` and `s2` *together* eating `p1` and `p2` *together* (presumably this means as a pizza sandwich?), so only results in one solution:
~~~
Solution 1: x=[s1, s2], y=[p1, p2]
~~~

##### Phase 2:
The solver will run the phase 2 algorithm using the appropriate adjective determiner with each variable:

First, find all groups where `card(2, x)` is `true`:
~~~
Group 1:
Solution 9: x=[s1, s2], y=[p1, p2]
~~~

Take each of those groups and see if `card(2, y)` is also `true`:

~~~
Group 1:
Solution 9: x=[s1, s2], y=[p1, p2]
~~~

Thus, Group 1 is returned as the only solution group.

#### Distributive/Cumulative example:
Given this world of pizzas and students:

~~~
s1
s2
p1
p2
[s1] eat [p1]
[s2] eat [p2]
~~~
This is a cumulative example since "students" adds up to 2, and "pizzas" add up to 2, but there isn't 2 of everything.

Phase 1 solutions:

~~~
Solution 1: x=[s1], y[p1]
Solution 2: x=[s2], y[p2]
~~~

Phase 2 solution groups:

~~~
Group 1:
Solution 1: x=[s1], y[p1]
Solution 2: x=[s2], y[p2]
~~~

One group is returned as the answer since it is the only set of answers where  there are 2 `x` values and 2 `y` values.

#### Distributive/Distributive example:
Given this world of pizzas and students:

~~~
s1
s2
p1
p2
p3
p4
[s1] eat [p1]
[s1] eat [p2]
[s2] eat [p3]
[s2] eat [p4]
~~~
This is a distributive example since each of 2 students separately is eating each of 2 pizzas separately.

Phase 1 solutions:

~~~
Solution 1: x=[s1], y[p1]
Solution 2: x=[s1], y[p2]
Solution 3: x=[s2], y[p3]
Solution 4: x=[s2], y[p4]
~~~

Phase 2 solution groups:

card(2, x) generates one solution which is:
Solution 1: x=[s1], y[p1]
Solution 2: x=[s1], y[p2]
Solution 3: x=[s2], y[p3]
Solution 4: x=[s2], y[p4]

~~~
Group 1:
Solution 1: x=[s1], y[p1]
Solution 3: x=[s2], y[p3]

Group 2:
Solution 2: x=[s1], y[p2]
Solution 4: x=[s2], y[p4]
~~~

To properly capture distributive/distributive modes we need to think of the determiner as meaning "count per other plural".

"2 students ate 2 pizzas in 2 rooms"

4 students ate 4 pizzas
3 students ate 3 pizzas
1 student  ate 

Good background: https://champollion.com/wp-content/uploads/2018/07/champollion_lsa2015.pdf
You can see how any combination of pizzas and students in sets of 1 or 2 will form a solution group, as long as they add up to 2 for each.

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

## Plurals
The above example didn't encode any constraints about plurality in the formula:

~~~
student(x), table(y), lift(x, y)
~~~

... and so we really didn't have a formula that represented how English works. Given these solutions:

|assignment|formula result|
|---|---|
|x=[alice], y=[table1]| Alice lifted a table|
|x=[bob], y=[table1]| Bob lifted a table|
|x=[alice, bob], y=[table1]| Alice and Bob lifted a table together|

If the original phrase really was: "a student lifted a table", then the last solution where Bob and Alice (together) lifted a table shouldn't be there since "Bob and Alice" are not "a student".  

On the other hand, if it was "students lifted a table", the first and second answers can't stand alone because they each only represent one student, not "students". 

Finally, if it was "students lifted tables", none of the answers should be there since there is only one table. 

So, we really didn't have a "formula language" that could capture the sematics of the phrase enough to distinguish these cases. Encoding the plurality in the formula and representing it properly in the answers is essential for properly capturing meaning.

In the MRS "formula language", plurality *is* encoded using a property of the variable, as described in the [MRS topic](devhowtoMRS#variable-properties). So, to encode plural students, a `[ x NUM: pl]` fragment would be in the MRS. We'll just put that at the top of our pseudo MRS in these simple examples to capture it for now:

~~~
[ x NUM: pl]
student(x), table(y), lift(x, y)
~~~

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
Because yes/no questions just need one answer, streaming means we only have to find one

### combinatoric variables
- If we don't know what predications require (must have) and support (can have), they have to do all alternatives 
    in case downstream predications need those alternatives
    - If they are declared then we can optimize *some* cases

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

### Don't generate alternatives that won't be used
"files are in folders": If there are 10 files, "files" generates all combinations of files when really they are almost all ignored
more_than_1(x), more_than_1(y)

The determiners are literally only counting things so we should be able to do some numeric optimizations

Option 1: Do special purpose optimizations
Walking back from the end: all constraint(1, inf, False) should be
    If the last determiner is > 1 delete it
The last determiner does not need to create groups outside of what it needs

If we assume we are really just putting constraints on the number of rows then:

Anything with no upper bound has to have them all:
- n_or_more: could be any number of rows
- at_least_n: could be any number of row
- more_than_n: ditto

Upper bounds have a limit:
- exactly_n: can't be more than n individual rows 
- less_than_n: can't be more than n individual rows

Could be combinatorial:
1_or_more
at least 1

If we have the engine generate *ranges* that the row count must be in it will reduce the solution space
    Only the first one gets to select the sets of solutions
    [allowing combinatorial will only help more_than_0 (which might be a lot of cases)]

If we count the actual values we can discard some combinations exactly

Implementation:
(done) quantifiers and determiners should also use the same function, they just have a bit flipped to pass them different arguments
(done) all counting determiners should use the same function then we can optimize by looking through the whole list and modifying it
(done) Make all determiners take the same arguments
    determiner(execution_context, variable_name, predication, all_rstr, solution_group, combinatorial, (extra args)
(done) Make them specify it using an abstract expression:
    number_constraint(min_count, max_count, exactly)
    or
    custom_constraint(function, args) that can't be optimized

    udef is 1, inf, False

Make quantifiers declare what they are doing

### If we look at the size of the variables, we might call in a different order

### For yes/no we only need to prove one answer, for wh we want to get the smallest set of answers?

## Basic model for coll/dist/cumul
A given quantifier is said to be coll/dist/cumul, not the sentence.


One way to think about how numeric determiners compose is that you can read a phrase like `determiner1(x), noun1(x), determiner2(y), noun2(y)` from left to right like this:
> For each x in a group of x's where: noun1(x) and the total of all x individuals is determiner1(x), 
>   there is a group of y's where: noun2(y) and the total of all y individuals is determiner2(y)

For example:

~~~
3 children ate 4 pizzas
for each x in a group of x's where: children(x) and the total of all x individuals is card(3, x), 
    there is a group of y's where: pizza(y) and the total of all y individuals is card(4, y).

a few students lifted more than 2 tables
for each x in a group of x's where: students(x) and the total of all x individuals is a _a+few_a_1(e, x),
    there is a group of y's where: table(y) and the total of all y individuals is _more+than_a_1(e,e10), card(2,e10,y)
~~~
Collective mode is when the `variable` is 1 set-based value of N elements that satisfies the determiner - i.e. its single value collectively satisfies the determiner. In the first example, `[[child1, child2, child3]]` is collective.

Distributive mode is when it takes N set-based values of 1 element to satisfy the determiner -- i.e. the values that satisfy the determiner are distributed across several values. In the first example `[[child1], [child2], [child3]]` is distributive.

But what about a world where 1 child is eating 1 pizza and another child is eating a different pizza and someone says "2 children are eating 2 pizzas"? Clearly the answer is "correct!", but this is neither distributive for the children (because that would need each child to be eating 2 pizzas) nor collective for the children (because that would require the two children *together* eating 2 pizzas). This is a third scenario, called "cumulative". Putting it in the same form as above for a phrase like `determiner1(x), noun1(x), determiner2(y), noun2(y)`:

> For a group of x's where: noun1(x) and the total of all x individuals is determiner1(x),
>   there is a group of y's where noun2(y) and the total of all y individuals is determiner2(y)

Cumulative mode just requires that there are `determiner1(x)` x's doing something, and `determiner2(y)` y's having something being done to them, in any combination.

Cumulative mode happens when there is arbitrary combination, not strictly collective or distributive, that satisfies the determiner: in the first example `[[child1, child2], [child3]]` is cumulative.



Definitions:
- A *adjective determiner* is an adjective that creates a numeric constraint on a particular `x` variable, such as `card(2,e,x)` or `much-many_a(e8,x3)`.
- A *quantifier determiner* is a quantifier that creates a numeric constraint on a particular `x` variable, such as `_all_q(x3,RSTR,BODY)` or `_the_q(x3,RSTR,BODY)`
- An *undetermined MRS* is formed by: 1) removing all determiner adjectives (and their modifiers), 2) converting all determiner quantifiers to "udef_q", 3) ignoring the `pl/sg` constraint on any variable.
- An *undetermined solution* is formed by assigning a single non-empty set to every `x` variable in an undetermined MRS such that it is true.
- A *determiner solution group* for `determiner(x)` is a group of undetermined solutions where the count of unique individuals across all `x` values in the group satisfies the determiner. It contains *subsets* (see next definition).
- A *determiner solution group subset* is a subset of undetermined solutions in a determiner group. Except for the first time through, the solutions in a subset all contain the same `x` value.

Algorithm: 
Start with an `ordered_determiner_list` of numeric determiners (adjective and quantifier) and a `previous_determiner_group` that starts as the set of all undetermined solutions. `previous_determiner_group` starts with a single subset that contains all the solutions. 

Using the next determiner in `ordered_determiner_list` (`determiner(variable)`) and `previous_determiner_group`:
    Find collective and distributive: For each `previous_subset` in `previous_determiner_group`:
        Group all the solutions in `previous_subset` by unique `variable` values (where "value" means the entire variable value as a set, not the individuals in it). 
            These form the `new_subsets`.
        Find each combination of the unique `variable` values just found
            Merge them into a unique list (removing duplicates)
            See if this combination satisfies `determiner(variable)`.
        Form `new_determiner_group` using `new_subsets` that go with these unique variable values
        Run the algorithm again after removing `determiner(variable)` from the list and using `new_determiner_group`
    Find cumulative: Do the same but merge all subsets instead of iterating over each subset

If all determiners are successful, the determiner group that remains at the end is a solution.





if we have `q_1(x), q_2(y)` in a world where:

~~~
[x1], [x2], [x3], [x1, x2], [x1, x2, x3], ... (i.e. all combinations of x1, x2, x3)
[y1], [y2, [y3], [y1, y2], [y1, y2, y3], ... (i.e. all combinations of y1, y2, y3)
~~~

For a given determiner quantifier like "all" or a determiner adjective like "2 (i.e. card(2, x))":

A distributive reading of `x` must only include a set of sets of single individuals in `x` that add up to the determiner count of N. So for "2 students": `x=[[x1], [x2]]` or `x=[[x2], [x3]]` is a valid distributive reading, but `x=[[x1, x2]]` is not, nor is `x=[[x1], [x2], [x3]]`.

A collective reading of `x` must only ever include a single set of the determiner count of N individuals. So for "2 students": `x=[[x1, x2]]` is a valid collective reading, but `x=[[x1]]` is not, nor is `x=[[x1, x2], [x2, x3]]`

A cumulative reading of `x` is any combination of values that add up to the determiner count of N individuals that isn't distributive or collective. So for "3 students": `x=[[x1, x2], [x3]]` or `x=[[x1], [x2, x3]]` are valid cumulative readings but any set of sets where the individuals add up to > N are not

Take the first determiner, `determiner1(x)`. 
Group all solutions by unique values of `x`.
Find a set of unique values that meet the determiner.
Call the group of solutions that go with these unique values a "determiner group"
Pass the determiner group to the next determiner




To determine the valid variable assignments in an MRS that uses plurals: Work out the fully-resolved trees for the MRS, and go through the following algorithm using pre-order traversal of each tree.


Going from left to right, `card(3)(x), card(2)(y)`, take the first value in the set generated by `x` and apply it to the set generated by `y`:
~~~
(distributive x, distributive y)
[x=[x1], y=[[y1], [y2], [y3]]], 
    [x=[x2], y=[[y4], [y5], [y6]]], 
        [x=[x3], y=[[y7], [y8], [y9]]]]

(distributive x, collective y)
[x=[x1], y=[[y1, y2, y3]], 
    [x=[x2], y=[[y4, y5, y6]], 
        [x=[x3], y=[[y7, y8, y9]]]

(distributive x, cumulative y)
[x=[x1], y=[[y1, y2], [y3]], 
    [x=[x2], y=[[y4], [y5, y6]], 
        [x=[x3], y=[[y7, y8, y9]]]


(collective x, distributive y)
[x=[x1, x2, x3], y=[[y1], [y2], [y3]]]

(collective x, collective y)
[x=[x1, x2, x3], y=[[y1, y2, y3]]]

(collective x, cumulative y)
[x=[x1, x2, x3], y=[[y1], [y2, y3]]]


(cumulative x, distributive y)
[x=[x1, x2], y=[[y1], [y2], [y3]],
    x=[x3], y=[[y1], [y2], [y3]]]

(cumulative x, collective y)
[x=[x1, x2], y=[[y1, y2, y3]], 
    [x=[x3], y=[[y4, y5, y6]] ]

(cumulative x, cumulative y)
[x=[x1, x2], y=[[y1], [y2, y3]], 
    [x=[x3], y=[[y4, y5, y6]]] ]

etc.
~~~

~~~
x=[[x1, x2, x3]] (collective)
x=[[x1], [x2, x3]] (cumulative)

y=[[y1], [y2], [y3]] (distributive)
y=[[y1, y2, y3]] (collective)
y=[[y1], [y2, y3]] (cumulative)
~~~




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


# Email



# Archive
Any cumulative or distributive readings where the count of `x10` *across the whole group* don't meet the determiner test won't be found. For example:
- Group 1
- todo: another case


~~~
Solution 3: x3=man3, x10=pizza3
Solution 4: x3=man4, x10=pizza3
~~~

You can see the ambiguity that @trimblet pointed out above in the answers:
- Group 2 is both disributive over `x3` and cumulative. 
- Group 3 is both collective over `x3` and cumulative. 


To get the collective, distributive and cumulative readings with reverse scope (with respect to the word order), you'd use the fully resolved tree with that scoping.

Issue:
- initial pass doesn't need both approaches
- Lots of duplication of scenarios