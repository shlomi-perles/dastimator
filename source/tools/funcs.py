from typing import Tuple

from manim import *
from manim import AnimationGroup


def highlight_code_lines(code: Code, lines: list = None, off_opacity: float = 0.5, indicate=True,
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
