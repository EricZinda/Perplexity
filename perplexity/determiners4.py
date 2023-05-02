import enum
from perplexity.set_utilities import count_set, all_nonempty_subsets_stream, product_stream
from perplexity.tree import find_quantifier_from_variable
from perplexity.utilities import is_plural_from_tree_info, parse_predication_name, is_plural
from perplexity.variable_binding import VariableValueType
from perplexity.vocabulary import PluralType


def determiner_from_binding(state, binding):
    if binding.variable.determiner is not None:
        return binding.variable.determiner

    else:
        quantifier = find_quantifier_from_variable(state.get_binding("tree").value[0]["Tree"], binding.variable.name)
        if is_plural(state, binding.variable.name):
            # Plural determiner, mark this as coming from the quantifier for error reporting purposes
            return VariableCriteria(quantifier,
                                    binding.variable.name,
                                    min_size=2,
                                    max_size=float('inf'))

        else:
            return VariableCriteria(quantifier,
                                    binding.variable.name,
                                    min_size=1,
                                    max_size=1)


def quantifier_from_binding(state, binding):
    return binding.variable.quantifier


def expand_combinatorial_variables(variable_metadata, solution):
    alternatives = {}
    for variable_item in variable_metadata.items():
        binding = solution.get_binding(variable_item[0])
        variable_plural_type = variable_item[1]["PluralType"]
        if binding.variable.value_type == VariableValueType.combinatoric:
            # If variable_name is combinatoric, all of its appropriate alternative combinations
            # have to be used. Thus, if the variable_plural_type is collective, we only add sets > 1, etc
            min_size = 1
            max_size = None
            if variable_plural_type == PluralType.distributive:
                max_size = 1

            elif variable_plural_type == PluralType.collective:
                min_size = 2

            else:
                assert variable_plural_type == PluralType.all

            alternatives[binding.variable.name] = all_nonempty_subsets_stream(binding.value, min_size=min_size, max_size=max_size)

    if len(alternatives) == 0:
        yield solution

    else:
        # create combinations by picking one from each
        variable_names = list(alternatives.keys())
        for assignment in product_stream(iter(alternatives.values())):
            new_solution = solution
            for variable_index in range(len(variable_names)):
                new_solution.set_x(variable_names[variable_index], tuple(assignment[variable_index]), VariableValueType.set)
            yield new_solution


def plural_groups_stream_initial_stats(execution_context, var_criteria):
    variable_metadata = {}
    for criteria in var_criteria:
        variable_metadata[criteria.variable_name] = execution_context.get_variable_metadata(criteria.variable_name)

    # Create the initial stats
    initial_stats_group = StatsGroup()
    has_global_constraint, variable_has_inf_max, constraints_are_open = initial_stats_group.initialize(var_criteria)

    return variable_metadata, initial_stats_group, has_global_constraint, variable_has_inf_max, constraints_are_open


# Every set that is generated has a GroupVariableStats object that does all
# the counting that we need to see if it meets the criteria
# New groups are created by copying an existing set and adding a new solution into it
#
# Criteria like "the" and "only" (as in "only 2") also need to track information *across groups*
# to ensure there is "only 2" solutions generated. This is tracked in the criteria object itself
# since it is reused across the sets
#
# yields: solution_group, set_id
# so that the caller can detect when a solution is just more rows in an existing set_id
def all_plural_groups_stream(execution_context, solutions, var_criteria, variable_metadata, initial_stats_group, has_global_constraint, sets_are_open):
    # Generate alternatives
    set_id = 0
    sets = [[initial_stats_group, [], set_id]]
    set_id += 1
    pending_global_criteria = []
    abort = False
    for combinatorial_solution in solutions:
        for next_solution in expand_combinatorial_variables(variable_metadata, combinatorial_solution):
            new_sets = []
            for existing_set in sets:
                # This is an *optimization* to reduce the number of sets being created
                # for scenarios like "which files are in a folder?"
                if can_merge_into_group(var_criteria, existing_set[0], existing_set[1], next_solution):
                    # The variable values already existed in this set,
                    # just add it. Return it as a solution since it is a unique solution
                    # TODO: mark it somehow that the unique variable assignments have already been returned
                    # and that this is just a more complete solution
                    existing_set[1].append(next_solution)
                    yield existing_set[1], existing_set[2]
                    continue

                new_set_stats_group = existing_set[0].copy()
                state = check_criteria_all(execution_context, var_criteria,  new_set_stats_group, next_solution)

                if state == CriteriaResult.fail_one:
                    #   - fail (doesn't meet criteria): don't add, don't yield
                    continue

                elif state == CriteriaResult.fail_all:
                    # A global criteria wasn't met so none will work
                    # Still run global constraints to get a good error
                    abort = True
                    break

                else:
                    # Doesn't fail
                    if sets_are_open:
                        new_set = existing_set

                    else:
                        new_set = [None, None, set_id]
                        set_id += 1
                        new_sets.append(new_set)

                    new_set[0] = new_set_stats_group
                    new_set[1] = existing_set[1] + [next_solution]

                    if state == CriteriaResult.meets:
                        yield new_set[1], new_set[2]

                    elif state == CriteriaResult.meets_pending_global:
                        pending_global_criteria.append([new_set[1], new_set[2]])

                    elif state == CriteriaResult.contender:
                        # Not yet a solution, don't track it as one
                        pass

            sets += new_sets

            if abort:
                break

        if abort:
            break

    # If we aborted, the error should already be set
    if not abort and has_global_constraint:
        for criteria in var_criteria:
            if not criteria.meets_global_criteria(execution_context):
                return

        yield from pending_global_criteria


