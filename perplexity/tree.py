import copy
import logging
from collections import defaultdict
from perplexity.execution import execution_context


class TreePredication(object):
    def __init__(self, index, name, args, arg_names=None):
        self.index = index
        self.name = name
        self.args = args
        self.arg_names = arg_names

        if arg_names is not None:
            self.arg_types = []
            for arg_index in range(0, len(self.arg_names)):
                self.arg_types.append(self.type_from_argument(self.arg_names[arg_index], self.args[arg_index]))

    def type_from_argument(self, name, value):
        if name == "CARG":
            return "c"
        else:
            if isinstance(value, str):
                return value[0]
            else:
                return "h"

    def introduced_variable(self):
        if self.arg_names[0] == "CARG":
            return self.args[1]
        else:
            return self.args[0]

    def argument_types(self):
        return self.arg_types

    def append_arg(self, name, value):
        self.arg_names.append(name)
        self.args.append(value)
        self.arg_types.append(self.type_from_argument(name, value))

    def x_args(self):
        x_args = []
        for arg_index in range(0, len(self.args)):
            if self.arg_types[arg_index] == "x":
                x_args.append(self.args[arg_index])

        return x_args

    def __repr__(self):
        return f"{self.name}({','.join([str(arg) for arg in self.args])})"


def tree_from_assignments(hole_label, assignments, predication_dict, mrs, current_index=None):
    if current_index is None:
        current_index = [0]

    # Get the list of predications that should fill in the hole
    # represented by labelName
    if hole_label in assignments.keys():
        predication_list = predication_dict[assignments[hole_label]]
    else:
        predication_list = predication_dict[hole_label]

    # predication_list is a list because multiple items might
    # have the same key and should be put in conjunction (i.e. be and'd together)
    conjunction_list = []
    for predication in predication_list:
        tree_node = TreePredication(current_index[0], predication.predicate, [], [])
        current_index[0] += 1

        # Recurse through this predication's arguments
        # and look for any scopal arguments to recursively convert
        for arg_name in predication.args.keys():
            original_value = predication.args[arg_name]

            # CARG arguments contain strings that are never
            # variables, they are constants
            if arg_name in ["CARG"]:
                new_value = original_value
            else:
                argType = original_value[0]
                if argType == "h":
                    new_value = tree_from_assignments(original_value, assignments, predication_dict, mrs, current_index)
                else:
                    new_value = original_value

            tree_node.append_arg(arg_name, new_value)

        conjunction_list.append(tree_node)

    if len(conjunction_list) == 1:
        return conjunction_list[0]
    else:
        # Since these are "and" they can be in any order
        # Sort them into an order which ensures event variable
        #   usage comes before introduction (i.e. ARG0)
        return sort_conjunctions(conjunction_list)


# Make sure a list of predications (like for a conjunction/"logical and")
#   is sorted such that predications that *modify* e variables
#   come before the *introducer* of them
# and that predications that *modify* x variables
#   come *after* the introducer of them
def sort_conjunctions(predication_list):
    # Build a dict with keys of introduced e args and values of the
    #   index of the predication that introduced them
    introduced_dict = {}
    for predication_index in range(0, len(predication_list)):
        introduced_arg = predication_list[predication_index].introduced_variable()
        if introduced_arg[0] in ["e", "x"]:
            introduced_dict[introduced_arg] = predication_index

    # Build the graph that represents the dependencies
    topological_sort = Cormen2001(len(predication_list))
    for predication_index in range(0, len(predication_list)):
        for arg_value in predication_list[predication_index].args:
            if isinstance(arg_value, str) and arg_value in introduced_dict:
                if predication_index != introduced_dict[arg_value]:
                    # This argument uses the ARG0 event of another predication in the list
                    if arg_value[0] == "x":
                        topological_sort.add_edge(introduced_dict[arg_value], predication_index)
                    else:
                        topological_sort.add_edge(predication_index, introduced_dict[arg_value])

    # Do the topological sort and return them
    topological_sort.topological_sort()
    assert not topological_sort.has_cycle, f"cyclic dependencies in predications {predication_list}"

    sorted_predications = []
    for predication_index in topological_sort.sorted_nodes:
        sorted_predications.append(predication_list[predication_index])

    return sorted_predications


