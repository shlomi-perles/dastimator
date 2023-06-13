from __future__ import annotations

import json
import re
from copy import deepcopy
from typing import Hashable

from manim import *
from manim_fonts import *
from moviepy.editor import VideoFileClip, concatenate_videoclips

from .consts import LINES_OFF_OPACITY, DISTANCE_LABEL_COLOR, DISTANCE_LABEL_SCALE, DISTANCE_LABEL_BUFFER, EDGE_CONFIG, \
    DEFAULT_ARROW_TIP_WIDTH, TIP_SIZE, VERTEX_CONFIG, LABEL_COLOR, VERTEX_LABEL_SCALE
from .graphs.my_graphs import WeightedGraph, DiGraph

QFLAGS_TO_QUALITY = {v["flag"]: k for k, v in QUALITIES.items() if v["flag"] is not None}
QUALITY_TO_DIR = {k: f"{QUALITIES[k]['pixel_height']}p{QUALITIES[k]['frame_rate']}" for k in QUALITIES.keys()}
DEFAULT_GIF_SCENES = list(range(1, 3))
SECTIONS_MEDIA_PATH = r"videos/{quality_dir}/sections"
SCENE_CLIP_NAME = "{scene_name}_{section_num:04d}.mp4"
DEFAULT_GIF_RESIZE = 0.2
CODE_MATH_SCALE = 0.9


def run_scenes(scenes_lst: list, media_path, presentation_mode: bool = False, disable_caching: bool = False,
               preview: bool = True, save_sections: bool = True, quality: str = None, create_gif: bool = None,
               gif_scenes: list = None, **kwargs):
    """Run a list of scenes. This function is used by the manim command line interface.
    Possible quality settings are:
    - fourk_quality [k] 2160X3840
    - production_quality [p] 1440X2560
    - high_quality [h] 1080X1920
    - medium_quality [m] 720X1280
    - low_quality [l] 480X854
    """
    if quality is None:
        quality = "fourk_quality" if presentation_mode else "low_quality"
    else:
        if quality not in QUALITIES and quality not in QFLAGS_TO_QUALITY:
            raise ValueError(f"Invalid quality setting: {quality}")

        quality = QFLAGS_TO_QUALITY[quality] if quality in QFLAGS_TO_QUALITY else quality
    if create_gif is None:
        create_gif = presentation_mode
    if not Path(media_path).exists():
        Path(media_path).mkdir(parents=True, exist_ok=True)
    for scene in scenes_lst:
        with tempconfig(
                {"quality": quality, "preview": preview, "media_dir": media_path, "save_sections": save_sections,
                 "disable_caching": disable_caching}):
            # if isinstance(scene, SectionsScene): #TODO: Fix this
            scene.PRESENTATION_MODE = presentation_mode
            scene().render()
        if create_gif:
            create_scene_gif(media_path, scene.__name__, DEFAULT_GIF_SCENES if gif_scenes is None else gif_scenes,
                             QUALITY_TO_DIR[quality])
    if save_sections:
        manim_editor_autocreated_scene_fix(media_path / SECTIONS_MEDIA_PATH.format(quality_dir=QUALITY_TO_DIR[quality]))


def create_scene_gif(out_dir: str | Path, scene_name, section_num_lst: list[int], quality_dir: str):
    """
    Create a gif from the video file.
    :param out_dir: Name of the directory run_scenes() was called with.
    :param section_num_lst: Number of the section to create a gif from.
    """
    out_dir = Path(out_dir) if isinstance(out_dir, str) else out_dir
    gif_dir = out_dir / "gifs"
    gif_dir.mkdir(parents=True, exist_ok=True)

    clips = [VideoFileClip(str(out_dir / SECTIONS_MEDIA_PATH.format(quality_dir=quality_dir) / SCENE_CLIP_NAME.format(
        scene_name=scene_name, section_num=i))).resize(DEFAULT_GIF_RESIZE) for i in section_num_lst]

    concatenate_videoclips(clips).write_gif(str(gif_dir / f"{scene_name}.gif"), fps=13)


def manim_editor_autocreated_scene_fix(json_path: Path | str):
    json_path = Path(json_path) if isinstance(json_path, str) else json_path
    # create a list of all jsons in this path
    json_files = [j_file for j_file in json_path.glob("*.json")]
    for j_file in json_files:
        section_json = []
        with open(j_file, "r+") as f:
            section_json = json.load(f)
        for i, section in enumerate(section_json):
            if section["name"] == "autocreated":
                if i < len(section_json) - 1:
                    section["name"] = section_json[i + 1]["name"]
                    section_json[i + 1]["type"] = "presentation.sub.normal"
        # write the new json
        with open(j_file, "w") as f:
            json.dump(section_json, f, indent=4)


# ---------------------------- Code ----------------------------

