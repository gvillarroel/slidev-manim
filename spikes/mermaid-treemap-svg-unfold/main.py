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
    ORIGIN,
    UP,
    Create,
    FadeIn,
    FadeOut,
    Indicate,
    Line,
    Rectangle,
    Scene,
    Text,
    VGroup,
    rate_functions,
)
from manimpango import list_fonts

SPIKE_FILE = Path(__file__).resolve()
SPIKE_DIR = SPIKE_FILE.parent
sys.path.insert(0, str(SPIKE_DIR.parent))

os.environ.setdefault("MERMAID_UNFOLD_SPIKE_FILE", str(SPIKE_FILE))
os.environ.setdefault("MERMAID_UNFOLD_SPIKE_DIR", str(SPIKE_DIR))
os.environ.setdefault("MERMAID_UNFOLD_TITLE", 'Treemap')
os.environ.setdefault("MERMAID_UNFOLD_FAMILY", 'Chart')

from mermaid_svg_unfold_engine import main

PRIMARY_RED = "#9e1b32"
PRIMARY_ORANGE = "#d45d00"
PRIMARY_YELLOW = "#f1b434"
PRIMARY_GREEN = "#4b8b3b"
PRIMARY_BLUE = "#007298"
PRIMARY_PURPLE = "#6f2c91"
WHITE = "#ffffff"
GRAY = "#333e48"
GRAY_200 = "#cfcfcf"
PAGE_BACKGROUND = "#f7f7f7"
TEXT_FONT = "Open Sans" if "Open Sans" in list_fonts() else "Arial"
SOURCE_CENTER_X = -2.15
MANIM_CENTER_X = 3.28


def _label_group(label: str, value: str, *, color: str, max_width: float, max_height: float) -> VGroup:
    label_text = Text(label, font=TEXT_FONT, font_size=24, color=color)
    value_text = Text(value, font=TEXT_FONT, font_size=23, color=color)
    group = VGroup(label_text, value_text).arrange(DOWN, buff=0.02)
    if group.width > max_width:
        group.scale_to_fit_width(max_width)
    if group.height > max_height:
        group.scale_to_fit_height(max_height)
    return group


def _filled_box(
    width: float,
    height: float,
    *,
    fill: str,
    stroke: str,
    label: str,
    value: str,
    text_color: str = WHITE,
) -> VGroup:
    body = Rectangle(
        width=width,
        height=height,
        stroke_color=stroke,
        stroke_width=2.4,
        fill_color=fill,
        fill_opacity=0.96,
    )
    label_group = _label_group(label, value, color=text_color, max_width=width * 0.78, max_height=height * 0.52)
    label_group.move_to(body.get_center())
    label_group.set_z_index(8)
    body.set_z_index(3)
    return VGroup(body, label_group)


def _slot_for(box: VGroup, color: str) -> Rectangle:
    body = box[0]
    slot = Rectangle(
        width=body.width,
        height=body.height,
        stroke_color=color,
        stroke_width=1.7,
        fill_color=color,
        fill_opacity=0.045,
    )
    slot.move_to(body.get_center())
    slot.set_z_index(1)
    return slot


def _section_header(center_x: float, top_y: float, width: float, name: str, value: str, color: str) -> VGroup:
    rule = Line(
        start=(center_x - width / 2, top_y, 0),
        end=(center_x + width / 2, top_y, 0),
        stroke_color=color,
        stroke_width=3.0,
    )
    label = Text(name, font=TEXT_FONT, font_size=18, color=color)
    total = Text(value, font=TEXT_FONT, font_size=18, color=color)
    header_y = top_y + 0.23
    label.move_to((center_x - width / 2 + 0.08 + label.width / 2, header_y, 0))
    total.move_to((center_x + width / 2 - 0.08 - total.width / 2, header_y, 0))
    group = VGroup(rule, label, total)
    group.set_z_index(7)
    return group


def _active_outline(target: VGroup | Rectangle) -> Rectangle:
    body = target[0] if isinstance(target, VGroup) else target
    outline = Rectangle(
        width=body.width + 0.12,
        height=body.height + 0.12,
        stroke_color=PRIMARY_RED,
        stroke_width=4.0,
        fill_opacity=0,
    )
    outline.move_to(body.get_center())
    outline.set_z_index(9)
    return outline


