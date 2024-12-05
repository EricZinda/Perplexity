import enum
import itertools
import logging
from copy import copy
from math import inf
import perplexity.predications
import perplexity.execution
from perplexity.set_utilities import count_set, CachedIterable
import perplexity.tree
from perplexity.utilities import plural_from_tree_info, parse_predication_name


def determiner_from_binding(tree_info, binding):
    if binding.variable.determiner is not None:
        return binding.variable.determiner

    else:
        quantifier = perplexity.tree.find_quantifier_from_variable(tree_info["Tree"], binding.variable.name)

        # If this is a wh_phrase, ignore the plurality contribution from "which_q" so that "which files are in this folder"
        # can return "file1.txt" (a single file) instead of "there aren't multiple files in this folder"
        pl_value = plural_from_tree_info(tree_info, binding.variable.name)
        if pl_value == "pl" and quantifier.name not in ["which_q", "_which_q"]:
            # Plural determiner, mark this as coming from the quantifier for error reporting purposes
            return VariableCriteria(quantifier,
                                    binding.variable.name,
                                    min_size=2,
                                    max_size=float('inf'))

        elif pl_value == "sg":
            # Singular determiner, mark this as coming from the quantifier for error reporting purposes
            return VariableCriteria(quantifier,
                                    binding.variable.name,
                                    min_size=1,
                                    max_size=1)


def quantifier_from_binding(state, binding):
    return binding.variable.quantifier


# Needs to be called before all_plural_groups_stream. Allows the caller to
# Gather useful stats that all_plural_groups_stream also consumes
def plural_groups_stream_initial_stats(execution_context, var_criteria):
    variable_metadata = {}
    for criteria in var_criteria:
        variable_metadata[criteria.variable_name] = execution_context.get_variable_metadata(criteria.variable_name)

    # Create the initial stats
    initial_stats_group = StatsGroup()
    has_global_constraint, variable_has_inf_max = initial_stats_group.initialize(var_criteria)

    return variable_metadata, initial_stats_group, has_global_constraint, variable_has_inf_max


# Returns a (possibly different) solution group that meets the code criteria
# or None if the incoming group does not meet the criteria
def check_group_against_code_criteria(execution_context, handlers, optimized_criteria_list, index_predication, group):
    phase2_context = execution_context.create_phase2_context()
    created_solution_group, group_list, next_best_error_info = run_handlers(phase2_context,
                                                                            handlers,
                                                                            optimized_criteria_list,
                                                                            group,
                                                                            index_predication)

    if created_solution_group is None:
        pipeline_logger.debug(f"No solution group handlers, or none handled it: just do the default behavior")
        return group_list, next_best_error_info

    elif isinstance(created_solution_group, (tuple, list)) and len(created_solution_group) == 0:
        pipeline_logger.debug(f"Handler said this is not a valid solution group. best error: {next_best_error_info}")
        return None, next_best_error_info

    else:
        pipeline_logger.debug(f"Handler said this is a valid solution group")
        return created_solution_group, next_best_error_info


# If a handler:
# 1. yields len([...]) > 0 -> Says the group is a solution, provides a (potentially different) solution group, stop further processing
# 2. doesn't yield and:
#   - report_error("formNotUnderstood") then it means the group handler was N/A, ignore the handler and continue trying others
#   - report_error(any other error): it means fail this solution and stop further processing. We understood and failure with this error is the right answer
#
# Why is this different from a predication which simply yields a value for success or returns without yielding for failure?
#   The solution group has already passed phase 1 and has been checked to meet phase 2 criteria.  The group
#   handler is designed for actually "doing whatever we should do" with the solution group
#   If we treated handlers as "Solution Group Interpretations"
#
# Errors:
# - Handlers will be run against one solution group, and they are all operating off of the same tree
#   so, since the tree is the same, we can use the same "deepest error logic" to return the best error
def run_handlers(execution_context, handlers, variable_constraints, group, index_predication):
    # Remember the initial error information because we may need to reset it if we run multiple handlers
    initial_error_info = execution_context.get_error_info()
    state_list = CachedIterable(group)
    if len(handlers) > 0:
        pipeline_logger.debug(f"Running {len(handlers)} solution group handlers")

        for is_predication_handler_name in handlers:
            execution_context.set_error_info(initial_error_info)
            handler_function = is_predication_handler_name[1]
            if is_predication_handler_name[0]:
                # This is a predication-style solution group handler
                # Build up an arg structure to call the predication with that
                # has the same arguments as the normal predication but has a list for each argument that represents the solution group
                handler_args = []
                for arg_index in range(len(index_predication.args)):
                    arg = index_predication.args[arg_index]
                    found_constraint = None
                    for constraint in variable_constraints:
                        if constraint.variable_name == arg:
                            found_constraint = constraint
                            break
                    if found_constraint is None:
                        found_constraint = VariableCriteria(index_predication, arg)
                    handler_args.append(GroupVariableValues(found_constraint, state_list, index_predication.argument_types()[arg_index], arg))

                handler_args = [execution_context, state_list] + handler_args

            else:
                handler_args = (execution_context, state_list) + (variable_constraints, )

            debug_name = is_predication_handler_name[2][0] + "." + is_predication_handler_name[2][1]
            pipeline_logger.debug(f"Running {debug_name} solution group handler")
            created_solution_group = None

            # Start with a cleared error context so we properly capture any initial errors
            execution_context.clear_error()

            # Continue to clear the error context every time we are successful so that old errors don't bleed into
            # the next call
            for next_solution_group in perplexity.execution.clear_error_when_yield_generator(execution_context, handler_function(*handler_args)):
                assert not (isinstance(next_solution_group, (tuple, list)) and len(next_solution_group) == 0), \
                    f"yielded value from solution group {debug_name} must be a tuple or list where len() > 0. Was: {str(next_solution_group)}"
                created_solution_group = next_solution_group
                pipeline_logger.debug(f"{debug_name} succeeded")
                break

            # First solution_group handler that yields, wins
            if created_solution_group:
                pipeline_logger.debug(f"{debug_name} succeeded. No more solution group handlers will be run.")
                break

            else:
                if execution_context.has_not_understood_error():
                    # That handler was N/A for this solution group, keep trying
                    pipeline_logger.debug(f"{debug_name} reported formNotUnderstood, trying alternative solution group handlers...")

                else:
                    # Return an empty solution group to indicate failure
                    # The error context will contain any error generated by the handler
                    pipeline_logger.debug(f"{debug_name} failed. No more solution group handlers will be run.")
                    created_solution_group = []
                    break

        pipeline_logger.debug(f"Done trying solution group handlers, best error: {execution_context.get_error_info()}")
        return created_solution_group, state_list, execution_context.get_error_info()

    else:
        return None, state_list, perplexity.execution.ExecutionContext.blank_error_info()


