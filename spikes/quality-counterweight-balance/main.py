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
    RIGHT,
    UP,
    AnimationGroup,
    Circle,
    FadeIn,
    FadeOut,
    Line,
    Rectangle,
    Scene,
    Transform,
    VGroup,
    WHITE,
    config,
    smooth,
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
GRAY_300 = "#adadad"

config.transparent = True
config.background_opacity = 0.0


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
        "--transparent",
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
    matches = sorted(STAGING_DIR.glob(f"**/{target_name}"), key=lambda path: path.stat().st_mtime)
    if not matches:
        raise FileNotFoundError(target_name)
    destination.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(matches[-1], destination)


def slab(color: str, width: float, height: float) -> Rectangle:
    return Rectangle(width=width, height=height, stroke_width=0, fill_color=color, fill_opacity=1)


def dot(color: str, radius: float) -> Circle:
    return Circle(radius=radius, stroke_width=0, fill_color=color, fill_opacity=1)


def guide_slot(center, width: float, height: float, color: str = GRAY_300) -> VGroup:
    left = Line(UP * height / 2, DOWN * height / 2, color=color, stroke_width=3).move_to(center + LEFT * width / 2)
    right = Line(UP * height / 2, DOWN * height / 2, color=color, stroke_width=3).move_to(center + RIGHT * width / 2)
    return VGroup(left, right).set_opacity(0.28)


def corner_brackets(center, width: float, height: float, color: str = PRIMARY_RED) -> VGroup:
    stroke = 5
    length = 0.34
    gap = 0.11
    left = center + LEFT * width / 2
    right = center + RIGHT * width / 2
    top = center + UP * height / 2
    bottom = center + DOWN * height / 2
    return VGroup(
        Line(left + UP * (height / 2 - length), left + UP * (height / 2 - gap), color=color, stroke_width=stroke),
        Line(left + DOWN * (height / 2 - length), left + DOWN * (height / 2 - gap), color=color, stroke_width=stroke),
        Line(right + UP * (height / 2 - length), right + UP * (height / 2 - gap), color=color, stroke_width=stroke),
        Line(right + DOWN * (height / 2 - length), right + DOWN * (height / 2 - gap), color=color, stroke_width=stroke),
        Line(top + LEFT * (width / 2 - length), top + LEFT * (width / 2 - gap), color=color, stroke_width=stroke),
        Line(top + RIGHT * (width / 2 - length), top + RIGHT * (width / 2 - gap), color=color, stroke_width=stroke),
        Line(bottom + LEFT * (width / 2 - length), bottom + LEFT * (width / 2 - gap), color=color, stroke_width=stroke),
        Line(bottom + RIGHT * (width / 2 - length), bottom + RIGHT * (width / 2 - gap), color=color, stroke_width=stroke),
    )


