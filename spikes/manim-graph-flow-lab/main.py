#!/usr/bin/env -S uv run --script
# /// script
# dependencies = [
#   "manim>=0.20.1,<0.21",
# ]
# ///

from __future__ import annotations

import argparse
import shutil
import subprocess
import sys
from pathlib import Path

import numpy as np
from manim import (
    DOWN,
    LEFT,
    RIGHT,
    UP,
    AnimationGroup,
    Circle,
    DiGraph,
    FadeIn,
    FadeOut,
    LaggedStart,
    MoveAlongPath,
    Rectangle,
    Scene,
    ShowPassingFlash,
    Text,
    TracedPath,
    VGroup,
    VMobject,
    linear,
    smooth,
)

SPIKE_DIR = Path(__file__).resolve().parent
REPO_ROOT = SPIKE_DIR.parent.parent
SPIKE_NAME = SPIKE_DIR.name
OUTPUT_DIR = REPO_ROOT / "videos" / SPIKE_NAME
STAGING_DIR = OUTPUT_DIR / ".manim"

PRIMARY_RED = "#9e1b32"
HIGHLIGHT_RED = "#ffccd5"
BLACK = "#000000"
WHITE = "#ffffff"
GRAY = "#333e48"
GRAY_100 = "#e7e7e7"
GRAY_200 = "#cfcfcf"
GRAY_300 = "#b5b5b5"
GRAY_400 = "#9c9c9c"
GRAY_500 = "#828282"
GRAY_600 = "#696969"
GRAY_700 = "#4f4f4f"
GRAY_800 = "#363636"
GRAY_900 = "#1c1c1c"
PAGE_BACKGROUND = "#f7f7f7"

FONT = "Arial"

VERTICES = ["S", "A", "B", "C", "D", "E", "T"]
EDGES = [
    ("S", "A"),
    ("S", "B"),
    ("A", "C"),
    ("A", "D"),
    ("B", "C"),
    ("B", "D"),
    ("C", "E"),
    ("C", "T"),
    ("D", "E"),
    ("E", "T"),
]
SELECTED_VERTICES = ["S", "B", "D", "E", "T"]
SELECTED_EDGES = [("S", "B"), ("B", "D"), ("D", "E"), ("E", "T")]
COMPETING_PATHS = [
    ["S", "A", "C", "T"],
    ["S", "A", "D", "E", "T"],
    ["S", "B", "C", "E", "T"],
]

INITIAL_LAYOUT = {
    "S": np.array([-5.35, 0.05, 0.0]),
    "A": np.array([-3.05, 1.55, 0.0]),
    "B": np.array([-3.05, -1.25, 0.0]),
    "C": np.array([-0.55, 1.25, 0.0]),
    "D": np.array([-0.55, -1.45, 0.0]),
    "E": np.array([2.35, -0.42, 0.0]),
    "T": np.array([5.1, 0.05, 0.0]),
}

FINAL_LAYOUT = {
    "S": np.array([-4.35, -0.22, 0.0]),
    "B": np.array([-2.15, -0.22, 0.0]),
    "D": np.array([0.05, -0.22, 0.0]),
    "E": np.array([2.25, -0.22, 0.0]),
    "T": np.array([4.45, -0.22, 0.0]),
}


class _Args(argparse.Namespace):
    quality: str


def parse_args() -> _Args:
    parser = argparse.ArgumentParser(description="Render the manim-graph-flow-lab spike.")
    parser.add_argument("--quality", choices=("low", "medium", "high", "production", "4k"), default="medium")
    return parser.parse_args(namespace=_Args())


def quality_flag(quality: str) -> str:
    return {"low": "-ql", "medium": "-qm", "high": "-qh", "production": "-qp", "4k": "-qk"}[quality]


def output_paths() -> tuple[Path, Path]:
    return OUTPUT_DIR / f"{SPIKE_NAME}.webm", OUTPUT_DIR / f"{SPIKE_NAME}.png"


def render_command(args: _Args, stem: str, poster: bool) -> list[str]:
    STAGING_DIR.mkdir(parents=True, exist_ok=True)
    command = [
        sys.executable,
        "-m",
        "manim",
        "render",
        quality_flag(args.quality),
        "-r",
        "1600,900",
        "--format",
        "webm",
        "-o",
        stem,
        "--media_dir",
        str(STAGING_DIR),
        str(Path(__file__).resolve()),
        "GraphFlowLabScene",
    ]
    if poster:
        command.insert(-2, "-s")
    return command


