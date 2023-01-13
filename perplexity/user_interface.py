import logging
import os
import platform
import sys
from delphin import ace
from delphin.codecs import simplemrs

from perplexity.execution import ExecutionContext
from perplexity.print_tree import create_draw_tree, TreeRenderer
from perplexity.tree import find_predicate, tree_from_assignments
from perplexity.tree_algorithm_zinda2020 import valid_hole_assignments
from perplexity.utilities import sentence_force, sentence_force_from_tree_info


class UserInterface(object):
    def __init__(self, state, vocabulary):
        self.max_holes = 13
        self.state = state
        self.execution_context = ExecutionContext(vocabulary)
        self.interaction_record = None

    # response_function gets passed three arguments:
    #   response_function(mrs, solutions, error)
    # It must use them to return a string to say to the user
    # Builds up a record of what happened so diagnostics
    # can be printed later
    def interact_once(self, response_function):
        # input() pauses the program and waits for the user to
        # type input and hit enter, and then returns it
        user_input = str(input("? "))

        # If this was a system command, do whatever it does
        # and then wait for the next one
        if self.handle_command(user_input):
            return

        self.interaction_record = {"UserInput": user_input,
                                   "Mrss": [],
                                   "ChosenMrsIndex": None,
                                   "ChosenTree": None,
                                   "ChosenResponse": None}

        # Loop through each MRS and each tree that can be
        # generated from it...
        for mrs in self.mrss_from_phrase(user_input):
            mrs_record = {"Mrs": mrs,
                          "UnknownWords": self.unknown_words(mrs),
                          "Trees": []}
            self.interaction_record["Mrss"].append(mrs_record)
            if len(mrs_record["UnknownWords"]) > 0:
                if self.interaction_record["ChosenResponse"] is None:
                    self.interaction_record["ChosenResponse"] = response_function(None, [], [0, ["unknownWords", mrs_record["UnknownWords"]]])
                    self.interaction_record["ChosenMrsIndex"] = len(self.interaction_record["Mrss"]) - 1
                    self.interaction_record["ChosenTree"] = len(mrs_record["Trees"]) - 1

                continue

            for tree in self.trees_from_mrs(mrs):
                tree_record = {"Tree": tree,
                               "Solutions": [],
                               "Error": None,
                               "ResponseMessage": None}
                mrs_record["Trees"].append(tree_record)

                # Collect all the solutions for this tree against the
                # current world state
                tree_info = {"Index": mrs.index,
                             "Variables": mrs.variables,
                             "Tree": tree}

                for item in self.execution_context.solve_mrs_tree(self.state, tree_info):
                    pipeline_logger.debug(f"solution: {item}")
                    tree_record["Solutions"].append(item)

                # Determine the response to it
                tree_record["Error"] = self.execution_context.error()
                pipeline_logger.debug(f"{len(tree_record['Solutions'])} solutions, error: {tree_record['Error']}")
                tree_record["ResponseMessage"] = response_function(tree_info, tree_record["Solutions"], tree_record["Error"])
                if len(tree_record["Solutions"]) > 0:
                    self.interaction_record["ChosenMrsIndex"] = len(self.interaction_record["Mrss"]) - 1
                    self.interaction_record["ChosenTree"] = len(mrs_record["Trees"]) - 1

                    # This worked, apply the results to the current world state if it was a command
                    if sentence_force_from_tree_info(tree_info) == "comm":
                        self.apply_solutions_to_state(tree_record["Solutions"])

                    print(tree_record["ResponseMessage"])
                    return

                else:
                    # This failed, remember it if it is the "best" failure
                    # which we currently define as the first one
                    if self.interaction_record["ChosenResponse"] is None:
                        self.interaction_record["ChosenResponse"] = tree_record["ResponseMessage"]
                        self.interaction_record["ChosenMrsIndex"] = len(self.interaction_record["Mrss"]) - 1
                        self.interaction_record["ChosenTree"] = len(mrs_record["Trees"]) - 1

        # If we got here, nothing worked: print out the best failure
        print(self.interaction_record["ChosenResponse"])

    # Commands always start with "/", followed by a string of characters and then
    # a space. Any arguments are after the space and their format is command specific.
    # For example:
    #   /show all
    def handle_command(self, value):
        cleaned_value = value.strip()
        if len(cleaned_value) > 0 and cleaned_value[0] == "/":
            parts = cleaned_value[1:].split(" ")
            if len(parts) > 1:
                all = parts[1].lower() == "all"
            else:
                all = False

            if parts[0].lower() == "show":
                self.print_diagnostics(all)

            else:
                print(f"unknown command '{parts[0]}'")

            return True

        else:
            return False

    def print_diagnostics(self, all):
        if self.interaction_record is not None:
            print(f"User Input: {self.interaction_record['UserInput']}")
            print(f"{len(self.interaction_record['Mrss'])} Parses")

            for mrs_index in range(0, len(self.interaction_record["Mrss"])):
                if all or mrs_index == self.interaction_record["ChosenMrsIndex"]:
                    extra = "CHOSEN " if mrs_index == self.interaction_record["ChosenMrsIndex"] else ""
                    print(f"\n***** {extra}Parse #{mrs_index}:")
                    mrs_record = self.interaction_record["Mrss"][mrs_index]
                    print(simplemrs.encode(mrs_record["Mrs"], indent=True))
                    print(f"\nUnknown words: {mrs_record['UnknownWords']}")
                    if all:
                        chosen_tree = None
                    else:
                        chosen_tree = self.interaction_record["ChosenTree"]

                    self.print_diagnostics_trees(all, mrs_index, chosen_tree, mrs_record)

    def print_diagnostics_trees(self, all, parse_number, chosen_tree, mrs_record):
        if len(mrs_record["Trees"]) == 0:
            # The trees aren't generated if we don't know terms for performance
            # reasons (since we won't be evaluating anything)
            tree_generator = [{"Tree": tree,
                               "Solutions": [],
                               "Error": None,
                               "ResponseMessage": None} for tree in self.trees_from_mrs(mrs_record["Mrs"])]
        else:
            tree_generator = mrs_record["Trees"]

        tree_index = 0
        for tree in tree_generator:
            if all or chosen_tree == tree_index:
                extra = "CHOSEN " if chosen_tree == tree_index else ""
                print(f"\n-- {extra}Parse #{parse_number}, {extra}Tree #{tree_index}: \n")
                draw_tree = create_draw_tree(mrs_record["Mrs"], tree["Tree"])
                renderer = TreeRenderer()
                renderer.print_tree(draw_tree)
                print(f"\n{tree['Tree']}")
                if len(tree['Solutions']) > 0:
                    for solution in tree['Solutions']:
                        print(f"Solution: {str(solution)}")

                else:
                    print(f"Error: {tree['Error']}")

                print(f"Response: {tree['ResponseMessage']}")

            tree_index += 1

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
