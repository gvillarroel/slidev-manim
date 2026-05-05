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

import imageio_ffmpeg
from manim import (
    DOWN,
    LEFT,
    ORIGIN,
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
    WHITE,
    config,
    linear,
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
    parser = argparse.ArgumentParser(description="Render the quality-rhythm-gating spike.")
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
        "QualityRhythmGatingScene",
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


def gate_column(x: float) -> VGroup:
    upper = Rectangle(width=0.72, height=1.55, stroke_width=0, fill_color=GRAY_100, fill_opacity=0.92).move_to(
        RIGHT * x + UP * 1.05
    )
    lower = Rectangle(width=0.72, height=1.55, stroke_width=0, fill_color=GRAY_100, fill_opacity=0.92).move_to(
        RIGHT * x + DOWN * 1.05
    )
    left_rule = Line([x - 0.64, -2.0, 0], [x - 0.64, 2.0, 0], color=GRAY_200, stroke_width=2.2)
    right_rule = Line([x + 0.64, -2.0, 0], [x + 0.64, 2.0, 0], color=GRAY_200, stroke_width=2.2)
    return VGroup(upper, lower, left_rule, right_rule)


def source_slot() -> VGroup:
    return VGroup(
        Line([-5.58, -0.42, 0], [-5.58, 0.42, 0], color=GRAY_300, stroke_width=3.0),
        Line([-5.46, 0.55, 0], [-5.18, 0.55, 0], color=GRAY_200, stroke_width=2.2),
        Line([-5.46, -0.55, 0], [-5.18, -0.55, 0], color=GRAY_200, stroke_width=2.2),
        Line([-4.72, 0.55, 0], [-4.48, 0.55, 0], color=GRAY_200, stroke_width=2.2),
        Line([-4.72, -0.55, 0], [-4.48, -0.55, 0], color=GRAY_200, stroke_width=2.2),
    ).set_opacity(0.72)


def target_slot() -> VGroup:
    return VGroup(
        Line([5.35, -0.52, 0], [5.35, 0.52, 0], color=GRAY_300, stroke_width=3.0),
        Line([5.23, 0.66, 0], [4.98, 0.66, 0], color=GRAY_200, stroke_width=2.2),
        Line([5.23, -0.66, 0], [4.98, -0.66, 0], color=GRAY_200, stroke_width=2.2),
        Line([4.48, 0.66, 0], [4.22, 0.66, 0], color=GRAY_200, stroke_width=2.2),
        Line([4.48, -0.66, 0], [4.22, -0.66, 0], color=GRAY_200, stroke_width=2.2),
    ).set_opacity(0.72)


def terminal_brackets() -> VGroup:
    width = 3.82
    height = 2.74
    leg = 0.42
    gap = 0.08
    left = -width / 2
    right = width / 2
    top = height / 2
    bottom = -height / 2
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


class QualityRhythmGatingScene(Scene):
    def construct(self) -> None:
        self.camera.background_color = WHITE
        self.camera.background_opacity = 0.0

        rail = Line(LEFT * 5.55, RIGHT * 5.55, color=GRAY_200, stroke_width=4).set_opacity(0.42)
        upper_review_rail = Line([-4.4, 2.56, 0], [4.4, 2.56, 0], color=GRAY_200, stroke_width=2).set_opacity(0.42)
        lower_review_rail = Line([-4.4, -2.56, 0], [4.4, -2.56, 0], color=GRAY_200, stroke_width=2).set_opacity(0.42)
        gates = VGroup(gate_column(-2.7), gate_column(0.0), gate_column(2.7))
        source = source_slot()
        target = target_slot()
        beat_slots = VGroup(
            *[
                Rectangle(width=0.58, height=0.18, stroke_color=GRAY_300, stroke_width=1.8, fill_opacity=0).move_to(
                    RIGHT * x + DOWN * 2.38
                )
                for x in (-2.7, 0.0, 2.7)
            ]
        ).set_opacity(0.68)
        actor = Circle(radius=0.24, stroke_width=0, fill_color=PRIMARY_RED, fill_opacity=1).move_to(LEFT * 5.05)

        self.add(upper_review_rail, lower_review_rail, rail, source, target, gates, beat_slots, actor)
        self.wait(2.7)

        positions = [-5.05, -2.7, 0.0, 2.7, 4.75]
        beat_marks: list[Rectangle] = []
        for index, gate in enumerate(gates):
            entrance = RIGHT * (positions[index + 1] - 0.68)
            center = RIGHT * positions[index + 1]
            exit_point = RIGHT * (positions[index + 1] + 0.68)

            self.play(actor.animate.move_to(entrance), run_time=1.35, rate_func=smooth)
            self.play(
                gate[0].animate.shift(UP * 0.34),
                gate[1].animate.shift(DOWN * 0.34),
                gate[2].animate.set_color(PRIMARY_RED).set_stroke(width=3.2, opacity=0.72),
                gate[3].animate.set_color(PRIMARY_RED).set_stroke(width=3.2, opacity=0.72),
                actor.animate.scale(1.08),
                run_time=0.8,
                rate_func=smooth,
            )
            self.wait(0.55)
            self.play(actor.animate.move_to(exit_point), run_time=1.15, rate_func=linear)
            beat_mark = Rectangle(width=0.52, height=0.13, stroke_width=0, fill_color=PRIMARY_RED, fill_opacity=1).move_to(
                RIGHT * positions[index + 1] + DOWN * 2.38
            )
            beat_marks.append(beat_mark)
            self.play(
                FadeIn(beat_mark),
                gate[0].animate.shift(DOWN * 0.34),
                gate[1].animate.shift(UP * 0.34),
                gate[2].animate.set_color(GRAY_200).set_stroke(width=2.2, opacity=0.72),
                gate[3].animate.set_color(GRAY_200).set_stroke(width=2.2, opacity=0.72),
                actor.animate.scale(1 / 1.08),
                run_time=0.75,
                rate_func=smooth,
            )
            self.play(beat_mark.animate.set_fill(GRAY_500, opacity=0.72), run_time=0.35)
            self.wait(0.42)

        self.play(actor.animate.move_to(RIGHT * 4.75), target.animate.set_opacity(0.72), run_time=1.25, rate_func=smooth)
        self.wait(0.75)

        beat_mark_group = VGroup(*beat_marks)
        compact_marks = VGroup(
            Rectangle(width=0.64, height=0.14, stroke_width=0, fill_color=GRAY_500, fill_opacity=0.74).move_to(
                LEFT * 0.82 + DOWN * 1.05
            ),
            Rectangle(width=0.64, height=0.14, stroke_width=0, fill_color=GRAY_500, fill_opacity=0.74).move_to(
                DOWN * 1.05
            ),
            Rectangle(width=0.64, height=0.14, stroke_width=0, fill_color=GRAY_500, fill_opacity=0.74).move_to(
                RIGHT * 0.82 + DOWN * 1.05
            ),
        )
        terminal_core = Circle(radius=0.58, stroke_width=0, fill_color=PRIMARY_RED, fill_opacity=1).move_to(UP * 0.18)
        terminal_echoes = VGroup(
            Line([-1.52, 0.18, 0], [-1.04, 0.18, 0], color=GRAY_300, stroke_width=3.0),
            Line([1.04, 0.18, 0], [1.52, 0.18, 0], color=GRAY_300, stroke_width=3.0),
            Line([-0.48, 1.3, 0], [0.48, 1.3, 0], color=GRAY_200, stroke_width=2.2),
        ).set_stroke(opacity=0.68)
        brackets = terminal_brackets().move_to(ORIGIN)

        self.remove(actor)
        self.play(
            FadeIn(terminal_core),
            Transform(beat_mark_group, compact_marks),
            gates.animate.set_opacity(0.0),
            source.animate.set_opacity(0.0),
            target.animate.set_opacity(0.0),
            beat_slots.animate.set_opacity(0.0),
            upper_review_rail.animate.set_opacity(0.18),
            lower_review_rail.animate.set_opacity(0.18),
            rail.animate.scale(0.38).move_to(DOWN * 1.05).set_opacity(0.16),
            run_time=1.05,
            rate_func=smooth,
        )
        self.play(
            FadeOut(source),
            FadeOut(target),
            FadeOut(gates),
            FadeOut(beat_slots),
            FadeOut(upper_review_rail),
            FadeOut(lower_review_rail),
            FadeOut(rail),
            run_time=0.72,
            rate_func=smooth,
        )
        self.play(FadeIn(terminal_echoes), FadeIn(brackets), run_time=0.75, rate_func=smooth)
        self.wait(0.35)
        self.play(terminal_core.animate.scale(1.08), run_time=0.32, rate_func=there_and_back)
        self.wait(6.4)


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
