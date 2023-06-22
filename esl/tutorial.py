import perplexity.messages
from perplexity.execution import report_error, call, execution_context
from perplexity.generation import english_for_delphin_variable
from perplexity.plurals import VariableCriteria, GlobalCriteria
from perplexity.predications import combinatorial_predication_1, in_style_predication_2
from perplexity.system_vocabulary import system_vocabulary, quantifier_raw
from perplexity.transformer import TransformerMatch, TransformerProduction, PropertyTransformerMatch
from perplexity.tree import find_predication_from_introduced
from perplexity.user_interface import UserInterface
from perplexity.utilities import ShowLogging, sentence_force
from perplexity.vocabulary import Predication, EventOption, Transform, override_predications
from esl.worldstate import *


vocabulary = system_vocabulary()
override_predications(vocabulary, "user", ["card__cex__"])


# Convert "would like <noun>" to "want <noun>"
@Transform(vocabulary)
def would_like_to_want_transformer():
    production = TransformerProduction(name="_want_v_1", args={"ARG0":"$e1", "ARG1":"$x1", "ARG2":"$x2"})
    like_match = TransformerMatch(name_pattern="_like_v_1", args_pattern=["e", "x", "x"], args_capture=[None, "x1", "x2"])
    return TransformerMatch(name_pattern="_would_v_modal", args_pattern=["e", like_match], args_capture=["e1", None], removed=["_would_v_modal", "_like_v_1"], production=production)


# Convert "Can/could I x?", "I can/could x?" to "I x?"
@Transform(vocabulary)
def can_removal_intransitive_transformer():
    production = TransformerProduction(name="$name", args={"ARG0":"$e1", "ARG1":"$x1"})
    target = TransformerMatch(name_pattern="*", name_capture="name", args_pattern=["e", "x"], args_capture=[None, "x1"])
    return TransformerMatch(name_pattern="_can_v_modal", args_pattern=["e", target], args_capture=["e1", None], removed=["_can_v_modal"], production=production)


# Convert "Can/could I x y?", "I can/could x y?" to "I x y?"
@Transform(vocabulary)
def can_removal_transitive_transformer():
    production = TransformerProduction(name="$name", args={"ARG0":"$e1", "ARG1":"$x1", "ARG2":"$x2"})
    target = TransformerMatch(name_pattern="*", name_capture="name", args_pattern=["e", "x", "x"], args_capture=[None, "x1", "x2"])
    return TransformerMatch(name_pattern="_can_v_modal", args_pattern=["e", target], args_capture=["e1", None], removed=["_can_v_modal"], production=production)


# Convert "I want to x y" to "I x_request y"
@Transform(vocabulary)
def want_removal_transitive_transformer():
    production = TransformerProduction(name="$|name|_request", args={"ARG0":"$e1", "ARG1":"$x1", "ARG2":"$x2"})
    target = TransformerMatch(name_pattern="*", name_capture="name", args_pattern=["e", "x", "x"], args_capture=[None, "x1", "x2"])
    return TransformerMatch(name_pattern="_want_v_1", args_pattern=["e", "x", target], args_capture=["e1", None, None], removed=["_want_v_1"], production=production)


# Convert "I want to x" to "I x_request"
@Transform(vocabulary)
def want_removal_intransitive_transformer():
    production = TransformerProduction(name="$|name|_request", args={"ARG0":"$e1", "ARG1":"$x1"})
    target = TransformerMatch(name_pattern="*", name_capture="name", args_pattern=["e", "x"], args_capture=[None, "x1"])
    return TransformerMatch(name_pattern="_want_v_1", args_pattern=["e", "x", target], args_capture=["e1", None, None], removed=["_want_v_1"], production=production)


# Convert "I would like to x y" to "I x_request y"
@Transform(vocabulary)
def would_like_removal_transitive_transformer():
    production = TransformerProduction(name="$|name|_request", args={"ARG0":"$e1", "ARG1":"$x1", "ARG2":"$x2"})
    target = TransformerMatch(name_pattern="*", name_capture="name", args_pattern=["e", "x", "x"], args_capture=[None, "x1", "x2"])
    like_match = TransformerMatch(name_pattern="_like_v_1", args_pattern=["e", "x", target], args_capture=[None, None, None])
    would_match = TransformerMatch(name_pattern="_would_v_modal", args_pattern=["e", like_match], args_capture=["e1", None], removed=["_would_v_modal", "_like_v_1"], production=production)
    return would_match


