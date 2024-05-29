"""
TODO: For next time: 1. Maybe for successor scale up all nodes bigger than successor
 and then scale down all nodes smaller than successor.
TODO: 2. When delete node with 1 child, move all his subtree to the parent and then change the edge.Not the other way around.
TODO: 3. Break down the main scene into smaller scenes.
"""
from __future__ import annotations

from tools.movie_maker import render_scenes
from tools.scenes import *
from tools.funcs import *
from tools.graphs.bst import *

ROOT_PATH = Path(__file__).resolve().parent.parent
sys.path.append(str(ROOT_PATH.parent.parent))
OUT_DIR = MEDIA_PATH / Path(__file__).resolve().parent.stem

PRESENTATION_MODE = True
DISABLE_CACHING = False
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
        # self.add(self.bst)

    def animate_find(self, key: int, fast_find: bool = False, show_path=False, **kwargs):
        run_time_factor = 0.2 if fast_find else 1
        self.next_section(f"Inserting key {key}", skip_section=fast_find)
        real_key, path = self.bst.search(key)
        new_key = real_key.copy()
        if path[-1] is None:
            path.pop()

        new_key.next_to(self.bst.root, UP)
        self.play(Write(new_key), run_time=1 * run_time_factor)
        for node in path:
            animations = []
            if node.parent is not None and not fast_find:
                self.next_section("Wiggle weight", skip_section=fast_find)
                animations.append(self.bst.edges[(node.parent, node)].animate(
                    run_time=0.001).fix_z_index())  # TODO: create wiggle anim
                animations.append(Wiggle(self.bst.edges[(node.parent, node)].weight_mob, scale_value=2, n_wiggles=14,
                                         rotation_angle=0.02 * TAU, run_time=2))
                down_anim = [new_key.animate(run_time=1 * run_time_factor).next_to(node, UP)]
                if show_path:
                    down_anim.append(
                        self.bst.edges[(node.parent, node)].animate_move_along_path(time_width=PATH_TIME_WIDTH * 2,
                                                                                    preserve_state=True,
                                                                                    run_time=1 * run_time_factor))
                animations.append(AnimationGroup(*down_anim))
            self.play(AnimationGroup(*animations, lag_ratio=0.8, suspend_mobject_updating=False))

        if not fast_find:
            self.next_section("Indicate key", skip_section=fast_find)
            self.play(IndicateNode(new_key, color=NODE_INDICATE_COLOR, run_time=1 * run_time_factor),
                      IndicateNode(real_key, color=NODE_INDICATE_COLOR, run_time=1 * run_time_factor))
        self.next_section("Remove double key", skip_section=fast_find)
        self.play(Unwrite(new_key))

    def animate_key_insert(self, key: int, fast_insert: bool = False, show_path=False, insert_last_node=True, **kwargs):
        run_time_factor = 0.2 if fast_insert else 1
        self.next_section(f"Inserting key {key}", skip_section=fast_insert)
        new_key = self.bst.insert_keys([key], **kwargs)[0]
        path = self.bst.search(new_key)[1][:-1]

        if path[-1] is None:
            path.pop()

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
                down_anim = [new_key.animate(run_time=1 * run_time_factor).next_to(node, UP)]
                if show_path:
                    down_anim.append(
                        self.bst.edges[(node.parent, node)].animate_move_along_path(time_width=PATH_TIME_WIDTH * 2,
                                                                                    preserve_state=True,
                                                                                    run_time=1 * run_time_factor))
                animations.append(AnimationGroup(*down_anim))
            self.play(AnimationGroup(*animations, lag_ratio=0.8, suspend_mobject_updating=False))

        if insert_last_node:
            self.next_section("Key inserted", skip_section=fast_insert)
            self.play(self.bst.animate(run_time=1 * run_time_factor).update_tree_layout())
            new_edge = self.bst.create_edge(new_key.parent, new_key)
            self.play(new_edge.draw_edge(run_time=1.5 * run_time_factor))

    def animate_delete_key(self, key: int, fast_delete: bool = False):
        run_time_factor = 0.2 if fast_delete else 1
        key_node = self.bst.search(key)[0]
        if key_node is None:
            return
        self.play(IndicateNode(key_node, run_time=1 * run_time_factor, preserve_indicate_color=True))
        minimum_scenario = key_node.left is not None and key_node.right is not None
        if minimum_scenario:
            self.next_section("Find minimum", skip_section=fast_delete)
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
            self.next_section("minimum replace", skip_section=fast_delete)
            remove_key_anim.append(min_key.animate(run_time=1 * run_time_factor).move_to(key.get_center()))
        self.play(AnimationGroup(*remove_key_anim, lag_ratio=0.8))
        if remove_edge is not None:
            self.next_section("Remove edge", skip_section=fast_delete)
            self.play(Unwrite(remove_edge), run_time=1 * run_time_factor)
        if update_edge is not None:
            self.next_section("Update edge", skip_section=fast_delete)
            self.play(
                update_edge.animate(run_time=1 * run_time_factor).put_start_and_end_on(update_edge.start.get_center(),
                                                                                       update_edge.end.get_center()))
        if minimum_scenario:
            self.next_section("Replace key", skip_section=fast_delete)
            self.play(min_key.animate(run_time=1 * run_time_factor).set_color(fill_color=VERTEX_COLOR,
                                                                              stroke_color=VERTEX_STROKE_COLOR))
        self.bst.add_updater(self.bst.update_edges)
        self.next_section("Update tree layout", skip_section=fast_delete)
        self.play(self.bst.animate.update_tree_layout(), run_time=1 * run_time_factor)

    def animate_successor(self, key: int, run_time_factor: float = 1, fast_successor: bool = False):
        run_time_factor = 0.2 if fast_successor else 1
        key_node = self.bst.search(key)[0]
        self.play(IndicateNode(key_node, color=NODE_INDICATE_COLOR, run_time=1 * run_time_factor,
                               preserve_indicate_color=True))
        self.next_section(f"Finding successor of key {key}", skip_section=fast_successor)
        if key_node.right is not None:
            self.play(IndicateNode(key_node.right, color_theme="green", run_time=1 * run_time_factor,
                                   preserve_indicate_color=True))
            self.next_section("Minimum of right subtree", skip_section=fast_successor)
            self.play(self.animate_minimum_find(key_node.right, run_time_factor))
        self.next_section("End minimum find")
        self.play(IndicateNode(key_node, color_theme="blue", scale_factor=1, run_time=1 * run_time_factor,
                               preserve_indicate_color=True),
                  IndicateNode(key_node.right, color_theme="blue", scale_factor=1, run_time=1 * run_time_factor,
                               preserve_indicate_color=True),
                  IndicateNode(self.bst.minimum(key_node.right), color_theme="blue", scale_factor=1,
                               run_time=1 * run_time_factor, preserve_indicate_color=True))

    def animate_minimum_find(self, node: Node, run_time_factor: float = 1, **kwargs) -> AnimationGroup:
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
        self.animate_delete_key(25)
        self.animate_delete_key(34)
        self.animate_delete_key(10)


