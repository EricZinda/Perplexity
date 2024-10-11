{% raw %}## Non-logical Meaning
So far, all the examples we've built have a very "logical" behavior.  They are literally asking about things in the world, possibly in relation to other things. We ask about their existence, where they are, etc.

```
? what file is large?
? a file is large
? where am i
? go to a folder
? students are lifting a table
? which students are lifting the table
```

The system "solves" the MRS by finding variable assignments that make it `true` and then gives built-in answers like "that is true" or lists what was requested.

Next, we are going to walk through how to implement phrases that aren't logical in that same way.  For example, imagine we want to implement a rudimentary help system for our file system example and we'd like users to be able to ask for help using phrases too. To find out what they can do, a user might ask, "Do you have commands?".

Here's a quick overview of how: start by adding the notion of a "command" object into the system, creating one for each of the commands we have so far ("copy" and "go") and implementing the new predications from the MRS, which are `_have_v_1` and `_command_n_1`, as you can see from the MRS:

```
[ "Do you have commands?"
  TOP: h0
  INDEX: e2 [ e SF: ques TENSE: pres MOOD: indicative PROG: - PERF: - ]
  RELS: < [ pron<3:6> LBL: h4 ARG0: x3 [ x PERS: 2 IND: + PT: std ] ]
          [ pronoun_q<3:6> LBL: h5 ARG0: x3 RSTR: h6 BODY: h7 ]
          [ _have_v_1<7:11> LBL: h1 ARG0: e2 ARG1: x3 ARG2: x8 [ x PERS: 3 NUM: pl IND: + ] ]
          [ udef_q<12:21> LBL: h9 ARG0: x8 RSTR: h10 BODY: h11 ]
          [ _command_n_1<12:20> LBL: h12 ARG0: x8 ] >
  HCONS: < h0 qeq h1 h6 qeq h4 h10 qeq h12 > ]

               ┌────── pron(x3)
pronoun_q(x3,RSTR,BODY)            ┌────── _command_n_1(x8)
                    └─ udef_q(x8,RSTR,BODY)
                                        └─ _have_v_1(e2,x3,x8)
```

Once we do that, the interaction will look like this:

```
? Do you have commands?
Yes.

? Which commands do you have?
copy
go
```

