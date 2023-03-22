import itertools
from file_system_example.objects import File, Folder, Megabyte, Measurement
from perplexity.cardinals import cardinal_from_binding, yield_all
from perplexity.execution import report_error, call
from perplexity.tree import is_index_predication, find_predication_from_introduced
from perplexity.utilities import is_plural
from perplexity.vocabulary import Vocabulary, Predication, EventOption


vocabulary = Vocabulary()


# Several meanings:
# 1. Means "this" which only succeeds for rstrs that are the single in scope x set and there are no others that are in scope
#       "put the two keys in the lock": should only work if there are only two keys in scope:
#       run the rstr, run the cardinal (potentially fail), the run the body (potentially fail)
# 2. Means "the one and only" which only succeeds if the rstr is a single set and there are no other sets
#       same approach
@Predication(vocabulary, names=["_the_q"])
def the_q(state, x_variable_binding, h_rstr, h_body):
    def the_behavior(cardinal_group_solutions):
        single_cardinal_group = None
        if len(cardinal_group_solutions) > 1:
            report_error(["moreThan1", ["AtPredication", h_body, x_variable_binding.variable.name]], force=True)
            return

        for cardinal_group in cardinal_group_solutions:
            # The file is large should fail if there is more than one "the file"
            # "The 2 files are large" should fail if there are more than 2 files but only 2 are large
            if len(cardinal_group.cardinal_group_values()) != len(cardinal_group.original_rstr_set):
                # There was not a single "the"
                report_error(["notTrueForAll", ["AtPredication", h_body, x_variable_binding.variable.name]], force=True)
                return

            elif single_cardinal_group is not None:
                report_error(["moreThan1", ["AtPredication", h_body, x_variable_binding.variable.name]], force=True)
                return

            else:
                single_cardinal_group = cardinal_group

        if single_cardinal_group is not None:
            yield from yield_all(single_cardinal_group.solutions)

    yield from quantifier_collector(state, x_variable_binding, h_rstr, h_body, the_behavior, cardinal_scoped_to_initial_rstr=True)


# "a" stops returning answers after a single solution works
@Predication(vocabulary, names=["_a_q"])
def a_q(state, x_variable_binding, h_rstr, h_body):
    def a_behavior(cardinal_group_solutions):
        # Return "a" (arbitrary) item, then stop
        if len(cardinal_group_solutions) > 0:
            yield from yield_all(cardinal_group_solutions[0].solutions)

    yield from quantifier_collector(state, x_variable_binding, h_rstr, h_body, a_behavior)


# The default quantifier just passes through all answers
@Predication(vocabulary, names=["udef_q", "which_q", "_which_q"])
def default_quantifier(state, x_variable_binding, h_rstr, h_body):
    def default_quantifier_behavior(cardinal_group_solutions):
        for cardinal_group_solution in cardinal_group_solutions:
            yield from yield_all(cardinal_group_solution.solutions)

    yield from quantifier_collector(state, x_variable_binding, h_rstr, h_body, default_quantifier_behavior)


class CardinalGroup(object):
    def __init__(self, variable_name, is_collective, original_rstr_set, solutions):
        assert not is_collective or (is_collective and len(solutions) == 1), \
            "collective cardinal groups can only have 1 solution"
        self.variable_name = variable_name
        self.is_collective = is_collective
        self.original_rstr_set = original_rstr_set
        self.solutions = solutions

    def cardinal_group_values(self):
        if self.is_collective:
            return self.solutions[0].get_binding(self.variable_name).value
        else:
            return [solution.get_binding(self.variable_name).value for solution in self.solutions]


