import copy
import logging
import queue
import sys
import perplexity.tree
import perplexity.solution_groups
from perplexity.set_utilities import product_stream
from perplexity.utilities import sentence_force, at_least_one_generator
from perplexity.vocabulary import ValueSize


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
    def __init__(self, context):
        self._context = context

    @classmethod
    def create_top_level_solver(cls, vocabulary, scope_function, scope_init_function):
        context = ExecutionContext(vocabulary)
        context.set_in_scope_function(scope_function, scope_init_function)
        return cls(context)

    def create_child_solver(self):
        # Subtrees are resolved using the same context so error state is shared
        return TreeSolver(self._context)

    # This is the class that gets passed to predications as "context"
    # Lowest level class that walks a tree, in-order
    # Consumed by the MRSLineage classes which break the solutions
    # into different solution sets
    class InterpretationSolver(object):
        def __init__(self, context):
            self._context = context
            self.vocabulary = self._context.vocabulary

            self._interpretation = None
            self._predication_index = -1
            self._predication = None
            self._phrase_type = None
            self._tree_info = None
            self._variable_metadata = None
            self._predication_runtime_settings = None
            self._lineage_failure_callback = None
            self._solution_lineages = None
            self._last_solution_lineage = None
            self._variable_execution_data = {}

        # Returns solutions for a specific tree interpretation
        def solve_tree_interpretation(self, state, tree_info, interpretation, lineage_failure_callback):
            self._interpretation = interpretation
            self._predication_index = 0
            self._predication = None
            self._phrase_type = sentence_force(tree_info["Variables"])
            self._tree_info = tree_info
            self._variable_metadata = perplexity.tree.gather_predication_metadata(self._context.vocabulary, tree_info)
            self._predication_runtime_settings = {}
            self._lineage_failure_callback = lineage_failure_callback
            self._solution_lineages = set()
            self._last_solution_lineage = None
            self._variable_execution_data = {}

            self._context.reset_scope(state)
            self._context.clear_error()

            for solution in self.call(state.set_x("tree", (tree_info,), False), tree_info["Tree"]):
                # Remember any disjunction lineages that had a solution
                tree_lineage_binding = state.get_binding("tree_lineage")
                if tree_lineage_binding.value is not None:
                    self._solution_lineages.add(tree_lineage_binding.value[0])

                yield solution

            if self._last_solution_lineage is None:
                self._lineage_failure_callback(self._context.get_error_info())

            else:
                self._handle_lineage_change("")

            pipeline_logger.debug(f"Error after tree evaluation: {self._context.get_error_info()}")

        def in_scope(self, state, thing):
            return self._context.in_scope(state, thing)

        def has_not_understood_error(self):
            return self._context.has_not_understood_error()

        def report_error_for_index(self, predication_index, error, force=False):
            return self._context.report_error_for_index(predication_index, error, force)

        def report_error(self, error, force=False):
            self._context.report_error_for_index(self._predication_index, error, force)

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
            return self._variable_metadata.get(variable_name, {"ValueSize": ValueSize.all})

        def call(self, state, term, normalize=False):
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
                    # This is a list of predications, so they should
                    # treated as a conjunction.
                    # Call each one and pass the state it returns
                    # to the next one, recursively
                    for nextState in self.call(state, term[0], normalize):
                        # Note the [1:] syntax which means "return a list
                        # of everything but the first item"
                        yield from self.call(nextState, term[1:], normalize)

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
                yield from self._call_predication(state, term, normalize)

                # Restore it since we are recursing
                self._predication_index = last_predication_index
                self._predication = last_predication

        # Do not use directly.
        # Use Call() instead so that the predication index is set properly
        # The format we're using is:
        # ["folder_n_of", "x1"]
        #   The first item is the predication name
        #   The rest of the items are the arguments
        def _call_predication(self, state, predication, normalize=False):
            if logger.isEnabledFor(logging.DEBUG):
                logger.debug(f"call {self._predication_index}: {predication}({str(state)}) [{self._phrase_type}]")

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
            # TODO: Make this part work with the new scheme
            assert normalize is False
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

            # If a MessageException happens during execution,
            # convert it to an error
            try:
                # You call a function "pointer" and pass it arguments
                # that are a list by using "function(*function_args)"
                # So: this is actually calling our function (which
                # returns an iterator, and thus we can iterate over it)
                had_solution = False
                for next_state in function(*function_args):
                    had_solution = True
                    yield next_state

            except MessageException as error:
                self.report_error(error.message_object())

            if not had_solution:
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

    # Represents a single lineage
    class MrsTreeLineage(object):
        def __init__(self, lineage_generator):
            self.lineage_generator = lineage_generator
            self.error_info = (None, False, -1)

        def __iter__(self):
            return self

        def __next__(self):
            try:
                return self.lineage_generator._next_solution()

            except StopIteration:
                self.error_info = self.lineage_generator.retrieve_lineage_failure()
                raise

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
            # pipeline_logger.debug(f"Next MRS solution: {solution}")

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

    # Main call to resolve a tree
    # Given a particular scope-resolved tree in tree_info,
    # yields a tree_record for every interpretation and combination of disjunctions
    # that was attempted (including if they were skipped)
    def tree_solutions(self, state, tree_info, response_function=None, message_function=None,
                       current_tree_index=0, target_tree_index=None):
        wh_phrase_variable = perplexity.tree.get_wh_question_variable(tree_info)
        this_sentence_force = sentence_force(tree_info["Variables"])
        for interpretation in self._mrs_tree_interpretations(tree_info):
            if target_tree_index is not None:
                if current_tree_index < target_tree_index:
                    skipped_tree_record = TreeSolver.new_error_tree_record(tree=tree_info["Tree"], error="skipped",
                                                                           tree_index=current_tree_index)
                    current_tree_index += 1
                    yield skipped_tree_record
                    continue

                elif current_tree_index > target_tree_index:
                    return

            if pipeline_logger.level == logging.DEBUG:
                func_list = ", ".join([f"{x.module}.{x.function}" for x in interpretation.values()])
                pipeline_logger.debug(f"Evaluating alternative '{func_list}'")

            interpretation_solver = TreeSolver.InterpretationSolver(self._context)
            lineage_generator = TreeSolver.MrsTreeLineageGenerator(interpretation_solver, state, tree_info, interpretation)
            for solutions in lineage_generator:
                tree_record = TreeSolver.new_tree_record(tree=tree_info["Tree"], tree_index=current_tree_index)

                # solution_groups() should return an iterator that iterates *groups*
                tree_record["SolutionGroupGenerator"] = at_least_one_generator(
                    perplexity.solution_groups.solution_groups(interpretation_solver, solutions, this_sentence_force,
                                                               wh_phrase_variable, tree_info))

                # Collect any error that might have occurred from the first solution group
                tree_record["Error"] = self._context.error()
                if message_function is not None and response_function is not None:
                    tree_record["ResponseGenerator"] = at_least_one_generator(
                        response_function(message_function, tree_info, tree_record["SolutionGroupGenerator"],
                                          tree_record["Error"]))
                else:
                    tree_record["ResponseGenerator"] = None

                tree_record["TreeIndex"] = current_tree_index
                if pipeline_logger.level == logging.DEBUG:
                    func_list = ", ".join([f"{x.module}.{x.function}" for x in interpretation.values()])
                    pipeline_logger.debug(f"Returning tree_record for '{tree_info['Tree']}'")

                yield tree_record

            current_tree_index += 1

    def _mrs_tree_interpretations(self, tree_info):
        # Gather together all the interpretations for the predications
        def gather(predication):
            alternatives = [(predication.index, x) for x in self._context.vocabulary.predications(predication.name,
                                                                                                 predication.arg_types,
                                                                                                 phrase_type)]
            predications.append(alternatives)

        phrase_type = sentence_force(tree_info["Variables"])
        predications = []
        perplexity.tree.walk_tree_predications_until(tree_info["Tree"], gather)

        # Now iterate through all combinations of them by selecting each alternative in
        # every combination
        for option in product_stream(*list(iter(x) for x in predications)):
            yield dict(option)

    # Errors are encoded in a fake tree
    @staticmethod
    def new_error_tree_record(tree=None, error=None, response_generator=None, tree_index=None):
        return TreeSolver.new_tree_record(tree=tree, error=error, response_generator=response_generator,
                                          tree_index=tree_index, error_tree=True)


    @staticmethod
    def new_tree_record(tree=None, error=None, response_generator=None, response_message=None, tree_index=None,
                        error_tree=False):
        value = {"Tree": tree,
                 "SolutionGroups": None,
                 "Solutions": [],
                 "Error": error,
                 "TreeIndex": tree_index,
                 "SolutionGroupGenerator": None,
                 "ResponseGenerator": [] if response_generator is None else response_generator,
                 "ResponseMessage": "" if response_message is None else response_message}

        if error_tree:
            value["ErrorTree"] = True

        return value


