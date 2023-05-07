from __future__ import annotations

from typing import Hashable

from tools.array import *
from tools.consts import *
from tools.funcs import *
from tools.scenes import *
from tools.my_graphs import DiGraph

ROOT_PATH = Path(__file__).resolve().parent
sys.path.append(str(ROOT_PATH.parent))
OUT_DIR = MEDIA_PATH / Path(__file__).resolve().parent.stem

PRESENTATION_MODE = False
DISABLE_CACHING = False
config.background_color = BACKGROUND_COLOR

# --------------------------------- constants --------------------------------- #
EDGE_COLOR = GREY
BFS_EDGE_CONFIG = EDGE_CONFIG.copy()
BFS_EDGE_CONFIG["stroke_color"] = EDGE_COLOR

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
        self.graph = self.create_graph()
        self.rendered_code = create_code(BFS_PSEUDO_CODE)
        self.queue_mob, self.u, self.pi = self.create_bfs_vars(self.rendered_code)
        self.dist_mob = VGroup(
            *([VMobject()] + [create_dist_label(i, self.graph, r"\infty") for i in self.vertices]))  # 1-indexed
        self.mobjects_garbage_collector = VGroup(*[mob for mob in self.dist_mob])

    def construct(self):
        self.next_section("BFS", pst.NORMAL)

        self.play(Write(self.rendered_code))
        self.play(Write(self.graph))

        self.animate_bfs()

        self.play(highlight_code_lines(self.rendered_code, indicate=False))
        self.next_section("BFS finished")
        self.play(Unwrite(self.graph), Unwrite(self.dist_mob), Unwrite(self.mobjects_garbage_collector))
        self.play(Unwrite(VGroup(self.queue_mob, self.u, self.pi)))
        self.play(Uncreate(self.rendered_code))
        self.wait()

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

    def create_graph(self):
        """
        Create graph and add labels to vertices,
        Note: vertices are 1-indexed
        """
        if not self.directed_graph:
            self.edges += [(v, u) for u, v in self.edges]

        edge_config = BFS_EDGE_CONFIG.copy()
        if self.directed_graph:
            edge_configs = {}
            for k, v in self.edges:
                if (v, k) in self.edges:
                    edge_configs[(k, v)] = BFS_EDGE_CONFIG.copy()
                else:
                    edge_configs[(k, v)] = BFS_EDGE_CONFIG.copy()
                    edge_configs[(k, v)]["tip_config"]["tip_length"] = TIP_SIZE
                    edge_configs[(k, v)]["tip_config"]["tip_width"] = DEFAULT_ARROW_TIP_WIDTH
            edge_config = edge_configs

        graph = DiGraph(self.vertices, self.edges, layout=self.layout, layout_scale=1.5, labels=True,
                        label_fill_color=LABEL_COLOR, vertex_config=VERTEX_CONFIG, edge_config=edge_config)
        for i, vertex in enumerate(graph.vertices):
            graph[vertex][1].scale(VERTEX_LABEL_SCALE)
        relative_scale = config.frame_width * 0.4 if graph.width > graph.height else config.frame_height * 0.7
        graph.scale_to_fit_width(relative_scale).move_to(ORIGIN).to_edge(RIGHT, buff=0.2)
        return graph

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
                                                               "tip_length": VISITED_TIP_SIZE if self.directed_graph else 0}}))
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


class BigGraphBFS(BFSScene):
    def __init__(self, **kwargs):
        vertices = list(range(1, 9))
        edges = [(1, 7), (1, 8), (2, 3), (2, 4), (2, 5),
                 (2, 8), (3, 4), (6, 1), (6, 2), (7, 2), (7, 4), (3, 6)]
        start_vertex = 1
        super().__init__(vertices, edges, start_vertex, **kwargs)
        # def construct(self):


class SmallGraphBFS(BFSScene):
    def __init__(self, **kwargs):
        vertices = list(range(1, 4))
        edges = [(1, 2), (1, 3), (2, 3)]
        start_vertex = 1
        super().__init__(vertices, edges, start_vertex, directed_graph=True, **kwargs)

    # def construct(self):
    #     super().construct()
    #     self.play(Create(Circle()))


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

    # def construct(self):
    #     self.play(Create(Circle()))
    #     super().construct()


class MovingDiGraph(Scene):
    def construct(self):
        vertices = list(range(1, 8))
        edges = [(1, 2), (1, 3),
                 (2, 3), (2, 4), (2, 5), (3, 6), (3, 7),
                 (5, 4), (5, 1), (6, 1), (6, 7)]
        start_vertex = 1
        vertices_locations = {1: UP * 2, 2: LEFT + UP, 3: RIGHT + UP, 4: 1.5 * LEFT, 5: 0.5 * LEFT, 6: 0.5 * RIGHT,
                              7: 1.5 * RIGHT}
        g = DiGraph(vertices, edges, layout_scale=1.5, layout=vertices_locations, labels=True,
                    label_fill_color=LABEL_COLOR, vertex_config=VERTEX_CONFIG.copy(),
                    edge_config=BFS_EDGE_CONFIG.copy())
        # g.scale(2)
        g.update_edges(g)
        self.add(g)
        self.play(g.animate.add_edges((2, 4), edge_config={"stroke_color": VISITED_COLOR,
                                                           "stroke_width": VISITED_EDGE_WIDTH,
                                                           "tip_config": {
                                                               "tip_length": VISITED_TIP_SIZE}}))
        self.play(g[4][0].animate.set_stroke(width=VISITED_VERTEX_WIDTH, color=VISITED_COLOR))
        g.update_edges(g)
        # b = Arrow()
        # self.play(GrowFromEdge(b[1], b.get_left()))

        self.wait()
        self.play(Unwrite(g))


# class DFSScene(Scene):

if __name__ == "__main__":
    # scenes_lst = [BigGraphBFS]
    # scenes_lst = [SmallGraphBFS]
    scenes_lst = [DirectedGraphBFS]
    # scenes_lst = [MovingDiGraph]

    run_scenes(scenes_lst, OUT_DIR, PRESENTATION_MODE, DISABLE_CACHING, gif_scenes=[28 + i for i in range(6)])
    # create_scene_gif(OUT_DIR, scenes_lst[0].__name__, section_num_lst=[28 + i for i in range(6)])
