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

Potential designs:
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
        In this model: a plural quantifier gets 3 things: quantifier_q(x, CARD, RSTR, BODY)
            Things like udef_q() run like card(x, udef_q(....
            Things like "the" use the cardinal after the rstr
            Things like "a" as in "a few dogs" or "only a few dogs" use the cardinal on the body to check how many
            examples:
                children ate pizzas: could be 2 children each ate 2 pizzas, or 2 children ate 2 pizzas

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
