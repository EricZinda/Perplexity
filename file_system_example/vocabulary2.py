import itertools
from file_system_example.objects import File, Folder, Megabyte, Measurement
from perplexity.cardinals import cardinal_from_binding, StopQuantifierException, yield_all, count_rstr
from perplexity.execution import report_error, call
from perplexity.tree import is_index_predication, find_predication_from_introduced
from perplexity.utilities import is_plural
from perplexity.vocabulary import Vocabulary, Predication, EventOption


vocabulary = Vocabulary()


# "a" stops returning answers after a single solution works
@Predication(vocabulary, names=["_a_q"])
def a_q(state, x_variable_binding, h_rstr, h_body):
    def a_behavior(state, rstr_value, cardinal, h_body):
        yield state

        # We have returned "a" (arbitrary) item, stop
        raise StopQuantifierException

    yield from quantifier_implementation(state, x_variable_binding, h_rstr, h_body, a_behavior)


# The default quantifier just passes through all answers
@Predication(vocabulary, names=["udef_q", "which_q", "_which_q"])
def default_quantifier(state, x_variable_binding, h_rstr_orig, h_body_orig, reverse=False):
    h_rstr = h_body_orig if reverse else h_rstr_orig
    h_body = h_rstr_orig if reverse else h_body_orig

    def default_quantifier_behavior(state, rstr_value, cardinal, h_body):
        yield state

    yield from quantifier_implementation(state, x_variable_binding, h_rstr, h_body, default_quantifier_behavior)


# Implementation of all quantifiers that takes cardinals and plurals into account
def quantifier_implementation(state, x_variable_binding, h_rstr, h_body, behavior_function):
    variable_name = x_variable_binding.variable.name
    # Run in both collective and distributive if it is plural
    modes = [True, False] if is_plural(state, x_variable_binding.variable.name) else [False]

    # Return a better error if there aren't any rstrs at all
    rstr_found = False
    for is_collective in modes:
        # Get on set of rstr values first
        for rstr_solution in call(state, h_rstr):
            cardinal = None
            rstr_found = True

            # If the rstr forced x to an incompatible coll/dist mode (as in "x ate pizzas *together*"), fail this mode
            rstr_binding = rstr_solution.get_binding(variable_name)
            if rstr_binding.variable.is_collective is not None and rstr_binding.variable.is_collective != is_collective:
                report_error(["wrongMode"])
                break

            # Attempt to solve the body with these RSTRs
            try:
                if is_collective:
                    # Get each collective solution to the body
                    for body_solution in call(rstr_solution.set_x(variable_name, rstr_binding.value, is_collective=True), h_body):
                        # Cardinal criteria is set by running the rstr so we have to retrieve it here
                        cardinal = cardinal_from_binding(body_solution, h_body, body_solution.get_binding(variable_name))

                        # See if the cardinal criteria has been met yet
                        # For collective, the cardinal criteria applies to the single rstr set
                        for cardinal_criteria_met_answer in cardinal.yield_if_criteria_met(body_solution.get_binding(variable_name).value, [body_solution]):
                            # It has, so now let the quantifier decide if the answers are properly quantified
                            yield from behavior_function(cardinal_criteria_met_answer, body_solution.get_binding(variable_name).value, cardinal, h_body)

                else:
                    # Cardinal criteria is set by running the rstr so we have to retrieve it here
                    # The cardinal criteria applies to all of the distributive answers as a group, so it
                    # does not get reset with each of the distributive answers
                    cardinal = cardinal_from_binding(rstr_solution, h_body, rstr_solution.get_binding(variable_name))

                    # Distributive mode requires that we run each element in the set
                    # through the system individually
                    for dist_item in rstr_binding.value:
                        # Get the solution to this distributive item in the body
                        for body_solution in call(rstr_solution.set_x(variable_name, [dist_item], is_collective=False), h_body):
                            # See if the cardinal has been successful yet
                            for dist_answer in cardinal.yield_if_criteria_met(body_solution.get_binding(variable_name).value, [body_solution]):
                                # It has, so now let the quantifier decide if the answers are quantified
                                yield from behavior_function(dist_answer, [dist_item], cardinal, h_body)

            # Allow cardinals like "a" to stop execution when they are done
            except StopQuantifierException:
                break

        # After coll or dist mode is finished, a cardinal like "only 2 files are x",
        # may have held answers to make sure there are "only 2", so now we give it a chance to finish
        if cardinal is not None:
            for answer in cardinal.yield_finish():
                yield from behavior_function(answer, None, cardinal, h_body)

    if not rstr_found:
        report_error(["doesntExist", ["AtPredicationIndex", h_body, variable_name]], force=True)


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
