import contextvars
import copy
import logging
import os
import platform
import sys
from collections import defaultdict
from delphin import ace
from delphin.codecs.simplemrs import encode
from delphin.lnk import LnkMixin
from delphin.predicate import split

from perplexity.erg import erg_file
from perplexity.tree_algorithm_zinda2020 import valid_hole_assignments
from perplexity.utilities import parse_predication_name, sentence_force, get_function
import perplexity.vocabulary


# Returns predication_handlers, global_handlers
# with just an array of functions in each
def find_solution_group_handlers_with_name(vocabulary, this_sentence_force, tree_info, name):
    handlers = []
    index_predication = perplexity.tree.find_index_predication(tree_info)
    if index_predication is None:
        # The index was not in the tree, which means we are executing a subtree and this
        # means the handlers would not have been run since the index predication is outside the tree
        return handlers, None

    for module_function in vocabulary.predications(name + "_" + index_predication.name, index_predication.argument_types(), this_sentence_force):
        handlers.append([True, get_function(module_function), module_function])

    for module_function in vocabulary.predications(name, [], this_sentence_force):
        handlers.append([False, get_function(module_function), module_function])

    return handlers, index_predication


class MrsParser(object):
    def __init__(self, max_holes=14, max_parses=None, log_file=None, generate_root=None):
        self.max_holes = max_holes
        self.max_parses = max_parses
        self.log_file = log_file
        self.generate_root = generate_root

    def mrss_from_phrase(self, phrase, synonyms=None, trace=False, one_time_max_parses=None):
        if synonyms is None:
            synonyms = dict()

        # Don't print errors to the screen
        if trace:
            f = self.log_file if self.log_file is not None else sys.stderr
        else:
            f = open(os.devnull, 'w')

        # Create an instance of the ACE parser and ask to give <= 100 MRS documents
        current_max_parses = one_time_max_parses if one_time_max_parses is not None else self.max_parses
        cmd_args = [] if current_max_parses is None else ['-n', str(current_max_parses)]
        with ace.ACEParser(erg_file(), cmdargs=cmd_args, stderr=f) as parser:
            ace_response = parser.interact(phrase)
            if current_max_parses is None or current_max_parses > len(ace_response['results']):
                pipeline_logger.debug(f"{len(ace_response['results'])} parse options for {phrase}")
            else:
                pipeline_logger.debug(f"{len(ace_response['results'])} parses (there may be more but that's the max) for {phrase}")

        for parse_index in range(0, len(ace_response.results())):
            # Keep track of the original phrase on the object
            mrs = ace_response.result(parse_index).mrs()
            mrs.surface = phrase
            mrs_list = []
            for ep in mrs.predications:
                ep.predicate = synonyms.get(ep.predicate, ep.predicate)
                arg_types = []
                for arg_item in ep.args.items():
                    arg_types.append(arg_item[1])
                mrs_list.append(f"{ep.predicate}({','.join(arg_types)})")
            pipeline_logger.debug(f"Parse {parse_index}: {', '.join(mrs_list)}")
            yield mrs

    def phrase_from_simple_mrs(self, simple, trace=False):
        if trace:
            f = self.log_file if self.log_file is not None else sys.stderr
        else:
            f = open(os.devnull, 'w')

        cmd_args = [] if self.max_parses is None else ['-n', str(self.max_parses)]
        if self.generate_root is not None:
            cmd_args += ['-r', self.generate_root]
        with ace.ACEGenerator(erg_file(), cmdargs=cmd_args, stderr=f) as generator:
            response = generator.interact(simple)
            surfaceStrings = []
            for index in range(0, len(response.results())):
                yield response.result(index)['surface']

    def mrs_to_string(self, mrs):
        return encode(mrs)

    def unscoped_tree(self, mrs):
        conjunction_list = []
        current_index = 0
        for predication in mrs.predications:
            if split(predication.predicate)[1] == "q":
                if predication.predicate not in ["udef", "pronoun_q", "proper_q", "_which_q", "which_q", "generic_q"]:
                    return False
                else:
                    continue
            else:
                # If a predication takes a scopal argument it might need to get inserted into any place
                # in the tree (i.e. neg()) so we need to return the different trees
                for arg_name in predication.args.keys():
                    original_value = predication.args[arg_name]

                    # CARG arguments contain strings that are never
                    # variables, they are constants
                    if arg_name not in ["CARG"]:
                        argType = original_value[0]
                        if argType == "h":
                            return False

        return True

    def trees_from_mrs(self, mrs):
        # If the tree doesn't have any true scopes, then only return
        # one tree since they will all be the same
        unscoped = self.unscoped_tree(mrs)

        required_root_label = None
        for predication in mrs.predications:
            # which_q should always have widest scope for questions
            # See: https://delphinqa.ling.washington.edu/t/understanding-neg-e-h-which-rocks-are-not-blue/860
            if predication.predicate in ["which_q", "_which_q"] and sentence_force(mrs.variables) in ["prop-or-ques", "ques"]:
                required_root_label = predication.label
                break

        # Iteratively return well-formed trees from the MRS
        for new_mrs, holes_assignments in valid_hole_assignments(mrs, self.max_holes, required_root_label):
            # valid_hole_assignments can return None if the grammar returns something
            # that doesn't have the same number of holes and floaters (which is a grammar bug)
            if holes_assignments is not None:
                # Create a dict of predications using their labels as each key
                # for easy access when building trees
                # Note that a single label could represent multiple predications
                # in conjunction so we need a list for each label
                mrs_predication_dict = {}
                for predication in new_mrs.predications:
                    if predication.label not in mrs_predication_dict.keys():
                        mrs_predication_dict[predication.label] = []
                    mrs_predication_dict[predication.label].append(predication)

                # Now we have the assignments of labels to holes, but we need
                # to actually build the *tree* using that information
                well_formed_tree = tree_from_assignments(new_mrs.top,
                                                         holes_assignments,
                                                         mrs_predication_dict,
                                                         new_mrs)
                pipeline_logger.debug(f"Tree: {well_formed_tree}")
                yield well_formed_tree
                if unscoped:
                    return