# Implementation of all quantifiers that take cardinals and plurals into account
def quantifier_collector(state, x_variable_binding, h_rstr, h_body, quantifier_function, cardinal_scoped_to_initial_rstr=False):
    variable_name = x_variable_binding.variable.name

    # Run in both collective and distributive if it is plural
    modes = [True, False] if is_plural(state, x_variable_binding.variable.name) else [False]

    # Get a rstr set value.
    # This defines the cardinal group that needs to be checked in
    # collective and distributive mode.
    cardinal = None
    rstr_found = True
    for rstr_solution in call(state, h_rstr):
        rstr_found = True
        rstr_binding = rstr_solution.get_binding(variable_name)

        # Assume the cardinal is the same for all rstr values
        if cardinal is None:
            cardinal = cardinal_from_binding(state, h_body, rstr_binding)

        # rstr_solutions will have one entry for every solution given by the rstr
        # that entry may have many XVariableSolutions
        raw_group_solutions = []
        for is_collective in modes:

            # If the rstr forced x to an incompatible coll/dist mode (as in "x ate pizzas *together*"), fail this mode
            if rstr_binding.variable.is_collective is not None and rstr_binding.variable.is_collective != is_collective:
                continue

            if is_collective:
                for x_variable_solution in call(rstr_solution.set_x(variable_name, rstr_binding.value, is_collective=is_collective), h_body):
                    # Every collective answer is a different cardinal group
                    raw_group_solutions.append(CardinalGroup(variable_name=variable_name, is_collective=is_collective, original_rstr_set=rstr_binding.value, solutions=[x_variable_solution]))

            elif is_plural(state, variable_name):
                # If this is plural, all distributive answers *together* are a cardinal group
                x_variable_values = [[value] for value in rstr_binding.value]
                dist_cardinal_group_solutions = []
                for x_variable_value in x_variable_values:
                    for x_variable_solution in call(rstr_solution.set_x(variable_name, x_variable_value, is_collective=is_collective), h_body):
                        dist_cardinal_group_solutions.append(x_variable_solution)

                if len(dist_cardinal_group_solutions) > 0:
                    raw_group_solutions.append(CardinalGroup(variable_name=variable_name, is_collective=is_collective, original_rstr_set=rstr_binding.value, solutions=dist_cardinal_group_solutions))

            else:
                # If it is singular, each distributive answer is a cardinal group
                x_variable_values = [[value] for value in rstr_binding.value]
                for x_variable_value in x_variable_values:
                    for x_variable_solution in call(rstr_solution.set_x(variable_name, x_variable_value, is_collective=is_collective), h_body):
                        raw_group_solutions.append(CardinalGroup(variable_name=variable_name, is_collective=is_collective, original_rstr_set=rstr_binding.value, solutions=[x_variable_solution]))

    if not rstr_found:
        report_error(["doesntExist", ["AtPredication", h_body, variable_name]], force=True)
        return

    if len(raw_group_solutions) == 0:
        return

    else:
        # The cardinal tests if each set of cardinal group solutions meets a criteria like "a few x" or "2 x" or "more than a few x"
        # Its criteria must be true across all the values in the cardinal group

        # Run the cardinal over all the values in a cardinal group
        cardinal_group_solutions = []
        for cardinal_group in raw_group_solutions:
            if cardinal.meets_criteria(cardinal_group, cardinal_scoped_to_initial_rstr):
                cardinal_group_solutions.append(cardinal_group)

        # Evaluate the quantifier. It should quantify at the level of the cardinal group
        # So, "the 2 babies" can be true because it is a single "set of 2 babies" even in dist mode
        yield from quantifier_function(cardinal_group_solutions)


def variable_is_megabyte(binding):
    return binding.value is not None and len(binding.value) == 1 and isinstance(binding.value[0], Megabyte)


def variable_is_measure(binding):
    return binding.value is not None and len(binding.value) == 1 and isinstance(binding.value[0], Measurement)


# 10 mb should not generate a set of 10 1mbs
# special case this.  Turns a megabyte into a *measure* which is a set of megabytes
@Predication(vocabulary, names=["card"])
def card_megabytes(state, c_count, e_introduced_binding, x_target_binding):
    if variable_is_megabyte(x_target_binding):
        yield state.set_x(x_target_binding.variable.name, [Measurement(x_target_binding.value[0], int(c_count))], is_collective=True)


@Predication(vocabulary, names=["card"])
def card_normal(state, c_count, e_introduced_binding, x_target_binding):
    if not variable_is_megabyte(x_target_binding):
        yield state.set_x(x_target_binding.variable.name, x_target_binding.value,
                          cardinal=["cardinals.CardCardinal", [int(c_count)]])


@Predication(vocabulary, names=["_a+few_a_1"])
def a_few_a_1(state, e_introduced_binding, x_target_binding):
    yield state.set_x(x_target_binding.variable.name, x_target_binding.value, cardinal=["cardinals.BetweenCardinal", [3, 5]])


