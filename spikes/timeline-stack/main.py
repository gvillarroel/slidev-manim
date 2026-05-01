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
FONT_FAMILY = "Arial"

VARIANTS = {
    "wide": {
        "scene": "TimelineStackWideScene",
        "resolution": "1600,900",
        "output": OUTPUT_DIR / "timeline-stack-wide.webm",
        "poster": OUTPUT_DIR / "timeline-stack-wide.png",
    },
    "portrait": {
        "scene": "TimelineStackPortraitScene",
        "resolution": "1080,1440",
        "output": OUTPUT_DIR / "timeline-stack-portrait.webm",
        "poster": OUTPUT_DIR / "timeline-stack-portrait.png",
    },
}


def configure_wide_audit_frame() -> None:
    configure_audit_frame(1600, 900)


def configure_portrait_audit_frame() -> None:
    configure_audit_frame(1080, 1440)


def configure_audit_frame(pixel_width: int, pixel_height: int) -> None:
    from manim import config

    config.pixel_width = pixel_width
    config.pixel_height = pixel_height
    config.frame_height = config.frame_width * (pixel_height / pixel_width)


class _Args(argparse.Namespace):
    quality: str
    preview: bool


def parse_args() -> _Args:
    parser = argparse.ArgumentParser(
        description="Render the timeline-stack Manim spike."
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


def render_command(args: _Args, variant_name: str, *, poster: bool) -> list[str]:
    STAGING_DIR.mkdir(parents=True, exist_ok=True)
    variant = VARIANTS[variant_name]
    output = variant["poster"] if poster else variant["output"]

    command = [
        sys.executable,
        "-m",
        "manim",
        "render",
        quality_flag(args.quality),
        "-r",
        variant["resolution"],
        "-o",
        output.stem,
        "--media_dir",
        str(STAGING_DIR),
    ]

    if poster:
        command.append("-s")
    else:
        command.extend(["--format", "webm", "-t"])
        if args.preview:
            command.append("-p")

    command.extend([str(Path(__file__).resolve()), variant["scene"]])
    return command


def promote_rendered_file(target_name: str, destination: Path) -> None:
    matches = sorted(STAGING_DIR.glob(f"**/{target_name}"))
    if not matches:
        raise FileNotFoundError(f"Could not find {target_name} under {STAGING_DIR}")

    destination.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(matches[-1], destination)


def run_variant(args: _Args, variant_name: str) -> int:
    variant = VARIANTS[variant_name]
    print(f"Rendering {variant['scene']} into {variant['output']}")

    video_result = subprocess.run(
        render_command(args, variant_name, poster=False),
        check=False,
        env={**os.environ, "SPIKE_RENDER_TARGET": "video"},
    )
    if video_result.returncode != 0:
        return video_result.returncode
    promote_rendered_file(Path(variant["output"]).name, variant["output"])

    poster_result = subprocess.run(
        render_command(args, variant_name, poster=True),
        check=False,
        env={**os.environ, "SPIKE_RENDER_TARGET": "poster"},
    )
    if poster_result.returncode != 0:
        return poster_result.returncode
    promote_rendered_file(Path(variant["poster"]).name, variant["poster"])

    return 0


from manim import (
    DOWN,
    LEFT,
    RIGHT,
    Scene,
    Text,
    UP,
    VGroup,
    WHITE,
    Circle,
    FadeIn,
    Line,
    Rectangle,
    Transform,
    linear,
)


class BaseTimelineStackScene(Scene):
    stage_width = 12.8
    stage_height = 7.15
    card_width = 8.2
    card_height = 1.34
    spine_x = -4.4
    spine_top = 2.55
    spine_bottom = -2.55
    card_title_size = 24
    card_body_size = 15
    step_specs = ()

    def construct(self) -> None:
        if os.environ.get("SPIKE_RENDER_TARGET") == "poster":
            self.camera.background_color = PAGE_BACKGROUND

        stage = Rectangle(
            width=self.stage_width,
            height=self.stage_height,
            stroke_width=0,
            fill_color=PAGE_BACKGROUND,
            fill_opacity=0.96,
        )

        spine_start = LEFT * abs(self.spine_x) + UP * self.spine_top
        spine_end = LEFT * abs(self.spine_x) + DOWN * abs(self.spine_bottom)
        spine = Line(spine_start, spine_end, color=GRAY_300, stroke_width=8)
        progress = Line(spine_start, spine_start, color=PRIMARY_RED, stroke_width=9)
        terminal_rule = Line(
            RIGHT * (self.stage_width * 0.28) + DOWN * (abs(self.spine_bottom) - 0.18),
            RIGHT * (self.stage_width * 0.42) + DOWN * (abs(self.spine_bottom) - 0.18),
            color=PRIMARY_RED,
            stroke_width=6,
        )
        terminal_rule.set_opacity(0)

        cards = []
        slots = []
        pending_markers = []
        active_markers = []
        for spec in self.step_specs:
            slot = self._build_slot()
            slot.move_to(spec["position"])
            slots.append(slot)

            card = self._build_card(spec["step"], spec["title"], spec["body"])
            card.move_to(spec["position"])
            cards.append(card)

            marker_point = LEFT * abs(self.spine_x) + UP * spec["marker_y"]
            pending_marker = Circle(radius=0.14, color=GRAY_300, stroke_width=2)
            pending_marker.set_fill(PAGE_BACKGROUND, opacity=1)
            pending_marker.move_to(marker_point)
            pending_markers.append(pending_marker)

            active_marker = Circle(radius=0.19, color=PRIMARY_RED, stroke_width=3)
            active_marker.set_fill(WHITE, opacity=1)
            active_marker.move_to(marker_point)
            active_markers.append(active_marker)

        for slot in slots:
            slot.set_z_index(1)
        for marker in pending_markers + active_markers:
            marker.set_z_index(3)
        for card in cards:
            card.set_z_index(2)
        progress.set_z_index(2)
        terminal_rule.set_z_index(3)

        self.add(stage, spine, progress, *slots, *pending_markers, terminal_rule)
        self.wait(2.8)

        for index, card in enumerate(cards):
            marker_point = LEFT * abs(self.spine_x) + UP * self.step_specs[index]["marker_y"]
            self.play(
                progress.animate.put_start_and_end_on(
                    spine_start,
                    marker_point,
                ),
                run_time=1.15,
                rate_func=linear,
            )
            self.play(
                Transform(pending_markers[index], active_markers[index]),
                slots[index].animate.set_stroke(color=PRIMARY_RED, width=2.5, opacity=0.55),
                FadeIn(card, shift=RIGHT * 0.22),
                run_time=1.2,
            )
            self.play(
                slots[index].animate.set_stroke(color=GRAY_200, width=2, opacity=0.26),
                run_time=0.35,
                rate_func=linear,
            )
            self.wait(2.65)

        self.play(terminal_rule.animate.set_opacity(1), run_time=0.75)
        self.wait(6.5)

    def _build_slot(self) -> Rectangle:
        return Rectangle(
            width=self.card_width,
            height=self.card_height,
            stroke_color=GRAY_200,
            stroke_width=2,
            fill_color=WHITE,
            fill_opacity=0.18,
        )

    def _build_card(self, step: str, title: str, body: str) -> VGroup:
        background = Rectangle(
            width=self.card_width,
            height=self.card_height,
            stroke_color=GRAY_200,
            stroke_width=2,
            fill_color=WHITE,
            fill_opacity=0.96,
        )
        accent = Rectangle(
            width=0.12,
            height=self.card_height,
            stroke_width=0,
            fill_color=PRIMARY_RED,
            fill_opacity=1,
        )
        accent.move_to(background.get_left() + RIGHT * 0.06)

        badge = Rectangle(
            width=0.9,
            height=0.34,
            stroke_width=0,
            fill_color=GRAY_700,
            fill_opacity=0.96,
        )
        badge_label = Text(step, font=FONT_FAMILY, font_size=14, color=WHITE)
        badge_group = VGroup(badge, badge_label)

        title_text = Text(title, font=FONT_FAMILY, font_size=self.card_title_size, color=GRAY)
        body_text = Text(body, font=FONT_FAMILY, font_size=self.card_body_size, color=GRAY_600)

        content = VGroup(badge_group, title_text, body_text).arrange(
            DOWN,
            aligned_edge=LEFT,
            buff=0.12,
        )
        content.move_to(background.get_center()).shift(LEFT * 0.15 + UP * 0.05)
        return VGroup(background, accent, content)


class TimelineStackWideScene(BaseTimelineStackScene):
    stage_width = 12.8
    stage_height = 7.15
    card_width = 8.9
    card_height = 1.48
    spine_x = -4.5
    spine_top = 2.45
    spine_bottom = -2.55
    card_title_size = 27
    card_body_size = 16
    step_specs = (
        {
            "step": "01",
            "title": "Open the track",
            "body": "Introduce the first idea\nand keep the motion calm.",
            "position": RIGHT * 0.36 + UP * 1.62,
            "marker_y": 1.6,
        },
        {
            "step": "02",
            "title": "Add the middle block",
            "body": "The second section explains\nwhy the sequence continues.",
            "position": RIGHT * 0.36 + UP * 0.0,
            "marker_y": 0.0,
        },
        {
            "step": "03",
            "title": "Close with the outcome",
            "body": "The final card lands the point\nand leaves room for the slide.",
            "position": RIGHT * 0.36 + DOWN * 1.62,
            "marker_y": -1.6,
        },
    )


class TimelineStackPortraitScene(BaseTimelineStackScene):
    stage_width = 7.55
    stage_height = 12.75
    card_width = 6.2
    card_height = 1.64
    spine_x = -3.03
    spine_top = 4.55
    spine_bottom = -4.55
    card_title_size = 25
    card_body_size = 15
    step_specs = (
        {
            "step": "01",
            "title": "Start small",
            "body": "Set the baseline and make\nthe sequence easy to follow.",
            "position": RIGHT * 0.42 + UP * 3.0,
            "marker_y": 3.0,
        },
        {
            "step": "02",
            "title": "Stack the middle",
            "body": "Let the next block land below\nwithout losing the rhythm.",
            "position": RIGHT * 0.42 + UP * 0.15,
            "marker_y": 0.15,
        },
        {
            "step": "03",
            "title": "Finish vertically",
            "body": "End with a clear visual stop\nthat feels like a conclusion.",
            "position": RIGHT * 0.42 + DOWN * 2.7,
            "marker_y": -2.7,
        },
    )


def main() -> int:
    args = parse_args()
    for variant_name in VARIANTS:
        result = run_variant(args, variant_name)
        if result != 0:
            return result
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
