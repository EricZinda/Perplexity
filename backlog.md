Remaining work to be shown in the tutorial:
- Make old tests work
- implement small

- "delete a folder" -> test infrastructure doesn't notice (there are more)
- 
- Get rid of the old plurals comments and docs
- Rebuild the scenarios to get the tests to pass again
- Build a backend to use for ESL Scenarios

Plurals work 
- Example 36: "delete files that are 20mb" -> crash
- Example 33: "delete only 2 files in the folder" -> There are more than 2 file in the folder
  - delete only two files in the folder -> (are you sure, this will be random?)
- delete the only two files in the folder -> should fail
- Example 33: "a file is a few megabytes" doesn't work
  - Also very slow
- Need to give a good error when Example 37: "which files are in a folder" or "(which) files are large" or "files are large" fails because there is only one file.
    - Also: Example 33: which files are in folders?
    - Bad error message, should be "less than 2 files are large"
- which 2 files are in a folder? (in a folder with more than 2): There is more than 2 2 file in a folder
  - Need a better error message
- Bug: Example 28: "a few files are 20 MB" says "there are more"
  - 3 files are counted as "a few" when 1 is 20 mb and the other 2 add up to 20 mb
  - Is this right?
- TODO: For propositions, we need to respond with "there are more" if it is "at least" or "exactly" once we get above the level that a normal person would say "at least" for
- Theory: Forward readings of trees are better
- Example 25: "which files are in a folder" -> when there are 2 files in one folder, and then a single in two other folders -> only returns the two files in one folder
  - Theory: Forward readings of trees are better
  - The tree that has folder first can't return the singles because we say "files" and there is only 1
    - So, the two files in the same folder are the only answer returned
    - when files is first, it can get them all

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
  - Tests: 
          - https://aclanthology.org/P88-1003.pdf
          - https://aclanthology.org/W13-0202.pdf

  - Slow Scenarios
    - Options:
      - Get rid of sets that can't possibly be right so we don't keep checking them
        - which 3 files are in a folder: have to keep around all the old ones in case there are duplicates. Faster way to check them?
      - Use a tree structure to quickly add a solution to the right groups
        - Build a data structure like the one they use in 3d games to divide the world?
    
    - Slow Scenarios:
      - Example33: which 2 files in the folder are large?
        - Very slow
        - There are two folders but we have to exhaust all possibilities for 2 files first
      - Bug: Which 2 files in the folder are large is still too slow
      - Example 33: "which 3 files are in 2 folders"
        - still VERY slow
        - Still need to generate all combinations of 3 x 2 to find out that none are in 2 folders
        - all combinations of 3 of 100 is 4950, for 1000 it is 499500, 3 of 200 is 1313400
      - "which 2 files in the folder are large?"
        - very slow
        - because the second folder doesn't show up until the very end and we are checking for "the folder"
      - Example 33: "a file is a few megabytes" is very slow

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

