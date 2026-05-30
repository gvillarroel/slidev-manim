#!/usr/bin/env -S uv run --script
# /// script
# dependencies = [
#   "imageio-ffmpeg>=0.6.0",
#   "manim>=0.20.0",
#   "Pillow>=10.0.0",
# ]
# ///

from __future__ import annotations

import argparse
import shutil
import sys
from dataclasses import dataclass
from pathlib import Path

from manim import DOWN, LEFT, ORIGIN, RIGHT, UP, AnimationGroup, Create, FadeIn, FadeOut, Line, Rectangle, Rotate, Scene, Text, Transform, VGroup, smooth, there_and_back

SPIKE_DIR = Path(__file__).resolve().parent
REPO_ROOT = SPIKE_DIR.parent.parent
SPIKES_DIR = SPIKE_DIR.parent
if str(SPIKES_DIR) not in sys.path:
    sys.path.insert(0, str(SPIKES_DIR))

from _common.components import (
    aperture_shutters,
    arc_handoff,
    balance_beam,
    bridge_lane,
    bumper_stop,
    clamp_pair,
    compression_channel,
    corridor_rails,
    cradle_catch,
    deformation_wave,
    edge_tension_marker,
    fan_guides,
    fork_guides,
    gate_column,
    hinge_pivot,
    keystone_lock,
    latch_anchor,
    layered_stack,
    magnet_capture,
    mask_window,
    merge_funnel,
    negative_space_frame,
    neutral_cluster,
    open_slot,
    orbit_guides,
    parallax_planes,
    pressure_wall,
    pulse,
    ramp_plane,
    slab,
    source_slot,
    sleeve_channel,
    settle_echo,
    target_slot,
    terminal_brackets,
    terminal_brackets_around,
    time_rail,
)
from _common.runner import convert_video_to_gif, render_scene
from _common.visual import GRAY_100, GRAY_200, GRAY_300, GRAY_400, GRAY_500, GRAY_600, GRAY_800, PRIMARY_RED, WHITE_HEX, configure_transparent_scene

SPIKE_NAME = SPIKE_DIR.name
OUTPUT_DIR = REPO_ROOT / "videos" / SPIKE_NAME
DOC_GIF_DIR = REPO_ROOT / ".specs" / "assets" / "component-demos"
DOC_README = REPO_ROOT / "docs" / "README.md"


def add_name(scene: Scene, name: str) -> Text:
    label = Text(name, font_size=28, color=GRAY_800)
    label.to_edge(UP, buff=0.42)
    scene.add(label)
    return label


class SlabDemo(Scene):
    def construct(self) -> None:
        configure_transparent_scene(self)
        add_name(self, "slab")
        body = slab(GRAY_600, 2.2, 0.62).move_to(ORIGIN)
        shadow = slab(GRAY_200, 2.6, 0.12, 0.9).move_to(DOWN * 0.58)
        self.add(shadow)
        self.play(FadeIn(body), run_time=0.45)
        self.play(body.animate.scale(1.12), run_time=0.38, rate_func=there_and_back)
        self.wait(1.5)


class PulseDemo(Scene):
    def construct(self) -> None:
        configure_transparent_scene(self)
        add_name(self, "pulse")
        actor = pulse(0.22).move_to(LEFT * 2.0)
        rail = Line(LEFT * 2.4, RIGHT * 2.4, color=GRAY_200, stroke_width=4).set_opacity(0.5)
        self.add(rail, actor)
        self.wait(0.5)
        self.play(actor.animate.move_to(RIGHT * 2.0), run_time=1.15, rate_func=smooth)
        self.play(actor.animate.scale(1.28), run_time=0.38, rate_func=there_and_back)
        self.wait(1.25)


class OpenSlotDemo(Scene):
    def construct(self) -> None:
        configure_transparent_scene(self)
        add_name(self, "open_slot")
        slot = open_slot(3.4, 1.65, opacity=0.5)
        actor = pulse(0.14).move_to(LEFT * 2.6)
        self.add(slot, actor)
        self.wait(0.5)
        self.play(slot.animate.set_stroke(color=PRIMARY_RED, opacity=0.8), actor.animate.move_to(ORIGIN), run_time=0.9, rate_func=smooth)
        self.play(slot.animate.set_stroke(color=GRAY_200, opacity=0.45), actor.animate.scale(1.15), run_time=0.38, rate_func=there_and_back)
        self.wait(1.35)


class SourceSlotDemo(Scene):
    def construct(self) -> None:
        configure_transparent_scene(self)
        add_name(self, "source_slot")
        slot = source_slot(scale=1.8).move_to(ORIGIN)
        actor = pulse(0.15).move_to(LEFT * 0.38)
        self.add(slot, actor)
        self.wait(0.7)
        self.play(actor.animate.move_to(RIGHT * 0.32), run_time=0.75, rate_func=smooth)
        self.play(slot.animate.set_opacity(0.42), actor.animate.scale(1.18), run_time=0.35, rate_func=there_and_back)
        self.wait(1.35)


class TargetSlotDemo(Scene):
    def construct(self) -> None:
        configure_transparent_scene(self)
        add_name(self, "target_slot")
        slot = target_slot(scale=1.8).move_to(ORIGIN)
        actor = pulse(0.15).move_to(LEFT * 2.2)
        self.add(slot, actor)
        self.wait(0.7)
        self.play(actor.animate.move_to(LEFT * 0.3), run_time=0.75, rate_func=smooth)
        self.play(slot.animate.set_opacity(0.42), actor.animate.scale(1.18), run_time=0.35, rate_func=there_and_back)
        self.wait(1.35)


