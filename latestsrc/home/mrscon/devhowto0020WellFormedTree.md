{% raw %}## Building Well-Formed MRS Trees
> This section is designed to help application developers understand how to build well-formed trees from MRS documents. To understand this section, first make sure you have a [basic understanding of the MRS format](https://blog.inductorsoftware.com/Perplexity/home/mrscon/devhowto0010MRS) or, for a more academic or linguistic approach, explore [Minimal Recursion Semantics: An Introduction](https://www.cl.cam.ac.uk/~aac10/papers/mrs.pdf).  

Let's use the sentence "every book is in a cave" as an example. If the phrase is parsed with [the ACE parser](http://sweaglesw.org/linguistics/ace/), you get an MRS document like this:

```
[ TOP: h0
INDEX: e2
RELS: < 
[ _a_q LBL: h10 ARG0: x9 [ x PERS: 3 NUM: sg IND: + ] RSTR: h11 BODY: h12 ]
[ _cave_n_1 LBL: h13 ARG0: x9 [ x PERS: 3 NUM: sg IND: + ] ]
[ _every_q LBL: h4 ARG0: x3 [ x PERS: 3 NUM: sg IND: + ] RSTR: h5 BODY: h6 ]
[ _book_n_of LBL: h7 ARG0: x3 [ x PERS: 3 NUM: sg IND: + ] ARG1: i8 ]
[ _in_p_loc LBL: h1 ARG0: e2 [ e SF: prop TENSE: pres MOOD: indicative PROG: - PERF: - ] ARG1: x3 ARG2: x9 ]
>
HCONS: < h0 qeq h1 h5 qeq h7 h11 qeq h13 > ]
```
Our goal is to eventually "solve" the MRS by finding values for its MRS variables such that it is "true". When complete, these variables indicate what the speaker *meant* and allow us to *do* something about it.  

To resolve an MRS against a world state (a particular state of the world at a moment in time) and get *solutions* to it (meaning the set of MRS variable assignments that make it true) you need to turn it into a *well-formed MRS tree*. We will examine *how* shortly, but for now just know that a well-formed MRS tree has (among other things) nodes that are the predications from the MRS like `_every_q__xhh` and arcs that are links between the [*scopal arguments*](https://blog.inductorsoftware.com/Perplexity/home/mrscon/devhowto0010MRS) of the predications and other nodes, like this:

```
              ┌────── _book_n_of(x3,i8)
_every_q(x3,RSTR,BODY)          ┌────── _cave_n_1(x9)
                   └─ _a_q(x9,RSTR,BODY)
                                     └─ _in_p_loc(e2,x3,x9)
```

This tree represents *one interpretation* of "every book is in a cave", namely, "every book is in a (possibly different) cave". 

To "solve" this tree against a particular world state, you walk it in depth-first order: `every_q` is the starting, leftmost node. It starts by selecting a book on its upper branch, and then solves its lower branch with the selected book. This finds "a cave that the (selected) book is in". `every_q` does this for every book in the world state. If they all succeed (they must all succeed because the speaker said "every"), we have a solution to the MRS. Because `_every_q` chooses a book *and then* a cave that it is in, it allows a *different* cave to be selected for each book. This tree will be only true if every book is in a (possibly different) cave.

But this is only one interpretation. Another interpretation of the *same* MRS is: "all books are in the same exact cave". The speaker might have meant that interpretation, which is represented by this tree:

```
          ┌────── _cave_n_1(x9)
_a_q(x9,RSTR,BODY)              ┌────── _book_n_of(x3,i8)
               └─ _every_q(x3,RSTR,BODY)
                                     └─ _in_p_loc(e2,x3,x9)
```

When `a_q` is the leftmost node, it starts by selecting a cave on its upper branch, and then resolves its lower branch with that selection, making sure that "every book is in the (selected) cave". This will only be true if there is (at least one) cave that every book is in.

> Don't worry if you don't completely understand how the solutions are obtained yet.  The point is that there are different interpretations for the same MRS, represented by different trees. The rest of the tutorial will work through how these get solved.

Both of these trees are represented by the same MRS document. The MRS structure is said to be *underspecified*, meaning that a single MRS document allows multiple interpretations. 

Here's the MRS for "Every book is in a cave" again, so we can see how:

```
[ TOP: h0
INDEX: e2
RELS: < 
[ _a_q LBL: h10 ARG0: x9 [ x PERS: 3 NUM: sg IND: + ] RSTR: h11 BODY: h12 ]
[ _cave_n_1 LBL: h13 ARG0: x9 [ x PERS: 3 NUM: sg IND: + ] ]
[ _every_q LBL: h4 ARG0: x3 [ x PERS: 3 NUM: sg IND: + ] RSTR: h5 BODY: h6 ]
[ _book_n_of LBL: h7 ARG0: x3 [ x PERS: 3 NUM: sg IND: + ] ARG1: i8 ]
[ _in_p_loc LBL: h1 ARG0: e2 [ e SF: prop TENSE: pres MOOD: indicative PROG: - PERF: - ] ARG1: x3 ARG2: x9 ]
>
HCONS: < h0 qeq h1 h5 qeq h7 h11 qeq h13 > ]
```
The MRS is a flat list of predications so that it avoids building a single tree which would "lock in" one interpretation.  How it does this is described in detail next, but in summary: It leaves "holes" using scopal (`h`) arguments for various predications and provides constraints (the `HCONS`) for plugging the predications together "legally".  If you combine the predications by following the constraints (among other things), you'll end up with a "well-formed MRS tree" which defines one valid interpretation of the sentence. If you build all the well-formed trees, you have all the possible interpretations.

This interpretation is what we need in order to eventually "solve" the phrase for the variables it contains. This topic describes how to build that tree.

## Holes and Constraints
"Holes" are `h` arguments in a predication that refer to a [predicate label](https://blog.inductorsoftware.com/Perplexity/home/mrscon/devhowto0010MRS) that is *not* defined. In the above MRS, `h0` (the `TOP:`), `h11`, `h12`, `h5`, and `h6` are all "holes" since none of the predicates use those names as their `LBL`.

The `HCONS` section of the MRS puts *CONS*traints on which placement of *H*andles in holes is valid.

The only kind of constraint used in "modern" MRS is a `qeq` constraint.  A `qeq` constraint always relates a hole to a (non-hole) handle and says that the handle must be a direct or eventual child in the tree. Furthermore, if not directly connected, the only things between the hole and the handle can be [quantifiers](https://blog.inductorsoftware.com/Perplexity/home/mrscon/devhowto0010MRS).  

Said a different way: 

> A qeq constraint of `h0 qeq h1` (as in the above example) says that the direct path in the final tree from `h0` to `h1` must only contain quantifier predicates, but can contain as many as you want, as long as they don't violate other constraints.

So, in this MRS:

```
[ TOP: h0
INDEX: e2
RELS: < 
[ _a_q LBL: h10 ARG0: x9 [ x PERS: 3 NUM: sg IND: + ] RSTR: h11 BODY: h12 ]
[ _cave_n_1 LBL: h13 ARG0: x9 [ x PERS: 3 NUM: sg IND: + ] ]
[ _every_q LBL: h4 ARG0: x3 [ x PERS: 3 NUM: sg IND: + ] RSTR: h5 BODY: h6 ]
[ _book_n_of LBL: h7 ARG0: x3 [ x PERS: 3 NUM: sg IND: + ] ARG1: i8 ]
[ _in_p_loc LBL: h1 ARG0: e2 [ e SF: prop TENSE: pres MOOD: indicative PROG: - PERF: - ] ARG1: x3 ARG2: x9 ]
>
HCONS: < h0 qeq h1 h5 qeq h7 h11 qeq h13 > ]
```

`h1` is the LBL of the `_in_p_loc__exx` predicate. Given the qeq constraint of `h0 qeq h1`, it would be perfectly valid to assign `h0 = h1` (meaning put the predication labelled by `h1` in the `h0` hole) since the path from `h0` to `h1` is direct. 

Again, given the qeq constraint of `h0 qeq h1`: You could alternatively assign `h0 = h4` (`h0` is the "hole" at the top of the tree, `h4` is the label for `_every_q`), and `h6 = h1` (`h6` is a "hole" in `_every_q`, `h1` is the label for `_in_p_loc`). With this configuration, `h0 qeq h1` is still valid because the path from `h0` to `h1` only includes the `every_q` quantifier and `h1` itself.

Once you fill *all* the holes with unique predications, and you follow all of the `qeq` constraints, you'll end up with a tree that is "scope-resolved", but not yet guaranteed to be "well-formed". There is one more rule to check.

## X Variable Scoping
All of the arguments that aren't handles in the MRS for `Every book is in a cave` except two (`e2` and `i8`) are `x` variables:

```
[ TOP: h0
INDEX: e2
RELS: < 
[ _a_q LBL: h10 ARG0: x9 [ x PERS: 3 NUM: sg IND: + ] RSTR: h11 BODY: h12 ]
[ _cave_n_1 LBL: h13 ARG0: x9 [ x PERS: 3 NUM: sg IND: + ] ]
[ _every_q LBL: h4 ARG0: x3 [ x PERS: 3 NUM: sg IND: + ] RSTR: h5 BODY: h6 ]
[ _book_n_of LBL: h7 ARG0: x3 [ x PERS: 3 NUM: sg IND: + ] ARG1: i8 ]
[ _in_p_loc LBL: h1 ARG0: e2 [ e SF: prop TENSE: pres MOOD: indicative PROG: - PERF: - ] ARG1: x3 ARG2: x9 ]
>
HCONS: < h0 qeq h1 h5 qeq h7 h11 qeq h13 > ]
```

The rules for MRS say that any variable in the MRS is "globally defined" (or "existentially qualified" in logic terms) for the whole structure *except* for `x` variables.  So, both `e2` and `i8` don't need any special handling, they are globally defined.

`x` variables, on the other hand, can *only* be defined by [quantifiers](https://blog.inductorsoftware.com/Perplexity/home/mrscon/devhowto0010MRS), and are *only* defined for the branches of the tree that are attached to the quantifier's scopal (`h`) arguments: `RSTR` and `BODY`.

So, while the predications can be in any order in the tree with respect to their `e`  (or `i` or `u` if it had them) arguments, the tree must be checked to make sure all of the `x` arguments have an eventual parent which is a quantifier which puts them in scope (i.e. has the `x` variable as its first argument: `ARG0`). This is an additional constraint that has to be checked to build a "well-formed" tree.

If the labels from the MRS are all in (exactly) one place, the built tree passes all `qeq` constraints, and the `x` variables are all properly scoped, then it is a "well-formed" tree that we can now attempt to solve.  That's what we're going for here.

## Resolving the tree
Finding ways to efficiently create these trees is an area of active research because natural language can easily create MRS structures that have a ton of holes.  `n` holes, in the worst case, can require `n!` checks to resolve, if done exhaustively.  So, an MRS structure with 12 holes (which is easy to generate) could require up to 480,000,000 checks before finding a valid solution if you just try every combination.  

To generate the well-formed trees, you could simply try all possible combinations of holes and labels, do the `qeq` and `x` scoping checks on each, and only keep the valid ones. This will only be practical for the simplest possible trees.

Another algorithm, the one we'll use in the tutorial, is able to prune the search space and works much faster.  The Python implementation can usually generate all trees for an MRS with 12 holes in around 1.5s (with some outliers being slower) on a 2013-era MacBook Pro.  This will be sufficient for the purposes of this tutorial.  Something like "put the diamond on the table where the safe is and the book is" generates MRS structures with up to 14 holes and could take up to 30 seconds to generate *all* the valid interpretations (1500+ valid interpretations in some cases!) for each MRS.  It turns out it is very rarely necessary to generate all the interpretations, but regardless: because it scales factorially, things slow down fast after 12 holes.

There are definitely more efficient approaches, but the algorithm below has the advantage of being relatively simple. Here is [one alternative](https://www.aclweb.org/anthology/W05-1105.pdf).  There are definitely more.

## A Simple, Fast Enough, Algorithm
> It isn't important to fully understand this algorithm as long as you understand what it has to do: build a well-formed MRS tree, and what the rules are in doing that. We'll use this code as a library routine all throughout the tutorial, but we won't dive into its implementation again.

This description is for those that are interested in how the algorithm works, and isn't necessary for understanding the rest of the tutorial:

First some definitions used in this algorithm:
- **Hole**: A scopal (i.e. `h` type) argument in an MRS predicate that doesn't refer to an existing predication
- **Floater**: A tree of predications that have had zero or more of their scopal (i.e. `h` type) arguments filled by predications.  [This is not at official MRS term, it is one created for this algorithm]

As a reminder, a tree is "well-formed" if:

1. Each predication is assigned to one, and only one, hole. No holes are left unfilled, and no predications are unassigned at the end  
2. None of the assignments of predications to holes violates a `qeq` constraint 
3. Any variable introduced by a quantifier is not used outside of the branches assigned to its `RSTR` or `BODY` arguments  

**Here's the intuition for how the algorithm works**: We are going to walk a search tree.  Every node of the search tree represents a partial assignment of floaters to holes that meets the above 3 constraints. Every arc from a parent node in the search tree to a child node in the search tree represents a unique assignment of a (otherwise unassigned) floater to a hole.  If that assignment violates a constraint, the search tree node is not valid (since obviously keeping this assignment and adding floaters to it can't be valid either) and we stop searching that whole branch of the search tree. This pruning is what makes it faster than the really naive "try every option" approach. Every node in the search tree that has no holes left to assign is a solution.

**Algorithm Flow Summary**: We start at the `TOP:` hole and record on it any `qeq` constraints that apply to it and any `X` variables that are in scope for it (none at the start). As we traverse an arc in the search tree and assign a new floater to a hole, we propagate any constraints and in-scope variables from the (parent) hole to the holes in the (child) floater.  Then we create the next node in the search tree by choosing the next hole to fill from the existing node.

**Start with**:\
Each node in the search tree has the following structures that represent where the search has progressed to:

`allHolesDict`:              Dictionary populated with all the holes in the MRS. Each hole has information about:
- The `qeq` constraints that currently apply to it
- The `X` variables that are currently in scope for it
- The floater it is from
`nodeAssignmentList`:        Assignments of floaters to holes that the search tree node represents. Empty for the initial node.
`nodeRemainingHolesList`:    Holes left to fill in this search tree node. Only contains the `TOP:` hole for the initial node.
`nodeRemainingFloatersList`: Floaters still unassigned at this node in the search tree. Contains all floaters for the initial node. Each floater contains information about:
- A list of holes it contains
- A list of unresolved `x` variables it contains
- A list of any `Lo` parts of a `qeq` constraint it contains (if it doesn't also have the `Hi` part in the floater) 

**Algorithm**:\
Starting at the initial node:
- Get `currentHole` by removing the first hole from `nodeRemainingHolesList` 
- Get `currentFloater` by removing each floater from `nodeRemainingFloatersList` and: 
  - If `currentFloater` does not violate the constraints in `currentHole`: 
    - Add `currentHole = currentFloater` to `nodeAssignmentList`
    - Propagate the constraints and variables from the new parent to all holes in `currentFloater` 
    - Add holes from `currentFloater` to the end of `nodeRemainingHolesList` 
    - Check number of holes left:
      - if == 0, return `nodeAssignmentList` as a solution
      - otherwise, continue the search by "creating a new search tree node" via recursing to the top of the algorithm

**Returns**:
`nodeAssignmentList` which is simply a dictionary where the keys are holes and the value is the floater that was assigned to it.

Once this has run its course you will have all the valid well-formed trees for the MRS. 

**Code and Example**
Below is the Python code for the main routine, all of the code is available [here](https://github.com/EricZinda/Perplexity/blob/main/perplexity/tree_algorithm_zinda2020.py).

Let's walk through an example of "Every person eats a steak” to see how the code works:

```
[ "Every person eats a steak"
  TOP: h0
  INDEX: e2 [ e SF: prop TENSE: pres MOOD: indicative PROG: - PERF: - ]
  RELS: < [ _every_q<0:5> LBL: h4 ARG0: x3 [ x PERS: 3 NUM: sg ] RSTR: h5 BODY: h6 ]
          [ _person_n_1<6:12> LBL: h7 ARG0: x3 ]
          [ _eat_v_1<13:17> LBL: h1 ARG0: e2 ARG1: x3 ARG2: x8 [ x PERS: 3 NUM: sg IND: + ] ]
          [ _a_q<18:19> LBL: h9 ARG0: x8 RSTR: h10 BODY: h11 ]
          [ _steak_n_1<20:25> LBL: h12 ARG0: x8 ] >
  HCONS: < h0 qeq h1 h5 qeq h7 h10 qeq h12 > ]
```

There are 5 holes in the MRS that need to be assigned a predication: `h0`, `h5`, `h6`, `h10`, `h11`.

To do this, `try_alternative_hole_assignments()` gets called initially with `all_holes_dict` assigned like this:

```
all_holes_dict = {
   'h0' = {'Constraints':  {'InScope': {},     'QeqLo': {'h1': False}},    'Floater': None, 'Label': 'h0'}
   'h5' = {'Constraints':  {'InScope': {'x3'}, 'QeqLo': {'h7': False}},    'Floater': None, 'Label': 'h5'}
   'h6' = {'Constraints':  {'InScope': {'x3'}, 'QeqLo': {}},               'Floater': None, 'Label': 'h6'}
   'h10' = {'Constraints': {'InScope': {'x8'}, 'QeqLo': {'h12': False}},   'Floater': None, 'Label': 'h10'}
   'h11' = {'Constraints': {'InScope': {'x8'}, 'QeqLo': {}},               'Floater': None, 'Label': 'h11'}}
```

You can see that 'Floater' is initially set to `None` for all the holes. The goal is to figure out which unassigned predications (i.e. floaters) should get assigned to each of these holes.

`try_alternative_hole_assignments()` does this by searching a tree of all possible assignments. 

It starts with the `all_holes_dict` from above. Since there are some holes that don’t have a predication assigned, it will:

1. Pick the next unassigned hole: in this case, `h0`.
2. Pick the next unassigned floater: in this case, `h1`.
3. If assigning `h1` to `h0` doesn't violate any constraints on building a scope-resolved tree: update `all_holes_dict()` to contain this assignment and recurse at step #1 with the new `all_holes_dict()`.
4. If the assignment does violate a constraint, skip it and jump to step #2 to try the next floater.

If you recurse to the point where there are no more holes you've found a valid tree: yield it, and then keep searching for more.

```
def TryAlternativeHoleAssignments(allHolesDict, nodeRemainingHolesListOrig, nodeRemainingFloatersList, nodeAssignmentList):
    # Grab the first hole to fill and remove it from the list
    currentHole = allHolesDict[nodeRemainingHolesListOrig[0]]
    nodeRemainingHolesList = nodeRemainingHolesListOrig[1:]

    index = 0
    # Try each remaining floater in this hole
    for index in range(0, len(nodeRemainingFloatersList)):
        # Grab the current floater and pull from the list for when we recurse
        currentFloater = nodeRemainingFloatersList[index]
        newNodeRemainingFloatersList = [x for i, x in enumerate(nodeRemainingFloatersList) if i != index]

        # Check if constraints are met. If not, prune entire search space by
        # skipping since none of its children can work either
        errorOut = []
        if not CheckConstraints(currentHole["Constraints"], currentFloater, errorOut):
            # Constraint Failed: try the next one
            continue

        # Hole successfully filled
        # Assign the floater to the hole in a copy of assignments since we will be
        # changing on each loop
        currentAssignments = copy.deepcopy(nodeAssignmentList)
        currentAssignments[currentHole["Label"]] = currentFloater["Label"]

        if len(newNodeRemainingFloatersList) == 0:
            # We filled the last hole, return the solution
            yield currentAssignments
            return

        # If this floater has more holes, add them to a copy of the nodeRemainingHolesListOrig
        # Fixup any of the holes from this floater in a *copy* of holeDict since it also holds the holes
        # and the pointer to the hole is being changed so we don't want other nodes to get changed too
        newNodeRemainingHolesList = copy.deepcopy(nodeRemainingHolesList)
        newHoleDict = copy.deepcopy(allHolesDict)
        FixupConstraintsForFloaterInHole(currentHole["Constraints"], currentFloater, newHoleDict)
        for nextHoleName in currentFloater["FloaterTreeHoles"]:
            newNodeRemainingHolesList.append(nextHoleName)

        # This hole was filled, see if any remain
        if len(newNodeRemainingHolesList) > 0:
            # recurse
            yield from TryAlternativeHoleAssignments(newHoleDict, newNodeRemainingHolesList, newNodeRemainingFloatersList, currentAssignments)

    # At this point we tried all the floaters in this hole
    return
```

> Comprehensive source for the completed tutorial is available [here](https://github.com/EricZinda/Perplexity).

Last update: 2024-10-23 by Eric Zinda [[edit](https://github.com/EricZinda/Perplexity/edit/main/docs/mrscon/devhowto0020WellFormedTree.md)]{% endraw %}