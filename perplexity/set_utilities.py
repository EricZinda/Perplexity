import itertools


# returns nonempty subsets of list items
def all_nonempty_subsets(items):
    subsets = []
    n = len(items)
    for i in range(1, n + 1):
        subsets.extend(itertools.combinations(items, i))

    return subsets


# Given a list of lists, returns another list of lists
# with all combinations of items from the original lists
# ensuring there is always one item from every list
def all_combinations_with_elements_from_all(list_of_lists):
    all_combinations_of_each_list = [all_nonempty_subsets(items) for items in list_of_lists]
    combs = [list(itertools.chain(*answer)) for answer in itertools.product(*all_combinations_of_each_list)]
    return combs


def append_if_unique(existing_values, new_value):
    unique = True
    for existing_value in existing_values:
        if new_value == existing_value:
            unique = False
            break

    if unique:
        existing_values.append(new_value)


if __name__ == '__main__':
    print(list(all_combinations_with_elements_from_all([[[1], [2], [3]]])))
