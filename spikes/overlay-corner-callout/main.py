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

SPIKE_DIR = Path(__file__).resolve().parent
REPO_ROOT = SPIKE_DIR.parent.parent
SPIKE_NAME = SPIKE_DIR.name
OUTPUT_DIR = REPO_ROOT / "videos" / SPIKE_NAME
STAGING_DIR = OUTPUT_DIR / ".manim"
OUTPUT_VIDEO = OUTPUT_DIR / f"{SPIKE_NAME}.webm"
OUTPUT_POSTER = OUTPUT_DIR / f"{SPIKE_NAME}.png"


class _Args(argparse.Namespace):
    quality: str
    preview: bool


def parse_args() -> _Args:
    parser = argparse.ArgumentParser(
        description="Render the overlay-corner-callout Manim spike."
    )
    parser.add_argument(
        "--quality",
        choices=("low", "medium", "high", "production", "4k"),
        default="medium",
        help="Manim quality preset. Defaults to medium for review speed.",
    )
    parser.add_argument(
        "--preview",
        action="store_true",
        help="Open the rendered video after completion.",
    )
    return parser.parse_args(namespace=_Args())


def quality_flag(quality: str) -> str:
    return {
        "low": "-ql",
        "medium": "-qm",
        "high": "-qh",
        "production": "-qp",
        "4k": "-qk",
    }[quality]


def render_command(args: _Args, poster: bool) -> list[str]:
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
        "-t",
        "-o",
        OUTPUT_VIDEO.stem if not poster else OUTPUT_POSTER.stem,
        "--media_dir",
        str(STAGING_DIR),
    ]
    if poster:
        command.append("-s")
    if args.preview:
        command.append("-p")
    command.extend([str(Path(__file__).resolve()), "OverlayCornerCalloutScene"])
    return command


def promote_rendered_file(target_name: str, destination: Path) -> None:
    matches = sorted(STAGING_DIR.glob(f"**/{target_name}"))
    if not matches:
        raise FileNotFoundError(f"Could not find {target_name} under {STAGING_DIR}")

    destination.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(matches[-1], destination)


def main() -> int:
    args = parse_args()

    video_env = os.environ.copy()
    video_env["SPIKE_RENDER_TARGET"] = "video"
    print(f"Rendering OverlayCornerCalloutScene into {OUTPUT_VIDEO}")
    video_result = subprocess.run(render_command(args, poster=False), check=False, env=video_env)
    if video_result.returncode != 0:
        return video_result.returncode
    promote_rendered_file(OUTPUT_VIDEO.name, OUTPUT_VIDEO)

    poster_env = os.environ.copy()
    poster_env["SPIKE_RENDER_TARGET"] = "poster"
    print(f"Rendering OverlayCornerCalloutScene poster into {OUTPUT_POSTER}")
    poster_result = subprocess.run(render_command(args, poster=True), check=False, env=poster_env)
    if poster_result.returncode != 0:
        return poster_result.returncode
    promote_rendered_file(OUTPUT_POSTER.name, OUTPUT_POSTER)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())


from manim import (
    BLACK,
    BLUE_E,
    DL,
    DR,
    ORIGIN,
    UL,
    UP,
    WHITE,
    Arrow,
    Circle,
    FadeIn,
    GrowArrow,
    RoundedRectangle,
    Scene,
    Text,
    VGroup,
    there_and_back,
)


class OverlayCornerCalloutScene(Scene):
    def construct(self) -> None:
        if os.environ.get("SPIKE_RENDER_TARGET") == "poster":
            self.camera.background_color = WHITE

        marker = Circle(radius=0.35, color=BLUE_E, stroke_width=10)
        marker.set_fill(BLUE_E, opacity=0.96)
        marker.move_to(DR * 2.45 + UP * 1.05)

        halo = Circle(radius=0.64, color=BLUE_E, stroke_width=6)
        halo.set_stroke(opacity=0.28)
        halo.move_to(marker)

        label_box = RoundedRectangle(
            corner_radius=0.16,
            width=3.25,
            height=0.8,
            stroke_color=BLUE_E,
            stroke_width=4,
            fill_color=WHITE,
            fill_opacity=1,
        )
        label = Text("Corner callout", font_size=28, color=BLACK)
        label.move_to(label_box.get_center())
        label_group = VGroup(label_box, label)
        label_group.next_to(marker, UL, buff=0.16)

        arrow = Arrow(
            label_group.get_bottom(),
            marker.get_top(),
            buff=0.1,
            color=BLUE_E,
            stroke_width=6,
            max_tip_length_to_length_ratio=0.16,
        )

        pulse = VGroup(halo, arrow, label_group, marker)
        pulse.shift(ORIGIN)

        self.play(
            FadeIn(halo, scale=0.9),
            FadeIn(label_group, shift=DL * 0.15),
            GrowArrow(arrow),
            FadeIn(marker),
            run_time=1.1,
        )
        self.play(
            halo.animate.scale(1.12),
            marker.animate.scale(1.06),
            run_time=0.55,
            rate_func=there_and_back,
        )
        self.wait(0.25)
