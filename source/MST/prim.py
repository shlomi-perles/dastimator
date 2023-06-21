from __future__ import annotations

import numpy as np

from tools.array import ArrayMob
from tools.scenes import *
from tools.graphs.edge import *
from tools.graphs.node import IndicateNode
from tools.graphs.utils import get_vertices_cut, get_neighbors
from mst_utils import *

ROOT_PATH = Path(__file__).resolve().parent
sys.path.append(str(ROOT_PATH.parent))
OUT_DIR = MEDIA_PATH / Path(__file__).resolve().parent.stem

PRESENTATION_MODE = True
DISABLE_CACHING = False

# --------------------------------- constants --------------------------------- #

PRIM_PSEUDO_CODE = r'''def Prim($G=\left(V,E,w\right)$, root):
    for v $\in V$:
        key[v] = ∞, π[v] = None
    key[root] = 0
    min_heap =  BuildMinHeap($V$) by key
    
    while min_heap  ≠ ø:
        u = ExtractMin(min_heap)
        for neighbor v of u:
            if v in min_heap and w(u,v) < key[v]:
                π[v] = u
                DecreaseKey(min_heap,v,w(u,v))
    return $(V,E')$'''

# PRIM_PSEUDO_CODE = r'''def prim:
#     abc as'''
DEFAULT_NODE_INDICATE_COLOR = "yellow"
PATH_TIME_WIDTH = 0.6
NODE_FROM_OPACITY = 0.5


def get_min_heap_lst(graph: WeightedGraph, edge_len: float = 1, node_radius: float = 0.2,
                     weight_radius: float = 1) -> VGroup:
    vertex_lst = VGroup()
    for vertex in graph.vertices:
        start_node = Node("").scale_to_fit_width(node_radius * 2).set_opacity(NODE_FROM_OPACITY)
        end_node = Node(vertex).scale_to_fit_width(node_radius * 2).shift(edge_len * RIGHT)
        edge_mob = Edge(start_node, end_node, weight=np.Inf, color=EDGE_COLOR, stroke_width=7)
        edge_mob.put_start_and_end_on(start_node.get_right(), end_node.get_left())
        edge_mob.weight_mob.scale_to_fit_width(weight_radius * node_radius * 3 / 2).set_stroke_width(0)
        vertex_lst += VGroup(edge_mob, start_node, end_node)

    return vertex_lst.arrange_in_grid(buff=0.5, rows=3).scale_to_fit_width(
        (config.frame_width - graph.width) * 0.80)


