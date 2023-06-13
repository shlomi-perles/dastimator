from __future__ import annotations

from manim import *
from typing import Callable, Iterable, List, Optional, Sequence, Union
from copy import copy, deepcopy

__all__ = ["ArrayMob", "Pointer", "TextPointer"]


class ArrayMob(VGroup):
    # TODO: create a class for the array entry
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

    """
    VALS_HEIGHT_FACTOR = 0.65
    LABELS_BUFF = 0.04

    def __init__(self, name: str, *array, name_config=None, arr_scale: float = 1, name_scale: float = 1,
                 show_labels: bool = False, labels_pos: Iterable = UP, labels_scale: float = 1, starting_index: int = 0,
                 align_point: Iterable = ORIGIN, **kwargs):
        super().__init__(name=name, **kwargs.pop("vgroup_config", {}))

        name_config = {} if name_config is None else name_config
        self.name = name
        self.array = array
        self.name_config = name_config
        self.array_name = None
        self.arr_scale = arr_scale
        self.name_scale = name_scale
        self.show_labels = show_labels
        self.labels_pos = labels_pos
        self.labels_scale = labels_scale
        self.labels = VGroup()
        self.squares = VGroup()
        self.vals_texts = VGroup()
        self.align_point = np.copy(align_point)
        self.starting_index = starting_index
        self.create_array_args = kwargs

        self.obj_ref = None
        self.height_ref = None

        self.relative_entry = None
        self.create_array()

        square, val_text, label = self.create_arr_entry(0, 0)
        square.add(val_text)
        square.add(label)
        self.relative_entry = square.set_opacity(0).next_to(self.array_name, direction=RIGHT)
        self.add(self.relative_entry)
        self.center()

    def create_array(self):
        """Creates the objects for each element in the array."""
        self.array_name = Tex(self.name, font_size=DEFAULT_FONT_SIZE * self.name_scale, **self.name_config)
        self.obj_ref = Tex(":", font_size=DEFAULT_FONT_SIZE * self.name_scale, **self.name_config)
        self.height_ref = self.obj_ref.height
        self.add(self.array_name)

        for index, val in enumerate(self.array):
            square, val_text, label = self.create_arr_entry(val, index)

            square.add(val_text)
            square.add(label)
            self.squares.add(square)
            if self.show_labels:
                self.labels.add(label)
            self.vals_texts.add(val_text)

        self.squares.arrange(buff=0)

        self.add(*self.squares)
        self.add(*self.vals_texts)
        self.array_name.next_to(self.align_point, LEFT, buff=0)
        # self.array_name.align_to(self.align_point, RIGHT)
        # self.squares.next_to(self.array_name.get_right(), direction=RIGHT, aligned_edge=LEFT)
        self.squares.next_to(self.array_name, direction=RIGHT, buff=DEFAULT_MOBJECT_TO_MOBJECT_BUFFER)

    def draw_array(self, **kwargs):
        """Draws the array. Returns a list of the array's animations."""
        if "lag_ratio" not in kwargs:
            kwargs["lag_ratio"] = 0.3

        all_anims = [Write(self.array_name)]
        all_anims += [Write(square) for square in self.squares]
        return AnimationGroup(*all_anims, **kwargs)

    # TODO: implement update_labels
    def pop(self, index: int = 0, shift=DOWN, update_labels=False, **kwargs) -> AnimationGroup:
        """
        Pops an element from the array.
        :param shift: The direction of the shift.
        :param index: The index of the element to be popped.
        :param kwargs: Additional arguments to the AnimationGroup.
        :return: The AnimationGroup of the pop animation.
        """
        if "lag_ratio" not in kwargs:
            kwargs["lag_ratio"] = 1

        animations = []

        # Fade out the element with the given index
        animations.append(
            AnimationGroup(FadeOut(self.squares[index], shift=shift), FadeOut(self.vals_texts[index], shift=shift)))

        self.remove(self.squares[index])
        self.remove(self.labels[index])
        self.remove(self.vals_texts[index])

        if len(self.squares) - 1 == 0:
            self.squares = VGroup()
            self.vals_texts = VGroup()
            return AnimationGroup(*animations, **kwargs)

        self.squares.remove(self.squares[index])
        self.labels.remove(self.labels[index])
        self.vals_texts.remove(self.vals_texts[index])

        if index != 0:
            animations.append(
                AnimationGroup(self.squares[index:].animate.next_to(self.squares[index - 1], direction=RIGHT, buff=0)))
        else:
            animations.append(AnimationGroup(
                self.squares[index:].animate.next_to(self.relative_entry.get_left(), direction=RIGHT, buff=0), ))

        return AnimationGroup(*animations, **kwargs)

    def push(self, value: int | str, side: np.ndarray = RIGHT, **kwargs) -> Animation:
        """
        Pushes an element to the array.
        :param value: The value of the element to be pushed.
        :param kwargs: Additional arguments to the AnimationGroup.
        :return: The AnimationGroup of the push animation.
        """
        side = np.array(side)
        square, val_text, label = self.create_arr_entry(value, index=len(self.squares))
        square.add(label)
        self.labels.add(label)

        if len(self.squares) == 0:
            square.next_to(self.array_name, direction=RIGHT)
        elif (side == RIGHT).all():
            square.move_to(self.squares[-1].get_right(), aligned_edge=LEFT)
        else:  # equal LEFT
            square.move_to(self.squares[0])

        val_text.move_to(square)
        square.remove(label)
        square.add(val_text)
        square.add(label)

        if (side == LEFT).all():
            def on_finish(scene: Scene):
                self.squares.add_to_back(square)
                self.vals_texts.add_to_back(val_text)
                self.add_to_back(square)
                self.add_to_back(val_text)

            relative_pos = square.copy().move_to(self.squares[0].get_left(), aligned_edge=RIGHT).get_center()
            return AnimationGroup(FadeIn(square, target_position=relative_pos, **kwargs),
                                  self.squares.animate.move_to(square.get_right(), aligned_edge=LEFT),
                                  group=self, _on_finish=on_finish, **kwargs)

        self.squares.add(square)
        self.vals_texts.add(val_text)
        self.add(square)
        self.add(val_text)
        return FadeIn(square, shift=-side, **kwargs)

    def create_arr_entry(self, value, index) -> tuple[VGroup, Tex, VGroup]:
        square = Square(**self.create_array_args.pop("square_config", {})).scale_to_fit_height(
            self.height_ref * self.arr_scale * 3)
        if self.relative_entry is not None:
            square.match_height(self.relative_entry)
        val_text = Tex("" if value is None else str(value), **self.create_array_args.pop("value_config", {}))
        if val_text.width < val_text.height:
            val_text.scale_to_fit_height(square.height * ArrayMob.VALS_HEIGHT_FACTOR)
        else:
            val_text.scale_to_fit_width(square.width * ArrayMob.VALS_HEIGHT_FACTOR)
        label = VGroup()
        if self.show_labels:
            label = self.create_label(index, square)
        return VGroup(square), val_text, label

    def create_label(self, index: int, square: Square):
        label = Text(str(index + self.starting_index)).match_height(square).scale(0.2 * self.labels_scale)
        if self.relative_entry is None:
            label.next_to(square, self.labels_pos, buff=-(label.height + self.LABELS_BUFF)).align_to(
                square, RIGHT).shift(LEFT * self.LABELS_BUFF)
        else:
            label.match_y(self.relative_entry[2]).set_x(square.get_x()).shift(
                RIGHT * (self.relative_entry[2].get_x() - self.relative_entry[0].get_x()))
        return label

    def get_square(self, index: int) -> VGroup:
        """Get the square object of an element with a given index."""
        return self.squares[index]

    def indicate_at(self, index: int, change_color: bool = True, **kwargs) -> AnimationGroup:
        """Used to indicate an element at a given index."""
        if change_color:
            self.squares[index].set_color(YELLOW)
            self.vals_texts[index].set_color(YELLOW)
        for i in range(len(self.squares)):
            if i != index:
                self.squares[index].set_z_index(1)
                self.vals_texts[index].set_z_index(1)

        return AnimationGroup(Indicate(self.squares[index]), Indicate(self.vals_texts[index]))

    def at(self, index: int, value: Union[float, str, "VMobject"]) -> Animation:
        """Changes the value of an element at a given index."""
        val_text = Tex("" if value is None else f"{value}", **self.create_array_args.pop("value_config", {}))

        old_element = self.vals_texts[index]
        if val_text.width < val_text.height:
            val_text.set_height(
                (self.squares[index].get_top()[1] - self.squares[index].get_bottom()[1]) * ArrayMob.VALS_HEIGHT_FACTOR)
        else:
            val_text.set_width(
                (self.squares[index].get_left()[0] - self.squares[index].get_right()[0]) * ArrayMob.VALS_HEIGHT_FACTOR)

        val_text.move_to(self.squares[index])

        if old_element.tex_string == "":
            self.squares[index].remove(old_element)
            self.remove(old_element)
            # self.squares[index].add(val_text) # TODO: handle bug
            self.vals_texts[index] = val_text
            self.add(val_text)
            return Write(val_text)

        self.squares[index].remove(old_element)
        self.remove(old_element)
        self.vals_texts[index] = val_text

        # self.squares[index].generate_target(use_deepcopy=True)
        # self.squares[index].target.remove(old_element)
        # self.squares[index].target.add(val_text)
        def _on_finish(scene: Scene):
            self.add(val_text)
            self.squares[index] += val_text

        return AnimationGroup(ReplacementTransform(old_element, val_text), _on_finish=_on_finish)

    def swap(self, i: int, j: int, path_args: dict = None, **kwargs) -> AnimationGroup:
        """Swaps the elements at indices i and j."""
        # TODO: update array indexes
        path_args = path_args or {}
        i -= self.starting_index
        j -= self.starting_index
        i, j = (j, i) if i > j else (i, j)
        right_path = ArcBetweenPoints(self.squares[i].get_center(), self.squares[j].get_center(), angle=TAU / 3)
        left_path = ArcBetweenPoints(self.squares[j].get_center(), self.squares[i].get_center(), angle=TAU / 3)
        return AnimationGroup(MoveAlongPath(self.squares[i], right_path, **path_args),
                              MoveAlongPath(self.squares[j], left_path, **path_args), **kwargs)


class Pointer(VGroup):
    def __init__(self, direction: Iterable):
        super().__init__()
        self.arrow = Vector(direction)
        self.add(self.arrow)

    def draw(self):
        return Create(self.arrow)


class TextPointer(Pointer):
    def __init__(self, text, text_size: float = 1, direction: Iterable = UP):
        super().__init__(direction)
        self.text = Text(text).scale(text_size)

        # Position the text
        if np.array_equal(direction, UP):
            self.text.next_to(self.arrow, DOWN)
        else:
            self.text.next_to(self.arrow, UP)

        self.add(self.text)

    def draw(self, **kwargs) -> AnimationGroup:
        lag_ratio = kwargs.pop("lag_ratio", 0.5)
        return AnimationGroup(Create(self.arrow), Write(self.text), lag_ratio=lag_ratio, **kwargs)
