## Title
all_plural_groups_stream() needs to return valid solution groups for an MRS. Valid solution groups:
- Are only in one mode: coll, dist or cuml
- Meet all the constraints

However, there is one more point: maximal? or all possible?  
- Even 1 plural variable in an MRS will require grouping to represent the complete solution if they are acting alone: "men walk".   (the collective can be one solution). In this case you'd just expect one group. But: subsets of that group would also be true.
- With two variables: men are walking a dog you'd still only expect one group in any world (the maximal solution). But again, subsets would work.
- Nobody wants a minimal answer. The only reason to generate combinations of solutions that all meet the constraints is if *constraints* need them
 
Because we only return one solution group to the user, we need it to be maximal. However it should return sets as soon as they find an answer that meets the constraints, but then keep returning it as it gets updated. That way, the user can see answers as they come

Other key model points:
- constraints are *per solution group*.  Global constraints say "across solution groups x must be true"

Really, we want to merge in a solution if it
  a) doesn't invalidate this or change its mode as a solution group and 
  b) ? couldn't be used to create other solution groups by adding a row?
  - This means that we are creating maximal solution groups?


### Algorithm Version 1
This will be the skeleton of the algorithm we're going to use. Start with an empty set. When a new row comes in, try adding to every existing set (this builds all the combinations). If it meets or could meet the criteria, add it as a new set. If it actually met the criteria, yield it as an solution group. This will produce all combinations that meet the criteria.

### Algorithm Version 2
Problem is that this will yield groups that are variations of the same answer. We want *maximal groups* since we only return one answer. ? None should be able to merged and still be the same mode ?

For a world that has 2 folders, each with 4 files, if the user says "which 2 files are in 2 folders", we can produce several distributive solution groups. But "which files are in 2 folders" you'd only expect to get a single solution back.  What's the difference? between(N, inf).

TODO: See if this is right: 
        # Check if this was a group that is not (n, inf) and this solution added individuals, if so we need a new group
        # So that they old group can be there to recombine with new solutions

  - Depends on:
    - Once a group is uniquely one mode it can't transition to another
So, some scenarios have a maximal answer that in one group represents all objects in any other answer. i.e. it is combinatorial


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
 However, if the user says "2 files are in a folder" and there are 100, it should say something like "True, but really there are more". That's what a human would do.
 (Assertions: actual solutions might be needed for abductive reasoning?)

Wh-questions
    Wants *all* answers but to *one solution group*

Commands: ? Unique values of all arguments ?
    (because of implied quantifier being one) Only wants the first answer
    Delete files (could be 2 files or all files)
    Need to decide if this a maximal or minimal solution
    Make it consistent with wh-questions


### Archive

Any variable that is plural can be combined with other plural variables in cdc (collective/distributive/cumulative) ways

