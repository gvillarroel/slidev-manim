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
            self.camera.background_color = PAGE_BACKGROUND

        stage = RoundedRectangle(
            width=12.8,
            height=4.35,
            corner_radius=0.3,
            stroke_width=0,
            fill_color=PAGE_BACKGROUND,
            fill_opacity=0.96,
        )

        source = RoundedRectangle(width=2.4, height=1.0, corner_radius=0.18)
        source.set_stroke(PRIMARY_GREEN, width=6, opacity=0.82)
        source.set_fill(HIGHLIGHT_GREEN, opacity=0.92)
        source.shift(LEFT * 4.0)

        transform_box = RoundedRectangle(width=2.6, height=1.0, corner_radius=0.18)
        transform_box.set_stroke(PRIMARY_BLUE, width=6, opacity=0.82)
        transform_box.set_fill(HIGHLIGHT_BLUE, opacity=0.92)

        output = RoundedRectangle(width=2.4, height=1.0, corner_radius=0.18)
        output.set_stroke(PRIMARY_PURPLE, width=6, opacity=0.82)
        output.set_fill(HIGHLIGHT_PURPLE, opacity=0.92)
        output.shift(RIGHT * 4.0)

        source_label = Text("Source", font_size=30, color=GRAY).move_to(source)
        transform_label = Text("Transform", font_size=28, color=GRAY).move_to(transform_box)
        output_label = Text("Output", font_size=30, color=GRAY).move_to(output)

        path_a = Line(source.get_right(), transform_box.get_left(), color=PRIMARY_ORANGE, stroke_width=8)
        path_a.set_stroke(opacity=0.62)
        path_b = Line(transform_box.get_right(), output.get_left(), color=PRIMARY_ORANGE, stroke_width=8)
        path_b.set_stroke(opacity=0.62)

        pulse = Dot(color=PRIMARY_YELLOW, radius=0.16).move_to(path_a.get_start())
        glow = always_redraw(
            lambda: RoundedRectangle(width=0.55, height=0.55, corner_radius=0.28)
            .set_stroke(PRIMARY_YELLOW, width=6, opacity=0.32)
            .set_fill(PRIMARY_YELLOW, opacity=0.12)
            .move_to(pulse)
        )

        self.add(
            stage,
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
