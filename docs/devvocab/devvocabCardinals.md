## Background
https://www-users.york.ac.uk/~ez506/downloads/EGG_Plurals_2.pdf
http://people.umass.edu/scable/LING720-FA13/Handouts/Mendia-Presentation.pdf
https://sites.rutgers.edu/kristen-syrett/wp-content/uploads/sites/40/2018/09/Distributivity_Syrett.pdf
Really useful info from Hobbs: https://www.isi.edu/~hobbs/metsyn/metsyn.html
From: https://www.isi.edu/~hobbs/metsyn/node9.html
- https://www.ncbi.nlm.nih.gov/pmc/articles/PMC3819043/
- http://www.lingref.com/cpp/wccfl/35/paper3417.pdf

Terms:
distributive, collective, or mixed (allowing for other interpretation) ((Link 1983, 1987, Dowty
1986, Lasersohn 1995)

determiners (https://en.wikipedia.org/wiki/Determiner, https://en.wikipedia.org/wiki/English_determiners): include all quantifiers AND "cardinals" (except pronouns)

### Plurals and Cardinals Background
10 children eating a cake: 10 (distributive) or 1 (collective)
Link (1983) approach

### Collective, Distributative and Cumulative (or subgroup) Readings
There are two entities associated with plural NPs--the set of entities referred to by the NP and the typical element of that set. In
In

The men ran.

each individual man must run by himself, so the predicate run applies to the typical element. This is the distributive reading. In
The men gathered.
The men were numerous.

the predicates gather and numerous apply to the set of men. This is the collective reading of the NP. The sentence
The men lifted the piano.

is ambiguous between the two readings. They could each have lifted it individually, the distributive reading, in which case the logical subject of lift would be the typical element of the set, or they could have lifted it together, the collective reading, in which case it would be the set, or the aggregate.


Cumulative started with Scha (1981) (https://people.umass.edu/scable/LING720-FA10/Handouts/Scha-198184.pdf)
Three boys carried two pianos.
Cumulative readings have the following two properties:
1 Each boy must participate in the carrying, and each piano must be
carried.
2 There is no number dependency between the two arguments. (No type 3 distributivity)

From wikipedia: https://en.wikipedia.org/wiki/Cumulativity_(linguistics)
If X is true of both of a and b, then it is also true of the combination of a and b

### Implied initial quantifier
"which 2 rocks are in 2 folders" has an implied cardinal of "a"

### quantifiers and cardinals
Quantifiers 

### Verbs and operators usage of cardinality
(Link 1983, 1987, Dowty 1986, Lasersohn 1995).
Some verbs force collective, distributive or mixed:
- collective: "the dogs surrounded the prey"
  - met: collective
  - gather:

- distributive: "The shrimp are red"
  - tall: distributive (but sara and mary are standing on each others shoulders they can be tall together)
  - scatter:

- mixed: "The children ate a cake"
    - dance: both

Quantifiers and other words can be added to force one way or another: 
- "each child ate a cake" each strongly encodes distributive
- "every child ate a cake" (weaker) encodes distributive

### Verb Implementation

There are two things that need to be managed for a predicate: 
- Whether it *allows* coll/dist: if a verb like surrounded(who, what) *forces* what to always be collective, it should fail for dist for that argument. Otherwise, for verbs like "in" which have a collective interpretation but don't do anything, it should process it when it is not the verb. When it is the verb, it shouldn't, to remove duplicates
- Whether it acts differently in the presence of coll/dist. Verbs that support both need to return answers for both so that downstream cardinals get the opportunity to try them.  However, if they actually have different answers for dist/coll (like "the men lifted the table", lifted(men:dist) is different than lifted(men:coll) they have to *mark* that they processed it so that the answers are preserved. Otherwise the engine will remove duplicates.

two children in two rooms ate 3 pizzas

A given variable is either coll or dist. if it was processed identically for both options, we should only keep one of them.
At the end, if a cardinal processed a coll variable, we should keep it.





### Weird cases
"which rocks are in here?" - the speaker assumes it will return single rocks.  bare Plurals just assumes there is one.
Another example? How many rocks are there? Answer: 1

4 files are in a folder together -> forces collective which doesn't make sense with "in" so it fails with ['formNotUnderstood', 'missing', 'collective']
    If you said "4 files are in a folder" it could find 4 different folders
    So in this case the user could be using it as a way to say "4 files are in the same folder"
## Approach
From the cardinal's perspective, they are just building up sets of N, it is the other predications that have to do something interesting with the "men lifting table"
Questions:

This is a pipeline. Each node of the pipeline needs to find a set of N items that are true in the body for all of the set of M incoming items
    Assume that the incoming is *always* a set, it may just be of one item, N = 1
    If incoming item is the first in its set, start a new set
The only state we need to keep for cardinal, outside of when it is checking a set, is the current successful set, and the combinator

The problem is that you have to pick every combination of items to make this work
Rewrite: quantifier_q(x, [cardinal(x, ...), cardinal_modifier()], body)
To the form: [cardinal_modifier(), cardinal_with_scope(x, non_cardinal_rstr, base_quantifier_q(x, thing(x), body)]
Observation: To handle two cardinals in a phase, the predications involved *must* know that they are operating on a set or they will not be able to make the "men lifted a table" work properly.
the cardinal's job is to find N things that match its body, once that succeeds, it returns them all

If a set is being pushed through there is a group context, this allows children to know they are dealing with a group. Things that don't care about groups (like a noun) can ignore it
For a child: each cardinal is finding a set and applying it to a parent set. The difference between coll and dist mode is whether its set applies to the parent set *as a group* or *individually*

observation: it is *eat* that is the one having to deal with sets, child and pizza are both just choosing items
    - For many (most) interpretations you won't be able to tell the difference between coll and dist
        - so maybe we don't handle it?? Let's try starting there, without supporting it
            To make this work iteratively: pickn(pizzas), pickn(children): There is one set of 3 pizzas that was eaten by one set of 4 children
                - You need the body to collect all the things that make it true until it gets the right number 
    - Really it just has to execute at the end and somehow mark as a single thing that happened

definitions:
variable set: a group of values that are treated as a whole. The group has a unique variable_set_id
variable set item: one element of a variable set
variable_set_cache: programming language construct that allows children to store information in the parent variable set so it is there next time
cardinal group: A cardinal has a group of variable sets that it deals with called a cardinal group. For coll, it is a list of one set of N, for dist it is a list of N sets of 1
                  it is a group of pairs of variable_set_id/[list of values]
cardinal group item: one of the sets in the cardinal group
variable_set_restart exception: is a way for a child to restart the parent variable set if the child set didn't work 
cardinal group generator: creates a new cardinal group (coll or dist).  Its scope is a parent variable set
solution alternatives: For a given set, there might be more than one answer in the children. These are the alternatives

NEED TO DISCUSS WHAT SOLUTIONS LOOK LIKE AND HOW TO DISENTANGLE THEM
NEED TO TALK ABOUT HOW TO ANSWER
TALK ABOUT HOW VARIABLES ARE MARKED SO WE KNOW WHAT IS IN THEM
  - The ultimate result should be variables with sets in them. 
    - 5 children eating the same 5 pizzas: x5=[child1, ...], x6=[pizza1, ...]
      - each child eating a different 5: x5=[child1], x6=[pizza1, ....]
      - Also need to return which *element* of a set an item is so it won't be repeated in the answer 
  
      - collective mode matters even if there is one cardinal in the phrase. For example: the men lifted the table could be one after the other or together
        - So, something needs to create the top level group and switch it between the modes

There are correct:
- Don't try a coll and dist *variation* of children of the last cardinal if there are no children. This is never right and creates duplicates. because there is nothing after it that gets to "rechoose" so the answers are the same
- If a predication *doesn't support* coll or dist (like gather/scatter) it needs to fail on that option
- The order of dist, coll or coll, dist matters because the first has scope over the second.  the second gets to *rechoose* answers

How to generate all the unique cardinal groups if nobody cares?
- Remember that each cardinal level picks N *cardinal groups* for each *variable set* that comes in!  The root just sends in one variable set (the empty set).
- So to get the unique cardinal groups, you need *maximize* the number of *variable sets* at each level
  - So you pick dist all the way through to get the maximum number of cardinal groups since this will be a superset of just sending 1 set (i.e. coll) through
  - Really, for the last one it doesn't matter

If somebody distinguishes coll/dist for a given variable, you need to return all alternatives for that level
- You always need to always choose the dist variation for everything up to that level to get the maximum number of cardinal groups handed to it

So:
  - if a predication can work for either (i.e. isn't wrong) it should let them through but not mark them as processed
  - if it processes coll differently, it should mark them as processed
  - if it doesn't work for either coll or dist it should fail for the one it doesn't work for
      - if it only allows coll, it should mark them as processed (or they won't get selected since dist is the default)

if nobody cares, the way to get all the unique answers is to do dist all the way through.

At the very end the logic is:
- If there is a coll, only use it if someone marked it as used_collective or if you want to use it as used_collective
  - At the end you don't want to let coll/dist alternatives that are processed the same pass through if they aren't treated differently because they will be duplicates
- If an answer is all dist, use it.

### How to deal with verbs
used_collective on a variable binding means: something has already processed this collective cardinal set as a set, and so it needs to contribute to the answer

All of the intermediate (non-index) predications in a phrase should just pass through collective and distributive options if they are valid but not processed specially (like "lift") so that downstream predications get a chance to look at them. However, the index predication is the last one in the phrase, and if *it* does this, it will return a bunch of duplicates. So, it should fail on any that aren't processed specially because they are dups. We do this automatically by forcing verbs to declare in `vocabulary` if they process collective verbs specially, and we don't even call them with collective if they don't process them (or if something in the tree didn't process them).

unique_solution_if_index() will only allow coll solutions that were actually processed to come through, as well as any that are listed in different_collective_behavior because those are the ones that this predication is going to process.

if someone says "delete 2 files together in this folder", "together" only allows through collective variables, or, if it is a cardinal-bearing variable that hasn't been processed, forces it to collective mode, so that the cardinal that generates the cardinal groups will only do that option.

for something like "in", it should get rid of coll/dist duplicates if it is the index, UNLESS they were processed or it is processing them specially.

General programming model: By default, assume they do not handle groups specially, so call unique_solution_if_index([]).  This will not do anything if it is not the index predication.
- If they handle particular collectives, they to to set that on the call.

How to handle: delete 2 files together in this folder?
- like "in", it can delete a coll but treats it like dist
- unique_solution_if_index() will allow a group through if one is used, but otherwise ignores it.

We can't get the sets directly because they might not be on the context stack anymore?
So instead we have to collect them

### Rewriting terms
“which 2 files in this folder together are 2 megabytes”
                         ┌── _megabyte_n_1(x19,u26)
             ┌────── and(0,1)
             │             └ card(2,e25,x19)
             │                                                           ┌────── _together_p_state(e18,e11)
udef_q(x19,RSTR,BODY)                                                    │
                  │                                          ┌────── _fol│er_n_of(x12,i17)
                  │                ┌────── _this_q_dem(x12,RSTR,BODY)    │ ┌──── _in_p_loc(e11,x3,x12)
                  │                │                              └─ and(0,1,2,3)
                  │                │                                         └─│ _file_n_of(x3,i10)
                  └─ _which_q(x3,RSTR,BODY)                                    │
                                        │                                      └ card(2,e9,x3)
                                        └─ loc_nonsp(e2,x3,x19)

if we treat card(2,e9,x3) like:
    card(, [file, in, together], thing(x))
    in the body, would it work

Really, the parent_variable_set_cache is just:
- alternating between coll/dist
- giving each cardinal a place to cache information
- allowing the cardinals to communicate (retry, etc)

The information about what state we are in is in the bindings.

If we only assume that things that modify the cardinal are in the same conjunction with it we could convert 

### Dealing with size
100 MB would be a set of 100.  Optimize

### Dealing with answers
If there are 3 files:
? which 2 files are in this folder? / delete 2 files in this folder
File(name=/Desktop/yellow.txt, size=1000000)
File(name=/Desktop/green.txt, size=1000000)

File(name=/Desktop/yellow.txt, size=1000000)
File(name=/Desktop/orange.txt, size=1000000)

File(name=/Desktop/green.txt, size=1000000)
File(name=/Desktop/orange.txt, size=1000000)

delete will delete them all.  There is an implicit "which (single group of) two files" which should return a failure if there are more than two

### How to deal with in and files
How in(what, where) works for sets.  [a, b] in [x, y] is the same as [a], [b] in [x], [y], i.e. the grouping of either doesn't matter. 
- So, as long as the cardinal groups are the same, the answers *as far as this predicate is concerned* are duplicates.

If a person says "two files in a folder together" it is forcing a group, so we should respect it and return the coll options, even though "in" returns the same thing.
If a person just says "two files are in a folder", just return the combinations

### How to deal with "x is verb y together"
"together_p_state" should simply create the appropriate group and call it handled *before* it gets to the predication, and also cancel out dist/dist
If together applies to the verb, it isn't clear if it is grouping the left, right or both sides (at the same time). Return them all.
the predications will just pass it through

Thus we can test all the possible coll/dist options by using:
- two files are in two folders (returns dist/dist)
- two files are in two folders together (returns coll/dist, dist/coll, coll, coll)

### How to deal with lift or any predicate that treats a group differently
Option 1: 
- Set a property of the variable? that says how many items in the group
- The verb must succeed for all the options, and collect them for a parent cardinal group, until it hits the final one
- On the final one it checks the whole set for the semantic. If it doesn't work, it sends a special exception to the parent to fail the cardinal group

## Multiple answers with cardinals
if there are two files in one folder and two in another and you say "delete two files in 2 folders together", which files get deleted

## Examples
files in folders:
in_p_loc doesn't treat either side differently if coll or dist.
~~~
  - file(dist), fold(dist): file1 in fold1, file1 in fold2, file2 in fold3, file1 in fold4
  - file(coll), fold(dist): file1 & file2 in fold1, file1 & file2 in fold2
  - fold(dist), file(dist): fold1 contains file1, fold1 contains file2, fold2 contains file3, fold2 contains file4
  - fold(coll), fold(dist): fold1 & fold2 contain file1, fold1 & fold2 contain file2

  - file(dist), fold(coll): file1 in fold1 & fold2, file2 in fold3 & fold4
  - file(coll), fold(coll): file1 & file2 in fold1 & fold2
  - fold(dist), file(coll): fold1 contains file1 & file2, fold2 contains file3 and file4
  - fold(coll), fold(coll): fold1 & fold2 contain file1 & file2

  - file(coll), fold(coll): file1 & file2 in fold1 & fold2
  - file(coll), fold(dist): file1 & file2 in fold1 & fold2
  - fold(coll), file(coll): fold1 & fold2 contains file1 & file2
  - fold(coll), fold(dist): fold1 & fold2 contains file1 & file2

  - file(dist), fold(coll): file1 in fold1 & fold2, file2 in fold3 & fold4
  - file(dist), fold(dist): file1 in fold1 & fold2, file2 in fold3 & fold4
  - fold(dist), file(coll): fold1 contains file1 & file2, fold2 contains file3 and file4
  - fold(dist), fold(dist): fold1 contains file1 & file2, fold2 contains file3 and file4
~~~
~~~
    - coll(pizzas), coll(children): There is one group of 3 pizzas that was eaten by one group of 4 children (3 pizzas, 4 children)
        - each child ate 3 pizzas together
        - each pizza was eaten by 4 children together
    - dist(pizzas), coll(children): There are 3 individual pizzas that each was eaten by a different group of 4 children  (3 pizzas, 12 children)
        - each child ate 1 pizza separately
        - each pizza was eaten by 4 children together
    - coll(pizzas), dist(children): There is one group of 3 pizzas that was eaten by a different 4 individual children (3 pizzas, 4 children)
        (same as 1??, not if we are talking about lifting...)
        - each child ate 3 pizzas together
        - each pizza was eaten by 4 children separately
    - dist(pizzas), dist(children): There are 3 individual pizzas that each was eaten by a different 4 individual children (3 pizzas, 12 children) 
        (same as 2? not if we are talking about lifting))
        - each child ate 1 pizza separately
        - each pizza was eaten by 4 children separately
    

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

- coll(children), coll(pizzas): There is one group of 4 children that, together, ate one group of 3 pizzas (3 pizzas, 4 children)
    (same as 1 above)
    - each child ate a group of 3 pizzas
    - each pizza was eaten by a group of 4 children
- dist(children), coll(pizzas): There are 4 individual children that, each, ate a different group of 3 pizzas (12 pizzas, 4 children)
    - each child ate a group of 3 pizzas
    - each pizza was eaten by 1 individul child
- coll(children), dist(pizzas): There is one group of 4 children that, together, ate the same 3 individual pizzas (3 pizzas, 4 children)
        (same as 3 above??, 
        (same as 1??, not if we are talking about lifting...)
    there are only 3 pizzes
    - each child ate the 3 pizzas separately
    - each pizza was eaten by 4 children together
- dist(children), dist(pizzas): There are 4 individual children that, each, ate a different 3 individual pizzas (12 pizzas, 4 children)
        (same as 2??, not if we are talking about lifting...)
    - each child ate 3 pizzas separately
    - each pizza was eaten by 1 child separately
                                   
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

## Tests
each/all/every
3 boys each carried for piaons (forces boys to dist)
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

# Old
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
