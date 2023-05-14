{% raw %}## Reporting a Failure More Robustly
One final piece of cleanup work remains in our effort to report decent failures when resolving an MRS. We will be returning a lot of the same errors from different predications. Instead of littering the code with full sentences like "There is not a large thing", we'll use constants like `doesntExist` and allow them to take arguments like `x3`. Then, using the code from the previous section, we can create a shared routine that turns them into English and fills them in with descriptions of the variables at the point of failure.  Like this:

```
# error_term is of the form: [index, error] where "error" is another 
# list like: ["name", arg1, arg2, ...]. The first item is the error 
# constant (i.e. its name). What the args mean depends on the error
def GenerateMessage(mrs, error_term):
    error_predicate_index = error_term[0]
    error_arguments = error_term[1]
    error_constant = error_arguments[0]

    if error_constant == "xIsNotY":
        arg1 = EnglishForDelphinVariable(error_predicate_index, error_arguments[1], mrs)
        arg2 = error_arguments[2]
        return f"{arg1} is not {arg2}"

    elif error_constant == "adjectiveDoesntApply":
        arg1 = error_arguments[1]
        arg2 = EnglishForDelphinVariable(error_predicate_index, error_arguments[2], mrs)
        return f"{arg2} is not {arg1}"
```

Most of what `GenerateMessage()` does is plug the error arguments into a string template.  The interesting work happens when one of the arguments is a DELPH-IN variable and it calls `EnglishForDelphinVariable()`.  This is where we use the code from the previous section to properly describe what is in that `x` variable. 

Finally, we can change our predications to use `ReportError()` with the new error format, and change `RespondToMRS()` to respond with decent errors using all the ideas and code we've written in the last few sections:

```
@Predication(vocabulary, name="_file_n_of")
def file_n_of(state, x):
    
    ...
    
    for item in iterator:
        if isinstance(item, File):
            new_state = state.SetX(x, item)
            yield new_state
        else:
            ReportError(["xIsNotY", x, "file"])
                        
            
@Predication(vocabulary, name="_large_a_1")
def large_a_1(state, e_introduced, x_target):
            
    ...
    
        for item in iterator:
        # Arbitrarily decide that "large" means a size greater
        # than 1,000,000 and apply any multipliers that other
        # predications set in the introduced event
        # Remember that "hasattr()" checks if an object has
        # a property
        if hasattr(item, 'size') and item.size > degree_multiplier * 1000000:
            new_state = state.SetX(x_target, item)
            yield new_state
        else:
            ReportError(["adjectiveDoesntApply", "large", x_target])
        

def RespondToMRS(self, state, mrs):

    ...
    
    if sentence_force == "prop":
        if len(solutions) > 0:
            print("Yes, that is true.")
        else:
            message = GenerateMessage(mrs, self.Error())
            print(f"No, that isn't correct: {message}")
```

So, the predications like `large_a_1` and `file_n_of` report their failures as described in the previous sections, but now use a constant and a list of arguments as the "shape" of their errors.  If an MRS can't be solved, `RespondToMRS()` calls the `GenerateMessage()` helper function to turn the error into English and prints it for the user.

With all that in place, we can now take some of our previous examples and make them fail to see what messages we get:

```
# Evaluate the proposition: "a file is large" when there are no *large* files
def Example10():
    state = State([Folder(name="Desktop"),
                   Folder(name="Documents"),
                   File(name="file1.txt", size=1000000),
                   File(name="file2.txt", size=1000000)])

    mrs = {}
    mrs["Index"] = "e1"
    mrs["Variables"] = {"x1": {"NUM": "pl"},
                        "e1": {"SF": "prop"}}
    mrs["RELS"] = [["_a_q", "x1", ["_file_n_of", "x1"], ["_large_a_1", "e1", "x1"]]]

    state = state.SetX("mrs", mrs)
    DelphinContext().RespondToMRS(state, mrs)
    
# Prints:
No, that isn't correct: a file is not large
```

A fine answer.  Let's try another:

```
# Evaluate the proposition: "a file is large" when there are no files, period
def Example11():
    state = State([Folder(name="Desktop"),
                   Folder(name="Documents")])

    mrs = {}
    mrs["Index"] = "e1"
    mrs["Variables"] = {"x1": {"NUM": "pl"},
                        "e1": {"SF": "prop"}}
    mrs["RELS"] = [["_a_q", "x1", ["_file_n_of", "x1"], ["_large_a_1", "e1", "x1"]]]

    state = state.SetX("mrs", mrs)
    DelphinContext().RespondToMRS(state, mrs)

# Prints:
No, that isn't correct: a thing is not a file
```

That one isn't good. The next section will analyze why, and how to fix it.

> Comprehensive source for the completed tutorial is available [here](https://github.com/EricZinda/Perplexity).


Last update: 2023-05-13 by EricZinda [[edit](https://github.com/EricZinda/Perplexity/edit/main/docs/devhowto/devhowto17.5ErrorsRobustFailure.md)]{% endraw %}