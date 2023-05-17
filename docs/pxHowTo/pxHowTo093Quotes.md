## Quoted Strings
We've been working around the fact that the most natural way to interact with a file system is by naming things using phrases like "What is in /documents?". This section will work through one way to do this.

There are several challenges with representing file and directory names in a phrase. First, the user may or may not represent them with some kind of escaping characters around them. For example: to move to the directory "blue" they might say:

~~~
go to 'blue'
go to "blue"
go to blue
~~~

The ERG will nicely recognize the different types of quotes as quotes, so those boil down to the same thing, but it will try to interpret the unquoted one as a "real" sentence, not a reference to "blue" as the name of a thing.

Furthermore, many of the specifiers the user may use for directories or files are not English:

~~~
go to /usr/gol
print the contents of f56.txt
~~~

The ERG will represent these, but they require implementing several more predications. The easiest approach is to require the user to quote anything that represents a file or folder.  We can attempt to do more options later.


If the user simply types in a phrase like "delete 'blue'", the ERG produces 4 parses. The first two attempt to interpret "blue" semantically as the color "blue" by using the predication `_blue_a_1` because it recognizes it as a valid English word:

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

That would be useful, perhaps, in a phrase like "She is 'blue'", where we do mean to use "blue" semantically to mean "sad".  In these cases, the information that "blue" was in quotes was lost. This may be the right answer for some scenarios, but it is not we want, so we can move to the next parse:

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

This one is closer. It indicates that `i13` represents "blue" but that `i13` is also part of a `fw_seq`. 

