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

from manim import DOWN, LEFT, RIGHT, UP, AnimationGroup, Circle, FadeIn, FadeOut, Line, Rectangle, Scene, Transform, VGroup, WHITE, smooth

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
    matches = sorted(STAGING_DIR.glob(f"**/{target_name}"), key=lambda path: path.stat().st_mtime)
    if not matches:
        raise FileNotFoundError(target_name)
    destination.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(matches[-1], destination)


def slab(color: str, width: float, height: float) -> Rectangle:
    return Rectangle(width=width, height=height, stroke_width=0, fill_color=color, fill_opacity=1)


def guide_slot(center, width: float, height: float, color: str = GRAY_300) -> VGroup:
    left = Line(UP * height / 2, DOWN * height / 2, color=color, stroke_width=3).move_to(center + LEFT * width / 2)
    right = Line(UP * height / 2, DOWN * height / 2, color=color, stroke_width=3).move_to(center + RIGHT * width / 2)
    return VGroup(left, right).set_opacity(0.32)


class QualityCounterliftBalanceScene(Scene):
    def construct(self) -> None:
        self.camera.background_color = WHITE
        frame = Rectangle(width=12.55, height=5.65, stroke_color=GRAY_200, stroke_width=2, fill_color=WHITE, fill_opacity=0)
        source_zone = Rectangle(width=3.45, height=3.75, stroke_width=0, fill_color=GRAY_100, fill_opacity=0).move_to(LEFT * 3.38)
        target_zone = Rectangle(width=4.85, height=3.75, stroke_width=0, fill_color=GRAY_100, fill_opacity=0).move_to(RIGHT * 1.72)

        green = slab(PRIMARY_GREEN, 2.18, 0.68).move_to(LEFT * 3.72 + UP * 0.72)
        blue = slab(PRIMARY_BLUE, 1.62, 0.58).move_to(LEFT * 3.02 + DOWN * 0.12)
        purple = slab(PRIMARY_PURPLE, 1.06, 0.44).move_to(LEFT * 2.68 + DOWN * 0.86)
        source = VGroup(green, blue, purple)

        balance = Line(LEFT * 0.1 + DOWN * 0.18, RIGHT * 3.42 + DOWN * 0.18, color=PRIMARY_ORANGE, stroke_width=7)
        tilted_balance = Line(LEFT * 0.08 + UP * 0.82, RIGHT * 3.46 + DOWN * 0.82, color=PRIMARY_ORANGE, stroke_width=7)
        pivot = Circle(radius=0.18, stroke_width=0, fill_color=PRIMARY_YELLOW, fill_opacity=1).move_to(RIGHT * 1.66 + DOWN * 0.18)
        pivot_hold = Circle(radius=0.18, stroke_width=0, fill_color=PRIMARY_YELLOW, fill_opacity=1).move_to(RIGHT * 1.68 + DOWN * 0.05)

        lift_slot = guide_slot(RIGHT * 0.38 + UP * 1.32, 1.94, 0.72)
        drop_slot = guide_slot(RIGHT * 3.08 + DOWN * 1.18, 1.62, 0.66)
        counter_slot = guide_slot(RIGHT * 2.46 + UP * 0.1, 1.24, 0.52)
        guide_slots = VGroup(lift_slot, drop_slot, counter_slot)

        green_ready = slab(PRIMARY_GREEN, 1.72, 0.5).move_to(RIGHT * 0.42 + UP * 0.54)
        blue_ready = slab(PRIMARY_BLUE, 1.3, 0.48).move_to(RIGHT * 3.0 + DOWN * 0.84)
        purple_ready = slab(PRIMARY_PURPLE, 0.94, 0.38).move_to(RIGHT * 2.36 + DOWN * 1.26)

        green_lift = slab(PRIMARY_GREEN, 1.72, 0.5).move_to(RIGHT * 0.38 + UP * 1.32)
        blue_drop = slab(PRIMARY_BLUE, 1.3, 0.48).move_to(RIGHT * 3.08 + DOWN * 1.18)
        purple_counter = slab(PRIMARY_PURPLE, 0.94, 0.38).move_to(RIGHT * 2.46 + UP * 0.1)

        final_green = Circle(radius=0.82, stroke_width=0, fill_color=PRIMARY_GREEN, fill_opacity=1).move_to(RIGHT * 0.42 + UP * 0.62)
        final_blue = Circle(radius=0.52, stroke_width=0, fill_color=PRIMARY_BLUE, fill_opacity=1).move_to(RIGHT * 2.08 + DOWN * 0.04)
        final_purple = Circle(radius=0.32, stroke_width=0, fill_color=PRIMARY_PURPLE, fill_opacity=1).move_to(RIGHT * 1.08 + DOWN * 1.06)

        terminal_left = Line(UP * 0.52, DOWN * 0.52, color=PRIMARY_RED, stroke_width=5).move_to(RIGHT * -0.62 + DOWN * 0.06)
        terminal_right = Line(UP * 0.52, DOWN * 0.52, color=PRIMARY_RED, stroke_width=5).move_to(RIGHT * 2.9 + DOWN * 0.06)
        terminal = VGroup(terminal_left, terminal_right)

        self.add(frame, source_zone, target_zone, balance, pivot, guide_slots, source)
        self.wait(2.6)
        self.play(
            AnimationGroup(
                Transform(green, green_ready.copy(), path_arc=0.3),
                Transform(blue, blue_ready.copy(), path_arc=-0.75),
                Transform(purple, purple_ready.copy(), path_arc=-0.35),
                lag_ratio=0.12,
            ),
            run_time=4.0,
            rate_func=smooth,
        )
        self.play(FadeOut(source_zone), run_time=0.8)
        self.wait(0.6)
        self.play(
            AnimationGroup(
                Transform(balance, tilted_balance.copy()),
                Transform(pivot, pivot_hold.copy()),
                Transform(green, green_lift.copy()),
                Transform(blue, blue_drop.copy()),
                Transform(purple, purple_counter.copy()),
                lag_ratio=0.04,
            ),
            run_time=3.6,
            rate_func=smooth,
        )
        self.wait(2.2)
        self.play(FadeOut(guide_slots), FadeOut(target_zone), FadeOut(balance), FadeOut(pivot), run_time=1.35)
        self.play(
            AnimationGroup(Transform(green, final_green.copy()), Transform(blue, final_blue.copy()), Transform(purple, final_purple.copy()), lag_ratio=0.08),
            run_time=2.7,
            rate_func=smooth,
        )
        self.play(FadeIn(terminal), run_time=1.2)
        self.wait(6.1)


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
