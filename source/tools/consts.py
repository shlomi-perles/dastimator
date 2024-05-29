from manim import *

BACKGROUND_COLOR: str = "#242424"  # Also, 1C1D21 or 242424 or 2C2F33

# ----------------------------------    Paths     ---------------------------------- #
DASTIMATOR_PATH: Path = Path(__file__).resolve().parent.parent.parent
MEDIA_PATH: Path = DASTIMATOR_PATH / "media"
SITE_PATH = DASTIMATOR_PATH / "docs"
MOVIES_PATH = SITE_PATH / "movies"

# ---------------------------------- Graph consts ---------------------------------- #
VERTEX_COLOR: str = DARK_BLUE
VERTEX_WIDTH: float = config.frame_width * 0.038
VERTEX_STROKE_WIDTH: float = DEFAULT_STROKE_WIDTH * 1.6
VERTEX_STROKE_COLOR: str = BLUE_D
VERTEX_LABEL_SCALE: float = 0.9
VERTEX_CONFIG: dict = {"fill_color": VERTEX_COLOR, "stroke_color": VERTEX_STROKE_COLOR,
                       "stroke_width": VERTEX_STROKE_WIDTH}

EDGE_COLOR: str = WHITE
EDGE_STROKE_WIDTH: float = DEFAULT_STROKE_WIDTH * 2
EDGE_PATH_WIDTH_FACTOR: float = 1
EDGE_TREE_PATH_WIDTH_FACTOR: float = 2.7
TIP_SIZE: float = DEFAULT_ARROW_TIP_LENGTH * 0.4
DEFAULT_ARROW_TIP_WIDTH: float = TIP_SIZE
TIP_CONFIG: dict = {"tip_config": {"tip_length": 0, "tip_width": 0}}
EDGE_CONFIG: dict = {"stroke_width": EDGE_STROKE_WIDTH, "stroke_color": EDGE_COLOR, **TIP_CONFIG}

WEIGHT_COLOR: str = YELLOW_D
WEIGHT_STROKE_COLOR: str = YELLOW_D
WEIGHT_STROKE_WIDTH: float = DEFAULT_STROKE_WIDTH * 1.6
WEIGHT_LABEL_FONT_COLOR: str = BLACK
WEIGHT_SCALE: float = 0.4
WEIGHT_LABEL_SCALE: float = 1
WEIGHT_CONFIG: dict = {"fill_color": WEIGHT_COLOR, "stroke_color": WEIGHT_STROKE_COLOR,
                       "stroke_width": WEIGHT_STROKE_WIDTH}

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
# ----------------------------------    Text     ---------------------------------- #
DEFINITION_TEX_ENV: str = "{minipage}{8cm}"
REMOVE_MATH_SPACE_PREAMBLE: str = r'''\setlength{\abovedisplayskip}{0pt}
\setlength{\belowdisplayskip}{0pt}
\setlength{\abovedisplayshortskip}{0pt}
\setlength{\belowdisplayshortskip}{0pt}
'''
# ----------------------------------    Manim    ---------------------------------- #
PROBABILITY_SPACE_BACK_COLOR: str = "#404040"
QUALITY_TO_DIR = {"l": "480p15", "h": "1080p60", "k": "2160p60"}
