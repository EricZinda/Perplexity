## Handling Unknown Words and Synonyms
Now that we have a nice interactive system, it is easy to encounter words that aren't implemented. The default behavior isn't good if the user types one in:

~~~
? there is a file
Traceback (most recent call last):
  File "/Users/ericzinda/Enlistments/Perplexity/file_system_example/examples.py", line 346, in <module>
    Example16()
  File "/Users/ericzinda/Enlistments/Perplexity/file_system_example/examples.py", line 305, in Example16
    user_interface.interact_once(respond_to_mrs_tree)
    
    ...
    
  File "/Users/ericzinda/Enlistments/Perplexity/perplexity/execution.py", line 87, in _call_predication
    module = sys.modules[module_function[0]]
TypeError: 'NoneType' object is not subscriptable

Process finished with exit code 1
~~~
Instead of crashing, we should be reporting a nice error. Adding a small amount of code to _`call_predication()` to report an error when there is not an implementation of a predication is one approach:

~~~
    def _call_predication(self, state, predication):
        
        ...
        
        # Look up the actual Python module and
        # function name given a string like "folder_n_of".
        # "vocabulary.Predication" returns a two-item list,
        # where item[0] is the module and item[1] is the function
        module_function = self.vocabulary.predication(predication_name)
        
        # If there is not an implementation of the predication, report an error
        if module_function is None:
            self.report_error(["termNotUnderstood", predication_name])
            return
~~~

The problem with this approach is that it will only report the first word that wasn't understood since the error stops the execution of the tree. Also, since it is using the normal error reporting system that predications use, the error can be caught and ignored. This is exactly what would happen if we implement that code and then run "there is a bird" through the system, you get:

~~~
? there is a bird
There isn't 'a bird' in the system
~~~

The real error is "I don't know the words 'be' and 'bird'", but our quantifiers have the following logic in them (from the [Quantifier Errors topic](devhowtoQuantifierErrors)) and so the error is ignored:

~~~
def a_q(state, x_variable, h_rstr, h_body):
    
    ...

    if not rstr_found:
        # Ignore whatever error the RSTR produced, this is a better one
        # Report the variable's English representation as it would be in the BODY
        report_error(["doesntExist", ["AtPredication", h_body, x_variable]], force=True)
~~~

A better approach all around is to add an earlier stage to our processing pipeline: Before we bother to [build a well-formed tree](devhowtoWellFormedTree) (because it could take some time), check and see if we understand all the terms. If not, building the tree won't help anyway.  In addition, this gives us a chance to do some swapping out of terms for synonyms if we so choose.

So, first let's build a function that goes through all the predications in an MRS and returns any that are not known by the system:

~~~
    def unknown_words(self, mrs):
        unknown_words = []
        for predication in mrs.predications:
            if self.execution_context.vocabulary.predication(predication.predicate) is None:
                # This predication is not implemented
                unknown_words.append(predication.predicate)

        return unknown_words
~~~

Now we can check if there are unknown words before we do the processing, like this:

~~~
class UserInterface(object):
    
    ...
    
    # response_function gets passed three arguments:
    #   response_function(mrs, solutions, error)
    # It must use them to return a string to say to the user
    def interact_once(self, response_function):
        # input() pauses the program and waits for the user to
        # type input and hit enter, and then returns it
        user_input = str(input("? "))
        best_failure = None

        # Loop through each MRS and each tree that can be
        # generated from it...
        for mrs in self.mrss_from_phrase(user_input):
            unknown_words = self.unknown_words(mrs)
            if len(unknown_words) > 0:
                if best_failure is None:
                    best_failure = response_function(None, [], [0, ["unknownWords", unknown_words]])

                continue

            for tree in self.trees_from_mrs(mrs):
                
                ...
~~~

And, for good measure, we'll add in support for synonyms to the `Predication` decorator and the `Vocabulary` class:

~~~

def Predication(vocabulary, name=None, synonyms=[]):
    ...
    
        vocabulary.add_predication(function_to_decorate.__module__, function_to_decorate.__name__, predication_name, synonyms)

    ...
    
    
class Vocabulary(object):
    def __init__(self):
        self.all = dict()

    def add_predication(self, module, function, delphin_name, synonyms):
        self.all[delphin_name] = [module, function]
        for synonym in synonyms:
            self.all[synonym] = [module, function]
    
    ...
~~~

Now if we run the sample interactively (with logging turned on) and use words that aren't known, we get a decent response:

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
                    
# Running Example16() results in:
? erase a file
Pipeline 2023-01-09 14:10:46,870: 2 parse options for erase a file
Pipeline 2023-01-09 14:10:46,878: Parse 0: <MRS object (pronoun_q pron _erase_v_1 _a_q _file_n_of) at 140409290505904>
Pipeline 2023-01-09 14:10:46,879: Parse 1: <MRS object (_erase_v_1 _a_q _file_n_of) at 140409290505008>
I don't know the words: erase
~~~

Much better! Now we can also easily add `erase` as a synonym of `delete` by looking at the emitted logs to see what the predication name was (`_erase_v_1`) and including it as a `synonym` argument of the `Predication` decorator for `delete_v_1`:

~~~
@Predication(vocabulary, name="_delete_v_1", synonyms=["_erase_v_1"])
def delete_v_1(state, e_introduced, x_actor, x_what):
    ...
    
# Running Example16() results in:
? erase a file
Done!  
~~~

Great! But what if the user types something like "a file is deleted"?
~~~
? a file is deleted
Traceback (most recent call last):
  File "/Users/ericzinda/Enlistments/Perplexity/file_system_example/examples.py", line 348, in <module>
    Example16()
  File "/Users/ericzinda/Enlistments/Perplexity/file_system_example/examples.py", line 307, in Example16
    user_interface.interact_once(respond_to_mrs_tree)
  File "/Users/ericzinda/Enlistments/Perplexity/perplexity/user_interface.py", line 45, in interact_once
    for item in self.execution_context.solve_mrs_tree(self.state, tree_info):
    
    ...
    
~~~

The [next section](devhowtoPredicationArgumentsAndUsage) will explore what is going on here and how we can fix it.

> Comprehensive source for the completed tutorial is available [here](https://github.com/EricZinda/Perplexity).
