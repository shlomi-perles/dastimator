from __future__ import annotations

from manim import *
from manim import AnimationGroup
from manim_fonts import *
from moviepy.editor import VideoFileClip, concatenate_videoclips
from .consts import LINES_OFF_OPACITY, MEDIA_PATH, BACKGROUND_COLOR
import imageio.v3 as iio

QFLAGS_TO_QUALITY = {v["flag"]: k for k, v in QUALITIES.items() if v["flag"] is not None}
DEFAULT_GIF_SCENES = list(range(1, 3))
SECTIONS_MEDIA_PATH = r"videos/2160p60/sections"
SCENE_CLIP_NAME = "{scene_name}_{section_num:04d}.mp4"
DEFAULT_GIF_RESIZE = 0.1


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
    for scene in scenes_lst:
        with tempconfig(
                {"quality": quality, "preview": preview, "media_dir": media_path, "save_sections": save_sections,
                 "disable_caching": disable_caching}):
            scene().render()
        if create_gif:
            create_scene_gif(media_path, scene.__name__, DEFAULT_GIF_SCENES if gif_scenes is None else gif_scenes)


def create_scene_gif(out_dir: str | Path, scene_name, section_num_lst: list[int]):
    """
    Create a gif from the video file.
    :param out_dir: Name of the directory run_scenes() was called with.
    :param section_num_lst: Number of the section to create a gif from.
    """
    out_dir = Path(out_dir) if isinstance(out_dir, str) else out_dir
    gif_dir = out_dir / "gifs"
    gif_dir.mkdir(parents=True, exist_ok=True)

    clips = [VideoFileClip(str(out_dir / SECTIONS_MEDIA_PATH / SCENE_CLIP_NAME.format(scene_name=scene_name,
                                                                                      section_num=i))).resize(
        DEFAULT_GIF_RESIZE) for i in section_num_lst]

    concatenate_videoclips(clips).write_gif(str(gif_dir / f"{scene_name}.gif"), fps=13)
    # clip.write_gif(gif_path, fps=10)
    # frames = np.vstack(gifs)
    # iio.imwrite(str(gif_dir / f"{scene_name}.gif"), frames, duration=iio.immeta(gif_path)["duration"])


# ---------------------------- Code ----------------------------

def highlight_code_lines(code: Code, lines: list = None, off_opacity: float = LINES_OFF_OPACITY, indicate=True,
                         **kwargs) -> AnimationGroup | tuple[AnimationGroup, AnimationGroup]:
    code = code.code
    lines_highlighted_animation = []
    lines_indicate_animation = []
    lines = list(range(len(code))) if lines is None else lines
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


def create_code(code_str: str):
    with RegisterFont("JetBrains Mono") as fonts:
        Code.set_default(font="JetBrains Mono")
    rendered_code = Code(code=code_str, tab_width=3, background="window", language="Python",
                         style="fruity").to_corner(LEFT + UP)
    rendered_code.scale_to_fit_width(config.frame_width * 0.5).to_corner(LEFT + UP)
    rendered_code.background_mobject[0].set_fill(opacity=0)
    return rendered_code


# --------------------------------- Graphs --------------------------------- #


def get_neighbors(graph: DiGraph, vertex):
    return [neighbor for neighbor in graph.vertices if (vertex, neighbor) in graph.edges]


def create_dist_label(index, graph, label):
    label = MathTex(rf"\mathbf{{{label}}}", color=DISTANCE_LABEL_COLOR)
    if label.width < label.height:
        label.scale_to_fit_height(graph[index].radius * DISTANCE_LABEL_SCALE)
    else:
        label.scale_to_fit_width(graph[index].radius * DISTANCE_LABEL_SCALE)
    return label.move_to(graph[index]).next_to(graph[index][1], RIGHT, buff=DISTANCE_LABEL_BUFFER)
