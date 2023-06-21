from __future__ import annotations

from tools.scenes import *
from tools.graphs.edge import *
from tools.graphs.node import IndicateNode
from tools.graphs.utils import get_vertices_cut
from mst_utils import *

ROOT_PATH = Path(__file__).resolve().parent
sys.path.append(str(ROOT_PATH.parent))
OUT_DIR = MEDIA_PATH / Path(__file__).resolve().parent.stem

PRESENTATION_MODE = True
DISABLE_CACHING = False

# --------------------------------- constants --------------------------------- #

KRUSKAL_UNION_PSEUDO_CODE = r'''def Kruskal($G=\left(V,E,w\right)$):
    for $v\in V$:
        MakeSet($v$)
    sort $E$ into $e_{1},e_{2},\ldots,e_{m}$ by weight
    $E'\leftarrow\emptyset$
    
    for $e_{i}=(u_{i},v_{i})\in E$:
        if FindSet($u_{i}$) $\neq$ FindSet($v_{i}$):
            $E'\leftarrow E'\cup\left\{ e_{i}\right\} $
            Union($u_{i},v_{i}$)
    return $(V,E')$'''
# KRUSKAL_UNION_PSEUDO_CODE = r'''def Kruskal:
#     abc $G$'''
DEFAULT_NODE_INDICATE_COLOR = "yellow"
VERTICES_SMALL_EXAMPLE = [1, 2, 3, 4]
EDGES_SMALL_EXAMPLE = [(1, 2), (1, 3), (1, 4), (2, 3), (3, 4)]
WEIGHTS_SMALL_EXAMPLE = {(1, 2): -1, (1, 3): 2, (1, 4): 6, (2, 3): 2, (3, 4): 4}


def get_edges_lst(graph: WeightedGraph, edge_len: float = 1, node_radius: float = 0.2,
                  directed: bool = False) -> VGroup:
    edges_lst = VGroup()
    add_edges = set()
    for (u, v), edge in graph.edges.items():
        if edge.weight is None or (not directed and ((v, u) in add_edges)):
            continue
        if not directed and graph.vertices[u].get_x() > graph.vertices[v].get_x():
            continue
        add_edges.add((u, v))
        start_node = Node(u).scale_to_fit_width(node_radius * 2)
        end_node = Node(v).scale_to_fit_width(node_radius * 2).shift(edge_len * RIGHT)
        edge_mob = Edge(start_node, end_node, weight=edge.weight, color=EDGE_COLOR, stroke_width=7)
        edge_mob.weight_mob.scale_to_fit_width(node_radius * 3 / 2).set_stroke_width(0)
        edges_lst += VGroup(edge_mob, start_node, end_node)

    return edges_lst.arrange_in_grid(buff=(0.5, 0.3), rows=3).scale_to_fit_width(
        (config.frame_width - graph.width) * 0.80)


class Intro(SectionsScene):
    def construct(self):
        self.next_section("Intro", pst.NORMAL)
        title = Title("Minimum Spanning Tree")
        overview = Tex(r'''Overview:
            \begin{itemize}
                \item[$\bullet$] MST
                \begin{itemize}
                    \item Kruskal's Algorithm - $O\left(\left|E\right|\log\left|E\right|\right)$
                    \item Prim's Algorithm - $O\left(\left(\left|E\right|+\left|V\right|\right)\log\left|V\right|\right)$
                \end{itemize}
                \item[$\bullet$] MST Questions
            \end{itemize}''', tex_environment=r"{minipage}{9.3cm}")
        color_tex(overview, t2c={"Kruskal": YELLOW, "Prim": YELLOW, "MST": GREEN, "Questions": GREEN})
        remark = Text(r"Remark: Today's graphs are all Undirected, Connected and Weighted.", t2w={"Undirected": BOLD,
                                                                                                  "Connected": BOLD,
                                                                                                  "Weighted": BOLD},
                      t2c={
                          "Undirected": BLUE, "Connected": BLUE, "Weighted": BLUE})
        remark.match_width(overview).to_edge(DOWN)

        self.play(Write(title))
        self.play(Write(overview))
        self.next_section("remark")
        self.play(Write(remark))
        self.next_section("End")
        self.play(Unwrite(title), Unwrite(overview), Unwrite(remark))
        self.wait()


