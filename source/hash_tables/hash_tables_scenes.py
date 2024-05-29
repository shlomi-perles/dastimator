from __future__ import annotations

from hash_tables.hash_tables_utils import *
from tools.array import ArrayEntry, ArrayMob, ArrayPointer
from tools.consts import MEDIA_PATH, DEFINITION_TEX_ENV, REMOVE_MATH_SPACE_PREAMBLE
from tools.funcs import color_tex, get_func_text, compile_code_tex_line, get_frame_center
from tools.hash_table import HashTable
from tools.movie_maker import render_scenes
from tools.scenes import *

ROOT_PATH = Path(__file__).resolve().parent
sys.path.append(str(ROOT_PATH.parent))
OUT_DIR = MEDIA_PATH / Path(__file__).resolve().parent.stem

PRESENTATION_MODE = False
DISABLE_CACHING = False


class Intro(SectionsScene):
    def construct(self):
        self.next_section("Intro", pst.NORMAL)
        title = Title("Hash Tables - Intro")
        overview = Tex(r'''Overview:
            \begin{itemize}
                \item[$\bullet$] Hash Tables
                \item[$\bullet$] Universal Hash Families
                \begin{itemize}
                \item examples
                \end{itemize}
                \item[$\bullet$] Check Triplets Problem
                \item[$\bullet$] $k$-Universal Hash Families
            \end{itemize}''', tex_environment=r"{minipage}{9.3cm}")

        color_tex(overview, t2c={"k": K_UNIVERSAL_COLOR}, tex_class=MathTex)
        color_tex(overview, t2c={"Hash Tables": FUNCS_COLOR})
        self.play(Write(title))
        self.play(Write(overview))
        self.next_section("End")
        self.play(Unwrite(title), Unwrite(overview))
        self.wait()


class HashTableRecipe(SectionsScene):
    def construct(self):
        self.next_section("Hash Table Recipe", pst.NORMAL)
        np.random.seed(0)
        title = Title("Hash Table Recipe")
        self.play(Write(title))

        frame_center, hash_table = get_main_hash_table_example()
        array_text, keys_text, hash_function_text = get_hash_table_subtitles(hash_table)
        self.next_section("array")
        array_coords = hash_table.array.get_center()
        hash_table.array.move_to(frame_center)
        array_text.scale(1 / SUB_TITLES_SCALE).match_x(hash_table.array)
        keys_text.scale(1 / SUB_TITLES_SCALE)
        self.play(Write(array_text))
        self.play(Write(hash_table.array))

        self.next_section("keys")
        self.play(array_text.animate.scale(SUB_TITLES_SCALE).set_x(array_coords[0]),
                  hash_table.array.animate.move_to(array_coords))

        keys_coords = hash_table.keys.get_center()
        hash_table.keys.move_to(frame_center)
        self.play(Write(keys_text))
        self.play(Write(hash_table.keys))

        self.next_section("Hash Function")
        self.play(keys_text.animate.scale(SUB_TITLES_SCALE).match_y(array_text),
                  hash_table.keys.animate.move_to(keys_coords))

        hash_function_def_text = MathTex(r"h", r":U\rightarrow\left[m\right]").next_to(hash_table, UP,
                                                                                       buff=-0.15)
        hash_function_def_text[0].set_color(FUNCS_COLOR)
        self.play(Write(hash_function_def_text))

        self.next_section("Show Hash Function")
        x_1_func_text = MathTex(r"h", "\left(", "x_1", r"\right)", color=FUNCS_COLOR).rotate(
            hash_table.arrows[0].get_angle()).next_to(hash_table.arrows[0], UP, buff=-0.5)
        x_3_func_text = MathTex(r"h", "\left(", "x_3", r"\right)", color=FUNCS_COLOR).rotate(
            hash_table.arrows[2].get_angle()).next_to(hash_table.arrows[2], UP, buff=-0.15)
        x_1_func_text[-2].set_color(WHITE)
        x_3_func_text[-2].set_color(WHITE)
        self.play(Write(x_1_func_text), Write(hash_table.arrows[0]))
        self.next_section("Show Hash Function")
        self.play(Write(x_3_func_text), Write(hash_table.arrows[2]))

        x_3_func_text.save_state()
        self.play(Unwrite(x_1_func_text), Unwrite(x_3_func_text))
        arrows_group = VGroup(*[hash_table.arrows[i] for i in range(len(hash_table.arrows)) if i not in [0, 2]])
        self.play(TransformMatchingTex(hash_function_def_text, hash_function_text),
                  Write(arrows_group))

        self.next_section("hash function note")
        hash_function_note = Tex("Note: $h$ required to be computed in $O(1)$ time").scale_to_fit_width(
            hash_table.width * 1.5).to_edge(LEFT + DOWN).to_edge(DOWN, buff=0.2)
        color_tex(hash_function_note, t2c={"h": FUNCS_COLOR}, tex_class=MathTex)
        self.play(Write(hash_function_note))

        self.next_section("hash table operations")
        self.play(Unwrite(hash_function_note))
        self.play(hash_table.arrows.animate.set_opacity(0.5))
        insert_text = get_func_text("Insert($x_3$)")
        search_text = get_func_text("Search($x_3$)")
        delete_text = get_func_text("Delete($x_3$)")
        for text in [insert_text, search_text, delete_text]:
            compile_code_tex_line(text, text.text, bold_math=False)
            text[-2].set_color(SELECT_KEY_COLOR)
        operations = VGroup(insert_text, search_text, delete_text).arrange(DOWN).next_to(keys_text, DOWN).to_edge(LEFT)
        self.play(AnimationGroup(*[Write(text) for text in operations],
                                 hash_table.keys[2].value_mob.animate.set_color(SELECT_KEY_COLOR), lag_ratio=0.5))

        self.next_section("apply operations")
        x_3_func_text.restore()
        x_3_func_text[-2].set_color(SELECT_KEY_COLOR)
        self.play(hash_table.arrows[2].animate.set_opacity(1), Write(x_3_func_text))
        x_3_keys_text = hash_table.keys[2].value_mob.copy().set_z_index(20)
        self.play(x_3_keys_text.animate.scale(0.8).move_to(hash_table.array[hash_table.hash_func(2)]))

        self.next_section("operations run time")
        brace_run_time = BraceLabel(operations, "O(1)", RIGHT)
        self.play(Write(brace_run_time))

        self.next_section("U size question")
        self.play(Unwrite(x_3_keys_text), Unwrite(x_3_func_text), hash_table.arrows.animate.set_opacity(1),
                  hash_table.keys[2].value_mob.animate.set_color(WHITE))
        u_size_question = Tex(r"What if $\left|U\right| \leq m$?").next_to(brace_run_time, DOWN, buff=0.7).set_x(
            -config.frame_width / 4)
        self.play(Write(u_size_question))
        self.next_section("U size question")
        u_size_question_2 = Tex(r"What if $\left|U\right| > m$?").next_to(u_size_question.get_left(), RIGHT, buff=0)
        self.play(TransformMatchingTex(u_size_question, u_size_question_2))

        self.next_section("Chaining", pst.NORMAL)
        chaining_text = Text("Chaining!").scale(1.2).next_to(u_size_question_2, DOWN)
        self.play(Write(chaining_text))
        chaining_lists = hash_table.get_chaining()
        for list in chaining_lists.values():
            self.play(AnimationGroup(*[FadeIn(chain, shift=RIGHT, run_time=0.8) for chain in list], lag_ratio=0.2))

        self.next_section("Operations complexity")
        x_i_tex = VGroup(*[MathTex("x_i", color=SELECT_KEY_COLOR).match_width(
            operations[0][-2]).move_to(oper[-2]) for oper in operations])
        self.play(Unwrite(brace_run_time),
                  *[Transform(oper[-2], x_i) for oper, x_i in zip(operations, x_i_tex)])

        brace_avg_run_time = BraceLabel(operations[1:],
                                        r"O\left(\begin{matrix}\text{linked}\\\text{list's}\\\text{length}\end{matrix}\right)",
                                        RIGHT)
        brace_avg_run_time.label.scale(0.6)
        brace_avg_run_time.brace.put_at_tip(brace_avg_run_time.label)
        insert_run_time = MathTex(r"O\left(1\right)").match_y(operations[0]).align_to(brace_avg_run_time.label, LEFT)
        self.play(Write(insert_run_time))
        self.next_section("Operations complexity")
        self.play(Write(brace_avg_run_time))

        self.next_section("linked list's expected length")
        self.play(Unwrite(u_size_question_2), Unwrite(chaining_text),
                  VGroup(operations, brace_avg_run_time, insert_run_time).animate.align_to(array_text, UP))
        linked_list_req_text = Tex(
            r"If\ \  $\mathbb{E}\left[\begin{matrix}\text{linked}\\\text{list's}\\\text{length}\end{matrix}\right]=O\left(1\right)$\ \  ",
            "then:").next_to(operations, DOWN, buff=0.2).align_to(operations, LEFT)
        self.play(Write(linked_list_req_text))

        self.next_section("ds medal")
        best_ds_medal = SVGMobject(str(ROOT_PATH / "images/best_ds_medal.svg"),
                                   stroke_color=WHITE, stroke_opacity=1).scale(1).next_to(
            linked_list_req_text[-1], DOWN, buff=0.2)
        self.play(DrawBorderThenFill(best_ds_medal, stroke_color=WHITE))
        self.next_section("end scene")
        self.play(Unwrite(operations), Unwrite(brace_avg_run_time), Unwrite(insert_run_time),
                  Unwrite(linked_list_req_text), Unwrite(best_ds_medal), Unwrite(title),
                  *[Unwrite(list) for list in chaining_lists.values()])
        self.wait()


