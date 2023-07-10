from __future__ import annotations

from tools.array import ArrayMob
from tools.graphs.node import IndicateNode
from tools.graphs.utils import create_graph
from tools.scenes import *
from shortes_path_utils import *

ROOT_PATH = Path(__file__).resolve().parent
sys.path.append(str(ROOT_PATH.parent))
OUT_DIR = MEDIA_PATH / Path(__file__).resolve().parent.stem

PRESENTATION_MODE = True
DISABLE_CACHING = False

# --------------------------------- constants --------------------------------- #

BELLMAN_FORD_PSEUDO_CODE = r'''def Bellman-Ford($G=\left(V,E,w\right),s$):
    Initialize-Single-Source($G,s$)
    for i in range(1,|V|):
        for each edge (u,v) ∈ E:
            Relax(u,v,$w$) # update best path
    
    for each edge (u,v) ∈ E:
        if v.d > u.d + $w$(u,v):
            return False
    return True'''

DEFAULT_NODE_INDICATE_COLOR = "yellow"

MAIN_GRAPH_VERTEX_NUM = 5
MAIN_GRAPH_EXAMPLE_VERTICES = list(range(1, MAIN_GRAPH_VERTEX_NUM + 1))
MAIN_GRAPH_EXAMPLE_EDGES = [(1, 2), (2, 3), (3, 2), (4, 3), (5, 4), (1, 5), (4, 1), (2, 5), (5, 3), (2, 4)]
MAIN_GRAPH_EXAMPLE_WEIGHTS = {(1, 2): 6, (2, 3): 5, (3, 2): -2, (4, 3): 7, (5, 4): 9, (1, 5): 7, (4, 1): 2, (2, 5): 8,
                              (5, 3): -3, (2, 4): -4}

VERTICES_SMALL_EXAMPLE = [1, 2, 3, 4]
EDGES_SMALL_EXAMPLE = [(1, 2), (3, 1), (1, 4), (2, 3), (3, 4)]
WEIGHTS_SMALL_EXAMPLE = {(1, 2): 5, (3, 1): -4, (1, 4): 9, (2, 3): -2, (3, 4): 8}


def get_main_graph_example() -> DiGraph | WeightedGraph:
    layout = change_layout(MAIN_GRAPH_VERTEX_NUM)
    add_y = 0.7
    layout[3][1] += add_y
    layout[2][1] = layout[3][1]
    layout[5][1] = layout[4][1]
    layout[1][1] += add_y / 2

    graph = create_graph(MAIN_GRAPH_EXAMPLE_VERTICES, MAIN_GRAPH_EXAMPLE_EDGES, graph_type=WeightedGraph,
                         weights=MAIN_GRAPH_EXAMPLE_WEIGHTS, directed_graph=True,
                         layout=layout).shift(1e-6 * LEFT)
    for v, node in graph.vertices.items():
        node.label.scale(0.8).next_to(node.get_top(), DOWN, buff=0.1)
    graph.edges[(2, 4)].weight_relative_position = 0.7
    graph.edges[(2, 4)].update_weight(graph.edges[(2, 4)])
    graph.edges[(5, 3)].weight_relative_position = 0.7
    graph.edges[(5, 3)].update_weight(graph.edges[(5, 3)])
    return graph


