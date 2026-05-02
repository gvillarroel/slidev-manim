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
PRIMARY_YELLOW = "#f1c319"
PRIMARY_GREEN = "#45842a"
PRIMARY_BLUE = "#007298"
PRIMARY_PURPLE = "#652f6c"
WHITE = "#ffffff"
GRAY = "#333e48"
GRAY_100 = "#e7e7e7"
GRAY_200 = "#cfcfcf"
GRAY_300 = "#b5b5b5"
GRAY_400 = "#9c9c9c"
GRAY_600 = "#696969"
GRAY_700 = "#4f4f4f"
HIGHLIGHT_RED = "#ffccd5"
HIGHLIGHT_ORANGE = "#ffe5cc"
HIGHLIGHT_YELLOW = "#fff4cc"
HIGHLIGHT_GREEN = "#dbffcc"
HIGHLIGHT_BLUE = "#cdf3ff"
HIGHLIGHT_PURPLE = "#f9ccff"
SHADOW_BLUE = "#004d66"
PAGE_BACKGROUND = "#f7f7f7"

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
    AnimationGroup,
    Circle,
    Create,
    DOWN,
    Dot,
    FadeIn,
    FadeOut,
    LEFT,
    Line,
    MoveAlongPath,
    RIGHT,
    Rectangle,
    ReplacementTransform,
    Scene,
    UP,
    VGroup,
    always_redraw,
    config,
    linear,
)


def _prepare_poster(scene: Scene) -> None:
    if os.environ.get("SPIKE_RENDER_TARGET") == "poster":
        scene.camera.background_color = PAGE_BACKGROUND


def setup_browser_audit_config() -> None:
    config.pixel_width = 1920
    config.pixel_height = 1080
    config.frame_height = 8.0
    config.frame_width = 8.0 * 16.0 / 9.0


def setup_device_audit_config() -> None:
    config.pixel_width = 1080
    config.pixel_height = 1920
    config.frame_width = 8.0
    config.frame_height = 8.0 * 16.0 / 9.0


def _accent_card(width: float, height: float, stroke_color: str, fill_opacity: float) -> Rectangle:
    card = Rectangle(width=width, height=height)
    card.set_stroke(stroke_color, width=4, opacity=0.6)
    card.set_fill(stroke_color, opacity=fill_opacity)
    return card


def _slot(width: float, height: float, color: str) -> Rectangle:
    slot = Rectangle(width=width, height=height)
    slot.set_stroke(color, width=3, opacity=0.22)
    slot.set_fill(color, opacity=0.035)
    return slot


def _pulse(radius: float = 0.12) -> tuple[Dot, Circle]:
    dot = Dot(color=PRIMARY_RED, radius=radius)
    halo = always_redraw(
        lambda: Circle(radius=radius * 2.6)
        .set_stroke(PRIMARY_RED, width=5, opacity=0.2)
        .set_fill(PRIMARY_RED, opacity=0.08)
        .move_to(dot)
    )
    return dot, halo


def _make_route(points: list) -> VGroup:
    segments = VGroup()
    for start, end in zip(points, points[1:]):
        segment = Line(start, end, color=GRAY_400, stroke_width=3)
        segment.set_stroke(opacity=0.28)
        segments.add(segment)
    return segments


def _move_on_segment(scene: Scene, dot: Dot, start, end, run_time: float) -> None:
    dot.move_to(start)
    path = Line(start, end)
    scene.play(MoveAlongPath(dot, path), run_time=run_time, rate_func=linear)