# Support iterating over just one variable value from a state iterator but
# without materializing all the states up front
class GroupVariableIterable(object):
    class GroupVariableIterator(object):
        def __init__(self, state_iterator, static_value=None, variable_name=None):
            self._state_iterator = state_iterator
            self._static_value = static_value
            self._variable_name = variable_name

        def __next__(self):
            # Call next_state even if we're not going to use it so we quit iterating when
            # we are out of values
            next_state = next(self._state_iterator)
            if self._static_value is not None:
                return self._static_value
            else:
                return next_state.get_binding(self._variable_name)

    def __init__(self, state_iterable, static_value=None, variable_name=None):
        self._state_iterable = state_iterable
        self._static_value = static_value
        self._variable_name = variable_name

    def __iter__(self):
        return GroupVariableIterable.GroupVariableIterator(self._state_iterable.__iter__(), self._static_value, self._variable_name)

    def __getitem__(self, key):
        # Even if we aren't using it, make sure this index exists by accessing it
        state = self._state_iterable[key]
        if self._static_value is not None:
            return self._static_value
        else:
            return state.get_binding(self._variable_name)


class GroupVariableValues(object):
    def __init__(self, variable_constraints, state_iterable, arg_type, arg_value):
        self.variable_constraints = variable_constraints

        if arg_type in ["c", "h"]:
            # returns arg_value for every state
            self.solution_values = GroupVariableIterable(state_iterable=state_iterable, static_value=arg_value)

        else:
            # return get_binding(arg_value) for every state
            self.solution_values = GroupVariableIterable(state_iterable=state_iterable, variable_name=arg_value)


class GroupSet(object):
    def __init__(self, stats_group, raw_set, set_id, final_set=None):
        self.stats_group = stats_group
        self.raw_set = raw_set
        self.set_id = set_id
        self.final_set = final_set


