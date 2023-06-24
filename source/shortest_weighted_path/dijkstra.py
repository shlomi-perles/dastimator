from __future__ import annotations

from tools.array import ArrayMob
from tools.scenes import *
from shortes_path_utils import *

ROOT_PATH = Path(__file__).resolve().parent
sys.path.append(str(ROOT_PATH.parent))
OUT_DIR = MEDIA_PATH / Path(__file__).resolve().parent.stem

PRESENTATION_MODE = False
DISABLE_CACHING = False

# --------------------------------- constants --------------------------------- #

DIJKSTRA_PSEUDO_CODE = r'''def Dijkstra($G=\left(V,E,w\right),s$):
    Initialize-Single-Source($G,s$)
    heap = BuildMinHeap($V$) by v.d
    
    while heap ≠ ø:
        u = Extract-Min(Q)
        for neighbor v of u:
            Relax(u,v,w) # update best path'''

RELAX_PSEUDO_CODE = r'''def Relax(u,v,w):
    if v.d > u.d + w(u,v):
        v.d = u.d + w(u,v)
        v.π = u
        Decrease-Key(Q,v,v.d)'''
# KRUSKAL_UNION_PSEUDO_CODE = r'''def Kruskal:
#     abc $G$'''
DEFAULT_NODE_INDICATE_COLOR = "yellow"


class Dijkstra(SectionsScene):
    def __init__(self, graph, **kwargs):
        self.graph = graph
        self.dist_mob = get_dist_labels(self.graph)
        self.graph.remove_updater(self.graph.update_edges)

        self.code = create_code(DIJKSTRA_PSEUDO_CODE, line_no_buff=0.6)
        self.heap_label, self.u, self.pi = self.create_dijkstra_vars()
        self.heap = VGroup(*[VGroup(node.copy().scale(0.7), dist.copy().scale(0.7)) for (_, node), dist in
                             zip(self.graph.vertices.items(), self.dist_mob[1:])]).arrange(RIGHT).next_to(
            self.heap_label, RIGHT)
        # self.code = Rectangle()
        self.board_width = (config.frame_width - graph.width) * 0.80
        super().__init__(**kwargs)

    def highlight_and_indicate_code(self, lines: list, **kwargs):  # TODO: implement code scene
        highlight, indicate = highlight_code_lines(self.code, lines, **kwargs)
        self.play(highlight, run_time=0.2)
        self.play(indicate, run_time=0.6)

    def create_dijkstra_vars(self) -> tuple[ArrayMob, Tex, ArrayMob]:
        scale = 1
        start_vars_y = self.code.get_bottom()[1]
        lag_y = (config.frame_height / 2 + start_vars_y) / 3
        heap_mob = ArrayMob("heap:", 1, name_scale=scale).set_y(start_vars_y - lag_y, DOWN).to_edge(
            LEFT)

        u = Tex("u:").scale_to_fit_height(heap_mob.height_ref).next_to(heap_mob, DOWN, buff=heap_mob.get_square(
            0).height * 0.8).align_to(heap_mob.array_name, RIGHT).set_y(start_vars_y - 2 * lag_y, DOWN)
        pi = ArrayMob(r"$\pi$:", *[""] * len(self.graph.vertices), name_scale=scale, show_labels=True, labels_pos=DOWN,
                      align_point=u.get_right() + 0.5 * DOWN * (heap_mob.obj_ref.get_bottom()[1] - u.get_top()[1]),
                      starting_index=1).set_y(start_vars_y - 3 * lag_y, DOWN)
        pi.shift((pi.array_name.get_right() - u.get_right())[0] * LEFT)
        u.set_y((heap_mob.get_bottom()[1] + pi.get_top()[1]) / 2)
        VGroup(heap_mob, u, pi).next_to(self.code, DOWN).to_edge(LEFT)
        heap_mob = heap_mob.array_name
        return heap_mob, u, pi


class DijkstraExample(Dijkstra):
    def __init__(self, **kwargs):
        super().__init__(get_main_graph_example(), **kwargs)

    def construct(self):
        self.next_section("Dijkstra Example", pst.NORMAL)
        self.add(self.graph, self.code, self.dist_mob)
        self.add(self.heap_label, self.u, self.pi)
        self.add(self.heap)
        # self.play(graph.vertices[3].animate.shift(LEFT * 2))
        # self.play(graph.edges[(2, 5)].animate_move_along_path(**SP_PATH_PARAMS))
        self.wait()


if __name__ == "__main__":
    scenes_lst = [DijkstraExample]

    run_scenes(scenes_lst, OUT_DIR, PRESENTATION_MODE, DISABLE_CACHING, gif_scenes=[28 + i for i in range(6)],
               create_gif=False)
