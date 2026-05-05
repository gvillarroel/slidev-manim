#!/usr/bin/env -S uv run --script
# /// script
# dependencies = [
#   "imageio-ffmpeg>=0.4.9",
#   "manim>=0.20.0",
#   "pillow>=10.0.0",
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
    Rectangle,
    Scene,
    Transform,
    VGroup,
    config,
    smooth,
)

SPIKE_DIR = Path(__file__).resolve().parent
REPO_ROOT = SPIKE_DIR.parent.parent
SPIKE_NAME = SPIKE_DIR.name
OUTPUT_DIR = REPO_ROOT / "videos" / SPIKE_NAME
STAGING_DIR = OUTPUT_DIR / ".manim"

PRIMARY_RED = "#9e1b32"
WHITE = "#ffffff"
GRAY_200 = "#cfcfcf"
GRAY_400 = "#9a9a9a"
GRAY_600 = "#666666"
GRAY_800 = "#333333"


class _Args(argparse.Namespace):
    quality: str


def parse_args() -> _Args:
    parser = argparse.ArgumentParser(description="Render the quality-bridge-span spike.")
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
        "QualityBridgeSpanScene",
    ]
    if poster:
        command.insert(-2, "-s")
    return command


def promote(target_name: str, destination: Path) -> None:
    matches = sorted(STAGING_DIR.glob(f"**/{target_name}"))
    if not matches:
        raise FileNotFoundError(target_name)
    destination.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(max(matches, key=lambda path: path.stat().st_mtime), destination)


