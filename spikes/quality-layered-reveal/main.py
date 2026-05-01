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
    Create,
    FadeIn,
    FadeOut,
    Line,
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
PRIMARY_GREEN = "#45842a"
PRIMARY_BLUE = "#007298"
PRIMARY_PURPLE = "#652f6c"
GRAY_100 = "#e7e7e7"
GRAY_200 = "#cfcfcf"


class _Args(argparse.Namespace):
    quality: str


def parse_args() -> _Args:
    parser = argparse.ArgumentParser(description="Render the quality-layered-reveal spike.")
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
        "QualityLayeredRevealScene",
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


def card(color: str, width: float = 2.15, height: float = 1.18, opacity: float = 1.0) -> Rectangle:
    return Rectangle(
        width=width,
        height=height,
        stroke_width=0,
        fill_color=color,
        fill_opacity=opacity,
    )


def orb(color: str, radius: float) -> VGroup:
    fill = Circle(radius=radius, stroke_width=0, fill_color=color, fill_opacity=1)
    ring = Circle(radius=radius + 0.14, stroke_color=color, stroke_width=6, fill_opacity=0)
    return VGroup(fill, ring)


class QualityLayeredRevealScene(Scene):
    def construct(self) -> None:
        self.camera.background_color = WHITE

        back_strip = Rectangle(width=12.0, height=1.4, stroke_width=0, fill_color=GRAY_100, fill_opacity=0.5).shift(UP * 1.1)
        front_panel = Rectangle(
            width=12.4,
            height=4.9,
            stroke_color=GRAY_200,
            stroke_width=2,
            fill_color=WHITE,
            fill_opacity=0.92,
        ).shift(DOWN * 0.25)
        source_field = Rectangle(
            width=3.55,
            height=3.65,
            stroke_color=GRAY_100,
            stroke_width=2,
            fill_color=GRAY_100,
            fill_opacity=0.32,
        ).move_to(LEFT * 3.65 + DOWN * 0.25)
        reveal_gate = VGroup(
            Rectangle(width=0.16, height=3.85, stroke_width=0, fill_color=GRAY_200, fill_opacity=0.78),
            Rectangle(width=0.16, height=3.85, stroke_width=0, fill_color=GRAY_200, fill_opacity=0.78),
            Rectangle(width=0.22, height=3.1, stroke_width=0, fill_color=PRIMARY_RED, fill_opacity=0.12),
        )
        reveal_gate[0].move_to(LEFT * 0.18 + DOWN * 0.18)
        reveal_gate[1].move_to(RIGHT * 0.18 + DOWN * 0.18)
        reveal_gate[2].move_to(DOWN * 0.18)
        gate_slots = VGroup(
            Rectangle(width=0.62, height=0.62, stroke_color=PRIMARY_RED, stroke_width=2, fill_opacity=0).move_to(
                DOWN * -0.05 + UP * 1.0
            ),
            Rectangle(width=0.62, height=0.62, stroke_color=PRIMARY_RED, stroke_width=2, fill_opacity=0).move_to(
                DOWN * 0.05
            ),
            Rectangle(width=0.62, height=0.62, stroke_color=PRIMARY_RED, stroke_width=2, fill_opacity=0).move_to(
                DOWN * 1.2
            ),
        )
        gate_slots.set_stroke(opacity=0.32)

        left_stack = VGroup(
            card(PRIMARY_GREEN).move_to(LEFT * 3.95 + UP * 1.0),
            card(PRIMARY_BLUE).move_to(LEFT * 3.25 + DOWN * 0.1),
            card(PRIMARY_PURPLE).move_to(LEFT * 2.55 + DOWN * 1.2),
        )
        ghost_stack = left_stack.copy().set_fill(color=GRAY_200, opacity=0.16).set_z_index(-1).shift(RIGHT * 0.22 + DOWN * 0.16)

        right_cluster = VGroup(
            orb(PRIMARY_GREEN, 0.62).move_to(RIGHT * 3.0 + UP * 0.95),
            orb(PRIMARY_BLUE, 0.54).move_to(RIGHT * 4.0 + DOWN * 0.05),
            orb(PRIMARY_PURPLE, 0.46).move_to(RIGHT * 2.85 + DOWN * 1.0),
        )
        target_slots = VGroup(
            Circle(radius=0.82, stroke_color=GRAY_200, stroke_width=3, fill_opacity=0).move_to(right_cluster[0]),
            Circle(radius=0.72, stroke_color=GRAY_200, stroke_width=3, fill_opacity=0).move_to(right_cluster[1]),
            Circle(radius=0.62, stroke_color=GRAY_200, stroke_width=3, fill_opacity=0).move_to(right_cluster[2]),
        )
        target_slots.set_stroke(opacity=0.55)
        final_cluster = VGroup(
            orb(PRIMARY_GREEN, 0.72).move_to(RIGHT * 0.25 + UP * 0.78),
            orb(PRIMARY_BLUE, 0.56).move_to(RIGHT * 1.45 + DOWN * 0.16),
            orb(PRIMARY_PURPLE, 0.46).move_to(LEFT * 0.85 + DOWN * 0.82),
        )

        guide_lines = VGroup(
            Line(left_stack[0].get_right(), right_cluster[0].get_left(), color=PRIMARY_ORANGE, stroke_width=5),
            Line(left_stack[1].get_right(), right_cluster[1].get_left(), color=PRIMARY_ORANGE, stroke_width=5),
            Line(left_stack[2].get_right(), right_cluster[2].get_left(), color=PRIMARY_ORANGE, stroke_width=5),
        )
        guide_lines.set_opacity(0.22)
        left_stack.set_z_index(4)
        right_cluster.set_z_index(5)
        guide_lines.set_z_index(1)
        target_slots.set_z_index(2)
        reveal_gate.set_z_index(3)
        gate_slots.set_z_index(3)

        self.add(back_strip, front_panel, source_field, target_slots, ghost_stack, guide_lines, reveal_gate, gate_slots, left_stack)
        self.wait(2.5)

        for index, segment in enumerate(guide_lines):
            active_segment = segment.copy().set_opacity(1).set_z_index(6)
            active_aperture = Rectangle(
                width=0.68,
                height=0.68,
                stroke_width=0,
                fill_color=PRIMARY_RED,
                fill_opacity=0.2,
            ).move_to(gate_slots[index])
            active_aperture.set_z_index(3)
            compressed_layer = card(
                [PRIMARY_GREEN, PRIMARY_BLUE, PRIMARY_PURPLE][index],
                width=0.72,
                height=0.58,
            ).move_to(gate_slots[index])
            compressed_layer.set_z_index(6)
            self.play(
                Create(active_segment),
                FadeIn(active_aperture),
                Transform(left_stack[index], compressed_layer),
                run_time=1.35,
                rate_func=smooth,
            )
            self.wait(0.25)
            self.play(
                Transform(left_stack[index], right_cluster[index]),
                FadeOut(active_segment),
                FadeOut(active_aperture),
                run_time=1.45,
                rate_func=smooth,
            )
            self.wait(0.85)

        self.play(
            FadeOut(guide_lines),
            FadeOut(target_slots),
            FadeOut(reveal_gate),
            FadeOut(gate_slots),
            FadeOut(ghost_stack),
            FadeOut(source_field),
            FadeOut(back_strip),
            run_time=1.1,
        )
        self.play(
            AnimationGroup(
                Transform(left_stack[0], final_cluster[0]),
                Transform(left_stack[1], final_cluster[1]),
                Transform(left_stack[2], final_cluster[2]),
                lag_ratio=0.12,
            ),
            front_panel.animate.set_width(7.8).set_height(3.7).move_to(RIGHT * 0.25 + DOWN * 0.02),
            run_time=2.2,
            rate_func=smooth,
        )
        self.wait(8.0)


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
