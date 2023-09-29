import copy
import numbers
import perplexity.messages
from esl.esl_planner import do_task
from esl.esl_planner_description import convert_to_english
from perplexity.execution import report_error, call, execution_context
from perplexity.generation import english_for_delphin_variable
from perplexity.plurals import VariableCriteria, GlobalCriteria
from perplexity.predications import combinatorial_predication_1, in_style_predication_2, \
    lift_style_predication_2, concept_meets_constraint
from perplexity.set_utilities import Measurement
from perplexity.sstring import s
from perplexity.system_vocabulary import system_vocabulary, quantifier_raw
from perplexity.transformer import TransformerMatch, TransformerProduction
from perplexity.tree import find_predication_from_introduced, get_wh_question_variable, TreePredication
from perplexity.user_interface import UserInterface
from perplexity.utilities import ShowLogging, sentence_force
from perplexity.vocabulary import Predication, EventOption, Transform, override_predications, ValueSize
from esl.worldstate import *

vocabulary = system_vocabulary()
override_predications(vocabulary, "user", ["card__cex__"])


# ******** Helpers ************
def convert_noun_structure(binding_value):
    new_list = []
    for item in binding_value:
        if hasattr(item, "is_concept"):
            new_list.append(item.modifiers())
        else:
            new_list.append(item)
    return tuple(new_list)


def variable_group_values_to_list(variable_group):
    return [binding.value for binding in variable_group.solution_values]


def check_concept_solution_group_constraints(state_list, x_what_variable_group, check_concepts):
    # These are concepts. Only need to check the first because:
    # If one item in the group is a concept, they all are
    assert is_concept(x_what_variable_group.solution_values[0].value[0])
    x_what_variable = x_what_variable_group.solution_values[0].variable.name

    # First we need to check to make sure that the specific concepts in the solution group like "steak", "menu",
    # etc meet the requirements I.e. if there are two preparations of steak on the menu and you say
    # "I'll have the steak" you should get an error
    x_what_values = [x.value for x in x_what_variable_group.solution_values]
    x_what_individuals_set = set()
    for value in x_what_values:
        x_what_individuals_set.update(value)
    concept_count, concept_in_scope_count, instance_count, instance_in_scope_count = count_of_instances_and_concepts(
        state_list[0], list(x_what_individuals_set))
    return concept_meets_constraint(state_list[0].get_binding("tree").value[0],
                                    x_what_variable_group.variable_constraints,
                                    concept_count,
                                    concept_in_scope_count,
                                    instance_count,
                                    instance_in_scope_count,
                                    check_concepts,
                                    variable=x_what_variable,
                                    value=x_what_variable_group.solution_values[0].value[0])


def is_past_tense(tree_info):
    return tree_info["Variables"][tree_info["Index"]]["TENSE"] in ["past"]


def is_present_tense(tree_info):
    return tree_info["Variables"][tree_info["Index"]]["TENSE"] in ["pres", "untensed"]


def is_future_tense(tree_info):
    return tree_info["Variables"][tree_info["Index"]]["TENSE"] in ["fut"]


def is_question(tree_info):
    return sentence_force(tree_info["Variables"]) in ["ques", "prop-or-ques"]


def is_wh_question(tree_info):
    if is_question(tree_info):
        return get_wh_question_variable(tree_info)

    return False


def is_request_from_tree(tree_info):
    introduced_predication = find_predication_from_introduced(tree_info["Tree"], tree_info["Index"])
    return sentence_force(tree_info["Variables"]) in ["ques", "prop-or-ques"] or \
        introduced_predication.name.endswith("_request") or \
        tree_info["Variables"][tree_info["Index"]]["TENSE"] == "fut"


def valid_player_request(state, x_objects, valid_types=None):
    # Things players can request
    if valid_types is None:
        valid_types = ["food", "table", "menu", "bill"]

    store_objects = [object_to_store(x) for x in x_objects]
    for store in store_objects:
        if not sort_of(state, store, valid_types):
            return False

    return True


def min_from_variable_group(variable_group):
    return variable_group.variable_constraints.min_size if variable_group.variable_constraints is not None else 1


# ******** Transforms ************
# Convert "would like <noun>" to "want <noun>"
@Transform(vocabulary)
def would_like_to_want_transformer():
    production = TransformerProduction(name="_want_v_1", args={"ARG0": "$e1", "ARG1": "$x1", "ARG2": "$x2"})
    like_match = TransformerMatch(name_pattern="_like_v_1", args_pattern=["e", "x", "x"],
                                  args_capture=[None, "x1", "x2"])
    return TransformerMatch(name_pattern="_would_v_modal", args_pattern=["e", like_match], args_capture=["e1", None],
                            removed=["_would_v_modal", "_like_v_1"], production=production)


# Convert "Can/could I x?", "I can/could x?" to "I x_able x?"
# "What can I x?"
@Transform(vocabulary)
def can_to_able_intransitive_transformer():
    production = TransformerProduction(name="$|name|_able", args={"ARG0": "$e1", "ARG1": "$x1"})
    target = TransformerMatch(name_pattern="*", name_capture="name", args_pattern=["e", "x"], args_capture=[None, "x1"])
    return TransformerMatch(name_pattern="_can_v_modal", args_pattern=["e", target], args_capture=["e1", None],
                            removed=["_can_v_modal"], production=production)


# Convert "can I have a table/steak/etc?" or "what can I have?"
# To: able_to
@Transform(vocabulary)
def can_to_able_transitive_transformer():
    production = TransformerProduction(name="$|name|_able", args={"ARG0": "$e1", "ARG1": "$x1", "ARG2": "$x2"})
    target = TransformerMatch(name_pattern="*", name_capture="name", args_pattern=["e", "x", "x"],
                              args_capture=[None, "x1", "x2"])
    return TransformerMatch(name_pattern="_can_v_modal", args_pattern=["e", target], args_capture=["e1", None],
                            removed=["_can_v_modal"], production=production)


# Convert "can you show me the menu" to "you show_able the menu"
@Transform(vocabulary)
def can_to_able_transitive_transformer_indir_obj():
    production = TransformerProduction(name="$|name|_able", args={"ARG0": "$e1", "ARG1": "$x1", "ARG2": "$x2", "ARG4": "$x3"})
    target = TransformerMatch(name_pattern="*", name_capture="name", args_pattern=["e", "x", "x", "x"],
                              args_capture=[None, "x1", "x2","x3"])
    return TransformerMatch(name_pattern="_can_v_modal", args_pattern=["e", target], args_capture=["e1", None],
                            removed=["_can_v_modal"], production=production)

# can i pay with cash
@Transform(vocabulary)
def can_paytype_transformer():
    production = TransformerProduction(name="$|name|_request", args={"ARG0": "$e1", "ARG1": "$x1", "ARG2": "$i1", "ARG3": "$i2"})
    target = TransformerMatch(name_pattern="*", name_capture="name", args_pattern=["e", "x", "i", "i"], args_capture=[None, "x1","i1","i2"])
    return TransformerMatch(name_pattern="_can_v_modal", args_pattern=["e", target], args_capture=["e1", None],
                            removed=["_can_v_modal"], production=production)


# Convert "May I x?"" to "I x_request x?"
@Transform(vocabulary)
def may_to_able_intransitive_transformer():
    production = TransformerProduction(name="$|name|_able", args={"ARG0": "$e1", "ARG1": "$x1"})
    target = TransformerMatch(name_pattern="*", name_capture="name", args_pattern=["e", "x"], args_capture=[None, "x1"])
    return TransformerMatch(name_pattern="_may_v_modal", args_pattern=["e", target], args_capture=["e1", None],
                            removed=["_may_v_modal"], production=production)


# Convert "may I have a table/steak/etc?" or "what may I have?"
# To: able_to
@Transform(vocabulary)
def may_to_able_transitive_transformer():
    production = TransformerProduction(name="$|name|_able", args={"ARG0": "$e1", "ARG1": "$x1", "ARG2": "$x2"})
    target = TransformerMatch(name_pattern="*", name_capture="name", args_pattern=["e", "x", "x"],
                              args_capture=[None, "x1", "x2"])
    return TransformerMatch(name_pattern="_may_v_modal", args_pattern=["e", target], args_capture=["e1", None],
                            removed=["_may_v_modal"], production=production)

# may i pay with cash
@Transform(vocabulary)
def may_paytype_transformer():
    production = TransformerProduction(name="$|name|_request", args={"ARG0": "$e1", "ARG1": "$x1", "ARG2": "$i1", "ARG3": "$i2"})
    target = TransformerMatch(name_pattern="*", name_capture="name", args_pattern=["e", "x", "i", "i"], args_capture=[None, "x1","i1","i2"])
    return TransformerMatch(name_pattern="_may_v_modal", args_pattern=["e", target], args_capture=["e1", None],
                            removed=["_may_v_modal"], production=production)


# Convert "I want to x y" to "I x_request y"
@Transform(vocabulary)
def want_removal_transitive_transformer():
    production = TransformerProduction(name="$|name|_request", args={"ARG0": "$e1", "ARG1": "$x1", "ARG2": "$x2"})
    target = TransformerMatch(name_pattern="*", name_capture="name", args_pattern=["e", "x", "x"],
                              args_capture=[None, "x1", "x2"])
    return TransformerMatch(name_pattern="_want_v_1", args_pattern=["e", "x", target], args_capture=["e1", None, None],
                            removed=["_want_v_1"], production=production)