class Prim(SectionsScene):
    def __init__(self, graph: WeightedGraph, root: Hashable = None, **kwargs):
        self.graph = graph.scale(0.94).to_edge(RIGHT, buff=0.7)
        self.graph.remove_updater(self.graph.update_edges)
        self.root = root
        self.cut = VGroup().move_to(self.graph.vertices[self.root])
        self.code = create_code(PRIM_PSEUDO_CODE, line_no_buff=0.6).scale_to_fit_width(
            config.frame_width * 0.47).to_corner(LEFT + UP)
        self.min_heap = self.create_min_heap()
        # self.heap_loc = [edge.get_center()]
        # self.code = Rectangle()
        self.board_width = (config.frame_width - graph.width) * 0.80
        super().__init__(**kwargs)

    def prim(self, **kwargs):
        vertices_in_cut = []
        self.next_section("init prim")
        self.highlight_and_indicate_code([2, 3])
        self.play(Create(self.min_heap))

        self.next_section("root key")
        self.highlight_and_indicate_code([4])
        root_edge = self.find_in_heap(self.root)
        self.play(root_edge[0].set_weight(0), Flash(root_edge[0].weight_mob))

        self.next_section("build min heap")
        self.highlight_and_indicate_code([5])
        self.next_section("build min heap visu")
        self.sort_heap()

        while len(self.min_heap) > 0:
            self.next_section("while min heap not empty")
            self.highlight_and_indicate_code([7, 8])

            self.next_section("extract min")
            min_edge = self.min_heap[-1]
            min_heap_vertex = min_edge[2]
            min_graph_vertex = self.graph.vertices[min_heap_vertex.key]
            parent_heap_vertex = min_edge[1]
            parent_graph_vertex = None
            nodes_to_indicate = [min_heap_vertex, min_graph_vertex]

            if isinstance(parent_heap_vertex.key, int):
                parent_graph_vertex = self.graph.vertices[parent_heap_vertex.key]
                nodes_to_indicate += [parent_heap_vertex, parent_graph_vertex]

            self.play(*[IndicateNode(node, color_theme=DEFAULT_NODE_INDICATE_COLOR, preserve_indicate_color=True)
                        for node in nodes_to_indicate])

            if parent_graph_vertex is not None:
                self.next_section("show mst edge")
                self.add_mst_edge(parent_heap_vertex.key, min_heap_vertex.key)

            self.next_section("remove from heap")
            vertices_in_cut.append(min_heap_vertex.key)
            new_cut = self.get_cut(vertices_in_cut)
            self.min_heap.remove(min_edge)
            min_edge.set_z_index(-5)
            self.cut.set_z_index(-5)
            self.play(ReplacementTransform(self.cut, new_cut), Unwrite(min_edge))
            self.cut = new_cut
            self.cut.set_z_index(-5)
            self.sort_heap()
            self.next_section("show cut phase")
            if parent_graph_vertex is not None:
                self.play(
                    IndicateNode(parent_graph_vertex, color_theme="blue", scale_factor=1, preserve_indicate_color=True))
            self.highlight_and_indicate_code([9, 10, 11, 12])
            neighbors = []
            for neighbor in get_neighbors(self.graph, min_heap_vertex.key):
                self.next_section("show neighbors")
                self.highlight_and_indicate_code([9])
                neighbor_graph_vertex = self.graph.vertices[neighbor]
                neighbors.append(neighbor_graph_vertex)
                self.play(
                    IndicateNode(neighbor_graph_vertex, color_theme="green", preserve_indicate_color=True))
                new_weight = self.graph.edges[(min_heap_vertex.key, neighbor)].weight

                self.next_section("check if in cut")
                self.highlight_and_indicate_code([10])
                relax_nodes = [neighbor_graph_vertex]
                if neighbor not in vertices_in_cut and new_weight < self.find_in_heap(neighbor)[0].weight:
                    neighbor_heap_edge = self.find_in_heap(neighbor)
                    relax_nodes.append(neighbor_heap_edge[2])
                    self.play(IndicateNode(neighbor_heap_edge[2], color_theme="green", preserve_indicate_color=True))

                    self.next_section("decrease key and update pi")
                    self.highlight_and_indicate_code([11, 12])
                    self.update_label(neighbor_heap_edge, min_heap_vertex.key)
                    # self.play(neighbor_heap_edge[1].animate.set_label(str(min_heap_vertex.key)),
                    #           Flash(neighbor_heap_edge[1].label))
                    self.next_section("decrease key visu")
                    self.decrease_key(neighbor, new_weight)
                    self.wait(0.2)
                self.play(*[IndicateNode(node, color_theme="blue", preserve_indicate_color=True,
                                         scale_factor=1) for node in relax_nodes])
            self.play(*[IndicateNode(node, color_theme="blue", preserve_indicate_color=True, scale_factor=1) for node in
                        neighbors],
                      IndicateNode(min_graph_vertex, color_theme="blue", preserve_indicate_color=True, scale_factor=1))
        self.play(highlight_code_lines(self.code, list(range(1, 14)), indicate=False))

    def update_label(self, edge: VGroup, new_label: int | str):
        node = edge[1]
        node.key = new_label
        new_label = MathTex(str(new_label), fill_color=LABEL_COLOR).match_height(edge[2].label).move_to(
            node).set_opacity(node.get_fill_opacity())
        node.label.move_to(new_label)
        self.play(node.label.animate.become(new_label), Flash(new_label))

    def find_in_heap(self, v: Hashable) -> VGroup:
        for edge in self.min_heap:
            if edge[2].key == v:
                return edge

    def highlight_and_indicate_code(self, lines: list, **kwargs):  # TODO: implement code scene
        highlight, indicate = highlight_code_lines(self.code, lines, **kwargs)
        self.play(highlight)
        self.play(indicate)

    def add_mst_edge(self, u, v):
        anim1, anim2 = self.graph.edges[(u, v)].animate_move_along_path(**MST_PATH_PARAMS), self.graph.edges[
            (v, u)].animate_move_along_path(
            **{"opposite_direction": True, **MST_PATH_PARAMS})
        self.play(anim1, anim2)

    def decrease_key(self, v: Hashable, key: float, **kwargs):
        for edge in self.min_heap:
            if edge[2].key == v:
                edge[0].set_weight(key)
                self.play(edge[0].set_weight(key), Flash(edge[0].weight_mob), **kwargs)
                self.sort_heap(**kwargs)
                return

    def sort_heap(self, **kwargs):
        prev_loc = [edge for edge in self.min_heap]
        self.min_heap.sort(submob_func=lambda x: -x[0].weight)
        anims = [edge.animate.move_to(prev_loc[i]) for i, edge in enumerate(self.min_heap)]
        if len(anims) > 0:
            self.play(*anims, **kwargs)

    def create_min_heap(self) -> VGroup:
        scale = 1
        start_vars_y = self.code.get_bottom()[1]
        min_heap = get_min_heap_lst(self.graph).scale(scale)
        return min_heap.to_edge(LEFT).set_y(start_vars_y - (start_vars_y + config.frame_height / 2) / 2)

    def find_circle_in_union(self, u, v, **kwargs):
        pass

    def get_cut(self, vertices: list[Hashable], **kwargs) -> Polygon:
        return get_vertices_cut(self.graph, vertices, **{**kwargs, **DEFAULT_CUT_PARAMS}).set_z_index(-5)


class PrimExample(Prim):
    def __init__(self, **kwargs):
        super().__init__(get_main_graph_example(), root=5, **kwargs)

    def construct(self):
        # TODO: animate that in fact key is the edges in the cut (and the low opacity vertex is pi)
        self.next_section("Prim Example", pst.NORMAL)
        self.play(Write(self.graph), Write(self.code))
        self.prim()
        self.next_section("Prim End")
        self.play(Unwrite(self.cut))
        self.wait()


class PrimComplexity(Prim):
    def __init__(self, **kwargs):
        super().__init__(get_main_graph_example(), root=5, **kwargs)

    def construct(self):
        self.add(self.graph, self.code)
        self.next_section("Prim Complexity", pst.NORMAL)
        total_complexity = MathTex(r"\left(\left|E\right|+\left|V\right|\right)", r"\log\left|V\right|").next_to(
            self.code, DOWN, buff=3).match_width(self.code).scale(0.7)
        self.highlight_and_indicate_code([7, 9])
        self.play(Write(total_complexity[0]))

        self.next_section("heap")
        self.highlight_and_indicate_code([7, 8, 9, 12])
        self.play(Write(total_complexity[1:]))
        self.next_section("total complexity")
        self.next_section("end")
        self.play(Unwrite(total_complexity), Unwrite(self.code), Unwrite(self.graph))
        self.wait()


if __name__ == "__main__":
    scenes_lst = [PrimExample, PrimComplexity]

    run_scenes(scenes_lst, OUT_DIR, PRESENTATION_MODE, DISABLE_CACHING, gif_scenes=[28 + i for i in range(6)],
               create_gif=False)
