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


def slab(color: str, width: float, height: float) -> Rectangle:
    return Rectangle(width=width, height=height, stroke_width=0, fill_color=color, fill_opacity=1)


class QualityMagnetCaptureScene(Scene):
    def construct(self) -> None:
        self.camera.background_color = WHITE
        source_zone = Rectangle(width=4.0, height=3.8, stroke_width=0, fill_color=GRAY_100, fill_opacity=0.22).move_to(LEFT * 3.18)
        target_zone = Rectangle(width=5.4, height=3.8, stroke_width=0, fill_color=GRAY_100, fill_opacity=0.28).move_to(RIGHT * 2.42)

        green = Circle(radius=0.76, stroke_width=0, fill_color=PRIMARY_GREEN, fill_opacity=1).move_to(LEFT * 3.34 + UP * 0.36)
        blue = slab(PRIMARY_BLUE, 1.18, 0.46).move_to(LEFT * 2.32 + DOWN * 0.88)
        purple = slab(PRIMARY_PURPLE, 0.82, 0.34).move_to(LEFT * 1.72 + UP * 0.94)
        source = VGroup(green, blue, purple)

        receiver_right = Line(RIGHT * 3.78 + UP * 1.02, RIGHT * 3.78 + DOWN * 1.02, color=PRIMARY_ORANGE, stroke_width=7)
        receiver_top = Line(RIGHT * 2.24 + UP * 1.02, RIGHT * 3.14 + UP * 1.02, color=PRIMARY_ORANGE, stroke_width=7)
        receiver_bottom = Line(RIGHT * 2.24 + DOWN * 1.02, RIGHT * 3.14 + DOWN * 1.02, color=PRIMARY_ORANGE, stroke_width=7)
        receiver = VGroup(receiver_right, receiver_top, receiver_bottom)
        receiver.set_opacity(0.42)

        slot_a = Circle(radius=0.22, stroke_color=GRAY_200, stroke_width=2, fill_opacity=0).move_to(RIGHT * 2.48 + UP * 0.42)
        slot_b = Circle(radius=0.16, stroke_color=GRAY_200, stroke_width=2, fill_opacity=0).move_to(RIGHT * 2.7 + DOWN * 0.46)
        target_slots = VGroup(slot_a, slot_b)

        core = Circle(radius=0.12, stroke_width=0, fill_color=PRIMARY_YELLOW, fill_opacity=1).move_to(RIGHT * 2.54 + UP * 0.02)
        field_1 = Line(RIGHT * 1.58 + UP * 0.52, RIGHT * 2.28 + UP * 0.52, color=PRIMARY_ORANGE, stroke_width=3).set_opacity(0.18)
        field_2 = Line(RIGHT * 1.42, RIGHT * 2.24, color=PRIMARY_ORANGE, stroke_width=3).set_opacity(0.2)
        field_3 = Line(RIGHT * 1.58 + DOWN * 0.52, RIGHT * 2.28 + DOWN * 0.52, color=PRIMARY_ORANGE, stroke_width=3).set_opacity(0.18)
        field = VGroup(field_1, field_2, field_3)

        green_stretch = slab(PRIMARY_GREEN, 2.22, 0.38).move_to(RIGHT * 1.98 + UP * 0.1)
        capture_shift = LEFT * 2.25
        green_capture = slab(PRIMARY_GREEN, 1.12, 0.5).move_to(RIGHT * 2.22 + UP * 0.08)
        core_capture = Circle(radius=0.12, stroke_width=0, fill_color=PRIMARY_RED, fill_opacity=1).move_to(RIGHT * 3.18 + UP * 0.08)
        blue_capture = slab(PRIMARY_BLUE, 0.78, 0.32).move_to(RIGHT * 2.58 + DOWN * 0.56).shift(capture_shift)
        purple_capture = slab(PRIMARY_PURPLE, 0.66, 0.28).move_to(RIGHT * 2.54 + UP * 0.66).shift(capture_shift)

        final_green = Circle(radius=0.84, stroke_width=0, fill_color=PRIMARY_GREEN, fill_opacity=1).move_to(ORIGIN + UP * 0.04)
        final_blue = Circle(radius=0.36, stroke_width=0, fill_color=PRIMARY_BLUE, fill_opacity=1).move_to(RIGHT * 0.72 + DOWN * 0.48)
        final_purple = Circle(radius=0.26, stroke_width=0, fill_color=PRIMARY_PURPLE, fill_opacity=1).move_to(RIGHT * 0.62 + UP * 0.7)
        final_zone = Rectangle(width=4.2, height=3.8, stroke_width=0, fill_color=GRAY_100, fill_opacity=0.24).move_to(ORIGIN)

        self.add(source_zone, target_zone, source, receiver, target_slots, core)
        self.wait(2.6)
        self.play(receiver.animate.set_opacity(1), FadeIn(field), core.animate.scale(1.45), run_time=1.8, rate_func=smooth)
        self.wait(1.0)
        self.play(Transform(green, green_stretch.copy()), core.animate.move_to(RIGHT * 2.16 + UP * 0.05), run_time=2.4, rate_func=smooth)
        self.wait(1.2)
        self.play(Transform(green, green_capture.copy()), Transform(core, core_capture.copy()), run_time=2.0, rate_func=smooth)
        self.wait(1.4)
        self.play(
            AnimationGroup(
                VGroup(target_zone, receiver, green, core).animate.shift(capture_shift),
                FadeOut(source_zone),
                FadeOut(field),
                FadeOut(target_slots),
                lag_ratio=0,
            ),
            run_time=1.8,
            rate_func=smooth,
        )
        self.wait(0.6)
        self.play(
            AnimationGroup(
                Transform(blue, blue_capture.copy()),
                Transform(purple, purple_capture.copy()),
                lag_ratio=0.22,
            ),
            run_time=2.4,
            rate_func=smooth,
        )
        self.wait(1.6)
        self.wait(1.1)
        self.play(FadeOut(receiver), FadeOut(core), run_time=0.8, rate_func=smooth)
        self.play(
            AnimationGroup(
                Transform(green, final_green.copy()),
                Transform(blue, final_blue.copy()),
                Transform(purple, final_purple.copy()),
                Transform(target_zone, final_zone.copy()),
                lag_ratio=0.04,
            ),
            run_time=3.2,
            rate_func=smooth,
        )
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
