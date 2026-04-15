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

MAIN_VIDEO = OUTPUT_DIR / "inset-annotation-panel-main.webm"
MAIN_POSTER = OUTPUT_DIR / "inset-annotation-panel-main.png"
ZOOM_VIDEO = OUTPUT_DIR / "inset-annotation-panel-zoom.webm"
ZOOM_POSTER = OUTPUT_DIR / "inset-annotation-panel-zoom.png"


class _Args(argparse.Namespace):
    quality: str
    preview: bool


def parse_args() -> _Args:
    parser = argparse.ArgumentParser(
        description="Render the inset-annotation-panel Manim spike."
    )
    parser.add_argument(
        "--quality",
        choices=("low", "medium", "high", "production", "4k"),
        default="medium",
        help="Manim quality preset. Defaults to medium for quick iteration.",
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


def build_command(
    args: _Args,
    *,
    variant: str,
    target: Path,
    poster: bool,
    resolution: str,
) -> tuple[list[str], dict[str, str]]:
    STAGING_DIR.mkdir(parents=True, exist_ok=True)
    command = [
        sys.executable,
        "-m",
        "manim",
        "render",
        quality_flag(args.quality),
    ]

    if poster:
        command.append("-s")
    else:
        command.extend(["--format", "webm", "-t"])
        if args.preview:
            command.append("-p")

    command.extend(
        [
            "-r",
            resolution,
            "-o",
            target.stem,
            "--media_dir",
            str(STAGING_DIR),
        ]
    )
    command.extend([str(Path(__file__).resolve()), "InsetAnnotationPanelScene"])

    env = os.environ.copy()
    env["SPIKE_RENDER_TARGET"] = "poster" if poster else "video"
    env["SPIKE_VARIANT"] = variant
    return command, env


def promote_rendered_file(target_name: str, destination: Path) -> None:
    matches = sorted(STAGING_DIR.glob(f"**/{target_name}"))
    if not matches:
        raise FileNotFoundError(f"Could not find {target_name} under {STAGING_DIR}")

    destination.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(matches[-1], destination)


def render_asset(
    args: _Args,
    *,
    variant: str,
    target: Path,
    poster: bool,
    resolution: str,
) -> int:
    command, env = build_command(
        args,
        variant=variant,
        target=target,
        poster=poster,
        resolution=resolution,
    )
    result = subprocess.run(command, env=env)
    if result.returncode != 0:
        return result.returncode
    promote_rendered_file(target.name, target)
    return 0


def main() -> int:
    args = parse_args()

    tasks = [
        ("main", MAIN_VIDEO, False, "1600,900"),
        ("main", MAIN_POSTER, True, "1600,900"),
        ("zoom", ZOOM_VIDEO, False, "1200,1200"),
        ("zoom", ZOOM_POSTER, True, "1200,1200"),
    ]

    for variant, target, poster, resolution in tasks:
        result = render_asset(
            args,
            variant=variant,
            target=target,
            poster=poster,
            resolution=resolution,
        )
        if result != 0:
            return result

    return 0


if __name__ == "__main__":
    raise SystemExit(main())


from manim import (
    BLUE_B,
    BLUE_D,
    BLUE_E,
    DOWN,
    GREY_B,
    GREY_D,
    LEFT,
    RIGHT,
    UR,
    WHITE,
    Circle,
    Create,
    FadeIn,
    Line,
    RoundedRectangle,
    Scene,
    Text,
    UP,
    linear,
)


class InsetAnnotationPanelScene(Scene):
    def construct(self) -> None:
        variant = os.environ.get("SPIKE_VARIANT", "main")
        if os.environ.get("SPIKE_RENDER_TARGET") == "poster":
            self.camera.background_color = WHITE

        if variant == "zoom":
            self.construct_zoom()
        else:
            self.construct_main()

    def construct_main(self) -> None:
        panel = RoundedRectangle(
            width=11.7,
            height=5.55,
            corner_radius=0.36,
            stroke_color=BLUE_E,
            stroke_width=6,
            fill_color=WHITE,
            fill_opacity=0.94,
        )
        header = Text(
            "Primary annotation panel",
            font_size=28,
            color=BLUE_D,
        ).next_to(panel.get_top(), DOWN, buff=0.28)

        track = Line(LEFT * 5.0 + DOWN * 0.65, RIGHT * 4.85 + DOWN * 0.65, color=GREY_B, stroke_width=8)
        track_label = Text("detail anchor", font_size=20, color=GREY_D).next_to(track, UP, buff=0.18)
        focus = Circle(radius=0.13, color=BLUE_B, stroke_width=0).set_fill(BLUE_B, opacity=1.0)
        focus.move_to(LEFT * 4.35 + DOWN * 0.65)
        callout = RoundedRectangle(
            width=2.35,
            height=0.72,
            corner_radius=0.18,
            stroke_color=BLUE_E,
            stroke_width=3,
            fill_color=BLUE_B,
            fill_opacity=0.12,
        ).move_to(UR * 1.95 + DOWN * 0.15)
        callout_text = Text("magnified later", font_size=18, color=BLUE_E).move_to(callout.get_center())
        accent = Line(UR * 1.35 + DOWN * 0.82, LEFT * 0.55 + DOWN * 0.58, color=BLUE_E, stroke_width=4)

        moving_dot = Circle(radius=0.45, color=BLUE_E, stroke_width=10).set_fill(BLUE_E, opacity=0.92)
        moving_dot.move_to(LEFT * 4.55 + UP * 0.8)
        motion_track = Line(LEFT * 4.45 + UP * 0.8, RIGHT * 4.45 + UP * 0.8, color=GREY_D, stroke_width=12)

        self.add(panel, header, motion_track, track, track_label, focus, accent)
        self.play(FadeIn(moving_dot), run_time=0.4)
        self.play(moving_dot.animate.move_to(RIGHT * 4.45 + UP * 0.8), run_time=3.1, rate_func=linear)
        self.play(FadeIn(callout), FadeIn(callout_text), run_time=0.35)
        self.wait(0.2)

    def construct_zoom(self) -> None:
        panel = RoundedRectangle(
            width=5.9,
            height=5.9,
            corner_radius=0.42,
            stroke_color=BLUE_E,
            stroke_width=6,
            fill_color=WHITE,
            fill_opacity=0.96,
        )
        title = Text("Zoomed detail", font_size=30, color=BLUE_D).next_to(panel.get_top(), DOWN, buff=0.22)
        magnifier = Circle(radius=1.65, color=BLUE_B, stroke_width=8).set_fill(BLUE_B, opacity=0.08)
        magnifier.shift(DOWN * 0.1)
        cross_h = Line(LEFT * 1.25, RIGHT * 1.25, color=GREY_B, stroke_width=6).move_to(magnifier)
        cross_v = Line(UP * 1.25, DOWN * 1.25, color=GREY_B, stroke_width=6).move_to(magnifier)
        detail_dot = Circle(radius=0.38, color=BLUE_E, stroke_width=10).set_fill(BLUE_E, opacity=0.95)
        detail_dot.move_to(LEFT * 0.5 + UP * 0.35)
        label = Text("detail focus", font_size=22, color=BLUE_E).next_to(magnifier, DOWN, buff=0.28)
        lens_ring = Circle(radius=2.1, color=BLUE_E, stroke_width=4).move_to(magnifier)

        self.add(panel, title, cross_h, cross_v, label)
        self.play(Create(magnifier), run_time=0.5)
        self.play(Create(detail_dot), run_time=0.25)
        self.play(
            detail_dot.animate.move_to(RIGHT * 0.95 + DOWN * 0.15),
            run_time=2.6,
            rate_func=linear,
        )
        self.play(Create(lens_ring), run_time=0.4)
        self.wait(0.2)
