import copy
import json
import logging
import os
import pickle
import sys
import time
import uuid
import perplexity.messages
from delphin.codecs import simplemrs
from perplexity.autocorrect import autocorrect, get_autocorrect
from perplexity.execution import MessageException, TreeSolver, ExecutionContext
from perplexity.print_tree import create_draw_tree, TreeRenderer
from perplexity.response import ResetOperation, ResponseLocation
from perplexity.set_utilities import CachedIterable
from perplexity.state import apply_solutions_to_state, LoadException
from perplexity.test_manager import TestManager, TestIterator, TestFolderIterator
from perplexity.transformer import TransformerMatch
from perplexity.tree import find_predications, find_predications_with_arg_types, \
    MrsParser, tree_contains_predication, TreePredication, get_wh_question_variable, surface_word_from_mrs_predication, \
    syntactic_heads_characteristic_variables
from perplexity.tree_algorithm_zinda2020 import TooComplicatedError
from perplexity.user_state import GetStateDirectoryName
from perplexity.utilities import sentence_force, module_name, import_function_from_names, at_least_one_generator, \
    split_into_sentences, output_interaction_records
from perplexity.world_registry import world_information, LoadWorldOperation, ui_from_world_name


def default_error_priority(error):
    system_priority = perplexity.messages.error_priority(error)
    if system_priority is not None:
        return system_priority
    else:
        return perplexity.messages.error_priority_dict["defaultPriority"]


def load_ui(path_and_filename, user_output=None, debug_output=None):
    with open(path_and_filename, "rb") as file:
        metadata = pickle.load(file)
        world_info = world_information(metadata.get("WorldName", None))
        if world_info is None:
            raise LoadException
        else:
            ui_function = import_function_from_names(world_info["WorldModule"], world_info["WorldUIFunction"])
            return ui_function(metadata, file, user_output, debug_output)