_tree_predication_context = contextvars.ContextVar('TreePredication', default=False)


def surface_word_from_mrs_predication(mrs, predication):
    wordLnk = LnkMixin(predication.lnk)
    if wordLnk.cfrom != -1:
        return mrs.surface[wordLnk.cfrom: wordLnk.cto]
    else:
        return "unknown"


class TreePredication(object):
    def __init__(self, index, name, args, arg_names=None, mrs_predication=None):
        self.index = index
        self.name = name
        self.args = args
        self.arg_names = arg_names
        if mrs_predication is not None:
            # Make a copy in case this gets changed later so it doesn't
            # mess up the original
            self.mrs_predication = copy.deepcopy(mrs_predication)

        if arg_names is not None:
            self.arg_types = []
            for arg_index in range(0, len(self.arg_names)):
                self.arg_types.append(self.type_from_argument(self.arg_names[arg_index], self.args[arg_index]))

    @staticmethod
    def from_ep(ep):
        return TreePredication(index=0,
                               name=ep.predicate,
                               args=list(ep.args.values()),
                               arg_names=list(ep.args.keys()),
                               mrs_predication=ep)

    def __eq__(self, other):
        if isinstance(other, TreePredication):
            if self.name == other.name:
                if len(self.args) == len(other.args):
                    for arg_index in range(len(self.args)):
                        if self.arg_types[arg_index] == other.arg_types[arg_index] and self.args[arg_index] == other.args[arg_index]:
                            continue
                        else:
                            return False

                    if self.index == other.index:
                        return True

        return False

    def type_from_argument(self, name, value):
        if name == "CARG":
            return "c"
        else:
            if isinstance(value, str):
                return value[0]
            else:
                return "h"

    def introduced_variable_index(self):
        if self.arg_names[0] == "CARG":
            return 1
        else:
            return 0

    def introduced_variable(self):
        return self.args[self.introduced_variable_index()]

    def argument_types(self):
        return self.arg_types

    def append_arg(self, name, value):
        self.arg_names.append(name)
        self.args.append(value)
        self.arg_types.append(self.type_from_argument(name, value))

    def x_args(self):
        return self.args_with_types(["x"])

    def scopal_args(self):
        return self.args_with_types(["h"])

    def args_with_types(self, types):
        found_args = []
        for arg_index in range(0, len(self.args)):
            if self.arg_types[arg_index] in types:
                found_args.append(self.args[arg_index])

        return found_args

    def scopal_arg_indices(self):
        for arg_index in range(0, len(self.args)):
            if self.arg_types[arg_index] == "h":
                yield arg_index

    def __repr__(self):
        global _tree_predication_context
        print_indices = _tree_predication_context.get()
        return f"{self.name}{(':' + str(self.index)) if print_indices else ''}({','.join([str(arg) for arg in self.args])})"

    # Uses a contextvar so that the indices are optionally printed out on __repr__
    def repr_with_indices(self):
        global _tree_predication_context
        try:
            old_context = _tree_predication_context.set(True)
            return f"{self.name}:{self.index}({','.join([str(arg) for arg in self.args])})"
        finally:
            _tree_predication_context.reset(old_context)


