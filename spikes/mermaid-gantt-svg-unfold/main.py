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

SPIKE_FILE = Path(__file__).resolve()
SPIKE_DIR = SPIKE_FILE.parent
sys.path.insert(0, str(SPIKE_DIR.parent))

os.environ.setdefault("MERMAID_UNFOLD_SPIKE_FILE", str(SPIKE_FILE))
os.environ.setdefault("MERMAID_UNFOLD_SPIKE_DIR", str(SPIKE_DIR))
os.environ.setdefault("MERMAID_UNFOLD_TITLE", 'Gantt')
os.environ.setdefault("MERMAID_UNFOLD_FAMILY", 'Process')

from manim import (
    DOWN,
    LEFT,
    RIGHT,
    UP,
    AnimationGroup,
    Create,
    FadeIn,
    FadeOut,
    GrowFromEdge,
    Line,
    Rectangle,
    Scene,
    Text,
    VGroup,
    rate_functions,
)

from mermaid_svg_unfold_engine import (
    GRAY,
    GRAY_100,
    GRAY_200,
    PAGE_BACKGROUND,
    PRIMARY_BLUE,
    PRIMARY_GREEN,
    PRIMARY_ORANGE,
    PRIMARY_PURPLE,
    PRIMARY_RED,
    TEXT_FONT,
    WHITE,
    main,
)


