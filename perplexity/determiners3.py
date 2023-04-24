import copy
import enum
import itertools
import logging
from perplexity.set_utilities import all_nonempty_subsets_stream, count_set
from perplexity.utilities import is_plural_from_tree_info
from perplexity.variable_binding import VariableValueType
from perplexity.vocabulary import PluralType


class CriteriaResult(enum.Enum):
    meets = 0,
    # Meets the criteria, as long as the global
    # criteria (like "only 2") for this variable is met
    meets_pending_global = 1
    contender = 2
    fail_one = 3
    # In some cases like "only 2" we can fail everything because
    # a global criteria wasn't met
    fail_all = 4


class GlobalCriteria(enum.Enum):
    exactly = 0
    all_rstr_meet_criteria = 1


criteria_transitions = {CriteriaResult.meets: {CriteriaResult.meets: CriteriaResult.meets,
                                               CriteriaResult.meets_pending_global: CriteriaResult.meets_pending_global,
                                               CriteriaResult.contender: CriteriaResult.contender,
                                               CriteriaResult.fail_one: CriteriaResult.fail_one,
                                               CriteriaResult.fail_all: CriteriaResult.fail_all},
                        CriteriaResult.meets_pending_global: {CriteriaResult.meets: CriteriaResult.meets,
                                                              CriteriaResult.meets_pending_global: CriteriaResult.meets_pending_global,
                                                              CriteriaResult.contender: CriteriaResult.contender,
                                                              CriteriaResult.fail_one: CriteriaResult.fail_one,
                                                              CriteriaResult.fail_all: CriteriaResult.fail_all},
                        CriteriaResult.contender: {CriteriaResult.meets: CriteriaResult.contender,
                                                   CriteriaResult.meets_pending_global: CriteriaResult.meets_pending_global,
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
                                                  CriteriaResult.fail_one: CriteriaResult.fail_all}
                        }


class VariableCriteria(object):
    def __init__(self, variable_name, min_size=1, max_size=float('inf'), global_criteria=None):
        self.variable_name = variable_name
        self.global_criteria = global_criteria
        self.min_size = min_size
        self.max_size = max_size
        self._unique_rstrs = set()

    # Numbers can only increase so ...
    def meets_criteria(self, value_list):
        values_count = count_set(value_list)

        if values_count > self.max_size:
            # It'll never get smaller so it fails forever
            return CriteriaResult.fail_one

        elif values_count < self.min_size:
            return CriteriaResult.contender

        else:
            # values_count >= self.min_size and values_count <= self.max_size
            if self.global_criteria:
                # "Only/Exactly", much like the quantifier "the" does more than just group solutions into groups
                # ("only 2 files are in the folder") it also limits *all* the solutions to that number.
                # So we need to track unique values across all answers in this case
                self._unique_rstrs.update(value_list)

            if self.global_criteria == GlobalCriteria.exactly:
                # We can fail immediately if we have too many
                if len(self._unique_rstrs) > self.max_size:
                    # execution_context.report_error_for_index(0, ["moreThan", error_location, max_count], force=True)
                    # return
                    return CriteriaResult.fail_all

                else:
                    return CriteriaResult.meets_pending_global

            elif self.global_criteria == GlobalCriteria.all_rstr_meet_criteria:
                return CriteriaResult.meets_pending_global

            else:
                return CriteriaResult.meets

    def meets_global_criteria(self, execution_context):
        if self.global_criteria == GlobalCriteria.all_rstr_meet_criteria:
            is_plural = is_plural_from_tree_info(execution_context.tree_info, self.variable_name)
            all_rstr_values = execution_context.get_variable_execution_data(self.variable_name)["AllRstrValues"]

            if not is_plural and len(all_rstr_values) > 1:
                # execution_context.report_error(["moreThan1", ["AtPredication", predication.args[2], variable_name]],
                #                                force=True)
                return False

            elif len(all_rstr_values) != len(self._unique_rstrs):
                # execution_context.report_error(["notTrueForAll", ["AtPredication", predication.args[2], variable_name]],
                #                                force=True)
                return False

            else:
                return True

        if self.global_criteria == GlobalCriteria.exactly:
            if len(self._unique_rstrs) < self.min_size:
                # execution_context.report_error_for_index(0, ["lessThan", error_location, min_count], force=True)
                # return
                return False

            else:
                return True

        else:
            return True