# Convert "I would like to x" to "I x_request x"
@Transform(vocabulary)
def would_like_removal_intransitive_transformer():
    production = TransformerProduction(name="$|name|_request", args={"ARG0":"$e1", "ARG1":"$x1"})
    target = TransformerMatch(name_pattern="*", name_capture="name", args_pattern=["e", "x"], args_capture=[None, "x1"])
    like_match = TransformerMatch(name_pattern="_like_v_1", args_pattern=["e", "x", target], args_capture=[None, None, None])
    would_match = TransformerMatch(name_pattern="_would_v_modal", args_pattern=["e", like_match], args_capture=["e1", None], removed=["_would_v_modal", "_like_v_1"], production=production)
    return would_match


# Convert "I would x y" to "I x_request y" (i.e. "I would have a menu")
@Transform(vocabulary)
def want_removal_transitive_transformer():
    production = TransformerProduction(name="$|name|_request", args={"ARG0":"$e1", "ARG1":"$x1", "ARG2":"$x2"})
    target = TransformerMatch(name_pattern="*", name_capture="name", args_pattern=["e", "x", "x"], args_capture=[None, "x1", "x2"])
    return TransformerMatch(name_pattern="_would_v_modal", args_pattern=["e", target], args_capture=["e1", None], removed=["_would_v_modal"], production=production)






@Predication(vocabulary, names=["pron"])
def pron(state, x_who_binding):
    person = int(state.get_binding("tree").value[0]["Variables"][x_who_binding.variable.name]["PERS"])
    plurality = "unknown"
    if "NUM" in state.get_binding("tree").value[0]["Variables"][x_who_binding.variable.name].keys():
        plurality = (state.get_binding("tree").value[0]["Variables"][x_who_binding.variable.name]["NUM"])

    def bound_variable(value):
        if person == 2 and value == "computer":
            return True
        if person == 1 and is_user_type(value):
            return True
        else:
            report_error(["dontKnowActor", x_who_binding.variable.name])

    def unbound_variable():
        if person == 2:
            yield "computer"
        if person == 1:
            if plurality == "pl":
                yield "user"
                yield "son1"

            else:
                yield "user"

    yield from combinatorial_predication_1(state, x_who_binding, bound_variable, unbound_variable)

def is_user_type(val):
    if not isinstance(val,tuple):
        return val in ["user","son1"]

    else:
        for i in val:
            if val not in ["user","son1"]:
                return False
        return True

@Predication(vocabulary, names=["generic_entity"])
def generic_entity(state, x_binding):
    def bound(val):
        # return val in state.ent
        return True

    def unbound():
        # for i in state.ent:
        #    yield i
        yield "generic_entity"

    yield from combinatorial_predication_1(state, x_binding, bound, unbound)


@Predication(vocabulary, names=["_okay_a_1"])
def _okay_a_1(state, i_binding, h_binding):
    yield from call(state, h_binding)



@Predication(vocabulary, names=["much-many_a"], handles=[("relevant_var", EventOption.optional)])
def much_many_a(state, e_binding, x_binding):
    if "relevant_var" in e_binding.value.keys():
        yield state.set_x(x_binding.variable.name, (json.dumps(
            {"relevant_var_name": e_binding.value["relevant_var"], "relevant_var_value": "to_determine",
             "structure": "price_type"}),))


@Predication(vocabulary, names=["measure"])
def measure(state, e_binding, e_binding2, x_binding):
    yield state.add_to_e(e_binding2.variable.name, "relevant_var", x_binding.variable.name)


@Predication(vocabulary, names=["abstr_deg"])
def abstr_deg(state, x_binding):
    yield state.set_x(x_binding.variable.name, ("abstract_degree",))




@Predication(vocabulary, names=["card"])
def card(state, c_number, e_binding, x_binding):
    if state.get_binding(x_binding.variable.name).value[0] == "generic_entity":
        if c_number.isnumeric():
            yield state.set_x(x_binding.variable.name, (Measurement("generic_cardinality", int(c_number)),))

@Predication(vocabulary, names=["card"])
def card_system(state, c_number, e_binding, x_binding):
    if state.get_binding(x_binding.variable.name).value[0] != "generic_entity":
        yield from perplexity.system_vocabulary.card(state, c_number, e_binding, x_binding)

@Predication(vocabulary, names=["_for_p"])
def _for_p(state, e_binding, x_binding, x_binding2):
    what_is = state.get_binding(x_binding.variable.name).value[0]
    what_for = state.get_binding(x_binding2.variable.name).value[0]
    if not isinstance(what_for, Measurement):
        yield state
    else:
        what_measuring = what_for.measurement_type
        if not what_measuring == "generic_cardinality":
            yield state
        else:
            yield state.set_x(x_binding.variable.name,
                              (json.dumps({"structure": "noun_for", "noun": what_is, "for_count": what_for.count}),))


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


