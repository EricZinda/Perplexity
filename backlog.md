Remaining work to be shown in the tutorial:
- Make bare plurals work
- Do some tricky quantifiers
- Make "only 2" work for cardinals
- Do cumulative
- Linking files says that the same file is in a folder twice under two names

- TODO: For collective, we actually run it N times even though the answer is the same.  Can we optimize?


- All of the places where state.set_x() are used, lose the state that is set and make cardinals not work right. The values need to stick.
- loc_nonsp declaration applies to both "location" and "size".  Need different versions with different declarations
- there are special case lists of predications in the card stuff, need this to be dynamic

- Do testing

- Doesn't work: which files in this folder are 2 megabytes together (when none is)
  - should return a good error
  - First problem: together, megabyte doesn't work
