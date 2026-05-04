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
    "hero": {
        "scene": "HeroPlusSupportingLoopHeroScene",
        "resolution": "1920,1080",
        "video": OUTPUT_DIR / "hero-plus-supporting-loop-hero.webm",
        "poster": OUTPUT_DIR / "hero-plus-supporting-loop-hero.png",
    },
    "support": {
        "scene": "HeroPlusSupportingLoopSupportScene",
        "resolution": "1080,1080",
        "video": OUTPUT_DIR / "hero-plus-supporting-loop-support.webm",
        "poster": OUTPUT_DIR / "hero-plus-supporting-loop-support.png",
    },
}


class _Args(argparse.Namespace):
    quality: str
    preview: bool


def parse_args() -> _Args:
    parser = argparse.ArgumentParser(
        description="Render the hero-plus-supporting-loop Manim spike."
    )
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
    STAGING_DIR.mkdir(parents=True, exist_ok=True)
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
    matches = sorted(STAGING_DIR.glob(f"**/{target_name}"))
    if not matches:
        raise FileNotFoundError(f"Could not find {target_name} under {STAGING_DIR}")

    destination.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(matches[-1], destination)


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
    frames_dir = out_dir / "frames"
    raw_dir.mkdir(parents=True, exist_ok=True)
    frames_dir.mkdir(parents=True, exist_ok=True)

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
        review_frame.save(frames_dir / f"frame-{index + 1:04d}-t{timestamp:06.3f}.png")
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


def render_variant(args: _Args, variant_name: str) -> None:
    variant = VARIANTS[variant_name]

    video_env = os.environ.copy()
    video_env["SPIKE_RENDER_TARGET"] = "video"
    print(f"Rendering {variant['scene']} into {variant['video']}")
    video_result = subprocess.run(
        render_command(args, variant_name, poster=False),
        check=False,
        env=video_env,
    )
    if video_result.returncode != 0:
        raise SystemExit(video_result.returncode)
    promote_rendered_file(variant["video"].name, variant["video"])

    poster_env = os.environ.copy()
    poster_env["SPIKE_RENDER_TARGET"] = "poster"
    print(f"Rendering {variant['scene']} poster into {variant['poster']}")
    poster_result = subprocess.run(
        render_command(args, variant_name, poster=True),
        check=False,
        env=poster_env,
    )
    if poster_result.returncode != 0:
        raise SystemExit(poster_result.returncode)
    promote_rendered_file(variant["poster"].name, variant["poster"])


def main() -> int:
    args = parse_args()
    if STAGING_DIR.exists():
        shutil.rmtree(STAGING_DIR)
    review_results = []
    for variant_name in VARIANTS:
        render_variant(args, variant_name)
        review_results.append(write_review_frames(VARIANTS[variant_name]["video"], variant_name))
    for result in review_results:
        print(
            "Review "
            f"{result['variant']}: frames={result['frame_count']} "
            f"alpha={result['alpha_extrema'][0]}..{result['alpha_extrema'][1]} "
            f"sheet={result['contact_sheet']}"
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())


from manim import (
    ORIGIN,
    PI,
    Arc,
    Circle,
    Create,
    Dot,
    FadeIn,
    FadeOut,
    GrowFromCenter,
    Line,
    MoveAlongPath,
    Scene,
    Transform,
    VGroup,
    always_redraw,
    linear,
    smooth,
)


