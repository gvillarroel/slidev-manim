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
GRAY_100 = "#e7e7e7"
GRAY_200 = "#cfcfcf"
GRAY_300 = "#b5b5b5"


class _Args(argparse.Namespace):
    quality: str


def parse_args() -> _Args:
    parser = argparse.ArgumentParser(description="Render the quality-mask-transfer spike.")
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
        "--transparent",
        "--format",
        "webm",
        "-o",
        stem,
        "--media_dir",
        str(STAGING_DIR),
        str(Path(__file__).resolve()),
        "QualityMaskTransferScene",
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


def chip(color: str, width: float, height: float) -> Rectangle:
    return Rectangle(
        width=width,
        height=height,
        stroke_width=0,
        fill_color=color,
        fill_opacity=1,
    )


def corner_brackets(group: VGroup, padding: float = 0.42, leg: float = 0.48, gap: float = 0.08) -> VGroup:
    left = group.get_left()[0] - padding
    right = group.get_right()[0] + padding
    top = group.get_top()[1] + padding
    bottom = group.get_bottom()[1] - padding
    return VGroup(
        Line([left + gap, top, 0], [left + leg, top, 0], color=PRIMARY_RED, stroke_width=4),
        Line([left, top - gap, 0], [left, top - leg, 0], color=PRIMARY_RED, stroke_width=4),
        Line([right - gap, top, 0], [right - leg, top, 0], color=PRIMARY_RED, stroke_width=4),
        Line([right, top - gap, 0], [right, top - leg, 0], color=PRIMARY_RED, stroke_width=4),
        Line([left + gap, bottom, 0], [left + leg, bottom, 0], color=PRIMARY_RED, stroke_width=4),
        Line([left, bottom + gap, 0], [left, bottom + leg, 0], color=PRIMARY_RED, stroke_width=4),
        Line([right - gap, bottom, 0], [right - leg, bottom, 0], color=PRIMARY_RED, stroke_width=4),
        Line([right, bottom + gap, 0], [right, bottom + leg, 0], color=PRIMARY_RED, stroke_width=4),
    ).set_stroke(opacity=0.68)


