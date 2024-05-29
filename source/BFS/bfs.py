from __future__ import annotations

from copy import copy
from typing import Hashable

from tools.graphs.utils import get_neighbors, create_dist_label, create_graph
from tools.movie_maker import render_scenes
from tools.scenes import *
from tools.array import *
from tools.consts import *
from tools.funcs import *
from tools.graphs.my_graphs import DiGraph

ROOT_PATH = Path(__file__).resolve().parent
sys.path.append(str(ROOT_PATH.parent))
OUT_DIR = MEDIA_PATH / Path(__file__).resolve().parent.stem

PRESENTATION_MODE = True
DISABLE_CACHING = False

# --------------------------------- constants --------------------------------- #
EDGE_COLOR = GREY
EDGE_CONFIG["stroke_color"] = EDGE_COLOR

BFS_PSEUDO_CODE = '''def BFS(G,s): 
    queue ← Build Queue({s})
    for each vertex u in V do:
        dist[u] ← ∞
    dist[s] ← 0
    π[s] ← None

    while queue ≠ ø do:
        u = queue.pop(0) 
        for neighbor v of u & dist[v] = ∞:
                queue.push(v)
                dist[v] = dist[u] + 1
                π[v] = u'''

SIMPLE_GRAPH_LAYOUT = {1: ORIGIN, 2: DOWN, 3: LEFT, 4: LEFT + DOWN}


# --------------------------------- functions --------------------------------- #

def get_big_triangle_graph(floors: int = 5) -> tuple[list[int], list[tuple[int, int]], dict[int, np.ndarray]]:
    left_shift = LEFT / np.sqrt(3)
    cur_left = copy(ORIGIN)
    cur_vertex = 0
    vertices = []
    edges = []
    layout = {}
    for i in range(floors):
        for j in range(i + 1):
            vertices.append(cur_vertex)
            layout[cur_vertex] = cur_left - 2 * j * left_shift + i * DOWN
            if i > 0:
                if j > 0:
                    edges.append((cur_vertex, cur_vertex - i - 1))
                if j < i:
                    edges.append((cur_vertex, cur_vertex - i))
                    edges.append((cur_vertex, cur_vertex + 1))
            cur_vertex += 1
        cur_left += left_shift
    return vertices, edges, layout


# --------------------------------- scenes --------------------------------- #

