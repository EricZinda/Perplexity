## Responding to Simple Propositions
"Propositions" are sentences that declare something to be true like "A file is very large". If true, a human would expect something like "yep, you are right" or "correct!" or "yes, this is true" as a response (error cases will be [handled later](devhowtoChoosingWhichFailure)). A phrase is a proposition if the "sentence force" (SF) property of its MRS `index` variable is `prop` as [described in the previous section](devhowtoSentenceForce).

Below is the MRS for "A file is very large". As described in the [previous section](devhowtoSentenceForce): The `INDEX = e2`, and `e2` has a sentence force of "proposition": `SF: prop`.
~~~
[ TOP: h0
INDEX: e2
RELS: < 
[ _a_q LBL: h4 ARG0: x3 [ x PERS: 3 NUM: sg IND: + ] RSTR: h5 BODY: h6 ]
[ _file_n_of LBL: h7 ARG0: x3 [ x PERS: 3 NUM: sg IND: + ] ARG1: i8 ]
[ _very_x_deg LBL: h1 ARG0: e9 [ e SF: prop TENSE: untensed MOOD: indicative PROG: - PERF: - ] ARG1: e2 ]
[ _large_a_1 LBL: h1 ARG0: e2 [ e SF: prop TENSE: pres MOOD: indicative PROG: - PERF: - ] ARG1: x3 ]
>
HCONS: < h0 qeq h1 h5 qeq h7 > ]

          ┌────── _file_n_of(x3,i8)
_a_q(x3,RSTR,BODY)    ┌── _very_x_deg(e9,e2)
               └─ and(0,1)
                        └ _large_a_1(e2,x3)
~~~

In order to start responding to user phrases properly, we need to begin passing in more information from the MRS, not just the predications.  We'll need the variable properties and the `INDEX`. We'll do this using a dictionary. In fact, we can make it easier to read using the Python `json` format. The `json` format is basically a way of building up an object out of base types (strings, integers, etc) and lists and dictionaries, in a big tree. 

In a `json` declaration:
- Dictionaries are surrounded by `{}` with key/value pairs represented by `"key":"value"`
- Lists are surrounded by `[]`, with items in the list separated by `,`
- Strings are surrounded by `""`
- Numbers are just bare

Note that a `list` can contain `dicts`, `dicts` can have `lists` as the value of a key value pair, etc.

As always, you can set the key of a `dict` using the syntax `dict["key"] = <value>`. 

~~~
# Start with an empty dictionary
mrs = {}

# Set its "index" key to the value "e1"
mrs["Index"] = "e1"

# Set its "Variables" key to *another* dictionary with 
# two keys: "x1" and "e1". Each of those has a "value" of 
# yet another dictionary that holds the properties of the variables
mrs["Variables"] = {"x1": {"NUM": "pl"},
                    "e1": {"SF": "prop"}}
                    
# Set the "RELS" key to the scope-resolved MRS tree, using our format
mrs["RELS"] = [["_a_q", "x1", ["_file_n_of", "x1"], ["_large_a_1", "e1", "x1"]]]
~~~
Thus, the `mrs` variable ends up being a big, single `json` object that has the MRS definition (that we understand so far) in it.

Now we can create a new function called `RespondToMRS()` that inspects the MRS to properly respond to a proposition:

~~~
def RespondToMRS(state, mrs):
    # Collect all the solutions to the MRS against the
    # current world state
    solution = []
    for item in Call(vocabulary, state, mrs["RELS"]):
        solution.append(item)
    
    index_variable = mrs["Index"]
    sentence_force = mrs["Variables"][index_variable]["SF"]
    if sentence_force == "prop":
        # This was a proposition, so the user only expects
        # a confirmation or denial of what they said.
        # The phrase was "true" if there was at least one answer
        if len(solution) > 0:
            print("Yes, that is true.")
        else:
            print("No, that isn't correct.")
            
            
# Evaluate the proposition: "a file is large"
def Example5():
    state = State([Folder(name="Desktop"),
                   Folder(name="Documents"),
                   File(name="file1.txt", size=2000000),
                   File(name="file2.txt", size=2000000)])

    # Start with an empty dictionary
    mrs = {}
    
    # Set its "index" key to the value "e1"
    mrs["Index"] = "e1"
    
    # Set its "Variables" key to *another* dictionary with 
    # two keys: "x1" and "e1". Each of those has a "value" of 
    # yet another dictionary that holds the properties of the variables
    mrs["Variables"] = {"x1": {"NUM": "pl"},
                        "e1": {"SF": "prop"}}
                        
    # Set the "RELS" key to the scope-resolved MRS tree, using our format
    mrs["RELS"] = [["_a_q", "x1", ["_file_n_of", "x1"], ["_large_a_1", "e1", "x1"]]]

    RespondToMRS(state, mrs)

# Outputs:
Yes, that is true.
~~~

In the [next section](devhowtoSimpleQuestions), we'll respond to questions.