# Convert "I want to x" to "I x_request"
@Transform(vocabulary)
def want_removal_intransitive_transformer():
    production = TransformerProduction(name="$|name|_request", args={"ARG0": "$e1", "ARG1": "$x1"})
    target = TransformerMatch(name_pattern="*", name_capture="name", args_pattern=["e", "x"], args_capture=[None, "x1"])
    return TransformerMatch(name_pattern="_want_v_1", args_pattern=["e", "x", target], args_capture=["e1", None, None],
                            removed=["_want_v_1"], production=production)


# Convert "I want to pay with x" to "I pay_for_request"
@Transform(vocabulary)
def want_removal_paytype_transformer():
    production = TransformerProduction(name="$|name|_request", args={"ARG0": "$e1", "ARG1": "$x1", "ARG2": "$i1", "ARG3": "$i2"})
    target = TransformerMatch(name_pattern="*", name_capture="name", args_pattern=["e", "x", "i", "i"], args_capture=[None, "x1","i1","i2"])
    return TransformerMatch(name_pattern="_want_v_1", args_pattern=["e", "x", target], args_capture=["e1", None, None],
                            removed=["_want_v_1"], production=production)


# Convert "I would like to x y" to "I x_request y"
@Transform(vocabulary)
def would_like_removal_transitive_transformer():
    production = TransformerProduction(name="$|name|_request", args={"ARG0": "$e1", "ARG1": "$x1", "ARG2": "$x2"})
    target = TransformerMatch(name_pattern="*", name_capture="name", args_pattern=["e", "x", "x"],
                              args_capture=[None, "x1", "x2"])
    like_match = TransformerMatch(name_pattern="_like_v_1", args_pattern=["e", "x", target],
                                  args_capture=[None, None, None])
    would_match = TransformerMatch(name_pattern="_would_v_modal", args_pattern=["e", like_match],
                                   args_capture=["e1", None], removed=["_would_v_modal", "_like_v_1"],
                                   production=production)
    return would_match


# Convert "I would like to x" to "I x_request x"
@Transform(vocabulary)
def would_like_removal_intransitive_transformer():
    production = TransformerProduction(name="$|name|_request", args={"ARG0": "$e1", "ARG1": "$x1"})
    target = TransformerMatch(name_pattern="*", name_capture="name", args_pattern=["e", "x"], args_capture=[None, "x1"])
    like_match = TransformerMatch(name_pattern="_like_v_1", args_pattern=["e", "x", target],
                                  args_capture=[None, None, None])
    would_match = TransformerMatch(name_pattern="_would_v_modal", args_pattern=["e", like_match],
                                   args_capture=["e1", None], removed=["_would_v_modal", "_like_v_1"],
                                   production=production)
    return would_match


# Convert "I would x y" to "I x_request y" (i.e. "I would have a menu")
@Transform(vocabulary)
def want_removal_transitive_transformer():
    production = TransformerProduction(name="$|name|_request", args={"ARG0": "$e1", "ARG1": "$x1", "ARG2": "$x2"})
    target = TransformerMatch(name_pattern="*", name_capture="name", args_pattern=["e", "x", "x"],
                              args_capture=[None, "x1", "x2"])
    return TransformerMatch(name_pattern="_would_v_modal", args_pattern=["e", target], args_capture=["e1", None],
                            removed=["_would_v_modal"], production=production)


# ***************************


@Predication(vocabulary, names=["pron"])
def pron(state, x_who_binding):
    person = int(state.get_binding("tree").value[0]["Variables"][x_who_binding.variable.name]["PERS"])
    plurality = "unknown"
    if "NUM" in state.get_binding("tree").value[0]["Variables"][x_who_binding.variable.name].keys():
        plurality = (state.get_binding("tree").value[0]["Variables"][x_who_binding.variable.name]["NUM"])

    def bound_variable(value):
        if person == 2 and value == "restaurant":
            return True
        if person == 1 and is_user_type(value):
            return True
        else:
            report_error(["dontKnowActor", x_who_binding.variable.name, state.get_reprompt()])

    def unbound_variable():
        if person == 2:
            yield "restaurant"
        if person == 1:
            if plurality == "pl":
                yield "user"
                yield "son1"

            else:
                yield "user"

    yield from combinatorial_predication_1(state, x_who_binding, bound_variable, unbound_variable)


@Predication(vocabulary, names=["generic_entity"])
def generic_entity(state, x_binding):
    def bound(val):
        return val == ReferringExpr(execution_context().current_predication(), x_binding.variable.name)

    def unbound():
        yield ReferringExpr(execution_context().current_predication(), x_binding.variable.name)

    yield from combinatorial_predication_1(state, x_binding, bound, unbound)


@Predication(vocabulary, names=["_okay_a_1"])
def _okay_a_1(state, i_binding, h_binding):
    yield from call(state, h_binding)


@Predication(vocabulary, names=["much-many_a"], handles=[("Measure", EventOption.optional)])
def much_many_a(state, e_binding, x_binding):
    if "Measure" in e_binding.value.keys():
        measure_into_variable = e_binding.value["Measure"]["Value"]
        # if we are measuring x_binding should have a ReferringExpr() that is the type of measurement
        x_binding_value = x_binding.value
        if len(x_binding_value) == 1 and is_referring_expr(x_binding_value[0]):
            # Set the actual value of the measurement to a string so that
            # a predication that receives it knows we are looking to fill in an unbound value
            measurement = Measurement(x_binding_value[0], measure_into_variable)

            # Replace x5 with measurement
            yield state.set_x(x_binding.variable.name, (measurement,))


@Predication(vocabulary, names=["measure"])
def measure(state, e_binding, e_binding2, x_binding):
    yield state.add_to_e(e_binding2.variable.name, "Measure",
                         {"Value": x_binding.variable.name,
                          "Originator": execution_context().current_predication_index()})


@Predication(vocabulary, names=["abstr_deg"])
def abstr_deg(state, x_binding):
    yield state.set_x(x_binding.variable.name, (referring_expr_from_lemma("abstract_degree"),))


@Predication(vocabulary, names=["card"])
def card(state, c_number, e_binding, x_binding):
    if isinstance(c_number,str):
        if c_number.isnumeric():
            c_number = int(c_number)
        else:
            report_error(["Notnumeric",state.get_reprompt()])
            return
    x_binding_value = state.get_binding(x_binding.variable.name).value
    if len(x_binding_value) == 1 and is_referring_expr(x_binding_value[0]) and isinstance(c_number, numbers.Number):
        e_what_value = e_binding.value
        modified = x_binding_value[0].add_bound_modifier(execution_context().current_predication(), [c_number, e_what_value, x_binding.value])

        yield state.set_x(x_binding.variable.name, (modified,))


@Predication(vocabulary, names=["card"])
def card_system(state, c_number, e_binding, x_binding):
    yield from perplexity.system_vocabulary.card_cex(state, c_number, e_binding, x_binding)


@Predication(vocabulary, names=["_for_p"], arguments=[("e",), ("x", ValueSize.all), ("x", ValueSize.all)])
def _for_p(state, e_binding, x_what_binding, x_for_binding):
    def both_bound_function(x_what, x_for):
        if len(x_what) == 1:
            x_what_type = perplexity.predications.value_type(x_what[0])
            if x_what_type == perplexity.predications.VariableValueType.referring_expression:
                # Is a referring expression, we'll add ourself to it below
                # Concepts just flow through
                return True

            elif x_what_type in [perplexity.predications.VariableValueType.instance, perplexity.predications.VariableValueType.concept]:
                if x_what_type == perplexity.predications.VariableValueType.concept:
                    store_object = x_what[0].concept_name
                else:
                    store_object = x_what

                if sort_of(state, store_object, "table"):
                    # We only have tables for 2
                    if len(x_for) == 1 and isinstance(x_for[0], numbers.Number) or is_user_type(x_for):
                        return True

        elif is_user_type(x_for):
            return True

    def x_what_unbound(x_for):
        if False:
            yield None

    def x_for_unbound(x_what):
        report_error(['errorText', "Host: Sorry, I'm not here to explain things to you ...",state.get_reprompt()])
        if False:
            yield None

    # Make this lift_style so that "for my son and I" gets properly interpreted as "together"
    # at least as an alternative
    for solution in lift_style_predication_2(state, x_what_binding, x_for_binding,
                                             both_bound_function,
                                             x_what_unbound,
                                             x_for_unbound):
        x_what_value = solution.get_binding(x_what_binding.variable.name).value
        if is_concept(x_what_value[0]):
            x_for_value = solution.get_binding(x_for_binding.variable.name).value
            if isinstance(x_for_value[0], numbers.Number):
                modified = x_what_value[0].add_criteria(rel_subjects, "maxCapacity", x_for_value[0])
            elif is_user_type(x_for_value):
                modified = x_what_value[0].add_criteria(rel_subjects, "maxCapacity", len(x_for_value))

            yield solution.set_x(x_what_binding.variable.name, (modified,))

        elif is_referring_expr(x_what_value[0]):
            e_what_value = solution.get_binding(e_binding.variable.name).value
            x_for_value = solution.get_binding(x_for_binding.variable.name).value
            modified = x_what_value[0].add_bound_modifier(execution_context().current_predication(), [e_what_value, x_what_value, x_for_value])
            yield solution.set_x(x_what_binding.variable.name, (modified,))

        else:
            yield solution


@Predication(vocabulary, names=["_cash_n_1"])
def _cash_n_1(state, x_bind):
    def bound(val):
        return val == "cash"

    def unbound():
        yield "cash"

    yield from combinatorial_predication_1(state, x_bind, bound, unbound)


@Predication(vocabulary, names=["_card_n_1"])
def _card_n_1(state, x_bind):
    def bound(val):
        return val == "card"

    def unbound():
        yield "card"

    yield from combinatorial_predication_1(state, x_bind, bound, unbound)


