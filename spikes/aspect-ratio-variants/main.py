#!/usr/bin/env -S uv run --script
# /// script
# dependencies = [
#   "manim>=0.19.0",
# ]
# ///

from __future__ import annotations

import argparse
import os
import shutil
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path

SPIKE_DIR = Path(__file__).resolve().parent
REPO_ROOT = SPIKE_DIR.parent.parent
SPIKE_NAME = SPIKE_DIR.name
OUTPUT_DIR = REPO_ROOT / "videos" / SPIKE_NAME
STAGING_DIR = OUTPUT_DIR / ".manim"

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


@dataclass(frozen=True)
class Variant:
    name: str
    scene_name: str
    width: int
    height: int


VARIANTS = (
    Variant(name="wide", scene_name="WideAspectRatioScene", width=1600, height=900),
    Variant(name="tall", scene_name="TallAspectRatioScene", width=900, height=1600),
)


class _Args(argparse.Namespace):
    quality: str
    preview: bool


def parse_args() -> _Args:
    parser = argparse.ArgumentParser(
        description="Render the aspect-ratio-variants Manim spike."
    )
    parser.add_argument(
        "--quality",
        choices=("low", "medium", "high", "production", "4k"),
        default="medium",
        help="Manim quality preset. Defaults to medium for quick iteration.",
    )
    parser.add_argument(
        "--preview",
        action="store_true",
        help="Open each rendered video after completion.",
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


def render_command(args: _Args, variant: Variant, *, poster: bool) -> list[str]:
    STAGING_DIR.mkdir(parents=True, exist_ok=True)
    output_name = f"{SPIKE_NAME}-{variant.name}"
    command = [
        sys.executable,
        "-m",
        "manim",
        "render",
        quality_flag(args.quality),
        "-r",
        f"{variant.width},{variant.height}",
        "--format",
        "webm",
        "-t",
        "-o",
        output_name,
        "--media_dir",
        str(STAGING_DIR),
    ]
    if poster:
        command.append("-s")
    if args.preview:
        command.append("-p")
    command.extend([str(Path(__file__).resolve()), variant.scene_name])
    return command


def promote_rendered_file(target_name: str, destination: Path) -> None:
    matches = sorted(STAGING_DIR.glob(f"**/{target_name}"))
    if not matches:
        raise FileNotFoundError(f"Could not find {target_name} under {STAGING_DIR}")

    destination.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(matches[-1], destination)


def render_variant(args: _Args, variant: Variant) -> int:
    output_video = OUTPUT_DIR / f"{SPIKE_NAME}-{variant.name}.webm"
    output_poster = OUTPUT_DIR / f"{SPIKE_NAME}-{variant.name}.png"

    video_env = os.environ.copy()
    video_env["SPIKE_RENDER_TARGET"] = "video"
    print(f"Rendering {variant.scene_name} into {output_video}")
    video_result = subprocess.run(
        render_command(args, variant, poster=False),
        check=False,
        env=video_env,
    )
    if video_result.returncode != 0:
        return video_result.returncode
    promote_rendered_file(output_video.name, output_video)

    poster_env = os.environ.copy()
    poster_env["SPIKE_RENDER_TARGET"] = "poster"
    print(f"Rendering {variant.scene_name} poster into {output_poster}")
    poster_result = subprocess.run(
        render_command(args, variant, poster=True),
        check=False,
        env=poster_env,
    )
    if poster_result.returncode != 0:
        return poster_result.returncode
    promote_rendered_file(output_poster.name, output_poster)

    return 0


def main() -> int:
    args = parse_args()
    for variant in VARIANTS:
        result = render_variant(args, variant)
        if result != 0:
            return result
    return 0


if __name__ == "__main__":
    raise SystemExit(main())


from manim import (
    DOWN,
    LEFT,
    RIGHT,
    UP,
    WHITE,
    Arrow,
    Circle,
    Line,
    RoundedRectangle,
    Scene,
    Text,
    VGroup,
    linear,
)


class AspectRatioVariantBase(Scene):
    title_text = "Aspect ratio variants"
    subtitle_text = "The same idea can be framed differently for different slide layouts."
    accent_label = "Reusable motion"

    def is_poster(self) -> bool:
        return os.environ.get("SPIKE_RENDER_TARGET") == "poster"

    def make_label_chip(self, text: str) -> VGroup:
        chip = RoundedRectangle(
            corner_radius=0.16,
            width=3.0,
            height=0.72,
            stroke_color=PRIMARY_BLUE,
            stroke_width=4,
            fill_color=WHITE,
            fill_opacity=1,
        )
        label = Text(text, font_size=26, color=GRAY)
        label.move_to(chip.get_center())
        return VGroup(chip, label)

    def make_track(
        self,
        *,
        start: object,
        end: object,
    ) -> tuple[Line, Circle, Circle]:
        track = Line(start, end, color=GRAY_300, stroke_width=10)
        start_marker = Circle(radius=0.09, color=GRAY_600, stroke_width=0).move_to(start)
        end_marker = Circle(radius=0.09, color=GRAY_600, stroke_width=0).move_to(end)
        return track, start_marker, end_marker


class WideAspectRatioScene(AspectRatioVariantBase):
    def construct(self) -> None:
        if self.is_poster():
            self.camera.background_color = PAGE_BACKGROUND

        stage = RoundedRectangle(
            width=12.85,
            height=7.15,
            corner_radius=0.34,
            stroke_width=0,
            fill_color=PAGE_BACKGROUND,
            fill_opacity=0.96,
        )

        frame = RoundedRectangle(
            width=12.2,
            height=6.25,
            corner_radius=0.34,
            stroke_color=PRIMARY_BLUE,
            stroke_width=6,
            fill_color=PAGE_BACKGROUND,
            fill_opacity=0.96,
        )
        frame.shift(DOWN * 0.08)

        title = Text(self.title_text, font_size=42, color=GRAY)
        subtitle = Text(self.subtitle_text, font_size=24, color=GRAY)
        title_group = VGroup(title, subtitle).arrange(DOWN, aligned_edge=LEFT, buff=0.18)
        title_group.to_edge(UP, buff=1.05).shift(LEFT * 2.75)

        chip = self.make_label_chip(self.accent_label)
        chip.next_to(title_group, DOWN, buff=0.38).align_to(title_group, LEFT)

        track_start = LEFT * 4.95 + DOWN * 0.7
        track_end = RIGHT * 4.95 + DOWN * 0.7
        track, start_marker, end_marker = self.make_track(
            start=track_start,
            end=track_end,
        )

        moving_circle = Circle(radius=0.72, color=PRIMARY_GREEN, stroke_width=10)
        moving_circle.set_fill(PRIMARY_GREEN, opacity=0.94)
        moving_circle.move_to(LEFT * 4.95 + DOWN * 0.05)

        arrow = Arrow(
            chip.get_bottom(),
            moving_circle.get_top(),
            buff=0.12,
            color=PRIMARY_ORANGE,
            stroke_width=6,
            max_tip_length_to_length_ratio=0.16,
        )

        self.add(stage, frame, title_group, chip, track, start_marker, end_marker, arrow, moving_circle)
        self.play(
            moving_circle.animate.move_to(RIGHT * 4.95 + DOWN * 0.05),
            run_time=3.0,
            rate_func=linear,
        )
        self.wait(0.15)


class TallAspectRatioScene(AspectRatioVariantBase):
    title_text = "Tall variant"
    subtitle_text = "The same motion can become a sidebar-ready visual when the frame is narrow."
    accent_label = "Vertical framing"

    def construct(self) -> None:
        if self.is_poster():
            self.camera.background_color = PAGE_BACKGROUND

        stage = RoundedRectangle(
            width=6.95,
            height=12.75,
            corner_radius=0.34,
            stroke_width=0,
            fill_color=PAGE_BACKGROUND,
            fill_opacity=0.96,
        )

        frame = RoundedRectangle(
            width=5.8,
            height=12.8,
            corner_radius=0.34,
            stroke_color=PRIMARY_BLUE,
            stroke_width=6,
            fill_color=PAGE_BACKGROUND,
            fill_opacity=0.96,
        )
        frame.shift(DOWN * 0.08)

        title = Text(self.title_text, font_size=42, color=GRAY)
        subtitle = Text(self.subtitle_text, font_size=24, color=GRAY)
        title_group = VGroup(title, subtitle).arrange(DOWN, aligned_edge=LEFT, buff=0.18)
        title_group.to_edge(UP, buff=0.95)

        chip = self.make_label_chip(self.accent_label)
        chip.next_to(title_group, DOWN, buff=0.32).align_to(title_group, LEFT)

        track_start = UP * 4.6 + LEFT * 0.05
        track_end = DOWN * 4.8 + LEFT * 0.05
        track, start_marker, end_marker = self.make_track(
            start=track_start,
            end=track_end,
        )

        moving_circle = Circle(radius=0.72, color=PRIMARY_GREEN, stroke_width=10)
        moving_circle.set_fill(PRIMARY_GREEN, opacity=0.94)
        moving_circle.move_to(UP * 4.55 + RIGHT * 0.18)

        arrow = Arrow(
            chip.get_bottom(),
            moving_circle.get_left(),
            buff=0.12,
            color=PRIMARY_ORANGE,
            stroke_width=6,
            max_tip_length_to_length_ratio=0.16,
        )

        help_box = RoundedRectangle(
            corner_radius=0.18,
            width=4.25,
            height=1.05,
            stroke_color=GRAY_300,
            stroke_width=3,
            fill_color=WHITE,
            fill_opacity=1,
        )
        help_text = Text("Good for a narrow panel or stacked layout.", font_size=22, color=GRAY)
        help_text.move_to(help_box.get_center())
        help_group = VGroup(help_box, help_text)
        help_group.next_to(track, UP, buff=0.45)

        self.add(
            stage,
            frame,
            title_group,
            chip,
            help_group,
            track,
            start_marker,
            end_marker,
            arrow,
            moving_circle,
        )
        self.play(
            moving_circle.animate.move_to(DOWN * 4.7 + RIGHT * 0.18),
            run_time=3.0,
            rate_func=linear,
        )
        self.wait(0.15)
