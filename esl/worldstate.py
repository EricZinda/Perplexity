import copy
import json
import logging
import numbers
import pickle
import esl.esl_planner
from perplexity.predications import is_concept, Concept
from perplexity.response import RespondOperation
from perplexity.set_utilities import DisjunctionValue
from perplexity.state import State


def in_scope_initialize(state):
    # Only concepts that are explicitly marked as "in scope"
    # are in scope
    in_scope_concepts = set()
    for i in state.all_rel("conceptInScope"):
        if i[1] == "true":
            in_scope_concepts.add(ESLConcept(i[0]))

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


def in_scope(initial_data, context, state, value):
    if is_concept(value):
        for concept in initial_data["InScopeConcepts"]:
            if concept.entailed_by(context, state, value):
                return True
        return False
    else:
        return value in initial_data["InScopeInstances"]


def user_types():
    yield from ["user", "son1"]


def requestable_concepts_by_sort(state):
    requestable_items = {ESLConcept("table"): ("table", "table"),
                         ESLConcept("menu"): ("menu", "menu"),
                         ESLConcept("bill"): ("bill", "bill")}

    # Add all the things you can order
    for dish in orderable_concepts(state):
        requestable_items[dish] = ("dish", dish.single_sort_name())

    return requestable_items


def orderable_concepts(state):
    things_we_know = []
    for menu_item in rel_subjects(state, "on", "menu"):
        things_we_know.append(ESLConcept(menu_item))

    things_we_know += specials_concepts(state)

    for menu_item in rel_subjects(state, "specializes", "drink"):
        things_we_know.append(ESLConcept(menu_item))

    return things_we_know


def specials_concepts(state):
    things_we_know = []
    for menu_item in rel_subjects(state, "specializes", "special"):
        things_we_know.append(ESLConcept(menu_item))

    return things_we_know


def is_user_type(val):
    if not isinstance(val, tuple):
        return val in user_types()

    else:
        for i in val:
            if i not in user_types():
                return False
        return True


def is_computer_type(val):
    if not isinstance(val, tuple):
        return val == "restaurant"

    else:
        for i in val:
            if i != "restaurant":
                return False
        return True


def all_user_type(val):
    assert isinstance(val, list)
    for i in val:
        if not is_user_type(i):
            return False
    return True


# Yield the different concept abstraction levels, each as a different
# disjunction set, where levels are like this:
# 1.    special
#       |
# 2.    soup            salad
#       |       |       |       |
# 3.    lentil  tomato  green   beet
def concept_disjunctions(state, root_concept, ignore_root=False):
    next_level = [root_concept]
    lineage = 0
    while len(next_level) > 0:
        next_next_level = []
        for next_level_type in next_level:
            if not ignore_root or (ignore_root and lineage > 0):
                object = store_to_object(state, next_level_type)
                yield DisjunctionValue(lineage, object)

            for item in immediate_specializations(state, next_level_type):
                next_next_level.append(item)

        next_level = next_next_level
        lineage += 1


def concept_disjunctions_reverse(state, root_concept, ignore_root=False):
    levels = []
    next_level = [root_concept]
    while len(next_level) > 0:
        levels.insert(0, next_level)
        next_next_level = []
        for next_level_type in next_level:
            for item in immediate_specializations(state, next_level_type):
                next_next_level.append(item)

        next_level = next_next_level

    lineage = len(levels)
    for level_index in range(len(levels) if not ignore_root else len(levels) - 1):
        level = levels[level_index]
        lineage -= 1
        for level_type in level:
            object = store_to_object(state, level_type)
            yield DisjunctionValue(lineage, object)


def immediate_specializations(state, base_type):
    yield from rel_subjects(state, "specializes", base_type)


def most_specific_specializations(state, base_type):
    most_specific_lineage = -1
    for item in concept_disjunctions_reverse(state, base_type):
        if most_specific_lineage == -1:
            most_specific_lineage = item.lineage

        if item.lineage == most_specific_lineage:
            yield item.value

        else:
            return


