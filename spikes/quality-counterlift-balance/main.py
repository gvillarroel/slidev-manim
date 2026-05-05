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
    PI,
    RIGHT,
    UP,
    AnimationGroup,
    ArcBetweenPoints,
    FadeIn,
    FadeOut,
    Line,
    Polygon,
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
CADENCE_REVIEW_DIR = OUTPUT_DIR / "review-frames-0.3s"
CADENCE_RAW_DIR = CADENCE_REVIEW_DIR / "raw-alpha"
CADENCE_FRAMES_DIR = CADENCE_REVIEW_DIR / "frames"
CADENCE_SHEETS_DIR = CADENCE_REVIEW_DIR / "sheets"

PRIMARY_RED = "#9e1b32"
BLACK = "#000000"
GRAY = "#333e48"
GRAY_100 = "#e7e7e7"
GRAY_200 = "#cfcfcf"
GRAY_300 = "#b5b5b5"
GRAY_500 = "#828282"

config.transparent = True
config.background_opacity = 0.0


class _Args(argparse.Namespace):
    quality: str
    skip_review: bool


def parse_args() -> _Args:
    parser = argparse.ArgumentParser(description="Render the quality-counterlift-balance spike.")
    parser.add_argument("--quality", choices=("low", "medium", "high", "production", "4k"), default="medium")
    parser.add_argument("--skip-review", action="store_true", help="Skip 0.3s white-background review extraction.")
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
        "QualityCounterliftBalanceScene",
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


def slab(color: str, width: float, height: float, opacity: float = 1.0) -> Rectangle:
    return Rectangle(width=width, height=height, stroke_width=0, fill_color=color, fill_opacity=opacity)


def open_slot(center, width: float, height: float, opacity: float = 0.42) -> VGroup:
    left = Line(UP * height / 2, DOWN * height / 2, color=GRAY_300, stroke_width=3).move_to(center + LEFT * width / 2)
    right = Line(UP * height / 2, DOWN * height / 2, color=GRAY_300, stroke_width=3).move_to(center + RIGHT * width / 2)
    slot = VGroup(left, right).set_opacity(opacity)
    return slot


def pivot_mark() -> Polygon:
    return Polygon(
        LEFT * 0.42 + DOWN * 0.3,
        RIGHT * 0.42 + DOWN * 0.3,
        UP * 0.42,
        stroke_width=0,
        fill_color=GRAY_500,
        fill_opacity=1,
    )


def terminal_ticks() -> VGroup:
    left = Line(UP * 0.62, DOWN * 0.62, color=PRIMARY_RED, stroke_width=4).move_to(LEFT * 1.7 + UP * 0.14)
    right = Line(UP * 0.62, DOWN * 0.62, color=PRIMARY_RED, stroke_width=4).move_to(RIGHT * 2.65 + UP * 0.14)
    return VGroup(left, right).set_opacity(0.72)


