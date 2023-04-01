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
    If you get all unquantified answers for coll and dist you get all the possible values that could be true
        "2 files in 2 folders" just becomes "files in folders"
    Then run the quantifiers cardinals against this and return all combinations of solutions where the set of x is unique and the cardinals are true
        You have to walk the cardinals and pick those solutions for which one is true, and then pass that filtered set to the next one
        The bindings in the solutions contain the cardinals that should be used for them
        Need to return groups of solutions that are "1 solution group" as the actual answer
    Issue: When the "2 file" cardinal filters the solutions to 2 individual files it passes along all the folders that those two files are in
        It seems like each cardinal needs to be passing along all combinations of solutions that have 2 files? Not the entire group?
        This means subsequent ones need to use all the solutions in their solutions
        But what about the first one?
            The first one just selects solutions that match and has to be combinatorial since nothing has been restricted yet
        Now dist, dist doesn't work because it requires file() to send along 4 answers

    Optimizations:
        Starting with the cardinal that generated the smallest set is probably best
        You can rule out everything if there aren't even card(rstr(x)) available at all for the first one (but maybe not for child cards because the rstr could depend on the first?)

    Questions:
        How does this really work:
            Unquantified and Uncardinalized gives you all potential answers 
            If you then filter the answers to the groups that are true for each quantifier in question, and only pass those that are true to the next one
            The cardinals and quantifiers are always operating on some relationship between the original RSTR solutions and those that are true in the body
                All you need to know is what is original rstr(x) and what is postbodyrstr(x)
                AFew(x) 
            Do we really need all combinations of answers returned?
                The fact that there may be many solutions involving a particular value of x doesn't matter for the count. So we should always make it a unique count.
                BUT: if we allow downstream predicates to filter out solutions, they may remove one that made an upstream predicate true which breaks the logic. 
                    so: the only way to have downstream predicates able to operate in isolation is to say they must not remove any solutions, which means all possible combinations need to run
                        OR: Optimization: maybe predicates can pass combinatoric options down?
                In other words: we need all combinations to be sent so that downstream predications can just see if the whole set is true, because there isn't a way to easily remove a solution at that point
                    and be sure you didn't break the upstream truth
                And: it isn't enough just to send one set of truth values, because downstream predications may need a different one that is also true
                Example: which files are large? returns all the alternatives many times
                    Because it gets 3 set answers 
                    The first quantifier is sent them as solution_combinatorial
                    And it sends all the combinations
                    Because it *might* have been: which large files are in this folder, in which case if it *didn't* send all the alternatives, it might have missed the solution        

            A cardinal for 2 is really just saying "two unique things are involved, somehow", it should allow downstream predicates to try all the alternatives
            How do you get rid of duplicates? Maybe duplicates don't really matter, they just get filtered at the bitter end by only reporting unique values.
            If you don't, then something like 
            It seems like we just need to be able to explore all the solutions until one is found and then return that
        Can we really run quantifiers after the fact?
            As long as we have the original rstr there, maybe?
            But: we won't have a record if it fails for it to return a good error. Should be some kind of workaround for this
            every(x, rstr, body)

Could we use this approach for dist and coll too?
    It might be better in that 
    coll for a variable is a single set that matches the cardinal. We'd need to group all the solutions that have the same values that 
    dist for a variable is a group of N sets of 1 that matches the cardinal
    coll is just cuml where you require the set to be in a single answer? Doesn't that just fall out naturally? 
        dist is just cuml where you require the set to be in all different answers? Doesn't that just fall out naturally?
            No, Cuml would not allow "2 children ate two pizzas" to have 2 children that ate two different pizzas each
    Real algorithm is:  
        collective: value of one variable meets the cardinal
        distributive: value of one variable meets the cardinal
1. Run query without quantifiers or cardinals
2. Cardinalize them
3. Quantify them

Is there an iterative approach?
    Cuml is an operation over the solutions that groups them
- Find every combination of rstr that matches the cardinal
    
What are the proper answers when 2 files are linked in two folders
which 2 files are in two folders?
coll, coll
dist, coll
coll, dist
dist, dist
cuml:
    file1 in folder1, file2 in folder2
    