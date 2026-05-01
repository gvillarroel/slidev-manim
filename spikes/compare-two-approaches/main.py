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
PRIMARY_ORANGE = "#e77204"
PRIMARY_YELLOW = "#f1c319"
PRIMARY_GREEN = "#45842a"
PRIMARY_BLUE = "#007298"
PRIMARY_PURPLE = "#652f6c"
WHITE = "#ffffff"
GRAY = "#333e48"
GRAY_100 = "#e7e7e7"
GRAY_200 = "#cfcfcf"
GRAY_300 = "#b5b5b5"
GRAY_400 = "#9c9c9c"
GRAY_600 = "#696969"
GRAY_700 = "#4f4f4f"
HIGHLIGHT_RED = "#ffccd5"
HIGHLIGHT_ORANGE = "#ffe5cc"
HIGHLIGHT_YELLOW = "#fff4cc"
HIGHLIGHT_GREEN = "#dbffcc"
HIGHLIGHT_BLUE = "#cdf3ff"
HIGHLIGHT_PURPLE = "#f9ccff"
SHADOW_BLUE = "#004d66"
PAGE_BACKGROUND = "#f7f7f7"
TEXT_FONT = "Arial"

VARIANTS = {
    "approach-a": "approach-a",
    "approach-b": "approach-b",
}


class _Args(argparse.Namespace):
    quality: str
    preview: bool


def parse_args() -> _Args:
    parser = argparse.ArgumentParser(
        description="Render the compare-two-approaches Manim spike."
    )
    parser.add_argument(
        "--quality",
        choices=("low", "medium", "high", "production", "4k"),
        default="medium",
        help="Manim quality preset. Defaults to medium for fast iteration.",
    )
    parser.add_argument(
        "--preview",
        action="store_true",
        help="Open the rendered video after completion.",
    )
    return parser.parse_args(namespace=_Args())


def quality_flag(quality: str) -> str:
    return {
        "low": "-ql",
        "medium": "-qm",
        "high": "-qh",
        "production": "-qp",
        "4k": "-qk",
    }[quality]


def build_command(args: _Args, *, variant: str, poster: bool) -> list[str]:
    STAGING_DIR.mkdir(parents=True, exist_ok=True)
    target = f"compare-two-approaches-{variant}"
    command = [
        sys.executable,
        "-m",
        "manim",
        "render",
        quality_flag(args.quality),
    ]

    if poster:
        command.append("-s")
    else:
        command.extend(["--format", "webm", "-t"])
        if args.preview:
            command.append("-p")

    command.extend(
        [
            "-r",
            "1600,900",
            "-o",
            target,
            "--media_dir",
            str(STAGING_DIR),
        ]
    )
    command.extend([str(Path(__file__).resolve()), "CompareTwoApproachesScene"])
    return command


def promote_rendered_file(target_name: str, destination: Path) -> None:
    matches = sorted(STAGING_DIR.glob(f"**/{target_name}"), key=lambda path: path.stat().st_mtime)
    if not matches:
        raise FileNotFoundError(f"Could not find {target_name} under {STAGING_DIR}")

    destination.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(matches[-1], destination)


def render_variant(args: _Args, variant: str) -> None:
    video_env = os.environ.copy()
    video_env["SPIKE_RENDER_TARGET"] = "video"
    video_env["SPIKE_VARIANT"] = variant
    video_result = subprocess.run(build_command(args, variant=variant, poster=False), env=video_env)
    if video_result.returncode != 0:
        raise SystemExit(video_result.returncode)
    promote_rendered_file(f"compare-two-approaches-{variant}.webm", OUTPUT_DIR / f"compare-two-approaches-{variant}.webm")

    poster_env = os.environ.copy()
    poster_env["SPIKE_RENDER_TARGET"] = "poster"
    poster_env["SPIKE_VARIANT"] = variant
    poster_result = subprocess.run(build_command(args, variant=variant, poster=True), env=poster_env)
    if poster_result.returncode != 0:
        raise SystemExit(poster_result.returncode)
    promote_rendered_file(f"compare-two-approaches-{variant}.png", OUTPUT_DIR / f"compare-two-approaches-{variant}.png")


