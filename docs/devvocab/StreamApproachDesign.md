The undetermined solutions are true in any combination (since each is true individually).  i.e. they are combinatorial solutions.
If a given variable is still combinatorial, it means that solution represents N individual solutions

"Only/Exactly", much like the quantifier "the" does more than just group solutions into groups ("only 2 files are in the folder") it also limits *all* the solutions to that number. So we need to go to the bitter end before we know that that are "only 2" group_rstr is set in the criteria each time a rstr is checked.
    Also, as soon as >2 are found, abort the whole thing
    At the very end return all sets

Because of dist vs cuml, it isn't this easy.

### We really don't need to return *all combinations that are solutions*, just the *unique* solutions that meet the criteria, all the rest are just duplicates
Algorithm for just returning maximal solutions that meet the criteria: only create sets that represent unique answers, or partial sets that will be used to generate alternatives
- If a solution can be added to any existing set, do it.
- Then, if any variable with a constraint has a value that hasn't been seen yet, we *potentially* need to generate a new set. Do it if:

    (1, inf) by itself never needs to build another set, it just means "any"
        So, really, (1, inf) can just be removed?
    (2, inf)  by itself never needs to build another set. it just means its one set must have at least 2 elements.
    (1, 1) needs to add a set for each alternative
    (2, 2) needs to add a set for every combination
    ...
    (n,n) needs to add a set for every combination. I.e. it should operate like it does now (might be some optimizations about sets that can't ever get more added?)

Basic algorithm: we are building up a list of potential solution groups. 
- Start with a list of a single empty set
- When a new solution comes in, for each set in the list:
  - See if the constrained variable values are already in the set
    - Yes: this is a "merge": Simply add the item into the set. Because it changes neither the unique individuals nor the unique values, nothing changes.
      - Theory: we are done and don't need to check other lists? Because we can't have this unique set of values in another list?
    - No: this is *potentially* an "add": See if the new solution can be added to the set and still meet the criteria.
      - Yes: does it have open constraints (see below)?
        - Yes: add it to the set
        - No: create a copy of the list and add this element to the copy. Add the set to the set list.
      - No: Done with this set, check the next.
    - Then: decide what to return. Options:
      - We could always return every set that was created or modified that meets the criteria
      - We could return any answer that had a constrained value that hadn't been seen
      - Think about this.
      
open/closed constraints:
    (1, inf) by itself never needs to build another set, it just means "any"
        So, really, (1, inf) can just be removed?
    (2, inf)  by itself never needs to build another set. it just means its one set must have at least 2 elements.
    (1, 1) needs to add a set for each alternative
    (2, 2) needs to add a set for every combination
    ...
    (n,n) needs to add a set for every combination. I.e. it should operate like it does now (might be some optimizations about sets that can't ever get more added?)