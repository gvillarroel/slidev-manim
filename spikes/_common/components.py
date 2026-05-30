from __future__ import annotations

from math import cos, sin

from manim import DOWN, LEFT, ORIGIN, PI, RIGHT, UP, Arc, Circle, Line, Rectangle, VGroup
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


def aperture_shutters(width: float = 3.75, height: float = 1.32, gap: float = 1.24, color: str = GRAY_200, opacity: float = 0.78) -> VGroup:
    top = slab(color, width, height, opacity).move_to(UP * gap / 2)
    bottom = slab(color, width, height, opacity).move_to(DOWN * gap / 2)
    return VGroup(top, bottom)


def merge_funnel(width: float = 3.2, height: float = 2.2, outlet_height: float = 0.46, color: str = GRAY_400, opacity: float = 0.72) -> VGroup:
    top = Line(LEFT * width / 2 + UP * height / 2, RIGHT * width / 2 + UP * outlet_height / 2)
    bottom = Line(LEFT * width / 2 + DOWN * height / 2, RIGHT * width / 2 + DOWN * outlet_height / 2)
    outlet = Line(RIGHT * width / 2 + DOWN * outlet_height / 2, RIGHT * width / 2 + UP * outlet_height / 2)
    funnel = VGroup(top, bottom, outlet)
    funnel.set_stroke(color=color, width=5, opacity=opacity)
    return funnel


def orbit_guides(radius: float = 1.55, color: str = GRAY_200, opacity: float = 0.48) -> VGroup:
    zone = Circle(radius=radius, stroke_color=color, stroke_width=3.0, stroke_opacity=opacity, fill_opacity=0)
    outer = Arc(radius=radius * 1.08, start_angle=PI * 0.86, angle=-PI * 1.08)
    inner = Arc(radius=radius * 0.58, start_angle=-PI * 0.18, angle=PI * 0.62)
    guides = VGroup(zone, outer, inner)
    guides.set_stroke(color=color, width=3.2, opacity=opacity)
    return guides


def fork_guides(width: float = 3.4, spread: float = 1.45, color: str = GRAY_300, opacity: float = 0.62) -> VGroup:
    trunk = Line(LEFT * width / 2, ORIGIN)
    upper = Line(ORIGIN, RIGHT * width / 2 + UP * spread / 2)
    lower = Line(ORIGIN, RIGHT * width / 2 + DOWN * spread / 2)
    fork = VGroup(trunk, upper, lower)
    fork.set_stroke(color=color, width=4.2, opacity=opacity)
    return fork


def pressure_wall(height: float = 2.85, color: str = GRAY_300, opacity: float = 0.72) -> VGroup:
    wall = slab(color, 0.16, height, opacity)
    ticks = VGroup(*[
        Line(LEFT * 0.34 + UP * y, LEFT * 0.08 + UP * y, color=color, stroke_width=2.4, stroke_opacity=opacity * 0.76)
        for y in (-height * 0.34, 0, height * 0.34)
    ])
    return VGroup(wall, ticks)


def clamp_pair(height: float = 2.25, gap: float = 1.28, width: float = 0.24, color: str = GRAY_400, opacity: float = 0.7) -> VGroup:
    left = slab(color, width, height, opacity).move_to(LEFT * gap / 2)
    right = slab(color, width, height, opacity).move_to(RIGHT * gap / 2)
    return VGroup(left, right)


def sleeve_channel(width: float = 1.7, height: float = 1.5, color: str = GRAY_300, opacity: float = 0.68) -> VGroup:
    left = Line(LEFT * width / 2 + UP * height / 2, LEFT * width / 2 + DOWN * height / 2)
    top = Line(LEFT * width / 2 + UP * height / 2, RIGHT * width / 2 + UP * height / 2)
    bottom = Line(LEFT * width / 2 + DOWN * height / 2, RIGHT * width / 2 + DOWN * height / 2)
    sleeve = VGroup(left, top, bottom)
    sleeve.set_stroke(color=color, width=5.0, opacity=opacity)
    return sleeve