class ExecutionContext(object):
    def __init__(self, vocabulary):
        self.vocabulary = vocabulary

        self._error = None
        self._error_predication_index = -1
        self._error_was_forced = False

        self._in_scope_initialize_function = None
        self._in_scope_initialize_data = None
        self._in_scope_function = None

    def reset_scope(self, state):
        if self._in_scope_initialize_function is not None:
            self._in_scope_initialize_data = self._in_scope_initialize_function(state)

    def set_in_scope_function(self, func, initialize_func=None):
        self._in_scope_function = func
        self._in_scope_initialize_function = initialize_func

    # Test if an object is in scope, by default everything is
    def in_scope(self, state, thing):
        if self._in_scope_function is not None:
            return self._in_scope_function(self._in_scope_initialize_data, state, thing)
        else:
            return True

    def get_error_info(self):
        return self._error, self._error_was_forced, self._error_predication_index

    def set_error_info(self, error_info):
        if error_info is not None:
            self._error = error_info[0]
            self._error_was_forced = error_info[1]
            self._error_predication_index = error_info[2]

    def clear_error(self):
        self._error = None
        self._error_was_forced = False
        self._error_predication_index = -1

    def has_not_understood_error(self):
        # System errors that indicate the phrase can't be understood can't be replaced
        # since they aren't indicating a logical failure, they are indicating that the system didn't understand
        # predications like neg() need to know if a branch failed due to a real logical failure or not
        not_understood_failures = ["formNotUnderstood"]
        return self._error is not None and self._error[0] in not_understood_failures

    def report_error_for_index(self, predication_index, error, force=False):
        if not self.has_not_understood_error() and \
                (force or (not self._error_was_forced and self._error_predication_index < predication_index)):
            self._error = error
            self._error_predication_index = predication_index
            if force:
                self._error_was_forced = True

    def error(self):
        return [self._error_predication_index, self._error]


logger = logging.getLogger('Execution')
pipeline_logger = logging.getLogger('Pipeline')