class UniversalHashFamilies(SectionsScene):
    def construct(self):
        np.random.seed(0)
        frame_center, hash_table = get_main_hash_table_example()
        array_text, keys_text, hash_function_text = get_hash_table_subtitles(hash_table)
        keys_text.match_y(array_text)
        self.next_section("Universal Hash Families", pst.NORMAL)
        self.add(hash_table, array_text, keys_text, hash_function_text)
        title = Title("Universal Hash Families")
        self.play(Write(title))

        hash_family_text = Tex("hash family ($\mathcal{H}$)").match_y(array_text).set_x(-array_text.get_x())
        hash_family = get_funcs_bowl().move_to(frame_center).match_x(hash_family_text)
        self.play(Write(hash_family_text))
        self.play(Write(hash_family))

        self.next_section("hash functions")
        self.play(hash_family_text.animate.match_height(keys_text),
                  hash_family.animate.scale(0.7))

        shift_recipe = DOWN * 0.6
        self.play(hash_family.animate.shift(shift_recipe),
                  hash_table.animate.shift(shift_recipe),
                  hash_function_text.animate.shift(shift_recipe))

        select_hash_arrow = CurvedArrow(hash_family.get_top() * RIGHT + hash_table.get_top() * UP, hash_table.get_top(),
                                        angle=-TAU / 6, color=GREEN, stroke_width=6)
        select_hash_text = MathTex(r"h", "_i", color=YELLOW).next_to(select_hash_arrow, UP, buff=0.1)
        select_hash_text.save_state()
        self.play(Write(select_hash_arrow), TransformMatchingTex(hash_function_text, select_hash_text))

        self.next_section("hash functions")
        prev_hash_text = select_hash_text
        for i in range(1, 8):
            new_hash_text = MathTex(rf"h", rf"_{{{i}}}", color=YELLOW).next_to(select_hash_arrow, UP, buff=0.1)
            self.play(TransformMatchingTex(prev_hash_text, new_hash_text),
                      hash_table.animate.rehash(lambda i: np.random.randint(0, 5)))
            prev_hash_text = new_hash_text

        self.next_section("universal hash family definition")

        definition = Tex(
            r'''Let $\mathcal{H}$ be a family of hash functions $U\rightarrow\left[m\right]$. We say that $\mathcal{H}$ is \textbf{universal} if, when choosing $h$ randomly from $\mathcal{H}$:
            \[
            \forall x\neq y\in U,\underset{h\in\mathcal{H}}{\mathbb{P}}\left[h\left(x\right)=h\left(y\right)\right]\leq\frac{1}{m}
            \]''', tex_environment=DEFINITION_TEX_ENV).next_to(title, DOWN)
        prob_eq_start_idx = 85
        prob_eq = definition[0][prob_eq_start_idx:]
        prob_eq.next_to(definition[0][:prob_eq_start_idx], DOWN, buff=0)
        color_tex(definition, t2c={r"\textbf{universal}": YELLOW}, tex_class=MathTex)
        color_tex(definition, t2c={r"x": SELECT_KEY_COLOR, r"y": SELECT_KEY_COLOR, "h": FUNCS_COLOR}, tex_class=MathTex)
        select_hash_text.restore().move_to(prev_hash_text)
        self.play(TransformMatchingTex(prev_hash_text, select_hash_text))
        hash_table_and_family = VGroup(hash_table, select_hash_arrow, select_hash_text, hash_family)
        self.play(Unwrite(array_text), Unwrite(keys_text), Unwrite(hash_family_text),
                  hash_table_and_family.animate.scale_to_fit_height(
                      (config.frame_height / 2 - definition.get_bottom()[1]) * 0.8).to_edge(DOWN, buff=0.3))
        self.play(Write(definition))

        self.next_section("events map")
        frame_center = get_frame_center(top=title)
        array_size = hash_table.array_size
        keys_size = hash_table.keys_size
        hashs_tab = get_hash_family_table(array_size, keys_size).set_y(frame_center[1])
        frame_center = get_frame_center(left=hashs_tab, top=title)

        self.play(Unwrite(hash_table_and_family), Unwrite(definition[0][:prob_eq_start_idx]))
        self.play(prob_eq.animate.scale(0.9).next_to(title, DOWN, buff=1.2).set_x(frame_center[0]))
        self.play(Write(hashs_tab))

        self.next_section("alternative perspective")
        down_arrow_buff = 0.6
        down_arrow = Tex(r"$\Downarrow$").scale(1.3).next_to(prob_eq, DOWN, buff=down_arrow_buff)
        for_x_y_tex = Tex(r"for ", "$x_1$", ", ", "$x_4$", "\ \ :").next_to(down_arrow, DOWN, buff=down_arrow_buff)
        first_key_tex = for_x_y_tex[1].set_color(SELECT_KEY_COLOR)
        second_key_tex = for_x_y_tex[3].set_color(SELECT_KEY_COLOR)
        color_tex(for_x_y_tex, t2c={r"x_1": SELECT_KEY_COLOR, r"x_4": SELECT_KEY_COLOR}, tex_class=MathTex)
        alternative_def = MathTex(
            r"\mathbb{P}\left[\begin{matrix}\hspace{1cm}\\\hspace{1cm}\end{matrix}\right]\leq\frac{1}{m}").next_to(
            for_x_y_tex, DOWN)
        prob_parentheses = alternative_def[0][1:3]
        prob_square = Square(stroke_color=GREEN, fill_color=PROB_BG_CELL_COLOR, fill_opacity=1).match_height(
            prob_parentheses).scale(0.9).move_to(prob_parentheses)
        for_x_y_tex.align_to(prob_eq, LEFT)
        self.play(Write(down_arrow))
        self.play(Write(for_x_y_tex), Write(alternative_def), Write(prob_square))

        self.next_section("alternative perspective example")
        bg_cells = VGroup(
            *[VGroup(*[hashs_tab.get_highlighted_cell((j, i), color=PROB_BG_CELL_COLOR, fill_opacity=0, z_index=-20) for
                       i in range(1, hashs_tab.row_dim + 1)]) for j in range(1, hashs_tab.col_dim + 1)])
        self.play(*animate_collision_prob(0, 3, hashs_tab, bg_cells))

        self.next_section("alternative perspective examples")
        last_index_str = r'\left|U\right|'

        start = True
        for i in range(keys_size):
            for j in range(i + 1, keys_size):
                if i == keys_size - 2 or j == keys_size - 2: continue
                animations = animate_collision_prob(i, j, hashs_tab, bg_cells)
                i_key_prob = MathTex(rf"x_{{{last_index_str if i == keys_size - 1 else i + 1}}}",
                                     color=SELECT_KEY_COLOR).move_to(first_key_tex).align_to(
                    first_key_tex, LEFT)
                j_key_prob = MathTex(rf"x_{{{last_index_str if j == keys_size - 1 else j + 1}}}",
                                     color=SELECT_KEY_COLOR).move_to(second_key_tex).align_to(
                    second_key_tex, LEFT + UP)
                self.play(*animations, TransformMatchingShapes(first_key_tex, i_key_prob),
                          TransformMatchingShapes(second_key_tex, j_key_prob))
                first_key_tex = i_key_prob
                second_key_tex = j_key_prob
                if start:
                    self.next_section("end examples")
                    start = False

        self.next_section("end scene")
        mobjects_to_unwrite = [down_arrow, for_x_y_tex, alternative_def, prob_square, first_key_tex, second_key_tex,
                               title, hashs_tab, prob_eq, bg_cells]
        self.play(*[Unwrite(obj) for obj in mobjects_to_unwrite])
        self.wait()


