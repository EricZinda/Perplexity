## Appendix: Optimizing the Solution Group Algorithm
[This is an appendix because it doesn't change the overall concepts you need to understand to use the system, it just walks through one architecture for how to implement them.]

In the section [introducing the solution grouping algorithm](devhowtoMRSSolverSolutionGroupsAlgorithm), the algorithm starts with:

> For each possible combination of solutions from Phase 1 ...

And leaves how to generate them as an exercise for the reader. In this section, we'll go through one approach to generating combinations of solutions that properly deals with the kinds of answers users expect and allows for some performance optimizations.


## Only 2 Solution Groups Are Needed
The number of solution groups for a tree in a given world can be quite large, but the system only needs 2 of them for any response (question, proposition or command). This allows for some nice performance optimizations. Let's go through each type of phrase to see why.

### WH-Questions
"WH-Questions" are "which/who/what/where" questions that expect a list as a response. Let's use this tree from the phase "which 2 files are in a folder?":

~~~
                          ┌── _file_n_of(x3,i10)
              ┌────── and(0,1)
              │             └ card(2,e9,x3)
_which_q(x3,RSTR,BODY)
                   │             ┌────── _folder_n_of(x11,i16)
                   └─ _a_q(x11,RSTR,BODY)
                                      └─ _in_p_loc(e2,x3,x11)
~~~

... in this world:

~~~
\desktop\file1.txt
\desktop\file2.txt
\system\file3.txt
\system\file4.txt
~~~

Some solution groups for this are:

~~~
Group:
  \desktop\file1.txt
  \desktop\file2.txt

Group:
  \system\file3.txt
  \system\file4.txt
  
Group:
  \desktop\file1.txt
  \system\file3.txt

Group:
  \desktop\file1.txt
  \system\file4.txt

Group:
  \desktop\file1.txt
  \system\file4.txt
  
etc., there are more ...
~~~

How many of these solution groups does the system need in order to respond? 1 of them? all of them? If we want the system to respond in the way a user expects, we need to observe the way a human would respond. 

Here are some typical responses a human might make when asked questions about the world above:

~~~
Lin: Which 2 files are in a folder?
Mila: Umm...there are more than 2 files in a folder ... which do you mean?
~~~

~~~
Irene: Which 2 files are in a folder?
Hana: Actually, there are a bunch of files in a folder, 2 of of them are: file1.txt and file2.txt
~~~

~~~
Juan: Which 2 files are in a folder?
Carlos: Well, lets see: file1.txt and file2.txt are in \desktop, file3.txt and file4.txt are in \documents, ...
~~~

The first two explicitly or implicitly acknowledge that the question is implying there are *only* 2 files in a folder, but the participants are willing to respond to a phrase the user didn't ask, giving them the benefit of the doubt. The last one interprets the phrase more broadly as something like "what are all the sets of 2 files in a folder".  Carlos is probably a puzzle or math guy and thought it was a trick question.

Another example: In a physics class of 20 students, where only one student got 100%, the professor is asked, "Which students aced the exam?" and responds with "Only Mariam." Note that the question had "students" (plural) and the professor felt the need to say "only" to indicate that they weren't really answering the question asked since they responded in singular. Saying simply "Mariam" feels *slightly* wrong, but note that if 2 students aced it, saying "Mariam and Aron" would be just fine and not feel wrong at all. So, something is being acknowledged in the one student case.

So, building a system that is completely literal and responds to "Which 2 files are in a folder?" with "There are more than only 2 files in a folder." (Mila's response above), might be correct but will be annoying.  The Carlos answer is the most complete and generous, but could result in a huge (possibly expensive) answer when the user, who also understands that the question implicitly means "only", probably misunderstood the world state. Hana's answer is a good middle ground that gives an answer "just in case", but acknowledges that the question was probably a misunderstanding of the world state. Hers also doesn't overload the questioner with a huge number of answers.

This implies that, for WH-questions (where, what, who, etc), we need to get one answer to respond and see if there is another to let the questioner know there are more. We need 2 answers.

### Yes/No Questions
What about (using the same examples from above): "Are there 2 files in a folder?" or "Did students ace the exam"? These act the same as WH-questions:

- Responding to "Are there 2 files in a folder?" with "Yes." is *technically* true for the above example, but would probably be considered a little misleading. So the answerer might respond with something like "*Technically* yes, but there are more."
- Responding to "Did students ace the exam?" with "Yes." would cause most people to be mildly annoyed later if they find out there was only one. 

This implies that, for Yes/No questions, we need to get one answer to respond and test if there is another answer to let the questioner know there are more. So, we also need 2 answers.

### Propositions
Continuing with our example, this time as a proposition: "2 files are in a folder" or "students aced the exam". These act just like Yes/No questions: The first is "technically true" the second is just wrong. So: 2 answers required.

### Commands
What should "delete 2 files in a folder" do? Deleting all examples of "2 files in a folder" feels wrong. There seems to be an implied "one instance of" after delete. A clearer example might be "delete a file in a folder". There are 4 examples (solution groups) of "a file in a folder" in the world in question, but deleting them all due to that phrase would be certainly wrong.

So, if we decide that we should only pick one of the solution groups to act on for commands, it should be noted that deleting "2 files" or "a file" when there is more than one solution group feels a bit random. For this example, a human might ask, "Do you mean a *random* 2 files?". Certainly saying, "delete files in a folder", if there is only 1 file, feels wrong, just like "Talk to the students that aced the exam" when there is only one student feels wrong.  Either would probably get a response like "OK, but there is only one" to communicate that the listener isn't going to do *exactly* what was commanded.

All this is to say that, again, commands should also retrieve 2 solution groups. The first is what will be "done", the second is to see if some kind of clarifying response should be given.

So, to summarize, we only need to return 2 solution groups in the algorithm we develop, across all types of phrases. This will give us some room for performance optimization.


## Maximal, Minimal, and Subset Solution Groups
Based on the above analysis, we're going to need to retrieve two solution groups (if they exist) when processing any user phrase and show the user (or do) the first group. The second group is just tested to see if it exists and then say "there are more answers here..." in some form.

The problem is: as we've seen in previous sections, there can be many correct solution groups for a given answer which aren't "maximal".  To see what "maximal" means, take: "which files are in a folder?" when there are these files in a folder:

~~~
/folder/file1.txt
/folder/file2.txt
/folder/file3.txt
/folder/file4.txt
~~~

... one *technically* correct answer is:

~~~
/folder/file1.txt
/folder/file2.txt
~~~

... another *technically* correct answer is:

~~~
/folder/file1.txt
/folder/file2.txt
/folder/file3.txt
~~~

etc. 

Basically, any combination of files in a folder is a "technically correct" answer so long as it is > 1 (due to plural "files"). While it is technically correct, if you asked a person, "which files are in a folder" and they gave you one of those answers, you might be a bit annoyed and clarify with "can you give me the whole list?"  Let's call these "subset solution groups".

So, since we are only going to return one solution group, we really want to return the *maximal* solution group, the one where no more solutions can be added to the group while still keeping it a valid group. Keeping it a valid group means *all* solutions in the group conform to at least one type of answer (collective, distributive or cumulative). It is OK if they *all* conform to more than one, however.

In general, subset solution groups can be generated any time a criteria for a variable has a range of values that can be true. When the solution group is at the bottom of the range for that variable it is a "minimal" solution, at the top is a "maximal" solution, anything in between is a "subset" solution. 

Two examples:

- Even one plural variable in an MRS can potentially generate multiple subset groups.  For example: "men are walking" (when talking about a specific group of men). The entire group of "men" can be represented in one solution group, so you'd just expect one group in answer to, "Which men are walking?". But: subsets of that group would also be true, so other solution groups are also technically correct.
- With two variables: "men(x) are walking a dog(y)" (when talking about one group of men walking a particular dog) you'd still only expect one solution group in answer to "Which men are walking a dog?": the "maximal" solution. But again, subsets would be technically true, just not really telling the whole story.


All this is to say: if you're only going to give one answer (which we are), it should be a maximal one. To make the system responsive, though, it should start returning an answer as soon as one meets the constraints (i.e. when we have a "minimal" answer), but then keep returning answers as the set gets enlarged. That way, the user can see answers as they come.

To sum up:
- Since we are only going to show the user one solution group, it should be a maximal group
- It should get returned iteratively, starting as soon as there is a minimal group that meets its constraints, but the entire maximal group should be ultimately returned
- The complete solution group shown should meet the rules for one of the three types (collective, distributive or cumulative)

Based on this, it is worth defining a few terms that we can use as we walk through more scenarios:
- a **"minimal solution group"** is one where the constraints meet the minimum required to be a solution group. Since adding a new solution only ever increases variable counts (since variables always have at least one individual), the first solution group that meets the criteria will always be minimal (it may also be maximal!)
- a **"maximal solution group"** is one where no more solutions can be added to the solution group and still have it a) meet the criteria and b) have all solutions be contributing to a single mode. This could be because all the criteria are at their maximum, or it could be because there are no more solutions to add.
- a **"subset solution group"** is anything that isn't maximal but is still a solution. It is a "subset" of some maximal solution group in that all of its rows are completely included in that other group.
- a **"unique solution group"** is one that isn't a subset of another solution group. It has at least one solution that is not in any other.

