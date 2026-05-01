#!/usr/bin/env -S uv run --script
# /// script
# dependencies = [
#   "manim>=0.20.0",
#   "numpy>=2.0.0",
# ]
# ///

from __future__ import annotations

import argparse
import os
import shutil
import subprocess
import sys
from collections.abc import Callable
from pathlib import Path

import numpy as np
from manim import (
    DEGREES,
    DOWN,
    LEFT,
    ORIGIN,
    RIGHT,
    UP,
    AnimationGroup,
    ArrowVectorField,
    Axes,
    Circle,
    Dot,
    FadeIn,
    FadeOut,
    Line,
    MoveAlongPath,
    ParametricFunction,
    Rectangle,
    StreamLines,
    Surface,
    Text,
    ThreeDAxes,
    ThreeDScene,
    TracedPath,
    VGroup,
    ValueTracker,
    always_redraw,
    linear,
    smooth,
)

SPIKE_DIR = Path(__file__).resolve().parent
REPO_ROOT = SPIKE_DIR.parent.parent
SPIKE_NAME = SPIKE_DIR.name
OUTPUT_DIR = REPO_ROOT / "videos" / SPIKE_NAME
STAGING_DIR = OUTPUT_DIR / ".manim"
VIDEO_PATH = OUTPUT_DIR / f"{SPIKE_NAME}.webm"
POSTER_PATH = OUTPUT_DIR / f"{SPIKE_NAME}.png"

BLACK = "#000000"
WHITE = "#ffffff"
PAGE_BACKGROUND = "#f7f7f7"
PRIMARY_RED = "#9e1b32"
PRIMARY_ORANGE = "#e77204"
PRIMARY_YELLOW = "#f1c319"
PRIMARY_GREEN = "#45842a"
PRIMARY_BLUE = "#007298"
PRIMARY_PURPLE = "#652f6c"
GRAY = "#333e48"
GRAY_100 = "#e7e7e7"
GRAY_200 = "#cfcfcf"
GRAY_300 = "#b5b5b5"
GRAY_400 = "#9c9c9c"
GRAY_500 = "#828282"
GRAY_600 = "#696969"
GRAY_700 = "#4f4f4f"
HIGHLIGHT_PURPLE = "#f9ccff"
FONT = "Arial"


class _Args(argparse.Namespace):
    quality: str


def parse_args() -> _Args:
    parser = argparse.ArgumentParser(description="Render the Manim complex color lab spike.")
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
    command.append("-s" if poster else "--format=webm")
    if not poster:
        command.append("-t")
    command.extend([str(Path(__file__).resolve()), "ManimComplexColorLabScene"])
    return command


def promote(target_name: str, destination: Path) -> None:
    matches = sorted(STAGING_DIR.glob(f"**/{target_name}"))
    if not matches:
        raise FileNotFoundError(target_name)
    destination.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(matches[-1], destination)


def panel(center_x: float, label: str, accent: str) -> VGroup:
    body = Rectangle(
        width=3.82,
        height=5.18,
        stroke_color=GRAY_300,
        stroke_width=2,
        fill_color=WHITE,
        fill_opacity=0.0,
    ).move_to(RIGHT * center_x)
    rail = Rectangle(width=3.82, height=0.16, stroke_width=0, fill_color=accent, fill_opacity=1).move_to(
        body.get_top() + DOWN * 0.08
    )
    title = Text(label.upper(), font=FONT, font_size=22, weight="BOLD", color=GRAY_700).move_to(
        body.get_top() + DOWN * 0.42
    )
    return VGroup(body, rail, title)


def panel_highlight(center_x: float, accent: str) -> Rectangle:
    highlight = Rectangle(
        width=3.62,
        height=4.72,
        stroke_color=accent,
        stroke_width=3,
        fill_color=accent,
        fill_opacity=0.0,
    ).move_to(RIGHT * center_x + DOWN * 0.08)
    highlight.set_stroke(opacity=0.0)
    return highlight


def small_badge(text: str, color: str, position: np.ndarray) -> VGroup:
    label = Text(text, font=FONT, font_size=17, color=WHITE, weight="BOLD")
    box = Rectangle(
        width=max(label.width + 0.35, 0.86),
        height=0.36,
        stroke_width=0,
        fill_color=color,
        fill_opacity=1,
    ).move_to(position)
    label.move_to(box)
    return VGroup(box, label)