class BFSScene(SectionsScene):
    def __init__(self, vertices: list[Hashable], edges: list[tuple[Hashable, Hashable]], start_vertex=1,
                 directed_graph: bool = False, layout: str | dict = "circular", **kwargs):
        super().__init__(**kwargs)
        self.directed_graph = directed_graph
        self.vertices = vertices
        self.edges = edges
        self.start_vertex = start_vertex
        self.layout = layout
        self.graph = create_graph(self.vertices, self.edges, self.layout, directed_graph=directed_graph,
                                  graph_type=DiGraph, labels=True)

        self.rendered_code = create_code(BFS_PSEUDO_CODE)
        self.queue_mob, self.u, self.pi = self.create_bfs_vars(self.rendered_code)
        self.dist_mob = VGroup(
            *([VMobject()] + [create_dist_label(i, self.graph, r"\infty") for i in self.vertices]))  # 1-indexed
        self.mobjects_garbage_collector = VGroup(*[mob for mob in self.dist_mob])

    def animate_bfs(self):
        """
        Animate BFS algorithm. We assume that the graph is connected.
        Else, we need to run BFS for each connected component.
        Each step of the algorithm is animated separately.
        Note: vertices are 1-indexed.
        """
        graph, rendered_code, dist_mob = self.graph, self.rendered_code, self.dist_mob
        queue_mob, u, pi = self.queue_mob, self.u, self.pi

        queue = [self.start_vertex]
        self.next_section("Initialize queue")
        self.highlight_and_indicate_code([2])
        self.play(Write(queue_mob))

        dist = [np.Inf] * (len(graph.vertices) + 1)
        self.next_section("Initialize dist")
        self.highlight_and_indicate_code([3, 4])
        self.play(AnimationGroup(*[anim(dist_mob[i]) for i in range(1, len(dist_mob)) for anim in [Write, Flash]],
                                 lag_ratio=0.3))

        dist[self.start_vertex] = 0
        self.next_section("Init first vertex dist")
        self.highlight_and_indicate_code([5])
        self.wait(0.2)
        self.play(self.change_dist(self.start_vertex, 0))

        parent = [None] * (len(graph.vertices) + 1)
        self.next_section("Init first vertex parent")
        self.highlight_and_indicate_code([6])
        self.play(Write(pi))
        self.play(pi.animate.at(1, "-"))
        visit_all = False

        while queue:
            self.highlight_and_indicate_code([8])
            # animate pop
            cur_vertex = queue.pop(0)
            if cur_vertex == self.start_vertex:
                self.play(Write(u))
            if not visit_all: self.next_section(f"Pop vertex {cur_vertex} from queue")
            self.highlight_and_indicate_code([9])
            if cur_vertex == self.start_vertex:
                self.visit_vertex_animation(graph, None, cur_vertex)
            pop_item = queue_mob.get_entry(0)
            self.play(queue_mob.indicate_at(0))
            self.play(pop_item.animate.match_y(u))
            pop_animation = queue_mob.pop(0, shift=RIGHT).animations
            self.play(AnimationGroup(*pop_animation[1:]))

            for neighbor in get_neighbors(graph, cur_vertex):
                if dist[neighbor] != np.Inf:
                    continue
                # animate for neighbor v of u & dist[v] = ∞
                self.next_section("Visit neighbor")
                self.highlight_and_indicate_code([10])
                self.next_section("Update visit")
                self.visit_vertex_animation(graph, cur_vertex, neighbor)

                # animate queue.push(v)
                queue.append(neighbor)
                self.next_section(f"Add vertex {neighbor} to queue")
                self.highlight_and_indicate_code([11])
                self.play(queue_mob.push(neighbor))

                # animate dist[v] = dist[u] + 1
                dist[neighbor] = dist[cur_vertex] + 1
                self.next_section(f"Set distance {dist[cur_vertex] + 1} to vertex {neighbor}")
                self.highlight_and_indicate_code([12])
                self.next_section("Update dist")
                self.play(self.change_dist(neighbor, dist[neighbor]))

                if np.Inf not in dist:
                    visit_all = True

                # animate π[v] ← u
                parent[neighbor] = cur_vertex
                self.next_section(f"Add parent {cur_vertex} to vertex {neighbor}")
                self.highlight_and_indicate_code([13])
                self.next_section("Update parent")
                self.play(pi.animate.at(neighbor, cur_vertex))
            self.play(pop_animation[0])

    def create_bfs_vars(self, rendered_code: Code) -> tuple[ArrayMob, Tex, ArrayMob]:
        scale = 1
        arr_scale = 0.38
        start_vars_y = rendered_code.get_bottom()[1]
        lag_y = (config.frame_height / 2 + start_vars_y) / 3
        queue_mob = ArrayMob("queue:", self.start_vertex, name_scale=scale).scale(arr_scale).set_y(start_vars_y - lag_y,
                                                                                                   DOWN).to_edge(LEFT)

        u = Tex("u:").match_height(queue_mob.obj_ref).next_to(queue_mob, DOWN, buff=queue_mob.get_entry(
            0).height * 0.8).align_to(queue_mob.name_mob, RIGHT).set_y(start_vars_y - 2 * lag_y, DOWN)
        pi = ArrayMob(r"$\pi$:", *[""] * len(self.vertices), name_scale=scale, show_indices=True, indices_pos=DOWN,
                      starting_index=1).scale(arr_scale).set_y(start_vars_y - 3 * lag_y, DOWN)
        pi.shift((queue_mob.entries.get_left()[0] - pi.entries.get_left()[0]) * RIGHT)
        u.set_y((queue_mob.get_bottom()[1] + pi.get_top()[1]) / 2)
        VGroup(queue_mob, u, pi).next_to(rendered_code, DOWN).to_edge(LEFT)
        return queue_mob, u, pi

    def visit_vertex_animation(self, graph: DiGraph, parent, next_vertex):
        visited_mark = Circle(radius=graph[next_vertex].radius * 0.9, fill_opacity=0, stroke_width=VISITED_VERTEX_WIDTH,
                              stroke_color=VISITED_COLOR, z_index=10).move_to(graph[next_vertex]).scale_to_fit_height(
            graph[next_vertex].height)
        self.mobjects_garbage_collector += visited_mark
        if parent is not None:
            visited_mark.rotate(graph.edges[(parent, next_vertex)].get_angle() + PI)
            self.play(graph.animate.add_edges((parent, next_vertex),
                                              edge_config={"stroke_color": VISITED_COLOR,
                                                           "stroke_width": VISITED_EDGE_WIDTH,
                                                           "tip_config": {
                                                               "tip_length": VISITED_TIP_SIZE if self.directed_graph else 0,
                                                               "tip_width": VISITED_TIP_SIZE if self.directed_graph else 0}}))
        self.play(Create(visited_mark))

    def change_dist(self, index: int, new_dist: int) -> AnimationGroup:
        old_dist = self.dist_mob[index]
        new_dist_tex = create_dist_label(index, self.graph, str(new_dist))
        # self.mobjects_garbage_collector += new_dist_tex
        self.dist_mob[index] = new_dist_tex
        return AnimationGroup(old_dist.animate.become(new_dist_tex), Flash(new_dist_tex), lag_ratio=0.5)

    def highlight_and_indicate_code(self, lines: list, **kwargs):
        highlight, indicate = highlight_code_lines(self.rendered_code, lines, **kwargs)
        self.play(highlight)
        self.play(indicate)


