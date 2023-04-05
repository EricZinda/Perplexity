## Basic solver approach
Variables are sets that are treated as items
yield all alternatives that make you true
empty variable means "everything"

optimization: combinatorial variables

## Quantifiers
Go through unquantified solutions as they are generated an create groups

## Plurals and Determiners
Plurals are treated as a default determiner

## Plural Solutions
Solutions to an MRS are a list of assignments to variables

~~~
Two boys ate two pizzas
~~~

~~~
                         ┌── _pizza_n_1(x10)
             ┌────── and(0,1)
             │             └ card(2,e16,x10)
udef_q(x10,RSTR,BODY)
                  │                          ┌── _boy_n_1(x3)
                  │              ┌────── and(0,1)
                  │              │             └ card(2,e9,x3)
                  └─ udef_q(x3,RSTR,BODY)
                                      └─ _eat_v_1(e2,x3,x10)
~~~

The solution is both of these together, each on its own is not enough:
~~~
x10=[pizza1, pizza2]        x3=[boy1]
x10=[pizza3, pizza4]        x3=[boy2]
~~~

Delete a file
~~~
               ┌────── pron(x3)
pronoun_q(x3,RSTR,BODY)          ┌────── _file_n_of(x8,i13)
                    └─ _a_q(x8,RSTR,BODY)
                                      └─ _delete_v_1(e2,x3,x8)
~~~

The raw solutions are these:
~~~
x3(VariableValueType.set)=(Actor(name=Computer, person=2),), x8(VariableValueType.set)=[File(name=/documents/file1.txt, size=1000)]
x3(VariableValueType.set)=(Actor(name=Computer, person=2),), x8(VariableValueType.set)=[File(name=/Desktop/file2.txt, size=10000000)]
x3(VariableValueType.set)=(Actor(name=Computer, person=2),), x8(VariableValueType.set)=[File(name=/Desktop/file3.txt, size=1000)]
~~~

### Which is special
All other items only look for one solution group.  Which wants them all

