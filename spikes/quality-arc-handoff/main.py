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
    ArcBetweenPoints,
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
    MoveAlongPath,
    RoundedRectangle,
    Scene,
    Transform,
    VGroup,
    WHITE,
    config,
    rate_functions,
    smooth,
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
PRIMARY_ORANGE = "#e77204"
PRIMARY_YELLOW = "#f1c319"
PRIMARY_GREEN = "#45842a"
PRIMARY_BLUE = "#007298"
PRIMARY_PURPLE = "#652f6c"
GRAY_100 = "#e7e7e7"
GRAY_200 = "#cfcfcf"
GRAY_300 = "#b5b5b5"
GRAY_500 = "#828282"

config.transparent = True
config.background_opacity = 0.0


class _Args(argparse.Namespace):
    quality: str


def parse_args() -> _Args:
    parser = argparse.ArgumentParser(description="Render the quality-arc-handoff spike.")
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
        "QualityArcHandoffScene",
    ]
    if poster:
        command.insert(-2, "-s")
    return command


def promote(target_name: str, destination: Path) -> None:
    matches = sorted(STAGING_DIR.glob(f"**/{target_name}"), key=lambda path: path.stat().st_mtime)
    if not matches:
        raise FileNotFoundError(target_name)
    destination.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(matches[-1], destination)


def build_cadence_review(video_path: Path) -> None:
    import imageio_ffmpeg
    from PIL import Image

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
    alpha_min = 255
    alpha_max = 0
    for raw_frame in sorted(CADENCE_RAW_DIR.glob("frame-*.png")):
        image = Image.open(raw_frame).convert("RGBA")
        frame_alpha_min, frame_alpha_max = image.getchannel("A").getextrema()
        alpha_min = min(alpha_min, frame_alpha_min)
        alpha_max = max(alpha_max, frame_alpha_max)
        background = Image.new("RGBA", image.size, "white")
        output = Image.alpha_composite(background, image).convert("RGB")
        frame_path = CADENCE_FRAMES_DIR / raw_frame.name
        output.save(frame_path)
        saved.append(frame_path)

    build_cadence_contact_sheets(saved)
    print(
        f"Wrote {len(saved)} cadence review frames to {CADENCE_FRAMES_DIR} "
        f"(alpha {alpha_min}..{alpha_max})"
    )


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


def slab(color: str, width: float, height: float) -> RoundedRectangle:
    return RoundedRectangle(width=width, height=height, corner_radius=0, stroke_width=0, fill_color=color, fill_opacity=1)


def bracket_slot(width: float, height: float, arm: float = 0.22, stroke_width: float = 2) -> VGroup:
    x = width / 2
    y = height / 2
    arm = min(arm, width * 0.28, height * 0.28)
    corners = VGroup(
        Line(LEFT * x + UP * y, LEFT * (x - arm) + UP * y),
        Line(LEFT * x + UP * y, LEFT * x + UP * (y - arm)),
        Line(RIGHT * x + UP * y, RIGHT * (x - arm) + UP * y),
        Line(RIGHT * x + UP * y, RIGHT * x + UP * (y - arm)),
        Line(LEFT * x + DOWN * y, LEFT * (x - arm) + DOWN * y),
        Line(LEFT * x + DOWN * y, LEFT * x + DOWN * (y - arm)),
        Line(RIGHT * x + DOWN * y, RIGHT * (x - arm) + DOWN * y),
        Line(RIGHT * x + DOWN * y, RIGHT * x + DOWN * (y - arm)),
    )
    corners.set_stroke(GRAY_200, width=stroke_width, opacity=0.46)
    return corners


