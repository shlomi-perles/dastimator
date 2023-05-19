"""
TODO: 1. Important! rotate the tree and then update the child edge. Not the other way around.
TODO: 2. Change the color of the inner child (beta).
TODO: 3. Maybe add delete example and worst case example (Example from TA7).
"""

from __future__ import annotations

from tools.funcs import *
from tools.graphs.avl_tree import *
from BST.bst import *

ROOT_PATH = Path(__file__).resolve().parent.parent
sys.path.append(str(ROOT_PATH.parent.parent))
OUT_DIR = MEDIA_PATH / Path(__file__).resolve().parent.stem

PRESENTATION_MODE = True
DISABLE_CACHING = True
config.background_color = BACKGROUND_COLOR
HD_TO_COLOR = {0: "blue", 1: "yellow", 2: "red", 3: "red"}
SUBTRE_HEIGHT_SCALE = {0: 0.95, 1: 1.6, 2: 2.25}
INSERT_WIDTH_TITLE = 0.33
ROTATE_WIDTH_TITLE = 0.28
INSERT_EXAMPLE_KEYS = [40, 15, 10, 5, 20, 60, 50, 70, 45, 55, 80, 52]
LEFT_ROTATE_KEYS = [2, 1, 4, 3, 5]
RL_ROTATE_KEYS = [2, 1, 6, 4, 3, 5, 7, 1.5]