We'll use these terms as we develop the algorithm below.

It is important to note that these terms are all invented for this algorithm. They (or even the notion of "solution group") are not DELPH-IN or even linguistic terms.  They are artifacts of the particular approach being used to solve MRS trees.

## Algorithm Version 1
This will form the skeleton of the algorithm we're going to eventually settle on. It is a general purpose algorithm that creates all combinations of items in a set:

1. Start with a list of sets: `set_list`, which initially contains a single empty set. 

2. When a new solution is found, for each `selected_set` in `set_list`:
- Build a `new_set` by adding the solution to `selected_set` 
- If `new_set` meets or could eventually meet the criteria (once more rows are added), add it to `set_list`
- If `new_set` actually *did* meet the criteria, also return it as a solution group
 
This algorithm works because each set in `set_list` becomes a base for creating new combinations when a new solution comes in. And, when that new alternative is created, it also gets added to `set_list` so it can also form new combinations. In this way, we generate all possible combinations.

This algorithm for creating all possible combinations has a very useful property: it doesn't require knowing the length of the flat list of solutions coming in, and it builds combinations out of the items it already has before retrieving another solution. This means it will allow us to efficiently stream solutions to it without having to calculate them all up front, which could be very expensive.  

This is not the final algorithm because, while it will produce all combinations that meet the criteria, it also produces the problematic "subset" or "minimal" solutions that we described above. But, it will form a good skeleton for an algorithm we can use with modifications.

