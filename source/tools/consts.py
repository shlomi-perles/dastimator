from pathlib import Path
from manim import *

BACKGROUND_COLOR: str = "#242424"  # Also 1C1D21 or 242424 or 2C2F33

# ----------------------------------    Paths     ---------------------------------- #
MEDIA_PATH = Path(__file__).resolve().parent.parent.parent.parent / "media"

# ---------------------------------- Graph consts ---------------------------------- #
VERTEX_COLOR = DARK_BLUE
VERTEX_STROKE_WIDTH = DEFAULT_STROKE_WIDTH * 1.6
VERTEX_STROKE_COLOR = BLUE_D
VERTEX_LABEL_SCALE = 0.7
VERTEX_CONFIG = {"fill_color": VERTEX_COLOR, "stroke_color": VERTEX_STROKE_COLOR, "stroke_width": VERTEX_STROKE_WIDTH}

EDGE_COLOR = GREY
EDGE_STROKE_WIDTH = DEFAULT_STROKE_WIDTH * 2
TIP_SIZE = DEFAULT_ARROW_TIP_LENGTH * 0.4
DEFAULT_ARROW_TIP_WIDTH = TIP_SIZE
TIP_CONFIG = {"tip_config": {"tip_length": 0, "tip_width": 0}}
EDGE_CONFIG = {"stroke_width": EDGE_STROKE_WIDTH, "stroke_color": EDGE_COLOR, **TIP_CONFIG}

VISITED_COLOR = PURE_GREEN
VISITED_EDGE_WIDTH = EDGE_STROKE_WIDTH * 1.5
VISITED_VERTEX_WIDTH = VERTEX_STROKE_WIDTH * 1.8
VISITED_VERTEX_CONFIG = {"fill_color": VERTEX_COLOR, "stroke_color": VISITED_COLOR,
                         "stroke_width": VISITED_VERTEX_WIDTH}
VISITED_TIP_SIZE = TIP_SIZE * 2.1
LABEL_COLOR = WHITE

DISTANCE_LABEL_BUFFER = 0.02
DISTANCE_LABEL_SCALE = 0.8
DISTANCE_LABEL_COLOR = ORANGE

# ---------------------------------- Code consts ---------------------------------- #
LINES_OFF_OPACITY = 0.5
