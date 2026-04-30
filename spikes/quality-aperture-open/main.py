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

PRIMARY_RED = "#9E1B32"
PRIMARY_ORANGE = "#E77204"
PRIMARY_YELLOW = "#F1C319"
PRIMARY_GREEN = "#45842A"
PRIMARY_BLUE = "#007298"
PRIMARY_PURPLE = "#652F6C"
GRAY_100 = "#E7E7E7"
GRAY_200 = "#CFCFCF"


class _Args(argparse.Namespace):
    quality: str


def parse_args() -> _Args:
    parser = argparse.ArgumentParser(description="Render the quality-aperture-open spike.")
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
        "QualityApertureOpenScene",
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


def slab(color: str, width: float, height: float, opacity: float = 1) -> RoundedRectangle:
    return RoundedRectangle(width=width, height=height, corner_radius=0.3, stroke_width=0, fill_color=color, fill_opacity=opacity)


class QualityApertureOpenScene(Scene):
    def construct(self) -> None:
        self.camera.background_color = WHITE

        frame = RoundedRectangle(width=12.9, height=5.8, corner_radius=0.34, stroke_color=GRAY_200, stroke_width=2, fill_color=WHITE, fill_opacity=0)
        source_zone = RoundedRectangle(width=4.1, height=4.25, corner_radius=0.35, stroke_width=0, fill_color=GRAY_100, fill_opacity=0.22).move_to(LEFT * 3.0)
        target_zone = RoundedRectangle(width=4.15, height=4.25, corner_radius=0.35, stroke_width=0, fill_color=GRAY_100, fill_opacity=0.28).move_to(RIGHT * 2.9)

        source = VGroup(
            slab(PRIMARY_GREEN, 2.55, 0.9).move_to(LEFT * 3.3 + UP * 0.7),
            slab(PRIMARY_BLUE, 1.84, 0.82).move_to(LEFT * 2.16 + DOWN * 0.08),
            slab(PRIMARY_PURPLE, 1.4, 0.68).move_to(LEFT * 1.6 + DOWN * 1.0),
        )

        guide = Line(LEFT * 0.95 + DOWN * 0.02, RIGHT * 0.9 + DOWN * 0.02, color=PRIMARY_ORANGE, stroke_width=6)
        accent = Circle(radius=0.12, stroke_width=0, fill_color=PRIMARY_YELLOW, fill_opacity=1).move_to(guide.get_start())

        shutter_top = slab(GRAY_200, 3.6, 1.08, opacity=0.74).move_to(RIGHT * 2.9 + UP * 0.48)
        shutter_bottom = slab(GRAY_200, 3.6, 1.08, opacity=0.74).move_to(RIGHT * 2.9 + DOWN * 0.48)

        reveal_green = slab(PRIMARY_GREEN, 2.05, 0.72).move_to(RIGHT * 2.58 + UP * 0.02)
        reveal_blue = slab(PRIMARY_BLUE, 1.56, 0.64).move_to(RIGHT * 3.52 + DOWN * 0.18)
        reveal_purple = slab(PRIMARY_PURPLE, 1.08, 0.5).move_to(RIGHT * 2.98 + DOWN * 0.72)

        final_green = Circle(radius=0.82, stroke_width=0, fill_color=PRIMARY_GREEN, fill_opacity=1).move_to(RIGHT * 2.48 + UP * 0.4)
        final_blue = Circle(radius=0.5, stroke_width=0, fill_color=PRIMARY_BLUE, fill_opacity=1).move_to(RIGHT * 3.66 + DOWN * 0.02)
        final_purple = Circle(radius=0.26, stroke_width=0, fill_color=PRIMARY_PURPLE, fill_opacity=1).move_to(RIGHT * 3.0 + DOWN * 0.98)

        self.add(frame, source_zone, target_zone)
        self.play(FadeIn(source, lag_ratio=0.08), run_time=0.7)
        self.play(FadeIn(guide), run_time=0.14)
        self.play(MoveAlongPath(accent, guide), run_time=0.34)
        self.play(FadeIn(shutter_top), FadeIn(shutter_bottom), run_time=0.16)
        self.play(
            AnimationGroup(
                Transform(source[0], reveal_green.copy()),
                Transform(source[1], reveal_blue.copy()),
                Transform(source[2], reveal_purple.copy()),
                lag_ratio=0.06,
            ),
            run_time=0.6,
            rate_func=smooth,
        )
        self.play(
            shutter_top.animate.shift(UP * 0.9),
            shutter_bottom.animate.shift(DOWN * 0.9),
            run_time=0.26,
            rate_func=smooth,
        )
        self.play(FadeOut(shutter_top), FadeOut(shutter_bottom), FadeOut(guide), run_time=0.12)
        self.play(
            AnimationGroup(
                Transform(source[0], final_green.copy()),
                Transform(source[1], final_blue.copy()),
                Transform(source[2], final_purple.copy()),
                lag_ratio=0.06,
            ),
            run_time=0.68,
            rate_func=smooth,
        )
        self.play(accent.animate.move_to(RIGHT * 2.88 + DOWN * 0.02).set_fill(PRIMARY_RED, opacity=1), run_time=0.16)
        for item in source:
            self.play(item.animate.scale(1.05), run_time=0.12, rate_func=there_and_back)
        self.play(FadeOut(accent), run_time=0.14)
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
