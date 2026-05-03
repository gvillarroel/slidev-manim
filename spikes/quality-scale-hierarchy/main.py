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
    MoveAlongPath,
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
        "--transparent",
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


def plate(color: str, width: float, height: float) -> Rectangle:
    return Rectangle(width=width, height=height, stroke_width=0, fill_color=color, fill_opacity=1)


class QualityScaleHierarchyScene(Scene):
    def construct(self) -> None:
        self.camera.background_color = WHITE
        self.camera.background_opacity = 0

        frame = Rectangle(width=12.4, height=5.9, stroke_color=GRAY_200, stroke_width=2, fill_opacity=0)
        source_rail = Line(LEFT * 5.75 + UP * 1.55, LEFT * 5.75 + DOWN * 1.55, stroke_color=GRAY_200, stroke_width=4)
        destination_plate = Rectangle(
            width=5.7,
            height=4.45,
            stroke_width=0,
            fill_color=GRAY_100,
            fill_opacity=0.28,
        ).move_to(RIGHT * 1.7 + DOWN * 0.06)

        source = VGroup(
            plate(PRIMARY_GREEN, 1.62, 0.62).move_to(LEFT * 4.48 + UP * 1.08),
            plate(PRIMARY_BLUE, 1.62, 0.62).move_to(LEFT * 4.48),
            plate(PRIMARY_PURPLE, 1.62, 0.62).move_to(LEFT * 4.48 + DOWN * 1.08),
        )

        targets = VGroup(
            Circle(radius=1.2, stroke_width=0, fill_color=PRIMARY_GREEN, fill_opacity=1).move_to(RIGHT * 0.65 + UP * 0.58),
            Circle(radius=0.66, stroke_width=0, fill_color=PRIMARY_BLUE, fill_opacity=1).move_to(RIGHT * 3.18 + DOWN * 0.18),
            Circle(radius=0.38, stroke_width=0, fill_color=PRIMARY_PURPLE, fill_opacity=1).move_to(RIGHT * 2.06 + DOWN * 1.52),
        )

        destination_slots = VGroup(
            Circle(radius=1.31, stroke_color=PRIMARY_GREEN, stroke_width=3, fill_color=PRIMARY_GREEN, fill_opacity=0.08).move_to(targets[0]),
            Circle(radius=0.76, stroke_color=PRIMARY_BLUE, stroke_width=3, fill_color=PRIMARY_BLUE, fill_opacity=0.08).move_to(targets[1]),
            Circle(radius=0.47, stroke_color=PRIMARY_PURPLE, stroke_width=3, fill_color=PRIMARY_PURPLE, fill_opacity=0.08).move_to(targets[2]),
        ).set_opacity(0.42)

        routes = VGroup(
            Line(source[0].get_right() + RIGHT * 0.18, targets[0].get_left() + LEFT * 0.16, stroke_color=GRAY_200, stroke_width=3),
            Line(source[1].get_right() + RIGHT * 0.18, targets[1].get_left() + LEFT * 0.16, stroke_color=GRAY_200, stroke_width=3),
            Line(source[2].get_right() + RIGHT * 0.18, targets[2].get_left() + LEFT * 0.16, stroke_color=GRAY_200, stroke_width=3),
        ).set_opacity(0.35)

        accent = Circle(radius=0.13, stroke_width=0, fill_color=PRIMARY_RED, fill_opacity=1)
        proof_ring = Circle(radius=1.36, stroke_color=PRIMARY_RED, stroke_width=5, fill_opacity=0).move_to(targets[0])
        final_brackets = VGroup(
            Line(LEFT * 0.92 + UP * 1.98, LEFT * 0.27 + UP * 1.98, stroke_color=PRIMARY_RED, stroke_width=5),
            Line(LEFT * 0.92 + UP * 1.98, LEFT * 0.92 + UP * 1.33, stroke_color=PRIMARY_RED, stroke_width=5),
            Line(RIGHT * 3.72 + DOWN * 2.22, RIGHT * 3.05 + DOWN * 2.22, stroke_color=PRIMARY_RED, stroke_width=5),
            Line(RIGHT * 3.72 + DOWN * 2.22, RIGHT * 3.72 + DOWN * 1.55, stroke_color=PRIMARY_RED, stroke_width=5),
        ).set_opacity(0.0)

        self.add(frame, destination_plate, source_rail, routes, destination_slots, source)
        self.wait(3.0)

        for index, (shape, target, route, slot) in enumerate(zip(source, targets, routes, destination_slots)):
            active_route = route.copy().set_stroke(PRIMARY_RED, width=5, opacity=1)
            accent.move_to(shape.get_right())
            self.play(
                Create(active_route),
                FadeIn(accent),
                slot.animate.set_opacity(0.72),
                run_time=0.45,
            )
            self.play(MoveAlongPath(accent, active_route), run_time=1.35 - index * 0.12, rate_func=linear)
            self.play(
                Transform(shape, target),
                FadeOut(active_route),
                slot.animate.set_opacity(0.24),
                run_time=1.35 - index * 0.1,
                rate_func=smooth,
            )
            self.play(FadeOut(accent), run_time=0.22)
            self.wait(0.48)

        self.play(
            FadeOut(routes),
            FadeOut(destination_slots),
            FadeOut(source_rail),
            FadeOut(frame),
            destination_plate.animate.set_opacity(0.16),
            source.animate.shift(LEFT * 1.6),
            proof_ring.animate.shift(LEFT * 1.6),
            final_brackets.animate.shift(LEFT * 1.6),
            run_time=1.25,
        )
        self.play(Create(proof_ring), run_time=0.8)
        self.play(
            AnimationGroup(
                source[0].animate.scale(1.08),
                source[1].animate.shift(RIGHT * 0.24 + DOWN * 0.06),
                source[2].animate.shift(RIGHT * 0.16 + DOWN * 0.18),
                lag_ratio=0.08,
            ),
            run_time=1.0,
            rate_func=smooth,
        )
        self.wait(1.4)
        self.play(
            FadeOut(proof_ring),
            destination_plate.animate.set_opacity(0.0),
            final_brackets.animate.set_opacity(1),
            run_time=1.2,
        )
        self.play(FadeOut(final_brackets), run_time=0.8)
        self.wait(7.0)


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
