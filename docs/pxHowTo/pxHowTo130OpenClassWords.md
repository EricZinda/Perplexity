## Centralizing Nouns and Adjectives
As we've built our vocabulary, there are certain types of words that are basically the same function, with small differences.  Look at the code for `_file_n_of` and `_folder_n_of` (both nouns):

~~~

@Predication(vocabulary, names=["_file_n_of"])
def file_n_of(context, state, x_binding, i_binding):
    def bound_variable(value):
        if isinstance(value, File):
            return True
        else:
            context.report_error(["valueIsNotX", value, x_binding.variable.name])
            return False

    def unbound_variable():
        for item in state.all_individuals():
            if bound_variable(item):
                yield item

    yield from combinatorial_predication_1(context,
                                           state,
                                           x_binding,
                                           bound_variable,
                                           unbound_variable)


# true for both sets and individuals as long as everything
# in the set is a file
@Predication(vocabulary, names=["_folder_n_of"])
def folder_n_of(context, state, x_binding, i_binding):
    def bound_variable(value):
        if isinstance(value, Folder):
            return True
        else:
            context.report_error(["valueIsNotX", value, x_binding.variable.name])
            return False

    def unbound_variable():
        for item in state.all_individuals():
            if bound_variable(item):
                yield item

    yield from combinatorial_predication_1(context,
                                           state,
                                           x_binding,
                                           bound_variable,
                                           unbound_variable)
~~~

They are identical except for the name of the predication (`_file_n_of` vs. `_folder_n_of`) and one line of code:

~~~
        if isinstance(value, File):
or
        if isinstance(value, Folder):
~~~

In many applications, whether an object is a `noun` of a particular type is a very simple check and repeating the code over and over would be a lot of wasted work. Of course, you could create a helper function and then only have to do the function headers, like this:

~~~
@Predication(vocabulary, names=["_folder_n_of"])
def folder_n_of(context, state, x_binding, i_binding):
    yield from noun_helper(noun="folder", object_type=folder)
    
@Predication(vocabulary, names=["_file_n_of"])
def file_n_of(context, state, x_binding, i_binding):
    yield from noun_helper(noun="folder", object_type=folder)
~~~

But that is still a lot of typing. And, what if all of your nouns are just listed in a data file some way? Or what if you'd like to return special errors for words you don't know? This alternative doesn't allow for a data driven approach.

### `match_all` predications
A more general approach is to implement a single function that matches all predications of a certain part-of-speech. Perplexity supports this by allowing you to specify a special predicate called `match_all_n`. It will be called for any noun predication that has the same arguments it implements.  The "lemma" for the predicate will be passed in as well.  I.e. "file" is the lemma for `_file_n_of`.  Then, your code can dynamically do whatever has to be done to determine if the binding is a thing of that type.

For the code below there are two functions not shown:

- `implemented_nouns()` just returns a list of all nouns the application supports
- `sort_of(state, value, noun_type)` returns true if `value` is something of type `noun_type` (which would be a lemma like "file")

How these work is very application specific.  Here's the code for the generalized function:

~~~
# Returns True if it is a lemma we have modelled in the system
def understood_noun(state, noun_lemma):
    return noun_lemma in implemented_nouns()
 
    
@Predication(vocabulary, names=["match_all_n"], matches_lemma_function=understood_noun)
def match_all_n_instances(noun_type, context, state, x_binding):
    def bound_variable(value):
        if sort_of(state, value, noun_type):
            return True
        else:
            context.report_error(["valueIsNotX", value, x_binding.variable.name])
            return False

    def unbound_variable():
        for item in state.all_individuals():
            if bound_variable(item):
                yield item

    yield from combinatorial_predication_1(context,
                                           state,
                                           x_binding,
                                           bound_variable,
                                           unbound_variable)                                           
~~~

Note building a `match_all_n` function requires building a helper function like `understood_noun(state, noun_lemma)` above which returns true if a lemma is implemented. This code replaces the code for `_file_n_of` and `_folder_n_of` above and then requires updating those helper functions as new words are added.  In a system that models objects in some kind of logical ontology, this could be a simple database lookup.