class GateColumnDemo(Scene):
    def construct(self) -> None:
        configure_transparent_scene(self)
        add_name(self, "gate_column")
        gate = gate_column()
        actor = pulse(0.18).move_to(LEFT * 2.2)
        self.add(gate, actor)
        self.wait(0.55)
        self.play(gate[0].animate.shift(UP * 0.32), gate[1].animate.shift(DOWN * 0.32), gate[2].animate.set_color(PRIMARY_RED), gate[3].animate.set_color(PRIMARY_RED), run_time=0.5)
        self.play(actor.animate.move_to(RIGHT * 2.2), run_time=0.85, rate_func=smooth)
        self.play(gate[0].animate.shift(DOWN * 0.32), gate[1].animate.shift(UP * 0.32), gate[2].animate.set_color(GRAY_200), gate[3].animate.set_color(GRAY_200), run_time=0.38)
        self.wait(1.2)


class TerminalBracketsOnlyDemo(Scene):
    def construct(self) -> None:
        configure_transparent_scene(self)
        add_name(self, "terminal_brackets")
        marks = terminal_brackets(3.0, 1.8)
        ghost = open_slot(2.3, 1.0, opacity=0.24)
        self.add(ghost)
        self.wait(0.45)
        self.play(Create(marks), run_time=0.75)
        self.play(ghost.animate.set_opacity(0.0), marks.animate.scale(1.05), run_time=0.35, rate_func=there_and_back)
        self.wait(1.4)


class NeutralClusterDemo(Scene):
    def construct(self) -> None:
        configure_transparent_scene(self)
        add_name(self, "neutral_cluster")
        cluster = neutral_cluster().scale(1.25)
        slot = open_slot(cluster.width + 0.7, cluster.height + 0.6, opacity=0.22)
        self.add(slot)
        self.play(FadeIn(cluster), run_time=0.55)
        self.play(cluster.animate.scale(1.06), run_time=0.35, rate_func=there_and_back)
        self.wait(1.5)


class ApertureShuttersDemo(Scene):
    def construct(self) -> None:
        configure_transparent_scene(self)
        add_name(self, "aperture_shutters")
        shutters = aperture_shutters()
        actor = pulse(0.17).move_to(LEFT * 2.65)
        self.add(shutters, actor)
        self.wait(0.55)
        self.play(shutters[0].animate.shift(UP * 0.5), shutters[1].animate.shift(DOWN * 0.5), run_time=0.5, rate_func=smooth)
        self.play(actor.animate.move_to(RIGHT * 2.65), run_time=1.0, rate_func=smooth)
        self.play(shutters[0].animate.shift(DOWN * 0.5), shutters[1].animate.shift(UP * 0.5), actor.animate.scale(1.16), run_time=0.42, rate_func=there_and_back)
        self.wait(1.25)


class MergeFunnelDemo(Scene):
    def construct(self) -> None:
        configure_transparent_scene(self)
        add_name(self, "merge_funnel")
        funnel = merge_funnel()
        top = pulse(0.14).move_to(LEFT * 2.45 + UP * 1.15)
        bottom = pulse(0.14).move_to(LEFT * 2.45 + DOWN * 1.15)
        output = pulse(0.22).move_to(RIGHT * 1.9)
        self.add(funnel, top, bottom)
        self.wait(0.55)
        self.play(funnel.animate.set_stroke(color=PRIMARY_RED, opacity=0.82), top.animate.move_to(RIGHT * 1.45 + UP * 0.18), bottom.animate.move_to(RIGHT * 1.45 + DOWN * 0.18), run_time=0.9, rate_func=smooth)
        self.play(FadeOut(top), FadeOut(bottom), FadeIn(output), funnel.animate.set_stroke(color=GRAY_300, opacity=0.46), run_time=0.45)
        self.play(output.animate.scale(1.14), run_time=0.35, rate_func=there_and_back)
        self.wait(1.25)


class OrbitGuidesDemo(Scene):
    def construct(self) -> None:
        configure_transparent_scene(self)
        add_name(self, "orbit_guides")
        guides = orbit_guides()
        anchor = pulse(0.2).move_to(ORIGIN)
        satellite = pulse(0.12).move_to(LEFT * 1.65 + UP * 0.55)
        self.add(guides, anchor, satellite)
        self.wait(0.55)
        self.play(satellite.animate.move_to(UP * 1.65 + RIGHT * 0.2), run_time=0.42, rate_func=smooth)
        self.play(satellite.animate.move_to(RIGHT * 1.55 + DOWN * 0.35), guides.animate.set_stroke(color=PRIMARY_RED, opacity=0.68), run_time=0.48, rate_func=smooth)
        self.play(satellite.animate.move_to(LEFT * 0.35 + DOWN * 1.35), guides.animate.set_stroke(color=GRAY_200, opacity=0.46), run_time=0.45, rate_func=smooth)
        self.play(anchor.animate.scale(1.12), satellite.animate.scale(1.14), run_time=0.35, rate_func=there_and_back)
        self.wait(1.25)


class ForkGuidesDemo(Scene):
    def construct(self) -> None:
        configure_transparent_scene(self)
        add_name(self, "fork_guides")
        fork = fork_guides()
        actor = pulse(0.17).move_to(LEFT * 2.2)
        upper = pulse(0.13).move_to(RIGHT * 2.05 + UP * 0.72)
        lower = pulse(0.13).move_to(RIGHT * 2.05 + DOWN * 0.72)
        self.add(fork, actor)
        self.wait(0.6)
        self.play(actor.animate.move_to(ORIGIN), fork.animate.set_stroke(color=PRIMARY_RED, opacity=0.82), run_time=0.7, rate_func=smooth)
        self.play(FadeOut(actor), FadeIn(upper), FadeIn(lower), fork.animate.set_stroke(color=GRAY_300, opacity=0.58), run_time=0.48)
        self.play(upper.animate.scale(1.16), lower.animate.scale(1.16), run_time=0.35, rate_func=there_and_back)
        self.wait(1.3)


