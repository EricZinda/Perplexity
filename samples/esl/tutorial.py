import os
import perplexity.messages
from perplexity.state import LoadException
from samples.esl.esl_planner import do_task
from samples.esl.esl_planner_description import convert_to_english, convert_to_english_list
from perplexity.plurals import VariableCriteria, GlobalCriteria, NegatedPredication
from perplexity.predications import combinatorial_predication_1, in_style_predication_2, \
    lift_style_predication_2, concept_meets_constraint
from perplexity.set_utilities import Measurement
from perplexity.solution_groups import declared_determiner_infos, optimize_determiner_infos, \
    create_group_variable_values
from perplexity.system_vocabulary import system_vocabulary, quantifier_raw
from perplexity.transformer import TransformerMatch, TransformerProduction, PropertyTransformerMatch, \
    PropertyTransformerProduction, ConjunctionMatchTransformer, ConjunctionProduction
from perplexity.tree import find_predication_from_introduced, get_wh_question_variable, \
    gather_scoped_variables_from_tree_at_index, TreePredication, used_predicatively
from perplexity.user_interface import UserInterface
from perplexity.utilities import ShowLogging, sentence_force, parse_predication_name
from perplexity.variable_binding import VariableBinding, VariableData
from perplexity.vocabulary import Predication, EventOption, Transform, ValueSize
from samples.esl.worldstate import *
import logging
import perplexity.OpenAI


vocabulary = system_vocabulary()


# ******** Helpers ************
def count_of_instances_and_concepts(context, state, variable, concepts_original, fail_if_no_instances):
    concepts = concepts_original
    concept_count = len(concepts)

    instances = []
    for concept in concepts:
        this_concept_instances = list(concept.instances(context, state))
        # If we are dealing with instances and one of the concepts generates zero, we don't want to just count the others
        # and succeed.  I.e. I have two ice creams and bowls should not succeed if there are no bowls
        if fail_if_no_instances and len(this_concept_instances) == 0:
            concept_english = concept.render_english()
            if "something" not in concept_english:
                # If we can render this concept as a real word (not just "something"), ask
                # chatgpt if it is food
                request_info = perplexity.OpenAI.StartOpenAIBooleanRequest("test",
                                                         "is_food_or_drink_predication",
                                                         f"Is {concept_english} either a food or a drink?")
                result = perplexity.OpenAI.CompleteOpenAIRequest(request_info, wait=5)
                if result == "true":
                    # It is, so report a nicer error than "I don't know that word"
                    context.report_error(["dontHaveThatFood", variable], force=True, phase=2)

                else:
                    # It is not. If it is a word we actually know, report a special error for that.
                    # Otherwise just say we don't know it
                    noun_predication = find_predication_from_introduced(state.get_binding("tree").value[0]["Tree"], variable)
                    parsed_name = parse_predication_name(noun_predication.name)

                    if understood_noun(state, parsed_name["Lemma"]):
                        context.report_error(["noInstancesOfConcept", variable], force=True, phase=2)

                    else:
                        # This is a word that we legitimately don't know
                        context.report_error(["unknownWords", [(noun_predication.name, None, None, False, parsed_name['Lemma'])]],
                                             force=True, phase=2)

            return None

        instances += this_concept_instances
    instance_count = len(instances)

    scope_data = in_scope_initialize(state)
    instance_in_scope_count = 0
    for instance in instances:
        if in_scope(scope_data, context, state, instance):
            instance_in_scope_count += 1

    concept_in_scope_count = 0
    for concept in concepts:
        if in_scope(scope_data, context, state, concept):
            concept_in_scope_count += 1

    return concept_count, concept_in_scope_count, instance_count, instance_in_scope_count


def variable_group_values_to_list(variable_group):
    return [binding.value for binding in variable_group.solution_values]


def check_concept_solution_group_constraints(context, state_list, x_what_variable_group, check_concepts):
    # These are concepts. Only need to check the first because:
    # If one item in the group is a concept, they all are
    assert x_what_variable_group.solution_values[0].value is not None, "variable_group is unbound, and thus not a concept, probably because it is scoped under negation"
    assert is_concept(x_what_variable_group.solution_values[0].value[0])
    x_what_variable = x_what_variable_group.solution_values[0].variable.name

    # First we need to check to make sure that the specific concepts in the solution group like "steak", "menu",
    # etc meet the requirements I.e. if there are two preparations of steak on the menu and you say
    # "I'll have the steak" you should get an error
    x_what_values = [x.value for x in x_what_variable_group.solution_values]
    x_what_individuals_set = set()
    for value in x_what_values:
        x_what_individuals_set.update(value)
    counts = count_of_instances_and_concepts(context, state_list[0], x_what_variable, list(x_what_individuals_set), not check_concepts)
    if counts is None:
        return False
    else:
        concept_count, concept_in_scope_count, instance_count, instance_in_scope_count = counts
        success = concept_meets_constraint(context,
                                            state_list[0].get_binding("tree").value[0],
                                            x_what_variable_group.variable_constraints,
                                            concept_count,
                                            concept_in_scope_count,
                                            instance_count,
                                            check_concepts,
                                            variable=x_what_variable)
        if not success:
            pipeline_logger.debug(f"check_concept_solution_group_constraints failed: {context.error()}")

        return success

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


# It is a valid request if we *have* such a thing and if it entails the list
# of valid_concepts
def valid_player_request(context, state, x_objects, valid_concepts=None):
    # Things players can request
    if valid_concepts is None:
        valid_concepts = [ESLConcept("food"),
                          ESLConcept("drink"),
                          ESLConcept("table"),
                          ESLConcept("menu"),
                          ESLConcept("bill"),
                          ESLConcept("dish"),
                          ESLConcept("check")]

    for x_object in x_objects:
        if is_concept(x_object) and len(x_object.instances(context, state)) == 0:
            return False

        found = False
        for valid_concept in valid_concepts:
            if instance_of_or_entails(context, state, x_object, valid_concept):
                found = True
                break
        if not found:
            return False

    return True


def min_from_variable_group(variable_group):
    return variable_group.variable_constraints.min_size if variable_group.variable_constraints is not None else 1


def max_from_variable_group(variable_group):
    return variable_group.variable_constraints.max_size if variable_group.variable_constraints is not None else float('inf')


# **** Transforms ****

# Ready to pay/pay the bill --> _pay_v_for_request
#
#                ┌────── pron(x3)
# pronoun_q(x3,RSTR,BODY)                   ┌─ _pay_v_for(e10,x3,i11,i12)
#                     └─ _ready_a_1(e2,x3,ARG2)
#
# Text Tree: pronoun_q(x3,pron(x3),_ready_a_1(e2,x3,_pay_v_for(e10,x3,i11,i12)))
#
#              ┌────── _bill_n_of(x12,i17)
# _the_q(x12,RSTR,BODY)               ┌────── pron(x3)
#                   └─ pronoun_q(x3,RSTR,BODY)                   ┌─ _pay_v_for(e10,x3,i11,x12)
#                                          └─ _ready_a_1(e2,x3,ARG2)
#
# Text Tree: _the_q(x12,_bill_n_of(x12,i17),pronoun_q(x3,pron(x3),_ready_a_1(e2,x3,_pay_v_for(e10,x3,i11,x12))))
#
@Transform(vocabulary)
def ready_to_pay_to_pay_for_transformer():
    # production = TransformerProduction(name="$|name|_able", args={"ARG0": "$e1", "ARG1": "$x1"})
    # production_event_replace = TransformerProduction(name="event_replace", args={"ARG0": "u99", "ARG1": "$e1", "ARG2": "$target_e"})
    # conjuct_production = ConjunctionProduction(conjunction_list=["$extra_conjuncts", production_event_replace, production])


    production_verb = TransformerProduction(name="$name", args={"ARG0": "$e_target"}, args_rest="$verb_rest_args")
    production = TransformerProduction(name="_want_v_1", args={"ARG0": "$e_ready", "ARG1": "$x_actor", "ARG2": production_verb})

    # target_predication = TransformerMatch(name_pattern="", name_capture="name", args_pattern=["e", "x"], args_capture=["target_e", "x1"])
    # target = ConjunctionMatchTransformer([target_predication], extra_conjuncts_capture="extra_conjuncts")
    target = TransformerMatch(name_pattern="*", name_capture="name", args_pattern=["e", "**"],
                              args_capture=["e_target"],
                              args_rest_capture="verb_rest_args")

    return TransformerMatch(name_pattern="_ready_a_1",
                            args_pattern=["e", "x", target],
                            args_capture=["e_ready", "x_actor", None],
                            removed=["_ready_a_1"],
                            production=production)


# Ready for x --> want x
#           ┌────── _table_n_1(x9)
# _a_q(x9,RSTR,BODY)               ┌────── pron(x3)
#                └─ pronoun_q(x3,RSTR,BODY)    ┌── _for_p(e8,e2,x9)
#                                       └─ and(0,1)
#                                                └ _ready_a_1(e2,x3)
@Transform(vocabulary)
def ready_for_to_want_transformer():
    production_want_verb = TransformerProduction(name="_want_v_1", args={"ARG0": "$e_original", "ARG1": "$x_actor", "ARG2": "$x_target"})
    conjuct_production = ConjunctionProduction(conjunction_list=[production_want_verb, "$extra_conjuncts"])
    quantifier_production = TransformerProduction(name="$quantifier_name", args={"ARG0": "$x_quantifier", "ARG1": "$rstr_quantifier", "ARG2": conjuct_production})

    target_ready_predication = TransformerMatch(name_pattern="_ready_a_1", args_pattern=["e", "x"], args_capture=["e_original", "x_actor"])
    target_for_predication = TransformerMatch(name_pattern="_for_p", args_pattern=["e", "e", "x"], args_capture=[None, None, "x_target"])
    target_conjunction = ConjunctionMatchTransformer([target_for_predication, target_ready_predication],
                                                     extra_conjuncts_capture="extra_conjuncts")

    return TransformerMatch(name_pattern="*",
                             name_capture="quantifier_name",
                             args_pattern=["x", "h", target_conjunction],
                             args_capture=["x_quantifier", "rstr_quantifier", None],
                             removed=["_ready_a_1", "_for_p"],
                             production=quantifier_production)


# Convert "and <phrase>?" to "<phrase>"
# as in "and I'll take the steak"
@Transform(vocabulary)
def and_with_single_phrase_transformer():
    target_and_predication = TransformerMatch(name_pattern="_and_c", args_pattern=["e", "u", "e"], args_capture=["e_original", None, "e_target"])
    target_verb_predication = TransformerMatch(name_pattern="*", name_capture="verb_name", args_pattern=["e", "**"], args_capture=["e_verb"], args_rest_capture="verb_rest_args")
    target_conjunction = ConjunctionMatchTransformer([target_and_predication, target_verb_predication], extra_conjuncts_capture="extra_conjuncts")

    production_event_replace = TransformerProduction(name="event_replace", args={"ARG0": "u99", "ARG1": "$e_target", "ARG2": "$e_original"})
    production_other_verb = TransformerProduction(name="$verb_name", args={"ARG0": "$e_verb"}, args_rest="$verb_rest_args")
    conjuct_production = ConjunctionProduction(conjunction_list=[production_event_replace, production_other_verb, "$extra_conjuncts"])
    quantifier_production = TransformerProduction(name="$quantifier_name", args={"ARG0": "$x_quantifier", "ARG1": "$rstr_quantifier", "ARG2": conjuct_production})

    return TransformerMatch(name_pattern="*",
                             name_capture="quantifier_name",
                             args_pattern=["x", "h", target_conjunction],
                             args_capture=["x_quantifier", "rstr_quantifier", None],
                             removed=["_and_c"],
                             new_index="$e_verb",
                             production=quantifier_production)



# thats it.
# - pronoun_q(x8,pron(x8),_that_q_dem(x3,generic_entity(x3),_be_v_id(e2,x3,x8)))
# - pronoun_q(x8,pron(x8),_that_q_dem(x3,generic_entity(x3),def_implicit_q(x14,[time_n(x14), _now_a_1(e19,x14)],[_for_p(e13,e2,x14), _be_v_id(e2,x3,x8)])))
@Transform(vocabulary)
def thats_it_transformer():
    no_standalone_production = TransformerProduction(name="no_standalone", args={"ARG0": "$target_e"})
    conjunction_production = ConjunctionProduction(conjunction_list=[no_standalone_production])

    be_exx_match = TransformerMatch(name_pattern="_be_v_id",
                                    args_pattern=["e", "x", "x"],
                                    args_capture=["target_e", None, None])
    conjunction_be_match = ConjunctionMatchTransformer(transformer_list=[be_exx_match], extra_conjuncts_capture="$extra_conjuncts")

    generic_entity_match = TransformerMatch(name_pattern="generic_entity",
                                   args_pattern=["x"])

    return TransformerMatch(name_pattern="_that_q_dem",
                            args_pattern=["x", generic_entity_match, conjunction_be_match],
                            removed=["_be_v_id", "_that_q_dem"],
                            production=conjunction_production)


#                           │                                                   ┌── generic_entity(x8)
#                           │                                       ┌────── and(0,1)
#                           │                   ┌────── generic_enti│y(x3)        │
#                           │                   │                   │             └ _for_p(e13,x8,x14)
#                           └─ _that_q_dem(x3,RSTR,BODY)            │
#                                                    └─ _all_q(x8,RSTR,BODY)
#                                                                        └─ _be_v_id(e2,x3,x8)
# Convert "That's all for now"/ to "no"
# Transform: def_implicit_q(x14,[time_n(x14), _now_a_1(e19,x14)],_that_q_dem(x3,generic_entity(x3),_all_q(x8,[generic_entity(x8), _for_p(e13,x8,x14)],_be_v_id(e2,x3,x8))))
# to: _no_a(e, x)
@Transform(vocabulary)
def that_will_be_all_now_transformer():
    no_standalone_production = TransformerProduction(name="no_standalone", args={"ARG0": "$target_e"})
    conjunction_production = ConjunctionProduction(conjunction_list=[no_standalone_production])

    be_exx_match = TransformerMatch(name_pattern="_be_v_id",
                                    args_pattern=["e", "x", "x"],
                                    args_capture=["target_e", None, None])
    conjunction_be_match = ConjunctionMatchTransformer(transformer_list=[be_exx_match], extra_conjuncts_capture="$extra_conjuncts")
    generic_entity_match_2 = TransformerMatch(name_pattern="generic_entity",
                                   args_pattern=["x"])
    conjunction_generic_entity_match = ConjunctionMatchTransformer(transformer_list=[generic_entity_match_2], extra_conjuncts_capture="$extra_conjuncts2")
    all_match = TransformerMatch(name_pattern="_all_q",
                     args_pattern=["x", conjunction_generic_entity_match, conjunction_be_match],
                     removed=["_be_v_id"])

    generic_entity_match = TransformerMatch(name_pattern="generic_entity",
                                   args_pattern=["x"])

    all_match = TransformerMatch(name_pattern="_that_q_dem",
                     args_pattern=["x", generic_entity_match, all_match],
                     removed=["_be_v_id", "_that_q_dem", "_all_q"],
                     production=conjunction_production)

    return all_match

# Convert "That will be all"/ to "no"
# Transform: _all_q(x9,generic_entity(x9),udef_q(x5,generic_entity(x5),_be_v_id(e2,x5,x9)))
# to: _no_a(e, x)
@Transform(vocabulary)
def that_will_be_all_transformer():
    no_standalone_production = TransformerProduction(name="no_standalone", args={"ARG0": "$target_e"})
    conjunction_production = ConjunctionProduction(conjunction_list=[no_standalone_production, "$extra_conjuncts"])

    be_exx_match = TransformerMatch(name_pattern="_be_v_id",
                                    args_pattern=["e", "x", "x"],
                                    args_capture=["target_e", None, None])
    conjunction_match = ConjunctionMatchTransformer(transformer_list=[be_exx_match], extra_conjuncts_capture="extra_conjuncts")
    generic_entity_match_2 = TransformerMatch(name_pattern="generic_entity",
                                   args_pattern=["x"])
    udef_match = TransformerMatch(name_pattern="udef_q",
                     args_pattern=["x", generic_entity_match_2, conjunction_match],
                     removed=["_be_v_id"])

    generic_entity_match = TransformerMatch(name_pattern="generic_entity",
                                   args_pattern=["x"])

    all_match = TransformerMatch(name_pattern="_all_q",
                     args_pattern=["x", generic_entity_match, udef_match],
                     removed=["_be_v_id"],
                     production=conjunction_production)

    return all_match


# Transform discourse(i2,greet(X,i6),Y) to Y
@Transform(vocabulary)
def discourse_transformer():
    production = TransformerProduction(name="$target_name", args={"ARG0": "$target_e"}, args_rest="$target_rest_args")
    conjunction_production = ConjunctionProduction(conjunction_list=["$extra_conjuncts", production])

    # Be sure to only match the verbs as the target
    target_match = TransformerMatch(name_pattern=["regex:_v_", "_please_a_1", "unknown"],
                                    name_capture="target_name",
                                    args_pattern=["*", "**"],
                                    args_capture=["target_e"],
                                    args_rest_capture="target_rest_args")
    conjunction_match = ConjunctionMatchTransformer(transformer_list=[target_match], extra_conjuncts_capture="extra_conjuncts")
    greet_match = TransformerMatch(name_pattern="greet",
                                   args_pattern=["c", "i"])
    return TransformerMatch(name_pattern="discourse",
                            args_pattern=["i", greet_match, conjunction_match],
                            args_capture=[None, None, "target_predication"],
                            removed=["discourse", "greet"],
                            production=conjunction_production,
                            new_index="$target_e")


# ******** Transforms "lets go with" to "I want" ************
# Convert:
#            ┌────── _steak_n_1(x10)
# _a_q(x10,RSTR,BODY)               ┌────── pron(x5)
#                 └─ pronoun_q(x5,RSTR,BODY)    ┌── _with_p(e9,e2,x10)
#                                        └─ and(0,1)
#                                                 └ _go_v_1(e2,x5)
#
# To:
#            ┌────── _steak_n_1(x10)
# _a_q(x10,RSTR,BODY)               ┌────── pron(x5)
#                 └─ pronoun_q(x5,RSTR,BODY)
#                                        └─ _want_v_1(e2, x5, x10)
# Change SF:comm to SF:prop
@Transform(vocabulary)
def lets_go_with_to_want():
    want_production = TransformerProduction(name="_want_v_1", args={"ARG0": "$verb_event", "ARG1": "$who", "ARG2": "$what"})
    conjunction_production = ConjunctionProduction(conjunction_list=["$extra_conjuncts", want_production])
    quantifier_production = TransformerProduction(name="pronoun_q", args={"ARG0": "$quantifier_var", "ARG1": "$quantifier_rstr", "ARG2": conjunction_production})
    sf_production = PropertyTransformerProduction({"$verb_event": {"SF": "prop"},
                                                   "$who": {"NUM": "sg"}})

    with_p_match = TransformerMatch(name_pattern="_with_p", args_pattern=["e", "e", "x"], args_capture=[None, None, "what"])
    go_match = TransformerMatch(name_pattern="_go_v_1", args_pattern=["e", "x"], args_capture=["verb_event", "who"])
    conjunction_match = ConjunctionMatchTransformer(transformer_list=[with_p_match, go_match], extra_conjuncts_capture="extra_conjuncts")
    property_match = PropertyTransformerMatch({"$verb_event": {"SF": "comm"},
                                               "$who": {"PERS": "1",
                                                        "NUM": "pl"}})

    return TransformerMatch(name_pattern="pronoun_q",
                            args_pattern=["x", "*", conjunction_match],
                            args_capture=["quantifier_var", "quantifier_rstr", None],
                            property_transformer=property_match,
                            production=quantifier_production,
                            properties_production=sf_production,
                            removed=["_go_v_1", "_with_p"])


# Helper function that supports several transformers doing the same thing but with different
# noun shapes
#
# How many steaks did I order?
# Text Tree: which_q(x9,abstr_deg(x9),pronoun_q(x3,pron(x3),udef_q(x5,[_steak_n_1(x5), measure(e14,e15,x9), much-many_a(e15,x5)],_order_v_1(e2,x3,x5))))
#   converts to:
#       count(e14, x9, x5, udef_q(x5,_steak_n_1(x5),_order_v_1(e2,x3,x5)))
#   meaning:
#       put into x9 the count of x5 where(...)
#
# Note that the shape of "how many soups did I order?" and "how much soup did I order?" is the same except for the plurality of "soup"
# In fact, the plurality of "how many soups did I order?" should always be underspecified since it might be "1", but if it is "1" and the variable is set as plural, it will fail
# So: always remove the plurality too
def how_many_transformer(noun_match, noun_production):
    udef_production = TransformerProduction(name="udef_q", args={"ARG0": "$noun_variable", "ARG1": noun_production, "ARG2": "$udef_body"})
    count_production = TransformerProduction(name="count", args={"ARG0": "$measure_event", "ARG1": "$count", "ARG2": "$noun_variable", "ARG3": udef_production})
    underspecify_plurality_production = PropertyTransformerProduction({"$noun_variable": {"NUM": None}})

    # measure(e14,e15,x9)
    measure_match = TransformerMatch(name_pattern="measure", args_pattern=["e", "e", "x"], args_capture=["measure_event", None, "count"])

    # much-many_a(e15,x5)
    much_many_match = TransformerMatch(name_pattern="much-many_a", args_pattern=["e", "x"])

    # conjunction
    if not isinstance(noun_match, list):
        noun_match = [noun_match]
    conjunction_match = ConjunctionMatchTransformer(transformer_list=noun_match + [measure_match, much_many_match], extra_conjuncts_capture="extra_conjuncts")

    return TransformerMatch(name_pattern="udef_q",
                            args_pattern=["x", conjunction_match, "*"],
                            args_capture=[None, None, "udef_body"],
                            properties_production=underspecify_plurality_production,
                            production=count_production,
                            removed=["measure", "much-many_a"])


# How much for the x?
# which_q(x10,abstr_deg(x10),_the_q(x17,_soup_n_1(x17),
#   udef_q(x4,[measure(e14,e15,x10), generic_entity(x4), _for_p(e16,x4,x17), much-many_a(e15,x4)],unknown(e2,x4))))
#
# - measure(e14,e15,x10), much-many_a(e15,x4), generic_entity(x4), _for_p(e16,x4,x17), is the key to this
#   x17 is soup
#   x4 is much-many_a(generic_entity(x4)) --> i.e. how much of a generic amount
#       This could also be dollar() or any other measure
#   x10 should hold the value of "how much for x at the end
#   convert to generic_entity(x4), measure_units_for_item(count, measure, noun)
#   and use a special unknown_ignore() so we don't think the user just said a single word
@Transform(vocabulary)
def how_many_for_e_x_x_transformer():
    measure_units_for_item_production = TransformerProduction(name="measure_units_for_item", args={"ARG0": "$count", "ARG1": "$measure", "ARG2": "$noun_variable"})
    conjunction_production = ConjunctionProduction(conjunction_list=["$extra_conjuncts", measure_units_for_item_production])
    unknown_ignore_production = TransformerProduction(name="unknown+ignore", args={"ARG0": "$unknown_event", "ARG1": "$unknown_variable"})
    udef_production = TransformerProduction(name="udef_q", args={"ARG0": "$noun_variable", "ARG1": conjunction_production, "ARG2": unknown_ignore_production})

    # Current grammar detects "how much for the soup" (with no punctuation) as a command which gives the response "yes!" (which is wrong)
    # Convert it to a question
    sf_fixup_production = PropertyTransformerProduction({"$unknown_event": {"SF": "ques"}})

    # measure(e14,e15,x9)
    measure_match = TransformerMatch(name_pattern="measure", args_pattern=["e", "e", "x"], args_capture=["measure_event", None, "count"])

    # much-many_a(e15,x5)
    much_many_match = TransformerMatch(name_pattern="much-many_a", args_pattern=["e", "x"], args_capture=[None,  "measure"])

    # _for_p(e16,x4,x17)
    for_match = TransformerMatch(name_pattern="_for_p", args_pattern=["e", "x", "x"], args_capture=["for_event", "for_arg1", "noun_variable"])

    # unknown(e2,x4)
    unknown_match = TransformerMatch(name_pattern="unknown", args_pattern=["e", "x"], args_capture=["unknown_event", "unknown_variable"])

    # generic_entity(x4) --> We leave this one so we know what units to use, it is part of the
    #   extra_conjuncts_capture="extra_conjuncts"
    conjunction_match = ConjunctionMatchTransformer(transformer_list=[measure_match, much_many_match, for_match], extra_conjuncts_capture="extra_conjuncts")

    return TransformerMatch(name_pattern="udef_q",
                            args_pattern=["x", conjunction_match, unknown_match],
                            args_capture=[None, None, "udef_body"],
                            properties_production=sf_fixup_production,
                            production=udef_production,
                            removed=["measure", "much-many_a", "_for_p", "unknown"])


@Transform(vocabulary)
def how_many_noun_x_u_transformer():
    noun_production = TransformerProduction(name="$noun_name", args={"ARG0": "$noun_variable", "ARG1": "$noun_u"})
    noun_match = TransformerMatch(name_pattern="*", args_pattern=["x", "u"], name_capture="noun_name", args_capture=["noun_variable", "noun_u"])
    return how_many_transformer(noun_match, noun_production)


@Transform(vocabulary)
def how_many_noun_x_transformer():
    noun_production = TransformerProduction(name="$noun_name", args={"ARG0": "$noun_variable"})
    noun_match = TransformerMatch(name_pattern="*", args_pattern=["x"], name_capture="noun_name", args_capture=["noun_variable"])
    return how_many_transformer(noun_match, noun_production)


# Convert "What is ..." (i.e. singular) to "what are ..." (i.e. plural)
# because a user saying "what is vegetarian?" expects 1..inf answers, but the MRS is singular so they only get one
# really this is a question of pragmatics and should be interpreted as "underspecified" (i.e. we don't know if it is singular or plural)
# so we remove it
@Transform(vocabulary)
def what_is_singular_to_underspecified_transformer():
    production = PropertyTransformerProduction({"$x1": {"NUM": None}})
    property_match = PropertyTransformerMatch({"$x1": {"NUM": "sg"}})
    thing_match = TransformerMatch(name_pattern="thing", args_pattern=["x"], args_capture=["x1"])
    return TransformerMatch(name_pattern="which_q", args_pattern=["x", thing_match, "*"], property_transformer=property_match, properties_production=production)


# Convert "would like <noun>" to "want <noun>"
@Transform(vocabulary)
def would_like_to_want_transformer():
    production = TransformerProduction(name="_want_v_1", args={"ARG0": "$e1", "ARG1": "$x1", "ARG2": "$x2"})
    like_match = TransformerMatch(name_pattern=["_like_v_1", "_love_v_1"], args_pattern=["e", "x", "x"],
                                  args_capture=[None, "x1", "x2"])
    return TransformerMatch(name_pattern="_would_v_modal",
                            args_pattern=["e", like_match],
                            args_capture=["e1", None],
                            removed=["_would_v_modal", "_like_v_1", "_love_v_1"],
                            production=production)


# Convert "Can/could I x?", "I can/could x?" to "I x_able x?"
# "What can I x?"
@Transform(vocabulary)
def can_to_able_intransitive_transformer():
    production = TransformerProduction(name="$|name|_able", args={"ARG0": "$e1", "ARG1": "$x1"})
    production_event_replace = TransformerProduction(name="event_replace", args={"ARG0": "u99", "ARG1": "$e1", "ARG2": "$target_e"})
    conjuct_production = ConjunctionProduction(conjunction_list=["$extra_conjuncts", production_event_replace, production])

    target_predication = TransformerMatch(name_pattern="*", name_capture="name", args_pattern=["e", "x"], args_capture=["target_e", "x1"])
    target = ConjunctionMatchTransformer([target_predication], extra_conjuncts_capture="extra_conjuncts")

    return TransformerMatch(name_pattern="_can_v_modal",
                            args_pattern=["e", target],
                            args_capture=["e1", None],
                            removed=["_can_v_modal", target],
                            production=conjuct_production)


