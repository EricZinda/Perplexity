{% raw %}## Solution Group Handlers and Global Criteria
In the [previous section](https://blog.inductorsoftware.com/Perplexity/home/pxhowto/pxHowTo100NonlogicalMeaning) we implemented variations of "Do you have commands?" by implementing a custom *solution group handler*, but we didn't complete it.  Since there are only two commands, really, we should do a better job on the following phrases that succeed, and shouldn't:

```
? Do you have 3 commands?
You can use the following commands: copy and go

? Do you have many commands?
You can use the following commands: copy and go

? Do you have several commands?
You can use the following commands: copy and go
```

All of these phrases are using words like "several" or "3" which quantify how many of something the speaker is interested in. When we implement a solution group handler we take over responsibility for doing the counting, and we're not doing that.

### Inspecting Global Criteria
When a speaker uses a phrase that constrains the solution group in some way, these constraints are added to the arguments and can be inspected:

Let's change our `have_v_1` solution group handler to output these constraints so we can see them:

```
@Predication(vocabulary,
             names=["solution_group__have_v_1"],
             handles_interpretation=_have_v_1_concept)
def _have_v_1_group(context, state_list, e_introduced_binding_list, x_actor_variable_group, x_target_variable_group):
    print(f"x_actor_binding constraints: {x_actor_variable_group.variable_constraints}")
    print(f"x_target_binding constraints: {x_target_variable_group.variable_constraints}")
    yield [state_list[0].record_operations([RespondOperation("You can use the following commands: copy and go")])]
```

And then run it:

```
? do you have commands
x_actor_binding constraints: {x3: min=1, max=inf, global=None, required_values=None, pred=pronoun_q(x3)}
x_target_binding constraints: {x8: min=2, max=inf, global=None, required_values=None, pred=udef_q(x8)}
You can use the following commands: copy and go

? /show
User Input: do you have commands
1 Parses

***** CHOSEN Parse #0:
Sentence Force: ques
[ "do you have commands"
  TOP: h0
  INDEX: e2 [ e SF: ques TENSE: pres MOOD: indicative PROG: - PERF: - ]
  RELS: < [ pron<3:6> LBL: h4 ARG0: x3 [ x PERS: 2 IND: + PT: std ] ]
          [ pronoun_q<3:6> LBL: h5 ARG0: x3 RSTR: h6 BODY: h7 ]
          [ _have_v_1<7:11> LBL: h1 ARG0: e2 ARG1: x3 ARG2: x8 [ x PERS: 3 NUM: pl IND: + ] ]
          [ udef_q<12:20> LBL: h9 ARG0: x8 RSTR: h10 BODY: h11 ]
          [ _command_n_1<12:20> LBL: h12 ARG0: x8 ] >
  HCONS: < h0 qeq h1 h6 qeq h4 h10 qeq h12 > ]

-- CHOSEN Parse #0, CHOSEN Tree #0: 

               ┌────── pron(x3)
pronoun_q(x3,RSTR,BODY)            ┌────── _command_n_1(x8)
                    └─ udef_q(x8,RSTR,BODY)
                                        └─ _have_v_1(e2,x3,x8)
```

You can see from the output that the constraints on `x3`, which is where "you" is represented are between 1 and inf (infinity):

```
x_actor_binding constraints: {x3: min=1, max=inf, global=None, required_values=None, pred=pronoun_q(x3)}
```

That's because, if you look at the MRS, `x3` doesn't indicate one way or the other if "you" is plural or singular "you", and there aren't any other predications that would constrain things.

For `x8` we get a constraint between 2 and infinity.  Looking at the MRS you can see that `x8` has the properties `[ x PERS: 3 NUM: pl IND: + ]` set in the `have_v_1` predication, which indicates plurality.  I.e. 2 or more:

```
x_target_binding constraints: {x8: min=2, max=inf, global=None, required_values=None, pred=udef_q(x8)}
```

Running this:

```
? Do you have 3 commands
x_actor_binding constraints: {x3: min=1, max=inf, global=None, required_values=None, pred=pronoun_q(x3)}
x_target_binding constraints: {x8: min=3, max=3, global=None, required_values=None, pred=card(3)}
You can use the following commands: copy and go
```

Shows how, if the speaker says "3", the constraints are set to a min and max of "3".

Let's try:

```
? Do you have the command?
x_actor_binding constraints: {x3: min=1, max=inf, global=None, required_values=None, pred=pronoun_q(x3)}
x_target_binding constraints: {x8: min=1, max=1, global=GlobalCriteria.all_rstr_meet_criteria, required_values=None, pred=_the_q(x8)}
You can use the following commands: copy and go
```

The word "the" means "the one and only" or "the 1 group" and so it has a min/max of 1 and it has `global=GlobalCriteria.all_rstr_meet_criteria`. `all_rstr_meet_criteria` is how "the 1 group" gets handled.  It means: all of the things that "the" refers to in its `RSTR` must be true of its `BODY`. Let's look at the MRS tree to explain:

```
               ┌────── pron(x3)
pronoun_q(x3,RSTR,BODY)            ┌────── _command_n_1(x8)
                    └─ _the_q(x8,RSTR,BODY)
                                        └─ _have_v_1(e2,x3,x8)
```

Since `all_rstr_meet_criteria` is set on `x8`, it is referring to the `RSTR` and `BODY` of: `_the_q(x8,RSTR,BODY)`.

The `RSTR` is simply `_command_n_1(x8)`, so *all* commands in the system are being referred to.  The `BODY` is set to `_have_v_1(e2,x3,x8)`.  So, as long as "you" have all of the commands in the system, this should be true.

What about "The commands are copy".  This would put "all commands" in the `RSTR` and "being copy" in the `BODY` which is certainly not true for all of them, so it should fail.

What about this:

```
? Do you have the 3 commands?
x_actor_binding constraints: {x3: min=1, max=inf, global=None, required_values=None, pred=pronoun_q(x3)}
x_target_binding constraints: {x8: min=3, max=3, global=GlobalCriteria.all_rstr_meet_criteria, required_values=None, pred=_the_q(x8)}
You can use the following commands: copy and go

? /show
...
                                               ┌── _command_n_1(x8)
                                   ┌────── and(0,1)
               ┌────── pron(x3)    │             │
               │                   │             └ card(3,e14,x8)
pronoun_q(x3,RSTR,BODY)            │
                    └─ _the_q(x8,RSTR,BODY)
                                        └─ _have_v_1(e2,x3,x8)
```

This one says `x8` which is `_the_q(x8,RSTR,BODY)` must have 3 different values in it. And: all commands in the system should be true of the body. While it is certainly true that the system "has" all the commands, it is not true that there are 3 of them, so this is false.

Normally, Perplexity handles checking these constraints and doesn't consider a solution group to be valid unless it meets them all. But when you build a solution group handler, you are telling the system: I am doing something custom, and thus I will be responsible for making sure the constraints are met.

Last update: 2024-10-11 by Eric Zinda [[edit](https://github.com/EricZinda/Perplexity/edit/main/docs/pxHowTo/pxHowTo105GlobalCriteria.md)]{% endraw %}