class WeightedGraphDefinition(SectionsScene):
    def construct(self):
        self.next_section("Weighted Graphs", pst.NORMAL)
        title = Title("Weighted Graph")
        definition = Tex(r'''A \textbf{weighted graph} is a graph $G=\left(V,E\right)$
        together\\ with a weight function $w:E\rightarrow\mathbb{R}$.''', tex_environment=DEFINITION_TEX_ENV).next_to(
            title, DOWN, buff=0.5)
        color_tex(definition,
                  t2c={r"\textbf{weighted graph}": YELLOW, r"$w:E\rightarrow\mathbb{R}$": BLUE})
        self.play(Write(title))
        self.play(Write(definition))

        self.next_section("Example")
        weight_format_str = r"\ w{0}={1}"
        example = Tex(
            rf'''Example: $V=\left\{'{'}{', '.join(map(str, VERTICES_SMALL_EXAMPLE))}\right\{'}'}$,
            $E=\left\{'{'}{', '.join(map(str, EDGES_SMALL_EXAMPLE))}\right\{'}'}$)\\
            ${', '.join(map(lambda x: weight_format_str.format(x, WEIGHTS_SMALL_EXAMPLE[x]), WEIGHTS_SMALL_EXAMPLE))}$''',
            tex_environment="flushleft").match_width(definition).next_to(definition, DOWN, buff=0.5)
        graph = create_graph(VERTICES_SMALL_EXAMPLE, EDGES_SMALL_EXAMPLE, graph_type=WeightedGraph,
                             weights=WEIGHTS_SMALL_EXAMPLE,
                             absolute_scale_vertices=True, layout="circular").scale(0.6).next_to(example, DOWN,
                                                                                                 buff=0.2)
        self.play(Write(example))
        self.play(Write(graph))
        self.next_section("End")
        graph.remove_updater(graph.update_edges)
        self.play(Unwrite(title), Unwrite(definition), Unwrite(example), Unwrite(graph))
        self.wait()


class MSTDefinition(SectionsScene):
    def construct(self):
        self.next_section("MST Definition", pst.NORMAL)
        title = Title("Minimum Spanning Tree")
        spanning_tree_def = Tex(r'''Let $G=\left(V,E\right)$ be a undirected and connected graph. A subgraph $T \subseteq G$
        is called a $\textbf{spanning tree}$ if $T$ is a tree and $V_{T}=V$.''', tex_environment=DEFINITION_TEX_ENV)
        spanning_tree_def.next_to(title, DOWN, buff=0.5)
        color_tex(spanning_tree_def, t2c={r"\textbf{spanning tree}": YELLOW})
        color_tex(spanning_tree_def, t2c={r"T": GREEN}, tex_class=MathTex)
        self.play(Write(title))
        self.play(Write(spanning_tree_def))

        self.next_section("Spanning Tree Example")
        example = Tex(r'''Example:''').next_to(spanning_tree_def, DOWN, buff=0.5).align_to(spanning_tree_def, LEFT)
        graph = create_graph(VERTICES_SMALL_EXAMPLE, EDGES_SMALL_EXAMPLE, absolute_scale_vertices=True,
                             graph_type=WeightedGraph, layout="circular").scale(0.7).move_to(ORIGIN).to_edge(DOWN)
        graph.remove_updater(graph.update_edges)
        self.play(Write(example))
        self.play(Write(graph))
        spanning_edges = [(2, 1), (1, 4), (4, 3)]
        self.play(AnimationGroup(*[graph.edges[edge].animate_move_along_path(**MST_PATH_PARAMS) for edge in
                                   spanning_edges],
                                 lag_ratio=0.5))

        self.next_section("Spanning Tree Example")
        self.play(Unwrite(spanning_tree_def), Unwrite(example), Unwrite(graph))
        mst_def = Tex(r'''Let $G=\left(V,E,w\right)$ be a undirected, connected and weighted graph. 
                    A spanning tree $T$ is called a $\textbf{minimum spanning tree}$ (MST) if
                    $w\left(T\right)\leq w\left(T’\right)$ for every spanning tree $T’$ in $G$.''',
                      tex_environment=DEFINITION_TEX_ENV).next_to(title, DOWN, buff=0.5)
        color_tex(mst_def, t2c={r"\textbf{minimum spanning tree}": YELLOW})
        color_tex(mst_def, t2c={r"T": GREEN}, tex_class=MathTex)
        color_tex(mst_def, t2c={"$T’$": WHITE})
        self.play(Write(mst_def))

        self.next_section("MST Example")
        example = Tex(r'''Example:''').next_to(mst_def, DOWN, buff=0.5).align_to(mst_def, LEFT)
        tree_weight = MathTex(fr"w\left(T\right)\ =\ ", "9").next_to(graph, UP + RIGHT, buff=0.3).move_to(ORIGIN)
        graph = create_graph(VERTICES_SMALL_EXAMPLE, EDGES_SMALL_EXAMPLE, absolute_scale_vertices=True,
                             weights=WEIGHTS_SMALL_EXAMPLE, graph_type=WeightedGraph, layout="circular").scale(
            0.7).next_to(tree_weight, RIGHT).to_edge(DOWN, buff=0.1)
        tree_weight.match_y(graph).shift(LEFT)
        graph.remove_updater(graph.update_edges)
        self.play(Write(example))
        self.play(Write(graph))
        self.play(AnimationGroup(*[graph.edges[edge].animate_move_along_path(**MST_PATH_PARAMS) for edge in
                                   spanning_edges],
                                 lag_ratio=0.5))
        self.play(Write(tree_weight))

        self.next_section("MST Example")
        self.play(graph.edges[(1, 4)].animate_move_along_path(
            **{"time_width": PATH_TIME_WIDTH * 0.1, "flash_color": EDGE_COLOR, **MST_PATH_PARAMS}),
            graph.edges[(3, 1)].animate_move_along_path(**MST_PATH_PARAMS))
        new_tree_weight = MathTex(fr"5").next_to(graph, UP + RIGHT, buff=0.3).move_to(
            tree_weight[1]).align_to(tree_weight[1], LEFT)
        self.play(ReplacementTransform(tree_weight[1], new_tree_weight))

        self.next_section("MST Example")
        self.play(graph.edges[(3, 1)].animate_move_along_path(
            **{"time_width": PATH_TIME_WIDTH * 0.1, "flash_color": EDGE_COLOR, **MST_PATH_PARAMS}),
            graph.edges[(3, 2)].animate_move_along_path(**MST_PATH_PARAMS))
        self.next_section("End")
        self.play(Unwrite(title), Unwrite(mst_def), Unwrite(example), Unwrite(graph), Unwrite(tree_weight))
        self.wait()