class QualityCounterliftBalanceScene(Scene):
    def construct(self) -> None:
        self.camera.background_color = WHITE
        self.camera.background_opacity = 0.0

        source_shift = RIGHT * 0.78
        target_shift = LEFT * 1.25

        source_back = Rectangle(
            width=3.2,
            height=2.4,
            stroke_color=GRAY_200,
            stroke_width=2,
            fill_color=WHITE,
            fill_opacity=0,
        ).move_to((LEFT * 4.18 + UP * 0.08) + source_shift)
        source_back.set_stroke(opacity=0.45)

        leader = slab(PRIMARY_RED, 1.78, 0.56).move_to((LEFT * 4.46 + UP * 0.72) + source_shift)
        drop_support = slab(GRAY, 1.36, 0.46).move_to((LEFT * 3.92 + DOWN * 0.08) + source_shift)
        counter_support = slab(GRAY_500, 0.94, 0.36).move_to((LEFT * 3.55 + DOWN * 0.72) + source_shift)

        beam = Line((LEFT * 0.9 + DOWN * 0.34) + target_shift, (RIGHT * 4.2 + DOWN * 0.34) + target_shift, color=GRAY, stroke_width=7)
        beam.set_opacity(0.86)
        tilted_beam = Line((LEFT * 0.92 + UP * 0.48) + target_shift, (RIGHT * 4.22 + DOWN * 1.18) + target_shift, color=GRAY, stroke_width=7)
        tilted_beam.set_opacity(0.86)
        pivot = pivot_mark().move_to((RIGHT * 1.6 + DOWN * 0.68) + target_shift)
        pivot_tilt = pivot_mark().move_to((RIGHT * 1.6 + DOWN * 0.5) + target_shift).rotate(-PI / 18)

        rise_slot = open_slot((RIGHT * 0.16 + UP * 1.62) + target_shift, 2.6, 0.74)
        drop_slot = open_slot((RIGHT * 3.82 + DOWN * 1.52) + target_shift, 1.94, 0.62)
        counter_slot = open_slot((RIGHT * 2.5 + UP * 0.18) + target_shift, 1.5, 0.48)
        guide_slots = VGroup(rise_slot, drop_slot, counter_slot)

        leader_route = ArcBetweenPoints((LEFT * 3.56 + UP * 0.72) + source_shift, (RIGHT * 0.16 + UP * 1.0) + target_shift, angle=PI / 5)
        leader_route.set_stroke(GRAY_300, 3, opacity=0.38)
        drop_route = ArcBetweenPoints((LEFT * 3.48 + DOWN * 0.08) + source_shift, (RIGHT * 3.82 + DOWN * 0.76) + target_shift, angle=PI / 5)
        drop_route.set_stroke(GRAY_300, 3, opacity=0.34)
        counter_route = ArcBetweenPoints((LEFT * 3.18 + DOWN * 0.7) + source_shift, (RIGHT * 2.5 + UP * 0.08) + target_shift, angle=PI / 6)
        counter_route.set_stroke(GRAY_300, 3, opacity=0.3)
        routes = VGroup(leader_route, drop_route, counter_route)

        lift_stem = Line(UP * 0.34, DOWN * 0.34, color=PRIMARY_RED, stroke_width=5).move_to((LEFT * 0.98 + UP * 1.16) + target_shift)
        lift_stem.set_opacity(0.0)
        lift_stem_active = Line(UP * 0.5, DOWN * 0.5, color=PRIMARY_RED, stroke_width=5).move_to((LEFT * 0.98 + UP * 1.24) + target_shift)
        lift_stem_active.set_opacity(0.68)

        leader_ready = slab(PRIMARY_RED, 1.78, 0.56).move_to((RIGHT * 0.2 + UP * 0.96) + target_shift)
        drop_ready = slab(GRAY, 1.32, 0.46).move_to((RIGHT * 3.42 + DOWN * 0.62) + target_shift)
        counter_ready = slab(GRAY_500, 0.9, 0.36).move_to((RIGHT * 2.42 + UP * 0.1) + target_shift)

        leader_lift = slab(PRIMARY_RED, 1.78, 0.56).move_to((RIGHT * 0.16 + UP * 1.62) + target_shift)
        drop_lower = slab(GRAY, 1.32, 0.46).move_to((RIGHT * 3.82 + DOWN * 1.52) + target_shift)
        counter_hold = slab(GRAY_500, 0.9, 0.36).move_to((RIGHT * 2.5 + UP * 0.18) + target_shift)

        final_shift = LEFT * 1.0 + UP * 0.08
        leader_final = slab(PRIMARY_RED, 1.7, 0.54).move_to((RIGHT * 0.16 + UP * 1.42) + final_shift)
        drop_final = slab(GRAY, 1.24, 0.44).move_to((RIGHT * 3.58 + DOWN * 1.36) + final_shift)
        counter_final = slab(GRAY_500, 0.86, 0.34).move_to((RIGHT * 2.32 + UP * 0.26) + final_shift)
        beam_final = Line(LEFT * 0.74 + UP * 0.42, RIGHT * 3.78 + DOWN * 1.08, color=GRAY_500, stroke_width=5).shift(final_shift)
        beam_final.set_opacity(0.5)
        pivot_final = pivot_mark().scale(0.86).move_to((RIGHT * 1.46 + DOWN * 0.42) + final_shift)
        pivot_final.set_opacity(0.62)
        ticks = terminal_ticks()

        for guide in (source_back, guide_slots, routes, beam, pivot, lift_stem):
            guide.set_z_index(0)
        for support in (drop_support, counter_support):
            support.set_z_index(1)
        leader.set_z_index(2)

        self.add(source_back, routes, guide_slots, beam, pivot, lift_stem, leader, drop_support, counter_support)
        self.wait(2.6)
        self.play(
            AnimationGroup(
                Transform(leader, leader_ready.copy(), path_arc=PI / 3),
                Transform(drop_support, drop_ready.copy(), path_arc=PI / 4),
                Transform(counter_support, counter_ready.copy(), path_arc=PI / 5),
                lag_ratio=0.12,
            ),
            run_time=4.4,
            rate_func=smooth,
        )
        self.play(FadeOut(source_back), FadeOut(routes), run_time=0.8)
        self.wait(0.7)
        self.play(FadeIn(lift_stem_active), FadeOut(lift_stem), run_time=0.45)
        self.play(
            AnimationGroup(
                Transform(beam, tilted_beam.copy()),
                Transform(pivot, pivot_tilt.copy()),
                Transform(lift_stem_active, lift_stem_active.copy().shift(UP * 0.24)),
                Transform(leader, leader_lift.copy()),
                Transform(drop_support, drop_lower.copy()),
                Transform(counter_support, counter_hold.copy()),
                lag_ratio=0.03,
            ),
            run_time=3.6,
            rate_func=smooth,
        )
        self.wait(2.4)
        self.play(FadeOut(guide_slots), FadeOut(lift_stem_active), run_time=0.9)
        self.play(
            AnimationGroup(
                Transform(leader, leader_final.copy()),
                Transform(drop_support, drop_final.copy()),
                Transform(counter_support, counter_final.copy()),
                Transform(beam, beam_final.copy()),
                Transform(pivot, pivot_final.copy()),
                lag_ratio=0.04,
            ),
            run_time=2.2,
            rate_func=smooth,
        )
        self.play(FadeIn(ticks), run_time=0.9)
        self.wait(6.8)


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
        build_cadence_review(video_path)


def main() -> int:
    args = parse_args()
    render_variant(args)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
