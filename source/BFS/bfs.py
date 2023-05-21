from __future__ import annotations

from typing import Hashable
from copy import copy, deepcopy

from tools.array import *
from tools.consts import *
from tools.funcs import *
from tools.scenes import *
from tools.graphs.my_graphs import DiGraph

ROOT_PATH = Path(__file__).resolve().parent
sys.path.append(str(ROOT_PATH.parent))
OUT_DIR = MEDIA_PATH / Path(__file__).resolve().parent.stem

PRESENTATION_MODE = False
DISABLE_CACHING = False
config.background_color = BACKGROUND_COLOR

# --------------------------------- constants --------------------------------- #
EDGE_COLOR = GREY
EDGE_CONFIG["stroke_color"] = EDGE_COLOR

BFS_PSEUDO_CODE = '''def BFS(G,s): 
    queue ← Build Queue({s})
    for all vertices u in V do:
        dist[u] ← ∞
    dist[s] ← 0
    π[s] ← None

    while queue ≠ ø do:
        u = queue.pop(0) 
        for neighbor v of u & dist[v] = ∞:
                queue.push(v)
                dist[v] = dist[u] + 1
                π[v] = u'''


# --------------------------------- functions --------------------------------- #
def create_graph(vertices: list[Hashable], edges: list[tuple[Hashable, Hashable]], layout: str = "spring",
                 directed_graph: bool = False, graph_type=DiGraph, absolute_scale_vertices=False,
                 labels: bool = True) -> DiGraph:
    """
    Create graph and add labels to vertices,
    Note: vertices are 1-indexed
    """
    edges = deepcopy(edges)
    if not directed_graph:
        edges += [(v, u) for u, v in edges]

    edge_config = EDGE_CONFIG
    if directed_graph:
        edge_configs = {}
        for k, v in edges:
            if (v, k) in edges:
                edge_configs[(k, v)] = EDGE_CONFIG.copy()
            else:
                edge_configs[(k, v)] = EDGE_CONFIG.copy()
                edge_configs[(k, v)]["tip_config"]["tip_length"] = TIP_SIZE
                edge_configs[(k, v)]["tip_config"]["tip_width"] = DEFAULT_ARROW_TIP_WIDTH
        edge_config = edge_configs

    graph = graph_type(vertices, edges, layout=layout, layout_scale=1.5, labels=labels,
                       label_fill_color=LABEL_COLOR, vertex_config=VERTEX_CONFIG, edge_config=edge_config)
    for i, vertex in enumerate(graph.vertices):
        if not labels:
            if not absolute_scale_vertices:
                graph[vertex].scale_to_fit_height(graph[0].height)
            continue
        label = graph[vertex][1]
        graph[vertex].remove(label)
        label.next_to(graph[vertex], RIGHT, buff=0)
        label.move_to(graph[vertex])
        if not absolute_scale_vertices:
            label.scale(VERTEX_LABEL_SCALE)
        else:
            graph[vertex].scale_to_fit_height(graph[0].height)
            label.scale_to_fit_height(graph[vertex].height * 0.5)
        graph[vertex].add(label)
    relative_scale = config.frame_width * 0.4 if graph.width > graph.height else config.frame_height * 0.7
    graph.scale_to_fit_width(relative_scale).move_to(ORIGIN).to_edge(RIGHT, buff=0.2)
    return graph


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
                                  graph_type=DiGraph, absolute_scale_vertices=False,
                                  labels=True)
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
        self.play(queue_mob.draw_array())

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
        self.play(pi.draw_array())
        self.play(pi.at(0, "-"))
        visit_all = False
        while queue:
            self.highlight_and_indicate_code([8])
            # animate pop
            cur_vertex = queue.pop(0)
            if cur_vertex == 2:
                break
            if cur_vertex == self.start_vertex:
                self.play(Write(u))
            if not visit_all: self.next_section(f"Pop vertex {cur_vertex} from queue")
            self.highlight_and_indicate_code([9])
            if cur_vertex == self.start_vertex:
                self.visit_vertex_animation(graph, None, cur_vertex)
            pop_item = queue_mob.get_square(0)
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
                self.play(pi.at(neighbor - 1, cur_vertex))

            self.play(pop_animation[0])

    def create_bfs_vars(self, rendered_code: Code) -> tuple[ArrayMob, Tex, ArrayMob]:
        scale = 1
        start_vars_y = rendered_code.get_bottom()[1]
        lag_y = (config.frame_height / 2 + start_vars_y) / 3
        queue_mob = ArrayMob("queue:", self.start_vertex, name_scale=scale).set_y(start_vars_y - lag_y, DOWN).to_edge(
            LEFT)

        u = Tex("u:").scale_to_fit_height(queue_mob.height_ref).next_to(queue_mob, DOWN, buff=queue_mob.get_square(
            0).height * 0.8).align_to(queue_mob.array_name, RIGHT).set_y(start_vars_y - 2 * lag_y, DOWN)
        pi = ArrayMob(r"$\pi$:", *[""] * len(self.vertices), name_scale=scale, show_labels=True, labels_pos=DOWN,
                      align_point=u.get_right() + 0.5 * DOWN * (queue_mob.obj_ref.get_bottom()[1] - u.get_top()[1]),
                      starting_index=1).set_y(start_vars_y - 3 * lag_y, DOWN)
        u.set_y((queue_mob.get_bottom()[1] + pi.get_top()[1]) / 2)
        VGroup(queue_mob, u, pi).next_to(rendered_code, DOWN).to_edge(LEFT)
        return queue_mob, u, pi

    def visit_vertex_animation(self, graph: DiGraph, parent, next_vertex):
        visited_mark = Circle(radius=graph[next_vertex].radius * 0.9, fill_opacity=0, stroke_width=VISITED_VERTEX_WIDTH,
                              stroke_color=VISITED_COLOR).move_to(graph[next_vertex]).scale_to_fit_height(
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

        self.visit_vertex_animation(self.graph, 1, 2)
        self.play(Write(self.rendered_code))
        self.play(Write(self.graph))

        self.animate_bfs()

        self.play(highlight_code_lines(self.rendered_code, indicate=False))
        self.next_section("BFS finished")
        self.play(Unwrite(self.graph), Unwrite(self.dist_mob), Unwrite(self.mobjects_garbage_collector))
        self.play(Unwrite(VGroup(self.queue_mob, self.u, self.pi)))
        self.play(Uncreate(self.rendered_code))
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
                                  graph_type=DiGraph, absolute_scale_vertices=True,
                                  labels=False).scale_to_fit_height(
            config.frame_height * 0.9).move_to(ORIGIN)
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
        vertices, edges, layout = get_big_triangle_graph(4)
        super().__init__(vertices, edges, layout, **kwargs)

    def construct(self):
        self.next_section("BFS Big Example", pst.NORMAL)
        self.play(Write(self.graph))
        self.next_section("Show BFS")
        self.animate_fast_bfs(0.3)
        self.next_section("BFS done")
        self.play(Unwrite(self.graph), Unwrite(self.mobjects_garbage_collector))
        self.wait(1)


if __name__ == "__main__":
    # scenes_lst = [BigGraphBFS]
    # scenes_lst = [SmallGraphBFS]
    scenes_lst = [BFSBigGraph]
    scenes_lst = [DirectedGraphBFS]
    # scenes_lst = [MovingDiGraph]

    run_scenes(scenes_lst, OUT_DIR, PRESENTATION_MODE, DISABLE_CACHING, gif_scenes=[28 + i for i in range(6)])
    # create_scene_gif(OUT_DIR, scenes_lst[0].__name__, section_num_lst=[28 + i for i in range(6)])
