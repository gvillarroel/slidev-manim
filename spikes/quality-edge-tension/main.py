#!/usr/bin/env -S uv run --script
# /// script
# dependencies = [
#   "imageio-ffmpeg>=0.6.0",
#   "manim>=0.20.0",
#   "Pillow>=10.0.0",
# ]
# ///

from __future__ import annotations

import argparse
import math
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
    Rectangle,
    Scene,
    Transform,
    VGroup,
    config,
    smooth,
    there_and_back,
)
from PIL import Image, ImageDraw

config.transparent = True
config.background_opacity = 0.0

SPIKE_DIR = Path(__file__).resolve().parent
REPO_ROOT = SPIKE_DIR.parent.parent
SPIKE_NAME = SPIKE_DIR.name
OUTPUT_DIR = REPO_ROOT / "videos" / SPIKE_NAME
STAGING_DIR = OUTPUT_DIR / ".manim"
CADENCE_REVIEW_DIR = OUTPUT_DIR / "review-frames-0.3s"
CADENCE_RAW_DIR = CADENCE_REVIEW_DIR / "raw-alpha"
CADENCE_FRAMES_DIR = CADENCE_REVIEW_DIR / "frames"
CADENCE_SHEETS_DIR = CADENCE_REVIEW_DIR / "sheets"

PRIMARY_RED = "#9e1b32"
GRAY_100 = "#e7e7e7"
GRAY_200 = "#cfcfcf"
GRAY_300 = "#b5b5b5"
GRAY_500 = "#828282"


class _Args(argparse.Namespace):
    quality: str


def parse_args() -> _Args:
    parser = argparse.ArgumentParser(description="Render the quality-edge-tension spike.")
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
        "--transparent",
        "--format",
        "webm",
        "-o",
        stem,
        "--media_dir",
        str(STAGING_DIR),
        str(Path(__file__).resolve()),
        "QualityEdgeTensionScene",
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


def build_cadence_review(video_path: Path) -> None:
    import imageio_ffmpeg

    for path in (CADENCE_RAW_DIR, CADENCE_FRAMES_DIR, CADENCE_SHEETS_DIR):
        if path.exists():
            shutil.rmtree(path)
        path.mkdir(parents=True, exist_ok=True)

    ffmpeg = Path(imageio_ffmpeg.get_ffmpeg_exe()).resolve()
    subprocess.run(
        [
            str(ffmpeg),
            "-y",
            "-c:v",
            "libvpx-vp9",
            "-i",
            str(video_path),
            "-vf",
            "fps=10/3,format=rgba",
            "-fps_mode",
            "vfr",
            str(CADENCE_RAW_DIR / "frame-%04d.png"),
        ],
        check=True,
    )

    saved: list[Path] = []
    for raw_frame in sorted(CADENCE_RAW_DIR.glob("frame-*.png")):
        image = Image.open(raw_frame).convert("RGBA")
        background = Image.new("RGBA", image.size, "white")
        output = Image.alpha_composite(background, image).convert("RGB")
        frame_path = CADENCE_FRAMES_DIR / raw_frame.name
        output.save(frame_path)
        saved.append(frame_path)

    build_cadence_contact_sheets(saved)
    print(f"Wrote {len(saved)} cadence review frames to {CADENCE_FRAMES_DIR}")