def all_specializations(state, base_type):
    for i in state.all_rel("specializes"):
        if i[1] == base_type:
            yield from all_specializations(state, i[0])
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

    process_list = [thing]
    process_index = 0
    instances = set()

    while process_index < len(process_list):
        to_process = process_list[process_index]
        for subject_object in state.all_rel("specializes"):
            if subject_object[1] == to_process:
                if subject_object[0] not in process_list:
                    process_list += [subject_object[0]]
                    yield subject_object[0]

        for subject_object in state.all_rel("instanceOf"):
            if subject_object[1] == to_process:
                if subject_object[0] not in instances:
                    yield subject_object[0]
                    instances.add(subject_object[0])

        process_index += 1


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


def instance_of_or_entails(context, state, thing, concept):
    if is_concept(thing):
        return concept.entailed_by(context, state, thing)
    else:
        return concept.instances(context, state, potential_instances=[thing])


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
    if not isinstance(who, (list, tuple, set)):
        who = [who]
    for who_item in who:
        found = False
        for location in rel_objects(state, who_item, "at"):
            if sort_of(state, location, where_type):
                found = True
                break
        if not found:
            return False

    return True


def count_of_instances_and_concepts(context, state, variable, concepts_original, fail_if_no_instances):
    concepts = concepts_original
    concept_count = len(concepts)

    instances = []
    for concept in concepts:
        this_concept_instances = list(concept.instances(context, state))
        # If we are dealing with instances and one of the concepts generates zero, we don't want to just count the others
        # and succeed.  I.e. I have two ice creams and bowls should not succeed if there are no bowls
        if fail_if_no_instances and len(this_concept_instances) == 0:
            context.report_error(["noInstancesOfConcept", variable], force=True, phase=2)
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


def object_to_store(o):
    return o.concept_name if is_concept(o) else o


def store_to_object(state, s):
    if not is_instance(state, s):
        return ESLConcept(s)
    else:
        return s


def serial_store_to_object(state, s_list):
    return [store_to_object(state, s) for s in s_list]


def find_unused_instances_from_concept(context, state, concept):
    for instance in concept.instances(context, state):
        someone_has = False
        for item in rel_subjects(state, "have", instance):
            if item != "restaurant":
                someone_has = True
                break
        for item in rel_subjects(state, "ordered", instance):
            if item != "restaurant":
                someone_has = True
                break
        if not someone_has:
            yield instance


def find_unused_item(state, object_type):
    for potential in all_instances(state, object_type):
        someone_has = False
        for item in rel_subjects(state, "have", potential):
            # The restaurant conceptually "has" everything
            if item != "restaurant":
                someone_has = True
                break
        if not someone_has:
            return potential


def has_item_of_type(state, object_type):
    for item in rel_subjects_objects(state, "have"):
        if sort_of(state, item[1], object_type):
            yield item[0]


# Some criteria aren't involved in instance selection, they are involved
# in where the instance ends up.  targetPossession is set by "a menu for me"
# and so it just includes everything
def noop_criteria(state, ignored1, ignored2):
    return True


def rel_subjects_greater_or_equal(state, rel, object):
    for item in state.all_rel(rel):
        if item[1] >= object:
            yield item[0]


def rel_check(state, subject, rel, object):
    return (subject, object) in state.all_rel(rel)


def rel_subjects_objects(state, rel):
    for item in state.all_rel(rel):
        yield item


# Yields all objects that are instanceof of specializes `type`
def rel_sort_of(state, _, type):
    yield from all_instances_and_spec(state, type)


def rel_entailed_by(state, _, type):
    yield from all_instances_and_spec(state, type)


def rel_object_with_rel(state, rel, _):
    for item in state.all_rel(rel):
        yield item[1]


def rel_objects(state, subject, rel):
    for item in state.all_rel(rel):
        if item[0] == subject:
            yield item[1]


def rel_subjects(state, rel, object):
    for item in state.all_rel(rel):
        if item[1] == object:
            yield item[0]


def rel_all_instances(state, _, type):
    return all_instances(state, type)


def rel_all_specializations(state, _, type):
    yield type
    yield from all_specializations(state, type)


def has_type(state, subject, type):
    for item in state.all_rel("have"):
        if item[0] == subject and sort_of(state, item[1], type):
            return True

    return False


class AddRelOp(object):
    def __init__(self, rel):
        self.toAdd = rel

    def __repr__(self):
        return str(self.__class__) + ": " + str(self.toAdd)

    def apply_to(self, state):
        state.mutate_add_rel(self.toAdd[0], self.toAdd[1], self.toAdd[2])


