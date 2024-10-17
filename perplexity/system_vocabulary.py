import copy
import logging
import numbers
import perplexity.predications
from perplexity.execution import TreeSolver
from perplexity.plurals import VariableCriteria, GlobalCriteria, NegatedPredication
from perplexity.predications import combinatorial_predication_1
from perplexity.tree import TreePredication, gather_scoped_variables_from_tree_at_index, \
    gather_referenced_x_variables_from_tree
from perplexity.vocabulary import Predication, Vocabulary


vocabulary = Vocabulary()


# Merge the system vocabulary into new_vocabulary
def system_vocabulary():
    return copy.deepcopy(vocabulary)


# Returns the RSTR that should be used and whether or not it should be reversed
def rstr_reorderable(context, rstr):
    if isinstance(rstr, list):
        new_rstr = []
        after_rstr =[]
        for predicate in rstr:
            if predicate_reorderable(context, predicate):
                after_rstr.append(predicate)
            else:
                new_rstr.append(predicate)

        # Don't reverse the RSTR and BODY, just the order of predications in the
        # conjunction
        return new_rstr + after_rstr, False

    else:
        return rstr, predicate_reorderable(context, rstr)


def predicate_reorderable(context, predicate):
    return isinstance(predicate, TreePredication) and predicate.name in ["place_n", "thing", "_thing_n_of-about", "person"] and \
            not context.get_variable_metadata(predicate.args[0]).get("ReferencedUnderNegation", False)


# Yield all undetermined, unquantified answers
def quantifier_raw(context, state, x_variable_binding, h_rstr_orig, h_body_orig, criteria_predication=None):
    h_rstr_orig, reversed = rstr_reorderable(context, h_rstr_orig)
    h_rstr = h_body_orig if reversed else h_rstr_orig
    h_body = h_rstr_orig if reversed else h_body_orig

    variable_name = x_variable_binding.variable.name
    rstr_values = set()
    rstr_values_tree_lineage = ""
    rstr_ran = False if reversed else True
    for rstr_solution in context.call(state, h_rstr):
        # We track RSTR values *per tree lineage* since these are effectively different trees
        # and so we need to clear it if the lineage changes
        tree_lineage_value = rstr_solution.get_binding("tree_lineage").value
        tree_lineage = rstr_solution.get_binding("tree_lineage").value[0] if tree_lineage_value is not None else ""
        if tree_lineage != rstr_values_tree_lineage:
            rstr_values = set()
            rstr_values_tree_lineage = tree_lineage

        if criteria_predication is not None:
            alternative_states = criteria_predication(rstr_solution, rstr_solution.get_binding(x_variable_binding.variable.name))
        else:
            alternative_states = [rstr_solution]

        for alternative_state in alternative_states:
            if not reversed:
                rstr_ran = True
                rstr_values.update(alternative_state.get_binding(variable_name).value)
                context.set_variable_execution_data(variable_name, "AllRstrValues", list(rstr_values))
            else:
                rstr_ran = True

            for body_solution in context.call(alternative_state, h_body):
                if reversed:
                    rstr_values.update(body_solution.get_binding(variable_name).value)
                    context.set_variable_execution_data(variable_name, "AllRstrValues", list(rstr_values))
                yield body_solution

    # If the RSTR actually ran (reversed or not) and returned no values, give a special error
    # saying that whatever the RSTR was doesn't exist.  Make sure we tell the error to use the value
    # of the variable *after* the real RSTR so it uses that word in the description and says
    # "There isn't a <RSTR> in the system"
    if not context.has_not_understood_error() and rstr_ran and len(rstr_values) == 0:
        context.report_error(["doesntExist", ["AtPredication", h_rstr if reversed else h_body, x_variable_binding.variable.name]], force=True)


@Predication(vocabulary, library="system", names=["_a_q"])
def a_q(context, state, x_variable_binding, h_rstr, h_body):
    state = state.set_variable_data(x_variable_binding.variable.name,
                                    quantifier=VariableCriteria(context.current_predication(),
                                                                x_variable_binding.variable.name,
                                                                min_size=1,
                                                                max_size=1))

    yield from quantifier_raw(context, state, x_variable_binding, h_rstr, h_body)


def in_scope(context, state, x_binding):
    def bound_variable(value):
        if context.in_scope(state, value):
            return True

        else:
            context.report_error(["variableIsNotInScope", x_binding.variable.name])
            return False

    def unbound_variable():
        for item in state.all_individuals():
            if context.in_scope(state, item):
                yield item

    yield from combinatorial_predication_1(context, state, x_binding, bound_variable, unbound_variable)


# The interpretation of "the x" which means "all of the x" is the same as "all x"
# The key part here is GlobalCriteria.all_rstr_meet_criteria which ensures that every value of the RSTR is true
# for the body
@Predication(vocabulary, library="system", names=["_the_q", "_all_q"])
def the_all_q(context, state, x_variable_binding, h_rstr, h_body):
    # Set the constraint to be 1, inf but this is just temporary. When the constraints are optimized,
    # whatever the determiner constraint gets set to will replace these
    state = state.set_variable_data(x_variable_binding.variable.name,
                                    quantifier=VariableCriteria(context.current_predication(),
                                                                x_variable_binding.variable.name,
                                                                min_size=1,
                                                                max_size=float('inf'),
                                                                global_criteria=GlobalCriteria.all_rstr_meet_criteria))

    yield from quantifier_raw(context, state, x_variable_binding, h_rstr, h_body)


