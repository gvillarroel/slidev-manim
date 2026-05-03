#!/usr/bin/env -S uv run --script
# /// script
# dependencies = [
#   "manim>=0.20.0",
# ]
# ///

from __future__ import annotations

import argparse
import math
import os
import shutil
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path

import numpy as np
from manim import (
    LEFT,
    RIGHT,
    UP,
    Circle,
    FadeIn,
    FadeOut,
    LaggedStart,
    Rectangle,
    RegularPolygon,
    Scene,
    Square,
    Star,
    Text,
    VGroup,
    rate_functions,
)
from manimpango import list_fonts

SPIKE_DIR = Path(__file__).resolve().parent
REPO_ROOT = SPIKE_DIR.parent.parent
SPIKE_NAME = SPIKE_DIR.name
OUTPUT_DIR = REPO_ROOT / "videos" / SPIKE_NAME
STAGING_DIR = OUTPUT_DIR / ".manim"
VIDEO_PATH = OUTPUT_DIR / f"{SPIKE_NAME}.webm"
POSTER_PATH = OUTPUT_DIR / f"{SPIKE_NAME}.png"

PRIMARY_RED = "#9e1b32"
DARK_RED = "#5f0d1e"
WHITE = "#ffffff"
GRAY = "#333e48"
GRAY_100 = "#e7e7e7"
GRAY_200 = "#cfcfcf"
GRAY_300 = "#b5b5b5"
GRAY_400 = "#9c9c9c"
GRAY_500 = "#828282"
GRAY_600 = "#696969"
GRAY_700 = "#4f4f4f"
GRAY_800 = "#363636"
PAGE_BACKGROUND = "#f7f7f7"

DEFAULT_ROOT_TEXT = "Generator"
FONT_FAMILY = "Open Sans" if "Open Sans" in list_fonts() else "Arial"


@dataclass(frozen=True)
class VariantSpec:
    label: str
    kind: str
    y: float
    bend: float
    count: int
    phase: float


class _Args(argparse.Namespace):
    quality: str
    preview: bool
    root_text: str


def parse_args() -> _Args:
    parser = argparse.ArgumentParser(description="Render a mind-map token-shape comparison spike.")
    parser.add_argument(
        "--quality",
        choices=("low", "medium", "high", "production", "4k"),
        default="medium",
        help="Manim quality preset. Defaults to medium for presentation review.",
    )
    parser.add_argument("--preview", action="store_true", help="Open the rendered output after rendering.")
    parser.add_argument("--root-text", default=DEFAULT_ROOT_TEXT, help="Text shown in the source box.")
    return parser.parse_args(namespace=_Args())


def quality_flag(quality: str) -> str:
    return {
        "low": "-ql",
        "medium": "-qm",
        "high": "-qh",
        "production": "-qp",
        "4k": "-qk",
    }[quality]


def render_command(args: _Args, poster: bool) -> list[str]:
    STAGING_DIR.mkdir(parents=True, exist_ok=True)
    target = POSTER_PATH if poster else VIDEO_PATH
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
        command.extend(["--format", "webm", "-t"])
    if args.preview:
        command.append("-p")
    command.extend([str(Path(__file__).resolve()), "MindMapShapeTokenLinesScene"])
    return command


def promote_rendered_file(target_name: str, destination: Path) -> None:
    matches = sorted(STAGING_DIR.glob(f"**/{target_name}"))
    if not matches:
        raise FileNotFoundError(f"Could not find {target_name} under {STAGING_DIR}")
    destination.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(max(matches, key=lambda path: path.stat().st_mtime), destination)


def text_box(
    label: str,
    width: float,
    height: float,
    fill: str,
    *,
    text_color: str = WHITE,
    stroke: str | None = None,
    font_size: int = 20,
    weight: str = "BOLD",
) -> VGroup:
    box = Rectangle(
        width=width,
        height=height,
        stroke_color=stroke or fill,
        stroke_width=1.6,
        fill_color=fill,
        fill_opacity=1,
    )
    text = Text(label, font=FONT_FAMILY, font_size=font_size, weight=weight, color=text_color)
    max_width = width * 0.78
    if text.width > max_width:
        text.scale(max_width / text.width)
    text.move_to(box.get_center())
    return VGroup(box, text)


def unit(vector: object) -> object:
    value = np.array(vector, dtype=float)
    norm = np.linalg.norm(value)
    return value if norm == 0 else value / norm


def normal_for(start: object, end: object) -> object:
    direction = unit(np.array(end) - np.array(start))
    return np.array([-direction[1], direction[0], 0.0])


def route_point(start: object, end: object, bend: float, t: float, phase: float) -> object:
    start_point = np.array(start)
    end_point = np.array(end)
    normal = normal_for(start_point, end_point)
    control = (start_point + end_point) / 2 + normal * bend
    base = ((1 - t) ** 2) * start_point + 2 * (1 - t) * t * control + (t**2) * end_point
    ripple = normal * (0.018 * math.sin(math.pi * t) * math.sin(phase + t * math.tau * 2.0))
    return base + ripple