@Predication(vocabulary, names=["unknown"])
def unknown(state, e_binding, x_binding):
    yield state.record_operations(state.handle_world_event(["unknown", x_binding.value[0]]))


@Predication(vocabulary, names=["unknown"])
def unknown_eu(state, e_binding, u_binding):
    yield state


@Predication(vocabulary, names=["_yes_a_1", "_yup_a_1", "_sure_a_1", "_yeah_a_1"])
def _yes_a_1(state, i_binding, h_binding):
    yield state.record_operations(state.handle_world_event(["yes"]))


@Predication(vocabulary, names=["_no_a_1", "_nope_a_1"])
def _no_a_1(state, i_binding, h_binding):
    yield state.record_operations(state.handle_world_event(["no"]))


def handles_noun(noun_lemma):
    return noun_lemma in ["special", "food", "menu", "soup", "salad", "table", "thing", "steak", "meat", "bill",
                          "check", "dish", "salmon", "chicken","bacon","son"]


# Simple example of using match_all that doesn't do anything except
# make sure we don't say "I don't know the word book"
@Predication(vocabulary, names=["match_all_n"], matches_lemma_function=handles_noun)
def match_all_n(noun_type, state, x_binding):
    def bound_variable(value):
        if sort_of(state, value, noun_type):
            return True
        else:
            report_error(["notAThing", x_binding.value, x_binding.variable.name])
            return False

    def unbound_variable():
        yield from all_instances(state, noun_type)

    yield from combinatorial_predication_1(state, x_binding, bound_variable, unbound_variable)


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
        veg = all_instances(state, "veggie")
        if value in veg:
            return True
        else:
            report_error(["Not Veg"])
            return False

    def unbound_values():
        # Find all large things
        for i in all_instances(state, "veggie"):
            yield i

    yield from combinatorial_predication_1(state, x_target_binding,
                                           criteria_bound,
                                           unbound_values)


class PastParticiple:
    def __init__(self, predicate_name_list, lemma):
        self.predicate_name_list = predicate_name_list
        self.lemma = lemma

    def predicate_function(self, state, e_introduced_binding, i_binding, x_target_binding):
        def bound(value):
            if (value, self.lemma) in state.rel["isAdj"]:
                return True
            else:
                report_error(["Not" + self.lemma])
                return False

        def unbound():
            for i in state.rel["isAdj"]:
                if i[1] == self.lemma:
                    yield i[0]

        yield from combinatorial_predication_1(state, x_target_binding,
                                               bound,
                                               unbound)

grilled = PastParticiple(["_grill_v_1"],"grilled")
roasted = PastParticiple(["_roast_v_cause"],"roasted")
@Predication(vocabulary, names=grilled.predicate_name_list)
def _grill_v_1(state, e_introduced_binding, i_binding, x_target_binding):
    yield from grilled.predicate_function(state,e_introduced_binding,i_binding,x_target_binding)

@Predication(vocabulary, names=roasted.predicate_name_list)
def _grill_v_1(state, e_introduced_binding, i_binding, x_target_binding):
    yield from roasted.predicate_function(state,e_introduced_binding,i_binding,x_target_binding)

@Predication(vocabulary, names=("_on_p_loc",))
def on_p_loc(state, e_introduced_binding, x_actor_binding, x_location_binding):
    def check_item_on_item(item1, item2):
        if "on" in state.rel.keys():
            if (item1, item2) in state.rel["on"]:
                return True
            else:
                report_error(["notOn", item1, item2])
        else:
            report_error(["notOn", item1, item2])

    def all_item1_on_item2(item2):
        if "on" in state.rel.keys():
            for i in state.rel["on"]:
                if i[1] == item2:
                    yield i[0]

    def all_item2_containing_item1(item1):
        if "on" in state.rel.keys():
            for i in state.rel["on"]:
                if i[0] == item1:
                    yield i[1]

    yield from in_style_predication_2(state,
                                      x_actor_binding,
                                      x_location_binding,
                                      check_item_on_item,
                                      all_item1_on_item2,
                                      all_item2_containing_item1)


@Predication(vocabulary, names=["_want_v_1"])
def _want_v_1(state, e_introduced_binding, x_actor_binding, x_object_binding):
    def criteria_bound(x_actor, x_object):
        if is_user_type(x_actor):
            return True
        elif "want" in state.rel.keys():
            if (x_actor, x_object) in state.rel["want"]:
                return True
        else:
            report_error(["notwant", "want", x_actor])
            return False

    def wanters_of_obj(x_object):
        if "want" in state.rel.keys():
            for i in state.rel["want"]:
                if i[1] == x_object:
                    yield i[0]

    def wanted_of_actor(x_actor):
        if "want" in state.rel.keys():
            for i in state.rel["want"]:
                if i[0] == x_actor:
                    yield i[1]

    success_states = list(in_style_predication_2(state, x_actor_binding, x_object_binding, criteria_bound,
                                                 wanters_of_obj, wanted_of_actor))
    for success_state in success_states:
        x_act = success_state.get_binding(x_actor_binding.variable.name).value[0]
        x_obj = success_state.get_binding(x_object_binding.variable.name).value[0]
        if is_user_type(x_act):
            if not x_obj is None:
                yield success_state.record_operations(state.handle_world_event(["user_wants", x_obj]))


