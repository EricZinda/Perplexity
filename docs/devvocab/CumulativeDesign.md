Cumulative readings have the following two properties:
1 Each boy must participate in the carrying, and each piano must be
carried.
2 There is no number dependency between the two arguments. (No type 3 distributivity)

As long as each parent quantifier rstr is true for at least one body and each child quantifier rstr is true for at least one parent, it is true
- The parent could be a collective subset, the child could be a collective subset

Start with udef_q:
    "boys carried pianos"
    As long as the original set of rstrs are involved in any of the coll or dist readings, it is true
    Unique answers are all unique combinations of all answers that exactly equal the set?
    "which boys carried pianos?" ideally would return all the non-overlapping combinations that worked. 
    The trick is when there are cardinals involved
    Across both collective and distributive for the whole quantifier, 
    The case that won't work now, but should in the new world is: 2 files are in 2 folders where there is just 1 file in 1 folder and another file in another folder
        This is a case where the second cardinal needs to remember what it has seen and make sure it adds to 2
To get all the readings we need to generate all combinations.

Brute force:
    If you get all uncardinalized answers for coll and dist
    Then run the cardinals against this and return all combinations of solutions where the set of x is unique and the cardinals are true
        You have to walk the cardinals and pick those solutions for which one is true, and then pass that filtered set to the next one
    The bindings in the solutions contain the cardinals that should be used for them

    Optimizations:
        Starting with the cardinal that generated the smallest set is probably best
        You can rule out everything if there aren't even card(rstr(x)) available at all for the first one (but maybe not for child cards because the rstr could depend on the first?)


Could we use this approach for dist and coll too?
    It might be better in that 
    coll for a variable is a single set that matches the cardinal. We'd need to group all the solutions that have the same values that 
    dist for a variable is a group of N sets of 1 that matches the cardinal
    coll is just cuml where you require the set to be in a single answer? Doesn't that just fall out naturally? 
        No, Cuml would not allow "2 children ate two pizzas" to have 2 children that ate two different pizzas each
                
    dist is just cuml where you require the set to be in all different answers? Doesn't that just fall out naturally?

1. Run quantifiers uncardinalized
2. Cardinalize them
3. Quantify them

Is there an iterative approach?
    Cuml is an operation over the solutions that groups them
- Find every combination of rstr that matches the cardinal
    