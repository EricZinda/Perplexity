

Big Improvements:
    - Get a better tree morpher
    - better tree manipulations

Bugs:
    High Pri:
        - Concept can't properly represent "table for a person" because quantifiers don't add anything...Is that OK?
        - which chicken menu items do you have? --> pork
                soup
                salad
                steak
                chicken
                salmon
                '_which_q(x5,udef_q(x10,udef_q(x16,_chicken_n_1(x16),[_menu_n_1(x10), compound(e15,x10,x16)]),[_thing_n_of-about(x5,i21), compound(e9,x5,x10)]),pronoun_q(x3,pron(x3),_have_v_1(e2,x3,x5)))'
                Theory: the problem is that one iterpretation is "chicken menu" (items) and another is "chicken" (menu items), we want the later.  It may just take a long time to get there?
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
        - Need a tool that processes a log, records the phrases and whether they have been seen before and counts them,
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
    Don't try different scoping trees that are equivalent
    Hi Pri:
- Figure out what happened here
        - Support
            "I want to eat"
            "I want to eat lunch"

        - Figure out what happened here
            --------------- 2024-07-14 23:05:57.968165 - ip-10-0-0-74.ec2.internal@1013: Interface:REST-, AfterInteractionData: YTd1N2h1NHp5aGpseW01cXpsbQ==-230557968143.backup
            - USER: Could i have a table for two please.
                Sorry, did you mean to say something?
                Host: How can I help you today?

        - Need a cleaner ending that isn't so open ended since it just causes failures
        - USER: What are the daily specials?
            ('soup0',) is not the special
            USER: cash is fine.
                ('cash',) is not cash
                Waiter: So, do you want to pay with cash or card?

        - USER: Are there any vegetarian options?
            Yes.
            Waiter: What can I get you?
            - Also: USER: is there a vegetarian menu
                Yes.
                Waiter: What can I get you?
        - USER: Tomato soup, green salad, and roasted chicken
            Waiter: soup is an excellent choice!
            Son: Wait, let's not order salad before we know how much it costs.
            chicken is not roasted.
            Waiter: Can I get you anything besides 2 soups for you?
            Waiter: Can I get you anything besides 2 soups for you?
            We never get a solution group with x4 set to distributive or collective values for all 3 items
                - suspect an and_c problem
                                                                               ┌── _salad_n_1(x25)
                                                                   ┌────── and(0,1)
                                                                   │             └ _green_a_2(e29,x25)
                                              ┌────── udef_q(x25,RSTR,BODY)
                                              │                         │                           ┌── _chicken_n_1(x31)
                                              │                         │               ┌────── and(0,1)
                                              │                         │               │             └ _roast_v_cause(e36,i37,x31)
                                              │                         └─ udef_q(x31,RSTR,BODY)
                         ┌────── _tomato_n_1(x│4)                                            │
            udef_q(x14,RSTR,BODY)             │                                              │
                              │               │                                              └─ _and_c(x20,x25,x31)
                              └─ udef_q(x20,RSTR,BODY)
                                                   │                                  ┌────── compound(e13,x9,x14)
                                                   │              ┌────── udef_q(x9,RSTR,BODY)
                                                   │              │                        └─ implicit_conj(x4,x9,x20)
                                                   └─ udef_q(x4,RSTR,BODY)
                                                                       └─ unknown(e2,x4)


        - Tomato soup for Johnny and the steak for me, please. --> Host: That is not for both steak0.
        - USER: a menu, to start
        - USER: Well, a menu, to start, would be wonderful/nice/awesome. --> I don't know the words: Well
            - a menu to start doesn't work either
        - USER: can I order chicken? -> I don't understand the way you are using: order

        - veggies -->  I don't know the words: veggies
        - 1 order of water doesn't work
        - my son's order is a glass of water --> nothing
            -even when he just ordered it

        - USER: how much would a salad cost
            I don't know the words: how, how
            Waiter: What can I get you?
        - USER: I would like to pay cash please
            I don't know the words: would, like and I don't know the way you used: pay
        - USER: what do you have on the menu?
            I don't know the way you used: on
        - Can I cancel our order?
            - just responds to order for user
            - because nobody makes sure the variable for poss() has multiple items in the solution
        - what do you have for lunch?
        ?:my son is vegan
            my son is not veggie
            Waiter: What can I get you?
            - also: My son Jimmy is vegetarian.
        - USER: My son Jimmy is vegetarian. Are there any options for him to eat?
            I don't know the words: My
            I don't know the words: eat
        - (at the door) USER: Please bring our menus --> I don't know the way you used: bring
        -   USER: Menus, and two hot waters.
                Waiter: Oh, I forgot to give you the menu! I'll get you one right away.
                Host: Sorry, I don't know how to give you that.
        - we're here for lunch --> I don't know the words: here, lunch
        - USER: Can i order? -> I don't know the way you used: order
        -  Salads please --> Can I get you anything besides a salad for you?
            - Only ordered 1!
            - Same here:
                USER: Two waters, please.
                Waiter: water is an excellent choice!
                Waiter: Can I get you anything besides a steak and a water for you and a salad for Johnny?
        - Do we have silverware? --> Sorry, did you mean to say something?
        - USER: can you get me a fork and a spoon?
            I don't know the words: fork, spoon
            Waiter: Can I get you anything besides a menu and a water for you?
            - USER: I would like a napkin
                I don't know the words: napkin
                Waiter: Can I get you anything besides a menu and a water for you?
            - Can we model these as simple things the user has that you can't really do much with?

        - i want you to give me a menu
            I don't know the words: in+order+to and I don't know the way you used: give

        - ? I'd like a table
            Host: How many in your party?

            ? we have 2
            you did not have 2 thing
            Host: How many in your party?

        - Saying "no"
            - USER: Nothing, thank you.
                I don't know the words: addressee
            - USER: Thank you, that is all for now
                I don't know the way you used: all
            - USER: We are fine, thank you
                ('user',) is not we
            - USER: I'm good
                I don't know the words: good
            - USER: We're okay
                I don't know the way you used: okay
            - USER: I'm good
                I don't know the words: good
            - USER: Not yet.
                I don't know the words: Not yet
            - USER: Nothing else, thank you.
                I don't know the words: thank you and I don't know the way you used: Nothing
        - order meal --> I don't think we have that here
            - order vegetarian --> Host: I'm sorry, you can't order that here. Take a look at the menu to see what is available.
            - Need to implement the rude "order x"
            - this is being interpreted as "order of meal"
            - I want to order a meal --> You already ordered a menu for you
                - that works

        - what do you have to eat?
            USER: What do you have to drink?
                I don't know the words: to
                Waiter: What can I get you?
        - USER: What do you have for a vegetarian?
            I don't know the way you used: vegetarian
            Waiter: What can I get you?
        - USER: I would like something to drink.
            I don't know the words: would, like, drink
            Waiter: Can I get you anything besides a menu for you?
        - USER: We need utensils and napkins.
            I don't know the words: utensils, napkins
            Waiter: Can I get you anything besides a soup and a salad for you?
        - USER: What is the price for each special? -> I don't know the words: price
            - need to implement price
        - USER: i would like to order a meal for me and my son -> I don't know the words: meal
            - maybe just synonym for dish??
             One regular meal for me, and one vegetarian meal.
                I don't know the words: meal, meal
        - USER: I would be happy with the steak but my son is a vegetarian.
            I don't know the way you used: vegetarian
            Waiter: Can I get you anything besides a menu and a water for you?
            - Handle "but" like and???
        - please order me chicken
            Doen't work
        - USER: I'll have the steak and Johnny will have the green salad.
            I don't know the way you used: and
        - USER: I would like to order lunch ->  I don't know the words: lunch
            - also dinner, breakfast
        - If you order food that we don't have it should say "just get something on the menu"
        - USER: a party of 2
            I don't know the words: party
        - USER: Can I get 2 of them please? --> I don't know the words: 2
            - 1) bad error
            - 2) need to implement pronouns
        -  order tomato soup --> Host: Sorry, I don't know how to give you that.
        - USER: Two waters to drink
            I don't know the words: to
        - USER: are there any non-meat dishes?
            Yes.
            Waiter: Can I get you anything besides a menu and a water for you?

        - Lots of people ask Johnny what he would like:
            - Anything that addresses johnny should give a particular message?
            - Johnny, what would you like? --> I don't know the words: Johnny,
            - USER: johnny, what do you want?
            - my son will tell you what he wants
        - we'd like dessert -> I don't know the words: dessert
        - USER: can I order a salad and a grilled salmon
            I don't understand the way you are using: order
            Waiter: What can I get you?

        - Need to tell them that we don't have a menu yet
            USER: read menu
            I don't know the words: read

            Waiter: Can I get you anything besides a water and a menu for you and a menu for Johnny?

            --------------- 2024-07-08 19:30:44.944773 - ip-10-0-0-198.ec2.internal@25: Interface:REST-, AfterInteractionData: dDVvMmJkMWh3aGNseWRkbTc2eQ==-193044944749.backup
            USER: I'm unable to read. would you please read me the menu?
            I don't know the words: unable
            I don't know the words: would, read

            Waiter: Can I get you anything besides a water and a menu for you and a menu for Johnny?
         -   Waiter: What can I get you?
            USER: vegetables
            I don't know the words: vegetable
            Waiter: What can I get you?
        - USER: Oh one of the chicken too
            I don't know the words: one
        - USER: Yes, what vegetarian dishes do you have?
            Ok, what?
            Waiter: Ah, I forgot to tell you about our specials. Today we have tomato soup, green salad, and smoked pork.
            Waiter: Can I get you anything besides a water for you?
            - "Yes" triggers "OK, what?"
        - USER: Water please, and menu
            Sorry, did you mean to say something?
            - Need a better response for when something doesn't parse
            - Another example: USER: Tomato soup for my son, and do you have something from chicken for me?
                Sorry, did you mean to say something?
                Waiter: Can I get you anything besides a water for you?
        - USER: my son does not eat vegetables
            I don't know the words: vegetable
            - Also:My son is vegetarian
            - Also: USER: my son does not eat meat
        - USER: is there a vegetarian option
            Yes.
            Waiter: Can I get you anything besides a salmon for you?
        - Waiter: What can I get you?
            USER: Nothing
            Waiter: I'll be right back!
            A few minutes go by and the waiter returns.
            Waiter: What can I get you?
            - should not have gone back!

        - ? I'd like a table
            Host: How many in your party?

            ? we have 2
            you did not have 2 thing
            Host: How many in your party?
        - USER: We need a minute to decide.
            I don't know the words: minute

        - USER: table for two people -> I don't know the words: people

        - If the commands are all one word, give a message about full sentences
        - Come up with a better ending, right now it just loops and there is not satisfying end
            - goodbye
            - quit
            - end
            - etc.
        - ?:vegetables
            I don't know the words: vegetable
        - USER: I want a green thing
            Sorry, did you mean to say something?
            also: USER: I'd like a green thing
                I don't know the words: 'd, like

        - You’re going to a restaurant with your son, Johnny, who is vegetarian and too scared to order by himself. Get a table and buy lunch for both of you. You have 20 dollars in cash.
            - Should be: You’re in the lobby of a restaurant with your son, Johnny, who is vegetarian and too scared to order by himself. Get a table and buy food for both of you. You have 20 dollars in cash.

        - USER: menu options --> Waiter: steak is an excellent choice!

        - USER: Free appetizer?
            I don't know the words: appetizer
            Waiter: Can I get you anything besides a menu for you?
            - We should at least know the word
        - USER: Johnny, what would you like to drink?
            I don't know the words: Johnny,
            Waiter: Can I get you anything besides a menu for you?
            - Also: USER: talk to johnny
                I don't know the words: talk
                Waiter: Can I get you anything besides a water for you?

            - This is not true, we *do* know the words
            - Also: Need to notice when they are talking to another person
        - USER: How about another table?
            I don't know the words: How about, another
            Waiter: Can I get you anything besides a menu for you?
            - "How About" should be ignored
            - "Another should not"
        - USER: May I have a vegetarian menu?
            Host: Sorry, I don't know how to give you that.
            Waiter: What can I get you?
            - Should tell the specials
        - USER: Could I get another menu, please?
            I don't know the words: another
            Waiter: Can I get you anything besides a water for you?
        - USER: just get the water.
            I don't know the way you used: just
            Waiter: Can I get you anything besides a menu and a water for you?
        - If you have two waters: USER: I don't want water!
            Waiter: I have removed a water from the order for you.
            Waiter: Can I get you anything besides a menu and a water for you?
            - only removes one!
        - USER: Do you have any drinks other than water?
            I don't know the words: other than
            Waiter: Can I get you anything besides a menu and 3 waters for you?
        -  14 people ->  I don't know the words: people
        - USER: Get the kid a tomato soup.
            I don't know the words: kid
            Waiter: Can I get you anything besides a water and a salmon for you?
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
        USER: Give soup to son
            Sorry, did you mean to say something?
            Waiter: Can I get you anything besides a water and a salmon for you?
            - Still need to detect "computerese" and deal with it
        - How much for salad
            I don't know the words: measure
        - How much for a salad
            -- I don't know the words: measure
        - USER: order soup -> Host: Sorry, I don't know how to give you that.
            - should somehow say something about rudeness?
        - what do u have here? -> I don't know the words: place

        - what do you guys have?
        - what do you guys serve?
        - ways to say no
            - we're good. thanks! --> Should be no
            - not right now
            - I don't want anything else.  is very slow
            - Not right now, thank you. --> doesn't work
                - not right now
            USER: no that's everything
                I don't know the way you used: everything
            USER: Nothing else, thank you.