You can almost hear the user say "Ugh! Dumb computer" after the first phrase.  A human would interpret that as "Tell me what commands you have, if you have them".  This is known in linguistics as ["Pragmatics"](https://en.wikipedia.org/wiki/Pragmatics). The area of Pragmatics concerns the meaning of phrases that can't be "logically" or "mechanically" interpreted since they require taking into account the context the phrase is uttered in and potentially taking some implied leaps to understand what is actually meant.

Making "Do you have commands?" actually say something custom and not purely give a logical response requires customizing how Perplexity responds when it finds a Solution Group. That is where we'll finish.

# Logical Interpretation

First let's create a `FileCommand` class which represents commands in the system, using the [same pattern](https://blog.inductorsoftware.com/Perplexity/home/pxhowto/pxHowTo082State) we used for the `File` and `Folder` classes:
```
class FileCommand(UniqueObject):
    def __init__(self, name):
        super().__init__()
        self.name = name
        self._hash = hash(self.name)

    def __hash__(self):
        return self._hash

    def __repr__(self):
        return f"Command(name={self.name})"

    def __eq__(self, obj):
        return isinstance(obj, FileCommand) and str(self.name) == str(obj.name)
```

Then, we need to add all the commands in the system to our state object, so they are returned when the system iterates through "all objects in the system" using the `State.all_individuals()` method:

```

class FileSystemState(State):
    def __init__(self, file_system, current_user=None, actors=None):
        super().__init__([])
        self.file_system = file_system
        self.current_user = file_system_example.objects.Actor(name="User", person=1, file_system=file_system) if current_user is None else current_user
        self.actors = [self.current_user,
                       file_system_example.objects.Actor(name="Computer", person=2, file_system=file_system)] if actors is None else actors
        self.commands = [file_system_example.objects.FileCommand("copy"), file_system_example.objects.FileCommand("go")]
       
    def all_individuals(self):
        yield from self.file_system.all_individuals()
        yield from self.actors
        yield from self.commands 
        
    ...
```

With that in place, we implement the predication that is generated when the user utters "command" so the system will be able to fill variables with these objects:

```
@Predication(vocabulary, names=["_command_n_1"])
def _command_n_1(context, state, x_binding):
    def bound_variable(value):
        if isinstance(value, file_system_example.objects.FileCommand):
            return True
        else:
            context.report_error(["valueIsNotX", value, x_binding.variable.name])
            return False

    def unbound_variable():
        for item in state.all_individuals():
            if bound_variable(item):
                yield item

    yield from combinatorial_predication_1(context,
                                           state,
                                           x_binding,
                                           bound_variable,
                                           unbound_variable)
```

And, finally, we can implement the `_have_v_1` predication, so that it is true only for 2nd person phrases like "do you have a command", and so that the only thing anything "has" are commands:

```
@Predication(vocabulary, names=["_have_v_1"])
def _have_v_1(context, state, e_introduced_binding, x_actor_binding, x_target_binding):
    def actor_have_target(item1, item2):
        if isinstance(item2, file_system_example.objects.FileCommand):
            return True
        else:
            context.report_error(["doNotHave", x_actor_binding.variable.name, x_target_binding.variable.name])
            return False

    def all_actors_having_target(item2):
        if False:
            yield None

    def all_targets_had_by_actor(item1):
        if False:
            yield None

    if x_actor_binding.value is not None and len(x_actor_binding.value) == 1 and x_actor_binding.value[0] == Actor(name="Computer", person=2):
        yield from in_style_predication_2(context,
                                          state,
                                          x_actor_binding,
                                          x_target_binding,
                                          actor_have_target,
                                          all_actors_having_target,
                                          all_targets_had_by_actor)

    else:
        context.report_error(["doNotHave", x_actor_binding.variable.name, x_target_binding.variable.name])
        return False
        
```

With that code, we can now make the first phrases work:

```
? do you have commands?
Yes.

? which commands do you have?
(Command(name=copy),)(Command(name=go),
```

# Pragmatic Interpretation
As described in the [Solution Group Algorithm topic](https://blog.inductorsoftware.com/Perplexity/home/devcon/devcon0040MRSSolverSolutionGroupsAlgorithm), by default, when a solution group is found for a phrase, and the phrase is a yes/no question, Perplexity responds with "Yes." To give a different response, we need to customize the way the system handles solution groups for this case.

To do this, we implement a *solution group handler*. It looks very much like the `have_v_1` handler above, with a few differences:
```
@Predication(vocabulary,
             names=["solution_group__have_v_1"])
def _have_v_1_group(context, state_list, e_introduced_binding_list, x_actor_variable_group, x_target_variable_group):
    yield state_list
```

First, instead of using "*have_v_1" as the name, we prefix the name with "solution_group*" and use "solution_group__have_v_1" as the name. This tells the system we are implementing a solution group handler.

It has the same number of arguments as the "have_v_1" function, but, because this is handling a solution *group*, the arguments contain multiple items instead of one: one item for each solution in the group.

Implementing a solution group handler allows you to inspect each solution group that Perplexity finds and write custom logic to invalidate it or respond differently than the system would.  Yielding a list of state objects from the solution group handler indicates that this list of state objects is a valid solution group.  If nothing is yielded, the incoming list of state objects is invalidated and Perplexity continues looking for alternative solution groups.

As written in the code above, the Perplexity behavior won't change since the code simply yields the solution group, as is. This indicates it is a valid solution group. Since the code doesn't do anything to respond in a custom way, Perplexity continues responding with its default behavior.

If we want a different response, we could start by doing this:

```
@Predication(vocabulary,
             names=["solution_group__have_v_1"])
def _have_v_1_group(context, state_list, e_introduced_binding_list, x_actor_variable_group, x_target_variable_group):
    new_solution_group = [state_list[0].record_operations([RespondOperation("You can use the following commands: 'copy' and 'go'.")])]
    yield new_solution_group
```

Instead of yielding the original solution group, we now are only yielding the first solution ... after modifying it to include a built-in operation called `RespondOperation`.  This is just like the [`DeleteOperation`](https://blog.inductorsoftware.com/Perplexity/home/pxhowto/pxHowTo070ActionVerbs) we created in an earlier section, but this operation's job is to print text for the user.  Putting a `RespondOperation` in any of the state objects we yield tells the system that we want to override the default output.  

So, now we get this:

```
? Do you have commands?
You can use the following commands: copy and go

? Which commands do you have?
You can use the following commands: copy and go
```

Because we are overriding the output, it really doesn't matter that we are changing the list of state objects in the solution group. Since they were only used to generate the default output, Perplexity won't pay attention to them anymore. Obviously we could instead run code to look up the commands in the system and dynamically build the string instead of hard coding it.

# Concepts
While that works, it seems inefficient to have to create `FileCommand` objects, implement them in several places, have Perplexity go through the process of solving the MRS, only to throw it all way and print out a custom message! It turns out that work was not wasted. It would be required for other phrases like "Do you have a 'copy' command?" and many other scenarios.  But: it really is unnecessary to build up a solution group with all the commands to only throw it away for *this* scenario.

Instead, we can use another Perplexity feature called a "Concept" to make it more efficient.  The idea is that, sometimes, instead of Perplexity assigning actual objects to variables, we'd like the "concept" of them (called a [`referring expression`](https://en.wikipedia.org/wiki/Referring_expression) in linguistics) to be assigned.  I.e. instead of assigning `x8 = FileCommand('copy')`, we'd like to have `x8 = {representation of whatever they said before it got resolved into an actual object}` so that we can look at what they said "conceptually" instead of dealing with the actual instances of objects that it generated. This allows the solution group handler to just see if they are were talking about "you" having "the concept of commands" and, if so, generate the custom text.  This would be much more efficient.

To do this, we start adding an alternative `_command_n_1` predication since that is where the instances of commands get generated.  Perplexity allows adding more than one *interpretation* of a predication by creating more than one function and indicating that they use the same predication name. It treats them as *alternatives* and attempts to solve the MRS once using the first interpretation and then again using the next. 

In the new interpretation, instead of yielding instances, we yield a `Concept("command")` object.  The `Concept` object in Perplexity literally does nothing except tell the system it is an opaque "Concept" object.  Here are both interpretations:

```
@Predication(vocabulary, names=["_command_n_1"])
def _command_n_1_concept(context, state, x_binding):
    def bound_variable(value):
        if isinstance(value, Concept) and value == Concept("command"):
            return True
        else:
            context.report_error(["valueIsNotX", value, x_binding.variable.name])
            return False

    def unbound_variable():
        yield Concept("command")

    yield from combinatorial_predication_1(context,
                                           state,
                                           x_binding,
                                           bound_variable,
                                           unbound_variable)
                                           
                                               
@Predication(vocabulary, names=["_command_n_1"])
def _command_n_1(context, state, x_binding):
    def bound_variable(value):
        if isinstance(value, file_system_example.objects.FileCommand):
            return True
        else:
            context.report_error(["valueIsNotX", value, x_binding.variable.name])
            return False

    def unbound_variable():
        for item in state.all_individuals():
            if bound_variable(item):
                yield item

    yield from combinatorial_predication_1(context,
                                           state,
                                           x_binding,
                                           bound_variable,
                                           unbound_variable)
```
With that in place, we'll first get a set of solution groups that have the `Concept("command")` object assigned to variables. Perplexity will do nothing with the `Concept` object except recognize that it is one and disable its logic to do any [collective/cumulative/distributive](https://blog.inductorsoftware.com/Perplexity/home/devcon/devcon0030MRSSolverSolutionGroups) solution group testing.  Instead, it will still create *all potential* solution groups and call your solution group handler.  It is now up to you to decide if they are valid readings. For this case it will be simple since we are going to treat any phrase of the form "Do you have {x} commands?" as a request to see the help string. That includes any of these:

```
Do you have commands?
Do you have 2 commands?
Do you have several commands?
Do you have any commands?
etc.
```

Next, recall that the implementation of `_have_v_1` only succeeds if the arguments are of type `FileCommand`:

```
**@Predication(vocabulary, names=["_have_v_1"])
def _have_v_1(context, state, e_introduced_binding, x_actor_binding, x_target_binding):
    def actor_have_target(item1, item2):
        if isinstance(item2, file_system_example.objects.FileCommand):
            return True
        else:
            context.report_error(["doNotHave", x_actor_binding.variable.name, x_target_binding.variable.name])
            return False

    ...
    
    if x_actor_binding.value is not None and len(x_actor_binding.value) == 1 and x_actor_binding.value[0] == Actor(name="Computer", person=2):
        yield from in_style_predication_2(context,
                                          state,
                                          x_actor_binding,
                                          x_target_binding,
                                          actor_have_target,
                                          all_actors_having_target,
                                          all_targets_had_by_actor)**

    else:
        context.report_error(["doNotHave", x_actor_binding.variable.name, x_target_binding.variable.name])
        return False                                       
```

This means it will fail when Perplexity attempts to solve it using the new `Concept` object.  So, we need a new interpretation of `_have_v_1` as well:

```
@Predication(vocabulary, names=["_have_v_1"])
def _have_v_1_concept(context, state, e_introduced_binding, x_actor_binding, x_target_binding):
    def actor_have_target(item1, item2):
        if isinstance(item2, Concept) and item2 == Concept("command"):
            return True
        else:
            context.report_error(["doNotHave", x_actor_binding.variable.name, x_target_binding.variable.name])
            return False

    def all_actors_having_target(item2):
        if False:
            yield None

    def all_targets_had_by_actor(item1):
        if False:
            yield None

    if x_actor_binding.value is not None and len(x_actor_binding.value) == 1 and x_actor_binding.value[0] == Actor(name="Computer", person=2):
        yield from in_style_predication_2(context,
                                          state,
                                          x_actor_binding,
                                          x_target_binding,
                                          actor_have_target,
                                          all_actors_having_target,
                                          all_targets_had_by_actor)

    else:
        context.report_error(["doNotHave", x_actor_binding.variable.name, x_target_binding.variable.name])
        return False
```

Finally, we want to change our solution group handler to only be used when the conceptual interpretation is used. We'll let perplexity handle the original interpretation. To do this, we set the `handles_interpretation` argument of the `Predication` class to point to the interpretation we want to pair it with, like this:

```
@Predication(vocabulary,
             names=["solution_group__have_v_1"],
             handles_interpretation=_have_v_1_concept)
def _have_v_1_group(context, state_list, e_introduced_binding_list, x_actor_variable_group, x_target_variable_group):
    yield [state_list[0].record_operations([RespondOperation("You can use the following commands: copy and go")])]
```

Now, we can try all the phrases below:

```
? which commands do you have?
You can use the following commands: copy and go

? do you have a command?
You can use the following commands: copy and go

? do you have 2 commands?
You can use the following commands: copy and go

? do I have a command?
you do not have a command

? do I have a file?
you do not have a file

? do you have a file?
us do not have a file
```

Note that all of those phrases end up using the conceptual interpretation. Our instance-based interpretation is currently unused. The most likely use for it would be for phrases like "Do you have a copy command?" or "How do I use the copy command?", i.e. in phrases where the user is talking about a particular instance, and not the general concept of commands. 

Also note that there also a whole set of phrases that happen to work that probably shouldn't:

```
? did you have a command?
You can use the following commands: copy and go

? you are having a command?
You can use the following commands: copy and go

? Are you having a command?
You can use the following commands: copy and go
```

Let's tackle tenses next.

Last update: 2024-10-11 by Eric Zinda [[edit](https://github.com/EricZinda/Perplexity/edit/main/docs/pxHowTo/pxHowTo100NonlogicalMeaning.md)]{% endraw %}