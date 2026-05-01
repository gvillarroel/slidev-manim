#!/usr/bin/env -S uv run --script
# /// script
# dependencies = [
#   "manim>=0.20.0",
# ]
# ///

from __future__ import annotations

import argparse
import shutil
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path

from manim import (
    DOWN,
    LEFT,
    RIGHT,
    TAU,
    UP,
    AnimationGroup,
    Arrow,
    Circle,
    Create,
    CurvedArrow,
    DoubleArrow,
    FadeIn,
    FadeOut,
    GrowArrow,
    Rectangle,
    Scene,
    Succession,
    Text,
    VGroup,
    rate_functions,
    smooth,
)

SPIKE_DIR = Path(__file__).resolve().parent
REPO_ROOT = SPIKE_DIR.parent.parent
SPIKE_NAME = SPIKE_DIR.name
OUTPUT_DIR = REPO_ROOT / "videos" / SPIKE_NAME
STAGING_DIR = OUTPUT_DIR / ".manim"

PRIMARY_RED = "#9e1b32"
PRIMARY_BLUE = "#007298"
PRIMARY_PURPLE = "#652f6c"
BLACK = "#000000"
WHITE = "#ffffff"
GRAY = "#333e48"
GRAY_100 = "#e7e7e7"
GRAY_200 = "#cfcfcf"
GRAY_300 = "#b5b5b5"
GRAY_500 = "#828282"
GRAY_700 = "#4f4f4f"
GRAY_900 = "#1c1c1c"
PAGE_BACKGROUND = "#f7f7f7"

FONT = "Arial"


class _Args(argparse.Namespace):
    quality: str


def parse_args() -> _Args:
    parser = argparse.ArgumentParser(description="Render the grow-arrow-lab spike.")
    parser.add_argument("--quality", choices=("low", "medium", "high", "production", "4k"), default="medium")
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
        "-o",
        stem,
        "--media_dir",
        str(STAGING_DIR),
        str(Path(__file__).resolve()),
        "GrowArrowLabScene",
    ]
    if poster:
        command.insert(-2, "-s")
    return command


def promote(target_name: str, destination: Path) -> None:
    matches = sorted(STAGING_DIR.glob(f"**/{target_name}"))
    if not matches:
        raise FileNotFoundError(target_name)
    destination.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(matches[-1], destination)


def label(text: str, size: int = 22, color: str = GRAY) -> Text:
    return Text(text, font=FONT, font_size=size, color=color)


def code_label(text: str) -> Text:
    return Text(text, font="Consolas", font_size=19, color=GRAY_700)


def panel_box(width: float = 5.7, height: float = 2.45) -> Rectangle:
    return Rectangle(
        width=width,
        height=height,
        stroke_color=GRAY_200,
        stroke_width=2,
        fill_color=PAGE_BACKGROUND,
        fill_opacity=1,
    )


def marker(point, color: str, radius: float = 0.075) -> Circle:
    return Circle(radius=radius, stroke_width=0, fill_color=color, fill_opacity=1).move_to(point)


def ghost_copy(arrow) -> object:
    ghost = arrow.copy()
    ghost.set_color(GRAY_300)
    ghost.set_stroke(width=4, opacity=0.44)
    return ghost


@dataclass
class ArrowExample:
    panel: VGroup
    live_arrow: object
    ghost_arrow: object
    start_dot: Circle
    end_dot: Circle


def straight_example(center, title: str, code: str, arrow_color: str = GRAY_900) -> ArrowExample:
    box = panel_box().move_to(center)
    title_text = label(title, size=22, color=BLACK).move_to(box.get_top() + DOWN * 0.28).align_to(box, LEFT).shift(RIGHT * 0.26)
    code_text = code_label(code).next_to(title_text, DOWN, buff=0.08).align_to(title_text, LEFT)

    start = center + LEFT * 2.05 + DOWN * 0.16
    end = center + RIGHT * 2.05 + DOWN * 0.16
    arrow = Arrow(start=start, end=end, buff=0.14, stroke_width=7, tip_length=0.24, color=arrow_color)
    ghost = ghost_copy(arrow)
    start_dot = marker(start, PRIMARY_RED)
    end_dot = marker(end, GRAY_500)

    rail_label = VGroup(label("start", size=15, color=GRAY_700).next_to(start_dot, DOWN, buff=0.18), label("end", size=15, color=GRAY_500).next_to(end_dot, DOWN, buff=0.18))
    panel = VGroup(box, title_text, code_text, ghost, start_dot, end_dot, rail_label)
    return ArrowExample(panel=panel, live_arrow=arrow, ghost_arrow=ghost, start_dot=start_dot, end_dot=end_dot)


def point_color_example(center) -> ArrowExample:
    example = straight_example(
        center,
        "Point color",
        "point_color=PRIMARY_RED",
        arrow_color=PRIMARY_BLUE,
    )
    return example


def double_arrow_example(center) -> ArrowExample:
    box = panel_box().move_to(center)
    title_text = label("Double headed", size=22, color=BLACK).move_to(box.get_top() + DOWN * 0.28).align_to(box, LEFT).shift(RIGHT * 0.26)
    code_text = code_label("DoubleArrow(start, end)").next_to(title_text, DOWN, buff=0.08).align_to(title_text, LEFT)

    start = center + LEFT * 2.05 + DOWN * 0.18
    end = center + RIGHT * 2.05 + DOWN * 0.18
    arrow = DoubleArrow(start=start, end=end, buff=0.11, stroke_width=6, tip_length=0.22, color=GRAY_900)
    ghost = ghost_copy(arrow)
    start_dot = marker(start, PRIMARY_RED)
    end_dot = marker(end, GRAY_500)

    rail_label = VGroup(label("start", size=15, color=GRAY_700).next_to(start_dot, DOWN, buff=0.18), label("end", size=15, color=GRAY_500).next_to(end_dot, DOWN, buff=0.18))
    panel = VGroup(box, title_text, code_text, ghost, start_dot, end_dot, rail_label)
    return ArrowExample(panel=panel, live_arrow=arrow, ghost_arrow=ghost, start_dot=start_dot, end_dot=end_dot)


