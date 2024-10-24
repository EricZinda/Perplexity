## Solution Group Handlers and Global Criteria
In the [previous section](pxHowTo100NonlogicalMeaning) we implemented variations of "Do you have commands?" by implementing a custom *solution group handler*, but we didn't complete it.  Since there are only two commands, we should do a better job on the following phrases that succeed, and shouldn't:

~~~
? Do you have 3 commands?
You can use the following commands: copy and go

? Do you have many commands?
You can use the following commands: copy and go

? Do you have several commands?
You can use the following commands: copy and go

? Do you have the command?
You can use the following commands: copy and go
~~~

All of these phrases are using words like "several" or "3" which quantify how many of something the speaker is interested in. The last uses "the" which implies there is just one that is so obvious the system should know which one it is. When we implement a solution group handler we take over responsibility for doing the counting, and we're not doing that.

### Inspecting Global Criteria
When a speaker uses a phrase that constrains the solution group using numeric constraints or "the", these constraints are tracked with the arguments in the solution group handler and can be inspected:

Let's change our `have_v_1` solution group handler to output these constraints so we can see them:

~~~
@Predication(vocabulary,
             names=["solution_group__have_v_1"],
             handles_interpretation=_have_v_1_concept)
def _have_v_1_group(context, state_list, e_introduced_binding_list, x_actor_variable_group, x_target_variable_group):
    print(f"x_actor_binding constraints: {x_actor_variable_group.variable_constraints}")
    print(f"x_target_binding constraints: {x_target_variable_group.variable_constraints}")
    yield [state_list[0].record_operations([RespondOperation("You can use the following commands: copy and go")])]
~~~

And then run it:

~~~
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
~~~

You can see from the output that the constraints on `x3`, which is where "you" is represented, are between 1 and `inf` (infinity):

~~~
x_actor_binding constraints: {x3: min=1, max=inf, global=None, required_values=None, pred=pronoun_q(x3)}
~~~

That's because, if you look at the MRS, `x3` doesn't indicate one way or the other if "you" is plural or singular "you", and there aren't any other predications that would constrain things.

For `x8` we get a constraint between 2 and infinity.  Looking at the MRS you can see that `x8` has the properties `[ x PERS: 3 NUM: pl IND: + ]` set in the `have_v_1` predication, which indicates plurality.  I.e. between 2 and infinity:

~~~
x_target_binding constraints: {x8: min=2, max=inf, global=None, required_values=None, pred=udef_q(x8)}
~~~

Running this:

~~~
? Do you have 3 commands
x_actor_binding constraints: {x3: min=1, max=inf, global=None, required_values=None, pred=pronoun_q(x3)}
x_target_binding constraints: {x8: min=3, max=3, global=None, required_values=None, pred=card(3)}
You can use the following commands: copy and go
~~~

Shows how, if the speaker says "3", the constraints are set to a min and max of "3".

Let's try:

~~~
? Do you have the command?
x_actor_binding constraints: {x3: min=1, max=inf, global=None, required_values=None, pred=pronoun_q(x3)}
x_target_binding constraints: {x8: min=1, max=1, global=GlobalCriteria.all_rstr_meet_criteria, required_values=None, pred=_the_q(x8)}
You can use the following commands: copy and go
~~~

The word "the" means "the one and only" or "the 1 group" and so it has a min/max of 1 and it has `global=GlobalCriteria.all_rstr_meet_criteria`. `all_rstr_meet_criteria` is how "the 1 group" gets handled.  It means: all of the things that "the" refers to in its `RSTR` must be true of its `BODY`. Let's look at the MRS tree to understand:

~~~
               ┌────── pron(x3)
pronoun_q(x3,RSTR,BODY)            ┌────── _command_n_1(x8)
                    └─ _the_q(x8,RSTR,BODY)
                                        └─ _have_v_1(e2,x3,x8)
~~~

Since `all_rstr_meet_criteria` is set on `x8`, it is referring to the `RSTR` and `BODY` of: `_the_q(x8,RSTR,BODY)`.

The `RSTR` is simply `_command_n_1(x8)`, so *all* commands in the system are being referred to.  The `BODY` is set to `_have_v_1(e2,x3,x8)`.  So, as long as "you" have "all" the commands in the system, this should be true.

What about "The commands are copy".  This would put "all commands" in the `RSTR` and "being copy" in the `BODY` which is certainly not true for all of them, so it should fail.

What about this:

~~~
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
~~~

This one says `x8` which is `_the_q(x8,RSTR,BODY)` must have 3 different values in it. And: all commands in the system should be true of the body. While it is certainly true that the system "has" all the commands, it is not true that there are 3 of them, so this is false.