def build_cadence_contact_sheets(frames: list[Path]) -> None:
    thumb_width = 320
    thumb_height = 180
    columns = 4
    rows = 5
    padding = 14
    label_height = 26
    frames_per_sheet = columns * rows
    sheet_count = math.ceil(len(frames) / frames_per_sheet)

    for sheet_index in range(sheet_count):
        chunk = frames[sheet_index * frames_per_sheet : (sheet_index + 1) * frames_per_sheet]
        canvas = Image.new(
            "RGB",
            (
                columns * thumb_width + (columns + 1) * padding,
                rows * (thumb_height + label_height) + (rows + 1) * padding,
            ),
            "white",
        )
        draw = ImageDraw.Draw(canvas)
        for index, frame_path in enumerate(chunk):
            frame_index = int(frame_path.stem.split("-")[-1]) - 1
            timestamp = frame_index * 0.3
            thumbnail = Image.open(frame_path).convert("RGB").resize(
                (thumb_width, thumb_height),
                Image.Resampling.LANCZOS,
            )
            x = padding + (index % columns) * (thumb_width + padding)
            y = padding + (index // columns) * (thumb_height + label_height + padding)
            canvas.paste(thumbnail, (x, y + label_height))
            draw.text((x, y), f"{timestamp:04.1f}s  {frame_path.name}", fill=(20, 20, 20))
        canvas.save(CADENCE_SHEETS_DIR / f"contact-sheet-{sheet_index + 1:02d}.png")


def disk(radius: float, color: str, opacity: float = 1.0) -> Circle:
    return Circle(radius=radius, stroke_width=0, fill_color=color, fill_opacity=opacity)


def bar(width: float, height: float, color: str, opacity: float) -> Rectangle:
    return Rectangle(width=width, height=height, stroke_width=0, fill_color=color, fill_opacity=opacity)


def hollow_disk(radius: float, color: str, opacity: float = 1.0) -> Circle:
    circle = Circle(radius=radius, stroke_color=color, stroke_width=3, fill_opacity=0)
    circle.set_stroke(color=color, width=3, opacity=opacity)
    circle.set_fill(opacity=0)
    return circle


class QualityEdgeTensionScene(Scene):
    def construct(self) -> None:
        self.camera.background_opacity = 0.0

        tension_line = bar(8.05, 0.045, GRAY_200, 0.46).move_to(LEFT * 0.925 + UP * 0.02)
        left_anchor = bar(0.085, 1.44, GRAY_300, 0.48).move_to(LEFT * 5.06)
        pressure_wall = bar(0.09, 3.16, GRAY_500, 0.44).move_to(RIGHT * 5.55)
        upper_review_rail = Line(LEFT * 5.92 + UP * 2.82, RIGHT * 5.92 + UP * 2.82, color=GRAY_200, stroke_width=2).set_opacity(0.4)
        lower_review_rail = Line(LEFT * 5.92 + DOWN * 2.82, RIGHT * 5.92 + DOWN * 2.82, color=GRAY_200, stroke_width=2).set_opacity(0.4)

        source_slot = VGroup(
            hollow_disk(0.44, GRAY_300, 0.36).move_to(LEFT * 4.25 + UP * 0.02),
            hollow_disk(0.25, GRAY_300, 0.28).move_to(LEFT * 3.58 + UP * 0.62),
            hollow_disk(0.2, GRAY_300, 0.28).move_to(LEFT * 3.78 + DOWN * 0.6),
        )
        target_slots = VGroup(
            hollow_disk(0.62, GRAY_300, 0.32).move_to(RIGHT * 4.42 + UP * 0.36),
            hollow_disk(0.31, GRAY_300, 0.26).move_to(RIGHT * 3.72 + DOWN * 0.42),
            hollow_disk(0.22, GRAY_300, 0.24).move_to(RIGHT * 4.36 + DOWN * 0.94),
        )

        leader = disk(0.42, PRIMARY_RED).move_to(source_slot[0])
        upper_support = disk(0.24, GRAY_300, 0.9).move_to(source_slot[1])
        lower_support = disk(0.19, GRAY_300, 0.9).move_to(source_slot[2])

        queue_state = VGroup(
            disk(0.42, PRIMARY_RED).move_to(LEFT * 0.26 + UP * 0.18),
            disk(0.24, GRAY_300, 0.9).move_to(LEFT * 0.74 + UP * 0.72),
            disk(0.19, GRAY_300, 0.9).move_to(LEFT * 0.62 + DOWN * 0.48),
        )
        pressure_state = VGroup(
            disk(0.42, PRIMARY_RED).stretch_to_fit_width(1.34).stretch_to_fit_height(0.54).move_to(RIGHT * 4.57 + UP * 0.18),
            disk(0.24, GRAY_300, 0.9).move_to(RIGHT * 3.82 + UP * 0.78),
            disk(0.19, GRAY_300, 0.9).move_to(RIGHT * 3.66 + DOWN * 0.54),
        )
        final_state = VGroup(
            disk(0.62, PRIMARY_RED).move_to(RIGHT * 4.42 + UP * 0.36),
            disk(0.31, GRAY_300, 0.9).move_to(RIGHT * 3.72 + DOWN * 0.42),
            disk(0.22, GRAY_300, 0.9).move_to(RIGHT * 4.36 + DOWN * 0.94),
        )
        stress_marks = VGroup(
            Line(RIGHT * 5.78 + UP * 1.08, RIGHT * 5.98 + UP * 1.08, color=PRIMARY_RED, stroke_width=5),
            Line(RIGHT * 5.76 + UP * 0.44, RIGHT * 6.06 + UP * 0.44, color=PRIMARY_RED, stroke_width=5),
            Line(RIGHT * 5.78 + DOWN * 0.2, RIGHT * 5.98 + DOWN * 0.2, color=PRIMARY_RED, stroke_width=5),
        ).set_opacity(0)

        self.add(
            upper_review_rail,
            lower_review_rail,
            tension_line,
            left_anchor,
            pressure_wall,
            source_slot,
            target_slots,
            leader,
            upper_support,
            lower_support,
            stress_marks,
        )
        self.wait(2.8)

        active_thread = Line(LEFT * 4.42 + UP * 0.02, LEFT * 0.72 + UP * 0.02, color=PRIMARY_RED, stroke_width=5).set_opacity(0.0)
        self.play(FadeIn(active_thread), pressure_wall.animate.set_opacity(0.58), run_time=1.1, rate_func=smooth)
        self.play(
            AnimationGroup(
                Transform(leader, queue_state[0].copy()),
                Transform(upper_support, queue_state[1].copy()),
                Transform(lower_support, queue_state[2].copy()),
                lag_ratio=0.08,
            ),
            active_thread.animate.put_start_and_end_on(LEFT * 4.42 + UP * 0.02, RIGHT * 0.46 + UP * 0.02),
            run_time=2.5,
            rate_func=smooth,
        )
        self.wait(1.25)

        self.play(
            AnimationGroup(
                Transform(leader, pressure_state[0].copy()),
                Transform(upper_support, pressure_state[1].copy()),
                Transform(lower_support, pressure_state[2].copy()),
                lag_ratio=0.08,
            ),
            active_thread.animate.put_start_and_end_on(LEFT * 4.42 + UP * 0.02, RIGHT * 4.0 + UP * 0.02),
            pressure_wall.animate.set_opacity(0.72),
            stress_marks.animate.set_opacity(1),
            run_time=3.0,
            rate_func=smooth,
        )
        self.wait(2.5)

        self.play(
            AnimationGroup(
                Transform(leader, final_state[0].copy()),
                Transform(upper_support, final_state[1].copy()),
                Transform(lower_support, final_state[2].copy()),
                lag_ratio=0.06,
            ),
            FadeOut(source_slot),
            FadeOut(target_slots),
            active_thread.animate.set_opacity(0.0),
            stress_marks.animate.set_opacity(0.0),
            pressure_wall.animate.set_opacity(0.34),
            run_time=2.1,
            rate_func=smooth,
        )
        self.wait(1.0)

        self.play(
            upper_review_rail.animate.set_opacity(0.16),
            lower_review_rail.animate.set_opacity(0.16),
            left_anchor.animate.set_opacity(0.28),
            tension_line.animate.set_opacity(0.3),
            run_time=1.0,
            rate_func=smooth,
        )
        self.play(leader.animate.scale(1.06), pressure_wall.animate.set_opacity(0.46), run_time=0.35, rate_func=there_and_back)
        self.wait(8.1)


def render_variant(args: _Args) -> None:
    video_path, poster_path = output_paths()
    if STAGING_DIR.exists():
        shutil.rmtree(STAGING_DIR)

    result = subprocess.run(render_command(args, video_path.stem, poster=False), check=False)
    if result.returncode != 0:
        raise SystemExit(result.returncode)
    promote(video_path.name, video_path)
    build_cadence_review(video_path)

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
