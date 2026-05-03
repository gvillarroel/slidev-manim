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
    Line,
    Rectangle,
    Scene,
    Transform,
    VGroup,
    WHITE,
    config,
    smooth,
)

config.transparent = True
config.background_opacity = 0.0

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
    parser = argparse.ArgumentParser(description="Render the quality-ramp-lift spike.")
    parser.add_argument("--quality", choices=("low", "medium", "high", "production", "4k"), default="medium")
    return parser.parse_args(namespace=_Args())


def quality_flag(quality: str) -> str:
    return {"low": "-ql", "medium": "-qm", "high": "-qh", "production": "-qp", "4k": "-qk"}[quality]


def output_paths() -> tuple[Path, Path]:
    return OUTPUT_DIR / f"{SPIKE_NAME}.webm", OUTPUT_DIR / f"{SPIKE_NAME}.png"


def render_command(args: _Args, stem: str, poster: bool) -> list[str]:
    STAGING_DIR.mkdir(parents=True, exist_ok=True)
    command = [
        sys.executable, "-m", "manim", "render", quality_flag(args.quality), "-r", "1600,900", "--format", "webm", "--transparent",
        "-o", stem, "--media_dir", str(STAGING_DIR), str(Path(__file__).resolve()), "QualityRampLiftScene",
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


def slot(width: float, height: float) -> Rectangle:
    return Rectangle(width=width, height=height, stroke_color=GRAY_200, stroke_width=2, fill_color=GRAY_100, fill_opacity=0.1)


def corner_brackets(width: float, height: float, length: float, color: str) -> VGroup:
    x = width / 2
    y = height / 2
    parts: list[Line] = []
    for sx in (-1, 1):
        for sy in (-1, 1):
            parts.append(Line((sx * (x - length), sy * y, 0), (sx * x, sy * y, 0), color=color, stroke_width=6))
            parts.append(Line((sx * x, sy * (y - length), 0), (sx * x, sy * y, 0), color=color, stroke_width=6))
    return VGroup(*parts)


class QualityRampLiftScene(Scene):
    def construct(self) -> None:
        self.camera.background_color = WHITE
        self.camera.background_opacity = 0.0

        source_zone = slot(3.7, 3.35).move_to(LEFT * 4.0 + DOWN * 0.1)
        target_slot = slot(3.95, 3.35).move_to(RIGHT * 2.9 + UP * 0.18)
        entry_slot = Rectangle(width=2.0, height=0.62, stroke_color=GRAY_200, stroke_width=2, fill_opacity=0).move_to(
            RIGHT * 0.35 + DOWN * 1.1
        )
        landing_slot = Circle(radius=1.02, stroke_color=GRAY_200, stroke_width=2, fill_color=GRAY_100, fill_opacity=0.08).move_to(
            RIGHT * 2.4 + UP * 0.8
        )

        ramp_angle = 0.43
        ramp_center = ORIGIN + RIGHT * 0.78 + DOWN * 0.25
        ramp_lower = Line(LEFT * 1.0 + DOWN * 0.72, RIGHT * 2.6 + UP * 0.83, color=GRAY_200, stroke_width=6)
        ramp_upper = ramp_lower.copy().shift(UP * 0.32)
        ramp = VGroup(ramp_lower, ramp_upper)
        pivot = Circle(radius=0.16, stroke_width=0, fill_color=PRIMARY_RED, fill_opacity=1).move_to(LEFT * 0.78 + DOWN * 0.62)

        green = slab(PRIMARY_GREEN, 1.9, 0.72).move_to(LEFT * 4.35 + UP * 0.62)
        blue = slab(PRIMARY_BLUE, 1.2, 0.54).move_to(LEFT * 3.65 + DOWN * 0.18)
        purple = slab(PRIMARY_PURPLE, 0.82, 0.42).move_to(LEFT * 3.18 + DOWN * 0.92)
        source = VGroup(green, blue, purple)
        scaffold = VGroup(source_zone, target_slot, entry_slot, landing_slot, ramp, pivot)

        green_on_ramp = slab(PRIMARY_GREEN, 1.48, 0.48).rotate(ramp_angle).move_to(ramp_center + RIGHT * 0.25 + UP * 0.48)
        lift_core = Circle(radius=0.14, stroke_width=0, fill_color=PRIMARY_RED, fill_opacity=1).move_to(
            ramp_center + LEFT * 0.45 + DOWN * 0.44
        )
        blue_ready = slab(PRIMARY_BLUE, 1.02, 0.42).move_to(RIGHT * 0.1 + DOWN * 1.42)
        purple_ready = slab(PRIMARY_PURPLE, 0.72, 0.36).move_to(RIGHT * 1.84 + DOWN * 1.0)

        green_lifted = slab(PRIMARY_GREEN, 1.42, 0.46).rotate(ramp_angle).move_to(RIGHT * 1.05 + UP * 1.05)
        blue_support = slab(PRIMARY_BLUE, 0.98, 0.42).move_to(RIGHT * 0.42 + DOWN * 0.34)
        purple_support = slab(PRIMARY_PURPLE, 0.68, 0.34).move_to(RIGHT * 2.28 + UP * 1.72)

        final_green = Circle(radius=1.08, stroke_width=0, fill_color=PRIMARY_GREEN, fill_opacity=1).move_to(LEFT * 0.18 + UP * 0.24)
        final_blue = Circle(radius=0.5, stroke_width=0, fill_color=PRIMARY_BLUE, fill_opacity=1).move_to(RIGHT * 1.65 + DOWN * 0.08)
        final_purple = Circle(radius=0.3, stroke_width=0, fill_color=PRIMARY_PURPLE, fill_opacity=1).move_to(RIGHT * 0.04 + DOWN * 1.48)
        final_cluster = VGroup(final_green, final_blue, final_purple)
        brackets = corner_brackets(4.25, 3.25, 0.32, PRIMARY_RED).move_to(final_cluster.get_center())

        self.add(scaffold, source)
        self.wait(2.7)

        self.play(Transform(green, green_on_ramp.copy()), FadeIn(lift_core), run_time=2.2, rate_func=smooth)
        self.wait(1.35)
        self.play(
            FadeOut(source_zone),
            FadeOut(entry_slot),
            FadeOut(target_slot),
            FadeOut(landing_slot),
            Transform(blue, blue_ready.copy()),
            Transform(purple, purple_ready.copy()),
            run_time=0.75,
            rate_func=smooth,
        )

        self.play(
            lift_core.animate.move_to(ramp_center + RIGHT * 1.15 + UP * 0.12),
            Transform(green, green_lifted.copy()),
            run_time=2.1,
            rate_func=smooth,
        )
        self.wait(1.2)
        self.play(FadeOut(lift_core), run_time=0.75)

        self.wait(0.9)

        self.play(
            AnimationGroup(
                Transform(blue, blue_support.copy()),
                Transform(purple, purple_support.copy()),
                lag_ratio=0.18,
            ),
            run_time=2.2,
            rate_func=smooth,
        )
        self.wait(1.0)

        self.play(
            FadeOut(ramp),
            FadeOut(pivot),
            green.animate.shift(LEFT * 0.9 + DOWN * 0.35),
            blue.animate.shift(LEFT * 0.9 + DOWN * 0.35),
            purple.animate.shift(LEFT * 0.9 + DOWN * 0.35),
            run_time=1.25,
        )
        self.play(
            AnimationGroup(
                Transform(green, final_green.copy()),
                FadeOut(blue),
                FadeOut(purple),
                lag_ratio=0.06,
            ),
            run_time=1.7,
            rate_func=smooth,
        )
        self.play(FadeIn(final_blue), FadeIn(final_purple), FadeIn(brackets), run_time=0.9)
        self.wait(6.4)


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
