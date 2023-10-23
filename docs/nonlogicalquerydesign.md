have_v and order_v are both just about verifying facts in the world, so they should be implemented the same. Many predications will be like these.

## How "I have the soup" works
Option 1: First match_all_n() returns all concepts and then all instances.  For concepts, no global constraints are checked, so the concept just gets through to the group_handler.  You can do the work to check if something is an "in scope concept" here if you want.

Option 2: Alternatively, match_all_the_concept_n() is a different interpretation that will return all instances of the "in scope concept" of "soup" if there is one. It removes any "the-type" constraints.  This allows simple fact checking things like "Do I have the soup?" to just work without messing around with concepts.  However, it means you can't know, by the time you get to have_v() whether they are talking about the concept or an instance.

But if the user asks "Do you have a table?", have_v() 

Background:
- Referring Expressions The Nature of Referring and ... https://assets.cambridge.org/97811071/43470/excerpt/9781107143470_excerpt.pdf
- Best:
  - https://cs.uwaterloo.ca/~david/ijcai19/
  - https://cs.uwaterloo.ca/~david/ijcai19/refexp-tutorial.pdf
  
Key insights:
    "you" can mean restaurant or waiter
    If "you" is "restaurant" we are always talking about concepts
    referring expressions are different than types. A referring expression can generate types
        (done) Need to rename these to "referring expressions"
(done) Types and instances should not be mixed, just like referring expressions and instances
    Types can be selected, just like instances.  
        "A blue bike" would return the type of a blue bike, if it exists in the system
        It would also return a referring expression for such a thing
        Issues:
            Do you have to create a "type" that represents:
                Examples:
                    "2 boys" for "2 boys are in a kitchen"?
                    "table for 2" for "I'd like a table for 2?"
                Answer: Yes
                    And concepts should only be built of the specific things said by the user?
                    
            What is the difference between a referring expression and a type? Can a type be represented as a referring expression?
                Seems like they should be different. The type is the result of evaluating a referring expression.
            If you say "do you have 2 steaks" it might mean "two concepts of steak" or "two instances of steaks"
    There are only two reasons you actually need to inspect the referring expression is if interpretation of the phrase requires it
        1. If the code wants to require that the the user asked for a table "for 2", there is no way to know that after the fact
        They could have asked for "a table", and it just so happens that all are for 2, so you won't know how specific they were.
        2. When you want to defer listing the potential outcomes of the referring expression. For example, when processing the phrase
        "Do you have (a menu)" we want to check to see if we are talking about "menus" and, if so, treat this as an implied request, 
        and find one (using the referring expression) that is not in use.

Interpretation 1: instance query
"Do I have a son?"
"Did I order (an instance of) a steak?"
"What dishes do I have?"
    - "dishes" refers to instances

Interpretation 2: in-scope concepts query
Analysis:
    Could be an inscope concept OR an instance, seems like we should always try for the instance first

"Do you have a (concept of) a steak?" --> does the restaurant have the concept of a steak
"Do you have the steak?" -> refers to having an inscope concept of "the steak"
"Do you have the table?" -> There is no in-scope concept of a table
"which steaks do you (restaurant) have?" -> which inscope concepts of steaks are there?

Interpretation 3: implied requests
Analysis:
    Any "computer have x?" pattern is really an implied request for that thing or sometimes a request for a description of that thing 
    In all of these, "you" means the restaurant, and they are all implied requests of some kind
    By the time we get to "have_v" we need to know if the user actually asked for a specific table or "a table" which can't be determined by just looking at the atom
        Is this really true?
        I think really we just need to know if there is an inscope concept that is being referred to or not

"Do you have steaks?" --> implied request if something is on the menu

Design:
    If this is a "computer have x?" pattern:
    Start by just treating them all as a request if the restaurant has such a thing
    Then, for specific cases like tables, menus, bills, also transition to taking an action

Scenarios:
    "I want a table for 2"
        - Need to process the *concept* because we need to interrogate it to see if the concept includes the number of people somehow
            - Otherwise, if we just process instances, we may *happen* to get an instance for 2 that works.  But we really want to know what they wanted.
        - Then we need to see if there are instances of it available by evaluating the concept
    "Do you have a table?" --> implied table request
        "Do you have a place we could sit?"
        Design: Any referring expression that resolves to "a table" should mean "get me a table"
    
    "what do you have?" --> implied menu request
    
    "Do you have a/the menu?" --> implied menu request
        "Do you have menus?"
        "What dishes do you have?"
            - "you" is interpreted as the restaurant
            - "dishes" refers to conceptual dishes
        Design: Any referring expression that resolves to "all food" should mean "get me a menu"
        
    "Do you have a/the bill?" --> implied bill request
        "Do you have the cost of what I ate?"
        Design: Any referring expression that resolves to "the cost of food" should mean "get me the bill"
    
    "what specials do you have?" --> implied request for description of specials
    
Design alternatives:
- Option 1: You *only* get a referring expression, and have to evaluate it if you want types and instances
  - If you evaluate it, you can get back types and instances
- Option 2: Variables can contain types, instances or referring expressions. You have to handle all of them and check for them
- Option 3: Referring expressions are handled specially and generated by the system.  You have to ask for them to get one
- Option 4: You can always ask for a referring expression for a variable, but you have to ask
- (go this way) Option 5: You rarely, if ever, deal directly with referring expressions. You instead deal with concepts and concepts can be evaluated to retrieve instances that match them.
- Across all alternatives: Phase 2 needs to properly handle types as separate from instances.
  - Between types, instances and referring expressions: they all should be in separate solution groups


Concepts Design:
    - Concepts are closely related to referring expressions in that they both can be evaluated to resolve instances.
        - But a referring expression can also be evaluated to return a concept, which can be further resolved to return instances.
        - The structure of a concept might look a lot like a referring expression, but it is application specific, and "simplified" or "reduced" down from what 
            the referring expression might have said to something "canonical"
    - Representation
        - It is application dependent, the engine shouldn't care.
        - There should be an "get_instances()" method that retrieves instances
            - If I say "I want 2 steaks", what does the concept look like?  When I call "get_instances()" what is returned?
                - The concept only represents a solution answer, not a solution group answer
                - you need to find the global criteria and make sure it matches for a solution group answer
        - There should be a "get_concepts()" method that retrieves concepts that are specializations of that concept
        - The ESL repr should simply be an expression of triples that can be run
            - conjunctions and disjunctions
        - predications add the proper criteria to the expression as they go
    "2 boys had 2 hats"
    - "boy" is a type
    - Treat the criteria "2" as a criteria and allow the group handler to handle
    - All other adjectives just restrict the list of types to those that match the adjectives
    - plurality for types and referring expressions should work the same?  Both should be handled as "opaque thing" that the group handler has to resolve?
