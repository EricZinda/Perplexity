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
1 file is in this folder
each/all/every
3 boys each carried for pianos (forces boys to dist)
) A group of three boys carried a group of four pianos. (forces both collective)
all 3 boys carried all 3
The cards below 7 and the cards from 7 up were separated.
The boys surrounded the building
Mary  and  Sue are  room-mates.  
The  girls hated  each  other. 
The girls told the boys two stories each
The boys are tall.
Two students danced. (could be either)
The boys are building a raft.
    The boys are building a raft each. (operator fixex)
    Every boy is building a raft. (quantifier fixes)
(Lasersohn 1995): The students closed their notebooks, left the room, and gathered in the hall after class. (The same DP can have both collective a distributive readings in
the same sentence.)
John and bill are a good team.
The committee is made up of John, Mary, Bill and Susan.
(Gillon 1987, 1990) Gilbert, Sullivan and Mozart wrote operas.
    - fact: Mozart wrote operas, and Gilbert and Sullivan wrote operas.
(Gillon 1987, 1990) Rodgers, Hammerstein and Hart wrote musicals.
    - fact: Rodgers and Hammerstein wrote musicals together, and Hammerstein and Hart wrote musicals together, but they did not write musicals as a trio, nor individually.
Schwarzschild (2011).  Force distributive: be round/square, have brown/blue eyes, be tall/big, and be intelligent
Those boxes are heavy. (could be both)
Three boys are holding each balloon.
Two boys (each) pushed a car (together).
Two boys (each) built a tower (together).
Two girls pushed a car (together).
Two girls (each) drew a circle (together).

(see Landman, 2000, Tunstall, 1998)
    Jake photographed every student in the class, but not separately.
    Jake photographed each student in the class, but not separately

No professors are in class
    Are there professors in class?


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

Need another design:
    Deeper issues:
    - "which files are 20 mb": Singular is an OK answer in this situation, but returns nothing if there is only one file

    variables are always sets, could be a set of 1
    predications always yield all the solutions
    file_n will always set x to the set of files
    There is a difference between predications "filtering" x and "checking" x. Can't get my head around it
        large_a operates in two modes:
            as a verb, it will only work on sets of 1
            as an adjective, it filters the set down

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
        the quantifier quantifies *over* the sets managed by the cardinality.  Thus "only a few x" means "1 set of a few"
        the quantifier x binding gets a mode set to say which mode it is in
        How to handle any coll/dist restrictions (like together, separately):
            together() sets a property on the variable binding to say which mode it has to be in. 
            The quantifier pays attention and does the right thing
        How to handle the cardinality restriction?
            The rstr sets x to a set AND (potentially) adds a criteria to how many elements of x must be true in the solution. 
                For card(2) it means "exactly 2"
                For at most card(2) it means "<= 2"
                If there is no cardinal in a plural it means "> 1"
    2 children ate 2 pizzas
        run the set of children through as a set
            then see how many of the set remain
        run the set of children through as a set of N
            then see how many of that group remain

Failed design:
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
