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
    Arrow,
    Circle,
    FadeIn,
    FadeOut,
    GrowArrow,
    Line,
    ORIGIN,
    Rectangle,
    Scene,
    Text,
    VGroup,
    config,
    rate_functions,
)
from manimpango import list_fonts

SPIKE_FILE = Path(__file__).resolve()
SPIKE_DIR = SPIKE_FILE.parent
sys.path.insert(0, str(SPIKE_DIR.parent))

os.environ.setdefault("MERMAID_UNFOLD_SPIKE_FILE", str(SPIKE_FILE))
os.environ.setdefault("MERMAID_UNFOLD_SPIKE_DIR", str(SPIKE_DIR))
os.environ.setdefault("MERMAID_UNFOLD_TITLE", 'Block Diagram')
os.environ.setdefault("MERMAID_UNFOLD_FAMILY", 'Structure')

from mermaid_svg_unfold_engine import ensure_fragments, ensure_mermaid_assets, main

PRIMARY_RED = "#9e1b32"
PRIMARY_ORANGE = "#e77204"
PRIMARY_GREEN = "#45842a"
PRIMARY_BLUE = "#007298"
WHITE = "#ffffff"
GRAY = "#333e48"
GRAY_200 = "#cfcfcf"
GRAY_600 = "#696969"
PAGE_BACKGROUND = "#f7f7f7"
TEXT_FONT = "Open Sans" if "Open Sans" in list_fonts() else "Arial"

config.transparent = True
config.background_opacity = 0.0


