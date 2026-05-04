#!/usr/bin/env -S uv run --script
# /// script
# dependencies = [
#   "manim>=0.20.0",
# ]
# ///

from __future__ import annotations

import os
import sys
from dataclasses import dataclass
from pathlib import Path

from manim import (
    DOWN,
    LEFT,
    ORIGIN,
    RIGHT,
    UP,
    FadeIn,
    FadeOut,
    GrowFromEdge,
    Line,
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
os.environ.setdefault("MERMAID_UNFOLD_TITLE", "Packet Diagram")
os.environ.setdefault("MERMAID_UNFOLD_FAMILY", "Data")

from mermaid_svg_unfold_engine import ensure_fragments, ensure_mermaid_assets, main

PRIMARY_RED = "#9e1b32"
WHITE = "#ffffff"
GRAY = "#333e48"
GRAY_100 = "#e7e7e7"
GRAY_200 = "#cfcfcf"
GRAY_600 = "#696969"
GRAY_700 = "#4f5862"
GRAY_800 = "#333e48"
PAGE_BACKGROUND = "#f7f7f7"
TEXT_FONT = "Open Sans" if "Open Sans" in list_fonts() else "Arial"

config.transparent = True
config.background_opacity = 0.0


@dataclass(frozen=True)
class FieldSpec:
    name: str
    bit_range: str
    bit_count: int
    row: int
    color: str


FIELD_SPECS = (
    FieldSpec("Header", "0-7", 8, 0, PRIMARY_RED),
    FieldSpec("Type", "8-15", 8, 0, GRAY_800),
    FieldSpec("Fragment id", "16-31", 16, 0, GRAY_700),
    FieldSpec("Payload", "32-63", 32, 1, GRAY),
)


class MermaidSvgUnfoldScene(Scene):
    def construct(self) -> None:
        self.camera.background_color = PAGE_BACKGROUND
        self.camera.background_opacity = 0.0
        svg_path, _png_path = ensure_mermaid_assets(force=os.environ.get("SPIKE_FORCE_MERMAID") == "1")
        ensure_fragments(svg_path, force=os.environ.get("SPIKE_FORCE_MERMAID") == "1")

        poster_mode = os.environ.get("SPIKE_RENDER_TARGET") == "poster"
        stage = Rectangle(
            width=11.65,
            height=4.35,
            stroke_width=0,
            fill_color=WHITE,
            fill_opacity=0,
        )
        stage.move_to(DOWN * 0.06)
        stage.set_z_index(-6)

        slots, faint_labels, ticks, final_fields = self._build_packet()
        packet_frame = VGroup(slots, faint_labels, ticks, final_fields)
        packet_frame.move_to(ORIGIN + DOWN * 0.03)
        final_fields.set_opacity(1)
        slots.set_opacity(0)
        faint_labels.set_opacity(0)
        terminal = self._terminal_brackets(VGroup(final_fields, ticks))

        if poster_mode:
            self.add(stage, ticks, final_fields, terminal)
            return

        slots.set_opacity(1)
        faint_labels.set_opacity(1)
        self.add(stage, slots, faint_labels, ticks)
        self.wait(2.7)

        elapsed = 2.7
        cursor = self._scan_cursor(slots[0], slots[0].get_left()[0] + 0.03)
        cursor.set_z_index(8)

        for index, field in enumerate(final_fields):
            slot = slots[index]

            start_x = slot.get_left()[0] + 0.04
            end_x = slot.get_right()[0] - 0.04
            start_cursor = self._scan_cursor(slot, start_x)
            end_cursor = self._scan_cursor(slot, end_x)
            if index == 0:
                cursor.move_to(start_cursor)
                self.play(FadeIn(cursor), run_time=0.4)
                elapsed += 0.4
            else:
                if index == 3:
                    self.play(FadeOut(cursor), run_time=0.18)
                    cursor = start_cursor
                    cursor.set_z_index(8)
                    self.play(FadeIn(cursor), run_time=0.42)
                    elapsed += 0.6
                else:
                    self.play(cursor.animate.move_to(start_cursor), run_time=0.5)
                    elapsed += 0.5

            self.play(
                slots[index].animate.set_opacity(0),
                faint_labels[index].animate.set_opacity(0),
                run_time=0.18,
            )
            self.play(
                GrowFromEdge(field[0], LEFT),
                cursor.animate.move_to(end_cursor),
                run_time=1.05,
                rate_func=rate_functions.ease_out_cubic,
            )
            self.play(
                FadeIn(field[1], shift=UP * 0.03),
                FadeIn(field[2], shift=DOWN * 0.03),
                run_time=0.38,
            )
            self.wait(0.46)
            self.wait(0.24)
            elapsed += 2.31

        self.wait(0.55)
        elapsed += 0.55
        self.play(FadeOut(cursor), FadeOut(slots), FadeOut(faint_labels), run_time=0.75)
        self.play(FadeIn(terminal), run_time=0.75, rate_func=rate_functions.ease_out_cubic)
        self.play(
            terminal.animate.scale(1.015).set_opacity(0.76),
            final_fields.animate.scale(1.005),
            run_time=0.82,
            rate_func=rate_functions.ease_out_cubic,
        )
        self.play(
            terminal.animate.scale(1 / 1.015).set_opacity(0.62),
            final_fields.animate.scale(1 / 1.005),
            run_time=0.28,
        )
        elapsed += 2.6
        self.wait(max(7.0, 25.6 - elapsed))

    def _build_packet(self) -> tuple[VGroup, VGroup, VGroup, VGroup]:
        total_width = 11.15
        row_height = 1.04
        row_gap = 0.48
        top_y = row_height / 2 + row_gap / 2
        bottom_y = -row_height / 2 - row_gap / 2
        left = -total_width / 2

        slots = VGroup()
        faint_labels = VGroup()
        ticks = VGroup()
        fields = VGroup()

        top_cursor = left
        for spec in FIELD_SPECS:
            row_bits = 32
            width = total_width * spec.bit_count / row_bits
            if spec.row == 0:
                x = top_cursor + width / 2
                y = top_y
                top_cursor += width
            else:
                width = total_width
                x = 0
                y = bottom_y

            slot = Rectangle(
                width=width,
                height=row_height,
                stroke_color=GRAY_200,
                stroke_width=2.4,
                fill_opacity=0,
            )
            slot.move_to(RIGHT * x + UP * y)
            slot.set_z_index(1)
            slots.add(slot)

            faint_label = self._faint_field_label(spec, slot)
            faint_labels.add(faint_label)

            display_width = width - 0.34
            body = Rectangle(
                width=display_width,
                height=row_height,
                stroke_color=spec.color,
                stroke_width=2.4,
                fill_color=spec.color,
                fill_opacity=0.96,
            )
            body.move_to(slot)
            body.set_z_index(3)
            name = Text(spec.name, font=TEXT_FONT, font_size=31, color=WHITE)
            if name.width > body.width - 0.36:
                name.scale_to_fit_width(body.width - 0.36)
            name.move_to(body.get_center() + DOWN * 0.03)
            name.set_z_index(5)
            bit_range = Text(spec.bit_range, font=TEXT_FONT, font_size=18, color=WHITE)
            bit_range.align_to(body, LEFT)
            bit_range.align_to(body, UP)
            bit_range.shift(RIGHT * 0.14 + DOWN * 0.15)
            bit_range.set_z_index(5)
            fields.add(VGroup(body, name, bit_range))

        boundary_xs = [left, left + total_width * 0.25, left + total_width * 0.5, left + total_width]
        boundary_labels = ["0", "8", "16", "31"]
        boundary_ys = [top_y, top_y, top_y, top_y]
        for x, label, y in zip(boundary_xs, boundary_labels, boundary_ys):
            tick = Line(UP * 0.15, DOWN * 0.15, color=GRAY_600, stroke_width=2.4)
            tick.move_to(RIGHT * x + UP * (y + row_height / 2 + 0.18))
            number = Text(label, font=TEXT_FONT, font_size=17, color=GRAY_600)
            number.next_to(tick, UP, buff=0.06)
            ticks.add(tick, number)

        divider = Line(LEFT * total_width / 2, RIGHT * total_width / 2, color=GRAY_100, stroke_width=2)
        divider.move_to(DOWN * 0.01)
        divider.set_z_index(0)
        ticks.add(divider)
        return slots, faint_labels, ticks, fields

    def _faint_field_label(self, spec: FieldSpec, slot: Rectangle) -> VGroup:
        name = Text(spec.name, font=TEXT_FONT, font_size=27, color=GRAY_600)
        if name.width > slot.width - 0.36:
            name.scale_to_fit_width(slot.width - 0.36)
        name.move_to(slot.get_center() + DOWN * 0.03)
        bit_range = Text(spec.bit_range, font=TEXT_FONT, font_size=17, color=GRAY_600)
        bit_range.align_to(slot, LEFT)
        bit_range.align_to(slot, UP)
        bit_range.shift(RIGHT * 0.1 + DOWN * 0.13)
        label = VGroup(name, bit_range)
        label.set_opacity(0.38)
        label.set_z_index(2)
        return label

    def _scan_cursor(self, slot: Rectangle, x: float) -> VGroup:
        top_y = slot.get_top()[1]
        bottom_y = slot.get_bottom()[1]
        top = Line(
            RIGHT * x + UP * (top_y + 0.28),
            RIGHT * x + UP * (top_y + 0.04),
            color=PRIMARY_RED,
            stroke_width=5,
        )
        bottom = Line(
            RIGHT * x + UP * (bottom_y - 0.04),
            RIGHT * x + UP * (bottom_y - 0.28),
            color=PRIMARY_RED,
            stroke_width=5,
        )
        return VGroup(top, bottom)

    def _terminal_brackets(self, target: VGroup) -> VGroup:
        width = target.width + 0.72
        height = target.height + 0.52
        center = target.get_center()
        tick_x = 0.28
        tick_y = 0.18
        brackets = VGroup()
        for x_sign, y_sign in [(-1, 1), (1, 1), (-1, -1), (1, -1)]:
            corner = center + RIGHT * (x_sign * width / 2) + UP * (y_sign * height / 2)
            horizontal = Line(
                ORIGIN,
                RIGHT * (x_sign * tick_x),
                color=PRIMARY_RED,
                stroke_width=4,
            ).move_to(corner + RIGHT * (x_sign * tick_x / 2))
            vertical = Line(
                ORIGIN,
                UP * (y_sign * tick_y),
                color=PRIMARY_RED,
                stroke_width=4,
            ).move_to(corner + UP * (y_sign * tick_y / 2))
            brackets.add(horizontal, vertical)
        brackets.set_z_index(8)
        brackets.set_opacity(0.62)
        return brackets


if __name__ == "__main__":
    raise SystemExit(main())
