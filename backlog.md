Remaining work to be shown in the tutorial:


Update the comments in the code and the docs
- TODO: For propositions, we need to respond with "there are more" if it is "at least" or "exactly" once we get above the level that a normal person would say "at least" for

- Bug: a few files are in a folder together needs to materialize the entire set
- variable_has_inf_max, constraints_are_open are just inverses of each other, get rid of one of them
- We don't care anymore if a solution is "uniquely" one set of solutions
- It seems like we don't care about "locked single modes" or not.  Really it is just: 
  - Merge a solution in if it only updates max(inf) variables.
  - Track lineage and if you see a solution that is a descendant of current lineage, use it and update the key 
  - 
Clean up code (i.e. not using modes returned from stream anymore)

Bug: Example33 should be set to 100 but it is way too slow for some scenarios

Bug: Test does not capture (there are more)
Plurals work 
Need to make these right
    - delete the only two files in the folder -> should fail
    - delete only two files in the folder -> (are you sure, this will be random?)

- Example33: which 2 files in the folder are large?
  - Very slow
  - There are two folders but we have to exhaust all possibilities for 2 files first
  
- "which files are in a folder" (forward reading). How many solution groups should there be?
  - In general:
    - Different modes should always be different solutions
    - Any constraints other than (n,inf) should be different solutions
      - We *can* have multiple of any of dist/coll/cuml because: we can have multiple solution groups. What we are doing is amounting to just merging the solution groups together

    - which means that the same mode with an (n,inf) should be a different solution

  - files() has 2,inf so we build up different sets with different combinations of 2, but they will all be the same
  - Instead, (n,inf) really isn't different solution groups.  It is just one solution group that must have at least n
  - Really we should do the add() method and it should tell us if we need to create a new group or just add it
    - If the only thing that changed are N, inf then we should not create a new group, which means each variable has to return if it is new
    - so, return a value that says if this changed the number of unique *individuals*
    
- Theory: Forward readings of trees are better
- Example 25: "which files are in a folder" -> when there are 2 files in one folder, and then a single in two other folders -> only returns the two files in one folder
  - Theory: Forward readings of trees are better
  - The tree that has folder first can't return the singles because we say "files" and there is only 1
    - So, the two files in the same folder are the only answer returned
    - when files is first, it can get them all
- Need to give a good error when "(which) files are large" or "files are large" fails because there is only one file.
    - Bad error message, should be "less than 2 files are large"
- which 2 files are in a folder? (in a folder with more than 2): There is more than 2 2 file in a folder
  - Need a better error message

- Dial in proper semantics for which 

- delete files that are 20 mb: really slow
- which files are 20 mb ends up with plural megabytes but only one object. But: this should work because we special-case "measure"
  
  Need to do better optimization, then
  - Option 1:
    - Need to make the quantifier itself take the plural restriction into account
      - Then: which_q() can handle plurals as it likes
  - Option 2:
    - Have rules for composing quantifier constraints with adjective constraints
      - which()  composes with plural to make between(1, inf)
      - the() composes with plur

