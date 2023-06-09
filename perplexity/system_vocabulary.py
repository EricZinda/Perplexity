import copy
from perplexity.execution import execution_context, call, set_variable_execution_data, report_error, \
    get_variable_metadata
from perplexity.plurals import VariableCriteria, GlobalCriteria, NegatedPredication
from perplexity.predications import combinatorial_predication_1, discrete_variable_generator
from perplexity.set_utilities import all_combinations_with_elements_from_all
from perplexity.tree import TreePredication, gather_scoped_variables_from_tree_at_index, \
    gather_referenced_x_variables_from_tree
from perplexity.vocabulary import Predication, Vocabulary

vocabulary = Vocabulary()


# Merge the system vocabulary into new_vocabulary
def system_vocabulary():
    return copy.deepcopy(vocabulary)


def rstr_reorderable(rstr):
    return isinstance(rstr, TreePredication) and rstr.name in ["place_n", "thing"]


# Yield all undetermined, unquantified answers
def quantifier_raw(state, x_variable_binding, h_rstr_orig, h_body_orig, criteria_predication=None):
    reverse = rstr_reorderable(h_rstr_orig)
    h_rstr = h_body_orig if reverse else h_rstr_orig
    h_body = h_rstr_orig if reverse else h_body_orig

    variable_name = x_variable_binding.variable.name
    rstr_values = []
    for rstr_solution in call(state, h_rstr):
        if criteria_predication is not None:
            alternative_states = criteria_predication(rstr_solution, rstr_solution.get_binding(x_variable_binding.variable.name))
        else:
            alternative_states = [rstr_solution]

        for alternative_state in alternative_states:
            rstr_values.extend(alternative_state.get_binding(variable_name).value)
            for body_solution in call(alternative_state, h_body):
                yield body_solution

    set_variable_execution_data(variable_name, "AllRstrValues", rstr_values)

    if not reverse and len(rstr_values) == 0:
        # If the rstr was actually run (i.e. not reversed) and produced no values:
        # Ignore whatever error the RSTR produced, this is a better one
        report_error(["doesntExist", ["AtPredication", h_body, x_variable_binding.variable.name]], force=True)


@Predication(vocabulary)
def thing(state, x_binding):
    def bound_variable(_):
        return True

    def unbound_variable():
        for item in state.all_individuals():
            yield item

    yield from combinatorial_predication_1(state, x_binding, bound_variable, unbound_variable)


@Predication(vocabulary, names=["_a_q"])
def a_q(state, x_variable_binding, h_rstr, h_body):
    state = state.set_variable_data(x_variable_binding.variable.name,
                                    quantifier=VariableCriteria(execution_context().current_predication(),
                                                                x_variable_binding.variable.name,
                                                                min_size=1,
                                                                max_size=1))

    yield from quantifier_raw(state, x_variable_binding, h_rstr, h_body)


# Several meanings:
# 1. Means "this" which only succeeds for rstrs that are the single in scope x set and there are no others that are in scope
#       "put the two keys in the lock": should only work if there are only two keys in scope:
#       run the rstr, run the cardinal (potentially fail), the run the body (potentially fail)
# 2. Means "the one and only" which only succeeds if the rstr is a single set and there are no other sets
#       same approach
@Predication(vocabulary, names=["_the_q"])
def the_q(state, x_variable_binding, h_rstr, h_body):
    # Set the constraint to be 1, inf but this is just temporary. When the constraints are optimized,
    # whatever the determiner constraint gets set to will replace these
    state = state.set_variable_data(x_variable_binding.variable.name,
                                    quantifier=VariableCriteria(execution_context().current_predication(),
                                                                x_variable_binding.variable.name,
                                                                min_size=1,
                                                                max_size=float('inf'),
                                                                global_criteria=GlobalCriteria.all_rstr_meet_criteria))

    yield from quantifier_raw(state, x_variable_binding, h_rstr, h_body)


