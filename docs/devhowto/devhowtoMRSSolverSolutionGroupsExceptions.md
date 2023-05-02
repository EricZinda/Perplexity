
### Multiple Constraints on a Variable

### More subtle: 20 mb
10 mb should not generate a set of 10 1mbs
special case this.  Turns a megabyte into a *measure* which is a set of megabytes


### More subtle: propositions
"files are large" when there is only 1 large file
    - should return false, but a human would say, "not 'files' but there is one..."

### More Subtle: 'which'
There are two dials here: how many answers we return and how many are allowed in an answer

Behavior spec: 
It should at least be consistent statements and which

Option 1: Which, when used with no other adjective, can return one.But "which 2 students passed the test" should fail if there are only 1
To do this, add a default determiner so that the plural determiner doesn't get added and require > 1
If there is an adjective like 2 it will override this and work properly
- "which" requires that the variable it refers to is "exactly" if there is any number specified

Issue: This scenario is bad: in a world where there is 4 10 mb files
  - 2 files are 20 mb -> true
  - which 2 files are 20 mb: -> error: there are more than 2 files that are 20 mb

Option 2: Really, both "2 students are in the room" (in a room with 4 students) and "which 2 students are in the room" should work the same, and say "really, there are 4 students in the room" and "which" should return them all.  But if you say "only" it should just fail?
    - Problem with this approach is it requires plural and singular to marked as "only" by default, as well as card, and thus everything needs to see the entire list before answering
    - Also, it gets annoying to say "which files are blah" and have the system say "only one file is blah" and make you have to repeat it as "which file is blah"
    - Could respond with "no but here's the answer you should have asked"

Option 3 (This seems like the right answer): If we make them both not have "exactly" set, then they work consistently, but may be misleading:
    - 2 files are in the folder -> yep (but there are more)
    - which 2 files are in the folder -> x, and y. (but there are more)
    - delete 2 files in the folder -> (are you sure, this will be random?)
    - If we get just enough to say "but there are more", then we can give a good interaction
    - If the user says "only 2 files are in the folder"-> that is wrong
    - Should fail:
        - delete the only two files in the folder 
        - which one file is in the folder
    - delete only two files in the folder -> (are you sure, this will be random?)
    - Design:
        - by default, all types of phrases (comm, prop, ques) are "reply with just one answer, but notify me if there are more". 
            - It could be as simple as "always saying 'there might be more', or doing that if things get expensive to calculate
            - The problem is that we return "minimal" answers iteratively from all_plural_groups_stream() so "which files are in a folder" will return "these 2, but there are more" 
                - Theory: people expect maximal answers
                - So, we need to go wall the way to the end, which means we'll really have all of the answers, which should we return?
                - Option 1: Just pick one and keep updating it as we get more from the generator, when it is done return it
                - Option 1a: return new answers as they come in
                - Option 2: collect and return them all
                - Option 3: just return the minimal set and say "there are more"
        - If the user puts "only" or "the" in front of something it puts a global constraint that ensure there are only that many and fails if not
            - the "notify me if not" will not kick in if there really is only that many, because there won't be more
        - commands work slightly differently though:
            - delete the only two files in the folder -> (there are more than 2)
            - delete only two files in the folder -> (ok, but there are more)

Tested:

Must work this way:
    For sure: which 2 files in a folder are large
        Should work if there are exactly 2 files in a folder that are large
    
    For sure: which files are in a folder? 
        should return all files that are in folders
        Should return 2 files from one folder and a singular one from another

    For sure: which 2 files are in 2 folders? when there is two folders with two files each
        should work. 
        If "which" works as "only": Requires that "only" work distributively

    For sure: which 2 files are 20 mb? if 2 files add up to 20 mb
        Should return the two files collectively

    Yes: "which files are 20 mb" 
        return 2 files that *add up to* 20 mb along with others that are 20 mb by themselves?
    
    For sure: The 2 files in a folder are 20 mb (when there is one folder with 1 file and one folder with 3 files, 2 of which are 20 mb)
        "the two files in a folder" is wrong, so fails