# Convert "can I have a table/steak/etc?" or "what can I have?" or "can I get a table"
# To: able_to
@Transform(vocabulary)
def can_to_able_transitive_transformer():
    production = TransformerProduction(name="$|name|_able", args={"ARG0": "$e1", "ARG1": "$x1", "ARG2": "$x2"})
    production_event_replace = TransformerProduction(name="event_replace", args={"ARG0": "u99", "ARG1": "$e1", "ARG2": "$target_e"})
    conjuct_production = ConjunctionProduction(conjunction_list=["$extra_conjuncts", production_event_replace, production])

    target_predication = TransformerMatch(name_pattern="*", name_capture="name", args_pattern=["e", "x", "x"], args_capture=["target_e", "x1", "x2"])
    target = ConjunctionMatchTransformer([target_predication], extra_conjuncts_capture="extra_conjuncts")

    return TransformerMatch(name_pattern="_can_v_modal",
                            args_pattern=["e", target],
                            args_capture=["e1", None],
                            removed=["_can_v_modal", target],
                            production=conjuct_production)


# Convert "can you show me the menu" to "you show_able the menu"
@Transform(vocabulary)
def can_to_able_transitive_transformer_indir_obj():
    production = TransformerProduction(name="$|name|_able", args={"ARG0": "$e1", "ARG1": "$x1", "ARG2": "$x2", "ARG4": "$x3"})
    target = TransformerMatch(name_pattern="*", name_capture="name", args_pattern=["e", "x", "x", "x"],
                              args_capture=[None, "x1", "x2", "x3"])
    return TransformerMatch(name_pattern="_can_v_modal", args_pattern=["e", target], args_capture=["e1", None],
                            removed=["_can_v_modal", target], production=production)





# ******** Transforms "I don't want x" to "I cancel x" ************
# Convert:
#            ┌────── _salad_n_1(x11)
# _a_q(x11,RSTR,BODY)               ┌────── pron(x3)
#                 └─ pronoun_q(x3,RSTR,BODY)         ┌─ _want_v_1(e10,x3,x11)
#                                        └─ neg(e2,ARG1)
#
@Transform(vocabulary)
def dont_want_to_cancel_transformer():
    production = TransformerProduction(name="_cancel_v_1", args={"ARG0": "$e1", "ARG1": "$x1", "ARG2": "$x2"})
    production_event_replace = TransformerProduction(name="event_replace", args={"ARG0": "u99", "ARG1": "$e1", "ARG2": "$target_e"})
    conjuct_production = ConjunctionProduction(conjunction_list=["$extra_conjuncts", production_event_replace, production])

    target_predication = TransformerMatch(name_pattern="_want_v_1", args_pattern=["e", "x", "x"], args_capture=["target_e", "x1", "x2"])
    target = ConjunctionMatchTransformer([target_predication], extra_conjuncts_capture="extra_conjuncts")

    return TransformerMatch(name_pattern="neg",
                            args_pattern=["e", target],
                            args_capture=["e1", None],
                            removed=["neg", "want_v_1"],
                            production=conjuct_production)



# can i pay the bill
@Transform(vocabulary)
def can_pay_object_transformer():
    production = TransformerProduction(name="$|name|_request", args={"ARG0": "$e1", "ARG1": "$x1", "ARG2": "$x2", "ARG3": "$i2"})

    target = TransformerMatch(name_pattern="*", name_capture="name", args_pattern=["e", "x", "x", "i"], args_capture=[None, "x1", "x2", "i2"])
    return TransformerMatch(name_pattern="_can_v_modal", args_pattern=["e", target], args_capture=["e1", None],
                            removed=["_can_v_modal", target], production=production)


# can i pay with cash
@Transform(vocabulary)
def can_paytype_transformer():
    production = TransformerProduction(name="$|name|_request", args={"ARG0": "$e1", "ARG1": "$x1", "ARG2": "$i1", "ARG3": "$i2"})
    production_event_replace = TransformerProduction(name="event_replace", args={"ARG0": "u99", "ARG1": "$e1", "ARG2": "$target_e"})
    conjuct_production = ConjunctionProduction(conjunction_list=["$extra_conjuncts", production_event_replace, production])

    target_predication = TransformerMatch(name_pattern="*", name_capture="name", args_pattern=["e", "x", "i", "i"], args_capture=["target_e", "x1", "i1", "i2"])
    target = ConjunctionMatchTransformer([target_predication], extra_conjuncts_capture="extra_conjuncts")
    return TransformerMatch(name_pattern=["_can_v_modal", "could_v_modal"],
                            name_capture="target_name",
                            args_pattern=["e", target],
                            args_capture=["e1", None],
                            removed=["$target_name",
                                     target_predication],
                            production=conjuct_production)


@Transform(vocabulary)
def could_to_able_intransitive_transformer():
    production = TransformerProduction(name="$|name|_able", args={"ARG0": "$e1", "ARG1": "$x1"})
    production_event_replace = TransformerProduction(name="event_replace", args={"ARG0": "u99", "ARG1": "$e1", "ARG2": "$target_e"})
    conjuct_production = ConjunctionProduction(conjunction_list=["$extra_conjuncts", production_event_replace, production])

    target_predication = TransformerMatch(name_pattern="*", name_capture="name", args_pattern=["e", "x"], args_capture=["target_e", "x1"])
    target = ConjunctionMatchTransformer([target_predication], extra_conjuncts_capture="extra_conjuncts")
    return TransformerMatch(name_pattern="_could_v_modal",
                            args_pattern=["e", target],
                            args_capture=["e1", None],
                            removed=["_could_v_modal", target_predication],
                            production=conjuct_production)


@Transform(vocabulary)
def could_to_able_transitive_transformer():
    production = TransformerProduction(name="$|name|_able", args={"ARG0": "$e1", "ARG1": "$x1", "ARG2": "$x2"})
    production_event_replace = TransformerProduction(name="event_replace", args={"ARG0": "u99", "ARG1": "$e1", "ARG2": "$target_e"})
    conjuct_production = ConjunctionProduction(conjunction_list=["$extra_conjuncts", production_event_replace, production])

    target_predication = TransformerMatch(name_pattern="*", name_capture="name", args_pattern=["e", "x", "x"], args_capture=["target_e", "x1", "x2"])
    target = ConjunctionMatchTransformer([target_predication], extra_conjuncts_capture="extra_conjuncts")

    return TransformerMatch(name_pattern="_could_v_modal",
                            args_pattern=["e", target],
                            args_capture=["e1", None],
                            removed=["_could_v_modal", target],
                            production=conjuct_production)


# Convert "can you show me the menu" to "you show_able the menu"
@Transform(vocabulary)
def could_to_able_transitive_transformer_indir_obj():
    production = TransformerProduction(name="$|name|_able", args={"ARG0": "$e1", "ARG1": "$x1", "ARG2": "$x2", "ARG4": "$x3"})
    target = TransformerMatch(name_pattern="*", name_capture="name", args_pattern=["e", "x", "x", "x"],
                              args_capture=[None, "x1", "x2", "x3"])
    return TransformerMatch(name_pattern="_could_v_modal", args_pattern=["e", target], args_capture=["e1", None],
                            removed=["_could_v_modal", target], production=production)


# coulc i pay the bill
@Transform(vocabulary)
def could_pay_object_transformer():
    production = TransformerProduction(name="$|name|_request", args={"ARG0": "$e1", "ARG1": "$x1", "ARG2": "$x2", "ARG3": "$i2"})
    target = TransformerMatch(name_pattern="*", name_capture="name", args_pattern=["e", "x", "x", "i"], args_capture=[None, "x1", "x2", "i2"])
    return TransformerMatch(name_pattern="_could_v_modal", args_pattern=["e", target], args_capture=["e1", None],
                            removed=["_could_v_modal", target], production=production)


# could i pay with cash
@Transform(vocabulary)
def could_paytype_transformer():
    production = TransformerProduction(name="$|name|_request", args={"ARG0": "$e1", "ARG1": "$x1", "ARG2": "$i1", "ARG3": "$i2"})
    target = TransformerMatch(name_pattern="*", name_capture="name", args_pattern=["e", "x", "i", "i"], args_capture=[None, "x1", "i1", "i2"])
    return TransformerMatch(name_pattern="_could_v_modal", args_pattern=["e", target], args_capture=["e1", None],
                            removed=["_could_v_modal", target], production=production)


# Convert "May I x?"" to "I x_request x?"
@Transform(vocabulary)
def may_to_able_intransitive_transformer():
    production = TransformerProduction(name="$|name|_able", args={"ARG0": "$e1", "ARG1": "$x1"})
    target = TransformerMatch(name_pattern="*", name_capture="name", args_pattern=["e", "x"], args_capture=[None, "x1"])
    return TransformerMatch(name_pattern="_may_v_modal", args_pattern=["e", target], args_capture=["e1", None],
                            removed=["_may_v_modal", target], production=production)


# Convert "may I have a table/steak/etc?" or "what may I have?"
# To: able_to
@Transform(vocabulary)
def may_to_able_transitive_transformer():
    production = TransformerProduction(name="$|name|_able", args={"ARG0": "$e1", "ARG1": "$x1", "ARG2": "$x2"})
    target = TransformerMatch(name_pattern="*", name_capture="name", args_pattern=["e", "x", "x"],
                              args_capture=[None, "x1", "x2"])
    return TransformerMatch(name_pattern="_may_v_modal", args_pattern=["e", target], args_capture=["e1", None],
                            removed=["_may_v_modal", target], production=production)


# may i pay with cash
@Transform(vocabulary)
def may_paytype_transformer():
    production = TransformerProduction(name="$|name|_request", args={"ARG0": "$e1", "ARG1": "$x1", "ARG2": "$i1", "ARG3": "$i2"})
    target = TransformerMatch(name_pattern="*", name_capture="name", args_pattern=["e", "x", "i", "i"], args_capture=[None, "x1", "i1", "i2"])
    return TransformerMatch(name_pattern="_may_v_modal", args_pattern=["e", target], args_capture=["e1", None],
                            removed=["_may_v_modal", target], production=production)


# Convert "I want a table for two, thank you"
# to: I want a table for two
# By removing _thank_v_1 because the index points to it and that makes things tricky
#                    ┌────── pron(x5)
# └─ pronoun_q(x27,RSTR,BODY)                       ┌─ pronoun_q(x5,RSTR,BODY)
#                        └─ _thank_v_1(e2,x3,x27,ARG3)                    └─ _want_v_1(e10,x5,x11)
# Index e2, Tree:_a_q:0(x11,def_implicit_q:1(x17,basic_numbered_hour:2(2,x17),[_table_n_1:3(x11), _for_p:4(e16,x11,x17)]),pronoun_q:5(x3,pron:6(x3),pronoun_q:7(x27,pron:8(x27),pronoun_q:9(x5,pron:10(x5),_want_v_1:11(e2,x5,x11)))))
@Transform(vocabulary)
def want_removal_transitive_transformer():
    production = TransformerProduction(name="$name", args={"ARG0": "$e1"}, args_rest="$verb_rest_args")

    target = TransformerMatch(name_pattern="*",
                              name_capture="name",
                              args_pattern=["e", "**"],
                              args_rest_capture="verb_rest_args")

    return TransformerMatch(name_pattern="_thank_v_1",
                            args_pattern=["e", "x", "x", target],
                            args_capture=["e1", None, None, None],
                            removed=["_want_v_1", target],
                            production=production)


# Convert "I want to x y" to "I x_request y"
@Transform(vocabulary)
def want_removal_transitive_transformer():
    production = TransformerProduction(name="$|name|_request", args={"ARG0": "$e1"}, args_rest="$verb_rest_args")

    target = TransformerMatch(name_pattern="*",
                              name_capture="name",
                              args_pattern=["e", "**"],
                              args_rest_capture="verb_rest_args")

    return TransformerMatch(name_pattern="_want_v_1",
                            args_pattern=["e", "x", target],
                            args_capture=["e1", None, None],
                            removed=["_want_v_1", target],
                            production=production)

# Convert "I want to x y" to "I x_request y"
@Transform(vocabulary)
def want_removal_transitive_transformer():
    production = TransformerProduction(name="$|name|_request", args={"ARG0": "$e1", "ARG1": "$x1", "ARG2": "$x2"})
    target = TransformerMatch(name_pattern="*", name_capture="name", args_pattern=["e", "x", "x"],
                              args_capture=[None, "x1", "x2"])
    return TransformerMatch(name_pattern="_want_v_1", args_pattern=["e", "x", target], args_capture=["e1", None, None],
                            removed=["_want_v_1", target], production=production)

# Convert "I want to x y" to "I x_request y"
@Transform(vocabulary)
def want_removal_transitive_transformer():
    production = TransformerProduction(name="$|name|_request", args={"ARG0": "$e1", "ARG1": "$x1", "ARG2": "$x2", "ARG3": "$i1"})
    target = TransformerMatch(name_pattern="*", name_capture="name", args_pattern=["e", "x", "x", "i"],
                              args_capture=[None, "x1", "x2", "i1"])
    return TransformerMatch(name_pattern="_want_v_1", args_pattern=["e", "x", target], args_capture=["e1", None, None],
                            removed=["_want_v_1", target], production=production)


# Convert "I want to x" to "I x_request"
@Transform(vocabulary)
def want_removal_intransitive_transformer():
    production = TransformerProduction(name="$|name|_request", args={"ARG0": "$e1", "ARG1": "$x1"})
    target = TransformerMatch(name_pattern="*", name_capture="name", args_pattern=["e", "x"], args_capture=[None, "x1"])
    return TransformerMatch(name_pattern="_want_v_1", args_pattern=["e", "x", target], args_capture=["e1", None, None],
                            removed=["_want_v_1", target], production=production)


# Convert "I want to pay with x" to "I pay_for_request"
@Transform(vocabulary)
def want_removal_paytype_transformer():
    production = TransformerProduction(name="$|name|_request", args={"ARG0": "$e1", "ARG1": "$x1", "ARG2": "$i1", "ARG3": "$i2"})
    target = TransformerMatch(name_pattern="*", name_capture="name", args_pattern=["e", "x", "i", "i"], args_capture=[None, "x1","i1","i2"])
    return TransformerMatch(name_pattern="_want_v_1", args_pattern=["e", "x", target], args_capture=["e1", None, None],
                            removed=["_want_v_1", target], production=production)


# TODO: allow the x in target(e, x) to be a conjunction
# Convert "I would like to x" to "I x_request x"
@Transform(vocabulary)
def would_like_removal_intransitive_transformer():
    production = TransformerProduction(name="$|name|_request", args={"ARG0": "$e1", "ARG1": "$x1"})
    production_event_replace = TransformerProduction(name="event_replace", args={"ARG0": "u99", "ARG1": "$e1", "ARG2": "$target_e"})
    conjuct_production = ConjunctionProduction(conjunction_list=["$extra_conjuncts", production_event_replace, production])
    target_predication = TransformerMatch(name_pattern="*", name_capture="name", args_pattern=["e", "x"], args_capture=["target_e", "x1"])
    target = ConjunctionMatchTransformer([target_predication], extra_conjuncts_capture="extra_conjuncts")
    like_match = TransformerMatch(name_pattern=["_like_v_1", "_love_v_1"], args_pattern=["e", "x", target],
                                  args_capture=[None, None, None])
    would_match = TransformerMatch(name_pattern="_would_v_modal",
                                   args_pattern=["e", like_match],
                                   args_capture=["e1", None],
                                   removed=["_would_v_modal", "_like_v_1", "_love_v_1", target_predication],
                                   production=conjuct_production)
    return would_match


# Convert "I would like to x y" to "I x_request y"
@Transform(vocabulary)
def would_like_removal_transitive_transformer():
    production = TransformerProduction(name="$|name|_request", args={"ARG0": "$etarget", "ARG1": "$x1", "ARG2": "$x2"})
    target = TransformerMatch(name_pattern="*", name_capture="name", args_pattern=["e", "x", "x"],
                              args_capture=["etarget", "x1", "x2"])
    like_match = TransformerMatch(name_pattern=["_like_v_1", "_love_v_1"], args_pattern=["e", "x", target],
                                  args_capture=[None, None, None])
    would_match = TransformerMatch(name_pattern="_would_v_modal",
                                   args_pattern=["e", like_match],
                                   args_capture=["e1", None],
                                   removed=["_would_v_modal", "_like_v_1", "_love_v_1", target],
                                   production=production)
    return would_match


# Convert "I would x y" to "I x_request y" (i.e. "I would have a menu")
@Transform(vocabulary)
def want_removal_transitive_transformer():
    production = TransformerProduction(name="$|name|_request", args={"ARG0": "$e1", "ARG1": "$x1", "ARG2": "$x2"})
    target = TransformerMatch(name_pattern="*", name_capture="name", args_pattern=["e", "x", "x"],
                              args_capture=[None, "x1", "x2"])
    return TransformerMatch(name_pattern="_would_v_modal", args_pattern=["e", target], args_capture=["e1", None],
                            removed=["_would_v_modal", target], production=production)


# ***************************
# This fake predication is used for when predications are removed during transformations
# but we need to make events equal each other so that information on them transfers through
# Start with a u variable so it doesn't look like it is introducing the new event
@Predication(vocabulary, names=["event_replace"])
def event_replace(context, state, u_ununused, e_new_binding, e_replaced_binding):
    if e_replaced_binding.value is not None:
        for item in e_replaced_binding.value.items():
            state = state.add_to_e(e_new_binding.variable.name, item[0], item[1])

    yield state


@Predication(vocabulary,
             names=["_quit_v_1"],
             phrases={
                 "quit": {'SF': 'prop-or-ques', 'TENSE': 'tensed', 'MOOD': 'indicative', 'PROG': '-', 'PERF': '-'}
             },
             properties=[{'SF': 'prop-or-ques', 'TENSE': 'tensed', 'MOOD': 'indicative', 'PROG': '-', 'PERF': '-'}]
             )
def _quit_v_1(context, state, e_binding, i_binding_1, i_binding_2):
    yield state.record_operations([LoadWorldOperation("lobby"),
                                   RespondOperation("Thanks for playing!", show_if_last_phrase=True)])


# @Predication(vocabulary,
#              names=["_thank_v_1"],
#              phrases={
#                  "That will be all, thank you": None
#              },
#              properties=None)
@Predication(vocabulary, names=["_thank_v_1"])
def _thank_v_1(context, state, e_binding, x_binding_1, x_binding_2):
    single_value_is_generic_entity_concept = x_binding_1.value is not None and \
                                             len(x_binding_1.value) == 1 and \
                                             is_concept(x_binding_1.value[0]) and \
                                             x_binding_1.value[0].single_sort_name() == "generic_entity"

    # x_binding_1.value can be None if a transform removes a generic_entity() that sets its value
    if (single_value_is_generic_entity_concept or x_binding_1.value is None) and is_computer_type(x_binding_2.value):
        yield state.record_operations([RespondOperation(f"You are welcome!"),
                                       samples.esl.esl_planner.get_reprompt_operation(state)])


@Predication(vocabulary, names=["_thank+you_v_1"])
def _thankyou_v_1(context, state, e_binding, x_target):
    if x_target.value is not None and len(x_target.value) == 1 and is_computer_type(x_target.value):
        yield state.record_operations([RespondOperation(f"You are welcome!"),
                                       samples.esl.esl_planner.get_reprompt_operation(state)])


# @Predication(vocabulary, names=["_thank_v_for"])
# def _thank_v_for(context, state, e_binding, i_unused1, x_target, i_unused2):
#     if x_target.value is not None and len(x_target.value) == 1 and is_user_type(x_target.value):
#         yield state.record_operations([RespondOperation(f"You are welcome!"),
#                                        esl.esl_planner.get_reprompt_operation(state)])

@Predication(vocabulary, names=["count"])
def count(context, state, e_binding, x_total_count_binding, x_item_to_count_binding, h_scopal_binding):
    scoped_variables, unscoped_variables = gather_scoped_variables_from_tree_at_index(state.get_binding("tree").value[0]["Tree"], context.current_predication_index())
    negated_predication_info = NegatedPredication(context.current_predication(), scoped_variables)

    # Solve the scopal binding, which could be quite complicated
    new_tree_info = copy.deepcopy(context.tree_info)
    new_tree_info["Tree"] = h_scopal_binding
    tree_solver = context.create_child_solver()
    subtree_state = state.set_x("tree", (new_tree_info,))

    # Don't try all alternative interpretations, just the one being used now
    wh_phrase_variable = perplexity.tree.get_wh_question_variable(state.get_binding("tree").value[0])
    for tree_record in tree_solver.tree_solutions(subtree_state, new_tree_info, interpretation=context._interpretation, wh_phrase_variable=wh_phrase_variable):
        if tree_record["SolutionGroupGenerator"] is not None:
            # There were solutions, so this is true
            unique_values = set()
            measurement_count = 0
            measurement_units = None
            for solution_group in tree_record["SolutionGroupGenerator"]:
                solution_group_list = []
                for solution_state in solution_group:
                    solution_group_list.append(solution_state)
                    value = solution_state.get_binding(x_item_to_count_binding.variable.name).value
                    if is_concept(value[0]):
                        context.report_error(["formNotUnderstood", "count"])
                        unique_values = set()
                        measurement_count = 0
                        break

                    else:
                        is_measurement = isinstance(value[0], Measurement)
                        if len(unique_values) > 0:
                            # We are counting individuals
                            if is_measurement:
                                # We can't mix measures and individuals
                                # try the next solution
                                break
                            else:
                                unique_values.update(value)

                        elif measurement_units is not None:
                            if not is_measurement:
                                # We can't mix measures and individuals
                                # try the next solution
                                break
                            else:
                                measurement_count += value[0].count

                        else:
                            # This is our first solution, it will set what
                            # kind of group we have
                            if isinstance(value[0], Measurement):
                                measurement_count += value[0].count if value[0].count is not None else 0
                                measurement_units = value[0].measurement_type

                            else:
                                unique_values.update(value)

                if len(unique_values) > 0 or measurement_units is not None:
                    # Make sure any operations that were created on solutions get passed on
                    all_operations = []
                    for solution in solution_group_list:
                        for operation in solution.get_operations():
                            all_operations.append(operation)

                    new_state = state.apply_operations(all_operations, True)

                    # Mark as a "negated_predication" so we don't try to check global constraints on it
                    measurement = Measurement(measurement_units if measurement_units is not None else "", len(unique_values) + measurement_count)
                    yield new_state.set_x(x_total_count_binding.variable.name, (measurement,)).add_to_e("negated_predications",
                                                                                                    context.current_predication_index(),
                                                                                                    negated_predication_info)
                    return


@Predication(vocabulary, names=["pron"])
def pron(context, state, x_who_binding):
    person = int(state.get_binding("tree").value[0]["Variables"][x_who_binding.variable.name]["PERS"])
    plurality = "unknown"
    if "NUM" in state.get_binding("tree").value[0]["Variables"][x_who_binding.variable.name].keys():
        plurality = (state.get_binding("tree").value[0]["Variables"][x_who_binding.variable.name]["NUM"])

    def bound_variable(value):
        if person == 3 and value == "son1":
            return True
        if person == 2 and value == "restaurant":
            return True
        if person == 1 and is_user_type(value):
            return True
        else:
            context.report_error(["dontKnowActor", x_who_binding.variable.name])

    def unbound_variable():
        if person == 3:
            yield "son1"
        if person == 2:
            yield "restaurant"
        if person == 1:
            if plurality == "pl":
                yield "user"
                yield "son1"

            else:
                yield "user"

    for item in combinatorial_predication_1(context, state, x_who_binding, bound_variable, unbound_variable):
        yield item


# One interpretation is a measurement, as in "How much is the steak?"
@Predication(vocabulary, names=["generic_entity"])
def generic_entity_measure(context, state, x_binding):
    def bound(val):
        if val == Measurement(ESLConcept("generic_entity"), None):
            return True

        else:
            context.report_error(["notAThing", x_binding.value, x_binding.variable.name])
            return False

    def unbound():
        yield Measurement(ESLConcept("generic_entity"), None)

    yield from combinatorial_predication_1(context, state, x_binding, bound, unbound)


@Predication(vocabulary, names=["generic_entity"])
def generic_entity(context, state, x_binding):
    def bound(val):
        if val == ESLConcept("generic_entity"):
            return True
        else:
            context.report_error(["notAThing", x_binding.value, x_binding.variable.name])
            return False

    def unbound():
        yield ESLConcept("generic_entity")

    yield from combinatorial_predication_1(context, state, x_binding, bound, unbound)


# "perfect."
@Predication(vocabulary, names=["_perfect_a_1"])
def _perfect_a_1(context, state, e_binding, u_binding):
    # Make sure there is an empty string response so that we don't say "That is correct"
    yield state.record_operations([get_reprompt_operation(state, use_blank_response=True)])


@Predication(vocabulary, names=["_okay_a_1", "_all+right_a_1", "_thanks_a_1"])
def _okay_a_1(context, state, i_binding, h_binding):
    if isinstance(h_binding, TreePredication) and h_binding.name == "unknown" and h_binding.argument_types() == ["e", "u"]:
        # Phrases like "OK." and "all right." will generate:
        # _all+right_a_1(i6,unknown(e2,u5))
        # No need to even respond
        # Make sure there is an empty string response so that we don't say "That is correct"
        yield state.record_operations([get_reprompt_operation(state, use_blank_response=True)])

    else:
        yield from context.call(state, h_binding)


@Predication(vocabulary, names=["abstr_deg"])
def abstr_deg(context, state, x_binding):
    def bound(val):
        if val == ESLConcept("degree"):
            return True
        else:
            context.report_error(["notAThing", x_binding.value, x_binding.variable.name])
            return False

    def unbound():
        yield state.set_x(x_binding.variable.name, (ESLConcept("degree"),))

    yield from combinatorial_predication_1(context, state, x_binding, bound, unbound)


