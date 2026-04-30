#!/usr/bin/env -S uv run --script
# /// script
# dependencies = [
#   "manim>=0.19.0",
# ]
# ///

from __future__ import annotations

import argparse
import os
import shutil
import subprocess
import sys
from pathlib import Path

SPIKE_DIR = Path(__file__).resolve().parent
REPO_ROOT = SPIKE_DIR.parent.parent
SPIKE_NAME = SPIKE_DIR.name
OUTPUT_DIR = REPO_ROOT / "videos" / SPIKE_NAME
STAGING_DIR = OUTPUT_DIR / ".manim"

PRIMARY_RED = "#9e1b32"
PRIMARY_ORANGE = "#e77204"
PRIMARY_GREEN = "#45842a"
PRIMARY_BLUE = "#007298"
PRIMARY_PURPLE = "#652f6c"
GRAY = "#333e48"
HIGHLIGHT_RED = "#ffccd5"
HIGHLIGHT_ORANGE = "#ffe5cc"
HIGHLIGHT_GREEN = "#dbffcc"
HIGHLIGHT_BLUE = "#cdf3ff"
HIGHLIGHT_PURPLE = "#f9ccff"

VARIANTS = {
    "background-loop": ("BackgroundLoopScene", "1920,1080"),
    "corner-callout": ("CornerCalloutScene", "1280,720"),
    "side-by-side": ("SideBySideScene", "1600,900"),
    "inset-main": ("InsetMainScene", "1600,900"),
    "inset-detail": ("InsetDetailScene", "900,900"),
    "compare-left": ("CompareLeftScene", "1200,900"),
    "compare-right": ("CompareRightScene", "1200,900"),
    "timeline": ("TimelineScene", "1080,1600"),
    "grid-journey": ("GridJourneyScene", "900,900"),
    "grid-pie": ("GridPieScene", "900,900"),
    "grid-git": ("GridGitScene", "900,900"),
    "grid-flow": ("GridFlowScene", "900,900"),
    "hero-main": ("HeroMainScene", "1920,1080"),
    "hero-support": ("HeroSupportScene", "1080,1080"),
    "device-frame": ("DeviceFrameScene", "1600,900"),
}


class _Args(argparse.Namespace):
    quality: str


def parse_args() -> _Args:
    parser = argparse.ArgumentParser(description="Render the mermaid-layout-gallery spike.")
    parser.add_argument(
        "--quality",
        choices=("low", "medium", "high", "production", "4k"),
        default="medium",
        help="Manim quality preset.",
    )
    return parser.parse_args(namespace=_Args())


def quality_flag(quality: str) -> str:
    return {
        "low": "-ql",
        "medium": "-qm",
        "high": "-qh",
        "production": "-qp",
        "4k": "-qk",
    }[quality]


def output_paths(name: str) -> tuple[Path, Path]:
    return OUTPUT_DIR / f"{name}.webm", OUTPUT_DIR / f"{name}.png"


def render_command(args: _Args, scene_name: str, resolution: str, stem: str, poster: bool) -> list[str]:
    STAGING_DIR.mkdir(parents=True, exist_ok=True)
    command = [
        sys.executable,
        "-m",
        "manim",
        "render",
        quality_flag(args.quality),
        "-r",
        resolution,
        "--format",
        "webm",
        "-o",
        stem,
        "--media_dir",
        str(STAGING_DIR),
    ]
    command.append("-s" if poster else "-t")
    command.extend([str(Path(__file__).resolve()), scene_name])
    return command


def promote(target_name: str, destination: Path) -> None:
    matches = sorted(STAGING_DIR.glob(f"**/{target_name}"))
    if not matches:
        raise FileNotFoundError(f"Could not find {target_name}")
    destination.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(matches[-1], destination)


def render_variant(args: _Args, name: str) -> None:
    scene_name, resolution = VARIANTS[name]
    video_path, poster_path = output_paths(name)

    video_env = os.environ.copy()
    video_env["SPIKE_RENDER_TARGET"] = "video"
    result = subprocess.run(
        render_command(args, scene_name, resolution, video_path.stem, poster=False),
        check=False,
        env=video_env,
    )
    if result.returncode != 0:
        raise SystemExit(result.returncode)
    promote(video_path.name, video_path)

    poster_env = os.environ.copy()
    poster_env["SPIKE_RENDER_TARGET"] = "poster"
    result = subprocess.run(
        render_command(args, scene_name, resolution, poster_path.stem, poster=True),
        check=False,
        env=poster_env,
    )
    if result.returncode != 0:
        raise SystemExit(result.returncode)
    promote(poster_path.name, poster_path)


def main() -> int:
    args = parse_args()
    for name in VARIANTS:
        render_variant(args, name)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())