@Predication(vocabulary, names=["solution_group__want_v_1"])
def want_group(state_list, e_introduced_binding_list, x_actor_binding_list, x_what_binding_list):
    if len(state_list) == 1:
        yield (state_list[0],)
    else:
        reset_operations(state_list[0])
        yield (state_list[0].record_operations(state_list[0].user_wants_group(x_actor_binding_list, x_what_binding_list)),)


@Predication(vocabulary, names=["_check_v_1"])
def _check_v_1(state, e_introduced_binding, x_actor_binding, i_object_binding):
    if i_object_binding.value is not None:
        return

    def criteria_bound(x):
        return x == "computer"

    def unbound():
        if False:
            yield None

    for success_state in combinatorial_predication_1(state, x_actor_binding, criteria_bound, unbound):
        yield success_state.record_operations(state.handle_world_event(["user_wants", "bill1"]))


@Predication(vocabulary, names=["_give_v_1", "_get_v_1"])
def _give_v_1(state, e_introduced_binding, x_actor_binding, x_object_binding, x_target_binding):
    if state.get_binding(x_actor_binding.variable.name).value[0] == "computer":
        if is_user_type(state.get_binding(x_target_binding.variable.name).value[0]):
            if not state.get_binding(x_object_binding.variable.name).value[0] is None:
                yield state.record_operations(
                    state.handle_world_event(
                        ["user_wants", state.get_binding(x_object_binding.variable.name).value[0]]))


@Predication(vocabulary, names=["_show_v_1"])
def _show_v_1(state, e_introduced_binding, x_actor_binding, x_object_binding, x_target_binding):
    if state.get_binding(x_actor_binding.variable.name).value[0] == "computer":
        if is_user_type(state.get_binding(x_target_binding.variable.name).value[0]):
            if not state.get_binding(x_object_binding.variable.name).value[0] is None:
                if state.get_binding(x_object_binding.variable.name).value[0] == "menu1":
                    yield state.record_operations(
                        state.handle_world_event(
                            ["user_wants_to_see", state.get_binding(x_object_binding.variable.name).value[0]]))


@Predication(vocabulary, names=["_seat_v_cause"])
def _seat_v_cause(state, e_introduced_binding, x_actor_binding, x_object_binding):
    if is_user_type(state.get_binding(x_object_binding.variable.name).value[0]):
        yield state.record_operations(state.handle_world_event(["user_wants", "table1"]))


@Predication(vocabulary, names=["loc_nonsp"])
def loc_nonsp(state, e_introduced_binding, x_actor_binding, x_loc_binding):
    def item1_in_item2(item1, item2):
        if item2 == "today":
            return True

        if (item1, item2) in state.rel["contains"]:
            return True
        return False

    def items_in_item1(item1):
        for i in state.rel["contains"]:
            if i[0] == item1:
                yield i[1]

    def item1_in_items(item1):
        for i in state.rel["contains"]:
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
            report_error(["notAThing", x_binding.value, x_binding.variable.name])
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
            report_error(["notAThing", x_binding.value, x_binding.variable.name])
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


@Predication(vocabulary, names=["_please_v_1"])
def _please_v_1(state, e_introduced_binding, i_binding1, i_binding2):
    yield state


@Predication(vocabulary, names=["polite"])
def polite(state, c_arg, i_binding, e_binding):
    yield state


@Predication(vocabulary, names=["_thanks_a_1", "_then_a_1"])
def _thanks_a_1(state, i_binding, h_binding):
    yield from call(state, h_binding)


#
# @Predication(vocabulary, names=["_and_c"])
# def _and_c(state, x_binding_introduced, x_binding_first, x_binding_second):
#     assert(state.get_binding(x_binding_first.variable.name).value[0] is not None)
#     assert (state.get_binding(x_binding_second.variable.name).value[0] is not None)
#     yield state.set_x(x_binding_introduced.variable.name,
#                       state.get_binding(x_binding_first.variable.name).value + state.get_binding(x_binding_second.variable.name).value,
#                       combinatoric=True)


