#!/usr/bin/env -S uv run --script
# /// script
# dependencies = [
#   "manim>=0.20.1",
# ]
# ///

from __future__ import annotations

import argparse
import os
import shutil
import subprocess
import sys
from pathlib import Path

from manimpango import list_fonts

from manim import (
    DOWN,
    LEFT,
    ORIGIN,
    RIGHT,
    UP,
    AnimationGroup,
    Arrow,
    Broadcast,
    Circle,
    Circumscribe,
    Create,
    Dot,
    FadeIn,
    FadeOut,
    Flash,
    Indicate,
    LaggedStart,
    Line,
    MoveAlongPath,
    Rectangle,
    Scene,
    ShowPassingFlash,
    Text,
    VGroup,
    Write,
    rate_functions,
)

SPIKE_DIR = Path(__file__).resolve().parent
REPO_ROOT = SPIKE_DIR.parent.parent
SPIKE_NAME = SPIKE_DIR.name
OUTPUT_DIR = REPO_ROOT / "videos" / SPIKE_NAME
STAGING_DIR = OUTPUT_DIR / ".manim"
VIDEO_PATH = OUTPUT_DIR / f"{SPIKE_NAME}.webm"
POSTER_PATH = OUTPUT_DIR / f"{SPIKE_NAME}.png"

PRIMARY_RED = "#9e1b32"
PRIMARY_GREEN = "#45842a"
PRIMARY_BLUE = "#007298"
BLACK = "#000000"
WHITE = "#ffffff"
GRAY = "#333e48"
GRAY_100 = "#e7e7e7"
GRAY_200 = "#cfcfcf"
GRAY_300 = "#b5b5b5"
GRAY_500 = "#828282"
GRAY_700 = "#4f4f4f"
PAGE_BACKGROUND = "#f7f7f7"
TEXT_FONT = "Open Sans" if "Open Sans" in list_fonts() else "Arial"


class _Args(argparse.Namespace):
    quality: str


def parse_args() -> _Args:
    parser = argparse.ArgumentParser(description="Render the manim-callout-reveal-lab spike.")
    parser.add_argument("--quality", choices=("low", "medium", "high", "production", "4k"), default="medium")
    return parser.parse_args(namespace=_Args())


def quality_flag(quality: str) -> str:
    return {
        "low": "-ql",
        "medium": "-qm",
        "high": "-qh",
        "production": "-qp",
        "4k": "-qk",
    }[quality]


def render_command(args: _Args, target: Path, *, poster: bool) -> list[str]:
    STAGING_DIR.mkdir(parents=True, exist_ok=True)
    command = [
        sys.executable,
        "-m",
        "manim",
        "render",
        quality_flag(args.quality),
        "-r",
        "1600,900",
        "-o",
        target.stem,
        "--media_dir",
        str(STAGING_DIR),
    ]
    if poster:
        command.append("-s")
    else:
        command.extend(["--format=webm", "-t"])
    command.extend([str(Path(__file__).resolve()), "CalloutRevealNarrationScene"])
    return command


def promote(target_name: str, destination: Path) -> None:
    matches = sorted(STAGING_DIR.glob(f"**/{target_name}"), key=lambda path: path.stat().st_mtime)
    if not matches:
        raise FileNotFoundError(target_name)
    destination.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(matches[-1], destination)


def label_text(text: str, *, max_width: float, font_size: int = 24, color: str = BLACK) -> Text:
    label = Text(text, font=TEXT_FONT, font_size=font_size, color=color, line_spacing=0.72)
    if label.width > max_width:
        label.scale_to_fit_width(max_width)
    return label


def card(label: str, x: float, y: float, *, accent: str = GRAY_500) -> VGroup:
    body = Rectangle(
        width=2.15,
        height=0.86,
        stroke_color=GRAY_300,
        stroke_width=2,
        fill_color=WHITE,
        fill_opacity=1,
    ).move_to(RIGHT * x + UP * y)
    bar = Rectangle(width=0.12, height=0.62, stroke_width=0, fill_color=accent, fill_opacity=1)
    bar.move_to(body.get_left() + RIGHT * 0.18)
    text = label_text(label, max_width=1.55, font_size=21, color=GRAY)
    text.move_to(body.get_center() + RIGHT * 0.16)
    return VGroup(body, bar, text)


