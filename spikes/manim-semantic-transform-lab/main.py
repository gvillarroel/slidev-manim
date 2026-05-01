#!/usr/bin/env -S uv run --script
# /// script
# dependencies = [
#   "imageio-ffmpeg>=0.6.0",
#   "manim>=0.20.0,<0.21",
# ]
# ///

from __future__ import annotations

import argparse
import os
import shutil
import subprocess
import sys
from pathlib import Path

import imageio_ffmpeg
from manimpango import list_fonts
from manim import (
    DOWN,
    LEFT,
    ORIGIN,
    PI,
    RIGHT,
    UP,
    AnimationGroup,
    Circle,
    DashedLine,
    FadeIn,
    FadeOut,
    FadeTransform,
    GrowFromCenter,
    Line,
    MoveToTarget,
    Rectangle,
    ReplacementTransform,
    Scene,
    Text,
    Transform,
    TransformFromCopy,
    TransformMatchingShapes,
    TransformMatchingTex,
    Triangle,
    VGroup,
    smooth,
)

SPIKE_DIR = Path(__file__).resolve().parent
REPO_ROOT = SPIKE_DIR.parent.parent
SPIKE_NAME = SPIKE_DIR.name
OUTPUT_DIR = REPO_ROOT / "videos" / SPIKE_NAME
STAGING_DIR = OUTPUT_DIR / ".manim"

BLACK = "#000000"
WHITE = "#ffffff"
PAGE_BACKGROUND = "#f7f7f7"
PRIMARY_RED = "#9e1b32"
GRAY_100 = "#e7e7e7"
GRAY_200 = "#cfcfcf"
GRAY_300 = "#b5b5b5"
GRAY_500 = "#828282"
GRAY_600 = "#696969"
GRAY_700 = "#4f4f4f"
FONT = "Open Sans" if "Open Sans" in list_fonts() else "Arial"


class _Args(argparse.Namespace):
    quality: str


def parse_args() -> _Args:
    parser = argparse.ArgumentParser(description="Render the semantic transform narration lab.")
    parser.add_argument("--quality", choices=("low", "medium", "high", "production", "4k"), default="medium")
    return parser.parse_args(namespace=_Args())


def quality_flag(quality: str) -> str:
    return {
        "low": "-ql",
        "medium": "-qm",
        "high": "-qh",
        "production": "-qp",
        "4k": "-qk",
    }[quality]


def output_paths() -> tuple[Path, Path]:
    return OUTPUT_DIR / f"{SPIKE_NAME}.webm", OUTPUT_DIR / f"{SPIKE_NAME}.png"


def render_environment() -> dict[str, str]:
    ffmpeg_path = Path(imageio_ffmpeg.get_ffmpeg_exe()).resolve()
    return {
        **os.environ,
        "PATH": f"{ffmpeg_path.parent}{os.pathsep}{os.environ.get('PATH', '')}",
    }


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
        "--media_dir",
        str(STAGING_DIR),
        "-o",
        stem,
        str(Path(__file__).resolve()),
        "SemanticTransformNarrationScene",
    ]
    if poster:
        command.insert(-2, "-s")
    else:
        command.insert(-2, "--format=webm")
        command.insert(-2, "-t")
    return command


def promote(target_name: str, destination: Path) -> None:
    matches = sorted(STAGING_DIR.glob(f"**/{target_name}"))
    if not matches:
        raise FileNotFoundError(target_name)
    destination.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(matches[-1], destination)


def chip(color: str, width: float, height: float, opacity: float = 1.0) -> Rectangle:
    return Rectangle(
        width=width,
        height=height,
        stroke_width=0,
        fill_color=color,
        fill_opacity=opacity,
    )


def label(text: str, size: int = 23, color: str = GRAY_700) -> Text:
    return Text(text, font=FONT, font_size=size, color=color)


def tex_token(text: str, size: int = 44) -> Text:
    token = Text(text, font=FONT, font_size=size, color=BLACK)
    token.tex_string = text
    for part in token.submobjects:
        part.tex_string = text
    return token


def tex_row(tokens: list[str]) -> VGroup:
    row = VGroup(*[tex_token(token) for token in tokens])
    row.arrange(RIGHT, buff=0.18)
    return row


def story_card(title: str, body: str, width: float = 2.75) -> VGroup:
    body_box = Rectangle(
        width=width,
        height=1.24,
        stroke_color=GRAY_500,
        stroke_width=2,
        fill_color=WHITE,
        fill_opacity=1,
    )
    title_text = label(title, size=23, color=BLACK).move_to(body_box.get_top() + DOWN * 0.31)
    body_text = label(body, size=20, color=GRAY_600).move_to(body_box.get_bottom() + UP * 0.35)
    return VGroup(body_box, title_text, body_text)


