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
