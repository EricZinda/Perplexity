Talk: ?Beyond Individuals?
    - concepts
        - entailment
        - inductive logic
        - Handling of "not"
            - What does it mean to be "not soup" for a particular interpretation of "be_v" since some are pragmatic and not logical?

    - pragmatics
    - interpretation and disjunction
Basic approach:
- Have is best example
  - "What tables do you have?" --> request for more than one table
  - "What table do you have?" --> just a single table
  - "What do you have?" --> request for a menu
  - "Do you have a steak?"
  - "Do you have a menu?"
  - "Do you have 2 menus?" --> implies one for each of us
  - Ditto for "Do you have menus", but that could also mean "just one for me"
- "What is not soup" is a good example:
  - which_q(x3,thing(x3),neg(e10,udef_q(x9,_soup_n_1(x9),_be_v_id(e2,x3,x9))))
    - Because it is running under negation, it does not use unbound arguments
- be_v_id is a good example now
- Only handle one interpretation per solution/group handler pair to reduce cognitive load
- decide if you are going to deal with the instance or concept space
- if instance:
  - upside is the engine will give you all the solution groups that are valid and you choose
  - downside is that it could be very slow due to combinatorics
- if concept:
  - upside is there will (probably) be way fewer concepts and be faster
  - downside is you need to check the global criteria yourself.  I.e. "I want steaks" -- you need to understand what
    the criteria are and what they mean in the scenario
    - This is a big downside because it is quite complex



I ordered 2 steaks will generate:
    - ordered(I, steak) with a global constraint of 2
I ordered 2 steaks and 2 salads will generate:
    - ordered(I, steak) 
    - ordered(I, salad) 
    - Count the instances of steak that I ordered and ditto for salad and compare to global criteria

## I want chicken
Let's go through an example. Here's one MRS and tree for "I want chicken":

~~~
Sentence Force: prop
[ "I want chicken"
  TOP: h0
  INDEX: e2 [ e SF: prop TENSE: pres MOOD: indicative PROG: - PERF: - ]
  RELS: < [ pron<0:1> LBL: h4 ARG0: x3 [ x PERS: 1 NUM: sg IND: + PT: std ] ]
          [ pronoun_q<0:1> LBL: h5 ARG0: x3 RSTR: h6 BODY: h7 ]
          [ _want_v_1<2:6> LBL: h1 ARG0: e2 ARG1: x3 ARG2: x8 [ x PERS: 3 NUM: sg ] ]
          [ udef_q<7:14> LBL: h9 ARG0: x8 RSTR: h10 BODY: h11 ]
          [ _chicken_n_1<7:14> LBL: h12 ARG0: x8 ] >
  HCONS: < h0 qeq h1 h6 qeq h4 h10 qeq h12 > ]

               ┌────── pron(x3)
pronoun_q(x3,RSTR,BODY)            ┌────── _chicken_n_1(x8)
                    └─ udef_q(x8,RSTR,BODY)
                                        └─ _want_v_1(e2,x3,x8)
~~~

Let's imagine our restaurant has a few chicken thighs in the kitchen and we say to the waiter, "I want chicken". The tree will be evaluated and `_chicken_n_1(x8)` will set `x8` to be every instance of a thing that is "chicken" in the world. I.e. `x8=thigh1` then `x8=thigh2` and so on. By the time `_want_v_1(e2,x3,x8)` gets evaluated, its filled in arguments will look something like `want_v_1(e2, "me", "thigh1")` or in plain English: "I want thigh1". If that's all that gets generated, we don't have a way to represent "I want (conceptual) chicken (and I don't care which specific one it is)".  To properly handle this, we need to discuss the Perplexity notion of a "Concept". 

The `Concept` object records the "class of thing" a referring expression referred to so the *idea* (as opposed to an *instance*) can be manipulated.  Outside of further refining them with more criteria, there are only two things you can do with a `Concept` object: ask it to enumerate instances (i.e. instances of it in the world) or enumerate more concepts that it entails (i.e. a `carrot` concept is entailed by a `vegetable` concept). 

Instances of chicken like "thigh1" are certainly chicken, as are concepts like `Concept(chicken)`.  Thus, both are `true` when set to `x` in `chicken_n_1(x)`, and both are valid solutions.  The solver will generate solution groups with either instances or concepts in every variable of an MRS (but never both in the same variable). This happens because there are two Python implementations of `_chicken_n_1` (literally two Python methods marked as handling `chicken_n_1`). One returns only concepts, the other returns only instances.  Whichever is first in the Python file returns its objects first.  

