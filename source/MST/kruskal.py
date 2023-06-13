from __future__ import annotations

from manim_editor import PresentationSectionType as pst

from tools.consts import *
from mst_utils import *

ROOT_PATH = Path(__file__).resolve().parent
sys.path.append(str(ROOT_PATH.parent))
OUT_DIR = MEDIA_PATH / Path(__file__).resolve().parent.stem

PRESENTATION_MODE = False
DISABLE_CACHING = True

# --------------------------------- constants --------------------------------- #

KRUSKAL_UNION_PSEUDO_CODE = '''def DFS(G,s):
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


class KruskalUnionExample(SectionsScene):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def construct(self):
        self.next_section("Kruskal Example", pst.NORMAL)
        graph = get_main_graph_example()
        self.add(graph)
        self.wait()
        # self.play(graph.animate.change_layout("circular"))


if __name__ == "__main__":
    scenes_lst = [KruskalUnionExample]

    run_scenes(scenes_lst, OUT_DIR, PRESENTATION_MODE, DISABLE_CACHING, gif_scenes=[28 + i for i in range(6)],
               create_gif=False)