class CalloutRevealNarrationScene(Scene):
    def is_poster(self) -> bool:
        return os.environ.get("SPIKE_RENDER_TARGET") == "poster"

    def construct(self) -> None:
        if self.is_poster():
            self.camera.background_color = WHITE

        stage = Rectangle(
            width=13.35,
            height=7.15,
            stroke_color=GRAY_200,
            stroke_width=2,
            fill_color=PAGE_BACKGROUND,
            fill_opacity=0.96,
        )
        title = label_text("Callout reveal", max_width=5.4, font_size=30, color=BLACK).move_to(UP * 3.14 + LEFT * 4.15)
        rule = Line(title.get_right() + RIGHT * 0.34, RIGHT * 5.72 + UP * 3.14, color=PRIMARY_RED, stroke_width=5)

        noisy_panel = Rectangle(width=5.05, height=4.25, stroke_color=GRAY_200, stroke_width=2, fill_color=WHITE, fill_opacity=0.72)
        noisy_panel.move_to(LEFT * 3.35 + DOWN * 0.2)
        guided_panel = Rectangle(width=5.05, height=4.25, stroke_color=GRAY_200, stroke_width=2, fill_color=WHITE, fill_opacity=0.72)
        guided_panel.move_to(RIGHT * 3.35 + DOWN * 0.2)

        noisy_label = label_text("decorative", max_width=2.2, font_size=18, color=GRAY_700).move_to(noisy_panel.get_top() + DOWN * 0.34)
        guided_label = label_text("receiver first", max_width=2.6, font_size=18, color=GRAY_700).move_to(guided_panel.get_top() + DOWN * 0.34)

        noisy_cards = VGroup(
            card("source", -4.45, 0.45, accent=GRAY_500),
            card("review", -3.35, -0.72, accent=GRAY_500),
            card("ship", -2.25, 0.45, accent=GRAY_500),
        )
        guided_cards = VGroup(
            card("source", 2.25, 0.45, accent=GRAY_500),
            card("review", 3.35, -0.72, accent=PRIMARY_BLUE),
            card("ship", 4.45, 0.45, accent=GRAY_500),
        )

        noisy_routes = VGroup(
            Arrow(noisy_cards[0].get_right(), noisy_cards[1].get_left(), buff=0.12, color=GRAY_300, stroke_width=3),
            Arrow(noisy_cards[1].get_right(), noisy_cards[2].get_left(), buff=0.12, color=GRAY_300, stroke_width=3),
        )
        guided_routes = VGroup(
            Arrow(guided_cards[0].get_right(), guided_cards[1].get_left(), buff=0.12, color=GRAY_300, stroke_width=3),
            Arrow(guided_cards[1].get_right(), guided_cards[2].get_left(), buff=0.12, color=GRAY_300, stroke_width=3),
        )

        receiver_slot = Rectangle(
            width=2.36,
            height=1.06,
            stroke_color=PRIMARY_RED,
            stroke_width=3,
            fill_opacity=0,
        ).move_to(guided_cards[1])
        receiver_slot.set_opacity(0.22)

        pulse_path = Line(guided_cards[0].get_right() + RIGHT * 0.12, guided_cards[1].get_left() + LEFT * 0.12)
        pulse = Dot(radius=0.105, color=PRIMARY_RED).move_to(pulse_path.get_start())
        terminal = Circle(radius=0.18, stroke_width=0, fill_color=PRIMARY_GREEN, fill_opacity=1).move_to(guided_cards[2].get_right() + RIGHT * 0.35)
        terminal_label = label_text("ok", max_width=0.72, font_size=19, color=BLACK).next_to(terminal, RIGHT, buff=0.13)
        terminal_group = VGroup(terminal, terminal_label)

        self.add(stage)
        self.play(
            FadeIn(title, shift=UP * 0.1),
            FadeIn(rule),
            FadeIn(noisy_panel),
            FadeIn(guided_panel),
            FadeIn(noisy_label),
            FadeIn(guided_label),
            FadeIn(receiver_slot),
            LaggedStart(FadeIn(noisy_cards), FadeIn(guided_cards), FadeIn(noisy_routes), FadeIn(guided_routes), lag_ratio=0.15),
            run_time=1.6,
        )
        self.wait(2.65)

        self.play(
            AnimationGroup(
                Flash(noisy_cards[0], color=PRIMARY_RED, line_length=0.26, num_lines=12, flash_radius=0.52),
                Flash(noisy_cards[1], color=PRIMARY_RED, line_length=0.26, num_lines=12, flash_radius=0.52),
                Flash(noisy_cards[2], color=PRIMARY_RED, line_length=0.26, num_lines=12, flash_radius=0.52),
                lag_ratio=0.08,
            ),
            run_time=2.6,
        )
        self.wait(0.8)
        self.play(noisy_cards.animate.set_opacity(0.46), noisy_routes.animate.set_opacity(0.22), run_time=0.75)

        self.play(receiver_slot.animate.set_opacity(0.58), FadeIn(pulse), run_time=0.55)
        self.wait(0.75)
        self.play(
            ShowPassingFlash(guided_routes[0].copy().set_color(PRIMARY_RED).set_stroke(width=6), time_width=0.35),
            MoveAlongPath(pulse, pulse_path),
            guided_cards[1][0].animate.set_stroke(PRIMARY_RED, width=3),
            run_time=3.4,
            rate_func=rate_functions.ease_in_out_cubic,
        )
        self.wait(0.8)

        self.play(
            Circumscribe(guided_cards[1], color=PRIMARY_RED, buff=0.14, stroke_width=6, fade_out=True),
            Indicate(guided_cards[1][1], color=PRIMARY_RED, scale_factor=1.1),
            run_time=2.7,
        )
        self.wait(0.75)

        self.play(
            Broadcast(
                Circle(radius=0.32, stroke_color=PRIMARY_RED, stroke_width=5, fill_opacity=0).move_to(guided_cards[1]),
                focal_point=guided_cards[1].get_center(),
                n_mobs=5,
                lag_ratio=0.14,
                initial_opacity=0.75,
                final_opacity=0,
                run_time=3.2,
            ),
            ShowPassingFlash(guided_routes[1].copy().set_color(PRIMARY_RED).set_stroke(width=6), time_width=0.32),
            guided_cards[2][1].animate.set_fill(PRIMARY_GREEN),
            run_time=3.2,
            rate_func=rate_functions.ease_in_out_cubic,
        )
        self.play(FadeIn(terminal), Write(terminal_label), run_time=0.9)
        self.wait(0.8)

        self.play(
            FadeOut(noisy_panel),
            FadeOut(noisy_label),
            FadeOut(noisy_cards),
            FadeOut(noisy_routes),
            FadeOut(receiver_slot),
            FadeOut(pulse),
            guided_panel.animate.move_to(ORIGIN + DOWN * 0.08).set_opacity(0.38),
            guided_label.animate.move_to(UP * 1.68 + LEFT * 1.0).set_color(GRAY),
            guided_cards.animate.shift(LEFT * 3.35),
            guided_routes.animate.shift(LEFT * 3.35).set_opacity(0.34),
            terminal_group.animate.shift(LEFT * 3.35),
            rule.animate.set_stroke(width=4),
            run_time=1.8,
        )
        self.play(guided_cards[1][0].animate.set_stroke(GRAY_300, width=2), run_time=0.5)
        self.wait(6.25)


def main() -> int:
    args = parse_args()
    for target, poster in ((VIDEO_PATH, False), (POSTER_PATH, True)):
        env = {**os.environ, "SPIKE_RENDER_TARGET": "poster" if poster else "video"}
        result = subprocess.run(render_command(args, target, poster=poster), check=False, env=env)
        if result.returncode != 0:
            return result.returncode
        promote(target.name, target)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