`fw_seq` stands for "foreign word sequence" (since quotations often delineate foreign phrases), but it is also used to represent all kinds of quoted text. `fw_seq` is described in more detail [here](https://delph-in.github.io/docs/erg/ErgSemantics_ForeignExpressions/). In this case, it's telling us that the phrase includes a string in quotes (by using `fw_seq`), but also gives us the semantic interpretation of the phrase in quotes (by using `_blue_a_1`). That would be a good hint if our system was trying to see if the speaker was indicating to us that the usage of "blue" was a "non-standard" use of the term by putting it in quotes since it captures both the semantic meaning and the fact that quotes were around it. In other words, the speaker meant something like "sad" instead of saying "she is literally the color blue", but it still isn't quite the interpretation we want. 

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
This parse doesn't try to deliver the semantic interpretation of the word in quotes. It just provides the raw term using the predication `quoted`, meaning "this text was in quotes". Then, it uses `fw_seq` on the quoted variable `i13`. This indicates it was a "sequence" of one quoted word. Finally, `x8` is quantified by `proper_q` which is often used for proper nouns, but can be used as a marker of all kinds of "raw text". As usual, the quantifier is already implemented by the system. So, for this, we need to implement: `quoted(i)`, `fw_seq(x,i)` and update `_delete_v_1(e,x,x)` to handle whatever they set the variables to.

### quoted(c,i)
`quoted` is unusual in that it has an argument called `CARG` (described in detail in the [ERG Essence topic](https://delph-in.github.io/docs/erg/ErgSemantics_Essence#further-ers-contents)). `CARG` is a way to pass a constant to a predication without requiring an `x` variable. The argument will simply be raw text:

~~~
          [ quoted<8:12> LBL: h12 ARG0: i13 CARG: "blue" ]
~~~

It is also unusual in that it uses an `i` variable instead of an `x` variable to hold an individual. This is because the ERG wanted to avoid having to have a quantifier for each quoted string (as would be required for an `x` argument). That pattern was covered in the [MRS Overview topic](../mrscon/devhowto0010MRS#other-variables-types-i-u-p).

So, the implementation of `quoted` only has to take the `CARG` and put it into a new object we'll create called `QuotedText` (that simply holds the string). Then, it will set the `i` variable to that object if `i` is unbound, or ensure that they are equal if both are bound:

~~~
class QuotedText(object):
    def __init__(self, name):
        self.name = name
        
...

    
# c_raw_text_value will always be set to a raw string
@Predication(vocabulary)
def quoted(state, c_raw_text_value, i_text_binding):
    def bound_value(value):
        if isinstance(value, QuotedText) and value.name == c_raw_text_value:
            return True

        else:
            report_error(["xIsNotYValue", i_text_binding, c_raw_text_value])
            return False

    def unbound_values():
        yield QuotedText(c_raw_text_value)

    yield from individual_style_predication_1(state,
                                              i_text_binding,
                                              bound_value,
                                              unbound_values,
                                              ["unexpected"])
~~~

`quoted()` uses `individual_style_predication_1` because it should never get a set of more than one item, and if it does, it isn't clear what having multiple quoted strings "together" means in MRS. So, we're forcing the system to only pass individuals to us and to report an error if the unexpected case happens.  In that case, we're using the system error `unexpected` which just prints out "I'm not sure what that means."

###
Implementing `fw_seq(x,i)` is a little more subtle. The meaning of `fw_seq(x,i)` is less linguistic and more mechanical: It is `true` when `x` and `i` hold the same "quoted term". If they are both bound, this is easy to check. If `x` is unbound, according to the [predication contract](../pxint/pxint0010PredicationContract), we should conceptually look through all the state in the world and `yield` each state that is the same as `i`. Since `i` could be any string, it would be impossible to do it that way. Instead, we can just assume that all possible text exists in the world (since files and folders can be named anything), and assume it will always exist. So we can simply set `x` to `i` if it is unbound (or vice versa if `i` is unbound): 

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
(Note that `fw_seq` comes in several flavors since its usual job is combine two words at a time from a string and this version is just a degenerate case. We'll get to that next.)

This simple approach means that `delete_v_1_comm` would have to now include `QuotedText` as a valid thing to delete, and `DeleteOperation.apply_to()` would have to be modified to handle converting a `QuotedText` object to a file or folder. In fact, lots of predications would now have to special case `QuotedText` since the user could say things like:

> What is in "foo"?
> 
> Where is "/etc/settings"
> 
> etc.

A different approach allows us to make this more invisible. We can put the logic for converting the quoted text into file and folder objects directly into `fw_seq`:
~~~
@Predication(vocabulary, names=["fw_seq"])
def fw_seq1(state, x_phrase_binding, i_part_binding):
    if i_part_binding.value is None:
        if x_phrase_binding.value is None:
            # This should never happen since it basically means
            # "return all possible strings"
            assert False

        else:
            yield state.set_x(i_part_binding.variable.name, x_phrase_binding.value)

    else:
        yield from yield_from_fw_seq(state, x_phrase_binding, i_part_binding.value)
            
            
# Yield all the solutions for fw_seq where value is bound
# and x_phrase_binding may or may not be
def yield_from_fw_seq(state, x_phrase_binding, value):
    if x_phrase_binding.value is None:
        # x has not be bound
        if is_this_last_fw_seq(state) and hasattr(value, "all_interpretations"):
            # Get all the interpretations of the quoted text
            # and bind them iteratively
            for interpretation in value.all_interpretations(state):
                yield state.set_x(x_phrase_binding.variable.name, interpretation)

            return

        yield state.set_x(x_phrase_binding.variable.name, value)

    else:
        # x has been bound, compare it to value
        if hasattr(value, "all_interpretations"):
            # Get all the interpretations of the object
            # and check them iteratively
            for interpretation in value.all_interpretations(state):
                if interpretation == x_phrase_binding.value:
                    yield state
        else:
            if value == x_phrase_binding.value:
                yield state       
                
                
class QuotedText(object):
    def __init__(self, name):
        self.name = name

    def __repr__(self):
        return f"{self.name}"

    def all_interpretations(self, state):
        # Yield the text converted to a file or folder if possible
        # If one of them exists, return it first so that its errors
        # get priority
        file_rep = File(name=self.name, file_system=state.file_system)
        folder_rep = Folder(name=self.name, file_system=state.file_system)
        if file_rep.exists():
            yield file_rep
            yield folder_rep
        else:
            yield folder_rep
            yield file_rep

        # Always yield the text value last since the others
        # are probably what was meant and the first error
        # hit will be what is returned
        yield self
~~~

In this approach, `fw_seq` yields every interpretation of the quoted text using the helper function `yield_from_fw_seq()`. It calls the `all_interpretations()` method of `QuotedText` and allows it to convert itself to whatever it can mean, thus centralizing the code.

`QuotedText.all_interpretations()` yields the objects that exist first since the first error encountered in a given predication will be the one that gets returned. To see why, imagine a scenario where 'blue' is a folder that doesn't have anything in it.  `fw_seq` will convert the text 'blue' into a folder, a file, and the raw text using the `all_interpretations()` method. `in_p_loc` will report the error "'blue' is not found" for the file, "nothing is in 'blue'" for the folder and the text.  Whichever is first will be remembered due to the [error reporting algorithm](../devhowto/devhowtoChoosingWhichFailure). So, we want the objects that actually exist to come first.

This ensures that a phrase like "what is in 'blue'", where 'blue' is a folder that doesn't have anything in it, will return "nothing is in blue" instead of "'blue' doesn't exist". The latter error gets generated

`proper_q` can just be a default quantifier as described [here](../devhowto/devhowtoSimpleQuestions):

~~~
@Predication(vocabulary)
def proper_q(state, x_variable, h_rstr, h_body):
    yield from default_quantifier(state, x_variable, h_rstr, h_body) 
~~~

With those changes, we can now use some simple phrases with one word quoted files:

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
        
Test: "blue" is in this folder
Yes, that is true.

Test: delete "blue"
Done!

Test: "blue" is in this folder
thing is not in this folder
~~~

That last message is not great. As always, when we add a new predication to the system, we need to teach [the NLG system](../devhowto/devhowtoConceptualFailures) how to interpret the new predications so that it doesn't say 'thing' in the error:

~~~
def refine_nlg_with_predication(tree_info, variable, predication, nlg_data):
    
    ...
    
                # Some abstract predications *should* contribute to the
                # English description of a variable
                
                ...
                
                elif parsed_predication["Lemma"] == "quoted":
                    nlg_data["Topic"] = predication.args[0]

                elif parsed_predication["Lemma"] == "fw_seq":
                    string_list = []
                    for arg_index in range(1, len(predication.arg_names)):
                        if predication.args[arg_index][0] == "i":
                            # Use 1000 to make sure we go through the whole tree
                            string_list.append(english_for_delphin_variable(1000, predication.args[arg_index], tree_info, default_a_quantifier=False))

                        elif predication.args[arg_index][0] == "x":
                            # Use 1000 to make sure we go through the whole tree
                            string_list.append(english_for_delphin_variable(1000, predication.args[arg_index], tree_info, default_a_quantifier=False))
                            
                    nlg_data["Topic"] = f"\'{' '.join(string_list)}\'"
~~~

Now we get:

~~~
Test: "blue" is in this folder
'blue' is not in this folder
~~~

For longer quotes strings like:

> delete "the yearly budget.txt"

The ERG generates a few more variations of `fw_seq` since each only glues two things together:

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

And then indicates that they are all part of a sequence using the predication `fw_seq` in various forms:

~~~
          [ fw_seq<7:18> LBL: h12 ARG0: x13 ARG1: i15 ARG2: i16 ]
          [ fw_seq<7:30> LBL: h12 ARG0: x8 ARG1: x13 ARG2: i14 ]
~~~

The first `fw_seq` joins together `i15` and `i16` which are "the" and "yearly" and puts the result in `x13`. The next `fw_seq` joins together `x13` and `i14` (which is "budget.txt") and puts the result in `x8`. So now, `x8` has the entire string again. `x8` is quantified by `proper_q` which is often used for proper nouns, but can be used as a marker of all kinds of "raw text". 

To make this work, we will need an implementation of `fw_seq(x,x,i)` and `fw_seq(x,i,i)`. We will need to name these differently because Python doesn't allow overloaded functions (i.e. the same function name with different arguments).  Here are all three together:

~~~
@Predication(vocabulary, names=["fw_seq"])
def fw_seq1(state, x_phrase_binding, i_part_binding):
    if i_part_binding.value is None:
        if x_phrase_binding.value is None:
            # This should never happen since it basically means
            # "return all possible strings"
            assert False

        else:
            yield state.set_x(i_part_binding.variable.name, x_phrase_binding.value)

    else:
        yield from yield_from_fw_seq(state, x_phrase_binding, i_part_binding.value)


@Predication(vocabulary, names=["fw_seq"])
def fw_seq2(state, x_phrase_binding, i_part1_binding, i_part2_binding):
    # Only succeed if part1 and part2 are set and are QuotedText instances to avoid
    # having to split x into pieces somehow
    if isinstance(i_part1_binding.value, QuotedText) and isinstance(i_part2_binding.value, QuotedText):
        combined_value = QuotedText(" ".join([i_part1_binding.value.name, i_part2_binding.value.name]))
        yield from yield_from_fw_seq(state, x_phrase_binding, combined_value)


@Predication(vocabulary, names=["fw_seq"])
def fw_seq3(state, x_phrase_binding, x_part1_binding, i_part2_binding):
    # Only succeed if part1 and part2 are set and are QuotedText instances to avoid
    # having to split x into pieces somehow
    if isinstance(x_part1_binding.value, QuotedText) and isinstance(i_part2_binding.value, QuotedText):
        combined_value = QuotedText(" ".join([x_part1_binding.value.name, i_part2_binding.value.name]))
        yield from yield_from_fw_seq(state, x_phrase_binding, combined_value)
~~~

You can see that the two new `fw_seq` implementations have logic to combine the `QuotedText` objects they are passed into a `QuotedText` object. It then returns the objects that this string represents using `yield_from_fw_seq()`. 

Now we have a dilemma: we don't want each `fw_seq` in a multiword string to convert the substring into objects, we only want this to happen on the *final* `fw_seq`, the one that creates the final string. We can detect this case by noticing that the final `fw_seq` is the only one whose introduced variable is used by something *other than* another `fw_seq`. The non-final ones are only consumed by other `fw_seq` as you can see in the MRS above.

So, we can build a helper to detect if a `fw_seq` predication is the final one:
~~~
def is_last_fw_seq(tree, fw_seq_predication):
    consuming_predications = find_predications_using_variable(tree, fw_seq_predication.args[0])
    return len([predication for predication in consuming_predications if predication.name != "fw_seq"]) > 0


def find_predications_using_variable(term, variable):
    def match_predication_using_variable(predication):
        for arg_index in range(1, len(predication.arg_types)):
            if predication.arg_types[arg_index] not in ["c", "h"]:
                if predication.args[arg_index] == variable:
                    predication_list.append(predication)

    predication_list = []
    walk_tree_predications_until(term, match_predication_using_variable)

    return predication_list
~~~

Now we can use this helper in `yield_from_fw_seq()`. Note that `yield_from_fw_seq()` needs a slightly different version of `is_last_fw_seq()` since we need to pass the predication itself to `is_last_fw_seq()` and we don't have that in the middle of executing it. 

So, we added another helper to do just that called `is_this_last_fw_seq()`:

~~~
def yield_from_fw_seq(state, variable, value):
    if is_this_last_fw_seq(state):
        if hasattr(value, "all_interpretations"):
            # Get all the interpretations of the quoted text
            # and return them iteratively
            for interpretation in value.all_interpretations(state):
                yield state.set_x(variable, interpretation)
        else:
            yield value

    else:
        yield state.set_x(variable, value)
                
        
def is_this_last_fw_seq(state):
    this_tree = state.get_binding("tree").value
    this_predication = predication_from_index(this_tree, execution_context().current_predication_index())
    return is_last_fw_seq(this_tree["Tree"], this_predication)
~~~

Now, we can finally run it:

~~~
? "the yearly budget.txt" is in this folder
Yes, that is true.

? delete "the yearly budget.txt"
Done!

? "the yearly budget.txt" is in this folder
''the yearly' budget.txt' is not in this folder
~~~

Note that the error message for the last statement isn't quite right yet because we are putting quotes around each `fw_seq` pair of strings. We can solve this by modifying our NLG code to use the new `is_last_fw_seq()` helper and only put quotes around the final one:

~~~
def refine_nlg_with_predication(tree_info, variable, predication, nlg_data):

    ...
    
                elif parsed_predication["Lemma"] == "fw_seq":
                    string_list = []
                    for arg_index in range(1, len(predication.arg_names)):
                        if predication.args[arg_index][0] == "i":
                            # Use 1000 to make sure we go through the whole tree
                            string_list.append(english_for_delphin_variable(1000, predication.args[arg_index], tree_info, default_a_quantifier=False))

                        elif predication.args[arg_index][0] == "x":
                            # Use 1000 to make sure we go through the whole tree
                            string_list.append(english_for_delphin_variable(1000, predication.args[arg_index], tree_info, default_a_quantifier=False))

                    # If the only thing consuming the introduced variable are other fw_seq predications
                    # Then this is not the final fw_seq, so don't put quotes around it
                    if is_last_fw_seq(tree_info["Tree"], predication):
                        nlg_data["Topic"] = f"'{' '.join(string_list)}'"
                    else:
                        nlg_data["Topic"] = f"{' '.join(string_list)}"

~~~

Now, if we run the scenario again, we get a better answer:

~~~
? "the yearly budget.txt" is in this folder
Yes, that is true.

? delete "the yearly budget.txt"
Done!

? "the yearly budget.txt" is in this folder
'the yearly budget.txt' is not in this folder
~~~

In this example I have not described one, reasonably large, change that needed to be done to make the error handling as clean as it is here (i.e. nonexistent). The [next topic](devvocabContextInHelpers) discusses that.

> Comprehensive source for the completed tutorial is available [here](https://github.com/EricZinda/Perplexity).