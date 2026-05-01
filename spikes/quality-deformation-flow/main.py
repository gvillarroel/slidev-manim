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
    PI,
    RIGHT,
    UP,
    Circle,
    Create,
    FadeIn,
    FadeOut,
    Line,
    Rectangle,
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
GRAY_200 = "#cfcfcf"
GRAY_300 = "#b7b7b7"
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


def node(color: str, radius: float = 0.54) -> VGroup:
    shadow = Circle(radius=radius, stroke_width=0, fill_color=GRAY_200, fill_opacity=0.4).shift(DOWN * 0.08 + RIGHT * 0.08)
    body = Circle(radius=radius, stroke_width=0, fill_color=color, fill_opacity=1)
    return VGroup(shadow, body)


def slot(radius: float = 0.72) -> VGroup:
    mark_style = {
        "color": GRAY_300,
        "stroke_width": 2,
        "stroke_opacity": 0.68,
    }
    vertical = 0.46
    gap = 0.22
    return VGroup(
        Line(LEFT * radius + UP * vertical, LEFT * radius + UP * gap, **mark_style),
        Line(LEFT * radius + DOWN * gap, LEFT * radius + DOWN * vertical, **mark_style),
        Line(RIGHT * radius + UP * vertical, RIGHT * radius + UP * gap, **mark_style),
        Line(RIGHT * radius + DOWN * gap, RIGHT * radius + DOWN * vertical, **mark_style),
    )


class QualityDeformationFlowScene(Scene):
    def construct(self) -> None:
        self.camera.background_color = WHITE

        layout_shift = RIGHT * 1.35
        start_positions = [
            LEFT * 4.9 + DOWN * 0.05 + layout_shift,
            LEFT * 2.55 + DOWN * 0.05 + layout_shift,
            LEFT * 0.2 + DOWN * 0.05 + layout_shift,
        ]
        end_positions = [RIGHT * 2.25 + UP * 1.75 + layout_shift, RIGHT * 2.25 + layout_shift, RIGHT * 2.25 + DOWN * 1.75 + layout_shift]
        throat_center = RIGHT * 0.9 + layout_shift
        throat_positions = [throat_center + UP * 0.78, throat_center, throat_center + DOWN * 0.78]
        colors = [PRIMARY_GREEN, PRIMARY_BLUE, PRIMARY_PURPLE]

        source_capsules = VGroup(*[capsule(color).move_to(pos) for color, pos in zip(colors, start_positions, strict=True)])
        target_nodes = VGroup(*[node(color).move_to(pos) for color, pos in zip(colors, end_positions, strict=True)])
        target_slots = VGroup(*[slot().move_to(pos) for pos in end_positions])

        source_links = VGroup(
            Line(source_capsules[0].get_right(), source_capsules[1].get_left(), color=PRIMARY_ORANGE, stroke_width=7),
            Line(source_capsules[1].get_right(), source_capsules[2].get_left(), color=PRIMARY_ORANGE, stroke_width=7),
        )

        link_clearance = 0.28
        link_offset = 0.54 + link_clearance
        target_links = VGroup(
            Line(end_positions[0] + DOWN * link_offset, end_positions[1] + UP * link_offset, color=PRIMARY_ORANGE, stroke_width=6),
            Line(end_positions[1] + DOWN * link_offset, end_positions[2] + UP * link_offset, color=PRIMARY_ORANGE, stroke_width=6),
        )
        target_links.set_z_index(1)
        target_nodes.set_z_index(3)
        target_slots.set_z_index(0)

        source_links.set_z_index(1)
        source_capsules.set_z_index(3)

        source_rail = Line(LEFT * 5.95 + DOWN * 0.98 + layout_shift, LEFT * 0.95 + DOWN * 0.98 + layout_shift, color=GRAY_200, stroke_width=3)
        route_in = Line(source_capsules[2].get_right() + RIGHT * 0.18, throat_center + LEFT * 0.36, color=GRAY_200, stroke_width=3)
        route_out = Line(throat_center + RIGHT * 0.36, end_positions[1] + LEFT * 0.78, color=GRAY_200, stroke_width=3)
        routes = VGroup(source_rail, route_in, route_out)
        routes.set_opacity(0.74)

        throat_left = Rectangle(
            width=0.12,
            height=2.95,
            stroke_width=0,
            fill_color=PRIMARY_RED,
            fill_opacity=0.82,
        ).move_to(throat_center + LEFT * 0.28)
        throat_right = throat_left.copy().move_to(throat_center + RIGHT * 0.28)
        throat_fill = Rectangle(
            width=0.34,
            height=2.66,
            stroke_width=0,
            fill_color=PRIMARY_RED,
            fill_opacity=0.08,
        ).move_to(throat_center)
        throat = VGroup(throat_fill, throat_left, throat_right)
        throat.set_z_index(2)

        self.add(routes, target_slots, throat, source_links, source_capsules)
        self.wait(2.6)

        for index, source in enumerate(source_capsules):
            if index < len(source_links):
                self.play(source_links[index].animate.set_color(PRIMARY_RED).set_stroke(width=9), run_time=0.45)

            self.play(
                target_slots[index].animate.set_stroke(PRIMARY_RED, width=4, opacity=0.92),
                throat_fill.animate.set_fill(PRIMARY_RED, opacity=0.2),
                run_time=0.45,
            )
            self.play(
                source.animate.move_to(throat_positions[index]).stretch(0.34, dim=0).stretch(1.18, dim=1),
                run_time=1.25,
                rate_func=smooth,
            )
            self.wait(0.55)
            self.play(
                Transform(source, target_nodes[index], path_arc=-PI / 3),
                FadeOut(target_slots[index]),
                throat_fill.animate.set_fill(PRIMARY_RED, opacity=0.08),
                run_time=1.55,
                rate_func=smooth,
            )

            if index == 0:
                self.wait(0.25)
            else:
                self.play(Create(target_links[index - 1]), run_time=0.45)

            if index < len(source_links):
                self.play(FadeOut(source_links[index]), run_time=0.35)

        resolved_stack = VGroup(source_capsules, target_links)
        self.wait(0.7)
        self.play(
            FadeOut(routes),
            FadeOut(throat),
            resolved_stack.animate.move_to(ORIGIN),
            run_time=1.6,
            rate_func=smooth,
        )
        self.wait(6.2)


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