def route_tangent(start: object, end: object, bend: float, t: float, phase: float) -> object:
    low = max(0.0, t - 0.018)
    high = min(1.0, t + 0.018)
    return unit(route_point(start, end, bend, high, phase) - route_point(start, end, bend, low, phase))


def token_stroke_for(color: str) -> str:
    return DARK_RED if color == PRIMARY_RED else GRAY_500


def token_stroke_width(opacity: float) -> float:
    return 1.05 if opacity >= 0.5 else 0.45


def token_stroke_opacity(opacity: float) -> float:
    if opacity >= 0.5:
        return min(0.9, opacity * 0.8 + 0.12)
    return opacity * 0.68


def settled_opacity_for(kind: str) -> float:
    return {
        "rectangles": 0.25,
        "squares": 0.22,
        "triangles": 0.24,
        "stars": 0.18,
        "circles": 0.22,
    }.get(kind, 0.22)


def style_token(shape: object, color: str, opacity: float, z_index: int) -> object:
    shape.set_fill(color, opacity=opacity)
    shape.set_stroke(
        color=token_stroke_for(color),
        width=token_stroke_width(opacity),
        opacity=token_stroke_opacity(opacity),
    )
    shape.set_z_index(z_index)
    return shape


def shape_token(
    kind: str,
    center: object,
    tangent: object,
    normal: object,
    index: int,
    color: str,
    opacity: float,
    z_index: int,
) -> object:
    tangent_vector = unit(tangent)
    normal_vector = unit(normal)
    side_pattern = (0.0, 0.7, -0.7, 0.32, -0.32)
    side = side_pattern[index % len(side_pattern)]
    position = np.array(center) + normal_vector * side * 0.045
    angle = math.atan2(tangent_vector[1], tangent_vector[0])

    if kind == "rectangles":
        shape = Rectangle(width=0.22, height=0.065)
        shape.rotate(angle)
    elif kind == "squares":
        shape = Square(side_length=0.105)
        shape.rotate(((index % 3) - 1) * 0.055)
    elif kind == "triangles":
        shape = RegularPolygon(n=3, radius=0.105)
        shape.rotate(angle - math.pi / 2)
    elif kind == "stars":
        shape = Star(n=5, outer_radius=0.11, inner_radius=0.049, density=2)
        shape.rotate(angle * 0.45 + index * 0.17)
    elif kind == "circles":
        shape = Circle(radius=0.068)
    else:
        shape = Rectangle(width=0.14, height=0.08)

    style_token(shape, color, opacity, z_index)
    shape.move_to(position)
    return shape


def token_line(
    start: object,
    end: object,
    bend: float,
    count: int,
    kind: str,
    color: str,
    opacity: float,
    z_index: int,
    phase: float,
    *,
    t_min: float = 0.0,
    t_max: float = 1.0,
) -> VGroup:
    tokens = VGroup()
    span = t_max - t_min
    for index in range(count):
        t = t_min + ((index + 1) / (count + 1)) * span
        center = route_point(start, end, bend, t, phase)
        tangent = route_tangent(start, end, bend, t, phase)
        normal = normal_for(start, end)
        tokens.add(shape_token(kind, center, tangent, normal, index, color, opacity, z_index))
    return tokens


