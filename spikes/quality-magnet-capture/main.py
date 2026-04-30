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
    parser = argparse.ArgumentParser(description="Render the quality-magnet-capture spike.")
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
        "-o", stem, "--media_dir", str(STAGING_DIR), str(Path(__file__).resolve()), "QualityMagnetCaptureScene",
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


class QualityMagnetCaptureScene(Scene):
    def construct(self) -> None:
        self.camera.background_color = WHITE
        frame = RoundedRectangle(width=12.9, height=5.8, corner_radius=0.34, stroke_color=GRAY_200, stroke_width=2, fill_color=WHITE, fill_opacity=0)
        source_zone = RoundedRectangle(width=4.0, height=4.1, corner_radius=0.35, stroke_width=0, fill_color=GRAY_100, fill_opacity=0.22).move_to(LEFT * 3.08)
        target_zone = RoundedRectangle(width=4.2, height=4.1, corner_radius=0.35, stroke_width=0, fill_color=GRAY_100, fill_opacity=0.28).move_to(RIGHT * 2.96)

        green = Circle(radius=0.76, stroke_width=0, fill_color=PRIMARY_GREEN, fill_opacity=1).move_to(LEFT * 3.06 + UP * 0.22)
        blue = slab(PRIMARY_BLUE, 1.38, 0.58).move_to(LEFT * 2.1 + DOWN * 0.54)
        purple = slab(PRIMARY_PURPLE, 0.96, 0.42).move_to(LEFT * 1.54 + UP * 0.98)
        source = VGroup(green, blue, purple)

        receiver_right = Line(RIGHT * 3.14 + UP * 0.92, RIGHT * 3.14 + DOWN * 0.96, color=PRIMARY_ORANGE, stroke_width=7)
        receiver_top = Line(RIGHT * 2.28 + UP * 0.92, RIGHT * 3.14 + UP * 0.92, color=PRIMARY_ORANGE, stroke_width=7)
        receiver_bottom = Line(RIGHT * 2.28 + DOWN * 0.96, RIGHT * 3.14 + DOWN * 0.96, color=PRIMARY_ORANGE, stroke_width=7)
        receiver = VGroup(receiver_right, receiver_top, receiver_bottom)
        core = Circle(radius=0.16, stroke_width=0, fill_color=PRIMARY_YELLOW, fill_opacity=1).move_to(RIGHT * 2.56 + UP * 0.04)

        green_pull = slab(PRIMARY_GREEN, 1.72, 0.42).move_to(RIGHT * 2.22 + UP * 0.16)
        blue_pull = slab(PRIMARY_BLUE, 0.94, 0.38).move_to(RIGHT * 2.7 + DOWN * 0.52)
        purple_pull = slab(PRIMARY_PURPLE, 0.78, 0.34).move_to(RIGHT * 2.74 + UP * 0.62)

        final_green = Circle(radius=0.84, stroke_width=0, fill_color=PRIMARY_GREEN, fill_opacity=1).move_to(RIGHT * 2.88 + UP * 0.1)
        final_blue = Circle(radius=0.4, stroke_width=0, fill_color=PRIMARY_BLUE, fill_opacity=1).move_to(RIGHT * 3.7 + DOWN * 0.52)
        final_purple = Circle(radius=0.28, stroke_width=0, fill_color=PRIMARY_PURPLE, fill_opacity=1).move_to(RIGHT * 3.56 + UP * 0.8)

        self.add(frame, source_zone, target_zone)
        self.play(FadeIn(source, lag_ratio=0.08), run_time=0.68)
        self.play(FadeIn(receiver), FadeIn(core), run_time=0.2)
        self.play(Transform(green, green_pull.copy()), run_time=0.34, rate_func=smooth)
        self.play(core.animate.move_to(RIGHT * 2.84 + UP * 0.06), run_time=0.16, rate_func=smooth)
        self.play(
            AnimationGroup(
                Transform(blue, blue_pull.copy()),
                Transform(purple, purple_pull.copy()),
                lag_ratio=0.08,
            ),
            run_time=0.2,
            rate_func=smooth,
        )
        self.play(
            AnimationGroup(
                Transform(green, final_green.copy()),
                Transform(blue, final_blue.copy()),
                Transform(purple, final_purple.copy()),
                lag_ratio=0.08,
            ),
            run_time=0.58,
            rate_func=smooth,
        )
        self.play(core.animate.move_to(RIGHT * 3.02 + UP * 0.02).set_fill(PRIMARY_RED, opacity=1), run_time=0.14)
        self.play(FadeOut(receiver), FadeOut(core), run_time=0.18)
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
