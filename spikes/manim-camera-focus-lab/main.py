#!/usr/bin/env -S uv run --script
# /// script
# dependencies = [
#   "manim>=0.20.1",
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
    RIGHT,
    UP,
    AnimationGroup,
    Circle,
    Create,
    Dot,
    FadeIn,
    FadeOut,
    Line,
    MoveAlongPath,
    MovingCameraScene,
    Rectangle,
    Restore,
    Text,
    Transform,
    VGroup,
    VMobject,
    WHITE,
    smooth,
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

FULL_MAP_WIDTH = 24.2
A_CENTER = LEFT * 7.7 + UP * 3.0
B_CENTER = RIGHT * 7.45 + UP * 3.05
C_CENTER = DOWN * 3.65


class _Args(argparse.Namespace):
    quality: str


def parse_args() -> _Args:
    parser = argparse.ArgumentParser(description="Render the Manim camera focus narration spike.")
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
    command.extend([str(Path(__file__).resolve()), "CameraFocusNarrationScene"])
    return command


def promote(target_name: str, destination: Path) -> None:
    matches = sorted(STAGING_DIR.glob(f"**/{target_name}"))
    if not matches:
        raise FileNotFoundError(target_name)
    destination.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(max(matches, key=lambda path: path.stat().st_mtime), destination)


def text_label(value: str, size: int = 22, color: str = GRAY_700) -> Text:
    return Text(value, font=FONT_FAMILY, font_size=size, color=color)


def panel(width: float = 5.65, height: float = 3.48) -> Rectangle:
    return Rectangle(
        width=width,
        height=height,
        stroke_color=GRAY_300,
        stroke_width=2,
        fill_color=WHITE_TOKEN,
        fill_opacity=0.92,
    )


def slab(color: str, width: float, height: float, opacity: float = 1.0) -> Rectangle:
    return Rectangle(width=width, height=height, stroke_width=0, fill_color=color, fill_opacity=opacity)


def outline(width: float, height: float, color: str = GRAY_400, stroke_width: float = 2.0) -> Rectangle:
    return Rectangle(width=width, height=height, stroke_color=color, stroke_width=stroke_width, fill_opacity=0)


def polyline(points: list, color: str, stroke_width: float, opacity: float = 1.0) -> VMobject:
    route = VMobject()
    route.set_points_as_corners(points)
    route.set_stroke(color=color, width=stroke_width, opacity=opacity)
    route.set_fill(opacity=0)
    return route


def grid_lines() -> VGroup:
    lines = VGroup()
    for x in range(-12, 13, 2):
        lines.add(Line([x, -6.8, 0], [x, 6.8, 0], color=GRAY_100, stroke_width=1).set_opacity(0.72))
    for y in range(-6, 7, 2):
        lines.add(Line([-12.4, y, 0], [12.4, y, 0], color=GRAY_100, stroke_width=1).set_opacity(0.72))
    return lines


