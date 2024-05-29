from __future__ import annotations

from manim import MathTex

from tools.consts import PROBABILITY_SPACE_BACK_COLOR
from tools.funcs import color_tex, get_frame_center
from tools.hash_table import HashTable
from tools.scenes import *
import string

FUNCS_COLOR = YELLOW
SELECT_KEY_COLOR = BLUE
K_UNIVERSAL_COLOR = GREEN
SUB_TITLES_SCALE = 0.7
PROB_BG_CELL_COLOR = "#4f6c44"
PROB_BG_CELL_OPACITY = 0.5
DEFAULT_HASH_FAMILY_TABLE_SIZE = 4
HASH_TABLE_FUNCS_TITLE_BUFF = -0.15


def get_universal_hash_family_def() -> Tex:
    universal_def = MathTex(
        r"\forall x\neq y\in U,\underset{h\in\mathcal{H}}{\mathbb{P}}\left[h\left(x\right)=h\left(y\right)\right]\leq\frac{1}{m}")
    color_tex(universal_def, t2c={r"x": SELECT_KEY_COLOR, r"y": SELECT_KEY_COLOR, "h": FUNCS_COLOR}, tex_class=MathTex)
    return universal_def


def get_two_universal_def() -> Tex:
    two_universal_def = MathTex(r'''\begin{matrix}\begin{matrix}\mathbin{\forall}y_{1}\neq y_{2}\in U\\
    \mathbin{\forall}i_{1},i_{2}\in\left[m\right]
    \end{matrix}\\
    \underset{h\in\mathcal{H}}{\mathbb{P}}\left[h\left(y_{1}\right)=i_{1}\land h\left(y_{2}\right)=i_{2}\right]\leq\frac{1}{m^{2}}
    \end{matrix}''')
    color_tex(two_universal_def, t2c={**{i: SELECT_KEY_COLOR for i in ["y_{1}", "y_{2}"]}, "h": FUNCS_COLOR},
              tex_class=MathTex)
    two_universal_def[0][-1].set_color(K_UNIVERSAL_COLOR)
    return two_universal_def


def get_funcs_bowl(num_format=int, last_func_idx: str = r"\left|\mathcal{H}\right|", gaps=None) -> VGroup:
    gaps = [7, 5] if gaps is None else gaps
    funcs_bowl = Arc(start_angle=PI, angle=PI).scale(3)
    funcs = VGroup()
    funcs_scale = 1.3
    for i in range(1, 1 + gaps[0]):
        funcs += MathTex(fr"h_{{{num_format(i)}}}").scale(funcs_scale)
    funcs.arrange(RIGHT)

    a = VGroup()
    for i in range(1 + gaps[0], 1 + gaps[0] + gaps[1]):
        a += MathTex(fr"h_{{{num_format(i)}}}").scale(funcs_scale)
    funcs += a.arrange(RIGHT).next_to(funcs, DOWN)
    funcs += MathTex(r"\vdots").next_to(funcs, DOWN)
    funcs += MathTex(rf"h_{{{last_func_idx}}}").next_to(funcs, DOWN).scale(funcs_scale)
    funcs.match_height(funcs_bowl).scale(0.9).move_to(funcs_bowl).set_color(FUNCS_COLOR)
    return VGroup(funcs_bowl, funcs)


def get_main_hash_table_example() -> tuple[np.ndarray, HashTable]:
    frame_center = get_frame_center(top=Title("abc"))
    hash_table_shift = DOWN * 0.6
    hash_map = {0: 1, 1: 0, 2: 2, 3: 3, 5: 2}
    hash_table = HashTable(6, 5, lambda i: hash_map[i], keys_array_gap_size=6,
                           arrows_config={"tip_length": 1.5, "stroke_width": 6,
                                          "max_tip_length_to_length_ratio": 0.35}).scale_to_fit_height(
        config.frame_height * 0.5)
    hash_table.shift(-hash_table.keys.get_center()).set_y(frame_center[1]).shift(hash_table_shift)
    return frame_center, hash_table


def get_hash_family_table(array_size: int, keys_size: int,
                          table_size: int = DEFAULT_HASH_FAMILY_TABLE_SIZE, seed=None) -> MobjectTable:
    if seed is not None:
        np.random.seed(seed)
    random_mapping = [[{i: np.random.randint(0, array_size) for i in range(keys_size)} for _ in range(table_size)]
                      for _ in range(table_size)]
    tables = [[HashTable(keys_size, array_size, lambda x, i=i, j=j: random_mapping[i][j][x],
                         arrows_config=dict(tip_length=2, stroke_width=3), keys_array_gap_size=3.5) for
               i in range(table_size)] for j in range(table_size)]
    tables[-2][-1] = MathTex(r"\vdots").scale(4.5)
    tables[-1][-2] = MathTex(r"\ldots").scale(4.5)
    hashs_tab = MobjectTable(tables, include_outer_lines=True).scale_to_fit_height(
        config.frame_height * 0.8).to_edge(LEFT)
    hashs_tab += BackgroundRectangle(hashs_tab, color=PROBABILITY_SPACE_BACK_COLOR, z_index=-30)
    return hashs_tab


