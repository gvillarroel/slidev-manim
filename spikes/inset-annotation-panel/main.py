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

MAIN_VIDEO = OUTPUT_DIR / "inset-annotation-panel-main.webm"
MAIN_POSTER = OUTPUT_DIR / "inset-annotation-panel-main.png"
ZOOM_VIDEO = OUTPUT_DIR / "inset-annotation-panel-zoom.webm"
ZOOM_POSTER = OUTPUT_DIR / "inset-annotation-panel-zoom.png"


class _Args(argparse.Namespace):
    quality: str
    preview: bool


def parse_args() -> _Args:
    parser = argparse.ArgumentParser(
        description="Render the inset-annotation-panel Manim spike."
    )
    parser.add_argument(
        "--quality",
        choices=("low", "medium", "high", "production", "4k"),
        default="medium",
        help="Manim quality preset. Defaults to medium for quick iteration.",
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


def build_command(
    args: _Args,
    *,
    variant: str,
    target: Path,
    poster: bool,
    resolution: str,
) -> tuple[list[str], dict[str, str]]:
    STAGING_DIR.mkdir(parents=True, exist_ok=True)
    command = [
        sys.executable,
        "-m",
        "manim",
        "render",
        quality_flag(args.quality),
    ]

    if poster:
        command.append("-s")
    else:
        command.extend(["--format", "webm", "-t"])
        if args.preview:
            command.append("-p")

    command.extend(
        [
            "-r",
            resolution,
            "-o",
            target.stem,
            "--media_dir",
            str(STAGING_DIR),
        ]
    )
    command.extend([str(Path(__file__).resolve()), "InsetAnnotationPanelScene"])

    env = os.environ.copy()
    env["SPIKE_RENDER_TARGET"] = "poster" if poster else "video"
    env["SPIKE_VARIANT"] = variant
    return command, env


def promote_rendered_file(target_name: str, destination: Path) -> None:
    matches = sorted(
        STAGING_DIR.glob(f"**/{target_name}"),
        key=lambda path: path.stat().st_mtime,
    )
    if not matches:
        raise FileNotFoundError(f"Could not find {target_name} under {STAGING_DIR}")

    destination.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(matches[-1], destination)


def render_asset(
    args: _Args,
    *,
    variant: str,
    target: Path,
    poster: bool,
    resolution: str,
) -> int:
    command, env = build_command(
        args,
        variant=variant,
        target=target,
        poster=poster,
        resolution=resolution,
    )
    result = subprocess.run(command, env=env)
    if result.returncode != 0:
        return result.returncode
    promote_rendered_file(target.name, target)
    return 0


def main() -> int:
    args = parse_args()
    if STAGING_DIR.exists():
        shutil.rmtree(STAGING_DIR)

    tasks = [
        ("main", MAIN_VIDEO, False, "1600,900"),
        ("main", MAIN_POSTER, True, "1600,900"),
        ("zoom", ZOOM_VIDEO, False, "1200,1200"),
        ("zoom", ZOOM_POSTER, True, "1200,1200"),
    ]

    for variant, target, poster, resolution in tasks:
        result = render_asset(
            args,
            variant=variant,
            target=target,
            poster=poster,
            resolution=resolution,
        )
        if result != 0:
            return result

    return 0


if __name__ == "__main__":
    raise SystemExit(main())


from manim import (
    DOWN,
    LEFT,
    ORIGIN,
    RIGHT,
    Circle,
    Create,
    Dot,
    FadeIn,
    FadeOut,
    Line,
    Rectangle,
    Scene,
    UP,
    VGroup,
    config,
    linear,
)


if os.environ.get("SPIKE_VARIANT") == "zoom":
    config.frame_width = 8.0
    config.frame_height = 8.0


def corner_brackets(
    width: float,
    height: float,
    *,
    length: float = 0.34,
    color: str = GRAY_300,
    stroke_width: float = 4,
) -> VGroup:
    left = -width / 2
    right = width / 2
    top = height / 2
    bottom = -height / 2
    corners = VGroup()
    for x, y, sx, sy in (
        (left, top, 1, -1),
        (right, top, -1, -1),
        (left, bottom, 1, 1),
        (right, bottom, -1, 1),
    ):
        corners.add(
            Line([x, y, 0], [x + sx * length, y, 0], color=color, stroke_width=stroke_width),
            Line([x, y, 0], [x, y + sy * length, 0], color=color, stroke_width=stroke_width),
        )
    return corners


def square_panel(width: float, height: float, *, stroke: str = GRAY_300, fill: str = WHITE) -> Rectangle:
    return Rectangle(
        width=width,
        height=height,
        stroke_color=stroke,
        stroke_width=3,
        fill_color=fill,
        fill_opacity=0.98,
    )


class InsetAnnotationPanelScene(Scene):
    def construct(self) -> None:
        variant = os.environ.get("SPIKE_VARIANT", "main")
        self.camera.background_color = PAGE_BACKGROUND

        if variant == "zoom":
            self.construct_zoom()
        else:
            self.construct_main()

    def construct_main(self) -> None:
        stage = Rectangle(width=12.8, height=7.15, stroke_width=0, fill_color=PAGE_BACKGROUND, fill_opacity=1)
        source_panel = square_panel(7.6, 4.65, stroke=GRAY_300).shift(LEFT * 2.15)
        inset_panel = square_panel(3.25, 3.25, stroke=GRAY_300).shift(RIGHT * 4.25 + DOWN * 0.08)

        source_guides = VGroup(
            Line(LEFT * 5.55 + UP * 1.2, RIGHT * 1.0 + UP * 1.2, color=GRAY_200, stroke_width=5),
            Line(LEFT * 5.55 + ORIGIN, RIGHT * 1.0, color=GRAY_200, stroke_width=5),
            Line(LEFT * 5.55 + DOWN * 1.2, RIGHT * 1.0 + DOWN * 1.2, color=GRAY_200, stroke_width=5),
        )
        source_guides.set_opacity(0.72)

        roi = corner_brackets(1.08, 1.08, length=0.25, color=GRAY_400, stroke_width=4)
        roi.move_to(LEFT * 0.85)
        inset_slot = corner_brackets(2.34, 2.34, length=0.32, color=GRAY_300, stroke_width=4)
        inset_slot.move_to(inset_panel)
        inset_cross = VGroup(
            Line(LEFT * 0.78, LEFT * 0.52, color=GRAY_200, stroke_width=4),
            Line(RIGHT * 0.52, RIGHT * 0.78, color=GRAY_200, stroke_width=4),
            Line(DOWN * 0.78, DOWN * 0.52, color=GRAY_200, stroke_width=4),
            Line(UP * 0.52, UP * 0.78, color=GRAY_200, stroke_width=4),
        ).move_to(inset_panel)
        pending_path = Line(LEFT * 5.35 + UP * 1.2, LEFT * 0.85 + UP * 1.2, color=GRAY_600, stroke_width=8)
        pending_drop = Line(LEFT * 0.85 + UP * 1.2, LEFT * 0.85, color=GRAY_400, stroke_width=5)
        bridge = Line(LEFT * 0.3, RIGHT * 2.56 + DOWN * 0.08, color=GRAY_300, stroke_width=5)

        dot = Dot(LEFT * 5.35 + UP * 1.2, radius=0.15, color=PRIMARY_RED)
        focus_position = inset_panel.get_center()
        focus_halo = Circle(radius=0.86, color=PRIMARY_RED, stroke_width=4).move_to(focus_position)
        terminal_brackets = corner_brackets(2.62, 2.62, length=0.36, color=PRIMARY_RED, stroke_width=4).move_to(inset_panel)

        self.add(stage, source_panel, inset_panel, source_guides, roi, inset_slot, inset_cross, pending_path, pending_drop, bridge, dot)
        self.wait(2.6)

        active_path = Line(LEFT * 5.35 + UP * 1.2, LEFT * 0.85 + UP * 1.2, color=PRIMARY_RED, stroke_width=8)
        self.play(Create(active_path), dot.animate.move_to(LEFT * 0.85 + UP * 1.2), run_time=3.8, rate_func=linear)
        self.wait(0.9)

        active_drop = Line(LEFT * 0.85 + UP * 1.2, LEFT * 0.85, color=PRIMARY_RED, stroke_width=6)
        self.play(Create(active_drop), dot.animate.move_to(LEFT * 0.85), roi.animate.set_color(PRIMARY_RED), run_time=2.7, rate_func=linear)
        self.wait(1.0)

        bridge_active = Line(LEFT * 0.3, RIGHT * 2.56 + DOWN * 0.08, color=PRIMARY_RED, stroke_width=6)
        self.play(Create(bridge_active), dot.animate.move_to(RIGHT * 2.56 + DOWN * 0.08), run_time=2.9, rate_func=linear)
        self.wait(0.8)

        self.play(
            dot.animate.move_to(focus_position).scale(1.6),
            Create(focus_halo),
            run_time=2.2,
        )
        self.wait(1.0)

        resolved_cluster = VGroup(inset_panel, inset_cross, dot, focus_halo, terminal_brackets)
        self.play(
            FadeOut(active_path),
            FadeOut(active_drop),
            FadeOut(bridge_active),
            FadeOut(bridge),
            FadeOut(pending_drop),
            FadeOut(pending_path),
            FadeOut(source_panel),
            FadeOut(source_guides),
            FadeOut(roi),
            FadeOut(inset_slot),
            run_time=0.6,
        )
        resolved_cluster.scale(1.1).shift(LEFT * 4.25)
        self.play(FadeIn(terminal_brackets), run_time=0.2)
        self.wait(7.7)

    def construct_zoom(self) -> None:
        stage = Rectangle(width=7.7, height=7.7, stroke_width=0, fill_color=PAGE_BACKGROUND, fill_opacity=1)
        panel = square_panel(6.25, 6.25, stroke=GRAY_300)
        entry_slot = corner_brackets(1.28, 1.28, length=0.24, color=GRAY_400, stroke_width=4).shift(LEFT * 1.28 + UP * 0.56)
        detail_slot = corner_brackets(3.55, 3.55, length=0.4, color=GRAY_300, stroke_width=4).shift(RIGHT * 0.42 + DOWN * 0.08)
        aperture = Rectangle(
            width=0.36,
            height=1.52,
            stroke_color=PRIMARY_RED,
            stroke_width=4,
            fill_color=PAGE_BACKGROUND,
            fill_opacity=1,
        ).shift(LEFT * 0.28 + UP * 0.12)
        cross = VGroup(
            Line(LEFT * 1.34, LEFT * 0.7, color=GRAY_200, stroke_width=4),
            Line(RIGHT * 0.7, RIGHT * 1.34, color=GRAY_200, stroke_width=4),
            Line(DOWN * 1.34, DOWN * 0.7, color=GRAY_200, stroke_width=4),
            Line(UP * 0.7, UP * 1.34, color=GRAY_200, stroke_width=4),
        ).shift(RIGHT * 0.42 + DOWN * 0.08)
        source_dot = Dot(LEFT * 1.28 + UP * 0.56, radius=0.16, color=PRIMARY_RED)
        expanded_position = RIGHT * 0.42 + DOWN * 0.08
        guide_in = Line(LEFT * 1.28 + UP * 0.56, LEFT * 0.28 + UP * 0.12, color=GRAY_300, stroke_width=5)
        guide_out = Line(LEFT * 0.1 + UP * 0.12, expanded_position, color=GRAY_300, stroke_width=5)
        ring = Circle(radius=1.62, color=PRIMARY_RED, stroke_width=4).move_to(expanded_position)
        terminal = corner_brackets(3.9, 3.9, length=0.44, color=PRIMARY_RED, stroke_width=4).shift(RIGHT * 0.42 + DOWN * 0.08)

        self.add(stage, panel, cross, entry_slot, detail_slot, aperture, guide_in, guide_out, source_dot)
        self.wait(2.6)

        guide_in_active = Line(LEFT * 1.28 + UP * 0.56, LEFT * 0.28 + UP * 0.12, color=PRIMARY_RED, stroke_width=6)
        self.play(Create(guide_in_active), source_dot.animate.move_to(LEFT * 0.28 + UP * 0.12), run_time=3.2, rate_func=linear)
        self.wait(1.0)

        squeeze = Dot(LEFT * 0.28 + UP * 0.12, radius=0.1, color=PRIMARY_RED)
        self.play(source_dot.animate.scale(0.55), FadeIn(squeeze), aperture.animate.set_height(1.0), run_time=1.8)
        self.wait(1.2)

        guide_out_active = Line(LEFT * 0.1 + UP * 0.12, expanded_position, color=PRIMARY_RED, stroke_width=6)
        self.play(
            Create(guide_out_active),
            source_dot.animate.move_to(expanded_position).scale(3.4),
            run_time=3.0,
            rate_func=linear,
        )
        self.wait(1.0)

        self.play(Create(ring), detail_slot.animate.set_opacity(0.24), run_time=2.2)
        self.wait(1.0)

        self.play(
            FadeOut(entry_slot),
            FadeOut(aperture),
            FadeOut(guide_in),
            FadeOut(guide_out),
            FadeOut(guide_in_active),
            FadeOut(guide_out_active),
            FadeOut(squeeze),
            FadeOut(detail_slot),
            FadeIn(terminal),
            run_time=2.0,
        )
        self.wait(7.9)