# See if the constrained variable values are already in the set
#     - Yes: this is a "merge": Simply add the item into the set. Because it changes neither the unique individuals nor the unique values:
#       - This can *only* happen when there are variables without constraints on them because otherwise the entire set of values can't already exist
#       - Nothing in the stats needs to be updated and the criteria must be the same as before. The state of the set is the same as before.
def can_merge_into_group(all_criteria, current_set_stats, current_set, new_solution):
    if len(all_criteria) == 0:
        return True

    else:
        for index in range(len(all_criteria)):
            variable_stats = current_set_stats.variable_stats[index]
            variable_criteria = all_criteria[index]
            variable_value = new_solution.get_binding(variable_criteria.variable_name).value
            if variable_value not in variable_stats.whole_group_unique_values:
                # Any variable that has (N, inf) on it and has met the criteria means that, if it generates more groups,
                # the only change is set membership in that variable so we don't need to remember this as a separate group
                if (variable_stats.current_state == CriteriaResult.meets or variable_stats.current_state == CriteriaResult.meets_pending_global) and \
                   variable_criteria.max_size == float('inf'):
                    continue

                return False

        # Either the values for variables with criteria already exist or
        # the ones that don't are already in the "meets" state for this solution
        # Either way, new_solution should be added to this set, a new set doesn't
        # need to be created
        return True


class StatsGroup(object):
    def __init__(self):
        self.variable_stats = []

    def initialize(self, var_criteria):
        has_global_constraint = False
        constraints_are_open = True
        variable_has_inf_max = False
        previous_variable_stats = None
        for criteria in var_criteria:
            if criteria.global_criteria is not None:
                has_global_constraint = True

            if criteria.max_size == float('inf'):
                variable_has_inf_max = True
            else:
                constraints_are_open = False

            var_stats = VariableStats(criteria.variable_name)
            var_stats.prev_variable_stats = previous_variable_stats
            if previous_variable_stats is not None:
                previous_variable_stats.next_variable_stats = var_stats

            previous_variable_stats = var_stats
            self.variable_stats.append(var_stats)

        return has_global_constraint, variable_has_inf_max, constraints_are_open

    def copy(self):
        new_group = StatsGroup()
        previous_new_stat = None
        for stat in self.variable_stats:
            new_stat = VariableStats(stat.variable_name, stat.whole_group_unique_individuals.copy(), stat.whole_group_unique_values.copy())
            new_stat.prev_variable_stats = previous_new_stat
            if previous_new_stat is not None:
                previous_new_stat.next_variable_stats = new_stat
            new_group.variable_stats.append(new_stat)
            previous_new_stat = new_stat

        return new_group


class VariableStats(object):
    def __init__(self, variable_name, whole_group_unique_individuals=None, whole_group_unique_values=None):
        self.variable_name = variable_name
        self.whole_group_unique_individuals = set() if whole_group_unique_individuals is None else whole_group_unique_individuals
        self.whole_group_unique_values = {} if whole_group_unique_values is None else whole_group_unique_values
        self.prev_variable_stats = None
        self.next_variable_stats = None
        self.current_state = None

    def __repr__(self):
        return f"values={len(self.whole_group_unique_values)}, ind={len(self.whole_group_unique_individuals)}"

    # Check if this variable will be a valid coll/dist/cuml variable after
    # adding this solution to the group this stats is tracking
    # Succeeds if the group, only considering this variable, can be interpreted as any (or multiple) of
    # cumulative/collective/distributive across all variables
    def add_solution(self, execution_context, variable_criteria, solution):
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
            cumulative_state = variable_criteria.meets_criteria(execution_context, self.whole_group_unique_individuals)
            if cumulative_state == CriteriaResult.meets:
                self.current_state = CriteriaResult.meets
                return self.current_state

            # Distributive
            # for each prev_unique_value: len(unique_values) meets criteria
            distributive_state = CriteriaResult.meets
            for prev_unique_value_item in self.prev_variable_stats.whole_group_unique_values.items():
                distributive_value_state = variable_criteria.meets_criteria(execution_context, prev_unique_value_item[1][0])
                distributive_state = criteria_transitions[distributive_state][distributive_value_state]
                if distributive_state == CriteriaResult.fail_one:
                    break

            if distributive_state == CriteriaResult.meets:
                self.current_state = CriteriaResult.meets
                return self.current_state

            self.current_state = CriteriaResult.contender if cumulative_state == CriteriaResult.contender or distributive_state == CriteriaResult.contender else CriteriaResult.fail_one
            return self.current_state

        elif prev_unique_value_count is None or prev_unique_value_count == 1:
            # Collective
            self.current_state = variable_criteria.meets_criteria(execution_context, self.whole_group_unique_individuals)
            return self.current_state

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
def check_criteria_all(execution_context, var_criteria, current_set_stats, new_solution):
    new_set_state = CriteriaResult.meets
    for index in range(len(var_criteria)):
        variable_stats = current_set_stats.variable_stats[index]
        criteria = var_criteria[index]
        state = variable_stats.add_solution(execution_context, criteria, new_solution)
        new_set_state = criteria_transitions[new_set_state][state]
        if new_set_state == CriteriaResult.fail_one or new_set_state == CriteriaResult.fail_all:
            return new_set_state

    return new_set_state