class GroupVariableStats(object):
    def __init__(self, variable_name):
        self.variable_name = variable_name
        self.whole_group_unique_individuals = set()
        self.whole_group_unique_values = {}
        self.prev_variable_stats = None
        self.next_variable_stats = None

    def __repr__(self):
        return f"values={len(self.whole_group_unique_values)}, ind={len(self.whole_group_unique_individuals)}"

    def add_solution(self, variable_criteria, solution):
        binding_value = solution.get_binding(self.variable_name).value
        self.whole_group_unique_individuals.update(binding_value)
        next_value = None if self.next_variable_stats is None else solution.get_binding(self.next_variable_stats.variable_name).value
        if binding_value not in self.whole_group_unique_values:
            self.whole_group_unique_values[binding_value] = [set(next_value if next_value is not None else []), [solution]]
        else:
            self.whole_group_unique_values[binding_value][0].update(next_value if next_value is not None else [])
            self.whole_group_unique_values[binding_value][1].append(solution)

        prev_unique_value_count = None if self.prev_variable_stats is None else len(self.prev_variable_stats.whole_group_unique_values)
        if prev_unique_value_count is not None and prev_unique_value_count > 1:
            # Cumulative
            cumulative_state = variable_criteria.meets_criteria(self.whole_group_unique_individuals)
            if cumulative_state == CriteriaResult.meets:
                return CriteriaResult.meets

            # Distributive
            # for each prev_unique_value: len(unique_values) meets criteria
            distributive_state = CriteriaResult.meets
            for prev_unique_value_item in self.prev_variable_stats.whole_group_unique_values.items():
                distributive_value_state = variable_criteria.meets_criteria(prev_unique_value_item[1][0])
                distributive_state = criteria_transitions[distributive_state][distributive_value_state]
                if distributive_state == CriteriaResult.fail_one:
                    break

            if distributive_state == CriteriaResult.meets:
                return CriteriaResult.meets

            return CriteriaResult.contender if cumulative_state == CriteriaResult.contender or distributive_state == CriteriaResult.contender else CriteriaResult.fail_one

        elif prev_unique_value_count is None or prev_unique_value_count == 1:
            # Collective
            return variable_criteria.meets_criteria(self.whole_group_unique_individuals)


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
#
def check_criteria_all(var_criteria, current_set_stats, new_solution):
    new_set_state = CriteriaResult.meets
    for index in range(len(var_criteria)):
        variable_stats = current_set_stats[index]
        criteria = var_criteria[index]
        state = variable_stats.add_solution(criteria, new_solution)
        new_set_state = criteria_transitions[new_set_state][state]
        if new_set_state == CriteriaResult.fail_one:
            return CriteriaResult.fail_one

    return new_set_state


# Every set that is generated has a GroupVariableStats object that does all
# the counting that we need to see if it meets the criteria
# New groups are created by copying an existing set and adding a new solution into it
#
# Criteria like "the" and "only" (as in "only 2") also need to track information *across groups*
# to ensure there is "only 2" solutions generated. This is tracked in the criteria object itself
# since it is reused across the sets
def all_plural_groups_stream(execution_context, solutions, var_criteria):
    # Create the initial stats
    initial_stats = []
    for criteria in var_criteria:
        var_stats = GroupVariableStats(criteria.variable_name)
        initial_stats.append(var_stats)

    for stat_index in range(len(initial_stats)):
        prev_stat = None if stat_index == 0 else initial_stats[stat_index - 1]
        next_stat = None if stat_index + 1 == len(initial_stats) else initial_stats[stat_index + 1]
        initial_stats[stat_index].prev_variable_stats = prev_stat
        initial_stats[stat_index].next_variable_stats = next_stat

    # Generate alternatives
    sets = [(initial_stats, ())]
    pending_global_criteria = []
    for i in solutions:
        new_sets = []
        for k in sets:
            new_set_criteria = copy.deepcopy(k[0])
            state = check_criteria_all(var_criteria,  new_set_criteria, i)
            if state == CriteriaResult.meets:
                #   - meets criteria: yield it
                new_set = (new_set_criteria, k[1] + (i,))
                yield new_set[1]
                new_sets.append(new_set)

            elif state == CriteriaResult.meets_pending_global:
                #   - meets criteria ... pending a global check at the end:
                # save it away until the end
                new_set = (new_set_criteria, k[1] + (i,))
                pending_global_criteria.append(new_set[1])
                new_sets.append(new_set)

            elif state == CriteriaResult.contender:
                # - contender (but doesn't meet yet): add to the set but don't yield
                new_set = (new_set_criteria, k[1] + (i,))
                new_sets.append(new_set)

            elif state == CriteriaResult.fail_one:
                #   - fail (doesn't meet ): don't add don't yield
                continue

            elif state == CriteriaResult.fail_all:
                # A global criteria wasn't met so none will work
                return

        sets += new_sets

    if len(pending_global_criteria) > 0:
        for criteria in var_criteria:
            if not criteria.meets_global_criteria(execution_context):
                return

        yield from pending_global_criteria


determiner_logger = logging.getLogger('Determiners')