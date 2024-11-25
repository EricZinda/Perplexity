    Fix: "which files are not in 2 folders?",
        returns: There are less than 2 2 folder
            Theory: in_p_loc_fail__solution_group always reports "formNotUnderstood" and
            quantifier_raw() won't return the "there aren't any X" error if this is the recorded error
            - Solution: If all the solution group handlers report "notUnderstood", shouldn't it be treated
                like there are no solution group handlers instead of recording that error?

                                                           ┌── _folder_n_of(x12,i19)
                                               ┌────── and(0,1)
                                               │             └ card(2,e18,x12)
              ┌────── _file_n_of(x3,i8)        │
_which_q(x3,RSTR,BODY)         ┌─ udef_q(x12,RSTR,BODY)
                   └─ neg(e9,ARG1)                  │
                                                    └─ _in_p_loc(e2,x3,x12)

    - The problem is: The context for the outer tree is being updated by the inner tree
        - Once fixed we have the problem: Example28_reset: "which files in this folder are not large"
        There isn't a folder in the system
        Expected:
        There isn't a file in this folder not large
        The right error isn't being recorded because doesntExist gets forced and so the right one doesn't appear
    - (Fixed) Example31_reset: 4 files are in a folder
    - Example34_reset: 'file1.txt' and 'file2.txt' are in a folder together

# Big Changes
    - Fix handling of phrases that have multiple syntactic heads:
        - "I want soup, I want salad" --> two want_v_1 heads joined by impl_conj(e, e, e)
        - "Hi, I'd love to have a table for 2, please" --> greet() and have_v_1() heads joined by discourse(i, h, h)
        - The engine should process them as separate "conjunctions"
        - Really this should probably happen way early in the parse process where we split the trees into two different MRSs (or trees) to process
            - Right now it is happening at runtime when we evaluate
        - Right now we only do one pair of conjuncts and not the general case
        - select_tree_conjunct, vocabulary.py:789 is the place that handles it
        - Really we need a more robust pipeline. There are a few things going on in it
            - Transforming the original trees to new ones. This needs to account for the syntactic heads instead of indexes, and properly map the old heads to new ones as they get transformed
            - Transforming one MRS into several for either conjunctions or other constructs that generate multiple syntactic heads like "discourse"
    - Fix some of the user interface issues:
        - do a better response than "I don't understand the way you used X" and other default messages
            - I don't know the words: plase/nn and I don't know the way you used: for
    - Don't try different scoping trees that are equivalent
    - Get a better tree morpher
        - Make transformers more understandable and debuggable
        - Conjunctions can't be root transformers
    - make fallback generation more robust
      - at least getting form of words right
    - Concept can't properly represent "table for a person" because quantifiers don't add anything...Is that OK?
    - Support "not" properly
        - Need to properly test in restaurant scenario
        - Make "What is not on the menu?" work properly
            - it returns everything
        - Not issues: For Example23
          - large files are not in this folder -> Yes, that is true.
            - Interpreted as not(large files in this folder)
    - Need a tool that processes a log, records the phrases and whether they have been seen before and counts them,
    - If you get N failures in a row, give help?
    - Handle concepts with extra information "bill for the food" failing if we don't know it
    - I will have any meat -> Sorry, I'm not sure which one you mean.
        - Also: I will have any meat dish
        - pronoun_q(x3,pron(x3),_any_q(x8,_meat_n_1(x8),_have_v_1(e2,x3,x8)))
        - should be: Wait, we already spent $20 so if we get 1 steak, we won't be able to pay for it with $20.
        - Do referring expression concepts have to capture the quantifier?
            - "I like any meat" shouldn't pick an arbitrary one
            - 1..inf is correct, but also needs to capture the "any works" as opposed to "a" which might care if there
             are different unfungible choices

