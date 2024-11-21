from __future__ import annotations

import json
import re
import shutil

from pathlib import Path

from manim import QUALITIES, Scene, tempconfig
from moviepy.video.compositing.concatenate import concatenate_videoclips
from moviepy.editor import VideoFileClip

from tools.scenes import SectionsScene
from tools.consts import MOVIES_PATH
from typing import List

import manim_editor
from manim_editor.editor import Section, get_project, get_scene
import jinja2
from distutils.dir_util import copy_tree

QFLAGS_TO_QUALITY = {v["flag"]: k for k, v in QUALITIES.items() if v["flag"] is not None}
QUALITY_TO_DIR = {k: f"{QUALITIES[k]['pixel_height']}p{QUALITIES[k]['frame_rate']}" for k in QUALITIES.keys()}
SECTIONS_MEDIA_PATH = r"videos/{quality_dir}/sections"
SCENE_CLIP_NAME = "{scene_name}_{section_num:04d}.mp4"
MANIM_EDITOR_COMMAND = "manedit"
MOVIE_MEDIA_DIR_NAME = "media"
DEFAULT_GIF_RESIZE = 0.2
CUR_DIR = Path(__file__).parent.absolute()


def render_scenes(scenes_lst: list, media_path, presentation_mode: bool = False, disable_caching: bool = False,
                  preview: bool = True, save_sections: bool = True, quality: str = None, overwrite_scenes: bool = True,
                  scenes_to_gif_frames: dict[Scene, list[int]] = None, run_manedit: bool = None, movie_name: str = "",
                  description_title: str = "", description: str = "", **kwargs):
    """Run a list of scenes. This function is used by the manim command line interface.
    Possible quality settings are:
    - fourk_quality [k] 2160X3840
    - production_quality [p] 1440X2560
    - high_quality [h] 1080X1920
    - medium_quality [m] 720X1280
    - low_quality [l] 480X854
    """
    if quality is None:
        quality = "production_quality" if presentation_mode else "low_quality"
    else:
        if quality not in QUALITIES and quality not in QFLAGS_TO_QUALITY:
            raise ValueError(f"Invalid quality setting: {quality}")

        quality = QFLAGS_TO_QUALITY[quality] if quality in QFLAGS_TO_QUALITY else quality

    if scenes_to_gif_frames is None:
        scenes_to_gif_frames = {}
    if run_manedit is None:
        run_manedit = presentation_mode
    if not Path(media_path).exists():
        Path(media_path).mkdir(parents=True, exist_ok=True)
    jsons_path = media_path / SECTIONS_MEDIA_PATH.format(quality_dir=QUALITY_TO_DIR[quality])

    for scene in scenes_lst:
        if not overwrite_scenes and jsons_path.with_name(scene.__name__ + ".mp4").exists():
            continue

        with tempconfig(
                {"quality": quality, "preview": preview, "media_dir": media_path, "save_sections": save_sections,
                 "disable_caching": disable_caching}):
            scene_obj = scene()
            if isinstance(scene_obj, SectionsScene):
                scene_obj.PRESENTATION_MODE = presentation_mode
            scene_obj.render()
        if scene in scenes_to_gif_frames:
            create_scene_gif(MOVIES_PATH / movie_name, scene.__name__, scenes_to_gif_frames[scene],
                             QUALITY_TO_DIR[quality], media_path, gif_name=movie_name)

    if save_sections:
        manim_editor_autocreated_scene_fix(jsons_path)

    if run_manedit:
        if movie_name == "":
            raise ValueError("movie_name must be specified when run_manedit is True")
        run_manim_editor(scenes_lst, jsons_path, movie_name, description_title, description)
        reorder_manedit_dirs_structure(MOVIES_PATH / movie_name)


def create_scene_gif(out_dir: str | Path, scene_name, section_num_lst: list[int], quality_dir: str, media_dir=None,
                     gif_name: str = None):
    """
    Create a gif from the video file.
    :param media_dir:
    :param out_dir: Name of the directory run_scenes() was called with.
    :param section_num_lst: Number of the section to create a gif from.
    """
    if gif_name is None:
        gif_name = scene_name
    out_dir = Path(out_dir) if isinstance(out_dir, str) else out_dir
    gif_dir = out_dir / "gifs"
    gif_dir.mkdir(parents=True, exist_ok=True)

    clips = [VideoFileClip(str(media_dir / SECTIONS_MEDIA_PATH.format(quality_dir=quality_dir) / SCENE_CLIP_NAME.format(
        scene_name=scene_name, section_num=i))).resize(DEFAULT_GIF_RESIZE) for i in section_num_lst]

    concatenate_videoclips(clips).write_gif(str(gif_dir / f"{gif_name}.gif"), fps=13)


def run_manim_editor(scenes_lst: list, jsons_path: Path | str, movie_name: str, description_title: str = "",
                     description: str = ""):
    jsons_path = Path(jsons_path) if isinstance(jsons_path, str) else jsons_path
    section_index_paths = [(jsons_path / scene.__name__).with_suffix(".json") for scene in scenes_lst]
    run_quick_present_export(section_index_paths, movie_name, description_title, description)


