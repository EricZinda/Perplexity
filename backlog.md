Remaining work to be shown in the tutorial:

Respecting Plurals
Answers need to be marked so the sets can be returned
The ultimate result should be variables with sets in them. 
- 5 children eating the same 5 pizzas: x5=[child1, ...], x6=[pizza1, ...]
- each child eating a different 5: x5=[child1], x6=[pizza1, ....]
- Could be as simple as marking each solution with the set ID it is a part of
  - Then, whatever reports out the answers has to look and see which variables are a set
    - Each group has an ID that is ParentID+ChildID
    - Each binding has a place to store the ID
    - When reporting out the answer to a variable that is plural, group the parent+child ids