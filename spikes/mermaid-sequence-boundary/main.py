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
VIDEO_PATH = OUTPUT_DIR / "mermaid-sequence-boundary.webm"
POSTER_PATH = OUTPUT_DIR / "mermaid-sequence-boundary.png"

PRIMARY_RED = "#9e1b32"
PRIMARY_ORANGE = "#e77204"
PRIMARY_YELLOW = "#f1c319"
PRIMARY_GREEN = "#45842a"
PRIMARY_BLUE = "#007298"
PRIMARY_PURPLE = "#652f6c"
GRAY = "#333e48"
GRAY_200 = "#cfcfcf"
SHADOW_BLUE = "#004d66"
HIGHLIGHT_BLUE = "#cdf3ff"
HIGHLIGHT_GREEN = "#dbffcc"
WHITE = "#ffffff"
PAGE_BACKGROUND = "#f7f7f7"


class _Args(argparse.Namespace):
    quality: str
    preview: bool


def parse_args() -> _Args:
    parser = argparse.ArgumentParser(
        description="Render the mermaid-sequence-boundary Manim spike."
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


def render_command(args: _Args, *, poster: bool) -> list[str]:
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
        (POSTER_PATH if poster else VIDEO_PATH).stem,
        "--media_dir",
        str(STAGING_DIR),
    ]
    if not poster:
        command.append("-t")
    if poster:
        command.append("-s")
    elif args.preview:
        command.append("-p")
    command.extend([str(Path(__file__).resolve()), "MermaidSequenceBoundaryScene"])
    return command


def promote_rendered_file(target_name: str, destination: Path) -> None:
    matches = sorted(STAGING_DIR.glob(f"**/{target_name}"))
    if not matches:
        raise FileNotFoundError(f"Could not find {target_name} under {STAGING_DIR}")
    destination.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(matches[-1], destination)


def render_scene(args: _Args) -> None:
    video_env = os.environ.copy()
    video_env["SPIKE_RENDER_TARGET"] = "video"
    video_result = subprocess.run(render_command(args, poster=False), check=False, env=video_env)
    if video_result.returncode != 0:
        raise SystemExit(video_result.returncode)
    promote_rendered_file(VIDEO_PATH.name, VIDEO_PATH)

    poster_env = os.environ.copy()
    poster_env["SPIKE_RENDER_TARGET"] = "poster"
    poster_result = subprocess.run(render_command(args, poster=True), check=False, env=poster_env)
    if poster_result.returncode != 0:
        raise SystemExit(poster_result.returncode)
    promote_rendered_file(POSTER_PATH.name, POSTER_PATH)


def main() -> int:
    args = parse_args()
    render_scene(args)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())


from manim import (
    Arrow,
    DOWN,
    FadeIn,
    LEFT,
    RIGHT,
    RoundedRectangle,
    Scene,
    Text,
    UP,
    VGroup,
)


class MermaidSequenceBoundaryScene(Scene):
    def construct(self) -> None:
        if os.environ.get("SPIKE_RENDER_TARGET") == "poster":
            self.camera.background_color = PAGE_BACKGROUND

        stage = RoundedRectangle(
            width=12.8,
            height=6.25,
            corner_radius=0.34,
            stroke_color=GRAY_200,
            stroke_width=2,
            fill_color=PAGE_BACKGROUND,
            fill_opacity=0.96,
        )

        alice_card = RoundedRectangle(width=3.2, height=1.2, corner_radius=0.18)
        alice_card.set_stroke(PRIMARY_GREEN, width=6, opacity=0.9)
        alice_card.set_fill(HIGHLIGHT_GREEN, opacity=0.95)
        alice_card.shift(LEFT * 4.1 + UP * 1.2)

        bob_card = RoundedRectangle(width=3.0, height=1.2, corner_radius=0.18)
        bob_card.set_stroke(PRIMARY_BLUE, width=6, opacity=0.9)
        bob_card.set_fill(HIGHLIGHT_BLUE, opacity=0.95)
        bob_card.shift(RIGHT * 4.1 + UP * 1.2)

        alice_label = Text("Alice", font_size=34, color=GRAY).move_to(alice_card)
        bob_label = Text("Bob", font_size=34, color=GRAY).move_to(bob_card)

        boundary_tag = Text("boundary", font_size=20, color=PRIMARY_GREEN)
        boundary_tag.next_to(alice_card, DOWN, buff=0.18)

        service_tag = Text("service", font_size=20, color=PRIMARY_BLUE)
        service_tag.next_to(bob_card, DOWN, buff=0.18)

        request_arrow = Arrow(
            start=alice_card.get_right() + DOWN * 1.15,
            end=bob_card.get_left() + DOWN * 1.15,
            buff=0.12,
            stroke_width=10,
            max_stroke_width_to_length_ratio=999,
            max_tip_length_to_length_ratio=0.08,
            color=PRIMARY_ORANGE,
        )

        request_label = Text("Request from boundary", font_size=28, color=PRIMARY_ORANGE)
        request_label.next_to(request_arrow, UP, buff=0.18)

        response_arrow = Arrow(
            start=bob_card.get_left() + DOWN * 2.25,
            end=alice_card.get_right() + DOWN * 2.25,
            buff=0.12,
            stroke_width=10,
            max_stroke_width_to_length_ratio=999,
            max_tip_length_to_length_ratio=0.08,
            color=PRIMARY_RED,
        )

        response_label = Text("Response to boundary", font_size=28, color=PRIMARY_RED)
        response_label.next_to(response_arrow, DOWN, buff=0.2)

        helper = Text("Boundary initiates. Service answers.", font_size=26, color=SHADOW_BLUE)
        helper.to_edge(DOWN).shift(UP * 0.45)

        group = VGroup(
            alice_card,
            bob_card,
            alice_label,
            bob_label,
            boundary_tag,
            service_tag,
            helper,
        )

        self.add(stage)
        self.play(FadeIn(group, shift=UP * 0.15), run_time=1.8)
        self.wait(0.8)
        self.play(FadeIn(request_arrow), FadeIn(request_label), run_time=2.0)
        self.wait(1.6)
        self.play(FadeIn(response_arrow), FadeIn(response_label), run_time=2.0)
        self.wait(1.8)