# Interpretation of "the" which means "the one in scope"
@Predication(vocabulary, library="system", names=["_the_q", "_this_q_dem", "_that_q_dem"])
def the_in_scope_q(context, state, x_variable_binding, h_rstr, h_body):
    # Set the constraint to be 1, inf but this is just temporary. When the constraints are optimized,
    # whatever the determiner constraint gets set to will replace these
    state = state.set_variable_data(x_variable_binding.variable.name,
                                    quantifier=VariableCriteria(context.current_predication(),
                                                                x_variable_binding.variable.name,
                                                                min_size=1,
                                                                max_size=float('inf'),
                                                                global_criteria=GlobalCriteria.all_rstr_meet_criteria))

    def in_scope_capture_context(state, binding):
        yield from in_scope(context, state, binding)

    yield from quantifier_raw(context, state, x_variable_binding, h_rstr, h_body, criteria_predication=in_scope_capture_context)


@Predication(vocabulary, library="system", names=["_every_q", "_each_q", "_each+and+every_q"])
def every_each_q(context, state, x_variable_binding, h_rstr, h_body):
    # Set the constraint to be 1, inf but this is just temporary. When the constraints are optimized,
    # whatever the determiner constraint gets set to will replace these
    state = state.set_variable_data(x_variable_binding.variable.name,
                                    quantifier=VariableCriteria(context.current_predication(),
                                                                x_variable_binding.variable.name,
                                                                min_size=1,
                                                                max_size=float('inf'),
                                                                global_criteria=GlobalCriteria.every_rstr_meet_criteria))

    yield from quantifier_raw(context, state, x_variable_binding, h_rstr, h_body)


@Predication(vocabulary, library="system", names=["which_q", "_which_q"])
def which_q(context, state, x_variable_binding, h_rstr, h_body):
    current_predication = context.current_predication()

    state = state.set_variable_data(x_variable_binding.variable.name,
                                    quantifier=VariableCriteria(current_predication,
                                                                x_variable_binding.variable.name,
                                                                min_size=1,
                                                                max_size=float('inf')))

    yield from quantifier_raw(context, state, x_variable_binding, h_rstr, h_body)


# Examples of "any":
#   are there any vegetarian dishes?
#       this construction works like a, but allows plural
#   I'll take any meat dish
#   I'll take any meat dishes
#       this means "all"
#   Are there any tables available?
# It should be represented the same as "a"
@Predication(vocabulary, library="system", names=["udef_q", "pronoun_q", "proper_q", "number_q", "_any_q"])
def generic_q(context, state, x_variable_binding, h_rstr, h_body):
    state = state.set_variable_data(x_variable_binding.variable.name,
                                    quantifier=VariableCriteria(context.current_predication(),
                                                                x_variable_binding.variable.name,
                                                                min_size=1,
                                                                max_size=float('inf')))

    yield from quantifier_raw(context, state, x_variable_binding, h_rstr, h_body)


