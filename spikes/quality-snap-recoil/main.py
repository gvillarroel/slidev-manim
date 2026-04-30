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
    Ellipse,
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
    parser = argparse.ArgumentParser(description="Render the quality-snap-recoil spike.")
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
        "QualitySnapRecoilScene",
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


def slab(color: str, width: float, height: float) -> Rectangle:
    return Rectangle(width=width, height=height, stroke_width=0, fill_color=color, fill_opacity=1)


class QualitySnapRecoilScene(Scene):
    def construct(self) -> None:
        self.camera.background_color = WHITE

        frame = Rectangle(width=12.4, height=5.35, stroke_color=GRAY_200, stroke_width=2, fill_color=WHITE, fill_opacity=0)
        source_zone = Rectangle(width=4.0, height=4.05, stroke_width=0, fill_color=GRAY_100, fill_opacity=0.24).move_to(LEFT * 3.05)
        target_zone = Rectangle(width=4.45, height=4.05, stroke_width=0, fill_color=GRAY_100, fill_opacity=0.3).move_to(RIGHT * 2.55)

        source = VGroup(
            slab(PRIMARY_GREEN, 2.58, 0.82).move_to(LEFT * 3.42 + UP * 0.74),
            slab(PRIMARY_BLUE, 1.72, 0.72).move_to(LEFT * 2.44 + DOWN * 0.1),
            slab(PRIMARY_PURPLE, 1.18, 0.56).move_to(LEFT * 1.98 + DOWN * 0.96),
        )

        final_green = Circle(radius=0.86, stroke_width=0, fill_color=PRIMARY_GREEN, fill_opacity=1).move_to(RIGHT * 2.2 + UP * 0.36)
        snap_green = Ellipse(width=2.22, height=1.12, stroke_width=0, fill_color=PRIMARY_GREEN, fill_opacity=1).move_to(RIGHT * 3.2 + UP * 0.36)
        final_blue = Circle(radius=0.48, stroke_width=0, fill_color=PRIMARY_BLUE, fill_opacity=1).move_to(RIGHT * 3.68 + DOWN * 0.4)
        blue_overshoot = Circle(radius=0.55, stroke_width=0, fill_color=PRIMARY_BLUE, fill_opacity=1).move_to(RIGHT * 3.92 + DOWN * 0.28)
        final_purple = Circle(radius=0.26, stroke_width=0, fill_color=PRIMARY_PURPLE, fill_opacity=1).move_to(RIGHT * 2.72 + DOWN * 1.16)
        purple_overshoot = Circle(radius=0.31, stroke_width=0, fill_color=PRIMARY_PURPLE, fill_opacity=1).move_to(RIGHT * 2.98 + DOWN * 1.32)

        slots = VGroup(
            Circle(radius=0.91, stroke_color=GRAY_200, stroke_width=4, fill_opacity=0).move_to(final_green),
            Circle(radius=0.52, stroke_color=GRAY_200, stroke_width=3, fill_opacity=0).move_to(final_blue),
            Circle(radius=0.3, stroke_color=GRAY_200, stroke_width=3, fill_opacity=0).move_to(final_purple),
        ).set_stroke(opacity=0.36)

        guide = Line(LEFT * 1.05 + UP * 0.36, RIGHT * 2.45 + UP * 0.36, color=PRIMARY_ORANGE, stroke_width=6).set_stroke(opacity=0.3)
        pressure_wall = Line(RIGHT * 4.75 + DOWN * 0.72, RIGHT * 4.75 + UP * 1.44, color=PRIMARY_RED, stroke_width=6).set_stroke(opacity=0.28)
        accent = Circle(radius=0.12, stroke_width=0, fill_color=PRIMARY_YELLOW, fill_opacity=1).move_to(guide.get_start())

        self.add(frame, source_zone, target_zone, slots, guide, pressure_wall, source, accent)
        self.wait(3.0)

        self.play(guide.animate.set_stroke(opacity=1), pressure_wall.animate.set_stroke(opacity=0.7), run_time=1.0)
        self.play(MoveAlongPath(accent, guide), run_time=2.35, rate_func=smooth)
        self.play(accent.animate.move_to(pressure_wall.get_center()).set_fill(PRIMARY_RED, opacity=1), run_time=0.55)
        self.play(Transform(source[0], snap_green.copy()), run_time=1.3, rate_func=smooth)
        self.wait(1.35)
        self.play(Transform(source[0], final_green.copy()), accent.animate.move_to(final_green.get_center()), run_time=1.15, rate_func=smooth)
        self.wait(0.8)
        self.play(FadeOut(slots), run_time=0.55)
        self.play(
            AnimationGroup(
                Transform(source[1], blue_overshoot.copy()),
                Transform(source[2], purple_overshoot.copy()),
                lag_ratio=0.22,
            ),
            run_time=2.1,
            rate_func=smooth,
        )
        self.play(
            AnimationGroup(
                Transform(source[1], final_blue.copy()),
                Transform(source[2], final_purple.copy()),
                lag_ratio=0.16,
            ),
            run_time=1.35,
            rate_func=smooth,
        )
        self.wait(0.7)
        self.play(
            FadeOut(source_zone),
            FadeOut(guide),
            FadeOut(pressure_wall),
            FadeOut(accent),
            run_time=1.25,
        )
        self.play(VGroup(target_zone, source).animate.shift(LEFT * 1.1), run_time=1.35, rate_func=smooth)
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
