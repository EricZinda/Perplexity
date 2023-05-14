### Reporting the Right Failure
Before we go any further, we need to step back and work through how to deal with and report on failures in the system. The way things are currently built:
- If the user says, "There is a large file" with no large files (or no files at all) in a backtracking system, they will get the response: "No, that isn't correct"
- If the user says "I delete a file" or "Bill deletes a file" they will get the response: "Couldn't do that"

We can do better, but we'll need to work through a few challenges first.

The first challenge is to figure out *which* of the failures to return. Usually there is more than one. To see why, recall that we are solving MRS by effectively pushing all combinations of items in the world "through" the MRS until we find the ones that make it true. 

For "A file is large", the MRS and a resolved tree are:

~~~
[ TOP: h0
INDEX: e2
RELS: < 
[ _a_q LBL: h4 ARG0: x3 [ x PERS: 3 NUM: sg IND: + ] RSTR: h5 BODY: h6 ]
[ _file_n_of LBL: h7 ARG0: x3 [ x PERS: 3 NUM: sg IND: + ] ARG1: i8 ]
[ _large_a_1 LBL: h1 ARG0: e2 [ e SF: prop TENSE: pres MOOD: indicative PROG: - PERF: - ] ARG1: x3 ]
>
HCONS: < h0 qeq h1 h5 qeq h7 > ]

          ┌────── _file_n_of(x3,i8)
_a_q(x3,RSTR,BODY)    
               └─ _large_a_1(e2,x3)
~~~

A described in [the predication contract](devhowtoPredicationContract), our idealized approach to solving it is:
1. `_a_q` iteratively sets `x3` to each object in the world and calls `_file_n_of` with that value
2. If `_file_n_of` succeeds, `_a_q` then calls `_large_a_1` with the values returned
3. If `large_a_1` succeeds, then `a_q` succeeds and stops iterating. 

(Also as described in [the predication contract](devhowtoPredicationContract), in reality, we optimize step #1 to have `_a_q` call `file_n_of` with free variables instead of iterating through every object. This allows `file_n_of` to more efficiently return the files in the system without testing every object. Conceptually, though, it is the same.)

So, let's take a world that has the following items in it, run it through the MRS for "A file is large" and see where things fail:

~~~
a folder
a small file
a large file
a dog
~~~

`a folder`:
1. `_a_q` sets `x3` to `a folder` and calls `_file_n_of` with that value
2. `_file_n_of` fails

`a small file`:
1. `_a_q` sets `x3` to `a small file` and calls `_file_n_of` with that value
2. `_file_n_of` succeeds, `_a_q` then calls `_large_a_1` with the values returned
3. `large_a_1` fails. 

`a large file`:
1. `_a_q` sets `x3` to `a large file` and calls `_file_n_of` with that value
2. `_file_n_of` succeeds, `_a_q` then calls `_large_a_1` with the values returned
3. `large_a_1` succeeds, therefore `a_q` succeeds and stops iterating. 


So, when solving the MRS with this world definition, we hit (in this order):
- a `_file_n_of` failure
- a `large_a_1` failure
- a solution (i.e. no failure)

Even though the system hit two failures in solving the MRS, the user that said "a file is large" wouldn't expect *any* failures to be reported. They would expect something like "Correct!" to be said.

Another example: What if the user said, "A file is *very* large"? In solving the MRS with the same world you'd get (in this order):  
- a `_file_n_of` failure
- a `large_a_1` failure (since none are "*very* large")
- a `large_a_1` failure (since none are "*very* large")
- a `_file_n_of` failure

There were 4 failures encountered when solving the MRS for this case. The user would ideally like the error to be something like, "No, there isn't a very large file", which presumably corresponds to the middle two. Which heuristic helps us choose those?

> One heuristic that works well in practice is this: If there is a solution for an MRS, don't report any errors. If there is no solution for an MRS, report the error from the "deepest/farthest" failure possible.

The intuition for why this works is this:

If there *was* a solution, it means that there was a way to make the phrase work logically in the world. Presumably, it will make sense to the user too, even if it isn't what they meant (though likely it is), so no failure should be reported. 

If there *wasn't* a solution, the user will want to know why not. The "real" reason is "because the MRS did not have a solution", but that is unsatisfying and no human would respond with that. A human would respond with where they got blocked attempting to do what the user asked. Furthermore, even if the human tried, or thought about, 10 different approaches to performing the request, they usually won't describe the 10 ways they tried that didn't work out. They'll likely list the failure that is "the closest they got to succeeding".  For example:

    (In a world where there are 10 things on the counter, 
    including milk, and Bob is holding things he can't put down)
    
    Alice: "Could you give me the milk?"
    Bob: (good answer) "My hands are full"
    Bob: (bad answer) "I thought about handing you ketchup, 
                        but then realized it wasn't milk"

The second answer is bad for many reasons, but here we'll focus on the fact that Alice probably wanted the answer "closest to the solution" as a starting point. She could always ask for more detail or alternative solutions if she really wanted them.

Let's look into Bob's head to see how the answers were generated: Bob tried to solve the request by looking at each thing on the counter until he found the milk (that was 9 different "failures" until one succeeded). Then, he tried to "give it to Alice" which failed because his hands were unavailable. The last failure happened "closest to the solution" and generated the best answer. The other 9 failures were earlier in the process and generated less optimal answers. The failures that get the farthest in the tree are usually closest to a solution and thus will usually "make the most sense" to report.

Here's a more explicit algorithm:
- Track the "depth" of each predication in the tree, where "depth" means "call order"
- Every time a predication fails, if it is the "deepest" failure so far, remember that error
- If the MRS has no solutions, report the remembered error to the user

So, we will need to remember the "current deepest" error as we go. To organize the methods and variables dealing with executing predications and tracking errors, we'll move our existing `Call()`, `CallPredication()` and `RespondToMRS()` functions into a class called `ExecutionContext`. Then, we can track our "current deepest" error there, along with a variable that tracks how deep the currently executing predication is.

The following methods aren't changed at all from what we wrote in previous sections except for `Call()`.  It now assigns an "index" to each predication as they are executed so we know how deep we are. There is also now a global `ExecutionContext` that we'll use for calling predications, along with a couple of methods that make it easy to call:
~~~
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
~~~

At this point, we've just restructured things into an `ExecutionContext` class and started giving an "index" to every predication, but we're not using it. 

Next, we can create a `ReportError()` method that will do the work of recording the "deepest" error, along with a helper function to make it easy to call.

~~~
class ExecutionContext(object):
    
    ...
    
    def ReportError(self, error):
        if self._error_predication_index < self._predication_index:
            self._error = error
            self._error_predication_index = self._predication_index


def ReportError(error):
    DelphinContext().ReportError(error)
~~~

The system will now remember which is the right ("deepest") error to report. The [next section](devhowtoReportingAFailure) will describe what they should say. This is not as obvious as it might seem. 

> Comprehensive source for the completed tutorial is available [here](https://github.com/EricZinda/Perplexity).