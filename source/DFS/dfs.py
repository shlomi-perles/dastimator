from __future__ import annotations

from typing import Hashable

from manim_editor import PresentationSectionType as pst

from tools.graphs.my_graphs import DiGraph
from BFS.bfs import BFS_PSEUDO_CODE, create_graph, get_big_triangle_graph
from tools.array import *
from tools.consts import *
from tools.funcs import *
from tools.graphs.my_graphs import DiGraph
from copy import copy, deepcopy

ROOT_PATH = Path(__file__).resolve().parent
sys.path.append(str(ROOT_PATH.parent))
OUT_DIR = MEDIA_PATH / Path(__file__).resolve().parent.stem

PRESENTATION_MODE = True
DISABLE_CACHING = False
config.background_color = BACKGROUND_COLOR

# --------------------------------- constants --------------------------------- #
EDGE_COLOR = GREY
EDGE_CONFIG["stroke_color"] = EDGE_COLOR
MAIN_GRAPH_EXAMPLE_VERTICES = list(range(1, 8))
MAIN_GRAPH_EXAMPLE_EDGES = [(1, 2), (1, 3), (2, 3), (2, 4), (2, 5), (3, 6), (3, 7), (5, 4), (5, 1), (6, 1), (6, 7)]
MAIN_GRAPH_EXAMPLE_VERTICES_LOC = {1: UP * 2, 2: LEFT + UP, 3: RIGHT + UP, 4: 1.5 * LEFT, 5: 0.5 * LEFT, 6: 0.5 * RIGHT,
                                   7: 1.5 * RIGHT}

DFS_PSEUDO_CODE = '''def DFS(G,s):
    queue ← Build Queue({s})
    Init dists to ∞, dist[s] ← 0
    π[s] ← None
    time ← 1

    while queue ≠ ø do:
        u = queue.pop()
        pre[u] ← time, time += 1
        for neighbor v of u & dist[v] = ∞:
                queue.push(v)
                dist[v] = dist[u] + 1
                π[v] ← u
                
        if π[u] = queue[-1]: # checkout
            post[π[u]] ← time, time += 1'''

RECURSIVE_DFS_PSEUDO_CODE = '''def DFS(G,s):
    time += 1
    pre[s] ← time
    for neighbor v of s & v.visited = False:
        v.visited ← True
        π[v] ← s
        DFS(G,v)
    time += 1
    post[s] ← time'''


# --------------------------------- DFS --------------------------------- #

