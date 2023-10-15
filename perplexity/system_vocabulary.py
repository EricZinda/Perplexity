import copy
import logging
import numbers

import perplexity.predications
from perplexity.execution import execution_context, call, set_variable_execution_data, report_error
from perplexity.plurals import VariableCriteria, GlobalCriteria, NegatedPredication
from perplexity.predications import combinatorial_predication_1, all_combinations_of_states, lift_style_predication_2, \
    in_style_predication_2, is_referring_expr
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
    rstr_values_tree_lineage = ""
    for rstr_solution in call(state, h_rstr):
        # We track RSTR values *per tree lineage* since these are effectively different trees
        # and so we need to clear it if the lineage changes
        tree_lineage_value = rstr_solution.get_binding("tree_lineage").value
        tree_lineage = rstr_solution.get_binding("tree_lineage").value[0] if tree_lineage_value is not None else ""
        if tree_lineage != rstr_values_tree_lineage:
            rstr_values = []
            rstr_values_tree_lineage = tree_lineage

        if criteria_predication is not None:
            alternative_states = criteria_predication(rstr_solution, rstr_solution.get_binding(x_variable_binding.variable.name))
        else:
            alternative_states = [rstr_solution]

        for alternative_state in alternative_states:
            rstr_values.extend(alternative_state.get_binding(variable_name).value)
            set_variable_execution_data(variable_name, "AllRstrValues", rstr_values)
            for body_solution in call(alternative_state, h_body):
                yield body_solution

    if not reverse and len(rstr_values) == 0:
        # If the rstr was actually run (i.e. not reversed) and produced no values:
        # Ignore whatever error the RSTR produced, this is a better one
        report_error(["doesntExist", ["AtPredication", h_body, x_variable_binding.variable.name]], force=True)


@Predication(vocabulary, library="system")
def thing(state, x_binding):
    def bound_variable(_):
        return True

    def unbound_variable():
        for item in state.all_individuals():
            yield item

    yield from combinatorial_predication_1(state, x_binding, bound_variable, unbound_variable)


@Predication(vocabulary, library="system", names=["_a_q"])
def a_q(state, x_variable_binding, h_rstr, h_body):
    state = state.set_variable_data(x_variable_binding.variable.name,
                                    quantifier=VariableCriteria(execution_context().current_predication(),
                                                                x_variable_binding.variable.name,
                                                                min_size=1,
                                                                max_size=1))

    yield from quantifier_raw(state, x_variable_binding, h_rstr, h_body)


def in_scope(state, x_binding):
    def bound_variable(value):
        if execution_context().in_scope(state, value):
            return True

        else:
            report_error(["variableIsNotInScope", x_binding.variable.name])
            return False

    def unbound_variable():
        for item in state.all_individuals():
            if execution_context().in_scope(state, item):
                yield item

    yield from combinatorial_predication_1(state, x_binding, bound_variable, unbound_variable)


# We want the interpretations of the to be mutually exclusive to avoid duplication
# since if there is only one "the" in the world, it can be duplicated if it is also in scope
@Predication(vocabulary, library="system", names=["_the_q"])
def the_selector_q(state, x_variable_binding, h_rstr, h_body):
    solution_found = False
    for solution in the_all_q(state, x_variable_binding, h_rstr, h_body):
        solution_found = True
        yield solution

    if not solution_found:
        yield from the_in_scope_q(state, x_variable_binding, h_rstr, h_body)


# The interpretation of "the x" which means "all of the x" is the same as "all x"
# The key part here is GlobalCriteria.all_rstr_meet_criteria which ensures that every value of the RSTR is true
# for the body
@Predication(vocabulary, library="system", names=["_all_q"])
def the_all_q(state, x_variable_binding, h_rstr, h_body):
    # Set the constraint to be 1, inf but this is just temporary. When the constraints are optimized,
    # whatever the determiner constraint gets set to will replace these
    state = state.set_variable_data(x_variable_binding.variable.name,
                                    quantifier=VariableCriteria(execution_context().current_predication(),
                                                                x_variable_binding.variable.name,
                                                                min_size=1,
                                                                max_size=float('inf'),
                                                                global_criteria=GlobalCriteria.all_rstr_meet_criteria))

    yield from quantifier_raw(state, x_variable_binding, h_rstr, h_body)


