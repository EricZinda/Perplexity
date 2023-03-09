Remaining work to be shown in the tutorial:
- Make "only 2" work for cardinals
- Linking files says that the same file is in a folder twice under two names

- Need to implement a verb that handles coll differently like lift
- TODO: For collective, we actually run it N times even though the answer is the same.  Can we optimize?

- Do testing
- (works) which 2 files are in this folder together
                                                    ┌── _file_n_of(x3,i10)
                                        ┌────── and(0,1)
                  ┌────── _folder_n_of(x│1,i16)       └ card(2,e9,x3)
_this_q_dem(x11,RSTR,BODY)              │
                       └─ _which_q(x3,RSTR,BODY)
                                             │      ┌── _together_p_state(e17,e2)
                                             └─ and(0,1)
                                                      └ _in_p_loc(e2,x3,x11)

Text Tree: _this_q_dem(x11,_folder_n_of(x11,i16),_which_q(x3,[_file_n_of(x3,i10), card(2,e9,x3)],[_together_p_state(e17,e2), _in_p_loc(e2,x3,x11)]))


                  ┌────── _folder_n_of(x11,i16)
_this_q_dem(x11,RSTR,BODY)                          ┌────── _file_n_of(x3,i10)
                       └─ card_with_scope(2,e9,x3,RSTR,BODY)                       ┌────── thing(x3)
                                                         └─ _which_q_cardinal(x3,RSTR,BODY)    ┌── _together_p_state(e17,e2)
                                                                                        └─ and(0,1)
                                                                                                 └ _in_p_loc(e2,x3,x11)
- together_p_state does't do all the combinations. Should it?
- All of the places where state.set_x() are used, lose the state that is set and make cardinals not work right. The values need to stick.
- loc_nonsp declaration applies to both "location" and "size".  Need different versions with different declarations
- 
- (fixed) fails: which 2 files are 10 megabytes together in Example30_reset
- (fixed) fails: delete 2 files in 2 folders together returns dist and coll options 
- (fixed) Doesn't work: which 2 files in this folder together are 2 megabytes
    - I think the problem is that together_p_state and together_p can set a variable to "collective only" *before* the cardinal of that variable runs
      - The cardinal needs to respect that
      - the together predications need to set it to used even if it isn't collective yet if it is plural

- (fixed) support card(c,e,x) in the body of a quantifier
- (fixed) Fails: which files in this folder are 2 megabytes together
  - Suspect that it is because terms in between a parent and the child retry and the child 
- Doens't work: which files in this folder are 2 megabytes together (when none is)
  - should return a good error
  - First problem: together, megabyte doesn't work
- Do cumulative
