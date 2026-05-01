#!/usr/bin/env -S uv run --script
# /// script
# dependencies = [
#   "manim>=0.20.1",
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
    Arrow,
    BarChart,
    ChangeDecimalToValue,
    Create,
    CubicBezier,
    DecimalNumber,
    Dot,
    FadeIn,
    FadeOut,
    Line,
    MobjectTable,
    MoveAlongPath,
    Rectangle,
    Scene,
    SurroundingRectangle,
    Text,
    VGroup,
    VMobject,
    ValueTracker,
    always_redraw,
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
PRIMARY_BLUE = "#007298"
BLACK = "#000000"
WHITE = "#ffffff"
GRAY = "#333e48"
GRAY_100 = "#e7e7e7"
GRAY_200 = "#cfcfcf"
GRAY_300 = "#b5b5b5"
GRAY_400 = "#9c9c9c"
GRAY_500 = "#828282"
GRAY_600 = "#696969"
GRAY_700 = "#4f4f4f"
GRAY_800 = "#363636"
PAGE_BACKGROUND = "#f7f7f7"
HIGHLIGHT_RED = "#ffccd5"
HIGHLIGHT_BLUE = "#cdf3ff"

FONT = "Arial"
TARGET_VALUE = 432


class _Args(argparse.Namespace):
    quality: str
    preview: bool


def parse_args() -> _Args:
    parser = argparse.ArgumentParser(description="Render the Manim data/counter narration spike.")
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
    command.extend([str(Path(__file__).resolve()), "DataCounterNarrationScene"])
    return command


def promote(target_name: str, destination: Path) -> None:
    matches = sorted(STAGING_DIR.glob(f"**/{target_name}"))
    if not matches:
        raise FileNotFoundError(f"Could not find {target_name} under {STAGING_DIR}")
    destination.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(max(matches, key=lambda path: path.stat().st_mtime), destination)


def label(value: str, size: int = 24, color: str = GRAY, weight: str | None = None) -> Text:
    kwargs = {"font": FONT, "font_size": size, "color": color}
    if weight:
        kwargs["weight"] = weight
    return Text(value, **kwargs)


def number_text(value: int | str, size: int = 25, color: str = GRAY, weight: str | None = None) -> Text:
    return label(str(value), size=size, color=color, weight=weight)


def paint_text(mob: VMobject, color: str) -> VMobject:
    mob.set_color(color, family=True)
    if hasattr(mob, "set_fill"):
        mob.set_fill(color=color, opacity=1, family=True)
    if hasattr(mob, "set_stroke"):
        mob.set_stroke(color=color, width=0, opacity=0, family=True)
    return mob


def fixed_decimal(value: int, size: int = 58, color: str = PRIMARY_RED) -> DecimalNumber:
    number = DecimalNumber(
        value,
        num_decimal_places=0,
        group_with_commas=False,
        mob_class=Text,
        font_size=size,
        color=color,
    )
    number.set_color(color)
    return number


def mobject_table_cell(value: VMobject) -> VMobject:
    return value


def fit(mob: VMobject, max_width: float, max_height: float) -> VMobject:
    if mob.width > max_width:
        mob.scale_to_fit_width(max_width)
    if mob.height > max_height:
        mob.scale_to_fit_height(max_height)
    return mob