class UserInterface(object):
    def __init__(self,
                 world_name,
                 reset_function,
                 vocabulary,
                 message_function=perplexity.messages.generate_message,
                 error_priority_function=default_error_priority,
                 response_function=perplexity.messages.respond_to_mrs_tree,
                 scope_init_function=None,
                 scope_function=None,
                 loaded_state=None,
                 user_output=None,
                 debug_output=None,
                 best_parses_file=None,
                 events=None,
                 timeout=None):

        self.user_output = print if user_output is None else user_output
        self.debug_output = print if debug_output is None else debug_output
        self.best_parses_file = best_parses_file
        self.autocorrect_file = get_autocorrect(world_name)
        self.max_holes = 14
        self.timeout = 15 if timeout is None else timeout
        self.generate_all_parses = False

        if best_parses_file is not None and os.path.exists(best_parses_file):
            with open(best_parses_file) as json_file:
                self.best_parses = json.load(json_file)
        else:
            self.best_parses = {}

        self.world_name = world_name
        self.reset = None
        self.vocabulary = None
        self.scope_function = None
        self.scope_init_function = None
        self.response_function = None
        self.message_function = None
        self.error_priority_function = None
        self.state = None
        if loaded_state is None:
            loaded_state = reset_function()
        self.load_ui(loaded_state, reset_function, vocabulary, message_function, error_priority_function, response_function, scope_init_function, scope_function)

        self.interaction_record = None
        self.records = None
        self.test_manager = TestManager()
        self.user_input = None
        self.last_system_command = None
        self.run_mrs_index = None
        self.run_tree_index = None
        self.show_all_answers = False
        self.run_all_parses = False
        # Only do the first 5 parses because quality falls off fast
        self.mrs_parser = MrsParser(self.max_holes, max_parses=5)
        self.log_tests = False
        self.new_ui = None
        self.events = events

    def load_ui(self, state, reset, vocabulary, message_function=perplexity.messages.generate_message, error_priority_function=default_error_priority, response_function=perplexity.messages.respond_to_mrs_tree, scope_init_function=None, scope_function=None):
        self.reset = reset
        self.vocabulary = vocabulary
        self.message_function = message_function
        self.error_priority_function = error_priority_function
        self.response_function = response_function
        self.scope_function = scope_function
        self.scope_init_function = scope_init_function

        self.state = state

    def save(self, path_and_filename):
        with open(path_and_filename, "wb") as file:
            pickle.dump({"WorldName": self.world_name, "Version": 1}, file, 5)
            self.state.save(file)

    def chosen_interpretation_record(self):
        if self.interaction_record is None:
            return None

        chosen_mrs_index = self.interaction_record["ChosenMrsIndex"]
        if chosen_mrs_index is None:
            return None

        else:
            chosen_interpretation_index = self.interaction_record["ChosenInterpretationIndex"]
            return self.interaction_record["Mrss"][chosen_mrs_index]["Interpretations"][chosen_interpretation_index]

    def new_mrs_record(self, mrs=None, unknown_words=None):
        return {"Mrs": mrs,
                "UnknownWords": unknown_words,
                "Interpretations": []}

    def default_loop(self):
        # Deal with command line arguments so that testing works the same across all worlds
        command_line_commands = sys.argv[1:] if len(sys.argv) > 1 else []
        while True:
            command = command_line_commands.pop(0) if len(command_line_commands) > 0 else None
            if command == "exit":
                os._exit(0)

            else:
                self.interact_once_across_conjunctions(command)
                if self.new_ui:
                    # The user gave a command to load a new UI
                    return self.new_ui

            output = self.user_output()

    def has_timed_out(self):
        if perplexity.utilities.running_under_debugger():
            return False

        if self.interaction_record is not None and time.perf_counter() - self.interaction_record["StartTime"] > self.timeout:
            pipeline_logger.debug(f"Timed out.")
            return True

        else:
            return False

    def output_sorted_responses(self, responses):
        responses.sort(key=lambda tup: tup[0])
        return "\n".join(item[1] for item in responses)

    # Convert any input that was multiple sentences into multiple interactions
    # Then: If the phrase is an implicit or explicit conjunction -- basically more than
    #       one phrase put together -- run the interaction loop N times, once for each conjunct.
    # Collect, and then return a list of interaction records that represent each all the interactions for the
    #       sentences and their conjuncts
    def interact_once_across_conjunctions(self, force_input=None):
        interaction_records = []
        next_ui = self

        if force_input is None:
            # input() pauses the program and waits for the user to
            # type input and hit enter, and then returns it
            self.user_input = str(input("? "))
        else:
            self.user_input = force_input

        command_result = self.handle_command(self.user_input)
        if command_result is not None:
            # If not None it was a system command
            self.test_manager.record_session_data("last_system_command", self.user_input)

        else:
            self.test_manager.record_session_data("last_phrase", self.user_input)

        if command_result is True:
            # if True, it was entirely handled and didn't have text to further process
            return []

        # Create an interaction record in case this is a command
        self.interaction_record = {"UserInput": self.user_input,
                                   "Mrss": [],
                                   "ChosenMrsIndex": None,
                                   "ChosenInterpretationIndex": None}

        if command_result is not None:
            # If not None it was a system command
            mrs_record = self.new_mrs_record()
            self.interaction_record["Mrss"].append(mrs_record)
            tree_record = TreeSolver.new_error_tree_record(response_generator=[command_result])
            mrs_record["Interpretations"].append(tree_record)
            self.interaction_record["ChosenMrsIndex"] = 0
            self.interaction_record["ChosenInterpretationIndex"] = 0
            self.user_output(command_result)

        last_phrase_response = ""
        record = None
        if command_result is not None:
            # If not None it was a system command so the interaction is done
            interaction_records.append(self.interaction_record)
            record = self.interaction_record

        else:
            # This was a phrase not a command (or a command that pushed a phrase through the system)
            # Do any corrections or fixup on the text
            self.user_input = self.autocorrect(self.user_input)
            sentences = split_into_sentences(self.user_input)
            for sentence in sentences:
                next_conjuncts = None
                conjunct_mrs_index = None
                conjunct_tree_index = None

                while True:
                    # Create a new interaction record for this sentence
                    self.user_input = sentence
                    self.interaction_record = {"UserInput": self.user_input,
                                               "Mrss": [],
                                               "ChosenMrsIndex": None,
                                               "ChosenInterpretationIndex": None,
                                               "StartTime": time.perf_counter()}

                    self._interact_once(force_input=sentence,
                                        conjunct_mrs_index=conjunct_mrs_index,
                                        conjunct_tree_index=conjunct_tree_index,
                                        next_conjuncts=next_conjuncts)

                    interaction_records.append(self.interaction_record)

                    next_ui = self.new_ui if self.new_ui else next_ui
                    record = self.chosen_interpretation_record()
                    if record is not None:
                        # There was a parse (whether successful or not)
                        if record["SolutionGroupGenerator"] is not None:
                            if "LastPhraseResponse" in record:
                                last_phrase_response = record["LastPhraseResponse"]

                            if self.new_ui is not None:
                                record["NewWorld"] = True

                                # Give the current world a chance to end its interaction
                                if self.events is not None:
                                    end_responses = self.events.interaction_end(self, interaction_records, last_phrase_response)
                                    if end_responses is not None:
                                        record["InteractionEnd"] = self.output_sorted_responses(end_responses)

                                # Because we are in a new world, the last_phrase_response gets reset
                                last_phrase_response = ""

                            # There were solutions, so keep going with conjuncts
                            if "SelectedConjuncts" in record and record["SelectedConjuncts"] is not None:
                                assert len(record["SelectedConjuncts"]) == 1
                                if record["SelectedConjuncts"][0] == 1:
                                    # We've processed all the conjuncts
                                    break

                                else:
                                    # Do it again with the next conjunct
                                    next_conjuncts = [1]
                                    conjunct_mrs_index = self.interaction_record["ChosenMrsIndex"]
                                    conjunct_tree_index = self.interaction_record["Mrss"][self.interaction_record["ChosenMrsIndex"]]["Interpretations"][self.interaction_record["ChosenInterpretationIndex"]]["TreeIndex"]

                            else:
                                # No conjuncts to process
                                break

                        else:
                            # No solutions, break
                            break

                    else:
                        # No parse, break
                        break

        if self is not next_ui:
            # The user gave a command to load a new UI
            self.new_ui = next_ui

        else:
            # Give whatever was the final world a chance to end its interaction
            if self.events is not None:
                end_responses = self.events.interaction_end(self, interaction_records, last_phrase_response)
                if end_responses is not None:
                    record["InteractionEnd"] = self.output_sorted_responses(end_responses)

        self.user_output(output_interaction_records(interaction_records))

        # self.records is a list if we are recording commands
        if isinstance(self.records, list):
            self.records.append(interaction_records)
            self.user_output(f"Recorded ({len(interaction_records)} items).")

        return interaction_records

    def save_best_parses(self):
        self.best_parses["timestamp"] = str(uuid.uuid4())
        if self.best_parses_file is not None:
            with open(self.best_parses_file, "w") as json_file:
                json_file.write(json.dumps(self.best_parses, indent=True))

    # If a phrase is an implicit or explicit conjunction, interact_once will treat it like different sentences and only
    # evaluate one at a time. It can be called again with conjunct_mrs_index, conjunct_tree_index, and next_conjuncts set
    # to evaluate the non default conjuncts
    def _interact_once(self, force_input, conjunct_mrs_index=None, conjunct_tree_index=None, next_conjuncts=None):
        if conjunct_mrs_index is not None:
            pipeline_logger.debug(f"Interact Once: force_input='{force_input}', conjunct_mrs_index={conjunct_mrs_index}, conjunct_tree_index={conjunct_tree_index}, next_conjuncts={next_conjuncts}")

        assert force_input is not None

        # At this point on we are processing a phrase

        # If we have recorded a particular MRS that is normally the best, move it
        # to the front. If this is a conjunct, we have already settled on the MRS so don't bother
        # Use 10000 to mean "get all parses". That should cover most phrases
        current_max_parses = (conjunct_mrs_index + 1) if conjunct_mrs_index is not None else None
        current_max_parses = 10000 if self.generate_all_parses else current_max_parses
        mrs_generator = CachedIterable(self.mrs_parser.mrss_from_phrase(force_input, synonyms=self.vocabulary.synonyms, one_time_max_parses=current_max_parses))
        if not conjunct_mrs_index and mrs_generator.at_least_one():
            best_parse_index_simple_mrs = simplemrs.dumps([mrs_generator[0]], lnk=False)
            best_parse_index = self.best_parses.get(best_parse_index_simple_mrs, {"Phrase": "none", "MRSIndex": 0})["MRSIndex"]
            if best_parse_index > 0:
                all_parses = None
                target_parse = None
                while target_parse is None:
                    target_parse = mrs_generator.get_from_index(best_parse_index, raise_if_none=False)
                    if target_parse is None:
                        if all_parses is None:
                            # We don't get all parses the first time through for performance reasons, try again but with all of them
                            all_parses = CachedIterable(self.mrs_parser.mrss_from_phrase(force_input, synonyms=self.vocabulary.synonyms,
                                                           one_time_max_parses=best_parse_index + 1))
                            mrs_generator = all_parses

                        else:
                            break

                    else:
                        break

                try:
                    if target_parse:
                        # Move the best MRS to be first and remove it from its previous position
                        mrs_generator.cached_values.insert(0, target_parse)
                        mrs_generator.cached_values.pop(best_parse_index + 1)
                        pipeline_logger.debug(f"Starting with best parse MRS: {best_parse_index}")

                except StopIteration:
                    # The best parse doesn't exist anymore, clear this out
                    self.best_parses.pop(best_parse_index_simple_mrs)
                    self.save_best_parses()

        # Loop through each MRS and each tree that can be
        # generated from it...
        mrs_index = -1
        tree_index = -1
        mrs_record = None
        for mrs in mrs_generator:
            mrs_index += 1
            if self.run_mrs_index is not None and self.run_mrs_index != mrs_index:
                mrs_record = self.new_mrs_record(mrs=mrs)
                self.interaction_record["Mrss"].append(mrs_record)
                continue

            if conjunct_mrs_index is not None and conjunct_mrs_index != mrs_index:
                continue

            unknown, contingent = self.unknown_words(mrs, self.state)
            mrs_record = self.new_mrs_record(mrs=mrs, unknown_words=unknown)
            self.interaction_record["Mrss"].append(mrs_record)

            tree_index = -1
            if self.has_timed_out():
                break

            if len(mrs_record["UnknownWords"]) > 0:
                unknown_words_error = ExecutionContext.blank_error(predication_index=0, error=["unknownWords", mrs_record["UnknownWords"]])
                tree_record = TreeSolver.new_error_tree_record(error=unknown_words_error,
                                                               response_generator=self.response_function(self.state, self.vocabulary, self.message_function, None, [], unknown_words_error),
                                                               tree_index=0)
                mrs_record["Interpretations"].append(tree_record)
                self.evaluate_best_response(has_solution_group=False)

            else:
                # Loop through all the "official" DELPH-IN trees using the official predications
                tree_generated = False
                try:
                    for tree_orig in self.mrs_parser.trees_from_mrs(mrs):
                        if self.has_timed_out():
                            break

                        heads = [x for x in syntactic_heads_characteristic_variables(mrs)]
                        tree_generated = True
                        tree_info_orig = {"Index": mrs.index,
                                          "SyntacticHeads": heads,
                                          "Variables": mrs.variables,
                                          "Tree": tree_orig,
                                          "MRS": self.mrs_parser.mrs_to_string(mrs)}

                        # Now loop through any tree modifications that have been built for this application
                        for tree_info in self.vocabulary.alternate_trees(self.state, tree_info_orig, len(contingent) == 0, conjunct_index_list=next_conjuncts):
                            if self.has_timed_out():
                                break

                            # At this point we have locked down which predications should be used and that won't change
                            # However: there might be multiple interpretations of these predications as well as disjunctions
                            # that cause various solution sets to be created. Each will be in its own tree_record
                            tree_index += 1
                            target_tree_index = conjunct_tree_index if conjunct_tree_index is not None else self.run_tree_index
                            if target_tree_index is not None:
                                if tree_index < target_tree_index:
                                    error_text = f"MRS #{mrs_index}, Tree #{tree_index}: Skipping"
                                    tree_record = TreeSolver.new_tree_record(tree=tree_info["Tree"], tree_index=tree_index, error=error_text)
                                    mrs_record["Interpretations"].append(tree_record)
                                    pipeline_logger.debug(error_text)
                                    continue

                                elif tree_index > target_tree_index:
                                    pipeline_logger.debug(f"MRS #{mrs_index}, Tree #{tree_index}: Skipping all trees beyond index #{tree_index}")
                                    break

                            # Make sure the contingent words were removed by a transformer
                            if len(contingent) > 0:
                                if tree_contains_predication(tree_info["Tree"], [x[0] for x in contingent]):
                                    # It is still there, fail this tree
                                    error_text = f"MRS #{mrs_index}, Tree #{tree_index}: One or more of these words not transformed out of tree: {[x[0] for x in contingent]}"
                                    tree_record = TreeSolver.new_tree_record(tree=tree_info["Tree"], tree_index=tree_index, error=error_text)
                                    mrs_record["Interpretations"].append(tree_record)
                                    pipeline_logger.debug(error_text)
                                    continue

                            pipeline_logger.debug(f"MRS #{mrs_index}, Tree #{tree_index}: {tree_info['Tree']}")

                            # Try the state from each frame that is available
                            # Used to loop through different frames, for now this is turned off
                            # until we decide if is necessary again since it is expensive
                            # was: for frame_state in self.state.frames():
                            wh_phrase_variable = perplexity.tree.get_wh_question_variable(tree_info)
                            for frame_state in [self.state]:
                                if self.has_timed_out():
                                    break

                                pipeline_logger.debug(f"Evaluating against frame '{frame_state.frame_name}'")

                                tree_solver = TreeSolver.create_top_level_solver(self.vocabulary, self.scope_function, self.scope_init_function)
                                for tree_record in tree_solver.tree_solutions(frame_state,
                                                                              tree_info,
                                                                              self.response_function,
                                                                              self.message_function,
                                                                              current_tree_index=tree_index,
                                                                              target_tree_index=conjunct_tree_index if conjunct_tree_index is not None else self.run_tree_index,
                                                                              find_all_solution_groups=self.show_all_answers,
                                                                              wh_phrase_variable=wh_phrase_variable,
                                                                              start_time=self.interaction_record["StartTime"],
                                                                              timeout=self.timeout):
                                    mrs_record["Interpretations"].append(tree_record)

                                    solution_group_generator = tree_record["SolutionGroupGenerator"]
                                    if solution_group_generator is not None:
                                        # There were solutions, so this is our answer.
                                        # Return it and stop looking
                                        self.evaluate_best_response(has_solution_group=True)

                                        # If it was not the first MRS parse (and it isn't a conjunct), record it as the best alternative so that we start there next time
                                        if not conjunct_mrs_index and mrs_index != 0:
                                            self.best_parses[best_parse_index_simple_mrs] = {"Phrase": force_input,
                                                                                             "MRSIndex": mrs_index}
                                            self.save_best_parses()

                                        # Go through all the responses in this solution group
                                        had_operations = False
                                        response, solution_group = next(tree_record["ResponseGenerator"])

                                        # Because this worked, we need to apply any Operations that were added to
                                        # any solution to the current world state.
                                        try:
                                            has_more_func = solution_group_generator.has_at_least_one_more

                                            def unique_wh_values_from_group(group):
                                                unique_wh_values = set()
                                                for solution in group:
                                                    unique_wh_values.add(solution.get_binding(wh_phrase_variable).value)

                                                return unique_wh_values

                                            # when the solution group is a wh_question, we only care if the wh variable
                                            # is different in the different solution groups
                                            def wh_aware_has_more():
                                                if wh_phrase_variable is None:
                                                    return solution_group_generator.has_at_least_one_more()

                                                else:
                                                    original_values = unique_wh_values_from_group(solution_group)
                                                    for next_solution_group in solution_group_generator:
                                                        maximal_group = next_solution_group.maximal_group_iterator()
                                                        next_original_values = unique_wh_values_from_group(maximal_group)
                                                        if next_original_values != original_values:
                                                            return True

                                                    return False

                                            solution_group_solutions = [solution for solution in solution_group]
                                            operation_responses, last_phrase_responses, new_state = apply_solutions_to_state(self.state, wh_aware_has_more, solution_group_solutions)
                                            self.state = new_state

                                            # Now deal with any resets that have been registered
                                            did_reset = False
                                            new_world_responses = []
                                            for solution in solution_group_solutions:
                                                for operation in solution.get_operations():
                                                    if isinstance(operation, ResetOperation):
                                                        self.state = self.reset()
                                                        did_reset = True
                                                        break

                                                    if isinstance(operation, LoadWorldOperation):
                                                        # World changed, load the new world
                                                        new_ui = ui_from_world_name(operation.world_name)
                                                        if new_ui is None:
                                                            print(f"World {operation.world_name} is not registered as a world")

                                                        else:
                                                            # Don't lose any recording that has happened
                                                            new_ui.records = self.records
                                                            self.new_ui = new_ui
                                                            tree_record["NewWorldCreated"] = True
                                                            tree_record["NewWorldName"] = new_ui.world_name
                                                            if self.new_ui.events is not None:
                                                                new_world_responses = self.new_ui.events.world_new()

                                                            did_reset = True
                                                            break

                                                if did_reset:
                                                    break

                                        except MessageException as error:
                                            response = self.response_function(self.state, self.vocabulary, self.message_function, tree_info, [], [0, error.message_object()])
                                            tree_record["ResponseMessage"] += f"\n{str(response)}"
                                            operation_responses = []
                                            last_phrase_responses = []
                                            new_world_responses = []

                                        if len(operation_responses) > 0:
                                            response = self.output_sorted_responses(operation_responses)

                                        elif response is None and len(last_phrase_responses) == 0:
                                            # No message was provided, give a default one
                                            this_sentence_force = sentence_force(tree_info["Variables"])
                                            if this_sentence_force == "comm":
                                                # Only give a "Done!" message if it was a command and there were no responses given
                                                response = "Done!"

                                            elif this_sentence_force == "prop" or this_sentence_force == "prop-or-ques":
                                                response = "Yes, that is true."

                                            else:
                                                response = "(no response)"

                                        if len(operation_responses) == 0:
                                            # Only shown if the developer didn't provide a custom message
                                            more_message = self.generate_more_message(tree_info, solution_group_generator)
                                            if more_message is not None:
                                                response += "\n" + more_message

                                        tree_record["ResponseMessage"] += response if response is not None else ""

                                        # These only get shown if this is the last phrase in the whole user utterance (which could be multiple
                                        # phrases), thus it is stored and not output right now
                                        if len(last_phrase_responses) > 0:
                                            tree_record["LastPhraseResponse"] = self.output_sorted_responses(last_phrase_responses)

                                        # Show any responses from the new world after *all* the previous world responses
                                        # thus it is stored and not output right now
                                        if len(new_world_responses) > 0:
                                            tree_record["NewWorldResponse"] = self.output_sorted_responses(new_world_responses)

                                        if not self.run_all_parses:
                                            return

                                    else:
                                        # This failed, remember it if it is the "best" failure
                                        # which we currently define as the first one
                                        self.evaluate_best_response(has_solution_group=False)

                                    if self.has_timed_out():
                                        break

                        alternate_tree_generated = tree_index > -1
                        if len(contingent) > 0 and not alternate_tree_generated:
                            unknown_words_error = ExecutionContext.blank_error(predication_index=0, error=["unknownWords", contingent])
                            tree_record = TreeSolver.new_error_tree_record(error=unknown_words_error,
                                                                           response_generator=self.response_function(self.state, self.vocabulary, self.message_function, None, [], unknown_words_error),
                                                                           tree_index=tree_index)
                            mrs_record["Interpretations"].append(tree_record)
                            self.evaluate_best_response(has_solution_group=False)

                except TooComplicatedError:
                    too_complicated_error = ExecutionContext.blank_error(predication_index=0, error=["tooComplicated"])
                    tree_record = TreeSolver.new_error_tree_record(error=too_complicated_error,
                                                                   response_generator=self.response_function(self.state, self.vocabulary,
                                                                                                             self.message_function, None, [],
                                                                                                             too_complicated_error),
                                                                   tree_index=tree_index)
                    mrs_record["Interpretations"].append(tree_record)
                    self.evaluate_best_response(has_solution_group=False)

        # If we got here, nothing worked: print out the best failure
        chosen_record = self.chosen_interpretation_record()
        if chosen_record is None:
            error = ["tooComplicatedTimeout"] if self.has_timed_out() else ["noParse"]
            no_chosen_record_error = ExecutionContext.blank_error(predication_index=0, error=error)
            tree_record = TreeSolver.new_error_tree_record(error=no_chosen_record_error,
                                                           response_generator=self.response_function(self.state, self.vocabulary,
                                                                                                     self.message_function,
                                                                                                     None, [],
                                                                                                     no_chosen_record_error),
                                                           tree_index=tree_index)
            if mrs_record is None:
                mrs_record = self.new_mrs_record()
                self.interaction_record["Mrss"].append(mrs_record)

            mrs_record["Interpretations"].append(tree_record)
            self.evaluate_best_response(has_solution_group=False)
            chosen_record = self.chosen_interpretation_record()

        if isinstance(chosen_record["ResponseGenerator"], list) and len(chosen_record["ResponseGenerator"]) == 0:
            response = None
        else:
            response, _ = next(chosen_record["ResponseGenerator"])

        if response is None:
            response = "(no error specified)"
        chosen_record["ResponseMessage"] += response

    def generate_more_message(self, tree, solution_groups):
        if solution_groups is None:
            return

        else:
            try:
                if next(solution_groups):
                    return "(there are more)"

            except StopIteration:
                pass

    # WORKAROUND: ERG doesn't properly quote all strings with "/" so convert to "\"
    def convert_slashes_until(self, stop_char, start_index, phrase):
        new_phrase = ""
        index = start_index
        found_stop_char = False
        while index < len(phrase):
            test_char = phrase[index]
            index += 1

            if test_char == "/":
                new_phrase += "\\>"
            elif test_char == stop_char:
                found_stop_char = True
                break
            else:
                new_phrase += test_char

        if new_phrase.strip() == "\\>":
            new_phrase = "\\>root111"

        return index, new_phrase + (stop_char if found_stop_char else "")

    def autocorrect(self, phrase):
        final_phrase = ""
        index = 0
        while index < len(phrase):
            final_phrase += phrase[index]
            if phrase[index] in ["'", "\""]:
                index, new_phrase = self.convert_slashes_until(phrase[index], index + 1, phrase)
                final_phrase += new_phrase
            else:
                index += 1

        return autocorrect(self.autocorrect_file, final_phrase)

    def evaluate_best_response(self, has_solution_group):
        current_mrs_index = len(self.interaction_record["Mrss"]) - 1
        current_interpretation_index = len(self.interaction_record["Mrss"][current_mrs_index]["Interpretations"]) - 1
        tree_record = self.interaction_record["Mrss"][current_mrs_index]["Interpretations"][current_interpretation_index]
        chosen_record = self.chosen_interpretation_record()
        chosen_error = chosen_record["Error"] if chosen_record is not None else None
        # If there was a success, return it as the best answer
        if has_solution_group or \
                (self.error_priority_function(tree_record["Error"]) > self.error_priority_function(chosen_error)):
            self.interaction_record["ChosenMrsIndex"] = current_mrs_index
            self.interaction_record["ChosenInterpretationIndex"] = current_interpretation_index
            pipeline_logger.debug(f"Recording best answer: MRSIndex {current_mrs_index}, TreeIndex: {current_interpretation_index}, Error: {tree_record['Error'] if not has_solution_group is None else 'none'}")

    # Commands always start with "/", followed by a string of characters and then
    # a space. Any arguments are after the space and their format is command specific.
    # For example:
    #   /show all
    # If it returns:
    # True: Command was handled and should not be recorded
    # None: Was not a command
    # Str: The string that should be recorded for the command
    def handle_command(self, text):
        try:
            text = text.strip()
            if len(text) > 0:
                if text[0] == "/":
                    text = text[1:]
                    items = text.split()
                    if len(items) > 0:
                        command = items[0].strip().lower()
                        command_info = command_data.get(command, None)
                        if command_info is not None:
                            return command_info["Function"](self, " ".join(text.split()[1:]))

                        else:
                            self.user_output("Don't know that command ...")
                            return True

        except Exception as error:
            self.user_output(str(error))
            return True

        return None

    def print_diagnostics(self, all, first_tree_only):
        if self.interaction_record is not None:
            self.user_output(f"User Input: {self.interaction_record['UserInput']}")
            self.user_output(f"{len(self.interaction_record['Mrss'])} Parses")

            for mrs_index in range(0, len(self.interaction_record["Mrss"])):
                if all or self.interaction_record["ChosenMrsIndex"] is None or mrs_index == self.interaction_record["ChosenMrsIndex"]:
                    extra = "CHOSEN " if mrs_index == self.interaction_record["ChosenMrsIndex"] else ""
                    self.user_output(f"\n***** {extra}Parse #{mrs_index}:")
                    mrs_record = self.interaction_record["Mrss"][mrs_index]
                    mrs = mrs_record['Mrs']
                    self.user_output(f"Sentence Force: {sentence_force(mrs.variables)}")
                    self.user_output(simplemrs.encode(mrs, indent=True))

                    if all:
                        chosen_tree = None
                    else:
                        chosen_tree = self.interaction_record["ChosenInterpretationIndex"]

                    self.print_diagnostics_trees(all, mrs_index, chosen_tree, mrs_record, first_tree_only)

    def print_diagnostics_trees(self, all, parse_number, chosen_tree, mrs_record, first_tree_only):
        is_ungenerated_tree = len(mrs_record["Interpretations"]) == 1 and mrs_record["Mrs"] is not None and "ErrorTree" in mrs_record["Interpretations"][0]
        if is_ungenerated_tree:
            # The trees aren't generated if we don't know terms for performance
            # reasons (since we won't be evaluating anything)
            tree_generator = []
            for tree in self.mrs_parser.trees_from_mrs(mrs_record["Mrs"]):
                tree_generator.append(TreeSolver.new_tree_record(tree=tree,
                                                                 error=mrs_record["Interpretations"][0]["Error"],
                                                                 response_generator=mrs_record["Interpretations"][0]["ResponseGenerator"],
                                                                 response_message=mrs_record["Interpretations"][0]["ResponseMessage"]))

        else:
            tree_generator = mrs_record["Interpretations"]

        tree_index = 0
        for tree_info in tree_generator:
            if first_tree_only and tree_index > 0:
                return

            if all or chosen_tree == tree_index:
                extra = "CHOSEN " if chosen_tree == tree_index else ""
                self.user_output(f"\n-- {extra}Parse #{parse_number}, {extra}Tree #{tree_index}: \n")
                draw_tree = create_draw_tree(mrs_record["Mrs"], tree_info["Tree"])
                renderer = TreeRenderer()
                renderer.print_tree(draw_tree)
                self.user_output(f"\nText Tree: {tree_info['Tree']}")
                self.user_output(f"\nInterpretation: {tree_info['Interpretation']}")
                if tree_info['SolutionGroups'] is not None:
                    for solution_group in tree_info['SolutionGroups']:
                        self.user_output(f"\nSolution group:")
                        for solution in solution_group:
                            self.user_output(f"{str(solution)}")
                    self.user_output()

                else:
                    self.user_output(f"Error: {tree_info['Error']}")

                if tree_info['ResponseMessage'] == "" and tree_info['ResponseGenerator'] is not None:
                    tree_info['ResponseMessage'] = ""
                    for response in tree_info['ResponseGenerator']:
                        tree_info['ResponseMessage'] += str(response)
                self.user_output(f"Response:\n{tree_info['ResponseMessage']}")

            tree_index += 1

    def unknown_words(self, mrs, state):
        unknown_words = []
        contingent_words = []
        phrase_type = sentence_force(mrs.variables)
        for predication in mrs.predications:
            argument_types = []
            for argument_item in predication.args.items():
                if argument_item[0] == "CARG":
                    argument_types.append("c")
                else:
                    argument_types.append(argument_item[1][0])

            if self.vocabulary.unknown_word(state, predication.predicate, argument_types, phrase_type):
                # BUT: if a transformer might remove it, return it as "contingent" so we can see if it did
                tree_predication = TreePredication(0, predication.predicate, list(predication.args.values()), arg_names=list(predication.args.keys()), mrs_predication=predication)
                if self.vocabulary.is_potentially_removed(tree_predication):
                    contingent_words.append((predication.predicate,
                                          argument_types,
                                          phrase_type,
                                          # Record if at least one form is understood for
                                          # better error messages
                                          self.vocabulary.version_exists(predication.predicate),
                                          surface_word_from_mrs_predication(mrs, predication)))

                else:
                    # If there aren't any implementations for this predication, or they are all match_all and don't implement it...
                    # This predication is not implemented
                    unknown_words.append((predication.predicate,
                                          argument_types,
                                          phrase_type,
                                          # Record if at least one form is understood for
                                          # better error messages
                                          self.vocabulary.version_exists(predication.predicate),
                                          surface_word_from_mrs_predication(mrs, predication)))

        if len(unknown_words) > 0:
            pipeline_logger.debug(f"Unknown predications: {unknown_words}")

        return unknown_words, contingent_words


