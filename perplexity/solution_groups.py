import copy
import logging
import sys
from math import inf
from perplexity.plurals import determiner_from_binding, quantifier_from_binding, \
    all_plural_groups_stream, VariableCriteria, GlobalCriteria, plural_groups_stream_initial_stats
from perplexity.response import RespondOperation
from perplexity.tree import gather_quantifier_order, find_predication_from_introduced
from perplexity.utilities import at_least_one_generator


class SingleSolutionTreeSetGenerator(object):
    def __init__(self, lineage, solution_tree_set_generator):
        self.lineage = lineage
        self.solution_tree_set_generator = solution_tree_set_generator

    def __iter__(self):
        return self

    def __next__(self):
        new_lineage, solution = self.solution_tree_set_generator._next_solution(self.lineage)
        if solution is not None:
            self.lineage = new_lineage
            return solution

        else:
            raise StopIteration


class SolutionTreeSetGenerator(object):
    def __init__(self, solution_generator):
        self.solution_generator = solution_generator
        self.current_lineage = None
        self.next_solution = None

    def __iter__(self):
        return self

    def __next__(self):
        if self.current_lineage is None:
            # Very start of generation
            return SingleSolutionTreeSetGenerator(None, self)

        elif self.next_solution is not None:
            # This solution was pulled for the current generator
            # but it was a new lineage, so it ended the last one but
            # was retained for the next one
            next_value = self.next_lineage
            return SingleSolutionTreeSetGenerator(next_value, self)

        else:
            raise StopIteration

    def _next_solution(self, current_lineage):
        if self.next_solution is not None:
            # This solution was pulled for the current generator
            # but it was a new lineage, so it ended the last one but
            # was retained for the next one
            state = self.next_solution
            self.next_solution = None
        else:
            state = next(self.solution_generator)

        solution_lineage = state.get_binding("tree_lineage").value[0]

        # If the current_lineage is None
        # The caller will use this as their new lineage
        if current_lineage is None or solution_lineage == current_lineage:
            return solution_lineage, state

        else:
            # This is the beginning of a new set of solutions
            self.current_lineage = solution_lineage
            self.next_solution = state
            return None, None


# Yields solutions in a single solution group
# asks its solution_group_generator to give it more than the initial group
# when it runs out of initial solutions
class SingleGroupGenerator(object):
    def __init__(self, group_id, solution_group_generator, group_list):
        self.group_id = group_id
        self.solution_group_generator = solution_group_generator
        self.group_list = group_list
        self.last_yielded_index = -1

    def __iter__(self):
        return self

    def __next__(self):
        if groups_logger.level == logging.DEBUG:
            groups_logger.debug(f"SingleGroupGenerator: Next solution requested for {self.group_id}, self.last_yielded_index={self.last_yielded_index}, len(self.group_list) - 1 = {len(self.group_list) - 1}")

        if self.last_yielded_index == len(self.group_list) - 1:
            # If no variable has a between(N, inf) constraint,
            # Just stop now and the caller will get a subset solution group for the answer they care about
            # Note that it may not be *minimal*, might be a subset, and might be maximal.
            # For example, if it is between(3, 10), we might stop at 4, which is correct, but not maximal
            # If it does have a between(N, inf) constraint, return them all
            # This is a performance optimization that really improves the performance of
            # "a few files are in a folder together"
            if not self.solution_group_generator.variable_has_inf_max:
                raise StopIteration

            # See if we can get more items
            elif not self.solution_group_generator.next_solution_in_group(self.group_id):
                raise StopIteration

        self.last_yielded_index += 1
        return self.group_list[self.last_yielded_index]


