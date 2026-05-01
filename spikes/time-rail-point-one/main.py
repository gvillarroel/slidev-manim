#!/usr/bin/env -S uv run --script
# /// script
# dependencies = [
#   "manim>=0.19.0",
# ]
# ///

from __future__ import annotations

import argparse
import os
import shutil
import subprocess
import sys
from pathlib import Path

SPIKE_DIR = Path(__file__).resolve().parent
REPO_ROOT = SPIKE_DIR.parent.parent
SPIKE_NAME = SPIKE_DIR.name
OUTPUT_DIR = REPO_ROOT / "videos" / SPIKE_NAME
STAGING_DIR = OUTPUT_DIR / ".manim"

PRIMARY_RED = "#9e1b32"
WHITE = "#ffffff"
GRAY = "#333e48"
GRAY_200 = "#cfcfcf"
GRAY_300 = "#b5b5b5"
GRAY_600 = "#696969"
GRAY_700 = "#4f4f4f"
PAGE_BACKGROUND = "#f7f7f7"
FONT_FAMILY = "Arial"


class _Args(argparse.Namespace):
    quality: str
    preview: bool


def parse_args() -> _Args:
    parser = argparse.ArgumentParser(description="Render the time-rail-point-one Manim spike.")
    parser.add_argument(
        "--quality",
        choices=("low", "medium", "high", "production", "4k"),
        default="medium",
        help="Manim quality preset. Defaults to medium for quick iteration.",
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


def render_command(args: _Args, *, poster: bool) -> list[str]:
    STAGING_DIR.mkdir(parents=True, exist_ok=True)
    output = OUTPUT_DIR / ("time-rail-point-one.png" if poster else "time-rail-point-one.webm")
    command = [
        sys.executable,
        "-m",
        "manim",
        "render",
        quality_flag(args.quality),
        "-r",
        "1600,900",
        "-o",
        output.stem,
        "--media_dir",
        str(STAGING_DIR),
    ]
    if poster:
        command.append("-s")
    else:
        command.extend(["--format", "webm", "-t"])
        if args.preview:
            command.append("-p")
    command.extend([str(Path(__file__).resolve()), "TimeRailPointOneScene"])
    return command


def promote_rendered_file(target_name: str, destination: Path) -> None:
    matches = sorted(STAGING_DIR.glob(f"**/{target_name}"), key=lambda path: path.stat().st_mtime)
    if not matches:
        raise FileNotFoundError(f"Could not find {target_name} under {STAGING_DIR}")
    destination.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(matches[-1], destination)


from manim import DOWN, LEFT, RIGHT, UP, Circle, FadeIn, FadeOut, Line, Rectangle, Scene, Text, Transform, VGroup, linear


class TimeRailPointOneScene(Scene):
    rail_x = -4.9
    rail_top = 2.35
    rail_bottom = -2.35

    def construct(self) -> None:
        if os.environ.get("SPIKE_RENDER_TARGET") == "poster":
            self.camera.background_color = PAGE_BACKGROUND

        stage = Rectangle(width=12.8, height=7.15, stroke_width=0, fill_color=PAGE_BACKGROUND, fill_opacity=0.96)
        rail_start = LEFT * abs(self.rail_x) + UP * self.rail_top
        rail_end = LEFT * abs(self.rail_x) + DOWN * abs(self.rail_bottom)
        base_rail = Line(rail_start, rail_end, color=GRAY_300, stroke_width=8)
        active_rail = Line(rail_start, rail_start, color=PRIMARY_RED, stroke_width=9)

        agenda_specs = [
            ("01", "Establish the frame", "What must be visible first.", 1.55),
            ("02", "Move through time", "How progress owns the sequence.", 0.0),
            ("03", "Resolve the section", "What should remain at the end.", -1.55),
        ]
        slots = VGroup()
        marks = VGroup()
        active_mark = None
        agenda_cards = []
        for index, (step, title, body, y) in enumerate(agenda_specs):
            slot = Rectangle(width=8.4, height=1.18, stroke_color=GRAY_200, stroke_width=2, fill_color=WHITE, fill_opacity=0.16)
            slot.move_to(RIGHT * 0.35 + UP * y)
            slots.add(slot)

            mark_position = LEFT * abs(self.rail_x) + UP * y
            mark = Circle(radius=0.14, color=GRAY_300, stroke_width=2)
            mark.set_fill(PAGE_BACKGROUND, opacity=1)
            mark.move_to(mark_position)
            marks.add(mark)
            if index == 0:
                active_mark = Circle(radius=0.2, color=PRIMARY_RED, stroke_width=3)
                active_mark.set_fill(WHITE, opacity=1)
                active_mark.move_to(mark_position)

            agenda_cards.append(self.build_agenda_card(step, title, body).move_to(slot))

        self.add(stage, base_rail, active_rail, slots, marks)
        self.wait(2.8)

        point_one_y = agenda_specs[0][3]
        point_one_position = LEFT * abs(self.rail_x) + UP * point_one_y
        self.play(active_rail.animate.put_start_and_end_on(rail_start, point_one_position), run_time=1.15, rate_func=linear)
        self.play(
            Transform(marks[0], active_mark),
            slots[0].animate.set_stroke(color=PRIMARY_RED, width=2.5, opacity=0.55),
            FadeIn(agenda_cards[0], shift=RIGHT * 0.22),
            run_time=1.2,
        )
        self.wait(2.0)

        future_group = VGroup(slots[1], slots[2], marks[1], marks[2])
        self.play(
            future_group.animate.set_opacity(0.2),
            slots[0].animate.set_stroke(color=PRIMARY_RED, width=2.5, opacity=0.75),
            run_time=0.75,
        )

        detail_panel = self.build_detail_panel()
        detail_panel.move_to(RIGHT * 1.65 + DOWN * 0.82)
        self.play(
            agenda_cards[0].animate.move_to(RIGHT * 0.1 + UP * 1.85).scale(1.06),
            slots[0].animate.move_to(RIGHT * 0.1 + UP * 1.85).scale(1.06),
            FadeOut(future_group),
            run_time=1.3,
        )
        self.play(FadeIn(detail_panel, shift=DOWN * 0.16), run_time=1.4)
        self.wait(2.0)

        row_cues = self.build_row_cues(detail_panel)
        for cue in row_cues:
            self.play(FadeIn(cue), run_time=0.35)
            self.wait(1.55)
            self.play(FadeOut(cue), run_time=0.25)

        self.wait(6.5)

    def build_agenda_card(self, step: str, title: str, body: str) -> VGroup:
        background = Rectangle(width=8.4, height=1.18, stroke_color=GRAY_200, stroke_width=2, fill_color=WHITE, fill_opacity=0.96)
        accent = Rectangle(width=0.11, height=1.18, stroke_width=0, fill_color=PRIMARY_RED, fill_opacity=1)
        accent.move_to(background.get_left() + RIGHT * 0.055)
        badge = Rectangle(width=0.76, height=0.3, stroke_width=0, fill_color=GRAY_700, fill_opacity=0.96)
        badge_label = Text(step, font=FONT_FAMILY, font_size=13, color=WHITE)
        title_text = Text(title, font=FONT_FAMILY, font_size=23, color=GRAY)
        body_text = Text(body, font=FONT_FAMILY, font_size=14, color=GRAY_600)
        content = VGroup(VGroup(badge, badge_label), title_text, body_text).arrange(DOWN, aligned_edge=LEFT, buff=0.09)
        content.move_to(background.get_center()).shift(LEFT * 0.12 + UP * 0.03)
        return VGroup(background, accent, content)

    def build_detail_panel(self) -> VGroup:
        panel = Rectangle(width=6.9, height=3.35, stroke_color=GRAY_200, stroke_width=2, fill_color=WHITE, fill_opacity=0.96)
        title = Text("Point 1 opens the frame", font=FONT_FAMILY, font_size=27, color=GRAY)
        title.move_to(panel.get_top() + DOWN * 0.45)
        rows = VGroup(
            self.build_detail_row("show", "The whole agenda is visible before motion."),
            self.build_detail_row("mark", "The rail reaches 01 before detail appears."),
            self.build_detail_row("focus", "Future items leave the stage quietly."),
        ).arrange(DOWN, aligned_edge=LEFT, buff=0.22)
        rows.move_to(panel.get_center() + DOWN * 0.35)
        return VGroup(panel, title, rows)

    def build_detail_row(self, label: str, body: str) -> VGroup:
        tag = Rectangle(width=0.78, height=0.34, stroke_width=0, fill_color=GRAY_700, fill_opacity=0.96)
        tag_text = Text(label, font=FONT_FAMILY, font_size=13, color=WHITE)
        body_text = Text(body, font=FONT_FAMILY, font_size=17, color=GRAY)
        return VGroup(VGroup(tag, tag_text), body_text).arrange(RIGHT, buff=0.18)

    def build_row_cues(self, detail_panel: VGroup) -> list[VGroup]:
        rows = detail_panel[2]
        cues = []
        for row in rows:
            cue_bar = Rectangle(width=0.08, height=0.44, stroke_width=0, fill_color=GRAY_700, fill_opacity=0.9)
            cue_bar.move_to(row.get_left() + LEFT * 0.12)
            cues.append(VGroup(cue_bar))
        return cues


def main() -> int:
    args = parse_args()
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    for poster in (False, True):
        env_target = "poster" if poster else "video"
        result = subprocess.run(render_command(args, poster=poster), check=False, env={**os.environ, "SPIKE_RENDER_TARGET": env_target})
        if result.returncode != 0:
            return result.returncode
        target = OUTPUT_DIR / ("time-rail-point-one.png" if poster else "time-rail-point-one.webm")
        promote_rendered_file(target.name, target)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
