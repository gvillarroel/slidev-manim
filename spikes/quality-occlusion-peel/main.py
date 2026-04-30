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
    parser = argparse.ArgumentParser(description="Render the quality-occlusion-peel spike.")
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
        "QualityOcclusionPeelScene",
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
    return RoundedRectangle(
        width=width,
        height=height,
        corner_radius=0.32,
        stroke_width=0,
        fill_color=color,
        fill_opacity=opacity,
    )


class QualityOcclusionPeelScene(Scene):
    def construct(self) -> None:
        self.camera.background_color = WHITE

        frame = RoundedRectangle(width=12.9, height=5.8, corner_radius=0.34, stroke_color=GRAY_200, stroke_width=2, fill_color=WHITE, fill_opacity=0)
        source_zone = RoundedRectangle(width=4.0, height=4.2, corner_radius=0.35, stroke_width=0, fill_color=GRAY_100, fill_opacity=0.24).move_to(LEFT * 2.85)
        target_zone = RoundedRectangle(width=4.1, height=4.3, corner_radius=0.35, stroke_width=0, fill_color=GRAY_100, fill_opacity=0.3).move_to(RIGHT * 3.0 + DOWN * 0.05)

        back_band = slab(PRIMARY_BLUE, 3.5, 0.88).move_to(LEFT * 2.75 + UP * 0.2)
        front_band = slab(PRIMARY_GREEN, 4.0, 1.04).move_to(LEFT * 2.42 + UP * 0.08)
        support_chip = slab(PRIMARY_PURPLE, 1.62, 0.78).move_to(LEFT * 1.55 + DOWN * 1.12)
        source = VGroup(back_band, front_band, support_chip)

        guide = Line(LEFT * 1.2 + DOWN * 0.04, RIGHT * 1.1 + DOWN * 0.04, color=PRIMARY_ORANGE, stroke_width=6)
        accent = Circle(radius=0.12, stroke_width=0, fill_color=PRIMARY_YELLOW, fill_opacity=1).move_to(guide.get_start())

        final_main = Circle(radius=0.86, stroke_width=0, fill_color=PRIMARY_GREEN, fill_opacity=1).move_to(RIGHT * 2.72 + UP * 0.32)
        final_support = Circle(radius=0.58, stroke_width=0, fill_color=PRIMARY_BLUE, fill_opacity=1).move_to(RIGHT * 3.82 + DOWN * 0.06)
        final_accent = Circle(radius=0.28, stroke_width=0, fill_color=PRIMARY_PURPLE, fill_opacity=1).move_to(RIGHT * 3.08 + DOWN * 1.08)

        peel_main = slab(PRIMARY_GREEN, 3.2, 0.9).move_to(RIGHT * 0.78 + UP * 1.02)
        peel_back = slab(PRIMARY_BLUE, 2.55, 0.78).move_to(RIGHT * 0.75 + DOWN * 0.04)
        peel_support = slab(PRIMARY_PURPLE, 1.18, 0.62).move_to(RIGHT * 1.58 + DOWN * 0.96)

        self.add(frame, source_zone, target_zone)
        self.play(FadeIn(source, lag_ratio=0.08), run_time=0.7)
        self.play(FadeIn(guide), run_time=0.14)
        self.play(MoveAlongPath(accent, guide), run_time=0.34)
        self.play(
            AnimationGroup(
                front_band.animate.move_to(peel_main.get_center()),
                back_band.animate.move_to(peel_back.get_center()),
                support_chip.animate.move_to(peel_support.get_center()),
                lag_ratio=0.06,
            ),
            run_time=0.62,
            rate_func=smooth,
        )
        self.play(front_band.animate.scale(0.95), run_time=0.16, rate_func=there_and_back)
        self.play(FadeOut(guide), run_time=0.12)
        self.play(
            AnimationGroup(
                Transform(front_band, final_main.copy()),
                Transform(back_band, final_support.copy()),
                Transform(support_chip, final_accent.copy()),
                lag_ratio=0.08,
            ),
            run_time=0.86,
            rate_func=smooth,
        )
        self.play(accent.animate.move_to(RIGHT * 2.86 + DOWN * 0.06).set_fill(PRIMARY_RED, opacity=1), run_time=0.16)
        for item in source:
            self.play(item.animate.scale(1.06), run_time=0.12, rate_func=there_and_back)
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
