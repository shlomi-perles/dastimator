from __future__ import annotations

from typing import Hashable
from copy import copy, deepcopy

from tools.array import *
from tools.consts import *
from tools.funcs import *
from tools.scenes import *
from tools.graphs.my_graphs import DiGraph

ROOT_PATH = Path(__file__).resolve().parent
sys.path.append(str(ROOT_PATH.parent))
OUT_DIR = MEDIA_PATH / Path(__file__).resolve().parent.stem

PRESENTATION_MODE = False
DISABLE_CACHING = True


class ArrayExample(SectionsScene):
    def construct(self):
        array = ArrayMob("Array:", *["-", "8", "1", "3", "9"], show_labels=True, labels_pos=DOWN, starting_index=1)
        array.scale_to_fit_width(config.frame_width * 0.6)
        self.play(Write(array))
        self.play(array.at(1, "b"))
        self.play(array.indicate_at(1))
        self.play(array.push(5))
        self.play(array.pop())
        self.play(array.swap(1, 3))

        # create a pointer with a text label
        pointer = TextPointer("Here", 0.8, UP)
        pointer.next_to(array.get_square(1), DOWN)
        self.play(pointer.draw())
        array += pointer

        self.play(pointer.animate.align_to(array.get_square(4), RIGHT))
        self.wait(2)


if __name__ == "__main__":
    scenes_lst = [ArrayExample]

    run_scenes(scenes_lst, OUT_DIR, PRESENTATION_MODE, DISABLE_CACHING, create_gif=False, save_sections=False)
    # create_scene_gif(OUT_DIR, scenes_lst[0].__name__, section_num_lst=[28 + i for i in range(6)])