def promote(target_name: str, destination: Path) -> None:
    matches = sorted(STAGING_DIR.glob(f"**/{target_name}"))
    if not matches:
        raise FileNotFoundError(target_name)
    destination.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(matches[-1], destination)


def label(text: str, size: int = 24, color: str = GRAY) -> Text:
    return Text(text, font=FONT, font_size=size, color=color)


def make_vertex(name: str) -> VGroup:
    dot = Circle(
        radius=0.31,
        stroke_color=GRAY_500,
        stroke_width=2.2,
        fill_color=WHITE,
        fill_opacity=1,
    )
    token = label(name, size=20, color=GRAY_800).move_to(dot)
    return VGroup(dot, token)


def path_from_vertices(graph: DiGraph, vertices: list[str], color: str, width: float, opacity: float) -> VMobject:
    path = VMobject()
    path.set_points_as_corners([graph.vertices[vertex].get_center() for vertex in vertices])
    path.set_stroke(color=color, width=width, opacity=opacity)
    return path


def route_pulse(point: np.ndarray) -> VGroup:
    core = Circle(radius=0.13, stroke_width=0, fill_color=PRIMARY_RED, fill_opacity=1).move_to(point)
    halo = Circle(radius=0.31, stroke_color=PRIMARY_RED, stroke_width=3, fill_opacity=0).move_to(point)
    halo.add_updater(lambda mob: mob.move_to(core))
    return VGroup(halo, core)


def style_edge(edge, color: str, width: float, opacity: float) -> None:
    edge.set_color(color)
    edge.set_stroke(color=color, width=width, opacity=opacity)
    edge.set_opacity(opacity)


def style_vertex(vertex: VGroup, stroke_color: str, label_color: str, stroke_width: float, fill_opacity: float) -> None:
    vertex[0].set_stroke(color=stroke_color, width=stroke_width)
    vertex[0].set_fill(color=WHITE, opacity=fill_opacity)
    vertex[1].set_color(label_color)