# Yields a generator that yields solutions in a minimal solution group as quickly as it is found
# but will continue returning solutions until it is maximal if requested. The idea is to make it easy
# to see if there is at least one solution for yes/no questions and propositions (thus the quick minimal solution)
# but allow other types of phrases to get all answers in a group if needed
#
# A group is only yielded from all_plural_groups_stream() when it meets the constraints. Then, if further
# solutions can be added to it and still meet the constraints, it is given an id that shows it came from that original group
# It will continue to grow until no more solutions exist that can be added and still keep the constraints. Note that
# whether the solution group is cuml/coll/dist may change as it grows, even though it is a solution group throughout.
#
# So, when a group is yielded from all_plural_groups_stream(), it has an id which is a "lineage"
# If that lineage is just one group away from an existing SingleGroupGenerator, it should be yielded
# from that SingleGroupGenerator and cause that generator to track the new group_id.  Otherwise, it should create a new group.
#
# Note that a single solution group may "fork" into multiple lineages if the original group gets different records added to
# it that still meet its constraints. The SingleGroupGenerator will "follow" the first fork, arbitrarily, and the others will
# be returned as other groups.
#
# So, a yielded SingleGroupGenerator will "follow" the first lineage that matches it
class SolutionGroupGenerator(object):
    def __init__(self, all_plural_groups_stream, variable_has_inf_max):
        self.all_plural_groups_stream = all_plural_groups_stream
        self.variable_has_inf_max = variable_has_inf_max
        self.solution_groups = {}
        # Use a dict so that we retain the order things got added in
        # but also have a fast way to find ids
        self.unyielded_solution_groups = dict()
        self.complete = False

    def __iter__(self):
        return self

    def __next__(self):
        if len(self.unyielded_solution_groups) == 0:
            # The caller is asking for the next group, and we don't have one yet
            if not self.next_solution_in_group(""):
                self.complete = True
                raise StopIteration

        # Find the next unyielded item and remove it from the unyielded list
        next_group_id = next(iter(self.unyielded_solution_groups))
        self.unyielded_solution_groups.pop(next_group_id)

        value = self.solution_groups[next_group_id]
        if groups_logger.level == logging.DEBUG:
            groups_logger.debug(f"SolutionGroupGenerator: Next solution group requested, returning id {next_group_id}: {value}")

        return value

    # Returns true if there is another solution found for group.id == current_id
    # If current_id == "" then returns true if there is a new group created
    def next_solution_in_group(self, current_id):
        while True:
            try:
                next_group, next_id, stats_group = next(self.all_plural_groups_stream)

            except StopIteration:
                self.complete = True
                return False

            # The ID reflects the lineage, so we can get the
            # parent ID by grabbing the text before the last ":"
            if stats_group.only_instances():
                colon_index = next_id.rfind(":")
                if colon_index == -1:
                    parent_id = ""
                else:
                    parent_id = next_id[:colon_index]
            else:
                parent_id = ""

            # See if the group returned is a descendant of
            # an existing group by first comparing its ID
            # and, if that doesn't work, then its parent_id
            if next_id in self.solution_groups:
                existing_solution_group_id = next_id
            elif parent_id in self.solution_groups:
                existing_solution_group_id = parent_id
            else:
                existing_solution_group_id = ""

            if existing_solution_group_id == "":
                # There wasn't an existing solution group to put this in, start tracking this as a new one
                self.solution_groups[next_id] = SingleGroupGenerator(next_id, self, next_group)
                self.unyielded_solution_groups[next_id] = None

            else:
                # This is an update to an existing solution group, either a parent or the exact id
                # Replace the data in the SingleGroupGenerator and update its ID
                # to the new value so it will properly track the lineage next time
                existing_solution_group = self.solution_groups[existing_solution_group_id]
                existing_solution_group.group_list = next_group
                existing_solution_group.group_id = next_id

                # Update the group_id of this updated solution group so that, if yet another
                # child of this group is created, it'll find it as its parent
                # Note that this can be a NOOP if next_id was already a solution group
                self.solution_groups.pop(existing_solution_group_id)
                self.solution_groups[next_id] = existing_solution_group

                # If the ID was unyielded, remove the old and add the new
                # to the unyielded list
                if existing_solution_group_id in self.unyielded_solution_groups:
                    self.unyielded_solution_groups.pop(existing_solution_group_id)
                    self.unyielded_solution_groups[next_id] = None

            if existing_solution_group_id == current_id:
                # Only return True if there is new data for current_id.
                # This happens if the requested group id (current_id)
                # is the same as existing_solution_group_id, which happens if:
                #   - current_id was "" and a new group was created (thus existing_solution_group_id == "")
                #   - next_id was the current_id solution group and it existed (thus current_id == existing_solution_group_id)
                #   - next_id's immediate parent was already a solution group and that group was current_id
                #       in this case, we give the solution group that we're tracking a new id of next_id
                return True

    def has_multiple_groups(self):
        if len(self.solution_groups) > 1:
            return True
        elif self.complete:
            return False
        else:
            return self.next_solution_in_group("")


