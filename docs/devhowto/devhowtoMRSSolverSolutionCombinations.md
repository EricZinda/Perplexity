## Title
Key model points:
    - constraints are *per solution group*.  Global constraints say "across solution groups x must be true"
  - Need an algorithm for maximal solutions
    - Currently, the code is trying all combinations of solutions and returning those that are coherent coll/etc groups. Because we only return one solution group to the user, we need it to be maximal.
    - The streaming engine will return sets as soon as they find an answer that meets the contraints, but then keep returning it as it gets updated

  - Really, we want to merge in a solution if it
    a) doesn't invalidate this or change its mode as a solution group and 
    b) ? couldn't be used to create other solution groups by adding a row?
    - This means that we are creating maximal solution groups?
  - Depends on:
    - Once a group is uniquely one mode it can't transition to another


Even 1 plural variable in an MRS will require grouping to represent the complete solution if they are acting alone: "men walk".   (the collective can be one solution). In this case you'd just expect one group. But: subsets of that group would also be true.

With two variables: men are walking a dog you'd still only expect one group in any world (the maximal solution). But again, subsets would work.

So, some scenarios have a maximal answer that in one group represents all objects in any other answer. i.e. it is combinatorial

Dials we have:
    - for some answers: there is a range. Sometimes we want min, sometimes max
    - 

### Criteria Optimizations
But: delete 2 files
    (not all, just two)
    This *doesn't mean* "delete but only if there are only 2 files"
    It does mean: only pick one of the solutions where there are 2 files and delete it
    Thus, it isn't the same as setting to exactly 2
    Conclusion: commands should just pick the first solution

If you say "2 children are eating" it is between(2, 2), but you really mean "at least"
    This is kind of an outer quantifier example...
    Ditto for "are 2 children eating?"
    BUT: this *isn't* the same as saying between(2, inf), because it still has to be exactly 2 per solution
    It matters because if you say "1 file is 20 mb" you *don't* mean "at least 1 file is 20 mb" because that would allow 2 files that add up to 20 mb.


delete large files
    (all)
delete files
    (all)
delete 2 files
    (not all, just two)

Theory: delete should just do the *first answer*. Only works like above if we get the maximal answer
Theory: commands should always be "only" (but this only makes sense if max isn't inf), and you have to specify for something else

2 files are large

### Which Outputs are Needed?
Stepping back, what does the system actually *use* from the output? 

True or False: yes/no questions and assertions
 doesn't have to return all answers, just one correct one. 
 (Assertions: actual solutions might be needed for abductive reasoning?)

Wh-questions
    Wants *all* answers
    Unique Values: But "Which" ideally would group the answers. A human would say "these guys are walking this dog, and those guys are walking that dog" 
        If we are willing to not group the answers, "which" doesn't have to return all answers, just correct ones. Meaning: it can avoid enumerating all the answers that are just subsets of a correct one for, for example, a between(1, inf).
        If we want groups, we could go for maximal answers, which is what was happening with "merging"

Commands: ? Unique values of all arguments ?
    (because of implied quantifier being one) Only wants the first answer
    Delete files (could be 2 files or all files)
    Need to decide if this a maximal or minimal solution



# There is no reason to return all combinations at the end because nothing will use them?
This seems right



### Archive
When numeric constraints are removed from an MRS we are left with a relatively straightforward constraint satisfaction problem that should be able to return solutions quickly, but there still may be *many* solutions.

Any variable that is plural can be combined with other plural variables in cdc (collective/distributive/cumulative) ways
    Actually, any plural variable that is combined with another variable *in any form* can form cdc groups: children are eating a (or 1) pizza. Requires cdc analysis to be true when people expect.

Actually, 


Phase 2 checks a given group to see if it meets the collective, distributive, cumulative criteria.

files are 20 mb: 

### Optimization: Removing sets that can't produce others
This trims the search space


### Scenario: "Which files are in a folder"
There are no global constraints so we can have more than one solution (but these constraints must be met per solution!)
files between(1, inf) (not between(2, inf) because of which): means any file
folder between(1, 1) ("at least" because it is not a command): means any one folder per any group of files... 

Wh-question: thus asking for only unique values of (files), or maximal answers (not all combinations)

If we transform between(1, 1) to be between(1, inf), then they all go away.

SoJust needs to return unique files that are in a folder (which is all of them)
Really this is just unique(x3)?