## Algorithm Version 2
We need 3 things from the final algorithm:

- **(for all cases) Retrieve a minimal solution group as quickly as possible**. For yes/no questions and propositions, we just need to prove there is one solution, so a minimal solution is enough to create the initial answer. For wh-questions and commands, we want to start showing the answers as soon as we have them for responsiveness.  So, in all cases, we don't care if it is maximal for the initial response, we just want it quickly.
- **(for WH-questions and commands) We want to stream the rest of the solutions until there is a maximal group**. This is so we respond to the user or do the command with a full answer (as described above). After receiving the minimal solution group, we'd like to continue getting additional solutions that belong in that solution group as they become available, until we have the maximal solution group. 
- **(for all cases) Detect if there is more than one unique solution group.** This allows us to say "there are more" (as described above). Importantly, it needs to be a *unique* solution group, not one that is a subset of another group.

Let's walk through how to modify the algorithm so it meets each requirement.

### Retrieve a Minimal Solution Group Quickly
Algorithm version 1 already does this. It returns a solution group as soon as it detects it is a valid collective, distributive or cumulative solution. No changes are needed to meet this requirement.

### Streaming Solutions Until There is a Maximal Group
Algorithm version 1 only generates alternative solution groups -- it doesn't say which are simply enlarging a previously returnedsolution group with another solution.

To fix this, note that each returned solution group was generated by taking an existing group from the set list and adding a solution to it. So, the algorithm can give each set a unique ID and a "lineage" that tracks where it came from. For example, set id `5` might have a lineage of `0:3:5` indicating that it came directly from set `3`, and `3` came from `0`. The lineage shows the set history (which sets this set came from) for this set.

If we include the lineage when we return a solution group, the caller can see if it is a simple update of a solution group they already have by comparing their lineages.  If they share a prefix, then the new one is a descendent -- it is just "a little more" of that solution. The caller must then use that new lineage as its base to compare from. This last step is needed so it doesn't think all the alternatives generated from its current solution group were also "a little more". It is effectively following one set as it grows.

In this way, we can get a minimal solution group first and slowly grow it over time by examining every solution group that comes from the algorithm and comparing the lineages to the solution we have. This allows us to stream the solutions as they get added to a solution group, eventually ending with the maximal solution group.

If there are 5 unique solution groups for a given phrase, this means we will effectively be picking one at random to show the user. This is OK since, if there are many solutions, it really doesn't matter which we show. [TODO: explain why].

But, this only works if all the subsets of a unique solution group have the same lineage.  Let's examine that next.

### Generate Only Unique Maxmimal Solution Groups
Algorithm 1 will generate all non-empty combinations of solutions. That means if the MRS is simply "files(x)" (which has the constraint `between(1, inf)`), and there are 2 files, it will generate:

~~~
Group 1:
  file1

Group 2:
  file2

Group 3:
  file1
  file2
~~~

The lineage technique will allow the caller to know that Group 3 is really just an updated Group 2, but Group 2 will look like an independent "unique" solution, when it really isn't. Constraints with an `inf` upper limit can accept *all* individuals and so will *always* generate duplicate solutions if they are allowed to form new sets. This is true even if their lower limit is > 1. So, any variable that has an upper constraint of `inf` should not *on its own* be a reason to add a new group to the `set_list`. 

