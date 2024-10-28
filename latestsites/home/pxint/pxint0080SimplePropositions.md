{% raw %}## Responding to Simple Propositions
The examples we've seen so far respond by printing out all the solutions that were found. It is time to start responding more like a human would. Here we'll walk through how to implement a better response to one type of phrase: the proposition. The next sections will walk through how to do the same for questions and commands.

"Propositions" are sentences that declare something to be true like, "A file is very large". If true, a human would expect something like "yep, you are right" or "correct!" or "yes, this is true" as a response (error cases will be handled later). As described in the [Sentence Types section](https://blog.inductorsoftware.com/Perplexity/home/devcon/devcon0070SentenceForce), the English Resource Grammar helps us identify the type of phrase we received by providing a property called `SF` or "Sentence Force". A phrase is a proposition if the `SF` property of its index variable is `prop`.

Below is the MRS for "A file is large". `e2` is the `INDEX` of the MRS, which represents the "syntactic head" or "main point" of the phrase.  It has a sentence force of "proposition": `SF: prop`.

```
[ "a file is large"
  TOP: h0
  INDEX: e2 [ e SF: prop TENSE: pres MOOD: indicative PROG: - PERF: - ]
  RELS: < [ _a_q<0:1> LBL: h4 ARG0: x3 [ x PERS: 3 NUM: sg IND: + ] RSTR: h5 BODY: h6 ]
          [ _file_n_of<2:6> LBL: h7 ARG0: x3 ARG1: i8 ]
          [ _large_a_1<10:15> LBL: h1 ARG0: e2 ARG1: x3 ] >
  HCONS: < h0 qeq h1 h5 qeq h7 > ]
```

In order to start responding to user phrases properly, we need to give the solver a dictionary of variable properties in addition to the predications. In fact, we can make it easier to read using the Python `JSON` format. The `JSON` format is basically a way of building up an object out of base types (strings, integers, etc) and lists and dictionaries, in a big tree. 

In a `JSON` declaration:
- Dictionaries are surrounded by `{}` with key/value pairs represented by `"key":"value"`
- Lists are surrounded by `[]`, with items in the list separated by `,`
- Strings are surrounded by `""`
- Numbers are just bare

Note that a `list` can contain `dicts`, `dicts` can have `lists` as the value of a key value pair, etc.

As always, you can set the key of a `dict` using the syntax `dict["key"] = <value>`. 

```
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

# Set the "RELS" key to the scope-resolved MRS predications
mrs["RELS"] = TreePredication(0, "_a_q", ["x3",
                                          TreePredication(1, "_file_n_of", ["x3", "i1"]),
                                          TreePredication(2, "_large_a_1", ["e2", "x3"])])

respond_to_mrs(state, mrs)
```

Thus, the `mrs` variable ends up being a single `json` object that has the MRS definition (that we understand so far) in it.

Now we can create a new function called `respond_to_mrs()` that inspects the MRS and uses the handy `sentence_force()` function to properly respond to a proposition:

```
# Get the SF property of the Index of the MRS
def sentence_force(mrs):
    if "Index" in mrs:
        if mrs["Index"] in mrs["Variables"]:
            if "SF" in mrs["Variables"][mrs["Index"]]:
                return mrs["Variables"][mrs["Index"]]["SF"]


def respond_to_mrs(state, mrs):
    # Collect all the solutions to the MRS against the
    # current world state
    solution = []
    for item in call(vocabulary, state, mrs["RELS"]):
        solution.append(item)

    force = sentence_force(mrs)
    if force == "prop":
        # This was a proposition, so the user only expects
        # a confirmation or denial of what they said.
        # The phrase was "true" if there was at least one answer
        if len(solution) > 0:
            print("Yes, that is true.")
        else:
            print("No, that isn't correct.")
```

Now we can run an example:

```
# Evaluate the proposition: "a file is large"
def Example7():
    state = State([Folder(name="Desktop"),
                   Folder(name="Documents"),
                   File(name="file1.txt", size=2000000),
                   File(name="file2.txt", size=2000000)])

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

    # Set the "RELS" key to the scope-resolved MRS predication tree
    mrs["RELS"] = TreePredication(0, "_a_q", ["x3",
                                              TreePredication(1, "_file_n_of", ["x3", "i1"]),
                                              TreePredication(2, "_large_a_1", ["e2", "x3"])])

    respond_to_mrs(state, mrs)
    
# Outputs:
Yes, that is true.
```

In the [next section](https://blog.inductorsoftware.com/Perplexity/home/pxint/pxint0090SimpleQuestions), we'll respond to questions.

> Comprehensive source for the completed tutorial is available [here](https://github.com/EricZinda/Perplexity/tree/main/samples/hello_world)

Last update: 2024-10-28 by Eric Zinda [[edit](https://github.com/EricZinda/Perplexity/edit/main/docs/pxint/pxint0080SimplePropositions.md)]{% endraw %}