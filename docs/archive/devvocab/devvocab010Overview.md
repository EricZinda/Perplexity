# Developer Predication Tutorial Overview
The [Developer How-To section](../devhowto/devhowtoOverview) is a tutorial that introduces developers to the DELPH-IN technologies by building a Python framework called ["Perplexity"](https://github.com/EricZinda/Perplexity) that evaluates DELPH-IN predications written in Python. In this section, we will show how to *use it* by implementing the vocabulary for a file system using the Perplexity framework. When finished, we'll have a working interactive natural language interface that allows users to browse their file system.

This section assumes a working knowledge of [The Minimal Recursion Semantics (MRS) Format](../devhowto/devhowtoMRS) and [Building Scope-Resolved MRS](../devhowto/devhowtoWellFormedTree) as well as a [basic understanding of Python](../devhowto/devhowtoPythonBasics/). Having read through the [Developer Tutorial](../devhowto/devhowtoOverview/) would also be very helpful, but shouldn't be required. We'll link to the relevant sections as we discuss them.
 
Let's start with a review of the Perplexity framework. 

### Predications
First, all the terms used in particular application are written as Python functions that implement ["The Predication Contract"](../devhowto/devhowtoPredicationContract) and are decorated with the [`@Predication()` decorator](../devhowto/devhowtoMRSToPython) like this implementation of the DELPH-IN predication for "file" (`_file_n_of`):

~~~
vocabulary = Vocabulary()

@Predication(vocabulary, names=["_file_n_of"])
def file_n_of(state, x, i):
    x_value = state.get_variable(x)
    if x_value is None:
        iterator = state.all_individuals()
    else:
        iterator = [x_value]

    for item in iterator:
        if isinstance(item, File):
            new_state = state.set_x(x, item)
            yield new_state
        else:
            report_error(["xIsNotY", x, "file"])
~~~

Note that predications are recorded in whatever `Vocabulary` instance is passed to the `@Predication()` decorator. This `Vocabulary` instance will then represent all the terms understood by the application.

### State 
State is represented by an object that can be completely tailored to the application. Predications (like `file_n_of` above) are always passed the state object as their first argument and use whatever methods it implements to do whatever they need to do. Only the predications care what methods the state object implements -- the Perplexity framework doesn't care. 

The `State` object we'll be using is described in [a previous section](../devhowto/devhowtoPythonBasics). The important methods are:

~~~
class State(object):
    def __init__(self, objects):
        ...
    
    # This is how predications will access the current value
    # of MRS variables like "x1" and "e1"
    def get_variable(self, variable_name):
        ...
    
    # This is how predications will set the value
    # of an "x" variable
    def set_x(self, variable_name, item):
~~~

As described in [that section](../devhowto/devhowtoPythonBasics):

> Note that the set_x() method does not actually “set” a value in the State object, it creates a copy of the current State object and sets the value in that. This ensures that variables set for a given State object are never changed (they are immutable).

You can see this in how the `file_n_of()` predication yields the object *returned by* `state.set_x()` and not the `state` object it was passed:

~~~
@Predication(vocabulary, names=["_file_n_of"])
def file_n_of(state, x, i):
    x_value = state.get_variable(x)
    if x_value is None:
        iterator = state.all_individuals()
    else:
        iterator = [x_value]

    for item in iterator:
        if isinstance(item, File):
            new_state = state.set_x(x, item)
            yield new_state
        else:
            report_error(["xIsNotY", x, "file"])
~~~

### Objects
As described in [a previous section](../devhowto/devhowtoPythonBasics), our file system example will be representing objects as simple Python objects derived from `UniqueObject`, like this:

~~~
# Base class that objects derive from so that
# objects have a unique ID that is preserved even
# when they are copied
class UniqueObject(object):
    def __init__(self):
        self.unique_id = uuid.uuid4()


# Derive from UniqueObject and call
# its __init__ method from this __init__
# method so we get the unique ID created
class Folder(UniqueObject):
    def __init__(self, name, size=0):
        super().__init__()
        self.name = name
        self.size = size

    def __repr__(self):
        return f"Folder(name={self.name}, size={self.size})"


class File(UniqueObject):
    def __init__(self, name, size=None):
        super().__init__()
        self.name = name
        self.size = size

    def __repr__(self):
        return f"File(name={self.name}, size={self.size})"
        
...

~~~

Again, the Perplexity framework doesn't care how the objects are represented -- they could be simple JSON files, database objects, whatever. As long as the predications understand what to expect.

### User Interaction
The `UserInterface` class takes user commands like: "What files are in this folder?" and:

1. Parses them into an MRS document (using the [ACE parser](http://sweaglesw.org/linguistics/ace/))
2. Converts them into Python function calls
3. ["Solves"](../devhowto/devhowtoPredicationContract/) them.

All this happens inside the [`UserInterface.interact_once()`](../devhowto/devhowtoWhichParseAndTree/) method which gets passed the `State` to operate against and the `Vocabulary` to use, like this:

~~~
def Example16():
    state = State([Actor(name="Computer", person=2),
                   Folder(name="Desktop"),
                   Folder(name="Documents"),
                   File(name="file1.txt", size=2000000)])

    user_interface = UserInterface(state, vocabulary)

    while True:
        user_interface.interact_once(respond_to_mrs_tree)
        print()
        
# Running Example16() yields:
? a file is large
Yes, that is true.

? which file is large?
File(name=file1.txt, size=2000000)

? which folder is large?
a folder is not large

? delete a folder
Done!
~~~

The responses given to the user are generated by the function passed to `interact_once()`, in this case: `respond_to_mrs_tree()`, described next.

### User Responses
After a user's phrase has been converted into Python and solved, the tree, solutions generated, and ['best error'](../devhowto/devhowtoChoosingWhichFailure/) get passed to whatever function was supplied to `interact_once()` (in this case: `respond_to_mrs_tree()`). It then decides how to respond by looking at [sentence force](../devhowto/devhowtoSentenceForce/), whether there was a solution and, if not, the error returned. In our example, it uses a helper function called [`generate_message(tree_info, error_term)`](../devhowto/devhowtoRobustFailure/) (also shown below) to convert errors into text:

~~~
# Implements the response for a given tree
def respond_to_mrs_tree(tree, solutions, error):
    ...
    
    sentence_force_type = sentence_force_from_tree_info(tree)
    if sentence_force_type == "prop":
        # This was a proposition, so the user only expects
        # a confirmation or denial of what they said.
        # The phrase was "true" if there was at least one answer
        if len(solutions) > 0:
            return "Yes, that is true."
        else:
            message = generate_message(tree, error)
            return message
           
    ...


# Generates all the responses that predications can return when an error
# occurs
#
# error_term is of the form: [index, error] where "error" is another
# list like: ["name", arg1, arg2, ...]. The first item is the error
# constant (i.e. its name). What the args mean depends on the error
def generate_message(tree_info, error_term):
    error_predicate_index = error_term[0]
    error_arguments = error_term[1]
    error_constant = error_arguments[0]

    if error_constant == "xIsNotY":
        arg1 = english_for_delphin_variable(error_predicate_index, error_arguments[1], tree_info)
        arg2 = error_arguments[2]
        return f"{arg1} is not {arg2}"

    elif error_constant == "adjectiveDoesntApply":
        arg1 = error_arguments[1]
        arg2 = english_for_delphin_variable(error_predicate_index, error_arguments[2], tree_info)
        return f"{arg2} is not {arg1}"
        
    ...
~~~

The first thing we need to do is [determine the phrases and vocabulary](devvocabPhrasesAndVocab) we need to implement.

> Comprehensive source for the completed tutorial is available [here](https://github.com/EricZinda/Perplexity).
