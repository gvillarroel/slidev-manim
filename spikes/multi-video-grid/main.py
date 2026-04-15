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

VARIANTS = {
    "orbit": {
        "scene": "MultiVideoGridOrbitScene",
        "resolution": "1600,900",
        "output": OUTPUT_DIR / "multi-video-grid-orbit.webm",
        "poster": OUTPUT_DIR / "multi-video-grid-orbit.png",
    },
    "pulse": {
        "scene": "MultiVideoGridPulseScene",
        "resolution": "1600,900",
        "output": OUTPUT_DIR / "multi-video-grid-pulse.webm",
        "poster": OUTPUT_DIR / "multi-video-grid-pulse.png",
    },
    "sweep": {
        "scene": "MultiVideoGridSweepScene",
        "resolution": "1600,900",
        "output": OUTPUT_DIR / "multi-video-grid-sweep.webm",
        "poster": OUTPUT_DIR / "multi-video-grid-sweep.png",
    },
    "merge": {
        "scene": "MultiVideoGridMergeScene",
        "resolution": "1600,900",
        "output": OUTPUT_DIR / "multi-video-grid-merge.webm",
        "poster": OUTPUT_DIR / "multi-video-grid-merge.png",
    },
}


class _Args(argparse.Namespace):
    quality: str
    preview: bool