def ramp_plane(width: float = 2.75, rise: float = 1.05, color: str = GRAY_300, opacity: float = 0.64) -> VGroup:
    plane = Line(LEFT * width / 2 + DOWN * rise / 2, RIGHT * width / 2 + UP * rise / 2)
    floor = Line(LEFT * width / 2 + DOWN * rise / 2, RIGHT * width / 2 + DOWN * rise / 2)
    brace = Line(RIGHT * width / 2 + DOWN * rise / 2, RIGHT * width / 2 + UP * rise / 2)
    ramp = VGroup(plane, floor, brace)
    ramp.set_stroke(color=color, width=4.2, opacity=opacity)
    return ramp


def fan_guides(count: int = 5, radius: float = 1.75, spread: float = PI * 0.72, color: str = GRAY_300, opacity: float = 0.56) -> VGroup:
    guides = VGroup()
    if count <= 1:
        guides.add(Line(ORIGIN, RIGHT * radius))
    else:
        start = -spread / 2
        step = spread / (count - 1)
        for index in range(count):
            angle = start + step * index
            endpoint = [radius * cos(angle), radius * sin(angle), 0]
            guides.add(Line(ORIGIN, endpoint))
    guides.set_stroke(color=color, width=3.4, opacity=opacity)
    return guides


def hinge_pivot(arm_length: float = 1.75, arc_radius: float = 0.74, color: str = GRAY_300, opacity: float = 0.68) -> VGroup:
    pivot = Circle(radius=0.16, stroke_width=0, fill_color=color, fill_opacity=opacity)
    arm = Line(ORIGIN, RIGHT * arm_length, color=color, stroke_width=5.0, stroke_opacity=opacity)
    arc = Arc(radius=arc_radius, start_angle=0, angle=PI / 2, stroke_color=color, stroke_width=3.2, stroke_opacity=opacity * 0.72)
    return VGroup(pivot, arm, arc)


def arc_handoff(radius: float = 1.42, color: str = GRAY_300, opacity: float = 0.62) -> VGroup:
    arc = Arc(radius=radius, start_angle=PI * 0.9, angle=-PI * 0.8, stroke_color=color, stroke_width=4.2, stroke_opacity=opacity)
    source = Circle(radius=0.1, stroke_width=0, fill_color=color, fill_opacity=opacity).move_to(LEFT * radius * 0.82 + UP * radius * 0.42)
    target = Circle(radius=0.1, stroke_width=0, fill_color=color, fill_opacity=opacity).move_to(RIGHT * radius * 0.82 + UP * radius * 0.42)
    return VGroup(arc, source, target)


def bumper_stop(width: float = 0.28, height: float = 1.78, color: str = GRAY_300, opacity: float = 0.68) -> VGroup:
    wall = slab(color, width, height, opacity)
    deflector = Line(LEFT * 0.62 + DOWN * 0.46, RIGHT * 0.16 + UP * 0.46, color=color, stroke_width=4.2, stroke_opacity=opacity)
    deflector.next_to(wall, LEFT, buff=0.18)
    return VGroup(wall, deflector)


def compression_channel(width: float = 3.0, gap: float = 0.76, color: str = GRAY_300, opacity: float = 0.62) -> VGroup:
    top = Line(LEFT * width / 2 + UP * gap / 2, RIGHT * width / 2 + UP * gap / 2)
    bottom = Line(LEFT * width / 2 + DOWN * gap / 2, RIGHT * width / 2 + DOWN * gap / 2)
    entry = open_slot(0.72, gap * 1.6, color=color, opacity=opacity * 0.74, stroke_width=2.4).move_to(LEFT * width / 2)
    channel = VGroup(top, bottom, entry)
    channel.set_stroke(color=color, width=4.0, opacity=opacity)
    return channel


def corridor_rails(width: float = 3.5, gap: float = 1.05, color: str = GRAY_300, opacity: float = 0.58) -> VGroup:
    top = slab(color, width, 0.08, opacity).move_to(UP * gap / 2)
    bottom = slab(color, width, 0.08, opacity).move_to(DOWN * gap / 2)
    squeeze = VGroup(
        slab(color, 0.1, gap * 0.46, opacity * 0.86).move_to(LEFT * width * 0.12),
        slab(color, 0.1, gap * 0.46, opacity * 0.86).move_to(RIGHT * width * 0.12),
    )
    return VGroup(top, bottom, squeeze)


