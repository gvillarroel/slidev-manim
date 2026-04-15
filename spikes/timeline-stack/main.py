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
    BLACK,
    BLUE_E,
    DOWN,
    GREY_A,
    GREY_B,
    GREY_D,
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
    RoundedRectangle,
    linear,
)


class BaseTimelineStackScene(Scene):
    card_width = 8.2
    card_height = 1.28
    card_gap = 0.34
    spine_x = -4.4
    spine_top = 2.55
    spine_bottom = -2.55
    card_title_size = 24
    card_body_size = 15
    step_specs = ()

    def construct(self) -> None:
        if os.environ.get("SPIKE_RENDER_TARGET") == "poster":
            self.camera.background_color = WHITE

        spine_start = LEFT * abs(self.spine_x) + UP * self.spine_top
        spine_end = LEFT * abs(self.spine_x) + DOWN * abs(self.spine_bottom)
        spine = Line(spine_start, spine_end, color=GREY_B, stroke_width=9)
        progress = Line(spine_start, spine_start, color=BLUE_E, stroke_width=10)

        self.add(spine, progress)

        cards = []
        markers = []
        for index, spec in enumerate(self.step_specs):
            card = self._build_card(spec["step"], spec["title"], spec["body"])
            card.move_to(spec["position"])
            cards.append(card)

            marker = Circle(radius=0.14, color=BLUE_E, stroke_width=2)
            marker.set_fill(BLUE_E, opacity=0.96)
            marker.move_to(LEFT * abs(self.spine_x) + UP * spec["marker_y"])
            markers.append(marker)

        for index, card in enumerate(cards):
            self.play(
                FadeIn(card, shift=RIGHT * 0.18),
                FadeIn(markers[index], scale=0.92),
                progress.animate.put_start_and_end_on(
                    spine_start,
                    LEFT * abs(self.spine_x) + UP * self.step_specs[index]["marker_y"],
                ),
                run_time=0.42,
                rate_func=linear,
            )
            if index < len(cards) - 1:
                self.play(
                    progress.animate.put_start_and_end_on(
                        spine_start,
                        LEFT * abs(self.spine_x) + UP * self.step_specs[index + 1]["marker_y"],
                    ),
                    run_time=0.32,
                    rate_func=linear,
                )

        self.wait(0.15)

    def _build_card(self, step: str, title: str, body: str) -> VGroup:
        background = RoundedRectangle(
            width=self.card_width,
            height=self.card_height,
            corner_radius=0.18,
            stroke_color=BLUE_E,
            stroke_width=2,
            fill_color=WHITE,
            fill_opacity=0.92,
        )
        badge = RoundedRectangle(
            width=0.9,
            height=0.34,
            corner_radius=0.12,
            stroke_width=0,
            fill_color=BLUE_E,
            fill_opacity=0.96,
        )
        badge_label = Text(step, font_size=14, color=WHITE)
        badge_group = VGroup(badge, badge_label)

        title_text = Text(title, font_size=self.card_title_size, color=BLACK)
        body_text = Text(body, font_size=self.card_body_size, color=GREY_D)

        content = VGroup(badge_group, title_text, body_text).arrange(
            DOWN,
            aligned_edge=LEFT,
            buff=0.14,
        )
        content.move_to(background.get_center()).shift(LEFT * 0.08 + UP * 0.06)
        return VGroup(background, content)


class TimelineStackWideScene(BaseTimelineStackScene):
    card_width = 8.6
    card_height = 1.38
    spine_x = -4.5
    spine_top = 2.45
    spine_bottom = -2.55
    card_title_size = 25
    card_body_size = 15
    step_specs = (
        {
            "step": "01",
            "title": "Open the track",
            "body": "Introduce the first idea\nand keep the motion calm.",
            "position": LEFT * 0.05 + UP * 1.6,
            "marker_y": 1.6,
        },
        {
            "step": "02",
            "title": "Add the middle block",
            "body": "The second section explains\nwhy the sequence continues.",
            "position": LEFT * 0.05 + UP * 0.0,
            "marker_y": 0.0,
        },
        {
            "step": "03",
            "title": "Close with the outcome",
            "body": "The final card lands the point\nand leaves room for the slide.",
            "position": LEFT * 0.05 + DOWN * 1.6,
            "marker_y": -1.6,
        },
    )


class TimelineStackPortraitScene(BaseTimelineStackScene):
    card_width = 5.95
    card_height = 1.54
    spine_x = -2.75
    spine_top = 4.55
    spine_bottom = -4.55
    card_title_size = 22
    card_body_size = 14
    step_specs = (
        {
            "step": "01",
            "title": "Start small",
            "body": "Set the baseline and make\nthe sequence easy to follow.",
            "position": LEFT * 0.05 + UP * 3.0,
            "marker_y": 3.0,
        },
        {
            "step": "02",
            "title": "Stack the middle",
            "body": "Let the next block land below\nwithout losing the rhythm.",
            "position": LEFT * 0.05 + UP * 0.15,
            "marker_y": 0.15,
        },
        {
            "step": "03",
            "title": "Finish vertically",
            "body": "End with a clear visual stop\nthat feels like a conclusion.",
            "position": LEFT * 0.05 + DOWN * 2.7,
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
