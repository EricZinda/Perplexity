- and how much is the soup -> doesn't work
-  I'll have the chicken and my son will have the soup and the salad
    - Crashes with "too many holes"
- Optimization: don't go past the first N% of MRSs because they will never be right
- Also: Make ace not get more than X parses

How to compile grammar:

svn checkout http://svn.delph-in.net/erg/tags/2020
cd 2020/ace
ace -G grammar.dat -g ./config.tdl


- check_concept_solution_group_constraints() fails for Concept(dish) because there are no direct instances of "dish" they are only derived types
    - i.e. Concept("dish").instances() returns []
    - Fixed! but unclear if the logic is right...

- Error handling Bugs:
    - error in solution_group is not returned because failing to match a different implementation puts formNotUnderstood in the error context and that overrides everything

- Docs
    - Get the terminology straight
        - fix the docs
        - fix the code
    -
- test, "I want my order to be ..."

- Potential writeups
    - Walk through implementing "What is my/my son's order?"
    - starts at b7a3556
    - Key points
        - Give them a default order that is always there, and one that is shared
        - made poss() be lift style to get a shared order
        - interpret be_v_id() in a one off way
- "My order is chicken and soup" fails properly but takes forever and gives a bad error

- Fix Luis bugs:
    -	I already had on my list handling all the constructions like “forgot what I said” or “let’s start over”, etc.  All the ways you’d tell a waiter you want to start fresh
        - Can we cancel my X?
        - I want to cancel my X
        - I don't want X anymore?
        - I want to/Could I cancel my order
        - (fixed) Can we/you/I cancel my order?
        - (fixed) Can we start over?
        - (fixed) Could we start over?
        - (fixed) can/could *you* start over?
    -	This was just a funny bug I need to fix:
        o	USER: I don't want the chicken
        o	That isn't true, there isn't the chicken that isn't the chicken
    -	And the implied request given by: “My son is a vegetarian”

- How much does the soup and the salad cost? --> I don't know the way you used: cost
    - Needs to be cost_v_1() but referencing and?
- change all the could/can transforms to use OR so there are less
- Fix some of the user interface issues:
    - implement a timeout
    - do a better response than "I don't understand the way you used X" and other default messages
        - I don't know the words: plase/nn and I don't know the way you used: for

- table for two crashes
- table for 1 crashes
- show us 3 menus -> there are less than 2 "we"
    - the error for "we usually give on menu per customer" isn't coming through
    - Because "Phase2LessThan" is forced and overwrites the error
    - Need to take another look at the way errors get propagated through
- BUG: We would like the menus/the steaks
    - match_all_the_concept_n() does not check the plurality of "menus/steaks" to make sure there are conceptually 2 or more
    - "We want water and menus" - only gives one menu
    - We'd like to start with some water and menus
        - /runparse 2, 39
        - only gives one menu

- "Did I order a steak for my son?" -> There isn't such a son here

- I have 20 dollars -> you did not have 20 dollar
- Make "what is the bill?" work

- Should "we" *require* that everyone is included like and_c does?
  - Should it also imply "together" as in "we want a table (together)"

- Don't generate one more if nothing cares
- OPTIMIZATIONS:
    - for my son, Johnny, please get the Roasted Chicken -> takes forever
    - How much is the soup and the salad? -> Takes forever
    - We would like the menus -> Takes forever
        - /runparse 0,5: We would like the menus
        - every possible combination will fail because the_concept() returns instances and want_v_1() fails for instances
        BUT: it will take a long time to exhaust all the alternatives since there are a lot to try
        - If we knew that _steak_n_1(x11) woudl only generate instances and that _want_v_1(e2,x3,x11) required non-instances we could solve this by failing quickly

                             ┌────── _steak_n_1(x11)
            _the_q(x11,RSTR,BODY)               ┌────── pron(x3)
                              └─ pronoun_q(x3,RSTR,BODY)
                                                     └─ _want_v_1(e2,x3,x11)

            Text Tree: _the_q(x11,_steak_n_1(x11),pronoun_q(x3,pron(x3),_want_v_1(e2,x3,x11)))

            Interpretation: perplexity.system_vocabulary.the_all_q, __main__.match_all_n_concepts, perplexity.system_vocabulary.generic_q, __main__.pron, __main__._want_v_1
    - /runparse 0, "a table for 2 and 4" --> There is more than a table for 2 thin, 4 thin (all together)
        - takes forever
        - returns a weird error

