Remaining work to be shown in the tutorial:
 
Plurals work
    - Get a command to work
        - a command has to work in two phases:
            1. queue up what would happen if it succeeded
            2. actually do it later
        - "a file is large" returns all of them so they will all get deleted
            - theory: when a solution group succeeds we are done because that group fulfils the query
                doesn't seem to work with "which"
                - Theory: which files are large: "files" should return the solution that is "the maximum set" first? i.e. all rstrs that are in the body
                    Quantifiers are choosing combinations of solutions that make them true because downstream children might need a particular group
                    They should always start with the maximum set?
                - Theory: Which should look through all answers and pick the maximal one?
                - Theory: Run the determiner *after* the quantifier?
                - Theory: Quantifier needs to be able to say "stop". "a" should say stop after one works.  "udef" should stop after 1 solution
                - Theory: commands should stop after the first solution group.
                - Theory: There is an implicit "uber quantifier" on the front of all phrases that tells you how many of the solutions to return? 
                    All should just return 1, except for which?
    - Figure out a way to make "in" be efficient for "which files are in folders"?
        - If we don't know what predications require (must have) and support (can have), they have to do all alternatives 
            in case downstream predications need those alternatives
        - If they are declared then we can optimize *some* cases
    - work through the tests and make them work in new regime 
    - Should remove duplicates before reporting answers
    - Really slow: Example28
        a few files are in a folder together
            Need to walk this through
        "4 files are in a folder"
        Returns an *enormous* number of items
            Are they all really legit?
        Start with "which files are in folders?"
            includes ones that are coll when it isn't used
            "in_p_loc" receives two combinatoric variables very quickly
            Then it tries every combination, returns pretty fast
                there are no duplicates, they are legit combinations
            solution_groups_helper() gets the list of solutions
            Really blows up on this line:                 for combination in itertools.combinations(variable_assignments, combination_size):
    Performance Ideas:
        We could stream answers from unquantified MRS to the solution groups
            I don't think this will work because we need to know all of the answers for "the", for example
        If nobody cares about sets, don't generate them
            What are the real terms for "don't care"
            each_q(x), every_q(x) forces distributive of x
            met(x) forces collective of x
            dance(x) could be anything (and means different things)
            in(x, y) could be anything (and means the same things)

            If we look at the size of actor and location, we can optimize and check differently
    - all 3 boys carried all 3
    - The girls told the boys two stories each
            The boys are building a raft each. (operator fixex)

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