class DeviceFrameEmbedBrowserScene(Scene):
    def construct(self) -> None:
        _prepare_poster(self)

        source = VGroup(
            _accent_card(1.45, 0.72, PRIMARY_GREEN, 0.14),
            _accent_card(1.45, 0.72, PRIMARY_BLUE, 0.1),
            _accent_card(1.45, 0.72, PRIMARY_PURPLE, 0.1),
        ).arrange(DOWN, buff=0.24)
        source.move_to(LEFT * 3.7 + UP * 0.1)

        processor_slot = _slot(2.15, 1.65, PRIMARY_ORANGE).move_to(LEFT * 0.15 + UP * 0.1)
        receipt_slot = _slot(2.0, 1.55, PRIMARY_BLUE).move_to(RIGHT * 3.35 + UP * 0.1)
        processor_card = _accent_card(2.15, 1.65, PRIMARY_ORANGE, 0.12).move_to(processor_slot)
        receipt_card = _accent_card(2.0, 1.55, PRIMARY_GREEN, 0.15).move_to(receipt_slot)

        processor_marks = VGroup(
            Line(LEFT * 0.72, RIGHT * 0.72, color=PRIMARY_ORANGE, stroke_width=5),
            Line(LEFT * 0.48, RIGHT * 0.48, color=PRIMARY_ORANGE, stroke_width=5),
            Line(LEFT * 0.28, RIGHT * 0.28, color=PRIMARY_ORANGE, stroke_width=5),
        ).arrange(DOWN, buff=0.22)
        processor_marks.move_to(processor_card)
        processor_marks.set_stroke(opacity=0.45)

        receipt_marks = VGroup(
            Rectangle(width=1.3, height=0.18).set_fill(PRIMARY_GREEN, opacity=0.18).set_stroke(PRIMARY_GREEN, opacity=0),
            Rectangle(width=1.0, height=0.18).set_fill(PRIMARY_GREEN, opacity=0.18).set_stroke(PRIMARY_GREEN, opacity=0),
            Rectangle(width=1.45, height=0.18).set_fill(PRIMARY_GREEN, opacity=0.18).set_stroke(PRIMARY_GREEN, opacity=0),
        ).arrange(DOWN, buff=0.18)
        receipt_marks.move_to(receipt_card)

        points = [
            source.get_right() + RIGHT * 0.2,
            processor_slot.get_left() + LEFT * 0.22,
            processor_slot.get_right() + RIGHT * 0.22,
            receipt_slot.get_left() + LEFT * 0.22,
        ]
        routes = _make_route(points)
        dot, halo = _pulse(0.13)
        dot.move_to(points[0])

        source_focus = Rectangle(width=source.width + 0.34, height=source.height + 0.34)
        source_focus.set_stroke(PRIMARY_RED, width=4, opacity=0.55)
        source_focus.set_fill(PRIMARY_RED, opacity=0)
        source_focus.move_to(source)

        final_brackets = VGroup(
            Line(LEFT * 0.34 + UP * 0.72, LEFT * 0.72 + UP * 0.72, color=PRIMARY_RED, stroke_width=5),
            Line(LEFT * 0.72 + UP * 0.72, LEFT * 0.72 + UP * 0.34, color=PRIMARY_RED, stroke_width=5),
            Line(RIGHT * 0.34 + DOWN * 0.72, RIGHT * 0.72 + DOWN * 0.72, color=PRIMARY_RED, stroke_width=5),
            Line(RIGHT * 0.72 + DOWN * 0.72, RIGHT * 0.72 + DOWN * 0.34, color=PRIMARY_RED, stroke_width=5),
        )
        final_brackets.move_to(receipt_card)

        self.add(source, processor_slot, receipt_slot, routes, dot, halo, source_focus)
        self.wait(2.4)
        self.play(FadeOut(source_focus), run_time=0.7)
        _move_on_segment(self, dot, points[0], points[1], 3.0)
        self.play(
            ReplacementTransform(processor_slot, processor_card),
            FadeIn(processor_marks, shift=UP * 0.08),
            run_time=1.4,
        )
        self.wait(0.7)
        _move_on_segment(self, dot, points[2], points[3], 3.2)
        self.play(
            AnimationGroup(
                ReplacementTransform(receipt_slot, receipt_card),
                FadeIn(receipt_marks, shift=UP * 0.08),
                lag_ratio=0.15,
            ),
            run_time=1.5,
        )
        self.play(FadeOut(routes), FadeOut(halo), FadeOut(dot), run_time=1.2)
        resolved = VGroup(processor_card, processor_marks, receipt_card, receipt_marks, final_brackets)
        self.play(source.animate.set_opacity(0.35).shift(LEFT * 0.35), resolved.animate.shift(LEFT * 0.45), run_time=1.5)
        self.play(Create(final_brackets), run_time=1.0)
        self.wait(10.4)


