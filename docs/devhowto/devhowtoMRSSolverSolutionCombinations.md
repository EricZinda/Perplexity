## Combination Algorithm
In the section [introducing the solution grouping algorithm](devhowtoMRSSolverSolutionGroupsAlgorithm), the algorithm starts with:

> For each possible combination of solutions from Phase 1 ...

And leaves how to generate this as an exercise for the reader. In this section we'll go through one approach to doing this that properly deals with some subtleties of solution groups that need to be addressed.

### Only 2 Solution Groups Are Needed
The number of solution groups for a given tree in a given world can be quite large, but the truth is that the system only needs 2 of them for any response to a question, proposition or command. Let's go through each to see why.

#### WH-Questions
Let's use this tree from the phase "which 2 files are in a folder?":

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

Some solutions to this are:

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
  
etc, there are more ...
~~~

How many of these does the system need in order to respond? 1 of them? all of them? If we want the system to respond in the way a user expects, we need to observe the way a human would respond. Here are some:

~~~
Lin: Which 2 files are in a folder?
Mila: Umm...there are way more than 2 files in a folder ... which do you mean?
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

Another example: In a physics class of 20 students, where only one student got 100%, the professor is asked, "Which students aced the exam?" and responds with "Only Mariam." Note that the question had "students" (plural) and the professor felt the need to say "only" to indicate that they weren't really answering the question asked since they responded in singular. Saying simply "Mariam" just feels slightly wrong, but note that if 2 students aced it, saying "Mariam and Aron" would be just fine.