def surface_height(u: float, v: float) -> float:
    ripple = 0.46 * np.sin(1.5 * u) * np.cos(1.1 * v)
    ridge = 0.28 * np.exp(-0.55 * ((u - 0.7) ** 2 + (v + 0.4) ** 2))
    basin = -0.22 * np.exp(-0.65 * ((u + 0.65) ** 2 + (v - 0.55) ** 2))
    return ripple + ridge + basin


def make_surface_cluster() -> VGroup:
    axes = ThreeDAxes(
        x_range=[-2.2, 2.2, 1.1],
        y_range=[-2.2, 2.2, 1.1],
        z_range=[-0.8, 0.8, 0.4],
        x_length=3.0,
        y_length=2.9,
        z_length=1.75,
        axis_config={"color": GRAY_500, "stroke_width": 2, "include_tip": False},
    )
    surface = Surface(
        lambda u, v: axes.c2p(u, v, surface_height(u, v)),
        u_range=[-2.2, 2.2],
        v_range=[-2.2, 2.2],
        resolution=(18, 18),
        fill_opacity=0.9,
        stroke_color=WHITE,
        stroke_opacity=0.32,
        stroke_width=0.35,
    )
    surface.set_fill_by_value(
        axes=axes,
        colorscale=[
            (PRIMARY_PURPLE, -0.55),
            (PRIMARY_BLUE, -0.2),
            (PRIMARY_GREEN, 0.02),
            (PRIMARY_YELLOW, 0.22),
            (PRIMARY_ORANGE, 0.45),
            (PRIMARY_RED, 0.68),
        ],
        axis=2,
    )
    ridge = ParametricFunction(
        lambda t: axes.c2p(t, 0.35 * np.sin(1.4 * t), surface_height(t, 0.35 * np.sin(1.4 * t)) + 0.035),
        t_range=[-2.0, 2.0],
        color=BLACK,
        stroke_width=5,
    )
    cluster = VGroup(axes, surface, ridge)
    cluster.set_z_index(10)
    cluster.scale(0.62)
    cluster.move_to(LEFT * 4.25 + DOWN * 0.22)
    return cluster


def make_surface_icon() -> VGroup:
    center = LEFT * 4.14 + DOWN * 0.02
    base_band = Rectangle(
        width=2.36,
        height=1.36,
        stroke_color=GRAY_200,
        stroke_width=1.5,
        fill_color=WHITE,
        fill_opacity=0.52,
    ).move_to(DOWN * 0.02)
    contour_specs = [
        (PRIMARY_BLUE, -0.48, 0.05),
        (PRIMARY_GREEN, -0.26, 0.45),
        (PRIMARY_YELLOW, -0.02, 0.82),
        (PRIMARY_ORANGE, 0.24, 1.18),
        (PRIMARY_RED, 0.48, 1.52),
    ]
    contours = VGroup()
    for color, offset, phase in contour_specs:
        contours.add(
            ParametricFunction(
                lambda t, y_offset=offset, curve_phase=phase: np.array(
                    [t, y_offset + 0.12 * np.sin(2.4 * t + curve_phase), 0.0]
                ),
                t_range=[-1.08, 1.08],
                color=color,
                stroke_width=4,
            )
        )
    ridge = ParametricFunction(
        lambda t: np.array([t, 0.1 + 0.34 * np.sin(2.1 * t - 0.3), 0.0]),
        t_range=[-0.9, 0.9],
        color=BLACK,
        stroke_width=5,
    )
    mesh = VGroup(
        Line(LEFT * 1.12 + DOWN * 0.64, LEFT * 1.12 + UP * 0.64, color=GRAY_300, stroke_width=2),
        Line(ORIGIN + DOWN * 0.7, ORIGIN + UP * 0.72, color=GRAY_300, stroke_width=2),
        Line(RIGHT * 1.12 + DOWN * 0.64, RIGHT * 1.12 + UP * 0.64, color=GRAY_300, stroke_width=2),
    )
    icon = VGroup(base_band, mesh, contours, ridge)
    icon.move_to(center)
    icon.set_z_index(8)
    return icon


def make_field_icon() -> VGroup:
    spiral = VGroup()
    for phase, color, width in [
        (0.0, PRIMARY_BLUE, 3.2),
        (0.78, PRIMARY_GREEN, 2.9),
        (1.56, PRIMARY_ORANGE, 2.5),
    ]:
        arm = ParametricFunction(
            lambda t, curve_phase=phase: np.array(
                [
                    0.11 * t * np.cos(t + curve_phase),
                    0.08 * t * np.sin(t + curve_phase),
                    0.0,
                ]
            ),
            t_range=[0.8, 8.2],
            color=color,
            stroke_width=width,
        )
        arm.set_stroke(opacity=0.48)
        spiral.add(arm)
    guide = Circle(radius=0.86, stroke_color=GRAY_300, stroke_width=2.0, fill_opacity=0)
    guide.set_stroke(opacity=0.34)
    guide.set_fill(opacity=0.0)
    icon = VGroup(guide, spiral).scale(0.9).move_to(DOWN * 0.04)
    icon.set_z_index(8)
    return icon


