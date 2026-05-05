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


def corner_brackets(width: float, height: float, leg: float, gap: float, color: str = PRIMARY_RED) -> VGroup:
    half_w = width / 2
    half_h = height / 2
    inner_w = half_w - leg
    inner_h = half_h - leg
    return VGroup(
        Line(LEFT * (half_w - gap) + UP * half_h, LEFT * inner_w + UP * half_h, color=color, stroke_width=5),
        Line(LEFT * half_w + UP * (half_h - gap), LEFT * half_w + UP * inner_h, color=color, stroke_width=5),
        Line(RIGHT * (half_w - gap) + UP * half_h, RIGHT * inner_w + UP * half_h, color=color, stroke_width=5),
        Line(RIGHT * half_w + UP * (half_h - gap), RIGHT * half_w + UP * inner_h, color=color, stroke_width=5),
        Line(LEFT * (half_w - gap) + DOWN * half_h, LEFT * inner_w + DOWN * half_h, color=color, stroke_width=5),
        Line(LEFT * half_w + DOWN * (half_h - gap), LEFT * half_w + DOWN * inner_h, color=color, stroke_width=5),
        Line(RIGHT * (half_w - gap) + DOWN * half_h, RIGHT * inner_w + DOWN * half_h, color=color, stroke_width=5),
        Line(RIGHT * half_w + DOWN * (half_h - gap), RIGHT * half_w + DOWN * inner_h, color=color, stroke_width=5),
    )


class QualityStagedConvergenceScene(Scene):
    def construct(self) -> None:
        self.camera.background_color = WHITE
        self.camera.background_opacity = 0.0

        source_zone = soft_panel(3.1, 3.6).move_to(LEFT * 3.85)
        lane_zone = VGroup(
            Line(LEFT * 1.03 + UP * 1.38, LEFT * 1.03 + DOWN * 1.38, color=GRAY_200, stroke_width=3),
            Line(RIGHT * 1.03 + UP * 1.38, RIGHT * 1.03 + DOWN * 1.38, color=GRAY_200, stroke_width=3),
        ).move_to(LEFT * 0.48)
        target_zone = soft_panel(4.3, 3.6).move_to(RIGHT * 2.65)
        target_edge = Line(RIGHT * 4.8 + UP * 1.46, RIGHT * 4.8 + DOWN * 1.46, color=GRAY_200, stroke_width=3)

        source = VGroup(
            slab(GRAY_700, 2.22, 0.64).move_to(LEFT * 4.0 + UP * 0.88),
            slab(GRAY_500, 1.66, 0.48).move_to(LEFT * 3.58 + DOWN * 0.08),
            slab(GRAY_300, 1.12, 0.38).move_to(LEFT * 3.22 + DOWN * 0.92),
        )

        lane_slots = VGroup(
            slab(GRAY_200, 0.82, 0.22).move_to(LEFT * 0.48 + UP * 0.52),
            slab(GRAY_200, 0.62, 0.18).move_to(LEFT * 0.48),
            slab(GRAY_200, 0.46, 0.14).move_to(LEFT * 0.48 + DOWN * 0.52),
        )
        lane_slots.set_opacity(0.33)

        target_slots = VGroup(
            Circle(radius=0.56, stroke_color=GRAY_200, stroke_width=3, fill_opacity=0).move_to(RIGHT * 1.55 + UP * 0.55),
            Circle(radius=0.27, stroke_color=GRAY_200, stroke_width=3, fill_opacity=0).move_to(RIGHT * 2.55 + DOWN * 0.08),
            Circle(radius=0.17, stroke_color=GRAY_200, stroke_width=3, fill_opacity=0).move_to(RIGHT * 1.62 + DOWN * 0.78),
        )
        target_slots.set_stroke(opacity=0.42)

        route_in = Line(LEFT * 2.2, LEFT * 2.05, color=GRAY_200, stroke_width=3)
        accent = Circle(radius=0.1, stroke_width=0, fill_color=PRIMARY_RED, fill_opacity=1).move_to(route_in.get_start())

        lane_red = slab(PRIMARY_RED, 0.72, 0.18).move_to(LEFT * 0.48 + UP * 0.58)
        lane_dark = slab(GRAY_700, 0.54, 0.16).move_to(LEFT * 0.48)
        lane_mid = slab(GRAY_500, 0.38, 0.14).move_to(LEFT * 0.48 + DOWN * 0.58)

        final_red = Circle(radius=0.56, stroke_width=0, fill_color=PRIMARY_RED, fill_opacity=1).move_to(RIGHT * 0.07 + UP * 0.55)
        final_dark = Circle(radius=0.27, stroke_width=0, fill_color=GRAY_700, fill_opacity=1).move_to(RIGHT * 1.03 + DOWN * 0.08)
        final_mid = Circle(radius=0.17, stroke_width=0, fill_color=GRAY_500, fill_opacity=1).move_to(RIGHT * 0.17 + DOWN * 0.78)

        terminal_brackets = corner_brackets(3.05, 2.45, 0.34, 0.1).move_to(RIGHT * 0.57 + DOWN * 0.02)

        self.add(source_zone, lane_zone, lane_slots, target_zone, target_edge, target_slots, source, accent)
        self.wait(2.7)
        self.play(MoveAlongPath(accent, route_in), run_time=1.4, rate_func=smooth)
        self.play(
            AnimationGroup(
                FadeOut(accent, run_time=0.5),
                FadeOut(lane_slots, run_time=0.5),
                FadeOut(target_edge, run_time=1.2),
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
        self.wait(3.0)
        self.play(FadeOut(target_slots), FadeOut(lane_zone), run_time=0.8)
        self.play(
            AnimationGroup(
                Transform(source[0], final_red.copy()),
                Transform(source[1], final_dark.copy()),
                Transform(source[2], final_mid.copy()),
                lag_ratio=0.08,
            ),
            run_time=3.5,
            rate_func=smooth,
        )
        self.play(
            FadeOut(source_zone),
            FadeOut(target_zone),
            FadeIn(terminal_brackets, scale=0.98),
            run_time=2.3,
            rate_func=smooth,
        )
        self.wait(8.1)


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
            "scale=320:-1,tile=5x17:margin=8:padding=4:color=white",
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
