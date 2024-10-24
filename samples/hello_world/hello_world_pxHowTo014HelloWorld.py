from perplexity.state import State
from perplexity.user_interface import UserInterface
from perplexity.vocabulary import Vocabulary
from perplexity.world_registry import register_world


# Contains entries for all predications we've implemented
# but just an initial Vocabulary object for now since
# we have none
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
               module="hello_world_pxHowTo014HelloWorld",
               ui_function="ui")


if __name__ == '__main__':
    user_interface = ui()
    while user_interface:
        # The loop might return a different user interface
        # object if the user changes worlds
        user_interface = user_interface.default_loop()