class DirectedGraphBFS(BFSScene):
    def __init__(self, **kwargs):
        vertices = list(range(1, 8))
        edges = [(1, 2), (1, 3),
                 (2, 3), (2, 4), (2, 5), (3, 6), (3, 7),
                 (5, 4), (5, 1), (6, 1), (6, 7)]
        start_vertex = 1
        vertices_locations = {1: UP * 2, 2: LEFT + UP, 3: RIGHT + UP, 4: 1.5 * LEFT, 5: 0.5 * LEFT, 6: 0.5 * RIGHT,
                              7: 1.5 * RIGHT}
        super().__init__(vertices, edges, start_vertex, layout=vertices_locations, directed_graph=True,
                         **kwargs)

    def construct(self):
        self.next_section("BFS Example", pst.NORMAL)
        self.play(Write(self.rendered_code))
        self.play(Write(self.graph))
        self.graph.set_z_index(-5)
        self.animate_bfs()

        self.play(highlight_code_lines(self.rendered_code, indicate=False))
        self.next_section("BFS finished")
        self.play(Unwrite(self.mobjects_garbage_collector))
        self.play(Unwrite(VGroup(self.queue_mob, self.u, self.pi)))
        self.wait()


class BFSComplexity(BFSScene):
    # TODO: next time unwrite graph from DirectedGraphBFS, add the ajacency_list_representation and bold the vertices
    #  at O(V) and the eighbors at O(E)
    def __init__(self, **kwargs):
        vertices = list(range(1, 8))
        edges = [(1, 2), (1, 3),
                 (2, 3), (2, 4), (2, 5), (3, 6), (3, 7),
                 (5, 4), (5, 1), (6, 1), (6, 7)]
        start_vertex = 1
        vertices_locations = {1: UP * 2, 2: LEFT + UP, 3: RIGHT + UP, 4: 1.5 * LEFT, 5: 0.5 * LEFT, 6: 0.5 * RIGHT,
                              7: 1.5 * RIGHT}
        super().__init__(vertices, edges, start_vertex, layout=vertices_locations, directed_graph=True,
                         **kwargs)

    def construct(self):
        self.next_section("BFS Complexity", pst.NORMAL)
        self.add(self.rendered_code, self.graph)
        self.highlight_and_indicate_code([8])
        complex_v = Tex(r"$O(|V|)$").next_to(self.rendered_code, DOWN, buff=2.3).to_edge(LEFT)
        self.next_section("BFS v")
        self.play(Write(complex_v))
        self.next_section("BFS e")
        self.highlight_and_indicate_code([10])
        complex_e = Tex(r" + $O(|E|)$").next_to(complex_v, RIGHT, buff=0.3)
        self.play(Write(complex_e))
        self.next_section("BFS v + e")
        total = Tex(r" = $O\left(\left|E\right|+\left|V\right|\right)$").next_to(complex_e, RIGHT, buff=0.3)
        self.play(Write(total))
        self.next_section("done")
        self.play(Unwrite(complex_v), Unwrite(complex_e), Unwrite(total))
        self.play(Unwrite(self.rendered_code), Unwrite(self.graph))
        self.wait()