class QualityCounterweightBalanceScene(Scene):
    def construct(self) -> None:
        self.camera.background_color = WHITE
        self.camera.background_opacity = 0.0

        beam = Line(LEFT * 2.35 + DOWN * 0.1, RIGHT * 2.35 + DOWN * 0.1, color=PRIMARY_ORANGE, stroke_width=7)
        pivot = dot(PRIMARY_YELLOW, 0.18).move_to(DOWN * 0.1)
        beam_tilt = Line(LEFT * 2.35 + UP * 0.72, RIGHT * 2.35 + DOWN * 0.92, color=PRIMARY_ORANGE, stroke_width=7)
        pivot_tilt = dot(PRIMARY_YELLOW, 0.18).move_to(DOWN * 0.1)

        source_green = slab(PRIMARY_GREEN, 1.78, 0.58).move_to(LEFT * 4.08 + UP * 0.82)
        source_blue = slab(PRIMARY_BLUE, 1.38, 0.5).move_to(LEFT * 3.72 + DOWN * 0.05)
        source_purple = dot(PRIMARY_PURPLE, 0.42).move_to(LEFT * 4.38 + DOWN * 0.92)
        source = VGroup(source_green, source_blue, source_purple)

        left_pan_slot = guide_slot(LEFT * 1.55 + UP * 0.72, 2.05, 0.76)
        right_pan_slot = guide_slot(RIGHT * 1.55 + DOWN * 1.16, 1.86, 0.72)
        upper_counter_slot = guide_slot(RIGHT * 3.45 + UP * 1.18, 1.36, 0.56)
        lower_counter_slot = guide_slot(RIGHT * 3.25 + DOWN * 1.48, 1.54, 0.62)
        slots = VGroup(left_pan_slot, right_pan_slot, upper_counter_slot, lower_counter_slot)

        green_on_pan = slab(PRIMARY_GREEN, 1.64, 0.48).move_to(LEFT * 1.56 + UP * 0.48)
        blue_on_pan = slab(PRIMARY_BLUE, 1.26, 0.42).move_to(LEFT * 1.2 + UP * 1.04)
        purple_counter = dot(PRIMARY_PURPLE, 0.36).move_to(RIGHT * 1.48 + DOWN * 0.92)

        red_counter = dot(PRIMARY_RED, 0.34).move_to(RIGHT * 3.4 + UP * 1.18)
        red_drop = dot(PRIMARY_RED, 0.34).move_to(RIGHT * 3.24 + DOWN * 1.48)
        purple_lift = dot(PRIMARY_PURPLE, 0.45).move_to(RIGHT * 3.34 + UP * 0.78)
        green_lift = slab(PRIMARY_GREEN, 1.64, 0.48).move_to(LEFT * 1.48 + UP * 1.2)
        blue_lift = slab(PRIMARY_BLUE, 1.26, 0.42).move_to(LEFT * 1.08 + UP * 1.74)

        final_green = dot(PRIMARY_GREEN, 0.78).move_to(LEFT * 0.68 + UP * 0.54)
        final_blue = dot(PRIMARY_BLUE, 0.48).move_to(RIGHT * 0.7 + UP * 0.32)
        final_purple = slab(PRIMARY_PURPLE, 1.28, 0.42).move_to(LEFT * 0.08 + DOWN * 0.72)
        final_red = slab(PRIMARY_RED, 1.02, 0.34).move_to(RIGHT * 1.1 + DOWN * 0.98)
        terminal = corner_brackets(RIGHT * 0.16 + DOWN * 0.2, 3.55, 2.65)

        self.add(beam, pivot, slots, source, red_counter)
        self.wait(2.7)
        self.play(
            AnimationGroup(
                Transform(source_green, green_on_pan.copy(), path_arc=-0.28),
                Transform(source_blue, blue_on_pan.copy(), path_arc=0.34),
                Transform(source_purple, purple_counter.copy(), path_arc=0.42),
                lag_ratio=0.12,
            ),
            run_time=4.1,
            rate_func=smooth,
        )
        self.wait(1.8)
        self.play(
            AnimationGroup(
                Transform(beam, beam_tilt.copy()),
                Transform(pivot, pivot_tilt.copy()),
                Transform(source_green, green_lift.copy()),
                Transform(source_blue, blue_lift.copy()),
                Transform(source_purple, purple_lift.copy()),
                Transform(red_counter, red_drop.copy()),
                lag_ratio=0.03,
            ),
            run_time=4.0,
            rate_func=smooth,
        )
        self.wait(2.2)
        self.play(FadeOut(slots), run_time=1.15)
        self.play(FadeOut(beam), FadeOut(pivot), run_time=0.75)
        self.play(
            AnimationGroup(
                Transform(source_green, final_green.copy()),
                Transform(source_blue, final_blue.copy()),
                Transform(source_purple, final_purple.copy()),
                Transform(red_counter, final_red.copy()),
                lag_ratio=0.08,
            ),
            run_time=3.05,
            rate_func=smooth,
        )
        self.play(FadeIn(terminal), run_time=1.15)
        self.wait(6.0)


def render_variant(args: _Args) -> None:
    video_path, poster_path = output_paths()
    if STAGING_DIR.exists():
        shutil.rmtree(STAGING_DIR)
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
