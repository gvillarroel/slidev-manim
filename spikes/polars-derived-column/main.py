#!/usr/bin/env -S uv run --script
# /// script
# dependencies = [
#   "manim>=0.20.0",
#   "polars>=1.0.0",
# ]
# ///

from __future__ import annotations

import argparse
import os
import shutil
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path

import polars as pl
from manim import (
    DOWN,
    LEFT,
    RIGHT,
    UP,
    AnimationGroup,
    DashedLine,
    FadeIn,
    FadeOut,
    Indicate,
    Line,
    RoundedRectangle,
    Scene,
    SurroundingRectangle,
    Text,
    ReplacementTransform,
    VGroup,
    rate_functions,
)

SPIKE_DIR = Path(__file__).resolve().parent
REPO_ROOT = SPIKE_DIR.parent.parent
SPIKE_NAME = SPIKE_DIR.name
OUTPUT_DIR = REPO_ROOT / "videos" / SPIKE_NAME
STAGING_DIR = OUTPUT_DIR / ".manim"

PRIMARY_ORANGE = "#e77204"
PRIMARY_YELLOW = "#f1c319"
PRIMARY_GREEN = "#45842a"
PRIMARY_BLUE = "#007298"
PRIMARY_PURPLE = "#652f6c"
WHITE = "#ffffff"
GRAY = "#333e48"
GRAY_200 = "#cfcfcf"
GRAY_300 = "#b5b5b5"
GRAY_400 = "#9c9c9c"
GRAY_700 = "#4f4f4f"
HIGHLIGHT_GREEN = "#dbffcc"
HIGHLIGHT_BLUE = "#cdf3ff"
HIGHLIGHT_PURPLE = "#f9ccff"
PAGE_BACKGROUND = "#f7f7f7"


@dataclass(frozen=True)
class Cell:
    center: object
    box: RoundedRectangle
    text: Text


class _Args(argparse.Namespace):
    quality: str
    preview: bool


def parse_args() -> _Args:
    parser = argparse.ArgumentParser(description="Render the polars-derived-column Manim spike.")
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


def output_paths() -> tuple[Path, Path]:
    return OUTPUT_DIR / f"{SPIKE_NAME}.webm", OUTPUT_DIR / f"{SPIKE_NAME}.png"


def render_command(args: _Args, stem: str, poster: bool) -> list[str]:
    STAGING_DIR.mkdir(parents=True, exist_ok=True)
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
        stem,
    ]

    if poster:
        command.append("-s")
    else:
        command.extend(["--format", "webm", "-t"])

    if args.preview:
        command.append("-p")

    command.extend([str(Path(__file__).resolve()), "PolarsDerivedColumnScene"])
    return command


def promote_rendered_file(target_name: str, destination: Path) -> None:
    matches = sorted(STAGING_DIR.glob(f"**/{target_name}"))
    if not matches:
        raise FileNotFoundError(f"Could not find {target_name} under {STAGING_DIR}")
    destination.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(matches[-1], destination)


def build_dataset() -> pl.DataFrame:
    source = pl.DataFrame(
        {
            "item": ["A", "B", "C", "D"],
            "qty": [3, 5, 2, 4],
            "unit_price": [12, 8, 25, 15],
        }
    )
    return source.with_columns(
        (pl.col("qty") * pl.col("unit_price")).alias("revenue")
    )


def money(value: int) -> str:
    return f"${value}"


def text(
    value: str,
    size: int = 24,
    color: str = GRAY,
    font: str = "Arial",
    weight: str | None = None,
) -> Text:
    kwargs = {"font_size": size, "color": color, "font": font}
    if weight:
        kwargs["weight"] = weight
    return Text(value, **kwargs)


def code_text(value: str, size: int = 22, color: str = GRAY) -> Text:
    return Text(value, font="Consolas", font_size=size, color=color)