Options:
    For sure: which 2 files are 20 mb? if there are 4 10mb files
        Issue: Does it work the same as "only 2 files are 20 mb"?
    
    For sure: which file is large? when there is more than one
        Issue: should it return more than one?
    
    Yes: which 2 files are large?
        ? returning 4 files is wrong, even though you can pair them up?
        Option: if there are more than 2 you should return an error. This says that it should be "exactly 2"
    
    Yes (with reservations): "Which students passed the test?" 
        might be "one". 
        But you probably say "just one" to acknowledge that it isn't quite right.
        Currently, it fails 
    
    which 2 files in a folder are large?
        Works as long as there are only 2 large files in a folder, anywhere.
        Interpret as "(which 2 files in a folder are large)"
        not as
        "which (2 files in a folder) are large" -> because that would fail if there are more than 2 files in a folder


Still thinking about:

    which files are large?
        just returning 2 of N large files is correct, but not right
        Theory: really people mean "(give me all answers to) which files are large?"

    But if you say "which 2 children in a room are eating?" returning more than one is ok? hmm.
    Unclear how wh should go...


# wh-ques: "which 2 files are large?" should behave like the and error out if there are more than 2
#   BUT: this only is true for the variable that wh-question is referring to
#   leave wh-questions out of this for now

"which students" is special: equivalent to "tell me any student that...between(1, inf), even if plural
    which students aced the exam - answering one student is OK
    Also note that this is required to make "how many students are here" work since the MRS uses which() and "how many" could be 1

"which 2 students": "tell me the 2 students that...
    - Answering with "these 2 and those 2" is probably not right
        Especially if there are 3. Answering with 1&2, 1&3, etc would not e riht



Implementation: tack on a determiner too, so the default won't get used

### More Subtle: 'the'
Needs to compose with whatever constraint is outside the quantifier

For "the lawyers came to both houses":
- "the" means 1, 
- lawyers means between(2, inf)
- the lawyers means the entire group of lawyers which is between(2, inf)

For "the 2 lawyers came to both houses":

There are some words which have a more subtle interpretation: "the" and "which" that is worth understanding.

Let's change the example to "the 2 students lifted a table". Clearly "the" has changed the meaning. While there could be several ways of interpreting "the" here, we'll focus on the reading where it means "the [only] 2 students [I could possibly be talking about] lifted a table". Let's consider two worlds:
- **World 1**: 4 students are lifting tables. A human speaker might respond with something like "which 2 do you mean? I see 4 students doing that.".
- **World 2**: 4 students are in the room with only 2 lifting tables. A human speaker might say something like "Well, yeah, but you see the other two students, right?" and wonder quietly if the speaker is confused.

Either way, we need the system to recognize that something is wrong and respond differently. The only change to the MRS and Tree is replacement of `udef_q` with `_the_q`, everything else is the same:

~~~
                        ┌── _student_n_of(x3,i10)
            ┌────── and(0,1)
            │             └ card(2,e9,x3)
_the_q(x3,RSTR,BODY)
                 │             ┌────── _table_n_1(x11)
                 └─ _a_q(x11,RSTR,BODY)
                                    └─ _lift_v_cause(e2,x3,x11)
~~~

Intuitively, "the" means "the one", as in "the student is here" or "the Eiffel tower is large". Used that way, the constraint would be `between(1, 1)`. But what about "the students are here" or "the buildings in paris are beautiful!"? Here, the constraint is `between(1, inf)`. And finally: "the two students lifted a table"? It seems like the constraint should be `between(2, 2)`.

One approach to handling this is to do the merging differently with `the`. 
|`x3` (students)|`x11`(table)|
|---|---|
|`the`: `between(1, 1)`| `_a_q`: `between(1, 1)`|
|`card`: `between(2, 2)`| `NUM: sg`: `between(1, 1)` |
|`NUM: pl`: `between(2, inf)`| |
