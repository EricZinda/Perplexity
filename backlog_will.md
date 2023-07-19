- ESL Architecture
  - handle_world_event() is the one place where all interpretations go
  - Most states of the world like "see" and "have" are modelled using those words as relations
  - RequestVerbTransitive/Intransitive convert various request verb forms into requests
  - Command/Response
    - Scenario: I'd like 2 steaks (at the front door) -> works and it shouldn't
      - Individual solutions succeed with RespondOperations instead of failures
      - Final response is handled by the group predications
        - If it is a single thing, its operation is responded
        - If it is multiple, its operation is overriden by whatever user_wants_multiple returns
    - Seems like a better architecture would be:
      - Let regular predications do basic error checking and logic checking for building up to the verb
        - things like "on" for "on the menu" or "table near the window"
      - The verb itself doesn't do anything except for breaking apart combinatorials and basic validation
      - Let the verb *group* do the heavy lifting
- Principles
  - Make everything as general as possible:
    - Interpret anything like "what do have [on the menu]" as meaning "show me the menu" if we are about to return everything on the menu/on the specials list
- Change phrases like "I would like" to "I want" using Transforms

- Overall observations:
  - A ton of these are just pattern matching future, present, specific objects, specific items
  - And either failing or transforming into a plan
  - They are easy to write with examples
  
- "can have" construct:
  - Scenarios:
    - The pizza can have meat?
    - "Can/could I have x?", "I can/could have x?", "Can I have a steak and a salad?", "Can we have a table/steak together?" --> request for something
    - (done) "I can/could have x." -> seems questionable but OK as a request for something
    - 
    - "Can I have hives?"
    - wh-questions
      - Which pizza can have meat?
      - (done) "What can I have?" "What do you have?"--> 
        - Conceptually, there are a lot of things the user is able to have: a table, a bill, a menu, a steak, etc.
          - But: this isn't really what they are asking. This is something that is a special phrase in the "restaurant frame" which means: "what is on the menu"
          - So it is a special case that we interpret as a request for a menu
      - (done) "Who can have a table/steak/etc?" -->
  - Analysis:
    - "can have" means "able_to_have"
    - It also has an implied push to ask for it
    - If wh-questions are involved it asks which x is able to have y
  - Implementation
    - Level 1: see if x is able to have y
    - Level 2: actually request it if the actor is one or the other player
    - 