class QualityMaskTransferScene(Scene):
    def construct(self) -> None:
        self.camera.background_color = WHITE

        panel = Rectangle(
            width=11.9,
            height=5.85,
            stroke_color=GRAY_200,
            stroke_width=2,
            fill_color=WHITE,
            fill_opacity=0,
        )

        band = Rectangle(
            width=1.42,
            height=5.18,
            stroke_width=0,
            fill_color=GRAY_100,
            fill_opacity=0.98,
        ).move_to(LEFT * 4.3)

        exit_gate = Rectangle(
            width=0.34,
            height=5.18,
            stroke_width=0,
            fill_color=GRAY_100,
            fill_opacity=0.52,
        ).move_to(RIGHT * 4.65)

        top_row = VGroup(
            chip(PRIMARY_GREEN, 1.96, 0.9).move_to(LEFT * 3.45 + UP * 1.32),
            chip(PRIMARY_BLUE, 1.88, 0.86).move_to(LEFT * 0.91 + UP * 1.32),
            chip(PRIMARY_PURPLE, 1.7, 0.78).move_to(RIGHT * 1.47 + UP * 1.32),
            chip(PRIMARY_RED, 1.52, 0.72).move_to(RIGHT * 3.67 + UP * 1.32),
        )

        target_slots = VGroup(
            Circle(radius=0.62, stroke_width=2.5, stroke_color=PRIMARY_GREEN, fill_opacity=0).move_to(LEFT * 3.2 + DOWN * 1.42),
            Circle(radius=0.53, stroke_width=2.5, stroke_color=PRIMARY_BLUE, fill_opacity=0).move_to(LEFT * 0.73 + DOWN * 1.39),
            Circle(radius=0.43, stroke_width=2.5, stroke_color=PRIMARY_PURPLE, fill_opacity=0).move_to(RIGHT * 1.4 + DOWN * 1.36),
            Circle(radius=0.35, stroke_width=2.5, stroke_color=PRIMARY_RED, fill_opacity=0).move_to(RIGHT * 3.2 + DOWN * 1.32),
        ).set_stroke(opacity=0.3)

        bottom_row = VGroup(
            Circle(radius=0.58, stroke_width=0, fill_color=PRIMARY_GREEN, fill_opacity=1).move_to(target_slots[0]),
            Circle(radius=0.49, stroke_width=0, fill_color=PRIMARY_BLUE, fill_opacity=1).move_to(target_slots[1]),
            Circle(radius=0.4, stroke_width=0, fill_color=PRIMARY_PURPLE, fill_opacity=1).move_to(target_slots[2]),
            Circle(radius=0.32, stroke_width=0, fill_color=PRIMARY_RED, fill_opacity=1).move_to(target_slots[3]),
        )

        guide_lines = VGroup(*[
            Line(top_row[i].get_bottom(), bottom_row[i].get_top(), color=GRAY_200, stroke_width=2.4)
            for i in range(4)
        ]).set_opacity(0.28)

        transfer_lines = VGroup(*[
            Line(top_row[i].get_bottom(), bottom_row[i].get_top(), color=PRIMARY_ORANGE, stroke_width=5.2)
            for i in range(4)
        ])

        accent = Circle(radius=0.18, stroke_width=0, fill_color=PRIMARY_YELLOW, fill_opacity=1).move_to(LEFT * 4.3 + UP * 2.0)

        self.add(panel, guide_lines, exit_gate, top_row, target_slots, band, accent)
        self.wait(2.4)

        self.play(
            band.animate.move_to(LEFT * 2.25),
            accent.animate.move_to(LEFT * 2.25 + UP * 2.0),
            run_time=2.4,
            rate_func=smooth,
        )
        self.play(
            Create(transfer_lines[0]),
            FadeIn(bottom_row[0]),
            target_slots[0].animate.set_stroke(opacity=0.12),
            guide_lines[0].animate.set_opacity(0.0),
            run_time=1.6,
            rate_func=smooth,
        )
        self.play(transfer_lines[0].animate.set_opacity(0.18), run_time=0.45, rate_func=smooth)
        self.wait(0.35)

        self.play(
            band.animate.move_to(RIGHT * 0.0),
            accent.animate.move_to(RIGHT * 0.0 + UP * 2.0),
            run_time=2.2,
            rate_func=smooth,
        )
        self.play(
            AnimationGroup(
                Create(transfer_lines[1]),
                FadeIn(bottom_row[1]),
                Create(transfer_lines[2]),
                FadeIn(bottom_row[2]),
                lag_ratio=0.32,
            ),
            target_slots[1].animate.set_stroke(opacity=0.12),
            target_slots[2].animate.set_stroke(opacity=0.12),
            guide_lines[1].animate.set_opacity(0.0),
            guide_lines[2].animate.set_opacity(0.0),
            run_time=2.4,
            rate_func=smooth,
        )
        self.play(
            transfer_lines[1].animate.set_opacity(0.18),
            transfer_lines[2].animate.set_opacity(0.18),
            run_time=0.45,
            rate_func=smooth,
        )
        self.wait(0.35)

        self.play(
            band.animate.move_to(RIGHT * 2.9),
            accent.animate.move_to(RIGHT * 2.9 + UP * 2.0),
            run_time=2.2,
            rate_func=smooth,
        )
        self.play(
            Create(transfer_lines[3]),
            FadeIn(bottom_row[3]),
            target_slots[3].animate.set_stroke(opacity=0.12),
            guide_lines[3].animate.set_opacity(0.0),
            run_time=1.5,
            rate_func=smooth,
        )
        self.play(transfer_lines[3].animate.set_opacity(0.18), run_time=0.45, rate_func=smooth)
        self.wait(0.35)

        compact_targets = VGroup(
            Circle(radius=0.82, stroke_width=0, fill_color=PRIMARY_GREEN, fill_opacity=1).move_to(LEFT * 0.46 + UP * 0.84),
            Circle(radius=0.58, stroke_width=0, fill_color=PRIMARY_BLUE, fill_opacity=1).move_to(RIGHT * 1.42 + UP * 0.2),
            Circle(radius=0.43, stroke_width=0, fill_color=PRIMARY_PURPLE, fill_opacity=1).move_to(LEFT * 0.06 + DOWN * 1.14),
            Circle(radius=0.34, stroke_width=0, fill_color=PRIMARY_RED, fill_opacity=1).move_to(RIGHT * 1.72 + DOWN * 1.22),
        )
        terminal_brackets = corner_brackets(compact_targets)

        self.play(
            FadeOut(top_row),
            FadeOut(transfer_lines),
            guide_lines.animate.set_opacity(0.0),
            target_slots.animate.set_stroke(opacity=0.0),
            run_time=0.25,
            rate_func=smooth,
        )
        self.play(
            band.animate.move_to(RIGHT * 4.9).set_opacity(0.28),
            accent.animate.move_to(RIGHT * 4.9 + UP * 2.0).set_opacity(0.35),
            FadeOut(exit_gate),
            run_time=0.9,
            rate_func=smooth,
        )
        self.play(
            AnimationGroup(*[Transform(bottom_row[i], compact_targets[i]) for i in range(4)], lag_ratio=0.07),
            band.animate.set_opacity(0.0),
            FadeOut(accent),
            FadeOut(panel),
            run_time=1.2,
            rate_func=smooth,
        )
        self.play(FadeIn(terminal_brackets), run_time=0.65, rate_func=smooth)
        self.wait(0.45)

        for dot in bottom_row:
            self.play(dot.animate.scale(1.08), run_time=0.28, rate_func=there_and_back)
        self.wait(5.8)


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
