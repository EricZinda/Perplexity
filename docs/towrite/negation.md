** Negation

Negation works by taking the part of the tree that is scopal under the `neg()` predication and seeing if there are are both no solution groups *and* that there is at least one failure that is not "formNotUnderstood". It does the latter to ensure the logic was actually processed and "proven" false.

Let's take the example, "I don't have cash":

~~~
                         ┌────── _cash_n_1(x11)
         ┌─ udef_q(x11,RSTR,BODY)               ┌────── pron(x3)
neg(e2,ARG1)                  └─ pronoun_q(x3,RSTR,BODY)
                                                     └─ _have_v_1(e10,x3,x11)
~~~

In a world where we have modeled that I *do* have cash, there will be a solution group for the branch that is under negation:

~~~
             ┌────── _cash_n_1(x11)
udef_q(x11,RSTR,BODY)               ┌────── pron(x3)
                 └─ pronoun_q(x3,RSTR,BODY)
                                         └─ _have_v_1(e10,x3,x11)
~~~

... and thus the negation will fail: neg(True) == False

But note that there are several distinct kinds of failures that the tree under negation could have. The sections below describe various kinds that you might encounter.

*** Logical Failures

If we assume that, "if there is not a fact that says it is true, then it is false", we have what is called a ["Closed-world Assumption"](https://en.wikipedia.org/wiki/Closed-world_assumption). This assumption allows the engine to assume it has proven something False if it is able to prove it True.  Conversely, if we can't prove it true then it is assumed to be False.  This means that there are an unlimited number of things that will be false simply because we don't have facts about them.

Continuing the example from above, if there is not a fact that says "User has cash" in the system, the subtree will not have a Solution Group, which the engine interprets as False, meaning "we have proven this fact to be false".

I'm calling this a "Logical Failure" for reasons that should become clear later.

*** Not Understood Failures

Imagine that the world does not have the logic to support present-tense "have" (as in "I don't have cash"). In Perplexity, situations where a predication is neither true nor false because they are not understood show this by failing, but registering the error "formNotUnderstood".

Failing the subtree with "formNotUnderstood" will also fail to provide a solution to the tree, but it is a very different kind of failure. Really, it should be interpreted as "I don't understand". Perplexity handles this case specially by making the `neg()` predication also fail with "formNotUnderstood" so that the entire phrase will get a "I'm not sure what you meant" error instead of an inappropriate "Yes it is true that you don't have cash!" error.

*** Non-logical Failures

Let's change the example slightly to "I don't have any cash in my wallet", and assume that the person doesn't have a wallet, and also that Perplexity does understand (have code for) all of the predications.  The tree being evaluated will effectively be "neg(I have cash in my wallet)". "I have cash in my wallet" will indeed fail, but not because there isn't any, and not because it wasn't understood. It will fail because the person doesn't have a wallet. 

For issues like this, Perplexity always tries to behave as a human would. A human would like respond with, "umm, you don't have a wallet". So, we want the subtree "I have cash in my wallet" to fail, but we don't want the failure to be interpreted as proving the fact False because Perplexity would interpret this as: neg(false) == true amd thus "you are correct!", which isn't how a human would respond. The error "formNotUnderstood" is not correct either because we *did* understand it, it just doesn't make sense. We want a way to mark the phrase as "understood, but failed, and not a logical failure." where "not a logical failure" means "don't interpret this failure to mean proving the statement as false".

One way to handle this is to assume that any failure that happens before the verb is processed is non-logical. So, in this case "in(cash, wallet)" would fail before "have(me, cash)", and thus can return the proper error. This allows us to only have to deal with non-logical failures where it is just the verb doing something non-logical.  For example, "I don't have the color green".  In this case, a valid response would be "I don't understand the way you are using 'have'" so returning "formNotUnderstood" is appropriate.

Sometimes it is hard to detect the verb, so instead we will just assume the "last predicate to be run" is the verb, which will be the predication that has the biggest MRS `Index`.

** Non-negateable Predication Failures

Some verbs simply can't, or aren't implemented to work under logical negation. Take "sit".  Imagine that "Let's sit" is implemented by changing the world to have the player and their friend sit down. If the user then says "Let's not sit", then the engine would attempt to solve "neg(Let's sit)" by solving "Let's sit", which would work, and then negating it, which doesn't make any sense.

To stop this from happening, verbs that *do* make sense under logical negation need to mark themselves as "supports_negation=True".

*** Nonsense Failures

From: https://www.cs.utexas.edu/~dnp/frege/subsec-englishvslogic.html

All three of these would be treated as non-logical failures since the failure happens before the verb:

- The sister of our textbook is not walking into class.
- There are no people in 7.
- A serving of pie doesn't have dragon calories.
  - "A serving of pie" would presumably be understood
  - "dragon calories" would fail as "dragon" isn't an adjective that applies
  - Thus, we'd get a non-logical failure

Unfortunately, if since we are operating under an closed-world assumption, this would be "true" since it presumably "Pencils are fond of chocolate" would not be recorded in the system as a fact:
    - Pencils are not fond of chocolate.


*** Vagueness Failures

From: https://www.cs.utexas.edu/~dnp/frege/subsec-englishvslogic.html

- It is not very hot
    Obviously what is "very hot" depends on what you mean by hot and where you are and other context, but this can all be decided by the particular world implementation and the system will handle "not" properly


*** Presupposition Failures
From: https://www.cs.utexas.edu/~dnp/frege/subsec-englishvslogic.html

~~~ 
"The king of France is bald."
Is this sentence true or false? It doesn’t feel false because there is no king of France with hair. But it doesn’t feel true because there is no bald King of France. We could translate this sentence into the following logical claim: 
  -  There is a king of France and that person is bald.

Now we can assign a truth value. This new sentence is clearly false.
~~~

Perplexity doesn't support this kind of presupposition detection and creation in its logic.  It is something you'd have to write yourself.


** Implementing Negatable Predications

Perplexity will automatically handle "not understood", "logical failures" and "nonsense failures" (except when the closed world assumption supports them as described above), as long as you mark predications that can be used as a verb which are logical tests that it makes sense to negate with `handles_negation=True`.

For example:
~~~
@Predication(vocabulary,
             names=["_have_v_1"],
             phrases={
                "Do you have a kitchen?": {'SF': 'ques', 'TENSE': 'pres', 'MOOD': 'indicative', 'PROG': '-', 'PERF': '-'},
                "Do you have this table?": {'SF': 'ques', 'TENSE': 'pres', 'MOOD': 'indicative', 'PROG': '-', 'PERF': '-'},
                "Do I|we have the table?": {'SF': 'ques', 'TENSE': 'pres', 'MOOD': 'indicative', 'PROG': '-', 'PERF': '-'},
                "Do you have a|the steak?": {'SF': 'ques', 'TENSE': 'pres', 'MOOD': 'indicative', 'PROG': '-', 'PERF': '-'},
                "We have 2 menus": {'SF': 'prop', 'TENSE': 'pres', 'MOOD': 'indicative', 'PROG': '-', 'PERF': '-'},
                "I have a son": {'SF': 'prop', 'TENSE': 'pres', 'MOOD': 'indicative', 'PROG': '-', 'PERF': '-'}
             },
             properties={'SF': ['ques', 'prop'], 'TENSE': 'pres', 'MOOD': 'indicative', 'PROG': '-', 'PERF': '-'},
             handles_negation=True)
def _have_v_1_fact_check(context, state, e_introduced_binding, x_actor_binding, x_object_binding):
~~~

Remember that adjectives are modelled as verbs when they are the sole object of "is". For example, "Salad is vegetarian" doesn't get a "be" verb, instead "vegetarian" is treated as the verb and so *it* would need to marked as `handles_negation`.


*** Negation Resources
[English vs Logic](https://www.cs.utexas.edu/~dnp/frege/subsec-englishvslogic.html)
https://www.cs.utexas.edu/~dnp/frege/ambiguity-of-some-logical-operators-negation.html