class DeleteRelOp(object):
    def __init__(self, rel):
        self.toDelete = rel

    def __repr__(self):
        return str(self.__class__) + ": " + str(self.toDelete)

    def apply_to(self, state):
        state.mutate_delete_rel(self.toDelete[0], self.toDelete[1], self.toDelete[2])


class AddBillOp(object):
    def __init__(self, item):
        self.toAdd = item

    def __repr__(self):
        return str(self.__class__) + ": " + str(self.toAdd)

    def apply_to(self, state):
        prices = state.sys["prices"]
        assert self.toAdd in prices
        state.mutate_add_bill(prices[self.toAdd])


class SetKnownPriceOp(object):
    def __init__(self, item):
        self.toAdd = item

    def __repr__(self):
        return str(self.__class__) + ": " + str(self.toAdd)

    def apply_to(self, state):
        state.mutate_remove_unknown_price(self.toAdd)


class CancelOrderItemOp(object):
    def __init__(self, person, item):
        self.person = person
        self.item = item

    def apply_to(self, state):
        state.mutate_clear_item_from_order(self.person, self.item)


class ResetOrderAndBillOp(object):
    def apply_to(self, state):
        state.mutate_clear_last_order()


class ResetOrderAndBillForPersonOp(object):
    def __init__(self, person):
        self.person = person

    def __repr__(self):
        return str(self.__class__) + ": " + str(self.person)

    def apply_to(self, state):
        state.mutate_clear_last_order(for_person=self.person)


class ResponseStateOp(object):
    def __init__(self, item):
        self.toAdd = item

    def __repr__(self):
        return str(self.__class__) + ": " + str(self.toAdd)

    def apply_to(self, state):
        state.mutate_set_response_state(self.toAdd)