# Run solution_group code within all_plural_groups_stream2() so that failed solution groups cause the right alternative sets to be created
# Problems:
#     - SingleGroupGenerator assumes that, if it gets a new group with the same lineage, that there will be *more* records in it
#         - and furthermore that the records that we already returned are still there
#     - Neither is true anymore because the group handler can completely swap things out
def all_plural_groups_stream(execution_context, solutions, var_criteria, variable_metadata, initial_stats_group, has_global_constraint,
                              handlers, optimized_criteria_list, index_predication):
    # Give a unique set_id to every group that gets created
    set_id = 0
    sets = []
    set_id += 1

    def initial_empty_set():
        return GroupSet(stats_group=initial_stats_group, raw_set=[], set_id=str(set_id), final_set=[])

    # Track solution groups that work so far, but need to wait till the end
    # because they require a global criteria to be true
    pending_global_criteria = []

    # When we know we have failed early (early_fail_quit)
    early_fail_quit = False
    for next_solution in solutions:
        if groups_logger.level == logging.DEBUG:
            groups_logger.debug(f"Processing solution: {next_solution}")
        new_sets = []
        next_solution_was_merged = False
        for existing_group_set in sets + [initial_empty_set()]:
            testing_initial_set = len(existing_group_set.raw_set) == 0
            if testing_initial_set and next_solution_was_merged:
                # Don't create a brand-new set by merging with the final empty set if this solution was
                # already merged into another set. Because: this solution is already being tracked.
                continue

            new_set_stats_group = existing_group_set.stats_group.copy()
            merge, state = check_criteria_all(execution_context, var_criteria, new_set_stats_group, next_solution)
            if groups_logger.level == logging.DEBUG and state in [CriteriaResult.fail_one, CriteriaResult.fail_all]:
                nl = "\n     "
                groups_logger.debug(f"Solution group state: {state} \n     {nl.join(str(x) for x in (existing_group_set.raw_set + [next_solution]))}")

            if state == CriteriaResult.fail_one:
                # Fail (doesn't meet criteria): don't add, don't yield
                continue

            elif state == CriteriaResult.fail_all:
                # A global criteria wasn't met so none will ever work
                # Still run global constraints to get a good error
                early_fail_quit = True
                break

            else:
                # Didn't fail, now check against any code criteria to make sure it really did succeed
                raw_set = existing_group_set.raw_set + [next_solution]
                code_criteria_failed = False
                final_set = None
                if state == CriteriaResult.meets:
                    if groups_logger.level == logging.DEBUG:
                        nl = "\n     "
                        groups_logger.debug(
                            f"Pre-code criteria Solution group raw (merged = {merge}): {state} \n     {nl.join(str(x) for x in raw_set)}")

                    final_set = raw_set

                # Decide whether to merge into the existing set or create a new one
                # Merge if the only variables that got updated had a criteria with an upper bound of inf
                # since alternatives won't be used anyway because the inf means that any set > lower bound is a solution
                # and thus these sets will only get merged later anyway, they are all subsets of the same base solution group
                # so generating alternatives will just cause more processing
                # However, if the code criteria failed, it means that this particular set is not a solution group
                # Thus it is either a contender or a failure.
                # Leaving it as a contender is safest since the worst that will happen is we do some extra processing.
                #   Removing it altogether could cause us to miss a solution group and affect correctness.
                # Furthermore, we can stop merging and again, we'll just end up processing extra stuff by producing more combinations than we needed
                #   Whereas continuing to merge might miss some alternatives that should be generated
                # So, because this failed, it means we stop this "merging optimization" and try the alternatives, even though it might be slower, so we
                #   don't miss any cases
                # Also, don't ever "merge" into the intial set because it means that all other solutions will be tracked
                # as a lineage since the initial set is the base for everything
                if merge and not code_criteria_failed and not testing_initial_set:
                    next_solution_was_merged = True
                    new_group_set = existing_group_set
                    if len(existing_group_set.raw_set) == 0:
                        new_sets.append(new_group_set)

                else:
                    new_group_set = GroupSet(stats_group=None, raw_set=None, set_id=existing_group_set.set_id + ":" + str(set_id))
                    set_id += 1
                    new_sets.append(new_group_set)

                new_group_set.stats_group = new_set_stats_group
                new_group_set.raw_set = raw_set
                new_group_set.final_set = final_set

                if groups_logger.level == logging.DEBUG:
                    nl = "\n     "
                    groups_logger.debug(f"Solution group raw (merged: {next_solution_was_merged}): {state} \n     {nl.join(str(x) for x in new_group_set.raw_set)}")

                if state == CriteriaResult.meets:
                    # Clear any errors that occurred trying to generate solution groups that didn't work
                    # so that the error that gets returned is whatever happens while *processing* the solution group
                    execution_context.clear_error()
                    yield new_group_set.final_set, new_group_set.set_id, new_group_set.stats_group, new_group_set.raw_set

                elif state == CriteriaResult.meets_pending_global:
                    # Remember the values we would have yielded it if it had met the criteria
                    pending_global_criteria.append([new_group_set.raw_set, new_group_set.set_id, new_group_set.stats_group, new_group_set.raw_set])

                elif state == CriteriaResult.contender:
                    # Not yet a solution, don't track it as one
                    pass

        sets += new_sets

        if early_fail_quit:
            break

    # If early_fail_quit is True, the error should already be set
    if not early_fail_quit and has_global_constraint and len(pending_global_criteria) > 0:
        for criteria in var_criteria:
            if not criteria.meets_global_criteria(execution_context):
                if groups_logger.level == logging.DEBUG:
                    nl = "\n     "
                    groups_logger.debug(f"Didn't meet global criteria: {criteria}")
                return

        # Clear any errors that occurred trying to generate solution groups that didn't work
        # so that the error that gets returned is whatever happens while *processing* the solution group
        execution_context.clear_error()

        for pending in pending_global_criteria:
            final_group = pending[0]
            if final_group:
                # Convert from whatever object to a real list
                final_group = [x for x in final_group]
                yield final_group, pending[1], pending[2], pending[3]

            else:
                # Fail (doesn't meet code criteria): don't add, don't yield
                continue