I                don't know the words: thank you and I don't know the way you used: Nothing
            -USER: Give us a minute.
                I don't know the words: minute

        - USER: Tomato soup and a green salad sounds great for my son
            I don't know the words: green
        - USER: Do you have anything with vegetables?
            I don't know the words: vegetables
            Waiter: Can I get you anything besides a water for you?
            - This is a failure case that wouldn't normally happen if the rest worked
        -USER: What do you have to drink?
            I don't know the words: to
            Waiter: Can I get you anything besides a water for you?
        - implement: let's start again
        - Yzl6OXRhZjg3c2tseW0yN2NuZg==-213801551568.backup
        - USER: Two of the salmon, please.
            I don't know the words: of
            Waiter: Can I get you anything besides a water for you?
        --------------- 2024-07-14 21:38:47.471504 - ip-10-0-0-74.ec2.internal@1013: Interface:REST-, AfterInteractionData: Yzl6OXRhZjg3c2tseW0yN2NuZg==-213847471481.backup
        - USER: tomato soup for son
            Host: Sorry, I don't know how to give you that.
            Waiter: Can I get you anything besides a water and a salmon for you?
            - Unclear h
        - I wont get the steak --> Yes, that is true.
        - Remove the steak --> I don't know the words: remove
        - Actually I won't have the steak --> I don't know the words: actual
        - ignore what I ordered
        - USER: Can you read the menu for me?
            I don't know the words: read
            Waiter: Can I get you anything besides a menu and a water for you?
        -  Hi, I'd love to have a table for 2, please
            - Runs this: discourse(i2,greet(hi,i6),_please_a_1(i33,_a_q(x20,number_q(x26,card(2,x26,i32),[_table_n_1(x20), _for_p(e25,x20,x26)]),pronoun_q(x3,pron(x3),_have_v_1_request(e13,x3,x20)))))
                and discourse is the index, so it just says "yes"
        - USER: I will have the steak, and my son will have the chicken
            I don't know the way you used: and
            because it is _and_c(e, e, e) and we don't know that one,  The index goes to and_c

        - USER: what vegetarian options can you offer
            I don't know the words: offer
            Waiter: What can I get you?
            - Also: USER: what vegetarian options can you cook
                I don't know the words: cook
                Waiter: What can I get you?
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
        - USER: Is there another menu
            I don't know the words: another
            Waiter: What can I get you?
        - USER: can i see the menu again
            Host: Sorry, I don't know how to give you that.
            Waiter: What can I get you?
            - again should be a NOOP
        - USER: is there salad
            Yes.
            Waiter: What can I get you?
        - Also: Read the menu
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
            USER: What's good to eat here? What do you recommend?
                I don't know the words: here
                I don't know the words: recommend
                Waiter: Can I get you anything besides a menu and a water for you?
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