- Need a way to clear out the order
  - start over please
  - Let's start again
  - could we reorder?
  - I don't want X
- implement "how many vegetarian dishes are there"
- implement "how many vegetarian dishes do you have?"
- There should be an exception if lift is called on a function that doesn't have its parameters marked as taking all types of sets
- Need to redo how unknown() works to handle sets > 1
- Table (then) Just two, my son Johnny and me.
    - takes forever to get to parse 88,1 which is the first that works
    - ditto for: We'd like to start with some water and menus
        - /runparse 2, 39
- "what did we order" --> "less than 2 people did that"
    - when only one person ordered
- "I'll just have a menu" --> means: clear the order and just give me a menu

- Clean up unused portions of state.handle_world_event()
- Performance fix: checkin was cca6733
    Before allowing rules to continue running over a transformed tree:
          Elapsed time: 647.23938
    After:
      Elapsed time: 979.71158
- could we see menus? -> I don't understand the way you are using: see
- what is green? --> crashes
- table for two please
    - also: table for two, please
    - only generate _for_x_cause, unclear what that means
- ChatGPT scenario:
  - You’re going to a restaurant with your son, Johnny, who is vegetarian and too scared to order by himself. Get a table and buy lunch for both of you. You have 15 dollars in cash.
  I am the waiter, you are the customer.  Interact with me only saying one sentence at a time and waiting for my response. Make the phrases very simple. OK?
  - Make these work:
    - How much does the tomato soup and the green salad cost? --> I don't know the way you used: cost
        - Parse 26
    - How much does the soup and salad cost?
    - Could you recommend a few vegetarian options, then?
    -  Hi! Could we have the vegetarian menu, please?
        - Fails
    - Could we have the vegetarian menu, please? --> There isn't such a vegetarian menu here
        - should talk about vegetarian items
    - How much is the soup and the salad? --> takes forever
    - I'll have the Grilled Salmon for myself, and for my son, Johnny, please get the Roasted Chicken.
    - Could you please recommend a vegetarian dish for my son?
    - Let's go to a table, please.
    - In that case, Johnny and I will both have the Roasted Chicken.
        - Unclear how to deal with "will both have": https://delphinqa.ling.washington.edu/t/what-is-the-common-mrs-between-we-both-will-have-soup-we-will-both-have-soup-meaning-2-of-us-will-have-soup/1011
    - We'll pay with cash, here is 15 dollars.
        First make each conjunct work:
        - (done) We'll pay with cash
        - Here is 15 dollars
             udef_q(x3,[_dollar_n_1(x3,u16), card(15,e15,x3)],def_implicit_q(x4,[place_n(x4), _here_a_1(e9,x4)],loc_nonsp(e2,x3,x4)))
             implicit command triggered by an observation

- Implementations like "_pay_v_for" support a lot of different properties.  They may allow constructions that are unexpected.  How to check for this?
  - The system makes sure that the examples listed work, but doesn't ensure that other examples don't...
- support "can we be seated?"
- make "how can I pay the bill?" work
- make "can I pay for the bill" work
- make "we want to sit at a table" work
- What do I have --> your card
  - should also say your son
- New Programming Model todo:
  - Need to recheck constraints if names are changed
  - Get rid of old metadata that doesn't have a function anymore, e.g. if the developer has it then deletes it
  - Need to support wh-question examples as a way to filter out those when necessary too
- Example33_reset: a few files are in a folder together
  - crazy slow now
  - _a_q(x10,[_folder_n_of(x10,i15), _together_p(e16,x10)],udef_q(x3,[_file_n_of(x3,i9), _a+few_a_1(e8,x3)],_in_p_loc(e2,x3,x10)))
  - Why
    - It needs to fail out of tree 0 which has "folder together" before it can get to "in together" that works
    - combinatorial_predication_1() returns all combinations "depth first" which generates a ton of options to work through before failure
    - Even worse: "a folder together" will always fail because "a" forces it to be "one" but "together" forces it to be 2
  - Ideas:
    - Should we be able to know that this will fail immediately because of the metadata on the predication and the constraint?
    - If we tried the alternatives in parallel we'd have an answer in the other tree pretty quickly