class MermaidSvgUnfoldScene(Scene):
    def construct(self) -> None:
        self.camera.background_color = WHITE
        self.camera.background_opacity = 0.0
        svg_path, _png_path = ensure_mermaid_assets(force=os.environ.get("SPIKE_FORCE_MERMAID") == "1")
        ensure_fragments(svg_path, force=os.environ.get("SPIKE_FORCE_MERMAID") == "1")

        poster_mode = os.environ.get("SPIKE_RENDER_TARGET") == "poster"

        stage = self._stage_rails()

        lane = Line(LEFT * 4.92, RIGHT * 4.92, color=GRAY_200, stroke_width=2.2)
        lane.move_to(DOWN * 0.04)
        lane.set_z_index(-1)

        steps = [
            ("MMD", PRIMARY_RED, LEFT * 4.15),
            ("SVG", PRIMARY_BLUE, LEFT * 1.38),
            ("Parts", PRIMARY_GREEN, RIGHT * 1.38),
            ("Video", PRIMARY_ORANGE, RIGHT * 4.15),
        ]
        cards = VGroup(*(self._card(label, color).move_to(point + DOWN * 0.04) for label, color, point in steps))
        connectors = VGroup(
            *(
                Arrow(
                    cards[index].get_right() + RIGHT * 0.12,
                    cards[index + 1].get_left() + LEFT * 0.12,
                    buff=0,
                    color=GRAY_600,
                    stroke_width=3.4,
                    max_tip_length_to_length_ratio=0.14,
                )
                for index in range(len(cards) - 1)
            )
        )
        slots = VGroup(*(self._slot(card) for card in cards))
        slot_hints = VGroup(
            *(
                Text(label, font=TEXT_FONT, font_size=22, color=GRAY_600).move_to(card).set_opacity(0.34)
                for (label, _color, _point), card in zip(steps, cards)
            )
        )

        if poster_mode:
            terminal = self._terminal(cards[-1]).set_opacity(0.36)
            self.add(stage, lane, connectors, cards, terminal)
            return

        route_scaffold = connectors.copy().set_opacity(0.18)
        self.add(stage, lane)
        self.add(slots, slot_hints, route_scaffold)
        self.wait(2.6)

        elapsed = 2.6
        self.play(
            FadeOut(slots[0], run_time=0.2),
            FadeOut(slot_hints[0], run_time=0.2),
            FadeIn(cards[0], shift=UP * 0.05),
            run_time=0.9,
            rate_func=rate_functions.ease_out_cubic,
        )
        self.wait(0.45)
        elapsed += 1.35

        active_dot = Circle(radius=0.082, color=PRIMARY_RED, fill_color=PRIMARY_RED, fill_opacity=1)
        active_dot.move_to(connectors[0].get_start() + RIGHT * 0.16)
        active_dot.set_z_index(9)

        visible_connectors = VGroup()
        for index in range(len(connectors)):
            target_slot = slots[index + 1]
            connector = connectors[index]
            self.play(
                target_slot.animate.set_stroke(PRIMARY_RED, opacity=0.72, width=3.2),
                run_time=0.34,
            )
            self.play(GrowArrow(connector), FadeIn(active_dot, scale=0.82), run_time=0.72)
            self.play(
                active_dot.animate.move_to(connector.get_end() + LEFT * 0.16),
                run_time=0.82,
                rate_func=rate_functions.ease_in_out_cubic,
            )
            self.play(
                FadeOut(target_slot, run_time=0.18),
                FadeOut(slot_hints[index + 1], run_time=0.18),
                FadeIn(cards[index + 1], shift=UP * 0.05),
                FadeOut(active_dot, scale=0.82),
                run_time=0.58,
                rate_func=rate_functions.ease_out_cubic,
            )
            self.play(
                cards[index + 1].animate.scale(1.035),
                run_time=0.22,
            )
            self.play(cards[index + 1].animate.scale(1 / 1.035), run_time=0.18)
            visible_connectors.add(connector)
            if index + 1 < len(connectors):
                active_dot.move_to(connectors[index + 1].get_start() + RIGHT * 0.16)
            elapsed += 2.86

        self.wait(0.42)
        elapsed += 0.42

        terminal = self._terminal(cards[-1])

        self.play(
            FadeOut(route_scaffold),
            FadeOut(stage),
            FadeIn(terminal),
            run_time=0.95,
            rate_func=rate_functions.ease_out_cubic,
        )
        self.play(
            terminal.animate.scale(1.06).set_opacity(0.86),
            cards[-1].animate.scale(1.018),
            run_time=0.9,
            rate_func=rate_functions.ease_out_cubic,
        )
        self.play(
            terminal.animate.scale(1 / 1.06).set_opacity(0.62),
            cards[-1].animate.scale(1 / 1.018),
            run_time=0.32,
        )
        elapsed += 2.17
        self.wait(max(7.0, 25.6 - elapsed))

    def _card(self, label: str, color: str) -> VGroup:
        box = Rectangle(
            width=2.25,
            height=1.18,
            stroke_color=color,
            stroke_width=2.2,
            fill_color=color,
            fill_opacity=0.96,
        )
        text = Text(label, font=TEXT_FONT, font_size=34, color=WHITE)
        if text.width > box.width - 0.38:
            text.scale_to_fit_width(box.width - 0.38)
        text.move_to(box)
        group = VGroup(box, text)
        group.set_z_index(4)
        return group

    def _stage_rails(self) -> VGroup:
        rail_width = 11.6
        top = Line(LEFT * (rail_width / 2), RIGHT * (rail_width / 2), color=GRAY_200, stroke_width=2.2)
        bottom = top.copy()
        rails = VGroup(top, bottom).arrange(DOWN, buff=2.55)
        rails.move_to(DOWN * 0.04)
        rails.set_opacity(0.78)
        rails.set_z_index(-5)
        return rails

    def _slot(self, card: VGroup) -> Rectangle:
        slot = Rectangle(
            width=card.width + 0.22,
            height=card.height + 0.22,
            stroke_color=GRAY_200,
            stroke_width=2,
            fill_opacity=0,
        )
        slot.move_to(card)
        slot.set_z_index(1)
        return slot

    def _terminal(self, target: VGroup) -> VGroup:
        width = target.width + 1.18
        height = target.height + 1.02
        anchor = target.get_center()
        tick_x = 0.24
        tick_y = 0.22
        gap = 0.09
        terminal = VGroup()
        for x_sign in (-1, 1):
            for y_sign in (-1, 1):
                horizontal = Line(
                    anchor + RIGHT * (x_sign * (width / 2 - tick_x - gap)) + UP * (y_sign * height / 2),
                    anchor + RIGHT * (x_sign * (width / 2 - gap)) + UP * (y_sign * height / 2),
                    color=PRIMARY_RED,
                    stroke_width=4,
                )
                vertical = Line(
                    anchor + RIGHT * (x_sign * width / 2) + UP * (y_sign * (height / 2 - tick_y - gap)),
                    anchor + RIGHT * (x_sign * width / 2) + UP * (y_sign * (height / 2 - gap)),
                    color=PRIMARY_RED,
                    stroke_width=4,
                )
                terminal.add(horizontal, vertical)
        terminal.set_opacity(0.72)
        terminal.set_z_index(7)
        return terminal


if __name__ == "__main__":
    raise SystemExit(main())
