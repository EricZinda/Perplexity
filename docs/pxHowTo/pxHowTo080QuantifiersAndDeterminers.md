## Quantifiers and Determiners
All of the examples we've used so far have produced quantifiers in their MRS, and all have been implemented automatically by the system:

- "A file is large": `a_q`
- "Which files are large?": `which_q`
- "Delete a file": `pronoun_q`

etc.

This will almost always be the case because quantifiers are not application specific. As described in the [Solution Group Algorithm topic](../devcon/devcon0040MRSSolverSolutionGroupsAlgorithm), quantifers do two things, neither of which is usually application specific:
- scope variables
- constrain their variables to be a certain count

So, the system can manage them automatically across applications.

The same is true for determiners that count like "a few", "less than 3", "both", etc.

### TODO: describe how to build one that isn't in the system like "this"

> Comprehensive source for the completed tutorial is available [here](https://github.com/EricZinda/Perplexity/tree/main/samples/hello_world)
