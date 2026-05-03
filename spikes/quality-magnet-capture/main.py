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

from manim import DOWN, LEFT, ORIGIN, RIGHT, UP, AnimationGroup, Circle, FadeIn, FadeOut, Line, Rectangle, Scene, Transform, VGroup, WHITE, config, smooth

SPIKE_DIR = Path(__file__).resolve().parent
REPO_ROOT = SPIKE_DIR.parent.parent
SPIKE_NAME = SPIKE_DIR.name
OUTPUT_DIR = REPO_ROOT / "videos" / SPIKE_NAME
STAGING_DIR = OUTPUT_DIR / ".manim"

PRIMARY_RED = "#9e1b32"
PAGE_BACKGROUND = "#f7f7f7"
GRAY_100 = "#e7e7e7"
GRAY_200 = "#cfcfcf"
GRAY_300 = "#b5b5b5"
GRAY_500 = "#828282"
GRAY_700 = "#333e48"

config.transparent = True
config.background_opacity = 0.0


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
        self.camera.background_opacity = 0.0

        source_zone = Rectangle(
            width=3.45,
            height=3.3,
            stroke_color=GRAY_200,
            stroke_width=3,
            fill_color=PAGE_BACKGROUND,
            fill_opacity=0.38,
        ).move_to(LEFT * 3.1)
        target_zone = Rectangle(
            width=4.15,
            height=3.35,
            stroke_width=0,
            fill_color=PAGE_BACKGROUND,
            fill_opacity=0.34,
        ).move_to(RIGHT * 2.25)

        leader = Circle(radius=0.76, stroke_width=0, fill_color=PRIMARY_RED, fill_opacity=1).move_to(LEFT * 3.42 + UP * 0.3)
        support_a = slab(GRAY_700, 1.05, 0.38).move_to(LEFT * 2.42 + DOWN * 0.72)
        support_b = slab(GRAY_500, 0.76, 0.3).move_to(LEFT * 2.08 + UP * 1.16)
        source = VGroup(leader, support_a, support_b)

        receiver_right = Line(RIGHT * 3.72 + UP * 1.0, RIGHT * 3.72 + DOWN * 1.0, color=GRAY_700, stroke_width=7)
        receiver_top = Line(RIGHT * 2.24 + UP * 1.0, RIGHT * 3.08 + UP * 1.0, color=GRAY_700, stroke_width=7)
        receiver_bottom = Line(RIGHT * 2.24 + DOWN * 1.0, RIGHT * 3.08 + DOWN * 1.0, color=GRAY_700, stroke_width=7)
        receiver = VGroup(receiver_right, receiver_top, receiver_bottom)
        receiver.set_opacity(0.44)

        slot_a = Circle(radius=0.24, stroke_color=GRAY_300, stroke_width=2, fill_opacity=0).move_to(RIGHT * 2.62 + UP * 0.76)
        slot_b = Circle(radius=0.18, stroke_color=GRAY_300, stroke_width=2, fill_opacity=0).move_to(RIGHT * 2.76 + DOWN * 0.66)
        target_slots = VGroup(slot_a, slot_b)

        core = Circle(radius=0.1, stroke_width=0, fill_color=PRIMARY_RED, fill_opacity=1).move_to(RIGHT * 2.48 + UP * 0.02)
        field_1 = Line(RIGHT * 1.46 + UP * 0.52, RIGHT * 2.24 + UP * 0.52, color=GRAY_500, stroke_width=3).set_opacity(0.22)
        field_2 = Line(RIGHT * 1.32, RIGHT * 2.2, color=GRAY_500, stroke_width=3).set_opacity(0.24)
        field_3 = Line(RIGHT * 1.46 + DOWN * 0.52, RIGHT * 2.24 + DOWN * 0.52, color=GRAY_500, stroke_width=3).set_opacity(0.22)
        field = VGroup(field_1, field_2, field_3)

        leader_stretch = slab(PRIMARY_RED, 2.34, 0.4).move_to(RIGHT * 1.86 + UP * 0.08)
        capture_shift = LEFT * 2.15
        leader_capture = slab(PRIMARY_RED, 1.18, 0.5).move_to(RIGHT * 2.2 + UP * 0.08)
        core_capture = Circle(radius=0.1, stroke_width=0, fill_color=PRIMARY_RED, fill_opacity=1).move_to(RIGHT * 3.12 + UP * 0.08)
        support_a_capture = slab(GRAY_700, 0.8, 0.34).move_to(RIGHT * 2.54 + DOWN * 0.58).shift(capture_shift)
        support_b_capture = slab(GRAY_500, 0.66, 0.28).move_to(RIGHT * 2.5 + UP * 0.68).shift(capture_shift)

        final_leader = Circle(radius=1.0, stroke_width=0, fill_color=PRIMARY_RED, fill_opacity=1).move_to(ORIGIN + LEFT * 0.06)
        final_support_a = Circle(radius=0.34, stroke_width=0, fill_color=GRAY_700, fill_opacity=1).move_to(RIGHT * 0.78 + DOWN * 0.48)
        final_support_b = Circle(radius=0.26, stroke_width=0, fill_color=GRAY_500, fill_opacity=1).move_to(RIGHT * 0.7 + UP * 0.78)
        self.add(source_zone, target_zone, source, receiver, target_slots, core)
        self.wait(2.6)
        self.play(receiver.animate.set_opacity(1), FadeIn(field), core.animate.scale(1.45), run_time=1.8, rate_func=smooth)
        self.wait(1.0)
        self.play(Transform(leader, leader_stretch.copy()), core.animate.move_to(RIGHT * 2.12 + UP * 0.05), run_time=2.4, rate_func=smooth)
        self.wait(1.2)
        self.play(Transform(leader, leader_capture.copy()), Transform(core, core_capture.copy()), run_time=2.0, rate_func=smooth)
        self.wait(1.4)
        self.play(
            AnimationGroup(
                VGroup(receiver, leader, core).animate.shift(capture_shift),
                FadeOut(source_zone),
                FadeOut(target_zone),
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
                Transform(support_a, support_a_capture.copy()),
                Transform(support_b, support_b_capture.copy()),
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
                Transform(leader, final_leader.copy()),
                Transform(support_a, final_support_a.copy()),
                Transform(support_b, final_support_b.copy()),
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
