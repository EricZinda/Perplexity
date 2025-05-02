import copy
import logging
import sys
import time
from collections import OrderedDict
import perplexity.tree
import perplexity.solution_groups
from perplexity.set_utilities import product_stream
from perplexity.utilities import sentence_force, at_least_one_generator, TimeoutException
import perplexity.vocabulary


# Allows code to throw an exception that should get converted
# to a user visible message
class MessageException(Exception):
    def __init__(self, message_name, message_args):
        self.message_name = message_name
        self.message_args = message_args

    def message_object(self):
        return [self.message_name] + self.message_args


# Generates all the solution groups that can produced by
# various interpretations of a tree.
# Each different interpretation results in a new tree_record
# even if it fails
class TreeSolver(object):
    def __init__(self, execution_context):
        self._execution_context = execution_context
        self._timeout = None
        self._start_time = None

    @staticmethod
    def create_top_level_solver(vocabulary, error_priority_function, scope_function, scope_init_function):
        context = ExecutionContext(vocabulary, error_priority_function)
        context.set_in_scope_function(scope_function, scope_init_function)
        return TreeSolver(context)

    # This is the class that gets passed to predications as "context"
    # It contains information scoped to the single interpretation function
    # It also has helper functions for the developer to use within their function
    # that call out to other wider contexts
    class CallContext(object):
        def __init__(self, execution_context, interpretation_solver, lineage, predication, predication_index, default_phase=1):
            self._execution_context = execution_context
            self._interpretation_solver = interpretation_solver
            self._lineage = lineage
            self._predication = predication
            # TODO: PredicationIndex gets set in call() but also is set up front as part of the predication object itself
            # these can get out of sync. They should probably be named different things so it is clear which you are using
            # because predications call call other predications and create a dynamic tree which is different from the original
            # MRS
            self._predication_index = predication_index
            self._default_phase = default_phase

        ##################################################################
        ### Helpers that delegate to ExecutionContext scope
        ##################################################################

        def in_scope(self, state, thing):
            return self._execution_context.in_scope(state, thing)

        def error_priority(self):
            return self._execution_context.error_priority()

        def new_initial_context(self):
            return self._execution_context.new_initial_context()

        ##################################################################
        ### Helpers that delegate to TreeSolver scope
        ##################################################################
        def new_solver(self):
            return TreeSolver(self.new_initial_context())

        ##################################################################
        ### Helpers that delegate to InterpretationSolver scope
        ##################################################################

        def interpretation(self):
            return self._interpretation_solver.interpretation()

        def tree_info(self):
            return self._interpretation_solver.tree_info

        def call(self, state, term):
            yield from self._interpretation_solver.call(state, term)

        def has_not_understood_error(self):
            return self._interpretation_solver.has_not_understood_error_lineage(self._lineage)

        def report_error_for_index(self, predication_index, error, force=False, phase=None):
            phase = phase if phase is not None else self._default_phase
            return self._interpretation_solver.report_error_for_index_lineage(self._lineage, predication_index, error, force, phase=phase)

        def report_error(self, error, force=False, phase=None):
            phase = phase if phase is not None else self._default_phase
            self._interpretation_solver.report_error_for_index_lineage(self._lineage, self._predication_index, error, force, phase=phase)

        def get_error_info(self):
            return self._interpretation_solver.get_error_info_lineage(self._lineage)

        def set_error_info(self, error_info):
            return self._interpretation_solver.set_error_info_lineage(self._lineage, error_info)

        def clear_error(self):
            return self._interpretation_solver.clear_error_lineage(self._lineage)

        def set_variable_execution_data(self, variable_name, key, value):
            self._interpretation_solver.set_variable_execution_data_lineage(self._lineage, variable_name, key, value)

        def get_variable_execution_data(self, variable_name):
            return self._interpretation_solver.get_variable_execution_data_lineage(self._lineage, variable_name)

        def get_variable_metadata(self, variable_name):
            # TODO: This is a hack to enable metadata for eval(). Need to fix it
            return self._interpretation_solver.get_variable_metadata(variable_name)

        ##################################################################
        ### Helpers at Interpretation Function scope
        ##################################################################

        def current_predication_index(self):
            return self._predication_index

        def current_predication(self):
            return self._predication

    # This is the lowest level class that walks a tree, in-order
    # and is consumed by the DisjunctionInterpretationGenerator class which breaks the solutions
    # into different solution sets
    class InterpretationSolver(object):
        def __init__(self, execution_context, timeout, start_time):
            self._execution_context = execution_context
            self._timeout = timeout
            self._start_time = start_time
            self.vocabulary = self._execution_context.vocabulary

            self._interpretation = None
            self._predication_index = -1
            self._predication = None
            self._phrase_type = None
            self.tree_info = None
            self._variable_metadata = None
            self.lineage_tracker = None
            self._disjunction_interpretation_generator = None

        # Needs to be called after construction due to a circular reference
        # between the two classes
        def set_disjunction_interpretation_generator(self, gen):
            self._disjunction_interpretation_generator = gen

        def lineages_complete(self, lineages):
            self._disjunction_interpretation_generator.lineages_complete(lineages)

        def has_timed_out(self, where):
            if perplexity.utilities.running_under_debugger():
                return False

            if self._timeout is not None and self._start_time is not None and time.perf_counter() - self._start_time > self._timeout:
                pipeline_logger.debug(f"Timed out in {where}.")
                return True

            else:
                return False

        # This is statically determined so doesn't depend on lineage
        def get_variable_metadata(self, variable_name):
            # TODO: This is a hack to enable metadata for eval(). Need to fix it
            return self._variable_metadata.get(variable_name, {"ValueSize": perplexity.vocabulary.ValueSize.all})

        # ************
        # *** All functions below here operate against the current lineage
        # ************

        # Base function that does some change to state from a lineage, and all lineages
        # that are children of it.  The state might be in the lineage_tracker (if still active)
        # or just a final state and stored in _disjunction_interpretation_generator (if complete)
        def apply_to_child_disjunction_interpretation_state_lineage(self, lineage, func):
            child_lineages = {lineage}
            for child_lineage in self.lineage_tracker.child_lineages_of(lineage):
                child_lineages.add(child_lineage)
                state = self.lineage_tracker.active_lineages.get(child_lineage, None)
                if state:
                    func(state)

            for child_lineage in child_lineages:
                interpretation = self._disjunction_interpretation_generator.interpretation_for_lineage(child_lineage)
                if interpretation:
                    func(interpretation.state)

        # Returns a copy
        def disjunction_interpretation_state_from_lineage(self, lineage):
            state = self.lineage_tracker.active_lineages.get(lineage, None)
            if state:
                return state
            else:
                return self._disjunction_interpretation_generator.interpretation_for_lineage(lineage).state

        def disjunction_interpretation_error_from_lineage(self, lineage):
            state = self.disjunction_interpretation_state_from_lineage(lineage)
            return copy.deepcopy(state.error_info)

        def set_variable_execution_data_lineage(self, lineage, variable_name, key, value):
            def func(state):
                state.set_variable_execution_data(variable_name, key, value)

            self.apply_to_child_disjunction_interpretation_state_lineage(lineage, func)

        def get_variable_execution_data_lineage(self, lineage, variable_name):
            state = self.disjunction_interpretation_state_from_lineage(lineage)
            return state.get_variable_execution_data_lineage(variable_name)

        def get_error_info_lineage(self, lineage):
            return self.disjunction_interpretation_error_from_lineage(lineage)

        def get_error_info(self, state):
            lineage = perplexity.tree.get_disjunction_tree_lineage(state)
            return self.get_error_info_lineage(lineage)

        def set_error_info_lineage(self, lineage, error_info):
            def func(state):
                state.error_info.set_error_info(error_info)

            self.apply_to_child_disjunction_interpretation_state_lineage(lineage, func)

        def set_error_info(self, state, error_info):
            lineage = perplexity.tree.get_disjunction_tree_lineage(state)
            self.set_error_info_lineage(lineage, error_info)

        def clear_error_lineage(self, lineage):
            def func(state):
                state.error_info.clear_error()

            self.apply_to_child_disjunction_interpretation_state_lineage(lineage, func)

        def clear_error(self, state):
            lineage = perplexity.tree.get_disjunction_tree_lineage(state)
            self.clear_error_lineage(lineage)

        def has_not_understood_error_lineage(self, lineage):
            return self.disjunction_interpretation_error_from_lineage(lineage).has_not_understood_error()

        def has_not_understood_error(self, state):
            lineage = perplexity.tree.get_disjunction_tree_lineage(state)
            return self.has_not_understood_error_lineage(lineage)

        def report_error_for_index_lineage(self, lineage, predication_index, error, force=False, phase=1):
            def func(state):
                # Only apply errors to interpretations that aren't already marked as notUnderstood
                if not state.error_info.has_not_understood_error():
                    state.error_info.report_error_for_index(predication_index=predication_index,
                                                                            error=error, force=force, phase=phase)

            self.apply_to_child_disjunction_interpretation_state_lineage(lineage, func)

        def report_error_for_index(self, state, predication_index, error, force=False, phase=1):
            lineage = perplexity.tree.get_disjunction_tree_lineage(state)
            self.report_error_for_index_lineage(lineage, predication_index, error, force=False, phase=1)

        # ************
        # *** end
        # ************

        def interpretation(self):
            return self._interpretation

        # Walk the tree and compare any predication with property requirements to the tree_info
        # Fail if they don't match
        def tree_matches_interpretation_properties(self, lineage, tree_info, interpretation):
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
                            self.report_error_for_index_lineage(lineage, predication.index, ["formNotUnderstood", function.__name__])
                            return False

            force = sentence_force(tree_info["Variables"])
            result = perplexity.tree.walk_tree_predications_until(tree_info["Tree"], check_predication)
            return result is not False

        # Returns solutions for a specific tree interpretation that is passed in
        # Ignores (but keeps track of) disjunction interpretation boundaries,
        # just returns a stream of all solutions
        def solve_tree_interpretation(self, state, tree_info, interpretation):
            self._interpretation = interpretation
            self._predication_index = 0
            self._predication = None
            self._phrase_type = sentence_force(tree_info["Variables"])
            self.tree_info = tree_info
            self._variable_metadata = perplexity.tree.gather_predication_metadata(self._execution_context.vocabulary, tree_info, interpretation)
            self._execution_context.reset_scope(state)
            self.lineage_tracker = DisjunctionInterpretationTracker()

            # Start with an initial ErrorInfo for the first predication
            # {interpretation_index} @ {new_lineage}
            initial_lineage = "-1@0"
            state = state.set_x("tree_lineage", (initial_lineage,))
            self.lineage_tracker.successful_predication(initial_lineage)

            # See if we should run the tree at all
            if self.tree_matches_interpretation_properties(initial_lineage, tree_info, interpretation):
                # Whenever there is a solution, this means there was not an error, by definition
                # So: clear it before we yield
                for solution in self.call(state.set_x("tree", (tree_info,), False), tree_info["Tree"]):
                    # Remember which interpretation generated this solution so that we can
                    # call the right solution group handler later
                    yield solution.set_x("interpretation", (interpretation, ))

            else:
                pipeline_logger.debug(f"Tree did not match interpretation properties for: {str(interpretation)}")

        def call(self, state, term):
            if self.has_timed_out("call"):
                raise TimeoutException

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

            # Create the context object this predication function will use
            lineage = perplexity.tree.get_disjunction_tree_lineage(state)
            call_context = TreeSolver.CallContext(self._execution_context, self, lineage, predication, self._predication_index)

            # [list] + [list] will return a new, combined list
            # in Python. This is how we add the state object
            # onto the front of the argument list
            function_args = [call_context, state] + bindings

            # Look up the actual Python module and
            # function name given a string like "folder_n_of".
            # "vocabulary.Predication" returns a two-item list,
            # where item[0] is the module and item[1] is the function
            vocabulary_entry = self._interpretation[predication.index]

            # sys.modules[] is a built-in Python list that allows you
            # to access actual Python Modules given a string name
            module = sys.modules[vocabulary_entry.module]

            # Functions are modeled as properties of modules in Python
            # and getattr() allows you to retrieve a property.
            # So: this is how we get the "function pointer" to the
            # predication function we wrote in Python
            function = getattr(module, vocabulary_entry.function)

            # See if the system wants us to tack any arguments to the front
            if vocabulary_entry[2] is not None:
                function_args = vocabulary_entry[2] + function_args

            if logger.isEnabledFor(logging.DEBUG):
                logger.debug(f"call {self._predication_index}: {vocabulary_entry.module}.{vocabulary_entry.function}, state: {str(state)}, phrase_type: [{self._phrase_type}]")

            # If a MessageException happens during execution,
            # convert it to an error
            try:
                # You call a function "pointer" and pass it arguments
                # that are a list by using "function(*function_args)"
                # So: function(*function_args) is actually calling our function (which
                # returns an iterator, and thus we can iterate over it)
                # DisjunctionPredicationWrapper tracks successes and failures of predications so we can properly
                # Manage disjunction trees which are created dynamically
                for next_state in TreeSolver.DisjunctionPredicationWrapper(self, call_context, function(*function_args), ):
                    if logger.isEnabledFor(logging.DEBUG):
                        logger.debug(f"yielding {predication}, state: {str(next_state)}, phrase_type: [{self._phrase_type}]")

                    yield next_state

            except MessageException as error:
                self.report_error(error.message_object())

    # Predications aren't iterated directly, they are always wrapped by a DisjunctionPredicationWrapper.
    # This iterator properly handles the logic of ignoring interpretations once any subpart of their tree has
    # set formNotUnderstood.
    #
    # If any of the functions in this interpretation subtree raises formNotUnderstood,
    # Then it means that either a) it will continue to do so since it is designed for "Concept" and is getting
    # instances (or vice versa) OR b) there are simply some atoms in the world that can't be processed by
    # the implementation for some reason and thus we can't say anything truthful about the statement since
    # we didn't understand some parts.  Either way: we should abort this interpretation and look for others
    #
    # But: if this is a disjunction interpretation, we should only abort the values from the current disjunction variant because
    # the next one might work
    class DisjunctionPredicationWrapper(object):
        def __init__(self, interpretation_solver, call_context, predication_iterator):
            self._interpretation_solver = interpretation_solver
            self._call_context = call_context
            self._initial_error_info = call_context.get_error_info()
            self._predication_iterator = predication_iterator
            self._current_lineage = None

        def __iter__(self):
            return self

        def __next__(self):
            if self.is_disjunction() and self._interpretation_solver.has_not_understood_error_lineage(self._current_lineage):
                # The call stack records this predication is in the *previous* lineage since the next lineage is actually created by it
                # so we need to use the lineage we created in this predication instead to see if our children lineages didn't understand
                # and, if so, skip until we get a new lineage
                logger.debug(f"formNotUnderstood set, {self._call_context.current_predication()} is a disjunction predication")
                current_lineage = self._current_lineage
                while True:
                    # Reset the error state to where we first started so we don't bleed the error into the next attempt
                    last_error_info = self._interpretation_solver.get_error_info_lineage(self._current_lineage)
                    self._call_context.set_error_info(self._initial_error_info)
                    try:
                        next_solution, next_lineage = self._get_next_interpretation_value()
                        if next_lineage != current_lineage:
                            logger.debug(f"Continuing next disjunction predication of {self._call_context.current_predication()} due to formNotUnderstood")
                            return next_solution

                    except StopIteration:
                        self._interpretation_solver.set_error_info_lineage(self._current_lineage, last_error_info)
                        raise

            elif self._call_context.has_not_understood_error():
                # A normal (i.e. non-disjunction) predication should just stop iterating if the tree
                # has encountered formNotUnderstood
                logger.debug(f"Stop processing non-disjunction predication {self._call_context.current_predication()} due to formNotUnderstood")
                raise StopIteration

            else:
                next_solution, _ = self._get_next_interpretation_value()
                return next_solution

        def is_disjunction(self):
            return self._current_lineage is not None

        def _get_next_interpretation_value(self):
            next_solution = next(self._predication_iterator)
            next_lineage = perplexity.tree.get_disjunction_tree_lineage(next_solution)

            # Only remember the lineage if *this predication* actually created a disjunction so we can use this later
            # to determine if this is a disjunction predication
            if perplexity.tree.has_created_disjunction(self._call_context.current_predication().index, next_solution):
                self._current_lineage = next_lineage

                # Inform the lineage tracker of any new lineages and retire any old ones
                complete_lineages = self._interpretation_solver.lineage_tracker.successful_predication(next_lineage)
                self._interpretation_solver.lineages_complete(complete_lineages)

            return next_solution, next_lineage

    # Starts with a tree and for every static interpretation of it (unless it is passed one, in which case it only does that one):
    # Yields an interpretation_solver and a generator for solutions for a *particular disjunction interpretation*
    # Only does phase1 evaluation on the tree
    def phase1(self, state, tree_info, current_tree_index=None, normalize=False, target_interpretation_index=None, interpretation=None):
        current_tree_index_final = 0 if current_tree_index is None else current_tree_index

        if interpretation is not None:
            interpretation_list = [interpretation]

        else:
            interpretation_list = self.mrs_tree_interpretations(tree_info, normalize)

        current_interpretation = -1
        for interpretation_dict in interpretation_list:
            current_interpretation += 1
            func_list = ", ".join([f"{x.module}.{x.function}" for x in interpretation_dict.values()]) if pipeline_logger.level == logging.DEBUG else None

            if target_interpretation_index is not None:
                if current_interpretation < target_interpretation_index:
                    skipped_interpretation_record = TreeSolver.new_error_tree_record(tree=tree_info["Tree"],
                                                                                     error=ErrorInfo(predication_index=0, error=['skipped'], phase=1),
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

            # Get the raw solver which ignores disjunction lineages in the interpretation and treats the tree as a stream of solutions
            interpretation_solver = TreeSolver.InterpretationSolver(self._execution_context, self._timeout, self._start_time)
            interpretation_solution_generator = interpretation_solver.solve_tree_interpretation(state, tree_info, interpretation_dict)

            # Wrap it with DisjunctionVariantGenerator which is a generator of generators and breaks it into discrete disjunction interpretations
            interpretation_disjunction_generator = perplexity.tree.DisjunctionInterpretationGenerator(interpretation_solver, interpretation_solution_generator)
            interpretation_solver.set_disjunction_interpretation_generator(interpretation_disjunction_generator)

            for disjunction_interpretation in interpretation_disjunction_generator:
                yield interpretation_solver, disjunction_interpretation

    def has_timed_out(self, where):
        if perplexity.utilities.running_under_debugger():
            return False

        if self._timeout is not None and self._start_time is not None and time.perf_counter() - self._start_time > self._timeout:
            pipeline_logger.debug(f"Timed out in {where}.")
            return True

        else:
            return False

    # Main call to resolve a tree
    # Given a particular scope-resolved tree in tree_info,
    # yields a tree_record for every complete interpretation
    # that was attempted (including records if they were skipped
    # for debugging purposes or failed to generate solutions)
    def tree_solutions(self,
                       state,
                       tree_info,
                       current_tree_index=None,
                       target_interpretation_index=None,
                       interpretation=None,
                       find_all_solution_groups=True,
                       wh_phrase_variable=None,
                       timeout=None,
                       start_time=None):
        self._timeout = timeout
        self._start_time = start_time
        current_tree_index_recorded = 0 if current_tree_index is None else current_tree_index

        this_sentence_force = sentence_force(tree_info["Variables"])
        try:
            for interpretation_solver, disjunction_interpretation in self.phase1(state, tree_info,
                                                                                 current_tree_index=current_tree_index,
                                                                                 target_interpretation_index=target_interpretation_index,
                                                                                 interpretation=interpretation):
                if isinstance(disjunction_interpretation, dict):
                    # This is a record of a skipped true, just yield the record
                    yield disjunction_interpretation
                    continue

                tree_record = TreeSolver.new_tree_record(tree=tree_info["Tree"],
                                                         tree_index=current_tree_index_recorded,
                                                         selected_conjuncts=tree_info.get("SelectedConjuncts", None))

                # solution_groups() returns an iterator that iterates *groups*
                all_solution_groups = [] if find_all_solution_groups else None
                tree_record["SolutionGroupGenerator"] = at_least_one_generator(
                    perplexity.solution_groups.solution_groups(self._execution_context,
                                                               interpretation_solver,
                                                               disjunction_interpretation,
                                                               this_sentence_force,
                                                               wh_phrase_variable,
                                                               tree_info,
                                                               start_time=self._start_time,
                                                               timeout=self._timeout))

                tree_record["SolutionGroups"] = all_solution_groups
                tree_record["Interpretation"] = ", ".join([f"{x.module}.{x.function}" for x in interpretation_solver.interpretation().values()])
                tree_record["Error"] = copy.deepcopy(disjunction_interpretation.state.error_info)
                tree_record["TreeIndex"] = current_tree_index_recorded
                if pipeline_logger.level == logging.DEBUG:
                    pipeline_logger.debug(f"Returning tree_record for {disjunction_interpretation.lineage} '{tree_info['Tree']}'")

                yield tree_record

        except TimeoutException:
            # TODO: why are we ignoring??
            pass

    def mrs_tree_interpretations(self, tree_info, normalize=False):
        # Gather together all the interpretations for the predications
        def gather(predication):
            alternatives = [(predication.index, vocabulary_entry) for vocabulary_entry in self._execution_context.vocabulary.predications(predication.name,
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
    def new_error_tree_record(tree=None, error=None, response_generator=None, tree_index=None, response_message=None):
        return TreeSolver.new_tree_record(tree=tree,
                                          error=error,
                                          response_generator=response_generator,
                                          response_message=response_message,
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


# Shared between the DisjunctionInterpretationTracker and DisjunctionInterpretation
# classes so they update the same object
class DisjunctionInterpretationState(object):
    def __init__(self):
        self.error_info = ErrorInfo()
        self.variable_execution_data = {}

    def set_variable_execution_data(self, variable_name, key, value):
        if variable_name not in self.variable_execution_data:
            self.variable_execution_data[variable_name] = {}

        self.variable_execution_data[variable_name][key] = value

    def get_variable_execution_data(self, variable_name):
        return self.variable_execution_data.get(variable_name, {})


# DisjunctionInterpretationTracker is designed to hold the state of a
# DisjunctionInterpretation while it is being evaluated (i.e. while it is active)
# and to quit tracking it (and return it to the caller) when lineages are complete
# which happens when the tree evaluation is such that we know they won't continue
# This allows us to report them as failed IF they generated no solutions since the
# DisjunctionInterpretationGenerator won't see them and would lose the failed interpretations
class DisjunctionInterpretationTracker:
    def __init__(self):
        # Always start with the initial lineage existing so that
        # callers can report errors on it
        self.active_lineages = {"-1@0": DisjunctionInterpretationState()}

    def complete_active_lineages(self):
        return self.successful_predication(None)

    # If the old lineage is not the prefix of the new lineage, then it is complete
    # Because: lineages monotonically increase and will not repeat the previous prefix
    def _old_lineage_complete(self, old_lineage, new_lineage):
        return not new_lineage.startswith(old_lineage)

    def _parent_lineage(self, lineage):
        return lineage[:lineage.rfind(".")]

    # Returns a list of DisjunctionInterpretations that are complete
    # If None is passed as lineage, it completes all active lineages
    # (and does not add "None" as a new one)
    def successful_predication(self, lineage):
        exists = False
        complete_lineage_error_infos = OrderedDict()
        for key in list(self.active_lineages.keys()):
            if lineage == key:
                # This is the exact lineage
                exists = True

            elif lineage is None or self._old_lineage_complete(old_lineage=key, new_lineage=lineage):
                # equality is caught by the initial if, so these are true prefixes, meaning there is another key at the end
                complete_lineage_error_infos[key] = self.active_lineages[key]
                del self.active_lineages[key]

        # Remember the new lineage and start with a copy of the lineage state it came from
        if lineage is not None and not exists:
            parent_lineage_state = self.active_lineages[self._parent_lineage(lineage)]
            self.active_lineages[lineage] = copy.deepcopy(parent_lineage_state)

        # Sort the lineages and only return those that have the longest lineages since those are the most explored trees
        # shorter lineages are just intermediate results
        complete_lineages = {}
        keys = list(complete_lineage_error_infos.keys())
        for index in range(0, len(complete_lineage_error_infos)):
            last_index = index == len(complete_lineage_error_infos) - 1
            if last_index or not keys[index + 1].startswith(keys[index]):
                complete_lineages[keys[index]] = complete_lineage_error_infos[keys[index]]

        return complete_lineages

    def child_lineages_of(self, lineage):
        for key in list(self.active_lineages.keys()):
            if key.startswith(lineage):
                yield key


# Tracks a single error and has methods to set if the new error is better
class ErrorInfo:
    def __init__(self, error=None, was_forced=False, predication_index=-1, phase=0):
        self.error = error
        self.error_was_forced = was_forced
        self.error_predication_index = predication_index
        self.error_phase = phase

    def __repr__(self):
        return f"{self.error} (forced={self.error_was_forced}, index={self.error_predication_index}, phase={self.error_phase})"

    def set_error_info(self, error_info):
        assert error_info is not None
        self.error = error_info.error
        self.error_was_forced = error_info.error_was_forced
        self.error_predication_index = error_info.error_predication_index
        self.error_phase = error_info.error_phase

    def clear_error(self):
        blank = ErrorInfo()
        self.set_error_info(blank)

    def has_not_understood_error(self):
        # System errors that indicate the phrase can't be understood can't be replaced
        # since they aren't indicating a logical failure, they are indicating that the system didn't understand
        # predications like neg() need to know if a branch failed due to a real logical failure or not
        return self.error is not None and self.error[0] == "formNotUnderstood"

    # Error Design: when a predication is called it either:
    # - yields a value (success)
    # - doesn't yield a value, which stops the generator (failure)
    #     - If it fails, it can report: nothing, a normal error, or a formNotUnderstood error
    #         - a forced error is always recorded as long as it is in the same phase or greater, and the first error at deepest level is always recorded
    # - When returning errors: if we only got formNotUnderstood, that is the error. Otherwise: the first real error is the error
    def report_error_for_index(self, predication_index, error, force=False, phase=1):
        if self.error_phase <= phase and (force or self.error_predication_index < predication_index or error[0] == "formNotUnderstood"):
            assert not self.has_not_understood_error()
            self.set_error_info(ErrorInfo(error, force, predication_index, phase))


# ExecutionContext tracks information used for processing the whole tree
# which spans interpretations
class ExecutionContext(object):
    def __init__(self, vocabulary, error_priority_function):
        self.vocabulary = vocabulary
        self.error_priority_function = error_priority_function
        self._in_scope_initialize_function = None
        self._in_scope_initialize_data = None
        self._in_scope_function = None

    def new_initial_context(self):
        context = ExecutionContext(self.vocabulary, self.error_priority_function)
        context.set_in_scope_function(self._in_scope_function, self._in_scope_initialize_function)
        return context

    def reset_scope(self, state):
        if self._in_scope_initialize_function is not None:
            self._in_scope_initialize_data = self._in_scope_initialize_function(state)

    def error_priority(self):
        return self.error_priority_function

    def set_in_scope_function(self, func, initialize_func=None):
        self._in_scope_function = func
        self._in_scope_initialize_function = initialize_func

    # Test if an object is in scope, by default everything is
    def in_scope(self, state, thing):
        if self._in_scope_function is not None:
            return self._in_scope_function(self._in_scope_initialize_data, self, state, thing)
        else:
            return True


logger = logging.getLogger('Execution')
pipeline_logger = logging.getLogger('Pipeline')
