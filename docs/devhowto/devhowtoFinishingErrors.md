## Adding Errors to Every Predication
Now that our more robust error approach is in place, lets fix the predications we have written before to properly use it.

`large_a_1`, `file_n_of` and `a_q` have already been completed. `delete_v_1`, `pron`, `pronoun_q`, `which_q`, `very_x_deg`, `folder_n_of` remain.

### `folder_n_of`
We can approach `folder_n_of` just like `file_n_of`, and, in fact, that is what most nouns will look like. The only new code is the last line below that says "`x` is not a folder" for the same reasons [we described before](devhowtoReportingAFailure):

~~~
@Predication(vocabulary, name="_folder_n_of")
def folder_n_of(state, x):
    
    ...
    
    for item in iterator:
        # "isinstance" is a built-in function in Python that
        # checks if a variable is an
        # instance of the specified class
        if isinstance(item, Folder):
            # state.SetX() returns a *new* state that
            # is a copy of the old one with just that one
            # variable set to a new value
            new_state = state.SetX(x, item)
            yield new_state
        else:
            ReportError(["xIsNotY", x, "folder"])
~~~

### `which_q`, and `pronoun_q`
The quantifiers `which_q`, and `pronoun_q` should work just like `a_q` did in a [previous section](devhowtoQuantifierErrors) and report a special error if their `RSTR` can't be resolved. If the `BODY` fails it will report its own error:

~~~
# This is just used as a way to provide a scope for a
# pronoun, so it only needs the default behavior
@Predication(vocabulary, name="pronoun_q")
def pronoun_q(state, x, h_rstr, h_body):
    yield from default_quantifier(state, x, h_rstr, h_body)


@Predication(vocabulary, name="_which_q")
def which_q(state, x_variable, h_rstr, h_body):
    yield from default_quantifier(state, x_variable, h_rstr, h_body)


# Many quantifiers are simply markers and should use this as
# the default behavior
def default_quantifier(state, x_variable, h_rstr, h_body):
    # Find every solution to RSTR
    rstr_found = False
    for solution in Call(vocabulary, state, h_rstr):
        rstr_found = True

        # And return it if it is true in the BODY
        for body_solution in Call(vocabulary, solution, h_body):
            yield body_solution

    if not rstr_found:
        # Ignore whatever error the RSTR produced, this is a better one
        ReportError(["doesntExist", ["AtPredication", h_body, x_variable]], force=True)
        
        
# "he/she" deletes a large file
def Example13():
    state = State([Actor(name="Computer", person=2),
                   Folder(name="Desktop"),
                   Folder(name="Documents"),
                   File(name="file1.txt", size=2000000),
                   File(name="file2.txt", size=1000000)])

    mrs = {}
    mrs["Index"] = "e2"
    mrs["Variables"] = {"x3": {"PERS": 3},
                        "e2": {"SF": "prop"}}
    mrs["RELS"] = [["pronoun_q", "x3", ["pron", "x3"],
                    ["_a_q", "x8", [["_large_a_1", "e1", "x8"], ["_file_n_of", "x8"]],
                     ["_delete_v_1", "e2", "x3", "x8"]]]]

    state = state.SetX("mrs", mrs)
    DelphinContext().RespondToMRS(state, mrs)

# Prints:
No, that isn't correct: There isn't pronoun pron in the system
~~~
The error shown from `Example13()` is obviously not the right answer. 

First, for "proposition failures", we can quit saying "No, that isn't correct:". Just saying the error should be enough.

Second, our simple approach of just including the quantifier worked for quantifiers like "a", "the", "some", but not for special "abstract" quantifiers like `pronoun_q` or `which_q`. Abstract quantifiers are predications which don't actually appear in the phrase but were needed by the MRS. They don't start with an "_" and the `ParsePredicationName()` function already detects this and sets "Surface" (meaning "in the original text") to `True` or `False`. So, those are easy enough to detect and ignore:
~~~
# See if this predication in any way contributes words to
# the variable specified. Put whatever it contributes in nlg_data
def RefineNLGWithPredication(variable, predication, nlg_data):
    # Parse the name of the predication to find out its
    # part of speech (POS) which could be a noun ("n"),
    # quantifier ("q"), etc.
    parsed_predication = ParsePredicationName(predication[0])

    # If the predication has this variable as its first argument,
    # it either *introduces* it, or is quantifying it
    if predication[1] == variable:
        if parsed_predication["Pos"] == "q" and parsed_predication["Surface"] is True:
            # It is quantifying it
            nlg_data["Quantifier"] = parsed_predication["Lemma"]
    
    ...

# Example13 now prints:
There isn't a pron in the system
~~~

We are closer! 

We have a similar issue with `pron` in that it is an abstract predication, but our code is treating it like a word from the sentence. In this case, we *do* want to have it contribute to what the variable means, but we'll have to write some code to teach it what all the pronouns are, and to convert the DELPH-IN variable properties to their corresponding pronoun:

