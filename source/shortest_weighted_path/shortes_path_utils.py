from __future__ import annotations

from typing import Hashable

import networkx as nx

from tools.consts import *
from tools.funcs import *
from tools.graphs.my_graphs import DiGraph, WeightedGraph, _determine_graph_layout

from tools.graphs.utils import create_graph, create_dist_label

# --------------------------------- constants --------------------------------- #
TIP_CONFIG["tip_config"]["tip_length"] = TIP_SIZE * 1.6
TIP_CONFIG["tip_config"]["tip_width"] = DEFAULT_ARROW_TIP_WIDTH * 1.6

EDGE_COLOR = GREY
WEIGHT_COLOR = EDGE_COLOR
EDGE_CONFIG["stroke_width"] = EDGE_STROKE_WIDTH
EDGE_CONFIG["stroke_color"] = EDGE_COLOR
EDGE_CONFIG["edge_type"] = ArcBetweenPoints
EDGE_CONFIG["angle"] = TAU / 7
EDGE_CONFIG["tip_config"] = TIP_CONFIG["tip_config"]
EDGE_CONFIG["tip_config"]["tip_width"] = TIP_CONFIG["tip_config"]["tip_width"]
EDGE_CONFIG["tip_config"]["tip_length"] = TIP_CONFIG["tip_config"]["tip_length"]

MAIN_GRAPH_VERTEX_NUM = 5
MAIN_GRAPH_EXAMPLE_VERTICES = list(range(1, MAIN_GRAPH_VERTEX_NUM + 1))
# circular graph with 1 as the root
MAIN_GRAPH_EXAMPLE_EDGES = [(1, 2), (2, 3), (3, 4), (4, 3), (5, 4), (1, 5), (4, 1), (2, 5), (5, 2), (5, 3)]
MAIN_GRAPH_EXAMPLE_WEIGHTS = {(1, 2): 10, (2, 3): 1, (3, 4): 4, (4, 3): 6, (5, 4): 2, (1, 5): 5, (4, 1): 7, (2, 5): 2,
                              (5, 2): 3, (5, 3): 9}

PATH_TIME_WIDTH = 0.6
SP_PATH_PARAMS = dict(width_factor=EDGE_TREE_PATH_WIDTH_FACTOR, time_width=PATH_TIME_WIDTH * 2,
                      preserve_state=True, run_time=1.7)


def change_layout(n, layout_scale: float = 2.4, layout_config: dict | None = None, rotate_angle: float = 0,
                  flip_x=True) -> dict[Hashable, np.ndarray]:
    networkx_graph = nx.path_graph([i for i in range(1, n + 1)])
    # remove center vertex
    layout = _determine_graph_layout(networkx_graph, layout="circular", layout_config=layout_config)
    if flip_x:
        center_x = np.average(list(layout.values()), axis=0)[0]
        layout = {k: np.array([2 * center_x - v[0], *v[1:]]) for k, v in layout.items()}
    # rotate layout around center vertex
    # layout = {k: rotate_vector(v, rotate_angle) for k, v in layout.items()}
    return layout


def get_main_graph_example() -> DiGraph | WeightedGraph:
    graph = create_graph(MAIN_GRAPH_EXAMPLE_VERTICES, MAIN_GRAPH_EXAMPLE_EDGES, graph_type=WeightedGraph,
                         weights=MAIN_GRAPH_EXAMPLE_WEIGHTS, directed_graph=True,
                         layout=change_layout(MAIN_GRAPH_VERTEX_NUM)).shift(1e-6 * LEFT)
    for v, node in graph.vertices.items():
        node.label.scale(0.8).next_to(node.get_top(), DOWN, buff=0.1)
    graph[2].match_y(graph[3])
    graph[5].match_y(graph[4])
    return graph


def get_dist_labels(graph: DiGraph | WeightedGraph):
    return VGroup(
        *([VMobject()] + [
            create_dist_label(i, graph, r"\infty").scale(2).next_to(node.get_bottom(), UP, buff=0.2).set_z_index(10)
            for i, node in graph.vertices.items()]))