def command_run_all_parses(ui, arg):
    turn_on = bool(arg) if len(arg) > 0 else True
    ui.user_output(f"Run all parses is now {turn_on}")
    ui.run_all_parses = turn_on
    return True


def convert_bool(value):
    convert = {"1": True,
               "0": False,
               "true": True,
               "false": False}
    return convert.get(value.lower(), "False")

def command_generate_all_parses(ui, arg):
    turn_on = convert_bool(arg) if len(arg) > 0 else True
    ui.user_output(f"Generate all parses is now {turn_on}")
    ui.generate_all_parses = turn_on
    return True


def command_show(ui, arg):
    parts = arg.split(",")
    all = False
    first_tree_only = False

    if len(parts) >= 1:
        all = parts[0].lower() == "all"

    if len(parts) >= 2:
        first_tree_only = convert_bool(parts[1])

    if len(parts) >= 3:
        ui.user_output("Don't know that argument set")
        return True

    ui.print_diagnostics(all, first_tree_only)
    return True


def command_repeat_system_command(ui, arg):
    repeat_phrase = ui.test_manager.get_session_data("last_system_command")
    if repeat_phrase is not None:
        ui.user_input = repeat_phrase
        ui.user_output(f"Repeat: {repeat_phrase}")
        return ui.handle_command(repeat_phrase)

    else:
        ui.user_output("No last command to repeat")

    return None


