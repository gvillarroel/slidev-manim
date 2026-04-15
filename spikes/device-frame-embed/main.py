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
    "browser": {
        "scene": "DeviceFrameEmbedBrowserScene",
        "resolution": "1920,1080",
        "video": OUTPUT_DIR / "device-frame-embed-browser.webm",
        "poster": OUTPUT_DIR / "device-frame-embed-browser.png",
    },
    "device": {
        "scene": "DeviceFrameEmbedDeviceScene",
        "resolution": "1080,1920",
        "video": OUTPUT_DIR / "device-frame-embed-device.webm",
        "poster": OUTPUT_DIR / "device-frame-embed-device.png",
    },
}


class _Args(argparse.Namespace):
    quality: str
    preview: bool


def parse_args() -> _Args:
    parser = argparse.ArgumentParser(description="Render the device-frame-embed Manim spike.")
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
    video_result = subprocess.run(render_command(args, variant_name, poster=False), check=False, env=video_env)
    if video_result.returncode != 0:
        raise SystemExit(video_result.returncode)
    promote_rendered_file(variant["video"].name, variant["video"])

    poster_env = os.environ.copy()
    poster_env["SPIKE_RENDER_TARGET"] = "poster"
    print(f"Rendering {variant['scene']} poster into {variant['poster']}")
    poster_result = subprocess.run(render_command(args, variant_name, poster=True), check=False, env=poster_env)
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
    DOWN,
    Dot,
    FadeIn,
    LEFT,
    Line,
    MoveAlongPath,
    RIGHT,
    RoundedRectangle,
    Scene,
    UP,
    VGroup,
    WHITE,
    always_redraw,
    linear,
)


def _prepare_poster(scene: Scene) -> None:
    if os.environ.get("SPIKE_RENDER_TARGET") == "poster":
        scene.camera.background_color = WHITE


def _accent_card(width: float, height: float, stroke_color: str, fill_opacity: float) -> RoundedRectangle:
    card = RoundedRectangle(width=width, height=height, corner_radius=0.16)
    card.set_stroke(stroke_color, width=4, opacity=0.55)
    card.set_fill(stroke_color, opacity=fill_opacity)
    return card


class DeviceFrameEmbedBrowserScene(Scene):
    def construct(self) -> None:
        _prepare_poster(self)

        shell = RoundedRectangle(width=10.8, height=5.9, corner_radius=0.22)
        shell.set_stroke(BLUE_D, width=8, opacity=0.5)
        shell.set_fill(BLUE_D, opacity=0.02)

        viewport = RoundedRectangle(width=10.0, height=4.85, corner_radius=0.18)
        viewport.set_stroke(BLUE_C, width=4, opacity=0.2)
        viewport.set_fill(BLUE_C, opacity=0.03)

        chrome = VGroup(
            Dot(color=BLUE_B, radius=0.09),
            Dot(color=BLUE_B, radius=0.09),
            Dot(color=BLUE_B, radius=0.09),
        ).arrange(RIGHT, buff=0.13)
        chrome.set_opacity(0.45)
        chrome.to_corner(UP + LEFT).shift(RIGHT * 0.55 + DOWN * 0.45)

        address_bar = RoundedRectangle(width=4.1, height=0.34, corner_radius=0.14)
        address_bar.set_stroke(BLUE_B, width=2, opacity=0.18)
        address_bar.set_fill(BLUE_B, opacity=0.06)
        address_bar.next_to(chrome, RIGHT, buff=0.45).shift(DOWN * 0.01)

        card_top_left = _accent_card(2.35, 1.05, BLUE_C, 0.08).move_to(LEFT * 2.35 + UP * 0.7)
        card_top_right = _accent_card(2.9, 1.05, BLUE_C, 0.05).move_to(RIGHT * 2.15 + UP * 0.7)
        card_bottom = _accent_card(5.9, 1.15, BLUE_D, 0.05).move_to(DOWN * 1.45)

        guide = Line(LEFT * 3.65 + DOWN * 0.85, RIGHT * 3.65 + DOWN * 0.85, color=BLUE_B, stroke_width=5)
        guide.set_stroke(opacity=0.22)

        dot = Dot(color=BLUE_E, radius=0.15)
        dot.move_to(guide.get_start())

        glow = always_redraw(
            lambda: RoundedRectangle(width=0.6, height=0.6, corner_radius=0.3)
            .set_stroke(BLUE_E, width=6, opacity=0.25)
            .set_fill(BLUE_E, opacity=0.12)
            .move_to(dot)
        )

        self.add(shell, viewport, chrome, address_bar, card_top_left, card_top_right, card_bottom, guide, dot, glow)
        self.play(FadeIn(shell, scale=0.98), FadeIn(viewport, scale=0.98), run_time=0.6)
        self.play(FadeIn(card_top_left), FadeIn(card_top_right), FadeIn(card_bottom), FadeIn(dot), run_time=0.7)
        self.play(MoveAlongPath(dot, guide), run_time=4.0, rate_func=linear)
        self.wait(0.15)


class DeviceFrameEmbedDeviceScene(Scene):
    def construct(self) -> None:
        _prepare_poster(self)

        shell = RoundedRectangle(width=4.35, height=8.05, corner_radius=0.42)
        shell.set_stroke(BLUE_D, width=8, opacity=0.52)
        shell.set_fill(BLUE_D, opacity=0.02)

        screen = RoundedRectangle(width=3.58, height=6.95, corner_radius=0.22)
        screen.set_stroke(BLUE_C, width=4, opacity=0.18)
        screen.set_fill(BLUE_C, opacity=0.03)

        notch = RoundedRectangle(width=1.35, height=0.16, corner_radius=0.08)
        notch.set_stroke(BLUE_B, width=2, opacity=0.16)
        notch.set_fill(BLUE_B, opacity=0.05)
        notch.to_edge(UP).shift(DOWN * 0.42)

        stack = VGroup(
            _accent_card(2.25, 0.68, BLUE_C, 0.08),
            _accent_card(2.7, 0.68, BLUE_C, 0.06),
            _accent_card(2.25, 0.68, BLUE_C, 0.08),
        ).arrange(DOWN, buff=0.26)
        stack.shift(UP * 0.78)

        footer = _accent_card(2.65, 0.84, BLUE_D, 0.06).shift(DOWN * 1.65)

        path = Line(UP * 2.45, DOWN * 2.25, color=BLUE_B, stroke_width=5)
        path.set_stroke(opacity=0.24)

        dot = Dot(color=BLUE_E, radius=0.16)
        dot.move_to(path.get_start())

        glow = always_redraw(
            lambda: RoundedRectangle(width=0.62, height=0.62, corner_radius=0.31)
            .set_stroke(BLUE_E, width=6, opacity=0.25)
            .set_fill(BLUE_E, opacity=0.12)
            .move_to(dot)
        )

        self.add(shell, screen, notch, stack, footer, path, dot, glow)
        self.play(FadeIn(shell, scale=0.98), FadeIn(screen, scale=0.98), run_time=0.6)
        self.play(FadeIn(stack), FadeIn(footer), FadeIn(dot), run_time=0.7)
        self.play(MoveAlongPath(dot, path), run_time=3.8, rate_func=linear)
        self.wait(0.15)