@Predication(vocabulary, names=["_credit_n_1"])
def _credit_n_1(state, x_bind):
    def bound(val):
        return val == "credit"

    def unbound():
        yield "credit"

    yield from combinatorial_predication_1(state, x_bind, bound, unbound)


@Predication(vocabulary, names=["_tomato_n_1"])
def _tomato_n_1(state, x_bind):
    def bound(val):
        report_error(["errorText","no declarative tomato",state.get_reprompt()])

    def unbound():
        yield ReferringExpr("tomato")

    yield from combinatorial_predication_1(state, x_bind, bound, unbound)


@Predication(vocabulary, names=["unknown"])
def unknown(state, e_binding, x_binding):
    operations = state.handle_world_event(["unknown", x_binding.value[0]])
    if operations is not None:
        yield state.record_operations(operations)


@Predication(vocabulary, names=["unknown"])
def unknown_eu(state, e_binding, u_binding):
    yield state


@Predication(vocabulary, names=["_yes_a_1", "_yup_a_1", "_sure_a_1", "_yeah_a_1"])
def _yes_a_1(state, i_binding, h_binding):
    yield state.record_operations(state.handle_world_event(["yes"]))


@Predication(vocabulary, names=["_no_a_1", "_nope_a_1"])
def _no_a_1(state, i_binding, h_binding):
    yield state.record_operations(state.handle_world_event(["no"]))


@Predication(vocabulary, names=["person"])
def person(state, x_person_binding):
    yield from match_all_n("person", state, x_person_binding)


def handles_noun(state, noun_lemma):
    handles = ["thing"] + list(all_specializations(state, "thing"))
    return noun_lemma in handles


# Simple example of using match_all that doesn't do anything except
# make sure we don't say "I don't know the word book"
@Predication(vocabulary, names=["match_all_n"], matches_lemma_function=handles_noun)
def match_all_n(noun_type, state, x_binding):
    def bound_variable(value):
        if sort_of(state, value, noun_type):
            return True
        else:
            report_error(["notAThing", x_binding.value, x_binding.variable.name,state.get_reprompt()])
            return False

    def unbound_variable_instances():
        for item in all_instances(state, noun_type):
            yield item

    def unbound_variable_concepts():
        yield store_to_object(state, noun_type)
        for item in all_specializations(state, noun_type):
            yield store_to_object(state, item)

    # Yield the referring expression first, and not as a combinatoric variable
    # because solutions can never mix conceptual and non-conceptual terms so it isn't
    # true that it is combinatoric since you can't pick the conceptual and include it with another and have
    # it be valid
    # yield state.set_x(x_binding.variable.name, (ReferringExpr(execution_context().current_predication(), x_binding.variable.name),))

    # Then yield a combinatorial value of all types
    yield from combinatorial_predication_1(state, x_binding, bound_variable, unbound_variable_concepts)

    # Then instances
    yield from combinatorial_predication_1(state, x_binding, bound_variable, unbound_variable_instances)


@Predication(vocabulary, names=["match_all_n"], matches_lemma_function=handles_noun)
def match_all_the_concept_n(noun_type, state, x_binding):
    def bound_variable(value):
        if sort_of(state, value, noun_type):
            return True
        else:
            report_error(["notAThing", x_binding.value, x_binding.variable.name,state.get_reprompt()])
            return False

    def unbound_variable_instances():
        for item in all_instances(state, noun_type):
            yield item

    if rel_check(state, noun_type, "conceptInScope", "true") and\
            x_binding.variable.quantifier.global_criteria == GlobalCriteria.all_rstr_meet_criteria:
        for instance_state in combinatorial_predication_1(state, x_binding, bound_variable, unbound_variable_instances):
            new_criteria = copy.deepcopy(x_binding.variable.quantifier)
            new_criteria.global_criteria = None
            yield instance_state.set_variable_data(x_binding.variable.name, quantifier=new_criteria)


@Predication(vocabulary, names=["match_all_n"], matches_lemma_function=handles_noun)
def match_all_n_i(noun_type, state, x_binding, i_binding):
    yield from match_all_n(noun_type, state, x_binding)


@Predication(vocabulary, names=["_some_q"])
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


@Predication(vocabulary, names=["_vegetarian_a_1"])
def _vegetarian_a_1(state, e_introduced_binding, x_target_binding):
    def criteria_bound(value):
        veg = all_instances_and_spec(state, "veggie")
        if value in serial_store_to_object(state,veg):
            return True
        else:
            report_error(["not_adj","vegetarian",state.get_reprompt()])
            return False

    def unbound_values():
        for i in all_instances_and_spec(state, "veggie"):
            yield store_to_object(state,i)

    yield from combinatorial_predication_1(state, x_target_binding,
                                           criteria_bound,
                                           unbound_values)


class PastParticiple:
    def __init__(self, predicate_name_list, lemma):
        self.predicate_name_list = predicate_name_list
        self.lemma = lemma

    def predicate_function(self, state, e_introduced_binding, i_binding, x_target_binding):
        def bound(value):
            if (object_to_store(value), self.lemma) in state.all_rel("isAdj"):
                return True
            else:
                report_error(["not_adj", self.lemma,state.get_reprompt()])
                return False

        def unbound():
            for i in state.all_rel("isAdj"):
                if object_to_store(i[1]) == self.lemma:
                    yield i[0]

        yield from combinatorial_predication_1(state, x_target_binding,
                                               bound,
                                               unbound)


grilled = PastParticiple(["_grill_v_1"], "grilled")
roasted = PastParticiple(["_roast_v_cause"], "roasted")
smoked = PastParticiple(["_smoke_v_1"], "smoked")


@Predication(vocabulary, names=grilled.predicate_name_list)
def _grill_v_1(state, e_introduced_binding, i_binding, x_target_binding):
    yield from grilled.predicate_function(state, e_introduced_binding, i_binding, x_target_binding)


@Predication(vocabulary, names=roasted.predicate_name_list)
def _roast_v_1(state, e_introduced_binding, i_binding, x_target_binding):
    yield from roasted.predicate_function(state, e_introduced_binding, i_binding, x_target_binding)

@Predication(vocabulary, names=smoked.predicate_name_list)
def _smoke_v_1(state, e_introduced_binding, i_binding, x_target_binding):
    yield from smoked.predicate_function(state, e_introduced_binding, i_binding, x_target_binding)



@Predication(vocabulary, names=("_on_p_loc",))
def on_p_loc(state, e_introduced_binding, x_actor_binding, x_location_binding):
    def check_item_on_item(item1, item2):
        if (item1, item2) in state.all_rel("on"):
            return True
        else:
            report_error(["notOn", item1, item2, state.get_reprompt()])

    def all_item1_on_item2(item2):
        for i in state.all_rel("on"):
            if i[1] == object_to_store(item2):
                yield store_to_object(state,i[0])

    def all_item2_containing_item1(item1):
        for i in state.all_rel("on"):
            if i[0] == item1:
                yield i[1]

    yield from in_style_predication_2(state,
                                      x_actor_binding,
                                      x_location_binding,
                                      check_item_on_item,
                                      all_item1_on_item2,
                                      all_item2_containing_item1)


@Predication(vocabulary, names=("_with_p",))
def _with_p(state, e_introduced_binding, e_main, x_binding):
    yield state.add_to_e(e_main.variable.name, "With", x_binding.value[0])


@Predication(vocabulary, names=["_pay_v_for","_pay_v_for_able","_pay_v_for_request"], handles=[("With", EventOption.optional)])
def _pay_v_for(state, e_introduced_binding, x_actor_binding, i_binding1,i_binding2):
    if not state.sys["responseState"] == "way_to_pay":
        yield do_task(state, [("respond", "It's not time to pay yet.")])
        return
    if not e_introduced_binding.value["With"] in ["cash","card"]:
        yield do_task(state,[("respond","You can't pay with that.")])
        return

    yield state.record_operations(state.handle_world_event(["unknown", e_introduced_binding.value["With"]]))


@Predication(vocabulary, names=["_want_v_1"])
def _want_v_1(state, e_introduced_binding, x_actor_binding, x_object_binding):
    def criteria_bound(x_actor, x_object):
        if is_user_type(x_actor):
            return True

        elif "want" in state.rel.keys():
            if (x_actor, x_object) in state.all_rel("want"):
                return True

        else:
            report_error(["notwant", "want", x_actor, state.get_reprompt()])
            return False

    def wanters_of_obj(x_object):
        if "want" in state.rel.keys():
            for i in state.all_rel("want"):
                if i[1] == x_object:
                    yield i[0]

    def wanted_of_actor(x_actor):
        if "want" in state.rel.keys():
            for i in state.all_rel("want"):
                if i[0] == x_actor:
                    yield i[1]

    yield from in_style_predication_2(state, x_actor_binding, x_object_binding, criteria_bound,
                                      wanters_of_obj, wanted_of_actor)