# x_left_binding is the "output" of compound, the one that is used elsewhere after being
# combined
@Predication(vocabulary, names=["compound"])
def compound(context, state, e_binding, x_left_binding, x_right_binding):
    if x_left_binding.value is not None and x_right_binding.value is not None:
        if x_left_binding.value[0] == x_right_binding.value[0]:
            yield state

        elif len(x_right_binding.value) == 1 and isinstance(x_right_binding.value[0], str) and \
                x_right_binding.value[0].lower() in greetings():
            # Handle "Hi/Howdy, ...phrase..."
            yield state

        elif is_concept(x_right_binding.value[0]):
            if is_concept(x_left_binding.value[0]):
                if len(x_right_binding.value) == 1 and x_right_binding.value[0].entails(context, state, ESLConcept("menu")):
                    for dish in most_specific_specializations(state, "dish"):
                        yield state.set_x(x_left_binding.variable.name, (dish,))

                if len(x_left_binding.value) == 1 and x_left_binding.value[0].single_sort_name() == "order" and \
                    len(x_right_binding.value) == 1 and len(x_right_binding.value[0].entailed_by_which(context, state, orderable_concepts(state))) > 0:
                    # "steak order" or "food order" or "grilled item order" should all convert to a concept object that yields something that is
                    # in an order
                    item = x_right_binding.value[0]
                    new_item = item.add_criteria(rel_object_with_rel, "ordered", None)
                    yield state.set_x(x_left_binding.variable.name, (new_item,))

                else:
                    # Handle compounds where the first word is modelled as an adjective, but is a noun.
                    # For example: "tomato soup" has "soup isAdj tomato" not "soup instanceOf tomato"
                    # Note that this two ways of handling above and here are not disjunctions since it is valid
                    # to have a solution group with both approaches
                    for type in x_right_binding.value[0].entails_which_specializations(context, state):
                        new_adj_concept = x_left_binding.value[0].add_criteria(rel_subjects, "isAdj", type)
                        yield state.set_x(x_left_binding.variable.name, (new_adj_concept,))

                    # This part handles compounds where the item in question is both words like "vegetarian dish", i.e. the
                    # item is vegetarian and is a dish.  Contrast with "bicycle seat" where it is a seat, but not a bicycle.
                    # The right side is the first word -- like "vegetarian" in "vegetarian dish"
                    # Because it is a concept we require that the left side is also a concept and we merge them into
                    # a single concept by adding their criteria in conjunction
                    new_concept = x_left_binding.value[0].add_conjunction(x_right_binding.value[0])
                    yield state.set_x(x_left_binding.variable.name, (new_concept,))

            else:
                # left binding is an instance and right is a concept.  Make sure that left is an instance of that concept
                if len(x_left_binding.value) == 1 and len(x_right_binding.value) == 1:
                    if x_right_binding.value[0].instances(context, state, [x_left_binding.value[0]]):
                        yield state

                    # or that left has the right side concept as an adjective
                    elif len(x_left_binding.value) == 1 and len(x_right_binding.value) == 1 and \
                            rel_check(state, x_left_binding.value[0], "isAdj", x_right_binding.value[0].single_sort_name()):
                        yield state

    elif x_right_binding.value is not None:
        # x_left_binding.value is None, which means it was thing() and got reordered,
        # so we interpret this as "x thing" or "x item" as in "menu item" or "bicycle thing"
        # which means "anything having to do with the noun specified" (e.g. "menu" or "bicycle")
        # But, since we don't really have much modelled to allow that, we'll just special case "menu item"
        if len(x_right_binding.value) == 1 and is_concept(x_right_binding.value[0]) and x_right_binding.value[0].entails(context, state, ESLConcept("menu")):
            yield state.set_x(x_left_binding.variable.name, (ESLConcept("dish"),))


@Predication(vocabulary, names=["_can_v_modal"])
def test_can_v_modal(context, state, e_binding, h_target_binding):
    if False:
        yield None


@Predication(vocabulary, names=["basic_numbered_hour"])
def basic_numbered_hour(context, state, c_count, x_binding):
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


@Predication(vocabulary, names=["_for_p"])
def _for_p_event(context, state, e_binding, e_target_binding, x_for_binding):
    if x_for_binding.value is not None and len(x_for_binding.value) == 1 and x_for_binding.value[0] == "now":
        yield state
    else:
        yield state.add_to_e(e_target_binding.variable.name, "for", {"Value": x_for_binding.value, "Binding": x_for_binding, "Originator": context.current_predication_index()})


# Checks to make sure a "for" construct is valid, and determines what kind of "for" construct it is
# Returns True | False, for_type, x_what_type
def for_check(context, state, x_what_list, x_for_list):
    # values must be all instances or all concepts so we only need to check the type of the first
    x_what_type = perplexity.predications.value_type(x_what_list[0])

    # If multiple items are given, they are all the same scenario or we fail
    for_types = set()
    for_type = None

    for item in x_for_list:
        if is_concept(item) and item.entails(context, state, ESLConcept("person")):
            # if 'for' is a number of people like:
            # "Table for 2 people"
            for_types.add("intended to belong to")

            # Make sure the people are only the customers
            # We support "Table for 2 people" or "steak for 2 people" but nothing
            # else with this construction. "table for 2 and 4" doesn't make sense
            if not is_user_type(item.instances(context, state)) or len(x_for_list) > 1:
                context.report_error(["unexpected"])
                return False, for_type, x_what_type

        elif isinstance(item, numbers.Number):
            # if 'for' is a number like: "Table for 2" or "walk for a mile" it means "to the extent or amount of"
            #       If x is an instance, this effectively means "has the capacity of" and it just needs to be check if it has that capacity
            for_types.add("to the extent or amount of")

            # We support "Table for 2" or "steak for N" but nothing
            # else with this construction. "table for 2 and 4" doesn't make sense
            if len(x_for_list) > 1:
                context.report_error(["unexpected"])
                return False, for_type, x_what_type

            if x_what_type == perplexity.predications.VariableValueType.instance:
                # If it is an instance, check to make sure it can handle that capacity
                for what in x_what_list:
                    for value in rel_objects(state, what, "maxCapacity"):
                        if value < x_for_list[0]:
                            context.report_error(
                                ['errorText', f"{convert_to_english(state, what)} is not for {convert_to_english(state, x_for_list[0])}.",
                                 state.get_reprompt()])
                            return False, for_type, x_what_type

        elif item == "now":
            return True, "ignore", "ignore"

        elif is_user_type(item):
            # if 'for' refers to an instance of a person (checked by is_user_type) like "Table for my son and I",
            # "steak for me", etc. it means "intended to belong to"
            for_types.add("intended to belong to")

            if x_what_type == perplexity.predications.VariableValueType.instance:
                # Since "what" is collective, they both have to have it
                #       If x is an instance, this effectively means "was ordered for"
                #       Since this is an instance and not a concept
                #       "steak for my son" is really equivalent to saying "my son's steak"
                #       "is this steak for my son and I?" can be checked by seeing if we both have it

                # the people in "for" must have it *together*, so we check if they, together, have it
                if (x_for_list, x_what_list) not in state.all_rel("have"):
                    context.report_error(
                        ['errorText', f"Host: That is not for both {'and'.join(x_what_list)}."])
                    return False, for_type, x_what_type

        elif is_concept(item) and item.entails(context, state, ESLConcept("dish")):
            # if 'for' refers to a course like "steak for my main course|dinner" it means "in order to obtain, gain, or acquire" (as in "a suit for alimony")
            #       If x is an instance, this effectively means "can be used for" which is true as long as the "for" is "main course/dinner/appetizer/etc"
            for_types.add("in order to obtain")

            # We'll accept "I want the steak for my appetizer" but not for two courses
            if len(x_for_list) > 1:
                context.report_error(["unexpected"])
                return False, for_type, x_what_type

            food_concept = ESLConcept("food")
            if not all(what.entails(context, state, food_concept) for what in x_what_list):
                context.report_error(["unexpected"])
                return False, for_type, x_what_type


        if len(for_types) > 1:
            context.report_error(["unexpected"])
            return False, for_type, x_what_type

        elif len(for_types) == 0:
            context.report_error(["unexpected"])
            return False, for_type, x_what_type

        else:
            for_type = next(iter(for_types))

        return True, for_type, x_what_type


# Called to actually update the state when a "for" construct is used so that the
# conceptual value has the meaning of the "for" included in it as criteria
#
# Returns an updated version of the solution state that has x_what_binding
# updated to include the information that x_for_binding added to it
def for_update_state(context, solution, x_what_type, for_type, x_what_binding, x_for_binding, x_for_list):
    if x_what_type == perplexity.predications.VariableValueType.instance or for_type == "ignore":
        # Already fully checked above
        return solution

    else:
        # Add the appropriate "for" information to the concepts
        x_what_values = x_what_binding.value
        if for_type == "to the extent or amount of":
            x_for_value = x_for_list[0]
            amount_value = None
            if is_concept(x_for_value):
                # We've already checked that it entails person and that it is a user type
                for_variable_constraints = perplexity.solution_groups.constraints_for_variable(context, solution, x_for_binding.variable.name)
                amount_value = for_variable_constraints.min_size if for_variable_constraints is not None else 1

            else:
                amount_value = x_for_value

            # x_what_binding could be multiple like "a steak and a salad for 2"
            modified_values = [value.add_criteria(rel_subjects_greater_or_equal, "maxCapacity", amount_value) for value
                               in x_what_values]

        elif for_type == "intended to belong to":
            if sort_of(solution, x_what_values, "table") or \
                    (len(x_what_values) == 1 and x_what_values[0].entails(context, solution, ESLConcept("table"))):
                # Interpret "table for x" to mean "table having the capacity for N people"
                # Get the criteria for the variable for() uses and see if it has a constraint on it
                tree_info = solution.get_binding("tree").value[0]
                wh_phrase_variable = perplexity.tree.get_wh_question_variable(tree_info)
                this_sentence_force = sentence_force(tree_info["Variables"])
                declared_criteria_list = [data for data in declared_determiner_infos(solution.get_binding("tree").value[0], solution)]
                optimized_criteria_list = list(
                    optimize_determiner_infos(declared_criteria_list, this_sentence_force, wh_phrase_variable))
                for_predication = find_predication_from_introduced(tree_info["Tree"], x_for_binding.variable.name)
                found_constraint = None
                for arg_index in range(len(for_predication.args)):
                    arg = for_predication.args[arg_index]
                    found_constraint = None
                    for constraint in optimized_criteria_list:
                        if constraint.variable_name == arg:
                            found_constraint = constraint
                            break
                    if found_constraint is not None:
                        size = found_constraint.min_size
                        break

                # Use >= since people can always sit at a larger table
                if found_constraint is None:
                    modified_values = [x_what_values[0].add_criteria(rel_subjects_greater_or_equal, "maxCapacity", len(x_for_list))]

                else:
                    if size == 1 and len(x_for_list) > 1:
                        size = len(x_for_list)
                    modified_values = [x_what_values[0].add_criteria(rel_subjects_greater_or_equal, "maxCapacity", size)]

            elif sort_of(solution, x_what_values, "order") or \
                    (len(x_what_values) == 1 and x_what_values[0].entails(context, solution, ESLConcept("order"))):
                modified_values = [value.add_criteria(rel_objects, x_for_list[0], "possess") for value
                                   in x_what_values]

            else:
                # Anything else gets "targetPossession" as a criteria to indicate what is desired
                # But any instance can be used so it is a noop function
                modified_values = [value.add_criteria(noop_criteria, "targetPossession", x_for_list) for value
                                   in x_what_values]

        elif for_type == "in order to obtain":
            # We're just going to ignore courses, so nothing to add
            modified_values = x_what_values

        return solution.set_x(x_what_binding.variable.name, tuple(modified_values))


# Scenarios:
# I want a steak for my son
#   Needs to be conceptual since it doesn't actually exist in the world
#   "for my son" needs to get added to "steak" (or whatever)
# Is the steak for my son there?
#   - equivalent to son's steak
# So: if "what" is an instance we can see if it meets any of those scenarios in the both_bound_function
# if it is a concept, criteria gets added to it below since we can't modify the values of arguments in the both_bound_function
@Predication(vocabulary, names=["_for_p"])
def _for_p_in_style(context, state, e_binding, x_what_binding, x_for_binding):
    if not(x_for_binding.value is not None and is_user_type(x_for_binding.value)):
        yield from _for_p_helper(in_style_predication_2, context, state, e_binding, x_what_binding, x_for_binding)


# Only bother doing lift style for scenarios where we need things "together" as in "for my son and I"
@Predication(vocabulary, names=["_for_p"], arguments=[("e",), ("x", ValueSize.all), ("x", ValueSize.all)])
def _for_p_lift_style(context, state, e_binding, x_what_binding, x_for_binding):
    if x_for_binding.value is not None and is_user_type(x_for_binding.value):
        yield from _for_p_helper(lift_style_predication_2, context, state, e_binding, x_what_binding, x_for_binding)


def _for_p_helper(predication_function, context, state, e_binding, x_what_binding, x_for_binding):
    def both_bound_function(x_what, x_for):
        nonlocal for_type, x_what_type
        if not isinstance(x_what, tuple):
            x_what = (x_what, )
        if not isinstance(x_for, tuple):
            x_for = (x_for, )
        result, for_type, x_what_type = for_check(context, state, x_what, x_for)
        return result

    def x_what_unbound(x_for):
        context.report_error(["formNotUnderstood", "_for_p"])
        if False:
            yield None

    def x_for_unbound(x_what):
        context.report_error(['errorText', "Host: Sorry, I'm not here to explain things to you ...",state.get_reprompt()])
        if False:
            yield None

    # These get set by each call to lift_style_predication_2
    for_type = None
    x_what_type = None

    # Make this lift_style so that "for my son and I" gets properly interpreted as "together"
    # at least as an alternative
    for solution in predication_function(context, state, x_what_binding, x_for_binding,
                                             both_bound_function,
                                             x_what_unbound,
                                             x_for_unbound):
        new_state = for_update_state(context, solution, x_what_type, for_type, x_what_binding, x_for_binding, x_for_binding.value)

        if perplexity.tree.used_predicatively(context, state):
            # "This steak is for 2" or "This steak is for my son"
            final_value = new_state.get_binding(x_what_binding.variable.name).value
            if len(final_value) == 1 and is_concept(final_value[0]):
                # Make sure there are actually *instances* of these or it is false
                if final_value[0].instances(context, state):
                    yield new_state
                else:
                    context.report_error(
                        ['errorText', "Host: No that is not true"])

        else:
            yield new_state



@Predication(vocabulary, names=["_nothing_n_1"])
def _nothing_n_1(context, state, x_bind):
    def bound(val):
        return val == "nothing"

    def unbound():
        yield "nothing"

    yield from combinatorial_predication_1(context, state, x_bind, bound, unbound)



@Predication(vocabulary, names=["_people_n_of"])
def _people_n_of_concept(context, state, x_bind, i_unused):
    def bound(val):
        return val == ESLConcept("person")

    def unbound():
        yield ESLConcept("person")

    yield from combinatorial_predication_1(context, state, x_bind, bound, unbound)


@Predication(vocabulary, names=["_cash_n_1"])
def _cash_n_1(context, state, x_bind):
    def bound(val):
        return val == "cash"

    def unbound():
        yield "cash"

    yield from combinatorial_predication_1(context, state, x_bind, bound, unbound)


@Predication(vocabulary, names=["_moment_n_1"])
def _moment_n_1(context, state, x_bind):
    def bound(val):
        return val == "moment"

    def unbound():
        yield "moment"

    yield from combinatorial_predication_1(context, state, x_bind, bound, unbound)


@Predication(vocabulary, names=["_card_n_1"])
def _card_n_1(context, state, x_bind):
    def bound(val):
        return val == "card"

    def unbound():
        yield "card"

    yield from combinatorial_predication_1(context, state, x_bind, bound, unbound)


@Predication(vocabulary, names=["_hello_n_1"])
def _hello_n_1(context, state, x_bind):
    def bound(val):
        return val == "hello"

    def unbound():
        yield "hello"

    yield from combinatorial_predication_1(context, state, x_bind, bound, unbound)


# Implement "One order of chicken" as "One chicken"
@Predication(vocabulary, names=["_order_n_of"])
def _order_n_of(context, state, x_order_binding, x_of_what_binding):
    def both_bound(order, of_what):
        # Never appears to be called. Not used by: "My order of fries"
        return False

    def of_what_bound(of_what):
        # "I want one order of chicken" leaves x_order_binding unbound and appears to be the only way this is ever called:
        # udef_q(x15,_chicken_n_1(x15),pronoun_q(x3,pron(x3),udef_q(x8,[_order_n_of(x8,x15), card(1,e14,x8)],_want_v_1(e2,x3,x8))))
        # Only support it for things that entail food
        # (of_what is forced to be a concept below)
        if of_what.entails(context, state, ESLConcept("food")):
            yield of_what

    def order_bound(order):
        # Never appears to be called. Not used by: "What is my order of?"
        if False:
            yield None

    if x_of_what_binding.value is not None and not is_concept(x_of_what_binding.value[0]):
        context.report_error(["formNotUnderstood"])
        return

    else:
        yield from in_style_predication_2(context,
                                          state,
                                          x_order_binding,
                                          x_of_what_binding,
                                          both_bound,
                                          of_what_bound,
                                          order_bound)


@Predication(vocabulary, names=["_glass_n_of"])
def _glass_n_of(context, state, x_glass_binding, x_of_what_binding):
    def both_bound(order, of_what):
        # Unclear how to get this called
        if False:
            yield None

    def of_what_bound(of_what):
        if instance_of_or_entails(context, state, of_what, ESLConcept("water")):
            yield of_what

    def glass_bound(glass):
        if instance_of_or_entails(context, state, glass, ESLConcept("water")):
            yield glass

    yield from in_style_predication_2(context,
                                      state,
                                      x_glass_binding,
                                      x_of_what_binding,
                                      both_bound,
                                      of_what_bound,
                                      glass_bound)


@Predication(vocabulary, names=["_credit_n_1"])
def _credit_n_1(context, state, x_bind):
    def bound(val):
        return val == "credit"

    def unbound():
        yield "credit"

    yield from combinatorial_predication_1(context, state, x_bind, bound, unbound)


# One interpretation is a measurement, as in "How many dollars is the steak?"
@Predication(vocabulary, names=["_dollar_n_1"])
def _dollar_n_1_measure(context, state, x_binding, u_unused):
    def bound(val):
        if val == Measurement(ESLConcept("dollar"), None):
            return True

        else:
            context.report_error(["notAThing", x_binding.value, x_binding.variable.name])
            return False

    def unbound():
        yield Measurement(ESLConcept("dollar"), None)

    yield from combinatorial_predication_1(context, state, x_binding, bound, unbound)


@Predication(vocabulary, names=["_dollar_n_1"])
def _dollar_n_1(context, state, x_binding, u_unused):
    def bound(val):
        if val == "dollar":
            return True
        else:
            context.report_error(["notAThing", x_binding.value, x_binding.variable.name])
            return False

    def unbound():
        yield "dollar"

    yield from combinatorial_predication_1(context, state, x_binding, bound, unbound)


@Predication(vocabulary,
             names=["unknown"],
             # phrases={
             #    "table for two?": {'SF': 'ques'},
             #    "Hi, table for two, please": {'SF': 'prop'},
             #    "a table for 2": {'SF': 'prop'},
             #    "a table for 2, please!": {'SF': 'prop'},
             #    "2": {'SF': 'prop-or-ques'},
             #    "Johnny and me": {'SF': 'prop'},
             #    "yes": {'SF': 'prop-or-ques'},
             #    "You too.": {'SF': 'prop'}
             # },
             # properties=[{'SF': 'ques'},
             #             {'SF': 'prop-or-ques'},
             #             {'SF': 'prop'}],
             arguments=[("e",), ("x", ValueSize.all)])
def unknown(context, state, e_binding, x_binding):
    if x_binding.value is not None and len(x_binding.value) == 1 and x_binding.value[0] in greetings():
        operations = state.handle_world_event(context, ("greeting", ))
    else:
        operations = state.handle_world_event(context, ["unknown", x_binding.value])

    if operations is not None:
        yield state.record_operations(operations)


@Predication(vocabulary, names=["unknown"])
def unknown_eu(context, state, e_binding, u_binding):
    yield state


def greetings():
    return ["hello", "hi", "howdy"]


@Predication(vocabulary, names=["greet"])
def greet(context, state, c_arg, i_unused):
    yield state.record_operations([RespondOperation("Hello!")])


@Predication(vocabulary, names=["discourse"])
def discourse(context, state, i_unused, h_left_binding, h_right_binding):
    for solution in context.call(state, h_left_binding):
        for final_solution in context.call(solution, h_right_binding):
            yield final_solution


@Predication(vocabulary, names=["appos"], arguments=[("e",), ("x", ValueSize.all), ("x", ValueSize.all)])
def appos(context, state, e_binding, x_left_binding, x_right_binding):
    # Handle "two, my son Johnny and me", 2 will be in apposition with Johnny and me
    if len(x_left_binding.value) == 1 and (isinstance(x_left_binding.value[0], numbers.Number) or (isinstance(x_left_binding.value[0], str) and x_left_binding.value[0].isnumeric())):
        number = int(x_left_binding.value[0])
        if len(x_right_binding.value) == number:
            yield state
    # Handle "Hello, table for 2 please"
    if len(x_left_binding.value) == 1 and isinstance(x_left_binding.value[0], str) and x_left_binding.value[0].lower() in greetings():
        # HACK: Need to replace the value of "hello" with whatever it is in opposition with because that's the variable that is used elsewhere
        # in the MRS
        yield state.set_x(x_left_binding.variable.name, x_right_binding.value)

    else:
        if x_left_binding.value == x_right_binding.value:
            yield state


@Predication(vocabulary, names=["_yes_a_1", "_yup_a_1", "_sure_a_1", "_yeah_a_1"])
def _yes_a_1(context, state, i_binding, h_binding):
    for final_state in context.call(state, h_binding):
        yield state.record_operations(state.handle_world_event(context, ["yes"]))

@Predication(vocabulary, names=["_no_a_1", "_nope_a_1"])
def _no_a_1(context, state, i_binding, h_binding):
    for final_state in context.call(state, h_binding):
        yield final_state.record_operations(state.handle_world_event(context, ["no"]))


# This is not a DELPH-IN predication. It is generated by transforms to phrases like "that will be all"
@Predication(vocabulary, names=["no_standalone"])
def no_standalone(context, state, e_binding):
    yield state.record_operations(state.handle_world_event(context, ["no"]))


@Predication(vocabulary, names=["thing"])
def thing_concepts(context, state, x_binding):
    def bound_variable(value):
        if is_concept(value):
            return True

        elif is_type(state, value):
            return True

        elif len(x_binding.value) == 1 and isinstance(x_binding.value[0], Measurement):
            return True

        else:
            context.report_error(["notAThing", x_binding.value, x_binding.variable.name])
            return False

    # Yield each layer of specializations as a disjunction starting with the most detailed
    def unbound_variable():
        yield from concept_disjunctions_reverse(state, "thing")

    yield from combinatorial_predication_1(context, state, x_binding, bound_variable, unbound_variable)


@Predication(vocabulary, names=["thing"])
def thing_instances(context, state, x_binding):
    def bound_variable(value):
        if not is_concept(value) and is_instance(state, value):
            return True
        else:
            context.report_error(["notAThing", x_binding.value, x_binding.variable.name])
            return False

    def unbound_variable():
        for item in state.all_individuals():
            yield item

    yield from combinatorial_predication_1(context, state, x_binding, bound_variable, unbound_variable)


@Predication(vocabulary, names=["person"])
def person_concepts(context, state, x_person_binding):
    yield from match_all_n_concepts("person", context, state, x_person_binding)


@Predication(vocabulary, names=["person"])
def person_instances(context, state, x_person_binding):
    yield from match_all_n_instances("person", context, state, x_person_binding)


@Predication(vocabulary, names=["named"])
def named_instances(context, state, c_arg, x_binding):
    def bound_variable(value):
        return rel_check(state, value, "hasName", c_arg)

    def unbound_variable_concepts():
        for item_name in rel_subjects_objects(state, "hasName"):
            if item_name[1].lower() == c_arg.lower():
                yield item_name[0]

    # Then yield a combinatorial value of all types
    for new_state in combinatorial_predication_1(context, state, x_binding, bound_variable,
                                                 unbound_variable_concepts):
        yield new_state


def handles_adjective(state, adjective_lemma):
    return True


@Predication(vocabulary, names=["match_all_a"], matches_lemma_function=handles_adjective)
def match_all_a_concepts(adjective_type, context, state, e_introduced, x_binding):
    if used_predicatively(context, state):
        yield from adjective_default_predicative_concepts(adjective_type, context, state, x_binding)

    else:
        yield from adjective_default_concepts(adjective_type, context, state, x_binding)


@Predication(vocabulary, names=["match_all_a"], matches_lemma_function=handles_adjective)
def match_all_a_instances(adjective_type, context, state, e_introduced, x_binding):
    yield from adjective_default_instances(adjective_type, context, state, x_binding)


def handles_noun(state, noun_lemma):
    return True


# Returns True if it is a lemma we have modelled in the system
def understood_noun(state, noun_lemma):
    noun_lemmas = [noun_lemma]
    handles = ["thing"] + list(all_specializations(state, "thing"))
    return any([x in handles for x in noun_lemmas])


# Succeeds when concepts that "are" type_name (when is_adjective is False) or "isAdj" type_name (when is_adjective is True)
# are entailed by something that is orderable
def match_all_concepts_with_adjective_menu(type_name, context, state, x_binding, is_adjective=True):
    def bound_variable(value):
        # When "not" is used ("what is not vegetarian?"), the argument will be bound since thing(x) binds every possible
        # thing into the argument. To be true, x_binding must be a single orderable thing and must entail type_name
        _, entails_orderable = value.entails_which(context, state, orderable)
        if len(entails_orderable) == 1:
            if value.entails(context, state, type_name_concept):
                return True

            else:
                context.report_error(["arg_is_not_value", x_binding.variable.name, type_name])
                return False

        else:
            context.report_error(["formNotUnderstood"])
            return

    def unbound_variable_concepts():
        # Phrases like "What is vegetarian?"
        entailed_orderable = type_name_concept.entailed_by_which(context, state, orderable)
        if len(entailed_orderable) > 0:
            # The answer to "What is [x]?" where "x" is any concept entailed by at least one menu item
            # is those menu items
            yield from entailed_orderable
            return

    if x_binding.value is not None and not is_concept(x_binding.value[0]):
        context.report_error(["formNotUnderstood"])
        return

    if is_adjective:
        type_name_concept = ESLConcept()
        type_name_concept = adjective.add_criteria(rel_subjects, "isAdj", type_name)
    else:
        type_name_concept = ESLConcept(type_name)

    orderable = orderable_concepts(state)
    for new_state in combinatorial_predication_1(context, state, x_binding, bound_variable, unbound_variable_concepts):
        yield new_state


@Predication(vocabulary, names=["match_all_n"], matches_lemma_function=handles_noun)
def match_all_n_concepts(noun_type, context, state, x_binding):
    record_new_food = False

    def bound_variable(value):
        if is_concept(value):
            return True

        else:
            noun_lemmas = [value]
            if any([sort_of(state, x, noun_type) for x in noun_lemmas]):
                return True

            else:
                context.report_error(["arg_is_not_value", x_binding.variable.name, noun_type])
                return False

    def unbound_variable_concepts():
        nonlocal record_new_food
        specializes_something = perplexity.utilities.at_least_one_generator(rel_objects(state, noun_type, "specializes"))
        if not specializes_something:
            # This is a word we don't natively know, so check to see if it is a food or drink
            request_info = perplexity.OpenAI.StartOpenAIBooleanRequest("test",
                                                                       "is_food_or_drink_predication",
                                                                       f"Is {noun_type} either a food or a drink?")
            result = perplexity.OpenAI.CompleteOpenAIRequest(request_info, wait=5)
            if result == "true":
                # It is, so remember it in the fact database
                # We have to do it in the outside function because this function can only yield objects
                # it can't yield a whole new state object
                record_new_food = True

        noun_lemmas = [noun_type]
        for noun_lemma in noun_lemmas:
            yield from concept_disjunctions(state, noun_lemma)

    # Then yield a combinatorial value of all types
    for new_state in combinatorial_predication_1(context, state, x_binding, bound_variable, unbound_variable_concepts):
        # If the incoming binding was a concept, add to it
        if x_binding.value is not None and len(x_binding.value) == 1 and is_concept(x_binding.value[0]):
            new_x_binding = new_state.get_binding(x_binding.variable.name)
            x = new_x_binding.value[0].add_criteria(rel_sort_of, None, noun_type)

            if record_new_food:
                operation = AddRelOp((noun_type, "specializes", "food"))
                state = state.apply_operations([operation])

            yield state.set_x(new_x_binding.variable.name, (x,))
        else:
            if record_new_food:
                operation = AddRelOp((noun_type, "specializes", "food"))
                new_state = new_state.apply_operations([operation])

            yield new_state