def make_source_table() -> tuple[MobjectTable, dict[str, VMobject]]:
    row_labels = [
        label("trial", 20, GRAY_700),
        label("baseline", 20, GRAY_700),
        label("launch", 21, BLACK, "BOLD"),
    ]
    col_labels = [
        label("units", 19, GRAY_700, "BOLD"),
        label("price", 19, GRAY_700, "BOLD"),
        label("revenue", 19, GRAY_700, "BOLD"),
    ]
    corner = label("row", 18, GRAY_700, "BOLD")
    cells = {
        "trial_units": number_text(14, 23, GRAY_700),
        "trial_price": number_text(22, 23, GRAY_700),
        "trial_revenue": number_text(308, 23, GRAY_700),
        "base_units": number_text(20, 23, GRAY_700),
        "base_price": number_text(17, 23, GRAY_700),
        "base_revenue": number_text(340, 23, GRAY_700),
        "launch_units": number_text(24, 26, BLACK, "BOLD"),
        "launch_price": number_text(18, 26, BLACK, "BOLD"),
        "launch_revenue": label("pending", 20, GRAY_500),
    }
    table = MobjectTable(
        [
            [cells["trial_units"], cells["trial_price"], cells["trial_revenue"]],
            [cells["base_units"], cells["base_price"], cells["base_revenue"]],
            [cells["launch_units"], cells["launch_price"], cells["launch_revenue"]],
        ],
        row_labels=row_labels,
        col_labels=col_labels,
        top_left_entry=corner,
        element_to_mobject=mobject_table_cell,
        include_outer_lines=True,
        h_buff=0.72,
        v_buff=0.42,
        arrange_in_grid_config={"cell_alignment": RIGHT},
        line_config={"color": GRAY_300, "stroke_width": 1.6},
    )
    for entry in table.get_entries():
        paint_text(entry, GRAY_700)
    for entry in (*row_labels, *col_labels, corner):
        paint_text(entry, GRAY_700)
    paint_text(row_labels[-1], BLACK)
    for key in ("launch_units", "launch_price"):
        paint_text(cells[key], BLACK)
    paint_text(cells["launch_revenue"], GRAY_600)
    for key in ("trial_revenue", "base_revenue"):
        paint_text(cells[key], GRAY_700)
    table.scale(0.88, scale_stroke=True)
    table.move_to(LEFT * 3.05 + DOWN * 0.55)
    return table, cells


def make_formula_panel(table: MobjectTable) -> tuple[VGroup, dict[str, VMobject]]:
    panel = Rectangle(
        width=3.82,
        height=2.18,
        stroke_color=GRAY_300,
        stroke_width=1.5,
        fill_color=WHITE,
        fill_opacity=0.96,
    )
    panel.move_to(RIGHT * 3.35 + UP * 0.7)

    title = label("side aggregation", 18, GRAY_700, "BOLD")
    title.move_to(panel.get_top() + DOWN * 0.27)

    source_caption = label("source terms", 14, GRAY_600)
    source_caption.move_to(panel.get_left() + RIGHT * 1.0 + UP * 0.38)

    result_caption = label("derived value", 14, GRAY_600)
    result_caption.move_to(panel.get_left() + RIGHT * 1.02 + DOWN * 0.56)

    slot_w = 0.74
    slot_h = 0.42
    units_slot = Rectangle(width=slot_w, height=slot_h, stroke_color=GRAY_300, stroke_width=1.2, fill_color=PAGE_BACKGROUND, fill_opacity=0.8)
    price_slot = units_slot.copy()
    result_slot = Rectangle(width=1.08, height=slot_h, stroke_color=PRIMARY_RED, stroke_width=1.8, fill_color=HIGHLIGHT_RED, fill_opacity=0.42)
    times = label("x", 25, GRAY_700)
    equals = label("=", 25, GRAY_700)

    formula_row = VGroup(units_slot, times, price_slot, equals, result_slot).arrange(RIGHT, buff=0.18)
    formula_row.move_to(panel.get_center() + DOWN * 0.08)

    units_term = number_text(24, 28, BLACK, "BOLD").move_to(units_slot)
    price_term = number_text(18, 28, BLACK, "BOLD").move_to(price_slot)
    result_term = number_text(TARGET_VALUE, 28, PRIMARY_RED, "BOLD").move_to(result_slot)
    for mob in (units_term, price_term, result_term):
        mob.set_opacity(0)

    arrow = Arrow(
        start=table.get_right() + RIGHT * 0.22,
        end=panel.get_left() + RIGHT * 0.22,
        buff=0.0,
        stroke_width=2.2,
        color=GRAY_400,
        max_tip_length_to_length_ratio=0.08,
    )
    arrow.set_opacity(0.52)

    group = VGroup(
        panel,
        title,
        source_caption,
        result_caption,
        arrow,
        units_slot,
        price_slot,
        result_slot,
        times,
        equals,
        units_term,
        price_term,
        result_term,
    )
    parts = {
        "panel": panel,
        "units_slot": units_slot,
        "price_slot": price_slot,
        "result_slot": result_slot,
        "units_term": units_term,
        "price_term": price_term,
        "result_term": result_term,
        "arrow": arrow,
    }
    return group, parts


