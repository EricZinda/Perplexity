Remaining work to be shown in the tutorial:

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
              - 
  - also copy x in y (the same scenario)

- Support for prepositions
  - show declaring verbs that understand prepositions
- Theory: We don't need to choose different variations of the index of the phrase based on "comm", "ques", etc
  - Except: if we want to use abductive logic to make "The door is open" not evaluated as a question, but as a desire to make that true and then make it true in the system

