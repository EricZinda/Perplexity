import copy
import enum
import itertools


class Measurement(object):
    def __init__(self, measurement_type, count):
        self.measurement_type = measurement_type
        self.count = count
        self._hash = hash((self.measurement_type, self.count))

    def __hash__(self):
        return self._hash

    def __eq__(self, other):
        if isinstance(other, Measurement) and self._hash == other._hash:
            return self.measurement_type == other.measurement_type and self.count == other.count

        else:
            return False

    def __ne__(self, other):
        return not self == other

    def __repr__(self):
        return "Measure:" + str(self.count) + " " + str(self.measurement_type)


# returns nonempty subsets of list items
def all_nonempty_subsets(items, min_size=1, max_size=None):
    subsets = []
    if max_size is None:
        n = len(items)
    else:
        n = min(max_size, len(items))

    for i in range(min_size, n + 1):
        subsets.extend(itertools.combinations(items, i))

    return subsets


# iteratively returns lists that are all nonempty subsets of s
# From https://stackoverflow.com/questions/1482308/how-to-get-all-subsets-of-a-set-powerset
#  Doesn't require len(s) and can stream its answers without materializing the whole list up front.
#  It also builds the combinations in a way that only pulls new items from s after all combinations
#  of previous answers are generated -- also good for streaming!
# float('inf') will be greater than any number since python can compare floats and ints
def all_nonempty_subsets_stream(s, min_size=1, max_size=float('inf')):
    sets = [()]
    for i in s:
        new_sets = []
        for k in sets:
            new_set = k+(i,)
            if min_size <= len(new_set) <= max_size:
                yield new_set
            new_sets.append(new_set)
        sets += new_sets


class CriteriaResult(enum.Enum):
    meets = 0
    contender = 1
    fail = 2


class VariableCriteria(object):
    def __init__(self, variable_name, min_size=1, max_size=float('inf')):
        self.variable_name = variable_name
        self.min_size = min_size
        self.max_size = max_size

    # Numbers can only increase so ...
    def meets_criteria(self, count):
        if count > self.max_size:
            # It'll never get smaller so it fails forever
            return CriteriaResult.fail

        elif count < self.min_size:
            return CriteriaResult.contender

        else:
            # count >= self.min_size and count <= self.max_size
            return CriteriaResult.meets


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
            cumulative_state = variable_criteria.meets_criteria(count_set(self.whole_group_unique_individuals))
            if cumulative_state == CriteriaResult.meets:
                return CriteriaResult.meets

            # Distributive
            # for each prev_unique_value: len(unique_values) meets criteria
            distributive_state = CriteriaResult.meets
            for prev_unique_value_item in self.prev_variable_stats.whole_group_unique_values.items():
                distributive_value_state = variable_criteria.meets_criteria(count_set(prev_unique_value_item[1][0]))
                distributive_state = criteria_transitions[distributive_state][distributive_value_state]
                if distributive_state == CriteriaResult.fail:
                    break

            if distributive_state == CriteriaResult.meets:
                return CriteriaResult.meets

            return CriteriaResult.contender if cumulative_state == CriteriaResult.contender or distributive_state == CriteriaResult.contender else CriteriaResult.fail

        elif prev_unique_value_count is None or prev_unique_value_count == 1:
            # Collective
            return variable_criteria.meets_criteria(count_set(self.whole_group_unique_individuals))


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
        if new_set_state == CriteriaResult.fail:
            return CriteriaResult.fail

    return new_set_state


def all_nonempty_subsets_var_all_stream(solutions, var_criteria):
    initial_stats = []
    for criteria in var_criteria:
        var_stats = GroupVariableStats(criteria.variable_name)
        initial_stats.append(var_stats)

    for stat_index in range(len(initial_stats)):
        prev_stat = None if stat_index == 0 else initial_stats[stat_index - 1]
        next_stat = None if stat_index + 1 == len(initial_stats) else initial_stats[stat_index + 1]
        initial_stats[stat_index].prev_variable_stats = prev_stat
        initial_stats[stat_index].next_variable_stats = next_stat

    sets = [(initial_stats, ())]
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

            elif state == CriteriaResult.contender:
                # - contender (but doesn't meet yet): add to the set but don't yield
                new_set = (new_set_criteria, k[1] + (i,))
                new_sets.append(new_set)

            elif state == CriteriaResult.fail:
                #   - fail (doesn't meet ): don't add don't yield
                continue

        sets += new_sets