If the concepts method is first, when the user says "I want chicken", we would get solution groups that look like this:
~~~
Solution Group 1:
x3=Concept(me), x8=Concept(chicken)

Solution Group 2:
x3=me, x8=Concept(chicken)

Solution Group 3:
x3=Concept(me), x8=thigh1

Solution Group 4:
x3=me, x8=thigh1

...
~~~

Solution Group 2 has `want_v_1(e2, me, Concept(chicken))`, "I want the concept of chicken"

Solution Group 4 has `want_v_1(e2, me, thigh1)`, "I want chicken thigh 1"

Both of these are valid ways to interpret the phrase "I want chicken" so they are both returned as solution groups -- i.e. solutions to the MRS.  The application code needs to decide which is the right interpretation in the current context and decide what to do about it.

## What do we have to work with: Operations on Concepts
A `Concept` object can return all of its instances in the world, as well as all of the `Concept` objects that it entails.  For example, `Concept(vegetable)` might return `Concept(carrot)` and `Concept(pea)` (because each is a vegetable concept) .  Note, however, that the conceptual space is much slipperier that the instance space.  The way the developer might have divided up the concept hierarchy could be arbitrary so, unless the concept model is known up front, it could be tricky to work with.  For example, a restaurant scenario might choose to have these concepts:

1.    special
      |
2.    soup            salad
      |       |       |            |
3.    lentil  tomato  green salad  beet salad

Answering the question "what are your specials?" by asking `Concept(special)` to enumerate *all* the concepts it entails would get you this list: `soup`, `salad`, `lentil soup`, `tomato soup`, `green salad`, `beet salad`, which would be a weird way to answer the question.

It is safer to check if an instance "is" a known concept than to hope the entailed concepts match the hierarchy you are expecting.

For this discussion, let's assume we have implemented all the predications required to convert any possible referring expression into instances or concepts. So, the criteria encoded in the concept object can be *arbitrarily* complex -- it really isn't feasible to somehow inspect the object to see what its criteria is and determine what it will do.  We can only run it and see what it does: i.e. ask it to produce the instances or concepts that it entails.

Since instances refer to real things in the world, they can be compared with ==.  We assume there is always a way to see if two objects refer to the same thing.

Concepts can also be compared with ==, and those that have identical criteria will be == and return the same instances and entailed concepts if asked.  However, note that you could have two Concepts that do *not* compare == but which *do* return the same concepts and instances (or maybe an intersecting set).  For example, Concept("braised chicken") and Concept("The forth thing on the menu") (assuming the forth thing on the menu is braised chicken).  The only way, in the most general case, of seeing if they return the same concepts and instances it to literally enumerate them.  Obviously that will only be true in the current world.  It might not be true 5 minutes from now.

Entailment by Induction: Given a referring expression, iterate through the instances it generates. If *all* of them (requires exhaustively listing them) are also returned by set Y, then set Y entails them.


## Algorithm for "I want x"
If someone says "I want X", how do we know to interpret it as something to put on their order? What if they said:

1) "I want [a table]"
2) "I want [a clean table]"
3) "I want [a place to sit]"
4) "I want [a table that is occupied]"  
5) "I want [that one table that those people are sitting at]"
6) "I want [something that is not a table]"
7) "I want [a bathroom]"
8) "I want [a good time]"
9) "I want [to be a better person]"

If the user asks for anything entailed by "I want an available table in this restaurant", they are asking to be seated at a table. Cases 1, 2 and 3 above are all good examples of different ways to say it.  We can use Entailment By Induction (from above) to see if any given referring expression entails "available table in this restaurant": If all instances generated are "an available table in this restaurant" then we can assume the concept entails it, and thus the user is asking to be seated at a table.

All the rest of the cases above would not be entailed by "an available table in this restaurant". If our software really only knows how to seat people, then we could simply respond with "I'm sorry, I can only seat people."  Or, we could work through the other cases by implementing them the same way:
- If the expression is entailed by "table that is occupied", say "I'm sorry, we can only seat you at open tables"
- If the expression is entailed by "a location in the restaurant", give directions
- etc.

[TODO: Note that we can see if the concepts entailed are ones we understand (Concept(table)) and shortcut the process for performance reasons.]

