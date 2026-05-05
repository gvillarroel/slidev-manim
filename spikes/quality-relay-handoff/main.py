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
    ORIGIN,
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
GRAY_300 = "#a9a9a9"
GRAY_500 = "#828282"

config.transparent = True
config.background_opacity = 0.0


class _Args(argparse.Namespace):
    quality: str
    skip_review: bool


def parse_args() -> _Args:
    parser = argparse.ArgumentParser(description="Render the quality-relay-handoff spike.")
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
        "--transparent",
        "--format",
        "webm",
        "-o",
        stem,
        "--media_dir",
        str(STAGING_DIR),
        str(Path(__file__).resolve()),
        "QualityRelayHandoffScene",
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

    thumb_width = 320
    thumb_height = 180
    columns = 4
    rows = 5
    padding = 14
    label_height = 26
    frames_per_sheet = columns * rows
    sheet_count = math.ceil(len(saved) / frames_per_sheet)
    for sheet_index in range(sheet_count):
        chunk = saved[sheet_index * frames_per_sheet : (sheet_index + 1) * frames_per_sheet]
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

    print(
        f"Wrote {len(saved)} cadence review frames to {CADENCE_FRAMES_DIR} "
        f"(alpha {alpha_min}..{alpha_max})"
    )


def slab(color: str, width: float, height: float, opacity: float = 1) -> Rectangle:
    return Rectangle(width=width, height=height, stroke_width=0, fill_color=color, fill_opacity=opacity)


def bracket_slot(width: float, height: float, opacity: float = 0.58, color: str = GRAY_300) -> VGroup:
    corner = 0.34
    half_w = width / 2
    half_h = height / 2
    segments = VGroup(
        Line(LEFT * half_w + UP * half_h, LEFT * (half_w - corner) + UP * half_h),
        Line(LEFT * half_w + UP * half_h, LEFT * half_w + UP * (half_h - corner)),
        Line(RIGHT * half_w + UP * half_h, RIGHT * (half_w - corner) + UP * half_h),
        Line(RIGHT * half_w + UP * half_h, RIGHT * half_w + UP * (half_h - corner)),
        Line(LEFT * half_w + DOWN * half_h, LEFT * (half_w - corner) + DOWN * half_h),
        Line(LEFT * half_w + DOWN * half_h, LEFT * half_w + DOWN * (half_h - corner)),
        Line(RIGHT * half_w + DOWN * half_h, RIGHT * (half_w - corner) + DOWN * half_h),
        Line(RIGHT * half_w + DOWN * half_h, RIGHT * half_w + DOWN * (half_h - corner)),
    )
    segments.set_color(color).set_stroke(width=3, opacity=opacity)
    return segments


def terminal_brackets() -> VGroup:
    width = 3.95
    height = 2.72
    leg = 0.42
    gap = 0.1
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
    ).set_stroke(opacity=0.62)


