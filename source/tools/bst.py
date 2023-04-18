from __future__ import annotations

from manim import *
from typing import Hashable, Iterable, Optional, Tuple, Union, List, Any
from .consts import *
from copy import deepcopy

BST_WEIGHT_COLOR = WHITE
BST_WEIGHT_FONT_COLOR = BLACK

# BST_WEIGHT_COLOR = BACKGROUND_COLOR
# BST_WEIGHT_FONT_COLOR = WHITE

BST_WEIGHT_LABEL_SCALE = 0.8
BST_WEIGHT_SCALE = 0.5


class Node(LabeledDot):
    """Simple class that represents a BST node"""

    def __init__(self, key=None, label=None, tree_height=0, **kwargs):
        if label is not isinstance(label, SVGMobject) and label is not None:
            label = MathTex(label, fill_color=LABEL_COLOR)
        label_scale = kwargs.pop("label_scale", VERTEX_LABEL_SCALE)
        kwargs = {**VERTEX_CONFIG, **kwargs}
        super().__init__(label=MathTex(key, fill_color=LABEL_COLOR) if label is None else label, **kwargs)
        self[1].scale(label_scale)
        self.label = self[1]
        self.key = label if key is None else key
        self.left = None
        self.right = None
        self.tree_height = tree_height


class Edge(Line):
    """Simple class that represents a BST edge"""

    def __init__(self, start: Node, end: Node, weight: str | int | VMobject = None, **kwargs):
        super().__init__(start.get_center(), end.get_center(), **kwargs)
        self.start = start
        self.end = end

        if weight is not None:
            self.weight = weight if isinstance(weight, VMobject) else LabeledDot(
                label=MathTex(weight, fill_color=WEIGHT_LABEL_FONT_COLOR), **WEIGHT_CONFIG)

            if weight is not isinstance(weight, VMobject):
                self.weight.scale(WEIGHT_SCALE)
                self.weight[1].scale(WEIGHT_LABEL_SCALE)

            self.weight.move_to(self.get_center())
            self.add(self.weight)


class BST(VGroup):
    """Class that represents a full binary search tree"""

    def __init__(self, keys: list = None, weighted: bool = True, **kwargs):
        super().__init__(**kwargs)
        self.root = None
        self.edges = {}
        self.nodes = VGroup()
        self.weighted = weighted
        if keys is not None:
            self.insert_keys(keys)

    def get_height(self):
        return max(self.nodes, key=lambda node: node.tree_height).tree_height

    def _insert_key(self, key: int | Node, node: Node = None, tree_height: int = 0) -> Node:
        if node is None:
            ret_key = key if isinstance(key, Node) else Node(key, tree_height=tree_height)
            self.nodes += ret_key
            self.add(ret_key)
            return ret_key

        key_val = key.key if isinstance(key, Node) else key
        if key_val < node.key:
            node.left = self._insert_key(key, node.left, tree_height=tree_height + 1)
        else:
            node.right = self._insert_key(key, node.right, tree_height=tree_height + 1)
        return node

    def insert_keys(self, keys: list | int, set_root=True):
        """Inserts a list of keys into the BST recursively"""
        keys = [keys] if isinstance(keys, int) else keys
        for key in keys:
            node = self._insert_key(key, self.root)
            self.root = node if set_root else self.root

    def search(self, key: int | Node) -> tuple[Node | None, list[Any]]:
        """Returns a list of nodes containing the path from root to target node"""
        path = []

        def search_helper(node: Node, key: int) -> Optional[Node]:
            if node is None:
                return None
            path.append(node)
            if key < node.key:
                return search_helper(node.left, key)
            elif key > node.key:
                return search_helper(node.right, key)
            else:
                return node

        key_val = key.key if isinstance(key, Node) else key
        return search_helper(self.root, key_val), path[:-1]

    def delete_key(self, key):  # TODO: update heights and remove edges and node from self and self.edges
        """Deletes the node with the given key from the tree"""
        parent, temp, is_left_child = None, self.root, False
        while temp.key != key:
            parent = temp
            if key < temp.key:
                is_left_child = True
                temp = temp.left
            else:
                temp = temp.right

        if temp.left is None and temp.right is None:
            if parent is None:
                self.root = None
                return
            if is_left_child:
                parent.left = None
            else:
                parent.right = None

        elif temp.left is None or temp.right is None:
            if parent is None:
                self.root = temp.left

    def traverse(self, func, *args):
        """Traverses the tree in a depth-first manner"""
        self.traverse_sub_tree(self.root, func, 0, *args)

    def traverse_sub_tree(self, node: Node, func, depth: int, *args):
        if node is None:
            return
        func(node, depth, *args)
        self.traverse_sub_tree(node.left, func, depth + 1, *args)
        self.traverse_sub_tree(node.right, func, depth + 1, *args)