class PressureWallDemo(Scene):
    def construct(self) -> None:
        configure_transparent_scene(self)
        add_name(self, "pressure_wall")
        wall = pressure_wall().move_to(RIGHT * 1.0)
        actor = pulse(0.18).move_to(LEFT * 2.45)
        lane = Line(LEFT * 2.8, RIGHT * 1.0, color=GRAY_200, stroke_width=3.4).set_opacity(0.32)
        self.add(lane, wall, actor)
        self.wait(0.55)
        self.play(actor.animate.move_to(RIGHT * 0.62), lane.animate.set_opacity(0.56), run_time=0.9, rate_func=smooth)
        self.play(wall.animate.shift(RIGHT * 0.18).set_opacity(0.86), actor.animate.scale(1.24), run_time=0.36, rate_func=there_and_back)
        self.play(wall.animate.shift(LEFT * 0.18).set_opacity(0.72), actor.animate.move_to(LEFT * 0.05), run_time=0.45, rate_func=smooth)
        self.wait(1.35)


class ClampPairDemo(Scene):
    def construct(self) -> None:
        configure_transparent_scene(self)
        add_name(self, "clamp_pair")
        clamp = clamp_pair()
        actor = slab(GRAY_600, 1.55, 0.42).move_to(LEFT * 2.4)
        self.add(clamp, actor)
        self.wait(0.55)
        self.play(actor.animate.move_to(ORIGIN), run_time=0.75, rate_func=smooth)
        self.play(clamp[0].animate.shift(RIGHT * 0.25).set_opacity(0.92), clamp[1].animate.shift(LEFT * 0.25).set_opacity(0.92), actor.animate.scale(0.78), run_time=0.45, rate_func=smooth)
        self.play(clamp.animate.set_color(PRIMARY_RED), actor.animate.scale(1.12), run_time=0.35, rate_func=there_and_back)
        self.wait(1.3)


class SleeveChannelDemo(Scene):
    def construct(self) -> None:
        configure_transparent_scene(self)
        add_name(self, "sleeve_channel")
        sleeve = sleeve_channel()
        actor = slab(GRAY_600, 1.25, 0.38).move_to(LEFT * 2.35)
        revealed = neutral_cluster().scale(0.72).move_to(RIGHT * 1.45)
        self.add(sleeve, actor)
        self.wait(0.55)
        self.play(actor.animate.move_to(ORIGIN), sleeve.animate.set_stroke(color=PRIMARY_RED, opacity=0.76), run_time=0.75, rate_func=smooth)
        self.play(Transform(actor, revealed), sleeve.animate.set_stroke(color=GRAY_300, opacity=0.4), run_time=0.85, rate_func=smooth)
        self.play(FadeOut(sleeve), actor.animate.scale(1.05), run_time=0.35, rate_func=there_and_back)
        self.wait(1.35)


class RampPlaneDemo(Scene):
    def construct(self) -> None:
        configure_transparent_scene(self)
        add_name(self, "ramp_plane")
        ramp = ramp_plane()
        actor = pulse(0.18).move_to(LEFT * 1.75 + DOWN * 0.72)
        target = open_slot(0.82, 0.82, opacity=0.38).move_to(RIGHT * 1.75 + UP * 0.72)
        self.add(ramp, target, actor)
        self.wait(0.55)
        self.play(ramp.animate.set_stroke(color=PRIMARY_RED, opacity=0.74), actor.animate.move_to(RIGHT * 1.55 + UP * 0.62), run_time=1.05, rate_func=smooth)
        self.play(FadeOut(ramp), target.animate.set_opacity(0.0), actor.animate.scale(1.14), run_time=0.4, rate_func=there_and_back)
        self.wait(1.35)


class FanGuidesDemo(Scene):
    def construct(self) -> None:
        configure_transparent_scene(self)
        add_name(self, "fan_guides")
        fan = fan_guides()
        actor = pulse(0.18).move_to(ORIGIN)
        outputs = VGroup(*[pulse(0.1, GRAY_500).move_to(point) for point in [RIGHT * 1.8, RIGHT * 1.45 + UP * 0.9, RIGHT * 1.45 + DOWN * 0.9]])
        self.add(fan, actor)
        self.wait(0.55)
        self.play(fan.animate.set_stroke(color=PRIMARY_RED, opacity=0.72), run_time=0.45)
        self.play(FadeIn(outputs), actor.animate.scale(1.18), run_time=0.55, rate_func=there_and_back)
        self.play(fan.animate.set_stroke(color=GRAY_300, opacity=0.42), outputs.animate.set_fill(PRIMARY_RED, opacity=1), run_time=0.45)
        self.wait(1.35)


class HingePivotDemo(Scene):
    def construct(self) -> None:
        configure_transparent_scene(self)
        add_name(self, "hinge_pivot")
        hinge = hinge_pivot()
        actor = pulse(0.14).move_to(RIGHT * 1.75)
        self.add(hinge, actor)
        self.wait(0.55)
        self.play(Rotate(hinge[1], angle=0.85, about_point=ORIGIN), actor.animate.move_to(RIGHT * 1.14 + UP * 1.3), hinge[2].animate.set_stroke(color=PRIMARY_RED, opacity=0.8), run_time=0.9, rate_func=smooth)
        self.play(hinge[0].animate.set_fill(PRIMARY_RED, opacity=1), actor.animate.scale(1.16), run_time=0.35, rate_func=there_and_back)
        self.wait(1.35)