class DFSScene(SectionsScene):
    def __init__(self, vertices: list[Hashable], edges: list[tuple[Hashable, Hashable]], start_vertex=1,
                 directed_graph: bool = False, layout: str | dict = "circular", priority_list=None, **kwargs):
        super().__init__(**kwargs)
        self.directed_graph = directed_graph
        self.vertices = vertices
        self.edges = edges
        self.start_vertex = start_vertex
        self.layout = layout
        self.graph = self.create_graph()
        self.rendered_code = create_code(DFS_PSEUDO_CODE)
        self.queue_mob, self.u, self.pi = self.create_bfs_vars(self.rendered_code)
        self.dist_mob = VGroup(
            *([VMobject()] + [create_dist_label(i, self.graph, r"\infty") for i in self.vertices]))  # 1-indexed
        self.mobjects_garbage_collector = VGroup(*[mob for mob in self.dist_mob])
        self.priority_list = priority_list

    def construct(self):
        # self.next_section("BFS to DFS", pst.NORMAL) # TODO: add
        # self.animate_bfs_dfs_comparison() # TODO: add

        self.next_section("DFS", pst.NORMAL)
        self.add(self.rendered_code)  # TODO: remove
        self.add(self.graph)  # TODO: remove
        # self.play(Write(self.rendered_code))
        # self.play(Write(self.graph))

        self.animate_dfs()

        self.play(highlight_code_lines(self.rendered_code, indicate=False))
        self.next_section("DFS finished", pst.SUB_NORMAL)
        self.play(Unwrite(self.graph), Unwrite(self.dist_mob), Unwrite(self.mobjects_garbage_collector))
        self.play(Unwrite(VGroup(self.queue_mob, self.u, self.pi)))
        self.play(Uncreate(self.rendered_code))
        self.wait()

    def animate_bfs_dfs_comparison(self):
        bfs_code = create_code(BFS_PSEUDO_CODE)
        self.add(bfs_code)
        self.play(transform_code_lines(bfs_code, self.rendered_code, {1: 1, 2: 2, 3: 3, 4: 3, 5: 3}))

        self.next_section("Change pop")
        self.play(Indicate(bfs_code.code[8]))
        self.play(transform_code_lines(bfs_code, self.rendered_code, {6: 4, 7: 6, 8: 7, 9: 8}))
        self.play(Indicate(self.rendered_code.code[7]))

        self.next_section("add time mark")
        self.rendered_code[0][0].set_z_index(0)
        self.play(TransformMatchingShapes(bfs_code.background_mobject[0], self.rendered_code.background_mobject[0],
                                          transform_mismatches=True))
        self.play(Create(self.rendered_code.line_numbers[13:]))
        self.play(AnimationGroup(
            *[Write(self.rendered_code.code[4]), Write(self.rendered_code.code[8]),
              Write(self.rendered_code.code[14:16])], lag_ratio=0.5))

        bfs_code.set_opacity(0)
        self.remove(bfs_code)
        self.add(self.rendered_code)
        self.play(highlight_code_lines(self.rendered_code, lines=[5, 9, 15, 16], indicate=False))

    def animate_dfs(self):
        """
        Animate BFS algorithm. We assume that the graph is connected.
        Else, we need to run BFS for each connected component.
        Each step of the algorithm is animated separately.
        Note: vertices are 1-indexed.
        """
        graph, rendered_code, dist_mob = self.graph, self.rendered_code, self.dist_mob
        queue_mob, u, pi = self.queue_mob, self.u, self.pi

        queue = [self.start_vertex]
        self.next_section("Initialize queue", pst.SUB_NORMAL)
        self.highlight_and_indicate_code([2])
        self.play(queue_mob.draw_array())

        dist = [np.Inf] * (len(graph.vertices) + 1)
        self.next_section("Initialize dists", pst.SUB_NORMAL)
        self.highlight_and_indicate_code([3])
        self.play(AnimationGroup(*[anim(dist_mob[i]) for i in range(1, len(dist_mob)) for anim in [Write, Flash]],
                                 lag_ratio=0.3))
        dist[self.start_vertex] = 0
        self.play(self.change_dist(self.start_vertex, 0))

        parent = [None] * (len(graph.vertices) + 1)
        self.next_section("Init first vertex parent", pst.SUB_NORMAL)
        self.highlight_and_indicate_code([4])
        self.play(pi.draw_array())
        self.play(pi.at(0, "-"))
        visit_all = False
        while queue:
            self.highlight_and_indicate_code([7])
            # animate pop
            cur_vertex = queue.pop()
            if cur_vertex == self.start_vertex:
                self.play(Write(u))
            if not visit_all: self.next_section(f"Pop vertex {cur_vertex} from queue", pst.SUB_NORMAL)
            self.highlight_and_indicate_code([8])
            if cur_vertex == self.start_vertex:
                self.visit_vertex_animation(graph, None, cur_vertex)
            pop_item = queue_mob.get_square(len(queue))
            self.play(queue_mob.indicate_at(len(queue)))
            self.play(pop_item.animate.match_y(u), run_time=0.5)
            self.play(pop_item.animate.next_to(self.u, RIGHT), run_time=0.5)
            pop_animation = queue_mob.pop(len(queue), shift=RIGHT).animations
            self.play(AnimationGroup(*pop_animation[1:]))

            for neighbor in get_neighbors(graph, cur_vertex, priority_lst=self.priority_lst):
                if dist[neighbor] != np.Inf:
                    continue
                # animate for neighbor v of u & dist[v] = ∞
                self.next_section("Visit neighbor", pst.SUB_NORMAL)
                self.highlight_and_indicate_code([10])
                self.next_section("Update visit", pst.SUB_NORMAL)
                self.visit_vertex_animation(graph, cur_vertex, neighbor)

                # animate queue.push(v)
                queue.append(neighbor)
                self.next_section(f"Add vertex {neighbor} to queue", pst.SUB_NORMAL)
                self.highlight_and_indicate_code([11])
                self.play(queue_mob.push(neighbor))

                # animate dist[v] = dist[u] + 1
                dist[neighbor] = dist[cur_vertex] + 1
                self.next_section(f"Set distance {dist[cur_vertex] + 1} to vertex {neighbor}", pst.SUB_NORMAL)
                self.highlight_and_indicate_code([12])
                self.next_section("Update dist", pst.SUB_NORMAL)
                self.play(self.change_dist(neighbor, dist[neighbor]))

                if np.Inf not in dist:
                    visit_all = True

                # animate π[v] ← u
                parent[neighbor] = cur_vertex
                self.next_section(f"Add parent {cur_vertex} to vertex {neighbor}", pst.SUB_NORMAL)
                self.highlight_and_indicate_code([13])
                self.next_section("Update parent", pst.SUB_NORMAL)
                self.play(pi.at(neighbor - 1, cur_vertex))

            self.play(pop_animation[0])

    def create_graph(self):
        """
        Create graph and add labels to vertices,
        Note: vertices are 1-indexed
        """
        if not self.directed_graph:
            self.edges += [(v, u) for u, v in self.edges]

        edge_config = EDGE_CONFIG
        if self.directed_graph:
            edge_configs = {}
            for k, v in self.edges:
                if (v, k) in self.edges:
                    edge_configs[(k, v)] = EDGE_CONFIG.copy()
                else:
                    edge_configs[(k, v)] = EDGE_CONFIG.copy()
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