class FastBFS(SectionsScene):
    def __init__(self, vertices, edges, layout, directed_graph=False, start_vertex=0, **kwargs):
        super().__init__(**kwargs)
        self.directed_graph = directed_graph
        self.vertices = vertices
        self.edges = edges
        self.start_vertex = start_vertex
        self.layout = layout
        self.graph = create_graph(self.vertices, self.edges, self.layout, directed_graph=directed_graph,
                                  graph_type=DiGraph, vertex_type=Dot, rescale_vertices=False,
                                  labels=False).scale_to_fit_height(config.frame_height * 0.9).move_to(ORIGIN)
        self.graph.remove_updater(self.graph.update_edges)
        self.mobjects_garbage_collector = VGroup()

    def animate_fast_bfs(self, run_time=0.5):
        """
        Animate BFS algorithm. We assume that the graph is connected.
        Else, we need to run BFS for each connected component.
        Each step of the algorithm is animated separately.
        Note: vertices are 1-indexed.
        """
        graph = self.graph

        queue = [self.start_vertex]
        dist = [np.Inf] * (len(graph.vertices) + 1)
        dist[self.start_vertex] = 0
        parent = [None] * (len(graph.vertices) + 1)

        while queue:
            # animate pop
            cur_vertex = queue.pop(0)
            if cur_vertex == self.start_vertex:
                self.visit_vertex_animation(graph, None, cur_vertex, run_time=run_time)

            for neighbor in get_neighbors(graph, cur_vertex):
                if dist[neighbor] != np.Inf:
                    continue
                self.visit_vertex_animation(graph, cur_vertex, neighbor, run_time=run_time)

                queue.append(neighbor)
                dist[neighbor] = dist[cur_vertex] + 1

                # animate π[v] ← u
                parent[neighbor] = cur_vertex

    def visit_vertex_animation(self, graph: DiGraph, parent, next_vertex, run_time=0.3):
        visited_mark = Circle(radius=graph[next_vertex].radius * 0.9, fill_opacity=0, stroke_width=VISITED_VERTEX_WIDTH,
                              stroke_color=VISITED_COLOR).move_to(graph[next_vertex]).scale_to_fit_height(
            graph[next_vertex].height).set_z_index(10)
        self.mobjects_garbage_collector += visited_mark
        if parent is not None:
            visited_mark.rotate(graph.edges[(parent, next_vertex)].get_angle() + PI)
            self.play(graph.animate.add_edges((parent, next_vertex),
                                              edge_config={"stroke_color": VISITED_COLOR,
                                                           "stroke_width": VISITED_EDGE_WIDTH}), run_time=run_time)
        self.play(Create(visited_mark, run_time=run_time))


