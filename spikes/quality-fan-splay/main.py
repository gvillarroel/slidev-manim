#!/usr/bin/env -S uv run --script
# /// script
# dependencies = [
#   "manim>=0.20.0",
# ]
# ///

from __future__ import annotations

import argparse
import math
import shutil
import subprocess
import sys
from pathlib import Path

from manim import (
    DOWN,
    LEFT,
    RIGHT,
    UP,
    AnimationGroup,
    Circle,
    FadeIn,
    FadeOut,
    Line,
    MoveAlongPath,
    RoundedRectangle,
    Scene,
    Transform,
    VGroup,
    WHITE,
    smooth,
    there_and_back,
)

SPIKE_DIR = Path(__file__).resolve().parent
REPO_ROOT = SPIKE_DIR.parent.parent
SPIKE_NAME = SPIKE_DIR.name
OUTPUT_DIR = REPO_ROOT / "videos" / SPIKE_NAME
STAGING_DIR = OUTPUT_DIR / ".manim"

PRIMARY_RED = "#9E1B32"
PRIMARY_ORANGE = "#E77204"
PRIMARY_YELLOW = "#F1C319"
PRIMARY_GREEN = "#45842A"
PRIMARY_BLUE = "#007298"
PRIMARY_PURPLE = "#652F6C"
GRAY_100 = "#E7E7E7"
GRAY_200 = "#CFCFCF"


class _Args(argparse.Namespace):
    quality: str


def parse_args() -> _Args:
    parser = argparse.ArgumentParser(description="Render the quality-fan-splay spike.")
    parser.add_argument("--quality", choices=("low", "medium", "high", "production", "4k"), default="medium")
    return parser.parse_args(namespace=_Args())


def quality_flag(quality: str) -> str:
    return {"low": "-ql", "medium": "-qm", "high": "-qh", "production": "-qp", "4k": "-qk"}[quality]


def output_paths() -> tuple[Path, Path]:
    return OUTPUT_DIR / f"{SPIKE_NAME}.webm", OUTPUT_DIR / f"{SPIKE_NAME}.png"


def render_command(args: _Args, stem: str, poster: bool) -> list[str]:
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
        stem,
        "--media_dir",
        str(STAGING_DIR),
        str(Path(__file__).resolve()),
        "QualityFanSplayScene",
    ]
    if poster:
        command.insert(-2, "-s")
    return command


def promote(target_name: str, destination: Path) -> None:
    matches = sorted(STAGING_DIR.glob(f"**/{target_name}"))
    if not matches:
        raise FileNotFoundError(target_name)
    destination.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(matches[-1], destination)


def slab(color: str, width: float, height: float) -> RoundedRectangle:
    return RoundedRectangle(width=width, height=height, corner_radius=0.3, stroke_width=0, fill_color=color, fill_opacity=1)


class QualityFanSplayScene(Scene):
    def construct(self) -> None:
        self.camera.background_color = WHITE

        frame = RoundedRectangle(width=12.9, height=5.8, corner_radius=0.34, stroke_color=GRAY_200, stroke_width=2, fill_color=WHITE, fill_opacity=0)
        source_zone = RoundedRectangle(width=4.1, height=4.2, corner_radius=0.35, stroke_width=0, fill_color=GRAY_100, fill_opacity=0.23).move_to(LEFT * 3.0)
        target_zone = RoundedRectangle(width=4.2, height=4.25, corner_radius=0.35, stroke_width=0, fill_color=GRAY_100, fill_opacity=0.28).move_to(RIGHT * 2.9)

        source = VGroup(
            slab(PRIMARY_GREEN, 2.5, 0.9).move_to(LEFT * 3.35 + UP * 0.7),
            slab(PRIMARY_BLUE, 1.9, 0.82).move_to(LEFT * 2.2 + DOWN * 0.1),
            slab(PRIMARY_PURPLE, 1.45, 0.7).move_to(LEFT * 1.6 + DOWN * 1.05),
        )

        funnel = Line(LEFT * 0.95 + DOWN * 0.02, RIGHT * 1.28 + DOWN * 0.02, color=PRIMARY_ORANGE, stroke_width=6)
        accent = Circle(radius=0.12, stroke_width=0, fill_color=PRIMARY_YELLOW, fill_opacity=1).move_to(funnel.get_start())

        narrow_green = slab(PRIMARY_GREEN, 1.95, 0.76).move_to(RIGHT * 1.12 + UP * 0.12)
        narrow_blue = slab(PRIMARY_BLUE, 1.54, 0.7).move_to(RIGHT * 1.32 + DOWN * 0.34)
        narrow_purple = slab(PRIMARY_PURPLE, 1.16, 0.6).move_to(RIGHT * 1.54 + DOWN * 0.84)

        final_green = slab(PRIMARY_GREEN, 2.18, 0.8).move_to(RIGHT * 2.54 + UP * 0.92).rotate(-math.pi / 16)
        final_blue = slab(PRIMARY_BLUE, 1.76, 0.72).move_to(RIGHT * 3.36 + UP * 0.08).rotate(math.pi / 28)
        final_purple = slab(PRIMARY_PURPLE, 1.28, 0.58).move_to(RIGHT * 4.02 + DOWN * 0.82).rotate(math.pi / 9)

        self.add(frame, source_zone, target_zone)
        self.play(FadeIn(source, lag_ratio=0.08), run_time=0.7)
        self.play(FadeIn(funnel), run_time=0.14)
        self.play(MoveAlongPath(accent, funnel), run_time=0.34)
        self.play(
            AnimationGroup(
                source[0].animate.move_to(narrow_green.get_center()),
                source[1].animate.move_to(narrow_blue.get_center()),
                source[2].animate.move_to(narrow_purple.get_center()),
                lag_ratio=0.06,
            ),
            run_time=0.56,
            rate_func=smooth,
        )
        self.play(
            AnimationGroup(
                Transform(source[0], final_green.copy()),
                Transform(source[1], final_blue.copy()),
                Transform(source[2], final_purple.copy()),
                lag_ratio=0.05,
            ),
            run_time=0.72,
            rate_func=smooth,
        )
        self.play(FadeOut(funnel), run_time=0.12)
        self.play(accent.animate.move_to(RIGHT * 3.22 + DOWN * 0.08).set_fill(PRIMARY_RED, opacity=1), run_time=0.16)
        for item in source:
            self.play(item.animate.scale(1.05), run_time=0.12, rate_func=there_and_back)
        self.play(FadeOut(accent), run_time=0.14)
        self.wait(0.25)


def render_variant(args: _Args) -> None:
    video_path, poster_path = output_paths()
    result = subprocess.run(render_command(args, video_path.stem, poster=False), check=False)
    if result.returncode != 0:
        raise SystemExit(result.returncode)
    promote(video_path.name, video_path)
    result = subprocess.run(render_command(args, poster_path.stem, poster=True), check=False)
    if result.returncode != 0:
        raise SystemExit(result.returncode)
    promote(poster_path.name, poster_path)


def main() -> int:
    args = parse_args()
    render_variant(args)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
