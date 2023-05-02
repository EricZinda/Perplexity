The undetermined solutions are true in any combination (since each is true individually).  i.e. they are combinatorial solutions.
If a given variable is still combinatorial, it means that solution represents N individual solutions

"Only/Exactly", much like the quantifier "the" does more than just group solutions into groups ("only 2 files are in the folder") it also limits *all* the solutions to that number. So we need to go to the bitter end before we know that that are "only 2" group_rstr is set in the criteria each time a rstr is checked.
    Also, as soon as >2 are found, abort the whole thing
    At the very end return all sets

Because of dist vs cuml, it isn't this easy.

### Algorithm
Note: We really don't need to return *all combinations that are solutions*, just the *unique* solutions that meet the criteria, all the rest are just duplicates

Algorithm for just returning maximal solutions that meet the criteria: only create sets that represent unique answers, or partial sets ("contenders") that will be used to generate alternatives

Goal: Return solution groups
Basic algorithm: each row that comes in gets combined with all the groups that exist to create new groups. 
    Any that can't possibly combine with another row (because it is monotonically increasing) should be removed from the set so we don't keep trying. That prunes some of the search space
    keep track of a list of potential solution groups - that is: groups from the set of all possible groups that.  
    the only variables considered when making groups are those with non-default constraints, 
    because the whole point of groups is dealing with plurals

- Start with a list of a single empty set
- When a new solution comes in, for each set in the list:
  - See if the constrained variable values are already in the set
    - Yes: this is a "merge": Simply add the item into the set. Because it changes neither the unique individuals nor the unique values:
      - This can *only* happen when there are variables without constraints on them because otherwise the entire set of values can't already exist (since solutions are always unique from the phase 1 solver)
      - Nothing in the stats needs to be updated and the criteria must be the same as before. The state of the set is the same as before.
      - No new sets need to be created because the set that represented this has already been added
        - This does mean, however, that return approach a) below could return different sets depending on the order of new solution groups?
          - If the dups are up front, before the criteria is met, only one solution will be returned when it eventually meets the criteria
          - If they are at the end, where the first one makes the criteria true, each dup will return the solution with just it added
          - TODO: As long as the caller only cares about unique values of things that have constraints AND they make sure their wh-question always has a constraint
            - then: don't return this as a new solution in either case.
    - No: See if the new solution can be added to the set and not fail.
      - Yes: does it have open constraints (see below)?
        - Yes: add it to the set
        - No: create a copy of the set and add this element to the copy. Add the set to the set list.
      - No: Done with this set, check the next.
    - Then: decide what to return. Options:
      a) We could always return every set that was created or modified that meets the criteria (some may be contenders). Used for wh-questions and commands.
        - Current behavior
      b) We could return any answer that had a constrained value that hadn't been seen that was added to a list that meets the criteria. Used for yes/no and propositions. 
      - Think about this. 
        - "which files are in two folders" would return the same list over and over with just a new item added for a). 

NOTE: see TODO above
NOTE: 
This notion of open is problematic. It was meant to create "maximal" solutions. But for "which files are 20mb" it stops 2 10mb files from working and more than 1 20mb file from working
    - it builds up the set but doesn't return it
    - Theory: because it is sticking all answers into a single bucket?
        - It is converting it to the equivalent of "which files are big". This is a case where the combinations matter and things can't just be grouped into a big group
        - which files are large returns 4 groups, each one just adding another item

open constraint set means: there is no reason to build multiple sets, there will only be one at the end. It is open because we just keep adding to it
  - What is the difference between sets_are_open and exists_in_group()? 
    - An open constraint set says there will only be one answer group.  exists_in_group() will modify existing groups with answers that
      don't change them (since the constrained variables are not modified)

open/closed constraint sets: a constraint set is "open" if all of its constraints are open. Otherwise, it is closed:
    (no constraint) Open. If there are no constraints at all, the set is open.
    (1, inf) Open. By itself never needs to build another set, it just means "any"
        So, really, (1, inf) can just be removed?
    (2, inf): Open.  By itself never needs to build another set. it just means its one set must have at least 2 elements.
    (1, 1) Closed. needs to add a set for each alternative
    (2, 2) Closed. needs to add a set for every combination
    ...
    (n,n) needs to add a set for every combination. I.e. it should operate like it does now (might be some optimizations about sets that can't ever get more added?)