class StatsGroup(object):
    def __init__(self, variable_has_inf_max=False, group_state=None, merge=False):
        self.variable_stats = []
        self.variable_has_inf_max = variable_has_inf_max
        self.group_state = group_state
        self.merge = merge

    def __repr__(self):
        return ",".join([f"({str(x)})" for x in self.variable_stats])

    def initialize(self, var_criteria):
        has_global_constraint = False
        previous_variable_stats = None
        self.variable_has_inf_max = False
        self.group_state = None
        for criteria in var_criteria:
            if criteria.global_criteria is not None:
                has_global_constraint = True

            if criteria.max_size == float('inf'):
                self.variable_has_inf_max = True

            var_stats = VariableStats(criteria.variable_name)
            var_stats.prev_variable_stats = previous_variable_stats
            if previous_variable_stats is not None:
                previous_variable_stats.next_variable_stats = var_stats
                var_stats.distributive_state = CriteriaResult.contender
                var_stats.collective_state = CriteriaResult.contender
                var_stats.cumulative_state = CriteriaResult.contender
            else:
                var_stats.distributive_state = CriteriaResult.fail_one
                var_stats.collective_state = CriteriaResult.contender
                var_stats.cumulative_state = CriteriaResult.fail_one

            previous_variable_stats = var_stats
            self.variable_stats.append(var_stats)

        return has_global_constraint, self.variable_has_inf_max

    def copy(self):
        new_group = StatsGroup(self.variable_has_inf_max, self.group_state, self.merge)
        previous_new_stat = None
        for stat in self.variable_stats:
            new_stat = VariableStats(stat.variable_name,
                                     stat.whole_group_unique_individuals.copy(),
                                     stat.whole_group_unique_values.copy(),
                                     stat.distributive_state,
                                     stat.collective_state,
                                     stat.cumulative_state,
                                     stat.variable_value_type,
                                     stat.only_single_values)
            new_stat.prev_variable_stats = previous_new_stat
            if previous_new_stat is not None:
                previous_new_stat.next_variable_stats = new_stat
            new_group.variable_stats.append(new_stat)
            previous_new_stat = new_stat

        return new_group

    def only_instances(self):
        for stat in self.variable_stats:
            if perplexity.predications.value_type(stat) != perplexity.predications.VariableValueType.instance:
                return False
        return True

    # Return the index (or None) for the neg() predication that
    # negated this variable
    def negated_index_for_variable(self, negated_variable_name):
        return None


