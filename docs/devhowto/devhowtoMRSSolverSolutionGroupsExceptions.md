
### Multiple Constraints on a Variable

For "the lawyers came to both houses":
- "the" means 1, 
- lawyers means many

For "the 2 lawyers came to both houses":

"which students" is tricky: equivalent to "tell me any student that...
which students aced the exam - answering one student is OK
which files are in a folder? Should it return 2 files from one folder and a singular one from another?

### More Subtle: 'the'
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
