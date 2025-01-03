import copy
import logging
import perplexity.tree
import perplexity.execution
from math import inf
import perplexity.plurals
from perplexity.utilities import at_least_one_generator, get_function, sentence_force, timeout_check


def constraints_for_variable(state, variable_name):
    declared_criteria_list = [data for data in declared_determiner_infos(state.get_binding("tree").value[0], state)]
    tree_info = state.get_binding("tree").value[0]
    this_sentence_force = sentence_force(tree_info["Variables"])
    wh_question_variable = perplexity.tree.get_wh_question_variable(tree_info)
    optimized_criteria_list = list(optimize_determiner_infos(declared_criteria_list, this_sentence_force, wh_question_variable))
    found_constraint = None
    for constraint in optimized_criteria_list:
        if constraint.variable_name == variable_name:
            found_constraint = constraint
            break

    groups_logger.debug(f"Constraints: {found_constraint}")

    return found_constraint


# Used to create new GroupVariableValues() when predications need to create them at runtime
def create_group_variable_values(context, state_list, variable_name):
    found_constraint = constraints_for_variable(state_list[0], variable_name)
    return perplexity.plurals.GroupVariableValues(found_constraint, state_list, variable_name[0], variable_name)


# Yields solutions in a single solution group
# asks its solution_group_generator to give it more than the initial group
# when it runs out of initial solutions
# Setting group_id=None means that it won't ask to generate more groups
class SingleMaximalGroupGenerator(object):
    def __init__(self, group_id, solution_group_generator, group_list, generate_maximal_group):
        self.group_id = group_id
        self.solution_group_generator = solution_group_generator
        self.group_list = group_list
        self.generate_maximal_group = generate_maximal_group
        self.last_yielded_index = -1

    def __iter__(self):
        return self

    def __next__(self):
        if groups_logger.level == logging.DEBUG:
            groups_logger.debug(f"SingleGroupGenerator: Next solution requested for {self.group_id}, self.last_yielded_index={self.last_yielded_index}, len(self.group_list) - 1 = {len(self.group_list) - 1}")

        if self.last_yielded_index >= len(self.group_list) - 1:
            if self.generate_maximal_group:
                if self.solution_group_generator is None or not self.solution_group_generator.next_solution_in_group(self.group_id):
                    raise StopIteration
            else:
                raise StopIteration

        self.last_yielded_index += 1
        if self.last_yielded_index > len(self.group_list) - 1:
            # This can happen if the solution group handlers return less records
            # than the original solution group had
            raise StopIteration
        return self.group_list[self.last_yielded_index]

    # If the caller wants to guarantee they have the maximal solution group, they call this method
    # and it returns a maximal group for this solution
    def maximal_group_iterator(self):
        # If no variable has a between(N, inf) constraint,
        # Just stop now and the caller will get a subset solution group for the answer they care about
        # Note that it may not be *minimal*, might be a subset, and might be maximal.
        # For example, if it is between(3, 10), we might stop at 4, which is correct, but not maximal
        # If it does have a between(N, inf) constraint, return them all
        # This is a performance optimization that really improves the performance of
        # "a few files are in a folder together"
        # Find all solutions
        self.generate_maximal_group = True
        return self


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
# If generate_maximal_group is False, then only the solutions in initial group will be yielded
# for that group, and the groups that would have been "followed" are simply discarded.  This allows
# the caller to find a minimal group and determine if there are other solution groups
class SolutionMaximalGroupGenerator(object):
    def __init__(self, all_plural_groups_stream, variable_has_inf_max, generate_maximal_group=True):
        self.all_plural_groups_stream = all_plural_groups_stream
        self.variable_has_inf_max = variable_has_inf_max
        self.generate_maximal_group = generate_maximal_group
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
    def next_solution_in_group(self, current_id, trace_string=None):
        while True:
            try:
                next_group, next_id, stats_group, raw_group = next(self.all_plural_groups_stream)

            except StopIteration:
                self.complete = True
                return False

            # The ID reflects the lineage, so we can get the
            # parent ID by grabbing the text before the last ":"
            if stats_group.only_instances() and stats_group.merge:
                colon_index = -1 if next_id is None else next_id.rfind(":")
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

            # Create a new group if:
            # There wasn't an existing solution group to put this in,
            # OR: There was one, but it was not a maximal group so it'll never request it
            create_new_group = existing_solution_group_id == "" or \
                    (existing_solution_group_id != "" and not self.solution_groups[existing_solution_group_id].generate_maximal_group)
            if create_new_group:
                groups_logger.debug(f"SolutionGroupGenerator: There wasn't an existing solution group for solution, start a new group: {next_group}")
                self.solution_groups[next_id] = SingleMaximalGroupGenerator(next_id, self, next_group, self.generate_maximal_group)
                self.unyielded_solution_groups[next_id] = None
                existing_solution_group_id = ""

            else:
                # This is an update to an existing solution group, either a parent or the exact id
                # Replace the data in the SingleGroupGenerator and update its ID
                # to the new value so it will properly track the lineage next time
                groups_logger.debug(f"SolutionGroupGenerator: New solution for existing group: {existing_solution_group_id}, new group id: {next_id}")
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

            if existing_solution_group_id == current_id :
                # Only return True if there is new data for current_id.
                # or if current_id == "" and we created a new group
                #
                # This happens if the requested group id (current_id)
                # is the same as existing_solution_group_id, which happens if:
                #   - current_id was "" and a new group was created (thus existing_solution_group_id == "")
                #   - next_id was the current_id solution group and it existed (thus current_id == existing_solution_group_id)
                #   - next_id's immediate parent was already a solution group and that group was current_id
                #       in this case, we give the solution group that we're tracking a new id of next_id
                if trace_string and current_id == "":
                    if groups_logger.level == logging.DEBUG:
                        nl = "\n     "
                        groups_logger.debug(
                            f"Processed: {trace_string}: {''.join([nl + str(x) for x in next_group])}")
                        groups_logger.debug(
                            f"Raw: {trace_string}: {''.join([nl + str(x) for x in raw_group])}")
                return True

    def has_multiple_groups(self):
        if len(self.solution_groups) > 1:
            return True
        elif self.complete:
            return False
        else:
            return self.next_solution_in_group("", "Has more solution group:")


