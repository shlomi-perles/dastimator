from __future__ import annotations

from typing import Hashable, Iterable, Optional, Tuple, Union, List, Any
from .consts import *

BST_WEIGHT_COLOR = WHITE
BST_WEIGHT_FONT_COLOR = BLACK

# BST_WEIGHT_COLOR = BACKGROUND_COLOR
# BST_WEIGHT_FONT_COLOR = WHITE

NODES_RELATIVE_HEIGHT = config.frame_height * 0.09


class Node(LabeledDot):
    """Simple class that represents a BST node"""

    def __init__(self, key=None, label=None, relative_height=None, **kwargs):
        if label is not isinstance(label, SVGMobject) and label is not None:
            label = MathTex(label, fill_color=LABEL_COLOR)
        label_scale = kwargs.pop("label_scale", VERTEX_LABEL_SCALE)
        kwargs = {**VERTEX_CONFIG, **kwargs}
        super().__init__(label=MathTex(key, fill_color=LABEL_COLOR) if label is None else label, **kwargs)
        self.scale_to_fit_height(NODES_RELATIVE_HEIGHT if relative_height is None else relative_height)
        self[1].scale(label_scale)
        self.label = self[1]
        self.key = label if key is None else key
        self.left = None
        self.right = None
        self.parent = None

    def indicate(self, scene: Scene, **kwargs):
        self.remove(self.label)
        scene.add(self.label)
        self.label.set_z_index(self.z_index + 1)

        def on_finish(scene: Scene):
            scene.remove(self.label)
            self.label.set_z_index(self.z_index)
            self.add(self.label)

        label_kwargs = {k: v for k, v in kwargs.items() if k != "color"}
        return AnimationGroup(Indicate(self, **kwargs), Indicate(self.label, color=self.label.color, **label_kwargs),
                              group=self, _on_finish=on_finish)

    def __str__(self):
        return str(self.key)

    def __lt__(self, other):
        if isinstance(other, Node):
            return self.key < other.key
        if isinstance(other, (float, int)):
            return self.key < other
        return False

    def __gt__(self, other):
        if isinstance(other, Node):
            return self.key > other.key
        if isinstance(other, (float, int)):
            return self.key > other
        return False

    def __le__(self, other):
        if isinstance(other, Node):
            return self.key <= other.key
        if isinstance(other, (float, int)):
            return self.key <= other
        return False

    def __ge__(self, other):
        if isinstance(other, Node):
            return self.key >= other.key
        if isinstance(other, (float, int)):
            return self.key >= other
        return False


class Edge(VGroup):
    """Simple class that represents a BST edge"""

    def __init__(self, start: Node, end: Node, weight: str | int | VMobject = None, **kwargs):
        self.edge = Line(start.get_center(), end.get_center(), **kwargs)
        self.start = start
        self.end = end

        if weight is not None:
            self.weight = weight if not isinstance(weight, VMobject) else weight[1].tex_string
            self.weight_mob = weight if isinstance(weight, VMobject) else LabeledDot(
                label=MathTex(weight, fill_color=WEIGHT_LABEL_FONT_COLOR), **WEIGHT_CONFIG)

            self.update_weight(self)
            self.add(self.weight_mob)
            self.add_updater(self.update_weight)

    def __str__(self):
        return f"Edge({self.start.key}, {self.end.key}{(',' + self.weight) if self.weight is not None else ''})"

    def put_start_and_end_on(self, start, end):
        self.fix_z_index()
        weight = self.weight_mob
        self.remove(self.weight_mob)
        self.weight_mob = None
        super().put_start_and_end_on(start, end)
        self.add(weight)
        self.weight_mob = weight

    def update_weight(self, edge):
        self.move_to(self)
        if self.weight_mob is not None:
            self.weight_mob.move_to(edge.get_center())

    def draw_edge(self, scene: Scene, relative_line_run_time=0.3, run_time=1.5, **kwargs):
        weight = self.weight_mob
        self.remove(self.weight_mob)
        self.weight_mob = None
        scene.play(FadeIn(self), run_time=relative_line_run_time * run_time, **kwargs)
        self.add(weight)
        self.weight_mob = weight
        scene.play(Write(self.weight_mob), run_time=run_time * (1 - relative_line_run_time), **kwargs)

    def fix_z_index(self):
        self.start.set_z_index(1)
        self.start.label.set_z_index(2)
        self.end.set_z_index(1)
        self.end.label.set_z_index(2)
        self.set_z_index(0)

    def animate_move_along_path(self, scene: Scene, flash_color=VISITED_COLOR, width_factor=1, **kwargs):
        self.fix_z_index()
        self.remove(self.weight_mob)
        scene.add(self.weight_mob)
        self.weight_mob.set_z_index(self.z_index + 1)

        def on_finish(scene: Scene):
            scene.remove(self.weight_mob)
            self.weight_mob.set_z_index(self.z_index)
            self.add(self.weight_mob)

        return AnimationGroup(
            ShowPassingFlash(self.copy().set_color(flash_color).set_stroke_width(width_factor * self.stroke_width),
                             **kwargs), group=self, _on_finish=on_finish)