class BFSBigGraph(FastBFS):
    def __init__(self, **kwargs):
        vertices, edges, layout = get_big_triangle_graph(10)
        super().__init__(vertices, edges, layout, **kwargs)

    def construct(self):
        self.next_section("BFS Big Example", pst.NORMAL)
        self.play(Write(self.graph))
        self.graph.set_z_index(-10)
        self.next_section("Show BFS")
        self.animate_fast_bfs(0.3)
        self.next_section("BFS done")
        self.play(Unwrite(self.graph), Unwrite(self.mobjects_garbage_collector))
        self.wait(1)


class BFSIntro(SectionsScene):
    def __init__(self, **kwargs):
        self.title_width = config.frame_width * 0.7
        super().__init__(**kwargs)

    def construct(self):
        self.next_section("BFS Introduction", pst.NORMAL)
        title = Title("Breadth First Search (BFS)").scale_to_fit_width(config.frame_width * 0.9)
        sub_title = Tex(
            r'''An algorithm for searching a tree data structure for a node that satisfies a given property.''',
            tex_environment="flushleft").scale_to_fit_width(config.frame_width * 0.8).next_to(title, DOWN, buff=0.5)
        bfs_out_title = Text("BFS Output:").next_to(sub_title, DOWN, buff=1).to_edge(LEFT)
        bfs_out = BulletedList(
            "A tree", "$\pi$ - The parent links trace the shortest path back to $s$").next_to(bfs_out_title, DOWN,
                                                                                              buff=0.5).shift(
            RIGHT * 0.4).align_to(bfs_out_title, LEFT).shift(RIGHT * 1)
        bfs_out_group = VGroup(bfs_out_title, bfs_out)

        self.play(Write(title))
        self.next_section("Show BFS Output")
        self.play(Write(sub_title))
        self.play(Write(bfs_out_group))
        self.next_section("BFS example")
        self.play(Unwrite(bfs_out_group), Unwrite(sub_title), Unwrite(title))

        example_title = Title("BFS Output Example").scale_to_fit_width(config.frame_width * 0.9).to_edge(UP)
        self.play(Write(example_title))

        graph_example = create_graph([1, 2, 3, 4], edges=[(1, 2), (2, 3), (3, 1), (3, 4)],
                                     layout={1: ORIGIN, 2: DOWN + LEFT, 3: DOWN + RIGHT, 4: 2 * (DOWN + RIGHT)}
                                     ).scale_to_fit_height(
            config.frame_height * 0.4).move_to(ORIGIN)
        bfs_func = get_func_text("BFS(G,1):").scale(0.6).next_to(graph_example, DOWN, buff=0).to_edge(LEFT)

        pi = ArrayMob(r"$\pi$:", "-", "1", "1", "3", name_scale=1.2, show_indices=True, indices_pos=DOWN,
                      starting_index=1).scale(0.38).to_edge(DOWN).set_x(0).shift(LEFT)
        self.play(Write(graph_example))
        self.next_section("BFS function")
        self.play(Write(bfs_func))
        self.next_section("BFS pi")
        print(graph_example.edges)
        self.play(Write(pi), graph_example.edges[(3, 2)].animate_move_along_path(
            time_width=4, width_factor=2.8, flash_color=DARK_GREY, preserve_state=True))
        self.next_section("BFS done")
        self.play(Unwrite(graph_example), Unwrite(bfs_func), Unwrite(pi), Unwrite(example_title))
        self.wait(1)


