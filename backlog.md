Remaining work to be shown in the tutorial:
- Make bare plurals work
- Do some tricky quantifiers
- Make "only 2" work for cardinals
- Do cumulative
- Linking files says that the same file is in a folder twice under two names

- TODO: For collective, we actually run it N times even though the answer is the same.  Can we optimize?
- there are special case lists of predications in the card stuff, need this to be dynamic

- Do testing

- Doesn't work: which 2 files in this folder are 2 megabytes together (when none is)
  - should return a good error not "duplicate"
  - Is better now (but still bad): a 2 in file is not 2 together megabyte
  - /runparse 7,0
  -                                                                   ┌── _together_p(e26,x18)
                                                      ┌────── and(0,1)
                  ┌────── _folder_n_of(x12,i17)       │             └ _megabyte_n_1(x18,u25)
_this_q_dem(x12,RSTR,BODY)                            │
                       └─ card_with_scope(2,e24,x18,RSTR,BODY)                                                                    ┌── _in_p_loc(e11,x3,x12)
                                                           │                                                          ┌────── and(0,1)
                                                           │                        ┌────── thing(x18)                │             └ _file_n_of(x3,i10)
                                                           └─ udef_q_cardinal(x18,RSTR,BODY)                          │
                                                                                         └─ card_with_scope(2,e9,x3,RSTR,BODY)
                                                                                                                           │                         ┌────── thing(x3)
                                                                                                                           └─ _which_q_cardinal(x3,RSTR,BODY)
                                                                                                                                                          └─ loc_nonsp(e2,x3,x18)