class AVLScene(BSTScene):
    def __init__(self, keys: list = None, **kwargs):
        self.avl = AVLTree(keys, tree_width=config.frame_width * 0.7, tree_left=-config.frame_width * 0.25)
        super().__init__(bst=self.avl, **kwargs)
        self.hd_map = self.get_hd_map()
        for node in self.avl.nodes:
            self.avl.update_height(node)

        self.avl.tree_width = config.frame_width
        self.avl.tree_left = -config.frame_width * 0.5
        self.avl.tree_top = config.frame_height * 0.45  # 0.6 touch title, 0.3 center
        self.avl.tree_height = config.frame_height * 1  # prev 1.5
        self.avl.update_tree_layout()

    def update_height(self, node: AVLNode, **kwargs):
        indicate_animations = []
        while node is not None:
            self.avl.update_height(node)

            if str(node.fill_color).upper() != str(THEME_DICT[HD_TO_COLOR[abs(node.hd)]]['fill_color']).upper():
                indicate_animations.append(
                    IndicateNode(node, color_theme=HD_TO_COLOR[abs(node.hd)], preserve_indicate_color=True))
            node = node.parent

        if indicate_animations:
            self.play(AnimationGroup(*indicate_animations, **kwargs))

    def right_rotate(self, node: AVLNode, run_time_factor=1, fast_rotate: bool = False):
        relative_pos = [0] * 3
        if node == self.avl.root:
            relative_pos = self.avl.root.get_center()
        if not fast_rotate:
            self.avl.remove_updater(self.avl.update_edges)
            if node.left.right is not None:
                self.avl.edges[(node.left, node.left.right)].start = node
                self.play(
                    self.avl.edges[(node.left, node.left.right)].animate(
                        run_time=1 * run_time_factor).put_start_and_end_on(
                        node.get_center(), node.left.right.get_center()))
                self.next_section(f"update edge weight")
                self.play(self.avl.edges[(node.left, node.left.right)].set_weight(create_bst_weight(r"<", node),
                                                                                  run_time=1 * run_time_factor))
            if node.parent is not None:
                self.next_section(f"update parent edge")
                self.play(
                    self.avl.edges[(node.parent, node)].animate(run_time=1 * run_time_factor).put_start_and_end_on(
                        node.parent.get_center(), node.left.get_center()))

            self.play(self.avl.edges[(node, node.left)].set_weight(create_bst_weight(r"\leq", node),
                                                                   run_time=1 * run_time_factor))

            self.avl.add_updater(self.avl.update_edges)

        self.avl.right_rotate(node)
        self.play(node.animate(run_time=0.0001).shift(RIGHT * 0))  # dont move this magic line
        self.next_section(f"update layout")
        self.play(self.avl.animate(run_time=1 * run_time_factor).update_tree_layout(relative_to_root=True,
                                                                                    relative_x=relative_pos[0],
                                                                                    relative_y=relative_pos[1]))

    def left_rotate(self, node: AVLNode, run_time_factor=1, fast_rotate: bool = False):
        relative_pos = [0] * 3
        if node == self.avl.root:
            relative_pos = self.avl.root.get_center()
        if not fast_rotate:
            self.avl.remove_updater(self.avl.update_edges)
            if node.right.left is not None:
                self.avl.edges[(node.right, node.right.left)].start = node
                self.play(
                    self.avl.edges[(node.right, node.right.left)].animate(
                        run_time=1 * run_time_factor).put_start_and_end_on(node.get_center(),
                                                                           node.right.left.get_center()))
                self.next_section(f"update edge weight")
                self.play(self.avl.edges[(node.right, node.right.left)].set_weight(create_bst_weight(r"\leq", node),
                                                                                   run_time=1 * run_time_factor))
            if node.parent is not None:
                self.next_section(f"update parent edge")
                self.play(
                    self.avl.edges[(node.parent, node)].animate(run_time=1 * run_time_factor).put_start_and_end_on(
                        node.parent.get_center(), node.right.get_center()))

            self.play(self.avl.edges[(node, node.right)].set_weight(create_bst_weight(r"<", node),
                                                                    run_time=1 * run_time_factor))

            self.avl.add_updater(self.avl.update_edges)

        self.avl.left_rotate(node)
        self.play(node.animate(run_time=0.0001).shift(RIGHT * 0))  # dont move this magic line
        self.next_section(f"update layout")
        self.play(self.avl.animate(run_time=1 * run_time_factor).update_tree_layout(relative_to_root=True,
                                                                                    relative_x=relative_pos[0],
                                                                                    relative_y=relative_pos[1]))

    def balance_up(self, node: AVLNode, run_time_factor=1, fast_anim: bool = False, **kwargs):
        while node is not None:
            if abs(node.hd) > 1:
                self.balance(node, run_time_factor=run_time_factor, fast_anim=fast_anim, **kwargs)
            node = node.parent

    def balance(self, node: AVLNode, run_time_factor=1, fast_anim: bool = False, l_rotate_title=None,
                r_rotate_title=None):
        if node is None:
            return
        if node.hd == 2:
            if node.left.hd == -1:
                if l_rotate_title is not None:
                    self.next_section("left rotate")
                    self.play(Write(l_rotate_title))
                self.left_rotate(node.left, run_time_factor=run_time_factor, fast_rotate=fast_anim)
                self.update_height(node.left.left, lag_ratio=0.5, run_time=1 * run_time_factor)
            if r_rotate_title is not None:
                self.next_section("right rotate")
                self.play(Write(r_rotate_title))
            self.right_rotate(node, run_time_factor=run_time_factor, fast_rotate=fast_anim)
            self.update_height(node, lag_ratio=0.5, run_time=1 * run_time_factor)

        elif node.hd == -2:
            if node.right.hd == 1:
                if r_rotate_title is not None:
                    self.next_section("right rotate")
                    self.play(Write(r_rotate_title))
                self.right_rotate(node.right, run_time_factor=run_time_factor, fast_rotate=fast_anim)
                self.update_height(node.right.right, lag_ratio=0.5, run_time=1 * run_time_factor)
            if l_rotate_title is not None:
                self.next_section("left rotate")
                self.play(Write(l_rotate_title))
            self.left_rotate(node, run_time_factor=run_time_factor, fast_rotate=fast_anim)
            self.update_height(node, lag_ratio=0.5, run_time=1 * run_time_factor)

    def get_hd_map(self):
        scale_tex = 1.2
        tex_buff = 0.5
        hd_map = VGroup()
        red_node = Node(label="").set_color(color_theme="red")
        red_tex = MathTex(r"\left|hd\right|=2").next_to(red_node, RIGHT, buff=tex_buff).scale(scale_tex)
        red_group = VGroup(red_node, red_tex)
        yellow_node = Node(label="").set_color(color_theme="yellow")
        yellow_tex = MathTex(r"\left|hd\right|=1").next_to(yellow_node, RIGHT, buff=tex_buff).scale(scale_tex)
        yellow_group = VGroup(yellow_node, yellow_tex)
        blue_node = Node(label="").set_color(color_theme="blue")
        blue_tex = MathTex(r"\left|hd\right|=0").next_to(blue_node, RIGHT, buff=tex_buff).scale(scale_tex)
        blue_group = VGroup(blue_node, blue_tex)

        hd_map.add(red_group, yellow_group, blue_group)
        hd_map.arrange(DOWN, buff=0.5)
        hd_map.scale_to_fit_height(config.frame_height * 0.2)
        hd_map.to_edge(LEFT + UP)
        return hd_map

    def construct(self):
        pass