@Predication(vocabulary, names=["match_all_n"], matches_lemma_function=handles_noun)
def match_all_n_instances(noun_type, context, state, x_binding):
    def bound_variable(value):
        if sort_of(state, value, noun_type):
            return True

        else:
            context.report_error(["arg_is_not_value", x_binding.variable.name, noun_type])
            return False

    def unbound_variable_instances():
        for item in all_instances(state, noun_type):
            yield item

    yield from combinatorial_predication_1(context, state, x_binding, bound_variable, unbound_variable_instances)


@Predication(vocabulary, names=["match_all_n"], matches_lemma_function=handles_noun)
def match_all_the_concept_n(noun_type, context, state, x_binding):
    def bound_variable(value):
        if sort_of(state, value, noun_type):
            return True
        else:
            context.report_error(["arg_is_not_value", x_binding.variable.name, noun_type])
            return False

    def unbound_variable_instances():
        for item in all_instances(state, noun_type):
            yield item

    # Make "the soup" return all the instances for a concept without any "the-type" restrictions IF the concept is in scope
    # This is to make pure fact checking predications like "have" and "ordered" be able to deal with instances and not have to
    # resort to concepts
    if x_binding.variable.quantifier.global_criteria == GlobalCriteria.all_rstr_meet_criteria:
        if rel_check(state, noun_type, "conceptInScope", "true"):
            for instance_state in combinatorial_predication_1(context, state, x_binding, bound_variable, unbound_variable_instances):
                new_criteria = copy.deepcopy(x_binding.variable.quantifier)
                new_criteria.global_criteria = None
                yield instance_state.set_variable_data(x_binding.variable.name, quantifier=new_criteria)
    else:
        context.report_error(["formNotUnderstood", "match_all_the_concept_n"])


@Predication(vocabulary, names=["match_all_n"], matches_lemma_function=handles_noun)
def match_all_n_i_concepts(noun_type, context, state, x_binding, i_binding):
    for new_state in match_all_n_concepts(noun_type, context, state, x_binding):
        yield new_state


@Predication(vocabulary, names=["match_all_n"], matches_lemma_function=handles_noun)
def match_all_n_i_instances(noun_type, context, state, x_binding, i_binding):
    for item in match_all_n_instances(noun_type, context, state, x_binding):
        yield item


@Predication(vocabulary, names=["_some_q"])
def the_q(context, state, x_variable_binding, h_rstr, h_body):
    # Set the constraint to be 1, inf but this is just temporary. When the constraints are optimized,
    # whatever the determiner constraint gets set to will replace these
    state = state.set_variable_data(x_variable_binding.variable.name,
                                    quantifier=VariableCriteria(context.current_predication(),
                                                                x_variable_binding.variable.name,
                                                                min_size=1,
                                                                max_size=float('inf')))

    yield from quantifier_raw(context, state, x_variable_binding, h_rstr, h_body)


def adjective_default_predicative_concepts(adjective_type, context, state, x_binding):
    def bound_variable(value):
        if rel_check(state, value, "isAdj", adjective_type):
            return True

        else:
            # Give an "I did not know that!" error if the user makes a statement about themselves
            # because we really don't know anything about them
            if is_user_type(value):
                context.report_error(["not_adj_about_player", value, adjective_type, "adjective_default_predicative_concepts"])
            else:
                context.report_error(["arg_is_not_value", x_binding.variable.name, adjective_type])

    def unbound_variable_concepts():
        # Phrases like "What is a green food?"
        for item in rel_subjects(state, "isAdj", adjective_type):
            if is_concept(item):
                yield item

    yield from combinatorial_predication_1(context, state, x_binding, bound_variable, unbound_variable_concepts)


def adjective_default_concepts(adjective_type, context, state, x_binding):
    def bound_variable(value):
        if is_concept(value):
            return True

    def unbound_variable_concepts():
        # Phrases like "What is a green food?"
        for item in rel_subjects(state, "isAdj", adjective_type):
            if is_concept(item):
                yield item

    for new_state in combinatorial_predication_1(context, state, x_binding, bound_variable, unbound_variable_concepts):
        new_x_binding = new_state.get_binding(x_binding.variable.name)
        if new_x_binding is not None and len(new_x_binding.value) == 1 and is_concept(new_x_binding.value[0]):
            x = new_x_binding.value[0].add_criteria(rel_subjects, "isAdj", adjective_type)
            yield state.set_x(new_x_binding.variable.name, (x,))



def adjective_default_instances(adjective_type, context, state, x_binding):
    def bound_variable(value):
        if not is_concept(value):
            if rel_check(state, value, "isAdj", adjective_type):
                return True
            else:
                has_match = False
                for type in all_ancestors(state, value):
                    if rel_check(state, type, "isAdj", adjective_type):
                        has_match = True
                        return True

                if not has_match:
                    context.report_error(["not_adj", x_binding.variable.name, adjective_type])
                    return False

    def unbound_variable_instances():
        for item in rel_subjects(state, "isAdj", adjective_type):
            if not is_concept(item):
                yield item

    yield from combinatorial_predication_1(context, state, x_binding, bound_variable, unbound_variable_instances)


# 'vegetarian food" is modelled as anything that has a "vegetarian" base class, not
# things that have a "hasAdj" relationship
@Predication(vocabulary, names=["_vegetarian_a_1"])
def _vegetarian_a_1_concepts_menu(context, state, e_introduced_binding, x_target_binding):
    if used_predicatively(context, state):
        # If "vegetarian" is used predicatively ('What is vegetarian?') attempt to interpret as
        # asking about properties of things on the menu
        yield from match_all_concepts_with_adjective_menu("vegetarian", context, state, x_target_binding, is_adjective=False)


@Predication(vocabulary,
             names=["solution_group__vegetarian_a_1"],
             properties_from=_vegetarian_a_1_concepts_menu,
             handles_interpretation=_vegetarian_a_1_concepts_menu)
def _vegetarian_a_1_concepts_menu_group(context, state_list, e_introduced_binding_list, x_target_binding_list):
    # Since the arguments are concepts constraints need to be checked
    if x_target_binding_list.solution_values[0].value is not None and is_concept(x_target_binding_list.solution_values[0].value[0]):
        if not check_concept_solution_group_constraints(context, state_list, x_target_binding_list, check_concepts=True):
            return

    yield state_list


@Predication(vocabulary, names=["_vegetarian_a_1"])
def _vegetarian_a_1_concepts(context, state, e_introduced_binding, x_target_binding):
    if not used_predicatively(context, state):
        yield from match_all_n_concepts("vegetarian", context, state, x_target_binding)


@Predication(vocabulary, names=["_vegetarian_a_1"])
def _vegetarian_a_1_instances(context, state, e_introduced_binding, x_target_binding):
    yield from match_all_n_instances("vegetarian", context, state, x_target_binding)



@Predication(vocabulary,
             names=["_start_v_over_able"],
             phrases={
                "Can you start over?": {'SF': 'ques', 'TENSE': 'pres', 'MOOD': 'indicative', 'PROG': '-', 'PERF': '-'},
                "Can I start over?": {'SF': 'ques', 'TENSE': 'pres', 'MOOD': 'indicative', 'PROG': '-', 'PERF': '-'},
                "Could I start over?": {'SF': 'ques', 'TENSE': 'tensed', 'MOOD': 'indicative', 'PROG': '-', 'PERF': '-'},
             },
             properties=[{'SF': 'ques', 'TENSE': ['pres', 'tensed'], 'MOOD': 'indicative', 'PROG': '-', 'PERF': '-'}]
             )
def _start_v_over_able(context, state, e_introduced_binding, x_who_binding):
    # "Can I start over" is ambiguous, it might mean just the parent, but it might mean the parent and the son too
    # assume the latter
    if x_who_binding.value is not None and len(x_who_binding.value) == 1 and x_who_binding.value[0] in ["user", "restaurant"]:
        final_state = do_task(state, [('reset_order_and_bill_for_person', context, "user"),
                                      ('reset_order_and_bill_for_person', context, "son1")])
        if final_state is not None:
            yield final_state

    elif x_who_binding.value is not None and len(x_who_binding.value) == 1 and x_who_binding.value[0] in ["son1"]:
        final_state = do_task(state, [('reset_order_and_bill_for_person', context, "son1")])
        if final_state is not None:
            yield final_state


class PastParticipleConcepts:
    def __init__(self, predicate_name_list, lemma, function=None, arg1=None, arg2=None, only_attributive=False):
        self.predicate_name_list = predicate_name_list
        self.lemma = lemma
        self.function = function if function is not None else rel_subjects
        self.arg1 = arg1 if arg1 is not None else "isAdj"
        self.arg2 = arg2 if arg2 is not None else self.lemma
        self.only_attributive = only_attributive

    def predicate_function(self, context, state, e_introduced_binding, x_actor_binding, x_target_binding):
        def bound(value):
            if is_concept(value):
                return True

            else:
                # context.report_error(["formNotUnderstood", "PastParticipleConcepts"])
                context.report_error(["not_adj", x_target_binding.variable.name, self.lemma])
                return False

        def unbound():
            for i in self.function(state, self.arg1, self.arg2):
                if is_type(state, i):
                    yield store_to_object(state, i)

        term_used_predicatively = used_predicatively(context, state)
        for new_state in combinatorial_predication_1(context, state, x_target_binding,
                                                bound,
                                                unbound):
            new_state_x_target_binding = new_state.get_binding(x_target_binding.variable.name)
            if len(new_state_x_target_binding.value) == 1:
                new_value = new_state_x_target_binding.value[0]
                if term_used_predicatively:
                    if self.only_attributive:
                        context.report_error(["formNotUnderstood"])
                        return

                # Add extra criteria to the concept to represent the past participle
                x_object = new_value.add_criteria(self.function, self.arg1, self.arg2)

                if term_used_predicatively and len(x_object.instances(context, state)) == 0:
                    # "The salmon is smoked" interpreted as a concept requires that there is at least one instance of
                    # "smoked salmon"
                    context.report_error(["not_adj", x_target_binding.variable.name, self.lemma])
                    return

                yield state.set_x(x_target_binding.variable.name, (x_object,))


class PastParticipleInstances:
    def __init__(self, predicate_name_list, lemma):
        self.predicate_name_list = predicate_name_list
        self.lemma = lemma

    def predicate_function(self, context, state, e_introduced_binding, i_binding, x_target_binding):
        def bound(value):
            if is_instance(value) and (value, self.lemma) in state.all_rel("isAdj"):
                return True

            else:
                # context.report_error(["formNotUnderstood", "PastParticipleInstances"])
                context.report_error(["not_adj", self.lemma,state.get_reprompt()])
                return False

        def unbound():
            for i in state.all_rel("isAdj"):
                if i[1] == self.lemma and is_instance(state, i[0]):
                    yield i[0]

        yield from combinatorial_predication_1(context, state, x_target_binding,
                                                bound,
                                                unbound)


grilled = PastParticipleConcepts(["_grill_v_1"], "grilled")
roasted = PastParticipleConcepts(["_roast_v_cause"], "roasted")
smoked_concepts = PastParticipleConcepts(["_smoke_v_1"], "smoked")
smoked_instances = PastParticipleInstances(["_smoke_v_1"], "smoked")
ordered_concepts_attributive = PastParticipleConcepts(["_order_v_1"], "ordered", rel_object_with_rel, "ordered", None, only_attributive=True)


@Predication(vocabulary,
             names=["_request_v_1"],
             phrases={
                "The steak I requested is rare": {'SF': 'prop', 'TENSE': 'past', 'MOOD': 'indicative', 'PROG': '-', 'PERF': '-'}
             },
             properties=[{'SF': 'prop', 'TENSE': 'past', 'MOOD': 'indicative', 'PROG': '-', 'PERF': '-'}]
             )
def _requested_v_1_attributive(context, state, e_introduced_binding, x_actor_binding, x_target_binding):
    yield from ordered_concepts_attributive.predicate_function(context, state, e_introduced_binding, x_actor_binding, x_target_binding)


@Predication(vocabulary,
             names=ordered_concepts_attributive.predicate_name_list,
             phrases={
                "The steak I ordered is rare": {'SF': 'prop', 'TENSE': 'past', 'MOOD': 'indicative', 'PROG': '-', 'PERF': '-'}
             },
             properties=[{'SF': 'prop', 'TENSE': 'past', 'MOOD': 'indicative', 'PROG': '-', 'PERF': '-'}]
             )
def _ordered_v_1_attributive(context, state, e_introduced_binding, x_actor_binding, x_target_binding):
    yield from ordered_concepts_attributive.predicate_function(context, state, e_introduced_binding, x_actor_binding, x_target_binding)


@Predication(vocabulary,
             names=grilled.predicate_name_list,
             phrases={
                "I want the grilled salmon": {'SF': 'prop', 'TENSE': 'untensed', 'MOOD': 'indicative', 'PROG': 'bool', 'PERF': '-'},
                "Do you have the grilled salmon?": {'SF': 'prop', 'TENSE': 'untensed', 'MOOD': 'indicative', 'PROG': 'bool', 'PERF': '-'},
                "Give me the grilled salmon.": {'SF': 'prop', 'TENSE': 'untensed', 'MOOD': 'indicative', 'PROG': 'bool', 'PERF': '-'},
                "Is the salmon grilled?": {'SF': 'ques', 'TENSE': 'pres', 'MOOD': 'indicative', 'PROG': '-', 'PERF': '-'},
                "The salmon is grilled": {'SF': 'prop', 'TENSE': 'pres', 'MOOD': 'indicative', 'PROG': '-', 'PERF': '-'}
             },
             properties=[{'SF': 'prop', 'TENSE': 'untensed', 'MOOD': 'indicative', 'PROG': 'bool', 'PERF': '-'},
                         {'SF': ['ques', 'prop'], 'TENSE': 'pres', 'MOOD': 'indicative', 'PROG': '-', 'PERF': '-'}]
             )
def _grill_v_1(context, state, e_introduced_binding, i_binding, x_target_binding):
    yield from grilled.predicate_function(context, state, e_introduced_binding, i_binding, x_target_binding)


@Predication(vocabulary,
             names=roasted.predicate_name_list,
             phrases={
                "I want the roasted chicken": {'SF': 'prop', 'TENSE': 'untensed', 'MOOD': 'indicative', 'PROG': 'bool', 'PERF': '-'},
                "Do you have the roasted chicken?": {'SF': 'prop', 'TENSE': 'untensed', 'MOOD': 'indicative', 'PROG': 'bool', 'PERF': '-'},
                "Give me the roasted chicken.": {'SF': 'prop', 'TENSE': 'untensed', 'MOOD': 'indicative', 'PROG': 'bool', 'PERF': '-'},
                "Is the chicken roasted?": {'SF': 'ques', 'TENSE': 'pres', 'MOOD': 'indicative', 'PROG': '-', 'PERF': '-'},
                "The chicken is roasted": {'SF': 'prop', 'TENSE': 'pres', 'MOOD': 'indicative', 'PROG': '-', 'PERF': '-'}
             },
             properties=[{'SF': 'prop', 'TENSE': 'untensed', 'MOOD': 'indicative', 'PROG': 'bool', 'PERF': '-'},
                         {'SF': ['ques', 'prop'], 'TENSE': 'pres', 'MOOD': 'indicative', 'PROG': '-', 'PERF': '-'}]
             )
def _roast_v_1(context, state, e_introduced_binding, i_binding, x_target_binding):
    yield from roasted.predicate_function(context, state, e_introduced_binding, i_binding, x_target_binding)


@Predication(vocabulary,
             names=smoked_concepts.predicate_name_list,
             phrases={
                "I want the smoked pork": {'SF': 'prop', 'TENSE': 'untensed', 'MOOD': 'indicative', 'PROG': 'bool', 'PERF': '-'},
                "Do you have the smoked pork?": {'SF': 'prop', 'TENSE': 'untensed', 'MOOD': 'indicative', 'PROG': 'bool', 'PERF': '-'},
                "Give me the smoked pork.": {'SF': 'prop', 'TENSE': 'untensed', 'MOOD': 'indicative', 'PROG': 'bool', 'PERF': '-'},
                "Is the pork smoked?": {'SF': 'ques', 'TENSE': 'pres', 'MOOD': 'indicative', 'PROG': '-', 'PERF': '-'},
                "The pork is smoked": {'SF': 'prop', 'TENSE': 'pres', 'MOOD': 'indicative', 'PROG': '-', 'PERF': '-'}
             },
             properties=[{'SF': 'prop', 'TENSE': 'untensed', 'MOOD': 'indicative', 'PROG': 'bool', 'PERF': '-'},
                         {'SF': ['ques', 'prop'], 'TENSE': 'pres', 'MOOD': 'indicative', 'PROG': '-', 'PERF': '-'}])
def _smoke_v_1(context, state, e_introduced_binding, i_binding, x_target_binding):
    yield from smoked_concepts.predicate_function(context, state, e_introduced_binding, i_binding, x_target_binding)


# Treat "x on the menu" as a special case, since it is really close to a figure of speech rather than something
# literal
@Predication(vocabulary, names=("_on_p_loc",))
def on_p_loc_menu(context, state, e_introduced_binding, x_actor_binding, x_location_binding):
    def check_item_on_item(item1, item2):
        if valid_player_request(context, state, [item1], [ESLConcept("food"),
                          ESLConcept("drink")]): #orderable_concepts(state)):
            return True
        else:
            context.report_error(["notOn", x_actor_binding.variable.name, x_location_binding.variable.name])

    def all_item1_on_item2(item2):
        # Code below already checked that item2 is a "menu"
        for i in state.all_rel("on"):
            if i[1] == "menu":
                yield store_to_object(state, i[0])

    def all_item2_containing_item1(item1):
        for i in state.all_rel("on"):
            if i[0] == item1:
                yield i[1]

    # Only implemented for entailments of "menu" that resolve to a real instance of a menu
    if x_location_binding.value is not None and len(x_location_binding.value) == 1 and is_concept(x_location_binding.value[0]) \
            and x_location_binding.value[0].entails(context, state, ESLConcept("menu")) and x_location_binding.value[0].instances(context, state):
        yield from in_style_predication_2(context,
                                          state,
                                          x_actor_binding,
                                          x_location_binding,
                                          check_item_on_item,
                                          all_item1_on_item2,
                                          all_item2_containing_item1)
    else:
        context.report_error(["formNotUnderstood"])
        return


# @Predication(vocabulary, names=("_on_p_loc",))
# def on_p_loc(context, state, e_introduced_binding, x_actor_binding, x_location_binding):
#     def check_item_on_item(item1, item2):
#         if (item1, item2) in state.all_rel("on"):
#             return True
#         else:
#             context.report_error(["notOn", x_actor_binding.variable.name, x_location_binding.variable.name])
#
#     def all_item1_on_item2(item2):
#         for i in state.all_rel("on"):
#             if i[1] == item2:
#                 yield store_to_object(state, i[0])
#
#     def all_item2_containing_item1(item1):
#         for i in state.all_rel("on"):
#             if i[0] == item1:
#                 yield i[1]
#
#     yield from in_style_predication_2(context,
#                                       state,
#                                       x_actor_binding,
#                                       x_location_binding,
#                                       check_item_on_item,
#                                       all_item1_on_item2,
#                                       all_item2_containing_item1)


@Predication(vocabulary, names=("_with_p",))
def _with_p(context, state, e_introduced_binding, e_main, x_binding):
    yield state.add_to_e(e_main.variable.name, "With", {"VariableName": x_binding.variable.name,
                                                        "Value": x_binding.value[0],
                                                        "Originator": context.current_predication_index()})


# Can I pay the bill?
@Predication(vocabulary,
             names=["_pay_v_for_request"],
             phrases={
                "Can I pay the bill?": {'SF': 'ques', 'TENSE': 'pres', 'MOOD': 'indicative', 'PROG': '-', 'PERF': '-'},
                "I want to pay the bill": {'SF': 'prop', 'TENSE': 'pres', 'MOOD': 'indicative', 'PROG': '-', 'PERF': '-'},
                "Who can pay the bill": {'SF': 'ques', 'TENSE': 'pres', 'MOOD': 'indicative', 'PROG': '-', 'PERF': '-'},
                "What can I pay?": {'SF': 'ques', 'TENSE': 'pres', 'MOOD': 'indicative', 'PROG': '-', 'PERF': '-'}
             },
             properties=[{'SF': 'ques', 'TENSE': 'pres', 'MOOD': 'indicative', 'PROG': '-', 'PERF': '-'},
                         {'SF': 'prop', 'TENSE': 'pres', 'MOOD': 'indicative', 'PROG': '-', 'PERF': '-'}]
             )
def _pay_v_for_object(context, state, e_introduced_binding, x_actor_binding, x_object_binding, i_binding):
    def both_bound_prediction_function(x_actor, x_object):
        # Players are able to pay for any food, or the bill
        if is_user_type(x_actor):
            if valid_player_request(context, state, [x_object], [ESLConcept("food"), ESLConcept("bill"), ESLConcept("check")]):
                return True
            else:
                context.report_error(["errorText", "You can't pay for that."])
                return False

    def actor_unbound(x_object):
        # What/Who can pay for x?
        found = False
        if valid_player_request(context, state, [x_object], [ESLConcept("food"), ESLConcept("bill"), ESLConcept("check")]):
            found = True
            yield from user_types()

        if not found:
            context.report_error(["nothing_verb_x", x_actor_binding.variable.name, "pay for", x_object_binding.variable.name])

    def object_unbound(x_actor):
        # This is a "What can I pay for?" type question
        if is_user_type(x_actor):
            yield ESLConcept("bill")

    yield from in_style_predication_2(context, state, x_actor_binding, x_object_binding,
                                      both_bound_prediction_function,
                                      actor_unbound,
                                      object_unbound)


@Predication(vocabulary,
             names=["solution_group__pay_v_for_request"],
             properties_from=_pay_v_for_object)
def _pay_v_for_object_group(context, state_list, e_introduced_list, x_actor_variable_group, x_object_variable_group, i_binding_list):
    tree_info = state_list[0].get_binding("tree").value[0]
    wh_variable = is_wh_question(tree_info)
    if wh_variable:
        yield state_list

    else:
        # As long as these were valid objects to pay for, just interpret as "give me the bill"
        task = ('satisfy_want', context, variable_group_values_to_list(x_actor_variable_group), [(ESLConcept("bill"),)], 1)
        final_state = do_task(state_list[0].world_state_frame(), [task])
        if final_state:
            yield [final_state]


# All of the "can/couldpay with" alternatives are interpreted as "I want to pay with cash/card"
@Predication(vocabulary,
             names=["_pay_v_for", "_pay_v_for_request"],
             phrases={
                "We're ready to pay": {'SF': 'prop', 'TENSE': 'pres', 'MOOD': 'indicative', 'PROG': '-', 'PERF': '-'},
                "I want to pay with cash": {'SF': 'prop', 'TENSE': 'pres', 'MOOD': 'indicative', 'PROG': '-', 'PERF': '-'},
                "I will pay with cash": {'SF': 'prop', 'TENSE': 'fut', 'MOOD': 'indicative', 'PROG': '-', 'PERF': '-'},
                "Can I pay with cash": {'SF': 'ques', 'TENSE': 'pres', 'MOOD': 'indicative', 'PROG': '-', 'PERF': '-'},
                "Could I pay with cash": {'SF': 'ques', 'TENSE': 'past', 'MOOD': 'indicative', 'PROG': '-', 'PERF': '-'}
             },
             properties=[{'SF': 'prop', 'TENSE': 'fut', 'MOOD': 'indicative', 'PROG': '-', 'PERF': '-'},
                         {'SF': 'ques', 'TENSE': 'pres', 'MOOD': 'indicative', 'PROG': '-', 'PERF': '-'},
                         {'SF': 'prop', 'TENSE': 'pres', 'MOOD': 'indicative', 'PROG': '-', 'PERF': '-'},
                         {'SF': 'ques', 'TENSE': 'past', 'MOOD': 'indicative', 'PROG': '-', 'PERF': '-'}],
             handles=[("With", EventOption.optional)])
def _pay_v_for(context, state, e_introduced_binding, x_actor_binding, i_binding1, i_binding2):
    if state.sys["responseState"] != "way_to_pay":
        way_to_pay_state = state.record_operations(state.handle_world_event(context, ["user_wants", (ESLConcept("bill"),)]))
        if way_to_pay_state.sys["responseState"] != "way_to_pay":
            yield way_to_pay_state
            return
    else:
        way_to_pay_state = state

    if e_introduced_binding.value is not None and "With" in e_introduced_binding.value:
        if is_concept(e_introduced_binding.value["With"]["Value"]):
            values = [x for x in e_introduced_binding.value["With"]["Value"].instances(context, way_to_pay_state)]
            if len(values) == 0:
                yield do_task(way_to_pay_state, [("respond", context, "You don't have one of those.")])
                return
        else:
            values = [e_introduced_binding.value["With"]["Value"]]

        if not any(x in ["cash", "card"] for x in values):
            yield do_task(way_to_pay_state, [("respond", context, "You can't pay with that.")])
            return

        yield way_to_pay_state.record_operations(
            way_to_pay_state.handle_world_event(context, ["unknown", (e_introduced_binding.value["With"]["Value"],)]))

    else:
        yield way_to_pay_state
        return


@Predication(vocabulary,
             names=["_want_v_1", "_need_v_1", "_get_v_1_request", "_have_v_1_request", "_order_v_1_request"],
             phrases={
                "we'd like a table for 2": {'SF': 'prop', 'TENSE': 'tensed', 'MOOD': 'indicative', 'PROG': '-', 'PERF': '-'},
                "I want a steak": {'SF': 'prop', 'TENSE': 'pres', 'MOOD': 'indicative', 'PROG': '-', 'PERF': '-'},
                "I'd like a steak": {'SF': 'prop', 'TENSE': 'tensed', 'MOOD': 'indicative', 'PROG': '-', 'PERF': '-'},
                "I need a steak": {'SF': 'prop', 'TENSE': 'pres', 'MOOD': 'indicative', 'PROG': '-', 'PERF': '-'},
                "My son would like a salad": {'SF': 'prop', 'TENSE': 'tensed', 'MOOD': 'indicative', 'PROG': '-', 'PERF': '-'},
                "I'd like to get a steak": {'SF': 'prop', 'TENSE': 'untensed', 'MOOD': 'indicative', 'PROG': '-', 'PERF': '-'},
                "I'd like to have a steak": {'SF': 'prop', 'TENSE': 'untensed', 'MOOD': 'indicative', 'PROG': '-', 'PERF': '-'},
                "I'd like to order a steak": {'SF': 'prop', 'TENSE': 'untensed', 'MOOD': 'indicative', 'PROG': '-', 'PERF': '-'},
                "I want a table thank you": {'SF': 'comm', 'TENSE': 'pres', 'MOOD': 'indicative', 'PROG': '-', 'PERF': '-'}
             },
             properties=[
                {'SF': 'comm', 'TENSE': 'pres', 'MOOD': 'indicative', 'PROG': '-', 'PERF': '-'},
                {'SF': 'prop', 'TENSE': ['pres', 'tensed', 'untensed'], 'MOOD': 'indicative', 'PROG': '-', 'PERF': '-'}
             ],
             arguments=[("e",), ("x", ValueSize.all), ("x", ValueSize.all)])
def _want_v_1(context, state, e_introduced_binding, x_actor_binding, x_object_binding):
    yield from want_v_1_helper(context, state, e_introduced_binding, x_actor_binding, x_object_binding)


# This is its own raw function so it can be called by many different predications and not get checked
# for verb properties (like sentence_force)
def want_v_1_helper(context, state, e_introduced_binding, x_actor_binding, x_object_binding):
    # We never support wanting a particular instance of something, so just fail now
    if x_object_binding.value is not None and not is_concept(x_object_binding.value[0]):
        return

    def criteria_bound(x_actor, x_object):
        if is_user_type(x_actor):
            # This allows anything the user(s) want to succeed
            return True

        elif (x_actor, x_object) in state.all_rel("want"):
                return True

        else:
            context.report_error(["notWant", x_actor_binding.variable.name, x_object_binding.variable.name])
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

    yield from lift_style_predication_2(context, state, x_actor_binding, x_object_binding, criteria_bound,
                                        wanters_of_obj, wanted_of_actor)