# if global_criteria is not set, then this only guarantees that the min and max size will be retained
# within a particular solution group. The count of that item *across* groups could be bigger.
class VariableCriteria(object):
    def __init__(self, predication, variable_name, min_size=1, max_size=float('inf'), global_criteria=None):
        self.predication_index = predication.index
        self.predication = predication
        self.variable_name = variable_name
        self.global_criteria = global_criteria
        self.min_size = min_size
        self.max_size = max_size
        self._unique_rstrs = set()
        self._after_phrase_error_location = ["AfterFullPhrase", self.variable_name]
        if parse_predication_name(predication.name)["Pos"] == "q":
            self._predication_error_location = ["AtPredication", predication.args[2], variable_name]
        else:
            self._predication_error_location = ["AtPredication", predication, variable_name]

    def __repr__(self):
        return f"{{{self.variable_name}: min={self.min_size}, max={self.max_size}, global={self.global_criteria}, pred={self.predication.name}({self.predication.args[0]})}}"

    # Numbers can only increase so ...
    def meets_criteria(self, execution_context, value_list):
        values_count = count_set(value_list)

        if self.global_criteria:
            # "Only/Exactly", much like the quantifier "the" does more than just group solutions into groups
            # ("only 2 files are in the folder") it also limits *all* the solutions to that number.
            # So we need to track unique values across all answers in this case
            self._unique_rstrs.update(value_list)

        if values_count > self.max_size:
            # It'll never get smaller so it fails forever
            execution_context.report_error_for_index(self.predication_index, ["moreThan", self._after_phrase_error_location, self.max_size])
            return CriteriaResult.fail_one

        elif values_count < self.min_size:
            execution_context.report_error_for_index(self.predication_index, ["lessThan", self._after_phrase_error_location, self.min_size])
            return CriteriaResult.contender

        else:
            # values_count >= self.min_size and values_count <= self.max_size
            if self.global_criteria == GlobalCriteria.exactly or self.global_criteria == GlobalCriteria.all_rstr_meet_criteria:
                # We can fail immediately if we have too many
                if len(self._unique_rstrs) > self.max_size:
                    # This is definitely the reason why something failed (since we are failing it here), so force=True
                    execution_context.report_error_for_index(self.predication_index, ["moreThanN", self._after_phrase_error_location, self.max_size], force=True)
                    return CriteriaResult.fail_all

                else:
                    return CriteriaResult.meets_pending_global

            else:
                return CriteriaResult.meets

    # Only called at the very end after all solutions have been generated
    def meets_global_criteria(self, execution_context):
        if self.global_criteria == GlobalCriteria.all_rstr_meet_criteria:
            # If there are more or less than the number the user said "the" of, return that error
            # For "the" singular there must be only one
            is_plural = is_plural_from_tree_info(execution_context.tree_info, self.variable_name)
            all_rstr_values = execution_context.get_variable_execution_data(self.variable_name)["AllRstrValues"]

            if not is_plural and len(all_rstr_values) > 1:
                execution_context.report_error_for_index(self.predication_index, ["moreThan1", ["AtPredication", self.predication.args[2], self.variable_name]], force=True)
                return False

            if len(all_rstr_values) < self.min_size:
                execution_context.report_error_for_index(self.predication_index, ["lessThan", self._predication_error_location, self.min_size, ], force=True)
                return False

            elif len(all_rstr_values) > self.max_size:
                execution_context.report_error_for_index(self.predication_index, ["moreThan", self._predication_error_location, self.max_size], force=True)
                return False

            elif len(all_rstr_values) != len(self._unique_rstrs):
                execution_context.report_error_for_index(self.predication_index, ["notTrueForAll", self._predication_error_location], force=True)
                return False

        if self.global_criteria == GlobalCriteria.exactly or self.global_criteria == GlobalCriteria.all_rstr_meet_criteria:
            # Then check to make sure there wer as many in the solution as the user specified
            if len(self._unique_rstrs) < self.min_size:
                execution_context.report_error_for_index(self.predication_index, ["lessThan", self._after_phrase_error_location, self.min_size], force=True)
                return False

            elif len(self._unique_rstrs) > self.max_size:
                execution_context.report_error_for_index(self.predication_index, ["moreThan", self._after_phrase_error_location, self.max_size], force=True)
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
    all_rstr_meet_criteria = 1


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
