have_v and order_v are both just about verifying facts in the world, so they should be implemented the same. Many predications will be like these.

Approach:
    - Start with "you" meaning restaurant
    - Start with only bound variables and make that work
    - Start by not worrying about what errors are returned
    - Key: For "you", it can mean either "the restaurant" or "the waiter"
        - We need to model these separately

How does a human process this?
    - Decide the alternatives for what the referring expression could be (there might be multiple options)
        - These will be the solution groups
    - rule out any that don't exist
        - This should happen in the solution predicate?
    - pick the best answer
        - Just assume the first that works?
    - Decide if it is an implied request or a factual question
        - Can be determined by context

Interpretation 1: non-conceptual query
"Did I order an (instance of) a steak?"
"What dishes do I have?"
    - "dishes" refers to instances
"Do you have a steak?" --> implied request if something is on the menu
"Do you have steaks?" --> implied request if something is on the menu

Interpretation 2: in-scope concepts query
Analysis:
    Could be an inscope concept OR an instance, seems like we should always try for the instance first

"Do you have a (concept of) a steak?"
"Do you have the steak?" -> refers to having an inscope concept of "the steak"
"Do you have the table?" -> There is no in-scope concept of a table

Interpretation 3: implied requests
Analysis:
    Any "computer have x?" pattern is really an implied request for that thing or sometimes a request for a description of that thing 
    In all of these, "you" means the restaurant, and they are all implied requests of some kind
    By the time we get to "have_v" we need to know if the user actually asked for a specific table or "a table" which can't be determined by just looking at the atom
        Is this really true?
        I think really we just need to know if there is an inscope concept that is being referred to or not

Design:
    If this is a "computer have x?" pattern:
    Start by just treating them all as a request if the restaurant has such a thing
    Then, for specific cases like tables, menus, bills, also transition to taking an action

Scenarios:
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
    
