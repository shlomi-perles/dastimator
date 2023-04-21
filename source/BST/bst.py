from __future__ import annotations

from typing import Hashable

from manim_editor import PresentationSectionType as pst

from tools.array import *
from tools.consts import *
from tools.funcs import *
from tools.bst import *
from tools.scenes import *
from tools.my_graphs import DiGraph
import random as rnd

ROOT_PATH = Path(__file__).resolve().parent.parent
sys.path.append(str(ROOT_PATH.parent.parent))
OUT_DIR = MEDIA_PATH / Path(__file__).resolve().parent.stem

PRESENTATION_MODE = False
DISABLE_CACHING = False
config.background_color = BACKGROUND_COLOR

# ----------------------------------    trees    ---------------------------------- #
LAYOUT_CONFIG = {"vertex_spacing": (1, 1.2)}

# BASE_TREE_VERTICES = [10, 13, 14, 20, 23, 25, 26, 28, 31, 31, 34]
BASE_TREE_VERTICES = [23, 14, 31, 10, 20, 25, 31, 13, 28, 34, 26]
BASE_TREE_EDGES = [(10, 13), (10, 14), (14, 20), (14, 23), (23, 31), (31, 25), (25, 28), (28, 26), (31, 31),
                   (31, 34)]


# ----------------------------------    BST scenes   ---------------------------------- #

class BSTScene(SectionsScene):
    def __init__(self, keys: list = None, **kwargs):
        super().__init__(**kwargs)
        self.bst = BST(keys)
        self.bst.create_tree()
        self.add(self.bst)

    def construct(self):
        pass

    def animate_key_insert(self, key: int, fast_insert: bool = False):
        run_time_factor = 0.2 if fast_insert else 1
        self.next_section(f"Inserting key {key}", skip_section=fast_insert)
        new_key = self.bst.insert_keys([key])[0]
        path = self.bst.search(new_key)[1]
        new_key.next_to(self.bst.root, UP)
        self.play(Write(new_key), run_time=1 * run_time_factor)
        animations = []
        for node in path:
            if node.parent is not None and not fast_insert:
                self.next_section("Wiggle weight", skip_section=fast_insert)
                animations.append(self.bst.edges[(node.parent, node)].animate(run_time=0.001).fix_z_index())
                animations.append(Wiggle(self.bst.edges[(node.parent, node)].weight_mob, scale_value=2, n_wiggles=14,
                                         rotation_angle=0.02 * TAU, run_time=2))
            animations.append(new_key.animate(run_time=1 * run_time_factor).next_to(node, UP))
            self.play(AnimationGroup(*animations, lag_ratio=0.5, suspend_mobject_updating=False))

        self.play(self.bst.animate(run_time=1 * run_time_factor).update_tree_layout())
        new_edge = self.bst.create_edge(new_key.parent, new_key)
        new_edge.draw_edge(self, run_time=1.5 * run_time_factor)

    def delete_key(self, key: int, fast_delete: bool = False):
        run_time_factor = 0.2 if fast_delete else 1
        self.next_section(f"Deleting key {key}", skip_section=fast_delete)
        node = self.bst.delete_key(key)
        if node.right is not None and node.left is not None:
            pass
        edge_to_delete = self.bst.edges[(node.parent, node)]
        edge_to_update = self.bst.edges[(node, node.right_child)] if node.right_child is not None else None
        self.play(node.animate(run_time=1 * run_time_factor).set_color(RED))
        self.play(node.animate(run_time=1 * run_time_factor).set_color(WHITE))
        self.bst.delete_key(key)
        self.play(self.bst.animate(run_time=1 * run_time_factor).update_tree_layout())
        self.next_section(f"Key {key} deleted", skip_section=fast_delete)


class SimpleBST(BSTScene):
    def __init__(self, **kwargs):
        keys = BASE_TREE_VERTICES[:5]
        super().__init__(keys=keys, **kwargs)

    def construct(self):
        super().construct()
        for key in BASE_TREE_VERTICES[5:7]:
            self.animate_key_insert(key)


if __name__ == "__main__":
    rnd.seed(1)
    # scenes_lst = [DrawOneBST]
    scenes_lst = [SimpleBST]

    run_scenes(scenes_lst, OUT_DIR, PRESENTATION_MODE, DISABLE_CACHING, gif_scenes=[28 + i for i in range(6)])