# Interpretation of "the" which means "the one in scope"
@Predication(vocabulary, library="system", names=["_this_q_dem"])
def the_in_scope_q(state, x_variable_binding, h_rstr, h_body):
    # Set the constraint to be 1, inf but this is just temporary. When the constraints are optimized,
    # whatever the determiner constraint gets set to will replace these
    state = state.set_variable_data(x_variable_binding.variable.name,
                                    quantifier=VariableCriteria(execution_context().current_predication(),
                                                                x_variable_binding.variable.name,
                                                                min_size=1,
                                                                max_size=float('inf'),
                                                                global_criteria=GlobalCriteria.all_rstr_meet_criteria))

    yield from quantifier_raw(state, x_variable_binding, h_rstr, h_body, criteria_predication=in_scope)


@Predication(vocabulary, library="system", names=["_every_q", "_each_q", "_each+and+every_q"])
def every_each_q(state, x_variable_binding, h_rstr, h_body):
    # Set the constraint to be 1, inf but this is just temporary. When the constraints are optimized,
    # whatever the determiner constraint gets set to will replace these
    state = state.set_variable_data(x_variable_binding.variable.name,
                                    quantifier=VariableCriteria(execution_context().current_predication(),
                                                                x_variable_binding.variable.name,
                                                                min_size=1,
                                                                max_size=float('inf'),
                                                                global_criteria=GlobalCriteria.every_rstr_meet_criteria))

    yield from quantifier_raw(state, x_variable_binding, h_rstr, h_body)


@Predication(vocabulary, library="system", names=["which_q", "_which_q"])
def which_q(state, x_variable_binding, h_rstr, h_body):
    current_predication = execution_context().current_predication()

    state = state.set_variable_data(x_variable_binding.variable.name,
                                    quantifier=VariableCriteria(current_predication,
                                                                x_variable_binding.variable.name,
                                                                min_size=1,
                                                                max_size=float('inf')))

    yield from quantifier_raw(state, x_variable_binding, h_rstr, h_body)


@Predication(vocabulary, library="system", names=["udef_q", "pronoun_q", "proper_q", "number_q"])
def generic_q(state, x_variable_binding, h_rstr, h_body):
    state = state.set_variable_data(x_variable_binding.variable.name,
                                    quantifier=VariableCriteria(execution_context().current_predication(),
                                                                x_variable_binding.variable.name,
                                                                min_size=1,
                                                                max_size=float('inf')))

    yield from quantifier_raw(state, x_variable_binding, h_rstr, h_body)


@Predication(vocabulary, library="system", names=["_a+few_a_1"])
def a_few_a_1(state, e_introduced_binding, x_target_binding):
    yield state.set_variable_data(x_target_binding.variable.name,
                                  determiner=VariableCriteria(execution_context().current_predication(),
                                                              x_target_binding.variable.name,
                                                              min_size=3,
                                                              max_size=5))


