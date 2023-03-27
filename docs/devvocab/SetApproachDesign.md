x-variables can be a set or an individual.
Examples:

    two files are in this folder:
    
                                                      ┌── _file_n_of(x3,i10)
                                          ┌────── and(0,1)
                      ┌────── _folder_n_of│x11,i16)     │
                      │                   │             └ card(2,e9,x3)
    _this_q_dem(x11,RSTR,BODY)            │
                           └─ udef_q(x3,RSTR,BODY)
                                               └─ _in_p_loc(e2,x3,x11)

    only two files are large    
                            ┌──── _file_n_of(x3,i11)
                            │ ┌── _only_x_deg(e5,e6)
                ┌────── and(0,1,2)
                │               └ card(2,e6,x3)
    udef_q(x3,RSTR,BODY)
                     └─ _large_a_1(e2,x3)

    only a few files are large
                            ┌──── _file_n_of(x3,i10)
                            │ ┌── _only_x_deg(e8,e9)
                ┌────── and(0,1,2)
                │               └ _a+few_a_1(e9,x3)
    udef_q(x3,RSTR,BODY)
                     └─ _large_a_1(e2,x3)


    files are in this folder:
                     ┌────── _folder_n_of(x9,i14)
    _this_q_dem(x9,RSTR,BODY)            ┌────── _file_n_of(x3,i8)
                          └─ udef_q(x3,RSTR,BODY)
                                              └─ _in_p_loc(e2,x3,x9)

    rocks are in folders:
                ┌────── _rock_n_1(x3)
    udef_q(x3,RSTR,BODY)            ┌────── _folder_n_of(x8,i13)
                     └─ udef_q(x8,RSTR,BODY)
                                         └─ _in_p_loc(e2,x3,x8)

    rocks are together:
                ┌────── _rock_n_1(x3)
    udef_q(x3,RSTR,BODY)
                     └─ _together_p(e2,x3)

    files are together in this folder
                      ┌────── _folder_n_of(x10,i15)
    _this_q_dem(x10,RSTR,BODY)            ┌────── _file_n_of(x3,i8)
                           └─ udef_q(x3,RSTR,BODY)    ┌── _together_p(e9,e2)
                                               └─ and(0,1)
                                                        └ _in_p_loc(e2,x3,x10)


_file_n_of(x3)
- because x3 is plural, file_n_of fills x3 with all files, which can be a generator or any type of iterator
  - Problem is: generators cannot be pickled
- So: need to take the approach where we rewrite the tree or put some kind of _file_n_of() restriction on the variable that can be pickled (which is like rewriting the tree)

card(2,e9,x3)
- returns all combinations of 2 things in x3 


Questions: 
    It seems like there are different rules for:
        things that introduce x variables like rock_n(x): has to create them from scratch (which is why thing(x) exists)
        things that dont: which can assume they are set to something

if large_a(x) is passed x = [1, 2, 3] how do we distinguish "the set of [1, 2, 3] is large vs. "each of the things in the set is large" at the end?

In this new model, options:
    - option 1: every single answer should be an assignment of variables that makes the statement true?
    - option 2: the collection of answers can be reconstructed to that

if "there are large files" runs, and large just leaves x3 as a set

Need another design:
    Variables are always sets, could be a set of 1
    They have metadata, much like events do, that are stored in the variable binding.
        set_type = how the set of values should be interpreted: 
            collective: single collective answer, 
            distributive: single distributive answer, 
            combinatorial: a set that represents "all combinations" of the values in the set
    The basic model is about *restriction of variables*. As variable values go through the system, they get restricted to the maximum set that makes a predicate true
        A predication can only restrict the incoming variables, never grow them. 
        A predication yields a state that has the variables are set such that they have been restricted to be true
        If they are unset it means "anything in the world"
        We have a "combinatorial set" *optimization* that says a variable set can mean "any combination of these will be true for me" 
            so we don't have to push every combination through the system
            It is not necessary to do this, the predication can instead yield each answer, but for cases like "file(x)" or "large(x), yielding every combination is quite large and would be inefficient
            So that downstream predications can always check the largest possible group, the variables always have to be the maximal subset
        By the time we are done at the end, if there are variables that are left combinatorial, it means all combinations will work, 
            we just need to choose how to give these responses to the user
        If a predication *does* have meaningful set behavior, then it has to yield all the sets that work individually (unless they all do)
            And mark the binding as being collective. Same is true for distributive.
    So, for a given predication, it needs to look at the incoming variables and act accordingly
        if a binding is marked as collective, the group needs to be kept as a whole, or fail
        if a binding is marked as interpret_collective, the predication must only generate sets that can be interpret_collective (or is_collective)
        For distributive, it is analagous
    What is the contract? If an comb set comes in, can you yield 3 different comb subsets of it?
        This must be true because this is what "in" does. "a", "b", "c" and "x", "y" come in and "a", b : x and c:y go out
            But would it be OK to return a:x, b:x and c:y?
                I think no because it limits downstream predication's ability to form groups
                It has to be the "maximum subsets"
                And it can't just be "all combinations of the original comb checked for 'in'" because some could generate duplicates
    At the end, the engine can look at the binding.  If it is comb, it can (by convention) be listed as dist
    A given predication should be able to create a "check" routine that just takes two arguments and we do the right thing outside of it

