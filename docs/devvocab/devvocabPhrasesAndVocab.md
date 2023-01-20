## Phrases and Vocabulary
When implementing a natural language system using DELPH-IN, start by analyzing the phrases you want to support and the predications they generate. The predications are what you'll need to implement. There are many ways to do this, but the easiest is to interact with the system we [ended the previous section with](../devhowto/devhowtoPredicationArgumentsAndUsage) and use the [diagnostics features](../devhowto/devhowtoDiagnostics) (i.e. `/show`) to see the predications for the phrases we type.  

Here's the code we'll use to run the whole system:

~~~
def Example18_reset():
    return State([Actor(name="Computer", person=2),
                  Folder(name="Desktop"),
                  Folder(name="Documents"),
                  File(name="file1.txt", size=1000000)
                  ])


def Example18():
    user_interface = UserInterface(Example18_reset, vocabulary, respond_to_mrs_tree)

    while True:
        user_interface.interact_once()
        print()
~~~

Note that the previous section already implemented an initial set of predications: [`_a_q`](../devhowto/devhowtoScopalArguments), [`file_n_of`, `large_a_1`](../devhowto/devhowtoConjunctions), [`small_a_1`](../devhowto/devhowtoHandlingEventInformation), and [`which_q`, `pron`, `pronoun_q`, `very_x_deg`, `folder_n_of`, `delete_v_1`](../devhowto/devhowtoFinishingErrors).

To determine the next set, let's feed phrases we want to support into `Example18()` and see what predications are missing.

### "Where am i?": `loc_nonsp` and `place_n`
"Where am I?" generates the following MRS:
~~~
# Running Example18() gives:
? where am i
I don't know the words: loc_nonsp, place

? /show
User Input: where am i
1 Parses

***** CHOSEN Parse #0:
[ "where am i"
  TOP: h0
  INDEX: e2 [ e SF: ques TENSE: pres MOOD: indicative PROG: - PERF: - ]
  RELS: < [ loc_nonsp<0:5> LBL: h1 ARG0: e2 ARG1: x3 [ x PERS: 1 NUM: sg IND: + PT: std ] ARG2: x4 [ x PERS: 3 NUM: sg ] ]
          [ place_n<0:5> LBL: h5 ARG0: x4 ]
          [ which_q<0:5> LBL: h6 ARG0: x4 RSTR: h7 BODY: h8 ]
          [ pron<9:10> LBL: h9 ARG0: x3 ]
          [ pronoun_q<9:10> LBL: h10 ARG0: x3 RSTR: h11 BODY: h12 ] >
  HCONS: < h0 qeq h1 h7 qeq h5 h11 qeq h9 > ]

Unknown words: [('loc_nonsp', ['e', 'x', 'x'], 'ques', False), ('place_n', ['x'], 'ques', False)]
~~~

We'll need to [implement the `loc_nonsp` and `place_n` predications](devvocabLoc_nonspAndPlace) to make it work. In that topic we'll also implement a notion of the "current" directory to support it.

### "What is in this directory?": `thing`, _`in_p_loc`, _`this_q_dem`
"What is in this directory?" introduces 3 new predications:

~~~
? what is in this directory?
I don't know the words: thing, in, this, directory

? /show
User Input: what is in this directory?
7 Parses

***** CHOSEN Parse #0:
Sentence Force: ques
[ "what is in this directory?"
  TOP: h0
  INDEX: e2 [ e SF: ques TENSE: pres MOOD: indicative PROG: - PERF: - ]
  RELS: < [ thing<0:4> LBL: h4 ARG0: x3 [ x PERS: 3 NUM: sg ] ]
          [ which_q<0:4> LBL: h5 ARG0: x3 RSTR: h6 BODY: h7 ]
          [ _in_p_loc<8:10> LBL: h1 ARG0: e2 ARG1: x3 ARG2: x8 [ x PERS: 3 NUM: sg IND: + ] ]
          [ _this_q_dem<11:15> LBL: h9 ARG0: x8 RSTR: h10 BODY: h11 ]
          [ _directory_n_1<16:25> LBL: h12 ARG0: x8 ] >
  HCONS: < h0 qeq h1 h6 qeq h4 h10 qeq h12 > ]

Unknown words: [('thing', ['x'], 'ques', False), ('_in_p_loc', ['e', 'x', 'x'], 'ques', False), ('_this_q_dem', ['x', 'h', 'h'], 'ques', False), ('_directory_n_1', ['x'], 'ques', False)]
~~~

We'll need to implement [`thing`](devvocabThing), `in_p_loc`, [`this_q_dem`](devvocabThis_q_dem) to make it work.

### TBD

- what files are there?
- what is in this directory?
- Where is X?
- Find all the files that X
- copy foo.txt to the folder named desktop


> Comprehensive source for the completed tutorial is available [here](https://github.com/EricZinda/Perplexity).
