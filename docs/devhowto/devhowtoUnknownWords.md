## Handling Unknown Words
Now that we have a nice interactive system it is easy to encounter words that aren't implemented and the default behavior isn't good if the user types one in:

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

A better approach all around is to add an earlier stage to our processing pipeline: Before we bother to build a well-formed tree (because it could take some time), check and see if we understand all the terms. If not, building the tree won't help anyway.  In addition, this gives us a chance to do some swapping out of terms for synonyms if we so choose.


Sometimes terms are the same with different arguments

> Comprehensive source for the completed tutorial is available [here](https://github.com/EricZinda/Perplexity).