Questions:
    If in(x, y) has x as comb(a, b, c) and they are all "in" (x), it is true that all the combinations are in x, and they do 
        need to be returned if "in" is not the index so that downstream predications can use them, but unless they actually get used, it will be a bunch of duplicates.
        Fact: It has to be the case that yielding all combinations is the same as a combinatorial set since comb() is just an optimization
        thoughts:
            If we had the notion of "used" vs "just true" ...
            If we do "files", it will return both combinatorial_coll and combinatorial_dist
                Let's assume that if, at the end, something returns both combs, we should only list dist (and comb_dist is just every item by itself)
            now "files in folders", both files and folders returns both combs and "in" gets all 4 combinations
            If "in" rejects all but dist, that isn't right because "files together" would create coll and so nothing would work
        design:
            if a predication like "in" or "file" works the same for both coll and dist, that is an implicit "dist_used"?
            dist is the default
                if something doesn't support it, it should fail, but then it *also* must guarantee that it will mark "used coll" for collective
                    Otherwise we won't know to pick collective for that variable
                if something does support it, it just succeeds
            coll gets pushed through the system
                if something doesn't support it, it should fail
                if something does support it, it just succeeds
            Those rules get us all possible coll/dist answers, which means there will be dups if some predications don't care
            We need intermediate nodes to pass through coll/dist answers even if they don't care since predicates after them might
            At the end, how to decide which are duplicate answers?
                Only plural variables generate coll and dist options
                If nobody marked the coll as used, it wasn't, so just use dist version

            At the end, if there are bindings that have don't care set, use only the dist version to get rid of duplicates
            Additionally: if something *pays attention* to coll, it marks the binding
            Why don't we have preds mark "used_dist"?
            At the end, we remove coll answers where coll didn't matter because they must be duplicates
                Why, what licenses this? Because we assume that the rstr returns the same value for 
                    both coll and dist if it generates them both. It might remove one completely, but if it is there, it will be 
                    the same
                But what if dist answers were completely removed, as in "which files together are large?"
                    Together removes the collective sets
                    large doesn't care so allows them
                So the rule should be: If there are both collective and dist answers and nobody cared, remove the coll

            Assume there is a "used collective" that means something acted differently with the collective data
            if something like loc_nonsp_size actually behaves differently with collective data, it should set the binding to collective
            answers with combinatoric_collective at the end mean that
            
    how does together_p(x) work? It says that the comb set needs to be treated as collective (but the comb set is not yet)
    how can in work and still leave things combinatorial?
        # Given a set of actors and a set of locations, assign actors to all their locations
        # This is a bipartite graph. And we need to generate all complete bipartite graphs from it.
        # Complete bipartite graph: complete bipartite graph or biclique is a special kind of bipartite graph where every vertex of the first set is connected to every vertex of the second set
        # https://en.wikipedia.org/wiki/Complete_bipartite_graph
        # https://stackoverflow.com/questions/15699714/find-all-maximal-complete-bipartite-subgraph-from-given-bipartite-graph
        # https://stackoverflow.com/questions/3069365/finding-maximal-bicliques
        # https://reader.elsevier.com/reader/sd/pii/S0166218X04000629?token=A60F49516114E93440CF9D4431A5492B62FFCD7C8E0AA67D9C6B71A9CEE64124799CECF84782677BD7D8039B57033AC3&originRegion=us-east-1&originCreation=20230323202858

    variable bindings are like the "introduced event" of the variable. 
        Quantifiers pay attention to what the rstr predications set this to and change behavior as appropriately
        It is also *way* more efficient for things like "2 files are large"?
            2 files leaves the whole set of files and runs them through the body
            if at the end there are "exactly 2 files" then it succeeded
        2 children ate 2 pizzas 
        This model totally makes sense now...
            It seems like it will make cumulative mode brain dead simple too...?
    card() needs to always restrict to a set of N
    quantifier has to turn them into coll or dist groups. The cardinal is what ensures that the entire collective or dist set works
        contract for the quantifier:
            There are several parts to the quantifier: the quantifier criteria, the cardinal criteria, the rstr and the body
            Logically "the two boys in the store are nice"
                "the" means "the only (rstr)" so, if there is more than one successful rstr (after the cardinal), it should fail, it doesn't care about the body
        Retrieving a RSTR gets the set of uncardinalized values
        The cardinal should really be run over the RSTR values and limit the set *before* running the body
            BUT: is it true that we can run the body and then work out the set?
        the quantifier quantifies *over* the sets managed by the cardinality.  Thus, "only a few x" means "1 set of a few"
        the quantifier x binding gets a mode set to say which mode it is in
        How to handle any coll/dist restrictions (like together, separately):
            together() sets a property on the variable binding to say which mode it has to be in. 
            The quantifier pays attention and does the right thing
        How to handle the cardinality restriction?
            The rstr sets x to a set AND (potentially) adds a criteria to how many elements of x must be true in the solution. 
                The sets returned by the rstr determine the *maximum* sets that the coll/dist groups can be.  
                    However, they can be *smaller*, 
                    and a given starting group might return multiple answers using subsets of the incoming group
                For card(2) it means "exactly 2"
                For at most card(2) it means "<= 2"
                If there is no cardinal in a plural it means "> 1"
    2 children ate 2 pizzas
        run the set of children through as a set
            then see how many of the set remain
        run the set of children through as a set of N
            then see how many of that group remain

