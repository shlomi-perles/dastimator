from __future__ import annotations

from tools.funcs import *
from tools.graphs.avl_tree import *
from BST.bst import *

ROOT_PATH = Path(__file__).resolve().parent.parent
sys.path.append(str(ROOT_PATH.parent.parent))
OUT_DIR = MEDIA_PATH / Path(__file__).resolve().parent.stem

PRESENTATION_MODE = False
DISABLE_CACHING = False
config.background_color = BACKGROUND_COLOR
HD_TO_COLOR = {0: "blue", 1: "yellow", 2: "red"}


class AVLScene(BSTScene):
    def __init__(self, keys: list = None, **kwargs):
        self.avl = AVLTree(keys, tree_width=config.frame_width * 0.7, tree_left=-config.frame_width * 0.25)
        super().__init__(bst=self.avl, **kwargs)

    def update_height(self, node: AVLNode, **kwargs):
        indicate_animations = []
        while node is not None:
            old_hd = node.hd
            self.avl.update_height(node)
            if node.hd != old_hd:
                indicate_animations.append(
                    IndicateNode(node, color_theme=HD_TO_COLOR[abs(node.hd)], preserve_indicate_color=True))
            node = node.parent

        if indicate_animations:
            self.play(AnimationGroup(*indicate_animations, **kwargs))

    def construct(self):
        pass


class AVLRotation(AVLScene):
    def __init__(self, **kwargs):
        keys = [0, 4, 2, 1, 3, 5]
        super().__init__(keys, **kwargs)

    def construct(self):
        self.next_section("AVL Rotation")
        self.update_height(self.avl.nodes[-1], lag_ratio=0.5, run_time=3)
        self.rotate_right(self.avl.nodes[1])
        # self.avl.right_rotate(self.avl.nodes[0])
        # self.play(self.avl.animate.update_tree_layout())
        # self.play(self.avl.edges[(self.avl.nodes[0], self.avl.nodes[0].left)].animate.shift(RIGHT))

    def rotate_right(self, node: AVLNode, run_time_factor=1, fast_rotate: bool = False):
        animations = []
        self.avl.remove_updater(self.avl.update_edges)
        self.avl.edges[(node.left, node.left.right)].start = node
        self.play(
            self.avl.edges[(node.left, node.left.right)].animate(run_time=1 * run_time_factor).put_start_and_end_on(
                node.get_center(), node.left.right.get_center()))

        self.next_section(f"update edge weight")
        self.play(self.avl.edges[(node.left, node.left.right)].set_weight(create_bst_weight(r"<", node),
                                                                          run_time=1 * run_time_factor))
        self.next_section(f"update parent edge")
        if node.parent is not None:
            self.play(
                self.avl.edges[(node.parent, node)].animate(run_time=1 * run_time_factor).put_start_and_end_on(
                    node.parent.get_center(), node.left.get_center()))

        self.play(self.avl.edges[(node, node.left)].set_weight(create_bst_weight(r"\geq", node),
                                                               run_time=1 * run_time_factor))

        self.avl.add_updater(self.avl.update_edges)
        self.avl.right_rotate(node)

        self.play(node.animate(run_time=0.0001).shift(RIGHT * 0))  # dont move this magic line

        self.play(self.avl.animate(run_time=1 * run_time_factor).update_tree_layout(relative_to_root=True))


class AVLBalanceCheck(AVLScene):
    def __init__(self, **kwargs):
        keys = [2, 1, 3, 4, 5]
        super().__init__(keys, **kwargs)

    def construct(self):
        self.next_section("AVL Tree")
        self.update_height(self.avl.nodes[-1], lag_ratio=0.5, run_time=3)
        last_edge = self.avl.edges[(self.avl.nodes[-2], self.avl.nodes[-1])]
        # self.play(last_edge.animate_move_along_path(time_width=PATH_TIME_WIDTH * 2, preserve_state=True, run_time=3))
        self.animate_key_insert(6, show_path=True)
        self.wait()


if __name__ == "__main__":
    scenes_lst = [AVLRotation]

    run_scenes(scenes_lst, OUT_DIR, PRESENTATION_MODE, DISABLE_CACHING, gif_scenes=[28 + i for i in range(6)])
