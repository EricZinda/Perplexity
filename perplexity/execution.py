import copy
import logging
import queue
import sys
import perplexity.tree
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
    def __init__(self, context, state, tree_info, interpretation):
        self.solution_generator = context.solve_mrs_tree(state, tree_info, interpretation, self.lineage_failed)
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
            return (None, False, -1)
        else:
            return self.lineage_failure_fifo.get()

    def __next__(self):
        if self.first or self.next_lineage_solution is not None or not self.lineage_failure_fifo.empty():
            self.first = False
            return MrsTreeLineage(self)
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


class TreeSolver(object):
    def __init__(self):
        pass

    # Errors are encoded in a fake tree
    @staticmethod
    def new_error_tree_record(tree=None, error=None, response_generator=None, tree_index=None):
        return TreeSolver.new_tree_record(tree=tree, error=error, response_generator=response_generator, tree_index=tree_index, error_tree=True)

    @staticmethod
    def new_tree_record(tree=None, error=None, response_generator=None, response_message=None, tree_index=None, error_tree=False):
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

    # Given a particular scope-resolved tree in tree_info,
    # yields a tree_record for every interpretation and combination of disjunctions that was attempted (including if they were skipped)
    def tree_solutions(self, state, tree_info, context, response_function=None, message_function=None, current_tree_index=0, target_tree_index=None):
        wh_phrase_variable = perplexity.tree.get_wh_question_variable(tree_info)
        this_sentence_force = sentence_force(tree_info["Variables"])
        for interpretation in context.mrs_tree_interpretations(tree_info):
            if target_tree_index is not None:
                if current_tree_index < target_tree_index:
                    skipped_tree_record = TreeSolver.new_error_tree_record(tree=tree_info["Tree"], error="skipped", tree_index=current_tree_index)
                    current_tree_index += 1
                    yield skipped_tree_record
                    continue

                elif current_tree_index > target_tree_index:
                    return

            if pipeline_logger.level == logging.DEBUG:
                func_list = ", ".join([f"{x.module}.{x.function}" for x in interpretation.values()])
                pipeline_logger.debug(f"Evaluating alternative '{func_list}'")

            lineage_generator = MrsTreeLineageGenerator(context, state, tree_info, interpretation)
            for solutions in lineage_generator:
                tree_record = TreeSolver.new_tree_record(tree=tree_info["Tree"], tree_index=current_tree_index)

                # solution_groups() should return an iterator that iterates *groups*
                tree_record["SolutionGroupGenerator"] = at_least_one_generator(
                    perplexity.solution_groups.solution_groups(context, solutions, this_sentence_force, wh_phrase_variable, tree_info))

                # Collect any error that might have occurred from the first solution group
                tree_record["Error"] = context.error()
                if message_function is not None and response_function is not None:
                    tree_record["ResponseGenerator"] = at_least_one_generator(
                        response_function(message_function, tree_info, tree_record["SolutionGroupGenerator"],
                                          tree_record["Error"]))
                else:
                    tree_record["ResponseGenerator"] = None

                tree_record["TreeIndex"] = current_tree_index
                yield tree_record

            current_tree_index += 1