def index_and_is_index_scoped_by_negation(tree_info):
    index_predication = find_index_predication(tree_info)
    return index_predication, is_introduced_variable_scoped_by_negation(tree_info["Tree"], index_predication.introduced_variable())


def is_variable_scoped_by_predications_in_binding(solution, predication_list_binding_name, variable_name):
    negated_predications_binding = solution.get_binding(predication_list_binding_name)
    negated_index = None
    if negated_predications_binding.value is not None:
        # There are negated predications in this tree,
        # see if this variable is scoped by one of them
        for negated_predication_item in negated_predications_binding.value.items():
            if variable_name in negated_predication_item[1].scoped_variables:
                negated_index = negated_predication_item[0]
                break

    return negated_index is not None


def is_variable_scoped_by_negation(solution, variable_name):
    return is_variable_scoped_by_predications_in_binding(solution, "negated_predications", variable_name)


def ignore_global_constraints_on_variable(solution, variable_name):
    return is_variable_scoped_by_predications_in_binding(solution, "negated_predications", variable_name) or \
        is_variable_scoped_by_predications_in_binding(solution, "ignore_constraints_scoped_by", variable_name)


def is_introduced_variable_scoped_by_negation(solution, variable_name):
    if solution.get_binding("tree").value[0].get("NegatedSubtree", False):
        return True

    negated_predications_binding = solution.get_binding("negated_predications")
    if negated_predications_binding.value is not None:
        for negation_scope in negated_predications_binding.value.values():
            # See if variable_name is introduced in this scope
            if find_predication_from_introduced(negation_scope.predication, variable_name):
                return True

    return False


# Phrases like "Hi, I'd love to have a table for 2, please" have more than one syntactic head
# i.e. greet() and have_v_1() heads joined by discourse(i, h, h)
# This function pulls out the characteristic variable for each
# - Start with a scope-resolved MRS
# - Initially "follow" the predication that introduces the variable that is the MRS index
# - To "follow" a given predication:
#     - If there are no scopal arguments, we have found a syntactic head
#     - Otherwise, if it is a special case predication (like 'nominalization_rel') follow its scopal arguments per whatever the special case is
#     - Otherwise, for each scopal argument from ARG1 to ARGN:
#         - If the ARG has a QEQ, use it to get the next predication (which might skip to somewhere deep in the tree) and follow that
#         - If not, just follow the predication the ARG points to
# - Note that this algorithm could return more than one syntactic head.  For example "I want steak and I want soup" will generate two: one for each want_v_1
def syntactic_heads_characteristic_variables(mrs):
    # Start with the characteristic variable indicated by INDEX
    variable = mrs.index
    handle = None
    for item in mrs.rels:
        if item.id == variable:
            handle = item.label
            break

    if handle is None:
        assert False, f"variable {variable} was not a characteristic variable: this case shouldn't exist"

    yield from search_syntactic_head(handle, mrs)


