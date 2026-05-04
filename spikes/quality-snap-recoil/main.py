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
    LEFT,
    RIGHT,
    UP,
    AnimationGroup,
    Circle,
    Ellipse,
    FadeOut,
    Rectangle,
    Scene,
    Transform,
    VGroup,
    WHITE,
    config,
    smooth,
)

config.transparent = True
config.background_opacity = 0.0

SPIKE_DIR = Path(__file__).resolve().parent
REPO_ROOT = SPIKE_DIR.parent.parent
SPIKE_NAME = SPIKE_DIR.name
OUTPUT_DIR = REPO_ROOT / "videos" / SPIKE_NAME
STAGING_DIR = OUTPUT_DIR / ".manim"

PRIMARY_RED = "#9e1b32"
GRAY_100 = "#e7e7e7"
GRAY_200 = "#cfcfcf"
GRAY_500 = "#828282"
GRAY_700 = "#333e48"


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
        "--transparent",
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
        config.background_opacity = 0.0
        self.camera.background_color = WHITE
        self.camera.background_opacity = 0.0

        source_zone = Rectangle(width=3.7, height=3.45, stroke_width=0, fill_color=GRAY_100, fill_opacity=0.24).move_to(LEFT * 3.05)
        target_zone = VGroup(
            slab(GRAY_100, 3.45, 0.045).move_to(RIGHT * 0.9 + UP * 1.65),
            slab(GRAY_100, 3.45, 0.045).move_to(RIGHT * 0.9 + UP * -1.45),
        ).set_fill(opacity=0.55)

        source = VGroup(
            slab(PRIMARY_RED, 2.42, 0.78).move_to(LEFT * 3.42 + UP * 0.72),
            slab(GRAY_500, 1.58, 0.56).move_to(LEFT * 2.7 + UP * -0.4),
            slab(GRAY_700, 1.02, 0.42).move_to(LEFT * 2.32 + UP * -1.12),
        )

        final_leader = Circle(radius=0.78, stroke_width=0, fill_color=PRIMARY_RED, fill_opacity=1).move_to(RIGHT * 0.45 + UP * 0.42)
        snap_leader = Ellipse(width=2.18, height=0.98, stroke_width=0, fill_color=PRIMARY_RED, fill_opacity=1).move_to(RIGHT * 1.4 + UP * 0.42)
        final_support = Circle(radius=0.45, stroke_width=0, fill_color=GRAY_500, fill_opacity=1).move_to(RIGHT * 1.6 + UP * -0.38)
        support_overshoot = Circle(radius=0.5, stroke_width=0, fill_color=GRAY_500, fill_opacity=1).move_to(RIGHT * 1.87 + UP * -0.3)
        final_echo = Circle(radius=0.24, stroke_width=0, fill_color=GRAY_700, fill_opacity=1).move_to(RIGHT * 0.63 + UP * -1.02)
        echo_overshoot = Circle(radius=0.28, stroke_width=0, fill_color=GRAY_700, fill_opacity=1).move_to(RIGHT * 0.89 + UP * -1.18)

        slots = VGroup(
            Circle(radius=0.84, stroke_color=GRAY_200, stroke_width=4, fill_opacity=0).move_to(final_leader),
            Circle(radius=0.5, stroke_color=GRAY_200, stroke_width=3, fill_opacity=0).move_to(final_support),
            Circle(radius=0.29, stroke_color=GRAY_200, stroke_width=3, fill_opacity=0).move_to(final_echo),
        ).set_stroke(opacity=0.36)

        guide = VGroup(
            slab(GRAY_200, 1.05, 0.045).move_to(LEFT * 0.7 + UP * 0.08),
            slab(GRAY_200, 0.8, 0.045).move_to(RIGHT * 0.8 + UP * 0.08),
        ).set_fill(opacity=0.46)
        pressure_wall = slab(PRIMARY_RED, 0.045, 1.72).move_to(RIGHT * 2.9 + UP * 0.4).set_fill(opacity=0.28)

        self.add(source_zone, target_zone, slots, guide, pressure_wall, source)
        self.wait(3.0)

        self.play(guide.animate.set_fill(opacity=0.7), pressure_wall.animate.set_fill(opacity=0.72), run_time=1.0)
        self.play(Transform(source[0], snap_leader.copy()), run_time=2.0, rate_func=smooth)
        self.wait(1.7)
        self.play(
            Transform(source[0], final_leader.copy()),
            pressure_wall.animate.set_fill(opacity=0.42),
            guide.animate.set_fill(opacity=0.24),
            run_time=1.3,
            rate_func=smooth,
        )
        self.wait(1.0)
        self.play(FadeOut(guide), FadeOut(pressure_wall), FadeOut(slots), run_time=0.9)
        self.play(
            AnimationGroup(
                Transform(source[1], support_overshoot.copy()),
                Transform(source[2], echo_overshoot.copy()),
                FadeOut(source_zone),
                lag_ratio=0.22,
            ),
            run_time=2.4,
            rate_func=smooth,
        )
        self.play(
            AnimationGroup(
                Transform(source[1], final_support.copy()),
                Transform(source[2], final_echo.copy()),
                lag_ratio=0.16,
            ),
            run_time=1.6,
            rate_func=smooth,
        )
        self.wait(1.2)
        self.play(
            FadeOut(target_zone),
            run_time=1.6,
            rate_func=smooth,
        )
        self.wait(8.2)


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