class VariableStats(object):
    def __init__(self,
                 variable_name,
                 whole_group_unique_individuals=None,
                 whole_group_unique_values=None,
                 distributive_state=None,
                 collective_state=None,
                 cumulative_state=None,
                 variable_value_type=None,
                 only_single_values=None):
        self.variable_name = variable_name
        self.whole_group_unique_individuals = set() if whole_group_unique_individuals is None else whole_group_unique_individuals
        self.whole_group_unique_values = {} if whole_group_unique_values is None else whole_group_unique_values
        self.prev_variable_stats = None
        self.next_variable_stats = None
        self.current_state = None

        self.distributive_state = None if distributive_state is None else distributive_state
        self.collective_state = None if collective_state is None else collective_state
        self.cumulative_state = None if cumulative_state is None else cumulative_state
        self.variable_value_type = variable_value_type
        self.only_single_values = only_single_values

    def __repr__(self):
        soln_modes = self.solution_modes()
        contenders_modes = []
        contenders_modes += ["dist"] if self.distributive_state == CriteriaResult.contender else []
        contenders_modes += ["coll"] if self.collective_state == CriteriaResult.contender else []
        contenders_modes += ["cuml"] if self.cumulative_state == CriteriaResult.contender else []

        return f"var={self.variable_name}, soln={','.join(soln_modes)}, cont={','.join(contenders_modes)}, values={len(self.whole_group_unique_values)}, ind={len(self.whole_group_unique_individuals)}"

    def solution_modes(self):
        solution_modes = []
        solution_modes += ["dist"] if (self.distributive_state == CriteriaResult.meets or self.distributive_state == CriteriaResult.meets_pending_global) else []
        solution_modes += ["coll"] if (self.collective_state == CriteriaResult.meets or self.collective_state == CriteriaResult.meets_pending_global) else []
        solution_modes += ["cuml"] if (self.cumulative_state == CriteriaResult.meets or self.cumulative_state == CriteriaResult.meets_pending_global) else []
        return tuple(solution_modes)

    # Check if this variable will be a valid coll/dist/cuml variable after
    # adding this solution to the group this stats object is tracking
    # Succeeds if the group, only considering this variable, can be interpreted as any (or multiple) of
    # cumulative/collective/distributive across all variables
    def add_solution(self, execution_context, variable_criteria, solution):
        binding_value = solution.get_binding(self.variable_name).value

        # Solutions can't have different types of values in the same solution group
        binding_value_type = perplexity.predications.value_type(binding_value[0])
        is_instance_solution = binding_value_type == perplexity.predications.VariableValueType.instance
        if len(self.whole_group_unique_individuals) == 0:
            # This is the first value, so nothing has to match
            self.variable_value_type = binding_value_type

        elif self.variable_value_type != binding_value_type:
            assert False, "Concepts and instances should never be generated in the same solution set since they should be created by a disjunction formed by different noun() predications"

        # See if this binding_value has any *individuals* we haven't seen yet and track them
        if any([x not in self.whole_group_unique_individuals for x in binding_value]):
            new_individuals = True
            self.whole_group_unique_individuals.update(binding_value)

        else:
            new_individuals = False

        next_value = None if self.next_variable_stats is None else solution.get_binding(self.next_variable_stats.variable_name).value

        # Update the unique *set values* mapping that is used for distributive readings
        # Add the *individuals* of the next variable value to the *set value* of this variable
        # This is done by maintaining self.whole_group_unique_values which is a dict that contains
        # each set value as a key, with a value that is a list of the values the next variable has
        # This data will be used *by the next variable* not by this one. It is just maintained by this one
        if binding_value not in self.whole_group_unique_values:
            if self.only_single_values is None:
                # Haven't decided if we are singles or sets of two or more yet, so this decides it
                self.only_single_values = len(binding_value) == 1
            elif (self.only_single_values and len(binding_value) > 1) or \
                    (not self.only_single_values and len(binding_value) == 1):
                # Don't allow a mix of sets of 1 and sets > 1
                self.current_state = CriteriaResult.fail_one
                return new_individuals, self.current_state

            self.whole_group_unique_values[binding_value] = [set(next_value if next_value is not None else []), [solution]]
        else:
            self.whole_group_unique_values[binding_value][0].update(next_value if next_value is not None else [])
            self.whole_group_unique_values[binding_value][1].append(solution)

        # See if there are any required_values criteria and make sure we meet them
        required_values_state = variable_criteria.meets_required_values_criteria(self.whole_group_unique_individuals, self.whole_group_unique_values)
        if required_values_state in [CriteriaResult.fail_one, CriteriaResult.fail_all]:
            self.current_state = required_values_state
            return new_individuals, required_values_state

        # Now we actually compare this variable to the previous value to see what kind of plural type this might be
        if not is_instance_solution:
            # This variable is a concept: do the one sanity check we can do: if there are more concepts
            # than the criteria allows, it can't possibly work

            # Otherwise: we assume it meets the numeric criteria
            # and allow the group handler to finalize the decision
            sanity_check = variable_criteria.meets_criteria(execution_context,
                                                                     self.whole_group_unique_individuals)
            if sanity_check in [CriteriaResult.fail_one, CriteriaResult.fail_all]:
                self.current_state = sanity_check
            else:
                self.current_state = required_values_state

            return new_individuals, self.current_state

        else:
            # This variable is an instance
            if self.prev_variable_stats is None:
                prev_unique_value_count = None
            else:
                prev_unique_value_count = len(self.prev_variable_stats.whole_group_unique_values)

            if prev_unique_value_count is not None and self.prev_variable_stats.variable_value_type != perplexity.predications.VariableValueType.instance:
                # Not used if the previous value is conceptual since all 3 modes might work
                only_collective = None

                # The *previous* variable is a concept, so we will pretend it meets the criteria for anything. Thus:
                # If this variable's values meets its own criteria, it could possibly be collective or cuml
                self.cumulative_state = variable_criteria.meets_criteria(execution_context, self.whole_group_unique_individuals)
                self.collective_state = self.cumulative_state

                # For distributive: Since the *previous* variable is a concept, we just need to prove there is *some number of previous values*
                # that would allow the current variable's unique values to be broken up and match the distributive pattern. The groups it gets broken
                # up into still have to meet this variables criteria, with no remainder.
                #   *** Note that we have to use this variable's *unique_values*, and not unique_individuals, because the unique values can't be broken up
                #       and assigned to different previous values since they are "together"
                # The groups it is divided into must be between self.min_size and self.max_size
                # Since this variable has a min size, we know that every group we find must satisfy min_size for this variable.
                # Furthermore, we need to count the *individuals* for a given group, not the unique values since this is distributive.
                #
                # Since the bins are all the same size, if the unique values are all size one, we can do this quickly.
                #   If we divide this variable's unique_values by self.min_size, we have the min count that the previous variable must be
                #   (given the values we have now) and a remainder.
                #   If the min count is > 0 and the remainder is <= (the distance between min and max) * number of groups, it works
                #   and this could be a valid distributive group assuming the concepts are interpreted with the value we came up with

                # If there are unique values that are > 1 it becomes a variant of the online bin packing problem, where the
                # bins have a lower bound AND an upper bound (usually).
                #   Given that we don't care how many bins (i.e. previous variable unique values) are required to make this distributive,
                #   just that it *can* be done, we can use a variant of the first fit online algorithm which is Θ(n log n). Basically: fit each item into
                #   the first bin it fits in. Sort the items from largest to smallest and then fit all the items > 1 into their own bin, and then fill the remaining
                #   with the items of size 1.
                # Sample list of tuples
                unique_value_count = len(self.whole_group_unique_values)
                sorted_whole_group_unique_values = sorted(self.whole_group_unique_values, key=len, reverse=True)
                if len(sorted_whole_group_unique_values[0]) == 1:
                    # All unique values have only one element, this is the easy approach
                    group_count = int(unique_value_count / variable_criteria.min_size)
                    if group_count > 0:
                        # It can at least be broken up such that it fills the min_size for each previous value,
                        # if there are group_count previous values. Remember that we just have to find *any* solution that works
                        # since the previous value is a concept
                        if variable_criteria.max_size == float(inf):
                            # Since every variable can contain any number of more unique values, it has to work
                            self.distributive_state = CriteriaResult.meets
                        else:
                            _, remainder = divmod(unique_value_count, variable_criteria.min_size)
                            min_max_delta = variable_criteria.max_size - variable_criteria.min_size
                            if remainder <= min_max_delta * group_count:
                                # The remainder can be divided into the groups and keep them all under the max
                                self.distributive_state = CriteriaResult.meets
                            else:
                                # Too much remainder. If we add more solutions it'll divide evenly, as long as there
                                # is some min_max_delta to absorb the extras. So: contender
                                if min_max_delta > 0:
                                    self.distributive_state = CriteriaResult.contender
                                else:
                                    self.distributive_state = CriteriaResult.fail_one
                else:
                    # at least one unique values has > 1 item, this is the harder approach:
                    result = self.is_concept_distributive(self.whole_group_unique_values, variable_criteria.min_size, variable_criteria.max_size)
                    if result is None:
                        # This will never work since there are values that don't meet the criteria
                        self.distributive_state = CriteriaResult.fail_one
                    elif result is True:
                        self.distributive_state = CriteriaResult.meets
                    elif result is False:
                        self.distributive_state = CriteriaResult.contender
            else:
                # This variable is an instance and the *previous* variable is an instance
                only_collective = prev_unique_value_count is None or prev_unique_value_count == 1
                if not only_collective:
                    # Collective fails from here on out because prev_unique_value_count > 1
                    self.collective_state = CriteriaResult.fail_one

                    # Cumulative
                    if self.cumulative_state != CriteriaResult.fail_one:
                        self.cumulative_state = variable_criteria.meets_criteria(execution_context, self.whole_group_unique_individuals)

                    # Distributive
                    # for each prev_unique_value: len(unique_values) meets criteria
                    if self.distributive_state != CriteriaResult.fail_one:
                        self.distributive_state = CriteriaResult.meets
                        for prev_unique_value_item in self.prev_variable_stats.whole_group_unique_values.items():
                            distributive_value_state = variable_criteria.meets_criteria(execution_context, prev_unique_value_item[1][0])
                            self.distributive_state = criteria_transitions[self.distributive_state][distributive_value_state]
                            if self.distributive_state == CriteriaResult.fail_one:
                                break

                else:
                    if self.collective_state != CriteriaResult.fail_one:
                        # Collective
                        self.collective_state = variable_criteria.meets_criteria(execution_context, self.whole_group_unique_individuals)

            # Now figure out what to return
            # If the previous variable is conceptual all 3 modes may be supported
            # Go through the possible states in an order that
            self.current_state = None
            for test_state in [CriteriaResult.fail_all, CriteriaResult.meets_pending_global, CriteriaResult.meets, CriteriaResult.contender]:
                if ((not is_instance_solution or only_collective) and self.collective_state == test_state) or \
                        ((not is_instance_solution or not only_collective) and
                            (self.distributive_state == test_state or
                             self.cumulative_state == test_state)):
                    # Merge together the results from the required_values and the test_state
                    if required_values_state == CriteriaResult.contender:
                        if test_state == CriteriaResult.meets:
                            self.current_state = CriteriaResult.contender
                        else:
                            self.current_state = test_state

                    elif required_values_state == CriteriaResult.meets:
                        if test_state == CriteriaResult.meets:
                            self.current_state = CriteriaResult.meets
                        else:
                            self.current_state = test_state

                    else:
                        assert False, "should never get here"

                    break

            if self.current_state is None:
                self.current_state = CriteriaResult.fail_one

            return new_individuals, self.current_state

    # Try all combinations of values in buckets by:
    # - Create a new bucket
    # - Try one way of filling it that makes it min <= size <= max
    # - Recurse
    # - if it didn't work, try the next way of filling it
    # - it we run out of values, we succeed
    # - if you did all combinations, we fail
    # Note that we don't care what the buckets are, just that the items were able to be placed in them
    # and meet the criteria
    def is_concept_distributive(self, unique_values, min, max):
        unique_value_sizes = []
        for value in unique_values:
            size = len(value)
            if size > max:
                return None
            else:
                unique_value_sizes.append(size)
        return self.is_concept_distributive_impl(unique_value_sizes, min, max)

    def is_concept_distributive_impl(self, unique_values_sizes, min, max):
        if len(unique_values_sizes) == 0:
            return True

        # Given that each unique_item is at least 1 item, the most combinations
        # we need to try is max (unless max == inf)
        combinations = len(unique_values_sizes) + 1 if max is inf else max
        for i in range(1, combinations):
            for combo in itertools.combinations(unique_values_sizes, i):
                if min <= sum(combo) <= max:
                    new_values = copy(unique_values_sizes)
                    for value in combo:
                        new_values.remove(value)
                    if self.is_concept_distributive_impl(new_values, min, max):
                        return True

        return False