@Predication(vocabulary,
             names=["solution_group__want_v_1", "solution_group__need_v_1", "solution_group__get_v_1_request", "solution_group__have_v_1_request",
                    "solution_group__order_v_1_request"],
             properties_from=_want_v_1)
def want_group(context, state_list, e_introduced_binding_list, x_actor_variable_group, x_what_variable_group):
    yield from want_group_helper(context, state_list, e_introduced_binding_list, x_actor_variable_group, x_what_variable_group)


def want_group_helper(context, state_list, e_introduced_binding_list, x_actor_variable_group, x_what_variable_group):
    current_state = copy.deepcopy(state_list[0])
    if is_concept(x_actor_variable_group.solution_values[0]):
        # This solution group handler requires non-conceptual actors
        context.report_error(["formNotUnderstood"])
        return

    # We do have lots of places where we deal with conceptual "wants", such as: "I want the menu", "I'll have a steak"
    # In fact, we *never* deal with wanting a particular instance because that would mean "I want that particular steak right there"
    # and we don't support that
    # These are concepts. Only need to check the first because:
    # If one item in the group is a concept, they all are
    # x_what_variable_group.solution_values[0].value can be None if it is scoped under negation
    if x_what_variable_group.solution_values[0].value is not None and is_concept(x_what_variable_group.solution_values[0].value[0]):
        concept = x_what_variable_group.solution_values[0].value[0]

        # Check to make sure the constraints are valid for this concept.
        # Because in "I want x", 'x' is always a concept, but the constraint is on the instances
        # (as in "I want a steak" meaning "I want 1 instance of the concept of steak", we tell
        # check_concept_solution_group_constraints to check instances via check_concepts=False
        if check_concept_solution_group_constraints(context, state_list, x_what_variable_group, check_concepts=False):
            # Even though it is only one type of thing, they could have said something like "We want steaks"
            # so they really want more than one instance
            current_state = do_task(current_state.world_state_frame(),
                                    [('satisfy_want',
                                      context,
                                      variable_group_values_to_list(x_actor_variable_group),
                                      variable_group_values_to_list(x_what_variable_group),
                                      min_from_variable_group(x_what_variable_group))])
            if current_state:
                yield [current_state]

    else:
        # This handler doesn't deal with wants of instances, but others might
        context.report_error(["formNotUnderstood"])
        return


@Predication(vocabulary,
             names=["_check_v_1"],
             phrases={
                "Check, please": {'SF': 'comm', 'TENSE': 'pres', 'MOOD': 'indicative', 'PROG': '-', 'PERF': '-'}
             },
             properties={'SF': 'comm', 'TENSE': 'pres', 'MOOD': 'indicative', 'PROG': '-', 'PERF': '-'})
def _check_v_1(context, state, e_introduced_binding, x_actor_binding, i_object_binding):
    if i_object_binding.value is not None:
        return

    def criteria_bound(x):
        return x == "restaurant"

    def unbound():
        yield None

    yield from combinatorial_predication_1(context, state, x_actor_binding, criteria_bound, unbound)


@Predication(vocabulary,
             names=["solution_group__check_v_1"],
             properties_from=_check_v_1)
def _check_v_1_group(context, state_list, e_introduced_binding, x_actor_binding, i_object_binding):
    current_state = copy.deepcopy(state_list[0])

    actors = variable_group_values_to_list(x_actor_binding)
    if len(actors) == 1 and len(actors[0]) == 1 and actors[0][0] == "restaurant":
        final_state = do_task(current_state.world_state_frame(), [('get_bill', context, [("user",)], min_from_variable_group(x_actor_binding))])
        if final_state is not None:
            yield [final_state]

    else:
        # This handler requires the check verb to be directed at the restaurant
        context.report_error(["formNotUnderstood"])
        return


# We do not want to support future propositions like "You will give me a table" even though
# they are syntactically correct because they just sound weird
@Predication(vocabulary,
             names=["_give_v_1", "_bring_v_1"],
             phrases={
                "Give|bring me a table": {'SF': 'comm', 'TENSE': 'pres', 'MOOD': 'indicative', 'PROG': '-', 'PERF': '-'},
                "Will you give|bring me a table?": {'SF': 'ques', 'TENSE': 'fut', 'MOOD': 'indicative', 'PROG': '-', 'PERF': '-'}
             },
             properties=[{'SF': 'comm', 'TENSE': 'pres', 'MOOD': 'indicative', 'PROG': '-', 'PERF': '-'},
                         {'SF': 'ques', 'TENSE': 'fut', 'MOOD': 'indicative', 'PROG': '-', 'PERF': '-'}
                         ])
def _give_v_1(context, state, e_introduced_binding, x_actor_binding, x_object_binding, x_target_binding):
    if state.get_binding(x_actor_binding.variable.name).value[0] == "restaurant":
        for item in want_v_1_helper(context, state, e_introduced_binding, x_target_binding, x_object_binding):
            yield item


@Predication(vocabulary,
             names=["solution_group__give_v_1", "solution_group__bring_v_1"],
             properties_from=_give_v_1)
def solution_group__give_v_1(context, state_list, e_introduced_binding_list, x_actor_variable_group, x_object_variable_group, x_target_variable_group):
    yield from want_group_helper(context, state_list, e_introduced_binding_list, x_target_variable_group, x_object_variable_group)


@Predication(vocabulary,
             names=["_show_v_1", "_show_v_1_able"],
             phrases={
                "Can you show me the menu?": {'SF': 'ques', 'TENSE': 'pres', 'MOOD': 'indicative', 'PROG': '-', 'PERF': '-'},
                "Could you show me the menu?": {'SF': 'ques', 'TENSE': 'tensed', 'MOOD': 'indicative', 'PROG': '-', 'PERF': '-'},
                "Show me a menu": {'SF': 'comm', 'TENSE': 'pres', 'MOOD': 'indicative', 'PROG': '-', 'PERF': '-'}
             },
             properties=[
                {'SF': ['ques', 'comm'], 'TENSE': 'pres', 'MOOD': 'indicative', 'PROG': '-', 'PERF': '-'},
                {'SF': 'ques', 'TENSE': 'tensed', 'MOOD': 'indicative', 'PROG': '-', 'PERF': '-'}
             ])
def _show_v_1(context, state, e_introduced_binding, x_actor_binding, x_target_binding, x_to_actor_binding):
    if is_concept(x_actor_binding) or is_concept(x_to_actor_binding):
        context.report_error(["formNotUnderstood", "_show_v_1"])
        return

    if not is_computer_type(x_actor_binding.value):
        context.report_error(["dontKnowHow"])
        return

    def bound(x_actor, x_object):
        # Do a cursory check to make sure it is some kind of "menu"
        # More detailed check is in the group predication
        if is_user_type(x_actor):
            if is_concept(x_object) and x_object.entails(context, state, ESLConcept("menu")):
                return True

            else:
                context.report_error(["errorText", "Sorry, I can't show you that"])

        else:
            context.report_error(["dontKnowHow"])
            return

    def wanters_of_obj(x_object):
        if False:
            yield None
        # not currently going to support asking who is seating someone
        context.report_error(["formNotUnderstood", "_show_v_1"])
        return

    def wanted_of_actor(x_actor):
        if False:
            yield None
        context.report_error(["formNotUnderstood", "_show_v_1"])
        return

    yield from in_style_predication_2(context, state, x_to_actor_binding, x_target_binding, bound,
                                      wanters_of_obj, wanted_of_actor)


@Predication(vocabulary, names=["solution_group__show_v_1", "solution_group__show_v_1_able"])
def _show_v_cause_group(context, state_list, e_introduced_binding, x_actor_variable_group, x_target_variable_group, x_to_actor_variable_group):
    # Only need to check constraints on x_target_variable_group since it is the only variable that is a concept
    # The player is asking to be shown *instances* so check_concepts = False
    if not check_concept_solution_group_constraints(context, state_list, x_target_variable_group, check_concepts=False):
        return

    to_actor_list = variable_group_values_to_list(x_to_actor_variable_group)
    show_list = variable_group_values_to_list(x_target_variable_group)
    current_state = do_task(state_list[0].world_state_frame(),
                            [('satisfy_want', context, to_actor_list, show_list, min_from_variable_group(x_target_variable_group))])
    if current_state:
        yield [current_state]


@Predication(vocabulary,
             names=["_seat_v_cause", "_seat_v_cause_able"],
             phrases={
                "seat me": {'SF': 'comm', 'TENSE': 'pres', 'MOOD': 'indicative', 'PROG': '-', 'PERF': '-'},
                "can you seat me?": {'SF': 'ques', 'TENSE': 'pres', 'MOOD': 'indicative', 'PROG': '-', 'PERF': '-'}
             },
             properties=[
                    {'SF': ['comm', 'ques'], 'TENSE': 'pres', 'MOOD': 'indicative', 'PROG': '-', 'PERF': '-'}
             ])
def _seat_v_cause(context, state, e_introduced_binding, x_actor_binding, x_object_binding):
    if is_concept(x_actor_binding) or is_concept(x_object_binding):
        context.report_error(["formNotUnderstood", "_seat_v_cause"])
        return

    def criteria_bound(x_actor, x_object):
        return is_computer_type(x_actor) and is_user_type(x_object)

    def wanters_of_obj(x_object):
        if False:
            yield None
        # not currently going to support asking who is seating someone
        context.report_error(["formNotUnderstood", "_seat_v_cause"])
        return

    def wanted_of_actor(x_actor):
        if False:
            yield None
        context.report_error(["formNotUnderstood", "_seat_v_cause"])
        return

    yield from in_style_predication_2(context, state, x_actor_binding, x_object_binding, criteria_bound,
                                      wanters_of_obj, wanted_of_actor)


@Predication(vocabulary,
             names=["solution_group__seat_v_cause", "solution_group__seat_v_cause_able"],
             properties_from=_seat_v_cause)
def _seat_v_cause_group(context, state_list, e_introduced_binding, x_actor_variable_group, x_what_variable_group):
    new_state = do_task(state_list[0].world_state_frame(),
                        [('satisfy_want', context, variable_group_values_to_list(x_what_variable_group), [(ESLConcept("table"),)], 1)])
    if new_state:
        yield [new_state]


@Predication(vocabulary, names=["loc_nonsp"])
def loc_nonsp(context, state, e_introduced_binding, x_actor_binding, x_loc_binding):
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

    yield from in_style_predication_2(context, state, x_actor_binding, x_loc_binding, item1_in_item2, items_in_item1,
                                      item1_in_items)


@Predication(vocabulary, names=["loc_nonsp"])
def loc_nonsp_eex(context, state, e_introduced_binding, e_binding, x_loc_binding):
    yield state


@Predication(vocabulary, names=["_now_a_1"])
def _now_a_1(context, state, e_introduced_binding, x_binding):
    def bound_variable(value):
        if value in ["now"]:
            return True

        else:
            context.report_error(["notAThing", x_binding.value, x_binding.variable.name])
            return False

    def unbound_variable():
        yield "now"

    yield from combinatorial_predication_1(context, state, x_binding, bound_variable, unbound_variable)


@Predication(vocabulary, names=["_today_a_1"])
def _today_a_1(context, state, e_introduced_binding, x_binding):
    def bound_variable(value):
        if value in ["today"]:
            return True

        else:
            context.report_error(["notAThing", x_binding.value, x_binding.variable.name])
            return False

    def unbound_variable():
        yield "today"

    yield from combinatorial_predication_1(context, state, x_binding, bound_variable, unbound_variable)


@Predication(vocabulary, names=["time_n"])
def time_n(context, state, x_binding):
    def bound_variable(value):
        if value in ["now", "today", "yesterday", "tomorrow"]:
            return True
        else:
            context.report_error(["notAThing", x_binding.value, x_binding.variable.name])
            return False

    def unbound_variable():
        yield "now"
        yield "today"
        yield "yesterday"
        yield "tomorrow"

    yield from combinatorial_predication_1(context, state, x_binding, bound_variable, unbound_variable)


@Predication(vocabulary, names=["def_implicit_q", "def_explicit_q"])
def def_implicit_q(context, state, x_variable_binding, h_rstr, h_body):
    state = state.set_variable_data(x_variable_binding.variable.name,
                                    quantifier=VariableCriteria(context.current_predication(),
                                                                x_variable_binding.variable.name,
                                                                min_size=1,
                                                                max_size=float('inf')))

    yield from quantifier_raw(context, state, x_variable_binding, h_rstr, h_body)


@Predication(vocabulary, names=["unknown+ignore"])
def unknown_ignore(context, state, e_introduced_binding, x_binding):
    yield state


@Predication(vocabulary, names=["_anymore_a_1"])
def _anymore_a_1(context, state, e_introduced_binding, e_binding):
    yield state


@Predication(vocabulary, names=["_just_a_1"])
def _just_a_1(context, state, e_introduced_binding, e_binding):
    yield state


@Predication(vocabulary, names=["_just_a_1"])
def _just_a_1(context, state, e_introduced_binding, x_binding):
    yield state


@Predication(vocabulary, names=["_just_x_deg"])
def _just_x_deg(context, state, e_introduced_binding, u_binding):
    yield state


@Predication(vocabulary, names=["_both_a_1"])
def _both_a_1(context, state, i_binding, e_binding):
    yield state


@Predication(vocabulary, names=["_well_a_1"])
def _well_a_1(context, state, i_introduced_binding, h_binding):
    yield from context.call(state, h_binding)


@Predication(vocabulary, names=["_please_a_1"])
def _please_a_1_scopal(context, state, i_binding, h_binding):
    yield from context.call(state, h_binding)


@Predication(vocabulary, names=["_please_a_1"])
def _please_a_1(context, state, e_introduced_binding, e_binding):
    yield state

@Predication(vocabulary, names=["_too_a_also"])
def _too_a_also(context, state, e_introduced_binding, x_binding):
    yield state


@Predication(vocabulary, names=["_please_v_1"])
def _please_v_1(context, state, e_introduced_binding, i_binding1, i_binding2):
    yield state


@Predication(vocabulary, names=["polite"])
def polite(context, state, c_arg, i_binding, e_binding):
    yield state


@Predication(vocabulary, names=["_thanks_a_1", "_then_a_1"])
def _thanks_a_1(context, state, i_binding, h_binding):
    yield from context.call(state, h_binding)


# Simply interpret "start with" as "want
@Predication(vocabulary,
             names=["_start_v_1_request", "_start_v_1_able"],
             phrases={
                 "I would like to start with a steak":  {'SF': 'prop', 'TENSE': 'tensed', 'MOOD': 'indicative', 'PROG': '-', 'PERF': '-'},
                 "I want to start with a steak":        {'SF': 'prop', 'TENSE': 'pres', 'MOOD': 'indicative', 'PROG': '-', 'PERF': '-'},
                 "Could I start with a steak?":         {'SF': 'ques', 'TENSE': 'tensed', 'MOOD': 'indicative', 'PROG': '-', 'PERF': '-'},
                 "Can I start with a steak?": {'SF': 'ques', 'TENSE': 'pres', 'MOOD': 'indicative', 'PROG': '-', 'PERF': '-'}
             },
             properties=[
                {'SF': 'prop', 'TENSE': ['pres', 'tensed'], 'MOOD': 'indicative', 'PROG': '-', 'PERF': '-'},
                {'SF': 'ques', 'TENSE': ['pres', 'tensed'], 'MOOD': 'indicative', 'PROG': '-', 'PERF': '-'}
             ],
             arguments=[("e",), ("x", ValueSize.all)],
             handles=[("With", EventOption.required)])
def _start_v_1_with_request(context, state, e_binding, x_actor_binding):
    variable_data = VariableData(e_binding.value["With"]["VariableName"])
    x_object_binding = VariableBinding(variable_data, (e_binding.value["With"]["Value"], ))

    variable_data_e = VariableData(e_binding.variable.name)
    want_e_binding = VariableBinding(variable_data_e, copy.deepcopy(e_binding.value))
    want_e_binding.value.pop("With")

    for item in want_v_1_helper(context, state, want_e_binding, x_actor_binding, x_object_binding):
        yield item


@Predication(vocabulary,
             names=["solution_group__start_v_1_request", "solution_group__start_v_1_able"],
             properties_from=_start_v_1_with_request)
def solution_group__start_v_1_request(context, state_list, e_introduced_binding_list, x_actor_variable_group):
    x_what_variable_name = e_introduced_binding_list.solution_values[0].value["With"]["VariableName"]
    yield from want_group_helper(context, state_list, e_introduced_binding_list, x_actor_variable_group, create_group_variable_values(context, state_list, x_what_variable_name))


@Predication(vocabulary,
             names=["_start_v_1"],
             phrases={
                 "Let's start with a steak": {'SF': 'comm', 'TENSE': 'pres', 'MOOD': 'indicative', 'PROG': '-', 'PERF': '-'},
                 "I will start with a steak": {'SF': 'prop', 'TENSE': 'fut', 'MOOD': 'indicative', 'PROG': '-', 'PERF': '-'}
             },
             properties=[
                {'SF': 'prop', 'TENSE': 'fut', 'MOOD': 'indicative', 'PROG': '-', 'PERF': '-'},
                {'SF': 'comm', 'TENSE': 'pres', 'MOOD': 'indicative', 'PROG': '-', 'PERF': '-'}
                ],
             arguments=[("e",), ("x", ValueSize.all)],
             handles=[("With", EventOption.required)])
def _start_v_1_order(context, state, e_binding, x_actor_binding):
    variable_data = VariableData(e_binding.value["With"]["VariableName"])
    x_object_binding = VariableBinding(variable_data, (e_binding.value["With"]["Value"],))

    variable_data_e = VariableData(e_binding.variable.name)
    have_e_binding = VariableBinding(variable_data_e, copy.deepcopy(e_binding.value))
    have_e_binding.value.pop("With")

    yield from _have_v_1_order(context, state, have_e_binding, x_actor_binding, x_object_binding)


@Predication(vocabulary,
             names=["solution_group__start_v_1"],
             properties_from=_start_v_1_order)
def _start_v_1_order_group(context, state_list, e_variable_group, x_actor_variable_group):
    x_what_variable_name = e_variable_group.solution_values[0].value["With"]["VariableName"]
    yield from _have_v_1_order_group(context, state_list, e_variable_group, x_actor_variable_group, create_group_variable_values(context, state_list, x_what_variable_name))



@Predication(vocabulary,
             names=["_sit_v_down", "_sit_v_1"],
             phrases={
                "I will sit down.": {'SF': 'prop', 'TENSE': 'fut', 'MOOD': 'indicative', 'PROG': '-', 'PERF': '-'},
                "I will sit.": {'SF': 'prop', 'TENSE': 'fut', 'MOOD': 'indicative', 'PROG': '-', 'PERF': '-'}
             },
             properties=[
                {'SF': 'prop', 'TENSE': 'fut', 'MOOD': 'indicative', 'PROG': '-', 'PERF': '-'}
             ])
def _sit_v_down_future(context, state, e_introduced_binding, x_actor_binding):
    if is_concept(x_actor_binding):
        context.report_error(["formNotUnderstood", "_sit_v_down_future"])
        return

    def bound(x_actor):
        if is_user_type(x_actor):
            return True

        else:
            context.report_error(["unexpected"])
            return

    def unbound():
        context.report_error(["unexpected", "_sit_v_down_future"])
        if False:
            yield None

    yield from combinatorial_predication_1(context, state, x_actor_binding, bound, unbound)


@Predication(vocabulary,
             names=["_sit_v_down", "_sit_v_1"],
             phrases={
                "Will I sit down?": {'SF': 'ques', 'TENSE': 'fut', 'MOOD': 'indicative', 'PROG': '-', 'PERF': '-'},
                "Will I sit?": {'SF': 'ques', 'TENSE': 'fut', 'MOOD': 'indicative', 'PROG': '-', 'PERF': '-'}
             },
             properties=[
                {'SF': 'ques', 'TENSE': 'fut', 'MOOD': 'indicative', 'PROG': '-', 'PERF': '-'}
             ])
def _sit_v_down_future_bad_english(context, state, e_introduced_binding, x_actor_binding):
    context.report_error(["unexpected"])
    if False:
        yield None


@Predication(vocabulary, names=["solution_group__sit_v_down", "solution_group__sit_v_1"])
def _sit_v_down_future_group(context, state_list, e_list, x_actor_variable_group):
    # The planner will only satisfy a want wrt the players
    task = ('satisfy_want', context, variable_group_values_to_list(x_actor_variable_group), [[ESLConcept("table")]], 1)
    final_state = do_task(state_list[0].world_state_frame(), [task])
    if final_state:
        yield [final_state]



@Predication(vocabulary,
             names=["_sit_v_down", "_sit_v_1", "_sit_v_down_able", "_sit_v_1_able"],
             phrases={
                "I can sit.": {'SF': 'prop', 'TENSE': 'pres', 'MOOD': 'indicative', 'PROG': '-', 'PERF': '-'},
                "I sit down": {'SF': 'prop', 'TENSE': 'pres', 'MOOD': 'indicative', 'PROG': '-', 'PERF': '-'},
                "Who sits down?": {'SF': 'ques', 'TENSE': 'pres', 'MOOD': 'indicative', 'PROG': '-', 'PERF': '-'},
                "Who is sitting down?": {'SF': 'ques', 'TENSE': 'pres', 'MOOD': 'indicative', 'PROG': '+', 'PERF': '-'},
                "I sit": {'SF': 'prop', 'TENSE': 'pres', 'MOOD': 'indicative', 'PROG': '-', 'PERF': '-'},
                "I can sit down.": {'SF': 'prop', 'TENSE': 'pres', 'MOOD': 'indicative', 'PROG': '-', 'PERF': '-'}
             },
             properties=[
                {'SF': ['prop', 'ques'], 'TENSE': 'pres', 'MOOD': 'indicative', 'PROG': '-', 'PERF': '-'},
                {'SF': 'ques', 'TENSE': 'pres', 'MOOD': 'indicative', 'PROG': '+', 'PERF': '-'}
             ])
def _sit_v_present_intransitive_bad_english(context, state, e_introduced_binding, x_actor_binding):
    if not is_present_tense(state.get_binding("tree").value[0]):
        context.report_error(["formNotUnderstood", "invalid_present_intransitive"])
        return

    context.report_error(["unexpected"])
    if False:
        yield None


# Scenarios:
#   - "Can I sit down?" "Can I sit?" --> request for table
#   - "Who can sit down?"
#
#   Poor English:
#   - "I can sit down."
@Predication(vocabulary,
             names=["_sit_v_down_able", "_sit_v_1_able"],
             phrases={
                "Can I sit down?": {'SF': 'ques', 'TENSE': 'pres', 'MOOD': 'indicative', 'PROG': '-', 'PERF': '-'},
                "Can I sit?": {'SF': 'ques', 'TENSE': 'pres', 'MOOD': 'indicative', 'PROG': '-', 'PERF': '-'},
                "Who can sit down?": {'SF': 'ques', 'TENSE': 'pres', 'MOOD': 'indicative', 'PROG': '-', 'PERF': '-'}
             },
             properties=[
                {'SF': 'ques', 'TENSE': 'pres', 'MOOD': 'indicative', 'PROG': '-', 'PERF': '-'}
             ],
             arguments=[("e",), ("x", ValueSize.all)])
def _sit_v_down_able(context, state, e_binding, x_actor_binding):
    if is_concept(x_actor_binding):
        context.report_error(["formNotUnderstood", "_sit_v_down_able"])
        return

    def bound(x_actor):
        if is_user_type(x_actor):
            return True

        else:
            context.report_error(["unexpected"])
            return

    def unbound():
        yield "user"

    yield from combinatorial_predication_1(context, state, x_actor_binding, bound, unbound)


@Predication(vocabulary,
             names=["_sit_v_down_request", "_sit_v_1_request"],
             phrases={
                 "I would like to sit": {'SF': 'prop', 'TENSE': 'tensed', 'MOOD': 'indicative', 'PROG': '-', 'PERF': '-'},
                 "we want to sit down": {'SF': 'prop', 'TENSE': 'pres', 'MOOD': 'indicative', 'PROG': '-', 'PERF': '-'},
                 "we want to sit": {'SF': 'prop', 'TENSE': 'pres', 'MOOD': 'indicative', 'PROG': '-', 'PERF': '-'}
             },
             properties=[
                {'SF': 'prop', 'TENSE': ['pres', 'tensed'], 'MOOD': 'indicative', 'PROG': '-', 'PERF': '-'}
             ],
             arguments=[("e",), ("x", ValueSize.all)])
def _sit_v_down_request(context, state, e_binding, x_actor_binding):
    if is_concept(x_actor_binding):
        context.report_error(["formNotUnderstood", "_sit_v_down_request"])
        return

    def bound(x_actor):
        if is_user_type(x_actor):
            return True

        else:
            context.report_error(["unexpected"])
            return

    def unbound():
        yield "user"

    yield from combinatorial_predication_1(context, state, x_actor_binding, bound, unbound)


@Predication(vocabulary,
             names=["solution_group__sit_v_down_able", "solution_group__sit_v_1_able", "solution_group__sit_v_down_request", "solution_group__sit_v_1_request"])
def _sit_v_down_able_group(context, state_list, e_introduced_binding_list, x_actor_variable_group):
    # If it is a wh_question, just answer it
    tree_info = state_list[0].get_binding("tree").value[0]
    if is_wh_question(tree_info):
        yield state_list

    else:
        # 'satisfy_want' understands ("user", "son") want (table) as meaning they want a table *together*
        actors = variable_group_values_to_list(x_actor_variable_group)
        task = ('satisfy_want', context, actors, [(ESLConcept("table"),)] * len(actors), 1)
        final_state = do_task(state_list[0].world_state_frame(), [task])
        if final_state:
            yield [final_state]


@Predication(vocabulary,
             names=["_eat_v_1", "_eat_v_1_request"],
             phrases={
                "eat now": {'SF': 'comm', 'TENSE': 'pres', 'MOOD': 'indicative', 'PROG': '-', 'PERF': '-'},
                "let's eat": {'SF': 'comm', 'TENSE': 'pres', 'MOOD': 'indicative', 'PROG': '-', 'PERF': '-'},
                "I want to eat": {'SF': 'prop', 'TENSE': 'pres', 'MOOD': 'indicative', 'PROG': '-', 'PERF': '-'}
             },
             properties=[
                {'SF': 'comm', 'TENSE': 'pres', 'MOOD': 'indicative', 'PROG': '-', 'PERF': '-'},
                {'SF': 'prop', 'TENSE': 'pres', 'MOOD': 'indicative', 'PROG': '-', 'PERF': '-'}
             ],
             arguments=[("e",), ("x", ValueSize.all), ("i", ValueSize.exactly_one)]
             )
def _eat_v_1_command(context, state, e_introduced_binding, x_actor_binding, i_unused_binding):
    def bound(val):
        if is_user_type(val):
            return True
        else:
            context.report_error(["unexpected"])
            return False

    def unbound():
        context.report_error(["unexpected"])
        if False:
            yield None

    yield from combinatorial_predication_1(context, state, x_actor_binding, bound, unbound)


@Predication(vocabulary,
             names=["solution_group__eat_v_1", "solution_group__eat_v_1_request"],
             properties_from=_eat_v_1_command)
def _eat_v_1_command_group(context, state_list, e_list, x_actor_variable_group, i_unused_variable_group):
    # The only valid scenario is "let's eat" so ...
    actor_group_values = variable_group_values_to_list(x_actor_variable_group)
    what_group_values = [(ESLConcept("dish"), )] * len(actor_group_values)
    task = ('satisfy_want',
            context,
            actor_group_values,
            what_group_values,
            1)
    final_state = do_task(state_list[0].world_state_frame(), [task])
    if final_state:
        yield [final_state]

    else:
        context.report_error(["formNotUnderstood"])
        return


