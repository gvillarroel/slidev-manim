#!/usr/bin/env -S uv run --script
# /// script
# dependencies = [
#   "manim>=0.20.0",
# ]
# ///

from __future__ import annotations

import os
import sys
from pathlib import Path

from manim import (
    DOWN,
    LEFT,
    RIGHT,
    UP,
    Create,
    Dot,
    FadeIn,
    FadeOut,
    Line,
    Rectangle,
    Text,
    VGroup,
    rate_functions,
)

SPIKE_FILE = Path(__file__).resolve()
SPIKE_DIR = SPIKE_FILE.parent
sys.path.insert(0, str(SPIKE_DIR.parent))

os.environ.setdefault("MERMAID_UNFOLD_SPIKE_FILE", str(SPIKE_FILE))
os.environ.setdefault("MERMAID_UNFOLD_SPIKE_DIR", str(SPIKE_DIR))
os.environ.setdefault("MERMAID_UNFOLD_TITLE", 'Kanban')
os.environ.setdefault("MERMAID_UNFOLD_FAMILY", 'Process')

import mermaid_svg_unfold_engine as _engine
from mermaid_svg_unfold_engine import (
    GRAY,
    GRAY_100,
    GRAY_200,
    PAGE_BACKGROUND,
    PRIMARY_BLUE,
    PRIMARY_GREEN,
    PRIMARY_RED,
    TEXT_FONT,
    WHITE,
    MermaidSvgUnfoldScene as _BaseMermaidSvgUnfoldScene,
    _Args,
    env_value,
)

CARD_W = 3.08
CARD_H = 0.72
COLUMN_W = 3.72
COLUMN_H = 3.86
HEADER_H = 0.7
TOP_Y = 1.95

_base_render_command = _engine.render_command


def render_command(args: _Args, stem: str, *, poster: bool) -> list[str]:
    command = _base_render_command(args, stem, poster=poster)
    if not poster and "-t" not in command and "--transparent" not in command:
        command.insert(-2, "-t")
    return command


_engine.render_command = render_command
main = _engine.main


def fit_label(label: Text, max_width: float, max_height: float) -> Text:
    if label.width > max_width:
        label.scale_to_fit_width(max_width)
    if label.height > max_height:
        label.scale_to_fit_height(max_height)
    return label


def build_card(text: str, accent: str) -> VGroup:
    body = Rectangle(
        width=CARD_W,
        height=CARD_H,
        stroke_color=GRAY_200,
        stroke_width=1.8,
        fill_color=WHITE,
        fill_opacity=1,
    )
    strip = Rectangle(
        width=0.11,
        height=CARD_H,
        stroke_width=0,
        fill_color=accent,
        fill_opacity=1,
    )
    strip.move_to(body.get_left() + RIGHT * 0.055)
    label = Text(text, font=TEXT_FONT, font_size=20, color=GRAY)
    fit_label(label, CARD_W - 0.42, CARD_H - 0.24)
    label.move_to(body.get_center() + RIGHT * 0.08)
    return VGroup(body, strip, label)


def build_slot(text: str) -> VGroup:
    outline = Rectangle(
        width=CARD_W,
        height=CARD_H,
        stroke_color=GRAY_200,
        stroke_width=1.6,
        fill_color=GRAY_100,
        fill_opacity=0.28,
    )
    label = Text(text, font=TEXT_FONT, font_size=18, color=GRAY)
    fit_label(label, CARD_W - 0.34, CARD_H - 0.26)
    label.move_to(outline)
    group = VGroup(outline, label)
    group.set_opacity(0.34)
    return group


def build_column(title: str, color: str, x: float) -> VGroup:
    panel = Rectangle(
        width=COLUMN_W,
        height=COLUMN_H,
        stroke_color=GRAY_200,
        stroke_width=2,
        fill_color=WHITE,
        fill_opacity=0.82,
    )
    panel.move_to([x, TOP_Y - COLUMN_H / 2, 0])
    header = Rectangle(
        width=COLUMN_W,
        height=HEADER_H,
        stroke_width=0,
        fill_color=color,
        fill_opacity=1,
    )
    header.move_to([x, TOP_Y - HEADER_H / 2, 0])
    label = Text(title, font=TEXT_FONT, font_size=24, color=WHITE)
    fit_label(label, COLUMN_W - 0.42, HEADER_H - 0.2)
    label.move_to(header)
    rail = Rectangle(
        width=COLUMN_W,
        height=0.07,
        stroke_width=0,
        fill_color=color,
        fill_opacity=0.86,
    )
    rail.move_to([x, TOP_Y - COLUMN_H + 0.08, 0])
    return VGroup(panel, header, label, rail)


def build_corner_brackets(target: VGroup, color: str = PRIMARY_RED) -> VGroup:
    box = Rectangle(width=target.width + 0.42, height=target.height + 0.36)
    box.move_to(target)
    length = 0.32
    corners = [
        (box.get_corner(UP + LEFT), RIGHT, DOWN),
        (box.get_corner(UP + RIGHT), LEFT, DOWN),
        (box.get_corner(DOWN + LEFT), RIGHT, UP),
        (box.get_corner(DOWN + RIGHT), LEFT, UP),
    ]
    strokes = []
    for corner, horizontal, vertical in corners:
        strokes.append(Line(corner, corner + horizontal * length, color=color, stroke_width=3))
        strokes.append(Line(corner, corner + vertical * length, color=color, stroke_width=3))
    return VGroup(*strokes)


