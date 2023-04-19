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


class DrawOneBST(Scene):
    """Draws one binary search tree of 30 random numbers"""

    def construct(self):
        bst = BST(BASE_TREE_VERTICES)
        bst = BST(rnd.sample(range(30), 30))
        self.add(bst)
        self.wait()


class DrawManyBSTs(Scene):
    """Draws many binary search trees, transitioning between them"""

    def construct(self):
        bst = BST(rnd.sample(range(100), 30))
        position_bst_layout(bst)
        self.add(bst)
        self.wait()

        for i in range(30):
            new_bst = BST(rnd.sample(range(100), 30))
            position_bst_layout(bst)
            self.add(bst)
            self.play(Transform(bst, new_bst))
            self.wait()


class InsertOneElement(Scene):
    """Inserts a random element to a random BST of size 30"""

    def construct(self):
        random_list = rnd.sample(range(100), 31)
        insert_bst(self, BST(random_list[:-1]), random_list[-1])


class InsertAllElements(SectionsScene):
    """Builds a BST with a random list of elements"""

    def construct(self):
        # random_list = sample(range(20), 10)
        start_insert = 4
        random_list = [10, 5, 15, 7, 12, 6, 13, 8, 11]
        random_list = BASE_TREE_VERTICES[:start_insert + 5]
        bst = BST(random_list[:start_insert])
        bst.create_tree()
        self.add(bst)
        self.wait()
        fast_insert = True
        run_time_factor = 0.2 if fast_insert else 1

        for i in random_list[start_insert:]:
            self.next_section(f"Inserting key {i}", skip_section=fast_insert)
            new_key = bst.insert_keys([i])[0]
            path = bst.search(new_key)[1]
            new_key.next_to(bst.root, UP)
            self.play(Write(new_key), run_time=1 * run_time_factor)

            for node in path:
                if node.parent is not None and not fast_insert:
                    self.next_section("Wiggle weight", skip_section=fast_insert)
                    self.play(Wiggle(bst.edges[(node.parent, node)].weight_mob, scale_value=2, n_wiggles=14,
                                     rotation_angle=0.02 * TAU, run_time=2))
                self.play(new_key.animate(run_time=1 * run_time_factor).next_to(node, UP))

            self.play(bst.animate(run_time=1 * run_time_factor).update_tree_layout())
            new_edge = bst.create_edge(new_key.parent, new_key)
            new_edge.draw_edge(self, run_time=1.5 * run_time_factor)


if __name__ == "__main__":
    rnd.seed(1)
    # scenes_lst = [DrawOneBST]
    scenes_lst = [InsertAllElements]

    run_scenes(scenes_lst, OUT_DIR, PRESENTATION_MODE, DISABLE_CACHING, gif_scenes=[28 + i for i in range(6)])