class UniversalHashExamples(SectionsScene):
    def construct(self):
        self.next_section("Universal Hash Families Examples 1+2", pst.NORMAL)
        title = Title("Universal Hash Families - Example ", "1")
        self.play(Write(title))

        small_hash_family = VGroup(self.get_small_hash_table(), self.get_small_hash_table()).arrange(DOWN, buff=1)
        h1_text = MathTex(r"h_1", color=FUNCS_COLOR).next_to(small_hash_family[0], UP, buff=HASH_TABLE_FUNCS_TITLE_BUFF)
        h2_text = MathTex(r"h_2", color=FUNCS_COLOR).next_to(small_hash_family[1], UP, buff=HASH_TABLE_FUNCS_TITLE_BUFF)
        small_hash_family += VGroup(h1_text, h2_text)
        small_hash_family[0].rehash(lambda x: 0 if x == 2 else 1)
        small_hash_family[1].rehash(lambda x: 1 if x == 2 else 0)
        small_hash_family.scale_to_fit_height(config.frame_height * 0.75).next_to(title, DOWN).to_edge(RIGHT)

        frame_center = get_frame_center(top=title, right=small_hash_family)
        question_1 = Tex(r"Is $\mathcal{H}$ a universal hash family?").next_to(title, DOWN, buff=0.65).set_x(
            frame_center[0])
        self.play(Write(question_1))
        self.play(Write(small_hash_family))

        self.next_section("Universal Hash Families Definition")
        reminder = get_univ_def_reminder()
        reminder.to_edge(DOWN, buff=0.4).set_x(frame_center[0])
        self.play(Write(reminder), question_1.animate.align_to(title, LEFT))

        self.next_section("Solution")
        solution = MathTex(r"\underset{h\in\mathcal{H}}{\mathbb{P}}\left[h\left(0\right)=h\left(1\right)\right]=", "0",
                           r"\leq\frac{1}{m}=\frac{1}{2}").move_to(
            get_frame_center(top=question_1, right=small_hash_family, bottom=reminder))
        color_tex(solution[0], t2c={r"h": FUNCS_COLOR, r"0": SELECT_KEY_COLOR, r"1": SELECT_KEY_COLOR},
                  tex_class=MathTex)
        self.play(Write(solution[0]))
        self.next_section("Solution part 1")
        self.play(Write(solution[1]))
        self.next_section("Solution part 2")
        self.play(Write(solution[2]))

        self.next_section("Universal Hash Families Examples 2")
        title_2 = Title("Universal Hash Families - Example ", "2")
        self.play(TransformMatchingShapes(title[1], title_2[1]), Unwrite(solution))
        self.wait()
        self.play(small_hash_family[0].animate.rehash(lambda x: 0), small_hash_family[1].animate.rehash(lambda x: 1))

        self.next_section("Solution")
        solution = MathTex(r"\underset{h\in\mathcal{H}}{\mathbb{P}}\left[h\left(0\right)=h\left(1\right)\right]=", "1",
                           r">\frac{1}{m}=\frac{1}{2}").move_to(solution)
        color_tex(solution[0], t2c={r"h": FUNCS_COLOR, r"0": SELECT_KEY_COLOR, r"1": SELECT_KEY_COLOR},
                  tex_class=MathTex)
        self.play(Write(solution[0]))
        self.next_section("Solution part 1")
        self.play(Write(solution[1]))
        self.next_section("Solution part 2")
        self.play(Write(solution[2]))

        self.next_section("Universal Hash Families Examples 3")
        self.play(*map(Unwrite, [title[:1], title[2:], title_2[1], small_hash_family, question_1, reminder, solution]))
        self.wait()

    def get_small_hash_table(self):
        small_hash_table = HashTable(3, 2, lambda x: 0 if x == 1 else 1)
        small_hash_table.keys[1].set_opacity(0)
        small_hash_table.keys[-1].next_to(small_hash_table.keys[0], DOWN, buff=0)
        small_hash_table.keys.match_y(small_hash_table.array)

        for key, key_val in zip([0, 2], [0, 1]):
            small_hash_table.keys[key].set_value(key_val)

        small_hash_table.array[0].value_mob.set_opacity(0)
        for array_idx in range(2):
            small_hash_table.array[array_idx].set_index(array_idx)
        return small_hash_table