## Implementation of "I want x"
So, if someone says "I want x", solution groups will be created where:
- `x` contains all the concepts entailed by that concept
- `x` contains a Concept that represents the referring expression
- and finally all the instances that these concepts would generate if asked.

The simplest thing we can do is to see if a given assignment of `x` to a concept == any concept on the menu.  If it does, then clearly that was one valid interpretation of what they said.  This works great for "I want [a steak]" or "I want [the lovely chicken that you make]" if these only return a single concept.  Something like "I want [something that is not chicken]" is going to literally return every other concept in the world, except chicken!

Note that, for any given referring expression, we will get one solution group that has the most general concept, by itself (i.e. Concept([something that is not chicken])), and then other solution groups that have concepts that are more specific.  (Note that a simpler phrase that has the same problem is "I want a menu item" or "I want a vegetarian item")
- It will start by providing a solution group that has one concept that is "not chicken" at a time.
- Finally, it will just give the Concept([something that is not chicken]) as its own solution group

So, we could examine the most general Conceptual solution group and see if it only generates a single menu concept.  If not, we could say "Hmm, could you be more specific?" or "Which of these would you like: a, b, c, etc?"  So, for `_want_v_1`, we will always *only* evaluate the most general Concept and fail the rest.


## I want a table
"I want [a table]"
"I want [a clean table]"
"I want [a table that is occupied]"  
"I want [something that is not a table]"
"I want [a place to sit]"
"I want [a bathroom]"
"I want [a good time]"

Just like menu items, we will treat tables as commodities, meaning we assume they are all identical *except* for whether they are occupied or not.  Just like instances of a given menu item are all the same *except* for whether it has already been given to someone or not.

So, we do a similar thing: Get the top level concept and see if it generates any `.concepts()` that == Concept("table")



## Solution Group Handlers and Constraints on Concepts
TODO: Writeup how things get hairy if you truly need to check the solution in the general case because you're basically building the solver.  This would happen if you try to implement be_v_id(order1, [steak]) using the concept of steak.  Because what if the user says 2 steaks? or 2 steaks and 2 salads? a better approach would be to allow it to enumerate instances and do normal solving.  Is this right?  That, really, using concepts in solutions should only happen when you are really trying to deal with the speaker talking about concepts. 

How do concepts work when there is some kind of global criteria on them?  For example, phrases like:
"I want 2 steaks"
"I want a few beers"

Because Concept objects can yield entailed concepts *or* instances, it is ambiguous how the solver should count them.  Thus, the solver just assumes variables in a solution group that contain concepts just work (i.e. the `x` representing steaks in "2 steaks"). It is up to the developer to validate that the constraints really are met for those cases. To enable this (and other scenarios) Perplexity has a special kind of function that gets called for each Solution Group -- unlike the predication functions that get called for each solution in a solution group.  These are called "Solution Group Handlers".

Because the main verb of a phrase identifies the action that occurs, a Solution Group Handler is defined for a given verb, and gets called when that verb is used.  To define it, you create a predication function and tack "solution_group_" onto the front of the verb predication name.  So for `_want_v_1`, you'd see this:

~~~
@Predication(vocabulary, names=["solution_group__want_v_1"])
def want_group(context, state_list, e_introduced_binding_list, x_actor_variable_group, x_what_variable_group):
  ...
~~~

Notice that it has the same argument structure as `_want_v_1`, but each argument is now a *list*. That is because this function will be called once for a given solution group, which has multiple solutions.  

The function's job is to validate any global constraints and yield the final Solution Group if they are met.  If they are not met, the function just returns:

~~~
@Predication(vocabulary, names=["solution_group__want_v_1"])
def want_group(context, state_list, e_introduced_binding_list, x_actor_variable_group, x_what_variable_group):
  if constraints_met:
    yield state_list
~~~ 


## Referring Expressions and Concepts
User's can use a (potentially complex) set of words to refer to things they want:
"I want [a steak]"
"I want [something that is not chicken]"
"I want [the lovely chicken that you make]"
"I want [literally the specific salad that my son is eating]"
"I want [a bathroom]"
"I want [a good time]"

