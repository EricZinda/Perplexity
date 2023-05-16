## The Perplexity State object
We are getting to the point where the examples need to get richer and the approach we've used so far of just hard-coding the state of the world or using the base `State` object is not going to be good enough for future examples. We need to step back and think about how to model the file system state in a more robust way.

## 

The default `State` object only has a very small amount of code for manipulating *application* state, the rest of its implementation manipulates MRS variables. We used that code in the [Action Verbs topic][pxHowTo070ActionVerbs) Here it is again:

~~~
~~~
class State(object):
    def __init__(self, objects):

        ...

        self.objects = objects

    ...
    
    def all_individuals(self):
        for item in self.objects:
            yield item

    ...
~~~
