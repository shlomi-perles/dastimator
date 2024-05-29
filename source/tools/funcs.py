from __future__ import annotations

import re

import numpy as np
from manim import *
from manim import Polygon, Rectangle, SurroundingRectangle, VGroup
from manim.mobject.geometry.boolean_ops import _BooleanOps
from manim_fonts import *
from scipy.spatial import ConvexHull, KDTree
import networkx as nx

from .consts import LINES_OFF_OPACITY
from .code_styles import DarculaStyle, pygments_monkeypatch_style

CODE_MATH_SCALE = 0.9


# ---------------------------- Code ----------------------------

def highlight_code_lines(code: Code, lines: list = None, off_opacity: float = LINES_OFF_OPACITY, indicate=True,
                         **kwargs) -> AnimationGroup | tuple[AnimationGroup, Indicate]:
    code = code.code
    lines_highlighted_animation = []
    lines_indicate = []
    lines = list(range(len(code) + 1)) if lines is None else lines
    # VMobjectFromSVGPath().background_stroke_opacity
    for line_number, line in enumerate(code):
        if line_number == 0: continue

        if line_number + 1 in lines:
            if indicate:
                lines_indicate.append(line)
            lines_highlighted_animation.append(line.animate.set_fill(opacity=1))
        else:
            lines_highlighted_animation.append(line.animate.set_fill(opacity=off_opacity))
    if indicate:
        return AnimationGroup(*lines_highlighted_animation, **kwargs), Indicate(VGroup(*lines_indicate), **kwargs)
    return AnimationGroup(*lines_highlighted_animation, **kwargs)


def code_explain(code: Code, lines: list, explain: str, off_opacity: float = LINES_OFF_OPACITY,
                 buff: float = SMALL_BUFF, explain_color: str = YELLOW, scale: float = 1,
                 **kwargs) -> tuple[VGroup, AnimationGroup]:
    code_obj = code.code
    lines_group = VGroup(*[code_obj[line - 1] for line in lines])
    brace_explain = Brace(lines_group, RIGHT, buff=buff, color=explain_color)
    exp_tx = Text(explain, color=explain_color).next_to(brace_explain, RIGHT, buff=buff)
    exp_tx.scale(scale)
    highlight_anim = highlight_code_lines(code, lines=lines, off_opacity=off_opacity, indicate=False)
    all_mobj = VGroup(brace_explain, exp_tx)
    return all_mobj, AnimationGroup(highlight_anim, GrowFromCenter(brace_explain), Write(exp_tx),
                                    **{"lag_ratio": 1, **kwargs})


def transform_code_lines(code: Code, target_code: Code, lines_transform_dict: dict, **kwargs) -> AnimationGroup:
    code = code.code
    target_code = target_code.code
    lines_transform_dict = {k - 1: v - 1 for k, v in lines_transform_dict.items()}
    lines_transform_animation = []
    added_lines = set()

    for line_number, line in enumerate(code):
        if line_number in lines_transform_dict and line_number not in added_lines:

            target_line_num = lines_transform_dict[line_number]
            transform_lines = VGroup()
            for key, val in lines_transform_dict.items():
                if val == target_line_num:
                    added_lines.add(key)
                    transform_lines += code[key]

            lines_transform_animation.append(
                TransformMatchingShapes(transform_lines, target_code[lines_transform_dict[line_number]]))
        # else:
        #     lines_transform_animation.append(line.animate.set_opacity(off_opacity))
    return AnimationGroup(*lines_transform_animation, **kwargs)


def create_code(code_str: str, tex=True, colored_func_name=True, **kwargs) -> Code:
    pygments_monkeypatch_style("darcula", DarculaStyle)
    with RegisterFont("JetBrains Mono") as fonts:
        Code.set_default(font="JetBrains Mono")
    rendered_code = Code(code=code_str, tab_width=3, background="window", language="Python",
                         style="darcula", **kwargs).to_corner(LEFT + UP)

    if colored_func_name:
        start_idx = len("def ")
        replace_code = rendered_code.code.chars[0][rendered_code.tab_spaces[0] + start_idx:]
        func_str = "".join([i[0] for i in rendered_code.code_json[0]])[start_idx:]
        func_name_mob = get_func_text(func_str)
        compile_code_tex_line(func_name_mob, func_name_mob.text)
        func_name_mob.match_height(replace_code).move_to(replace_code, aligned_edge=LEFT)
        replace_code.become(func_name_mob)

    if tex and '$' in code_str:
        compile_code_tex(rendered_code, start_line=1)

    rendered_code.scale_to_fit_width(config.frame_width * 0.5).to_corner(LEFT + UP)
    rendered_code.background_mobject[0].set_fill(opacity=0)
    return rendered_code


