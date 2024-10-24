## Determining the Right Parse and Tree
In the [previous section](pxint0070GenerateMRSAndTrees), we wrote the code to generate all the parses for a phrase, and all the fully-resolved MRS trees that result from. Next we have to decide which one is the one the user intended and write the code to run it. As discussed in the conceptual topic on [Choosing a Parse and Tree](../devcon/devcon0060WhichParseAndTree), returning the response from the first MRS parse and tree that succeeded (or failed) is good heuristic to use in general. 

To implement the code for choosing the right tree, we're going to create a new class that will be the main entry point into the whole system. It is called `UserInterface` and its main method is `interact_once()`. Each call to that method does a single "command/response" interaction with the system mostly using code we've already written. Here's a summary of its logic:

1. Use the code we wrote in the [previous topic](pxint0070GenerateMRSAndTrees) to convert the phrase to MRS and then generate the trees for the MRS, go through them in order. 
2. Solve the trees using a modification to the `call()` function from [Conjunctions topic](pxint0050Conjunctions) which is called `solve`. Go through these in order.
3. If an error occurs when solving a tree, get a string for it by calling `generate_message_with_index` (which gets passed as an argument to `interact_once`). We built this in the [English Domain Names section](pxint0120ErrorsConceptualFailures)
4. When we are done, actually respond using the (slightly refactored) `respond_to_solutions()` function we built in [the Propositions Section](pxint0080SimplePropositions)

The new code is at the end of the function, where we apply all the operations to a single state object and then store it away as the new state.  Otherwise, changes would just get discarded and the next interaction wouldn't see them.

Our new code iterates through every MRS, then every tree it has.  If the function succeeds on a particular tree, it stops processing. Otherwise, it continues until it finds a succcess or runs out of trees. If nothing succeeds, it will report the first tree failure.

Here is the full code for it:
~~~
class UserInterface(object):
    def __init__(self, state, vocabulary):
        self.max_holes = 13
        self.state = state
        self.execution_context = ExecutionContext()
        self.vocabulary = vocabulary

    # response_function gets passed three arguments:
    #   response_function(mrs, solutions, error)
    # It must use them to return a string to say to the user
    def interact_once(self, response_function):
        # input() pauses the program and waits for the user to
        # type input and hit enter, and then returns it
        user_input = str(input("? "))
        best_failure = None

        # Loop through each MRS and each tree that can be
        # generated from it...
        for mrs_raw in self.mrss_from_phrase(user_input):
            for tree in self.trees_from_mrs(mrs_raw):
                print(tree)
                # Collect all the solutions for this tree against the
                # current world state
                mrs = {"Index": mrs_raw.index,
                       "Variables": mrs_raw.variables,
                       "RELS": tree}

                call_state = self.state.set_x("mrs", (mrs, ))
                solutions = []
                try:
                    for item in context().solve(vocabulary, call_state, mrs["RELS"]):
                        solutions.append(item)
                except NotImplementedError as e:
                    print(str(e))
                    continue

                # Determine the response to it
                error_text = response_function(call_state,
                                               context().deepest_error_predication_index(),
                                               context().deepest_error()) if len(solutions) == 0 else None

                message = respond_to_solutions(call_state, mrs, solutions, error_text)
                if len(solutions) > 0:
                    # This worked, give a response
                    print(message)

                    # apply the results to the current world state if it was a command
                    if sentence_force(mrs) == "comm":
                        self.state = self.apply_solutions_to_state(self.state, solutions)
                        print(f"New state: {str(self.state.objects)}")

                    return
                else:
                    # This failed, remember it if it is the "best" failure
                    # which we currently define as the first one
                    if best_failure is None:
                        best_failure = message

        # If we got here, nothing worked: print out the best failure
        print(best_failure)
        
        ...
~~~

Here is the modified `ExecutionContext` that has the new `solve()` method that is only there to reset the predication index since it can now be called multiple times as we process new phrases:

~~~
class ExecutionContext(object):
    def __init__(self):
        self.reset()

    def reset(self):
        self._error = None
        self._error_predication_index = -1
        self._predication_index = -1

    def solve(self, vocabulary, state, term):
        self.reset()
        yield from call(vocabulary, state, term)

    def call(self, vocabulary, state, term):
        ...
        
    ...
~~~

Below is the modified `respond_to_solutions()` function. It no longer generates solutions or error text, instead it requires the caller to pass them in. That allows us to centralize the code that does the solving into `interact_once()`.  It also returns the response instead of printing it now.  The rest of the code is the same:

