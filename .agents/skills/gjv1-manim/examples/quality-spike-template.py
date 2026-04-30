#!/usr/bin/env -S uv run --script
# /// script
# dependencies = [
#   "manim>=0.19.0",
# ]
# ///

from __future__ import annotations

import argparse
import os
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
    RoundedRectangle,
    Scene,
    Transform,
    VGroup,
    smooth,
)

SPIKE_DIR = Path(__file__).resolve().parent
REPO_ROOT = SPIKE_DIR.parent.parent if SPIKE_DIR.parent.name == "spikes" else Path.cwd()
SPIKE_NAME = SPIKE_DIR.name if SPIKE_DIR.parent.name == "spikes" else "gjv1-quality-template"
OUTPUT_DIR = REPO_ROOT / "videos" / SPIKE_NAME
STAGING_DIR = OUTPUT_DIR / ".manim"
VIDEO_PATH = OUTPUT_DIR / f"{SPIKE_NAME}.webm"
POSTER_PATH = OUTPUT_DIR / f"{SPIKE_NAME}.png"

# Preferred color styles: references/preferred-color-styles.md in this skill.
PRIMARY_RED = "#9e1b32"
PRIMARY_ORANGE = "#e77204"
PRIMARY_YELLOW = "#f1c319"
PRIMARY_GREEN = "#45842a"
PRIMARY_BLUE = "#007298"
PRIMARY_PURPLE = "#652f6c"
GRAY_100 = "#e7e7e7"
GRAY_200 = "#cfcfcf"
PAGE_BACKGROUND = "#f7f7f7"


def quality_flag(quality: str) -> str:
    return {
        "low": "-ql",
        "medium": "-qm",
        "high": "-qh",
        "production": "-qp",
        "4k": "-qk",
    }[quality]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Render a GJV1 quality spike template.")
    parser.add_argument("--quality", choices=("low", "medium", "high", "production", "4k"), default="medium")
    return parser.parse_args()


def render_command(args: argparse.Namespace, poster: bool) -> list[str]:
    STAGING_DIR.mkdir(parents=True, exist_ok=True)
    target = POSTER_PATH if poster else VIDEO_PATH
    command = [
        sys.executable,
        "-m",
        "manim",
        "render",
        quality_flag(args.quality),
        "-r",
        "1600,900",
        "-o",
        target.stem,
        "--media_dir",
        str(STAGING_DIR),
    ]
    command.append("-s" if poster else "--format=webm")
    if not poster:
        command.append("-t")
    command.extend([str(Path(__file__).resolve()), "GJV1QualityTemplateScene"])
    return command


def promote(target_name: str, destination: Path) -> None:
    matches = sorted(STAGING_DIR.glob(f"**/{target_name}"))
    if not matches:
        raise FileNotFoundError(target_name)
    destination.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(matches[-1], destination)


def slab(color: str, width: float, height: float) -> RoundedRectangle:
    return RoundedRectangle(
        width=width,
        height=height,
        corner_radius=min(height * 0.28, 0.24),
        stroke_width=0,
        fill_color=color,
        fill_opacity=1,
    )


class GJV1QualityTemplateScene(Scene):
    def construct(self) -> None:
        self.camera.background_color = PAGE_BACKGROUND

        stage = RoundedRectangle(
            width=12.8,
            height=6.3,
            corner_radius=0.34,
            stroke_color=GRAY_200,
            stroke_width=2,
            fill_color=PAGE_BACKGROUND,
            fill_opacity=0.96,
        )
        source_zone = RoundedRectangle(
            width=4.0,
            height=4.1,
            corner_radius=0.35,
            stroke_width=0,
            fill_color=GRAY_100,
            fill_opacity=0.24,
        ).move_to(LEFT * 3.05)
        target_zone = source_zone.copy().move_to(RIGHT * 3.0).set_fill(GRAY_100, opacity=0.3)

        green = slab(PRIMARY_GREEN, 2.6, 0.86).move_to(LEFT * 3.35 + UP * 0.72)
        blue = slab(PRIMARY_BLUE, 1.86, 0.76).move_to(LEFT * 2.22 + DOWN * 0.04)
        purple = slab(PRIMARY_PURPLE, 1.38, 0.62).move_to(LEFT * 1.68 + DOWN * 0.92)
        source = VGroup(green, blue, purple)

        gate_top = Line(RIGHT * 1.15 + UP * 0.44, RIGHT * 2.65 + UP * 0.44, color=PRIMARY_ORANGE, stroke_width=7)
        gate_bottom = Line(RIGHT * 1.15 + DOWN * 0.44, RIGHT * 2.65 + DOWN * 0.44, color=PRIMARY_ORANGE, stroke_width=7)
        gate = VGroup(gate_top, gate_bottom)
        pulse = Circle(radius=0.12, stroke_width=0, fill_color=PRIMARY_YELLOW, fill_opacity=1).move_to(LEFT * 0.8)

        compressed = VGroup(
            slab(PRIMARY_GREEN, 1.78, 0.52).move_to(RIGHT * 1.9 + UP * 0.2),
            slab(PRIMARY_BLUE, 1.22, 0.46).move_to(RIGHT * 1.9 + DOWN * 0.14),
            slab(PRIMARY_PURPLE, 0.9, 0.36).move_to(RIGHT * 1.9 + DOWN * 0.47),
        )
        final = VGroup(
            Circle(radius=0.84, stroke_width=0, fill_color=PRIMARY_GREEN, fill_opacity=1).move_to(RIGHT * 2.65 + UP * 0.46),
            Circle(radius=0.5, stroke_width=0, fill_color=PRIMARY_BLUE, fill_opacity=1).move_to(RIGHT * 3.82 + DOWN * 0.02),
            Circle(radius=0.26, stroke_width=0, fill_color=PRIMARY_PURPLE, fill_opacity=1).move_to(RIGHT * 3.14 + DOWN * 0.96),
        )

        self.add(stage, source_zone, target_zone, source)
        self.wait(2.6)
        self.play(FadeIn(gate), FadeIn(pulse), run_time=0.8)
        self.play(
            AnimationGroup(
                Transform(green, compressed[0]),
                Transform(blue, compressed[1]),
                Transform(purple, compressed[2]),
                pulse.animate.move_to(RIGHT * 1.9),
                lag_ratio=0.08,
            ),
            run_time=4.0,
            rate_func=smooth,
        )
        self.wait(2.2)
        self.play(FadeOut(gate), run_time=0.7)
        self.play(
            AnimationGroup(
                Transform(green, final[0]),
                Transform(blue, final[1]),
                Transform(purple, final[2]),
                pulse.animate.move_to(RIGHT * 3.2).set_fill(PRIMARY_RED, opacity=1),
                lag_ratio=0.12,
            ),
            run_time=4.2,
            rate_func=smooth,
        )
        self.play(FadeOut(pulse), run_time=0.7)
        self.wait(7.0)


def main() -> int:
    args = parse_args()
    for poster in (False, True):
        env = {**os.environ, "SPIKE_RENDER_TARGET": "poster" if poster else "video"}
        result = subprocess.run(render_command(args, poster), check=False, env=env)
        if result.returncode != 0:
            return result.returncode
        promote((POSTER_PATH if poster else VIDEO_PATH).name, POSTER_PATH if poster else VIDEO_PATH)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