Normally, Perplexity handles checking these constraints and doesn't consider a solution group to be valid unless it meets them all. But when you build a solution group handler, you are telling the system: I am doing something custom with the solution group and thus I will also be responsible for making sure the constraints are met on it.

### Different Interpretations of Constraints
To determine if constraints are met, you first need to make a decision about what the speaker meant by the phrase. This isn't always obvious. Consider the following phrases:

> Do you have more than 2 chairs?

If Aiden walks into an office and is looking for a place to sit, he is probably asking about *instances* of chairs.

If Aiden walks into a furniture store wanting to buy a chair, he is probably asking about *types* of chairs ... unless he's been talking the salesman about a particular type and is wondering how many they have in stock.

> Do you have the steak?

If Elie is talking to a waiter and there is often a steak special, she probably means "is the *conceptual type* of steak you usually have on the menu today?".

If instead she is talking to her friend about a particular steak he bought, she probably means the *instance*.

> Do you have two menus?

If Zahra is in a restaurant that has several types of menus, maybe for lunch and dinner, she might be referring to *types* of menus.

She could also mean "one menu for me and one for my Mom".

What these all have in common is that hints about what the speaker means can be found in the *context*, or scenario, that is occurring. It is often not obvious which is meant a priori. So, you'll need to determine which is meant given your scenario. Note that you can also implement both as different *interpretations* and try each to see which works, or reorder them based on the current context.  You may also decide that the constraint doesn't matter. If there are no steaks available in your vegetarian restaurant just about any question about a steak should be met with, "I'm so sorry, we don't have those here."

### The `concept_meets_constraint` Helper
Regardless of which you decide, you need to write the code to make sure the constraints are met.  As shown above, the constraints are available in the `variable_constraints` property of each variable group in your solution group handler. That code is repeated below:

~~~
@Predication(vocabulary,
             names=["solution_group__have_v_1"],
             handles_interpretation=_have_v_1_concept)
def _have_v_1_group(context, state_list, e_introduced_binding_list, x_actor_variable_group, x_target_variable_group):
    print(f"x_actor_binding constraints: {x_actor_variable_group.variable_constraints}")
    print(f"x_target_binding constraints: {x_target_variable_group.variable_constraints}")
    ...
    
? do you have commands
x_actor_binding constraints: {x3: min=1, max=inf, global=None, required_values=None, pred=pronoun_q(x3)}
x_target_binding constraints: {x8: min=2, max=inf, global=None, required_values=None, pred=udef_q(x8)}
~~~

However, very often you'll just need to decide if the intended meaning is about concepts or instances and want to see if the concepts and instances in the solution group match them. If your solution group is dealing with *concepts* in the variable (which is most commonly why you'd create a solution group), you can use a Perplexity function called `concept_meets_constraint`. This function checks a particular concept-valued variable to see if it meets the global constraints. Let's go through the implementation of this function to see how it works.

The function assumes the variable in question contains *concepts* and requires that you give it some information about the concepts in the solution group, as well as some information about the world the phrase was uttered in. Let's go through the incoming arguments first:
~~~
def concept_meets_constraint(context, 
                             tree_info, 
                             variable_constraints, 
                             concept_count, 
                             concept_in_scope_count, 
                             instance_count, 
                             check_concepts, 
                             variable):
    ...
~~~

The first two arguments are the `context` and `tree_info` from the solution group handler which can be retrieved like this:

~~~
@Predication(vocabulary,
             names=["solution_group__have_v_1"],
             handles_interpretation=_have_v_1_concept)