def make_trace_icon() -> VGroup:
    center = RIGHT * 4.14 + DOWN * 0.02
    window = Rectangle(
        width=2.55,
        height=1.55,
        stroke_color=GRAY_200,
        stroke_width=1.8,
        fill_color=HIGHLIGHT_PURPLE,
        fill_opacity=0.08,
    )
    axis = Line(LEFT * 1.1, RIGHT * 1.1, color=GRAY_300, stroke_width=2)
    curve = ParametricFunction(
        lambda t: np.array([t, 0.34 * np.sin(3.6 * t) + 0.12 * np.cos(6.2 * t), 0.0]),
        t_range=[-1.05, 1.05],
        color=PRIMARY_PURPLE,
        stroke_width=4,
    )
    cursor = Dot(RIGHT * 0.52 + UP * 0.16, radius=0.055, color=PRIMARY_RED)
    icon = VGroup(window, axis, curve, cursor).move_to(center)
    window.set_stroke(opacity=0.5)
    window.set_fill(opacity=0.08)
    axis.set_stroke(opacity=0.42)
    curve.set_stroke(opacity=0.48)
    cursor.set_opacity(0.62)
    icon.set_z_index(8)
    return icon


def vector_function(point: np.ndarray) -> np.ndarray:
    x = point[0]
    y = point[1]
    return np.array(
        [
            -0.52 * y + 0.32 * np.sin(1.4 * x),
            0.5 * x + 0.26 * np.cos(1.7 * y),
            0.0,
        ]
    )


def make_field_cluster() -> VGroup:
    arrows = ArrowVectorField(
        vector_function,
        x_range=[-1.16, 1.17, 0.58],
        y_range=[-1.16, 1.17, 0.58],
        min_color_scheme_value=0.05,
        max_color_scheme_value=1.35,
        colors=[PRIMARY_BLUE, PRIMARY_GREEN, PRIMARY_YELLOW, PRIMARY_ORANGE, PRIMARY_RED],
        length_func=lambda norm: min(0.3, 0.2 + 0.13 * norm),
        opacity=0.72,
        vector_config={"stroke_width": 2.8, "max_tip_length_to_length_ratio": 0.25},
    )
    streams = StreamLines(
        vector_function,
        x_range=[-1.14, 1.14, 0.34],
        y_range=[-1.14, 1.14, 0.34],
        colors=[PRIMARY_BLUE, PRIMARY_GREEN, PRIMARY_YELLOW, PRIMARY_ORANGE],
        min_color_scheme_value=0.1,
        max_color_scheme_value=1.25,
        stroke_width=1.8,
        opacity=0.44,
        padding=0.08,
        virtual_time=2.2,
        max_anchors_per_line=26,
    )
    focus_ring = Circle(radius=0.56, stroke_color=PRIMARY_RED, stroke_width=4, fill_opacity=0).move_to(ORIGIN)
    focus_ring.set_stroke(opacity=0.0)
    focus_ring.set_fill(opacity=0.0)
    cluster = VGroup(streams, arrows, focus_ring)
    cluster.scale(0.86)
    cluster.move_to(DOWN * 0.12)
    return cluster


