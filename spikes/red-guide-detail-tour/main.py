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

try:
    from manimpango import list_fonts
except Exception:  # pragma: no cover - fallback for unusual local font probes
    list_fonts = lambda: []  # noqa: E731

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
    GrowFromCenter,
    LaggedStart,
    Line,
    MoveAlongPath,
    MovingCameraScene,
    Rectangle,
    Text,
    Transform,
    VGroup,
    VMobject,
    rate_functions,
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
PRIMARY_BLUE = "#007298"
WHITE = "#ffffff"
GRAY = "#333e48"
PAGE_BACKGROUND = "#f7f7f7"
GRAY_100 = "#e7e7e7"
GRAY_200 = "#cfcfcf"
GRAY_300 = "#b5b5b5"
GRAY_400 = "#9c9c9c"
GRAY_500 = "#828282"
GRAY_600 = "#696969"
GRAY_700 = "#4f4f4f"
GRAY_800 = "#363636"
GRAY_900 = "#1c1c1c"
HIGHLIGHT_RED = "#ffccd5"
HIGHLIGHT_BLUE = "#cdf3ff"
TEXT_FONT = "Open Sans" if "Open Sans" in list_fonts() else "Arial"

FULL_MAP_WIDTH = 30.0
SIGNAL_CENTER = LEFT * 8.95 + UP * 3.55
STRUCTURE_CENTER = RIGHT * 0.3 + UP * 3.65
NEST_CENTER = RIGHT * 8.55 + DOWN * 2.25
RESOLVE_CENTER = LEFT * 6.25 + DOWN * 4.55
MICRO_CENTER = NEST_CENTER + LEFT * 0.32 + UP * 0.18
DEEP_CENTER = MICRO_CENTER + RIGHT * 0.55 + DOWN * 0.16
DEEP_WIDTH = 6.35
DEEP_HEIGHT = DEEP_WIDTH * 9 / 16
PINNED_DOT = DEEP_CENTER + LEFT * (DEEP_WIDTH / 2 - 0.74) + UP * (DEEP_HEIGHT / 2 - 0.64)


class _Args(argparse.Namespace):
    quality: str


def parse_args() -> _Args:
    parser = argparse.ArgumentParser(description="Render the red-guide-detail-tour spike.")
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
    command.extend([str(Path(__file__).resolve()), "RedGuideDetailTourScene"])
    return command


def promote(target_name: str, destination: Path) -> None:
    matches = sorted(STAGING_DIR.glob(f"**/{target_name}"), key=lambda path: path.stat().st_mtime)
    if not matches:
        raise FileNotFoundError(target_name)
    destination.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(matches[-1], destination)


def label_text(text: str, *, font_size: int = 22, color: str = GRAY_700, max_width: float | None = None) -> Text:
    label = Text(text, font=TEXT_FONT, font_size=font_size, color=color)
    if max_width and label.width > max_width:
        label.scale_to_fit_width(max_width)
    return label


def panel(width: float, height: float, center, fill: str = WHITE, opacity: float = 0.88) -> Rectangle:
    return Rectangle(
        width=width,
        height=height,
        stroke_color=GRAY_300,
        stroke_width=2,
        fill_color=fill,
        fill_opacity=opacity,
    ).move_to(center)


def slab(color: str, width: float, height: float, opacity: float = 1.0) -> Rectangle:
    return Rectangle(width=width, height=height, stroke_width=0, fill_color=color, fill_opacity=opacity)


def outline(width: float, height: float, center, color: str = GRAY_400, stroke_width: float = 2.0, opacity: float = 1.0) -> Rectangle:
    return Rectangle(
        width=width,
        height=height,
        stroke_color=color,
        stroke_width=stroke_width,
        fill_opacity=0,
    ).move_to(center).set_opacity(opacity)


def polyline(points: list, color: str, stroke_width: float, opacity: float = 1.0) -> VMobject:
    route = VMobject()
    route.set_points_as_corners(points)
    route.set_stroke(color=color, width=stroke_width, opacity=opacity)
    route.set_fill(opacity=0)
    return route


