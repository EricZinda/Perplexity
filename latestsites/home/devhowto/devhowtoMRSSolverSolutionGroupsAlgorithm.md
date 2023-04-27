{% raw %}## Solution Group Algorithm
As described in the [previous section](https://blog.inductorsoftware.com/Perplexity/home/devhowto/devhowtoMRSSolverSolutionGroups), the only way to represent the semantics of cumulative and distributive readings of a sentence like:

```
students lifted a table

formula: student(x3), table(x10), lift(x3, x10)
scoped formula: scope(x3, [student(x3), scope(x10, [table(y), lift(x3, x10)])])
```

... is to have the solver create groups of solutions ("solution groups") that are the complete answers -- a single solution to the MRS is not enough. This section describes one algorithm that can accomplish this.

### Overview
The basic approach is to generate the solutions, exactly like we've been doing so far, but then add a new "grouping pass" afterward. This grouping pass will find the groups of solutions that meet all the *numeric constraints* that the words in the phrase has placed on the variables. The groups found represent the complete answers to the MRS.  

To illustrate what "numeric constraint" means, take "students lifted a table":
- "students ..." is plural, which means the contraint is: `count(students) > 2`
- "... a table" means the constraint is: `count(tables) = 1`
- etc.

To determine `count(students)` in the above example, we could simply count the students across all the solutions in a given group. If we do this as well for `count(tables)` and return those groups where `count(students) > 2` and `count(tables) = 1`, we will produce groups which *are* valid, but will miss any answers that require a "per previous value" count. So, we'll miss the distributive ones. We need to do a slightly more complicated counting algorithm that is "per previous value" to get *all* the readings.

Here's an overview of the how the algorithm can determine groups that properly account for cumulative, collective and distributive readings:
> 1. Determine the order variables appear when evaluating the tree
> 2. Walk the variables in order. For each variable: count individuals in the solutions two different ways:
>    - Cumulatively: Total the variable individuals across all rows (as above)
>    - Distributive/collectively: Group the individuals by the value of the previous variable in the order, and then do the total *per previous value*. If the totals are all the same, across all previous values, that is the count. If not, this count fails and has no value.
>      - If this is the first variable: there is no "previous value" to use in the "total per previous value" definition of collective and distributive. Therefore, the first can only be totalled as cumulative. 
> 3. If either count meets the variable constraint, it succeeds and the next variable in the order is tried. If not, this group fails.
> 4. If the end is reached and all variables succeeded, this is a valid solution group.


To get the groups that should be checked in the process above, we (you guessed it...) try every combination of solutions that solving the tree produced. We will end this entire section with ways of efficiently doing this, but we'll start with the simplistic approach because it is easier to follow and does work, just not efficiently as it could. 

Figuring out the contraints on the variables is a longer story, which the next few sections will cover.

### Variable Constraints Overview
Notice that every `x` variable used in a tree has *some kind of* numeric constraint applied to it, even if implied. We can model them all using a `between(min, max)` (inclusive) constraint with a lower bound and an upper bound. The upper bound can be "inf", meaning "infinity".

For "students lifted a table":
- "students ..." is plural, which means: `between(2, inf)`
- "... a table" means: `between(1, 1)` (i.e. exactly 1)

For "which file is under 2 tables?":
- "... file ..." is singular, which means: `between(1, 1)`
- "... 2 tables ..." specifies two, so: `between(2, 2)`

`between(1, inf)` is the default constraint, meaning: "anything". Variables with no other constraint get this one -- it is implied.

The next section talks about how to extract these constraints from the tree itself.

### Determining Constraints From the MRS Tree
Numeric constraints can come from 3 places in an MRS: quantifiers, adjectives and the plurality property of a variable. Determining constraints will force us to finally start looking at full MRS documents as opposed to simplified MRS fragments that use the artificial `scope()` predication.

Let's start with "two students lifted a table". Here's one MRS reading of it, along with one well-formed tree:

```
[ "two students lifted a table"
  TOP: h0
  INDEX: e2 [ e SF: prop TENSE: past MOOD: indicative PROG: - PERF: - ]
  RELS: < [ udef_q<0:3> LBL: h4 ARG0: x3 [ x PERS: 3 NUM: pl IND: + ] RSTR: h5 BODY: h6 ]
          [ card<0:3> LBL: h7 ARG0: e9 [ e SF: prop TENSE: untensed MOOD: indicative PROG: - PERF: - ] ARG1: x3 CARG: "2" ]
          [ _student_n_of<4:12> LBL: h7 ARG0: x3 ARG1: i10 ]
          [ _lift_v_cause<13:19> LBL: h1 ARG0: e2 ARG1: x3 ARG2: x11 [ x PERS: 3 NUM: sg IND: + ] ]
          [ _a_q<20:21> LBL: h12 ARG0: x11 RSTR: h13 BODY: h14 ]
          [ _table_n_1<22:27> LBL: h15 ARG0: x11 ] >
  HCONS: < h0 qeq h1 h5 qeq h7 h13 qeq h15 > ]

                        ┌── _student_n_of(x3,i10)
            ┌────── and(0,1)
            │             └ card(2,e9,x3)
udef_q(x3,RSTR,BODY)
                 │             ┌────── _table_n_1(x11)
                 └─ _a_q(x11,RSTR,BODY)
                                    └─ _lift_v_cause(e2,x3,x11)

Text Tree: udef_q(x3,[_student_n_of(x3,i10), card(2,e9,x3)],_a_q(x11,_table_n_1(x11),_lift_v_cause(e2,x3,x11)))
```
Two points to note as we transition to using real MRS instead of simplified trees:

1. At this point, we can dispense with the artificial `scope()` predication because the MRS [quantifier predications](https://blog.inductorsoftware.com/Perplexity/home/devhowto/devhowtoMRS) (those with `_q` at the end) fulfill the same variable scoping role as `scope()`. They declare where in the tree a variable can be used.  They *also* can add numeric constraints to the variable, as we'll see below.
2. Predications in MRS have [variable types](https://blog.inductorsoftware.com/Perplexity/home/devhowto/devhowtoMRS) beyond the `x`-type variables we've been using. For the examples we'll see here, these can be safely ignored. We'll handle those in a later section.

With that covered, let's walk through how to get the numeric constraints from the above MRS.

#### Order of Variables
First, notice that the variable order in this tree is [`x3`, `x11`] (read left to right) since that is the order of the variable quantifiers when evaluating the tree depth-first.

#### Quantifier Constraints
Each variable in an MRS [must have a quantifier that scopes it](https://blog.inductorsoftware.com/Perplexity/home/devhowto/devhowtoMRS) (the artificial `scope()` predication performed this function in prior examples), and quantifiers always add a numeric criteria to the variable they scope.  Some, like `udef_q` in our example, add the default criteria `between(1, inf)`. This simply means: "at least one". The `_a_q` quantifier means "a single thing", so it adds `between(1, 1)`. 

Thus, the quantifiers in this example add these constraints:

|`x3` (students)|`x11`(table)|
|---|---|
|`udef`: `between(1, inf)`| `_a_q`: `between(1, 1)`|

#### Adjective Constraints
Some adjectives also add numeric constraints. In our example, the adjective "two" gets converted to the predication: `card(2,e9,x3)` in the MRS. This predication adds the constraint `between(2, 2)` to `x3`. Now we have these:

|`x3` (students)|`x11`(table)|
|---|---|
|`udef`: `between(1, inf)`| `_a_q`: `between(1, 1)`|
|`card`: `between(2, 2)`| |

#### Plural Variable Properties
Finally, some variables (`x3` in our example), are defined to be plural by the MRS, as indicated by `NUM: pl` in the [variable properties](https://blog.inductorsoftware.com/Perplexity/home/devhowto/devhowtoMRS) of `x3`:

```
[ udef_q<0:3> LBL: h4 ARG0: x3 [ x PERS: 3 NUM: pl IND: + ] RSTR: h5 BODY: h6 ]
```

This adds the constraint `between(2, inf)` to `x3`. 

`x11` from `_table_n_1(x11)` is singular based on its variable properties:

```
[ _lift_v_cause<13:19> LBL: h1 ARG0: e2 ARG1: x3 ARG2: x11 [ x PERS: 3 NUM: sg IND: + ] ]
```

...  so it adds `between(1, 1)`:

Thus, our final list of constraints is:

|`x3` (students)|`x11`(table)|
|---|---|
|`udef`: `between(1, inf)`| `_a_q`: `between(1, 1)`|
|`card`: `between(2, 2)`| `[NUM: sg]`: `between(1, 1)` |
|`[NUM: pl]`: `between(2, inf)`| |

#### Combining Constraints
The final constraints from the example can be combined.  If `x3` must be:
- "between 1 and infinity" *and* "between 2 and infinity" then saying "between 2 and infinity" is enough.
- "between 2 and infinity" *and* "between 2 and 2 (i.e. exactly 2)" then saying "between 2 and 2" is enough.

Using this logic, the final list of constraints above can be reduced to:

|`x3` (students)|`x11`(table)|
|---|---|
|`between(2, 2)`| `between(1, 1)`|

Which matches the intuition that there should be exactly two students and exacty one table (possibly for each student) in "two students lifted a table".

#### MRS Constraints Summary
So, now we have an approach to gathering the constraints from the MRS:

> For each `x` variable in the MRS:
> 1. Add the appropriate constraint for its quantifier
> 2. Add any constraints from adjectives that modify it
> 3. Add the `NUM: pl` or `NUM: sg` constraint
> 4. Reduce them to the minimal set


### The Final Algorithm: Introducing Phase 0
This section started by describing the two phases of the solver algorithm:
- Phase 1: Evaluate the MRS tree to get the solutions
- Phase 2: Group the solutions into solution groups that meet the phrase's numeric constraints

It turns out that the (just described) process of building the numeric constraints is really a "Phase 0". And, if you think about what adjectives like "two" (or "a few" or "many") actually *do*, their entire contribution is to act as a numeric constraint. Their work happens during Phase 2 ... they have nothing to do in Phase 1. So, after we extract the criteria from them in Phase 0, they should be *removed from the tree* and Phase 1 should be solved using the modified tree without them.

Furthermore, recall that quantifiers do two things: scope a variable and add a numeric constraint to the variable. So, after you extract the numeric constraint from quantifiers like `_a_q` or `_some_q`, you've also removed all of their contribution to Phase 1 *except for variable scoping*. So, we don't *remove* them, but we do *replace* them with the most generic quantifier: `udef_q`.

Thus, Phase 0 analyzes the full tree for "2 students lifted a table", which is this:
```
                        ┌── _student_n_of(x3,i10)
            ┌────── and(0,1)
            │             └ card(2,e9,x3)
udef_q(x3,RSTR,BODY)
                 │             ┌────── _table_n_1(x11)
                 └─ _a_q(x11,RSTR,BODY)
                                    └─ _lift_v_cause(e2,x3,x11)
```
... but then, after extracting numeric constraints, converts it to a tree without the numeric constraints in it (since those will run in Phase 2), and provides this modified tree to Phase 1:

```
            ┌────── _student_n_of(x3,i10)
            │             
udef_q(x3,RSTR,BODY)
                 │               ┌────── _table_n_1(x11)
                 └─ udef_q(x11,RSTR,BODY)
                                      └─ _lift_v_cause(e2,x3,x11)
```

... and finally Phase 3 runs the extracted numeric constraints over the Phase 1 solutions to generate the final solution groups. 

Here's the full algorithm all in one place:

> Phase 0: Setup
> 1. Start with a well-formed MRS Tree
> 2. Determine the list of `x` variables in the tree and the order they will be evaluated in
> 3. Determine the constraints placed on each `x` variable by predications that modify it.
> 4. Create a modified tree by:
>    - Removing adjective predications that added numeric constraints
>    - Changing quantifiers that added numeric constraints to `udef_q`
> 
> Phase 1: Solution Generation
> 
> 5. Generate the list of solutions to the modified tree using the approach described in the [previous section](https://blog.inductorsoftware.com/Perplexity/home/devhowto/devhowtoMRSSolverSets)
> 
> Phase 2: Group Generation
> 
> 6. For each possible combination of solutions from Phase 1: Walk the `x` variables in evaluation order. 
> 7. For each `x` variable: Count individuals in the solutions two different ways:
>    - Cumulatively: Total the variable individuals across all solutions
>    - Distributive/collectively: Group the individuals by the value of the previous variable in the order, and total individuals in this variable per previous value. If the totals are all the same, across all previous values, that is the count. If not, this count fails and has no value.
>      - If this is the first variable, there is no "previous value" to use in the "total per previous value" definition of distributive/collective. Therefore, the first can only be totalled cumulatively
> 8. If either count meets the variable constraints: it succeeds and the next variable in the order is tried
>    - If not: this group fails and the next group starts at step #5
> 9. If the end of the variables is reached and all succeeded, this is a valid solution group


### Example
That can be a lot to take in, so let's go through an example: "students lifted a table":
```
[ "students lifted a table"
  TOP: h0
  INDEX: e2 [ e SF: prop TENSE: past MOOD: indicative PROG: - PERF: - ]
  RELS: < [ udef_q<0:8> LBL: h4 ARG0: x3 [ x PERS: 3 NUM: pl IND: + ] RSTR: h5 BODY: h6 ]
          [ _student_n_of<0:8> LBL: h7 ARG0: x3 ARG1: i8 ]
          [ _lift_v_cause<9:15> LBL: h1 ARG0: e2 ARG1: x3 ARG2: x9 [ x PERS: 3 NUM: sg IND: + ] ]
          [ _a_q<16:17> LBL: h10 ARG0: x9 RSTR: h11 BODY: h12 ]
          [ _table_n_1<18:23> LBL: h13 ARG0: x9 ] >
  HCONS: < h0 qeq h1 h5 qeq h7 h11 qeq h13 > ]

            ┌────── _student_n_of(x3,i8)
udef_q(x3,RSTR,BODY)          ┌────── _table_n_1(x10)
                 └─ _a_q(x10,RSTR,BODY)
                                   └─ _lift_v_cause(e2,x3,x10)

Text Tree: udef_q(x3,_student_n_of(x3,i8),_a_q(x10,_table_n_1(x10),_lift_v_cause(e2,x3,x10)))
```

#### Phase 0: Setup
> - Start with a well-formed MRS Tree
> - Determine the list of `x` variables in the tree and the order they will be evaluated in
> - Determine the constraints placed on each `x` variable by predications that modify it.


Using the approach described above, the evaluation order of variables is [`x3`, `x10`] in a depth-first traversal and the found constraints for the variables are:

|`x3` (students)|`x10`(table)|
|---|---|
|`udef`: `between(1, inf)`| `_a_q`: `between(1, 1)`|
|`[NUM: pl]`: `between(2, inf)`| `[NUM: sg]`: `between(1, 1)` |

When simplified, they are:

|`x3` (students)|`x10`(table)|
|---|---|
|`between(2, inf)`| `between(1, 1)` |

> - Create a modified tree by:
>   - Removing adjective predications that added numeric constraints
>   - Changing quantifiers that added numeric constraints to `udef_q`


The modified tree is:

```
            ┌────── _student_n_of(x3,i8)
udef_q(x3,RSTR,BODY)             ┌────── _table_n_1(x10)
                 └─ udef_q(x10,RSTR,BODY)
                                      └─ _lift_v_cause(e2,x3,x10)
```

#### Phase 1: Solution Generation

> - Generate the list of solutions to the modified tree using the approach described in the [previous section](https://blog.inductorsoftware.com/Perplexity/home/devhowto/devhowtoMRSSolverSets)


Using a (unshown) world state, and using the approach described in the [previous section](https://blog.inductorsoftware.com/Perplexity/home/devhowto/devhowtoMRSSolverSets), the solutions to the modified tree are (let's say):
```
"students lifted a table"

Tree: udef_q(x3,_student_n_of(x3,i8),udef_q(x10,_table_n_1(x10),_lift_v_cause(e2,x3,x10)))

Solution 1: x3=[student1], x10=[table1]                     "student1 is lifting table1"
Solution 2: x3=[student2], x10=[table2]
Solution 3: x3=[student3], x10=[table3]
Solution 4: x3=[student3], x10=[table4]
Solution 5: x3=[student4], x10=[table5]
Solution 6: x3=[student4], x10=[table6]
Solution 7: x3=[student5,student6], x10=[table7]            "student5 and student6 [together] are lifting table7"
Solution 8: x3=[student5,student6], x10=[table8]
Solution 9: x3=[student7,student8], x10=[table9, table10]   "student7 and student8 [together] are lifting table9 and table10 [at the same time]"
Solution 10: x3=[student9], x10=[table11, table12]          "student9 is lifting table11 and table12 [at the same time]"
Solution 11: x3=[student10,student11], x10=[table13]
Solution 12: x3=[student12], x10=[table14]
```

#### Phase 2: Group Generation
> 6. For each possible combination of solutions from Phase 1: Walk the `x` variables in evaluation order. 


Start by generating (as yet untested) groups that are all combinations of the above solutions. These may or may not be solution groups, we don't know yet. We need to test each one:

```
Group 1:
  Solution 1: x3=[student1], x10=[table1]                     "student1 is lifting table1"

Group 2:
  Solution 1: x3=[student1], x10=[table1]                     "student1 is lifting table1"
  Solution 2: x3=[student2], x10=[table2]

Group 3:
  Solution 1: x3=[student1], x10=[table1]                     "student1 is lifting table1"
  Solution 2: x3=[student2], x10=[table2]
  Solution 3: x3=[student3], x10=[table3]

... etc. (there are *many* more groups not listed)
```

> For each group:
> - For each `x` variable: Count individuals in the solutions two different ways:
>   - Cumulatively: Total the variable individuals across all solutions
>   - Distributive/collectively: Group the individuals by the value of the previous variable in the order, and total individuals in this variable per previous value. If the values are all the same, that is the count. If not, this count fails and has no value.
>     - If this is the first variable, there is no "previous value" to use in the "total per previous value" definition of distributive/collective. Therefore, the first can only be totalled cumulatively
> - If either count meets the variable constraints: it succeeds and the next variable in the order is tried
>   - If not: this group fails and the next group starts at step #5
> - If the end of the variables is reached and all succeeded, this is a valid solution group


Using the constraints we determined:

|`x3` (students)|`x10`(table)|
|---|---|
|`between(2, inf)`| `between(1, 1)` |

... let's analyze each group:
```
Group 1:
  Solution 1: x3=[student1], x10=[table1]                     "student1 is lifting table1"
```

`x3` is the first variable so we only do the cumulative count for it: `cumulative_count=1`. The constraint on `x3` is `between(2, inf)`. Thus: this group fails.

```
Group 2:
  Solution 1: x3=[student1], x10=[table1]                     "student1 is lifting table1"
  Solution 2: x3=[student2], x10=[table2]
```
`x3` is the first variable so we only do the cumulative count for it: `cumulative_count=2` which passes the constraint `between(2, inf)`. Try the next variable.  

`x10` gets both kinds of count: 
- `cumulative_count=2`. This fails the `between(1, 1)` constraint, but we have one more try...
- `dist_coll_count(student1)=1`, `dist_coll_count(student2)=1`. Both counts are the same so `dist_coll_count=1` The constraint on `x10` is `between(1, 1)`. Thus: this variable succeeds.

There are no more variables, thus this group is an answer: a *distributive* answer.

etc. 

All of the groups that succeed are solution groups and will be valid collective, distributive or cumulative readings of the phrase in that world.

There are a couple of subtleties that need to be address with this algorithm. Namely the special handling of "which" and "the". That is described in the next section.

Last update: 2023-04-27 by EricZinda [[edit](https://github.com/EricZinda/Perplexity/edit/main/docs/devhowto/devhowtoMRSSolverSolutionGroupsAlgorithm.md)]{% endraw %}