class ArcHandoffDemo(Scene):
    def construct(self) -> None:
        configure_transparent_scene(self)
        add_name(self, "arc_handoff")
        guide = arc_handoff()
        actor = pulse(0.16).move_to(LEFT * 1.18 + UP * 0.62)
        self.add(guide, actor)
        self.wait(0.55)
        self.play(guide[0].animate.set_stroke(color=PRIMARY_RED, opacity=0.78), actor.animate.move_to(UP * 1.45), run_time=0.55, rate_func=smooth)
        self.play(actor.animate.move_to(RIGHT * 1.18 + UP * 0.62), run_time=0.55, rate_func=smooth)
        self.play(guide.animate.set_opacity(0.38), actor.animate.scale(1.14), run_time=0.35, rate_func=there_and_back)
        self.wait(1.25)


class BumperStopDemo(Scene):
    def construct(self) -> None:
        configure_transparent_scene(self)
        add_name(self, "bumper_stop")
        bumper = bumper_stop().move_to(RIGHT * 1.25)
        actor = pulse(0.18).move_to(LEFT * 2.25)
        self.add(bumper, actor)
        self.wait(0.55)
        self.play(actor.animate.move_to(RIGHT * 0.82), run_time=0.75, rate_func=smooth)
        self.play(bumper.animate.set_color(PRIMARY_RED), actor.animate.move_to(LEFT * 0.28 + UP * 0.8), run_time=0.48, rate_func=smooth)
        self.play(bumper.animate.set_opacity(0.42), actor.animate.scale(1.14), run_time=0.35, rate_func=there_and_back)
        self.wait(1.3)


class CompressionChannelDemo(Scene):
    def construct(self) -> None:
        configure_transparent_scene(self)
        add_name(self, "compression_channel")
        channel = compression_channel()
        actor = slab(GRAY_600, 1.15, 0.52).move_to(LEFT * 2.25)
        self.add(channel, actor)
        self.wait(0.55)
        self.play(actor.animate.move_to(LEFT * 0.25).stretch(0.58, dim=1), channel.animate.set_stroke(color=PRIMARY_RED, opacity=0.76), run_time=0.85, rate_func=smooth)
        self.play(actor.animate.move_to(RIGHT * 1.55).stretch(1.72, dim=1), channel.animate.set_stroke(color=GRAY_300, opacity=0.42), run_time=0.55, rate_func=smooth)
        self.play(FadeOut(channel), actor.animate.scale(1.08), run_time=0.35, rate_func=there_and_back)
        self.wait(1.25)


class CorridorRailsDemo(Scene):
    def construct(self) -> None:
        configure_transparent_scene(self)
        add_name(self, "corridor_rails")
        rails = corridor_rails()
        actor = pulse(0.16).move_to(LEFT * 2.25)
        self.add(rails, actor)
        self.wait(0.55)
        self.play(actor.animate.move_to(ORIGIN), rails[2].animate.set_color(PRIMARY_RED), run_time=0.75, rate_func=smooth)
        self.play(actor.animate.scale(0.78), rails[2][0].animate.shift(RIGHT * 0.22), rails[2][1].animate.shift(LEFT * 0.22), run_time=0.38, rate_func=there_and_back)
        self.play(actor.animate.move_to(RIGHT * 2.25), rails.animate.set_opacity(0.36), run_time=0.65, rate_func=smooth)
        self.wait(1.25)


class CradleCatchDemo(Scene):
    def construct(self) -> None:
        configure_transparent_scene(self)
        add_name(self, "cradle_catch")
        cradle = cradle_catch()
        actor = pulse(0.18).move_to(LEFT * 1.85 + UP * 1.0)
        self.add(cradle, actor)
        self.wait(0.55)
        self.play(actor.animate.move_to(ORIGIN + DOWN * 0.38), cradle.animate.set_color(PRIMARY_RED), run_time=0.78, rate_func=smooth)
        self.play(cradle.animate.set_opacity(0.42), actor.animate.scale(1.16), run_time=0.38, rate_func=there_and_back)
        self.wait(1.35)


class BalanceBeamDemo(Scene):
    def construct(self) -> None:
        configure_transparent_scene(self)
        add_name(self, "balance_beam")
        beam = balance_beam()
        left_load = pulse(0.16, GRAY_500).move_to(LEFT * 1.2 + UP * 0.28)
        right_load = pulse(0.16, PRIMARY_RED).move_to(RIGHT * 1.2 + UP * 0.28)
        self.add(beam, left_load, right_load)
        self.wait(0.55)
        self.play(Rotate(beam[0], angle=-0.18, about_point=ORIGIN), right_load.animate.shift(DOWN * 0.32), left_load.animate.shift(UP * 0.2), run_time=0.65, rate_func=smooth)
        self.play(Rotate(beam[0], angle=0.18, about_point=ORIGIN), right_load.animate.shift(UP * 0.32), left_load.animate.shift(DOWN * 0.2), run_time=0.55, rate_func=smooth)
        self.play(right_load.animate.scale(1.14), run_time=0.35, rate_func=there_and_back)
        self.wait(1.25)


class DeformationWaveDemo(Scene):
    def construct(self) -> None:
        configure_transparent_scene(self)
        add_name(self, "deformation_wave")
        wave = deformation_wave()
        actor = slab(GRAY_600, 0.54, 0.54).move_to(LEFT * 2.15)
        self.add(wave, actor)
        self.wait(0.55)
        self.play(actor.animate.move_to(ORIGIN).stretch(1.45, dim=0), wave.animate.set_stroke(color=PRIMARY_RED, opacity=0.78), run_time=0.85, rate_func=smooth)
        self.play(actor.animate.move_to(RIGHT * 2.1).stretch(0.7, dim=0), wave.animate.set_opacity(0.38), run_time=0.65, rate_func=smooth)
        self.wait(1.3)


