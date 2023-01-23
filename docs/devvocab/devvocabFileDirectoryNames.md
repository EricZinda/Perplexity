## Representing File and Directory Names: `fw_seq` and `quoted`
There are several challenges with representing file and directory names in a phrase. First, the user may or may not represent them with some kind of escaping characters around them. For example, to move to the directory "blue" they could say:

~~~
go to 'blue'
go to "blue"
go to blue
~~~

The ERG will nicely recognize the different types of quotes as quotes, so those boil down to the same thing, but it will try to interpret the unquoted one as a "real" sentence, not a reference to "blue" as the name of a thing.

Furthermore, many of the specifiers the user may use for directories or files are not English:

~~~
go to /user/brett
list out f56.txt
~~~

The easiest approach is to require the user to quote anything that represents a file or folder.  We can attempt to do more complicated options later.


If the user simply types in a phrase like "delete 'blue'", the ERG produces 4 parses. The first two attempt to interpret "blue" semantically as the color "blue" by using the predication `_blue_a_1`:

~~~
***** Parse #0:
Sentence Force: comm
[ "delete "blue""
  TOP: h0
  INDEX: e2 [ e SF: comm TENSE: pres MOOD: indicative PROG: - PERF: - ]
  RELS: < [ pronoun_q<0:13> LBL: h4 ARG0: x3 [ x PERS: 2 PT: zero ] RSTR: h5 BODY: h6 ]
          [ pron<0:13> LBL: h7 ARG0: x3 ]
          [ _delete_v_1<0:6> LBL: h1 ARG0: e2 ARG1: x3 ARG2: x8 [ x PERS: 3 NUM: sg ] ]
          [ udef_q<7:13> LBL: h9 ARG0: x8 RSTR: h10 BODY: h11 ]
          [ _blue_a_1<8:12> LBL: h12 ARG0: x8 ARG1: i13 ] >
  HCONS: < h0 qeq h1 h5 qeq h7 h10 qeq h12 > ]

-- Parse #0, Tree #0: 

               ┌────── pron(x3)
pronoun_q(x3,RSTR,BODY)            ┌────── _blue_a_1(x8,i13)
                    └─ udef_q(x8,RSTR,BODY)
                                        └─ _delete_v_1(e2,x3,x8)

...
    

***** Parse #1:
Sentence Force: prop-or-ques
[ "delete "blue""
  TOP: h0
  INDEX: e2 [ e SF: prop-or-ques TENSE: tensed MOOD: indicative PROG: - PERF: - ]
  RELS: < [ _delete_v_1<0:6> LBL: h1 ARG0: e2 ARG1: i3 ARG2: x4 [ x PERS: 3 NUM: sg ] ]
          [ udef_q<7:13> LBL: h5 ARG0: x4 RSTR: h6 BODY: h7 ]
          [ _blue_a_1<8:12> LBL: h8 ARG0: x4 ARG1: i9 ] >
  HCONS: < h0 qeq h1 h6 qeq h8 > ]

-- Parse #1, Tree #0: 

            ┌────── _blue_a_1(x4,i9)
udef_q(x4,RSTR,BODY)
                 └─ _delete_v_1(e2,i3,x4)

~~~

That would be useful, perhaps, in a phrase like "She is 'blue'", where we do mean to use the "blue" semantically to mean "sad" but where the speaker is indicating this is a nonstandard or special use of the word by putting it in quotes. This is not we want, so we can examine the next parse:

~~~
***** Parse #2:
Sentence Force: comm
[ "delete "blue""
  TOP: h0
  INDEX: e2 [ e SF: comm TENSE: pres MOOD: indicative PROG: - PERF: - ]
  RELS: < [ pronoun_q<0:13> LBL: h4 ARG0: x3 [ x PERS: 2 PT: zero ] RSTR: h5 BODY: h6 ]
          [ pron<0:13> LBL: h7 ARG0: x3 ]
          [ _delete_v_1<0:6> LBL: h1 ARG0: e2 ARG1: x3 ARG2: x8 [ x PERS: 3 NUM: sg ] ]
          [ proper_q<7:13> LBL: h9 ARG0: x8 RSTR: h10 BODY: h11 ]
          [ fw_seq<-1:-1> LBL: h12 ARG0: x8 ARG1: i13 ]
          [ _blue_a_1<8:12> LBL: h12 ARG0: i13 ARG1: i14 ] >
  HCONS: < h0 qeq h1 h5 qeq h7 h10 qeq h12 > ]

-- Parse #2, Tree #0: 

                                                 ┌── _blue_a_1(i13,i14)
                                     ┌────── and(0,1)
               ┌────── pron(x3)      │             │
               │                     │             └ fw_seq(x8,i13)
pronoun_q(x3,RSTR,BODY)              │
                    └─ proper_q(x8,RSTR,BODY)
                                          └─ _delete_v_1(e2,x3,x8)

... 
    
~~~