# We have a tree where a node has children that represent what it depends on
# If we topologically sort the DAG it will give us the ordering that represents
# the dependent predications first
#
# From Wikipedia for the Cormen et al. (2001) topological sort algorithm:
#
# L ← Empty list that will contain the sorted nodes
# while exists nodes without a permanent mark do
#     select an unmarked node n
#     visit(n)
#
# function visit(node n)
#     if n has a permanent mark then
#         return
#     if n has a temporary mark then
#         stop   (graph has at least one cycle)
#
#     mark n with a temporary mark
#
#     for each node m with an edge from n to m do
#         visit(m)
#
#     remove temporary mark from n
#     mark n with a permanent mark
#     add n to head of L
class Cormen2001(object):
    def __init__(self, node_count):
        # Each node is represented by an index
        # graph[index] returns a list of the nodes that
        # have an edge from index to them
        self.node_count = node_count
        self.graph = defaultdict(list)
        self.visited = [False] * self.node_count
        self.temporary_mark = [False] * self.node_count
        self.sorted_nodes = []
        self.has_cycle = False

    def add_edge(self, from_node, to_node):
        self.graph[from_node].append(to_node)

    def topological_sort(self):
        while True:
            unvisited_index = None
            for index in range(0, self.node_count):
                if not self.visited[index]:
                    unvisited_index = index
                    break

            if unvisited_index is None:
                break
            else:
                if not self.visit(unvisited_index):
                    # graph has at least one cycle
                    break

    # Returns False if there is a cycle, otherwise True
    def visit(self, node_index):
        if self.visited[node_index]:
            return True

        if self.temporary_mark[node_index]:
            # graph has at least one cycle
            self.has_cycle = True
            return False

        self.temporary_mark[node_index] = True
        for edge_to_node_index in self.graph[node_index]:
            if not self.visit(edge_to_node_index):
                return False

        self.temporary_mark[node_index] = False
        self.visited[node_index] = True
        self.sorted_nodes.insert(0, node_index)
        return True


# WalkTreeUntil() is a helper function that just walks
# the tree represented by "term". For every predication found,
# it calls func(found_predication)
# If func returns anything besides "None", it quits and
# returns that value
def walk_tree_predications_until(term, func):
    if isinstance(term, list):
        # This is a conjunction, recurse through the
        # items in it
        for item in term:
            result = walk_tree_predications_until(item, func)
            if result is not None:
                return result

    else:
        # This is a single term, call func with it
        result = func(term)
        if result is not None:
            return result

        # If func didn't say to quit, see if any of its terms are scopal
        # i.e. are predications themselves
        for arg in term.args:
            if not isinstance(arg, str):
                result = walk_tree_predications_until(arg, func)
                if result is not None:
                    return result

    return None


# Calls predication_func(predication) for every predication encountered
# Calls arg_func(predication, arg) with the raw value of every scopal argument
# If either returns anything besides None, stops recursing and returns that value
def walk_tree_args_until(term, predication_func, arg_func):
    if isinstance(term, list):
        # This is a conjunction, recurse through the
        # items in it
        for item in term:
            result = walk_tree_args_until(item, predication_func, arg_func)
            if result is not None:
                return result

    else:
        # This is a single term, call func with it
        result = predication_func(term)
        if result is not None:
            return result

        # If func didn't say to quit, see if any of its terms are scopal
        # i.e. are predications themselves
        for arg in term.args:
            if not isinstance(arg, str):
                result = arg_func(term, arg)
                if result is not None:
                    return result

                result = walk_tree_args_until(arg, predication_func, arg_func)
                if result is not None:
                    return result

    return None


# True if an `fw_seq` predication is used by something *besides* an `fw_seq` predication
# because that means it is the final one
def is_this_last_fw_seq(state):
    this_tree = state.get_binding("tree").value[0]
    this_predication = predication_from_index(this_tree, execution_context().current_predication_index())
    return is_last_fw_seq(this_tree["Tree"], this_predication)


def is_index_predication(state):
    this_tree = state.get_binding("tree").value[0]
    this_predication = predication_from_index(this_tree, execution_context().current_predication_index())
    return this_predication.introduced_variable() == this_tree["Index"]


def is_last_fw_seq(tree, fw_seq_predication):
    consuming_predications = find_predications_using_variable(tree, fw_seq_predication.args[0])
    return len([predication for predication in consuming_predications if predication.name != "fw_seq"]) > 0


def find_predications_using_variable(term, variable):
    def match_predication_using_variable(predication):
        for arg_index in range(1, len(predication.arg_types)):
            if predication.arg_types[arg_index] not in ["c", "h"]:
                if predication.args[arg_index] == variable:
                    predication_list.append(predication)

    predication_list = []
    walk_tree_predications_until(term, match_predication_using_variable)

    return predication_list


def find_predications_using_variable_ARG1(term, variable):
    def match_predication_using_variable(predication):
        if len(predication.arg_types) > 1:
            if predication.arg_types[1] not in ["c", "h"]:
                if predication.args[1] == variable:
                    predication_list.append(predication)

    predication_list = []
    walk_tree_predications_until(term, match_predication_using_variable)

    return predication_list


