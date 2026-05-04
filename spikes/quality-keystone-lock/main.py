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
    PI,
    RIGHT,
    UP,
    AnimationGroup,
    Create,
    FadeOut,
    Line,
    Polygon,
    Rectangle,
    Scene,
    Transform,
    WHITE,
    smooth,
)

SPIKE_DIR = Path(__file__).resolve().parent
REPO_ROOT = SPIKE_DIR.parent.parent
SPIKE_NAME = SPIKE_DIR.name
OUTPUT_DIR = REPO_ROOT / "videos" / SPIKE_NAME
STAGING_DIR = OUTPUT_DIR / ".manim"

PRIMARY_RED = "#9e1b32"
GRAY_100 = "#e7e7e7"
GRAY_200 = "#cfcfcf"


class _Args(argparse.Namespace):
    quality: str


def parse_args() -> _Args:
    parser = argparse.ArgumentParser(description="Render the quality-keystone-lock spike.")
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
        "--transparent",
        "-o",
        stem,
        "--media_dir",
        str(STAGING_DIR),
        str(Path(__file__).resolve()),
        "QualityKeystoneLockScene",
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


def slab(color: str, width: float, height: float, opacity: float = 1) -> Rectangle:
    return Rectangle(width=width, height=height, stroke_width=0, fill_color=color, fill_opacity=opacity)


def slot(width: float, height: float, opacity: float = 0.42) -> Rectangle:
    return Rectangle(width=width, height=height, stroke_color=GRAY_200, stroke_width=2, fill_color=WHITE, fill_opacity=0).set_stroke(opacity=opacity)


def keystone(color: str, opacity: float = 1) -> Polygon:
    return Polygon(
        LEFT * 0.96 + UP * 0.45,
        RIGHT * 0.74 + UP * 0.45,
        RIGHT * 1.04,
        RIGHT * 0.58 + DOWN * 0.45,
        LEFT * 0.96 + DOWN * 0.45,
        stroke_width=0,
        fill_color=color,
        fill_opacity=opacity,
    )


