{% raw %}## Simple Questions
Note that the MRS for "Is a file large?" is identical to the proposition "A file is large." *except* that it has a different sentence force of `SF: ques`:

```
[ TOP: h0
INDEX: e2
RELS: < 
[ _a_q LBL: h4 ARG0: x3 [ x PERS: 3 NUM: sg IND: + ] RSTR: h5 BODY: h6 ]
[ _file_n_of LBL: h7 ARG0: x3 [ x PERS: 3 NUM: sg IND: + ] ARG1: i8 ]
[ _large_a_1 LBL: h1 ARG0: e2 [ e SF: ques TENSE: pres MOOD: indicative PROG: - PERF: - ] ARG1: x3 ]
>
HCONS: < h0 qeq h1 h5 qeq h7 > ]

          ┌────── _file_n_of(x3,i8)
_a_q(x3,RSTR,BODY)
               └─ _large_a_1(e2,x3)
```

Handling this can be as simple as responding "yes" or "no". We can add an `elif` clause to our `respond_to_mrs()` function to respond properly:

```
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
            
    elif sentence_force == "ques":
        # This was a question, so the user only expects
        # a yes or no.
        # The phrase was "true" if there was at least one answer
        if len(solution) > 0:
            print("Yes.")
        else:
            print("No.")
            
```

So far, so good. But what if the user says "Which file is large?":

```
[ TOP: h0
INDEX: e2
RELS: < 
[ _which_q LBL: h4 ARG0: x3 [ x PERS: 3 NUM: sg IND: + ] RSTR: h5 BODY: h6 ]
[ _file_n_of LBL: h7 ARG0: x3 [ x PERS: 3 NUM: sg IND: + ] ARG1: i8 ]
[ _large_a_1 LBL: h1 ARG0: e2 [ e SF: ques TENSE: pres MOOD: indicative PROG: - PERF: - ] ARG1: x3 ]
>
HCONS: < h0 qeq h1 h5 qeq h7 > ]
```

The MRS looks *very* similar and still has a `SF: ques` sentence force. However, it used a new quantifier: `_which_q`. `which_q` is simply a way for the MRS to indicate which variable the user is expecting an answer to. In this case: `x3`. These are called "wh" questions in linguistics (i.e. which, what, where, when, who). The quantifier itself doesn't quantify anything, it simply evaluates all the `RSTR` answers against the `BODY` and returns whatever worked. The ERG has several quantifiers that are just "markers"  like this. So, we're going to build a function they can share, called `default_quantifier()`:

```
@Predication(vocabulary, name="_which_q")
def which_q(state, x_variable, h_rstr, h_body):
    yield from default_quantifier(state, x_variable, h_rstr, h_body)


def default_quantifier(state, x_variable, h_rstr, h_body):
    # Find every solution to RSTR
    for solution in Call(vocabulary, state, h_rstr):
        # And return it if it is true in the BODY
        for body_solution in Call(vocabulary, solution, h_body):
            yield body_solution
```

When `_which_q` is in a sentence, we should answer the question with all the values of the variable that it quantifies (`x3` in this case). To do that, we're going to have to build a function that finds the `_which_q` predication, if it exists. Since searching through the tree is something we'll do often, we'll build another helper function called `walk_tree_predications_until` and then use it to build :

```
# walk_tree_predications_until() is a helper function that just walks
# the tree represented by "term". For every predication found,
# it calls func(found_predication)
# If func returns anything besides "None", it quits and
# returns that value
def walk_tree_predications_until(term, func):
    if isinstance(term, list):
        # This is a conjunction, recurse through the
        # items in it
        for item in term:
            result = walk_tree_predications_until(item, func)
            if result is not None:
                return result

    else:
        # This is a single term, call func with it if it is a predication
        if isinstance(term, TreePredication):
            result = func(term)
            if result is not None:
                return result

            # If func didn't say to quit, see if any of its terms are scopal
            # i.e. are predications themselves
            for arg in term.args:
                if not isinstance(arg, str):
                    result = walk_tree_predications_until(arg, func)
                    if result is not None:
                        return result

    return None


# Walk the tree represented by "term" and
# return the predication that matches
# "predicate_name" or "None" if none is found
def FindPredicate(term, predication_name):
    # This function gets called for every predication
    # in the tree. It is a private function since it is 
    # only used here
    def MatchPredicationName(predication):
        if predication[0] == predication_name:
            return predication
        else:
            return None
    
    # Pass our private function to WalkTreeUntil as
    # a way to filter through the tree to find
    # predication_name
    return WalkTreeUntil(term, MatchPredicationName)
```

Now we can update the `RespondToMRS()` function to answer "which" questions with actual values:

```
def respond_to_mrs(state, mrs):
    # Collect all the solutions to the MRS against the
    # current world state
    solutions = []
    for item in call(vocabulary, state, mrs["RELS"]):
        solutions.append(item)

    force = sentence_force(mrs)
    if force == "prop":
        # This was a proposition, so the user only expects
        # a confirmation or denial of what they said.
        # The phrase was "true" if there was at least one answer
        if len(solutions) > 0:
            print("Yes, that is true.")
        else:
            print("No, that isn't correct.")

    elif force == "ques":
        # See if this is a "WH" type question
        wh_predication = find_predication(mrs["RELS"], "_which_q")
        if wh_predication is None:
            # This was a simple question, so the user only expects
            # a yes or no.
            # The phrase was "true" if there was at least one answer
            if len(solutions) > 0:
                print("Yes.")
            else:
                print("No.")
        else:
            # This was a "WH" question
            # return the values of the variable asked about
            # from the solution
            # The phrase was "true" if there was at least one answer
            if len(solutions) > 0:
                wh_variable = wh_predication.args[0]
                for solutions in solutions:
                    print(solutions.get_binding(wh_variable).value)
            else:
                print("I don't know")
```

Now we can run an example:

```
def Example8():
    state = State([Folder(name="Desktop"),
                   Folder(name="Documents"),
                   File(name="file1.txt", size=2000000),
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
                        "e2": {"SF": "ques"}}

    # Set the "RELS" key to the scope-resolved MRS tree
    mrs["RELS"] = TreePredication(0, "_which_q", ["x3",
                                                 TreePredication(1, "_file_n_of", ["x3", "i1"]),
                                                 TreePredication(2, "_large_a_1", ["e2", "x3"])])

    respond_to_mrs(state, mrs)
    
# Prints:
(File(file1.txt, 2000000),)
```

Note that we have a subtle bug in our implementation of `default_quantifier`: we are not yet paying attention to `NUM: sg`.  If there were two large files, they would both get returned in this implementation. Really, they should return a failure since the premise of "which file" is wrong (since there are multiple of them). We'll address that once we get to the section on how to handle plurals.

> Comprehensive source for the completed tutorial is available [here](https://github.com/EricZinda/Perplexity).

Last update: 2024-10-21 by Eric Zinda [[edit](https://github.com/EricZinda/Perplexity/edit/main/docs/pxint/pxint0090SimpleQuestions.md)]{% endraw %}