# Group the unquantified solutions into "solution groups" that meet the criteria on each variable.
# Designed to return the minimal solution that meets the criteria as quickly as possible.
#
# If the criteria has any between(N, inf) criteria, it will keep streaming answers until the end
# If not, it will stop after the first (minimal) solution is found.
#
# Allows the developer to choose which solution group to return
#   if they return [], it means "skip this solution group" and we'll try the next one
# yields an iterator that returns solution groups
# TODO: Intelligently choosing the initial cardinal could greatly reduce the combinations processed...
def solution_groups(execution_context,
                    solutions_orig,
                    this_sentence_force,
                    wh_question_variable,
                    tree_info,
                    all_groups=False,
                    all_solution_groups=None,
                    criteria_list=None,
                    start_time=None,
                    timeout=None):
    pipeline_logger.debug(f"Finding solution groups for {tree_info['Tree']}")
    solutions = at_least_one_generator(solutions_orig)

    if solutions is not None:
        timeout_check("solution_groups", timeout, start_time)
        declared_criteria_list = [data for data in declared_determiner_infos(solutions.first_item.get_binding("tree").value[0], solutions.first_item)]
        optimized_criteria_list = list(optimize_determiner_infos(declared_criteria_list, this_sentence_force, wh_question_variable))

        # variable_has_inf_max means at least one variable has (N, inf) which means we need to go all the way to the end to get the maximal
        # solution. Otherwise, we can just stop when we have a solution and return a minimal solution
        variable_metadata, initial_stats_group, has_global_constraint, variable_has_inf_max = perplexity.plurals.plural_groups_stream_initial_stats(execution_context, optimized_criteria_list)

        # We also set this if the user asks a wh_question so we ensure we get all of the values
        variable_has_inf_max = variable_has_inf_max if wh_question_variable is None else True
        handlers, index_predication = perplexity.tree.find_solution_group_handlers_with_name(execution_context.vocabulary, this_sentence_force, tree_info, "solution_group")
        groups_stream = perplexity.plurals.all_plural_groups_stream(execution_context, solutions, optimized_criteria_list, variable_metadata,
                                                 initial_stats_group, has_global_constraint,
                                                 handlers, optimized_criteria_list, index_predication)

        # yes/no questions and propositions only need the minimal solution, so don't return a SolutionMaximalGroupGenerator
        get_maximal_solution_group = not (this_sentence_force == "prop" or
            (this_sentence_force in ["prop-or-ques", "ques"] and wh_question_variable is None))

        group_generator = SolutionMaximalGroupGenerator(groups_stream, variable_has_inf_max, generate_maximal_group=get_maximal_solution_group)

        handlers, index_predication = perplexity.tree.find_solution_group_handlers_with_name(execution_context.vocabulary,
                                                                                             this_sentence_force,
                                                                                             tree_info,
                                                                                             "solution_group")
        # create a context that will track errors across solution groups
        temp_context = execution_context.new_initial_context()
        for solution_group in group_generator:
            # The context is cleared every time so we need to remember the "best" error
            # Since the trees are the same for every solution group, we can use the normal logic
            created_solution_group, last_error_info = perplexity.plurals.check_group_against_code_criteria(
                execution_context,
                handlers,
                optimized_criteria_list,
                index_predication,
                solution_group)
            if created_solution_group:
                # Clear any errors that occurred trying to generate solution groups that didn't work
                # so that the error that gets returned is whatever happens while *processing* the solution group
                execution_context.clear_error()
                yield created_solution_group
            else:
                temp_context.report_error_for_index(predication_index=last_error_info[2],
                                                    error=last_error_info[0], force=last_error_info[1],
                                                    phase=last_error_info[3])

        # Make sure to record the last error (of the final solution or solution group that didn't work)
        last_error_info = execution_context.get_error_info()
        temp_context.report_error_for_index(predication_index=last_error_info[2],
                                            error=last_error_info[0], force=last_error_info[1],
                                            phase=last_error_info[3])

        # Set the error to the best failure we recorded
        next_best_error_info = temp_context.get_error_info()
        execution_context.set_error_info(temp_context.get_error_info())
        groups_logger.debug(f"solution_groups recorded error: {execution_context.get_error_info()}")
    else:
        execution_context.set_error_info(solutions_orig.error_info)
        groups_logger.debug(f"solution_groups recorded error: {execution_context.get_error_info()}")


