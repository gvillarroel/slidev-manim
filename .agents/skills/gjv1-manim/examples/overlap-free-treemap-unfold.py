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
    UP,
    Create,
    FadeIn,
    FadeOut,
    Indicate,
    Line,
    Rectangle,
    Scene,
    Text,
    VGroup,
    rate_functions,
)
from manimpango import list_fonts

EXAMPLE_FILE = Path(__file__).resolve()
OUTPUT_DIR = Path.cwd() / "videos" / "gjv1-overlap-free-treemap"
STAGING_DIR = OUTPUT_DIR / ".manim"
VIDEO_PATH = OUTPUT_DIR / "gjv1-overlap-free-treemap.webm"
POSTER_PATH = OUTPUT_DIR / "gjv1-overlap-free-treemap.png"

PRIMARY_RED = "#9e1b32"
PRIMARY_ORANGE = "#d45d00"
PRIMARY_YELLOW = "#f1b434"
PRIMARY_GREEN = "#4b8b3b"
PRIMARY_BLUE = "#007298"
PRIMARY_PURPLE = "#6f2c91"
WHITE = "#ffffff"
GRAY = "#333e48"
PAGE_BACKGROUND = "#f7f7f7"
TEXT_FONT = "Open Sans" if "Open Sans" in list_fonts() else "Arial"


def quality_flag(quality: str) -> str:
    return {
        "low": "-ql",
        "medium": "-qm",
        "high": "-qh",
        "production": "-qp",
        "4k": "-qk",
    }[quality]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Render an overlap-free treemap unfold example.")
    parser.add_argument("--quality", choices=("low", "medium", "high", "production", "4k"), default="medium")
    return parser.parse_args()


def render_command(args: argparse.Namespace, poster: bool) -> list[str]:
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
        "-o",
        target.stem,
        "--media_dir",
        str(STAGING_DIR),
    ]
    command.append("-s" if poster else "--format=webm")
    if not poster:
        command.append("-t")
    command.extend([str(EXAMPLE_FILE), "OverlapFreeTreemapScene"])
    return command


def promote(target_name: str, destination: Path) -> None:
    matches = list(STAGING_DIR.glob(f"**/{target_name}"))
    if not matches:
        raise FileNotFoundError(target_name)
    destination.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(max(matches, key=lambda path: path.stat().st_mtime), destination)


def label_group(label: str, value: str, *, color: str, max_width: float, max_height: float) -> VGroup:
    label_text = Text(label, font=TEXT_FONT, font_size=24, color=color)
    value_text = Text(value, font=TEXT_FONT, font_size=23, color=color)
    group = VGroup(label_text, value_text).arrange(DOWN, buff=0.02)
    if group.width > max_width:
        group.scale_to_fit_width(max_width)
    if group.height > max_height:
        group.scale_to_fit_height(max_height)
    return group


def filled_cell(
    width: float,
    height: float,
    *,
    fill: str,
    label: str,
    value: str,
    text_color: str = WHITE,
) -> VGroup:
    body = Rectangle(
        width=width,
        height=height,
        stroke_color=fill,
        stroke_width=2.4,
        fill_color=fill,
        fill_opacity=0.96,
    )
    text = label_group(label, value, color=text_color, max_width=width * 0.78, max_height=height * 0.52)
    text.move_to(body.get_center())
    body.set_z_index(3)
    text.set_z_index(8)
    return VGroup(body, text)


def slot_for(cell: VGroup, color: str) -> Rectangle:
    body = cell[0]
    slot = Rectangle(
        width=body.width,
        height=body.height,
        stroke_color=color,
        stroke_width=1.7,
        fill_color=color,
        fill_opacity=0.045,
    )
    slot.move_to(body.get_center())
    slot.set_z_index(1)
    return slot


def section_header(center_x: float, top_y: float, width: float, name: str, value: str, color: str) -> VGroup:
    rule = Line(
        start=(center_x - width / 2, top_y, 0),
        end=(center_x + width / 2, top_y, 0),
        stroke_color=color,
        stroke_width=3.0,
    )
    label = Text(name, font=TEXT_FONT, font_size=18, color=color)
    total = Text(value, font=TEXT_FONT, font_size=18, color=color)
    header_y = top_y + 0.23
    label.move_to((center_x - width / 2 + 0.08 + label.width / 2, header_y, 0))
    total.move_to((center_x + width / 2 - 0.08 - total.width / 2, header_y, 0))
    group = VGroup(rule, label, total)
    group.set_z_index(7)
    return group


