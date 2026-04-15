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
    "intro": {
        "scene": "StepRevealIntroScene",
        "resolution": "1920,1080",
        "output": OUTPUT_DIR / "step-reveal-sequence-intro.webm",
        "poster": OUTPUT_DIR / "step-reveal-sequence-intro.png",
    },
    "context": {
        "scene": "StepRevealContextScene",
        "resolution": "1920,1080",
        "output": OUTPUT_DIR / "step-reveal-sequence-context.webm",
        "poster": OUTPUT_DIR / "step-reveal-sequence-context.png",
    },
    "wrap": {
        "scene": "StepRevealWrapScene",
        "resolution": "1920,1080",
        "output": OUTPUT_DIR / "step-reveal-sequence-wrap.webm",
        "poster": OUTPUT_DIR / "step-reveal-sequence-wrap.png",
    },
}


class _Args(argparse.Namespace):
    quality: str
    preview: bool


def parse_args() -> _Args:
    parser = argparse.ArgumentParser(
        description="Render the step-reveal-sequence Manim spike."
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
        "-o",
        Path(variant["poster"] if poster else variant["output"]).stem,
        "--media_dir",
        str(STAGING_DIR),
    ]

    if not poster:
        command.extend(["--format", "webm", "-t"])
    else:
        command.append("-s")

    if args.preview:
        command.append("-p")

    command.extend([str(Path(__file__).resolve()), variant["scene"]])
    return command


def promote_rendered_file(target_name: str, destination: Path) -> None:
    matches = sorted(STAGING_DIR.glob(f"**/{target_name}"))
    if not matches:
        raise FileNotFoundError(f"Could not find {target_name} under {STAGING_DIR}")

    source = matches[-1]
    destination.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(source, destination)


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
    BLUE_E,
    DOWN,
    LEFT,
    RIGHT,
    UP,
    UR,
    BLACK,
    GRAY_B,
    GRAY_D,
    WHITE,
    Circle,
    Create,
    FadeIn,
    GrowFromCenter,
    Line,
    RoundedRectangle,
    Scene,
    Text,
    VGroup,
    linear,
)


class BaseStepRevealScene(Scene):
    headline = ""
    subtitle = ""
    card_title = ""
    card_body = ""
    final_label = ""

    def construct(self) -> None:
        if os.environ.get("SPIKE_RENDER_TARGET") == "poster":
            self.camera.background_color = WHITE

        title = Text(self.headline, font_size=42, color=BLACK)
        title.to_edge(UP, buff=0.55)
        subtitle = Text(self.subtitle, font_size=24, color=GRAY_D)
        subtitle.next_to(title, DOWN, buff=0.18)

        track = Line(
            LEFT * 5.7 + DOWN * 0.65,
            RIGHT * 5.7 + DOWN * 0.65,
            color=GRAY_B,
            stroke_width=10,
        )
        start_marker = Circle(radius=0.12, color=GRAY_B, stroke_width=2)
        end_marker = Circle(radius=0.12, color=GRAY_B, stroke_width=2)
        start_marker.move_to(LEFT * 5.2 + DOWN * 0.65)
        end_marker.move_to(RIGHT * 5.2 + DOWN * 0.65)

        circle = Circle(radius=0.42, color=BLUE_E, stroke_width=8)
        circle.set_fill(BLUE_E, opacity=0.92)
        circle.move_to(LEFT * 5.2 + DOWN * 0.65)

        self.add(track, start_marker, end_marker, title, subtitle, circle)
        self.play(GrowFromCenter(circle), run_time=0.35)
        self.play(
            circle.animate.move_to(LEFT * 0.6 + DOWN * 0.65),
            run_time=1.15,
            rate_func=linear,
        )

        card = None
        if self.card_title:
            card = self._build_card()
            self.play(FadeIn(card, shift=UP * 0.18), run_time=0.4)

        self.play(
            circle.animate.move_to(RIGHT * 5.2 + DOWN * 0.65),
            run_time=1.2,
            rate_func=linear,
        )

        if self.final_label:
            badge = self._build_badge()
            self.play(FadeIn(badge, shift=UP * 0.12), run_time=0.35)

        self.wait(0.15)

    def _build_card(self) -> VGroup:
        box = RoundedRectangle(
            width=4.2,
            height=1.6,
            corner_radius=0.18,
            stroke_color=BLUE_E,
            stroke_width=2,
            fill_color=WHITE,
            fill_opacity=0.88,
        )
        title = Text(self.card_title, font_size=26, color=BLACK)
        body = Text(self.card_body, font_size=18, color=GRAY_D)
        body.next_to(title, DOWN, buff=0.12)
        content = VGroup(title, body).move_to(box.get_center())
        card = VGroup(box, content)
        card.to_corner(UR, buff=0.55)
        return card

    def _build_badge(self) -> VGroup:
        badge = RoundedRectangle(
            width=3.6,
            height=0.82,
            corner_radius=0.2,
            stroke_color=BLUE_E,
            stroke_width=2,
            fill_color=WHITE,
            fill_opacity=0.9,
        )
        label = Text(self.final_label, font_size=22, color=BLACK)
        label.move_to(badge.get_center())
        group = VGroup(badge, label)
        group.to_edge(DOWN, buff=0.55)
        return group


class StepRevealIntroScene(BaseStepRevealScene):
    headline = "Step Reveal Sequence"
    subtitle = "Start with a single motion and let the later slides add the narrative."
    card_title = ""
    card_body = ""
    final_label = ""


class StepRevealContextScene(BaseStepRevealScene):
    headline = "Step 1: Add context"
    subtitle = "The same motion now carries supporting explanation."
    card_title = "Why this matters"
    card_body = "Reusing the same asset keeps the explanation visually stable."
    final_label = ""


class StepRevealWrapScene(BaseStepRevealScene):
    headline = "Step 2: Close the loop"
    subtitle = "The final slide reuses the motion but shifts the emphasis to the outcome."
    card_title = "What changed"
    card_body = "The narrative now points at the result instead of the setup."
    final_label = "Ready for the slide narrative"


def main() -> int:
    args = parse_args()
    for variant_name in VARIANTS:
        result = run_variant(args, variant_name)
        if result != 0:
            return result
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
