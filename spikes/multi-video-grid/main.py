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
import os
import shutil
import subprocess
import sys
from pathlib import Path

import imageio_ffmpeg
from PIL import Image, ImageDraw

from manim import (
    DOWN,
    LEFT,
    ORIGIN,
    RIGHT,
    UP,
    Circle,
    Create,
    Dot,
    FadeIn,
    FadeOut,
    GrowFromCenter,
    Line,
    MoveAlongPath,
    Rectangle,
    Scene,
    Transform,
    VGroup,
    config,
    linear,
    smooth,
    there_and_back,
)

config.transparent = True
config.background_opacity = 0.0

SPIKE_DIR = Path(__file__).resolve().parent
REPO_ROOT = SPIKE_DIR.parent.parent
SPIKE_NAME = SPIKE_DIR.name
OUTPUT_DIR = REPO_ROOT / "videos" / SPIKE_NAME
STAGING_DIR = OUTPUT_DIR / ".manim"
CADENCE_REVIEW_DIR = OUTPUT_DIR / "review-frames-0.3s"

PRIMARY_RED = "#9e1b32"
WHITE = "#ffffff"
GRAY = "#333e48"
GRAY_100 = "#e7e7e7"
GRAY_200 = "#cfcfcf"
GRAY_300 = "#b5b5b5"
GRAY_500 = "#828282"
PAGE_BACKGROUND = "#f7f7f7"

VARIANTS = {
    "orbit": {
        "scene": "MultiVideoGridOrbitScene",
        "resolution": "1600,900",
        "output": OUTPUT_DIR / "multi-video-grid-orbit.webm",
        "poster": OUTPUT_DIR / "multi-video-grid-orbit.png",
    },
    "pulse": {
        "scene": "MultiVideoGridPulseScene",
        "resolution": "1600,900",
        "output": OUTPUT_DIR / "multi-video-grid-pulse.webm",
        "poster": OUTPUT_DIR / "multi-video-grid-pulse.png",
    },
    "sweep": {
        "scene": "MultiVideoGridSweepScene",
        "resolution": "1600,900",
        "output": OUTPUT_DIR / "multi-video-grid-sweep.webm",
        "poster": OUTPUT_DIR / "multi-video-grid-sweep.png",
    },
    "merge": {
        "scene": "MultiVideoGridMergeScene",
        "resolution": "1600,900",
        "output": OUTPUT_DIR / "multi-video-grid-merge.webm",
        "poster": OUTPUT_DIR / "multi-video-grid-merge.png",
    },
}


class _Args(argparse.Namespace):
    quality: str
    preview: bool


def parse_args() -> _Args:
    parser = argparse.ArgumentParser(
        description="Render the multi-video-grid Manim spike."
    )
    parser.add_argument(
        "--quality",
        choices=("low", "medium", "high", "production", "4k"),
        default="medium",
        help="Manim quality preset. Defaults to medium for fast review.",
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


def render_command(args: _Args, variant_name: str, poster: bool) -> list[str]:
    STAGING_DIR.mkdir(parents=True, exist_ok=True)
    variant = VARIANTS[variant_name]

    command = [
        sys.executable,
        "-m",
        "manim",
        "render",
        quality_flag(args.quality),
        "-r",
        variant["resolution"],
        "--transparent",
        "-o",
        Path(variant["poster"] if poster else variant["output"]).stem,
        "--media_dir",
        str(STAGING_DIR),
    ]

    if poster:
        command.append("-s")
    else:
        command.extend(["--format", "webm", "-t"])
        if args.preview:
            command.append("-p")

    command.extend([str(Path(__file__).resolve()), variant["scene"]])
    return command


def promote_rendered_file(target_name: str, destination: Path) -> None:
    matches = sorted(
        STAGING_DIR.glob(f"**/{target_name}"),
        key=lambda path: path.stat().st_mtime,
    )
    if not matches:
        raise FileNotFoundError(f"Could not find {target_name} under {STAGING_DIR}")

    destination.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(matches[-1], destination)


def build_cadence_review(video_path: Path, variant_name: str) -> None:
    review_root = CADENCE_REVIEW_DIR / variant_name
    raw_dir = review_root / "raw-alpha"
    frames_dir = review_root / "frames"
    sheets_dir = review_root / "sheets"
    for path in (raw_dir, frames_dir, sheets_dir):
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
            str(raw_dir / "frame-%04d.png"),
        ],
        check=True,
    )

    saved: list[Path] = []
    for raw_frame in sorted(raw_dir.glob("frame-*.png")):
        image = Image.open(raw_frame).convert("RGBA")
        background = Image.new("RGBA", image.size, "white")
        background.alpha_composite(image)
        frame_path = frames_dir / raw_frame.name
        background.convert("RGB").save(frame_path)
        saved.append(frame_path)

    build_contact_sheets(saved, sheets_dir)
    print(f"Wrote {len(saved)} cadence review frames to {frames_dir}")


