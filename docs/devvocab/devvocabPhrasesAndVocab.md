## Phrases and Vocabulary
When implementing a natural language system using DELPH-IN, start by analyzing the phrases you want to support and the predications they generate. The predications are what you'll need to implement. We can interact with the system we [ended the previous section with](../devhowto/devhowtoPredicationArgumentsAndUsage) and turn tracing on in order to see the predications for the phrases we type.  

Here's the code we'll use:

~~~
def Example16():
    ShowLogging("Pipeline")

    state = State([Actor(name="Computer", person=2),
                   Folder(name="Desktop"),
                   Folder(name="Documents"),
                   File(name="file1.txt", size=2000000)])

    user_interface = UserInterface(state, vocabulary)

    while True:
        user_interface.interact_once(respond_to_mrs_tree)
        print()
~~~

Note that the previous section already implemented an initial set of predications: [`_a_q`](../devhowto/devhowtoScopalArguments), [`file_n_of`, `large_a_1`](../devhowto/devhowtoConjunctions), [`small_a_1`](../devhowto/devhowtoHandlingEventInformation), and [`which_q`, `pron`, `pronoun_q`, `very_x_deg`, `folder_n_of`, `delete_v_1`](../devhowto/devhowtoFinishingErrors).

To determine the next set, let's feed phrases we want to support into `Example16()` and see what predications are missing.

### Where am i?
We should support "where am i?" by having a notion of the "current" directory and printing it:
~~~
# Running Example16() gives:
? where am i
Pipeline 2023-01-11 13:58:27,286: 1 parse options for where am i
Pipeline 2023-01-11 13:58:27,294: Parse 0: <MRS object (loc_nonsp place_n which_q pron pronoun_q) at 140561813576608>
Pipeline 2023-01-11 13:58:27,294: Unknown predications: [('loc_nonsp', ['e', 'x', 'x'], 'ques', False), ('place_n', ['x'], 'ques', False)]
I don't know the words: loc_nonsp, place
~~~




> Comprehensive source for the completed tutorial is available [here](https://github.com/EricZinda/Perplexity).