def compile_code_tex(code: Code, start_line: int = 0, end_line: int = None):
    end_line = code.code.__len__() if end_line is None else end_line
    indent_x = code.code.chars[1][0].get_x()
    for line_no in range(start_line, end_line):
        line = code.code.chars[line_no]
        line_start_idx = code.tab_spaces[line_no]
        compile_code_tex_line(line, "".join([i[0] for i in code.code_json[line_no]]), line_start_idx)
        if line_no != 0:
            for i in range(code.tab_spaces[line_no]):
                line[i].set_x(indent_x)
    code.background_mobject[0].stretch_to_fit_width(  # 0.1 * 3 appears in manim source code
        VGroup(code.code, code.line_numbers).width + 0.1 * 3 + 2 * code.margin, about_edge=LEFT)


def compile_code_tex_line(line_mob, line_str: str, line_start_idx: int = 0, bold_math=True):
    math_strings = find_math_substrings(line_str)
    for string, idx in math_strings:
        idx += line_start_idx
        replace_word = line_mob[idx:idx + len(string)]
        tex_str = r"$\boldsymbol{" + string.strip("$") + r"}$"
        if not bold_math:
            tex_str = r"$" + string.strip("$") + r"$"
        tex = Tex(tex_str).match_height(replace_word[1:-1]).scale(CODE_MATH_SCALE).move_to(replace_word,
                                                                                           aligned_edge=LEFT).set_stroke(
            width=0, opacity=0)
        replace_word[-1].become(tex)
        replace_word[:-1].become(VGroup().scale(0).move_to(tex.get_right()))
        replace_word.set_stroke(width=0, opacity=0)
        line_mob[idx + len(string):].next_to(replace_word[-1], buff=0.05)


def find_math_substrings(string):
    pattern = r'\$(.*?)\$'
    matches = re.findall(pattern, string)
    return [("$" + match + "$", string.index("$" + match + "$")) for match in matches]


def get_func_text(string: str, blue_args: list = None, **kwargs):
    blue_args = [] if blue_args is None else blue_args
    # Find the word before the first bracket
    func_name = string.split("(")[0]

    # Extract all the numbers from the string
    numbers = [int(num) for num in re.findall(r'\d+', string)]

    return Text(string, font="JetBrains Mono",
                t2c={func_name: YELLOW, ",": ORANGE, **({str(num): BLUE_D for num in numbers}),
                     **({arg: BLUE_D for arg in blue_args})}, **kwargs)


# ---------------------------- text --------------------------------
def search_shape_in_text(text: VMobject, shape: VMobject):
    T = TransformMatchingShapes
    results = []
    l = len(shape.submobjects[0])
    shape_aux = VMobject()
    shape_aux.points = np.concatenate([p.points for p in shape.submobjects[0]])
    for j in range(len(text.submobjects)):
        results.append([])
        for i in range(len(text.submobjects[j])):
            subtext = VMobject()
            subtext.points = np.concatenate([p.points for p in text.submobjects[j][i:i + l]])
            if T.get_mobject_key(subtext) == T.get_mobject_key(shape_aux):
                results[j].append(slice(i, i + l))
    return results


def color_tex(equation: Tex | MathTex, t2c: dict, tex_class: type[Tex | MathTex] = Tex):
    for string, color in t2c.items():
        tex = tex_class(string)
        results = search_shape_in_text(equation, tex)
        for i in range(len(results)):
            for result in results[i]:
                equation[i][result].set_color(color)


# ---------------------------- geometry ----------------------------