@Predication(vocabulary, names=["solution_group__want_v_1"])
def want_group(state_list, has_more, e_introduced_binding_list, x_actor_variable_group, x_what_variable_group):
    current_state = copy.deepcopy(state_list[0])

    # This may be getting called with concepts or instances, before we call the planner
    # we need to decide if we have the requisite amount of them
    if is_referring_expr(x_actor_variable_group.solution_values[0]):
        # We don't want to deal with conceptual actors, fail this solution group
        # and wait for the one with real actors
        yield []

    # We do have lots of places where we deal with conceptual "wants", such as: "I want the menu", "I'll have a steak"
    # In fact, we *never* deal with wanting a particular instance because that would mean "I want that particular steak right there"
    # and we don't support that
    # These are concepts. Only need to check the first because:
    # If one item in the group is a concept, they all are
    if is_concept(x_what_variable_group.solution_values[0].value[0]):
        # We first check to make sure the constraints are valid for this concept.
        # Because in "I want x", 'x' is always a concept, but the constraint is on the instances
        # (as in "I want a steak" meaning "I want 1 instance of the concept of steak", we tell
        # check_concept_solution_group_constraints to check instances via check_concepts=False
        if check_concept_solution_group_constraints(state_list, x_what_variable_group, check_concepts=False):
            # If there is more than one concept here, they said something like "we want steaks and fries" but doing the magic
            # To figure that out how much of each is too much
            x_what_values = [x.value for x in x_what_variable_group.solution_values]
            x_what_individuals_set = set()
            for value in x_what_values:
                x_what_individuals_set.update(value)
            if len(x_what_individuals_set) > 1:
                report_error(["errorText", "One thing at a time, please!", current_state.get_reprompt()], force=True)
                yield []
                return

            # At this point we are only dealing with one concept
            first_x_what_binding_value = copy.deepcopy(x_what_variable_group.solution_values[0].value[0])

            # Even though it is only one thing, they could have said something like "We want steaks" so they really want more than one
            # Give them the minimum number by adding a card() predication into the concept
            #   - card(state, c_number, e_binding, x_binding):
            # args = [x_what_variable_group.variable_constraints.min_size, "e999", first_x_what_binding_value.variable_name]
            # first_x_what_binding_value = first_x_what_binding_value.add_modifier(TreePredication(0, "card", args, arg_names=["CARG", "ARG0", "ARG1"]))
            actor_values = [x.value for x in x_actor_variable_group.solution_values]
            current_state = do_task(current_state.world_state_frame(), [('satisfy_want', actor_values, [(first_x_what_binding_value,)], min_from_variable_group(x_what_variable_group))])
            if current_state is None:
                yield []
            else:
                yield [current_state]

        else:
            yield []
    else:
        yield []


@Predication(vocabulary, names=["_check_v_1"])
def _check_v_1(state, e_introduced_binding, x_actor_binding, i_object_binding):
    if i_object_binding.value is not None:
        return

    def criteria_bound(x):
        return x == "restaurant"

    def unbound():
        yield None

    yield from combinatorial_predication_1(state, x_actor_binding, criteria_bound, unbound)


@Predication(vocabulary, names=["solution_group__check_v_1"])
def _check_v_1_group(state_list, has_more, e_introduced_binding, x_actor_binding, i_object_binding):
    current_state = copy.deepcopy(state_list[0])
    final_state = do_task(current_state.world_state_frame(), [('get_bill',)])
    if final_state is None:
        yield []
    else:
        yield[final_state]



@Predication(vocabulary, names=["_give_v_1"])
def _give_v_1(state, e_introduced_binding, x_actor_binding, x_object_binding, x_target_binding):
    if state.get_binding(x_actor_binding.variable.name).value[0] == "restaurant":
        if is_user_type(state.get_binding(x_target_binding.variable.name).value[0]):
            if not state.get_binding(x_object_binding.variable.name).value[0] is None:
                yield state.record_operations(
                    state.handle_world_event(
                        ["user_wants", state.get_binding(x_object_binding.variable.name).value[0]]))


@Predication(vocabulary, names=["_show_v_1", "_show_v_1_able"])
def _show_v_1(state, e_introduced_binding, x_actor_binding, x_target_binding, x_to_actor_binding):
    if not is_present_tense(state.get_binding("tree").value[0]):
        return
    if is_concept(x_actor_binding) or is_concept(x_to_actor_binding):
        return
    if not is_computer_type(x_actor_binding.value):
        report_error(["dontKnowHow"])
        return

    def bound(x_actor, x_object):
        # Do a cursory check to make sure it is some kind of "menu"
        # More detailed check is in the group predication
        if is_user_type(x_actor):
            if is_concept(x_object) and x_object.concept_name in ["menu"]:
                return True

            else:
                report_error(["errorText", "Sorry, I can't show you that"])
        else:
            report_error(["dontKnowHow"])
            return

    def wanters_of_obj(x_object):
        # not currently going to support asking who is seating someone
        return

    def wanted_of_actor(x_actor):
        return

    yield from in_style_predication_2(state, x_to_actor_binding, x_target_binding, bound,
                                      wanters_of_obj, wanted_of_actor)


@Predication(vocabulary, names=["solution_group__show_v_1", "solution_group__show_v_1_able"])
def _show_v_cause_group(state_list, has_more, e_introduced_binding, x_actor_variable_group, x_target_variable_group, x_to_actor_variable_group):
    # Only need to check constraints on x_target_variable_group since it is the only variable that is a concept
    # The player is asking to be shown *instances* so check_concepts = False
    if not check_concept_solution_group_constraints(state_list, x_target_variable_group, check_concepts=False):
        yield []
        return

    to_actor_list = variable_group_values_to_list(x_to_actor_variable_group)
    show_list = variable_group_values_to_list(x_target_variable_group)
    current_state = do_task(state_list[0].world_state_frame(),
                            [('satisfy_want', to_actor_list, show_list, min_from_variable_group(x_target_variable_group))])
    if current_state is None:
        yield []

    else:
        yield [current_state]


@Predication(vocabulary, names=["_seat_v_cause", "_seat_v_cause_able"])
def _seat_v_cause(state, e_introduced_binding, x_actor_binding, x_object_binding):
    if is_concept(x_actor_binding) or is_concept(x_object_binding):
        return

    def criteria_bound(x_actor, x_object):
        return is_computer_type(x_actor) and is_user_type(x_object)

    def wanters_of_obj(x_object):
        # not currently going to support asking who is seating someone
        return

    def wanted_of_actor(x_actor):
        return

    yield from in_style_predication_2(state, x_actor_binding, x_object_binding, criteria_bound,
                                      wanters_of_obj, wanted_of_actor)


@Predication(vocabulary, names=["solution_group__seat_v_cause", "solution_group__seat_v_cause_able"])
def _seat_v_cause_group(state_list, has_more, e_introduced_binding, x_actor_variable_group, x_what_variable_group):
    new_state = do_task(state_list[0].world_state_frame(),
                        [('satisfy_want', variable_group_values_to_list(x_what_variable_group), [(ESLConcept("table"),)], 1)])
    if new_state is None:
        yield []
    else:
        yield [new_state]


@Predication(vocabulary, names=["loc_nonsp"])
def loc_nonsp(state, e_introduced_binding, x_actor_binding, x_loc_binding):
    def item1_in_item2(item1, item2):
        if item2 == "today":
            return True

        if (item1, item2) in state.all_rel("contains"):
            return True
        return False

    def items_in_item1(item1):
        for i in state.all_rel("contains"):
            if i[0] == item1:
                yield i[1]

    def item1_in_items(item1):
        for i in state.all_rel("contains"):
            if i[1] == item1:
                yield i[0]

    yield from in_style_predication_2(state, x_actor_binding, x_loc_binding, item1_in_item2, items_in_item1,
                                      item1_in_items)


@Predication(vocabulary, names=["loc_nonsp"])
def loc_nonsp_eex(state, e_introduced_binding, e_binding, x_loc_binding):
    yield state


@Predication(vocabulary, names=["_today_a_1"])
def _today_a_1(state, e_introduced_binding, x_binding):
    def bound_variable(value):
        if value in ["today"]:
            return True
        else:
            report_error(["notAThing", x_binding.value, x_binding.variable.name,state.get_reprompt()])
            return False

    def unbound_variable():
        yield "today"

    yield from combinatorial_predication_1(state, x_binding, bound_variable, unbound_variable)


@Predication(vocabulary, names=["time_n"])
def time_n(state, x_binding):
    def bound_variable(value):
        if value in ["today", "yesterday", "tomorrow"]:
            return True
        else:
            report_error(["notAThing", x_binding.value, x_binding.variable.name,state.get_reprompt()])
            return False

    def unbound_variable():
        yield "today"
        yield "yesterday"
        yield "tomorrow"

    yield from combinatorial_predication_1(state, x_binding, bound_variable, unbound_variable)


@Predication(vocabulary, names=["def_implicit_q", "def_explicit_q"])
def def_implicit_q(state, x_variable_binding, h_rstr, h_body):
    state = state.set_variable_data(x_variable_binding.variable.name,
                                    quantifier=VariableCriteria(execution_context().current_predication(),
                                                                x_variable_binding.variable.name,
                                                                min_size=1,
                                                                max_size=float('inf')))

    yield from quantifier_raw(state, x_variable_binding, h_rstr, h_body)


@Predication(vocabulary, names=["_like_v_1"])
def _like_v_1(state, e_introduced_binding, x_actor_binding, x_object_binding):
    if is_user_type(state.get_binding(x_actor_binding.variable.name).value[0]):
        if not state.get_binding(x_object_binding.variable.name).value[0] is None:
            yield state.record_operations(
                state.handle_world_event(["user_wants", state.get_binding(x_object_binding.variable.name).value[0]]))
    else:
        yield state


@Predication(vocabulary, names=["_please_a_1"])
def _please_a_1(state, e_introduced_binding, e_binding):
    yield state

@Predication(vocabulary, names=["_too_a_also"])
def _too_a_also(state, e_introduced_binding, x_binding):
    yield state


@Predication(vocabulary, names=["_please_v_1"])
def _please_v_1(state, e_introduced_binding, i_binding1, i_binding2):
    yield state


@Predication(vocabulary, names=["polite"])
def polite(state, c_arg, i_binding, e_binding):
    yield state


