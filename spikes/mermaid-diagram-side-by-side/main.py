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
VIDEO_PATH = OUTPUT_DIR / "mermaid-diagram-side-by-side.webm"
POSTER_PATH = OUTPUT_DIR / "mermaid-diagram-side-by-side.png"


class _Args(argparse.Namespace):
    quality: str
    preview: bool


def parse_args() -> _Args:
    parser = argparse.ArgumentParser(description="Render the mermaid-diagram-side-by-side Manim spike.")
    parser.add_argument(
        "--quality",
        choices=("low", "medium", "high", "production", "4k"),
        default="medium",
        help="Manim quality preset. Defaults to medium for review speed.",
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


def render_command(args: _Args, *, poster: bool) -> list[str]:
    STAGING_DIR.mkdir(parents=True, exist_ok=True)
    command = [
        sys.executable,
        "-m",
        "manim",
        "render",
        quality_flag(args.quality),
        "-r",
        "1600,900",
        "--format",
        "webm",
        "-o",
        (POSTER_PATH if poster else VIDEO_PATH).stem,
        "--media_dir",
        str(STAGING_DIR),
    ]
    if not poster:
        command.append("-t")
    if poster:
        command.append("-s")
    elif args.preview:
        command.append("-p")
    command.extend([str(Path(__file__).resolve()), "MermaidDiagramSideBySideScene"])
    return command


def promote_rendered_file(target_name: str, destination: Path) -> None:
    matches = sorted(STAGING_DIR.glob(f"**/{target_name}"))
    if not matches:
        raise FileNotFoundError(f"Could not find {target_name} under {STAGING_DIR}")
    destination.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(matches[-1], destination)


def render_scene(args: _Args) -> None:
    video_env = os.environ.copy()
    video_env["SPIKE_RENDER_TARGET"] = "video"
    video_result = subprocess.run(render_command(args, poster=False), check=False, env=video_env)
    if video_result.returncode != 0:
        raise SystemExit(video_result.returncode)
    promote_rendered_file(VIDEO_PATH.name, VIDEO_PATH)

    poster_env = os.environ.copy()
    poster_env["SPIKE_RENDER_TARGET"] = "poster"
    poster_result = subprocess.run(render_command(args, poster=True), check=False, env=poster_env)
    if poster_result.returncode != 0:
        raise SystemExit(poster_result.returncode)
    promote_rendered_file(POSTER_PATH.name, POSTER_PATH)


def main() -> int:
    args = parse_args()
    render_scene(args)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())


from manim import (
    BLUE_B,
    BLUE_C,
    BLUE_D,
    BLUE_E,
    Dot,
    LEFT,
    Line,
    MoveAlongPath,
    RIGHT,
    RoundedRectangle,
    Scene,
    Text,
    VGroup,
    WHITE,
    always_redraw,
    linear,
)


class MermaidDiagramSideBySideScene(Scene):
    def construct(self) -> None:
        if os.environ.get("SPIKE_RENDER_TARGET") == "poster":
            self.camera.background_color = WHITE

        source = RoundedRectangle(width=2.4, height=1.0, corner_radius=0.18)
        source.set_stroke(BLUE_D, width=6, opacity=0.6)
        source.set_fill(BLUE_D, opacity=0.06)
        source.shift(LEFT * 4.0)

        transform_box = RoundedRectangle(width=2.6, height=1.0, corner_radius=0.18)
        transform_box.set_stroke(BLUE_C, width=6, opacity=0.6)
        transform_box.set_fill(BLUE_C, opacity=0.06)

        output = RoundedRectangle(width=2.4, height=1.0, corner_radius=0.18)
        output.set_stroke(BLUE_B, width=6, opacity=0.6)
        output.set_fill(BLUE_B, opacity=0.06)
        output.shift(RIGHT * 4.0)

        source_label = Text("Source", font_size=30, color=BLUE_E).move_to(source)
        transform_label = Text("Transform", font_size=28, color=BLUE_E).move_to(transform_box)
        output_label = Text("Output", font_size=30, color=BLUE_E).move_to(output)

        path_a = Line(source.get_right(), transform_box.get_left(), color=BLUE_C, stroke_width=8)
        path_a.set_stroke(opacity=0.35)
        path_b = Line(transform_box.get_right(), output.get_left(), color=BLUE_B, stroke_width=8)
        path_b.set_stroke(opacity=0.35)

        pulse = Dot(color=BLUE_E, radius=0.16).move_to(path_a.get_start())
        glow = always_redraw(
            lambda: RoundedRectangle(width=0.55, height=0.55, corner_radius=0.28)
            .set_stroke(BLUE_E, width=6, opacity=0.22)
            .set_fill(BLUE_E, opacity=0.10)
            .move_to(pulse)
        )

        self.add(
            VGroup(source, transform_box, output),
            VGroup(source_label, transform_label, output_label),
            path_a,
            path_b,
            pulse,
            glow,
        )
        self.play(MoveAlongPath(pulse, path_a), run_time=2.1, rate_func=linear)
        self.play(MoveAlongPath(pulse, path_b), run_time=2.1, rate_func=linear)
        self.wait(0.15)
