from ..consts import *
from .node import Node


class Edge(VGroup):
    EDGE_Z_INDEX = 0
    NODE_Z_INDEX = 1
    LABEL_Z_INDEX = 2
    WEIGHT_Z_INDEX = 3
    """Simple class that represents a BST edge"""

    def __init__(self, start: Node, end: Node, weight: str | int | VMobject = None, **kwargs):
        """kwargs are passed to Line constructor"""
        super().__init__()
        self.edge_line = Line(start.get_center(), end.get_center(), **kwargs)
        self.start = start
        self.end = end

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
        return f"Edge({self.start.key}, {self.end.key}{(',' + self.weight) if self.weight is not None else ''})"

    def put_start_and_end_on(self, start, end):
        self.fix_z_index()
        self.edge_line.put_start_and_end_on(start, end)
        self.update_weight(self)

    def update_weight(self, edge):
        if self.weight_mob is not None:
            self.weight_mob.move_to(edge.edge_line.get_center())

    def draw_edge(self, relative_line_run_time=0.3, run_time=1.5, lag_ratio=0.7, **kwargs) -> AnimationGroup:
        self.fix_z_index()
        return AnimationGroup(FadeIn(self.edge_line, run_time=relative_line_run_time * run_time, **kwargs),
                              Write(self.weight_mob, run_time=run_time * (1 - relative_line_run_time), **kwargs),
                              lag_ratio=lag_ratio)

    def fix_z_index(self):
        if self.start is None or self.end is None:
            return
        self.start.set_z_index(self.NODE_Z_INDEX)
        self.start.label.set_z_index(self.LABEL_Z_INDEX)
        self.end.set_z_index(self.NODE_Z_INDEX)
        self.end.label.set_z_index(self.LABEL_Z_INDEX)
        self.edge_line.set_z_index(self.EDGE_Z_INDEX)
        if self.weight_mob is not None:
            self.weight_mob.set_z_index(self.WEIGHT_Z_INDEX)

    def animate_move_along_path(self, scene: Scene, flash_color=VISITED_COLOR, width_factor=1, **kwargs):
        self.fix_z_index()

        return AnimationGroup(
            ShowPassingFlash(
                self.edge_line.copy().set_z_index(self.edge_line.z_index).set_color(flash_color).set_stroke_width(
                    width_factor * self.stroke_width),
                **kwargs), group=self)