class QualityArcHandoffScene(Scene):
    def construct(self) -> None:
        self.camera.background_color = WHITE
        self.camera.background_opacity = 0.0

        source_slot = bracket_slot(2.95, 2.72, arm=0.28, stroke_width=2.3).move_to(LEFT * 3.82 + UP * 0.02)
        source_slot.set_stroke(GRAY_200, opacity=0.56)

        source = VGroup(
            slab(PRIMARY_RED, 2.12, 0.64).move_to(LEFT * 3.95 + UP * 0.9),
            slab(GRAY_500, 1.56, 0.5).move_to(LEFT * 3.7 + DOWN * 0.08),
            slab(GRAY_300, 1.02, 0.38).move_to(LEFT * 4.06 + DOWN * 0.88),
        )

        target_slots = VGroup(
            bracket_slot(2.05, 2.05, arm=0.25, stroke_width=2.4).move_to(RIGHT * 2.65 + UP * 0.72),
            bracket_slot(1.28, 1.28, arm=0.18, stroke_width=2.2).move_to(RIGHT * 3.82 + DOWN * 0.24),
            bracket_slot(0.76, 0.76, arm=0.12, stroke_width=2.0).move_to(RIGHT * 2.52 + DOWN * 1.16),
        )
        target_slots.set_stroke(GRAY_200, opacity=0.72)

        leader_path = ArcBetweenPoints(
            start=source[0].get_center(),
            end=RIGHT * 2.65 + UP * 0.72,
            angle=-1.02,
        )
        support_path = ArcBetweenPoints(
            start=source[1].get_center(),
            end=RIGHT * 3.82 + DOWN * 0.24,
            angle=-0.42,
        )
        lower_path = ArcBetweenPoints(
            start=source[2].get_center(),
            end=RIGHT * 2.52 + DOWN * 1.16,
            angle=-0.34,
        )

        leader_rail = ArcBetweenPoints(
            start=leader_path.get_start() + DOWN * 0.35,
            end=leader_path.get_end() + DOWN * 0.35,
            angle=-1.02,
            color=GRAY_200,
            stroke_width=3.2,
        ).set_stroke(opacity=0.46)
        support_rail = ArcBetweenPoints(
            start=support_path.get_start() + DOWN * 0.18,
            end=support_path.get_end() + DOWN * 0.18,
            angle=-0.42,
            color=GRAY_200,
            stroke_width=2.4,
        ).set_stroke(opacity=0.3)
        lower_rail = ArcBetweenPoints(
            start=lower_path.get_start() + DOWN * 0.16,
            end=lower_path.get_end() + DOWN * 0.16,
            angle=-0.34,
            color=GRAY_200,
            stroke_width=2.0,
        ).set_stroke(opacity=0.26)
        guide_group = VGroup(leader_rail, support_rail, lower_rail)

        leader_landing = slab(PRIMARY_RED, 1.68, 0.58).move_to(RIGHT * 2.65 + UP * 0.72)
        support_landing = slab(GRAY_500, 1.1, 0.42).move_to(RIGHT * 3.82 + DOWN * 0.24)
        lower_landing = slab(GRAY_300, 0.76, 0.32).move_to(RIGHT * 2.52 + DOWN * 1.16)

        final_leader = Circle(radius=0.72, stroke_width=0, fill_color=PRIMARY_RED, fill_opacity=1).move_to(LEFT * 0.18 + UP * 0.48)
        final_support = Circle(radius=0.42, stroke_width=0, fill_color=GRAY_500, fill_opacity=1).move_to(RIGHT * 0.82 + DOWN * 0.28)
        final_lower = Circle(radius=0.22, stroke_width=0, fill_color=GRAY_300, fill_opacity=1).move_to(LEFT * 0.55 + DOWN * 0.68)

        self.add(source_slot, guide_group, target_slots, source)
        self.wait(2.6)

        leader_pulse = Circle(radius=0.18, stroke_width=0, fill_color=PRIMARY_RED, fill_opacity=0.92).move_to(
            leader_path.get_start()
        )
        self.play(FadeIn(leader_pulse), run_time=0.45)
        self.wait(0.55)

        self.play(
            MoveAlongPath(source[0], leader_path),
            MoveAlongPath(leader_pulse, leader_path),
            run_time=3.85,
            rate_func=smooth,
        )
        self.play(Transform(source[0], leader_landing.copy()), run_time=0.5)
        self.wait(1.25)

        self.play(
            MoveAlongPath(source[1], support_path),
            run_time=1.9,
            rate_func=smooth,
        )
        self.play(Transform(source[1], support_landing.copy()), run_time=0.35)
        self.wait(0.45)

        self.play(
            MoveAlongPath(source[2], lower_path),
            run_time=1.65,
            rate_func=smooth,
        )
        self.play(Transform(source[2], lower_landing.copy()), run_time=0.35)
        self.wait(1.05)

        self.play(
            AnimationGroup(
                Transform(source[0], final_leader.copy()),
                Transform(source[1], final_support.copy()),
                Transform(source[2], final_lower.copy()),
                target_slots.animate.set_opacity(0.34),
                source_slot.animate.set_opacity(0.34),
                guide_group.animate.set_opacity(0.16),
                FadeOut(leader_pulse),
                lag_ratio=0.04,
            ),
            run_time=3.6,
            rate_func=rate_functions.ease_in_out_cubic,
        )
        self.play(
            FadeOut(target_slots),
            FadeOut(source_slot),
            FadeOut(guide_group),
            run_time=0.55,
        )
        self.wait(0.8)

        terminal_ticks = VGroup(
            Line(LEFT * 1.28 + UP * 1.18, LEFT * 0.72 + UP * 1.18, color=PRIMARY_RED, stroke_width=3.6),
            Line(RIGHT * 1.36 + DOWN * 0.96, RIGHT * 0.9 + DOWN * 0.96, color=PRIMARY_RED, stroke_width=3.6),
            Line(LEFT * 1.18 + DOWN * 1.02, LEFT * 0.88 + DOWN * 0.74, color=PRIMARY_RED, stroke_width=3.2),
        ).set_stroke(opacity=0.58)
        self.play(Create(terminal_ticks), run_time=0.7)
        self.wait(6.2)


def render_variant(args: _Args) -> None:
    video_path, poster_path = output_paths()
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
