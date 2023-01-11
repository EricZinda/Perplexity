# Handling Event Information
Once you have a predication like `_very_x_deg` that modifies event variables introduced by other predications, you need to decide how to handle predications that *aren't* paying attention to decorations on their introduced event.

For example, let's implement the word "small" to cover the space that "large" doesn't. Namely: files <= 1,000,000 bytes in size:

~~~
@Predication(vocabulary, names=["_small_a_1"])
def small_a_1(state, e_introduced, x_target):
    x_target_value = state.get_variable(x_target)

    if x_target_value is None:
        iterator = state.all_individuals()
    else:
        iterator = [x_target_value]

    for item in iterator:
        # Arbitrarily decide that "small" means a size <= 1,000,000
        # Remember that "hasattr()" checks if an object has
        # a property
        if hasattr(item, 'size') and item.size <= 1000000:
            new_state = state.set_x(x_target, item)
            yield new_state
        else:
            report_error(["adjectiveDoesntApply", "small", x_target])


# Evaluate the proposition: "which file is very small?"
def Example6a():
    state = State([Folder(name="Desktop"),
                   Folder(name="Documents"),
                   File(name="file1.txt", size=2000000),
                   File(name="file2.txt", size=1000000)])

    mrs = {}
    mrs["Index"] = "e1"
    mrs["Variables"] = {"x1": {"NUM": "sg"},
                        "e1": {"SF": "ques"}}
    mrs["Tree"] = [["_which_q", "x1", ["_file_n_of", "x1", "i1"], [["_very_x_deg", "e2", "e1"], ["_small_a_1", "e1", "x1"]]]]

    print(solve_and_respond(state, mrs))
    
# Example prints:
File(name=file2.txt, size=1000000)
~~~

Notice that, even though we said "*very* small" in `Example6a()` the system blithely ignored it and just interpreted it as plain old "small".  The magic of the DELPH-IN system is that it does *deep* linguistic parsing and supports writing code to understand every word in the phrase. If the code ignores some words, the user will lose confidence that the system really understands them.

We want a way to declare the event decorations a predication requires or optionally handles. Then, we can modify our `Predication()` decorator so that it automatically fails if something is on an introduced event that the introducer isn't prepared to handle. To see why this works, recall that a predication [*introduces* a variable that represents it](https://blog.inductorsoftware.com/docsproto/howto/devhowto/devhowtoMRS/#predication-arguments-and-variables). Thus, any decorations on this event are meant to be understood by the predication that introduced it. If the predication doesn't know what to do with them then we want to return an error to the user. This proves we're not just ignoring terms we don't understand and builds trust in the interface.

The logic will be in a function called `ensure_handles_event()`. Its job is to look up the event passed in `event` using the `state` object and compare the decorations on that event to the list of handled decorations passed in the `handles` argument. If they don't match, it sets an error. This function is called in the guts of the `Predication()` decorator: 

~~~
    class EventOption(enum.Enum):
        optional = 1
        required = 2
    
    # handles = [(Name, EventOption), ...]
    # returns True or False, if False sets an error using report_error
    def ensure_handles_event(state, handles, event):
        if event[0] == "e":
            eventState = state.get_variable(event)
            # Look at everything in event and make sure it is handled
            if eventState is not None:
                foundItem = False
                for item in eventState.items():
                    for handledItem in handles:
                        if item[0] == handledItem[0]:
                            foundItem = True
                            break

                    if not foundItem:
                        report_error(["formNotUnderstood", "notHandled", item])
                        return False

            # Look at everything it handles and make sure the required things are there
            for item in handles:
                if item[1] == EventOption.required and (eventState is None or item[0] not in eventState):
                    report_error(["formNotUnderstood", "missing", item])
                    return False

        return True
~~~

With only this set of changes in place, and no changes to our `small_a_1()` predication above, we get:

~~~
# Evaluate the proposition: "which file is very small?"
def Example6a():
    state = State([Folder(name="Desktop"),
                   Folder(name="Documents"),
                   File(name="file1.txt", size=20000000),
                   File(name="file2.txt", size=1000000)])

    mrs = {}
    mrs["Index"] = "e1"
    mrs["Variables"] = {"x1": {"NUM": "sg"},
                        "e1": {"SF": "ques"}}
    mrs["Tree"] = [["_which_q", "x1", ["_file_n_of", "x1", "i1"], [["_very_x_deg", "e2", "e1"], ["_small_a_1", "e1", "x1"]]]]

    print(solve_and_respond(state, mrs))
    
# Example prints:
[4, ['formNotUnderstood', 'notHandled', ('DegreeMultiplier', 10)]]
~~~

We see a raw error because we haven't modified `generate_message()` to handle error messages from `ensure_handles_event()` yet. Even so, it is clearly doing the right thing: it tells us that term 4 (`_small_a_1`) was passed a decoration on its event that it couldn't handle (`DegreeMultiplier`).

To make a nice error message like "I don't understand using 'very' with 'small'", we need to record where the information on the event came from. We'll start a convention where information added to an event is a dictionary with two keys `Value` and `Originator`. `Originator` will store the index of the predication that added the information and `Value` will actually be the information.  Like this:

~~~
@Predication(vocabulary, names=["_very_x_deg"])
def very_x_deg(state, e_introduced, e_target):
    # First see if we have been "very'd"!
    initial_degree_multiplier = degree_multiplier_from_event(state, e_introduced)

    # We'll interpret "very" as meaning "one order of magnitude larger"
    yield state.add_to_e(e_target, "DegreeMultiplier", {"Value": initial_degree_multiplier * 10, "Originator": execution_context().current_predication_index()})


# This is a helper function that any predication that can
# be "very'd" can use to understand just how "very'd" it is
def degree_multiplier_from_event(state, e_introduced):
    # if a "very" is modifying this event, use that value
    # otherwise, return 1
    e_introduced_value = state.get_variable(e_introduced)
    if e_introduced_value is None or "DegreeMultiplier" not in e_introduced_value:
        degree_multiplier = 1
    else:
        degree_multiplier = e_introduced_value["DegreeMultiplier"]["Value"]

    return degree_multiplier
~~~

Then we can use that information (if it exists) to create a nice error:

~~~
# Generates all the responses that predications can return when an error
# occurs
#
# error_term is of the form: [index, error] where "error" is another
# list like: ["name", arg1, arg2, ...]. The first item is the error
# constant (i.e. its name). What the args mean depends on the error
def generate_message(tree_info, error_term):
    error_predicate_index = error_term[0]
    error_arguments = error_term[1]
    error_constant = error_arguments[0]

    ...
    
    elif error_constant == "formNotUnderstood":
        predication = predication_from_index(tree_info, error_predicate_index)
        parsed_predicate = parse_predication_name(predication[0])

        if error_arguments[1] == "notHandled":
            # The event had something that the predication didn't know how to handle
            # See if there is information about where it came from
            if "Originator" in error_arguments[2][1]:
                originator_index = error_arguments[2][1]["Originator"]
                originator_predication = predication_from_index(tree_info, originator_index)
                parsed_originator = parse_predication_name(originator_predication[0])
                return f"I don't understand the way you are using '{parsed_originator['Lemma']}' with '{parsed_predicate['Lemma']}'"

        return f"I don't understand the way you are using: {parsed_predicate['Lemma']}"

    else:
        return error_term

# Running Example6a() now prints:
I don't understand the way you are using 'very' with 'small'
~~~

Finally, we will need to update `large_a_1` to say that it *does* handle the decorations added by `very_x_deg` or it will return the same error:

~~~
@Predication(vocabulary, names=["_large_a_1"], handles=[("DegreeMultiplier", EventOption.optional)])
def large_a_1(state, e_introduced, x_target):
    
    ...
~~~



> Comprehensive source for the completed tutorial is available [here](https://github.com/EricZinda/Perplexity).