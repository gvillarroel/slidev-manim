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

OUTPUT_VIDEO = OUTPUT_DIR / "split-screen-sync.webm"
OUTPUT_POSTER = OUTPUT_DIR / "split-screen-sync.png"


class _Args(argparse.Namespace):
    quality: str
    preview: bool


def parse_args() -> _Args:
    parser = argparse.ArgumentParser(
        description="Render the split-screen-sync Manim spike."
    )
    parser.add_argument(
        "--quality",
        choices=("low", "medium", "high", "production", "4k"),
        default="medium",
        help="Manim quality preset. Defaults to medium for fast iteration.",
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


def build_command(args: _Args, *, poster: bool) -> list[str]:
    STAGING_DIR.mkdir(parents=True, exist_ok=True)
    output = OUTPUT_POSTER if poster else OUTPUT_VIDEO
    command = [
        sys.executable,
        "-m",
        "manim",
        "render",
        quality_flag(args.quality),
    ]

    if poster:
        command.extend(["-s"])
    else:
        command.extend(["--format", "webm", "-t"])
        if args.preview:
            command.append("-p")

    command.extend(
        [
            "-r",
            "1600,900",
            "-o",
            output.stem,
            "--media_dir",
            str(STAGING_DIR),
        ]
    )
    command.extend([str(Path(__file__).resolve()), "SplitScreenSyncScene"])
    return command


def promote_rendered_file(target_name: str, destination: Path) -> None:
    matches = sorted(STAGING_DIR.glob(f"**/{target_name}"))
    if not matches:
        raise FileNotFoundError(f"Could not find {target_name} under {STAGING_DIR}")

    destination.parent.mkdir(parents=True, exist_ok=True)
    newest = max(matches, key=lambda path: path.stat().st_mtime)
    shutil.copy2(newest, destination)


def main() -> int:
    args = parse_args()
    if STAGING_DIR.exists():
        shutil.rmtree(STAGING_DIR)

    video_env = os.environ.copy()
    video_env["SPIKE_RENDER_TARGET"] = "video"
    video_result = subprocess.run(build_command(args, poster=False), env=video_env)
    if video_result.returncode != 0:
        return video_result.returncode
    promote_rendered_file(OUTPUT_VIDEO.name, OUTPUT_VIDEO)

    poster_env = os.environ.copy()
    poster_env["SPIKE_RENDER_TARGET"] = "poster"
    poster_result = subprocess.run(build_command(args, poster=True), env=poster_env)
    if poster_result.returncode != 0:
        return poster_result.returncode
    promote_rendered_file(OUTPUT_POSTER.name, OUTPUT_POSTER)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())


from manim import (
    DOWN,
    LEFT,
    RIGHT,
    UP,
    Circle,
    Create,
    FadeIn,
    FadeOut,
    Line,
    Rectangle,
    Scene,
    VGroup,
    linear,
    smooth,
)