# "and" could have incoming combinatoric variables, but it also needs to combine
# its x_binding_first, x_binding_second arguments into a single thing.
# So it needs to call something to "uncombinatoric" the values
# It calls in_style because the bound_check is always true
# It sets its introduced variable to combinatoric because we want to allow
# "My son and I want a steak" to have a solution group for:
# Group:
#   my son wants a steak
#   I want a steak
# Group:
#   my son and I want a steak
@Predication(vocabulary, library="system", names=["_and_c"])
def and_c(state, x_binding_introduced, x_binding_first, x_binding_second):
    def both_bound_prediction_function(x_what, x_for):
        return True

    def binding1_unbound_predication_function():
        assert False
        if False:
            yield None

    def binding2_unbound_predication_function():
        assert False
        if False:
            yield None

    # Use in_style_predication_2 simply to break out the combinatorial alternatives
    for solution in in_style_predication_2(state, x_binding_first, x_binding_second,
                             both_bound_prediction_function, binding1_unbound_predication_function,
                             binding2_unbound_predication_function):
        solution_first = solution.get_binding(x_binding_first.variable.name)
        solution_second = solution.get_binding(x_binding_second.variable.name)
        and_value = solution_first.value + solution_second.value

        if x_binding_first.variable.determiner is not None and x_binding_first.variable.determiner.required_values is not None:
            required_values = x_binding_first.variable.determiner.required_values + solution_second.value
        else:
            required_values = and_value

        if len(set([perplexity.predications.value_type(x) for x in and_value])) > 1:
            # If anything is a concept, everything must be
            continue

        yield solution.set_x(x_binding_introduced.variable.name,
                             and_value,
                             combinatoric=True,
                             determiner=VariableCriteria(execution_context().current_predication(),
                                                         x_binding_introduced.variable.name,
                                                         required_values=required_values)
                          )


@Predication(vocabulary, library="system", names=["implicit_conj"])
def implicit_conj(state, x_binding_introduced, x_binding_first, x_binding_second):
    yield from and_c(state, x_binding_introduced, x_binding_first, x_binding_second)


@Predication(vocabulary, library="system", names=["card"])
def card_cex(state, c_count, e_introduced_binding, x_target_binding):
    if c_count.isnumeric():
        yield state.set_variable_data(x_target_binding.variable.name,
                                      determiner=VariableCriteria(execution_context().current_predication(),
                                                                  x_target_binding.variable.name,
                                                                  min_size=int(c_count),
                                                                  max_size=int(c_count)))


# This version of card() is used to mean "the number x, on its own" and not "x of something"
@Predication(vocabulary, library="system", names=["card"])
def card_cxi(state, c_count, x_binding, i_binding):
    def bound_variable(value):
        if value == c_value:
            return True
        else:
            report_error(["notAThing", x_binding.value, x_binding.variable.name])
            return False

    def unbound_variable():
            yield c_value

    if isinstance(c_count, numbers.Number) or (isinstance(c_count, str) and c_count.isnumeric()):
        c_value = int(c_count)
        yield from combinatorial_predication_1(state,
                                               x_binding,
                                               bound_variable,
                                               unbound_variable)


def generate_not_error(unscoped_referenced_variables):
    if len(unscoped_referenced_variables) == 0:
        quantifier_variable = execution_context().current_predication().args[1].args[0]
        report_error(["notAllError", quantifier_variable, ["AfterFullPhrase", quantifier_variable]], force=True)

    elif len(unscoped_referenced_variables) == 1:
        report_error(["notError", ["AfterFullPhrase", unscoped_referenced_variables[0]]], force=True)

    else:
        report_error(["notClause"], force=True)