# Group the unquantified solutions into "solution groups" that meet the criteria on each variable.
# Designed to return the minimal solution that meets the criteria as quickly as possible.
#
# If the criteria has any between(N, inf) criteria, it will keep streaming answers until the end
# If not, it will stop after the first (minimal) solution is found.
#
# A second solution group will be returned, if it exists, but will be bogus. It is just there so that the caller can see there is one. This is
# to reduce the cost of generating the answer
#
# Allows the developer to choose which solution group to return
#   if they return [], it means "skip this solution group" and we'll try the next one
# yields an iterator that returns solution groups
# TODO: Intelligently choosing the initial cardinal could greatly reduce the combinations processed...
def solution_groups(execution_context, solutions_orig, this_sentence_force, wh_question_variable, tree_info, all_groups=False, all_unprocessed_groups=None, criteria_list=None):
    pipeline_logger.debug(f"Finding solution groups for {tree_info['Tree']}")
    solutions = at_least_one_generator(solutions_orig)
    if solutions:
        # Go through each variable that has a quantifier in order and gather and optimize the criteria list
        # if it wasn't given to us
        if criteria_list is not None:
            declared_criteria_list = criteria_list
        else:
            declared_criteria_list = [data for data in declared_determiner_infos(execution_context, solutions.first_item)]
        optimized_criteria_list = list(optimize_determiner_infos(declared_criteria_list, this_sentence_force, wh_question_variable))

        # variable_has_inf_max means at least one variable has (N, inf) which means we need to go all the way to the end to get the maximal
        # solution. Otherwise, we can just stop when we have a solution and return a minimal solution
        variable_metadata, initial_stats_group, has_global_constraint, variable_has_inf_max = plural_groups_stream_initial_stats(execution_context, optimized_criteria_list)

        # We also set this if the user asks a wh_question so we ensure we get all of the values
        variable_has_inf_max = variable_has_inf_max if wh_question_variable is None else True

        lineage_generator = next(SolutionTreeSetGenerator(solutions))
        lineage_stream = at_least_one_generator(lineage_generator)

        groups_stream = all_plural_groups_stream(execution_context, lineage_stream, optimized_criteria_list, variable_metadata,
                                                 initial_stats_group, has_global_constraint)

        group_generator = SolutionGroupGenerator(groups_stream, variable_has_inf_max)
        if all_unprocessed_groups is not None:
            unprocessed_groups = []
            for group in group_generator:
                unprocessed_groups.append([x for x in group])
            group_generator = unprocessed_groups
            all_unprocessed_groups.append(unprocessed_groups)

        at_least_one_group = at_least_one_generator(group_generator)
        if at_least_one_group is not None:
            if all_groups:
                yield from at_least_one_group

            else:
                # If there are multiple solution groups, we need to add one more (fake) group
                # and yield it so that the caller thinks there are multiple answers and will give a message
                # to the user. The answers aren't shown so it can be anything
                one_more = len(group_generator) > 1 if isinstance(group_generator, list) else group_generator.has_multiple_groups()

                # First see if there is a solution_group handler that should be called
                handlers, index_predication = find_solution_group_handlers(execution_context, this_sentence_force, tree_info)
                wh_handlers = find_wh_group_handlers(execution_context, this_sentence_force)

                # Returning errors:
                # If no solution groups are found, errors from trying to generate them should be returned
                # If even one solution group was found, but failed in the handlers, the error from that handler should be
                # returned because it means the phrase made sense, but something about the world made it fail when is better than
                # errors generated because the phrase made no sense
                best_error_info = (None, False, -1)
                for next_group in at_least_one_group:
                    created_solution_group, has_more, group_list, next_best_error_info = run_handlers(execution_context, wh_handlers, handlers, optimized_criteria_list, one_more, next_group, index_predication, wh_question_variable)
                    if best_error_info[0] is None and next_best_error_info[0] is not None:
                        best_error_info = next_best_error_info
                    if created_solution_group is None:
                        pipeline_logger.debug(f"No solution group handlers, or none handled it or failed: just do the default behavior")
                        if wh_question_variable is not None:
                            wh_created_solution_group = run_wh_group_handlers(wh_handlers, wh_question_variable, one_more, group_list)
                            if len(wh_created_solution_group) == 0:
                                # wh_handler said to fail
                                if best_error_info[0] is None and execution_context.get_error_info()[0] is not None:
                                    best_error_info = execution_context.get_error_info()
                                break
                            else:
                                yield wh_created_solution_group
                        else:
                            yield group_list

                        # If there are multiple solution groups, we need to add one more (fake) group
                        # and yield it so that the caller thinks there are multiple answers and will give a message
                        # to the user. The answers aren't shown so it can be anything
                        if one_more:
                            yield True

                        return

                    elif isinstance(created_solution_group, (tuple, list)) and len(created_solution_group) == 0:
                        pipeline_logger.debug(f"Handler said to skip this group")
                        continue

                    else:
                        pipeline_logger.debug(f"Handler said this group was a solution")
                        yield created_solution_group
                        if has_more:
                            yield True

                        return

                pipeline_logger.debug(f"No more solution groups.")
                execution_context.set_error_info(best_error_info)


