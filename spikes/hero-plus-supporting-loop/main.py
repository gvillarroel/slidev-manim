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
    "hero": {
        "scene": "HeroPlusSupportingLoopHeroScene",
        "resolution": "1920,1080",
        "video": OUTPUT_DIR / "hero-plus-supporting-loop-hero.webm",
        "poster": OUTPUT_DIR / "hero-plus-supporting-loop-hero.png",
    },
    "support": {
        "scene": "HeroPlusSupportingLoopSupportScene",
        "resolution": "1080,1080",
        "video": OUTPUT_DIR / "hero-plus-supporting-loop-support.webm",
        "poster": OUTPUT_DIR / "hero-plus-supporting-loop-support.png",
    },
}


class _Args(argparse.Namespace):
    quality: str
    preview: bool


def parse_args() -> _Args:
    parser = argparse.ArgumentParser(
        description="Render the hero-plus-supporting-loop Manim spike."
    )
    parser.add_argument(
        "--quality",
        choices=("low", "medium", "high", "production", "4k"),
        default="medium",
        help="Manim quality preset. Defaults to medium for review speed.",
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
        "--format",
        "webm",
        "-o",
        (variant["poster"] if poster else variant["video"]).stem,
        "--media_dir",
        str(STAGING_DIR),
    ]
    if not poster:
        command.append("-t")
    if poster:
        command.append("-s")
    elif args.preview:
        command.append("-p")
    command.extend([str(Path(__file__).resolve()), variant["scene"]])
    return command


def promote_rendered_file(target_name: str, destination: Path) -> None:
    matches = sorted(STAGING_DIR.glob(f"**/{target_name}"))
    if not matches:
        raise FileNotFoundError(f"Could not find {target_name} under {STAGING_DIR}")

    destination.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(matches[-1], destination)


def render_variant(args: _Args, variant_name: str) -> None:
    variant = VARIANTS[variant_name]

    video_env = os.environ.copy()
    video_env["SPIKE_RENDER_TARGET"] = "video"
    print(f"Rendering {variant['scene']} into {variant['video']}")
    video_result = subprocess.run(
        render_command(args, variant_name, poster=False),
        check=False,
        env=video_env,
    )
    if video_result.returncode != 0:
        raise SystemExit(video_result.returncode)
    promote_rendered_file(variant["video"].name, variant["video"])

    poster_env = os.environ.copy()
    poster_env["SPIKE_RENDER_TARGET"] = "poster"
    print(f"Rendering {variant['scene']} poster into {variant['poster']}")
    poster_result = subprocess.run(
        render_command(args, variant_name, poster=True),
        check=False,
        env=poster_env,
    )
    if poster_result.returncode != 0:
        raise SystemExit(poster_result.returncode)
    promote_rendered_file(variant["poster"].name, variant["poster"])


def main() -> int:
    args = parse_args()
    for variant_name in VARIANTS:
        render_variant(args, variant_name)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())


from manim import (
    BLUE_B,
    BLUE_C,
    BLUE_D,
    BLUE_E,
    ORIGIN,
    Circle,
    Dot,
    FadeIn,
    Line,
    MoveAlongPath,
    Scene,
    WHITE,
    always_redraw,
    linear,
)


class HeroPlusSupportingLoopHeroScene(Scene):
    def construct(self) -> None:
        if os.environ.get("SPIKE_RENDER_TARGET") == "poster":
            self.camera.background_color = WHITE

        orbit = Circle(radius=3.25, color=BLUE_D, stroke_width=18)
        orbit.set_stroke(opacity=0.78)

        inner_orbit = Circle(radius=2.28, color=BLUE_C, stroke_width=8)
        inner_orbit.set_stroke(opacity=0.22)

        center_core = Circle(radius=0.48, color=BLUE_E, stroke_width=10)
        center_core.set_fill(BLUE_E, opacity=0.95)

        center_ring = Circle(radius=0.95, color=BLUE_B, stroke_width=6)
        center_ring.set_stroke(opacity=0.28)

        orbit_dot = Dot(color=BLUE_E, radius=0.18)
        orbit_dot.move_to(orbit.point_from_proportion(0))

        orbit_glow = always_redraw(
            lambda: Circle(radius=0.31, color=BLUE_E, stroke_width=6)
            .set_fill(BLUE_E, opacity=0.16)
            .move_to(orbit_dot)
        )

        anchor_points = []
        for proportion in (0.0, 0.25, 0.5, 0.75):
            anchor = Dot(color=BLUE_B, radius=0.07)
            anchor.move_to(orbit.point_from_proportion(proportion))
            anchor.set_opacity(0.45)
            anchor_points.append(anchor)

        self.add(inner_orbit, orbit, center_ring, center_core, *anchor_points, orbit_dot, orbit_glow)
        self.play(
            FadeIn(inner_orbit, scale=0.96),
            FadeIn(center_ring, scale=0.94),
            FadeIn(center_core, scale=0.92),
            FadeIn(orbit_dot),
            run_time=0.75,
        )
        self.play(
            MoveAlongPath(orbit_dot, orbit),
            run_time=4.4,
            rate_func=linear,
        )
        self.wait(0.12)


class HeroPlusSupportingLoopSupportScene(Scene):
    def construct(self) -> None:
        if os.environ.get("SPIKE_RENDER_TARGET") == "poster":
            self.camera.background_color = WHITE

        orbit = Circle(radius=1.62, color=BLUE_D, stroke_width=12)
        orbit.set_stroke(opacity=0.84)

        support_ring = Circle(radius=2.0, color=BLUE_B, stroke_width=5)
        support_ring.set_stroke(opacity=0.22)

        center_core = Circle(radius=0.34, color=BLUE_E, stroke_width=8)
        center_core.set_fill(BLUE_E, opacity=0.96)

        orbit_dot = Dot(color=BLUE_E, radius=0.12)
        orbit_dot.move_to(orbit.point_from_proportion(0))

        orbit_glow = always_redraw(
            lambda: Circle(radius=0.22, color=BLUE_E, stroke_width=4)
            .set_fill(BLUE_E, opacity=0.14)
            .move_to(orbit_dot)
        )

        guide = Line(
            orbit.point_from_proportion(0.0),
            orbit.point_from_proportion(0.5),
            color=BLUE_B,
            stroke_width=5,
        )
        guide.set_stroke(opacity=0.2)

        self.add(support_ring, guide, orbit, center_core, orbit_dot, orbit_glow)
        self.play(
            FadeIn(support_ring, scale=0.95),
            FadeIn(center_core, scale=0.9),
            FadeIn(orbit_dot),
            run_time=0.6,
        )
        self.play(
            MoveAlongPath(orbit_dot, orbit),
            run_time=3.6,
            rate_func=linear,
        )
        self.wait(0.12)
