## thing(x)
When there is no other predication restricting a variable, the ERG will often use `thing(x)` to indicate that `x` should be a generic thing.  The implementation of it is simple: it is true for any object in the system.

For example, in "What is large?", we get:

~~~
[ "what is large?"
  TOP: h0
  INDEX: e2 [ e SF: ques TENSE: pres MOOD: indicative PROG: - PERF: - ]
  RELS: < [ thing<0:4> LBL: h4 ARG0: x3 [ x PERS: 3 NUM: sg ] ]
          [ which_q<0:4> LBL: h5 ARG0: x3 RSTR: h6 BODY: h7 ]
          [ _large_a_1<8:13> LBL: h1 ARG0: e2 ARG1: x3 ] >
  HCONS: < h0 qeq h1 h6 qeq h4 > ]

             ┌────── thing(x3)
which_q(x3,RSTR,BODY)
                  └─ _large_a_1(e2,x3)
~~~

`thing(x3)` has the same [problem that `place(x)` had](devvocabReorderingQuantifierArguments): it is called before any other predication so the system will literally iterate through every object (e.g. file and folder) in the system to see if it is in "this folder". It also has the same solution that was described in that section.  Adding `thing` to the list of ["reorderable quantifier arguments"](devvocabReorderingQuantifierArguments) will solve it:

~~~
def rstr_reorderable(rstr):
    return isinstance(rstr, TreePredication) and rstr.name in ["place_n", "thing"]
    
    
@Predication(vocabulary)
def thing(state, x):
    x_value = state.get_variable(x)

    if x_value is None:
        iterator = state.all_individuals()
    else:
        iterator = [x_value]

    for item in iterator:
        yield state.set_x(x, item)
~~~

We can now ask "what is large?" against a world that has a large folder and a large file:

~~~
def Example22_reset():
    return FileSystemState(FileSystemMock([(True, "/documents/file1.txt", {"size": 1000}),
                                           (False, "/Desktop", {"size": 10000000}),
                                           (True, "/Desktop/file2.txt", {"size": 10000000}),
                                           (True, "/Desktop/file3.txt", {"size": 1000})],
                                          "/Desktop"))


def Example22():
    user_interface = UserInterface(Example22_reset, vocabulary, respond_to_mrs_tree)

    while True:
        user_interface.interact_once()
        print()


? what is large
Folder(name=/Desktop, size=10000000)
File(name=/Desktop/file2.txt, size=10000000)


? /show
User Input: what is large
1 Parses

***** CHOSEN Parse #0:
Sentence Force: ques
[ "what is large"
  TOP: h0
  INDEX: e2 [ e SF: ques TENSE: pres MOOD: indicative PROG: - PERF: - ]
  RELS: < [ thing<0:4> LBL: h4 ARG0: x3 [ x PERS: 3 NUM: sg ] ]
          [ which_q<0:4> LBL: h5 ARG0: x3 RSTR: h6 BODY: h7 ]
          [ _large_a_1<8:13> LBL: h1 ARG0: e2 ARG1: x3 ] >
  HCONS: < h0 qeq h1 h6 qeq h4 > ]

-- CHOSEN Parse #0, CHOSEN Tree #0: 

             ┌────── thing(x3)
which_q(x3,RSTR,BODY)
                  └─ _large_a_1(e2,x3)

which_q(x3,thing(x3),_large_a_1(e2,x3))
~~~

"What is large?" has a parse with `thing(x)` in it, which successfully lists all the large things in the system, both the folder and the file.

> Comprehensive source for the completed tutorial is available [here](https://github.com/EricZinda/Perplexity).
