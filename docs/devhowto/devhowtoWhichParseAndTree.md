## Determining the Right Parse and Tree
As discussed in the [MRS topic](devhowtoMRS) and the [Well-Formed Trees topic](devhowtoWellFormedTree), a single phrase like "Look under the table" produces `m` MRS documents, and each of those produces `n` well-formed trees, thus generating `m x n` potential interpretations of a phrase. How do you determine which one is the one the user *meant*?

The short answer is that, just like when you are talking to a human, you never *really* know what they meant unless you pick your best guess and confirm it with them. But: there are a couple of things that help: First, [ACE](http://sweaglesw.org/linguistics/ace/) uses a machine-learning-based algorithm to sort the MRS documents and returns the "most common" ones first. This means the more obscure MRS interpretations will be sorted last. Unfortunately, there is no such mechanism for the well-formed trees. So, at best we have a partial ordering of the `m x n` trees in terms of "most commonly meant". 

With that in mind, a simple approach to choosing the "right" interpretation that works surprisingly well is: 

> Execute each well-formed tree against the world state using the provided partial order. Assume the first one that succeeds is what the user meant. If none succeed, return the first failure.

This works for the same reason human interactions work: Most phrases are meant to convey information that *makes sense*. I.e. the phrase discusses things that actually exist, uses verbs that make sense with objects being discussed, etc. So, most phrases the user gives your system *should* have a solution given the current world state. Furthermore, humans have an intuitive understanding of the ambiguity of language and are forgiving of errors when they are understandable and logical failures. I.e. "I can see why you thought that, even though it wasn't what I meant...". 

So, if the system finds a tree that has a solution in the current world state, it is likely to be at least close to what the user meant. Even if it isn't, given that it was a solution in the world state, it will still be *logical* and the user will very often understand (and sometimes be delighted by) how their phrase was misinterpreted.

Thus, the approach to finding which of the `m x n` meanings is the "meant one" is to run them all, in order, and assume the first that works is the right one.

Things get a little trickier if none of them works. However, the same principle holds: as long as the error response we give is *logical* and *understandable*, it will make sense to the user, even if it isn't quite the answer a person would have given. Often we can do better than just returning the first failure, but this requires knowing what kinds of errors your particular system produces, which ones are less useful, etc. For now, we'll just return the first failure.

To implement the code for choosing the right tree, we're going to create a new class that will be the main entry point into the whole system. It is called `UserInterface` and its main method is `interact_once()`. Each call to that method does a single "command/response" interaction with the system. It uses the code we wrote in the [previous topic](devhowtoGenerateMRSAndTrees) to convert the phrase to MRS, and then generate the trees for the MRS. It then iterates through all of them and solves them using `solve_mrs_tree()` which solves the tree using the approach we saw in the [Conjunctions topic](devhowtoConjunctions):

~~~
class UserInterface(object):
    def __init__(self, state, vocabulary):
        self.max_holes = 13
        self.state = state
        self.execution_context = ExecutionContext(vocabulary)
        
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
        for mrs in self.mrss_from_phrase(user_input):
            for tree in self.trees_from_mrs(mrs):
                # Collect all the solutions for this tree against the
                # current world state
                tree_info = {"Index": mrs.index,
                             "Variables": mrs.variables,
                             "Tree": tree}

                solutions = []
                for item in self.execution_context.solve_mrs_tree(self.state, tree_info):
                    pipeline_logger.debug(f"solution: {item}")
                    solutions.append(item)

                # Determine the response to it
                error = self.execution_context.error()
                pipeline_logger.debug(f"{len(solutions)} solutions, error: {error}")
                message = response_function(tree_info, solutions, error)
                if len(solutions) > 0:
                    # This worked, apply the results to the current world state if it was a command
                    if sentence_force(tree_info) == "comm":
                        self.apply_solutions_to_state(solutions)

                    print(message)
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

The function that `interact_once()` is passed in the `response_function` argument is responsible for taking the MRS, the solutions (if any), and the error (if any) and generating a response to the user. This function is the same one we've been using all along (`respond_to_mrs_tree()`). It, and the main function it calls (`generate_message()` -- that we've also been using all along), are included below:

~~~
def respond_to_mrs_tree(tree, solutions, error):
    sentence_force_type = sentence_force(tree)
    if sentence_force_type == "prop":
        # This was a proposition, so the user only expects
        # a confirmation or denial of what they said.
        # The phrase was "true" if there was at least one answer
        if len(solutions) > 0:
            return "Yes, that is true."
        else:
            message = generate_message(tree, error)
            return message

    elif sentence_force_type == "ques":
        # See if this is a "WH" type question
        wh_predication = find_predicate(tree["Tree"], "_which_q")
        if wh_predication is None:
            # This was a simple question, so the user only expects
            # a yes or no.
            # The phrase was "true" if there was at least one answer
            if len(solutions) > 0:
                return "Yes."
            else:
                message = generate_message(tree, error)
                return message
        else:
            # This was a "WH" question
            # return the values of the variable asked about
            # from the solution
            # The phrase was "true" if there was at least one answer
            if len(solutions) > 0:
                wh_variable = wh_predication[1]
                message = ""
                for solution in solutions:
                    message += str(solution.get_variable(wh_variable)) + "\n"

                return message
            else:
                message = generate_message(tree, error)
                return message

    elif sentence_force_type == "comm":
        # This was a command so, if it works, just say so
        # We'll get better errors and messages in upcoming sections
        if len(solutions) > 0:
            return "Done!"
        else:
            message = generate_message(tree, error)
            return message


# Generates all the responses that predications can return when an error
# occurs
#
# error_term is of the form: [index, error] where "error" is another
# list like: ["name", arg1, arg2, ...]. The first item is the error
# constant (i.e. its name). What the args mean depends on the error
def generate_message(mrs, error_term):
    error_predicate_index = error_term[0]
    error_arguments = error_term[1]
    error_constant = error_arguments[0]

    if error_constant == "xIsNotY":
        arg1 = english_for_delphin_variable(error_predicate_index, error_arguments[1], mrs)
        arg2 = error_arguments[2]
        return f"{arg1} is not {arg2}"

    elif error_constant == "adjectiveDoesntApply":
        arg1 = error_arguments[1]
        arg2 = english_for_delphin_variable(error_predicate_index, error_arguments[2], mrs)
        return f"{arg2} is not {arg1}"
        
    ...
~~~

With this, we now have a (simple) fully functioning interactive natural language system! Here's a simple example that runs it in a loop, and an interactive session using some phrases we've used throughout the tutorial to test it:

~~~
def Example16():
    state = State([Actor(name="Computer", person=2),
                   Folder(name="Desktop"),
                   Folder(name="Documents")])

    user_interface = UserInterface(state, vocabulary)

    while True:
        user_interface.interact_once(respond_to_mrs_tree)
        print()
        
# Example15 session:

? a file is large
Yes, that is true.

? which file is large?
File(name=file1.txt, size=2000000)

? which folder is large?
a folder is not large

? delete a folder
Done!

? delete him
There isn't 'he/she' in the system
~~~

> Comprehensive source for the completed tutorial is available [here](https://github.com/EricZinda/Perplexity).
