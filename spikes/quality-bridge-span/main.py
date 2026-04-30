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
    Rectangle,
    Scene,
    Transform,
    VGroup,
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
WHITE = "#ffffff"
GRAY_100 = "#e7e7e7"
GRAY_200 = "#cfcfcf"


class _Args(argparse.Namespace):
    quality: str


def parse_args() -> _Args:
    parser = argparse.ArgumentParser(description="Render the quality-bridge-span spike.")
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
        "QualityBridgeSpanScene",
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


class QualityBridgeSpanScene(Scene):
    def construct(self) -> None:
        self.camera.background_color = WHITE

        frame = Rectangle(width=12.6, height=5.55, stroke_color=GRAY_200, stroke_width=2, fill_color=WHITE, fill_opacity=0)
        source_zone = Rectangle(width=3.85, height=3.82, stroke_width=0, fill_color=GRAY_100, fill_opacity=0.22).move_to(LEFT * 3.42)
        target_zone = Rectangle(width=3.95, height=3.82, stroke_width=0, fill_color=GRAY_100, fill_opacity=0.26).move_to(RIGHT * 3.08)

        green = slab(PRIMARY_GREEN, 2.44, 0.82).move_to(LEFT * 3.58 + UP * 0.76)
        blue = slab(PRIMARY_BLUE, 1.62, 0.68).move_to(LEFT * 2.92 + DOWN * 0.08)
        purple = slab(PRIMARY_PURPLE, 1.02, 0.46).move_to(LEFT * 2.52 + DOWN * 0.9)
        source = VGroup(green, blue, purple)

        bridge_top = Rectangle(width=4.42, height=0.14, stroke_width=0, fill_color=PRIMARY_ORANGE, fill_opacity=1).move_to(RIGHT * 0.42 + UP * 0.3)
        bridge_bottom = Rectangle(width=4.42, height=0.14, stroke_width=0, fill_color=PRIMARY_ORANGE, fill_opacity=1).move_to(RIGHT * 0.42 + DOWN * 0.3)
        bridge_entry = Rectangle(width=0.14, height=0.84, stroke_width=0, fill_color=PRIMARY_ORANGE, fill_opacity=0.72).move_to(LEFT * 1.79)
        bridge_exit = Rectangle(width=0.14, height=0.84, stroke_width=0, fill_color=PRIMARY_ORANGE, fill_opacity=0.72).move_to(RIGHT * 2.63)
        bridge = VGroup(bridge_top, bridge_bottom, bridge_entry, bridge_exit)
        bridge.set_z_index(1)

        target_slot_green = Rectangle(width=1.64, height=0.82, stroke_color=GRAY_200, stroke_width=2, fill_opacity=0).move_to(RIGHT * 2.58 + UP * 0.48)
        target_slot_blue = Rectangle(width=0.88, height=0.62, stroke_color=GRAY_200, stroke_width=2, fill_opacity=0).move_to(RIGHT * 3.7 + DOWN * 0.22)
        target_slot_purple = Rectangle(width=0.5, height=0.4, stroke_color=GRAY_200, stroke_width=2, fill_opacity=0).move_to(RIGHT * 2.98 + DOWN * 1.02)
        target_slots = VGroup(target_slot_green, target_slot_blue, target_slot_purple).set_opacity(0.55)

        accent = Circle(radius=0.14, stroke_width=0, fill_color=PRIMARY_RED, fill_opacity=1).move_to(LEFT * 1.82)
        accent.set_z_index(4)

        green_entry = slab(PRIMARY_GREEN, 1.72, 0.46).move_to(LEFT * 0.92)
        green_bridge = slab(PRIMARY_GREEN, 1.82, 0.46).move_to(RIGHT * 0.48)
        green_exit = slab(PRIMARY_GREEN, 1.62, 0.58).move_to(RIGHT * 2.52 + UP * 0.28)
        blue_wait = slab(PRIMARY_BLUE, 1.38, 0.58).move_to(LEFT * 2.86 + DOWN * 0.28)
        purple_wait = slab(PRIMARY_PURPLE, 0.86, 0.4).move_to(LEFT * 2.24 + DOWN * 1.06)
        blue_release = slab(PRIMARY_BLUE, 1.1, 0.58).move_to(RIGHT * 1.34 + DOWN * 0.9)
        purple_release = slab(PRIMARY_PURPLE, 0.64, 0.38).move_to(RIGHT * 2.18 + DOWN * 1.26)

        final_green = Circle(radius=0.82, stroke_width=0, fill_color=PRIMARY_GREEN, fill_opacity=1).move_to(RIGHT * 2.54 + UP * 0.48)
        final_blue = Circle(radius=0.46, stroke_width=0, fill_color=PRIMARY_BLUE, fill_opacity=1).move_to(RIGHT * 3.56 + DOWN * 0.18)
        final_purple = Circle(radius=0.25, stroke_width=0, fill_color=PRIMARY_PURPLE, fill_opacity=1).move_to(RIGHT * 2.86 + DOWN * 0.94)
        centered_target_zone = Rectangle(width=3.95, height=3.82, stroke_width=0, fill_color=GRAY_100, fill_opacity=0.26).move_to(RIGHT * 0.72)
        centered_green = Circle(radius=0.82, stroke_width=0, fill_color=PRIMARY_GREEN, fill_opacity=1).move_to(RIGHT * 0.18 + UP * 0.48)
        centered_blue = Circle(radius=0.46, stroke_width=0, fill_color=PRIMARY_BLUE, fill_opacity=1).move_to(RIGHT * 1.2 + DOWN * 0.18)
        centered_purple = Circle(radius=0.25, stroke_width=0, fill_color=PRIMARY_PURPLE, fill_opacity=1).move_to(RIGHT * 0.5 + DOWN * 0.94)

        for actor in source:
            actor.set_z_index(3)
        self.add(frame, source_zone, target_zone, source, target_slots)
        self.wait(2.4)
        self.play(FadeIn(bridge), FadeIn(accent), run_time=1.2)
        self.wait(0.8)
        self.play(accent.animate.move_to(LEFT * 0.96), run_time=1.4, rate_func=smooth)
        self.play(Transform(green, green_entry.copy()), run_time=1.6, rate_func=smooth)
        self.wait(1.0)
        self.play(
            AnimationGroup(
                Transform(green, green_bridge.copy()),
                Transform(blue, blue_wait.copy()),
                Transform(purple, purple_wait.copy()),
                accent.animate.move_to(RIGHT * 0.46),
                lag_ratio=0.08,
            ),
            run_time=2.4,
            rate_func=smooth,
        )
        self.wait(1.8)
        self.play(accent.animate.move_to(RIGHT * 2.34), run_time=1.7, rate_func=smooth)
        self.play(Transform(green, green_exit.copy()), run_time=1.5, rate_func=smooth)
        self.wait(0.9)
        self.play(
            AnimationGroup(
                Transform(green, final_green.copy()),
                Transform(blue, blue_release.copy()),
                Transform(purple, purple_release.copy()),
                lag_ratio=0.18,
            ),
            run_time=2.1,
            rate_func=smooth,
        )
        self.play(
            AnimationGroup(
                Transform(target_zone, centered_target_zone.copy()),
                Transform(green, centered_green.copy()),
                Transform(blue, centered_blue.copy()),
                Transform(purple, centered_purple.copy()),
                FadeOut(bridge),
                FadeOut(target_slots),
                FadeOut(source_zone),
                accent.animate.move_to(centered_green.get_center()).set_fill(PRIMARY_RED, opacity=0.4),
                lag_ratio=0.05,
            ),
            run_time=2.2,
            rate_func=smooth,
        )
        self.play(FadeOut(accent), run_time=0.7)
        self.wait(6.2)


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
