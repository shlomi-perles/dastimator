from __future__ import annotations

from tools.array import *
from tools.consts import *
from tools.movie_maker import render_scenes
from tools.scenes import *

ROOT_PATH = Path(__file__).resolve().parent
sys.path.append(str(ROOT_PATH.parent))
OUT_DIR = MEDIA_PATH / Path(__file__).resolve().parent.stem

PRESENTATION_MODE = False
DISABLE_CACHING = True


class ArrayExample(SectionsScene):
    def construct(self):
        self.next_section("arr", pst.NORMAL)
        array = ArrayMob("Array:", "", "8", "1", "3", "9", show_indices=True, indices_pos=DOWN, starting_index=1)
        array.scale_to_fit_width(config.frame_width * 0.6)
        self.play(Write(array))
        self.play(array.animate.at(1, "b"))
        self.play(array.animate.at(1, 3))
        self.play(array.animate.at(1, 2))
        self.play(array.animate.at(1, 5))
        self.play(array.indicate_at(1))
        self.play(array.push(5))
        self.play(array.pop(4))
        self.play(array.swap(1, 3))

        # create a pointer with a text label
        pointer = ArrayPointer("Here", 0.8, UP)
        pointer.next_to(array.get_entry(1), DOWN)
        self.play(Write(pointer))
        array += pointer

        self.play(pointer.animate.align_to(array.get_entry(4), RIGHT))
        self.wait(2)


def make_elements():  # only setting up the mobjects
    dots = VGroup(Dot(), Dot(), Dot(), Dot(), Dot(), Dot(), Dot(), z_index=0)
    dots.arrange(buff=0.7).scale(2).set_color(BLUE)
    dots[0].set_color(ORANGE)
    dots[-1].set_color(ORANGE)
    moving_dot = Dot(color=ORANGE, z_index=1).scale(2.5)
    moving_dot.move_to(dots[0])
    path = VGroup()
    path.add_updater(lambda x: x.become(Line(dots[0], moving_dot, stroke_width=10, z_index=1, color=ORANGE)))
    return dots, moving_dot, path


class MinimalPresentationExample(SectionsScene):
    def construct(self):
        dots, moving_dot, path = make_elements()
        self.add(dots, moving_dot, path)

        self.next_section("A", pst.NORMAL)
        self.play(moving_dot.animate.move_to(dots[1]), rate_func=linear)

        self.next_section("A.1", pst.SUB_NORMAL)
        self.play(moving_dot.animate.move_to(dots[2]), rate_func=linear)

        self.next_section("B", pst.SKIP)
        self.play(moving_dot.animate.move_to(dots[3]), rate_func=linear)

        self.next_section("C", pst.LOOP)
        self.play(moving_dot.animate.move_to(dots[4]), rate_func=linear)

        self.next_section("D", pst.COMPLETE_LOOP)
        self.play(moving_dot.animate.move_to(dots[5]), rate_func=linear)

        self.next_section("E", pst.NORMAL)
        self.play(moving_dot.animate.move_to(dots[6]), rate_func=linear)


if __name__ == "__main__":
    scenes_lst = [ArrayExample]
    # scenes_lst = [MinimalPresentationExample, ArrayExample]

    render_scenes(scenes_lst, OUT_DIR, PRESENTATION_MODE, DISABLE_CACHING, create_gif=False, save_sections=True,
                  quality="low_quality", movie_name="tmp")
    # create_scene_gif(OUT_DIR, scenes_lst[0].__name__, section_num_lst=[28 + i for i in range(6)])