def is_request_from_tree(tree_info):
    introduced_predication = find_predication_from_introduced(tree_info["Tree"], tree_info["Index"])
    return sentence_force(tree_info["Variables"]) in ["ques", "prop-or-ques"] or \
        introduced_predication.name.endswith("_request") or \
        tree_info["Variables"][tree_info["Index"]]["TENSE"] == "fut"


class RequestVerbTransitive:
    def __init__(self, predicate_name_list, lemma, logic, group_logic):
        self.predicate_name_list = predicate_name_list
        self.lemma = lemma
        self.logic = logic
        self.group_logic = group_logic

    def predicate_func(self, state, e_binding, x_actor_binding, x_object_binding):
        is_request = is_request_from_tree(state.get_binding("tree").value[0])

        if self.lemma == "have":
            if state.get_binding(x_actor_binding.variable.name).value[0] == "computer":
                if state.get_binding(x_object_binding.variable.name).value is None:
                    yield state.set_x(x_object_binding.variable.name, ("dummy_variable",)).record_operations(
                        state.handle_world_event(["user_wants", "menu1"]))
                    return

        def bound(x_actor, x_object):
            if is_request and is_user_type(x_actor):
                return True
            else:
                if self.lemma in state.rel.keys():
                    if (x_actor, x_object) in state.rel[self.lemma]:
                        return True
                    else:
                        report_error(["verbDoesntApply", x_actor, self.lemma, x_object])
                        return False

                else:
                    report_error(["verbDoesntApply", x_actor, self.lemma, x_object])
                    return False

        def actor_from_object(x_object):
            if self.lemma in state.rel.keys():
                something_sees = False
                for i in state.rel[self.lemma]:
                    if i[1] == x_object:
                        yield i[0]
                        something_sees = True
                if not something_sees:
                    report_error(["Nothing_VTRANS_X", self.lemma, x_object])
            else:
                report_error(["No_VTRANS", self.lemma, x_object])

        def object_from_actor(x_actor):
            if self.lemma in state.rel.keys():
                sees_something = False
                for i in state.rel[self.lemma]:
                    if i[0] == x_actor or i[0] == x_actor[0]:
                        yield i[1]
                        sees_something = True
                if not sees_something:
                    report_error(["X_VTRANS_Nothing", self.lemma, x_actor])
            else:
                report_error(["No_VTRANS", self.lemma, x_actor])

        state_exists = False
        for success_state in in_style_predication_2(state, x_actor_binding, x_object_binding, bound, actor_from_object,
                                                    object_from_actor):
            state_exists = True
            x_act = success_state.get_binding(x_actor_binding.variable.name).value[0]
            x_obj = success_state.get_binding(x_object_binding.variable.name).value[0]

            if is_request and is_user_type(x_act):
                if x_obj is not None:
                    yield success_state.record_operations(success_state.handle_world_event([self.logic, x_obj, x_act]))
            else:
                yield success_state

        if not state_exists:
            report_error(["RequestVerbTransitiveFailure"])

    def group_predicate_func(self, state_list, e_introduced_binding_list, x_actor_binding_list, x_what_binding_list):
        should_call_want = False
        for i in range(len(state_list)):
            if is_request_from_tree(state_list[i].get_binding("tree").value[0]):
                should_call_want = True
                break

        if not should_call_want:
            yield state_list

        else:
            if len(state_list) == 1:
                yield (state_list[0],)
            else:
                reset_operations(state_list[0])
                yield (state_list[0].record_operations(state_list[0].handle_world_event([self.group_logic, x_actor_binding_list, x_what_binding_list])),)


# use for sit_v_down
class RequestVerbIntransitive:
    def __init__(self, predicate_name_list, lemma, logic, group_logic):
        self.predicate_name_list = predicate_name_list
        self.lemma = lemma
        self.logic = logic
        self.group_logic = group_logic

    def predicate_func(self, state, e_binding, x_actor_binding):
        is_request = is_request_from_tree(state.get_binding("tree").value[0])

        def bound(x_actor):
            if is_request and is_user_type(x_actor):
                return True
            else:
                if self.lemma in state.rel.keys():
                    for pair in state.rel[self.lemma]:
                        if pair[0] == x_actor:
                            return True

                    report_error(["verbDoesntApply", x_actor, self.lemma])
                    return False

                else:
                    report_error(["verbDoesntApply", x_actor, self.lemma])
                    return False

        def unbound():
            if self.lemma in state.rel.keys():
                for i in state.rel[self.lemma]:
                    yield i[0]

        for success_state in combinatorial_predication_1(state, x_actor_binding, bound, unbound):
            x_act = success_state.get_binding(x_actor_binding.variable.name).value[0]

            if is_request and is_user_type(x_act):
                yield success_state.record_operations(success_state.handle_world_event([self.logic, x_act]))
            else:
                yield success_state

    def group_predicate_func(self,state_list,e_introduced_binding_list,x_actor_binding_list):
        should_call_want = False
        for i in range(len(state_list)):
            if is_request_from_tree(state_list[i].get_binding("tree").value[0]):
                should_call_want = True
                break

        if not should_call_want:
            yield state_list
        else:
            if len(state_list) == 1:
                yield (state_list[0],)
            else:
                reset_operations(state_list[0])
                yield (state_list[0].record_operations(state_list[0].handle_world_event([self.group_logic, x_actor_binding_list])),)



