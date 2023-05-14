## Python Primer and the State object
The [predication contract](devhowtoPredicationContract) can be implemented in any programming language, but we'll be using Python. This section should give enough background so that even readers not familiar with Python can read the code and understand the examples. Even if you know Python, skim through this section since we will be implementing a key class (`State`) used elsewhere in the documentation.

The Python language has functions, classes, methods, variables, operators, statements, and other elements shared by many imperative programming languages such as C++, Java, Javascript, Go, etc. How these work will be described as we go along and should be relatively straightforward to understand if you are proficient in an existing imperative programming language. 

Python also has a notion of "iterators" which needs a bit more attention. Iterators are objects that can be "iterated" or "listed" or "looped through". These can be lists represented in square brackets like `[item1, item2]`. They can also be special functions called "generators" which act like a list but allow code to dynamically generate the items that are returned.    

You iterate over an iterator of any type using the `for ... in ...` construct like this:

~~~
# '#" in Python starts a line with a comment
for item in iterator:

    # Indenting in Python indicates the code that
    # "belongs" to the thing above. Everything indented
    # here will get looped over

    # Now "item" has the first value from iterator
    # and we can print it
    print(item)
~~~

If you want to write code to *dynamically* build an iterator (called a "generator"), you simply write a fuction that calls `yield` to return each item. `yield` returns the value and then continues on the next line when the next value is asked for. If the function exits without a yield, the iteration stops (this is what we've been calling "fail" in the predication contract):

~~~
# "def" defines a function in Python
# Everything indented below it is in the function
def MyIterator1():
    yield 1
    yield 2
    yield 3

# Here's another function that does
# the same thing differently
def MyIterator2():
    # A list in Python is surrounded by []
    my_list = [1, 2, 3]
    for index in my_list:
        yield index


def OutputResults():
    for item in MyIterator1():
        print(item)
    for item in MyIterator2():
        print(item)

# Calling OutputResults() prints:
# 1
# 2
# 3
# 1
# 2
# 3
~~~

Given the [predication contract](devhowtoPredicationContract), we'll be doing lots of iteration and this syntactic sugar from Python makes it easier. 

Let's work through how to implement a class in Python by creating the class that will hold the state of the world: `State`. The current state of all MRS variables *and* the state of everything in the world will be accessed through this class. Because we want the state to be changed by predications, we will include an instance of it as the first argument when calling them. 

The implementation of the `State` object can be very simple for now:

~~~
# "class" declares an object-oriented class in Python
# The parenthesis after the "State" class name surround
# the object the class derives from (object)
class State(object):

    # All class methods are indented under the
    # class and take "self" as their first argument.
    # "self" represents the class instance.

    # "__init__" is a special method name that
    # indicates the constructor, which is called to create
    # a new instance of the class. Arguments beyond "self"
    # get passed to the function when the instance is created
    def __init__(self, objects):
        # Class member variables are created by
        # simply assigning to them
        self.variables = dict()  # an empty dictionary

        # "objects" are passed to us as an argument
        # by whoever creates an instance of the class
        self.objects = objects


    # A standard "class method" is just a function definition,
    # indented properly, with "self" as the first argument

    # This is how predications will access the current value
    # of MRS variables like "x1" and "e1"
    def GetVariable(self, variable_name):
        # "get()" is one way to access a value in a dictionary.
        # The second argument, "None", is what to return if the
        # key doesn't exist.  "None" is a built-in value in Python
        # like "null"
        return self.variables.get(variable_name, None)

    # This is how predications will set the value
    # of an "x" variable
    def SetX(self, variable_name, item):
        # Make a *copy* of the entire object using the built-in Python
        # class called "copy", we pass it "self" so it copies this 
        # instance of the object
        new_state = copy.deepcopy(self)

        # Now we have a new "State" object with the same
        # world state that we can modify.
        
        # Dictionaries hold name/value pairs.
        # This is how you assign values to keys in dictionaries
        new_state.variables[variable_name] = item

        # "return" returns to the caller the new state with
        # that one variable set to a new value
        return new_state

    # This is an iterator (described above) that returns
    # all the objects in the world
    def AllIndividuals(self):
        for item in self.objects:
            yield item
~~~
Note that the `SetX()` method does not actually "set" a value in the `State` object, it creates a copy of the current `State` object and sets the value in *that*.  This ensures that variables set for a given `State` object are never changed (they are *immutable*). Immutability allows our solver to reuse the same state object multiple times when calling a predication in order to get fresh values bound to the variables. And this, in turn, is important to allow backtracking through possible solutions to the MRS. The fact that the *entire* state object (not just the variables) gets copied will be important when we get to verbs that change the world (e.g. deleting a file). 

> Note: There are much more efficient ways to isolate the data than copying the entire world, but we're doing a copy to keep the code simple. For example, database engines like MySQL have transactions to isolate different parts of code from changes until they should be seen. We could improve our simple implementation by keeping a difference list and not copying the entire state for every copy, but for now we'll keep it simple.

Objects in the world can just be Python objects, although there are many other ways to represent them (the [predication contract](devhowtoPredicationContract) doesn't care). 

Because we will be copying the `State` object when changes are made, we will need some way to identify that, for example, the `foo` folder in one `State` object is the same `foo` folder in another `State` object. To do this, we'll give each object a unique ID by creating a base class called `UniqueObject`. It will create a member variable called `unique_id` with a UUID (a globally unique number) in it. Then, we'll derive all the objects in the system from it. That way, objects will always have a unique ID that follows them even if they are copied. 

Here's how we'll create classes for each "type of thing" in our file system world:
~~~
class UniqueObject(object):
    def __init__(self):
        self.unique_id = uuid.uuid4()


# Derive from UniqueObject and call
# its __init__ method from this __init__
# method so we get the unique ID created
class Folder(UniqueObject):
    def __init__(self, name):
        super().__init__()
        self.name = name
        

class File(UniqueObject):
    def __init__(self, name, size=None):
        super().__init__()
        self.name = name
        self.size = size
~~~

Creating a `State` object with the list of the objects from the example looks like this:

~~~
state = State([Folder(name="Desktop"), 
               Folder(name="Documents"), 
               File(name="file1.txt"), 
               File(name="file2.txt")])
~~~

Note that an instance of the `State` object is created by calling it like a function. This really calls the `__init__` function of `State` and passes the supplied argument (a list) to `__init__`. Each object in the list is created just like `State` was: by calling it as a function. Note that arguments can be named like `name="Documents"` to clarify what is going on.

Now you've seen some of the basic Python you'll see throughout the tutorial and we've defined the core `State` class we'll use in our predications.  Next, we'll [implement a predication](devhowtoImplementPredication).

> Comprehensive source for the completed tutorial is available [here](https://github.com/EricZinda/Perplexity).