class AVLRotation(AVLScene):
    def __init__(self, **kwargs):
        # keys = [0, 4, 2, 1, 3, 5]  # right check
        keys = [0, 2, 1, 4, 3, 5]  # left check
        super().__init__(keys, **kwargs)

    def construct(self):
        self.next_section("AVL Rotation")
        self.update_height(self.avl.nodes[-1], lag_ratio=0.5, run_time=3)
        self.left_rotate(self.avl.nodes[1])


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


class AVLInsert(AVLScene):
    def __init__(self, **kwargs):
        keys = [40, 15, 10, 5, 20, 60, 50, 70, 45, 55, 80, 52]
        super().__init__(keys, **kwargs)

    def construct(self):
        self.next_section("AVL Tree")
        self.animate_key_insert(53, show_path=True, update_height=False)
        self.update_height(self.avl.nodes[-1], lag_ratio=0.5, run_time=3)
        self.balance_up(self.avl.nodes[-1], run_time_factor=1)
        # last_edge = self.avl.edges[(self.avl.nodes[-2], self.avl.nodes[-1])]
        # self.play(last_edge.animate_move_along_path(time_width=PATH_TIME_WIDTH * 2, preserve_state=True, run_time=3))
        self.wait()


class AVLTeachRotate(AVLScene):

    def __init__(self, **kwargs):
        # keys = [0, 4, 2, 1, 3, 5]  # right check
        keys = [2, 1, 4, 3, 5]  # left check
        super().__init__(keys, **kwargs)
        for node in self.avl.nodes:
            self.avl.update_height(node)

    def construct(self):
        self.next_section("AVL Rotation")
        alpha_subtree = SubTree(self.avl.nodes[1]).scale(SUBTRE_HEIGHT_SCALE[0])
        beta_subtree = SubTree(self.avl.nodes[3]).scale(SUBTRE_HEIGHT_SCALE[0])
        gamma_subtree = SubTree(self.avl.nodes[4]).scale(SUBTRE_HEIGHT_SCALE[0])
        self.avl.add(alpha_subtree, beta_subtree, gamma_subtree)
        self.avl.tree_height = self.avl.tree_height * 0.7
        self.avl.tree_width = config.frame_width * 0.4
        self.avl.update_tree_layout()
        # self.add(self.avl, alpha_subtree, beta_subtree, gamma_subtree)
        self.avl.to_edge(DOWN)
        self.avl.to_edge(RIGHT, buff=-0.8)
        self.play(Write(self.avl))
        self.left_rotate(self.avl.root)


