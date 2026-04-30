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
    CubicBezier,
    FadeIn,
    FadeOut,
    RoundedRectangle,
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
    parser = argparse.ArgumentParser(description="Render the quality-parallax-transfer spike.")
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
        "QualityParallaxTransferScene",
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
    return RoundedRectangle(width=width, height=height, corner_radius=0.3, stroke_width=0, fill_color=color, fill_opacity=1)


class QualityParallaxTransferScene(Scene):
    def construct(self) -> None:
        self.camera.background_color = WHITE

        frame = RoundedRectangle(width=12.9, height=5.8, corner_radius=0.34, stroke_color=GRAY_200, stroke_width=2, fill_color=WHITE, fill_opacity=0)
        source_zone = RoundedRectangle(width=3.95, height=4.1, corner_radius=0.35, stroke_width=0, fill_color=GRAY_100, fill_opacity=0.22).move_to(LEFT * 3.15)
        mid_zone = RoundedRectangle(width=2.15, height=3.4, corner_radius=0.3, stroke_width=0, fill_color=GRAY_100, fill_opacity=0.16).move_to(RIGHT * 0.1)
        target_zone = RoundedRectangle(width=4.1, height=4.1, corner_radius=0.35, stroke_width=0, fill_color=GRAY_100, fill_opacity=0.28).move_to(RIGHT * 3.0)

        green = slab(PRIMARY_GREEN, 2.7, 0.92).move_to(LEFT * 3.3 + UP * 0.74)
        blue = slab(PRIMARY_BLUE, 1.9, 0.82).move_to(LEFT * 2.18 + DOWN * 0.02)
        purple = slab(PRIMARY_PURPLE, 1.34, 0.62).move_to(LEFT * 1.58 + DOWN * 0.98)
        source = VGroup(green, blue, purple)

        path = CubicBezier(
            LEFT * 0.78 + DOWN * 0.08,
            RIGHT * 0.18 + UP * 0.54,
            RIGHT * 1.32 + UP * 0.76,
            RIGHT * 2.08 + UP * 0.2,
            color=PRIMARY_ORANGE,
            stroke_width=6,
        )
        accent = Circle(radius=0.12, stroke_width=0, fill_color=PRIMARY_YELLOW, fill_opacity=1).move_to(path.get_start())

        green_mid = slab(PRIMARY_GREEN, 2.26, 0.82).move_to(RIGHT * 1.34 + UP * 0.8)
        blue_mid = slab(PRIMARY_BLUE, 1.64, 0.72).move_to(LEFT * 0.1 + DOWN * 0.02)
        purple_mid = slab(PRIMARY_PURPLE, 1.02, 0.52).move_to(RIGHT * 0.44 + DOWN * 1.0)

        final_green = Circle(radius=0.92, stroke_width=0, fill_color=PRIMARY_GREEN, fill_opacity=1).move_to(RIGHT * 2.62 + UP * 0.44)
        final_blue = Circle(radius=0.44, stroke_width=0, fill_color=PRIMARY_BLUE, fill_opacity=1).move_to(RIGHT * 3.76 + DOWN * 0.06)
        final_purple = Circle(radius=0.24, stroke_width=0, fill_color=PRIMARY_PURPLE, fill_opacity=1).move_to(RIGHT * 3.0 + DOWN * 1.06)

        self.add(frame, source_zone, mid_zone, target_zone)
        self.play(FadeIn(source, lag_ratio=0.08), run_time=0.68)
        self.play(FadeIn(path), run_time=0.16)
        self.play(accent.animate.move_to(LEFT * 0.18 + UP * 0.16), Transform(green, green_mid.copy()), run_time=0.24, rate_func=smooth)
        self.play(
            AnimationGroup(
                Transform(blue, blue_mid.copy()),
                Transform(purple, purple_mid.copy()),
                lag_ratio=0.12,
            ),
            run_time=0.28,
            rate_func=smooth,
        )
        self.play(accent.animate.move_to(path.get_end()), run_time=0.18, rate_func=smooth)
        self.play(
            AnimationGroup(
                Transform(green, final_green.copy()),
                Transform(blue, final_blue.copy()),
                Transform(purple, final_purple.copy()),
                lag_ratio=0.08,
            ),
            run_time=0.62,
            rate_func=smooth,
        )
        self.play(FadeOut(path), run_time=0.14)
        self.play(accent.animate.move_to(RIGHT * 2.9 + DOWN * 0.02).set_fill(PRIMARY_RED, opacity=1), run_time=0.16)
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