def main() -> int:
    args = parse_args()
    for variant in VARIANTS:
        render_variant(args, variant)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())


from manim import (
    DOWN,
    LEFT,
    ORIGIN,
    RIGHT,
    Scene,
    UP,
    Circle,
    CubicBezier,
    Dot,
    FadeOut,
    Line,
    MoveAlongPath,
    Rectangle,
    Text,
    VGroup,
    rate_functions,
)


class CompareTwoApproachesScene(Scene):
    panel_width = 11.4
    panel_height = 5.9

    def construct(self) -> None:
        variant = os.environ.get("SPIKE_VARIANT", "approach-a")
        is_poster = os.environ.get("SPIKE_RENDER_TARGET") == "poster"
        if is_poster:
            self.camera.background_color = WHITE

        if variant == "approach-b":
            self.render_approach_b()
        else:
            self.render_approach_a()

    def common_frame(self) -> tuple[Rectangle, Line, Rectangle, Rectangle, Circle]:
        frame = Rectangle(
            width=self.panel_width,
            height=self.panel_height,
            stroke_color=GRAY_200,
            stroke_width=3,
            fill_color=PAGE_BACKGROUND,
            fill_opacity=0.96,
        )
        title_rule = Line(
            LEFT * 4.65 + UP * 1.55,
            RIGHT * 4.65 + UP * 1.55,
            color=GRAY_200,
            stroke_width=2,
        ).set_opacity(0.7)
        lane = Line(
            LEFT * 4.05 + DOWN * 0.45,
            RIGHT * 4.05 + DOWN * 0.45,
            color=GRAY_300,
            stroke_width=5,
        )
        start_slot = Rectangle(
            width=1.05,
            height=1.05,
            stroke_color=GRAY_400,
            stroke_width=2.4,
            fill_opacity=0,
        ).move_to(LEFT * 4.05 + DOWN * 0.45)
        end_slot = Rectangle(
            width=1.05,
            height=1.05,
            stroke_color=GRAY_400,
            stroke_width=2.4,
            fill_opacity=0,
        ).move_to(RIGHT * 4.05 + DOWN * 0.45)
        start_slot.set_stroke(opacity=0.34)
        end_slot.set_stroke(opacity=0.34)
        moving_circle = (
            Circle(radius=0.46, color=PRIMARY_GREEN, stroke_width=5)
            .set_fill(PRIMARY_GREEN, opacity=0.94)
            .move_to(start_slot)
        )
        frame.add(title_rule)
        return frame, lane, start_slot, end_slot, moving_circle

    def title_group(self, title: str, subtitle: str) -> VGroup:
        title_mob = Text(title, font=TEXT_FONT, font_size=28, weight="BOLD", color=GRAY).move_to(UP * 2.27)
        subtitle_mob = Text(subtitle, font=TEXT_FONT, font_size=18, color=GRAY_700).move_to(UP * 1.94)
        return VGroup(title_mob, subtitle_mob)

    def render_approach_a(self) -> None:
        frame, lane, start_slot, end_slot, moving_circle = self.common_frame()
        title = self.title_group("Approach A", "direct transfer")
        direct_route = Line(
            start_slot.get_center(),
            end_slot.get_center(),
            color=PRIMARY_RED,
            stroke_width=5,
        ).set_opacity(0.0)
        terminal_ring = Circle(radius=0.62, color=PRIMARY_RED, stroke_width=4).move_to(end_slot)
        terminal_ring.set_stroke(opacity=0)

        self.add(frame, lane, start_slot, end_slot, title, moving_circle)
        self.wait(2.7)
        self.add(direct_route)
        self.play(
            direct_route.animate.set_opacity(0.38),
            end_slot.animate.set_stroke(color=PRIMARY_RED, opacity=0.62),
            run_time=1.25,
            rate_func=rate_functions.ease_out_cubic,
        )
        self.wait(1.25)
        self.play(
            MoveAlongPath(moving_circle, direct_route),
            run_time=9.2,
            rate_func=rate_functions.ease_in_out_sine,
        )
        self.wait(1.45)
        self.add(terminal_ring)
        self.play(
            terminal_ring.animate.set_stroke(opacity=0.95),
            direct_route.animate.set_opacity(0.12),
            start_slot.animate.set_stroke(opacity=0.08),
            run_time=1.1,
            rate_func=rate_functions.ease_out_cubic,
        )
        resolved = VGroup(moving_circle, terminal_ring)
        self.play(
            FadeOut(lane),
            FadeOut(direct_route),
            FadeOut(start_slot),
            FadeOut(end_slot),
            resolved.animate.move_to(ORIGIN + DOWN * 0.2),
            run_time=2.1,
            rate_func=rate_functions.ease_in_out_cubic,
        )
        self.wait(7.1)

    def render_approach_b(self) -> None:
        frame, lane, start_slot, end_slot, moving_circle = self.common_frame()
        title = self.title_group("Approach B", "receiver-guided handoff")
        guide_path = CubicBezier(
            start_slot.get_center(),
            LEFT * 1.8 + UP * 0.95,
            RIGHT * 1.8 + UP * 0.95,
            end_slot.get_center(),
        )
        guide_path.set_stroke(color=PRIMARY_ORANGE, width=4, opacity=0.16)
        active_guide = Dot(point=guide_path.get_start(), radius=0.075, color=PRIMARY_RED)
        halo = Circle(radius=1.03, color=PRIMARY_YELLOW, stroke_width=8).set_stroke(opacity=0.42)
        halo.move_to(moving_circle.get_center())
        receiver_cue = Rectangle(
            width=1.35,
            height=1.35,
            stroke_color=PRIMARY_RED,
            stroke_width=3.5,
            fill_opacity=0,
        ).move_to(end_slot)
        receiver_cue.set_stroke(opacity=0)
        terminal_ring = Circle(radius=0.66, color=PRIMARY_RED, stroke_width=4.4).move_to(end_slot)
        terminal_ring.set_stroke(opacity=0)

        self.add(frame, lane, start_slot, end_slot, title, guide_path, halo, moving_circle)
        self.wait(2.6)
        self.play(
            guide_path.animate.set_stroke(opacity=0.38),
            end_slot.animate.set_stroke(color=PRIMARY_ORANGE, opacity=0.62),
            run_time=1.3,
            rate_func=rate_functions.ease_out_cubic,
        )
        self.wait(0.9)
        self.add(active_guide)
        self.play(
            MoveAlongPath(active_guide, guide_path),
            run_time=3.2,
            rate_func=rate_functions.ease_in_out_sine,
        )
        self.add(receiver_cue)
        self.play(
            receiver_cue.animate.set_stroke(opacity=0.78),
            FadeOut(active_guide),
            run_time=0.85,
            rate_func=rate_functions.ease_out_cubic,
        )
        self.wait(0.8)
        self.play(
            MoveAlongPath(moving_circle, guide_path),
            MoveAlongPath(halo, guide_path),
            run_time=7.8,
            rate_func=rate_functions.ease_in_out_sine,
        )
        self.wait(1.15)
        self.add(terminal_ring)
        self.play(
            terminal_ring.animate.set_stroke(opacity=0.95),
            receiver_cue.animate.set_stroke(opacity=0.0),
            guide_path.animate.set_opacity(0.1),
            run_time=1.1,
            rate_func=rate_functions.ease_out_cubic,
        )
        resolved = VGroup(moving_circle, halo, terminal_ring)
        self.play(
            FadeOut(lane),
            FadeOut(guide_path),
            FadeOut(start_slot),
            FadeOut(end_slot),
            FadeOut(receiver_cue),
            resolved.animate.move_to(ORIGIN + DOWN * 0.2),
            run_time=2.15,
            rate_func=rate_functions.ease_in_out_cubic,
        )
        self.wait(6.7)
