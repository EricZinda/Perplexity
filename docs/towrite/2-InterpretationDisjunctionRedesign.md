## Summary
A phrase generates at least one MRS. 

That MRS can generate at least one scope-resolved MRS.

Each predication in that scope-resolved MRS might have multiple, alternative, interpretations (represented by actual Python functions). All combinations of all the interpretations of the predications in the MRS must be tried to investigate all possible solutions.

A given interpretation of a predication might, itself, generate independent assignments that make sense together, but not interleaved with other sets of assignments (i.e. disjunctions) based on the values of the arguments.  These also need to be tried in all combinations.

Finally, a set of solutions that have chosen a particular set of assignment sets for every predication interpretation AND for every disjunction alternative from a predication, constitute a self-consistent set of solutions. This can go through phase 2 as a unit, but, again, cannot be interleaved with solutions from other interpretations.

Errors: Errors need to be tracked for each complete interpretation of the tree. Complete meaning: a view of a tree that has chosen interpretations for all predications AND chosen disjunction alternatives. If it fails, it needs to be identified as an interpretation that failed and be able to return a unique error for the failure.

If they all fail, each interpretation record that was generated can be inspected to return the best error.

## Phase 1
Phase 1 generates a set of local (i.e. true for only the MRS local constraints) solutions that contain variable assignments from only one complete interpretation of each predication. This is called a `solution set` and is the output of Phase 1. Here's how these are found:

That scope-resolved MRS tree can generate, statically (i.e. before execution), at least one `static interpretation` which is a selection of alternative interpretations of the predications within it. The predication interpretations are defined by actual Python function implementations of the predication.  Each concrete function represents an *alternative* interpretation. All combinations of `static interpretations` for each predication must be built into trees and then solved *on their own*, for every possible tree, to fully search for all possible meanings.

Each `static interpretation tree` may further generate one or more `disjunction trees` if the `static interpretation tree` has interpretations within it that are `disjunction predications`. A `disjunction predication` is a predication that can itself generate sets of values that belong together, but cannot be interleaved. They are different interpretations. They thus generate further *alternatives*, but, crucially, they cannot be known beforehand as they depend on the values of the arguments passed in, and the set of these values is not known beforehand. Just like `static interpretations`, all combinations of `disjunction interpretations` must be tried to fully search the tree for meaning. But, because the alternatives can only be known at runtime, they can't just be put together and tried in all combinations by the engine. They have to be discovered by evaluating the tree and allowing the depth first algorithm to explore them.

### Creating a disjunction
Because these must be created at runtime, by yielding the `DisjunctionValue(lineage, object)` class when using predicate helper functions like `combinatorial_predication_1`

### Evaluating the tree
It is the job of the disjunction predication to record the fact that it is in fact yielding disjunction alternatives. There are a few rules:
- If it *ever* is going to yield a disjunction, it must always do so
  - TODO: Is this really necessary?
- It has to give a unique identifier (called a `lineage`) to every different set of disjunction values that it produces.  Values that share the same lineage are treated as part of the same `disjunction interpretation`

To indicate that a predication has created a disjunction variant, it modifies the "tree_lineage" variable in the state object by adding a new `.predication_id@variant_id` at the end. This forms a long string that indicates, at any point in the tree execution, which dynamically created variant is being evaluated. This is done automatically by the system when a `DisjunctionValue` object is yielded to a helper function like `combinatorial_predication_1`.

Let's imagine we are evaluating a (fake) tree for "small boy is strong" `noun1_conj("boy", x1), adj1("small", x1), adj2_conj("strong", x1)`.
- `noun1_conj` and `adj2_conj` create disjunction variants, `adj1` does not.
- `adj1` is evaluated between the two disjunction variant functions

This could produce the following lineage on the state at the end at either successful or failed evaluation:

0: .1@1         (failed at `adj1` because `x1` contained a large boy)
1: .1@1.3@1     (succeeded)
2: .1@1         (failed at `adj1` because `x1` contained a different large boy)
3: .1@1.3@1     (succeeded)
4: .1@1.3@2     (succeeded)
5: .1@2         (failed at `adj1` because `x1` contained a different large boy)
6: .1@2.3@1     (succeeded) 
7: .1@2.3@2     (succeeded)

If we could evaluate these statically, they would be run as separate trees where only one sequence of lineages that starts with some value and then picks only one next value (and so on) would be seen:

Tree 1:
0: .1@1         (failed at `adj1` because `x1` contained a large boy)
1: .1@1.3@1     (succeeded)
2: .1@1         (failed at `adj1` because `x1` contained a different large boy)
3: .1@1.3@1     (succeeded)

Tree 2:
0: .1@1         (failed at `adj1` because `x1` contained a large boy)
2: .1@1         (failed at `adj1` because `x1` contained a different large boy)
4: .1@1.3@2     (succeeded)

Tree 3:
5: .1@2         (failed at `adj1` because `x1` contained a different large boy)
6: .1@2.3@1     (succeeded) 