class UniversalHashBaseExample(SectionsScene):
    def construct(self):
        self.next_section("Universal Hash Families Example 3", pst.NORMAL)
        self.title = Title("Universal Hash Families - Example ", "3")
        self.play(Write(self.title))

        self.numbers_color = BLUE
        self.bases_color = RED
        self.k_color = K_UNIVERSAL_COLOR

        self.bases_intro()
        self.explain_example()
        self.proof_of_universal_hash_family()

        self.wait()

    def bases_intro(self):
        sub_title = Text("Introduction to Base Changing").scale(0.8).next_to(self.title, DOWN)

        bases = [2, 4, 6, 8, 10, 16]
        bases = VGroup(
            *[VGroup(Tex(f"Base ", f"{base}", ":"), IntegerBase(0, base, color=self.numbers_color)).arrange(RIGHT,
                                                                                                            buff=0.5)
              for base in bases]).arrange(DOWN, buff=0.5).next_to(sub_title, DOWN, buff=0.7)
        for base in bases:
            base.align_to(bases[0], RIGHT)
            base[0][1].set_color(self.bases_color)

        self.play(Write(sub_title))
        self.play(Write(bases))

        steps = 11
        for i in range(steps):
            self.next_section(f"Base Changing - Step {i + 1}")
            self.play(*map(lambda x: x[1].animate.set_value(i + 1), bases))

        self.play(*map(lambda x: Count(x[1], steps, 143, LEFT, run_time=6), bases))
        bases_calc = VGroup(
            *[get_base_convert_calc(base[1], self.numbers_color, self.bases_color).match_height(bases[0][1]).match_y(
                base[1]) for
                base in bases])
        bases_calc[0].scale_to_fit_width(config.frame_width * 0.55)
        for base_calc in bases_calc:
            base_calc.match_height(bases_calc[0])
        bases_calc.to_edge(RIGHT)
        self.play(bases.animate.to_edge(LEFT))
        calc_arrow = Arrow(bases.get_right() + LEFT, bases_calc.get_left() + RIGHT, buff=0.5).next_to(bases[3], RIGHT)
        sum_eq = MathTex(r"\underset{i=0}{\overset{n}{\sum}}a_{i}b^{i}").next_to(calc_arrow, UP, buff=0)
        color_tex(sum_eq, {"a_{i}": self.numbers_color, "b^{i}": self.bases_color}, MathTex)
        self.play(FadeIn(calc_arrow, shift=RIGHT), Write(sum_eq))

        self.next_section("Show calc base 2")
        self.animate_base_calc(0, bases, bases_calc)

        self.next_section("Show calc base 16")
        self.animate_base_calc(-1, bases, bases_calc)

        self.next_section("All calcs")
        self.play(Write(bases_calc[1:-1]))

        self.next_section("Show example")
        self.play(Unwrite(sub_title), Unwrite(bases), Unwrite(bases_calc), Unwrite(calc_arrow), Unwrite(sum_eq))

    def explain_example(self):
        example_tex = Tex(
            r'''\begin{itemize}
        \setlength\itemsep{0.03em}
        \item[$\bullet$] $p=$prime number
        \item[$\bullet$] $k\in\mathbb{N}$
        \item[$\bullet$] $U=\left\{ 0,1,\ldots, p^{k}-1\right\}$
        \item[$\bullet$] $x_{i}$ denotes the $i$-th digit of $x$ in base $p$.
        \end{itemize}
        The hash function $h_{a}:U\rightarrow\left\{ 0,1,\ldots p-1\right\}$, where $a\in U$, is defined as follows:
        \[
        h_{a}(x)=\sum_{i=1}^{k}a_{i}x_{i}\ \left(\bmod\ p\right)
        \]''', tex_environment=DEFINITION_TEX_ENV).next_to(self.title, DOWN)
        color_tex(example_tex, t2c={r"x": SELECT_KEY_COLOR, r"x_{i}": SELECT_KEY_COLOR, r"h_{a}": FUNCS_COLOR,
                                    r"a": FUNCS_COLOR, r"a_{i}": FUNCS_COLOR, "p": self.bases_color,
                                    "k": self.k_color}, tex_class=MathTex)

        example_tex[0][31].set_color(self.k_color)
        example_tex[0][134].set_color(self.k_color)
        hash_func_def_idx = 128
        self.hash_func_def = example_tex[0][hash_func_def_idx:]
        self.hash_func_def.to_edge(DOWN)

        last_U_def_idx = 35
        self.play(Write(example_tex[0][1:last_U_def_idx]), Write(example_tex[0][0]))
        self.play_U_example(example_tex, last_U_def_idx)
        self.play(Write(example_tex[0][last_U_def_idx:]))

        self.play_hash_func_example(example_tex, hash_func_def_idx)

    def play_U_example(self, example_tex, last_U_def_idx):
        self.next_section("Show U example 1")
        p, k = 2, 5
        num_U_example = Tex(f"Example: $p={p}$, $k={k}$").next_to(example_tex[0][:last_U_def_idx], DOWN,
                                                                  buff=0.7).to_edge(
            LEFT)
        color_tex(num_U_example, t2c={r"p": self.bases_color, "k": self.k_color}, tex_class=MathTex)
        U_eq = Tex("U=").move_to(get_frame_center(top=num_U_example)).align_to(num_U_example, LEFT)
        U_example_base10 = self.get_U_space(p, k, 10, arrange_cols=(4, 8)).next_to(U_eq, RIGHT)
        U_example_base_p = self.get_U_space(p, k, arrange_cols=(4, 8)).move_to(U_example_base10)
        self.play(Write(num_U_example))
        self.play(Write(U_example_base10), Write(U_eq))
        self.next_section("Change U base")
        self.play(ReplacementTransform(U_example_base10, U_example_base_p))
        self.next_section("Show U example 2")
        self.play(Unwrite(U_example_base_p))
        p, k = 5, 3
        num_U_example2 = Tex(f"Example: $p={p}$, $k={k}$").move_to(num_U_example).align_to(num_U_example, LEFT)
        color_tex(num_U_example2, t2c={r"p": self.bases_color, "k": self.k_color}, tex_class=MathTex)
        U_example_base10 = self.get_U_space(p, k, 10).next_to(U_eq, RIGHT)
        U_example_base_p = self.get_U_space(p, k).move_to(U_example_base10)
        self.play(TransformMatchingTex(num_U_example, num_U_example2))
        self.play(Write(U_example_base10))
        self.next_section("Change U base")
        self.play(ReplacementTransform(U_example_base10, U_example_base_p))
        self.next_section("end example explain")
        self.play(Unwrite(num_U_example2), Unwrite(U_eq), Unwrite(U_example_base_p))

    def play_hash_func_example(self, example_tex, hash_func_def_idx):
        self.next_section("Show hash func example 1")
        self.play(Unwrite(example_tex[0][:hash_func_def_idx]))

        p, k, a = 5, 2, 8
        keys_size = 10
        int_base_formatter = IntegerBase(0, p, zeroes_padding=k)._get_num_string
        funcs_bowl = get_funcs_bowl(int_base_formatter, f"{p - 1}" * k, [5, 5])
        hash_table = HashTable(keys_size, p, lambda x: get_hash_func(p, k, a)(x if x != keys_size - 1 else p ** k - 1),
                               arrows_config={"tip_length": 1.5, "stroke_width": 6,
                                              "max_tip_length_to_length_ratio": 0.35},
                               keys_array_gap_size=7)
        ArrayEntry.INDICES_BUFF *= 0.5
        for i, entry in enumerate(hash_table.array):
            entry.set_index(i)
            entry.set_value("")
        ArrayEntry.INDICES_BUFF *= 2
        for i, key in enumerate(hash_table.keys):
            if i == hash_table.keys_size - 2: continue
            key.set_value(f"{p - 1}" * k if i == hash_table.keys_size - 1 else int_base_formatter(i))

        hash_table.to_edge(DR)
        funcs_bowl.scale(0.7).next_to(hash_table, LEFT, buff=1).align_to(hash_table.keys, UP).shift(DOWN * 0.2)
        select_hash_arrow = CurvedArrow(funcs_bowl.get_top() * RIGHT + hash_table.get_top() * UP, hash_table.get_top(),
                                        angle=-TAU / 6, color=GREEN, stroke_width=6)
        hash_func_arrow_text = MathTex(r"h", f"_{{{int_base_formatter(a)}}}", color=YELLOW).next_to(select_hash_arrow,
                                                                                                    UP, buff=0.1)
        select_hash_arrow.add(hash_func_arrow_text)

        params_tex = Tex(f"Example: $p={p}$, $k={k}$").next_to(funcs_bowl, DOWN).align_to(self.title, LEFT)
        color_tex(params_tex, t2c={r"p": self.bases_color, "k": self.k_color}, tex_class=MathTex)

        self.play(self.hash_func_def.animate.next_to(self.title, DOWN, buff=0.2).align_to(self.title, LEFT))
        self.play(Write(params_tex), Write(hash_table), Write(funcs_bowl))
        self.play(Write(select_hash_arrow))

        self.next_section("example 1")
        x_1 = 3
        equation, mod_tex = get_hash_func_calc(p, k, a, x_1, self.bases_color, SELECT_KEY_COLOR, FUNCS_COLOR)
        VGroup(equation, mod_tex).move_to(get_frame_center(top=params_tex, right=hash_table))
        self.play(Write(equation[:-1]), Write(mod_tex),
                  hash_table.keys[x_1].value_mob.animate.set_color(SELECT_KEY_COLOR))
        self.next_section("Show solution")
        self.play(Write(equation[-1]))

        self.next_section("example 2")
        x_2 = 7
        equation_2, _ = get_hash_func_calc(p, k, a, x_2, self.bases_color, SELECT_KEY_COLOR, FUNCS_COLOR)
        equation_2.move_to(equation).align_to(equation, LEFT)
        self.play(Unwrite(equation[-1]), hash_table.keys[x_1].value_mob.animate.set_color(WHITE))
        self.play(ReplacementTransform(equation[:-1], equation_2[:-1]),
                  hash_table.keys[x_2].value_mob.animate.set_color(SELECT_KEY_COLOR))
        self.next_section("Show solution")
        self.play(Write(equation_2[-1]))

        self.next_section("end example explain")
        self.play(Unwrite(params_tex), Unwrite(hash_table), Unwrite(funcs_bowl), Unwrite(select_hash_arrow),
                  Unwrite(equation_2), Unwrite(mod_tex))

    def proof_of_universal_hash_family(self):
        self.next_section("Universal Hash Families Example 3 - Proof", pst.NORMAL)
        question = Tex(r"Is $\mathcal{H}=\left\{ h_{a}\middle|a\in U\right\}$ a universal hash family?").next_to(
            self.title, DOWN).align_to(self.title, LEFT)
        color_tex(question, t2c={r"h_{a}": FUNCS_COLOR}, tex_class=MathTex)
        reminder = get_univ_def_reminder().scale(0.7).to_edge(DL, buff=0.3)
        self.play(self.hash_func_def.animate.next_to(reminder, UP))
        self.play(Write(question))
        self.play(Write(reminder))

        self.next_section("Proof")
        proof = VGroup(MathTex(r"P\left[h_{a}(x)=h_{a}(y)\right]",
                               r"=&P\left[\sum_{i=1}^{k}a_{i}\cdot x_{i}=\sum_{i=1}^{k}a_{i}\cdot y_{i}\ \left(\bmod\ p\right)\right]"),
                       MathTex(
                           r"=P\left[\sum_{i=1}^{k}a_{i}\cdot\left(x_{i}-y_{i}\right)=0\ \left(\bmod\ p\right)\right]"),
                       MathTex(
                           r"=P\left[\sum_{i\neq j}a_{i}\cdot\left(x_{i}-y_{i}\right)+a_{j}\left(x_{j}-y_{j}\right)=0\ \left(\bmod\ p\right)\right]"),
                       MathTex(
                           r"=P\left[\sum_{i\neq j}a_{i}\cdot\left(x_{i}-y_{i}\right)=a_{j}\left(y_{j}-x_{j}\right)\ \left(\bmod\ p\right)\right]"),
                       MathTex(
                           r"=P\left[\frac{\sum_{i\neq j}a_{i}\cdot\left(x_{i}-y_{i}\right)}{\left(y_{j}-x_{j}\right)}=a_{j}\ \left(\bmod\ p\right)\right]",
                           r"=\frac{1}{p}")).arrange(DOWN, buff=0.3).scale_to_fit_height(
            (config.frame_height - question.get_bottom()[1]) * 0.95)
        for i, line in enumerate(proof):
            color_tex(line, t2c={"x": SELECT_KEY_COLOR, "y": SELECT_KEY_COLOR,
                                 "x_{i}": SELECT_KEY_COLOR, "y_{i}": SELECT_KEY_COLOR,
                                 "x_{j}": SELECT_KEY_COLOR, "y_{j}": SELECT_KEY_COLOR,
                                 "a_{i}": FUNCS_COLOR, "a_{j}": FUNCS_COLOR, "h_{a}": FUNCS_COLOR,
                                 "p": self.bases_color}, tex_class=MathTex)
            if i != 0:
                line.align_to(proof[0][1], LEFT)

        proof.next_to(question, DOWN, buff=0.25).align_to(self.title, RIGHT)

        vdots = MathTex(r"\vdots").scale(3).move_to(
            get_frame_center(left=self.hash_func_def, top=proof[0][0], bottom=proof[-1][-1]))
        self.play(Write(proof[0][0]), Write(vdots), Write(proof[-1][-1]))

        proof_steps = VGroup(proof[0][1], *proof[1:-1], proof[-1][0])
        self.next_section("Proof steps")
        self.play(Unwrite(vdots))
        self.play(Write(proof_steps[0]))

        for i, step in enumerate(proof_steps[1:], start=1):
            self.next_section(f"Proof step {i + 1}")
            prev_step = proof_steps[i - 1].copy()
            self.play(prev_step.animate.match_y(step))
            self.play(TransformMatchingShapes(prev_step, step))

        self.next_section("end of proof")
        self.play(Unwrite(proof), Unwrite(question), Unwrite(reminder), Unwrite(self.hash_func_def),
                  Unwrite(self.title))

    def animate_base_calc(self, base_idx, bases, bases_calc):
        int_base = bases[base_idx][1]
        bases_calc[base_idx][::4].set_opacity(0)
        zeroes_num = int_base.zeroes_padding - len(int_base._get_num_string(int_base.get_value()).lstrip('0'))
        base_cp = bases[base_idx][1].copy()[zeroes_num:]
        self.play(base_cp.animate.move_to(bases_calc[base_idx]).match_height(bases_calc[base_idx][0]))
        self.play(*[base_cp[i].animate.move_to(bases_calc[base_idx][i * 4]) for i in range(len(base_cp))])
        self.play(Write(bases_calc[base_idx]))
        bases_calc[base_idx].add(base_cp)

    def get_U_space(self, p: int, k: int, base: int = None, arrange_cols: tuple | list = None):
        base = p if base is None else base
        arrange_cols = (p, p ** (k - 1)) if arrange_cols is None else arrange_cols
        U_example = VGroup(
            *[IntegerBase(i, base, zeroes_padding=k, zeroes_opacity=1, color=WHITE) for i in
              range(p ** k)]).arrange_in_grid(*arrange_cols, flow_order="dr").scale_to_fit_width(
            config.frame_width * 0.86).set_color(SELECT_KEY_COLOR)
        return U_example


