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
    PI,
    RIGHT,
    UP,
    AnimationGroup,
    Arc,
    Circle,
    FadeIn,
    FadeOut,
    MoveAlongPath,
    RoundedRectangle,
    Scene,
    VGroup,
    WHITE,
    linear,
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
    parser = argparse.ArgumentParser(description="Render the quality-anchored-orbit spike.")
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
        "QualityAnchoredOrbitScene",
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


def chip(color: str, width: float, height: float) -> RoundedRectangle:
    return RoundedRectangle(width=width, height=height, corner_radius=0.28, stroke_width=0, fill_color=color, fill_opacity=1)


class QualityAnchoredOrbitScene(Scene):
    def construct(self) -> None:
        self.camera.background_color = WHITE

        frame = RoundedRectangle(width=12.9, height=5.8, corner_radius=0.34, stroke_color=GRAY_200, stroke_width=2, fill_color=WHITE, fill_opacity=0)
        zone = Circle(radius=1.65, stroke_width=0, fill_color=GRAY_100, fill_opacity=0.34).move_to(RIGHT * 2.15)

        anchor = Circle(radius=0.82, stroke_width=0, fill_color=PRIMARY_GREEN, fill_opacity=1).move_to(RIGHT * 2.15)
        satellite_1 = chip(PRIMARY_BLUE, 1.95, 0.82).move_to(LEFT * 3.55 + UP * 0.4)
        satellite_2 = chip(PRIMARY_PURPLE, 1.75, 0.76).move_to(LEFT * 1.2 + DOWN * 0.8)
        orbit_target_1 = chip(PRIMARY_BLUE, 1.75, 0.74).move_to(RIGHT * 3.65 + UP * 0.55)
        orbit_target_2 = chip(PRIMARY_PURPLE, 1.55, 0.68).move_to(RIGHT * 1.2 + DOWN * 1.3)
        arc_1 = Arc(radius=1.55, start_angle=PI, angle=-0.9 * PI, arc_center=anchor.get_center(), color=PRIMARY_ORANGE, stroke_width=6)
        arc_2 = Arc(radius=1.4, start_angle=PI + 0.2, angle=-0.95 * PI, arc_center=anchor.get_center(), color=PRIMARY_ORANGE, stroke_width=6)
        accent = Circle(radius=0.14, stroke_width=0, fill_color=PRIMARY_YELLOW, fill_opacity=1).move_to(anchor.get_center() + LEFT * 1.55)

        self.add(frame, zone)
        self.play(FadeIn(anchor), FadeIn(VGroup(satellite_1, satellite_2)), run_time=0.7)
        self.play(FadeIn(VGroup(arc_1, arc_2)), run_time=0.22)
        self.play(MoveAlongPath(accent, arc_1), run_time=0.48, rate_func=linear)
        self.play(MoveAlongPath(satellite_1, arc_1), run_time=0.72, rate_func=smooth)
        self.play(MoveAlongPath(accent, arc_2), run_time=0.4, rate_func=linear)
        self.play(MoveAlongPath(satellite_2, arc_2), run_time=0.66, rate_func=smooth)
        self.play(
            AnimationGroup(
                satellite_1.animate.move_to(orbit_target_1).scale(0.98),
                satellite_2.animate.move_to(orbit_target_2).scale(0.96),
                lag_ratio=0.06,
            ),
            run_time=0.35,
        )
        self.play(FadeOut(VGroup(arc_1, arc_2)), run_time=0.16)
        self.play(anchor.animate.scale(1.08), run_time=0.18, rate_func=there_and_back)
        self.play(satellite_1.animate.scale(1.05), satellite_2.animate.scale(1.05), run_time=0.16, rate_func=there_and_back)
        self.play(accent.animate.move_to(anchor.get_center() + DOWN * 1.05).set_fill(PRIMARY_RED, opacity=1), run_time=0.18)
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