def make_trace_cluster() -> tuple[VGroup, ValueTracker, ValueTracker, Callable[[float, float], float]]:
    axes = Axes(
        x_range=[0, 6.4, 1.6],
        y_range=[-1.6, 1.6, 0.8],
        x_length=2.95,
        y_length=2.55,
        tips=False,
        axis_config={"color": GRAY_500, "stroke_width": 2},
    ).move_to(RIGHT * 4.14 + DOWN * 0.16)

    phase = ValueTracker(0.0)
    cursor = ValueTracker(0.0)

    def curve_y(x: float, p: float) -> float:
        return 0.65 * np.sin(1.75 * x + p) + 0.28 * np.cos(3.3 * x - 0.5 * p)

    envelope = Rectangle(
        width=3.18,
        height=2.84,
        stroke_color=GRAY_200,
        stroke_width=2,
        fill_color=HIGHLIGHT_PURPLE,
        fill_opacity=0.12,
    ).move_to(axes)

    graph = always_redraw(
        lambda: axes.plot(
            lambda x: curve_y(x, phase.get_value()),
            x_range=[0, 6.35],
            color=PRIMARY_PURPLE,
            stroke_width=5,
        )
    )
    driver = always_redraw(
        lambda: Dot(
            axes.c2p(cursor.get_value(), curve_y(cursor.get_value(), phase.get_value())),
            radius=0.095,
            color=PRIMARY_RED,
        )
    )
    cursor_line = always_redraw(
        lambda: Line(
            axes.c2p(cursor.get_value(), -1.35),
            axes.c2p(cursor.get_value(), 1.35),
            color=PRIMARY_RED,
            stroke_width=2.6,
        ).set_opacity(0.36)
    )
    trace = TracedPath(driver.get_center, stroke_color=PRIMARY_ORANGE, stroke_width=4.5, dissipating_time=3.2)
    reference = axes.plot(lambda x: 0.0, x_range=[0, 6.35], color=GRAY_300, stroke_width=3)

    return VGroup(envelope, axes, reference, graph, trace, cursor_line, driver), phase, cursor, curve_y