have = RequestVerbTransitive(["_have_v_1", "_get_v_1", "_take_v_1", "_have_v_1_request"], "have", "user_wants", "user_wants_group")
see = RequestVerbTransitive(["_see_v_1", "_see_v_1_request"], "see", "user_wants_to_see", "user_wants_to_see_group")
sit_down = RequestVerbIntransitive(["_sit_v_down", "_sit_v_down_request"], "sitting_down", "user_wants_to_sit", "user_wants_to_sit_group")


@Predication(vocabulary, names=have.predicate_name_list)
def _have_v_1(state, e_introduced_binding, x_actor_binding, x_object_binding):
    yield from have.predicate_func(state, e_introduced_binding, x_actor_binding, x_object_binding)


@Predication(vocabulary, names=["solution_group_" + x for x in have.predicate_name_list])
def _have_v_1_group(state_list, e_list, x_act_list, x_obj_list):
    yield from have.group_predicate_func(state_list, e_list, x_act_list, x_obj_list)


@Predication(vocabulary, names=see.predicate_name_list)
def _see_v_1(state, e_introduced_binding, x_actor_binding, x_object_binding):
    yield from see.predicate_func(state, e_introduced_binding, x_actor_binding, x_object_binding)


@Predication(vocabulary, names=["solution_group_" + x for x in see.predicate_name_list])
def _see_v_1_group(state_list, e_list, x_act_list, x_obj_list):
    yield from see.group_predicate_func(state_list, e_list, x_act_list, x_obj_list)


@Predication(vocabulary, names=sit_down.predicate_name_list)
def _sit_v_down(state, e_introduced_binding, x_actor_binding):
    yield from sit_down.predicate_func(state, e_introduced_binding, x_actor_binding)


@Predication(vocabulary, names=["solution_group_" + x for x in sit_down.predicate_name_list])
def _sit_v_down_group(state_list, e_introduced_binding_list, x_actor_binding_list):
    yield from sit_down.group_predicate_func(state_list, e_introduced_binding_list, x_actor_binding_list)


@Predication(vocabulary, names=["poss"])
def poss(state, e_introduced_binding, x_object_binding, x_actor_binding):
    def bound(x_actor, x_object):

        if "have" in state.rel.keys():
            if (x_actor, x_object) in state.rel["have"]:
                return True
            else:
                report_error(["verbDoesntApply", x_actor, "have", x_object])
                return False

        else:
            report_error(["verbDoesntApply", x_actor, "have", x_object])
            return False

    def actor_from_object(x_object):
        if "have" in state.rel.keys():
            for i in state.rel["have"]:
                if i[1] == x_object:
                    yield i[0]

    def object_from_actor(x_actor):
        if "have" in state.rel.keys():
            for i in state.rel["have"]:
                if i[0] == x_actor:
                    yield i[1]

    yield from in_style_predication_2(state, x_actor_binding, x_object_binding, bound, actor_from_object,
                                      object_from_actor)


@Predication(vocabulary, names=["_be_v_id"])
def _be_v_id(state, e_introduced_binding, x_actor_binding, x_object_binding):
    def criteria_bound(x_actor, x_object):
        if not x_object[0] == "{":
            first_in_second = x_actor in all_instances_and_spec(state, x_object)
            second_in_first = x_object in all_instances_and_spec(state, x_actor)

            return first_in_second or second_in_first
        else:
            x_object = json.loads(x_object)
            if x_object["structure"] == "price_type":
                if type(x_object["relevant_var_value"]) is int:
                    if not (x_actor, x_object["relevant_var_value"]) in state.sys["prices"]:
                        report_error("WrongPrice")
                        return False
            return True

    def unbound(x_object):
        for i in all_instances(state, x_object):
            yield i
        yield x_object

    for success_state in in_style_predication_2(state, x_actor_binding, x_object_binding, criteria_bound, unbound,
                                                unbound):
        x_obj = success_state.get_binding(x_object_binding.variable.name).value[0]
        x_act = success_state.get_binding(x_actor_binding.variable.name).value[0]
        if not x_obj[0] == "{":
            yield success_state
        else:
            x_obj = json.loads(x_obj)
            if x_obj["structure"] == "price_type":
                if x_obj["relevant_var_value"] == "to_determine":
                    if instance_of_what(state, x_act) in success_state.sys["prices"].keys():
                        yield success_state.set_x(x_obj["relevant_var_name"], (str(instance_of_what(state, x_act)) + ": " + str(success_state.sys["prices"][instance_of_what(state, x_act)]) + " dollars",)).record_operations([SetKnownPriceOp(instance_of_what(state, x_act))])

                    else:
                        yield success_state.record_operations([RespondOperation("Haha, it's not for sale.")])