Failed design (why?):
    New General Model
        A predication restricts its variables and yields new state with those variables set to the new set for which they are true
            When predications fill a variable (like "file_n(x)") they fill it as a set or individual based on whether the variable metadata is_collective or not
        Plural variables can be:
            a list which means "collective mode" i.e. the group is treated as "together", 
            a single value because it is "distributive mode"

    coll vs. dist
        The quantifier that quantifies a plural variable should handle the two alternatives: collective and distributive
            Coll: Send the entire set of x through at once
            Dist: Then divide the x into N individuals and send them through
            whether coll or dist mode "succeeds" depends on the semantics of the quantifier
            
    quantifiers: 
        count the number of rstrs that are in the body
        see if the count matches the quantifier
        set the variable to coll or dist before calling rstr

    cardinals:
        In a perfect world card() would stay as card(c, x) which means that it *must* always work on a set
        which means that the rstr would stay a set and only the quantifier changes it to something else
        The problem is that things in the rstr like together_p, separately(), 

        The rule could be: 
            in a rstr: if the binding metadata mode is None, it should do the default which, for plural, is to treat a variable as a set
            something in the rstr can set the binding mode one way or the other as well
            when the quantifier finally gets it, it is allowed to convert to dist OR coll if the mode is None, otherwise it can only do one of them
        So: card(2, x) does *not* change the mode, it leave it at None, BUT: it only works on a set, and it produces groups of 2
            it can get modified by "separate", "together", "at least", etc

            Issue: "only 2 files are large" is a challenge since it needs to fail for the first 2 through if there is a second 2
                - workaround: could set some bit that the quantifier uses since it works fine if we do card(udef_q(

                                        ┌──── _file_n_of(x3,i11)
                                        │ ┌── _only_x_deg(e5,e6)
                            ┌────── and(0,1,2)
                            │               └ card(2,e6,x3)
                udef_q(x3,RSTR,BODY)
                                 └─ _large_a_1(e2,x3)
            Issue: "files are large" should fail if there is only 1 file.  Similar problem to the above. Means "only > 1 x" 
            solution: just add a property to the binding that only the quantifier looks for. For plural, it can be inferred. Call this a "gate"

    bare plurals:
        Option: A fake cardinal is put in the rstr of quantifiers if there isn't one ("rocks are in this folder")
            does this work for "rocks are in 5 folders"?
            doesn't work for "which rocks are in 5 folders"?
        Option: The quantifier runs them through one at a time and succeeds with the set of all that are true
            "rocks are in folders"
            doesn't work for "rocks are together", "together" needs a set
        Option: There is always an implicit plural(x) on a bare plural

    Words
        udef_q means: as many as work in the body
            BUT: if it is plural, it has to be at least 2, if it is "2 files" it has to be at least two, etc
            So, It does check a cardinal (sometimes implicit) against the resulting successful items


Future optimization:
    What is the model behind constraints?
        you can call "eval()" on a constrained variable and it will yield all the answers
        if you set_x() a constrained variable ?? It fails ??
            need to start doing "yield from state.set_x()" so that set_x can not yield anything if it fails?

    Optimization: terms assigning values to an unset variable just add a filter to it, at the moment the set_x is called with a non-filter, the filters are run 
        "rocks are together":
                    ┌────── _rock_n_1(x3)
        udef_q(x3,RSTR,BODY)
                         └─ _together_p(e2,x3)

History:
    Alternative option for cardinal handling:

        option 2:
            rewrite the term.

            cardinals get turned into the form card(c, x, body)
            In this model: a plural quantifier gets 3 things: quantifier_q(x, CARD, RSTR, BODY)
                Things like udef_q() run like card(x, udef_q(....
                    "two files are large" -> 
                        Option 1: udef_q([card(2, x), file(x)], large(x)): would work, but would iterate through all sets of 2 files
                        Option 2: udef_q(card(2, x), file(x), large(x)): allows udef to run the cardinal *after* but only works if it is really:  card(2, x, udef_q(file(x), large(x)))
                Things like "the" use the cardinal after the rstr
                Things like "a" as in "a few dogs" or "only a few dogs" use the cardinal on the body to check how many
                examples:
                    children ate pizzas: could be 2 children each ate 2 pizzas, or 2 children ate 2 pizzas
