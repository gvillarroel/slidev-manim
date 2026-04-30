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

from manim import DOWN, LEFT, RIGHT, UP, AnimationGroup, Circle, FadeIn, FadeOut, Rectangle, Scene, Transform, VGroup, WHITE, smooth

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
    parser = argparse.ArgumentParser(description="Render the quality-clamp-close spike.")
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
        "-o", stem, "--media_dir", str(STAGING_DIR), str(Path(__file__).resolve()), "QualityClampCloseScene",
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


def promote_all(args: _Args) -> None:
    video_path, poster_path = output_paths()
    result = subprocess.run(render_command(args, video_path.stem, poster=False), check=False)
    if result.returncode != 0:
        raise SystemExit(result.returncode)
    promote(video_path.name, video_path)
    result = subprocess.run(render_command(args, poster_path.stem, poster=True), check=False)
    if result.returncode != 0:
        raise SystemExit(result.returncode)
    promote(poster_path.name, poster_path)


def slab(color: str, width: float, height: float) -> Rectangle:
    return Rectangle(width=width, height=height, stroke_width=0, fill_color=color, fill_opacity=1)


class QualityClampCloseScene(Scene):
    def construct(self) -> None:
        self.camera.background_color = WHITE
        frame = Rectangle(width=12.9, height=5.8, stroke_color=GRAY_200, stroke_width=2, fill_color=WHITE, fill_opacity=0)
        source_zone = Rectangle(width=4.0, height=4.1, stroke_width=0, fill_color=GRAY_100, fill_opacity=0.2).move_to(LEFT * 3.18)
        target_zone = Rectangle(width=4.35, height=4.1, stroke_width=0, fill_color=GRAY_100, fill_opacity=0.26).move_to(RIGHT * 1.78)

        green = slab(PRIMARY_GREEN, 2.72, 0.92).move_to(LEFT * 3.46 + UP * 0.82)
        blue = slab(PRIMARY_BLUE, 1.84, 0.78).move_to(LEFT * 2.62 + DOWN * 0.1)
        purple = slab(PRIMARY_PURPLE, 1.24, 0.58).move_to(LEFT * 3.78 + DOWN * 1.02)
        source = VGroup(green, blue, purple)

        clamp_left = slab(PRIMARY_BLUE, 0.42, 2.24).move_to(RIGHT * 0.94 + DOWN * 0.02)
        clamp_right = slab(PRIMARY_PURPLE, 0.42, 2.24).move_to(RIGHT * 2.42 + DOWN * 0.02)
        clamp_left.set_opacity(0.62)
        clamp_right.set_opacity(0.62)
        accent = Circle(radius=0.16, stroke_width=0, fill_color=PRIMARY_YELLOW, fill_opacity=1).move_to(RIGHT * 1.68 + DOWN * 0.02)

        green_clamp = slab(PRIMARY_GREEN, 1.02, 0.34).move_to(RIGHT * 1.68 + DOWN * 0.02)
        blue_clamp = slab(PRIMARY_BLUE, 0.46, 0.36).move_to(RIGHT * 1.12 + DOWN * 0.62)
        purple_clamp = slab(PRIMARY_PURPLE, 0.42, 0.32).move_to(RIGHT * 2.22 + UP * 0.62)
        pressure_wall = Rectangle(width=1.58, height=0.66, stroke_color=PRIMARY_RED, stroke_width=3, fill_opacity=0).move_to(RIGHT * 1.68 + DOWN * 0.02)

        final_green = Circle(radius=0.9, stroke_width=0, fill_color=PRIMARY_GREEN, fill_opacity=1).move_to(RIGHT * 1.56 + UP * 0.42)
        final_blue = Circle(radius=0.47, stroke_width=0, fill_color=PRIMARY_BLUE, fill_opacity=1).move_to(RIGHT * 2.74 + DOWN * 0.1)
        final_purple = Circle(radius=0.28, stroke_width=0, fill_color=PRIMARY_PURPLE, fill_opacity=1).move_to(RIGHT * 2.08 + DOWN * 1.04)

        self.add(frame, source_zone, target_zone, source, clamp_left, clamp_right)
        self.wait(2.6)
        self.play(
            AnimationGroup(
                Transform(green, green_clamp.copy()),
                blue.animate.move_to(LEFT * 2.62 + DOWN * 0.1).set_opacity(0.55),
                purple.animate.move_to(LEFT * 3.78 + DOWN * 1.02).set_opacity(0.48),
                lag_ratio=0.0,
            ),
            run_time=3.2,
            rate_func=smooth,
        )
        self.wait(1.0)
        self.play(
            AnimationGroup(
                clamp_left.animate.move_to(RIGHT * 1.28 + DOWN * 0.02).set_opacity(1),
                clamp_right.animate.move_to(RIGHT * 2.08 + DOWN * 0.02).set_opacity(1),
                Transform(blue, blue_clamp.copy()),
                Transform(purple, purple_clamp.copy()),
                FadeIn(accent),
                lag_ratio=0.0,
            ),
            run_time=2.4,
            rate_func=smooth,
        )
        self.play(FadeIn(pressure_wall), FadeOut(source_zone), accent.animate.scale(1.35), run_time=0.9, rate_func=smooth)
        self.wait(1.6)
        self.play(FadeOut(pressure_wall), accent.animate.move_to(RIGHT * 2.36 + UP * 0.26).set_fill(PRIMARY_RED, opacity=1), run_time=1.2, rate_func=smooth)
        self.play(FadeOut(clamp_left), FadeOut(clamp_right), run_time=0.8, rate_func=smooth)
        self.play(
            AnimationGroup(
                Transform(green, final_green.copy()),
                Transform(blue, final_blue.copy()),
                Transform(purple, final_purple.copy()),
                lag_ratio=0.1,
            ),
            run_time=3.4,
            rate_func=smooth,
        )
        self.wait(0.8)
        self.play(
            target_zone.animate.move_to(RIGHT * 1.94).set_opacity(0.2),
            run_time=1.2,
            rate_func=smooth,
        )
        self.play(accent.animate.move_to(RIGHT * 2.92 + DOWN * 0.12).scale(0.74), run_time=1.1, rate_func=smooth)
        self.play(FadeOut(accent), run_time=0.8)
        self.wait(6.4)


def main() -> int:
    args = parse_args()
    promote_all(args)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
