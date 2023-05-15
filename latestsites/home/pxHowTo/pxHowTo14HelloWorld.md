{% raw %}## Hello World

The simplest Perplexity application is:

```
from perplexity.state import State
from perplexity.user_interface import UserInterface
from perplexity.vocabulary import Vocabulary

vocabulary = Vocabulary()


def reset():
    return State([])


def hello_world():
    user_interface = UserInterface(reset, vocabulary)

    while True:
        user_interface.interact_once()
        print()


if __name__ == '__main__':
    hello_world()
```

The `UserInterface` class is the main entry point to Perplexity. 

It is created and passed a function (`reset()` in this example) whose job is to return an object derived from the [Perplexity `State` class](https://blog.inductorsoftware.com/Perplexity/home/pxint/pxint0020PythonBasics) that is in the "startup state", whatever that means for the application. 

The second argument is a `Vocabulary` object that contains all the vocabulary required for the application. We don't yet have any vocabulary so an empty `Vocabulary` class is used above.

To allow user interaction, `UserInterface.interact_once()` is called in a loop.  That's it!

To run this:

1. Create a `hello_world` directory in the Perplexity project
2. Create a `hello_world.py` file in that directory with the code above
3. From within the `hello_world` directory, run: `python ./hello_world.py`

[Note: As always, you will need to have your environment activated as described in the [Installation](https://blog.inductorsoftware.com/Perplexity/home/pxHowTo/pxHowTo12Install) section to successfully run]

You'll get something like this:

```
python ./hello_world.py
? hello!
I don't know the words: unknown, greet, discourse

? where am i?
I don't know the words: loc_nonsp, place, which, pron, pronoun
```

So far, it has no vocabulary so it will just keep saying, "I don't know the words..." until we implement some. That's what the whole rest of the tutorial is about.

## Example
We are implementing a natural language interface to a file system. so we derive from `State` and add two things to it. 
```
# Optimized for the file system example
class FileSystemState(State):
    def __init__(self, file_system):
        super().__init__([])
        self.file_system = file_system
        self.current_user = file_system_example.objects.Actor(name="User", person=1, file_system=file_system)
        self.actors = [self.current_user,
                       file_system_example.objects.Actor(name="Computer", person=2, file_system=file_system)]

    def all_individuals(self):
        yield from self.file_system.all_individuals()
        yield from self.actors

    def user(self):
        return self.current_user
```

This will be the state object we'll use, so now hello world is this, where the only change is telling the system to use our `FileSystemState` object instead of the built in `State`:

```
from perplexity.state import State
from perplexity.user_interface import UserInterface
from perplexity.vocabulary import Vocabulary

vocabulary = Vocabulary()


def reset():
    return FileSystemState([])


def hello_world():
    user_interface = UserInterface(reset, vocabulary)

    while True:
        user_interface.interact_once()
        print()


if __name__ == '__main__':
    hello_world()
```

Last update: 2023-05-15 by EricZinda [[edit](https://github.com/EricZinda/Perplexity/edit/main/docs/pxHowTo/pxHowTo14HelloWorld.md)]{% endraw %}