def get_depth(current_node: Node):
    """Returns the depth of the current subtree"""
    if current_node is None:
        return 0
    return 1 + max(get_depth(current_node.left), get_depth(current_node.right))


def get_column_positions_from_root(current_node: Node, current_pos: int, relative_positions: dict[Node, int]):
    """Assigns relative column positions to each node, with no regard for overlap"""
    if current_node is None:
        return

    relative_positions[current_node] = current_pos
    get_column_positions_from_root(current_node.left, current_pos - 1, relative_positions)
    get_column_positions_from_root(current_node.right, current_pos + 1, relative_positions)


def eliminate_overlap(current_node: Node, relative_positions: dict[Node, int], bst: BST):
    """Recursively shifts the tree to eliminate overlaps and enforce a minimum horizontal distance
     between nodes from the bottom up"""
    if current_node is None:
        return

    eliminate_overlap(current_node.left, relative_positions, bst)
    eliminate_overlap(current_node.right, relative_positions, bst)

    rightmost_in_left, leftmost_in_right = {}, {}
    compute_rightmost_or_leftmost(current_node.left, 0, rightmost_in_left, True, relative_positions)
    compute_rightmost_or_leftmost(current_node.right, 0, leftmost_in_right, False, relative_positions)

    overlap_given_depth = {depth: rightmost_in_left[depth] - leftmost_in_right[depth]
                           for depth in set(rightmost_in_left.keys()).intersection(leftmost_in_right.keys())}

    if len(overlap_given_depth) == 0:
        return

    amount_to_shift = max(overlap_given_depth.values()) / 2 + 1

    def shift_subtree(current_node: Node, depth, amount_to_shift: int):
        """Shifts the entire subtree rooted at the given node to the right by some given amount (could be negative)"""
        relative_positions[current_node] += amount_to_shift
    # shift sutree as lambda function
    c = lambda node, depth, amount_to_shift: relative_positions.update({node: relative_positions[node] + amount_to_shift})
    bst.traverse_sub_tree(current_node.left, c, 0, - amount_to_shift)
    bst.traverse_sub_tree(current_node.right, c, 0, amount_to_shift)

def shift_tree_cols(bst: BST, relative_positions: dict[Node, int]):
    """Shifts the entire tree to the right by some given amount (could be negative)"""
    amount_to_shift = min(relative_positions.values()) - 1
    bst.traverse_sub_tree(lambda node, depth, amount_to_shift: relative_positions.update({node: relative_positions[node] - amount_to_shift}),
                 amount_to_shift)

def compute_rightmost_or_leftmost(current_node: Node, depth: int, depth_to_most_col: dict[int, int],
                                  rightmost: bool, relative_positions: dict[Node, int]):
    """Calculates and stores either the rightmost or leftmost position
     in a given subtree for every depth level"""
    if current_node is None:
        return

    operator = max if rightmost else min

    depth_to_most_col[depth] = operator(depth_to_most_col[depth], relative_positions[
        current_node]) if depth in depth_to_most_col.keys() else relative_positions[current_node]

    compute_rightmost_or_leftmost(current_node.left, depth + 1, depth_to_most_col, rightmost, relative_positions)
    compute_rightmost_or_leftmost(current_node.right, depth + 1, depth_to_most_col, rightmost, relative_positions)


