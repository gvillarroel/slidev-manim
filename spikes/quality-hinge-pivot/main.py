#!/usr/bin/env -S uv run --script
# /// script
# dependencies = [
#   "manim>=0.20.0",
# ]
# ///

from __future__ import annotations

import argparse
import math
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
    Rotate,
    RoundedRectangle,
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
    parser = argparse.ArgumentParser(description="Render the quality-hinge-pivot spike.")
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
        "QualityHingePivotScene",
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
    return RoundedRectangle(width=width, height=height, corner_radius=0.32, stroke_width=0, fill_color=color, fill_opacity=1)


class QualityHingePivotScene(Scene):
    def construct(self) -> None:
        self.camera.background_color = WHITE

        frame = RoundedRectangle(width=12.9, height=5.8, corner_radius=0.34, stroke_color=GRAY_200, stroke_width=2, fill_color=WHITE, fill_opacity=0)
        source_zone = RoundedRectangle(width=4.0, height=4.2, corner_radius=0.35, stroke_width=0, fill_color=GRAY_100, fill_opacity=0.22).move_to(LEFT * 3.05)
        target_zone = RoundedRectangle(width=4.25, height=4.35, corner_radius=0.35, stroke_width=0, fill_color=GRAY_100, fill_opacity=0.28).move_to(RIGHT * 2.85)

        hinge = Circle(radius=0.13, stroke_width=0, fill_color=PRIMARY_ORANGE, fill_opacity=1).move_to(LEFT * 2.4 + UP * 0.25)
        arm = slab(PRIMARY_GREEN, 3.2, 0.86).move_to(LEFT * 3.35 + UP * 0.42)
        blue = slab(PRIMARY_BLUE, 1.7, 0.8).move_to(LEFT * 1.8 + DOWN * 0.42)
        purple = slab(PRIMARY_PURPLE, 1.3, 0.68).move_to(LEFT * 2.08 + DOWN * 1.35)
        source = VGroup(arm, blue, purple)

        guide_arc = Line(LEFT * 1.0 + UP * 0.38, RIGHT * 0.86 + UP * 0.16, color=PRIMARY_ORANGE, stroke_width=5)
        accent = Circle(radius=0.12, stroke_width=0, fill_color=PRIMARY_YELLOW, fill_opacity=1).move_to(guide_arc.get_start())

        pivot_target = slab(PRIMARY_GREEN, 3.0, 0.82).move_to(RIGHT * 1.35 + UP * 0.92).rotate(-math.pi / 7)
        final_main = Circle(radius=0.82, stroke_width=0, fill_color=PRIMARY_GREEN, fill_opacity=1).move_to(RIGHT * 2.62 + UP * 0.44)
        final_blue = Circle(radius=0.52, stroke_width=0, fill_color=PRIMARY_BLUE, fill_opacity=1).move_to(RIGHT * 3.72 + DOWN * 0.12)
        final_purple = Circle(radius=0.28, stroke_width=0, fill_color=PRIMARY_PURPLE, fill_opacity=1).move_to(RIGHT * 3.02 + DOWN * 1.06)

        self.add(frame, source_zone, target_zone)
        self.play(FadeIn(hinge), FadeIn(source, lag_ratio=0.08), run_time=0.72)
        self.play(FadeIn(guide_arc), run_time=0.14)
        self.play(MoveAlongPath(accent, guide_arc), run_time=0.34)
        self.play(
            AnimationGroup(
                Rotate(arm, angle=-math.pi / 5.5, about_point=hinge.get_center()),
                blue.animate.move_to(LEFT * 0.75 + DOWN * 0.16),
                purple.animate.move_to(LEFT * 0.2 + DOWN * 0.95),
                lag_ratio=0.05,
            ),
            run_time=0.7,
            rate_func=smooth,
        )
        self.play(Transform(arm, pivot_target.copy()), run_time=0.24, rate_func=smooth)
        self.play(FadeOut(hinge), FadeOut(guide_arc), run_time=0.12)
        self.play(
            AnimationGroup(
                Transform(arm, final_main.copy()),
                Transform(blue, final_blue.copy()),
                Transform(purple, final_purple.copy()),
                lag_ratio=0.08,
            ),
            run_time=0.82,
            rate_func=smooth,
        )
        self.play(accent.animate.move_to(RIGHT * 3.02 + DOWN * 0.02).set_fill(PRIMARY_RED, opacity=1), run_time=0.18)
        for item in source:
            self.play(item.animate.scale(1.06), run_time=0.12, rate_func=there_and_back)
        self.play(FadeOut(accent), run_time=0.14)
        self.wait(0.25)


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
