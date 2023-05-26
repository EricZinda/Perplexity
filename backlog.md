Remaining work to be shown in the tutorial:
- (fixed) "which files" generates to "which files" which is wrong
- (fixed) "what is "foo" in?" generates "'foo' is not in what"
- "59.txt" is in this folder
- 
- Generation issues:
  people_n with NUM=sg doesn't generate person. But dice does

- Bug: Test: the 2 files in a folder are 20 mb
             There is more than 2 2 files in folders

        Expected: There are more than the 2 file in a folder
  the real error is "there are more than two files in a folder"
  - We need a way to pluralize the noun phrase "files in a folder" properly
    We can do it with MRS Generation if we can get the MRS for it
    - Generate the MRS that round trips
    - Replace the BODY with unknown(x)
- CARG arguments for things like "polite": "please, could I have a table" in the MRS the argument is first, but in the tree it is last

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
    
- Need a classic "push a context on the stack" for questions like "Do you want takeout?" know how to deal with responses like:
  - "I want to sit down"
  - "yes, I'd like a hamburger please"
  - Need a conversation model? Discourse analysis?

- what about "I want two hamburgers"?
  - If hamburgers don't exist it will fail on hamburger_n() with "I don't know the word"
    - We kind of want "want" to get called with the text of what the user wants and fail in "want/give", right?
    - with a message like "We don't have those here"
    - Implies there is a generic noun_n() that gets called

- ESL Features TODO
  - Don't respond with items if the user added a response with RespondCommand
  - Need a NLG realizer for strings
    - https://delphinqa.ling.washington.edu/t/using-ace-via-pydelphin-to-generate-fragments/779/5
    - https://delphinqa.ling.washington.edu/t/how-to-generate-english-sentence-from-a-parse-having-nn-u-unknown-jj-u-unknown/851
    - Approach 1: 
      - Focus on noun phrases only
        - pick the parse that generates the original string when round tripped
      - Create a template and fill with a phrase later.  Replace the quantifier, clean up MRS
      - Compare output of ACE with the entire original string and only accept the one that has the same front and back
      - How to generate the fragment:
        - If given a word: [a, sayName(_1ObjectID)], [The, sayName(idDeer1, default, singular)]
          - sayText("I don't know about [a door: object]", object=myObject), sayText("[The deer] quietly walks away", object)
          - decide what kind of determiner (somehow)
          - generate the mrs for the fragment
          - plug it into the original
        - If given a list: [is, sayListNames(an, _1Items, default)]
          - fake it out by generating the phrase with plural or singular *words* and then replace with the whole string of comma delimited stuff
        - If given a verb: [is, sayListNames(an, _1Items, default)]
        - Cache everything but the runtime generation since it is expensive. Don't evaluate it until we actually show the user
      - TODO: Handle words the engine doesn't know with the same POS and replace? But then you need to pluralize
    - Approach 2:
      - Focus on noun phrases only
        - If given a word or phrase: [a, sayName(_1ObjectID)], [The, sayName(idDeer1, default, singular)]
          - decide if it is uncountable or not  (somehow) 
          - decide which indefinite article (somehow)
            - https://stackoverflow.com/questions/20336524/verify-correct-use-of-a-and-an-in-english-texts-python
            - 
          - plug it into the original
        - If given a verb: [is, sayListNames(an, _1Items, default)]
          - Use something to generate the right form of verb
          - 
        - Give a way to replace a list with your own (like a global event for solution groups)
        - Scenarios:
          - "There is more than x y"
            - Need to make y have no determiner and be singular
        - Design:
          - Have an object that can handle a single word: Determiner, Plural in any combination
          - TODO: Get rid of determiners like "2"
            - Probably have to have these in metadata so that we can properly report errors where there is no state to see if they added criteria
    - The old prototype would gather up all responses in one answer and return it
  - "What else is on the menu?" -> need to see if "else" is on "which"
    - Not included in any predication
  - Way to push a conversation so the system can ask "Do you want this?" and properly deal with responses
  - Add chat_gpt code so we can play with using it for nouns
  - NEED TO UPDATE DOCS FOR VERBS TO MAKE ALL THIS CLEAR:
    - "I want ham" is a proposition that we want to interpret as a command
    - For a verb: Succeeding means it "worked" and should add an operation to change the state
      - it is not modelled as world state as in "I want a burger = True"
      - Really think about a phrase as setting up all the various variables so that the verb can be called
        - Really it just means: this is the proper interpretation, but it might be an error, in which case it can do a RespondOperation
      - delegate to "give me" *as one alternative* if it works, great!
        - If: it is a proposition and IF pron(I) and IF arguments are bound: There is something concrete they want, next determine how to deal with it
            - in the doorway: "I want a table" -> give me a table, "I want a place to sit", "I want to eat " (different want_v), I want a burger" -> "Do you want take-out?"
          
- Put thing() in the system space.  Others?  "a few"?
- Docs update:
  - Figure out how to do examples in the internals section.  Just replicate the how-to?
- Make old tests work
- Bug: What is large? Will only return one item because it is singular


- Rebuild the scenarios to get the tests to pass again
- Build a backend to use for ESL Scenarios

- Need to write a section on predication design
  - Objects should be implemented purely and independently so that the magic of language and logic "just work"
  
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

