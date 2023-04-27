## Solution Group Algorithm
As described in the [previous section](devhowtoMRSSolverSolutionGroups), the only way to represent the semantics of cumulative and distributive readings of a sentence like:

~~~
students lifted a table

formula: student(x3), table(x10), lift(x3, x10)
scoped formula: scope(x3, [student(x3), scope(x10, [table(y), lift(x3, x10)])])
~~~

... is to have the solver create groups of solutions (called "solution groups") that are the "real" solutions. This section describes how.

The approach is to generate the solutions exactly like we've been doing so far, but add a second "grouping pass" to the solver. This grouping pass will find the groups of solutions that represent actually answers.

Groups are created that meet all the *numeric constraints* that the words in the phrase put on the  variables. For example, for "students lifted a table":
- "students ..." is plural, which means the contraint is: `count(students) > 2`
- "... a table" means the constraint is: `count(tables) = 1`
- etc.

If we simply return all groups where `count(students) > 2` and `count(tables) = 1`, we will get a bunch of valid groups, but miss all of those that use a "per previous value" interpretation. So, we'll miss the distributive ones. To get them all, we need to also count "per previous value". So, here's the full algorithm:
>1. Determine the order variables appear when evaluating the tree.
>2. Walk them in order. For each variable: count individuals in the solutions two different ways:
>    - cumulatively: total the variable individuals across all rows
>    - distributive/collectively: Group the individuals by the value of the previous variable in the order, and do the total per previous value.
>        - If this is the first variable: there is no "previous value" to use in the `total per previous value` definition of coll and dist. Therefore, the first can only be totalled as cumulative. 
>3. If either "count" meets the variable constraint, it succeeds and the next variable in the order is tried. If not, this group fails.
>4. If the end is reached and all succeeded, this is a valid solution group.

To get the groups that should be checked, we (you guessed it...) try every combination of solutions from the first pass. We will end this entire section with ways of efficiently doing this, but we'll start with the simplistic approach, which can be quite expensive: try all `(2^n - 1)` combinations as described in the previous section. 

Figuring out what the contraints are on variables is a longer story, which the next few sections will cover.

### Variable Constraints
Notice that every variable in an MRS has *some kind of* count constraint applied to it, even if implied. We can model them all using a `between` (inclusive) constraint with a lower bound and an upper bound (which could be "inf" meaning "infinity"), like this: `between(min, max)`.

For "students lifted a table":
- "students ..." is plural, which means: `between(2, inf)`
- "... a table" means: `between(1, 1)` (i.e. exactly 1)

For "which file is under 2 tables?":
- "... file ..." is singular, which means: `between(1, 1)`
- "... 2 tables ..." specifies two, so: `between(2, 2)`

`between(1, inf)` is the default constraint meaning: "anything". Variables with no other constraint get this one. Variables that have only the default constraint are not included in the list of variables to process. 

In that way, we can create a `between()` constraint for every variable and decide which can be ignored.


### Advanced Variable constraints: more than one constraint
For "the lawyers came to both houses":
- "the" means 1, lawyers means many

For "the 2 lawyers came to both houses":

"which students" is tricky: equivalent to "tell me any student that...
which students aced the exam - answering one student is OK
which files are in a folder? Should it return 2 files from one folder and a singular one from another?

### Determining Constraints From the MRS
Any predications that constrains numerically.
The pl/sg property.



### Example
Let's just start with a partial list of solutions to the formula for "students lifted a table" in an unspecified world state:
~~~
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
~~~

The order of variables is [`x3`, `x10`]

Constraints for `x3`:
- `x3` has the `[NUM: pl]` property: `between(2, inf)`
- `x3` has the `udef_q()` quantifier: `between(1, inf)`

Constraints for `x10`:
- `x10` has the `[NUM: sg]` property: `between(1, 1)`
- `x10` has the `_a_q` quantifier: `between(1, 1)`

~~~
"students lifted a table"

formula: student(x3), table(x10), lift(x3, x10)
scoped formula: scope(x3, [student(x3), scope(x10, [table(y), lift(x3, x10)])])

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
~~~

The unoptimized solver will generate all combinations of these solutions, like this partial list:

~~~
Solution 1: x3=[student1], x10=[table1]                     "student1 is lifting table1"

Solution 1: x3=[student1], x10=[table1]                     "student1 is lifting table1"
Solution 2: x3=[student2], x10=[table2]

Solution 1: x3=[student1], x10=[table1]                     "student1 is lifting table1"
Solution 2: x3=[student2], x10=[table2]
Solution 3: x3=[student3], x10=[table3]

... etc. (there are *many* more solutions not listed)
~~~

... and test each one to see if it represents a distributive, collective or cumulative solution.  Here are the definitions again from the previous section:

> For: "`M` Students lifting `N` Tables":
> 
> *The distributive reading*: "Two students [separately] lifted two tables [each]"
> - Students are grouped *distributively* into subgroups, which means:
>   - 2 or more subgroups
>   - Every student is in exactly one subgroup
>   - The total of students across the subgroups must add up to `M`.
> - Tables: Each student subgroup must be together (if the subgroup contains more than one student) lifting exactly `N` tables.
> 
> *The collective reading*: "Two students [together] lifted two tables [at the same time]"
>   - Students are grouped *collectively*, which means:
>   - Exactly 1 "subgroup" that contains the entire set of students.
> - Tables: Identical to the distributive reading, but using just one "subgroup" that contains everyone.
> 
> *The cumulative reading*: "One student lifted one table and another student lifted a different table"
> - Students: Identical to the distributive reading.
> - Tables: The total of tables across all subgroups *adds up* to `M`.

If the solution group being considered matches one of those rules then it is a "solution group" and represents one of the actual answers to the problem.




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