class TheCutLemma(SectionsScene):
    def construct(self):
        self.next_section("The Cut Lemma", pst.NORMAL)
        title = Title("The Cut Lemma")
        cut_def = Tex(r'''Let $G=\left(V,E,w\right)$ be graph and $U\subseteq V$. The $\textbf{cut}$ defined by $U$ is
        \[ C\left(U\right)=\left\{\left(u,v\right)\in E\mid u\in U, v\notin U\right\} \]''',
                      tex_environment=DEFINITION_TEX_ENV)
        cut_def.next_to(title, DOWN, buff=0.5)
        color_tex(cut_def, t2c={r"\textbf{cut}": RED})
        color_tex(cut_def, t2c={r"U": GREEN, "C": RED}, tex_class=MathTex)
        self.play(Write(title))
        self.play(Write(cut_def))

        self.next_section("Cut Example")
        example = Tex(r'Example: $U=$', r"$\left\{1\right\}$").next_to(cut_def, DOWN, buff=0.5).align_to(cut_def, LEFT)
        color_tex(example, t2c={r"U": GREEN}, tex_class=MathTex)
        graph = create_graph(VERTICES_SMALL_EXAMPLE, EDGES_SMALL_EXAMPLE, absolute_scale_vertices=True,
                             graph_type=WeightedGraph, layout="circular").scale(0.6).move_to(ORIGIN).to_edge(DOWN,
                                                                                                             buff=0.2)
        graph.remove_updater(graph.update_edges)

        self.play(Write(example))
        self.play(Write(graph))
        self.next_section("Cut Example")
        cut = [1]
        cut_mob = get_vertices_cut(graph, cut, **DEFAULT_CUT_PARAMS).set_z_index(-5)
        self.play(Write(cut_mob))
        self.next_section("Cut Example")
        self.draw_edges_in_cut(graph, cut, RED)

        self.next_section("Cut Example")
        self.play(Unwrite(cut_mob))
        self.draw_edges_in_cut(graph, cut, EDGE_COLOR)
        cut = [1, 3]
        new_cut_mob = SurroundingRectangle(VGroup(graph.vertices[1], graph.vertices[3]), buff=0.4, **DEFAULT_CUT_PARAMS,
                                           corner_radius=0.3).set_z_index(-5)
        self.play(ReplacementTransform(cut_mob, new_cut_mob))
        cut_tex = Tex(r"$\left\{1,3\right\}$").move_to(example[1]).align_to(example[1], LEFT)
        self.play(ReplacementTransform(example[1], cut_tex))
        self.next_section("Cut Example")
        self.draw_edges_in_cut(graph, cut, RED)
        self.next_section("End")

        self.play(Unwrite(cut_def), Unwrite(example), Unwrite(graph), Unwrite(cut_tex), Unwrite(new_cut_mob))

        the_cut_lemma = Tex(r'''Theorem: Let $G=\left(V,E,w\right)$ be a graph and $C\left(U\right)$ be a cut.
        Let $F \subseteq E$ be a forest such that there exists an MST $T$ with $F\subseteq T$ and $F\cap C=\emptyset$.
        Let $e\in C$ be an edge with minimal weight. Then there exists an MST $T’$ such that $F\cup\left\{e\right\}\subseteq T’$.''',
                            tex_environment="{minipage}{9cm}").next_to(title, DOWN, buff=0.5)
        color_tex(the_cut_lemma, t2c={r"C": RED, "T": YELLOW, "e": BLUE, "F": ORANGE, "U": GREEN}, tex_class=MathTex)
        color_tex(the_cut_lemma, t2c={"$T’$": WHITE})
        self.play(Write(the_cut_lemma))

        self.next_section("Example:")
        example_tex = Tex(r"Example:").next_to(the_cut_lemma, DOWN, buff=0.5).align_to(the_cut_lemma, LEFT)
        graph = create_graph(VERTICES_SMALL_EXAMPLE, EDGES_SMALL_EXAMPLE, absolute_scale_vertices=True,
                             weights=WEIGHTS_SMALL_EXAMPLE,
                             graph_type=WeightedGraph, layout="circular").scale(0.6).move_to(ORIGIN).to_edge(DOWN)
        graph.remove_updater(graph.update_edges)
        cut = [1, 3]
        new_cut_mob = SurroundingRectangle(VGroup(graph.vertices[1], graph.vertices[3]), buff=0.4, **DEFAULT_CUT_PARAMS,
                                           corner_radius=0.3).set_z_index(-5)
        self.play(Write(example_tex), Write(graph))
        self.play(Write(new_cut_mob))
        self.play(AnimationGroup(
            AnimationGroup(graph.edges[(3, 1)].animate_move_along_path(width_factor=EDGE_TREE_PATH_WIDTH_FACTOR,
                                                                       time_width=PATH_TIME_WIDTH * 2,
                                                                       flash_color=ORANGE, preserve_state=True),
                           graph.edges[(1, 3)].animate_move_along_path(width_factor=EDGE_TREE_PATH_WIDTH_FACTOR,
                                                                       time_width=PATH_TIME_WIDTH * 2,
                                                                       flash_color=ORANGE, preserve_state=True,
                                                                       opposite_direction=True)), lag_ratio=0.5))
        self.next_section("minimum edge")
        self.play(AnimationGroup(
            AnimationGroup(graph.edges[(1, 2)].animate_move_along_path(width_factor=EDGE_TREE_PATH_WIDTH_FACTOR,
                                                                       time_width=PATH_TIME_WIDTH * 2,
                                                                       flash_color=BLUE, preserve_state=True),
                           graph.edges[(2, 1)].animate_move_along_path(width_factor=EDGE_TREE_PATH_WIDTH_FACTOR,
                                                                       time_width=PATH_TIME_WIDTH * 2,
                                                                       flash_color=BLUE, preserve_state=True,
                                                                       opposite_direction=True)), lag_ratio=0.5))
        self.next_section("End")
        self.play(Unwrite(title), Unwrite(example_tex), Unwrite(graph), Unwrite(new_cut_mob), Unwrite(the_cut_lemma))
        self.wait()

    def draw_edges_in_cut(self, graph, cut, color):
        edges_in_cut = [graph.edges[edge] for edge in graph.edges if (edge[0] in cut) and (edge[1] not in cut)]
        oposite_cut = [graph.edges[edge[::-1]] for edge in graph.edges if (edge[0] in cut) and (edge[1] not in cut)]
        self.play(AnimationGroup(
            *[AnimationGroup(edges_in_cut[i].animate_move_along_path(width_factor=EDGE_TREE_PATH_WIDTH_FACTOR,
                                                                     time_width=PATH_TIME_WIDTH * 2,
                                                                     flash_color=color, preserve_state=True),
                             oposite_cut[i].animate_move_along_path(width_factor=EDGE_TREE_PATH_WIDTH_FACTOR,
                                                                    time_width=PATH_TIME_WIDTH * 2,
                                                                    flash_color=color, preserve_state=True,
                                                                    opposite_direction=True)) for i in
              range(len(edges_in_cut))], lag_ratio=0.5))


