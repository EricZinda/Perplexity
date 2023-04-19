import copy
import itertools
import logging
from perplexity.set_utilities import all_nonempty_subsets_stream, all_combinations_with_elements_from_all, count_set, \
    append_if_unique
from perplexity.utilities import is_plural, at_least_one_generator
from perplexity.variable_binding import VariableValueType
from perplexity.vocabulary import PluralType


# For phrases like "files are large" or "only 2 files are large" we need a gate around
# the quantifier that only returns answers if they meet some criteria
# Note that the thing being counted is the actual rstr values,
# so rstr_x = [a, b] would count as 2
def determiner_from_binding(state, binding):
    if binding.variable.determiner is not None:
        determiner_constraint = binding.variable.determiner[0]
        determiner_type = binding.variable.determiner[1]
        determiner_constraint_args = binding.variable.determiner[2]
        return [determiner_constraint, determiner_type, determiner_constraint_args]

    elif is_plural(state, binding.variable.name):
        # Plural determiner
        return ["number_constraint", "default", [1, float('inf'), False]]

    else:
        # A default singular determiner is not necessary because the quantifiers that
        # distinguish singular (like "the" and "only 1") already check for it.
        # Furthermore, adding it as ["number_constraint", "default", [1, 1, False]]
        # unnecessarily breaks optimizations that are possible in optimize_determiner_infos
        return


def quantifier_from_binding(state, binding):
    if binding.variable.quantifier is not None:
        quantifier_constraint = binding.variable.quantifier[0]
        quantifier_type = binding.variable.quantifier[1]
        quantifier_constraint_args = binding.variable.quantifier[2]
        return [quantifier_constraint, quantifier_type, quantifier_constraint_args]

    else:
        return None


# TODO: every call to this requires materializing the entire list
def build_determiner_group(solutions, determiner_variable_name):
    new_subsets = {}
    for solution in solutions:
        binding_value = solution.get_binding(determiner_variable_name).value
        if binding_value not in new_subsets:
            new_subsets[binding_value] = [solution]
        else:
            new_subsets[binding_value].append(solution)

    return new_subsets


def unique_objects_from_variables(variable_value_list):
    unique_objects = set()
    for variable_value in variable_value_list:
        for unique_object in variable_value:
            unique_objects.add(unique_object)
    return unique_objects


# Definitions:
# - A *adjective determiner* is an adjective that creates a numeric constraint on a particular `x` variable, such as `card(2,e,x)` or `much-many_a(e8,x3)`.
# - A *quantifier determiner* is a quantifier that creates a numeric constraint on a particular `x` variable, such as `_all_q(x3,RSTR,BODY)` or `_the_q(x3,RSTR,BODY)`
# - An *undetermined MRS* is formed by: 1) removing all determiner adjectives (and their modifiers), 2) converting all determiner quantifiers to "udef_q", 3) ignoring the `pl/sg` constraint on any variable.
# - An *undetermined solution* is formed by assigning a single non-empty set to every `x` variable in an undetermined MRS such that it is true.
# - A *determiner solution group* for `determiner(x)` is a group of undetermined solutions where the count of unique individuals across all `x` values in the group satisfies the determiner. It contains *subsets* (see next definition).
# - A *determiner solution group subset* is a subset of undetermined solutions in a determiner group. Except for the first time through, the solutions in a subset all contain the same `x` value.
#
# Algorithm:
# Start with an `ordered_determiner_list` of numeric determiners (adjective and quantifier) and a `previous_determiner_group` that starts as the set of all undetermined solutions.
#   `previous_determiner_group` starts with a single subset that contains all the solutions.
#
# Using the next determiner in `ordered_determiner_list` (`determiner(variable)`) and `previous_determiner_group`:
#     Find collective and distributive: For each `previous_subset` in `previous_determiner_group`:
#         Group all the solutions in `previous_subset` by unique `variable` values (where "value" means the entire variable value as a set, not the individuals in it). These form the `new_subsets`.
#         Find a group of the unique `variable` values just found that satisfies `determiner(variable)`.
#           These variable values may have duplicate objects, merge them into a unique set of objects
#         Form `new_determiner_group` using `new_subsets` that go with these unique variable values
#         Run the algorithm again after removing `determiner(variable)` from the list and using `new_determiner_group`
#     Find cumulative: Do the same but merge all subsets instead of iterating over each subset
#
# If all determiners are successful, the determiner group that remains at the end is a solution.
def determiner_solution_groups(execution_context, previous_determiner_group, determiner_variable_name, determiner_criteria, solution_group_combinatorial, is_last_determiner, max_answer_count=float('inf')):
    # Find collective and distributive:
    # For each `previous_subset` in `previous_determiner_group`
    for previous_subset in previous_determiner_group.items():
        yield from new_determiner_groups_helper(execution_context, previous_subset[1], determiner_variable_name, determiner_criteria, solution_group_combinatorial, is_last_determiner, max_answer_count)

    # Find cumulative:
    # Do the same but merge all subsets instead of iterating over each subset
    solutions = []
    for solution_list in previous_determiner_group.values():
        solutions.extend(solution_list)
    yield from new_determiner_groups_helper(execution_context, solutions, determiner_variable_name, determiner_criteria, solution_group_combinatorial, is_last_determiner, max_answer_count)


