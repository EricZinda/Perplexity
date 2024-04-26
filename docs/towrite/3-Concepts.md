## Concepts in Solution Groups
If a given MRS variable contains a concept:
Phase 1:
- The tree is evaluated as it is for instances.  If the predication interpretation succeeds, that tree is considered a solution
Phase 2:
- To see if the solution group is a success, any numeric constraints on that variable are assumed to be met
  - And the solution group handler needs to verify them later
  - Note that this means if the phrase was "2 boys ate 2 ice creams", the solution group handler needs to handle all  
  the coll/dist/cuml options, which is the work the solver normally does, and is a ton of work
  - Note also that it may need to check concepts in variables that aren't part of the verb???

## Concept Levels
Conceptually, for any noun predication like `special_n(x)`:

When called with unbound `x`, it should yield:
- the concept `special`
- any other concepts that specialize `special` such as `soup`, `salad`
  - Because those are `special` and this is logically makes sense
- any instances of the above concepts

When called with a bound `x`, it should yield:
- whatever concept `x` held, but further modified to hold the criteria that `special_n` represents now added
- Do we ever just check if `x` is a `special_n` instead of building up the concept?
  - The other thing that could be done is to perform one of the small set of conceptual operations we know how to do on the
    object
    - i.e. check if it is a "sort_of" `special` or see if it has that adjective
    - The problem is that it is unclear if those can be done on concepts that already have criteria set on them, let's say, like "not"
    - we could always fall back to an inductive check on the instances...
    - 
The problem is that, while the instances are a flat list of things that "are a" special, the concepts are a hierarchy. When generating solution sets to form into groups, putting "soup" and "salad" into the same group makes sense, but this group shouldn't include "special" too.  If there are overlapping concepts then we will get duplicate answers?

Basically, every set of concepts that span all the individuals makes sense, and none should overlap

So, if we have the following hierarchy:

1.    special
      |
2.    soup            salad
      |       |       |            |
3.    lentil  tomato  green salad  beet salad


Each level of the hierarchy is a disjunction that should be returned in a different solution set.

But: what if there are instances that derive from a non-leaf level of the hierarchy (like "special") directly? then these disjunctions will have different answers

This does mean the hierarchy has to be carefully constructed.

Scenarios:
      "What kinds of cars do you have?"
      "what are the/your specials?"

## "Do you have [referring expression]"
`re` could be:
- "Do you have [a steak]"
- "Do you have [a small meaty thing that comes from a cow]"
- "Do you have [something that is not chicken]"
- "Do you have [the lovely chicken that you make]"
- "Do you have [literally the specific salad that my son is eating]"
- "Do you have [a bathroom]"


## What can be done with a Concept?
- Alternative thought: the "concept_name" being used is a way of indicating the starting set.  The resulting items will be in that set, so it serves a scoping function.
- 
- You can ask it for instances() or concepts() it entails
  - Which implies that, if you are willing to wait long enough, you can see if it entails only one concept, which is as close as we get to knowing a type
    - but, for example, if it entailed "vegetable", it might also entail "carrot", so even if it entails more than one it might only entail one "base"
    - Also, we can basically construct any arbitrary set of concepts from a given concept can't we?
- You can ask it if a given instance or a given concept is entailed
  - It shouldn't be required to tell if an arbitrary expression is entailed, but a specific instance or concept should work

- Because these can be "instances" or "concepts" there can be an initial base "concept name" that is used as the initial generator of instances or concepts (which are then further filtered down by other criteria).  This can default to simply "thing" to include everything.

Issues:
    - Does the concept include the quantifier (i.e. "something small") or not ("small")?
    - What about the referring expression?

Scenarios:
    - "Do you have something small?"
        - Theoretically returns all the menu items that are "small" as concepts
            - How does it not return the concept of "vegetarian menu item" (the superclass of "soup", "salad", etc)?
Notes:
    - The notion of "concept_name" seems wrong
        - It is bogus in a world of conjunctions...what is the "concept_name" of "[something small] and [a delicious candy]"?
            - just using either the concept_name "small_thing" or "delicious_candy" would be fine if we think of "concept_name" as really being "useful main criteria"
                - a better way to do this is to require the caller to ask about a property of the solution.  I.e. "will any instance or concept that come out of this have the small property?" or "be an instance of steak?"
                    - It is probably true that in the general sense we can't figure it out by inspecting the criteria.  Instead we have to generate instances and induce the answer.
                        - we might be able to inspect the criteria if it is a simple logic
            - we could call it something like "will be an instance of in some way" or "guaranteed that this object will be true for 'instanceOf type'"
                - maybe call it "isa"?
        - How do we convert to english if we can't use that?
          - also, if it doesn't return any instances, how can we convert it to english or get a type from it? There is nothing to "duck type"
          - Certainly we could remember the phrase that created the referring expression and use that for english generation
            - might mean just remembering the DELPH-IN variable?
        - convert to "is_concept(x)"? for things that want to see if it is a certain type?
          - No because if that could work, we'd use it in "want" to see the type
          - We at least need a way to "duck type" for things like `compound` that see if the right side is a "menu"
        - But for things like `_have_v_1_present`, we need to know the type of thing the user mentioned, it isn't enough to do "is_concept(y)", right?
            - Currently, the logic for `have_v_1_present` is: 
                - make sure the actor is the restaurant
                - See if the restaurant has a relationship: "has X" where X is a concept.  
                - while this approach allows for answering "yes" to concepts that have no instances, it also requires that we remember mark both instances and concepts as being "had" by the restaurant.
                - A better approach might be to see if we `have` even a single instance of the concept?
          - what if the user said "Do you have something small?", there is no "one type" for that
            - We could enumerate all concepts the user "has" and put "all small things" into those buckets?
            - In general: Allow sending a list of concepts and return which of those the instances were
          - getting instances for use in duck typing does not work if the concept doesn't have any instances in the world yet
            - This seems crucial
            - But if we can "prove" it based on criteria, etc. that is a workaround
        
## be_v_id(subject, object)
for concepts: every x that specializes concept y should be able to be subject or object and should yield when either is unbound