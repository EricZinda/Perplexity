
## Links
https://www-users.york.ac.uk/~ez506/downloads/EGG_Plurals_2.pdf
http://people.umass.edu/scable/LING720-FA13/Handouts/Mendia-Presentation.pdf
https://sites.rutgers.edu/kristen-syrett/wp-content/uploads/sites/40/2018/09/Distributivity_Syrett.pdf
Really useful info from Hobbs: https://www.isi.edu/~hobbs/metsyn/metsyn.html
From: https://www.isi.edu/~hobbs/metsyn/node9.html
- https://www.ncbi.nlm.nih.gov/pmc/articles/PMC3819043/
- http://www.lingref.com/cpp/wccfl/35/paper3417.pdf

## Tests
Go through wikipedia examples: many more, less than 5, not very many, both the x, all the y
the 2 folders have 1 file each
https://en.wikipedia.org/wiki/List_of_English_determiners
https://sites.rutgers.edu/kristen-syrett/wp-content/uploads/sites/40/2018/09/Distributivity_Syrett.pdf
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

## Facts/Terms
distributive, collective, or mixed (allowing for other interpretation) ((Link 1983, 1987, Dowty
1986, Lasersohn 1995)

Cumulative started with Scha (1981) (https://people.umass.edu/scable/LING720-FA10/Handouts/Scha-198184.pdf)
  Cumulative readings have the following two properties:
  1. Each boy must participate in the carrying, and each piano must be carried.
  2. There is no number dependency between the two arguments. (No type 3 distributivity)

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


  - if a predication can work for either (i.e. isn't wrong) it should let them through but not mark them as processed
  - if it processes coll differently, it should mark them as processed
  - if it doesn't work for either coll or dist it should fail for the one it doesn't work for
      - if it only allows coll, it should mark them as processed (or they won't get selected since dist is the default)

All the intermediate (non-index) predications in a phrase should just pass through collective and distributive options if they are valid but not processed specially (like "lift") so that downstream predications get a chance to look at them. However, the index predication is the last one in the phrase, and if *it* does this, it will return a bunch of duplicates. So, it should fail on any that aren't processed specially because they are dups. We do this automatically by forcing verbs to declare in `vocabulary` if they process collective verbs specially, and we don't even call them with collective if they don't process them (or if something in the tree didn't process them).

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
- 
## List of quantifiers:
  _a+bit_q : ARG0 x { NUM sg }, RSTR h, BODY h.
  _a+fourth_q : ARG0 x, RSTR h, BODY h.
  _a+further_q : ARG0 x { NUM pl }, RSTR h, BODY h.
  _a+great+many_q : ARG0 e, ARG1 x { NUM pl }.
  _a+little_q : ARG0 x { NUM sg }, RSTR h, BODY h.
  _a+third_q : ARG0 x, RSTR h, BODY h.
  _a+total_q : ARG0 x, RSTR h, BODY h.
  _a_q : ARG0 x { IND + }, RSTR h, BODY h.
  _all_q : ARG0 x, RSTR h, BODY h.
  _an+additional_q : ARG0 x { NUM pl }, RSTR h, BODY h.
  _an+average_q : ARG0 x, RSTR h, BODY h.
  _another_q : ARG0 x, RSTR h, BODY h.
  _any+more_q : ARG0 x, RSTR h, BODY h.
  _any_q : ARG0 x, RSTR h, BODY h.
  _both_q : ARG0 x { NUM pl }, RSTR h, BODY h.
  _certain_q : ARG0 x, RSTR h, BODY h.
  _each+and+every_q : ARG0 x, RSTR h, BODY h.
  _each_q : ARG0 x, RSTR h, BODY h.
  _either_q : ARG0 x, RSTR h, BODY h.
  _enough_q : ARG0 x, RSTR h, BODY h.
  _every_q : ARG0 x, RSTR h, BODY h.
  _half_q : ARG0 x, RSTR h, BODY h.
  _less+than+a_q : ARG0 x, RSTR h, BODY h.
  _less_q : ARG0 x, RSTR h, BODY h.
  _little+or+no_q : ARG0 x { NUM sg }, RSTR h, BODY h.
  _many+a_q : ARG0 x { IND + }, RSTR h, BODY h.
  _more_q_than : ARG0 x, RSTR h, BODY h.
  _most+every_q : ARG0 x, RSTR h, BODY h.
  _most_q : ARG0 x, RSTR h, BODY h.
  _neither_q : ARG0 x, RSTR h, BODY h.
  _no+more_q : ARG0 x, RSTR h, BODY h.
  _no_q : ARG0 x { NUM sg }, RSTR h, BODY h.
  _no_q : ARG0 x, RSTR h, BODY h.
  _not+all_q : ARG0 x, RSTR h, BODY h.
  _part_q : ARG0 x, RSTR h, BODY h.
  _q_a_colon : ARG0 i, ARG1 h.
  _some+more_q : ARG0 x, RSTR h, BODY h.
  _some_q : ARG0 x, RSTR h, BODY h.
  _some_q_indiv : ARG0 x, RSTR h, BODY h.
  _such+a_q : ARG0 x { IND + }, RSTR h, BODY h.
  _such_q : ARG0 x, RSTR h, BODY h.
  _that_q_dem : ARG0 x, RSTR h, BODY h.
  _the+least_q : ARG0 x, RSTR h, BODY h.
  _the+most_q : ARG0 x, RSTR h, BODY h.
  _the_q : ARG0 x, RSTR h, BODY h.
  _these_q_dem : ARG0 x { NUM pl }, RSTR h, BODY h.
  _this_q_dem : ARG0 x, RSTR h, BODY h.
  _those_q_dem : ARG0 x { NUM pl }, RSTR h, BODY h.
  _thrice_q : ARG0 x, RSTR h, BODY h.
  _times4_q : ARG0 x, RSTR h, BODY h.
  _times5_q : ARG0 x, RSTR h, BODY h.
  _twice+a_q : ARG0 x, RSTR h, BODY h.
  _twice_q : ARG0 x, RSTR h, BODY h.
  _umpteen_q : ARG0 x { NUM pl }, RSTR h, BODY h.
  _what+a_q : ARG0 x { IND + }, RSTR h, BODY h.
  _which_q : ARG0 x, RSTR h, BODY h.
  _x_q : ARG0 x, RSTR h, BODY h.
  a_or_freerel_q : ARG0 x, RSTR h, BODY h.
  a_or_no_q : ARG0 x, RSTR h, BODY h.
  abstr_def_or_udef_q : ARG0 x, RSTR h, BODY h.
  abstract_q : ARG0 x, RSTR h, BODY h.
  any_q : ARG0 x, RSTR h, BODY h.
  basic_def_explicit_q : ARG0 x, RSTR h, BODY h.
  basic_free_relative_q : ARG0 x, RSTR h, BODY h.
  both_all_q : ARG0 x, RSTR h, BODY h.
  both_all_udef_q : ARG0 x, RSTR h, BODY h.
  def_explicit_q : ARG0 x, RSTR h, BODY h.
  def_or_demon_q : ARG0 x, RSTR h, BODY h.
  def_or_proper_q : ARG0 x, RSTR h, BODY h.
  def_or_udef_or_demon_q : ARG0 x, RSTR h, BODY h.
  def_or_udef_q : ARG0 x, RSTR h, BODY h.
  def_poss_or_barepl_or_prop_q : ARG0 x, RSTR h, BODY h.
  def_poss_q : ARG0 x, RSTR h, BODY h.
  def_q : ARG0 x, RSTR h, BODY h.
  def_udef_a_q : ARG0 x, RSTR h, BODY h.
  def_udef_some_a_no_q : ARG0 x, RSTR h, BODY h.
  defdate_q : ARG0 x, RSTR h, BODY h.
  demon_far_q : ARG0 x, RSTR h, BODY h.
  demon_near_q : ARG0 x, RSTR h, BODY h.
  demonstrative_q : ARG0 x, RSTR h, BODY h.
  every_q : ARG0 x { NUM sg }, RSTR h, BODY h.
  exist_or_univ_q : ARG0 x, RSTR h, BODY h.
  existential_q : ARG0 x, RSTR h, BODY h.
  explicit_noagr_nodef_q : ARG0 x, RSTR h, BODY h.
  explicit_nodef_q : ARG0 x, RSTR h, BODY h.
  explicit_or_proper_q : ARG0 x, RSTR h, BODY h.
  explicit_q : ARG0 x, RSTR h, BODY h.
  explicit_quant_agr_q : ARG0 x, RSTR h, BODY h.
  explicit_quant_noagr_q : ARG0 x, RSTR h, BODY h.
  explicit_quant_or_udef_noagr_q : ARG0 x, RSTR h, BODY h.
  free_relative_ever_q : ARG0 x, RSTR h, BODY h.
  free_relative_q : ARG0 x, RSTR h, BODY h.
  idiom_q_i : ARG0 x, RSTR h, BODY h.
  impl_or_expl_or_pron_q : ARG0 x, RSTR h, BODY h.
  impl_or_expl_or_prop_q : ARG0 x, RSTR h, BODY h.
  impl_or_expl_q : ARG0 x, RSTR h, BODY h.
  impl_or_proper_q : ARG0 x, RSTR h, BODY h.
  impl_or_the_q : ARG0 x, RSTR h, BODY h.
  implicit_q : ARG0 x, RSTR h, BODY h.
  meas_np_or_proper_q : ARG0 x, RSTR h, BODY h.
  no_q : ARG0 x, RSTR h, BODY h.
  nodef_q : ARG0 x, RSTR h, BODY h.
  non_freerel_q : ARG0 x, RSTR h, BODY h.
  non_pronoun_q : ARG0 x, RSTR h, BODY h.
  nondef_explicit_q : ARG0 x, RSTR h, BODY h.
  num_or_demon_q : ARG0 x, RSTR h, BODY h.
  num_or_proper_q : ARG0 x, RSTR h, BODY h.
  num_q : ARG0 x, RSTR h, BODY h.
  number_q : ARG0 x, RSTR h, BODY h.
  pronoun_q : ARG0 x, RSTR h, BODY h.
  proper_q : ARG0 x, RSTR h, BODY h.
  some-any_q : ARG0 x, RSTR h, BODY h.
  some_q : ARG0 x, RSTR h, BODY h.
  udef_a_q : ARG0 x, RSTR h, BODY h.
  udef_or_proper_q : ARG0 x, RSTR h, BODY h.
  udef_q : ARG0 x, RSTR h, BODY h.
  universal_q : ARG0 x, RSTR h, BODY h.
  which_q : ARG0 x, RSTR h, BODY h.
