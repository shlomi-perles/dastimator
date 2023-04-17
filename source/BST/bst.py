from __future__ import annotations

from typing import Hashable

from manim_editor import PresentationSectionType as pst

from tools.array import *
from tools.consts import *
from tools.funcs import *
from tools.my_graphs import DiGraph

ROOT_PATH = Path(__file__).resolve().parent.parent
sys.path.append(str(ROOT_PATH.parent.parent))
OUT_DIR = MEDIA_PATH / Path(__file__).stem

PRESENTATION_MODE = False
DISABLE_CACHING = False
config.background_color = BACKGROUND_COLOR

# ----------------------------------    trees    ---------------------------------- #
LAYOUT_CONFIG = {"vertex_spacing": (1, 1.2)}

BASE_TREE_VERTICES = [10, 13, 14, 20, 23, 25, 26, 28, 31, "31", 34]
BASE_TREE_EDGES = [(10, 13), (10, 14), (14, 20), (14, 23), (23, 31), (31, 25), (25, 28), (28, 26), (31, "31"),
                   ("31", 34)]


# ----------------------------------    BST scenes   ---------------------------------- #

class BST(Scene):
    def __init__(self, vertices: list[Hashable], edges: list[tuple[Hashable, Hashable]], root=1, **kwargs):
        super().__init__(**kwargs)
        self.vertices = vertices
        self.edges = edges
        self.root = root
        self.graph = self.create_graph()
        self.mobjects_garbage_collector = VGroup()

    def my_next_section(self, name: str = "unnamed", type: str = pst.SUB_NORMAL, skip_animations: bool = False):
        if PRESENTATION_MODE:
            self.next_section(name, type, skip_animations)
        else:
            self.wait()

    def construct(self):
        self.my_next_section("BST", pst.NORMAL)
        self.play(Write(self.graph))

        self.introduce_tree_properties()

    def introduce_tree_properties(self):
        return

    def create_graph(self):
        """
        Create graph and add labels to vertices,
        Note: vertices are 1-indexed
        """
        # if not self.directed_graph:
        #     self.edges += [(v, u) for u, v in self.edges]

        edge_config = EDGE_CONFIG
        graph = Graph(self.vertices, self.edges, layout="tree", layout_scale=1.5, labels=True,
                      label_fill_color=LABEL_COLOR, vertex_config=VERTEX_CONFIG, edge_config=edge_config,
                      root_vertex=self.root, layout_config=LAYOUT_CONFIG)

        for i, vertex in enumerate(graph.vertices):
            graph[vertex][1].scale(VERTEX_LABEL_SCALE)
        relative_scale = config.frame_width * 0.4 if graph.width > graph.height else config.frame_height * 0.7
        graph.scale_to_fit_width(relative_scale).move_to(ORIGIN).to_edge(RIGHT, buff=0.2)
        return graph


class StartBST(BST):
    def __init__(self, **kwargs):
        super().__init__(BASE_TREE_VERTICES, BASE_TREE_EDGES, root=23, **kwargs)

    def construct(self):
        super().construct()


class LargeTreeGeneration(MovingCameraScene):
    DEPTH = 4
    CHILDREN_PER_VERTEX = 2
    LAYOUT_CONFIG = {"vertex_spacing": (1, 1.2)}
    VERTEX_CONF = {"radius": 0.25, "color": BLUE_B, "fill_opacity": 1}

    def expand_vertex(self, g, vertex_id: str, depth: int):
        new_vertices = [f"{vertex_id}/{i}" for i in range(self.CHILDREN_PER_VERTEX)]
        new_edges = [(vertex_id, child_id) for child_id in new_vertices]
        g.add_edges(*new_edges, vertex_config=self.VERTEX_CONF,
                    positions={k: g.vertices[vertex_id].get_center() + 0.1 * DOWN for k in new_vertices}, )
        self.play(g.animate.change_layout("tree", root_vertex="ROOT", layout_config=self.LAYOUT_CONFIG))
        if depth < self.DEPTH:
            for child_id in new_vertices:
                self.expand_vertex(g, child_id, depth + 1)

        return g

    def construct(self):
        g = Graph(["ROOT"], [], vertex_config=self.VERTEX_CONF)
        self.add(g)
        g = self.expand_vertex(g, "ROOT", 1)

        self.play(g.animate.change_layout("tree", root_vertex="ROOT", layout_config=self.LAYOUT_CONFIG))
        self.play(self.camera.auto_zoom(g, margin=1), run_time=0.5)


if __name__ == "__main__":
    scenes_lst = [StartBST]

    run_scenes(scenes_lst, OUT_DIR, PRESENTATION_MODE, DISABLE_CACHING, gif_scenes=[28 + i for i in range(6)])
