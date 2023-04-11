import itertools


# returns nonempty subsets of list items
from file_system_example.objects import Measurement


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
    sets = [[]]
    for i in s:
        new_sets = []
        for k in sets:
            new_set = k+[i]
            if min_size <= len(new_set) <= max_size:
                yield new_set
            new_sets.append(new_set)
        sets += new_sets


# Given a list of lists, returns another list of lists
# with all combinations of items from the original lists
# ensuring there is always one item from every list
def all_combinations_with_elements_from_all(list_of_lists):
    def nonempty_subsets_of_list_of_lists():
        for items in list_of_lists:
            yield all_nonempty_subsets_stream(items)

    all_combinations_of_each_list = nonempty_subsets_of_list_of_lists()
    for answer in itertools.product(*all_combinations_of_each_list):
        yield list(itertools.chain(*answer))


def in_equals(existing_values, new_value):
    for existing_value in existing_values:
        if new_value == existing_value:
            return True

    return False


def append_if_unique(existing_values, new_value):
    if not in_equals(existing_values, new_value):
        existing_values.append(new_value)


# Special cases things like Measurement that are a single object that represents a set
def count_set(rstr_value):
    if isinstance(rstr_value, (list, tuple)):
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
    print(list(all_combinations_with_elements_from_all([[0, 2], [1]])))
