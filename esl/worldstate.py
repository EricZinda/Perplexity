import copy
import json
import numbers
import esl.esl_planner
from perplexity.predications import is_concept, Concept, concept_from_lemma
from perplexity.response import RespondOperation
from perplexity.set_utilities import Measurement
from perplexity.state import State
from perplexity.tree import TreePredication
from perplexity.utilities import at_least_one_generator


def noun_structure(value, part):
    if isinstance(value, Concept):
        # [({'for_count': 2, 'noun': 'table1', 'structure': 'noun_for'},)]
        return value.modifiers().get(part, None)

    else:
        if part == "noun":
            return value


def in_scope_initialize(state):
    # Only concepts that are explicitly marked as "in scope"
    # are in scope
    in_scope_concepts = set()
    for i in state.all_rel("conceptInScope"):
        if i[1] == "true":
            in_scope_concepts.add(concept_from_lemma(i[0]))

    # Any instances that the user or son "have" are in scope
    in_scope_instances = set()
    for i in state.all_rel("have"):
        if is_user_type(i[0]):
            in_scope_instances.add(i[1])

    # Any place where the user are son are "at" is in scope
    for i in state.all_rel("at"):
        if is_user_type(i[0]):
            in_scope_instances.add(i[1])

    return {"InScopeConcepts": in_scope_concepts,
            "InScopeInstances": in_scope_instances}


def in_scope(initial_data, state, value):
    if is_concept(value):
        return value in initial_data["InScopeConcepts"]
    else:
        return value in initial_data["InScopeInstances"]


def is_user_type(val):
    if not isinstance(val, tuple):
        return val in ["user", "son1"]

    else:
        for i in val:
            if i not in ["user", "son1"]:
                return False
        return True

def all_user_type(val):
    assert isinstance(val,list)
    for i in val:
        if not is_user_type(i):
            return False
    return True

def specializations(state, base_type):
    for i in state.all_rel("specializes"):
        if i[1] == base_type:
            yield from specializations(state, i[0])
            yield i[0]


def sort_of(state, thing_list, possible_types):
    if not isinstance(thing_list, list) and not isinstance(thing_list, tuple):
        thing_list = [thing_list]
    if not isinstance(possible_types, list) and not isinstance(possible_types, tuple):
        possible_types = [possible_types]

    for thing in thing_list:
        if thing in possible_types:
            continue

        found = False
        for i in state.all_rel("specializes"):
            if i[1] in possible_types:
                if sort_of(state, thing, i[0]):
                    found = True
                    break
        if found:
            continue

        found = False
        for i in state.all_rel("instanceOf"):
            if i[1] in possible_types:
                if sort_of(state, thing, i[0]):
                    found = True
                    break
        if found:
            continue

        return False

    return True


def reset_operations(state):
    state.operations = []


def all_instances(state, thing):
    proc = [thing]
    proc_idx = 0
    inst = set()

    while proc_idx < len(proc):
        to_process = proc[proc_idx]
        for i in state.all_rel("specializes"):
            if i[1] == to_process:
                if i[0] not in proc:
                    proc += [i[0]]

        for i in state.all_rel("instanceOf"):
            if i[1] == to_process:
                if i[0] not in inst:
                    yield i[0]
                    inst.add(i[0])
        proc_idx += 1


def all_instances_and_spec(state, thing):
    yield thing

    proc = [thing]
    proc_idx = 0
    inst = set()

    while proc_idx < len(proc):
        to_process = proc[proc_idx]
        for i in state.all_rel("specializes"):
            if i[1] == to_process:
                if i[0] not in proc:
                    proc += [i[0]]
                    yield i[0]

        for i in state.all_rel("instanceOf"):
            if i[1] == to_process:
                if i[0] not in inst:
                    yield i[0]
                    inst.add(i[0])
        proc_idx += 1


