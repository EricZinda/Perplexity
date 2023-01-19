## Reordering Quantifier Arguments
We have a serious performance problem in the initial implementation of [`loc_nonsp`](devvocabLoc_nonspAndPlace). The MRS for "Where am I?" is generated such that the predication `place_n` is called before `loc_nonsp`. This means that we will literally call `loc_nonsp` with *every file and folder in the system* until we find where the user is:

~~~
Sentence Force: ques
[ "where am i"
  TOP: h0
  INDEX: e2 [ e SF: ques TENSE: pres MOOD: indicative PROG: - PERF: - ]
  RELS: < [ loc_nonsp<0:5> LBL: h1 ARG0: e2 ARG1: x3 [ x PERS: 1 NUM: sg IND: + PT: std ] ARG2: x4 [ x PERS: 3 NUM: sg ] ]
          [ place_n<0:5> LBL: h5 ARG0: x4 ]
          [ which_q<0:5> LBL: h6 ARG0: x4 RSTR: h7 BODY: h8 ]
          [ pron<9:10> LBL: h9 ARG0: x3 ]
          [ pronoun_q<9:10> LBL: h10 ARG0: x3 RSTR: h11 BODY: h12 ] >
  HCONS: < h0 qeq h1 h7 qeq h5 h11 qeq h9 > ]

               ┌────── pron(x3)
pronoun_q(x3,RSTR,BODY)             ┌────── place_n(x4)
                    └─ which_q(x4,RSTR,BODY)
                                         └─ loc_nonsp(e2,x3,x4)
~~~

If we turn on tracing and execute "Where am I?", you can see `call 5: ['loc_nonsp', ...` being called with `x4` (i.e. `x_location`) set to every file and folder in our test data before the solution is returned: 

~~~
? where am i
Execution 2023-01-18 12:10:39,395: call 1: ['pronoun_q', 'x3', [['pron', 'x3']], [['which_q', 'x4', [['place_n', 'x4']], [['loc_nonsp', 'e2', 'x3', 'x4']]]]]() [ques]
Execution 2023-01-18 12:10:39,395: call 2: ['pron', 'x3']() [ques]
Execution 2023-01-18 12:10:39,396: call 3: ['which_q', 'x4', [['place_n', 'x4']], [['loc_nonsp', 'e2', 'x3', 'x4']]](x3 = Actor(name=User, person=1)) [ques]
Execution 2023-01-18 12:10:39,396: call 4: ['place_n', 'x4'](x3 = Actor(name=User, person=1)) [ques]
Execution 2023-01-18 12:10:39,396: call 5: ['loc_nonsp', 'e2', 'x3', 'x4'](x3 = Actor(name=User, person=1), x4 = Folder(name=/documents, size=0)) [ques]
Execution 2023-01-18 12:10:39,397: call 5: ['loc_nonsp', 'e2', 'x3', 'x4'](x3 = Actor(name=User, person=1), x4 = Folder(name=/, size=0)) [ques]
Execution 2023-01-18 12:10:39,397: call 5: ['loc_nonsp', 'e2', 'x3', 'x4'](x3 = Actor(name=User, person=1), x4 = Folder(name=/Desktop, size=0)) [ques]
Execution 2023-01-18 12:10:39,398: call 5: ['loc_nonsp', 'e2', 'x3', 'x4'](x3 = Actor(name=User, person=1), x4 = File(name=/documents/file1.txt, size=None)) [ques]
Folder(name=/, size=0)
Folder(name=/Desktop, size=0)
~~~

Looking at the implementation of `loc_nonsp` below, observe that the code handling `if x_location_value is None:` is very efficient: it simply asks an object where it is located. The current behavior is hitting the `else` statement which is plenty efficient in general, *but*: the entire tree is inefficient since it loops through every single file and folder and asks "is the user here?":

~~~
@Predication(vocabulary)
def loc_nonsp(state, e_introduced, x_actor, x_location):
    x_actor_value = state.get_variable(x_actor)
    x_location_value = state.get_variable(x_location)

    if x_actor_value is not None:
        if hasattr(x_actor_value, "all_locations"):
            if x_location_value is None:
                # This is a "where is X?" type query since no location specified
                for location in x_actor_value.all_locations():
                    yield state.set_x(x_location, location)
            else:
                # The system is asking if a location of x_actor is x_location,
                # so check the list exhaustively until we find a match, then stop
                for location in x_actor_value.all_locations():
                    if location == x_location_value:
                        # Variables are already set,
                        # no need to set them again, just return the state
                        yield state
                        break
    else:
        # For now, return errors for cases where x_actor is unbound
        pass

    report_error(["thingHasNoLocation", x_actor, x_location])
~~~

So, we can address the performance problem by getting `loc_nonsp` to do the work of finding out the location of its `x_actor` instead. Here's how: Notice that the `which_q` quantifier is what calls `place_n` first and then `loc_nonsp` ([as it should](../devhowto/devhowtoScopalArguments)):
~~~
               ┌────── pron(x3)
pronoun_q(x3,RSTR,BODY)             ┌────── place_n(x4)
                    └─ which_q(x4,RSTR,BODY)
                                         └─ loc_nonsp(e2,x3,x4)
~~~

... but the logic is just as valid (for this case anyway), if it called them in the reverse order. Doing it that way allows us to find the more performant path through `loc_nonsp` since `x4` will be unbound. We can add some simple code to `which_q` to reorder its arguments when it hits this very case:

~~~
def rstr_reorderable(rstr):
    return len(rstr) == 1 and rstr[0][0] in ["place_n"]


@Predication(vocabulary, names=["which_q", "_which_q"])
def which_q(state, x_variable, h_rstr, h_body):
    if rstr_reorderable(h_rstr):
        yield from default_quantifier(state, x_variable, h_body, h_rstr)
    else:
        yield from default_quantifier(state, x_variable, h_rstr, h_body)
~~~

... and we don't have to change `loc_nonsp` at all.

If we run the code again, notice that, unlike the original code above, we are now only iterating through the actual locations that the user is in:

~~~
? where am i
Execution 2023-01-18 16:02:17,321: call 1: ['pronoun_q', 'x3', [['pron', 'x3']], [['which_q', 'x4', [['place_n', 'x4']], [['loc_nonsp', 'e2', 'x3', 'x4']]]]]() [ques]
Execution 2023-01-18 16:02:17,321: call 2: ['pron', 'x3']() [ques]
Execution 2023-01-18 16:02:17,322: call 3: ['which_q', 'x4', [['place_n', 'x4']], [['loc_nonsp', 'e2', 'x3', 'x4']]](x3 = Actor(name=User, person=1)) [ques]
Execution 2023-01-18 16:02:17,322: call 4: ['loc_nonsp', 'e2', 'x3', 'x4'](x3 = Actor(name=User, person=1)) [ques]
Execution 2023-01-18 16:02:17,323: call 5: ['place_n', 'x4'](x3 = Actor(name=User, person=1), x4 = Folder(name=/Desktop, size=0)) [ques]
Execution 2023-01-18 16:02:17,324: call 5: ['place_n', 'x4'](x3 = Actor(name=User, person=1), x4 = Folder(name=/, size=0)) [ques]
in /Desktop
~~~

Much more efficient.

We'll use this same trick later, when we encounter the `thing` predication which is even worse since it returns literally every object in the system!