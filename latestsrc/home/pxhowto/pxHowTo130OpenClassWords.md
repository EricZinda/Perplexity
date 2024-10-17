{% raw %}## Centralizing Nouns and Adjectives
As we've built our vocabulary, there are certain types of words that are basically the same function with small differences.  Look at the code for `_file_n_of` and `_folder_n_of` (both nouns):

```

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
```

They are identical except for the name of the predication (`_file_n_of` vs. `_folder_n_of`) and one line of code:

```
        if isinstance(value, File):
or
        if isinstance(value, Folder):
```

In many applications, whether an object is a `noun` of a particular type is a very simple check and repeating the code over and over would be a lot of wasted work. Of course, you could create a helper function and only have to write the function headers, like this:

```
@Predication(vocabulary, names=["_folder_n_of"])
def folder_n_of(context, state, x_binding, i_binding):
    yield from noun_helper(noun="folder", object_type=folder)
    
@Predication(vocabulary, names=["_file_n_of"])
def file_n_of(context, state, x_binding, i_binding):
    yield from noun_helper(noun="folder", object_type=folder)
```

But that is still a lot of typing and what if all of your nouns are just listed in a data file? Or if you want to return special errors for words you don't know? This alternative also doesn't allow for a data driven approach.

### `match_all` predications
A more general approach is to implement a single function that matches all predications of a certain part-of-speech. Perplexity supports this by allowing you to specify a special predicate called `match_all_n`. It will be called for any noun predication that matches its arguments.  The "lemma" for the predicate will be passed in as an additional first argument ("file" is the *lemma* for `_file_n_of`).  Then, your code can dynamically determine if the binding is of that type.

For the code below, there are two functions not shown:

- `implemented_nouns()` just returns a list of all nouns the application supports
- `sort_of(state, value, noun_type)` returns true if `value` is something of type `noun_type` (which would be a lemma like "file")

How these work is very application specific.  Here's the code for the generalized function:

```
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
```

Note that building a `match_all_n` function requires building a helper function (like `understood_noun(state, noun_lemma)` above) which returns `True` if a lemma is implemented. 

All the code above replaces the original code for `_file_n_of` and `_folder_n_of`. It then requires updating those helper functions as new words are added.  In a system that models objects in some kind of logical ontology, this could be a simple database lookup.

Since the signatures of "file" and "folder" are actually `_file_n_of(x, i)` and `_folder_n_of(x, i)`, and thus have an extra `i` argument compared to what is implemented above, this new function won't actually be called for them.  Instead, we need to build a wrapper that has, but ignores, this `i` argument since it is acting as unused for these predicates:

```
@Predication(vocabulary, names=["match_all_n"], matches_lemma_function=understood_noun)
def match_all_n_i_instances(noun_type, context, state, x_binding, i_binding):
    yield from match_all_n_instances(noun_type, context, state, x_binding):
```

### `match_all` conceptual predications
If you go this route, you'll also probably want to implement the conceptual versions of the nouns, as discussed in the section on [Conceptual Expressions](https://blog.inductorsoftware.com/Perplexity/home/pxhowto/pxHowTo120ConceptsReferringExpressions).  Currently, the conceptual implementation of `_file_n_of` looks like this:

```
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
```

Turning this into the template for any type of conceptual object (and using the `RichConcept` object we implemented in [Conceptual Expressions](https://blog.inductorsoftware.com/Perplexity/home/pxhowto/pxHowTo120ConceptsReferringExpressions)) would look like this:

```

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
```

Note that we are using the `entails` function, not testing equality. As described in  [Conceptual Expressions](https://blog.inductorsoftware.com/Perplexity/home/pxhowto/pxHowTo120ConceptsReferringExpressions), entailment means "implies" and MRS predications really test for entailment. Thus, anything that *entails* file should be true: "large file", "empty file", "slimy pink file", "file I saw yesterday", etc. As long as it is, at its root, a "file", this should be true.

### Matching Other Parts of Speech
`match_all` predications can be used for any part of speech that the grammar supports.  Adjectives can also be very repetitive since they might just check for a particular property on an object. A `match_all_a` predication could be built like this:

```
def handles_adjective(state, adjective_lemma):
    return True
    
@Predication(vocabulary, names=["match_all_a"], matches_lemma_function=handles_adjective)
def match_all_a_concepts(adjective_type, context, state, e_introduced, x_binding):
    ...
```

Any part of speech can be tacked on to the base `match_all_` to create a predication that will match all predicates of that part-of-speech.  Just remember that the arguments need to match too. Normally, though, nouns and adjectives are the only parts of speech that end up templatized like this.

### Interpretations and `match_all`
Often you will have some words that need a special implementation, your `match_all` function won't work. Just like any normal predication, you can create other *interpretations* (alternatives) by just creating more functions. They get run in the order they are in the file.  So, if we wanted the "command" word to have another way it might get interpreted, we'd add this to the file that contains the other `match_all` functions:

```
@Predication(vocabulary, names=["_command_n_1"])
def _command_n_1(context, state, x_binding):
    ...
```

If you *only* want this new predication to run, then you'd also return `False` from the `understood_noun` function written above that tells the system when to call `match_all_n`.


Last update: 2024-10-17 by Eric Zinda [[edit](https://github.com/EricZinda/Perplexity/edit/main/docs/pxHowTo/pxHowTo130OpenClassWords.md)]{% endraw %}