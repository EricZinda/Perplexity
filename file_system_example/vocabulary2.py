import itertools
from file_system_example.objects import File
from perplexity.cardinals import cardinal_from_binding, StopQuantifierException, yield_all
from perplexity.execution import report_error, call
from perplexity.tree import is_index_predication
from perplexity.utilities import is_plural
from perplexity.vocabulary import Vocabulary, Predication, EventOption


vocabulary = Vocabulary()


@Predication(vocabulary, names=["_a_q"])
def a_q(state, x_variable_binding, h_rstr, h_body):
    def a_behavior(state, rstr_value, cardinal, h_body):
        body_solutions = []
        for body_solution in call(state, h_body):
            body_solutions.append(body_solution)

        if len(body_solutions) > 0:
            yield from cardinal.yield_if_criteria_met(rstr_value, body_solutions)
            if cardinal.criteria_met():
                # We have returned "a" (arbitrary) item, stop
                raise StopQuantifierException

    yield from quantifier_implementation(state, x_variable_binding, h_rstr, h_body, a_behavior)


@Predication(vocabulary, names=["udef_q", "which_q", "_which_q"])
def default_quantifier(state, x_variable_binding, h_rstr_orig, h_body_orig, reverse=False):
    h_rstr = h_body_orig if reverse else h_rstr_orig
    h_body = h_rstr_orig if reverse else h_body_orig

    def default_quantifier_behavior(state, rstr_value, cardinal, h_body):
        body_solutions = []
        for body_solution in call(state, h_body):
            body_solutions.append(body_solution)

        if len(body_solutions) > 0:
            yield from cardinal.yield_if_criteria_met(rstr_value, body_solutions)

    yield from quantifier_implementation(state, x_variable_binding, h_rstr, h_body, default_quantifier_behavior)


def quantifier_implementation(state, x_variable_binding, h_rstr, h_body, behavior_function):
    modes = [True, False] if is_plural(state, x_variable_binding.variable.name) else [False]

    # Gate function is the same for every value of the rstr
    cardinal = None

    # Need to do coll and dist versions
    for is_collective in modes:
        # Run the rstr
        for solution in call(state, h_rstr):
            # If the rstr forced x to an incompatible mode, fail this mode
            rstr_binding = solution.get_binding(x_variable_binding.variable.name)
            if rstr_binding.variable.is_collective is not None and rstr_binding.variable.is_collective != is_collective:
                report_error(["wrongMode"])
                break

            # The gate function must be retrieved after the rstr is run
            if cardinal is None:
                cardinal = cardinal_from_binding(solution, solution.get_binding(x_variable_binding.variable.name))

            try:
                if is_collective:
                    yield from behavior_function(solution, rstr_binding.value, cardinal, h_body)

                else:
                    # Distributive mode requires that we run each element in the set
                    # through the system individually
                    for dist_item in rstr_binding.value:
                        dist_state = solution.set_x(x_variable_binding.variable.name, [dist_item])
                        yield from behavior_function(dist_state, [dist_item], cardinal, h_body)

            except StopQuantifierException:
                break

        if cardinal is not None:
            yield from cardinal.yield_finish()


@Predication(vocabulary)
def card(state, c_count, e_introduced_binding, x_target_binding):
    yield state.set_x(x_target_binding.variable.name, x_target_binding.value,
                      cardinal=["vocabulary2.CardCardinal", [int(c_count)]])


# card(2) means "exactly 2"
# This means that it doesn't actually return answers
# until yield_finish() is called because it needs to ensure that
# not more than 2 were successful
class CardCardinal(object):
    def __init__(self, count):
        self.count = count
        self.yielded_rstr_count = 0
        self.running_count = 0
        self.cached_answers = []

    def criteria_met(self):
        return self.running_count == self.count

    def yield_if_criteria_met(self, rstr_value, answers):
        # Force to be a generator
        if False:
            yield None

        if len(answers) > 0:
            self.cached_answers += answers
            if isinstance(rstr_value, list):
                self.running_count += len(rstr_value)
            else:
                self.running_count += 1

            if self.running_count > self.count:
                raise StopQuantifierException

    def yield_finish(self):
        if self.criteria_met():
            yield from yield_all(self.cached_answers)

        else:
            if self.running_count > self.count:
                report_error(["too many"], force=True)

            else:
                # If we got over 1, we already yielded them
                # So there is nothing to finish
                report_error(["notEnough"], force=True)


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