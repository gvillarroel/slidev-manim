#!/usr/bin/env -S uv run --script
# /// script
# dependencies = [
#   "manim>=0.20.0",
# ]
# ///

from __future__ import annotations

import argparse
import copy
import os
import shutil
import subprocess
import sys
import xml.etree.ElementTree as ET
from pathlib import Path

from manim import (
    DOWN,
    LEFT,
    ORIGIN,
    RIGHT,
    UP,
    AnimationGroup,
    ArcBetweenPoints,
    Circle,
    Create,
    FadeIn,
    FadeOut,
    Line,
    ReplacementTransform,
    Scene,
    Succession,
    SVGMobject,
    VGroup,
    WHITE,
    smooth,
)

SPIKE_DIR = Path(__file__).resolve().parent
REPO_ROOT = SPIKE_DIR.parent.parent
SPIKE_NAME = SPIKE_DIR.name
ASSET_DIR = SPIKE_DIR / "assets"
OUTPUT_DIR = REPO_ROOT / "videos" / SPIKE_NAME
STAGING_DIR = OUTPUT_DIR / ".manim"
GENERATED_DIR = OUTPUT_DIR / ".generated"

PRIMARY_RED = "#9e1b32"
PRIMARY_ORANGE = "#e77204"
PRIMARY_YELLOW = "#f1c319"
WHITE_HEX = "#ffffff"
SVG_NS = "http://www.w3.org/2000/svg"

ROLE_LAYOUT = {
    "source": {
        "body": (5.7, ORIGIN + DOWN * 0.05),
        "slot": (3.05, LEFT * 0.45 + DOWN * 0.15),
        "accent": (0.42, LEFT * 1.96 + UP * 1.06),
        "delete_badge": (0.96, RIGHT * 2.2 + UP * 1.12),
    },
    "middle": {
        "body": (5.1, ORIGIN + DOWN * 0.02),
        "slot": (2.16, RIGHT * 0.02 + DOWN * 0.02),
        "accent": (0.4, ORIGIN + DOWN * 0.02),
    },
    "target": {
        "body": (5.25, RIGHT * 0.14 + DOWN * 0.08),
        "slot": (1.28, RIGHT * 2.22 + UP * 1.12),
        "accent": (0.42, LEFT * 0.7 + DOWN * 1.06),
    },
}
ROLE_Z_INDEX = {"body": 1, "slot": 2, "accent": 3, "delete_badge": 4}


class _Args(argparse.Namespace):
    quality: str


def parse_args() -> _Args:
    parser = argparse.ArgumentParser(description="Render the svg-subelement-transform spike.")
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
    ]
    command.append("-s" if poster else "-t")
    command.extend([str(Path(__file__).resolve()), "SvgSubelementTransformScene"])
    return command


def promote(target_name: str, destination: Path) -> None:
    matches = sorted(STAGING_DIR.glob(f"**/{target_name}"))
    if not matches:
        raise FileNotFoundError(target_name)
    destination.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(matches[-1], destination)


def _find_group_by_id(root: ET.Element, role: str) -> ET.Element:
    for element in root.iter():
        if element.attrib.get("id") == role:
            return element
    raise ValueError(f"Could not find SVG group id={role!r}")


def write_role_fragment(stage: str, role: str) -> Path:
    ET.register_namespace("", SVG_NS)
    source_path = ASSET_DIR / f"{stage}.svg"
    tree = ET.parse(source_path)
    root = tree.getroot()
    role_group = copy.deepcopy(_find_group_by_id(root, role))

    out_root = ET.Element(
        f"{{{SVG_NS}}}svg",
        {
            "viewBox": root.attrib.get("viewBox", "0 0 400 240"),
            "width": root.attrib.get("width", "400"),
            "height": root.attrib.get("height", "240"),
        },
    )
    out_root.append(role_group)

    destination = GENERATED_DIR / "fragments" / f"{stage}-{role}.svg"
    destination.parent.mkdir(parents=True, exist_ok=True)
    ET.ElementTree(out_root).write(destination, encoding="utf-8", xml_declaration=False)
    return destination


def load_role(stage: str, role: str) -> SVGMobject:
    width, position = ROLE_LAYOUT[stage][role]
    fragment_path = write_role_fragment(stage, role)
    mobject = SVGMobject(str(fragment_path))
    mobject.scale_to_fit_width(width)
    mobject.move_to(position)
    mobject.set_z_index(ROLE_Z_INDEX[role])
    return mobject


def build_stage(stage: str, include_deleted: bool = True) -> dict[str, SVGMobject]:
    roles = list(ROLE_LAYOUT[stage])
    if not include_deleted:
        roles = [role for role in roles if role != "delete_badge"]
    return {role: load_role(stage, role) for role in roles}


def stage_group(parts: dict[str, SVGMobject]) -> VGroup:
    return VGroup(*[parts[role] for role in ("body", "slot", "accent", "delete_badge") if role in parts])


def squeeze_gate() -> VGroup:
    left_bar = Line(LEFT * 2.05 + UP * 1.12, LEFT * 2.05 + DOWN * 1.12, color=PRIMARY_ORANGE, stroke_width=10)
    right_bar = Line(RIGHT * 2.05 + UP * 1.12, RIGHT * 2.05 + DOWN * 1.12, color=PRIMARY_ORANGE, stroke_width=10)
    gate = VGroup(left_bar, right_bar)
    gate.set_z_index(0)
    gate.set_opacity(0.88)
    return gate


