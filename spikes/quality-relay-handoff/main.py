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
PRIMARY_YELLOW = "#f1c319"
PRIMARY_GREEN = "#45842a"
PRIMARY_BLUE = "#007298"
PRIMARY_PURPLE = "#652f6c"
GRAY_100 = "#e7e7e7"
GRAY_200 = "#cfcfcf"
GRAY_300 = "#a9a9a9"


class _Args(argparse.Namespace):
    quality: str


def parse_args() -> _Args:
    parser = argparse.ArgumentParser(description="Render the quality-relay-handoff spike.")
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
        "QualityRelayHandoffScene",
    ]
    if poster:
        command.insert(-2, "-s")
    return command


def promote(target_name: str, destination: Path) -> None:
    matches = sorted(STAGING_DIR.glob(f"**/{target_name}"), key=lambda path: path.stat().st_mtime)
    if not matches:
        raise FileNotFoundError(target_name)
    destination.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(matches[-1], destination)


def slab(color: str, width: float, height: float) -> Rectangle:
    return Rectangle(width=width, height=height, stroke_width=0, fill_color=color, fill_opacity=1)


def slot(color: str, width: float, height: float, opacity: float = 0.16) -> VGroup:
    corner = 0.26
    half_w = width / 2
    half_h = height / 2
    segments = VGroup(
        Line(LEFT * half_w + UP * half_h, LEFT * (half_w - corner) + UP * half_h),
        Line(LEFT * half_w + UP * half_h, LEFT * half_w + UP * (half_h - corner)),
        Line(RIGHT * half_w + UP * half_h, RIGHT * (half_w - corner) + UP * half_h),
        Line(RIGHT * half_w + UP * half_h, RIGHT * half_w + UP * (half_h - corner)),
        Line(LEFT * half_w + DOWN * half_h, LEFT * (half_w - corner) + DOWN * half_h),
        Line(LEFT * half_w + DOWN * half_h, LEFT * half_w + DOWN * (half_h - corner)),
        Line(RIGHT * half_w + DOWN * half_h, RIGHT * (half_w - corner) + DOWN * half_h),
        Line(RIGHT * half_w + DOWN * half_h, RIGHT * half_w + DOWN * (half_h - corner)),
    )
    segments.set_color(color).set_stroke(width=3, opacity=opacity)
    return segments


