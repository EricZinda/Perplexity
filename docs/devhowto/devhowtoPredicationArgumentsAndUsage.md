# Different Predication Signatures and Usage
In a grammar for a language in DELPH-IN, the same predication name might get called with different sets of arguments depending on how it is used. For example, the verb "delete" (`_delete_v_1`) can be called with these signatures:

- "Delete a file" (includes an implied "actor" ("you") as the first `x` argument): `_delete_v_1(e, x, x)`
- "a file is deleted" (no implied actor, so the first `x` argument is [dropped](devhowtoMRS#other-variables-types-i-u-p) and becomes an `i`): `_delete_v_1(e, i, x)`

Furthermore, if you imagine the implementation of `delete_v_1` for each of those sentences, they are very different. The first needs to actually delete a file and the second should (perhaps) look through the trash to see if a file has been deleted. It seems like we should be smarter in our vocabulary to allow "overloading" and enable different functions to be written for the different cases.

Let's make two other changes to vocabulary tracking while we're there: 
1. Instead of just listing one `name`, we will allow a list of `names` so that synonyms can be easily implemented by just listing them
2. Support having alternative meanings for words that get tried automatically instead of having a big switch statement in a single function. We'll do this by allowing more than one implementation of a predication and keeping them in an ordered list. When evaluating a `call()`, we'll try each one and stop after one succeeds.

We'll do all this by recording both the argument signature (`exx` or `eix` in the example) and sentence force (`prop`, `ques`, or `comm`) in addition to the predication name for every vocabulary implementation. We'll set it up so that all the information can be in the `Predication()` decoration *or* the user can just name things following a convention and we'll derive it:
- `names`: If not specified, the name of the function, minus any phrase_type specifiers (e.g. `_comm`) is used
- `arguments`: If not specified, the `e_`, `x_`, etc. on the argument names is used 
- `phrase_types`: If not specified, any number of `_` separated types at the end is used. (e.g. `_comm` or `_comm_ques`)

~~~
# Fully specified version
@Predication(vocabulary, names=["_delete_v_1"], arguments=["e", "x", "x"], phrase_types=["comm"])
def delete(state, introduced, actor, what):
    
    ....

# Fully defaulted version that means the same thing as the example
# above but uses conventions to specify all the arguments
@Predication(vocabulary)
def _delete_v_1_comm(state, e_introduced, x_actor, x_what):
    
    ....
~~~

As [before](devhowtoMRSToPython), it isn't important to understand how the `Predication()` decorator works, but if you're interested: the final code is [here](https://github.com/EricZinda/Perplexity/blob/main/perplexity/vocabulary.py).

With this, we can now try the same example and get a better error (well, better than crashing, at least):

~~~
? a file is deleted
I don't know the words: delete
~~~

This is a bit confusing since we *do* know the world `delete`, we just don't understand the way it is being used here. 

We can improve this by remembering all the words we know *in any form* in a field (`words`) in the `Vocabulary` object, and creating a simple lookup function for it called `version_exists()`:

~~~
class Vocabulary(object):
    def __init__(self):
        self.all = dict()
        self.words = dict()

    ...
    
    def version_exists(self, delphin_name):
        name_parts = parse_predication_name(delphin_name)
        return name_parts["Lemma"] in self.words

    def add_predication(self, module, function, delphin_names, arguments, phrase_types, first=False):
        
        ...
        
        for delphin_name in delphin_names:
            name_parts = parse_predication_name(delphin_name)
            self.words[name_parts["Lemma"]] = delphin_name

~~~

Then, in the `unknown_words()` function that checks that we know all the words in a phrase, we can use `version_exists()` to record if we know other forms of the word:

~~~
    def unknown_words(self, mrs):
        unknown_words = []
        phrase_type = sentence_force(mrs.index, mrs.variables)
        for predication in mrs.predications:
            argument_types = [argument[1][0] for argument in predication.args.items()]
            predications = list(self.execution_context.vocabulary.predications(predication.predicate, argument_types, phrase_type))
            if len(predications) == 0:
                # This predication is not implemented
                unknown_words.append((predication.predicate,
                                      argument_types,
                                      phrase_type,
                                      # Record if at least one form is understood for
                                      # better error messages
                                      self.execution_context.vocabulary.version_exists(predication.predicate)))

        pipeline_logger.debug(f"Unknown predications: {unknown_words}")
        return unknown_words
~~~

This allows us to create a better error message:

~~~
def generate_message(mrs, error_term):
    
    ...
    
    elif error_constant == "unknownWords":
        lemmas_unknown = []
        lemmas_form_known = []
        for unknown_predication in error_arguments[1]:
            parsed_predicate = parse_predication_name(unknown_predication[0])
            if unknown_predication[3]:
                lemmas_form_known.append(parsed_predicate["Lemma"])
            else:
                lemmas_unknown.append(parsed_predicate["Lemma"])

        answers = []
        if len(lemmas_unknown) > 0:
            answers.append(f"I don't know the words: {', '.join(lemmas_unknown)}")

        if len(lemmas_form_known) > 0:
            answers.append(f"I don't know the way you used: {', '.join(lemmas_form_known)}")

        return " and ".join(answers)
~~~

And now running `Example16()` gives a much better result:
~~~
def Example16():
    ShowLogging("Pipeline")

    state = State([Actor(name="Computer", person=2),
                   Folder(name="Desktop"),
                   Folder(name="Documents"),
                   File(name="file1.txt", size=2000000)])

    user_interface = UserInterface(state, vocabulary)

    while True:
        user_interface.interact_once(respond_to_mrs_tree)
        print()
        
# Running Example16() produces:
? a file is deleted
I don't know the way you used: delete
~~~

> Comprehensive source for the completed tutorial is available [here](https://github.com/EricZinda/Perplexity).