def cradle_catch(width: float = 2.05, height: float = 1.0, color: str = GRAY_300, opacity: float = 0.62) -> VGroup:
    left_pad = slab(color, 0.5, 0.14, opacity).rotate(PI / 8).move_to(LEFT * width / 4 + DOWN * height / 3)
    right_pad = slab(color, 0.5, 0.14, opacity).rotate(-PI / 8).move_to(RIGHT * width / 4 + DOWN * height / 3)
    basin = Arc(radius=width / 2, start_angle=PI * 1.05, angle=PI * 0.9, stroke_color=color, stroke_width=3.6, stroke_opacity=opacity)
    basin.shift(DOWN * height * 0.22)
    return VGroup(basin, left_pad, right_pad)


def balance_beam(width: float = 3.0, color: str = GRAY_300, opacity: float = 0.62) -> VGroup:
    beam = Line(LEFT * width / 2, RIGHT * width / 2, color=color, stroke_width=5.0, stroke_opacity=opacity)
    fulcrum = VGroup(
        Line(ORIGIN, LEFT * 0.34 + DOWN * 0.62, color=color, stroke_width=3.4, stroke_opacity=opacity),
        Line(ORIGIN, RIGHT * 0.34 + DOWN * 0.62, color=color, stroke_width=3.4, stroke_opacity=opacity),
    )
    return VGroup(beam, fulcrum)


def deformation_wave(width: float = 3.2, amplitude: float = 0.32, color: str = GRAY_300, opacity: float = 0.62) -> VGroup:
    segments = VGroup()
    step = width / 4
    for index in range(4):
        start_x = -width / 2 + step * index
        arc = Arc(radius=step / 2, start_angle=PI, angle=-PI, stroke_color=color, stroke_width=3.8, stroke_opacity=opacity)
        arc.stretch_to_fit_height(amplitude * 2)
        arc.move_to(LEFT * (-(start_x + step / 2)))
        if index % 2:
            arc.flip(UP)
        segments.add(arc)
    return segments


def settle_echo(count: int = 3, radius: float = 0.55, color: str = GRAY_300, opacity: float = 0.54) -> VGroup:
    echoes = VGroup()
    for index in range(count):
        echoes.add(Circle(radius=radius + index * 0.22, stroke_color=color, stroke_width=2.8, stroke_opacity=opacity * (1 - index * 0.2), fill_opacity=0))
    return echoes


def edge_tension_marker(height: float = 2.4, tether: float = 1.25, color: str = GRAY_300, opacity: float = 0.66) -> VGroup:
    wall = slab(color, 0.12, height, opacity).move_to(RIGHT * tether / 2)
    line = Line(LEFT * tether / 2, RIGHT * tether / 2, color=color, stroke_width=3.8, stroke_opacity=opacity)
    notch = Line(RIGHT * tether / 2 + UP * 0.24, RIGHT * tether / 2 + DOWN * 0.24, color=color, stroke_width=3.0, stroke_opacity=opacity)
    return VGroup(line, wall, notch)


def keystone_lock(width: float = 1.65, color: str = GRAY_300, opacity: float = 0.64) -> VGroup:
    cap = slab(color, width, 0.26, opacity).move_to(UP * 0.58)
    center = slab(color, width * 0.42, 0.88, opacity).move_to(ORIGIN)
    left = slab(color, width * 0.24, 0.58, opacity * 0.8).rotate(-PI / 12).move_to(LEFT * width * 0.34 + DOWN * 0.12)
    right = slab(color, width * 0.24, 0.58, opacity * 0.8).rotate(PI / 12).move_to(RIGHT * width * 0.34 + DOWN * 0.12)
    return VGroup(cap, left, center, right)