This one is closer because it does indicate that `i13` is a `fw_seq`. `fw_seq` stands for "foreign word sequence" (since quotations often delineate foreign phrases), but it is also used for all kinds of quoted text. It is described in more detail [here](https://blog.inductorsoftware.com/docsproto/erg/ErgSemantics_ForeignExpressions/). In this case, it is telling us that the phrase includes a string in quotes (by using `fw_seq`), but also gives us the semantic interpretation of the phrase in quotes (by using `_blue_a_1`). That would be a good hint if our system was trying to see if the usage of "blue" was a "non-standard" use of the term to mean something like "sad" instead of saying "she is literally the color blue", but it still isn't quite the interpretation we want. 

The next one is what we need here:
~~~
***** CHOSEN Parse #3:
Sentence Force: comm
[ "delete "blue""
  TOP: h0
  INDEX: e2 [ e SF: comm TENSE: pres MOOD: indicative PROG: - PERF: - ]
  RELS: < [ pronoun_q<0:13> LBL: h4 ARG0: x3 [ x PERS: 2 PT: zero ] RSTR: h5 BODY: h6 ]
          [ pron<0:13> LBL: h7 ARG0: x3 ]
          [ _delete_v_1<0:6> LBL: h1 ARG0: e2 ARG1: x3 ARG2: x8 [ x PERS: 3 NUM: sg ] ]
          [ proper_q<7:13> LBL: h9 ARG0: x8 RSTR: h10 BODY: h11 ]
          [ fw_seq<-1:-1> LBL: h12 ARG0: x8 ARG1: i13 ]
          [ quoted<8:12> LBL: h12 ARG0: i13 CARG: "blue" ] >
  HCONS: < h0 qeq h1 h5 qeq h7 h10 qeq h12 > ]

-- Parse #3, Tree #0: 

                                                 ┌── quoted(blue,i13)
                                     ┌────── and(0,1)
               ┌────── pron(x3)      │             │
               │                     │             └ fw_seq(x8,i13)
pronoun_q(x3,RSTR,BODY)              │
                    └─ proper_q(x8,RSTR,BODY)
                                          └─ _delete_v_1(e2,x3,x8)
~~~
This parse doesn't try to deliver the semantic interpretation of the word in quotes, and instead just gives us the raw term using the predication `quoted`, meaning "this text was in quotes". Then, it uses `fw_seq` on the quoted variable `i13`. This will make more sense later since `fw_seq` is used to join together all the words in a quoted string. We'll see that next. For now, it is just a degenerate case that is there for consistency with more complicated quoted strings.

Note that `x8` is quantified by `proper_q` which is often used for proper nouns, but can be used as a marker of all kinds of "raw text". So, by the time `x8` gets to `_delete_v_1`, it should be a nicely quoted string, wrapped in some object, that `_delete_v_1` can use to delete the file.

So for this, we need to implement: `quoted(i)`, `fw_seq(x,i)` and update  `_delete_v_1(e,x,x)` to handle whatever they output.

`quoted` is special in that it has an argument called `CARG` (described in detail [here](https://blog.inductorsoftware.com/docsproto/erg/ErgSemantics_Essence/#further-ers-contents)). `CARG` is a way to pass a constant to a predication without holding in a variable. The argument will simply be raw text:

~~~
          [ quoted<8:12> LBL: h12 ARG0: i13 CARG: "blue" ]
~~~

It is also special in that it uses an `i` variable instead of an `x` variable to hold a value. This is because the ERG wanted to avoid having to have a quantifier for each quoted string, as would be required for an `x` argument. That pattern was covered in the [MRS topic](../devhowto/devhowtoMRS/#other-variables-types-i-u-p).

So, the implementation of `quoted` only has to take the `CARG` and put it into a new object called `QuotedText`, setting the `i` variable to that:

~~~
class QuotedText(object):
    def __init__(self, name):
        self.name = name
        
...

    
@Predication(vocabulary)
def quoted(state, c_raw_text, i_text):
    # c_raw_text_value will always be set
    c_raw_text_value = c_raw_text
    i_text_value = state.get_variable(i_text)

    if i_text_value is None:
        yield state.set_x(i_text, QuotedText(c_raw_text_value))
    else:
        if isinstance(i_text_value, QuotedText) and i_text_value.name == c_raw_text:
            yield state
~~~

The job of `fw_seq(x,i)` is only to set the value of `x` to whatever `i` is, or vice versa (other versions will get more interesting, as described below):

~~~
@Predication(vocabulary)
def fw_seq(state, x_phrase, i_part):
    x_phrase_value = state.get_variable(x_phrase)
    i_part_value = state.get_variable(i_part)
    if i_part_value is None:
        if x_phrase_value is None:
            # This should never happen since it basically means
            # "return all possible strings"
            assert False
        else:
            yield state.set_x(i_part, x_phrase_value)
    else:
        if x_phrase_value is None:
            yield state.set_x(x_phrase, i_part_value)

        elif x_phrase_value == i_part_value:
            yield state
~~~

... and `delete_v_1_comm` has to now include `QuotedText` as a valid thing to delete, and `DeleteOperation.apply_to()` has to be modified to handle converting a `QuotedText` object to a file using the `FileSystem.item_from_path()` method:

~~~
def delete_v_1_comm(state, e_introduced, x_actor, x_what):
    # We only know how to delete things from the
    # computer's perspective
    if state.get_variable(x_actor).name == "Computer":
        x_what_value = state.get_variable(x_what)

        # Only allow deleting files and folders or
        # textual names of files
        if isinstance(x_what_value, (File, Folder, QuotedText)):
            yield state.apply_operations([DeleteOperation(x_what_value)])
            

class DeleteOperation(object):
    
    ...
    
    def apply_to(self, state):
        if isinstance(state, FileSystemState):
            state.file_system.delete_item(self.object_to_delete)
            if isinstance(self.object_to_delete, QuotedText):
                object_to_delete = state.file_system.item_from_path(self.object_to_delete.name)
            else:
                object_to_delete = self.object_to_delete

            state.file_system.delete_item(object_to_delete)
            
~~~

`proper_q` can just be a default quantifier as described [here](../devhowto/devhowtoSimpleQuestions):

~~~
@Predication(vocabulary)
def proper_q(state, x_variable, h_rstr, h_body):
    yield from default_quantifier(state, x_variable, h_rstr, h_body) 
~~~

With those changes, 

~~~
def Example23_reset():
    return FileSystemState(FileSystemMock([(True, "/documents/file1.txt", {"size": 1000}),
                                           (False, "/Desktop", {"size": 10000000}),
                                           (True, "/Desktop/the yearly budget.txt", {"size": 10000000}),
                                           (True, "/Desktop/blue", {"size": 1000})],
                                          "/Desktop"))


def Example23():
    user_interface = UserInterface(Example23_reset, vocabulary, respond_to_mrs_tree)

    while True:
        user_interface.interact_once()
        print()
        
# Running Example23() gives:
? "blue" is in this folder
? delete "blue"
? "blue" is in this folder
~~~


~~~
Sentence Force: comm
[ "delete "the yearly budget.txt""
  TOP: h0
  INDEX: e2 [ e SF: comm TENSE: pres MOOD: indicative PROG: - PERF: - ]
  RELS: < [ pronoun_q<0:30> LBL: h4 ARG0: x3 [ x PERS: 2 PT: zero ] RSTR: h5 BODY: h6 ]
          [ pron<0:30> LBL: h7 ARG0: x3 ]
          [ _delete_v_1<0:6> LBL: h1 ARG0: e2 ARG1: x3 ARG2: x8 [ x PERS: 3 NUM: sg ] ]
          [ proper_q<7:30> LBL: h9 ARG0: x8 RSTR: h10 BODY: h11 ]
          [ fw_seq<7:30> LBL: h12 ARG0: x8 ARG1: x13 ARG2: i14 ]
          [ fw_seq<7:18> LBL: h12 ARG0: x13 ARG1: i15 ARG2: i16 ]
          [ quoted<8:11> LBL: h12 ARG0: i15 CARG: "the" ]
          [ quoted<12:18> LBL: h12 ARG0: i16 CARG: "yearly" ]
          [ quoted<19:29> LBL: h12 ARG0: i14 CARG: "budget.txt" ] >
  HCONS: < h0 qeq h1 h5 qeq h7 h10 qeq h12 > ]

                                                 ┌──────── quoted(budget.txt,i14)
                                                 │ ┌────── quoted(yearly,i16)
                                                 │ │ ┌──── quoted(the,i15)
                                     ┌────── and(0,1,2,3,4)
                                     │                 └─│ fw_seq(x13,i15,i16)
               ┌────── pron(x3)      │                   │
pronoun_q(x3,RSTR,BODY)              │                   │
                    │                │                   └ fw_seq(x8,x13,i14)
                    └─ proper_q(x8,RSTR,BODY)
                                          └─ _delete_v_1(e2,x3,x8)
~~~
The ERG converts the quoted phrase into a set of predications, one for each word in quotes:

~~~
          [ quoted<8:11> LBL: h12 ARG0: i15 CARG: "the" ]
          [ quoted<12:18> LBL: h12 ARG0: i16 CARG: "yearly" ]
          [ quoted<19:29> LBL: h12 ARG0: i14 CARG: "budget.txt" ]
~~~

And then indicates that they are all part of a sequence using the predication `fw_seq` in various forms. `fw_seq` stands for "foreign word sequence" since quotations often delineate foreign phrases, but it is used for all kinds of quoted text. It is described in more detail [here](https://blog.inductorsoftware.com/docsproto/erg/ErgSemantics_ForeignExpressions/):

~~~
          [ fw_seq<7:18> LBL: h12 ARG0: x13 ARG1: i15 ARG2: i16 ]
          [ fw_seq<7:30> LBL: h12 ARG0: x8 ARG1: x13 ARG2: i14 ]
~~~

The first `fw_seq` joins together `i15` and `i16` which are "the" and "yearly" and puts the result in `x13`. The next `fw_seq` joins together `x13` and `i14` (which is "budget.txt") and puts the result in `x8`. So now, `x8` has the entire string again. Note that `x8` is quantified by `proper_q` which is often used for proper nouns, but can be used as a marker of all kinds of "raw text". 