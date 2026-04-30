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
    LaggedStart,
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
    parser = argparse.ArgumentParser(description="Render the quality-rhythm-gating spike.")
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
        "QualityRhythmGatingScene",
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


def block(color: str, width: float, height: float) -> RoundedRectangle:
    return RoundedRectangle(width=width, height=height, corner_radius=0.28, stroke_width=0, fill_color=color, fill_opacity=1)


def gate(x: float) -> RoundedRectangle:
    return RoundedRectangle(
        width=1.0,
        height=4.7,
        corner_radius=0.28,
        stroke_width=0,
        fill_color=GRAY_100,
        fill_opacity=0.68,
    ).move_to(RIGHT * x)


class QualityRhythmGatingScene(Scene):
    def construct(self) -> None:
        self.camera.background_color = WHITE

        frame = RoundedRectangle(width=12.9, height=5.8, corner_radius=0.34, stroke_color=GRAY_200, stroke_width=2, fill_color=WHITE, fill_opacity=0)
        gates = VGroup(gate(-3.8), gate(-0.6), gate(2.6))
        source = VGroup(
            block(PRIMARY_GREEN, 2.0, 0.95).move_to(LEFT * 4.6),
            block(PRIMARY_BLUE, 2.0, 0.95).move_to(LEFT * 2.1),
            block(PRIMARY_PURPLE, 2.0, 0.95).move_to(RIGHT * 0.4),
        )
        targets = VGroup(
            Circle(radius=0.62, stroke_width=0, fill_color=PRIMARY_GREEN, fill_opacity=1).move_to(RIGHT * 1.95 + UP * 0.85),
            Circle(radius=0.5, stroke_width=0, fill_color=PRIMARY_BLUE, fill_opacity=1).move_to(RIGHT * 3.0 + DOWN * 0.0),
            Circle(radius=0.42, stroke_width=0, fill_color=PRIMARY_PURPLE, fill_opacity=1).move_to(RIGHT * 2.4 + DOWN * 1.05),
        )
        guides = VGroup(
            Line(source[0].get_right(), targets[0].get_left(), color=PRIMARY_ORANGE, stroke_width=6),
            Line(source[1].get_right(), targets[1].get_left(), color=PRIMARY_ORANGE, stroke_width=6),
            Line(source[2].get_right(), targets[2].get_left(), color=PRIMARY_ORANGE, stroke_width=6),
        ).set_opacity(0)
        accent = Circle(radius=0.14, stroke_width=0, fill_color=PRIMARY_YELLOW, fill_opacity=1).move_to(source[0].get_center())

        self.add(frame)
        self.play(FadeIn(gates, lag_ratio=0.08), FadeIn(source, lag_ratio=0.06), run_time=0.7)

        for index in range(3):
            self.play(gates[index].animate.scale(1.06), run_time=0.16, rate_func=there_and_back)
            self.play(FadeIn(guides[index]), run_time=0.12)
            self.play(MoveAlongPath(accent, guides[index]), run_time=0.45, rate_func=linear)
            self.play(Transform(source[index], targets[index]), run_time=0.42, rate_func=smooth)
            if index < 2:
                self.play(accent.animate.move_to(source[index + 1].get_center()), run_time=0.15)

        self.play(FadeOut(guides), FadeOut(gates), run_time=0.18)
        for dot in source:
            self.play(dot.animate.scale(1.08), run_time=0.16, rate_func=there_and_back)
        self.play(accent.animate.move_to(RIGHT * 2.45 + DOWN * 0.05).set_fill(PRIMARY_RED, opacity=1), run_time=0.2)
        self.play(FadeOut(accent), run_time=0.16)
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
