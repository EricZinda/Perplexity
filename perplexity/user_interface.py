import logging
import os
import platform
import sys
from delphin import ace
from file_system_example.messages import generate_message
from perplexity.execution import ExecutionContext
from perplexity.tree import find_predicate, tree_from_assignments
from perplexity.tree_algorithm_zinda2020 import valid_hole_assignments
from perplexity.utilities import sentence_force


class UserInterface(object):
    def __init__(self, state, vocabulary):
        self.max_holes = 13
        self.state = state
        self.execution_context = ExecutionContext(vocabulary)

    # response_function gets passed: response_function(mrs, solutions, error) and
    # must return a string to say to the user
    def interact_once(self, response_function):
        user_input = str(input("? "))

        best_message = None
        for mrs in self.mrss_from_phrase(user_input):
            for tree in self.trees_from_mrs(mrs):
                # Collect all the solutions for this tree against the
                # current world state
                mrs = {"Index": mrs.index,
                       "Variables": mrs.variables,
                       "Tree": tree}

                solutions = []
                for item in self.execution_context.solve_mrs_tree(self.state, mrs):
                    solutions.append(item)

                # Determine the response to it
                message = response_function(mrs, solutions, self.execution_context.error())
                if len(solutions) > 0:
                    # This worked, apply the results to the current world state if it was a command
                    if sentence_force(mrs) == "comm":
                        self.apply_solutions_to_state(solutions)

                    print(message)
                    return
                else:
                    # This failed, remember it if it is the "best"
                    # failure
                    if best_message is None:
                        best_message = message

        # If we got here, nothing worked: print out the best failure
        print(best_message)

    def apply_solutions_to_state(self, solutions):
        # Collect all of the operations that were done
        all_operations = []
        for solution in solutions:
            all_operations += solution.get_operations()

        # Now apply all the operations to the original state object and
        # print it to prove it happened
        self.state = self.state.apply_operations(all_operations)
        print(self.state.objects)

    def mrss_from_phrase(self, phrase):
        # Don't print errors to the screen
        f = open(os.devnull, 'w')

        # Create an instance of the ACE parser and ask to give <= 25 MRS documents
        with ace.ACEParser(self.erg_file(), cmdargs=['-n', '25'], stderr=f) as parser:
            ace_response = parser.interact(phrase)
            pipeline_logger.debug(f"{len(ace_response['results'])} parse options for {phrase}")

        for parse_result in ace_response.results():
            # Keep track of the original phrase on the object
            mrs = parse_result.mrs()
            mrs.surface = phrase
            yield mrs

    def trees_from_mrs(self, mrs):
        # Create a dict of predications using labels as the key for easy access when building trees
        mrs_predication_dict = {}
        for predication in mrs.predications:
            if predication.label not in mrs_predication_dict.keys():
                mrs_predication_dict[predication.label] = []
            mrs_predication_dict[predication.label].append(predication)

        # Iteratively return well-formed trees from the MRS
        for holes_assignments in valid_hole_assignments(mrs, self.max_holes):
            if holes_assignments is not None:
                well_formed_tree = tree_from_assignments(mrs.top, holes_assignments, mrs_predication_dict, mrs)
                yield well_formed_tree

    def erg_file(self):
        if sys.platform == "linux":
            ergFile = "erg-2020-ubuntu-perplexity.dat"

        elif sys.platform == "darwin":
            # Mac returns darwin for both M1 and Intel silicon, need to dig deeper
            unameResult = platform.uname()

            if "ARM" in unameResult.version:
                # M1 silicon
                ergFile = "erg-2020-osx-m1-perplexity.dat"

            else:
                # Intel silicon
                ergFile = "erg-2020-osx-perplexity.dat"

        else:
            ergFile = "erg-2020-ubuntu-perplexity.dat"

        return ergFile


pipeline_logger = logging.getLogger('Pipeline')
