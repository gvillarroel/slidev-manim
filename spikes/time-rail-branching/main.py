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
    parser = argparse.ArgumentParser(description="Render the time-rail-branching Manim spike.")
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
    output = OUTPUT_DIR / ("time-rail-branching.png" if poster else "time-rail-branching.webm")
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
    command.extend([str(Path(__file__).resolve()), "TimeRailBranchingScene"])
    return command


def promote_rendered_file(target_name: str, destination: Path) -> None:
    matches = sorted(STAGING_DIR.glob(f"**/{target_name}"), key=lambda path: path.stat().st_mtime)
    if not matches:
        raise FileNotFoundError(f"Could not find {target_name} under {STAGING_DIR}")
    destination.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(matches[-1], destination)


from manim import DOWN, LEFT, RIGHT, UP, Circle, Create, FadeIn, Line, Rectangle, Scene, Text, Transform, VGroup, linear


class TimeRailBranchingScene(Scene):
    def construct(self) -> None:
        if os.environ.get("SPIKE_RENDER_TARGET") == "poster":
            self.camera.background_color = PAGE_BACKGROUND

        stage = Rectangle(width=12.8, height=7.15, stroke_width=0, fill_color=PAGE_BACKGROUND, fill_opacity=0.96)
        rail_x = -4.9
        rail_start = LEFT * abs(rail_x) + UP * 2.55
        rail_end = LEFT * abs(rail_x) + DOWN * 2.55
        base_rail = Line(rail_start, rail_end, color=GRAY_300, stroke_width=8)
        active_rail = Line(rail_start, rail_start, color=PRIMARY_RED, stroke_width=9)
        terminal_rule = Line(RIGHT * 3.15 + DOWN * 2.55, RIGHT * 4.35 + DOWN * 2.55, color=PRIMARY_RED, stroke_width=6)
        terminal_rule.set_opacity(0)

        branches = [
            ("A", "First fork", "One branch opens when\ntime reaches this mark.", 1.45, RIGHT * 0.05 + UP * 1.45),
            ("B", "Middle fork", "The rail keeps ownership\nwhile the side state lands.", 0.0, RIGHT * 0.9 + UP * 0.0),
            ("C", "Late fork", "The ending keeps branch guides\nquiet and subordinate.", -1.45, RIGHT * 0.05 + DOWN * 1.45),
        ]

        branch_guides = []
        pending_marks = VGroup()
        active_marks = []
        cards = []
        branch_slots = VGroup()
        for label, title, body, y, card_position in branches:
            mark_position = LEFT * abs(rail_x) + UP * y
            guide = Line(mark_position + RIGHT * 0.2, card_position + LEFT * 3.25, color=GRAY_300, stroke_width=4)
            guide.set_opacity(0.2)
            branch_guides.append(guide)

            pending = Circle(radius=0.14, color=GRAY_300, stroke_width=2)
            pending.set_fill(PAGE_BACKGROUND, opacity=1)
            pending.move_to(mark_position)
            pending_marks.add(pending)

            active = Circle(radius=0.2, color=PRIMARY_RED, stroke_width=3)
            active.set_fill(WHITE, opacity=1)
            active.move_to(mark_position)
            active_marks.append(active)

            slot = Rectangle(width=5.7, height=1.22, stroke_color=GRAY_200, stroke_width=2, fill_color=WHITE, fill_opacity=0.18)
            slot.move_to(card_position)
            branch_slots.add(slot)
            cards.append(self.build_card(label, title, body).move_to(card_position))

        self.add(stage, base_rail, active_rail, *branch_guides, branch_slots, pending_marks, terminal_rule)
        self.wait(2.8)

        for index, (_, _, _, y, _) in enumerate(branches):
            mark_position = LEFT * abs(rail_x) + UP * y
            self.play(active_rail.animate.put_start_and_end_on(rail_start, mark_position), run_time=1.15, rate_func=linear)
            branch_guides[index].set_color(PRIMARY_RED)
            self.play(
                Transform(pending_marks[index], active_marks[index]),
                branch_slots[index].animate.set_stroke(color=PRIMARY_RED, width=2.4, opacity=0.52),
                Create(branch_guides[index]),
                run_time=0.95,
            )
            self.play(FadeIn(cards[index], shift=RIGHT * 0.2), run_time=1.0)
            self.play(
                branch_guides[index].animate.set_color(GRAY_300).set_opacity(0.24),
                branch_slots[index].animate.set_stroke(color=GRAY_200, width=2, opacity=0.22),
                run_time=0.35,
            )
            self.wait(2.45)

        self.play(terminal_rule.animate.set_opacity(1), run_time=0.8)
        self.wait(6.5)

    def build_card(self, label: str, title: str, body: str) -> VGroup:
        background = Rectangle(width=5.7, height=1.22, stroke_color=GRAY_200, stroke_width=2, fill_color=WHITE, fill_opacity=0.96)
        accent = Rectangle(width=0.11, height=1.22, stroke_width=0, fill_color=PRIMARY_RED, fill_opacity=1)
        accent.move_to(background.get_left() + RIGHT * 0.055)
        badge = Rectangle(width=0.58, height=0.3, stroke_width=0, fill_color=GRAY_700, fill_opacity=0.96)
        badge_label = Text(label, font=FONT_FAMILY, font_size=13, color=WHITE)
        title_text = Text(title, font=FONT_FAMILY, font_size=22, color=GRAY)
        body_text = Text(body, font=FONT_FAMILY, font_size=14, color=GRAY_600)
        content = VGroup(VGroup(badge, badge_label), title_text, body_text).arrange(DOWN, aligned_edge=LEFT, buff=0.09)
        content.move_to(background.get_center()).shift(LEFT * 0.1 + UP * 0.03)
        return VGroup(background, accent, content)


def main() -> int:
    args = parse_args()
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    for poster in (False, True):
        env_target = "poster" if poster else "video"
        result = subprocess.run(render_command(args, poster=poster), check=False, env={**os.environ, "SPIKE_RENDER_TARGET": env_target})
        if result.returncode != 0:
            return result.returncode
        target = OUTPUT_DIR / ("time-rail-branching.png" if poster else "time-rail-branching.webm")
        promote_rendered_file(target.name, target)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
