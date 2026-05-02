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
GRAY_300 = "#b5b5b5"
GRAY_500 = "#828282"
GRAY_700 = "#555555"


class _Args(argparse.Namespace):
    quality: str


def parse_args() -> _Args:
    parser = argparse.ArgumentParser(description="Render the quality-throat-gate spike.")
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
        "QualityThroatGateScene",
    ]
    if poster:
        command.insert(-2, "-s")
    return command


def promote(target_name: str, destination: Path) -> None:
    matches = sorted(STAGING_DIR.glob(f"**/{target_name}"))
    if not matches:
        raise FileNotFoundError(target_name)
    destination.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(max(matches, key=lambda path: path.stat().st_mtime), destination)


def slab(color: str, width: float, height: float) -> Rectangle:
    return Rectangle(width=width, height=height, stroke_width=0, fill_color=color, fill_opacity=1)


def panel(width: float, height: float, opacity: float = 0.2) -> Rectangle:
    return Rectangle(width=width, height=height, stroke_width=0, fill_color=GRAY_100, fill_opacity=opacity)


def slot(width: float, height: float, color: str = GRAY_300) -> Rectangle:
    return Rectangle(width=width, height=height, stroke_color=color, stroke_width=2, fill_opacity=0)


def route(start: tuple[float, float, float], end: tuple[float, float, float]) -> Line:
    return Line(start, end, stroke_color=GRAY_300, stroke_width=2, stroke_opacity=0.45)