# Yields all determiner groups that satisfy determiner_criteria
def new_determiner_groups_helper(execution_context, solutions_orig, determiner_variable_name, determiner_criteria, solution_group_combinatorial, is_last_determiner, max_answer_count):
    # First get rid of combinatorial variables
    for solutions in solution_list_alternatives_without_combinatorial_variables(execution_context, determiner_variable_name, solutions_orig, solution_group_combinatorial):
        # Group all the solutions in `solutions` by unique `determiner_variable_name` values
        # (where "value" means the entire variable value as a set, not the individuals in it).
        # These form the `new_subsets`.
        new_subsets = build_determiner_group(solutions, determiner_variable_name)
        if solution_group_combinatorial:
            # COMBINATORIC: Find each subset of unique `variable` values from those just found that satisfies `determiner(variable)`
            for unique_values_combination_key_value in all_nonempty_subsets_stream(new_subsets.items(), min_size=1, max_size=max_answer_count):
                # Materialize the list because we need it later and the iterator will be exhausted
                unique_values_combination_key_value_list = list(unique_values_combination_key_value)
                # These variable values may have duplicate objects, merge them into a unique set of objects
                unique_objects = unique_objects_from_variables((unique_value_key_value[0] for unique_value_key_value in unique_values_combination_key_value_list))
                if determiner_criteria(unique_objects):
                    # Each variable value might have multiple solutions that go with it, so this means any combination of them will also work
                    # If we are not the last determiner, return all possible combinations of solutions that contained the assignments
                    # in case later determiners need them
                    if not is_last_determiner:
                        # COMBINATORIC: Return all combinations of the list of solutions that go with each rstr answer
                        # as long as there is at least one element from each
                        lists_of_value_solutions = [item[1] for item in unique_values_combination_key_value_list]
                        for possible_solution in all_combinations_with_elements_from_all(lists_of_value_solutions):
                            possible_solution_list = tuple([item for item in possible_solution])
                            yield build_determiner_group(possible_solution_list, determiner_variable_name)

                    else:
                        # The last determiner does not need to create groups outside of what it needs
                        # to do its job. Just return the new determiner group
                        determiner_group = dict()
                        for value in unique_values_combination_key_value_list:
                            determiner_group[value[0]] = value[1]

                        yield determiner_group

        else:
            unique_objects = unique_objects_from_variables(new_subsets.keys())
            if determiner_criteria(unique_objects):
                yield new_subsets


