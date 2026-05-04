#!/usr/bin/env -S uv run --script
# /// script
# dependencies = [
#   "imageio-ffmpeg",
#   "manim>=0.19.0",
#   "pillow",
# ]
# ///

from __future__ import annotations

import argparse
import json
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
REVIEW_DIR = OUTPUT_DIR / "review"
SUMMARY_FILE = OUTPUT_DIR / "recording-summary.json"

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
LEGACY_VIDEO = OUTPUT_DIR / f"{SPIKE_NAME}.webm"

VARIANTS = {
    "full": {
        "scene": "CircleLeftToRightFullScene",
        "resolution": "1920,1080",
        "output": OUTPUT_DIR / "circle-left-to-right-full.webm",
        "mp4": OUTPUT_DIR / "circle-left-to-right-full.mp4",
        "poster": OUTPUT_DIR / "circle-left-to-right-full.png",
    },
    "content": {
        "scene": "CircleLeftToRightContentScene",
        "resolution": "1600,900",
        "output": OUTPUT_DIR / "circle-left-to-right-content.webm",
        "mp4": OUTPUT_DIR / "circle-left-to-right-content.mp4",
        "poster": OUTPUT_DIR / "circle-left-to-right-content.png",
    },
}


class _Args(argparse.Namespace):
    quality: str
    preview: bool


