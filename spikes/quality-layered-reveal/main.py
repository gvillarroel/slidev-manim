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
    Rectangle,
    RoundedRectangle,
    Scene,
    Transform,
    VGroup,
    WHITE,
    linear,
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
    parser = argparse.ArgumentParser(description="Render the quality-layered-reveal spike.")
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
        "QualityLayeredRevealScene",
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


def card(color: str, width: float = 2.1, height: float = 1.25, opacity: float = 1.0) -> RoundedRectangle:
    return RoundedRectangle(
        width=width,
        height=height,
        corner_radius=0.28,
        stroke_width=0,
        fill_color=color,
        fill_opacity=opacity,
    )


def orb(color: str, radius: float) -> VGroup:
    fill = Circle(radius=radius, stroke_width=0, fill_color=color, fill_opacity=1)
    ring = Circle(radius=radius + 0.14, stroke_color=color, stroke_width=6, fill_opacity=0)
    return VGroup(fill, ring)


class QualityLayeredRevealScene(Scene):
    def construct(self) -> None:
        self.camera.background_color = WHITE

        back_strip = Rectangle(width=13.5, height=2.0, stroke_width=0, fill_color=GRAY_100, fill_opacity=0.55).shift(UP * 0.8)
        front_panel = RoundedRectangle(
            width=12.8,
            height=4.25,
            corner_radius=0.35,
            stroke_color=GRAY_200,
            stroke_width=2,
            fill_color=WHITE,
            fill_opacity=0.92,
        ).shift(DOWN * 0.95)

        left_stack = VGroup(
            card(PRIMARY_GREEN).move_to(LEFT * 3.35 + UP * 0.95),
            card(PRIMARY_BLUE).move_to(LEFT * 2.35 + UP * 0.02),
            card(PRIMARY_PURPLE).move_to(LEFT * 1.35 + DOWN * 0.95),
        )
        ghost_stack = left_stack.copy().set_fill(color=GRAY_200, opacity=0.14).set_z_index(-1).shift(RIGHT * 0.18 + DOWN * 0.12)

        right_cluster = VGroup(
            orb(PRIMARY_GREEN, 0.62).move_to(RIGHT * 2.9 + UP * 0.9),
            orb(PRIMARY_BLUE, 0.54).move_to(RIGHT * 3.95 + DOWN * 0.05),
            orb(PRIMARY_PURPLE, 0.46).move_to(RIGHT * 2.7 + DOWN * 0.95),
        )

        guide_lines = VGroup(
            Line(left_stack[0].get_right(), right_cluster[0].get_left(), color=PRIMARY_ORANGE, stroke_width=6),
            Line(left_stack[1].get_right(), right_cluster[1].get_left(), color=PRIMARY_ORANGE, stroke_width=6),
            Line(left_stack[2].get_right(), right_cluster[2].get_left(), color=PRIMARY_ORANGE, stroke_width=6),
        )
        pulse = Circle(radius=0.14, stroke_width=0, fill_color=PRIMARY_YELLOW, fill_opacity=1).move_to(guide_lines[0].get_start())

        self.add(back_strip, front_panel, ghost_stack)
        self.play(FadeIn(left_stack, shift=UP * 0.15, lag_ratio=0.1), run_time=0.9)
        self.play(FadeIn(guide_lines, lag_ratio=0.12), run_time=0.45)

        for segment in guide_lines:
            self.play(FadeIn(pulse), run_time=0.12)
            self.play(MoveAlongPath(pulse, segment), run_time=0.55, rate_func=linear)
            self.play(FadeOut(pulse), run_time=0.08)

        self.play(
            AnimationGroup(
                Transform(left_stack[0], right_cluster[0]),
                Transform(left_stack[1], right_cluster[1]),
                Transform(left_stack[2], right_cluster[2]),
                lag_ratio=0.08,
            ),
            run_time=1.7,
            rate_func=smooth,
        )
        self.play(FadeOut(guide_lines), run_time=0.22)
        self.wait(0.35)


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