@Predication(vocabulary, library="system", names=["neg"])
def neg(state, e_introduced_binding, h_scopal):
    # Gather all the bound x variables and their values that are referenced in h_scopal
    referenced_x_variables = gather_referenced_x_variables_from_tree(h_scopal)
    combinatorial_referenced_x_values = {}
    for variable_name in referenced_x_variables:
        binding = state.get_binding(variable_name)
        if binding.value is not None and binding.variable.combinatoric:
            combinatorial_referenced_x_values[variable_name] = binding.value

    # Record all the variables this neg() has scope over so we can add it as an event later
    scoped_variables, unscoped_variables = gather_scoped_variables_from_tree_at_index(state.get_binding("tree").value[0]["Tree"], execution_context().current_predication_index())

    # Referenced variables that are not scoped in h_scopal
    unscoped_referenced_variables = []
    for referenced_x_variable in referenced_x_variables:
        if referenced_x_variable in unscoped_variables:
            unscoped_referenced_variables.append(referenced_x_variable)

    negated_predication_info = NegatedPredication(execution_context().current_predication(), scoped_variables)

    # If a state makes h_scopal True, this predication fails since it is neg(). That part is straightforward.
    # However, we need to return the neg() success states too. neg() succeeds when h_scopal fails, but the problem is that
    # combinatorial variables can be in the incoming state, and thus an h_scopal like large(x) might fail for some subset of the combinatorial values
    # in x, and we won't know since we only see the successes coming out of large(x) (i.e. when it yields). We need a way to determine
    # if a particular value fails
    #
    # Furthermore, combinatorial variables might expand under neg(), like
    #   "which files are not in two folders": which_q(x3,_file_n_of(x3,i8),neg(e9,udef_q(x12,[_folder_n_of(x12,i19), card(2,e18,x12)],_in_p_loc(e2,x3,x12))))
    #   if x3 is combinatorial, it will expand under neg() effectively creating:
    #   which_q(x3,,neg(e9,[_file_n_of(x3,i8), udef_q(x12,[_folder_n_of(x12,i19), card(2,e18,x12)],_in_p_loc(e2,x3,x12)))])
    #   which is a different answer
    #
    # So, if there are combinatorial variables, we need to make them discrete before neg. The final subtlety is that *all combinations* of the
    # combinatorial variables must be tried, so we need to return the combinatorics. So, we need a function that returns the cartesian product
    # of all combinatorial variables
    h_scopal_has_quantifiers = len(scoped_variables) > 0
    if h_scopal_has_quantifiers:
        def state_generator():
            # Use state instead of negated_predications_state so the solution group processor doesn't think
            # this is negative: we want it evaluated positively
            for combination_state in all_combinations_of_states(state, combinatorial_referenced_x_values):
                # Use resolve_fragment to run numeric criteria on the "not" clause. So that a phrase like
                # "which files not in this folder are not large?" would work
                had_negative_success = False
                for temp in execution_context().resolve_fragment_new(combination_state, h_scopal):
                    # This is true, don't yield it since neg() makes it False
                    generate_not_error(unscoped_referenced_variables)
                    had_negative_success = True
                    break

                if execution_context().has_not_understood_error():
                    # this was not a logical failure, we simply didn't understand
                    return

                if not had_negative_success:
                    # There were no solutions for this combination_state, so it is false, and thus true
                    # Record that this was a negative success for debugging purposes
                    combination_state = combination_state.add_to_e("negated_predications",
                                                                   execution_context().current_predication_index(),
                                                                   negated_predication_info)
                    yield combination_state.add_to_e("negated_successes", execution_context().current_predication_index(), True)

    else:
        def state_generator():
            # Use negated_predications_state so the solution group processor knows
            # this should be negated later when it runs
            negated_predications_state = state.add_to_e("negated_predications",
                                                        execution_context().current_predication_index(),
                                                        negated_predication_info)
            for combination_state in all_combinations_of_states(negated_predications_state, combinatorial_referenced_x_values):
                # No scoped variables, just run it directly
                had_negative_success = False
                for _ in call(combination_state, h_scopal):
                    # This is true, don't yield it since neg() makes it False
                    generate_not_error(unscoped_referenced_variables)
                    had_negative_success = True

                if execution_context().has_not_understood_error():
                    # this was not a logical failure, we simply didn't understand
                    return

                if not had_negative_success:
                    # There were no solutions for this combination_state, so it is false, and thus true
                    # Record that this was a negative success for debugging purposes
                    yield combination_state.add_to_e("negated_successes", execution_context().current_predication_index(), True)

    yield from state_generator()


pipeline_logger = logging.getLogger('Pipeline')

