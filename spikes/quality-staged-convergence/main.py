#!/usr/bin/env -S uv run --script
# /// script
# dependencies = [
#   "imageio-ffmpeg>=0.6.0",
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
    FadeIn,
    FadeOut,
    Line,
    MoveAlongPath,
    Rectangle,
    Scene,
    Transform,
    VGroup,
    WHITE,
    config,
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
GRAY_300 = "#b7b7b7"
GRAY_500 = "#737373"
GRAY_700 = "#3d3d3d"

config.transparent = True
config.background_opacity = 0.0


class _Args(argparse.Namespace):
    quality: str
    skip_review: bool


def parse_args() -> _Args:
    parser = argparse.ArgumentParser(description="Render the quality-staged-convergence spike.")
    parser.add_argument("--quality", choices=("low", "medium", "high", "production", "4k"), default="medium")
    parser.add_argument("--skip-review", action="store_true", help="Skip extracting 0.3s white-background review frames.")
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
        "--transparent",
        "--format",
        "webm",
        "-o",
        stem,
        "--media_dir",
        str(STAGING_DIR),
        str(Path(__file__).resolve()),
        "QualityStagedConvergenceScene",
    ]
    if poster:
        command.insert(-2, "-s")
    return command


def promote(target_name: str, destination: Path) -> None:
    matches = list(STAGING_DIR.glob(f"**/{target_name}"))
    if not matches:
        raise FileNotFoundError(target_name)
    destination.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(max(matches, key=lambda path: path.stat().st_mtime), destination)


def slab(color: str, width: float, height: float) -> Rectangle:
    return Rectangle(width=width, height=height, stroke_width=0, fill_color=color, fill_opacity=1)


def soft_panel(width: float, height: float) -> Rectangle:
    return Rectangle(width=width, height=height, stroke_width=0, fill_color=GRAY_100, fill_opacity=0.2)


def corner_brackets(
    width: float,
    height: float,
    leg: float,
    gap: float,
    color: str = PRIMARY_RED,
    stroke_width: float = 5,
    opacity: float = 1.0,
) -> VGroup:
    half_w = width / 2
    half_h = height / 2
    inner_w = half_w - leg
    inner_h = half_h - leg
    return VGroup(
        Line(LEFT * (half_w - gap) + UP * half_h, LEFT * inner_w + UP * half_h, color=color, stroke_width=stroke_width),
        Line(LEFT * half_w + UP * (half_h - gap), LEFT * half_w + UP * inner_h, color=color, stroke_width=stroke_width),
        Line(RIGHT * (half_w - gap) + UP * half_h, RIGHT * inner_w + UP * half_h, color=color, stroke_width=stroke_width),
        Line(RIGHT * half_w + UP * (half_h - gap), RIGHT * half_w + UP * inner_h, color=color, stroke_width=stroke_width),
        Line(LEFT * (half_w - gap) + DOWN * half_h, LEFT * inner_w + DOWN * half_h, color=color, stroke_width=stroke_width),
        Line(LEFT * half_w + DOWN * (half_h - gap), LEFT * half_w + DOWN * inner_h, color=color, stroke_width=stroke_width),
        Line(RIGHT * (half_w - gap) + DOWN * half_h, RIGHT * inner_w + DOWN * half_h, color=color, stroke_width=stroke_width),
        Line(RIGHT * half_w + DOWN * (half_h - gap), RIGHT * half_w + DOWN * inner_h, color=color, stroke_width=stroke_width),
    )
    brackets.set_stroke(opacity=opacity)
    return brackets