def latch_anchor(width: float = 1.9, color: str = GRAY_300, opacity: float = 0.66) -> VGroup:
    anchor = Circle(radius=0.2, stroke_width=0, fill_color=color, fill_opacity=opacity).move_to(LEFT * width / 2)
    hook = VGroup(
        Line(LEFT * width / 2, RIGHT * width / 2, color=color, stroke_width=4.0, stroke_opacity=opacity),
        Line(RIGHT * width / 2, RIGHT * width / 2 + DOWN * 0.48, color=color, stroke_width=4.0, stroke_opacity=opacity),
        Line(RIGHT * width / 2 + DOWN * 0.48, RIGHT * width / 2 + LEFT * 0.38 + DOWN * 0.48, color=color, stroke_width=4.0, stroke_opacity=opacity),
    )
    return VGroup(anchor, hook)


def layered_stack(count: int = 3, width: float = 1.8, height: float = 0.52, color: str = GRAY_300, opacity: float = 0.54) -> VGroup:
    layers = VGroup()
    for index in range(count):
        layers.add(slab(color, width, height, opacity + index * 0.08).move_to(RIGHT * index * 0.18 + DOWN * index * 0.18))
    return layers


def magnet_capture(radius: float = 1.0, color: str = GRAY_300, opacity: float = 0.62) -> VGroup:
    left = Arc(radius=radius, start_angle=PI / 2, angle=PI, stroke_color=color, stroke_width=4.0, stroke_opacity=opacity).shift(LEFT * 0.24)
    right = Arc(radius=radius, start_angle=-PI / 2, angle=PI, stroke_color=color, stroke_width=4.0, stroke_opacity=opacity).shift(RIGHT * 0.24)
    poles = VGroup(slab(color, 0.18, 0.46, opacity).move_to(LEFT * 0.6), slab(color, 0.18, 0.46, opacity).move_to(RIGHT * 0.6))
    return VGroup(left, right, poles)


def negative_space_frame(width: float = 3.0, height: float = 2.0, opening: float = 0.82, color: str = GRAY_200, opacity: float = 0.58) -> VGroup:
    top = slab(color, width, (height - opening) / 2, opacity).move_to(UP * (opening / 2 + (height - opening) / 4))
    bottom = slab(color, width, (height - opening) / 2, opacity).move_to(DOWN * (opening / 2 + (height - opening) / 4))
    left = slab(color, (width - opening) / 2, opening, opacity).move_to(LEFT * (opening / 2 + (width - opening) / 4))
    right = slab(color, (width - opening) / 2, opening, opacity).move_to(RIGHT * (opening / 2 + (width - opening) / 4))
    return VGroup(top, bottom, left, right)


def parallax_planes(width: float = 2.2, height: float = 0.62, color: str = GRAY_300, opacity: float = 0.52) -> VGroup:
    back = slab(color, width, height, opacity * 0.72).move_to(LEFT * 0.36 + UP * 0.34)
    mid = slab(color, width, height, opacity).move_to(ORIGIN)
    front = slab(color, width, height, min(opacity * 1.18, 1)).move_to(RIGHT * 0.36 + DOWN * 0.34)
    return VGroup(back, mid, front)


def occlusion_peel(width: float = 2.2, height: float = 1.35, color: str = GRAY_300, opacity: float = 0.58) -> VGroup:
    base = open_slot(width, height, color=color, opacity=opacity * 0.72)
    cover = slab(color, width * 0.58, height, opacity).move_to(RIGHT * width * 0.18)
    lip = Line(cover.get_left() + UP * height / 2, cover.get_left() + DOWN * height / 2, color=color, stroke_width=3.4, stroke_opacity=opacity)
    return VGroup(base, cover, lip)


def relay_nodes(count: int = 3, spacing: float = 1.15, color: str = GRAY_300, opacity: float = 0.62) -> VGroup:
    nodes = VGroup()
    connectors = VGroup()
    start = -(count - 1) * spacing / 2
    for index in range(count):
        nodes.add(Circle(radius=0.16, stroke_width=0, fill_color=color, fill_opacity=opacity).move_to(RIGHT * (start + index * spacing)))
        if index:
            connectors.add(Line(RIGHT * (start + (index - 1) * spacing), RIGHT * (start + index * spacing), color=color, stroke_width=3.2, stroke_opacity=opacity * 0.72))
    return VGroup(connectors, nodes)


