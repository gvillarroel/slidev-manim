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
    FadeOut,
    Line,
    Polygon,
    Rectangle,
    Scene,
    Transform,
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

config.transparent = True
config.background_opacity = 0.0


class _Args(argparse.Namespace):
    quality: str
    skip_review: bool


def parse_args() -> _Args:
    parser = argparse.ArgumentParser(description="Render the quality-keystone-lock spike.")
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
        "QualityKeystoneLockScene",
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


def slab(color: str, width: float, height: float, opacity: float = 1) -> Rectangle:
    return Rectangle(width=width, height=height, stroke_width=0, fill_color=color, fill_opacity=opacity)


def slot(width: float, height: float, opacity: float = 0.54) -> Rectangle:
    return Rectangle(width=width, height=height, stroke_color=GRAY_200, stroke_width=2.4, fill_color=WHITE, fill_opacity=0).set_stroke(opacity=opacity)


def keystone(color: str, opacity: float = 1) -> Polygon:
    return Polygon(
        LEFT * 0.96 + UP * 0.45,
        RIGHT * 0.74 + UP * 0.45,
        RIGHT * 1.04,
        RIGHT * 0.58 + DOWN * 0.45,
        LEFT * 0.96 + DOWN * 0.45,
        stroke_width=0,
        fill_color=color,
        fill_opacity=opacity,
    )


class QualityKeystoneLockScene(Scene):
    def construct(self) -> None:
        self.camera.background_color = WHITE

        route = Line(LEFT * 2.35 + DOWN * 0.04, RIGHT * 0.25 + DOWN * 0.04).set_stroke(GRAY_200, 3, opacity=0.52)

        leader = keystone(PRIMARY_RED).scale(1.08).move_to(LEFT * 3.25)
        support_top = slab(GRAY_200, 1.96, 0.34, 0.95).move_to(LEFT * 3.28 + UP * 1.02)
        support_lower = slab(GRAY_200, 1.56, 0.34, 0.95).move_to(LEFT * 2.9 + DOWN * 1.02)
        support_post = slab(GRAY_200, 0.34, 1.56, 0.95).move_to(LEFT * 4.45 + DOWN * 0.03)

        upper_slot = slot(2.14, 0.38).rotate(-PI / 8).move_to(RIGHT * 1.3 + UP * 0.78)
        lower_slot = slot(2.04, 0.38).rotate(PI / 8).move_to(RIGHT * 1.28 + DOWN * 0.78)
        post_slot = slot(0.38, 1.82).move_to(RIGHT * 2.32 + DOWN * 0.02)
        for guide in (route, upper_slot, lower_slot, post_slot):
            guide.set_z_index(0)
        for support in (support_top, support_lower, support_post):
            support.set_z_index(1)
        leader.set_z_index(2)

        upper_lock = slab(GRAY_200, 2.14, 0.34, 0.95).rotate(-PI / 8).move_to(RIGHT * 1.3 + UP * 0.78)
        lower_lock = slab(GRAY_200, 2.04, 0.34, 0.95).rotate(PI / 8).move_to(RIGHT * 1.28 + DOWN * 0.78)
        post_lock = slab(GRAY_200, 0.36, 1.78, 0.95).move_to(RIGHT * 2.34 + DOWN * 0.02)
        red_stretch = keystone(PRIMARY_RED).scale(1.08).stretch(1.16, 0).move_to(LEFT * 0.86)
        red_lock = keystone(PRIMARY_RED).scale(1.08).move_to(RIGHT * 1.3)
        final_shift = LEFT * 1.0

        upper_tight = slab(GRAY_200, 1.92, 0.34, 0.95).rotate(-PI / 8).move_to(RIGHT * 1.28 + UP * 0.66)
        lower_tight = slab(GRAY_200, 1.84, 0.34, 0.95).rotate(PI / 8).move_to(RIGHT * 1.26 + DOWN * 0.66)
        post_tight = slab(GRAY_200, 0.36, 1.54, 0.95).move_to(RIGHT * 2.2 + DOWN * 0.02)

        final_leader = keystone(PRIMARY_RED).scale(1.02).move_to(RIGHT * 0.32)
        final_upper = slab(GRAY_200, 1.68, 0.3, 0.95).rotate(-PI / 9).move_to(RIGHT * 0.28 + UP * 0.74)
        final_lower = slab(GRAY_200, 1.58, 0.3, 0.95).rotate(PI / 9).move_to(RIGHT * 0.26 + DOWN * 0.74)
        final_post = slab(GRAY_200, 0.3, 1.28, 0.95).move_to(RIGHT * 1.74)

        self.add(
            route,
            upper_slot,
            lower_slot,
            post_slot,
            leader,
            support_top,
            support_lower,
            support_post,
        )
        self.wait(2.4)
        self.play(
            AnimationGroup(
                Transform(support_top, upper_lock.copy()),
                Transform(support_lower, lower_lock.copy()),
                Transform(support_post, post_lock.copy()),
                lag_ratio=0.18,
            ),
            run_time=4.0,
            rate_func=smooth,
        )
        self.wait(1.1)
        self.play(Transform(leader, red_stretch.copy()), run_time=2.1, rate_func=smooth)
        self.play(Transform(leader, red_lock.copy()), run_time=2.5, rate_func=smooth)
        self.wait(1.5)
        self.play(
            AnimationGroup(
                FadeOut(upper_slot),
                FadeOut(lower_slot),
                FadeOut(post_slot),
                Transform(leader, red_lock.copy().shift(final_shift)),
                Transform(support_top, upper_tight.copy().shift(final_shift)),
                Transform(support_lower, lower_tight.copy().shift(final_shift)),
                Transform(support_post, post_tight.copy().shift(final_shift)),
                lag_ratio=0.05,
            ),
            run_time=2.4,
            rate_func=smooth,
        )
        self.play(FadeOut(route), run_time=0.7)
        self.wait(1.2)
        self.play(
            AnimationGroup(
                Transform(leader, final_leader.copy()),
                Transform(support_top, final_upper.copy()),
                Transform(support_lower, final_lower.copy()),
                Transform(support_post, final_post.copy()),
                lag_ratio=0.06,
            ),
            run_time=2.4,
            rate_func=smooth,
        )
        self.wait(6.3)


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