def build_contact_sheets(frames: list[Path], sheets_dir: Path) -> None:
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
        canvas.save(sheets_dir / f"contact-sheet-{sheet_index + 1:02d}.png")


def run_variant(args: _Args, variant_name: str) -> int:
    variant = VARIANTS[variant_name]
    print(f"Rendering {variant['scene']} into {variant['output']}")

    video_result = subprocess.run(
        render_command(args, variant_name, poster=False),
        check=False,
        env={**os.environ, "SPIKE_RENDER_TARGET": "video"},
    )
    if video_result.returncode != 0:
        return video_result.returncode
    promote_rendered_file(Path(variant["output"]).name, variant["output"])
    build_cadence_review(variant["output"], variant_name)

    poster_result = subprocess.run(
        render_command(args, variant_name, poster=True),
        check=False,
        env={**os.environ, "SPIKE_RENDER_TARGET": "poster"},
    )
    if poster_result.returncode != 0:
        return poster_result.returncode
    promote_rendered_file(Path(variant["poster"]).name, variant["poster"])

    return 0


def open_stage() -> VGroup:
    top = Line(LEFT * 5.25 + UP * 2.45, RIGHT * 5.25 + UP * 2.45, color=GRAY_200, stroke_width=3.0)
    bottom = Line(LEFT * 5.25 + DOWN * 2.45, RIGHT * 5.25 + DOWN * 2.45, color=GRAY_200, stroke_width=3.0)
    left = Line(LEFT * 5.25 + UP * 2.45, LEFT * 5.25 + UP * 1.72, color=GRAY_200, stroke_width=3.0)
    right = Line(RIGHT * 5.25 + DOWN * 1.72, RIGHT * 5.25 + DOWN * 2.45, color=GRAY_200, stroke_width=3.0)
    return VGroup(top, bottom, left, right).set_z_index(-2).set_opacity(0.8)


def dot(radius: float = 0.18, color: str = PRIMARY_RED) -> Dot:
    return Dot(radius=radius, color=color).set_z_index(8)


def square_slot(center, size: float = 0.72, opacity: float = 0.55) -> Rectangle:
    return Rectangle(
        width=size,
        height=size,
        stroke_color=GRAY_300,
        stroke_width=2.5,
        fill_opacity=0,
    ).move_to(center).set_opacity(opacity)


def corner_brackets(width: float, height: float, leg: float = 0.38, gap: float = 0.08) -> VGroup:
    left = -width / 2
    right = width / 2
    top = height / 2
    bottom = -height / 2
    segments = [
        Line([left, top, 0], [left + leg, top, 0]),
        Line([left, top, 0], [left, top - leg, 0]),
        Line([right, top, 0], [right - leg, top, 0]),
        Line([right, top, 0], [right, top - leg, 0]),
        Line([left, bottom, 0], [left + leg, bottom, 0]),
        Line([left, bottom, 0], [left, bottom + leg, 0]),
        Line([right, bottom, 0], [right - leg, bottom, 0]),
        Line([right, bottom, 0], [right, bottom + leg, 0]),
    ]
    for segment in segments:
        segment.set_stroke(PRIMARY_RED, width=4.0, opacity=0.92)
    group = VGroup(*segments)
    for segment in group[::2]:
        segment.shift(UP * gap if segment.get_center()[1] > 0 else DOWN * gap)
    for segment in group[1::2]:
        segment.shift(LEFT * gap if segment.get_center()[0] < 0 else RIGHT * gap)
    return group


class BaseMultiVideoGridScene(Scene):
    def construct(self) -> None:
        self.camera.background_opacity = 0.0
        if os.environ.get("SPIKE_RENDER_TARGET") == "poster":
            self.camera.background_color = PAGE_BACKGROUND
            self.camera.background_opacity = 1.0

        self.build_motion()

    def build_motion(self) -> None:
        raise NotImplementedError


