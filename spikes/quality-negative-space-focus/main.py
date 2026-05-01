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
    parser = argparse.ArgumentParser(description="Render the quality-negative-space-focus spike.")
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
        "QualityNegativeSpaceFocusScene",
    ]
    if poster:
        command.insert(-2, "-s")
    return command


def promote(target_name: str, destination: Path) -> None:
    matches = sorted(STAGING_DIR.glob(f"**/{target_name}"), key=lambda path: path.stat().st_mtime)
    if not matches:
        raise FileNotFoundError(target_name)
    destination.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(matches[-1], destination)


def tile(color: str, width: float, height: float) -> Rectangle:
    return Rectangle(
        width=width,
        height=height,
        stroke_width=0,
        fill_color=color,
        fill_opacity=1,
    )


def orb(color: str, radius: float) -> Circle:
    return Circle(radius=radius, stroke_width=0, fill_color=color, fill_opacity=1)


class QualityNegativeSpaceFocusScene(Scene):
    def construct(self) -> None:
        self.camera.background_color = WHITE

        frame = Rectangle(
            width=12.55,
            height=5.55,
            stroke_color=GRAY_200,
            stroke_width=2,
            fill_color=WHITE,
            fill_opacity=0,
        )
        frame.set_z_index(5)
        source_zone = Rectangle(
            width=4.15,
            height=3.85,
            stroke_width=0,
            fill_color=GRAY_100,
            fill_opacity=0.45,
        ).move_to(LEFT * 3.15 + DOWN * 0.05)
        source_zone.set_z_index(0)
        destination_zone = Rectangle(
            width=3.05,
            height=3.58,
            stroke_width=0,
            fill_color=GRAY_100,
            fill_opacity=0.18,
        ).move_to(RIGHT * 2.22 + DOWN * 0.08)
        destination_zone.set_z_index(0)

        source_tiles = VGroup(
            tile(PRIMARY_GREEN, 2.2, 1.25).move_to(LEFT * 4.05 + UP * 0.9),
            tile(PRIMARY_BLUE, 2.2, 1.15).move_to(LEFT * 2.95 + DOWN * 0.15),
            tile(PRIMARY_PURPLE, 2.0, 1.05).move_to(LEFT * 1.85 + DOWN * 1.15),
        )
        source_tiles.set_z_index(3)
        destination_group = VGroup(
            orb(PRIMARY_GREEN, 0.68).move_to(RIGHT * 2.75 + UP * 0.9),
            orb(PRIMARY_BLUE, 0.54).move_to(RIGHT * 1.32 + DOWN * 0.22),
            orb(PRIMARY_PURPLE, 0.48).move_to(RIGHT * 2.45 + DOWN * 1.2),
        )

        target_slots = VGroup(
            Circle(radius=0.82, stroke_color=PRIMARY_GREEN, stroke_width=4, stroke_opacity=0.24, fill_opacity=0).move_to(destination_group[0]),
            Circle(radius=0.67, stroke_color=PRIMARY_BLUE, stroke_width=4, stroke_opacity=0.22, fill_opacity=0).move_to(destination_group[1]),
            Circle(radius=0.59, stroke_color=PRIMARY_PURPLE, stroke_width=4, stroke_opacity=0.22, fill_opacity=0).move_to(destination_group[2]),
        )
        target_slots.set_z_index(1)

        route_gap = RIGHT * 0.36
        guide_lines = [
            Line(source_tiles[0].get_right() + route_gap, destination_group[0].get_left() - route_gap, color=PRIMARY_ORANGE, stroke_width=6).set_z_index(2),
            Line(source_tiles[1].get_right() + route_gap, destination_group[1].get_left() - route_gap, color=PRIMARY_ORANGE, stroke_width=6).set_z_index(2),
            Line(source_tiles[2].get_right() + route_gap, destination_group[2].get_left() - route_gap, color=PRIMARY_ORANGE, stroke_width=6).set_z_index(2),
        ]

        pulse = Circle(radius=0.16, stroke_width=0, fill_color=PRIMARY_YELLOW, fill_opacity=1).move_to(source_tiles[0].get_center() + RIGHT * 0.2)
        pulse.set_z_index(4)

        self.add(frame, source_zone, destination_zone, target_slots, source_tiles, pulse)
        self.wait(2.4)

        route_scaffold = VGroup(*(line.copy().set_stroke(width=2.4, opacity=0.22).set_z_index(1) for line in guide_lines))
        self.play(FadeIn(route_scaffold, lag_ratio=0.16), run_time=0.9)
        self.wait(0.55)

        for index, guide in enumerate(guide_lines):
            active_guide = guide.copy().set_stroke(width=7, opacity=0.9).set_z_index(2)
            self.play(FadeIn(active_guide), run_time=0.35)
            self.play(MoveAlongPath(pulse, active_guide), run_time=2.15, rate_func=linear)
            self.play(
                AnimationGroup(
                    Transform(source_tiles[index], destination_group[index]),
                    FadeOut(target_slots[index]),
                    lag_ratio=0,
                ),
                run_time=1.25,
                rate_func=smooth,
            )
            self.play(FadeOut(active_guide), FadeOut(route_scaffold[index]), run_time=0.35)
            if index < len(guide_lines) - 1:
                self.play(pulse.animate.move_to(source_tiles[index + 1].get_center() + RIGHT * 0.2), run_time=0.55)
                self.wait(0.35)

        self.remove(route_scaffold)
        resolve_shift = LEFT * 1.15
        self.play(
            AnimationGroup(
                FadeOut(source_zone),
                destination_zone.animate.set_fill(opacity=0.42).scale(1.06).shift(resolve_shift),
                source_tiles.animate.shift(resolve_shift),
                FadeOut(pulse),
                lag_ratio=0.05,
            ),
            run_time=1.35,
            rate_func=smooth,
        )
        terminal_focus = Rectangle(
            width=3.5,
            height=3.95,
            stroke_color=PRIMARY_RED,
            stroke_width=4,
            stroke_opacity=0.68,
            fill_opacity=0,
        ).move_to(destination_zone)
        terminal_focus.set_z_index(2)
        self.play(FadeIn(terminal_focus), run_time=0.4)
        for dot in source_tiles:
            self.play(dot.animate.scale(1.08), run_time=0.42, rate_func=there_and_back)
        self.play(terminal_focus.animate.set_stroke(opacity=0.18).scale(1.04), run_time=0.55)
        self.play(FadeOut(terminal_focus), run_time=0.4)
        self.wait(6.2)


def render_variant(args: _Args) -> None:
    video_path, poster_path = output_paths()

    if STAGING_DIR.exists():
        shutil.rmtree(STAGING_DIR)

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