class QualityThroatGateScene(Scene):
    def construct(self) -> None:
        self.camera.background_color = WHITE

        frame = Rectangle(width=12.35, height=5.75, stroke_color=GRAY_200, stroke_width=2, fill_opacity=0)
        source_zone = panel(3.4, 3.55, 0.18).move_to(LEFT * 3.52)
        target_zone = panel(3.65, 3.55, 0.2).move_to(RIGHT * 3.16)

        lead = slab(PRIMARY_RED, 2.32, 0.72).move_to(LEFT * 3.82 + UP * 0.76)
        support_a = slab(GRAY_500, 1.62, 0.52).move_to(LEFT * 3.0 + DOWN * 0.05)
        support_b = slab(GRAY_700, 1.0, 0.42).move_to(LEFT * 2.64 + DOWN * 0.78)
        source = VGroup(lead, support_a, support_b)

        lead_slot = slot(1.72, 1.48, PRIMARY_RED).move_to(RIGHT * 3.02 + UP * 0.35).set_stroke(opacity=0.2)
        support_slot_a = slot(1.04, 0.96).move_to(RIGHT * 4.22 + DOWN * 0.3).set_stroke(opacity=0.22)
        support_slot_b = slot(0.7, 0.64).move_to(RIGHT * 3.1 + DOWN * 1.08).set_stroke(opacity=0.22)
        target_slots = VGroup(lead_slot, support_slot_a, support_slot_b)

        gate_top = slab(GRAY_700, 2.35, 0.18).move_to(RIGHT * 0.82 + UP * 0.33)
        gate_bottom = slab(GRAY_700, 2.35, 0.18).move_to(RIGHT * 0.82 + DOWN * 0.33)
        throat_mark = Rectangle(width=0.16, height=0.52, stroke_color=PRIMARY_RED, stroke_width=3, fill_opacity=0).move_to(RIGHT * 0.82)
        gate = VGroup(gate_top, gate_bottom, throat_mark)

        ingress = route((-2.05, 0.76, 0), (-0.38, 0.08, 0))
        exit_guide = route((1.42, 0.0, 0), (2.25, 0.22, 0))
        support_route_a = route((-2.2, -0.05, 0), (1.68, -0.72, 0))
        support_route_b = route((-1.78, -0.78, 0), (2.08, 0.86, 0))
        guides = VGroup(ingress, exit_guide, support_route_a, support_route_b)

        lead_entrance = slab(PRIMARY_RED, 1.72, 0.52).move_to(LEFT * 0.7 + UP * 0.16)
        lead_squeezed = slab(PRIMARY_RED, 1.24, 0.18).move_to(RIGHT * 0.82)
        lead_released = Circle(radius=0.76, stroke_width=0, fill_color=PRIMARY_RED, fill_opacity=1).move_to(RIGHT * 3.02 + UP * 0.35)
        support_a_queue = slab(GRAY_500, 1.12, 0.34).move_to(RIGHT * 0.04 + DOWN * 0.86)
        support_b_queue = slab(GRAY_700, 0.74, 0.3).move_to(RIGHT * 1.68 + UP * 0.86)
        support_a_final = Circle(radius=0.42, stroke_width=0, fill_color=GRAY_500, fill_opacity=1).move_to(RIGHT * 4.22 + DOWN * 0.3)
        support_b_final = Circle(radius=0.26, stroke_width=0, fill_color=GRAY_700, fill_opacity=1).move_to(RIGHT * 3.1 + DOWN * 1.08)

        final_brackets = VGroup(
            Line((2.08, 1.34, 0), (2.45, 1.34, 0), stroke_color=PRIMARY_RED, stroke_width=3),
            Line((2.08, 1.34, 0), (2.08, 0.97, 0), stroke_color=PRIMARY_RED, stroke_width=3),
            Line((4.78, 0.45, 0), (4.78, 0.08, 0), stroke_color=PRIMARY_RED, stroke_width=3),
            Line((4.78, 0.08, 0), (4.41, 0.08, 0), stroke_color=PRIMARY_RED, stroke_width=3),
            Line((2.16, -1.48, 0), (2.53, -1.48, 0), stroke_color=PRIMARY_RED, stroke_width=3),
            Line((2.16, -1.48, 0), (2.16, -1.11, 0), stroke_color=PRIMARY_RED, stroke_width=3),
        ).set_opacity(0.82).shift(LEFT * 2.4)

        self.add(frame, source_zone, target_zone, target_slots, gate, guides, source)
        self.wait(2.6)
        self.play(Create(ingress), Transform(lead, lead_entrance), run_time=2.15, rate_func=smooth)
        self.wait(0.75)
        self.play(
            Transform(lead, lead_squeezed),
            gate_top.animate.shift(DOWN * 0.08),
            gate_bottom.animate.shift(UP * 0.08),
            throat_mark.animate.scale(0.72),
            run_time=2.35,
            rate_func=smooth,
        )
        self.wait(1.9)
        self.play(
            AnimationGroup(
                Transform(support_a, support_a_queue),
                Transform(support_b, support_b_queue),
                lag_ratio=0.25,
            ),
            run_time=2.3,
            rate_func=smooth,
        )
        self.wait(0.8)
        self.play(
            FadeOut(source_zone),
            FadeOut(ingress),
            FadeOut(throat_mark),
            gate_top.animate.shift(UP * 0.3).set_fill(GRAY_300, opacity=0.45),
            gate_bottom.animate.shift(DOWN * 0.3).set_fill(GRAY_300, opacity=0.45),
            Transform(lead, lead_released),
            FadeOut(lead_slot),
            run_time=2.55,
            rate_func=smooth,
        )
        self.play(
            AnimationGroup(
                Transform(support_a, support_a_final),
                FadeOut(support_slot_a),
                Transform(support_b, support_b_final),
                FadeOut(support_slot_b),
                lag_ratio=0.18,
            ),
            run_time=2.45,
            rate_func=smooth,
        )
        self.play(
            FadeOut(gate_top),
            FadeOut(gate_bottom),
            FadeOut(guides),
            FadeOut(target_zone),
            lead.animate.shift(LEFT * 2.4),
            support_a.animate.shift(LEFT * 2.4),
            support_b.animate.shift(LEFT * 2.4),
            AnimationGroup(FadeIn(final_brackets), lag_ratio=0.08),
            run_time=1.75,
            rate_func=smooth,
        )
        self.remove(frame)
        self.wait(6.2)


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
