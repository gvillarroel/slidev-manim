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
    Circle,
    Create,
    DashedLine,
    Dot,
    FadeIn,
    FadeOut,
    Line,
    Text,
    RoundedRectangle,
    Scene,
    VGroup,
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
WHITE = "#ffffff"
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
            width=12.65,
            height=6.85,
            corner_radius=0.34,
            stroke_color=GRAY_200,
            stroke_width=2,
            fill_color=WHITE,
            fill_opacity=0,
        )

        axes = Axes(
            x_range=[0, 10, 1],
            y_range=[0, 10, 1],
            x_length=8.25,
            y_length=5.05,
            axis_config={"stroke_color": GRAY_400, "stroke_width": 1.8, "include_ticks": False},
            tips=False,
        ).move_to(DOWN * 0.06 + RIGHT * 0.08)

        quadrant_boxes = VGroup(
            RoundedRectangle(width=4.1, height=2.5, corner_radius=0.14, stroke_width=0, fill_color=GRAY_100, fill_opacity=0.14).move_to(axes.c2p(2.5, 7.5)),
            RoundedRectangle(width=4.1, height=2.5, corner_radius=0.14, stroke_width=0, fill_color=GRAY_100, fill_opacity=0.09).move_to(axes.c2p(7.5, 7.5)),
            RoundedRectangle(width=4.1, height=2.5, corner_radius=0.14, stroke_width=0, fill_color=GRAY_100, fill_opacity=0.09).move_to(axes.c2p(2.5, 2.5)),
            RoundedRectangle(width=4.1, height=2.5, corner_radius=0.14, stroke_width=0, fill_color=GRAY_100, fill_opacity=0.14).move_to(axes.c2p(7.5, 2.5)),
        )
        vertical_split = RoundedRectangle(width=0.035, height=5.05, corner_radius=0.017, stroke_width=0, fill_color=GRAY_200, fill_opacity=0.55).move_to(axes.c2p(5, 5))
        horizontal_split = RoundedRectangle(width=8.25, height=0.035, corner_radius=0.017, stroke_width=0, fill_color=GRAY_200, fill_opacity=0.55).move_to(axes.c2p(5, 5))

        quadrant_labels = VGroup(
            Text("Quick Wins", font_size=24, color=GRAY_300).move_to(axes.c2p(2.0, 8.45)),
            Text("Premium Bets", font_size=24, color=GRAY_300).move_to(axes.c2p(7.8, 8.45)),
            Text("Low Yield", font_size=24, color=GRAY_300).move_to(axes.c2p(2.0, 1.55)),
            Text("Scale Plays", font_size=24, color=GRAY_300).move_to(axes.c2p(7.7, 1.55)),
        )
        x_label = Text("Intelligence Value", font_size=24, color=GRAY_400).next_to(axes.x_axis, DOWN, buff=0.38)
        y_label = Text("Cost", font_size=24, color=GRAY_400).rotate(90 * 3.1415926535 / 180).next_to(axes.y_axis, LEFT, buff=0.44)

        points = {
            "green": Dot(axes.c2p(3.2, 7.4), radius=0.135, color=PRIMARY_GREEN),
            "blue": Dot(axes.c2p(6.8, 6.3), radius=0.11, color=PRIMARY_BLUE),
            "purple": Dot(axes.c2p(4.9, 3.8), radius=0.1, color=PRIMARY_PURPLE),
            "orange": Dot(axes.c2p(7.8, 2.4), radius=0.1, color=PRIMARY_ORANGE),
        }
        static_points = VGroup(points["blue"], points["purple"], points["orange"])

        moving_point = points["green"]
        drop_position = axes.c2p(3.2, 4.4)
        target_position = axes.c2p(6.6, 4.4)
        target_marker = Circle(radius=0.18, stroke_color=PRIMARY_YELLOW, stroke_width=5, fill_opacity=0).move_to(target_position)
        drop_marker = Dot(drop_position, radius=0.055, color=PRIMARY_YELLOW, fill_opacity=0.72, stroke_width=0)
        landing_rail = Line(
            drop_position + RIGHT * 0.12,
            target_position + LEFT * 0.22,
            stroke_color=PRIMARY_ORANGE,
            stroke_width=4,
        ).set_opacity(0.38)
        drop_lane = DashedLine(
            moving_point.get_center() + DOWN * 0.22,
            drop_position + UP * 0.16,
            dash_length=0.13,
            dashed_ratio=0.56,
            stroke_color=PRIMARY_ORANGE,
            stroke_width=3.2,
        ).set_opacity(0.42)
        arrow = Arrow(
            start=moving_point.get_center() + DOWN * 0.3,
            end=drop_position + UP * 0.26,
            buff=0.02,
            stroke_width=8,
            max_tip_length_to_length_ratio=0.14,
            color=PRIMARY_RED,
        )

        self.add(frame, axes, quadrant_boxes, vertical_split, horizontal_split, quadrant_labels, x_label, y_label)
        self.wait(3.0)
        self.play(FadeIn(moving_point, scale=1.2), run_time=0.8)
        self.play(
            AnimationGroup(
                FadeIn(points["blue"], scale=1.15),
                FadeIn(points["purple"], scale=1.15),
                FadeIn(points["orange"], scale=1.15),
                lag_ratio=0.32,
            ),
            run_time=2.0,
        )
        self.wait(1.0)
        self.play(FadeIn(target_marker), FadeIn(drop_marker), Create(landing_rail), Create(drop_lane), run_time=1.0)
        self.play(Create(arrow), run_time=1.1)
        self.wait(2.5)
        self.play(FadeOut(arrow), run_time=0.8)
        self.wait(0.6)
        self.play(moving_point.animate.move_to(drop_position), run_time=2.6, rate_func=smooth)
        self.wait(0.6)
        self.play(moving_point.animate.move_to(target_position), run_time=2.6, rate_func=smooth)
        self.play(
            AnimationGroup(
                moving_point.animate.set_color(PRIMARY_YELLOW),
                static_points.animate.set_opacity(0.9),
                lag_ratio=0.0,
            ),
            run_time=0.8,
        )
        self.play(FadeOut(drop_lane), FadeOut(landing_rail), FadeOut(drop_marker), run_time=0.8)
        self.wait(7.5)


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