~~~
def RefineNLGWithPredication(mrs, variable, predication, nlg_data):
    # Parse the name of the predication to find out its
    # part of speech (POS) which could be a noun ("n"),
    # quantifier ("q"), etc.
    parsed_predication = ParsePredicationName(predication[0])

    # If the predication has this variable as its first argument,
    # it either *introduces* it, or is quantifying it
    if predication[1] == variable:
        if parsed_predication["Pos"] == "q" and parsed_predication["Surface"] is True:
            # It is quantifying it
            nlg_data["Quantifier"] = parsed_predication["Lemma"]
        else:
            if parsed_predication["Surface"] is True:
                # It is introducing it, thus it is the "main" description
                # of the variable, usually a noun predication
                nlg_data["Topic"] = parsed_predication["Lemma"]
            else:
                # Some abstract predications *should* contribute to the
                # English description of a variable
                if parsed_predication["Lemma"] == "pron":
                    nlg_data["Topic"] = PronounFromVariable(mrs, variable)


pronouns = {1: {"sg": "I",
                "pl": "we"},
            2: {"sg": "you",
                "pl": "you"},
            3: {"sg": "he/she",
                "pl": "they"}
            }


def PronounFromVariable(mrs, variable):
    mrs_variable = mrs["Variables"][variable]
    if "PERS" in mrs_variable:
        person = mrs_variable["PERS"]
    else:
        person = 1

    if "NUM" in mrs_variable:
        number = mrs_variable["NUM"]
    else:
        # "sg" is singular in MRS
        number = "sg"

    return pronouns[person][number]

# Example13 now prints:
There isn't a he/she in the system
~~~

Looks good! 

### `pron(x)`
`pron(x)` *does* need an error so that it can report when the user uses a pronoun that we haven't implemented. We can't really form sentences that will use this yet, because everything we can say has `pron` in the `RSTR` and any error we report there will get overridden by the quantifier as [described here](devhowtoQuantifierErrors). We'll add the code, though, so it can be used later.

~~~
@Predication(vocabulary, name="pron")
def pron(state, x_who):
    
    ...
    
        else:
            ReportError(["dontKnowPronoun", x_who])
            
            
def GenerateMessage(mrs, error_term):
    
    ...
    
    elif error_constant == "dontKnowPronoun":
        arg1 = EnglishForDelphinVariable(error_constant, error_arguments[1], mrs)
        return f"I don't know who '{arg1}' is"



~~~


### `very_x_deg`
`very_x_deg` doesn't really *do* anything except give data to other words, so there are no errors to provide there. However, we will eventually have to start reporting errors if the predications don't know how to handle a world like "very". Just ignoring it isn't right. We'll do that in an upcoming section. For now, we'll just leave it as it is:

~~~
@Predication(vocabulary, "_very_x_deg")
def very_x_deg(state, e_introduced, e_target):
    # First see if we have been "very'd"!
    initial_degree_multiplier = DegreeMultiplierFromEvent(state, e_introduced)

    # We'll interpret "very" as meaning "one order of magnitude larger"
    yield state.AddToE(e_target, "DegreeMultiplier", initial_degree_multiplier * 10)
~~~

### `delete_v_1`
The last predication we need to add errors to is `delete_v_1`. We only have to handle the case where someone tries to delete something they shouldn't and when someone besides the "computer" is asked to do the deleting:
~~~
@Predication(vocabulary, name="_delete_v_1")
def delete_v_1(state, e_introduced, x_actor, x_what):
    # We only know how to delete things from the
    # computer's perspective
    if state.GetVariable(x_actor).name == "Computer":
        x_what_value = state.GetVariable(x_what)

        # Only allow deleting files and folders
        if isinstance(x_what_value, (File, Folder)):
            yield state.ApplyOperations([DeleteOperation(x_what_value)])
            
        else:
            ReportError(["cantDo", "delete", x_what])

    else:
        ReportError(["dontKnowActor", x_actor])
        
        
def GenerateMessage(mrs, error_term):
    
    ...
    
    elif error_constant == "dontKnowActor":
        arg1 = EnglishForDelphinVariable(error_constant, error_arguments[1], mrs)
        return f"I don't know who '{arg1}' is"

    elif error_constant == "cantDo":
        arg1 = error_arguments[1]
        arg2 = EnglishForDelphinVariable(error_constant, error_arguments[2], mrs)
        return f"I can't {arg1} {arg2}"
~~~

To see the result we also need to update `RespondToMRS()` to use our new error reporting for commands:

~~~
    def RespondToMRS(self, state, mrs):
    
        ...
        
        elif sentence_force == "comm":
            if len(solutions) > 0:
                
                ...
                
            else:
                message = GenerateMessage(mrs, self.Error())
                print(message)
~~~

Now we can run the example we saw much earlier, "Delete you":

