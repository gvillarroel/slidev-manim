#!/usr/bin/env -S uv run --script
# /// script
# dependencies = [
#   "imageio-ffmpeg>=0.6.0",
#   "manim>=0.19.0",
#   "pillow>=10.0.0",
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
REVIEW_DIR = OUTPUT_DIR / "review"

PRIMARY_RED = "#9e1b32"
WHITE = "#ffffff"
GRAY = "#333e48"
GRAY_200 = "#cfcfcf"
GRAY_300 = "#b5b5b5"
GRAY_500 = "#7c7c7c"
PAGE_BACKGROUND = "#f7f7f7"
VIDEO_PATH = OUTPUT_DIR / "mermaid-diagram-side-by-side.webm"
POSTER_PATH = OUTPUT_DIR / "mermaid-diagram-side-by-side.png"


class _Args(argparse.Namespace):
    quality: str
    preview: bool


def parse_args() -> _Args:
    parser = argparse.ArgumentParser(description="Render the mermaid-diagram-side-by-side Manim spike.")
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


def render_command(args: _Args, *, poster: bool) -> list[str]:
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
        "-o",
        (POSTER_PATH if poster else VIDEO_PATH).stem,
        "--media_dir",
        str(STAGING_DIR),
    ]
    if not poster:
        command.append("-t")
    if poster:
        command.append("-s")
    elif args.preview:
        command.append("-p")
    command.extend([str(Path(__file__).resolve()), "MermaidDiagramSideBySideScene"])
    return command


def promote_rendered_file(target_name: str, destination: Path) -> None:
    matches = sorted(STAGING_DIR.glob(f"**/{target_name}"), key=lambda path: path.stat().st_mtime)
    if not matches:
        raise FileNotFoundError(f"Could not find {target_name} under {STAGING_DIR}")
    destination.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(matches[-1], destination)


def render_scene(args: _Args) -> None:
    if STAGING_DIR.exists():
        shutil.rmtree(STAGING_DIR)

    video_env = os.environ.copy()
    video_env["SPIKE_RENDER_TARGET"] = "video"
    video_result = subprocess.run(render_command(args, poster=False), check=False, env=video_env)
    if video_result.returncode != 0:
        raise SystemExit(video_result.returncode)
    promote_rendered_file(VIDEO_PATH.name, VIDEO_PATH)

    poster_env = os.environ.copy()
    poster_env["SPIKE_RENDER_TARGET"] = "poster"
    poster_result = subprocess.run(render_command(args, poster=True), check=False, env=poster_env)
    if poster_result.returncode != 0:
        raise SystemExit(poster_result.returncode)
    promote_rendered_file(POSTER_PATH.name, POSTER_PATH)


def load_review_font(size: int = 13):
    from PIL import ImageFont

    for name in ("OpenSans-Regular.ttf", "Open Sans.ttf", "arial.ttf", "DejaVuSans.ttf"):
        try:
            return ImageFont.truetype(name, size)
        except OSError:
            continue
    return ImageFont.load_default()


def write_review_frames(video: Path, cadence: float = 0.3) -> dict[str, object]:
    import imageio_ffmpeg
    from PIL import Image, ImageDraw

    out_dir = REVIEW_DIR / f"{video.stem}-0.3s"
    if out_dir.exists():
        shutil.rmtree(out_dir)
    raw_dir = out_dir / "raw-alpha"
    raw_dir.mkdir(parents=True, exist_ok=True)

    ffmpeg = imageio_ffmpeg.get_ffmpeg_exe()
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
            str(raw_dir / "raw-%04d.png"),
        ],
        check=True,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.PIPE,
    )

    frames = []
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
    sheet = Image.new("RGB", (columns * thumb_width, rows * (thumb_height + label_height)), PAGE_BACKGROUND)
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
        "video": str(video),
        "cadence_seconds": cadence,
        "review_dir": str(out_dir),
        "contact_sheet": str(contact_sheet),
        "frame_count": len(frames),
        "alpha_extrema": [alpha_min, alpha_max],
    }


