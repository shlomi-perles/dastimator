from manim import *
from typing import Callable, Iterable, List, Optional, Sequence, Union

__all__ = ["ArrayMob", "Pointer", "TextPointer"]


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
        self.play(array.draw_array())

        # create a pointer with a text label
        pointer = TextPointer("Here", 0.8, UP)
        pointer.next_to(array.get_square(2), DOWN)
        self.play(*pointer.draw(), run_time=0.5)

        # connect the pointer, so when you transform the array
        # it will transform the pointer as well
        array += pointer

        # shift the pointer
        self.play(pointer.animate.align_to(array.get_square(4), RIGHT), run_time=0.5)

        self.play(array.indicate_at(4), run_time=0.5)
        # example for scaling the whole array
        self.play(array.animate.scale(1.1), run_time=0.5)

        # popping an element
        self.play(array.pop(index=0))
        self.wait()

        # change the value at the 0th index to 3
        self.play(*array.at(0, 3), run_time=0.3)
        self.wait()
        self.play(array.push(6))

        self.wait(1)
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
        self.align_point = align_point
        self.starting_index = starting_index
        self.create_array_args = kwargs

        self.obj_ref = None
        self.height_ref = None

        self.create_array()

    def create_array(self):
        """Creates the objects for each element in the array."""
        self.array_name = Tex(self.name, font_size=DEFAULT_FONT_SIZE * self.name_scale, **self.name_config)
        self.obj_ref = Tex(":", font_size=DEFAULT_FONT_SIZE * self.name_scale, **self.name_config)
        self.height_ref = self.obj_ref.height
        self.add(self.array_name)

        for index, val in enumerate(self.array):
            square, val_text, label = self.create_arr_entry(val, index + self.starting_index)

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
        self.squares.next_to(self.array_name.get_right(), direction=RIGHT, aligned_edge=LEFT)

    def draw_array(self, **kwargs):
        """Draws the array. Returns a list of the array's animations."""
        if "lag_ratio" not in kwargs:
            kwargs["lag_ratio"] = 0.3

        all_anims = [Write(self.array_name)]
        all_anims += [Write(square) for square in self.squares]
        return AnimationGroup(*all_anims, **kwargs)

    def pop(self, index: int = 0, shift=DOWN, **kwargs) -> AnimationGroup:
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

        # Noticed a bit of a logical flaw here
        self.remove(self.squares[index])
        self.remove(self.vals_texts[index])

        if len(self.squares) - 1 == 0:
            self.squares = VGroup()
            self.vals_texts = VGroup()
            return AnimationGroup(*animations, **kwargs)

        self.squares.remove(self.squares[index])
        self.vals_texts.remove(self.vals_texts[index])

        shift_arr_to = self.array_name if index == 0 else self.squares[index - 1]
        buff = DEFAULT_MOBJECT_TO_MOBJECT_BUFFER if index == 0 else 0
        animations.append(self.squares[index:].animate.next_to(shift_arr_to, direction=RIGHT, buff=buff))

        return AnimationGroup(*animations, **kwargs)

    def push(self, value: int, side: np.ndarray = RIGHT, **kwargs) -> Animation:
        """
        Pushes an element to the array.
        :param value: The value of the element to be pushed.
        :param kwargs: Additional arguments to the AnimationGroup.
        :return: The AnimationGroup of the push animation.
        """
        square, val_text, label = self.create_arr_entry(value, index=len(self.squares))

        if len(self.squares) == 0:
            square.next_to(self.array_name, direction=RIGHT)
        elif (side == RIGHT).all():
            square.move_to(self.squares[-1].get_right(), aligned_edge=LEFT)
        else:  # equal LEFT
            square.move_to(self.squares[0])

        val_text.move_to(square)
        square.add(val_text)

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
        val_text = Tex("" if value is None else str(value), **self.create_array_args.pop("value_config", {}))
        if val_text.width < val_text.height:
            val_text.scale_to_fit_height(square.height * ArrayMob.VALS_HEIGHT_FACTOR)
        else:
            val_text.scale_to_fit_width(square.width * ArrayMob.VALS_HEIGHT_FACTOR)
        label = VGroup()
        if self.show_labels:
            label = Text(str(index)).match_height(square).scale(0.2 * self.labels_scale)
            label.next_to(square, self.labels_pos, buff=-(label.height + self.LABELS_BUFF)).align_to(
                square, RIGHT).shift(LEFT * self.LABELS_BUFF)
        return VGroup(square), val_text, label

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
        # self.squares[index].generate_target(use_deepcopy=True)
        # self.squares[index].target.remove(old_element)
        # self.squares[index].target.add(val_text)
        # self.add(val_text)

        return AnimationGroup(Write(val_text))  # TODO: handle not empty string. Maybe use MoveToTarget?


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

    def draw(self):
        """Returns list of [Create(arrow), Write(text)] animations"""
        return [Create(self.arrow), Write(self.text)]
