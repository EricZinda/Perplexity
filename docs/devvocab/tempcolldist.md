If we get through all the dist options (which will be the first cardinal_solution_id) for the top parent, we are guaranteed to have succeeded for the right number of all the children.

There are two functions that represent:
1. Setting things up for what the parent is doing
2. Doing the logic of this cardinal for children

# TODO: really test all of the examples here: https://sites.rutgers.edu/kristen-syrett/wp-content/uploads/sites/40/2018/09/Distributivity_Syrett.pdf
# Also this: https://www-users.york.ac.uk/~ez506/downloads/EGG_Plurals_2.pdf
# TODO: the toplevel mrs looper needs to respect retry
# Solved Issue: Two children ate two pizzas could mean: there is one child that ate one pizza and another child that ate another pizza
#        Two children ate three pizzas could mean: 1 child ate 2 pizzas and 2 children ate 1 of them
#           The problem with this one is that pizzas are shareable.
#       Both of these are the cumulative reading: https://www-users.york.ac.uk/~ez506/downloads/EGG_Plurals_2.pdf

# definitions:
# variable set: a group of values that are treated as a whole. The group has a unique variable_set_id
# variable set item: one element of a variable set
# variable_set_cache: programming language construct that allows children to store information in the parent variable set so it is there next time
# cardinal group: A cardinal has a group of variable sets that it deals with called a cardinal group. For coll, it is a list of one set of N, for dist it is a list of N sets of 1
#                   it is a group of pairs of variable_set_id/[list of values]
# cardinal group item: one of the sets in the cardinal group

# variable_set_restart exception: is a way for a child to restart the parent variable set if the child set didn't work 
# cardinal group generator: creates a new cardinal group (coll or dist).  Its scope is a parent variable set
# solution alternatives: For a given set, there might be more than one answer in the children. These are the alternatives

# The parent is either starting a new set or continuing a previous one or asking for a new value for a previous set
# cardinalid represents the set being bound to a variable. For dist, it is N sets of 1, each having different cardinalids.
# solutionid represents the set of sets. It is used at the very end to piece together the solutions
# group is used to mark the boundaries of the incoming set. It can have "NextSolution" set on it to tell the child to get a different solution for the same incoming set

# The logic for managing state that has to do with the parent_variable_set and matching it
# with a new or cached this_cardinal_group
def cardinal_variable_set_incoming(N):
    if new parent_variable_set or parent_variable_set_next_solution:
        if new parent_variable_set:
            create a new cardinal group generator that match coll or dist
        elif parent_variable_set_next_solution:
            use the existing generator
            set parent_variable_set_next_solution = False so we don't do it again
        Loop
            Get new this_cardinal_group from generator 
                solutions = cardinal_group_outgoing_solution(this_cardinal_group)
                if the whole this_cardinal_group didn't work, continue the loop to find one that does
                if it did work, cache this_cardinal_group and generator in parent_variable_set so it gets reused for the others in that variable_set

    else
        use the cached this_cardinal_group
        solutions = cardinal_outgoing_solution(this_cardinal_group)
        if the whole this_cardinal_group didn't work:
            Set parent_variable_set_next_solution = True in variable_set_group
            ask the parent to variable_set_restart so we can find a new set but where we left off in the combinator
        if it did work, cache the cardinal group

# Get all solutions for the entire this_cardinal_group
# The whole cardinal group must work or it fails
def cardinal_group_outgoing_solutions(this_cardinal_group):
    for each variable_set in this_cardinal_group:
        variable_set_solutions = []
        # Try the child in both coll and dist mode
        for is_child_coll in [False, True]:
            create a this_variable_set_cache to represent the variable_set
            answers = cardinal_outgoing_set(this_variable_set_cache, variable_set)
            variable_set_solutions.append(answers)
            if not has_children_cardinals:
                break
    
        if variable_set_solutions is empty (meaning no coll or dist solutions): 
            fail since all variable sets in a cardinal group must succeed for the cardinal to succeed
        else:
            cardinal_group_solutions.append(variable_set_solutions)
    
    return cardinal_group_solutions