from manim import (
    ArcBetweenPoints,
    Arrow,
    Circle,
    Dot,
    FadeIn,
    LEFT,
    Line,
    MoveAlongPath,
    PI,
    RIGHT,
    RoundedRectangle,
    Scene,
    Sector,
    Text,
    UP,
    DOWN,
    VGroup,
    WHITE as MANIM_WHITE,
    always_redraw,
    linear,
)


def prep(scene: Scene) -> None:
    if os.environ.get("SPIKE_RENDER_TARGET") == "poster":
        scene.camera.background_color = MANIM_WHITE


def card(label: str, width: float, height: float, stroke: str, fill: str) -> VGroup:
    box = RoundedRectangle(width=width, height=height, corner_radius=0.18)
    box.set_stroke(stroke, width=6, opacity=0.9)
    box.set_fill(fill, opacity=0.95)
    text = Text(label, font_size=28, color=GRAY).move_to(box)
    return VGroup(box, text)


class BackgroundLoopScene(Scene):
    def construct(self) -> None:
        prep(self)
        orbit = Circle(radius=2.6, color=PRIMARY_BLUE, stroke_width=12).set_stroke(opacity=0.24)
        dot = Dot(color=PRIMARY_ORANGE, radius=0.16).move_to(orbit.point_from_proportion(0))
        glow = always_redraw(lambda: Circle(radius=0.34, color=PRIMARY_ORANGE, stroke_width=6).set_fill(PRIMARY_ORANGE, opacity=0.10).move_to(dot))
        rings = VGroup(
            Circle(radius=1.6, color=PRIMARY_GREEN, stroke_width=7).set_stroke(opacity=0.18),
            Circle(radius=3.5, color=PRIMARY_PURPLE, stroke_width=10).set_stroke(opacity=0.14),
        )
        self.add(rings, orbit, dot, glow)
        self.play(MoveAlongPath(dot, orbit), run_time=5.2, rate_func=linear)
        self.wait(0.2)


class CornerCalloutScene(Scene):
    def construct(self) -> None:
        prep(self)
        a = card("Collect", 2.2, 0.9, PRIMARY_GREEN, HIGHLIGHT_GREEN).shift(LEFT * 2.8)
        b = card("Review", 2.2, 0.9, PRIMARY_ORANGE, HIGHLIGHT_ORANGE)
        c = card("Ship", 2.2, 0.9, PRIMARY_RED, HIGHLIGHT_RED).shift(RIGHT * 2.8)
        pulse = Dot(color=PRIMARY_BLUE, radius=0.13).move_to(a.get_right())
        path = Line(a.get_right(), c.get_left(), color=PRIMARY_BLUE, stroke_width=8)
        self.add(a, b, c, Arrow(a.get_right(), b.get_left(), buff=0.12, color=PRIMARY_BLUE, stroke_width=8), Arrow(b.get_right(), c.get_left(), buff=0.12, color=PRIMARY_BLUE, stroke_width=8), pulse)
        self.play(MoveAlongPath(pulse, path), run_time=3.8, rate_func=linear)
        self.wait(0.2)


class SideBySideScene(Scene):
    def construct(self) -> None:
        prep(self)
        left = card("Boundary", 2.8, 1.0, PRIMARY_GREEN, HIGHLIGHT_GREEN).shift(LEFT * 3.8 + UP * 1.1)
        right = card("Service", 2.8, 1.0, PRIMARY_BLUE, HIGHLIGHT_BLUE).shift(RIGHT * 3.8 + UP * 1.1)
        request = Arrow(left.get_right() + DOWN * 1.1, right.get_left() + DOWN * 1.1, buff=0.12, color=PRIMARY_ORANGE, stroke_width=10)
        response = Arrow(right.get_left() + DOWN * 2.2, left.get_right() + DOWN * 2.2, buff=0.12, color=PRIMARY_RED, stroke_width=10)
        self.play(FadeIn(left), FadeIn(right), run_time=0.8)
        self.play(FadeIn(request), run_time=1.0)
        self.play(FadeIn(response), run_time=1.0)
        self.wait(0.4)


class InsetMainScene(Scene):
    def construct(self) -> None:
        prep(self)
        idle = card("Idle", 2.1, 0.9, PRIMARY_BLUE, HIGHLIGHT_BLUE).shift(LEFT * 3.3)
        active = card("Running", 2.6, 0.9, PRIMARY_ORANGE, HIGHLIGHT_ORANGE)
        done = card("Done", 2.1, 0.9, PRIMARY_GREEN, HIGHLIGHT_GREEN).shift(RIGHT * 3.3)
        path = ArcBetweenPoints(idle.get_right(), done.get_left(), angle=-PI / 6, color=PRIMARY_BLUE, stroke_width=8)
        dot = Dot(color=PRIMARY_RED, radius=0.14).move_to(path.get_start())
        self.add(idle, active, done, path, dot)
        self.play(MoveAlongPath(dot, path), run_time=4.4, rate_func=linear)
        self.wait(0.2)


