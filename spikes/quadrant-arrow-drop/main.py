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
    Arrow,
    Axes,
    Create,
    Dot,
    FadeIn,
    FadeOut,
    Text,
    RoundedRectangle,
    Scene,
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
GRAY_300 = "#b5b5b5"
GRAY_400 = "#9c9c9c"
GRAY_600 = "#696969"


class _Args(argparse.Namespace):
    quality: str


def parse_args() -> _Args:
    parser = argparse.ArgumentParser(description="Render the quadrant-arrow-drop spike.")
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
        "QuadrantArrowDropScene",
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


class QuadrantArrowDropScene(Scene):
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

        axes = Axes(
            x_range=[0, 10, 1],
            y_range=[0, 10, 1],
            x_length=6.2,
            y_length=3.8,
            axis_config={"stroke_color": GRAY_400, "stroke_width": 1.8, "include_ticks": False},
            tips=False,
        ).move_to(DOWN * 0.06 + RIGHT * 0.08)

        quadrant_boxes = VGroup(
            RoundedRectangle(width=3.08, height=1.88, corner_radius=0.12, stroke_width=0, fill_color=GRAY_100, fill_opacity=0.12).move_to(axes.c2p(2.5, 7.5)),
            RoundedRectangle(width=3.08, height=1.88, corner_radius=0.12, stroke_width=0, fill_color=GRAY_100, fill_opacity=0.08).move_to(axes.c2p(7.5, 7.5)),
            RoundedRectangle(width=3.08, height=1.88, corner_radius=0.12, stroke_width=0, fill_color=GRAY_100, fill_opacity=0.08).move_to(axes.c2p(2.5, 2.5)),
            RoundedRectangle(width=3.08, height=1.88, corner_radius=0.12, stroke_width=0, fill_color=GRAY_100, fill_opacity=0.12).move_to(axes.c2p(7.5, 2.5)),
        )
        vertical_split = RoundedRectangle(width=0.03, height=3.8, corner_radius=0.015, stroke_width=0, fill_color=GRAY_200, fill_opacity=0.55).move_to(axes.c2p(5, 5))
        horizontal_split = RoundedRectangle(width=6.2, height=0.03, corner_radius=0.015, stroke_width=0, fill_color=GRAY_200, fill_opacity=0.55).move_to(axes.c2p(5, 5))

        quadrant_labels = VGroup(
            Text("Quick Wins", font_size=22, color=GRAY_300).move_to(axes.c2p(2.0, 8.5)),
            Text("Premium Bets", font_size=22, color=GRAY_300).move_to(axes.c2p(7.8, 8.5)),
            Text("Low Yield", font_size=22, color=GRAY_300).move_to(axes.c2p(2.0, 1.5)),
            Text("Scale Plays", font_size=22, color=GRAY_300).move_to(axes.c2p(7.7, 1.5)),
        )
        x_label = Text("Intelligence Value", font_size=24, color=GRAY_400).next_to(axes.x_axis, DOWN, buff=0.38)
        y_label = Text("Cost", font_size=24, color=GRAY_400).rotate(90 * 3.1415926535 / 180).next_to(axes.y_axis, LEFT, buff=0.44)

        points = {
            "green": Dot(axes.c2p(3.2, 7.4), radius=0.12, color=PRIMARY_GREEN),
            "blue": Dot(axes.c2p(6.8, 6.3), radius=0.11, color=PRIMARY_BLUE),
            "purple": Dot(axes.c2p(4.9, 3.8), radius=0.1, color=PRIMARY_PURPLE),
            "orange": Dot(axes.c2p(7.8, 2.4), radius=0.1, color=PRIMARY_ORANGE),
        }
        static_points = VGroup(points["blue"], points["purple"], points["orange"])

        moving_point = points["green"]
        target_position = axes.c2p(6.6, 4.4)
        target_marker = Dot(target_position, radius=0.075, color=PRIMARY_YELLOW, fill_opacity=0.7, stroke_width=0)
        arrow = Arrow(
            start=axes.c2p(3.55, 7.0),
            end=target_position + LEFT * 0.06 + UP * 0.06,
            buff=0.02,
            stroke_width=7,
            max_tip_length_to_length_ratio=0.18,
            color=PRIMARY_RED,
        )

        self.add(frame)
        self.play(Create(axes), run_time=0.3)
        self.play(FadeIn(quadrant_boxes), FadeIn(vertical_split), FadeIn(horizontal_split), FadeIn(quadrant_labels), FadeIn(x_label), FadeIn(y_label), run_time=0.28)
        self.play(FadeIn(moving_point), run_time=0.18)
        self.play(
            AnimationGroup(
                FadeIn(points["blue"]),
                FadeIn(points["purple"]),
                FadeIn(points["orange"]),
                lag_ratio=0.18,
            ),
            run_time=0.42,
        )
        self.play(FadeIn(target_marker), FadeIn(arrow), run_time=0.22)
        self.wait(0.18)
        self.play(FadeOut(arrow), run_time=0.18)
        self.play(moving_point.animate.move_to(target_position), run_time=0.54, rate_func=smooth)
        self.play(
            AnimationGroup(
                moving_point.animate.set_color(PRIMARY_YELLOW),
                static_points.animate.set_opacity(0.9),
                lag_ratio=0.0,
            ),
            run_time=0.16,
        )
        self.wait(0.3)


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