@Predication(vocabulary, names=["_thanks_a_1", "_then_a_1"])
def _thanks_a_1(state, i_binding, h_binding):
    yield from call(state, h_binding)


# Scenarios:
#   - "I will sit down"
#   - "Will I sit down?"
@Predication(vocabulary, names=["_sit_v_down", "sit_v_1"])
def _sit_v_down_future(state, e_introduced_binding, x_actor_binding):
    tree_info = state.get_binding("tree").value[0]
    if not is_future_tense(tree_info): return
    if is_question(tree_info):
        # None of the future tense questions are valid english in this scenario
        report_error(["unexpected",state.get_reprompt()])
        return

    def bound(x_actor):
        if is_user_type(x_actor):
            return True
        else:
            report_error(["unexpected",state.get_reprompt()])
            return

    def unbound():
        if False:
            yield None

    yield from combinatorial_predication_1(state, x_actor_binding, bound, unbound)


@Predication(vocabulary, names=["solution_group__sit_v_down", "solution_group__sit_v_1"])
def _sit_v_down_future_group(state_list, has_more, e_list, x_actor_variable_group):
    tree_info = state_list[0].get_binding("tree").value[0]
    if not is_future_tense(tree_info): return

    # The planner will only satisfy a want wrt the players
    task = ('satisfy_want', variable_group_values_to_list(x_actor_variable_group), [[referring_expr_from_lemma("table")]], 1)
    final_state = do_task(state_list[0].world_state_frame(), [task])
    if final_state:
        yield [final_state]
    else:
        yield []


# Scenarios:
#   "I sit down"
#   "Who sits down?"
@Predication(vocabulary, names=["_sit_v_down", "_sit_v_1"])
def invalid_present_intransitive(state, e_introduced_binding, x_actor_binding):
    if not is_present_tense(state.get_binding("tree").value[0]): return
    report_error(["unexpected",state.get_reprompt()])
    if False: yield None


# Scenarios:
#   - "Can I sit down?" "Can I sit?" --> request for table
#   - "Who can sit down?"
#   -
#   Poor English:
#   - "Who sits down?"
#   - "Who is sitting down?"
#   - "I can sit down."
@Predication(vocabulary, names=["_sit_v_down_able", "_sit_v_1_able"])
def _sit_v_down_able(state, e_binding, x_actor_binding):
    tree_info = state.get_binding("tree").value[0]
    if not is_present_tense(tree_info):
        report_error(["unexpected",state.get_reprompt()])
        return

    if not is_question(tree_info):
        report_error(["unexpected",state.get_reprompt()])
        return

    def bound(x_actor):
        if is_user_type(x_actor):
            return True
        else:
            report_error(["unexpected",state.get_reprompt()])
            return

    def unbound():
        yield "user"

    yield from combinatorial_predication_1(state, x_actor_binding, bound, unbound)

@Predication(vocabulary, names=["_sit_v_down_request", "_sit_v_1_request"])
def _sit_v_down_request(state, e_binding, x_actor_binding):
    tree_info = state.get_binding("tree").value[0]

    def bound(x_actor):
        if is_user_type(x_actor):
            return True
        else:
            report_error(["unexpected",state.get_reprompt()])
            return

    def unbound():
        yield "user"

    yield from combinatorial_predication_1(state, x_actor_binding, bound, unbound)


@Predication(vocabulary, names=["solution_group__sit_v_down_able", "solution_group__sit_v_1_able", "solution_group__sit_v_down_request", "solution_group__sit_v_1_request"])
def _sit_v_down_able_group(state_list, has_more, e_introduced_binding_list, x_actor_variable_group):
    tree_info = state_list[0].get_binding("tree").value[0]

    # If it is a wh_question, just answer it
    if is_wh_question(tree_info):
        yield state_list
    else:
        # The planner will only satisfy a want wrt the players
        task = ('satisfy_want', variable_group_values_to_list(x_actor_variable_group), [[referring_expr_from_lemma("table")]], 1)
        final_state = do_task(state_list[0].world_state_frame(), [task])
        if final_state:
            yield [final_state]


# Scenarios:
#   "Can I see a menu? -> implied request
#   "I can see a menu. -> poor english
#   Anthing else --> don't understand
@Predication(vocabulary, names=["_see_v_1_able"])
def _see_v_1_able(state, e_introduced_binding, x_actor_binding, x_object_binding):
    tree_info = state.get_binding("tree").value[0]
    if not is_question(tree_info):
        report_error(["unexpected",state.get_reprompt()])
        return

    def both_bound_prediction_function(x_actor, x_object):
        if is_user_type(x_actor):
            if valid_player_request(state, [x_object], valid_types=["menu"]):
                return True
            else:
                report_error(["unexpected",state.get_reprompt()])
                return False

        else:
            # Anything about "you/they will have" is not good english
            report_error(["unexpected",state.get_reprompt()])
            return False

    def actor_unbound(x_object):
        # Anything about "what will x have
        report_error(["unexpected",state.get_reprompt()])
        if False:
            yield None

    def object_unbound(x_actor):
        report_error(["unexpected",state.get_reprompt()])
        if False:
            yield None

    yield from in_style_predication_2(state, x_actor_binding, x_object_binding,
                                      both_bound_prediction_function,
                                      actor_unbound,
                                      object_unbound)


@Predication(vocabulary, names=["solution_group__see_v_1_able"])
def _see_v_1_able_group(state_list, has_more, e_list, x_actor_variable_group, x_object_variable_group):
    # The only valid scenarios for will have are requests, so ...
    # The planner will only satisfy a want wrt the players
    task = ('satisfy_want',
            variable_group_values_to_list(x_actor_variable_group),
            variable_group_values_to_list(x_object_variable_group),
            min_from_variable_group(x_object_variable_group))
    final_state = do_task(state_list[0].world_state_frame(), [task])
    if final_state:
        yield [final_state]
    else:
        yield []


# Scenarios:
#   "I/we will see a menu" -> implied request
#   Poor English:
#       "I will see a table/steak, etc"
@Predication(vocabulary, names=["_see_v_1"])
def _see_v_1_future(state, e_introduced_binding, x_actor_binding, x_object_binding):
    tree_info = state.get_binding("tree").value[0]
    if not is_future_tense(tree_info): return
    if is_question(tree_info):
        # None of the future tense questions are valid english in this scenario
        report_error(["unexpected",state.get_reprompt()])
        return

    def both_bound_prediction_function(x_actor, x_object):
        if is_user_type(x_actor):
            if valid_player_request(state, [x_object], valid_types=["menu"]):
                return True
            else:
                report_error(["unexpected",state.get_reprompt()])
                return False

        else:
            # Anything about "you/they will have" is not good english
            report_error(["unexpected",state.get_reprompt()])
            return False

    def actor_unbound(x_object):
        # Anything about "what will x have
        report_error(["unexpected", state.get_reprompt()])
        if False:
            yield None

    def object_unbound(x_actor):
        report_error(["unexpected", state.get_reprompt()])
        if False:
            yield None

    yield from in_style_predication_2(state, x_actor_binding, x_object_binding,
                                      both_bound_prediction_function,
                                      actor_unbound,
                                      object_unbound)


@Predication(vocabulary, names=["solution_group__see_v_1"])
def _see_v_1_future_group(state_list, has_more, e_list, x_actor_variable_group, x_object_variable_group):
    tree_info = state_list[0].get_binding("tree").value[0]
    if not is_future_tense(tree_info): return

    # The only valid scenarios for will have are requests, so ...
    # The planner will only satisfy a want wrt the players
    task = ('satisfy_want',
            variable_group_values_to_list(x_actor_variable_group),
            variable_group_values_to_list(x_object_variable_group),
            min_from_variable_group(x_object_variable_group))
    final_state = do_task(state_list[0].world_state_frame(), [task])
    if final_state:
        yield [final_state]
    else:
        yield []


# Scenarios:
#   - "Can I take a menu/table/steak?"
# All are poor english
@Predication(vocabulary, names=["_take_v_1_able"])
def _take_v_1_able(state, e_introduced_binding, x_actor_binding, x_object_binding):
    report_error(["unexpected", state.get_reprompt()])
    if False: yield None


# Present tense scenarios:
#   "I get x?", "I get x" --> not great english, respond with an error
#   "What do I see?"
#   "Who sees an x?
#   "I see a menu?"
#   "I see a menu"
@Predication(vocabulary, names=["_get_v_1", "_take_v_1", "_see_v_1"])
def invalid_present_transitive(state, e_introduced_binding, x_actor_binding, x_object_binding):
    if not is_present_tense(state.get_binding("tree").value[0]): return
    report_error(["unexpected", state.get_reprompt()])
    if False: yield None


@Predication(vocabulary, names=["_order_v_1"])
def _order_v_1_past(state, e_introduced_binding, x_actor_binding, x_object_binding):
    if not is_past_tense(state.get_binding("tree").value[0]):
        return
    if is_referring_expr(x_actor_binding) or is_referring_expr(x_object_binding):
        return
    if is_concept(x_actor_binding) or is_concept(x_object_binding):
        return

    def bound(x_actor, x_object):
        for o in rel_objects(state, x_actor, "ordered"):
            if o == x_object:
                return True

        report_error(["verbDoesntApplyArg", x_actor_binding.variable.name, "order", x_object_binding.variable.name, state.get_reprompt()])
        return False

    def actor_from_object(x_object):
        # "Who ordered X?"
        found = False
        for i in rel_subjects(state, "ordered", x_object):
            found = True
            yield store_to_object(i)

        if not found:
            report_error(["Nothing_VTRANS_X", "order", x_object, state.get_reprompt()])

    def object_from_actor(x_actor):
        # "what did I order?"
        found = False
        for i in rel_objects(state, x_actor, "ordered"):
            found = True
            yield store_to_object(state, i)

        if not found:
            report_error(["X_VTRANS_Nothing", "order", convert_to_english(state, x_actor), state.get_reprompt()])

    yield from in_style_predication_2(state, x_actor_binding, x_object_binding, bound, actor_from_object,
                                      object_from_actor)