class DataTable:
    def __init__(self, frame_left: float = -5.15, frame_top: float = 2.26) -> None:
        self.left = frame_left
        self.top = frame_top
        self.row_height = 0.64
        self.col_widths = [1.18, 1.55, 2.22, 2.15]
        self.headers = ["item", "qty", "unit_price", "revenue"]
        self.header_colors = [GRAY, PRIMARY_GREEN, PRIMARY_BLUE, PRIMARY_PURPLE]
        self.body_fills = [WHITE, HIGHLIGHT_GREEN, HIGHLIGHT_BLUE, HIGHLIGHT_PURPLE]
        self.group = VGroup()
        self.cells: dict[tuple[int, int], Cell] = {}
        self.revenue_texts: list[Text] = []
        self.revenue_column_box: SurroundingRectangle | None = None

    def center_for(self, row: int, col: int) -> object:
        x = self.left + sum(self.col_widths[:col]) + self.col_widths[col] / 2
        y = self.top - row * self.row_height - self.row_height / 2
        return RIGHT * x + UP * y

    def build(self, df: pl.DataFrame) -> VGroup:
        frame = RoundedRectangle(
            width=sum(self.col_widths) + 0.34,
            height=self.row_height * 5 + 0.34,
            corner_radius=0.18,
            stroke_color=GRAY_400,
            stroke_width=2,
            fill_color=WHITE,
            fill_opacity=1,
        )
        frame.move_to(
            RIGHT * (self.left + sum(self.col_widths) / 2)
            + UP * (self.top - self.row_height * 2.5)
        )
        frame.set_z_index(0)
        self.group.add(frame)

        for col, label in enumerate(self.headers):
            cell = self._cell(0, col, label, self.header_colors[col], WHITE, 1, bold=True)
            self.cells[(0, col)] = cell
            self.group.add(cell.box, cell.text)

        for row_index, row in enumerate(df.iter_rows(named=True), start=1):
            values = [
                row["item"],
                str(row["qty"]),
                money(row["unit_price"]),
                "",
            ]
            for col, value in enumerate(values):
                cell = self._cell(row_index, col, value, self.body_fills[col], GRAY, 1)
                self.cells[(row_index, col)] = cell
                self.group.add(cell.box, cell.text)

            revenue_text = text(money(row["revenue"]), size=25, color=PRIMARY_PURPLE, weight="BOLD")
            revenue_text.move_to(self.center_for(row_index, 3))
            revenue_text.set_z_index(3)
            self.revenue_texts.append(revenue_text)

        revenue_cells = VGroup(*[self.cells[(row, 3)].box for row in range(0, 5)])
        self.revenue_column_box = SurroundingRectangle(
            revenue_cells,
            color=PRIMARY_PURPLE,
            stroke_width=4,
            buff=0.02,
            corner_radius=0.13,
        )
        self.revenue_column_box.set_z_index(4)
        return self.group

    def _cell(
        self,
        row: int,
        col: int,
        value: str,
        fill_color: str,
        text_color: str,
        fill_opacity: float,
        bold: bool = False,
    ) -> Cell:
        box = RoundedRectangle(
            width=self.col_widths[col] - 0.04,
            height=self.row_height - 0.05,
            corner_radius=0.08,
            stroke_color=GRAY_200,
            stroke_width=1.5,
            fill_color=fill_color,
            fill_opacity=fill_opacity,
        )
        box.move_to(self.center_for(row, col))
        box.set_z_index(1)
        label = text(value, size=22 if row == 0 else 24, color=text_color, weight="BOLD" if bold else None)
        label.move_to(box.get_center())
        label.set_z_index(3)
        return Cell(center=box.get_center(), box=box, text=label)


