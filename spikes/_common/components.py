from __future__ import annotations

from manim import DOWN, LEFT, RIGHT, UP, Circle, Line, Rectangle, VGroup
from manim.mobject.mobject import Mobject

from _common.visual import GRAY_100, GRAY_200, GRAY_300, GRAY_400, GRAY_500, GRAY_600, GRAY_800, PRIMARY_RED


def slab(color: str, width: float, height: float, opacity: float = 1.0) -> Rectangle:
    return Rectangle(width=width, height=height, stroke_width=0, fill_color=color, fill_opacity=opacity)


def pulse(radius: float = 0.18, color: str = PRIMARY_RED) -> Circle:
    actor = Circle(radius=radius, stroke_width=0, fill_color=color, fill_opacity=1)
    actor.set_z_index(10)
    return actor


def open_slot(width: float, height: float, color: str = GRAY_200, opacity: float = 0.72, stroke_width: float = 3) -> VGroup:
    top = Line(LEFT * width / 2 + UP * height / 2, RIGHT * width / 2 + UP * height / 2)
    bottom = Line(LEFT * width / 2 + DOWN * height / 2, RIGHT * width / 2 + DOWN * height / 2)
    left = Line(LEFT * width / 2 + UP * height * 0.25, LEFT * width / 2 + DOWN * height * 0.25)
    right = Line(RIGHT * width / 2 + UP * height * 0.25, RIGHT * width / 2 + DOWN * height * 0.25)
    slot = VGroup(top, bottom, left, right)
    slot.set_stroke(color=color, width=stroke_width, opacity=opacity)
    return slot


def source_slot(scale: float = 1.0) -> VGroup:
    slot = VGroup(
        Line([-0.56, -0.42, 0], [-0.56, 0.42, 0], color=GRAY_300, stroke_width=3.0),
        Line([-0.44, 0.55, 0], [-0.16, 0.55, 0], color=GRAY_200, stroke_width=2.2),
        Line([-0.44, -0.55, 0], [-0.16, -0.55, 0], color=GRAY_200, stroke_width=2.2),
        Line([0.30, 0.55, 0], [0.56, 0.55, 0], color=GRAY_200, stroke_width=2.2),
        Line([0.30, -0.55, 0], [0.56, -0.55, 0], color=GRAY_200, stroke_width=2.2),
    )
    slot.set_opacity(0.72)
    return slot.scale(scale)


def target_slot(scale: float = 1.0) -> VGroup:
    slot = source_slot(scale)
    slot.flip(LEFT)
    return slot


def bridge_lane(width: float = 3.4, gap: float = 0.84, color: str = GRAY_400, opacity: float = 0.5) -> VGroup:
    top = slab(color, width, 0.075, opacity).move_to(UP * gap / 2)
    bottom = slab(color, width, 0.075, opacity).move_to(DOWN * gap / 2)
    left_gate = slab(color, 0.09, gap * 0.64, opacity * 0.82).move_to(LEFT * width / 2)
    right_gate = slab(color, 0.09, gap * 0.64, opacity * 0.82).move_to(RIGHT * width / 2)
    lane = VGroup(top, bottom, left_gate, right_gate)
    lane.set_z_index(1)
    return lane


def gate_column(height: float = 3.9, aperture: float = 1.12, color: str = GRAY_100) -> VGroup:
    upper = slab(color, 0.72, (height - aperture) / 2, 0.92).move_to(UP * (aperture / 2 + (height - aperture) / 4))
    lower = slab(color, 0.72, (height - aperture) / 2, 0.92).move_to(DOWN * (aperture / 2 + (height - aperture) / 4))
    left_rule = Line(LEFT * 0.64 + DOWN * height / 2, LEFT * 0.64 + UP * height / 2, color=GRAY_200, stroke_width=2.2)
    right_rule = Line(RIGHT * 0.64 + DOWN * height / 2, RIGHT * 0.64 + UP * height / 2, color=GRAY_200, stroke_width=2.2)
    return VGroup(upper, lower, left_rule, right_rule)


def time_rail(height: float = 4.6, ticks: int = 4, color: str = GRAY_200) -> VGroup:
    rail = Line(DOWN * height / 2, UP * height / 2, color=color, stroke_width=4).set_opacity(0.48)
    marks = VGroup()
    if ticks > 1:
        step = height / (ticks - 1)
        for index in range(ticks):
            y = -height / 2 + step * index
            marks.add(Line(LEFT * 0.16 + UP * y, RIGHT * 0.32 + UP * y, color=GRAY_300, stroke_width=2.4))
    return VGroup(rail, marks)


def mask_window(height: float = 4.6, width: float = 0.72) -> VGroup:
    window = Rectangle(
        width=width,
        height=height,
        stroke_color=PRIMARY_RED,
        stroke_width=4,
        fill_color=PRIMARY_RED,
        fill_opacity=0.07,
    )
    core = slab(PRIMARY_RED, 0.11, height - 0.32, 0.92)
    mask = VGroup(window, core)
    mask.set_z_index(8)
    return mask


def terminal_brackets(width: float, height: float, color: str = PRIMARY_RED, leg: float = 0.42, gap: float = 0.08) -> VGroup:
    left = -width / 2
    right = width / 2
    top = height / 2
    bottom = -height / 2
    marks = VGroup(
        Line([left + gap, top, 0], [left + leg, top, 0], color=color, stroke_width=4),
        Line([left, top - gap, 0], [left, top - leg, 0], color=color, stroke_width=4),
        Line([right - gap, top, 0], [right - leg, top, 0], color=color, stroke_width=4),
        Line([right, top - gap, 0], [right, top - leg, 0], color=color, stroke_width=4),
        Line([left + gap, bottom, 0], [left + leg, bottom, 0], color=color, stroke_width=4),
        Line([left, bottom + gap, 0], [left, bottom + leg, 0], color=color, stroke_width=4),
        Line([right - gap, bottom, 0], [right - leg, bottom, 0], color=color, stroke_width=4),
        Line([right, bottom + gap, 0], [right, bottom + leg, 0], color=color, stroke_width=4),
    )
    return marks.set_stroke(opacity=0.68)


def terminal_brackets_around(target: Mobject, padding: float = 0.42) -> VGroup:
    brackets = terminal_brackets(target.width + padding * 2, target.height + padding * 2)
    brackets.move_to(target)
    return brackets


def neutral_cluster() -> VGroup:
    return VGroup(
        slab(GRAY_800, 1.46, 0.46).move_to(LEFT * 0.46 + UP * 0.42),
        slab(GRAY_600, 1.02, 0.4).move_to(RIGHT * 0.58 + DOWN * 0.05),
        slab(GRAY_500, 0.66, 0.32).move_to(LEFT * 0.2 + DOWN * 0.66),
    )