# Values come in, the job of the predication is to restrict them
# to something that is true for the predication and yield that state
# Whether they yield the values one by one (distributive) or as a set
# (collective) is determined by the variable metadata
@Predication(vocabulary, names=["_file_n_of"])
def file_n_of(state, x_binding, i_binding):
    if x_binding.value is None:
        # Unbound variable means "all things"
        # Restrict the values of x (i.e. the world) to "all files"
        iterator = state.all_individuals()

    else:
        # x is set to a set of values, restrict them to just files
        iterator = x_binding.value

    values = []
    for value in iterator:
        if isinstance(value, File):
            values.append(value)

    if len(values) > 0:
        yield state.set_x(x_binding.variable.name, values)


@Predication(vocabulary, names=["_folder_n_of"])
def folder_n_of(state, x_binding, i_binding):
    if x_binding.value is None:
        iterator = state.all_individuals()

    else:
        iterator = x_binding.value

    values = []
    for value in iterator:
        if isinstance(value, Folder):
            values.append(value)

    if len(values) > 0:
        yield state.set_x(x_binding.variable.name, values)


@Predication(vocabulary, names=["_megabyte_n_1"])
def megabyte_n_1(state, x_binding, u_binding):
    if x_binding.value is None:
        iterator = [Megabyte()]

    else:
        iterator = x_binding.value

    values = []
    for value in iterator:
        if isinstance(value, Megabyte):
            values.append(value)

    if len(values) > 0:
        yield state.set_x(x_binding.variable.name, values)

    else:
        report_error(["xIsNotYValue", x_binding.value, "megabyte"])


@Predication(vocabulary)
def thing(state, x_binding):
    if x_binding.value is None:
        iterator = state.all_individuals()

    else:
        iterator = x_binding.value

    values = []
    for value in iterator:
        values.append(value)

    if len(values) > 0:
        yield state.set_x(x_binding.variable.name, values)


# large_a operates in two modes:
#     as a verb, it will only work on sets of 1
#     as an adjective, it filters the set down
@Predication(vocabulary, names=["_large_a_1"], handles=[("DegreeMultiplier", EventOption.optional)])
def large_a_1(state, e_introduced_binding, x_target_binding):
    if is_index_predication(state) and len(x_target_binding.value) > 1:
        report_error(["notDist", x_target_binding.variable.name])
        return

    if x_target_binding.value is None:
        iterator = state.all_individuals()
    else:
        iterator = x_target_binding.value

    # See if any modifiers have changed *how* large
    # we should be
    degree_multiplier = degree_multiplier_from_event(state, e_introduced_binding)

    values = []
    for value in iterator:
        # Arbitrarily decide that "large" means a size greater
        # than 1,000,000 and apply any multipliers that other
        # predications set in the introduced event
        # Remember that "hasattr()" checks if an object has
        # a property
        if hasattr(value, 'size') and value.size > degree_multiplier * 1000000:
            values.append(value)

        else:
            report_error(["adjectiveDoesntApply", "large", x_target_binding.variable.name])

    if len(values) > 0:
        yield state.set_x(x_target_binding.variable.name, values)


# This is a helper function that any predication that can
# be "very'd" can use to understand just how "very'd" it is
def degree_multiplier_from_event(state, e_introduced_binding):
    # if a "very" is modifying this event, use that value
    # otherwise, return 1
    if e_introduced_binding.value is None or "DegreeMultiplier" not in e_introduced_binding.value:
        degree_multiplier = 1

    else:
        degree_multiplier = e_introduced_binding.value["DegreeMultiplier"]["Value"]

    return degree_multiplier


def in_p_loc(state, e_introduced_binding, x_actor_binding, x_location_binding):
    # restrict to just actors in location
    final_actors = []
    final_locations = []
    for actor in x_actor_binding.value:
        for location in x_location_binding.value:
            if actor in location:
                final_actors.append(actor)
                final_locations.append(location)

    if len(final_actors) > 0:
        yield state.set_x(x_actor_binding.variable.name, final_actors).set_x(x_location_binding.variable.name, final_locations)
    else:
        report_error(["thingHasNoLocation", x_actor_binding.variable.name, x_location_binding.variable.name])