class ESLConcept(Concept):
    def __init__(self, sort_of=None, mrs_variable=None):
        super().__init__(sort_of)
        self.criteria = []
        self.conjunctions = []
        self._hash = None
        self.mrs_variable = mrs_variable

    def __repr__(self):
        return f"ESLConcept({','.join(self._sort_of_criteria)}: {[x for x in self.criteria]} )"

    # The only required property is that objects which compare equal have the same hash value
    # But: objects with the same hash aren't required to be equal
    # It must remain the same for the lifetime of the object
    def __hash__(self):
        if self._hash is None:
            # TODO: Make this more efficient
            self._hash = hash(tuple(self._sort_of_criteria))

        return self._hash

    def __eq__(self, other):
        if isinstance(other, ESLConcept) and self.__hash__() == other.__hash__():
            if self._sort_of_criteria != other._sort_of_criteria:
                return False

            elif len(self.criteria) != len(other.criteria):
                return False

            else:
                for item in self._sort_of_criteria:
                    if item not in other._sort_of_criteria:
                        return False

                for index in range(len(self.criteria)):
                    if self.criteria[index] not in other.criteria:
                        return False

                return True

    def render_english(self):
        # We have simplistic logic for converting concepts to english
        single_sort_name = self.single_sort_name()
        if single_sort_name is not None:
            return single_sort_name

        else:
            words = []
            for function_arg1_arg2 in self.criteria:
                if function_arg1_arg2[0] == rel_subjects and function_arg1_arg2[1] == "isAdj":
                    words.append(function_arg1_arg2[2])
                else:
                    # Kind of criteria we don't understand ... abort
                    return "something"
            if len(self._sort_of_criteria) == 0:
                words.append("something")
            else:
                words.append(next(iter(self._sort_of_criteria)))

            return " ".join(words)

    # Used to add another concept as a conjunction to this one by simply
    # combining their sort_of_criteria and criteria
    def add_conjunction(self, concept):
        self_copy = self.add_sort_of_criteria_list(concept._sort_of_criteria)
        return self_copy.add_criteria_list(concept.criteria)

    def add_criteria(self, function, arg1, arg2):
        return self.add_criteria_list([(function, arg1, arg2)])

    def add_criteria_list(self, function_arg1_arg2_triples):
        self_copy = copy.deepcopy(self)
        self_copy.criteria += [tuple(x) for x in function_arg1_arg2_triples]
        return self_copy

    def add_sort_of_criteria_list(self, sort_of_criteria_list):
        self_copy = copy.deepcopy(self)
        self_copy._sort_of_criteria.update(sort_of_criteria_list)
        # Needs to update the hash since it is based on sort_of_criteria of the object
        self_copy._hash = None
        return self_copy

    # Pass None to any argument that should be ignored
    def find_criteria(self, function, arg1, arg2):
        for c in self.criteria:
            if function is not None and function != c[0]:
                continue
            if arg1 is not None and arg1 != c[1]:
                continue
            if arg2 is not None and arg2 != c[2]:
                continue
            return c

    # Build a list of criteria that can be executed from the sort_of list
    def sort_to_criteria(self, criteria_function):
        return [(criteria_function, None, sort) for sort in self._sort_of_criteria]

    # return any instances that meet all the criteria in self.criteria
    def instances(self, context, state, potential_instances=None):
        return self._meets_criteria(context, state, self.sort_to_criteria(rel_all_instances) + self.criteria,
                                    initial_instances=potential_instances)

    def has_instance(self, context, state, instance):
        return len(self._meets_criteria(context, state, [instance])) > 0

    # get the actual identifiers of all concepts that meet all the criteria
    def concepts(self, context, state, potential_concepts=None):
        raw_concepts = self._meets_criteria(context, state, self.sort_to_criteria(rel_all_specializations) +
                                            self.criteria, initial_instances=potential_concepts)

        if len(raw_concepts) == 0:
            # Since the concept generated might be different than what the user said,
            # For example, "table for my son" is interpreted as "table for 1", we need
            # to generate an error that is specific to the *concept*
            context.report_error(["conceptNotFound", self.mrs_variable if self.mrs_variable is not None else self.single_sort_name()], force=True)

        # ... and return them wrapped in a Concept() with the same criteria
        return [ESLConcept(x) for x in raw_concepts]

    def mutually_entailed(self, context, state, equivalent_concept):
        return self.entailed_by(context, state, equivalent_concept) and equivalent_concept.entailed_by(context, state, self)

    def entailed_by(self, context, state, smaller_concept):
        return smaller_concept.entails(context, state, self)

    def entailed_by_which(self, context, state, smaller_concept_list):
        entailed_by = []
        for smaller_concept in smaller_concept_list:
            if self.entailed_by(context, state, smaller_concept):
                entailed_by.append(smaller_concept)

        return entailed_by

    # One way of getting all the types in the system that this concept "is"
    # Get all the instances and see what specializations they *all* share
    def entails_which_specializations(self, context, state):
        sort = self.single_sort_name()
        if sort is not None:
            return [sort] + [x for x in all_ancestors(state, sort)]

        else:
            shared_specializations = set()
            for instance in self.instances(context, state):
                specializations = set([x for x in all_ancestors(state, instance)])
                if len(shared_specializations) == 0:
                    shared_specializations = specializations

                else:
                    shared_specializations = shared_specializations & specializations
                    if len(shared_specializations) == 0:
                        return []

                    # Once the intersected set is "thing" it won't ever get bigger than that due to semantics
                    # of set intersection
                    if len(shared_specializations) == 1 and next(iter(shared_specializations)) == "thing":
                        return shared_specializations

            return shared_specializations

    # True if larger_concept entails self, meaning that:
    #   if larger_concept(x) is true then self(x) must be true
    #
    # If a concept A entails a concept B, concept A cannot be true without B being true as well
    # if A is "Concept(small bird)" and B is "Concept(bird)", A entails B since all "small birds" will also be "birds"
    #
    # Another word for entailment is "implication" or "consequence". I.e. the truth of A implies the truth of B
    #
    # If we can't prove it formally, we will approximate (meaning it may be wrong) using a kind of inductive
    # reasoning: determine entailment by seeing if all these instances are also larger_concept instances
    def entails(self, context, state, larger_concept):
        # Special case we can prove formally if:
        # 1. larger concept is really just one criteria: object sortOf concept_name
        # 2. smaller concept specializes concept_name and doesn't use not
        # Then:  smaller concept must imply (i.e. entail) larger concept
        # self specializes larger_concept and there are no "nots" in the criteria
        larger_concept_sort = larger_concept.single_sort_name()
        if larger_concept_sort is not None:
            if larger_concept_sort in self._sort_of_criteria and not self._has_sort_negation():
                return True

        instances, instances_by_concept = self.instances_of_concepts(context, state, [larger_concept])
        return len(instances_by_concept) == 1 and len(instances_by_concept[larger_concept]) == len(instances)

    # Returns a list of concepts which are entailed by this concept
    # using inductive logic.  I.e. if all instances are instances of a concept, then this concept must entail that concept
    def entails_which(self, context, state, larger_concept_list):
        instances, instances_by_concept = self.instances_of_concepts(context, state, larger_concept_list)
        entailed = []
        entailed_set = set()
        not_entailed_set = set()
        instance_count = len(instances)
        for item in instances_by_concept.items():
            if instance_count == len(item[1]):
                # All instances were also instances of this concept
                # therefore (inductively), they are entailed
                entailed.append(item[0])
                entailed_set.add(item[0])
                if item[0] in not_entailed_set:
                    not_entailed_set.remove(entailed)
            else:
                # Not all instances were instances of this concept
                if item[0] not in entailed_set:
                    not_entailed_set.add(item[0])

        # Add in any concepts that didn't even match one instance
        not_entailed_set.update(set(larger_concept_list) - set(instances_by_concept.keys()))

        return not_entailed_set, entailed

    # Checks every instance generated by this concept to see if it is also
    # an instance of any of the concepts in concept_list.
    # Adds any that are into a dictionary keyed by the concept
    def instances_of_concepts(self, context, state, concept_list):
        instances_by_concept = {}
        all_instances = [x for x in self.instances(context, state)]
        for concept in concept_list:
            found_instances = concept.instances(context, state, all_instances)
            if len(found_instances) > 0:
                instances_by_concept[concept] = found_instances

        return all_instances, instances_by_concept

    # There is one special case where we can get a "type name" or "concept name" from a concept
    # without resorting to entailment: when we can prove it is that sort and nothing more or less
    def single_sort_name(self):
        if len(self._sort_of_criteria) == 1 and len(self.criteria) == 0:
            return next(iter(self._sort_of_criteria))

        else:
            return None

    # Things like "is not a food"
    def _has_sort_negation(self):
        # No way to express this yet so easy answer
        return False

    # Each of the criterion is a triple: (function, arg1, arg2)
    # `function` is required to:
    #   - be of the signature: function(state, x, y).  x and y get passed in arg1 and arg2
    #   - yield values that are true of x and y given the criteria it implements
    def _meets_criteria(self, context, state, final_criteria, initial_instances=None):
        found_cumulative = None if initial_instances is None else initial_instances
        for current_criteria in final_criteria:
            found = []

            if current_criteria[0] == noop_criteria:
                found = found_cumulative

            else:
                for result in current_criteria[0](state, current_criteria[1], current_criteria[2]):
                    if found_cumulative is None or result in found_cumulative:
                        found.append(result)

            found_cumulative = found
            if len(found_cumulative) == 0:
                break

        return found_cumulative


