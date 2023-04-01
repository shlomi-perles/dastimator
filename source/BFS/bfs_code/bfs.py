from tools.consts import *
from tools.funcs import *
from pathlib import Path
from bfs_tools import *
from manim_editor import PresentationSectionType as pst
from typing import Callable, Iterable, List, Optional, Sequence, Union

MAIN_PATH = Path(__file__).resolve().parent.parent
sys.path.append(str(MAIN_PATH.parent.parent))

PRESENTATION_MODE = False
DISABLE_CACHING = False
config.background_color = BACKGROUND_COLOR

# --------------------------------- constants --------------------------------- #
VERTEX_COLOR = DARK_BLUE
VERTEX_STROKE_WIDTH = DEFAULT_STROKE_WIDTH * 1.6
VERTEX_STROKE_COLOR = BLUE_D

EDGE_COLOR = GREY
EDGE_STROKE_WIDTH = DEFAULT_STROKE_WIDTH * 2

VISITED_COLOR = PURE_GREEN
VISITED_EDGE_WIDTH = EDGE_STROKE_WIDTH * 1.5
VISITED_VERTEX_WIDTH = VERTEX_STROKE_WIDTH * 1.8
LABEL_COLOR = WHITE

LINES_OPACITY = 0.5


def get_neighbors(graph: Graph, vertex):
    return [neighbor for neighbor in graph.vertices if (vertex, neighbor) in graph.edges]


# --------------------------------- BFS --------------------------------- #