class DeviceFrameEmbedDeviceScene(Scene):
    def construct(self) -> None:
        _prepare_poster(self)

        stack = VGroup(
            _accent_card(2.6, 0.56, PRIMARY_GREEN, 0.14),
            _accent_card(2.6, 0.56, PRIMARY_BLUE, 0.1),
            _accent_card(2.6, 0.56, PRIMARY_PURPLE, 0.1),
        ).arrange(DOWN, buff=0.26)
        stack.move_to(UP * 2.35)

        processor_slot = _slot(2.75, 1.05, PRIMARY_ORANGE).move_to(UP * 0.35)
        receipt_slot = _slot(2.75, 1.05, PRIMARY_BLUE).move_to(DOWN * 1.85)
        processor_card = _accent_card(2.75, 1.05, PRIMARY_ORANGE, 0.12).move_to(processor_slot)
        receipt_card = _accent_card(2.75, 1.05, PRIMARY_GREEN, 0.15).move_to(receipt_slot)

        processor_marks = VGroup(
            Line(LEFT * 0.75, RIGHT * 0.75, color=PRIMARY_ORANGE, stroke_width=5),
            Line(LEFT * 0.55, RIGHT * 0.55, color=PRIMARY_ORANGE, stroke_width=5),
        ).arrange(DOWN, buff=0.22)
        processor_marks.move_to(processor_card)
        processor_marks.set_stroke(opacity=0.45)

        receipt_marks = VGroup(
            Rectangle(width=1.35, height=0.16).set_fill(PRIMARY_GREEN, opacity=0.18).set_stroke(PRIMARY_GREEN, opacity=0),
            Rectangle(width=1.65, height=0.16).set_fill(PRIMARY_GREEN, opacity=0.18).set_stroke(PRIMARY_GREEN, opacity=0),
        ).arrange(DOWN, buff=0.18)
        receipt_marks.move_to(receipt_card)

        points = [
            stack.get_bottom() + DOWN * 0.18,
            processor_slot.get_top() + UP * 0.2,
            processor_slot.get_bottom() + DOWN * 0.2,
            receipt_slot.get_top() + UP * 0.2,
        ]
        routes = _make_route(points)
        dot, halo = _pulse(0.14)
        dot.move_to(points[0])

        stack_focus = Rectangle(width=stack.width + 0.34, height=stack.height + 0.32)
        stack_focus.set_stroke(PRIMARY_RED, width=4, opacity=0.55)
        stack_focus.set_fill(PRIMARY_RED, opacity=0)
        stack_focus.move_to(stack)

        final_brackets = VGroup(
            Line(LEFT * 0.44 + UP * 0.54, LEFT * 0.86 + UP * 0.54, color=PRIMARY_RED, stroke_width=5),
            Line(LEFT * 0.86 + UP * 0.54, LEFT * 0.86 + UP * 0.18, color=PRIMARY_RED, stroke_width=5),
            Line(RIGHT * 0.44 + DOWN * 0.54, RIGHT * 0.86 + DOWN * 0.54, color=PRIMARY_RED, stroke_width=5),
            Line(RIGHT * 0.86 + DOWN * 0.54, RIGHT * 0.86 + DOWN * 0.18, color=PRIMARY_RED, stroke_width=5),
        )
        final_brackets.move_to(receipt_card)

        self.add(stack, processor_slot, receipt_slot, routes, dot, halo, stack_focus)
        self.wait(2.4)
        self.play(FadeOut(stack_focus), run_time=0.7)
        _move_on_segment(self, dot, points[0], points[1], 3.0)
        self.play(
            ReplacementTransform(processor_slot, processor_card),
            FadeIn(processor_marks, shift=UP * 0.08),
            run_time=1.4,
        )
        self.wait(0.7)
        _move_on_segment(self, dot, points[2], points[3], 3.2)
        self.play(
            AnimationGroup(
                ReplacementTransform(receipt_slot, receipt_card),
                FadeIn(receipt_marks, shift=UP * 0.08),
                lag_ratio=0.15,
            ),
            run_time=1.5,
        )
        self.play(FadeOut(routes), FadeOut(halo), FadeOut(dot), run_time=1.2)
        resolved = VGroup(processor_card, processor_marks, receipt_card, receipt_marks, final_brackets)
        self.play(stack.animate.set_opacity(0.35).shift(UP * 0.28), resolved.animate.shift(UP * 0.16), run_time=1.5)
        self.play(Create(final_brackets), run_time=1.0)
        self.wait(10.4)