def rhythm_gate_marks(count: int = 4, spacing: float = 0.72, color: str = GRAY_300, opacity: float = 0.62) -> VGroup:
    marks = VGroup()
    start = -(count - 1) * spacing / 2
    for index in range(count):
        marks.add(slab(color, 0.14, 0.72 if index % 2 == 0 else 0.46, opacity).move_to(RIGHT * (start + index * spacing)))
    rail = Line(LEFT * (count * spacing / 2), RIGHT * (count * spacing / 2), color=color, stroke_width=2.6, stroke_opacity=opacity * 0.52)
    rail.shift(DOWN * 0.56)
    return VGroup(rail, marks)


def shear_rails(width: float = 2.55, offset: float = 0.42, color: str = GRAY_300, opacity: float = 0.62) -> VGroup:
    top = Line(LEFT * width / 2 + UP * 0.48, RIGHT * width / 2 + UP * 0.48 + RIGHT * offset, color=color, stroke_width=4.0, stroke_opacity=opacity)
    bottom = Line(LEFT * width / 2 + DOWN * 0.48 + LEFT * offset, RIGHT * width / 2 + DOWN * 0.48, color=color, stroke_width=4.0, stroke_opacity=opacity)
    body = slab(color, width * 0.58, 0.46, opacity * 0.56)
    return VGroup(top, bottom, body)


def sling_arc(radius: float = 1.25, color: str = GRAY_300, opacity: float = 0.62) -> VGroup:
    band = Arc(radius=radius, start_angle=PI * 1.08, angle=PI * 0.86, stroke_color=color, stroke_width=4.2, stroke_opacity=opacity)
    left_anchor = Circle(radius=0.12, stroke_width=0, fill_color=color, fill_opacity=opacity).move_to(LEFT * radius * 0.92 + DOWN * 0.34)
    right_anchor = Circle(radius=0.12, stroke_width=0, fill_color=color, fill_opacity=opacity).move_to(RIGHT * radius * 0.92 + DOWN * 0.34)
    return VGroup(band, left_anchor, right_anchor)


def snap_recoil_stop(height: float = 1.9, color: str = GRAY_300, opacity: float = 0.66) -> VGroup:
    stop = pressure_wall(height=height, color=color, opacity=opacity)
    spring = VGroup(
        Line(LEFT * 1.0 + UP * 0.24, LEFT * 0.72 + DOWN * 0.24, color=color, stroke_width=3.2, stroke_opacity=opacity),
        Line(LEFT * 0.72 + DOWN * 0.24, LEFT * 0.44 + UP * 0.24, color=color, stroke_width=3.2, stroke_opacity=opacity),
        Line(LEFT * 0.44 + UP * 0.24, LEFT * 0.16 + DOWN * 0.24, color=color, stroke_width=3.2, stroke_opacity=opacity),
    )
    return VGroup(spring, stop)


def convergence_lane(width: float = 3.0, neck: float = 0.54, color: str = GRAY_300, opacity: float = 0.62) -> VGroup:
    top = Line(LEFT * width / 2 + UP * 0.88, RIGHT * width / 2 + UP * neck / 2, color=color, stroke_width=4.0, stroke_opacity=opacity)
    bottom = Line(LEFT * width / 2 + DOWN * 0.88, RIGHT * width / 2 + DOWN * neck / 2, color=color, stroke_width=4.0, stroke_opacity=opacity)
    throat = Line(RIGHT * width / 2 + UP * neck / 2, RIGHT * width / 2 + DOWN * neck / 2, color=color, stroke_width=4.0, stroke_opacity=opacity)
    return VGroup(top, bottom, throat)


def weave_crossing(width: float = 2.4, color: str = GRAY_300, opacity: float = 0.62) -> VGroup:
    upper = Line(LEFT * width / 2 + UP * 0.45, RIGHT * width / 2 + DOWN * 0.45, color=color, stroke_width=4.0, stroke_opacity=opacity)
    lower_left = Line(LEFT * width / 2 + DOWN * 0.45, LEFT * 0.18 + DOWN * 0.06, color=color, stroke_width=4.0, stroke_opacity=opacity * 0.72)
    lower_right = Line(RIGHT * 0.18 + UP * 0.06, RIGHT * width / 2 + UP * 0.45, color=color, stroke_width=4.0, stroke_opacity=opacity * 0.72)
    gap = Circle(radius=0.18, stroke_width=0, fill_color=GRAY_100, fill_opacity=1)
    return VGroup(upper, lower_left, lower_right, gap)