def command_repeat(ui, arg):
    repeat_phrase = ui.test_manager.get_session_data("last_phrase")
    if repeat_phrase is not None:
        ui.user_output(f"Repeat: {repeat_phrase}")
        ui.user_input = repeat_phrase

    else:
        ui.user_output("No last command to repeat")

    return None


def command_record_test(ui, arg):
    turn_on = bool(arg) if len(arg) > 0 else True
    ui.records = [] if turn_on else None
    ui.user_output(f"Recording is now {turn_on}")
    return True


def command_create_test(ui, arg):
    if len(arg) == 0:
        ui.user_output(f"Please supply a test name.")

    else:
        ui.test_manager.create_test(ui, arg, ui.records)
        ui.records = None
        ui.user_output(f"Recording is now off")

    return True


def command_append_test(ui, arg):
    if len(arg) == 0:
        ui.user_output(f"Please supply a test name.")

    else:
        ui.test_manager.append_test(arg, ui.records)
        ui.records = None
        ui.user_output(f"Recording is now off")

    return True


def command_run_test(ui, arg):
    if len(arg) == 0:
        ui.user_output(f"Please supply a test name.")

    else:
        # Remember that we ran a single test not a folder
        ui.test_manager.record_session_data("LastTestFolder", "")
        test_iterator = TestIterator(ui.test_manager, ui.test_manager.full_test_path(arg + ".tst"))
        ui.test_manager.run_tests(test_iterator, ui)

        # Set the test world state as the new word state if we are just running a single test
        if ui.test_manager.final_ui is not None:
            ui.new_ui = ui.test_manager.final_ui

    return True


