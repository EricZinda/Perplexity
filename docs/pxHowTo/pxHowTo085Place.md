## Representing Places
To understand what we need to properly represent places, let's go through a key predication from the ERG that represents place, `loc_nonsp`.

`loc_nonsp` ("nonspecific location") is true when `x_location` represents a "place" where `x_actor` "is" or "is at" but doesn't get more specific than that. It shows up in phrases like:

- "Where am I?" -> no relationship other than I "am" somewhere
- "Where is the stick?" -> no relationship other than the stick "is" somewhere
- "The dog barks every day" -> No relationship to day other than it "happens" every day

It *would not* show up in phrases that more specifically locate something, such as:

- The stick is on the table. -> locates the stick in a place on the location
- He arrives before/at 10am. -> locates the arrival before/at a certain time

More information is available in the [ERG reference](https://blog.inductorsoftware.com/docsproto/erg/ErgSemantics_ImplicitLocatives/).

In this topic, we'll implement the `loc_nonsp` and `place_n` predications to make the phrase "Where am I?" work. As always, we'll start by examining the MRS to see what predications it generates for the phrase:

~~~
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

### `place_n(x)`
As in "Where am I?", a predication that often appears with `loc_nonsp` is `place_n` when the location being referred to is inferred by the system to be a place.

What are the "places" in a file system? They are all the objects where something else can be located, some obvious ones:
- `file`: text can be located in a file, "where is the text 'summary of costs'?"
- `folder`: files can be in a folder, "where is the file 'foo.txt'?"

For this particular system, a good proxy for "place" might be anything that something can be "in", aka a "container". We'll want easy ways to:

- Find all the containers
- Find all the containers that contain a particular thing

`place_n` will be able to leverage the methods on the objects we built in the [previous section](pxHowTo082State) to do this, and we'll use the same approach we've been using for other nouns introduced in the [Implementing a Predication topic](pxHowTo020ImplementAPredication):

~~~
@Predication(vocabulary)
def place_n(state, x_binding):
    def bound_variable(value):
        # Any object is a "place" as long as it can contain things
        if hasattr(value, "contained_items"):
            return True
        else:
            report_error(["valueIsNotX", value, x_binding.variable.name])
            return False

    def unbound_variable():
        for item in state.all_individuals():
            if bound_variable(item):
                yield item

    yield from combinatorial_style_predication_1(state, 
                                                 x_binding, 
                                                 bound_variable, 
                                                 unbound_variable)
~~~
This should all look reasonablly familiar by now. If an object has a `contained_items` method, that means it is a container and that means it is "a place". Different systems will have different criteria for place depending on their scenarios. The function iterates through all objects in the system and yields any that have this method when its `x` argument is unbound, thus yielding all the "places".

### `loc_nonsp(e,x,x)`: Representing Generic Location
As described above, `loc_nonsp(e,x_actor,x_location)` is true when `x_location` represents a "place" where `x_actor` "is" or "is at" but doesn't get more specific than that. Basically, it is the "generic location" of `x_actor` (`x_actor` does not need to be an actually be an `Actor` it can be anything). This means we'll need to get the "location" from the objects in the system. Note that a given file or folder has many "locations":

- It is located in a folder
- It is also located in the parent folder
- It is also located in the parent of the parent folder
- etc.

We've already implemented a method to return the locations of objects called `all_locations()` on the `Actor`, `File` and `Folder` objects which we can use:

~~~
@Predication(vocabulary, names=["loc_nonsp"])
def loc_nonsp(state, e_introduced_binding, x_actor_binding, x_location_binding):
    def item_at_item(item1, item2):
        if hasattr(item1, "all_locations"):
            # Asking if a location of item1 is at item2
            for location in item1.all_locations(x_actor_binding.variable):
                if location == item2:
                    return True

        report_error(["thingHasNoLocation", x_actor_binding.variable.name, x_location_binding.variable.name])
        return False

    def location_unbound_values(actor_value):
        # This is a "where is actor?" type query since no location specified (x_location_binding was unbound)
        # Order matters, so all_locations needs to return the best answer first
        if hasattr(actor_value, "all_locations"):
            for location in actor_value.all_locations(x_actor_binding.variable):
                yield location

        report_error(["thingHasNoLocation", x_actor_binding.variable.name, x_location_binding.variable.name])

    def actor_unbound_values(location_value):
        # This is a "what is at x?" type query since no actor specified (x_actor_binding was unbound)
        # Order matters, so all_locations needs to return the best answer first
        if hasattr(location_value, "contained_items"):
            for actor in location_value.contained_items(x_location_binding.variable):
                yield actor

        report_error(["thingIsNotContainer", x_location_binding.variable.name])

    yield from in_style_predication_2(state, 
                                      x_actor_binding, 
                                      x_location_binding, 
                                      item_at_item, 
                                      actor_unbound_values, 
                                      location_unbound_values)
~~~

`loc_nonsp` is an "in-style" predication because if the location of `x` is `location1` and the location of `y` is `location`, then they are both there "together" or "separately" and it doesn't mean anything special, but also shouldn't be prohibited. This is a pretty straightforward implementation, just like the implementation of `_in_p_loc` in the [In-Style Predications topic](pxHowTo030InStylePredications).

We've introduced two new location-based errors `thingHasNoLocation` and `thingIsNotContainer`, so we need to provide messages for them in `generate_custom_message()` as well (using [s-strings](pxHowTo025SStrings)):

~~~
def generate_custom_message(tree_info, error_term):
    ...

    elif error_constant == "thingHasNoLocation":
        return s("{arg1} is not in {arg2}", tree_info)

    elif error_constant == "thingIsNotContainer":
        return s("{arg1} can't contain things", tree_info)

    ...
~~~

# Example
Including the implementation of `loc_nonsp` and `place_n`, with no other changes to the code we've built so far, allows us to start interacting with place a bit:

~~~
python hello_world.py
? where am I?
(Folder(name=/documents, size=0),)
(there are more)

? where are you?
you is not in place

? where is a file?
(Folder(name=/documents, size=0),)
(there are more)

? where is a folder?
(Folder(name=/, size=0),)
~~~

Both "where am I?" and "where is a file?" give an answer and then say, "(there are more)". That is because the user asked for "a place" (singular) but most things will "be located" in more than one place. For example, the user is in both "/documents" and "/" (the root directory). As described in the [Combination Algorithm and Proper Responses topic](../devcon/devcon0050MRSSolverSolutionCombinations), we let the user know if they there is more than one thing if they ask for a singular answer, just to clarify.

Also note that "you" refers to "the computer" and we haven't put it anywhere, that's why the system responds with "you is not in place". Again, we'll fix the English on error messages soon.

> Comprehensive source for the completed tutorial is available [here](https://github.com/EricZinda/Perplexity).