class BigGraphDFS(DFSScene):
    def __init__(self, **kwargs):
        vertices = list(range(1, 9))
        edges = [(1, 7), (1, 8), (2, 3), (2, 4), (2, 5),
                 (2, 8), (3, 4), (6, 1), (6, 2), (7, 2), (7, 4), (3, 6)]
        start_vertex = 1
        super().__init__(vertices, edges, start_vertex, **kwargs)
        # def construct(self):


class SmallGraphDFS(DFSScene):
    def __init__(self, **kwargs):
        vertices = list(range(1, 4))
        edges = [(1, 2), (1, 3), (2, 3)]
        start_vertex = 1
        super().__init__(vertices, edges, start_vertex, directed_graph=True, **kwargs)

    # def construct(self):
    #     super().construct()
    #     self.play(Create(Circle()))


class DirectedGraphDFS(DFSScene):
    def __init__(self, **kwargs):
        vertices = list(range(1, 8))
        edges = MAIN_GRAPH_EXAMPLE_EDGES
        start_vertex = 1
        vertices_locations = MAIN_GRAPH_EXAMPLE_VERTICES_LOC
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
                    label_fill_color=LABEL_COLOR, vertex_config=VERTEX_CONFIG.copy(), edge_config=EDGE_CONFIG.copy())
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


