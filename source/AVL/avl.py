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

class AVLScene(BSTScene):
    def __init__(self, keys: list = None, bst: BST = None, **kwargs):
        self.avl = AVLTree(keys, tree_width=config.frame_width * 0.7, tree_left=-config.frame_width * 0.25)
        super().__init__(keys, bst, **kwargs)
        self.avl.create_tree()
        self.add(self.avl)

    def construct(self):
        self.next_section("AVL Tree")
        sel

class AVLRotation(SectionsScene):

    def construct(self):
        sub_tree = SubTree()
        self.add(sub_tree.scale(0.5))
        self.play(sub_tree.animate(run_time=1).shift(LEFT * 3))


if __name__ == "__main__":
    # scenes_lst = [CheckBSTInsert]
    scenes_lst = [AVLScene]

    run_scenes(scenes_lst, OUT_DIR, PRESENTATION_MODE, DISABLE_CACHING, gif_scenes=[28 + i for i in range(6)])
