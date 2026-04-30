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
    parser = argparse.ArgumentParser(description="Render the quality-compression-release spike.")
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
        "QualityCompressionReleaseScene",
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


class QualityCompressionReleaseScene(Scene):
    def construct(self) -> None:
        self.camera.background_color = WHITE

        frame = RoundedRectangle(width=12.9, height=5.8, corner_radius=0.34, stroke_color=GRAY_200, stroke_width=2, fill_color=WHITE, fill_opacity=0)
        soft = RoundedRectangle(width=4.4, height=4.4, corner_radius=0.35, stroke_width=0, fill_color=GRAY_100, fill_opacity=0.34).move_to(RIGHT * 2.8)

        source = VGroup(
            chip(PRIMARY_GREEN, 1.9, 0.9).move_to(LEFT * 4.2 + UP * 0.8),
            chip(PRIMARY_BLUE, 1.8, 0.86).move_to(LEFT * 2.25 + DOWN * 0.05),
            chip(PRIMARY_PURPLE, 1.7, 0.8).move_to(LEFT * 0.45 + DOWN * 1.0),
        )
        compressed_positions = [RIGHT * 1.55 + UP * 0.22, RIGHT * 1.92 + DOWN * 0.04, RIGHT * 2.25 + DOWN * 0.34]
        release_positions = [RIGHT * 2.35 + UP * 0.42, RIGHT * 3.62 + DOWN * 0.12, RIGHT * 2.82 + DOWN * 1.18]
        release_targets = VGroup(
            Circle(radius=0.82, stroke_width=0, fill_color=PRIMARY_GREEN, fill_opacity=1).move_to(release_positions[0]),
            Circle(radius=0.58, stroke_width=0, fill_color=PRIMARY_BLUE, fill_opacity=1).move_to(release_positions[1]),
            Circle(radius=0.32, stroke_width=0, fill_color=PRIMARY_PURPLE, fill_opacity=1).move_to(release_positions[2]),
        )
        path = Line(LEFT * 4.0 + UP * 0.55, RIGHT * 1.42 + UP * 0.04, color=PRIMARY_ORANGE, stroke_width=5)
        accent = Circle(radius=0.12, stroke_width=0, fill_color=PRIMARY_YELLOW, fill_opacity=1).move_to(path.get_start())
        settle_point = RIGHT * 2.94 + DOWN * 0.06

        self.add(frame, soft)
        self.play(FadeIn(source, lag_ratio=0.08), run_time=0.68)
        self.play(FadeIn(path), run_time=0.14)
        self.play(MoveAlongPath(accent, path), run_time=0.34)
        self.play(
            AnimationGroup(
                source[0].animate.move_to(compressed_positions[0]),
                source[1].animate.move_to(compressed_positions[1]),
                source[2].animate.move_to(compressed_positions[2]),
                lag_ratio=0.06,
            ),
            run_time=0.62,
            rate_func=smooth,
        )
        self.play(source.animate.scale(0.88), run_time=0.18, rate_func=there_and_back)
        self.play(
            AnimationGroup(
                Transform(source[0], release_targets[0].copy()),
                Transform(source[1], release_targets[1].copy()),
                Transform(source[2], release_targets[2].copy()),
                lag_ratio=0.08,
            ),
            run_time=0.84,
            rate_func=smooth,
        )
        self.play(FadeOut(path), run_time=0.14)
        self.play(accent.animate.move_to(settle_point).set_fill(PRIMARY_RED, opacity=1), run_time=0.16)
        for item in source:
            self.play(item.animate.scale(1.06), run_time=0.13, rate_func=there_and_back)
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