class BST(VGroup):
    """Class that represents a full binary search tree"""

    def __init__(self, keys: list = None, weighted: bool = True, layout=None, **kwargs):
        super().__init__(**kwargs)
        self.root = None
        self.edges = {}  # edges are not added as a group. They are added one by one to the scene when they are created.
        self.nodes = VGroup()  # same as edges.
        self.weighted = weighted
        self.layout = layout
        if keys is not None:
            self.insert_keys(keys, set_root=True)
            self.create_tree()
        self.add_updater(self.update_edges)

    def _insert_key(self, key: int | Node, node: Node = None, parent: Node = None) -> Node:
        if node is None:
            ret_key = key if isinstance(key, Node) else Node(key)
            if parent != None:
                ret_key.parent = parent
            self.nodes += ret_key
            self.add(ret_key)
            return ret_key

        if key < node:
            node.left = self._insert_key(key, node.left, parent=node)
        else:
            node.right = self._insert_key(key, node.right, parent=node)
        return node

    def insert_keys(self, keys: list | int, set_root=False):
        """Inserts a list of keys into the BST recursively"""
        keys = [keys] if isinstance(keys, int) else keys
        nodes = []
        for key in keys:
            node = self._insert_key(key, self.root)
            if set_root:
                self.root = node
                set_root = False
            nodes.append(self.nodes[-1])
        return nodes

    def search(self, key: int | Node) -> tuple[Node | None, list[Any]]:
        """Returns a list of nodes containing the path from root to target node"""
        path = []

        def search_helper(node: Node, key: int) -> Optional[Node]:
            if node is None:
                return None
            path.append(node)
            if key < node:
                return search_helper(node.left, key)
            elif key > node:
                return search_helper(node.right, key)
            elif node.right is not None and node.right.key == key:
                return search_helper(node.left, key)
            else:
                return node

        return search_helper(self.root, key), path[:-1]

    def delete_key(self, key: Node | float | int) -> tuple[Node | None, Node | None, Edge | None, Edge | None] | None:
        # TODO: update heights and remove edges and node from self and self.edges
        """Deletes the node with the given key from the tree"""
        remove_edge, update_edge, min_key = None, None, None
        key = key if isinstance(key, Node) else self.search(key)[0]
        if key is None:
            return

        if key.left is None:
            update_edge = self.transplant(key, key.right)
            remove_edge = self.edges.pop((key, key.right), None)
        elif key.right is None:
            update_edge = self.transplant(key, key.left)
            remove_edge = self.edges.pop((key, key.left), None)
        else:
            y = min_key = self.minimum(key.right)
            remove_edge = self.edges.pop((y, y.right), None)
            if y.parent != key:
                update_edge = self.transplant(y, y.right)
                y.right = key.right
                y.right.parent = y
            self.transplant(key, y)
            y.left = key.left
            y.left.parent = y

        self.nodes.remove(key)
        self.remove(remove_edge)
        self.remove(key)
        return key, min_key, remove_edge, update_edge

    def transplant(self, u: Node, v: Node) -> Edge | None:
        update_edge = None
        if u.parent is None:
            self.root = v
            self.root.parent = None
            return
        elif u == u.parent.left:
            u.parent.left = v
        else:
            u.parent.right = v
        if (u.parent, u) in self.edges:
            update_edge = self.edges.pop((u.parent, u))
            update_edge.end = v
            self.edges[(u.parent, v)] = update_edge
        if v is not None:
            v.parent = u.parent
        return update_edge

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

    def minimum(self, node: Node) -> Node:
        """Returns the minimum node in the sub-tree"""
        while node.left is not None:
            node = node.left
        return node

    # ----------------- Layout ----------------- #

    def set_layout(self, left=-config.frame_width / 2, width=config.frame_width, top=config.frame_height / 2,
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
        """Creates the tree layout and edges and updates the nodes"""
        if self.layout is None:
            self.set_layout()

        self.update_nodes()

        for node in self.nodes:
            for child in [n for n in [node.left, node.right] if n is not None]:
                if (node, child) not in self.edges:
                    self.create_edge(node, child)

    def create_edge(self, node, child, **kwargs):
        edge_params = dict(start=node, end=child, buff=0, z_index=-10)
        if self.weighted:
            edge_params["weight"] = create_bst_weight("<" if node.left is child else r"\geq", node)
        self.edges[(node, child)] = Edge(**edge_params)
        self.add(self.edges[(node, child)])
        return self.edges[(node, child)]

    def update_nodes(self):
        """Updates the nodes to their new positions in the layout"""
        for node in self.nodes:
            node.move_to(self.layout[node])

    def update_tree_layout(self):
        self.set_layout()
        self.update_nodes()

    def update_edges(self, graph):
        for (u, v), edge in graph.edges.items():
            edge.fix_z_index()
            if edge.weight_mob is not None:
                edge.remove(edge.weight_mob)
            edge.put_start_and_end_on(u.get_center(), v.get_center())
            if edge.weight_mob is not None:
                edge.add(edge.weight_mob)
            if self.weighted and edge.weight_mob is not None:
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


def create_bst_weight(weight: str | LabeledDot, relative_node: Node, **kwargs) -> LabeledDot:
    params = {**WEIGHT_CONFIG, **{"fill_color": BST_WEIGHT_COLOR, "stroke_color": BST_WEIGHT_COLOR,
                                  "stroke_width": 0}}
    weight_mob = LabeledDot(label=MathTex(weight, fill_color=BST_WEIGHT_FONT_COLOR), **params).scale_to_fit_height(
        relative_node.height * WEIGHT_SCALE) if isinstance(weight,
                                                           str) else weight
    weight_mob[1].scale(WEIGHT_LABEL_SCALE)
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
