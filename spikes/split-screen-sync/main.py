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

OUTPUT_VIDEO = OUTPUT_DIR / "split-screen-sync.webm"
OUTPUT_POSTER = OUTPUT_DIR / "split-screen-sync.png"


class _Args(argparse.Namespace):
    quality: str
    preview: bool


def parse_args() -> _Args:
    parser = argparse.ArgumentParser(
        description="Render the split-screen-sync Manim spike."
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


def build_command(args: _Args, *, poster: bool) -> list[str]:
    STAGING_DIR.mkdir(parents=True, exist_ok=True)
    output = OUTPUT_POSTER if poster else OUTPUT_VIDEO
    command = [
        sys.executable,
        "-m",
        "manim",
        "render",
        quality_flag(args.quality),
    ]

    if poster:
        command.extend(["-s"])
    else:
        command.extend(["--format", "webm", "-t"])
        if args.preview:
            command.append("-p")

    command.extend(
        [
            "-r",
            "1600,900",
            "-o",
            output.stem,
            "--media_dir",
            str(STAGING_DIR),
        ]
    )
    command.extend([str(Path(__file__).resolve()), "SplitScreenSyncScene"])
    return command


def promote_rendered_file(target_name: str, destination: Path) -> None:
    matches = sorted(STAGING_DIR.glob(f"**/{target_name}"))
    if not matches:
        raise FileNotFoundError(f"Could not find {target_name} under {STAGING_DIR}")

    destination.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(matches[-1], destination)


def main() -> int:
    args = parse_args()

    video_env = os.environ.copy()
    video_env["SPIKE_RENDER_TARGET"] = "video"
    video_result = subprocess.run(build_command(args, poster=False), env=video_env)
    if video_result.returncode != 0:
        return video_result.returncode
    promote_rendered_file(OUTPUT_VIDEO.name, OUTPUT_VIDEO)

    poster_env = os.environ.copy()
    poster_env["SPIKE_RENDER_TARGET"] = "poster"
    poster_result = subprocess.run(build_command(args, poster=True), env=poster_env)
    if poster_result.returncode != 0:
        return poster_result.returncode
    promote_rendered_file(OUTPUT_POSTER.name, OUTPUT_POSTER)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())


from manim import BLUE_E, DOWN, GREY_B, GREY_D, LEFT, RIGHT, Scene, UP, WHITE, Circle, Line, RoundedRectangle, linear


class SplitScreenSyncScene(Scene):
    panel_width = 11.1
    panel_height = 5.8
    circle_radius = 0.78
    start_x = -4.6
    end_x = 4.6
    lane_y = -0.2
    run_time = 3.1

    def construct(self) -> None:
        if os.environ.get("SPIKE_RENDER_TARGET") == "poster":
            self.camera.background_color = WHITE

        frame = RoundedRectangle(
            width=self.panel_width,
            height=self.panel_height,
            corner_radius=0.35,
            stroke_color=BLUE_E,
            stroke_width=6,
        )
        lane = Line(
            LEFT * 4.45 + DOWN * abs(self.lane_y),
            RIGHT * 4.45 + DOWN * abs(self.lane_y),
            color=GREY_B,
            stroke_width=8,
        )
        start_marker = Circle(radius=0.09, color=GREY_D, stroke_width=0).move_to(
            LEFT * 4.45 + DOWN * abs(self.lane_y)
        )
        end_marker = Circle(radius=0.09, color=GREY_D, stroke_width=0).move_to(
            RIGHT * 4.45 + DOWN * abs(self.lane_y)
        )
        moving_circle = (
            Circle(radius=self.circle_radius, color=BLUE_E, stroke_width=10)
            .set_fill(BLUE_E, opacity=0.93)
            .move_to(LEFT * abs(self.start_x) + UP * 0.9)
        )

        self.add(frame, lane, start_marker, end_marker, moving_circle)
        self.play(
            moving_circle.animate.move_to(RIGHT * abs(self.end_x) + UP * 0.9),
            run_time=self.run_time,
            rate_func=linear,
        )
        self.wait(0.15)
