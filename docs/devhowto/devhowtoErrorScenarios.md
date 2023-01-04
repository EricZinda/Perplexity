## Error Scenarios
We've gone through a lot to improve the error handling of the system. Now, let's compare where we started and finished by going through some scenarios:


> Example5_1 World: Has files, but no large ones. 
> 
> User: "a file is large"
> 
> Old: "No, that isn't correct"
> 
> New: "a file is not large"

Pretty good. 

What if there are no files at all?
> Example5_2 World: Has no files. 
> 
> User: "a file is large"
> 
> Old: "No, that isn't correct"
> 
> New: "There isn't a file in the system"

That one is very clear.

> Example9 World: Has files, but no large ones. 
> 
> User: "delete a large file"
> 
> Old: "Couldn't do that"
> 
> New: "There isn't a file in the system"

This one is correct *except* that our NLG functions don't know how to add "large" in there. Let's update them to understand (some) adjectives:

~~~
# See if this predication in any way contributes words to
# the variable specified. Put whatever it contributes in nlg_data
def RefineNLGWithPredication(mrs, variable, predication, nlg_data):
    # Parse the name of the predication to find out its
    # part of speech (POS) which could be a noun ("n"),
    # quantifier ("q"), etc.
    parsed_predication = ParsePredicationName(predication[0])
    
    ...
    
    # Assume that adjectives that take the variable as their first argument
    # are adding an adjective modifier to the phrase
    elif parsed_predication["Pos"] == "a" and predication[2] == variable:
        if "Modifiers" not in nlg_data:
            nlg_data["Modifiers"] = []

        nlg_data["Modifiers"].append(parsed_predication["Lemma"])


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
~~~
Now it properly responds with "There isn't a *large* file in the system". Great!

> Example13 World: Has large files. 
> 
> User: "He deletes a large file"
> 
> Old: "Couldn't do that"
> 
> New: "There isn't a he/she in the system"

Great! It clearly says *why* the system couldn't do it now.
