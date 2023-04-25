Remaining work to be shown in the tutorial:
 
Plurals work

Future optimizations:
- Delete sets that can't work. Anything where one variable is at the upper limit can never work again since every add adds at least one item
- We really don't need to return *all combinations that are solutions*, just the *unique* solutions that meet the criteria, all the rest are just duplicates
  - Therefore:
    - Any criteria that has only (1, inf) (in any number) means: return all answers

- Figure out where the scaling problems are: where combinatorics are exploding
    - Example 33: which files are in a folder: logarithmically slow
      - files(1, inf), folder(1,1)
      - Each new row generates every combination of previous items
      - We don't need to generate all combinations at this point since we are really only trying to meet the numeric criteria
        - generating combinations that have already been seen is not useful since, with a wh-type question, we are looking for new, unique values
      - Maybe the generator should 
        - option 1
          - assume every row is going to have a new value?
          - optimize for returning new values faster
        - option 2
          - Only sets that meet all criteria will be returned
          - if the second criteria is (1, 1) then we know only single unique values of that variable will match
        - (seems key) option 3
          - Is it true that, as far as wh-questions, statements and commands go: 
            - we don't care about getting the right solution groups, only about the actual individuals? 
            - I.e. solution groups are an implementation detail
            - Which means that we should only return single solutions, one by one, if they go in a group that meets the criteria
            - Which means that how a question was modelled internally is a black box.  
              - It is certainly true that right now the *output* is not grouped in any way that would allow you to distinguish the cases
                - If it just so happens that the answers I give you come from a distributive *and* collective solution group you'll figure that out and ask a more specific question?
                - Or maybe it is that they need to be
          - there is no further grouping of files(1, inf) needed since:
            - we've already run the undetermined MRS, 
            - there is no reason to return different subsets of it unless they are needed for other criteria
            - i.e. we don't need *all possible* solutions at this point
          - maybe: treat each set that is created as the "maximal solution". i.e. use a greedy algorithm unless we prove another set is needed
            - as long as a single group still meets the criteria or is a contender, keep adding to it until it doesn't, and then form new groups
              - theory: if a set is a contender, we are done. Don't add more sets
          - maybe: we are building up the smallest set of solutions
            
- Do we really need to do all combinations of solutions?
    - Is there a better way?
      - Streaming algorithm
      - online algorithms
      - Integer programming: https://stackoverflow.com/questions/62622312/algorithm-to-find-some-rows-from-a-matrix-whose-sum-is-equal-to-a-given-row
      - Scenarios:
        - files are large: >1(x)
        - which file is large: =1(x)
        - 2 files are large: 2(x)
        - which 3 files are in 2 folders: 3(x), 2(y)
- Stream the undetermined solutions
  - Phase 2 requires AllRstrValues to be generated for things like "the" and maybe "all"
    - The entire MRS must be finished in the current model to get these
    - Instead, we could *maybe* generate them up front if needed
  - (fixed) Doing Phase 2 collective forces an entire group to be materialized
  - solution_list_alternatives_without_combinatorial_variables forces the entire group to be materialized
    - The only time we really do solution_group_combinatorial is for the first one
      - Should we break apart the distinction between  solution_group_combinatorial and variable?
3 students are eating 2 pizzas
    - the 2 pizzas can be the same, it just needs to be 2 against the same

- TODO: Still need to do combinatorial variables

