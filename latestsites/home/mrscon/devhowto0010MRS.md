{% raw %}## The Minimal Recursion Semantics (MRS) Format
> This section is designed to give application developers an *overview* of the Minimal Recursion Semantics format which is the primary artifact used by DELPH-IN to represent the meaning of a phrase. For a deeper dive into MRS, or one that has a more academic or linguistic approach, explore [Minimal Recursion Semantics: An Introduction](https://www.cl.cam.ac.uk/~aac10/papers/mrs.pdf).

The DELPH-IN [English Resource Grammar (ERG)](https://delph-in.github.io/docs/erg/ErgTop/) converts an English phrase into a data structure called an ["Minimal Recursion Semantics Formalism" (MRS)](https://www.cl.cam.ac.uk/~aac10/papers/mrs.pdf) which is a technical representation of human language. The [ACE processor](http://sweaglesw.org/linguistics/ace/), among other processors, processes the grammar and the phrase to produce the MRS formalism and represent it in one of several formats, such as [Simple MRS](https://delph-in.github.io/docs/tools/MrsRFC/). Processors can be used with any of the [other DELPH-IN grammars](https://delph-in.github.io/docs/grammars/GrammarsOverview/) to convert other natural languages into the MRS format. While the examples below use English, the concepts apply across the DELPH-IN grammars.

Because language is ambiguous, most phrases parse into more than one MRS document, each representing a different interpretation of the phrase. Each MRS document encodes one high-level meaning of the phrase into a list of predicate-logic-like predicates (called *predications*).

Each MRS document *also* has multiple interpretations. Using constraints that are included as part of the MRS, a set of trees (called *well-formed trees*) can be built from the flat list of predications in a given MRS.  These well-formed trees define all the alternative meanings of that particular MRS.

So, a phrase generates `n` MRS documents, each of those generates `m` well-formed trees, which results in `n x m` possible interpretations of a single phrase. One of the challenges of building a system that uses natural language is to determine which of the many possible meanings was intended by the user (one approach to doing this will be discussed in the conceptual topic: [Determining the Right Parse and Tree](https://blog.inductorsoftware.com/Perplexity/home/devcon/devcon0060WhichParseAndTree)).

For example, the phrase: "Look under the table." produces 12 different MRS documents (also called "parses" or "interpretations"). These include interpretations that mean: 

1. "Look (at whatever is) under the table" 
2. "Look (around while you are) under the table" 

... among 10 others. 

The MRS document for the first interpretation is:
```
[ TOP: h0
INDEX: e2
RELS: < 
[ _the_q LBL: h10 ARG0: x9 [ x PERS: 3 NUM: sg IND: + ] RSTR: h11 BODY: h12 ]
[ _table_n_1 LBL: h13 ARG0: x9 [ x PERS: 3 NUM: sg IND: + ] ]
[ pronoun_q LBL: h4 ARG0: x3 [ x PERS: 2 PT: zero ] RSTR: h5 BODY: h6 ]
[ pron LBL: h7 ARG0: x3 [ x PERS: 2 PT: zero ] ]
[ _under_p_dir LBL: h1 ARG0: e8 [ e SF: prop TENSE: untensed MOOD: indicative PROG: - PERF: - ] ARG1: e2 ARG2: x9 ]
[ _look_v_1 LBL: h1 ARG0: e2 [ e SF: comm TENSE: pres MOOD: indicative PROG: - PERF: - ] ARG1: x3 ]
>
HCONS: < h0 qeq h1 h5 qeq h7 h11 qeq h13 > ]
```

Using the constraints described in the `HCONS` section (which we will describe later), there are two well-formed trees that can be built from that MRS, which describe the two alternatives that *it* could mean:

```
            ┌────── _table_n_1(x9)
_the_q(x9,RSTR,BODY)               ┌────── pron(x3)
                 └─ pronoun_q(x3,RSTR,BODY)    ┌── _under_p_dir(e8,e2,x9)
                                        └─ and(0,1)
                                                 └ _look_v_1(e2,x3)

               ┌────── pron(x3)
pronoun_q(x3,RSTR,BODY)            ┌────── _table_n_1(x9)
                    └─ _the_q(x9,RSTR,BODY)    ┌── _under_p_dir(e8,e2,x9)
                                        └─ and(0,1)
                                                 └ _look_v_1(e2,x3)
```

The rest of this section will give you a base understanding of the MRS format so that we can explore how to build these well-formed trees in a [later section](https://blog.inductorsoftware.com/Perplexity/home/mrscon/devhowto0020WellFormedTree) and ultimately write software that derives the speaker's intended meaning from them.  Deriving their intended meaning is the topic of this entire tutorial.

## Underspecification
A DELPH-IN parser like [ACE](http://sweaglesw.org/linguistics/ace/) will usually generate more than one MRS document representing the various high-level interpretations of a phrase. Each one contains a *list* of predicate-logic-like predications and not a *tree* like you'll see in many natural language systems.  That's because it is *underspecified*.  Even though the parser has already done one level of interpretation on the phrase, there are still (usually) multiple ways to interpret *that*.  

The final interpretations of a phrase are called "well-formed MRS trees". The MRS document doesn't pick a primary interpretation by choosing a specific tree, it provides the rules for building *all of them*. That's what "underspecified" means. `Every book is in a cave` could mean "all books are in the same cave" or "every book is in a (possibly different) cave". Given just the phrase, it isn't clear which the speaker intended, so the MRS provides all the alternatives. Context (which the MRS doesn't have) usually helps to decide which is meant.

This section will go through the entire MRS document in detail, but as a navigational guide to the format itself: The list of predicate-logic-like predications in provided in the `RELS` section of the MRS document:
```
...

RELS: < 
[ _the_q LBL: h10 ARG0: x9 [ x PERS: 3 NUM: sg IND: + ] RSTR: h11 BODY: h12 ]
[ _table_n_1 LBL: h13 ARG0: x9 [ x PERS: 3 NUM: sg IND: + ] ]
[ pronoun_q LBL: h4 ARG0: x3 [ x PERS: 2 PT: zero ] RSTR: h5 BODY: h6 ]
[ pron LBL: h7 ARG0: x3 [ x PERS: 2 PT: zero ] ]
[ _under_p_dir LBL: h1 ARG0: e8 [ e SF: prop TENSE: untensed MOOD: indicative PROG: - PERF: - ] ARG1: e2 ARG2: x9 ]
[ _look_v_1 LBL: h1 ARG0: e2 [ e SF: comm TENSE: pres MOOD: indicative PROG: - PERF: - ] ARG1: x3 ]
>

...
```

... and the `HCONS` section lists the constraints on putting the predications together to create a well-formed tree which represents a single meaning:

```
... 

HCONS: < h0 qeq h1 h5 qeq h7 h11 qeq h13 > ]
```

The MRS is underspecified, and the `RELS` together with the `HCONS` provide the information to make it specific and recover the various possible meanings.

## Predications
A phrase is converted into a list of predicate-logic like predications in the MRS which you can see in the `RELS` section of the MRS for "Look under the table":

```
...

RELS: < 
[ _the_q LBL: h10 ARG0: x9 [ x PERS: 3 NUM: sg IND: + ] RSTR: h11 BODY: h12 ]
[ _table_n_1 LBL: h13 ARG0: x9 [ x PERS: 3 NUM: sg IND: + ] ]
[ pronoun_q LBL: h4 ARG0: x3 [ x PERS: 2 PT: zero ] RSTR: h5 BODY: h6 ]
[ pron LBL: h7 ARG0: x3 [ x PERS: 2 PT: zero ] ]
[ _under_p_dir LBL: h1 ARG0: e8 [ e SF: prop TENSE: untensed MOOD: indicative PROG: - PERF: - ] ARG1: e2 ARG2: x9 ]
[ _look_v_1 LBL: h1 ARG0: e2 [ e SF: comm TENSE: pres MOOD: indicative PROG: - PERF: - ] ARG1: x3 ]
>

...
```

Predications are "predicate-logic-like" in that they state a relation or a fact about their arguments that must be true in order for the MRS to be true. The arguments are most often variables and, if you find values for all the variables that make all the predications in the MRS true in a given world, then you have "solved" or "resolved" the MRS. You have figured out (in a sense) the meaning of the sentence. So, predications do the work in an MRS by providing constraints or restrictions on the variables they are passed. 

For example: the predication `_table_n_1(x9)` in the example above is saying "restrict the set of things in the variable `x9` to be only those which are a 'table'" or, alternatively: "ensure that `x9` contains a 'table'".  Depending on how you ultimately solve the MRS, you might look at these variables as containing sets or individual items. Our approach will start by iteratively solving the MRS using individual items, so we'll be describing predications as restricting to individual items for the rest of the tutorial.

If we evaluated a different predication such as `_large_a_1(x9)` immediately afterward, it would mean "also make sure the thing in `x9` is 'large'".  An MRS that contains both predications like that is saying, "restrict `x9` to be a 'large table' from the world we are talking about".

We'll get into the other examples later after we've covered more basics.

### Predication Labels
Each predication has a label in the MRS, indicated by `LBL:`. The label serves as an ID or a pointer to the predication. Note that predications *can* share the same label. In fact, this is how the MRS indicates they are "in conjunction" (i.e. should be interpreted together using a logical "and", as in the above example).

Look at the labels for the different predications in an MRS for "Look under the large table" and note that `_large_a_1` and `_table_n_1` share the same label, indicating they are "in conjunction":
```
[ TOP: h0
INDEX: e2
RELS: < [ _the_q LBL: h10 ARG0: x9 [ x PERS: 3 NUM: sg IND: + ] RSTR: h11 BODY: h12 ]
[ _large_a_1 LBL: h13 ARG0: e14 [ e SF: prop TENSE: untensed MOOD: indicative PROG: bool PERF: - ] ARG1: x9 ]
[ _table_n_1 LBL: h13 ARG0: x9 [ x PERS: 3 NUM: sg IND: + ] ]
[ pronoun_q LBL: h4 ARG0: x3 [ x PERS: 2 PT: zero ] RSTR: h5 BODY: h6 ]
[ pron LBL: h7 ARG0: x3 [ x PERS: 2 PT: zero ] ]
[ _under_p_dir LBL: h1 ARG0: e8 [ e SF: prop TENSE: untensed MOOD: indicative PROG: - PERF: - ] ARG1: e2 ARG2: x9 ]
[ _look_v_1 LBL: h1 ARG0: e2 [ e SF: comm TENSE: pres MOOD: indicative PROG: - PERF: - ] ARG1: x3 ]
>
HCONS: < h0 qeq h1 h5 qeq h7 h11 qeq h13 > ]
```

These labels are used to turn the flat list of predications into the set of well-formed trees that represent its various meanings. The section below on scopal arguments gives an overview of how this works. The [Well-Formed Trees topic](https://blog.inductorsoftware.com/Perplexity/home/mrscon/devhowto0020WellFormedTree) describes it in detail.

### Predication Names
The name of a predication, for example, `_table_n_1`, encodes important information about it:
- The "lemma" or root word (this is the first word you see): "table"
- Whether it was actually seen in the text (starts with `_`) or added abstractly by the grammar (no initial `_`)
- Its part of speech. The `_n_` in `_table_n_1` means "table" is a "noun". The `_q` in `_the_q` means "the" is a "quantifier" (quantifiers are described below)
- It may have extras at the end like `_1` to indicate which "variant" or synonym of the word it represents

There is some documentation for what the predications *mean*, which can be found by doing a search of the documentation. Otherwise, their meaning can often be determined by looking at the MRS and intuiting what they are trying to do using your knowledge of the language. If all else fails, you can [post on the message boards](https://delphinqa.ling.washington.edu/).  

### Predication Arguments and Variables
Predications have arguments with names like `ARG0`, `ARG1`, `ARG2`, `RSTR`, `BODY`, etc.  Think of those exactly like the name of named arguments in some programming languages such as Python.

They also have variables assigned to the arguments like `x5`, `h1`, `e6`.  The initial letter in the name indicates the "type" of variable it is.  The types create a hierarchy, with the bottommost "leaves" being the types that are the most concrete and most common in predications. Each of these types will be discussed below:

```
    u
   / \
  i   p
 / \ / \
e   x   h
```

The number on a variable just makes it unique. When the same variable name appears in more than one place it is shared, just like if you used a Python variable in more than one place in a function.\
So, if an MRS has two predications like this:

```
[ _large_a_1 LBL: h13 ARG0: e14 [ e SF: prop TENSE: untensed MOOD: indicative PROG: bool PERF: - ] ARG1: x9 ]
[ _table_n_1 LBL: h13 ARG0: x9 [ x PERS: 3 NUM: sg IND: + ] ]
```

... you can see that:
- `_large_a_1` has two arguments: `ARG0` and `ARG1`, and the variables assigned to them are: `e14` and `x9`. The first is of type `event` (`e`) and the second is of type `instance` (`x`)
- `_table_n_1` shares `x9` in its `ARG0` and so both predications are restricting the same variable. This means that, ultimately, `x9` should contain only "large tables"

Thinking of MRS variables as variables in a math equation can help: The MRS is effectively defining a formula with variables. If you pick variable values such that the MRS is true for a given world, then you have understood the meaning of the MRS in that world.

Of all the arguments, `ARG0` is special.  It holds a variable that "represents" the predication, sometimes called the "characteristic" or "distinguished" variable, but most often the "instrinsic variable".  If you read the [Minimal Recursion Semantics: An Introduction](https://www.cl.cam.ac.uk/~aac10/papers/mrs.pdf) documentation, you'll see the term "introduced" is used to describe the intrinsic variable.  A predicate is described as "introducing" its "intrinsic variable" (which is always `ARG0`). Sometimes phrases like "the variable *introduced by* predicate X..." are used.  This will become important later, mostly when we talk about [events](https://blog.inductorsoftware.com/Perplexity/home/pxhowto/pxHowTo050EventPredications) or about how to [convert predications back into a phrase](https://blog.inductorsoftware.com/Perplexity/home/pxint/pxint0120ErrorsConceptualFailures). For now, it is enough to understand that `ARG0` *represents* the predication in some special ways.

One final point: Every variable in an MRS is introduced by exactly one predication in the MRS (which is why they can serve as makeshift "representations" of the predication). We'll come back to this when we [talk about `i`, `p` and `u` variable types]().

#### H (Handle) Variables, aka "Scopal Arguments"
The semantic meaning of an MRS is ultimately represented by a *tree* (described in the [next topic](https://blog.inductorsoftware.com/Perplexity/home/mrscon/devhowto0020WellFormedTree)) and handle variables passed to predications (aka "scopal arguments") provide the mechanism to build a tree from the list of predications.

Handle variables represent the "holes" where branches of the tree can be placed. To do this, handle variables are set to the `LBL` of another predication. As described above, the MRS `LBL` field serves as a way to "label" each predication with a unique identifier. Thus, the `LBL:` of a predication can be assigned to a handle variable in a different predication to indicate that it should be placed there. By assigning `LBL:`s to holes like that, an entire tree can be built.

When a tree is built and being resolved, a predication with handle arguments is expected to use those branches to do ... whatever it is supposed to do. For example, the `_the_q` has two handle arguments, `h5` and `h6` in the MRS for "The dog is small":

```
[ TOP: h0
INDEX: e2
RELS: < 
[ _the_q LBL: h4 ARG0: x3 [ x PERS: 3 NUM: sg IND: + ] RSTR: h5 BODY: h6 ]
[ _dog_n_1 LBL: h7 ARG0: x3 [ x PERS: 3 NUM: sg IND: + ] ]
[ _small_a_1 LBL: h1 ARG0: e2 [ e SF: prop TENSE: pres MOOD: indicative PROG: - PERF: - ] ARG1: x3 ]
>
HCONS: < h0 qeq h1 h5 qeq h7 > ]
```

In building a tree, we have assigned `LBL: h7` to `h5` and `LBL: h1` to `h6`:

```
            ┌────── _dog_n_1(x3)
_the_q(x3,RSTR,BODY)
                 └─ _small_a_1(e2,x3)
```

Think of this process like a lambda function being passed to a function in a programming language like C++ or C#.  The `the_q` predication itself will be responsible for "doing something" with the two branches it is passed.  What, exactly, is specific to the predication. We go into this more in the section on  [solving scopal arguments](https://blog.inductorsoftware.com/Perplexity/home/pxint/pxint0060ScopalArguments). For now, think about scopal arguments as places to put other predications which are acting like programming language "lambda functions".

Because the MRS is underspecified, it usually doesn't directly list which predication to put in which scopal argument. You figure that out by the process of [creating a well-formed tree](https://blog.inductorsoftware.com/Perplexity/home/mrscon/devhowto0020WellFormedTree).  However, if a predication has a `LBL` that is the same handle as a scopal argument, then that part of the tree *has* been specified and is "locked in place" (i.e. there is no hole there for something else to be).

#### X (Instance) Variables
Instance (`x`) variables are just like normal First Order Logic variables, or like variables in popular programming languages. The types of things they can contain are "individuals", which is another name for a "thing in the world".  They hold the things the speaker is talking about.

In the MRS for "Look under the large table":

```
[ TOP: h0
INDEX: e2
RELS: < 
[ _the_q LBL: h10 ARG0: x9 [ x PERS: 3 NUM: sg IND: + ] RSTR: h11 BODY: h12 ]
[ _large_a_1 LBL: h13 ARG0: e14 [ e SF: prop TENSE: untensed MOOD: indicative PROG: bool PERF: - ] ARG1: x9 ]
[ _table_n_1 LBL: h13 ARG0: x9 [ x PERS: 3 NUM: sg IND: + ] ]
[ pronoun_q LBL: h4 ARG0: x3 [ x PERS: 2 PT: zero ] RSTR: h5 BODY: h6 ]
[ pron LBL: h7 ARG0: x3 [ x PERS: 2 PT: zero ] ]
[ _under_p_dir LBL: h1 ARG0: e8 [ e SF: prop TENSE: untensed MOOD: indicative PROG: - PERF: - ] ARG1: e2 ARG2: x9 ]
[ _look_v_1 LBL: h1 ARG0: e2 [ e SF: comm TENSE: pres MOOD: indicative PROG: - PERF: - ] ARG1: x3 ]
>
HCONS: < h0 qeq h1 h5 qeq h7 h11 qeq h13 > ]
```

... there are only two instance variables that represent the "things in the world being talked about":
- `x9`: "the large table"
- `x3`: "you". This is implied since it is a command. I.e. "[You] look under the large table". You can tell it wasn't in the original phrase because the predication doesn't start with `_`.

The other variables in the MRS are there to help build up the tree (`h` variables, described previously) or allow predications to refer to each other (`e` variables, described next).  `x` variables are the most concrete type of variable that maps most obviously to what is being said in the phrase.

Note that instance variables are always *scoped* by a quantifier when a well-formed tree is built. Quantifiers are described later, but for now think of them as a predication named with `_q` and with the argument structure: (`x`, `h`, `h`). The first argument of the quantifier, `x`, is the variable being "scoped", and the two branches in its scopal arguments are the only branches allowed to use that particular `x` variable.  That's what "scoped by a quantifier" means. This is important to know when creating [well-formed trees](https://blog.inductorsoftware.com/Perplexity/home/mrscon/devhowto0020WellFormedTree) but also helps explain some of the uses of other variable types later in this section.

#### E (Event) Variables
Event variables have a rich history and lot of fascinating conceptual linguistic background to them (Davidson 1967a is a good start), but for our purposes, we can think of them as holding a "bag of information" (represented in code as a dictionary, perhaps). Predications *introduce* them to provide a place for other predications to hang information that will be used by the introducer. 

For example, event variables are used by adverbs like "slowly" as in, "move slowly", to provide the `move` predication with information about *how* to move. `slowly` does this by adding data to the event variable that `move` introduces. You can see in the MRS below for "move slowly" that `_slow_a_1` is passed the `e2` event variable that `_move_v_1` introduces:

```
[ TOP: h0
INDEX: e2
RELS: < 
[ pronoun_q LBL: h4 ARG0: x3 [ x PERS: 2 PT: zero ] RSTR: h5 BODY: h6 ]
[ pron LBL: h7 ARG0: x3 [ x PERS: 2 PT: zero ] ]
[ _slow_a_1 LBL: h1 ARG0: e8 [ e SF: prop TENSE: untensed MOOD: indicative PROG: - PERF: - ] ARG1: e2 ]
[ _move_v_1 LBL: h1 ARG0: e2 [ e SF: comm TENSE: pres MOOD: indicative PROG: - PERF: - ] ARG1: x3 ]
>
HCONS: < h0 qeq h1 h5 qeq h7 > ]
```

The `_slow_a_1` predication is passed the `e2` argument so that it can attach data about "*how* to do something" to the event. `_move_v_1` needs `e2` passed to it so that it can inspect it and determine how to do the "moving".  

Events can also be used to add information about *where* to do something. For example, in "go to the store", "to" is one of many prepositions that can be used with "go" to say *where* to go. So, if a preposition like "to" is in the phrase, it modifies the event that "go" introduces:

```
[ TOP: h0
INDEX: e2
RELS: < 
[ _the_q LBL: h10 ARG0: x9 [ x PERS: 3 NUM: sg IND: + ] RSTR: h11 BODY: h12 ]
[ _store_n_1 LBL: h13 ARG0: x9 [ x PERS: 3 NUM: sg IND: + ] ]
[ pronoun_q LBL: h4 ARG0: x3 [ x PERS: 2 PT: zero ] RSTR: h5 BODY: h6 ]
[ pron LBL: h7 ARG0: x3 [ x PERS: 2 PT: zero ] ]
[ _to_p_dir LBL: h1 ARG0: e8 [ e SF: prop TENSE: untensed MOOD: indicative PROG: - PERF: - ] ARG1: e2 ARG2: x9 ]
[ _go_v_1 LBL: h1 ARG0: e2 [ e SF: comm TENSE: pres MOOD: indicative PROG: - PERF: - ] ARG1: x3 ]
>
HCONS: < h0 qeq h1 h5 qeq h7 h11 qeq h13 > ]
```

Event variables conceptually hold a single "event" that accumulates information over the course of evaluating the predications. Multiple predications may "enrich" it with information before it's actually used by, for example, a verb. Contrast this with an instance (`x`) variable which only holds a particular individual at a given point it time. Said another way: an instance variable is like a `string` and can only hold one value, where an event is like a `dictionary` or a `list` and can hold many and be added to over time.

Note that the DELPH-IN grammars are very liberal in putting event variables on predications and, depending on context, sometimes they aren't used. This is just to prevent the consumer of the MRS from having to deal with the same predication both with and without an event variable.

The predication that introduces an event variable will often (but not always) be the predication that consumes or "does something" with the "fully enriched" event. Predications that have it in other arguments will often (but not always) be simply adding information to the event.

#### Other Variables Types: I, U, P
Recall that the variable types in DELPH-IN form a hierarchy. So far we've discussed the bottommost "leaves", which are most commonly seen:

```
    u
   / \
  i   p
 / \ / \
e   x   h
```

The other three types of variables represent a type that is "in-between" or "underspecified" between the other "concrete" types (`e`, `x`, `h`).  In general, these appear when the ERG can't decide the type of something since it falls somewhere between the types (i.e. is "underspecified").  From the ERG documentation:

> "i (for individual) is a generalization over eventualities and instances; p (the half-way mark in the alphabet between h and x) is a generalization over labels and instances; and u (for unspecific or maybe unbound) generalizes over all of the above. Note that Copestake et al. (2001) use individual for what is called instance here."

In practice, they appear in two pretty specific scenarios:

**Unquantified `x` variables**: Some predications in the ERG have an argument that is conceptually an individual (`x`) type, but does not require quantification. Since the rules require that all `x` variables are scoped by a quantifier, the most appropriate of the three "in-between" types will be used instead as a "work-around". This is usually `i` since these are most often of type `x`, and `i` is the most specific of the options that includes `x`. As with all non-`x` variables, this will be "existentially quantified" (globally defined) -- that is the whole point of using them here.

**Dropped arguments**: Sometimes the predication that would introduce a variable is missing. For example, take "I left" vs. "I left Oregon". In the latter, "Oregon" becomes a predication that introduces a variable that "left" uses, but in the former, this predication doesn't exist, so the variable is not introduced. In this case, the missing (or "dropped") variable uses an `i`, `p` or `u` type in place of the original type. Variables typed like this should be treated like the act of passing `None` in Python or `Null` in SQL to a function. The easiest way to detect when one of these three variable types means "dropped or ignored argument" is by checking if any other predication is also using it (as in the previous case). If not, it is probably dropped/ignored.
- `i` means dropped `e` or `x`
- `u` means dropped `e`, `x`, or `h`
- `p` means dropped `x` or `h`

#### Variable Properties
Variables in an MRS have *properties*, which are like single argument predications for the variables. They define many different properties of a variable that aren't included anywhere else. They are defined after the variable in the MRS, surrounded by `[]`. You can see several examples in the MRS for "he will go":

```
[ pronoun_q LBL: h5 ARG0: x3 [ x PERS: 3 NUM: sg GEND: m IND: + PT: std ] RSTR: h6 BODY: h7 ]
[ pron LBL: h4 ARG0: x3 [ x PERS: 3 NUM: sg GEND: m IND: + PT: std ] ]
[ _go_v_1 LBL: h1 ARG0: e2 [ e SF: prop TENSE: fut MOOD: indicative PROG: - PERF: - ] ARG1: x3 ]
```
The properties provided depend on the type of variable:

Instance (`x`) variables can have these properties:
- Number (`NUM`): `sg` (singular) or `pl` (plural)
- Person (`PERS`): `1`,`2`, or `3` for first-person (speaker) I/we, second-person (hearer) you, and third-person otherwise
- Individuated (`IND`): `+` or `-` (meaning true or false). Distinguishes individuated entities introduced by count nouns such as cat or cats from non-individuated referents for mass nouns such as rice
- Gender (`GEN`): `m` for male, `f` for female, `n` otherwise
- Pronoun Type(`PT`): ?

Event (`e`) variables can have these properties:
- Tense (`TENSE`): `past` for past, `pres` for present, `fut` for future, or `untensed`
- Viewpoint aspect (or 'grammatical aspect') describes the situation from a particular viewpoint, dividing it into endpoints and stages (Smith 1991, 1997)
  - `PERF` (for perfect): `+` or `-` (meaning true or false)
  - `PROG` (for progressive): `+` or `-` (meaning true or false)
- Sentence Force (`SF`): `comm` for command, `ques` for question, `prop` for proposition. Indicates the type of sentence.
- Mood (`MOOD`): Roughly describes the opinions or attitudes of the speaker, with most common values being: `subjunctive` and `indicative`

## Quantifier Predications
Quantifiers in DELPH-IN are the primary predications that glue a tree together. They provide two functions: they show where in the tree certain variables can be used (i.e. provide *scope* to the variable) and they often also constrain "how much" of the variable can be used. "The", "a", "some" and "all" are really common examples. 

Quantifier predications in DELPH-IN always have a specific argument signature: 

```
quantifier_q(x,h,h)
```

In addition to (often) doing the job of saying "how much of" their `x` variable there should be to make the MRS true ("lots", "some", "the", etc), they provide scope to the `x` variable. All `x` variables must be scoped by a quantifier, which means that they can only be used in the branches of the tree that are contained in the quantifier's two `h` (scopal) arguments. This rule for well-formedness means that there are many quantifiers that don't do "real" quantification at all, they are in the MRS solely to scope the `x` variable. Some also act like "markers" of some kind (again without doing any quantification).

The MRS for "go north" shows an example of this:
```
[ TOP: h0
INDEX: e2
RELS: < 
[ def_implicit_q LBL: h11 ARG0: x9 [ x PERS: 3 NUM: sg ] RSTR: h12 BODY: h13 ]
[ place_n LBL: h10 ARG0: x9 [ x PERS: 3 NUM: sg ] ]
[ _north_a_1 LBL: h10 ARG0: i14 [ i ] ARG1: x9 ARG2: u15 ]
[ pronoun_q LBL: h4 ARG0: x3 [ x PERS: 2 PT: zero ] RSTR: h5 BODY: h6 ]
[ pron LBL: h7 ARG0: x3 [ x PERS: 2 PT: zero ] ]
[ loc_nonsp LBL: h1 ARG0: e8 [ e SF: prop TENSE: untensed MOOD: indicative PROG: - PERF: - ] ARG1: e2 ARG2: x9 ]
[ _go_v_1 LBL: h1 ARG0: e2 [ e SF: comm TENSE: pres MOOD: indicative PROG: - PERF: - ] ARG1: x3 ]
>
HCONS: < h0 qeq h1 h5 qeq h7 h12 qeq h10 > ]

                                ┌── place_n(x9)
                    ┌────── and(0,1)
                    │             └ _north_a_1(i14,x9,u15)
def_implicit_q(x9,RSTR,BODY)
                         │                 ┌────── pron(x3)
                         └─ pronoun_q(x3,RSTR,BODY)    ┌── loc_nonsp(e8,e2,x9)
                                                └─ and(0,1)
                                                         └ _go_v_1(e2,x3)
```
The variable `x9` represents `north` but nothing in the phrase is "quantifying" direction in any way.  Since the rules for MRS require `x` variables to be quantified (among other reasons), an abstract quantifier called `def_implicit_q` is used to do the scoping of the variable.

Note that, unlike non-quantifier predications, the first (`ARG0`) argument of a quantifier *does not* "introduce" an "intrinsic variable" (as described in the variables section), quantifiers just scope and optionally quantify their `ARG0`.

## Constraints
The `HCONS` section of the MRS is used when building a well-formed tree. It puts *CONS*traints on where the *H*andles for predications can be validly placed and still be a legal interpretation of the phrase. The only constraints used in "modern" MRS are `qeq` constraints so that's all you'll see in this section.  

A `qeq` constraint always relates an `h` argument of one predication, called a "hole", to the handle (`LBL`) of another predication. It states that the handle must be a direct or eventual child of the hole in the tree and, if not direct, the only things between the hole and the handle can be quantifiers.  Said a different way: 

> A qeq constraint of "X qeq Y" says that the direct path from X to Y must only contain quantifiers (except for the final predication Y).

As we work through [fully resolving the MRS into a tree](https://blog.inductorsoftware.com/Perplexity/home/mrscon/devhowto0020WellFormedTree), we'll see more description and examples of how the `HCONS` section is used.

## Index
One final part of the MRS needs to be described: `INDEX`:
```
TOP: h0
INDEX: e2
RELS: < 
[ _the_q__xhh LBL: h10 ARG0: x9 [ x PERS: 3 NUM: sg IND: + ] RSTR: h11 BODY: h12 ]
[ _cave_n_1 LBL: h13 ARG0: x9 [ x PERS: 3 NUM: sg IND: + ] ]
[ pronoun_q__xhh LBL: h4 ARG0: x3 [ x PERS: 2 PT: zero ] RSTR: h5 BODY: h6 ]
[ pron__x LBL: h7 ARG0: x3 [ x PERS: 2 PT: zero ] ]
[ _to_p_dir__eex LBL: h1 ARG0: e8 [ e SF: prop TENSE: untensed MOOD: indicative PROG: - PERF: - ] ARG1: e2 ARG2: x9 ]
[ _go_v_1__ex LBL: h1 ARG0: e2 [ e SF: comm TENSE: pres MOOD: indicative PROG: - PERF: - ] ARG1: x3 ]
>
HCONS: < h0 qeq h1 h5 qeq h7 h11 qeq h13 > 
```
The MRS will represent the syntactic head of the phrase with one or more predications. Index will point to the one that could (in principle) be used to further compose the phrase with other phrases [See HPSG Backgrounder]. In general, the index predication can be used to determine what the phrase is “about”, or what the phrase is “built around”.

The `INDEX` part of the MRS indicates the variable introduced by the predication (or predications if there is a conjunction) that is the "main point of the phrase". It is "the thing being done", which is usually the main verb.  In the example above `INDEX: e2` is referring to the variable introduced by `_go_v_1__ex`.  This indicates that the verb `go` is the "main point of the phrase". This is called the "syntactic head" in linguistics.

Note that the `INDEX` does not always point at a verb. In phrases that just state that something "is" something else, such is: "the flower is blue", "is" is not included. "blue" acts like the verb and is the `INDEX`:

```
[ TOP: h0
INDEX: e2
RELS: < 
[ _the_q LBL: h4 ARG0: x3 [ x PERS: 3 NUM: sg IND: + ] RSTR: h5 BODY: h6 ]
[ _flower_n_1 LBL: h7 ARG0: x3 [ x PERS: 3 NUM: sg IND: + ] ]
[ _blue_a_1 LBL: h1 ARG0: e2 [ e SF: prop TENSE: pres MOOD: indicative PROG: - PERF: - ] ARG1: x3 ]
>
HCONS: < h0 qeq h1 h5 qeq h7 > ]


            ┌────── _flower_n_1(x3)
_the_q(x3,RSTR,BODY)
                 └─ _blue_a_1(e2,x3)
```

More information on `INDEX` is described in the section on dealing with different types of phrases.

The [next topic](https://blog.inductorsoftware.com/Perplexity/home/mrscon/devhowto0020WellFormedTree) walks through the rules of creating "well-formed MRS trees", and is the last big chunk of conceptual background needed before we start building the system.

> Comprehensive source for the completed tutorial is available [here](https://github.com/EricZinda/Perplexity).

Last update: 2024-10-23 by Eric Zinda [[edit](https://github.com/EricZinda/Perplexity/edit/main/docs/mrscon/devhowto0010MRS.md)]{% endraw %}