# Scenarios:
#   - "I will have a steak/menu/table." --> restaurant frame special case for requesting
#   - "I will have a steak/menu/table?" --> Not good english
#   - "You/they, etc will have x" --> Not good english
#   - "Will I have a steak/menu/table?" --> Not good english
#   - "Will you have a table?" --> Not good english
#   - "What will I have?" --> Not good english
#   - "Who will have x?" --> Not good english
@Predication(vocabulary, names=["_have_v_1", "_take_v_1"])
def _have_v_1_future(state, e_introduced_binding, x_actor_binding, x_object_binding):
    tree_info = state.get_binding("tree").value[0]
    if not is_future_tense(tree_info): return
    if is_question(tree_info):
        # None of the future tense questions are valid english in this scenario
        report_error(["unexpected", state.get_reprompt()])
        return

    def both_bound_prediction_function(x_actors, x_objects):
        if is_user_type(x_actors):
            return valid_player_request(state, x_objects)
        else:
            # Anything about "you/they will have" is not good english
            report_error(["unexpected", state.get_reprompt()])
            return False

    def actor_unbound(x_object):
        # Anything about "what will x have
        report_error(["unexpected", state.get_reprompt()])
        if False:
            yield None

    def object_unbound(x_actor):
        report_error(["unexpected", state.get_reprompt()])
        if False:
            yield None

    yield from lift_style_predication_2(state, x_actor_binding, x_object_binding,
                                        both_bound_prediction_function,
                                        actor_unbound,
                                        object_unbound)


@Predication(vocabulary, names=["solution_group__have_v_1", "solution_group__take_v_1"])
def _have_v_1_future_group(state_list, has_more, e_variable_group, x_actor_variable_group, x_object_variable_group):
    tree_info = state_list[0].get_binding("tree").value[0]
    if not is_future_tense(tree_info): return

    # The only valid scenarios for will have are requests, so ...
    # The planner will only satisfy a want wrt the players
    task = ('satisfy_want',
            variable_group_values_to_list(x_actor_variable_group),
            variable_group_values_to_list(x_object_variable_group),
            min_from_variable_group(x_object_variable_group))
    final_state = do_task(state_list[0].world_state_frame(), [task])
    if final_state:
        yield [final_state]
    else:
        yield []


# Just purely answers questions about having things in the present tense
# like have_v_1, BUT: handles some special cases like "do you have a table?"
# which is really an implied request. See group handler for scenarios.
@Predication(vocabulary, names=["_have_v_1"])
def _have_v_1_present(state, e_introduced_binding, x_actor_binding, x_object_binding):
    if not is_present_tense(state.get_binding("tree").value[0]):
        return
    if is_concept(x_actor_binding):
        return

    def bound(x_actor, x_object):
        # If everything is instances, just answer if x has y
        if not is_concept(x_object):
            return rel_check(state, x_actor, "have", x_object)

        else:
            if x_actor == "restaurant":
                # "Do you (the restaurant) have (the concept of) x?"
                # Let the group handler perform the implied request action
                # or just answer the question, as long as we do have it
                return rel_check(state, x_actor, "have", x_object.concept_name)

        report_error(["verbDoesntApply", convert_to_english(state, x_actor), "have", convert_to_english(state, x_object), state.get_reprompt()])
        return False

    def actor_from_object(x_object):
        for i in rel_subjects(state, "have", object_to_store(x_object)):
            found = True
            yield store_to_object(state, i)

        if not found:
            report_error(["Nothing_VTRANS_X", "have", x_object, state.get_reprompt()])

    def object_from_actor(x_actor):
        found = False
        for i in rel_objects(state, x_actor, "have"):
            found = True
            yield store_to_object(state, i)

        if not found:
            report_error(["X_VTRANS_Nothing", "have", convert_to_english(state, x_actor), state.get_reprompt()])

    yield from in_style_predication_2(state, x_actor_binding, x_object_binding, bound, actor_from_object,
                                      object_from_actor)


# Scenarios:
# - "Do you have a table?" --> implied table request
# - "what do you have?" --> implied menu request
# - "Do you have a/the menu?" --> implied menu request
# - "Do you have a/the bill?" --> implied bill request
# - "what specials do you have?" --> implied request for description of specials
#   "do I/we have x?" --> ask about the state of the world
# - "Do you have the table?" --> Should fail due to "the table" since there is neither 1 table, nor one conceptual table in scope
# - "Do you have a/the steak?" --> just asking about the steak, no implied request
# - "Do you have a bill?" --> just asking about the bill, no implied request
# - "Do you have menus?" --> Could mean "do you have conceptual menus?" or "implied menu request and thus instance check"
# - "Do you have steaks?" --> Could mean "do you have more than one preparation of steak" or "Do you have more than one instance of a steak"
@Predication(vocabulary, names=["solution_group__have_v_1"])
def _have_v_1_present_group(state_list, has_more, e_list, x_act_list, x_obj_list):
    # Ignore this group if it isn't present tense
    tree_info = state_list[0].get_binding("tree").value[0]
    if not is_present_tense(tree_info):
        return

    # The solution predication guarantees that this is either actor and object instances or
    # actor instance and object concept. We only have to check one solution since they will all be the same
    first_x_obj = x_obj_list.solution_values[0].value[0]
    object_concepts = is_concept(first_x_obj)

    if not object_concepts:
        # This is a "x has y" type statement with instances and these have already been checked
        yield state_list
        return

    else:
        # Since this is a concept, the solution handler already checked that the actor is
        # "restaurant" and that the restaurant "has" the solution group concepts.
        final_states = []
        for solution_index in range(len(state_list)):
            # Deal with the user saying "do you have x and y *together*"
            x_obj_value = x_obj_list.solution_values[solution_index].value
            if len(x_obj_value) > 1:
                report_error(["errorText", "One thing at a time, please!", state_list[solution_index].get_reprompt()], force=True)
                yield []
                return

            # Now we are guaranteed to only have one item
            # wh-questions aren't implied requests.  I.e. "which tables do you have?"
            x_obj = x_obj_value[0]
            wh_variable = is_wh_question(tree_info)
            # Only doing a cursory check to make sure they are talking about things that could
            # be requests in general. More specific things like "a cheap bill" will be figured out
            # in the planner and failed if we can't give it
            if not wh_variable and x_obj.concept_name in ["bill", "table", "menu"]:
                # "Can I have a table/menu/bill?" is really about the instances
                # thus check_concepts=False
                # Fail this group if we don't meet the constraints
                if not check_concept_solution_group_constraints(state_list, x_obj_list, check_concepts=False):
                    yield []
                    return

                # Questions about "Do you have a (concept of a) table/menu/bill?" are really implied requests in a restaurant
                # that mean "Can I have a table/menu/bill?"
                # Note that this is where the concept really gets checked in case they said something like
                # Do you have a *dirty* menu or something...
                task = ('satisfy_want', [("user",)], [(x_obj,)], 1)
                final_state = do_task(state_list[0].world_state_frame(), [task])
                if final_state:
                    final_states.append(final_state)

                else:
                    yield []
                    return

            else:
                # Not an implied request and the solution predication already confirmed
                # that the restaurant has this concept, so: succeed
                final_states.append(state_list[solution_index])

        yield final_states
        return


# Used only when there is a form of have that means "able to"
# The regular predication only checks if x is able to have y
# Scenarios:
#   "What can I have?" --> implied menu request
@Predication(vocabulary, names=["_have_v_1_able", "_get_v_1_able"])
def _have_v_1_able(state, e_introduced_binding, x_actor_binding, x_object_binding):
    def both_bound_prediction_function(x_actors, x_objects):
        # Players are able to have any food, a table or a menu
        if is_user_type(x_actors):
            return valid_player_request(state, x_objects)

        # Food is able to have ingredients, restaurant can have food, etc.
        # Whatever we have modelled
        else:
            store_actors = [object_to_store(x) for x in x_actors]
            store_objects = [object_to_store(x) for x in x_objects]

            for store_actor in store_actors:
                for store_object in store_objects:
                    if not rel_check(state, store_actor, "have", store_object):
                        return False

            return True

    def actor_unbound(x_object):
        if False:
            yield None

    def object_unbound(x_actor):
        # This is a "What can I have?" type question
        # - Conceptually, there are a lot of things the user is able to have: a table, a bill, a menu, a steak, etc.
        #   - But: this isn't really what they are asking. This is something that is a special phrase in the "restaurant frame" which means: "what is on the menu"
        #     - So it is a special case that we interpret as a request for a menu
        if is_user_type(x_actor):
            yield (ESLConcept("menu"),)

    yield from lift_style_predication_2(state, x_actor_binding, x_object_binding,
                                        both_bound_prediction_function,
                                        actor_unbound,
                                        object_unbound)


