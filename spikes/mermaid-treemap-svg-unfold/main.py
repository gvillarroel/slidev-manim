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
    AnimationGroup,
    Create,
    FadeIn,
    FadeOut,
    Indicate,
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
LEFT_OFFSET = (-2.15, 0, 0)
RIGHT_OFFSET = (3.05, 0, 0)


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


def _slot_for(box: VGroup) -> Rectangle:
    body = box[0]
    slot = Rectangle(
        width=body.width,
        height=body.height,
        stroke_color=GRAY_200,
        stroke_width=1.7,
        fill_color=WHITE,
        fill_opacity=0.22,
    )
    slot.move_to(body.get_center())
    slot.set_z_index(1)
    return slot


def _frame_header(frame: Rectangle, name: str, value: str, color: str) -> VGroup:
    label = Text(name, font=TEXT_FONT, font_size=18, color=color)
    total = Text(value, font=TEXT_FONT, font_size=18, color=color)
    header_y = frame.get_top()[1] - 0.26
    label.move_to((frame.get_left()[0] + 0.52, header_y, 0))
    total.move_to((frame.get_right()[0] - 0.24, header_y, 0))
    group = VGroup(label, total)
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

        title = Text("Mermaid Treemap SVG", font=TEXT_FONT, font_size=28, color=GRAY)
        subtitle = Text("generated, decomposed, unfolded", font=TEXT_FONT, font_size=15, color=PRIMARY_BLUE)
        title_group = VGroup(title, subtitle).arrange(DOWN, buff=0.10).to_edge(UP, buff=0.38)

        stage = Rectangle(
            width=12.25,
            height=6.00,
            stroke_color=GRAY_200,
            stroke_width=2,
            fill_color=WHITE,
            fill_opacity=0.76,
        )
        stage.move_to(ORIGIN + DOWN * 0.40)
        stage.set_z_index(-4)

        source_frame = Rectangle(
            width=6.45,
            height=4.25,
            stroke_color=PRIMARY_BLUE,
            stroke_width=3.2,
            fill_color=PRIMARY_BLUE,
            fill_opacity=0.12,
        ).move_to(ORIGIN + DOWN * 0.36 + LEFT_OFFSET)
        manim_frame = Rectangle(
            width=3.80,
            height=4.25,
            stroke_color=PRIMARY_GREEN,
            stroke_width=3.2,
            fill_color=PRIMARY_GREEN,
            fill_opacity=0.12,
        ).move_to(ORIGIN + DOWN * 0.36 + RIGHT_OFFSET)

        source_header = _frame_header(source_frame, "Mermaid SVG", "17", PRIMARY_BLUE)
        manim_header = _frame_header(manim_frame, "Manim", "10", PRIMARY_GREEN)

        source_y = source_frame.get_center()[1] - 0.22
        child_height = 3.32
        gap = 0.11
        x0 = source_frame.get_left()[0] + 0.19
        fragments = _filled_box(3.10, child_height, fill=PRIMARY_ORANGE, stroke=PRIMARY_ORANGE, label="Fragments", value="8")
        source = _filled_box(1.65, child_height, fill=PRIMARY_PURPLE, stroke=PRIMARY_PURPLE, label="Source", value="5")
        labels = _filled_box(1.28, child_height, fill=PRIMARY_YELLOW, stroke=PRIMARY_YELLOW, label="Labels", value="4", text_color=GRAY)
        fragments.move_to((x0 + fragments[0].width / 2, source_y, 0))
        source.move_to((fragments.get_right()[0] + gap + source[0].width / 2, source_y, 0))
        labels.move_to((source.get_right()[0] + gap + labels[0].width / 2, source_y, 0))

        right_x = manim_frame.get_center()[0]
        timing = _filled_box(3.42, 1.74, fill=PRIMARY_RED, stroke=PRIMARY_RED, label="Timing", value="6")
        review = _filled_box(3.42, 1.45, fill=PRIMARY_BLUE, stroke=PRIMARY_BLUE, label="Review", value="4")
        timing.move_to((right_x, manim_frame.get_center()[1] + 0.56, 0))
        review.move_to((right_x, manim_frame.get_center()[1] - 1.24, 0))

        source_slots = VGroup(*[_slot_for(box) for box in (fragments, source, labels)])
        manim_slots = VGroup(*[_slot_for(box) for box in (timing, review)])
        all_boxes = VGroup(fragments, source, labels, timing, review)
        final_group = VGroup(source_frame, manim_frame, source_header, manim_header, all_boxes)

        if os.environ.get("SPIKE_RENDER_TARGET") == "poster":
            self.add(stage, title_group, source_frame, manim_frame, source_header, manim_header, all_boxes)
            return

        self.add(stage, title_group, source_frame, manim_frame, source_header, manim_header, source_slots, manim_slots)
        self.wait(2.6)

        self.play(
            AnimationGroup(Indicate(source_frame, color=PRIMARY_RED, scale_factor=1.015), Indicate(source_header, color=PRIMARY_RED, scale_factor=1.02)),
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
            AnimationGroup(Indicate(manim_frame, color=PRIMARY_RED, scale_factor=1.015), Indicate(manim_header, color=PRIMARY_RED, scale_factor=1.02)),
            run_time=1.0,
        )
        self.wait(0.35)

        for box, slot in ((timing, manim_slots[0]), (review, manim_slots[1])):
            outline = _active_outline(slot)
            self.play(Create(outline), run_time=0.38, rate_func=rate_functions.ease_out_cubic)
            self.play(FadeIn(box, scale=0.985), FadeOut(outline), run_time=0.82, rate_func=rate_functions.ease_out_cubic)
            self.remove(slot)
            self.wait(0.25)

        terminal = Rectangle(
            width=final_group.width + 0.34,
            height=final_group.height + 0.34,
            stroke_color=PRIMARY_RED,
            stroke_width=4.5,
            fill_opacity=0,
        )
        terminal.move_to(final_group.get_center())
        terminal.set_z_index(10)
        self.play(Create(terminal), run_time=0.80, rate_func=rate_functions.ease_out_cubic)
        self.play(FadeOut(terminal), final_group.animate.scale(1.012), run_time=0.75, rate_func=rate_functions.ease_out_cubic)
        self.play(final_group.animate.scale(1 / 1.012), run_time=0.30)

        self.wait(11.4)
if __name__ == "__main__":
    raise SystemExit(main())