class MultiVideoGridOrbitScene(BaseMultiVideoGridScene):
    def build_motion(self) -> None:
        stage = open_stage()
        orbit_path = Circle(radius=1.56, color=GRAY_300, stroke_width=4.2).shift(LEFT * 0.25)
        anchor = dot(0.075, GRAY).move_to(orbit_path.get_center())
        slots = VGroup(
            *[
                square_slot(orbit_path.point_from_proportion(t), size=0.46, opacity=0.42)
                for t in (0.0, 0.25, 0.5, 0.75)
            ]
        )
        traveler = dot(0.18).move_to(orbit_path.point_from_proportion(0.0))
        lead_ray = Line(traveler.get_center(), anchor.get_center(), color=GRAY_300, stroke_width=3.0)
        terminal = corner_brackets(3.95, 3.95).move_to(orbit_path.get_center()).set_opacity(0)

        self.add(stage, orbit_path, slots, anchor, lead_ray, traveler)
        self.wait(2.5)
        self.play(Create(orbit_path.copy().set_color(GRAY_500)), run_time=1.1)
        for target in (0.25, 0.5, 0.75):
            target_point = orbit_path.point_from_proportion(target)
            self.play(
                traveler.animate.move_to(target_point),
                lead_ray.animate.put_start_and_end_on(target_point, anchor.get_center()),
                run_time=3.1,
                rate_func=smooth,
            )
            self.play(slots[int(target * 4)].animate.set_stroke(PRIMARY_RED, width=3.5), run_time=0.5)
            self.wait(0.9)
            self.play(slots[int(target * 4)].animate.set_stroke(GRAY_300, width=2.5), run_time=0.45)
        self.play(
            MoveAlongPath(traveler, orbit_path),
            lead_ray.animate.set_opacity(0),
            run_time=3.8,
            rate_func=linear,
        )
        final_group = VGroup(traveler, anchor).copy()
        final_group.arrange(RIGHT, buff=0.72).move_to(ORIGIN)
        self.play(
            Transform(VGroup(traveler, anchor), final_group),
            FadeOut(slots),
            orbit_path.animate.set_stroke(GRAY_200, width=3.0, opacity=0.55),
            run_time=1.4,
        )
        terminal.set_opacity(1)
        self.play(FadeIn(terminal), FadeOut(stage), run_time=1.0)
        self.wait(6.1)


class MultiVideoGridPulseScene(BaseMultiVideoGridScene):
    def build_motion(self) -> None:
        stage = open_stage()
        core = dot(0.32)
        inner = Circle(radius=0.82, color=GRAY_300, stroke_width=4.0)
        outer = Circle(radius=1.46, color=GRAY_200, stroke_width=3.4)
        left_gate = Line(LEFT * 3.2, LEFT * 1.95, color=GRAY_300, stroke_width=6.0)
        right_gate = Line(RIGHT * 1.95, RIGHT * 3.2, color=GRAY_300, stroke_width=6.0)
        ticks = VGroup(
            *[
                Line(UP * 1.92 + RIGHT * x, UP * 1.52 + RIGHT * x, color=GRAY_200, stroke_width=2.5)
                for x in (-2.4, 0, 2.4)
            ]
        )
        terminal = corner_brackets(3.65, 3.65).set_opacity(0)

        self.add(stage, outer, inner, left_gate, right_gate, ticks, core)
        self.wait(2.5)
        for index, scale in enumerate((1.22, 1.42, 1.68)):
            ring = Circle(radius=0.62, color=PRIMARY_RED, stroke_width=5.0).move_to(core)
            ring.set_opacity(0.78)
            self.play(FadeIn(ring), core.animate.scale(1.16), run_time=0.65, rate_func=there_and_back)
            self.play(ring.animate.scale(scale).set_opacity(0.18), run_time=1.2, rate_func=smooth)
            self.play(
                FadeOut(ring),
                ticks[index].animate.set_stroke(PRIMARY_RED, width=4.0, opacity=0.9),
                run_time=0.55,
            )
            self.wait(1.0)
            self.play(ticks[index].animate.set_stroke(GRAY_200, width=2.5, opacity=0.85), run_time=0.35)
        self.play(
            inner.animate.scale(1.18).set_stroke(PRIMARY_RED, width=5.0),
            outer.animate.scale(0.93).set_stroke(GRAY_300, width=3.0),
            run_time=2.0,
            rate_func=smooth,
        )
        self.wait(1.3)
        self.play(
            FadeOut(left_gate),
            FadeOut(right_gate),
            FadeOut(ticks),
            outer.animate.set_opacity(0.35),
            inner.animate.set_stroke(GRAY_300, width=3.0),
            run_time=1.35,
        )
        terminal.set_opacity(1)
        self.play(FadeIn(terminal), FadeOut(stage), run_time=1.0)
        self.wait(6.0)


