## Converting Variable Domains to English
So far, the error reporting code for `large_a_1` looks like this:
~~~
@Predication(vocabulary, name="_large_a_1")
def large_a_1(state, e_introduced, x_target):
            
    ...
            # "A thing is not large"
            context().report_error(["thingNotLarge")
~~~

In a world with no large files, it responds to: "A file is large" with: "A *thing* is not large". This is because, in the [previous section](pxint0110ErrorsReportingAFailure), we didn't know how to describe the "domain" that `x` is restricted to. Remember that the `large_a_1` predication will be used for anything the user references as "large", so it will need to be flexible about how it reports its failures.  `x` won't always contain files.

For example, here is a scope-resolved tree for "A file is large":

~~~
          ┌────── _file_n_of(x3,i8)
_a_q(x3,RSTR,BODY)    
               └─ _large_a_1(e2,x3)
~~~

The error in that MRS from `_large_a_1` should say "A *file* is not large" since the only things that can be in `x` by the time it gets to `_large_a_1` have been restricted to files. 

For "A dog is large":
~~~
          ┌────── _dog_n_1(x3)
_a_q(x3,RSTR,BODY)    
               └─ _large_a_1(e2,x3)
~~~
The error in *that* MRS from `_large_a_1` should say "A *dog* is not large". 

etc. 

If we can get a description of the domain of `x`, we can write one error message and have it work no matter how the predication is used.

### Determining What to Call the Domain of "x"
We can figure out what the variable `x` has been restricted to "so far" by taking advantage of some things we know:

1. We know the tree is executed depth-first
2. We know the predications in the tree
3. We know which predication reported the error 

Thus: We know *where* the failed predication is in the execution order.

So, in the scope-resolved tree for "a dog is large":

~~~
          ┌────── _dog_n_1(x3)
_a_q(x3,RSTR,BODY)    
               └─ _large_a_1(e2,x3)
~~~

... if the error came from `_large_a_1`, we must have finished `_dog_n_1` but be in the middle of resolving `_a_q`.  At that point, the variable `x3` contains something that is restricted to `dog` things (not even `*a* dog` yet).  In this way, we can write code which gives the English description of a variable *at a certain point in the tree's execution*. We can use that to build failure messages that have the proper "domain" for any phrase we encounter.

To do this, let's create a function, `english_for_delphin_variable()`, which takes:

1) The `variable` we want an English representation of 
2) The MRS
3) The predication index (i.e. the place in the tree) for which we want the English

It will walk the tree in execution order using the function we've written [in a previous section](pxint0090SimpleQuestions) called `walk_tree_predications_until()`. This function will pass each predication, in execution order, to a different function called `refine_NLG_with_predication()` ("NLG" stands for "Natural Language Generation"). That function will determine if the predication is restricting the `variable` in question somehow. If so, it adds some data to a structure called `nlg_data` that records what the English description of the restriction is. At the end, we'll call a function (`convert_to_english()`) that takes all the gathered data and turns it into English:

~~~
# Given the index where an error happened and a variable,
# return what that variable "is" up to that point (i.e. its "domain")
# in English
def english_for_delphin_variable(failure_index, variable, mrs):
    # Integers can't be passed by reference in Python, so we need to pass
    # the current index in a list so it can be changed as we iterate
    current_predication_index = [0]

    # This function will be called for every predication in the MRS
    # as we walk it in execution order
    def RecordPredicationsUntilFailureIndex(predication):
        # Once we have hit the index where the failure happened, stop
        if current_predication_index[0] == failure_index:
            return False
        else:
            # See if this predication can contribute anything to the
            # description of the variable we are describing. If so,
            # collect it in nlg_data
            refine_NLG_with_predication(variable, predication, nlg_data)
            current_predication_index[0] = current_predication_index[0] + 1
            return None

    nlg_data = {}

    # WalkTreeUntil() walks the predications in mrs["RELS"] and calls
    # the function RecordPredicationsUntilFailureIndex(), until hits the
    # failure_index position
    walk_tree_predications_until(mrs["RELS"], RecordPredicationsUntilFailureIndex)

    # Take the data we gathered and convert to English
    return convert_to_english(nlg_data)
~~~

For now, `refine_NLG_with_predication()` takes a very simple approach to seeing if a predication is restricting the `variable`: Predications which *introduce* a variable (as described in a [the MRS conceptual section](../mrscon/devhowto0010MRS)) are, in some sense, the base "thing" that the variable is. They should clearly be part of its description. Quantifiers for that variable describe "how much" of it there is, so they should be included as well. There is lots more we could add (and we will later) but keeping it simple is fine for now:

~~~
# See if this predication in any way contributes words to
# the variable specified. Put whatever it contributes in nlg_data
def refine_NLG_with_predication(variable, predication, nlg_data):
    # Parse the name of the predication to find out its
    # part of speech (POS) which could be a noun ("n"),
    # quantifier ("q"), etc.
    parsed_predication = parse_predication_name(predication.name)

    # If the predication has this variable as its first argument,
    # it either *introduces* it, or is quantifying it
    if predication.args[0] == variable:
        if parsed_predication["Pos"] == "q":
            # It is quantifying it
            nlg_data["Quantifier"] = parsed_predication["Lemma"]
        else:
            # It is introducing it, thus it is the "main" description
            # of the variable, usually a noun predication
            nlg_data["Topic"] = parsed_predication["Lemma"]
~~~