def parse_args() -> _Args:
    parser = argparse.ArgumentParser(
        description="Render the circle-left-to-right Manim spike."
    )
    parser.add_argument(
        "--quality",
        choices=("low", "medium", "high", "production", "4k"),
        default="medium",
        help="Manim quality preset. Defaults to medium for presentation review.",
    )
    parser.add_argument(
        "--preview",
        action="store_true",
        help="Open the rendered output after rendering.",
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


def build_command(args: _Args, variant_name: str) -> list[str]:
    STAGING_DIR.mkdir(parents=True, exist_ok=True)
    variant = VARIANTS[variant_name]

    command = [
        sys.executable,
        "-m",
        "manim",
        "render",
        quality_flag(args.quality),
        "--format",
        "webm",
        "-t",
        "-r",
        variant["resolution"],
        "-o",
        Path(variant["output"]).stem,
        "--media_dir",
        str(STAGING_DIR),
    ]

    if args.preview:
        command.append("-p")

    command.extend([str(Path(__file__).resolve()), variant["scene"]])
    return command


def build_mp4_command(args: _Args, variant_name: str) -> list[str]:
    STAGING_DIR.mkdir(parents=True, exist_ok=True)
    variant = VARIANTS[variant_name]

    command = [
        sys.executable,
        "-m",
        "manim",
        "render",
        quality_flag(args.quality),
        "--format",
        "mp4",
        "-r",
        variant["resolution"],
        "-o",
        Path(variant["mp4"]).stem,
        "--media_dir",
        str(STAGING_DIR),
    ]

    if args.preview:
        command.append("-p")

    command.extend([str(Path(__file__).resolve()), variant["scene"]])
    return command


def build_poster_command(args: _Args, variant_name: str) -> list[str]:
    variant = VARIANTS[variant_name]
    return [
        sys.executable,
        "-m",
        "manim",
        "render",
        quality_flag(args.quality),
        "-s",
        "-r",
        variant["resolution"],
        "-o",
        Path(variant["poster"]).stem,
        "--media_dir",
        str(STAGING_DIR),
        str(Path(__file__).resolve()),
        variant["scene"],
    ]


def promote_rendered_file(target_name: str, destination: Path) -> None:
    matches = sorted(STAGING_DIR.glob(f"**/{target_name}"))
    if not matches:
        raise FileNotFoundError(f"Could not find {target_name} under {STAGING_DIR}")

    source = matches[-1]
    destination.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(source, destination)


def promote_rendered_video(variant_name: str) -> None:
    variant = VARIANTS[variant_name]
    promote_rendered_file(Path(variant["output"]).name, variant["output"])


def promote_mp4(variant_name: str) -> None:
    variant = VARIANTS[variant_name]
    promote_rendered_file(Path(variant["mp4"]).name, variant["mp4"])


def promote_poster(variant_name: str) -> None:
    variant = VARIANTS[variant_name]
    promote_rendered_file(Path(variant["poster"]).name, variant["poster"])


def load_review_font(size: int = 13):
    from PIL import ImageFont

    for name in ("OpenSans-Regular.ttf", "Open Sans.ttf", "arial.ttf", "DejaVuSans.ttf"):
        try:
            return ImageFont.truetype(name, size)
        except OSError:
            continue
    return ImageFont.load_default()


def write_review_frames(video: Path, variant_name: str, cadence: float = 0.3) -> dict[str, object]:
    import imageio_ffmpeg
    from PIL import Image, ImageDraw

    out_dir = REVIEW_DIR / f"{video.stem}-0.3s"
    if out_dir.exists():
        shutil.rmtree(out_dir)
    raw_dir = out_dir / "raw-alpha"
    raw_dir.mkdir(parents=True, exist_ok=True)

    ffmpeg = imageio_ffmpeg.get_ffmpeg_exe()
    raw_pattern = raw_dir / "raw-%04d.png"
    subprocess.run(
        [
            ffmpeg,
            "-y",
            "-c:v",
            "libvpx-vp9",
            "-i",
            str(video),
            "-vf",
            f"fps=1/{cadence}",
            str(raw_pattern),
        ],
        check=True,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.PIPE,
    )

    frames: list[tuple[float, Image.Image]] = []
    alpha_min, alpha_max = 255, 0
    for index, raw_frame in enumerate(sorted(raw_dir.glob("raw-*.png"))):
        timestamp = round(index * cadence, 3)
        rgba = Image.open(raw_frame).convert("RGBA")
        frame_alpha_min, frame_alpha_max = rgba.getchannel("A").getextrema()
        alpha_min = min(alpha_min, frame_alpha_min)
        alpha_max = max(alpha_max, frame_alpha_max)

        background = Image.new("RGBA", rgba.size, WHITE)
        background.alpha_composite(rgba)
        review_frame = background.convert("RGB")
        review_frame.save(out_dir / f"frame-{timestamp:06.3f}.png")
        frames.append((timestamp, review_frame.copy()))

    if not frames:
        raise RuntimeError(f"No review frames extracted from {video}")

    frame_width, frame_height = frames[0][1].size
    thumb_width = 240
    thumb_height = round(thumb_width * frame_height / frame_width)
    label_height = 24
    columns = 5
    rows = math.ceil(len(frames) / columns)
    sheet = Image.new(
        "RGB",
        (columns * thumb_width, rows * (thumb_height + label_height)),
        PAGE_BACKGROUND,
    )
    draw = ImageDraw.Draw(sheet)
    font = load_review_font()

    for index, (timestamp, frame) in enumerate(frames):
        frame.thumbnail((thumb_width, thumb_height), Image.Resampling.LANCZOS)
        tile = Image.new("RGB", (thumb_width, thumb_height), WHITE)
        tile.paste(frame, ((thumb_width - frame.width) // 2, (thumb_height - frame.height) // 2))
        x = (index % columns) * thumb_width
        y = (index // columns) * (thumb_height + label_height)
        sheet.paste(tile, (x, y + label_height))
        draw.text((x + 4, y + 4), f"{timestamp:05.2f}s", fill=GRAY, font=font)
        draw.rectangle(
            [x, y + label_height, x + thumb_width - 1, y + label_height + thumb_height - 1],
            outline=GRAY_200,
        )

    contact_sheet = out_dir / "contact-sheet.png"
    sheet.save(contact_sheet)
    return {
        "variant": variant_name,
        "video": str(video),
        "cadence_seconds": cadence,
        "review_dir": str(out_dir),
        "contact_sheet": str(contact_sheet),
        "frame_count": len(frames),
        "alpha_extrema": [alpha_min, alpha_max],
    }


def main() -> int:
    args = parse_args()
    review_results = []
    for variant_name, variant in VARIANTS.items():
        command = build_command(args, variant_name)
        print(f"Rendering {variant['scene']} into {variant['output']}")
        video_env = os.environ.copy()
        video_env["SPIKE_RENDER_TARGET"] = "video"
        result = subprocess.run(command, check=False, env=video_env)
        if result.returncode != 0:
            return result.returncode
        promote_rendered_video(variant_name)
        review_results.append(write_review_frames(variant["output"], variant_name))

        mp4_env = os.environ.copy()
        mp4_env["SPIKE_RENDER_TARGET"] = "mp4"
        mp4_result = subprocess.run(
            build_mp4_command(args, variant_name),
            check=False,
            env=mp4_env,
        )
        if mp4_result.returncode != 0:
            return mp4_result.returncode
        promote_mp4(variant_name)

        poster_env = os.environ.copy()
        poster_env["SPIKE_RENDER_TARGET"] = "poster"
        poster_result = subprocess.run(
            build_poster_command(args, variant_name),
            check=False,
            env=poster_env,
        )
        if poster_result.returncode != 0:
            return poster_result.returncode
        promote_poster(variant_name)

    shutil.copy2(VARIANTS["full"]["output"], LEGACY_VIDEO)
    shutil.copy2(VARIANTS["full"]["mp4"], OUTPUT_DIR / f"{SPIKE_NAME}.mp4")
    SUMMARY_FILE.write_text(
        json.dumps(
            {
                "spike": SPIKE_NAME,
                "review_cadence_seconds": 0.3,
                "variants": review_results,
            },
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())


from manim import (
    Circle,
    Dot,
    FadeOut,
    Line,
    Scene,
    VGroup,
    ValueTracker,
    always_redraw,
    smooth,
)


class BaseCircleLeftToRightScene(Scene):
    radius = 0.54
    start_x = -4.8
    end_x = 4.8

    def construct(self) -> None:
        if os.environ.get("SPIKE_RENDER_TARGET") in {"mp4", "poster"}:
            self.camera.background_color = PAGE_BACKGROUND

        start = (-abs(self.start_x), 0, 0)
        end = (abs(self.end_x), 0, 0)
        checkpoint = ((start[0] + end[0]) / 2, 0, 0)
        progress = ValueTracker(0)

        def point_at(alpha: float) -> tuple[float, float, float]:
            return (
                start[0] + (end[0] - start[0]) * alpha,
                start[1] + (end[1] - start[1]) * alpha,
                0,
            )

        rail = Line(start, end, color=GRAY_300, stroke_width=6).set_stroke(opacity=0.62)
        start_slot = Circle(radius=self.radius * 1.38, color=GRAY_300, stroke_width=4)
        start_slot.set_fill(WHITE, opacity=0).set_stroke(opacity=0.48).move_to(start)
        target_slot = Circle(radius=self.radius * 1.38, color=GRAY_300, stroke_width=4)
        target_slot.set_fill(WHITE, opacity=0).set_stroke(opacity=0.56).move_to(end)
        checkpoint_slot = Circle(radius=self.radius * 0.72, color=GRAY_200, stroke_width=3)
        checkpoint_slot.set_fill(WHITE, opacity=0).set_stroke(opacity=0.55).move_to(checkpoint)
        ticks = VGroup(
            *[
                Line((x, -0.18, 0), (x, 0.18, 0), color=GRAY_200, stroke_width=3).set_stroke(opacity=0.7)
                for x in (start[0], checkpoint[0], end[0])
            ]
        )

        active_rail = always_redraw(
            lambda: Line(
                start,
                point_at(progress.get_value()),
                color=PRIMARY_RED,
                stroke_width=7,
            ).set_stroke(opacity=0.78)
        )
        circle = Circle(radius=self.radius, color=PRIMARY_RED, stroke_width=7)
        circle.set_fill(PRIMARY_RED, opacity=0.95)
        core = Dot(color=WHITE, radius=self.radius * 0.12)
        leader = VGroup(circle, core).move_to(start).set_z_index(10)
        leader.add_updater(lambda mobject: mobject.move_to(point_at(progress.get_value())))

        self.add(rail, ticks, start_slot, target_slot, checkpoint_slot, active_rail, leader)
        self.wait(3.0)
        self.play(
            target_slot.animate.set_stroke(color=PRIMARY_RED, opacity=0.55, width=5),
            run_time=1.1,
        )
        self.play(progress.animate.set_value(0.5), run_time=5.2, rate_func=smooth)
        self.wait(0.8)
        self.play(
            checkpoint_slot.animate.set_stroke(opacity=0.18),
            start_slot.animate.set_stroke(opacity=0.24),
            progress.animate.set_value(1.0),
            run_time=5.6,
            rate_func=smooth,
        )
        self.wait(1.4)

        leader.clear_updaters()
        active_rail.clear_updaters()
        self.play(
            FadeOut(active_rail),
            FadeOut(checkpoint_slot),
            rail.animate.set_stroke(color=GRAY_300, opacity=0.48, width=5),
            start_slot.animate.set_stroke(color=GRAY_300, opacity=0.22, width=3),
            target_slot.animate.set_stroke(color=GRAY_300, opacity=0.58, width=4),
            run_time=1.9,
        )
        self.wait(6.5)


class CircleLeftToRightFullScene(BaseCircleLeftToRightScene):
    radius = 0.58
    start_x = -4.9
    end_x = 4.9


class CircleLeftToRightContentScene(BaseCircleLeftToRightScene):
    radius = 0.62
    start_x = -4.25
    end_x = 4.25