class MermaidSvgUnfoldScene(Scene):
    def construct(self) -> None:
        self.camera.background_color = PAGE_BACKGROUND

        title = Text("Mermaid Treemap", font=TEXT_FONT, font_size=28, color=GRAY)
        subtitle = Text("SVG generated, decomposed, unfolded", font=TEXT_FONT, font_size=15, color=PRIMARY_BLUE)
        title_group = VGroup(title, subtitle).arrange(DOWN, buff=0.10).to_edge(UP, buff=0.38)

        source_header = _section_header(SOURCE_CENTER_X, 1.36, 6.20, "Mermaid SVG", "17", PRIMARY_BLUE)
        manim_header = _section_header(MANIM_CENTER_X, 1.36, 3.70, "Manim", "10", PRIMARY_GREEN)

        source_y = -0.61
        child_height = 3.38
        gap = 0.18
        x0 = SOURCE_CENTER_X - 3.10
        fragments = _filled_box(2.95, child_height, fill=PRIMARY_ORANGE, stroke=PRIMARY_ORANGE, label="Fragments", value="8")
        source = _filled_box(1.55, child_height, fill=PRIMARY_PURPLE, stroke=PRIMARY_PURPLE, label="Source", value="5")
        labels = _filled_box(1.18, child_height, fill=PRIMARY_YELLOW, stroke=PRIMARY_YELLOW, label="Labels", value="4", text_color=GRAY)
        fragments.move_to((x0 + fragments[0].width / 2, source_y, 0))
        source.move_to((fragments.get_right()[0] + gap + source[0].width / 2, source_y, 0))
        labels.move_to((source.get_right()[0] + gap + labels[0].width / 2, source_y, 0))

        timing = _filled_box(3.45, 1.62, fill=PRIMARY_RED, stroke=PRIMARY_RED, label="Timing", value="6")
        review = _filled_box(3.45, 1.36, fill=PRIMARY_BLUE, stroke=PRIMARY_BLUE, label="Review", value="4")
        timing.move_to((MANIM_CENTER_X, 0.18, 0))
        review.move_to((MANIM_CENTER_X, -1.70, 0))

        source_slots = VGroup(*[_slot_for(box, PRIMARY_BLUE) for box in (fragments, source, labels)])
        manim_slots = VGroup(*[_slot_for(box, PRIMARY_GREEN) for box in (timing, review)])
        all_boxes = VGroup(fragments, source, labels, timing, review)
        final_group = VGroup(source_header, manim_header, all_boxes)

        if os.environ.get("SPIKE_RENDER_TARGET") == "poster":
            self.add(title_group, source_header, manim_header, all_boxes)
            return

        self.add(title_group, source_header, manim_header, source_slots, manim_slots)
        self.wait(2.6)

        self.play(
            Indicate(source_header, color=PRIMARY_RED, scale_factor=1.02),
            run_time=1.0,
        )
        self.wait(0.35)

        for box, slot in ((fragments, source_slots[0]), (source, source_slots[1]), (labels, source_slots[2])):
            outline = _active_outline(slot)
            self.play(Create(outline), run_time=0.38, rate_func=rate_functions.ease_out_cubic)
            self.play(FadeIn(box, scale=0.985), FadeOut(outline), run_time=0.82, rate_func=rate_functions.ease_out_cubic)
            self.remove(slot)
            self.wait(0.25)

        self.play(
            Indicate(manim_header, color=PRIMARY_RED, scale_factor=1.02),
            run_time=1.0,
        )
        self.wait(0.35)

        for box, slot in ((timing, manim_slots[0]), (review, manim_slots[1])):
            outline = _active_outline(slot)
            self.play(Create(outline), run_time=0.38, rate_func=rate_functions.ease_out_cubic)
            self.play(FadeIn(box, scale=0.985), FadeOut(outline), run_time=0.82, rate_func=rate_functions.ease_out_cubic)
            self.remove(slot)
            self.wait(0.25)

        self.wait(13.25)
if __name__ == "__main__":
    raise SystemExit(main())
