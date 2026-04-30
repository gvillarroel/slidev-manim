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
    matches = sorted(STAGING_DIR.glob(f"**/{target_name}"))
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


from manim import DOWN, LEFT, RIGHT, Scene, UP, WHITE, Circle, Dot, Line, RoundedRectangle, Text, linear


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

    def common_frame(self) -> tuple[RoundedRectangle, Line, Dot, Dot, Circle]:
        frame = RoundedRectangle(
            width=self.panel_width,
            height=self.panel_height,
            corner_radius=0.36,
            stroke_color=PRIMARY_BLUE,
            stroke_width=6,
            fill_color=PAGE_BACKGROUND,
            fill_opacity=0.96,
        )
        lane = Line(
            LEFT * 4.65 + DOWN * 0.25,
            RIGHT * 4.65 + DOWN * 0.25,
            color=GRAY_300,
            stroke_width=8,
        )
        start_marker = Dot(point=LEFT * 4.65 + DOWN * 0.25, color=GRAY_600, radius=0.075)
        end_marker = Dot(point=RIGHT * 4.65 + DOWN * 0.25, color=GRAY_600, radius=0.075)
        moving_circle = (
            Circle(radius=0.82, color=PRIMARY_GREEN, stroke_width=10)
            .set_fill(PRIMARY_GREEN, opacity=0.94)
            .move_to(LEFT * 4.35 + UP * 0.88)
        )
        return frame, lane, start_marker, end_marker, moving_circle

    def render_approach_a(self) -> None:
        frame, lane, start_marker, end_marker, moving_circle = self.common_frame()
        title = Text("Approach A", font_size=28, weight="BOLD", color=GRAY).move_to(
            UP * 2.18
        )
        subtitle = Text("minimal motion", font_size=20, color=GRAY).move_to(UP * 1.82)

        self.add(frame, lane, start_marker, end_marker, title, subtitle, moving_circle)
        self.play(
            moving_circle.animate.move_to(RIGHT * 4.35 + UP * 0.88),
            run_time=3.0,
            rate_func=linear,
        )
        self.wait(0.15)

    def render_approach_b(self) -> None:
        frame, lane, start_marker, end_marker, moving_circle = self.common_frame()
        title = Text("Approach B", font_size=28, weight="BOLD", color=GRAY).move_to(
            UP * 2.18
        )
        subtitle = Text("same motion, more emphasis", font_size=20, color=GRAY).move_to(
            UP * 1.82
        )
        halo = Circle(radius=1.03, color=PRIMARY_YELLOW, stroke_width=8).set_stroke(opacity=0.42)
        halo.move_to(moving_circle.get_center())
        trail = Line(
            LEFT * 4.05 + UP * 0.88,
            LEFT * 3.0 + UP * 0.88,
            color=PRIMARY_ORANGE,
            stroke_width=12,
            sheen_factor=0.2,
        ).set_opacity(0.6)

        self.add(frame, lane, start_marker, end_marker, title, subtitle, trail, halo, moving_circle)
        self.play(
            moving_circle.animate.move_to(RIGHT * 4.35 + UP * 0.88),
            halo.animate.move_to(RIGHT * 4.35 + UP * 0.88),
            run_time=3.0,
            rate_func=linear,
        )
        self.wait(0.15)