class GraphFlowLabScene(Scene):
    def construct(self) -> None:
        self.camera.background_color = WHITE

        title = label("One path becomes the story", size=32, color=BLACK).to_edge(UP, buff=0.36)
        rule = Rectangle(width=12.4, height=0.035, stroke_width=0, fill_color=GRAY_200, fill_opacity=1).next_to(
            title, DOWN, buff=0.18
        )
        subtitle = label("Alternatives stay present but subordinate until the route earns focus.", size=19, color=GRAY_700).next_to(
            rule, DOWN, buff=0.16
        )

        vertex_mobjects = {vertex: make_vertex(vertex) for vertex in VERTICES}
        graph = DiGraph(
            VERTICES,
            EDGES,
            layout=INITIAL_LAYOUT,
            vertex_mobjects=vertex_mobjects,
            edge_config={
                "stroke_color": GRAY_400,
                "stroke_width": 3,
                "tip_config": {"tip_length": 0.16, "tip_width": 0.16},
            },
        )

        for edge in EDGES:
            style_edge(graph.edges[edge], GRAY_500, 3.0, 0.32)
        for vertex in VERTICES:
            style_vertex(graph.vertices[vertex], GRAY_500, GRAY_800, 2.2, 1)

        source_ring = Circle(radius=0.47, stroke_color=PRIMARY_RED, stroke_width=3, fill_opacity=0).move_to(
            graph.vertices["S"]
        )
        target_ring = Circle(radius=0.47, stroke_color=PRIMARY_RED, stroke_width=3, fill_opacity=0).move_to(
            graph.vertices["T"]
        )

        self.add(title, rule, subtitle, graph, source_ring, target_ring)
        self.wait(2.7)

        competing_flashes = []
        for path_vertices in COMPETING_PATHS:
            path = path_from_vertices(graph, path_vertices, GRAY_500, 6.5, 0.42)
            competing_flashes.append(ShowPassingFlash(path, time_width=0.18, run_time=2.2))

        self.play(
            LaggedStart(*competing_flashes, lag_ratio=0.28),
            source_ring.animate.set_stroke(width=4.3),
            target_ring.animate.set_stroke(width=4.3),
            run_time=3.0,
            rate_func=smooth,
        )
        self.wait(0.5)

        selection_anims = []
        for edge in SELECTED_EDGES:
            live_edge = graph.edges[edge]
            flash = live_edge.copy()
            flash.set_color(HIGHLIGHT_RED)
            flash.set_stroke(color=HIGHLIGHT_RED, width=10, opacity=0.74)
            selection_anims.append(
                AnimationGroup(
                    live_edge.animate.set_color(PRIMARY_RED).set_stroke(color=PRIMARY_RED, width=5.8, opacity=1),
                    ShowPassingFlash(flash, time_width=0.45),
                )
            )

        vertex_anims = []
        for vertex in SELECTED_VERTICES:
            vertex_mob = graph.vertices[vertex]
            vertex_anims.extend(
                [
                    vertex_mob[0].animate.set_stroke(color=PRIMARY_RED, width=3.6).set_fill(color=WHITE, opacity=1),
                    vertex_mob[1].animate.set_color(PRIMARY_RED),
                ]
            )

        self.play(
            LaggedStart(*selection_anims, lag_ratio=0.42),
            AnimationGroup(*vertex_anims, lag_ratio=0.05),
            source_ring.animate.set_stroke(width=2.0, opacity=0.42),
            target_ring.animate.set_stroke(width=2.0, opacity=0.42),
            run_time=4.2,
            rate_func=smooth,
        )
        self.wait(0.8)

        route_path = path_from_vertices(graph, SELECTED_VERTICES, PRIMARY_RED, 6.0, 1)
        pulse_group = route_pulse(graph.vertices["S"].get_center())
        pulse_halo, pulse_core = pulse_group
        trace = TracedPath(
            pulse_core.get_center,
            stroke_width=7,
            stroke_color=PRIMARY_RED,
            dissipating_time=3.2,
        )
        moving_flash = path_from_vertices(graph, SELECTED_VERTICES, HIGHLIGHT_RED, 13, 0.55)

        self.add(trace, pulse_group)
        self.play(
            MoveAlongPath(pulse_core, route_path),
            ShowPassingFlash(moving_flash, time_width=0.13),
            run_time=7.4,
            rate_func=linear,
        )
        pulse_halo.clear_updaters()
        self.wait(0.9)

        non_selected_edges = [graph.edges[edge] for edge in EDGES if edge not in SELECTED_EDGES]
        non_selected_vertices = [graph.vertices[vertex] for vertex in VERTICES if vertex not in SELECTED_VERTICES]
        cleanup_group = VGroup(*non_selected_edges, *non_selected_vertices, source_ring, target_ring, pulse_group, trace)

        selected_edge_settle = [
            graph.edges[edge].animate.set_color(PRIMARY_RED).set_stroke(color=PRIMARY_RED, width=6.2, opacity=1)
            for edge in SELECTED_EDGES
        ]
        self.play(
            FadeOut(cleanup_group),
            AnimationGroup(*selected_edge_settle, lag_ratio=0.07),
            run_time=2.5,
            rate_func=smooth,
        )

        final_moves = [graph.vertices[vertex].animate.move_to(FINAL_LAYOUT[vertex]) for vertex in SELECTED_VERTICES]
        final_vertex_styles = []
        for vertex in SELECTED_VERTICES:
            vertex_mob = graph.vertices[vertex]
            final_vertex_styles.extend(
                [
                    vertex_mob[0].animate.set_stroke(color=PRIMARY_RED, width=3.8),
                    vertex_mob[1].animate.set_color(GRAY_900),
                ]
            )

        final_rule = Rectangle(width=9.35, height=0.035, stroke_width=0, fill_color=PRIMARY_RED, fill_opacity=1)
        final_rule.move_to(DOWN * 1.12)

        self.play(
            AnimationGroup(*final_moves, lag_ratio=0.04),
            AnimationGroup(*final_vertex_styles, lag_ratio=0.04),
            FadeOut(subtitle),
            FadeIn(final_rule),
            run_time=3.6,
            rate_func=smooth,
        )
        self.wait(6.4)


def render_variant(args: _Args) -> None:
    video_path, poster_path = output_paths()
    result = subprocess.run(render_command(args, video_path.stem, poster=False), check=False)
    if result.returncode != 0:
        raise SystemExit(result.returncode)
    promote(video_path.name, video_path)
    result = subprocess.run(render_command(args, poster_path.stem, poster=True), check=False)
    if result.returncode != 0:
        raise SystemExit(result.returncode)
    promote(poster_path.name, poster_path)


def main() -> int:
    args = parse_args()
    render_variant(args)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