def parse_args() -> _Args:
    parser = argparse.ArgumentParser(
        description="Render the multi-video-grid Manim spike."
    )
    parser.add_argument(
        "--quality",
        choices=("low", "medium", "high", "production", "4k"),
        default="medium",
        help="Manim quality preset. Defaults to medium for fast review.",
    )
    parser.add_argument(
        "--preview",
        action="store_true",
        help="Open the rendered video after completion.",
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


def render_command(args: _Args, variant_name: str, poster: bool) -> list[str]:
    STAGING_DIR.mkdir(parents=True, exist_ok=True)
    variant = VARIANTS[variant_name]

    command = [
        sys.executable,
        "-m",
        "manim",
        "render",
        quality_flag(args.quality),
        "-r",
        variant["resolution"],
        "-o",
        Path(variant["poster"] if poster else variant["output"]).stem,
        "--media_dir",
        str(STAGING_DIR),
    ]

    if poster:
        command.append("-s")
    else:
        command.extend(["--format", "webm", "-t"])
        if args.preview:
            command.append("-p")

    command.extend([str(Path(__file__).resolve()), variant["scene"]])
    return command


def promote_rendered_file(target_name: str, destination: Path) -> None:
    matches = sorted(STAGING_DIR.glob(f"**/{target_name}"))
    if not matches:
        raise FileNotFoundError(f"Could not find {target_name} under {STAGING_DIR}")

    destination.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(matches[-1], destination)


def run_variant(args: _Args, variant_name: str) -> int:
    variant = VARIANTS[variant_name]
    print(f"Rendering {variant['scene']} into {variant['output']}")

    video_result = subprocess.run(
        render_command(args, variant_name, poster=False),
        check=False,
        env={**os.environ, "SPIKE_RENDER_TARGET": "video"},
    )
    if video_result.returncode != 0:
        return video_result.returncode
    promote_rendered_file(Path(variant["output"]).name, variant["output"])

    poster_result = subprocess.run(
        render_command(args, variant_name, poster=True),
        check=False,
        env={**os.environ, "SPIKE_RENDER_TARGET": "poster"},
    )
    if poster_result.returncode != 0:
        return poster_result.returncode
    promote_rendered_file(Path(variant["poster"]).name, variant["poster"])

    return 0


from manim import (
    BLUE_E,
    DOWN,
    GREEN_E,
    GREY_B,
    GREY_D,
    LEFT,
    ORANGE,
    RIGHT,
    Scene,
    TEAL_E,
    Text,
    UP,
    WHITE,
    Circle,
    Create,
    FadeIn,
    Line,
    MoveAlongPath,
    RoundedRectangle,
    linear,
    there_and_back,
)


class BaseMultiVideoGridScene(Scene):
    accent = BLUE_E
    title = ""
    subtitle = ""

    def construct(self) -> None:
        if os.environ.get("SPIKE_RENDER_TARGET") == "poster":
            self.camera.background_color = WHITE

        shell = RoundedRectangle(
            width=11.0,
            height=4.9,
            corner_radius=0.34,
            stroke_color=self.accent,
            stroke_width=5,
        ).move_to(DOWN * 0.55)
        title = Text(self.title, font_size=42, color=GREY_D)
        title.to_edge(UP, buff=0.45)
        subtitle = Text(self.subtitle, font_size=21, color=GREY_B)
        subtitle.next_to(title, DOWN, buff=0.12)

        self.add(shell, title, subtitle)
        self.build_motion(shell)
        self.wait(0.15)

    def build_motion(self, shell: RoundedRectangle) -> None:
        raise NotImplementedError


class MultiVideoGridOrbitScene(BaseMultiVideoGridScene):
    accent = BLUE_E
    title = "Orbit"
    subtitle = "Circular motion keeps the frame alive without fighting the slide."

    def build_motion(self, shell: RoundedRectangle) -> None:
        center = shell.get_center()
        orbit_path = Circle(radius=1.45, color=GREY_B, stroke_width=6).move_to(
            center + LEFT * 1.3 + DOWN * 0.05
        )
        dot = Circle(radius=0.16, color=self.accent, stroke_width=4).set_fill(
            self.accent, opacity=1.0
        )
        dot.move_to(orbit_path.point_from_proportion(0.0))
        core = Circle(radius=0.13, color=self.accent, stroke_width=0).set_fill(
            self.accent, opacity=0.9
        ).move_to(orbit_path.get_center())
        label = Text("Independent path", font_size=24, color=GREY_D)
        label.move_to(shell.get_center() + DOWN * 1.95)

        self.play(Create(orbit_path), FadeIn(core), FadeIn(dot), FadeIn(label), run_time=0.4)
        self.play(MoveAlongPath(dot, orbit_path), run_time=2.4, rate_func=linear)


class MultiVideoGridPulseScene(BaseMultiVideoGridScene):
    accent = TEAL_E
    title = "Pulse"
    subtitle = "A centered signal test with repeated expansion and contraction."

    def build_motion(self, shell: RoundedRectangle) -> None:
        center = shell.get_center()
        outer_ring = Circle(radius=1.3, color=GREY_B, stroke_width=5).move_to(center)
        inner_ring = Circle(radius=0.82, color=self.accent, stroke_width=8).move_to(
            center
        )
        core = Circle(radius=0.36, color=self.accent, stroke_width=0).set_fill(
            self.accent, opacity=0.92
        ).move_to(center)
        left_bar = Line(
            center + LEFT * 2.4 + DOWN * 0.55,
            center + LEFT * 1.55 + DOWN * 0.55,
            color=GREY_B,
            stroke_width=8,
        )
        right_bar = Line(
            center + RIGHT * 1.55 + DOWN * 0.55,
            center + RIGHT * 2.4 + DOWN * 0.55,
            color=GREY_B,
            stroke_width=8,
        )
        caption = Text("Signal gain", font_size=24, color=GREY_D)
        caption.move_to(shell.get_center() + DOWN * 1.95)

        self.play(
            Create(outer_ring),
            Create(inner_ring),
            FadeIn(core),
            FadeIn(left_bar),
            FadeIn(right_bar),
            FadeIn(caption),
            run_time=0.45,
        )
        self.play(core.animate.scale(1.24), run_time=0.75, rate_func=there_and_back)
        self.play(inner_ring.animate.scale(1.12), run_time=0.85, rate_func=there_and_back)


class MultiVideoGridSweepScene(BaseMultiVideoGridScene):
    accent = ORANGE
    title = "Sweep"
    subtitle = "A horizontal pass checks how well the clip reads in a wide tile."

    def build_motion(self, shell: RoundedRectangle) -> None:
        center = shell.get_center()
        track = Line(
            center + LEFT * 4.25 + DOWN * 0.2,
            center + RIGHT * 4.25 + DOWN * 0.2,
            color=GREY_B,
            stroke_width=8,
        )
        tick_left = Line(
            center + LEFT * 4.25 + DOWN * 0.4,
            center + LEFT * 4.25 + DOWN * 0.0,
            color=GREY_B,
            stroke_width=4,
        )
        tick_mid = Line(
            center + DOWN * 0.4,
            center + DOWN * 0.0,
            color=GREY_B,
            stroke_width=4,
        )
        tick_right = Line(
            center + RIGHT * 4.25 + DOWN * 0.4,
            center + RIGHT * 4.25 + DOWN * 0.0,
            color=GREY_B,
            stroke_width=4,
        )
        marker = RoundedRectangle(
            width=0.52,
            height=0.52,
            corner_radius=0.14,
            stroke_color=self.accent,
            stroke_width=4,
        ).set_fill(self.accent, opacity=0.93)
        marker.move_to(center + LEFT * 4.25 + DOWN * 0.2)
        caption = Text("Track coverage", font_size=24, color=GREY_D)
        caption.move_to(shell.get_center() + DOWN * 1.95)

        self.play(
            Create(track),
            Create(tick_left),
            Create(tick_mid),
            Create(tick_right),
            FadeIn(marker),
            FadeIn(caption),
            run_time=0.35,
        )
        self.play(marker.animate.move_to(center + RIGHT * 4.25 + DOWN * 0.2), run_time=2.4, rate_func=linear)


class MultiVideoGridMergeScene(BaseMultiVideoGridScene):
    accent = GREEN_E
    title = "Merge"
    subtitle = "Two independent pieces converge into one shared result."

    def build_motion(self, shell: RoundedRectangle) -> None:
        center = shell.get_center()
        bridge = Line(
            center + LEFT * 2.35 + DOWN * 0.12,
            center + RIGHT * 2.35 + DOWN * 0.12,
            color=GREY_B,
            stroke_width=8,
        )
        left = Circle(radius=0.42, color=self.accent, stroke_width=6).set_fill(
            self.accent, opacity=0.92
        ).move_to(center + LEFT * 2.35 + DOWN * 0.12)
        right = Circle(radius=0.42, color=self.accent, stroke_width=6).set_fill(
            self.accent, opacity=0.92
        ).move_to(center + RIGHT * 2.35 + DOWN * 0.12)
        badge = RoundedRectangle(
            width=3.25,
            height=0.92,
            corner_radius=0.2,
            stroke_color=self.accent,
            stroke_width=4,
        ).set_fill(WHITE, opacity=0.92)
        badge.move_to(center + DOWN * 0.12)
        label = Text("Combined view", font_size=26, color=GREY_D)
        label.move_to(badge.get_center())
        caption = Text("Independent inputs", font_size=24, color=GREY_D)
        caption.move_to(shell.get_center() + DOWN * 1.95)

        self.play(
            Create(bridge),
            FadeIn(left),
            FadeIn(right),
            FadeIn(caption),
            run_time=0.35,
        )
        self.play(
            left.animate.move_to(center + LEFT * 0.62 + DOWN * 0.12),
            right.animate.move_to(center + RIGHT * 0.62 + DOWN * 0.12),
            run_time=1.5,
            rate_func=linear,
        )
        self.play(FadeIn(badge), FadeIn(label), run_time=0.35)


def main() -> int:
    args = parse_args()
    for variant_name in VARIANTS:
        result = run_variant(args, variant_name)
        if result != 0:
            return result
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