def all_ancestors(state, thing):
    proc = [thing]
    proc_idx = 0

    while proc_idx < len(proc):
        to_process = proc[proc_idx]
        for i in state.all_rel("instanceOf"):
            if i[0] == to_process:
                if i[1] not in proc:
                    yield i[1]
                    proc += [i[1]]

        for i in state.all_rel("specializes"):
            if i[0] == to_process:
                if i[1] not in proc:
                    proc += [i[1]]
                    yield i[1]
        proc_idx += 1


def instance_of_or_concept_name(state, thing):
    if is_concept(thing):
        return thing.concept_name
    else:
        return instance_of_what(state, thing)


def instance_of_what(state, thing):
    for i in state.all_rel("instanceOf"):
        if i[0] == thing:
            return i[1]


def is_type(state, thing):
    return isinstance(thing, str) and not is_instance(state, thing)


def is_instance(state, thing):
    return instance_of_what(state, thing) is not None


def location_of_type(state, who, where_type):
    for location in rel_objects(state, who, "at"):
        if sort_of(state, location, where_type):
            return True

    return False


def count_of_instances_and_concepts(state, concepts_original):
    concepts = copy.copy(concepts_original)
    for concept in concepts:
        concepts += [concept_from_lemma(x) for x in specializations(state, concept.concept_name)]
    concept_count = len(concepts)

    instances = []
    for concept in concepts:
        instances += list(all_instances(state, concept.concept_name))
    instance_count = len(instances)

    scope_data = in_scope_initialize(state)
    instance_in_scope_count = 0
    for instance in instances:
        if in_scope(scope_data, state, instance):
            instance_in_scope_count += 1

    concept_in_scope_count = 0
    for concept in concepts:
        if in_scope(scope_data, state, concept):
            concept_in_scope_count += 1

    return concept_count, concept_in_scope_count, instance_count, instance_in_scope_count


def object_to_store(o):
    return o.concept_name if is_concept(o) else o


def store_to_object(state, s):
    if not is_instance(state, s):
        return concept_from_lemma(s)
    else:
        return s


def serial_store_to_object(state, s_list):
    return [store_to_object(state, s) for s in s_list]


def find_unused_value_from_concept(concept, solution_group_generator):
    for solution_group in solution_group_generator:
        for solution in solution_group:
            concept_variable_value = solution.get_binding(concept.variable_name).value
            all_items_available = True
            for concept_variable_item in concept_variable_value:
                taken = at_least_one_generator(rel_subjects(solution, "have", concept_variable_item))
                if taken is not None:
                    # Someone already has this
                    all_items_available = False
                    break

            if all_items_available:
                return concept_variable_value

def find_unused_item(state, object_type):
    for potential in all_instances(state, object_type):
        taken = at_least_one_generator(rel_subjects(state, "have", potential))
        if taken is None:
            return potential


def has_item_of_type(state, object_type):
    for item in rel_subjects_objects(state, "have"):
        if sort_of(state, item[1], object_type):
            yield item[0]


def rel_check(state, subject, rel, object):
    return (subject, object) in state.all_rel(rel)


def rel_subjects_objects(state, rel):
    for item in state.all_rel(rel):
        yield item


def rel_objects(state, subject, rel):
    for item in state.all_rel(rel):
        if item[0] == subject:
            yield item[1]


def rel_subjects(state, rel, object):
    for item in state.all_rel(rel):
        if item[1] == object:
            yield item[0]


def has_type(state, subject, type):
    for item in state.all_rel("have"):
        if item[0] == subject and sort_of(state, item[1], type):
            return True

    return False


class AddRelOp(object):
    def __init__(self, rel):
        self.toAdd = rel

    def apply_to(self, state):
        state.mutate_add_rel(self.toAdd[0], self.toAdd[1], self.toAdd[2])


class DeleteRelOp(object):
    def __init__(self, rel):
        self.toDelete = rel

    def apply_to(self, state):
        state.mutate_delete_rel(self.toDelete[0], self.toDelete[1], self.toDelete[2])


class AddBillOp(object):
    def __init__(self, item):
        self.toAdd = item

    def apply_to(self, state):
        prices = state.sys["prices"]
        assert self.toAdd in prices
        state.mutate_add_bill(prices[self.toAdd])