def extract_review_frames(video_path: Path) -> tuple[int, tuple[int, int]]:
    from PIL import Image, ImageDraw
    import imageio_ffmpeg

    review_dir = OUTPUT_DIR / "review-frames-final-0p3"
    contact_sheet = OUTPUT_DIR / "contact-sheet-final-0p3.png"
    if review_dir.exists():
        shutil.rmtree(review_dir)
    review_dir.mkdir(parents=True, exist_ok=True)

    ffmpeg = imageio_ffmpeg.get_ffmpeg_exe()
    subprocess.run(
        [
            ffmpeg,
            "-hide_banner",
            "-loglevel",
            "error",
            "-c:v",
            "libvpx-vp9",
            "-i",
            str(video_path),
            "-filter_complex",
            "color=c=white:s=1600x900:r=10/3[bg];[0:v]fps=10/3,format=rgba[fg];[bg][fg]overlay=shortest=1,format=rgb24",
            "-vsync",
            "0",
            str(review_dir / "frame-%04d.png"),
        ],
        check=True,
    )

    frames = sorted(review_dir.glob("frame-*.png"))
    thumbs = []
    for index, frame in enumerate(frames):
        image = Image.open(frame).convert("RGB")
        image.thumbnail((240, 135), Image.Resampling.LANCZOS)
        thumb = Image.new("RGB", (240, 153), WHITE)
        thumb.paste(image, (0, 0))
        ImageDraw.Draw(thumb).text((6, 137), f"{index * 0.3:05.1f}s", fill=GRAY_800)
        thumbs.append(thumb)

    columns = 10
    rows = max(1, (len(thumbs) + columns - 1) // columns)
    sheet = Image.new("RGB", (columns * 240, rows * 153), WHITE)
    for index, thumb in enumerate(thumbs):
        sheet.paste(thumb, ((index % columns) * 240, (index // columns) * 153))
    sheet.save(contact_sheet)
    return len(frames), decoded_alpha_range(video_path)


def decoded_alpha_range(video_path: Path) -> tuple[int, int]:
    import imageio_ffmpeg

    ffmpeg = imageio_ffmpeg.get_ffmpeg_exe()
    result = subprocess.run(
        [
            ffmpeg,
            "-hide_banner",
            "-loglevel",
            "error",
            "-c:v",
            "libvpx-vp9",
            "-i",
            str(video_path),
            "-vf",
            "format=rgba",
            "-vframes",
            "3",
            "-f",
            "rawvideo",
            "-",
        ],
        check=True,
        capture_output=True,
    )
    alpha = result.stdout[3::4]
    return (min(alpha), max(alpha)) if alpha else (0, 0)


def slab(color: str, width: float, height: float) -> Rectangle:
    return Rectangle(width=width, height=height, stroke_width=0, fill_color=color, fill_opacity=1)


def short_slot(width: float, height: float, color: str = GRAY_200, opacity: float = 0.72) -> VGroup:
    top = Line(LEFT * width / 2 + UP * height / 2, RIGHT * width / 2 + UP * height / 2)
    bottom = Line(LEFT * width / 2 + DOWN * height / 2, RIGHT * width / 2 + DOWN * height / 2)
    left = Line(LEFT * width / 2 + UP * height * 0.24, LEFT * width / 2 + DOWN * height * 0.24)
    right = Line(RIGHT * width / 2 + UP * height * 0.24, RIGHT * width / 2 + DOWN * height * 0.24)
    slot = VGroup(top, bottom, left, right)
    slot.set_stroke(color=color, width=3, opacity=opacity)
    return slot


def terminal_mark() -> Rectangle:
    return Rectangle(width=1.05, height=0.085, stroke_width=0, fill_color=PRIMARY_RED, fill_opacity=1)


class QualityBridgeSpanScene(Scene):
    def construct(self) -> None:
        config.transparent = True
        config.background_opacity = 0.0
        self.camera.background_opacity = 0.0
        self.camera.background_color = WHITE

        source_zone = short_slot(3.95, 3.38, opacity=0.42).move_to(LEFT * 3.32 + DOWN * 0.04)
        target_zone = short_slot(3.58, 3.22, opacity=0.5).move_to(RIGHT * 3.08 + DOWN * 0.04)

        green = slab(GRAY_800, 2.24, 0.76).move_to(LEFT * 3.56 + UP * 0.72)
        blue = slab(GRAY_600, 1.5, 0.6).move_to(LEFT * 2.98 + DOWN * 0.12)
        purple = slab(GRAY_400, 0.9, 0.38).move_to(LEFT * 2.46 + DOWN * 0.88)
        source = VGroup(green, blue, purple)

        bridge_top = Rectangle(width=3.12, height=0.075, stroke_width=0, fill_color=GRAY_400, fill_opacity=0.7).move_to(RIGHT * 0.04 + UP * 0.42)
        bridge_bottom = Rectangle(width=3.12, height=0.075, stroke_width=0, fill_color=GRAY_400, fill_opacity=0.7).move_to(RIGHT * 0.04 + DOWN * 0.42)
        bridge_entry = Rectangle(width=0.09, height=0.54, stroke_width=0, fill_color=GRAY_400, fill_opacity=0.52).move_to(LEFT * 1.52)
        bridge_exit = Rectangle(width=0.09, height=0.54, stroke_width=0, fill_color=GRAY_400, fill_opacity=0.52).move_to(RIGHT * 1.62)
        bridge = VGroup(bridge_top, bridge_bottom, bridge_entry, bridge_exit)
        bridge.set_z_index(1)
        bridge.set_opacity(0.42)

        target_slot_green = short_slot(1.82, 0.94, opacity=0.58).move_to(RIGHT * 2.5 + UP * 0.56)
        target_slot_blue = short_slot(1.0, 0.72, opacity=0.54).move_to(RIGHT * 3.64 + DOWN * 0.26)
        target_slot_purple = short_slot(0.62, 0.48, opacity=0.5).move_to(RIGHT * 2.74 + DOWN * 1.08)
        target_slots = VGroup(target_slot_green, target_slot_blue, target_slot_purple)

        accent = Circle(radius=0.14, stroke_width=0, fill_color=PRIMARY_RED, fill_opacity=1).move_to(LEFT * 1.52 + UP * 1.04)
        accent.set_z_index(4)

        green_entry = slab(GRAY_800, 1.56, 0.38).move_to(LEFT * 0.86)
        green_bridge = slab(GRAY_800, 1.62, 0.34).move_to(RIGHT * 0.36)
        green_exit = slab(GRAY_800, 1.54, 0.52).move_to(RIGHT * 2.48 + UP * 0.44)
        blue_wait = slab(GRAY_600, 1.32, 0.54).move_to(LEFT * 2.9 + DOWN * 0.28)
        purple_wait = slab(GRAY_400, 0.82, 0.36).move_to(LEFT * 2.24 + DOWN * 1.06)
        blue_release = slab(GRAY_600, 1.02, 0.52).move_to(RIGHT * 1.32 + DOWN * 0.92)
        purple_release = slab(GRAY_400, 0.58, 0.34).move_to(RIGHT * 2.16 + DOWN * 1.32)

        final_green = Circle(radius=0.76, stroke_width=0, fill_color=GRAY_800, fill_opacity=1).move_to(RIGHT * 2.3 + UP * 0.64)
        final_blue = Circle(radius=0.4, stroke_width=0, fill_color=GRAY_600, fill_opacity=1).move_to(RIGHT * 3.42 + DOWN * 0.16)
        final_purple = Circle(radius=0.24, stroke_width=0, fill_color=GRAY_400, fill_opacity=1).move_to(RIGHT * 2.54 + DOWN * 1.06)
        centered_green = Circle(radius=0.76, stroke_width=0, fill_color=GRAY_800, fill_opacity=1).move_to(LEFT * 0.34 + UP * 0.58)
        centered_blue = Circle(radius=0.4, stroke_width=0, fill_color=GRAY_600, fill_opacity=1).move_to(RIGHT * 0.82 + DOWN * 0.12)
        centered_purple = Circle(radius=0.24, stroke_width=0, fill_color=GRAY_400, fill_opacity=1).move_to(LEFT * 0.02 + DOWN * 0.96)
        terminal = terminal_mark().move_to(RIGHT * 0.16 + DOWN * 1.55)

        for actor in source:
            actor.set_z_index(3)
        self.add(source_zone, target_zone, bridge, source, target_slots)
        self.wait(2.4)
        self.play(bridge.animate.set_opacity(0.86), FadeIn(accent), run_time=1.2)
        self.wait(0.8)
        self.play(accent.animate.move_to(LEFT * 0.86 + UP * 1.04), run_time=1.4, rate_func=smooth)
        self.play(Transform(green, green_entry.copy()), run_time=1.6, rate_func=smooth)
        self.wait(1.0)
        self.play(
            AnimationGroup(
                Transform(green, green_bridge.copy()),
                Transform(blue, blue_wait.copy()),
                Transform(purple, purple_wait.copy()),
                accent.animate.move_to(RIGHT * 0.36 + UP * 1.04),
                lag_ratio=0.08,
            ),
            run_time=2.4,
            rate_func=smooth,
        )
        self.wait(1.8)
        self.play(accent.animate.move_to(RIGHT * 1.62 + UP * 1.04), run_time=1.7, rate_func=smooth)
        self.play(Transform(green, green_exit.copy()), run_time=1.5, rate_func=smooth)
        self.wait(0.9)
        self.play(FadeOut(bridge), FadeOut(accent), FadeOut(target_slot_green), run_time=0.9)
        self.play(
            AnimationGroup(
                Transform(green, final_green.copy()),
                Transform(blue, blue_release.copy()),
                lag_ratio=0.18,
            ),
            run_time=1.6,
            rate_func=smooth,
        )
        self.play(Transform(purple, purple_release.copy()), run_time=1.0, rate_func=smooth)
        self.play(
            AnimationGroup(
                Transform(blue, final_blue.copy()),
                Transform(purple, final_purple.copy()),
                lag_ratio=0.16,
            ),
            run_time=1.1,
            rate_func=smooth,
        )
        self.play(
            AnimationGroup(
                Transform(green, centered_green.copy()),
                Transform(blue, centered_blue.copy()),
                Transform(purple, centered_purple.copy()),
                FadeOut(VGroup(target_slot_blue, target_slot_purple)),
                FadeOut(source_zone),
                FadeOut(target_zone),
                lag_ratio=0.05,
            ),
            run_time=2.2,
            rate_func=smooth,
        )
        self.play(FadeIn(terminal), run_time=0.6)
        self.wait(6.2)


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
    frame_count, alpha_range = extract_review_frames(video_path)
    print(f"review_frames={frame_count}")
    print(f"alpha_range={alpha_range[0]}..{alpha_range[1]}")


def main() -> int:
    args = parse_args()
    render_variant(args)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