def search_syntactic_head(handle, mrs):
    # Find the EP for this handle by searching
    # for the EP that has this handle as its label
    # Note that there might be multiple in conjunction
    eps = []
    for item in mrs.rels:
        if item.label == handle:
            eps.append(item)

    if len(eps) == 0:
        # Must be a hole, and thus has a QEQ
        for item in mrs.hcons:
            if item.hi == handle:
                # Found the QEQ constraint, now find the predication
                # that maps to the lo part
                for ep_candidate in mrs.rels:
                    if ep_candidate.label == item.lo:
                        eps.append(ep_candidate)

                if eps:
                    break

    ep = None
    if len(eps) == 0:
        assert False, f"variable {handle} was not a characteristic variable and was not a handle: this case shouldn't exist"

    elif len(eps) == 1:
        ep = eps[0]

    else:
        # There are multiple EPs in conjunction.
        # “that will be all, thank you.” and “nails are rusty and red” generate shared labels that have some form of implicit_conj or _and_conj
        # which both reference other event variables
        for test_ep in eps:
            if test_ep.predicate in ["implicit_conj", "_and_c"]:
                ep = test_ep
                break

        if ep is None:
            # Otherwise Choose the one that doesn't reference the introduced variable of any others
            final_eps = []
            for test_ep in eps:
                doesnt_reference_any = True
                for other_ep in eps:
                    if test_ep == other_ep:
                        continue

                    if other_ep.id in test_ep.args.values():
                        doesnt_reference_any = False
                        break

                if doesnt_reference_any:
                    final_eps.append(test_ep)

            if ep is None and len(final_eps) > 1:
                # unknown words like "leving" as a full phrase, can generate multiple EPs in conjunction that don't reference
                # each other like unknown(e2,i4), _leving/vbg_u_unknown(e5,i4,i6)
                # special case this and choose unknown
                # "show me 2 menus" puts appos(e6,x5,x7), _show_v_1(e2,i3,x4,x5) in the same label. In this case, chose the one marked as a verb
                for item in final_eps:
                    if item.predicate in ["unknown"] or parse_predication_name(item.predicate)["Pos"] == "v":
                        ep = item
                        break

                # Case 2: "1 file is in a folder together" generates a parse with "_together_p(e17,x3), _in_p_loc(e2,x3,x11)" where it
                # is unclear which to pick, choose the last one
                ep = final_eps[-1]

            if len(final_eps) == 1:
                ep = final_eps[0]

        assert ep is not None, f"Couldn't find an EP that didn't reference others: {eps}"

    # Recurse on any arguments that are handles
    is_scopal = False
    for arg in ep.args.items():
        if arg[0] != "CARG" and arg[1][0] == "h":
            is_scopal = True
            # found a scopal arg
            yield from search_syntactic_head(arg[1], mrs)

    # If there are no scopal arguments, we have found a syntactic head
    if not is_scopal:
        yield ep.id


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
        tree_node = TreePredication(current_index[0], predication.predicate, [], [], predication)
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


# yield all the variables that are consumed in the arg_value
# arg_value can be a predication, conjunction or tree
def consumed_variables(arg_value):
    if isinstance(arg_value, str):
        yield arg_value
    elif isinstance(arg_value, list):
        for item in arg_value:
            yield from consumed_variables(item)
    elif isinstance(arg_value, TreePredication):
        for item in arg_value.args:
            yield from consumed_variables(item)
    else:
        assert False


# Make sure a list of predications (like for a conjunction/"logical and")
#   is sorted such that predications that *modify* e variables
#   come before the *introducer* of them
# and that predications that *modify* x variables
#   come *after* the introducer of them
def sort_conjunctions(predication_list):
    # Build a dict with keys of introduced e and x args and values of the
    #   index of the predication that introduced them
    introduced_dict = {}
    for predication_index in range(0, len(predication_list)):
        introduced_arg = predication_list[predication_index].introduced_variable()
        if introduced_arg[0] in ["e", "x"]:
            introduced_dict[introduced_arg] = predication_index

    # Build the graph that represents the dependencies
    topological_sort = Cormen2001(len(predication_list))
    for predication_index in range(0, len(predication_list)):
        for consumed_variable in consumed_variables(predication_list[predication_index]):
            if consumed_variable in introduced_dict:
                if predication_index != introduced_dict[consumed_variable]:
                    # This argument uses the ARG0 event of another predication in the list
                    if consumed_variable[0] == "x":
                        topological_sort.add_edge(introduced_dict[consumed_variable], predication_index)
                    else:
                        topological_sort.add_edge(predication_index, introduced_dict[consumed_variable])

    # Do the topological sort and return them
    topological_sort.topological_sort()
    assert not topological_sort.has_cycle, f"cyclic dependencies in predications {predication_list}"

    # Get the original index of each predication and reassign those
    # given the new order
    predication_indices = [pred.index for pred in predication_list]
    predication_indices.sort()

    sorted_predications = []
    for predication_index in topological_sort.sorted_nodes:
        new_predication = predication_list[predication_index]
        new_predication.index = predication_indices[len(sorted_predications)]
        sorted_predications.append(new_predication)

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
        # This is a single term, call func with it if it is a predication
        if isinstance(term, TreePredication):
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