# Distributive needs to create groups by unique variable value
# Every set needs set[0] to be a dict that tracks the shape of the set when a new row is added
# we yield a set when its shape is a valid coll/dist/cuml shape
# for each level, the shape needs to track:
#   How many unique values of x across the whole set
#   How many unique individuals of x across the whole set
#   How many unique individuals of x per previous variable unique value
#
#   So this means that each variable tracks:
#       whole_group_unique_individuals
#       whole_group_unique_values
#           solutions that go with each unique_value
#
#   A given set is a solution if every variable is a cum/dst/col solution
#   A given x is a cum/dst/col solution if:
#       collective if len(prev_unique_values) == 1 and len(unique_values) meets criteria
#       distributive if len(prev_unique_values) > 1 and for each prev_unique_value: len(unique_values) meets criteria
#       cumulative if len(prev_unique_values) > 1 and len(unique_values) meets criteria
def check_criteria_all(execution_context, var_criteria, new_set_stats_group, new_solution):
    current_set_state = CriteriaResult.meets
    merge = True
    for index in range(len(var_criteria)):
        # Get the existing statistics for the variable at this index
        # and the criteria for the variable as well
        variable_stats = new_set_stats_group.variable_stats[index]

        state = None
        if perplexity.tree.is_variable_scoped_by_negation(new_solution, variable_stats.variable_name):
            # This variable is under a neg() predication at negated_index,
            # This means its plurals were already evaluated by neg(), and because it is here, they must be true
            state = CriteriaResult.meets
            # TODO: should new_individuals be getting updated?
            new_individuals = None

        if state is None:
            criteria = var_criteria[index]

            # See what the CriteriaResult is for the whole solution group plus the new solution
            # but only for this particular variable
            new_individuals, state = variable_stats.add_solution(execution_context, criteria, new_solution)

        # Decide the new state of the entire solution group, so far, based on the previous variable
        # state and the new state
        current_set_state = criteria_transitions[current_set_state][state]
        if current_set_state == CriteriaResult.fail_one or current_set_state == CriteriaResult.fail_all:
            new_set_stats_group.group_state = current_set_state
            new_set_stats_group.merge = merge
            return None, current_set_state

        # If the value in new_solution for the current variable added a new value to the set of values
        # being tracked by a variable without an upper bound of inf, then we need to create a new group
        # because we need to generate alternatives from it
        # OR if this variable is not an instance, don't merge either so we get all the alternatives
        if new_individuals and criteria.max_size != float('inf'):
            merge = False

    new_set_stats_group.group_state = current_set_state
    new_set_stats_group.merge = merge
    return merge, current_set_state


