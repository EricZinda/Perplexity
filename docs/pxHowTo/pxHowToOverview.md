## Perplexity Overview
Perplexity is a Python library designed to build natural language interfaces for various kinds of software. It builds a Python interface on top of the DELPH-IN technologies and allows developers to build a natural language interface for an application by implementing their application vocabulary as Python functions.


~~~


def hello_world():
    user_interface = UserInterface(State(), vocabulary, respond_to_mrs_tree, error_priority)

    while True:
        user_interface.interact_once()
        print()
        
if __name__ == '__main__':
    hello_world()
    
~~~