def StringBooleanToBoolean(value):
    return value.lower() in ['true', '1', 't', 'y', 'yes']


def command_log_tests(ui, arg):
    if len(arg) == 0:
        value = not ui.log_tests
    else:
        value = StringBooleanToBoolean(arg)
    ui.log_tests = value
    ui.user_output("Log Test Results is now {}".format(value))
    return True


def command_resolve_tests(ui, arg):
    ui.test_manager.resolve_tests()
    return True


def command_soln(ui, arg):
    if len(arg) == 0:
        ui.show_all_answers = not ui.show_all_answers
    else:
        ui.show_all_answers = arg.strip().lower() == "all"

    ui.user_output(f"Show all solutions is now: {ui.show_all_answers}")

    return True


def command_run_parse(ui, arg):
    if arg.strip() == '':
        ui.run_mrs_index = None
        ui.run_tree_index = None
        ui.user_output("Runparse is off")
        return True

    parts = arg.split(",")

    ui.run_mrs_index = int(parts[0])
    if len(parts) == 2:
        ui.run_tree_index = int(parts[1])

    return True


def command_run_folder(ui, arg):
    ui.test_manager.record_session_data("LastTestFolder", arg)
    test_iterator = TestFolderIterator(ui.test_manager, arg)
    ui.test_manager.run_tests(test_iterator, ui)

    return True


