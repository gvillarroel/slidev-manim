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
    parser = argparse.ArgumentParser(description="Render the time-rail-sequence Manim spike.")
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
    output = OUTPUT_DIR / ("time-rail-sequence.png" if poster else "time-rail-sequence.webm")
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
    command.extend([str(Path(__file__).resolve()), "TimeRailSequenceScene"])
    return command


def promote_rendered_file(target_name: str, destination: Path) -> None:
    matches = sorted(STAGING_DIR.glob(f"**/{target_name}"), key=lambda path: path.stat().st_mtime)
    if not matches:
        raise FileNotFoundError(f"Could not find {target_name} under {STAGING_DIR}")
    destination.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(matches[-1], destination)


from manim import DOWN, LEFT, RIGHT, UP, Circle, FadeIn, Line, Rectangle, Scene, Text, Transform, VGroup, linear


class TimeRailSequenceScene(Scene):
    def construct(self) -> None:
        if os.environ.get("SPIKE_RENDER_TARGET") == "poster":
            self.camera.background_color = PAGE_BACKGROUND

        stage = Rectangle(width=12.8, height=7.15, stroke_width=0, fill_color=PAGE_BACKGROUND, fill_opacity=0.96)
        rail_x = -4.75
        top_y = 2.35
        bottom_y = -2.45
        rail_start = LEFT * abs(rail_x) + UP * top_y
        rail_end = LEFT * abs(rail_x) + DOWN * abs(bottom_y)
        base_rail = Line(rail_start, rail_end, color=GRAY_300, stroke_width=8)
        active_rail = Line(rail_start, rail_start, color=PRIMARY_RED, stroke_width=9)
        terminal_rule = Line(RIGHT * 3.0 + DOWN * 2.6, RIGHT * 4.25 + DOWN * 2.6, color=PRIMARY_RED, stroke_width=6)
        terminal_rule.set_opacity(0)

        steps = [
            ("00", "Context appears", "The scene starts with a visible\npending structure.", 1.55),
            ("01", "Time advances", "The rail records progress before\nthe next state resolves.", 0.0),
            ("02", "Outcome holds", "The final state keeps the timeline\nas the narrator.", -1.55),
        ]

        slots = VGroup()
        pending_marks = VGroup()
        active_marks = []
        cards = []
        for step, title, body, y in steps:
            slot = Rectangle(width=8.8, height=1.34, stroke_color=GRAY_200, stroke_width=2, fill_color=WHITE, fill_opacity=0.18)
            slot.move_to(RIGHT * 0.4 + UP * y)
            slots.add(slot)

            mark_position = LEFT * abs(rail_x) + UP * y
            pending = Circle(radius=0.14, color=GRAY_300, stroke_width=2)
            pending.set_fill(PAGE_BACKGROUND, opacity=1)
            pending.move_to(mark_position)
            pending_marks.add(pending)

            active = Circle(radius=0.2, color=PRIMARY_RED, stroke_width=3)
            active.set_fill(WHITE, opacity=1)
            active.move_to(mark_position)
            active_marks.append(active)

            cards.append(self.build_card(step, title, body).move_to(slot))

        self.add(stage, base_rail, active_rail, slots, pending_marks, terminal_rule)
        self.wait(2.8)

        for index, (_, _, _, y) in enumerate(steps):
            mark_position = LEFT * abs(rail_x) + UP * y
            self.play(active_rail.animate.put_start_and_end_on(rail_start, mark_position), run_time=1.2, rate_func=linear)
            self.play(
                Transform(pending_marks[index], active_marks[index]),
                slots[index].animate.set_stroke(color=PRIMARY_RED, width=2.5, opacity=0.55),
                FadeIn(cards[index], shift=RIGHT * 0.24),
                run_time=1.2,
            )
            self.play(slots[index].animate.set_stroke(color=GRAY_200, width=2, opacity=0.24), run_time=0.35)
            self.wait(2.7)

        self.play(terminal_rule.animate.set_opacity(1), run_time=0.8)
        self.wait(6.5)

    def build_card(self, step: str, title: str, body: str) -> VGroup:
        background = Rectangle(width=8.8, height=1.34, stroke_color=GRAY_200, stroke_width=2, fill_color=WHITE, fill_opacity=0.96)
        accent = Rectangle(width=0.12, height=1.34, stroke_width=0, fill_color=PRIMARY_RED, fill_opacity=1)
        accent.move_to(background.get_left() + RIGHT * 0.06)
        badge = Rectangle(width=0.84, height=0.32, stroke_width=0, fill_color=GRAY_700, fill_opacity=0.96)
        badge_label = Text(step, font=FONT_FAMILY, font_size=14, color=WHITE)
        title_text = Text(title, font=FONT_FAMILY, font_size=25, color=GRAY)
        body_text = Text(body, font=FONT_FAMILY, font_size=15, color=GRAY_600)
        content = VGroup(VGroup(badge, badge_label), title_text, body_text).arrange(DOWN, aligned_edge=LEFT, buff=0.1)
        content.move_to(background.get_center()).shift(LEFT * 0.15 + UP * 0.04)
        return VGroup(background, accent, content)


def main() -> int:
    args = parse_args()
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    for poster in (False, True):
        env_target = "poster" if poster else "video"
        result = subprocess.run(render_command(args, poster=poster), check=False, env={**os.environ, "SPIKE_RENDER_TARGET": env_target})
        if result.returncode != 0:
            return result.returncode
        target = OUTPUT_DIR / ("time-rail-sequence.png" if poster else "time-rail-sequence.webm")
        promote_rendered_file(target.name, target)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