class CheckTriplets(SectionsScene):
    def construct(self):
        self.next_section("Question - Check Triplets", pst.NORMAL)
        self.title = Title("Check Triplets")
        self.play(Write(self.title))
        self.example_lst = [5, 9, 4, 1, 2]
        self.show_question()
        self.show_solution()

        self.wait()

    def show_question(self):
        question = BulletedList(r"\textbf{Algorithm:}",
                                r"\textbf{Input:} Array $A$ of n integers.",
                                REMOVE_MATH_SPACE_PREAMBLE + r"\textbf{Output:} Determine if there exists a triplet forming an arithmetic sequence of length $3$: \[\exists d\ s.t.\ \forall i\ \ a_{i+1}-a_{i}=d\]",
                                "If such a triplet exists, return it.",
                                r"\textbf{Expected Runtime:} $O\left(n^{2}\right)$",
                                tex_environment=DEFINITION_TEX_ENV,
                                dot_scale_factor=3, buff=0.18).scale(0.8).next_to(self.title,
                                                                                  DOWN).align_to(self.title, LEFT)
        color_tex(question, t2c={"A": BLUE}, tex_class=MathTex)
        check_triplet_question_func = get_func_text("CheckTriplets(A)", ["A"]).match_height(question[0]
                                                                                            ).next_to(question[0],
                                                                                                      RIGHT)
        self.play(Write(question), Write(check_triplet_question_func))

        self.next_section("Example")
        example_tex = Tex("Example:").scale(1.2).next_to(question, DOWN, buff=0.4).align_to(question, LEFT)
        array_mob = ArrayMob("A=", *self.example_lst).match_height(example_tex)
        array_mob.name_mob[0][0].set_color(BLUE)
        check_triplet_func = check_triplet_question_func.copy().match_height(array_mob.name_mob)
        solution = MathTex(r"= [1, 5, 9]")
        color_tex(solution, t2c={"1": YELLOW, "5": YELLOW, "9": YELLOW}, tex_class=MathTex)
        solution[0][-4].set_color(YELLOW)

        VGroup(array_mob, check_triplet_func, solution).arrange(RIGHT).scale_to_fit_width(
            config.frame_width * 0.9).move_to(get_frame_center(top=example_tex))
        self.play(Write(VGroup(example_tex, array_mob)))

        self.next_section("Solution")
        self.play(Write(VGroup(check_triplet_func, solution)),
                  *[array_mob.get_entry(i).value_mob.animate(run_time=2).set_color(YELLOW) for i in [0, 1, 3]])

        self.next_section("end example")
        self.play(Unwrite(
            VGroup(example_tex, question, check_triplet_func, array_mob, solution, check_triplet_question_func)))

    def show_solution(self):
        self.next_section("Solution - Check Triplets")
        subtitle = Text("Solution").scale(1.2).next_to(self.title, DOWN).align_to(self.title, LEFT)
        self.play(Write(subtitle))

        naive_sol_title = Text("Naive Solution").scale(0.8).next_to(subtitle, DOWN, buff=0.5).align_to(subtitle, LEFT)
        naive_solution = BulletedList(r"Use three nested loops to check all possible triplets.",
                                      r"\textbf{Runtime:} $O\left(n^{3}\right)$",
                                      tex_environment=DEFINITION_TEX_ENV,
                                      dot_scale_factor=3, buff=0.18).next_to(naive_sol_title, DOWN).align_to(
            naive_sol_title, LEFT)
        self.play(Write(VGroup(naive_sol_title, naive_solution[:-1])))

        self.next_section("Show Runtime")
        self.play(Write(naive_solution[-1]))

        self.next_section("Optimized Solution")
        self.play(Unwrite(VGroup(naive_sol_title, naive_solution)))

        observation_title = Text("Observation").scale(0.8).next_to(subtitle, DOWN, buff=0.5).align_to(subtitle, LEFT)
        observation = BulletedList(REMOVE_MATH_SPACE_PREAMBLE +
                                   r"An arithmetic sequence of length $3$ is determined by its first two elements:" +
                                   r"\[\begin{matrix}1)\ b-a=d\\2)\ c-b=d\end{matrix}\overset{2-1}{\Longrightarrow}c=b+\left(b-a\right)=2b-a\]",
                                   r"Thus, for each $a, b$ pair, we can check if $2b-a$ exists in $A$ (or even better, in a hash table!).",
                                   tex_environment=DEFINITION_TEX_ENV,
                                   dot_scale_factor=3, buff=0.4).next_to(naive_sol_title, DOWN).align_to(
            naive_sol_title, LEFT)
        color_tex(observation, t2c={"a": YELLOW, "b": YELLOW, "c": YELLOW, "A": BLUE}, tex_class=MathTex)
        self.play(Write(VGroup(observation_title, observation[:-1])))

        self.next_section("Show Hash Table solution")
        self.play(Write(observation[-1]))

        self.next_section("Show algorithm")
        self.play(Unwrite(VGroup(observation_title, observation)))
        solution_steps = BulletedList(r"Initalize hash table $T$ and insert all elements of $A$.",
                                      r"For each $a<b$ pair, check if $2b-a$ exists in $T$.",
                                      r"\textbf{Expected Runtime:}",
                                      tex_environment=DEFINITION_TEX_ENV,
                                      dot_scale_factor=3, buff=0.4).next_to(subtitle, DOWN).align_to(
            subtitle, LEFT)
        color_tex(solution_steps, t2c={"a": YELLOW, "b": YELLOW, "A": BLUE}, tex_class=MathTex)
        self.play(Write(solution_steps[:-1]))

        example_tex = Tex("Example:").scale(1.2).next_to(solution_steps[:-1], DOWN, buff=0.4).align_to(solution_steps,
                                                                                                       LEFT)
        array_mob = ArrayMob("A=", *self.example_lst).scale_to_fit_width(config.frame_width * 0.4).move_to(
            get_frame_center(top=example_tex)).align_to(example_tex, LEFT)
        array_mob.name_mob[0][0].set_color(BLUE)
        hash_table = ArrayMob("T", *self.example_lst).match_height(array_mob)
        hash_table.entries.arrange(DOWN, buff=0)
        hash_table.name_mob.next_to(hash_table.entries, UP, buff=0.2)
        hash_table.to_edge(DR)
        self.play(Write(VGroup(example_tex, array_mob)))

        pointer_1 = ArrayPointer(array_mob, 0, "a", direction=0.4 * DOWN)
        pointer_2 = ArrayPointer(array_mob, 1, "b", direction=0.4 * DOWN)
        self.play(Write(hash_table))
        self.play(pointer_1.write_arrow(), pointer_2.write_arrow())

        self.next_section("first calc")
        c = str(2 * self.example_lst[1] - self.example_lst[0])
        calc_tex = MathTex("2b-a=", c).next_to(example_tex, DOWN).set_x(
            get_frame_center(right=hash_table.entries, left=array_mob.entries)[0])
        color_tex(calc_tex, t2c={"a": YELLOW, "b": YELLOW, c: BLUE}, tex_class=MathTex)
        self.play(Write(calc_tex))
        func_calc = get_func_text(f"T.Search({c})", [c]).next_to(calc_tex, DOWN, buff=1.3)
        self.play(Write(func_calc))

        for a_idx, a in enumerate(self.example_lst):
            found_c = False
            for b_idx, b in enumerate(self.example_lst):
                if a >= b or (a_idx == 0 and b_idx == 1): continue
                self.next_section("next search")
                anims = []
                c = str(2 * b - a)
                self.play(pointer_1.to_entry(a_idx), run_time=0.3)
                self.play(pointer_2.to_entry(b_idx), run_time=0.3)
                anims.append(calc_tex[1].animate.become(MathTex(c, color=BLUE).move_to(calc_tex[1])))
                func_arg = func_calc[-3:-1]
                anims.append(func_arg.animate.become(get_func_text(f"{c}", [c]).match_height(func_arg).move_to(
                    func_arg)))
                self.play(*anims, run_time=0.7)
                if int(c) in self.example_lst:
                    found_c = True
                    self.play(hash_table.indicate_at(self.example_lst.index(int(c))))
                    break

            if found_c:
                break
        self.next_section("Compute complexity")
        self.play(Unwrite(VGroup(calc_tex, func_calc, pointer_1, pointer_2, array_mob, hash_table, example_tex)))
        self.play(Write(solution_steps[-1]))

        self.next_section("first_complex")
        complexity_calc = MathTex(r"O\left(n\right)", r"+O_{\mathbb{E}}\left(n^{2}\right)",
                                  r"=O_{\mathbb{E}}\left(n^{2}\right)").next_to(
            solution_steps[-1], RIGHT)
        self.play(Write(complexity_calc[0]), solution_steps[1].animate.set_opacity(0.5), Indicate(solution_steps[0]))

        self.next_section("second_complex")
        solution_steps[1].set_opacity(1)
        self.play(Write(complexity_calc[1]), solution_steps[0].animate.set_opacity(0.5), Indicate(solution_steps[1]))

        self.next_section("final solution")
        self.play(Write(complexity_calc[2]), solution_steps.animate.set_opacity(1))

        self.next_section("end solution")
        self.play(Unwrite(VGroup(self.title, subtitle, solution_steps, complexity_calc)))


