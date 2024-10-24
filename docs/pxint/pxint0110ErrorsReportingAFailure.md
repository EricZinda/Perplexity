
## Reporting a Failure Naively
In the [previous section](pxint0105ErrorsChoosingWhichFailure) we updated our code to support reporting errors (via `ExecutionContext.report_error()`) and updated the `ExecutionContext.call()` method to record the index of our currently executing predication.  This allowed us to keep track of the "deepest" error.

With that in place, we can now start reporting errors from predications. As outlined in the [predication contract](pxint0010PredicationContract), "failure" is when the predication is not true for its arguments. So, let's add ode at the end of `large_a_1` to record an error when there is a failure. We'll call the new `report_error()` method and pass it what seems like the right error given the code:

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
                context().report_error(["notLarge", item])
~~~

`large_a_1` looks at an object, checks if it has a size at all, and if so, checks if it is "large" and succeeds if it is. If not, a logical error to report would be "'this thing I was passed' is not large", which is what the code does.

We finish by updating `generate_message()` to convert the error to a string:

~~~
def generate_message(state, error):
    ... 
    
    elif error_constant == "notLarge":
        return f"'{arg1}' is not large"

    ...
~~~


... and then run the sample:

~~~
# "a file is large" in a world with no large files
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

    respond_to_mrs(state, mrs)
    
# Outputs:
No, that isn't correct:'File(file1.txt, 100)' is not large
~~~

While the code is all working correctly, it isn't responding the way a user would expect. If nothing is large, a human would say something like "No, nothing is large", "No, a file isn't large" or maybe: "No files are large".  Our code is picking the first thing that appeared and saying "the [first file that was checked] is not large", which is pretty random. 

We can correct it by remembering what is going on at the abstract level: The user will only see this error if there ends up being no large files. If there *are* large files, the system will report, "That is true!".  So, what *should* get reported is, "[whatever domain is being checked] is not large".  In this case the "domain being checked" is "a file". So it should say "a file is not large" (or "no files are large"). We need a way to get a textual description of "the domain that is being checked".

Right now, all that `large_a_1` knows about the domain of `x` is that it is a variable that could hold anything. It doesn't know that x represents `a file` (we'll fix this [next](pxint0120ErrorsConceptualFailures)). So, the best we can do at the moment is to say "a thing":

~~~
@Predication(vocabulary, name="_large_a_1")
def large_a_1(state, e_introduced, x_target):
    
    ...
    
            ReportError(["thingNotLarge"])
~~~

With that (and the appropriate changes to `generate_message()`, if we run "A file is large" through the system with no large files, we'll get: "A thing is not large".  This is the best we can do for now. 

The [next section](pxint0120ErrorsConceptualFailures) will improve it to say "A file is not large" which is more clear.

> Comprehensive source for the completed tutorial is available [here](https://github.com/EricZinda/Perplexity).