Go through each plural    
- Test: 
        - https://aclanthology.org/P88-1003.pdf
        - https://aclanthology.org/W13-0202.pdf
    - when large() is applied to a set, it is unclear how to declare it. Figure this out later.
    - "which files are in folders" -> The problem is that it generates all combinations of 13 files and finds a ton of duplicate answers
        First attempt: just generate them all
        Later: optimize
        - which files are in a folder(): really does need to exhaust all the options
            files are in a folder(): does not
            So, we want to keep the ability to quickly check but also get the right answer when it is exhaustive

    - Figure out a way to make "in" be efficient for "which files are in folders"?
        - still slow for 1000 files, but now it appears to be all in phase 1 for that phrase
            - which 2 files are in a folder is that *plus* phase 2
        - Gets initial answers quickly but lags at end
            For phase 2 we generate all combinations of potential answers for the plural determiners
                Even when we stick to combinations of just distributive we have 2^n combinations
                (done) (good one) Don't build all the alternatives up front because we might only use one.  Stream them
                (good one) Optimization 2: Don't bother generating combinations that won't work for downstream determiners
                    "files are in 2 folders": We generate all combinations of N files, but there will at most 2 rows in the group at the end, so many are wasted
                    If we ignore the fact that collective exists, we could generate criteria based simply on counts and we will know it is *at most* that many rows
                    Key: Phase 2 is really about counting (or arbitrary criteria) on variable values
                        Should be able to somehow avoid generating whole classes of groups of solutions that can't work
                        It seems like we should be able to say "all groups where x13 < 2 and x15 > 1"
                        Constraint solver: https://mlabonne.github.io/blog/constraintprogramming/
                                           https://developers.google.com/optimization/cp/cp_solver
                        knapsack problem? https://developers.google.com/optimization/pack/multiple_knapsack
                        Should be easy to calculate a range of numbers that the rows must be in
                        For yes/no we only need to prove one answer, for wh we want to get the smallest set of answers?
                        This approach can stream
                (good one?) Optimization 4: Really we should allow it to stay combinatorial for the next determiner
                Use solvers to generate answers to knapsack problem
                (done) Optimization 1: If there are no more determiners, no need to do combinations, just return the smallest set of groups that meet the criteria
                Optimization 3: determiner_solution_groups_helper() is called by the determiner. It should be told the criteria so it only generates groups that match it?
                What is the goal? The goal is to return all groups of solutions that meet the criteria
                Scenario 1: files are in folders: files > 1, folders > 1
                Scenario 2: which 2 files are large? files = 2
                3: which folders have at most 3 files
            But then how does "boys ate pizza" work?
                Or boys ate 3 pizzas (where one group at 1 and the other group ate 2)
        - If we don't know what predications require (must have) and support (can have), they have to do all alternatives 
            in case downstream predications need those alternatives
            - If they are declared then we can optimize *some* cases
    - work through the tests and make them work in new regime 
    - Should remove duplicates before reporting answers
    - Really slow: Example28
        a few files are in a folder together
            Need to walk this through
        "4 files are in a folder"
        Returns an *enormous* number of items
            Are they all really legit?
        Start with "which files are in folders?"
            includes ones that are coll when it isn't used
            "in_p_loc" receives two combinatoric variables very quickly
            Then it tries every combination, returns pretty fast
                there are no duplicates, they are legit combinations
            solution_groups_helper() gets the list of solutions
            Really blows up on this line:                 for combination in itertools.combinations(variable_assignments, combination_size):
    Performance Ideas:
        Related to the Boolean Satisfiability Problem (SAT): Find an assignment to the propositional variables of the formula such that the formula evaluates to TRUE, or prove that no such assignment exists.
            SAT is an NP-complete decision problem
            - SAT was the first problem to be shown NP-complete.
            - There are no known polynomial time algorithms for SAT.
        https://link.springer.com/article/10.1007/s10601-016-9257-7
        Resolution: http://web.stanford.edu/class/linguist289/robinson65.pdf
        Tree is in Conjunctive Normal Form?
            https://haslab.github.io/MFES/2122/PL+SAT-handout.pdf
        Solving quantifiers in raw mode reduces them from a(x, b, c) to b, c
            SAT solvers based on a stochastic local search
            I the solver guesses a full assignment, and then, if the formula is
            evaluated to false under this assignment, starts to flip values of
            variables according to some heuristic.
            SAT solvers based on the DPLL framework
            I optimizations to the Davis-Putnam-Logemann-Loveland algorithm
            (DPLL) which corresponds to backtrack search through the space of
            possible variable assignments.
            DPLL-based SAT solvers, however, are considered better in most cases.


        What we are doing is not resolution because that involves axioms of the form a -> b:
            Research related to resolution: https://www.semanticscholar.org/paper/A-Machine-Oriented-Logic-Based-on-the-Resolution-Robinson/d2109eba4f160755f0b9a7497b6b691c2fa2d5d8
        We now do pass 1 without quantifiers.  Could we use SMT or Constraint logic programming or Answer Set Programming to solve that phase?
        We could stream answers from unquantified MRS to the solution groups
            I don't think this will work because we need to know all of the answers for "the", for example
        If nobody cares about sets, don't generate them
            What are the real terms for "don't care"
            each_q(x), every_q(x) forces distributive of x
            met(x) forces collective of x
            dance(x) could be anything (and means different things)
            in(x, y) could be anything (and means the same things)

            If we look at the size of actor and location, we can optimize and check differently
    - all 3 boys carried all 3
    - The girls told the boys two stories each
            The boys are building a raft each. (operator fixex)

    - "a file is a few megabytes" doesn't work
  