class KUniversalHashFamilies(SectionsScene):
    def construct(self):
        self.next_section("k-Universal Hash Families", pst.NORMAL)
        title = Title("$k$-Universal Hash Families")
        color_tex(title, t2c={"k": K_UNIVERSAL_COLOR}, tex_class=MathTex)
        self.play(Write(title))

        frame_center, hash_table = get_main_hash_table_example()
        array_text, keys_text, hash_function_text = get_hash_table_subtitles(hash_table)
        hash_family_text = Tex("hash family ($\mathcal{H}$)").match_y(array_text).set_x(-array_text.get_x())
        hash_family = get_funcs_bowl().move_to(frame_center).match_x(hash_family_text)

        hash_family_text.match_height(keys_text)
        hash_family.scale(0.7)

        shift_recipe = DOWN * 0.6
        hash_family.shift(shift_recipe)
        hash_table.shift(shift_recipe)
        hash_function_text.shift(shift_recipe)

        select_hash_arrow = CurvedArrow(hash_family.get_top() * RIGHT + hash_table.get_top() * UP, hash_table.get_top(),
                                        angle=-TAU / 6, color=GREEN, stroke_width=6)
        select_hash_text = MathTex(r"h", "_i", color=YELLOW).next_to(select_hash_arrow, UP, buff=0.1)
        reminder_text = Text("Reminder:").next_to(title, DOWN, buff=0.5, aligned_edge=LEFT)
        hash_model = VGroup(hash_family_text, keys_text, array_text, select_hash_text, select_hash_arrow, hash_family,
                            hash_table).scale(0.8).next_to(reminder_text, DOWN, buff=0.5).set_x(0)
        self.play(Write(reminder_text), *map(Write, hash_model))

        self.next_section("universal hash family definition")
        # self.play(Unwrite(reminder_text), Unwrite(hash_model))

        definition = Tex(
            r'''Let $k\in\mathbb{N}$ and let $\mathcal{H}$ be a family of hash functions $U\rightarrow\left[m\right]$. We say that $\mathcal{H}$ is $k$\textbf{-universal} if, when choosing $h$ randomly from $\mathcal{H}$:
            \[
            \begin{matrix}\mathbin{\forall}y_{1}\neq \ldots\neq y_{k}\in U\\
\mathbin{\forall}i_{1},\ldots,i_{k}\in\left[m\right]
\end{matrix},\
\underset{h\in\mathcal{H}}{\mathbb{P}}\left[h\left(y_{1}\right)=i_{1}\land\ldots\land h\left(y_{k}\right)=i_{k}\right]\leq\frac{1}{m^{k}}
            \]''', tex_environment=DEFINITION_TEX_ENV).next_to(title, DOWN, aligned_edge=LEFT)
        prob_eq_start_idx = 96
        pure_prob_start_idx = 125 - prob_eq_start_idx
        prob_eq = definition[0][prob_eq_start_idx:]
        prob_eq.scale_to_fit_width(config.frame_width * 0.9).next_to(definition[0][:prob_eq_start_idx], DOWN,
                                                                     buff=0.3).set_x(0)
        color_tex(definition, t2c={r"\textbf{-universal}": YELLOW}, tex_class=MathTex)
        color_tex(definition, t2c={**{i: SELECT_KEY_COLOR for i in ["y_{1}", "y_{k}"]}, "h": FUNCS_COLOR,
                                   "k": K_UNIVERSAL_COLOR}, tex_class=MathTex)
        definition[0][-1].set_color(K_UNIVERSAL_COLOR)
        hash_table_and_family = VGroup(hash_table, select_hash_arrow, select_hash_text, hash_family)
        self.play(Unwrite(array_text), Unwrite(keys_text), Unwrite(hash_family_text), Unwrite(reminder_text),
                  hash_table_and_family.animate.scale_to_fit_height(
                      (config.frame_height / 2 + definition.get_bottom()[1]) * 0.9).to_edge(DOWN, buff=0.3))
        self.play(Write(definition))

        self.next_section("Show compress def")
        frame_center = get_frame_center(top=title)

        self.play(Unwrite(hash_table_and_family), Unwrite(definition[0][:prob_eq_start_idx]))
        self.play(VGroup(prob_eq[:pure_prob_start_idx], prob_eq[pure_prob_start_idx:]).animate.scale(1.3).arrange(
            DOWN).move_to(get_frame_center(top=title)))

        self.next_section("Show 2-universal definition")
        array_size = hash_table.array_size
        keys_size = hash_table.keys_size
        frame_center = get_frame_center(top=title)
        hashs_tab = get_hash_family_table(hash_table.array_size, hash_table.keys_size, seed=2).set_y(frame_center[1])
        frame_center = get_frame_center(left=hashs_tab, top=title)

        two_universal_def = get_two_universal_def()
        two_universal_def.match_width(prob_eq).move_to(prob_eq)
        self.play(TransformMatchingShapes(prob_eq, two_universal_def))
        self.next_section("alternative perspective")
        self.play(two_universal_def.animate.scale(0.7).next_to(title, DOWN, buff=0.5).set_x(frame_center[0]))
        self.play(Write(hashs_tab))

        self.next_section("Show for examples")
        down_arrow_buff = 0.4
        down_arrow = Tex(r"$\Downarrow$").scale(1.3).next_to(two_universal_def, DOWN, buff=down_arrow_buff)
        for_x_y_tex = Tex(r"for ", "$y_1=$", "$x_1$", ", ", "$y_2=$", "$x_2$", "\ \ :").next_to(down_arrow, DOWN,
                                                                                                buff=down_arrow_buff)
        first_key_tex = for_x_y_tex[2].set_color(SELECT_KEY_COLOR)
        second_key_tex = for_x_y_tex[5].set_color(SELECT_KEY_COLOR)

        for_i_tex = Tex(r"for ", "$i_1=$", "$3$", " , ", "$i_2=$", "$2$", "\ \ :").next_to(for_x_y_tex, DOWN)
        first_i_tex = for_i_tex[2]
        second_i_tex = for_i_tex[5]

        # color_tex(for_x_y_tex, t2c={r"y_1": SELECT_KEY_COLOR, r"y_4": SELECT_KEY_COLOR}, tex_class=MathTex)
        alternative_def = MathTex(
            r"\mathbb{P}\left[\begin{matrix}\hspace{1cm}\\\hspace{1cm}\end{matrix}\right]\leq\frac{1}{m^{2}}").next_to(
            for_i_tex, DOWN)
        # alternative_def[0][-1].set_color(K_UNIVERSAL_COLOR)
        prob_parentheses = alternative_def[0][1:3]
        prob_square = Square(stroke_color=GREEN, fill_color=PROB_BG_CELL_COLOR, fill_opacity=1).match_height(
            prob_parentheses).scale(0.9).move_to(prob_parentheses)
        for_x_y_tex.align_to(two_universal_def, LEFT)
        for_i_tex.next_to(for_x_y_tex, DOWN, aligned_edge=LEFT, buff=0.2).shift(RIGHT * 0.5)
        self.play(Write(down_arrow))
        self.play(Write(for_x_y_tex), Write(for_i_tex), Write(alternative_def), Write(prob_square))

        self.next_section("alternative perspective example")
        bg_cells = VGroup(
            *[VGroup(*[hashs_tab.get_highlighted_cell((j, i), color=PROB_BG_CELL_COLOR, fill_opacity=0, z_index=-20) for
                       i in range(1, hashs_tab.row_dim + 1)]) for j in range(1, hashs_tab.col_dim + 1)])
        self.play(*animate_collision_prob(0, 1, hashs_tab, bg_cells, i_1=2, i_2=1))

        self.next_section("alternative perspective examples")
        last_index_str = r'\left|U\right|'

        start = True
        for y_1 in range(keys_size):
            for y_2 in range(y_1 + 1, keys_size):
                if y_1 == keys_size - 2 or y_2 == keys_size - 2: continue
                for i_1 in range(array_size):
                    for i_2 in range(array_size):
                        if i_1 == array_size - 2 or i_2 == array_size - 2: continue

                        animations = animate_collision_prob(y_1, y_2, hashs_tab, bg_cells, i_1=i_1, i_2=i_2)
                        i_key_prob = MathTex(rf"x_{{{last_index_str if y_1 == keys_size - 1 else y_1 + 1}}}",
                                             color=SELECT_KEY_COLOR).move_to(first_key_tex).align_to(
                            first_key_tex, LEFT)
                        j_key_prob = MathTex(rf"x_{{{last_index_str if y_2 == keys_size - 1 else y_2 + 1}}}",
                                             color=SELECT_KEY_COLOR).move_to(second_key_tex).align_to(
                            second_key_tex, LEFT + UP)
                        i_1_prob = MathTex(str(i_1 + 1) if i_1 != array_size - 1 else "m",
                                           ).move_to(first_i_tex).align_to(first_i_tex, LEFT)
                        i_2_prob = MathTex(str(i_2 + 1) if i_2 != array_size - 1 else "m",
                                           ).move_to(second_i_tex).align_to(second_i_tex, LEFT)
                        self.play(*animations, TransformMatchingShapes(first_key_tex, i_key_prob),
                                  TransformMatchingShapes(second_key_tex, j_key_prob),
                                  TransformMatchingShapes(first_i_tex, i_1_prob),
                                  TransformMatchingShapes(second_i_tex, i_2_prob),
                                  run_time=0.02 if not start else 1)
                        first_key_tex = i_key_prob
                        second_key_tex = j_key_prob
                        first_i_tex = i_1_prob
                        second_i_tex = i_2_prob
                        if start:
                            self.next_section("end examples")
                            start = False
        self.next_section("end examples")
        mobjects_to_unwrite = [down_arrow, for_x_y_tex, for_i_tex, alternative_def, prob_square, first_key_tex,
                               second_key_tex,
                               first_i_tex, second_i_tex, two_universal_def, bg_cells]
        self.play(*[Unwrite(obj) for obj in mobjects_to_unwrite])
        self.wait()


