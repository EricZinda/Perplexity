# 
The [Developer How-To section](../devhowto/devhowtoOverview) is a tutorial that introduces developers to the DELPH-IN technologies by building a Python framework called ["Perplexity"](https://github.com/EricZinda/Perplexity) that allows Python functions to implement and evaluate DELPH-IN predications. In this section, we will show how to *use it* by implementing the vocabulary for a file system using the Perplexity framework. When finished, we'll have a working interactive natural language interface that allows users to browse their file system.

This section requires a working knowledge of 

Let's start with a review of the Perplexity framework. First, user commands like: "what files are in this folder?" get parsed into an MRS document by the ACE parser. All this is done by the `UserInterface` 

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