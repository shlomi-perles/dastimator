from __future__ import annotations

from manim import *
from tools.array import ArrayEntry

DEFAULT_HASH_ARROWS_COLOR: ManimColor = YELLOW


class HashTable(VGroup):
    def __init__(self, keys_size: int, array_size: int, hash_func: Callable[[int], int],
                 keys_array_gap_size: float = 2.5, arrows_config: dict = None, **kwargs):
        super().__init__(**kwargs)
        self.keys_size = keys_size
        self.array_size = array_size
        self.hash_func = hash_func
        self.keys = VGroup(
            *[ArrayEntry(
                r"$\vdots$" if i == keys_size - 1 else r'$x_{\left|U\right|}$' if i == keys_size else fr"$x_{{{i}}}$",
                "", index_scale=1.4) for i in range(1, keys_size + 1)]).arrange(DOWN, buff=0)
        self.array = VGroup(*[ArrayEntry(r"$\vdots$" if i == array_size - 1 else "",
                                         "m" if i == array_size else "" if i == array_size - 1 else i,
                                         index_scale=1.4) for i in range(1, array_size + 1)]).arrange(DOWN, buff=0)
        self.array.move_to(self.keys.get_center() + keys_array_gap_size * self.array.width * RIGHT)
        arrows_config = arrows_config if arrows_config is not None else {}
        self.arrows_config = {"tip_length": 0.5, "stroke_width": 6, "buff": 0, "color": DEFAULT_HASH_ARROWS_COLOR,
                              **arrows_config}
        self.arrows = VGroup(*[Arrow(LEFT, RIGHT, **self.arrows_config) for _ in range(keys_size - 1)])
        self.rehash(hash_func)

        round_radius = 0.8
        self.round_keys_frame(round_radius)

        self.add(self.keys, self.array, self.arrows)
        self.scale_to_fit_height(config.frame_height * 0.6).center()

    def get_arrow(self, i: int) -> Arrow:
        if i == self.keys_size - 2 or i >= self.keys_size:
            raise Exception("Invalid arrow index")
        return self.arrows[i if i < self.keys_size - 2 else self.keys_size - 2]

    def round_keys_frame(self, round_radius):
        top_orig_frame = self.keys[0].frame
        top_round_rect = top_orig_frame.copy().stretch_to_fit_height(top_orig_frame.get_height() * 1.5).round_corners(
            round_radius).next_to(top_orig_frame.get_top(), DOWN, buff=0)
        top_orig_frame.next_to(self.keys[1].frame.get_top(), DOWN, buff=0)
        custom_rect = Difference(top_round_rect, top_orig_frame)
        top_orig_frame.become(custom_rect)

        bottom_orig_frame = self.keys[-1].frame
        bottom_round_rect = bottom_orig_frame.copy().stretch_to_fit_height(
            bottom_orig_frame.get_height() * 1.5).round_corners(
            round_radius).next_to(bottom_orig_frame.get_bottom(), UP, buff=0)
        bottom_orig_frame.next_to(self.keys[-2].frame.get_bottom(), UP, buff=0)
        custom_rect = Difference(bottom_round_rect, bottom_orig_frame)
        bottom_orig_frame.become(custom_rect)

    def rehash(self, hash_func: Callable[[int], int]):
        self.hash_func = hash_func
        for i in range(self.keys_size):
            if i == self.keys_size - 2: continue
            self.get_arrow(i).put_start_and_end_on(
                self.keys[i].get_right(), self.array[hash_func(i)].get_left() + 0.1 * LEFT)
        return self

    def get_chaining(self) -> dict[int, VGroup]:
        linked_lists = {}
        for i in range(self.keys_size):
            if i == self.keys_size - 2: continue
            array_idx = self.hash_func(i)
            if array_idx not in linked_lists:
                linked_lists[array_idx] = VGroup()
            array_entry = self.array[array_idx]
            link = Arrow
            link_args = {"tip_length": 0.2, "stroke_width": 4, "buff": 0}
            right_anchor = array_entry.get_right()
            if len(linked_lists[array_idx]) != 0:
                link = Line
                link_args = {"stroke_width": 4}
                right_anchor = linked_lists[array_idx][-1].get_right()

            linked_lists[array_idx] += link(right_anchor, right_anchor + array_entry.width * 0.7 * RIGHT,
                                            **link_args)
            linked_lists[array_idx] += ArrayEntry(
                r'$x_{\left|U\right|}$' if i == self.keys_size - 1 else fr"$x_{{{i + 1}}}$",
                "").scale_to_fit_width(array_entry.width * 0.7).next_to(linked_lists[array_idx][-1], RIGHT, buff=0)
        return linked_lists
