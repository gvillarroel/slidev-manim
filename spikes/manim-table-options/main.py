#!/usr/bin/env -S uv run --script
# /// script
# dependencies = [
#   "manim>=0.20.0",
# ]
# ///

from __future__ import annotations

import argparse
import os
import shutil
import subprocess
import sys
from pathlib import Path

from manim import (
    DOWN,
    LEFT,
    RIGHT,
    UP,
    Circle,
    Create,
    FadeIn,
    FadeOut,
    Rectangle,
    Scene,
    Square,
    Star,
    SurroundingRectangle,
    Table,
    Text,
    Triangle,
    VGroup,
    VMobject,
    Write,
    rate_functions,
)

SPIKE_DIR = Path(__file__).resolve().parent
REPO_ROOT = SPIKE_DIR.parent.parent
SPIKE_NAME = SPIKE_DIR.name
OUTPUT_DIR = REPO_ROOT / "videos" / SPIKE_NAME
STAGING_DIR = OUTPUT_DIR / ".manim"
VIDEO_PATH = OUTPUT_DIR / f"{SPIKE_NAME}.webm"
POSTER_PATH = OUTPUT_DIR / f"{SPIKE_NAME}.png"

PRIMARY_RED = "#9e1b32"
PRIMARY_ORANGE = "#e77204"
PRIMARY_YELLOW = "#f1c319"
PRIMARY_GREEN = "#45842a"
PRIMARY_BLUE = "#007298"
PRIMARY_PURPLE = "#652f6c"
BLACK = "#000000"
WHITE = "#ffffff"
GRAY = "#333e48"
GRAY_100 = "#e7e7e7"
GRAY_200 = "#cfcfcf"
GRAY_300 = "#b5b5b5"
GRAY_400 = "#9c9c9c"
GRAY_600 = "#696969"
GRAY_700 = "#4f4f4f"
PAGE_BACKGROUND = "#f7f7f7"
HIGHLIGHT_RED = "#ffccd5"
HIGHLIGHT_ORANGE = "#ffe5cc"
HIGHLIGHT_YELLOW = "#fff4cc"
HIGHLIGHT_GREEN = "#dbffcc"
HIGHLIGHT_BLUE = "#cdf3ff"
HIGHLIGHT_PURPLE = "#f9ccff"

FONT = "Arial"
DATA = [["10", "20", "30"], ["15", "25", "35"], ["18", "28", "38"]]
ROWS = ["r1", "r2", "r3"]
COLS = ["A", "B", "C"]


class _Args(argparse.Namespace):
    quality: str
    preview: bool


def parse_args() -> _Args:
    parser = argparse.ArgumentParser(description="Render the Manim Table options spike.")
    parser.add_argument(
        "--quality",
        choices=("low", "medium", "high", "production", "4k"),
        default="medium",
        help="Manim quality preset. Defaults to medium for presentation review.",
    )
    parser.add_argument("--preview", action="store_true", help="Open the rendered output after rendering.")
    return parser.parse_args(namespace=_Args())


def quality_flag(quality: str) -> str:
    return {
        "low": "-ql",
        "medium": "-qm",
        "high": "-qh",
        "production": "-qp",
        "4k": "-qk",
    }[quality]


def render_command(args: _Args, poster: bool) -> list[str]:
    STAGING_DIR.mkdir(parents=True, exist_ok=True)
    target = POSTER_PATH if poster else VIDEO_PATH
    command = [
        sys.executable,
        "-m",
        "manim",
        "render",
        quality_flag(args.quality),
        "-r",
        "1600,900",
        "--media_dir",
        str(STAGING_DIR),
        "-o",
        target.stem,
    ]
    command.append("-s" if poster else "--format=webm")
    if not poster:
        command.append("-t")
    if args.preview:
        command.append("-p")
    command.extend([str(Path(__file__).resolve()), "ManimTableOptionsScene"])
    return command


def promote(target_name: str, destination: Path) -> None:
    matches = sorted(STAGING_DIR.glob(f"**/{target_name}"))
    if not matches:
        raise FileNotFoundError(f"Could not find {target_name} under {STAGING_DIR}")
    destination.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(max(matches, key=lambda path: path.stat().st_mtime), destination)