class SettleEchoDemo(Scene):
    def construct(self) -> None:
        configure_transparent_scene(self)
        add_name(self, "settle_echo")
        echoes = settle_echo()
        actor = pulse(0.18).move_to(LEFT * 1.7 + UP * 0.6)
        self.add(echoes, actor)
        self.wait(0.55)
        self.play(actor.animate.move_to(ORIGIN), run_time=0.65, rate_func=smooth)
        self.play(echoes.animate.set_stroke(color=PRIMARY_RED, opacity=0.72), actor.animate.scale(1.18), run_time=0.45, rate_func=there_and_back)
        self.play(echoes.animate.scale(1.12).set_opacity(0.28), run_time=0.45)
        self.wait(1.25)


class EdgeTensionMarkerDemo(Scene):
    def construct(self) -> None:
        configure_transparent_scene(self)
        add_name(self, "edge_tension_marker")
        marker = edge_tension_marker().move_to(RIGHT * 0.85)
        actor = pulse(0.18).move_to(LEFT * 1.9)
        self.add(marker, actor)
        self.wait(0.55)
        self.play(actor.animate.move_to(RIGHT * 0.65), marker.animate.set_color(PRIMARY_RED), run_time=0.85, rate_func=smooth)
        self.play(actor.animate.shift(LEFT * 0.28), marker.animate.set_opacity(0.44), run_time=0.42, rate_func=smooth)
        self.play(actor.animate.scale(1.14), run_time=0.35, rate_func=there_and_back)
        self.wait(1.25)


class KeystoneLockDemo(Scene):
    def construct(self) -> None:
        configure_transparent_scene(self)
        add_name(self, "keystone_lock")
        lock = keystone_lock()
        key = slab(PRIMARY_RED, 0.42, 0.74).move_to(UP * 1.75)
        self.add(lock, key)
        self.wait(0.55)
        self.play(key.animate.move_to(ORIGIN), lock[2].animate.set_fill(PRIMARY_RED, opacity=0.85), run_time=0.75, rate_func=smooth)
        self.play(lock.animate.scale(1.08), key.animate.scale(0.72), run_time=0.36, rate_func=there_and_back)
        self.wait(1.35)


class LatchAnchorDemo(Scene):
    def construct(self) -> None:
        configure_transparent_scene(self)
        add_name(self, "latch_anchor")
        latch = latch_anchor()
        actor = pulse(0.16).move_to(LEFT * 2.1 + UP * 0.75)
        self.add(latch, actor)
        self.wait(0.55)
        self.play(actor.animate.move_to(RIGHT * 0.72 + DOWN * 0.48), latch.animate.set_color(PRIMARY_RED), run_time=0.8, rate_func=smooth)
        self.play(actor.animate.scale(1.16), latch.animate.set_opacity(0.46), run_time=0.36, rate_func=there_and_back)
        self.wait(1.35)


class LayeredStackDemo(Scene):
    def construct(self) -> None:
        configure_transparent_scene(self)
        add_name(self, "layered_stack")
        stack = layered_stack().move_to(ORIGIN)
        self.add(stack)
        self.wait(0.55)
        self.play(stack[0].animate.shift(LEFT * 0.42 + UP * 0.24), stack[1].animate.set_fill(PRIMARY_RED, opacity=0.78), stack[2].animate.shift(RIGHT * 0.42 + DOWN * 0.24), run_time=0.75, rate_func=smooth)
        self.play(stack.animate.arrange(DOWN, buff=0.16).move_to(ORIGIN), run_time=0.55, rate_func=smooth)
        self.wait(1.35)


class MagnetCaptureDemo(Scene):
    def construct(self) -> None:
        configure_transparent_scene(self)
        add_name(self, "magnet_capture")
        magnet = magnet_capture()
        actor = pulse(0.16).move_to(LEFT * 2.15)
        self.add(magnet, actor)
        self.wait(0.55)
        self.play(actor.animate.move_to(ORIGIN), magnet.animate.set_color(PRIMARY_RED), run_time=0.8, rate_func=smooth)
        self.play(magnet.animate.set_opacity(0.38), actor.animate.scale(1.18), run_time=0.38, rate_func=there_and_back)
        self.wait(1.35)


class NegativeSpaceFrameDemo(Scene):
    def construct(self) -> None:
        configure_transparent_scene(self)
        add_name(self, "negative_space_frame")
        frame = negative_space_frame()
        actor = pulse(0.16).move_to(LEFT * 2.15)
        self.add(frame, actor)
        self.wait(0.55)
        self.play(actor.animate.move_to(ORIGIN), frame.animate.set_opacity(0.74), run_time=0.8, rate_func=smooth)
        self.play(frame.animate.set_fill(GRAY_200, opacity=0.32), actor.animate.scale(1.18), run_time=0.4, rate_func=there_and_back)
        self.wait(1.35)


class ParallaxPlanesDemo(Scene):
    def construct(self) -> None:
        configure_transparent_scene(self)
        add_name(self, "parallax_planes")
        planes = parallax_planes()
        actor = pulse(0.14).move_to(LEFT * 2.15 + UP * 0.55)
        self.add(planes, actor)
        self.wait(0.55)
        self.play(planes[0].animate.shift(LEFT * 0.35), planes[2].animate.shift(RIGHT * 0.45), actor.animate.move_to(RIGHT * 0.65 + DOWN * 0.34), run_time=0.85, rate_func=smooth)
        self.play(planes[2].animate.set_fill(PRIMARY_RED, opacity=0.72), actor.animate.scale(1.16), run_time=0.35, rate_func=there_and_back)
        self.wait(1.35)