@Predication(vocabulary, names=["_cost_v_1"])
def _cost_v_1(state, e_introduced_binding, x_actor_binding, x_object_binding):
    def criteria_bound(x_actor, x_object):
        if not x_object[0] == "{":
            report_error("Have not dealt with declarative cost")
        else:
            x_object = json.loads(x_object)
            if x_object["structure"] == "price_type":
                if type(x_object["relevant_var_value"]) is int:
                    if not (instance_of_what(state, x_act), x_object["relevant_var_value"]) in state.sys["prices"]:
                        report_error("WrongPrice")
                        return False
            return True

    def get_actor(x_object):
        if False:
            yield None

    def get_object(x_actor):
        if instance_of_what(state, x_act) in state.sys["prices"].keys():
            yield str(instance_of_what(state, x_act)) + ": " + str(state.sys["prices"][instance_of_what(state, x_act)]) + " dollars"

    for success_state in in_style_predication_2(state, x_actor_binding, x_object_binding, criteria_bound, get_actor,
                                                get_object):
        x_obj = success_state.get_binding(x_object_binding.variable.name).value[0]
        x_act = success_state.get_binding(x_actor_binding.variable.name).value[0]
        if not x_obj[0] == "{":
            yield success_state
        else:
            x_obj = json.loads(x_obj)
            if x_obj["structure"] == "price_type":
                if x_obj["relevant_var_value"] == "to_determine":
                    if instance_of_what(state, x_act) in success_state.sys["prices"].keys():
                        yield success_state.set_x(x_obj["relevant_var_name"], (
                            str(instance_of_what(state, x_act)) + ": " + str(success_state.sys["prices"][instance_of_what(state, x_act)]) + " dollars",))
                    else:
                        yield success_state.record_operations([RespondOperation("Haha, it's not for sale.")])


@Predication(vocabulary, names=["_be_v_there"])
def _be_v_there(state, e_introduced_binding, x_object_binding):
    def bound_variable(value):
        yield value in state.get_entities()

    def unbound_variable():
        for i in state.get_entities():
            yield i

    yield from combinatorial_predication_1(state, x_object_binding, bound_variable, unbound_variable)


@Predication(vocabulary, names=["compound"])
def compound(state, e_introduced_binding, x_first_binding, x_second_binding):
    assert (x_first_binding is not None)
    assert (x_second_binding is not None)
    yield state.set_x(x_first_binding.variable.name, (state.get_binding(x_first_binding.variable.name).value[0] + ", " +
                                                      state.get_binding(x_second_binding.variable.name).value[0],))


# Generates all the responses that predications can
# return when an error occurs
def generate_custom_message(tree_info, error_term):
    # See if the system can handle converting the error
    # to a message first
    system_message = perplexity.messages.generate_message(tree_info, error_term)
    if system_message is not None:
        return system_message

    # error_term is of the form: [index, error] where "error" is another
    # list like: ["name", arg1, arg2, ...]. The first item is the error
    # constant (i.e. its name). What the args mean depends on the error
    error_predicate_index = error_term[0]
    error_arguments = error_term[1]
    error_constant = error_arguments[0] if error_arguments is not None else "no error set"

    if error_constant == "notAThing":
        arg1 = error_arguments[1]
        # english_for_delphin_variable() converts a variable name like 'x3' into the english words
        # that it represented in the MRS
        arg2 = english_for_delphin_variable(error_predicate_index, error_arguments[2], tree_info)
        return f"{arg1} is not {arg2}"
    if error_constant == "notOn":
        arg1 = error_arguments[1]
        arg2 = error_arguments[2]
        return f"No. {arg1} is not on {arg2}"
    if error_constant == "verbDoesntApply":
        return f"No. {error_arguments[1]} does not {error_arguments[2]} {error_arguments[3]}"
    else:
        # No custom message, just return the raw error for debugging
        return str(error_term)