class InsetDetailScene(Scene):
    def construct(self) -> None:
        prep(self)
        outer = Circle(radius=1.0, color=PRIMARY_BLUE, stroke_width=8).set_fill(HIGHLIGHT_BLUE, opacity=0.7)
        inner = Circle(radius=0.45, color=PRIMARY_ORANGE, stroke_width=6).set_fill(HIGHLIGHT_ORANGE, opacity=0.85)
        self.play(FadeIn(VGroup(outer, inner)), run_time=0.8)
        self.wait(0.8)


class CompareLeftScene(Scene):
    def construct(self) -> None:
        prep(self)
        c = card("Customer", 2.7, 0.9, PRIMARY_GREEN, HIGHLIGHT_GREEN).shift(UP * 1.8)
        o = card("Order", 2.4, 0.9, PRIMARY_BLUE, HIGHLIGHT_BLUE)
        i = card("Item", 2.2, 0.9, PRIMARY_ORANGE, HIGHLIGHT_ORANGE).shift(DOWN * 1.8)
        self.add(c, o, i, Line(c.get_bottom(), o.get_top(), color=PRIMARY_BLUE, stroke_width=8), Line(o.get_bottom(), i.get_top(), color=PRIMARY_RED, stroke_width=8))
        self.wait(1.0)


class CompareRightScene(Scene):
    def construct(self) -> None:
        prep(self)
        left = card("Read", 2.1, 0.9, PRIMARY_BLUE, HIGHLIGHT_BLUE).shift(LEFT * 2.8)
        right = card("Write", 2.1, 0.9, PRIMARY_PURPLE, HIGHLIGHT_PURPLE).shift(RIGHT * 2.8)
        center = card("Model", 2.3, 0.95, PRIMARY_GREEN, HIGHLIGHT_GREEN)
        self.add(left, center, right, Arrow(left.get_right(), center.get_left(), buff=0.1, color=PRIMARY_ORANGE, stroke_width=8), Arrow(center.get_right(), right.get_left(), buff=0.1, color=PRIMARY_RED, stroke_width=8))
        self.wait(1.0)


class TimelineScene(Scene):
    def construct(self) -> None:
        prep(self)
        line = Line(UP * 5.5, DOWN * 5.5, color=PRIMARY_BLUE, stroke_width=9)
        marks = VGroup(
            Dot(UP * 4.0, color=PRIMARY_GREEN, radius=0.15),
            Dot(UP * 1.5, color=PRIMARY_ORANGE, radius=0.15),
            Dot(DOWN * 1.2, color=PRIMARY_RED, radius=0.15),
            Dot(DOWN * 4.0, color=PRIMARY_PURPLE, radius=0.15),
        )
        cards = VGroup(
            card("Start", 2.2, 0.8, PRIMARY_GREEN, HIGHLIGHT_GREEN).next_to(marks[0], RIGHT, buff=0.6),
            card("Build", 2.2, 0.8, PRIMARY_ORANGE, HIGHLIGHT_ORANGE).next_to(marks[1], RIGHT, buff=0.6),
            card("Review", 2.2, 0.8, PRIMARY_RED, HIGHLIGHT_RED).next_to(marks[2], RIGHT, buff=0.6),
            card("Launch", 2.2, 0.8, PRIMARY_PURPLE, HIGHLIGHT_PURPLE).next_to(marks[3], RIGHT, buff=0.6),
        )
        self.add(line, marks, cards)
        self.wait(1.0)


class GridJourneyScene(Scene):
    def construct(self) -> None:
        prep(self)
        path = Line(LEFT * 2.8, RIGHT * 2.8, color=PRIMARY_BLUE, stroke_width=8)
        stops = VGroup(
            Dot(path.point_from_proportion(0.0), color=PRIMARY_GREEN, radius=0.14),
            Dot(path.point_from_proportion(0.5), color=PRIMARY_ORANGE, radius=0.14),
            Dot(path.point_from_proportion(1.0), color=PRIMARY_RED, radius=0.14),
        )
        traveler = Dot(color=PRIMARY_PURPLE, radius=0.12).move_to(stops[0])
        self.add(path, stops, traveler)
        self.play(MoveAlongPath(traveler, path), run_time=3.5, rate_func=linear)
        self.wait(0.2)