~~~
def respond_to_solutions(state, mrs, solutions, error_text):
    force = sentence_force(mrs)
    if force == "prop":
        # This was a proposition, so the user only expects
        # a confirmation or denial of what they said.
        # The phrase was "true" if there was at least one answer
        if len(solutions) > 0:
            return "Yes, that is true."
        else:
            return f"No, that isn't correct: {error_text}"

    elif force == "ques":
        # See if this is a "WH" type question
        wh_predication = find_predication(mrs["RELS"], "_which_q")
        if wh_predication is None:
            # This was a simple question, so the user only expects
            # a yes or no.
            # The phrase was "true" if there was at least one answer
            if len(solutions) > 0:
                return "Yes."
            else:
                return f"No, {error_text}"
        else:
            # This was a "WH" question
            # return the values of the variable asked about
            # from the solution
            # The phrase was "true" if there was at least one answer
            if len(solutions) > 0:
                wh_variable = wh_predication.args[0]
                for solutions in solutions:
                    return f"{str(solutions.get_binding(wh_variable).value)}"
            else:
                return f"{error_text}"

    elif force == "comm":
        # This was a command so, if it works, just say so
        # We'll get better errors and messages in upcoming sections
        if len(solutions) > 0:
            return f"Done!"
        else:
            return f"Couldn't do that: {error_text}"
~~~

We also moved the functions that parse and build trees (`mrss_from_phrase`, `tree_from_assignments` and `trees_from_mrs`) to be part of the `UserInterface` class just to clean up the code.

With this, we now have a (simple) fully-functioning interactive natural language system! Here's a simple example that runs it in a loop, and an interactive session using some phrases we've used throughout the tutorial to test it:

~~~
def Example12():
    state = State([Actor(name="Computer", person=2),
                   Folder(name="Desktop"),
                   Folder(name="Documents"),
                   File(name="file1.txt", size=2000000),
                   File(name="file2.txt", size=100)])

    user_interface = UserInterface(state, vocabulary)

    while True:
        user_interface.interact_once(generate_message_with_index)
        print()
        
~~~

Running that sample leaves you at the command prompt waiting for you to interact.  Here's a session that runs all the phrases we've done in previous sections:

~~~
? a file is large
[_a_q(x3,[_file_n_of(x3,i8)],[_large_a_1(e2,x3)])]
Yes, that is true.

? which file is large?
[_which_q(x3,[_file_n_of(x3,i8)],[_large_a_1(e2,x3)])]
(File(file1.txt, 2000000),)

? delete a large file
[_a_q(x4,[_large_a_1(e9,x4), _file_n_of(x4,i10)],[_delete_v_1(e2,i3,x4)])]
Implementation for Predication _delete_v_1(e2,i3,x4) not found
[pronoun_q(x3,[pron(x3)],[_a_q(x8,[_large_a_1(e13,x8), _file_n_of(x8,i14)],[_delete_v_1(e2,x3,x8)])])]
Done!
New state: [Actor(name=Computer, person=2), Folder(Desktop), Folder(Documents), File(file2.txt, 100)]

? which file is large?
[_which_q(x3,[_file_n_of(x3,i8)],[_large_a_1(e2,x3)])]
[udef_q(x3,[_which_q(x10,[generic_entity(x10)],[nominalization(x3,[_file_v_1(e14,x10,i15)])])],[_large_a_1(e2,x3)])]
Implementation for Predication udef_q(x3,[_which_q(x10,[generic_entity(x10)],[nominalization(x3,[_file_v_1(e14,x10,i15)])])],[_large_a_1(e2,x3)]) not found
[_which_q(x10,[generic_entity(x10)],[udef_q(x3,[nominalization(x3,[_file_v_1(e14,x10,i15)])],[_large_a_1(e2,x3)])])]
Implementation for Predication generic_entity(x10) not found
which file is not large

? which folder is large?
[_which_q(x3,[_folder_n_of(x3,i8)],[_large_a_1(e2,x3)])]
which folder is not large

? a folder is large
[_a_q(x3,[_folder_n_of(x3,i8)],[_large_a_1(e2,x3)])]
No, that isn't correct: a folder is not large
~~~

`interact_once()` prints out the trees that get found so it is easier to see which is being used and which have missing predications. It also helps point out when a tree failed and the solver is trying more trees to find a success. You can see that in action by looking at the difference between the first "which file is large?" which only generates one tree since it succeeds, and the second one which fails since there are no large files.  The second one keeps going trying to find a tree that works.

> Comprehensive source for the completed tutorial is available [here](https://github.com/EricZinda/Perplexity/tree/main/samples/hello_world)
