from ..consts import *
from typing import Optional

NODES_RELATIVE_HEIGHT = config.frame_height * 0.09


class Node(LabeledDot):
    """Simple class that represents a BST node"""

    def __init__(self, key=None, label=None, relative_height=None, **kwargs):
        if label is not isinstance(label, SVGMobject) and label is not None:
            label = MathTex(label, fill_color=LABEL_COLOR)
        label_scale = kwargs.pop("label_scale", VERTEX_LABEL_SCALE)
        kwargs = {**VERTEX_CONFIG, **kwargs}
        super().__init__(label=MathTex(key, fill_color=LABEL_COLOR) if label is None else label, **kwargs)
        self.scale_to_fit_height(NODES_RELATIVE_HEIGHT if relative_height is None else relative_height)
        self[1].scale(label_scale)
        self.label = self[1]
        self.label.set_z_index(self.z_index + 1)
        self.key = label if key is None else key
        self.left = None
        self.right = None
        self.parent = None

    def set_color(self, fill_color=None, stroke_color=None, label_color=None):
        fill_color = fill_color if fill_color is not None else self.fill_color
        stroke_color = stroke_color if stroke_color is not None else self.stroke_color
        label_color = label_color if label_color is not None else self.label.get_fill_color()
        self.set_fill(fill_color)
        self.set_stroke(stroke_color)
        self.label.set_color(label_color)
        return self

    def __str__(self):
        return str(self.key)

    def __lt__(self, other):
        if isinstance(other, Node):
            return self.key < other.key
        if isinstance(other, (float, int)):
            return self.key < other
        return False

    def __gt__(self, other):
        if isinstance(other, Node):
            return self.key > other.key
        if isinstance(other, (float, int)):
            return self.key > other
        return False

    def __le__(self, other):
        if isinstance(other, Node):
            return self.key <= other.key
        if isinstance(other, (float, int)):
            return self.key <= other
        return False

    def __ge__(self, other):
        if isinstance(other, Node):
            return self.key >= other.key
        if isinstance(other, (float, int)):
            return self.key >= other
        return False


class IndicateNode(Transform):
    def __init__(
            self, mobject: "Mobject", scale_factor: float = 1.2, fill_color: str = YELLOW_E, stroke_color: str = YELLOW,
            preserve_indicate_color=False, rate_func: Callable[[float, Optional[float]], np.ndarray] = linear,
            **kwargs) -> None:
        self.fill_color = fill_color
        self.stroke_color = stroke_color
        self.preserve_indicate_color = preserve_indicate_color
        self.scale_factor = scale_factor
        super().__init__(mobject, rate_func=rate_func, **kwargs)

    def create_target(self) -> "Mobject":
        self.mobject.label.set_z_index(self.mobject.z_index + 1)
        target = self.mobject.copy()
        target.scale(self.scale_factor)
        target.set_fill(self.fill_color)
        target.set_stroke(self.stroke_color)
        target.label.set_color(WHITE)
        target.label.set_z_index(target.z_index + 1)
        return target

    def interpolate_submobject(self, sub, st_mob, tg, alpha):
        sub.interpolate(st_mob, tg, there_and_back(alpha), self.path_func)
        if alpha >= 0.5 and self.preserve_indicate_color and isinstance(st_mob, Node):
            st_mob.set_color(fill_color=self.fill_color, stroke_color=self.stroke_color)
        return self
