#!/usr/bin/env -S uv run --script
# /// script
# dependencies = [
#   "manim>=0.20.0",
# ]
# ///

from __future__ import annotations

import argparse
import shutil
import subprocess
import sys
from pathlib import Path

from manim import DOWN, LEFT, RIGHT, UP, AnimationGroup, Circle, FadeIn, FadeOut, Line, RoundedRectangle, Scene, Transform, VGroup, WHITE, smooth

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
    parser = argparse.ArgumentParser(description="Render the quality-fork-diverge spike.")
    parser.add_argument("--quality", choices=("low", "medium", "high", "production", "4k"), default="medium")
    return parser.parse_args(namespace=_Args())


def quality_flag(quality: str) -> str:
    return {"low": "-ql", "medium": "-qm", "high": "-qh", "production": "-qp", "4k": "-qk"}[quality]


def output_paths() -> tuple[Path, Path]:
    return OUTPUT_DIR / f"{SPIKE_NAME}.webm", OUTPUT_DIR / f"{SPIKE_NAME}.png"


def render_command(args: _Args, stem: str, poster: bool) -> list[str]:
    STAGING_DIR.mkdir(parents=True, exist_ok=True)
    command = [
        sys.executable, "-m", "manim", "render", quality_flag(args.quality), "-r", "1600,900", "--format", "webm",
        "-o", stem, "--media_dir", str(STAGING_DIR), str(Path(__file__).resolve()), "QualityForkDivergeScene",
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


class QualityForkDivergeScene(Scene):
    def construct(self) -> None:
        self.camera.background_color = WHITE
        frame = RoundedRectangle(width=12.9, height=5.8, corner_radius=0.34, stroke_color=GRAY_200, stroke_width=2, fill_color=WHITE, fill_opacity=0)
        source_zone = RoundedRectangle(width=4.0, height=4.1, corner_radius=0.35, stroke_width=0, fill_color=GRAY_100, fill_opacity=0.22).move_to(LEFT * 3.08)
        target_zone = RoundedRectangle(width=4.2, height=4.1, corner_radius=0.35, stroke_width=0, fill_color=GRAY_100, fill_opacity=0.28).move_to(RIGHT * 2.96)

        green = slab(PRIMARY_GREEN, 2.68, 0.92).move_to(LEFT * 3.16 + UP * 0.76)
        blue = slab(PRIMARY_BLUE, 1.72, 0.76).move_to(LEFT * 2.24 + DOWN * 0.02)
        purple = slab(PRIMARY_PURPLE, 1.18, 0.58).move_to(LEFT * 1.66 + DOWN * 0.98)
        source = VGroup(green, blue, purple)

        fork_trunk = Line(RIGHT * 0.94 + DOWN * 0.1, RIGHT * 2.04 + DOWN * 0.1, color=PRIMARY_ORANGE, stroke_width=7)
        fork_top = Line(RIGHT * 2.04 + DOWN * 0.1, RIGHT * 2.88 + UP * 0.92, color=PRIMARY_ORANGE, stroke_width=7)
        fork_bottom = Line(RIGHT * 2.04 + DOWN * 0.1, RIGHT * 2.9 + DOWN * 1.04, color=PRIMARY_ORANGE, stroke_width=7)
        fork = VGroup(fork_trunk, fork_top, fork_bottom)
        accent = Circle(radius=0.13, stroke_width=0, fill_color=PRIMARY_YELLOW, fill_opacity=1).move_to(RIGHT * 1.08 + DOWN * 0.1)

        green_mid = slab(PRIMARY_GREEN, 1.64, 0.36).move_to(RIGHT * 1.56 + DOWN * 0.1)
        blue_mid = slab(PRIMARY_BLUE, 0.96, 0.4).move_to(RIGHT * 2.82 + UP * 0.92)
        purple_mid = slab(PRIMARY_PURPLE, 0.9, 0.36).move_to(RIGHT * 2.86 + DOWN * 1.02)

        final_green = Circle(radius=0.72, stroke_width=0, fill_color=PRIMARY_GREEN, fill_opacity=1).move_to(RIGHT * 2.34 + UP * 0.88)
        final_blue = Circle(radius=0.46, stroke_width=0, fill_color=PRIMARY_BLUE, fill_opacity=1).move_to(RIGHT * 3.72 + UP * 0.02)
        final_purple = Circle(radius=0.34, stroke_width=0, fill_color=PRIMARY_PURPLE, fill_opacity=1).move_to(RIGHT * 2.84 + DOWN * 1.06)

        self.add(frame, source_zone, target_zone)
        self.play(FadeIn(source, lag_ratio=0.08), run_time=0.68)
        self.play(FadeIn(fork), run_time=0.2)
        self.play(accent.animate.move_to(RIGHT * 1.84 + DOWN * 0.1), run_time=0.16, rate_func=smooth)
        self.play(Transform(green, green_mid.copy()), run_time=0.28, rate_func=smooth)
        self.play(
            AnimationGroup(
                Transform(blue, blue_mid.copy()),
                Transform(purple, purple_mid.copy()),
                lag_ratio=0.08,
            ),
            run_time=0.28,
            rate_func=smooth,
        )
        self.play(accent.animate.move_to(RIGHT * 2.34 + UP * 0.42), run_time=0.14, rate_func=smooth)
        self.play(
            AnimationGroup(
                Transform(green, final_green.copy()),
                Transform(blue, final_blue.copy()),
                Transform(purple, final_purple.copy()),
                lag_ratio=0.08,
            ),
            run_time=0.6,
            rate_func=smooth,
        )
        self.play(accent.animate.move_to(RIGHT * 2.92 + UP * 0.44).set_fill(PRIMARY_RED, opacity=1), run_time=0.14)
        self.play(FadeOut(fork), FadeOut(accent), run_time=0.18)
        self.wait(0.28)


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
