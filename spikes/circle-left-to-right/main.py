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
LEGACY_VIDEO = OUTPUT_DIR / f"{SPIKE_NAME}.webm"

VARIANTS = {
    "full": {
        "scene": "CircleLeftToRightFullScene",
        "resolution": "1920,1080",
        "output": OUTPUT_DIR / "circle-left-to-right-full.webm",
        "mp4": OUTPUT_DIR / "circle-left-to-right-full.mp4",
        "poster": OUTPUT_DIR / "circle-left-to-right-full.png",
    },
    "content": {
        "scene": "CircleLeftToRightContentScene",
        "resolution": "1600,900",
        "output": OUTPUT_DIR / "circle-left-to-right-content.webm",
        "mp4": OUTPUT_DIR / "circle-left-to-right-content.mp4",
        "poster": OUTPUT_DIR / "circle-left-to-right-content.png",
    },
}


class _Args(argparse.Namespace):
    quality: str
    preview: bool


def parse_args() -> _Args:
    parser = argparse.ArgumentParser(
        description="Render the circle-left-to-right Manim spike."
    )
    parser.add_argument(
        "--quality",
        choices=("low", "medium", "high", "production", "4k"),
        default="medium",
        help="Manim quality preset. Defaults to medium for presentation review.",
    )
    parser.add_argument(
        "--preview",
        action="store_true",
        help="Open the rendered output after rendering.",
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


def build_command(args: _Args, variant_name: str) -> list[str]:
    STAGING_DIR.mkdir(parents=True, exist_ok=True)
    variant = VARIANTS[variant_name]

    command = [
        sys.executable,
        "-m",
        "manim",
        "render",
        quality_flag(args.quality),
        "--format",
        "webm",
        "-t",
        "-r",
        variant["resolution"],
        "-o",
        Path(variant["output"]).stem,
        "--media_dir",
        str(STAGING_DIR),
    ]

    if args.preview:
        command.append("-p")

    command.extend([str(Path(__file__).resolve()), variant["scene"]])
    return command


def build_mp4_command(args: _Args, variant_name: str) -> list[str]:
    STAGING_DIR.mkdir(parents=True, exist_ok=True)
    variant = VARIANTS[variant_name]

    command = [
        sys.executable,
        "-m",
        "manim",
        "render",
        quality_flag(args.quality),
        "--format",
        "mp4",
        "-r",
        variant["resolution"],
        "-o",
        Path(variant["mp4"]).stem,
        "--media_dir",
        str(STAGING_DIR),
    ]

    if args.preview:
        command.append("-p")

    command.extend([str(Path(__file__).resolve()), variant["scene"]])
    return command


def build_poster_command(args: _Args, variant_name: str) -> list[str]:
    variant = VARIANTS[variant_name]
    return [
        sys.executable,
        "-m",
        "manim",
        "render",
        quality_flag(args.quality),
        "-s",
        "-r",
        variant["resolution"],
        "-o",
        Path(variant["poster"]).stem,
        "--media_dir",
        str(STAGING_DIR),
        str(Path(__file__).resolve()),
        variant["scene"],
    ]


def promote_rendered_file(target_name: str, destination: Path) -> None:
    matches = sorted(STAGING_DIR.glob(f"**/{target_name}"))
    if not matches:
        raise FileNotFoundError(f"Could not find {target_name} under {STAGING_DIR}")

    source = matches[-1]
    destination.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(source, destination)


def promote_rendered_video(variant_name: str) -> None:
    variant = VARIANTS[variant_name]
    promote_rendered_file(Path(variant["output"]).name, variant["output"])


def promote_mp4(variant_name: str) -> None:
    variant = VARIANTS[variant_name]
    promote_rendered_file(Path(variant["mp4"]).name, variant["mp4"])


def promote_poster(variant_name: str) -> None:
    variant = VARIANTS[variant_name]
    promote_rendered_file(Path(variant["poster"]).name, variant["poster"])


def main() -> int:
    args = parse_args()
    for variant_name, variant in VARIANTS.items():
        command = build_command(args, variant_name)
        print(f"Rendering {variant['scene']} into {variant['output']}")
        video_env = os.environ.copy()
        video_env["SPIKE_RENDER_TARGET"] = "video"
        result = subprocess.run(command, check=False, env=video_env)
        if result.returncode != 0:
            return result.returncode
        promote_rendered_video(variant_name)

        mp4_env = os.environ.copy()
        mp4_env["SPIKE_RENDER_TARGET"] = "mp4"
        mp4_result = subprocess.run(
            build_mp4_command(args, variant_name),
            check=False,
            env=mp4_env,
        )
        if mp4_result.returncode != 0:
            return mp4_result.returncode
        promote_mp4(variant_name)

        poster_env = os.environ.copy()
        poster_env["SPIKE_RENDER_TARGET"] = "poster"
        poster_result = subprocess.run(
            build_poster_command(args, variant_name),
            check=False,
            env=poster_env,
        )
        if poster_result.returncode != 0:
            return poster_result.returncode
        promote_poster(variant_name)

    shutil.copy2(VARIANTS["full"]["output"], LEGACY_VIDEO)
    shutil.copy2(VARIANTS["full"]["mp4"], OUTPUT_DIR / f"{SPIKE_NAME}.mp4")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())


from manim import Dot, LEFT, Line, RIGHT, VGroup, WHITE, Circle, Scene, linear


class BaseCircleLeftToRightScene(Scene):
    radius = 1.0
    start_x = -5.0
    end_x = 5.0
    run_time = 2.8

    def construct(self) -> None:
        if os.environ.get("SPIKE_RENDER_TARGET") in {"mp4", "poster"}:
            self.camera.background_color = PAGE_BACKGROUND

        start = LEFT * abs(self.start_x)
        end = RIGHT * abs(self.end_x)
        guide = Line(start, end, color=PRIMARY_ORANGE, stroke_width=7)
        guide.set_stroke(opacity=0.34)

        circle = Circle(radius=self.radius, color=PRIMARY_GREEN, stroke_width=10)
        circle.set_fill(PRIMARY_GREEN, opacity=0.94)
        core = Dot(color=PRIMARY_YELLOW, radius=self.radius * 0.12)
        leader = VGroup(circle, core).move_to(start)

        self.add(guide, leader)
        self.play(
            leader.animate.move_to(end),
            run_time=self.run_time,
            rate_func=linear,
        )
        self.wait(0.15)


class CircleLeftToRightFullScene(BaseCircleLeftToRightScene):
    radius = 1.2
    start_x = -5.8
    end_x = 5.8
    run_time = 3.0


class CircleLeftToRightContentScene(BaseCircleLeftToRightScene):
    radius = 1.35
    start_x = -4.6
    end_x = 4.6
    run_time = 2.8
