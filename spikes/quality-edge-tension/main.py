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


def slab(color: str, width: float, height: float) -> RoundedRectangle:
    return RoundedRectangle(width=width, height=height, corner_radius=0.3, stroke_width=0, fill_color=color, fill_opacity=1)


class QualityEdgeTensionScene(Scene):
    def construct(self) -> None:
        self.camera.background_color = WHITE

        frame = RoundedRectangle(width=12.9, height=5.8, corner_radius=0.34, stroke_color=GRAY_200, stroke_width=2, fill_color=WHITE, fill_opacity=0)
        left_soft = RoundedRectangle(width=3.9, height=4.5, corner_radius=0.35, stroke_width=0, fill_color=GRAY_100, fill_opacity=0.26).move_to(LEFT * 3.45)
        right_soft = RoundedRectangle(width=3.0, height=4.15, corner_radius=0.35, stroke_width=0, fill_color=GRAY_100, fill_opacity=0.3).move_to(RIGHT * 4.55 + DOWN * 0.15)

        source = VGroup(
            slab(PRIMARY_GREEN, 1.95, 0.9).move_to(LEFT * 3.95 + UP * 0.82),
            slab(PRIMARY_BLUE, 1.82, 0.84).move_to(LEFT * 2.52 + DOWN * 0.02),
            slab(PRIMARY_PURPLE, 1.66, 0.78).move_to(LEFT * 1.1 + DOWN * 0.98),
        )
        targets = VGroup(
            Circle(radius=0.88, stroke_width=0, fill_color=PRIMARY_GREEN, fill_opacity=1).move_to(RIGHT * 4.82 + UP * 0.52),
            Circle(radius=0.52, stroke_width=0, fill_color=PRIMARY_BLUE, fill_opacity=1).move_to(RIGHT * 3.92 + DOWN * 0.42),
            Circle(radius=0.28, stroke_width=0, fill_color=PRIMARY_PURPLE, fill_opacity=1).move_to(RIGHT * 4.48 + DOWN * 1.12),
        )
        overshoot_targets = VGroup(
            Circle(radius=0.92, stroke_width=0, fill_color=PRIMARY_GREEN, fill_opacity=1).move_to(RIGHT * 5.02 + UP * 0.5),
            Circle(radius=0.54, stroke_width=0, fill_color=PRIMARY_BLUE, fill_opacity=1).move_to(RIGHT * 4.08 + DOWN * 0.4),
            Circle(radius=0.28, stroke_width=0, fill_color=PRIMARY_PURPLE, fill_opacity=1).move_to(RIGHT * 4.62 + DOWN * 1.06),
        )

        guide = Line(LEFT * 0.58 + DOWN * 0.02, RIGHT * 4.2 + DOWN * 0.02, color=PRIMARY_ORANGE, stroke_width=7)
        accent = Circle(radius=0.12, stroke_width=0, fill_color=PRIMARY_YELLOW, fill_opacity=1).move_to(guide.get_start())
        settle_point = RIGHT * 4.42 + DOWN * 0.08

        self.add(frame, left_soft, right_soft)
        self.play(FadeIn(source, lag_ratio=0.08), run_time=0.68)
        self.play(FadeIn(guide), run_time=0.14)
        self.play(MoveAlongPath(accent, guide), run_time=0.36)
        self.play(
            AnimationGroup(
                Transform(source[0], overshoot_targets[0].copy()),
                Transform(source[1], overshoot_targets[1].copy()),
                Transform(source[2], overshoot_targets[2].copy()),
                lag_ratio=0.08,
            ),
            run_time=0.84,
            rate_func=smooth,
        )
        self.play(
            AnimationGroup(
                source[0].animate.move_to(targets[0].get_center()).scale(targets[0].width / source[0].width),
                source[1].animate.move_to(targets[1].get_center()).scale(targets[1].width / source[1].width),
                source[2].animate.move_to(targets[2].get_center()).scale(targets[2].width / source[2].width),
                lag_ratio=0.04,
            ),
            run_time=0.18,
            rate_func=smooth,
        )
        self.play(FadeOut(guide), run_time=0.14)
        self.play(accent.animate.move_to(settle_point).set_fill(PRIMARY_RED, opacity=1), run_time=0.16)
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