~~~
# delete you
def Example8():
    state = State([Actor(name="Computer", person=2),
                   Folder(name="Desktop"),
                   Folder(name="Documents"),
                   File(name="file1.txt", size=2000000),
                   File(name="file2.txt", size=1000000)])

    mrs = {}
    mrs["Index"] = "e2"
    mrs["Variables"] = {"x3": {"PERS": 2},
                        "x8": {"PERS": 2},
                        "e2": {"SF": "comm"}}
    mrs["RELS"] = [["pronoun_q", "x3", ["pron", "x3"], ["pronoun_q", "x8", ["pron", "x8"], ["_delete_v_1", "e2", "x3", "x8"]]]]
    state = state.SetX("mrs", mrs)

    DelphinContext().RespondToMRS(state, mrs)
    
# Prints:
I can't delete a you
~~~
First: Notice that it is using the code for transforming ("realizing" in linguistics) `pron` in English to say "you".  But the error itself isn't quite right.  It shouldn't say "a you".

The last trick is figuring out when a quantifier like "a" should be used added to a word. This is getting pretty deep into Natural Language Generation, which is a whole tutorial in itself. In this case, though, we can do something simple: we'll create a special word `<none>` that is used when an abstract quantifier is detected. When `ConvertToEnglish()` sees it, it won't add a default "a" to the word:

~~~
def RefineNLGWithPredication(mrs, variable, predication, nlg_data):
    parsed_predication = ParsePredicationName(predication[0])
    if predication[1] == variable:
        if parsed_predication["Pos"] == "q":
            if parsed_predication["Surface"] is True:
                nlg_data["Quantifier"] = parsed_predication["Lemma"]
            else:
                # abstract quantifiers *shouldn't* contribute a quantifier
                # at all, so set a special value
                nlg_data["Quantifier"] = "<none>"


# Takes the information gathered in the nlg_data dictionary
# and converts it, in a very simplistic way, to English
def ConvertToEnglish(nlg_data):
    phrase = ""

    if "Quantifier" in nlg_data:
        if nlg_data["Quantifier"] != "<none>":
            phrase += nlg_data["Quantifier"] + " "
    else:
        phrase += "a "

    if "Modifiers" in nlg_data:
        # " ".join() takes a list and turns it into a string
        # with the string " " between each item
        phrase += " ".join(nlg_data["Modifiers"]) + " "

    if "Topic" in nlg_data:
        phrase += nlg_data["Topic"]
    else:
        phrase += "thing"

    return phrase
        
        
# Example8 now prints:
I can't delete you
~~~

Writing a test for the other error is impossible at the moment because we need more predications to say things like "Bill deletes a file".

### Errors from Questions
We still need to update the last type of sentence (`ques`) to return proper errors:

~~~
    def RespondToMRS(self, state, mrs):
        
        ...
        
        elif sentence_force == "ques":
            # See if this is a "WH" type question
            wh_predication = FindPredicate(mrs["RELS"], "_which_q")
            if wh_predication is None:
                # This was a simple question, so the user only expects
                # a yes or no.
                # The phrase was "true" if there was at least one answer
                if len(solutions) > 0:
                    print("Yes.")
                else:
                    message = GenerateMessage(mrs, self.Error())
                    print(f"{message}")
            else:
                # This was a "WH" question
                # return the values of the variable asked about
                # from the solution
                # The phrase was "true" if there was at least one answer
                if len(solutions) > 0:
                    wh_variable = wh_predication[1]
                    for solution in solutions:
                        print(solution.GetVariable(wh_variable))
                else:
                    message = GenerateMessage(mrs, self.Error())
                    print(f"{message}")
~~~

Now we can run some tests:

~~~
# Evaluate the proposition: "which file is large?" if there are no files
def Example14():
    state = State([Folder(name="Desktop"),
                   Folder(name="Documents")])

    mrs = {}
    mrs["Index"] = "e1"
    mrs["Variables"] = {"x1": {"NUM": "sg"},
                        "e1": {"SF": "ques"}}
    mrs["RELS"] = [["_which_q", "x1", ["_file_n_of", "x1"], ["_large_a_1", "e1", "x1"]]]

    state = state.SetX("mrs", mrs)
    DelphinContext().RespondToMRS(state, mrs)
    
# Prints:
There isn't which file in the system
~~~
To fix this, we need to update `RefineNLGWithPredication()` to ignore the "which_q" predication

~~~
def RefineNLGWithPredication(mrs, variable, predication, nlg_data):
    # Parse the name of the predication to find out its
    # part of speech (POS) which could be a noun ("n"),
    # quantifier ("q"), etc.
    parsed_predication = ParsePredicationName(predication[0])

    # If the predication has this variable as its first argument,
    # it either *introduces* it, or is quantifying it
    if predication[1] == variable:
        if parsed_predication["Pos"] == "q":
            if parsed_predication["Surface"] is True:
                if parsed_predication["Lemma"] not in ["which"]:
                    # It is quantifying it
                    nlg_data["Quantifier"] = parsed_predication["Lemma"]
                    
# Now Example14() prints:
There isn't a file in the system
~~~
Very nice!
