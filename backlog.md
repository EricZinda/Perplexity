- Clean up conceptual versions of have_v and order_v as per nonlogicalquerydesign.md
- Make esl/table pass

- Fix the planner to use stop_plan_with_error instead of messages when the plan doesn't work

- We have 0 menus -> No. you does not have something 
- When trying alternative trees, it seems like errors need to be retained as alternatives are tried so they all start from the same base error
                
- Do we still need frames with the new concept handling?
- "What did we order?" -> Nothing
  - Because "we" didn't order anything...Just I did
- Do I have a son?
- "Who has steaks?" returns an error from referring_expression. Non-optimal
- Can I have a steak?
  - concepts are included in combinatoric with instances
- what specials do you have?
  - treats types as referring expressions
  - Need to convert to Concepts
  - look for all object_to_store() references and make sure they shouldn't be referring_expression
  - 
- referring expressions are different than types. A referring expression can generate types
  - Need to rename these to "referring expressions"
  - Need to rethink what it means for a solution group to have a referring expression in it
    - Does this mean that the solution group handler is looking for the referring expression to return *types*? and we have to check if those *types* meet the criteria?
    - This is a pretty different way of thinking about "concepts" as they were referred to before and may cause lots of code to get rethought
    - BUT: This seems like a clearer way to think about what is going on:
      - The solver generates solution groups with referring expressions
      - Those get resolved into types and instances which get processed
      - etc.
      
- If you say "which dishes do you have?" no concepts are returned since they are filtered out by referring expression
  - But if we return all concepts, it will include "dishes" too
    - The referring expression should always return concepts *that aren't the same as the original*

- have_v and order_v are both just about verifying facts in the world, so they should be implemented the same
  - Alternative Implementation
    - There should be one function for have_present() that are straight fact checking routines, that allows the system to just run the query
      - Anything that needs special handling should go to another routine
        - If it is implied request for something else, it should
        
  - Implementation
      Only handle: "I ordered the (conceptual referring expression)"
      We need to process the conceptual version of the referring expression
      to properly handle "I ordered the soup" because "the soup" needs to be interpreted
      as an "in-scope concept" and not "the one soup on the table" (or something similar)
      And since we already have to process the conceptual referring expression, we will also
      use conceptual for all phrases like "I ordered a soup" since they all work the same

    - check_conceptual will ensure that there is "the soup"
    - evaluating the referring expression will find all the things that the referring expression refers to
      - then you can see if those things were "ordered" or "had"
    - If the user asks, "Do you have a steak" or "Do you have the steak" we have options:
      - We could resolve the referring expression and make sure the computer has an instance of a steak
      OR
      - We could see if they have the concept of one
      
- Bug: "I have the soup" should work when I have *a* soup
  - "I have the soup" --> There is more than the soup
      
- Doesn't seem like we should have to model the computer as "having the concept of menu?"
- "who has which dish" doesn't work

- I don't have *the* soup works because:
  - there is more than one soup so negation fails, and thus this works
- "a table for two" crashes at startup
- I don't have soup / have soup both work when you have ordered soup
  - because:
    - for "I don't have soup" the first MRS is the proper interpretation meaning "not(I have soup)"
      - but it fails since you *do* have soup, so we keep going
    - the second interpretation of "I don't have soup" means "check each soup and see if you have it" and there are some that you don't have
      - so it succeeds and we return this one
  - Same thing will happen with "I don't have a soup"
  - Posted a question on the forum for this

- "What is not soup" --> crashes
  - Can't handle unbound variable in not()
- How many steaks did I order --> doesn't work
- How much is the soup and salad doesn't mark you as knowing the price
- Getting a menu should pass the menu concept all the way through so it can be evaluated
- Get rid of extra arg in relationships 
- Do we really need frames()? Only one test breaks if we turn it off
- Make "find unused thing" use concept
- Make "check conceptual constraints" properly use eval too