However, if the tree has multiple variables with constraints, other variables *may* be a reason to form a new group. If another variable has an upper limit < `inf` then we do want to return all combinations of, say, "2 files". Thus, in that case we *do* want to create a new set in `set_list` with the new solution so that it can form new combinations, but *only if the value for that variable in the new solution is not already in a set*. Because, if it is already in a set, it is already being tracked and creating a new set to form combinations will, again, create duplicates. 

So, the logic for creating new sets needs to be: Merge a solution into an existing set if it doesn't contribute new individuals to any variables that have constraints that have a max < `inf`. If it doesn't get merged into any existing set, create a new one and add it to `set_list`.

This means that, in the new algorithm, `set_list` begins with no sets. The empty set that Algorithm 1 started with is only used if a solution wasn't merged into an existing set.

### Detect If There Is More Than One Unique Solution Group
Algorithm Version 1 doesn't indicate whether a returned solution group is a unique solution group -- one that isn't a subset of any other. It just returns solution groups that have 1 more solution than those it has generated before. This problem is really the inverse of the one above. In this case, we want to see if a new solution group *isn't* a subset of the one we've selected.

The lineage described above provides a way to determine this. A solution group can only be a subset of another if its lineage is a prefix of the other. Said another way: if group 1 is a subset of group 2, group 2 will have group 1's exact lineage as the start of its lineage. This is because lineage shows a complete history of how a set came to be. If there is a solution that has a different lineage than the one we are tracking as "the chosen solution to show the user", it must include at least one answer that is different than the chosen one, and thus it must be a different unique solution.

So, we will be able to detect if we have more than one unique solution group by picking the lineage that is "the answer" we'll show the user, and then seeing if we can find another solution group that has a different lineage. If there is one, that is a second unique solution group.

### When Can We Stop
If at least one variable has max=inf we need to go all the way to the end to get the maximal solution. If none do, we actually want the *minimal* solution (but tell the user there are more). So we can stop after we find two solutions

TODO: finish this

### Algorithm 2 Design
We now have everything we need to design Algorithm 2. It will be more efficient than Algorithm 1 while also allowing us to give the kinds of answers a user will expect. It uses the same skeleton as Algorithm 1, but has some extensions to meet the requirements above. There are two parts: a "combination generator" based on Algorithm 1, and a "solution group picker" which is new.

**Combination Generator**

Start with:
- `set_list` (a list of sets), which initially is empty

When a `new_solution` is found, for each `selected_set` in `set_list`:

1. Build `new_set` by adding `new_solution` to `selected_set`
2. Generate a `unique_id`. Then, create a lineage for `new_set` by appending `unique_id` to the end of the `selected_set` lineage
3. If `new_set` meets or could meet the criteria (once more rows are added):
  - If it can be merged into `selected_set` merge it
  - If not, add it, along with its lineage, to `set_list`
4. If `new_set` actually *did* meet the criteria, also return it, and its lineage, as a solution group

If `new_solution` meets or could meet the criteria and did not get merged into any set in `set_list`, add it to `set_list`. 


**Solution Group Picker**

Start with `more_than_one_solution_group=False` and `chosen_solution=None`
1. Get the first solution group from the combination generator. This is the `chosen_solution`. Yield it as the "minimal solution" to the caller.
2. From then on, for each `new_solution_group` returned from the combination generator:
- If the lineage of `chosen_solution` is a prefix of `new_solution_group`:
  - Return the new solution in `new_solution_group` as the next solution in `chosen_solution`.
  - Set `chosen_solution` to be the `new_solution_group`
- Otherwise, set `more_than_one_solution_group` to `True`

When complete, indicate to the caller if `more_than_one_solution_group` is `True` or `False`

This algorithm will allow the user interface to call the Solution Group Picker and have it return the "answer" solution group (if one exists), as well as a flag indicating if there are other solution groups so it can respond appropriately as described above.

### Performance Optimizations

Given what we now know about what is needed from our combination generator, there are many optimizations that can be made to improve performance. Here are a couple:
- **Quit generating at 2**: Since we only really care about 2 solution groups, the generator doesn't need to keep track of all the sets to build all combinations.  Instead, once it has returned two unique solution groups, it only needs to generate iterations of those. In fact, it really only needs to generate iterations of the first. This eliminates a lot of work generating and testing sets that aren't used.
- **Merge answers**: We can reduce the number of sets we have to consider in `set_list` by observing that we only need to add a new set to the set list if we have a set that needs to be the base for more alternatives. Variables that have constraints with an upper limit of `inf` don't need to generate all the combinations since they will just be subsets of the one maximal set. So, if a solution only introduces new individuals to variables that have an upper limit of `inf`, it can just be merged into that set, it doesn't need to be added as a separate set to `set_list`.