class AVLLectureIntro(AVLScene):

    def __init__(self, **kwargs):
        keys = INSERT_EXAMPLE_KEYS
        super().__init__(keys, **kwargs)

    def construct(self):
        self.next_section("AVL Tree", pst.NORMAL)
        avl_title = Text("AVL Tree").scale_to_fit_width(config.frame_width * 0.9)
        self.play(Write(avl_title))

        self.next_section("height explanation")
        self.play(avl_title.animate.scale_to_fit_width(self.hd_map.width * 0.4).to_edge(UP))
        orig_avl = self.avl
        self.avl = orig_avl.copy()
        self.play(Write(self.avl))
        self.explain_avl_heights()

        self.explain_hd()

        self.next_section("AVL Definition")
        orig_avl = self.avl.copy()
        self.play(Unwrite(avl_title), Unwrite(self.hd_map), Unwrite(self.avl))
        self.avl = orig_avl.copy()
        avl_def_title = Text("AVL Invariant:").to_edge(LEFT)
        avl_def = BulletedList(
            "BST Invariant", "For every node $v$: $|hd(v)| \leq 1$").next_to(avl_def_title, DOWN, buff=0.7).shift(
            RIGHT * 0.4).align_to(avl_def_title, LEFT).shift(RIGHT * 1.5)
        avl_def_group = VGroup(avl_def_title, avl_def)
        self.play(Write(avl_def_group))

        self.next_section("end of AVL definition")
        self.play(Unwrite(avl_def_group))
        self.wait(0.1)

    def explain_avl_heights(self):
        heights_text = {
            node: Tex(f"$h={int(node.tree_height)}$", color=YELLOW).next_to(node, RIGHT, buff=0.1).scale(0.7)
            for
            node in self.avl.nodes}
        arrow_heights = Arrow(self.avl.root.get_top(), self.avl.root.get_bottom(), buff=0.1, color=GREEN)
        h_question = Tex("$h=?$", color=GREEN).next_to(arrow_heights, UP, buff=0.1)
        h_question.add_updater(lambda m: m.next_to(arrow_heights, UP, buff=0.1))

        height_tex = VGroup(arrow_heights, h_question)
        cur_node = self.avl.search(20)[0]
        arrow_heights.next_to(cur_node, UP, buff=0.1)
        self.play(Write(height_tex))

        self.next_section("show height")
        self.play(Write(heights_text[cur_node]))
        self.next_section("next height question")
        cur_node = self.avl.search(15)[0]
        self.play(arrow_heights.animate.next_to(cur_node, UP, buff=0.1))
        self.next_section("show height")
        self.play(Write(heights_text[cur_node]))
        self.next_section("explain question")
        reveals_heights = [5, 10]
        self.play(*[Write(heights_text[self.avl.search(key)[0]]) for key in reveals_heights])
        self.next_section("reveal all heights")
        already_revealed = reveals_heights + [20, 15]
        self.play(*[Write(heights_text[node]) for node in self.avl.nodes if node.key not in already_revealed])
        self.next_section("end explain heights")
        self.play(Unwrite(height_tex), *[Unwrite(heights_text[node]) for node in self.avl.nodes])

    def explain_hd(self):
        self.next_section("explain hd")
        hd_equation = Tex("hd(v) = h(v.left) - h(v.right)").to_edge(LEFT + DOWN)
        self.play(Write(hd_equation))
        self.next_section("explain hd")

        hd_text = {node: Tex(f"$hd={int(node.hd)}$", color=YELLOW).next_to(node, RIGHT, buff=0.03).scale(0.7)
                   for node in self.avl.nodes}
        arrow_hd = Arrow(self.avl.root.get_top(), self.avl.root.get_bottom(), buff=0.1, color=GREEN)
        hd_question = Tex("$hd=?$", color=GREEN).next_to(arrow_hd, UP, buff=0.1)
        hd_question.add_updater(lambda m: m.next_to(arrow_hd, UP, buff=0.1))

        hd_tex = VGroup(arrow_hd, hd_question)
        cur_node = self.avl.search(20)[0]
        arrow_hd.next_to(cur_node, UP, buff=0.1)
        self.play(Write(hd_tex))

        self.next_section("show hd")
        self.play(Write(hd_text[cur_node]))
        self.next_section("next hd question")
        cur_node = self.avl.search(15)[0]
        self.play(arrow_hd.animate.next_to(cur_node, UP, buff=0.1))
        self.next_section("show hd")
        self.play(Write(hd_text[cur_node]))
        self.next_section("explain question")
        reveals_hd = [5, 10]
        self.play(*[Write(hd_text[self.avl.search(key)[0]]) for key in reveals_hd])
        self.next_section("reveal all hd")
        already_revealed = reveals_hd + [20, 15]
        self.play(*[Write(hd_text[node]) for node in self.avl.nodes if node.key not in already_revealed])
        self.next_section("explain color map")
        self.play(Write(self.hd_map))
        self.play(*[IndicateNode(node, color_theme=HD_TO_COLOR[abs(node.hd)], preserve_indicate_color=True) for node in
                    self.avl.nodes])

        self.next_section("end explain hd")
        self.play(Unwrite(hd_tex), *[Unwrite(hd_text[node]) for node in self.avl.nodes], Unwrite(hd_equation))