class GroupVariableValues(object):
    def __init__(self, variable_constraints):
        self.variable_constraints = variable_constraints
        self.solution_values = []


# If a handler returns:
#   None --> it means ignore the handler and continue
#   [] or () --> it means fail this solution
def run_handlers(execution_context, wh_handlers, handlers, variable_constraints, one_more, group, index_predication, wh_question_variable):
    best_error_info = (None, False, -1)
    created_solution_group = None
    has_more = False
    state_list = list(group)
    if pipeline_logger.level == logging.DEBUG:
        nl = '\n'
        pipeline_logger.debug(f"Found solution group: {nl + '   ' + (nl + '   ').join([str(s) for s in state_list])}")
        pipeline_logger.debug(f"Current execution context error: {execution_context.error()}")

    if len(handlers) > 0:
        pipeline_logger.debug(f"Running {len(handlers)} solution group handlers")

        for is_predication_handler_name in handlers:
            handler_function = is_predication_handler_name[1]
            if is_predication_handler_name[0]:
                # This is a predication-style solution group handler
                # Build up an arg structure to call the predication with that
                # has the same arguments as the normal predication but has a list for each argument that represents the solution group
                handler_args = []
                for arg in index_predication.args:
                    found_constraint = None
                    for constraint in variable_constraints:
                        if constraint.variable_name == arg:
                            found_constraint = constraint
                            break
                    handler_args.append(GroupVariableValues(found_constraint))

                for state in state_list:
                    for arg_index in range(len(index_predication.args)):
                        if index_predication.argument_types()[arg_index] == "c" or index_predication.argument_types()[arg_index] == "h":
                            handler_args[arg_index].solution_values.append(index_predication.args[arg_index])
                        else:
                            handler_args[arg_index].solution_values.append(state.get_binding(index_predication.args[arg_index]))

                handler_args = [state_list, one_more] + handler_args

            else:
                handler_args = (state_list, one_more) + (variable_constraints, )

            debug_name = is_predication_handler_name[2][0] + "." + is_predication_handler_name[2][1]
            pipeline_logger.debug(f"Running {debug_name} solution group handler")
            for next_solution_group in handler_function(*handler_args):
                if created_solution_group is None:
                    created_solution_group = next_solution_group
                    if len(created_solution_group) == 0:
                        # handler said to fail
                        if best_error_info[0] is None and execution_context.get_error_info()[0] is not None:
                            best_error_info = execution_context.get_error_info()
                        break
                    pipeline_logger.debug(f"{debug_name} succeeded with first solution")
                    if wh_question_variable is not None:
                        created_solution_group = run_wh_group_handlers(wh_handlers, wh_question_variable, one_more, created_solution_group)
                        if len(created_solution_group) == 0:
                            # handler said to fail
                            if best_error_info[0] is None and execution_context.get_error_info()[0] is not None:
                                best_error_info = execution_context.get_error_info()
                            break
                else:
                    pipeline_logger.debug(f"{handler_function.__name__} succeeded with second solution")
                    has_more = True
                    break

            # First solution_group handler that yields, wins
            if created_solution_group:
                pipeline_logger.debug(f"{debug_name} succeeded so no more solution group handlers will be run")
                break
            else:
                pipeline_logger.debug(f"{debug_name} failed, so trying alternative solution group handlers...")

        pipeline_logger.debug(f"Done trying solution group handlers, best error: {best_error_info}")
        return created_solution_group, has_more, state_list, best_error_info

    else:
        return None, None, state_list, (None, False, -1)


