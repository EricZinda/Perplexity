Remaining work to be shown in the tutorial:
- CardinalID is not changing for each new set in dist
  - Because it is set by the parent in the group, and the group represents the parent solution
- (fixed) coll dist reuses the same item on dist and they should start from the beginning
  - If an existing cardinal_id comes in, we go into coll mode and only test the existing values.
    - coll/dist should see if the set of coll is true for each item in dist coll(folder), dist(file) means: a file is in both folders, a different file is in both folders
    - It is succeeding but then failing at the end
- (fixed) PredicateID is wrong now on retry
  - raise() doesn't undo the stack properly
- (fixed) We've lost the lineage for cardinal_ids
- (fixed) We aren't using the right cardinal_item_id for dist: they are the same
- (fixed) Answers from dist/dist don't return both children
- (fixed) Issue: When both in dist mode, you get the same parent for everything
    - First issue: parent thinks things succeeded if only one parent worked
      - It seems like failing to return more than one answer for a given set combination is being treated as failure

- (fixed) When grouping answers because we only group by the childmost, we don't properly get the parent coll, we only get one of them

- (fixed) When a set is checked with a child, it needs to be checked against *one set* from the child completely before the child returns more
    The parent should loop over its subset until there are no more solutions
    The child should stick to one answer set until the parent creates a new group
    The group holds the combinator, so it needs to be passed again to the child for a new solution
        But the parent needs a way to indicate that it should pick a new solutionid

- (fixed) When the parent is in coll mode and the child is in dist
  - When we go back to the rstr to get new values, it is bound to a previous value for the parent

- (fixed) When the parent is in coll mode and we are in coll mode
  - When we go back to the rstr to get new values, it is bound to a previous value for the parent
    - need to only use the bound value from the rstr.  Assume it is just iterating through unfiltered stuff that doesn't depend on the current state
    
- (fixed) Issue: if a two cardinal phrase are both in coll mode you should get the same child coll for the one set of parent coll
  - (fixed) We are finding a new alternative but not throwing the exception
  - (fixed) We are not using the same solutionid for coll in the child


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
- (done) (bug) Don't try coll and dist for children if there are no children. This is never right.
- DO THIS NEXT: We have a way to group *sets* but not *solutions*. Sets for a variable are the cardinal_id. But *solutions* are something else.
  - BUG: We aren't reusing the same solutionID if the parent is in coll mode, we are creating a new one.  Might be OK depending on the algorithm
  - each cardinal will do whichever it is told (coll or dist) and then ask its children to do both. how do these get separated?
    - How do you tell when the set (which includes all of the dist items) is done?
      - It isn't by set because dist cause a different set for each item
      - You could say it is when the items roll back to 0
      - For each card node, it alternates its children between dist and coll. Call those 0 and 1
        - Some branches won't exist
        - The answers are every unique combination of cardinal nodes (not plural variables since "1 file" will make a cardinal) like 00, 01
          - Does this depend on the order that answers come back? Don't think so since we can group the answers using cardinalID
- Because the order of card determines when a new set is chosen (the later ones choose a new set for every previous set that comes through) There could be legitimate different answers for all predications even if they are the same for coll and dist. But the last predication just creates duplicates if the verb doesn't care
  - WRONG:We could solve the duplication problem by simply removing duplications before reporting out answers. As long as we pay attention to sets this should be correct.
    - The problem is that we don't know which duplicates to remove since the last item comes back with dist and coll versions (even though they are the same), so they look different. We only know they are dups if we know the semantics of set are ignored
    - Any predicate along the way that takes the args could behave differently. So, we should tag a group as "processed as a group" if they were. Then, when we report answers, we can treat coll/dist groups as the same if they don't have this set
      - How is this indicated? Options:
        - Set it on the variable.
          - Weird because it causes something like in_p_loc to have to create new state for an answer when there really wasn't new state
          - But it happens infrequently
        - Mark it on the predicate and automatically set it on the variable as a property up front
          - If a predicate says it consumes a variable and uses it as a set we could know that up front by just scanning the predications
            - But we won't know until runtime if that particular implementation was used!
  - THEN: We might be able to optimize by not trying the last cardinal in both coll and dist if nobody cares

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
              - If it *does* care it needs to mark itself as such. The only thing that will change is that we won't do the final child optimization to remove duplicates
              - Really we could do this by having it fail for the versions it doesn't handle?
        - So, inploc can simply check "in" for each thing that comes in and it will be correct
        - BUT: since it doesn't distinguish we shouldn't duplicate the alternatives that are the same
        - TODO:
          - have the final collector of answers remove duplicates when they exist

definitions:
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

  - Thoughts:
    - The order of dist, coll or coll, dist matters because the first has scope over the second.  the second gets to rechoose
      - (this is right) It is only the *last* cardinal that can be the same because there is nothing after it that gets to "rechoose"
      - which means it is correct for the second to last parent to not try alternatives in the child
        - But it is *not* correct to skip that step if the verb cares
    - If this is not a "men holding the table scenario", then there are only 4 different scenarios. You need to alternate the parent and keep the child the same, and it doesn't matter which you choose, coll or dist. 
    - if doing something *together* doesn't mean anything different than doing it the same, then we only need the four cases
      - Really you just make sure the final child only runs one case (either one)
    - In fact, if the verb is such that it doesn't distinguish the "men holding the table scenario" (as I suspect most are), then we should just do this automatically
    
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
    
