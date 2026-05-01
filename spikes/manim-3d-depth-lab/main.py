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

import numpy as np
from manim import (
    DEGREES,
    GrowFromPoint,
    LaggedStart,
    MoveAlongPath,
    ParametricFunction,
    Prism,
    Rectangle,
    Sphere,
    Surface,
    ThreeDAxes,
    ThreeDScene,
    VGroup,
    WHITE,
    config,
    linear,
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
PAGE_BACKGROUND = "#f7f7f7"
GRAY_100 = "#e7e7e7"
GRAY_200 = "#cfcfcf"
GRAY_300 = "#b5b5b5"
GRAY_400 = "#9c9c9c"
GRAY_500 = "#828282"
GRAY_700 = "#4f4f4f"

config.transparent = True
config.background_opacity = 0.0

X_MIN = -2.35
X_MAX = 2.35
SAMPLE_XS = [-2.2, -1.1, 0.0, 1.1, 2.2]


class _Args(argparse.Namespace):
    quality: str


def parse_args() -> _Args:
    parser = argparse.ArgumentParser(description="Render the Manim 3D depth narration lab spike.")
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
    command.extend([str(Path(__file__).resolve()), "DepthNarrationScene"])
    return command


def promote(target_name: str, destination: Path) -> None:
    matches = sorted(STAGING_DIR.glob(f"**/{target_name}"))
    if not matches:
        raise FileNotFoundError(target_name)
    destination.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(max(matches, key=lambda path: path.stat().st_mtime), destination)


def ridge_height(x: float, y: float = 0.0) -> float:
    return 1.05 + 0.42 * np.sin(1.15 * x) + 0.18 * np.cos(2.0 * x) - 0.14 * y * y


class DepthNarrationScene(ThreeDScene):
    def construct(self) -> None:
        self.camera.background_color = WHITE
        self.camera.background_opacity = 0

        axes = ThreeDAxes(
            x_range=(-3, 3, 1),
            y_range=(-1.8, 1.8, 1),
            z_range=(0, 2.0, 1),
            x_length=6.0,
            y_length=3.6,
            z_length=2.4,
            axis_config={"color": GRAY_400, "stroke_width": 2, "include_ticks": False},
            tips=False,
        )
        depth_focus = axes.c2p(0, 0, 0.35)
        self.set_camera_orientation(phi=0 * DEGREES, theta=-90 * DEGREES, zoom=1.02, frame_center=depth_focus)

        floor = Rectangle(
            width=6.2,
            height=3.7,
            stroke_color=GRAY_200,
            stroke_width=1.5,
            fill_color=PAGE_BACKGROUND,
            fill_opacity=0.24,
        ).move_to(axes.c2p(0, 0, 0))

        surface = Surface(
            lambda u, v: axes.c2p(u, v, ridge_height(u, v)),
            u_range=(-2.65, 2.65),
            v_range=(-1.45, 1.45),
            resolution=(24, 12),
            checkerboard_colors=[GRAY_100, GRAY_200],
            fill_opacity=0.48,
            stroke_color=GRAY_300,
            stroke_width=0.32,
        )
        surface.set_shade_in_3d(True)

        shadow_path = ParametricFunction(
            lambda t: axes.c2p(t, 0, 0.018),
            t_range=(X_MIN, X_MAX),
            color=GRAY_500,
            stroke_width=5,
        )
        ridge_path = ParametricFunction(
            lambda t: axes.c2p(t, 0, ridge_height(t)),
            t_range=(X_MIN, X_MAX),
            color=PRIMARY_RED,
            stroke_width=7,
        )
        ridge_path.set_shade_in_3d(True)

        depth_columns = VGroup()
        sample_points = VGroup()
        for index, x_value in enumerate(SAMPLE_XS):
            z_value = ridge_height(x_value)
            column = Prism(
                dimensions=[0.11, 0.11, z_value],
                fill_color=GRAY_400,
                fill_opacity=0.34,
                stroke_width=0,
            ).move_to(axes.c2p(x_value, 0, z_value / 2))
            column.set_shade_in_3d(True)
            depth_columns.add(column)

            point_color = BLACK if index in (1, 3) else GRAY_700
            point = Sphere(
                center=axes.c2p(x_value, 0, z_value),
                radius=0.105,
                resolution=(10, 10),
                fill_color=point_color,
                fill_opacity=0.92,
                stroke_width=0,
            )
            point.set_color(point_color)
            point.set_shade_in_3d(True)
            sample_points.add(point)

        active_probe = Sphere(
            center=axes.c2p(X_MIN, 0, ridge_height(X_MIN)),
            radius=0.15,
            resolution=(14, 14),
            fill_color=PRIMARY_RED,
            fill_opacity=1,
            stroke_width=0,
        )
        active_probe.set_color(PRIMARY_RED)
        active_probe.set_shade_in_3d(True)

        self.add(floor, axes, surface, shadow_path, ridge_path, sample_points, active_probe)
        self.wait(2.8)

        column_reveal = LaggedStart(
            *[
                GrowFromPoint(column, point=axes.c2p(SAMPLE_XS[index], 0, 0))
                for index, column in enumerate(depth_columns)
            ],
            lag_ratio=0.14,
            run_time=5.2,
        )
        self.move_camera(
            phi=63 * DEGREES,
            theta=-49 * DEGREES,
            zoom=1.05,
            frame_center=depth_focus,
            run_time=5.2,
            rate_func=smooth,
            added_anims=[column_reveal],
        )
        self.wait(1.0)

        self.begin_ambient_camera_rotation(rate=0.035, about="theta")
        self.play(
            MoveAlongPath(active_probe, ridge_path),
            run_time=6.8,
            rate_func=linear,
        )
        self.stop_ambient_camera_rotation(about="theta")

        self.move_camera(
            phi=62 * DEGREES,
            theta=-42 * DEGREES,
            zoom=1.05,
            frame_center=depth_focus,
            run_time=2.6,
            rate_func=smooth,
        )
        self.wait(6.6)


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
