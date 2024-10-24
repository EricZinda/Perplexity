## Reporting Failures
So far, we've only dealt with successful examples: examples where the phrase has a solution.  Let's see what happens when we say a phrase that has no solution:

~~~
# "a file is large" in a world with no large files
def Example10():
    # Note neither file is "large" now
    state = State([Folder(name="Desktop"),
                   Folder(name="Documents"),
                   File(name="file1.txt", size=100),
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
                        "e2": {"SF": "prop"}}

    mrs["RELS"] = TreePredication(0, "_a_q", ["x3",
                                       TreePredication(1, "_file_n_of", ["x3", "i1"]),
                                       TreePredication(2, "_large_a_1", ["e2", "x3"])])

    respond_to_mrs(state, mrs)
        
# Outputs:

~~~

Nothing gets printed out because we haven't implemented a way to report errors from the system. Now it is time to dig into failures.

### Failure Codes and Data
To centralize error reporting and make the code easy to maintain, we will separate the notion of the *error code* from the actual text that gets shown to the user. That way, we can report the same error in multiple places but change the wording shown to the user in one place.

The format will be a simple list. The first list item is a string representing the error code, and the rest of the list is whatever information is needed to generate the string later.  For example:

~~~
["notAThing", "dog", "car"]
~~~

... could later be used to generate the string:

~~~
A "dog" is not a "car"
~~~

### Recording Errors
Recall from the conceptual section on [reporting errors](../devcon/devcon0080ErrorsChoosingWhichFailure) that the best error is usually the *deepest* error, the one which was generated at the deepest part of the predication tree when traversing it in a depth-first manner. To track current depth, and allow for reporting errors, we'll build a new class called `ExecutionContext` and create a single global instance of it.  Our MRS solver code will be modified to use it to record the current depth as the tree is traversed, and the predication implementations will record their errors in it. `ExecutionContext` will use the current depth to only remember the "deepest" error.  

Here's the class, along with its global instance and a helper to retrieve it. It doesn't yet include the changes to `call()` needed to record the current predication index, we'll do that next:

~~~
class ExecutionContext(object):
    def __init__(self):
        self._error = None
        self._error_predication_index = -1
        self._predication_index = -1

    def deepest_error(self):
        return self._error
        
    def report_error(self, error):
        if self._error_predication_index < self._predication_index:
            self._error = error
            self._error_predication_index = self._predication_index


# Create a global execution context
execution_context = ExecutionContext()


# Helper to access the global context so code is isolated from
# how we manage it
def context():
    return execution_context
~~~

Now we can modify our main entry point, `respond_to_mrs` to start using this.  It will retrieve the error string if there were no solutions and use it for each sentence type in the failure case. Here we can see the changes for the 'prop' sentence type:

~~~
    ...
    
    error = generate_message(state, context().deepest_error()) if len(solutions) == 0 else None
    
    ...
    
    if force == "prop":
        ...
        if len(solutions) > 0:
            print("Yes, that is true.")
        else:
            print(f"No, that isn't correct:{error}")
            
    etc.
~~~

... and here is the full code:

~~~
def respond_to_mrs(state, mrs):
    # Collect all the solutions to the MRS against the
    # current world state
    solutions = []
    for item in call(vocabulary, state, mrs["RELS"]):
        solutions.append(item)

    error = generate_message(state, context().deepest_error()) if len(solutions) == 0 else None
    force = sentence_force(mrs)
    if force == "prop":
        # This was a proposition, so the user only expects
        # a confirmation or denial of what they said.
        # The phrase was "true" if there was at least one answer
        if len(solutions) > 0:
            print("Yes, that is true.")
        else:
            print(f"No, that isn't correct:{error}")

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
                print(f"No, {error}")
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
                print(f"{error}")

    elif force == "comm":
        # This was a command so, if it works, just say so
        # We'll get better errors and messages in upcoming sections
        if len(solutions) > 0:
            # Collect all the operations that were done
            all_operations = []
            for solution in solutions:
                all_operations += solution.get_operations()

            # Now apply all the operations to the original state object and
            # print it to prove it happened
            final_state = state.apply_operations(all_operations)

            print("Done!")
            print(final_state.objects)
        else:
            print(f"Couldn't do that: {error}")

~~~

Next, we'll need to update our functions that traverse the tree to record the current predication index. We'll do this by moving the `call()` and `call_predication()` functions to be members of the `ExecutionContext` class and update `call()` to set the predication index.  Here is the only change to `call()`:

~~~
class ExecutionContext(object):
    ...

    def call(self, vocabulary, state, term):
        # See if the first thing in the list is actually a list
        # If so, we have a conjunction
        if isinstance(term, list):
            
            ...
            
        else:
            # The first thing in the list was not a list
            # so we assume it is just a TreePredication term.
            # Evaluate it using call_predication
            last_predication_index = self._predication_index
            self._predication_index += 1

            yield from self.call_predication(vocabulary, state, term)

            # Restore it since we are recursing
            self._predication_index = last_predication_index
        
        ...
~~~

... and here is the full code of `ExecutionContext` now:

~~~
class ExecutionContext(object):
    def __init__(self):
        self._error = None
        self._error_predication_index = -1
        self._predication_index = -1

    def deepest_error(self):
        return self._error

    def report_error(self, error):
        if self._error_predication_index < self._predication_index:
            self._error = error
            self._error_predication_index = self._predication_index

    def call(self, vocabulary, state, term):
        # See if the first thing in the list is actually a list
        # If so, we have a conjunction
        if isinstance(term, list):
            # If "term" is an empty list, we have solved all
            # predications in the conjunction, return the final answer.
            # "len()" is a built-in Python function that returns the
            # length of a list
            if len(term) == 0:
                yield state
            else:
                # This is a list of predications, so they should
                # be treated as a conjunction.
                # call each one and pass the state it returns
                # to the next one, recursively
                for nextState in self.call(vocabulary, state, term[0]):
                    # Note the [1:] syntax which means "return a list
                    # of everything but the first item"
                    yield from self.call(vocabulary, nextState, term[1:])

        else:
            # The first thing in the list was not a list
            # so we assume it is just a TreePredication term.
            # Evaluate it using call_predication
            last_predication_index = self._predication_index
            self._predication_index += 1

            yield from self.call_predication(vocabulary, state, term)

            # Restore it since we are recursing
            self._predication_index = last_predication_index

    # Takes a TreePredication object, maps it to a Python function and calls it
    def call_predication(self, vocabulary, state, predication):
        # Look up the actual Python module and
        # function name given a string like "folder_n_of".
        # "vocabulary.Predication" returns a two-item list,
        # where item[0] is the module and item[1] is the function
        module_function = vocabulary.predication(predication)

        if module_function is None:
            raise NotImplementedError(f"Implementation for Predication {predication} not found")

        # sys.modules[] is a built-in Python list that allows you
        # to access actual Python Modules given a string name
        module = sys.modules[module_function[0]]

        # Functions are modeled as properties of modules in Python
        # and getattr() allows you to retrieve a property.
        # So: this is how we get the "function pointer" to the
        # predication function we wrote in Python
        function = getattr(module, module_function[1])

        # [list] + [list] will return a new, combined list
        # in Python. This is how we add the state object
        # onto the front of the argument list
        predication_args = predication.args
        function_args = [state] + predication_args

        # You call a function "pointer" and pass it arguments
        # that are a list by using "function(*function_args)"
        # So: this is actually calling our function (which
        # returns an iterator and thus we can iterate over it)
        for next_state in function(*function_args):
            yield next_state
~~~

The system will now remember which is the right ("deepest") error to report. The [next section](pxint0110ErrorsReportingAFailure) will describe what the error should say. This is not as obvious as it might seem. 

> Comprehensive source for the completed tutorial is available [here](https://github.com/EricZinda/Perplexity/tree/main/samples/hello_world)