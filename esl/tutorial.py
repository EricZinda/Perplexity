import os
import sys
import perplexity.messages
from esl.esl_planner import do_task
from esl.esl_planner_description import convert_to_english
from perplexity.generation import english_for_delphin_variable
from perplexity.plurals import VariableCriteria, GlobalCriteria, NegatedPredication, GroupVariableValues
from perplexity.predications import combinatorial_predication_1, in_style_predication_2, \
    lift_style_predication_2, concept_meets_constraint
from perplexity.set_utilities import Measurement
from perplexity.solution_groups import declared_determiner_infos, optimize_determiner_infos, \
    create_group_variable_values
from perplexity.sstring import s
from perplexity.system_vocabulary import system_vocabulary, quantifier_raw
from perplexity.transformer import TransformerMatch, TransformerProduction, PropertyTransformerMatch, \
    PropertyTransformerProduction, ConjunctionMatchTransformer, ConjunctionProduction
from perplexity.tree import find_predication_from_introduced, get_wh_question_variable, \
    gather_scoped_variables_from_tree_at_index, TreePredication
from perplexity.user_interface import UserInterface
from perplexity.utilities import ShowLogging, sentence_force
from perplexity.variable_binding import VariableBinding, VariableData
from perplexity.vocabulary import Predication, EventOption, Transform, ValueSize
from esl.worldstate import *

vocabulary = system_vocabulary()


