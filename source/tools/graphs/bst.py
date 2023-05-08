from __future__ import annotations

from .node import *
from .edge import *

BST_WEIGHT_COLOR = WHITE
BST_WEIGHT_FONT_COLOR = BLACK


# BST_WEIGHT_COLOR = BACKGROUND_COLOR
# BST_WEIGHT_FONT_COLOR = WHITE

class BST(VGroup):
    """Class that represents a full binary search tree"""

    def __init__(self, keys: list = None, weighted: bool = True, layout=None, tree_left=-config.frame_width / 2,
                 tree_width=config.frame_width, tree_top=config.frame_height / 2, tree_height=config.frame_height,
                 extra_space_at_top=False, node_type=Node, **kwargs):
        super().__init__(**kwargs)
        self.root = None
        self.edges = {}  # edges are not added as a group. They are added one by one to the scene when they are created.
        self.nodes = VGroup()  # same as edges.
        self.weighted = weighted
        self.layout = layout
        self.tree_left = tree_left  # the leftmost x-coordinate of the bounding box.
        self.tree_width = tree_width
        self.tree_top = tree_top
        self.tree_height = tree_height
        self.extra_space_at_top = extra_space_at_top
        self.node_type = node_type
        if keys is not None:
            self.insert_keys(keys, set_root=True)
            self.create_tree()
        self.add_updater(self.update_edges)

    def _insert_key(self, key: int | Node, node: Node = None, parent: Node = None) -> Node:
        if node is None:
            ret_key = key if isinstance(key, Node) else self.node_type(key)
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
            self.transplant(key, key.right)
            remove_edge, update_edge = self.update_transplant_edges(key, key.right)
        elif key.right is None:
            self.transplant(key, key.left)
            remove_edge, update_edge = self.update_transplant_edges(key, key.left)
        else:
            y = min_key = self.minimum(key.right)
            remove_edge = self.edges.pop((y, y.right), None)
            if y.parent != key:
                self.transplant(y, y.right)
                tmp_rem, update_edge = self.update_transplant_edges(y, y.right)
                remove_edge = remove_edge if remove_edge is not None else tmp_rem
                y.right = key.right
                y.right.parent = y
            self.transplant(key, y)
            y.left = key.left
            y.left.parent = y

            if y.right is not None:
                self.edges[(y, y.right)] = self.edges.pop((key, key.right))
            if y.left is not None:
                self.edges[(y, y.left)] = self.edges.pop((key, key.left))

        self.nodes.remove(key)
        self.remove(remove_edge)
        self.remove(key)
        return key, min_key, remove_edge, update_edge

    def update_transplant_edges(self, key: Node, child: Node):
        update_edge, remove_edge = None, None
        if child is not None:
            remove_edge = self.edges.pop((key, child), None)
            update_edge = self.edges.pop((key.parent, key))
            update_edge.end = child
            update_edge.parent = child.parent
            self.edges[(child.parent, child)] = update_edge
        else:
            remove_edge = self.edges.pop((key.parent, key), None)
        return remove_edge, update_edge

    def transplant(self, u: Node, v: Node):
        if u.parent is None:
            self.root = v
            self.root.parent = None
            return
        elif u == u.parent.left:
            u.parent.left = v
        else:
            u.parent.right = v
        # if (u.parent, u) in self.edges:
        #     update_edge = self.edges.pop((u.parent, u))
        #     if v is not None:
        #         update_edge.end = v
        #         self.edges[(u.parent, v)] = update_edge
        if v is not None:
            v.parent = u.parent
            # return update_edge

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

    def set_layout(self):
        """
        Positions the nodes of the given binary search tree in a way that
        minimizes overlap and maximizes horizontal distance.
        :param bst: the binary search tree to position.
        :return:
        """
        relative_cols_positions = {}

        get_column_positions_from_root(self.root, 0, relative_cols_positions)

        eliminate_overlap(self.root, relative_cols_positions, self)

        num_cols = max(relative_cols_positions.values()) - min(relative_cols_positions.values()) + 1
        horiz_increment = self.tree_width / (num_cols + 1)
        vert_increment = self.tree_height / (get_depth(self.root) + 1 + self.extra_space_at_top)
        minimum_position = min(relative_cols_positions.values())

        if self.extra_space_at_top:
            self.tree_top -= vert_increment

        def locate_nodes(current_node: Node, depth: int, layout: dict[Node, np.ndarray]):
            """Converts the relative horizontal coordinates to circle objects in the canvas"""
            x_coord = self.tree_left + (relative_cols_positions[current_node] - minimum_position + 1) * horiz_increment
            y_coord = self.tree_top - (depth + 1) * vert_increment
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
