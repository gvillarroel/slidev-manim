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
    PI,
    RIGHT,
    UP,
    AnimationGroup,
    Arc,
    ArcBetweenPoints,
    Circle,
    Dot,
    FadeIn,
    FadeOut,
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
    parser = argparse.ArgumentParser(description="Render the quality-anchored-orbit spike.")
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
        "QualityAnchoredOrbitScene",
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
    return RoundedRectangle(width=width, height=height, corner_radius=0.28, stroke_width=0, fill_color=color, fill_opacity=1)


class QualityAnchoredOrbitScene(Scene):
    def construct(self) -> None:
        self.camera.background_color = WHITE

        anchor_center = RIGHT * 1.05

        frame = RoundedRectangle(
            width=12.15,
            height=5.95,
            corner_radius=0.34,
            stroke_color=GRAY_200,
            stroke_width=2,
            fill_color=WHITE,
            fill_opacity=0,
        )
        source_stage = RoundedRectangle(
            width=3.15,
            height=3.55,
            corner_radius=0.28,
            stroke_color=GRAY_200,
            stroke_width=2,
            fill_color=GRAY_100,
            fill_opacity=0.24,
        ).move_to(LEFT * 3.55)
        orbit_zone = Circle(radius=2.0, stroke_width=0, fill_color=GRAY_100, fill_opacity=0.34).move_to(anchor_center)

        anchor = Circle(radius=0.78, stroke_width=0, fill_color=PRIMARY_GREEN, fill_opacity=1).move_to(anchor_center)
        blue_start = LEFT * 3.85 + UP * 0.85
        purple_start = LEFT * 3.35 + DOWN * 0.88
        satellite_1 = chip(PRIMARY_BLUE, 1.72, 0.72).move_to(blue_start)
        satellite_2 = chip(PRIMARY_PURPLE, 1.5, 0.66).move_to(purple_start)

        blue_slot = chip(PRIMARY_BLUE, 1.58, 0.62).set_opacity(0.2).move_to(anchor_center + RIGHT * 1.55 + UP * 0.62)
        purple_slot = chip(PRIMARY_PURPLE, 1.36, 0.56).set_opacity(0.2).move_to(anchor_center + LEFT * 0.9 + DOWN * 1.5)
        slot_group = VGroup(blue_slot, purple_slot)

        approach_1 = Arc(radius=2.08, start_angle=PI * 0.98, angle=-0.58 * PI, arc_center=anchor_center, color=PRIMARY_ORANGE, stroke_width=5)
        approach_2 = ArcBetweenPoints(
            purple_start,
            purple_slot.get_center(),
            angle=0.82 * PI,
            color=PRIMARY_ORANGE,
            stroke_width=5,
        )
        inner_echo = Arc(radius=1.24, start_angle=PI * 0.08, angle=0.34 * PI, arc_center=anchor_center, color=PRIMARY_ORANGE, stroke_width=3).set_opacity(0.42)
        orbit_guides = VGroup(approach_1, approach_2, inner_echo)
        accent_1 = Dot(anchor_center + LEFT * 2.08, radius=0.08, color=PRIMARY_YELLOW)
        accent_2 = Dot(anchor_center + LEFT * 1.74 + DOWN * 0.15, radius=0.08, color=PRIMARY_YELLOW)
        final_pulse = Circle(radius=0.96, stroke_color=PRIMARY_YELLOW, stroke_width=4, fill_opacity=0).move_to(anchor_center)

        self.add(frame, source_stage, orbit_zone, anchor, satellite_1, satellite_2, slot_group)
        self.wait(2.6)

        self.play(
            source_stage.animate.set_fill(GRAY_100, opacity=0.16),
            FadeIn(orbit_guides),
            slot_group.animate.set_opacity(0.34),
            run_time=2.0,
        )
        self.wait(1.1)

        self.play(
            MoveAlongPath(accent_1, approach_1),
            anchor.animate.scale(1.06),
            run_time=1.8,
            rate_func=linear,
        )
        self.play(anchor.animate.scale(1 / 1.06), run_time=0.45, rate_func=smooth)
        self.play(
            AnimationGroup(
                MoveAlongPath(satellite_1, approach_1),
                blue_slot.animate.set_opacity(0.46),
                lag_ratio=0.0,
            ),
            run_time=3.1,
            rate_func=smooth,
        )
        self.play(blue_slot.animate.set_opacity(0.08), run_time=0.45, rate_func=smooth)
        self.wait(0.55)

        self.play(
            FadeOut(accent_1),
            MoveAlongPath(accent_2, approach_2),
            purple_slot.animate.set_opacity(0.42),
            run_time=1.7,
            rate_func=linear,
        )
        self.play(
            AnimationGroup(
                MoveAlongPath(satellite_2, approach_2),
                anchor.animate.scale(1.05),
                lag_ratio=0.0,
            ),
            run_time=3.0,
            rate_func=smooth,
        )
        self.play(anchor.animate.scale(1 / 1.05), purple_slot.animate.set_opacity(0.08), run_time=0.45, rate_func=smooth)
        self.wait(0.9)

        self.play(
            Transform(satellite_1, chip(PRIMARY_BLUE, 1.58, 0.62).move_to(blue_slot)),
            Transform(satellite_2, chip(PRIMARY_PURPLE, 1.36, 0.56).move_to(purple_slot)),
            FadeOut(accent_2),
            run_time=1.8,
            rate_func=smooth,
        )
        self.play(
            FadeOut(orbit_guides),
            FadeOut(slot_group),
            source_stage.animate.set_opacity(0),
            run_time=1.25,
        )
        resolved_cluster = VGroup(orbit_zone, anchor, satellite_1, satellite_2)
        self.play(resolved_cluster.animate.shift(LEFT * 0.62), run_time=1.15, rate_func=smooth)
        final_pulse.move_to(anchor.get_center())
        self.play(final_pulse.animate.scale(1.35).set_stroke(opacity=0), run_time=1.1, rate_func=smooth)
        self.play(
            anchor.animate.scale(1.04),
            satellite_1.animate.scale(1.025),
            satellite_2.animate.scale(1.025),
            run_time=0.45,
            rate_func=there_and_back,
        )
        self.wait(6.8)


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