def device_frame(width: float = 2.8, height: float = 1.7, color: str = GRAY_300, opacity: float = 0.62) -> VGroup:
    shell = Rectangle(width=width, height=height, stroke_color=color, stroke_width=3.2, stroke_opacity=opacity, fill_opacity=0)
    header = slab(color, width, 0.18, opacity * 0.72).move_to(UP * (height / 2 - 0.09))
    viewport = open_slot(width * 0.72, height * 0.48, color=color, opacity=opacity * 0.58, stroke_width=2.2).move_to(DOWN * 0.08)
    return VGroup(shell, header, viewport)


def callout_panel(width: float = 2.2, height: float = 1.1, color: str = GRAY_300, opacity: float = 0.62) -> VGroup:
    panel = Rectangle(width=width, height=height, stroke_color=color, stroke_width=3.0, stroke_opacity=opacity, fill_color=color, fill_opacity=opacity * 0.18)
    pointer = VGroup(
        Line(LEFT * width * 0.12 + DOWN * height / 2, LEFT * width * 0.38 + DOWN * (height / 2 + 0.42), color=color, stroke_width=3.0, stroke_opacity=opacity),
        Line(LEFT * width * 0.38 + DOWN * (height / 2 + 0.42), LEFT * width * 0.48 + DOWN * height / 2, color=color, stroke_width=3.0, stroke_opacity=opacity),
    )
    return VGroup(panel, pointer)


def svg_role_slots(count: int = 3, spacing: float = 1.08, color: str = GRAY_300, opacity: float = 0.58) -> VGroup:
    slots = VGroup()
    start = -(count - 1) * spacing / 2
    for index in range(count):
        slots.add(open_slot(0.76, 0.56, color=color, opacity=opacity, stroke_width=2.2).move_to(RIGHT * (start + index * spacing)))
    connectors = VGroup(*[
        Line(slots[index].get_right(), slots[index + 1].get_left(), color=color, stroke_width=2.2, stroke_opacity=opacity * 0.7)
        for index in range(count - 1)
    ])
    return VGroup(connectors, slots)


def mind_map_branch_guides(count: int = 5, radius: float = 1.55, color: str = GRAY_300, opacity: float = 0.58) -> VGroup:
    hub = Circle(radius=0.2, stroke_width=0, fill_color=color, fill_opacity=opacity)
    branches = VGroup()
    leaves = VGroup()
    start = -PI * 0.42
    spread = PI * 0.84
    for index in range(count):
        angle = start + spread * index / max(count - 1, 1)
        endpoint = [radius * cos(angle), radius * sin(angle), 0]
        branches.add(Line(ORIGIN, endpoint, color=color, stroke_width=2.8, stroke_opacity=opacity))
        leaves.add(Circle(radius=0.11, stroke_width=0, fill_color=color, fill_opacity=opacity).move_to(endpoint))
    return VGroup(hub, branches, leaves)


def multi_video_grid(rows: int = 2, columns: int = 2, cell_width: float = 1.15, cell_height: float = 0.72, color: str = GRAY_300, opacity: float = 0.58) -> VGroup:
    cells = VGroup()
    for row in range(rows):
        for column in range(columns):
            x = (column - (columns - 1) / 2) * (cell_width + 0.22)
            y = ((rows - 1) / 2 - row) * (cell_height + 0.22)
            cells.add(open_slot(cell_width, cell_height, color=color, opacity=opacity, stroke_width=2.2).move_to(RIGHT * x + UP * y))
    return cells


