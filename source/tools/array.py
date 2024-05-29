from __future__ import annotations

from manim import *
from typing import Callable, Iterable, Union

__all__ = ["ArrayMob", "ArrayPointer"]


class ArrayEntry(VGroup):
    DEFAULT_CHAR = "-"
    VALS_HEIGHT_FACTOR = 0.65
    INDICES_BUFF = 0.12

    def __init__(self, value: float | str, index: int | MathTex | Tex | Text, index_scale: float = 1,
                 frame_type: Callable = Square,
                 index_pos: Iterable = np.copy(DOWN), frame_config: dict = None, value_config: dict = None,
                 index_config: dict = None, **kwargs):
        super().__init__(**kwargs)

        self.value_config = {} if value_config is None else value_config
        self.index_config = {} if index_config is None else index_config
        self.frame_config = {} if frame_config is None else frame_config
        self.frame_type = frame_type
        self.value = value
        self.index = index
        self.index_scale = index_scale

        self.index_pos = index_pos

        self._create_arr_entry(value, index)

    def get_value(self):
        return self.value

    def _create_arr_entry(self, value: float | str, index: int | MathTex | Tex | Text):
        self.frame = self.frame_type(**self.frame_config)
        self.value_mob = Tex(ArrayEntry.DEFAULT_CHAR if value in {None, ""} else str(value), **self.value_config)
        self.index_mob = index if isinstance(index, (MathTex, Tex, Text)) else Text(
            ArrayEntry.DEFAULT_CHAR if index in {None, ""} else str(index), **self.index_config)

        if value in {None, ""}:
            self.value_mob.set_opacity(0).scale(0.2)
        if index in {None, ""}:
            self.index_mob.set_opacity(0).scale(0.2)

        self.place_value()

        if self.index:
            self.place_index()

        self.add(self.frame, self.value_mob, self.index_mob)

    def set_value(self, value: float | str):
        self.value = value
        self.value_mob.become(Tex(ArrayEntry.DEFAULT_CHAR if value in {None, ""} else str(value), **self.value_config))
        if value in {None, ""}:
            self.value_mob.set_opacity(0).scale(0.2)
        self.place_value()
        return self

    def set_index(self, index: int | MathTex | Tex | Text):
        self.index = index
        self.index_mob.become(index if isinstance(index, (MathTex, Tex, Text)) else Text(
            ArrayEntry.DEFAULT_CHAR if index in {None, ""} else str(index), **self.index_config))
        if index in {None, ""}:
            self.index_mob.set_opacity(0).scale(0.2)
        self.place_index()
        return self

    def place_value(self):
        self.value_mob.move_to(self.frame)
        if self.value_mob.width < self.value_mob.height:
            self.value_mob.scale_to_fit_height(self.frame.height * ArrayEntry.VALS_HEIGHT_FACTOR)
        else:
            self.value_mob.scale_to_fit_width(self.frame.width * ArrayEntry.VALS_HEIGHT_FACTOR)
        if self.value in {None, ""}:
            self.value_mob.scale(0.1)
        return self

    def place_index(self):
        self.index_mob.scale_to_fit_height(
            self.frame.height * 0.18 * self.index_scale).next_to(self.frame, self.index_pos, buff=-(
                self.index_mob.height + self.INDICES_BUFF)).align_to(self.frame, RIGHT).shift(
            LEFT * self.INDICES_BUFF)
        return self