class ExecutionContext(object):
    def __init__(self, vocabulary):
        self.vocabulary = vocabulary
        self._error = None
        self._error_predication_index = -1
        self._error_was_forced = False
        self._interpretation = None
        self.lineage_failure_callback = None
        self.solution_lineages = None
        self.last_solution_lineage = None
        self._predication_index = -1
        self._predication = None
        self._predication_runtime_settings = None
        self._phrase_type = None
        self._variable_execution_data = {}
        self.tree_info = None
        self._variable_metadata = None
        self._in_scope_initialize_function = None
        self._in_scope_initialize_data = None
        self._in_scope_function = None

    def resolve_fragment_new(self, state, tree_node):
        pipeline_logger.debug(f"Solving fragment: {tree_node}")
        solver = TreeSolver()
        new_tree_info = copy.deepcopy(self.tree_info)
        new_tree_info["Tree"] = tree_node
        new_state = state.set_x("tree", (new_tree_info, ))
        for tree_record in solver.tree_solutions(new_state,
                                                 new_tree_info,
                                                 self):
            solution_group_generator = tree_record["SolutionGroupGenerator"]
            if solution_group_generator is not None:
                # There were solutions, so this is our answer.
                solutions = [x for x in solution_group_generator]
                if pipeline_logger.level == logging.DEBUG:
                    nl = '\n'
                    pipeline_logger.debug(
                        f"Found fragment solution group: {nl + '   ' + (nl + '   ').join([str(s) for s in solutions])}")
                yield solutions

        pipeline_logger.debug(f"Done Resolving fragment: {tree_node}")

    def resolve_fragment(self, state, tree_node, extra_variables=None, criteria_list=None):
        this_sentence_force = sentence_force(self.tree_info["Variables"])
        new_tree_info = copy.deepcopy(self.tree_info)
        if extra_variables is not None:
            new_tree_info["Variables"].update(extra_variables)

        new_tree_info["Tree"] = tree_node
        new_state = state.set_x("tree", (new_tree_info, ))
        wh_phrase_variable = None
        if this_sentence_force == "ques":
            predication = perplexity.tree.find_predication(self.tree_info["Tree"], "_which_q")
            if predication is not None:
                wh_phrase_variable = predication.args[0]

        solutions = self.call(new_state, tree_node)
        solutions_list = list(solutions)
        pipeline_logger.debug(f"Resolving fragment: {tree_node}")
        # TODO: suspect the interleaving of resolve_fragment() with normal MRS solving is causing a subtle bug since
        #         resolving it all up front doesn't have the bug. Fix that bug and then allow this to stream
        for group in perplexity.solution_groups.solution_groups(self, solutions_list, this_sentence_force, wh_phrase_variable, new_tree_info, all_groups=True, criteria_list=criteria_list):
            solutions = [x for x in group]
            if pipeline_logger.level == logging.DEBUG:
                nl = '\n'
                pipeline_logger.debug(
                    f"Found fragment solution group: {nl + '   ' + (nl + '   ').join([str(s) for s in solutions])}")
            yield solutions

        pipeline_logger.debug(f"Done Resolving fragment: {tree_node}")

    def mrs_tree_interpretations(self, tree_info):
        # Gather together all the interpretations for the predications
        def gather(predication):
            identifier = (predication.name, tuple(predication.arg_types), phrase_type)
            alternatives = [(predication.index, x) for x in self.vocabulary.predications(predication.name, predication.arg_types, phrase_type)]
            predications.append(alternatives)

        phrase_type = sentence_force(tree_info["Variables"])
        predications = []
        perplexity.tree.walk_tree_predications_until(tree_info["Tree"], gather)

        # Now iterate through all combinations of them by selecting each alternative in
        # every combination
        for option in product_stream(*list(iter(x) for x in predications)):
            yield dict(option)

    # Needs to be called in a: with ExecutionContext() block
    # so that the execution context is set up properly
    # and maintained while all the solution groups are generated
    def solve_mrs_tree(self, state, tree_info, interpretation, lineage_failure_callback):
        self.clear_error()
        self._interpretation = interpretation
        self._predication_index = 0
        self._predication_runtime_settings = None
        self._phrase_type = sentence_force(tree_info["Variables"])
        self.tree_info = tree_info
        self.gather_tree_metadata()
        self.lineage_failure_callback = lineage_failure_callback
        self.solution_lineages = set()
        self.last_solution_lineage = None

        if self._in_scope_initialize_function is not None:
            self.in_scope_initialize_data = self._in_scope_initialize_function(state)

        for solution in self.call(state.set_x("tree", (tree_info, ), False), tree_info["Tree"]):
            # Remember any disjunction lineages that had a solution
            tree_lineage_binding = state.get_binding("tree_lineage")
            if tree_lineage_binding.value is not None:
                self.solution_lineages.add(tree_lineage_binding.value[0])

            yield solution

        if self.last_solution_lineage is None:
            self.lineage_failure_callback(self.get_error_info())
        else:
            self.handle_lineage_change("")

        pipeline_logger.debug(f"Error after tree evaluation: {self.get_error_info()}")

    def gather_tree_metadata(self):
        self._variable_metadata = perplexity.tree.gather_predication_metadata(self.vocabulary, self.tree_info)

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
                # This is a list of predications, so they should be
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
            last_predication_runtime_settings = self._predication_runtime_settings
            self._predication_index = term.index
            self._predication = term
            self._predication_runtime_settings = {}

            # The first thing in the list was not a list
            # so we assume it is just a term like
            # ["_large_a_1", "e1", "x1"]
            # evaluate it using CallPredication
            yield from self._call_predication(state, term, normalize)

            # Restore it since we are recursing
            self._predication_index = last_predication_index
            self._predication = last_predication
            self._predication_runtime_settings = last_predication_runtime_settings

    # Do not use directly.
    # Use Call() instead so that the predication index is set properly
    # The format we're using is:
    # ["folder_n_of", "x1"]
    #   The first item is the predication name
    #   The rest of the items are the arguments
    def _call_predication(self, state, predication, normalize=False):
        if logger.isEnabledFor(logging.DEBUG):
            logger.debug(f"call {self._predication_index}: {predication}, state=({str(state)}) [{self._phrase_type}]")

        bindings = []
        for arg_index in range(0, len(predication.args)):
            if predication.arg_types[arg_index] in ["c", "h"]:
                bindings.append(predication.args[arg_index])

            else:
                bindings.append(state.get_binding(predication.args[arg_index]))

        # Look up the actual Python module and
        # function name given a string like "folder_n_of".
        # "vocabulary.Predication" returns a two-item list,
        # where item[0] is the module and item[1] is the function

        # TODO: Make this part work with the new scheme
        assert normalize is False

        module_function = self._interpretation[predication.index]

        # for module_function in self.vocabulary.predications(predication.name,
        #                                                     predication.arg_types,
        #                                                     self._phrase_type):

        # sys.modules[] is a built-in Python list that allows you
        # to access actual Python Modules given a string name
        module = sys.modules[module_function.module]

        # Functions are modeled as properties of modules in Python
        # and getattr() allows you to retrieve a property.
        # So: this is how we get the "function pointer" to the
        # predication function we wrote in Python
        function = getattr(module, module_function.function)

        # [list] + [list] will return a new, combined list
        # in Python. This is how we add the state object
        # onto the front of the argument list
        function_args = [self, state] + bindings

        # See if the system wants us to tack any arguments to the front
        if module_function.extra_arg is not None:
            function_args = module_function.extra_arg + function_args

        # If a MessageException happens during execution,
        # convert it to an error
        try:
            # You call a function "pointer" and pass it arguments
            # that are a list by using "function(*function_args)"
            # So: this is actually calling our function (which
            # returns an iterator and thus we can iterate over it)
            had_solution = False
            for next_state in function(*function_args):
                had_solution = True
                tree_lineage_binding = next_state.get_binding("tree_lineage")
                if tree_lineage_binding.value is not None:
                    self.handle_lineage_change(tree_lineage_binding.value[0])

                yield next_state
                # had_solution = True
                # tree_lineage_binding = next_state.get_binding("tree_lineage")
                # tree_lineage = "" if tree_lineage_binding.value is None else tree_lineage_binding.value[0]
                # new_lineage = f"{tree_lineage}.{module_function.id}"
                # yield next_state.set_x("tree_lineage", (new_lineage,))

            if not had_solution:
                if self._predication_runtime_settings.get("Disjunction", False):
                    self.lineage_failure_callback(self.get_error_info())

        except MessageException as error:
            self.report_error(error.message_object())

    def handle_lineage_change(self, new_lineage):
        if self.last_solution_lineage is not None and new_lineage != self.last_solution_lineage:
            if not new_lineage.startswith(self.last_solution_lineage):
                # Fire an error for every disjunction set that didn't generate a solution
                last_segments = self.last_solution_lineage.split(".")[1:]
                new_segments = new_lineage.split(".")[1:]
                for index in range(len(last_segments)):
                    if index > (len(new_segments) - 1) or last_segments[index] != new_segments[index]:
                        # This disjunction changed, fire a failure if there were no solutions
                        test_lineage = ".".join(last_segments[:index + 1])
                        was_successful = False
                        for successful_lineage in self.solution_lineages:
                            if successful_lineage.startswith(test_lineage):
                                was_successful = True
                                break

                        if not was_successful:
                            self.lineage_failure_callback(self.get_error_info())

        # And remember this as the last lineage
        self.last_solution_lineage = new_lineage

    def set_disjunction(self):
        self.set_predication_runtime_settings("Disjunction", True)

    def set_predication_runtime_settings(self, key, value):
        self._predication_runtime_settings[key] = value

    # Replace scopal arguments with an "h" and simply
    # return the others
    def arg_types_from_call(self, predication):
        arg_types = []
        for arg_index in range(0, len(predication.args)):
            if predication.arg_names is not None:
                arg_name = predication.arg_names[arg_index]

            arg = predication.args[arg_index]
            if arg_name is not None and arg_name == "CARG":
                arg_types.append("c")
            else:
                if isinstance(arg, str):
                    arg_types.append(arg[0])
                else:
                    arg_types.append("h")

        return arg_types

    def set_in_scope_function(self, func, initialize_func = None):
        self._in_scope_function = func
        self._in_scope_initialize_function = initialize_func

    # Test if an object is in scope, by default everything is
    def in_scope(self, state, thing):
        if self._in_scope_function is not None:
            return self._in_scope_function(self.in_scope_initialize_data, state, thing)
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

    def report_error(self, error, force=False):
        self.report_error_for_index(self._predication_index, error, force)

    def error(self):
        return [self._error_predication_index, self._error]

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


logger = logging.getLogger('Execution')
pipeline_logger = logging.getLogger('Pipeline')