def get_hash_table_subtitles(hash_table: HashTable) -> tuple[VGroup, VGroup, VGroup]:
    array_text = Text("array").scale(SUB_TITLES_SCALE).next_to(hash_table, UP, buff=1.2).match_x(hash_table.array)
    keys_text = Text("keys").scale(SUB_TITLES_SCALE).next_to(hash_table, UP, buff=1.2).match_x(hash_table.keys)
    hash_function_text = MathTex(r"h", color=FUNCS_COLOR).next_to(hash_table, UP,
                                                                  buff=HASH_TABLE_FUNCS_TITLE_BUFF).match_x(hash_table)
    return array_text, keys_text, hash_function_text


def animate_collision_prob(i: int, j: int, hashs_tab: MobjectTable,
                           bg_cells: VGroup = None, i_1: int = None, i_2: int = None,
                           cell_color: str = PROB_BG_CELL_COLOR, cells_opacity: float = 1,
                           change_others_opacity: bool = True) -> list[Animation]:
    animations = []
    if bg_cells is None:
        bg_cells = VGroup(
            *[VGroup(
                *[hashs_tab.get_highlighted_cell((j, i), color=cell_color, fill_opacity=0, z_index=-20) for
                  i in range(1, hashs_tab.row_dim + 1)]) for j in range(1, hashs_tab.col_dim + 1)])

    for hash_table_ij in hashs_tab.elements:
        if not isinstance(hash_table_ij, HashTable): continue
        for key_idx, key in enumerate(hash_table_ij.keys):
            animations.append(
                key.value_mob.animate.set_color(SELECT_KEY_COLOR if key_idx in [i, j] else WHITE))

    for i_tab in range(1, hashs_tab.row_dim + 1):
        for j_tab in range(1, hashs_tab.col_dim + 1):
            colored_arrows = []
            hash_table_ij = hashs_tab.get_entries((i_tab, j_tab))
            if not isinstance(hash_table_ij, HashTable): continue
            if (hash_table_ij.hash_func(i) == hash_table_ij.hash_func(j) and (i_1 == None or i_2 == None)) or (
                    hash_table_ij.hash_func(i) == i_1 and hash_table_ij.hash_func(j) == i_2):
                animations.append(
                    bg_cells[i_tab - 1][j_tab - 1].animate.set_fill(color=cell_color, opacity=cells_opacity))
                for idx in [i, j]:
                    colored_arrows.append(hash_table_ij.get_arrow(idx))
                    animations.append(
                        hash_table_ij.get_arrow(idx).animate.set_color(SELECT_KEY_COLOR).set_z_index(10))
                    animations.append(hash_table_ij.keys[idx].value_mob.animate.set_color(SELECT_KEY_COLOR))
            elif change_others_opacity:
                animations.append(bg_cells[i_tab - 1][j_tab - 1].animate.set_fill(opacity=0))
            else:
                continue

            for arrow in hash_table_ij.arrows:
                if arrow not in colored_arrows:
                    animations.append(arrow.animate.set_color(FUNCS_COLOR).set_z_index(1))
    return animations