# Called if we can shortcut because we have already found the answers but we still need to check global constraints.
# The set of unique individuals needed to check that "only 2 ..." are collected is in the criteria
# So we can rip through all the solutions and run the criteria to see if global criteria are met, ignoring coll/etc.
def check_only_global_criteria_all(execution_context, var_criteria, new_solution):
    for index in range(len(var_criteria)):
        criteria = var_criteria[index]
        binding_value = new_solution.get_binding(criteria.variable_name).value
        criteria_state = criteria.meets_criteria(execution_context, binding_value)
        if criteria_state == CriteriaResult.fail_all:
            False

    return True


class NegatedPredication(object):
    def __init__(self, predication, scoped_variables):
        self.predication = predication
        self.scoped_variables = scoped_variables

    def __repr__(self):
        return str(self.predication)


# if global_criteria is not set, then this only guarantees that the min and max size will be retained
# within a particular solution group. The count of that item *across* groups could be bigger.
class VariableCriteria(object):
    def __init__(self, predication, variable_name, min_size=1, max_size=float('inf'), global_criteria=None, required_values=None):
        self.predication_index = predication.index
        self.predication = predication
        self.variable_name = variable_name
        self.min_size = min_size
        self.max_size = max_size
        self.required_values = required_values
        self._unique_rstrs = set()
        self.global_criteria = global_criteria
        self._after_phrase_error_location = ["AfterFullPhrase", self.variable_name]
        if parse_predication_name(predication.name)["Pos"] == "q":
            self._predication_error_location = ["AtPredication", predication.args[2], variable_name]
        else:
            self._predication_error_location = ["AtPredication", predication, variable_name]

    def __repr__(self):
        return f"{{{self.variable_name}: min={self.min_size}, max={self.max_size}, global={self.global_criteria}, required_values={self.required_values}, pred={self.predication.name}({self.predication.args[0]})}}"

    def meets_criteria(self, execution_context, value_list):
        values_count = count_set(value_list)

        # Check global criteria
        if self.global_criteria:
            # "Only/Exactly", much like the quantifier "the", does more than just group solutions into groups
            # ("only 2 files are in the folder") it also limits *all* the solutions to that number.
            # So we need to track unique values across all answers in this case
            # BUT: Only track instances because non-instances are handled by the developer manually
            self._unique_rstrs.update([item for item in value_list if perplexity.predications.value_type(item) == perplexity.predications.VariableValueType.instance])

        if self.global_criteria == GlobalCriteria.exactly:
            # We can fail immediately if we have too many
            if len(self._unique_rstrs) > self.max_size:
                # This is definitely the reason why something failed (since we are failing it here), so force=True
                execution_context.report_error_for_index(self.predication_index, ["phase2MoreThanN", self._after_phrase_error_location, self.max_size], force=True, phase=2)
                return CriteriaResult.fail_all

        if self.global_criteria == GlobalCriteria.all_rstr_meet_criteria:
            # We can fail immediately if we have too many
            if len(self._unique_rstrs) > self.max_size:
                # This is definitely the reason why something failed (since we are failing it here), so force=True
                execution_context.report_error_for_index(self.predication_index, ["phase2MoreThanN", self._predication_error_location, self.max_size], force=True, phase=2)
                return CriteriaResult.fail_all

        # Check numeric criteria
        if values_count > self.max_size:
            # It'll never get smaller so it fails forever
            execution_context.report_error_for_index(self.predication_index, ["phase2MoreThan", self._after_phrase_error_location, self.max_size], force=True, phase=2)
            return CriteriaResult.fail_one

        elif values_count < self.min_size:
            execution_context.report_error_for_index(self.predication_index, ["phase2LessThan", self._after_phrase_error_location, self.min_size], force=True, phase=2)
            return CriteriaResult.contender

        else:
            # Meets the numeric criteria
            # values_count >= self.min_size and values_count <= self.max_size
            if self.global_criteria == GlobalCriteria.exactly or self.global_criteria == GlobalCriteria.all_rstr_meet_criteria:
                return CriteriaResult.meets_pending_global

            else:
                return CriteriaResult.meets

    def meets_required_values_criteria(self, unique_individuals_list, unique_values_list):
        if self.required_values is not None:
            # Ensure the values are all singles or a single collective
            if len(unique_values_list) > 1:
                if any([len(x) > 1 for x in unique_values_list]):
                    return CriteriaResult.fail_one

            # See if we have the right individuals
            for value in unique_individuals_list:
                if (value, ) not in self.required_values:
                    return CriteriaResult.fail_one

            if len(unique_individuals_list) == len(self.required_values):
                # This constraint was met, whatever the count said is the answer
                return CriteriaResult.meets

            else:
                # It is a contender for this constraint
                return CriteriaResult.contender
        else:
            return CriteriaResult.meets

    # Only called at the very end after all solutions have been generated
    def meets_global_criteria(self, execution_context):
        if self.global_criteria == GlobalCriteria.all_rstr_meet_criteria:
            all_rstr_values = execution_context.get_variable_execution_data(self.variable_name)["AllRstrValues"]
            if groups_logger.level == logging.DEBUG:
                nl = "\n     "
                groups_logger.debug(f"all rstr values: {nl.join([str(x) for x in all_rstr_values])}")

            if len(all_rstr_values) < self.min_size:
                execution_context.report_error_for_index(self.predication_index, ["phase2LessThan", self._predication_error_location, self.min_size, ], force=True, phase=2)
                return False

            elif len(all_rstr_values) > self.max_size:
                execution_context.report_error_for_index(self.predication_index, ["phase2MoreThan", self._predication_error_location, self.max_size], force=True, phase=2)
                return False

            elif len(all_rstr_values) != len(self._unique_rstrs):
                execution_context.report_error_for_index(self.predication_index, ["phase2NotTrueForAll", self._predication_error_location], force=True, phase=2)
                return False

        if self.global_criteria == GlobalCriteria.exactly or self.global_criteria == GlobalCriteria.all_rstr_meet_criteria:
            # Then check to make sure there were as many in the solution as the user specified
            if groups_logger.level == logging.DEBUG:
                nl = "\n     "
                groups_logger.debug(f"unique rstr values: {nl.join([str(x) for x in self._unique_rstrs])}")

            if len(self._unique_rstrs) < self.min_size:
                execution_context.report_error_for_index(self.predication_index, ["phase2LessThan", self._after_phrase_error_location, self.min_size], force=True, phase=2)
                return False

            elif len(self._unique_rstrs) > self.max_size:
                execution_context.report_error_for_index(self.predication_index, ["phase2MoreThan", self._after_phrase_error_location, self.max_size], force=True, phase=2)
                return False

        return True