@Predication(vocabulary,
             names=["_eat_v_1_request"],
             phrases={
                 "I want to eat":  {'SF': 'prop', 'TENSE': 'pres', 'MOOD': 'indicative', 'PROG': '-', 'PERF': '-'},
                 "we want to eat lunch": {'SF': 'prop', 'TENSE': 'pres', 'MOOD': 'indicative', 'PROG': '-', 'PERF': '-'}
             },
             properties=[
                {'SF': 'prop', 'TENSE': 'pres', 'MOOD': 'indicative', 'PROG': '-', 'PERF': '-'}
             ])
def _eat_v_1_request(context, state, e_introduced_binding, x_actor_binding, x_object_binding):
    if x_actor_binding.value is not None and len(x_actor_binding.value) == 1 and x_actor_binding.value[0] == "restaurant":
        # Don't support "You want to eat"
        context.report_error(["unexpected"])
        return

    # All other combinations are OK
    yield from want_v_1_helper(context, state, e_introduced_binding, x_actor_binding, x_object_binding)


@Predication(vocabulary,
             names=["solution_group__eat_v_1_request"],
             properties_from=_eat_v_1_request)
def _eat_v_1_request_group(context, state_list, e_introduced_binding_list, x_actor_variable_group, x_what_variable_group):
    yield from want_group_helper(context, state_list, e_introduced_binding_list, x_actor_variable_group, x_what_variable_group)


@Predication(vocabulary,
             names=["_see_v_1_able"],
             phrases={
                "Can I see a menu?":   {'SF': 'ques', 'TENSE': 'pres', 'MOOD': 'indicative', 'PROG': '-', 'PERF': '-'},  # -> implied request
                "Could I see a menu?": {'SF': 'ques', 'TENSE': 'tensed', 'MOOD': 'indicative', 'PROG': '-', 'PERF': '-'}
             },
             properties=[
                {'SF': 'ques', 'TENSE': 'pres', 'MOOD': 'indicative', 'PROG': '-', 'PERF': '-'},
                {'SF': 'ques', 'TENSE': 'tensed', 'MOOD': 'indicative', 'PROG': '-', 'PERF': '-'}
             ])
def _see_v_1_able(context, state, e_introduced_binding, x_actor_binding, x_object_binding):
    def both_bound_prediction_function(x_actor, x_object):
        if is_user_type(x_actor):
            if valid_player_request(context, state, [x_object], [ESLConcept("menu")]):
                return True
            else:
                context.report_error(["unexpected"])
                return False

        else:
            # Anything about "you/they will have" is not good english
            context.report_error(["unexpected"])
            return False

    def actor_unbound(x_object):
        # Anything about "what will x have
        context.report_error(["unexpected"])
        if False:
            yield None

    def object_unbound(x_actor):
        context.report_error(["unexpected"])
        if False:
            yield None

    yield from in_style_predication_2(context, state, x_actor_binding, x_object_binding,
                                      both_bound_prediction_function,
                                      actor_unbound,
                                      object_unbound)


@Predication(vocabulary,
             names=["_see_v_1_able"],
             phrases={
                "I can see a menu": {'SF': 'prop', 'TENSE': 'pres', 'MOOD': 'indicative', 'PROG': '-', 'PERF': '-'}  # -> implied request
             },
             properties=[
                {'SF': 'prop', 'TENSE': 'pres', 'MOOD': 'indicative', 'PROG': '-', 'PERF': '-'}
             ])
def _see_v_1_able_bad_english(context, state, e_introduced_binding, x_actor_binding, x_object_binding):
    if False:
        yield None
    context.report_error(["unexpected"])
    return


@Predication(vocabulary,
             names=["solution_group__see_v_1_able"],
             properties_from=_see_v_1_able)
def _see_v_1_able_group(context, state_list, e_list, x_actor_variable_group, x_object_variable_group):
    # The only valid scenarios for will have are requests, so ...
    # The planner will only satisfy a want wrt the players
    task = ('satisfy_want',
            context,
            variable_group_values_to_list(x_actor_variable_group),
            variable_group_values_to_list(x_object_variable_group),
            min_from_variable_group(x_object_variable_group))
    final_state = do_task(state_list[0].world_state_frame(), [task])
    if final_state:
        yield [final_state]

    else:
        context.report_error(["formNotUnderstood"])
        return


# Scenarios:
#   "I/we will see a menu" -> implied request
#   Poor English:
#       "I will see a table/steak, etc"
@Predication(vocabulary,
             names=["_see_v_1"],
             phrases={
                 "I|we will see a menu": {'SF': 'prop', 'TENSE': 'fut', 'MOOD': 'indicative', 'PROG': '-', 'PERF': '-'}
             },
             properties=[{'SF': 'prop', 'TENSE': 'fut', 'MOOD': 'indicative', 'PROG': '-', 'PERF': '-'}])
def _see_v_1_future(context, state, e_introduced_binding, x_actor_binding, x_object_binding):
    def both_bound_prediction_function(x_actor, x_object):
        if is_user_type(x_actor):
            if valid_player_request(context, state, [x_object], [ESLConcept("menu")]):
                return True
            else:
                context.report_error(["unexpected"])
                return False

        else:
            # Anything about "you/they will have" is not good english
            context.report_error(["unexpected"])
            return False

    def actor_unbound(x_object):
        # Anything about "what will x have
        context.report_error(["unexpected"])
        if False:
            yield None

    def object_unbound(x_actor):
        context.report_error(["unexpected"])
        if False:
            yield None

    yield from in_style_predication_2(context, state, x_actor_binding, x_object_binding,
                                      both_bound_prediction_function,
                                      actor_unbound,
                                      object_unbound)


@Predication(vocabulary,
             names=["_see_v_1"],
             phrases={
                 "I|we will see a menu?": {'SF': 'ques', 'TENSE': 'fut', 'MOOD': 'indicative', 'PROG': '-', 'PERF': '-'}
             },
             properties=[{'SF': 'ques', 'TENSE': 'fut', 'MOOD': 'indicative', 'PROG': '-', 'PERF': '-'}])
def _see_v_1_future_bad_english(context, state, e_introduced_binding, x_actor_binding, x_object_binding):
    if False:
        yield None
    context.report_error(["unexpected"])


@Predication(vocabulary,
             names=["solution_group__see_v_1"],
             properties_from=_see_v_1_future)
def _see_v_1_future_group(context, state_list, e_list, x_actor_variable_group, x_object_variable_group):
    # The only valid scenarios for will have are requests, so ...
    # The planner will only satisfy a want wrt the players
    task = ('satisfy_want',
            context,
            variable_group_values_to_list(x_actor_variable_group),
            variable_group_values_to_list(x_object_variable_group),
            min_from_variable_group(x_object_variable_group))
    final_state = do_task(state_list[0].world_state_frame(), [task])
    if final_state:
        yield [final_state]

    else:
        context.report_error(["formNotUnderstood"])
        return


@Predication(vocabulary,
             names=["_take_v_1_able"],
             phrases={
                "Can I take a menu?": {'SF': 'ques', 'TENSE': 'pres', 'MOOD': 'indicative', 'PROG': '-', 'PERF': '-'},
                "I can take a menu.": {'SF': 'prop', 'TENSE': 'pres', 'MOOD': 'indicative', 'PROG': '-', 'PERF': '-'}
             },
             properties=[
                {'SF': ['ques', 'prop'], 'TENSE': 'pres', 'MOOD': 'indicative', 'PROG': '-', 'PERF': '-'}
             ])
def _take_v_1_able(context, state, e_introduced_binding, x_actor_binding, x_object_binding):
    context.report_error(["unexpected"])
    if False:
        yield None


# Present tense scenarios: all of these are not great english, respond with an error
#   "I get x?", "I get x"
#   "I see a menu?"
#   "I see a menu"
@Predication(vocabulary,
             names=["_get_v_1", "_take_v_1", "_see_v_1"],
             phrases={
                "I get|take a menu?": {'SF': 'ques', 'TENSE': 'pres', 'MOOD': 'indicative', 'PROG': '-', 'PERF': '-'},
                "I get|take a menu": {'SF': 'prop', 'TENSE': 'pres', 'MOOD': 'indicative', 'PROG': '-', 'PERF': '-'},
                "I see a menu?": {'SF': 'ques', 'TENSE': 'pres', 'MOOD': 'indicative', 'PROG': '-', 'PERF': '-'},
                "I see a menu": {'SF': 'prop', 'TENSE': 'pres', 'MOOD': 'indicative', 'PROG': '-', 'PERF': '-'}
             },
             properties=[
                {'SF': ['ques', 'prop'], 'TENSE': 'pres', 'MOOD': 'indicative', 'PROG': '-', 'PERF': '-'}
             ])
def get_take_see_v_present_transitive_bad_english(context, state, e_introduced_binding, x_actor_binding, x_object_binding):
    if not is_present_tense(state.get_binding("tree").value[0]):
        context.report_error(["formNotUnderstood", "invalid_present_transitive"])
        return
    context.report_error(["unexpected"])
    if False:
        yield None


@Predication(vocabulary,
             names=["_cancel_v_1"],
             phrases={
                 "I don't want a salad": {'SF': 'prop', 'TENSE': 'pres', 'MOOD': 'indicative', 'PROG': '-', 'PERF': '-'},
                 "Cancel my steak": {'SF': 'comm', 'TENSE': 'pres', 'MOOD': 'indicative', 'PROG': '-', 'PERF': '-'}
             },
             properties={'SF': ['comm', 'prop'], 'TENSE': 'pres', 'MOOD': 'indicative', 'PROG': '-', 'PERF': '-'})
def _cancel_v_1(context, state, e_introduced_binding, x_actor_binding, x_object_binding):
    yield from _cancel_helper(context, state, e_introduced_binding, x_actor_binding, x_object_binding)


@Predication(vocabulary,
             names=["solution_group__cancel_v_1"],
             properties_from=_cancel_v_1)
def _cancel_v_1_group(context, state_list, e_introduced_binding_list, x_actor_variable_group, x_what_variable_group):
    yield from cancel_group_helper(context, state_list, e_introduced_binding_list, x_actor_variable_group, x_what_variable_group)


@Predication(vocabulary,
             names=["_cancel_v_1_request"],
             phrases={
                 "I want to cancel my order":  {'SF': 'prop', 'TENSE': 'pres', 'MOOD': 'indicative', 'PROG': '-', 'PERF': '-'},
                 "I'd like to cancel my steak": {'SF': 'prop', 'TENSE': 'untensed', 'MOOD': 'indicative', 'PROG': '-', 'PERF': '-'}
             },
             properties={'SF': 'prop', 'TENSE': ['pres', 'untensed'], 'MOOD': 'indicative', 'PROG': '-', 'PERF': '-'})
def _cancel_v_1_request(context, state, e_introduced_binding, x_actor_binding, x_object_binding):
    if x_actor_binding.value is not None and len(x_actor_binding.value) == 1 and x_actor_binding.value[0] == "restaurant":
        # Don't support "You want to cancel my order"
        context.report_error(["unexpected"])
        return

    # All other combinations are OK
    yield from _cancel_helper(context, state, e_introduced_binding, x_actor_binding, x_object_binding)


@Predication(vocabulary,
             names=["solution_group__cancel_v_1_request"],
             properties_from=_cancel_v_1_request)
def _cancel_v_1_request_group(context, state_list, e_introduced_binding_list, x_actor_variable_group, x_what_variable_group):
    yield from cancel_group_helper(context, state_list, e_introduced_binding_list, x_actor_variable_group, x_what_variable_group)


@Predication(vocabulary,
             names=["_cancel_v_1_able"],
             phrases={
                 "Could I cancel my order?":  {'SF': 'ques', 'TENSE': 'tensed', 'MOOD': 'indicative', 'PROG': '-', 'PERF': '-'},
                 "Can I cancel my order?":  {'SF': 'ques', 'TENSE': 'pres', 'MOOD': 'indicative', 'PROG': '-', 'PERF': '-'}
             },
             properties={'SF': 'ques', 'TENSE': ['pres', 'tensed'], 'MOOD': 'indicative', 'PROG': '-', 'PERF': '-'})
def _cancel_v_1_able(context, state, e_introduced_binding, x_actor_binding, x_object_binding):
    yield from _cancel_helper(context, state, e_introduced_binding, x_actor_binding, x_object_binding)


# "Cancel the steak"
# "Cancel the order" --> means cancel both orders
# "Cancel my steak"
# "Cancel our steaks"
def _cancel_helper(context, state, e_introduced_binding, x_actor_binding, x_object_binding):
    def bound(x_actor, x_object):
        # We support "Can/Could I/we/you cancel my/Johnnys [order | thing you can order]"
        if (is_user_type(x_actor) or is_computer_type(x_actor)) and is_concept(x_object) and x_object.entails_which(context, state, cancellable):
            return True

        else:
            context.report_error(["dontKnowHow"])

    def actor_from_object(x_object):
        if False:
            yield None

    def object_from_actor(x_actor):
        if False:
            yield None

    cancellable = orderable_concepts(state) + [ESLConcept("order")]
    yield from in_style_predication_2(context, state, x_actor_binding, x_object_binding, bound, actor_from_object, object_from_actor)


@Predication(vocabulary,
             names=["solution_group__cancel_v_1_able"],
             properties_from=_cancel_v_1_able)
def _cancel_v_1_able_group(context, state_list, e_introduced_binding_list, x_actor_variable_group, x_what_variable_group):
    yield from cancel_group_helper(context, state_list, e_introduced_binding_list, x_actor_variable_group, x_what_variable_group)


def cancel_group_helper(context, state_list, e_introduced_binding_list, x_actor_variable_group, x_what_variable_group):
    current_state = copy.deepcopy(state_list[0])
    if is_concept(x_actor_variable_group.solution_values[0]):
        # This solution group handler requires non-conceptual actors
        context.report_error(["formNotUnderstood"])
        return

    # In fact, we *never* deal with cancelling a particular instance because that would mean "I don't wnat that particular steak right there"
    # and we don't support that
    # These are concepts. Only need to check the first because:
    # If one item in the group is a concept, they all are
    # x_what_variable_group.solution_values[0].value can be None if it is scoped under negation
    if x_what_variable_group.solution_values[0].value is not None and is_concept(x_what_variable_group.solution_values[0].value[0]):
        concept = x_what_variable_group.solution_values[0].value[0]

        # Checking to make sure the constraints are valid for this concept
        # is done in the planner
        # Even though it is only one type of thing, they could have said something like "We want steaks"
        # so they really want more than one instance
        what_list = variable_group_values_to_list(x_what_variable_group)
        actor_list = [[None]] * len(what_list)
        current_state = do_task(current_state.world_state_frame(),
                                [('cancel',
                                  context,
                                  actor_list,
                                  what_list,
                                  min_from_variable_group(x_what_variable_group))])
        if current_state:
            yield [current_state]

    else:
        # This handler doesn't deal with wants of instances, but others might
        context.report_error(["formNotUnderstood"])
        return



# Translates to "I want X"
@Predication(vocabulary,
             names=["_order_v_1"],
             phrases={
                "I will order a steak":  {'SF': 'prop', 'TENSE': 'fut', 'MOOD': 'indicative', 'PROG': '-', 'PERF': '-'}
             },
             properties={'SF': 'prop', 'TENSE': 'fut', 'MOOD': 'indicative', 'PROG': '-', 'PERF': '-'})
def _order_v_1_future(context, state, e_introduced_binding, x_actor_binding, x_object_binding):
    yield from want_v_1_helper(context, state, e_introduced_binding, x_actor_binding, x_object_binding)


@Predication(vocabulary,
             names=["solution_group__order_v_1"],
             properties_from=_order_v_1_future)
def _order_v_1_future_group(context, state_list, e_introduced_binding_list, x_actor_variable_group, x_what_variable_group):
    yield from want_group_helper(context, state_list, e_introduced_binding_list, x_actor_variable_group, x_what_variable_group)



@Predication(vocabulary,
             names=["_order_v_1"],
             phrases={
                "What did I order?": {'SF': 'ques', 'TENSE': 'past', 'MOOD': 'indicative', 'PROG': '-', 'PERF': '-'},
                "I ordered a steak":  {'SF': 'prop', 'TENSE': 'past', 'MOOD': 'indicative', 'PROG': '-', 'PERF': '-'},
                "how much soup did I order?": {'SF': 'ques', 'TENSE': 'past', 'MOOD': 'indicative', 'PROG': '-', 'PERF': '-'}
             },
             properties={'SF': ['ques', 'prop'], 'TENSE': 'past', 'MOOD': 'indicative', 'PROG': '-', 'PERF': '-'})
def _order_v_1_past(context, state, e_introduced_binding, x_actor_binding, x_object_binding):
    predicately = used_predicatively(context, state)
    if not predicately or (used_predicatively(context, state) and (is_concept(x_actor_binding) or is_concept(x_object_binding))):
        # Must be used predicately and when used as a predicate these must be instances
        context.report_error(["formNotUnderstood", "_order_v_1_past"])
        return

    def bound(x_actor, x_object):
        if rel_check(state, x_actor, "ordered", x_object):
            return True

        else:
            context.report_error(["verbDoesntApplyArg", x_actor_binding.variable.name, "order", x_object_binding.variable.name])
            return False

    def actor_from_object(x_object):
        # "Who ordered X?"
        found = False
        for i in rel_subjects(state, "ordered", x_object):
            found = True
            yield store_to_object(state, i)

        if not found:
            context.report_error(["nothing_verb_x", x_actor_binding.variable.name, "ordered", x_object_binding.variable.name])

    def object_from_actor(x_actor):
        # "what did I order?"
        found = False
        for i in rel_objects(state, x_actor, "ordered"):
            found = True
            yield store_to_object(state, i)

        if not found:
            context.report_error(["x_verb_nothing", x_actor_binding.variable.name, "ordered"])

    yield from in_style_predication_2(context, state, x_actor_binding, x_object_binding, bound, actor_from_object,
                                      object_from_actor)



@Predication(vocabulary,
             names=["_get_v_1"],
             phrases={
                 "Get a steak for me": {'SF': 'comm', 'TENSE': 'pres', 'MOOD': 'indicative', 'PROG': '-', 'PERF': '-'}
             },
             properties=[
                {'SF': 'comm', 'TENSE': 'pres', 'MOOD': 'indicative', 'PROG': '-', 'PERF': '-'}
                ],
             arguments=[("e",), ("x", ValueSize.all), ("x", ValueSize.all)],
             handles=[("for", EventOption.optional)])
def _get_v_1_command(context, state, e_introduced_binding, x_actor_binding, x_object_binding):
    def both_bound_prediction_function(x_actor, x_object):
        nonlocal for_type, x_what_type

        if is_computer_type(x_actor) and valid_player_request(context, state, [x_object]):
            if e_introduced_binding.value is not None and "for" in e_introduced_binding.value:
                for_list = e_introduced_binding.value["for"]["Value"]
                result, for_type, x_what_type = for_check(context, state, [x_object], for_list)
                return result
            else:
                return True

    def actor_unbound(x_object):
        # Anything about "Who gets x?"
        context.report_error(["unexpected"])
        if False:
            yield None

    def object_unbound(x_actor):
        # "What can you get?"
        context.report_error(["unexpected"])
        if False:
            yield None

    # These get set by each call to in_style_predication_2
    for_type = None
    x_what_type = None
    for new_state in in_style_predication_2(context, state, x_actor_binding, x_object_binding,
                                            both_bound_prediction_function,
                                            actor_unbound,
                                            object_unbound):
        if e_introduced_binding.value is not None and "for" in e_introduced_binding.value:
            for_list = e_introduced_binding.value["for"]["Value"]
            for_binding = e_introduced_binding.value["for"]["Binding"]
            yield for_update_state(context, new_state, x_what_type, for_type, x_object_binding, for_binding, for_list)
        else:
            yield new_state


@Predication(vocabulary,
             names=["solution_group__get_v_1"],
             properties_from=_get_v_1_command)
def _get_v_1_command_group(context, state_list, e_variable_group, x_actor_variable_group, x_object_variable_group):
    actor_list = variable_group_values_to_list(x_actor_variable_group)
    if not is_computer_type(actor_list[0]):
        context.report_error(["formNotUnderstood"])
        return

    object_list = variable_group_values_to_list(x_object_variable_group)
    actor_list = [("user", )] * len(object_list)
    task = ('satisfy_want',
            context,
            actor_list,
            object_list,
            min_from_variable_group(x_object_variable_group))
    final_state = do_task(state_list[0].world_state_frame(), [task])
    if final_state:
        yield [final_state]

    else:
        context.report_error(["formNotUnderstood"])
        return


# Handle "I will have a steak/menu/table." as an implied order
#
# All the question forms aren't handled:
#   - "I will have a steak/menu/table?" --> Not good english
#   - "Will I have a steak/menu/table?" --> Not good english
#   - "Will you have a table?" --> Not good english
#   - "What will I have?" --> Not good english
#   - "Who will have x?" --> Not good english
@Predication(vocabulary,
             names=["_have_v_1", "_take_v_1", "_get_v_1"],
             phrases={
                 "Let's take|have|get a steak": {'SF': 'comm', 'TENSE': 'pres', 'MOOD': 'indicative', 'PROG': '-', 'PERF': '-'},
                 "I will take|have|get a steak": {'SF': 'prop', 'TENSE': 'fut', 'MOOD': 'indicative', 'PROG': '-', 'PERF': '-'}
             },
             properties=[
                {'SF': 'prop', 'TENSE': 'fut', 'MOOD': 'indicative', 'PROG': '-', 'PERF': '-'},
                {'SF': 'comm', 'TENSE': 'pres', 'MOOD': 'indicative', 'PROG': '-', 'PERF': '-'}
                ],
             arguments=[("e",), ("x", ValueSize.all), ("x", ValueSize.all)],
             handles=[("for", EventOption.optional)])
def _have_v_1_order(context, state, e_introduced_binding, x_actor_binding, x_object_binding):
    def both_bound_prediction_function(x_actors, x_objects):
        nonlocal for_type, x_what_type

        if is_user_type(x_actors):
            if valid_player_request(context, state, x_objects):
                if e_introduced_binding.value is not None and "for" in e_introduced_binding.value:
                    # Let's get soup for Johnny"
                    for_list = e_introduced_binding.value["for"]["Value"]
                    result, for_type, x_what_type = for_check(context, state, x_objects, for_list)
                    return result

                else:
                    return True

            else:
                return False

        else:
            # Anything about "you/they will have" is not good english
            context.report_error(["unexpected"])
            return False

    def actor_unbound(x_object):
        # Anything about "what will x have?"
        context.report_error(["unexpected"])
        if False:
            yield None

    def object_unbound(x_actor):
        # "who will have x?"
        context.report_error(["unexpected"])
        if False:
            yield None

    # These get set by each call to lift_style_predication_2
    for_type = None
    x_what_type = None
    for new_state in lift_style_predication_2(context, state, x_actor_binding, x_object_binding,
                                                both_bound_prediction_function,
                                                actor_unbound,
                                                object_unbound):
        if e_introduced_binding.value is not None and "for" in e_introduced_binding.value:
            for_list = e_introduced_binding.value["for"]["Value"]
            for_binding = e_introduced_binding.value["for"]["Binding"]
            yield for_update_state(context, new_state, x_what_type, for_type, x_object_binding, for_binding, for_list)

        else:
            yield new_state


@Predication(vocabulary,
             names=["solution_group__have_v_1", "solution_group__take_v_1", "solution_group__get_v_1"],
             properties_from=_have_v_1_order,
             handles_interpretation=[_have_v_1_order, _start_v_1_order])
def _have_v_1_order_group(context, state_list, e_variable_group, x_actor_variable_group, x_object_variable_group):
    task = ('satisfy_want',
            context,
            variable_group_values_to_list(x_actor_variable_group),
            variable_group_values_to_list(x_object_variable_group),
            min_from_variable_group(x_object_variable_group))
    final_state = do_task(state_list[0].world_state_frame(), [task])
    if final_state:
        yield [final_state]


# Handle phrases of the form "Do you have ..."
#   Questions like "Do you have a (concept of a) table/menu/bill?" that ask about "having" a thing you could order directly
#       are implied requests for those things.  Implied requests are always of the form "you" (meaning "the restaurant")
#       and anything that could have been successfully asked for in the form, "I would like [x]"
#
#   Questions like "Do you have specials/meats/vegetarian items?" that entail multiple menu items
#       are implied requests for a menu
#
#   Both can also be of the form "what [x] do you have?"
#
# Note that "Do you have a menu?" will eventually try to solve "Do you have menu1?" (i.e. the menu1 instance)
# which is true and is the next have_v_1 interpretation.  But, because concepts come through first,
# we will hit this interpretation first and interpret it as an implied request
@Predication(vocabulary,
             names=["_have_v_1"],
             phrases={
                "Do you have a table?": {'SF': 'ques', 'TENSE': 'pres', 'MOOD': 'indicative', 'PROG': '-', 'PERF': '-'},          # --> implied table request
                "What do you have?": {'SF': 'ques', 'TENSE': 'pres', 'MOOD': 'indicative', 'PROG': '-', 'PERF': '-'},             # --> implied menu request
                "Do you have a|the menu|bill?": {'SF': 'ques', 'TENSE': 'pres', 'MOOD': 'indicative', 'PROG': '-', 'PERF': '-'},  # --> implied menu request
                "What specials do you have?": {'SF': 'ques', 'TENSE': 'pres', 'MOOD': 'indicative', 'PROG': '-', 'PERF': '-'},    # --> implied request for description of specials
                "Do you have a bill?": {'SF': 'ques', 'TENSE': 'pres', 'MOOD': 'indicative', 'PROG': '-', 'PERF': '-'},           # --> implied request, kind of
                "Do you have menus?": {'SF': 'ques', 'TENSE': 'pres', 'MOOD': 'indicative', 'PROG': '-', 'PERF': '-'},            # --> Could mean "do you have conceptual menus?" or "implied menu request and thus instance check"
                "Do you have steaks?": {'SF': 'ques', 'TENSE': 'pres', 'MOOD': 'indicative', 'PROG': '-', 'PERF': '-'}            # --> Could mean "do you have more than one preparation of steak" or "Do you have more than one instance of a steak"
             },
             properties={'SF': 'ques', 'TENSE': 'pres', 'MOOD': 'indicative', 'PROG': '-', 'PERF': '-'})
def _have_v_1_request_order(context, state, e_introduced_binding, x_actor_binding, x_object_binding):
    def bound(x_actor, x_object):
        # If they are asking if the restaurant "has" anything that they could request,
        # this is the interpretation
        if valid_player_request(context, state, [x_object]):
            return True

        else:
            # Because x_object is a concept (which is checked in the outer function),
            # This really is the function to handle it, none of the others are appropriate
            # and given that it isn't a valid thing to ask for
            context.report_error(["doesntExist", x_object_binding.variable.name])
            return False

    def actor_from_object(x_object):
        # "Who has a steak?" This is a very odd way to ask for a
        # steak so we assume it isn't a request and thus not handled here
        context.report_error(["formNotUnderstood", "_have_v_1_request_order"])
        if False:
            yield none

    def object_from_actor(x_actor):
        # "What do you [the restaurant] have?" --> request for a menu
        # We've already checked in the outer function if actor = restaurant, so ...
        yield ESLConcept("menu")

    # Must be an instance of an actor with a conceptual object (either can be unbound)
    if (x_actor_binding.value is not None and is_concept(x_actor_binding)) or (x_object_binding.value is not None and not is_concept(x_object_binding)):
        context.report_error(["formNotUnderstood", "_have_v_1_request_order"])
        return

    if (x_actor_binding.value is not None and (len(x_actor_binding.value) > 1 or x_actor_binding.value[0] != "restaurant")):
        context.report_error(["formNotUnderstood", "_have_v_1_request_order"])
        return

    yield from in_style_predication_2(context, state, x_actor_binding, x_object_binding, bound, actor_from_object,
                                      object_from_actor)


