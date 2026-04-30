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
    linear,
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
    parser = argparse.ArgumentParser(description="Render the quality-negative-space-focus spike.")
    parser.add_argument("--quality", choices=("low", "medium", "high", "production", "4k"), default="medium")
    return parser.parse_args(namespace=_Args())


def quality_flag(quality: str) -> str:
    return {
        "low": "-ql",
        "medium": "-qm",
        "high": "-qh",
        "production": "-qp",
        "4k": "-qk",
    }[quality]


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
        "QualityNegativeSpaceFocusScene",
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


def tile(color: str, width: float, height: float) -> RoundedRectangle:
    return RoundedRectangle(
        width=width,
        height=height,
        corner_radius=0.28,
        stroke_width=0,
        fill_color=color,
        fill_opacity=1,
    )


def orb(color: str, radius: float) -> Circle:
    return Circle(radius=radius, stroke_width=0, fill_color=color, fill_opacity=1)


class QualityNegativeSpaceFocusScene(Scene):
    def construct(self) -> None:
        self.camera.background_color = WHITE

        frame = RoundedRectangle(
            width=12.9,
            height=5.8,
            corner_radius=0.34,
            stroke_color=GRAY_200,
            stroke_width=2,
            fill_color=WHITE,
            fill_opacity=0,
        )
        soft_zone = RoundedRectangle(
            width=4.4,
            height=4.1,
            corner_radius=0.36,
            stroke_width=0,
            fill_color=GRAY_100,
            fill_opacity=0.45,
        ).move_to(LEFT * 3.2 + DOWN * 0.05)

        source_tiles = VGroup(
            tile(PRIMARY_GREEN, 2.2, 1.25).move_to(LEFT * 4.05 + UP * 0.9),
            tile(PRIMARY_BLUE, 2.2, 1.15).move_to(LEFT * 2.95 + DOWN * 0.15),
            tile(PRIMARY_PURPLE, 2.0, 1.05).move_to(LEFT * 1.85 + DOWN * 1.15),
        )
        destination_group = VGroup(
            orb(PRIMARY_GREEN, 0.72).move_to(RIGHT * 2.75 + UP * 0.9),
            orb(PRIMARY_BLUE, 0.58).move_to(RIGHT * 1.85 + DOWN * 0.1),
            orb(PRIMARY_PURPLE, 0.5).move_to(RIGHT * 2.8 + DOWN * 1.2),
        )

        guide_lines = VGroup(
            Line(source_tiles[0].get_right(), destination_group[0].get_left(), color=PRIMARY_ORANGE, stroke_width=6),
            Line(source_tiles[1].get_right(), destination_group[1].get_left(), color=PRIMARY_ORANGE, stroke_width=6),
            Line(source_tiles[2].get_right(), destination_group[2].get_left(), color=PRIMARY_ORANGE, stroke_width=6),
        ).set_opacity(0.82)

        pulse = Circle(radius=0.16, stroke_width=0, fill_color=PRIMARY_YELLOW, fill_opacity=1).move_to(source_tiles[0].get_center() + RIGHT * 0.2)

        self.add(frame, soft_zone)
        self.play(FadeIn(source_tiles, shift=UP * 0.12, lag_ratio=0.1), run_time=0.85)
        self.play(FadeIn(guide_lines, lag_ratio=0.14), run_time=0.4)
        self.play(MoveAlongPath(pulse, guide_lines[0]), run_time=0.52, rate_func=linear)
        self.play(pulse.animate.move_to(source_tiles[1].get_center() + RIGHT * 0.2), run_time=0.18)
        self.play(MoveAlongPath(pulse, guide_lines[1]), run_time=0.52, rate_func=linear)
        self.play(pulse.animate.move_to(source_tiles[2].get_center() + RIGHT * 0.2), run_time=0.18)
        self.play(MoveAlongPath(pulse, guide_lines[2]), run_time=0.52, rate_func=linear)

        self.play(
            AnimationGroup(
                Transform(source_tiles[0], destination_group[0]),
                Transform(source_tiles[1], destination_group[1]),
                Transform(source_tiles[2], destination_group[2]),
                soft_zone.animate.move_to(RIGHT * 2.25 + DOWN * 0.02).scale(1.02),
                lag_ratio=0.08,
            ),
            run_time=1.55,
            rate_func=smooth,
        )
        self.play(FadeOut(guide_lines), run_time=0.18)
        self.play(pulse.animate.move_to(RIGHT * 2.25 + DOWN * 0.02).set_fill(PRIMARY_RED, opacity=1), run_time=0.22)
        for dot in source_tiles:
            self.play(dot.animate.scale(1.08), run_time=0.18, rate_func=there_and_back)
        self.play(FadeOut(pulse), run_time=0.18)
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
