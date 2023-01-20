# Code to draw a nice text tree inspired by and parts copied from:
# https://stackoverflow.com/questions/13128750/what-are-the-step-to-the-reingold-tilford-algorithm-and-how-might-i-program-it
# https://rachel53461.wordpress.com/2014/04/20/algorithm-for-drawing-trees/
from perplexity.tree import TreePredication
from perplexity.utilities import parse_predication_name


# Get original argument names from the mrs given a name and arg count
def arg_names_from_mrs(mrs, predication_name, arg_count):
    for item in mrs.predications:
        if item.predicate == predication_name and arg_count == len(item.args):
            return list(item.args.keys())

    # Give anything without a real predication
    # (like the fake "and" predication we add)
    # just a list of numbers
    return [str(item) for item in range(0, arg_count)]


# Convert Perplexity tree format to a set
# of printable nodes
def create_draw_tree(mrs, tree_node, parent=None, hole=None):
    if isinstance(tree_node, list):
        if len(tree_node) > 1:
            # Need to treat as a single fake "and" node
            predication = TreePredication(-1, "and", tree_node)
        else:
            predication = tree_node[0]

    elif isinstance(tree_node, TreePredication):
        predication = tree_node

    else:
        return

    new_node = DrawNode(parent, predication.name, hole)
    arg_names = arg_names_from_mrs(mrs, predication.name, len(predication.args))

    for arg_index in range(0, len(arg_names)):
        arg = predication.args[arg_index]
        arg_name = arg_names[arg_index]
        child = create_draw_tree(mrs, arg, new_node, arg_name)
        if child is None:
            new_node.args.append(arg)

        else:
            new_node.args.append(arg_name)
            new_node.children.append(child)

    return new_node


# nodes are represented as a function with args like:
#   label(arg1,arg2,...)
# hole_label is used to match a DrawNode with the argument in its
#   parent where its line should be drawn from
class DrawNode(object):
    def __init__(self, parent, predication_name, hole_label):
        self.parent = parent
        self.label = predication_name
        self.hole_label = hole_label
        self.args = []
        self.children = []
        self.x = None
        self.y = None
        self.mod = None
        self.width = None
        self.height = None

        self.text = None
        self.line_y = None
        self.arg_x_offset = {}

    def calculate_bounding_box(self):
        if self.label == "and":
            raw_predicate = "and"
        else:
            raw_predicate = parse_predication_name(self.label)["PredicateRaw"]

        base_text = raw_predicate + "("
        x_pos = len(base_text)
        for arg in self.args:
            self.arg_x_offset[arg] = x_pos + int(len(arg) / 2)
            x_pos += len(arg) + 1
        self.text = base_text + ",".join([arg for arg in self.args]) + ")"

    def is_leaf(self):
        return len(self.children) == 0

    def is_topmost(self):
        if self.parent is None:
            return True
        else:
            return self.parent.children[0] == self

    def is_bottommost(self):
        if self.parent is None:
            return True
        else:
            return self.parent.children[-1] == self

    def is_middle(self):
        if len(self.parent.children) % 2 != 0:
            return self.parent.children.index(self) == int(len(self.parent.children) / 2) + 1
        else:
            return False

    def previous_sibling(self):
        if self.is_topmost():
            return None
        else:
            return self.parent.children[self.parent.children.index(self) - 1]

    def next_sibling(self):
        if self.is_bottommost():
            return None
        else:
            return self.parent.children[self.parent.children.index(self) + 1]

    def topmost_sibling(self):
        if self.parent is None:
            return None
        else:
            return self.parent.children[0]

    def topmost_child(self):
        if len(self.children) == 0:
            return None
        else:
            return self.children[0]

    def bottommost_child(self):
        if len(self.children) == 0:
            return None
        else:
            return self.children[-1]


