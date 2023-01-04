from collections import defaultdict


def tree_from_assignments(labelName, assignments, predication_dict, mrs):
    if labelName in assignments.keys():
        predication_list = predication_dict[assignments[labelName]]
    else:
        predication_list = predication_dict[labelName]

    # predication_dict has a list for every key because multiple items might
    # have the same key and should be put in conjunction (i.e. and'd together)
    conjunction_list = []
    for predication in predication_list:
        tree_node = [predication.predicate]

        # Recurse through this predication's arguments
        for arg_name in predication.args.keys():
            original_value = predication.args[arg_name]

            # Certain Arguments names only ever contain a type that is not a scope
            # skip those
            if arg_name in ["CARG"]:
                arg_value = original_value
            else:
                argType = original_value[0]
                if argType == "h":
                    arg_value = tree_from_assignments(original_value, assignments, predication_dict, mrs)
                else:
                    arg_value = original_value

            tree_node.append(arg_value)

        conjunction_list.append(tree_node)

    # Since these are "and" they can be in any order
    # Sort them into an order which ensures event variable
    #   usage comes before introduction (i.e. ARG0)
    return sort_conjunctions(conjunction_list)


# Make sure a list of predications (like for a conjunction/"logical and")
#   is sorted such that predications that *modify* e variables
#   come before the *introducer* of them
def sort_conjunctions(predication_list):
    # Build a dict with keys of introduced e args and values of the
    #   index of the predication that introduced them
    introduced_dict = {}
    for predication_index in range(0, len(predication_list)):
        introduced_arg = predication_list[predication_index][1]
        if introduced_arg[0] == "e":
            introduced_dict[introduced_arg] = predication_index

    # Build the graph that represents the dependencies
    topological_sort = Cormen2001(len(predication_list))
    for predication_index in range(0, len(predication_list)):
        for arg_value in predication_list[predication_index][1:]:
            if isinstance(arg_value, str) and arg_value in introduced_dict:
                if predication_index != introduced_dict[arg_value]:
                    # This argument uses the ARG0 event of another predication in the list
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
def walk_tree_until(term, func):
    if isinstance(term[0], list):
        # This is a conjunction, recurse through the
        # items in it
        for item in term:
            result = walk_tree_until(item, func)
            if result is not None:
                return result

    else:
        # This is a single term, call func with it
        result = func(term)
        if result is not None:
            return result

        # If func didn't say to quit, see if any of its terms are scopal
        # i.e. are predications themselves
        for arg in term[1:]:
            if not isinstance(arg, str):
                result = walk_tree_until(arg, func)
                if result is not None:
                    return result

    return None


# Walk the tree represented by "term" and
# return the predication that matches
# "predicate_name" or "None" if none is found
def find_predicate(term, predication_name):
    # This function gets called for every predication
    # in the tree. It is a private function since it is
    # only used here
    def match_predication_name(predication):
        if predication[0] == predication_name:
            return predication
        else:
            return None

    # Pass our private function to WalkTreeUntil as
    # a way to filter through the tree to find
    # predication_name
    return walk_tree_until(term, match_predication_name)