def get_function(module_function):
    module = sys.modules[module_function[0]]
    function = getattr(module, module_function[1])
    return function


def find_wh_group_handlers(execution_context, this_sentence_force):
    # First get the list of handlers, if any
    handlers = []
    for module_function in execution_context.vocabulary.predications("solution_group_wh", [], this_sentence_force):
        handlers.append((get_function(module_function), module_function[0], module_function[1]))

    return handlers


# Called only if we have a successful solution group
# Same semantic as solution group handlers: First wh_group handler that yields, wins
def run_wh_group_handlers(wh_handlers, wh_question_variable, one_more, group):
    # If there are responses in the group, don't run the handlers
    for solution in group:
        for operation in solution.get_operations():
            if isinstance(operation, RespondOperation):
                return group

    if len(wh_handlers) > 0:
        value_binding_list = [solution.get_binding(wh_question_variable) for solution in group]
        for function_module_functionname in wh_handlers:
            pipeline_logger.debug(f"Running {function_module_functionname[1]}.{function_module_functionname[2]} wh-solution group handler")

            for resulting_group in function_module_functionname[0](group, one_more, value_binding_list):
                if resulting_group is not None and len(resulting_group) > 0:
                    return resulting_group
                else:
                    pipeline_logger.debug(f"{function_module_functionname[1]}.{function_module_functionname[2]} handler said to ignore")


    else:
        return group


# Returns predication_handlers, global_handlers
# with just an array of functions in each
def find_solution_group_handlers(execution_context, this_sentence_force, tree_info):
    handlers = []
    index_predication = find_predication_from_introduced(tree_info["Tree"], tree_info["Index"])
    for module_function in execution_context.vocabulary.predications("solution_group_" + index_predication.name, index_predication.argument_types(), this_sentence_force):
        handlers.append([True, get_function(module_function), module_function])

    for module_function in execution_context.vocabulary.predications("solution_group", [], this_sentence_force):
        handlers.append([False, get_function(module_function), module_function])

    return handlers, index_predication


# Return the infos in the order they will be executed in
def declared_determiner_infos(execution_context, state, variables=None):
    tree_info = state.get_binding("tree").value[0]
    if variables is None:
        variables = gather_quantifier_order(tree_info)
    for variable_name in variables:
        if variable_name[0] == "x":
            binding = state.get_binding(variable_name)

            # First get the determiner
            determiner = determiner_from_binding(state, binding)
            if determiner is not None:
                yield determiner

            # Then get the quantifier
            quantifier_determiner = quantifier_from_binding(state, binding)
            if quantifier_determiner is not None:
                yield quantifier_determiner