class SetKnownPriceOp(object):
    def __init__(self, item):
        self.toAdd = item

    def apply_to(self, state):
        state.mutate_remove_unknown_price(self.toAdd)


class ResetOrderAndBillOp(object):
    def apply_to(self, state):
        state.mutate_reset_bill()
        state.mutate_reset_order()


class ResponseStateOp(object):
    def __init__(self, item):
        self.toAdd = item

    def apply_to(self, state):
        state.mutate_set_response_state(self.toAdd)


class WorldState(State):
    def __init__(self, relations, system, name=None, world_state_frame=None):
        super().__init__([])
        self.__name__ = name
        self._rel = relations
        self.sys = system
        self.frame_name = name
        self._world_state_frame = world_state_frame

    # *********** Used for HTN
    def copy(self, new_name=None):
        return copy.deepcopy(self)

    def display(self, heading=None):
        """
        Print the state's state-variables and their values.
         - heading (optional) is a heading to print beforehand.
        """
        pass

    def state_vars(self):
        pass

    # *********** Used for HTN

    # ******* Base Operations ********
    def mutate_delete_rel(self, first, relation_name, second, frame=None):
        world_state = self.world_state_frame()

        new_relation = copy.deepcopy(world_state._rel)
        if relation_name in new_relation:
            for item in new_relation[relation_name]:
                if item[0] == first and item[1] == second:
                    new_relation[relation_name].remove(item)
                    break
        world_state._rel = new_relation

    def add_rel(self, first, relation_name, second, frame=None):
        world_state = self.world_state_frame()

        new_relation = copy.deepcopy(world_state._rel)
        if relation_name not in new_relation:
            new_relation[relation_name] = [(first, second, frame)]
        else:
            new_relation[relation_name] += [(first, second, frame)]

        return WorldState(new_relation, world_state.sys)

    def mutate_add_rel(self, first, relation_name, second, frame=None):
        world_state = self.world_state_frame()

        new_relation = copy.deepcopy(world_state._rel)
        if relation_name not in new_relation:
            new_relation[relation_name] = [(first, second, frame)]
        else:
            new_relation[relation_name] += [(first, second, frame)]

        world_state._rel = new_relation

    def mutate_reset_rel(self, keyname):
        world_state = self.world_state_frame()

        new_relation = copy.deepcopy(world_state._rel)
        new_relation.pop(keyname, None)
        world_state._rel = new_relation

    def all_rel(self, rel):
        if rel not in self._rel.keys():
            return
        else:
            yield from [(x[0], x[1]) for x in self._rel[rel]]

    def rel_exists(self, rel):
        return rel in self._rel.keys()

    # ******* Base Operations ********

    # ******* Overrides of State ********
    def __repr__(self):
        if self._world_state_frame is None:
            return super().__repr__()
        else:
            return self._world_state_frame.__repr__()

    def get_binding(self, variable_name):
        # return super().get_binding(variable_name)
        if self._world_state_frame is None:
            return super().get_binding(variable_name)
        else:
            return self._world_state_frame.get_binding(variable_name)

    def set_variable_data(self, variable_name, determiner=None, quantifier=None):
        # return super().set_variable_data(variable_name, determiner, quantifier)
        if self._world_state_frame is None:
            return super().set_variable_data(variable_name, determiner, quantifier)
        else:
            newState = copy.deepcopy(self)
            newState._world_state_frame = self._world_state_frame.set_variable_data(variable_name, determiner, quantifier)
            return newState

    def set_x(self, variable_name, item, combinatoric=False, determiner=None, quantifier=None):
        # return super().set_x(variable_name, item, combinatoric, determiner, quantifier)
        if self._world_state_frame is None:
            return super().set_x(variable_name, item, combinatoric, determiner, quantifier)
        else:
            newState = copy.deepcopy(self)
            newState._world_state_frame = self._world_state_frame.set_x(variable_name, item, combinatoric, determiner, quantifier)
            return newState

    def add_to_e(self, event_name, key, value):
        # return super().add_to_e(event_name, key, value)
        if self._world_state_frame is None:
            return super().add_to_e(event_name, key, value)
        else:
            newState = copy.deepcopy(self)
            newState._world_state_frame =self._world_state_frame.add_to_e(event_name, key, value)
            return newState

    def frames(self):
        # Start with just the in scope frame
        in_scope = in_scope_initialize(self)

        # Concept of "thing" isn't declared anywhere but is always in scope
        # Nothing has "user" but they are always in scope
        everything_in_scope = set(["thing", "user"])
        everything_in_scope.update(in_scope["InScopeInstances"])
        everything_in_scope.update([x.concept_name for x in in_scope["InScopeConcepts"]])

        # All generic concepts are always in scope
        everything_in_scope.update(x[0] for x in self.all_rel("specializes"))

        # Now include all relations any of these in scope things have
        new_rels = {}
        for item in self._rel.items():
            if item[0] not in new_rels:
                new_rels[item[0]] = []

            for relation in item[1]:
                if relation[0] in everything_in_scope and (relation[1] == "true" or relation[1] in everything_in_scope):
                    new_rels[item[0]] += [relation]

        yield WorldState(new_rels, copy.deepcopy(self.sys), "in_scope", self)

        # Then yield everything
        yield self

    def world_state_frame(self):
        if self._world_state_frame is None:
            return self
        else:
            return self._world_state_frame

    def all_individuals(self):
        for i in self.get_entities():
            yield i

    # Operations are always applied to the world_state frame and thus
    # create a new world_state frame. But if this world state is a different
    # frame, then

    # But we need to return a copy
    # Call to apply a list of operations to
    # a new State object
    def record_operations(self, operation_list):
        newState = copy.deepcopy(self)
        world_state = newState.world_state_frame()
        for operation in operation_list:
            world_state.operations.append(operation)

        return newState

    # Call to apply a list of operations to
    # a new State object
    def apply_operations(self, operation_list, record_operations=True):
        newState = copy.deepcopy(self)
        world_state = newState.world_state_frame()
        for operation in operation_list:
            operation.apply_to(world_state)
            if record_operations:
                world_state.operations.append(operation)

        return newState

    def get_operations(self):
        world_state = self.world_state_frame()
        return copy.deepcopy(world_state.operations)

    # ******* Overrides of State ********

    def bill_total(self):
        for i in self.all_rel("valueOf"):
            if i[1] == "bill1":
                return i[0]

    def mutate_remove_unknown_price(self, toRemove):
        world_state = self.world_state_frame()
        if (toRemove, "user") in world_state.all_rel("priceUnknownTo"):
            world_state._rel["priceUnknownTo"].remove((toRemove, "user", None))

    def mutate_add_bill(self, addition):
        world_state = self.world_state_frame()
        new_relation = copy.deepcopy(world_state._rel)
        for i in range(len(new_relation["valueOf"])):
            if new_relation["valueOf"][i][1] == "bill1":
                new_relation["valueOf"][i] = (addition + new_relation["valueOf"][i][0], "bill1")
        world_state._rel = new_relation

    def mutate_reset_bill(self):
        world_state = self.world_state_frame()
        new_relation = copy.deepcopy(world_state._rel)
        for i in range(len(new_relation["valueOf"])):
            if new_relation["valueOf"][i][1] == "bill1":
                new_relation["valueOf"][i] = (0, "bill1")
        world_state._rel = new_relation

    def mutate_reset_order(self):
        world_state = self.world_state_frame()
        new_relation = copy.deepcopy(world_state._rel)
        new_relation["ordered"] = []
        world_state._rel = new_relation

    def mutate_set_response_state(self, new_state):
        world_state = self.world_state_frame()
        world_state.sys["responseState"] = new_state

    def get_entities(self):
        entities = set()
        for i in self._rel.keys():
            for j in self.all_rel(i):
                entities.add(j[0])
                entities.add(j[1])
        return entities

    def get_reprompt(self):
        if self.sys["responseState"] == "something_to_eat":
            return " \nWaiter: Can I get you something to eat?"
        if self.sys["responseState"] == "anticipate_party_size":
            return " \nWaiter: How many in your party?"
        if self.sys["responseState"] == "anything_else":
            return " \nWaiter: Can I get you something else before I put your order in?"
        return ""

    def user_ordered_veg(self):
        veggies = list(all_instances_and_spec(self, "veggie"))
        if self.rel_exists("ordered"):
            for i in self.all_rel("ordered"):
                if i[0] == "user":
                    if i[1] in veggies:
                        return True
        return False

    # def user_wants(self, wanted):
    #     # if wanted not in self.get_entities():
    #     #   return [RespondOperation("Sorry, we don't have that.")]
    #
    #     if wanted[0] == "{":
    #         wanted_dict = json.loads(wanted)
    #         if wanted_dict["structure"] == "noun_for":
    #             if wanted_dict["noun"] == "table1":
    #                 if ("user", "table") in self.all_rel("at"):
    #                     return [RespondOperation("Um... You're at a table." + self.get_reprompt()),
    #                             ResponseStateOp("anything_else")]
    #                 if wanted_dict["for_count"] > 2:
    #                     return [RespondOperation("Host: Sorry, we don't have a table with that many seats")]
    #                 if wanted_dict["for_count"] < 2:
    #                     return [RespondOperation("Johnny: Hey! That's not enough seats!")]
    #                 if wanted_dict["for_count"] == 2:
    #                     return (RespondOperation(
    #                         "Host: Perfect! Please come right this way. The host shows you to a wooden table with a checkered tablecloth. "
    #                         "A minute goes by, then your waiter arrives.\nWaiter: Hi there, can I get you something to eat?"),
    #                             AddRelOp(("user", "at", "table")), ResponseStateOp("something_to_eat"))
    #
    #             else:
    #                 wanted = wanted_dict["noun"]
    #
    #     if sort_of(self, wanted, "food"):
    #         if ("user", "table") in self.all_rel("at"):
    #             if "ordered" in self.rel.keys():
    #                 if ("user", wanted) in self.all_rel("ordered"):
    #                     return [RespondOperation(
    #                         "Sorry, you got the last one of those. We don't have any more. Can I get you something else?"),
    #                         ResponseStateOp("anything_else")]
    #             if (instance_of_what(self, wanted), "user") in self.all_rel("priceUnknownTo"):
    #                 return [RespondOperation(
    #                     "Son: Wait, let's not order that before we know how much it costs." + self.get_reprompt())]
    #
    #             assert (instance_of_what(self,wanted) in self.sys["prices"])
    #             if self.sys["prices"][instance_of_what(self,wanted)] + self.bill_total() > 15:
    #                 return [RespondOperation("Son: Wait, we already spent $" + str(
    #                     self.bill_total()) + " so if we get that, we won't be able to pay for it with $15." + self.get_reprompt())]
    #
    #             return [RespondOperation("Excellent Choice! Can I get you anything else?"),
    #                     AddRelOp(("user", "ordered", wanted)), AddBillOp(wanted),
    #                     ResponseStateOp("anything_else")]
    #
    #         return [RespondOperation("Sorry, you must be seated to order")]
    #
    #     for i in all_instances(self, "table"):
    #         if i == wanted:
    #             if ("user", "table") in self.all_rel("at"):
    #                 return [RespondOperation("Um... You're at a table." + self.get_reprompt())]
    #             return [RespondOperation("How many in your party?"), ResponseStateOp("anticipate_party_size")]
    #
    #     if sort_of(self, wanted, "menu"):
    #         if ("user", "table") in self.all_rel("at"):
    #             if ("user", "menu1") not in self.all_rel("have"):
    #                 return [AddRelOp(("user", "have", "menu1")), RespondOperation(
    #                     "Waiter: Oh, I forgot to give you the menu? Here it is. The waiter walks off.\nSteak -- $10\nRoasted Chicken -- $7\nGrilled Salmon -- $12\nYou read the menu and then the waiter returns.\nWaiter: What can I get you?"),
    #                         ResponseStateOp("anticipate_dish")]
    #             else:
    #                 return [RespondOperation(
    #                     "Oh, I already gave you a menu. You look and see that there is a menu in front of you.\nSteak -- $10\nRoasted Chicken -- $7\nGrilled Salmon -- $12\n" + self.get_reprompt())]
    #         return [RespondOperation("Sorry, you must be seated to order")]
    #
    #     if wanted == "bill1":
    #         for i in self.all_rel("valueOf"):
    #             if i[1] == "bill1":
    #                 total = i[0]
    #                 if self.sys["responseState"] == "done_ordering":
    #                     return [RespondOperation(
    #                         "Your total is " + str(total) + " dollars. Would you like to pay by cash or card?"),
    #                         ResponseStateOp("way_to_pay")]
    #                 else:
    #                     return [RespondOperation("But... you haven't got any food yet!" + self.get_reprompt())]
    #
    #     return [RespondOperation("Sorry, I can't get that for you at the moment.")]

    def user_wants_multiple(self, wanted_tuple):
        foods = list(all_instances(self, "food"))
        if len(wanted_tuple) == 1:
            return self.user_wants(wanted_tuple[0])

        for i in wanted_tuple:
            if i not in foods:
                return [RespondOperation("Hey, one thing at a time please..." + self.get_reprompt())]

        userKnowsPrices = True
        for i in wanted_tuple:
            if (instance_of_what(self, i), "user") in self.all_rel("priceUnknownTo"):
                return [RespondOperation(
                    "Son: Wait, let's not order anything before we know how much it costs." + self.get_reprompt())]
        total_price = 0

        for i in wanted_tuple:
            total_price += self.sys["prices"][instance_of_what(self, i)]

        if total_price + self.bill_total() > 15:
            return [RespondOperation(
                "Son: Wait, we've spent $" + str(self.bill_total()) + " and all that food costs $" + str(
                    total_price) + " so if we get all that, we won't be able to pay for it with $15." + self.get_reprompt())]

        for i in wanted_tuple:
            if "ordered" in self.rel.keys():
                if ("user", i) in self.all_rel("ordered"):
                    return [RespondOperation(
                        "Sorry, you got the last " + i + " . We don't have any more." + self.get_reprompt())]
        for i in wanted_tuple:
            if wanted_tuple.count(i) > 1:
                return [
                    RespondOperation("Sorry, we only have one" + i + ". Please try again." + self.get_reprompt())]

        toReturn = [RespondOperation("Excellent Choices! Can I get you anything else?"),
                    ResponseStateOp("anything_else")]
        for i in wanted_tuple:
            toReturn += [AddRelOp(("user", "ordered", i)), AddBillOp(i)]
        return toReturn

    def user_wants_group(self, users, wanted):
        allTables = True  # if multiple actors (son and user) want table, we don't need two tables
        allMenus = True
        allTableRequests = True

        for i in wanted:
            if not sort_of(self, i.value[0], "table"):
                allTables = False
            if not sort_of(self, i.value[0], "menu"):
                allMenus = False
            if not i.value[0][0] == "{":
                allTableRequests = False
            else:
                if not json.loads(i.value[0])["structure"] == "noun_for":
                    allTableRequests = False
        if allTables:
            return self.handle_world_event(["user_wants", "table1"])
        if allMenus:
            return self.handle_world_event(["user_wants", "menu1"])
        elif allTableRequests:
            return self.handle_world_event(["user_wants", wanted[0].value[0]])
        else:
            unpack = lambda x: x.value[0]
            return self.handle_world_event(["user_wants_multiple", [unpack(j) for j in wanted]])

    def user_wants_to_see(self, wanted):
        if wanted == "menu1":
            return self.user_wants("menu1")
        elif wanted == "table1":
            return [RespondOperation("All our tables are nice. Trust me on this one" + self.get_reprompt())]
        else:
            return [RespondOperation("Sorry, I can't show you that." + self.get_reprompt())]

    def user_wants_to_see_group(self, actor_list, wanted_list):
        all_menu = True
        for i in wanted_list:
            if not sort_of(self, i.value[0], "menu"):
                all_menu = False
                break
        if all_menu:
            return self.handle_world_event(["user_wants", "menu1"])
        else:
            return [RespondOperation("Sorry, I can't show you that." + self.get_reprompt())]

    def no(self):
        return self.find_plan([('complete_order',)])

    def yes(self):
        if self.sys["responseState"] in ["anything_else", "something_to_eat"]:
            return [RespondOperation("Ok, what?"), ResponseStateOp("anticipate_dish")]
        else:
            return [RespondOperation("Hmm. I didn't understand what you said." + self.get_reprompt())]

    # This should always be the answer to a question since it is a partial sentence that generated
    # an unknown() predication in the MRS for the verb
    def unknown(self, x):
        concept_name = None
        if isinstance(x, Concept):
            concept_name = x.concept_name
        if self.sys["responseState"] == "way_to_pay":
            if x in ["cash", "card", "card, credit"]:
                return [RespondOperation("Ah. Perfect! Have a great rest of your day.")]
            else:
                return [RespondOperation("Hmm. I didn't understand what you said." + self.get_reprompt())]

        elif self.sys["responseState"] in ["anticipate_dish", "anything_else", "initial"]:
            if concept_name is not None:
                if concept_name in self.get_entities():
                    return self.handle_world_event(["user_wants", x])
                else:
                    return [RespondOperation("Sorry, we don't have that")]
            else:
                return [RespondOperation("Sorry, we don't allow ordering specific things like that")]

        elif self.sys["responseState"] in ["anticipate_party_size"]:
            if isinstance(x, numbers.Number):
                table_concept = concept_from_lemma("table")
                # e_binding, x_what_binding, x_for_binding
                args = ["e999", table_concept.variable_name, "x1000"]
                table_concept = table_concept.add_bound_modifier(TreePredication(0, "_for_p", args, arg_names=["ARG0", "ARG1", "ARG2"]),
                                                                 [None, None, (x, )],
                                                                 {"x1000":[]})

                actors = [("user",)]
                whats = [(table_concept,)]
                return self.find_plan([('satisfy_want', actors, whats, 1)])
            if is_concept(x) and x.concept_name == "generic_entity" and noun_structure(x, "card") is not None:
                actors = [("user",)]
                whats = [(Concept("table", dict({"for": (Concept('generic_entity', {'card': 2}),)})),)]
                return self.find_plan([('satisfy_want', actors, whats)])

            else:
                return [RespondOperation("Hmm. I didn't understand what you said." + self.get_reprompt())]

        else:
            return [RespondOperation("Hmm. I didn't understand what you said." + self.get_reprompt())]

    def find_plan(self, tasks):
        current_state = esl.esl_planner.do_task(self.world_state_frame(), tasks)
        if current_state is not None:
            return current_state.get_operations()
        else:
            return [RespondOperation("I'm not sure what to do about that." + self.get_reprompt())]

    def handle_world_event(self, args):
        if args[0] == "user_wants":
            return self.find_plan([('satisfy_want', [("user",)], [(args[1],)], 1)])
        elif args[0] == "user_wants_to_see":
            return self.user_wants_to_see(args[1])
        elif args[0] == "user_wants_multiple":
            return self.user_wants_multiple(args[1])
        elif args[0] == "no":
            return self.no()
        elif args[0] == "yes":
            return self.yes()
        elif args[0] == "unknown":
            # User said something that wasn't a full sentence that generated an
            # unknown() predication
            return self.unknown(args[1])
        elif args[0] == "user_wants_to_sit":
            return self.user_wants("table1")
        elif args[0] == "user_wants_to_sit_group":
            return self.user_wants("table1")
        elif args[0] == "user_wants_group":
            who_list = [binding.value for binding in args[1].solution_values]
            what_list = [binding.value for binding in args[2].solution_values]
            return self.find_plan([('satisfy_want', who_list, what_list)])

            return self.user_wants_group(args[1], args[2])
        elif args[0] == "user_wants_to_see_group":
            return self.user_wants_to_see_group(args[1], args[2])