So, building a system that is completely literal and responds to "Which 2 files are in a folder?" with "There are more than only 2 files in a folder." (Mila's response above), might be correct but will be annoying.  The Carlos answer is the most complete and generous, but could result in a huge (possibly expensive) answer when the user, who also understands that the question implicitly means "only", probably misunderstood the world state. Hana's answer is a good middle ground that gives an answer "just in case", but acknowledges that the question was probably a misunderstanding of the world state. Hers doesn't overload the questioner with a huge number of answers.

This implies that, for WH-questions (where, what, who, etc), we need to get one answer to respond and see if there is another answer to let the questioner know there are more. So, we need 2 answers.

#### Yes/No Questions
What about (using the same examples from above): "are there 2 files in a folder?" or "did students ace the exam"? These act the same as WH-Questions. Responding to "did students ace the exam" with "yes." would be very misleading, and most would consider it outright wrong. Responding to "Are there 2 files in a folder" with Yes is technically true for the above example, but would probably just be considered a little misleading. So the answerer might respond with something like "*technically* yes, but there are more."

This implies that, for Yes/No questions, we need to get one answer to respond and see if there is another answer to let the questioner know there are more. So, we also need 2 answers.

#### Propositions
Continuing with our example, this time as a proposition: "2 files are in a folder" or "students aced the exam". These act just like Yes/No questions: The first is "technically true" the second is just wrong. So: 2 answers required.

#### Commands
What should "delete 2 files in a folder" do? Delete all examples of "2 files in a folder" feels wrong. There seems to be an implied "one instance of" after delete. A clearer example might be "delete a file in a folder". There are 4 examples of "a file in a folder" in the world in question, but deleting them all due to that phrase would be certainly wrong.

It should also be noted that actually deleting "2 files" or "a file" feels a bit random. For this example, a human might ask, "Do you mean a random 2 files?". Certainly "delete files in a folder" if there is only 1 file feels wrong, just like "Talk to the students that aced the exam" when there is only 1.  It would probably get a response like "OK, but there is only one" to indicate that it isn't *quite* the question asked.

All this is to say that, again, commands should also retrieve 2 solution groups. The first is what will be "done", the second is to see if some kind of clarifying response should be given.

#### The, Only, At Least, etc
TODO: The difference between "2 files are in a folder" or "students aced the exam" is that "2 files is explicit"...

### Maximal vs. Subset Solution Groups
Based on the above analysis, we're going to need to retrieve two solution groups when processing a user phrase and show the user (or do) the first group. The second group is just tested to see if it exists and then to say "there are more answers here...".

The problem is: there can be many correct solution groups for a given answer which aren't "maximal".  For example: for "which files are in a folder?" when there are these files in a folder:

~~~
/folder/file1.txt
/folder/file2.txt
/folder/file3.txt
/folder/file4.txt
~~~

... one correct answer is:

~~~
/folder/file1.txt
/folder/file2.txt
~~~

... another is:

~~~
/folder/file1.txt
/folder/file2.txt
/folder/file3.txt
~~~

etc. Basically, any combination of files in a folder is a "technically correct" answer so long as it is > 1 (due to plural "files"). While it is technically correct, if you asked a person, "which files are in a folder" and they gave you one of those answers, you might be a bit annoyed and clarify with "can you give me the whole list?" If we are only going to return one solution group, we really want to return the maximal solution group.  

Even one plural variable in an MRS can potentially generate multiple groups.  For example: "men are walking" (when talking about a specific group of men). The entire group of "men" can be represented in one solution group, so you'd just expect one group. But: subsets of that group would also be true, so other solution groups are also technically correct.

With two variables: "men(x) are walking a dog(y)" (when talking about one group of men walking a particular dog) you'd still only expect one solution group: the "maximal" solution. But again, subsets would be technically true, just not really telling the whole story.

All this is to say: if you're only going to give one answer, nobody wants one that isn't "maximal". The only reason to generate different combinations of solutions that all meet the constraints is if *constraints* need the alternatives. Otherwise, we should maximize the groups that are created.
 
However, it should return sets as soon as they find an answer that meets the constraints, but then keep returning it as the set gets enlarged. That way, the user can see answers as they come.

One final point: all solutions in a solution group needs to conform consistently to at least one type (collective, distributive or cumulative). There are some cases where a given group can conform to more than one, which is fine.

To sum up:
- Since we are only going to show the user one solution group, it should be a maximal group
- It should get returned iteratively, starting as soon as there is a minimal group that meets its constraints, but the entire maximal group should be ultimately returned before it finishes.
- The complete solution group shown should meet the rules for one of the three types (collective, distributive or cumulative).


### Algorithm Version 1
This will be the skeleton of the algorithm we're going to use:

Start with a list of sets, which initially is only the empty set. 

2. When a new solution is found: for each set in the list:
- Build a new set by adding the solution to the chosen existing set 
- If it meets or could (once more rows are added) meet the criteria, add it to the list of sets as a new set
- Then, if it actually did meet the criteria, also yield it as a solution group
 
It is not final because, while it will produce all combinations that meet the criteria, it also produces the problematic "subset" or "minimal" solutions that we described above. 

### Algorithm Version 2
We want *maximal groups* since we only show the user one answer and we don't want to show what seems like a "subset" answer as described above. We don't want groups where the union between it and another group forms a valid group, because then it isn't maximal.

Thinking about the algorithm: The only time to create a new set in the set list is if we need that new set in the list so that it combines with new solutions to generate alternative solution groups with it. We only want alternative solution groups that are *maximal*. So, we should only add new sets into the list that won't become subsets. Any variable with a criteria that has an upper bound like "2 files" (between(2, 2)) or "less than 2" (between(1,2 )) will generate solution groups

Note that some of these *can* be merged together and still meet the criteria so the defintion above of "those that combines with new solutions to generate alternative solution " is wrong?

For each variable in the criteria:
- If the variable's upper bound is inf then it potentially isn't finished gathering solutions until they have all been seen. Furthermore, it means that any alternative arrangements of that variable can be merged back and still be valid. Therefore, that particular variable, on its own, should not force an alternative solution group.
- If its upper bound is not inf this means it is a set number of items, and thus every combination is unique. Thus, it is an alternative and shouldn't be merged

So: since the lower bound is always >= 1, and never inf, those are really the only two cases. 

This means that we do not need to generate all alternatives for variables with an upper bound of inf. So, if a solution comes in that *only* updates variables with an upper bound of inf, we can just update those sets in place -- we don't need the alternatives.

Furthermore, if *all* variables with criteria have an upper bound of inf, then we can lock down to one solution group to collect the single answer.

However, if we want to continue returning answers after the initial "minimal" solution, we need to only choose one of the newly generated combinations per new solution. To do this, we track the lineage of a solution group by giving it an ID.

Thoughts:
- Once a solution group meets across all variables, we need to keep returning answers if new solutions get added to it.
  - After it has been initially returned as a solution that meets, the only answers that can possibly get added to it are those that only modify variables that have an upper bound of inf (because that is the criteria for merging).
  - BUG: the bug is that we are requiring it to be a unique coll/etc. value. It is just that it is a solution is all that matters.
- TODO: For propositions, we need to respond with "there are more" if it is "at least" or "exactly" once we get above the level that a normal person would say "at least" for.  So, sometimes we say "there are more" for when there is another solution group, but othertimes we say "there are more" for when "only" would have failed.  For example: "a few files ..." works for 100 files since it is "at least". but "only a few files" would fail.
Potential bug: less than 10: between(1, 10), which solution groups will it generate?
- because max != inf it will generate all combinations as different solutions, including those that are < 10.  
- "Maximal" really means: the largest number for which the criteria is still true, that seems to be the better definition
Key: The real design here is that we want to get back answers when they meet the minimal constraints, that allows us to stop immediately for prop and ques and answer. But for comm and wh_ques, we then want to iterate to the maximal group
- for prop and ques, we want to add "there are more" even if there are more *in the current solution group*. If the user says "a few files are in this folder" and there are 100, we'd like it to say "yes but there are more". For wh-ques and comm, we want it to say there are more if there is another *solution group*


### Criteria Optimizations

### TODO
TODO: For a world that has 2 folders, each with 4 files, if the user says "which 2 files are in 2 folders", we can produce several distributive solution groups. But "which files are in 2 folders" you'd only expect to get a single solution back.  What's the difference? between(N, inf).

TODO: See if this is right: 
        # Check if this was a group that is not (n, inf) and this solution added individuals, if so we need a new group
        # So that they old group can be there to recombine with new solutions

But: delete 2 files
    (not all, just two)
    This *doesn't mean* "delete but only if there are only 2 files"
    It does mean: only pick one of the solutions where there are 2 files and delete it
    Thus, it isn't the same as setting to exactly 2
    Conclusion: commands should just pick the first solution

If you say "2 children are eating" it is between(2, 2), but you really mean "at least"
    This is kind of an outer quantifier example...
    Ditto for "are 2 children eating?"
    BUT: this *isn't* the same as saying between(2, inf), because it still has to be exactly 2 per solution
    It matters because if you say "1 file is 20 mb" you *don't* mean "at least 1 file is 20 mb" because that would allow 2 files that add up to 20 mb.


delete large files
    (all)
delete files
    (all)
delete 2 files
    (not all, just two)

Theory: delete should just do the *first answer*. Only works like above if we get the maximal answer
Theory: commands should always be "only" (but this only makes sense if max isn't inf), and you have to specify for something else