# The group predication for have_able can also generate an implied request,
# but only if it was a question with a bound actor
#
# Scenarios:
# - "who can have a steak?" -_> you, "there are more"
# - "What can I have?" --> implicit menu request
# - "Can I have a steak and a salad?" --> implicit order request
@Predication(vocabulary, names=["solution_group__have_v_1_able", "solution_group__get_v_1_able"])
def _have_v_1_able_group(state_list, has_more, e_variable_group, x_actor_variable_group, x_object_variable_group):
    # At this point they were *able* to have the item, now we see if this was an implicit request for it
    # If this is a question, but not a wh question, involving the players, then it is also a request for something
    tree_info = state_list[0].get_binding("tree").value[0]
    force = sentence_force(tree_info["Variables"])
    wh_variable = get_wh_question_variable(tree_info)
    if force in ["ques", "prop-or-ques"] and \
        ((wh_variable and x_object_variable_group.solution_values[0].value[0] == ESLConcept("menu")) or \
         not get_wh_question_variable(tree_info)):
        # The planner will only satisfy a want wrt the players
        task = ('satisfy_want', variable_group_values_to_list(x_actor_variable_group), variable_group_values_to_list(x_object_variable_group), min_from_variable_group(x_object_variable_group))
        final_state = do_task(state_list[0].world_state_frame(), [task])
        if final_state:
            yield [final_state]
    else:
        # Not an implicit request
        yield state_list

        if has_more:
            yield True


@Predication(vocabulary, names=["poss"])
def poss(state, e_introduced_binding, x_object_binding, x_actor_binding):
    def bound(x_actor, x_object):
        if (x_actor, x_object) in state.all_rel("have"):
            return True
        else:
            report_error(["verbDoesntApply", x_actor, "have", x_object, state.get_reprompt()])
            return False

    def actor_from_object(x_object):
        for i in state.all_rel("have"):
            if i[1] == x_object:
                yield i[0]

    def object_from_actor(x_actor):
        for i in state.all_rel("have"):
            if i[0] == x_actor:
                yield i[1]

    yield from in_style_predication_2(state, x_actor_binding, x_object_binding, bound, actor_from_object,
                                      object_from_actor)


# Returns:
# the variable to measure into, the units to measure
# or None if not a measurement unbound variable
def measurement_information(x):
    if isinstance(x, Measurement) and isinstance(x.count, str):
        # if x is a Measurement() with a string as a value,
        # then we are being asked to measure x_actor
        measure_into_variable = x.count
        units = x.measurement_type
        if is_referring_expr(units):
            return measure_into_variable, units.referring_expr_name

    return None, None


@Predication(vocabulary, names=["_be_v_id"])
def _be_v_id(state, e_introduced_binding, x_actor_binding, x_object_binding):
    def criteria_bound(x_actor, x_object):
        measure_into_variable, units = measurement_information(x_object)
        if measure_into_variable is not None:
            return True

        else:
            first_in_second = x_actor in all_instances_and_spec(state, x_object)
            second_in_first = x_object in all_instances_and_spec(state, x_actor)
            if first_in_second or second_in_first:
                return True
            else:
                report_error(["is_not", convert_to_english(state,x_actor), convert_to_english(state,x_object), state.get_reprompt()])

    def unbound(x_object):
        if is_concept(x_object):
            yield from x_object.instances(state)
            yield from x_object.concepts(state)

    for success_state in in_style_predication_2(state, x_actor_binding, x_object_binding, criteria_bound, unbound,
                                                unbound):
        x_object_value = success_state.get_binding(x_object_binding.variable.name).value[0]
        x_actor_value = success_state.get_binding(x_actor_binding.variable.name).value[0]
        measure_into_variable, units = measurement_information(x_object_value)
        if measure_into_variable is not None:
            # This is a "how much is x" question and we need to measure the value
            # into the specified variable
            concept_item = instance_of_or_concept_name(state, x_actor_value)
            if units in ["generic_entity", "dollar"]:
                if concept_item in state.sys["prices"]:
                    price = Measurement("dollar", state.sys["prices"][concept_item])
                    # Remember that we now know the price
                    yield success_state.set_x(measure_into_variable, (price,)). \
                        record_operations([SetKnownPriceOp(concept_item)])
                elif concept_item == "bill":
                    total = list(rel_objects(state, "bill1", "valueOf"))
                    if len(total) == 0:
                        total.append(0)
                    price = Measurement("dollar", total[0])
                    yield success_state.set_x(measure_into_variable, (price,))

                else:
                    yield success_state.record_operations([RespondOperation("Haha, it's not for sale.")])
                    return False

        else:
            yield success_state


@Predication(vocabulary, names=["solution_group__be_v_id"])
def _be_v_id_group(state_list, has_more, e_introduced_binding_list, x_obj1_variable_group, x_obj2_variable_group):
    yield state_list


@Predication(vocabulary, names=["_cost_v_1"])
def _cost_v_1(state, e_introduced_binding, x_actor_binding, x_object_binding):
    def criteria_bound(x_actor, x_object):
        if not isinstance(x_object, Measurement):
            report_error(["Have not dealt with declarative cost", state.get_reprompt()])
            yield False

        else:
            yield True  # will need to implement checking for price correctness in the future if user says "the soup costs one steak"

            '''
            x_object = json.loads(x_object)
            if x_object["structure"] == "price_type":
                if type(x_object["relevant_var_value"]) is int:
                    if not (instance_of_what(state, x_act), x_object["relevant_var_value"]) in state.sys["prices"]:
                        report_error("WrongPrice")
                        return False
            return True
            '''

    def get_actor(x_object):
        if False:
            yield None

    def get_object(x_actor):
        if is_concept(x_actor):
            # Make sure it is something that is actually in the world
            # by evaluating it to make sure there are instances
            if len(x_actor.instances(state)) == 0:
                return

        concept_item = instance_of_or_concept_name(state, x_actor)
        if concept_item in state.sys["prices"].keys():
            yield concept_item + " : " + str(state.sys["prices"][concept_item]) + " dollars"
        else:
            yield "Ah. It's not for sale."

    for success_state in in_style_predication_2(state, x_actor_binding, x_object_binding, criteria_bound, get_actor,
                                                get_object):
        x_object_value = success_state.get_binding(x_object_binding.variable.name).value[0]
        x_actor_value = success_state.get_binding(x_actor_binding.variable.name).value[0]
        measure_into_variable, units = measurement_information(x_object_value)
        if measure_into_variable is not None:
            # This is a "how much is x" question and we need to measure the value
            # into the specified variable
            concept_item = instance_of_or_concept_name(state, x_actor_value)
            if units in ["generic_entity", "dollar"]:
                if concept_item in state.sys["prices"]:
                    price = Measurement("dollar", state.sys["prices"][concept_item])
                    # Remember that we now know the price
                    yield success_state.set_x(measure_into_variable, (price,)). \
                        record_operations([SetKnownPriceOp(concept_item)])
                elif concept_item == "bill":
                    total = list(rel_objects(state, "bill1", "valueOf"))
                    if len(total) == 0:
                        total.append(0)
                    price = Measurement("dollar", total[0])
                    yield success_state.set_x(measure_into_variable, (price,))

                else:
                    yield success_state.record_operations([RespondOperation("Haha, it's not for sale.")])
                    return False

        else:
            yield success_state


@Predication(vocabulary, names=["solution_group__cost_v_1"])
def _cost_v_1_group(state_list, has_more, e_introduced_binding_list, x_act_variable_group, x_obj2_variable_group):
    if is_referring_expr(x_act_variable_group.solution_values[0].value[0]):
        if not check_concept_solution_group_constraints(state_list, x_act_variable_group, check_concepts=True):
            yield []
            return
    yield state_list


@Predication(vocabulary, names=["_be_v_there"])
def _be_v_there(state, e_introduced_binding, x_object_binding):
    def bound_variable(value):
        yield value in state.get_entities()

    def unbound_variable():
        for i in state.get_entities():
            yield i

    yield from combinatorial_predication_1(state, x_object_binding, bound_variable, unbound_variable)


# This needs to be rewritten given the conceptual changes we've made
# @Predication(vocabulary, names=["compound"])
# def compound(state, e_introduced_binding, x_first_binding, x_second_binding):
#     assert (x_first_binding is not None)
#     assert (x_second_binding is not None)
#     if x_second_binding.value[0] == concept_from_lemma("tomato"):
#         yield state
#     else:
#         yield state.set_x(x_first_binding.variable.name, (state.get_binding(x_first_binding.variable.name).value[0] + ", " +
#                                                       state.get_binding(x_second_binding.variable.name).value[0],))

# This needs to be rewritten to actually do something
# @Predication(vocabulary, names=["_green_a_2"])
# def compound(state, e_introduced_binding, x_first_binding):
#     yield state

def computer_in_state(state):
    for i in state.variables:
        if i.value == ("restaurant",):
            return True
    return False


# Any successful solution group that is a wh_question will call this
@Predication(vocabulary, names=["solution_group_wh"])
def wh_question(state_list, has_more, binding_list):
    current_state = do_task(state_list[0].world_state_frame(), [('describe', [x.value for x in binding_list])])
    if current_state is not None:
        yield (current_state,)
    else:
        yield state_list


