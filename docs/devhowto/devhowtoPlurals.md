
# Algorithm for Dealing with Plurals in MRS
## Overview
A *really* brief summary of one possible approach for properly resolving plurals in an MRS against a world state is:

> The fully resolved tree for an MRS can be evaluated against a world state in two stages:
> 
> *Stage 1:* Remove all the numeric determiner semantics ("many", "2 or more", "all", "some", "the", etc.) from the fully-resolved tree and solve it. This involves literally removing the numeric *adjective* determiners and their modifiers (e.g. `card(2,e,x)` or `much-many_a(e8,x3)`) and converting the numeric *quantifier determiners* (e.g. `_all_q(x3,RSTR,BODY)` or `_the_q(x3,RSTR,BODY)`) to `udef_q`. This creates a set of "undetermined solutions".
> 
> *Stage 2:* Create groups out of the undetermined solutions that satisfy the first determiner and run each group recursively (left to right) through the rest of the numeric determiners in order. The groups that succeed are solutions.  Forward and reverse readings happen via different fully-resolved trees.

Below I walk through this in much more detail, with examples.

## Collective/Distributive/Cumulative Definitions
For “two firefighters carried two hoses”:

When referring to a fully-resolved tree (which means that forward and reverse readings with respect to word order are just different trees and aren’t included in the definition):

“The distributive reading”
- Firefighters: 2 or more subgroups, each of size > 0, where every individual in question is in exactly one group (the definition above).
- Hoses: All subgroups must have two hoses each. Individual hoses may be repeated in subgroups.

“The collective reading”
- Firefighters: Exactly 1 subgroup that contains the entire set of individuals in question
- Hoses: Identical to distributive

“The cumulative reading”
- Firefighters: Identical to distributive
- Hoses: The total of unique individual hoses across all subgroups adds up to two.

So:

Distributive and collective group the first variable differently, but do the same math problem across the group(s) for the second variable.
Cumulative does the same first variable grouping as distributive, but a different math problem across the groups for the second variable.


## Determiner Definitions
- A *numeric determiner* creates a numeric constraint on a particular `x` variable
- A *numeric adjective determiner* is an adjective that creates a numeric constraint on a particular `x` variable, such as `card(2,e,x)` or `much-many_a(e8,x3)`.
- A *numeric quantifier determiner* is a quantifier that creates a numeric constraint on a particular `x` variable, such as `_all_q(x3,RSTR,BODY)` or `_the_q(x3,RSTR,BODY)`

## Stage 1
Stage 1 is done by removing all the numeric determiner semantics from a fully-resolved MRS tree and then evaluating it. For example, here's a forward reading (with respect to word order) of: "some men are eating two pizzas":

~~~
_some_q(x3,_man_n_1(x3),udef_q(x10,[_pizza_n_1(x10), card(2,e14,x10)],_eat_v_1(e2,x3,x10)))
~~~

In stage 1, `_some_q` is converted to `udef_q` (which seems like the most "NOOP" quantifier) and `card` is removed, like this:

~~~
udef_q(x3,_man_n_1(x3),udef_q(x10,_pizza_n_1(x10),_eat_v_1(e2,x3,x10)))
~~~

... which gets you something like "men are eating pizzas", but, I evaluate it ignoring the plural as well, so, it is really more like: "man/men is/are eating pizza(s)".  Solving that gives you a flat set of solutions that I'm calling "undetermined solutions". 

For example, imagine a world where a bunch of men are eating pizzas and we solve the "undetermined MRS" above for all values of `x3` and `x10`. Below, solutions are represented as assignments of values (which are always a set but can be a set of 1) to variables in the MRS that make it true. The set of variable assignments in 1 solution makes the MRS true, and the MRS is true for each of the solutions. Within a solution: If a variable is assigned a set of > 1, it means those individuals are doing something "together". 