class CameraFocusNarrationScene(MovingCameraScene):
    def construct(self) -> None:
        self.camera.background_color = WHITE
        self.camera.frame.set(width=FULL_MAP_WIDTH).move_to(ORIGIN)
        self.camera.frame.save_state()

        stage = Rectangle(
            width=25.8,
            height=14.1,
            stroke_color=GRAY_100,
            stroke_width=1,
            fill_color=PAGE_BACKGROUND,
            fill_opacity=0.98,
        )
        grid = grid_lines()
        station_a, a_parts = self._station_a()
        station_b, b_parts = self._station_b()
        station_c, c_parts = self._station_c()

        route_ab = polyline(
            [
                A_CENTER + RIGHT * 2.55,
                LEFT * 2.9 + UP * 4.55,
                RIGHT * 2.55 + UP * 4.55,
                B_CENTER + LEFT * 2.55,
            ],
            GRAY_400,
            4.0,
            0.46,
        )
        route_bc = polyline(
            [
                B_CENTER + DOWN * 1.45,
                RIGHT * 8.1 + DOWN * 0.1,
                RIGHT * 3.0 + DOWN * 5.25,
                C_CENTER + RIGHT * 2.45,
            ],
            GRAY_400,
            4.0,
            0.42,
        )
        route_ca = polyline(
            [
                C_CENTER + LEFT * 2.35,
                LEFT * 5.7 + DOWN * 5.55,
                LEFT * 10.05 + DOWN * 0.8,
                A_CENTER + DOWN * 1.35,
            ],
            GRAY_400,
            2.5,
            0.22,
        )
        route_group = VGroup(route_ab, route_bc, route_ca)
        for route in route_group:
            route.set_z_index(1)

        traveler = Dot(A_CENTER + LEFT * 2.1, radius=0.13, color=PRIMARY_RED).set_z_index(12)
        traveler_halo = Circle(radius=0.27, color=PRIMARY_RED, stroke_width=3).set_fill(HIGHLIGHT_RED, 0.08)
        traveler_halo.move_to(traveler).set_z_index(11)
        traveler_halo.add_updater(lambda halo: halo.move_to(traveler))

        world = VGroup(stage, grid, route_group, station_a, station_b, station_c)
        self.add(stage, grid, route_group, station_a, station_b, station_c, traveler_halo, traveler)
        self.wait(2.7)

        self.play(
            self.camera.frame.animate.set(width=8.25).move_to(A_CENTER),
            traveler.animate.move_to(a_parts["slot"].get_center() + LEFT * 0.42),
            run_time=2.0,
            rate_func=smooth,
        )
        self._focus_intake(a_parts, traveler)
        self.wait(0.55)

        active_ab = route_ab.copy().set_stroke(PRIMARY_RED, width=5.0, opacity=0.9).set_z_index(4)
        self.play(
            self.camera.frame.animate.set(width=18.2).move_to((A_CENTER + B_CENTER) / 2 + UP * 0.15),
            run_time=1.2,
            rate_func=smooth,
        )
        self.wait(0.45)
        self.play(
            Create(active_ab),
            MoveAlongPath(traveler, route_ab),
            self.camera.frame.animate.set(width=8.4).move_to(B_CENTER),
            run_time=3.1,
            rate_func=smooth,
        )
        self._focus_detail(b_parts, traveler)
        self.wait(0.55)

        active_bc = route_bc.copy().set_stroke(PRIMARY_RED, width=5.0, opacity=0.86).set_z_index(4)
        self.play(
            self.camera.frame.animate.set(width=20.8).move_to(RIGHT * 3.8 + DOWN * 0.4),
            run_time=1.15,
            rate_func=smooth,
        )
        self.wait(0.45)
        self.play(
            Create(active_bc),
            MoveAlongPath(traveler, route_bc),
            self.camera.frame.animate.set(width=8.5).move_to(C_CENTER),
            run_time=3.2,
            rate_func=smooth,
        )
        self._focus_resolution(c_parts, traveler)

        final_route = VGroup(active_ab, active_bc)
        terminal_mark = Dot(C_CENTER + RIGHT * 1.75 + DOWN * 0.1, radius=0.16, color=PRIMARY_RED).set_z_index(12)
        terminal_mark.set_opacity(0)
        self.add(terminal_mark)
        traveler_halo.clear_updaters()
        self.play(
            FadeOut(traveler_halo),
            traveler.animate.move_to(terminal_mark).set_opacity(0),
            terminal_mark.animate.set_opacity(1),
            final_route.animate.set_opacity(0.72),
            Restore(self.camera.frame),
            run_time=2.4,
            rate_func=smooth,
        )
        self.play(
            world.animate.set_opacity(0.96),
            final_route.animate.set_opacity(0.84),
            terminal_mark.animate.scale(1.12),
            run_time=0.7,
            rate_func=smooth,
        )
        self.wait(6.2)

    def _station_a(self) -> tuple[VGroup, dict[str, object]]:
        box = panel().move_to(A_CENTER)
        title = text_label("prepare", 24, GRAY_700).move_to(A_CENTER + UP * 1.28 + LEFT * 1.7)
        header = Line(A_CENTER + LEFT * 2.28 + UP * 0.88, A_CENTER + RIGHT * 2.28 + UP * 0.88, color=GRAY_200, stroke_width=2)
        source = VGroup(
            slab(GRAY_900, 1.48, 0.36).move_to(A_CENTER + LEFT * 1.55 + UP * 0.2),
            slab(GRAY_600, 1.16, 0.3).move_to(A_CENTER + LEFT * 1.32 + DOWN * 0.32),
            slab(GRAY_400, 0.86, 0.24).move_to(A_CENTER + LEFT * 1.1 + DOWN * 0.78),
        )
        slot = outline(1.2, 1.34, GRAY_400, 2.2).move_to(A_CENTER + RIGHT * 1.45 + DOWN * 0.22)
        slot_label = text_label("slot", 18, GRAY_500).next_to(slot, DOWN, buff=0.12)
        rail_top = Line(slot.get_left() + UP * 0.45, slot.get_right() + UP * 0.45, color=GRAY_300, stroke_width=3)
        rail_bottom = Line(slot.get_left() + DOWN * 0.45, slot.get_right() + DOWN * 0.45, color=GRAY_300, stroke_width=3)
        target = VGroup(
            slab(GRAY_900, 0.88, 0.28).move_to(slot.get_center() + UP * 0.34),
            slab(GRAY_600, 0.68, 0.23).move_to(slot.get_center()),
            slab(PRIMARY_RED, 0.46, 0.18).move_to(slot.get_center() + DOWN * 0.31),
        )
        group = VGroup(box, title, header, source, slot, slot_label, rail_top, rail_bottom).set_z_index(3)
        return group, {"source": source, "slot": slot, "rails": VGroup(rail_top, rail_bottom), "target": target}

    def _station_b(self) -> tuple[VGroup, dict[str, object]]:
        box = panel().move_to(B_CENTER)
        title = text_label("inspect", 24, GRAY_700).move_to(B_CENTER + UP * 1.28 + LEFT * 1.72)
        header = Line(B_CENTER + LEFT * 2.28 + UP * 0.88, B_CENTER + RIGHT * 2.28 + UP * 0.88, color=GRAY_200, stroke_width=2)

        dots = VGroup()
        for row in range(3):
            for col in range(4):
                dots.add(Dot(B_CENTER + LEFT * 1.55 + RIGHT * col * 0.54 + UP * (0.24 - row * 0.48), radius=0.08, color=GRAY_500))
        focus_dot = Dot(B_CENTER + LEFT * 0.47 + UP * 0.24, radius=0.11, color=BLACK)
        window = outline(1.08, 0.78, GRAY_400, 2.1).move_to(focus_dot)
        output_slot = outline(1.36, 1.0, GRAY_400, 2.0).move_to(B_CENTER + RIGHT * 1.42 + DOWN * 0.17)
        output_hint = Line(output_slot.get_left(), output_slot.get_right(), color=GRAY_300, stroke_width=3)
        bridge = Line(window.get_right(), output_slot.get_left(), color=GRAY_300, stroke_width=3).set_opacity(0.75)
        selected = slab(PRIMARY_RED, 0.72, 0.26).move_to(output_slot.get_center())
        group = VGroup(box, title, header, dots, focus_dot, window, bridge, output_slot, output_hint).set_z_index(3)
        return group, {"dots": dots, "focus_dot": focus_dot, "window": window, "bridge": bridge, "output_slot": output_slot, "selected": selected}

    def _station_c(self) -> tuple[VGroup, dict[str, object]]:
        box = panel(width=6.1, height=3.62).move_to(C_CENTER)
        title = text_label("recenter", 24, GRAY_700).move_to(C_CENTER + UP * 1.34 + LEFT * 1.88)
        header = Line(C_CENTER + LEFT * 2.48 + UP * 0.94, C_CENTER + RIGHT * 2.48 + UP * 0.94, color=GRAY_200, stroke_width=2)
        left_stack = VGroup(
            slab(GRAY_700, 1.22, 0.3).move_to(C_CENTER + LEFT * 1.82 + UP * 0.34),
            slab(GRAY_500, 0.96, 0.25).move_to(C_CENTER + LEFT * 1.68 + DOWN * 0.14),
            slab(GRAY_400, 0.72, 0.21).move_to(C_CENTER + LEFT * 1.52 + DOWN * 0.56),
        )
        center_slot = outline(1.46, 1.4, GRAY_400, 2.1).move_to(C_CENTER + RIGHT * 0.25 + DOWN * 0.1)
        final_stack = VGroup(
            slab(GRAY_900, 1.2, 0.34).move_to(center_slot.get_center() + UP * 0.36),
            slab(GRAY_600, 0.92, 0.28).move_to(center_slot.get_center()),
            slab(PRIMARY_RED, 0.68, 0.22).move_to(center_slot.get_center() + DOWN * 0.34),
        )
        final_anchor = outline(0.9, 0.9, GRAY_300, 1.6).move_to(C_CENTER + RIGHT * 1.92 + DOWN * 0.08)
        final_anchor_label = text_label("hold", 18, GRAY_500).next_to(final_anchor, DOWN, buff=0.12)
        group = VGroup(box, title, header, left_stack, center_slot, final_anchor, final_anchor_label).set_z_index(3)
        return group, {"left_stack": left_stack, "center_slot": center_slot, "final_stack": final_stack, "final_anchor": final_anchor}

    def _focus_intake(self, parts: dict[str, object], traveler: Dot) -> None:
        source = parts["source"]
        slot = parts["slot"]
        rails = parts["rails"]
        target = parts["target"]
        self.play(
            slot.animate.set_stroke(PRIMARY_RED, width=3.5),
            rails.animate.set_stroke(PRIMARY_RED, width=4).set_opacity(0.9),
            traveler.animate.move_to(slot.get_center() + LEFT * 0.34),
            run_time=0.85,
            rate_func=smooth,
        )
        self.play(
            AnimationGroup(
                Transform(source[0], target[0]),
                Transform(source[1], target[1]),
                Transform(source[2], target[2]),
                traveler.animate.move_to(slot.get_center() + RIGHT * 0.42),
                lag_ratio=0.07,
            ),
            run_time=2.75,
            rate_func=smooth,
        )

    def _focus_detail(self, parts: dict[str, object], traveler: Dot) -> None:
        dots = parts["dots"]
        focus_dot = parts["focus_dot"]
        window = parts["window"]
        bridge = parts["bridge"]
        output_slot = parts["output_slot"]
        selected = parts["selected"]
        self.play(
            window.animate.set_stroke(PRIMARY_RED, width=3.5),
            bridge.animate.set_stroke(PRIMARY_RED, width=4).set_opacity(0.86),
            traveler.animate.move_to(window.get_center() + RIGHT * 0.18),
            run_time=0.9,
            rate_func=smooth,
        )
        self.play(
            dots.animate.set_opacity(0.28),
            focus_dot.animate.scale(1.42).set_fill(BLACK, opacity=1),
            traveler.animate.move_to(output_slot.get_center() + LEFT * 0.2),
            run_time=1.6,
            rate_func=smooth,
        )
        self.play(
            FadeIn(selected),
            output_slot.animate.set_stroke(PRIMARY_RED, width=3),
            traveler.animate.move_to(output_slot.get_center() + RIGHT * 0.42),
            run_time=1.25,
            rate_func=smooth,
        )

    def _focus_resolution(self, parts: dict[str, object], traveler: Dot) -> None:
        left_stack = parts["left_stack"]
        center_slot = parts["center_slot"]
        final_stack = parts["final_stack"]
        final_anchor = parts["final_anchor"]
        self.play(
            center_slot.animate.set_stroke(PRIMARY_RED, width=3.4),
            traveler.animate.move_to(center_slot.get_center() + LEFT * 0.45),
            run_time=0.85,
            rate_func=smooth,
        )
        self.play(
            AnimationGroup(
                Transform(left_stack[0], final_stack[0]),
                Transform(left_stack[1], final_stack[1]),
                Transform(left_stack[2], final_stack[2]),
                traveler.animate.move_to(center_slot.get_center() + RIGHT * 0.42),
                lag_ratio=0.08,
            ),
            run_time=2.45,
            rate_func=smooth,
        )
        self.play(
            left_stack.animate.next_to(final_anchor, LEFT, buff=0.32),
            center_slot.animate.set_stroke(GRAY_300, width=1.4).set_opacity(0.38),
            final_anchor.animate.set_stroke(PRIMARY_RED, width=3.0),
            traveler.animate.move_to(final_anchor.get_center()),
            run_time=1.4,
            rate_func=smooth,
        )


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