class ReceiverSlotDemo(Scene):
    def construct(self) -> None:
        configure_transparent_scene(self)
        add_name(self, "receiver_slot")
        slot = open_slot(4.1, 2.15, opacity=0.42).move_to(ORIGIN)
        card = slab(GRAY_600, 1.45, 0.62).move_to(LEFT * 3.35)
        actor = pulse(0.14).move_to(LEFT * 2.0 + UP * 0.72)
        terminal = terminal_brackets_around(card.copy().move_to(ORIGIN), padding=0.34)
        self.add(slot, card, actor)
        self.wait(0.7)
        self.play(slot.animate.set_stroke(color=PRIMARY_RED, opacity=0.74), actor.animate.move_to(LEFT * 1.35 + UP * 0.72), run_time=0.55, rate_func=smooth)
        self.play(card.animate.move_to(ORIGIN), actor.animate.move_to(RIGHT * 1.15 + UP * 0.72), run_time=1.2, rate_func=smooth)
        self.play(FadeOut(slot), FadeOut(actor), FadeIn(terminal), run_time=0.45)
        self.play(card.animate.scale(1.05), run_time=0.35, rate_func=there_and_back)
        self.wait(1.2)


class TerminalBracketsDemo(Scene):
    def construct(self) -> None:
        configure_transparent_scene(self)
        add_name(self, "terminal_brackets_around")
        cluster = neutral_cluster().scale(1.15).move_to(ORIGIN)
        brackets = terminal_brackets_around(cluster, padding=0.44)
        guide = open_slot(cluster.width + 1.0, cluster.height + 0.92, color=GRAY_200, opacity=0.32)
        self.add(guide, cluster)
        self.wait(0.7)
        self.play(Create(brackets), guide.animate.set_opacity(0.0), run_time=0.8, rate_func=smooth)
        self.play(cluster.animate.scale(1.04), run_time=0.35, rate_func=there_and_back)
        self.wait(1.55)


class BridgeLaneDemo(Scene):
    def construct(self) -> None:
        configure_transparent_scene(self)
        add_name(self, "bridge_lane")
        lane = bridge_lane(width=4.4, gap=1.1, opacity=0.46)
        source = neutral_cluster().scale(0.9).move_to(LEFT * 4.0)
        target_slot = open_slot(2.1, 1.45, opacity=0.46).move_to(RIGHT * 3.6)
        actor = pulse(0.15).move_to(LEFT * 2.25 + UP * 0.8)
        final = neutral_cluster().scale(0.9).move_to(RIGHT * 3.6)
        self.add(lane, source, target_slot, actor)
        self.wait(0.7)
        self.play(lane.animate.set_opacity(0.86), actor.animate.move_to(LEFT * 1.7 + UP * 0.8), run_time=0.5, rate_func=smooth)
        self.play(Transform(source, final), actor.animate.move_to(RIGHT * 2.05 + UP * 0.8), run_time=1.55, rate_func=smooth)
        self.play(FadeOut(lane), FadeOut(target_slot), FadeOut(actor), run_time=0.45)
        self.wait(1.15)


class RhythmGateDemo(Scene):
    def construct(self) -> None:
        configure_transparent_scene(self)
        add_name(self, "rhythm_gate")
        rail = Line(LEFT * 4.75, RIGHT * 4.75, color=GRAY_200, stroke_width=4).set_opacity(0.42)
        gates = VGroup(gate_column().move_to(LEFT * 2.2), gate_column().move_to(ORIGIN), gate_column().move_to(RIGHT * 2.2))
        actor = pulse(0.2).move_to(LEFT * 4.45)
        marks = VGroup(*[Rectangle(width=0.46, height=0.12, stroke_width=0, fill_color=GRAY_300, fill_opacity=0.75).move_to(RIGHT * x + DOWN * 2.25) for x in (-2.2, 0, 2.2)])
        self.add(rail, gates, marks, actor)
        self.wait(0.55)
        for index, x in enumerate([-2.2, 0, 2.2]):
            gate = gates[index]
            self.play(actor.animate.move_to(RIGHT * (x - 0.68)), run_time=0.45, rate_func=smooth)
            self.play(gate[0].animate.shift(UP * 0.28), gate[1].animate.shift(DOWN * 0.28), gate[2].animate.set_color(PRIMARY_RED), gate[3].animate.set_color(PRIMARY_RED), run_time=0.35)
            self.play(actor.animate.move_to(RIGHT * (x + 0.68)), marks[index].animate.set_fill(PRIMARY_RED, opacity=1), run_time=0.42)
            self.play(gate[0].animate.shift(DOWN * 0.28), gate[1].animate.shift(UP * 0.28), gate[2].animate.set_color(GRAY_200), gate[3].animate.set_color(GRAY_200), marks[index].animate.set_fill(GRAY_500, opacity=0.75), run_time=0.25)
        self.play(actor.animate.move_to(RIGHT * 4.45), run_time=0.45, rate_func=smooth)
        self.play(FadeOut(gates), rail.animate.set_opacity(0.16), run_time=0.45)
        self.wait(1.0)


class TimeRailDemo(Scene):
    def construct(self) -> None:
        configure_transparent_scene(self)
        add_name(self, "time_rail")
        rail = time_rail(ticks=4).move_to(LEFT * 3.7)
        active = Line(LEFT * 3.7 + DOWN * 2.3, LEFT * 3.7 + DOWN * 2.3, color=PRIMARY_RED, stroke_width=5)
        cards = VGroup(*[open_slot(2.2, 0.62, opacity=0.38).move_to(LEFT * 0.35 + UP * y) for y in (-1.55, -0.5, 0.55, 1.6)])
        fills = VGroup(*[slab(GRAY_600 if i % 2 else GRAY_400, 1.72, 0.38).move_to(cards[i]) for i in range(4)])
        self.add(rail, active, cards)
        self.wait(0.7)
        for index, y in enumerate([-1.55, -0.5, 0.55, 1.6]):
            end_y = -2.3 + (index + 1) * (4.6 / 4)
            branch = Line(LEFT * 3.48 + UP * end_y, fills[index].get_left(), color=GRAY_200, stroke_width=2.2).set_opacity(0.56)
            self.play(active.animate.put_start_and_end_on(LEFT * 3.7 + DOWN * 2.3, LEFT * 3.7 + UP * end_y), Create(branch), run_time=0.45, rate_func=smooth)
            self.play(FadeIn(fills[index]), cards[index].animate.set_opacity(0.12), run_time=0.35)
        self.play(FadeOut(cards), FadeIn(terminal_brackets_around(fills, padding=0.26)), run_time=0.55)
        self.wait(1.05)