def make_counter_panel() -> tuple[VGroup, dict[str, VMobject | ValueTracker | BarChart]]:
    panel = Rectangle(
        width=3.82,
        height=2.58,
        stroke_color=GRAY_300,
        stroke_width=1.5,
        fill_color=WHITE,
        fill_opacity=0.96,
    )
    panel.move_to(RIGHT * 3.35 + DOWN * 1.94)

    title = label("counter landing", 18, GRAY_700, "BOLD")
    title.move_to(panel.get_top() + DOWN * 0.28)

    readout_box = Rectangle(
        width=2.35,
        height=0.68,
        stroke_color=GRAY_300,
        stroke_width=1.2,
        fill_color=PAGE_BACKGROUND,
        fill_opacity=0.95,
    )
    readout_box.move_to(panel.get_center() + UP * 0.52)
    counter = fixed_decimal(0)
    counter.move_to(readout_box)
    counter.add_updater(lambda mob: mob.move_to(readout_box.get_center()))

    track = Rectangle(
        width=2.72,
        height=0.13,
        stroke_color=GRAY_300,
        stroke_width=1.0,
        fill_color=GRAY_100,
        fill_opacity=1,
    )
    track.move_to(readout_box.get_bottom() + DOWN * 0.26)

    progress = ValueTracker(0)
    fill = always_redraw(
        lambda: Rectangle(
            width=max(0.015, track.width * progress.get_value()),
            height=track.height,
            stroke_width=0,
            fill_color=PRIMARY_RED,
            fill_opacity=1,
        ).move_to(track.get_left() + RIGHT * max(0.015, track.width * progress.get_value()) / 2)
    )

    chart = BarChart(
        values=[210, 325, 0],
        y_range=[0, 500, 100],
        x_length=2.7,
        y_length=0.72,
        bar_width=0.55,
        bar_colors=[GRAY_300, GRAY_500, PRIMARY_RED],
        bar_fill_opacity=0.78,
        bar_stroke_width=1.2,
        axis_config={
            "stroke_color": GRAY_400,
            "stroke_width": 1.2,
            "include_ticks": False,
            "label_constructor": Text,
            "font_size": 12,
        },
        y_axis_config={"include_numbers": False},
        x_axis_config={"include_numbers": False},
        tips=False,
    )
    chart.move_to(panel.get_bottom() + UP * 0.55)

    group = VGroup(panel, title, readout_box, track, fill, counter, chart)
    parts: dict[str, VMobject | ValueTracker | BarChart] = {
        "panel": panel,
        "readout_box": readout_box,
        "track": track,
        "fill": fill,
        "counter": counter,
        "progress": progress,
        "chart": chart,
    }
    return group, parts


def source_token(start: VMobject, target: VMobject) -> tuple[Dot, CubicBezier]:
    start_point = start.get_top() + UP * 0.08
    end_point = target.get_left() + LEFT * 0.06
    path = CubicBezier(
        start_point,
        start_point + RIGHT * 0.75 + UP * 0.34,
        end_point + LEFT * 0.75 + UP * 0.24,
        end_point,
    )
    path.set_stroke(color=PRIMARY_RED, width=1.5, opacity=0.16)
    path.set_z_index(4)
    token = Dot(point=start_point, radius=0.055, color=PRIMARY_RED)
    token.set_z_index(12)
    return token, path