# Return all of the predications in the list that have a name in the list
def find_predications_in_list_in_list(term, predication_name_list):
    if isinstance(term, list):
        term_list = term
    else:
        term_list = [term]

    found_predications = []
    for predication in term_list:
        if predication.name in predication_name_list:
            found_predications.append(predication)

    return found_predications


def find_predication_from_introduced(term, introduced_variable):
    def match_introduced_variable(predication):
        if predication.introduced_variable() == introduced_variable:
            return predication
        else:
            return None

    return walk_tree_predications_until(term, match_introduced_variable)


# Walk the tree represented by "term" and
# return the predication that matches
# "predicate_name" or "None" if none is found
def find_predication(term, predication_name):
    # This function gets called for every predication
    # in the tree. It is a private function since it is
    # only used here
    def match_predication_name(predication):
        if predication.name == predication_name:
            return predication
        else:
            return None

    # Pass our private function to WalkTreeUntil as
    # a way to filter through the tree to find
    # predication_name
    return walk_tree_predications_until(term, match_predication_name)


# Return all of the predications named predication_name
def find_predications(term, predication_name):
    # This function gets called for every predication
    # in the tree. It is a private function since it is
    # only used here
    def match_predication_name(predication):
        if predication.name == predication_name:
            found_predications.append(predication)

    found_predications = []

    # Pass our private function to WalkTreeUntil as
    # a way to filter through the tree to find
    # predication_name
    walk_tree_predications_until(term, match_predication_name)
    return found_predications


def find_predications_with_arg_types(term, predication_name, arg_filter):
    # This function gets called for every predication
    # in the tree. It is a private function since it is
    # only used here
    def match_predication_name(predication):
        if predication_name == "_" or predication.name.find(predication_name) != -1:
            if len(arg_filter) == len(predication.arg_types):
                for index in range(0, len(arg_filter)):
                    if arg_filter[index] != "_" and arg_filter[index] != predication.arg_types[index]:
                        return

                found_predications.append(predication)

    found_predications = []

    # Pass our private function to WalkTreeUntil as
    # a way to filter through the tree to find
    # predication_name
    walk_tree_predications_until(term, match_predication_name)
    return found_predications


# Return the predication at a particular index
def predication_from_index(tree_info, index):
    def stop_at_index(predication):
        nonlocal index_predication

        # Once we have hit the index where the failure happened, stop
        if predication.index == index:
            index_predication = predication
            return False

    index_predication = None

    # WalkTreeUntil() walks the predications in mrs["Tree"] and calls
    # the function record_predications_until_failure_index(), until hits the
    # failure_index position
    walk_tree_predications_until(tree_info["Tree"], stop_at_index)

    return index_predication


# Walk every predication in the tree and allow predication_rewrite_func() to rewrite it
# Then recurse over the rewritten predication
def rewrite_tree_predications(term, predication_rewrite_func, index_by_ref):
    if isinstance(term, list):
        # This is a conjunction, recurse through the
        # predications in it
        new_term = []
        for predication in term:
            new_term.append(rewrite_tree_predications(predication, predication_rewrite_func, index_by_ref))

        return new_term

    else:
        # This is a predication, rewrite it
        new_term = predication_rewrite_func(term, index_by_ref)
        if new_term is None:
            # no rewrite, copy and keep the term, but use the new index_by_ref
            predication_copy = copy.deepcopy(term)
            predication_copy.index = index_by_ref[0]
            index_by_ref[0] += 1

            # See if any of its terms are scopal
            # i.e. are predications themselves
            for scopal_index in predication_copy.scopal_arg_indices():
                predication_copy.args[scopal_index] = rewrite_tree_predications(predication_copy.args[scopal_index], predication_rewrite_func, index_by_ref)

            return predication_copy

        else:
            # New term has been rewritten the rewriter needs to have handled all
            # of its args recursively, so we are done
            return new_term


# Return all of the predications that take the introduced variable
# from primary_predication, and consume it
def split_predications_consuming_event(term, target_event):
    def find(predication):
        introduced_index = predication.introduced_variable_index()
        for arg_index in range(0, len(predication.arg_types)):
            if predication.arg_types[arg_index] not in ["c", "h"]:
                if predication.args[arg_index] == target_event:
                    if arg_index != introduced_index:
                        found_predications.append(predication)
                    return

        remaining_predications.append(predication)

    found_predications = []
    remaining_predications = []

    walk_tree_predications_until(term, find)
    return found_predications, remaining_predications


pipeline_logger = logging.getLogger('Pipeline')