class RecursiveDFSScene(SectionsScene):
    def __init__(self, vertices: list[Hashable], edges: list[tuple[Hashable, Hashable]], start_vertex=1,
                 directed_graph: bool = False, layout: str | dict = "circular", priority_lst=None, **kwargs):
        super().__init__(**kwargs)
        self.directed_graph = directed_graph
        self.vertices = vertices
        self.edges = edges
        self.start_vertex = start_vertex
        self.layout = layout
        self.priority_lst = priority_lst
        self.graph = create_graph(self.vertices, self.edges, self.layout, self.directed_graph)
        self.rendered_code = create_code(RECURSIVE_DFS_PSEUDO_CODE)
        self.queue_mob, self.u, self.pi, self.time = self.create_dfs_vars(self.rendered_code)
        self.pre, self.post = self.create_pre_ans_post()
        self.pre_and_post = VGroup(*[i for i in self.pre if i is not None], *[i for i in self.post if i is not None])
        self.mobjects_garbage_collector = VGroup(self.pre_and_post)

    def animate_recursive_dfs(self):
        """
        Animate DFS algorithm. We assume that the graph is connected.
        Else, we need to run BFS for each connected component.
        Each step of the algorithm is animated separately.
        Note: vertices are 1-indexed.
        """
        graph, rendered_code = self.graph, self.rendered_code
        queue_mob, u, pi, time = self.queue_mob, self.u, self.pi, self.time
        times_tex_height_factor = 0.6

        self.next_section("DFS Present")
        self.highlight_and_indicate_code([4, 5, 6])

        self.next_section("DFS time present")
        self.highlight_and_indicate_code([2, 3, 7, 8])
        self.next_section("Present pre and post")
        self.play(Write(self.pre_and_post))
        self.next_section("Start DFS")

        dist = [np.Inf] * (len(graph.vertices) + 1)
        self.play(highlight_code_lines(self.rendered_code, indicate=False))
        dist[self.start_vertex] = 0
        parent = [None] * (len(graph.vertices) + 1)
        fast_run = False

        def dfs(start_vertex):
            if start_vertex != self.start_vertex:
                self.highlight_and_indicate_code([1])
                self.next_section(f"DFS on vertex {start_vertex}", skip_section=fast_run)
                self.play(queue_mob.push(start_vertex, LEFT))
            else:
                self.visit_vertex_animation(graph, None, start_vertex)

            self.next_section("Mark vertex as visited", skip_section=fast_run)
            self.highlight_and_indicate_code([2, 3])
            self.play(ChangeDecimalToValue(time[1], time[1].number + 1),
                      Flash(time[1], flash_radius=time[1].height))
            pre_time = time[1].copy()
            self.mobjects_garbage_collector.add(pre_time)
            self.play(
                pre_time.animate.scale_to_fit_height(self.pre[start_vertex].height * times_tex_height_factor).move_to(
                    self.pre[start_vertex]))
            for neighbor in get_neighbors(graph, start_vertex, self.priority_lst):
                if dist[neighbor] != np.Inf:
                    continue
                dist[neighbor] = dist[start_vertex] + 1
                self.next_section(f"DFS on vertex {neighbor}", skip_section=fast_run)
                self.highlight_and_indicate_code([4, 5])
                self.visit_vertex_animation(graph, parent[start_vertex], start_vertex)

                # animate π[v] ← s
                parent[neighbor] = start_vertex
                self.next_section(f"Add parent {start_vertex} to vertex {neighbor}", skip_section=fast_run)
                self.highlight_and_indicate_code([6])
                self.next_section("Update parent", skip_section=fast_run)
                self.play(pi.at(neighbor - 1, start_vertex))

                # animate DFS(G,v)
                self.next_section(f"DFS on vertex {neighbor}", skip_section=fast_run)
                self.highlight_and_indicate_code([7])
                dfs(neighbor)

            self.next_section(f"DFS finished on vertex {start_vertex}", skip_section=fast_run)
            self.highlight_and_indicate_code([8, 9])
            self.play(ChangeDecimalToValue(time[1], time[1].number + 1),
                      Flash(time[1], flash_radius=time[1].height))
            post_time = time[1].copy()
            self.mobjects_garbage_collector.add(post_time)
            self.play(
                post_time.animate.scale_to_fit_height(self.post[start_vertex].height * times_tex_height_factor).move_to(
                    self.post[start_vertex]))
            self.next_section(f"Pop vertex {start_vertex} from queue", skip_section=fast_run)
            self.play(queue_mob.pop())

        dfs(self.start_vertex)

    def create_pre_ans_post(self):
        positions = {1: UP, 2: LEFT + UP, 3: UP + RIGHT, 4: DOWN, 5: DOWN, 6: DOWN, 7: DOWN}
        pre = [Square(fill_color=GREEN, fill_opacity=1, stroke_color=WHITE).scale_to_fit_height(
            self.graph.vertices[i].height * 0.5)
            for i in range(1, len(self.vertices) + 1)]
        pre.insert(0, None)
        post = [Square(fill_color=RED, fill_opacity=1, stroke_color=WHITE).scale_to_fit_height(
            self.graph.vertices[i].height * 0.5)
            for i in range(1, len(self.vertices) + 1)]
        post.insert(0, None)
        for vertex in self.vertices:
            post[vertex].next_to(pre[vertex], RIGHT, buff=0)
            VGroup(pre[vertex], post[vertex]).next_to(self.graph.vertices[vertex], positions[vertex], buff=0.1)
        return pre, post

    def create_dfs_vars(self, rendered_code: Code) -> tuple[ArrayMob, VGroup, ArrayMob, VGroup]:
        scale = 1
        start_vars_y = rendered_code.get_bottom()[1] * 1.3
        lag_y = (config.frame_height / 2 + start_vars_y) * 0.35

        queue_mob = ArrayMob("stack:", self.start_vertex, name_scale=scale).set_y(start_vars_y - lag_y, DOWN).to_edge(
            LEFT)
        pi = ArrayMob(r"$\pi$:", *[""] * len(self.vertices), name_scale=scale, show_labels=True, labels_pos=DOWN,
                      align_point=queue_mob.array_name.get_right(), starting_index=1).set_y(start_vars_y - 2 * lag_y,
                                                                                            DOWN)
        # queue_mob.set_y((s.get_bottom()[1] + pi.get_top()[1]) / 2)
        s = Tex("s").set_y(start_vars_y - lag_y, DOWN).to_edge(LEFT).next_to(queue_mob.get_square(0), UP, buff=0.2)
        VGroup(s, queue_mob, pi).next_to(rendered_code, DOWN, buff=1).to_edge(LEFT)
        time = get_func_text("time = ").scale_to_fit_height(queue_mob.array_name.height * 1.3)
        time = VGroup(time, DecimalNumber(0, num_decimal_places=0).match_height(time).next_to(
            time, RIGHT, buff=0.4)).next_to(self.graph, UP, buff=1).set_color(WHITE)

        s = VGroup(queue_mob.get_square(0)[0].copy().set_stroke(color=YELLOW).set_z_index(10), s).set_z_index(10)
        return queue_mob, s, pi, time

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

    def highlight_and_indicate_code(self, lines: list, **kwargs):
        highlight, indicate = highlight_code_lines(self.rendered_code, lines, **kwargs)
        self.play(highlight)
        self.play(indicate)


