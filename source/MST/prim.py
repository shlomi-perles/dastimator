from __future__ import annotations

from tools.array import ArrayMob
from tools.scenes import *
from tools.graphs.edge import *
from tools.graphs.node import IndicateNode
from tools.graphs.utils import get_vertices_cut
from mst_utils import *

ROOT_PATH = Path(__file__).resolve().parent
sys.path.append(str(ROOT_PATH.parent))
OUT_DIR = MEDIA_PATH / Path(__file__).resolve().parent.stem

PRESENTATION_MODE = False
DISABLE_CACHING = False

# --------------------------------- constants --------------------------------- #

PRIM_PSEUDO_CODE = r'''def Prim($G=\left(V,E,w\right)$, root):
    for v $\in V$:
        key[v] = ∞, π[v] = None
    key[toor] = 0
    min_heap =  BuildMinHeap($V$) by key
    #6
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
        edge_mob = Edge(start_node, end_node, weight="\infty", color=EDGE_COLOR, stroke_width=7)
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
        self.cut = self.get_cut([root])
        self.code = create_code(PRIM_PSEUDO_CODE, line_no_buff=0.6).scale_to_fit_width(
            config.frame_width * 0.47).to_corner(LEFT + UP)
        self.min_heap = self.create_min_heap()
        # self.code = Rectangle()
        self.board_width = (config.frame_width - graph.width) * 0.80
        super().__init__(**kwargs)

    def prim(self, **kwargs):
        self.next_section("init prim")
        self.play(self.highlight_and_indicate_code([2, 3]))

    def highlight_and_indicate_code(self, lines: list, **kwargs):  # TODO: implement code scene
        highlight, indicate = highlight_code_lines(self.code, lines, **kwargs)
        self.play(highlight)
        self.play(indicate)

    def decrease_key(self, v: Hashable, key: float, **kwargs):
        for edge in self.min_heap:
            if edge[2].key == v:
                edge[0].set_weight(key)
                self.play(edge[0].weight_mob.set_value(key), Flash(edge[0].weight_mob), **kwargs)
                self.sort_heap(**kwargs)
                return

    def sort_heap(self, **kwargs) -> AnimationGroup:
        self.min_heap.sort(submob_func=lambda x: x[0].weight)
        return self.min_heap.animate(**kwargs).arrange_in_grid(buff=(0.5, 0.3), rows=3)

    def create_min_heap(self) -> VGroup:
        scale = 1
        start_vars_y = self.code.get_bottom()[1]
        min_heap = get_min_heap_lst(self.graph).scale(scale)
        return min_heap.to_edge(LEFT).set_y(start_vars_y - (start_vars_y + config.frame_height / 2) / 2)

    def find_circle_in_union(self, u, v, **kwargs):
        pass

    def update_cut(self, vertices: list[Hashable], **kwargs):
        new_cut = self.get_cut(vertices)
        self.play(Transform(self.cut, new_cut), **kwargs)

    def get_cut(self, vertices: list[Hashable], **kwargs) -> Polygon:
        return get_vertices_cut(self.graph, vertices, **{**kwargs, **DEFAULT_CUT_PARAMS}).set_z_index(-1)


class PrimExample(Prim):
    def __init__(self, **kwargs):
        super().__init__(get_main_graph_example(), root=5, **kwargs)

    def construct(self):
        # TODO: animate that in fact key is the edges in the cut
        self.next_section("Kruskal Example", pst.NORMAL)
        self.add(self.min_heap)
        self.add(self.graph)
        self.add(self.code)
        # explain, explain_anim = code_explain(self.code, [9, 10, 11], "Update min in cut")
        # self.play(explain_anim)
        self.wait()

        # self.add(self.graph, self.code)
        # self.prim()
        # self.wait()
        return


if __name__ == "__main__":
    scenes_lst = [PrimExample]

    run_scenes(scenes_lst, OUT_DIR, PRESENTATION_MODE, DISABLE_CACHING, gif_scenes=[28 + i for i in range(6)],
               create_gif=False)
