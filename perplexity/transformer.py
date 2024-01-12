import copy
import logging
from delphin.mrs import EP
import perplexity.tree
from perplexity.utilities import sentence_force


def replace_str_captures(value, captures):
    items = value.split("$")
    if len(items) == 1:
        return value
    else:
        new_value = items[0]
        for item in items[1:]:
            item_split = item.split("|")
            if len(item_split) == 1:
                # No | separators
                token = item
                after_str = ""
            else:
                assert len(item_split) == 3
                token = item_split[1]
                after_str = item_split[2]
                new_value += item_split[0]
            assert token in captures, f"There is no capture named {token}"
            if isinstance(new_value, str) and len(new_value) == 0:
                new_value = captures[token]
            else:
                new_value += captures[token]

            if len(after_str) > 0:
                new_value += after_str

        return new_value


class TransformerProduction(object):
    def __init__(self, name, args, label="h999"):
        # Name can be a string that contains any number of $ replacements
        # args can be:
        #   a string that contains any number of $ replacements like foo$bar or foo$|bar|goo
        #   another TransformerProduction
        self.name = name
        self.args = args
        self.label = label

    def create(self, vocabulary, state, tree_info, captures, current_index):
        my_index = current_index[0]
        current_index[0] += 1
        name = self.transform_using_captures(self.name, vocabulary, state, tree_info, captures, current_index)
        args_values = [self.transform_using_captures(x, vocabulary, state, tree_info, captures, current_index) for x in self.args.values()]
        args_names = list(self.args.keys())
        label = self.transform_using_captures(self.label, vocabulary, state, tree_info, captures, current_index)
        args_handle_values = []
        for arg_value in args_values:
            if isinstance(arg_value, perplexity.tree.TreePredication):
                args_handle_values.append(arg_value.mrs_predication.label)
            else:
                args_handle_values.append(arg_value)

        new_ep = EP(predicate=name, label=label, args=dict(zip(args_names, args_handle_values)))
        new_predication = perplexity.tree.TreePredication(my_index, name, args_values, arg_names=args_names, mrs_predication=new_ep)
        phrase_type = sentence_force(tree_info["Variables"])
        if state is None or not vocabulary.unknown_word(state, new_predication.name, new_predication.argument_types(), phrase_type):
            return new_predication
        else:
            transform_logger.debug(
                f"Predication: {new_predication.name} could not be created by the transformer because it has no implementation")

    def transform_using_captures(self, value, vocabulary, state, tree_info, captures, current_index):
        if isinstance(value, str):
            return replace_str_captures(value, captures)
        else:
            return value.create(vocabulary, state, tree_info, captures, current_index)


# Runs at the very end
class PropertyTransformerMatch(object):
    # requires a dictionary where:
    #   each key is a capture name of a variable
    #   each value is a dictionary of properties and values to match
    def __init__(self, variables_pattern):
        self.variables_pattern = variables_pattern

    def match(self, tree_info, captures, metadata):
        for variable_reference_item in self.variables_pattern.items():
            variable = replace_str_captures(variable_reference_item[0], captures)
            properties = variable_reference_item[1]
            if variable not in tree_info["Variables"]:
                return False
            existing_properties = tree_info["Variables"][variable]
            for property_item in properties.items():
                if property_item[0] not in existing_properties or \
                        property_item[1] != existing_properties[property_item[0]]:
                    return False
        return True


# conjunction_list must be a list of either: a string which is eval'd like elsewhere or
# another production
class ConjunctionProduction(object):
    def __init__(self, conjunction_list=None):
        self.conjunction_list = conjunction_list

    def create(self, vocabulary, state, variables, captures, current_index):
        production_list = []
        for item in self.conjunction_list:
            if isinstance(item, str):
                value = replace_str_captures(item, captures)
                if value != "":
                    production_list.append(value)
            elif hasattr(item, "create"):
                production_list.append(item.create(vocabulary, state, variables, captures, current_index))
            else:
                assert False, "ConjunctionProduction(conjunction_list) must be a list of a combination of strings or productions only"

        if len(production_list) == 1:
            return production_list[0]
        else:
            return production_list


