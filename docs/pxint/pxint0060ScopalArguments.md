## Solving Scopal Arguments
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
And finally, using our PredicationTree object, you get:
~~~
Todo: update example
~~~

This MRS says "from all the files in the world model, return a single (arbitrary) one that is large". It is indicating that we want the answer to be "a" (i.e. an arbitrary single) large file, whereas `_large_a_1(e,x) and _file_n_of(x)` would give us *all* large files.

If you look at the resolved tree, it really is just one predication with the other two as arguments. So, the `Call()` solver [we built](devhowtoConjunctions) is only going to call the function that implements `_a_q`. The work of implementing the rest of the tree goes to that predication itself. It works this way because the job of predications with scopal arguments is to handle *how* those trees get resolved. That is their whole point. Thus, they need control over the resolution behavior for those arguments.

To implement `_a_q` using our [predication contract](devhowtoPredicationContract), we conceptually:

1. Find the first set of variable assignments returned from the first argument, `_file_n_of(x3)`, using `Call()`
2. Use *those* variable assignments to find a solution to the second argument, `_large_a_1(e2,x3)`, again using `Call()`
3. If there was at least one answer, this is `true`. So: return each of the body solutions that worked from `a_q`, one by one.  Don't "backtrack" to find another "file" since `a_q` should only return "one, arbitrary thing". Other quantifiers like "every" will behave differently.
4. If there was not an answer from the first "file", go back to #1 and try again (remember that our contract says these predications will keep returning values until there are no more)

If there were no large files, `a_q` fails instead of returning any assignments, as per the [predication contract](devhowtoPredicationContract). Here's the Python code that does all this:

~~~
Todo: update example
~~~
Note that, even though we have made both files "large" for this example, only one, arbitrary, file is returned since the phrase is "*a* large file".

At this point we have a fully functional evaluator, now we need to use it to process real phrases and build some of the mechanism around it.

We'll start by stepping back and walking through how [MRS documents and trees are generated](pxint0070GenerateMRSAndTrees.md) in the first place.

> Comprehensive source for the completed tutorial is available [here](https://github.com/EricZinda/Perplexity).