class BellmanFordIntro(SectionsScene):
    def construct(self):
        self.next_section("Belman-Ford Intro", pst.NORMAL)
        title = Title("Belman-Ford Algorithm")

        bf_input = Tex(r'''\textbf{Input}: A Directed weighted graph $G$ where $w:E\rightarrow\mathbb{R}$
                        and a source $s$.

                        \textbf{Output}: For all $v\in V$:\\
                         \ \ \ $v.d$ - the distance from $s$ to $v$.\\
                          \ \ \ $v.\pi$ - the previous node of $v$ in the path $s$ to $v$.\\
                        False if there is a negative cycle and True otherwise.''',
                       tex_environment="{minipage}{9.3cm}").match_width(title).next_to(title, DOWN,
                                                                                       buff=0.5)
        color_tex(bf_input, t2c={"s": BLUE, "v.\pi": GREEN, "v.d": ORANGE}, tex_class=MathTex)
        color_tex(bf_input, t2c={"True": ORANGE, "False": ORANGE})

        self.play(Write(title))
        self.play(Write(bf_input))

        self.next_section("Example")
        example = Text("Negative cycle example:").scale(0.6).next_to(bf_input, DOWN, buff=0.2).align_to(bf_input, LEFT)

        graph = create_graph(VERTICES_SMALL_EXAMPLE, EDGES_SMALL_EXAMPLE, graph_type=WeightedGraph,
                             weights=WEIGHTS_SMALL_EXAMPLE, directed_graph=True, absolute_scale_vertices=True,
                             layout="circular").scale(0.5).next_to(bf_input, DOWN).to_edge(DOWN, buff=0.18)
        graph.clear_updaters(recursive=True)

        for edge in graph.edges.values():
            edge.clear_updaters()

        first_example_path = [(2, 3), (3, 1)]
        first_example_anim = AnimationGroup(*[graph.edges[edge].animate_move_along_path(**SP_PATH_PARAMS) for edge in
                                              first_example_path], lag_ratio=0.5)
        next_anim = graph.edges[(1, 2)].animate_move_along_path(**SP_PATH_PARAMS)
        weight = MathTex(r"w(2\rightarrow1)=", "-6").next_to(graph, RIGHT)

        self.play(Write(example))
        self.play(Write(graph))
        self.play(Write(weight[0]))
        self.next_section("first example")
        self.play(first_example_anim)
        self.play(Write(weight[1]))

        self.next_section("dist")
        self.play(next_anim)
        new_weight_1 = MathTex("-7").match_height(weight[1]).move_to(weight[1])
        self.play(ReplacementTransform(weight[1], new_weight_1))

        self.next_section("dist")
        new_weight_2 = MathTex("-8").match_height(weight[1]).move_to(weight[1])
        self.play(ReplacementTransform(new_weight_1, new_weight_2))

        self.next_section("End")
        self.play(Unwrite(graph), Unwrite(example), Unwrite(bf_input), Unwrite(title), Unwrite(weight),
                  Unwrite(new_weight_2))
        self.wait()