@Predication(vocabulary, library="system", names=["_a+few_a_1"])
def a_few_a_1(context, state, e_introduced_binding, x_target_binding):
    yield state.set_variable_data(x_target_binding.variable.name,
                                  determiner=VariableCriteria(context.current_predication(),
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
def and_c(context, state, x_binding_introduced, x_binding_first, x_binding_second):
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

    solution_first = state.get_binding(x_binding_first.variable.name)
    solution_second = state.get_binding(x_binding_second.variable.name)
    assert not solution_first.variable.combinatoric and not solution_second.variable.combinatoric

    and_value = solution_first.value + solution_second.value

    if x_binding_first.variable.determiner is not None and x_binding_first.variable.determiner.required_values is not None:
        required_values = x_binding_first.variable.determiner.required_values + solution_second.value
    else:
        required_values = and_value

    # Everything must be of the same type
    if len(set([perplexity.predications.value_type(x) for x in and_value])) > 1:
        return

    for value in perplexity.predications.used_combinations(context, x_binding_introduced, and_value):
        yield state.set_x(x_binding_introduced.variable.name,
                          value,
                          determiner=VariableCriteria(context.current_predication(),
                                                      x_binding_introduced.variable.name,
                                                      required_values=required_values))


# "and salmon" said just by itself should just be transparent
@Predication(vocabulary, library="system", names=["_and_c"])
def and_c_u_x(context, state, x_binding_introduced, u_binding_first, x_binding_second):
    yield state.set_x(x_binding_introduced.variable.name, x_binding_second.value)


# This is never actually called, but is here so the system knows that
# it understands implicit_conj. Instead of calling this, the system actually removes it
# and calls each conjunct independently
@Predication(vocabulary, library="system", names=["implicit_conj"])
def implicit_conj(context, state, e_binding, e_binding_1, e_binding_2):
    if False:
        yield None


@Predication(vocabulary, library="system", names=["implicit_conj"])
def implicit_conj(context, state, x_binding_introduced, x_binding_first, x_binding_second):
    yield from and_c(context, state, x_binding_introduced, x_binding_first, x_binding_second)


@Predication(vocabulary, library="system", names=["card"])
def card_cex(context, state, c_count, e_introduced_binding, x_target_binding):
    if c_count.isnumeric():
        yield state.set_variable_data(x_target_binding.variable.name,
                                      determiner=VariableCriteria(context.current_predication(),
                                                                  x_target_binding.variable.name,
                                                                  min_size=int(c_count),
                                                                  max_size=int(c_count)))
    else:
        context.report_error(["formNotUnderstood", "card_cex"])


# This version of card() is used to mean "the number x, on its own" and not "x of something"
@Predication(vocabulary, library="system", names=["card"])
def card_cxi(context, state, c_count, x_binding, i_binding):
    def bound_variable(value):
        if value == c_value:
            return True
        else:
            context.report_error(["notAThing", x_binding.value, x_binding.variable.name])
            return False

    def unbound_variable():
        yield c_value

    if isinstance(c_count, numbers.Number) or (isinstance(c_count, str) and c_count.isnumeric()):
        c_value = int(c_count)
        yield from combinatorial_predication_1(context, state,
                                               x_binding,
                                               bound_variable,
                                               unbound_variable)


def generate_not_error(context, unscoped_referenced_variables):
    if len(unscoped_referenced_variables) == 0:
        quantifier_variable = context.current_predication().args[1].args[0]
        context.report_error(["notAllError", quantifier_variable, ["AfterFullPhrase", quantifier_variable]], force=True)

    elif len(unscoped_referenced_variables) == 1:
        context.report_error(["notError", ["AfterFullPhrase", unscoped_referenced_variables[0]]], force=True)

    else:
        context.report_error(["notClause"], force=True)


# neg() is an operation on the truth of its entire scopal arg, which means that it needs to evaluate phase 1 and phase 2
# of its scopal arg in order to know if that arg was "true", it isn't enough to know if a particular solution is true
@Predication(vocabulary, library="system", names=["neg"])
def neg(context, state, e_introduced_binding, h_scopal):
    pipeline_logger.debug(f"Neg: {str(state)}")
    # Gather all the bound x variables and their values that are referenced in h_scopal
    referenced_x_variables = gather_referenced_x_variables_from_tree(h_scopal)

    # Record all the variables this neg() has scope over so we can add it as an event later
    scoped_variables, unscoped_variables = gather_scoped_variables_from_tree_at_index(state.get_binding("tree").value[0]["Tree"], context.current_predication_index())

    # Referenced variables that are not scoped in h_scopal
    unscoped_referenced_variables = []
    for referenced_x_variable in referenced_x_variables:
        if referenced_x_variable in unscoped_variables:
            unscoped_referenced_variables.append(referenced_x_variable)

    negated_predication_info = NegatedPredication(context.current_predication(), scoped_variables)

    # If a state makes h_scopal True, this predication fails since it is neg().
    # Conversely, we need to return the neg() success states too. neg() succeeds when h_scopal fails
    # Use tree_solutions to run numeric criteria on the "not" clause. So that a phrase like
    # "which files not in this folder are not large?" would work (and properly count the plural "files")
    new_tree_info = copy.deepcopy(context.tree_info)
    new_tree_info["Tree"] = h_scopal
    new_tree_info["NegatedSubtree"] = True

    # Don't create a child solver since it shares the context with the parent
    # We want the negation() tree to be completely run on its own, isolated, so
    # We can return particular areas about the tree and not have its phase 2 errors
    # contaminate the errors from the parent
    tree_solver = TreeSolver(context.new_initial_context())

    subtree_state = state.set_x("tree", (new_tree_info,))
    had_negative_success = False
    had_negative_failure = False
    wh_phrase_variable = perplexity.tree.get_wh_question_variable(state.get_binding("tree").value[0])

    # use the same interpretation for the subtree that the main tree used
    for tree_record in tree_solver.tree_solutions(subtree_state, new_tree_info, interpretation=context._interpretation, wh_phrase_variable=wh_phrase_variable):
        if tree_record["SolutionGroupGenerator"] is not None:
            # There were solutions, so this is true,
            # don't yield it since neg() makes it False
            generate_not_error(context, unscoped_referenced_variables)
            had_negative_success = True
            break
        elif tree_record["Error"] is not None and tree_record["Error"][1] is not None and tree_record["Error"][1][0] == "formNotUnderstood":
            # this was not a logical failure, we simply didn't understand
            continue
        else:
            had_negative_failure = True

    if not had_negative_success and had_negative_failure:
        # There were no solutions for this combination_state, and there were legitimate failures
        # (not just phrases we didn't understand) so it is false, and thus true
        # Record that this was a negative success for debugging purposes
        negative_success_state = state.add_to_e("negated_predications",
                                                context.current_predication_index(),
                                                negated_predication_info)
        yield negative_success_state.add_to_e("negated_successes", context.current_predication_index(), True)


pipeline_logger = logging.getLogger('Pipeline')