def reset():
    # return State([])
    # initial_state = WorldState({}, ["pizza", "computer", "salad", "soup", "steak", "ham", "meat","special"])
    initial_state = WorldState({},
                                {"prices": {"salad": 3, "steak": 10, "soup": 4, "salmon": 12, "chicken": 7, "bacon" : 2},
                                "responseState": "initial"
                                })
    initial_state = initial_state.add_rel("table", "specializes", "thing")
    initial_state = initial_state.add_rel("menu", "specializes", "thing")
    initial_state = initial_state.add_rel("food", "specializes", "thing")
    initial_state = initial_state.add_rel("person", "specializes", "thing")
    initial_state = initial_state.add_rel("son", "specializes", "person")


    initial_state = initial_state.add_rel("dish", "specializes", "food")
    initial_state = initial_state.add_rel("special", "specializes", "dish")

    initial_state = initial_state.add_rel("pizza", "specializes", "dish")
    initial_state = initial_state.add_rel("meat", "specializes", "dish")
    initial_state = initial_state.add_rel("veggie", "specializes", "dish")
    initial_state = initial_state.add_rel("steak", "specializes", "meat")
    initial_state = initial_state.add_rel("chicken", "specializes", "meat")
    initial_state = initial_state.add_rel("salmon", "specializes", "meat")
    initial_state = initial_state.add_rel("bacon", "specializes", "meat")

    initial_state = initial_state.add_rel("table1", "instanceOf", "table")
    initial_state = initial_state.add_rel("table1", "maxCap", 4)




    initial_state = initial_state.add_rel("menu1", "instanceOf", "menu")


    initial_state = initial_state.add_rel("soup", "specializes", "special")
    initial_state = initial_state.add_rel("salad", "specializes", "special")
    initial_state = initial_state.add_rel("soup", "specializes", "veggie")
    initial_state = initial_state.add_rel("salad", "specializes", "veggie")


    dish_types = ["soup","salad","bacon","salmon","steak","chicken"]
    for j in dish_types:
        for i in range(3):
            initial_state = initial_state.add_rel(j+str(i), "instanceOf", j)
            initial_state = initial_state.add_rel("computer", "have", j+str(i))
            if j == "chicken":
                initial_state = initial_state.add_rel(j+str(i), "isAdj", "roasted")
            if j == "salmon":
                initial_state = initial_state.add_rel(j+str(i), "isAdj", "grilled")

    initial_state = initial_state.add_rel("user", "have", "bill1")

    initial_state = initial_state.add_rel("steak1", "on", "menu1")
    initial_state = initial_state.add_rel("chicken1", "on", "menu1")
    initial_state = initial_state.add_rel("salmon1", "on", "menu1")
    initial_state = initial_state.add_rel("bacon1", "on", "menu1")

    initial_state = initial_state.add_rel("bill", "specializes", "thing")
    initial_state = initial_state.add_rel("check", "specializes", "thing")
    initial_state = initial_state.add_rel("bill1", "instanceOf", "bill")
    initial_state = initial_state.add_rel("bill1", "instanceOf", "check")
    initial_state = initial_state.add_rel(0, "valueOf", "bill1")
    initial_state = initial_state.add_rel("room", "contains", "user")

    initial_state = initial_state.add_rel("soup", "priceUnknownTo", "user")
    initial_state = initial_state.add_rel("salad", "priceUnknownTo", "user")

    initial_state = initial_state.add_rel("son1", "instanceOf", "son")
    initial_state = initial_state.add_rel("user", "have", "son1")


    return initial_state


def error_priority(error_string):
    global error_priority_dict
    if error_string is None:
        return 0

    else:
        if error_string[1] is None:
            # No error specified
            return error_priority_dict["noError"]

        error_constant = error_string[1][0]
        priority = error_priority_dict.get(error_constant, error_priority_dict["defaultPriority"])
        if error_constant == "unknownWords":
            priority -= len(error_string[1][1])

        return priority


error_priority_dict = {
    # No error specified
    "noError": 100,
    # Unknown words error should only be shown if
    # there are no other errors, AND the number
    # of unknown words is subtracted from it so
    # lower constants should be defined below this:
    # "unknownWordsMin": 800,
    "unknownWords": 900,
    # Slightly better than not knowing the word at all
    "formNotUnderstood": 901,
    "defaultPriority": 1000,

    # This is just used when sorting to indicate no error, i.e. success.
    # Nothing should be higher
    "success": 10000000
}


def hello_world():
    user_interface = UserInterface(reset, vocabulary, message_function=generate_custom_message,
                                   error_priority_function=error_priority)

    while True:
        user_interface.interact_once()
        print()


if __name__ == '__main__':
    print("Hello there, what can I do for you?")
    # ShowLogging("Pipeline")
    # ShowLogging("Transformer")
    hello_world()