def command_resume_test(ui, arg):
    test_folder = ui.test_manager.get_session_data("LastTestFolder")
    if test_folder is None:
        ui.user_output(f"Nothing to resume.")
        return True

    else:
        if test_folder == "":
            test_name = ui.test_manager.get_session_data("LastTest")
            if test_name is None:
                ui.user_output("No test to resume.")
                return True

            else:
                ui.user_output(f"**** Resuming test: {test_name}")
                test_iterator = TestIterator(ui.test_manager, test_name, resume=True)

        else:
            ui.user_output(f"**** Resuming test folder: {test_folder}")
            test_iterator = TestFolderIterator(ui.test_manager, test_folder, resume=True)

        ui.test_manager.run_tests(test_iterator, ui)
        return True


def command_reset(ui, arg):
    ui.state = ui.reset()
    return f"State reset using {module_name(ui.reset)}.{ui.reset.__name__}()."


def command_new(ui, arg):
    arg_parts = arg.split(".")
    if len(arg_parts) < 2:
        ui.user_output("reset function must be in the form: module_name.function_name")
        return True

    ui.reset = import_function_from_names(".".join(arg_parts[0:-1]), arg_parts[-1])
    return command_reset(ui, arg)


def command_save(ui, arg):
    if arg is None or arg == "":
        path = GetStateDirectoryName("default")
        if not os.path.exists(path):
            os.makedirs(path)
        arg = os.path.join(path, "state.p8y")
    ui.save(arg)
    ui.user_output(f"World saved at: {arg}")
    return True