# The solution handler ensures that the actor is "restaurant" and that object is a concept and
# that the item is requestable
@Predication(vocabulary,
             names=["solution_group__have_v_1"],
             properties_from=_have_v_1_request_order,
             handles_interpretation=_have_v_1_request_order)
def _have_v_1_request_order_group(context, state_list, e_list, x_actor_variable_group, x_object_variable_group):
    # "Can I have a table/menu/bill?" is really about the instances thus check_concepts=False
    if not check_concept_solution_group_constraints(context, state_list, x_object_variable_group, check_concepts=False):
        return

    # If any of the items requested entail more than one menu item, interpret the request as asking for a menu.
    # For example: "Do you have vegetarian items?" or "Do you have things to drink?"
    orderable_list = orderable_concepts(state_list[0])
    all_bucketed_instances_of_concepts = dict()
    for x_object_binding in x_object_variable_group.solution_values:
        x_object_value = x_object_binding.value
        if len(x_object_value) > 1:
            # Let's just reduce complexity by not supporting ordering things "together"
            context.report_error(["errorText", "One thing at a time, please!"], force=True)
            return

        else:
            _, bucketed_instances_of_concepts = x_object_value[0].instances_of_concepts(context, state_list[0], orderable_list)
            all_bucketed_instances_of_concepts.update(bucketed_instances_of_concepts)

    if len(all_bucketed_instances_of_concepts) > 1:
        special_count = 0
        specials = specials_concepts(state_list[0])
        for key in all_bucketed_instances_of_concepts.keys():
            if key in specials:
                special_count += 1

        if len(specials) >= special_count:
            # Only asking about specials
            task = ('describe', context, [tuple(x for x in all_bucketed_instances_of_concepts.keys()) ])
        else:
            task = ('satisfy_want', context, [("user",)], [(ESLConcept("menu"),) ], 1)

    else:
        min = min_from_variable_group(x_object_variable_group)
        if min == 2 and x_object_value[0].entails(context, state_list[0], ESLConcept("menu")):
            # Something like "Do you have menus? or 2 menus?" was said
            # Assume it means we each want one
            task = ('satisfy_want', context, [("user",), ("son1",)], [x_object_value, x_object_value], 1)

        else:
            task = ('satisfy_want', context, [("user",)], [x_object_value], min_from_variable_group(x_object_variable_group))

    final_state = do_task(state_list[0].world_state_frame(), [task])
    if final_state:
        final_states = None
        for next_state in state_list:
            if final_states is None:
                # skip the first one
                final_states = []
                continue
            else:
                final_states.append(next_state)

        final_states.insert(0, final_state)
        yield final_states

    else:
        return


# This interprets _have_v_1 as simply "does x have y" meaning "have with them", contain, own, etc.
# Requires that both arguments be instances
@Predication(vocabulary,
             names=["_have_v_1"],
             phrases={
                "Do you have a kitchen?": {'SF': 'ques', 'TENSE': 'pres', 'MOOD': 'indicative', 'PROG': '-', 'PERF': '-'},
                "Do you have this table?": {'SF': 'ques', 'TENSE': 'pres', 'MOOD': 'indicative', 'PROG': '-', 'PERF': '-'},
                "Do I|we have the table?": {'SF': 'ques', 'TENSE': 'pres', 'MOOD': 'indicative', 'PROG': '-', 'PERF': '-'},
                "Do you have a|the steak?": {'SF': 'ques', 'TENSE': 'pres', 'MOOD': 'indicative', 'PROG': '-', 'PERF': '-'},
                "We have 2 menus": {'SF': 'prop', 'TENSE': 'pres', 'MOOD': 'indicative', 'PROG': '-', 'PERF': '-'},
                "I have a son": {'SF': 'prop', 'TENSE': 'pres', 'MOOD': 'indicative', 'PROG': '-', 'PERF': '-'}
             },
             properties={'SF': ['ques', 'prop'], 'TENSE': 'pres', 'MOOD': 'indicative', 'PROG': '-', 'PERF': '-'})
def _have_v_1_fact_check(context, state, e_introduced_binding, x_actor_binding, x_object_binding):
    def bound(x_actor, x_object):
        if rel_check(state, x_actor, "have", x_object):
            return True

        else:
            context.report_error(["verbDoesntApplyArg", x_actor_binding.variable.name, "have", x_object_binding.variable.name])
            return False

    def actor_from_object(x_object):
        # "who has x"
        found = False
        for i in rel_subjects(state, "have", x_object):
            found = True
            yield i

        if not found:
            context.report_error(["nothing_verb_x", x_actor_binding.variable.name, "has", x_object_binding.variable.name])

    def object_from_actor(x_actor):
        # "What do I have?"
        found = False
        for i in rel_objects(state, x_actor, "have"):
            found = True
            yield i

        if not found:
            context.report_error(["x_verb_nothing", x_actor_binding.variable.name, "has"])

    # Both arguments must be instances
    if (x_actor_binding.value is not None and is_concept(x_actor_binding)) or (x_object_binding.value is not None and is_concept(x_object_binding)):
        context.report_error(["formNotUnderstood", "_have_v_1_request"])
        return

    yield from in_style_predication_2(context, state, x_actor_binding, x_object_binding, bound, actor_from_object,
                                      object_from_actor)


# Used only when there is a form of have that means "able to"
# The solution predication only checks if "x is able to have y" nothing is implied
# Except: "What can I have?" implies asking for a menu
@Predication(vocabulary,
             names=["_have_v_1_able", "_get_v_1_able"],
             phrases={
                "Could I have|get a steak?": {'SF': 'ques', 'TENSE': 'tensed', 'MOOD': 'indicative', 'PROG': '-', 'PERF': '-'},
                "Can I have|get a steak?": {'SF': 'ques', 'TENSE': 'pres', 'MOOD': 'indicative', 'PROG': '-', 'PERF': '-'},
                "What can I have|get?": {'SF': 'ques', 'TENSE': 'pres', 'MOOD': 'indicative', 'PROG': '-', 'PERF': '-'},
                "Can the salad have nuts?": {'SF': 'ques', 'TENSE': 'pres', 'MOOD': 'indicative', 'PROG': '-', 'PERF': '-'},
                "who can have|get a steak?": {'SF': 'ques', 'TENSE': 'pres', 'MOOD': 'indicative', 'PROG': '-', 'PERF': '-'}
             },
             properties={'SF': 'ques', 'TENSE': ['pres', 'tensed'], 'MOOD': 'indicative', 'PROG': '-', 'PERF': '-'},
             arguments=[("e",), ("x", ValueSize.all), ("x", ValueSize.all)])
