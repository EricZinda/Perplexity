Upload to itch.io:
- https://htmleditor.io/
- https://onlinetools.com/image/convert-image-to-data-uri


- Need to update the ubuntu and M1 grammar to 2024


Bugs:
    High Pri:
        - which chicken menu items do you have? --> pork
                soup
                salad
                steak
                chicken
                salmon
                '_which_q(x5,udef_q(x10,udef_q(x16,_chicken_n_1(x16),[_menu_n_1(x10), compound(e15,x10,x16)]),[_thing_n_of-about(x5,i21), compound(e9,x5,x10)]),pronoun_q(x3,pron(x3),_have_v_1(e2,x3,x5)))'
                Theory: the problem is that one iterpretation is "chicken menu" (items) and another is "chicken" (menu items), we want the later.  It may just take a long time to get there?
        - (ChatGPT) Could we have a vegetarian menu? --> Host: Sorry, I don't know how to give you that.
        - which dishes are specials -> veggie, meat
            - _which_q(x5,_dish_n_of(x5,i9),udef_q(x3,_special_n_1(x3),_be_v_id(e2,x3,x5)))
        - How much does the soup and the salad cost? --> I don't know the way you used: cost
            - Needs to be cost_v_1() but referencing and?
        - "Did I order a steak for my son?" -> I'm not sure what that means.
        - USER: I don't want the chicken -> yes that is true
            - That isn't true, there isn't the chicken that isn't the chicken
        - what is the green thing/what is the green item
            - don't work
    Low Pri:
        - Figure out how to make "I want 2 steaks and 1 salad" work
            - It only sends 1 steak to order
        - "I will see menus" --> works, but shouldn't
        - Make "What is not on the menu?" work properly
            - it returns everything
        - I have 20 dollars -> you did not have 20 dollar
        - I will have any meat -> Sorry, I'm not sure which one you mean.
            - Also: I will have any meat dish
            - pronoun_q(x3,pron(x3),_any_q(x8,_meat_n_1(x8),_have_v_1(e2,x3,x8)))
            - should be: Wait, we already spent $20 so if we get 1 steak, we won't be able to pay for it with $20.
            - Do referring expression concepts have to capture the quantifier?
                - "I like any meat" shouldn't pick an arbitrary one
                - 1..inf is correct, but also needs to capture the "any works" as opposed to "a" which might care if there
                 are different unfungible choices
        - Need to handle other adjectives used predicatively for ordering like "what is cheap?" by
        - what is a table for 2? --> no answer?
        - What is my food? -> never finishes?

Cleanup:
    Hi Pri:
        - Stop processing after some time and give the best answer so far
        - Tests don't properly record output from events (like restarting the game)
        - very slow
            - how about a vegetarian soup?
                also: how about a soup
            - for my son, Johnny, please get the Roasted Chicken
                - does it ever work?
            - Table (then) Just two, my son Johnny and me.
                - takes forever to get to parse 88,1 which is the first that works
                - ditto for: We'd like to start with some water and menus
                    - /runparse 2, 39

            - "My order is chicken and soup" fails properly but takes forever and gives a bad error
            - My son needs a vegetarian dish
            - My soup is a vegetarian dish
            - Which 2 dishes are specials
            - We'll have one tomato soup and one green salad, please
            - what are specials -> very slow (but correct)
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
        - Make transformers more understandable and debuggable

    Low Pri:
        - Conjunctions can't be root transformers
        - Do we still need frames with the new concept handling?
        - lift_style_predication_2
          - should assert if the predication doesn't allow for > 1 in the set
        - Finish removing combinatorics since it simply fails for a lot of cases and complicates the code
        - New Programming Model todo:
          - Need to recheck constraints if names are changed
          - Get rid of old metadata that doesn't have a function anymore, e.g. if the developer has it then deletes it
          - Need to support wh-question examples as a way to filter out those when necessary too
        - Get rid of reordering
          - If you get rid of reordering, then you don't have to worry about unbound in most predications which is nice
          - But we need a way to optimize somehow, it really is slow
            - Use the GPU for some parallelization? https://numba.pydata.org/
          - Timing with reordering:
            - filesystem: 231.11059
          - Timing without:
            - filesystem: 292.00379
        - Get rid of extra arg in relationships
        - Can we automatically call count_of_instances_and_concepts() for conceptual stuff? So that we don't have to call it in the group?
        - redo all the noun() type predications to properly return notathing and look like match_all_n_concepts
        - Rename lineage something like disjunction
        - Clean up unused portions of state.handle_world_event()
        - There should be an exception if lift is called on a function that doesn't have its parameters marked as taking all types of sets
        - Fix some of the user interface issues:
            - implement a timeout
            - do a better response than "I don't understand the way you used X" and other default messages
                - I don't know the words: plase/nn and I don't know the way you used: for
        - change all the could/can transforms to use OR so there are less
        - Need to check if we are dealing properly with "I want 2 steaks and 2 salads".  [2 steaks and 2 salads] comes in as a single variable, with no constraints (it is a conjunction), right? Have we lost the constraints for the conjunct variables?
            - It does have the requirement that it contains an element of each, but pretty sure we've lost the original constraints
        - Need to think this through: Disabling RSTR/BODY reversal means that "what can I order?" will always be bound.  I.e. using the unbound method as a proxy for "asking a question" is wrong.
        - allow solution handlers to say "I'm it!" just like groups so the other handlers don't have to run
        - Have a method to call to say "continue" in a solution group handler instead of calling report_error("formNotUnderstood")
        - Performance fix: checkin was cca6733
            Before allowing rules to continue running over a transformed tree:
                  Elapsed time: 647.23938
            After:
              Elapsed time: 979.71158