# True if a "joining" predication like `fw_seq` or `and_c` predication is used by something *besides* another joining predication
# because that means it is the final one
def is_this_last_joining_predication(context, state, joining_synonyms):
    this_tree = state.get_binding("tree").value[0]
    this_predication = predication_from_index(this_tree, context.current_predication_index())
    return is_last_joining_predication(this_tree["Tree"], this_predication, joining_synonyms)


def is_last_joining_predication(tree, joining_predication, joining_synonyms):
    consuming_predications = find_predications_using_variable(tree, joining_predication.args[0])
    return len([predication for predication in consuming_predications if predication.name not in joining_synonyms]) > 0


# True if an `fw_seq` predication is used by something *besides* an `fw_seq` predication
# because that means it is the final one
def is_this_last_fw_seq(context, state):
    return is_this_last_joining_predication(context, state, ["fw_seq"])


def is_last_fw_seq(tree, fw_seq_predication):
    return is_last_joining_predication(tree, fw_seq_predication, ["fw_seq"])


# As per this thread: https://delphinqa.ling.washington.edu/t/converting-mrs-output-to-a-logical-form/413/29
# "Predicatively" means used as a verb, as in "the dog is brown" where "brown" is used predicatively
# "attributively" means used as an adjective, as in "the brown dog barked" where "brown" is used adjectively
def used_predicatively(context, state):
    tree_info = state.get_binding("tree").value[0]
    this_predication = predication_from_index(tree_info, context.current_predication_index())
    return not predication_in_conjunction(tree_info, this_predication.index)


def get_wh_question_variable(tree_info):
    this_sentence_force = sentence_force(tree_info["Variables"])
    if this_sentence_force in ["ques", "prop-or-ques"]:
        predication = find_predications_in_list_in_list(tree_info["Tree"], ["_which_q", "which_q"])
        if predication is not None and len(predication) > 0:
            return predication[0].args[0]


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
        if isinstance(predication, list):
            foo = 5
        if predication.name in predication_name_list:
            found_predications.append(predication)

    return found_predications


# Returns the conjunction (if any) that the predication that introduced this
# variable is in
def find_predication_conjunction_from_introduced(term, introduced_variable):
    def match_introduced_variable(predication):
        for scopal_arg_raw in predication.scopal_args():
            scopal_arg_list = scopal_arg_raw if isinstance(scopal_arg_raw, list) else [scopal_arg_raw]
            for scopal_arg_predication in scopal_arg_list:
                if scopal_arg_predication.introduced_variable() == introduced_variable:
                    predication_data = parse_predication_name(scopal_arg_predication.name)
                    if predication_data["Pos"] != "q":
                        return scopal_arg_list
        return None

    return walk_tree_predications_until(term, match_introduced_variable)


def find_predication_from_introduced(term, introduced_variable):
    def match_introduced_variable(predication):
        if predication.introduced_variable() == introduced_variable:
            predication_data = parse_predication_name(predication.name)
            if predication_data["Pos"] != "q":
                return predication
        else:
            return None

    return walk_tree_predications_until(term, match_introduced_variable)


def find_quantifier_from_variable(term, variable_name):
    def match_variable(predication):
        predication_data = parse_predication_name(predication.name)
        if predication_data["Pos"] == "q" and predication.args[0] == variable_name:
            return predication
        else:
            return None

    return walk_tree_predications_until(term, match_variable)