- abstract-types
  - Dealing with multiple people in verbs
    - We don't want to say the same thing twice if it is the same
    - Really, we should put two messages in there and then merge them at the end if they are the same
  - Planning
    - Always returns a single state in the state group
      - Pass the first state in the group and list arguments for the different states
    - Sometimes it is necessary to examine the whole solution group to decide what to do
      - The planner should always get passed a StateGroup
  - Statements about canonical things
    - Problems
      - By the time the verb is executed: How to tell the difference between "any menu" and "the specific menu that is in the variable"
        - Between: "I want the menu", "I want a menu" and "I want the menu my son has"?
        - Both have a specific menu in the variable
    - Scenarios
      - "I want a taxi", can't say "I want *the* taxi"
      - "I want the menu I have heard so much about"
      - "I want two menus/two steaks"
      - "Do you have 2 menus?"
      - "menus from the kitchen are always dirty"
      - "Do you have the blue menu": could be a class of menu or one that just has unusual blue ink on it
      - "I have heard about your menu"
      - "Can I get one of your steaks?"
      - "Can I have the steak?" but not "Can I have the table?"
      - "What is the menu?" but not "what is the table"
      - "What is a menu?" "What is a table?"
      - "Give me a job"
      - "Give me the job"
      - "I'd like a table by the window"
      - "Are there 2 menus here?"
      - "Are 2 children singing 2 songs?"
      - "what is on the menu?"
      - "what is on a menu?"
      - "what is on today's menu?"
      - "How hard is the job?"
      - "we want menus"
      - "what are the specials?"
        - in be_v_id, how to tell the difference between that and "which food on this table is a special?", which requires instances
    - Analysis
      - There needs to be a way to tell the a difference between the canonical instance of menu for this restaurant "What is on the menu?"
        and one that is generic "what is on a menu?"
        - This is done by putting concepts "in scope".  An in scope menu concept should support "the menu"
      - There needs to be a way to tell the difference between the user indicating a specific instance "Give me the menu my son is holding" and
        a generic instance "give me a menu"
      - For generic instances there might be a lot of extra data with them: 
        "I want the menu I have heard so much about"
        "I want 2 menus"
      - Sometimes extra data can be used to select a type: 
        - "tell me about today's menu" should select the type that is for "today"
        - "what is on your prix fixe menu?"
      - Sometimes the extra data needs to be carried along:
        - "give me 2 menus, please!"
          - 2 should not filter the menus but should be part of the data
      - Quantifiers shouldn't filter out abstract items. Even though "I want the taxi" seems like it could only be an instance
        in a restaurant where "the taxi" is a burger choice it could be abstract
    - Design
      - The developer is going to get all the variations of solutions, they need to decide which is right
      - nouns should always return types and instances
      - just like instances, types can be:
        - in or out of scope
        - Filtered by other words in the phrase
      - types can collect data as they are modified as in "give me today's menu"
        - If that solution is used by the filtered data isn't, it should fail? Like if a word isn't understood?
      - How does a predication like today() decide whether to add data or filter
        - Probably this should be two solutions?
        - And downstream predicates decide how to deal with it?
      - Phase 2 will deliver solutions where there is only the abstract instance in a variable and pass along the criteria
        The developer needs to build up the right solution group by checking the context of the phrase and deciding whether to use the abstract version
        or fail the group with the abstract version and wait for the instances solution group
        - If they decide to use the abstract version, they need to be careful to properly check criteria so that
    - Questions
      - Are canonical instances and types different?
        - Let's say no, since there doesn't seem to be anything to distinguish them
      - Is scoping built into the system or on top?
     - Implementation
        - (done) Implement a generic way to see if something is an abstract type
          - hasattr("is_abstract")
        - (done) Abstract types should not get mixed in with other types *in the same variable*
          - This should fail in add_solution()
        - (done) meets_criteria() should just return "true" if the variable is an abstract type
        - (done) add_solution() currently checks *either* collective *or* cuml/dist
          - It should have a different set of checks if the previous variable is abstract:
            - This variables values meets the criteria, it is collective or cuml
            - This variables values could be divided such that it meets the criteria, evenly with no remainder, it is dist
            - Also: if *this* variable is conceptual, it is going to match *all three* potential plural types
        - (done) Update abstract variables to use new Concept() object
        - (done) Have a way for predications like "for" to add information to Concept variables
        - Need a way to get the constraints for a variable in the group hanlder.  Options:
          - Force the developer to ask
          - Pass as an argument
        - The developer will have to ensure that abstract variables meet global constraints
        - The developer will have to see which kind of solution group this is: a cuml/coll group or a dist group
        - The developer will have divide up the group however makes sense
        - It *might* be helpful to have the system indicate which type of group a variable is
        - Implement table fully
          - How to deal with 2 tables vs "the table" vs 3 tables?
          - Seems like there should be a way to say "This is what we have, this is what was required"
            what is the answer, if any?
        - Implement menu fully
        - Make pronouns implement abstract types?
        - Issues:
          - combinatoric logic also needs to not mix conceptual and instances
            - TODO: Might be easier to just prevent conceptual in combinatoric
          - Conceptual instances can come through in any order, if you want conceptual you 
            might need to wait for it
          - Need a way to return errors from the plan that get shown to the user
            for scenarios like "we don't allow specific tables"
          - Something that processes a concept needs to understand all of it or fail
            - How to enforce this?
            
- Dealing with all the different phrasings of "What are the specials?"
  - Scenarios:
    - "Are there any specials?"
    - "Could you describe the specials?"
    - "Do you have specials?"
    - "Could you tell me the specials?"
    - "Are there vegetarian dishes?" (before they have heard about the specials)
  - Issues
    - When asking for a description, the asker wants the long winded version
    - When asking "What did I order?" the user just wants the world "the soup special"
    - Even when ordering, the user could say "is anything vegetarian?" and the answer should probably be "the soup special" but a flowery description is ok
  - Design
    - If the answer to anything is one of the specials concepts, and we haven't described them, we should first list the short them, then
      describe them all (or ask if we want to hear)
    - Really this should be true of the menu as well