def get_bst_layout(bst: BST, left=-config.frame_width / 2, width=config.frame_width, top=config.frame_height / 2,
                   height=config.frame_height, extra_space_at_top=False):
    """
    Positions the nodes of the given binary search tree in a way that
    minimizes overlap and maximizes horizontal distance.
    :param bst: the binary search tree to position.
    :param left: the leftmost x-coordinate of the bounding box.
    :param width: the width of the bounding box.
    :param top: the topmost y-coordinate of the bounding box.
    :param height: the height of the bounding box.
    :param extra_space_at_top: whether to leave extra space at the top of the bounding box.
    :return:
    """
    relative_cols_positions = {}

    get_column_positions_from_root(bst.root, 0, relative_cols_positions)

    eliminate_overlap(bst.root, relative_cols_positions, bst)

    num_cols = max(relative_cols_positions.values()) - min(relative_cols_positions.values()) + 1
    horiz_increment = width / (num_cols + 1)
    vert_increment = height / (get_depth(bst.root) + 1 + extra_space_at_top)
    scale_factor = min(horiz_increment, vert_increment)
    minimum_position = min(relative_cols_positions.values())

    if extra_space_at_top:
        top -= vert_increment

    def locate_nodes(current_node: Node, depth: int, layout: dict[Node, np.ndarray]):
        """Converts the relative horizontal coordinates to circle objects in the canvas"""
        x_coord = left + (relative_cols_positions[current_node] - minimum_position + 1) * horiz_increment
        y_coord = top - (depth + 1) * vert_increment
        layout[current_node] = RIGHT * x_coord + UP * y_coord

    layout = {}
    bst.traverse(locate_nodes, layout)
    for node in layout:
        node.move_to(layout[node])

    def create_edges(current_node: Node):
        """Creates arrow objects in the canvas mapping from circle center to circle center"""
        if current_node is None:
            return

        for child in [n for n in [current_node.left, current_node.right] if n is not None]:
            edge_params = dict(start=current_node, end=child, buff=0, stroke_width=scale_factor * 3, z_index=-10)
            if bst.weighted:
                edge_params["weight"] = create_bst_weight("<" if current_node.left is child else r"\geq", current_node)
            bst.edges[child] = Edge(**edge_params)
            bst.add(bst.edges[child])

        create_edges(current_node.left)
        create_edges(current_node.right)

    create_edges(bst.root)

    return scale_factor


def insert_bst(scene: Scene, bst: BST, key: int, left=-7, width=14, top=4, height=8):
    """Inserts the given key to the BST and animates the process"""
    position_bst_layout(bst, left, width, top, height)
    shift_bst = bst.copy()
    old_scale = position_bst_layout(shift_bst, left, width, top, height, True)

    bst.insert_keys(key)
    new_bst = bst.copy()
    new_scale = position_bst_layout(new_bst, left, width, top, height)
    key_node, path = bst.search(key)

    tracing_circle = Node(key=key, color=YELLOW)
    tracing_circle.next_to(shift_bst.search(path[0])[0], UP)

    # scene.add(*old_arrows.values(), *old_circles.values())

    scene.play(transform_bst(bst, shift_bst), FadeIn(tracing_circle))
    scene.wait()

    for node in path[1:]:
        scene.play(tracing_circle.animate.next_to(shift_bst.search(node)[0], UP))
        scene.wait()

    scene.play(transform_bst(bst, new_bst), Transform(tracing_circle, new_bst.search(key_node)[0]))
    scene.wait()

    # scene.play(FadeIn(new_bst.edges[key_node]))
    scene.wait()

    to_remove = [bst, tracing_circle, new_bst]

    return to_remove


def create_bst_weight(weight: str | LabeledDot, relative_node: Node, **kwargs) -> LabeledDot:
    params = {**WEIGHT_CONFIG, **{"fill_color": BST_WEIGHT_COLOR, "stroke_color": BST_WEIGHT_COLOR,
                                  "stroke_width": 0}}
    weight_mob = LabeledDot(label=MathTex(weight, fill_color=BST_WEIGHT_FONT_COLOR), **params).scale_to_fit_height(
        relative_node.height * BST_WEIGHT_SCALE) if isinstance(weight,
                                                               str) else weight
    weight_mob[1].scale(BST_WEIGHT_LABEL_SCALE)
    return weight_mob


def transform_bst(bst, target_bst, **kwargs) -> AnimationGroup:
    """Transforms the given BST to the target BST"""
    transform_bst_animations = []
    for node in bst.nodes:
        if node in target_bst.nodes:
            transform_bst_animations.append(Transform(bst.search(node)[0], target_bst.search(node)[0]))

        if node in target_bst.edges:
            transform_bst_animations.append(Transform(bst.edges[node], target_bst.edges[node]))

    return AnimationGroup(*transform_bst_animations, **kwargs)