class RecursiveDFSMainExamp(RecursiveDFSScene):
    def __init__(self, **kwargs):
        vertices = copy(MAIN_GRAPH_EXAMPLE_VERTICES)
        edges = MAIN_GRAPH_EXAMPLE_EDGES
        start_vertex = 1
        vertices_locations = MAIN_GRAPH_EXAMPLE_VERTICES_LOC
        priority_lst = [1, 2, 4, 5, 3, 6, 7]
        super().__init__(vertices, edges, start_vertex, layout=vertices_locations, directed_graph=True,
                         priority_lst=priority_lst, **kwargs)

    def construct(self):
        self.next_section("DFS Example", pst.NORMAL)
        self.play(Write(self.rendered_code))
        self.play(Write(self.graph))
        self.pi.at(0, "-")
        self.play(Write(self.queue_mob), Write(self.u), Write(self.pi), Write(self.time))

        self.animate_recursive_dfs()
        self.play(highlight_code_lines(self.rendered_code, indicate=False))
        self.next_section("DFS finished", pst.SUB_NORMAL)
        self.play(Unwrite(self.graph), Unwrite(self.mobjects_garbage_collector))
        self.play(Unwrite(VGroup(self.queue_mob, self.u, self.pi, self.time)))
        self.play(Uncreate(self.rendered_code))
        self.wait()


class FastDFS(SectionsScene):
    def __init__(self, vertices, edges, layout, directed_graph=False, start_vertex=0, **kwargs):
        self.vertices = vertices
        self.edges = edges
        self.layout = layout
        self.start_vertex = start_vertex
        self.directed_graph = directed_graph
        self.graph = create_graph(self.vertices, self.edges, self.layout, directed_graph=directed_graph,
                                  graph_type=DiGraph, absolute_scale_vertices=True, labels=False).scale_to_fit_height(
            config.frame_height * 0.9).move_to(ORIGIN)
        self.mobjects_garbage_collector = VGroup()
        super().__init__(**kwargs)

    def animate_fast_recursive_dfs(self, run_time=0.5):
        """
        Animate DFS algorithm. We assume that the graph is connected.
        Else, we need to run BFS for each connected component.
        Each step of the algorithm is animated separately.
        Note: vertices are 1-indexed.
        """
        graph = self.graph
        dist = [np.Inf] * (len(graph.vertices) + 1)
        dist[self.start_vertex] = 0
        parent = [None] * (len(graph.vertices) + 1)

        def dfs(start_vertex):
            if start_vertex != self.start_vertex:
                self.visit_vertex_animation(graph, parent[start_vertex], start_vertex, run_time=run_time)
            else:
                self.visit_vertex_animation(graph, None, start_vertex)

            for neighbor in get_neighbors(graph, start_vertex):
                if dist[neighbor] != np.Inf:
                    continue
                dist[neighbor] = dist[start_vertex] + 1
                # animate π[v] ← s
                parent[neighbor] = start_vertex
                dfs(neighbor)

        dfs(self.start_vertex)

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


class DFSBigGraph(FastDFS):
    def __init__(self, **kwargs):
        vertices, edges, layout = get_big_triangle_graph(10)
        super().__init__(vertices, edges, layout, **kwargs)

    def construct(self):
        self.next_section("DFS Big Example", pst.NORMAL)
        self.play(Write(self.graph))
        self.next_section("Show DFS")
        self.animate_fast_recursive_dfs(0.3)
        self.next_section("DFS done")
        self.play(Unwrite(self.graph), Unwrite(self.mobjects_garbage_collector))
        self.wait(1)


if __name__ == "__main__":
    scenes_lst = [RecursiveDFSMainExamp, DFSBigGraph]

    run_scenes(scenes_lst, OUT_DIR, PRESENTATION_MODE, DISABLE_CACHING, gif_scenes=[28 + i for i in range(6)],
               create_gif=False)
