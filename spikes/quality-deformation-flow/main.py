#!/usr/bin/env -S uv run --script
# /// script
# dependencies = [
#   "manim>=0.20.0",
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
    ORIGIN,
    RIGHT,
    UP,
    AnimationGroup,
    Circle,
    FadeIn,
    FadeOut,
    GrowFromCenter,
    Line,
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
GRAY_200 = "#cfcfcf"
GRAY_700 = "#4f4f4f"


class _Args(argparse.Namespace):
    quality: str


def parse_args() -> _Args:
    parser = argparse.ArgumentParser(description="Render the quality-deformation-flow spike.")
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
        "QualityDeformationFlowScene",
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


def capsule(color: str, width: float = 2.1, height: float = 0.96) -> VGroup:
    shadow = RoundedRectangle(
        width=width,
        height=height,
        corner_radius=0.26,
        stroke_width=0,
        fill_color=GRAY_200,
        fill_opacity=0.42,
    ).shift(DOWN * 0.08 + RIGHT * 0.08)
    body = RoundedRectangle(
        width=width,
        height=height,
        corner_radius=0.26,
        stroke_width=0,
        fill_color=color,
        fill_opacity=1,
    )
    return VGroup(shadow, body)


def node(color: str, radius: float = 0.58) -> VGroup:
    shadow = Circle(radius=radius, stroke_width=0, fill_color=GRAY_200, fill_opacity=0.4).shift(DOWN * 0.08 + RIGHT * 0.08)
    body = Circle(radius=radius, stroke_width=0, fill_color=color, fill_opacity=1)
    return VGroup(shadow, body)


class QualityDeformationFlowScene(Scene):
    def construct(self) -> None:
        self.camera.background_color = WHITE

        guide = RoundedRectangle(
            width=13.2,
            height=5.4,
            corner_radius=0.32,
            stroke_color=GRAY_200,
            stroke_width=2,
            fill_color=WHITE,
            fill_opacity=0,
        )

        start_positions = [LEFT * 4.6 + DOWN * 0.2, LEFT * 2.2 + DOWN * 0.2, ORIGIN + DOWN * 0.2]
        end_positions = [RIGHT * 2.85 + UP * 1.2, RIGHT * 2.85 + DOWN * 0.05, RIGHT * 2.85 + DOWN * 1.3]
        colors = [PRIMARY_GREEN, PRIMARY_BLUE, PRIMARY_PURPLE]

        source_capsules = VGroup(*[capsule(color).move_to(pos) for color, pos in zip(colors, start_positions, strict=True)])
        target_nodes = VGroup(*[node(color).move_to(pos) for color, pos in zip(colors, end_positions, strict=True)])

        source_links = VGroup(
            Line(source_capsules[0].get_right(), source_capsules[1].get_left(), color=PRIMARY_ORANGE, stroke_width=7),
            Line(source_capsules[1].get_right(), source_capsules[2].get_left(), color=PRIMARY_ORANGE, stroke_width=7),
        )

        target_links = VGroup(
            Line(target_nodes[0].get_bottom(), target_nodes[1].get_top(), color=PRIMARY_ORANGE, stroke_width=6),
            Line(target_nodes[1].get_bottom(), target_nodes[2].get_top(), color=PRIMARY_ORANGE, stroke_width=6),
        )

        pulse = Circle(radius=0.12, stroke_width=0, fill_color=PRIMARY_YELLOW, fill_opacity=1)
        pulse.move_to(source_capsules[0].get_left() + RIGHT * 0.3)
        flow_path = Line(source_capsules[0].get_left() + RIGHT * 0.25, source_capsules[2].get_right() + RIGHT * 0.65)

        self.add(guide)
        self.play(
            FadeIn(source_capsules, shift=UP * 0.18, lag_ratio=0.06),
            FadeIn(source_links, lag_ratio=0.1),
            run_time=0.9,
        )
        self.play(GrowFromCenter(pulse), run_time=0.35)
        self.play(MoveAlongPath(pulse, flow_path), run_time=0.8, rate_func=linear)

        transforms = [Transform(source_capsules[index], target_nodes[index]) for index in range(3)]
        self.play(
            AnimationGroup(
                *[source_links[i].animate.set_opacity(0.0) for i in range(2)],
                *transforms,
                lag_ratio=0.08,
            ),
            run_time=2.0,
            rate_func=smooth,
        )
        self.play(FadeIn(target_links, lag_ratio=0.12), run_time=0.35)
        self.play(pulse.animate.move_to(end_positions[0] + UP * 0.92).set_fill(PRIMARY_RED, opacity=1), run_time=0.22)

        for target in target_nodes:
            self.play(target.animate.scale(1.06), run_time=0.18, rate_func=there_and_back)

        self.wait(0.35)
        self.play(FadeOut(pulse), run_time=0.2)
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