def load_world_state(file):
    sys = pickle.load(file)
    rel = pickle.load(file)
    return WorldState(rel, sys)


inherited_relationships = {"isAdj"}


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
        if not self.rel_exists(rel):
            return

        else:
            if rel in inherited_relationships:
                processed = set()
                for subject_object in self._rel[rel]:
                    # If subject is a type yield this relationship on all children
                    # Add each yielded item into a set so we don't do it again
                    # All specializations and all instances of them also have this property
                    for item in all_instances_and_spec(self, subject_object[0]):
                        if item not in processed:
                            yield item, subject_object[1]
                            processed.add(item)

            elif rel == "possess":
                # The "possess" relationship happens with poss(), i.e. "my steak"
                # Note that it is not just "anything I have" since
                # "cancel my steak" refers to a steak I don't have
                yield from self.all_rel("have")
                yield from self.ordered_but_not_delivered()

            else:
                yield from [(x[0], x[1]) for x in self._rel[rel]]

    def rel_exists(self, rel):
        return rel in self._rel.keys() or rel == "possess"

    # ******* Base Operations ********

    # ******* Overrides of State ********
    def __repr__(self):
        if self._world_state_frame is None:
            return super().__repr__()
        else:
            return self._world_state_frame.__repr__()

    def save(self, file):
        pickle.dump(self.sys, file, 5)
        pickle.dump(self._rel, file, 5)

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

    def mutate_clear_item_from_order(self, person, item):
        world_state = self.world_state_frame()
        new_relation = copy.deepcopy(world_state._rel)
        subtract = 0
        new_relation["ordered"].remove((person, item, None))
        order_type = instance_of_what(self, item)
        if order_type in self.sys["prices"]:
            subtract += self.sys["prices"][order_type]
        world_state._rel = new_relation
        self.mutate_add_bill(-subtract)

    def mutate_clear_last_order(self, for_person=None):
        if for_person is not None and not isinstance(for_person, (list, tuple)):
            for_person = (for_person, )
        world_state = self.world_state_frame()
        new_relation = copy.deepcopy(world_state._rel)

        subtract = 0
        for who_item in self.ordered_but_not_delivered():
            if for_person is not None and who_item[0] not in for_person:
                continue

            new_relation["ordered"].remove((who_item[0], who_item[1], None))
            order_type = instance_of_what(self, who_item[1])
            if order_type in self.sys["prices"]:
                subtract += self.sys["prices"][order_type]
        world_state._rel = new_relation
        self.mutate_add_bill(-subtract)

    def mutate_set_response_state(self, new_state):
        world_state = self.world_state_frame()
        world_state.sys["responseState"] = new_state

    # Just get a unique list of all identifiers used as
    # subjects or objects
    def get_entities(self):
        entities = set()
        for i in self._rel.keys():
            for j in self.all_rel(i):
                entities.add(j[0])
                entities.add(j[1])
        return entities

    def get_reprompt(self, return_first=True):
        prefix = " \n" if return_first else ""
        if self.sys["responseState"] == "anticipate_party_size":
            return prefix + "Host: How many in your party?"
        if self.sys["responseState"] == "anticipate_dish":
            if [item for item in self.ordered_but_not_delivered()]:
                return prefix + "Waiter: Can I get you anything else?"
            else:
                return prefix + "Waiter: What can I get you?"
        if self.sys["responseState"] == "way_to_pay":
            return prefix + "Waiter: So, do you want to pay with cash or card?"
        if self.sys["responseState"] in ["initial"]:
            return ""
        assert False, f"Unknown state {self.sys['responseState']}"

    def food_in_order(self, order):
        # First figure out who this order belongs to
        owner_list = [x for x in rel_subjects(self, "have", object_to_store(order))]
        owners = owner_list[0]
        if not isinstance(owners, (tuple, list)):
            owners = (owners, )

        for who_food in self.ordered_food():
            if who_food[0] in owners:
                yield who_food[1]

    def have_food(self):
        for who_item in self.all_rel("have"):
            if is_user_type(who_item[0]) and sort_of(self, who_item[1], ["food"]):
                yield who_item

    def ordered_food(self):
        for who_item in self.all_rel("ordered"):
            if sort_of(self, who_item[1], ["food"]):
                yield who_item

    def ordered_but_not_delivered(self, for_person=None):
        for who_item in self.all_rel("ordered"):
            if who_item[1] in rel_objects(self, who_item[0], "have"):
                # They already got this item
                continue
            else:
                if for_person is None or who_item[0] == for_person:
                    yield who_item

    def only_ordered_not_delivered_water_or_menus(self):
        has_items = False
        for item in self.ordered_but_not_delivered():
            has_items = True
            if not sort_of(self, item[1], ["water", "menu"]):
                return False

        return has_items

    def user_ordered_veg(self):
        veggies = list(all_instances_and_spec(self, "veggie"))
        if self.rel_exists("ordered"):
            for i in self.all_rel("ordered"):
                if i[0] in ["user", "son1"]:
                    if i[1] in veggies:
                        return True
        return False

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

        if total_price + self.bill_total() > 20:
            return [RespondOperation(
                "Son: Wait, we've spent $" + str(self.bill_total()) + " and all that food costs $" + str(
                    total_price) + " so if we get all that, we won't be able to pay for it with $20." + self.get_reprompt())]

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
                    ResponseStateOp("anticipate_dish")]
        for i in wanted_tuple:
            toReturn += [AddRelOp(("user", "ordered", i)), AddBillOp(i)]
        return toReturn

    def user_wants_group(self, context, users, wanted):
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
            return self.handle_world_event(context, ["user_wants", "table1"])
        if allMenus:
            return self.handle_world_event(context, ["user_wants", "menu1"])
        elif allTableRequests:
            return self.handle_world_event(context, ["user_wants", wanted[0].value[0]])
        else:
            unpack = lambda x: x.value[0]
            return self.handle_world_event(context, ["user_wants_multiple", [unpack(j) for j in wanted]])

    def user_wants_to_see(self, wanted):
        if wanted == "menu1":
            return self.user_wants("menu1")
        elif wanted == "table1":
            return [RespondOperation("All our tables are nice. Trust me on this one" + self.get_reprompt())]
        else:
            return [RespondOperation("Sorry, I can't show you that." + self.get_reprompt())]

    def user_wants_to_see_group(self, context, actor_list, wanted_list):
        all_menu = True
        for i in wanted_list:
            if not sort_of(self, i.value[0], "menu"):
                all_menu = False
                break
        if all_menu:
            return self.handle_world_event(context, ["user_wants", "menu1"])
        else:
            return [RespondOperation("Sorry, I can't show you that." + self.get_reprompt())]

    def no(self, context):
        return self.find_plan(context, [('complete_order', context)])

    def yes(self):
        if self.sys["responseState"] in ["anticipate_dish"]:
            return [RespondOperation("Ok, what?"), ResponseStateOp("anticipate_dish")]
        else:
            return [RespondOperation("Host: Hmm. I didn't understand what you said." + self.get_reprompt())]

    # This should always be the answer to a question since it is a partial sentence that generated
    # an unknown() predication in the MRS for the verb
    # x will be a variable value, thus it will be a set of one or more items
    def unknown(self, context, x):
        if self.sys["responseState"] == "way_to_pay":
            if len(x) == 1:
                x = x[0]
                if x in ["cash"]:
                    return [RespondOperation("Ah. Perfect! Have a great rest of your day.")]
                elif x in ["card", "card, credit"]:
                    return [RespondOperation("You reach into your pocket and realize you don’t have a credit card." + self.get_reprompt())]
                else:
                    return [RespondOperation("Waiter: Hmm. I didn't understand what you said." + self.get_reprompt())]

        elif self.sys["responseState"] in ["anticipate_dish", "initial"]:
            return self.handle_world_event(context, ["user_wants", x])

        elif self.sys["responseState"] in ["anticipate_party_size"]:
            if is_user_type(x):
                # The user said something like "me" or "me and my son"
                # since we are asking about party size convert to a count
                x = (len(x), ) if isinstance(x, (tuple, list)) else (1, )

            if len(x) == 1:
                x = x[0]
                if isinstance(x, numbers.Number):
                    table_concept = ESLConcept("table")
                    table_concept = table_concept.add_criteria(rel_subjects_greater_or_equal, "maxCapacity", x)
                    actors = [("user",)]
                    whats = [(table_concept,)]
                    return self.find_plan(context, [('satisfy_want', context, actors, whats, 1)])

        context.report_error(["errorText", "Hmm. I didn't understand what you said." + self.get_reprompt()])

    def find_plan(self, context, tasks):
        current_state = esl.esl_planner.do_task(self.world_state_frame(), tasks)
        if current_state is not None:
            return current_state.get_operations()
        else:
            context.report_error(["errorText", "I'm not sure what to do about that." + self.get_reprompt()])

    def handle_world_event(self, context, args):
        if args[0] == "user_wants":
            return self.find_plan(context, [('satisfy_want', context, [("user",)], [args[1]], 1)])
        elif args[0] == "user_wants_to_see":
            return self.user_wants_to_see(args[1])
        elif args[0] == "user_wants_multiple":
            return self.user_wants_multiple(args[1])
        elif args[0] == "no":
            return self.no(context)
        elif args[0] == "yes":
            return self.yes()
        elif args[0] == "greeting":
            return [RespondOperation("Hello!")]
        elif args[0] == "unknown":
            # User said something that wasn't a full sentence that generated an
            # unknown() predication
            return self.unknown(context, args[1])
        elif args[0] == "user_wants_to_sit":
            return self.user_wants("table1")
        elif args[0] == "user_wants_to_sit_group":
            return self.user_wants("table1")
        elif args[0] == "user_wants_group":
            who_list = [binding.value for binding in args[1].solution_values]
            what_list = [binding.value for binding in args[2].solution_values]
            return self.find_plan(context, [('satisfy_want', context, who_list, what_list)])
        elif args[0] == "user_wants_to_see_group":
            return self.user_wants_to_see_group(context, args[1], args[2])


pipeline_logger = logging.getLogger('Pipeline')