class KruskalUnion(SectionsScene):
    def __init__(self, graph, **kwargs):
        self.graph = graph.scale(0.94).to_edge(RIGHT, buff=0.7)
        self.graph.remove_updater(self.graph.update_edges)
        self.code = create_code(KRUSKAL_UNION_PSEUDO_CODE, line_no_buff=0.6).scale_to_fit_width(
            config.frame_width * 0.47).to_corner(LEFT + UP)
        self.edges_lst = get_edges_lst(self.graph).match_width(self.code).to_corner(LEFT + DOWN)
        # self.code = Rectangle()
        self.board_width = (config.frame_width - graph.width) * 0.80
        super().__init__(**kwargs)

    def sort_edges(self, **kwargs) -> AnimationGroup:
        self.edges_lst.sort(submob_func=lambda x: x[0].weight)
        return self.edges_lst.animate.arrange_in_grid(buff=(0.5, 0.3), rows=3)

    def kruskal(self, **kwargs):
        self.add(self.code)
        find_mst = False
        vertices = self.graph.vertices

        cuts_to_vertices, vertices_to_cuts = {}, {}
        self.next_section("MakeSet")
        anims = []
        for i in vertices:
            cut = self.get_cut([i])
            cuts_to_vertices[cut] = {i}
            vertices_to_cuts[i] = cut
            anims.append(FadeIn(VGroup(cut)))
        self.highlight_and_indicate_code([2, 3])
        self.play(AnimationGroup(*anims, run_time=2, lag_ratio=0.5))

        self.next_section("Sort edges")
        self.highlight_and_indicate_code([4])
        self.next_section("Sort visu")
        self.play(self.sort_edges())

        self.next_section("Initialize MST")
        mst_list = []
        self.highlight_and_indicate_code([5])
        edges = [edge for edge in self.edges_lst]
        for edge in edges:
            self.next_section("Get edge", skip_section=find_mst)
            u_node, v_node = edge[0].start, edge[0].end
            u, v = u_node.key, v_node.key
            self.highlight_and_indicate_code([7])
            self.edges_lst.remove(edge)
            self.play(edge.animate.next_to(self.code, DOWN, buff=0).set_y(
                self.code.get_bottom()[1] - (self.code.get_bottom() - self.edges_lst.get_top())[
                    1] / 2).scale_to_fit_width(self.board_width * 0.7))

            self.next_section("Find set", skip_section=find_mst)
            self.highlight_and_indicate_code([8])
            self.next_section("Find set visu", skip_section=find_mst)
            self.play(IndicateNode(u_node, color_theme=DEFAULT_NODE_INDICATE_COLOR, preserve_indicate_color=True),
                      IndicateNode(v_node, color=DEFAULT_NODE_INDICATE_COLOR, preserve_indicate_color=True),
                      IndicateNode(vertices[u], color=DEFAULT_NODE_INDICATE_COLOR, preserve_indicate_color=True),
                      IndicateNode(vertices[v], color=DEFAULT_NODE_INDICATE_COLOR, preserve_indicate_color=True))

            cut_u, cut_v = vertices_to_cuts[u], vertices_to_cuts[v]

            if cut_u != cut_v:
                self.next_section("Add edge", skip_section=find_mst)
                self.highlight_and_indicate_code([9])
                self.next_section("Add edge visu", skip_section=find_mst)
                self.play(*self.add_mst_edge(u, v))

                self.next_section("Union", skip_section=find_mst)
                self.highlight_and_indicate_code([10])
                self.next_section("Union visu", skip_section=find_mst)
                new_cut_vertices = cuts_to_vertices[cut_u] | cuts_to_vertices[cut_v]
                cut = self.get_cut(list(new_cut_vertices))
                cuts_to_vertices[cut] = new_cut_vertices
                for vertex in new_cut_vertices:
                    vertices_to_cuts[vertex] = cut
                self.play(ReplacementTransform(VGroup(cut_u, cut_v), cut))

                mst_list.append(edge)
            self.next_section("Remove preview edge", skip_section=find_mst)
            self.play(FadeOut(edge),
                      IndicateNode(vertices[u], color_theme="blue", preserve_indicate_color=True, scale_factor=1),
                      IndicateNode(vertices[v], color_theme="blue", preserve_indicate_color=True, scale_factor=1))
            if len(mst_list) == len(vertices) - 1:
                find_mst = True
            # if u == 5 or v == 5:
            # return
        # self.play(self.sort_edges())
        self.play(FadeOut(vertices_to_cuts[1]))
        self.play(highlight_code_lines(self.code, list(range(1, 12)), indicate=False))

    def add_mst_edge(self, u, v):
        anim1, anim2 = self.graph.edges[(u, v)].animate_move_along_path(**MST_PATH_PARAMS), self.graph.edges[
            (v, u)].animate_move_along_path(
            **{"opposite_direction": True, **MST_PATH_PARAMS})
        return anim1, anim2

    def highlight_and_indicate_code(self, lines: list, **kwargs):  # TODO: implement code scene
        highlight, indicate = highlight_code_lines(self.code, lines, **kwargs)
        self.play(highlight, run_time=0.2)
        self.play(indicate, run_time=0.6)

    def find_circle_in_union(self, u, v, **kwargs):
        pass

    def get_cut(self, vertices: list[Hashable], **kwargs) -> Polygon:
        return get_vertices_cut(self.graph, vertices, **{**kwargs, **DEFAULT_CUT_PARAMS}).set_z_index(-1)