# Bugs
    # Pri 1
        - Document!!!! For the solution handlers for conceptual stuff, they should not allow solutions through that are not ever going to work
            - i.e. solution handlers should fail if the solution could never work in the solution group handler
        - Handling groups of things that can be "anded" goes beyond "want", look for other code with this problem


        - Write up how "and" works for solution group handlers
        - Make sure other constructions like "I ordered one steak" also work
        - order tomato soup --> sorry you can't order that here
        - Bug: When we run "I want one menu for me and two menus for johnny" there are different errors returned from each solution group
            - We record the last one that failed in solution_groups.py line 282
            - what we *should* be doing, is using the logic that ExecutionContext/UserInterface uses to compare them and return the *best* one
                - should the logic be: deepest, and then highest priority if there is a tie?
                    - but the trees will be different so "deepest" probably doesn't make sense
                    - so maybe it is just highest priority?
        - Bug: table for one person --> I'm not sure what to do about that
            - Seems to be the same bug as the previous one

        - Need to add tests to every kind of thing you can ask for to make sure we are handling criteria right
            - I want a water and a steak for me and 2 salads for johnny
            - I want a steak and the bill
            - Cancel 1 steak and 2 salads
        - Need to make check_concept_solution_group_constraints() actually check the constraints for anded value

        - Figure out how to make "I want 2 steaks and 1 salad" work
            - Problem: The constraints aren't pulled through the _and_c, just the required values and "NUM:PL"
            - For instances, the constraints on the predications that manipulate those values directly will ensure the solution group has the right count
            - For concepts: the problem is that we need a way to get the real constraints for each anded value
                - Need to capture
                - Need to make satisfy_want_group_group() able to figure out what is needed
                    - Need to make what_size_constraint() a list too and somehow populate it
                        - Need to capture the variable that is used for each part of the and as part of the and
                            - The solution group is either distributive (one value per solution) or collective (all values in one solution)
                                - we could ignore the combined value and just pay attention to the original referenced variables and the values they contain
                                    - We know that x8=2..2 and x9=1..1 but we don't know what the combined value contains
                                        - We need to record something in the actual binding
                                            - The binding information is changeable per binding, BUT: We currently use the first solution to work out the binding constraints and assume it is
                                                the same for all of them
                                            - Options:
                                                - leave the binding metadata to be just about this particular value
                                                - The metadata value could point us to which variables it came from
                                                - The function that scans the metadata has to walk the tree of metadata, which might lead to more metadata, since the and_c's could be chained
                                                    - The metadata needs to have a way to figure out if it is and_c or or_c, etc.
                                                - It really just needs to be a list
                                                    - The list should say which other variables this is composed of, so that they can be retrieved and tested
                                                    - It has to be the same constraint across the whole solution set since there is only one
                                                    - When we are dealing with concepts
        - How much does the soup and the salad cost? --> I don't know the way you used: cost
            - Needs to be cost_v_1() but referencing and?
        - "Did I order a steak for my son?" -> I'm not sure what that means.
        - USER: I don't want the chicken -> yes that is true
            - That isn't true, there isn't the chicken that isn't the chicken
            - This works because we haven't told the system that you want chicken and thus it assumes it is false.
        - I have 20 dollars -> you did not have 20 dollar

    # Pri 2
        - "I will see menus" --> works, but shouldn't
        - Need to handle other adjectives used predicatively for ordering like "what is cheap?"
        - what is a table for 2? --> no answer?
        - What is my food? -> never finishes?

# New Language
    # Pri 1
        - USER: cash is fine.
            ('cash',) is not cash
            Waiter: So, do you want to pay with cash or card?
            - Issue 1: (fixed) bad error message
            - Issue 2: now it says cash is not fine
                Waiter: What can I get you?
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
        - my son is vegan
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

    # Pri 2
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

# Code Cleanup
    - Refactor the code based on what we've learned:
        - Need an MRS pipeline up front that does several things
            - Transforms the tree using user defined tree transforms
            - potentially generates multiple MRS from a single MRS for cases where there are conjuncts or multiple syntactic heads (like "Hi, I'd love to have a table for 2, please")
                - properly puts "SyntacticHeads" in the MRS (and not the tree) since it is MRS (not tree) dependent

        - solution groups
            - The code has become very hard to follow due to interpretations, and the sheer number of generators upon generators that get used
            - Figure out how to properly maintain constraints in the face of "and" like "I want 2 steaks and 2 soups"

        - user_interface
            - Code is very convoluted at this point, clean it up and make it maintainable
            - Do a more principled job of what interaction records are, especially in the face of a single phrase generating multiple interactions
            - Do a cleaner job of what output happens, and where.

    - Switch the code to use the term "scope-resolved MRS" instead of "well-formed tree" or "scope-resolved tree"
    - Get rid of all "NextConjunct" code?
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
        - change all the could/can transforms to use OR so there are less
        - Need to check if we are dealing properly with "I want 2 steaks and 2 salads".  [2 steaks and 2 salads] comes in as a single variable, with no constraints (it is a conjunction), right? Have we lost the constraints for the conjunct variables?
            - It does have the requirement that it contains an element of each, but pretty sure we've lost the original constraints
        - Need to think this through: Disabling RSTR/BODY reversal means that "what can I order?" will always be bound.  I.e. using the unbound method as a proxy for "asking a question" is wrong.
        - allow solution handlers to say "I'm it!" just like groups so the other handlers don't have to run
        - Have a method to call to say "continue" in a solution group handler instead of calling report_error("formNotUnderstood")

# Performance Problems
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
          
      - could I get a soup? is very slow when you don't know the cost
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
    - Performance fix: checkin was cca6733
        Before allowing rules to continue running over a transformed tree:
              Elapsed time: 647.23938
        After:
          Elapsed time: 979.71158