# handles size only
# loc_nonsp will add up the size of files if a collective set of actors comes in, so declare that as handling them differently
# we treat megabytes as a group, all added up, which is different than separately (a megabyte as a time) so ditto
@Predication(vocabulary, names=["loc_nonsp"])
def loc_nonsp_size(state, e_introduced_binding, x_actor_binding, x_size_binding):
    if x_actor_binding.value is not None:
        if x_size_binding.value is not None:
            if variable_is_measure(x_size_binding):
                # Try to add up all combinations of x_actor_binding
                # to total x_size_binding
                for i in range(1, len(x_actor_binding.value) + 1):
                    for j in itertools.combinations(x_actor_binding.value, i):
                        total = 0
                        for actor in j:
                            if not hasattr(actor, "size_measurement"):
                                report_error(["xIsNotY", x_actor_binding.variable.name, x_size_binding.variable.name])
                                return
                            else:
                                total += actor.size_measurement().count

                        if x_size_binding.value[0].count == total:
                            yield state.set_x(x_actor_binding.variable.name, j)

                        else:
                            report_error(["xIsNotY", x_actor_binding.variable.name, x_size_binding.variable.name])


# Needed for "together, which 3 files are 3 mb?"
@Predication(vocabulary, names=["_together_p"])
def together_p_ee(state, e_introduced_binding, e_target_binding):
    yield from together_p_state(state, e_introduced_binding, e_target_binding)


@Predication(vocabulary, names=["_together_p"])
def together_p(state, e_introduced_binding, x_target_binding):
    yield from force_bindings_to_collective(state, [x_target_binding])


# This version doesn't add information to the target event, it just affects cardinal groupings
# together_p_state just acts like a restriction on all x args on its target predication
# it ensures that at least one of them is collective
#
# Two children ate two pizzas together could mean:
# 1. each child ate two pizzas at the same time
# 2. two children together ate two pizzas
# or both
# So, "together_p_state" needs to force the x variables in its target to have all combinations
# of coll/dist settings where there is at least one coll
# HOWEVER, it should only do this for variables that are "cardinal-bearing", meaning: those that are plurals
# otherwise, it will force things like "you" to be plural when the speaker didn't say it
@Predication(vocabulary, names=["_together_p_state"])
def together_p_state(state, e_introduced_binding, e_target_binding):
    # Figure out which x variables are on e_target_binding
    target_predication = find_predication_from_introduced(state.get_binding("tree").value["Tree"], e_target_binding.variable.name)
    target_x_args = target_predication.x_args()
    target_x_bindings = [state.get_binding(x_arg) for x_arg in target_x_args]
    yield from force_bindings_to_collective(state, target_x_bindings)


def force_bindings_to_collective(state, target_x_bindings):
    # First see if any of the variables are already collective and just force them to be used
    # in the answer by setting used_collective=True
    found_collective = False
    for binding in target_x_bindings:
        if binding.variable.is_collective:
            yield state
            return

    if not found_collective:
        # None of the target variables are collective, but one of them might not have been
        # set to coll/dist yet, and together() is here to set that value to collective.
        # Here's why it will only be one:
        # IF the predication it targets has N variables, then it *must* be the case that
        #   the target predication is in the tree under the quantifiers that declare those variables.
        #   This means that at most one of the ones that are plural should be left "uncardinalized"
        #   because it is either in the rstr or body of all the cardinals and those have set that value
        #   (BUT this requires that cardinalization is set *before* the rstr is run).
        #   Furthermore, this one variable would be the one that is quantified by the quantifier that
        #   the target predication is in the rstr of (if it is in the body it will be set and not uncardinalized)
        #   In the rstr, when we are looking for a value, we only set variable_binding.is_collective
        #   and leave the others unset to indicate this is what mode that variable is in.
        uncardinalized_binding = None
        for target_x_binding in target_x_bindings:
            if is_plural(state, target_x_binding.variable.name) and target_x_binding.variable.is_collective is None:
                assert uncardinalized_binding is None
                uncardinalized_binding = target_x_binding

        if uncardinalized_binding is not None:
            state = state.set_x(uncardinalized_binding.variable.name, uncardinalized_binding.value,
                                is_collective=True)
            yield state

        else:
            # If it id not find an existing collective binding and there isn't one to
            # set then "together" cant be run
            report_error(["formNotUnderstood", "missing", "collective"])
            return
