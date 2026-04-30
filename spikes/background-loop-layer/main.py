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
OUTPUT_VIDEO = OUTPUT_DIR / "background-loop-layer.webm"
OUTPUT_POSTER = OUTPUT_DIR / "background-loop-layer.png"


class _Args(argparse.Namespace):
    quality: str
    preview: bool


def parse_args() -> _Args:
    parser = argparse.ArgumentParser(
        description="Render the background-loop-layer Manim spike."
    )
    parser.add_argument(
        "--quality",
        choices=("low", "medium", "high", "production", "4k"),
        default="medium",
        help="Manim quality preset. Defaults to medium for quick iteration.",
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
    command.extend([str(Path(__file__).resolve()), "BackgroundLoopLayerScene"])
    return command


def promote_rendered_file(target_name: str, destination: Path) -> None:
    matches = sorted(STAGING_DIR.glob(f"**/{target_name}"))
    if not matches:
        raise FileNotFoundError(f"Could not find {target_name} under {STAGING_DIR}")

    destination.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(matches[-1], destination)


def main() -> int:
    args = parse_args()

    video_result = subprocess.run(
        build_command(args, poster=False),
        check=False,
        env={**os.environ, "SPIKE_RENDER_TARGET": "video"},
    )
    if video_result.returncode != 0:
        return video_result.returncode
    promote_rendered_file(OUTPUT_VIDEO.name, OUTPUT_VIDEO)

    poster_result = subprocess.run(
        build_command(args, poster=True),
        check=False,
        env={**os.environ, "SPIKE_RENDER_TARGET": "poster"},
    )
    if poster_result.returncode != 0:
        return poster_result.returncode
    promote_rendered_file(OUTPUT_POSTER.name, OUTPUT_POSTER)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())


from manim import (
    Circle,
    DOWN,
    Ellipse,
    LEFT,
    Line,
    MoveAlongPath,
    RIGHT,
    Scene,
    UP,
    WHITE,
    linear,
)


class BackgroundLoopLayerScene(Scene):
    runtime = 7.2

    def construct(self) -> None:
        if os.environ.get("SPIKE_RENDER_TARGET") == "poster":
            self.camera.background_color = PAGE_BACKGROUND

        glow = Circle(radius=1.9, stroke_width=0, fill_color=PRIMARY_PURPLE, fill_opacity=0.08).shift(
            RIGHT * 1.35 + UP * 0.05
        )
        halo = Circle(radius=3.45, color=PRIMARY_BLUE, stroke_width=10, stroke_opacity=0.08).shift(
            LEFT * 0.7 + UP * 0.18
        )
        orbit_a = Ellipse(
            width=12.5,
            height=5.8,
            color=GRAY_300,
            stroke_width=6,
            stroke_opacity=0.11,
        ).shift(RIGHT * 0.1)
        orbit_b = Ellipse(
            width=9.2,
            height=3.7,
            color=PRIMARY_GREEN,
            stroke_width=5,
            stroke_opacity=0.12,
        ).shift(LEFT * 0.8 + DOWN * 0.08)
        orbit_c = Ellipse(
            width=6.8,
            height=2.35,
            color=PRIMARY_PURPLE,
            stroke_width=4,
            stroke_opacity=0.12,
        ).shift(RIGHT * 1.15 + DOWN * 0.75)
        horizon = Line(
            LEFT * 6.55 + DOWN * 1.28,
            RIGHT * 6.55 + DOWN * 1.28,
            color=GRAY_600,
            stroke_width=3,
            stroke_opacity=0.08,
        )

        self.add(glow, halo, orbit_a, orbit_b, orbit_c, horizon)

        moving_specs = (
            {"path": orbit_a, "radius": 0.16, "color": PRIMARY_YELLOW, "opacity": 0.92, "start": 0.05},
            {"path": orbit_a, "radius": 0.1, "color": WHITE, "opacity": 0.7, "start": 0.58},
            {"path": orbit_b, "radius": 0.12, "color": PRIMARY_ORANGE, "opacity": 0.86, "start": 0.24},
            {"path": halo, "radius": 0.085, "color": PRIMARY_GREEN, "opacity": 0.78, "start": 0.69},
        )

        moving_dots = []
        animations = []
        for spec in moving_specs:
            dot = Circle(radius=spec["radius"], stroke_width=0)
            dot.set_fill(spec["color"], opacity=spec["opacity"])
            dot.move_to(spec["path"].point_from_proportion(spec["start"]))
            moving_dots.append(dot)
            animations.append(MoveAlongPath(dot, spec["path"]))

        self.add(*moving_dots)
        self.play(*animations, run_time=self.runtime, rate_func=linear)
        self.wait(0.2)