class MermaidSvgUnfoldScene(_BaseMermaidSvgUnfoldScene):
    def construct(self) -> None:
        self.camera.background_color = PAGE_BACKGROUND
        self.camera.background_opacity = 0

        xs = [-4.15, 0.0, 4.15]
        columns = VGroup(
            build_column("Source", PRIMARY_RED, xs[0]),
            build_column("Render", PRIMARY_BLUE, xs[1]),
            build_column("Unfold", PRIMARY_GREEN, xs[2]),
        )

        source_card = build_card("diagram.mmd", PRIMARY_RED).move_to([xs[0], 0.55, 0])
        render_svg = build_card("diagram.svg", PRIMARY_BLUE).move_to([xs[1], 0.55, 0])
        render_png = build_card("reference.png", PRIMARY_BLUE).move_to([xs[1], -0.36, 0])
        unfold_fragments = build_card("SVG fragments", PRIMARY_GREEN).move_to([xs[2], 0.55, 0])
        unfold_video = build_card("Manim video", PRIMARY_GREEN).move_to([xs[2], -0.36, 0])

        render_svg_slot = build_slot("diagram.svg").move_to(render_svg)
        render_png_slot = build_slot("reference.png").move_to(render_png)
        unfold_fragments_slot = build_slot("SVG fragments").move_to(unfold_fragments)
        unfold_video_slot = build_slot("Manim video").move_to(unfold_video)
        slots = VGroup(render_svg_slot, render_png_slot, unfold_fragments_slot, unfold_video_slot)

        route_source_to_render = Line(
            source_card.get_right() + RIGHT * 0.16,
            render_svg_slot.get_left() + LEFT * 0.16,
            color=GRAY,
            stroke_width=2.2,
            stroke_opacity=0.28,
        )
        route_render_to_unfold = Line(
            render_png.get_right() + RIGHT * 0.16,
            unfold_video_slot.get_left() + LEFT * 0.16,
            color=GRAY,
            stroke_width=2.2,
            stroke_opacity=0.28,
        )
        routes = VGroup(route_source_to_render, route_render_to_unfold)

        final_cards = VGroup(source_card, render_svg, render_png, unfold_fragments, unfold_video)
        terminal_brackets = build_corner_brackets(unfold_video)

        if env_value("SPIKE_RENDER_TARGET") == "poster":
            self.add(columns, final_cards, terminal_brackets)
            return

        source_halo = build_corner_brackets(source_card).set_opacity(0.0)
        self.add(columns, slots, routes, source_card, source_halo)
        self.wait(2.6)

        pulse = Dot(source_card.get_right() + RIGHT * 0.18, radius=0.09, color=PRIMARY_RED)
        pulse.set_z_index(10)
        self.play(
            source_halo.animate.set_opacity(1),
            FadeIn(pulse, scale=0.7),
            run_time=0.65,
            rate_func=rate_functions.ease_out_cubic,
        )
        self.play(
            pulse.animate.move_to(route_source_to_render.get_end()),
            render_svg_slot[0].animate.set_stroke(PRIMARY_RED, width=2.8, opacity=0.84),
            render_png_slot[0].animate.set_stroke(PRIMARY_RED, width=2.8, opacity=0.84),
            run_time=1.75,
            rate_func=rate_functions.ease_in_out_cubic,
        )
        self.play(
            FadeOut(render_svg_slot),
            FadeOut(render_png_slot),
            run_time=0.32,
            rate_func=rate_functions.ease_out_cubic,
        )
        self.play(
            FadeOut(pulse, scale=0.7),
            FadeIn(render_svg, shift=UP * 0.05),
            FadeIn(render_png, shift=UP * 0.05),
            source_halo.animate.set_opacity(0.36),
            run_time=0.88,
            rate_func=rate_functions.ease_out_cubic,
        )
        self.wait(1.05)

        pulse = Dot(render_png.get_right() + RIGHT * 0.18, radius=0.09, color=PRIMARY_RED)
        pulse.set_z_index(10)
        render_halo = build_corner_brackets(VGroup(render_svg, render_png)).set_opacity(0.0)
        self.add(render_halo)
        self.play(
            render_halo.animate.set_opacity(1),
            FadeIn(pulse, scale=0.7),
            run_time=0.65,
            rate_func=rate_functions.ease_out_cubic,
        )
        self.play(
            pulse.animate.move_to(route_render_to_unfold.get_end()),
            unfold_fragments_slot[0].animate.set_stroke(PRIMARY_RED, width=2.8, opacity=0.84),
            unfold_video_slot[0].animate.set_stroke(PRIMARY_RED, width=2.8, opacity=0.84),
            run_time=1.75,
            rate_func=rate_functions.ease_in_out_cubic,
        )
        self.play(
            FadeOut(unfold_fragments_slot),
            FadeOut(unfold_video_slot),
            run_time=0.32,
            rate_func=rate_functions.ease_out_cubic,
        )
        self.play(
            FadeOut(pulse, scale=0.7),
            FadeIn(unfold_fragments, shift=UP * 0.05),
            FadeIn(unfold_video, shift=UP * 0.05),
            render_halo.animate.set_opacity(0.34),
            run_time=0.88,
            rate_func=rate_functions.ease_out_cubic,
        )
        self.wait(1.05)

        self.play(
            FadeOut(routes),
            FadeOut(source_halo),
            FadeOut(render_halo),
            Create(terminal_brackets),
            run_time=1.25,
            rate_func=rate_functions.ease_out_cubic,
        )
        self.play(
            terminal_brackets.animate.set_opacity(0.8),
            final_cards.animate.scale(1.012),
            run_time=0.7,
            rate_func=rate_functions.ease_out_cubic,
        )
        self.play(final_cards.animate.scale(1 / 1.012), run_time=0.35)
        self.wait(14.6)


if __name__ == "__main__":
    raise SystemExit(main())
