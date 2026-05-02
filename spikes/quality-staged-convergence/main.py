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
    parser = argparse.ArgumentParser(description="Render the quality-staged-convergence spike.")
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
        "--transparent",
        "--format",
        "webm",
        "-o",
        stem,
        "--media_dir",
        str(STAGING_DIR),
        str(Path(__file__).resolve()),
        "QualityStagedConvergenceScene",
    ]
    if poster:
        command.insert(-2, "-s")
    return command


def promote(target_name: str, destination: Path) -> None:
    matches = list(STAGING_DIR.glob(f"**/{target_name}"))
    if not matches:
        raise FileNotFoundError(target_name)
    destination.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(max(matches, key=lambda path: path.stat().st_mtime), destination)


def slab(color: str, width: float, height: float) -> Rectangle:
    return Rectangle(width=width, height=height, stroke_width=0, fill_color=color, fill_opacity=1)


def soft_panel(width: float, height: float) -> Rectangle:
    return Rectangle(width=width, height=height, stroke_width=0, fill_color=GRAY_100, fill_opacity=0.2)


def corner_brackets(width: float, height: float, leg: float, color: str = PRIMARY_RED) -> VGroup:
    half_w = width / 2
    half_h = height / 2
    return VGroup(
        Line(LEFT * half_w + UP * half_h, LEFT * (half_w - leg) + UP * half_h, color=color, stroke_width=5),
        Line(LEFT * half_w + UP * half_h, LEFT * half_w + UP * (half_h - leg), color=color, stroke_width=5),
        Line(RIGHT * half_w + UP * half_h, RIGHT * (half_w - leg) + UP * half_h, color=color, stroke_width=5),
        Line(RIGHT * half_w + UP * half_h, RIGHT * half_w + UP * (half_h - leg), color=color, stroke_width=5),
        Line(LEFT * half_w + DOWN * half_h, LEFT * (half_w - leg) + DOWN * half_h, color=color, stroke_width=5),
        Line(LEFT * half_w + DOWN * half_h, LEFT * half_w + DOWN * (half_h - leg), color=color, stroke_width=5),
        Line(RIGHT * half_w + DOWN * half_h, RIGHT * (half_w - leg) + DOWN * half_h, color=color, stroke_width=5),
        Line(RIGHT * half_w + DOWN * half_h, RIGHT * half_w + DOWN * (half_h - leg), color=color, stroke_width=5),
    )


class QualityStagedConvergenceScene(Scene):
    def construct(self) -> None:
        self.camera.background_color = WHITE

        source_zone = soft_panel(3.35, 3.85).move_to(LEFT * 3.75)
        lane_zone = VGroup(
            Line(LEFT * 0.85 + UP * 1.28, LEFT * 0.85 + DOWN * 1.28, color=GRAY_200, stroke_width=3),
            Line(RIGHT * 0.85 + UP * 1.28, RIGHT * 0.85 + DOWN * 1.28, color=GRAY_200, stroke_width=3),
        ).move_to(LEFT * 0.62)
        target_zone = soft_panel(3.2, 3.85).move_to(RIGHT * 2.05)

        source = VGroup(
            slab(PRIMARY_GREEN, 2.42, 0.7).move_to(LEFT * 3.92 + UP * 0.9),
            slab(PRIMARY_BLUE, 1.82, 0.64).move_to(LEFT * 3.46 + DOWN * 0.06),
            slab(PRIMARY_PURPLE, 1.32, 0.54).move_to(LEFT * 3.12 + DOWN * 1.0),
        )

        lane_slots = VGroup(
            slab(GRAY_200, 0.92, 0.3).move_to(LEFT * 0.62 + UP * 0.36),
            slab(GRAY_200, 0.78, 0.28).move_to(LEFT * 0.62),
            slab(GRAY_200, 0.62, 0.24).move_to(LEFT * 0.62 + DOWN * 0.36),
        )
        lane_slots.set_opacity(0.33)

        target_slots = VGroup(
            Circle(radius=0.62, stroke_color=GRAY_200, stroke_width=3, fill_opacity=0).move_to(RIGHT * 1.65 + UP * 0.5),
            Circle(radius=0.32, stroke_color=GRAY_200, stroke_width=3, fill_opacity=0).move_to(RIGHT * 2.66 + DOWN * 0.25),
            Circle(radius=0.2, stroke_color=GRAY_200, stroke_width=3, fill_opacity=0).move_to(RIGHT * 1.68 + DOWN * 0.78),
        )
        target_slots.set_stroke(opacity=0.42)

        route_in = Line(LEFT * 2.1, LEFT * 1.75, color=GRAY_200, stroke_width=3)
        accent = Circle(radius=0.12, stroke_width=0, fill_color=PRIMARY_RED, fill_opacity=1).move_to(route_in.get_start())

        lane_green = slab(PRIMARY_GREEN, 0.94, 0.2).move_to(LEFT * 0.62 + UP * 0.55)
        lane_blue = slab(PRIMARY_BLUE, 0.78, 0.18).move_to(LEFT * 0.62)
        lane_purple = slab(PRIMARY_PURPLE, 0.62, 0.16).move_to(LEFT * 0.62 + DOWN * 0.55)

        final_green = Circle(radius=0.62, stroke_width=0, fill_color=PRIMARY_GREEN, fill_opacity=1).move_to(RIGHT * 1.65 + UP * 0.5)
        final_blue = Circle(radius=0.32, stroke_width=0, fill_color=PRIMARY_BLUE, fill_opacity=1).move_to(RIGHT * 2.66 + DOWN * 0.25)
        final_purple = Circle(radius=0.2, stroke_width=0, fill_color=PRIMARY_PURPLE, fill_opacity=1).move_to(RIGHT * 1.68 + DOWN * 0.78)

        terminal_brackets = corner_brackets(2.7, 2.25, 0.28).move_to(RIGHT * 2.02 + DOWN * 0.05)

        self.add(source_zone, lane_zone, lane_slots, target_zone, target_slots, source, accent)
        self.wait(2.7)
        self.play(MoveAlongPath(accent, route_in), run_time=1.4, rate_func=smooth)
        self.play(FadeOut(accent), FadeOut(lane_slots), run_time=0.6)
        self.play(
            AnimationGroup(
                Transform(source[0], lane_green.copy()),
                Transform(source[1], lane_blue.copy()),
                Transform(source[2], lane_purple.copy()),
                lag_ratio=0.16,
            ),
            run_time=3.2,
            rate_func=smooth,
        )
        self.wait(3.0)
        self.play(FadeOut(target_slots), FadeOut(target_zone), run_time=0.8)
        self.play(
            AnimationGroup(
                Transform(source[0], final_green.copy()),
                Transform(source[1], final_blue.copy()),
                Transform(source[2], final_purple.copy()),
                lag_ratio=0.08,
            ),
            run_time=3.5,
            rate_func=smooth,
        )
        self.play(
            FadeOut(source_zone),
            FadeOut(lane_zone),
            FadeIn(terminal_brackets, scale=0.98),
            VGroup(source, terminal_brackets).animate.shift(LEFT * 1.45),
            run_time=2.3,
            rate_func=smooth,
        )
        self.wait(8.1)


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
