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
    MoveAlongPath,
    Rectangle,
    Scene,
    Transform,
    VGroup,
    WHITE,
    smooth,
    there_and_back,
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


class _Args(argparse.Namespace):
    quality: str


def parse_args() -> _Args:
    parser = argparse.ArgumentParser(description="Render the quality-aperture-open spike.")
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
        "QualityApertureOpenScene",
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


def slab(color: str, width: float, height: float, opacity: float = 1) -> Rectangle:
    return Rectangle(width=width, height=height, stroke_width=0, fill_color=color, fill_opacity=opacity)


class QualityApertureOpenScene(Scene):
    def construct(self) -> None:
        self.camera.background_color = WHITE

        frame = Rectangle(width=12.9, height=5.8, stroke_color=GRAY_200, stroke_width=2, fill_color=WHITE, fill_opacity=0)
        source_zone = Rectangle(width=4.1, height=4.25, stroke_width=0, fill_color=GRAY_100, fill_opacity=0.22).move_to(LEFT * 3.0)
        target_zone = Rectangle(width=4.3, height=4.25, stroke_width=0, fill_color=GRAY_100, fill_opacity=0.28).move_to(RIGHT * 2.7)

        source = VGroup(
            slab(PRIMARY_GREEN, 2.55, 0.9).move_to(LEFT * 3.3 + UP * 0.7),
            slab(PRIMARY_BLUE, 1.84, 0.82).move_to(LEFT * 2.16 + DOWN * 0.08),
            slab(PRIMARY_PURPLE, 1.4, 0.68).move_to(LEFT * 1.6 + DOWN * 1.0),
        )

        guide = Line(LEFT * 0.85 + DOWN * 0.02, RIGHT * 1.22 + DOWN * 0.02, color=PRIMARY_ORANGE, stroke_width=6)
        accent = Circle(radius=0.12, stroke_width=0, fill_color=PRIMARY_YELLOW, fill_opacity=1).move_to(guide.get_start())

        target_slots = VGroup(
            Rectangle(width=2.25, height=0.78, stroke_color=GRAY_200, stroke_width=2, fill_opacity=0).move_to(RIGHT * 2.42 + UP * 0.24),
            Rectangle(width=1.56, height=0.58, stroke_color=GRAY_200, stroke_width=2, fill_opacity=0).move_to(RIGHT * 3.4 + DOWN * 0.2),
            Rectangle(width=1.0, height=0.4, stroke_color=GRAY_200, stroke_width=2, fill_opacity=0).move_to(RIGHT * 2.78 + DOWN * 0.82),
        ).set_opacity(0.45)

        shutter_top = slab(GRAY_200, 3.75, 1.32, opacity=0.78).move_to(RIGHT * 2.72 + UP * 0.62)
        shutter_bottom = slab(GRAY_200, 3.75, 1.32, opacity=0.78).move_to(RIGHT * 2.72 + DOWN * 0.62)

        reveal_green = slab(PRIMARY_GREEN, 2.12, 0.72).move_to(RIGHT * 2.42 + UP * 0.24)
        reveal_blue = slab(PRIMARY_BLUE, 1.52, 0.62).move_to(RIGHT * 3.4 + DOWN * 0.2)
        reveal_purple = slab(PRIMARY_PURPLE, 0.98, 0.44).move_to(RIGHT * 2.78 + DOWN * 0.82)

        final_green = Circle(radius=0.86, stroke_width=0, fill_color=PRIMARY_GREEN, fill_opacity=1).move_to(RIGHT * 1.24 + UP * 0.44)
        final_blue = Circle(radius=0.5, stroke_width=0, fill_color=PRIMARY_BLUE, fill_opacity=1).move_to(RIGHT * 2.38 + DOWN * 0.02)
        final_purple = Circle(radius=0.26, stroke_width=0, fill_color=PRIMARY_PURPLE, fill_opacity=1).move_to(RIGHT * 1.66 + DOWN * 0.98)

        self.add(frame, source_zone, target_zone, target_slots, source)
        self.wait(2.6)
        self.play(FadeIn(guide), FadeIn(accent), run_time=0.8)
        self.play(MoveAlongPath(accent, guide), run_time=1.8, rate_func=smooth)
        self.play(FadeIn(shutter_top), FadeIn(shutter_bottom), target_slots.animate.set_opacity(0.18), run_time=1.0)
        self.play(
            AnimationGroup(
                Transform(source[0], reveal_green.copy()),
                Transform(source[1], reveal_blue.copy()),
                Transform(source[2], reveal_purple.copy()),
                lag_ratio=0.06,
            ),
            run_time=2.4,
            rate_func=smooth,
        )
        self.wait(1.0)
        self.play(
            shutter_top.animate.shift(UP * 1.15),
            shutter_bottom.animate.shift(DOWN * 1.15),
            target_slots.animate.set_opacity(0.34),
            run_time=2.8,
            rate_func=smooth,
        )
        self.wait(1.2)
        self.play(
            FadeOut(shutter_top),
            FadeOut(shutter_bottom),
            FadeOut(guide),
            FadeOut(target_slots),
            source_zone.animate.set_opacity(0),
            run_time=1.0,
        )
        self.play(
            AnimationGroup(
                Transform(source[0], final_green.copy()),
                Transform(source[1], final_blue.copy()),
                Transform(source[2], final_purple.copy()),
                accent.animate.move_to(RIGHT * 1.62 + DOWN * 0.02).set_fill(PRIMARY_RED, opacity=1),
                target_zone.animate.move_to(RIGHT * 1.72),
                lag_ratio=0.06,
            ),
            run_time=2.6,
            rate_func=smooth,
        )
        self.play(
            AnimationGroup(*(item.animate.scale(1.05) for item in source), lag_ratio=0.16),
            run_time=1.2,
            rate_func=there_and_back,
        )
        self.play(FadeOut(accent), run_time=0.8)
        self.wait(6.8)


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