class GraphsIntro(SectionsScene):
    def __init__(self, **kwargs):
        self.title_width = config.frame_width * 0.7
        self.definition_width = config.frame_width * 0.8
        self.example_tex_width = config.frame_width * 0.5
        self.example_buffer = 1
        super().__init__(**kwargs)

    def construct(self):
        self.next_section("Graphs Introduction", pst.NORMAL)
        title = Title("Undirected Graph").scale_to_fit_width(self.title_width).to_edge(UP)
        graph_def = Tex(
            r'''A\textbf{ undirected graph} $G$ is defined as a pair of two sets:
            $G=(V,E)$, where $V$ represents a set of vertices and $E$ is a
            set of pairs of vertices, representing edges between the vertices.''',
            tex_environment="flushleft").scale_to_fit_width(self.definition_width).next_to(title, DOWN, buff=0.5)
        color_tex(graph_def, t2c={r"\textbf{ undirected graph}": YELLOW})
        example_txt = Tex(
            r'''\textbf{Example}: $G=\left(\{1,2,3,4\},\ \left\{ \{1,2\},\{1,3\},\{3,4\}\right\} \right)$''',
            tex_environment="flushleft").scale_to_fit_width(self.definition_width).next_to(graph_def, DOWN,
                                                                                           buff=self.example_buffer)
        graph_example = create_graph([1, 2, 3, 4], edges=[(1, 2), (1, 3), (3, 4)], layout=SIMPLE_GRAPH_LAYOUT,
                                     directed_graph=False).scale_to_fit_height(
            config.frame_height * 0.3).next_to(example_txt, DOWN, buff=0.3).set_x(0)

        self.play(Write(title))
        self.play(Write(graph_def))
        self.next_section("Graphs example")
        self.play(Write(example_txt))
        self.play(Write(graph_example))
        self.next_section("Graphs done")
        self.play(Unwrite(graph_def), Unwrite(example_txt), Unwrite(graph_example), Unwrite(title))
        self.wait(1)

        self.next_section("Directed Graphs")
        title = Title("Directed Graph").scale_to_fit_width(self.title_width).to_edge(UP)
        graph_def = Tex(
            r'''A \textbf{directed graph} $G$ is defined as a pair of two sets: $G=\left(V,E\right)$,
            where $V$ represents a set of vertices and $E\subseteq V\times V$
            is a set of directed edges between vertices.''', tex_environment="flushleft").scale_to_fit_width(
            self.definition_width).next_to(title, DOWN, buff=0.5)
        color_tex(graph_def, t2c={r"\textbf{directed graph}": YELLOW})
        example_txt = Tex(
            r'''\textbf{Example}: $G=\left(\{1,2,3,4\},\ \left\{ (1,2),(1,4),(4,1),(4,3)\right\} \right)$''',
            tex_environment="flushleft").scale_to_fit_width(self.definition_width).next_to(graph_def, DOWN,
                                                                                           buff=self.example_buffer)
        graph_example = create_graph([1, 2, 3, 4], edges=[(1, 2), (1, 4), (4, 1), (4, 3)], layout=SIMPLE_GRAPH_LAYOUT,
                                     directed_graph=True, dual_arrow=True).scale_to_fit_height(
            config.frame_height * 0.3).next_to(example_txt, DOWN, buff=0.3).set_x(0)

        self.play(Write(title))
        self.play(Write(graph_def))
        self.next_section("Graphs example")
        self.play(Write(example_txt))
        self.play(Write(graph_example))
        self.next_section("Graphs done")
        self.play(Unwrite(graph_def), Unwrite(example_txt), Unwrite(graph_example), Unwrite(title))
        self.wait(1)


class EdgesUpperBound(SectionsScene):
    def __init__(self, **kwargs):
        self.title_width = config.frame_width * 0.7
        self.definition_width = config.frame_width * 0.8
        self.example_tex_width = config.frame_width * 0.5
        self.example_buffer = 1
        super().__init__(**kwargs)

    def construct(self):
        self.next_section("Edges Upper Bound", pst.NORMAL)
        title = Title("Edges Upper Bound").scale_to_fit_width(self.title_width).to_edge(UP)
        # full graph
        vertices = list(range(1, 6))
        graph_example = create_graph(vertices, edges=[(i, j) for i in vertices for j in vertices if i != j],
                                     layout='circular', directed_graph=False).scale_to_fit_width(
            self.example_tex_width * 0.5).next_to(title, DOWN, buff=0.2).set_x(0)

        edeges_upper_bound = Tex(
            r"$\left|E\right|\leq{\left|V\right| \choose 2}=\frac{\left|V\right|\left(\left|V\right|-1\right)}{2}=O\left(\left|V\right|^{2}\right)$")
        edeges_upper_bound.scale_to_fit_width(self.definition_width).next_to(graph_example, DOWN, buff=0.5)
        self.play(Write(title))
        self.play(Write(graph_example))
        self.next_section("claculation")
        self.play(Write(edeges_upper_bound))
        self.next_section("done")
        self.play(Unwrite(edeges_upper_bound), Unwrite(graph_example), Unwrite(title))
        self.wait(1)