List of quantifiers:
  _a+bit_q : ARG0 x { NUM sg }, RSTR h, BODY h.
  _a+fourth_q : ARG0 x, RSTR h, BODY h.
  _a+further_q : ARG0 x { NUM pl }, RSTR h, BODY h.
  _a+great+many_q : ARG0 e, ARG1 x { NUM pl }.
  _a+little_q : ARG0 x { NUM sg }, RSTR h, BODY h.
  _a+third_q : ARG0 x, RSTR h, BODY h.
  _a+total_q : ARG0 x, RSTR h, BODY h.
  _a_q : ARG0 x { IND + }, RSTR h, BODY h.
  _all_q : ARG0 x, RSTR h, BODY h.
  _all_q : ARG0 x { IND + }, RSTR h, BODY h.
  _an+additional_q : ARG0 x { NUM pl }, RSTR h, BODY h.
  _an+average_q : ARG0 x, RSTR h, BODY h.
  _another_q : ARG0 x, RSTR h, BODY h.
  _another_q : ARG0 x { NUM pl }, RSTR h, BODY h.
  _any+more_q : ARG0 x, RSTR h, BODY h.
  _any_q : ARG0 x, RSTR h, BODY h.
  _any_q : ARG0 x { NUM sg }, RSTR h, BODY h.
  _both_q : ARG0 x { NUM pl }, RSTR h, BODY h.
  _both_q : ARG0 x, RSTR h, BODY h.
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
  _neither_q : ARG0 x { NUM pl }, RSTR h, BODY h.
  _no+more_q : ARG0 x, RSTR h, BODY h.
  _no_q : ARG0 x { NUM sg }, RSTR h, BODY h.
  _no_q : ARG0 x, RSTR h, BODY h.
  _not+all_q : ARG0 x, RSTR h, BODY h.
  _part_q : ARG0 x, RSTR h, BODY h.
  _q_a_colon : ARG0 i, ARG1 h.
  _some+more_q : ARG0 x, RSTR h, BODY h.
  _some_q : ARG0 x, RSTR h, BODY h.
  _some_q : ARG0 x { NUM sg }, RSTR h, BODY h.
  _some_q_indiv : ARG0 x, RSTR h, BODY h.
  _such+a_q : ARG0 x { IND + }, RSTR h, BODY h.
  _such_q : ARG0 x, RSTR h, BODY h.
  _that_q_dem : ARG0 x { GEND n, NUM sg }, RSTR h, BODY h.
  _that_q_dem : ARG0 x, RSTR h, BODY h.
  _the+least_q : ARG0 x, RSTR h, BODY h.
  _the+most_q : ARG0 x, RSTR h, BODY h.
  _the_q : ARG0 x, RSTR h, BODY h.
  _the_q : ARG0 x { NUM sg }, RSTR h, BODY h.
  _these_q_dem : ARG0 x { NUM pl }, RSTR h, BODY h.
  _this_q_dem : ARG0 x { GEND n, NUM sg }, RSTR h, BODY h.
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
  def_explicit_q : ARG0 x { NUM sg }, RSTR h, BODY h.
  def_implicit_q : ARG0 x, RSTR h, BODY h.
  def_implicit_q : ARG0 x { NUM sg }, RSTR h, BODY h.
  def_implicit_q : ARG0 x { NUM sg, IND + }, RSTR h, BODY h.
  def_implicit_q : ARG0 x { GEND n, NUM sg }, RSTR h, BODY h.
  def_or_demon_q : ARG0 x, RSTR h, BODY h.
  def_or_proper_q : ARG0 x, RSTR h, BODY h.
  def_or_udef_or_demon_q : ARG0 x, RSTR h, BODY h.
  def_or_udef_q : ARG0 x, RSTR h, BODY h.
  def_poss_or_barepl_or_prop_q : ARG0 x, RSTR h, BODY h.
  def_poss_q : ARG0 x, RSTR h, BODY h.
  def_poss_q : ARG0 x { NUM sg }, RSTR h, BODY h.
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
  free_relative_ever_q : ARG0 x { NUM sg }, RSTR h, BODY h.
  free_relative_ever_q : ARG0 x, RSTR h, BODY h.
  free_relative_q : ARG0 x { NUM sg }, RSTR h, BODY h.
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
  pronoun_q : ARG0 x { GEND m, NUM sg, IND + }, RSTR h, BODY h.
  pronoun_q : ARG0 x { GEND f, NUM sg, IND + }, RSTR h, BODY h.
  pronoun_q : ARG0 x { GEND m-or-f, NUM sg, IND + }, RSTR h, BODY h.
  pronoun_q : ARG0 x { GEND m-or-f, NUM sg }, RSTR h, BODY h.
  pronoun_q : ARG0 x { GEND f, NUM sg }, RSTR h, BODY h.
  pronoun_q : ARG0 x { GEND m, NUM sg }, RSTR h, BODY h.
  pronoun_q : ARG0 x { NUM sg, IND + }, RSTR h, BODY h.
  pronoun_q : ARG0 x { GEND n, NUM sg }, RSTR h, BODY h.
  pronoun_q : ARG0 x { NUM sg }, RSTR h, BODY h.
  pronoun_q : ARG0 x { GEND n, NUM sg, IND + }, RSTR h, BODY h.
  pronoun_q : ARG0 x { NUM pl }, RSTR h, BODY h.
  pronoun_q : ARG0 x { NUM pl, IND + }, RSTR h, BODY h.
  pronoun_q : ARG0 x { IND + }, RSTR h, BODY h.
  proper_q : ARG0 x, RSTR h, BODY h.
  some-any_q : ARG0 x, RSTR h, BODY h.
  some_q : ARG0 x, RSTR h, BODY h.
  udef_a_q : ARG0 x, RSTR h, BODY h.
  udef_or_proper_q : ARG0 x, RSTR h, BODY h.
  udef_q : ARG0 x, RSTR h, BODY h.
  udef_q : ARG0 x { NUM sg, IND + }, RSTR h, BODY h.
  udef_q : ARG0 x { NUM sg }, RSTR h, BODY h.
  udef_q : ARG0 x { NUM pl }, RSTR h, BODY h.
  udef_q : ARG0 x { IND + }, RSTR h, BODY h.
  universal_q : ARG0 x, RSTR h, BODY h.
  which_q : ARG0 x, RSTR h, BODY h.
  which_q : ARG0 x { NUM sg }, RSTR h, BODY h.