class PropertyTransformerProduction(object):
    # requires a dictionary where:
    #   each key is a capture name of a variable
    #   each value is a dictionary of properties and values to match
    def __init__(self, variables_pattern):
        self.variables_pattern = variables_pattern

    def create(self, vocabulary, state, variables, captures, current_index):
        for variable_item in self.variables_pattern.items():
            variable_value = replace_str_captures(variable_item[0], captures)
            for property_item in variable_item[1].items():
                if property_item[1] is None:
                    # remove the property
                    variables[variable_value].pop(property_item[0])
                else:
                    # update the property
                    variables[variable_value][property_item[0]] = property_item[1]


class AllMatchTransformer(object):
    def __init__(self):
        pass

    def __repr__(self):
        return "<All Match>"

    # Return True or False if the single predication represented by
    # scopal_arg matches this transformer
    # Also: fill in captures() from the predication
    def match(self, scopal_arg, captures, metadata):
        return True

    # Return the transformer to use for the specified arg
    # returning AllMatchTransformer
    def arg_transformer(self, index):
        return AllMatchTransformer()

    # True if this is the root of the tree of predications doing
    # a match
    def is_root(self):
        return False


# Matches a conjunction, where the items in the conjunction
# are other MatchTransforers
class ConjunctionMatchTransformer(object):
    def __init__(self, transformer_list, extra_conjuncts_capture=None, property_transformer=None, production=None, properties_production=None):
        self.transformer_list = transformer_list
        self.property_transformer = property_transformer
        self.production = production
        self.properties_production = properties_production
        self.extra_conjuncts_capture = extra_conjuncts_capture

    def __repr__(self):
        return "<ConjunctionMatchTransformer>"

    # When called with a root transformer will either return None or a new predication
    # Otherwise returns True for a match, or False
    def match_tree(self, transformer_search, conjunction, variables, capture, metadata, current_index):
        if not isinstance(conjunction, list) or (not self.extra_conjuncts_capture and len(self.transformer_list) != len(conjunction)):
            return False

        unmatched_indices = [x for x in range(len(conjunction))]
        for predication_index in range(len(self.transformer_list)):
            found_match = False
            for match_index in unmatched_indices:
                if transformer_search(conjunction[match_index],
                                      variables,
                                      self.transformer_list[predication_index],
                                      capture,
                                      metadata,
                                      current_index):
                    unmatched_indices.remove(match_index)
                    found_match = True
                    break

            if not found_match:
                return False

        if self.extra_conjuncts_capture:
            unmatched_list = []
            for unmatched_index in unmatched_indices:
                unmatched_list.append(conjunction[unmatched_index])

            capture[self.extra_conjuncts_capture] = unmatched_list if len(unmatched_list) > 0 else ""
        if self.property_transformer is not None:
            return self.property_transformer.match(self.tree_info, capture, metadata)

        else:
            return True

    # Return True or False if the single predication represented by
    # scopal_arg matches this transformer
    # Also: fill in captures() from the predication
    def match(self, scopal_arg, captures, metadata):
        return False

    # Return the transformer to use for the specified arg
    # returning AllMatchTransformer
    def arg_transformer(self, index):
        assert False

    # True if this is the root of the tree of predications doing
    # a match
    def is_root(self):
        return self.production is not None or self.properties_production is not None