def shape_pack() -> VGroup:
    square = chip(BLACK, 0.58, 0.58)
    triangle = Triangle(stroke_width=0, fill_color=GRAY_600, fill_opacity=1).scale(0.44)
    dot = Circle(radius=0.32, stroke_width=0, fill_color=PRIMARY_RED, fill_opacity=1)
    return VGroup(square, triangle, dot).arrange(RIGHT, buff=0.34)


class SemanticTransformNarrationScene(Scene):
    def construct(self) -> None:
        if os.environ.get("SPIKE_RENDER_TARGET") == "poster":
            self.camera.background_color = WHITE

        stage = Rectangle(
            width=13.35,
            height=7.45,
            stroke_color=GRAY_200,
            stroke_width=2,
            fill_color=PAGE_BACKGROUND,
            fill_opacity=0.96,
        )
        self.add(stage)

        top_y = 1.85
        source = story_card("claim", "A + B").move_to(LEFT * 4.85 + UP * top_y)
        evidence_slot = Rectangle(
            width=2.75,
            height=1.24,
            stroke_color=GRAY_300,
            stroke_width=2,
            fill_color=GRAY_100,
            fill_opacity=0.3,
        ).move_to(LEFT * 1.65 + UP * top_y)
        proof_slot = Rectangle(
            width=2.75,
            height=1.24,
            stroke_color=GRAY_300,
            stroke_width=2,
            fill_color=GRAY_100,
            fill_opacity=0.3,
        ).move_to(RIGHT * 1.65 + UP * top_y)
        final_slot = Rectangle(
            width=2.75,
            height=1.24,
            stroke_color=GRAY_300,
            stroke_width=2,
            fill_color=GRAY_100,
            fill_opacity=0.3,
        ).move_to(RIGHT * 4.85 + UP * top_y)

        route_a = DashedLine(source.get_right(), evidence_slot.get_left(), color=GRAY_300, stroke_width=3, dash_length=0.18)
        route_b = DashedLine(evidence_slot.get_right(), proof_slot.get_left(), color=GRAY_300, stroke_width=3, dash_length=0.18)
        route_c = DashedLine(proof_slot.get_right(), final_slot.get_left(), color=GRAY_300, stroke_width=3, dash_length=0.18)
        routes = VGroup(route_a, route_b, route_c)

        anchor = chip(PRIMARY_RED, 0.46, 0.46).move_to(source[0].get_left() + RIGHT * 0.44)
        anchor_target = Circle(radius=0.27, stroke_width=0, fill_color=PRIMARY_RED, fill_opacity=1).move_to(source[0].get_left() + RIGHT * 0.44)

        self.play(FadeIn(source), FadeIn(VGroup(evidence_slot, proof_slot, final_slot)), FadeIn(routes), run_time=1.1)
        self.play(GrowFromCenter(anchor), run_time=0.6)
        self.wait(2.2)

        self.play(Transform(anchor, anchor_target), run_time=1.0, rate_func=smooth)
        source.generate_target()
        source.target.scale(0.92).move_to(LEFT * 1.65 + UP * top_y)
        self.play(MoveToTarget(source), anchor.animate.move_to(LEFT * 1.65 + UP * 2.32), run_time=2.7, rate_func=smooth)
        self.wait(1.0)

        handoff_badge = chip(PRIMARY_RED, 0.34, 0.34).move_to(proof_slot.get_left() + RIGHT * 0.48)
        proof_line = Line(evidence_slot.get_right(), proof_slot.get_left(), color=PRIMARY_RED, stroke_width=5)
        self.play(FadeIn(proof_line), run_time=0.6)
        self.play(
            TransformFromCopy(anchor, handoff_badge),
            run_time=1.4,
            path_arc=-PI / 5,
            rate_func=smooth,
        )
        self.wait(1.8)

        proof_card = story_card("proof", "A + B = C").move_to(proof_slot)
        proof_mark = Circle(radius=0.29, stroke_width=0, fill_color=PRIMARY_RED, fill_opacity=1).move_to(proof_card[0].get_right() + LEFT * 0.41)
        self.play(
            ReplacementTransform(source, proof_card),
            ReplacementTransform(handoff_badge, proof_mark),
            FadeOut(proof_line),
            anchor.animate.set_opacity(0.18),
            run_time=2.2,
            rate_func=smooth,
        )
        self.wait(1.2)

        shape_source = shape_pack().move_to(LEFT * 4.45 + DOWN * 1.25)
        shape_target = VGroup(shape_source[2].copy(), shape_source[0].copy(), shape_source[1].copy())
        shape_target.arrange(RIGHT, buff=0.34).move_to(LEFT * 1.75 + DOWN * 1.25)
        shape_caption = label("same parts", size=20).next_to(shape_source, UP, buff=0.3)
        shape_caption_target = label("new order", size=20).next_to(shape_target, UP, buff=0.3)
        self.play(FadeIn(shape_source), FadeIn(shape_caption), run_time=0.8)
        self.play(
            TransformMatchingShapes(shape_source, shape_target, path_arc=PI / 4),
            FadeTransform(shape_caption, shape_caption_target),
            run_time=2.7,
            rate_func=smooth,
        )
        self.wait(0.9)

        equation_source = tex_row(["A", "+", "B", "=", "C"]).move_to(RIGHT * 1.45 + DOWN * 1.25)
        equation_target = tex_row(["C", "-", "B", "=", "A"]).move_to(RIGHT * 4.35 + DOWN * 1.25)
        equation_caption = label("same symbols", size=20).next_to(equation_source, UP, buff=0.3)
        equation_caption_target = label("new role", size=20).next_to(equation_target, UP, buff=0.3)
        self.play(FadeIn(equation_source), FadeIn(equation_caption), run_time=0.8)
        self.play(
            TransformMatchingTex(equation_source, equation_target, path_arc=-PI / 5),
            FadeTransform(equation_caption, equation_caption_target),
            run_time=2.8,
            rate_func=smooth,
        )
        self.wait(1.1)

        unreadable_morph_source = VGroup(
            chip(GRAY_600, 0.52, 0.76),
            chip(GRAY_500, 0.38, 1.04),
            chip(BLACK, 0.68, 0.44),
            Circle(radius=0.3, stroke_width=0, fill_color=GRAY_700, fill_opacity=1),
        ).arrange(RIGHT, buff=0.18).move_to(LEFT * 4.25 + DOWN * 2.85)
        incompatible_target = VGroup(
            chip(WHITE, 2.55, 0.92),
            Line(LEFT * 0.92, RIGHT * 0.92, color=BLACK, stroke_width=5),
            Circle(radius=0.22, stroke_width=0, fill_color=PRIMARY_RED, fill_opacity=1).shift(RIGHT * 1.08),
        ).move_to(LEFT * 0.95 + DOWN * 2.85)
        incompatible_target[0].set_stroke(GRAY_500, width=2)
        topology_caption = label("topology changes", size=20).next_to(unreadable_morph_source, UP, buff=0.3)
        topology_caption_target = label("fade, then land", size=20).next_to(incompatible_target, UP, buff=0.3)
        self.play(FadeIn(unreadable_morph_source), FadeIn(topology_caption), run_time=0.7)
        self.play(
            FadeTransform(unreadable_morph_source, incompatible_target, stretch=False, dim_to_match=0),
            FadeTransform(topology_caption, topology_caption_target),
            run_time=1.8,
            rate_func=smooth,
        )
        self.wait(1.0)

        final_card = story_card("decision", "keep identity").move_to(final_slot)
        final_mark = Circle(radius=0.29, stroke_width=0, fill_color=PRIMARY_RED, fill_opacity=1).move_to(final_card[0].get_right() + LEFT * 0.41)
        self.play(
            ReplacementTransform(proof_card, final_card),
            ReplacementTransform(proof_mark, final_mark),
            FadeOut(anchor),
            FadeOut(VGroup(shape_target, shape_caption_target, equation_target, equation_caption_target)),
            FadeOut(VGroup(incompatible_target, topology_caption_target)),
            run_time=2.6,
            rate_func=smooth,
        )
        self.play(
            FadeOut(VGroup(evidence_slot, proof_slot, routes)),
            final_slot.animate.set_stroke(PRIMARY_RED, width=3).set_fill(WHITE, opacity=1),
            run_time=1.2,
            rate_func=smooth,
        )
        resolved = VGroup(final_slot, final_card, final_mark)
        self.play(resolved.animate.move_to(ORIGIN).scale(1.35), run_time=1.0, rate_func=smooth)
        self.wait(6.3)


def render_variant(args: _Args) -> None:
    video_path, poster_path = output_paths()
    result = subprocess.run(
        render_command(args, video_path.stem, poster=False),
        check=False,
        env={**render_environment(), "SPIKE_RENDER_TARGET": "video"},
    )
    if result.returncode != 0:
        raise SystemExit(result.returncode)
    promote(video_path.name, video_path)

    result = subprocess.run(
        render_command(args, poster_path.stem, poster=True),
        check=False,
        env={**render_environment(), "SPIKE_RENDER_TARGET": "poster"},
    )
    if result.returncode != 0:
        raise SystemExit(result.returncode)
    promote(poster_path.name, poster_path)


def main() -> int:
    args = parse_args()
    render_variant(args)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
