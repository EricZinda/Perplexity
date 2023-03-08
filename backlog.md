Remaining work to be shown in the tutorial:
- Make "only 2" work for cardinals
- Linking files says that the same file is in a folder twice under two names

- Need to implement a verb that handles coll differently like lift
- which 2 files total 5
-                                                ┌── _file_n_of(x5,i11)
                                   ┌────── and(0,1)
               ┌────── card(5,x14,i│0)           └ card(2,e10,x5)
number_q(x14,RSTR,BODY)            │
                    └─ udef_q(x5,RSTR,BODY)
                                        │      ┌── loc_nonsp(e13,e2,x14)
                                        └─ and(0,1)
                                                 └ _total_v_1(e2,x5,i12)

which 2 files total 5 megabytes
                         ┌── _megabyte_n_1(x11,u18)
             ┌────── and(0,1)
             │             └ card(5,e17,x11)
udef_q(x11,RSTR,BODY)
                  │                            ┌── _file_n_of(x3,i10)
                  │                ┌────── and(0,1)
                  │                │             └ card(2,e9,x3)
                  └─ _which_q(x3,RSTR,BODY)
                                        └─ _total_v_1(e2,x3,x11)

                                    ┌────── card(5,x17,i23)
             ┌────── number_q(x17,RSTR,BODY)    ┌── _megabyte_n_1(x11,u24)
             │                           └─ and(0,1)
             │                                    └ compound(e16,x11,x17)
udef_q(x11,RSTR,BODY)
                  │                            ┌── _file_n_of(x3,i10)
                  │                ┌────── and(0,1)
                  │                │             └ card(2,e9,x3)
                  └─ _which_q(x3,RSTR,BODY)
                                        └─ _total_v_1(e2,x3,x11)

START HERE NEXT maybe find: /findtree card(_,x,_)&total_v_1(e,x,_)&compound(e,x,x)
# Rewrite: quantifier_q(x, [cardinal(x, ...), cardinal_modifier()], body)
# To the form: [cardinal_modifier(), cardinal_with_scope(x, non_cardinal_rstr, base_quantifier_q(x, thing(x), body)]
# card_with_scope([_megabyte_n_1(x10,u18), _total_a_1(e15,x10)], udef_q(x10, body)

- Implement: which 2 files are 10 megabytes/which 2 files are 10 megabytes together
    - is it really necessary to implement loc_nonsp? maybejust _be_v_id is enough, because that seems required?
      - No, look at this

                           ┌── _megabyte_n_1(x11,u18)
               ┌────── and(0,1)
               │             └ card(10,e17,x11)
udef_q(x11,RSTR,BODY)                          ┌── _file_n_of(x3,i10)
                  │                ┌────── and(0,1)
                  │                │             └ card(2,e9,x3)
                  └─ _which_q(x3,RSTR,BODY)
                                        │      ┌── _together_p(e19,x3)
                                        └─ and(0,1)
                                                 └ loc_nonsp(e2,x3,x11)


- Implement: The size of 2 files is 10 megabytes
                         ┌── _megabyte_n_1(x16,u23)
             ┌────── and(0,1)
             │             └ card(10,e22,x16)
             │                                                   ┌── _file_n_of(x8,i15)
             │                                       ┌────── and(0,1)
             │                                       │             └ card(2,e14,x8)
udef_q(x16,RSTR,BODY)                                │
                  │              ┌────── udef_q(x8,RSTR,BODY)
                  │              │                        └─ _size_n_of(x3,x8)
                  └─ _the_q(x3,RSTR,BODY)
                                      └─ _be_v_id(e2,x3,x16)



- Do cumulative
 
  - what verbs are collective?
    - add up to
  - size
    -Design:
        - We should track whether a card is in dist or coll mode as a property on the variable, so that other things in the system can detect it
            - each cardinal sets its own variable property itself, its parent tells it what to set it to
              This allows any predicate in the tree to say that it mattered so it is kept
- 
      - We should not succeed for both dist and coll if the verb doesn't distinguish since they will be the same, we should only succeed for one
          - Thus there should be a default for verbs (dist since it is easier and more common) and we only call coll if it is specified
          - verb arguments can be named with x_set_blah if they want to handle a set
          - Need to determine which predicate to call dynamically by inspecting state since we switch dist/coll mode at runtime
          - does this mean that every predication between two cardinals has to properly handle sets?
              - No, we default predications to dist mode
        - Theory: if a predication doesn't care for an argument we should remove duplicates of it, so really folder/file should only have one set of answers
            So if used_collective is set, we should keep the answer. Otherwise we should remove it
            An alternative is that, if a predication is the index, it should fail if it doesn't handle the case
            