class CriteriaResult(enum.Enum):
    # Meets the criteria
    meets = 0,
    # Meets the criteria, as long as the global
    # criteria (like "only 2") for this variable is met
    meets_pending_global = 1
    # has not yet exceeded the criteria, but hasn't meet it. It is a contender.
    contender = 2
    # This set does not meet the criteria, and never will again (since all additions only increase)
    fail_one = 3
    # In some cases like "only 2" we can fail everything because
    # a global criteria wasn't met
    fail_all = 4


class GlobalCriteria(enum.Enum):
    exactly = 0
    # words like "the" and "all" require every RSTR to meet the body
    all_rstr_meet_criteria = 1
    # words like "each" and "every" are said with a singular, but allow 1,inf in the answer
    # so they must do a special transformation when being collapsed
    every_rstr_meet_criteria = 2


# If the previous variable is state x, and this variable is state y, then what is the whole state?
criteria_transitions = {CriteriaResult.meets: {CriteriaResult.meets: CriteriaResult.meets,
                                               CriteriaResult.meets_pending_global: CriteriaResult.meets_pending_global,
                                               CriteriaResult.contender: CriteriaResult.contender,
                                               CriteriaResult.fail_one: CriteriaResult.fail_one,
                                               CriteriaResult.fail_all: CriteriaResult.fail_all},
                        CriteriaResult.meets_pending_global: {CriteriaResult.meets: CriteriaResult.meets_pending_global,
                                                              CriteriaResult.meets_pending_global: CriteriaResult.meets_pending_global,
                                                              CriteriaResult.contender: CriteriaResult.contender,
                                                              CriteriaResult.fail_one: CriteriaResult.fail_one,
                                                              CriteriaResult.fail_all: CriteriaResult.fail_all},
                        CriteriaResult.contender: {CriteriaResult.meets: CriteriaResult.contender,
                                                   CriteriaResult.meets_pending_global: CriteriaResult.contender,
                                                   CriteriaResult.contender: CriteriaResult.contender,
                                                   CriteriaResult.fail_one: CriteriaResult.fail_one,
                                                   CriteriaResult.fail_all: CriteriaResult.fail_all},
                        CriteriaResult.fail_one: {CriteriaResult.meets: CriteriaResult.fail_one,
                                                  CriteriaResult.meets_pending_global: CriteriaResult.fail_one,
                                                  CriteriaResult.contender: CriteriaResult.fail_one,
                                                  CriteriaResult.fail_one: CriteriaResult.fail_one,
                                                  CriteriaResult.fail_all: CriteriaResult.fail_all},
                        CriteriaResult.fail_all: {CriteriaResult.meets: CriteriaResult.fail_all,
                                                  CriteriaResult.meets_pending_global: CriteriaResult.fail_all,
                                                  CriteriaResult.contender: CriteriaResult.fail_all,
                                                  CriteriaResult.fail_one: CriteriaResult.fail_all,
                                                  CriteriaResult.fail_all: CriteriaResult.fail_all}
                        }


groups_logger = logging.getLogger('SolutionGroups')
pipeline_logger = logging.getLogger('Pipeline')
