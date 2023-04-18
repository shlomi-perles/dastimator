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
        self.parent = None
        self.tree_height = tree_height


class Edge(Line):
    """Simple class that represents a BST edge"""

    def __init__(self, start: Node, end: Node, weight: str | int | VMobject = None, **kwargs):
        super().__init__(start.get_center(), end.get_center(), **kwargs)
        self.start = start
        self.end = end

        if weight is not None:
            self.weight = weight if not isinstance(weight, VMobject) else weight[1].tex_string
            self.weight_mob = weight if isinstance(weight, VMobject) else LabeledDot(
                label=MathTex(weight, fill_color=WEIGHT_LABEL_FONT_COLOR), **WEIGHT_CONFIG)

            if weight is not isinstance(weight, VMobject):
                self.weight_mob.scale(WEIGHT_SCALE)
                self.weight_mob[1].scale(WEIGHT_LABEL_SCALE)

            self.weight_mob.move_to(self.get_center())
            self.add(self.weight_mob)


class BST(VGroup):
    """Class that represents a full binary search tree"""

    def __init__(self, keys: list = None, weighted: bool = True, layout=None, **kwargs):
        super().__init__(**kwargs)
        self.root = None
        self.edges = {}
        self.nodes = VGroup()
        self.weighted = weighted
        self.layout = layout
        if keys is not None:
            self.insert_keys(keys)
            self.create_tree()
        self.add_updater(self.update_edges)

    def get_height(self):
        return max(self.nodes, key=lambda node: node.tree_height).tree_height

    def _insert_key(self, key: int | Node, node: Node = None, parent: Node = None, tree_height: int = 0) -> Node:
        if node is None:
            ret_key = key if isinstance(key, Node) else Node(key, tree_height=tree_height)
            if parent != None:
                ret_key.parent = parent
                # self.create_edge(parent, ret_key)
            self.nodes += ret_key
            self.add(ret_key)
            return ret_key

        key_val = key.key if isinstance(key, Node) else key
        if key_val < node.key:
            node.left = self._insert_key(key, node.left, parent=node, tree_height=tree_height + 1)
        else:
            node.right = self._insert_key(key, node.right, parent=node, tree_height=tree_height + 1)
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

    def traverse(self, func, **kwargs):
        """Traverses the tree in a depth-first manner"""
        self.traverse_sub_tree(self.root, func, **kwargs)

    def traverse_sub_tree(self, node: Node, func, **kwargs):
        if node is None:
            return
        func(node, **kwargs)
        if "depth" in kwargs:
            kwargs["depth"] += 1
        self.traverse_sub_tree(node.left, func, **kwargs)
        self.traverse_sub_tree(node.right, func, **kwargs)

    # ----------------- Layout ----------------- #

    def create_layout(self, left=-config.frame_width / 2, width=config.frame_width, top=config.frame_height / 2,
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

        get_column_positions_from_root(self.root, 0, relative_cols_positions)

        eliminate_overlap(self.root, relative_cols_positions, self)

        num_cols = max(relative_cols_positions.values()) - min(relative_cols_positions.values()) + 1
        horiz_increment = width / (num_cols + 1)
        vert_increment = height / (get_depth(self.root) + 1 + extra_space_at_top)
        minimum_position = min(relative_cols_positions.values())

        if extra_space_at_top:
            top -= vert_increment

        def locate_nodes(current_node: Node, depth: int, layout: dict[Node, np.ndarray]):
            """Converts the relative horizontal coordinates to circle objects in the canvas"""
            x_coord = left + (relative_cols_positions[current_node] - minimum_position + 1) * horiz_increment
            y_coord = top - (depth + 1) * vert_increment
            layout[current_node] = RIGHT * x_coord + UP * y_coord

        self.layout = {}
        self.traverse(locate_nodes, depth=0, layout=self.layout)

    # ----------------- Draw ----------------- #

    def create_tree(self):
        """Creates the tree from the root node"""
        if self.layout is None:
            self.create_layout()

        self.update_nodes()

        for node in self.nodes:
            for child in [n for n in [node.left, node.right] if n is not None]:
                if (node, child) not in self.edges:
                    self.create_edge(node, child)
        # self.traverse(self.create_edge)

    def create_edge(self, node, child, **kwargs):
        edge_params = dict(start=node, end=child, buff=0, z_index=-10)
        if self.weighted:
            edge_params["weight"] = create_bst_weight("<" if node.left is child else r"\geq", node)
        self.edges[(node, child)] = Edge(**edge_params)
        self.add(self.edges[(node, child)])

    def update_nodes(self):
        for node in self.nodes:
            node.move_to(self.layout[node])

    def update_layout(self):
        self.create_layout()
        self.update_nodes()

    def update_edges(self, graph):
        for (u, v), edge in graph.edges.items():
            # self.create_edge(u, v)
            edge.put_start_and_end_on(u.get_center(), v.get_center())
            if self.weighted:
                edge.weight_mob.move_to(edge.get_center())


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

    def update_depth_col(node: Node, depth: int, depth_to_most_col: dict[int, int], rightmost: bool,
                         relative_positions: dict[Node, int], **kwargs):
        operator = max if rightmost else min

        depth_to_most_col[depth] = operator(depth_to_most_col[depth], relative_positions[
            node]) if depth in depth_to_most_col.keys() else relative_positions[node]

    bst.traverse_sub_tree(current_node.left, update_depth_col, depth=0, depth_to_most_col=rightmost_in_left,
                          rightmost=True, relative_positions=relative_positions)
    bst.traverse_sub_tree(current_node.right, update_depth_col, depth=0, depth_to_most_col=leftmost_in_right,
                          rightmost=False, relative_positions=relative_positions)

    overlap_given_depth = {depth: rightmost_in_left[depth] - leftmost_in_right[depth]
                           for depth in set(rightmost_in_left.keys()).intersection(leftmost_in_right.keys())}

    if len(overlap_given_depth) == 0:
        return

    amount_to_shift = max(overlap_given_depth.values()) / 2 + 1

    shift_tree_cols(bst, amount_to_shift, relative_positions, current_node)


def shift_tree_cols(bst: BST, amount_to_shift: float, relative_positions: dict[Node, int], node=None):
    """Shifts the entire tree to the right by some given amount (could be negative)"""
    node = node if node is not None else bst.root
    shift_func = lambda pos_node, amount_to_shift, **kwargs: relative_positions.update(
        {pos_node: relative_positions[pos_node] + amount_to_shift})
    bst.traverse_sub_tree(node.left, shift_func, amount_to_shift=- amount_to_shift)
    bst.traverse_sub_tree(node.right, shift_func, amount_to_shift=amount_to_shift)


def insert_bst(scene: Scene, bst: BST, key: int, left=-7, width=14, top=4, height=8):
    """Inserts the given key to the BST and animates the process"""
    # position_bst_layout(bst, left, width, top, height)
    shift_bst = bst.copy()
    # old_scale = position_bst_layout(shift_bst, left, width, top, height, True)

    bst.insert_keys(key)
    new_bst = bst.copy()
    # new_scale = position_bst_layout(new_bst, left, width, top, height)
    new_bst.create_tree()
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