- Using Frames determine whether have we respond with instances or concepts
  - Scenarios:
    - "what are the menus?"
    - "what are the steaks?"
  - Could mean the concept of steak or the instances of steaks on the table
    - Predications should decide which we are talking about based on context
      - If there are steaks on the table it could mean either
      - If no steaks on the table but at the table probably means concepts
      - The state that is available is different depending on (something) which happens to be location here
      - This is different than scope, because various concepts and objects might be out of scope here too
      - Seems like the world state should be one thing, and a "frame" is created from the world state
    - The base theory is to answer with the most relevant answer
      - Even if there aren't steaks on the table, the user could ask: 
        "Are there steaks in the kitchen?" or "Are there steaks left?" which should get "yes"
      - Is this really just a question of scope?
        - No, it is different: it prioritizes what we're talking about. First try this, if it works, done. otherwise try this.
        - Scope says "if the user says 'this' and nothing is in scope, fail"
    - So, if the user is at the table, the conceptual answers are returned but the others are still available
      - Try to get an answer in the current frame, but if it doesn't work, use the global frame
      - Means running the solver over several state alternatives
      - Which state alternatives to try first also depends on the state of the world
        - Once there is food on the table, they are more likely to be talking about food instances "the steak is cold"
        - Approach: Create a list of frames, from most specific to least
          - Run the query against each
          - The world state has a method to iterate through frames
            - It runs custom code for the scenario
            - In the restaurant it first returns state filtered for the specific place the user is
              - Then it returns the global state
          - Design
            - Everything "in scope" is always in the frame
            - All abstract concepts are always in the frame
            - Really we are just trying to get things that are "in scope" to be the first answer
            - Problem: We want to run the query against the frame, but allow the engine to manipulate the world state
              - Need to include a way to get at the whole state
              - Add a method that allows access to the whole state

- Make "how much is the soup" work
  - the wh-variable is abstract_degree and thus isn't listed
                                                                      ┌──── measure(e14,e15,x10)
                                                                      │ ┌── generic_entity(x5)
                  ┌────── abstr_deg(x10)                              │ │
                  │                                       ┌────── and(0,1,2)
    which_q(x10,RSTR,BODY)            ┌────── _soup_n_1(x3│               │
                       │              │                   │               └ much-many_a(e15,x5)
                       └─ _the_q(x3,RSTR,BODY)            │
                                           └─ udef_q(x5,RSTR,BODY)
                                                               └─ _be_v_id(e2,x3,x5)
  - generic_entity(x5) is telling what measurement to use
    - it is replaced by _dollar_n_1(x5,u16) if the question is "how many dollars is the soup?"
  - measure(e14,e15,x10), much-many_a(e15,x5)
    - measure tells much-many_a it is measuring something and putting its measure in x10
  - much-many_a(e15,x5) is told to measure x5's "how muchness" and and put into x10
  - be_v_id(x3=soup, x5=something you can measure)
  - So 
    - measure(e14,e15,x10), generic_entity(x5), much-many_a(e15,x5), _be_v_id(e2,x3,x5) means: measure in generic units and put into x10
      - measure() puts event information in much-many_a(e15, ...) saying what to measure *into*
      - generic_entity(x5) puts the Concept("generic_entity") in x5
      - much-many_a(e15,x5) replaces x5 with measurement with an unbound value
      - be_v_id fills in the me
    - measure(e14,e15,x10), _dollar_n_1(x5,u16), much-many_a(e15,x5), _be_v_id(e2,x3,x5) means: measure in dollars and put into x10
      - dollar_n_1() puts the concept(dollar) in x5
  - The problem is that x5 will already be filled by the time it gets to be_v_id
      - In principle generic_entity is every possible measurement
      - be_v_id
  - Note that "the soup is 2" requires be_v_id to compare to a generic_entity
    - Option 1:
      - be_v_id needs to set x10 to a value based on what x5 is
    - Option 2:
      - treat x5 as a scopal arg? where e2 is modified by much-many_a
    - Option 3:
      - Treat x5 as holding a predication (much-many_a) that must be evaluated when seen
    - Option 4:
      - St x5 to be a measurement() object that has a type but not a value yet
  - how big is the soup?
                   ┌────── abstr_deg(x5)
    which_q(x5,RSTR,BODY)            ┌────── _soup_n_1(x3)
                        └─ _the_q(x3,RSTR,BODY)    ┌── measure(e9,e2,x5)
                                            └─ and(0,1)
                                                     └ _big_a_1(e2,x3)    
    - big_a_1 is told to measure x3s "bigness" and put in x5
    - 
- Redo existing code using Perplexity ontology
- Implement all nouns in terms of base engine using noun_n()
- Implement "I want ham"
- Dealing with all the duplication of items and combinatorics seems like a waste. Seems like there must be a better way that involves symbolics. For example
  - We want a steak
  - If there are 10 steaks, then want_v_1 will get called 20 times (10 for each person). Whereas if "steak" was symbolic it would only get called twice