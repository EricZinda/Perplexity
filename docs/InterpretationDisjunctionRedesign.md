## Summary
A phrase generates at least one MRS. 

That MRS can generate at least one scope-resolved MRS.

Each predication in that scope-resolved MRS might have multiple, alternative, interpretations (represented by actual Python functions). All combinations of all the interpretations of the predications in the MRS must be tried to investigate all possible solutions.

A given interpretation of a predication might, itself, generate independent assignments (i.e. disjunctions) based on the values of the arguments.  These also need to be tried in all combinations.

Finally, a set of solutions that have chosen a particular set of assignment sets for every predication interpretation AND for every disjunction alternative from a predication, constitute a self-consistent solution set. This can go through phase 2 as a unit.

Errors: Errors need to be tracked for each full interpretation of the tree. I.e. a view of a tree that has chosen interpretations for all predications AND chosen disjunction alternatives constitutes and interpretation, if it fails, it needs to be identified as an interpretation that failed and be able to return a unique error for the failure.

If they all fail, each interpretation record that was generated can be inspected to return the best error.

## Phase 1
Phase 1 generates a set of local (i.e. true for only the MRS local constraints) solutions that contain variable assignments from only one "interpretation" of each predication. This is called a `solution set` and is the output of Phase 1. Here's how these are found:

That scope-resolved MRS tree can generate, statically (i.e. before resolution), at least one `interpretation` which is a selection of alternative interpretations of the predications within it. The predication interpretations are defined by actual Python method implementations of the predication.  Each implementation represents an *alternative* interpretation. This means that the variable assignments it generates should not be combined with the results of other interpretations.  They are *alternatives*. All combinations of `interpretations` for the predications which have them must be tried exhaustively to fully search for all possible meanings.

Each `interpretation` may further generate one or more `disjunction trees` because the `interpretation` has predications within it that are `disjunction predications`. They generate further *alternatives*, but, crucially, they cannot be known beforehand as they depend on the values of the arguments passed in. A `disjunction predication`, therefore, generates further interpretations, but they are only known at runtime. Just like statically known `interpretations`, all combinations of disjunction alternatives must be tried to fully search the tree for meaning. But, because the alternatives can only be known at runtime, they can't just be put together and tried in all combinations by the engine. They have to be discovered by evaluating the tree and allowing the depth first algorithm to explore them.

Why can't we take the same approach, then, even for static ones? We could, but breaking them out statically allows us to fully search a given interpretation quickly, without having to exhaustively try all combinations of trees until the very end before we have the answer to one interpretation.  We'd do this for conjunctions too, if we could, but we can't since they need to be determined at runtime.


## Phase 1: Resolving Scopal Arguments
Predications like `neg()` can operate logically on a whole fragment of a tree (i.e. a branch), and require that both phase 1 and 2 be resolved in order to determine their logical outcome. Take this example:

> "which files are not in two folders": which_q(x3,_file_n_of(x3,i8),neg(e9,udef_q(x12,[_folder_n_of(x12,i19), card(2,e18,x12)],_in_p_loc(e2,x3,x12))))

In this case, `neg()` needs to know the results of the phase 2 evaluation of its scopal argument to determine if there are "2 folders" that each file is not in.

## Phase 2
Phase 2 groups a single solution set into solution groups that are now true for global constraints as well.

## Error handling
Each interpretation of a tree (including disjunctive interpretations), either fails in Phase 1 by not generating any solutions, or generates at least one solution. If it fails, it should return the "best" error it found in its tree_record. If it succeeds, it returns the solutions that got generated.

If it generates solutions, it can still fail in Phase 2 by not generating any solution groups or succeed by generating at least one. If it fails phase 2, it should return the global constraint error that failed, not any errors from phase 1.

If a scopal argument fails during phase 1, the error it generates should be the one returned from phase 1.


## Design
A tree_record object holds a bunch of generators that generate results for the tree *when requested*. These generators record errors in the execution context they were given. There can be subtrees that get executed (e.g. by neg()) in the course of evaluating a tree that should *share* the error context with the outer tree.  

There is no reason to share a context across different trees.  The context itself is a TreeSolver, and each TreeSolver has an ExecutionContext with it. When a subtree gets resolved (as in neg()), a new TreeSolver is created to do it, but uses the same ExecutionContext so errors are recorded for the whole tree.

[TODO: Describe how neg() works, and why it is different than virtual arguments...]

The same thing happens with scopal arguments such as "copy "file5.txt" in "documents"":
    pronoun_q(x3,pron(x3),udef_q(x18,_document_n_1(x18),proper_q(x8,[quoted(file5.txt,i14), fw_seq(x8,i14)],_copy_v_1(e2,x3,x8,_in_p_loc(e17,x8,x18)))))
    the predications under the scopal generator could generate multiple *alternative solution sets*, i.e. disjunctions, in which case they need to be treated as other disjunctions
    

## Scopal arguments
- Difference between the way: quantifier(), neg(), copy() evaluate their scopal args
  - quantifier() can just use call because it is operating against the interpretation that it was given
  - copy(..., scopal) needs the "normalized" form of its scopal arg, which is a *different* interpretation, so it needs to call phase1() to ask for that interpretation
  - neg() is an operation on the truth of its entire scopal arg, which means that it needs to evaluate phase 1 and phase 2 
    of its scopal arg in order to know if that arg was "true", it isn't enough to know if a particular solution is true

Scopal arguments have already had an interpretation of their predicates selected because the whole tree's interpretations have been selected. So that won't generate new tree_records.

However, they may have conjunctions in them which do generate alternatives.

