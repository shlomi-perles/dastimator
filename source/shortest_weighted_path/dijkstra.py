from __future__ import annotations

from tools.array import ArrayMob
from tools.graphs.node import IndicateNode
from tools.graphs.utils import create_graph
from tools.movie_maker import render_scenes
from tools.scenes import *
from shortest_weighted_path.shortes_path_utils import *

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
    if u.d + w(u,v) < v.d:
        v.d = u.d + w(u,v)
        v.π = u
        Decrease-Key(Q,v,v.d)'''
DEFAULT_NODE_INDICATE_COLOR = "yellow"

MAIN_GRAPH_VERTEX_NUM = 5
MAIN_GRAPH_EXAMPLE_VERTICES = list(range(1, MAIN_GRAPH_VERTEX_NUM + 1))
MAIN_GRAPH_EXAMPLE_EDGES = [(1, 2), (2, 3), (3, 4), (4, 3), (5, 4), (1, 5), (4, 1), (2, 5), (5, 2), (5, 3)]
MAIN_GRAPH_EXAMPLE_WEIGHTS = {(1, 2): 10, (2, 3): 1, (3, 4): 4, (4, 3): 6, (5, 4): 2, (1, 5): 5, (4, 1): 7, (2, 5): 2,
                              (5, 2): 3, (5, 3): 9}

VERTICES_SMALL_EXAMPLE = [1, 2, 3, 4]
EDGES_SMALL_EXAMPLE = [(1, 2), (3, 1), (1, 4), (2, 3), (3, 4)]
WEIGHTS_SMALL_EXAMPLE = {(1, 2): 7, (3, 1): -4, (1, 4): 9, (2, 3): -2, (3, 4): 8}


def get_main_graph_example() -> DiGraph | WeightedGraph:
    layout = change_layout(MAIN_GRAPH_VERTEX_NUM)
    add_y = 0.7
    layout[3][1] += add_y
    layout[2][1] = layout[3][1]
    layout[5][1] = layout[4][1]
    layout[1][1] += add_y / 2

    graph = create_graph(MAIN_GRAPH_EXAMPLE_VERTICES, MAIN_GRAPH_EXAMPLE_EDGES, layout=layout, directed_graph=True,
                         graph_type=WeightedGraph, weights=MAIN_GRAPH_EXAMPLE_WEIGHTS, rescale_vertices=False).shift(
        1e-6 * LEFT)
    for v, node in graph.vertices.items():
        node.label.scale(0.5).next_to(node.get_top(), DOWN, buff=0.1)
    return graph


class Intro(SectionsScene):
    def construct(self):
        self.next_section("Intro", pst.NORMAL)
        title = Title("Shortest Path in a Weighted Graph")
        overview = Tex(r'''Overview:
            \begin{itemize}
                \item[$\bullet$] Dijkstra Algorithm - $O\left(\left(\left|E\right|+\left|V\right|\right)\log\left|V\right|\right)$
                \begin{itemize}
                \item weight function: $w: E \rightarrow \mathbb{R}^+$ (non-negative)
                \end{itemize}
                \item[$\bullet$] Bellman-Ford Algorithm - $O\left(\left|V\right|\left|E\right|\right)$
                \begin{itemize}
                \item weight function: $w: E \rightarrow \mathbb{R}$
                \end{itemize}
            \end{itemize}''', tex_environment=r"{minipage}{9.3cm}")
        color_tex(overview, t2c={"Dijkstra": YELLOW, "Bellman-Ford": YELLOW})
        remark = Text(r"Remark: Today's graphs are all directed and weighted.",
                      t2w={"directed": BOLD, "weighted": BOLD},
                      t2c={
                          "directed": BLUE, "weighted": BLUE})
        remark.match_width(overview).to_edge(DOWN)

        self.play(Write(title))
        self.play(Write(overview))
        self.next_section("remark")
        self.play(Write(remark))
        self.next_section("End")
        self.play(Unwrite(title), Unwrite(overview), Unwrite(remark))
        self.wait()


class ShortestPath(SectionsScene):
    def construct(self):
        self.next_section("Shortest Path", pst.NORMAL)
        title = Title("Shortest Path")

        definition = Tex(r'''The \textbf{distance} from u to v is denote as: 
                        \[
                        \delta(u,v)=\min\left\{ w(\text{path})\middle|\text{path}:u\text{ to }v\right\} 
                        \]''', tex_environment=DEFINITION_TEX_ENV).next_to(title, DOWN, buff=0.5)
        color_tex(definition, t2c={r"\textbf{distance}": YELLOW})
        self.play(Write(title))
        self.play(Write(definition))

        self.next_section("Example")
        example = Text("Example:").next_to(definition, DOWN, buff=0.5).align_to(definition, LEFT)

        graph = create_graph(VERTICES_SMALL_EXAMPLE, EDGES_SMALL_EXAMPLE, layout="circular", directed_graph=True,
                             graph_type=WeightedGraph, rescale_vertices=False,
                             weights=WEIGHTS_SMALL_EXAMPLE).scale(0.7).next_to(definition, DOWN).to_edge(DOWN)
        graph.clear_updaters(recursive=True)
        for edge in graph.edges.values():
            edge.clear_updaters()

        delta_1 = MathTex(r"\delta(2,4)=", "3").next_to(graph, RIGHT, buff=0.5)
        delta_1_path = [(2, 3), (3, 1), (1, 4)]
        delta_1_anim = AnimationGroup(*[graph.edges[edge].animate_move_along_path(**SP_PATH_PARAMS) for edge in
                                        delta_1_path], lag_ratio=0.5)

        delta_2 = MathTex(r"\delta(4,2)=", "\infty").next_to(delta_1, DOWN, buff=0.5).align_to(delta_1, LEFT)

        self.play(Write(example))
        self.play(Write(graph))
        self.play(Write(delta_1[0]))
        self.next_section("delat 1")
        self.play(delta_1_anim)
        self.play(Write(delta_1[1]))

        self.next_section("delta 2")
        self.play(Write(delta_2[0]))
        self.next_section("show infty")
        self.play(Write(delta_2[1]))

        self.next_section("End")
        self.play(Unwrite(graph), Unwrite(example), Unwrite(delta_1), Unwrite(delta_2), Unwrite(title),
                  Unwrite(definition))
        self.wait()


class DijkstraIntro(SectionsScene):
    def construct(self):
        self.next_section("Dijkstra Intro", pst.NORMAL)
        title = Title("Dijkstra Algorithm")

        dijk_input = Tex(r'''\textbf{Input}: A Directed weighted graph $G$ where $w:E\rightarrow\mathbb{R}^{+}$
                        (\textbf{non-negative} edge weight) and a source $s$.
                        
                        \textbf{Output}: For all $v\in V$:\\
                         \ \ \ $v.d$ - the distance from $s$ to $v$.\\
                          \ \ \ $v.\pi$ - the previous node of $v$ in the path $s$ to $v$.''',
                         tex_environment="{minipage}{9.3cm}").match_width(title).next_to(title, DOWN,
                                                                                         buff=0.5)
        color_tex(dijk_input, t2c={"s": BLUE, "v.\pi": GREEN, "v.d": ORANGE}, tex_class=MathTex)

        self.play(Write(title))
        self.play(Write(dijk_input))

        self.next_section("Example")
        example = Text("Example:").scale(0.8).next_to(dijk_input, DOWN, buff=0.2).align_to(dijk_input, LEFT)
        weights = {(1, 2): 7, (3, 1): 2, (1, 4): 4, (2, 3): 1, (3, 4): 8}
        graph = create_graph(VERTICES_SMALL_EXAMPLE, EDGES_SMALL_EXAMPLE, layout="circular", directed_graph=True,
                             graph_type=WeightedGraph, rescale_vertices=False,
                             weights=weights).scale(0.55).next_to(dijk_input, DOWN).to_edge(DOWN, buff=0.18).shift(
            RIGHT * 1.8)
        graph.clear_updaters(recursive=True)

        for edge in graph.edges.values():
            edge.clear_updaters()

        first_example = get_func_text("Dijkstra(G, 2)").match_height(example).next_to(example, RIGHT, buff=0.5)
        first_example_path = [(2, 3), (3, 1), (1, 4)]
        first_example_anim = AnimationGroup(*[graph.edges[edge].animate_move_along_path(**SP_PATH_PARAMS) for edge in
                                              first_example_path], lag_ratio=0.5)
        first_example_dist = VGroup(get_sp_dist_label(graph, 1, 3), get_sp_dist_label(graph, 2, 0),
                                    get_sp_dist_label(graph, 3, 1), get_sp_dist_label(graph, 4, 7))
        for i, label in enumerate(first_example_dist):
            label.move_to(graph.vertices[i + 1])

        for v, node in graph.vertices.items():
            node.label.scale(0.8).next_to(node, UP, buff=0.1)
        graph.vertices[2].label.next_to(graph.vertices[2], DOWN, buff=0.1)

        self.play(Write(example))
        self.play(Write(graph))
        self.play(Write(first_example))
        self.next_section("first example")
        self.play(first_example_anim)
        self.next_section("dist")
        self.play(Write(first_example_dist))

        self.next_section("End")
        self.play(Unwrite(graph), Unwrite(example), Unwrite(first_example), Unwrite(first_example_dist),
                  Unwrite(title), Unwrite(dijk_input))
        self.wait()


class Relax(SectionsScene):
    def construct(self):
        self.next_section("Relax", pst.NORMAL)
        title = Title("Vertex Relaxation")
        code = create_code(RELAX_PSEUDO_CODE).next_to(title, DOWN, buff=0.5)

        graph = create_graph(["v", "u"], [("u", "v")], layout="circular", directed_graph=True, graph_type=WeightedGraph,
                             rescale_vertices=False, weights={("u", "v"): 2}).scale(0.7).next_to(code, DOWN, buff=0.9)
        graph.clear_updaters(recursive=True)

        for edge in graph.edges.values():
            edge.clear_updaters()

        u_dist = get_sp_dist_label(graph, "u", 5).move_to(graph.vertices["u"])
        v_dist_1 = get_sp_dist_label(graph, "v", 9).move_to(graph.vertices["v"])
        v_dist_update = get_sp_dist_label(graph, "v", 7).move_to(graph.vertices["v"])
        v_dist_2 = get_sp_dist_label(graph, "v", 6).move_to(graph.vertices["v"])
        for v, node in graph.vertices.items():
            node.label.scale(0.8).next_to(node, UP, buff=0.1)

        self.play(Write(title))
        self.play(Write(code))

        relax_1 = get_func_text("Relax(u,v,w)").next_to(graph, DOWN, buff=0.5)
        self.next_section("relax")
        self.play(Write(graph), Write(u_dist), Write(v_dist_1))
        self.play(Write(relax_1))

        graph.set_z_index(-10)
        v_dist_1.set_z_index(10)
        v_dist_update.set_z_index(10)
        self.next_section("relax update")
        back_edge = get_background_edge(graph, "u", "v").set_z_index(-20)
        self.play(Write(back_edge))
        self.next_section("relax update")
        self.play(ReplacementTransform(v_dist_1, v_dist_update), Flash(v_dist_1))
        self.play(graph.edges[("u", "v")].animate_move_along_path(**SP_PATH_PARAMS))
        self.next_section("relax update")
        self.play(Unwrite(back_edge))
        self.next_section(" end")
        self.play(Unwrite(graph), Unwrite(u_dist), Unwrite(v_dist_update), Unwrite(relax_1), Unwrite(title),
                  Unwrite(code))

        self.wait()


class Dijkstra(SectionsScene):
    def __init__(self, graph, **kwargs):
        self.graph = graph
        self.graph.remove_updater(self.graph.update_edges)
        self.dist_mob = get_sp_dist_labels(self.graph).set_z_index(10)

        self.code = create_code(DIJKSTRA_PSEUDO_CODE, line_no_buff=0.6)
        self.heap_label, self.u, self.pi = self.create_dijkstra_vars()
        self.min_heap = VGroup(*[VGroup(node.copy().scale(0.7), dist.copy().scale(0.7)) for (_, node), dist in
                                 zip(self.graph.vertices.items(), self.dist_mob[1:])]).arrange(RIGHT).next_to(
            self.heap_label, RIGHT)
        self.board_width = (config.frame_width - graph.width) * 0.80
        super().__init__(**kwargs)

    def dijksra(self, s: Hashable, **kwargs):
        self.next_section("Initialization")
        self.highlight_and_indicate_code([2, 3])
        self.play(Write(self.dist_mob))
        self.play(Write(self.min_heap))
        self.decrease_key(s, 0)

        while len(self.min_heap) > 0:
            self.next_section("Main Loop")
            self.highlight_and_indicate_code([5, 6])
            u = self.pop_min_to_u()
            u_val = int(u[0].key.tex_string)

            self.next_section(f"Relaxation of {u_val}")
            self.highlight_and_indicate_code([7, 8])
            neighbors_back_edges_dict = get_neighbors_background(self.graph, u_val)
            self.play(*[Write(edge) for edge in neighbors_back_edges_dict.values()])

            for v in get_neighbors(self.graph, u_val):
                self.next_section(f"Relaxation of {u_val} to {v}")
                self.relax(u_val, v, neighbors_back_edges_dict[v])

            self.play(u[0].animate.set_stroke(color=VERTEX_STROKE_COLOR),
                      self.graph.vertices[u_val].animate.set_stroke(color=VISITED_COLOR))
            self.play(FadeOut(u, shift=RIGHT))

    def relax(self, u: Hashable, v: Hashable, relax_edge: VMobject, **kwargs):
        v_dist = self.dist_mob[v]
        v_dist_val = self.get_dist_val(v_dist)
        u_dist = self.dist_mob[u]
        u_dist_val = self.get_dist_val(u_dist)
        cur_edge = self.graph.edges[(u, v)]
        weight = cur_edge.weight

        if v_dist_val > u_dist_val + weight:
            self.decrease_key(v, u_dist_val + weight)
            self.next_section("Update π")
            if self.pi.get_entry(v).value != "":
                self.play(self.graph.edges[(int(self.pi.get_entry(v).value), v)].animate_move_along_path(
                    **SP_RELAX_PATH_PARAMS))
            self.play(self.graph.edges[(u, v)].animate_move_along_path(**SP_PATH_PARAMS))
            self.play(self.pi.animate.at(v, u))

        self.play(Unwrite(relax_edge))

    def pop_min_to_u(self, **kwargs) -> VGroup:
        min_vertex = self.min_heap[0]
        anims = [min_vertex.animate.match_y(self.u)]
        if len(self.min_heap) > 1:
            anims += [self.min_heap[i].animate.move_to(self.min_heap[i - 1]) for i in range(1, len(self.min_heap))]
        self.min_heap.remove(min_vertex)
        self.play(AnimationGroup(*anims), **kwargs)
        min_vertex[0].set_stroke(color=YELLOW)
        self.graph.vertices[int(min_vertex[0].key.tex_string)].set_stroke(color=YELLOW)
        self.play(IndicateNode(min_vertex[0], color_theme=DEFAULT_NODE_INDICATE_COLOR),
                  IndicateNode(self.graph.vertices[int(min_vertex[0].key.tex_string)],
                               color_theme=DEFAULT_NODE_INDICATE_COLOR))
        return min_vertex

    def highlight_and_indicate_code(self, lines: list, **kwargs):  # TODO: implement code scene
        highlight, indicate = highlight_code_lines(self.code, lines, **kwargs)
        self.play(highlight, run_time=0.2)
        self.play(indicate, run_time=0.6)

    def create_dijkstra_vars(self) -> tuple[ArrayMob, Tex, ArrayMob]:
        scale = 1
        arr_scale = 0.38
        start_vars_y = self.code.get_bottom()[1]
        lag_y = (config.frame_height / 2 + start_vars_y) / 3
        heap_mob = ArrayMob("min-heap:", 1, name_scale=scale).scale(arr_scale).set_y(start_vars_y - lag_y,
                                                                                     DOWN).to_edge(LEFT)

        u = Tex("u:").match_height(heap_mob.obj_ref).next_to(heap_mob, DOWN, buff=heap_mob.get_entry(
            0).height * 0.8).align_to(heap_mob.name_mob, RIGHT).set_y(start_vars_y - 2 * lag_y, DOWN)
        pi = ArrayMob(r"$\pi$:", *[""] * len(self.graph.vertices), name_scale=scale, show_indices=True,
                      indices_pos=DOWN, starting_index=1).scale(arr_scale).set_y(start_vars_y - 3 * lag_y, DOWN)
        pi.shift((heap_mob.entries.get_left()[0] - pi.entries.get_left()[0]) * RIGHT)
        u.set_y((heap_mob.get_bottom()[1] + pi.get_top()[1]) / 2)
        VGroup(heap_mob, u, pi).next_to(self.code, DOWN).to_edge(LEFT)
        heap_mob = heap_mob.name_mob
        return heap_mob, u, pi

    def find_in_heap(self, v: Hashable) -> VGroup:
        for vertex in self.min_heap:
            if str(vertex[0].key.tex_string) == str(v):
                return vertex

    def decrease_key(self, v: Hashable, key: float, **kwargs):
        vertex = self.find_in_heap(v)
        vertex[0].set_z_index(-10)
        new_label = create_dist_label(v, self.graph, key).move_to(vertex[1]).set_z_index(10).scale_to_fit_height(
            vertex[0].height * 0.3)

        self.play(ReplacementTransform(vertex[1], new_label), Flash(new_label),
                  ReplacementTransform(self.dist_mob[v],
                                       get_sp_dist_label(self.graph, v, key).move_to(self.dist_mob[v])),
                  Flash(self.graph[v], flash_radius=0.5), **kwargs)

        self.sort_heap(**kwargs)

    def sort_heap(self, **kwargs):
        prev_loc = [vertex for vertex in self.min_heap]
        self.min_heap.sort(submob_func=lambda x: self.get_dist_val(x[1]))
        anims = [edge.animate.move_to(prev_loc[i]) for i, edge in enumerate(self.min_heap)]
        if len(anims) > 0:
            self.play(*anims, **kwargs)

    def get_dist_val(self, dist: MathTex) -> int:
        dist = dist.tex_string
        return np.Inf if "infty" in dist else int(re.findall(r"[-+]?\d*\.\d+|\d+", dist)[-1])


class DijkstraExample(Dijkstra):
    def __init__(self, **kwargs):
        super().__init__(get_main_graph_example(), **kwargs)

    def construct(self):
        self.next_section("Dijkstra Example", pst.NORMAL)
        self.play(Write(self.code), Write(self.graph))
        self.play(Write(self.heap_label), Write(self.u), Write(self.pi))

        self.dijksra(1)

        self.next_section("End")
        self.play(Unwrite(self.min_heap), Unwrite(self.u), Unwrite(self.pi), Unwrite(self.heap_label),
                  Unwrite(self.dist_mob))
        self.play(AnimationGroup(
            *[edge.animate_move_along_path(**SP_RELAX_PATH_PARAMS) for edge in self.graph.edges.values()]),
            AnimationGroup(
                *[vertex.animate.set_stroke(color=VERTEX_STROKE_COLOR) for vertex in self.graph.vertices.values()]))
        self.highlight_and_indicate_code(list(range(2, 9)))
        self.wait()


class DijkstraComplexity(Dijkstra):
    def __init__(self, **kwargs):
        super().__init__(get_main_graph_example(), **kwargs)

    def construct(self):
        self.add(self.graph, self.code)
        self.graph.clear_updaters(recursive=True)
        for edge in self.graph.edges.values():
            edge.clear_updaters()
        self.next_section("Dijkstra Complexity", pst.NORMAL)
        total_complexity = MathTex(r"O(\left(\left|E\right|+\left|V\right|\right)", r"\log\left|V\right|)").next_to(
            self.code, DOWN, buff=3).match_y(self.u).match_width(self.code)
        self.highlight_and_indicate_code([5, 7])
        self.play(Write(total_complexity[0]))

        self.next_section("heap")
        self.highlight_and_indicate_code([6, 8])
        self.next_section("total complexity")
        self.play(Write(total_complexity[1:]))
        self.highlight_and_indicate_code([5, 6, 7, 8])
        self.next_section("end")
        self.play(Unwrite(total_complexity), Unwrite(self.code), Unwrite(self.graph))
        self.wait()


if __name__ == "__main__":
    scenes_lst = [Intro, ShortestPath, DijkstraIntro, Relax, DijkstraExample, DijkstraComplexity]

    render_scenes(scenes_lst, OUT_DIR, PRESENTATION_MODE, DISABLE_CACHING, gif_scenes=[18 + i for i in range(5)],
                  create_gif=False)
