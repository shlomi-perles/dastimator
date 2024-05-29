from __future__ import annotations

from typing import Hashable

from tools.consts import *
from tools.funcs import *
from tools.graphs.my_graphs import DiGraph, WeightedGraph, _determine_graph_layout

from tools.graphs.utils import create_dist_label, get_neighbors

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

# circular graph with 1 as the root

PATH_TIME_WIDTH = 0.6
SP_PATH_PARAMS = dict(width_factor=EDGE_TREE_PATH_WIDTH_FACTOR, time_width=PATH_TIME_WIDTH * 2,
                      preserve_state=True, run_time=1.7)
SP_RELAX_PATH_PARAMS = dict(width_factor=EDGE_TREE_PATH_WIDTH_FACTOR * 0.8, time_width=PATH_TIME_WIDTH * 2,
                            flash_color=EDGE_COLOR, preserve_state=True, run_time=1.7)


def change_layout(n, layout_scale: float = 2.4, layout_config: dict | None = None, rotate_angle: float = 0,
                  flip_x=True) -> dict[Hashable, np.ndarray]:
    networkx_graph = nx.path_graph([i for i in range(1, n + 1)])
    # remove center vertex
    layout = _determine_graph_layout(networkx_graph, layout="circular", layout_config=layout_config)
    if flip_x:
        center_x = np.average(list(layout.values()), axis=0)[0]
        layout = {k: np.array([2 * center_x - v[0], *v[1:]]) for k, v in layout.items()}
    return layout


def get_sp_dist_labels(graph: DiGraph | WeightedGraph):
    return VGroup(
        *([VMobject()] + [get_sp_dist_label(graph, i, "\infty") for i, node in graph.vertices.items()]))


def get_sp_dist_label(graph: DiGraph | WeightedGraph, v: Hashable, dist: int | float | str):
    return create_dist_label(v, graph, dist).scale(2).next_to(graph.vertices[v].get_bottom(), UP, buff=0.2).set_z_index(
        10)


def get_neighbors_background(graph: DiGraph | WeightedGraph, v: Hashable) -> dict[Hashable, VMobject]:
    edges_dict = {}
    for vertex in get_neighbors(graph, v):
        edge = get_background_edge(graph, v, vertex)
        edges_dict[vertex] = edge
    return edges_dict


def get_background_edge(graph: DiGraph | WeightedGraph, v: Hashable, u: Hashable) -> VMobject:
    cur_edge_line = graph.edges[(v, u)].edge_line
    edge = cur_edge_line.copy().set_z_index(-10)
    edge.pop_tips()
    edge.put_start_and_end_on(cur_edge_line.get_start(), cur_edge_line.get_end())
    edge.set_background_stroke(color=RED_D, width=cur_edge_line.get_stroke_width() * 6, opacity=0.4)
    # edge.set_stroke(color=RED, width=cur_edge_line.get_stroke_width() * 4, opacity=0.2)
    return edge