class ArrayMob(VGroup):
    """
        Array Object
        Parameters
        ----------
        name:
            Name of the array. It's rendered when draw_array is called.
        values:
            The elements to be contained in the array
        name_config:
            Additional configuration to the Tex object that is the name
            of the array
        kwargs:
            Additional configurations to the object as inheriting from
            VMobject

        Usage Example:
        --------------
        array = ArrayMob("Array:", "-", "8", "1", "3", "9", show_indices=True, indices_pos=DOWN, starting_index=1)
        array.scale_to_fit_width(config.frame_width * 0.6)
        self.play(Write(array))
        self.play(array.animate.at(1, "b"))
        self.play(array.indicate_at(1))
        self.play(array.push(5))
        self.play(array.pop(4))
        self.play(array.swap(1, 3))

        # create a pointer with a text label
        pointer = TextPointer("Here", 0.8, UP)
        pointer.next_to(array.get_entry(1), DOWN)
        self.play(Write(pointer))
        array += pointer

        self.play(pointer.animate.align_to(array.get_entry(4), RIGHT))
        self.wait(2)

    """

    def __init__(self, name: str, *array, name_config=None, arr_scale: float = 1, name_scale: float = 1,
                 show_indices: bool = False, indices_pos: Iterable = np.copy(UP), indices_scale: float = 1,
                 starting_index: int = 0, align_point: Iterable = np.copy(ORIGIN), **kwargs):
        super().__init__(name=name, **kwargs)

        name_config = {} if name_config is None else name_config
        self.name = name
        self.array = array
        self.name_config = name_config
        self.name_mob = None
        self.arr_scale = arr_scale
        self.name_scale = name_scale
        self.show_indices = show_indices
        self.indices_pos = indices_pos
        self.indices_scale = indices_scale
        self.entries = VGroup()
        self.align_point = np.copy(align_point)
        self.starting_index = starting_index
        self.array_args = kwargs

        self.obj_ref = None
        self.height_ref = None
        self.relative_entry = None
        self._create_array()

        self.center()

    def _create_array(self):
        """Creates the objects for each element in the array."""
        self.name_mob = Tex(self.name, font_size=3.5 * DEFAULT_FONT_SIZE * self.name_scale, **self.name_config)
        self.obj_ref = Tex(":", font_size=3.5 * DEFAULT_FONT_SIZE * self.name_scale, **self.name_config).set_opacity(0)
        self.height_ref = self.obj_ref.height
        self.add(VGroup(self.name_mob))

        for index, val in enumerate(self.array, self.starting_index):
            self.entries += ArrayEntry(val, index if self.show_indices else "", index_scale=self.indices_scale,
                                       frame_config=self.array_args.get("frame_config", {}),
                                       value_config=self.array_args.get("value_config", {}),
                                       index_config=self.array_args.get("indices_config", {}))

        self.entries.arrange(buff=0)

        self.add(*self.entries)
        self.name_mob.next_to(self.align_point, LEFT, buff=0)
        self.entries.next_to(self.name_mob, direction=RIGHT, buff=0.5)

        self.relative_entry = ArrayEntry(0, 0).set_opacity(0).move_to(self.entries[0])
        self[0] += VGroup(self.relative_entry, self.obj_ref)

    def get_entry(self, index: int) -> ArrayEntry:
        return self.entries[index - self.starting_index]

    # TODO: implement update_indices
    def pop(self, index: int = None, shift=DOWN, update_indices=False, **kwargs) -> AnimationGroup:
        """
        Pops an element from the array.
        :param shift: The direction of the shift.
        :param index: The index of the element to be popped.
        :param kwargs: Additional arguments to the AnimationGroup.
        :return: The AnimationGroup of the pop animation.
        """
        index = len(self.entries) + self.starting_index - 1 if index is None else index
        if "lag_ratio" not in kwargs:
            kwargs["lag_ratio"] = 1

        animations = []

        pop_entry = self.get_entry(index)
        # Fade out the element with the given index
        animations.append(FadeOut(pop_entry, shift=shift))

        self.remove(pop_entry)
        self.entries.remove(pop_entry)

        if len(self.entries) == 0:
            return AnimationGroup(*animations, **kwargs)

        shift_entries = VGroup(*[self.get_entry(i) for i in range(index, len(self.entries) + self.starting_index)])

        if index != self.starting_index:
            animations.append(
                AnimationGroup(shift_entries.animate.next_to(self.get_entry(index - 1), direction=RIGHT, buff=0)))
        else:
            animations.append(
                AnimationGroup(shift_entries.animate.next_to(self.relative_entry.get_left(), direction=RIGHT, buff=0)))

        return AnimationGroup(*animations, **kwargs)

    # TODO: update indices
    def push(self, value: int | str, side: np.ndarray = RIGHT, **kwargs) -> Animation:
        """
        Pushes an element to the array.
        :param value: The value of the element to be pushed.
        :param side: The side from which the element will be pushed.
        :param kwargs: Additional arguments to the AnimationGroup.
        :return: The AnimationGroup of the push animation.
        """
        side = np.array(side)
        new_entry = ArrayEntry(value, len(self.entries) + self.starting_index if self.show_indices else "",
                               index_scale=self.indices_scale,
                               frame_config=self.array_args.get("frame_config", {}),
                               value_config=self.array_args.get("value_config", {}),
                               index_config=self.array_args.get("indices_config", {})).match_height(self.relative_entry)

        if len(self) <= 1 or np.allclose(side, LEFT):
            new_entry.move_to(self.relative_entry)
        else:
            new_entry.next_to(self.entries[-1], direction=side, buff=0)

        if np.allclose(side, LEFT):
            self.entries.insert(0, new_entry)
            self.insert(1, new_entry)
            return AnimationGroup(FadeIn(new_entry, shift=-side, run_time=1, **kwargs), self.entries[1:].animate(
                run_time=1).next_to(self.relative_entry, direction=RIGHT, buff=0), run_time=1)
        else:
            self.entries.add(new_entry)
            self.add(new_entry)
            return FadeIn(new_entry, shift=-side, **kwargs)

    def indicate_at(self, index: int, color: str = YELLOW, preserve_color: bool = True, **kwargs) -> AnimationGroup:
        """Used to indicate an element at a given index."""
        if preserve_color:
            self.get_entry(index).set_color(color)
        for i in range(len(self.entries)):
            if i != index:
                self.get_entry(index).set_z_index(self.get_z_index() + 1)

        return AnimationGroup(Indicate(self.get_entry(index), **kwargs))

    def at(self, index: int, value: Union[float, str, "VMobject"]) -> ArrayEntry:
        """Changes the value of an element at a given index."""
        return self.get_entry(index).set_value(value)

    # TODO: update array indexes
    def swap(self, i: int, j: int, path_args: dict = None, **kwargs) -> AnimationGroup:
        """Swaps the elements at indices i and j."""
        path_args = path_args or {}
        i, j = (j, i) if i > j else (i, j)
        right_path = ArcBetweenPoints(self.get_entry(i).get_center(), self.get_entry(j).get_center(), angle=TAU / 3)
        left_path = ArcBetweenPoints(self.get_entry(j).get_center(), self.get_entry(i).get_center(), angle=TAU / 3)
        ret = AnimationGroup(MoveAlongPath(self.get_entry(i), right_path, **path_args),
                             MoveAlongPath(self.get_entry(j), left_path, **path_args), **kwargs)
        a, b = i - self.starting_index, j - self.starting_index
        self.entries[a], self.entries[b] = self.entries[b], self.entries[a]
        self[a + 1], self[b + 1] = self[b + 1], self[a + 1]
        return ret


