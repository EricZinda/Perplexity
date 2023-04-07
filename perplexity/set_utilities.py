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


# Given a list of lists, returns another list of lists
# with all combinations of items from the original lists
# ensuring there is always one item from every list
def all_combinations_with_elements_from_all(list_of_lists):
    all_combinations_of_each_list = [all_nonempty_subsets(items) for items in list_of_lists]
    combs = [list(itertools.chain(*answer)) for answer in itertools.product(*all_combinations_of_each_list)]
    return combs


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
    print(list(all_combinations_with_elements_from_all([[[1], [2], [3]]])))
