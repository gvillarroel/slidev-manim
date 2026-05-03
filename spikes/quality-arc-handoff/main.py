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
    ArcBetweenPoints,
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
    MoveAlongPath,
    RoundedRectangle,
    Scene,
    Transform,
    VGroup,
    WHITE,
    config,
    rate_functions,
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

config.transparent = True
config.background_opacity = 0.0


class _Args(argparse.Namespace):
    quality: str


def parse_args() -> _Args:
    parser = argparse.ArgumentParser(description="Render the quality-arc-handoff spike.")
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
        "QualityArcHandoffScene",
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


def slab(color: str, width: float, height: float) -> RoundedRectangle:
    return RoundedRectangle(width=width, height=height, corner_radius=0, stroke_width=0, fill_color=color, fill_opacity=1)


def bracket_slot(width: float, height: float, arm: float = 0.22, stroke_width: float = 2) -> VGroup:
    x = width / 2
    y = height / 2
    arm = min(arm, width * 0.28, height * 0.28)
    corners = VGroup(
        Line(LEFT * x + UP * y, LEFT * (x - arm) + UP * y),
        Line(LEFT * x + UP * y, LEFT * x + UP * (y - arm)),
        Line(RIGHT * x + UP * y, RIGHT * (x - arm) + UP * y),
        Line(RIGHT * x + UP * y, RIGHT * x + UP * (y - arm)),
        Line(LEFT * x + DOWN * y, LEFT * (x - arm) + DOWN * y),
        Line(LEFT * x + DOWN * y, LEFT * x + DOWN * (y - arm)),
        Line(RIGHT * x + DOWN * y, RIGHT * (x - arm) + DOWN * y),
        Line(RIGHT * x + DOWN * y, RIGHT * x + DOWN * (y - arm)),
    )
    corners.set_stroke(GRAY_200, width=stroke_width, opacity=0.46)
    return corners


class QualityArcHandoffScene(Scene):
    def construct(self) -> None:
        self.camera.background_color = WHITE
        self.camera.background_opacity = 0.0

        frame = RoundedRectangle(width=12.45, height=5.45, corner_radius=0, stroke_color=GRAY_200, stroke_width=2, fill_color=WHITE, fill_opacity=0)
        source_zone = RoundedRectangle(width=3.7, height=3.65, corner_radius=0, stroke_width=0, fill_color=GRAY_100, fill_opacity=0.2).move_to(LEFT * 3.45)
        target_zone = RoundedRectangle(width=4.45, height=3.95, corner_radius=0, stroke_width=0, fill_color=GRAY_100, fill_opacity=0.24).move_to(RIGHT * 3.2 + DOWN * 0.05)

        source = VGroup(
            slab(PRIMARY_GREEN, 2.45, 0.74).move_to(LEFT * 3.55 + UP * 0.88),
            slab(PRIMARY_BLUE, 1.84, 0.66).move_to(LEFT * 3.2 + DOWN * 0.08),
            slab(PRIMARY_PURPLE, 1.34, 0.52).move_to(LEFT * 2.82 + DOWN * 0.92),
        )

        target_slots = VGroup(
            bracket_slot(2.05, 2.05, arm=0.24).move_to(RIGHT * 2.62 + UP * 0.65),
            bracket_slot(1.36, 1.36, arm=0.18).move_to(RIGHT * 4.05 + DOWN * 0.42),
            bracket_slot(0.82, 0.82, arm=0.13).move_to(RIGHT * 2.6 + DOWN * 1.18),
        ).set_opacity(0.62)

        main_arc = ArcBetweenPoints(start=LEFT * 2.32 + UP * 1.24, end=RIGHT * 3.44 + UP * 1.29, angle=-1.08, color=PRIMARY_ORANGE, stroke_width=6)
        support_arc = ArcBetweenPoints(start=LEFT * 2.26 + DOWN * 0.72, end=RIGHT * 3.44 + DOWN * 0.92, angle=-0.34, color=GRAY_200, stroke_width=4)
        lower_arc = ArcBetweenPoints(start=LEFT * 2.02 + DOWN * 1.5, end=RIGHT * 2.46 + DOWN * 1.72, angle=-0.28, color=GRAY_200, stroke_width=3)
        guide_group = VGroup(main_arc, support_arc, lower_arc)

        accent = Circle(radius=0.14, stroke_width=0, fill_color=PRIMARY_YELLOW, fill_opacity=1).move_to(main_arc.get_start())

        handoff_green = slab(PRIMARY_GREEN, 2.05, 0.62).move_to(RIGHT * 2.62 + UP * 0.95)
        support_blue = slab(PRIMARY_BLUE, 1.42, 0.54).move_to(RIGHT * 3.22 + DOWN * 0.18)
        support_purple = slab(PRIMARY_PURPLE, 1.0, 0.42).move_to(RIGHT * 2.34 + DOWN * 1.08)

        final_green = Circle(radius=0.86, stroke_width=0, fill_color=PRIMARY_GREEN, fill_opacity=1).move_to(RIGHT * 2.62 + UP * 0.65)
        final_blue = Circle(radius=0.52, stroke_width=0, fill_color=PRIMARY_BLUE, fill_opacity=1).move_to(RIGHT * 4.05 + DOWN * 0.42)
        final_purple = Circle(radius=0.29, stroke_width=0, fill_color=PRIMARY_PURPLE, fill_opacity=1).move_to(RIGHT * 2.6 + DOWN * 1.18)

        self.add(frame, source_zone, target_zone, target_slots, source)
        self.wait(2.7)

        self.play(Create(main_arc), FadeIn(accent), run_time=1.35)
        self.wait(0.9)

        self.play(
            MoveAlongPath(accent, main_arc),
            Transform(source[0], handoff_green.copy()),
            run_time=4.2,
            rate_func=smooth,
        )
        self.wait(1.2)

        self.play(
            AnimationGroup(
                Create(support_arc),
                Create(lower_arc),
                Transform(source[1], support_blue.copy()),
                Transform(source[2], support_purple.copy()),
                lag_ratio=0.16,
            ),
            run_time=3.4,
            rate_func=smooth,
        )
        self.wait(0.9)

        self.play(FadeOut(target_slots), run_time=0.45)

        self.play(
            AnimationGroup(
                Transform(source[0], final_green.copy()),
                Transform(source[1], final_blue.copy()),
                Transform(source[2], final_purple.copy()),
                FadeOut(guide_group, shift=UP * 0.06),
                FadeOut(accent),
                lag_ratio=0.04,
            ),
            run_time=4.15,
            rate_func=rate_functions.ease_in_out_cubic,
        )
        self.wait(1.0)

        self.play(
            source.animate.shift(LEFT * 2.45),
            target_zone.animate.set_opacity(0.16).move_to(RIGHT * 0.58 + DOWN * 0.06),
            run_time=1.65,
            rate_func=rate_functions.ease_out_cubic,
        )
        self.play(
            FadeOut(source_zone),
            FadeOut(frame),
            run_time=0.55,
        )
        self.wait(6.3)


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
