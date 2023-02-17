Remaining work to be shown in the tutorial:



Respecting Plurals
- (done) Answers need to be marked so the sets can be returned
  - The ultimate result should be variables with sets in them. 
    - 5 children eating the same 5 pizzas: x5=[child1, ...], x6=[pizza1, ...]
      - each child eating a different 5: x5=[child1], x6=[pizza1, ....]
      - Could be as simple as marking each solution with the set ID it is a part of
        - Then, whatever reports out the answers has to look and see which variables are a set
          - Each group has an ID that is ParentID+ChildID
          - Each binding has a place to store the ID
          - When reporting out the answer to a variable that is plural, group the parent+child ids
      - Also need to return which *element* of a set an item is so it won't be repeated in the answer
- (done) collective mode matters even if there is one cardinal. For example: the men lifted the table could be one after the other or together
  - (done) So, something needs to create the top level group and switch it between the modes
- Make in_p_loc handle coll mode
  - Only need to handle: inploc(either, dist) because
    - Two files together in the same folder is the same as two files separate in the same folder
      - Thus the left side can treat dist and coll as the same
    - the same file in two different folders is the same as the same file in two folders together
      - Thus the right side can treat dist and coll as the same
    - the same two files in the same two folders
    - Key observation: maybe the right way to think about what a verb supports is using the term :"at the same time" and seeing if it changes the meaning
        - are these two files are in a folder *at the same time*? is the same as are each of them in the same folder
        - If it doesn't care, it needs to handle both (but it can just ignore whether they are coll or dist) because both are needed in order to get all the options, and then the cardinal can optimize away the last child to not get duplicates
          - If it *does* care it needs to mark itself as such. The only thing that will change is that we won't do the final child optimization.
          - 
    - So, inploc can simply check "in" for each thing that comes in and it will be correct
    - BUT: since it doesn't distinguish we shouldn't duplicate the alternatives that are the same

definitions:
  - file(dist), fold(dist): file1 in fold1 & fold2, file2 in fold3 & fold4
  - file(coll), fold(dist): file1 & file2 in fold1 & fold2
  - fold(dist), file(dist): fold1 contains file1 & file2, fold2 contains file3 and file4
  - fold(coll), fold(dist): fold1 & fold2 contain file1 & file2

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

  - Thoughts:
    - The order of dist, coll or coll, dist matters because the first has scope over the second.  the second gets to rechoose
      - (this is right) It is only the *last* cardinal that can be the same because there is nothing after it that gets to "rechoose"
      - which means it is correct for the second to last parent to not try alternatives in the child
        - TODO But it is *not* correct to skip that step if the verb cares
    - If this is not a "men holding the table scenario", then there are only 4 different scenarios. You need to alternate the parent and keep the child the same, and it doesn't matter which you choose, coll or dist. This means that in_p_loc needs to handle both alternatives of the first arg, and only 1 of the second. 
    - if doing something *together* doesn't mean anything different than doing it the same, then we only need the four cases
      - Really you just make sure the final child only runs one case (either one)
    - In fact, if the verb is such that it doesn't distinguish the "men holding the table scenario" (as I suspect most are), then we should just do this automatically
    - Wrong: It feels like the only one we should do automatically is dist/dist

- 
- 
    - for the parent cardinal, if this cardinal is in:
        - collective mode: call children with a group that will include all N items in this set
        - distributive mode: call children with N different groups that each include 1 item from the set
        - Both modes are run twice, telling its child to operate in coll and dist modes
    - for the child cardinal, if this cardinal is in:
        - collective mode: find a set of N that must apply collectively to the entire set coming in. A new set of N is chosen for each new set that comes in
        - distributive mode: find N different items that must apply individually to the set coming in. N different items are chosen for each new set that comes in
            - really, this just looks like collective with N set to 1


Design:
    - Key observations:
        - For a child: each cardinal is finding a set and applying it to a parent set. The difference between coll and dist mode is whether its set applies to the parent set *as a group* or *individually*
        - We should track whether a card is in dist or coll mode as a property on the variable, so that other things in the system can detect it
            - each cardinal sets its own variable property itself, its parent tells it what to set it to
        - We should only try coll and dist for children IF there is a child, otherwise it just duplicates values
        - We should not succeed for both dist and coll if the verb doesn't distinguish since they will be the same, we should only succeed for one
            - Thus there should be a default for verbs (dist since it is easier and more common) and we only call coll if it is specified
            - verb arguments can be named with x_set_blah if they want to handle a set
            - Need to determine which predicate to call dynamically by inspecting state since we switch dist/coll mode at runtime
            - does this mean that every predication between two cardinals has to properly handle sets?
                - No, we default predications to dist mode
            
- parent:
        - if coll, group covers all N
        - if dist, group covers each 1 of N
    - child
        - there are two pieces of information the child needs to know:
            - whether items coming in are part of a set and when the set is done
                - this is done by the parent setting a group
            - how to manage its own set it is processing against the parent set
                - it always collects a set of N, the only difference is whether they apply as a unit or separately
        - remembers what N items must apply to the set coming in
        - processes them against all items in the set
        - how does it know when the parent set is done? 
            - When the group changes. 
    - verb: lifted
        - needs to know if its variables are dist or coll
            - each variable is only in one mode

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


How to detect the boundaries of the different solutions?
  - Answer: each card sets a group property that says whether its child should be in coll or dist mode
  - The first cardinal creates a group which indicates it is sending a set through the system iteratively
    - the next child cardinal needs to only return answers for that set
    - the child cardinal needs to remember any state *alternative* (coll or dist) it is doing and stay in that mode 
    until the parent starts a new set
  - Design: A cardinal always has a current group that is available to it, even if it is the first one (the scope is created by the system)
    - The group tells it whether it is in coll or dist mode
    - the cardinal operates in that mode and when done it finishes its generator
    - its parent will create a new group when it is time to try the next mode
    