def text(value: str, size: int = 24, color: str = GRAY, weight: str | None = None) -> Text:
    kwargs = {"font_size": size, "color": color, "font": FONT}
    if weight is not None:
        kwargs["weight"] = weight
    return Text(value, **kwargs)


def mono(value: str, size: int = 19, color: str = GRAY) -> Text:
    return Text(value, font="Consolas", font_size=size, color=color)


def table_element(
    value: str | float | VMobject,
    font_size: int = 21,
    color: str = GRAY,
    font: str = FONT,
    weight: str | None = None,
) -> VMobject:
    if isinstance(value, VMobject):
        return value
    kwargs = {"font_size": font_size, "color": color, "font": font}
    if weight is not None:
        kwargs["weight"] = weight
    return Text(str(value), **kwargs)


def label_list(names: list[str], color: str = GRAY_700) -> VGroup:
    items = VGroup(*[mono(name, size=16, color=color) for name in names])
    items.arrange(DOWN, aligned_edge=LEFT, buff=0.08)
    return items


def fit(mob: VMobject, max_width: float, max_height: float) -> VMobject:
    if mob.width > max_width:
        mob.scale_to_fit_width(max_width)
    if mob.height > max_height:
        mob.scale_to_fit_height(max_height)
    return mob


def demo_table(
    *,
    row_labels: bool = False,
    col_labels: bool = False,
    top_left_entry: bool = False,
    include_outer_lines: bool = False,
    h_buff: float = 0.8,
    v_buff: float = 0.45,
    line_color: str = GRAY_300,
    line_width: float = 1.7,
    element_color: str = GRAY,
    element_size: int = 21,
    alignment=RIGHT,
    add_entry_backgrounds: bool = False,
    table_background: bool = False,
    data: list[list[str | VMobject]] | None = None,
) -> Table:
    kwargs = {
        "v_buff": v_buff,
        "h_buff": h_buff,
        "include_outer_lines": include_outer_lines,
        "element_to_mobject": table_element,
        "element_to_mobject_config": {
            "font_size": element_size,
            "color": element_color,
            "font": FONT,
        },
        "arrange_in_grid_config": {"cell_alignment": alignment},
        "line_config": {"color": line_color, "stroke_width": line_width},
    }
    if row_labels:
        kwargs["row_labels"] = [text(row, 17, GRAY_700, "BOLD") for row in ROWS]
    if col_labels:
        kwargs["col_labels"] = [text(col, 17, GRAY_700, "BOLD") for col in COLS]
    if top_left_entry:
        kwargs["top_left_entry"] = text("#", 17, GRAY_700, "BOLD")
    if add_entry_backgrounds:
        kwargs["add_background_rectangles_to_entries"] = True
        kwargs["entries_background_color"] = HIGHLIGHT_YELLOW
    if table_background:
        kwargs["include_background_rectangle"] = True
        kwargs["background_rectangle_color"] = WHITE

    return Table(data or DATA, **kwargs)


def option_card(title: str, table: Table, methods: list[str], accent: str = PRIMARY_RED) -> VGroup:
    panel = Rectangle(
        width=5.35,
        height=2.42,
        stroke_color=GRAY_200,
        stroke_width=1.5,
        fill_color=WHITE,
        fill_opacity=0.96,
    )
    heading = mono(title, size=18, color=accent)
    heading.move_to(panel.get_top() + DOWN * 0.28)
    heading.set_z_index(3)

    fit(table, 4.95, 1.35)
    table.move_to(panel.get_center() + DOWN * 0.06)
    table.set_z_index(2)

    methods_group = label_list(methods)
    fit(methods_group, 4.95, 0.34)
    methods_group.move_to(panel.get_bottom() + UP * 0.24)
    methods_group.set_z_index(3)

    return VGroup(panel, heading, table, methods_group)


def page_title(title: str, subtitle: str) -> VGroup:
    title_mob = text(title, size=29, color=GRAY, weight="BOLD")
    subtitle_mob = text(subtitle, size=17, color=GRAY_700)
    block = VGroup(title_mob, subtitle_mob).arrange(DOWN, buff=0.12)
    backing = Rectangle(
        width=11.5,
        height=block.height + 0.28,
        stroke_color=GRAY_200,
        stroke_width=1.2,
        fill_color=WHITE,
        fill_opacity=0.96,
    )
    backing.move_to(block.get_center())
    block.add_to_back(backing)
    block.to_edge(UP, buff=0.48)
    return block