def final_poster_composition() -> VGroup:
    source = stage_group(build_stage("source", include_deleted=False)).scale(0.62).move_to(LEFT * 3.25 + DOWN * 0.08)
    target = stage_group(build_stage("target")).scale(0.92).move_to(RIGHT * 2.95 + DOWN * 0.02)
    path = ArcBetweenPoints(
        source.get_right() + RIGHT * 0.18,
        target.get_left() + LEFT * 0.18,
        angle=-0.42,
        color=PRIMARY_ORANGE,
        stroke_width=8,
    )
    path.set_z_index(0)
    return VGroup(path, source, target)


class SvgSubelementTransformScene(Scene):
    def construct(self) -> None:
        self.camera.background_color = WHITE
        poster_mode = os.environ.get("SPIKE_RENDER_TARGET") == "poster"

        if poster_mode:
            self.add(final_poster_composition())
            return

        current = build_stage("source")
        source = stage_group(current)
        self.add(source)
        self.wait(2.6)

        pulse = Circle(radius=0.13, stroke_width=0, fill_color=PRIMARY_YELLOW, fill_opacity=1)
        pulse.move_to(current["accent"].get_center())
        delete_path = ArcBetweenPoints(
            current["accent"].get_center(),
            current["delete_badge"].get_center(),
            angle=-0.36,
            color=PRIMARY_ORANGE,
            stroke_width=7,
        )
        delete_path.set_z_index(0)
        ring = Circle(
            radius=0.5,
            stroke_color=PRIMARY_YELLOW,
            stroke_width=7,
            fill_color=WHITE_HEX,
            fill_opacity=0,
        )
        ring.move_to(current["delete_badge"].get_center())

        self.play(Create(delete_path), FadeIn(pulse, scale=0.7), run_time=1.0, rate_func=smooth)
        self.play(pulse.animate.move_to(current["delete_badge"].get_center()).scale(1.55), run_time=1.1, rate_func=smooth)
        self.play(FadeIn(ring, scale=0.85), current["delete_badge"].animate.scale(0.84), run_time=0.65)
        self.play(
            FadeOut(current["delete_badge"], scale=0.08, shift=UP * 0.18),
            FadeOut(ring, scale=1.2),
            FadeOut(pulse, scale=0.3),
            FadeOut(delete_path),
            run_time=1.25,
        )
        self.remove(current["delete_badge"])
        del current["delete_badge"]
        self.wait(1.0)

        gate = squeeze_gate()
        middle = build_stage("middle")
        self.play(FadeIn(gate), run_time=0.65)
        self.play(
            AnimationGroup(
                ReplacementTransform(current["body"], middle["body"], path_arc=-0.12),
                ReplacementTransform(current["slot"], middle["slot"], path_arc=0.08),
                ReplacementTransform(current["accent"], middle["accent"], path_arc=-0.18),
                lag_ratio=0.12,
            ),
            run_time=4.0,
            rate_func=smooth,
        )
        self.wait(2.0)
        self.play(FadeOut(gate), run_time=0.65)

        current = middle
        target = build_stage("target")
        transform_path = ArcBetweenPoints(
            current["body"].get_left() + LEFT * 0.2,
            target["slot"].get_center() + LEFT * 0.2,
            angle=0.64,
            color=PRIMARY_ORANGE,
            stroke_width=8,
        )
        transform_path.set_z_index(0)
        self.play(Create(transform_path), run_time=0.8)
        self.play(
            Succession(
                FadeOut(current["body"], shift=DOWN * 0.1, scale=0.97, run_time=0.32),
                Create(target["body"], run_time=0.93),
            ),
            run_time=1.25,
            rate_func=smooth,
        )
        self.play(
            AnimationGroup(
                ReplacementTransform(current["slot"], target["slot"], path_arc=-0.18),
                ReplacementTransform(current["accent"], target["accent"], path_arc=0.22),
                lag_ratio=0.16,
            ),
            run_time=2.95,
            rate_func=smooth,
        )

        halo = Circle(
            radius=0.35,
            stroke_color=PRIMARY_YELLOW,
            stroke_width=7,
            fill_color=WHITE_HEX,
            fill_opacity=0,
        )
        halo.move_to(target["accent"].get_center())
        halo.set_z_index(4)
        self.play(FadeIn(halo, scale=0.75), FadeOut(transform_path), run_time=0.55)
        self.play(FadeOut(halo, scale=1.35), run_time=0.6)
        self.wait(6.2)


def render_variant(args: _Args) -> None:
    video_path, poster_path = output_paths()

    video_env = os.environ.copy()
    video_env["SPIKE_RENDER_TARGET"] = "video"
    result = subprocess.run(render_command(args, video_path.stem, poster=False), check=False, env=video_env)
    if result.returncode != 0:
        raise SystemExit(result.returncode)
    promote(video_path.name, video_path)

    poster_env = os.environ.copy()
    poster_env["SPIKE_RENDER_TARGET"] = "poster"
    result = subprocess.run(render_command(args, poster_path.stem, poster=True), check=False, env=poster_env)
    if result.returncode != 0:
        raise SystemExit(result.returncode)
    promote(poster_path.name, poster_path)


def main() -> int:
    args = parse_args()
    render_variant(args)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