class PolarsDerivedColumnScene(Scene):
    def construct(self) -> None:
        if os.environ.get("SPIKE_RENDER_TARGET") == "poster":
            self.camera.background_color = PAGE_BACKGROUND

        df = build_dataset()
        table = DataTable()
        table_group = table.build(df)

        title_panel = RoundedRectangle(
            width=10.85,
            height=0.88,
            corner_radius=0.18,
            stroke_color=GRAY_200,
            stroke_width=1.5,
            fill_color=WHITE,
            fill_opacity=1,
        )
        title_panel.to_edge(UP, buff=0.26)
        title_panel.set_z_index(0)
        title = text("Column derived from two source columns", size=33, color=GRAY, weight="BOLD")
        title.to_edge(UP, buff=0.42)
        title.set_z_index(2)
        subtitle = text("Polars evaluates the expression for every row", size=21, color=GRAY_700)
        subtitle.next_to(title, DOWN, buff=0.11)
        subtitle.set_z_index(2)

        code_panel, code_parts = self._build_code_panel()
        route_guides = self._build_route_guides(table)

        self.play(
            FadeIn(title_panel, shift=DOWN * 0.06),
            FadeIn(title, shift=DOWN * 0.12),
            FadeIn(subtitle, shift=DOWN * 0.12),
            run_time=0.45,
        )
        self.play(FadeIn(table_group, shift=UP * 0.1), run_time=0.55)
        self.play(FadeIn(code_panel, shift=UP * 0.12), run_time=0.35)
        self.play(FadeIn(route_guides), run_time=0.22)
        self.play(
            AnimationGroup(
                Indicate(table.cells[(0, 1)].box, color=PRIMARY_GREEN, scale_factor=1.04),
                Indicate(code_parts["qty"], color=PRIMARY_GREEN, scale_factor=1.04),
                Indicate(table.cells[(0, 2)].box, color=PRIMARY_BLUE, scale_factor=1.04),
                Indicate(code_parts["unit_price"], color=PRIMARY_BLUE, scale_factor=1.04),
                lag_ratio=0.12,
            ),
            run_time=0.95,
        )
        self.wait(2.0)

        for row_index, row in enumerate(df.iter_rows(named=True), start=1):
            self._animate_row(row_index, row, table)

        self.play(
            FadeOut(route_guides),
            FadeIn(table.revenue_column_box),
            Indicate(code_parts["revenue"], color=PRIMARY_PURPLE, scale_factor=1.06),
            run_time=0.55,
        )
        self.wait(2.99)

    def _build_code_panel(self) -> tuple[VGroup, dict[str, Text]]:
        panel = RoundedRectangle(
            width=11.95,
            height=1.42,
            corner_radius=0.16,
            stroke_color=GRAY_400,
            stroke_width=2,
            fill_color=WHITE,
            fill_opacity=1,
        )
        panel.move_to(DOWN * 2.82)

        line_one = code_text("df.with_columns(", size=21, color=GRAY_700)
        line_one.move_to(panel.get_left() + RIGHT * 1.42 + UP * 0.29)

        qty = code_text('pl.col("qty")', color=PRIMARY_GREEN)
        op = code_text(" * ", color=PRIMARY_ORANGE)
        unit_price = code_text('pl.col("unit_price")', color=PRIMARY_BLUE)
        alias_open = code_text(').alias("', color=GRAY_700)
        revenue = code_text("revenue", color=PRIMARY_PURPLE)
        alias_close = code_text('")', color=GRAY_700)
        line_two = VGroup(qty, op, unit_price, alias_open, revenue, alias_close)
        line_two.arrange(RIGHT, buff=0.03)
        line_two.move_to(panel.get_left() + RIGHT * 4.42 + DOWN * 0.28)

        close_paren = code_text(")", size=21, color=GRAY_700)
        close_paren.move_to(panel.get_right() + LEFT * 0.54 + DOWN * 0.28)

        panel_group = VGroup(panel, line_one, line_two, close_paren)
        return panel_group, {"qty": qty, "unit_price": unit_price, "revenue": revenue}

    def _build_route_guides(self, table: DataTable) -> VGroup:
        guides = VGroup()
        for row_index in range(1, 5):
            qty_center = table.cells[(row_index, 1)].box.get_center()
            price_center = table.cells[(row_index, 2)].box.get_center()
            revenue_cell = table.cells[(row_index, 3)].box
            revenue_center = revenue_cell.get_center()
            join = revenue_cell.get_right() + RIGHT * 1.05
            guides.add(
                DashedLine(
                    qty_center + RIGHT * 0.34,
                    join + LEFT * 0.74,
                    color=GRAY_300,
                    stroke_width=1.5,
                    dash_length=0.08,
                    dashed_ratio=0.55,
                ),
                DashedLine(
                    price_center + RIGHT * 0.52,
                    join + LEFT * 0.74,
                    color=GRAY_300,
                    stroke_width=1.5,
                    dash_length=0.08,
                    dashed_ratio=0.55,
                ),
                Line(
                    join + LEFT * 0.72,
                    revenue_center + RIGHT * 0.52,
                    color=PRIMARY_ORANGE,
                    stroke_width=2.2,
                    stroke_opacity=0.2,
                ),
            )
        return guides

    def _animate_row(self, row_index: int, row: dict[str, object], table: DataTable) -> None:
        qty_cell = table.cells[(row_index, 1)].box
        price_cell = table.cells[(row_index, 2)].box
        revenue_cell = table.cells[(row_index, 3)].box
        revenue_text = table.revenue_texts[row_index - 1]

        row_marker = RoundedRectangle(
            width=0.11,
            height=0.48,
            corner_radius=0.05,
            stroke_width=0,
            fill_color=PRIMARY_YELLOW,
            fill_opacity=1,
        )
        row_marker.move_to(table.cells[(row_index, 0)].box.get_left() + LEFT * 0.13)
        row_marker.set_z_index(5)

        row_line = Line(
            qty_cell.get_left() + DOWN * 0.24,
            revenue_cell.get_right() + DOWN * 0.24,
            color=PRIMARY_YELLOW,
            stroke_width=3,
            stroke_opacity=0.82,
        )
        row_line.set_z_index(4)
        row_focus = VGroup(row_marker, row_line)

        join = revenue_cell.get_right() + RIGHT * 1.05
        result_token = text(money(row["revenue"]), size=31, color=PRIMARY_YELLOW, weight="BOLD")
        result_token.move_to(revenue_cell.get_center())
        result_token.set_z_index(7)
        _formula, formula_parts = self._calculation_badge(
            row,
            join + UP * 0.08,
        )
        badge_box = formula_parts["box"]
        formula_terms = VGroup(
            formula_parts["qty"],
            formula_parts["op"],
            formula_parts["price"],
            formula_parts["eq"],
        )

        self.play(
            FadeIn(row_focus),
            FadeIn(badge_box),
            Indicate(qty_cell, color=PRIMARY_GREEN, scale_factor=1.02),
            Indicate(price_cell, color=PRIMARY_BLUE, scale_factor=1.02),
            run_time=0.65,
        )
        self.add(formula_terms)
        self.wait(0.7)
        self.add(formula_parts["result"])
        self.wait(0.6)
        self.wait(0.65)
        self.play(
            ReplacementTransform(formula_parts["result"], result_token),
            run_time=0.85,
            rate_func=rate_functions.ease_out_cubic,
        )
        self.play(
            ReplacementTransform(result_token, revenue_text),
            run_time=0.35,
            rate_func=rate_functions.ease_out_cubic,
        )
        self.wait(0.9)
        self.play(
            FadeOut(row_focus),
            FadeOut(formula_terms, shift=UP * 0.04),
            FadeOut(badge_box, shift=UP * 0.04),
            run_time=0.75,
        )

    def _calculation_badge(self, row: dict[str, object], position: object) -> tuple[VGroup, dict[str, object]]:
        qty = code_text(str(row["qty"]), size=19, color=PRIMARY_GREEN)
        op = code_text("*", size=19, color=PRIMARY_ORANGE)
        price = code_text(str(row["unit_price"]), size=19, color=PRIMARY_BLUE)
        eq = code_text("=", size=19, color=GRAY)
        result = code_text(str(row["revenue"]), size=19, color=PRIMARY_YELLOW)
        terms = VGroup(qty, op, price, eq, result)
        terms.arrange(RIGHT, buff=0.2)
        terms.set_z_index(7)
        badge = RoundedRectangle(
            width=terms.width + 0.52,
            height=0.4,
            corner_radius=0.08,
            stroke_color=PRIMARY_ORANGE,
            stroke_width=1.8,
            fill_color=WHITE,
            fill_opacity=0.96,
        )
        badge.set_z_index(6)
        terms.move_to(badge.get_center())
        group = VGroup(badge, terms)
        group.move_to(position)
        return group, {
            "box": badge,
            "qty": qty,
            "op": op,
            "price": price,
            "eq": eq,
            "result": result,
        }


def render_variant(args: _Args) -> None:
    video_path, poster_path = output_paths()

    video_result = subprocess.run(
        render_command(args, video_path.stem, poster=False),
        check=False,
        env={**os.environ, "SPIKE_RENDER_TARGET": "video"},
    )
    if video_result.returncode != 0:
        raise SystemExit(video_result.returncode)
    promote_rendered_file(video_path.name, video_path)

    poster_result = subprocess.run(
        render_command(args, poster_path.stem, poster=True),
        check=False,
        env={**os.environ, "SPIKE_RENDER_TARGET": "poster"},
    )
    if poster_result.returncode != 0:
        raise SystemExit(poster_result.returncode)
    promote_rendered_file(poster_path.name, poster_path)


def main() -> int:
    args = parse_args()
    render_variant(args)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
