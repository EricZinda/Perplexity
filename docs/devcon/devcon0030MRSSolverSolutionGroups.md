## Collective and Distributive Readings
If we change the "students lifted a table" example from the [previous section](devcon0020MRSSolverSets) slightly, we can uncover another layer of meaning we need to represent in the solver. 

For example:

~~~
Two students lifted one table
~~~
...*could* mean: 

~~~
1. Two students [together] lifted one table [at the same time]
2. Two students [separately] lifted one [different] table
~~~

So, in addition to representing things working together or separately by using sets as we did in the [previous section](devcon0020MRSSolverSet), we need to deal with the fact that terms representing sets in language create a new layer of ambiguity: it isn't always clear if you are talking about the whole group of "two students" working together, or subsets of the group working separately. The solver needs to be able to find either solution properly.

Let's start by defining some linguistics terminology to help us talk about the different ways students are grouped in the interpretations above:
- A group of items operating together are called *collective*: #1 has collective students.
- A group of items where different subsets of the group operate "separately" are called *distributive*: #2 has distributive students. 

Now, notice that there is more going on than just a different grouping of students. Reading #1 above describes a single table being lifted, whereas reading #2 has two ... but they both come out of a phrase that says "... lifted *one* table". This happens because the phrases are both being interpreted as "one table [*per group*]". #1 has a single group (of two students), #2 has two groups (of one student). 

So, to discuss the whole phenomena across the phrase (and not just how the students are being grouped), the term "reading" is used in conjunction with collective or distributive. As in: "#1 is a collective *reading*" and "#2 is a distributive *reading*". Defining these a bit more rigorously:

> For: "`M` students lifting `N` tables":
> 
> To be the distributive reading:
> - Students: must be grouped *distributively* into subgroups, which means:
>   - 2 or more subgroups
>   - Every student is in exactly one subgroup
>   - The total of students across the subgroups must add up to `M`
> - Tables: Each student subgroup with more than one student must be together lifting exactly `N` tables
> 
> To be the collective reading:
>   - Students must be grouped *collectively*, which means:
>     - Exactly 1 "subgroup" that contains the entire set of students
> - Tables: Identical to the distributive reading, but using just one "subgroup" that contains everyone

### Cumulative Readings
If we change the phrase again just slightly to allow for more than one table:

~~~
Two students lifted two tables
~~~

... language lets in one more possible interpretation ... by counting *total* tables (not *per group*):

~~~
3. One student lifted one table and another student lifted a different table.
~~~

This interpretation distributively groups the students, but *counts the tables differently*.  This can be confusing, so let's do the three definitions at once:

> For: "`M` students lifting `N` tables":
>  
> *The distributive reading*: "Two students [separately] lifted two tables [each]"
> - Students: must be grouped *distributively* into subgroups, which means:
>   - 2 or more subgroups
>   - Every student is in exactly one subgroup
>   - The total of students across the subgroups must add up to `M`
> - Tables: Each student subgroup with more than one student must be together lifting exactly `N` tables
> 
> *The collective reading*: "Two students [together] lifted two tables [at the same time]"
>   - Students must be grouped *collectively*, which means:
>     - Exactly 1 "subgroup" that contains the entire set of students
> - Tables: Identical to the distributive reading, but using just one "subgroup" that contains everyone
> 
> *The cumulative reading*: "One student lifted one table and another student lifted a different table"
> - Students: Identical to the distributive reading.
> - Tables: The total of tables across all subgroups must *add up* to `M`

Note how the math for the cumulative reading is different than the math for collective and distributive readings. Collective and distributive readings require `M` tables *per student subgroup*, whereas cumulative requires `M` tables, total, *across all student subgroups*.

It is important to note that this is not some DELPH-IN feature or artifact, this is how human language works. We are just trying to emulate it by building an algorithm that processes phrases like a human would.

### Algorithm Fixes for Collective, Distributive and Cumulative
The backtracking algorithm we've defined in previous sections will actually find the collective, distributive, and cumulative solutions to an MRS, if they exist, because it will find *all* solutions to the MRS.  But, there is a problem with the way we're currently defining "solution". To see why, let's bring back the three readings:

> "two students lifted two tables"
> 1. *The distributive reading*: "Two students [separately] lifted two tables [each]"
> 2. *The collective reading*: "Two students [together] lifted two tables [at the same time]"
> 3. *The cumulative reading*: "One student lifted one table and another student lifted a different table"

Note that situations #1 and #3 are only properly represented by a *group* of solutions as we've defined "solution": 

> Solution: Assignments of single set-based values to all variables that make the MRS `true` 

There isn't a way to represent #1 and #3 as a *single* solution (i.e. a single set of variable assignments) in this model. For example, look at #1: Since each student is lifting a different "two tables", it will take 4 solutions to capture the meaning:

~~~
x=[student1], y=[table1]
x=[student1], y=[table2]
x=[student2], y=[table3]
x=[student2], y=[table4]
~~~

Even if each student is lifting two tables *at the same time*, we still need two solutions:

~~~
x=[student1], y=[table1, table2]
x=[student2], y=[table3, table4]
~~~

We need to represent 2 students operating *separately* which means they must be in their own set, and variables can only be assigned one set-based value in a solution. Thus, distributive or cumulative scenarios will require a *group* of solutions to represent the answer. This is the change we need to make to the solver.

## Solution Groups
We can address the problem by changing our solver algorithm to generate *solution groups*, and then start interpreting a *group* of solutions as a complete answer. Let's go through the different scenarios using the grouping approach.

First, a collective reading scenario:
~~~
formula: student(x), table(y), lift(x, y)
scoped formula: scope(x, [student(x), scope(y, [table(y), lift(x, y)])])

world individuals:
  alice
  bob
  table1
  table2

world facts:
  [alice, bob] lift [table1, table2]
~~~

The *solution group* that represents this can actually be represented by a single solution in the group:

> Solution Group for *the collective reading*: "Two students [together] lifted two tables [at the same time]"
> 
> |solution|interpretation|
> |---|---|
> |x=[alice, bob], y=[table1, table2]| Alice and Bob [together] lifted two tables [at the same time]|

Next, a distributive reading scenario:

~~~
formula: student(x), table(y), lift(x, y)
scoped formula: scope(x, [student(x), scope(y, [table(y), lift(x, y)])])

world individuals:
  alice
  bob
  table1
  table2
  table3
  table4

world facts:
  [alice] lift [table1]
  [alice] lift [table2]
  [bob] lift [table3]
  [bob] lift [table4]
~~~

The *solution group* that represents this requires multiple solutions in the group:

> Solution Group for *the distributive reading*: "Two students [separately] lifted two tables [each]"
> 
> |solution|interpretation|
> |---|---|
> |x=[alice], y=[table1]| Alice [separately] lifted one table|
> |x=[alice], y=[table2]| Alice [separately] lifted another table|
> |x=[bob], y=[table3]| Bob [separately] lifted one table|
> |x=[bob], y=[table4]| Bob [separately] lifted another table|

Finally, a cumulative reading:
~~~
formula: student(x), table(y), lift(x, y)
scoped formula: scope(x, [student(x), scope(y, [table(y), lift(x, y)])])

world individuals:
  alice
  bob
  table1
  table2

world facts:
  [alice] lift [table1]
  [bob] lift [table2]
~~~

The *solution group* that represents this also requires multiple solutions in the group:

> Solution Group for *The cumulative reading*: "One student lifted one table and another student lifted a different table"
> 
> |solution|interpretation|
> |---|---|
> |x=[alice], y=[table1]| Alice [separately] lifted one table|
> |x=[bob], y=[table2]| Bob [separately] lifted one table|


## Summary
With the addition of solution groups, the solver can now properly represent the meaning of plural sentences across collective, distributive and cumulative readings.

[The appendices](devcon0040MRSSolverSolutionGroupsAlgorithm) have a description of how the solver can actually *do* the grouping and arrive at those answers.

TODO: talk about forward and reverse readings with respect to word order being a function of the tree that is generated.