class GridPieScene(Scene):
    def construct(self) -> None:
        prep(self)
        sectors = VGroup(
            Sector(radius=2.2, start_angle=0, angle=PI * 0.6, color=PRIMARY_BLUE).set_fill(HIGHLIGHT_BLUE, opacity=0.9),
            Sector(radius=2.2, start_angle=PI * 0.6, angle=PI * 0.8, color=PRIMARY_GREEN).set_fill(HIGHLIGHT_GREEN, opacity=0.9),
            Sector(radius=2.2, start_angle=PI * 1.4, angle=PI * 0.6, color=PRIMARY_ORANGE).set_fill(HIGHLIGHT_ORANGE, opacity=0.9),
        )
        self.play(FadeIn(sectors), run_time=1.2)
        self.wait(0.8)


class GridGitScene(Scene):
    def construct(self) -> None:
        prep(self)
        main = Line(LEFT * 3.3, RIGHT * 3.3, color=PRIMARY_BLUE, stroke_width=8)
        branch = Line(LEFT * 0.8 + DOWN * 1.8, RIGHT * 2.2 + DOWN * 1.8, color=PRIMARY_GREEN, stroke_width=8)
        join = Line(RIGHT * 2.2 + DOWN * 1.8, RIGHT * 2.8, color=PRIMARY_GREEN, stroke_width=8)
        commits = VGroup(
            Dot(LEFT * 2.6, color=PRIMARY_BLUE, radius=0.13),
            Dot(LEFT * 1.1, color=PRIMARY_BLUE, radius=0.13),
            Dot(RIGHT * 1.4, color=PRIMARY_GREEN, radius=0.13).shift(DOWN * 1.8),
            Dot(RIGHT * 2.8, color=PRIMARY_RED, radius=0.13),
        )
        self.add(main, branch, join, commits)
        self.wait(1.0)


class GridFlowScene(Scene):
    def construct(self) -> None:
        prep(self)
        a = card("Idea", 2.0, 0.8, PRIMARY_PURPLE, HIGHLIGHT_PURPLE).shift(UP * 1.6)
        b = card("Test", 2.0, 0.8, PRIMARY_ORANGE, HIGHLIGHT_ORANGE)
        c = card("Adopt", 2.0, 0.8, PRIMARY_GREEN, HIGHLIGHT_GREEN).shift(DOWN * 1.6)
        self.add(a, b, c, Arrow(a.get_bottom(), b.get_top(), buff=0.1, color=PRIMARY_BLUE), Arrow(b.get_bottom(), c.get_top(), buff=0.1, color=PRIMARY_RED))
        self.wait(1.0)


class HeroMainScene(Scene):
    def construct(self) -> None:
        prep(self)
        top = card("Client", 3.0, 1.0, PRIMARY_GREEN, HIGHLIGHT_GREEN).shift(UP * 2.6)
        mid = card("Gateway", 3.2, 1.0, PRIMARY_BLUE, HIGHLIGHT_BLUE)
        bot = card("Services", 3.4, 1.0, PRIMARY_PURPLE, HIGHLIGHT_PURPLE).shift(DOWN * 2.6)
        self.add(top, mid, bot, Line(top.get_bottom(), mid.get_top(), color=PRIMARY_BLUE, stroke_width=10), Line(mid.get_bottom(), bot.get_top(), color=PRIMARY_RED, stroke_width=10))
        self.wait(1.0)


class HeroSupportScene(Scene):
    def construct(self) -> None:
        prep(self)
        loop = Circle(radius=1.7, color=PRIMARY_ORANGE, stroke_width=10).set_stroke(opacity=0.82)
        dot = Dot(color=PRIMARY_RED, radius=0.12).move_to(loop.point_from_proportion(0))
        self.add(loop, dot)
        self.play(MoveAlongPath(dot, loop), run_time=3.2, rate_func=linear)
        self.wait(0.2)


class DeviceFrameScene(Scene):
    def construct(self) -> None:
        prep(self)
        shell = RoundedRectangle(width=6.2, height=4.3, corner_radius=0.28)
        shell.set_stroke(PRIMARY_BLUE, width=8, opacity=0.9)
        shell.set_fill(HIGHLIGHT_BLUE, opacity=0.10)
        top = card("Search", 2.0, 0.7, PRIMARY_ORANGE, HIGHLIGHT_ORANGE).shift(UP * 1.0)
        bottom = card("Checkout", 2.4, 0.8, PRIMARY_GREEN, HIGHLIGHT_GREEN).shift(DOWN * 1.1)
        arrow = Arrow(top.get_bottom(), bottom.get_top(), buff=0.12, color=PRIMARY_RED, stroke_width=8)
        self.add(shell, top, bottom, arrow)
        self.wait(1.0)