class BFSScene(Scene):
    def __init__(self, vertices: Iterable, edges: Iterable[tuple], start_vertex=1, **kwargs):
        super().__init__(**kwargs)
        self.vertices = vertices
        self.edges = edges
        self.start_vertex = start_vertex

    def my_next_section(self, name: str = "unnamed", type: str = pst.SUB_NORMAL, skip_animations: bool = False):
        if PRESENTATION_MODE:
            self.next_section(name, type, skip_animations)
        else:
            self.wait()

    def construct(self):
        self.my_next_section("BFS", pst.NORMAL)
        graph = self.create_graph()
        rendered_code = self.create_code()
        queue_mob, u, pi = self.create_bfs_vars(rendered_code)

        self.play(Write(rendered_code))
        self.play(Write(graph))

        self.animate_bfs(graph, rendered_code, queue_mob, u, pi)

        self.play(highlight_code_lines(rendered_code))
        self.play(Unwrite(VGroup(graph, rendered_code, queue_mob, u)))
        self.wait()

    def animate_bfs(self, graph: Graph, rendered_code: Code, queue_mob: ArrayMob, u: Tex, pi: ArrayMob):
        """
        Animate BFS algorithm. We assume that the graph is connected. Else, we need to run BFS for each connected component.
        Each step of the algorithm is animated separately.
        :param graph: Graph to animate
        :param rendered_code: Code to animate
        :param queue_mob: ArrayMob of queue
        :param u: VGroup of u mob
        :param pi: ArrayMob of pi
        """
        dist = [np.Inf] * (len(graph.vertices) + 1)
        dist[self.start_vertex] = 0
        parent = [None] * (len(graph.vertices) + 1)
        queue = [self.start_vertex]

        self.play(queue_mob.draw_array(), Write(u), pi.draw_array())

        while queue:
            self.play(highlight_code_lines(rendered_code, [9]))

            # animate pop
            cur_vertex = queue.pop(0)
            self.my_next_section(f"Pop vertex {cur_vertex} from queue", pst.SUB_NORMAL)
            self.play(highlight_code_lines(rendered_code, [10]))
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
                self.my_next_section("Visit neighbor", pst.SUB_NORMAL)
                self.play(highlight_code_lines(rendered_code, [11]))
                self.my_next_section("Update visit", pst.SUB_NORMAL)
                self.visit_vertex_animation(graph, cur_vertex, neighbor)

                # animate π[v] ← u
                parent[neighbor] = cur_vertex
                self.my_next_section(f"Add parent {cur_vertex} to vertex {neighbor}", pst.SUB_NORMAL)
                self.play(highlight_code_lines(rendered_code, [12]))
                self.my_next_section("Update parent", pst.SUB_NORMAL)
                self.play(pi.at(neighbor - 1, cur_vertex))

                # animate dist[v] = dist[u] + 1
                dist[neighbor] = dist[cur_vertex] + 1
                self.my_next_section(f"Set distance {dist[cur_vertex] + 1} to vertex {neighbor}", pst.SUB_NORMAL)
                self.play(highlight_code_lines(rendered_code, [13]))

                # animate queue.push(v)
                queue.append(neighbor)
                self.my_next_section(f"Add vertex {neighbor} to queue", pst.SUB_NORMAL)
                self.play(highlight_code_lines(rendered_code, [14]))
                self.play(queue_mob.push(neighbor))
            self.play(pop_animation[0])

    def visit_vertex_animation(self, graph: Graph, parent, next_vertex):
        visited_mark = Circle(radius=graph[next_vertex].radius, fill_opacity=0, stroke_width=VISITED_VERTEX_WIDTH,
                              stroke_color=VISITED_COLOR).move_to(graph[next_vertex]).scale_to_fit_height(
            graph[next_vertex].height)
        if parent is not None:
            visited_mark.rotate(graph.edges[(parent, next_vertex)].get_angle() + PI)
            self.play(graph.animate.add_edges((parent, next_vertex), edge_config={"stroke_color": VISITED_COLOR,
                                                                                  "stroke_width": VISITED_EDGE_WIDTH}))
        self.play(Create(visited_mark))

    def create_code(self):
        code = '''def BFS(G,s): 
    for all vertices u in V do:
        dist[u] ← ∞
        
    dist[s] ← 0
    π[s] ← None
    queue ← Build Queue({s})
     
    while queue ≠ ø do:
        u = queue.pop() 
        for neighbor v of u & dist[v] = ∞:
                π[v] ← u
                dist[v] = dist[u] + 1
                queue.push(v)'''
        Code.set_default(font="Consolas")
        rendered_code = Code(code=code, tab_width=3, background="window", language="Python", style="fruity").to_corner(
            LEFT + UP)
        rendered_code.scale_to_fit_width(config.frame_width * 0.5).to_corner(LEFT + UP)
        return rendered_code

    def create_graph(self):
        self.edges += [(v, u) for u, v in self.edges]
        vertex_config = {
            "fill_color": VERTEX_COLOR,
            "stroke_color": VERTEX_STROKE_COLOR,
            "stroke_width": VERTEX_STROKE_WIDTH
        }
        edge_config = {
            "stroke_color": EDGE_COLOR,
            "stroke_width": EDGE_STROKE_WIDTH
        }
        graph = Graph(self.vertices, self.edges, layout="circular", layout_scale=1.5,
                      labels=True, label_fill_color=LABEL_COLOR, vertex_config=vertex_config, edge_config=edge_config)
        relative_scale = config.frame_width * 0.5 if graph.width > graph.height else config.frame_height * 0.7
        graph.scale_to_fit_width(relative_scale).to_edge(RIGHT, buff=0.2)
        return graph

    def create_bfs_vars(self, rendered_code: Code) -> tuple[ArrayMob, Tex, ArrayMob]:
        scale = 1
        queue_mob = ArrayMob("queue:", self.start_vertex, name_scale=scale).next_to(rendered_code, DOWN,
                                                                                    buff=0.5).to_edge(LEFT)

        u = Tex("u:").scale_to_fit_height(queue_mob.height_ref).next_to(queue_mob, DOWN, buff=queue_mob.get_square(
            0).height * 0.8).align_to(queue_mob.array_name, RIGHT)
        pi = ArrayMob(r"$\pi$:", *[""] * len(self.vertices), name_scale=scale, show_labels=True, labels_pos=DOWN,
                      align_point=u.get_right() + 0.5 * DOWN * (queue_mob.obj_ref.get_bottom()[1] - u.get_top()[1]),
                      starting_index=1)
        return queue_mob, u, pi


class BigGraphBFS(BFSScene):
    def __init__(self, **kwargs):
        vertices = [1, 2, 3, 4, 5, 6, 7, 8]
        edges = [(1, 7), (1, 8), (2, 3), (2, 4), (2, 5),
                 (2, 8), (3, 4), (6, 1), (6, 2), (7, 2), (7, 4), (3, 6)]
        vertices = [1, 2, 3]
        edges = [(1, 2), (1, 3), (2, 3)]
        start_vertex = 1
        super().__init__(vertices, edges, start_vertex, **kwargs)
    # def construct(self):
    #     super().construct()


if __name__ == "__main__":

    # scenes_lst = [BFSScene]
    scenes_lst = [BigGraphBFS]

    for sc in scenes_lst:
        quality = "fourk_quality" if PRESENTATION_MODE else "low_quality"

        with tempconfig({"quality": quality, "preview": True, "media_dir": MAIN_PATH / "media", "save_sections": True,
                         "disable_caching": DISABLE_CACHING}):
            scene = sc()
            scene.render()
