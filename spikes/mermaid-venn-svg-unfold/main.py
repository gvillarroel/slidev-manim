#!/usr/bin/env -S uv run --script
# /// script
# dependencies = [
#   "manim>=0.20.0",
# ]
# ///

from __future__ import annotations

import math
import os
import sys
from pathlib import Path

SPIKE_FILE = Path(__file__).resolve()
SPIKE_DIR = SPIKE_FILE.parent
sys.path.insert(0, str(SPIKE_DIR.parent))

os.environ.setdefault("MERMAID_UNFOLD_SPIKE_FILE", str(SPIKE_FILE))
os.environ.setdefault("MERMAID_UNFOLD_SPIKE_DIR", str(SPIKE_DIR))
os.environ.setdefault("MERMAID_UNFOLD_TITLE", 'Venn Diagram')
os.environ.setdefault("MERMAID_UNFOLD_FAMILY", 'Chart')

from manim import (
    DOWN,
    LEFT,
    RIGHT,
    UP,
    AnimationGroup,
    Circle,
    FadeIn,
    FadeOut,
    Group,
    Line,
    Rectangle,
    VGroup,
    VMobject,
    rate_functions,
)

from mermaid_svg_unfold_engine import (
    GRAY,
    GRAY_200,
    PAGE_BACKGROUND,
    PRIMARY_BLUE,
    PRIMARY_GREEN,
    PRIMARY_RED,
    WHITE,
    MermaidSvgUnfoldScene as _BaseMermaidSvgUnfoldScene,
    build_title,
    ensure_fragments,
    ensure_mermaid_assets,
    env_value,
    main,
)


def lens_shape(radius: float, half_distance: float, samples: int = 56) -> VMobject:
    lens_half_height = math.sqrt(radius * radius - half_distance * half_distance)
    theta = math.atan2(lens_half_height, half_distance)
    left_center = (-half_distance, 0.0, 0.0)
    right_center = (half_distance, 0.0, 0.0)

    points: list[tuple[float, float, float]] = []
    for index in range(samples + 1):
        alpha = theta - (2 * theta * index / samples)
        points.append(
            (
                left_center[0] + radius * math.cos(alpha),
                radius * math.sin(alpha),
                0.0,
            )
        )
    for index in range(samples + 1):
        alpha = math.pi + theta - (2 * theta * index / samples)
        points.append(
            (
                right_center[0] + radius * math.cos(alpha),
                radius * math.sin(alpha),
                0.0,
            )
        )

    lens = VMobject()
    lens.set_points_as_corners([*points, points[0]])
    return lens


