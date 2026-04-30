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
    Create,
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
GRAY_300 = "#b5b5b5"


class _Args(argparse.Namespace):
    quality: str


def parse_args() -> _Args:
    parser = argparse.ArgumentParser(description="Render the quality-edge-tension spike.")
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
        "QualityEdgeTensionScene",
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


class QualityEdgeTensionScene(Scene):
    def construct(self) -> None:
        self.camera.background_color = WHITE

        frame = Rectangle(width=12.8, height=5.65, stroke_color=GRAY_200, stroke_width=2, fill_color=WHITE, fill_opacity=0)
        left_soft = Rectangle(width=3.8, height=4.25, stroke_width=0, fill_color=GRAY_100, fill_opacity=0.24).move_to(LEFT * 3.58)
        right_soft = Rectangle(width=2.55, height=4.2, stroke_width=0, fill_color=GRAY_100, fill_opacity=0.34).move_to(RIGHT * 4.9 + DOWN * 0.04)
        pressure_wall = Line(RIGHT * 5.96 + DOWN * 1.96, RIGHT * 5.96 + UP * 1.96, color=PRIMARY_RED, stroke_width=8).set_opacity(0.42)

        source = VGroup(
            slab(PRIMARY_GREEN, 1.95, 0.86).move_to(LEFT * 4.08 + UP * 0.86),
            slab(PRIMARY_BLUE, 1.82, 0.8).move_to(LEFT * 2.78 + DOWN * 0.02),
            slab(PRIMARY_PURPLE, 1.62, 0.74).move_to(LEFT * 1.48 + DOWN * 0.9),
        )
        compressed = VGroup(
            slab(PRIMARY_GREEN, 1.1, 0.78).move_to(RIGHT * 0.35 + UP * 0.52),
            slab(PRIMARY_BLUE, 1.0, 0.72).move_to(RIGHT * 0.54 + DOWN * 0.16),
            slab(PRIMARY_PURPLE, 0.86, 0.66).move_to(RIGHT * 0.76 + DOWN * 0.76),
        )
        targets = VGroup(
            Circle(radius=0.86, stroke_width=0, fill_color=PRIMARY_GREEN, fill_opacity=1).move_to(RIGHT * 5.02 + UP * 0.46),
            Circle(radius=0.52, stroke_width=0, fill_color=PRIMARY_BLUE, fill_opacity=1).move_to(RIGHT * 4.2 + DOWN * 0.48),
            Circle(radius=0.29, stroke_width=0, fill_color=PRIMARY_PURPLE, fill_opacity=1).move_to(RIGHT * 4.78 + DOWN * 1.18),
        )
        overshoot_targets = VGroup(
            Circle(radius=0.9, stroke_width=0, fill_color=PRIMARY_GREEN, fill_opacity=1).move_to(RIGHT * 5.28 + UP * 0.47),
            Circle(radius=0.55, stroke_width=0, fill_color=PRIMARY_BLUE, fill_opacity=1).move_to(RIGHT * 4.44 + DOWN * 0.48),
            Circle(radius=0.3, stroke_width=0, fill_color=PRIMARY_PURPLE, fill_opacity=1).move_to(RIGHT * 4.98 + DOWN * 1.15),
        )
        target_slots = VGroup(
            Circle(radius=0.9, stroke_color=GRAY_300, stroke_width=3, fill_opacity=0).move_to(targets[0]),
            Circle(radius=0.55, stroke_color=GRAY_300, stroke_width=3, fill_opacity=0).move_to(targets[1]),
            Circle(radius=0.3, stroke_color=GRAY_300, stroke_width=3, fill_opacity=0).move_to(targets[2]),
        ).set_opacity(0.36)

        guide = Line(LEFT * 0.45 + DOWN * 0.06, RIGHT * 5.25 + DOWN * 0.06, color=PRIMARY_ORANGE, stroke_width=7)
        accent = Circle(radius=0.12, stroke_width=0, fill_color=PRIMARY_YELLOW, fill_opacity=1).move_to(guide.get_start())
        settle_point = RIGHT * 5.42 + DOWN * 0.06

        self.add(frame, left_soft, right_soft, source, target_slots, pressure_wall)
        self.wait(2.6)
        self.play(Create(guide), FadeIn(accent), pressure_wall.animate.set_opacity(0.76), run_time=1.4)
        self.wait(1.2)
        self.play(MoveAlongPath(accent, guide), run_time=2.4, rate_func=smooth)
        self.wait(0.7)
        self.play(
            AnimationGroup(
                Transform(source[0], compressed[0].copy()),
                Transform(source[1], compressed[1].copy()),
                Transform(source[2], compressed[2].copy()),
                lag_ratio=0.07,
            ),
            run_time=2.8,
            rate_func=smooth,
        )
        self.wait(1.4)
        self.play(
            AnimationGroup(
                Transform(source[0], overshoot_targets[0].copy()),
                Transform(source[1], overshoot_targets[1].copy()),
                Transform(source[2], overshoot_targets[2].copy()),
                lag_ratio=0.08,
            ),
            run_time=2.7,
            rate_func=smooth,
        )
        self.wait(2.4)
        self.play(
            AnimationGroup(
                source[0].animate.move_to(targets[0].get_center()).scale(targets[0].width / source[0].width),
                source[1].animate.move_to(targets[1].get_center()).scale(targets[1].width / source[1].width),
                source[2].animate.move_to(targets[2].get_center()).scale(targets[2].width / source[2].width),
                lag_ratio=0.04,
            ),
            run_time=1.6,
            rate_func=smooth,
        )
        self.play(FadeOut(guide), FadeOut(target_slots), FadeOut(left_soft), run_time=1.0)
        self.play(accent.animate.move_to(settle_point).set_fill(PRIMARY_RED, opacity=1), pressure_wall.animate.set_opacity(0.28), run_time=1.1)
        for item in source:
            self.play(item.animate.scale(1.06), run_time=0.38, rate_func=there_and_back)
        self.play(FadeOut(accent), FadeOut(pressure_wall), run_time=1.1)
        self.wait(7.0)


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