class TransformerMatch(object):
    def __init__(self, name_pattern, args_pattern, name_capture=None, args_capture=None, label_capture=None, property_transformer=None, removed=None, production=None, properties_production=None):
        self.name_pattern = name_pattern
        self.name_capture = name_capture if name_pattern is not None else [None] * len(name_pattern)
        self.args_pattern = args_pattern
        self.args_capture = args_capture if args_capture is not None else [None] * len(args_pattern)
        self.label_capture = label_capture
        self.property_transformer = property_transformer
        self.production = production
        self.properties_production = properties_production
        self.removed = removed
        self.did_transform = False

    def __repr__(self):
        return f"{self.name_pattern}({', '.join([str(x) for x in self.args_pattern])})"

    def match(self, scopal_arg, captures, metadata):
        if isinstance(scopal_arg, perplexity.tree.TreePredication):
            # Remember all the which_q predications in case we need to match them
            if scopal_arg.name in ["_which_q", "which_q"]:
                if "SystemWH" not in metadata:
                    metadata["SystemWH"] = []
                metadata["SystemWH"].append(scopal_arg.args[0])

            name_alternatives = self.name_pattern.split("|")
            if self.name_pattern == "*" or scopal_arg.name in name_alternatives:
                local_capture = {}
                if self.name_capture is not None:
                    local_capture[self.name_capture] = scopal_arg.name
                if self.label_capture is not None:
                    local_capture[self.label_capture] = scopal_arg.mrs_predication.label
                if len(self.args_pattern) == len(scopal_arg.args):
                    for arg_index in range(len(self.args_pattern)):
                        pattern = self.args_pattern[arg_index]
                        if isinstance(pattern, str) and len(pattern) > 2:
                            assert pattern[0:2] == "wh", f"Unknown argument pattern: {pattern}"
                            match_wh = pattern[2]
                            assert match_wh in ["+", "-"]
                            arg_pattern = pattern[3:]
                        else:
                            match_wh = None
                            arg_pattern = pattern

                        if arg_pattern == "*" or \
                                arg_pattern == scopal_arg.arg_types[arg_index] or \
                                isinstance(arg_pattern, (TransformerMatch, ConjunctionMatchTransformer)) and scopal_arg.arg_types[arg_index] == "h":
                            # Ensure that this variable either is or isn't a wh_variable
                            if "SystemWH" in metadata:
                                is_wh = scopal_arg.args[arg_index] in metadata["SystemWH"]
                            else:
                                is_wh = False

                            if match_wh == "+" and is_wh or match_wh == "-" and not is_wh or match_wh is None:
                                if self.args_capture[arg_index] is not None:
                                    local_capture[self.args_capture[arg_index]] = scopal_arg.args[arg_index]
                            else:
                                # WH didn't match
                                return False
                        else:
                            # Args didn't match
                            return False

                    captures.update(local_capture)
                    return True

        return False

    def arg_transformer(self, index):
        if isinstance(self.args_pattern[index], (TransformerMatch, ConjunctionMatchTransformer)):
            return self.args_pattern[index]
        else:
            return AllMatchTransformer()

    def record_transform(self):
        self.did_transform = True

    def reset_transform(self, tree_info):
        self.did_transform = False
        self.tree_info = tree_info

    def is_root(self):
        return self.production is not None or self.properties_production is not None

    def removed_predications(self):
        if self.removed is None:
            return []
        else:
            return self.removed