def highlight_code_lines(code: Code, lines: list = None, off_opacity: float = LINES_OFF_OPACITY, indicate=True,
                         **kwargs) -> AnimationGroup | tuple[AnimationGroup, AnimationGroup]:
    code = code.code
    lines_highlighted_animation = []
    lines_indicate_animation = []
    lines = list(range(len(code) + 1)) if lines is None else lines
    for line_number, line in enumerate(code):
        if line_number == 0: continue

        if line_number + 1 in lines:
            if indicate:
                lines_indicate_animation.append(Indicate(line))
            lines_highlighted_animation.append(line.animate.set_opacity(1))
        else:
            lines_highlighted_animation.append(line.animate.set_opacity(off_opacity))
    if indicate:
        return AnimationGroup(*lines_highlighted_animation, **kwargs), AnimationGroup(*lines_indicate_animation,
                                                                                      **kwargs)
    return AnimationGroup(*lines_highlighted_animation, **kwargs)


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


def create_code(code_str: str, tex=True, colored_func_name=True, **kwargs):
    with RegisterFont("JetBrains Mono") as fonts:
        Code.set_default(font="JetBrains Mono")
    rendered_code = Code(code=code_str, tab_width=3, background="window", language="Python",
                         style="fruity", **kwargs).to_corner(LEFT + UP)

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


def compile_code_tex_line(line_mob, line_str: str, line_start_idx: int = 0):
    math_strings = find_math_substrings(line_str)
    for string, idx in math_strings:
        idx += line_start_idx
        replace_word = line_mob[idx:idx + len(string)]
        tex_str = r"$\boldsymbol{" + string.strip("$") + r"}$"
        tex = Tex(tex_str).match_height(replace_word[1:-1]).scale(CODE_MATH_SCALE).move_to(replace_word,
                                                                                           aligned_edge=LEFT)
        replace_word.become(tex)
        line_mob[idx + len(string):].next_to(replace_word, buff=0.05)


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


# --------------------------------- Graphs --------------------------------- #


def get_neighbors(graph: DiGraph, vertex, priority_lst=None):
    priority_lst = graph.vertices if priority_lst is None else priority_lst
    return [neighbor for neighbor in priority_lst if (vertex, neighbor) in graph.edges]


def create_dist_label(index, graph, label):
    label = MathTex(rf"\mathbf{{{label}}}", color=DISTANCE_LABEL_COLOR)
    if label.width < label.height:
        label.scale_to_fit_height(graph[index].radius * DISTANCE_LABEL_SCALE)
    else:
        label.scale_to_fit_width(graph[index].radius * DISTANCE_LABEL_SCALE)
    return label.move_to(graph[index]).next_to(graph[index][1], RIGHT, buff=DISTANCE_LABEL_BUFFER)


def create_graph(vertices: list[Hashable], edges: list[tuple[Hashable, Hashable]],
                 layout: str | dict[Hashable, np.ndarray] = "spring", layout_scale: float = 1.5,
                 directed_graph: bool = False, graph_type=DiGraph, absolute_scale_vertices=False,
                 labels: bool = True,
                 weights: dict[tuple[Hashable, Hashable], float] = None) -> WeightedGraph | DiGraph:
    """
    Create graph and add labels to vertices,
    Note: vertices are 1-indexed
    """
    edges = deepcopy(edges)
    if not directed_graph:
        edges += [(v, u) for u, v in edges]

    edge_config = EDGE_CONFIG.copy()
    if directed_graph:
        edge_configs = {}
        for k, v in edges:
            if (v, k) in edges:
                edge_configs[(k, v)] = EDGE_CONFIG.copy()
            else:
                edge_configs[(k, v)] = EDGE_CONFIG.copy()
                edge_configs[(k, v)]["tip_config"]["tip_length"] = TIP_SIZE
                edge_configs[(k, v)]["tip_config"]["tip_width"] = DEFAULT_ARROW_TIP_WIDTH
        edge_config = edge_configs
    args = dict(vertices=vertices, edges=edges, layout=layout, layout_scale=layout_scale, labels=labels,
                label_fill_color=LABEL_COLOR, vertex_config=VERTEX_CONFIG.copy(), edge_config=edge_config,
                root_vertex=1)

    if weights is not None:
        graph_type = WeightedGraph
        if not directed_graph:
            weights = {**{(v, u): w for (u, v), w in weights.items()}, **weights}
        args["weights"] = weights

    graph = graph_type(**args)
    for i, vertex in enumerate(graph.vertices):
        if not labels:
            if not absolute_scale_vertices:
                graph[vertex].scale_to_fit_height(graph[0].height)
            continue
        label = graph[vertex][1]
        graph[vertex].remove(label)
        label.next_to(graph[vertex], RIGHT, buff=0)
        label.move_to(graph[vertex])
        if not absolute_scale_vertices:
            label.scale(VERTEX_LABEL_SCALE)
        else:
            graph[vertex].scale_to_fit_height(graph[list(graph.vertices.keys())[0]].height)
            label.scale_to_fit_height(graph[vertex].height * 0.5)
        graph[vertex].add(label)

    relative_scale = config.frame_width * 0.4 if graph.width > graph.height else config.frame_height * 0.7
    graph.scale_to_fit_width(relative_scale).move_to(ORIGIN).to_edge(RIGHT, buff=0.2)
    return graph
