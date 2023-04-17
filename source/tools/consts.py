from manim import *

BACKGROUND_COLOR: str = "#242424"  # Also, 1C1D21 or 242424 or 2C2F33

# ----------------------------------    Paths     ---------------------------------- #
MEDIA_PATH: Path = Path(__file__).resolve().parent.parent.parent / "media"

# ---------------------------------- Graph consts ---------------------------------- #
VERTEX_COLOR: str = DARK_BLUE
VERTEX_STROKE_WIDTH: float = DEFAULT_STROKE_WIDTH * 1.6
VERTEX_STROKE_COLOR: str = BLUE_D
VERTEX_LABEL_SCALE: float = 0.7
VERTEX_CONFIG: dict = {"fill_color": VERTEX_COLOR, "stroke_color": VERTEX_STROKE_COLOR,
                       "stroke_width": VERTEX_STROKE_WIDTH}

EDGE_COLOR: str = WHITE
EDGE_STROKE_WIDTH: float = DEFAULT_STROKE_WIDTH * 2
TIP_SIZE: float = DEFAULT_ARROW_TIP_LENGTH * 0.4
DEFAULT_ARROW_TIP_WIDTH: float = TIP_SIZE
TIP_CONFIG: dict = {"tip_config": {"tip_length": 0, "tip_width": 0}}
EDGE_CONFIG: dict = {"stroke_width": EDGE_STROKE_WIDTH, "stroke_color": EDGE_COLOR, **TIP_CONFIG}

VISITED_COLOR: str = PURE_GREEN
VISITED_EDGE_WIDTH: float = EDGE_STROKE_WIDTH * 1.5
VISITED_VERTEX_WIDTH: float = VERTEX_STROKE_WIDTH * 1.8
VISITED_VERTEX_CONFIG: dict = {"fill_color": VERTEX_COLOR, "stroke_color": VISITED_COLOR,
                               "stroke_width": VISITED_VERTEX_WIDTH}
VISITED_TIP_SIZE: float = TIP_SIZE * 2.1
LABEL_COLOR: str = WHITE

DISTANCE_LABEL_BUFFER: float = 0.02
DISTANCE_LABEL_SCALE: float = 0.8
DISTANCE_LABEL_COLOR: str = ORANGE

# ---------------------------------- Code consts ---------------------------------- #
LINES_OFF_OPACITY: float = 0.5

# ----------------------------------    Manim    ---------------------------------- #
QUALITY_TO_DIR = {"l": "480p15", "h": "1080p60", "k": "2160p60"}
