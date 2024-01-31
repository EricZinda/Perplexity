{% raw %}### Reporting the Right Failure
As described in the conceptual topic on [Choosing a Failure](https://blog.inductorsoftware.com/Perplexity/home/devcon/devcon0080ErrorsChoosingWhichFailure), a good heurstic to use for reporting failures to the user is to pick the "deepest" failure encountered. Here we'll walk through how Perplexity does that.

We will need to remember the "current deepest" error as we go. To organize the methods and variables dealing with executing predications and tracking errors, we'll move our existing `Call()`, `CallPredication()` and `RespondToMRS()` functions into a class called `ExecutionContext`. Then, we can track our "current deepest" error there, along with a variable that tracks how deep the currently executing predication is.

The following methods aren't changed at all from what we wrote in previous sections except for `Call()`.  It now assigns an "index" to each predication as they are executed so we know how deep we are. There is also now a global `ExecutionContext` that we'll use for calling predications, along with a couple of methods that make it easy to call:
```
class ExecutionContext(object):
    def __init__(self, vocabulary):
        
        ...
        
        self._error = None
        self._error_predication_index = -1
        self._predication_index = -1

    def Call(self, vocabulary, state, term):
        # Keep track of how deep in the tree this 
        # predication is
        last_predication_index = self._predication_index
        self._predication_index += 1

        ...

        # Restore it since we are recursing
        self._predication_index = last_predication_index

    # Do not use directly.
    # Use Call() instead so that the predication index is set properly
    def _CallPredication(self, vocabulary, state, predication):
        
        ...

    def RespondToMRS(self, state, mrs):
        
        ...
                          
            
# Create a global execution context to use when running the MRS
execution_context = ExecutionContext(vocabulary)


# Helper to access the global context so code is isolated from
# how we manage it
def DelphinContext():
    return execution_context


# Helper used by predications just to make the code easier to read
def Call(*args, **kwargs):
    yield from DelphinContext().Call(*args, **kwargs)
```

At this point, we've just restructured things into an `ExecutionContext` class and started giving an "index" to every predication, but we're not using it. 

Next, we can create a `ReportError()` method that will do the work of recording the "deepest" error, along with a helper function to make it easy to call.

```
class ExecutionContext(object):
    
    ...
    
    def ReportError(self, error):
        if self._error_predication_index < self._predication_index:
            self._error = error
            self._error_predication_index = self._predication_index


def ReportError(error):
    DelphinContext().ReportError(error)
```

The system will now remember which is the right ("deepest") error to report. The next section will describe what they should say. This is not as obvious as it might seem. 

> Comprehensive source for the completed tutorial is available [here](https://github.com/EricZinda/Perplexity).

Last update: 2023-05-14 by EricZinda [[edit](https://github.com/EricZinda/Perplexity/edit/main/docs/pxint/pxint0105ErrorsChoosingWhichFailure.md)]{% endraw %}