# rewrites the tree in place
def build_transformed_tree(vocabulary, state, tree_info, transformer_root):
    def build_production(transformer, variables, capture, current_index):
        if transformer.properties_production:
            # The properties production will simply update the tree directly
            transformer.properties_production.create(vocabulary, state, variables, capture, current_index)
            transformer.record_transform()

        # The node might not be able to be created if there is no implementation
        if transformer.production:
            new_node = transformer.production.create(vocabulary, state, tree_info, capture, current_index)
            if new_node is not None:
                # we just return the new node
                # and record that at least one transform occurred
                transformer.record_transform()
                return new_node

        elif transformer.properties_production:
            # Just properties got updated
            return True

    # When called with a root transformer will either return None or a new predication
    # Otherwise returns True for a match, or False
    def transformer_search(scopal_arg, variables, transformer, capture, metadata, current_index):
        if isinstance(scopal_arg, list):
            if isinstance(transformer, ConjunctionMatchTransformer):
                if transformer.is_root():
                    if transformer.match_tree(transformer_search, scopal_arg, variables, capture, metadata, current_index):
                        new_conjunction = build_production(transformer, variables, capture, current_index)
                        if new_conjunction in [None, True]:
                            return scopal_arg
                        else:
                            return new_conjunction

                else:
                    # This is not the transformer root so we are just finishing the match and
                    # filling in the capture
                    return transformer.match_tree(transformer_search, scopal_arg, variables, capture, metadata, current_index)

            elif transformer.is_root():
                new_conjunction = []
                for predication in scopal_arg:
                    new_predication = transformer_search(predication, variables, transformer, {}, metadata, current_index)
                    if new_predication is None:
                        new_predication = predication
                    new_predication.index = current_index[0]
                    current_index[0] += 1
                    new_conjunction.append(new_predication)
                return new_conjunction

            else:
                # transformers can't span a conjunction, so fail if this is not the root
                return False

        else:
            predication = scopal_arg
            predication_matched = transformer.match(predication, capture, metadata)
            if transformer.is_root():
                # Since this is the root: Need to return None for no new predication creation or a new predication
                if predication_matched:
                    transform_logger.debug(f"Root Match: {predication_matched}. Pattern:{transformer}, Predicate:{predication}")
                    # This is the transformer root: we are now just trying to finish the match
                    # and fill in the capture
                    children_matched = True
                    for scopal_arg_index in predication.scopal_arg_indices():
                        if not transformer_search(predication.args[scopal_arg_index], variables, transformer.arg_transformer(scopal_arg_index), capture, metadata, current_index):
                            # The child failed so this match fails
                            children_matched = False
                            break

                    if children_matched:
                        # The children matched so now we need to check the properties
                        properties_matched = True
                        if transformer.property_transformer is not None:
                            properties_matched = transformer.property_transformer.match(transformer.tree_info, capture, metadata)

                        if properties_matched:
                            return build_production(transformer, variables, capture, current_index)

                # This predication will stick around, update its index
                predication.index = current_index[0]
                current_index[0] += 1

                # If we got here, the predication OR its children didn't match,
                # try the root on the children
                for scopal_arg_index in predication.scopal_arg_indices():
                    # transformer_search using the root transformer will return False or a new predication
                    new_predication = transformer_search(predication.args[scopal_arg_index], variables, transformer, {}, metadata, current_index)
                    if new_predication:
                        predication.args[scopal_arg_index] = new_predication

                # Return None to indicate no new predication was created
                return None

            else:
                # This is not the transformer root, so we are just finishing the match and
                # filling in the capture
                if predication_matched:
                    transform_logger.debug(f"Child Match: {predication_matched}. Pattern:{transformer}, Predicate:{predication}")
                    for scopal_arg_index in predication.scopal_arg_indices():
                        if not transformer_search(predication.args[scopal_arg_index], variables, transformer.arg_transformer(scopal_arg_index), capture, metadata, current_index):
                            # The child failed so this match fails
                            # Since this is not the root, we just end now
                            return False

                    # The children all matched, so: success
                    return True

                else:
                    # If this isn't the root and we didn't match, we fail
                    return False

    new_tree_info = copy.deepcopy(tree_info)
    current_index = [0]
    transformer_root.reset_transform(tree_info)
    metadata = {}
    transformer_search(new_tree_info["Tree"], new_tree_info["Variables"], transformer_root, {}, metadata, current_index)
    if transformer_root.did_transform:
        # Make sure the tree indexes are set right
        new_tree_info["Tree"] = perplexity.tree.reindex_tree(new_tree_info["Tree"])
        new_tree_info["Transformed"] = str(transformer_root)
        pipeline_logger.debug(f"Transformed Tree: {new_tree_info['Tree'].repr_with_indices()}")
        return new_tree_info


pipeline_logger = logging.getLogger('Pipeline')
transform_logger = logging.getLogger('Transformer')
