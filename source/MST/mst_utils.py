from __future__ import annotations

from typing import Hashable

import networkx as nx

from tools.consts import *
from tools.funcs import *
from tools.graphs.my_graphs import DiGraph, WeightedGraph, _determine_graph_layout

from tools.graphs.utils import create_graph

# --------------------------------- constants --------------------------------- #
EDGE_COLOR = GREY
WEIGHT_COLOR = EDGE_COLOR
EDGE_CONFIG["stroke_color"] = EDGE_COLOR

MAIN_GRAPH_VERTEX_NUM = 7
MAIN_GRAPH_EXAMPLE_VERTICES = list(range(1, MAIN_GRAPH_VERTEX_NUM + 1))
# circular graph with 1 as the root
MAIN_GRAPH_EXAMPLE_EDGES = [(i, i + 1) if i < MAIN_GRAPH_VERTEX_NUM else (MAIN_GRAPH_VERTEX_NUM, 2) for i in
                            range(2, 1 + MAIN_GRAPH_VERTEX_NUM)] + [
                               (1, i) for i in range(3, MAIN_GRAPH_VERTEX_NUM + 1)] + [(3, 7)]
MAIN_GRAPH_EXAMPLE_WEIGHTS = {(2, 3): 5, (3, 4): 16, (4, 5): 26, (5, 6): 4, (6, 7): 18, (1, 3): 3,
                              (1, 4): 30, (1, 5): 14, (1, 6): 12, (1, 7): 2, (2, 7): 8, (3, 7): 10}

DEFAULT_CUT_PARAMS = dict(fill_color=GREEN_D, stroke_color=GREEN, fill_opacity=0.14, stroke_width=3)


def star_layout(n, center_vertex: Hashable, layout_scale: float = 2.4,
                layout_config: dict | None = None, rotate_angle: float = 0) -> dict[Hashable, np.ndarray]:
    networkx_graph = nx.star_graph(n)
    # remove center vertex
    networkx_graph.remove_node(center_vertex)
    layout = _determine_graph_layout(networkx_graph, layout="circular", layout_scale=layout_scale,
                                     layout_config=layout_config)
    layout[center_vertex] = np.average(list(layout.values()), axis=0)
    # rotate layout around center vertex
    layout = {k: rotate_vector(v, rotate_angle) for k, v in layout.items()}
    return layout


def get_main_graph_example() -> DiGraph | WeightedGraph:
    return create_graph(MAIN_GRAPH_EXAMPLE_VERTICES, MAIN_GRAPH_EXAMPLE_EDGES, graph_type=WeightedGraph,
                        weights=MAIN_GRAPH_EXAMPLE_WEIGHTS, absolute_scale_vertices=True,
                        layout=star_layout(MAIN_GRAPH_EXAMPLE_VERTICES[::-1], 1, rotate_angle=PI * 5 / 6))