class TwoUniversalsAreUniversal(SectionsScene):
    def construct(self):
        self.next_section("2-Universals Are Universal", pst.NORMAL)

        self.title = Title("$k$-Universal Hash Families")
        color_tex(self.title, t2c={"k": K_UNIVERSAL_COLOR}, tex_class=MathTex)
        frame_center = get_frame_center(top=self.title)
        array_size = 5
        keys_size = 6
        self.hashs_tab = get_hash_family_table(array_size, keys_size, seed=2).set_y(frame_center[1])
        self.add(self.title, self.hashs_tab)

        theorem_tex = Tex(r"Theorem:\\If $\mathcal{H}$ is a $2$-universal hash family, then it is also universal.",
                          tex_environment="{minipage}{5cm}").move_to(
            get_frame_center(top=self.title, left=self.hashs_tab))
        color_tex(theorem_tex, t2c={"2": K_UNIVERSAL_COLOR, "\mathcal{H}": FUNCS_COLOR}, tex_class=MathTex)
        self.play(Write(theorem_tex))

        self.next_section("alternative perspective")
        self.play(Unwrite(theorem_tex))
        self.play_alternative_perspective()
        self.next_section("Show proof")
        self.play_proof()

    def play_alternative_perspective(self):
        universal_def = get_universal_hash_family_def()
        two_universal_def = get_two_universal_def()
        partition_line = Line(LEFT, RIGHT).scale_to_fit_width(
            0.9 * (config.frame_width / 2 - self.hashs_tab.get_right()[0])).move_to(
            get_frame_center(top=self.title, left=self.hashs_tab))
        down_arrow = Tex(r"$\Downarrow$").scale(1.3).move_to(partition_line)

        two_universal_def.move_to(get_frame_center(top=self.title, left=self.hashs_tab, bottom=partition_line))
        universal_def.move_to(get_frame_center(top=partition_line, left=self.hashs_tab))

        self.play(*map(Write, [universal_def, two_universal_def, down_arrow]))

        self.next_section("Show alternative proof")
        self.play(Unwrite(down_arrow), Unwrite(two_universal_def))
        self.play(Write(partition_line))

        single_probs_tex = MathTex(*[
            rf"\mathbb{{P}}[h\left(x_{{1}}\right)=h\left(x_{{3}}\right)={i if i != 4 else 'm'}]" if i != 3 else "\ldots"
            for i in range(5)], arg_separator="+").match_width(partition_line).align_to(self.hashs_tab, UP).match_x(
            partition_line)
        color_tex(single_probs_tex, t2c={"h": FUNCS_COLOR, "x_{1}": SELECT_KEY_COLOR, "x_{3}": SELECT_KEY_COLOR},
                  tex_class=MathTex)

        self.play(Write(single_probs_tex))

        alternative_def = MathTex(
            *[r"\mathbb{P}\left[\begin{matrix}\hspace{1cm}\\\hspace{1cm}\end{matrix}\right]"] * len(single_probs_tex),
            arg_separator="+")
        alternative_def.match_width(single_probs_tex).next_to(single_probs_tex, DOWN, buff=0.35)

        colors = [RED_C, BLUE_C, GOLD_C, MAROON_C, PURPLE_C]
        prob_parentheses = alternative_def[0][1:3]
        prob_squares = VGroup(*[Square(color=colors[i], fill_opacity=0.6).match_height(
            prob_parentheses).scale(0.9).move_to(alternative_def[i][1:3]) for i in range(len(alternative_def))])

        self.play(Write(alternative_def), Write(prob_squares))
        bg_cells = VGroup(
            *[VGroup(
                *[self.hashs_tab.get_highlighted_cell((j, i), color=PROB_BG_CELL_COLOR, fill_opacity=0, z_index=-20) for
                  i in range(1, 5)]) for j in range(1, 5)])

        self.play(*[anim for i in range(5) for anim in
                    animate_collision_prob(0, 2, self.hashs_tab, bg_cells, i, i, cell_color=colors[i],
                                           cells_opacity=0.6, change_others_opacity=False)])

        self.next_section("Show bracket")
        single_probs_bracket = VGroup(
            *[BraceLabel(alternative_def[i][1:3], r"\leq\frac{1}{m^2}", DOWN, font_size=20, buff=0.02) for i in
              range(len(prob_squares))])
        for brace in single_probs_bracket:
            brace.brace.put_at_tip(brace.label, buff=0.05)
        first_write_idx = 2
        self.play(Write(single_probs_bracket[first_write_idx]))

        self.next_section("Show all brackets")
        self.play(*[Write(single_probs_bracket[i]) for i in range(len(single_probs_bracket)) if i != first_write_idx])

        self.next_section("Show final bracket")
        total_bracket = BraceLabel(single_probs_bracket, r"\leq\frac{1}{m}", DOWN, font_size=30, buff=0.05)
        total_bracket.brace.put_at_tip(total_bracket.label, buff=0.1)
        self.play(Write(total_bracket))
        self.play(universal_def.animate.next_to(partition_line, DOWN, buff=0.2))

        self.next_section("Show final result")
        univ_alter_prob = MathTex(
            r"\mathbb{P}\left[\begin{matrix}\hspace{1cm}\\\hspace{1cm}\end{matrix}\right]\leq\frac{1}{m}")
        univ_prob_square = Square(stroke_color=GREEN, fill_color=PROB_BG_CELL_COLOR, fill_opacity=1).match_height(
            univ_alter_prob[0][1:3]).scale(0.9).move_to(univ_alter_prob[0][1:3])
        univ_alter_prob_group = VGroup(univ_alter_prob, univ_prob_square).move_to(
            get_frame_center(top=universal_def, left=self.hashs_tab))
        self.play(*animate_collision_prob(0, 2, self.hashs_tab, bg_cells), Write(univ_alter_prob_group))

        self.next_section("end proof")
        self.play(
            *map(Unwrite, [self.hashs_tab, bg_cells, partition_line, universal_def, single_probs_tex, alternative_def,
                           prob_squares, single_probs_bracket, total_bracket, univ_alter_prob_group]))

    def play_proof(self):
        two_univ_assumption = Tex(r"Assume $\mathcal{H}$ is $2$-universal:").next_to(self.title, DOWN,
                                                                                     buff=0.5).align_to(self.title,
                                                                                                        LEFT)
        self.play(Write(two_univ_assumption))

        self.next_section("Show step")
        proof = VGroup(MathTex(r"\mathbb{P}\left[h\left(x\right)=h\left(y\right)\right]",
                               r"=\mathbb{P}\left[\left(h\left(x\right)=h\left(y\right)=1\right)\lor\ldots\lor\left(h\left(x\right)=h\left(y\right)=m\right)\right]"),
                       MathTex(
                           r"\leq\sum_{i=1}^{m}\mathbb{P}\left[h\left(x\right)=h\left(y\right)=i\right]"),
                       MathTex(
                           r"\leq\sum_{i=1}^{m}\frac{1}{m^{2}}", r"=\frac{1}{m}")).arrange(DOWN,
                                                                                           buff=0.6).scale_to_fit_width(
            config.frame_width * 0.9)

        for i, line in enumerate(proof):
            color_tex(line, t2c={"x": SELECT_KEY_COLOR, "y": SELECT_KEY_COLOR, "h": FUNCS_COLOR},
                      tex_class=MathTex)

            if i != 0:
                line.align_to(proof[0][1], LEFT)

        proof.move_to(get_frame_center(top=two_univ_assumption)).align_to(two_univ_assumption, LEFT)

        vdots = MathTex(r"\vdots").scale(3).move_to(
            get_frame_center(left=proof[0][0], top=proof[0][0], bottom=proof[-1][-1], right=proof[-1][-1]))
        self.play(Write(proof[0][0]), Write(vdots), Write(proof[-1][-1]))

        proof_steps = VGroup(proof[0][1], *proof[1:-1], proof[-1][0])
        self.next_section("Proof steps")
        self.play(Unwrite(vdots))
        self.play(Write(proof_steps[0]))
        union_bound = get_unit_bound().scale_to_fit_width(
            (config.frame_width / 2 + proof_steps[1].get_left()[0]) * 0.6).next_to(proof_steps[1], LEFT, buff=0.6)
        union_bound += Tex("Union Bound").match_width(union_bound).scale(0.5).next_to(union_bound, UP, buff=0.1,
                                                                                      aligned_edge=LEFT)
        for i, step in enumerate(proof_steps[1:], start=1):
            self.next_section(f"Proof step {i + 1}")
            if i == 1:
                self.play(Write(step), Write(union_bound))
            else:
                self.play(Write(step))

        self.next_section("end proof")
        self.play(*map(Unwrite, [self.title, two_univ_assumption, proof, union_bound]))
        self.wait()


if __name__ == "__main__":
    scenes_lst = [Intro, HashTableRecipe, UniversalHashFamilies, UniversalHashExamples, UniversalHashBaseExample,
                  CheckTriplets, KUniversalHashFamilies, TwoUniversalsAreUniversal]
    scenes_lst = [Intro]

    render_scenes(scenes_lst, OUT_DIR, PRESENTATION_MODE, DISABLE_CACHING, gif_scenes=[18 + i for i in range(5)],
                  create_gif=False)
