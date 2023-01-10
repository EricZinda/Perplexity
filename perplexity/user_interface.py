import logging
import os
import platform
import sys
from delphin import ace
from perplexity.execution import ExecutionContext
from perplexity.tree import find_predicate, tree_from_assignments
from perplexity.tree_algorithm_zinda2020 import valid_hole_assignments
from perplexity.utilities import sentence_force


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
            unknown_words = self.unknown_words(mrs)
            if len(unknown_words) > 0:
                if best_failure is None:
                    best_failure = response_function(None, [], [0, ["unknownWords", unknown_words]])

                continue

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

    def unknown_words(self, mrs):
        unknown_words = []
        phrase_type = sentence_force(mrs.index, mrs.variables)
        for predication in mrs.predications:
            argument_types = [argument[1][0] for argument in predication.args.items()]
            predications = list(self.execution_context.vocabulary.predications(predication.predicate, argument_types, phrase_type))
            if len(predications) == 0:
                # This predication is not implemented
                unknown_words.append((predication.predicate,
                                      argument_types,
                                      phrase_type,
                                      # Record if at least one form is understood for
                                      # better error messages
                                      self.execution_context.vocabulary.version_exists(predication.predicate)))

        pipeline_logger.debug(f"Unknown predications: {unknown_words}")
        return unknown_words

    def apply_solutions_to_state(self, solutions):
        # Collect all of the operations that were done
        all_operations = []
        for solution in solutions:
            all_operations += solution.get_operations()

        # Now apply all the operations to the original state object and
        # print it to prove it happened
        self.state = self.state.apply_operations(all_operations)
        logger.debug(f"Final state: {self.state.objects}")

    def mrss_from_phrase(self, phrase):
        # Don't print errors to the screen
        f = open(os.devnull, 'w')

        # Create an instance of the ACE parser and ask to give <= 25 MRS documents
        with ace.ACEParser(self.erg_file(), cmdargs=['-n', '25'], stderr=f) as parser:
            ace_response = parser.interact(phrase)
            pipeline_logger.debug(f"{len(ace_response['results'])} parse options for {phrase}")

        for parse_index in range(0, len(ace_response.results())):
            # Keep track of the original phrase on the object
            mrs = ace_response.result(parse_index).mrs()
            mrs.surface = phrase
            pipeline_logger.debug(f"Parse {parse_index}: {mrs}")
            yield mrs

    def trees_from_mrs(self, mrs):
        # Create a dict of predications using their labels as each key
        # for easy access when building trees
        # Note that a single label could represent multiple predications
        # in conjunction so we need a list for each label
        mrs_predication_dict = {}
        for predication in mrs.predications:
            if predication.label not in mrs_predication_dict.keys():
                mrs_predication_dict[predication.label] = []
            mrs_predication_dict[predication.label].append(predication)

        # Iteratively return well-formed trees from the MRS
        for holes_assignments in valid_hole_assignments(mrs, self.max_holes):
            # valid_hole_assignments can return None if the grammar returns something
            # that doesn't have the same number of holes and floaters (which is a grammar bug)
            if holes_assignments is not None:
                # Now we have the assignments of labels to holes, but we need
                # to actually build the *tree* using that information
                well_formed_tree = tree_from_assignments(mrs.top,
                                                         holes_assignments,
                                                         mrs_predication_dict,
                                                         mrs)
                pipeline_logger.debug(f"Tree: {well_formed_tree}")
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


logger = logging.getLogger('UserInterface')
pipeline_logger = logging.getLogger('Pipeline')