Tree 4:
5: .1@2         (failed at `adj1` because `x1` contained a different large boy)
7: .1@2.3@2     (succeeded)

Note that:
- there are more results here since some of the nodes (like `.1@1` would happen for any lineage that starts with `1@1` and so would run again. Running them dynamically as in the first example doesn't require this
- The same lineage can be repeated after backtracking (as in 0 and 2 in the first listing) because either:
  - some predications don't produce disjunction alternatives (e.g. `adj1`), and things aren't backtracking all the way to a disjunction alternate to try a new disjunction
  OR
  - a disjunction interpretation may have multiple values, so when it backtracks it uses the same number

So, the goal is to be able to evaluate the tree like the first example, but interpret it like the second example so that we can follow the basic model we are trying to perform, even in the face of dynamically adding new predications at runtime.

### Solutions
Let's start with some facts we know to be true:

1. Solutions with identical lineages are all from the same `disjunction tree` and those are the only solutions from that tree
  - Because: all predications must have run (since this is a *solution*) and any predication that ever produces a disjunction must mark all values as a disjunction thus marking the lineage
2. A partial lineage is finished and will not be generated again when we see a new lineage where the prefix length that matches this prefix is different
  - Because: we are traversing a tree and the disjunction values are monotonically increasing

So, it is trivial just iterate through all the solutions from a tree and group each solution by its lineage.


### Failed Trees
But we also need to gather all the `disjunction interpretations` that had no solutions. For example, between these two solutions there could be `n` different failures for trees that never succeeded, and thus don't show up as solutions:

> solution0: .1@1         (failed at `adj1` because `x1` contained a large boy)
>   (always failed) .1@1.3@-1 
>   (always failed) .1@1.3@0
> solution1: .1@1.3@1     (succeeded)

We don't get the failure trees naturally because the solution iterator only returns *solutions*.

We need to decide when these trees are completed and won't be called again so we can return the failed trees. 

1. We do this by continuously updating a list of unique lineages we've seen to represent our best picture of the `disjunction interpretations` that occur from the base tree. The farther down the base tree we get and the more failures that get explored, the better our picture gets. Once the base tree has been completely run we know exactly what disjunction trees were created at this point in the world state, which is all we care about.
2. Furthermore, if we notice a new lineage that indicates a bunch of lineages are now finished (see fact 2 above), we know *they* won't get any additional processing, and we can return the ones that never fully succeeded as failed `disjunction interpretations`.
3. We can ignore any lineages that are prefixes of a longer lineage since that longer lineage represents a more complete exploration of the dynamic `disjunction interpretation` tree

We can do this by running code after every *successful* predication (since any and only successful predication can create a new lineage) which:
- Registers the lineage as "active"
- Deletes any active lineages which are prefixes of it (since the new one represents a truer, more complete exploration of the `disjunction interpretation`)
- Reports any lineages which this isn't a prefix of as "complete" if they had no solutions

At the very end we also need to complete any lineages that are still active since there will be no "next" lineage to complete them.

### Finding the Error for a Failed tree
When we report a failed tree (i.e. a tree that won't be run again and had no solutions) we need to record what error caused the failure. We need the error to be the "best" (deepest, etc) error that happened while conceptually executing *only the tree with this disjunction lineage in it*. The current way the tree is executed has two problems that prevent us from just looking at the context at its final failure point:

1. It conflates the errors from different trees since there is a single error context and different disjunction tree variants can be interleaved but still use that one context.
2.It clears the error when there is any solution, thus losing even the (potentially inaccurate) data we had

An example of the first problem is below. The error code for the first solution will be recorded in the context and the second one won't, since there will already be an error at predication index in the tree, but really there should be two different errors recorded since these are disjunction variants:

> solution6: .1@2.3@1     (failed) 
> solution7: .1@2.3@2     (failed)

The natural solution is to remember errors *by unique disjunction tree*. However, at the point of execution we may not know which tree a given lineage applies to.  For example:

> solution0: .1@1

is in two unique trees since it is early in execution:

> solution0: .1@1         (failed at `adj1` because `x1` contained a large boy)
> solution1: .1@1.3@1     (succeeded)
> solution2: .1@1         (failed at `adj1` because `x1` contained a different large boy)
> solution3: .1@1.3@1     (succeeded)

> solution0: .1@1         (failed at `adj1` because `x1` contained a large boy)
> solution2: .1@1         (failed at `adj1` because `x1` contained a different large boy)
> solution4: .1@1.3@2     (succeeded)

To fix this, we will modify `report_error` to pay attention to the current lineage and register its error with any "active lineage" that has this lineage as its prefix (including equality), using a special context kept for each. Because only successful predications can create new lineages, the "active lineage" list above will always have it available.

We also have to create the same behavior on other operations that change or access the error context like `clear_error`, `get_error`, `get_error_info` and `set_error_info`.

That way, we would have the "best" error for any given lineage.