- copy x to y
  - needs copy with a scopal arg
    - We need to support turning a tree into something abstract that can be manipulated and understood
      - We could simply use the tree directly but then we'd have to special case all of the prepositions
      - Instead, we will create a special event that the scopal args get attached to
      - Then ask the tree to "interpret itself" in an abstract way that we have a chance of understanding
        - Some terms are actual things in the world and others are the way we want it to be
      - How?
        - We could run the predications using abductive logic?
        - We could "make a plan" to make X true
        - We could special case prepositions and just handle them
        - We could assume the scopal argument contains a particular thing (that depends on the predication it is in) and ask for that thing
          - i.e. copy assumes a locative preposition and looks for that
          - Can we find out what kinds of things "copy" can take as its scopal argument?
        - Theory: the verb with the scopal argument has an arg that is resolved in the scopal argument
          - Not true for make me be quieter, the argument comes from somewhere else
        - Theory:
          - The scopal argument determines some state change for the topic being verbed. The verb needs to collect this state change and then make it happen in the manner of verbing:
              - put the vase on the table: _put_v_1(e2,x3,x8,_on_p_loc(e15,x8,x16))
                - "put" means "move" so: put_v first makes a copy of x8, and then lets scopal "do what it does" to it
              - paint the tree green: _paint_v_1(e2,x3,x8,_green_a_2(e16,x8))
                - "paint" means "change it to" so it lets its arguments just do that
              - make me be quieter: _make_v_cause(e2,x3,(more_comp(e16,e15,u17), _quiet_a_1(e15,x10)))
                - Make is a special case
              - It would be *ideal* if this was just the same as abduction.  It isn't quite, since the verb (paint, copy) changes what happens:
                - paint the flower in the corner
                - copy the file in the folder
                - both use a scopal for _in_p_loc(e15,x8,x16) but what "in" does very different
                - effectively, "paint x in the corner" and "paint x blue" are very different operations meaning different paints
                  - so maybe the best approach is to build a different version of paint for each class of thing it can handle and treat it like a new argument
                  - reflect should copy data about itself into its event in a form that can be easily parsed
                  - How to find the right target in the scopal arg?
                    - Find all predications that use it as their ARG1?
                  - And then let "quoting" create a representation that puts them into "classes"
                    - "quoting" has to be special case code per predication because conversion into a canoncal form is per predication and not directly determinable from arguments. For example "copy the file above folderx" has above(folderx) but the copying should happen in the folder above it
  - also copy x in y (the same scenario)

- Support for prepositions
  - show declaring verbs that understand prepositions
- Theory: We don't need to choose different variations of the index of the phrase based on "comm", "ques", etc
  - Except: if we want to use abductive logic to make "The door is open" not evaluated as a question, but as a desire to make that true and then make it true in the system

