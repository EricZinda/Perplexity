## Determining the Right Parse and Tree
As discussed in the [MRS topic](devhowtoMRS) and the [Well-Formed Trees topic](devhowtoWellFormedTree), a single phrase like "Look under the table" produces `m` MRS documents, and each of those produces `n` well-formed trees, thus generating `m x n` potential interpretations of a phrase. How do you determine which one is the one the user *meant*?

The short answer is that, just like when you are talking to a human, you never *really* know what they meant unless you pick your best guess and confirm it with them. But: there are a couple of things that help: First, [ACE](http://sweaglesw.org/linguistics/ace/) uses a machine-learning-based algorithm to sort the MRS documents and returns the "most common" ones first. This means the more obscure MRS interpretations will be sorted last. Unfortunately, there is no such mechanism for the well-formed trees. So, at best we have a partial ordering of the `m x n` trees in terms of "most commonly meant". 

With that in mind, a simple approach to choosing the "right" interpretation that works surprisingly well is: 

> Execute each well-formed tree against the world state using the provided partial order. Assume the first one that succeeds is what the user meant. If none succeed, return the first failure.

This works for the same reason human interactions work: Most phrases are meant to convey information that *makes sense*. I.e. the phrase discusses things that actually exist, uses verbs that make sense with objects being discussed, etc. So, most phrases the user gives your system *should* have a solution given the current world state. Furthermore, humans have an intuitive understanding of the ambiguity of language and are forgiving of errors when they are understandable and logical failures. I.e. "I can see why you thought that, even though it wasn't what I meant...". 

So, if the system finds a tree that has a solution in the current world state, it is likely to be at least close to what the user meant. Even if it isn't, given that it was a solution in the world state, it will still be *logical* and the user will very often understand (and sometimes be delighted by) how their phrase was misinterpreted.

Thus, the approach to finding which of the `m x n` meanings is the "meant one" is to run them all, in order, and assume the first that works is the right one.

Things get a little trickier if none of them works. However, the same principle holds: as long as the error response we give is *logical* and *understandable*, it will make sense to the user, even if it isn't quite the answer a person would have given. Often we can do better than just returning the first failure, but this requires knowing what kinds of errors your particular system produces, which ones are less useful, etc. Returning the first failure is a good place to start.

> Comprehensive source for the completed tutorial is available [here](https://github.com/EricZinda/Perplexity).
