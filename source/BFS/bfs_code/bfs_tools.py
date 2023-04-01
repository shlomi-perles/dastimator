from manim import *
from typing import Callable, Iterable, List, Optional, Sequence, Union

__all__ = ["ArrayMob", "Pointer", "TextPointer"]


# class QueueMob(VGroup):
#     def __init__(self, queue: list[Union[float, str, "VMobject"]], anchor: Iterable = ORIGIN,
#                  anchor_side: Iterable = RIGHT, anchor_buff: float = 0, height: int = 5, **kwargs):
#         super().__init__(**kwargs)
#         self.height = height
#         self.anchor = ORIGIN
#         self.anchor_side = anchor_side
#         self.anchor_buff = anchor_buff
#         for i in queue:
#             square = Square(fill_opacity=0, side_length=self.height)
#             square.add(Text(str(i)).scale_to_fit_height(square.height * 0.8).move_to(square.get_center()))
#             self.add(square)
#         self.arrange(direction=RIGHT, buff=0)
#         self.next_to(anchor, anchor_side, buff=anchor_buff)
#
#     def animate_pop(self, index: int = 0, return_to_anchor: bool = True, **kwargs):
#         animations = []
#         pop_item = self[index]
#         self.remove(pop_item)
#         self.arrange(direction=RIGHT, buff=0)
#         animations.append(FadeOut(pop_item))
#         if return_to_anchor:
#             animations.append(self.animate.next_to(self.anchor, self.anchor_side, buff=self.anchor_buff))
#         return AnimationGroup(*animations, **kwargs)
#
#     def animate_push(self, value: Union[float, str, "VMobject"], return_to_anchor: bool = True, **kwargs):
#         animations = []
#         push_item = Square(fill_opacity=0, side_length=self.height)
#         push_item.add(Text(str(value)).scale_to_fit_height(push_item.height * 0.8).move_to(push_item.get_center()))
#         self.add(push_item)
#         self.arrange(direction=RIGHT, buff=0)
#         if return_to_anchor:
#             animations.append(self.animate.next_to(self.anchor, self.anchor_side, buff=self.anchor_buff))
#         animations.append(FadeIn(push_item))
#         return AnimationGroup(*animations, **kwargs)