- Example33_reset: which files are in a folder?
  - Really slow because each file that is found gets added in every combination
  - Once we have a solution we should either:
    - stop (since it is a solution)
    - OR
    - Only try adding solutions from the set to it to see if there are more
  - It quickly finds a solution group, but maybe it is iterating another already?
    - It is because it is exhaustively searching for the whole list of files?
      - Which we do have to do because:
        - we need to see if any operations have RespondOperations in them
        - problem is that each iteration gets slower
    - Options
      - update respond_to_mrs_tree() to yield answers for answerWithList
      - Mark a particular set as "solve now"
        - How do you go back and do the others later?
          - You could push the set and resolve it and then, if you want to go back for others, 
            - you could regenerate it
            - you could say that that set is out of the rotation
            - We'd have to collect all the solutions

Code cleanup:
- SingleGroupGenerator assumes that, if it gets a new group with the same lineage, that there will be *more* records in it
    - and furthermore that the records that we already returned are still there
    - Neither is true anymore because the group handler can completely swap out one set of solutions for an arbitrary different set
- Get rid of reordering
  - If you get rid of reordering, then you don't have to worry about unbound in most predications which is nice
  - But we need a way to optimize somehow, it really is slow
    - Use the GPU for some parallelization? https://numba.pydata.org/
  - Timing with reordering:
    - filesystem: 231.11059
  - Timing without:
    - filesystem: 292.00379
- Get rid of extra arg in relationships
- Finish removing combinatorics since it simply fails for a lot of cases and complicates the code
- redo all the noun() type predications to properly return notathing and look like match_all_n_concepts
- Rename lineage something like disjunction
- Alternative Implementation for have_v_1_present and _order_v_1_past
  - There should be one function for have_present() that are straight fact checking routines, that allows the system to just run the query
    - Anything that needs special handling should go to another routine and be treated as a disjunction (i.e. alternative interpretation)
      - I.e. things like implied requests
- Do we still need frames with the new concept handling?
- lift_style_predication_2
  - should assert if the predication doesn't allow for > 1 in the set

Lower Pri:
- We have 0 menus -> No. you does not have something
- "who has which dish" doesn't work
- I don't have *the* soup works because:
  - there is more than one soup so negation fails, and thus this works
- I don't have soup / I have soup both work when you have ordered soup
  - because:
    - for "I don't have soup" the first MRS is the proper interpretation meaning "not(I have soup)"
      - but it fails since you *do* have soup, so we keep going
    - the second interpretation of "I don't have soup" means "check each soup and see if you have it" and there are some that you don't have
      - so it succeeds and we return this one
  - Same thing will happen with "I don't have a soup"
  - Posted a question on the forum for this
- "how much *is* the soup and salad" is crazy slow and will never work

- I want to sit down?
- could I sit down?
- "I will see menus" --> works, but shouldn't
- implement future tense get
  - Will I get a menu?
- Make "I take a steak" or "I get a steak" say "Did you mean X"
- "Do I/my son have a menu?" doesn't work
- "What did I order?" --> Make work for debugging
- implement past tense get: "Did I get a steak?"
- Can we automatically call count_of_instances_and_concepts() for conceptual stuff? So that we don't have to call it in the group?
- Make "how much are your dishes" work
- Verbs should declare what tenses they deal with, if none, they should default to present only
- Figure out how to make "I want 2 steaks and 1 salad" work
  - it only sends "2 steaks" to want so that is all that gets checked
- Get the bill working
- Make "What is not on the menu?" work properly
- Fix ontology.  Right now there are instances on the menu, for example
- Handle concepts with extra information "bill for the food" failing if we don't know it
- I'd like 2 steaks at the front door -> doesn't work
- Not issues: For Example23
  - large files are not in this folder -> Yes, that is true.
    - Interpreted as not(large files in this folder)
- Not able to update tests for /runparse 0,1 to the actual response that happened
- Need to be able to run code on the solution group
  - not() is going to require special processing
- Bug: It looks like collective only checks for one value???
    - whole_group_unique_individuals.update(binding_value) never adds a set of individuals to the set
- Build a backend to use for ESL Scenarios
- make fallback generation more robust
  - at least getting form of words right