class AVLLectureIntroInsert(AVLScene):

    def __init__(self, **kwargs):
        keys = INSERT_EXAMPLE_KEYS
        super().__init__(keys, **kwargs)
        for node in self.avl.nodes:
            node.set_color(color_theme=HD_TO_COLOR[abs(node.hd)])

    def construct(self):
        self.next_section("AVL Insert example")
        self.play(Write(self.avl), Write(self.hd_map))
        insert_tex = get_func_text("Insert(AVL,53)").scale_to_fit_width(
            config.frame_width * INSERT_WIDTH_TITLE).to_edge(
            LEFT + DOWN)
        self.play(Write(insert_tex))
        self.animate_key_insert(53, show_path=True, update_height=False)
        self.next_section("update heights")
        self.update_height(self.avl.nodes[-1], lag_ratio=0.5, run_time=3)
        self.next_section("end insert")
        self.play(Unwrite(insert_tex), Unwrite(self.avl), Unwrite(self.hd_map))


class AVLLectureRotations(AVLScene):

    def __init__(self, **kwargs):
        keys = INSERT_EXAMPLE_KEYS
        super().__init__(keys, **kwargs)

    def construct(self):
        self.next_section("AVL Rotation", pst.NORMAL)
        self.rotations_explain()
        self.wait(0.1)

    def rotations_explain(self):
        explain_avl = AVLTree(keys=LEFT_ROTATE_KEYS)
        explain_avl.create_tree()
        for node in explain_avl.nodes:
            explain_avl.update_height(node)
            node.set_color(color_theme=HD_TO_COLOR[abs(node.hd)])
        alpha_subtree = SubTree(explain_avl.nodes[1]).scale(SUBTRE_HEIGHT_SCALE[0])
        beta_subtree = SubTree(explain_avl.nodes[3]).scale(SUBTRE_HEIGHT_SCALE[0])
        gamma_subtree = SubTree(explain_avl.nodes[4]).scale(SUBTRE_HEIGHT_SCALE[0])
        x_node = explain_avl.nodes[0]
        y_node = explain_avl.nodes[2]
        x_node.set_label("x")
        y_node.set_label("y")

        explain_avl.add(alpha_subtree, beta_subtree, gamma_subtree)
        explain_avl.tree_height = explain_avl.tree_height * 0.7
        explain_avl.tree_width = config.frame_width * 0.33
        explain_avl.update_tree_layout()
        # self.add(explain_avl, alpha_subtree, beta_subtree, gamma_subtree)
        explain_avl.to_edge(DOWN)
        explain_avl.to_edge(RIGHT, buff=-0.8)
        explain_avl.set_x(config.frame_width * 0.54)

        rotations_title = Text("AVL Rotations").scale_to_fit_width(config.frame_width * 0.6).to_edge(UP)

        self.play(Write(explain_avl), Write(rotations_title), Write(self.hd_map))
        self.next_section("left rotate")
        left_avl = explain_avl.copy()
        left_avl.to_edge(LEFT, buff=1.2)

        left_arrow = CurvedArrow(explain_avl.get_left(), left_avl.get_right())
        left_arrow_text = get_func_text("Left-Rotate(AVL,x)", ["x"]).next_to(left_arrow, UP).scale_to_fit_width(
            left_arrow.width)
        left_info_group = VGroup(left_arrow, left_arrow_text)
        left_info_group_cop = left_info_group.copy()
        self.play(Write(left_arrow_text))
        self.play(Write(left_arrow))
        left_avl.move_to(explain_avl)
        self.play(left_avl.animate.to_edge(LEFT, buff=1.2))
        remember_avl = self.avl
        self.avl = left_avl
        self.next_section("animate left rotate")
        self.left_rotate(left_avl.root)
        self.update_height(left_avl.root.left)

        self.next_section("right rotate")
        right_avl = left_avl.copy()
        right_avl.move_to(explain_avl)
        right_arrow = CurvedArrow(left_avl.get_right(), right_avl.get_left()).match_width(left_arrow).match_x(
            left_arrow)
        right_arrow_text = get_func_text("Right-Rotate(AVL,y)", ["y"]).scale_to_fit_width(
            right_arrow.width).next_to(right_arrow, DOWN)
        right_info_group = VGroup(right_arrow, right_arrow_text)
        self.play(Unwrite(left_info_group), Unwrite(explain_avl), Write(right_arrow_text))
        self.play(Write(right_arrow))
        self.avl = right_avl
        right_avl.move_to(left_avl)
        self.play(right_avl.animate.next_to(right_arrow, RIGHT, buff=-0.2).match_y(left_avl))
        self.next_section("show rotations")
        self.right_rotate(right_avl.root)
        self.update_height(right_avl.root.right)
        self.next_section("show rotations")
        self.play(Write(left_info_group_cop))
        self.next_section("end rotations")
        self.play(Unwrite(left_info_group_cop), Unwrite(right_info_group), Unwrite(right_avl), Unwrite(left_avl),
                  Unwrite(rotations_title), Unwrite(self.hd_map))
        self.avl = remember_avl
        self.wait(0.1)