class HeroPlusSupportingLoopHeroScene(Scene):
    def construct(self) -> None:
        if os.environ.get("SPIKE_RENDER_TARGET") == "poster":
            self.camera.background_color = PAGE_BACKGROUND

        route_radius = 3.16
        orbit = Circle(radius=route_radius, color=GRAY, stroke_width=13)
        orbit.set_stroke(opacity=0.82)

        inner_orbit = Circle(radius=1.9, color=GRAY_300, stroke_width=5)
        inner_orbit.set_stroke(opacity=0.7)

        center_ring = Circle(radius=0.86, color=GRAY_200, stroke_width=7)
        center_ring.set_stroke(opacity=0.9)

        center_core = Dot(ORIGIN, color=GRAY_700, radius=0.22)

        anchor_proportions = (0.0, 0.25, 0.5, 0.75)
        anchor_positions = [orbit.point_from_proportion(p) for p in anchor_proportions]
        anchor_points = VGroup(
            *[
                Dot(position, color=GRAY_600, radius=0.085).set_opacity(0.72)
                for position in anchor_positions
            ]
        )
        support_links = VGroup(
            *[
                Line(ORIGIN, position, color=GRAY_200, stroke_width=3).set_opacity(0.38)
                for position in anchor_positions
            ]
        )

        support_nodes = VGroup(
            Dot([-1.62, -1.0, 0], color=GRAY_400, radius=0.12),
            Dot([0, -1.32, 0], color=GRAY_400, radius=0.12),
            Dot([1.62, -1.0, 0], color=GRAY_400, radius=0.12),
        )
        support_nodes.set_opacity(0.72)
        support_fan = VGroup(
            *[
                Line(node.get_center(), ORIGIN, color=GRAY_200, stroke_width=2.5).set_opacity(0.34)
                for node in support_nodes
            ]
        )

        lead = Dot(color=PRIMARY_RED, radius=0.18)
        lead.move_to(anchor_positions[0])
        lead_glow = always_redraw(
            lambda: Circle(radius=0.27, color=PRIMARY_RED, stroke_width=4.5)
            .set_fill(PRIMARY_RED, opacity=0.08)
            .set_stroke(opacity=0.42)
            .move_to(lead)
        )

        self.add(
            support_links,
            support_fan,
            inner_orbit,
            orbit,
            center_ring,
            center_core,
            anchor_points,
            support_nodes,
            lead_glow,
            lead,
        )
        self.wait(2.6)

        trail_segments = VGroup()
        for index, position in enumerate(anchor_positions[1:] + [anchor_positions[0]]):
            path = Arc(
                radius=route_radius,
                start_angle=index * PI / 2,
                angle=PI / 2,
                color=PRIMARY_RED,
                stroke_width=8,
            )
            path.set_stroke(opacity=0.0)
            trail = path.copy().set_stroke(opacity=0.74)
            trail_segments.add(trail)

            pulse = Circle(radius=0.29, color=PRIMARY_RED, stroke_width=4.5).move_to(position)
            pulse.set_fill(PRIMARY_RED, opacity=0.06).set_stroke(opacity=0.68)
            self.play(
                MoveAlongPath(lead, path),
                Create(trail),
                run_time=3.0,
                rate_func=linear,
            )
            self.play(
                GrowFromCenter(pulse),
                anchor_points[index + 1 if index < 3 else 0].animate.set_color(PRIMARY_RED).scale(1.22),
                run_time=0.35,
            )
            self.play(
                FadeOut(pulse, scale=1.45),
                anchor_points[index + 1 if index < 3 else 0].animate.set_color(GRAY_600).scale(1 / 1.22),
                run_time=0.55,
            )

        support_targets = [
            [-0.72, -0.43, 0],
            [0, -0.58, 0],
            [0.72, -0.43, 0],
        ]
        for node, target in zip(support_nodes, support_targets):
            self.play(
                node.animate.move_to(target).set_opacity(0.86),
                run_time=1.0,
                rate_func=smooth,
            )

        terminal_core = Dot(ORIGIN, color=PRIMARY_RED, radius=0.22)
        terminal_spokes = VGroup(
            *[
                Line(
                    [target[0] * 0.33, target[1] * 0.33, 0],
                    [target[0] * 0.82, target[1] * 0.82, 0],
                    color=GRAY_300,
                    stroke_width=3.2,
                ).set_opacity(0.58)
                for target in support_targets
            ]
        )
        terminal_outer = Circle(radius=route_radius, color=GRAY, stroke_width=12).set_stroke(opacity=0.66)
        terminal_inner = Circle(radius=1.9, color=GRAY_300, stroke_width=4).set_stroke(opacity=0.52)
        self.play(
            Transform(lead, terminal_core),
            Transform(orbit, terminal_outer),
            Transform(inner_orbit, terminal_inner),
            FadeIn(terminal_spokes),
            FadeOut(lead_glow, scale=1.2),
            FadeOut(trail_segments, shift=ORIGIN),
            FadeOut(anchor_points, scale=0.92),
            FadeOut(support_links),
            FadeOut(support_fan),
            FadeOut(center_core, scale=0.82),
            FadeOut(center_ring, scale=0.92),
            run_time=1.8,
            rate_func=smooth,
        )
        self.wait(6.2)


class HeroPlusSupportingLoopSupportScene(Scene):
    def construct(self) -> None:
        if os.environ.get("SPIKE_RENDER_TARGET") == "poster":
            self.camera.background_color = PAGE_BACKGROUND

        orbit = Circle(radius=2.32, color=GRAY, stroke_width=13)
        orbit.set_stroke(opacity=0.82)

        support_ring = Circle(radius=2.84, color=GRAY_300, stroke_width=5)
        support_ring.set_stroke(opacity=0.66)

        center_core = Dot(ORIGIN, color=GRAY_700, radius=0.19)

        motion_path = Circle(radius=2.58)
        orbit_dot = Dot(color=PRIMARY_RED, radius=0.16)
        orbit_dot.move_to(motion_path.point_from_proportion(0))

        orbit_glow = always_redraw(
            lambda: Circle(radius=0.29, color=PRIMARY_RED, stroke_width=4.5)
            .set_fill(PRIMARY_RED, opacity=0.08)
            .set_stroke(opacity=0.42)
            .move_to(orbit_dot)
        )

        guide = Line(
            orbit.point_from_proportion(0.0),
            orbit.point_from_proportion(0.5),
            color=GRAY_300,
            stroke_width=4,
        )
        guide.set_stroke(opacity=0.58)

        self.add(support_ring, guide, orbit, center_core, orbit_glow, orbit_dot)
        self.wait(0.7)
        self.play(
            MoveAlongPath(orbit_dot, motion_path),
            run_time=5.05,
            rate_func=linear,
        )
        self.wait(0.55)
