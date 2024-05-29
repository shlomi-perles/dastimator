from __future__ import annotations

from copy import deepcopy
from typing import Hashable

import numpy as np
from manim import MathTex, RIGHT, config, ORIGIN, VGroup, Line, Union, Intersection, ArcBetweenPoints

from manim.mobject.geometry.polygram import Polygon
from scipy.spatial import Voronoi

from tools.consts import DISTANCE_LABEL_COLOR, DISTANCE_LABEL_SCALE, DISTANCE_LABEL_BUFFER, EDGE_CONFIG, TIP_SIZE, \
    DEFAULT_ARROW_TIP_WIDTH, LABEL_COLOR, VERTEX_CONFIG, VERTEX_LABEL_SCALE, VERTEX_WIDTH
from tools.funcs import get_convex_hull_polygon, get_tangent_points, boolean_op_to_polygons
from tools.graphs.my_graphs import DiGraph, WeightedGraph, Graph, Edge
from tools.graphs.node import Node


def get_neighbors(graph: DiGraph, vertex, priority_lst=None):
    priority_lst = graph.vertices if priority_lst is None else priority_lst
    return [neighbor for neighbor in priority_lst if (vertex, neighbor) in graph.edges]


def create_dist_label(index: int, graph: DiGraph | WeightedGraph, label: str | int | float) -> MathTex:
    label = MathTex(rf"\mathbf{{{label}}}", color=DISTANCE_LABEL_COLOR).set_z_index(10)
    if label.width < label.height:
        label.scale_to_fit_height(graph[index].radius * DISTANCE_LABEL_SCALE)
    else:
        label.scale_to_fit_width(graph[index].radius * DISTANCE_LABEL_SCALE)
    return label.move_to(graph[index]).next_to(graph[index][1], RIGHT, buff=DISTANCE_LABEL_BUFFER)


def create_graph(vertices: list[Hashable], edges: list[tuple[Hashable, Hashable]],
                 layout: str | dict[Hashable, np.ndarray] = "spring", layout_scale: float = 1.5,
                 directed_graph: bool = False, graph_type=None, edge_type=Edge, vertex_type=Node,
                 rescale_vertices=True, labels: bool | dict[Hashable, str] = True,
                 weights: dict[tuple[Hashable, Hashable], float] = None,
                 dual_arrow: bool = False) -> Graph | WeightedGraph | DiGraph:
    """
    Create graph and add labels to vertices,
    Note: vertices are 1-indexed
    """
    edges = deepcopy(edges)
    if not directed_graph:
        edges += [(v, u) for u, v in edges]
    if graph_type is None:
        graph_type = DiGraph if directed_graph else WeightedGraph if weights is not None else Graph

    edge_config = deepcopy(EDGE_CONFIG)
    if directed_graph:
        edge_configs = {}
        for k, v in edges:
            if (v, k) in edges and not dual_arrow:
                edge_configs[(k, v)] = deepcopy(EDGE_CONFIG)
            else:
                edge_configs[(k, v)] = deepcopy(EDGE_CONFIG)
                tip_conf = edge_configs[(k, v)].get("tip_config", {})

                tip_size = tip_conf.get("tip_length", None)
                tip_size = TIP_SIZE if tip_size is None or tip_size <= 0 else tip_size
                edge_configs[(k, v)]["tip_config"]["tip_length"] = tip_size

                tip_width = tip_conf.get("tip_width", None)
                tip_width = DEFAULT_ARROW_TIP_WIDTH if tip_width is None or tip_width <= 0 else tip_width
                edge_configs[(k, v)]["tip_config"]["tip_width"] = tip_width

            if edge_configs[(k, v)].get("edge_type", None) == ArcBetweenPoints and (v, k) not in edges:
                edge_configs[(k, v)]["angle"] = 0

        edge_config = edge_configs

    args = dict(vertices=vertices, edges=edges, layout=layout, layout_scale=layout_scale, labels=labels,
                label_fill_color=LABEL_COLOR, vertex_config=VERTEX_CONFIG.copy(), edge_config=edge_config,
                edge_type=edge_type, vertex_type=vertex_type, root_vertex=1)

    if weights is not None:
        graph_type = WeightedGraph
        if not directed_graph:
            weights = {**{(v, u): w for (u, v), w in weights.items()}, **weights}
        args["weights"] = weights

    graph = graph_type(**args)
    if rescale_vertices:
        graph[list(graph.vertices.keys())[0]].scale_to_fit_width(VERTEX_WIDTH)

    for i, vertex in enumerate(graph.vertices):
        if not labels:
            continue
        label = graph[vertex][1]
        graph[vertex].remove(label)
        label.move_to(graph[vertex])

        if rescale_vertices:
            graph[vertex].scale_to_fit_height(graph[list(graph.vertices.keys())[0]].height)
            label.scale_to_fit_height(graph[vertex].height * 0.5)
        else:
            label.scale(VERTEX_LABEL_SCALE)

        graph[vertex].add(label)

    relative_scale = config.frame_width * 0.4 if graph.width > graph.height else config.frame_height * 0.7
    graph.scale_to_fit_width(relative_scale).move_to(ORIGIN).to_edge(RIGHT, buff=0.2)
    return graph