# Axes are: up is negative Y, down is positive Y
#           left is negative X, right is positive X
class TreeRenderer(object):
    def __init__(self):
        self.node_size = 1
        self.sibling_distance = 0.0
        self.tree_distance = 1.0

    def calculate_positions(self, node):
        # initialize node x, y, and mod values
        self.initialize_nodes(node, 0)
        # assign initial y and Mod values for nodes
        self.calculate_initial_y(node)
        self.check_bounds(node)
        self.final_positions(node, 0)
        self.arrange_for_text(node)

    def arrange_for_text(self, node):
        y_positions = {}
        max_x = [0]
        max_width = [0]
        self.draw_stats(node, y_positions, max_x, max_width)
        sorted_y_positions = sorted(y_positions.items(), key=lambda x: x[0])
        for index in range(0, len(sorted_y_positions)):
            for y_node in sorted_y_positions[index][1]:
                y_node.line_y = index

    def print_tree(self, node):
        self.calculate_positions(node)
        surface = TextSurface()
        self.print_node(surface, 0, node)
        surface.print()

    def print_node(self, surface, x_offset, node):
        surface.draw_string(x_offset, node.line_y, node.text)
        for child in node.children:
            if child.label != "":
                # Draw the line to the child
                y_offset = -1 if node.line_y > child.line_y else +1
                surface.draw_square_line(y_offset, x_offset + node.arg_x_offset[child.hole_label], node.line_y, x_offset + len(node.text), child.line_y)
                self.print_node(surface, x_offset + len(node.text), child)

    def draw_stats(self, node, y_positions, max_x, max_width):
        if node.y not in y_positions:
            y_positions[node.y] = []

        y_positions[node.y].append(node)
        node.calculate_bounding_box()
        if node.x > max_x[0]:
            max_x[0] = node.x
        if len(node.text) > max_width[0]:
            max_width[0] = len(node.text)

        for child in node.children:
            self.draw_stats(child, y_positions, max_x, max_width)

    def initialize_nodes(self, node, depth):
        node.x = depth
        node.y = -1
        node.mod = 0
        for child in node.children:
            self.initialize_nodes(child, depth + 1)

    def calculate_initial_y(self, node):
        for child in node.children:
            self.calculate_initial_y(child)

        # For each parent node, we want the node centered over the children.
        # This would be the midway point between the first child’s Y position,
        # and the last child’s Y position.
        if node.is_leaf():
            # No children
            if node.is_topmost():
                # This is the first node in a set, set Y to 0
                node.y = 0
            else:
                # There is a previous sibling in this set, set Y to previous sibling + designated distance
                node.y = node.previous_sibling().y + self.node_size + self.sibling_distance

        elif len(node.children) == 1:
            # There is only one child
            midpoint = node.children[0].y
            # For odd # of children add .5 to force the children to be on either side for the wires
            midpoint += .5
            if node.is_topmost():
                # This is the first node in a set, set its Y value equal to its child's Y value
                node.y = midpoint
            else:
                # Make the node the size of its children so the siblings are pushed away to make room for the wires
                node.y = node.previous_sibling().y + self.node_size + self.sibling_distance
                node.mod = node.y - midpoint

        else:
            # More than one child
            top_child = node.topmost_child()
            bottom_child = node.bottommost_child()
            midpoint = (top_child.y + bottom_child.y) / 2
            # For odd # of children add .5 to force the children to be on either side for the wires
            if len(node.children) % 2 != 0:
                midpoint += .5

            if node.is_topmost():
                node.y = midpoint

            else:
                node.y = node.previous_sibling().y + self.node_size + self.sibling_distance
                node.mod = node.y - midpoint

        if not node.is_topmost():
            # Since subtrees can overlap, check for conflicts and shift tree down if needed
            self.check_tree_overlaps(node)

    def check_bounds(self, root_node):
        root_top_contour = {}
        self.top_contour(root_node, 0, root_top_contour)
        shift = 0
        for x in root_top_contour.keys():
            if root_top_contour[x] + shift < 0:
                shift = root_top_contour[x] * -1

        if shift > 0:
            root_node.y += shift
            root_node.mod += shift

    def final_positions(self, node, mod_sum):
        node.y += mod_sum
        mod_sum += node.mod

        for child in node.children:
            self.final_positions(child, mod_sum)

        if len(node.children) == 0:
            node.width = node.x
            node.height = node.y
        else:
            node.width = max([child.width for child in node.children])
            node.height = max([child.height for child in node.children])

    # Get the top contour of this node and incrementally
    # move it away from the bottom contour of those above it
    def check_tree_overlaps(self, node):
        min_distance = self.tree_distance + self.node_size
        shift = 0.0

        node_top_contour = {}
        self.top_contour(node, 0, node_top_contour)

        # Go through each sibling to see if there are overlaps
        sibling = node.topmost_sibling()
        while sibling is not None and sibling != node:
            sibling_bottom_contour = {}
            self.bottom_contour(sibling, 0, sibling_bottom_contour)

            # Get the largest x value present in each contour
            max_sibling_bottom_contour = max(sibling_bottom_contour.keys())
            max_node_top_contour = max(node_top_contour.keys())

            # start at node.x and go through all the x values until you hit the end
            # of whichever contour is smallest, This assumes that the nodes are drawn
            # such that only the same X values can overlap
            # If the distance between the contours is too small, increase it
            for level in range(node.x + 1, min([max_sibling_bottom_contour, max_node_top_contour]) + 1):
                distance = node_top_contour[level] - sibling_bottom_contour[level]
                if distance + shift < min_distance:
                    shift = max([min_distance - distance, shift])

            # Then check if the first level children of the sibling overlap this node too
            # This can happen because the length of text drawn for a node can be much smaller
            # for the sibling node which pulls the children back
            if node.x + 1 in sibling_bottom_contour:
                distance = node_top_contour[node.x] - sibling_bottom_contour[node.x + 1]
                if distance + shift < min_distance:
                    shift = max([min_distance - distance, shift])

            sibling = sibling.next_sibling()

        if shift > 0:
            node.y += shift
            node.mod += shift
            self.center_between(node, sibling)
            shift = 0

    def center_between(self, top_node, bottom_node):
        top_index = top_node.parent.children.index(top_node)
        bottom_index = bottom_node.parent.children.index(bottom_node)
        nodes_between = (bottom_index - top_index) - 1
        if nodes_between > 0:
            distance_between = (top_node.y - bottom_node.y) / (nodes_between + 1)

            count = 1
            for i in range(top_index + 1, bottom_index):
                middle_node = top_node.parent.children[i]
                desired_y = bottom_node.y + (distance_between * count)
                offset = desired_y - middle_node.y
                middle_node.y += offset
                middle_node.mod += offset
                count += 1

            self.check_tree_overlaps(top_node)

    # Walk through each node and record its minimum (farthest up) y value
    def top_contour(self, node, mod_sum, contour):
        if node.x not in contour:
            contour[node.x] = node.y + mod_sum
        else:
            contour[node.x] = min([contour[node.x], node.y + mod_sum])

        mod_sum += node.mod
        for child in node.children:
            self.top_contour(child, mod_sum, contour)

    # Walk through each node and record its maximum (farthest down) y value
    def bottom_contour(self, node, mod_sum, contour):
        if node.x not in contour:
            contour[node.x] = node.y + mod_sum
        else:
            contour[node.x] = max([contour[node.x], node.y + mod_sum])

        mod_sum += node.mod
        for child in node.children:
            self.bottom_contour(child, mod_sum, contour)


# List that can dynamically grow
class DefaultList(list):
    def __init__(self, default_factory, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.default_factory = default_factory

    def _extend(self, index):
        while len(self) <= index:
            self.append(self.default_factory())

    def __getitem__(self, index):
        self._extend(index)
        return super().__getitem__(index)

    def __setitem__(self, index, value):
        self._extend(index)
        super().__setitem__(index, value)


# Allows for drawing on a 2D text "graphics" surface
class TextSurface(object):
    def __init__(self):
        self.surface = DefaultList(lambda: DefaultList(lambda: " "))

    def draw_string(self, x, y, string):
        for index in range(0, len(string)):
            self.surface[y][x + index] = string[index]

    def draw_square_line(self, offset, x1, y1, x2, y2):
        y1 += offset
        for y in range(y1, y2, -1 if y2 < y1 else +1):
            self.surface[y][x1] = "│"
        for x in range(x1, x2 - 1, -1 if x2 < x1 else +1):
            self.surface[y2][x] = "─"
        self.surface[y2][x2] = "╴"
        if offset < 0:
            self.surface[y2][x1] = "┌"
        else:
            self.surface[y2][x1] = "└"

    def print(self):
        for row in self.surface:
            print("".join(row))