def _have_v_1_able(context, state, e_introduced_binding, x_actor_binding, x_object_binding):
    def both_bound_prediction_function(x_actor, x_object):
        # Players are able to have any food, a table or a menu
        if is_user_type(x_actor):
            return valid_player_request(context, state, [x_object])

        else:
            # "Can the salad have nuts?"
            # "Can a nut-free salad have nuts?"
            # Prove via induction any concepts
            # Because this is "able" as long as one instance has it then it is "able"
            actor_instances = x_actor.instances(context, state) if is_concept(x_actor) else [x_actor]
            object_instances = x_object.instances(context, state) if is_concept(x_object) else [x_object]
            for actor in actor_instances:
                for object in object_instances:
                    if rel_check(state, actor, "have", object):
                        return True

            return False

    def actor_unbound(x_object):
        # What/Who can have x? Comes in unbound because it is reorderable
        # so we need to return everything that is able to have x
        # First, see if people can have x
        found = False
        if valid_player_request(context, state, [x_object]):
            found = True
            for item in user_types():
                yield item

        # Now see if anything else can have x via induction
        object_instances = x_object.instances(context, state) if is_concept(x_object) else [x_object]
        for object in object_instances:
            for subject in rel_subjects(state, "have", object):
                found = True
                yield subject

        if not found:
            context.report_error(["nothing_verb_x", x_actor_binding.variable.name, "have", x_object_binding.variable.name])

    def object_unbound(x_actor):
        # This is a "What can I have?" type question
        # - Conceptually, there are a lot of things the user is able to have: a table, a bill, a menu, a steak, etc.
        #   - But: this isn't really what they are asking. This is something that is a special phrase in the "restaurant frame" which means: "what is on the menu"
        #     - So it is a special case that we interpret as a request for a menu
        if is_user_type(x_actor):
            yield ESLConcept("menu")

    yield from in_style_predication_2(context, state, x_actor_binding, x_object_binding,
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
@Predication(vocabulary,
             names=["solution_group__have_v_1_able", "solution_group__get_v_1_able"],
             properties_from=_have_v_1_able)
def _have_v_1_able_group(context, state_list, e_variable_group, x_actor_variable_group, x_object_variable_group):
    # At this point they were *able* to have the item, now we see if this was an implicit request for it
    # If this is a question, but not a wh question, involving the players, then it is also a request for something
    tree_info = state_list[0].get_binding("tree").value[0]
    force = sentence_force(tree_info["Variables"])
    wh_variable = get_wh_question_variable(tree_info)
    if force in ["ques", "prop-or-ques"] and \
            ((wh_variable and x_object_variable_group.solution_values[0].value[0] == ESLConcept("menu")) or
             not wh_variable):
        # The planner will only satisfy a want wrt the players
        task = ('satisfy_want', context, variable_group_values_to_list(x_actor_variable_group), variable_group_values_to_list(x_object_variable_group), min_from_variable_group(x_object_variable_group))
        final_state = do_task(state_list[0].world_state_frame(), [task])
        if final_state:
            yield [final_state]

    else:
        # Not an implicit request
        yield state_list


@Predication(vocabulary, names=["poss"],
             arguments=[("e",), ("x", ValueSize.all), ("x", ValueSize.all)])
def poss_lift_style(context, state, e_introduced_binding, x_object_binding, x_actor_binding):
    def bound(x_actors, x_objects):
        # If any are concepts, they all are since thats how the solver works
        if is_concept(x_objects[0]):
            # This is converted to a concept that has the criteria "actor has" below
            if len(x_objects) == 1:
                return True

        else:
            # Objects are instances, and actors are required to be from the code below in the body of the function
            actors = x_actors[0] if len(x_actors) == 1 else tuple([x_actor for x_actor in x_actors])
            objects = x_objects[0] if len(x_objects) == 1 else tuple([x_object for x_object in x_objects])
            if (actors, objects) in state.all_rel("have"):
                return True

            else:
                context.report_error(
                    ["verbDoesntApplyArg", x_actor_binding.variable.name, "have", x_object_binding.variable.name,
                     state.get_reprompt()])
                return False

    def actor_from_objects(x_objects):
        for i in state.all_rel("have"):
            if i[1] == x_objects:
                actor = store_to_object(i[0])
                if not isinstance(actor, tuple):
                    actor = (actor, )
                yield actor

    def object_from_actors(x_actors):
        for i in state.all_rel("have"):
            if i[0] == x_actors:
                object = store_to_object(i[1])
                if not isinstance(object, tuple):
                    object = (object, )
                yield object

    # This predication doesn't support conceptual actors
    if x_actor_binding.value is None or all([not is_concept(item) for item in x_actor_binding.value]):
        for item in lift_style_predication_2(context, state, x_actor_binding, x_object_binding, bound, actor_from_objects, object_from_actors):
            if x_actor_binding is not None and \
                    x_object_binding.value is not None and len(x_object_binding.value) == 1 and is_concept(x_object_binding.value[0]):
                # Add extra criteria to the concept to represent possession by x_actor
                x_object = x_object_binding.value[0].add_criteria(rel_objects, x_actor_binding.value[0], "possess")
                yield state.set_x(x_object_binding.variable.name, (x_object, ))

            else:
                yield item
    else:
        context.report_error(["formNotUnderstood"])
        return

# Returns:
# the variable to measure into, the units to measure
# or None if not a measurement unbound variable
def measure_units(x):
    if isinstance(x, Measurement) and x.count is None:
        # if x is a Measurement() with None as a value,
        # then we are being asked to measure x_actor
        units = x.measurement_type
        if is_concept(units):
            return units

    return None


def is_be_v_id_order(context, state, x_subject_binding, x_object_binding):
    for check_binding in [x_subject_binding, x_object_binding]:
        if check_binding.value is not None and len(check_binding.value) == 1 and instance_of_or_entails(context, state, check_binding.value[0], ESLConcept("order")):
            return True

    return False


@Predication(vocabulary,
             names=["_be_v_id"],
             phrases={
                 "What is my order?":   {'SF': 'ques', 'TENSE': 'pres', 'MOOD': 'indicative', 'PROG': '-', 'PERF': '-'},
                 "My order is chicken": {'SF': 'prop', 'TENSE': 'pres', 'MOOD': 'indicative', 'PROG': '-', 'PERF': '-'},
                 "Chicken is my order": {'SF': 'prop', 'TENSE': 'pres', 'MOOD': 'indicative', 'PROG': '-', 'PERF': '-'}
             },
             properties={'SF': ['ques', 'prop'], 'TENSE': ['pres'], 'MOOD': 'indicative', 'PROG': '-', 'PERF': '-'},
             arguments=[("e",), ("x", ValueSize.all), ("x", ValueSize.exactly_one)])
def _be_v_id_order_1(context, state, e_introduced_binding, x_subject_binding, x_object_binding):
    yield from _be_v_id_order_base(context, state, e_introduced_binding, x_subject_binding, x_object_binding)


@Predication(vocabulary,
             names=["_be_v_id"],
             phrases={
                 "What is my order?":   {'SF': 'ques', 'TENSE': 'pres', 'MOOD': 'indicative', 'PROG': '-', 'PERF': '-'},
                 "My order is chicken": {'SF': 'prop', 'TENSE': 'pres', 'MOOD': 'indicative', 'PROG': '-', 'PERF': '-'},
                 "Chicken is my order": {'SF': 'prop', 'TENSE': 'pres', 'MOOD': 'indicative', 'PROG': '-', 'PERF': '-'}
             },
             properties={'SF': ['ques', 'prop'], 'TENSE': ['pres'], 'MOOD': 'indicative', 'PROG': '-', 'PERF': '-'},
             arguments=[("e",), ("x", ValueSize.exactly_one), ("x", ValueSize.all)])
def _be_v_id_order_2(context, state, e_introduced_binding, x_subject_binding, x_object_binding):
    yield from _be_v_id_order_base(context, state, e_introduced_binding, x_subject_binding, x_object_binding)

# There are two alternative _be_v_id_order implementations: _be_v_id_order_1 and _be_v_id_order_2 because the base
# requires that one of the arguments is a singular order and this allows us to not generate a *ton* of alternatives
# Discussions about the customers order are about a *particular* order, and thus deal with order instances, not concepts
# However: the items *in* the order must be concepts
def _be_v_id_order_base(context, state, e_introduced_binding, x_subject_binding, x_object_binding):
    def criteria_bound(x_subject, x_object):
        # Either argument could be the order
        for order_item in [x_subject, x_object]:
            if len(order_item) == 1 and instance_of_what(state, order_item[0]) == "order":
                # "My order is X" or "X is my order] --> See if the set of items in x_object entail what was ordered
                potential_concepts_in_order = x_subject if order_item == x_object else x_object
                order = order_item[0]
                order_food_instances = sorted([x for x in state.food_in_order(order)])
                if len(order_food_instances) > 0:
                    for food_concept in potential_concepts_in_order:
                        if not is_concept(food_concept):
                            return False
                        found_instances = food_concept.instances(context, state, order_food_instances)
                        found_type = len(found_instances) > 0
                        if found_type:
                            for found_instance in found_instances:
                                order_food_instances.remove(found_instance)

                        else:
                            break

                    if found_type and len(order_food_instances) == 0:
                        return True

                else:
                    context.report_error(["errorText", "Nothing"])

        if len(x_subject) == 1 and not is_concept(x_subject[0]) and sort_of(state, x_subject[0], "order"):
            # "My order is X" --> See if the set of items in x_object entail what was ordered
            order = x_subject[0]
            order_food_instances = sorted([x for x in state.food_in_order(order)])
            if len(order_food_instances) > 0:
                for food_concept in x_object:
                    if not is_concept(food_concept):
                        return False
                    found_instances = food_concept.instances(context, state, order_food_instances)
                    found_type = len(found_instances) > 0
                    if found_type:
                        for found_instance in found_instances:
                            order_food_instances.remove(found_instance)

                    else:
                        break

                if found_type and len(order_food_instances) == 0:
                    return True

            else:
                context.report_error(["errorText", "Nothing"])

    def unbound(x_object):
        # The phrase "What is my order?" means "what are the things in my order"
        order = x_object[0]
        order_foods = tuple([x for x in state.food_in_order(order)])
        if len(order_foods) > 0:
            yield order_foods
        else:
            context.report_error(["errorText", "Nothing"])

    # Only use this interpretation if we are talking about an instance of "order"
    # The other argument will be checked in the bound/unbound functions above
    has_instance = False
    for order_binding in [x_subject_binding, x_object_binding]:
        if order_binding.value is not None and len(order_binding.value) == 1 and not is_concept(order_binding.value[0]) and \
                instance_of_what(state, order_binding.value[0]) == "order":
            has_instance = True
            break

    if not has_instance:
        context.report_error(["formNotUnderstood"])
        return

    # Use lift_style so that we get everything in the order as a single value, meaning "together"
    for success_state in lift_style_predication_2(context, state, x_subject_binding, x_object_binding, criteria_bound, unbound, unbound):
        yield success_state


@Predication(vocabulary,
             names=["solution_group__be_v_id"],
             properties_from=_be_v_id_order_1,
             handles_interpretation=_be_v_id_order_1)
def _be_v_id_order_group(context, state_list, e_introduced_binding_list, x_subject_variable_group, x_object_variable_group):
    # Since one of the arguments holds concepts, constraints need to be checked
    # Figure out which argument it is
    concept_variable_group = None
    for check_variable_group in [x_subject_variable_group, x_object_variable_group]:
        if check_variable_group.solution_values[0].value is not None and is_concept(check_variable_group.solution_values[0].value[0]):
            concept_variable_group = check_variable_group
            order_variable_group = x_subject_variable_group if x_object_variable_group == check_variable_group else x_object_variable_group

    if not concept_variable_group:
        # This solution group handler requires conceptual things in an order
        context.report_error(["formNotUnderstood"])
        return

    else:
        # Get the global criteria
        min = min_from_variable_group(check_variable_group)
        max = max_from_variable_group(check_variable_group)

        # Figure out the count of things ordered that "are" this concept
        # Then compare the actual count across the solution group to the global criteria
        tree_info = state_list[0].get_binding("tree")
        order = order_variable_group.solution_values[0].value[0]
        order_foods = sorted([x for x in state_list[0].food_in_order(order)])
        found_count = 0
        for food_concept_binding in concept_variable_group.solution_values:
            for food_concept in food_concept_binding.value:
                found_instances = food_concept.instances(context, state_list[0], order_foods)
                found_count += len(found_instances)
                for found_instance in found_instances:
                    order_foods.remove(found_instance)

        if found_count < min:
            context.report_error(["phase2LessThan", concept_variable_group.variable_constraints.variable_name, min], force=True, phase=2)
            return

        elif found_count > max:
            context.report_error(["phase2MoreThan", concept_variable_group.variable_constraints.variable_name, max], force=True, phase=2)
            return

        yield state_list


# Handle "what is X?", "where is X?", "who is x?" when it has exactly one unbound argument and one bound concept argument and
# the concept argument is entailed by at least one menu item
#
# Since the bound arg is a concept, we have a choice to make. We need to decide *what kind* of "what is/are ..." question this is:
#   1. is the person asking us to list the things that are of type x_object? I.e. that specialize it? as in "what are the specials?"
#   or
#   2. does "what are your specials?" mean "what property do they all share?" as in "they are vegetarian" or "they are all delicious"?
#
# If we are talking about an object which represents a *class* of things on the menu, asking "what" something is almost certainly means
# "list the classes it represents on the menu!"
#   "A class of things" means: a concept that will be entailed by at least one other concept. I.e. "what are your light items?"
#   "what are the cheap choices?"
#
# It is probably unusual to ask "What are your vegetarian items" when meaning "what does 'vegetarian item' mean?"
#
# Just like above, asking "what is chicken?" could mean "what on the menu includes chicken" or "what is this meat called 'chicken'"
# This works just like "what are your specials?": see if "[chicken]"  will be entailed by at least one thing on the menu.  If so,
# it is this case.
#
# If our menu contained more complicated items the "what does it mean?" meaning might be used more to get clarification,
#   as in "what is cardomom?"
#
# So, we will interpret anything that is entailed by concepts on the menu to mean "list them"
#
# So this means the following would all return a list of things (if we've implemented all the predications):
# "What is a cheap dish?"
# "What are things written in text in this room?"
# "what is edible here?"
# "what are your small dishes?"
# "What is vegetarian?
#
# These would not match:
#   "what is my bill?"
#   "where is a restroom?"
@Predication(vocabulary,
             names=["_be_v_id"],
             phrases={
                 "What are the specials?": {'SF': 'ques', 'TENSE': 'pres', 'MOOD': 'indicative', 'PROG': '-', 'PERF': '-'},
                 "What will be the specials?": {'SF': 'ques', 'TENSE': 'fut', 'MOOD': 'indicative', 'PROG': '-', 'PERF': '-'}
             },
             properties={'SF': ['ques'], 'TENSE': ['pres', 'fut'], 'MOOD': 'indicative', 'PROG': '-', 'PERF': '-'},
             handles_negation=True)
def _be_v_id_list(context, state, e_introduced_binding, x_subject_binding, x_object_binding):
    def criteria_bound(x_subject, x_object):
        # When "not" is used ("what is not vegetarian?"), both arguments will be bound since thing(x) binds every possible
        # thing into the first argument. To be true, the right side must be orderable, and the left side must entail it
        entailed_orderable = x_object.entailed_by_which(context, state, orderable)
        if len(entailed_orderable):
            if x_subject.entails(context, state, x_object):
                return True
            else:
                # Distinguish between subjects that aren't orderable at all (which don't belong here
                # thus formNotUnderstood) vs. those that are but just don't entail the object
                _, entailed = x_subject.entails_which(context, state, orderable)
                if not entailed:
                    context.report_error(["formNotUnderstood"])
                return False
        else:
            context.report_error(["formNotUnderstood"])
            return

    def unbound(x_object):
        entailed_orderable = x_object.entailed_by_which(context, state, orderable)
        if len(entailed_orderable) > 0:
            # The answer to "What is [x]?" where "x" is any concept entailed by at least one menu item
            # is those menu items
            yield from entailed_orderable
            return

    # Don't use this interpretation if we are talking about an "order"
    if is_be_v_id_order(context, state, x_subject_binding, x_object_binding):
        context.report_error(["formNotUnderstood"])
        return

    # one or both of subject or object must be bound
    subject_unbound = x_subject_binding.value is None
    object_unbound = x_object_binding.value is None
    if subject_unbound and object_unbound:
        context.report_error(["formNotUnderstood"])
        return

    # Require that the any bound arguments are concepts
    if (not subject_unbound and not is_concept(x_subject_binding.value[0])) or \
        (not object_unbound and not is_concept(x_object_binding.value[0])):
        context.report_error(["formNotUnderstood"])
        return

    orderable = orderable_concepts(state)
    yield from in_style_predication_2(context, state, x_subject_binding, x_object_binding, criteria_bound, unbound, unbound)


@Predication(vocabulary,
             names=["solution_group__be_v_id"],
             properties_from=_be_v_id_list,
             handles_interpretation=_be_v_id_list,
             handles_negation=True)
def _be_v_id_list_group(context, state_list, e_introduced_binding_list, x_subject_variable_group, x_object_variable_group):
    # Don't use this interpretation if we are talking about an "order"
    if all([is_be_v_id_order(context,
                             state,
                             state.get_binding(x_subject_variable_group.solution_values[0].variable.name),
                             state.get_binding(x_object_variable_group.solution_values[0].variable.name)) for state in state_list]):
        context.report_error(["formNotUnderstood"])
        return

    # Since the arguments are concepts constraints need to be checked
    for check_variable_group in [x_subject_variable_group, x_object_variable_group]:
        if check_variable_group.solution_values[0].value is not None and is_concept(check_variable_group.solution_values[0].value[0]):
            if not check_concept_solution_group_constraints(context, state_list, check_variable_group, check_concepts=True):
                return

    yield state_list


@Predication(vocabulary, names=["measure_units_for_item"])
def measure_units_for_item(context, state, x_count, x_measure, x_item):
    if any([x is None for x in [x_measure.value, x_item.value]]):
        context.report_error(["formNotUnderstood"])
        return
    if len(x_measure.value) != 1 or not isinstance(x_measure.value[0], Measurement) or not is_concept(x_measure.value[0].measurement_type):
        context.report_error(["formNotUnderstood"])
        return

    yield from yield_cost_of_subject_into_object(context, state, x_measure.value[0].measurement_type, x_item.variable.name, x_count.variable.name)


def yield_cost_of_subject_into_object(context, state, units, subject_variable, object_variable):
    # Use entailment to check the units so that
    # "How many 'american cash units'" or "How many items of 'green paper used for cash'" would
    # theoretically work
    if units.entailed_by_which(context, state, [ESLConcept("generic_entity"), ESLConcept("dollar")]):
        x_subject_concept = state.get_binding(subject_variable).value[0]
        if is_concept(x_subject_concept):
            entailed_concept = None
            if x_subject_concept is not None:
                priced_concepts = [ESLConcept(x) for x in state.sys["prices"].keys()]
                concepts_we_know = [ESLConcept("generic_entity"), ESLConcept("bill")] + priced_concepts
                _, subject_entails_concepts = x_subject_concept.entails_which(context, state, concepts_we_know)
                if len(subject_entails_concepts) > 1:
                    yield state.record_operations([RespondOperation("That is more than one thing.")])
                    return False
                elif len(subject_entails_concepts) == 1:
                    entailed_concept = subject_entails_concepts[0]

                else:
                    return

            if x_subject_concept is None or entailed_concept == ESLConcept("generic_entity"):
                # Happens for "That will be all, thank you"
                return

            elif entailed_concept in priced_concepts:
                concept_name = entailed_concept.single_sort_name()
                price = Measurement("dollar", state.sys["prices"][concept_name])

                # Remember that we now know the price
                yield state.set_x(object_variable, (price,)).record_operations([SetKnownPriceOp(concept_name)])

            elif entailed_concept == ESLConcept("bill"):
                total = list(rel_objects(state, "bill1", "valueOf"))
                if len(total) == 0:
                    total.append(0)
                price = Measurement("dollar", total[0])
                yield state.set_x(object_variable, (price,))

            else:
                yield state.record_operations([RespondOperation("Haha, it's not for sale.")])
                return False


@Predication(vocabulary,
             names=["_be_v_id"],
             phrases={
                 "How much is the soup?": {'SF': 'ques', 'TENSE': 'pres', 'MOOD': 'indicative', 'PROG': '-', 'PERF': '-'},
                 "How much will the soup be?": {'SF': 'ques', 'TENSE': 'fut', 'MOOD': 'indicative', 'PROG': '-', 'PERF': '-'},
                 "How many dollars is the soup?": {'SF': 'ques', 'TENSE': 'pres', 'MOOD': 'indicative', 'PROG': '-', 'PERF': '-'},
                 "How many dollars will the soup be?": {'SF': 'ques', 'TENSE': 'fut', 'MOOD': 'indicative', 'PROG': '-', 'PERF': '-'}
             },
             properties={'SF': ['ques'], 'TENSE': ['pres', 'fut'], 'MOOD': 'indicative', 'PROG': '-', 'PERF': '-'})
def _be_v_id_much_many(context, state, e_introduced_binding, x_subject_binding, x_object_binding):
    def criteria_bound(x_subject, x_object):
        # Just check if this is an object and a measurement, if so, handle it below
        units = measure_units(x_object)
        return units is not None

    def unbound(x_object):
        if False:
            yield None

    # Don't use this interpretation if we are talking about an "order", we have a different implementation for that
    if is_be_v_id_order(context, state, x_subject_binding, x_object_binding):
        return

    for success_state in in_style_predication_2(context, state, x_subject_binding, x_object_binding, criteria_bound, unbound, unbound):
        # This is a "how much is x" question: we need to measure the value
        # into the specified variable
        x_object_value = success_state.get_binding(x_object_binding.variable.name).value[0]
        units = measure_units(x_object_value)
        yield from yield_cost_of_subject_into_object(context, success_state, units, x_subject_binding.variable.name, x_object_binding.variable.name)


@Predication(vocabulary,
             names=["solution_group__be_v_id"],
             properties_from=_be_v_id_much_many,
             handles_interpretation=_be_v_id_much_many)
def _be_v_id_much_many_group(context, state_list, e_introduced_binding_list, x_subject_variable_group, x_object_variable_group):
    # If the arguments are concepts constraints need to be checked
    for check_variable_group in [x_subject_variable_group, x_object_variable_group]:
        if check_variable_group.solution_values[0].value is not None and is_concept(check_variable_group.solution_values[0].value[0]):
            if not check_concept_solution_group_constraints(context, state_list, check_variable_group, check_concepts=True):
                return

    yield state_list


# Interpret "Who/What/Where is [x]?" as asking "which instance is [x]"
# "Who is my son?" --> son1
# "What is the room with the toilet?" --> bathroom1
# Require that x_subject is an instance and x_object can be an instance or concept
@Predication(vocabulary,
             names=["_be_v_id"],
             phrases={
                 "our dishes are specials": {'SF': 'prop', 'TENSE': 'pres', 'MOOD': 'indicative', 'PROG': '-', 'PERF': '-'},
                 "Which are the open tables?": {'SF': 'ques', 'TENSE': 'pres', 'MOOD': 'indicative', 'PROG': '-', 'PERF': '-'},
                 "Who is my son?": {'SF': 'ques', 'TENSE': 'pres', 'MOOD': 'indicative', 'PROG': '-', 'PERF': '-'},
                 "What is the room with the toilet?": {'SF': 'ques', 'TENSE': 'pres', 'MOOD': 'indicative', 'PROG': '-', 'PERF': '-'},
                 "What is the location of your bathroom?": {'SF': 'ques', 'TENSE': 'pres', 'MOOD': 'indicative', 'PROG': '-', 'PERF': '-'},
                 "My son is my son": {'SF': 'prop', 'TENSE': 'pres', 'MOOD': 'indicative', 'PROG': '-', 'PERF': '-'},
                 "My soup is a vegetarian dish": {'SF': 'prop', 'TENSE': 'pres', 'MOOD': 'indicative', 'PROG': '-', 'PERF': '-'}
             },
             properties=[{'SF': ['prop'], 'TENSE': ['pres'], 'MOOD': 'indicative', 'PROG': '-', 'PERF': '-'},
                         {'SF': ['ques'], 'TENSE': ['pres'], 'MOOD': 'indicative', 'PROG': '-', 'PERF': '-'}])
def _be_v_id_instance_concept(context, state, e_introduced_binding, x_subject_binding, x_object_binding):
    def criteria_bound(x_subject, x_object):
        if is_concept(x_object):
            if instance_of_or_entails(context, state, x_subject, x_object):
                return True
            elif rel_check(state, x_subject, "isAdj", x_object.single_sort_name()):
                return True

        else:
            if x_subject == x_object:
                return True

        context.report_error(["is_not", x_subject_binding.variable.name, x_object_binding.variable.name])
        return False

    def unbound(x_object):
        if is_concept(x_object):
            # yields instances since this interpretation is "instance_concept"
            yield from x_object.instances(context, state)

        else:
            yield x_object

    # Don't use this interpretation if we are talking about an "order", we have a different implementation for that
    if is_be_v_id_order(context, state, x_subject_binding, x_object_binding):
        return

    # Require that the subject is an instance
    # Only need to check one value since there is never a mix of instances and concepts
    if x_subject_binding.value is not None and not is_instance(state, x_subject_binding.value[0]):
        return

    for success_state in in_style_predication_2(context, state, x_subject_binding, x_object_binding, criteria_bound, unbound, unbound):
        yield success_state


@Predication(vocabulary,
             names=["solution_group__be_v_id"],
             properties_from=_be_v_id_instance_concept,
             handles_interpretation=_be_v_id_instance_concept)
def _be_v_id_instance_concept_group(context, state_list, e_introduced_binding_list, x_subject_variable_group, x_object_variable_group):
    # If object is a concept, constraints need to be checked
    if x_object_variable_group.solution_values[0].value is not None and is_concept(x_object_variable_group.solution_values[0].value[0]):
        if not check_concept_solution_group_constraints(context, state_list, x_object_variable_group, check_concepts=True):
            return

    yield state_list


# Interpret "Who/What/Where is [x]?" as asking "what does [x] specialize"
# "Who is my son?" --> a person
# "What is the room with the toilet?" --> a bathroom
# Require that x_subject is an concept and x_object is a concept
@Predication(vocabulary,
             names=["_be_v_id"],
             phrases={
                 "Who is my son?": {'SF': 'ques', 'TENSE': 'pres', 'MOOD': 'indicative', 'PROG': '-', 'PERF': '-'},
                 "What is the room with the toilet?": {'SF': 'ques', 'TENSE': 'pres', 'MOOD': 'indicative', 'PROG': '-', 'PERF': '-'},
                 "What is the location of your bathroom?": {'SF': 'ques', 'TENSE': 'pres', 'MOOD': 'indicative', 'PROG': '-', 'PERF': '-'},
                 "soup is a vegetarian dish": {'SF': 'prop', 'TENSE': 'pres', 'MOOD': 'indicative', 'PROG': '-', 'PERF': '-'}
             },
             properties=[{'SF': ['prop'], 'TENSE': ['pres'], 'MOOD': 'indicative', 'PROG': '-', 'PERF': '-'},
                         {'SF': ['ques'], 'TENSE': ['pres'], 'MOOD': 'indicative', 'PROG': '-', 'PERF': '-'}])
def _be_v_id_concept_concept(context, state, e_introduced_binding, x_subject_binding, x_object_binding):
    def criteria_bound(x_subject, x_object):
        if x_subject.entails(context, state, x_object):
            return True

        context.report_error(["is_not", x_subject_binding.variable.name, x_object_binding.variable.name])
        return False

    def unbound(x_object):
        # The user is asking what sort of thing x_object is.  But x_object might be
        # a complicated concepts like "People that have different colored eyes" and the base concept
        # can't be found by examining the type and looking at what the concept specializes (because there might not be an obvious type)
        # This won't find all the adjectives (i.e. "what is the pork" won't return "smoked"), but that could be added
        for item in x_object.entails_which_specializations(context, state):
            yield ESLConcept(item)

    # Don't use this interpretation if we are talking about an "order", we have a different implementation for that
    if is_be_v_id_order(context, state, x_subject_binding, x_object_binding):
        return

    # Require that any bound value is a concept
    for check_binding in [x_subject_binding, x_object_binding]:
        if check_binding.value is not None and not is_concept(check_binding.value[0]):
            return

    for success_state in in_style_predication_2(context, state, x_subject_binding, x_object_binding, criteria_bound, unbound, unbound):
        yield success_state


@Predication(vocabulary,
             names=["solution_group__be_v_id"],
             properties_from=_be_v_id_concept_concept,
             handles_interpretation=_be_v_id_concept_concept)
def _be_v_id_concept_concept_group(context, state_list, e_introduced_binding_list, x_subject_variable_group, x_object_variable_group):
    # If object is a concept, constraints need to be checked
    for check_variable_group in [x_subject_variable_group, x_object_variable_group]:
        if check_variable_group.solution_values[0].value is not None and is_concept(check_variable_group.solution_values[0].value[0]):
            if not check_concept_solution_group_constraints(context, state_list, check_variable_group, check_concepts=True):
                return

    yield state_list


@Predication(vocabulary,
             names=["_cost_v_1"],
             phrases={
                "What does the steak cost?": {'SF': 'ques', 'TENSE': 'pres', 'MOOD': 'indicative', 'PROG': '-', 'PERF': '-'},
                "What will the steak cost?": {'SF': 'ques', 'TENSE': 'fut', 'MOOD': 'indicative', 'PROG': '-', 'PERF': '-'},
                "The steak costs 10 dollars": {'SF': 'prop', 'TENSE': 'pres', 'MOOD': 'indicative', 'PROG': '-', 'PERF': '-'}
             },
             properties=[{'SF': 'ques', 'TENSE': ['pres', 'fut'], 'MOOD': 'indicative', 'PROG': '-', 'PERF': '-'},
                         {'SF': 'prop', 'TENSE': 'pres', 'MOOD': 'indicative', 'PROG': '-', 'PERF': '-'}])
def _cost_v_1(context, state, e_introduced_binding, x_actor_binding, x_object_binding):
    def criteria_bound(x_actor, x_object):
        if not isinstance(x_object, Measurement):
            context.report_error(["Have not dealt with declarative cost"])
            yield False

        else:
            yield True  # will need to implement checking for price correctness in the future if user says "the soup costs one steak"

    def get_actor(x_object):
        if False:
            yield None

    def get_object(x_actor):
        # What does x cost?
        if is_concept(x_actor):
            # Make sure it is something that is actually in the world
            # by evaluating it to make sure there are instances
            if len(x_actor.instances(context, state)) == 0:
                return

            priced_concepts = [ESLConcept(x) for x in state.sys["prices"].keys()]
            _, actor_entails_concepts = x_actor.entails_which(context, state, priced_concepts)
            if len(actor_entails_concepts) > 1:
                yield "Ah. It's not for sale."

            else:
                # entailed_concept_name = actor_entails_concepts[0].single_sort_name()
                yield Measurement(ESLConcept("dollar"), None)
                # yield entailed_concept_name + " : " + str(state.sys["prices"][entailed_concept_name]) + " dollars"

        else:
            concept_item = instance_of_what(state, x_actor)
            if concept_item in state.sys["prices"].keys():
                yield Measurement(ESLConcept("dollar"), None)

            else:
                yield "Ah. It's not for sale."

    for success_state in in_style_predication_2(context, state, x_actor_binding, x_object_binding, criteria_bound, get_actor, get_object):
        x_object_value = success_state.get_binding(x_object_binding.variable.name).value[0]
        units = measure_units(x_object_value)
        if units is not None:
            # This is a "how much is x" question: we need to measure the value
            # into the specified variable
            yield from yield_cost_of_subject_into_object(context, success_state, units, x_actor_binding.variable.name,                          x_object_binding.variable.name)

        else:
            # concept_name = entailed_concept.single_sort_name()
            # price = Measurement("dollar", state.sys["prices"][concept_name])
            #
            # # Remember that we now know the price
            # yield state.set_x(object_variable, (price,)).record_operations([SetKnownPriceOp(concept_name)])

            yield success_state


@Predication(vocabulary,
             names=["solution_group__cost_v_1"],
             properties_from=_cost_v_1)
def _cost_v_1_group(context, state_list, e_introduced_binding_list, x_act_variable_group, x_obj2_variable_group):
    if is_concept(x_act_variable_group.solution_values[0].value[0]):
        if not check_concept_solution_group_constraints(context, state_list, x_act_variable_group, check_concepts=True):
            return

    yield state_list


@Predication(vocabulary,
             names=["_be_v_there"],
             phrases={
                "Which vegetarian dishes are there?": {'SF': 'ques', 'TENSE': 'pres', 'MOOD': 'indicative', 'PROG': '-', 'PERF': '-'}
             },
             properties={'SF': 'ques', 'TENSE': 'pres', 'MOOD': 'indicative', 'PROG': '-', 'PERF': '-'})
def _be_v_there(context, state, e_introduced_binding, x_object_binding):
    def bound_variable(value):
        yield value in state.get_entities()

    def unbound_variable():
        for i in state.get_entities():
            yield i

    yield from combinatorial_predication_1(context, state, x_object_binding, bound_variable, unbound_variable)


@Predication(vocabulary, names=["_available_a_to-for"])
def _available_a_to_for(context, state, e_introduced_binding, x_object_binding, u_ignored):
    def bound_variable(value):
        yield value in state.get_entities()

    def unbound_variable():
        for i in state.get_entities():
            yield i

    yield from combinatorial_predication_1(context, state, x_object_binding, bound_variable, unbound_variable)


# Any successful solution group that is a wh_question will call this
@Predication(vocabulary,
             names=["solution_group_wh"],
             handles_negation=True)
def wh_question(context, state_list, binding_list, timed_out):
    current_state = do_task(state_list[0].world_state_frame(), [('describe', context, [x.value for x in binding_list])])
    if current_state is not None:
        # Make sure any operations that were created on solutions get passed on
        all_operations = []
        for solution in state_list:
            for operation in solution.get_operations():
                all_operations.append(operation)

        if timed_out:
            print("did it")
            all_operations.append(RespondOperation("(that's all I can think of at the moment)"))
        new_state = current_state.apply_operations(all_operations, True)

        # Include all of the solutions even though we only added operations to the first solution
        # This is so the engine can properly compare this solution group to others and return "(there are more)"
        yield (new_state,) + tuple(state_list[1:])


# Generates all the responses that predications can
# return when an error occurs
def generate_custom_message(state, tree_info, error_term):
    # error_term is of the form: [index, error] where "error" is another
    # list like: ["name", arg1, arg2, ...]. The first item is the error
    # constant (i.e. its name). What the args mean depends on the error
    error_predicate_index = error_term[0]
    error_arguments = error_term[1]
    error_constant = error_arguments[0] if error_arguments is not None else "no error set"
    arg_length = len(error_arguments) if error_arguments is not None else 0
    arg1 = error_arguments[1] if arg_length > 1 else None
    arg2 = error_arguments[2] if arg_length > 2 else None
    arg3 = error_arguments[3] if arg_length > 3 else None
    arg4 = error_arguments[4] if arg_length > 4 else None

    # See if the system can handle converting the error
    # to a message first except for those we are overriding

    # Override these
    if error_constant == "doesntExist":
        english_word = s("{bare arg1:sg}", tree_info)
        if english_word == "thing":
            return s("Host: Nothing.")
        elif english_word == "person":
            return s("Host: Nobody.")
        else:
            if "something" not in english_word:
                # If we can render this concept as a real word (not just "something"), ask
                # chatgpt if it is food
                request_info = perplexity.OpenAI.StartOpenAIBooleanRequest("test",
                                                                           "is_food_or_drink_predication",
                                                                           f"Is {english_word} either a food or a drink?")
                result = perplexity.OpenAI.CompleteOpenAIRequest(request_info, wait=5)
                if result == "true":
                    # It is, so report a nicer error than "I don't know that word"
                    return s("Host: I'm sorry, you can't order that here. Take a look at the menu to see what is available.", tree_info)

            return s("Host: There isn't such {a *english_word} here", tree_info)

    else:
        system_message = perplexity.messages.generate_message(state, tree_info, error_term)
        if system_message is not None:
            return system_message

    if error_constant == "dontHaveThatFood":
        return s("Host: I'm sorry, you can't order that here. Take a look at the menu to see what is available.", tree_info)
    if error_constant == "dontHaveInstances":
        # Happens if the user asks "Do you have x?" for any noun that isn't requestable.  I.e. "Do you have a bathroom?"
        return "I'm sorry, I'm not sure if we have that."

    if error_constant == "dontKnowHow":
        return "I don't know how to do that."
    if error_constant == "notAThing":
        # english_for_delphin_variable() converts a variable name like 'x3' into the english words
        # that it represented in the MRS
        arg1 = convert_to_english_list(state, arg1)
        return s("{*arg1} {'is':<arg1} not {arg2:@error_predicate_index}.", tree_info)
    if error_constant == "nothing_verb_x":
        return s("No {arg1} {*arg2} {a arg3}", tree_info, reverse_pronouns=True)
    if error_constant == "x_verb_nothing":
        return s("{arg1} {*arg2} nothing", tree_info, reverse_pronouns=True)
    if error_constant == "not_adj_about_player":
        return s("Ahh. I did not know that!")
    if error_constant == "not_adj":
        return s("{arg1:@error_predicate_index} {'is':<arg1} not {*arg2}.", tree_info, reverse_pronouns=True)
    if error_constant == "is_not":
        return s("{arg1} is not {arg2}", tree_info, reverse_pronouns=True)
    if error_constant == "arg_is_not_value":
        return s("{arg1} {'is':<arg1} not {*arg2}", tree_info, reverse_pronouns=True)
    if error_constant == "notOn":
        return s("{arg1} is not on {arg2}", tree_info)
    if error_constant == "notWant":
        return s("{arg1} {'do':<arg1} not want {arg2}", tree_info, reverse_pronouns=True)
    if error_constant == "verbDoesntApplyArg":
        return s("{arg1} {'do':<arg1} not {*arg2} {arg3}", tree_info, reverse_pronouns=True)
    if error_constant == "verbDoesntApply":
        return f"{arg1} does not {arg2} {arg3}"
    else:
        # No custom message, just return the raw error for debugging
        return str(error_term)


def reset():
    initial_state = WorldState({},
                               {"prices": {"salad": 3, "steak": 10, "soup": 4, "salmon": 12,
                                           "chicken": 7, "pork": 8, "water": 0},
                                "responseState": "initial"
                                })

    # Some basic rules:
    initial_state = initial_state.add_rel("order", "specializes", "thing")


    # The restaurant has to "have" all the things in it so that questions like "Do you have this table?" work
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

    initial_state = initial_state.add_rel("drink", "specializes", "thing")
    initial_state = initial_state.add_rel("water", "specializes", "drink")

    initial_state = initial_state.add_rel("food", "specializes", "thing")
    initial_state = initial_state.add_rel("dish", "specializes", "food")
    initial_state = initial_state.add_rel("meat", "specializes", "dish")
    initial_state = initial_state.add_rel("vegetarian", "specializes", "dish")
    initial_state = initial_state.add_rel("special", "specializes", "dish")

    initial_state = initial_state.add_rel("steak", "specializes", "meat")
    initial_state = initial_state.add_rel("chicken", "specializes", "meat")
    initial_state = initial_state.add_rel("salmon", "specializes", "meat")
    initial_state = initial_state.add_rel("pork", "specializes", "meat")

    initial_state = initial_state.add_rel("soup", "specializes", "vegetarian")
    initial_state = initial_state.add_rel("tomato", "specializes", "food")
    initial_state = initial_state.add_rel("soup", "isAdj", "tomato")

    initial_state = initial_state.add_rel("salad", "specializes", "vegetarian")
    initial_state = initial_state.add_rel("green", "specializes", "thing")
    initial_state = initial_state.add_rel("salad", "isAdj", "green")

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
    initial_state = initial_state.add_rel("restaurant", "have", "vegetarian")
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
    initial_state = initial_state.add_rel("restaurant", "have", "table1")
    initial_state = initial_state.add_rel("table2", "instanceOf", "table")
    initial_state = initial_state.add_rel("table2", "maxCapacity", 2)
    initial_state = initial_state.add_rel("restaurant", "have", "table2")
    initial_state = initial_state.add_rel("table3", "instanceOf", "table")
    initial_state = initial_state.add_rel("table3", "maxCapacity", 1)
    initial_state = initial_state.add_rel("restaurant", "have", "table3")

    initial_state = initial_state.add_rel("menu1", "instanceOf", "menu")
    initial_state = initial_state.add_rel("restaurant", "have", "menu1")
    initial_state = initial_state.add_rel("menu2", "instanceOf", "menu")
    initial_state = initial_state.add_rel("restaurant", "have", "menu2")
    initial_state = initial_state.add_rel("menu3", "instanceOf", "menu")
    initial_state = initial_state.add_rel("restaurant", "have", "menu3")

    initial_state = initial_state.add_rel("water1", "instanceOf", "water")
    initial_state = initial_state.add_rel("restaurant", "have", "water1")
    initial_state = initial_state.add_rel("water2", "instanceOf", "water")
    initial_state = initial_state.add_rel("restaurant", "have", "water2")
    initial_state = initial_state.add_rel("water3", "instanceOf", "water")
    initial_state = initial_state.add_rel("restaurant", "have", "water3")

    menu_types = ["salmon", "steak", "chicken"]
    special_types = ["soup", "salad", "pork"]
    dish_types = menu_types + special_types
    for dish_type in dish_types:
        # The restaurant has the concepts of the items so it can answer "do you have steak?"
        initial_state = initial_state.add_rel("restaurant", "have", dish_type)
        initial_state = initial_state.add_rel("restaurant", "describes", dish_type)

        if dish_type == "chicken":
            initial_state = initial_state.add_rel(dish_type, "isAdj", "roasted")
            initial_state = initial_state.add_rel(dish_type, "isAdj", "roast")
        if dish_type == "salmon":
            initial_state = initial_state.add_rel(dish_type, "isAdj", "grilled")
        if dish_type == "pork":
            initial_state = initial_state.add_rel(dish_type, "isAdj", "smoked")

        # These concepts are "in scope" meaning it is OK to say "the X"
        initial_state = initial_state.add_rel(dish_type, "conceptInScope", "true")

        if dish_type in menu_types:
            initial_state = initial_state.add_rel(dish_type, "on", "menu")
        else:
            initial_state = initial_state.add_rel(dish_type, "priceUnknownTo", "user")
            initial_state = initial_state.add_rel(dish_type, "specializes", "special")


        # Create the food instances
        for i in range(3):
            # Create an instance of this food
            food_instance = dish_type + str(i)
            initial_state = initial_state.add_rel(food_instance, "instanceOf", dish_type)
            # All foods are for 2
            initial_state = initial_state.add_rel(food_instance, "maxCapacity", 2)

            # The kitchen is where all the food is
            initial_state = initial_state.add_rel("kitchen1", "contain", food_instance)
            initial_state = initial_state.add_rel("restaurant", "have", food_instance)

    initial_state = initial_state.add_rel("hi", "hasName", "Hawaii")
    initial_state = initial_state.add_rel("howdy", "hasName", "howdy")
    initial_state = initial_state.add_rel("restaurant", "have", "special")
    initial_state = initial_state.add_rel("restaurant", "hasName", "restaurant")
    initial_state = initial_state.add_rel("bill1", "instanceOf", "bill")
    initial_state = initial_state.add_rel("bill1", "instanceOf", "check")
    initial_state = initial_state.add_rel("user", "have", "bill1")
    initial_state = initial_state.add_rel(0, "valueOf", "bill1")
    initial_state = initial_state.add_rel("room", "contains", "user")

    # Give the parent and the son each their own order (which might be empty) so they can say things like
    # "My order is x" or "Could we restart my order?", etc
    initial_state = initial_state.add_rel("order1", "instanceOf", "order")
    initial_state = initial_state.add_rel("user", "have", "order1")
    initial_state = initial_state.add_rel("order2", "instanceOf", "order")
    initial_state = initial_state.add_rel("son1", "have", "order2")
    initial_state = initial_state.add_rel("order3", "instanceOf", "order")
    initial_state = initial_state.add_rel(("user", "son1"), "have", "order3")

    initial_state = initial_state.add_rel("son1", "instanceOf", "son")
    initial_state = initial_state.add_rel("son1", "hasName", "Johnny")
    initial_state = initial_state.add_rel("user", "instanceOf", "person")
    initial_state = initial_state.add_rel("user", "hasName", "you")
    initial_state = initial_state.add_rel("user", "have", "son1")
    initial_state = initial_state.add_rel("user", "heardSpecials", "false")

    initial_state = initial_state.add_rel("adjective", "specializes", "thing")
    initial_state = initial_state.add_rel("roast", "specializes", "adjective")

    return initial_state


def error_priority(error_string):
    system_priority = perplexity.messages.error_priority(error_string)
    if system_priority is not None:
        return system_priority
    else:
        # Must be a message from our code
        error_constant = error_string[1][0]
        priority = error_priority_dict.get(error_constant, error_priority_dict["defaultPriority"])
        priority += error_string[2] * error_priority_dict["success"]
        return priority


error_priority_dict = {
    "verbDoesntApply": 960,
    "defaultPriority": 1000,
    # This is just used when sorting to indicate no error, i.e. success.
    # Nothing should be higher because higher is used for phase 2 errors
    "success": 10000000
}


class EslEvents(object):
    def interaction_end(self, ui, interaction_records, last_phrase_response):
        if last_phrase_response == "":
            return [(perplexity.response.ResponseLocation.last, ui.state.get_reprompt(return_first=False))]

    def world_new(self):
        return [(perplexity.response.ResponseLocation.first, "(Note: This game is designed to practice English: type in actual sentences you'd say in real life. If you get stuck, ask yourself what you would really say in the real world and type that.)\n\n" + "You’re going to a restaurant with your son, Johnny, who is vegetarian and too scared to order by himself. Get a table and buy lunch for both of you. You have 20 dollars in cash.\nHost: Hello! How can I help you today?")]


def ui(loading_info=None, file=None, user_output=None, debug_output=None):
    scriptPath = os.path.dirname(os.path.realpath(__file__))
    best_parses_file = os.path.join(scriptPath, "tutorial.bestparse")
    loaded_state = None
    if loading_info is not None:
        if loading_info.get("Version", None) != 1:
            raise LoadException()

        if file is not None:
            loaded_state = load_world_state(file)

    vocabulary.synonyms = {
        "_item_n_of": "_thing_n_of-about",
        "_meal_n_1": "_dish_n_of",
        "_lunch_n_1": "_dish_n_of",
        "_dinner_n_1": "_dish_n_of",
        "_breakfast_n_1": "_dish_n_of",
        "_main_n_1": "_dish_n_of",
        "_choice_n_of": "_dish_n_of",
        "_speciality_n_1": "_dish_n_of",
        "_option_n_1": "_dish_n_of"
    }
    ui = UserInterface("esl",
                        reset,
                        vocabulary,
                        message_function=generate_custom_message,
                        error_priority_function=error_priority,
                        scope_function=in_scope,
                        scope_init_function=in_scope_initialize,
                        loaded_state=loaded_state,
                        user_output=user_output,
                        debug_output=debug_output,
                        best_parses_file=best_parses_file,
                        events=EslEvents())

    return ui


def hello_world():
    user_interface = ui()
    user_interface.user_output(user_interface.output_sorted_responses(user_interface.events.world_new()))

    while user_interface:
        user_interface = user_interface.default_loop()


pipeline_logger = logging.getLogger('Pipeline')


if __name__ == '__main__':

    # test_state = reset()

    # for item in test_state.all_rel("isAdj"):
    #     if item[1] == "roast":
    #         print(item)
    #
    # concept = ESLConcept("chicken")
    # concept = concept.add_criteria(rel_subjects, "isAdj", "roast")
    # print(concept.instances(None, test_state))

    ShowLogging("Pipeline")
    # ShowLogging("ChatGPT")
    # ShowLogging("Testing")
    # ShowLogging("Execution")
    # ShowLogging("Generation")
    # ShowLogging("SString")
    # ShowLogging("UserInterface")
    # ShowLogging("Determiners")
    ShowLogging("SolutionGroups")
    ShowLogging("Transformer")

    hello_world()
