from __future__ import annotations

from tools.funcs import *
from tools.graphs.bst import *
from tools.scenes import *

ROOT_PATH = Path(__file__).resolve().parent.parent
sys.path.append(str(ROOT_PATH.parent.parent))
OUT_DIR = MEDIA_PATH / Path(__file__).resolve().parent.stem

PRESENTATION_MODE = False
DISABLE_CACHING = False
config.background_color = BACKGROUND_COLOR
# ----------------------------------    consts   ---------------------------------- #
NODE_INDICATE_COLOR = GREEN
MOVE_PATH_RUNTIME = 4
MOVE_PATH_WIDTH_FACTOR = 2
PATH_TIME_WIDTH = 0.6
# ----------------------------------    trees    ---------------------------------- #
LAYOUT_CONFIG = {"vertex_spacing": (1, 1.2)}

# BASE_TREE_VERTICES = [10, 13, 14, 20, 23, 25, 26, 28, 31, 31, 34]
BASE_TREE_VERTICES = [23, 14, 31, 10, 20, 25, 31, 13, 28, 34, 26]
BASE_TREE_EDGES = [(10, 13), (10, 14), (14, 20), (14, 23), (23, 31), (31, 25), (25, 28), (28, 26), (31, 31),
                   (31, 34)]


# ----------------------------------    BST scenes   ---------------------------------- #

class BSTScene(SectionsScene):
    def __init__(self, keys: list = None, bst: BST = None, **kwargs):
        super().__init__(**kwargs)
        self.bst = bst
        if self.bst is None:
            self.bst = BST(keys, tree_width=config.frame_width * 0.7, tree_left=-config.frame_width * 0.25)
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
        for node in path:
            animations = []
            if node.parent is not None and not fast_insert:
                self.next_section("Wiggle weight", skip_section=fast_insert)
                animations.append(self.bst.edges[(node.parent, node)].animate(
                    run_time=0.001).fix_z_index())  # TODO: create wiggle anim
                animations.append(Wiggle(self.bst.edges[(node.parent, node)].weight_mob, scale_value=2, n_wiggles=14,
                                         rotation_angle=0.02 * TAU, run_time=2))
            animations.append(new_key.animate(run_time=1 * run_time_factor).next_to(node, UP))
            self.play(AnimationGroup(*animations, lag_ratio=0.8, suspend_mobject_updating=False))

        self.play(self.bst.animate(run_time=1 * run_time_factor).update_tree_layout())
        new_edge = self.bst.create_edge(new_key.parent, new_key)
        self.play(new_edge.draw_edge(run_time=1.5 * run_time_factor))

    def animate_delete_key(self, key: int, fast_delete: bool = False):
        run_time_factor = 0.2 if fast_delete else 1
        self.next_section(f"Deleting key {key}", skip_section=fast_delete)
        key_node = self.bst.search(key)[0]
        if key_node is None:
            return
        minimum_scenario = key_node.left is not None and key_node.right is not None
        if minimum_scenario:
            self.play(self.animate_minimum_find(key_node.right, run_time_factor))
        self.bst.remove_updater(self.bst.update_edges)
        key, min_key, remove_edge, update_edge = self.bst.delete_key(key)
        if key is not None:
            self.add(key)
        if remove_edge is not None:
            self.add(remove_edge)

        remove_key_anim = []
        remove_key_anim.append(Unwrite(key, run_time=1 * run_time_factor))
        if min_key is not None:
            remove_key_anim.append(min_key.animate(run_time=1 * run_time_factor).move_to(key.get_center()))
        self.play(AnimationGroup(*remove_key_anim, lag_ratio=0.8))
        if remove_edge is not None:
            self.play(Unwrite(remove_edge), run_time=1 * run_time_factor)
        if update_edge is not None:
            self.play(
                update_edge.animate(run_time=1 * run_time_factor).put_start_and_end_on(update_edge.start.get_center(),
                                                                                       update_edge.end.get_center()))
        if minimum_scenario:
            self.play(min_key.animate(run_time=1 * run_time_factor).set_color(fill_color=VERTEX_COLOR,
                                                                              stroke_color=VERTEX_STROKE_COLOR))
        self.bst.add_updater(self.bst.update_edges)
        self.play(self.bst.animate.update_tree_layout(), run_time=1 * run_time_factor)

    def animate_minimum_find(self, node: Node, run_time_factor: float, **kwargs) -> AnimationGroup:

        animations_lst = []
        while node.left is not None:
            # flash_color = YELLOW if node.left.left is None or node == start_node else NODE_INDICATE_COLOR
            mini_anim = []
            mini_anim.append(
                self.bst.edges[(node, node.left)].animate_move_along_path(flash_color=NODE_INDICATE_COLOR,
                                                                          width_factor=MOVE_PATH_WIDTH_FACTOR,
                                                                          run_time=MOVE_PATH_RUNTIME * run_time_factor,
                                                                          time_width=PATH_TIME_WIDTH))
            mini_anim.append(
                IndicateNode(node, color_theme="green", run_time=1 * run_time_factor))
            animations_lst.append(AnimationGroup(*mini_anim, lag_ratio=0.15 * run_time_factor))
            node = node.left
        animations_lst.append(
            IndicateNode(node, run_time=1 * run_time_factor, scale_factor=1.5, preserve_indicate_color=True))
        return AnimationGroup(*animations_lst, lag_ratio=0.5 * run_time_factor, **kwargs)


class CheckBSTInsert(BSTScene):
    def __init__(self, **kwargs):
        keys = BASE_TREE_VERTICES[:5]
        super().__init__(keys=keys, **kwargs)

    def construct(self):
        super().construct()
        for key in BASE_TREE_VERTICES[5:8]:
            self.animate_key_insert(key)


class CheckBSTDelete(BSTScene):
    def __init__(self, **kwargs):
        keys = BASE_TREE_VERTICES
        super().__init__(keys=keys, **kwargs)

    def construct(self):
        super().construct()
        self.animate_delete_key(23)
        # self.animate_delete_key(25)
        # self.animate_delete_key(34)
        # self.animate_delete_key(10)


if __name__ == "__main__":
    scenes_lst = [CheckBSTInsert]
    # scenes_lst = [CheckBSTDelete]

    run_scenes(scenes_lst, OUT_DIR, PRESENTATION_MODE, DISABLE_CACHING, gif_scenes=[28 + i for i in range(6)])