class QueueMob(VGroup):
    def __init__(self, table: list[Union[float, str, "VMobject"]], table_params: Optional[dict] = None, **kwargs):
        super().__init__(**kwargs)
        table_params = {} if table_params is None else table_params

        self.anchor = ORIGIN
        self.queue_vals = [str(i) for i in table]
        self.table = Table([self.queue_vals], include_outer_lines=True, **table_params)
        self.add(self.table)
        self.table_params = table_params

    def set_anchor(self, anchor: Union[Sequence[float], "VMobject"] = None, **kwargs):
        if anchor is None or isinstance(anchor, VMobject):
            self.anchor = self.get_center()
        else:
            self.anchor = np.array(anchor)

    def animate_pop(self, index: int = 0, return_to_anchor: bool = True, **kwargs):
        animations = []
        self.set_anchor()

        self.queue_vals.pop(index)
        if len(self.queue_vals) == 0:
            self.queue_vals.append(" ")
        return self.update_table(return_to_anchor, **kwargs)

    def animate_push(self, value: Union[float, str, "VMobject"], return_to_anchor: bool = True, **kwargs):
        self.set_anchor()
        if self.queue_vals[0] == " ":
            self.queue_vals.pop(0)
        self.queue_vals.append(str(value))
        return self.update_table(return_to_anchor, **kwargs)

    def update_table(self, return_to_anchor: bool = True, **kwargs):
        animations = []
        self.generate_target(use_deepcopy=True)
        self.target.table = Table([self.queue_vals], include_outer_lines=True, **self.table_params).shift(RIGHT)
        animations.append(self.animate.become(self.target))
        # if return_to_anchor:
        #     animations.append(self.animate.move_to(self.anchor))
        return AnimationGroup(*animations, **kwargs)


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

    def __init__(self, name: str, *values, name_config=None, arr_factor_size: float = 1.8, name_size: float = 1,
                 **kwargs):
        name_config = {} if name_config is None else name_config
        self.array_name = Tex(name, **name_config)
        super().__init__(name=name, **kwargs.pop("vgroup_config", {}))

        self.add(self.array_name)
        self.array = values
        self.squares = VGroup()
        self.vals_texts = VGroup()
        self.arr_factor_size = arr_factor_size
        self.name_size = name_size
        self.create_array_args = kwargs
        self.create_array()

    def create_array(self):
        """Creates the objects for each element in the array."""
        self.array_name.scale(self.name_size)
        for val in self.array:
            val_text = Tex("" if val is None else str(val), **self.create_array_args.pop("value_config", {}))

            square = Square(**self.create_array_args.pop("square_config", {})).scale_to_fit_height(
                self.array_name.height * self.arr_factor_size)
            val_text.scale_to_fit_height(square.height * ArrayMob.VALS_HEIGHT_FACTOR)

            square.add(val_text)
            self.squares.add(square)
            self.vals_texts.add(val_text)

        self.squares.arrange(buff=0)

        self.add(*self.squares)
        self.add(*self.vals_texts)

        self.array_name.next_to(self.squares.get_left(), direction=LEFT, aligned_edge=RIGHT)

        # if self.show_labels:
        #     self.labels = VGroup()
        #     for i in range(len(self.values)):
        #         label = TextMobject(str(i)).scale(self.labels_scale)
        #         label.move_to((i * RIGHT * self.element_width) +
        #                       (UP * self.element_height * 0.8))

    def draw_array(self, **kwargs):
        """Draws the array. Returns a list of the array's animations."""
        if "lag_ratio" not in kwargs:
            kwargs["lag_ratio"] = 0.3

        all_anims = [Write(self.array_name)]
        all_anims += [Write(square) for square in self.squares]
        return AnimationGroup(*all_anims, **kwargs)

    def pop(self, index: int = 0, **kwargs) -> AnimationGroup:
        """
        Pops an element from the array.
        :param index: The index of the element to be popped.
        :param kwargs: Additional arguments to the AnimationGroup.
        :return: The AnimationGroup of the pop animation.
        """
        if "lag_ratio" not in kwargs:
            kwargs["lag_ratio"] = 1

        animations = []

        # Fade out the element with the given index
        animations.append(
            AnimationGroup(FadeOut(self.squares[index], shift=DOWN), FadeOut(self.vals_texts[index], shift=DOWN)))

        # Noticed a bit of a logical flaw here
        self.remove(self.squares[index])
        self.remove(self.vals_texts[index])

        if len(self.squares) - 1 == 0:
            self.squares = VGroup()
            self.vals_texts = VGroup()
            return AnimationGroup(*animations, **kwargs)

        self.squares.remove(self.squares[index])
        self.vals_texts.remove(self.vals_texts[index])

        for i in range(index, len(self.squares) - 1):
            self.squares[i] = self.squares[i + 1]
            self.vals_texts[i] = self.vals_texts[i + 1]

        shift_arr_to = self.array_name if index == 0 else self.squares[index - 1]
        buff = DEFAULT_MOBJECT_TO_MOBJECT_BUFFER if index == 0 else 0
        animations.append(self.squares[index:].animate.next_to(shift_arr_to, direction=RIGHT, buff=buff))

        return AnimationGroup(*animations, **kwargs)

    def push(self, value: int, **kwargs) -> Animation:
        """
        Pushes an element to the array.
        :param value: The value of the element to be pushed.
        :param kwargs: Additional arguments to the AnimationGroup.
        :return: The AnimationGroup of the push animation.
        """

        square = Square(**self.create_array_args.pop("square_config", {})).scale_to_fit_height(
            self.array_name.height * self.arr_factor_size)
        val_text = Tex(str(value), **self.create_array_args.pop("value_config", {}))
        val_text.scale_to_fit_height(square.height * ArrayMob.VALS_HEIGHT_FACTOR)

        if len(self.squares) == 0:
            square.next_to(self.array_name, direction=RIGHT)
        else:
            square.move_to(self.squares[-1].get_right(), aligned_edge=LEFT)

        val_text.move_to(square)

        square.add(val_text)
        self.squares.add(square)
        self.vals_texts.add(val_text)
        self.add(square)
        self.add(val_text)
        return FadeIn(square, shift=LEFT, **kwargs)

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

    def at(self, index: int, value: Union[float, str, "VMobject"]):
        """Changes the value of an element at a given index."""
        val_text = Tex("" if value is None else f"{value}", **self.create_array_args.pop("value_config", {}))

        old_element = self.vals_texts[index]

        val_text.set_height(self.squares[index].height * ArrayMob.VALS_HEIGHT_FACTOR)
        val_text.move_to(old_element)

        old_element.target = val_text

        return [MoveToTarget(old_element)]


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
