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
    Arc,
    Circle,
    FadeIn,
    FadeOut,
    Line,
    PI,
    Rectangle,
    Scene,
    Transform,
    VGroup,
    WHITE,
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
GRAY_300 = "#a9a9a9"


class _Args(argparse.Namespace):
    quality: str


def parse_args() -> _Args:
    parser = argparse.ArgumentParser(description="Render the quality-cradle-catch spike.")
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
        "QualityCradleCatchScene",
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


def slab(color: str, width: float, height: float) -> Rectangle:
    return Rectangle(width=width, height=height, stroke_width=0, fill_color=color, fill_opacity=1)


class QualityCradleCatchScene(Scene):
    def construct(self) -> None:
        self.camera.background_color = WHITE

        frame = Rectangle(
            width=12.8,
            height=5.7,
            stroke_color=GRAY_200,
            stroke_width=2,
            fill_color=WHITE,
            fill_opacity=0,
        )
        source_zone = Rectangle(width=4.0, height=4.1, stroke_width=0, fill_color=GRAY_100, fill_opacity=0.2).move_to(LEFT * 3.05)
        target_zone = Rectangle(width=4.25, height=4.1, stroke_width=0, fill_color=GRAY_100, fill_opacity=0.24).move_to(RIGHT * 2.92)

        green = slab(PRIMARY_GREEN, 2.46, 0.76).move_to(LEFT * 3.28 + UP * 0.9)
        blue = slab(PRIMARY_BLUE, 1.68, 0.58).move_to(LEFT * 2.42 + DOWN * 0.2)
        purple = slab(PRIMARY_PURPLE, 1.12, 0.46).move_to(LEFT * 3.55 + DOWN * 1.05)
        source = VGroup(green, blue, purple)

        guide = Line(LEFT * 0.88 + UP * 0.78, RIGHT * 1.2 + UP * 0.34, color=PRIMARY_ORANGE, stroke_width=5)
        guide.set_opacity(0.72)
        cradle_arc = Arc(
            radius=1.3,
            start_angle=200 / 180 * PI,
            angle=140 / 180 * PI,
            color=GRAY_300,
            stroke_width=4,
        ).move_to(RIGHT * 2.54 + DOWN * 0.16)
        cradle_arc.set_opacity(0.36)

        left_slot = slab(GRAY_300, 1.08, 0.16).move_to(RIGHT * 1.6 + DOWN * 0.78).rotate(17 / 180 * PI)
        right_slot = slab(GRAY_300, 1.08, 0.16).move_to(RIGHT * 3.34 + DOWN * 0.78).rotate(-17 / 180 * PI)
        left_slot.set_opacity(0.32)
        right_slot.set_opacity(0.32)

        accent = Circle(radius=0.14, stroke_width=0, fill_color=PRIMARY_YELLOW, fill_opacity=1).move_to(LEFT * 0.72 + UP * 0.72)

        blue_cradle = slab(PRIMARY_BLUE, 1.34, 0.36).move_to(RIGHT * 1.78 + DOWN * 0.72).rotate(17 / 180 * PI)
        purple_cradle = slab(PRIMARY_PURPLE, 1.08, 0.32).move_to(RIGHT * 3.18 + DOWN * 0.72).rotate(-17 / 180 * PI)
        green_catch = slab(PRIMARY_GREEN, 1.72, 0.5).move_to(RIGHT * 2.46 + UP * 0.04)

        green_settle = Circle(radius=0.68, stroke_width=0, fill_color=PRIMARY_GREEN, fill_opacity=1).move_to(RIGHT * 2.5 + UP * 0.24)
        blue_settle = Circle(radius=0.36, stroke_width=0, fill_color=PRIMARY_BLUE, fill_opacity=1).move_to(RIGHT * 1.42 + DOWN * 0.86)
        purple_settle = Circle(radius=0.3, stroke_width=0, fill_color=PRIMARY_PURPLE, fill_opacity=1).move_to(RIGHT * 3.54 + DOWN * 0.86)

        final_green = Circle(radius=0.72, stroke_width=0, fill_color=PRIMARY_GREEN, fill_opacity=1).move_to(RIGHT * 1.24 + UP * 0.3)
        final_blue = Circle(radius=0.38, stroke_width=0, fill_color=PRIMARY_BLUE, fill_opacity=1).move_to(RIGHT * 0.22 + DOWN * 0.9)
        final_purple = Circle(radius=0.31, stroke_width=0, fill_color=PRIMARY_PURPLE, fill_opacity=1).move_to(RIGHT * 2.18 + DOWN * 0.9)

        self.add(frame, source_zone, target_zone, source, guide, cradle_arc, left_slot, right_slot)
        self.wait(2.6)

        self.play(FadeIn(accent), run_time=0.8)
        self.play(accent.animate.move_to(RIGHT * 0.92 + UP * 0.34), run_time=2.0, rate_func=smooth)
        self.play(
            AnimationGroup(
                Transform(blue, blue_cradle.copy()),
                Transform(purple, purple_cradle.copy()),
                accent.animate.move_to(RIGHT * 1.62 + DOWN * 0.34),
                lag_ratio=0.18,
            ),
            run_time=3.2,
            rate_func=smooth,
        )
        self.wait(1.1)
        self.play(
            AnimationGroup(
                Transform(green, green_catch.copy()),
                accent.animate.move_to(RIGHT * 2.34 + DOWN * 0.1),
                lag_ratio=0.1,
            ),
            run_time=3.4,
            rate_func=smooth,
        )
        self.wait(2.2)
        self.play(
            AnimationGroup(
                Transform(green, green_settle.copy()),
                Transform(blue, blue_settle.copy()),
                Transform(purple, purple_settle.copy()),
                lag_ratio=0.12,
            ),
            run_time=2.8,
            rate_func=smooth,
        )
        self.play(
            FadeOut(guide),
            FadeOut(cradle_arc),
            FadeOut(left_slot),
            FadeOut(right_slot),
            FadeOut(source_zone),
            FadeOut(target_zone),
            FadeOut(accent),
            run_time=1.4,
        )
        self.play(
            AnimationGroup(
                Transform(green, final_green.copy()),
                Transform(blue, final_blue.copy()),
                Transform(purple, final_purple.copy()),
                lag_ratio=0.1,
            ),
            run_time=2.3,
            rate_func=smooth,
        )
        self.wait(7.0)


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