class AVLLectureBalance(AVLScene):

    def __init__(self, **kwargs):
        keys = LEFT_ROTATE_KEYS
        super().__init__(keys, **kwargs)

    def construct(self):
        self.next_section("AVL Balance", pst.NORMAL)
        for node in self.avl.nodes:
            self.avl.update_height(node)
            node.set_color(color_theme=HD_TO_COLOR[abs(node.hd)])

        alpha_subtree = SubTree(self.avl.nodes[1]).scale(SUBTRE_HEIGHT_SCALE[1])
        beta_subtree = SubTree(self.avl.nodes[3]).scale(SUBTRE_HEIGHT_SCALE[1])
        gamma_subtree = SubTree(self.avl.nodes[4]).scale(SUBTRE_HEIGHT_SCALE[2])
        v_node = self.avl.nodes[0]
        u_node = self.avl.nodes[2]
        v_node.set_label("v").set_color(color_theme=HD_TO_COLOR[2])
        u_node.set_label("u").set_color(color_theme=HD_TO_COLOR[1])

        self.avl.add(alpha_subtree, beta_subtree, gamma_subtree)
        self.avl.tree_height = self.avl.tree_height * 0.7
        self.avl.tree_width = config.frame_width * 0.9
        self.avl.update_tree_layout()
        # self.add(self.avl, alpha_subtree, beta_subtree, gamma_subtree)
        self.avl.move_to(ORIGIN).to_edge(RIGHT)
        # self.avl.to_edge(RIGHT, buff=-0.8)
        # self.avl.set_x(config.frame_width * 0.54)

        rr_rotations_title = Text("AVL RR Rotation").scale_to_fit_width(config.frame_width * 0.6).to_edge(UP)

        self.play(Write(self.avl), Write(rr_rotations_title), Write(self.hd_map))
        self.next_section("left rotate")
        right_rotate_text = get_func_text("Left-Rotate(AVL,v)", ["v"]).next_to(
            rr_rotations_title, DOWN).scale_to_fit_width(rr_rotations_title.width * 0.5).to_edge(RIGHT)
        self.play(Write(right_rotate_text))
        self.left_rotate(self.avl.root)
        self.next_section("update heights")
        self.play(AnimationGroup(IndicateNode(v_node, color_theme=HD_TO_COLOR[0], preserve_indicate_color=True),
                                 IndicateNode(u_node, color_theme=HD_TO_COLOR[0], preserve_indicate_color=True),
                                 lag_ratio=0.5))

        self.next_section("rl rotation")
        rl_rotations_title = Text("AVL RL Rotation").scale_to_fit_width(config.frame_width * 0.6).to_edge(UP)
        self.play(Unwrite(self.avl), Unwrite(right_rotate_text))
        self.play(TransformMatchingShapes(rr_rotations_title, rl_rotations_title))

        rt_tree = AVLTree(keys=RL_ROTATE_KEYS)
        rt_tree.create_tree()
        for node in rt_tree.nodes:
            rt_tree.update_height(node)
        self.avl = rt_tree
        self.avl.nodes[-1].set_opacity(0)
        self.avl.edges[(self.avl.root.left, self.avl.nodes[-1])].set_opacity(0)
        alpha_subtree = SubTree(self.avl.nodes[1]).scale(SUBTRE_HEIGHT_SCALE[1])
        beta_subtree = SubTree(self.avl.nodes[4]).scale(SUBTRE_HEIGHT_SCALE[1])
        gamma_subtree = SubTree(self.avl.nodes[5]).scale(SUBTRE_HEIGHT_SCALE[1])
        delta_subtree = SubTree(self.avl.nodes[6]).scale(SUBTRE_HEIGHT_SCALE[1])
        v_node = self.avl.nodes[0]
        u_node = self.avl.nodes[2]
        w_node = self.avl.nodes[3]
        v_node.set_label("v").set_color(color_theme=HD_TO_COLOR[2])
        u_node.set_label("u").set_color(color_theme=HD_TO_COLOR[1])
        w_node.set_label("w").set_color(color_theme=HD_TO_COLOR[0])
        rt_tree.add(alpha_subtree, beta_subtree, gamma_subtree, delta_subtree)
        rt_tree.tree_height = rt_tree.tree_height * 0.7
        rt_tree.tree_width = config.frame_width * 0.9
        rt_tree.update_tree_layout()
        self.avl.move_to(ORIGIN).to_edge(RIGHT + DOWN)

        self.play(Write(self.avl))
        self.next_section("right rotate")
        right_rotate_text = get_func_text("Right-Rotate(AVL,u)", ["u"]).next_to(
            rl_rotations_title, DOWN).scale_to_fit_width(rl_rotations_title.width * 0.5).to_edge(RIGHT)
        self.play(Write(right_rotate_text))
        self.right_rotate(self.avl.root.right)
        self.next_section("update heights")
        self.play(AnimationGroup(IndicateNode(u_node, color_theme=HD_TO_COLOR[0], preserve_indicate_color=True),
                                 IndicateNode(w_node, color_theme=HD_TO_COLOR[1], preserve_indicate_color=True),
                                 lag_ratio=0.5))
        self.next_section("left rotate")
        left_rotate_text = get_func_text("Left-Rotate(AVL,v)", ["v"]).match_height(right_rotate_text).next_to(
            right_rotate_text, DOWN)
        self.play(Write(left_rotate_text))
        self.left_rotate(self.avl.root)
        self.next_section("update heights")
        self.play(AnimationGroup(IndicateNode(v_node, color_theme=HD_TO_COLOR[0], preserve_indicate_color=True),
                                 IndicateNode(w_node, color_theme=HD_TO_COLOR[0], preserve_indicate_color=True),
                                 lag_ratio=0.5))
        self.next_section("done")
        self.play(Unwrite(self.avl), Unwrite(right_rotate_text), Unwrite(left_rotate_text), Unwrite(rl_rotations_title),
                  Unwrite(self.hd_map))
        self.wait(0.3)


