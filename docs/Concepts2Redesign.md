
A phrase generates at least one MRS. 

That MRS can generate at least one scope-resolved MRS tree.

## Phase 1
Phase 1 generates a set of local (i.e. true for only the MRS local constraints) solutions that contain variable assignments from only one "interpretation" of each predication. This is called a `solution set` and is the output of Phase 1. Here's how these are found:

That scope-resolved MRS tree can generate, statically (i.e. before resolution), at least one `interpretation` which is a selection of alternative interpretations of the predications within it. The predication interpretations are defined by actual Python method implementations of the predication.  Each implementation represents an *alternative* interpretation. This means that the variable assignments it generates should not be combined with the results of other interpretations.  They are *alternatives*. All combinations of `interpretations` for the predications which have them must be tried exhaustively to fully search for all possible meanings.

Each `interpretation` may further generate one or more `disjunction trees` because the `interpretation` has predications within it that are `disjunction predications`. They generate further *alternatives*, but, crucially, they cannot be known beforehand as they depend on the values of the arguments passed in. A `disjunction predication`, therefore, generates further interpretations, but they are only known at runtime. Just like statically known `interpretations`, all combinations of disjunction alternatives must be tried to fully search the tree for meaning. But, because the alternatives can only be known at runtime, they can't just be put together and tried in all combinations by the engine. They have to be discovered by evaluating the tree and allowing the depth first algorithm to explore them.[Issue: Why can't we take the same approach, then, for static ones??]

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


# Design
A tree_record object holds a bunch of generators that generate results for the tree *when requested*. These generators record errors in the execution context they were given. There can be subtrees that get executed (e.g. by neg()) in the course of evaluating a tree that should *share* the error context with the outer tree.  

There is no reason to share a context across different trees.  The context itself is a TreeSolver, and each TreeSolver has an ExecutionContext with it. When a subtree gets resolved (as in neg()), a new TreeSolver is created to do it, but uses the same ExecutionContext so errors are recorded for the whole tree.

[TODO: Describe how neg() works.]

The same thing happens with scopal arguments such as "copy "file5.txt" in "documents"":
    pronoun_q(x3,pron(x3),udef_q(x18,_document_n_1(x18),proper_q(x8,[quoted(file5.txt,i14), fw_seq(x8,i14)],_copy_v_1(e2,x3,x8,_in_p_loc(e17,x8,x18)))))
    the predications under the scopal generator could generate multiple *alternative solution sets*, i.e. disjunctions, in which case they need to be treated as other disjunctions
    

This whole thing came about because we weren't getting "(there are more)" messages because solutions to the same tree were not necessarily consecutive
    - What is the difference between building alternative trees up front and forking as you go?
    - The goal is to end up with a self-consistent set of solutions that are true for the MRS local constraints
    - We'll need all the dynamic alternatives to be tried against each other but never used together, only one of them should ever be used, though.
        - This is basically a disjunction that returns a set of items that should be used as solution items, but are distinct from the next set it returns
            - The solution set should return all combinations of items from every disjunction as possible solutions
        - we could potentially treat like concept vs. referring expression, etc. Where the solution group generator does post-processing to make sure they are mutually exclusive
    - Analysis of "which 2 files in a folder are large?"
        - Note: there is nothing disjunctive about this
        - World: [(True, "/Desktop/file2.txt", {"size": 10000000}),
                   (True, "/Desktop/file3.txt", {"size": 10000}),
                   (True, "/documents/file4.txt", {"size": 10000000}),
                   (True, "/documents/file5.txt", {"size": 10000})]
            - We pick out file2 and it is large -> succeeds
            - We then grab file3 and it is not -> fails
                - This should not stop the solution set generation
                - What should?
    - Design:
        - If we allow each predication to just yield all alternatives but, if they are disjunctions, they have a different lineage ID, then it should naturally walk through all the alternatives
        - There is not, however, a way to declare that a particular branch of a disjunction has a failure and return an error for it.  
            You get to return an error for an entire disjunctive predication if it fails, and that is it
            We could make errors work the same if the disjunctive predications had a way to mark failure for all the alternatives that failed
            - More thoughts:
                - When is a disjunctive tree complete?
                    - A tree starts as a unique set of predictions
                    - Disjunction ids in the state indicate when there are successful disjunction values in the state
                    - If any disjunction values get all the way to the end and become a solution, they should be recorded, 
                        this indicates that that particular disjunction value had a solution
                    - If a disjunctive prediction generates no alternatives then the disjunctive tree failed
                        - This is easy to check if the predication marks that it is a disjunction
                    - If we see a new disjunction ID in any position, it means the previous one is finished since they are always consecutive
                        - if none of the successful solution lineages contained this ID in this position, then there were no solutions for it and that should be reported
                    - If there is a disjunctive prediction that generates alternatives, all of which fail by hitting a predication that has no solutions
                        - every predication that fails to generate answers is failing a solution. If there are lineages in it, then it contained disjunctions
                        - if we are at a disjunction lineage that has not been seen before OR we are at the end, it is time to check the previous one:
                            - and the previous one never had a success
                            - then the tree failed
            - Design:
                - always remember:
                    - what all the successful (meaning the whole tree was successful) disjunction lineages were
                    - what the most recent disjunction lineage is
                - For every state that gets generated that has a lineage, check its lineage:
                    - Every segment in the new one from the right side to left that had a value in both previous and this one, but is different means a disjunction set is complete
                        - handle each one
                - And the very end when there are no more solutions for this tree:
                    - Handle every segment from the last set
                - "handling a segment" means:
                    - Fire errors for all the disjunctions where the lineage of the segment is not the *prefix* of any solutions that got generated
                - Returning errors:
                    - MrsTreeLineages contain the error that stopped them, that is good
                    - A potential problem is that they pollute the global error

The basic flow is this:
    - Generate all the solutions for a given set of predication interpretations
        - "Predication interpretation" means one interpretation of a predication given the input.
        - So, if a predication like fw_seq(x, y), returns 2 *alternative* y's for a given x, which should not be in the same solution group, that is two different interpretations
        - Another alternative is "the soup", where it is really be interpreted as a special kind of noun, not using "the" as a determiner
    - Do phase 2 on them
    - Do the next set


Design Alternatives:
    - Start by just assuming that each alternative is a different interpretation
        - For a given MRS, gather all of the alternatives up front before execution
        - Then execute each combination of them
    - For predications that can't be separated up front because they depend on input data
        - They shouldn't be run as pure alternatives because they are generating alternatives depending on the state
    - Mark predications as mutually exclusive
        - Make "the soup" be a tree transform?