def constructor_page() -> VGroup:
    default = option_card(
        "default grid",
        demo_table(),
        ["table", "v_buff", "h_buff"],
        PRIMARY_RED,
    )
    labeled = option_card(
        "labels + corner",
        demo_table(row_labels=True, col_labels=True, top_left_entry=True, include_outer_lines=True),
        ["row_labels", "col_labels", "top_left_entry"],
        PRIMARY_BLUE,
    )
    aligned = option_card(
        "compact right align",
        demo_table(
            row_labels=True,
            col_labels=True,
            h_buff=0.42,
            v_buff=0.28,
            alignment=RIGHT,
            element_size=19,
        ),
        ["arrange_in_grid_config", "cell_alignment"],
        PRIMARY_GREEN,
    )
    line_style = option_card(
        "outer + line style",
        demo_table(
            row_labels=True,
            col_labels=True,
            top_left_entry=True,
            include_outer_lines=True,
            line_color=PRIMARY_ORANGE,
            line_width=2.6,
        ),
        ["include_outer_lines", "line_config"],
        PRIMARY_ORANGE,
    )
    cards = VGroup(default, labeled, aligned, line_style).arrange_in_grid(rows=2, cols=2, buff=(0.36, 0.28))
    cards.move_to(DOWN * 0.45)
    return VGroup(
        page_title("Manim Table constructor options", "Buffers, labels, alignment, outer lines, and line style"),
        cards,
    )


def backgrounds_page() -> VGroup:
    entry_bg = option_card(
        "entry backplates",
        demo_table(row_labels=True, col_labels=True, add_entry_backgrounds=True),
        ["add_background_rectangles_to_entries", "entries_background_color"],
        PRIMARY_YELLOW,
    )
    table_bg = option_card(
        "whole table backing",
        demo_table(
            row_labels=True,
            col_labels=True,
            include_outer_lines=True,
            table_background=True,
            line_color=GRAY_400,
        ),
        ["include_background_rectangle", "background_rectangle_color"],
        PRIMARY_PURPLE,
    )
    text_config = option_card(
        "custom text entries",
        demo_table(
            row_labels=True,
            col_labels=True,
            element_color=PRIMARY_BLUE,
            element_size=25,
            h_buff=0.62,
        ),
        ["element_to_mobject", "element_to_mobject_config"],
        PRIMARY_BLUE,
    )
    shape_data: list[list[str | VMobject]] = [
        [
            Square(side_length=0.28, color=PRIMARY_RED, fill_color=HIGHLIGHT_RED, fill_opacity=1),
            Circle(radius=0.18, color=PRIMARY_BLUE, fill_color=HIGHLIGHT_BLUE, fill_opacity=1),
        ],
        [
            Star(n=5, outer_radius=0.22, color=PRIMARY_ORANGE, fill_color=HIGHLIGHT_ORANGE, fill_opacity=1),
            Triangle(color=PRIMARY_GREEN, fill_color=HIGHLIGHT_GREEN, fill_opacity=1).scale(0.28),
        ],
    ]
    shape_mix = option_card(
        "VMobject cells",
        demo_table(
            data=shape_data,
            h_buff=0.65,
            v_buff=0.45,
            include_outer_lines=True,
            alignment=RIGHT,
        ),
        ["table entries as VMobject"],
        PRIMARY_GREEN,
    )
    cards = VGroup(entry_bg, table_bg, text_config, shape_mix).arrange_in_grid(rows=2, cols=2, buff=(0.36, 0.28))
    cards.move_to(DOWN * 0.45)
    return VGroup(
        page_title("Backgrounds and entry conversion", "Constructor flags plus custom element conversion"),
        cards,
    )


