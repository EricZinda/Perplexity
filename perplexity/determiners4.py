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
    has_global_constraint, variable_has_inf_max = initial_stats_group.initialize(var_criteria)

    return variable_metadata, initial_stats_group, has_global_constraint, variable_has_inf_max


# Every set that is generated has a StatsGroup object that does all
# the counting that we need to see if it meets the criteria
#
# New groups are created by copying an existing set and adding a new solution into it
# or merging in special cases.
#
# Criteria like "the" and "only" (as in "only 2") also need to track information *across groups*
# to ensure there is "only 2" solutions generated. This is tracked in the criteria object itself
# since it is reused across the sets
#
# yields: solution_group, set_id
# set_id is a lineage like 1:3:5 ... so that the caller can detect when a solution is just more rows in an existing set_id by seeing
# if it came from a previous group
def all_plural_groups_stream(execution_context, solutions, var_criteria, variable_metadata, initial_stats_group, has_global_constraint, variable_has_inf_max):
    # Give a unique set_id to every group that gets created
    set_id = 0
    sets = [[initial_stats_group, [], str(set_id)]]
    set_id += 1

    # Track the unique solution groups that are returned so we
    # can stop after we have 2 since that is all we need
    unique_solution_groups = []

    # Track solution groups that work so far, but need to wait till the end
    # because they require a global criteria to be true
    pending_global_criteria = []

    # Cases when we know we have failed early (early_fail_quit) and when we know we
    # have a solution early (early_success_quit)
    early_fail_quit = False
    early_success_quit = False
    for combinatorial_solution in solutions:
        if early_success_quit:
            # If there are global constraints, we still need to gather the stats for all possible
            # rstrs (for GlobalCriteria.all_rstr_meet_criteria) or successful rstrs (for GlobalCriteria.exactly)
            # But we no longer need to check for coll/dist/cuml so it can be faster
            if not check_only_global_criteria_all(execution_context, var_criteria, combinatorial_solution):
                early_fail_quit = True
                break

        else:
            for next_solution in expand_combinatorial_variables(variable_metadata, combinatorial_solution):
                # unique_solution_groups tracks solution groups that we have returned so far
                if unique_solution_groups is not None and len(unique_solution_groups) == 2:
                    if not variable_has_inf_max:
                        # We are looking for a minimal solution if max != inf, so we can quit early
                        early_success_quit = True
                        break

                    else:
                        # Otherwise, just switch to only developing the two groups we need to return
                        # By setting "sets" to be just those groups
                        sets = unique_solution_groups
                        unique_solution_groups = None

                new_sets = []
                for existing_set in sets:
                    new_set_stats_group = existing_set[0].copy()
                    force_new_group, state = check_criteria_all(execution_context, var_criteria,  new_set_stats_group, next_solution)

                    if state == CriteriaResult.fail_one:
                        # Fail (doesn't meet criteria): don't add, don't yield
                        continue

                    elif state == CriteriaResult.fail_all:
                        # A global criteria wasn't met so none will ever work
                        # Still run global constraints to get a good error
                        early_fail_quit = True
                        break

                    else:
                        # Didn't fail, decide whether to merge into the existing set or create a new one
                        # Merge if the only variables that got updated had a criteria with an upper bound of inf
                        # since alternatives won't be used anyway
                        if force_new_group:
                            new_set = [None, None, existing_set[2] + ":" + str(set_id)]
                            set_id += 1
                            new_sets.append(new_set)

                        else:
                            new_set = existing_set

                        new_set[0] = new_set_stats_group
                        new_set[1] = existing_set[1] + [next_solution]

                        if state == CriteriaResult.meets:
                            yield new_set[1], new_set[2]

                        elif state == CriteriaResult.meets_pending_global:
                            pending_global_criteria.append([new_set[1], new_set[2]])

                        elif state == CriteriaResult.contender:
                            # Not yet a solution, don't track it as one
                            pass

                        # Why does force_new_group need to be true?
                        #
                        # force_new_group is only False if:
                        # a) no variables being tracked changed
                        # or
                        # b) every variable being tracked has an upper limit of inf
                        #
                        # If no variables changed, then this can't be a new solution because, if it was, the previous would have been so it would already have been tracked
                        # If every variable has an upper limit of inf then we will only generate one solution group since they will always be merged
                        # So we don't need to do this optimization
                        if force_new_group and (state == CriteriaResult.meets or state == CriteriaResult.meets_pending_global) and \
                                unique_solution_groups is not None:
                            # We still haven't transitioned to tracking only the two solution groups
                            # So: add this one if it just transitioned from contender to solution group
                            # If we haven't yet found 2
                            if existing_set[0].group_state not in [CriteriaResult.meets, CriteriaResult.meets_pending_global] and \
                                    len(unique_solution_groups) < 2:
                                unique_solution_groups.append(new_set)

                sets += new_sets

                if early_fail_quit:
                    break

            if early_fail_quit:
                break

    # If early_fail_quit is True, the error should already be set
    if not early_fail_quit and has_global_constraint:
        for criteria in var_criteria:
            if not criteria.meets_global_criteria(execution_context):
                return

        yield from pending_global_criteria


