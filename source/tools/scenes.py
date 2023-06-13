from manim import *
from manim_editor import PresentationSectionType as pst
from tools.consts import BACKGROUND_COLOR

config.background_color = BACKGROUND_COLOR


class SectionsScene(Scene):
    PRESENTATION_MODE = False

    def next_section(self, name: str = "unnamed", type: str = pst.SUB_NORMAL, skip_animations: bool = False,
                     skip_section: bool = False):
        if skip_section:
            return
        if self.PRESENTATION_MODE:
            self.wait(0.3)
            super().next_section(name, type, skip_animations)
        else:
            self.wait()
