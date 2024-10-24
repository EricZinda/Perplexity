## Python Decorators and the Vocabulary Class
This section describes a more arcane part of Python called "decorators" that we use to register predication methods in the `Vocabulary Class`. It is not important to understand how the code works, but it is here for those that are interested.

Python decorators allow us to run code at load time that inspects whatever they decorate and take action. In this case, we will take the name and arguments of the function passed to `@Predication()`, and record it in the `vocabulary` instance we are given. That way, we will have an object that knows all the predications after the file is loaded.

The `vocabulary` class is simple: it has a dictionary that maps predication names to functions:
~~~
class Vocabulary(object):
    def __init__(self):
        self.all = dict()

    def AddPredication(self, module, function, delphin_name):
        self.all[delphin_name] = [module, function]

    def Predication(self, delphin_name):
        return self.all.get(delphin_name, None)
~~~

The `Predication` class is the actual "decorator" class. It uses the fact that Python functions can define other functions within them.
> TODO: Describe in more detail how this decorator works
~~~
def Predication(vocabulary, name=None):
    # Gets called when the function is first created
    # function_to_decorate is the function definition
    def PredicationDecorator(function_to_decorate):
        def WrapperFunction(*args, **kwargs):
            # For now just iterate from the predication,
            # later we'll do more here
            yield from function_to_decorate(*args, **kwargs)

        predication_name = name if name is not None else function_to_decorate.__name__
        vocabulary.AddPredication(function_to_decorate.__module__, function_to_decorate.__name__, predication_name)

        return WrapperFunction

    return PredicationDecorator
~~~

> Comprehensive source for the completed tutorial is available [here](https://github.com/EricZinda/Perplexity/tree/main/samples/hello_world)
