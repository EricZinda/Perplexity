{% raw %}## Hello World

The simplest Perplexity application is:

```
from perplexity.state import State
from perplexity.user_interface import UserInterface
from perplexity.vocabulary import Vocabulary
from perplexity.world_registry import register_world


# The Vocabulary object will eventually be where all of the 
# functions that implement the MRS predications get registered
# Is just an initial object since we have none
vocabulary = Vocabulary()


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


# Worlds need to be registered so the user can switch between them by name
# and so that the engine can search for their autocorrect and other cached files
# in the same directory where the ui() function resides
register_world(world_name="SimplestExample",
               module="hello_world",
               ui_function="ui")


if __name__ == '__main__':
    user_interface = ui()
    while user_interface:
        # The loop might return a different user interface
        # object if the user changes worlds
        user_interface = user_interface.default_loop()
```
The basics are described in comments above, but the basic flow is: 
1. A micro-world gets registered with a name ("SimplestExample") and a pointer to the module and function where the system can create its `UserInterface` object to run it.
2. In `__main__`, this `UserInterface` object is created and run in a loop.  Each iteration of the loop processes one phrase from the user.

The state of the world is encapsulated, in whatever form the developer wants, in the object that is returned by the reset function (`reset()`).

That's it! All of these objects will be described more as we go through the tutorial.

To run this:

1. Create a `hello_world` directory in the Perplexity project
2. Create a `hello_world.py` file in that directory with the code above
3. From within the `hello_world` directory, run: `python ./hello_world.py`

[Note: As always, you will need to have your environment activated as described in the [Installing Perplexity topic](https://blog.inductorsoftware.com/Perplexity/home/pxHowTo/pxHowTo012Install) to successfully run]

You'll get something like this:

```
python ./hello_world.py
? Hello!
I don't know the words: Hi, Hi!

? Where am I?
I don't know the words: I, Where
```

So far, it has no vocabulary so it will just keep saying, "I don't know the words..." to any phrases typed until we implement some. That's what [the remainder of the tutorial](https://blog.inductorsoftware.com/Perplexity/home/pxhowto/pxHowTo020ImplementAPredication) is about.

> Comprehensive source for the completed tutorial is available [here](https://github.com/EricZinda/Perplexity/tree/main/samples/hello_world)

Last update: 2024-10-25 by Eric Zinda [[edit](https://github.com/EricZinda/Perplexity/edit/main/docs/pxHowTo/pxHowTo014HelloWorld.md)]{% endraw %}