def _have_v_1_group(context, state_list, e_introduced_binding_list, x_actor_variable_group, x_target_variable_group):
        success = concept_meets_constraint(context,
                                           state_list[0].get_binding("tree").value[0]
                                           ...
~~~

`concept_count` refers to the number of different concepts that are in this variable in the solution group.  To gather the different concepts in a variable like `x_target`, we can use a Python `set` object like this:

~~~
def _have_v_1_group(context, state_list, e_introduced_binding_list, x_actor_variable_group, x_target_variable_group):
    target_concepts = set([x.value for x in x_target_variable_group.solution_values])
    target_concept_count = len(target_concepts)
~~~

We use a set because we want *unique* concepts. The solution group may have several solutions that have the same concept and we only want to count that as a single concept.

The next argument is `concept_in_scope_count`. In Perplexity, "in-scope concepts" are how you indicate how many of the set of concepts you just gathered are "in-scope", meaning that there is a particular concept that it would be appropriate to say "the" with.  Some examples:

- "Please give me the menu": there is "one menu" that they are obviously referring to
- "Where are the girls?": there are a particular set of girls that we are talking about
- "Do you still have the chair"

etc.

How you decide which concepts make sense to be "in-scope" is up to you, but is obviously very context dependent. If you have a function that determines it based on the state of the world, you'd do something like this:

~~~
    concept_in_scope_count = 0
    for concept in target_concepts:
        if in_scope(context, state, concept):
            concept_in_scope_count += 1
~~~

`instance_count` refers to how many *instances* of those concepts are in the world.  This is used for phrases like "Do you have 2 chairs?" interpreted as the user referring to instances (not types of) chairs.  So, you need a way to find out how many instances there are for all the concepts in the solution group.  Below we use an ".instances()" method of `Concept` which you'll need to implement to generate the instances based on how you've implemented your `Concept` object:

~~~
    instances = []
    for concept in concepts:
        this_concept_instances = list(concept.instances(context, state))
        # If we are dealing with instances and one of the concepts generates 
        # zero, we don't want to just count the others
        # and succeed.  e.g. "I have two ice creams and bowls" should not 
        # succeed if there are no bowls
        if len(this_concept_instances) == 0:
            instances = None
            break

        instances += this_concept_instances
    if instances is None:
        # We can fail immediately
        return
    else:
        instance_count = len(instances)
~~~

`check_concepts` is `True` if you are interpreting the criteria as counting concepts, otherwise instances are checked.

`variable` is the final argument, and is simply the name of the MRS variable being checked.

Now that we've seen all the arguments, here they are all together being used to check for an interpretation where the speaker is asking about having the concept of, not instances of, something. For example, "Do you have specials?". Since the implementation of most of this depends on your implementation, it isn't a library function. However, it will be the same for most of your predications so you can create one of your own:

~~~
@Predication(vocabulary,
             names=["solution_group__have_v_1"],
             handles_interpretation=_have_v_1_concept)
def _have_v_1_group(context, state_list, e_introduced_binding_list, x_actor_variable_group, x_target_variable_group):
    # Count the concepts
    target_concepts = set([x.value for x in x_target_variable_group.solution_values])
    target_concept_count = len(target_concepts)
    
    # Count the in-scope concepts
    concept_in_scope_count = 0
    for concept in target_concepts:
        if in_scope(context, state, concept):
            concept_in_scope_count += 1

    # Count the instances
    instances = []
    for concept in concepts:
        this_concept_instances = list(concept.instances(context, state))
        # If we are dealing with instances and one of the concepts generates 
        # zero, we don't want to just count the others
        # and succeed.  e.g. "I have two ice creams and bowls" should not 
        # succeed if there are no bowls
        if len(this_concept_instances) == 0:
            instances = None
            break

        instances += this_concept_instances
        
    if instances is None:
        # We can fail immediately
        return
    else:
        instance_count = len(instances)
    
    success = concept_meets_constraint(context=context,
                                       tree_info=state_list[0].get_binding("tree").value[0],
                                       variable_constraints=x_target_variable_group.variable_constraints,
                                       concept_count=target_concept_count,
                                       concept_in_scope_count=concept_in_scope_count,
                                       instance_count=instance_count,
                                       check_concepts=True,
                                       variable=x_what_variable_group.solution_values[0].variable.name)
    
    if success:
        # Your custom code here
~~~

### The `concept_meets_constraint` Implementation
Now let's go through how `concept_meets_constraint` uses these arguments to check if a solution group meets its constraints. It is useful to understand since you may need different logic for some of your predications. This function just implements the most common behavior.

First, default `min` and `max` constraints are filled in the the variable doesn't have them. Then, it branches based on whether the caller asked to check concepts or instances.  First let's do concepts.  The comments in the code describe what is happening:

~~~
def concept_meets_constraint(context,
                             tree_info,
                             variable_constraints,
                             concept_count,
                             concept_in_scope_count,
                             instance_count,
                             check_concepts,
                             variable):
    min_size = variable_constraints.min_size if variable_constraints is not None else 1
    max_size = variable_constraints.max_size if variable_constraints is not None else float(inf)
    
    if check_concepts:
        # We are making sure the constraints succeed against the concept count
        if variable_constraints is not None and variable_constraints.global_criteria == perplexity.plurals.GlobalCriteria.all_rstr_meet_criteria:
            # If the user says "the specials" or "the 2 menus" they are putting a criteria
            # on the *concept*, not the instances. I.e. there should be
            # 2 *types* of menus in scope. Examples:
            #
            # "Do you have the 2 menus?" (interpreted as meaning classes of menus)
            # "Are the 2 specials good?" (ditto)
            # "Do you have the steak?" (ditto)
            #
            # Furthermore, because they said "the", they are referring to a "in-scope concept", 
            # i.e. "the menu", not just any old menu. It is a special one. This is modelled as 
            # having the concept be "in scope". The generic type, "menu" still exists, but is
            # a type that is out of scope. If they said "What is generally on a menu?" they'd
            # be referring to that generic type.
            check_count = concept_in_scope_count

        else:
            # The user didn't say "the", so the concept doesn't need to be "in-scope" and so
            # they are talking about the generic type (as described above). Examples:
            #
            # "How many specials do you have?" (meaning classes of specials)
            # "Are 2 specials available" (ditto)
            # "What chairs do you have?" (ditto)
            # "specials are cheaper" (ditto)
            # "Are specials available?" (ditto)
            # "Can I get a table?" (ditto)
            check_count = concept_count

        if check_count == 0:
            introducing_predication = perplexity.tree.find_quantifier_from_variable(tree_info["Tree"], variable)
            context.report_error(["phase2ZeroCount", ["AtPredication", introducing_predication.args[2], variable]], force=True, phase=2)
            return False

        if check_count < min_size:
            context.report_error(["phase2LessThan", ["AfterFullPhrase", variable], min_size], force=True, phase=2)
            return False

        elif check_count > max_size:
            context.report_error(["phase2MoreThanN", ["AfterFullPhrase", variable], max_size], force=True, phase=2)
            return False

        return True
    
    ...
~~~

The real work for checking concepts is to decide whether the word "the" has been used. This determines whether we check the "in-scope concept" count or just the "concept count".  The rest of the code is just comparing the resulting number to the `min` and `max` sizes and reporting an error if it isn't in range.

The second part of the function gets run when `check_concepts=False`. In this case, the speaker is talking about a concept, but the ultimate thing that needs to be manipulated is an instance.  E.g. to implement "I want a menu", our code will need to find a menu and give it to the speaker. 

Here again the only subtlety is dealing with "the" and making sure we interpret phrases like, "give me the two menus" properly. Even if they are ultimately wanting instances, "the two menus" will need to be checked to make sure that we actually do have two *types* of menu, so that we can then give them both.

~~~
def concept_meets_constraint(context,
                             tree_info,
                             variable_constraints,
                             concept_count,
                             concept_in_scope_count,
                             instance_count,
                             check_concepts,
                             variable):
    
    ...
    
    else:
        # The user is talking about a concept, but, ultimately, our code will need to check if there are 
        # enough instances. Examples:
        #   "We want a menu" --> "We want 1 instance of a menu concept"
        #   "We want a table" --> "We want 1 instance of a table concept"
        #   "We want tables/menus" --> "We want instances of the tables"
        #   "We want the menu(s)" --> "We want an undefined number of instances of 
        #                             'the one and only table concept in scope'"
        #   "We want the specials" --> "We want an undefined number of instances of 
        #                              'the (undefined number of) the special concepts in scope'"
        #
        # First, check to make sure we the system has the right number of "in scope" concepts if "the" is used,
        # as in "I'd like the 2 menus" (if there are a drink menu and a food menu)
        if variable_constraints is not None and variable_constraints.global_criteria == perplexity.plurals.GlobalCriteria.all_rstr_meet_criteria:
            check_count = concept_in_scope_count
            if check_count == 0:
                context.report_error(["conceptNotFound", variable], force=True, phase=2)
                return False

            if check_count < min_size:
                context.report_error(["phase2LessThan", ["AfterFullPhrase", variable], min_size], force=True, phase=2)
                return False

            elif check_count > max_size:
                context.report_error(["phase2MoreThanN", ["AfterFullPhrase", variable], max_size], force=True, phase=2)
                return False

        # Then, regardless of whether "the" was used, check to make sure there are enough instances to 
        # meet the criteria since that is what we are ultimately looking for
        check_count = instance_count
        if check_count == 0:
            context.report_error(["conceptNotFound", variable], force=True, phase=2)
            return False

        if check_count < min_size:
            context.report_error(["phase2LessThan", ["AfterFullPhrase", variable], min_size], force=True, phase=2)
            return False

        # As long as the instances are >= min_size, we are good because the caller is responsible
        # for limiting the number of instances being dealt with.
        # For example: "We'd like a table for 2". If there are 20 tables, the caller
        # is responsible for giving only 1
        return True
~~~

### Actually Doing Something
The work to *actually do something* in the system was not covered above.  We walked through how process a phrase like "Give me a menu" by interpreting it as a "Conceptual" menu and building a solution group handler in the section on [implementing non-logical meaning](pxHowTo100NonlogicalMeaning), and then checking global constraints in the description above. Once all that succeeds, you still need to *do the thing*.  

How to do that is up to you.  

> Comprehensive source for the completed tutorial is available [here](https://github.com/EricZinda/Perplexity/tree/main/samples/hello_world)