criteria_transitions = {CriteriaResult.meets: {CriteriaResult.meets: CriteriaResult.meets,
                                               CriteriaResult.contender: CriteriaResult.contender,
                                               CriteriaResult.fail: CriteriaResult.fail},
                        CriteriaResult.contender: {CriteriaResult.meets: CriteriaResult.contender,
                                                   CriteriaResult.contender: CriteriaResult.contender,
                                                   CriteriaResult.fail: CriteriaResult.fail},
                        CriteriaResult.fail: {CriteriaResult.meets: CriteriaResult.fail,
                                              CriteriaResult.contender: CriteriaResult.fail,
                                              CriteriaResult.fail: CriteriaResult.fail}
                        }


def all_nonempty_subsets_of_list_of_lists_stream(list_of_lists):
    for items in list_of_lists:
        yield all_nonempty_subsets_stream(items)


def product_stream(*args, repeat=1):
    """Find the Cartesian product of the arguments.

    The interface is identical to itertools.product.
    """
    def index_from_stream(array_stream, index):
        try:
            while index >= len(array_stream[0]):
                next_element = next(array_stream[1])
                array_stream[0].append(next_element)

            return True, array_stream[0][index]

        except StopIteration:
            return False, None

    # Initialize data structures and handle bad input
    if len(args) == 0:
        # Match behavior of itertools.product
        yield ()
        return

    gears = [([], arg) for arg in args] * repeat
    for gear in gears:
        if not index_from_stream(gear, 0)[0]:
            return

    tooth_numbers = [0] * len(gears)
    result = [index_from_stream(gear, 0)[1] for gear in gears]

    # Rotate through all gears
    last_gear_number = len(gears) - 1
    finished = False
    while not finished:
        yield tuple(result)

        # Get next result
        gear_number = last_gear_number
        while gear_number >= 0:
            gear = gears[gear_number]
            tooth_number = tooth_numbers[gear_number] + 1
            has_tooth, gear_tooth_value = index_from_stream(gear, tooth_number)
            if has_tooth:
                # No gear change is necessary, so exit the loop
                result[gear_number] = gear_tooth_value
                tooth_numbers[gear_number] = tooth_number
                break

            _, result[gear_number] = index_from_stream(gear, 0)
            tooth_numbers[gear_number] = 0
            gear_number -= 1

        else:
            # We changed all the gears, so we are back at the beginning
            finished = True


# Given a list of lists, returns another list of lists
# with all combinations of items from the original lists
# ensuring there is always one item from every list
def all_combinations_with_elements_from_all(list_of_lists):
    all_combinations_of_each_list = all_nonempty_subsets_of_list_of_lists_stream(list_of_lists)
    for answer in product_stream(*all_combinations_of_each_list):
        yield itertools.chain(*answer)


def in_equals(existing_values, new_value):
    for existing_value in existing_values:
        if new_value == existing_value:
            return True

    return False


def append_if_unique(existing_values_set, new_value):
    if new_value not in existing_values_set:
        existing_values_set.add(new_value)


# Special cases things like Measurement that are a single object that represents a set
def count_set(rstr_value):
    if isinstance(rstr_value, set):
        if len(rstr_value) == 1:
            value = next(iter(rstr_value))
            if isinstance(value, Measurement):
                return value.count
        return len(rstr_value)

    elif isinstance(rstr_value, (list, tuple)):
        if len(rstr_value) == 1 and isinstance(rstr_value[0], Measurement):
            return rstr_value[0].count
        else:
            return len(rstr_value)

    else:
        if isinstance(rstr_value, Measurement):
            return rstr_value.count
        else:
            return 1


if __name__ == '__main__':
    pass