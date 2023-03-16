from file_system_example.objects import File
from perplexity.execution import report_error, call
from perplexity.tree import is_index_predication
from perplexity.utilities import is_plural
from perplexity.vocabulary import Vocabulary, Predication, EventOption

vocabulary = Vocabulary()


def yield_coll_or_dist(state, binding, value_set):
    if len(value_set) == 0:
        return

    if binding.variable.is_collective:
        yield state.set_x(binding.variable.name, value_set)

    else:
        for value in value_set:
            yield state.set_x(binding.variable.name, value)


def yield_all(set):
    if isinstance(set, list):
        for item in set:
            yield from yield_all(item)
    else:
        yield set


@Predication(vocabulary, names=["udef_q", "which_q", "_which_q"])
def default_quantifier(state, x_variable_binding, h_rstr_orig, h_body_orig, reverse=False):
    h_rstr = h_body_orig if reverse else h_rstr_orig
    h_body = h_rstr_orig if reverse else h_body_orig

    # If x is plural, start with the collective reading,
    # Otherwise just do dist
    modes = [True, False] if is_plural(state, x_variable_binding.variable.name) else [False]

    # Return a different error if there is no rstr that works
    # in any mode
    rstr_found = False
    for mode in modes:
        state = state.set_x(x_variable_binding.variable.name, x_variable_binding.value,
                            is_collective=mode)

        for solution in call(state, h_rstr):
            rstr_found = True
            for body_solution in call(solution, h_body):
                yield body_solution

    if not rstr_found:
        # Ignore whatever error the RSTR produced, this is a better one
        if not reverse:
            report_error(["doesntExist", ["AtPredication", h_body, x_variable_binding.variable.name]], force=True)


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
        iterator = x_binding.value if isinstance(x_binding.value, list) else [x_binding.value]

    values = []
    for value in iterator:
        if isinstance(value, File):
            values.append(value)

    yield from yield_coll_or_dist(state, x_binding, values)


# large_a_1 should only work distributively since it doesn't support adding everything up
# to see if the set is large
@Predication(vocabulary, names=["_large_a_1"], handles=[("DegreeMultiplier", EventOption.optional)])
def large_a_1(state, e_introduced_binding, x_target_binding):
    if x_target_binding.variable.is_collective:
        report_error(["notDist", x_target_binding.variable.name])
        return

    if x_target_binding.value is None:
        iterator = state.all_individuals()
    else:
        iterator = x_target_binding.value if isinstance(x_target_binding.value, list) else [x_target_binding.value]

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

    yield from yield_coll_or_dist(state, x_target_binding, values)


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


# # x_actor_binding, x_location_binding will always be set to *something* but it could
# # be something broad like thing(x) or place(x)
# def in_p_loc(state, e_introduced_binding, x_actor_binding, x_location_binding):
#     # restrict to just actors in location
#     final_actors = []
#     final_locations = []
#     for actor in x_actor_binding.values:
#         for location in x_location_binding.values:
#             if actor in location:
#                 final_actors.append(actor)
#                 final_locations.append(location)
#
#     if len(final_actors) > 0:
#         yield state.set_x(x_actor_binding.variable.name, final_actors).set_x(x_location_binding.variable.name, final_locations)
#     else:
#         report_error(["thingHasNoLocation", x_actor_binding.variable.name, x_location_binding.variable.name])