def get_hash_func(p: int, k: int, a: int):
    return lambda x: int(sum((a // p ** i % p) * (x // p ** i % p) for i in range(k))) % p


class IntegerBase(Integer):
    def __init__(self, value, base, zeroes_padding=8, zeroes_opacity: float = 0.3, **kwargs):
        self.base = base
        self.zeroes_padding = zeroes_padding
        self.zeroes_opacity = zeroes_opacity
        self.digs = string.digits + string.ascii_uppercase
        super().__init__(value, **kwargs)
        self.set_value(value)

    def set_value(self, value, align_digits: bool = True):
        old_val = self.copy()
        super().set_value(value)
        zeroes_number = self.zeroes_padding - len(self._get_num_string(value).lstrip('0'))
        if zeroes_number > 0:
            self[:zeroes_number].set_opacity(self.zeroes_opacity)
        if align_digits:
            for i, digit in enumerate(self):
                digit.match_x(old_val[i])

    def _get_num_string(self, number):
        number = int(np.round(number, self.num_decimal_places))
        if number < 0:
            sign = -1
        elif number == 0:
            return self.digs[0].zfill(self.zeroes_padding)
        else:
            sign = 1

        number *= sign
        digits = []

        while number:
            digits.append(self.digs[number % self.base])
            number = number // self.base

        if sign < 0:
            digits.append('-')

        digits.reverse()
        return ''.join(digits).zfill(self.zeroes_padding)


class Count(Animation):
    def __init__(self, number: DecimalNumber, start: float, end: float, align=None, **kwargs) -> None:
        # Pass number as the mobject of the animation
        super().__init__(number, **kwargs)
        # Set start and end
        self.start = start
        self.end = end
        self.origin_mob = number.copy()
        self.align = align

    def interpolate_mobject(self, alpha: float) -> None:
        # Set value of DecimalNumber according to alpha
        value = self.start + (alpha * (self.end - self.start))
        self.mobject.set_value(value)
        if self.align is not None:
            self.mobject.align_to(self.origin_mob, self.align)


def get_base_convert_calc(number: IntegerBase, number_color: str, base_color: str, no_padding: bool = True) -> MathTex:
    number_str = number._get_num_string(number.get_value())
    if no_padding:
        number_str = number_str.lstrip("0")
    math_tex_lst = []
    for idx, dig in enumerate(number_str):
        dig_val = number.digs.index(dig)
        math_tex_lst.append(f"{dig_val}")
        math_tex_lst.append(r"\cdot")
        math_tex_lst.append(rf"{number.base}^{{{len(number_str) - idx - 1}}}")
        if idx != len(number_str) - 1:
            math_tex_lst.append(r"+")
    math_tex_mob = MathTex(*math_tex_lst)
    math_tex_mob[0::4].set_color(number_color)
    math_tex_mob[2::4].set_color(base_color)
    return math_tex_mob


def get_hash_func_calc(p: int, k: int, a: int, x: int, base_color, keys_color, hash_color) -> tuple[MathTex, MathTex]:
    int_base_format = IntegerBase(x, p, zeroes_padding=k)._get_num_string
    a_str = int_base_format(a)
    x_str = int_base_format(x)
    math_tex_lst = [rf"h_{{{a_str}}}\left({x_str}\right)="]
    for i in range(k):
        math_tex_lst.append(rf"{a_str[i]}")
        math_tex_lst.append(rf"\cdot")
        math_tex_lst.append(rf"{x_str[i]}")
        if i != k - 1:
            math_tex_lst.append(r"+")
    math_tex_lst.append(rf" = {get_hash_func(p, k, a)(x)}")
    math_tex = MathTex(*math_tex_lst)
    math_tex[1:-1:4].set_color(hash_color)
    math_tex[3:-1:4].set_color(keys_color)
    color_tex(math_tex, t2c={f"h_{{{a_str}}}": hash_color, f"{x_str}": keys_color}, tex_class=MathTex)
    mod_tex = MathTex(rf"\ \left(\bmod\ {p}\right)").next_to(math_tex, RIGHT)
    mod_tex[0][-2].set_color(base_color)
    return math_tex, mod_tex


def get_univ_def_reminder() -> VGroup:
    reminder = Text("Reminder (Universal Hash Family):").scale(0.7)
    prob_eq = get_universal_hash_family_def().next_to(reminder, DOWN).align_to(reminder, LEFT)
    reminder_text = VGroup(reminder, prob_eq)
    reminder_rect = SurroundingRectangle(reminder_text, stroke_color=WHITE, fill_color=DARK_GREY, corner_radius=0.1,
                                         fill_opacity=0.8)
    return VGroup(reminder_rect, reminder_text)


def get_unit_bound() -> VGroup():
    square_bg_1 = Square(fill_color=PROBABILITY_SPACE_BACK_COLOR, fill_opacity=1).set_z_index(-10)
    right_squares = VGroup(square_bg_1.copy(), MathTex(r"+").scale(1.5), square_bg_1.copy()).set_z_index(-10)
    leq_sign = MathTex(r"\leq").scale(1.5)
    event_1 = Square(stroke_color=GREEN, fill_color=PROB_BG_CELL_COLOR, fill_opacity=1).scale(0.6).align_to(square_bg_1,
                                                                                                            LEFT + UP)
    event_2 = event_1.copy().align_to(square_bg_1, RIGHT + DOWN)
    square_bg_1.add(Union(event_1, event_2, color=PROB_BG_CELL_COLOR, fill_opacity=1).set_stroke(GREEN))
    right_squares[0].add(event_1)
    right_squares[2].add(event_2)
    right_squares.arrange(RIGHT, buff=0.2)

    return VGroup(square_bg_1, leq_sign, right_squares).arrange(RIGHT, buff=0.3)