- 
  - Because the order of cards in the tree determines when a new set is chosen (the later ones choose a new set for every previous set that comes through) There could be legitimate different answers at the end even if the intermediate predications are they are the same for coll and dist. But the last predication just creates duplicates if the verb doesn't care
  - So, predications shouldn't fail if they are transparent (i.e. don't care) about coll or dist? but fail if they actually are wrong?
  - The problem is that we don't know which duplicates to remove since the last item comes back with dist and coll versions (even though they are the same), so they look different. We only know they are dups if we know the semantics of set are ignored
  - Any predicate along the way that takes the args could behave differently. So, we should tag a group as "processed as a group" if they were. Then, when we report answers, we can treat coll/dist groups as the same if they don't have this set
    - How is this indicated? Options:
      - (go this way) Set it on the variable.
        - Weird because it causes something like in_p_loc to have to create new state for an answer when there really wasn't new state
        - But it happens infrequently
      - Mark it on the predicate and automatically set it on the variable as a property up front
        - If a predicate says it consumes a variable and uses it as a set we could know that up front by just scanning the predications
          - But we won't know until runtime if that particular implementation was used!
  - THEN: We might be able to optimize by not trying the last cardinal in both coll and dist if nobody cares
    - Make in_p_loc handle coll mode
      - Only need to handle: inploc(either, dist) because
        - Two files together in the same folder is the same as two files separate in the same folder
          - Thus the left side can treat dist and coll as the same, it doesn't care
        - The same file in two different folders is the same as the same file in two folders together
          - Thus the right side can treat dist and coll as the same
        - the same two files in the same two folders
        - Key observation: maybe the right way to think about what a verb supports is using the term :"at the same time" and seeing if it changes the meaning
            - are these two files are in a folder *at the same time*? is the same as are each of them in the same folder? If so, nothing changes and it doesn't care
            - If it doesn't care, it needs to handle both (but it can just ignore whether they are coll or dist) because both are needed in order to get all the options, and then the cardinal can optimize away the last child to not get duplicates
              - If it *does* care it needs to mark itself as such. The only thing that will change is that we won't do the final child optimization to remove duplicates
                - Really we could do this by having it fail for the versions it doesn't handle?
        - So, inploc can simply check "in" for each thing that comes in and it will be correct
        - BUT: since it doesn't distinguish we shouldn't duplicate the alternatives that are the same
        - TODO:
          - have the final collector of answers remove duplicates when they exist
  - Thoughts:
    - If this is not a "men holding the table scenario", then there are only 4 different scenarios. You need to alternate the parent and keep the child the same, and it doesn't matter which you choose, coll or dist. 
    - if doing something *together* doesn't mean anything different than doing it the same, then we only need the four cases
      - Really you just make sure the final child only runs one case (either one)
    - In fact, if the verb is such that it doesn't distinguish the "men holding the table scenario" (as I suspect most are), then we should just do this automatically



Example: which two files are in 3 directories
1. 2card is in coll mode, group 1. It sets a property of the group to tell children to be in coll mode first. 3card detects the new group and starts in coll mode, group 2
    - 2card keeps calling the body with rstr values until its count is met
      - for as long as 2card sends group 1: For each new item that comes through, 3card ensures that all the items in its set apply to the new one
        - when success or fail, it stops the generator
2. 2card finishes (success or failure) its own coll mode. Now it does coll mode again but creates a new group with a property that tells its child to go into dist mode
    - 2card keeps calling the body with rstr values until its count is met
      - for as long as 2card sends group 1: For each new item that comes through, because it is dist mode, 3card ensures that all the items in its set apply to the new one
        - when success or fail, it stops the generator
        - The only difference between 1 and 2 is that the child sets a property of its variable to tell any downstream items what mode its variable is in.
3. 2card now returns
4. root calls 2card again, this time set to dist mode. It sets a property of the group to tell children to be in coll mode first. 3card detects the new group and starts in coll mode, group 2
   - 2card keeps calling the body with rstr values until its count is met, *but uses a different group each time*
     - for each group that 2card sends: For each new item that comes through, 3card ensures that all the items in its set apply to the new one
       - when success or fail, it stops the generator
       