The set of words in `[]` is called a *referring expression* in linguistics. In an MRS, a variable like `x8` will hold the thing or things a referring expression refers to. This variable can yield a set of instances or a set of Concept objects that encodes the criteria of the referring expression. The concept itself can return more concepts if they meet all of its requirements.  For example, the Concept("Menu Item") can return the Concept("Fried Chicken").  The Concept("the lovely chicken that you make") can also return the Concept("Fried Chicken"). The Concept("literally the specific fried chicken that my son is eating") *cannot* return Concept("Fried Chicken") because that covers more instances than just the one my son is eating.  This is called *entailment*.





## TODO: Better examples:

Distinguishing these cases requires a) seeing if the referring expression generates a single concept at the same conceptual level (i.e. carrot and beet are at the same conceptual level, but vegetable and carrot are not. As well as deciding which conceptual level to return.  In general, don't we usually want the conceptual level right above instances?).  If so, see if there are any instances that are available for order
- "Do you have steaks?" --> implied request if something is on the menu. Determining what it is a class *of* could be just looking at the base type, or doing an intersection
  - What about "Do you have a steak?" -> a_q implies "choose one", so maybe that is the solution?
- "Do you have that one steak that was undercooked?" --> Probably just a yes/no request for a further conversation

"which steaks/specials do you (restaurant) have?" --> requires returning concepts and disjunctions

"Do you have a table?" --> Might randomly correctly choose a table for 2, but we want to check this to make sure

"what do you have?" --> implied menu request, just needs to be transformed at the top, maybe in the MRS?




## 
"Do you have steaks?"
"Do you have a steak?"
"Do you have [literally the specific steak that my son is eating]"
  - For the scenario of *ordering* you need to say something that defines a class that intersects with a menu item
  - A menu item will return instances that *have not* been ordered yet

"Do you have specials?"
"Do you have salads?"



#### OLD
So far we've been building predications to process the world very logically, like a database might. If someone says "what files are large?" our predications find large files and list them. Language is not always logical, however.

Let's change to a restaurant example and imagine we want to write the implementation for "I want chicken". We want to interpret it as meaning, "Record chicken as my order."

Here's one MRS and tree for "I want chicken":

~~~
Sentence Force: prop
[ "I want chicken"
  TOP: h0
  INDEX: e2 [ e SF: prop TENSE: pres MOOD: indicative PROG: - PERF: - ]
  RELS: < [ pron<0:1> LBL: h4 ARG0: x3 [ x PERS: 1 NUM: sg IND: + PT: std ] ]
          [ pronoun_q<0:1> LBL: h5 ARG0: x3 RSTR: h6 BODY: h7 ]
          [ _want_v_1<2:6> LBL: h1 ARG0: e2 ARG1: x3 ARG2: x8 [ x PERS: 3 NUM: sg ] ]
          [ udef_q<7:14> LBL: h9 ARG0: x8 RSTR: h10 BODY: h11 ]
          [ _chicken_n_1<7:14> LBL: h12 ARG0: x8 ] >
  HCONS: < h0 qeq h1 h6 qeq h4 h10 qeq h12 > ]

               ┌────── pron(x3)
pronoun_q(x3,RSTR,BODY)            ┌────── _chicken_n_1(x8)
                    └─ udef_q(x8,RSTR,BODY)
                                        └─ _want_v_1(e2,x3,x8)

Text Tree: pronoun_q(x3,pron(x3),udef_q(x8,_chicken_n_1(x8),_want_v_1(e2,x3,x8)))
~~~

Let's imagine our restaurant has a few chicken thighs in the kitchen and we say to the waiter "I want chicken". As with the file system examples, the tree will be evaluated and `_chicken_n_1(x8)` will set `x8` to be every instance of a thing that is "chicken" in the world. I.e. `x8=thigh1` then `x8=thigh2` and so on. By the time `_want_v_1(e2,x3,x8)` gets evaluated, it will look something like `want_v_1(e2, "me", "thigh1")` or in plain English: "I want thigh1". We've lost the fact that the customer really asked to *order* the chicken. 

To properly handle this, we need to solve two problems. 

First: distinguishing between the user saying "I want that piece of chicken right there" and "I want to order chicken". We're going to use the notion of "Concepts" to distinguish them.

As discussed in previous sections, the Perplexity solver puts very few constraints on how the state of the world is modelled outside of it being Python objects. It will, however, notice when variables like `x8` get set to Python objects that are meant to represent *concepts*.  They mark this by having a `value_type()` method, and returning `perplexity.predications.VariableValueType.concept`.  When the solver sees these objects, it ensures that they only form solution groups with other concepts and aren't mixed with instances in a single variable. This means that, for a given phrase, we can get a solution group where a variable is set to concepts, and one where it is set to instances. 

This happens because there are two Python implementations of `_chicken_n_1` (literally two Python methods marked as handling `chicken_n_1`) and one returns only concepts, the other returns only instances.  Whichever is first in the Python file returns its objects first.

If the concepts method is first, when the user says "I want chicken", we would get solution groups that look like this:
~~~
Solution Group 1:
x3=Concept(me), x8=Concept(chicken)

Solution Group 2:
x3=me, x8=Concept(chicken)

Solution Group 3:
x3=Concept(me), x8=thigh1

Solution Group 4:
x3=me, x8=thigh1

...
~~~

Solution Group 2 has `want_v_1(e2, me, Concept(chicken))`, "I want the concept of chicken"

Solution Group 4 has `want_v_1(e2, me, thigh1)`, "I want chicken thigh 1"

Both of these are valid ways to interpret the phrase "I want chicken" so they are both returned as solution groups -- i.e. solutions to the MRS.  The application code needs to decide which is the right interpretation in the current context, and decide what to do about it.

We can start by deciding what we think these mean:

"I want the concept of chicken":
- probably means "please order some chicken for me"
- might (but probably doesn't) mean: "the user just wants us to know that they have an existential need for chicken.  Nothing to do about it other than record it"

"I want chicken thigh 1":
- probably means "Give me chicken thigh 1, wherever it is"
- might (but probably doesn't) mean: "the user just wants us to know that they have an existential need for chicken thigh 1.  Nothing to do about it other than record it"

So, the first interpretation of each is worth implementing.  We can ignore the second implementation unless we are building a system that is a psychoanalyst or something.

Furthermore, we can decide which of the remaining two to take as the meaning based on the state of the world.  If the user is a table talking to the waiter about what to order, then we should choose the conceptual want.  In probably any other scenario, we should choose the instance-based one.

Before we go into the edge cases and what-ifs, let's go through how we'd write some initial code:

~~~
@Predication(vocabulary, names=["_want_v_1"]
def _want_v_1(context, state, e_introduced_binding, x_actor_binding, x_object_binding):
    def bound(x_actor, x_object):
        # "actor wants object" 
        if x_actor == "user":
            if user_at_table_talking_to_waiter() and is_concept(x_object):
                # "please order some chicken for me"
                return True
                
            elif not user_at_table_talking_to_waiter() and not is_concept(x_object):
                # "Give me chicken thigh 1, wherever it is"    
                return True
                
    def actor_from_object(x_object):
        # "Which actor wants object?" ... just fail for now
        if False:
            yield None

    def object_from_actor(x_actor):
        # "What does actor want?" ... just fail for now
        if False:
            yield None

    # For now only deal with single, non-conceptual actors wanting something     
    actor_is_bound = x_actor_binding.value is not None
    actor_is_singular = actor_is_bound and len(x_actor_binding.value) == 1
    if actor_is_singular and not is_concept(x_actor_binding.value[0]):
        for new_state in_style_predication_2(context, state, x_actor_binding, x_object_binding, 
                                             bound, actor_from_object, object_from_actor):
            if is_concept(x_actor_binding.value[0]):
                yield new_state.record_operations([AddItemToOrderOperation(x_actor_binding.value[0], x_actor_binding.value[0])])

            else:
                yield new_state.record_operations([GiveItemToUser(x_actor_binding.value[0], x_actor_binding.value[0])])
~~~

This does what we set out to do for those scenarios, but probably doesn't behave how we'd like as we expand the scenarios out.

## More complicated concepts
When sitting at the table talking to the waiter we currently interpret anything that is a variant of the base chicken concept as "order me a regular chicken":

1. "I want chocolate chicken" -> will just order a regular chicken
2. "I want this person's chicken" -> will just order a regular chicken

The user could say something arbitrarily complex about chicken in what is known as a "referring expression" (a set of words that refer to something).  If it resolves down to something random (chocolate chicken), we want to say so.  If it is just a complicated way of referring to a real menu item ("That lovely chicken you guys make!" or "The same chicken my friend ordered"), we'd ideally like to do the right thing and add it to the order.

Figuring out if a referring expression refers to a menu item using abstract logic can be a really hard problem.  However, we can often take a shortcut.  Basically: find all the instances that meet the criteria outlined by the referring expression ("chocolate chicken" or "this person's chicken" or "That lovely chicken you guys make!").  Check to see if any of those is an "instance of a menu item that is available to order".  If so, go ahead and order it.  It is important that it is "available to order" to exclude phrases like "my son's chicken" that might resolve to an instance of a chicken ... which *is* on the menu ... but is not available to order (since my son already has it).

To implement this, let's assume that our `Concept` object has a `.instances()` method which yields all the instances of that concept. That will let us iterate through them.

Then, let's assume we also have a `item_available_for_order()` function that checks if an instance is on the menu and available to order. 

~~~
def _want_v_1(context, state, e_introduced_binding, x_actor_binding, x_object_binding):
    def bound(x_actor, x_object):
        # "actor wants object" 
        if x_actor == "user":
            if user_at_table_talking_to_waiter() and is_concept(x_object):
                # "please order some chicken for me"
                for item in x_object.instances():
                    if item_available_for_order(item):
                        return True
                        
    ...             
~~~

With this in place, "I want chocolate chicken" will fail since none of the instances will be on the menu.  "I want this person's chicken" will also fail since it is not available for oder. "That lovely chicken you guys make!" will evenually work (assuming all the predications required to process it are implemented) since it will return all the instances of that menu item until one hasn't been ordered.

Even though we now have an approach that works, we really didn't see how a `Concept` object could be implemented.  Let's do that now.

## An Example Concept Object
Concepts are built in an application specific way since they depend greatly on how state is represented.  However, it is safe to assume that every application will have a way to tweak an existing generic `Concept(chicken)` object to indicate that it is also "chocolate" (case 1 above) or "belongs to someone" (case 2 above). In addition, an application's concept object needs to be able to generate instances of objects in the world that meet its criteria ... somehow.

For this example, let's assume our application's data is stored as triples of the form, `(subject, relationship, object)`, like:

~~~
("chocolate", "specializes", "food")
("chicken", "specializes", "food")
("thigh1", "instanceOf", "chicken")
~~~

The `Concept` object could look like this:

~~~
class Concept(object):
    def __init__(self, concept_name):
        self.concept_name = concept_name
        self.criteria = []
        
    # Return any instances that meet all the criteria in self.criteria
    def instances(self, context, state, potential_instances=None):
        # add the criteria "object instanceOf self.concept_name" to the list of criteria
        # so we only get instances
        return self._meets_criteria(state, 
                                    [(rel_subjects, "instanceOf", self.concept_name)] + self.criteria)
        
    # Criteria are simply a function that takes 3 arguments, 
    # 2 are explicitly listed, and one (the current state) is implied
    # and passed when called
    def add_criteria(self, function, arg1, arg2):
        self_copy = copy.deepcopy(self)
        self_copy.criteria.append((function, arg1, arg2))
        return self_copy
                            
    def _meets_criteria(self, state, final_criteria):
        found_cumulative = None
        for current_criteria in final_criteria:
            found = []

            if current_criteria[0] == noop_criteria:
                found = found_cumulative
                
            else:
                for result in current_criteria[0](state, current_criteria[1], current_criteria[2]):
                    if found_cumulative is None or result in found_cumulative:
                        found.append(result)

            found_cumulative = found
            if len(found_cumulative) == 0:
                break

        return found_cumulative   
        
def rel_subjects(state, rel, object):
    # Get all the triples that have the relation "rel"
    for item in state.all_rel(rel):
        # If they also have an object of "object", yield the subject
        if item[1] == object:
            yield item[0]                                        
~~~

We can use that object to implement the predications for `_chicken_n_1` and `_chocolate_a_1`:

~~~
@Predication(vocabulary, names=["_chicken_n_1"])
def _chicken_n_1_concept(x_object_binding):
    def bound(val):
        return is_concept(val) and val.concept_name == "chicken"

    def unbound():
        # This will yield all things that are "instanceOf chicken" in the system
        yield Concept("chicken")

    yield from combinatorial_predication_1(context, state, x_bind, bound, unbound)
    

@Predication(vocabulary, names=["_chocolate_a_1"])
def _chocolate_a_1(e_introduced_binding, x_object_binding)
    def bound(val):
        if is_concept(val):
            # We'll add the notion of "is chocolate" to this concept below
            return True
            
    def unbound():
        yield Concept("chicken")

    if x_object_binding.value is None or \
       (x_object_binding.value is not None and len(x_object_binding.value) == 1 and is_concept(x_object_binding.value[0]):
        for new_state in combinatorial_predication_1(context, state, x_bind, bound, unbound):
            # Add the criteria "objects who have the relationship 'object madeOf chocolate'" to the concept object 
            # and yield state with this new, more specific object 
            x_object = x_object_binding.value[0].add_criteria((rel_subjects, "madeOf", "chocolate"))
            yield state.set_x(x_object_binding.variable.name, (x_object, ))
            
    else:
        # This implementation only deals with singular concepts, report formNotUnderstood
        # to allow other implementations to run
        context.report_error(["formNotUnderstood"])

~~~

So now, if someone says "I want chocolate chicken", the following tree will be solved:

~~~
                                               ┌── _chicken_n_1(x8)
                                   ┌────── and(0,1)
               ┌────── pron(x3)    │             │
               │                   │             └ _chocolate_a_1(e13,x8)
pronoun_q(x3,RSTR,BODY)            │
                    └─ udef_q(x8,RSTR,BODY)
                                        └─ _want_v_1(e2,x3,x8)
~~~

... which, because of the implementation of `_chicken_n_1()` and `_chocolate_a_1()` above, will set `x8` to a `Concept(chicken)` object that has an additional criteria of: `(rel_subjects, "madeOf", "chocolate")`

Calling `.instances()` on that `Concept` object will yield any objects in the system where:

~~~
(object, "madeOf", "chocolate")

and

(object, "instanceOf", "chicken")
~~~

Below is the code from above that implemented `_want_v_1`:

~~~
def _want_v_1(context, state, e_introduced_binding, x_actor_binding, x_object_binding):
    def bound(x_actor, x_object):
        # "actor wants object" 
        if x_actor == "user":
            if user_at_table_talking_to_waiter() and is_concept(x_object):
                # "please order some chicken for me"
                for item in x_object.instances():
                    if item_available_for_order(item):
                        return True

    def actor_from_object(x_object):
        # "Which actor wants object?" ... just fail for now
        if False:
            yield None

    def object_from_actor(x_actor):
        # "What does actor want?" ... just fail for now
        if False:
            yield None

    # For now only deal with single, non-conceptual actors wanting something     
    actor_is_bound = x_actor_binding.value is not None
    actor_is_singular = actor_is_bound and len(x_actor_binding.value) == 1
    if actor_is_singular and not is_concept(x_actor_binding.value[0]):
        for new_state in_style_predication_2(context, state, x_actor_binding, x_object_binding, 
                                             bound, actor_from_object, object_from_actor):
            if is_concept(x_actor_binding.value[0]):
                yield new_state.record_operations([AddItemToOrderOperation(x_actor_binding.value[0], x_actor_binding.value[0])])

            else:
                yield new_state.record_operations([GiveItemToUser(x_actor_binding.value[0], x_actor_binding.value[0])])
~~~

From it we can see that:

- If there are no chocolate chickens in the world, `bound()` will fail and not add anything to the order
- If there *are* some in the world, `bound()` will see if they are an `item_available_for_order()`, which presumably they won't be, and thus will also fail.
 
`item_available_for_order()` isn't listed here because it is straightforward. It simply checks if the instance is something that is on the menu, and which hasn't been ordered yet.

Similarly, you can see how, if the user says, "I want my son's salad", the `Concept` object will have a criteria like:

~~~
(object, "instanceOf", "salad")
(object, "ownedBy", "mySon")
~~~

... and might generate the object `salad1` from its `.instances()` method.  This would not be succeed when calling `item_available_for_order()` (although `salad2` and `salad3` might!) since it has already been given out.  Thus, it wouldn't be ordered either.

## Final thoughts on More Complicated Concepts
The truth is that we don't *really* need to use the notion of a `Concept` here.  Because we are calling the `.instances()` method we are really doing the same thing the solver will do anyway.  All we really need to do is to check if they are a) on the menu and b) available for order.

It *is* required, however, for "what is on the menu?"

## More complicated constraints
"I want 2 chickens" -> will just order a single chicken. Need to check constraints

## Section 2
Second, dealing with all the constraints "2 chickens, etc"
This needs a solution group handler.