# Generates all the responses that predications can
# return when an error occurs
def generate_custom_message(tree_info, error_term):
    # error_term is of the form: [index, error] where "error" is another
    # list like: ["name", arg1, arg2, ...]. The first item is the error
    # constant (i.e. its name). What the args mean depends on the error
    error_predicate_index = error_term[0]
    error_arguments = error_term[1]
    error_constant = error_arguments[0] if error_arguments is not None else "no error set"

    # See if the system can handle converting the error
    # to a message first except for those we are overriding

    # Override these
    if error_constant == "doesntExist":
        arg1 = error_arguments[1]
        return s("Host: There isn't such {a arg1:sg} here", tree_info)

    else:
        system_message = perplexity.messages.generate_message(tree_info, error_term)
        if system_message is not None:
            return system_message

    # if error_constant == "conceptNotFound":

    if error_constant == "dontKnowHow":
        return "I don't know how to do that."
    if error_constant == "notAThing":
        arg1 = error_arguments[1]
        # english_for_delphin_variable() converts a variable name like 'x3' into the english words
        # that it represented in the MRS
        arg2 = english_for_delphin_variable(error_predicate_index, error_arguments[2], tree_info)
        arg3 = error_arguments[3]
        return f"{arg1} is not {arg2}{arg3}"
    if error_constant == "X_VTRANS_Nothing":
        return "Nothing." + error_arguments[3]
    if error_constant == "not_adj":
        return "It's not " + error_arguments[1] + "." + error_arguments[2]
    if error_constant == "is_not":
        return f"{error_arguments[1]} is not {error_arguments[2]}{error_arguments[3]}"
    if error_constant == "notOn":
        arg1 = error_arguments[1]
        arg2 = error_arguments[2]
        arg3 = error_arguments[3]
        return f"No. {arg1} is not on {arg2}{arg3}"
    if error_constant == "verbDoesntApplyArg":
        arg1 = error_arguments[1]
        arg2 = error_arguments[2]
        arg3 = error_arguments[3]
        arg4 = error_arguments[4]
        return s("No, {arg1} {'did':<arg1} not {*arg2} {arg3} {*arg4}", tree_info, reverse_pronouns=True)
    if error_constant == "verbDoesntApply":
        return f"No. {error_arguments[1]} does not {error_arguments[2]} {error_arguments[3]} {error_arguments[4]}"
    else:
        # No custom message, just return the raw error for debugging
        return str(error_term)


def reset():
    # return State([])
    # initial_state = WorldState({}, ["pizza", "restaurant", "salad", "soup", "steak", "ham", "meat","special"])
    initial_state = WorldState({},
                               {"prices": {"salad": 3, "steak": 10, "soup": 4, "salmon": 12,
                                           "chicken": 7, "pork": 8},
                                "responseState": "initial"
                                })

    initial_state = initial_state.add_rel("bill_type", "specializes", "thing")
    initial_state = initial_state.add_rel("bill", "specializes", "bill_type")
    initial_state = initial_state.add_rel("check", "specializes", "bill_type")
    initial_state = initial_state.add_rel("kitchen", "specializes", "thing")
    # The restaurant has the concepts of the items so it can answer "do you have x?"
    initial_state = initial_state.add_rel("restaurant", "have", "kitchen")

    initial_state = initial_state.add_rel("table", "specializes", "thing")
    # The restaurant has the concepts of the items so it can answer "do you have x?"
    initial_state = initial_state.add_rel("restaurant", "have", "table")

    initial_state = initial_state.add_rel("menu", "specializes", "thing")
    # The restaurant has the concepts of the items so it can answer "do you have x?"
    initial_state = initial_state.add_rel("restaurant", "have", "menu")
    initial_state = initial_state.add_rel("restaurant", "instanceOf", "thing")

    initial_state = initial_state.add_rel("person", "specializes", "thing")
    initial_state = initial_state.add_rel("son", "specializes", "person")

    initial_state = initial_state.add_rel("food", "specializes", "thing")
    initial_state = initial_state.add_rel("dish", "specializes", "food")
    initial_state = initial_state.add_rel("meat", "specializes", "dish")
    initial_state = initial_state.add_rel("veggie", "specializes", "dish")
    initial_state = initial_state.add_rel("special", "specializes", "dish")

    initial_state = initial_state.add_rel("steak", "specializes", "meat")
    initial_state = initial_state.add_rel("chicken", "specializes", "meat")
    initial_state = initial_state.add_rel("salmon", "specializes", "meat")
    initial_state = initial_state.add_rel("pork", "specializes", "meat")

    initial_state = initial_state.add_rel("soup", "specializes", "veggie")
    initial_state = initial_state.add_rel("salad", "specializes", "veggie")

    # These concepts are "in scope" meaning it is OK to say "the X"
    initial_state = initial_state.add_rel("special", "conceptInScope", "true")

    # These concepts are only in scope in the table frame
    initial_state = initial_state.add_rel("menu", "conceptInScope", "true")
    initial_state = initial_state.add_rel("bill", "conceptInScope", "true")
    initial_state = initial_state.add_rel("check", "conceptInScope", "true")

    # The restaurant has the concepts of the items so it can answer "do you have steak?"
    initial_state = initial_state.add_rel("restaurant", "have", "menu")
    initial_state = initial_state.add_rel("restaurant", "have", "food")
    initial_state = initial_state.add_rel("restaurant", "have", "dish")
    initial_state = initial_state.add_rel("restaurant", "have", "meat")
    initial_state = initial_state.add_rel("restaurant", "have", "veggie")
    initial_state = initial_state.add_rel("restaurant", "have", "bill1")
    initial_state = initial_state.add_rel("restaurant", "describes", "menu")
    initial_state = initial_state.add_rel("restaurant", "describes", "bill")
    initial_state = initial_state.add_rel("restaurant", "have", "bill")
    initial_state = initial_state.add_rel("restaurant", "describes", "table")

    # Instances below here
    # Location and "in scope" are modeled as who "has" a thing
    # If user or son has it, it is "in scope"
    # otherwise it is not
    initial_state = initial_state.add_rel("kitchen1", "instanceOf", "kitchen")

    initial_state = initial_state.add_rel("table1", "instanceOf", "table")
    initial_state = initial_state.add_rel("table1", "maxCapacity", 2)
    initial_state = initial_state.add_rel("table2", "instanceOf", "table")
    initial_state = initial_state.add_rel("table2", "maxCapacity", 2)
    initial_state = initial_state.add_rel("table3", "instanceOf", "table")
    initial_state = initial_state.add_rel("table3", "maxCapacity", 1)

    initial_state = initial_state.add_rel("menu1", "instanceOf", "menu")
    initial_state = initial_state.add_rel("menu2", "instanceOf", "menu")
    initial_state = initial_state.add_rel("menu3", "instanceOf", "menu")

    menu_types = [ "salmon", "steak", "chicken"]
    special_types = ["soup", "salad", "pork"]
    dish_types = menu_types + special_types
    for dish_type in dish_types:
        # The restaurant has the concepts of the items so it can answer "do you have steak?"
        initial_state = initial_state.add_rel("restaurant", "have", dish_type)
        initial_state = initial_state.add_rel("restaurant", "describes", dish_type)

        # These concepts are "in scope" meaning it is OK to say "the X"
        initial_state = initial_state.add_rel(dish_type, "conceptInScope", "true")

        if dish_type in menu_types:
            initial_state = initial_state.add_rel(dish_type, "on", "menu")
        else:
            initial_state = initial_state.add_rel(dish_type, "priceUnknownTo", "user")
            initial_state = initial_state.add_rel(dish_type, "specializes", "special")

        # Create the food instances
        for i in range(2):
            # Create an instance of this food
            food_instance = dish_type + str(i)
            initial_state = initial_state.add_rel(food_instance, "instanceOf", dish_type)

            # The kitchen is where all the food is
            initial_state = initial_state.add_rel("kitchen1", "contain", food_instance)
            if dish_type == "chicken":
                initial_state = initial_state.add_rel(food_instance, "isAdj", "roasted")
            if dish_type == "salmon":
                initial_state = initial_state.add_rel(food_instance, "isAdj", "grilled")
            if dish_type == "pork":
                initial_state = initial_state.add_rel(food_instance, "isAdj", "smoked")

    initial_state = initial_state.add_rel("restaurant", "have", "special")
    initial_state = initial_state.add_rel("restaurant", "hasName", "restaurant")
    initial_state = initial_state.add_rel("bill1", "instanceOf", "bill")
    initial_state = initial_state.add_rel("bill1", "instanceOf", "check")
    initial_state = initial_state.add_rel(0, "valueOf", "bill1")
    initial_state = initial_state.add_rel("room", "contains", "user")

    initial_state = initial_state.add_rel("son1", "instanceOf", "son")
    initial_state = initial_state.add_rel("son1", "hasName", "your son")
    initial_state = initial_state.add_rel("user", "instanceOf", "person")
    initial_state = initial_state.add_rel("user", "hasName", "you")
    initial_state = initial_state.add_rel("user", "have", "son1")
    initial_state = initial_state.add_rel("user", "heardSpecials", "false")

    initial_state = initial_state.add_rel("chicken", "isAdj", "roasted")
    initial_state = initial_state.add_rel("salmon", "isAdj", "grilled")
    initial_state = initial_state.add_rel("pork", "isAdj", "smoked")

    return initial_state


def error_priority(error_string):
    system_priority = perplexity.messages.error_priority(error_string)
    if system_priority is not None:
        return system_priority
    else:
        # Must be a message from our code
        error_constant = error_string[1][0]
        return error_priority_dict.get(error_constant, error_priority_dict["defaultPriority"])


error_priority_dict = {
    "defaultPriority": 1000
}


def hello_world():
    user_interface = UserInterface(reset, vocabulary, message_function=generate_custom_message,
                                   error_priority_function=error_priority, scope_function=in_scope,
                                   scope_init_function=in_scope_initialize)

    while True:
        user_interface.interact_once()
        print()


if __name__ == '__main__':
    # ShowLogging("Execution")
    # ShowLogging("Generation")
    # ShowLogging("UserInterface")
    ShowLogging("Pipeline")
    # ShowLogging("SString")
    # ShowLogging("Determiners")
    # ShowLogging("SolutionGroups")

    print("You’re going to a restaurant with your son, Johnny, who is vegetarian and too scared to order by himself. Get a table and buy lunch for both of you. You have 15 dollars in cash.\nHost: Hello! How can I help you today?")
    # ShowLogging("Pipeline")
    # ShowLogging("Transformer")
    hello_world()
