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


def chip(color: str, width: float, height: float) -> Rectangle:
    return Rectangle(
        width=width,
        height=height,
        stroke_width=0,
        fill_color=color,
        fill_opacity=1,
    )


class QualityMaskTransferScene(Scene):
    def construct(self) -> None:
        self.camera.background_color = WHITE

        panel = Rectangle(
            width=12.4,
            height=5.5,
            stroke_color=GRAY_200,
            stroke_width=2,
            fill_color=WHITE,
            fill_opacity=0,
        )

        band = Rectangle(
            width=1.25,
            height=4.85,
            stroke_width=0,
            fill_color=GRAY_100,
            fill_opacity=0.98,
        ).move_to(LEFT * 4.75)

        top_row = VGroup(
            chip(PRIMARY_GREEN, 1.75, 0.82).move_to(LEFT * 3.9 + UP * 1.05),
            chip(PRIMARY_BLUE, 1.68, 0.78).move_to(LEFT * 1.35 + UP * 1.05),
            chip(PRIMARY_PURPLE, 1.52, 0.72).move_to(RIGHT * 1.15 + UP * 1.05),
            chip(PRIMARY_RED, 1.34, 0.66).move_to(RIGHT * 3.35 + UP * 1.05),
        )

        target_slots = VGroup(
            Circle(radius=0.52, stroke_width=2.5, stroke_color=GRAY_300, fill_opacity=0).move_to(LEFT * 3.6 + DOWN * 1.1),
            Circle(radius=0.44, stroke_width=2.5, stroke_color=GRAY_300, fill_opacity=0).move_to(LEFT * 1.15 + DOWN * 1.08),
            Circle(radius=0.36, stroke_width=2.5, stroke_color=GRAY_300, fill_opacity=0).move_to(RIGHT * 1.05 + DOWN * 1.05),
            Circle(radius=0.29, stroke_width=2.5, stroke_color=GRAY_300, fill_opacity=0).move_to(RIGHT * 2.85 + DOWN * 1.02),
        ).set_stroke(opacity=0.36)

        bottom_row = VGroup(
            Circle(radius=0.5, stroke_width=0, fill_color=PRIMARY_GREEN, fill_opacity=1).move_to(target_slots[0]),
            Circle(radius=0.42, stroke_width=0, fill_color=PRIMARY_BLUE, fill_opacity=1).move_to(target_slots[1]),
            Circle(radius=0.34, stroke_width=0, fill_color=PRIMARY_PURPLE, fill_opacity=1).move_to(target_slots[2]),
            Circle(radius=0.28, stroke_width=0, fill_color=PRIMARY_RED, fill_opacity=1).move_to(target_slots[3]),
        )

        transfer_lines = VGroup(*[
            Line(top_row[i].get_bottom(), bottom_row[i].get_top(), color=PRIMARY_ORANGE, stroke_width=4)
            for i in range(4)
        ]).set_opacity(0.0)

        accent = Circle(radius=0.16, stroke_width=0, fill_color=PRIMARY_YELLOW, fill_opacity=1).move_to(LEFT * 4.75 + UP * 1.95)

        self.add(panel, top_row, target_slots, band, accent)
        self.wait(2.4)

        self.play(
            band.animate.move_to(LEFT * 2.6),
            accent.animate.move_to(LEFT * 2.6 + UP * 1.95),
            run_time=2.4,
            rate_func=smooth,
        )
        self.play(
            Create(transfer_lines[0]),
            FadeIn(bottom_row[0]),
            target_slots[0].animate.set_stroke(opacity=0.12),
            run_time=1.6,
            rate_func=smooth,
        )
        self.wait(0.7)

        self.play(
            band.animate.move_to(LEFT * 0.35),
            accent.animate.move_to(LEFT * 0.35 + UP * 1.95),
            run_time=2.2,
            rate_func=smooth,
        )
        self.play(
            AnimationGroup(
                Create(transfer_lines[1]),
                FadeIn(bottom_row[1]),
                Create(transfer_lines[2]),
                FadeIn(bottom_row[2]),
                lag_ratio=0.32,
            ),
            target_slots[1].animate.set_stroke(opacity=0.12),
            target_slots[2].animate.set_stroke(opacity=0.12),
            run_time=2.4,
            rate_func=smooth,
        )
        self.wait(0.7)

        self.play(
            band.animate.move_to(RIGHT * 2.55),
            accent.animate.move_to(RIGHT * 2.55 + UP * 1.95),
            run_time=2.2,
            rate_func=smooth,
        )
        self.play(
            Create(transfer_lines[3]),
            FadeIn(bottom_row[3]),
            target_slots[3].animate.set_stroke(opacity=0.12),
            run_time=1.5,
            rate_func=smooth,
        )
        self.wait(0.8)

        self.play(
            band.animate.move_to(RIGHT * 4.75),
            accent.animate.move_to(RIGHT * 4.75 + UP * 1.95),
            run_time=1.9,
            rate_func=smooth,
        )

        compact_targets = VGroup(
            Circle(radius=0.69, stroke_width=0, fill_color=PRIMARY_GREEN, fill_opacity=1).move_to(LEFT * 0.1 + UP * 0.58),
            Circle(radius=0.49, stroke_width=0, fill_color=PRIMARY_BLUE, fill_opacity=1).move_to(RIGHT * 1.5 + UP * 0.02),
            Circle(radius=0.36, stroke_width=0, fill_color=PRIMARY_PURPLE, fill_opacity=1).move_to(RIGHT * 0.45 + DOWN * 1.22),
            Circle(radius=0.28, stroke_width=0, fill_color=PRIMARY_RED, fill_opacity=1).move_to(RIGHT * 1.95 + DOWN * 1.38),
        )

        self.play(
            transfer_lines.animate.set_opacity(0.0),
            target_slots.animate.set_stroke(opacity=0.0),
            FadeOut(top_row),
            band.animate.set_opacity(0.0),
            FadeOut(accent),
            run_time=1.2,
            rate_func=smooth,
        )
        self.play(
            AnimationGroup(*[Transform(bottom_row[i], compact_targets[i]) for i in range(4)], lag_ratio=0.07),
            run_time=2.2,
            rate_func=smooth,
        )
        self.wait(0.7)

        for dot in bottom_row:
            self.play(dot.animate.scale(1.08), run_time=0.28, rate_func=there_and_back)
        self.play(FadeOut(panel), run_time=1.0)
        self.wait(5.8)


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
