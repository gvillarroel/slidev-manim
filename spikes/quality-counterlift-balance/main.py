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

PRIMARY_RED = "#9e1b32"
PRIMARY_ORANGE = "#e77204"
PRIMARY_YELLOW = "#f1c319"
PRIMARY_GREEN = "#45842a"
PRIMARY_BLUE = "#007298"
PRIMARY_PURPLE = "#652f6c"
GRAY_100 = "#e7e7e7"
GRAY_200 = "#cfcfcf"


class _Args(argparse.Namespace):
    quality: str


def parse_args() -> _Args:
    parser = argparse.ArgumentParser(description="Render the quality-counterlift-balance spike.")
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
        "-o", stem, "--media_dir", str(STAGING_DIR), str(Path(__file__).resolve()), "QualityCounterliftBalanceScene",
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


class QualityCounterliftBalanceScene(Scene):
    def construct(self) -> None:
        self.camera.background_color = WHITE
        frame = RoundedRectangle(width=12.9, height=5.8, corner_radius=0.34, stroke_color=GRAY_200, stroke_width=2, fill_color=WHITE, fill_opacity=0)
        source_zone = RoundedRectangle(width=4.0, height=4.1, corner_radius=0.35, stroke_width=0, fill_color=GRAY_100, fill_opacity=0.22).move_to(LEFT * 3.08)
        target_zone = RoundedRectangle(width=4.2, height=4.1, corner_radius=0.35, stroke_width=0, fill_color=GRAY_100, fill_opacity=0.28).move_to(RIGHT * 2.96)

        green = slab(PRIMARY_GREEN, 2.66, 0.92).move_to(LEFT * 3.24 + UP * 0.76)
        blue = slab(PRIMARY_BLUE, 1.86, 0.82).move_to(LEFT * 2.08 + DOWN * 0.02)
        purple = slab(PRIMARY_PURPLE, 1.3, 0.62).move_to(LEFT * 1.54 + DOWN * 0.98)
        source = VGroup(green, blue, purple)

        balance = Line(RIGHT * 1.04 + DOWN * 0.2, RIGHT * 2.86 + DOWN * 0.2, color=PRIMARY_ORANGE, stroke_width=6)
        tilted_balance = Line(RIGHT * 1.06 + UP * 0.42, RIGHT * 2.92 + DOWN * 0.52, color=PRIMARY_ORANGE, stroke_width=6)
        pivot = Circle(radius=0.16, stroke_width=0, fill_color=PRIMARY_YELLOW, fill_opacity=1).move_to(RIGHT * 1.96 + DOWN * 0.04)
        pivot_hold = Circle(radius=0.16, stroke_width=0, fill_color=PRIMARY_YELLOW, fill_opacity=1).move_to(RIGHT * 1.98 + DOWN * 0.06)

        green_lift = slab(PRIMARY_GREEN, 1.44, 0.42).move_to(RIGHT * 1.4 + UP * 0.66)
        blue_drop = slab(PRIMARY_BLUE, 1.16, 0.46).move_to(RIGHT * 2.74 + DOWN * 0.9)
        purple_counter = slab(PRIMARY_PURPLE, 0.88, 0.36).move_to(RIGHT * 2.4 + DOWN * 0.08)

        final_green = Circle(radius=0.86, stroke_width=0, fill_color=PRIMARY_GREEN, fill_opacity=1).move_to(RIGHT * 2.3 + UP * 0.46)
        final_blue = Circle(radius=0.48, stroke_width=0, fill_color=PRIMARY_BLUE, fill_opacity=1).move_to(RIGHT * 3.56 + DOWN * 0.18)
        final_purple = Circle(radius=0.28, stroke_width=0, fill_color=PRIMARY_PURPLE, fill_opacity=1).move_to(RIGHT * 2.72 + DOWN * 1.04)

        self.add(frame, source_zone, target_zone)
        self.play(FadeIn(source, lag_ratio=0.08), run_time=0.68)
        self.play(FadeIn(balance), FadeIn(pivot), run_time=0.18)
        self.play(
            AnimationGroup(
                Transform(balance, tilted_balance.copy()),
                Transform(pivot, pivot_hold.copy()),
                Transform(green, green_lift.copy()),
                Transform(blue, blue_drop.copy()),
                Transform(purple, purple_counter.copy()),
                lag_ratio=0.04,
            ),
            run_time=0.5,
            rate_func=smooth,
        )
        self.play(
            AnimationGroup(Transform(green, final_green.copy()), Transform(blue, final_blue.copy()), Transform(purple, final_purple.copy()), lag_ratio=0.08),
            run_time=0.58,
            rate_func=smooth,
        )
        self.play(FadeOut(balance), FadeOut(pivot), run_time=0.18)
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
