## Handling Tenses
In the previous section on [Non-logical meaning](pxHowTo100NonlogicalMeaning), we saw how, in implementing the predications to support "Do you have commands?" we accidentally supported phrases like:

~~~
? did you have a command?
You can use the following commands: copy and go

? you are having a command?
You can use the following commands: copy and go

? Are you having a command?
You can use the following commands: copy and go
~~~

While they aren't all that likely to be uttered, they really shouldn't work.  And, it makes you wonder what other phrases might work that could be really confusing. When building predications in Perplexity it is always a good idea to be intentional about the phrases you want to support (and test them). When users get unexpected results from utterances (because they weren't anticipated), they lose faith in the ability of the system to understand them.

### Specifying Required Properties
To support restricting when predications get used, and support less accidental misunderstandings like the ones above, Perplexity allows you to specify the types of phrases your predication is meant to support and will automatically skip the predication if the phrase doesn't match. It does this by matching [MRS variable properties](../mrscon/devhowto0010MRS#variable-properties) of the [MRS Index](mrscon/devhowto0010MRS#index) of the phrase. 

Recall that the MRS Index variable is the introduced variable that represents the predication that is "the syntactic head of the phrase". That predication represents what the phrase is “about” or “built around". Usually it is just the main verb. So for "Do you have commands?" it would be `_have_v_1`. There are variable properties specified in the MRS that indicate tense information about that verb, and you can specify which tenses your predication is meant to support using those.

We can see these properties by inspecting the MRS using `/show`:

~~~
? Do you have commands?
You can use the following commands: copy and go

? /show
User Input: Do you have commands?
1 Parses

***** CHOSEN Parse #0:
Sentence Force: ques
[ "Do you have commands?"
  TOP: h0
  INDEX: e2 [ e SF: ques TENSE: pres MOOD: indicative PROG: - PERF: - ]
  RELS: < [ pron<3:6> LBL: h4 ARG0: x3 [ x PERS: 2 IND: + PT: std ] ]
          [ pronoun_q<3:6> LBL: h5 ARG0: x3 RSTR: h6 BODY: h7 ]
          [ _have_v_1<7:11> LBL: h1 ARG0: e2 ARG1: x3 ARG2: x8 [ x PERS: 3 NUM: pl IND: + ] ]
          [ udef_q<12:21> LBL: h9 ARG0: x8 RSTR: h10 BODY: h11 ]
          [ _command_n_1<12:20> LBL: h12 ARG0: x8 ] >
  HCONS: < h0 qeq h1 h6 qeq h4 h10 qeq h12 > ]
~~~

The `INDEX` variable of the MRS is `e2`, which is the introduced variable (i.e. `ARG0`) of `_have_v_1`, as expected.  You can see that `e2` has some properties specified:

~~~
  INDEX: e2 [ e SF: ques TENSE: pres MOOD: indicative PROG: - PERF: - ]
~~~

... that indicate this is a question (`SF: ques`), it is present tense (`TENSE: pres`), etc.  All of the properties are described in the [MRS variable properties section](../mrscon/devhowto0010MRS#variable-properties). If we only want our `_have_v_1` predications called when the verb is in exactly that tense (which we do), we can declare those properties as the only ones supported by using the `properties` argument of the `Predication` object:

~~~
@Predication(vocabulary,
             names=["_have_v_1"],
             properties=[{'SF': 'ques', 'TENSE': 'pres', 'MOOD': 'indicative', 'PROG': '-', 'PERF': '-'}]
             )
def _have_v_1_concept(context, state, e_introduced_binding, x_actor_binding, x_target_binding):
    ...
    
@Predication(vocabulary,
             names=["_have_v_1"],
             properties=[{'SF': 'ques', 'TENSE': 'pres', 'MOOD': 'indicative', 'PROG': '-', 'PERF': '-'}]
             )
def _have_v_1(context, state, e_introduced_binding, x_actor_binding, x_target_binding):
    ...
~~~

With just that change, the follow results:

~~~
? Do you have commands?
You can use the following commands: copy and go

? did you have a command?
I don't understand the way you are using: have

? you are having a command?
I don't understand the way you are using: have

? Are you having a command?
I don't understand the way you are using: have
~~~

The system ignores the predication unless it matches the properties of the phrase, and if it can't find one that works gives a "I didn't understand" message.

### Using Phrases to Specify Properties
Collecting the properties manually can get annoying, and they really don't provide good documentation for what phrases a predication is meant to support. So Perplexity provides an additional approach to you help you build these: Phrases.  Instead of populating the `properties` argument directly, you can provide phrases and Perplexity will help you work it out.

If we instead started with this code, which specifies the phrase we want to support but doesn't supply any properties for it (i.e. specifies `None` where the properties should be:
~~~
@Predication(vocabulary,
             names=["_have_v_1"],
             phrases={"What commands do you have?": None}
             )
def _have_v_1_concept(context, state, e_introduced_binding, x_actor_binding, x_target_binding):
    ...
~~~

... when you run the sample, you get this failure:

~~~
Generating phrase properties for <function _have_v_1_concept at 0x7f8364280790>...
   parsing example: 'What commands do you have?' ...
      'None' did not match properties in any of the following parses:
      _which_q(x5,_command_n_1(x5),pronoun_q(x3,pron(x3),_have_v_1(e2,x3,x5))): {'SF': 'ques', 'TENSE': 'pres', 'MOOD': 'indicative', 'PROG': '-', 'PERF': '-'}
      pronoun_q(x9,pron(x9),basic_free_relative_q(x3,[_command_n_1(x3), _do_v_1(e8,x3,x9)],ellipsis_ref(e2,x3))): Did not contain predicates listed for this function: ['_have_v_1']
      basic_free_relative_q(x3,pronoun_q(x9,pron(x9),[_command_n_1(x3), _do_v_1(e8,x3,x9)]),ellipsis_ref(e2,x3)): Did not contain predicates listed for this function: ['_have_v_1']
      basic_free_relative_q(x3,pronoun_q(x9,pron(x9),[_command_n_1(x3), _do_v_1(e8,x3,x9)]),ellipsis_ref(e2,x3)): Did not contain predicates listed for this function: ['_have_v_1']
      pronoun_q(x9,pron(x9),basic_free_relative_q(x2,[_command_n_1(x2), _do_v_1(e8,x2,x9)],ellipsis_ref(e15,i3))): Did not contain predicates listed for this function: ['_have_v_1']
      pronoun_q(x9,basic_free_relative_q(x2,[_command_n_1(x2), _do_v_1(e8,x2,x9)],pron(x9)),ellipsis_ref(e15,i3)): Did not contain predicates listed for this function: ['_have_v_1']
      basic_free_relative_q(x2,pronoun_q(x9,pron(x9),[_command_n_1(x2), _do_v_1(e8,x2,x9)]),ellipsis_ref(e15,i3)): Did not contain predicates listed for this function: ['_have_v_1']
      basic_free_relative_q(x2,pronoun_q(x9,pron(x9),[_command_n_1(x2), _do_v_1(e8,x2,x9)]),ellipsis_ref(e15,i3)): Did not contain predicates listed for this function: ['_have_v_1']
      pronoun_q(x10,pron(x10),basic_free_relative_q(x5,[_command_n_1(x5), _do_v_1(e9,x5,x10)],ellipsis_ref(e2,i3))): Did not contain predicates listed for this function: ['_have_v_1']
      pronoun_q(x10,basic_free_relative_q(x5,[_command_n_1(x5), _do_v_1(e9,x5,x10)],pron(x10)),ellipsis_ref(e2,i3)): Did not contain predicates listed for this function: ['_have_v_1']
      basic_free_relative_q(x5,pronoun_q(x10,pron(x10),[_command_n_1(x5), _do_v_1(e9,x5,x10)]),ellipsis_ref(e2,i3)): Did not contain predicates listed for this function: ['_have_v_1']
      basic_free_relative_q(x5,pronoun_q(x10,pron(x10),[_command_n_1(x5), _do_v_1(e9,x5,x10)]),ellipsis_ref(e2,i3)): Did not contain predicates listed for this function: ['_have_v_1']
      pronoun_q(x9,pron(x9),basic_free_relative_q(x2,[_command_n_1(x2), _do_v_1(e8,x2,x9)],ellipsis_ref(e15,i3))): Did not contain predicates listed for this function: ['_have_v_1']
      pronoun_q(x9,basic_free_relative_q(x2,[_command_n_1(x2), _do_v_1(e8,x2,x9)],pron(x9)),ellipsis_ref(e15,i3)): Did not contain predicates listed for this function: ['_have_v_1']
      basic_free_relative_q(x2,pronoun_q(x9,pron(x9),[_command_n_1(x2), _do_v_1(e8,x2,x9)]),ellipsis_ref(e15,i3)): Did not contain predicates listed for this function: ['_have_v_1']
      basic_free_relative_q(x2,pronoun_q(x9,pron(x9),[_command_n_1(x2), _do_v_1(e8,x2,x9)]),ellipsis_ref(e15,i3)): Did not contain predicates listed for this function: ['_have_v_1']
      pronoun_q(x16,pron(x16),free_relative_q(x4,udef_q(x10,_command_n_1(x10),[thing(x4), _have_v_1(e20,x16,x4), _do_v_1(e14,x10,x4)]),unknown(e2,x4))): {'SF': 'prop', 'TENSE': 'pres', 'MOOD': 'indicative', 'PROG': '-', 'PERF': '-'}
      pronoun_q(x11,pron(x11),pronoun_q(x17,pron(x17),free_relative_q(x3,[thing(x3), _command_v_1(e8,x3,_do_v_1(e16,x11,x17))],ellipsis_ref(e2,x3)))): Did not contain predicates listed for this function: ['_have_v_1']
      pronoun_q(x11,pron(x11),free_relative_q(x3,pronoun_q(x17,pron(x17),[thing(x3), _command_v_1(e8,x3,_do_v_1(e16,x11,x17))]),ellipsis_ref(e2,x3))): Did not contain predicates listed for this function: ['_have_v_1']
      pronoun_q(x11,pron(x11),free_relative_q(x3,[thing(x3), _command_v_1(e8,x3,pronoun_q(x17,pron(x17),_do_v_1(e16,x11,x17)))],ellipsis_ref(e2,x3))): Did not contain predicates listed for this function: ['_have_v_1']
      pronoun_q(x17,pron(x17),pronoun_q(x11,pron(x11),free_relative_q(x3,[thing(x3), _command_v_1(e8,x3,_do_v_1(e16,x11,x17))],ellipsis_ref(e2,x3)))): Did not contain predicates listed for this function: ['_have_v_1']
      pronoun_q(x17,pron(x17),free_relative_q(x3,pronoun_q(x11,pron(x11),[thing(x3), _command_v_1(e8,x3,_do_v_1(e16,x11,x17))]),ellipsis_ref(e2,x3))): Did not contain predicates listed for this function: ['_have_v_1']
      pronoun_q(x17,pron(x17),free_relative_q(x3,[thing(x3), _command_v_1(e8,x3,pronoun_q(x11,pron(x11),_do_v_1(e16,x11,x17)))],ellipsis_ref(e2,x3))): Did not contain predicates listed for this function: ['_have_v_1']
      free_relative_q(x3,pronoun_q(x11,pron(x11),pronoun_q(x17,pron(x17),[thing(x3), _command_v_1(e8,x3,_do_v_1(e16,x11,x17))])),ellipsis_ref(e2,x3)): Did not contain predicates listed for this function: ['_have_v_1']
      free_relative_q(x3,pronoun_q(x11,pron(x11),[thing(x3), _command_v_1(e8,x3,pronoun_q(x17,pron(x17),_do_v_1(e16,x11,x17)))]),ellipsis_ref(e2,x3)): Did not contain predicates listed for this function: ['_have_v_1']
      free_relative_q(x3,pronoun_q(x17,pron(x17),pronoun_q(x11,pron(x11),[thing(x3), _command_v_1(e8,x3,_do_v_1(e16,x11,x17))])),ellipsis_ref(e2,x3)): Did not contain predicates listed for this function: ['_have_v_1']
      free_relative_q(x3,pronoun_q(x17,pron(x17),[thing(x3), _command_v_1(e8,x3,pronoun_q(x11,pron(x11),_do_v_1(e16,x11,x17)))]),ellipsis_ref(e2,x3)): Did not contain predicates listed for this function: ['_have_v_1']
      free_relative_q(x3,[thing(x3), _command_v_1(e8,x3,pronoun_q(x11,pron(x11),pronoun_q(x17,pron(x17),_do_v_1(e16,x11,x17))))],ellipsis_ref(e2,x3)): Did not contain predicates listed for this function: ['_have_v_1']
      free_relative_q(x3,[thing(x3), _command_v_1(e8,x3,pronoun_q(x17,pron(x17),pronoun_q(x11,pron(x11),_do_v_1(e16,x11,x17))))],ellipsis_ref(e2,x3)): Did not contain predicates listed for this function: ['_have_v_1']
      free_relative_q(x3,[thing(x3), _command_v_1(e8,x3,pronoun_q(x17,pron(x17),pronoun_q(x11,pron(x11),_do_v_1(e16,x11,x17))))],ellipsis_ref(e2,x3)): Did not contain predicates listed for this function: ['_have_v_1']
      pronoun_q(x14,pron(x14),free_relative_q(x3,udef_q(x9,_command_n_1(x9),[thing(x3), _do_v_1(e13,x9,x3,x14)]),ellipsis_ref(e2,x3))): Did not contain predicates listed for this function: ['_have_v_1']
      pronoun_q(x14,pron(x14),udef_q(x9,_command_n_1(x9),free_relative_q(x3,[thing(x3), _do_v_1(e13,x9,x3,x14)],ellipsis_ref(e2,x3)))): Did not contain predicates listed for this function: ['_have_v_1']
      free_relative_q(x3,pronoun_q(x14,pron(x14),udef_q(x9,_command_n_1(x9),[thing(x3), _do_v_1(e13,x9,x3,x14)])),ellipsis_ref(e2,x3)): Did not contain predicates listed for this function: ['_have_v_1']
      free_relative_q(x3,udef_q(x9,_command_n_1(x9),pronoun_q(x14,pron(x14),[thing(x3), _do_v_1(e13,x9,x3,x14)])),ellipsis_ref(e2,x3)): Did not contain predicates listed for this function: ['_have_v_1']
      udef_q(x9,_command_n_1(x9),pronoun_q(x14,pron(x14),free_relative_q(x3,[thing(x3), _do_v_1(e13,x9,x3,x14)],ellipsis_ref(e2,x3)))): Did not contain predicates listed for this function: ['_have_v_1']
      udef_q(x9,_command_n_1(x9),free_relative_q(x3,pronoun_q(x14,pron(x14),[thing(x3), _do_v_1(e13,x9,x3,x14)]),ellipsis_ref(e2,x3))): Did not contain predicates listed for this function: ['_have_v_1']
      udef_q(x9,_command_n_1(x9),free_relative_q(x3,pronoun_q(x14,pron(x14),[thing(x3), _do_v_1(e13,x9,x3,x14)]),ellipsis_ref(e2,x3))): Did not contain predicates listed for this function: ['_have_v_1']
      pronoun_q(x14,pron(x14),free_relative_q(x3,udef_q(x9,_command_n_1(x9),[thing(x3), _do_v_1(e13,x9,x14,x3)]),ellipsis_ref(e2,x3))): Did not contain predicates listed for this function: ['_have_v_1']
      pronoun_q(x14,pron(x14),udef_q(x9,_command_n_1(x9),free_relative_q(x3,[thing(x3), _do_v_1(e13,x9,x14,x3)],ellipsis_ref(e2,x3)))): Did not contain predicates listed for this function: ['_have_v_1']
      free_relative_q(x3,pronoun_q(x14,pron(x14),udef_q(x9,_command_n_1(x9),[thing(x3), _do_v_1(e13,x9,x14,x3)])),ellipsis_ref(e2,x3)): Did not contain predicates listed for this function: ['_have_v_1']
      free_relative_q(x3,udef_q(x9,_command_n_1(x9),pronoun_q(x14,pron(x14),[thing(x3), _do_v_1(e13,x9,x14,x3)])),ellipsis_ref(e2,x3)): Did not contain predicates listed for this function: ['_have_v_1']
      udef_q(x9,_command_n_1(x9),pronoun_q(x14,pron(x14),free_relative_q(x3,[thing(x3), _do_v_1(e13,x9,x14,x3)],ellipsis_ref(e2,x3)))): Did not contain predicates listed for this function: ['_have_v_1']
      udef_q(x9,_command_n_1(x9),free_relative_q(x3,pronoun_q(x14,pron(x14),[thing(x3), _do_v_1(e13,x9,x14,x3)]),ellipsis_ref(e2,x3))): Did not contain predicates listed for this function: ['_have_v_1']
      udef_q(x9,_command_n_1(x9),free_relative_q(x3,pronoun_q(x14,pron(x14),[thing(x3), _do_v_1(e13,x9,x14,x3)]),ellipsis_ref(e2,x3))): Did not contain predicates listed for this function: ['_have_v_1']
      pronoun_q(x12,pron(x12),pronoun_q(x20,pron(x20),free_relative_q(x4,[thing(x4), _have_v_1(e24,x20,x4), _command_v_1(e9,x4,_do_v_1(e17,x12,i18))],unknown(e2,x4)))): {'SF': 'prop', 'TENSE': 'pres', 'MOOD': 'indicative', 'PROG': '-', 'PERF': '-'}
      pronoun_q(x3,pron(x3),basic_free_relative_q(x5,[_command_n_1(x5), _do_v_1(e9,x5,i10)],ellipsis_ref(e2,x3))): Did not contain predicates listed for this function: ['_have_v_1']
      pronoun_q(x3,basic_free_relative_q(x5,[_command_n_1(x5), _do_v_1(e9,x5,i10)],pron(x3)),ellipsis_ref(e2,x3)): Did not contain predicates listed for this function: ['_have_v_1']
      basic_free_relative_q(x5,[_command_n_1(x5), _do_v_1(e9,x5,i10)],pronoun_q(x3,pron(x3),ellipsis_ref(e2,x3))): Did not contain predicates listed for this function: ['_have_v_1']
      basic_free_relative_q(x5,[_command_n_1(x5), _do_v_1(e9,x5,i10)],pronoun_q(x3,pron(x3),ellipsis_ref(e2,x3))): Did not contain predicates listed for this function: ['_have_v_1']
~~~

Examining the output, you can see that Perplexity first parsed the example phrase "What commands do you have?" and then said that `None`, which is the properties we said we supported, didn't match the properties on any MRS parses that ACE provided, and then proceeds to list them all:

~~~
   parsing example: 'What commands do you have?' ...
      'None' did not match properties in any of the following parses:
      
   ...
~~~

This allows us to examine the parses to find which is the one we meant to support and just copy the properties it has. It will usually be near the top.  In this case it is the first one:

~~~
      _which_q(x5,_command_n_1(x5),pronoun_q(x3,pron(x3),_have_v_1(e2,x3,x5))): {'SF': 'ques', 'TENSE': 'pres', 'MOOD': 'indicative', 'PROG': '-', 'PERF': '-'}
~~~

Now we can copy those properties directly into our function definition:

~~~
@Predication(vocabulary,
             names=["_have_v_1"],
             phrases={"What commands do you have?": {'SF': 'ques', 'TENSE': 'pres', 'MOOD': 'indicative', 'PROG': '-', 'PERF': '-'}
                     }
             )
def _have_v_1_concept(context, state, e_introduced_binding, x_actor_binding, x_target_binding):
    ...
~~~

Now we get a different error when we run it:

~~~
Generating phrase properties for <function _have_v_1_concept at 0x7fe317098790>...
   parsing example: 'What commands do you have?' ...
The declared properties:
None

don't match the properties declared by the phrases:
{'SF': 'ques', 'TENSE': 'pres', 'MOOD': 'indicative', 'PROG': '-', 'PERF': '-'}
~~~

Now it is telling us that it understands we want to support the specified phrase, with the specified properties, but that the `properties` argument didn't match (since it is missing).

~~~
@Predication(vocabulary,
             names=["_have_v_1"],
             phrases={"What commands do you have?": {'SF': 'ques', 'TENSE': 'pres', 'MOOD': 'indicative', 'PROG': '-', 'PERF': '-'}
                     },
             properties={'SF': 'ques', 'TENSE': 'pres', 'MOOD': 'indicative', 'PROG': '-', 'PERF': '-'}
             )
def _have_v_1_concept(context, state, e_introduced_binding, x_actor_binding, x_target_binding):
    ...
~~~

This time it works! The real goal here is to get the `properties` argument populated.  The `phrases` section is a way to document why those properties were selected and help you build them.

Note that multiple phrases can be supported. Let's say we also want to support "You have commands." Going through the same process would lead to this:

~~~
@Predication(vocabulary,
             names=["_have_v_1"],
             phrases={"What commands do you have?": {'SF': 'ques', 'TENSE': 'pres', 'MOOD': 'indicative', 'PROG': '-', 'PERF': '-'},
                      "You have commands.": {'SF': 'prop', 'TENSE': 'pres', 'MOOD': 'indicative', 'PROG': '-', 'PERF': '-'}
                      },
             properties=[{'SF': 'ques', 'TENSE': 'pres', 'MOOD': 'indicative', 'PROG': '-', 'PERF': '-'},
                         {'SF': 'prop', 'TENSE': 'pres', 'MOOD': 'indicative', 'PROG': '-', 'PERF': '-'}]
             )
~~~

To save space, you can compress the values permitted in the `properties` argument for `SF` since it is the only difference, using a list. Like this:

~~~
@Predication(vocabulary,
             names=["_have_v_1"],
             phrases={"What commands do you have?": {'SF': 'ques', 'TENSE': 'pres', 'MOOD': 'indicative', 'PROG': '-', 'PERF': '-'},
                      "You have commands.": {'SF': 'prop', 'TENSE': 'pres', 'MOOD': 'indicative', 'PROG': '-', 'PERF': '-'}
                      },
             properties={'SF': ['ques', 'prop'], 'TENSE': 'pres', 'MOOD': 'indicative', 'PROG': '-', 'PERF': '-'}
             )
~~~