class AVLLectureInsert(AVLScene):

    def __init__(self, **kwargs):
        keys = INSERT_EXAMPLE_KEYS
        super().__init__(keys, **kwargs)
        for node in self.avl.nodes:
            node.set_color(color_theme=HD_TO_COLOR[abs(node.hd)])

    def construct(self):
        self.next_section("AVL Insert example")
        self.play(Write(self.avl), Write(self.hd_map))
        insert_tex = get_func_text("Insert(AVL,53)").scale_to_fit_width(
            config.frame_width * INSERT_WIDTH_TITLE).to_edge(LEFT + DOWN)
        self.play(Write(insert_tex))
        self.animate_key_insert(53, show_path=True, update_height=False)
        self.next_section("update heights")
        self.update_height(self.avl.nodes[-1], lag_ratio=0.5, run_time=3)
        self.next_section("balance up")
        l_rotation_text = get_func_text("Left-Rotate(AVL,52)").scale_to_fit_width(
            config.frame_width * ROTATE_WIDTH_TITLE).to_edge(UP + RIGHT)
        r_rotation_text = get_func_text("Right-Rotate(AVL,55)").match_height(
            l_rotation_text).next_to(l_rotation_text, DOWN)
        self.balance_up(self.avl.nodes[-1], run_time_factor=1, l_rotate_title=l_rotation_text,
                        r_rotate_title=r_rotation_text)

        self.next_section("AVL Insert example")
        self.remove_path(self.avl.search(55)[0])
        self.play(Unwrite(l_rotation_text), Unwrite(r_rotation_text))
        insert_tex_2 = get_func_text("Insert(AVL,57)").scale_to_fit_width(
            config.frame_width * INSERT_WIDTH_TITLE).to_edge(
            LEFT + DOWN)
        self.play(TransformMatchingShapes(insert_tex, insert_tex_2))
        self.animate_key_insert(57, show_path=True, update_height=False)
        self.next_section("update heights")
        self.update_height(self.avl.nodes[-1], lag_ratio=0.5, run_time=3)
        self.next_section("balance up")
        l_rotation_text = get_func_text("Left-Rotate(AVL,50)").scale_to_fit_width(
            config.frame_width * ROTATE_WIDTH_TITLE).to_edge(UP + RIGHT)
        self.balance_up(self.avl.nodes[-1], run_time_factor=1, l_rotate_title=l_rotation_text)
        self.next_section("done")
        self.play(Unwrite(insert_tex_2), Unwrite(self.avl), Unwrite(self.hd_map), Unwrite(l_rotation_text))
        self.wait(0.3)

    def remove_path(self, node):
        animations = []
        while node.parent is not None:
            animations.append(
                self.avl.edges[node.parent, node].animate_move_along_path(flash_color=WHITE, opposite_direction=True,
                                                                          time_width=PATH_TIME_WIDTH * 2,
                                                                          preserve_state=True))
            node = node.parent
        self.play(AnimationGroup(*animations, lag_ratio=0.5))


