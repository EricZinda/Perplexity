- does card() really need the body? or can it just appear in the rstr?
  - We'd need a different way to manage the variable_set_cache
    - The engine could automatically do it
    - hasChildrenCardinals is easy to detect up front
    - Parent VariableSetID could be determined by knowing what the parent variable is and checking variable metadata
    - Need to properly handle VariableSetRestart in the quantifier


### Design
Rewrite: quantifier1_q(x, [cardinal1(x, ...), cardinal_modifier()], body)
To the form: quantifier1_q(x, [cardinal_modifier(), cardinal1_with_scope(x, cardinal_rstr)], body, 

The job of `card_with_scope()` is to create cardinal groups and variable sets and set the variable properties appropriately
- Same logic as before:
  - If you call with new parent, it picks a new group
  - If you call with "NextGroup", it picks a new group
  - If you call with "NextGroup", it picks a new set in the group
  - If you call with "retryset", it restarts the current set
  - If you call with same parent, it iterates through existing group till it fails
  
Quantifiers just have to pay attention to if their arguments are collective or not, just like other verbs
- it is the job of the quantifier to raise and handle VariableSetRestart
- If they get a VariableSetRestart they need to try the same variableset again, which is easy since they have it available, no coordination with the card_with_scope needed
- If a set fails, and there are children cardinals, they need to send a CardinalRetry signal downstream

where does the variable_set_cache come from?
they are associated with each variable and can be looked up by variable
- you can look it up by asking who your parent cardinal is
- they have to be independent of variable metadata

We build a structure up front that allows a predicate to ask for its cache, and can tell if you have children

Step 1: Build the variable_set_cache infrastructure
  - (done) Build a cardinal tree up front with a place to hang stuff
  - (done) get rid of context and call_with_group
    - rewrite group_context() to return the right node and not use context
    - call it parent_variable_set_cache()
    - get rid of call_with_group()
      - Instead, do a try/except and somehow set the global tree node to be the right variable cache
        - context.set_variable_cache
        - context.clear_variable_cache
      - root_cardinal_node should be accessible from execution context