class BellmanFord(SectionsScene):
    def __init__(self, graph, **kwargs):
        self.graph = graph
        self.graph.remove_updater(self.graph.update_edges)
        self.dist_mob = get_sp_dist_labels(self.graph).set_z_index(10)

        self.code = create_code(BELLMAN_FORD_PSEUDO_CODE, line_no_buff=0.6)
        self.pi = self.create_bf_vars()

        self.board_width = (config.frame_width - graph.width) * 0.80
        super().__init__(**kwargs)

    def bellman_ford(self, s: Hashable, **kwargs):
        self.next_section("Initialization")
        self.highlight_and_indicate_code([2])
        self.play(Write(self.dist_mob))
        self.set_dist(s, 0)
        edges_to_update = [(s, v) for v in get_neighbors(self.graph, s)]

        for i in range(1, len(self.graph.vertices)):
            self.next_section("Main Loop")
            self.highlight_and_indicate_code([3])
            if i <= 1:
                iteration_count = MathTex("i = ", "1", color=YELLOW).next_to(self.graph, UP, buff=0.5)
                self.play(Write(iteration_count))
            else:
                self.play(ReplacementTransform(iteration_count[1],
                                               MathTex(str(i), color=YELLOW).match_height(iteration_count[1]).move_to(
                                                   iteration_count[1])))
            relax_back_edges = {edge: get_background_edge(self.graph, *edge) for edge in edges_to_update}

            edges_to_update = []
            self.next_section("Relaxation")
            self.highlight_and_indicate_code([4, 5])
            self.play(*[Write(edge) for edge in relax_back_edges.values()])
            for edge, back_edge in relax_back_edges.items():
                self.next_section(f"Relaxation of {edge}")
                if self.relax(*edge, back_edge):
                    edges_to_update += [(edge[1], v) for v in get_neighbors(self.graph, edge[1])]

        self.play(Unwrite(iteration_count))

    def relax(self, u: Hashable, v: Hashable, relax_edge: VMobject, **kwargs) -> bool:
        v_dist = self.dist_mob[v]
        v_dist_val = self.get_dist_val(v_dist)
        u_dist = self.dist_mob[u]
        u_dist_val = self.get_dist_val(u_dist)
        cur_edge = self.graph.edges[(u, v)]
        weight = cur_edge.weight
        ret = False

        if v_dist_val > u_dist_val + weight:
            self.set_dist(v, u_dist_val + weight)
            self.next_section("Update π")
            if self.pi.get_square(v - 1)[2].tex_string != "":
                self.play(self.graph.edges[(int(self.pi[v][2].tex_string), v)].animate_move_along_path(
                    **SP_RELAX_PATH_PARAMS))
            self.play(self.graph.edges[(u, v)].animate_move_along_path(**SP_PATH_PARAMS))
            self.play(self.pi.at(v - 1, u))
            ret = True

        self.play(Unwrite(relax_edge))
        return ret

    def highlight_and_indicate_code(self, lines: list, **kwargs):  # TODO: implement code scene
        highlight, indicate = highlight_code_lines(self.code, lines, **kwargs)
        self.play(highlight, run_time=0.2)
        self.play(indicate, run_time=0.6)

    def create_bf_vars(self) -> ArrayMob:
        scale = 1
        start_vars_y = self.code.get_bottom()[1]
        lag_y = (config.frame_height / 4 + start_vars_y)

        pi = ArrayMob(r"$\pi$:", *[""] * len(self.graph.vertices), name_scale=scale, show_labels=True, labels_pos=DOWN,
                      starting_index=1).scale(1.6).set_y(start_vars_y - lag_y, DOWN).to_edge(LEFT)
        return pi

    def set_dist(self, v: Hashable, dist: float, **kwargs):
        self.play(ReplacementTransform(self.dist_mob[v],
                                       get_sp_dist_label(self.graph, v, dist).move_to(self.dist_mob[v])),
                  Flash(self.graph[v], flash_radius=0.5), **kwargs)

    def get_dist_val(self, dist: MathTex) -> int:
        dist = dist.tex_string
        return np.Inf if "infty" in dist else int(re.findall(r"[-+]?\d*\.\d+|\d+", dist)[-1])


class BellmanFordExample(BellmanFord):
    def __init__(self, **kwargs):
        super().__init__(get_main_graph_example(), **kwargs)

    def construct(self):
        self.next_section("Bellman-Ford Example", pst.NORMAL)
        self.play(Write(self.code), Write(self.graph))
        self.play(Write(self.pi))
        self.bellman_ford(1)
        self.next_section("End")
        self.play(Unwrite(self.pi), Unwrite(self.dist_mob))
        self.play(AnimationGroup(
            *[edge.animate_move_along_path(**SP_RELAX_PATH_PARAMS) for edge in self.graph.edges.values()]))
        self.highlight_and_indicate_code(list(range(2, 11)))
        self.wait()


class BellmanFordComplexity(BellmanFord):
    def __init__(self, **kwargs):
        super().__init__(get_main_graph_example(), **kwargs)

    def construct(self):
        self.add(self.graph, self.code)
        self.graph.clear_updaters(recursive=True)
        for edge in self.graph.edges.values():
            edge.clear_updaters()
        self.next_section("Bellman-Ford Complexity", pst.NORMAL)
        self.highlight_and_indicate_code([3, 4])
        self.next_section("Complexity")
        total_complexity = MathTex(r"O\left(\left|E\right|\left|V\right|\right)").scale(1.5).move_to(self.pi)
        self.play(Write(total_complexity))

        self.next_section("end")
        self.play(Unwrite(total_complexity), Unwrite(self.code), Unwrite(self.graph))
        self.wait()


if __name__ == "__main__":
    scenes_lst = [BellmanFordIntro, BellmanFordExample, BellmanFordComplexity]

    run_scenes(scenes_lst, OUT_DIR, PRESENTATION_MODE, DISABLE_CACHING, gif_scenes=[28 + i for i in range(6)],
               create_gif=False)
