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
GRAY_600 = "#696969"


class _Args(argparse.Namespace):
    quality: str


def parse_args() -> _Args:
    parser = argparse.ArgumentParser(description="Render the quality-slot-docking spike.")
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
        "QualitySlotDockingScene",
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


class QualitySlotDockingScene(Scene):
    def construct(self) -> None:
        self.camera.background_color = WHITE

        frame = Rectangle(width=12.9, height=5.8, stroke_color=GRAY_200, stroke_width=2, fill_color=WHITE, fill_opacity=0)
        source_zone = Rectangle(width=3.95, height=4.1, stroke_width=0, fill_color=GRAY_100, fill_opacity=0.2).move_to(LEFT * 3.15)
        target_zone = Rectangle(width=4.2, height=4.1, stroke_width=0, fill_color=GRAY_100, fill_opacity=0.26).move_to(RIGHT * 2.95)

        rail_top = Line(RIGHT * 1.54 + UP * 0.62, RIGHT * 3.28 + UP * 0.62, color=GRAY_600, stroke_width=5)
        rail_bottom = Line(RIGHT * 1.54 + DOWN * 0.48, RIGHT * 3.28 + DOWN * 0.48, color=GRAY_600, stroke_width=5)
        rail_back = Line(RIGHT * 3.28 + DOWN * 0.48, RIGHT * 3.28 + UP * 0.62, color=GRAY_600, stroke_width=5)
        slot_shell = VGroup(rail_top, rail_bottom, rail_back)

        green = slab(PRIMARY_GREEN, 2.72, 0.92).move_to(LEFT * 3.28 + UP * 0.76)
        blue = slab(PRIMARY_BLUE, 1.78, 0.72).move_to(LEFT * 2.18 + DOWN * 0.04)
        purple = slab(PRIMARY_PURPLE, 1.12, 0.54).move_to(LEFT * 1.68 + DOWN * 0.92)
        source = VGroup(green, blue, purple)

        guide = Line(LEFT * 0.72 + UP * 0.02, RIGHT * 1.52 + UP * 0.02, color=PRIMARY_ORANGE, stroke_width=5).set_stroke(opacity=0.45)
        accent = Circle(radius=0.12, stroke_width=0, fill_color=PRIMARY_YELLOW, fill_opacity=1).move_to(guide.get_start())

        green_approach = slab(PRIMARY_GREEN, 2.0, 0.72).move_to(RIGHT * 1.56 + UP * 0.08)
        blue_approach = slab(PRIMARY_BLUE, 1.28, 0.6).move_to(RIGHT * 0.42 + DOWN * 0.66)
        purple_approach = slab(PRIMARY_PURPLE, 0.84, 0.46).move_to(RIGHT * 0.92 + UP * 0.84)

        pressure_top = Line(RIGHT * 1.48 + UP * 0.38, RIGHT * 1.48 + UP * 0.7, color=PRIMARY_RED, stroke_width=6)
        pressure_bottom = Line(RIGHT * 1.48 + DOWN * 0.56, RIGHT * 1.48 + DOWN * 0.24, color=PRIMARY_RED, stroke_width=6)
        pressure = VGroup(pressure_top, pressure_bottom)

        green_dock = slab(PRIMARY_GREEN, 1.34, 0.46).move_to(RIGHT * 2.42 + UP * 0.07)
        blue_hold = slab(PRIMARY_BLUE, 1.32, 0.54).move_to(RIGHT * 1.52 + DOWN * 0.82)
        purple_hold = slab(PRIMARY_PURPLE, 0.82, 0.42).move_to(RIGHT * 3.08 + DOWN * 0.86)

        final_green = Circle(radius=0.84, stroke_width=0, fill_color=PRIMARY_GREEN, fill_opacity=1).move_to(RIGHT * 1.04 + UP * 0.42)
        final_blue = Circle(radius=0.48, stroke_width=0, fill_color=PRIMARY_BLUE, fill_opacity=1).move_to(RIGHT * 2.16 + DOWN * 0.08)
        final_purple = Circle(radius=0.26, stroke_width=0, fill_color=PRIMARY_PURPLE, fill_opacity=1).move_to(RIGHT * 1.36 + DOWN * 1.02)

        self.add(frame, source_zone, target_zone, guide, slot_shell, source, accent)
        self.wait(2.6)
        self.play(
            guide.animate.set_stroke(width=7, opacity=1),
            accent.animate.scale(1.18),
            slot_shell.animate.set_stroke(width=6),
            run_time=1.2,
            rate_func=smooth,
        )
        self.play(accent.animate.move_to(RIGHT * 1.24 + UP * 0.02), run_time=2.0, rate_func=smooth)
        self.play(
            AnimationGroup(
                Transform(green, green_approach.copy()),
                Transform(blue, blue_approach.copy()),
                Transform(purple, purple_approach.copy()),
                lag_ratio=0.12,
            ),
            run_time=3.2,
            rate_func=smooth,
        )
        self.wait(1.2)
        self.play(FadeIn(pressure), run_time=0.8)
        self.play(
            AnimationGroup(
                Transform(green, green_dock.copy()),
                Transform(blue, blue_hold.copy()),
                Transform(purple, purple_hold.copy()),
                accent.animate.move_to(RIGHT * 2.42 + UP * 0.07).set_fill(PRIMARY_RED, opacity=1),
                lag_ratio=0.1,
            ),
            run_time=3.2,
            rate_func=smooth,
        )
        self.wait(2.4)
        self.play(
            FadeOut(guide),
            FadeOut(pressure),
            slot_shell.animate.set_stroke(opacity=0.35, width=4),
            run_time=1.2,
            rate_func=smooth,
        )
        self.play(
            FadeOut(source_zone),
            FadeOut(slot_shell),
            target_zone.animate.move_to(RIGHT * 1.25).scale(0.9).set_fill(GRAY_100, opacity=0.22),
            AnimationGroup(
                Transform(green, final_green.copy()),
                Transform(blue, final_blue.copy()),
                Transform(purple, final_purple.copy()),
                lag_ratio=0.08,
            ),
            accent.animate.move_to(RIGHT * 1.6 + DOWN * 0.14).scale(0.82),
            run_time=3.8,
            rate_func=smooth,
        )
        self.play(FadeOut(accent), run_time=0.8)
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
