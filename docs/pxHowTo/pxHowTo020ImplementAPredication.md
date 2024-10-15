## Implementing a Predication
Recall from the conceptual topic on [backtracking](../devcon/devcon0010MRSSolver) that Perplexity interprets a phrase by:
1. Converting the phrase to an [MRS document](../mrscon/devhowto0010MRS)
2. Creating a [well-formed tree](../mrscon/devhowto0020WellFormedTree) from the MRS document
3. Using backtracking to walk the tree and find values for the variables that make the MRS `true`

Using that approach, the phrase "A file is large." creates this MRS and tree (among others):

~~~
[ "a file is large"
  TOP: h0
  INDEX: e2 [ e SF: prop TENSE: pres MOOD: indicative PROG: - PERF: - ]
  RELS: < [ _a_q<0:1> LBL: h4 ARG0: x3 [ x PERS: 3 NUM: sg IND: + ] RSTR: h5 BODY: h6 ]
          [ _file_n_of<2:6> LBL: h7 ARG0: x3 ARG1: i8 ]
          [ _large_a_1<10:15> LBL: h1 ARG0: e2 ARG1: x3 ] >
  HCONS: < h0 qeq h1 h5 qeq h7 > ]


          ┌────── _file_n_of(x3,i8)
_a_q(x3,RSTR,BODY)
               └─ _large_a_1(e2,x3)
~~~

As described in the [backtracking section](../devcon/devcon0010MRSSolver), the backtracking solver maps each predication in the tree to a Python function and does a depth-first traversal of the tree. A `State` object is used to track the current value of all MRS variables (such as `x3`) as the solver goes through this process. At a given point in the traversal, the `State` object always has the current value of all MRS variables *and* any other current state the application needs to do its own work. Each program that uses Perplexity derives an object from `State` to allow predications to interact with the application.

The rest of this section describes how to write these predication functions and how to interact with the `State` object.