Using that approach, here is a list of all the true states of the "undetermined MRS" in this world, found by resolving the tree (how *that* is done is described elsewhere, to be written):
~~~
Solution 1: x3=[man1], x10=[pizza1]                 "man1 is eating pizza1"
Solution 2: x3=[man2], x10=[pizza2]
Solution 3: x3=[man3], x10=[pizza3]
Solution 4: x3=[man3], x10=[pizza4]
Solution 5: x3=[man4], x10=[pizza5]
Solution 6: x3=[man4], x10=[pizza6]
Solution 7: x3=[man5,man6], x10=[pizza7]            "man5 and man6, together, are eating pizza7"
Solution 8: x3=[man5,man6], x10=[pizza8]
Solution 9: x3=[man7,man8], x10=[pizza9, pizza10]   "man7 and man8, together are eating pizza9 and pizza10 at the same time"
Solution 10: x3=[man9], x10=[pizza11, pizza12]      "man9 is eating pizza11 and pizza12 at the same time"
Solution 11: x3=[man10,man11], x10=[pizza13]
Solution 12: x3=[man12], x10=[pizza14]
~~~

At the end of Stage 1, we have just the flat list of undetermined solutions.
## Stage 2
Summary: Stage 2 recursively (left to right in execution order) runs each numeric determiner that has been removed over a group of solutions generated by the previous determiner. 
- The first determiner creates a "determiner group" for every combination of solutions that satisfy it and sends each determiner group forward to the next.
- The next determiner checks to see if the entire provided determiner group satisfies it. If so, it passes it forward to the next.
- etc.
- Any groups that make it all the way to the end are a valid interpretation

So, the first determiner, `some_q(x3, ...)`, has the special job of creating all the determiner groups that will be tested by the rest of the determiners. It groups the incoming initial solutions (the flat list of undetermined solutions, above) into *all possible groups* where there are, lets say, at least two `x3` individuals (meaning "some >= 2"), like this:

~~~
some_q(x3, ...) determiner groups
-------------------------------

Group 1: (created since 2 men)
    x3=[man1]:
        Solution 1: x3=[man1], x10=[pizza1]
    x3=[man2]:
        Solution 2: x3=[man2], x10=[pizza2]

Group 2: (created since 2 men - only unique values matter)
    x3=[man3]:
        Solution 3: x3=[man3], x10=[pizza3]
        Solution 4: x3=[man3], x10=[pizza4]
    x3=[man4]:
        Solution 5: x3=[man4], x10=[pizza5]
        Solution 6: x3=[man4], x10=[pizza6]

Group 3: (created since 2 men - unique *individuals* are counted)
    x3=[man5,man6]:
        Solution 7: x3=[man5,man6], x10=[pizza7]
        Solution 8: x3=[man5,man6], x10=[pizza8]
    
Group 4: (created since 3 men is still "some")
    x3=[man7,man8]:
        Solution 9: x3=[man7,man8], x10=[pizza9, pizza10]
    x3=[man9]:
        Solution 10: x3=[man9], x10=[pizza11, pizza12]

Group 5: (created since 3 men is still "some")
    x3=[man10,man11]:
        Solution 11: x3=[man10,man11], x10=[pizza13]
    x3=[man12]:
        Solution 12: x3=[man12], x10=[pizza14]

... etc. (there are *many* more solutions not listed)
~~~

Then, stage 2 tests the next determiner against each generated determiner group. Now that we're going beyond the initial determiner, stage 2 evaluation no longer generates new groups, it just tests them. It also has to use one additional test to find all the collective, distributive and cumulative answers. So, there are *two* tests used by every determiner beyond the first.

### Test 1
Test 1 is the new one (not used by the initial determiner) and tests if the total *for each previous determiner variable value* satisfies its determiner. It will find distributive answers (among others).

So, If you take each incoming `some_q(x3, ...)` determiner group like `Group 1`, and evaluate `card(2,e14,x10)` against the solutions that go with unique *x3* values, you get these results:

~~~
Group 1: (FAIL: each unique x3 doesn't have 2 x10 pizzas)
    x3=[man1]:
        Solution 1: x3=[man1], x10=[pizza1]
    x3=[man2]:
        Solution 2: x3=[man2], x10=[pizza2]

Group 2: (distributive over x3: each unique x3 has 2 x10 pizzas)
    x3=[man3]:
        Solution 3: x3=[man3], x10=[pizza3]
        Solution 4: x3=[man3], x10=[pizza4]
    x3=[man4]:
        Solution 5: x3=[man4], x10=[pizza5]
        Solution 6: x3=[man4], x10=[pizza6]

Group 3: (collective over x3: each unique x3 has 2 x10 pizzas)
    x3=[man5,man6]:
        Solution 7: x3=[man5,man6], x10=[pizza7]
        Solution 8: x3=[man5,man6], x10=[pizza8]
    
Group 4: (distributive over x3: each unique x3 has 2 x10 pizzas)
    x3=[man7,man8]:
        Solution 9: x3=[man7,man8], x10=[pizza9, pizza10]
    x3=[man9]:
        Solution 10: x3=[man9], x10=[pizza11, pizza12]

Group 5: (FAIL: each unique x3 doesn't have 2 x10 pizzas)
    x3=[man10,man11]:
        Solution 11: x3=[man10,man11], x10=[pizza13]
    x3=[man12]:
        Solution 12: x3=[man12], x10=[pizza14]
~~~

Test 1 succeeds when the count of individuals in its characteristic variable per previous determiner group *x3 subset* satisfy its determiner. Thus, in general, it finds the following readings over the previous quantifier:
- *All* `distributive readings` (e.g. `Group 2`) since it checks the "per `x3` total", and when all the `x3` values are a single individual, that's the definition of distributive.
- *All* `collective readings` (e.g. `Group 3`) since it will test a "per `x3` total" for a single `x3` set > 1 
- *Some tiny number of technically* `cumulative readings` where the `x10` individuals are the same for each `x3`

### Test 2
Test 2 is the test used by the initial determiner and is the "cumulative" test: it tests if the total *across the whole determiner group* satisfies its determiner. 

For Test 2: If you take `Group 1` from `some_q(x3, ...)` and test the `card(2,e14,x10)` determiner *across the whole group* (i.e. *ignoring* its `x3` subsets), you've done one group. If you do them all, you'll get:
~~~
Group 1: (cumulative over x3: count of all unique x10 is 2)
    Solution 1: x3=[man1], x10=[pizza1]
    Solution 2: x3=[man2], x10=[pizza2]

Group 2: (FAIL: count of all unique x10 is > 2)
    Solution 3: x3=[man3], x10=[pizza3]
    Solution 4: x3=[man3], x10=[pizza4]
    Solution 5: x3=[man4], x10=[pizza5]
    Solution 6: x3=[man4], x10=[pizza6]

Group 3: (collective over x3: count of all unique x10 is 2)
    Solution 7: x3=[man5,man6], x10=[pizza7]
    Solution 8: x3=[man5,man6], x10=[pizza8]
    
Group 4: (FAIL: count of all unique x10 is > 2)
    Solution 9: x3=[man7,man8], x10=[pizza9, pizza10]
    Solution 10: x3=[man9], x10=[pizza11, pizza12]

Group 5: (cumulative over x3: count of all unique x10 is 2)
    Solution 11: x3=[man10,man11], x10=[pizza13]
    Solution 12: x3=[man12], x10=[pizza14]
~~~

Test 2 finds the following readings over the previous quantifier:
- *All* `collective readings` (e.g. `Group 3`). In a collective reading like `Group 3`, there is only one value of `x3` (that happens to be a set > 1) and thus there is no distinction between "per `x3` value" and "across all `x3` values", so this test duplicates all collective groups from Test 1.
- *All* `cumulative readings` (e.g. `Group1` and `Group 5`).
- *Some (tiny number of technically)* `distributive readings`. Namely, ones where each `x3` meets the determiner test *with the exact same values*. These will be duplicates of Test 1.

Note that, if you limit test 2 to only groups that have exactly 1 unique `x3` assignment, then the only duplication that happens is the distributive one listed, with no loss of generality.

After running through both Phase 1 and Phase 2 for each determiner, in order, the groups that remain represent all the collective, distributive and cumulative solutions, with some duplication.