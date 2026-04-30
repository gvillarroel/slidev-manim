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

from manim import DOWN, LEFT, ORIGIN, RIGHT, UP, AnimationGroup, Circle, FadeIn, FadeOut, Line, Rectangle, Scene, Transform, VGroup, WHITE, smooth

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
    parser = argparse.ArgumentParser(description="Render the quality-bumper-deflect spike.")
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
        "-o", stem, "--media_dir", str(STAGING_DIR), str(Path(__file__).resolve()), "QualityBumperDeflectScene",
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


class QualityBumperDeflectScene(Scene):
    def construct(self) -> None:
        self.camera.background_color = WHITE
        frame = Rectangle(width=12.55, height=5.55, stroke_color=GRAY_200, stroke_width=2, fill_color=WHITE, fill_opacity=0)
        source_zone = Rectangle(width=3.8, height=3.85, stroke_width=0, fill_color=GRAY_100, fill_opacity=0.22).move_to(LEFT * 3.18)
        target_zone = Rectangle(width=4.8, height=3.85, stroke_width=0, fill_color=GRAY_100, fill_opacity=0.28).move_to(RIGHT * 2.85)

        green = slab(PRIMARY_GREEN, 2.6, 0.88).move_to(LEFT * 3.48 + UP * 0.78)
        blue = slab(PRIMARY_BLUE, 1.72, 0.72).move_to(LEFT * 2.62 + DOWN * 0.12)
        purple = slab(PRIMARY_PURPLE, 1.08, 0.5).move_to(LEFT * 2.18 + DOWN * 1.0)
        source = VGroup(green, blue, purple)

        target_slots = VGroup(
            Circle(radius=0.84, stroke_color=GRAY_200, stroke_width=3, fill_opacity=0).move_to(RIGHT * 2.4 + UP * 0.62),
            Circle(radius=0.42, stroke_color=GRAY_200, stroke_width=3, fill_opacity=0).move_to(RIGHT * 4.4 + DOWN * 0.22),
            Circle(radius=0.24, stroke_color=GRAY_200, stroke_width=3, fill_opacity=0).move_to(RIGHT * 3.75 + DOWN * 1.18),
        )
        target_slots.set_stroke(opacity=0.38)

        bumper = Line(RIGHT * 1.78 + DOWN * 0.88, RIGHT * 2.78 + UP * 0.92, color=PRIMARY_ORANGE, stroke_width=12)
        contact_mark = Circle(radius=0.16, stroke_width=0, fill_color=PRIMARY_YELLOW, fill_opacity=1).move_to(RIGHT * 1.28 + DOWN * 0.1)

        green_approach = slab(PRIMARY_GREEN, 2.32, 0.62).move_to(RIGHT * 0.78 + DOWN * 0.1).rotate(0.04)
        green_hit = slab(PRIMARY_GREEN, 1.74, 0.34).move_to(RIGHT * 1.7 + DOWN * 0.02).rotate(0.12)
        blue_support = slab(PRIMARY_BLUE, 1.08, 0.46).move_to(RIGHT * 1.02 + DOWN * 1.38)
        purple_support = slab(PRIMARY_PURPLE, 0.72, 0.34).move_to(RIGHT * 3.75 + DOWN * 1.18)

        final_green = Circle(radius=0.84, stroke_width=0, fill_color=PRIMARY_GREEN, fill_opacity=1).move_to(RIGHT * 2.4 + UP * 0.62)
        final_blue = Circle(radius=0.42, stroke_width=0, fill_color=PRIMARY_BLUE, fill_opacity=1).move_to(RIGHT * 4.4 + DOWN * 0.22)
        final_purple = Circle(radius=0.24, stroke_width=0, fill_color=PRIMARY_PURPLE, fill_opacity=1).move_to(RIGHT * 3.75 + DOWN * 1.18)
        resolved_group = VGroup(target_zone, green, blue, purple)

        self.add(frame, source_zone, target_zone, target_slots, source)
        self.wait(2.4)
        self.play(FadeIn(bumper), FadeIn(contact_mark), run_time=0.8)
        self.play(contact_mark.animate.move_to(RIGHT * 1.78 + DOWN * 0.02), run_time=0.8, rate_func=smooth)
        self.wait(0.8)
        self.play(Transform(green, green_approach.copy()), contact_mark.animate.move_to(RIGHT * 2.02 + DOWN * 0.02), run_time=2.2, rate_func=smooth)
        self.play(Transform(green, green_hit.copy()), contact_mark.animate.move_to(RIGHT * 2.16 + UP * 0.02).set_fill(PRIMARY_RED, opacity=1), run_time=1.55, rate_func=smooth)
        self.wait(1.4)
        self.play(
            AnimationGroup(Transform(blue, blue_support.copy()), Transform(purple, purple_support.copy()), lag_ratio=0.1),
            run_time=2.35,
            rate_func=smooth,
        )
        self.wait(0.9)
        self.play(FadeOut(target_slots), run_time=0.6)
        self.play(
            AnimationGroup(Transform(green, final_green.copy()), Transform(blue, final_blue.copy()), Transform(purple, final_purple.copy()), lag_ratio=0.08),
            run_time=3.0,
            rate_func=smooth,
        )
        self.wait(0.9)
        self.play(FadeOut(bumper), FadeOut(contact_mark), FadeOut(source_zone), run_time=1.4)
        self.play(resolved_group.animate.move_to(ORIGIN), run_time=1.8, rate_func=smooth)
        self.wait(6.0)


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