### Predication Function Arguments
Perplexity comes preinstalled and configured to use the DELPH-IN English grammar, which is called the ["English Resource Grammar"](https://https://delph-in.github.io/docs/erg/ErgTop/) or "ERG".  You can see from the MRS document in the above example that the ERG predication generated for "file" is:
~~~
_file_n_of(x3,i8)
~~~

Perplexity uses the `Vocabulary` object to map this to a Python function that can be called. All predication Python functions have the same two initial arguments: `context` and `state`, followed by arguments that represent the predication arguments, `x3` and `i8` in this case.  So, the Python implementation of `_file_n_of` looks like this:

~~~
def file_n_of(context, state, x_binding, i_binding):
   ...
~~~

`context` represents the current point in the tree traversal and can be called to report errors or manually traverse the tree farther.  We'll see that used later. Think of it as holding useful helper functions you might need.

`state` is the `State` object described above that represents the state of the world when the predication is called. It holds, among other things, the current value of all the MRS variables at this point in the solver backtracking process.  Because of backtracking, the same predication can be called many times with different states as the solver attempts to find a solution to the MRS. 

`x_binding` and `i_binding` hold all the information about the MRS variables that `_file_n_of` uses. These are `VariableBinding` objects and have properties like `x_binding.variable.name` that will return the MRS variable name (`x3` or `i8` in this example), as well as their current value (`x_binding.value`) from the `state` object. 


### Predication Success
Recall from the section on [backtracking](../devcon/devcon0010MRSSolver) that the job of a predication is to be `true` when its arguments "are set to values that are (or mean) what the predication means".  So, `file_n_of` should be `true` if `x_binding` and `i_binding` have values that mean "file" in the world it is implementing.

Predication functions must be [Python generator functions](../pxint/pxint0020PythonBasics) so they can return multiple values iteratively by calling the Python `yield` operator (we'll see this used next). `true` is indicated by `yield`ing the `state` object, as is, to indicate that this predication is `true` for the current state of the arguments. `false` is indicated by calling Python `return` directly -- i.e. returning without yielding anything.

Here's a simple example: Let's say we are building an interface to a program that has one file in it, called `file1.txt`. We could implement `file_n_of` like this:

~~~
def file_n_of(context, state, x_binding, i_binding):
    if x_binding.value is not None and len(x_binding.value) == 1 and x_binding.value[0] == "file1.txt":
        yield state
~~~

Note that `i_binding` is ignored since `i` variables usually indicate an ignored (or 'dropped') argument as described in the section on [MRS](../mrscon/devhowto0010MRS#other-variables-types-i-u-p).

The code illustrates that bindings have a `binding.value` property that returns the current variable's value, which is always a list for reasons described in the [Together conceptual topic](../devcon/devcon0020MRSSolverSets) . So, this function retrieves the first item in the list and checks to see if it is the one file we have in our world. That is the only time this will bet `true` since that is all we have. If so, it `yields` the state object to indicate that this predication is `true` for the current state of its variables. The `state` object is just yielded, as is, since we are just checking if the values passed in are a "file" and not changing anything. 

Predications will often be called with all of their variables bound like this. But, recall that sometimes the engine will instead be looking for the function to provide a list of *all* `file_n` objects as opposed to checking if a particular object is a file. It indicates this by leaving one or more variables "unbound", which is when: `binding.value is None`.  This indicates to the function that it should `yield` all the things in the world that are a `file`, like this:

~~~
def file_n_of(context, state, x_binding, i_binding):
    if x_binding.value is None:
        yield state.set_x(x_binding.variable.name, ("file1.txt", ))
    elif len(x_binding.value) == 1 and x_binding.value[0] == "file1.txt":
        yield state
~~~

[Note that sets are represented as a Python tuple, and Python tuples require single element tuples to have a trailing `,`, so returning a single item tuple is done like this: `("file1.txt, )`]

`x_binding.value` being `None` means that the MRS variable `x3` is unbound (not set to anything). When a variable is unbound, the predication needs to `yield` all the the variable assignments that *could* make it true -- which in this case is just one: "file1.txt". It does this by setting the variable in the state object and yielding it.

Note that the `state` object is *immutable*, meaning that it cannot be changed directly.  Instead, when methods like `state.set_x()` are called, the method returns a *copy* of the object with only the change the method accomplished. That's why the function yields like this: `yield state.set_x(...)` -- it needs to yield the *copy* with changes in it.

Since our world only has one file in it, we've just hard-coded it here. Obviously the code would be more complicated in a real example.

## Predication Failure
If the predication is called with variable values that make it `false`, it simply returns without yielding. However, it needs to register an error first so we can report something to the user. Reporting errors is done by calling `context.report_error()` and passing it a list. The list names the error and includes any other information needed to build a message for the user, like this:

~~~
def file_n_of(context, state, x_binding, i_binding):
    if x_binding.value is None:
        yield state.set_x(x_binding.variable.name, ("file1.txt",))
    elif len(x_binding.value) == 1 and x_binding.value[0] == "file1.txt":
        yield state
    else:
        report_error(["notAThing", x_binding.value, x_binding.variable.name])
        return False
~~~

Errors are reported as a list and here we've created a custom `notAThing` error to show how it is done. To create a custom error, we pick a string to represent it like `"notAThing"`, and include all the information we'll need later to generate a nice text string for the user. In this case, we provide `x_binding.value` as its first argument, which will be some non-file object like `"folder1"`. The second argument is `x_binding.variable.name`, which is the name of the variable: `x3`. Perplexity has functions that can convert variable names like `x3` to their actual words like "a file". So, passing the variable name is a way of not hard-coding the predication name and allowing the system to generate richer errors. This is described more in the [Converting Variables to English](../pxint/pxint0120ErrorsConceptualFailures) topic, and the mechanics of it is shown next.

## Converting Errors to Messages
If the error returned is a system error, the system will convert it to a message for the user.  If we have custom errors like "notAThing", we need to create a function that converts the custom error information to messages and pass that function as an additional argument to the `UserInterface` object, like this:

~~~
...

def ui():
    ui = UserInterface(world_name="SimplestExample",
                       reset_function=reset,
                       vocabulary=vocabulary,
                       message_function=generate_custom_message)
    return ui


# Generates all the responses that predications can
# return when an error occurs
def generate_custom_message(state, tree_info, error_term):
    # See if the system can handle converting the error
    # to a message first
    system_message = perplexity.messages.generate_message(state, tree_info, error_term)
    if system_message is not None:
        return system_message
    
    else:
        # error_term is of the form: [index, error] where "error" is another
        # list like: ["name", arg1, arg2, ...]. The first item is the error
        # constant (i.e. its name). What the args mean depends on the error
        error_predicate_index = error_term[0]
        error_arguments = error_term[1]
        error_constant = error_arguments[0] if error_arguments is not None else "no error set"
        arg_length = len(error_arguments) if error_arguments is not None else 0
        arg1 = error_arguments[1] if arg_length > 1 else None
        arg2 = error_arguments[2] if arg_length > 2 else None
        arg3 = error_arguments[3] if arg_length > 3 else None
        arg4 = error_arguments[4] if arg_length > 4 else None
    
        if error_constant == "notAThing":
            # s() acts like a Python "f string" but also
            # converts a variable name like 'x3' into the english words
            # that it represented in the MRS. The "*" in {*arg1} tells
            # it to use the value of arg1 directly without converting it 
            # (described below)
            return s("{*arg1} is not {arg2}", tree_info)
    
        else:
            # No custom message, just return the raw error for debugging
            return str(error_term)

~~~

You can use whatever logic you want for converting the error code to a string, this is just an example. Note the use of the `s-string` function `s()`:

~~~
return s("{*arg1} is not {arg2}", tree_info)
~~~

... This is how a variable name like `x3` gets converted to a string like "file". S-strings are a Perplexity feature described in a [separate topic](pxHowTo025SStrings).

The logic Perplexity uses for reporting errors is not obvious, it is worth reading the [section on errors](../devcon/devcon0080ErrorsChoosingWhichFailure) to understand how it works.


## Variables are a Tuple
Recall from the [Together conceptual topic](../devcon/devcon0020MRSSolverSets) that Perplexity represents items operating together as a set (represented as a `tuple` in Python). Because users of the system may ask questions like, "Are the files 20 mb?" (meaning are they 20mb *together*), predications need to be prepared to deal with variables that have a set of more than one item. Let's update the `file_n_of()` function to handle this case.

Assume we have two more files in our example, so that now we have: `file1.txt`, `file2.txt` and `file3.txt`. There is no extra meaning for files "together" vs. files "separately" as far as being files: they are still just "files".  So, we only have to change the logic to loop through the list and make sure they are all files. However, if the `x` variable is unbound, we need to yield *all combinations* of files since any combination of them could make this predication `true`, like this:

~~~
def file_n_of(context, state, x_binding, i_binding):
    if x_binding.value is None:
        # Yield all combinations of files in the system
        yield state.set_x(x_binding.variable.name, ("file1.txt",))
        yield state.set_x(x_binding.variable.name, ("file2.txt",))
        yield state.set_x(x_binding.variable.name, ("file3.txt",))
        yield state.set_x(x_binding.variable.name, ("file1.txt","file2.txt"))
        yield state.set_x(x_binding.variable.name, ("file1.txt","file3.txt"))
        yield state.set_x(x_binding.variable.name, ("file2.txt","file3.txt"))
        yield state.set_x(x_binding.variable.name, ("file1.txt","file2.txt","file3.txt"))
        
    else:
        for item in x_binding.value:
            if item not in ["file1.txt", "file2.txt", "file3.txt"]
                context.report_error(["notAThing", x_binding.value, x_binding.variable.name])
                return False
        yield state
~~~

Manually returning all combinations of a set like this can get complicated and obviously won't work if you don't know the set ahead of time. To make this easier, Perplexity provides a helper function called `combinatorial_predication_1` that does it for you. The `_1` means it is only appropriate for predications with one `x` argument. 

To use this function, you provide it two functions and then let the helper work out all the combinations, like this:

~~~
def file_n_of(context, state, x_binding, i_binding):
    def bound_variable(value):
        if value in ["file1.txt", "file2.txt", "file3.txt"]:
            return True
        else:
            context.report_error(["notAThing", x_binding.value, x_binding.variable.name])
            return False

    def unbound_variable():
        yield "file1.txt"
        yield "file2.txt"
        yield "file3.txt"

    yield from combinatorial_predication_1(context,
                                           state,
                                           x_binding,
                                           bound_variable,
                                           unbound_variable)
~~~

The `bound_variable()` function only needs to implement the logic to check if a single value is a file and report an error if not. The helper does the work of iterating through the set and calling the function to see if each element is a file. 

The `unbound_variable()` function only needs to yield each item that is a file and the system handles yielding all the combinations.

Note that there are several optimizations the system does to avoid having to do the most brute force approach shown above, and the helper handles them all automatically.

## Adding Predications to the Vocabulary
The final step in creating a predication is to register the function as part of the vocabulary and indicate which ERG predication it maps to. This is done using Python ["decorators"](../pxint/pxint03000PythonDecorators) which are really just special functions you can use to label other functions. They are preceded by `@`, like this:
~~~
@Predication(vocabulary, names=["_file_n_of"])
def file_n_of(context, state, x_binding, i_binding):
    ...
~~~

The first argument to `@Predication` is the `Vocabulary` object that the program wants to register the predication in, and `names=[]` provides a list of all the predication names (in case some are synonyms) that should use this function.

Note that Perplexity requires that the function have the right number of arguments for the predications listed in `names=[]`, that the names of the function arguments start with the arguments type (like `x-` or `i-`) and that those types match the types of all predications listed.

With that, the system can now recognize that the function exists and know which ERG predication(s) to map it to.

## Implementing "large"
Let's finish by implementing the predication for "large" (`_large_a_1(e2, x3)` from the MRS above) so we can see the system process "a file is large".

Just like `file_n_of`, `_large_a_1(e2, x3)` has a single `x` variable, so we can copy the approach above to implement it. For now, we can just ignore the event variable `e2`, we'll describe how to handle that in the [Event Predications topic](pxHowTo050EventPredications) later.

We'll implement large by making it be `true` only for "file2.txt" to simulate that being the only "large thing" in the system:
~~~
@Predication(vocabulary, names=["_large_a_1"])
def large_a_1(context, state, e_introduced_binding, x_target_binding):
    def criteria_bound(value):
        if value == "file2.txt":
            return True

        else:
            context.report_error(["adjectiveDoesntApply", "large", x_target_binding.variable.name])
            return False

    def unbound_values():
        # Find all large things
        yield "file2.txt"

    yield from combinatorial_predication_1(context,
                                           state, 
                                           x_target_binding, 
                                           criteria_bound,
                                           unbound_values)
~~~

Once the implementation of `large_a_1` and `file_n_of` are added to `hello_world.py`, we can now run `hello_world.py` and get this:

~~~
python ./hello_world.py
? a file is large
I don't know the words: a
~~~

We dont yet have an implementation for the word "a".  You can see that this is required by typing `/show`. Perplexity will then output the MRS, tree, and other debugging information:

~~~
? a file is large
I don't know the words: a

? /show
User Input: a file is large
1 Parses

***** CHOSEN Parse #0:
Sentence Force: prop
[ "a file is large"
  TOP: h0
  INDEX: e2 [ e SF: prop TENSE: pres MOOD: indicative PROG: - PERF: - ]
  RELS: < [ _a_q<0:1> LBL: h4 ARG0: x3 [ x PERS: 3 NUM: sg IND: + ] RSTR: h5 BODY: h6 ]
          [ _file_n_of<2:6> LBL: h7 ARG0: x3 ARG1: i8 ]
          [ _large_a_1<10:15> LBL: h1 ARG0: e2 ARG1: x3 ] >
  HCONS: < h0 qeq h1 h5 qeq h7 > ]

-- CHOSEN Parse #0, CHOSEN Tree #0: 

          ┌────── _file_n_of(x3,i8)
_a_q(x3,RSTR,BODY)
               └─ _large_a_1(e2,x3)

Text Tree: _a_q(x3,_file_n_of(x3,i8),_large_a_1(e2,x3))

Interpretation: None
Error: (0, ['unknownWords', [('_a_q', ['x', 'h', 'h'], 'prop', False, 'a')]], 0)
Response:
I don't know the words: a
~~~

Luckily, Perplexity provides many built-in predication implementations that you can load by calling the `system_vocabulary()` helper instead of starting with an empty `Vocabulary` object.  This will return a vocabulary object already filled with the built-in perplexity predications:

~~~
# Instead of vocabulary = Vocabulary() call this:
vocabulary = system_vocabulary()
~~~

Running after that change yields this:

~~~
python ./hello_world.py
? a file is large
Yes, that is true.

? which file is large?
('file2.txt',) 
~~~

(Note that Perplexity also provided the predication `which_q` which was needed for the second phrase)

Perplexity has built-in logic for responding to propositions like "a file is large" and for answering questions like "which file is large?" automatically. So, by implementing just `file_n_of` and `large_a_1`, we can already start processing a few phrases.

Below is the full source for the predications we've gone through above. [Next up](pxHowTo030InStylePredications), we'll handle a few more kinds of predications.

## Example Full Source
The full source for the example is now:

~~~
from perplexity.predications import combinatorial_predication_1
from perplexity.state import State
from perplexity.system_vocabulary import system_vocabulary
from perplexity.user_interface import UserInterface
from perplexity.vocabulary import Predication
from perplexity.world_registry import register_world
import perplexity.messages


vocabulary = system_vocabulary()


@Predication(vocabulary, names=["_file_n_of"])
def file_n_of(context, state, x_binding, i_binding):
    def bound_variable(value):
        if value in ["file1.txt", "file2.txt", "file3.txt"]:
            return True
        else:
            context.report_error(["notAThing", x_binding.value, x_binding.variable.name])
            return False

    def unbound_variable():
        yield "file1.txt"
        yield "file2.txt"
        yield "file3.txt"

    yield from combinatorial_predication_1(context,
                                           state,
                                           x_binding,
                                           bound_variable,
                                           unbound_variable)


@Predication(vocabulary, names=["_large_a_1"])
def large_a_1(context, state, e_introduced_binding, x_target_binding):
    def criteria_bound(value):
        if value == "file2.txt":
            return True

        else:
            context.report_error(["adjectiveDoesntApply", "large", x_target_binding.variable.name])
            return False

    def unbound_values():
        # Find all large things
        yield "file2.txt"

    yield from combinatorial_predication_1(context,
                                           state,
                                           x_target_binding,
                                           criteria_bound,
                                           unbound_values)


# Called to initialize or reset the micro-world state
def reset():
    return State([])


# Creates the micro-world interface on startup
# or if the user loads the world later
def ui():
    ui = UserInterface(world_name="SimplestExample",
                       reset_function=reset,
                       vocabulary=vocabulary)
    return ui


# Generates all the responses that predications can
# return when an error occurs
def generate_custom_message(state, tree_info, error_term):
    # See if the system can handle converting the error
    # to a message first
    system_message = perplexity.messages.generate_message(state, tree_info, error_term)
    if system_message is not None:
        return system_message

    else:
        # error_term is of the form: [index, error] where "error" is another
        # list like: ["name", arg1, arg2, ...]. The first item is the error
        # constant (i.e. its name). What the args mean depends on the error
        error_predicate_index = error_term[0]
        error_arguments = error_term[1]
        error_constant = error_arguments[0] if error_arguments is not None else "no error set"
        arg_length = len(error_arguments) if error_arguments is not None else 0
        arg1 = error_arguments[1] if arg_length > 1 else None
        arg2 = error_arguments[2] if arg_length > 2 else None
        arg3 = error_arguments[3] if arg_length > 3 else None
        arg4 = error_arguments[4] if arg_length > 4 else None

        if error_constant == "notAThing":
            # s() acts like a Python "f string" but also
            # converts a variable name like 'x3' into the english words
            # that it represented in the MRS. The "*" in {*arg1} tells
            # it to use the value of arg1 directly without converting it
            # (described below)
            return s("{*arg1} is not {arg2}", tree_info)

        else:
            # No custom message, just return the raw error for debugging
            return str(error_term)


# Worlds need to be registered so the user can switch between them by name
# and so that the engine can search for their autocorrect and other cached files
# in the same directory where the ui() function resides
register_world(world_name="SimplestExample",
               module="hello_world_simplest",
               ui_function="ui")


if __name__ == '__main__':
    user_interface = ui()
    while user_interface:
        # The loop might return a different user interface
        # object if the user changes worlds
        user_interface = user_interface.default_loop()
~~~
