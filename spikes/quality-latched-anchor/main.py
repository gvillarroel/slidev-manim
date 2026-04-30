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
    RoundedRectangle,
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


class _Args(argparse.Namespace):
    quality: str


def parse_args() -> _Args:
    parser = argparse.ArgumentParser(description="Render the quality-latched-anchor spike.")
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
        "QualityLatchedAnchorScene",
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


class QualityLatchedAnchorScene(Scene):
    def construct(self) -> None:
        self.camera.background_color = WHITE

        frame = RoundedRectangle(width=12.9, height=5.8, corner_radius=0.34, stroke_color=GRAY_200, stroke_width=2, fill_color=WHITE, fill_opacity=0)
        source_zone = RoundedRectangle(width=4.15, height=4.2, corner_radius=0.35, stroke_width=0, fill_color=GRAY_100, fill_opacity=0.23).move_to(LEFT * 3.0)
        target_zone = RoundedRectangle(width=4.15, height=4.2, corner_radius=0.35, stroke_width=0, fill_color=GRAY_100, fill_opacity=0.28).move_to(RIGHT * 2.9)

        green = slab(PRIMARY_GREEN, 2.52, 0.9).move_to(LEFT * 3.28 + UP * 0.72)
        blue = slab(PRIMARY_BLUE, 1.84, 0.82).move_to(LEFT * 2.12 + DOWN * 0.02)
        purple = slab(PRIMARY_PURPLE, 1.36, 0.66).move_to(LEFT * 1.58 + DOWN * 0.96)
        source = VGroup(green, blue, purple)

        guide = Line(LEFT * 0.95 + DOWN * 0.02, RIGHT * 0.18 + DOWN * 0.02, color=PRIMARY_ORANGE, stroke_width=6)
        accent = Circle(radius=0.12, stroke_width=0, fill_color=PRIMARY_YELLOW, fill_opacity=1).move_to(guide.get_start())
        latch_outer = Circle(radius=0.24, stroke_width=0, fill_color=PRIMARY_ORANGE, fill_opacity=1)
        latch_inner = Circle(radius=0.11, stroke_width=0, fill_color=WHITE, fill_opacity=1)
        latch = VGroup(latch_outer, latch_inner).move_to(RIGHT * 0.9 + UP * 0.28)

        green_latch = slab(PRIMARY_GREEN, 1.92, 0.68).move_to(latch.get_center() + RIGHT * 1.18)
        blue_hold = slab(PRIMARY_BLUE, 1.52, 0.66).move_to(RIGHT * 1.46 + DOWN * 0.1)
        purple_hold = slab(PRIMARY_PURPLE, 1.08, 0.54).move_to(RIGHT * 2.04 + DOWN * 0.74)

        final_green = Circle(radius=0.84, stroke_width=0, fill_color=PRIMARY_GREEN, fill_opacity=1).move_to(RIGHT * 2.44 + UP * 0.42)
        final_blue = Circle(radius=0.5, stroke_width=0, fill_color=PRIMARY_BLUE, fill_opacity=1).move_to(RIGHT * 3.64 + DOWN * 0.04)
        final_purple = Circle(radius=0.26, stroke_width=0, fill_color=PRIMARY_PURPLE, fill_opacity=1).move_to(RIGHT * 2.96 + DOWN * 1.0)

        self.add(frame, source_zone, target_zone)
        self.play(FadeIn(source, lag_ratio=0.08), run_time=0.68)
        self.play(FadeIn(guide), FadeIn(latch), run_time=0.14)
        self.play(MoveAlongPath(accent, guide), run_time=0.32)
        self.play(
            AnimationGroup(
                Transform(green, green_latch.copy()),
                Transform(blue, blue_hold.copy()),
                Transform(purple, purple_hold.copy()),
                lag_ratio=0.05,
            ),
            run_time=0.46,
            rate_func=smooth,
        )
        self.play(FadeOut(guide), run_time=0.12)
        self.play(
            AnimationGroup(
                Transform(green, final_green.copy()),
                Transform(blue, final_blue.copy()),
                Transform(purple, final_purple.copy()),
                lag_ratio=0.08,
            ),
            run_time=0.62,
            rate_func=smooth,
        )
        self.play(FadeOut(latch), run_time=0.1)
        self.play(accent.animate.move_to(RIGHT * 2.84 + DOWN * 0.02).set_fill(PRIMARY_RED, opacity=1), run_time=0.16)
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
