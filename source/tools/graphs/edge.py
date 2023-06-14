from __future__ import annotations

from ..consts import *
from .node import Node


class Edge(VGroup):
    EDGE_Z_INDEX = 0
    NODE_Z_INDEX = 1
    LABEL_Z_INDEX = 2
    WEIGHT_Z_INDEX = 3
    """Simple class that represents a BST edge"""

    def __init__(self, start: Node | np.ndarray, end: Node | np.ndarray, weight: str | int | VMobject = None,
                 edge_type: type[VMobject] = Line, **kwargs):
        """kwargs are passed to Line constructor"""
        super().__init__()
        self.edge_type = edge_type
        start_loc = start.get_center() if isinstance(start, Node) else np.copy(start)
        end_loc = end.get_center() if isinstance(end, Node) else np.copy(end)
        self.edge_line = edge_type(start_loc, end_loc, **kwargs)
        self.start = start
        self.end = end
        self.weight_mob = None

        self.add(self.edge_line)
        if weight is not None:
            self.weight = weight if not isinstance(weight, VMobject) else weight[1].tex_string
            self.weight_mob = weight if isinstance(weight, VMobject) else LabeledDot(
                label=MathTex(weight, fill_color=WEIGHT_LABEL_FONT_COLOR), **WEIGHT_CONFIG)

            self.update_weight(self)
            self.add(self.weight_mob)
            self.add_updater(self.update_weight)
        self.fix_z_index()

    def __str__(self):
        return f"Edge({self.start.key}, {self.end.key}{(' ,' + str(self.weight)) if self.weight is not None else ''})"

    def put_start_and_end_on(self, start, end):  # TODO: update start and end?
        self.fix_z_index()
        self.edge_line.put_start_and_end_on(start, end)
        self.update_weight(self)

    def update_weight(self, edge):
        self.fix_z_index()
        if self.weight_mob is not None:
            self.weight_mob.move_to(edge.edge_line.get_center())

    def set_weight(self, val: str | LabeledDot, **kwargs) -> Animation:
        self.fix_z_index()
        if self.weight_mob is not None:
            self.weight = val if not isinstance(val, VMobject) else val[1].tex_string
            new_weight = LabeledDot(
                label=MathTex(val), **WEIGHT_CONFIG).scale_to_fit_width(self.weight_mob.width) if isinstance(val,
                                                                                                             str) else val
            new_weight.move_to(self.weight_mob)
            return Transform(self.weight_mob, new_weight, **kwargs, group=self)

    def draw_edge(self, relative_line_run_time=0.3, run_time=1.5, lag_ratio=0.7, **kwargs) -> AnimationGroup:
        self.fix_z_index()
        return AnimationGroup(FadeIn(self.edge_line, run_time=relative_line_run_time * run_time, **kwargs),
                              Write(self.weight_mob, run_time=run_time * (1 - relative_line_run_time), **kwargs),
                              lag_ratio=lag_ratio)

    def fix_z_index(self):
        if self.start is None or self.end is None:
            return
        if isinstance(self.start, Node):
            self.start.set_z_index(self.NODE_Z_INDEX)
            self.start.label.set_z_index(self.LABEL_Z_INDEX)
        if isinstance(self.end, Node):
            self.end.set_z_index(self.NODE_Z_INDEX)
            self.end.label.set_z_index(self.LABEL_Z_INDEX)
        self.edge_line.set_z_index(self.EDGE_Z_INDEX)
        if self.weight_mob is not None:
            self.weight_mob.set_z_index(self.WEIGHT_Z_INDEX)

    def animate_move_along_path(self, flash_color=VISITED_COLOR, width_factor=EDGE_PATH_WIDTH_FACTOR,
                                time_width: float = 0.1, opposite_direction=False, preserve_state=False,
                                **kwargs) -> AnimationGroup:
        self.fix_z_index()
        copy_line = self.edge_line.copy()
        if opposite_direction:
            copy_line.rotate(PI)
        animations = [
            ShowPassingFlash(copy_line.set_z_index(self.edge_line.z_index).set_color(flash_color).set_stroke_width(
                width_factor * self.stroke_width), time_width=time_width)]
        if preserve_state:
            animations.append(self.edge_line.animate.set_color(flash_color).set_stroke_width(
                width_factor * self.stroke_width))

        return AnimationGroup(*animations, **kwargs, group=self)

    def pop_tips(self):
        return self.edge_line.pop_tips()

    def add_tip(self, *args, **kwargs):
        self.edge_line.add_tip(*args, **kwargs)
        return self

    def get_color(self):
        return self.edge_line.get_color()

    def set_color(self, *args, **kwargs):
        self.edge_line.set_color(*args, **kwargs)
        return self