class GraphRepresentation(SectionsScene):
    def __init__(self, **kwargs):
        self.title_width = config.frame_width * 0.7
        self.definition_width = config.frame_width * 0.8
        self.example_tex_width = config.frame_width * 0.5
        self.example_buffer = 1
        self.figs_height = config.frame_height * 0.2
        super().__init__(**kwargs)

    def construct(self):
        self.next_section("Graph Representation", pst.NORMAL)
        title = Title("Graph Representation").to_edge(UP)

        graph_examp = create_graph([1, 2, 3, 4], edges=[(1, 2), (1, 4), (1, 3), (4, 1), (4, 3), (3, 1)],
                                   layout=SIMPLE_GRAPH_LAYOUT, directed_graph=True,
                                   dual_arrow=True).scale_to_fit_height(
            self.figs_height)
        for vertex in graph_examp.vertices:
            graph_examp[vertex].scale(0.7)

        ajacency_list_representation = SVGMobject(
            str(ROOT_PATH / "images/graph_represent_link.svg")).scale_to_fit_height(self.figs_height)

        ajacency_matrix_representation = SVGMobject(
            str(ROOT_PATH / "images/graph_represent_mat.svg")).scale_to_fit_height(self.figs_height)

        VGroup(graph_examp, ajacency_list_representation, ajacency_matrix_representation).arrange(RIGHT,
                                                                                                  buff=0.5).scale_to_fit_width(
            config.frame_width * 0.9).to_edge(LEFT)

        mat_title = Text("Adjacency Matrix").scale(0.5).next_to(ajacency_matrix_representation, UP, buff=0.3)
        adj_title = Text("Adjacency List").scale(0.5).next_to(ajacency_list_representation, UP, buff=0.3).match_y(
            mat_title)

        space_complex_title = Text("Space Complexity:").match_width(graph_examp).next_to(graph_examp, DOWN, buff=1)
        space_complex_adj = Tex(r"$O\left(\left|V\right|+\left|E\right|\right)$").next_to(adj_title,
                                                                                          DOWN).match_y(
            space_complex_title)
        space_complex_mat = Tex(r"$O\left(\left|V\right|^{2}\right)$").next_to(mat_title, DOWN).match_y(
            space_complex_title)

        self.play(Write(title))
        self.play(Write(graph_examp))
        self.next_section("Adjacency List")
        self.play(Write(ajacency_list_representation), Write(adj_title))
        self.next_section("Space Complexity")
        self.play(Write(space_complex_title))
        self.next_section("Space Complexity")
        self.play(Write(space_complex_adj))
        self.next_section("Adjacency Matrix")
        self.play(Write(ajacency_matrix_representation), Write(mat_title))
        self.next_section("Space Complexity")
        self.play(Write(space_complex_mat))
        self.next_section("done")
        self.play(Unwrite(ajacency_list_representation), Unwrite(adj_title), Unwrite(ajacency_matrix_representation),
                  Unwrite(mat_title), Unwrite(graph_examp), Unwrite(title), Unwrite(space_complex_title),
                  Unwrite(space_complex_adj), Unwrite(space_complex_mat))
        self.wait(1)


if __name__ == "__main__":
    scenes_lst = [GraphsIntro, EdgesUpperBound, GraphRepresentation, BFSIntro, BFSBigGraph, DirectedGraphBFS,
                  BFSComplexity]

    render_scenes(scenes_lst, OUT_DIR, PRESENTATION_MODE, DISABLE_CACHING, gif_scenes=[28 + i for i in range(6)],
                  create_gif=False)