def pending_route_hint(start: object, end: object, spec: VariantSpec) -> VGroup:
    starter = token_line(
        start,
        end,
        spec.bend,
        max(7, min(11, spec.count // 4)),
        spec.kind,
        GRAY_300,
        0.14 if spec.kind != "stars" else 0.1,
        -3,
        spec.phase,
        t_min=0.02,
        t_max=0.28,
    )
    receiver = token_line(
        start,
        end,
        spec.bend,
        4,
        spec.kind,
        GRAY_300,
        0.11 if spec.kind != "stars" else 0.08,
        -3,
        spec.phase,
        t_min=0.88,
        t_max=0.98,
    )
    return VGroup(starter, receiver)


def bud(center: object, radius: float, color: str, opacity: float, z_index: int) -> Circle:
    shape = Circle(radius=radius, stroke_width=0, fill_color=color, fill_opacity=opacity)
    shape.move_to(center)
    shape.set_z_index(z_index)
    return shape


def variants() -> tuple[VariantSpec, ...]:
    return (
        VariantSpec("Rectangles", "rectangles", 2.45, 0.38, 34, 0.1),
        VariantSpec("Squares", "squares", 1.22, 0.18, 40, 0.9),
        VariantSpec("Triangles", "triangles", 0.0, -0.08, 36, 1.7),
        VariantSpec("Stars", "stars", -1.22, -0.22, 30, 2.5),
        VariantSpec("Circles", "circles", -2.45, -0.36, 44, 3.2),
    )


class MindMapShapeTokenLinesScene(Scene):
    def construct(self) -> None:
        self.camera.background_color = PAGE_BACKGROUND

        stage = Rectangle(width=12.8, height=7.15, stroke_width=0, fill_color=PAGE_BACKGROUND, fill_opacity=0.96)
        stage.set_z_index(-10)
        stage_border = Rectangle(width=12.34, height=6.62, stroke_color=GRAY_200, stroke_width=2, fill_opacity=0)
        stage_border.set_z_index(-9)

        root = text_box(os.environ.get("MIND_MAP_ROOT_TEXT", DEFAULT_ROOT_TEXT), 2.35, 0.82, PRIMARY_RED, font_size=28)
        root.move_to(LEFT * 4.55)
        root.set_z_index(6)
        source = root.get_right() + RIGHT * 0.38
        seed = bud(root.get_right() + RIGHT * 0.25, 0.066, PRIMARY_RED, 1, 8)

        variant_specs = variants()
        cards = VGroup()
        pending = VGroup()
        starts: list[object] = []
        ends: list[object] = []
        for index, spec in enumerate(variant_specs):
            card = text_box(spec.label, 1.58, 0.43, WHITE, text_color=GRAY, stroke=GRAY_500, font_size=15, weight="NORMAL")
            card.move_to(RIGHT * 4.22 + UP * spec.y)
            card[0].set_fill(GRAY_100, opacity=0.86)
            card[0].set_stroke(GRAY_400, width=1.15, opacity=0.58)
            card.set_z_index(5)
            cards.add(card)

            start = source + UP * spec.y * 0.018
            end = card.get_left() + LEFT * 0.24
            starts.append(start)
            ends.append(end)
            pending.add(pending_route_hint(start, end, spec))

        self.add(stage, stage_border, pending, cards, root, seed)
        self.wait(2.7)

        active_lines = VGroup()
        for index, spec in enumerate(variant_specs):
            card = cards[index]
            start = starts[index]
            end = ends[index]
            active = token_line(start, end, spec.bend, spec.count, spec.kind, PRIMARY_RED, 0.92, 3, spec.phase)
            active_lines.add(active)
            terminal = bud(end, 0.06, PRIMARY_RED, 1, 8)
            settled_opacity = settled_opacity_for(spec.kind)

            self.play(
                FadeOut(pending[index]),
                card[0].animate.set_stroke(PRIMARY_RED, width=1.8, opacity=0.78).set_fill(WHITE, opacity=1),
                LaggedStart(*[FadeIn(token, scale=0.18) for token in active], lag_ratio=0.032),
                FadeIn(terminal, scale=0.55),
                run_time=1.05,
                rate_func=rate_functions.ease_out_cubic,
            )
            self.play(
                FadeOut(terminal, scale=1.35),
                card[0].animate.set_stroke(GRAY_600, width=1.25, opacity=0.7).set_fill(GRAY_100, opacity=0.95),
                *[
                    token.animate.scale(0.86)
                    .set_fill(GRAY_300, opacity=settled_opacity)
                    .set_stroke(color=GRAY_500, opacity=min(0.34, settled_opacity + 0.06), width=0.5)
                    for token in active
                ],
                run_time=0.52,
                rate_func=rate_functions.ease_out_cubic,
            )
            self.wait(0.22)

        pulse = bud(seed.get_center(), 0.14, PRIMARY_RED, 0.85, 9)
        self.play(FadeIn(pulse, scale=0.7), run_time=0.2)
        self.play(
            pulse.animate.scale(2.7).set_fill(PRIMARY_RED, opacity=0),
            *[
                token.animate.set_fill(GRAY_300, opacity=settled_opacity_for(spec.kind)).set_stroke(
                    color=GRAY_500,
                    opacity=min(0.34, settled_opacity_for(spec.kind) + 0.06),
                    width=0.45,
                )
                for spec, line in zip(variant_specs, active_lines)
                for token in line
            ],
            run_time=0.8,
            rate_func=rate_functions.ease_out_cubic,
        )
        self.remove(pulse)
        self.play(
            root.animate.scale(1.012),
            *[card.animate.scale(1.012) for card in cards],
            run_time=0.36,
            rate_func=rate_functions.there_and_back,
        )

        elapsed_before_hold = 2.7 + len(variant_specs) * (1.05 + 0.52 + 0.22) + 1.36
        self.wait(max(7.0, 26.0 - elapsed_before_hold))


def render_variant(args: _Args) -> int:
    env = {
        **os.environ,
        "MIND_MAP_ROOT_TEXT": args.root_text,
    }
    for poster in (False, True):
        result = subprocess.run(render_command(args, poster), check=False, env=env)
        if result.returncode != 0:
            return result.returncode
        promote_rendered_file((POSTER_PATH if poster else VIDEO_PATH).name, POSTER_PATH if poster else VIDEO_PATH)
    return 0


def main() -> int:
    return render_variant(parse_args())


if __name__ == "__main__":
    raise SystemExit(main())
