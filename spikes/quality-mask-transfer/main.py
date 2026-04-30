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
    parser = argparse.ArgumentParser(description="Render the quality-mask-transfer spike.")
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
        "QualityMaskTransferScene",
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
    return RoundedRectangle(
        width=width,
        height=height,
        corner_radius=0.3,
        stroke_width=0,
        fill_color=color,
        fill_opacity=1,
    )


class QualityMaskTransferScene(Scene):
    def construct(self) -> None:
        self.camera.background_color = WHITE

        panel = RoundedRectangle(
            width=12.8,
            height=5.7,
            corner_radius=0.35,
            stroke_color=GRAY_200,
            stroke_width=2,
            fill_color=WHITE,
            fill_opacity=0,
        )
        band = RoundedRectangle(
            width=2.15,
            height=5.1,
            corner_radius=0.34,
            stroke_width=0,
            fill_color=GRAY_100,
            fill_opacity=0.95,
        ).move_to(LEFT * 4.7)

        top_row = VGroup(
            chip(PRIMARY_GREEN, 2.1, 1.0).move_to(LEFT * 3.8 + UP * 0.8),
            chip(PRIMARY_BLUE, 2.0, 0.96).move_to(LEFT * 1.1 + UP * 0.8),
            chip(PRIMARY_PURPLE, 1.9, 0.92).move_to(RIGHT * 1.4 + UP * 0.8),
            chip(PRIMARY_RED, 1.8, 0.88).move_to(RIGHT * 3.8 + UP * 0.8),
        )
        bottom_row = VGroup(
            Circle(radius=0.5, stroke_width=0, fill_color=PRIMARY_GREEN, fill_opacity=1).move_to(LEFT * 2.75 + DOWN * 1.1),
            Circle(radius=0.42, stroke_width=0, fill_color=PRIMARY_BLUE, fill_opacity=1).move_to(LEFT * 0.55 + DOWN * 1.08),
            Circle(radius=0.34, stroke_width=0, fill_color=PRIMARY_PURPLE, fill_opacity=1).move_to(RIGHT * 1.45 + DOWN * 1.05),
            Circle(radius=0.28, stroke_width=0, fill_color=PRIMARY_RED, fill_opacity=1).move_to(RIGHT * 3.05 + DOWN * 1.02),
        )
        transfer_lines = VGroup(*[
            Line(top_row[i].get_bottom(), bottom_row[i].get_top(), color=PRIMARY_ORANGE, stroke_width=5)
            for i in range(4)
        ]).set_opacity(0)

        accent = Circle(radius=0.15, stroke_width=0, fill_color=PRIMARY_YELLOW, fill_opacity=1).move_to(LEFT * 4.55 + UP * 1.9)

        self.add(panel, band)
        self.play(FadeIn(top_row, lag_ratio=0.08), run_time=0.7)
        self.play(band.animate.move_to(RIGHT * 0.2), accent.animate.move_to(RIGHT * 0.35 + UP * 1.9), run_time=0.9, rate_func=smooth)
        self.play(FadeIn(transfer_lines, lag_ratio=0.06), FadeIn(bottom_row, lag_ratio=0.08), run_time=0.45)
        self.play(band.animate.move_to(RIGHT * 4.25), accent.animate.move_to(RIGHT * 4.45 + UP * 1.9), run_time=0.8, rate_func=smooth)

        compact_targets = VGroup(
            Circle(radius=0.68, stroke_width=0, fill_color=PRIMARY_GREEN, fill_opacity=1).move_to(RIGHT * 1.95 + UP * 0.55),
            Circle(radius=0.52, stroke_width=0, fill_color=PRIMARY_BLUE, fill_opacity=1).move_to(RIGHT * 3.0 + UP * 0.0),
            Circle(radius=0.38, stroke_width=0, fill_color=PRIMARY_PURPLE, fill_opacity=1).move_to(RIGHT * 2.35 + DOWN * 0.95),
            Circle(radius=0.28, stroke_width=0, fill_color=PRIMARY_RED, fill_opacity=1).move_to(RIGHT * 3.65 + DOWN * 1.15),
        )

        self.play(
            AnimationGroup(*[Transform(bottom_row[i], compact_targets[i]) for i in range(4)], lag_ratio=0.07),
            transfer_lines.animate.set_opacity(0.0),
            top_row.animate.set_opacity(0.08),
            band.animate.set_opacity(0.0),
            run_time=1.3,
            rate_func=smooth,
        )
        for dot in bottom_row:
            self.play(dot.animate.scale(1.08), run_time=0.16, rate_func=there_and_back)
        self.play(accent.animate.move_to(RIGHT * 2.55 + DOWN * 0.18).set_fill(PRIMARY_YELLOW, opacity=1), run_time=0.22)
        self.play(FadeOut(accent), FadeOut(top_row), run_time=0.18)
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