class DataCounterNarrationScene(Scene):
    def construct(self) -> None:
        self.camera.background_color = PAGE_BACKGROUND

        stage = Rectangle(
            width=13.2,
            height=7.38,
            stroke_width=0,
            fill_color=PAGE_BACKGROUND,
            fill_opacity=0.98,
        )
        stage.set_z_index(-20)
        self.add(stage)

        heading = label("data handoff to a live counter", 29, GRAY, "BOLD")
        heading.to_edge(UP, buff=0.85)

        table, cells = make_source_table()
        formula_panel, formula = make_formula_panel(table)
        counter_panel, counter = make_counter_panel()
        self.add(counter["progress"])

        active_row = VGroup(
            cells["launch_units"],
            cells["launch_price"],
            cells["launch_revenue"],
        )
        row_marker = Rectangle(
            width=0.08,
            height=active_row.height + 0.34,
            stroke_width=0,
            fill_color=PRIMARY_RED,
            fill_opacity=1,
        )
        row_marker.move_to([table.get_left()[0] - 0.13, active_row.get_y(), 0])
        row_rule = Line(
            start=[table.get_left()[0] + 0.07, active_row.get_bottom()[1] - 0.15, 0],
            end=[table.get_right()[0] - 0.08, active_row.get_bottom()[1] - 0.15, 0],
            color=PRIMARY_RED,
            stroke_width=3,
        )
        row_marker.set_opacity(0)
        row_rule.set_opacity(0)

        units_ring = SurroundingRectangle(cells["launch_units"], color=PRIMARY_RED, buff=0.12, stroke_width=3)
        price_ring = SurroundingRectangle(cells["launch_price"], color=PRIMARY_RED, buff=0.12, stroke_width=3)
        result_ring = SurroundingRectangle(cells["launch_revenue"], color=PRIMARY_RED, buff=0.13, stroke_width=3)
        for ring in (units_ring, price_ring, result_ring):
            ring.set_fill(opacity=0)
            ring.set_stroke(opacity=0)
            ring.set_z_index(6)

        final_value = paint_text(number_text(TARGET_VALUE, 26, PRIMARY_RED, "BOLD"), PRIMARY_RED)
        final_value.move_to(cells["launch_revenue"])
        final_value.set_z_index(8)

        self.add(heading, table, formula_panel, counter_panel, row_marker, row_rule, units_ring, price_ring, result_ring)
        self.wait(2.65)

        self.play(
            row_marker.animate.set_opacity(1),
            row_rule.animate.set_opacity(1),
            run_time=0.9,
            rate_func=rate_functions.ease_out_cubic,
        )
        self.wait(1.0)

        self.play(units_ring.animate.set_stroke(opacity=1), run_time=0.42)
        self.wait(0.25)
        unit_token, unit_path = source_token(cells["launch_units"], formula["units_slot"])
        self.add(unit_path, unit_token)
        self.play(
            MoveAlongPath(unit_token, unit_path),
            formula["units_term"].animate.set_opacity(1),
            run_time=1.15,
            rate_func=rate_functions.ease_in_out_cubic,
        )
        self.play(FadeOut(unit_token), unit_path.animate.set_opacity(0.0), units_ring.animate.set_stroke(opacity=0.42), run_time=0.35)

        self.play(price_ring.animate.set_stroke(opacity=1), run_time=0.42)
        self.wait(0.25)
        price_token, price_path = source_token(cells["launch_price"], formula["price_slot"])
        self.add(price_path, price_token)
        self.play(
            MoveAlongPath(price_token, price_path),
            formula["price_term"].animate.set_opacity(1),
            run_time=1.15,
            rate_func=rate_functions.ease_in_out_cubic,
        )
        self.play(FadeOut(price_token), price_path.animate.set_opacity(0.0), price_ring.animate.set_stroke(opacity=0.42), run_time=0.35)
        self.wait(1.05)

        self.play(
            formula["result_term"].animate.set_opacity(1),
            formula["result_slot"].animate.set_stroke(color=PRIMARY_RED, width=3),
            units_ring.animate.set_stroke(opacity=0.16),
            price_ring.animate.set_stroke(opacity=0.16),
            run_time=0.9,
            rate_func=rate_functions.ease_out_cubic,
        )
        self.wait(0.85)

        count_start = formula["result_slot"].get_bottom() + DOWN * 0.04
        count_end = counter["readout_box"].get_top() + UP * 0.05
        count_token = Dot(point=count_start, radius=0.065, color=PRIMARY_RED)
        count_token.set_z_index(12)
        count_path = CubicBezier(
            count_start,
            count_start + DOWN * 0.54 + RIGHT * 0.08,
            count_end + UP * 0.32 + RIGHT * 0.12,
            count_end,
        )
        count_path.set_stroke(color=PRIMARY_RED, width=1.7, opacity=0.18)
        count_path.set_z_index(4)
        self.add(count_path, count_token)
        self.play(
            MoveAlongPath(count_token, count_path),
            ChangeDecimalToValue(counter["counter"], TARGET_VALUE),
            counter["progress"].animate.set_value(1),
            counter["chart"].animate.change_bar_values([210, 325, TARGET_VALUE]),
            run_time=3.35,
            rate_func=rate_functions.ease_in_out_cubic,
        )
        self.play(FadeOut(count_token), count_path.animate.set_opacity(0.0), run_time=0.35)
        self.wait(0.9)

        self.play(
            formula["units_term"].animate.set_opacity(0.0),
            formula["price_term"].animate.set_opacity(0.0),
            formula["result_term"].animate.set_opacity(0.38),
            formula["result_slot"].animate.set_stroke(width=1.7),
            run_time=0.45,
        )
        return_start = counter["readout_box"].get_left() + LEFT * 0.05
        return_end = cells["launch_revenue"].get_right() + RIGHT * 0.12
        return_token = Dot(point=return_start, radius=0.065, color=PRIMARY_RED)
        return_token.set_z_index(12)
        table_path = CubicBezier(
            return_start,
            return_start + LEFT * 0.9 + UP * 0.35,
            return_end + RIGHT * 0.95 + UP * 0.38,
            return_end,
        )
        table_path.set_stroke(color=PRIMARY_RED, width=1.8, opacity=0.18)
        table_path.set_z_index(4)
        self.add(table_path, return_token)
        self.play(
            result_ring.animate.set_stroke(opacity=1),
            cells["launch_revenue"].animate.set_opacity(0),
            run_time=0.45,
        )
        self.play(
            MoveAlongPath(return_token, table_path),
            run_time=1.45,
            rate_func=rate_functions.ease_in_out_cubic,
        )
        final_value.move_to(cells["launch_revenue"])
        self.play(
            FadeOut(return_token),
            FadeIn(final_value),
            table_path.animate.set_opacity(0.0),
            formula["result_term"].animate.set_opacity(0.0),
            run_time=0.22,
        )
        table.add(final_value)
        self.wait(1.78)

        terminal = VGroup(table, result_ring)
        self.play(
            FadeOut(units_ring),
            FadeOut(price_ring),
            FadeOut(row_marker),
            FadeOut(row_rule),
            run_time=0.04,
            rate_func=rate_functions.ease_out_cubic,
        )
        self.play(
            FadeOut(formula_panel, shift=RIGHT * 0.22),
            FadeOut(counter_panel, shift=RIGHT * 0.22),
            terminal.animate.move_to(DOWN * 0.55).scale(1.06, scale_stroke=True),
            heading.animate.move_to(UP * 2.55),
            run_time=0.16,
            rate_func=rate_functions.ease_out_cubic,
        )
        self.play(result_ring.animate.set_stroke(width=3.4, opacity=0.88), run_time=0.42)
        self.wait(6.35)


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
