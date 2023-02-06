## Plurals and Cardinals
We have a bug in the system built so far.  This example shouldn't work:

~~~
def Example24_reset():
    return FileSystemState(FileSystemMock([(True, "/temp/59.txt", {"size": 1000}),
                                           (True, "/documents/file1.txt", {"size": 1000}),
                                           (False, "/Desktop", {"size": 10000000}),
                                           (True, "/Desktop/the yearly budget.txt", {"size": 10000000}),
                                           (True, "/Desktop/blue", {"size": 1000})],
                                          "/Desktop"))


def Example24():
    user_interface = UserInterface(Example23_reset, vocabulary, respond_to_mrs_tree, error_priority)

    while True:
        user_interface.interact_once()
        print()
        
        
# Running Example24()
? what file is in "/Desktop"?
File(name=/Desktop/the yearly budget.txt, size=10000000)
File(name=/Desktop/blue, size=1000)
~~~

The user asked "what file" (singular) and the system responded with 2 files. The system so far is ignoring the plurality information given by the system.

As described in the [MRS topic](../devhowto/devhowtoMRS#variable-properties), plurality is provided in the MRS as a variable property on an individual (i.e. `x` variable). You can see that in the MRS for the above phrase:

~~~
[ "what file is in "/Desktop"?"
  TOP: h0
  INDEX: e2 [ e SF: ques TENSE: pres MOOD: indicative PROG: - PERF: - ]
  RELS: < [ _which_q<0:4> LBL: h4 ARG0: x3 [ x PERS: 3 NUM: sg IND: + ] RSTR: h5 BODY: h6 ]
          [ _file_n_of<5:9> LBL: h7 ARG0: x3 ARG1: i8 ]
          [ _in_p_loc<13:15> LBL: h1 ARG0: e2 ARG1: x3 ARG2: x9 [ x PERS: 3 NUM: sg ] ]
          [ proper_q<16:28> LBL: h10 ARG0: x9 RSTR: h11 BODY: h12 ]
          [ fw_seq<-1:-1> LBL: h13 ARG0: x9 ARG1: i14 ]
          [ quoted<17:26> LBL: h13 ARG0: i14 CARG: "\\>Desktop" ] >
  HCONS: < h0 qeq h1 h5 qeq h7 h11 qeq h13 > ]
~~~

"Which file" is represented by the variable `x3` in the MRS, and it has the following properties:

~~~
x3 [ x PERS: 3 NUM: sg IND: + ]
~~~

`NUM` has the value `sg` which means "singular". If it was plural it would be `pl`.

Plural is tricky because it is, in a sense, doing another level of quantification in addition to whatever quantification the quantifier does. For example, "The X" usually implies that there will be a single X and the quantifier implementation would insure that. But "The rocks" really means that there is one *set* of rocks. There are also words called *cardinals* that provide finer grained "extra quantification" but are not quantifiers. These are words like "many, few, several, 2, 3, 4, etc". All of these act very much like the `NUM=pl/sg` variable property in that they restrict some variable to be of a certain quantity. In fact, the way we will implement singular and plural will be the same way we implement the cardinals.  

When applied to a noun as in the phrase "a few files", the cardinal "few" will always appear as a predication in the `RSTR` of the quantifier (in this case "udef_q") being used:

~~~
                           ┌── quoted(/documents,i15)
               ┌────── and(0,1)
               │             └ fw_seq(x10,i15)
proper_q(x10,RSTR,BODY)
                    │                          ┌── _file_n_of(x3,i9)
                    │              ┌────── and(0,1)
                    │              │             └ _a+few_a_1(e8,x3)
                    └─ udef_q(x3,RSTR,BODY)
                                        └─ _in_p_loc(e2,x3,x10)
~~~

[`udef_q` is just a "default quantifier" like `proper_q`, and can just be added as a synonym to the default quantifier implementation that already exists.]

You can see that "a few" gets converted to the predication `_a+few_a_1` in the `RSTR` of `udef_q`

For the phrase, "1 file is in '/documents'" we get:

~~~
                           ┌── quoted(\\>documents,i16)
               ┌────── and(0,1)
               │             └ fw_seq(x11,i16)
proper_q(x11,RSTR,BODY)
                    │                          ┌── _file_n_of(x3,i10)
                    │              ┌────── and(0,1)
                    │              │             └ card(1,e9,x3)
                    └─ udef_q(x3,RSTR,BODY)
                                        └─ _in_p_loc(e2,x3,x11)
~~~

... which is analogous, but uses the predication `card(1,e9,x3)`.  Both this and the previous case could be interpreted as "*only* 1 file is in '/documents'" or "*at least* 1 file is in '/documents'".  We can choose "at least" as the default, and force the user to use "only 1 file" if they want the other. We could obviously go the other way as well.

Either way, we have a problem in that the cardinal predications don't operate on a set. [list reasons why this is a problem] There are in the wrong *form*, we really need them in a quantifier form with scopal arguments to do this properly. 

For default quantifiers it will be enough to run the cardinal on the output of the quantifier without the cardinal, and then let the cardinal count, like this:
~~~

~~~

But, consider how "the" works, it effectively is adding "only" to the cardinal. If the user says "the two files in "/documents" are hidden" they pretty clearly mean "there is *only* two files". So, the logic of `card(2, ...)` being true if there are *at least* won't work. "The" will need to add "only" to the cardinal

Secondly, plural nouns have both collective and distributive readings. For example, consider “four children ate three pizzas”. The collective reading is that three pizzas were eaten in total. The distributive reading is that each child ate three pizzas, so twelve pizzas were eaten in total.

- The collective reading has exactly 4 children and 3 pizzas, in total: the children are collectively doing the eating, and the pizzas are collectively being eaten.
  - we use card on the rstr and "choose 3" that get used
- The distributive reading is that each child ate three pizzas, so twelve pizzas were eaten in total.
- The distributive reading with inverse scope (inverse with respect to the surface word order) has 3 pizzas and 12 children.

Theory: 
    - The RSTR either picks a set of N, or loops through N different individuals
    - one approach is using the cardinal to choose a set and push that set through the system
        - This means that the body must be true for a set of N things
            - So for "The men lifted the table (together)", it needs a way to know that it is operating on a set
                - For many (most) interpretations you won't be able to tell the difference between this and the distributive
                    - so maybe we don't handle it?? Let's try starting there, without supporting it
                        To make this work iteratively: pickn(pizzas), pickn(children): There is one set of 3 pizzas that was eaten by one set of 4 children
                            - You need the body to collect all the things that make it true until it gets the right number 
        - A plural quantifier operating in collective mode means the solution found should also be true for the next thing coming in
            - need a way to reset and backtrack, though
            - seems like this is just a regular iterator
                - maybe the body of the first cardinal has a term which is the next cardinal
                    - the cardinal itself knows if it is operating in dist or coll mode.  
                        - If coll, then it only returns when its criteria is met (like having 4 children that eat the first pizza)
                        - If it is called again, because it is in coll model, it tries the same 4 children again, 
                            - if it fails it has to find a new set of four
        - Approach:
            - The problem is that you have to pick every combination of items to make this work
            - Or maybe we simply iterate through all the answers and only return the one that is a single set
        - Another approach:
            - Run the quantifiers with no cardinals, you get a set of solutions with the two variables (children and pizzas)
            - Then, run the cardinals on those to match the criteria
        - Another approach:
            - First pizza chosen, 4 children are found
            - Next pizza chosen, same 4 children are tried again
                - If it fails, backtrack and find 4 more for the first pizza
        - Another approach:
            - have different predications, or even trees for coll and dist that just do different stuff
        - Another approach: collective mode means: find a set of card items for which this is true
        - Observation: To handle two cardinals in a phase, the predications involved *must* know that they are operating on a set or they will not be able to make the "men lifted a table" work properly. Either:
            - The inner one somehow needs to know it is operating on a set, either:
                - needs to get the whole set from the outer one so it can backtrack (or whatever)
                - Or the outer one needs a way to manipulate the inner one to iteratively pass it items
            - (Doesn't make "men lifted a table" work properly) We have to find all combinations without the cardinals until they are both true
    - the other is acting on the result of the quantifier
        cardinal(..., default_q(x, base_rstr, body)

What is the difference between collective and distributive from the perspective of the quantifier?
    - There is no difference here:
        - (collective) Whatever the body does must be true of the whole set
            - Once we have N RSTR items that are true in the body we are done
        - (distributive) Whatever the body does must be true only of each individual
            - Once we have N RSTR items that are true in the body we are done
    - The body needs to get a solution and then apply it to each member of the set

        - The body solution should be the same for each member of the set?
    - The body in the first example below (when acting distributive) is finding 4 different children that each ate the (collective) first RSTR
        - So we hold the child constant and loop through all of the items in the RSTR
    - The body in the first example below (when acting collective) is finding 4 different children that *together*  ate the (collective) first RSTR, which is the same as above for eating but not for lifting
        - So we hold the child constant and loop through all of the items in the RSTR
    - 
~~~
    - pickn(pizzas), pickn(children): There is one set of 3 pizzas that was eaten by one set of 4 children (everyone ate them together = 3 pizzas)
    - quant(pizzas), pickn(children): There are 3 different individual pizzas that each was eaten by a (potentially different) set of 4 children  (pick a pizza, a group of 4 children ate that one)
    - pickn(pizzas), quant(children): There is one set of 3 pizzas that was eaten by 4 different individual children  (same as 1??, not if we are talking about lifting...)
    - quant(pizzas), quant(children): There are 3 different individual pizzas that each was eaten by a (potentially different) individual child (each of 3 pizzas had 4 different children eating it (same as 2??))
there must be 3 pizzas and there must be 4 (possibly different) children for every pizza = 12
OR 3 pizzas and the same 4 children eating them

                         ┌── _pizza_n_1(x10)
             ┌────── and(0,1)
             │             └ card(3,e16,x10)
udef_q(x10,RSTR,BODY)
                  │                          ┌── _child_n_1(x3)
                  │              ┌────── and(0,1)
                  │              │             └ card(4,e9,x3)
                  └─ udef_q(x3,RSTR,BODY)
                                      └─ _eat_v_1(e2,x3,x10)
                                      
There must be 4 children and each one must eat 3 (possibly different) pizzas = 12

- pickn(children), pickn(pizzas): There is one set of 4 children that ate one set of 3 pizzas (same as above)
- quant(children), pickn(pizzas): There are individual children that each ate a (potentially different) set of 3 pizzas
- pickn(children), quant(pizzas): There is one set of 4 children that ate 3 different individual pizzas
- quant(children), quant(pizzas): There are 4 individual children that each ate a (potentially different) pizza
                                   
                        ┌── _child_n_1(x3)
            ┌────── and(0,1)
            │             └ card(4,e9,x3)
udef_q(x3,RSTR,BODY)
                 │                           ┌── _pizza_n_1(x10)
                 │               ┌────── and(0,1)
                 │               │             └ card(3,e16,x10)
                 └─ udef_q(x10,RSTR,BODY)
                                      └─ _eat_v_1(e2,x3,x10)
~~~
Our approach will thus be to have the quantifier implementations pull out the cardinals from the RSTR and do the appropriate logic for the quantifier with them.

Really useful info from Hobbs: https://www.isi.edu/~hobbs/metsyn/metsyn.html
From: https://www.isi.edu/~hobbs/metsyn/node9.html

There are two entities associated with plural NPs--the set of entities referred to by the NP and the typical element of that set. In

The men ran.

each individual man must run by himself, so the predicate run applies to the typical element. This is the distributive reading. In
The men gathered.
The men were numerous.

the predicates gather and numerous apply to the set of men. This is the collective reading of the NP. The sentence
The men lifted the piano.

is ambiguous between the two readings. They could each have lifted it individually, the distributive reading, in which case the logical subject of lift would be the typical element of the set, or they could have lifted it together, the collective reading, in which case it would be the set, or the aggregate.