class MermaidSvgUnfoldScene(_BaseMermaidSvgUnfoldScene):
    def construct(self) -> None:
        self.camera.background_color = PAGE_BACKGROUND
        poster_mode = env_value("SPIKE_RENDER_TARGET") == "poster"
        force_assets = env_value("SPIKE_FORCE_MERMAID") == "1"

        svg_path, _png_path = ensure_mermaid_assets(force=force_assets)
        ensure_fragments(svg_path, force=force_assets)

        stage = Rectangle(
            width=11.65,
            height=6.35,
            stroke_color=GRAY_200,
            stroke_width=2,
            fill_color=WHITE,
            fill_opacity=0.78,
        ).move_to(DOWN * 0.22)
        stage.set_z_index(-4)

        title = build_title()
        radius = 1.86
        half_distance = 0.86
        diagram_shift = DOWN * 0.25

        left_slot = Circle(radius=radius, stroke_color=GRAY_200, stroke_width=3, fill_opacity=0)
        right_slot = left_slot.copy()
        left_slot.shift(LEFT * half_distance + diagram_shift)
        right_slot.shift(RIGHT * half_distance + diagram_shift)
        center_slot = lens_shape(radius, half_distance)
        center_slot.set_stroke(PRIMARY_GREEN, width=2.4, opacity=0.38)
        center_slot.set_fill(opacity=0)
        center_slot.shift(diagram_shift)

        left_set = Circle(
            radius=radius,
            stroke_color=GRAY,
            stroke_width=2.8,
            fill_color=PRIMARY_RED,
            fill_opacity=0.9,
        ).shift(LEFT * half_distance + diagram_shift)
        right_set = Circle(
            radius=radius,
            stroke_color=GRAY,
            stroke_width=2.8,
            fill_color=PRIMARY_BLUE,
            fill_opacity=0.9,
        ).shift(RIGHT * half_distance + diagram_shift)
        overlap = lens_shape(radius, half_distance)
        overlap.set_stroke(GRAY, width=2.3, opacity=0.95)
        overlap.set_fill(PRIMARY_GREEN, opacity=0.92)
        overlap.shift(diagram_shift)

        corner_gap = 0.36
        final_bounds = Rectangle(width=4.95, height=4.18).move_to(diagram_shift)
        corners = Group(
            Line(final_bounds.get_corner(UP + LEFT), final_bounds.get_corner(UP + LEFT) + RIGHT * corner_gap),
            Line(final_bounds.get_corner(UP + LEFT), final_bounds.get_corner(UP + LEFT) + DOWN * corner_gap),
            Line(final_bounds.get_corner(UP + RIGHT), final_bounds.get_corner(UP + RIGHT) + LEFT * corner_gap),
            Line(final_bounds.get_corner(UP + RIGHT), final_bounds.get_corner(UP + RIGHT) + DOWN * corner_gap),
            Line(final_bounds.get_corner(DOWN + LEFT), final_bounds.get_corner(DOWN + LEFT) + RIGHT * corner_gap),
            Line(final_bounds.get_corner(DOWN + LEFT), final_bounds.get_corner(DOWN + LEFT) + UP * corner_gap),
            Line(final_bounds.get_corner(DOWN + RIGHT), final_bounds.get_corner(DOWN + RIGHT) + LEFT * corner_gap),
            Line(final_bounds.get_corner(DOWN + RIGHT), final_bounds.get_corner(DOWN + RIGHT) + UP * corner_gap),
        )
        for corner in corners:
            corner.set_stroke(PRIMARY_RED, width=4, opacity=0.72)
        corners.set_z_index(8)

        for index, mob in enumerate([left_set, right_set, overlap]):
            mob.set_z_index(2 + index)

        scaffold = VGroup(left_slot, right_slot, center_slot)

        if poster_mode:
            self.add(stage, title, left_set, right_set, overlap, corners)
            return

        self.add(stage, title, scaffold)
        self.wait(2.4)

        self.play(
            left_slot.animate.set_stroke(PRIMARY_RED, width=4, opacity=0.74),
            FadeIn(left_set, scale=0.92),
            run_time=1.55,
            rate_func=rate_functions.ease_out_cubic,
        )
        self.play(left_slot.animate.set_stroke(GRAY_200, width=3, opacity=0.48), run_time=0.25)
        self.wait(0.95)

        self.play(
            right_slot.animate.set_stroke(PRIMARY_RED, width=4, opacity=0.74),
            FadeIn(right_set, scale=0.92),
            run_time=1.55,
            rate_func=rate_functions.ease_out_cubic,
        )
        self.play(right_slot.animate.set_stroke(GRAY_200, width=3, opacity=0.48), run_time=0.25)
        self.wait(1.0)

        self.play(
            center_slot.animate.set_stroke(PRIMARY_RED, opacity=0.78, width=3.4),
            run_time=0.75,
        )
        self.play(
            FadeIn(overlap, scale=0.9),
            center_slot.animate.scale(1.03).set_stroke(opacity=0.42),
            run_time=1.55,
            rate_func=rate_functions.ease_out_cubic,
        )
        self.wait(1.3)

        self.play(
            FadeOut(left_slot),
            FadeOut(right_slot),
            FadeOut(center_slot),
            run_time=1.0,
        )
        self.play(
            AnimationGroup(
                left_set.animate.shift(RIGHT * 0.08),
                right_set.animate.shift(LEFT * 0.08),
                overlap.animate.scale(1.035),
                lag_ratio=0,
            ),
            run_time=0.75,
            rate_func=rate_functions.ease_out_cubic,
        )
        self.play(overlap.animate.scale(1 / 1.035), run_time=0.35)
        self.play(FadeIn(corners), run_time=0.7)
        self.wait(12.0)


if __name__ == "__main__":
    raise SystemExit(main())