def main() -> int:
    args = parse_args()
    render_scene(args)
    result = write_review_frames(VIDEO_PATH)
    print(
        "Review frames: "
        f"{result['frame_count']} at {result['cadence_seconds']}s cadence, "
        f"alpha={result['alpha_extrema']}, sheet={result['contact_sheet']}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())


from manim import (  # noqa: E402
    DOWN,
    Dot,
    FadeIn,
    FadeOut,
    LEFT,
    Line,
    MoveAlongPath,
    Rectangle,
    RIGHT,
    Scene,
    Text,
    Transform,
    VGroup,
    config,
    linear,
)

config.transparent = True
config.background_opacity = 0.0

FONT = "Arial"


def make_card(label: str, *, width: float = 2.28, height: float = 1.02) -> VGroup:
    body = Rectangle(width=width, height=height, stroke_color=GRAY, stroke_width=3)
    body.set_fill(WHITE, opacity=0.96)
    text = Text(label, font=FONT, font_size=27, color=GRAY).move_to(body)
    return VGroup(body, text)


def make_slot(label: str, *, width: float = 2.28, height: float = 1.02) -> VGroup:
    body = Rectangle(width=width, height=height, stroke_color=GRAY_300, stroke_width=2)
    body.set_fill(WHITE, opacity=0.16)
    text = Text(label, font=FONT, font_size=24, color=GRAY_500).move_to(body)
    text.set_opacity(0.42)
    return VGroup(body, text)


def make_corner_brackets(target: VGroup, *, color: str = PRIMARY_RED, length: float = 0.28, inset: float = 0.11) -> VGroup:
    box = target[0]
    left = box.get_left()[0] - inset
    right = box.get_right()[0] + inset
    top = box.get_top()[1] + inset
    bottom = box.get_bottom()[1] - inset
    return VGroup(
        Line([left, top, 0], [left + length, top, 0], color=color, stroke_width=5),
        Line([left, top, 0], [left, top - length, 0], color=color, stroke_width=5),
        Line([right, top, 0], [right - length, top, 0], color=color, stroke_width=5),
        Line([right, top, 0], [right, top - length, 0], color=color, stroke_width=5),
        Line([left, bottom, 0], [left + length, bottom, 0], color=color, stroke_width=5),
        Line([left, bottom, 0], [left, bottom + length, 0], color=color, stroke_width=5),
        Line([right, bottom, 0], [right - length, bottom, 0], color=color, stroke_width=5),
        Line([right, bottom, 0], [right, bottom + length, 0], color=color, stroke_width=5),
    )


def make_route(start, end, *, color: str = GRAY_300, width: float = 5) -> Line:
    route = Line(start, end, color=color, stroke_width=width)
    route.set_stroke(opacity=0.78)
    return route


class MermaidDiagramSideBySideScene(Scene):
    def construct(self) -> None:
        self.camera.background_opacity = 0.0
        if os.environ.get("SPIKE_RENDER_TARGET") == "poster":
            self.camera.background_color = PAGE_BACKGROUND
            self.camera.background_opacity = 1.0

        source = make_card("Source").shift(LEFT * 3.8 + DOWN * 0.1)
        transform_slot = make_slot("Transform").shift(DOWN * 0.1)
        output_slot = make_slot("Output").shift(RIGHT * 3.8 + DOWN * 0.1)

        route_gap = 0.2
        route_a = make_route(source[0].get_right() + RIGHT * route_gap, transform_slot[0].get_left() + LEFT * route_gap)
        route_b = make_route(transform_slot[0].get_right() + RIGHT * route_gap, output_slot[0].get_left() + LEFT * route_gap)
        top_rule = Line([-5.45, 1.06, 0], [5.45, 1.06, 0], color=GRAY_200, stroke_width=3)
        bottom_rule = Line([-5.45, -1.26, 0], [5.45, -1.26, 0], color=GRAY_200, stroke_width=3)
        top_rule.set_stroke(opacity=0.54)
        bottom_rule.set_stroke(opacity=0.54)

        pulse = Dot(color=PRIMARY_RED, radius=0.14).move_to(route_a.get_start())
        transform_cue = make_corner_brackets(transform_slot)
        output_cue = make_corner_brackets(output_slot)
        transform_card = make_card("Transform").move_to(transform_slot)
        output_card = make_card("Output").move_to(output_slot)

        for item in (
            source,
            transform_slot,
            output_slot,
            transform_card,
            output_card,
            route_a,
            route_b,
            top_rule,
            bottom_rule,
            pulse,
            transform_cue,
            output_cue,
        ):
            item.scale(1.24, about_point=[0, 0, 0])

        transform_cue.set_opacity(0.0)
        output_cue.set_opacity(0.0)

        self.add(top_rule, bottom_rule, route_a, route_b, transform_slot, output_slot, source, pulse)
        self.wait(3.0)

        self.play(FadeIn(transform_cue), run_time=0.8)
        self.wait(0.9)
        self.play(MoveAlongPath(pulse, route_a), run_time=3.0, rate_func=linear)
        self.wait(0.7)
        self.play(
            FadeOut(transform_slot),
            Transform(transform_cue, make_corner_brackets(transform_card, color=GRAY_300)),
            FadeIn(transform_card, shift=DOWN * 0.08),
            run_time=1.6,
        )
        self.wait(1.1)

        next_pulse = Dot(color=PRIMARY_RED, radius=0.14).move_to(route_b.get_start())
        self.play(Transform(pulse, next_pulse), FadeIn(output_cue), run_time=0.8)
        self.wait(0.9)
        self.play(MoveAlongPath(pulse, route_b), run_time=3.0, rate_func=linear)
        self.wait(0.7)
        self.play(
            FadeOut(output_slot),
            Transform(output_cue, make_corner_brackets(output_card, color=GRAY_300)),
            FadeIn(output_card, shift=DOWN * 0.08),
            run_time=1.6,
        )
        self.wait(1.0)

        final_brackets = make_corner_brackets(output_card)
        self.play(
            FadeOut(transform_cue),
            FadeOut(output_cue),
            route_a.animate.set_stroke(color=GRAY_200, opacity=0.42, width=3),
            route_b.animate.set_stroke(color=GRAY_200, opacity=0.42, width=3),
            FadeIn(final_brackets),
            FadeOut(pulse),
            run_time=2.2,
        )
        self.wait(6.2)