class QualityRelayHandoffScene(Scene):
    def construct(self) -> None:
        self.camera.background_color = WHITE
        self.camera.background_opacity = 0.0

        leader = slab(PRIMARY_RED, 1.85, 0.72).move_to(LEFT * 4.15 + UP * 0.72)
        support_one = slab(GRAY_500, 1.18, 0.42, 0.96).move_to(LEFT * 4.22 + DOWN * 0.35)
        support_two = slab(GRAY_300, 0.92, 0.34, 0.95).move_to(LEFT * 3.65 + DOWN * 1.18)
        source = VGroup(leader, support_one, support_two)

        relay_one_target = slab(GRAY_500, 1.18, 0.42, 0.96).move_to(LEFT * 1.52 + DOWN * 0.35)
        relay_two_target = slab(GRAY_300, 0.92, 0.34, 0.95).move_to(RIGHT * 1.22 + UP * 0.86)
        leader_hold = slab(PRIMARY_RED, 1.62, 0.66).move_to(RIGHT * 2.82 + DOWN * 0.35)

        pad_one = bracket_slot(1.86, 0.94).move_to(relay_one_target)
        pad_two = bracket_slot(1.54, 0.86).move_to(relay_two_target)
        leader_pad = bracket_slot(2.02, 1.02, opacity=0.5).move_to(leader_hold)
        pads = VGroup(pad_one, pad_two, leader_pad)

        guide_one = Line(support_one.get_right() + RIGHT * 0.16, pad_one.get_left() + LEFT * 0.16, color=GRAY_300, stroke_width=3)
        guide_two = Line(pad_one.get_right() + RIGHT * 0.18, pad_two.get_left() + LEFT * 0.18, color=GRAY_300, stroke_width=3)
        gate_top = leader_pad.get_left() + LEFT * 0.32 + UP * 0.52
        gate_bottom = leader_pad.get_left() + LEFT * 0.32 + DOWN * 0.52
        guide_three = Line(gate_top, gate_bottom, color=GRAY_300, stroke_width=3)
        guides = VGroup(guide_one, guide_two, guide_three).set_opacity(0.36)

        relay_one = Line(support_one.get_right() + RIGHT * 0.18, pad_one.get_left() + LEFT * 0.18, color=PRIMARY_RED, stroke_width=5)
        relay_two = Line(pad_one.get_right() + RIGHT * 0.2, pad_two.get_left() + LEFT * 0.2, color=PRIMARY_RED, stroke_width=5)
        relay_three = Line(gate_top, gate_bottom, color=PRIMARY_RED, stroke_width=5)
        baton = Circle(radius=0.16, stroke_width=0, fill_color=PRIMARY_RED, fill_opacity=1).move_to(relay_one.get_start())
        baton.set_z_index(5)

        final_leader = slab(PRIMARY_RED, 1.78, 0.74).move_to(LEFT * 0.12 + UP * 0.2)
        final_support_one = slab(GRAY_500, 1.18, 0.36, 0.95).move_to(LEFT * 0.16 + DOWN * 0.92)
        final_support_two = slab(GRAY_300, 0.92, 0.32, 0.95).move_to(RIGHT * 1.34 + UP * 0.88)
        final_stem = Line(final_support_one.get_top() + UP * 0.1, final_leader.get_bottom() + DOWN * 0.08, color=GRAY_300, stroke_width=3)
        final_stem.set_opacity(0.58)
        brackets = terminal_brackets().move_to(ORIGIN)

        for mobject in (guides, pads):
            mobject.set_z_index(0)
        source.set_z_index(2)

        self.add(pads, guides, source)
        self.wait(2.6)

        self.play(FadeIn(baton), Create(relay_one), run_time=0.9)
        self.play(
            AnimationGroup(
                Transform(support_one, relay_one_target.copy()),
                baton.animate.move_to(pad_one.get_center()),
                lag_ratio=0.05,
            ),
            run_time=1.35,
            rate_func=smooth,
        )
        self.wait(1.45)

        self.play(Create(relay_two), run_time=0.7)
        self.play(
            AnimationGroup(
                Transform(support_two, relay_two_target.copy()),
                baton.animate.move_to(pad_two.get_center()),
                lag_ratio=0.08,
            ),
            run_time=1.4,
            rate_func=smooth,
        )
        self.wait(1.55)

        self.play(FadeOut(relay_one), pad_one.animate.set_stroke(opacity=0.14), run_time=0.7)
        self.play(Create(relay_three), run_time=0.75)
        self.wait(0.35)
        self.play(
            FadeOut(relay_two),
            FadeOut(relay_three),
            FadeOut(baton),
            pad_two.animate.set_stroke(opacity=0.14),
            run_time=0.55,
        )
        self.play(
            AnimationGroup(
                Transform(leader, leader_hold.copy()),
                leader_pad.animate.set_stroke(opacity=0.3),
                lag_ratio=0.1,
            ),
            run_time=1.8,
            rate_func=smooth,
        )
        self.wait(1.65)

        self.play(
            FadeOut(guides),
            FadeOut(pads),
            run_time=1.0,
        )
        self.play(
            AnimationGroup(
                Transform(leader, final_leader.copy()),
                Transform(support_one, final_support_one.copy()),
                Transform(support_two, final_support_two.copy()),
                lag_ratio=0.08,
            ),
            run_time=2.0,
            rate_func=smooth,
        )
        self.play(FadeIn(final_stem), FadeIn(brackets), run_time=0.9, rate_func=smooth)
        self.play(brackets.animate.set_stroke(opacity=0.48), run_time=0.8)
        self.wait(6.1)


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
