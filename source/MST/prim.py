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

PRIM_PSEUDO_CODE = r'''def Prim($G=\left(V,E,w\right)$, root):
    for $v\in V$:
        key[$v$]$\leftarrow\infty$, $\pi\left[v\right]\leftarrow$None
    key[toor]$\leftarrow0$
    $Q\leftarrow$ BuildMinHeap($V$) by key
    #6
    while $Q\neq\emptyset$:
        $u\leftarrow$ ExtractMin($Q$)
        for neighbor $v$ of $u$:
            if $v\in Q$ and $w\left(u,v\right)<$key[$v$]:
                $\pi\left[v\right]\leftarrow u$
                DecreaseKey($Q,v,w\left(u,v\right)$)
    return $(V,E')$'''

# KRUSKAL_UNION_PSEUDO_CODE = r'''def Kruskal:
#     abc $G$'''
DEFAULT_NODE_INDICATE_COLOR = "yellow"
PATH_TIME_WIDTH = 0.6


class Prim(SectionsScene):
    def __init__(self, graph, **kwargs):
        self.graph = graph.scale(0.94).to_edge(RIGHT, buff=0.7)
        self.graph.remove_updater(self.graph.update_edges)
        self.code = create_code(PRIM_PSEUDO_CODE, line_no_buff=0.6).scale_to_fit_width(
            config.frame_width * 0.47).to_corner(LEFT + UP)
        # self.edges_lst = get_edges_lst(self.graph).match_width(self.code).to_corner(LEFT + DOWN)
        # self.code = Rectangle()
        self.board_width = (config.frame_width - graph.width) * 0.80
        super().__init__(**kwargs)

    def prim(self, **kwargs):
        self.add(self.code)

    def highlight_and_indicate_code(self, lines: list, **kwargs):  # TODO: implement code scene
        highlight, indicate = highlight_code_lines(self.code, lines, **kwargs)
        self.play(highlight)
        self.play(indicate)

    def select_edge(self, edge):
        edge.next_to(self.code, DOWN, buff=0).set_y(
            self.code.get_bottom()[1] - (self.code.get_bottom() - self.edges_lst.get_top())[
                1] / 2).scale_to_fit_width(self.board_width * 0.7)
        edge[0].set_stroke_width(3)
        edge[0].weight_mob.scale(0.8)
        # self.play(edge.animate.next_to(self.code, DOWN, buff=0).set_y(
        #     self.code.get_bottom()[1] - (self.code.get_bottom() - self.edges_lst.get_top())[
        #         1] / 2).scale_to_fit_width(self.board_width * 0.7),
        #           edge[0].animate.set_stroke_width(3))

    def find_circle_in_union(self, u, v, **kwargs):
        pass

    def get_cut(self, vertices: list[Hashable], **kwargs) -> Polygon:
        return get_vertices_cut(self.graph, vertices, **{**kwargs, **DEFAULT_CUT_PARAMS}).set_z_index(-1)


class PrimExample(Prim):
    def __init__(self, **kwargs):
        super().__init__(get_main_graph_example(), **kwargs)

    def construct(self):
        self.next_section("Kruskal Example", pst.NORMAL)
        # self.add(self.graph, self.code)
        # self.wait()
        self.add(self.code)
        explain, explain_anim = code_explain(self.code, [8, 9, 10], "Find circle")
        self.play(explain_anim)
        self.wait()

        # self.add(self.graph, self.code)
        # self.prim()
        # self.wait()
        return


if __name__ == "__main__":
    scenes_lst = [PrimExample]

    run_scenes(scenes_lst, OUT_DIR, PRESENTATION_MODE, DISABLE_CACHING, gif_scenes=[28 + i for i in range(6)],
               create_gif=False)
