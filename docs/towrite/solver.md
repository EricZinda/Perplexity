- "Which two dishes are specials?" -> how to show "there are more"?
  - allow Response() operations to have an argument "more" that only gets printed if it matches whether there is or isn't more
  - If the user didn't customize the message, show "there are more" by default

Global criteria count the number of "these" things per the number of the previous things.
  - whether values or individuals are counted depends on the kind of grouping (coll, dist, cuml)
  - For the first one there is not a "previous"
Basically: we need an algorithm that will generate sets of all kinds if allowed to generate all possible sets
  - merging only makes sense when only only one set could be used is 

Scenarios:
  - 2 students learned a song
    - Clearly counting individuals
    - But if (a), (a, b), and (b) all learned one single song that is OK
  - We want a menu
    - all of us [(a), (a, b), and (b)] getting the same menu is ok 
        - This seems wrong: Is it really even possible for us each to have an item alone and "together"? 
    - all of us [(a), (a, b), and (b)] getting a *different* menu is OK 
    - The logic for giving a menu is:
      - give a one,
      - give b one,
      - then give (a, b) one which ?is wrong?or not?
      - Theory:
        - It *could* be technically correct in the general case, but we know it isn't correct for this case because it isn't something the user would want to do
        - Also: it seems uncommon or confusing to allow (a), (b), (a, b) as set of solutions to the first quantifier
        - Current approach: force to be either individuals (i.e. sets of 1) or a collective (sets > 1) group but not a mix of both in a particular solution group variable
    - Theory for generation: if it switches the type (i.e. coll to dist) it should be a new group?