class MultiVideoGridSweepScene(BaseMultiVideoGridScene):
    def build_motion(self) -> None:
        stage = open_stage()
        track = Line(LEFT * 4.55, RIGHT * 4.55, color=GRAY_300, stroke_width=5.4)
        pending = VGroup(
            Line(LEFT * 4.55 + DOWN * 0.34, LEFT * 4.55 + UP * 0.34, color=GRAY_300, stroke_width=3),
            Line(DOWN * 0.34, UP * 0.34, color=GRAY_300, stroke_width=3),
            Line(RIGHT * 4.55 + DOWN * 0.34, RIGHT * 4.55 + UP * 0.34, color=GRAY_300, stroke_width=3),
        )
        marker = Rectangle(width=0.52, height=0.52, stroke_width=0, fill_color=PRIMARY_RED, fill_opacity=1).move_to(LEFT * 4.55)
        active_track = Line(LEFT * 4.55, LEFT * 4.55, color=PRIMARY_RED, stroke_width=5.4)
        terminal = corner_brackets(9.65, 1.9, leg=0.46).set_opacity(0)

        self.add(stage, track, pending, active_track, marker)
        self.wait(2.5)
        checkpoints = [(-2.25, 0), (0, 1), (2.25, 1), (4.55, 2)]
        for x, tick_index in checkpoints:
            self.play(
                marker.animate.move_to(RIGHT * x),
                active_track.animate.put_start_and_end_on(LEFT * 4.55, RIGHT * x),
                run_time=2.45,
                rate_func=smooth,
            )
            self.play(pending[tick_index].animate.set_stroke(PRIMARY_RED, width=4.2), run_time=0.42)
            self.wait(0.75)
            self.play(pending[tick_index].animate.set_stroke(GRAY_300, width=3.0), run_time=0.35)
        self.play(marker.animate.scale(1.18), run_time=0.6, rate_func=there_and_back)
        self.play(
            active_track.animate.set_opacity(0.18),
            track.animate.set_stroke(GRAY_200, width=4.0, opacity=0.65),
            pending.animate.set_opacity(0.35),
            run_time=1.3,
        )
        terminal.set_opacity(1)
        self.play(FadeIn(terminal), FadeOut(stage), run_time=1.0)
        self.wait(6.0)


class MultiVideoGridMergeScene(BaseMultiVideoGridScene):
    def build_motion(self) -> None:
        stage = open_stage()
        left_slot = square_slot(LEFT * 3.4, size=0.9, opacity=0.48)
        right_slot = square_slot(RIGHT * 3.4, size=0.9, opacity=0.48)
        receiver = VGroup(
            Line(LEFT * 0.7 + UP * 0.6, RIGHT * 0.7 + UP * 0.6, color=GRAY_300, stroke_width=4),
            Line(LEFT * 0.7 + DOWN * 0.6, RIGHT * 0.7 + DOWN * 0.6, color=GRAY_300, stroke_width=4),
        )
        left_route = Line(LEFT * 3.0, LEFT * 0.85, color=GRAY_300, stroke_width=4.2)
        right_route = Line(RIGHT * 3.0, RIGHT * 0.85, color=GRAY_300, stroke_width=4.2)
        left = dot(0.26).move_to(LEFT * 3.4)
        right = dot(0.26).move_to(RIGHT * 3.4)
        combined = Rectangle(
            width=1.45,
            height=1.02,
            stroke_color=PRIMARY_RED,
            stroke_width=4.0,
            fill_color=WHITE,
            fill_opacity=0.0,
        )
        terminal = corner_brackets(3.0, 2.28).set_opacity(0)

        self.add(stage, left_slot, right_slot, receiver, left_route, right_route, left, right)
        self.wait(2.5)
        self.play(left_slot.animate.set_stroke(PRIMARY_RED, width=3.5), run_time=0.45)
        self.play(left.animate.move_to(LEFT * 1.0), run_time=2.4, rate_func=smooth)
        self.wait(0.9)
        self.play(right_slot.animate.set_stroke(PRIMARY_RED, width=3.5), run_time=0.45)
        self.play(right.animate.move_to(RIGHT * 1.0), run_time=2.4, rate_func=smooth)
        self.wait(0.9)
        self.play(
            left.animate.move_to(LEFT * 0.28),
            right.animate.move_to(RIGHT * 0.28),
            receiver.animate.set_stroke(PRIMARY_RED, width=4.2),
            run_time=2.2,
            rate_func=smooth,
        )
        self.play(GrowFromCenter(combined), run_time=0.7)
        self.wait(1.2)
        self.play(
            Transform(VGroup(left, right), dot(0.34).move_to(ORIGIN)),
            FadeOut(left_slot),
            FadeOut(right_slot),
            FadeOut(left_route),
            FadeOut(right_route),
            receiver.animate.set_opacity(0.28),
            run_time=1.45,
        )
        terminal.set_opacity(1)
        self.play(FadeIn(terminal), FadeOut(stage), FadeOut(combined), run_time=1.0)
        self.wait(9.0)


def main() -> int:
    args = parse_args()
    for variant_name in VARIANTS:
        result = run_variant(args, variant_name)
        if result != 0:
            return result
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