class StatsGroup(object):
    def __init__(self, variable_has_inf_max=False, group_state=None):
        self.variable_stats = []
        self.variable_has_inf_max = variable_has_inf_max
        self.group_state = group_state

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
        new_group = StatsGroup(self.variable_has_inf_max, self.group_state)
        previous_new_stat = None
        for stat in self.variable_stats:
            new_stat = VariableStats(stat.variable_name, stat.whole_group_unique_individuals.copy(), stat.whole_group_unique_values.copy(), stat.distributive_state, stat.collective_state, stat.cumulative_state)
            new_stat.prev_variable_stats = previous_new_stat
            if previous_new_stat is not None:
                previous_new_stat.next_variable_stats = new_stat
            new_group.variable_stats.append(new_stat)
            previous_new_stat = new_stat

        return new_group


class VariableStats(object):
    def __init__(self, variable_name, whole_group_unique_individuals=None, whole_group_unique_values=None, distributive_state=None, collective_state=None, cumulative_state=None):
        self.variable_name = variable_name
        self.whole_group_unique_individuals = set() if whole_group_unique_individuals is None else whole_group_unique_individuals
        self.whole_group_unique_values = {} if whole_group_unique_values is None else whole_group_unique_values
        self.prev_variable_stats = None
        self.next_variable_stats = None
        self.current_state = None

        self.distributive_state = None if distributive_state is None else distributive_state
        self.collective_state = None if collective_state is None else collective_state
        self.cumulative_state = None if cumulative_state is None else cumulative_state

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
    # adding this solution to the group this stats is tracking
    # Succeeds if the group, only considering this variable, can be interpreted as any (or multiple) of
    # cumulative/collective/distributive across all variables
    def add_solution(self, execution_context, variable_criteria, solution):
        binding_value = solution.get_binding(self.variable_name).value
        if any([x not in self.whole_group_unique_individuals for x in binding_value]):
            new_individuals = True
            self.whole_group_unique_individuals.update(binding_value)

        else:
            new_individuals = False

        next_value = None if self.next_variable_stats is None else solution.get_binding(self.next_variable_stats.variable_name).value

        # Update the unique values mapping that is used for distributive readings
        if binding_value not in self.whole_group_unique_values:
            self.whole_group_unique_values[binding_value] = [set(next_value if next_value is not None else []), [solution]]

        else:
            self.whole_group_unique_values[binding_value][0].update(next_value if next_value is not None else [])
            self.whole_group_unique_values[binding_value][1].append(solution)

        if self.prev_variable_stats is None:
            prev_unique_value_count = None

        else:
            prev_unique_value_count = len(self.prev_variable_stats.whole_group_unique_values)

        if prev_unique_value_count is not None and prev_unique_value_count > 1:
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

        if prev_unique_value_count is None or prev_unique_value_count == 1:
            if self.collective_state != CriteriaResult.fail_one:
                # Collective
                self.collective_state = variable_criteria.meets_criteria(execution_context, self.whole_group_unique_individuals)

        else:
            self.collective_state = CriteriaResult.fail_one

        # Now figure out what to return
        if self.collective_state == CriteriaResult.fail_all or \
                self.distributive_state == CriteriaResult.fail_all or \
                self.cumulative_state == CriteriaResult.fail_all:
            self.current_state = CriteriaResult.fail_all

        elif self.collective_state == CriteriaResult.meets_pending_global or \
                self.distributive_state == CriteriaResult.meets_pending_global or \
                self.cumulative_state == CriteriaResult.meets_pending_global:
            self.current_state = CriteriaResult.meets_pending_global

        elif self.collective_state == CriteriaResult.meets or \
                self.distributive_state == CriteriaResult.meets or \
                self.cumulative_state == CriteriaResult.meets:
            self.current_state = CriteriaResult.meets

        elif self.collective_state == CriteriaResult.contender or \
                self.distributive_state == CriteriaResult.contender or \
                self.cumulative_state == CriteriaResult.contender:
            self.current_state = CriteriaResult.contender

        else:
            self.current_state = CriteriaResult.fail_one

        return new_individuals, self.current_state


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
def check_criteria_all(execution_context, var_criteria, new_set_stats_group, new_solution):
    current_set_state = CriteriaResult.meets
    force_new_group = False
    for index in range(len(var_criteria)):
        # Get the existing statistics for the variable at this index
        # and the criteria for the variable as well
        variable_stats = new_set_stats_group.variable_stats[index]
        criteria = var_criteria[index]

        # See what the CriteriaResult is for the whole solution group plus the new solution
        # but only for this particular variable
        new_individuals, state = variable_stats.add_solution(execution_context, criteria, new_solution)

        # Decide the new state of the entire solution group, so far, based on the previous variable
        # state and the new state
        current_set_state = criteria_transitions[current_set_state][state]
        if current_set_state == CriteriaResult.fail_one or current_set_state == CriteriaResult.fail_all:
            new_set_stats_group.group_state = current_set_state
            return None, current_set_state

        # If the value in new_solution for the current variable actually added a new value to the set of values
        # being tracked, and the criteria for this variable doesn't have an upper bound of inf,
        # then we need to create a new group because we need to generate alternatives from it
        if new_individuals and criteria.max_size != float('inf'):
            force_new_group = True

    new_set_stats_group.group_state = current_set_state
    return force_new_group, current_set_state