def cell_helpers_page() -> VGroup:
    table = demo_table(
        row_labels=True,
        col_labels=True,
        top_left_entry=True,
        include_outer_lines=True,
        h_buff=0.76,
        v_buff=0.46,
        line_color=GRAY_400,
    )
    fit(table, 6.35, 3.72)
    table.move_to(LEFT * 2.2 + DOWN * 1.35)
    table.add_background_to_entries(color=HIGHLIGHT_BLUE)

    soft_cell = table.get_highlighted_cell((2, 3), color=HIGHLIGHT_GREEN, fill_opacity=0.86)
    table.add_to_back(soft_cell)
    table.add_highlighted_cell((1, 1), color=HIGHLIGHT_YELLOW, fill_opacity=0.9)
    outline = table.get_cell((3, 2), color=PRIMARY_RED, stroke_width=4)
    outline.set_fill(opacity=0)
    outline.set_z_index(5)
    table.add(outline)

    legend_panel = Rectangle(
        width=4.2,
        height=3.45,
        stroke_color=GRAY_200,
        stroke_width=1.5,
        fill_color=WHITE,
        fill_opacity=0.96,
    )
    legend_panel.move_to(RIGHT * 3.9 + DOWN * 1.35)
    legend_title = mono("cell helpers", size=21, color=PRIMARY_RED)
    legend_title.move_to(legend_panel.get_top() + DOWN * 0.34)
    legend = label_list(
        [
            "add_background_to_entries",
            "get_highlighted_cell((2, 3))",
            "add_highlighted_cell((1, 1))",
            "get_cell((3, 2))",
        ],
        color=GRAY,
    )
    legend.move_to(legend_panel.get_center() + DOWN * 0.16)
    return VGroup(
        page_title("Addressing cells", "Background rectangles and polygon cell outlines use 1-based table positions"),
        table,
        VGroup(legend_panel, legend_title, legend),
    )


def accessors_page() -> VGroup:
    table = demo_table(
        row_labels=True,
        col_labels=True,
        top_left_entry=True,
        include_outer_lines=True,
        h_buff=0.72,
        v_buff=0.44,
        line_color=GRAY_400,
    )
    table.get_col_labels().set_color(PRIMARY_BLUE)
    table.get_row_labels().set_color(PRIMARY_GREEN)
    table.get_labels().set_opacity(1)
    table.get_entries((2, 2)).set_color(PRIMARY_RED).scale(1.16)
    table.get_entries_without_labels((3, 3)).set_color(PRIMARY_PURPLE).scale(1.16)
    row_box = SurroundingRectangle(table.get_rows()[2], color=PRIMARY_ORANGE, buff=0.08, stroke_width=3.2)
    col_box = SurroundingRectangle(table.get_columns()[3], color=PRIMARY_PURPLE, buff=0.08, stroke_width=3.2)
    row_box.set_fill(opacity=0)
    col_box.set_fill(opacity=0)
    table.add(row_box, col_box)
    fit(table, 7.25, 3.9)
    table.move_to(LEFT * 1.95 + DOWN * 1.35)

    legend_panel = Rectangle(
        width=4.56,
        height=3.72,
        stroke_color=GRAY_200,
        stroke_width=1.5,
        fill_color=WHITE,
        fill_opacity=0.96,
    )
    legend_panel.move_to(RIGHT * 3.62 + DOWN * 1.35)
    legend_title = mono("read accessors", size=21, color=PRIMARY_BLUE)
    legend_title.move_to(legend_panel.get_top() + DOWN * 0.34)
    legend = label_list(
        [
            "get_entries / get_entries_without_labels",
            "get_labels",
            "get_row_labels / get_col_labels",
            "get_rows / get_columns",
        ],
        color=GRAY,
    )
    fit(legend, 4.1, 2.7)
    legend.move_to(legend_panel.get_center() + DOWN * 0.12)
    return VGroup(
        page_title("Reading table parts", "Accessors return VMobjects or VGroups that can be styled after creation"),
        table,
        VGroup(legend_panel, legend_title, legend),
    )