# ******** Helpers ************
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
    concept_count, concept_in_scope_count, instance_count, instance_in_scope_count = count_of_instances_and_concepts(
        context, state_list[0], list(x_what_individuals_set))
    return concept_meets_constraint(context,
                                    state_list[0].get_binding("tree").value[0],
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
        valid_types = ["food", "drink", "table", "menu", "bill", "check"]

    store_objects = [object_to_store(x) for x in x_objects]
    for store in store_objects:
        if not sort_of(state, store, valid_types):
            return False

    return True


def min_from_variable_group(variable_group):
    return variable_group.variable_constraints.min_size if variable_group.variable_constraints is not None else 1


# **** Transforms ****

# Convert "That will be all" to "no"
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
    target_match = TransformerMatch(name_pattern=["regex:_v_", "unknown"],
                                    name_capture="target_name",
                                    args_pattern=["e", "**"],
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
    conjunction_match = ConjunctionMatchTransformer(transformer_list=[noun_match, measure_match, much_many_match])

    return TransformerMatch(name_pattern="udef_q",
                            args_pattern=["x", conjunction_match, "*"],
                            args_capture=[None, None, "udef_body"],
                            properties_production=underspecify_plurality_production,
                            production=count_production,
                            removed=["measure", "much-many_a"])


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
    production = TransformerProduction(name="$|name|_request", args={"ARG0": "$e1", "ARG1": "$x1", "ARG2": "$x2"})
    target = TransformerMatch(name_pattern="*", name_capture="name", args_pattern=["e", "x", "x"],
                              args_capture=[None, "x1", "x2"])
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
                                             x_binding_1.value[0].concept_name == "generic_entity"

    # x_binding_1.value can be None if a transform removes a generic_entity() that sets its value
    if (single_value_is_generic_entity_concept or x_binding_1.value is None) and is_computer_type(x_binding_2.value):
        yield state.record_operations([RespondOperation(f"You are welcome! {state.get_reprompt()}")])


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
        if person == 2 and value == "restaurant":
            return True
        if person == 1 and is_user_type(value):
            return True
        else:
            context.report_error(["dontKnowActor", x_who_binding.variable.name, state.get_reprompt()])

    def unbound_variable():
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
            context.report_error(["notAThing", x_binding.value, x_binding.variable.name, state.get_reprompt()])
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
            context.report_error(["notAThing", x_binding.value, x_binding.variable.name, state.get_reprompt()])
            return False

    def unbound():
        yield ESLConcept("generic_entity")

    yield from combinatorial_predication_1(context, state, x_binding, bound, unbound)


@Predication(vocabulary, names=["_okay_a_1", "_all+right_a_1"])
def _okay_a_1(context, state, i_binding, h_binding):
    yield from context.call(state, h_binding)


@Predication(vocabulary, names=["abstr_deg"])
def abstr_deg(context, state, x_binding):
    def bound(val):
        if val == ESLConcept("degree"):
            return True
        else:
            context.report_error(["notAThing", x_binding.value, x_binding.variable.name, state.get_reprompt()])
            return False

    def unbound():
        yield state.set_x(x_binding.variable.name, (ESLConcept("degree"),))

    yield from combinatorial_predication_1(context, state, x_binding, bound, unbound)


@Predication(vocabulary, names=["compound"])
def compound(context, state, e_binding, x_left_binding, x_right_binding):
    if x_left_binding.value is not None and x_right_binding.value is not None:
        if x_left_binding.value[0] == x_right_binding.value[0]:
            yield state
        elif is_concept(x_right_binding.value[0]):
            # Records that predication index X is a disjunction
            context.set_disjunction()

            # Since these are *alternative* interpretations, they need to be in different lineages
            # just like if there were separate predication implementations yielding them
            interpretation_id = 0
            tree_lineage_binding = state.get_binding("tree_lineage")
            tree_lineage = "" if tree_lineage_binding.value is None else tree_lineage_binding.value[0]

            for concept_state in adjective_default_concepts(x_right_binding.value[0].concept_name, context, state, x_left_binding):
                yield concept_state.set_x("tree_lineage", (f"{tree_lineage}.1",))

            for instance_state in adjective_default_instances(x_right_binding.value[0].concept_name, context, state, x_left_binding):
                yield instance_state.set_x("tree_lineage", (f"{tree_lineage}.2",))


# @Predication(vocabulary, names=["_for_x_cause"])
# def _for_x_cause(context, state, e_introduced, h_left_binding, h_right_binding):
#     if isinstance(h_left_binding, TreePredication) and h_left_binding.name == "greet":
#         for solution in context.call(state, h_right_binding):
#             yield solution


@Predication(vocabulary, names=["_can_v_modal"])
def test_can_v_modal(context, state, e_binding, h_target_binding):
    if False:
        yield None

@Predication(vocabulary, names=["_for_p"])
def _for_p_event(context, state, e_binding, e_target_binding, x_for_binding):
    yield state.add_to_e(e_target_binding.variable.name, "for", {"Value": x_for_binding.value, "Originator": context.current_predication_index()})


# Checks to make sure a "for" construct is valid, and determines what kind of "for" construct it is
# Returns True | False, for_type, x_what_type
def for_check(state, context, x_what_list, x_for_list):
    # values must be all instances or all concepts so we only need to check the type of the first
    x_what_type = perplexity.predications.value_type(x_what_list[0])

    # If multiple items are given, they are all the same scenario or we fail
    for_types = set()
    for_type = None
    store_whats = [object_to_store(value) for value in x_what_list]
    for item in x_for_list:
        if isinstance(item, numbers.Number):
            # if 'for' is a number like: "Table for 2" or "walk for a mile" it means "to the extent or amount of"
            #       If x is an instance, this effectively means "has the capacity of" and it just needs to be check if it has that capacity
            for_types.add("to the extent or amount of")

            # We support "Table for 2" or "steak for N" but nothing
            # else with this construction. "table for 2 and 4" doesn't make sense
            if len(x_for_list) > 1:
                context.report_error(["unexpected", state.get_reprompt()])
                return False, for_type, x_what_type

            if x_what_type == perplexity.predications.VariableValueType.instance:
                # If it is an instance, check to make sure it can handle that capacity
                for what in store_whats:
                    for value in rel_objects(state, what, "maxCapacity"):
                        if value < x_for_list[0]:
                            context.report_error(
                                ['errorText', f"{convert_to_english(state, what)} is not for {convert_to_english(state, x_for_list[0])}.",
                                 state.get_reprompt()])
                            return False, for_type, x_what_type

        elif is_user_type(item):
            # if 'for' refers to a person like "Table for my son and I", "steak for me", etc. it means "intended to belong to"
            # Since "what" is collective, they both have to have it
            #       If x is an instance, this effectively means "was ordered for"
            #       Since this is an instance and not a concept
            #       "steak for my son" is really equivalent to saying "my son's steak"
            #       "is this steak for my son and I?" can be checked by seeing if we both have it
            for_types.add("intended to belong to")

            if x_what_type == perplexity.predications.VariableValueType.instance:
                # the people in "for" must have it *together*, so we check if they, together, have it
                if (object_to_store(x_for_list), store_whats) not in state.all_rel("have"):
                    context.report_error(
                        ['errorText', f"Host: That is not for both {'and'.join(store_whats)}.", state.get_reprompt()])
                    return False, for_type, x_what_type

        elif sort_of(state, object_to_store(item), "course"):
            # if 'for' refers to a course like "steak for my main course|dinner" it means "in order to obtain, gain, or acquire" (as in "a suit for alimony")
            #       If x is an instance, this effectively means "can be used for" which is true as long as the "for" is "main course/dinner/appetizer/etc"
            for_types.add("in order to obtain")

            # We'll accept "I want the steak for my appetizer" but not for two courses
            if len(x_for_list) > 1:
                context.report_error(["unexpected", state.get_reprompt()])
                return False, for_type, x_what_type

            if not sort_of(state, store_whats, ["food"]):
                context.report_error(["unexpected", state.get_reprompt()])
                return False, for_type, x_what_type


            else:
                return False

        if len(for_types) > 1:
            context.report_error(["unexpected", state.get_reprompt()])
            return False, for_type, x_what_type

        elif len(for_types) == 0:
            context.report_error(["unexpected", state.get_reprompt()])
            return False, for_type, x_what_type

        else:
            for_type = next(iter(for_types))

        return True, for_type, x_what_type


# Called to actually update the state when a "for" construct is used so that the
# conceptual value has the meaning of the "for" included in it as criteria
#
# Returns an updated version of the solution state that has x_what_binding
# updated to include the information that x_for_binding added to it
def for_update_state(solution, x_what_type, for_type, x_what_binding, x_for_list):
    if x_what_type == perplexity.predications.VariableValueType.instance:
        # Already fully checked above
        return solution

    else:
        # Add the appropriate "for" information to the concepts
        x_what_values = x_what_binding.value
        if for_type == "to the extent or amount of":
            # x_for_list was already checked to make sure it was only one number
            x_for_value = x_for_list[0]

            # x_what_binding could be multiple like "a steak and a salad for 2"
            modified_values = [value.add_criteria(rel_subjects_greater_or_equal, "maxCapacity", x_for_value) for value
                               in x_what_values]

        elif for_type == "intended to belong to":
            if sort_of(solution, x_what_values, "table"):
                # If "what" is a table, we've already made sure there is only one above
                # and we assume they are talking about "capacity" not ownership so:
                modified_values = [x_what_values[0].add_criteria(rel_subjects, "maxCapacity", len(x_for_list))]

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
@Predication(vocabulary, names=["_for_p"], arguments=[("e",), ("x", ValueSize.all), ("x", ValueSize.all)])
def _for_p(context, state, e_binding, x_what_binding, x_for_binding):
    def both_bound_function(x_what, x_for):
        nonlocal for_type, x_what_type
        result, for_type, x_what_type = for_check(state, context, x_what, x_for)
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
    for solution in lift_style_predication_2(context, state, x_what_binding, x_for_binding,
                                             both_bound_function,
                                             x_what_unbound,
                                             x_for_unbound):
        yield for_update_state(solution, x_what_type, for_type, x_what_binding, x_for_binding.value)


@Predication(vocabulary, names=["_cash_n_1"])
def _cash_n_1(context, state, x_bind):
    def bound(val):
        return val == "cash"

    def unbound():
        yield "cash"

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


@Predication(vocabulary, names=["_order_n_of"])
def _order_n_of(context, state, x_order_binding, x_of_what_binding):
    def both_bound(order, of_what):
        return sort_of(state, object_to_store(order), ["of_what"])

    def of_what_bound(of_what):
        if sort_of(state, object_to_store(of_what), ["food"]):
            yield of_what

    def order_bound(order):
        if sort_of(state, object_to_store(order), ["food"]):
            yield order

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
        return sort_of(state, object_to_store(order), [object_to_store(of_what)])

    def of_what_bound(of_what):
        if sort_of(state, object_to_store(of_what), ["water"]):
            yield of_what

    def glass_bound(glass):
        if sort_of(state, object_to_store(glass), ["water"]):
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
            context.report_error(["notAThing", x_binding.value, x_binding.variable.name, state.get_reprompt()])
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
            context.report_error(["notAThing", x_binding.value, x_binding.variable.name, state.get_reprompt()])
            return False

    def unbound():
        yield "dollar"

    yield from combinatorial_predication_1(context, state, x_binding, bound, unbound)


@Predication(vocabulary,
             names=["unknown"],
             phrases={
                "Hi, table for two, please": {'SF': 'prop', 'TENSE': 'untensed', 'MOOD': 'indicative', 'PROG': '-', 'PERF': '-'},
                "a table for 2": {'SF': 'prop', 'TENSE': 'untensed', 'MOOD': 'indicative'},
                "a table for 2, please!": {'SF': 'prop', 'TENSE': 'untensed', 'MOOD': 'indicative', 'PROG': '-', 'PERF': '-'},
                "2": {'SF': 'prop-or-ques'},
                "Johnny and me": {'SF': 'prop-or-ques'},
                "yes": {'SF': 'prop-or-ques'},
                "You too.": {'SF': 'prop'}
             },
             properties=[{'SF': 'prop-or-ques'},
                         {'SF': 'prop', 'TENSE': 'untensed', 'MOOD': 'indicative'},
                         {'SF': 'prop', 'TENSE': 'untensed', 'MOOD': 'indicative', 'PROG': '-', 'PERF': '-'},
                         {'SF': 'prop'}],
             arguments=[("e",), ("x", ValueSize.all)])
def unknown(context, state, e_binding, x_binding):
    operations = state.handle_world_event(context, ["unknown", x_binding.value])
    if operations is not None:
        yield state.record_operations(operations)

    else:
        context.report_error(["formNotUnderstood", "unknown"])


@Predication(vocabulary, names=["unknown"])
def unknown_eu(context, state, e_binding, u_binding):
    yield state


def greetings():
    return ["hello", "hi", "howdy"]
#
#
# @Predication(vocabulary, names=["greet"])
# def greet(context, state, c_arg, i_unused):
#     yield state
#
#
# @Predication(vocabulary, names=["discourse"])
# def discourse(context, state, i_unused, h_left_binding, h_right_binding):
#     if isinstance(h_left_binding, TreePredication) and h_left_binding.name == "greet":
#         for solution in context.call(state, h_right_binding):
#             yield solution


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
    yield state.record_operations(state.handle_world_event(context, ["yes"]))


@Predication(vocabulary, names=["_no_a_1", "_nope_a_1"])
def _no_a_1(context, state, i_binding, h_binding):
    yield state.record_operations(state.handle_world_event(context, ["no"]))


# This is not a DELPH-IN predication. It is generated by transforms to phrases like "that will be all"
@Predication(vocabulary, names=["no_standalone"])
def no_standalone(context, state, e_binding):
    yield state.record_operations(state.handle_world_event(context, ["no"]))


@Predication(vocabulary, names=["thing"])
def thing_concepts(context, state, x_binding):
    def bound_variable(value):
        if is_type(state, object_to_store(value)):
            return True
        else:
            context.report_error(["notAThing", x_binding.value, x_binding.variable.name, state.get_reprompt()])
            return False

    # Yield each layer of specializations as a disjunction
    def unbound_variable():
        yield from concept_disjunctions_reverse(state, "thing")

    yield from combinatorial_predication_1(context, state, x_binding, bound_variable, unbound_variable)


@Predication(vocabulary, names=["thing"])
def thing_instances(context, state, x_binding):
    def bound_variable(value):
        if is_instance(state, object_to_store(value)):
            return True
        else:
            context.report_error(["notAThing", x_binding.value, x_binding.variable.name, state.get_reprompt()])
            return False

    def unbound_variable():
        for item in state.all_instances():
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
    yield from adjective_default_concepts(adjective_type, context, state, x_binding)


@Predication(vocabulary, names=["match_all_a"], matches_lemma_function=handles_adjective)
def match_all_a_instances(adjective_type, context, state, e_introduced, x_binding):
    yield from adjective_default_instances(adjective_type, context, state, x_binding)


def handles_noun(state, noun_lemma):
    handles = ["thing"] + list(all_specializations(state, "thing"))
    return noun_lemma in handles


@Predication(vocabulary, names=["match_all_n"], matches_lemma_function=handles_noun)
def match_all_n_concepts(noun_type, context, state, x_binding):
    def bound_variable(value):
        if sort_of(state, object_to_store(value), noun_type):
            return True

        else:
            context.report_error(["notAThing", x_binding.value, x_binding.variable.name, state.get_reprompt()])
            return False

    def unbound_variable_concepts():
        yield from concept_disjunctions_reverse(state, noun_type)

    # Then yield a combinatorial value of all types
    for new_state in combinatorial_predication_1(context, state, x_binding, bound_variable, unbound_variable_concepts):
        yield new_state


@Predication(vocabulary, names=["match_all_n"], matches_lemma_function=handles_noun)
def match_all_n_instances(noun_type, context, state, x_binding):
    def bound_variable(value):
        if sort_of(state, value, noun_type):
            return True
        else:
            context.report_error(["notAThing", x_binding.value, x_binding.variable.name, state.get_reprompt()])
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
            context.report_error(["notAThing", x_binding.value, x_binding.variable.name,state.get_reprompt()])
            return False

    def unbound_variable_instances():
        for item in all_instances(state, noun_type):
            yield item

    # Make "the soup" return all the instances for a concept without any "the-type" restrictions IF the concept is in scope
    # This is to make pure fact checking predications like "have" and "ordered" be able to deal with instances and not have to
    # resort to concepts
    if rel_check(state, noun_type, "conceptInScope", "true") and \
            x_binding.variable.quantifier.global_criteria == GlobalCriteria.all_rstr_meet_criteria:
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


def adjective_default_concepts(adjective_type, context, state, x_binding):
    def bound_variable(value):
        if is_concept(value):
            if rel_check(state, object_to_store(x_binding.value[0]), "isAdj", adjective_type):
                return True

            else:
                context.report_error(["notAThing", x_binding.value, x_binding.variable.name, state.get_reprompt()])
                return False

    def unbound_variable_concepts():
        # Phrases like "What is a green food?"
        for item in rel_subjects(state, "isAdj", adjective_type):
            if is_concept(item):
                yield item

    # Then yield a combinatorial value of all types
    for new_state in combinatorial_predication_1(context, state, x_binding, bound_variable, unbound_variable_concepts):
        yield new_state


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
                    context.report_error(["notAThing", x_binding.value, x_binding.variable.name, state.get_reprompt()])
                    return False

    def unbound_variable_instances():
        for item in rel_subjects(state, "isAdj", adjective_type):
            if not is_concept(item):
                yield item

    yield from combinatorial_predication_1(context, state, x_binding, bound_variable, unbound_variable_instances)


# 'vegetarian food" is modelled as anything that has a "veggie" base class, not
# things that have a "hasAdj" relationship
@Predication(vocabulary, names=["_vegetarian_a_1"])
def _vegetarian_a_1_concepts(context, state, e_introduced_binding, x_target_binding):
    yield from match_all_n_concepts("veggie", context, state, x_target_binding)


@Predication(vocabulary, names=["_vegetarian_a_1"])
def _vegetarian_a_1_instances(context, state, e_introduced_binding, x_target_binding):
    yield from match_all_n_instances("veggie", context, state, x_target_binding)


class PastParticiple:
    def __init__(self, predicate_name_list, lemma):
        self.predicate_name_list = predicate_name_list
        self.lemma = lemma

    def predicate_function(self, context, state, e_introduced_binding, i_binding, x_target_binding):
        def bound(value):
            if (object_to_store(value), self.lemma) in state.all_rel("isAdj"):
                return True

            else:
                context.report_error(["not_adj", self.lemma,state.get_reprompt()])
                return False

        def unbound():
            for i in state.all_rel("isAdj"):
                if object_to_store(i[1]) == self.lemma:
                    yield i[0]

        yield from combinatorial_predication_1(context, state, x_target_binding,
                                               bound,
                                               unbound)


grilled = PastParticiple(["_grill_v_1"], "grilled")
roasted = PastParticiple(["_roast_v_cause"], "roasted")
smoked = PastParticiple(["_smoke_v_1"], "smoked")


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
             names=smoked.predicate_name_list,
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
    yield from smoked.predicate_function(context, state, e_introduced_binding, i_binding, x_target_binding)


@Predication(vocabulary, names=("_on_p_loc",))
def on_p_loc(context, state, e_introduced_binding, x_actor_binding, x_location_binding):
    def check_item_on_item(item1, item2):
        if (item1, item2) in state.all_rel("on"):
            return True
        else:
            context.report_error(["notOn", item1, item2, state.get_reprompt()])

    def all_item1_on_item2(item2):
        for i in state.all_rel("on"):
            if i[1] == object_to_store(item2):
                yield store_to_object(state,i[0])

    def all_item2_containing_item1(item1):
        for i in state.all_rel("on"):
            if i[0] == item1:
                yield i[1]

    yield from in_style_predication_2(context,
                                      state,
                                      x_actor_binding,
                                      x_location_binding,
                                      check_item_on_item,
                                      all_item1_on_item2,
                                      all_item2_containing_item1)


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
            if valid_player_request(state, [x_object], ["food", "bill", "check"]):
                return True
            else:
                context.report_error(["errorText", "You can't pay for that."])
                return False

    def actor_unbound(x_object):
        # What/Who can pay for x?
        found = False
        if valid_player_request(state, [x_object], ["food", "bill", "check"]):
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
        if final_state is None:
            yield []
        else:
            yield [final_state]


# All of the "can/couldpay with" alternatives are interpreted as "I want to pay with cash/card"
@Predication(vocabulary,
             names=["_pay_v_for", "_pay_v_for_request"],
             phrases={
                "I want to pay with cash": {'SF': 'prop', 'TENSE': 'pres', 'MOOD': 'indicative', 'PROG': '-', 'PERF': '-'},
                "I will pay with cash": {'SF': 'prop', 'TENSE': 'fut', 'MOOD': 'indicative', 'PROG': '-', 'PERF': '-'},
                "Can I pay with cash": {'SF': 'ques', 'TENSE': 'pres', 'MOOD': 'indicative', 'PROG': '-', 'PERF': '-'},
                "Could I pay with cash": {'SF': 'ques', 'TENSE': 'past', 'MOOD': 'indicative', 'PROG': '-', 'PERF': '-'}
             },
             properties=[{'SF': 'prop', 'TENSE': 'fut', 'MOOD': 'indicative', 'PROG': '-', 'PERF': '-'},
                         {'SF': 'ques', 'TENSE': 'pres', 'MOOD': 'indicative', 'PROG': '-', 'PERF': '-'},
                         {'SF': 'prop', 'TENSE': 'pres', 'MOOD': 'indicative', 'PROG': '-', 'PERF': '-'},
                         {'SF': 'ques', 'TENSE': 'past', 'MOOD': 'indicative', 'PROG': '-', 'PERF': '-'}],
             handles=[("With", EventOption.required)])
def _pay_v_for(context, state, e_introduced_binding, x_actor_binding, i_binding1, i_binding2):
    if not state.sys["responseState"] == "way_to_pay":
        yield do_task(state, [("respond", context, "It's not time to pay yet.")])
        return
    if not e_introduced_binding.value["With"]["Value"] in ["cash", "card"]:
        yield do_task(state, [("respond", context, "You can't pay with that.")])
        return

    yield state.record_operations(state.handle_world_event(context, ["unknown", (e_introduced_binding.value["With"]["Value"], )]))


@Predication(vocabulary,
             names=["_want_v_1"],
             phrases={
                "we'd like a table for 2": {'SF': 'prop', 'TENSE': 'tensed', 'MOOD': 'indicative', 'PROG': '-', 'PERF': '-'},
                "I want a steak": {'SF': 'prop', 'TENSE': 'pres', 'MOOD': 'indicative', 'PROG': '-', 'PERF': '-'},
                "I'd like a steak": {'SF': 'prop', 'TENSE': 'tensed', 'MOOD': 'indicative', 'PROG': '-', 'PERF': '-'},
                "My son would like a salad": {'SF': 'prop', 'TENSE': 'tensed', 'MOOD': 'indicative', 'PROG': '-', 'PERF': '-'}
             },
             properties=[
                {'SF': 'prop', 'TENSE': ['pres', 'tensed'], 'MOOD': 'indicative', 'PROG': '-', 'PERF': '-'}
             ],
             arguments=[("e",), ("x", ValueSize.all), ("x", ValueSize.all)])
def _want_v_1(context, state, e_introduced_binding, x_actor_binding, x_object_binding):
    yield from want_v_1_helper(context, state, e_introduced_binding, x_actor_binding, x_object_binding)


# This is its own raw function so it can be called by many different predications and not get checked
# for verb properties (like sentence_force)
def want_v_1_helper(context, state, e_introduced_binding, x_actor_binding, x_object_binding):
    def criteria_bound(x_actor, x_object):
        if is_user_type(x_actor):
            return True

        elif (x_actor, x_object) in state.all_rel("want"):
                return True

        else:
            context.report_error(["notwant", "want", x_actor, state.get_reprompt()])
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
             names=["solution_group__want_v_1"],
             properties_from=_want_v_1)
def want_group(context, state_list, e_introduced_binding_list, x_actor_variable_group, x_what_variable_group):
    yield from want_group_helper(context, state_list, e_introduced_binding_list, x_actor_variable_group, x_what_variable_group)


def want_group_helper(context, state_list, e_introduced_binding_list, x_actor_variable_group, x_what_variable_group):
    current_state = copy.deepcopy(state_list[0])
    if is_concept(x_actor_variable_group.solution_values[0]):
        # We don't want to deal with conceptual actors, fail this solution group
        # and wait for the one with real actors
        yield []

    # We do have lots of places where we deal with conceptual "wants", such as: "I want the menu", "I'll have a steak"
    # In fact, we *never* deal with wanting a particular instance because that would mean "I want that particular steak right there"
    # and we don't support that
    # These are concepts. Only need to check the first because:
    # If one item in the group is a concept, they all are
    # x_what_variable_group.solution_values[0].value can be None if it is scoped under negation
    if x_what_variable_group.solution_values[0].value is not None and is_concept(x_what_variable_group.solution_values[0].value[0]):
        # We first check to make sure the constraints are valid for this concept.
        # Because in "I want x", 'x' is always a concept, but the constraint is on the instances
        # (as in "I want a steak" meaning "I want 1 instance of the concept of steak", we tell
        # check_concept_solution_group_constraints to check instances via check_concepts=False
        if check_concept_solution_group_constraints(context, state_list, x_what_variable_group, check_concepts=False):
            # Even though it is only one thing, they could have said something like "We want steaks" so they really want more than one
            # Give them the minimum number by adding a card() predication into the concept
            #   - card(state, c_number, e_binding, x_binding):
            # args = [x_what_variable_group.variable_constraints.min_size, "e999", first_x_what_binding_value.variable_name]
            # first_x_what_binding_value = first_x_what_binding_value.add_modifier(TreePredication(0, "card", args, arg_names=["CARG", "ARG0", "ARG1"]))
            # actor_values = [x.value for x in x_actor_variable_group.solution_values]
            current_state = do_task(current_state.world_state_frame(),
                                    [('satisfy_want', context, variable_group_values_to_list(x_actor_variable_group), variable_group_values_to_list(x_what_variable_group), min_from_variable_group(x_what_variable_group))])
            if current_state is None:
                yield []
            else:
                yield [current_state]

        else:
            yield []
    else:
        yield []


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
        if final_state is None:
            yield []
        else:
            yield[final_state]


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
            if is_concept(x_object) and x_object.concept_name in ["menu"]:
                return True

            else:
                context.report_error(["errorText", "Sorry, I can't show you that"])

        else:
            context.report_error(["dontKnowHow"])
            return

    def wanters_of_obj(x_object):
        # not currently going to support asking who is seating someone
        context.report_error(["formNotUnderstood", "_show_v_1"])
        return

    def wanted_of_actor(x_actor):
        context.report_error(["formNotUnderstood", "_show_v_1"])
        return

    yield from in_style_predication_2(context, state, x_to_actor_binding, x_target_binding, bound,
                                      wanters_of_obj, wanted_of_actor)


@Predication(vocabulary, names=["solution_group__show_v_1", "solution_group__show_v_1_able"])
def _show_v_cause_group(context, state_list, e_introduced_binding, x_actor_variable_group, x_target_variable_group, x_to_actor_variable_group):
    # Only need to check constraints on x_target_variable_group since it is the only variable that is a concept
    # The player is asking to be shown *instances* so check_concepts = False
    if not check_concept_solution_group_constraints(context, state_list, x_target_variable_group, check_concepts=False):
        yield []
        return

    to_actor_list = variable_group_values_to_list(x_to_actor_variable_group)
    show_list = variable_group_values_to_list(x_target_variable_group)
    current_state = do_task(state_list[0].world_state_frame(),
                            [('satisfy_want', context, to_actor_list, show_list, min_from_variable_group(x_target_variable_group))])
    if current_state is None:
        yield []

    else:
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
        # not currently going to support asking who is seating someone
        context.report_error(["formNotUnderstood", "_seat_v_cause"])
        return

    def wanted_of_actor(x_actor):
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
    if new_state is None:
        yield []

    else:
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


@Predication(vocabulary, names=["_today_a_1"])
def _today_a_1(context, state, e_introduced_binding, x_binding):
    def bound_variable(value):
        if value in ["today"]:
            return True

        else:
            context.report_error(["notAThing", x_binding.value, x_binding.variable.name,state.get_reprompt()])
            return False

    def unbound_variable():
        yield "today"

    yield from combinatorial_predication_1(context, state, x_binding, bound_variable, unbound_variable)


@Predication(vocabulary, names=["time_n"])
def time_n(context, state, x_binding):
    def bound_variable(value):
        if value in ["today", "yesterday", "tomorrow"]:
            return True
        else:
            context.report_error(["notAThing", x_binding.value, x_binding.variable.name,state.get_reprompt()])
            return False

    def unbound_variable():
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


@Predication(vocabulary, names=["_just_a_1"])
def _just_a_1(context, state, e_introduced_binding, e_binding):
    yield state


@Predication(vocabulary, names=["_just_a_1"])
def _just_a_1(context, state, e_introduced_binding, x_binding):
    yield state


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
            context.report_error(["unexpected", state.get_reprompt()])
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
    context.report_error(["unexpected", state.get_reprompt()])
    if False:
        yield None


@Predication(vocabulary, names=["solution_group__sit_v_down", "solution_group__sit_v_1"])
def _sit_v_down_future_group(context, state_list, e_list, x_actor_variable_group):
    # The planner will only satisfy a want wrt the players
    task = ('satisfy_want', context, variable_group_values_to_list(x_actor_variable_group), [[ESLConcept("table")]], 1)
    final_state = do_task(state_list[0].world_state_frame(), [task])
    if final_state:
        yield [final_state]

    else:
        yield []


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

    context.report_error(["unexpected", state.get_reprompt()])
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
            context.report_error(["unexpected", state.get_reprompt()])
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
            context.report_error(["unexpected", state.get_reprompt()])
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
        #
        actors = variable_group_values_to_list(x_actor_variable_group)
        task = ('satisfy_want', context, actors, [(ESLConcept("table"),)] * len(actors), 1)
        final_state = do_task(state_list[0].world_state_frame(), [task])
        if final_state:
            yield [final_state]
        else:
            yield []


@Predication(vocabulary,
             names=["_see_v_1_able"],
             phrases={
                "Can I see a menu?": {'SF': 'ques', 'TENSE': 'pres', 'MOOD': 'indicative', 'PROG': '-', 'PERF': '-'}  # -> implied request
             },
             properties=[
                {'SF': 'ques', 'TENSE': 'pres', 'MOOD': 'indicative', 'PROG': '-', 'PERF': '-'}
             ])
def _see_v_1_able(context, state, e_introduced_binding, x_actor_binding, x_object_binding):
    def both_bound_prediction_function(x_actor, x_object):
        if is_user_type(x_actor):
            if valid_player_request(state, [x_object], valid_types=["menu"]):
                return True
            else:
                context.report_error(["unexpected", state.get_reprompt()])
                return False

        else:
            # Anything about "you/they will have" is not good english
            context.report_error(["unexpected", state.get_reprompt()])
            return False

    def actor_unbound(x_object):
        # Anything about "what will x have
        context.report_error(["unexpected", state.get_reprompt()])
        if False:
            yield None

    def object_unbound(x_actor):
        context.report_error(["unexpected", state.get_reprompt()])
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
    context.report_error(["unexpected", state.get_reprompt()])
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
        yield []


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
            if valid_player_request(state, [x_object], valid_types=["menu"]):
                return True
            else:
                context.report_error(["unexpected", state.get_reprompt()])
                return False

        else:
            # Anything about "you/they will have" is not good english
            context.report_error(["unexpected", state.get_reprompt()])
            return False

    def actor_unbound(x_object):
        # Anything about "what will x have
        context.report_error(["unexpected", state.get_reprompt()])
        if False:
            yield None

    def object_unbound(x_actor):
        context.report_error(["unexpected", state.get_reprompt()])
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
    context.report_error(["unexpected", state.get_reprompt()])


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
        yield []


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
    context.report_error(["unexpected", state.get_reprompt()])
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
    context.report_error(["unexpected", state.get_reprompt()])
    if False:
        yield None


@Predication(vocabulary,
             names=["_order_v_1"],
             phrases={
                "What did I order?": {'SF': 'ques', 'TENSE': 'past', 'MOOD': 'indicative', 'PROG': '-', 'PERF': '-'},
                "I ordered a steak":  {'SF': 'prop', 'TENSE': 'past', 'MOOD': 'indicative', 'PROG': '-', 'PERF': '-'},
                "how much soup did I order?": {'SF': 'ques', 'TENSE': 'past', 'MOOD': 'indicative', 'PROG': '-', 'PERF': '-'}
             },
             properties={'SF': ['ques', 'prop'], 'TENSE': 'past', 'MOOD': 'indicative', 'PROG': '-', 'PERF': '-'})
def _order_v_1_past(context, state, e_introduced_binding, x_actor_binding, x_object_binding):
    if is_concept(x_actor_binding) or is_concept(x_object_binding):
        context.report_error(["formNotUnderstood", "_order_v_1_past"])
        return

    def bound(x_actor, x_object):
        if rel_check(state, x_actor, "ordered", x_object):
            return True

        else:
            context.report_error(["verbDoesntApplyArg", x_actor_binding.variable.name, "order", x_object_binding.variable.name, state.get_reprompt()])
            return False

    def actor_from_object(x_object):
        # "Who ordered X?"
        found = False
        for i in rel_subjects(state, "ordered", x_object):
            found = True
            yield store_to_object(state, i)

        if not found:
            context.report_error(["nothing_verb_x", x_actor_binding.variable.name, "ordered", x_object_binding.variable.name, state.get_reprompt()])

    def object_from_actor(x_actor):
        # "what did I order?"
        found = False
        for i in rel_objects(state, x_actor, "ordered"):
            found = True
            yield store_to_object(state, i)

        if not found:
            context.report_error(["x_verb_nothing", x_actor_binding.variable.name, "ordered", state.get_reprompt()])

    yield from in_style_predication_2(context, state, x_actor_binding, x_object_binding, bound, actor_from_object,
                                      object_from_actor)


# Scenarios:
#   - "I will have a steak/menu/table." --> restaurant frame special case for requesting
#   - "I will have a steak/menu/table?" --> Not good english
#   - "You/they, etc will have x" --> Not good english
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
            if valid_player_request(state, x_objects):
                if e_introduced_binding.value is not None and "for" in e_introduced_binding.value:
                    for_list = e_introduced_binding.value["for"]["Value"]
                    result, for_type, x_what_type = for_check(state, context, x_objects, for_list)
                    return result
                else:
                    return True
            else:
                return False

        else:
            # Anything about "you/they will have" is not good english
            context.report_error(["unexpected", state.get_reprompt()])
            return False

    def actor_unbound(x_object):
        # Anything about "what will x have
        context.report_error(["unexpected", state.get_reprompt()])
        if False:
            yield None

    def object_unbound(x_actor):
        context.report_error(["unexpected", state.get_reprompt()])
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
            yield for_update_state(new_state, x_what_type, for_type, x_object_binding, for_list)
        else:
            yield new_state

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

        if is_computer_type(x_actor) and valid_player_request(state, [x_object]):
            if e_introduced_binding.value is not None and "for" in e_introduced_binding.value:
                for_list = e_introduced_binding.value["for"]["Value"]
                result, for_type, x_what_type = for_check(state, context, [x_object], for_list)
                return result
            else:
                return True

    def actor_unbound(x_object):
        # Anything about "Who gets x?"
        context.report_error(["unexpected", state.get_reprompt()])
        if False:
            yield None

    def object_unbound(x_actor):
        # "What can you get?"
        context.report_error(["unexpected", state.get_reprompt()])
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
            yield for_update_state(new_state, x_what_type, for_type, x_object_binding, for_list)
        else:
            yield new_state


@Predication(vocabulary,
             names=["solution_group__get_v_1"],
             properties_from=_get_v_1_command)
def _get_v_1_command_group(context, state_list, e_variable_group, x_actor_variable_group, x_object_variable_group):
    actor_list = variable_group_values_to_list(x_actor_variable_group)
    if not is_computer_type(actor_list[0]):
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
        yield []


@Predication(vocabulary,
             names=["solution_group__have_v_1", "solution_group__take_v_1", "solution_group__get_v_1"],
             properties_from=_have_v_1_order)
def _have_v_1_order_group(context, state_list, e_variable_group, x_actor_variable_group, x_object_variable_group):
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
        yield []


# Works identically to "ordered" since, for non-implied requests like "do you have a menu"
# We are just checking if facts are true
# Just purely answers questions about having things in the present tense
# like have_v_1, BUT: handles some special cases like "do you have a table?"
# which is really an implied request.
# Implied requests are always of the form "you" (meaning restaurant) and, because concepts come through first,
# we will hit these first and interpret them as implied requests
@Predication(vocabulary,
             names=["_have_v_1"],
             phrases={
                "Do you have a table?": {'SF': 'ques', 'TENSE': 'pres', 'MOOD': 'indicative', 'PROG': '-', 'PERF': '-'},          # --> implied table request
                "Do you have this table?": {'SF': 'ques', 'TENSE': 'pres', 'MOOD': 'indicative', 'PROG': '-', 'PERF': '-'},       # --> fact checking question
                "What do you have?": {'SF': 'ques', 'TENSE': 'pres', 'MOOD': 'indicative', 'PROG': '-', 'PERF': '-'},             # --> implied menu request
                "Do you have a|the menu|bill?": {'SF': 'ques', 'TENSE': 'pres', 'MOOD': 'indicative', 'PROG': '-', 'PERF': '-'},         # --> implied menu request
                "What specials do you have?": {'SF': 'ques', 'TENSE': 'pres', 'MOOD': 'indicative', 'PROG': '-', 'PERF': '-'},    # --> implied request for description of specials
                "Do I|we have the table?": {'SF': 'ques', 'TENSE': 'pres', 'MOOD': 'indicative', 'PROG': '-', 'PERF': '-'},         # --> ask about the state of the world
                "Do you have a|the steak?": {'SF': 'ques', 'TENSE': 'pres', 'MOOD': 'indicative', 'PROG': '-', 'PERF': '-'},        # --> just asking about the steak, no implied request
                "Do you have a bill?": {'SF': 'ques', 'TENSE': 'pres', 'MOOD': 'indicative', 'PROG': '-', 'PERF': '-'},           # --> implied request, kind of
                "Do you have menus?": {'SF': 'ques', 'TENSE': 'pres', 'MOOD': 'indicative', 'PROG': '-', 'PERF': '-'},            # --> Could mean "do you have conceptual menus?" or "implied menu request and thus instance check"
                "Do you have steaks?": {'SF': 'ques', 'TENSE': 'pres', 'MOOD': 'indicative', 'PROG': '-', 'PERF': '-'},           # --> Could mean "do you have more than one preparation of steak" or "Do you have more than one instance of a steak"
                "We have 2 menus": {'SF': 'prop', 'TENSE': 'pres', 'MOOD': 'indicative', 'PROG': '-', 'PERF': '-'}                # --> fact checking question
             },
             properties={'SF': ['ques', 'prop'], 'TENSE': 'pres', 'MOOD': 'indicative', 'PROG': '-', 'PERF': '-'})
def _have_v_1_present(context, state, e_introduced_binding, x_actor_binding, x_object_binding):
    if is_concept(x_actor_binding):
        context.report_error(["formNotUnderstood", "_have_v_1_present"])
        return

    def bound(x_actor, x_object):
        # If it is an instance, just answer if x has y
        if not is_concept(x_object):
            if rel_check(state, x_actor, "have", x_object):
                return True
            else:
                context.report_error(["verbDoesntApplyArg", x_actor_binding.variable.name, "have", x_object_binding.variable.name, state.get_reprompt()])
                return False

        else:
            if x_actor == "restaurant":
                # "Do you (the restaurant) have (the concept of) x?"
                # Let the group handler perform the implied request action
                # or just answer the question, as long as we do have it
                return rel_check(state, x_actor, "have", x_object.concept_name)

        context.report_error(["verbDoesntApply", convert_to_english(state, x_actor), "have", convert_to_english(state, x_object), state.get_reprompt()])
        return False

    def actor_from_object(x_object):
        found = False
        for i in rel_subjects(state, "have", object_to_store(x_object)):
            found = True
            yield store_to_object(state, i)

        if not found:
            context.report_error(["nothing_verb_x", x_actor_binding.variable.name, "has", x_object_binding.variable.name, state.get_reprompt()])

    def object_from_actor(x_actor):
        found = False
        for i in rel_objects(state, x_actor, "have"):
            found = True
            yield store_to_object(state, i)

        if not found:
            context.report_error(["x_verb_nothing", x_actor_binding.variable.name, "has"])

    yield from in_style_predication_2(context, state, x_actor_binding, x_object_binding, bound, actor_from_object,
                                      object_from_actor)


@Predication(vocabulary,
             names=["solution_group__have_v_1"],
             properties_from=_have_v_1_present)
def _have_v_1_present_group(context, state_list, e_list, x_act_list, x_obj_list):
    # The solution predication guarantees that this is either actor and object instances or
    # actor instance and object concept. We only have to check one solution since they will all be the same
    first_x_obj = x_obj_list.solution_values[0].value[0]
    object_concepts = is_concept(first_x_obj)

    if not object_concepts:
        # This is a "x has y" type statement with instances and these have already been checked
        yield state_list

    else:
        # Since this is a concept, the solution handler already checked that the actor is
        # "restaurant" and that the restaurant "has" the solution group concepts.
        final_states = []
        solution_index = -1
        for state in state_list:
            solution_index += 1
            # Deal with the user saying "do you have x and y *together*"
            x_obj_value = x_obj_list.solution_values[solution_index].value
            if len(x_obj_value) > 1:
                context.report_error(["errorText", "One thing at a time, please!", state.get_reprompt()], force=True)
                yield []
                return

            # Now we are guaranteed to only have one item in x_obj_value
            # wh-questions aren't implied requests.  I.e. "which tables do you have?"
            x_obj = x_obj_value[0]
            tree_info = state_list[0].get_binding("tree").value[0]
            wh_variable = is_wh_question(tree_info)

            # Only doing a cursory check to make sure they are talking about things that could
            # be requests in general. More specific things like "a cheap bill" will be figured out
            # in the planner and failed if we can't give it
            if not wh_variable and x_obj.concept_name in ["bill", "table", "menu"]:
                # "Can I have a table/menu/bill?" is really about the instances
                # thus check_concepts=False
                # Fail this group if we don't meet the constraints
                if not check_concept_solution_group_constraints(context, state_list, x_obj_list, check_concepts=False):
                    yield []
                    return

                # Questions about "Do you have a (concept of a) table/menu/bill?" are really implied requests in a restaurant
                # that mean "Can I have a table/menu/bill?"
                # Note that this is where the concept really gets checked in case they said something like
                # Do you have a *dirty* menu or something...
                task = ('satisfy_want', context, [("user",)], [(x_obj,)], 1)
                final_state = do_task(state_list[0].world_state_frame(), [task])
                if final_state:
                    final_states.append(final_state)

                else:
                    yield []
                    return

            else:
                # Not an implied request and the solution predication already confirmed
                # that the restaurant has this concept, so: succeed
                # Fail this group if we don't meet the constraints
                if not check_concept_solution_group_constraints(context, state_list, x_obj_list, check_concepts=True):
                    yield []
                    return

                final_states.append(state)

        yield final_states


# Used only when there is a form of have that means "able to"
# The regular predication only checks if x is able to have y
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
    def both_bound_prediction_function(x_actors, x_objects):
        # Players are able to have any food, a table or a menu
        if is_user_type(x_actors):
            return valid_player_request(state, x_objects)

        # Food is able to have ingredients, restaurant can have food, etc.
        # Whatever we have modelled
        else:
            store_actor = object_to_store(x_actors)
            store_object = object_to_store(x_objects)

            return rel_check(state, store_actor, "have", store_object)

    def actor_unbound(x_objects):
        # What/Who can have x? Comes in unbound because it is reorderable
        # so we need to return everything that can have x
        found = False
        if valid_player_request(state, x_objects):
            found = True
            for item in user_types():
                yield (item,)

        for item in rel_subjects(state, "have", x_objects):
            found = True
            yield (item,)

        if not found:
            context.report_error(["nothing_verb_x", x_actor_binding.variable.name, "have", x_object_binding.variable.name])

    def object_unbound(x_actor):
        # This is a "What can I have?" type question
        # - Conceptually, there are a lot of things the user is able to have: a table, a bill, a menu, a steak, etc.
        #   - But: this isn't really what they are asking. This is something that is a special phrase in the "restaurant frame" which means: "what is on the menu"
        #     - So it is a special case that we interpret as a request for a menu
        if is_user_type(x_actor):
            yield (ESLConcept("menu"), )

    yield from lift_style_predication_2(context, state, x_actor_binding, x_object_binding,
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
            yield []
            return
    else:
        # Not an implicit request
        yield state_list


@Predication(vocabulary, names=["poss"])
def poss(context, state, e_introduced_binding, x_object_binding, x_actor_binding):
    def bound(x_actor, x_object):
        if (object_to_store(x_actor), object_to_store(x_object)) in state.all_rel("have"):
            return True
        else:
            context.report_error(["verbDoesntApply", x_actor, "have", x_object, state.get_reprompt()])
            return False

    def actor_from_object(x_object):
        for i in state.all_rel("have"):
            if i[1] == x_object:
                yield store_to_object(i[0])

    def object_from_actor(x_actor):
        for i in state.all_rel("have"):
            if i[0] == x_actor:
                yield store_to_object(i[1])

    for item in in_style_predication_2(context, state, x_actor_binding, x_object_binding, bound, actor_from_object,
                                      object_from_actor):
        yield item


# Returns:
# the variable to measure into, the units to measure
# or None if not a measurement unbound variable
def measure_units(x):
    if isinstance(x, Measurement) and x.count is None:
        # if x is a Measurement() with None as a value,
        # then we are being asked to measure x_actor
        units = x.measurement_type
        if is_concept(units):
            return units.concept_name

    return None


@Predication(vocabulary,
             names=["_be_v_id"],
             phrases={
                 "What are the specials?": {'SF': 'ques', 'TENSE': 'pres', 'MOOD': 'indicative', 'PROG': '-', 'PERF': '-'},
                 "What will be the specials?": {'SF': 'ques', 'TENSE': 'fut', 'MOOD': 'indicative', 'PROG': '-', 'PERF': '-'},
                 "How much is the soup?": {'SF': 'ques', 'TENSE': 'pres', 'MOOD': 'indicative', 'PROG': '-', 'PERF': '-'},
                 "How much will the soup be?": {'SF': 'ques', 'TENSE': 'fut', 'MOOD': 'indicative', 'PROG': '-', 'PERF': '-'},
                 "How many dollars is the soup?": {'SF': 'ques', 'TENSE': 'pres', 'MOOD': 'indicative', 'PROG': '-', 'PERF': '-'},
                 "How many dollars will the soup be?": {'SF': 'ques', 'TENSE': 'fut', 'MOOD': 'indicative', 'PROG': '-', 'PERF': '-'},
                 "soup is a vegetarian dish": {'SF': 'prop', 'TENSE': 'pres', 'MOOD': 'indicative', 'PROG': '-', 'PERF': '-'},
                 "soup will be a vegetarian dish": {'SF': 'prop', 'TENSE': 'fut', 'MOOD': 'indicative', 'PROG': '-', 'PERF': '-'}
             },
             properties={'SF': ['ques', 'prop'], 'TENSE': ['pres', 'fut'], 'MOOD': 'indicative', 'PROG': '-', 'PERF': '-'})
def _be_v_id(context, state, e_introduced_binding, x_subject_binding, x_object_binding):
    def criteria_bound(x_subject, x_object):
        # Just check if this is an object and a measurement, if so, handle it below
        units = measure_units(x_object)
        if units is not None:
            return True

        else:
            if x_subject in all_instances_and_spec(state, x_object):
                return True

            elif x_object in all_instances_and_spec(state, x_subject):
                return True

            else:
                context.report_error(["is_not", x_subject_binding.variable.name, x_object_binding.variable.name, state.get_reprompt()])

    def unbound(x_object):
        # if x_subject is unbound it means the questions is of the form: "what is X", "where is X", "who is x"
        # responding with the object itself is the most basic logic, which allows answering "what is soup" with "soup" (not wrong)
        # and also "what are the specials?" or any phrases that want a list of what things are of a particular type because it forces x_object
        # (e.g. "specials") to yield the various values and then be_v_id just passes them through
        #
        # If, instead, we yielded things that are specializations of x_object, a phrase like "what are the vegetarian dishes?" won't work because
        # "dishes" is plural but gets locked into a single value because, say, a dish like "soup" doesn't have any concepts that specialize it
        # so it will fail to yield anything. Since neither soup nor salad have specializations, that locks in "dishes" to a single value, which fails
        # since it is plural
        yield from concept_disjunctions_reverse(state, object_to_store(x_object))

    for success_state in in_style_predication_2(context, state, x_subject_binding, x_object_binding, criteria_bound, unbound, unbound):
        x_object_value = success_state.get_binding(x_object_binding.variable.name).value[0]
        units = measure_units(x_object_value)
        if units is not None:
            # This is a "how much is x" question: we need to measure the value
            # into the specified variable
            yield from yield_cost_of_subject_into_object(success_state, units, x_subject_binding.variable.name, x_object_binding.variable.name)

        else:
            yield success_state


def yield_cost_of_subject_into_object(state, units, subject_variable, object_variable):
    x_subject_value = state.get_binding(subject_variable).value[0]
    concept_item = instance_of_or_concept_name(state, x_subject_value)
    if units in ["generic_entity", "dollar"]:
        if concept_item in state.sys["prices"]:
            price = Measurement("dollar", state.sys["prices"][concept_item])
            # Remember that we now know the price
            yield state.set_x(object_variable, (price,)).record_operations([SetKnownPriceOp(concept_item)])

        elif concept_item == "bill":
            total = list(rel_objects(state, "bill1", "valueOf"))
            if len(total) == 0:
                total.append(0)
            price = Measurement("dollar", total[0])
            yield state.set_x(object_variable, (price,))

        elif concept_item is None or concept_item == "generic_entity":
            # Happens for "That will be all, thank you"
            return

        else:
            yield state.record_operations([RespondOperation("Haha, it's not for sale.")])
            return False


# This is here to remove "there are more" if we are asking about specials...
# And to check constraints for concepts
# Scenarios:
# Which dishes are specials? -> Could be either "which of these dishes is a special" or "which conceptual dishes are specials?"
#   _which_q(x3,_dish_n_of(x3,i8),udef_q(x9,_special_n_1(x9),_be_v_id(e2,x3,x9)))
#
# What are your specials? What are your steaks? What are your tables? -> Almost certainly means "which are the concepts of X?
#   which_q(x3,thing(x3),pronoun_q(x14,pron(x14),def_explicit_q(x8,[_special_n_1(x8), poss(e13,x8,x14)],_be_v_id(e2,x3,x8))))
#
# Which 2 dishes are specials?
@Predication(vocabulary,
             names=["solution_group__be_v_id"],
             properties_from=_be_v_id)
def _be_v_id_group(context, state_list, e_introduced_binding_list, x_subject_variable_group, x_object_variable_group):
    # If the arguments are concepts constraints need to be checked
    if x_subject_variable_group.solution_values[0].value is not None and is_concept(x_subject_variable_group.solution_values[0].value[0]):
        if not check_concept_solution_group_constraints(context, state_list, x_subject_variable_group, check_concepts=True):
            yield []
            return

    if x_object_variable_group.solution_values[0].value is not None and is_concept(x_object_variable_group.solution_values[0].value[0]):
        if not check_concept_solution_group_constraints(context, state_list, x_object_variable_group, check_concepts=True):
            yield []
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
            context.report_error(["Have not dealt with declarative cost", state.get_reprompt()])
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

        concept_item = instance_of_or_concept_name(state, x_actor)
        if concept_item in state.sys["prices"].keys():
            yield concept_item + " : " + str(state.sys["prices"][concept_item]) + " dollars"
        else:
            yield "Ah. It's not for sale."

    for success_state in in_style_predication_2(context, state, x_actor_binding, x_object_binding, criteria_bound, get_actor, get_object):
        x_object_value = success_state.get_binding(x_object_binding.variable.name).value[0]
        units = measure_units(x_object_value)
        if units is not None:
            # This is a "how much is x" question: we need to measure the value
            # into the specified variable
            yield from yield_cost_of_subject_into_object(success_state, units, x_actor_binding.variable.name, x_object_binding.variable.name)

        else:
            yield success_state


@Predication(vocabulary,
             names=["solution_group__cost_v_1"],
             properties_from=_cost_v_1)
def _cost_v_1_group(context, state_list, e_introduced_binding_list, x_act_variable_group, x_obj2_variable_group):
    if is_concept(x_act_variable_group.solution_values[0].value[0]):
        if not check_concept_solution_group_constraints(context, state_list, x_act_variable_group, check_concepts=True):
            yield []
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
@Predication(vocabulary, names=["solution_group_wh"])
def wh_question(context, state_list, binding_list):
    current_state = do_task(state_list[0].world_state_frame(), [('describe', context, [x.value for x in binding_list])])
    if current_state is not None:
        # Make sure any operations that were created on solutions get passed on
        all_operations = []
        for solution in state_list:
            for operation in solution.get_operations():
                all_operations.append(operation)

        new_state = current_state.apply_operations(all_operations, True)

        yield (new_state,)


# Generates all the responses that predications can
# return when an error occurs
def generate_custom_message(tree_info, error_term):
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
        result = s("{bare arg1:sg}", tree_info)
        if result == "thing":
            return s("Host: Nothing.")
        elif result == "person":
            return s("Host: Nobody.")
        else:
            return s("Host: There isn't such {a *result} here", tree_info)

    else:
        system_message = perplexity.messages.generate_message(tree_info, error_term)
        if system_message is not None:
            return system_message

    if error_constant == "dontKnowHow":
        return "I don't know how to do that."
    if error_constant == "notAThing":
        # english_for_delphin_variable() converts a variable name like 'x3' into the english words
        # that it represented in the MRS
        arg2 = english_for_delphin_variable(error_predicate_index, arg2, tree_info)
        return f"{arg1} is not {arg2}{arg3}"
    if error_constant == "nothing_verb_x":
        return s("No {arg1} {*arg2} {a arg3}", tree_info, reverse_pronouns=True)
    if error_constant == "x_verb_nothing":
        return s("{arg1} {*arg2} nothing", tree_info, reverse_pronouns=True)
    if error_constant == "not_adj":
        return s("{arg3:@error_predicate_index} {'is':<arg3} not {*arg1}." + arg2, tree_info)
    if error_constant == "is_not":
        return s("{arg1} is not {arg2}{*arg3}", tree_info)
    if error_constant == "arg_is_not_value_arg":
        return s("{arg1} is not {*arg2} {arg3}", tree_info)
    if error_constant == "notOn":
        return f"No. {arg1} is not on {arg2}{arg3}"
    if error_constant == "verbDoesntApplyArg":
        return s("{arg1} {'did':<arg1} not {*arg2} {arg3} {*arg4}", tree_info, reverse_pronouns=True)
    if error_constant == "verbDoesntApply":
        return f"No. {arg1} does not {arg2} {arg3} {arg4}"
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
    initial_state = initial_state.add_rel("veggie", "specializes", "dish")
    initial_state = initial_state.add_rel("special", "specializes", "dish")

    initial_state = initial_state.add_rel("steak", "specializes", "meat")
    initial_state = initial_state.add_rel("chicken", "specializes", "meat")
    initial_state = initial_state.add_rel("salmon", "specializes", "meat")
    initial_state = initial_state.add_rel("pork", "specializes", "meat")

    initial_state = initial_state.add_rel("soup", "specializes", "veggie")
    initial_state = initial_state.add_rel("tomato", "specializes", "food")
    initial_state = initial_state.add_rel("soup", "isAdj", "tomato")

    initial_state = initial_state.add_rel("salad", "specializes", "veggie")
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
            if dish_type == "chicken":
                initial_state = initial_state.add_rel(food_instance, "isAdj", "roasted")
            if dish_type == "salmon":
                initial_state = initial_state.add_rel(food_instance, "isAdj", "grilled")
            if dish_type == "pork":
                initial_state = initial_state.add_rel(food_instance, "isAdj", "smoked")

    initial_state = initial_state.add_rel("hi", "hasName", "Hawaii")
    initial_state = initial_state.add_rel("howdy", "hasName", "howdy")
    initial_state = initial_state.add_rel("restaurant", "have", "special")
    initial_state = initial_state.add_rel("restaurant", "hasName", "restaurant")
    initial_state = initial_state.add_rel("bill1", "instanceOf", "bill")
    initial_state = initial_state.add_rel("bill1", "instanceOf", "check")
    initial_state = initial_state.add_rel("user", "have", "bill1")
    initial_state = initial_state.add_rel(0, "valueOf", "bill1")
    initial_state = initial_state.add_rel("room", "contains", "user")

    initial_state = initial_state.add_rel("son1", "instanceOf", "son")
    initial_state = initial_state.add_rel("son1", "hasName", "Johnny")
    initial_state = initial_state.add_rel("user", "instanceOf", "person")
    initial_state = initial_state.add_rel("user", "hasName", "you")
    initial_state = initial_state.add_rel("user", "have", "son1")
    # initial_state = initial_state.add_rel("user", "have", "card")
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


def ui(loading_info=None, file=None, user_output=None, debug_output=None):
    loaded_state = None
    if loading_info is not None:
        if loading_info.get("Version", None) != 1:
            raise LoadException()

        if file is not None:
            loaded_state = load_world_state(file)

        message = ""
    else:
        message = "You’re going to a restaurant with your son, Johnny, who is vegetarian and too scared to order by himself. Get a table and buy lunch for both of you. You have 20 dollars in cash.\nHost: Hello! How can I help you today?"

    ui = UserInterface("esl", reset, vocabulary,
                         message_function=generate_custom_message,
                         error_priority_function=error_priority,
                         scope_function=in_scope,
                         scope_init_function=in_scope_initialize,
                         loaded_state=loaded_state,
                         user_output=user_output,
                         debug_output=debug_output)
    ui.user_output(message)
    return ui


def hello_world():
    user_interface = ui()
    while user_interface:
        user_interface = user_interface.default_loop()


if __name__ == '__main__':
    # ShowLogging("Execution")
    # ShowLogging("Generation")
    # ShowLogging("SString")
    # ShowLogging("UserInterface")
    # ShowLogging("Pipeline")

    # ShowLogging("SString")
    # ShowLogging("Determiners")
    # ShowLogging("SolutionGroups")
    # ShowLogging("Transformer")

    hello_world()