@Predication(vocabulary, names=["which_q", "_which_q"])
def which_q(state, x_variable_binding, h_rstr, h_body):
    current_predication = execution_context().current_predication()

    state = state.set_variable_data(x_variable_binding.variable.name,
                                    quantifier=VariableCriteria(current_predication,
                                                                x_variable_binding.variable.name,
                                                                min_size=1,
                                                                max_size=float('inf')))

    yield from quantifier_raw(state, x_variable_binding, h_rstr, h_body)


@Predication(vocabulary, names=["udef_q", "pronoun_q", "proper_q"])
def generic_q(state, x_variable_binding, h_rstr, h_body):
    state = state.set_variable_data(x_variable_binding.variable.name,
                                    quantifier=VariableCriteria(execution_context().current_predication(),
                                                                x_variable_binding.variable.name,
                                                                min_size=1,
                                                                max_size=float('inf')))

    yield from quantifier_raw(state, x_variable_binding, h_rstr, h_body)


@Predication(vocabulary, names=["_a+few_a_1"])
def a_few_a_1(state, e_introduced_binding, x_target_binding):
    yield state.set_variable_data(x_target_binding.variable.name,
                                  determiner=VariableCriteria(execution_context().current_predication(),
                                                              x_target_binding.variable.name,
                                                              min_size=3,
                                                              max_size=5))


@Predication(vocabulary, names=["_and_c"])
def and_c(state, x_binding_introduced, x_binding_first, x_binding_second):
    size_total = len(x_binding_first.value) + len(x_binding_second.value)
    yield state.set_x(x_binding_introduced.variable.name,
                      x_binding_first.value + x_binding_second.value,
                      combinatoric=True,
                      determiner=VariableCriteria(execution_context().current_predication(),
                                                  x_binding_introduced.variable.name,
                                                  min_size=size_total,
                                                  max_size=size_total)
                      )


@Predication(vocabulary, names=["implicit_conj"])
def implicit_conj(state, x_binding_introduced, x_binding_first, x_binding_second):
    yield from and_c(state, x_binding_introduced, x_binding_first, x_binding_second)


def all_combinations_of_states(original_state, unused_x_variables):
    unused_x_variables_values = list(unused_x_variables.values())
    unused_x_variables_names = list(unused_x_variables.keys())
    for combination in all_combinations_with_elements_from_all(unused_x_variables_values):
        combination_list = list(combination)
        new_state = original_state
        for variable_index in range(len(unused_x_variables_names)):
            new_state = new_state.set_x(unused_x_variables_names[variable_index], combination_list[variable_index])

        yield new_state


def record_success_variables(referenced_x_variables, success_state):
    for item in referenced_x_variables.items():
        # TODO: break apart combinatorial variables
        referenced_x_variables[item[0]].append(success_state.get_binding(item[0]).value)


# Find any values in any variables in h_scopal of original state that were not
# true for h_scopal. That means they will all be neg(False) == True
# for neg()
def find_unused_x_variables(original_state, used_h_scopal_x_variables):
    unused_x_variables = dict([[x, []] for x in used_h_scopal_x_variables])
    variable_size = {}
    for variable_name in unused_x_variables:
        binding_metadata = get_variable_metadata(variable_name)
        variable_size[variable_name] = binding_metadata["ValueSize"]

    for item in used_h_scopal_x_variables.items():
        original_x_binding = original_state.get_binding(item[0])
        original_x = original_x_binding.value
        if original_x is not None:
            for combinatoric_item in discrete_variable_generator(original_x, original_x_binding.variable.combinatoric, variable_size[item[0]]):
                if combinatoric_item not in used_h_scopal_x_variables[item[0]]:
                    unused_x_variables[item[0]].append(combinatoric_item)

    non_empty_unused_x_variables = {}
    for item in unused_x_variables.items():
        if len(item[1]) > 0:
            non_empty_unused_x_variables[item[0]] = item[1]
    return non_empty_unused_x_variables