def line_and_color_shell() -> tuple[VGroup, Table, VGroup]:
    title = page_title("Lines, color setters, create, and scale", "The last page animates Table.create() before styling parts in place")
    table = demo_table(
        row_labels=True,
        col_labels=True,
        top_left_entry=True,
        include_outer_lines=True,
        h_buff=0.86,
        v_buff=0.46,
        line_color=GRAY_400,
        line_width=2,
    )
    fit(table, 6.9, 3.9)
    table.move_to(LEFT * 1.2 + DOWN * 0.1)

    panel = Rectangle(
        width=4.62,
        height=3.65,
        stroke_color=GRAY_200,
        stroke_width=1.5,
        fill_color=WHITE,
        fill_opacity=0.96,
    )
    panel.move_to(RIGHT * 3.72 + DOWN * 0.1)
    methods = label_list(
        [
            "create(line_animation=Create)",
            "get_horizontal_lines()",
            "get_vertical_lines()",
            "set_column_colors(...)",
            "set_row_colors(...)",
            "scale(.92, scale_stroke=True)",
        ],
        color=GRAY,
    )
    fit(methods, 4.16, 2.85)
    methods.move_to(panel.get_center())
    heading = mono("animated method pass", size=21, color=PRIMARY_PURPLE)
    heading.move_to(panel.get_top() + DOWN * 0.34)
    shell = VGroup(title, panel, heading, methods)
    return shell, table, methods


class ManimTableOptionsScene(Scene):
    def construct(self) -> None:
        self.camera.background_color = PAGE_BACKGROUND

        stage = Rectangle(
            width=12.35,
            height=6.9,
            stroke_color=GRAY_200,
            stroke_width=1.5,
            fill_color=PAGE_BACKGROUND,
            fill_opacity=0.98,
        )
        stage.set_z_index(-20)
        self.add(stage)

        current = constructor_page()
        self.add(current)
        self.wait(2.75)

        for page in (backgrounds_page(), cell_helpers_page(), accessors_page()):
            self.play(FadeOut(current, shift=UP * 0.08), run_time=0.45)
            current = page
            self.play(FadeIn(current, shift=UP * 0.06), run_time=0.65)
            self.wait(4.05)

        shell, table, methods = line_and_color_shell()
        self.play(FadeOut(current, shift=UP * 0.08), run_time=0.45)
        self.play(FadeIn(shell, shift=UP * 0.06), run_time=0.65)
        self.play(
            table.create(
                lag_ratio=0.24,
                line_animation=Create,
                label_animation=Write,
                element_animation=FadeIn,
                entry_animation=FadeIn,
            ),
            run_time=2.15,
        )
        self.wait(0.55)
        self.play(
            table.get_horizontal_lines().animate.set_color(PRIMARY_ORANGE).set_stroke(width=3.2),
            table.get_vertical_lines().animate.set_color(PRIMARY_BLUE).set_stroke(width=3.2),
            methods[1].animate.set_color(PRIMARY_ORANGE),
            methods[2].animate.set_color(PRIMARY_BLUE),
            run_time=0.85,
        )
        self.play(
            table.animate.set_column_colors(GRAY_700, PRIMARY_BLUE, PRIMARY_GREEN, PRIMARY_PURPLE),
            methods[3].animate.set_color(PRIMARY_GREEN),
            run_time=0.9,
            rate_func=rate_functions.ease_out_cubic,
        )
        self.play(
            table.animate.set_row_colors(GRAY_700, PRIMARY_RED, PRIMARY_ORANGE, PRIMARY_YELLOW),
            methods[4].animate.set_color(PRIMARY_RED),
            run_time=0.9,
            rate_func=rate_functions.ease_out_cubic,
        )
        self.play(
            table.animate.scale(0.92, scale_stroke=True).shift(LEFT * 0.18),
            methods[5].animate.set_color(PRIMARY_PURPLE),
            run_time=0.75,
            rate_func=rate_functions.ease_out_cubic,
        )
        self.wait(6.0)


def render_variant(args: _Args) -> None:
    for poster in (False, True):
        result = subprocess.run(
            render_command(args, poster),
            check=False,
            env={**os.environ, "SPIKE_RENDER_TARGET": "poster" if poster else "video"},
        )
        if result.returncode != 0:
            raise SystemExit(result.returncode)
        target = POSTER_PATH if poster else VIDEO_PATH
        promote(target.name, target)


def main() -> int:
    args = parse_args()
    render_variant(args)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
