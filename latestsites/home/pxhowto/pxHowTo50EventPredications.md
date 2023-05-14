{% raw %}## Predications with Event Variables
So far, we have been conveniently ignoring event variables (variables that start with "e"). Where instance (`x`) variables contain a single instance for any solution, event (`e`) variables are designed to build up a structure. They are how modifiers to a word like "very" and "slowly" get tracked. 

For example, we've been talking about a `_large_a_1(e2,x3), _file_n_of(x3)` and have ignored what the event variable `e2` is for. We can't do this if we are trying to find a `_very_x_deg(e2, e1), _large_a_1(e1,x3), _file_n_of(x3)`.

In an MRS, any predication except a quantifier is said to "introduce" its first argument. If you look closely you'll see that every variable is only "introduced" by one predication in a given MRS -- only one predication has a given variable as its first argument.  So, in a sense, that variable *represents* that predication.  If a predication like `_large_a_1(e2,x3)` introduces event variable `e2`, it does so to provide a place for other predications to hang modifiers to it.

For example, to represent something that is "very large", the word "very" needs to be able to attach its "veryness" to "large". For "very very large" you build a chain where the first "very" modifies the second which modifies "large". This is all done with events, and it happens like this because languages allow all kinds of recursive constructions. DELPH-IN needed a way to model this.

Here are the predications generated for: "very large" and "very very large". The comma (",") is being used to indicate a conjunction (i.e. "and"):

```
# Very large
_very_x_deg(e2, e1), _large_a_1(e1,x3)

# Very very large
_very_x_deg(e3, e2), _very_x_deg(e2, e1), _large_a_1(e1,x3)
```

You can see that in "very large" `_very_x_deg` takes the event variable *introduced by* `_large_a_1` as an argument. The job of `_very_x_deg` is to put something in the event that `_large_a_1` can look for so that its behavior can be modified to be "very large". 

`_very_x_deg` also introduces *its own* event variable that other predications can modify as, for example, in "very very large". The first "very" modifies the event variable introduced by the second "very", etc.

This means, first, that we need a mechanism for handling event variables and, second, that our implementation of `_large_a_1` needs to be modified to pay attention to modifications to its event.

Since event variables need to be able to capture what could be a large buildup of modifications in a given sentence, we'll internally use a dictionary for them. The `State` object passed to every predication has an `add_to_e()` method to allow predications to build up information on the event variable.  `x` variables have a value that is a single set, while `e` variables are a dictionary that builds up over time. So, `add_to_e()` has arguments that indicate what information to add to the event. However, just like `set_x()`,  `add_to_e()` returns a new `state` that must be yielded to indicate success.

The `add_to_e()` method looks like this:

```
def add_to_e(self, event_name, key, value):
    ...
```
`add_to_e()` adds the key/value pair it is given to a dictionary that represents the event state and returns a new `State` object, just like `set_x()` does. But, unlike `set_x()`, it keeps whatever was in the event variable before. This allows information to get built up in the event.

Now, using the helpers from the previous sections and the new `add_to_e()` method, let's create a `_very_x_deg` predication along with a `_large_a_1` predication that pays attention to modifications to its event.

Let's start with `very_x_deg`:
```
@Predication(vocabulary, names=["_very_x_deg"])
def very_x_deg(state, e_introduced_binding, e_target_binding):
    # We'll interpret every "very" as meaning "one order of magnitude larger"
    yield state.add_to_e(e_target_binding.variable.name, 
                         "DegreeMultiplier", 
                         {"Value": 10, 
                          "Originator": execution_context().current_predication_index()})
```
`very_x_deg()` doesn't have any `x` variables, so we don't have to worry about if they are bound or unbound. Predications like this simply have to add information to the `e` variable they are modifying. Recall that the first argument (in this case, `e_introduced_binding`) represents *this* predication, so the variable being modified is the second one: `e_target_binding`.

It really doesn't matter *what* the predication adds to `e_target_binding` as long as the predications that consume it know what to look for. It is application specific. However, the system will look for the `Originator: execution_context().current_predication_index()` field and use it to produce nice errors. 

So, we've chosen to give the key `"DegreeMultiplier"` to the information provided by `very_x_deg`, and added a field that indicates to what degree something should be increased using `"Value": 10`.

We can build a helper that know about the names and fields we've chosen so that any predication that understands "very" can use it:

```
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
```

The helper function gets passed an event variable and looks for the information that `very_x_deg` adds to it. If found, it turns it. Otherwise, it just returns 1. Now, any predication can multiply numbers using this value.  Here's an example of `large_a_1` using it:

```
@Predication(vocabulary, names=["_large_a_1"])
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
```
`large_a_1` uses the same `combinatorial_style_predication_1()` helper that "file" did from a previous section. It tests if something is large by seeing if it has a size property and, if so, seeing if the size is 1,000,000 multiplied by however many "very's" the user said. Obviously, this only makes sense if we are talking about files, the implementation of `large_a_1`, like every predication, is application specific.

Note that if `large_a_1` is called with an unbound variable, it looks through every object in the system and only returns the ones that are "large" (or "very large") by calling the same function used to check bound variables.

## Declaring Use of Event Information
There is a problem, however. This doesn't work yet. If the user says "a file is very large" the system will respond with:

```
I don't understand the way you are using 'very' with 'large'
```

This is because Perplexity is designed to make sure it understands *every* word in a sentence so that users gain confidence that they truly are understood and that the system isn't just doing "keyword picking". One way it does this is by ensuring that any information added to an event is actually consumed by another predication in the phrase. If not, it replies with that error.

Since we have implemented very with large, the fix is simple: we just need to add information to the `@Predication` declaration, like this:

```
@Predication(vocabulary, names=["_large_a_1"], handles=[("DegreeMultiplier", EventOption.optional)])
def large_a_1(state, e_introduced_binding, x_target_binding):

    ...
```

The `handles=[]` clause lists out all of the keys that the predication knows how to process in its introduced event. In this case, we have also added `EventOption.optional` to say that large doesn't *require* "very", but understands it if said. Now it will properly process the phrase.

> Comprehensive source for the completed tutorial is available [here](https://github.com/EricZinda/Perplexity).


Last update: 2023-05-13 by EricZinda [[edit](https://github.com/EricZinda/Perplexity/edit/main/docs/pxHowTo/pxHowTo50EventPredications.md)]{% endraw %}