def reorder_manedit_dirs_structure(movie_path: Path | str):
    movie_path = Path(movie_path) if isinstance(movie_path, str) else movie_path
    # create media dir if not exists
    media_dir = movie_path / MOVIE_MEDIA_DIR_NAME
    media_dir.mkdir(parents=True, exist_ok=True)

    # move all files end with .mp4 or .jpg to media dir
    for file in movie_path.glob("*.mp4"):
        shutil.move(file, media_dir)
    for file in movie_path.glob("*.jpg"):
        shutil.move(file, media_dir)

    # replace all "data-video="video" to "data-video="media/video" in all index.html file
    index_html = movie_path / "index.html"
    with open(index_html, "r+", encoding="utf-8") as f:
        content = f.read()
        content = content.replace('data-video="video', f'data-video="{MOVIE_MEDIA_DIR_NAME}/video')
        for match in re.findall(r'<img src="thumb_(\d+).jpg"', content):
            content = content.replace(f'<img src="thumb_{match}.jpg"',
                                      f'<img src="{MOVIE_MEDIA_DIR_NAME}/thumb_{str(int(match) - 1).zfill(4)}.jpg"')
        f.seek(0)
        f.write(content)
        f.truncate()


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
                print(f"Found autocreated section in {j_file.name} at index {i}")
                if i < len(section_json) - 1:
                    section["name"] = section_json[i + 1]["name"]
                    section_json[i + 1]["type"] = "presentation.sub.normal"
        # write the new json
        with open(j_file, "w") as f:
            json.dump(section_json, f, indent=4)


# ----------------------------------- manim editor -----------------------------------
def run_quick_present_export(section_index_paths: List[Path], movie_name: str, description_title: str = "",
                             description: str = ""):
    """Create a project from scene(s) and export the presentation.
    Using the name of the first project if ``project_name`` is not given.
    """
    manim_editor.set_config(manim_editor.config.Config)
    movie_dir = MOVIES_PATH / movie_name
    movie_dir.mkdir(parents=True, exist_ok=True)
    out_media_dir = movie_dir / MOVIE_MEDIA_DIR_NAME
    out_media_dir.mkdir(parents=True, exist_ok=True)

    sections: List[Section] = []
    for section_index_path in section_index_paths:
        scene = get_scene(section_index_path, 0)
        if scene is None:
            raise RuntimeError(f"Couldn't find a section index file at '{section_index_path}'.")
        sections += scene.sections

    if not populate_project_with_loaded_sections(movie_name, movie_dir, out_media_dir, sections):
        raise RuntimeError("Failed to populate project.")

    slides = get_project(movie_dir)[-1]
    if movie_name is None:
        raise RuntimeError("Failed to load project.")
    export_movie(movie_name, movie_dir, slides, description_title, description)


def populate_project_with_loaded_sections(movie_name: str, movie_dir: Path, out_media_dir: Path,
                                          sections: List[Section]) -> bool:
    if not len(sections):
        raise RuntimeError(f"No sections given for project '{movie_name}'.")
    if sections[0].is_sub_section:
        raise RuntimeError(f"The first section of project '{movie_name}' can't be a sub section.")

    # load slides
    slides: List[manim_editor.editor.presentation_classes.Slide] = []
    for id, section in enumerate(sections):
        # add subsection
        if section.is_sub_section:
            if not slides[-1].populate_sub_section(section):
                return False
        else:
            # set main section
            slides.append(manim_editor.editor.presentation_classes.Slide())
            if not slides[-1].populate_main_section(section, out_media_dir, id):
                return False

    for slide in slides:
        for section in slide.sections:
            section.project_name = movie_name

    # write project file
    with open(movie_dir / "project.json", "w") as file:
        json.dump([slide.get_dict() for slide in slides], file, indent=4)
    return True


def export_movie(movie_name: str, movie_dir: Path,
                 slides: List[manim_editor.editor.presentation_classes.Slide], description_title="",
                 description="") -> None:
    print(f"Exporting Movie '{movie_name}' as presentation.")
    jinja2_env = jinja2.Environment(
        loader=jinja2.FileSystemLoader(
            [
                CUR_DIR / "app" / "templates",
                CUR_DIR / "app" / "main" / "templates",
                CUR_DIR / "app" / "error" / "templates",
            ]
        ),
        autoescape=jinja2.select_autoescape(["html"]),
    )

    html = jinja2_env.get_template("edit_project.html").render(
        present_export=True, version=manim_editor.editor.config.get_config().VERSION, name=movie_name, slides=slides,
        url_for=manim_editor.editor.edit_project.emulate_url_for, description_title=description_title,
        description=description)
    with open(movie_dir / "index.html", "w", encoding="utf-8") as file:
        file.write(html)
    print(f"Movie is ready at '{Path(movie_name).absolute()}'")