# Return the infos in the order they will be executed in
def declared_determiner_infos(tree_info, state, variables=None):
    if variables is None:
        variables = perplexity.tree.gather_quantifier_order(tree_info)
    for variable_name in variables:
        if variable_name[0] == "x":
            binding = state.get_binding(variable_name)

            # First get the determiner
            determiner = perplexity.plurals.determiner_from_binding(tree_info, binding)
            if determiner is not None:
                yield determiner

            # Then get the quantifier
            quantifier_determiner = perplexity.plurals.quantifier_from_binding(state, binding)
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
        if constraint.global_criteria == perplexity.plurals.GlobalCriteria.exactly:
            # If there is more than one "only" ... that should never happen. Unclear what words would cause it
            assert exactly_constraint is None
            exactly_constraint = constraint

        elif constraint.global_criteria == perplexity.plurals.GlobalCriteria.all_rstr_meet_criteria:
            # ditto
            assert all_rstr_constraint is None
            all_rstr_constraint = constraint

        elif constraint.global_criteria == perplexity.plurals.GlobalCriteria.every_rstr_meet_criteria:
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
        global_constraint = perplexity.plurals.GlobalCriteria.exactly
        predication = exactly_constraint.predication

    if all_rstr_constraint is not None:
        if len(variable_info_list) > 1:
            # convert "the 2" into a single constraint so it can ensure there are really only 2
            # Should only ever be "the"
            assert all_rstr_constraint.min_size == 1 and all_rstr_constraint.max_size == float(inf)
            global_constraint = perplexity.plurals.GlobalCriteria.all_rstr_meet_criteria
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
            global_constraint = perplexity.plurals.GlobalCriteria.all_rstr_meet_criteria
            predication = every_rstr_constraint.predication

        else:
            # This was the only constraint, use it, but convert to all_rstr_meet_criteria
            all_rstr_constraint = copy.deepcopy(every_rstr_constraint)
            all_rstr_constraint.global_criteria = perplexity.plurals.GlobalCriteria.all_rstr_meet_criteria
            return [all_rstr_constraint]

    if predication is None:
        predication = variable_info_list[0].predication

    return [perplexity.plurals.VariableCriteria(predication, variable_info_list[0].variable_name, min_size, max_size, global_criteria=global_constraint, required_values=required_values_constraint)]


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

    groups_logger.debug(f"Constraints: {determiner_info_list}")

    return determiner_info_list


groups_logger = logging.getLogger('SolutionGroups')
pipeline_logger = logging.getLogger('Pipeline')