- Test plurals:
  - each:
    - the folders have 1 file each
- 
- Dealing with all the duplication of items and combinatorics seems like a waste. Seems like there must be a better way that involves symbolics. For example
  - We want a steak
  - If there are 10 steaks, then want_v_1 will get called 20 times (10 for each person). Whereas if "steak" was symbolic it would only get called twice


- NEED TO UPDATE DOCS FOR VERBS TO MAKE ALL THIS CLEAR:
  - "I want ham" is a proposition that we want to interpret as a command
  - For a verb: Succeeding means it "worked" and should add an operation to change the state
    - it is not modelled as world state as in "I want a burger = True"
    - Really think about a phrase as setting up all the various variables so that the verb can be called
      - Really it just means: this is the proper interpretation, but it might be an error, in which case it can do a RespondOperation
    - delegate to "give me" *as one alternative* if it works, great!
      - If: it is a proposition and IF pron(I) and IF arguments are bound: There is something concrete they want, next determine how to deal with it
          - in the doorway: "I want a table" -> give me a table, "I want a place to sit", "I want to eat " (different want_v), I want a burger" -> "Do you want take-out?"

- Switch the code to use the term "scope-resolved MRS" instead of "well-formed tree" or "scope-resolved tree"
- 3 files are in a folder together -> There is more than a folder together
  - "together_p" is applied to "a folder" and returns an error that there is more than 1 folder "together"
    - together requires sets of more than one be generated, and "a_q" means exactly one
    - Probably should be a special case error if there is a min=1, max=1 constraint on a variable that only generates > 1?
- Really slow: (if at least one isn't) "file1.txt", "file2.txt" and "file3.txt" are in this folder
- 1 file is in a folder together
  - udef(card(1)) is the determiner for this
- How to MRS generate strings that represent the variable at the end of the whole sentence?
  - Theory: Put a quantifier in front of the whole tree?
  - sstring can use MRS generation even in non-default meaning_at_index cases if nothing will contribute english to it
- Will usability: error_priority_function should have a perplexity default that is not "no prioritization". Should at least deprioritize "I don't know word x"
- CARG arguments for things like "polite": "please, could I have a table" in the MRS the argument is first, but in the tree it is last
  - same thing for card(e,x,c) becoming card(c,e,x)
  
- How to deal with "I want a strawberry" when we know about strawberries but there aren't any
  - Do we need different messages based on the state of the world? For example, in the doorway: ""
  - create an object called "CanonicalInstance()" if we are talking about a think "in principle" like "I'd like to order a strawberry"?
  - How to think about it:
    - In a given context, whether something exists or not might elicit a different response, thus a different error
    - We could let verbs handle whether an item is a "canonicalinstance()" or not

- How to answer "what is on the menu?" or "what items are on the menu?" with "we have a lovely selection of ..." 
  - Conceptually this means: read the menu
  - Unbound "what" can trigger an action that adds operations to the results
    - Need a way to insert the beginning "We have a lovely section of " and then the list: x, y, z all from the on_p predication
      - And each one will be a different solution. The user could have said "what are 2 things on the menu?" -> which probably shouldn't have "we have a lovely selection of..." in it
        - But: the on_p predication can't tell
        - Maybe there is a RespondCommand if the whole set is used, and another for a subset?
        - Or there is some kind of global event that gets called to decide the pre and postamble?
          - Could it be a "solution group" event?
  - The question "is fish on the menu" should be answered with "yes"
  - Look at what we did in adventure.pl with querySetAnswer()
    - Possibly we need different predications for attributive vs. predicative? Or index?
- Add chat_gpt code so we can play with using it for nouns

- Docs: Need to write a section on predication design
  - Objects should be implemented purely and independently so that the magic of language and logic "just work"
  
Plurals work 
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
                    - "quoting" has to be special case code per predication because conversion into a canonical form is per predication and not directly determinable from arguments. For example "copy the file above folderx" has above(folderx) but the copying should happen in the folder above it
  - also copy x in y (the same scenario)

  - Support for prepositions
    - show declaring verbs that understand prepositions
  - Theory: We don't need to choose different variations of the index of the phrase based on "comm", "ques", etc
    - Except: if we want to use abductive logic to make "The door is open" not evaluated as a question, but as a desire to make that true and then make it true in the system