class QualityKeystoneLockScene(Scene):
    def construct(self) -> None:
        self.camera.background_color = WHITE

        source_zone = Rectangle(width=3.95, height=3.35, stroke_width=0, fill_color=GRAY_100, fill_opacity=0.15).move_to(LEFT * 3.55)
        target_plate = Rectangle(width=3.9, height=3.35, stroke_width=0, fill_color=GRAY_100, fill_opacity=0.12).move_to(RIGHT * 2.45)
        route = Line(LEFT * 2.2 + DOWN * 0.04, RIGHT * 1.0 + DOWN * 0.04).set_stroke(GRAY_200, 3, opacity=0.55)

        leader = keystone(PRIMARY_RED).scale(0.95).move_to(LEFT * 3.55)
        support_top = slab(GRAY_200, 1.72, 0.3, 0.95).move_to(LEFT * 3.58 + UP * 0.86)
        support_lower = slab(GRAY_200, 1.36, 0.3, 0.95).move_to(LEFT * 3.25 + DOWN * 0.88)
        support_post = slab(GRAY_200, 0.32, 1.35, 0.95).move_to(LEFT * 4.58 + DOWN * 0.04)

        upper_slot = slot(1.96, 0.34).rotate(-PI / 8).move_to(RIGHT * 2.2 + UP * 0.66)
        lower_slot = slot(1.86, 0.34).rotate(PI / 8).move_to(RIGHT * 2.18 + DOWN * 0.66)
        post_slot = slot(0.34, 1.62).move_to(RIGHT * 3.22 + DOWN * 0.02)
        notch_outline = keystone(GRAY_200, opacity=0).scale(1.02).move_to(RIGHT * 2.24)
        notch_outline.set_stroke(GRAY_200, 2, opacity=0.5)
        for guide in (source_zone, target_plate, route, upper_slot, lower_slot, post_slot, notch_outline):
            guide.set_z_index(0)
        for support in (support_top, support_lower, support_post):
            support.set_z_index(1)
        leader.set_z_index(2)

        upper_lock = slab(GRAY_200, 1.96, 0.3, 0.95).rotate(-PI / 8).move_to(RIGHT * 2.2 + UP * 0.66)
        lower_lock = slab(GRAY_200, 1.86, 0.3, 0.95).rotate(PI / 8).move_to(RIGHT * 2.18 + DOWN * 0.66)
        post_lock = slab(GRAY_200, 0.32, 1.58, 0.95).move_to(RIGHT * 3.22 + DOWN * 0.02)
        red_stretch = keystone(PRIMARY_RED).scale(0.95).stretch(1.34, 0).move_to(LEFT * 0.42)
        red_lock = keystone(PRIMARY_RED).scale(0.95).move_to(RIGHT * 2.24)
        final_shift = LEFT * 1.72

        upper_tight = slab(GRAY_200, 1.78, 0.3, 0.95).rotate(-PI / 8).move_to(RIGHT * 2.18 + UP * 0.55)
        lower_tight = slab(GRAY_200, 1.7, 0.3, 0.95).rotate(PI / 8).move_to(RIGHT * 2.16 + DOWN * 0.55)
        post_tight = slab(GRAY_200, 0.32, 1.35, 0.95).move_to(RIGHT * 3.06 + DOWN * 0.02)

        final_leader = keystone(PRIMARY_RED).scale(0.92).move_to(RIGHT * 0.52)
        final_upper = slab(GRAY_200, 1.42, 0.28, 0.95).rotate(-PI / 9).move_to(RIGHT * 0.5 + UP * 0.6)
        final_lower = slab(GRAY_200, 1.34, 0.28, 0.95).rotate(PI / 9).move_to(RIGHT * 0.48 + DOWN * 0.6)
        final_post = slab(GRAY_200, 0.28, 1.1, 0.95).move_to(RIGHT * 1.72)

        self.add(
            source_zone,
            target_plate,
            route,
            upper_slot,
            lower_slot,
            post_slot,
            leader,
            support_top,
            support_lower,
            support_post,
        )
        self.wait(2.4)
        self.play(Create(notch_outline), run_time=0.7)
        self.play(
            AnimationGroup(
                Transform(support_top, upper_lock.copy()),
                Transform(support_lower, lower_lock.copy()),
                Transform(support_post, post_lock.copy()),
                lag_ratio=0.18,
            ),
            run_time=4.0,
            rate_func=smooth,
        )
        self.wait(1.1)
        self.play(Transform(leader, red_stretch.copy()), run_time=2.1, rate_func=smooth)
        self.play(Transform(leader, red_lock.copy()), run_time=2.5, rate_func=smooth)
        self.wait(1.5)
        self.play(
            AnimationGroup(
                FadeOut(upper_slot),
                FadeOut(lower_slot),
                FadeOut(post_slot),
                FadeOut(notch_outline),
                Transform(leader, red_lock.copy().shift(final_shift)),
                Transform(support_top, upper_tight.copy().shift(final_shift)),
                Transform(support_lower, lower_tight.copy().shift(final_shift)),
                Transform(support_post, post_tight.copy().shift(final_shift)),
                lag_ratio=0.05,
            ),
            run_time=2.4,
            rate_func=smooth,
        )
        self.play(FadeOut(source_zone), FadeOut(target_plate), FadeOut(route), run_time=0.7)
        self.wait(1.2)
        self.play(
            AnimationGroup(
                Transform(leader, final_leader.copy()),
                Transform(support_top, final_upper.copy()),
                Transform(support_lower, final_lower.copy()),
                Transform(support_post, final_post.copy()),
                lag_ratio=0.06,
            ),
            run_time=2.4,
            rate_func=smooth,
        )
        self.wait(6.3)


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