def find_index_predication(tree_info):
    # TODO: stop using Index for syntactic head once we are sure that trees will always have just one OR
    # start returning multiple heads and deal with that properly
    syntactic_head_variable = tree_info["SyntacticHeads"][0] if len(tree_info["SyntacticHeads"]) == 1 else tree_info["Index"]
    return find_predication_from_introduced(tree_info["Tree"], syntactic_head_variable)


def gather_remaining_syntactic_heads(tree_info):
    def gather_heads(predication):
        if predication.introduced_variable() in tree_info["SyntacticHeads"]:
            remaining_heads.append(predication.introduced_variable())

    remaining_heads = []
    walk_tree_predications_until(tree_info["Tree"], gather_heads)
    return remaining_heads


def find_last_predication(tree):
    def process(predication):
        nonlocal last_predication
        if predication.index > last_predication.index:
            last_predication = predication

    last_predication = tree
    walk_tree_predications_until(tree, process)
    return last_predication


def gather_quantifier_order(tree_info):
    def gather_metadata(predication):
        if predication.arg_types[0] == "x":
            predication_info = parse_predication_name(predication.name)
            if predication_info["Pos"] == "q":
                quantifier_order.append(predication.args[0])

    quantifier_order = []
    walk_tree_predications_until(tree_info["Tree"], gather_metadata)
    return quantifier_order


def gather_scoped_variables_from_tree_at_index(tree, start_index):
    def gather_scoped_variables(predication):
        nonlocal scoped_variables, unscoped_variables
        predication_data = parse_predication_name(predication.name)
        if predication_data["Pos"] == "q":
            variable_kind = scoped_variables if predication.index >= start_index else unscoped_variables
            arg_name = predication.args[0]
            if arg_name not in variable_kind:
                variable_kind[arg_name] = None

    scoped_variables = {}
    unscoped_variables = {}
    walk_tree_predications_until(tree, gather_scoped_variables)
    return scoped_variables, unscoped_variables


def gather_referenced_x_variables_from_tree(tree):
    def gather_referenced_variables(predication):
        nonlocal referenced_x_variables
        for arg_name in predication.x_args():
            referenced_x_variables.add(arg_name)

    referenced_x_variables = set()
    walk_tree_predications_until(tree, gather_referenced_variables)
    return list(referenced_x_variables)


# Gather the metadata that a developer has decorated a predication with
# using @vocabulary.  Merge it *across* predications so the final metadata has
# the union
def gather_predication_metadata(vocabulary, tree_info, interpretation):
    def gather_metadata(predication):
        nonlocal interpretation

        # Any variable referenced under negation should not allow the predication that introduces it
        # to be reordered in its quantifier.  Because: that would allow the variable to be unbound and
        # returning the value of an unbound variable that fails (and thus succeeds) under negation is hard
        # but required if the user says "what is not vegetarian?" for example. So, avoid the whole thing
        if predication.name == "neg":
            referenced_variables = gather_referenced_x_variables_from_tree(predication.args[1])
            for variable in referenced_variables:
                if variable not in variable_metadata:
                    variable_metadata[variable] = {}
                variable_metadata[variable]["ReferencedUnderNegation"] = True

        metadata_list = vocabulary.metadata(predication.name, predication.arg_types)
        interpretation_module = interpretation[predication.index].module
        interpretation_function = interpretation[predication.index].function
        for metadata in metadata_list:
            if metadata.function != interpretation_function or metadata.module != interpretation_module:
                continue
            for arg_index in range(len(metadata.args_metadata)):
                if predication.arg_types[arg_index] == "h":
                    continue

                arg_name = predication.args[arg_index]
                arg_metadata = metadata.args_metadata[arg_index]

                if arg_name not in variable_metadata:
                    variable_metadata[arg_name] = {}

                # "ValueSize" are all the values from the ValueSize enum:
                # class ValueSize(enum.Enum):
                #     exactly_one = 1  # default
                #     more_than_one = 2
                #     all = 3
                if arg_metadata["VariableType"] == "x":
                    if "ValueSize" not in variable_metadata[arg_name]:
                        variable_metadata[arg_name]["ValueSize"] = None

                    if variable_metadata[arg_name]["ValueSize"] is None:
                        variable_metadata[arg_name]["ValueSize"] = arg_metadata["ValueSize"]

                    elif variable_metadata[arg_name]["ValueSize"] != perplexity.vocabulary.ValueSize.all:
                        if variable_metadata[arg_name]["ValueSize"] != arg_metadata["ValueSize"]:
                            variable_metadata[arg_name]["ValueSize"] = perplexity.vocabulary.ValueSize.all

    variable_metadata = {}
    walk_tree_predications_until(tree_info["Tree"], gather_metadata)
    return variable_metadata


