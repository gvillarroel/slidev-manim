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
    parser = argparse.ArgumentParser(description="Render the quality-scale-hierarchy spike.")
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
        "QualityScaleHierarchyScene",
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


def plate(color: str, width: float, height: float) -> RoundedRectangle:
    return RoundedRectangle(width=width, height=height, corner_radius=0.3, stroke_width=0, fill_color=color, fill_opacity=1)


class QualityScaleHierarchyScene(Scene):
    def construct(self) -> None:
        self.camera.background_color = WHITE

        frame = RoundedRectangle(width=12.9, height=5.8, corner_radius=0.34, stroke_color=GRAY_200, stroke_width=2, fill_color=WHITE, fill_opacity=0)
        zone = RoundedRectangle(width=4.8, height=4.7, corner_radius=0.36, stroke_width=0, fill_color=GRAY_100, fill_opacity=0.38).move_to(RIGHT * 2.65)

        source = VGroup(
            plate(PRIMARY_GREEN, 1.9, 0.92).move_to(LEFT * 4.25 + UP * 0.85),
            plate(PRIMARY_BLUE, 1.8, 0.88).move_to(LEFT * 2.2 + DOWN * 0.05),
            plate(PRIMARY_PURPLE, 1.7, 0.82).move_to(LEFT * 0.4 + DOWN * 1.0),
        )
        targets = VGroup(
            Circle(radius=0.95, stroke_width=0, fill_color=PRIMARY_GREEN, fill_opacity=1).move_to(RIGHT * 2.35 + UP * 0.45),
            Circle(radius=0.54, stroke_width=0, fill_color=PRIMARY_BLUE, fill_opacity=1).move_to(RIGHT * 4.1 + DOWN * 0.45),
            Circle(radius=0.34, stroke_width=0, fill_color=PRIMARY_PURPLE, fill_opacity=1).move_to(RIGHT * 3.15 + DOWN * 1.35),
        )

        accent = Circle(radius=0.15, stroke_width=0, fill_color=PRIMARY_YELLOW, fill_opacity=1).move_to(source[0].get_center())
        path_1 = plate(PRIMARY_ORANGE, 4.2, 0.12).move_to(LEFT * 0.45 + UP * 0.68)
        path_2 = plate(PRIMARY_ORANGE, 3.4, 0.12).move_to(RIGHT * 1.05 + DOWN * 0.05)
        path_3 = plate(PRIMARY_ORANGE, 2.2, 0.12).move_to(RIGHT * 2.0 + DOWN * 0.95)
        guides = VGroup(path_1, path_2, path_3).set_opacity(0.0)

        self.add(frame, zone)
        self.play(FadeIn(source, lag_ratio=0.08), run_time=0.7)
        self.play(FadeIn(guides, lag_ratio=0.08), run_time=0.22)
        self.play(MoveAlongPath(accent, guides[0]), run_time=0.4, rate_func=linear)
        self.play(accent.animate.move_to(source[1].get_center()), run_time=0.12)
        self.play(MoveAlongPath(accent, guides[1]), run_time=0.36, rate_func=linear)
        self.play(accent.animate.move_to(source[2].get_center()), run_time=0.12)
        self.play(MoveAlongPath(accent, guides[2]), run_time=0.3, rate_func=linear)
        self.play(
            AnimationGroup(
                Transform(source[0], targets[0]),
                Transform(source[1], targets[1]),
                Transform(source[2], targets[2]),
                lag_ratio=0.08,
            ),
            run_time=1.2,
            rate_func=smooth,
        )
        self.play(FadeOut(guides), run_time=0.16)
        self.play(accent.animate.move_to(RIGHT * 2.6 + DOWN * 0.12).set_fill(PRIMARY_RED, opacity=1), run_time=0.18)
        for item in source:
            self.play(item.animate.scale(1.07), run_time=0.14, rate_func=there_and_back)
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