@Predication(vocabulary, names=["neg"])
def neg(state, e_introduced_binding, h_scopal):
    # Gather all the x variables that are referenced in h_scopal
    success_h_scopal_x_variables = dict([[x, []] for x in gather_referenced_x_variables_from_tree(h_scopal)])

    # Record all the variables this neg() has scope over
    scoped_variables, unscoped_variables = gather_scoped_variables_from_tree_at_index(state.get_binding("tree").value[0]["Tree"], execution_context().current_predication_index())

    # TODO: For now, refuse to run anything that has a quantifier under it so that we don't have to
    # run numeric criteria on the "not" clause. So that a phrase like
    # "which files not in this folder are not large?" would work
    if len(scoped_variables) > 0:
        report_error(["notClause"], force=True)
        return

    new_state = state.add_to_e("negated_predications", execution_context().current_predication_index(), NegatedPredication(execution_context().current_predication(), scoped_variables, len(unscoped_variables) == 0))


    # If a state makes h_scopal True, this predication fails since it is neg(). That part is straightforward.
    # However, we need to return the neg() success states too. neg() succeeds when h_scopal fails, but the problem is that
    # combinatorial variables can be in the incoming state, and thus an h_scopal like large(x) might fail for some subset of the combinatorial values
    # in x, and we won't know since we only see the successes coming out of large(x) (i.e. when it yields)
    #
    # So, if there are combinatorial variables, we need a way to represent successes for the ones that don't work (i.e. not(false)).
    # We can do this for any variable by comparing its incoming set of values, with values that were true for h_scopal. Any that weren't in
    # a state that was yielded for a true value of h_scopal must have been False for h_scopal, and should be yielded as True due to neg()
    #
    # The final subtlety is that *all combinations* of the combinatorial variables that weren't used must also be False in h_scopal, so we need
    # to return the combinatorics

    # First handle the successes (that will be failures due to neg())
    # If h_scopal is True that means that this particular solution is False due to neg()
    # However, if there are quantifiers in h_scopal (as in "... not in 2 folders") the solution group might not be False (e.g. if there aren't two failreas for a file in 2 folders)
    # So, we need Phase 2 to count them:
    # - neg() marks the variables it scopes over in a special event variable
    #   - It records that the solution is a phase 1 negative success by putting something in state that says its index and that it was a negative success
    #     - something like {"Index": 2, "NegVariables": ['x2', 'x4']}
    #   - Phase 2 iterates through all the criteria and if it gets to one where the variable is in a negative group
    #     - it checks to see if this is a negative success for the index that represents that group
    #     - if so, it succeeds and skips the rest
    for success_state in call(new_state, h_scopal):
        # Record all successful values of all variables referenced in h_scopal
        record_success_variables(success_h_scopal_x_variables, success_state)

        if len(scoped_variables) > 0:
            # Since this state succeeded, it *might* be ultimately true in h_scopal (and thus false due to neg()), but quantifiers
            # in h_scopal (like "... in 2 folders") could make it fail in h_scopal, we won't know until phase 2
            # The "negated_predications" event added above will make sure phase 2 treats it as negation
            # We just yield it as a success
            yield success_state

        else:
            # If there are no quantifiers, then we know it is false already
            # since there is no phase 2 processing required.
            # So: don't yield it since neg() makes it False
            report_error(["notClause"], force=True)

    # Now handle the failures
    # Find the original referenced_x_variables that weren't successes
    unused_x_variables = find_unused_x_variables(state, success_h_scopal_x_variables)

    # return all combinations
    if len(unused_x_variables) > 0:
        for negative_success_state in all_combinations_of_states(new_state, unused_x_variables):
            # There were no solutions for this state, so it is false, and thus true
            # Record that this was a negative success
            # None of the determiner criteria for the subtree will have been added
            yield negative_success_state.add_to_e("negated_successes", execution_context().current_predication_index(), True)