def curved_arrow_example(center) -> ArrowExample:
    box = panel_box().move_to(center)
    title_text = label("Curved route", size=22, color=BLACK).move_to(box.get_top() + DOWN * 0.28).align_to(box, LEFT).shift(RIGHT * 0.26)
    code_text = code_label("Create(CurvedArrow(...))").next_to(title_text, DOWN, buff=0.08).align_to(title_text, LEFT)

    start = center + LEFT * 1.95 + DOWN * 0.36
    end = center + RIGHT * 1.95 + DOWN * 0.36
    arrow = CurvedArrow(start_point=start, end_point=end, angle=-TAU / 5, stroke_width=6, tip_length=0.22, color=PRIMARY_PURPLE)
    ghost = ghost_copy(arrow)
    start_dot = marker(start, PRIMARY_RED)
    end_dot = marker(end, GRAY_500)

    rail_label = VGroup(label("start", size=15, color=GRAY_700).next_to(start_dot, DOWN, buff=0.18), label("end", size=15, color=GRAY_500).next_to(end_dot, DOWN, buff=0.18))
    panel = VGroup(box, title_text, code_text, ghost, start_dot, end_dot, rail_label)
    return ArrowExample(panel=panel, live_arrow=arrow, ghost_arrow=ghost, start_dot=start_dot, end_dot=end_dot)


class GrowArrowLabScene(Scene):
    def construct(self) -> None:
        self.camera.background_color = WHITE

        title = label("GrowArrow builds direction from the start point", size=31, color=BLACK).to_edge(UP, buff=0.38)
        rule = Rectangle(width=12.6, height=0.035, stroke_width=0, fill_color=GRAY_200, fill_opacity=1).next_to(title, DOWN, buff=0.2)
        subtitle = label("The arrow shape can change; the growth anchor stays the same.", size=19, color=GRAY_700).next_to(rule, DOWN, buff=0.16)

        examples = [
            straight_example(LEFT * 3.1 + UP * 1.2, "Straight arrow", "Arrow(start, end, buff=0.14)"),
            point_color_example(RIGHT * 3.1 + UP * 1.2),
            double_arrow_example(LEFT * 3.1 + DOWN * 1.72),
            curved_arrow_example(RIGHT * 3.1 + DOWN * 1.72),
        ]
        panels = VGroup(*(example.panel for example in examples))

        self.add(title, rule, subtitle, panels)
        self.wait(2.6)

        self.play(GrowArrow(examples[0].live_arrow), FadeOut(examples[0].ghost_arrow), run_time=2.2, rate_func=smooth)
        self.wait(0.9)

        self.play(
            GrowArrow(examples[1].live_arrow, point_color=PRIMARY_RED),
            FadeOut(examples[1].ghost_arrow),
            examples[1].start_dot.animate.scale(1.8),
            run_time=2.35,
            rate_func=rate_functions.ease_in_out_cubic,
        )
        self.play(examples[1].start_dot.animate.scale(1 / 1.8), run_time=0.4)
        self.wait(0.85)

        self.play(GrowArrow(examples[2].live_arrow), FadeOut(examples[2].ghost_arrow), run_time=2.25, rate_func=smooth)
        self.wait(0.95)

        self.play(Create(examples[3].live_arrow), FadeOut(examples[3].ghost_arrow), run_time=2.55, rate_func=smooth)
        self.wait(1.05)

        anchor_rings = VGroup(*(
            Circle(radius=0.18, color=PRIMARY_RED, stroke_width=3, fill_opacity=0).move_to(example.start_dot)
            for example in examples
        ))
        anchor_label = label("same growth anchor", size=22, color=PRIMARY_RED).move_to(DOWN * 0.22)
        anchor_rule = Rectangle(width=3.2, height=0.03, stroke_width=0, fill_color=PRIMARY_RED, fill_opacity=1).next_to(anchor_label, DOWN, buff=0.1)

        self.play(
            Succession(*(FadeIn(ring, scale=1.8) for ring in anchor_rings)),
            FadeIn(anchor_label),
            FadeIn(anchor_rule),
            run_time=2.9,
            rate_func=smooth,
        )
        self.wait(1.1)

        self.play(
            AnimationGroup(
                *(example.live_arrow.animate.set_stroke(width=8).set_color(PRIMARY_RED) for example in examples),
                lag_ratio=0.08,
            ),
            run_time=2.0,
            rate_func=rate_functions.ease_in_out_cubic,
        )
        self.wait(6.2)


def render_variant(args: _Args) -> None:
    video_path, poster_path = output_paths()
    result = subprocess.run(render_command(args, video_path.stem, poster=False), check=False)
    if result.returncode != 0:
        raise SystemExit(result.returncode)
    promote(video_path.name, video_path)
    result = subprocess.run(render_command(args, poster_path.stem, poster=True), check=False)
    if result.returncode != 0:
        raise SystemExit(result.returncode)
    promote(poster_path.name, poster_path)


def main() -> int:
    args = parse_args()
    render_variant(args)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
