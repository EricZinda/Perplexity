## Predications with Event Variables
So far, we have been conveniently ignoring any event variables (variables that start with "e"). Where instance (`x`) variables contain a single instance for any solution, event (`e`) variables are designed to build up a structure. They are how modifiers to a word get tracked. 

For example, we've been talking about a `_large_a_1(e2,x3) and _file_n_of(x3)` and have ignored what the event variable `e2` is for. We can't do this if we are trying to find a `_very_x_deg(e2, e1) and _large_a_1(e1,x3) and _file_n_of(x3)`.

In an MRS, any predication except a quantifier is said to "introduce" its first argument. If you look closely you'll see that every variable is only "introduced" by one predication in a given MRS.  In a sense, that variable *represents* that predication.  If a predication like `_large_a_1(e2,x3)` introduces an event variable `e2`, it does so to provide a place that represents it for other predications to hang modifiers.

For example, to represent something that is "very large", the word "very" needs to be able to attach its "veryness" to "large". For "very very large" you build a chain where the first "very" modifies the second which modifies "large". This is all done with events, and it happens like this because languages allow all kinds of recursive constructions. DELPH-IN needed a way to model this.

Here are the predications generated for: "very large" and "very very large" (note that the comma (",") is being used to indicate a conjunction):

~~~
# Very large
_very_x_deg(e2, e1), _large_a_1(e1,x3)

# Very very large
_very_x_deg(e3, e2), _very_x_deg(e2, e1), _large_a_1(e1,x3)
~~~

You can see that in "very large" `_very_x_deg` takes the event variable *introduced by* `_large_a_1` as an argument. The job of `_very_x_deg` is to put something in the event that `_large_a_1` can look for so that its behavior can be modified to be "very large". 

`_very_x_deg` also introduces *its own* event variable that other predications can modify as, for example, in "very very large". The first "very" modifies the event variable introduced by the second "very", etc.

This means, first, that we need a mechanism for handling event variables and, second, that our implementation of `_large_a_1` needs to be modified to pay attention to modifications to its event.

Since event variables need to be able to capture what could be a large buildup of modifications in a given sentence, we'll internally use a dictionary for them. The `State` object passed to every predication has an `add_to_e()` method to allow predications to build up information on the event variable.  Remember that `x` variables simple have a value that is a single set, while `e` variables are a dictionary that builds up over time. So, `add_to_e()` has arguments that indicate what information to add to the event. However, just like `set_x()`,  `add_to_e()` returns a new `state` that must be yielded to indicate success.



We'll add a helper function to the `State` object to modify them:


~~~
class State(object):
    def add_to_e(self, event_name, key, value):
    ...
~~~
`add_to_e()` adds the key/value pair it is given to a (possibly new) dictionary that represents the event state and returns a new `State` object, just like `set_x()` does. 

Now, using the helpers from the previous sections and the new `add_to_e()` method, let's create a `_very_x_deg` predication along with a `_large_a_1` predication that pays attention to modifications to its event.

~~~
@Predication(vocabulary, names=["_very_x_deg"])
def very_x_deg(state, e_introduced_binding, e_target_binding):
    # First see if we have been "very'd"!
    initial_degree_multiplier = degree_multiplier_from_event(state, e_introduced_binding)

    # We'll interpret "very" as meaning "one order of magnitude larger"
    yield state.add_to_e(e_target_binding.variable.name, 
                         "DegreeMultiplier", 
                         {"Value": initial_degree_multiplier * 10, "Originator": execution_context().current_predication_index()})


# This is a helper function that any predication that can
# be "very'd" can use to understand just how "very'd" it is
def degree_multiplier_from_event(state, e_introduced_binding):
    # if a "very" is modifying this event, use that value
    # otherwise, return 1
    if e_introduced_binding.value is None or "DegreeMultiplier" not in e_introduced_binding.value:
        degree_multiplier = 1

    else:
        degree_multiplier = e_introduced_binding.value["DegreeMultiplier"]["Value"]

    return degree_multiplier


@Predication(vocabulary, names=["_large_a_1"], handles=[("DegreeMultiplier", EventOption.optional)])
def large_a_1(state, e_introduced_binding, x_target_binding):
    # See if any modifiers have changed *how* large we should be
    degree_multiplier = degree_multiplier_from_event(state, e_introduced_binding)

    def bound_variable(value):
        if hasattr(value, 'size') and value.size > degree_multiplier * 1000000:
            return True

        else:
            report_error(["adjectiveDoesntApply", "large", x_target_binding.variable.name])
            return False

    def unbound_variable():
        for item in state.all_individuals():
            if bound_variable(item):
                yield item

    yield from combinatorial_style_predication_1(state, x_target_binding, bound_variable, unbound_variable)
~~~
`very_x_deg` adds a "DegreeMultiplier" to the event dictionary of its target, and also pays attention to *its own* introduced event in case someone added one there.  This allows "very very very very..." to work.

`large_a_1` now uses the same logic to determine how much to modify its default notion of "large". Obviously, what "large", "very", etc mean are very domain specific, but this illustrates the concept.

TODO: describe `handles`
> Comprehensive source for the completed tutorial is available [here](https://github.com/EricZinda/Perplexity).