class MaskWindowDemo(Scene):
    def construct(self) -> None:
        configure_transparent_scene(self)
        add_name(self, "mask_window")
        row = VGroup(*[slab(GRAY_600 if i % 2 else GRAY_400, 1.1, 0.42).move_to(LEFT * 3.15 + RIGHT * i * 2.1 + UP * 0.9) for i in range(4)])
        slots = VGroup(*[open_slot(1.1, 0.88, opacity=0.34).move_to(row[i].get_center() + DOWN * 1.85) for i in range(4)])
        mask = mask_window(height=3.7).move_to(LEFT * 4.25)
        outputs = VGroup(*[pulse(0.24 if i == 3 else 0.18, PRIMARY_RED if i == 3 else GRAY_500).move_to(slots[i]) for i in range(4)])
        self.add(row, slots, mask)
        self.wait(0.7)
        for index, x in enumerate([-3.15, -1.05, 1.05, 3.15]):
            line = Line(row[index].get_bottom(), slots[index].get_top(), color=PRIMARY_RED, stroke_width=3.4)
            self.play(mask.animate.move_to(RIGHT * x), run_time=0.45, rate_func=smooth)
            self.play(Create(line), FadeIn(outputs[index]), slots[index].animate.set_opacity(0.12), run_time=0.35)
            self.play(line.animate.set_color(GRAY_300).set_opacity(0.3), run_time=0.18)
        self.play(FadeOut(mask), FadeOut(row), FadeOut(slots), outputs.animate.arrange(RIGHT, buff=0.28).move_to(ORIGIN), run_time=0.65, rate_func=smooth)
        self.play(FadeIn(terminal_brackets_around(outputs, padding=0.34)), run_time=0.45)
        self.wait(1.0)


@dataclass(frozen=True)
class ComponentDemo:
    slug: str
    name: str
    scene: type[Scene]
    note: str


COMPONENTS = [
    ComponentDemo("slab", "slab", SlabDemo, "Solid rectangular block used for bars, rails, cards, and resolved payloads."),
    ComponentDemo("pulse", "pulse", PulseDemo, "Primary-red active actor used to carry handoffs, routes, and proof beats."),
    ComponentDemo("open-slot", "open_slot", OpenSlotDemo, "Open receiver outline that reserves a destination without enclosing the actor."),
    ComponentDemo("source-slot", "source_slot", SourceSlotDemo, "Bracketed launch slot for a source-side active actor."),
    ComponentDemo("target-slot", "target_slot", TargetSlotDemo, "Mirrored bracketed landing slot for a receiver-side active actor."),
    ComponentDemo("bridge-lane", "bridge_lane", BridgeLaneDemo, "Guided transfer lane between source and destination zones."),
    ComponentDemo("gate-column", "gate_column", GateColumnDemo, "Prepared vertical gate that opens around the active actor."),
    ComponentDemo("time-rail", "time_rail", TimeRailDemo, "Left-side timeline rail that narrates progressive card activation."),
    ComponentDemo("mask-window", "mask_window", MaskWindowDemo, "Moving mask window that reveals transferred outputs."),
    ComponentDemo("terminal-brackets", "terminal_brackets", TerminalBracketsOnlyDemo, "Separated corner marks used as a terminal resolved-state cue."),
    ComponentDemo("terminal-brackets-around", "terminal_brackets_around", TerminalBracketsDemo, "Convenience wrapper that sizes terminal brackets around a target cluster."),
    ComponentDemo("neutral-cluster", "neutral_cluster", NeutralClusterDemo, "Reusable quiet gray payload cluster for transfer and resolve demos."),
    ComponentDemo("aperture-shutters", "aperture_shutters", ApertureShuttersDemo, "Reusable opening shutters extracted from aperture-style transition spikes."),
    ComponentDemo("merge-funnel", "merge_funnel", MergeFunnelDemo, "Converging guide rails for combining two inputs into one output."),
    ComponentDemo("orbit-guides", "orbit_guides", OrbitGuidesDemo, "Circular guide marks for anchored orbit and return-motion explanations."),
    ComponentDemo("fork-guides", "fork_guides", ForkGuidesDemo, "Branching guide rails for diverging one active actor into parallel outcomes."),
    ComponentDemo("pressure-wall", "pressure_wall", PressureWallDemo, "Compact resistance marker for pressure, constraint, and boundary-contact scenes."),
    ComponentDemo("clamp-pair", "clamp_pair", ClampPairDemo, "Opposing vertical clamp bars extracted from compression and clamp-close spikes."),
    ComponentDemo("sleeve-channel", "sleeve_channel", SleeveChannelDemo, "Three-sided reveal sleeve for contained payload transitions."),
    ComponentDemo("ramp-plane", "ramp_plane", RampPlaneDemo, "Inclined support plane for lift, ramp, and assisted-transfer scenes."),
    ComponentDemo("fan-guides", "fan_guides", FanGuidesDemo, "Radial guide set for fan-out, splay, and multi-target distribution scenes."),
    ComponentDemo("hinge-pivot", "hinge_pivot", HingePivotDemo, "Pivot, arm, and arc guide for hinge or swing-motion explanations."),
    ComponentDemo("arc-handoff", "arc_handoff", ArcHandoffDemo, "Curved route with source and target points for arced handoff scenes."),
    ComponentDemo("bumper-stop", "bumper_stop", BumperStopDemo, "Angled stop and wall for deflecting an active actor away from a boundary."),
    ComponentDemo("compression-channel", "compression_channel", CompressionChannelDemo, "Narrow parallel rails for squeezing or releasing a payload."),
    ComponentDemo("corridor-rails", "corridor_rails", CorridorRailsDemo, "Long guide rails with a central squeeze point for corridor passages."),
    ComponentDemo("cradle-catch", "cradle_catch", CradleCatchDemo, "Lower catch basin and support pads for landing or settling scenes."),
    ComponentDemo("balance-beam", "balance_beam", BalanceBeamDemo, "Fulcrum and beam primitive for counterweight and counterlift balance scenes."),
    ComponentDemo("deformation-wave", "deformation_wave", DeformationWaveDemo, "Elastic wave guide for deformation, flex, and shape-change proof beats."),
    ComponentDemo("settle-echo", "settle_echo", SettleEchoDemo, "Concentric settling rings for echo, impact, and delayed-resolution scenes."),
    ComponentDemo("edge-tension-marker", "edge_tension_marker", EdgeTensionMarkerDemo, "Boundary wall and tether marker for edge-pressure compositions."),
    ComponentDemo("keystone-lock", "keystone_lock", KeystoneLockDemo, "Central locking block with side supports for keystone-style closures."),
    ComponentDemo("latch-anchor", "latch_anchor", LatchAnchorDemo, "Anchor dot and hook path for latched handoff scenes."),
    ComponentDemo("layered-stack", "layered_stack", LayeredStackDemo, "Offset layer stack for progressive reveal and peel-style compositions."),
    ComponentDemo("magnet-capture", "magnet_capture", MagnetCaptureDemo, "Opposing capture arcs and poles for magnetic attraction scenes."),
    ComponentDemo("negative-space-frame", "negative_space_frame", NegativeSpaceFrameDemo, "Four-part frame that leaves an intentional central opening."),
    ComponentDemo("parallax-planes", "parallax_planes", ParallaxPlanesDemo, "Offset depth planes for parallax transfer and layered motion scenes."),
    ComponentDemo("receiver-slot", "receiver_slot", ReceiverSlotDemo, "Composite receiver-slot pattern with pending outline, moving payload, and terminal mark."),
    ComponentDemo("rhythm-gate", "rhythm_gate", RhythmGateDemo, "Composite cadence pattern using several gate columns along a rail."),
]