class KruskalUnionExample(KruskalUnion):
    def __init__(self, **kwargs):
        super().__init__(get_main_graph_example(), **kwargs)

    def construct(self):
        self.next_section("Kruskal Example", pst.NORMAL)
        # self.add(self.graph, self.code)
        # self.wait()
        self.play(Write(self.code), Write(self.graph))
        self.play(Write(self.edges_lst))

        # explain, explain_anim = code_explain(self.code, [8, 9, 10], "Find circle")
        # self.play(explain_anim)

        self.kruskal()
        self.wait()
        return


class KruskalComplexity(KruskalUnion):
    def __init__(self, **kwargs):
        super().__init__(get_main_graph_example(), **kwargs)

    def construct(self):
        self.add(self.graph, self.code)
        self.next_section("Kruskal Complexity", pst.NORMAL)
        union_find_reminder = Tex(r'''Reminder:

                    FindSet($v$) = $O\left(\alpha\left(n\right)\right)$ (inverse Ackermann
                    function)
                    
                    Union($v$,$u$) = $O\left(\alpha\left(n\right)\right)$ ''', tex_environment="flushleft").next_to(
            self.code, DOWN, buff=0.7).match_width(self.code)
        ackerman_aprox = MathTex(r'''O\left(\alpha\left(n\right)\right)\approx O\left(1\right)''').next_to(
            union_find_reminder, DOWN)
        self.play(Write(union_find_reminder))
        self.play(Write(ackerman_aprox))
        self.next_section("sort")
        self.play(Unwrite(union_find_reminder), Unwrite(ackerman_aprox))
        self.highlight_and_indicate_code([4])
        total_complexity = MathTex(r"\left|E\right|\log\left|E\right|", r"\left|E\right|", arg_separator="+").move_to(
            ackerman_aprox).match_width(ackerman_aprox)
        self.play(Write(total_complexity[0]))

        self.next_section("union")
        self.highlight_and_indicate_code([7, 8, 9, 10])
        self.play(Write(total_complexity[1:]))

        self.next_section("total complexity")
        final_complexity = MathTex(r"\left|E\right|\log\left|E\right|").move_to(total_complexity).match_width(
            total_complexity)
        self.play(TransformMatchingTex(total_complexity, final_complexity))
        self.next_section("end")
        self.play(Unwrite(final_complexity), Unwrite(self.code), Unwrite(self.graph))
        self.wait()


if __name__ == "__main__":
    scenes_lst = [Intro, WeightedGraphDefinition, MSTDefinition, TheCutLemma, KruskalUnionExample, KruskalComplexity]

    run_scenes(scenes_lst, OUT_DIR, PRESENTATION_MODE, DISABLE_CACHING, gif_scenes=[28 + i for i in range(6)],
               create_gif=False)