class QualityStagedConvergenceScene(Scene):
    def construct(self) -> None:
        self.camera.background_color = WHITE
        self.camera.background_opacity = 0.0

        lane_zone = VGroup(
            Line(LEFT * 1.03 + UP * 1.52, LEFT * 1.03 + DOWN * 1.52, color=GRAY_200, stroke_width=3),
            Line(RIGHT * 1.03 + UP * 1.52, RIGHT * 1.03 + DOWN * 1.52, color=GRAY_200, stroke_width=3),
        ).move_to(LEFT * 0.35)
        target_edge = slab(GRAY_200, 0.035, 2.96).move_to(RIGHT * 4.2)
        target_edge.set_opacity(0.55)

        source = VGroup(
            slab(GRAY_700, 2.5, 0.72).move_to(LEFT * 3.3 + UP * 1.02),
            slab(GRAY_500, 1.84, 0.52).move_to(LEFT * 2.95 + UP * 0.02),
            slab(GRAY_300, 1.24, 0.4).move_to(LEFT * 2.6 + DOWN * 0.86),
        )

        lane_slots = VGroup(
            slab(GRAY_200, 0.98, 0.24).move_to(LEFT * 0.35 + UP * 0.64),
            slab(GRAY_200, 0.72, 0.18).move_to(LEFT * 0.35),
            slab(GRAY_200, 0.52, 0.14).move_to(LEFT * 0.35 + DOWN * 0.64),
        )
        lane_slots.set_opacity(0.42)

        target_red = Circle(radius=0.62, stroke_width=0, fill_color=PRIMARY_RED, fill_opacity=1).move_to(RIGHT * 0.72 + UP * 0.62)
        target_dark = Circle(radius=0.3, stroke_width=0, fill_color=GRAY_700, fill_opacity=1).move_to(RIGHT * 1.62 + DOWN * 0.06)
        target_mid = Circle(radius=0.2, stroke_width=0, fill_color=GRAY_500, fill_opacity=1).move_to(RIGHT * 0.82 + DOWN * 0.78)

        target_slots = VGroup(
            Circle(radius=target_red.radius, stroke_color=GRAY_200, stroke_width=3, fill_color=GRAY_100, fill_opacity=0.06).move_to(target_red),
            Circle(radius=target_dark.radius, stroke_color=GRAY_200, stroke_width=3, fill_color=GRAY_100, fill_opacity=0.06).move_to(target_dark),
            Circle(radius=target_mid.radius, stroke_color=GRAY_200, stroke_width=3, fill_color=GRAY_100, fill_opacity=0.06).move_to(target_mid),
        )
        target_slots.set_stroke(opacity=0.52)

        target_guides = VGroup()

        route_in = Line(LEFT * 2.3 + UP * 0.45, LEFT * 1.88 + UP * 0.45, color=GRAY_200, stroke_width=3)
        accent = Circle(radius=0.1, stroke_width=0, fill_color=PRIMARY_RED, fill_opacity=1).move_to(route_in.get_start())

        lane_red = slab(PRIMARY_RED, 0.92, 0.22).move_to(LEFT * 0.35 + UP * 0.66)
        lane_dark = slab(GRAY_700, 0.68, 0.18).move_to(LEFT * 0.35)
        lane_mid = slab(GRAY_500, 0.48, 0.15).move_to(LEFT * 0.35 + DOWN * 0.66)

        final_red = Circle(radius=0.62, stroke_width=0, fill_color=PRIMARY_RED, fill_opacity=1).move_to(RIGHT * 0.08 + UP * 0.58)
        final_dark = Circle(radius=0.3, stroke_width=0, fill_color=GRAY_700, fill_opacity=1).move_to(RIGHT * 1.04 + DOWN * 0.08)
        final_mid = Circle(radius=0.2, stroke_width=0, fill_color=GRAY_500, fill_opacity=1).move_to(RIGHT * 0.18 + DOWN * 0.82)

        terminal_brackets = corner_brackets(3.25, 2.6, 0.36, 0.12).move_to(RIGHT * 0.58 + DOWN * 0.03)

        self.add(lane_zone, lane_slots, target_edge, target_guides, target_slots, source, accent)
        self.wait(2.7)
        self.play(MoveAlongPath(accent, route_in), run_time=1.6, rate_func=smooth)
        self.play(
            AnimationGroup(
                FadeOut(accent, run_time=0.5),
                FadeOut(lane_zone, run_time=0.6),
                FadeOut(lane_slots, run_time=0.5),
                FadeOut(target_edge, run_time=1.1),
                AnimationGroup(
                    Transform(source[0], lane_red.copy()),
                    Transform(source[1], lane_dark.copy()),
                    Transform(source[2], lane_mid.copy()),
                    lag_ratio=0.16,
                    run_time=3.2,
                ),
                lag_ratio=0,
            ),
            run_time=3.2,
            rate_func=smooth,
        )
        self.play(FadeIn(lane_zone), run_time=0.5)
        self.wait(2.4)
        self.play(FadeOut(lane_zone), run_time=0.8)
        self.play(
            AnimationGroup(
                Transform(source[0], target_red.copy()),
                Transform(source[1], target_dark.copy()),
                Transform(source[2], target_mid.copy()),
                FadeOut(target_slots, run_time=1.8),
                FadeOut(target_guides, run_time=1.6),
                lag_ratio=0.08,
            ),
            run_time=3.4,
            rate_func=smooth,
        )
        self.wait(1.4)
        self.play(
            Transform(source[0], final_red.copy()),
            Transform(source[1], final_dark.copy()),
            Transform(source[2], final_mid.copy()),
            FadeIn(terminal_brackets, scale=0.98),
            run_time=2.8,
            rate_func=smooth,
        )
        self.wait(6.9)


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
    if not args.skip_review:
        extract_review_frames(video_path)


def extract_review_frames(video_path: Path) -> None:
    import imageio_ffmpeg

    review_dir = OUTPUT_DIR / "review-frames"
    review_dir.mkdir(parents=True, exist_ok=True)
    for path in review_dir.glob("frame_*.png"):
        path.unlink()
    contact_sheet = review_dir / "contact-sheet.png"
    if contact_sheet.exists():
        contact_sheet.unlink()

    ffmpeg = imageio_ffmpeg.get_ffmpeg_exe()
    subprocess.run(
        [
            ffmpeg,
            "-hide_banner",
            "-loglevel",
            "error",
            "-f",
            "lavfi",
            "-i",
            "color=c=white:s=1600x900:r=30",
            "-c:v",
            "libvpx-vp9",
            "-i",
            str(video_path),
            "-filter_complex",
            "[1:v]format=rgba[fg];[0:v][fg]overlay=shortest=1:format=auto,fps=10/3",
            str(review_dir / "frame_%04d.png"),
        ],
        check=True,
    )
    frame_count = len(list(review_dir.glob("frame_*.png")))
    tile_columns = 5
    tile_rows = max(1, (frame_count + tile_columns - 1) // tile_columns)
    subprocess.run(
        [
            ffmpeg,
            "-hide_banner",
            "-loglevel",
            "error",
            "-framerate",
            "10/3",
            "-i",
            str(review_dir / "frame_%04d.png"),
            "-vf",
            f"scale=320:-1,tile={tile_columns}x{tile_rows}:margin=8:padding=4:color=white",
            str(contact_sheet),
        ],
        check=True,
    )


def main() -> int:
    args = parse_args()
    render_variant(args)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