def boolean_op_to_polygons(boolean_op: _BooleanOps, convex_hull=True, **kwargs) -> Polygon:
    points = np.array([np.copy(bezier(point)(1)) for point in boolean_op.get_cubic_bezier_tuples()])
    # points = np.copy(boolean_op.points)
    # return Polygon(*points, **kwargs)
    points = [points[i] for i in ConvexHull(points[:, :2]).vertices] if convex_hull else [i for i in points]
    # return Polygon(*np.array(points), **kwargs)
    filter_points = [points[0]]
    for i in range(1, len(points)):
        if not np.any(np.all(np.isclose(filter_points, points[i], atol=1.e-1), axis=1)):
            filter_points = np.vstack((filter_points, points[i]))
    return Polygon(*np.array(filter_points), **kwargs)
    tmp_points = np.copy(filter_points)
    G = nx.Graph()  # A graph to hold the nearest neighbours
    points = list(map(tuple, filter_points[:, :2]))
    tree = KDTree(points, leafsize=2)  # Create a distance tree
    found_points = set()
    start_point = next_point = points[0]
    G.add_nodes_from(points)
    while len(found_points) < len(points):
        for dist, ind in zip(*tree.query(next_point, k=len(points))):
            point = tuple(points[ind])
            if point not in found_points:
                G.add_edge(next_point, point)
                found_points.add(point)
                next_point = point
                break
    target_point = next_point
    filter_points = [np.append(p, 0) for p in nx.shortest_path(G, source=start_point, target=target_point)]
    return Polygon(*np.array(filter_points), **kwargs)


def get_convex_hull_polygon(points: np.ndarray, round_radius=0.2, **kwargs) -> Polygon:
    hull = ConvexHull(points[:, :2])
    return Polygon(*[np.append(points[i], 0) for i in hull.vertices], **kwargs).round_corners(radius=round_radius)


def get_tangent_points(polygon_a: Polygon, polygon_b: Polygon) -> list[tuple[int, int]]:
    tangent_points = []
    poly_a_vertices = polygon_a.get_vertices()
    poly_b_vertices = polygon_b.get_vertices()
    for i in range(len(poly_a_vertices)):
        for j in range(len(poly_b_vertices)):
            if np.allclose(poly_a_vertices[i], poly_b_vertices[j]):
                tangent_points.append(poly_a_vertices[i])
    return tangent_points


def get_surrounding_rectangle(mobject_a, mobject_b, **kwargs) -> Rectangle:
    rect_height = np.linalg.norm(mobject_a.get_center() - mobject_b.get_center())
    mobject_b_cp = mobject_b.copy().match_x(mobject_a)
    rect = SurroundingRectangle(VGroup(mobject_a, mobject_b_cp), **kwargs).scale_to_fit_height(rect_height)
    u_v_angle = np.arctan2(mobject_a.get_center()[1] - mobject_b.get_center()[1],
                           mobject_a.get_center()[0] - mobject_b.get_center()[0])
    rect.rotate(u_v_angle, about_point=mobject_a.get_center())
    return rect


def get_frame_center(left: Mobject | np.ndarray = None, right: Mobject | np.ndarray = None,
                     top: Mobject | np.ndarray = None, bottom: Mobject | np.ndarray = None) -> np.ndarray:
    ref_obj = Text(".").scale(0.01)
    left = ref_obj.to_edge(LEFT, buff=0).get_right() if left is None else left if not isinstance(left,
                                                                                                 Mobject) else left.get_right()
    right = ref_obj.to_edge(RIGHT, buff=0).get_left() if right is None else right if not isinstance(right,
                                                                                                    Mobject) else right.get_left()
    top = ref_obj.to_edge(UP, buff=0).get_bottom() if top is None else top if not isinstance(top,
                                                                                             Mobject) else top.get_bottom()
    bottom = ref_obj.to_edge(DOWN, buff=0).get_top() if bottom is None else bottom if not isinstance(bottom,
                                                                                                     Mobject) else bottom.get_top()

    return np.array(
        [Line(left * RIGHT, right * RIGHT, buff=0).get_center()[0], Line(top * UP, bottom * UP, buff=0).get_center()[1],
         0])