class BSTLecture(BSTScene):
    def __init__(self, **kwargs):
        self.funcs_txt_loc = LEFT + UP
        self.funcs_txt_buff = 0.3
        keys = BASE_TREE_VERTICES[:-2]
        super().__init__(keys=keys, **kwargs)

    def construct(self):
        self.next_section("BST", pst.NORMAL)
        bst_title = Text("Binary Search Tree (BST)").scale_to_fit_width(config.frame_width * 0.9)
        self.play(Write(bst_title))

        self.next_section("BST Definition")
        bst_def_title = Text("BST Invariant:").to_edge(LEFT)
        bst_def = Tex("For every node $v$: left-subtree($v$).keys $<$ $v$.key $\leq$ right-subtree($v$).keys"). \
            scale_to_fit_width(config.frame_width * 0.9).next_to(bst_def_title, DOWN, buff=0.7).shift(
            RIGHT * 0.4).align_to(bst_def_title, LEFT)
        bst_def_group = VGroup(bst_def_title, bst_def)
        self.play(bst_title.animate.to_edge(UP).scale_to_fit_width(config.frame_width * 0.6))
        self.play(Write(bst_def_group))

        self.next_section("BST example")
        self.play(Unwrite(bst_def_group))
        self.bst.tree_width = config.frame_width
        self.bst.tree_left = -config.frame_width * 0.5
        self.bst.tree_top = config.frame_height * 0.45  # 0.6 touch title, 0.3 center
        self.bst.tree_height = config.frame_height * 1  # prev 1.5
        self.bst.update_tree_layout()
        self.play(Write(self.bst))

        self.next_section("BST find", pst.NORMAL)
        self.play(Unwrite(bst_title))
        find_key = 20
        find_txt = get_func_text(f"Find({find_key})").to_edge(self.funcs_txt_loc, buff=self.funcs_txt_buff)
        self.play(Write(find_txt))
        self.animate_find(find_key)
        find_complexity_tex = Tex("Time Complexity: O(h)").next_to(find_txt, DOWN).scale(0.8).align_to(find_txt, LEFT)

        self.play(Write(find_complexity_tex))
        b2 = Brace(self.bst, direction=RIGHT)
        b2text = b2.get_tex("h", buff=0.1)
        self.play(GrowFromCenter(b2), Write(b2text))

        self.next_section("BST insert", pst.NORMAL)
        self.play(Unwrite(find_complexity_tex), Unwrite(b2), Unwrite(b2text), Unwrite(find_txt))
        insert_key = 26
        insert_txt = get_func_text(f"Insert({insert_key})").to_edge(self.funcs_txt_loc, buff=self.funcs_txt_buff)
        self.play(Write(insert_txt))
        self.animate_key_insert(insert_key)
        insert_complexity_tex = Tex("Time Complexity: O(h)").next_to(insert_txt, DOWN).scale(0.8).align_to(find_txt,
                                                                                                           LEFT)
        self.play(Write(insert_complexity_tex))

        self.next_section("BST successor", pst.NORMAL)
        self.play(Unwrite(insert_complexity_tex), Unwrite(insert_txt))
        successor_key = 23
        successor_txt = get_func_text(f"Successor({successor_key})").to_edge(self.funcs_txt_loc,
                                                                             buff=self.funcs_txt_buff)
        self.play(Write(successor_txt))
        self.animate_successor(successor_key)
        successor_complexity_tex = Tex("Time Complexity: O(h)").next_to(successor_txt, DOWN).scale(0.8).align_to(
            find_txt, LEFT)
        self.play(Write(successor_complexity_tex))

        self.next_section("BST delete", pst.NORMAL)
        self.play(Unwrite(successor_complexity_tex), Unwrite(successor_txt))
        delete_key = 20
        delete_txt = get_func_text(f"Delete({delete_key})").to_edge(self.funcs_txt_loc, buff=self.funcs_txt_buff)
        self.play(Write(delete_txt))
        self.next_section("BST delete")
        self.animate_delete_key(delete_key)

        self.next_section("BST delete")
        self.play(Unwrite(delete_txt))
        delete_key = 10
        delete_txt = get_func_text(f"Delete({delete_key})").to_edge(self.funcs_txt_loc, buff=self.funcs_txt_buff)
        self.play(Write(delete_txt))
        self.next_section("BST delete")
        self.animate_delete_key(delete_key)

        self.next_section("BST delete")
        self.play(Unwrite(delete_txt))
        delete_key = 23
        delete_txt = get_func_text(f"Delete({delete_key})").to_edge(self.funcs_txt_loc, buff=self.funcs_txt_buff)
        self.play(Write(delete_txt))
        self.next_section("BST delete")
        self.animate_delete_key(delete_key)

        self.next_section("BST delete")
        self.play(Unwrite(delete_txt))
        delete_key = 25
        delete_txt = get_func_text(f"Delete({delete_key})").to_edge(self.funcs_txt_loc,
                                                                    buff=self.funcs_txt_buff)
        self.play(Write(delete_txt))
        self.next_section("BST delete")
        self.animate_delete_key(delete_key)

        self.next_section("BST delete complexity")
        delete_complexity_tex = Tex("Time Complexity: O(h)").next_to(delete_txt, DOWN).scale(0.8).align_to(find_txt,
                                                                                                           LEFT)
        self.play(Write(delete_complexity_tex))
        self.next_section("BST summary")
        self.play(Unwrite(delete_complexity_tex), Unwrite(delete_txt))
        self.next_section("BST summary 2")
        self.play(Unwrite(self.bst))
        self.wait()