SCENES = {component.slug: component for component in COMPONENTS}


class _Args(argparse.Namespace):
    quality: str
    component: str
    skip_gifs: bool


def parse_args() -> _Args:
    parser = argparse.ArgumentParser(description="Render common component GIF demos.")
    parser.add_argument("--quality", choices=("low", "medium", "high", "production", "4k"), default="low")
    parser.add_argument("--component", choices=("all", *SCENES.keys()), default="all")
    parser.add_argument("--skip-gifs", action="store_true")
    return parser.parse_args(namespace=_Args())


def selected_components(args: _Args) -> list[str]:
    return list(SCENES.keys()) if args.component == "all" else [args.component]


def write_catalog() -> None:
    DOC_README.parent.mkdir(parents=True, exist_ok=True)
    rows = "\n".join(
        f"| `{component.name}` | ![{component.name}](../.specs/assets/component-demos/{component.slug}.gif) | {component.note} |"
        for component in COMPONENTS
    )
    sections = "\n\n".join(
        "\n".join(
            [
                f"## `{component.name}`",
                "",
                component.note,
                "",
                f"![{component.name}](../.specs/assets/component-demos/{component.slug}.gif)",
            ]
        )
        for component in COMPONENTS
    )
    DOC_README.write_text(
        "\n".join(
            [
                "# Component GIF Catalog",
                "",
                "This catalog collects every component GIF generated so far for the shared Manim component library.",
                "Every entry is generated from the component demo manifest in `spikes/component-library-demos/main.py`,",
                "so each component has a matching GIF and visible component name.",
                "",
                "Regenerate the current set with:",
                "",
                "```powershell",
                "uv run --script spikes/component-library-demos/main.py --quality low",
                "```",
                "",
                "Source demos live in `spikes/component-library-demos/`. Full render outputs live in",
                "`videos/component-library-demos/components/`. Doc-ready GIFs live in",
                "`.specs/assets/component-demos/`.",
                "",
                "## Current Components",
                "",
                "| Component | Demo | Notes |",
                "| --- | --- | --- |",
                rows,
                "",
                sections,
                "",
            ]
        ),
        encoding="utf-8",
    )


def main() -> int:
    args = parse_args()
    DOC_GIF_DIR.mkdir(parents=True, exist_ok=True)
    for slug in selected_components(args):
        component = SCENES[slug]
        component_dir = OUTPUT_DIR / "components" / slug
        rendered = render_scene(Path(__file__).resolve(), component.scene.__name__, component_dir, quality=args.quality, output_stem=slug)
        if not args.skip_gifs:
            gif_path = component_dir / f"{slug}.gif"
            convert_video_to_gif(rendered.video, gif_path)
            shutil.copy2(gif_path, DOC_GIF_DIR / gif_path.name)
            print(f"gif={gif_path}")
            print(f"doc_gif={DOC_GIF_DIR / gif_path.name}")
        print(f"video={rendered.video}")
        print(f"poster={rendered.poster}")
    if args.component == "all" and not args.skip_gifs:
        write_catalog()
        print(f"catalog={DOC_README}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