def get_graph_convex_hull(graph: DiGraph | WeightedGraph, buff=None, round_radius=None, **kwargs) -> Polygon:
    points = np.array([vertex.get_center()[:2] for vertex in graph.vertices.values()])
    buff = buff if buff is not None else next(iter(graph.vertices.values())).get_width() * 2.8
    round_radius = round_radius if round_radius is not None else 0
    return get_convex_hull_polygon(points, round_radius=round_radius, **kwargs).surround(graph, buff=buff)


# ---------------------------- graph cut ----------------------------
def get_vertices_cut(graph: DiGraph | WeightedGraph, vertices: list[Hashable], buff=None, scale=0.8,
                     round_radius=None, **kwargs) -> Polygon:
    buff = buff if buff is not None else next(iter(graph.vertices.values())).get_width() * 2
    round_radius = round_radius if round_radius is not None else next(iter(graph.vertices.values())).get_width() * 0.5
    polygons = get_vertices_voronoi_polygons(graph, buff=buff, round_radius=0, **kwargs)
    vertex_to_polygon = {vertex: polygon for vertex, polygon in zip(graph.vertices, polygons)}
    if len(vertices) == 1:
        return vertex_to_polygon[vertices[0]].round_corners(round_radius).scale(scale)
    cut = VGroup(*[vertex_to_polygon[vertex] for vertex in vertices])
    ret = VGroup()
    fix_scale_cut = VGroup()
    scale_a = 0.8
    scale = 0.7
    shift_size = 0.2
    polygon_neghibors = set()
    edges_cut = {}
    for i, vertex_a in enumerate(vertices):
        for vertex_b in vertices[i + 1:]:
            tangent_points = get_tangent_points(vertex_to_polygon[vertex_a], vertex_to_polygon[vertex_b])
            if len(tangent_points) >= 2:
                polygon_neghibors.add((vertex_a, vertex_b))
                polygon_neghibors.add((vertex_b, vertex_a))
                line_a = Line(tangent_points[0], tangent_points[1]).scale(scale_a).move_to(
                    graph.vertices[vertex_b].get_center())
                line_a.shift(-(line_a.get_center() - graph.vertices[vertex_a].get_center()) * shift_size)
                line_b = Line(tangent_points[0], tangent_points[1]).scale(scale_a).move_to(
                    graph.vertices[vertex_a].get_center())
                line_b.shift(-(line_b.get_center() - graph.vertices[vertex_b].get_center()) * shift_size)
                fix_scale_cut += Polygon(
                    *[line_b.get_end(), line_a.get_end(), line_a.get_start(), line_b.get_start()][::-1],
                    **kwargs).round_corners(0.1, components_per_rounded_corner=8)

                edges_cut[(vertex_a, vertex_b)] = fix_scale_cut[-1]
                ret += Polygon(*[line_a.get_start(), line_a.get_end(), line_b.get_end(), line_b.get_start()],
                               **kwargs)
    trig = VGroup()
    for tri in find_all_triangular_in_vertives_set(polygon_neghibors, vertices):
        vertex_poly_tri = [vertex_to_polygon[vertex] for vertex in tri]
        cut += boolean_op_to_polygons(Union(*[vertex_to_polygon[vertex] for vertex in tri]), convex_hull=False,
                                      **kwargs).surround(VGroup(*vertex_poly_tri), buff=0, stretch=True).scale(
            scale * 1.7)
        trig += cut[-1]
        remove_poly = [edges_cut[edge] for edge in edges_cut if edge[0] in tri and edge[1] in tri]
        fix_scale_cut.remove(*remove_poly)
        cut.remove(*remove_poly)
    cut = VGroup(*[polygon.scale(scale) for polygon in cut])
    new_group = VGroup(*fix_scale_cut, *cut)
    real_ret = boolean_op_to_polygons(Union(*new_group), convex_hull=False,
                                      **kwargs).round_corners(0.3, components_per_rounded_corner=8)
    return real_ret


def find_all_triangular_in_vertives_set(neighbors_edges, vertices: list[Hashable]) -> set[set[Hashable]]:
    ret = set()
    for i, vertex_a in enumerate(vertices):
        for j, vertex_b in enumerate(vertices[i + 1:]):
            for vertex_c in vertices[j + 1:]:
                if (vertex_a, vertex_b) in neighbors_edges and (vertex_b, vertex_c) in neighbors_edges and (vertex_c,
                                                                                                            vertex_a) in neighbors_edges:
                    ret.add((vertex_a, vertex_b, vertex_c))
    return ret


def get_vertices_voronoi_polygons(graph: DiGraph | WeightedGraph, round_radius: float = None, buff=None, **kwargs) -> \
        VGroup[Polygon]:
    graph_hull = get_graph_convex_hull(graph, buff=buff, **kwargs)
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