class SplitScreenSyncScene(Scene):
    panel_width = 11.1
    panel_height = 5.8
    row_colors = (PRIMARY_GREEN, PRIMARY_BLUE, PRIMARY_PURPLE)
    row_ys = (1.25, 0.0, -1.25)

    def construct(self) -> None:
        if os.environ.get("SPIKE_RENDER_TARGET") == "poster":
            self.camera.background_color = PAGE_BACKGROUND

        frame = Rectangle(
            width=self.panel_width,
            height=self.panel_height,
            stroke_color=PRIMARY_BLUE,
            stroke_width=5,
            fill_color=PAGE_BACKGROUND,
            fill_opacity=0.96,
        )
        divider = Line(
            UP * 2.45,
            DOWN * 2.45,
            color=GRAY_200,
            stroke_width=4,
        )
        left_stage = Rectangle(
            width=4.25,
            height=4.25,
            stroke_color=GRAY_200,
            stroke_width=3,
            fill_color=WHITE,
            fill_opacity=0.36,
        ).move_to(LEFT * 2.9)
        right_stage = Rectangle(
            width=4.25,
            height=4.25,
            stroke_color=GRAY_200,
            stroke_width=3,
            fill_color=WHITE,
            fill_opacity=0.36,
        ).move_to(RIGHT * 2.9)
        left_stage.set_z_index(0)
        right_stage.set_z_index(0)
        divider.set_z_index(1)

        source_cards = VGroup()
        target_slots = VGroup()
        target_cards = VGroup()
        routes = VGroup()

        for index, (y, color) in enumerate(zip(self.row_ys, self.row_colors)):
            source = self._source_card(color).move_to(LEFT * 2.9 + UP * y)
            slot = self._target_slot().move_to(RIGHT * 2.9 + UP * y)
            target = self._target_card(color).move_to(slot)
            target.set_opacity(0)
            route = Line(
                source.get_right() + RIGHT * 0.42,
                slot.get_left() + LEFT * 0.42,
                color=PRIMARY_ORANGE,
                stroke_width=4,
            ).set_opacity(0.16)
            route.set_z_index(1)
            source.set_z_index(3)
            slot.set_z_index(2)
            target.set_z_index(4)
            source_cards.add(source)
            target_slots.add(slot)
            target_cards.add(target)
            routes.add(route)

        final_links = VGroup(
            *[
                Line(
                    source_cards[index].get_right() + RIGHT * 0.42,
                    target_cards[index].get_left() + LEFT * 0.42,
                    color=GRAY_400,
                    stroke_width=3,
                ).set_opacity(0.0)
                for index in range(len(source_cards))
            ]
        )
        final_outline = self._corner_marks(
            width=3.35,
            height=4.12,
            length=0.48,
            color=PRIMARY_RED,
            stroke_width=6,
        ).move_to(RIGHT * 2.9)
        final_outline.set_z_index(5)
        target_halo = Rectangle(
            width=3.38,
            height=4.12,
            stroke_color=HIGHLIGHT_RED,
            stroke_width=10,
            fill_opacity=0,
        ).move_to(RIGHT * 2.9)
        target_halo.set_z_index(4)

        self.add(
            frame,
            left_stage,
            right_stage,
            divider,
            routes,
            source_cards,
            target_slots,
            target_cards,
            final_links,
        )
        self.wait(2.6)

        for index in range(len(source_cards)):
            source = source_cards[index]
            slot = target_slots[index]
            target = target_cards[index]
            route = routes[index]
            pulse = Circle(radius=0.1, stroke_width=0).set_fill(
                PRIMARY_RED, opacity=1
            )
            pulse.move_to(route.get_start())
            pulse.set_z_index(6)
            active_route = route.copy().set_color(PRIMARY_RED).set_stroke(width=7)
            active_route.set_opacity(1)

            self.play(
                Create(active_route),
                FadeIn(pulse),
                run_time=0.5,
            )
            self.play(
                pulse.animate.move_to(route.get_end()),
                run_time=1.7,
                rate_func=smooth,
            )
            self.play(
                target.animate.set_opacity(1),
                slot.animate.set_opacity(0.0),
                source.animate.set_opacity(0.82),
                run_time=1.0,
            )
            self.play(
                FadeOut(pulse),
                FadeOut(active_route),
                final_links[index].animate.set_opacity(0.42),
                run_time=1.1,
            )
            self.wait(0.7)

        self.play(
            target_slots.animate.set_opacity(0.0),
            routes.animate.set_opacity(0.0),
            final_links.animate.set_opacity(0.22),
            source_cards.animate.set_opacity(0.44),
            left_stage.animate.set_opacity(0.2),
            divider.animate.set_opacity(0.36),
            run_time=0.9,
            rate_func=linear,
        )
        self.play(FadeIn(target_halo), Create(final_outline), run_time=1.0)
        self.play(FadeOut(target_halo), run_time=0.7)
        self.wait(6.1)

    def _source_card(self, color: str) -> VGroup:
        body = Rectangle(
            width=2.55,
            height=0.62,
            stroke_color=color,
            stroke_width=4,
            fill_color=color,
            fill_opacity=0.9,
        )
        notch = Rectangle(
            width=0.38,
            height=0.28,
            stroke_color=WHITE,
            stroke_width=2,
            fill_color=WHITE,
            fill_opacity=0.9,
        ).move_to(body.get_left() + RIGHT * 0.35)
        rail = Line(
            body.get_left() + RIGHT * 0.82,
            body.get_right() + LEFT * 0.28,
            color=WHITE,
            stroke_width=3,
        ).set_opacity(0.72)
        return VGroup(body, notch, rail)

    def _target_slot(self) -> VGroup:
        outer = Rectangle(
            width=2.55,
            height=0.62,
            stroke_color=GRAY_300,
            stroke_width=3,
            fill_color=WHITE,
            fill_opacity=0.18,
        )
        outer.set_stroke(opacity=0.58)
        outer.set_fill(opacity=0.10)
        open_left = Line(
            outer.get_left() + UP * 0.31,
            outer.get_left() + DOWN * 0.31,
            color=PAGE_BACKGROUND,
            stroke_width=7,
        )
        open_left.set_stroke(opacity=1.0)
        return VGroup(outer, open_left)

    def _target_card(self, color: str) -> VGroup:
        body = Rectangle(
            width=2.55,
            height=0.62,
            stroke_color=color,
            stroke_width=3,
            fill_color=color,
            fill_opacity=0.74,
        )
        terminal = Circle(radius=0.1, stroke_width=0).set_fill(PRIMARY_YELLOW, opacity=1)
        terminal.move_to(body.get_right() + LEFT * 0.33)
        return VGroup(body, terminal)

    def _corner_marks(
        self,
        *,
        width: float,
        height: float,
        length: float,
        color: str,
        stroke_width: float,
    ) -> VGroup:
        x = width / 2
        y = height / 2
        marks = VGroup()
        for sx in (-1, 1):
            for sy in (-1, 1):
                corner = RIGHT * (sx * x) + UP * (sy * y)
                horizontal = Line(
                    corner,
                    corner + LEFT * (sx * length),
                    color=color,
                    stroke_width=stroke_width,
                )
                vertical = Line(
                    corner,
                    corner + DOWN * (sy * length),
                    color=color,
                    stroke_width=stroke_width,
                )
                marks.add(horizontal, vertical)
        return marks