Since the signatures of "file" and "folder" are actually `_file_n_of(x, i)` and `_folder_n_of(x, i)` and thus have an extra `i` argument compared to what is implemented above, this new function won't actually be called.  Instead, we need to build a wrapper that has, but ignores, this `i` argument since it is acting as unused for these predicates:

~~~
@Predication(vocabulary, names=["match_all_n"], matches_lemma_function=understood_noun)
def match_all_n_i_instances(noun_type, context, state, x_binding, i_binding):
    yield from match_all_n_instances(noun_type, context, state, x_binding):
~~~

### `match_all` conceptual predications
If you go this route, you'll also probably want to implement the conceptual versions of the nouns, as discussed in the section on [Conceptual Expressions](pxHowTo120ConceptsReferringExpressions).  Currently, the conceptual implementation of `_file_n_of` looks like this:

~~~
@Predication(vocabulary, names=["_file_n_of"])
def file_n_of_concept(context, state, x_binding, i_binding):
    def bound_variable(value):
        if isinstance(value, RichConcept) and value == RichConcept("file"):
            return True
        else:
            context.report_error(["valueIsNotX", value, x_binding.variable.name])
            return False

    def unbound_variable():
        yield RichConcept("file")

    yield from combinatorial_predication_1(context,
                                           state,
                                           x_binding,
                                           bound_variable,
                                           unbound_variable)
~~~

Turning this into the template for any type of conceptual object (and using the `RichConcept` object we implemented in [Conceptual Expressions](pxHowTo120ConceptsReferringExpressions)) would look like this:

~~~

@Predication(vocabulary, names=["match_all_n"], matches_lemma_function=understood_noun)
def match_all_n_concepts(noun_type, context, state, x_binding):
    def bound_variable(value):
        if isinstance(value, RichConcept) and value.entails(RichConcept(noun_type)):
            return True
        else:
            context.report_error(["valueIsNotX", value, x_binding.variable.name])
            return False

    def unbound_variable():
        yield RichConcept(noun_type)

    yield from combinatorial_predication_1(context,
                                           state,
                                           x_binding,
                                           bound_variable,
                                           unbound_variable)

@Predication(vocabulary, names=["match_all_n"], matches_lemma_function=understood_noun)
def match_all_n_i_concepts(noun_type, context, state, x_binding, i_binding):
    for new_state in match_all_n_concepts(noun_type, context, state, x_binding):
        yield new_state
~~~

Note that we are using the `entails` function, not testing equality. As described in  [Conceptual Expressions](pxHowTo120ConceptsReferringExpressions), entailment means "implies" and MRS predications really test for entailment. Thus, anything that *entails* file should be true: "large file", "empty file", "slimy pink file", "file I saw yesterday", etc. As long as it is, at its root, a "file", this should be true.

### Matching Other Parts of Speech
`match_all` predications can be used for any part of speech that the grammar supports.  Thus for the English Resource Grammar that we've been using. Since adjectives can often be very repetitive since they might just be checking for a particular property on an object, a `match_all_a` predication could be built like this:

~~~
def handles_adjective(state, adjective_lemma):
    return True
    
@Predication(vocabulary, names=["match_all_a"], matches_lemma_function=handles_adjective)
def match_all_a_concepts(adjective_type, context, state, e_introduced, x_binding):
    ...
~~~

Any part of speech can be tacked on to the base `match_all_` to create a predication that will match all of those predicates.  Just remember that the arguments need to match too. Normally, though, nouns and adjectives are the only parts of speech that end up templatized like this.

### Interpretations and `match_all`
Often you will have some words that really need a special implementation, your `match_all` function is not enough. Just like any normal predication, you can create other *interpretations* (alternatives) by just creating more functions. They get run in the order they are in the file.  So, if we wanted the "command" word to have another way it might get interpreted, we'd add this to the file that contains the other `match_all` functions:

~~~
@Predication(vocabulary, names=["_command_n_1"])
def _command_n_1(context, state, x_binding):
    ...
~~~

If you *only* want this new predication to run, then you'd also return `False` from the `understood_noun` function written above that tells the system when to call `match_all_n`.