- Make eval() and concepts work more systematically
  - Option 4: Build the concept from the tree directly
    - Find the quantifier for the noun variable
    - Pull off the RSTR?
    - It could literally be implemented by the quantifier converting the RSTR to a concept instead of evaluating it...
    - This seems like the best way to go

  - what vegetarian dishes do you have?
  # - "what food/dishes/vegetarian dishes/food do you have?" --> implied request for description of menu
  # - "what steaks do you have?" --> implied request for description of menu
  #   support:
  #   "what food do you have?"
  #   "which dishes do you have?"
  #   "what vegetarian dishes do you have?"
  #   "what is the food that you have?"
        {
            "Command": "what food do you have?",
            "Expected": "Sorry, you must be seated to get a menu",
            "Tree": "_a_q(x11,_menu_n_1(x11),pronoun_q(x3,pron(x3),_see_v_1_able(e2,x3,x11)))",
            "Enabled": true,
            "ID": "98aa8219-aea7-4a10-a917-21bd96368a2d"
        },
        {
            "Command": "which foods do you have?",
            "Expected": "Sorry, you must be seated to get a menu",
            "Tree": "_a_q(x11,_menu_n_1(x11),pronoun_q(x3,pron(x3),_see_v_1_able(e2,x3,x11)))",
            "Enabled": true,
            "ID": "98aa8219-aea7-4a10-a917-21bd96368a2d"
        },
        {
            "Command": "which dishes do you have?",
            "Expected": "Sorry, you must be seated to get a menu",
            "Tree": "_a_q(x11,_menu_n_1(x11),pronoun_q(x3,pron(x3),_see_v_1_able(e2,x3,x11)))",
            "Enabled": true,
            "ID": "98aa8219-aea7-4a10-a917-21bd96368a2d"
        },
        {
            "Command": "what vegetarian dishes do you have?",
            "Expected": "Sorry, you must be seated to get a menu",
            "Tree": "_a_q(x11,_menu_n_1(x11),pronoun_q(x3,pron(x3),_see_v_1_able(e2,x3,x11)))",
            "Enabled": true,
            "ID": "98aa8219-aea7-4a10-a917-21bd96368a2d"
        },
  
- I want a table, 2 --> Fail
  - Adding a new predication to a concept may introduce a new variable
  - That variable won't have its execution metadata filled in because it wasn't part of the tree
  - Fix: eval() needs its own execution context since it could have anything in it
  - Need to fix the hack that says this:         # TODO: This is a hack to enable metadata for eval(). Need to fix it

- lift_style_predication_2
  - should assert if the predication doesn't allow for > 1 in the set
- What do I have? -> should say son
- 
- I want to sit down?
- could I sit down?
- 
- "I will see menus" --> works, but shouldn't
- implement future tense get
  - Will I get a menu?
- Make "I take a steak" or "I get a steak" say "Did you mean X"
- "Do I/my son have a menu?" doesn't work
- "What did I order?" --> Make work for debugging
- implement past tense get: "Did I get a steak?"
- Can we automatically call count_of_instances_and_concepts() for conceptual stuff? So that we don't have to call it in the group?


- "what are your specials?" --> There isn't a special in the system
- "What do you have?"
    - In the context of the entrance, this *could* mean "do you have a table for us?" or "Do you have a menu?"
    - at the table it means the menu
- Make "how much are your dishes" work
- Get rid of old code
- Verbs should declare what tenses they deal with, if none, they should default to present only
- Figure out how to make "I want 2 steaks and 1 salad" work
  - it only sends "2 steaks" to want so that is all that gets checked
- Get the bill working
- Make "What is not on the menu?" work properly
- Get rid of old code that has been implemented differently
- Fix ontology.  Right now there are instances on the menu, for example
- Handle concepts with extra information "bill for the food" failing if we don't know it
- I'd like 2 steaks at the front door -> doesn't work

- Demo for summit
  - card() not in rstr
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
                    - "quoting" has to be special case code per predication because conversion into a canoncal form is per predication and not directly determinable from arguments. For example "copy the file above folderx" has above(folderx) but the copying should happen in the folder above it
  - also copy x in y (the same scenario)

  - Support for prepositions
    - show declaring verbs that understand prepositions
  - Theory: We don't need to choose different variations of the index of the phrase based on "comm", "ques", etc
    - Except: if we want to use abductive logic to make "The door is open" not evaluated as a question, but as a desire to make that true and then make it true in the system