def grid_lines() -> VGroup:
    lines = VGroup()
    for x in range(-14, 15, 2):
        lines.add(Line([x, -7.2, 0], [x, 7.2, 0], color=GRAY_100, stroke_width=1).set_opacity(0.66))
    for y in range(-7, 8, 2):
        lines.add(Line([-14.6, y, 0], [14.6, y, 0], color=GRAY_100, stroke_width=1).set_opacity(0.66))
    return lines


class RedGuideDetailTourScene(MovingCameraScene):
    def construct(self) -> None:
        self.camera.background_color = WHITE
        self.camera.frame.set(width=FULL_MAP_WIDTH).move_to(ORIGIN)

        stage = Rectangle(
            width=31.2,
            height=16.8,
            stroke_color=GRAY_100,
            stroke_width=1,
            fill_color=PAGE_BACKGROUND,
            fill_opacity=0.98,
        )
        grid = grid_lines()

        signal_panel, signal_parts = self._signal_station()
        structure_panel = self._structure_station()
        nested_panel, nested_parts = self._nested_station()
        resolve_panel = self._resolve_station()

        route_signal_to_structure = polyline(
            [
                SIGNAL_CENTER + RIGHT * 3.0,
                LEFT * 4.2 + UP * 5.15,
                STRUCTURE_CENTER + LEFT * 2.8,
            ],
            GRAY_400,
            4.0,
            0.44,
        )
        route_structure_to_nested = polyline(
            [
                STRUCTURE_CENTER + RIGHT * 2.72 + DOWN * 0.1,
                RIGHT * 5.1 + UP * 1.58,
                RIGHT * 9.65 + UP * 0.4,
                NEST_CENTER + UP * 1.9,
            ],
            GRAY_400,
            4.0,
            0.42,
        )
        route_nested_to_resolve = polyline(
            [
                NEST_CENTER + LEFT * 2.9,
                RIGHT * 1.2 + DOWN * 5.3,
                RESOLVE_CENTER + RIGHT * 2.6,
            ],
            GRAY_400,
            2.5,
            0.24,
        )
        routes = VGroup(route_signal_to_structure, route_structure_to_nested, route_nested_to_resolve)
        routes.set_z_index(1)

        guide = Dot(SIGNAL_CENTER + LEFT * 2.52 + UP * 0.12, radius=0.135, color=PRIMARY_RED).set_z_index(20)
        halo = Circle(radius=0.32, stroke_color=PRIMARY_RED, stroke_width=3, fill_color=HIGHLIGHT_RED, fill_opacity=0.08)
        halo.move_to(guide).set_z_index(19)
        halo.add_updater(lambda mob: mob.move_to(guide))

        world = VGroup(stage, grid, routes, signal_panel, structure_panel, nested_panel, resolve_panel)
        self.add(stage, grid, routes, signal_panel, structure_panel, nested_panel, resolve_panel, halo, guide)
        self.wait(2.8)

        self.play(
            self.camera.frame.animate.set(width=9.0).move_to(SIGNAL_CENTER),
            guide.animate.move_to(signal_parts["receiver"].get_left() + RIGHT * 0.24),
            run_time=2.0,
            rate_func=smooth,
        )
        self._animate_signal_station(signal_parts, guide)
        self.wait(0.55)

        active_bridge = route_structure_to_nested.copy().set_stroke(PRIMARY_RED, width=5.2, opacity=0.88).set_z_index(4)
        self.play(
            self.camera.frame.animate.set(width=21.6).move_to(RIGHT * 4.9 + UP * 0.18),
            guide.animate.move_to(route_structure_to_nested.get_start()),
            signal_panel.animate.set_opacity(0.08),
            route_signal_to_structure.animate.set_stroke(opacity=0.18),
            route_nested_to_resolve.animate.set_stroke(opacity=0.12),
            run_time=1.15,
            rate_func=smooth,
        )
        self.play(
            Create(active_bridge),
            MoveAlongPath(guide, route_structure_to_nested),
            structure_panel.animate.set_opacity(0.18),
            run_time=3.0,
            rate_func=rate_functions.ease_in_out_cubic,
        )
        self.play(FadeOut(active_bridge), run_time=0.35, rate_func=smooth)
        self.play(
            self.camera.frame.animate.set(width=8.55).move_to(NEST_CENTER),
            guide.animate.move_to(nested_parts["selection"].get_center() + LEFT * 0.34),
            run_time=1.3,
            rate_func=smooth,
        )
        self._animate_nested_selection(nested_parts, guide)
        self.wait(0.5)

        detail_parts = self._build_detail_panel()
        self.play(
            self.camera.frame.animate.set(width=DEEP_WIDTH).move_to(DEEP_CENTER),
            guide.animate.move_to(PINNED_DOT).scale(1.12),
            nested_parts["station_shell"].animate.set_opacity(0),
            nested_parts["side_stack"].animate.set_opacity(0.16),
            nested_parts["cells"].animate.set_opacity(0.18),
            nested_parts["selection"].animate.move_to(MICRO_CENTER).set_stroke(PRIMARY_RED, width=4.0),
            run_time=2.2,
            rate_func=smooth,
        )
        self._open_detail_panel(nested_parts, detail_parts, guide)
        self.wait(6.4)

    def _signal_station(self) -> tuple[VGroup, dict[str, object]]:
        body = panel(6.85, 4.12, SIGNAL_CENTER)
        title = label_text("scan", font_size=24).move_to(SIGNAL_CENTER + LEFT * 2.25 + UP * 1.5)
        header = Line(SIGNAL_CENTER + LEFT * 2.78 + UP * 1.1, SIGNAL_CENTER + RIGHT * 2.78 + UP * 1.1, color=GRAY_200, stroke_width=2)
        source = VGroup(
            slab(GRAY_900, 1.48, 0.38).move_to(SIGNAL_CENTER + LEFT * 1.85 + UP * 0.48),
            slab(GRAY_600, 1.24, 0.32).move_to(SIGNAL_CENTER + LEFT * 1.65),
            slab(GRAY_500, 0.96, 0.28).move_to(SIGNAL_CENTER + LEFT * 1.48 + DOWN * 0.48),
            slab(GRAY_400, 0.78, 0.24).move_to(SIGNAL_CENTER + LEFT * 1.35 + DOWN * 0.9),
        )
        receiver = outline(1.46, 1.34, SIGNAL_CENTER + RIGHT * 1.65 + DOWN * 0.12, GRAY_400, 2.1, 0.44)
        rails = VGroup(
            Line(receiver.get_left() + UP * 0.44, receiver.get_right() + UP * 0.44, color=GRAY_300, stroke_width=3),
            Line(receiver.get_left() + DOWN * 0.44, receiver.get_right() + DOWN * 0.44, color=GRAY_300, stroke_width=3),
        ).set_opacity(0.68)
        output = outline(1.16, 0.54, SIGNAL_CENTER + RIGHT * 2.55 + DOWN * 0.12, GRAY_300, 1.8, 0.32)
        group = VGroup(body, title, header, source, receiver, rails, output).set_z_index(3)
        return group, {"source": source, "receiver": receiver, "rails": rails, "output": output}

    def _structure_station(self) -> VGroup:
        body = panel(6.2, 3.95, STRUCTURE_CENTER, opacity=0.82)
        title = label_text("orient", font_size=24).move_to(STRUCTURE_CENTER + LEFT * 1.9 + UP * 1.42)
        spine = Line(STRUCTURE_CENTER + LEFT * 2.1 + DOWN * 0.7, STRUCTURE_CENTER + RIGHT * 2.15 + UP * 0.6, color=GRAY_300, stroke_width=4)
        nodes = VGroup(
            Dot(STRUCTURE_CENTER + LEFT * 1.72 + DOWN * 0.58, radius=0.13, color=GRAY_700),
            Dot(STRUCTURE_CENTER + LEFT * 0.38 + DOWN * 0.15, radius=0.11, color=GRAY_600),
            Dot(STRUCTURE_CENTER + RIGHT * 0.76 + UP * 0.23, radius=0.1, color=GRAY_600),
            Dot(STRUCTURE_CENTER + RIGHT * 1.84 + UP * 0.55, radius=0.13, color=GRAY_800),
        )
        shelves = VGroup(
            slab(GRAY_100, 2.25, 0.2, 0.72).move_to(STRUCTURE_CENTER + LEFT * 0.92 + UP * 0.75),
            slab(GRAY_100, 1.65, 0.18, 0.72).move_to(STRUCTURE_CENTER + RIGHT * 1.02 + DOWN * 0.86),
        )
        return VGroup(body, title, spine, nodes, shelves).set_z_index(3)

    def _nested_station(self) -> tuple[VGroup, dict[str, object]]:
        body = panel(6.75, 4.35, NEST_CENTER)
        title = label_text("nested field", font_size=24, max_width=2.7).move_to(NEST_CENTER + LEFT * 1.84 + UP * 1.58)
        header = Line(NEST_CENTER + LEFT * 2.75 + UP * 1.15, NEST_CENTER + RIGHT * 2.75 + UP * 1.15, color=GRAY_200, stroke_width=2)

        cells = VGroup()
        for row in range(4):
            for col in range(5):
                cell_center = NEST_CENTER + LEFT * 1.52 + RIGHT * col * 0.74 + UP * (0.46 - row * 0.42)
                fill = GRAY_100 if (row + col) % 2 == 0 else WHITE
                cells.add(
                    Rectangle(
                        width=0.5,
                        height=0.24,
                        stroke_color=GRAY_300,
                        stroke_width=1.2,
                        fill_color=fill,
                        fill_opacity=0.88,
                    ).move_to(cell_center)
                )
        selected = cells[7]
        selected.move_to(MICRO_CENTER)
        selection = outline(0.72, 0.42, MICRO_CENTER, PRIMARY_RED, 3.0, 0.0)
        microscope = outline(1.12, 0.8, MICRO_CENTER, GRAY_400, 2.0, 0.0)
        side_stack = VGroup(
            slab(GRAY_800, 1.3, 0.32).move_to(NEST_CENTER + RIGHT * 2.02 + UP * 0.42),
            slab(GRAY_500, 1.04, 0.26).move_to(NEST_CENTER + RIGHT * 2.02),
            slab(GRAY_300, 0.78, 0.22).move_to(NEST_CENTER + RIGHT * 2.02 + DOWN * 0.36),
        )
        group = VGroup(body, title, header, cells, selection, microscope, side_stack).set_z_index(3)
        return group, {
            "station_shell": VGroup(body, title, header),
            "cells": cells,
            "selected": selected,
            "selection": selection,
            "microscope": microscope,
            "side_stack": side_stack,
        }

    def _resolve_station(self) -> VGroup:
        body = panel(6.45, 3.9, RESOLVE_CENTER, opacity=0.78)
        title = label_text("resolve", font_size=24).move_to(RESOLVE_CENTER + LEFT * 1.96 + UP * 1.38)
        slots = VGroup(
            outline(1.52, 0.62, RESOLVE_CENTER + LEFT * 1.58 + DOWN * 0.2, GRAY_300, 1.7, 0.48),
            outline(1.52, 0.62, RESOLVE_CENTER + RIGHT * 0.18 + DOWN * 0.2, GRAY_300, 1.7, 0.48),
            outline(1.52, 0.62, RESOLVE_CENTER + RIGHT * 1.92 + DOWN * 0.2, GRAY_300, 1.7, 0.48),
        )
        bridge = Line(slots[0].get_right(), slots[2].get_left(), color=GRAY_300, stroke_width=3).set_opacity(0.48)
        return VGroup(body, title, bridge, slots).set_z_index(3)

    def _animate_signal_station(self, parts: dict[str, object], guide: Dot) -> None:
        source = parts["source"]
        receiver = parts["receiver"]
        rails = parts["rails"]
        output = parts["output"]
        receiver_targets = VGroup(
            slab(GRAY_900, 1.04, 0.28).move_to(receiver.get_center() + UP * 0.3),
            slab(GRAY_600, 0.82, 0.24).move_to(receiver.get_center() + UP * 0.02),
            slab(PRIMARY_RED, 0.58, 0.2).move_to(receiver.get_center() + DOWN * 0.25),
            slab(GRAY_400, 0.46, 0.18).move_to(receiver.get_center() + DOWN * 0.48),
        )
        self.play(
            receiver.animate.set_opacity(1).set_stroke(PRIMARY_RED, width=3.2),
            rails.animate.set_stroke(PRIMARY_RED, width=4).set_opacity(0.9),
            guide.animate.move_to(receiver.get_center() + LEFT * 0.44),
            run_time=0.9,
            rate_func=smooth,
        )
        self.play(
            AnimationGroup(
                Transform(source[0], receiver_targets[0]),
                Transform(source[1], receiver_targets[1]),
                Transform(source[2], receiver_targets[2]),
                Transform(source[3], receiver_targets[3]),
                guide.animate.move_to(receiver.get_center() + RIGHT * 0.36),
                lag_ratio=0.06,
            ),
            run_time=2.9,
            rate_func=rate_functions.ease_in_out_cubic,
        )
        self.play(
            output.animate.set_opacity(0.78).set_stroke(PRIMARY_RED, width=2.5),
            guide.animate.move_to(output.get_center()),
            receiver.animate.set_stroke(GRAY_300, width=1.6).set_opacity(0.5),
            rails.animate.set_opacity(0.36),
            run_time=0.95,
            rate_func=smooth,
        )

    def _animate_nested_selection(self, parts: dict[str, object], guide: Dot) -> None:
        cells = parts["cells"]
        selected = parts["selected"]
        selection = parts["selection"]
        microscope = parts["microscope"]
        side_stack = parts["side_stack"]
        self.play(
            selection.animate.set_opacity(1),
            microscope.animate.set_opacity(0.48),
            cells.animate.set_opacity(0.58),
            selected.animate.set_fill(WHITE, opacity=1).set_stroke(PRIMARY_RED, width=2.5),
            guide.animate.move_to(MICRO_CENTER + LEFT * 0.42),
            run_time=0.9,
            rate_func=smooth,
        )
        self.play(
            microscope.animate.scale(1.18).set_stroke(PRIMARY_RED, width=3.0),
            guide.animate.move_to(MICRO_CENTER + UP * 0.3),
            side_stack.animate.set_opacity(0.45),
            run_time=1.7,
            rate_func=there_and_back,
        )
        self.play(
            cells.animate.set_opacity(0.34),
            selected.animate.scale(1.18),
            guide.animate.move_to(MICRO_CENTER + RIGHT * 0.36),
            run_time=1.05,
            rate_func=smooth,
        )

    def _build_detail_panel(self) -> dict[str, object]:
        panel_center = DEEP_CENTER + RIGHT * 0.45 + DOWN * 0.12
        detail_background = Rectangle(
            width=4.5,
            height=2.72,
            stroke_color=HIGHLIGHT_BLUE,
            stroke_width=2.2,
            fill_color=PRIMARY_BLUE,
            fill_opacity=0.98,
        ).move_to(panel_center)
        detail_background.set_z_index(12)

        pointer = Line(PINNED_DOT + RIGHT * 0.22 + DOWN * 0.08, detail_background.get_left() + RIGHT * 0.28 + UP * 0.78, color=PRIMARY_RED, stroke_width=4)
        pointer.set_z_index(18)

        header = Line(detail_background.get_left() + RIGHT * 0.42 + UP * 1.02, detail_background.get_right() + LEFT * 0.42 + UP * 1.02, color=WHITE, stroke_width=2.4)
        header.set_opacity(0.78).set_z_index(14)
        title = label_text("sector detail", font_size=18, color=WHITE, max_width=1.9).move_to(detail_background.get_left() + RIGHT * 1.18 + UP * 1.18)
        title.set_z_index(15)

        inputs = VGroup(
            slab(WHITE, 1.06, 0.18, 0.94).move_to(panel_center + LEFT * 1.48 + UP * 0.46),
            slab(HIGHLIGHT_BLUE, 0.84, 0.16, 0.92).move_to(panel_center + LEFT * 1.58 + UP * 0.12),
            slab(WHITE, 0.64, 0.14, 0.9).move_to(panel_center + LEFT * 1.68 + DOWN * 0.2),
        ).set_z_index(15)
        gate = VGroup(
            Line(panel_center + LEFT * 0.44 + UP * 0.55, panel_center + LEFT * 0.04 + UP * 0.55, color=WHITE, stroke_width=5),
            Line(panel_center + LEFT * 0.44 + DOWN * 0.34, panel_center + LEFT * 0.04 + DOWN * 0.34, color=WHITE, stroke_width=5),
        ).set_z_index(15)
        active_segment = slab(PRIMARY_RED, 0.54, 0.2, 1.0).move_to(panel_center + LEFT * 0.22 + UP * 0.04).set_z_index(16)
        outputs = VGroup(
            outline(0.98, 0.46, panel_center + RIGHT * 1.28 + UP * 0.44, WHITE, 1.8, 0.95),
            outline(1.18, 0.42, panel_center + RIGHT * 1.38, HIGHLIGHT_BLUE, 1.8, 0.92),
            outline(0.86, 0.38, panel_center + RIGHT * 1.2 + DOWN * 0.4, WHITE, 1.8, 0.9),
        ).set_z_index(15)
        red_result = slab(PRIMARY_RED, 0.46, 0.14).move_to(outputs[1].get_center() + DOWN * 0.05).set_z_index(16)
        labels = VGroup(
            label_text("input", font_size=14, color=WHITE, max_width=0.7).move_to(panel_center + LEFT * 1.62 + DOWN * 0.75),
            label_text("rule", font_size=14, color=WHITE, max_width=0.62).move_to(panel_center + LEFT * 0.22 + DOWN * 0.75),
            label_text("output", font_size=14, color=WHITE, max_width=0.78).move_to(panel_center + RIGHT * 1.3 + DOWN * 0.75),
        ).set_z_index(15)
        return {
            "background": detail_background,
            "pointer": pointer,
            "header": header,
            "title": title,
            "inputs": inputs,
            "gate": gate,
            "active_segment": active_segment,
            "outputs": outputs,
            "red_result": red_result,
            "labels": labels,
        }

    def _open_detail_panel(self, nested_parts: dict[str, object], detail: dict[str, object], guide: Dot) -> None:
        seed = Rectangle(
            width=0.32,
            height=0.2,
            stroke_color=PRIMARY_RED,
            stroke_width=2,
            fill_color=PRIMARY_BLUE,
            fill_opacity=0.95,
        ).move_to(MICRO_CENTER).set_z_index(12)
        self.add(seed)
        self.play(
            FadeOut(nested_parts["microscope"]),
            nested_parts["cells"].animate.set_opacity(0.1),
            nested_parts["side_stack"].animate.set_opacity(0.08),
            nested_parts["selection"].animate.set_opacity(0),
            Transform(seed, detail["background"]),
            guide.animate.move_to(PINNED_DOT),
            run_time=1.25,
            rate_func=rate_functions.ease_in_out_cubic,
        )
        self.play(
            FadeIn(detail["pointer"]),
            FadeIn(detail["header"]),
            FadeIn(detail["title"], shift=RIGHT * 0.12),
            run_time=0.7,
            rate_func=smooth,
        )
        self.play(
            LaggedStart(
                FadeIn(detail["inputs"][0], shift=RIGHT * 0.12),
                FadeIn(detail["inputs"][1], shift=RIGHT * 0.12),
                FadeIn(detail["inputs"][2], shift=RIGHT * 0.12),
                lag_ratio=0.18,
            ),
            run_time=1.25,
        )
        self.play(
            FadeIn(detail["gate"]),
            guide.animate.scale(1 / 1.12),
            run_time=0.7,
            rate_func=smooth,
        )
        self.play(
            FadeIn(detail["active_segment"], shift=RIGHT * 0.12),
            detail["gate"][0].animate.shift(DOWN * 0.08),
            detail["gate"][1].animate.shift(UP * 0.08),
            run_time=1.05,
            rate_func=rate_functions.ease_in_out_cubic,
        )
        self.play(
            LaggedStart(
                FadeIn(detail["outputs"][0], shift=RIGHT * 0.1),
                FadeIn(detail["outputs"][1], shift=RIGHT * 0.1),
                FadeIn(detail["outputs"][2], shift=RIGHT * 0.1),
                lag_ratio=0.16,
            ),
            detail["active_segment"].animate.move_to(detail["outputs"][1].get_center() + DOWN * 0.05),
            run_time=1.45,
            rate_func=smooth,
        )
        self.play(
            Transform(detail["active_segment"], detail["red_result"]),
            FadeIn(detail["labels"], shift=UP * 0.08),
            run_time=0.9,
            rate_func=smooth,
        )
        pulse = Circle(radius=0.28, stroke_color=HIGHLIGHT_RED, stroke_width=5, fill_opacity=0).move_to(detail["outputs"][1])
        pulse.set_z_index(17)
        self.play(GrowFromCenter(pulse), detail["pointer"].animate.set_stroke(width=5.5), run_time=0.55)
        self.play(FadeOut(pulse), detail["pointer"].animate.set_stroke(width=4), run_time=0.5)


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