class ComplexitySummary(SectionsScene):
    def construct(self):
        complex_table = Table(
            [["O(h)", "O(logn)"],
             ["O(h)", "O(logn)"],
             ["O(h)", "O(logn)"]],
            row_labels=[get_func_text("Find(x)", ["x"]), get_func_text("Delete(x)", ["x"]),
                        get_func_text("Insert(x)", ["x"])],
            col_labels=[Text("BST"), Text("AVL")],
            include_outer_lines=True,
            arrange_in_grid_config={"cell_alignment": RIGHT})
        complex_table.move_to(ORIGIN).scale_to_fit_width(config.frame_width * 0.8)
        self.next_section("complexity summary", pst.NORMAL)
        self.play(Write(complex_table))
        self.next_section("done")
        self.play(Unwrite(complex_table))
        self.wait(0.3)


if __name__ == "__main__":
    create_scene_gif("D:\projects\Manim\dastimator\media\AVL", "AVLLectureRotations", [1+i for i in range(11)],
                     quality_dir="2160p60")
    # scenes_lst = [AVLLectureIntro, AVLLectureIntroInsert, AVLLectureRotations, AVLLectureBalance, AVLLectureInsert,
    #               ComplexitySummary]
    #
    # run_scenes(scenes_lst, OUT_DIR, PRESENTATION_MODE, DISABLE_CACHING, gif_scenes=[1 + i for i in range(6)],
    #            create_gif=False)