# Called if we can shortcut because we have already found the answers but we still need to check global constraints
# The set of unique individuals needed to check that "only 2 ..." are collected in the criteria
# So we can rip through all the solutions and run the criteria to see if global criteria are met, ignoring coll/etc.
def check_only_global_criteria_all(execution_context, var_criteria, new_solution):
    for index in range(len(var_criteria)):
        criteria = var_criteria[index]
        binding_value = new_solution.get_binding(criteria.variable_name).value
        criteria_state = criteria.meets_criteria(execution_context, binding_value)
        if criteria_state == CriteriaResult.fail_all:
            False

    return True


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

        if self.global_criteria == GlobalCriteria.exactly:
            # We can fail immediately if we have too many
            if len(self._unique_rstrs) > self.max_size:
                # This is definitely the reason why something failed (since we are failing it here), so force=True
                execution_context.report_error_for_index(self.predication_index, ["moreThanN", self._after_phrase_error_location, self.max_size], force=True)
                return CriteriaResult.fail_all

        if self.global_criteria == GlobalCriteria.all_rstr_meet_criteria:
            # We can fail immediately if we have too many
            if len(self._unique_rstrs) > self.max_size:
                # This is definitely the reason why something failed (since we are failing it here), so force=True
                execution_context.report_error_for_index(self.predication_index, ["moreThanN", self._predication_error_location, self.max_size], force=True)
                return CriteriaResult.fail_all

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
