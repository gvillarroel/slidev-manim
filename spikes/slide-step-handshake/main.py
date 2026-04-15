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

from manim import *

SPIKE_DIR = Path(__file__).resolve().parent
REPO_ROOT = SPIKE_DIR.parent.parent
SPIKE_NAME = SPIKE_DIR.name
OUTPUT_DIR = REPO_ROOT / "videos" / SPIKE_NAME
STAGING_DIR = OUTPUT_DIR / ".manim"
VIDEO_FILE = OUTPUT_DIR / "slide-step-handshake.webm"
POSTER_FILE = OUTPUT_DIR / "slide-step-handshake.png"


class _Args(argparse.Namespace):
    quality: str
    preview: bool


def parse_args() -> _Args:
    parser = argparse.ArgumentParser(description="Render the slide-step-handshake spike.")
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


def render_command(args: _Args, poster: bool) -> list[str]:
    STAGING_DIR.mkdir(parents=True, exist_ok=True)
    command = [
        sys.executable,
        "-m",
        "manim",
        "render",
        quality_flag(args.quality),
        "-r",
        "1920,1080",
        "--format",
        "webm",
        "-o",
        (POSTER_FILE if poster else VIDEO_FILE).stem,
        "--media_dir",
        str(STAGING_DIR),
    ]
    if not poster:
        command.append("-t")
    if poster:
        command.append("-s")
    elif args.preview:
        command.append("-p")
    command.extend([str(Path(__file__).resolve()), "SlideStepHandshakeScene"])
    return command


def promote_rendered_file(target_name: str, destination: Path) -> None:
    matches = sorted(STAGING_DIR.glob(f"**/{target_name}"))
    if not matches:
        raise FileNotFoundError(f"Could not find {target_name} under {STAGING_DIR}")

    destination.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(matches[-1], destination)


def main() -> int:
    args = parse_args()

    print(f"Rendering SlideStepHandshakeScene into {VIDEO_FILE}")
    video_result = subprocess.run(render_command(args, poster=False), check=False)
    if video_result.returncode != 0:
        raise SystemExit(video_result.returncode)
    promote_rendered_file(VIDEO_FILE.name, VIDEO_FILE)

    poster_env = os.environ.copy()
    poster_env["SPIKE_RENDER_TARGET"] = "poster"
    print(f"Rendering SlideStepHandshakeScene poster into {POSTER_FILE}")
    poster_result = subprocess.run(render_command(args, poster=True), check=False, env=poster_env)
    if poster_result.returncode != 0:
        raise SystemExit(poster_result.returncode)
    promote_rendered_file(POSTER_FILE.name, POSTER_FILE)

    return 0


class SlideStepHandshakeScene(Scene):
    def construct(self) -> None:
        if os.environ.get("SPIKE_RENDER_TARGET") == "poster":
            self.camera.background_color = WHITE

        left_node = Circle(radius=0.78, color=BLUE_C, stroke_width=10)
        left_node.set_fill(BLUE_C, opacity=0.96)
        right_node = Circle(radius=0.78, color=ORANGE, stroke_width=10)
        right_node.set_fill(ORANGE, opacity=0.96)

        left_node.move_to(LEFT * 4.0 + DOWN * 0.15)
        right_node.move_to(RIGHT * 4.0 + UP * 0.15)

        left_label = Text("Step A", font_size=30, weight=BOLD, color=WHITE)
        right_label = Text("Step B", font_size=30, weight=BOLD, color=WHITE)
        left_label.move_to(left_node)
        right_label.move_to(right_node)

        bridge = Line(left_node.get_right(), right_node.get_left(), color=TEAL_B, stroke_width=8)
        bridge.set_stroke(opacity=0.35)

        pulse = Circle(radius=0.12, color=TEAL_B, stroke_width=6)
        pulse.set_fill(TEAL_B, opacity=0.22)
        pulse.move_to(ORIGIN)

        anchor = Dot(color=TEAL_B, radius=0.06)
        anchor.move_to(ORIGIN)

        self.add(bridge, left_node, right_node, left_label, right_label, pulse, anchor)
        self.play(
            left_node.animate.move_to(LEFT * 1.75 + DOWN * 0.1),
            right_node.animate.move_to(RIGHT * 1.75 + UP * 0.1),
            left_label.animate.move_to(LEFT * 1.75 + DOWN * 0.1),
            right_label.animate.move_to(RIGHT * 1.75 + UP * 0.1),
            bridge.animate.put_start_and_end_on(LEFT * 1.25 + DOWN * 0.1, RIGHT * 1.25 + UP * 0.1),
            run_time=1.8,
            rate_func=smooth,
        )
        self.play(
            left_node.animate.move_to(LEFT * 0.95 + DOWN * 0.05),
            right_node.animate.move_to(RIGHT * 0.95 + UP * 0.05),
            left_label.animate.scale(0.95),
            right_label.animate.scale(0.95),
            bridge.animate.put_start_and_end_on(LEFT * 0.65 + DOWN * 0.05, RIGHT * 0.65 + UP * 0.05),
            pulse.animate.scale(2.2),
            run_time=1.35,
            rate_func=there_and_back,
        )
        self.wait(0.15)


if __name__ == "__main__":
    raise SystemExit(main())
