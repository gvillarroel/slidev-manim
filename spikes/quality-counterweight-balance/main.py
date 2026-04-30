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

from manim import (
    DOWN,
    LEFT,
    ORIGIN,
    RIGHT,
    UP,
    AnimationGroup,
    Circle,
    FadeIn,
    FadeOut,
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
    parser = argparse.ArgumentParser(description="Render the quality-counterweight-balance spike.")
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
        "QualityCounterweightBalanceScene",
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


def dot(color: str, radius: float) -> Circle:
    return Circle(radius=radius, stroke_width=0, fill_color=color, fill_opacity=1)


class QualityCounterweightBalanceScene(Scene):
    def construct(self) -> None:
        self.camera.background_color = WHITE

        frame = RoundedRectangle(width=12.9, height=5.8, corner_radius=0.34, stroke_color=GRAY_200, stroke_width=2, fill_color=WHITE, fill_opacity=0)
        soft_left = RoundedRectangle(width=3.7, height=4.2, corner_radius=0.34, stroke_width=0, fill_color=GRAY_100, fill_opacity=0.38).move_to(LEFT * 3.2)
        soft_right = RoundedRectangle(width=3.7, height=4.2, corner_radius=0.34, stroke_width=0, fill_color=GRAY_100, fill_opacity=0.38).move_to(RIGHT * 3.0)

        left_group = VGroup(
            slab(PRIMARY_GREEN, 2.1, 1.0).move_to(LEFT * 4.05 + UP * 0.8),
            slab(PRIMARY_BLUE, 2.1, 1.0).move_to(LEFT * 3.15 + DOWN * 0.45),
        )
        right_group = VGroup(
            dot(PRIMARY_PURPLE, 0.62).move_to(RIGHT * 2.4 + UP * 0.55),
            dot(PRIMARY_RED, 0.42).move_to(RIGHT * 3.6 + DOWN * 0.8),
        )
        left_targets = VGroup(
            dot(PRIMARY_GREEN, 0.62).move_to(LEFT * 1.0 + UP * 0.55),
            dot(PRIMARY_BLUE, 0.5).move_to(LEFT * 2.0 + DOWN * 0.75),
        )
        right_targets = VGroup(
            slab(PRIMARY_PURPLE, 2.0, 0.94).move_to(RIGHT * 2.2 + UP * 0.9),
            slab(PRIMARY_RED, 1.75, 0.82).move_to(RIGHT * 3.0 + DOWN * 0.45),
        )
        accent = Circle(radius=0.14, stroke_width=0, fill_color=PRIMARY_YELLOW, fill_opacity=1).move_to(ORIGIN + DOWN * 0.1)

        self.add(frame, soft_left, soft_right)
        self.play(FadeIn(left_group, shift=UP * 0.12), FadeIn(right_group, shift=DOWN * 0.12), run_time=0.7)
        self.play(accent.animate.shift(LEFT * 1.6), run_time=0.2)
        self.play(
            AnimationGroup(
                Transform(left_group[0], left_targets[0]),
                Transform(left_group[1], left_targets[1]),
                right_group.animate.shift(RIGHT * 0.85 + UP * 0.2),
                lag_ratio=0.06,
            ),
            run_time=0.9,
            rate_func=smooth,
        )
        self.play(accent.animate.shift(RIGHT * 3.25), run_time=0.2)
        self.play(
            AnimationGroup(
                Transform(right_group[0], right_targets[0]),
                Transform(right_group[1], right_targets[1]),
                left_group.animate.shift(LEFT * 0.6 + DOWN * 0.1),
                lag_ratio=0.06,
            ),
            run_time=0.9,
            rate_func=smooth,
        )
        self.play(soft_left.animate.shift(RIGHT * 1.0), soft_right.animate.shift(LEFT * 0.7), run_time=0.35)
        for item in VGroup(*left_group, *right_group):
            self.play(item.animate.scale(1.06), run_time=0.14, rate_func=there_and_back)
        self.play(accent.animate.move_to(RIGHT * 0.75 + DOWN * 0.1).set_fill(PRIMARY_ORANGE, opacity=1), run_time=0.18)
        self.play(FadeOut(accent), run_time=0.16)
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
