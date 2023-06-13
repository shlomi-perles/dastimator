from __future__ import annotations

import networkx as nx
from tools.funcs import *
from tools.graphs.my_graphs import DiGraph, WeightedGraph, _determine_graph_layout
from manim.mobject.geometry.boolean_ops import _BooleanOps

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


from scipy.spatial import Voronoi, ConvexHull


def get_vertices_cut(graph: DiGraph | WeightedGraph, vertices: list[Hashable], buff=None, scale=0.9,
                     round_radius=None, **kwargs) -> Polygon:
    buff = buff if buff is not None else next(iter(graph.vertices.values())).get_width() * 0.8
    round_radius = round_radius if round_radius is not None else next(iter(graph.vertices.values())).get_width() * 0.8
    polygons = get_vertices_voronoi_polygons(graph, buff=buff, round_radius=0, **kwargs)
    vertex_to_polygon = {vertex: polygon for vertex, polygon in zip(graph.vertices, polygons)}
    cut = [vertex_to_polygon[vertex] for vertex in vertices]
    return boolean_op_to_polygons(Union(*cut), convex_hull=False, **kwargs).scale(
        scale).surround(VGroup(*[graph.vertices[vertex] for vertex in vertices]), buff=buff)


def get_vertices_voronoi_polygons(graph: DiGraph | WeightedGraph, round_radius: float = None, buff=None, **kwargs) -> \
        VGroup[Polygon]:
    graph_hull = get_graph_convex_hull(graph, buff=buff, round_radius=0, **kwargs)
    surround_hull = get_graph_convex_hull(graph).scale(10)
    vor = Voronoi(np.concatenate((np.array([vertex.get_center()[:2] for vertex in graph.vertices.values()]),
                                  surround_hull.get_vertices()[:, :2])))
    polygons = []
    round_radius = round_radius if round_radius is not None else next(iter(graph.vertices.values())).get_width() * 0.8
    for r in range(len(vor.point_region)):
        region = vor.regions[vor.point_region[r]]
        if not -1 in region:
            polygon = Polygon(*[np.append(vor.vertices[i], 0) for i in region], **kwargs)
            intersec_shape = Intersection(polygon, graph_hull)
            polygons.append(boolean_op_to_polygons(intersec_shape, **kwargs).round_corners(radius=round_radius))
    return VGroup(*polygons)


def boolean_op_to_polygons(boolean_op: _BooleanOps, convex_hull=True, **kwargs) -> Polygon:
    points = boolean_op.points
    points = [points[i] for i in ConvexHull(points[:, :2]).vertices] if convex_hull else points
    return Polygon(*points, **kwargs)


def get_graph_convex_hull(graph: DiGraph | WeightedGraph, buff=None, round_radius=None, **kwargs) -> Polygon:
    points = np.array([vertex.get_center()[:2] for vertex in graph.vertices.values()])
    buff = buff if buff is not None else next(iter(graph.vertices.values())).get_width() * 0.8
    round_radius = round_radius if round_radius is not None else buff
    return get_convex_hull_polygon(points, round_radius=round_radius, **kwargs).surround(graph, buff=buff)


def get_convex_hull_polygon(points: np.ndarray, round_radius=0.2, **kwargs) -> Polygon:
    hull = ConvexHull(points[:, :2])
    return Polygon(*[np.append(points[i], 0) for i in hull.vertices], **kwargs).round_corners(radius=round_radius)