class MermaidSvgUnfoldScene(Scene):
    def construct(self) -> None:
        self.camera.background_color = PAGE_BACKGROUND
        poster_mode = os.environ.get("SPIKE_RENDER_TARGET") == "poster"

        title = Text("Mermaid Gantt SVG", font=TEXT_FONT, font_size=30, color=GRAY)
        subtitle = Text("source to video timeline", font=TEXT_FONT, font_size=17, color=PRIMARY_BLUE)
        header = VGroup(title, subtitle).arrange(DOWN, buff=0.1).to_edge(UP, buff=0.42)

        stage = Rectangle(
            width=12.0,
            height=6.28,
            stroke_color=GRAY_200,
            stroke_width=2,
            fill_color=WHITE,
            fill_opacity=0.74,
        ).move_to(DOWN * 0.16)
        stage.set_z_index(-5)

        chart_left = -5.0
        chart_width = 10.0
        chart_top = 1.4
        chart_bottom = -1.96
        row_height = 0.42
        row_y = [0.74, 0.06, -0.62, -1.3]
        day_count = 6

        def day_x(day: float) -> float:
            return chart_left + chart_width * day / day_count

        grid = VGroup()
        for day in range(day_count + 1):
            stroke = 1.45 if day in {0, 2, 6} else 0.8
            line = Line(
                [day_x(day), chart_top, 0],
                [day_x(day), chart_bottom, 0],
                color=GRAY_200,
                stroke_width=stroke,
            )
            grid.add(line)

        axis = Line([day_x(0), chart_bottom, 0], [day_x(6), chart_bottom, 0], color=GRAY, stroke_width=2)
        tick_labels = VGroup()
        for day, label in [(0, "Jan 1"), (2, "Jan 3"), (4, "Jan 5"), (6, "Jan 7")]:
            tick = Text(label, font=TEXT_FONT, font_size=15, color=GRAY).move_to([day_x(day), chart_bottom - 0.28, 0])
            tick_labels.add(tick)

        section = Text("Build", font=TEXT_FONT, font_size=20, color=GRAY).move_to([chart_left - 0.48, -0.1, 0])
        section.set_z_index(4)

        tasks = [
            ("Source mmd", 0, 2, row_y[0], PRIMARY_RED),
            ("Mermaid SVG", 2, 4, row_y[1], PRIMARY_BLUE),
            ("SVG fragments", 2, 5, row_y[2], PRIMARY_GREEN),
            ("Manim video", 2, 6, row_y[3], PRIMARY_ORANGE),
        ]

        slot_group = VGroup()
        bars = VGroup()
        labels = VGroup()
        for label, start, end, y, color in tasks:
            width = day_x(end) - day_x(start)
            center_x = (day_x(start) + day_x(end)) / 2
            slot = Rectangle(
                width=width,
                height=row_height,
                stroke_color=GRAY_200,
                stroke_width=1.2,
                fill_color=GRAY_100,
                fill_opacity=0.18,
            ).move_to([center_x, y, 0])
            slot.set_z_index(1)
            bar = Rectangle(
                width=width,
                height=row_height,
                stroke_color=color,
                stroke_width=1.6,
                fill_color=color,
                fill_opacity=0.94,
            ).move_to([center_x, y, 0])
            bar.set_z_index(3)
            text = Text(label, font=TEXT_FONT, font_size=17, color=WHITE).move_to(bar)
            if text.width > width - 0.22:
                text.scale_to_fit_width(width - 0.22)
            text.set_z_index(5)
            slot_group.add(slot)
            bars.add(bar)
            labels.add(text)

        dependency = VGroup(
            Line([day_x(2), row_y[0] - row_height / 2, 0], [day_x(2), row_y[1] + row_height / 2, 0], color=PRIMARY_RED, stroke_width=3),
            Line([day_x(2), row_y[1] - row_height / 2, 0], [day_x(2), row_y[2] + row_height / 2, 0], color=PRIMARY_RED, stroke_width=3),
            Line([day_x(2), row_y[2] - row_height / 2, 0], [day_x(2), row_y[3] + row_height / 2, 0], color=PRIMARY_RED, stroke_width=3),
        )
        dependency.set_z_index(6)

        cursor = Line(
            [day_x(0), chart_top + 0.18, 0],
            [day_x(0), chart_bottom - 0.05, 0],
            color=PRIMARY_RED,
            stroke_width=4,
        )
        cursor.set_z_index(7)

        bracket_bounds = VGroup(*bars, *labels)
        pad_x = 0.32
        pad_y = 0.3
        left = bracket_bounds.get_left()[0] - pad_x
        right = bracket_bounds.get_right()[0] + pad_x
        top = bracket_bounds.get_top()[1] + pad_y
        bottom = bracket_bounds.get_bottom()[1] - pad_y
        corner = 0.42
        terminal_brackets = VGroup(
            Line([left, top, 0], [left + corner, top, 0], color=PRIMARY_RED, stroke_width=3),
            Line([left, top, 0], [left, top - corner, 0], color=PRIMARY_RED, stroke_width=3),
            Line([right, top, 0], [right - corner, top, 0], color=PRIMARY_RED, stroke_width=3),
            Line([right, top, 0], [right, top - corner, 0], color=PRIMARY_RED, stroke_width=3),
            Line([left, bottom, 0], [left + corner, bottom, 0], color=PRIMARY_RED, stroke_width=3),
            Line([left, bottom, 0], [left, bottom + corner, 0], color=PRIMARY_RED, stroke_width=3),
            Line([right, bottom, 0], [right - corner, bottom, 0], color=PRIMARY_RED, stroke_width=3),
            Line([right, bottom, 0], [right, bottom + corner, 0], color=PRIMARY_RED, stroke_width=3),
        )
        terminal_brackets.set_z_index(8)

        resolved = VGroup(stage, header, grid, axis, tick_labels, section, bars, labels, terminal_brackets)
        if poster_mode:
            self.add(resolved)
            return

        self.add(stage, header, grid, axis, tick_labels, section, slot_group)
        self.wait(2.4)
        elapsed = 2.4

        self.play(Create(cursor), run_time=0.35)
        elapsed += 0.35

        self.play(
            cursor.animate.move_to([day_x(2), (chart_top + chart_bottom) / 2 + 0.065, 0]),
            GrowFromEdge(bars[0], LEFT),
            FadeIn(labels[0], shift=UP * 0.04),
            run_time=2.45,
            rate_func=rate_functions.ease_in_out_cubic,
        )
        self.wait(0.45)
        elapsed += 2.9

        self.play(
            AnimationGroup(*[Create(line) for line in dependency], lag_ratio=0.18),
            run_time=0.85,
            rate_func=rate_functions.ease_out_cubic,
        )
        self.wait(0.35)
        elapsed += 1.2

        self.play(
            cursor.animate.move_to([day_x(6), (chart_top + chart_bottom) / 2 + 0.065, 0]),
            GrowFromEdge(bars[1], LEFT),
            GrowFromEdge(bars[2], LEFT),
            GrowFromEdge(bars[3], LEFT),
            run_time=4.25,
            rate_func=rate_functions.ease_in_out_cubic,
        )
        self.play(
            FadeIn(labels[1], shift=UP * 0.035),
            FadeIn(labels[2], shift=UP * 0.035),
            FadeIn(labels[3], shift=UP * 0.035),
            run_time=0.72,
        )
        self.wait(0.45)
        elapsed += 5.42

        self.play(
            FadeOut(slot_group),
            FadeOut(dependency),
            FadeOut(cursor),
            run_time=0.9,
            rate_func=rate_functions.ease_out_cubic,
        )
        self.play(FadeIn(terminal_brackets, scale=0.98), run_time=0.45)
        elapsed += 1.35

        self.wait(max(7.0, 25.5 - elapsed))


if __name__ == "__main__":
    raise SystemExit(main())
