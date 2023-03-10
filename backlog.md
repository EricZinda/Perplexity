Remaining work to be shown in the tutorial:
- Make bare plurals work
- Do some tricky quantifiers
- Make "only 2" work for cardinals
- Do cumulative
- Linking files says that the same file is in a folder twice under two names

- Make sure we can implement various quantifiers with cardinals
- there are special case lists of predications in the card stuff, need this to be dynamic
- Implement separately
- delete 1 file in this folder, deletes 2
  - Treats it as "delete all 1 files that are in this folder"
  - Similar to the problem of "which 2 files are in this folder" -- if there are 3, you'll get many answers, should be one
  - Should have to add "what are all the sets of 2 files in this folder"
- Better error for: which 2 files in this folder are 2 megabytes together (when none is)
  - Is better now (but still bad): a 2 in file is not 2 together megabyte
- TODO: For collective, we actually run it N times even though the answer is the same.  Can we optimize?

- Do testing
"together, which 3 files are 3 mb" - doesn't work because it is together_p(e4,e2), loc_nonsp(e2,x6,x13)