# solve a particular outgoing variable_set. 
def cardinal_variable_set_outgoing_solutions(this_variable_set_cache, variable_set):
    There could be multiple solutions to this whole set
    variable_set_solution_alternatives = []
    this_variable_set_cache.nextsolution = true
    while this_variable_set_cache.nextsolution = true
        # child will reset that value of this_variable_set_cache.nextsolution to false
        variable_set_solutions = []
        for each item in variable_set:
            try:
                call with this_variable_set_cache
                collect the one answer that worked in body in variable_set_solutions
    
            catch variable_set_restart:
                a child asked us to retry which means a child had a variable_set that didn't completely work against this set
                So: the alternatives we have so far are right, but we need to restart the variable set (this keeps the same group to allow the child to cache things there)
                this_variable_set_cache.nextsolution = true
                break
            
            if no solutions, then fail because every element of the set must work
            variable_set_solutions.append(answers)
        
    
    if len(variable_set_solution_alternatives) > 0:
        return variable_set_solution_alternatives



This is a pipeline. Each node of the pipeline needs to find a set of N items that are true in the body for all of the set of M incoming items
    Assume that the incoming is *always* a set, it may just be of one item, N = 1
    If incoming item is the first in its set, start a new set
if a node is coll it needs to make sure that all N items work for the *same* body
    The same N items have to be used for all M items coming it since we are working iteratively
    If they don't all work, we need to get the next combination
        - Every time we change the combination, we need to recheck the whole set
        - Algorithm for all combinations (assuming order doesn't matter):
            - Keep an array that represents the list of all answers
            - have a generator
    If a predication like "in" wants to handle the whole set as a group, it has to succeed (and collect) items until the last comes in, and then succeed or fail.

# The only state we need to keep for cardinal, outside of when it is checking a set,
# is the current successful set, and the combinator
def cardinal(N):
    # If we are coll, our set is N, otherwise, our set is 1
    # If we have a set:
    #   if findNPrevious(previous_set):
    #       still works! Succeed
    #   else:
    #       ask parent to retry its set from the beginning
    #       set our set to None so we find a new one
    #  else:
    #       if findNNew(combinator):
    #           We found a set that works for this item
    #           set our set to this one
    #       else:
    #           No set works for this item, fail

# See if this set still works 
def findNPrevious(previous_set):
    # See if it works in the body
    #   if the child asks for a restart, just try again from the beginning
    # if not fail

# Find the next set that works
def findNNew(combinator):
    # Until we find a set that works:
    #   Generate a set from the combinator
    #   now we have the outgoing set
    #       See if it works in the body
    #           if the child asks for a restart, just try again from the beginning
    #       If it does, then return this set as a solution
    # fail

if a node is dist, each of N items is a set that work for the body
    If one doesn't, just need to throw away that set
From the cardinal's perspective, they are just building up sets of N
    It is the other predications that have to do something interesting with the "men lifting table"
Questions:
    - how to you get coll(N) lifting coll(M)?

Each solution is a list of solution elements. The number of solution elements can be very different for dist and coll combos.
    Each solution element is a list of variable assignments to sets. The sets can be a coll set of N or a dist set of 1
    Restarting algorithm:
        - If the card is collective, it remembers which items worked so far.
        - If new state comes in for which the new values don't work we need to try again, keeping the ones that did, but substituting new ones
            from the saved rstr. 
            - If there are any that did work: Throw an exception to get the parent to restart using its same values so we can retry an alternative for the ones that didn't work
            - If we hit the end of the rstr without getting a full set: ask the parent to pick a different set
                - The different parent set should not include any in the set that it had before since they didn't work
        - SO: there are two things that need to be communicated: fail and retry.  fail can just be normal iterator fail, and retry can be an exception

A cardinal solution id:
    - contains either a single coll set or a list of separate dist sets (of 1).
    
Algorithm:
- answers with the same cardinal_id have to be together
- answers with the same cardinal_id AND cardinal_item_id are the same answer
- If a child is Coll, then the previous same answers get grouped into one solution element
- Go from childmost to parentmost
  - if the child is coll, group all of the cardinal_ids for it into a single answer and walk each parent of that answer
    - If the parent is coll group all the cardinal_ids for it into a single answer that includes the child
    - if the parent is dist, copy the previous answer into each one
  - if the child is dist, create a solution element for each item in the solution id

    - Every unique combination of solutionIDs for all variables constitutes a solution
    - Necessary: the top parent must have the same groupids for the answers to be in the same solution group
    - If all solutions (dist and coll) for all cardinals succeeded then there would be a dist and coll at each level
      - It acts like a binary number
      - all answers that have the same number go together
      - 
Solution: x11#2(0:1:17->0)[dist] = Folder(name=/Desktop, size=10000000), x3#8(0:1:17:20->0)[dist] = File(name=/Desktop/Desktop1.txt, size=10000000)
Solution: x11#2(0:1:17->0)[dist] = Folder(name=/Desktop, size=10000000), x3#8(0:1:17:21->1)[dist] = File(name=/Desktop/Desktop2.txt, size=1000)
Solution: x11#2(0:1:22->1)[dist] = Folder(name=/temp, size=0), x3#10(0:1:22:27->0)[dist] = File(name=/temp/temp1.txt, size=10000000)
Solution: x11#2(0:1:22->1)[dist] = Folder(name=/temp, size=0), x3#10(0:1:22:28->1)[dist] = File(name=/temp/temp2.txt, size=1000)
Solution: x11#11(0:1:30->0)[dist] = Folder(name=/Desktop, size=10000000), x3#13(0:1:30:31->0)[coll] = File(name=/Desktop/Desktop1.txt, size=10000000)
Solution: x11#11(0:1:30->0)[dist] = Folder(name=/Desktop, size=10000000), x3#13(0:1:30:31->1)[coll] = File(name=/Desktop/Desktop2.txt, size=1000)
Solution: x11#11(0:1:32->1)[dist] = Folder(name=/temp, size=0), x3#15(0:1:32:33->0)[coll] = File(name=/temp/temp1.txt, size=10000000)
Solution: x11#11(0:1:32->1)[dist] = Folder(name=/temp, size=0), x3#15(0:1:32:33->1)[coll] = File(name=/temp/temp2.txt, size=1000)

Solution
    solutionelement(0:1:17->0, 0:1:17:20->0)
    solutionelement(0:1:17->0, 0:1:17:21->1)
    solutionelement(0:1:22->1, 0:1:22:27->0)
    solutionelement(0:1:22->1, 0:1:22:28->1)

Solution
    solutionelement(0:1:30->0, [0:1:30:31->0, 0:1:30:31->1])
    solutionelement(0:1:32->1, [0:1:32:33->0, 0:1:32:33->1])


Fro code:
[[x11#2(1:17->0)[dist]=Folder(name=/Desktop, size=10000000)], [x3#8(1:17:20->0)[dist]=File(name=/Desktop/Desktop1.txt, size=10000000)]]
[[x11#2(1:17->0)[dist]=Folder(name=/Desktop, size=10000000)], [x3#8(1:17:21->1)[dist]=File(name=/Desktop/Desktop2.txt, size=1000)]]
[[x11#2(1:22->1)[dist]=Folder(name=/temp, size=0)], [x3#10(1:22:27->0)[dist]=File(name=/temp/temp1.txt, size=10000000)]]
[[x11#2(1:22->1)[dist]=Folder(name=/temp, size=0)], [x3#10(1:22:28->1)[dist]=File(name=/temp/temp2.txt, size=1000)]]
[[x11#11(1:30->0)[dist]=Folder(name=/Desktop, size=10000000)], [x3#13(1:30:31->0)[coll]=File(name=/Desktop/Desktop1.txt, size=10000000), x3#13(1:30:31->1)[coll]=File(name=/Desktop/Desktop2.txt, size=1000)]]
[[x11#11(1:32->1)[dist]=Folder(name=/temp, size=0)], [x3#15(1:32:33->0)[coll]=File(name=/temp/temp1.txt, size=10000000), x3#15(1:32:33->1)[coll]=File(name=/temp/temp2.txt, size=1000)]]