class QualityRelayHandoffScene(Scene):
    def construct(self) -> None:
        self.camera.background_color = WHITE

        frame = Rectangle(width=12.3, height=5.85, stroke_color=GRAY_200, stroke_width=2, fill_color=WHITE, fill_opacity=0)
        source_zone = Rectangle(width=3.7, height=3.45, stroke_width=0, fill_color=GRAY_100, fill_opacity=0.22).move_to(LEFT * 3.28)
        target_zone = Rectangle(width=4.45, height=3.7, stroke_width=0, fill_color=GRAY_100, fill_opacity=0.24).move_to(RIGHT * 2.58)

        green = slab(PRIMARY_GREEN, 2.28, 0.72).move_to(LEFT * 3.52 + UP * 0.72)
        blue = slab(PRIMARY_BLUE, 1.46, 0.56).move_to(LEFT * 3.34 + DOWN * 0.18)
        purple = slab(PRIMARY_PURPLE, 1.04, 0.44).move_to(LEFT * 2.78 + DOWN * 1.02)
        source = VGroup(green, blue, purple)

        blue_relay = slab(PRIMARY_BLUE, 1.46, 0.56).move_to(LEFT * 1.08 + DOWN * 0.18)
        purple_relay = slab(PRIMARY_PURPLE, 1.04, 0.44).move_to(RIGHT * 1.16 + UP * 0.78)
        green_hold = slab(PRIMARY_GREEN, 1.66, 0.58).move_to(RIGHT * 2.02 + DOWN * 0.62)

        blue_pad = slot(PRIMARY_BLUE, 2.12, 1.08).move_to(blue_relay)
        purple_pad = slot(PRIMARY_PURPLE, 1.78, 0.98).move_to(purple_relay)
        green_pad = slot(PRIMARY_GREEN, 2.28, 1.04).move_to(green_hold)
        pads = VGroup(blue_pad, purple_pad, green_pad)

        guide_one = Line(blue.get_right() + RIGHT * 0.12, blue_pad.get_left() + LEFT * 0.12, color=GRAY_300, stroke_width=3).set_opacity(0.28)
        guide_two = Line(blue_pad.get_right() + RIGHT * 0.16, purple_pad.get_left() + LEFT * 0.16, color=GRAY_300, stroke_width=3).set_opacity(0.24)
        green_route_gate_top = purple_pad.get_bottom() + LEFT * 0.52 + DOWN * 0.16
        green_route_gate_bottom = green_route_gate_top + DOWN * 0.76
        guide_three = Line(green_route_gate_top, green_route_gate_bottom, color=GRAY_300, stroke_width=3).set_opacity(0.2)
        guides = VGroup(guide_one, guide_two, guide_three)

        relay_one = Line(blue.get_right() + RIGHT * 0.12, blue_pad.get_left() + LEFT * 0.12, color=PRIMARY_ORANGE, stroke_width=7)
        relay_two = Line(blue_pad.get_right() + RIGHT * 0.16, purple_pad.get_left() + LEFT * 0.16, color=PRIMARY_ORANGE, stroke_width=7)
        relay_three = Line(green_route_gate_top, green_route_gate_bottom, color=PRIMARY_ORANGE, stroke_width=7)
        relay = VGroup(relay_one, relay_two, relay_three)
        accent = Circle(radius=0.13, stroke_width=0, fill_color=PRIMARY_RED, fill_opacity=1).move_to(relay_one.get_start())
        accent.set_z_index(5)

        final_zone = Rectangle(width=3.95, height=3.05, stroke_width=0, fill_color=GRAY_100, fill_opacity=0.24).move_to(RIGHT * 0.18)
        final_green = Circle(radius=0.88, stroke_width=0, fill_color=PRIMARY_GREEN, fill_opacity=1).move_to(LEFT * 0.42 + UP * 0.43)
        final_blue = Circle(radius=0.48, stroke_width=0, fill_color=PRIMARY_BLUE, fill_opacity=1).move_to(RIGHT * 1.2 + UP * 0.05)
        final_purple = Circle(radius=0.29, stroke_width=0, fill_color=PRIMARY_PURPLE, fill_opacity=1).move_to(RIGHT * 0.25 + DOWN * 0.98)
        final_halo = Circle(radius=1.02, stroke_color=PRIMARY_RED, stroke_width=4, fill_opacity=0).move_to(final_green).set_stroke(opacity=0.66)
        terminal_pulse = Circle(radius=0.11, stroke_width=0, fill_color=PRIMARY_YELLOW, fill_opacity=1).move_to(
            final_halo.point_at_angle(0.78)
        )

        self.add(frame, source_zone, target_zone, pads, guides, source)
        self.wait(2.5)

        self.play(FadeIn(accent), Create(relay_one), run_time=0.9)
        self.play(
            AnimationGroup(
                Transform(blue, blue_relay.copy()),
                accent.animate.move_to(blue_pad.get_center()),
                lag_ratio=0.05,
            ),
            run_time=1.35,
            rate_func=smooth,
        )
        self.wait(1.45)

        self.play(Create(relay_two), run_time=0.7)
        self.play(
            AnimationGroup(
                Transform(purple, purple_relay.copy()),
                accent.animate.move_to(purple_pad.get_center()),
                lag_ratio=0.08,
            ),
            run_time=1.4,
            rate_func=smooth,
        )
        self.wait(1.55)

        self.play(FadeOut(relay_one), blue_pad.animate.set_stroke(opacity=0.08), run_time=0.7)
        self.play(Create(relay_three), run_time=0.75)
        self.play(
            AnimationGroup(
                Transform(green, green_hold.copy()),
                accent.animate.move_to(green_pad.get_center()),
                lag_ratio=0.1,
            ),
            run_time=1.8,
            rate_func=smooth,
        )
        self.wait(1.65)

        self.play(
            FadeOut(relay_two),
            FadeOut(relay_three),
            FadeOut(guides),
            FadeOut(pads),
            FadeOut(source_zone),
            FadeOut(frame),
            FadeOut(accent),
            run_time=1.0,
        )
        self.play(
            AnimationGroup(
                Transform(green, final_green.copy()),
                Transform(blue, final_blue.copy()),
                Transform(purple, final_purple.copy()),
                Transform(target_zone, final_zone.copy()),
                lag_ratio=0.08,
            ),
            run_time=2.0,
            rate_func=smooth,
        )
        self.play(FadeIn(final_halo), FadeIn(terminal_pulse), run_time=0.9, rate_func=smooth)
        self.play(FadeOut(terminal_pulse), final_halo.animate.set_stroke(opacity=0.28), run_time=0.8)
        self.wait(6.1)


def render_variant(args: _Args) -> None:
    video_path, poster_path = output_paths()
    if STAGING_DIR.exists():
        shutil.rmtree(STAGING_DIR)
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