# Return an iterator that yields lists of solutions ("a solution list") without combinatorial variables.
# These are lists of solutions because: If variable_name is a combinatorial variable it means that any combination
#   of values in it are true, so as long as one from the group remains at the end, the solution group is still valid.
#       For solution_group_combinatorial=true, it is the equivalent of breaking it into N more alternative
#           solutions with each solution having one of the combinations of possible values
#       For solution_group_combinatorial=false, it means that the solutions can't be broken up and must all be true.
#           But: the combinatorial variable means that *any* of the combinations for that variable can be true
#           if we just include all combinations in the non-combinatorial list, it will require them all to be true which isn't right
#           so instead we have to try every alternative by generating an entire new answer list for each alternative
# If it is not a combinatorial value, it gets added, as is, to set_solution_list
def solution_list_alternatives_without_combinatorial_variables(execution_context, variable_name, solutions_orig, solution_group_combinatorial=False):
    variable_metadata = execution_context.get_variable_metadata(variable_name)
    variable_plural_type = variable_metadata["PluralType"]

    # set_solution_alternatives_list contains all the alternatives for
    # a combinatoric variable. set_solution_list contains all values that were not combinatoric
    set_solution_alternatives_list = []
    set_solution_list = []

    for solution in solutions_orig:
        binding = solution.get_binding(variable_name)
        if binding.variable.value_type == VariableValueType.combinatoric:
            # If variable_name is combinatoric, all of its appropriate alternative combinations
            # get added to set_solution_alternatives_list
            # Thus, if the variable_plural_type is collective, we only add sets > 1, etc
            min_size = 1
            max_size = None
            if variable_plural_type == PluralType.distributive:
                max_size = 1

            elif variable_plural_type == PluralType.collective:
                min_size = 2

            else:
                assert variable_plural_type == PluralType.all

            def binding_alternative_generator():
                # COMBINATORIC: return all subsets
                for subset in all_nonempty_subsets_stream(binding.value, min_size=min_size, max_size=max_size):
                    yield solution.set_x(variable_name, subset, VariableValueType.set)

            binding_alternatives = binding_alternative_generator()
            set_solution_alternatives_list.append(binding_alternatives)

        else:
            set_solution_list.append(solution)

    # Flatten out the list of lists since they are all alternatives of the same variable
    if len(set_solution_alternatives_list) > 0:
        determiner_logger.debug(f"Found {len(set_solution_alternatives_list)} combinatoric answers")
        temp = [item for item in itertools.chain.from_iterable(set_solution_alternatives_list)]
        set_solution_alternatives_list = temp

    # Now the combination of set_solution_alternatives_list together with set_solution_list contain
    # all the alternative assignments of variable_name. Next, yield each combined alternative
    if solution_group_combinatorial:
        def combinatorial_solution_group_generator():
            for item in itertools.chain.from_iterable([set_solution_list, set_solution_alternatives_list]):
                if determiner_logger.isEnabledFor(logging.DEBUG):
                    determiner_logger.debug(f"Combinatorial answer: {item}")
                yield item

        yield combinatorial_solution_group_generator()

    else:
        determiner_logger.debug(f"Answers are not combinatorial")
        # See comments at top of function for what this is doing
        set_solution_alternatives_list = at_least_one_generator(set_solution_alternatives_list)
        alternative_yielded = False
        if set_solution_alternatives_list is not None:
            # COMBINATORIC:
            for alternative_list in all_nonempty_subsets_stream(set_solution_alternatives_list):
                # First add all the solutions that are shared between the alternatives
                # because they weren't combinatorial. Then add this combinatorial alternative
                def combinatorial_solution_group_generator():
                    yield from itertools.chain.from_iterable([copy.deepcopy(set_solution_list), alternative_list])

                yield combinatorial_solution_group_generator()
                alternative_yielded = True

        if not alternative_yielded:
            yield solutions_orig


# Set max to float('inf') to mean "no maximum"
def between_determiner(execution_context, determiner_variable_name, predication, all_rstr, previous_determiner_group, combinatorial, is_last_determiner, min_count, max_count, exactly):
    def criteria(rstr_value_list):
        cardinal_group_values_count = count_set(rstr_value_list)
        error_location = ["AfterFullPhrase", determiner_variable_name]

        # Even though this *looks* like exactly, it is picking out solutions where there just happen to be
        # N files, so it isn't really
        if cardinal_group_values_count > max_count:
            execution_context.report_error_for_index(0, ["moreThan", error_location, max_count], force=True)
            return False

        elif cardinal_group_values_count < min_count:
            execution_context.report_error_for_index(0, ["lessThan", error_location, min_count], force=True)
            return False

        else:
            nonlocal group_rstr
            group_rstr = rstr_value_list
            return True

    if exactly:
        error_location = ["AfterFullPhrase", determiner_variable_name]

        # "Only/Exactly", much like the quantifier "the" does more than just group solutions into groups ("only 2 files are in the folder")
        # it also limits *all* the solutions to that number. So we need to go to the bitter end before we know that that are "only 2"
        # group_rstr is set in the criteria each time a rstr is checked
        group_rstr = []
        unique_rstrs = set()
        groups = []
        for group in determiner_solution_groups(execution_context, previous_determiner_group, determiner_variable_name, criteria, combinatorial, is_last_determiner, max_count):
            for item in group_rstr:
                append_if_unique(unique_rstrs, item)

            if len(unique_rstrs) > max_count:
                execution_context.report_error_for_index(0, ["moreThan", error_location, max_count], force=True)
                return

            else:
                groups.append(group)

        if len(unique_rstrs) < min_count:
            execution_context.report_error_for_index(0, ["lessThan", error_location, min_count], force=True)
            return

        else:
            yield from groups

    else:
        yield from determiner_solution_groups(execution_context, previous_determiner_group, determiner_variable_name, criteria, combinatorial, is_last_determiner, max_count)


determiner_logger = logging.getLogger('Determiners')