class ArrayPointer(Vector):
    def __init__(self, array: ArrayMob, index: int, text: str | Mobject = None, text_scale: float = 0.6,
                 direction: np.ndarray = DOWN, change_val_color: bool = True, val_color: str = None,
                 text_args=None, **kwargs):
        kwargs["color"] = YELLOW if "color" not in kwargs else kwargs["color"]
        super().__init__(direction, **kwargs)
        self.index = index
        self.array = array
        self.arrow = self[0]
        self.change_val_color = change_val_color
        self.val_color = kwargs.get("color", YELLOW) if val_color is None else val_color
        self.zero_base_z_index = self.array.get_z_index()
        self.array.get_entry(self.index).set_z_index(self.zero_base_z_index + 1)
        self._position_arrow()
        self.text_args = {} if text_args is None else text_args
        self.text_scale = text_scale
        self.text = self._get_text_mob(text, **self.text_args)
        self.add(self.text)

    def write_arrow(self) -> AnimationGroup:
        self._color_val(self.index)
        return AnimationGroup(Write(self), self.array.indicate_at(self.index, scale_factor=1))

    def _get_text_mob(self, text: str | Mobject, **kwargs):
        text = Text(".").set_opacity(0) if text in {None, ""} else text
        text = text if isinstance(text, Mobject) else MathTex(str(text), **kwargs)
        text.next_to(self.arrow, direction=-self.get_vector(), buff=0.1).set_color(self.get_color())
        return text

    def to_entry(self, index: int, text: str | Mobject = None, change_val_color=None, **kwargs):
        anims = []
        if change_val_color is True or (self.change_val_color and change_val_color is None):
            anims.append(self.array.get_entry(self.index).animate.set_color(
                self.array.relative_entry.value_mob.get_color()).set_z_index(self.zero_base_z_index))
            if self.index + 1 - self.array.starting_index < len(self.array.entries):
                anims.append(self.array.get_entry(self.index + 1).animate.shift(ORIGIN))

            if self.index - 1 - self.array.starting_index < len(self.array.entries):
                anims.append(self.array.get_entry(self.index - 1).animate.shift(ORIGIN))

            anims.append(
                self.array.get_entry(index).animate.set_color(self.val_color).set_z_index(self.zero_base_z_index + 1))

        self.index = index

        if text is not None:
            anims.append(self.text.animate.become(self._get_text_mob(text, **self.text_args)))
        return AnimationGroup(*anims, self.animate._position_arrow(), **kwargs)

    def _position_arrow(self, **kwargs):
        return self.next_to(self.array.get_entry(self.index), direction=-self.get_vector(), **kwargs)

    def _color_val(self, index: int):
        new_entry, prev_entry = self.array.get_entry(index), self.array.get_entry(self.index)

        prev_entry.value_mob.set_color(self.array.relative_entry.value_mob.get_color())
        prev_entry.frame.set_color(self.array.relative_entry.frame.get_color())
        new_entry.value_mob.set_color(self.val_color)
        new_entry.frame.set_color(self.val_color)
        new_entry.set_z_index(self.zero_base_z_index + 1)
        prev_entry.set_z_index(self.zero_base_z_index)