> Note: The code for `parse_predication_name()` is available in the [main Perplexity tree](https://github.com/EricZinda/Perplexity/blob/1a7e058a77dd8d64a6ee7acdea4adbef93bbeef5/perplexity/utilities.py#L91)

Finally, we can take the information we gathered and convert it (in a very simple way) to English. Note that generating proper English is *much* more complicated than this, and we'll tackle doing it "more right" later. For now, our naive approach will illustrate the ideas:

~~~
# Takes the information gathered in the nlg_data dictionary
# and converts it, in a very simplistic way, to English
def convert_to_english(nlg_data):
    phrase = ""

    if "Quantifier" in nlg_data:
        phrase += nlg_data["Quantifier"] + " "
    else:
        phrase += "a "

    if "Topic" in nlg_data:
        phrase += nlg_data["Topic"]
    else:
        phrase += "thing"

    return phrase
~~~

Those functions will provide the start of a system that converts a variable into English, given a spot in the MRS. 

Using the MRS from "A file is large", we can test it out by calling it with different indices to see what it thinks `x3` is at that point:

~~~
# Generating English for "a file is large"
def Example11():
    # Note neither file is "large" now
    state = State([Folder(name="Desktop"),
                   Folder(name="Documents"),
                   File(name="file1.txt", size=100),
                   File(name="file2.txt", size=100)])

    # Start with an empty dictionary
    mrs = {}

    # Set its "index" key to the value "e2"
    mrs["Index"] = "e2"

    # Set its "Variables" key to *another* dictionary with
    # keys that represent the variables. Each of those has a "value" of
    # yet another dictionary that holds the properties of the variables
    # For now we'll just fill in the SF property
    mrs["Variables"] = {"x3": {},
                        "i1": {},
                        "e2": {"SF": "prop"}}

    mrs["RELS"] = TreePredication(0, "_a_q", ["x3",
                                              TreePredication(1, "_file_n_of", ["x3", "i1"]),
                                              TreePredication(2, "_large_a_1", ["e2", "x3"])])

    # Set index to failure in _a_q
    print(english_for_delphin_variable(0, "x3", mrs))

    # Set index to failure in _file_n_of
    print(english_for_delphin_variable(1, "x3", mrs))

    # Set index to failure in _large_a_1
    print(english_for_delphin_variable(2, "x3", mrs))
    
    
# Outputs:
a thing
a thing
a file
~~~

You can see that, until predication #3 has succeeded (`_file_n_of`), `x8` is described as "a thing" since nothing has restricted it yet. Once it gets past predication #3, it now holds "a file". We could easily beef up our code so that after `_large_a_1` it is described as "a large file" and we will, eventually.

To enable our code to use `english_for_delphin_variable()`, we need to know what predication reported the error.  We'll add a helper to `ExecutionContext` to retrieve it:

~~~
class ExecutionContext(object):
    def __init__(self):
        self._error = None
        self._error_predication_index = -1
        self._predication_index = -1

    ...
    
    def deepest_error_predication_index(self):
        return self._error_predication_index
    
    ...
~~~

... and pass it to `generate_message_with_index` in `respond_to_mrs`. `generate_message_with_index` is a renamed `generate_message` that now just has an extra argument that code can use:

~~~
def respond_to_mrs(state, mrs):
    ...
    
    error = generate_message_with_index(state,
                                        context().deepest_error_predication_index(),
                                        context().deepest_error()) if len(solutions) == 0 else None
~~~

### Fixing _large_a_1 to Use Domains
Recall from the beginning that, running an example, "a file is large" in a world with no large files resulted in "a thing is not large". Once we use the work above, we will get a better result. We'll report a new error code (`notLargeDomain`) from `large_a_1` that will use the MRS *variable* as data:

~~~
@Predication(vocabulary, name="_large_a_1")
def large_a_1(state, e, x):
        ... 
        
        if isinstance(item, File):
            if item.size > 1000:
                # state.SetX() returns a *new* state that
                # is a copy of the old one with just that one
                # variable set to a new value
                # Variable bindings are always tuples so we set
                # this one using the tuple syntax: (item, )
                new_state = state.set_x(x, (item, ))
                yield new_state
            else:
                context().report_error(["notLargeDomain", x])
~~~

Then we can convert this to a string in `generate_message` using our new `english_for_delphin_variable`, which gives us the *domain* of the variable:

~~~
def generate_message_with_index(state, predication_index, error):
    ...

    elif error_constant == "notLargeDomain":
        mrs = state.get_binding("mrs").value[0]
        domain = english_for_delphin_variable(predication_index, arg1, mrs)
        return f"{domain} is not large"
~~~

Running the example now gives:

~~~
def Example10():
    # Note neither file is "large" now
    state = State([Folder(name="Desktop"),
                   Folder(name="Documents"),
                   File(name="file1.txt", size=100),
                   File(name="file2.txt", size=100)])

    # Start with an empty dictionary
    mrs = {}

    # Set its "index" key to the value "e2"
    mrs["Index"] = "e2"

    # Set its "Variables" key to *another* dictionary with
    # keys that represent the variables. Each of those has a "value" of
    # yet another dictionary that holds the properties of the variables
    # For now we'll just fill in the SF property
    mrs["Variables"] = {"x3": {},
                        "i1": {},
                        "e2": {"SF": "prop"}}

    mrs["RELS"] = TreePredication(0, "_a_q", ["x3",
                                       TreePredication(1, "_file_n_of", ["x3", "i1"]),
                                       TreePredication(2, "_large_a_1", ["e2", "x3"])])

    state = state.set_x("mrs", (mrs,))
    respond_to_mrs(state, mrs)
    
# Outputs:
No, that isn't correct: a file is not large
~~~

Much better!

> Comprehensive source for the completed tutorial is available [here](https://github.com/EricZinda/Perplexity).