New Language:
    Hi Pri:
        - USER: table for two thank you -->  I don't know the way you used: for
        - ? I'd like a table
            Host: How many in your party?

            ? we have 2
            you did not have 2 thing
            Host: How many in your party?

        - USER: table for two people -> I don't know the words: people
        - USER: and salmon
            I don't know the words: salmon
        - USER: i would like to order a meal for me and my son -> I don't know the words: meal
            - maybe just synonym for dish??
             One regular meal for me, and one vegetarian meal.
                I don't know the words: meal, meal

        - USER: Nothing, thank you.
            I don't know the words: addressee
        - USER: Thank you, that is all for now
            I don't know the way you used: all
        - USER: We are fine, thank you
            ('user',) is not we
        - You’re going to a restaurant with your son, Johnny, who is vegetarian and too scared to order by himself. Get a table and buy lunch for both of you. You have 20 dollars in cash.
            - Should be: You’re in the lobby of a restaurant with your son, Johnny, who is vegetarian and too scared to order by himself. Get a table and buy food for both of you. You have 20 dollars in cash.
        - USER: I'm good
            I don't know the words: good
        - USER: We're okay
            I don't know the way you used: okay
        - Errors of unknown words should say the actual word

        - USER: what do you have on the menu?
            I don't know the way you used: on
        - USER: menu options --> Waiter: steak is an excellent choice!
        - USER: do you have any vegan food -> I don't know the words: vegan
            Should say "Dad I'm a vegetarian!"
        - USER: Can i order? -> I don't know the way you used: order
        - USER: I would like to order lunch ->  I don't know the words: lunch
            - also dinner, breakfast
        -  14 people ->  I don't know the words: people
        - USER: table
            Host: How many in your party?
            USER: 14
            Host: Sorry, I don't know how to give you that.
            - SHould be: too many!
        - If you get N failures in a row, give help?
        - USER: how much does water cost -> There are less than 1 thing
        - USER: another water -> I don't know the words: another
        - Just a couple waters thanks --> Sorry, I don't know how to give you that.
        - a couple glasses of water -> Sorry, I don't know how to give you that.
        USER: Get my son three salads
            - I'm not sure what that means.
        - How much for salad
            I don't know the words: measure
        - How much for a salad
            -- I don't know the words: measure

        - what do u have here? -> I don't know the words: place
            -
        - USER: Tomato soup and a green salad sounds great for my son
            I don't know the words: green

        - implement: let's start again
        - I wont get the steak --> Yes, that is true.
        - Remove the steak --> I don't know the words: remove
        - Actually I won't have the steak --> I don't know the words: actual
        - ignore what I ordered

        - what do you have to eat?
        - what do you guys have?
        - what do you guys serve?

        - we're good. thanks! --> Should be no
        - not right now
        - I don't want anything else.  is very slow
        - Not right now, thank you. --> doesn't work
            - not right now

        -  Hi, I'd love to have a table for 2, please
            - Runs this: discourse(i2,greet(hi,i6),_please_a_1(i33,_a_q(x20,number_q(x26,card(2,x26,i32),[_table_n_1(x20), _for_p(e25,x20,x26)]),pronoun_q(x3,pron(x3),_have_v_1_request(e13,x3,x20)))))
                and discourse is the index, so it just says "yes"
        - USER: I will have the steak, and my son will have the chicken
            I don't know the way you used: and
            because it is _and_c(e, e, e) and we don't know that one,  The index goes to and_c

        - I don't know the words: hamburger
            - Use chatgpt to give a better error
        - that would be it, thanks
        - And are there any other non meat options --> yes
            - did this really work??
        - USER: How much do the meals cost?
            - I don't know the words: meal
        - How much are each of the vegetarian options?
        - Card, please --> I don't know the way you used: polite
        - How much are each of the specials? --> I don't know the words: part_of
        - how about vegetarian soup? --> I don't know the words: generic_verb, how+about
            - Need a better error message
        - how about a soup? --> I don't know the words: generic_verb, how+about
        - we'd both like waters to drink please --> doesn't work
        - what is vegetarian on the menu
        - USER: what other options are on the menu
            No. ESLConcept(dish: [(<function rel_subjects at 0x7f01fdc05a60>, 'isAdj', 'other')] ) is not on ESLConcept(menu: [] )
            Waiter: What can I get you?
            Waiter: What can I get you?
        - what do you have on your menu? --> doesn't work
            what vegetarian items do you have on your menu?
        - could I get a soup? is very slow when you don't know the cost

        - Work through cancelling order language
            Could you cancel the steak I ordered earlier?
                Requires implementing:
                        ┌──── more_comp(e29,e28)
                        │ ┌── time_n(x23)
               ── and(0,1,2)
                           └ _early_a_1(e28,x23)
            Can you please take the soup off my order
            - "cancel the order for me" --> "for me" isn't implemented as possessive
            - can you remove the salad from my order
            - start over please
            - Let's start again
            - could we reorder?
            - could we redo my order?

        - table for two please
            - also: table for two, please
            - only generate _for_x_cause, unclear what that means
            - Theory: suspect this might fix it: https://delphinqa.ling.washington.edu/t/hi-table-for-2-please-missing-parse-with-discourse-greet-and-please-a/1017/4
            - Need to try the daily grammar
        - could I sit down?
        - we want to sit at a table
        - support "can we be seated?"
        - can I pay for the bill?
        - (ChatGPT) Could you recommend a few vegetarian options, then?
            - Also: Could you please recommend a vegetarian dish for my son?
        - (chatGPT) How much does the tomato soup and the green salad cost? --> I don't know the way you used: cost
            - Parse 26
        - (chatGPT) Johnny and I will both have the Roasted Chicken
            - Unclear how to deal with "will both have": https://delphinqa.ling.washington.edu/t/what-is-the-common-mrs-between-we-both-will-have-soup-we-will-both-have-soup-meaning-2-of-us-will-have-soup/1011
        - (ChatGPT) In that case, I'll have chicken
        - (ChatGPT) Here is 15 dollars
                 udef_q(x3,[_dollar_n_1(x3,u16), card(15,e15,x3)],def_implicit_q(x4,[place_n(x4), _here_a_1(e9,x4)],loc_nonsp(e2,x3,x4)))
                 implicit command triggered by an observation
        - how can I pay the bill?
        - (ChatGPT) Let's go to a table, please. --> I don't know the words: to
        - "at the moment" should be ignored

    Low Pri:
        - Convert plz to please
        - Convert u to you
        - I'd like to get two menus
            Waiter: Our policy is to give one menu to every customer ...
            Waiter: What can I get you?
            Waiter: What can I get you?
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
        - "how much *is* the soup and salad" is crazy slow and will never work        - I want to sit down?
        - implement past tense get: "Did I get a steak?"
        - "I want my order to be chicken" -> I don't know the way you used: want
        - implement "how many vegetarian dishes are there" -> I don't know the words: measure
        - implement "how many vegetarian dishes do you have?" -> I don't know the words: measure

        - "I'll just have a menu"
            - Need to implement "just" means: clear the order and just give me that thing
        -	And the implied request given by: “My son is a vegetarian”


- ChatGPT scenario:
  - You’re going to a restaurant with your son, Johnny, who is vegetarian and too scared to order by himself. Get a table and buy lunch for both of you. You have 15 dollars in cash.
  I am the waiter, you are the customer.  Interact with me only saying one sentence at a time and waiting for my response. Make the phrases very simple. OK?


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


- Handle concepts with extra information "bill for the food" failing if we don't know it
- Not issues: For Example23
  - large files are not in this folder -> Yes, that is true.
    - Interpreted as not(large files in this folder)
- Bug: It looks like collective only checks for one value???
    - whole_group_unique_individuals.update(binding_value) never adds a set of individuals to the set
- make fallback generation more robust
  - at least getting form of words right
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

