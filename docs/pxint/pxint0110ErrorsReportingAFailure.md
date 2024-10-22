
## Reporting a Failure Naively
With all that in place, we can now start reporting errors from predications. As outlined in the [predication contract](devhowtoPredicationContract), "failure" is when the predication is not true for its arguments, so let's add a little code at the end of `large_a_1` to record an error when there is a failure. We'll call the new `report_error()` method and pass it what seems like the right error given the code:

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

Let's try it by evaluating "A file is large":

~~~
          ┌────── _file_n_of(x3,i8)
_a_q(x3,RSTR,BODY)    
               └─ _large_a_1(e2,x3)
~~~

... against this example world:

~~~
a folder
a small file
a file
a dog
~~~

... and with our new error logic, we'll get these failures:

1. `a folder`: a `_file_n_of` failure
2. `a small file`: a `large_a_1` failure
3. `a file`: a `large_a_1` failure
4. `a dog`: a `_file_n_of` failure

Error #2 will be remembered using our new heuristic. The actual error reported from #2 for the phrase, "A file is large" will be: "'a small file' is not large". 

This is an odd answer.  Even though it looked like it made sense in the code, it is pretty far from the one we wanted which is something like: "There isn't a large file". 

We can correct it if we remember what is going on at the abstract level: We are finding values for the variables that make the MRS true.  The *mechanics* are to feed every object in the world through the variables in the MRS, but the overall *objective* is to, for example, find an `x` that makes `_large_a_1` true.  The problem is that we are reporting the error with a textual description of the *example* that is currently in the `x` variable (e.g. `a small file`) instead of what `x` *represents* ("a file").  

Right now, all that `large_a_1` knows about `x` is that it is a variable, it doesn't know that x represents `a file` (we'll fix this [next](devhowtoConceptualFailures)). So, the best we can do at the moment is to say "a thing":

~~~
@Predication(vocabulary, name="_large_a_1")
def large_a_1(state, e_introduced, x_target):
    
    ...
    
            ReportError("A thing is not large")
~~~

With that, if we run "A file is large" through the system with no large files, we'll get: "A thing is not large".  This is the best we can do for now. 

The [next section](devhowtoConceptualFailures) will improve it to say "A file is not large" which is more clear.

> Comprehensive source for the completed tutorial is available [here](https://github.com/EricZinda/Perplexity).
