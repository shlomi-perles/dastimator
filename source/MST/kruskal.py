from __future__ import annotations

from manim_editor import PresentationSectionType as pst

from tools.scenes import *
from tools.consts import *
from tools.graphs.edge import *
from mst_utils import *

ROOT_PATH = Path(__file__).resolve().parent
sys.path.append(str(ROOT_PATH.parent))
OUT_DIR = MEDIA_PATH / Path(__file__).resolve().parent.stem

PRESENTATION_MODE = False
DISABLE_CACHING = True

# --------------------------------- constants --------------------------------- #

KRUSKAL_UNION_PSEUDO_CODE = r'''def Kruskal($G=\left(V,E,w\right)$):
    for $v\in V$:
        MakeSet($v$)
    sort $E$ into $e_{1},e_{2},\ldots,e_{m}$ by weight
    $E'\leftarrow\emptyset$
    
    for $e_{i}=(u_{i},v_{i})\in E$:
        if FindSet($u_{i}$) $\neq$ FindSet($v_{i}$):
            $E'\leftarrow E'\cup\left\{ e_{i}\right\} $
            Union($u_{i},v_{i}$)
    return $(V,E')$'''


def get_edges_lst(graph: WeightedGraph, edge_len: float = 1, node_radius: float = 0.2):
    edges_lst = VGroup()
    add_edges = set()
    for (u, v), edge in graph.edges.items():
        if edge.weight is None or (v, u) in add_edges:
            continue
        add_edges.add((u, v))
        start_node = Node(u).scale_to_fit_width(node_radius * 2)
        end_node = Node(v).scale_to_fit_width(node_radius * 2).shift(edge_len * RIGHT)
        edge = Edge(start_node, end_node, weight=edge.weight, color=EDGE_COLOR, stroke_width=7)
        edge.weight_mob.scale_to_fit_width(node_radius * 3 / 2).set_stroke_width(0)
        edges_lst += VGroup(edge, start_node, end_node)

    return edges_lst.arrange_in_grid(buff=(0.5, 0.3), rows=3).scale_to_fit_width(
        (config.frame_width - graph.width) * 0.85)


class KruskalUnion(SectionsScene):
    def __init__(self, graph, **kwargs):
        self.graph = graph
        self.edges_lst = get_edges_lst(self.graph).to_edge(DOWN + LEFT)
        # self.code = create_code(KRUSKAL_UNION_PSEUDO_CODE, line_no_buff=0.6)
        super().__init__(**kwargs)

    def sort_edges(self, **kwargs) -> AnimationGroup:
        sorted_lst = sorted(self.edges_lst, key=lambda x: x[0].weight)
        sort_index = {edge: index for index, edge in enumerate(sorted_lst)}
        self.edges_lst.sort(submob_func=lambda x: x[0].weight)
        # return AnimationGroup(*[edge.animate.move_to(self.edges_lst[sort_index[edge]]) for edge in self.edges_lst],
        #                       **kwargs)
        return self.edges_lst.animate.arrange_in_grid(buff=(0.5, 0.3), rows=3)


class KruskalUnionExample(KruskalUnion):
    def __init__(self, **kwargs):
        super().__init__(get_main_graph_example(), **kwargs)

    def construct(self):
        self.next_section("Kruskal Example", pst.NORMAL)
        # self.add(self.graph, self.code)
        self.add(self.graph, self.edges_lst)

        # self.add(self.edges_lst)
        # self.play(self.sort_edges())
        cut = get_vertices_cut(self.graph, [1, 7], color=GREEN, fill_opacity=0.3, fill_color=GREEN)
        cut_2 = get_vertices_cut(self.graph, [2, 3, 4, 5, 6], color=RED, fill_opacity=0.3, fill_color=RED)
        self.add(cut, cut_2)
        self.wait()


if __name__ == "__main__":
    scenes_lst = [KruskalUnionExample]

    run_scenes(scenes_lst, OUT_DIR, PRESENTATION_MODE, DISABLE_CACHING, gif_scenes=[28 + i for i in range(6)],
               create_gif=False)
