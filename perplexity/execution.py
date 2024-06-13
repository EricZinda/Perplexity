import logging
import queue
import sys
import perplexity.tree
import perplexity.solution_groups
from perplexity.set_utilities import product_stream
from perplexity.utilities import sentence_force, at_least_one_generator
import perplexity.vocabulary


# Allows code to throw an exception that should get converted
# to a user visible message
class MessageException(Exception):
    def __init__(self, message_name, message_args):
        self.message_name = message_name
        self.message_args = message_args

    def message_object(self):
        return [self.message_name] + self.message_args


def clear_error_when_yield_generator(context, generator):
    for next_value in generator:
        context.clear_error()
        yield next_value


# Generates all the solution groups that can produced by
# various interpretations of a tree.
# Each different interpretation results in a new tree_record
# even if it fails
class TreeSolver(object):
    def __init__(self, context):
        self._context = context

    @classmethod
    def create_top_level_solver(cls, vocabulary, scope_function, scope_init_function):
        context = ExecutionContext(vocabulary)
        context.set_in_scope_function(scope_function, scope_init_function)
        return cls(context)

    # This is the class that gets passed to predications as "context"
    # It is the lowest level class that walks a tree, in-order
    # and is consumed by the MRSLineage classes which break the solutions
    # into different solution sets
    class InterpretationSolver(object):
        def __init__(self, execution_context):
            self._context = execution_context
            self.vocabulary = self._context.vocabulary

            self._interpretation = None
            self._predication_index = -1
            self._predication = None
            self._phrase_type = None
            self.tree_info = None
            self._variable_metadata = None
            self._predication_runtime_settings = None
            self._lineage_failure_callback = None
            self._solution_lineages = None
            self._last_solution_lineage = None
            self._variable_execution_data = {}

        def interpretation(self):
            return self._interpretation

        def create_child_solver(self):
            # Subtrees are resolved using the same context so error state is shared
            return TreeSolver(self._context)

        # Overwrite the error reporting to default to phase=2
        def create_phase2_context(self):
            class InterpretationSolverPhase2:
                def __init__(self, proxied_object):
                    self.__proxied = proxied_object

                def __getattr__(self, attr):
                    def wrapped_method(*args, **kwargs):
                        result = getattr(self.__proxied, attr)(*args, **kwargs)
                        return result

                    if attr == "report_error_for_index":
                        return self.report_error_for_index
                    elif attr == "report_error":
                        return self.report_error
                    else:
                        return wrapped_method

                def report_error_for_index(self, predication_index, error, force=False, phase=None):
                    if phase is None:
                        return self.__proxied.report_error_for_index(predication_index, error, force, phase=2)
                    else:
                        return self.__proxied.report_error_for_index(predication_index, error, force, phase=phase)

                def report_error(self, error, force=False, phase=None):
                    if phase is None:
                        return self.__proxied.report_error(error, force, phase=2)
                    else:
                        return self.__proxied.report_error(error, force, phase=phase)

            return InterpretationSolverPhase2(self)

        # Walk the tree and compare any predication with property requirements to the tree_info
        # Fail if they don't match
        def tree_matches_interpretation_properties(self, tree_info, interpretation):
            def check_predication(predication):
                module_function = interpretation[predication.index]
                module = sys.modules[module_function.module]
                function = getattr(module, module_function.function)
                if hasattr(function, "_delphin_properties"):
                    properties_to_use = function._delphin_properties
                    if properties_to_use:
                        assert predication.arg_types[predication.introduced_variable_index()] == "e", f"verb '{function.__module__}.{function.__name__}' doesn't have an event as arg 0"
                        phrase_properties = {"SF": force}
                        phrase_properties.update(tree_info["Variables"][predication.args[predication.introduced_variable_index()]])
                        if perplexity.vocabulary.missing_properties(properties_to_use, phrase_properties):
                            self.report_error_for_index(predication.index, ["formNotUnderstood", function.__name__])
                            return False

            force = sentence_force(tree_info["Variables"])
            result = perplexity.tree.walk_tree_predications_until(tree_info["Tree"], check_predication)
            return result is not False

        # Returns solutions for a specific tree interpretation that is passed in
        def solve_tree_interpretation(self, state, tree_info, interpretation, lineage_failure_callback):
            self._interpretation = interpretation
            self._predication_index = 0
            self._predication = None
            self._phrase_type = sentence_force(tree_info["Variables"])
            self.tree_info = tree_info
            self._variable_metadata = perplexity.tree.gather_predication_metadata(self._context.vocabulary, tree_info, interpretation)
            self._predication_runtime_settings = {}
            self._lineage_failure_callback = lineage_failure_callback
            self._solution_lineages = set()
            self._last_solution_lineage = None
            self._variable_execution_data = {}

            self._context.reset_scope(state)
            self._context.clear_error()

            # See if we should run the tree at all
            if self.tree_matches_interpretation_properties(tree_info, interpretation):
                # Start out with an empty error context so that the first .call() records the right error
                self.clear_error()

                # Whenever there is a solution, this means there was not an error, by definition
                # So: clear it before we yield
                for solution in clear_error_when_yield_generator(self, self.call(state.set_x("tree", (tree_info,), False), tree_info["Tree"])):
                    # Remember any disjunction lineages that had a solution
                    tree_lineage_binding = solution.get_binding("tree_lineage")
                    if tree_lineage_binding.value is None:
                        self._solution_lineages.add(None)
                    else:
                        self._solution_lineages.add(tree_lineage_binding.value[0])

                    # Remember which interpretation generated this solution so that we can
                    # call the right solution group handler later
                    yield solution.set_x("interpretation", (interpretation, ))
            else:
                pipeline_logger.debug(f"Tree did not match interpretation properties for: {str(interpretation)}")

            # Fire an error for the last disjunction tree (which might be the whole tree if there were no disjunctions)
            # but only if no solutions were generated
            if self._last_solution_lineage is None and None not in self._solution_lineages:
                self._lineage_failure_callback(self._context.get_error_info())

            else:
                self._handle_lineage_change("")

            pipeline_logger.debug(f"Error after tree evaluation: {self._context.get_error_info()}")

        def in_scope(self, state, thing):
            return self._context.in_scope(state, thing)

        def has_not_understood_error(self):
            return self._context.has_not_understood_error()

        def report_error_for_index(self, predication_index, error, force=False, phase=0):
            return self._context.report_error_for_index(predication_index, error, force, phase=phase)

        def report_error(self, error, force=False, phase=0):
            self._context.report_error_for_index(self._predication_index, error, force, phase=phase)

        def error(self):
            return self._context.error()

        def get_error_info(self):
            return self._context.get_error_info()

        def set_error_info(self, error_info):
            return self._context.set_error_info(error_info)

        def clear_error(self):
            return self._context.clear_error()

        def set_disjunction(self):
            self.set_predication_runtime_settings("Disjunction", True)

        def set_predication_runtime_settings(self, key, value):
            self._predication_runtime_settings[key] = value

        def current_predication_index(self):
            return self._predication_index

        def current_predication(self):
            return self._predication

        def set_variable_execution_data(self, variable_name, key, value):
            if variable_name not in self._variable_execution_data:
                self._variable_execution_data[variable_name] = {}

            self._variable_execution_data[variable_name][key] = value

        def get_variable_execution_data(self, variable_name):
            return self._variable_execution_data.get(variable_name, {})

        def get_variable_metadata(self, variable_name):
            # TODO: This is a hack to enable metadata for eval(). Need to fix it
            return self._variable_metadata.get(variable_name, {"ValueSize": perplexity.vocabulary.ValueSize.all})

        def call(self, state, term):
            # See if the term is actually a list
            # If so, we have a conjunction
            if isinstance(term, list):
                # If "term" is an empty list, we have solved all
                # predications in the conjunction, return the final answer.
                # "len()" is a built-in Python function that returns the
                # length of a list
                if len(term) == 0:
                    yield state

                else:
                    # This is a list of predications, so they should be
                    # treated as a conjunction.
                    # Call each one and pass the state it returns
                    # to the next one, recursively
                    for nextState in self.call(state, term[0]):
                        # Note the [1:] syntax which means "return a list
                        # of everything but the first item"
                        yield from self.call(nextState, term[1:])

            else:
                # Keep track of how deep in the tree this
                # predication is
                last_predication_index = self._predication_index
                last_predication = self._predication
                self._predication_index = term.index
                self._predication = term

                # The first thing in the list was not a list
                # so we assume it is just a term like
                # ["_large_a_1", "e1", "x1"]
                # evaluate it using CallPredication
                yield from self._call_predication(state, term)

                # Restore it since we are recursing
                self._predication_index = last_predication_index
                self._predication = last_predication

        # Do not use directly.
        # Use Call() instead so that the predication index is set properly
        # The format we're using is:
        # ["folder_n_of", "x1"]
        #   The first item is the predication name
        #   The rest of the items are the arguments
        def _call_predication(self, state, predication):
            bindings = []
            for arg_index in range(0, len(predication.args)):
                if predication.arg_types[arg_index] in ["c", "h"]:
                    bindings.append(predication.args[arg_index])

                else:
                    bindings.append(state.get_binding(predication.args[arg_index]))

            # [list] + [list] will return a new, combined list
            # in Python. This is how we add the state object
            # onto the front of the argument list
            function_args = [self, state] + bindings

            # Look up the actual Python module and
            # function name given a string like "folder_n_of".
            # "vocabulary.Predication" returns a two-item list,
            # where item[0] is the module and item[1] is the function
            module_function = self._interpretation[predication.index]

            # sys.modules[] is a built-in Python list that allows you
            # to access actual Python Modules given a string name
            module = sys.modules[module_function.module]

            # Functions are modeled as properties of modules in Python
            # and getattr() allows you to retrieve a property.
            # So: this is how we get the "function pointer" to the
            # predication function we wrote in Python
            function = getattr(module, module_function.function)

            # See if the system wants us to tack any arguments to the front
            if module_function[2] is not None:
                function_args = module_function[2] + function_args

            if logger.isEnabledFor(logging.DEBUG):
                logger.debug(f"call {self._predication_index}: {module_function.module}.{module_function.function}, state: {str(state)}, phrase_type: [{self._phrase_type}]")

            # If a MessageException happens during execution,
            # convert it to an error
            had_solution = False
            try:
                # You call a function "pointer" and pass it arguments
                # that are a list by using "function(*function_args)"
                # So: this is actually calling our function (which
                # returns an iterator, and thus we can iterate over it)
                for next_state in function(*function_args):
                    if logger.isEnabledFor(logging.DEBUG):
                        logger.debug(f"yielding {predication}, state: {str(next_state)}, phrase_type: [{self._phrase_type}]")

                    had_solution = True
                    yield next_state

            except MessageException as error:
                self.report_error(error.message_object())

            if not had_solution:
                if logger.isEnabledFor(logging.DEBUG):
                    logger.debug(f"No solutions from {self._predication_index}: {module_function.module}.{module_function.function}")

                if self._predication_runtime_settings.get("Disjunction", False):
                    self._lineage_failure_callback(self._context.get_error_info())

        def _handle_lineage_change(self, new_lineage):
            if self._last_solution_lineage is not None and new_lineage != self._last_solution_lineage:
                if not new_lineage.startswith(self._last_solution_lineage):
                    # Fire an error for every disjunction set that didn't generate a solution
                    last_segments = self._last_solution_lineage.split(".")[1:]
                    new_segments = new_lineage.split(".")[1:]
                    for index in range(len(last_segments)):
                        if index > (len(new_segments) - 1) or last_segments[index] != new_segments[index]:
                            # This disjunction changed, fire a failure if there were no solutions
                            test_lineage = ".".join(last_segments[:index + 1])
                            was_successful = False
                            for successful_lineage in self._solution_lineages:
                                if successful_lineage.startswith(test_lineage):
                                    was_successful = True
                                    break

                            if not was_successful:
                                self._lineage_failure_callback(self._context.get_error_info())

            # And remember this as the last lineage
            self._last_solution_lineage = new_lineage

    # Represents a single lineage which is a particular choice of predication interpretations
    # and a selection of disjunction alternatives within any disjunction.
    # Note that this class records the failure that was encountered for the particular lineage
    class MrsTreeLineage(object):
        def __init__(self, lineage_generator):
            self.lineage_generator = lineage_generator
            self.error_info = ExecutionContext.blank_error_info()

        def __iter__(self):
            return self

        def __next__(self):
            try:
                return self.lineage_generator._next_solution()

            except StopIteration:
                self.error_info = self.lineage_generator.retrieve_lineage_failure()
                raise

    # Generator that returns every MrsTreeLineage alternative for a particular interpretation of a scope-resolved MRS.
    # This will only be one tree unless some of the predication implementations are disjunctions, in which case it will
    # return a different MrsTreeLineage for every combination of solution sets from each disjunction
    #
    # Because it is given an interpretation, the python functions that represent alternative interpretations are chosen up front
    # All that is left to disambiguate are different solution sets for interpretations that are disjunctions. These are identified
    # by a special variable added to the tree called "tree_lineage". If that exists, it means that one of the predications is a disjunction
    # and it adds a unique ID to the value of that variable in the form ":id:id:id", where each "id" represents a unique value for a particular
    # solution set from the disjunction at that point in the tree.
    #
    # Assumptions:
    #   - Disjunction predications must always indicate that they are a disjunction by calling context.set_disjunction() so that we
    #       can determine that a failure was a disjunction failure and generate an independent record for it
    #   - If a predication is a disjunction it must *always* put an ID in that position or else the lineage might mistakenly have a
    #       different predication giving a different ID for that position (because the original one is missing).
    #   - The same disjunction values must always be together. A disjunction predication can't intermingle the different solution sets.
    #       this allows us to assume that a conjunction has moved on when we encounter a new ID in its position and not have to wait for the
    #       whole set of solutions to be returned and sort them
    class MrsTreeLineageGenerator(object):
        def __init__(self, interpretation_solver, state, tree_info, interpretation):
            self.solution_generator = interpretation_solver.solve_tree_interpretation(state, tree_info, interpretation,
                                                                                      self.lineage_failed)
            self.lineage_failure_fifo = queue.Queue()
            self.next_lineage_solution = None
            self.first = True
            self.last_lineage = None

        def __iter__(self):
            return self

        def lineage_failed(self, error_info):
            pipeline_logger.debug(f"Lineage failed with error: {error_info}")
            self.lineage_failure_fifo.put(error_info)

        def retrieve_lineage_failure(self):
            if self.lineage_failure_fifo.empty():
                return None, False, -1
            else:
                return self.lineage_failure_fifo.get()

        def __next__(self):
            if self.first or self.next_lineage_solution is not None or not self.lineage_failure_fifo.empty():
                self.first = False
                return TreeSolver.MrsTreeLineage(self)
            else:
                raise StopIteration

        def _next_solution(self):
            # TODO: use try: so that we catch lineage failures at the end?
            if not self.lineage_failure_fifo.empty():
                # There are queued up errors to return
                raise StopIteration

            if self.next_lineage_solution is not None:
                # There is a queued up solution to return
                value = self.next_lineage_solution
                self.next_lineage_solution = None
                return value

            solution = next(self.solution_generator)
            tree_lineage_binding = solution.get_binding("tree_lineage")
            tree_lineage = "" if tree_lineage_binding.value is None else tree_lineage_binding.value[0]
            pipeline_logger.debug(f"MrsTreeLineageGenerator got solution for lineage {tree_lineage}: {str(solution)}")

            if not self.lineage_failure_fifo.empty():
                # There was at least one lineage failure during execution of next()
                self.next_lineage_solution = solution
                self.last_lineage = tree_lineage
                raise StopIteration

            elif self.last_lineage is None or self.last_lineage == tree_lineage:
                self.last_lineage = tree_lineage
                return solution

            else:
                self.next_lineage_solution = solution
                self.last_lineage = tree_lineage
                raise StopIteration

    # Yields an interpretation_solver and a generator for solutions for a particular lineage
    # Only does phase1 evaluation on the tree
    def phase1(self, state, tree_info, current_tree_index=None, normalize=False, target_interpretation_index=None, interpretation=None):
        current_tree_index_final = 0 if current_tree_index is None else current_tree_index

        if interpretation is not None:
            interpretation_list = [interpretation]
        else:
            interpretation_list = self._mrs_tree_interpretations(tree_info, normalize)

        current_interpretation = -1
        for interpretation_dict in interpretation_list:
            current_interpretation += 1
            if pipeline_logger.level == logging.DEBUG:
                func_list = ", ".join([f"{x.module}.{x.function}" for x in interpretation_dict.values()])

            if target_interpretation_index is not None:
                if current_interpretation < target_interpretation_index:
                    skipped_interpretation_record = TreeSolver.new_error_tree_record(tree=tree_info["Tree"],
                                                                                     error=ExecutionContext.blank_error(predication_index=0, error=['skipped']),
                                                                                     tree_index=current_tree_index_final)
                    if pipeline_logger.level == logging.DEBUG:
                        pipeline_logger.debug(f"Skipping interpretation #{current_interpretation}: '{func_list}'")

                    yield None, skipped_interpretation_record
                    continue

                elif current_interpretation > target_interpretation_index:
                    pipeline_logger.debug(f"Stopping alternatives since the target tree index {current_interpretation} has been passed")
                    return

            if pipeline_logger.level == logging.DEBUG:
                pipeline_logger.debug(f"Tree #{current_tree_index_final if current_tree_index is not None else 'unknown'}, interpretation #{current_interpretation if interpretation is None else 'unknown'}: '{func_list}'")

            interpretation_solver = TreeSolver.InterpretationSolver(self._context)
            lineage_generator = TreeSolver.MrsTreeLineageGenerator(interpretation_solver, state, tree_info, interpretation_dict)
            for solutions in lineage_generator:
                yield interpretation_solver, solutions

    # Main call to resolve a tree
    # Given a particular scope-resolved tree in tree_info,
    # yields a tree_record for every interpretation and combination of disjunctions
    # that was attempted (including records if they were skipped for debugging purposes)
    def tree_solutions(self, state,
                       tree_info,
                       response_function=None,
                       message_function=None,
                       current_tree_index=None,
                       target_tree_index=None,
                       target_interpretation_index=None,
                       interpretation=None,
                       find_all_solution_groups=True,
                       wh_phrase_variable=None):
        current_tree_index_recorded = 0 if current_tree_index is None else current_tree_index

        this_sentence_force = sentence_force(tree_info["Variables"])
        for context, solutions in self.phase1(state, tree_info,
                                              current_tree_index=current_tree_index,
                                              target_interpretation_index=target_interpretation_index,
                                              interpretation=interpretation):
            if isinstance(solutions, dict):
                # This is a record of a skipped true
                yield solutions
                continue

            tree_record = TreeSolver.new_tree_record(tree=tree_info["Tree"],
                                                     tree_index=current_tree_index_recorded,
                                                     selected_conjuncts=tree_info.get("SelectedConjuncts", None))

            # solution_groups() should return an iterator that iterates *groups*
            all_solution_groups = [] if find_all_solution_groups else None
            tree_record["SolutionGroupGenerator"] = at_least_one_generator(
                perplexity.solution_groups.solution_groups(context, solutions, this_sentence_force, wh_phrase_variable, tree_info, all_solution_groups=all_solution_groups))

            tree_record["SolutionGroups"] = all_solution_groups
            tree_record["Interpretation"] = ", ".join([f"{x.module}.{x.function}" for x in context.interpretation().values()])

            # Collect any error that might have occurred from the first solution group
            tree_record["Error"] = self._context.error()
            if message_function is not None and response_function is not None:
                tree_record["ResponseGenerator"] = at_least_one_generator(
                    response_function(self._context.vocabulary, message_function, tree_info, tree_record["SolutionGroupGenerator"], tree_record["Error"]))
            else:
                tree_record["ResponseGenerator"] = None

            tree_record["TreeIndex"] = current_tree_index_recorded
            if pipeline_logger.level == logging.DEBUG:
                pipeline_logger.debug(f"Returning tree_record for '{tree_info['Tree']}'")

            yield tree_record

    def _mrs_tree_interpretations(self, tree_info, normalize=False):
        # Gather together all the interpretations for the predications
        def gather(predication):
            alternatives = [(predication.index, x) for x in self._context.vocabulary.predications(predication.name,
                                                                                                 predication.arg_types,
                                                                                                 phrase_type)]
            predications.append(alternatives)

        phrase_type = sentence_force(tree_info["Variables"]) if not normalize else "norm"
        predications = []
        perplexity.tree.walk_tree_predications_until(tree_info["Tree"], gather)

        # Now iterate through all combinations of them by selecting each alternative in
        # every combination
        for option in product_stream(*list(iter(x) for x in predications)):
            yield dict(option)

    # Errors are encoded in a fake tree
    @staticmethod
    def new_error_tree_record(tree=None, error=None, response_generator=None, tree_index=None):
        return TreeSolver.new_tree_record(tree=tree,
                                          error=error,
                                          response_generator=response_generator,
                                          tree_index=tree_index,
                                          error_tree=True)

    @staticmethod
    def new_tree_record(tree=None, error=None, response_generator=None, response_message=None, tree_index=None,
                        error_tree=False, interpretation=None, selected_conjuncts=None):
        value = {"Tree": tree,
                 "Interpretation": interpretation,
                 "SolutionGroups": None,
                 "Solutions": [],
                 "Error": error,
                 "TreeIndex": tree_index,
                 "SolutionGroupGenerator": None,
                 "ResponseGenerator": [] if response_generator is None else response_generator,
                 "ResponseMessage": "" if response_message is None else response_message,
                 "SelectedConjuncts": selected_conjuncts}

        if error_tree:
            value["ErrorTree"] = True

        return value


