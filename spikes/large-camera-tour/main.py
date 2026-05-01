#!/usr/bin/env -S uv run --script
# /// script
# dependencies = [
#   "manim>=0.20.0",
# ]
# ///

from __future__ import annotations

import argparse
import os
import shutil
import subprocess
import sys
from pathlib import Path

from manim import (
    DOWN,
    LEFT,
    ORIGIN,
    PI,
    RIGHT,
    UP,
    AnimationGroup,
    Circle,
    Create,
    Dot,
    FadeIn,
    FadeOut,
    GrowFromCenter,
    LaggedStart,
    Line,
    MoveAlongPath,
    MovingCameraScene,
    Rectangle,
    Rotate,
    Text,
    Transform,
    VGroup,
    VMobject,
    WHITE,
    linear,
    smooth,
    there_and_back,
)

SPIKE_DIR = Path(__file__).resolve().parent
REPO_ROOT = SPIKE_DIR.parent.parent
SPIKE_NAME = SPIKE_DIR.name
OUTPUT_DIR = REPO_ROOT / "videos" / SPIKE_NAME
STAGING_DIR = OUTPUT_DIR / ".manim"
VIDEO_PATH = OUTPUT_DIR / f"{SPIKE_NAME}.webm"
POSTER_PATH = OUTPUT_DIR / f"{SPIKE_NAME}.png"

BLACK = "#000000"
PRIMARY_RED = "#9e1b32"
WHITE_TOKEN = "#ffffff"
GRAY = "#333e48"
PAGE_BACKGROUND = "#f7f7f7"
GRAY_100 = "#e7e7e7"
GRAY_200 = "#cfcfcf"
GRAY_300 = "#b5b5b5"
GRAY_400 = "#9c9c9c"
GRAY_500 = "#828282"
GRAY_600 = "#696969"
GRAY_700 = "#4f4f4f"
GRAY_900 = "#1c1c1c"
HIGHLIGHT_RED = "#ffccd5"
FONT_FAMILY = "Arial"

A_CENTER = LEFT * 9.9 + UP * 4.15
B_CENTER = RIGHT * 9.65 + UP * 4.65
C_CENTER = LEFT * 8.95 + DOWN * 4.85
D_CENTER = RIGHT * 9.2 + DOWN * 4.7
HUB_CENTER = ORIGIN
FULL_MAP_WIDTH = 33.0


class _Args(argparse.Namespace):
    quality: str


def parse_args() -> _Args:
    parser = argparse.ArgumentParser(description="Render the large-camera-tour spike.")
    parser.add_argument("--quality", choices=("low", "medium", "high", "production", "4k"), default="medium")
    return parser.parse_args(namespace=_Args())


def quality_flag(quality: str) -> str:
    return {"low": "-ql", "medium": "-qm", "high": "-qh", "production": "-qp", "4k": "-qk"}[quality]


def render_command(args: _Args, poster: bool) -> list[str]:
    STAGING_DIR.mkdir(parents=True, exist_ok=True)
    target = POSTER_PATH if poster else VIDEO_PATH
    command = [
        sys.executable,
        "-m",
        "manim",
        "render",
        quality_flag(args.quality),
        "-r",
        "1600,900",
        "-o",
        target.stem,
        "--media_dir",
        str(STAGING_DIR),
    ]
    command.append("-s" if poster else "--format=webm")
    if not poster:
        command.append("-t")
    command.extend([str(Path(__file__).resolve()), "LargeCameraTourScene"])
    return command


def promote(target_name: str, destination: Path) -> None:
    matches = sorted(STAGING_DIR.glob(f"**/{target_name}"))
    if not matches:
        raise FileNotFoundError(target_name)
    destination.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(max(matches, key=lambda path: path.stat().st_mtime), destination)


def panel(width: float, height: float) -> Rectangle:
    return Rectangle(
        width=width,
        height=height,
        stroke_color=GRAY_300,
        stroke_width=2,
        fill_color=WHITE_TOKEN,
        fill_opacity=0.82,
    )


def block(color: str, width: float, height: float, opacity: float = 1.0) -> Rectangle:
    return Rectangle(width=width, height=height, stroke_width=0, fill_color=color, fill_opacity=opacity)


