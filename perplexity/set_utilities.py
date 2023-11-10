import itertools


# Creating a CachedIterable(iterable) allows the caller to treat the CachedIterable()
# like a materialized list by accessing with an index or iterating over it.
# BUT: it does not actually materialize the list more than it has to. So, multiple
# iterators can be started on it, and they will share the same underlying (perhaps partially)
# materialized list.
# Not threadsafe.
class CachedIterable(object):
    class CachedIterator(object):
        def __init__(self, cached_iterable):
            self._cached_iterable = cached_iterable
            self.next_index = 0

        def __next__(self):
            value = self._cached_iterable.get_from_index(self.next_index)
            self.next_index += 1
            return value

    def __init__(self, iterable):
        # This is the main iterator that will materialize
        # the underlying data, *as needed*
        self.iterator = iter(iterable)
        self.done = False
        self.cached_values = []

    def __iter__(self):
        return CachedIterable.CachedIterator(self)

    def __getitem__(self, key):
        try:
            return self.get_from_index(key)

        except StopIteration:
            raise IndexError

    def get_from_index(self, index):
        try:
            while index >= len(self.cached_values):
                if self.done:
                    raise StopIteration
                self.cached_values.append(next(self.iterator))

        except StopIteration:
            self.done = True
            raise

        return self.cached_values[index]


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


class DisjunctionValue(object):
    def __init__(self, lineage, value):
        self.lineage = lineage
        self.value = value

    def __repr__(self):
        return f"{self.lineage}->{self.value}"


# Iterable that returns generators which represent disjunctions.
#   The returned generators return sets (represented as tuples) representing all combinations
#       of values determined by the sizes passed in
# Passed a value_generator that can either just return values or
# can return a list, where the first item in the list is the lineage
class DisjunctionIterable(object):
    def __init__(self, value_generator, min_size=1, max_size=float('inf')):
        self.generator = value_generator
        self.min_size = min_size
        self.max_size = max_size
        self.lineage = None
        self.cached_item = None

    def __next__(self):
        def disjunction_generator():
            sets = [()]
            while True:
                try:
                    next_item = self._next_item()

                except StopIteration:
                    self.generator = None
                    return

                if isinstance(next_item, DisjunctionValue):
                    next_lineage = next_item.lineage
                    next_value = next_item.value

                else:
                    next_lineage = ""
                    next_value = next_item

                if self.lineage is None:
                    self.lineage = next_lineage

                elif self.lineage != next_lineage:
                    self.push_cached_item(next_item, next_lineage)
                    return

                new_sets = []
                for k in sets:
                    new_set = k+(next_value,)
                    if self.min_size <= len(new_set) <= self.max_size:
                        yield self.lineage, new_set
                    if len(new_set) < self.max_size:
                        # Only add the set to the list of sets if its length is such
                        # that it can still be added to.  Otherwise, it just generates
                        # alternatives that will never be used
                        new_sets.append(new_set)
                sets += new_sets

        if self.generator is None:
            raise StopIteration

        else:
            return disjunction_generator()

    def __iter__(self):
        return self

    def push_cached_item(self, value, lineage):
        assert self.cached_item is None
        self.cached_item = value
        self.lineage = lineage

    def _next_item(self):
        if self.cached_item:
            value = self.cached_item
            self.cached_item = None
            return value
        else:
            return next(self.generator)


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
            if len(new_set) < max_size:
                # Only add the set to the list of sets if its length is such
                # that it can still be added to.  Otherwise, it just generates
                # alternatives that will never be used
                new_sets.append(new_set)
        sets += new_sets


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
                if isinstance(value.count, str):
                    # This means it is a representing an unbound variable
                    # and it will be marked as singular
                    return 1
                else:
                    return value.count

        return len(rstr_value)

    elif isinstance(rstr_value, (list, tuple)):
        if len(rstr_value) == 1 and isinstance(rstr_value[0], Measurement):
            if isinstance(rstr_value[0].count, str):
                # This means it is a representing an unbound variable
                # and it will be marked as singular
                return 1
            else:
                return rstr_value[0].count
        else:
            return len(rstr_value)

    else:
        if isinstance(rstr_value, Measurement):
            if isinstance(rstr_value.count, str):
                # This means it is a representing an unbound variable
                # and it will be marked as singular
                return 1
            else:
                return rstr_value.count
        else:
            return 1


if __name__ == '__main__':
    pass