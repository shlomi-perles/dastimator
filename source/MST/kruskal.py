from __future__ import annotations

from manim_editor import PresentationSectionType as pst

from tools.graphs.node import IndicateNode
from tools.graphs.utils import get_vertices_cut
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
KRUSKAL_UNION_PSEUDO_CODE = r'''def Kruskal:
    abdasd'''
DEFAULT_NODE_INDICATE_COLOR = "yellow"
PATH_TIME_WIDTH = 0.6


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
        (config.frame_width - graph.width) * 0.80)


class KruskalUnion(SectionsScene):
    def __init__(self, graph, **kwargs):
        self.graph = graph.scale(0.94).to_edge(RIGHT, buff=0.7)
        self.code = create_code(KRUSKAL_UNION_PSEUDO_CODE, line_no_buff=0.6).scale_to_fit_width(
            config.frame_width * 0.4).to_corner(LEFT + UP)
        self.edges_lst = get_edges_lst(self.graph).match_width(self.code).to_corner(LEFT + DOWN)
        # self.code = Rectangle()
        self.board_width = (config.frame_width - graph.width) * 0.80
        super().__init__(**kwargs)

    def sort_edges(self, **kwargs) -> AnimationGroup:
        self.edges_lst.sort(submob_func=lambda x: x[0].weight)
        return self.edges_lst.animate.arrange_in_grid(buff=(0.5, 0.3), rows=3)

    def kruskal(self, **kwargs):
        vertices = self.graph.vertices
        cuts_to_vertices, vertices_to_cuts = {}, {}
        self.next_section("Kruskal run")
        anims = []
        for i in vertices:
            cut = self.get_cut([i])
            cuts_to_vertices[cut] = {i}
            vertices_to_cuts[i] = cut
            anims.append(FadeIn(cut))
        self.play(*anims)
        self.play(self.sort_edges())
        mst_list = []
        self.next_section("Kruskal run")
        for edge in self.edges_lst:
            u_node, v_node = edge[0].start, edge[0].end
            u, v = u_node.key, v_node.key
            self.play(edge.animate.next_to(self.code, DOWN, buff=0).set_y(
                self.code.get_bottom()[1] - (self.code.get_bottom() - self.edges_lst.get_top())[
                    1] / 2).scale_to_fit_width(self.board_width * 0.7))
            self.play(IndicateNode(u_node, color_theme=DEFAULT_NODE_INDICATE_COLOR, preserve_indicate_color=True),
                      IndicateNode(v_node, color=DEFAULT_NODE_INDICATE_COLOR, preserve_indicate_color=True),
                      IndicateNode(vertices[u], color=DEFAULT_NODE_INDICATE_COLOR, preserve_indicate_color=True),
                      IndicateNode(vertices[v], color=DEFAULT_NODE_INDICATE_COLOR, preserve_indicate_color=True))

            cut_u, cut_v = vertices_to_cuts[u], vertices_to_cuts[v]

            if cut_u != cut_v:
                self.play(self.graph.edges[(u, v)].animate_move_along_path(width_factor=EDGE_TREE_PATH_WIDTH_FACTOR,
                                                                           time_width=PATH_TIME_WIDTH * 2),
                          self.graph.edges[(v, u)].animate_move_along_path(width_factor=EDGE_TREE_PATH_WIDTH_FACTOR,
                                                                           time_width=PATH_TIME_WIDTH * 2,
                                                                           opposite_direction=True))
                new_cut_vertices = cuts_to_vertices[cut_u] | cuts_to_vertices[cut_v]
                cut = self.get_cut(list(new_cut_vertices))
                self.play(ReplacementTransform(VGroup(cut_u, cut_v), cut))
                cuts_to_vertices[cut] = new_cut_vertices
                vertices_to_cuts[u] = vertices_to_cuts[v] = cut
                mst_list.append(edge)
            self.play(FadeOut(edge),
                      IndicateNode(vertices[u], color="blue", preserve_indicate_color=True, scale_factor=1),
                      IndicateNode(vertices[v], color="blue", preserve_indicate_color=True, scale_factor=1))
            return
        # self.play(self.sort_edges())

    def get_cut(self, vertices: list[Hashable], **kwargs):
        return get_vertices_cut(self.graph, vertices, **{**kwargs, **DEFAULT_CUT_PARAMS}).set_z_index(-1)


class KruskalUnionExample(KruskalUnion):
    def __init__(self, **kwargs):
        super().__init__(get_main_graph_example(), **kwargs)

    def construct(self):
        self.next_section("Kruskal Example", pst.NORMAL)
        # self.add(self.graph, self.code)
        # self.wait()
        self.add(self.graph, self.edges_lst, self.code)
        self.kruskal()
        self.wait()
        return

        # self.add(self.edges_lst)
        # self.play(self.sort_edges())
        # cut = get_vertices_cut(self.graph, [1, 7], color=GREEN, fill_opacity=0.3, fill_color=GREEN)
        # self.add(cut)
        # cut_2 = get_vertices_cut(self.graph, [2, 3, 4, 5, 6], color=RED, fill_opacity=0.3, fill_color=RED)
        # self.add(cut_2)
        # cut_3 = get_vertices_cut(self.graph, [1, 7, 2], color=GREEN, fill_opacity=0.3, fill_color=GREEN)
        # # self.add(cut_3)
        # self.play(self.sort_edges())
        cut_1 = get_vertices_cut(self.graph, [7, 1], color=RED, fill_opacity=0.3, fill_color=RED)
        self.add(cut_1)
        cut_2 = get_vertices_cut(self.graph, [7, 1, 3], color=RED, fill_opacity=0.3, fill_color=RED)
        self.play(ReplacementTransform(cut_1, cut_2))
        cut_3 = get_vertices_cut(self.graph, [6, 5], color=RED, fill_opacity=0.3, fill_color=RED)
        self.play(FadeIn(cut_3))
        cut_4 = get_vertices_cut(self.graph, [7, 1, 3, 2], color=RED, fill_opacity=0.3, fill_color=RED)
        self.play(ReplacementTransform(cut_2, cut_4))
        cut_5 = get_vertices_cut(self.graph, [7, 1, 3, 2, 6, 5], color=RED, fill_opacity=0.3, fill_color=RED)
        self.play(ReplacementTransform(VGroup(cut_3, cut_4), cut_5))
        # cut_2 = VGroup()
        self.wait()


if __name__ == "__main__":
    scenes_lst = [KruskalUnionExample]

    run_scenes(scenes_lst, OUT_DIR, PRESENTATION_MODE, DISABLE_CACHING, gif_scenes=[28 + i for i in range(6)],
               create_gif=False)