def command_load(ui, arg):
    if arg is None or arg == "":
        path = GetStateDirectoryName("default")
        arg = os.path.join(path, "state.p8y")
        if not os.path.exists(arg):
            ui.user_output("There is no saved state")

    ui.new_ui = load_ui(arg)
    ui.user_output(f"World loaded from: {arg}")
    return True


def command_timeout(ui, arg):
    if arg is None or arg == "":
        ui.timeout = 9999
    else:
        ui.timeout = int(arg)

    ui.user_output(f"Timeout is now: {ui.timeout}")
    return True


def command_help(ui, arg):
    helpText = "\nCommands start with /:\n"

    category = None
    for descKey in command_data.keys():
        if command_data[descKey]["Category"] != category:
            category = command_data[descKey]["Category"]
            helpText += f"\n****** {category} ******\n"

        helpText += "/" + descKey + " " + command_data[descKey]["Description"] + " -> e.g. " + command_data[descKey]["Example"] + "\n"
    ui.user_output(helpText)
    return True


def command_debug_tree(ui, arg):
    predication_name = None
    if arg != "":
        parts = arg.split("(")
        predication_name = parts[0]
        arg_parts = parts[1].split(",")
        arg_parts[-1] = arg_parts[-1].strip(")")

        predication_args = []
        for part in arg_parts:
            clean_arg = part.strip()
            if clean_arg in ["_", "None", "none", ""]:
                predication_args.append("_")
            else:
                predication_args.append(clean_arg)

        ui.user_output(f"searching for trees containing predication: {predication_name}({','.join(predication_args)})\n")

    if ui.interaction_record is not None:
        for mrs_index in range(0, len(ui.interaction_record["Mrss"])):
            mrs_record = ui.interaction_record["Mrss"][mrs_index]

            if len(mrs_record["Interpretations"]) == 1 and mrs_record["Interpretations"][0]["Tree"] is None:
                # The trees aren't generated if we don't know terms for performance
                # reasons (since we won't be evaluating anything)
                tree_generator = [{"Tree": tree,
                                   "Solutions": [],
                                   "Error": None,
                                   "ResponseMessage": None} for tree in ui.mrs_parser.trees_from_mrs(mrs_record["Mrs"])]
            else:
                tree_generator = mrs_record["Interpretations"]

            for tree_info in tree_generator:
                if predication_name is not None:
                    if len(find_predications_with_arg_types(tree_info["Tree"], predication_name, predication_args)):
                        ui.user_output(f"Found in parse #{mrs_index}:\n")
                        draw_tree = create_draw_tree(mrs_record["Mrs"], tree_info["Tree"])
                        renderer = TreeRenderer()
                        renderer.print_tree(draw_tree)
                        ui.user_output(f"\nText Tree: {tree_info['Tree']}\n")

                    break
                else:
                    ui.user_output(f"QUOTED: {str(find_predications(tree_info['Tree'], 'quoted'))}")

    return True


def command_debug_mrs(ui, arg):
    if ui.interaction_record is not None:
        for mrs_index in range(0, len(ui.interaction_record["Mrss"])):
            found = []
            mrs_record = ui.interaction_record["Mrss"][mrs_index]
            for predication in mrs_record["Mrs"].predications:
                if predication.predicate == "quoted" or predication.predicate == "fw_seq":
                    found.append(predication)

            ui.user_output(found)

    return True


