from __future__ import annotations

from .bst import *


class AVLNode(Node):
    def __init__(self, key=None, label=None, **kwargs):
        super().__init__(key, label, **kwargs)
        self.tree_height = 0
        self.hd = 0

    def __str__(self):
        return f"Node({self.key}, height={self.tree_height}, hd={self.hd})"

    def __repr__(self):
        return f"Node({self.key}, height={self.tree_height}, hd={self.hd})"


class SubTree(AVLNode):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.triangle = VGroup()
        self.triangle += Triangle(fill_color=DARK_GREY, stroke_color=VERTEX_STROKE_COLOR,
                                  stroke_width=VERTEX_STROKE_WIDTH, fill_opacity=1)

        a_node, b_node, c_node = Node(""), Node(""), Node("")
        b_node.shift(LEFT * 0.6 + DOWN)
        c_node.shift(RIGHT * 0.6 + DOWN)
        edge_a = Edge(a_node, b_node, stroke_color=LIGHTER_GREY, stroke_width=EDGE_STROKE_WIDTH * 0.7)
        edge_b = Edge(a_node, c_node, stroke_color=LIGHTER_GREY, stroke_width=EDGE_STROKE_WIDTH * 0.7)
        self.sub_tree = VGroup(a_node, b_node, c_node, edge_a, edge_b).set_z(1).move_to(self.triangle)

        self.dots = MathTex(r"\vdots").set_z(1).next_to(self.sub_tree, DOWN, buff=0.1)

        self.triangle.scale_to_fit_width(self.sub_tree.get_width() * 2)
        self.add(self.triangle, self.sub_tree, self.dots)


class AVLTree(BST):

    def __init__(self, keys: list = None, **kwargs):
        kwargs["node_type"] = AVLNode
        super().__init__(keys, **kwargs)

    def update_height(self, node: AVLNode):
        if node is None:
            return
        h_left = -1 if node.left is None else node.left.tree_height
        h_right = -1 if node.right is None else node.right.tree_height
        node.tree_height = max(h_left, h_right) + 1
        node.hd = h_left - h_right

    def left_rotate(self, node: AVLNode):
        pivot = node.right
        pivot.parent = node.parent
        if pivot.parent is not None:
            pivot.parent.left = pivot
        node.parent = pivot
        node.right = pivot.left
        pivot.left = node
        self.update_height(node)
        self.update_height(pivot)
        self.root = self.find_root(node)
        self.edges[(node, node.right)] = self.edges.pop((pivot, node.right))
        self.edges[(pivot, node)] = self.edges.pop((node, pivot))

        if pivot.parent is not None:
            self.edges[(pivot.parent, pivot)] = self.edges.pop((pivot.parent, node))

    def right_rotate(self, node: AVLNode):
        pivot = node.left
        pivot.parent = node.parent
        if pivot.parent is not None:
            pivot.parent.right = pivot
        node.parent = pivot
        node.left = pivot.right
        pivot.right = node
        self.update_height(node)
        self.update_height(pivot)
        self.root = self.find_root(node)
        self.edges[(node, node.left)] = self.edges.pop((pivot, node.left))
        self.edges[(pivot, node)] = self.edges.pop((node, pivot))

        if pivot.parent is not None:
            self.edges[(pivot.parent, pivot)] = self.edges.pop((pivot.parent, node))
        # TODO: updata start annd end edges?

    def balance(self, node: AVLNode):
        if node is None:
            return
        if node.hd == 2:
            if node.left.hd == -1:
                self.left_rotate(node.left)
            self.right_rotate(node)

        elif node.hd == -2:
            if node.right.hd == 1:
                self.right_rotate(node.right)
            self.left_rotate(node)

    def balance_up(self, node: AVLNode):
        while node is not None:
            self.update_height(node)
            if abs(node.hd) > 1:
                self.balance(node)
            node = node.parent

    def _insert_key(self, key: int | Node, node: Node = None, parent: Node = None, balance_up=False) -> Node:
        key_node = key if isinstance(key, self.node_type) else self.node_type(key)
        insert_node = super()._insert_key(key_node, node, parent)
        if balance_up:
            self.balance_up(key_node)
        return insert_node

    def insert_keys(self, keys: list | int, **kwargs):
        nodes = super().insert_keys(keys, **kwargs)
        return nodes
