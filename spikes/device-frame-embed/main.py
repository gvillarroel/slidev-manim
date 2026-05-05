#!/usr/bin/env -S uv run --script
# /// script
# dependencies = [
#   "imageio-ffmpeg>=0.6.0",
#   "manim>=0.19.0",
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

SPIKE_DIR = Path(__file__).resolve().parent
REPO_ROOT = SPIKE_DIR.parent.parent
SPIKE_NAME = SPIKE_DIR.name
OUTPUT_DIR = REPO_ROOT / "videos" / SPIKE_NAME
STAGING_DIR = OUTPUT_DIR / ".manim"
CADENCE_REVIEW_DIR = OUTPUT_DIR / "review-frames-0.3s"

PRIMARY_RED = "#9e1b32"
PRIMARY_ORANGE = "#e77204"
PRIMARY_YELLOW = "#f1c319"
PRIMARY_GREEN = "#45842a"
PRIMARY_BLUE = "#007298"
PRIMARY_PURPLE = "#652f6c"
WHITE = "#ffffff"
GRAY = "#333e48"
GRAY_100 = "#e7e7e7"
GRAY_200 = "#cfcfcf"
GRAY_300 = "#b5b5b5"
GRAY_400 = "#9c9c9c"
GRAY_600 = "#696969"
GRAY_700 = "#4f4f4f"
HIGHLIGHT_RED = "#ffccd5"
HIGHLIGHT_ORANGE = "#ffe5cc"
HIGHLIGHT_YELLOW = "#fff4cc"
HIGHLIGHT_GREEN = "#dbffcc"
HIGHLIGHT_BLUE = "#cdf3ff"
HIGHLIGHT_PURPLE = "#f9ccff"
SHADOW_BLUE = "#004d66"
PAGE_BACKGROUND = "#f7f7f7"

VARIANTS = {
    "browser": {
        "scene": "DeviceFrameEmbedBrowserScene",
        "resolution": "1920,1080",
        "video": OUTPUT_DIR / "device-frame-embed-browser.webm",
        "poster": OUTPUT_DIR / "device-frame-embed-browser.png",
    },
    "device": {
        "scene": "DeviceFrameEmbedDeviceScene",
        "resolution": "1080,1920",
        "video": OUTPUT_DIR / "device-frame-embed-device.webm",
        "poster": OUTPUT_DIR / "device-frame-embed-device.png",
    },
}


class _Args(argparse.Namespace):
    quality: str
    preview: bool