# Prints any MRS that matches the criteria, which is a comma separated list of predications.
# - If the same predication appears twice, there must be two of them
# _for_x_cause -> match that name with any arguments
# _for_x_cause(x,h,h)   -> match that name with those exact arguments
# _for_x_cause(e,x,_,h) -> match that name with hose arguments, but arg 3 can be anything (but must exist)
# _for_x_cause(e,x,*,h) -> match that name with those arguments, but arg 3 can be anything (and can be missing, i.e. only 3 arguments)
# *(x, h, h)            -> match any name with those arguments
def command_find_mrs(ui, arg):
    # First parse the string into TransformerMatch objects
    predication_patterns = []
    parts = arg.split("(")
    index = 0
    if len(parts) < 2:
        print("use /help for instructions on how to use")
        return True

    # parts = ['a', 'b, c), d', ... ]
    while index < len(parts):
        arg_parts = parts[index + 1].split(")")
        predication_string = f"{parts[index]}({arg_parts[0]})"
        next_name = arg_parts[1].strip(", ")
        if len(next_name) > 0:
            parts.insert(index + 2, next_name)
        index += 2
        predication_patterns.append(TransformerMatch.from_string_definition(predication_string))

    print("Searching ...")

    # Then search all the MRS
    found = False
    if ui.interaction_record is not None:
        for mrs_index in range(0, len(ui.interaction_record["Mrss"])):
            mrs_predications = []
            unmatched_predications = []
            mrs_record = ui.interaction_record["Mrss"][mrs_index]["Mrs"]
            remaining_patterns = copy.deepcopy(predication_patterns)
            for ep in mrs_record.rels:
                predication = TreePredication.from_ep(ep)
                mrs_predications.append(predication)
                for pattern in remaining_patterns:
                    if pattern.match(predication, {}, {}):
                        remaining_patterns.remove(pattern)
                        predication = None
                        break
                if predication is not None:
                    unmatched_predications.append(predication)

            if len(remaining_patterns) == 0:
                # Match!
                found = True
                pipeline_logger.debug(f"Match Parse {mrs_index}: {', '.join([str(x) for x in mrs_predications])}\n      unmatched: {', '.join([str(x) for x in unmatched_predications])}")

    if not found:
        print("None found.")

    return True


logger = logging.getLogger('UserInterface')
pipeline_logger = logging.getLogger('Pipeline')
command_data = {
    "help": {"Function": command_help, "Category": "General",
             "Description": "Get list of commands", "Example": "/help"},
    "r": {"Function": command_repeat, "Category": "General",
            "Description": "Repeat the last phrase",
            "Example": "/r"},
    "s": {"Function": command_repeat_system_command, "Category": "General",
            "Description": "Repeat the last system command (i.e. the /command)",
            "Example": "/s"},
    "new": {"Function": command_new, "Category": "General",
            "Description": "Calls the passed function to get the new state to use",
            "Example": "/new examples.Example18_reset"},
    "reset": {"Function": command_reset, "Category": "General",
              "Description": "Resets to the initial state",
              "Example": "/reset"},
    "save": {"Function": command_save, "Category": "General",
              "Description": "Saves the current world state to the ./data/default directory. If given a path, saves to that path instead.",
              "Example": "/save"},
    "load": {"Function": command_load, "Category": "General",
             "Description": "Loads the current world state from the ./data/default directory. If given a path, loads from that path instead.",
             "Example": "/load"},
    "timeout": {"Function": command_timeout, "Category": "General",
                "Description": "Sets timeout time for a given phrase",
                "Example": "/timeout or /timeout 20"},
    "show": {"Function": command_show, "Category": "Parsing",
             "Description": "Shows tracing information from last command. Add 'all' to see all interpretations, 1 to see only first trees",
             "Example": "/show or /show all or /show all, 1"},
    "soln": {"Function": command_soln, "Category": "Parsing",
             "Description": "Retrieves all solutions when parsing so they can be shown with /show. Add 'all' to see all solutions, anything else toggles the current setting",
             "Example": "/soln or /soln all"},
    "genall": {"Function": command_generate_all_parses, "Category": "Parsing",
                  "Description": "Generates all parses (normally only the first 5 are generated)",
                  "Example": "/genall 1 OR /genall True"},
    "runall": {"Function": command_run_all_parses, "Category": "Parsing",
                  "Description": "Runs all parses, doesn't stop after success",
                  "Example": "/runall 1 OR /runall True"},
    "runparse": {"Function": command_run_parse, "Category": "Parsing",
                  "Description": "Only runs the identified parse index and optional tree index. Pass no arguments to turn off",
                  "Example": "/runparse 1 OR /runparse 1, 0"},
    "debugtree": {"Function": command_debug_tree, "Category": "Parsing",
                  "Description": "Shows tracing information about the tree. give a predication query after to only show trees that match it. Use '_' to mean 'anything' for an argument or the predication name",
                  "Example": "/debugtree OR /debugtree which(x,h,h) OR /debugtree _(e,x,_,h)"},
    "debugmrs": {"Function": command_debug_mrs, "Category": "Parsing",
                  "Description": "Shows tracing information about the mrs",
                  "Example": "/debugmrs"},
    "findmrs": {"Function": command_find_mrs, "Category": "Parsing",
                 "Description": "?",
                 "Example": "/findmrs"},

    "recordtest": {"Function": command_record_test, "Category": "Testing",
                   "Description": "Starts recording a test. Finish with /createtest or /appendtest", "Example": "/record"},
    "createtest": {"Function": command_create_test, "Category": "Testing",
                   "Description": "Creates a test using name you specify based on the interactions recorded by /record",
                   "Example": "/createtest Foo"},
    "appendtest": {"Function": command_append_test, "Category": "Testing",
                   "Description": "Appends the interactions recorded by /record to an existing test",
                   "Example": "/appendtest Foo"},
    "runtest": {"Function": command_run_test, "Category": "Testing",
                "Description": "Runs a test",
                "Example": "/runtest subdirectory/foo"},
    "resolvetests": {"Function": command_resolve_tests, "Category": "Testing",
                "Description": "Resolves all the test results stored in 'testresults.txt'",
                "Example": "/resolvetests"},
    "logtests": {"Function": command_log_tests, "Category": "Testing",
                "Description": "Logs test results to the file 'testresults.txt'",
                "Example": "/logtests true"},
    "runfolder": {"Function": command_run_folder, "Category": "Testing", "WebSafe": False,
                  "Description": "Runs all tests in a directory",
                  "Example": "/runfolder foldername"},
    "resume": {"Function": command_resume_test, "Category": "Testing", "WebSafe": False,
                  "Description": "Resume running the last test (or sequence of tests in a folder) at the last reset before it was stopped",
                  "Example": "/resume"},

    }
