from file_system_example.state import State
from perplexity.user_interface import UserInterface
from perplexity.vocabulary import Vocabulary

vocabulary = Vocabulary()


def hello_world():
    user_interface = UserInterface(State(), vocabulary, respond_to_mrs_tree, error_priority)

    while True:
        user_interface.interact_once()
        print()


def respond_to_mrs_tree(tree, solution_groups, error):
    yield "Hello!", None


def error_priority(error_string):
    if error_string is None:
        return 0


if __name__ == '__main__':
    hello_world()