def active_outline(target: VGroup | Rectangle) -> Rectangle:
    body = target[0] if isinstance(target, VGroup) else target
    outline = Rectangle(
        width=body.width + 0.08,
        height=body.height + 0.08,
        stroke_color=PRIMARY_RED,
        stroke_width=4.0,
        fill_opacity=0,
    )
    outline.move_to(body.get_center())
    outline.set_z_index(9)
    return outline


class OverlapFreeTreemapScene(Scene):
    def construct(self) -> None:
        self.camera.background_color = PAGE_BACKGROUND

        title = Text("Overlap-free Treemap", font=TEXT_FONT, font_size=28, color=GRAY)
        subtitle = Text("native cells, real gutters, parent rules", font=TEXT_FONT, font_size=15, color=PRIMARY_BLUE)
        title_group = VGroup(title, subtitle).arrange(DOWN, buff=0.10).to_edge(UP, buff=0.38)

        left_x = -2.15
        right_x = 3.28
        left_header = section_header(left_x, 1.36, 6.20, "Source group", "17", PRIMARY_BLUE)
        right_header = section_header(right_x, 1.36, 3.70, "Derived group", "10", PRIMARY_GREEN)

        cell_y = -0.61
        cell_height = 3.38
        gutter = 0.34
        x0 = left_x - 3.10

        fragments = filled_cell(2.95, cell_height, fill=PRIMARY_ORANGE, label="Fragments", value="8")
        source = filled_cell(1.55, cell_height, fill=PRIMARY_PURPLE, label="Source", value="5")
        labels = filled_cell(1.18, cell_height, fill=PRIMARY_YELLOW, label="Labels", value="4", text_color=GRAY)
        fragments.move_to((x0 + fragments[0].width / 2, cell_y, 0))
        source.move_to((fragments.get_right()[0] + gutter + source[0].width / 2, cell_y, 0))
        labels.move_to((source.get_right()[0] + gutter + labels[0].width / 2, cell_y, 0))

        timing = filled_cell(3.45, 1.62, fill=PRIMARY_RED, label="Timing", value="6")
        review = filled_cell(3.45, 1.36, fill=PRIMARY_BLUE, label="Review", value="4")
        timing.move_to((right_x, 0.18, 0))
        review.move_to((right_x, -1.70, 0))

        cells = (fragments, source, labels, timing, review)
        left_slots = VGroup(*[slot_for(cell, PRIMARY_BLUE) for cell in (fragments, source, labels)])
        right_slots = VGroup(*[slot_for(cell, PRIMARY_GREEN) for cell in (timing, review)])
        all_cells = VGroup(*cells)

        if os.environ.get("SPIKE_RENDER_TARGET") == "poster":
            self.add(title_group, left_header, right_header, all_cells)
            return

        self.add(title_group, left_header, right_header, left_slots, right_slots)
        self.wait(2.6)

        self.play(Indicate(left_header, color=PRIMARY_RED, scale_factor=1.02), run_time=1.0)
        self.wait(0.35)

        for cell, slot in ((fragments, left_slots[0]), (source, left_slots[1]), (labels, left_slots[2])):
            outline = active_outline(slot)
            self.play(Create(outline), run_time=0.38, rate_func=rate_functions.ease_out_cubic)
            self.play(FadeIn(cell, scale=0.985), FadeOut(outline), run_time=0.82, rate_func=rate_functions.ease_out_cubic)
            self.remove(slot)
            self.wait(0.25)

        self.play(Indicate(right_header, color=PRIMARY_RED, scale_factor=1.02), run_time=1.0)
        self.wait(0.35)

        for cell, slot in ((timing, right_slots[0]), (review, right_slots[1])):
            outline = active_outline(slot)
            self.play(Create(outline), run_time=0.38, rate_func=rate_functions.ease_out_cubic)
            self.play(FadeIn(cell, scale=0.985), FadeOut(outline), run_time=0.82, rate_func=rate_functions.ease_out_cubic)
            self.remove(slot)
            self.wait(0.25)

        self.wait(13.25)


def main() -> int:
    args = parse_args()
    for poster in (False, True):
        env = {**os.environ, "SPIKE_RENDER_TARGET": "poster" if poster else "video"}
        result = subprocess.run(render_command(args, poster), check=False, env=env)
        if result.returncode != 0:
            return result.returncode
        promote((POSTER_PATH if poster else VIDEO_PATH).name, POSTER_PATH if poster else VIDEO_PATH)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