def reduce_variable_determiners(variable_info_list, this_sentence_force, wh_question_variable):
    min_size = 0
    max_size = float(inf)
    global_constraint = None
    exactly_constraint = None
    all_rstr_constraint = None
    every_rstr_constraint = None
    required_values_constraint = None
    predication = None
    for constraint in variable_info_list:
        if constraint.global_criteria == GlobalCriteria.exactly:
            # If there is more than one "only" ... that should never happen. Unclear what words would cause it
            assert exactly_constraint is None
            exactly_constraint = constraint

        elif constraint.global_criteria == GlobalCriteria.all_rstr_meet_criteria:
            # ditto
            assert all_rstr_constraint is None
            all_rstr_constraint = constraint

        elif constraint.global_criteria == GlobalCriteria.every_rstr_meet_criteria:
            # ditto
            assert every_rstr_constraint is None
            every_rstr_constraint = constraint

        else:
            # Constraints with no global criteria just get merged to most restrictive
            if constraint.min_size > min_size:
                min_size = constraint.min_size
                predication = constraint.predication

            if constraint.max_size < max_size:
                max_size = constraint.max_size
                predication = constraint.predication

        if constraint.required_values is not None:
            if required_values_constraint is None:
                required_values_constraint = constraint.required_values
            else:
                required_values_constraint += constraint.required_values

    if exactly_constraint is not None:
        assert exactly_constraint.min_size >= min_size and exactly_constraint.max_size <= max_size
        min_size = exactly_constraint.min_size
        max_size = exactly_constraint.max_size
        global_constraint = GlobalCriteria.exactly
        predication = exactly_constraint.predication

    if all_rstr_constraint is not None:
        if len(variable_info_list) > 1:
            # convert "the 2" into a single constraint so it can ensure there are really only 2
            # Should only ever be "the"
            assert all_rstr_constraint.min_size == 1 and all_rstr_constraint.max_size == float(inf)
            global_constraint = GlobalCriteria.all_rstr_meet_criteria
            predication = all_rstr_constraint.predication

        else:
            # This was the only constraint, use it
            return [all_rstr_constraint]

    if every_rstr_constraint is not None:
        if len(variable_info_list) > 1:
            if min_size == 1 and max_size == 1:
                # Convert singular constraint (i.e. "every file is large") into plural
                assert every_rstr_constraint.min_size == 1 and every_rstr_constraint.max_size == float(inf)
                max_size = float(inf)

            # Now that we have converted the singular to plural, it is just "all"
            global_constraint = GlobalCriteria.all_rstr_meet_criteria
            predication = every_rstr_constraint.predication

        else:
            # This was the only constraint, use it, but convert to all_rstr_meet_criteria
            all_rstr_constraint = copy.deepcopy(every_rstr_constraint)
            all_rstr_constraint.global_criteria = GlobalCriteria.all_rstr_meet_criteria
            return [all_rstr_constraint]

    if predication is None:
        predication = variable_info_list[0].predication

    return [VariableCriteria(predication, variable_info_list[0].variable_name, min_size, max_size, global_criteria=global_constraint, required_values=required_values_constraint)]


def reduce_determiner_infos(determiner_info_list_orig, this_sentence_force, wh_question_variable):
    determiner_info_list = copy.deepcopy(determiner_info_list_orig)
    info_by_variable = determiner_info_by_variable(determiner_info_list)
    reduced_determiner_infos = []
    for variable_info_list in info_by_variable.values():
        reduced_determiner_infos += reduce_variable_determiners(variable_info_list, this_sentence_force, wh_question_variable)

    return reduced_determiner_infos


def determiner_info_by_variable(determiner_info_list):
    info_by_variable = {}
    for determiner_info in determiner_info_list:
        if determiner_info.variable_name not in info_by_variable:
            info_by_variable[determiner_info.variable_name] = []
        info_by_variable[determiner_info.variable_name].append(determiner_info)

    return info_by_variable


# Is passed a list of VariableCriteria
def optimize_determiner_infos(determiner_info_list_orig, this_sentence_force, wh_question_variable):
    determiner_info_list = copy.deepcopy(determiner_info_list_orig)

    # First combine the determiners into 1 if possible
    determiner_info_list = reduce_determiner_infos(determiner_info_list, this_sentence_force, wh_question_variable)

    return determiner_info_list


groups_logger = logging.getLogger('SolutionGroups')
pipeline_logger = logging.getLogger('Pipeline')