class ManimComplexColorLabScene(ThreeDScene):
    def add_frame_fixed(self, *mobjects) -> None:
        self.add_fixed_in_frame_mobjects(*mobjects)
        self.add(*mobjects)

    def construct(self) -> None:
        self.camera.background_color = WHITE
        self.camera.background_opacity = 0.0
        self.set_camera_orientation(phi=64 * DEGREES, theta=-48 * DEGREES, gamma=0)
        layout_shift = UP * 0.1

        stage = Rectangle(
            width=12.9,
            height=6.35,
            stroke_color=GRAY_200,
            stroke_width=2,
            fill_color=PAGE_BACKGROUND,
            fill_opacity=0.98,
        )
        slots = VGroup(
            panel(-4.14, "surface", PRIMARY_BLUE),
            panel(0.0, "field", PRIMARY_GREEN),
            panel(4.14, "trace", PRIMARY_PURPLE),
        )
        surface_highlight = panel_highlight(-4.14, PRIMARY_BLUE)
        field_highlight = panel_highlight(0.0, PRIMARY_GREEN)
        trace_highlight = panel_highlight(4.14, PRIMARY_PURPLE)
        surface_badges = VGroup(
            small_badge("z", PRIMARY_RED, LEFT * 5.36 + DOWN * 2.18),
            small_badge("mesh", GRAY_600, LEFT * 4.58 + DOWN * 2.18),
            small_badge("height", PRIMARY_BLUE, LEFT * 3.56 + DOWN * 2.18),
        )
        field_badges = VGroup(
            small_badge("speed", PRIMARY_GREEN, LEFT * 0.86 + DOWN * 2.18),
            small_badge("curl", PRIMARY_ORANGE, ORIGIN + DOWN * 2.18),
            small_badge("focus", PRIMARY_RED, RIGHT * 0.88 + DOWN * 2.18),
        )
        trace_badges = VGroup(
            small_badge("phase", PRIMARY_PURPLE, RIGHT * 3.54 + DOWN * 2.18),
            small_badge("cursor", PRIMARY_RED, RIGHT * 4.58 + DOWN * 2.18),
            small_badge("trail", PRIMARY_ORANGE, RIGHT * 5.44 + DOWN * 2.18),
        )

        surface_cluster = make_surface_cluster()
        surface_icon = make_surface_icon()
        field_icon = make_field_icon()
        trace_icon = make_trace_icon()
        field_cluster = make_field_cluster()
        trace_cluster, phase, cursor, _curve_y = make_trace_cluster()
        VGroup(
            stage,
            slots,
            surface_highlight,
            field_highlight,
            trace_highlight,
            surface_badges,
            field_badges,
            trace_badges,
            surface_icon,
            field_icon,
            trace_icon,
            surface_cluster,
            field_cluster,
            trace_cluster,
        ).shift(layout_shift)

        stage.set_z_index(-30)
        slots.set_z_index(-20)
        surface_highlight.set_z_index(-18)
        field_highlight.set_z_index(-18)
        trace_highlight.set_z_index(-18)
        surface_badges.set_z_index(30)
        field_badges.set_z_index(30)
        trace_badges.set_z_index(30)
        surface_highlight.set_fill(opacity=0.045)
        surface_highlight.set_stroke(opacity=0.75)

        self.add_frame_fixed(
            stage,
            slots,
            surface_highlight,
            field_highlight,
            trace_highlight,
            surface_badges,
            field_badges,
            trace_badges,
            surface_icon,
            field_icon,
            trace_icon,
        )
        surface_badges.set_opacity(0.0)
        field_badges.set_opacity(0.0)
        trace_badges.set_opacity(0.0)

        self.wait(2.6)
        self.play(surface_badges.animate.set_opacity(1.0), FadeOut(surface_icon), run_time=0.55)
        self.play(FadeIn(surface_cluster), run_time=0.6)
        self.play(surface_cluster.animate.scale(1.05).shift(DOWN * 0.04), run_time=3.8, rate_func=smooth)
        self.play(
            FadeOut(surface_cluster),
            FadeIn(surface_icon),
            surface_badges.animate.set_opacity(0.38),
            surface_highlight.animate.set_fill(opacity=0.0).set_stroke(opacity=0.0),
            field_highlight.animate.set_fill(opacity=0.045).set_stroke(opacity=0.75),
            run_time=0.7,
        )

        streams = field_cluster[0]
        arrows = field_cluster[1]
        focus_ring = field_cluster[2]
        streams.set_opacity(0.0)
        arrows.set_opacity(0.0)
        focus_ring.set_stroke(opacity=0.0)
        focus_ring.set_fill(opacity=0.0)
        self.add_frame_fixed(field_cluster)
        self.play(
            AnimationGroup(
                FadeOut(field_icon),
                streams.animate.set_opacity(0.52),
                arrows.animate.set_opacity(0.82),
                field_badges.animate.set_opacity(1.0),
                lag_ratio=0.12,
            ),
            run_time=1.0,
        )
        self.wait(1.4)
        self.play(focus_ring.animate.set_stroke(opacity=1.0).scale(1.24), run_time=0.9, rate_func=smooth)
        field_path = ParametricFunction(
            lambda t: np.array(
                [
                    0.68 * np.cos(t) * (1 - 0.08 * t / np.pi),
                    0.5 * np.sin(t) + 0.1 * np.sin(2 * t),
                    0.0,
                ]
            ),
            t_range=[0, 2.2 * np.pi],
            color=PRIMARY_RED,
            stroke_opacity=0,
        )
        field_path.move_to(DOWN * 0.08 + layout_shift)
        traveler = VGroup(
            Circle(radius=0.19, stroke_color=PRIMARY_RED, stroke_width=3.0, fill_opacity=0),
            Dot(radius=0.075, color=PRIMARY_RED),
        ).move_to(
            field_path.get_start()
        )
        self.add_frame_fixed(field_path, traveler)
        self.play(MoveAlongPath(traveler, field_path), run_time=2.2, rate_func=linear)
        self.play(
            FadeOut(traveler),
            focus_ring.animate.set_stroke(opacity=0.0).set_fill(opacity=0.0),
            field_badges.animate.set_opacity(0.4),
            field_highlight.animate.set_fill(opacity=0.0).set_stroke(opacity=0.0),
            trace_highlight.animate.set_fill(opacity=0.045).set_stroke(opacity=0.75),
            run_time=0.55,
        )

        self.add_frame_fixed(trace_cluster)
        self.play(
            FadeOut(trace_icon),
            trace_badges.animate.set_opacity(1.0),
            run_time=1.0,
        )
        self.play(
            phase.animate.set_value(1.75 * np.pi),
            cursor.animate.set_value(6.2),
            run_time=5.0,
            rate_func=smooth,
        )
        self.play(
            surface_badges.animate.set_opacity(0.82),
            field_badges.animate.set_opacity(0.82),
            trace_badges.animate.set_opacity(0.82),
            surface_highlight.animate.set_fill(opacity=0.028).set_stroke(opacity=0.38),
            field_highlight.animate.set_fill(opacity=0.028).set_stroke(opacity=0.38),
            trace_highlight.animate.set_fill(opacity=0.04).set_stroke(opacity=0.65),
            run_time=0.9,
        )
        self.wait(6.4)


def main() -> int:
    args = parse_args()
    if STAGING_DIR.exists():
        shutil.rmtree(STAGING_DIR)
    for poster in (False, True):
        env = {**os.environ, "SPIKE_RENDER_TARGET": "poster" if poster else "video"}
        result = subprocess.run(render_command(args, poster), check=False, env=env)
        if result.returncode != 0:
            return result.returncode
        promote((POSTER_PATH if poster else VIDEO_PATH).name, POSTER_PATH if poster else VIDEO_PATH)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