def caliper_gauge(width: float = 2.2, jaw: float = 0.62, color: str = GRAY_300, opacity: float = 0.62) -> VGroup:
    rail = Line(LEFT * width / 2, RIGHT * width / 2, color=color, stroke_width=3.4, stroke_opacity=opacity)
    left = VGroup(Line(LEFT * width / 2, LEFT * width / 2 + DOWN * jaw, color=color, stroke_width=4.0, stroke_opacity=opacity), Line(LEFT * width / 2 + DOWN * jaw, LEFT * (width / 2 - 0.32) + DOWN * jaw, color=color, stroke_width=4.0, stroke_opacity=opacity))
    right = VGroup(Line(RIGHT * width / 2, RIGHT * width / 2 + DOWN * jaw, color=color, stroke_width=4.0, stroke_opacity=opacity), Line(RIGHT * width / 2 + DOWN * jaw, RIGHT * (width / 2 - 0.32) + DOWN * jaw, color=color, stroke_width=4.0, stroke_opacity=opacity))
    return VGroup(rail, left, right)


def circuit_route(color: str = GRAY_300, opacity: float = 0.62) -> VGroup:
    path = VGroup(
        Line(LEFT * 1.45, LEFT * 0.45, color=color, stroke_width=3.2, stroke_opacity=opacity),
        Line(LEFT * 0.45, LEFT * 0.45 + UP * 0.62, color=color, stroke_width=3.2, stroke_opacity=opacity),
        Line(LEFT * 0.45 + UP * 0.62, RIGHT * 0.55 + UP * 0.62, color=color, stroke_width=3.2, stroke_opacity=opacity),
        Line(RIGHT * 0.55 + UP * 0.62, RIGHT * 0.55 + DOWN * 0.42, color=color, stroke_width=3.2, stroke_opacity=opacity),
        Line(RIGHT * 0.55 + DOWN * 0.42, RIGHT * 1.45 + DOWN * 0.42, color=color, stroke_width=3.2, stroke_opacity=opacity),
    )
    nodes = VGroup(*[Circle(radius=0.1, stroke_width=0, fill_color=color, fill_opacity=opacity).move_to(point) for point in (LEFT * 1.45, LEFT * 0.45 + UP * 0.62, RIGHT * 0.55 + DOWN * 0.42, RIGHT * 1.45 + DOWN * 0.42)])
    return VGroup(path, nodes)


def coil_guide(turns: int = 4, radius: float = 0.34, color: str = GRAY_300, opacity: float = 0.62) -> VGroup:
    coils = VGroup()
    for index in range(turns):
        arc = Arc(radius=radius, start_angle=PI, angle=-PI, stroke_color=color, stroke_width=3.4, stroke_opacity=opacity)
        arc.move_to(RIGHT * (index - (turns - 1) / 2) * radius * 1.18)
        if index % 2:
            arc.flip(UP)
        coils.add(arc)
    return coils


def lattice_grid(rows: int = 3, columns: int = 4, cell: float = 0.42, color: str = GRAY_300, opacity: float = 0.5) -> VGroup:
    grid = VGroup()
    width = columns * cell
    height = rows * cell
    for column in range(columns + 1):
        x = -width / 2 + column * cell
        grid.add(Line(RIGHT * x + DOWN * height / 2, RIGHT * x + UP * height / 2, color=color, stroke_width=2.0, stroke_opacity=opacity))
    for row in range(rows + 1):
        y = -height / 2 + row * cell
        grid.add(Line(LEFT * width / 2 + UP * y, RIGHT * width / 2 + UP * y, color=color, stroke_width=2.0, stroke_opacity=opacity))
    return grid


def narrative_stage(width: float = 3.2, color: str = GRAY_300, opacity: float = 0.56) -> VGroup:
    rail = Line(LEFT * width / 2 + DOWN * 0.78, RIGHT * width / 2 + DOWN * 0.78, color=color, stroke_width=3.0, stroke_opacity=opacity)
    beats = VGroup(*[Circle(radius=0.09, stroke_width=0, fill_color=color, fill_opacity=opacity).move_to(LEFT * width / 2 + RIGHT * (index * width / 3) + DOWN * 0.78) for index in range(4)])
    frame = open_slot(width * 0.68, 1.1, color=color, opacity=opacity, stroke_width=2.4).move_to(UP * 0.16)
    return VGroup(frame, rail, beats)
