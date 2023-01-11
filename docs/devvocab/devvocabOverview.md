# 
The [Developer How-To section](/docs/devhowto/devhowtoOverview) is a tutorial that describes how to build a Python framework for implementing the vocabulary of an application using DELPH-IN technologies. The framework is called ["Perplexity"](https://github.com/EricZinda/Perplexity).  In this section, we will show how to *use it* by implementing the vocabulary for a file system using the Perplexity framework. When finished, we'll have a working interactive natural language interface that allows users to browse their file system.

Let's start with a review of the Perplexity framework. First user commands like: "what files are in this folder?" get parsed into an MRS document by the ACE parser. All this is done

~~~
def Example16():
    state = State([Actor(name="Computer", person=2),
                   Folder(name="Desktop"),
                   Folder(name="Documents"),
                   File(name="file1.txt", size=2000000)])

    user_interface = UserInterface(state, vocabulary)

    while True:
        user_interface.interact_once(respond_to_mrs_tree)
        print()
~~~