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
    Create,
    FadeIn,
    FadeOut,
    Line,
    Rectangle,
    Scene,
    Transform,
    VGroup,
    WHITE,
    config,
    smooth,
    there_and_back,
)

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
GRAY_400 = "#9c9c9c"
GRAY_500 = "#828282"
GRAY_600 = "#696969"
GRAY_700 = "#4f4f4f"

config.transparent = True
config.background_opacity = 0.0


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


def build_cadence_review(video_path: Path) -> None:
    import imageio_ffmpeg
    from PIL import Image, ImageDraw

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
    from PIL import Image, ImageDraw

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
        self.camera.background_opacity = 0.0

        stage_rails = VGroup(
            Line(LEFT * 4.95 + UP * 2.32, RIGHT * 4.95 + UP * 2.32, color=GRAY_200, stroke_width=2),
            Line(LEFT * 4.95 + DOWN * 2.22, RIGHT * 4.95 + DOWN * 2.22, color=GRAY_200, stroke_width=2),
        ).set_stroke(opacity=0.46)

        mask_window = Rectangle(
            width=0.72,
            height=4.94,
            stroke_color=PRIMARY_RED,
            stroke_width=4,
            fill_color=PRIMARY_RED,
            fill_opacity=0.07,
        )
        mask_core = Rectangle(
            width=0.11,
            height=4.62,
            stroke_width=0,
            fill_color=PRIMARY_RED,
            fill_opacity=0.92,
        )
        mask = VGroup(mask_window, mask_core).move_to(LEFT * 4.18)

        exit_gate = VGroup(
            Line(RIGHT * 4.62 + UP * 2.0, RIGHT * 4.62 + UP * 0.62, color=GRAY_200, stroke_width=5),
            Line(RIGHT * 4.62 + DOWN * 0.62, RIGHT * 4.62 + DOWN * 2.0, color=GRAY_200, stroke_width=5),
        ).set_stroke(opacity=0.46)

        top_row = VGroup(
            chip(GRAY_600, 1.9, 0.74).move_to(LEFT * 3.42 + UP * 1.24),
            chip(GRAY_500, 1.72, 0.68).move_to(LEFT * 0.88 + UP * 1.24),
            chip(GRAY_500, 1.5, 0.62).move_to(RIGHT * 1.38 + UP * 1.24),
            chip(GRAY_600, 1.28, 0.56).move_to(RIGHT * 3.42 + UP * 1.24),
        )

        target_slots = VGroup(
            Circle(radius=0.62, stroke_width=2.4, stroke_color=GRAY_300, fill_opacity=0).move_to(LEFT * 3.16 + DOWN * 1.36),
            Circle(radius=0.54, stroke_width=2.4, stroke_color=GRAY_300, fill_opacity=0).move_to(LEFT * 0.82 + DOWN * 1.34),
            Circle(radius=0.46, stroke_width=2.4, stroke_color=GRAY_300, fill_opacity=0).move_to(RIGHT * 1.28 + DOWN * 1.32),
            Circle(radius=0.42, stroke_width=2.8, stroke_color=PRIMARY_RED, fill_opacity=0).move_to(RIGHT * 3.08 + DOWN * 1.28),
        ).set_stroke(opacity=0.34)

        bottom_row = VGroup(
            Circle(radius=0.54, stroke_width=0, fill_color=GRAY_500, fill_opacity=1).move_to(target_slots[0]),
            Circle(radius=0.46, stroke_width=0, fill_color=GRAY_600, fill_opacity=1).move_to(target_slots[1]),
            Circle(radius=0.38, stroke_width=0, fill_color=GRAY_500, fill_opacity=1).move_to(target_slots[2]),
            Circle(radius=0.34, stroke_width=0, fill_color=PRIMARY_RED, fill_opacity=1).move_to(target_slots[3]),
        )

        guide_lines = VGroup(*[
            Line(top_row[i].get_bottom(), bottom_row[i].get_top(), color=GRAY_200, stroke_width=2.4)
            for i in range(4)
        ]).set_opacity(0.26)

        transfer_lines = VGroup(*[
            Line(top_row[i].get_bottom(), bottom_row[i].get_top(), color=PRIMARY_RED, stroke_width=4.0)
            for i in range(4)
        ])

        self.add(stage_rails, guide_lines, exit_gate, top_row, target_slots, mask)
        self.wait(2.4)

        self.play(
            mask.animate.move_to(LEFT * 2.35),
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
        self.play(transfer_lines[0].animate.set_color(GRAY_300).set_opacity(0.28), run_time=0.45, rate_func=smooth)
        self.wait(0.35)

        self.play(
            mask.animate.move_to(RIGHT * 0.0),
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
            transfer_lines[1].animate.set_color(GRAY_300).set_opacity(0.28),
            transfer_lines[2].animate.set_color(GRAY_300).set_opacity(0.28),
            run_time=0.45,
            rate_func=smooth,
        )
        self.wait(0.35)

        self.play(
            mask.animate.move_to(RIGHT * 2.86),
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
        self.play(transfer_lines[3].animate.set_opacity(0.42), run_time=0.45, rate_func=smooth)
        self.wait(0.35)

        compact_targets = VGroup(
            Circle(radius=0.44, stroke_width=0, fill_color=GRAY_500, fill_opacity=1).move_to(LEFT * 0.72 + UP * 0.82),
            Circle(radius=0.36, stroke_width=0, fill_color=GRAY_600, fill_opacity=1).move_to(RIGHT * 1.04 + UP * 0.84),
            Circle(radius=0.32, stroke_width=0, fill_color=GRAY_500, fill_opacity=1).move_to(LEFT * 0.92 + DOWN * 0.78),
            Circle(radius=0.76, stroke_width=0, fill_color=PRIMARY_RED, fill_opacity=1).move_to(RIGHT * 0.34 + DOWN * 0.16),
        )
        compact_slots = VGroup(*[
            Circle(
                radius=target.radius + 0.22,
                stroke_width=2.2,
                stroke_color=GRAY_200,
                fill_opacity=0,
            ).move_to(target)
            for target in compact_targets
        ]).set_stroke(opacity=0.24)
        terminal_brackets = corner_brackets(compact_targets)

        self.play(
            FadeOut(top_row),
            FadeOut(transfer_lines),
            guide_lines.animate.set_opacity(0.0),
            target_slots.animate.set_stroke(opacity=0.0),
            stage_rails.animate.set_stroke(opacity=0.0),
            run_time=0.35,
            rate_func=smooth,
        )
        self.play(
            FadeIn(compact_slots),
            FadeOut(mask),
            FadeOut(exit_gate),
            run_time=0.9,
            rate_func=smooth,
        )
        self.play(
            AnimationGroup(*[Transform(bottom_row[i], compact_targets[i]) for i in range(4)], lag_ratio=0.07),
            FadeOut(stage_rails),
            FadeOut(compact_slots),
            run_time=1.2,
            rate_func=smooth,
        )
        self.play(FadeIn(terminal_brackets), run_time=0.65, rate_func=smooth)
        self.wait(0.45)

        self.play(bottom_row[3].animate.scale(1.08), run_time=0.38, rate_func=there_and_back)
        self.wait(0.25)
        self.play(bottom_row[3].animate.scale(1.06), run_time=0.32, rate_func=there_and_back)
        self.wait(5.8)


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