class ExecutionContext(object):
    def __init__(self, vocabulary):
        self.vocabulary = vocabulary
        self._in_scope_initialize_function = None
        self._in_scope_initialize_data = None
        self._in_scope_function = None
        self.clear_error()

    @staticmethod
    def blank_error_info(error=None, was_forced=False, predication_index=-1, phase=0):
        return error, was_forced, predication_index, phase

    @staticmethod
    def blank_error(error=None, predication_index=-1, phase=0):
        return predication_index, error, phase

    def reset_scope(self, state):
        if self._in_scope_initialize_function is not None:
            self._in_scope_initialize_data = self._in_scope_initialize_function(state)

    def set_in_scope_function(self, func, initialize_func=None):
        self._in_scope_function = func
        self._in_scope_initialize_function = initialize_func

    # Test if an object is in scope, by default everything is
    def in_scope(self, state, thing):
        if self._in_scope_function is not None:
            return self._in_scope_function(self._in_scope_initialize_data, self, state, thing)
        else:
            return True

    def get_error_info(self):
        if self._error is not None:
            return self._error, self._error_was_forced, self._error_predication_index, self._error_phase
        else:
            return self._notUnderstood

    def set_error_info(self, error_info):
        if error_info is not None:
            self._error = error_info[0]
            self._error_was_forced = error_info[1]
            self._error_predication_index = error_info[2]
            self._error_phase = error_info[3]

    def clear_error(self):
        blank = self.blank_error_info()
        self._error = blank[0]
        self._error_was_forced = blank[1]
        self._error_predication_index = blank[2]
        self._error_phase = blank[3]

        self.clear_not_understood_error()

    def clear_not_understood_error(self):
        self._notUnderstood = self.blank_error_info()

    def has_not_understood_error(self):
        # System errors that indicate the phrase can't be understood can't be replaced
        # since they aren't indicating a logical failure, they are indicating that the system didn't understand
        # predications like neg() need to know if a branch failed due to a real logical failure or not
        if self._notUnderstood[0] is not None:
            return self._notUnderstood

    def report_error(self, error, force=False, phase=0):
        self.report_error_for_index(0, error, force, phase=phase)

    # Error Design: when a predication is called it either:
    #     - yields a value (success)
    #         - A success clears the error
    #     - doesn't yield a value, which stops the generator (failure)
    #         - If it fails, it can report: nothing, an normal error, or a formNotUnderstood error
    #             - a forced error is always recorded, and the first error at deepest level is always recorded
    #                 - Record both the first instance of a regular error and the first instance of formNotUnderstood at the deepest point
    #     - When returning errors: if we only got formNotUnderstood, that is the error. Otherwise: the first real error is the error
    def report_error_for_index(self, predication_index, error, force=False, phase=0):
        if force or self._error_predication_index < predication_index:
            if error[0] == "formNotUnderstood":
                # If previous error was not forced
                if not self._notUnderstood[1]:
                    self._notUnderstood = [error, force, predication_index, phase]

            else:
                if not self._error_was_forced:
                    self._error = error
                    self._error_predication_index = predication_index
                    self._error_phase = phase
                    if force:
                        self._error_was_forced = True

                    # Since we have a real error, clear out
                    self.clear_not_understood_error()

    def error(self):
        if self._error is not None:
            return [self._error_predication_index, self._error, self._error_phase]

        else:
            return [self._notUnderstood[2], self._notUnderstood[0], self._notUnderstood[3]]


logger = logging.getLogger('Execution')
pipeline_logger = logging.getLogger('Pipeline')