class ComplexitySummaryBST(BSTScene):
    def __init__(self, **kwargs):
        keys = [1]
        super().__init__(keys=keys, **kwargs)

    def construct(self):
        self.next_section("BST Complexity", pst.NORMAL)
        worst_case_title = Text("BST Worst Case").scale_to_fit_width(config.frame_width * 0.9)
        self.play(Write(worst_case_title))
        self.next_section("Worst BST")
        self.play(Unwrite(worst_case_title), Write(self.bst))
        for i in range(2, 12):
            self.animate_key_insert(i, fast_insert=True)

        b2 = Brace(self.bst, direction=LEFT)
        b2text = b2.get_tex("h=n", buff=0.1)
        self.play(GrowFromCenter(b2), Write(b2text))
        self.next_section("BST complexity table")
        self.play(Unwrite(b2), Unwrite(b2text), Unwrite(self.bst))
        complex_table = Table(
            [["O(h)"],
             ["O(h)"],
             ["O(h)"]],
            row_labels=[get_func_text("Find(x)", ["x"]), get_func_text("Delete(x)", ["x"]),
                        get_func_text("Insert(x)", ["x"])],
            col_labels=[Text("BST")],
            include_outer_lines=True,
            arrange_in_grid_config={"cell_alignment": RIGHT})
        complex_table.move_to(ORIGIN).scale_to_fit_height(config.frame_height * 0.7)
        self.play(Write(complex_table))
        self.next_section("done")
        self.play(Unwrite(complex_table))
        self.wait(0.3)


if __name__ == "__main__":
    scenes_lst = [BSTLecture, ComplexitySummaryBST]

    render_scenes(scenes_lst, OUT_DIR, PRESENTATION_MODE, DISABLE_CACHING, gif_scenes=[28 + i for i in range(6)],
                  create_gif=False)
