{% raw %}## Reporting a Failure Naively
With all that in place, we can now start reporting errors from predications. As outlined in the predication contract, "failure" is when the predication is not true for its arguments, so let's add a little code at the end of `large_a_1` to record an error when there is a failure. We'll call the new `ReportError()` method and pass it what seems like the right error given the code:

```
@Predication(vocabulary, name="_large_a_1")
def large_a_1(state, e_introduced, x_target):

    ...
    
    degree_multiplier = DegreeMultiplierFromEvent(state, e_introduced)
    for item in iterator:
        if hasattr(item, 'size') and item.size > degree_multiplier * 1000000:
            new_state = state.SetX(x_target, item)
            yield new_state
        else:
            # starting a string with: f" allows you to put local Python
            # variables into it using {}, in a kind of template approach
            ReportError(f"'{item}' is not large")
```

`large_a_1` looks at an object, checks if it has a size at all, and if so, checks if it is "large" and succeeds if it is. If not, a logical error to report would be "'this thing I was passed' is not large" (which is what we did).

Let's try it by evaluating "A file is large":

```
          ┌────── _file_n_of(x3,i8)
_a_q(x3,RSTR,BODY)    
               └─ _large_a_1(e2,x3)
```

... against this example world:

```
a folder
a small file
a file
a dog
```

... and with our new error logic, we'll get these failures:

1. `a folder`: a `_file_n_of` failure
2. `a small file`: a `large_a_1` failure
3. `a file`: a `large_a_1` failure
4. `a dog`: a `_file_n_of` failure

Error #2 will be remembered using our new heuristic. The actual error reported from #2 for the phrase, "A file is large" will be: "'a small file' is not large". 

This is an odd answer.  Even though it looked like it made sense in the code, it is pretty far from the one we wanted which is something like: "There isn't a large file". 

We can correct it if we remember what is going on at the abstract level: We are finding values for the variables that make the MRS true.  The *mechanics* are to feed every object in the world through the variables in the MRS, but the overall *objective* is to, for example, find an `x` that makes `_large_a_1` true.  The problem is that we are reporting the error with a textual description of the *example* that is currently in the `x` variable (e.g. `a small file`) instead of what `x` *represents* ("a file").  

Right now, all that `large_a_1` knows about `x` is that it is a variable, it doesn't know that x represents `a file` (we'll fix this next). So, the best we can do at the moment is to say "a thing":

```
@Predication(vocabulary, name="_large_a_1")
def large_a_1(state, e_introduced, x_target):
    
    ...
    
            ReportError("A thing is not large")
```

With that, if we run "A file is large" through the system with no large files, we'll get: "A thing is not large".  This is the best we can do for now. 

The next section will improve it to say "A file is not large" which is more clear.

> Comprehensive source for the completed tutorial is available [here](https://github.com/EricZinda/Perplexity).


Last update: 2023-05-14 by EricZinda [[edit](https://github.com/EricZinda/Perplexity/edit/main/docs/devhowto/devhowto16ErrorsReportingAFailure.md)]{% endraw %}