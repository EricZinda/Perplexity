import copy
import logging

import perplexity.tree


class TransformerProduction(object):
    def __init__(self, name, args):
        # Name can be a string that contains any number of $ replacements
        # args can be:
        #   a string that contains any number of $ replacements like foo$bar or foo$|bar|goo
        #   another TransformerProduction
        self.name = name
        self.args = args

    def create(self, captures, current_index):
        my_index = current_index[0]
        current_index[0] += 1
        name = self.transform_using_captures(self.name, captures, current_index)
        args_values = [self.transform_using_captures(x, captures, current_index) for x in self.args.values()]
        args_names = list(self.args.keys())
        new_predication = perplexity.tree.TreePredication(my_index, name, args_values, arg_names=args_names)
        return new_predication

    def transform_using_captures(self, value, captures, current_index):
        if isinstance(value, str):
            items = value.split("$")
            if len(items) == 1:
                return value
            else:
                new_string = items[0]
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
                        new_string += item_split[0]
                    assert token in captures, f"There is no capture named {token}"
                    new_string += captures[token]
                    new_string += after_str

                return new_string

        else:
            return value.create(captures, current_index)

class AllMatchTransformer(object):
    def __init__(self):
        self.is_root = False

    def match(self, scopal_arg, captures):
        return True


class TransformerMatch(object):
    def __init__(self, name_pattern, args_pattern, name_capture=None, args_capture=None, production=None):
        self.name_pattern = name_pattern
        self.name_capture = name_capture if name_pattern is not None else [None] * len(name_pattern)
        self.args_pattern = args_pattern
        self.args_capture = args_capture if args_capture is not None else [None] * len(args_pattern)
        self.production = production
        self.did_transform = False

    def match(self, scopal_arg, captures):
        if isinstance(scopal_arg, perplexity.tree.TreePredication):
            if self.name_pattern == "*" or self.name_pattern == scopal_arg.name:
                local_capture = {}
                if self.name_capture is not None:
                    local_capture[self.name_capture] = scopal_arg.name

                if len(self.args_pattern) == len(scopal_arg.args):
                    for arg_index in range(len(self.args_pattern)):
                        if self.args_pattern[arg_index] == "*" or \
                                self.args_pattern[arg_index] == scopal_arg.arg_types[arg_index] or \
                                isinstance(self.args_pattern[arg_index], TransformerMatch) and scopal_arg.arg_types[arg_index] == "h":
                            if self.args_capture[arg_index] is not None:
                                local_capture[self.args_capture[arg_index]] = scopal_arg.args[arg_index]
                        else:
                            # Args didn't match
                            return False

                    captures.update(local_capture)
                    return True

        return False

    def arg_transformer(self, index):
        if isinstance(self.args_pattern[index], TransformerMatch):
            return self.args_pattern[index]
        else:
            return AllMatchTransformer()

    def record_transform(self):
        self.did_transform = True

    def is_root(self):
        return self.production is not None

# rewrites the tree in place
def build_transformed_tree(tree, transformer_root):
    # When called with a root transformer will either return None or a new predication
    # Otherwise returns True for a match, or False
    def transformer_search(scopal_arg, transformer, capture, current_index):
        if isinstance(scopal_arg, list):
            if transformer.is_root():
                new_conjunction = []
                for predication in scopal_arg:
                    new_predication = transformer_search(predication, transformer, {}, current_index)
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
            predication_matched = transformer.match(predication, capture)
            if transformer.is_root():
                # Since this is the root: Need to return None for no new predication creation or a new predication
                if predication_matched:
                    # This is the transformer root: we are now just trying to finish the match
                    # and fill in the capture
                    children_matched = True
                    for scopal_arg_index in predication.scopal_arg_indices():
                        if not transformer_search(predication.args[scopal_arg_index], transformer.arg_transformer(scopal_arg_index), capture, current_index):
                            # The child failed so this match fails
                            children_matched = False
                            break

                    if children_matched:
                        # The children matched so now we just return the new node
                        # and record that at least one transform occurred
                        transformer.record_transform()
                        return transformer.production.create(capture, current_index)

                # This predication will stick around, update its index
                predication.index = current_index[0]
                current_index[0] += 1

                # If we got here, the predication OR its children didn't match,
                # try the root on the children
                for scopal_arg_index in predication.scopal_arg_indices():
                    # transformer_search using the root transformer will return False or a new predication
                    new_predication = transformer_search(predication.args[scopal_arg_index], transformer, {}, current_index)
                    if new_predication:
                        predication.args[scopal_arg_index] = new_predication

                # Return None to indicate no new predication was created
                return None

            else:
                # This is not the transformer root so we are just finishing the match and
                # filling in the capture
                if predication_matched:
                    for scopal_arg_index in predication.scopal_arg_indices():
                        if not transformer_search(predication.args[scopal_arg_index], transformer.arg_transformer(scopal_arg_index), capture):
                            # The child failed so this match fails
                            # Since this is not the root, we just end now
                            return False

                    # The children all matched, so: success
                    return True

                else:
                    # If this isn't the root and we didn't match, we fail
                    return False


    new_tree = copy.deepcopy(tree)
    current_index = [0]
    transformer_search(new_tree, transformer_root, {}, current_index)
    if transformer_root.did_transform:
        pipeline_logger.debug(f"Transformed Tree: {new_tree}")
        return new_tree


pipeline_logger = logging.getLogger('Pipeline')
