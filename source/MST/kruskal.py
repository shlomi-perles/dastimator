from __future__ import annotations

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
# KRUSKAL_UNION_PSEUDO_CODE = r'''def Kruskal:
#     abc $G$'''
DEFAULT_NODE_INDICATE_COLOR = "yellow"
PATH_TIME_WIDTH = 0.6


def get_edges_lst(graph: WeightedGraph, edge_len: float = 1, node_radius: float = 0.2,
                  directed: bool = False) -> VGroup:
    edges_lst = VGroup()
    add_edges = set()
    for (u, v), edge in graph.edges.items():
        if edge.weight is None or (not directed and ((v, u) in add_edges)):
            continue
        if not directed and graph.vertices[u].get_x() > graph.vertices[v].get_x():
            continue
        add_edges.add((u, v))
        start_node = Node(u).scale_to_fit_width(node_radius * 2)
        end_node = Node(v).scale_to_fit_width(node_radius * 2).shift(edge_len * RIGHT)
        edge_mob = Edge(start_node, end_node, weight=edge.weight, color=EDGE_COLOR, stroke_width=7)
        edge_mob.weight_mob.scale_to_fit_width(node_radius * 3 / 2).set_stroke_width(0)
        edges_lst += VGroup(edge_mob, start_node, end_node)

    return edges_lst.arrange_in_grid(buff=(0.5, 0.3), rows=3).scale_to_fit_width(
        (config.frame_width - graph.width) * 0.80)


class KruskalUnion(SectionsScene):
    def __init__(self, graph, **kwargs):
        self.graph = graph.scale(0.94).to_edge(RIGHT, buff=0.7)
        self.graph.remove_updater(self.graph.update_edges)
        self.code = create_code(KRUSKAL_UNION_PSEUDO_CODE, line_no_buff=0.6).scale_to_fit_width(
            config.frame_width * 0.47).to_corner(LEFT + UP)
        self.edges_lst = get_edges_lst(self.graph).match_width(self.code).to_corner(LEFT + DOWN)
        # self.code = Rectangle()
        self.board_width = (config.frame_width - graph.width) * 0.80
        super().__init__(**kwargs)

    def sort_edges(self, **kwargs) -> AnimationGroup:
        self.edges_lst.sort(submob_func=lambda x: x[0].weight)
        return self.edges_lst.animate.arrange_in_grid(buff=(0.5, 0.3), rows=3)

    def kruskal(self, **kwargs):
        self.add(self.code)
        find_mst = False
        vertices = self.graph.vertices

        cuts_to_vertices, vertices_to_cuts = {}, {}
        self.next_section("MakeSet")
        anims = []
        for i in vertices:
            cut = self.get_cut([i])
            cuts_to_vertices[cut] = {i}
            vertices_to_cuts[i] = cut
            anims.append(FadeIn(VGroup(cut)))
        self.highlight_and_indicate_code([2, 3])
        self.play(AnimationGroup(*anims, run_time=2, lag_ratio=0.5))

        self.next_section("Sort edges")
        self.highlight_and_indicate_code([4])
        self.next_section("Sort visu")
        self.play(self.sort_edges())

        self.next_section("Initialize MST")
        mst_list = []
        self.highlight_and_indicate_code([5])
        edges = [edge for edge in self.edges_lst]
        for edge in edges:
            self.next_section("Get edge", skip_section=find_mst)
            u_node, v_node = edge[0].start, edge[0].end
            u, v = u_node.key, v_node.key
            self.highlight_and_indicate_code([7])
            self.edges_lst.remove(edge)
            self.play(edge.animate.next_to(self.code, DOWN, buff=0).set_y(
                self.code.get_bottom()[1] - (self.code.get_bottom() - self.edges_lst.get_top())[
                    1] / 2).scale_to_fit_width(self.board_width * 0.7))

            self.next_section("Find set", skip_section=find_mst)
            self.highlight_and_indicate_code([8])
            self.next_section("Find set visu", skip_section=find_mst)
            self.play(IndicateNode(u_node, color_theme=DEFAULT_NODE_INDICATE_COLOR, preserve_indicate_color=True),
                      IndicateNode(v_node, color=DEFAULT_NODE_INDICATE_COLOR, preserve_indicate_color=True),
                      IndicateNode(vertices[u], color=DEFAULT_NODE_INDICATE_COLOR, preserve_indicate_color=True),
                      IndicateNode(vertices[v], color=DEFAULT_NODE_INDICATE_COLOR, preserve_indicate_color=True))

            cut_u, cut_v = vertices_to_cuts[u], vertices_to_cuts[v]

            if cut_u != cut_v:
                self.next_section("Add edge", skip_section=find_mst)
                self.highlight_and_indicate_code([9])
                self.next_section("Add edge visu", skip_section=find_mst)
                path_ind_params = dict(width_factor=EDGE_TREE_PATH_WIDTH_FACTOR, time_width=PATH_TIME_WIDTH * 2,
                                       preserve_state=True, run_time=1)
                self.play(self.graph.edges[(u, v)].animate_move_along_path(**path_ind_params),
                          self.graph.edges[(v, u)].animate_move_along_path(
                              **{"opposite_direction": True, **path_ind_params}))

                self.next_section("Union", skip_section=find_mst)
                self.highlight_and_indicate_code([10])
                self.next_section("Union visu", skip_section=find_mst)
                new_cut_vertices = cuts_to_vertices[cut_u] | cuts_to_vertices[cut_v]
                cut = self.get_cut(list(new_cut_vertices))
                cuts_to_vertices[cut] = new_cut_vertices
                for vertex in new_cut_vertices:
                    vertices_to_cuts[vertex] = cut
                self.play(ReplacementTransform(VGroup(cut_u, cut_v), cut))

                mst_list.append(edge)
            self.next_section("Remove preview edge", skip_section=find_mst)
            self.play(FadeOut(edge),
                      IndicateNode(vertices[u], color_theme="blue", preserve_indicate_color=True, scale_factor=1),
                      IndicateNode(vertices[v], color_theme="blue", preserve_indicate_color=True, scale_factor=1))
            if len(mst_list) == len(vertices) - 1:
                find_mst = True
            # if u == 5 or v == 5:
            return
        # self.play(self.sort_edges())

    def highlight_and_indicate_code(self, lines: list, **kwargs):  # TODO: implement code scene
        highlight, indicate = highlight_code_lines(self.code, lines, **kwargs)
        self.play(highlight)
        self.play(indicate)

    def find_circle_in_union(self, u, v, **kwargs):
        pass

    def get_cut(self, vertices: list[Hashable], **kwargs) -> Polygon:
        return get_vertices_cut(self.graph, vertices, **{**kwargs, **DEFAULT_CUT_PARAMS}).set_z_index(-1)


class KruskalUnionExample(KruskalUnion):
    def __init__(self, **kwargs):
        super().__init__(get_main_graph_example(), **kwargs)

    def construct(self):
        self.next_section("Kruskal Example", pst.NORMAL)
        # self.add(self.graph, self.code)
        # self.wait()
        self.add(self.graph, self.edges_lst, self.code)

        # explain, explain_anim = code_explain(self.code, [8, 9, 10], "Find circle")
        # self.play(explain_anim)

        self.kruskal()
        self.wait()
        return


if __name__ == "__main__":
    scenes_lst = [KruskalUnionExample]

    run_scenes(scenes_lst, OUT_DIR, PRESENTATION_MODE, DISABLE_CACHING, gif_scenes=[28 + i for i in range(6)],
               create_gif=False)
