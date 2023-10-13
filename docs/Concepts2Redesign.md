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