# Walk the tree represented by "term" and
# return the predication that matches
# "predicate_name" or "None" if none is found
def find_predication(term, predication_name):
    if isinstance(predication_name, list):
        predication_names = predication_name
    else:
        predication_names = [predication_name]

    # This function gets called for every predication
    # in the tree. It is a private function since it is
    # only used here
    def match_predication_name(predication):
        if predication.name in predication_names:
            return predication
        else:
            return None

    # Pass our private function to WalkTreeUntil as
    # a way to filter through the tree to find
    # predication_name
    return walk_tree_predications_until(term, match_predication_name)


# Return all of the predications named predication_name
def find_predications(term, predication_names):
    # This function gets called for every predication
    # in the tree. It is a private function since it is
    # only used here
    def match_predication_name(predication):
        if predication.name in predication_names:
            found_predications.append(predication)

    if not isinstance(predication_names, (list, tuple, set)):
        predication_names = (predication_names,)

    found_predications = []

    # Pass our private function to WalkTreeUntil as
    # a way to filter through the tree to find
    # predication_name
    walk_tree_predications_until(term, match_predication_name)
    return found_predications


def tree_contains_predication(term, predication_list):
    def match_predication_name(predication):
        if predication.name in predication_list:
            return True

    return walk_tree_predications_until(term, match_predication_name)


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


def predication_in_conjunction(tree_info, index):
    def stop_at_index(predication):
        nonlocal index

        for arg in predication.args_with_types("h"):
            if isinstance(arg, list):
                for conjunction_predication in arg:
                    if conjunction_predication.index == index:
                        return True

    in_conjunction = walk_tree_predications_until(tree_info["Tree"], stop_at_index)
    return in_conjunction is True


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


# predication_rewrite_func gets called with each predication AND each list that represents a conjunction
# predication_rewrite_func must return a new predication or None if it wants to use the old one
# rewrite_tree_predications2 will then iterate on the arguments from the returned predication
# or the items in the list regardless if it is a new predication or the old one
def rewrite_tree_predications2(term, predication_rewrite_func, index_by_ref):
    if isinstance(term, list):
        # This is a conjunction, give predication_rewrite_func a chance to rewrite it
        # and, for example, remove or add items to it
        new_conjunction = predication_rewrite_func(term, index_by_ref)
        if new_conjunction is None:
            # no rewrite, copy and keep the conjunction
            new_conjunction = copy.deepcopy(term)

        new_term = []
        for predication in new_conjunction:
            new_term.append(rewrite_tree_predications2(predication, predication_rewrite_func, index_by_ref))

        return new_term

    else:
        # This is a predication, rewrite it
        new_term = predication_rewrite_func(term, index_by_ref)
        if new_term is None:
            # no rewrite, copy and keep the term, but use the new index_by_ref
            new_term = copy.deepcopy(term)
            new_term.index = index_by_ref[0]
            index_by_ref[0] += 1

        else:
            # New term has been rewritten, the rewriter needs to have reset its index
            pass

        # See if any of its terms are scopal
        # i.e. are predications themselves
        for scopal_index in new_term.scopal_arg_indices():
            new_term.args[scopal_index] = rewrite_tree_predications2(new_term.args[scopal_index], predication_rewrite_func, index_by_ref)

        return new_term


# Rewrite all the indexes in the tree to ensure there aren't any duplicates
# and they are consecutive
def reindex_tree(tree):
    def no_rewrite(term, index_by_ref):
        return None
    index_by_ref = [0]
    return rewrite_tree_predications(tree, no_rewrite, index_by_ref)


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


if __name__ == '__main__':
    force_input = "which chicken menu items do you have?"
    parser = MrsParser()
    for mrs in parser.mrss_from_phrase(force_input):
        print(f"MRS {mrs}")
        for tree_orig in parser.trees_from_mrs(mrs):
            print(tree_orig)