def parse_args() -> _Args:
    parser = argparse.ArgumentParser(description="Render the device-frame-embed Manim spike.")
    parser.add_argument(
        "--quality",
        choices=("low", "medium", "high", "production", "4k"),
        default="medium",
        help="Manim quality preset. Defaults to medium for review speed.",
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
    variant = VARIANTS[variant_name]
    command = [
        sys.executable,
        "-m",
        "manim",
        "render",
        quality_flag(args.quality),
        "-r",
        variant["resolution"],
        "--format",
        "webm",
        "--transparent",
        "-o",
        (variant["poster"] if poster else variant["video"]).stem,
        "--media_dir",
        str(STAGING_DIR),
    ]
    if not poster:
        command.append("-t")
    if poster:
        command.append("-s")
    elif args.preview:
        command.append("-p")
    command.extend([str(Path(__file__).resolve()), variant["scene"]])
    return command


def promote_rendered_file(target_name: str, destination: Path) -> None:
    matches = sorted(STAGING_DIR.glob(f"**/{target_name}"), key=lambda path: path.stat().st_mtime)
    if not matches:
        raise FileNotFoundError(f"Could not find {target_name} under {STAGING_DIR}")

    destination.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(matches[-1], destination)


def build_cadence_review(video_path: Path, variant_name: str, resolution: str) -> None:
    import imageio_ffmpeg
    from PIL import Image, ImageDraw

    width, height = [int(part) for part in resolution.split(",")]
    review_dir = CADENCE_REVIEW_DIR / variant_name
    raw_dir = review_dir / "raw-alpha"
    frames_dir = review_dir / "frames"
    sheets_dir = review_dir / "sheets"
    for directory in (raw_dir, frames_dir, sheets_dir):
        if directory.exists():
            shutil.rmtree(directory)
        directory.mkdir(parents=True, exist_ok=True)

    ffmpeg = Path(imageio_ffmpeg.get_ffmpeg_exe()).resolve()
    subprocess.run(
        [
            str(ffmpeg),
            "-y",
            "-hide_banner",
            "-loglevel",
            "error",
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

    alpha_min = 255
    alpha_max = 0
    saved: list[Path] = []
    for raw_frame in sorted(raw_dir.glob("frame-*.png")):
        image = Image.open(raw_frame).convert("RGBA")
        frame_alpha_min, frame_alpha_max = image.getchannel("A").getextrema()
        alpha_min = min(alpha_min, frame_alpha_min)
        alpha_max = max(alpha_max, frame_alpha_max)
        background = Image.new("RGBA", image.size, "white")
        output = Image.alpha_composite(background, image).convert("RGB")
        frame_path = frames_dir / raw_frame.name
        output.save(frame_path)
        saved.append(frame_path)

    thumb_width, thumb_height = (320, 180) if width > height else (180, 320)
    columns, rows = (4, 5) if width > height else (4, 4)
    padding = 14
    label_height = 26
    frames_per_sheet = columns * rows
    for sheet_index in range(math.ceil(len(saved) / frames_per_sheet)):
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
        canvas.save(sheets_dir / f"contact-sheet-{sheet_index + 1:02d}.png")

    print(
        f"Wrote {len(saved)} {variant_name} cadence review frames to {frames_dir} "
        f"(alpha {alpha_min}..{alpha_max})"
    )


def render_variant(args: _Args, variant_name: str) -> None:
    variant = VARIANTS[variant_name]

    if STAGING_DIR.exists():
        shutil.rmtree(STAGING_DIR)
    STAGING_DIR.mkdir(parents=True, exist_ok=True)
    video_env = os.environ.copy()
    video_env["SPIKE_RENDER_TARGET"] = "video"
    print(f"Rendering {variant['scene']} into {variant['video']}")
    video_result = subprocess.run(render_command(args, variant_name, poster=False), check=False, env=video_env)
    if video_result.returncode != 0:
        raise SystemExit(video_result.returncode)
    promote_rendered_file(variant["video"].name, variant["video"])
    build_cadence_review(variant["video"], variant_name, variant["resolution"])

    if STAGING_DIR.exists():
        shutil.rmtree(STAGING_DIR)
    STAGING_DIR.mkdir(parents=True, exist_ok=True)
    poster_env = os.environ.copy()
    poster_env["SPIKE_RENDER_TARGET"] = "poster"
    print(f"Rendering {variant['scene']} poster into {variant['poster']}")
    poster_result = subprocess.run(render_command(args, variant_name, poster=True), check=False, env=poster_env)
    if poster_result.returncode != 0:
        raise SystemExit(poster_result.returncode)
    promote_rendered_file(variant["poster"].name, variant["poster"])


def main() -> int:
    args = parse_args()
    for variant_name in VARIANTS:
        render_variant(args, variant_name)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())


from manim import (
    AnimationGroup,
    Circle,
    Create,
    DOWN,
    Dot,
    FadeIn,
    FadeOut,
    LEFT,
    Line,
    MoveAlongPath,
    RIGHT,
    Rectangle,
    Scene,
    UP,
    VGroup,
    always_redraw,
    config,
    linear,
)

config.transparent = True
config.background_opacity = 0.0


def _prepare_poster(scene: Scene) -> None:
    if os.environ.get("SPIKE_RENDER_TARGET") == "poster":
        scene.camera.background_color = PAGE_BACKGROUND


def setup_browser_audit_config() -> None:
    config.pixel_width = 1920
    config.pixel_height = 1080
    config.frame_height = 8.0
    config.frame_width = 8.0 * 16.0 / 9.0


def setup_device_audit_config() -> None:
    config.pixel_width = 1080
    config.pixel_height = 1920
    config.frame_width = 8.0
    config.frame_height = 8.0 * 16.0 / 9.0


def _accent_card(width: float, height: float, stroke_color: str, fill_opacity: float) -> Rectangle:
    card = Rectangle(width=width, height=height)
    card.set_stroke(stroke_color, width=4, opacity=0.72)
    card.set_fill(stroke_color, opacity=fill_opacity)
    return card


def _slot(width: float, height: float, color: str = GRAY_300) -> Rectangle:
    slot = Rectangle(width=width, height=height)
    slot.set_stroke(color, width=3, opacity=0.46)
    slot.set_fill(color, opacity=0.025)
    return slot


def _pulse(radius: float = 0.12) -> tuple[Dot, Circle]:
    dot = Dot(color=PRIMARY_RED, radius=radius)
    halo = always_redraw(
        lambda: Circle(radius=radius * 2.6)
        .set_stroke(PRIMARY_RED, width=4, opacity=0.15)
        .set_fill(PRIMARY_RED, opacity=0.055)
        .move_to(dot)
    )
    return dot, halo


def _make_route(points: list) -> VGroup:
    segments = VGroup()
    for start, end in zip(points, points[1:]):
        segment = Line(start, end, color=GRAY_400, stroke_width=3)
        segment.set_stroke(opacity=0.28)
        segments.add(segment)
    return segments


def _move_on_segment(scene: Scene, dot: Dot, start, end, run_time: float) -> None:
    dot.move_to(start)
    path = Line(start, end)
    scene.play(MoveAlongPath(dot, path), run_time=run_time, rate_func=linear)


def _source_stack(width: float, height: float, gap: float, stroke_width: float) -> VGroup:
    cards = VGroup(
        _accent_card(width, height, GRAY_600, 0.16),
        _accent_card(width, height, GRAY_400, 0.11),
        _accent_card(width, height, GRAY_700, 0.08),
    ).arrange(DOWN, buff=gap)
    cards.set_stroke(opacity=0.6, width=stroke_width)
    return cards


def _line_marks(color: str, widths: tuple[float, ...], stroke_width: float, gap: float) -> VGroup:
    marks = VGroup(*(Line(LEFT * (width / 2), RIGHT * (width / 2), color=color, stroke_width=stroke_width) for width in widths))
    marks.arrange(DOWN, buff=gap)
    marks.set_stroke(opacity=0.58)
    return marks


def _terminal_brackets(width: float, height: float, arm: float, stroke_width: float) -> VGroup:
    x = width / 2
    y = height / 2
    return VGroup(
        Line(LEFT * x + UP * y, LEFT * (x - arm) + UP * y, color=PRIMARY_RED, stroke_width=stroke_width),
        Line(LEFT * x + UP * y, LEFT * x + UP * (y - arm), color=PRIMARY_RED, stroke_width=stroke_width),
        Line(RIGHT * x + DOWN * y, RIGHT * (x - arm) + DOWN * y, color=PRIMARY_RED, stroke_width=stroke_width),
        Line(RIGHT * x + DOWN * y, RIGHT * x + DOWN * (y - arm), color=PRIMARY_RED, stroke_width=stroke_width),
    )


class DeviceFrameEmbedBrowserScene(Scene):
    def construct(self) -> None:
        _prepare_poster(self)
        self.camera.background_opacity = 0.0

        source = _source_stack(1.86, 0.62, 0.22, 3).move_to(LEFT * 4.35 + UP * 0.1)

        processor_slot = _slot(2.55, 1.7).move_to(LEFT * 0.35 + UP * 0.1)
        receipt_slot = _slot(2.45, 1.7).move_to(RIGHT * 3.75 + UP * 0.1)
        processor_card = _accent_card(2.55, 1.7, GRAY_600, 0.055).move_to(processor_slot)
        receipt_card = _accent_card(2.45, 1.7, GRAY_600, 0.075).move_to(receipt_slot)

        processor_marks = _line_marks(GRAY_600, (1.42, 1.05, 0.72), 5, 0.22).move_to(processor_card)
        receipt_marks = _line_marks(GRAY_600, (1.56, 1.16, 1.66), 6, 0.2).move_to(receipt_card)

        points = [
            source.get_right() + RIGHT * 0.3,
            processor_slot.get_left() + LEFT * 0.3,
            processor_slot.get_right() + RIGHT * 0.3,
            receipt_slot.get_left() + LEFT * 0.3,
        ]
        routes = VGroup(_make_route(points[:2]), _make_route(points[2:]))
        dot, halo = _pulse(0.13)
        dot.move_to(points[0])

        final_brackets = _terminal_brackets(2.82, 2.02, 0.34, 5)

        self.add(source, processor_slot, receipt_slot, routes, dot, halo)
        self.wait(2.4)
        _move_on_segment(self, dot, points[0], points[1], 3.0)
        self.play(
            FadeOut(processor_slot),
            FadeIn(processor_card),
            FadeIn(processor_marks, shift=UP * 0.08),
            run_time=1.4,
        )
        self.wait(0.8)
        _move_on_segment(self, dot, points[2], points[3], 3.2)
        self.play(
            AnimationGroup(
                FadeOut(receipt_slot),
                FadeIn(receipt_card),
                FadeIn(receipt_marks, shift=UP * 0.08),
                lag_ratio=0.15,
            ),
            run_time=1.5,
        )
        self.play(FadeOut(routes), FadeOut(halo), FadeOut(dot), run_time=1.2)
        resolved = VGroup(processor_card, processor_marks, receipt_card, receipt_marks)
        self.play(source.animate.set_opacity(0.22).shift(LEFT * 0.25), resolved.animate.shift(LEFT * 0.82), run_time=1.5)
        final_brackets.move_to(receipt_card)
        self.play(Create(final_brackets), run_time=1.0)
        self.wait(10.4)


class DeviceFrameEmbedDeviceScene(Scene):
    def construct(self) -> None:
        _prepare_poster(self)
        self.camera.background_opacity = 0.0

        stack = _source_stack(4.0, 0.72, 0.28, 3.5).move_to(UP * 3.65)

        processor_slot = _slot(4.15, 1.45).move_to(UP * 0.45)
        receipt_slot = _slot(4.15, 1.45).move_to(DOWN * 2.75)
        processor_card = _accent_card(4.15, 1.45, GRAY_600, 0.055).move_to(processor_slot)
        receipt_card = _accent_card(4.15, 1.45, GRAY_600, 0.075).move_to(receipt_slot)

        processor_marks = _line_marks(GRAY_600, (2.25, 1.58, 1.08), 6, 0.2).move_to(processor_card)
        receipt_marks = _line_marks(GRAY_600, (2.25, 1.55, 2.55), 6, 0.2).move_to(receipt_card)

        points = [
            stack.get_bottom() + DOWN * 0.32,
            processor_slot.get_top() + UP * 0.32,
            processor_slot.get_bottom() + DOWN * 0.32,
            receipt_slot.get_top() + UP * 0.32,
        ]
        routes = _make_route(points)
        dot, halo = _pulse(0.14)
        dot.move_to(points[0])

        final_brackets = _terminal_brackets(4.72, 1.78, 0.42, 5.5)

        self.add(stack, processor_slot, receipt_slot, routes, dot, halo)
        self.wait(2.4)
        _move_on_segment(self, dot, points[0], points[1], 3.0)
        self.play(
            FadeOut(processor_slot),
            FadeIn(processor_card),
            FadeIn(processor_marks, shift=UP * 0.08),
            run_time=1.4,
        )
        self.wait(0.8)
        _move_on_segment(self, dot, points[2], points[3], 3.2)
        self.play(
            AnimationGroup(
                FadeOut(receipt_slot),
                FadeIn(receipt_card),
                FadeIn(receipt_marks, shift=UP * 0.08),
                lag_ratio=0.15,
            ),
            run_time=1.5,
        )
        self.play(FadeOut(routes), FadeOut(halo), FadeOut(dot), run_time=1.2)
        resolved = VGroup(processor_card, processor_marks, receipt_card, receipt_marks)
        self.play(stack.animate.set_opacity(0.22).shift(UP * 0.32), resolved.animate.shift(UP * 0.34), run_time=1.5)
        final_brackets.move_to(receipt_card)
        self.play(Create(final_brackets), run_time=1.0)
        self.wait(10.4)
