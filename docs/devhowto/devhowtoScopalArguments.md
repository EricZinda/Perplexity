## Scopal Arguments
Scopal arguments are predication arguments that hold *other predications*, much like lambda functions can pass around functions as arguments in some programming languages.  They indicate that the predication should do its job using the results of the whole "branch" it is given. Exactly *what* job depends on the predication. The most common scopal arguments are seen in quantifiers like "a, the, every, some" etc. The job of a quantifier in a natural language is to limit (i.e. "quantify") the number of answers in some way. They do that by taking a `RSTR` argument that indicates what the quantifier is about (e.g. "a *folder*"), and a `BODY` argument that says what we are restricting the quantification to (e.g. "something *large*"). 

For example, take the phrase: "a file is large". One of the scope-resolved MRS trees for it is:

~~~
           ┌───── _file_n_of(x3)
_a_q(x3, RSTR,BODY)
                └ _large_a_1(e2,x3)
~~~
> We can ignore for the moment variables of type `e`. We'll handle those later, they don't matter for this example.

If we convert this into text, it would be something like:
~~~
 _a_q(x3, _file_n_of(x3), _large_a_1(e2, x3))
~~~
And finally, using our text format, you get:
~~~
["_a_q", "x3", ["_file_n_of", "x3"], ["_large_a_1", "e2", "x3"]]
~~~

This MRS says "from all the files in the world model, return a single (arbitrary) one that is large". It is indicating that we want the answer to be "a" (i.e. an arbitrary single) large file, whereas `_large_a_1(e,x) and _file_n_of(x)` would give us *all* large files.

If you look at the resolved tree, it really is just one predication with the other two as arguments. So, the `Call()` solver [we built](devhowtoConjunctions) is only going to call the function that implements `_a_q`. The work of implementing the rest of the tree goes to that predication itself. It works this way because the job of predications with scopal arguments is to handle *how* those trees get resolved. That is their whole point. Thus, they need control over the resolution behavior for those arguments.

To implement `_a_q` using our [predication contract](devhowtoPredicationContract), we conceptually:

1. Find the first set of variable assignments returned from the first argument, `_file_n_of(x3)`, using `Call()`
2. Use *those* variable assignments to find a solution to the second argument, `_large_a_1(e2,x3)`, again using `Call()`
3. If there was at least one answer, this is true. So: return each of the body solutions that worked from `a_q`, one by one.  Don't "backtrack" to find another "file" since `a_q` should only return "one, arbitrary thing". Other quantifiers like "every" will behave differently.
4. If there was not an answer from the first "file", go back to #1 and try again (remember that our contract says these predications will keep returning values until there are no more)

If there were no large files, `a_q` fails instead of returning any assignments, as per the [predication contract](devhowtoPredicationContract). Here's the Python code that does all this:

~~~
@Predication(vocabulary, name="_a_q")
def a_q(state, x_variable, h_rstr, h_body):
    # Run the RSTR which should fill in the variable with an item
    for solution in Call(vocabulary, state, h_rstr):
        # Now see if that solution works in the BODY
        success = False
        for body_solution in Call(vocabulary, solution, h_body):
            yield body_solution
            success = True

        if success:
            # If it works, stop looking. This one is the single arbitrary item we are looking for
            break

def Example4():
    # Note that both files are "large" now
    state = State([Folder(name="Desktop"),
                   Folder(name="Documents"),
                   File(name="file1.txt", size=1000000),
                   File(name="file2.txt", size=2000000)])
    mrs = ["_a_q", "x3", ["_file_n_of", "x3"], ["_large_a_1", "e2", "x3"]]
    for item in Call(vocabulary, state, mrs):
        print(item.variables)
        
# Example4() prints:
{'x3': File(name=file2.txt, size=2000000)}
~~~
Note that, even though we have made both files "large" for this example, only one, arbitrary, file is returned since the phrase is "*a* large file".

At this point we have a fully functional evaluator, but there are a few things still to work out:
- Dealing with variable types beyond `x` variables
- Handling questions vs. commands vs. propositions
- Reporting errors

The [next topics](devhowtoEvents) will tackle these issues.