def outline_slot(width: float, height: float) -> Rectangle:
    return Rectangle(width=width, height=height, stroke_color=GRAY_400, stroke_width=2, fill_opacity=0)


def label(text: str) -> Text:
    return Text(text, font=FONT_FAMILY, font_size=22, color=GRAY_700)


def polyline(points: list, color: str, stroke_width: float, opacity: float = 1.0) -> VMobject:
    route = VMobject()
    route.set_points_as_corners(points)
    route.set_stroke(color=color, width=stroke_width, opacity=opacity)
    return route


def grid_lines() -> VGroup:
    lines = VGroup()
    for x in range(-14, 15, 2):
        lines.add(Line([x, -7.2, 0], [x, 7.2, 0], color=GRAY_100, stroke_width=1).set_opacity(0.7))
    for y in range(-6, 7, 2):
        lines.add(Line([-14.2, y, 0], [14.2, y, 0], color=GRAY_100, stroke_width=1).set_opacity(0.7))
    return lines


class LargeCameraTourScene(MovingCameraScene):
    def construct(self) -> None:
        self.camera.background_color = WHITE
        self.camera.frame.set(width=FULL_MAP_WIDTH).move_to(ORIGIN)

        stage = Rectangle(
            width=28.8,
            height=15.0,
            stroke_color=GRAY_100,
            stroke_width=1,
            fill_color=PAGE_BACKGROUND,
            fill_opacity=0.97,
        )
        grid = grid_lines()

        route_ab = polyline([A_CENTER + RIGHT * 2.85, [-2.4, 4.45, 0], B_CENTER + LEFT * 2.75], GRAY_400, 4, 0.48)
        route_bc = polyline([B_CENTER + DOWN * 2.0, [4.6, 0.0, 0], [-3.0, -0.2, 0], C_CENTER + UP * 2.05], GRAY_400, 4, 0.4)
        route_cd = polyline([C_CENTER + RIGHT * 3.0, [-1.2, -5.3, 0], [3.4, -4.9, 0], D_CENTER + LEFT * 3.0], GRAY_400, 4, 0.48)
        route_da = polyline([D_CENTER + UP * 1.7, [7.8, 0.5, 0], [2.0, 1.2, 0], A_CENTER + DOWN * 2.0], GRAY_400, 2.5, 0.22)
        routes = VGroup(route_ab, route_bc, route_cd, route_da)

        a_panel, a_group = self._build_compression_segment()
        b_panel, b_group = self._build_orbit_segment()
        c_panel, c_group = self._build_fork_segment()
        d_panel, d_group = self._build_merge_segment()
        hub = self._build_hub_segment()

        traveler = Dot(A_CENTER + RIGHT * 2.85, radius=0.13, color=PRIMARY_RED)
        traveler.set_z_index(10)

        self.add(stage, grid, routes, hub, a_panel, b_panel, c_panel, d_panel, a_group, b_group, c_group, d_group, traveler)
        self.wait(2.8)

        self.play(self.camera.frame.animate.set(width=8.25).move_to(A_CENTER), run_time=2.0, rate_func=smooth)
        self._animate_compression_segment(a_group, traveler)
        self.wait(0.6)
        self.play(self.camera.frame.animate.set(width=13.5).move_to(A_CENTER), run_time=0.8, rate_func=smooth)

        self.play(
            self.camera.frame.animate.set(width=13.5).move_to(B_CENTER),
            MoveAlongPath(traveler, route_ab),
            run_time=2.8,
            rate_func=smooth,
        )
        self.play(self.camera.frame.animate.set(width=9.2).move_to(B_CENTER), run_time=0.9, rate_func=smooth)
        self._animate_orbit_segment(b_group, traveler)
        self.wait(0.6)

        self.play(
            self.camera.frame.animate.set(width=8.9).move_to(C_CENTER),
            MoveAlongPath(traveler, route_bc),
            run_time=3.0,
            rate_func=smooth,
        )
        self._animate_fork_segment(c_group, traveler)
        self.wait(0.5)

        self.play(
            self.camera.frame.animate.set(width=9.0).move_to(D_CENTER),
            MoveAlongPath(traveler, route_cd),
            run_time=2.8,
            rate_func=smooth,
        )
        self._animate_merge_segment(d_group, traveler)

        final_route = VGroup(
            route_ab.copy().set_stroke(PRIMARY_RED, width=5, opacity=0.9),
            route_bc.copy().set_stroke(PRIMARY_RED, width=5, opacity=0.82),
            route_cd.copy().set_stroke(PRIMARY_RED, width=5, opacity=0.9),
        )
        final_route.set_z_index(4)
        self.play(
            self.camera.frame.animate.set(width=FULL_MAP_WIDTH).move_to(ORIGIN),
            traveler.animate.move_to(D_CENTER + RIGHT * 2.38).scale(1.25),
            run_time=2.4,
            rate_func=smooth,
        )
        self.play(Create(final_route), run_time=1.1, rate_func=smooth)
        self.play(traveler.animate.scale(1 / 1.25), run_time=0.35, rate_func=there_and_back)
        self.wait(6.6)

    def _build_compression_segment(self) -> tuple[VGroup, VGroup]:
        body = panel(6.7, 4.05).move_to(A_CENTER)
        title = label("compress").move_to(A_CENTER + LEFT * 2.05 + UP * 1.65)
        intake_lane = Line(A_CENTER + LEFT * 2.4, A_CENTER + LEFT * 0.25, color=GRAY_300, stroke_width=5).set_opacity(0.6)
        release_lane = Line(A_CENTER + RIGHT * 0.8, A_CENTER + RIGHT * 2.45, color=GRAY_300, stroke_width=5).set_opacity(0.6)

        chips = VGroup(
            block(GRAY_900, 1.45, 0.38).move_to(A_CENTER + LEFT * 2.05 + UP * 0.82),
            block(GRAY_600, 1.15, 0.34).move_to(A_CENTER + LEFT * 2.15 + UP * 0.24),
            block(GRAY_500, 0.95, 0.3).move_to(A_CENTER + LEFT * 2.05 + DOWN * 0.32),
            block(GRAY_400, 0.72, 0.26).move_to(A_CENTER + LEFT * 2.12 + DOWN * 0.82),
        )
        gate_top = Line(A_CENTER + RIGHT * 0.22 + UP * 0.56, A_CENTER + RIGHT * 1.28 + UP * 0.56, color=GRAY_700, stroke_width=8)
        gate_bottom = Line(A_CENTER + RIGHT * 0.22 + DOWN * 0.56, A_CENTER + RIGHT * 1.28 + DOWN * 0.56, color=GRAY_700, stroke_width=8)
        gate = VGroup(gate_top, gate_bottom).set_opacity(0.0)
        slot = outline_slot(1.82, 1.06).move_to(A_CENTER + RIGHT * 1.72).set_opacity(0.0)

        group = VGroup(title, intake_lane, release_lane, chips, gate, slot)
        return VGroup(body), group

    def _build_orbit_segment(self) -> tuple[VGroup, VGroup]:
        body = panel(6.45, 4.25).move_to(B_CENTER)
        title = label("orbit").move_to(B_CENTER + LEFT * 2.28 + UP * 1.72)
        orbit = Circle(radius=1.34, stroke_color=GRAY_300, stroke_width=4, fill_opacity=0).move_to(B_CENTER + RIGHT * 0.2)
        core = Circle(radius=0.42, stroke_width=0, fill_color=GRAY_900, fill_opacity=1).move_to(B_CENTER + RIGHT * 0.2)
        satellites = VGroup(
            block(GRAY_600, 0.86, 0.36).move_to(B_CENTER + LEFT * 0.64 + UP * 1.1),
            block(GRAY_500, 0.76, 0.32).move_to(B_CENTER + RIGHT * 1.52 + UP * 0.38),
            block(GRAY_400, 0.66, 0.28).move_to(B_CENTER + LEFT * 0.08 + DOWN * 1.24),
        )
        slots = VGroup(
            outline_slot(0.98, 0.48).move_to(B_CENTER + RIGHT * 1.42 + UP * 0.98),
            outline_slot(0.88, 0.44).move_to(B_CENTER + RIGHT * 1.22 + DOWN * 1.02),
            outline_slot(0.78, 0.4).move_to(B_CENTER + LEFT * 1.1 + DOWN * 0.72),
        ).set_opacity(0.35)
        group = VGroup(title, orbit, core, satellites, slots)
        return VGroup(body), group

    def _build_fork_segment(self) -> tuple[VGroup, VGroup]:
        body = panel(6.8, 4.3).move_to(C_CENTER)
        title = label("fork").move_to(C_CENTER + LEFT * 2.46 + UP * 1.75)
        trunk = Line(C_CENTER + LEFT * 2.2, C_CENTER + LEFT * 0.3, color=GRAY_300, stroke_width=5).set_opacity(0.7)
        source = VGroup(
            block(GRAY_900, 1.18, 0.42).move_to(C_CENTER + LEFT * 2.12 + UP * 0.54),
            block(GRAY_600, 1.02, 0.36).move_to(C_CENTER + LEFT * 2.15),
            block(GRAY_500, 0.86, 0.32).move_to(C_CENTER + LEFT * 2.1 + DOWN * 0.5),
        )
        branch_point = C_CENTER + LEFT * 0.28
        branches = VGroup(
            polyline([branch_point, C_CENTER + RIGHT * 1.2 + UP * 0.95, C_CENTER + RIGHT * 2.4 + UP * 1.0], GRAY_500, 4, 0.0),
            polyline([branch_point, C_CENTER + RIGHT * 1.35, C_CENTER + RIGHT * 2.45], GRAY_500, 4, 0.0),
            polyline([branch_point, C_CENTER + RIGHT * 1.2 + DOWN * 0.95, C_CENTER + RIGHT * 2.35 + DOWN * 1.02], GRAY_500, 4, 0.0),
        )
        slots = VGroup(
            outline_slot(1.2, 0.52).move_to(C_CENTER + RIGHT * 2.55 + UP * 1.0),
            outline_slot(1.08, 0.48).move_to(C_CENTER + RIGHT * 2.58),
            outline_slot(0.96, 0.44).move_to(C_CENTER + RIGHT * 2.52 + DOWN * 1.02),
        ).set_opacity(0.18)
        group = VGroup(title, trunk, source, branches, slots)
        return VGroup(body), group

    def _build_merge_segment(self) -> tuple[VGroup, VGroup]:
        body = panel(6.9, 4.2).move_to(D_CENTER)
        title = label("merge").move_to(D_CENTER + LEFT * 2.48 + UP * 1.68)
        lanes = VGroup(
            Line(D_CENTER + LEFT * 2.4 + UP * 0.88, D_CENTER + LEFT * 0.25 + UP * 0.28, color=GRAY_300, stroke_width=5),
            Line(D_CENTER + LEFT * 2.45, D_CENTER + LEFT * 0.15, color=GRAY_300, stroke_width=5),
            Line(D_CENTER + LEFT * 2.35 + DOWN * 0.9, D_CENTER + LEFT * 0.25 + DOWN * 0.28, color=GRAY_300, stroke_width=5),
        ).set_opacity(0.58)
        packets = VGroup(
            block(GRAY_900, 1.08, 0.36).move_to(D_CENTER + LEFT * 2.48 + UP * 0.88),
            block(GRAY_600, 0.96, 0.34).move_to(D_CENTER + LEFT * 2.52),
            block(GRAY_500, 0.82, 0.3).move_to(D_CENTER + LEFT * 2.46 + DOWN * 0.9),
        )
        merge_slot = outline_slot(1.54, 1.28).move_to(D_CENTER + RIGHT * 0.48).set_opacity(0.28)
        output = block(GRAY_200, 1.78, 0.56).move_to(D_CENTER + RIGHT * 2.38).set_opacity(0.52)
        output_slot = outline_slot(2.0, 0.78).move_to(D_CENTER + RIGHT * 2.38).set_opacity(0.34)
        group = VGroup(title, lanes, packets, merge_slot, output, output_slot)
        return VGroup(body), group

    def _build_hub_segment(self) -> VGroup:
        hub_panel = Rectangle(
            width=3.9,
            height=2.5,
            stroke_color=GRAY_300,
            stroke_width=2,
            fill_color=WHITE_TOKEN,
            fill_opacity=0.64,
        ).move_to(HUB_CENTER + DOWN * 0.06)
        hub_title = label("map").scale(0.86).move_to(HUB_CENTER + LEFT * 1.18 + UP * 0.86)
        hub_core = block(GRAY_900, 1.1, 0.56).move_to(HUB_CENTER + UP * 0.12)
        hub_echo = block(GRAY_300, 0.78, 0.34).move_to(HUB_CENTER + RIGHT * 0.92 + DOWN * 0.44)
        return VGroup(hub_panel, hub_title, hub_core, hub_echo)

    def _animate_compression_segment(self, group: VGroup, traveler: Dot) -> None:
        chips = group[3]
        gate = group[4]
        slot = group[5]
        targets = VGroup(
            block(GRAY_900, 1.16, 0.3).move_to(A_CENTER + RIGHT * 1.58 + UP * 0.32),
            block(GRAY_600, 0.9, 0.26).move_to(A_CENTER + RIGHT * 1.66 + UP * 0.05),
            block(GRAY_500, 0.72, 0.23).move_to(A_CENTER + RIGHT * 1.67 + DOWN * 0.2),
            block(GRAY_400, 0.52, 0.2).move_to(A_CENTER + RIGHT * 1.68 + DOWN * 0.42),
        )
        self.play(gate.animate.set_opacity(1), slot.animate.set_opacity(0.46), traveler.animate.move_to(A_CENTER + LEFT * 0.2), run_time=0.9)
        self.play(
            AnimationGroup(
                Transform(chips[0], targets[0]),
                Transform(chips[1], targets[1]),
                Transform(chips[2], targets[2]),
                Transform(chips[3], targets[3]),
                gate[0].animate.shift(DOWN * 0.16),
                gate[1].animate.shift(UP * 0.16),
                traveler.animate.move_to(A_CENTER + RIGHT * 1.25).scale(1.25),
                lag_ratio=0.04,
            ),
            run_time=3.1,
            rate_func=smooth,
        )
        self.play(
            gate.animate.set_opacity(0.2),
            slot.animate.set_stroke(PRIMARY_RED, opacity=0.74),
            traveler.animate.move_to(A_CENTER + RIGHT * 2.85).scale(1 / 1.25),
            run_time=0.95,
            rate_func=smooth,
        )

    def _animate_orbit_segment(self, group: VGroup, traveler: Dot) -> None:
        orbit = group[1]
        core = group[2]
        satellites = group[3]
        slots = group[4]
        self.play(
            orbit.animate.set_stroke(PRIMARY_RED, opacity=0.72),
            slots.animate.set_opacity(0.52),
            traveler.animate.move_to(B_CENTER + LEFT * 0.9 + UP * 1.0),
            run_time=0.85,
        )
        self.play(
            Rotate(satellites, angle=-0.72 * PI, about_point=core.get_center()),
            traveler.animate.move_to(B_CENTER + RIGHT * 1.45 + UP * 0.92),
            core.animate.scale(1.08),
            run_time=2.7,
            rate_func=smooth,
        )
        self.play(core.animate.scale(1 / 1.08), run_time=0.35, rate_func=there_and_back)
        final_positions = [
            block(GRAY_600, 0.86, 0.36).move_to(slots[0]),
            block(GRAY_500, 0.76, 0.32).move_to(slots[1]),
            block(GRAY_400, 0.66, 0.28).move_to(slots[2]),
        ]
        self.play(
            AnimationGroup(
                Transform(satellites[0], final_positions[0]),
                Transform(satellites[1], final_positions[1]),
                Transform(satellites[2], final_positions[2]),
                traveler.animate.move_to(B_CENTER + DOWN * 2.0),
                lag_ratio=0.05,
            ),
            run_time=1.4,
            rate_func=smooth,
        )
        self.play(orbit.animate.set_stroke(GRAY_300, opacity=0.34), slots.animate.set_opacity(0.18), run_time=0.45)

    def _animate_fork_segment(self, group: VGroup, traveler: Dot) -> None:
        source = group[2]
        branches = group[3]
        slots = group[4]
        branch_pulses = VGroup(*[Dot(branches[i].get_start(), radius=0.09, color=PRIMARY_RED) for i in range(3)])
        self.add(branch_pulses)
        self.play(
            branches.animate.set_stroke(opacity=0.72),
            slots.animate.set_opacity(0.45),
            traveler.animate.move_to(branches[0].get_start()),
            run_time=0.9,
        )
        self.play(
            AnimationGroup(
                MoveAlongPath(branch_pulses[0], branches[0]),
                MoveAlongPath(branch_pulses[1], branches[1]),
                MoveAlongPath(branch_pulses[2], branches[2]),
                lag_ratio=0.08,
            ),
            run_time=1.5,
            rate_func=linear,
        )
        targets = VGroup(
            block(GRAY_900, 1.1, 0.38).move_to(slots[0]),
            block(GRAY_600, 0.98, 0.34).move_to(slots[1]),
            block(GRAY_500, 0.82, 0.3).move_to(slots[2]),
        )
        self.play(
            AnimationGroup(
                Transform(source[0], targets[0]),
                Transform(source[1], targets[1]),
                Transform(source[2], targets[2]),
                traveler.animate.move_to(C_CENTER + RIGHT * 3.0),
                lag_ratio=0.07,
            ),
            run_time=1.95,
            rate_func=smooth,
        )
        self.play(
            FadeOut(branch_pulses),
            branches.animate.set_stroke(opacity=0.32),
            slots.animate.set_opacity(0.16),
            run_time=0.55,
        )

    def _animate_merge_segment(self, group: VGroup, traveler: Dot) -> None:
        packets = group[2]
        merge_slot = group[3]
        output = group[4]
        output_slot = group[5]
        self.play(
            merge_slot.animate.set_stroke(PRIMARY_RED, opacity=0.72),
            traveler.animate.move_to(D_CENTER + LEFT * 0.15),
            run_time=0.85,
        )
        merged_targets = VGroup(
            block(GRAY_900, 1.36, 0.38).move_to(D_CENTER + RIGHT * 0.42 + UP * 0.2),
            block(GRAY_600, 1.06, 0.32).move_to(D_CENTER + RIGHT * 0.45 + DOWN * 0.12),
            block(GRAY_500, 0.78, 0.26).move_to(D_CENTER + RIGHT * 0.48 + DOWN * 0.38),
        )
        self.play(
            AnimationGroup(
                Transform(packets[0], merged_targets[0]),
                Transform(packets[1], merged_targets[1]),
                Transform(packets[2], merged_targets[2]),
                traveler.animate.move_to(D_CENTER + RIGHT * 0.48).scale(1.18),
                lag_ratio=0.05,
            ),
            run_time=2.1,
            rate_func=smooth,
        )
        resolved = VGroup(
            block(GRAY_900, 1.54, 0.44).move_to(D_CENTER + RIGHT * 2.38 + UP * 0.08),
            block(PRIMARY_RED, 0.62, 0.18).move_to(D_CENTER + RIGHT * 2.38 + DOWN * 0.33),
            block(GRAY_600, 1.0, 0.26).move_to(D_CENTER + RIGHT * 2.38 + DOWN * 0.05),
        )
        self.play(
            Transform(packets[0], resolved[0]),
            Transform(packets[1], resolved[2]),
            Transform(packets[2], resolved[1]),
            output.animate.set_opacity(0),
            output_slot.animate.set_stroke(PRIMARY_RED, opacity=0.55),
            traveler.animate.move_to(D_CENTER + RIGHT * 2.38).scale(1 / 1.18),
            run_time=1.65,
            rate_func=smooth,
        )
        pulse = Circle(radius=0.62, stroke_color=HIGHLIGHT_RED, stroke_width=6, fill_opacity=0).move_to(D_CENTER + RIGHT * 2.38)
        self.play(GrowFromCenter(pulse), traveler.animate.move_to(D_CENTER + RIGHT * 2.72), run_time=0.5)
        self.play(FadeOut(pulse), merge_slot.animate.set_stroke(GRAY_400, opacity=0.2), run_time=0.55)


def main() -> int:
    args = parse_args()
    for poster in (False, True):
        env = {**os.environ, "SPIKE_RENDER_TARGET": "poster" if poster else "video"}
        result = subprocess.run(render_command(args, poster), check=False, env=env)
        if result.returncode != 0:
            return result.returncode
        promote((POSTER_PATH if poster else VIDEO_PATH).name, POSTER_PATH if poster else VIDEO_PATH)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
