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
    LaggedStart,
    Line,
    MoveAlongPath,
    RoundedRectangle,
    Scene,
    VGroup,
    WHITE,
    linear,
    smooth,
    there_and_back_with_pause,
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
GRAY_600 = "#696969"


class _Args(argparse.Namespace):
    quality: str


def parse_args() -> _Args:
    parser = argparse.ArgumentParser(description="Render the quality-pulse-routing spike.")
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
        "QualityPulseRoutingScene",
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


def station(color: str, scale: float = 1.0) -> VGroup:
    shadow = Circle(radius=0.56 * scale, stroke_width=0, fill_color=GRAY_200, fill_opacity=0.38).shift(RIGHT * 0.08 + DOWN * 0.08)
    body = Circle(radius=0.56 * scale, stroke_width=0, fill_color=color, fill_opacity=1)
    ring = Circle(radius=0.72 * scale, stroke_color=color, stroke_width=6, fill_opacity=0)
    return VGroup(shadow, body, ring)


class QualityPulseRoutingScene(Scene):
    def construct(self) -> None:
        self.camera.background_color = WHITE

        panel = RoundedRectangle(
            width=12.6,
            height=5.8,
            corner_radius=0.35,
            stroke_color=GRAY_200,
            stroke_width=2,
            fill_color=GRAY_100,
            fill_opacity=0.15,
        )
        panel.shift(DOWN * 0.1)

        positions = [
            LEFT * 4.25 + UP * 1.2,
            LEFT * 1.25 + DOWN * 0.15,
            RIGHT * 2.0 + UP * 1.0,
            RIGHT * 4.45 + DOWN * 1.3,
        ]
        colors = [PRIMARY_GREEN, PRIMARY_BLUE, PRIMARY_PURPLE, PRIMARY_RED]
        stations = VGroup(*[station(color).move_to(pos) for color, pos in zip(colors, positions, strict=True)])

        path = VGroup(
            Line(positions[0], positions[1], color=GRAY_600, stroke_width=7),
            Line(positions[1], positions[2], color=GRAY_600, stroke_width=7),
            Line(positions[2], positions[3], color=GRAY_600, stroke_width=7),
        )
        active_path = VGroup(
            Line(positions[0], positions[1], color=PRIMARY_ORANGE, stroke_width=7),
            Line(positions[1], positions[2], color=PRIMARY_ORANGE, stroke_width=7),
            Line(positions[2], positions[3], color=PRIMARY_ORANGE, stroke_width=7),
        ).set_opacity(0)

        pulse = Circle(radius=0.16, stroke_width=0, fill_color=PRIMARY_YELLOW, fill_opacity=1).move_to(positions[0])

        self.add(panel)
        self.play(
            LaggedStart(*[FadeIn(station_group, shift=UP * 0.16) for station_group in stations], lag_ratio=0.12),
            FadeIn(path),
            run_time=1.0,
        )
        self.play(FadeIn(pulse), run_time=0.2)

        for index, segment in enumerate(active_path):
            self.play(FadeIn(segment), run_time=0.18)
            self.play(MoveAlongPath(pulse, segment), run_time=0.6, rate_func=linear)
            self.play(
                stations[index + 1].animate.scale(1.08).set_opacity(1.0),
                stations[max(index, 0)].animate.set_opacity(0.84),
                run_time=0.28,
                rate_func=there_and_back_with_pause,
            )

        halo = Circle(radius=0.32, stroke_width=10, stroke_color=PRIMARY_YELLOW, fill_opacity=0).move_to(positions[-1])
        self.play(
            AnimationGroup(
                FadeIn(halo),
                stations[-1].animate.scale(1.14),
                lag_ratio=0.0,
            ),
            run_time=0.35,
        )
        self.play(halo.animate.scale(1.8).set_stroke(opacity=0), run_time=0.45, rate_func=smooth)
        self.play(FadeOut(pulse), FadeOut(halo), run_time=0.2)
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