- And the other constraints get added as per the docs

  - Test that this approach works by going through examples. Scenarios to try:
    - not
      - Anything that converts to between(x, y) should work
        - not more than x = between(1, x), not less than x between(x, inf)
        - some = between(2, inf)?
      - no files are in a folder: no_q() succeeds with no values
        - _a_q(x9,_folder_n_of(x9,i14),_no_q(x3,_file_n_of(x3,i8),_in_p_loc(e2,x3,x9)))
      
    - all 3 boys carried all 3
    - The girls told the boys two stories each
            The boys are building a raft each. (operator fixex)
    - 
    - Tests: 
            - https://aclanthology.org/P88-1003.pdf
            - https://aclanthology.org/W13-0202.pdf

    - Deal with this:
      - TODO: As long as the caller only cares about unique values of things that have constraints AND they make sure their wh-question always has a constraint
      - then: don't return this as a new solution in either case.
    - Slow Scenarios
      - Options:
        - if it isn't a wh-question, we don't need to return the actual answers, don't keep them, just the stats. Saves a little space.
        - Get rid of sets that can't possibly be right so we don't keep checking them
          - which 3 files are in a folder: have to keep around all the old ones in case there are duplicates. Faster way to check them?
        - Phase 2 requires AllRstrValues to be generated for things like "the" and maybe "all"
          - The entire MRS must be finished in the current model to get these
            - In some cases that may be quicker since we'll know it isn't possible and not have to do the combinatorics 
              - We could *maybe* generate them up front if needed
        - Use a tree structure to quickly add a solution to the right groups
          - Build a data structure like the one they use in 3d games to divide the world?
        - Only return the first N
        - Streaming algorithm
        - online algorithms
        - Integer programming: https://stackoverflow.com/questions/62622312/algorithm-to-find-some-rows-from-a-matrix-whose-sum-is-equal-to-a-given-row
    
      - Slow Scenarios:
        - which 3 files are in 2 folders: 3(x), 2(y)
          - still VERY slow
          - Still need to generate all combinations of 3 x 2 to find out that none are in 2 folders
          - all combinations of 3 of 100 is 4950, for 1000 it is 499500, 3 of 200 is 1313400
        - "which 2 files in the folder are large?"
          - very slow
          - because the second folder doesn't show up until the very end and we are checking for "the folder"
        - which files are in folders?
          - There is *no* criteria but it is still slow
          - Phase 2 is fast, it is phase 1 that is slow
            - Suspect implemenation of "in"
              - "in" is slow because it is checked like:
                - for item in item2.contained_items(x_location_binding.variable)

      - "a file is a few megabytes" doesn't work

  - copy x to y
    - needs copy with a scopal arg
      - We need to support turning a tree into something abstract that can be manipulated and understood
        - We could simply use the tree directly but then we'd have to special case all of the prepositions
        - Instead, we will create a special event that the scopal args get attached to
        - Then ask the tree to "interpret itself" in an abstract way that we have a chance of understanding
          - Some terms are actual things in the world and others are the way we want it to be
        - How?
          - We could run the predications using abductive logic?
          - We could "make a plan" to make X true
          - We could special case prepositions and just handle them
          - We could assume the scopal argument contains a particular thing (that depends on the predication it is in) and ask for that thing
            - i.e. copy assumes a locative preposition and looks for that
            - Can we find out what kinds of things "copy" can take as its scopal argument?
          - Theory: the verb with the scopal argument has an arg that is resolved in the scopal argument
            - Not true for make me be quieter, the argument comes from somewhere else
          - Theory:
            - The scopal argument determines some state change for the topic being verbed. The verb needs to collect this state change and then make it happen in the manner of verbing:
                - put the vase on the table: _put_v_1(e2,x3,x8,_on_p_loc(e15,x8,x16))
                  - "put" means "move" so: put_v first makes a copy of x8, and then lets scopal "do what it does" to it
                - paint the tree green: _paint_v_1(e2,x3,x8,_green_a_2(e16,x8))
                  - "paint" means "change it to" so it lets its arguments just do that
                - make me be quieter: _make_v_cause(e2,x3,(more_comp(e16,e15,u17), _quiet_a_1(e15,x10)))
                  - Make is a special case
                - It would be *ideal* if this was just the same as abduction.  It isn't quite, since the verb (paint, copy) changes what happens:
                  - paint the flower in the corner
                  - copy the file in the folder
                  - both use a scopal for _in_p_loc(e15,x8,x16) but what "in" does very different
                  - effectively, "paint x in the corner" and "paint x blue" are very different operations meaning different paints
                    - so maybe the best approach is to build a different version of paint for each class of thing it can handle and treat it like a new argument
                    - reflect should copy data about itself into its event in a form that can be easily parsed
                    - How to find the right target in the scopal arg?
                      - Find all predications that use it as their ARG1?
                    - And then let "quoting" create a representation that puts them into "classes"
                      - "quoting" has to be special case code per predication because conversion into a canoncal form is per predication and not directly determinable from arguments. For example "copy the file above folderx" has above(folderx) but the copying should happen in the folder above it
    - also copy x in y (the same scenario)

    - Support for prepositions
      - show declaring verbs that understand prepositions
    - Theory: We don't need to choose different variations of the index of the phrase based on "comm", "ques", etc
      - Except: if we want to use abductive logic to make "The door is open" not evaluated as a question, but as a desire to make that true and then make it true in the system

