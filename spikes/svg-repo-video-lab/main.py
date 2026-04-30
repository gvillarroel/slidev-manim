#!/usr/bin/env -S uv run --script
# /// script
# dependencies = [
#   "manim>=0.20.0",
# ]
# ///

from __future__ import annotations

import argparse
import copy
import math
import os
import shutil
import subprocess
import sys
import urllib.error
import urllib.request
import xml.etree.ElementTree as ET
from dataclasses import dataclass
from pathlib import Path

from manim import (
    BOLD,
    DOWN,
    LEFT,
    ORIGIN,
    PI,
    RIGHT,
    UP,
    AnimationGroup,
    ArcBetweenPoints,
    Circle,
    Create,
    DashedLine,
    FadeIn,
    FadeOut,
    GrowFromCenter,
    Line,
    MovingCameraScene,
    ReplacementTransform,
    RoundedRectangle,
    SVGMobject,
    SurroundingRectangle,
    Text,
    Transform,
    TransformMatchingShapes,
    VGroup,
    WHITE,
    smooth,
)

SPIKE_DIR = Path(__file__).resolve().parent
REPO_ROOT = SPIKE_DIR.parent.parent
SPIKE_NAME = SPIKE_DIR.name
ASSET_DIR = SPIKE_DIR / "assets"
RAW_DIR = ASSET_DIR / "raw"
OUTPUT_DIR = REPO_ROOT / "videos" / SPIKE_NAME
STAGING_DIR = OUTPUT_DIR / ".manim"
GENERATED_DIR = OUTPUT_DIR / ".generated"
GENERATED_SVG_DIR = GENERATED_DIR / "svg"

PRIMARY_RED = "#9e1b32"
PRIMARY_ORANGE = "#e77204"
PRIMARY_YELLOW = "#f1c319"
PRIMARY_GREEN = "#45842a"
PRIMARY_BLUE = "#007298"
PRIMARY_PURPLE = "#652f6c"
SHADOW_BLUE = "#004d66"
SHADOW_PURPLE = "#431f47"
HIGHLIGHT_BLUE = "#cdf3ff"
PAGE_BACKGROUND = "#f7f7f7"
WHITE_HEX = "#ffffff"
GRAY = "#333e48"
GRAY_100 = "#e7e7e7"
GRAY_200 = "#cfcfcf"
GRAY_300 = "#b5b5b5"
GRAY_400 = "#9c9c9c"
GRAY_700 = "#4f4f4f"

SVG_NS = "http://www.w3.org/2000/svg"
ET.register_namespace("", SVG_NS)


@dataclass(frozen=True)
class SvgAsset:
    name: str
    source_url: str
    page_url: str
    fallback_svg: str


FALLBACK_ICON = """<?xml version="1.0" encoding="utf-8"?>
<svg width="800px" height="800px" viewBox="0 0 100 100" xmlns="http://www.w3.org/2000/svg">
  <rect x="18" y="18" width="64" height="64" rx="10" fill="#000000"/>
  <circle cx="38" cy="42" r="7" fill="#ffffff"/>
  <circle cx="62" cy="42" r="7" fill="#ffffff"/>
  <rect x="34" y="60" width="32" height="8" rx="4" fill="#ffffff"/>
</svg>
"""

ASSETS = [
    SvgAsset(
        "robot",
        "https://www.svgrepo.com/show/35383/robot.svg",
        "https://www.svgrepo.com/svg/35383/robot",
        FALLBACK_ICON,
    ),
    SvgAsset(
        "chart",
        "https://www.svgrepo.com/show/528126/chart.svg",
        "https://www.svgrepo.com/svg/528126/chart",
        FALLBACK_ICON,
    ),
    SvgAsset(
        "bulb",
        "https://www.svgrepo.com/show/27795/light-bulb.svg",
        "https://www.svgrepo.com/svg/27795/light-bulb",
        FALLBACK_ICON,
    ),
    SvgAsset(
        "text-document",
        "https://www.svgrepo.com/show/17578/text.svg",
        "https://www.svgrepo.com/svg/17578/text",
        FALLBACK_ICON,
    ),
    SvgAsset(
        "code-window",
        "https://www.svgrepo.com/show/245847/code.svg",
        "https://www.svgrepo.com/svg/245847/code",
        FALLBACK_ICON,
    ),
]


class _Args(argparse.Namespace):
    quality: str
    refresh_assets: bool


def parse_args() -> _Args:
    parser = argparse.ArgumentParser(description="Render the svg-repo-video-lab spike.")
    parser.add_argument("--quality", choices=("low", "medium", "high", "production", "4k"), default="medium")
    parser.add_argument("--refresh-assets", action="store_true", help="Redownload the source SVG Repo assets.")
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
    command.extend([str(Path(__file__).resolve()), "SvgRepoVideoLabScene"])
    return command


def promote(target_name: str, destination: Path) -> None:
    matches = sorted(STAGING_DIR.glob(f"**/{target_name}"))
    if not matches:
        raise FileNotFoundError(target_name)
    destination.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(max(matches, key=lambda path: path.stat().st_mtime), destination)


def is_svg_payload(payload: bytes) -> bool:
    head = payload[:512].lower()
    return b"<svg" in head or (b"<?xml" in head and b"<html" not in head)


def raw_asset_path(name: str) -> Path:
    return RAW_DIR / f"{name}.svg"


def fetch_svg(asset: SvgAsset) -> bytes:
    request = urllib.request.Request(
        asset.source_url,
        headers={
            "User-Agent": "Mozilla/5.0 (compatible; slidev-manim-svg-video-lab/1.0)",
            "Accept": "image/svg+xml,text/plain,*/*",
        },
    )
    with urllib.request.urlopen(request, timeout=30) as response:
        payload = response.read()
    if not is_svg_payload(payload):
        raise ValueError(f"SVG Repo returned a non-SVG payload for {asset.name}.")
    return payload


def ensure_raw_assets(refresh: bool = False) -> None:
    RAW_DIR.mkdir(parents=True, exist_ok=True)
    for asset in ASSETS:
        path = raw_asset_path(asset.name)
        if path.exists() and not refresh and is_svg_payload(path.read_bytes()):
            continue
        try:
            payload = fetch_svg(asset)
        except (urllib.error.URLError, TimeoutError, ValueError) as exc:
            payload = asset.fallback_svg.encode("utf-8")
            print(f"Using fallback SVG for {asset.name}: {exc}", file=sys.stderr)
        path.write_bytes(payload)


def decode_xml(path: Path) -> ET.Element:
    return ET.fromstring(path.read_bytes())


def _style_pairs(style: str) -> list[tuple[str, str]]:
    pairs: list[tuple[str, str]] = []
    for chunk in style.split(";"):
        if ":" not in chunk:
            continue
        key, value = chunk.split(":", 1)
        pairs.append((key.strip(), value.strip()))
    return pairs


def _write_style_pairs(pairs: list[tuple[str, str]]) -> str:
    return ";".join(f"{key}:{value}" for key, value in pairs if key)


def _set_style_fill(element: ET.Element, color: str) -> None:
    style = element.attrib.get("style")
    if not style:
        return
    pairs = _style_pairs(style)
    changed = False
    for index, (key, value) in enumerate(pairs):
        if key == "fill" and value.lower() != "none":
            pairs[index] = (key, color)
            changed = True
    if changed:
        element.set("style", _write_style_pairs(pairs))


def _set_style_stroke(element: ET.Element, color: str) -> None:
    style = element.attrib.get("style")
    if not style:
        return
    pairs = _style_pairs(style)
    changed = False
    for index, (key, value) in enumerate(pairs):
        if key == "stroke" and value.lower() != "none":
            pairs[index] = (key, color)
            changed = True
    if changed:
        element.set("style", _write_style_pairs(pairs))


def set_fill(element: ET.Element, color: str) -> None:
    fill = element.attrib.get("fill")
    if fill and fill.lower() != "none":
        element.set("fill", color)
    _set_style_fill(element, color)


def set_stroke(element: ET.Element, color: str) -> None:
    stroke = element.attrib.get("stroke")
    if stroke and stroke.lower() != "none":
        element.set("stroke", color)
    _set_style_stroke(element, color)


def write_tree(root: ET.Element, destination: Path) -> None:
    destination.parent.mkdir(parents=True, exist_ok=True)
    ET.ElementTree(root).write(destination, encoding="utf-8", xml_declaration=True)


def write_mono_variant(name: str, color: str, stroke: str | None = None) -> Path:
    root = decode_xml(raw_asset_path(name))
    for element in root.iter():
        set_fill(element, color)
        if stroke:
            set_stroke(element, stroke)
    destination = GENERATED_SVG_DIR / f"{name}-color.svg"
    write_tree(root, destination)
    return destination


def write_chart_variant() -> Path:
    root = decode_xml(raw_asset_path("chart"))
    palette = [PRIMARY_GREEN, PRIMARY_BLUE, PRIMARY_PURPLE, GRAY_300]
    fill_index = 0
    for element in root.iter():
        if element.attrib.get("fill") and element.attrib["fill"].lower() != "none":
            element.set("fill", palette[fill_index % len(palette)])
            fill_index += 1
    destination = GENERATED_SVG_DIR / "chart-color.svg"
    write_tree(root, destination)
    return destination


def write_text_document_variant() -> Path:
    root = decode_xml(raw_asset_path("text-document"))
    palette = [WHITE_HEX, GRAY_200, GRAY_300, GRAY_300, GRAY_300, PRIMARY_BLUE, PRIMARY_PURPLE]
    fill_index = 0
    for element in root.iter():
        style = element.attrib.get("style", "")
        if "fill:" in style:
            set_fill(element, palette[fill_index % len(palette)])
            fill_index += 1
        elif element.attrib.get("fill") and element.attrib["fill"].lower() != "none":
            element.set("fill", palette[fill_index % len(palette)])
            fill_index += 1
    destination = GENERATED_SVG_DIR / "text-document-color.svg"
    write_tree(root, destination)
    return destination


def write_code_variant() -> Path:
    root = decode_xml(raw_asset_path("code-window"))
    color_map = {
        "#E4EAF8": WHITE_HEX,
        "#5B5D6E": GRAY_700,
        "#D5DCED": GRAY_200,
        "#FF5050": PRIMARY_RED,
        "#FFF082": PRIMARY_YELLOW,
        "#A0FFB4": PRIMARY_GREEN,
        "#00C3FF": PRIMARY_BLUE,
        "#80E1FF": HIGHLIGHT_BLUE,
        "#00AAF0": SHADOW_BLUE,
        "#AFB9D2": GRAY_300,
        "#FFFFFF": WHITE_HEX,
    }

    def remap_fill(value: str) -> str:
        return color_map.get(value.upper(), value)

    for element in root.iter():
        if "fill" in element.attrib and element.attrib["fill"].lower() != "none":
            element.set("fill", remap_fill(element.attrib["fill"]))
        style = element.attrib.get("style")
        if style:
            pairs = _style_pairs(style)
            for index, (key, value) in enumerate(pairs):
                if key == "fill" and value.lower() != "none":
                    pairs[index] = (key, remap_fill(value))
            element.set("style", _write_style_pairs(pairs))
    destination = GENERATED_SVG_DIR / "code-window-color.svg"
    write_tree(root, destination)
    return destination


def write_text_badge_svg(label: str) -> Path:
    root = decode_xml(raw_asset_path("text-document"))
    view_box = root.attrib.get("viewBox", "0 0 309.267 309.267")
    text_node = ET.Element(
        f"{{{SVG_NS}}}text",
        {
            "x": "154.633",
            "y": "165",
            "text-anchor": "middle",
            "font-family": "Arial, sans-serif",
            "font-size": "38",
            "font-weight": "700",
            "fill": PRIMARY_PURPLE,
        },
    )
    text_node.text = label
    root.append(text_node)
    root.set("viewBox", view_box)
    destination = GENERATED_SVG_DIR / f"text-document-{label.lower()}.svg"
    write_tree(root, destination)
    return destination


def ensure_generated_variants() -> None:
    GENERATED_SVG_DIR.mkdir(parents=True, exist_ok=True)
    write_mono_variant("robot", PRIMARY_BLUE, SHADOW_BLUE)
    write_chart_variant()
    write_mono_variant("bulb", PRIMARY_YELLOW, PRIMARY_ORANGE)
    write_text_document_variant()
    write_code_variant()
    write_text_badge_svg("RAW")
    write_text_badge_svg("VIDEO")


def raw_path(name: str) -> Path:
    return raw_asset_path(name)


def color_path(name: str) -> Path:
    return GENERATED_SVG_DIR / f"{name}-color.svg"


def svg_icon(path: Path, height: float, position=ORIGIN, opacity: float = 1.0) -> SVGMobject:
    icon = SVGMobject(str(path))
    icon.scale_to_fit_height(height)
    icon.move_to(position)
    icon.set_opacity(opacity)
    return icon


def document_label(text: str, target: SVGMobject, color: str = PRIMARY_PURPLE) -> Text:
    label = Text(text, font="Arial", weight=BOLD, color=color)
    label.scale_to_fit_width(max(0.72, min(1.35, target.width * 0.5)))
    label.move_to(target.get_center() + UP * (target.height * 0.04))
    label.set_z_index(6)
    return label


def final_label(text: str) -> Text:
    label = Text(text, font="Arial", weight=BOLD, color=GRAY)
    label.scale_to_fit_width(1.25)
    return label


RAW_POSITIONS = {
    "robot": LEFT * 4.6 + UP * 1.85,
    "chart": LEFT * 4.6 + UP * 0.62,
    "bulb": LEFT * 4.6 + DOWN * 0.62,
    "text-document": LEFT * 4.6 + DOWN * 1.85,
    "code-window": LEFT * 3.25 + DOWN * 0.02,
}

COLOR_POSITIONS = {
    "robot": LEFT * 0.86 + UP * 1.92,
    "chart": LEFT * 0.86 + UP * 0.64,
    "bulb": LEFT * 0.86 + DOWN * 0.64,
    "text-document": LEFT * 0.86 + DOWN * 1.92,
    "code-window": RIGHT * 0.78 + DOWN * 0.02,
}

FINAL_CLUSTER_SHIFT = DOWN * 0.22
FINAL_POSITIONS = {
    "robot": RIGHT * 1.58 + UP * 1.4 + FINAL_CLUSTER_SHIFT,
    "chart": RIGHT * 0.78 + UP * 0.42 + FINAL_CLUSTER_SHIFT,
    "bulb": RIGHT * 2.34 + UP * 0.22 + FINAL_CLUSTER_SHIFT,
    "text-document": RIGHT * 1.0 + DOWN * 1.28 + FINAL_CLUSTER_SHIFT,
    "code-window": RIGHT * 2.32 + DOWN * 1.12 + FINAL_CLUSTER_SHIFT,
}


class SvgRepoVideoLabScene(MovingCameraScene):
    def construct(self) -> None:
        self.camera.background_color = WHITE
        poster_mode = os.environ.get("SPIKE_RENDER_TARGET") == "poster"
        if poster_mode:
            self.add(self.poster_composition())
            return

        stage, rails, source_zone, edit_zone, final_zone, edit_hints = self.stage()
        final_zone.set_opacity(0)
        self.add(stage, rails, source_zone, edit_zone, final_zone, edit_hints)
        self.camera.frame.set(width=11.25)
        self.camera.frame.move_to(LEFT * 2.05 + DOWN * 0.02)

        raw = self.raw_icons()
        raw_group = VGroup(*raw.values())
        for icon in raw.values():
            icon.set_z_index(2)
        self.add(raw_group)
        self.wait(2.75)

        colored = self.colored_icons()
        route = ArcBetweenPoints(LEFT * 2.94 + UP * 1.86, RIGHT * 1.0 + UP * 1.86, angle=-0.14)
        route.set_stroke(PRIMARY_ORANGE, width=7, opacity=0.82)
        scanner = RoundedRectangle(
            width=0.42,
            height=4.05,
            corner_radius=0.14,
            stroke_width=0,
            fill_color=PRIMARY_ORANGE,
            fill_opacity=0.66,
        ).move_to(LEFT * 2.56)
        scanner.set_z_index(5)
        swatches = self.color_swatches()
        self.play(Create(route), FadeIn(scanner), FadeIn(swatches), run_time=1.05)
        self.play(
            scanner.animate.move_to(RIGHT * 1.46),
            source_zone.animate.set_stroke(opacity=0).set_fill(opacity=0),
            final_zone.animate.set_stroke(opacity=0).set_fill(opacity=0),
            edit_hints.animate.set_opacity(0.22),
            self.camera.frame.animate.set(width=11.7).move_to(LEFT * 0.75 + DOWN * 0.02),
            AnimationGroup(
                *[
                    ReplacementTransform(raw[name], colored[name], path_arc=(-0.16 if index % 2 else 0.16))
                    for index, name in enumerate(raw)
                ],
                lag_ratio=0.08,
            ),
            run_time=4.1,
            rate_func=smooth,
        )
        self.wait(0.25)
        self.play(
            FadeOut(scanner),
            FadeOut(route),
            FadeOut(swatches),
            FadeOut(rails),
            FadeOut(edit_hints),
            source_zone.animate.set_stroke(opacity=0).set_fill(opacity=0),
            final_zone.animate.set_stroke(opacity=0).set_fill(opacity=0),
            edit_zone.animate.set_stroke(opacity=0).set_fill(opacity=0),
            self.camera.frame.animate.set(width=11.2).move_to(ORIGIN + DOWN * 0.02),
            run_time=0.7,
            rate_func=smooth,
        )

        raw_label = document_label("RAW", colored["text-document"], color=PRIMARY_BLUE)
        video_label = document_label("VIDEO", colored["text-document"], color=PRIMARY_PURPLE)
        label_pulse = Circle(radius=0.32, stroke_color=PRIMARY_YELLOW, stroke_width=6, fill_opacity=0)
        label_pulse.move_to(raw_label.get_center())
        label_pulse.set_z_index(5)
        self.play(FadeIn(raw_label, scale=0.9), GrowFromCenter(label_pulse), run_time=0.75)
        self.play(
            TransformMatchingShapes(raw_label, video_label),
            FadeOut(label_pulse, scale=1.35),
            run_time=1.45,
            rate_func=smooth,
        )
        self.wait(0.7)

        clamp = self.shape_clamp()
        mid = self.mid_icons(colored)
        mid_label = document_label("VIDEO", mid["text-document"], color=PRIMARY_PURPLE)
        self.play(FadeIn(clamp), run_time=0.55)
        self.play(
            AnimationGroup(
                ReplacementTransform(colored["robot"], mid["robot"], path_arc=-0.18),
                ReplacementTransform(colored["chart"], mid["chart"], path_arc=0.14),
                ReplacementTransform(colored["bulb"], mid["bulb"], path_arc=-0.1),
                ReplacementTransform(colored["text-document"], mid["text-document"], path_arc=0.2),
                ReplacementTransform(colored["code-window"], mid["code-window"], path_arc=-0.12),
                Transform(video_label, mid_label),
                lag_ratio=0.08,
            ),
            run_time=4.55,
            rate_func=smooth,
        )
        rays = self.bulb_rays(mid["bulb"])
        self.play(FadeIn(rays, lag_ratio=0.12), FadeOut(clamp), run_time=0.55)
        self.wait(0.95)
        self.play(FadeOut(rays), run_time=0.35)

        final = self.final_icons()
        final_video_label = document_label("VIDEO", final["text-document"], color=PRIMARY_PURPLE)
        core = self.final_core()
        fan_guides = self.fan_guides()
        self.play(
            FadeOut(source_zone),
            FadeOut(edit_zone),
            FadeIn(fan_guides),
            FadeIn(core, scale=0.9),
            self.camera.frame.animate.set(width=8.65).move_to(RIGHT * 1.03 + UP * 0.06),
            run_time=0.85,
        )
        self.play(
            AnimationGroup(
                ReplacementTransform(mid["robot"], final["robot"], path_arc=0.22),
                ReplacementTransform(mid["chart"], final["chart"], path_arc=-0.2),
                ReplacementTransform(mid["bulb"], final["bulb"], path_arc=0.18),
                ReplacementTransform(mid["text-document"], final["text-document"], path_arc=-0.14),
                ReplacementTransform(mid["code-window"], final["code-window"], path_arc=0.16),
                Transform(video_label, final_video_label),
                lag_ratio=0.1,
            ),
            run_time=3.75,
            rate_func=smooth,
        )
        accent = Circle(radius=0.18, stroke_width=0, fill_color=PRIMARY_YELLOW, fill_opacity=1)
        accent.move_to(core[0].get_center())
        accent.set_z_index(8)
        self.play(FadeIn(accent, scale=0.7), run_time=0.32)
        self.play(
            accent.animate.scale(1.9).set_fill(PRIMARY_ORANGE, opacity=0),
            FadeOut(fan_guides),
            run_time=0.8,
        )
        self.wait(2.4)
        self.remove(accent)

        source_group = VGroup(*final.values(), core, video_label)
        input_panel = self.subproject_input_panel()
        block_skeletons = self.project_block_skeletons()
        self.play(
            source_group.animate.move_to(ORIGIN + DOWN * 0.05),
            self.camera.frame.animate.set(width=13.15).move_to(ORIGIN + DOWN * 0.02),
            run_time=0.9,
            rate_func=smooth,
        )
        self.play(
            FadeIn(input_panel, shift=LEFT * 0.1),
            FadeIn(block_skeletons, shift=RIGHT * 0.1),
            source_group.animate.scale(0.6).move_to(LEFT * 3.82 + DOWN * 0.12),
            run_time=0.75,
            rate_func=smooth,
        )
        self.wait(0.55)

        trunk, top_branch, bottom_branch = self.subproject_guides()
        top_block, top_items = self.project_block(
            "SVG Asset Pipeline",
            PRIMARY_BLUE,
            PRIMARY_YELLOW,
            ("cache source SVGs", "normalize palette variants", "expose editable roles"),
            RIGHT * 2.15 + UP * 1.47,
        )
        bottom_block, bottom_items = self.project_block(
            "Slide Video Layer",
            PRIMARY_PURPLE,
            PRIMARY_GREEN,
            ("render transparent WebM", "stage progressive reveals", "sample review frames"),
            RIGHT * 2.15 + DOWN * 1.47,
        )

        self.play(Create(trunk), run_time=0.45)
        self.play(
            Create(top_branch),
            FadeOut(block_skeletons[0], scale=1.02),
            FadeIn(top_block, shift=UP * 0.04),
            run_time=0.75,
            rate_func=smooth,
        )
        for row in top_items:
            self.play(FadeIn(row, shift=RIGHT * 0.14), run_time=0.52, rate_func=smooth)
            self.wait(0.15)
        self.wait(0.35)
        self.play(
            Create(bottom_branch),
            FadeIn(bottom_block, shift=DOWN * 0.04),
            run_time=0.75,
            rate_func=smooth,
        )
        self.play(FadeOut(block_skeletons[1], scale=1.02), run_time=0.25, rate_func=smooth)
        for row in bottom_items:
            self.play(FadeIn(row, shift=RIGHT * 0.14), run_time=0.52, rate_func=smooth)
            self.wait(0.15)

        output_pulse = Circle(radius=0.16, stroke_width=0, fill_color=PRIMARY_YELLOW, fill_opacity=1)
        output_pulse.move_to(LEFT * 1.32 + DOWN * 0.02)
        output_pulse.set_z_index(8)
        self.play(FadeIn(output_pulse, scale=0.7), run_time=0.25)
        self.play(
            output_pulse.animate.scale(2.4).set_fill(PRIMARY_ORANGE, opacity=0),
            trunk.animate.set_opacity(0.22),
            top_branch.animate.set_opacity(0.22),
            bottom_branch.animate.set_opacity(0.22),
            run_time=0.85,
            rate_func=smooth,
        )
        self.wait(6.1)

    def stage(self) -> tuple[RoundedRectangle, VGroup, RoundedRectangle, RoundedRectangle, RoundedRectangle, VGroup]:
        stage = RoundedRectangle(
            width=12.9,
            height=7.16,
            corner_radius=0.32,
            stroke_width=0,
            fill_color=PAGE_BACKGROUND,
            fill_opacity=0.96,
        )
        stage.set_z_index(-10)
        source_zone = RoundedRectangle(
            width=3.45,
            height=5.65,
            corner_radius=0.28,
            stroke_color=GRAY_200,
            stroke_width=2,
            fill_color=WHITE_HEX,
            fill_opacity=0.72,
        ).move_to(LEFT * 3.95)
        edit_zone = RoundedRectangle(
            width=4.25,
            height=5.65,
            corner_radius=0.28,
            stroke_color=GRAY_300,
            stroke_width=2,
            fill_color=WHITE_HEX,
            fill_opacity=0.5,
        ).move_to(ORIGIN + DOWN * 0.02)
        final_zone = RoundedRectangle(
            width=3.6,
            height=5.65,
            corner_radius=0.28,
            stroke_color=GRAY_200,
            stroke_width=2,
            fill_color=WHITE_HEX,
            fill_opacity=0.68,
        ).move_to(RIGHT * 4.42)
        rails = VGroup(
            DashedLine(LEFT * 2.05 + UP * 2.85, RIGHT * 1.95 + UP * 2.85, dash_length=0.18, color=GRAY_300, stroke_width=3),
        )
        rails.set_z_index(-2)
        for zone in (source_zone, edit_zone, final_zone):
            zone.set_z_index(-3)
        final_zone.set_stroke(opacity=0)
        final_zone.set_fill(opacity=0)
        edit_hints = self.edit_target_hints()
        return stage, rails, source_zone, edit_zone, final_zone, edit_hints

    def edit_target_hints(self) -> VGroup:
        slot_specs = {
            "robot": (0.58, 0.54, PRIMARY_BLUE),
            "chart": (0.7, 0.46, PRIMARY_GREEN),
            "bulb": (0.54, 0.54, PRIMARY_YELLOW),
            "text-document": (0.54, 0.7, PRIMARY_PURPLE),
            "code-window": (0.9, 0.68, PRIMARY_RED),
        }
        hints = VGroup()
        for name, (width, height, color) in slot_specs.items():
            slot = RoundedRectangle(
                width=width,
                height=height,
                corner_radius=0.08,
                stroke_color=GRAY_200,
                stroke_width=1.4,
                fill_color=WHITE_HEX,
                fill_opacity=0.32,
            ).move_to(COLOR_POSITIONS[name])
            accent = RoundedRectangle(
                width=min(width * 0.58, 0.48),
                height=0.06,
                corner_radius=0.03,
                stroke_width=0,
                fill_color=color,
                fill_opacity=0.36,
            ).move_to(slot.get_top() + DOWN * 0.13)
            hints.add(VGroup(slot, accent))
        hints.set_z_index(-1)
        hints.set_opacity(0.72)
        return hints

    def raw_icons(self) -> dict[str, SVGMobject]:
        heights = {"robot": 1.08, "chart": 0.94, "bulb": 0.96, "text-document": 0.96, "code-window": 1.48}
        icons = {name: svg_icon(raw_path(name), heights[name], RAW_POSITIONS[name], opacity=0.42) for name in RAW_POSITIONS}
        for icon in icons.values():
            icon.set_color(GRAY_400)
        return icons

    def colored_icons(self) -> dict[str, SVGMobject]:
        heights = {"robot": 1.16, "chart": 1.0, "bulb": 1.04, "text-document": 1.02, "code-window": 1.58}
        icons = {name: svg_icon(color_path(name), heights[name], COLOR_POSITIONS[name]) for name in COLOR_POSITIONS}
        for icon in icons.values():
            icon.set_z_index(3)
        return icons

    def mid_icons(self, colored: dict[str, SVGMobject]) -> dict[str, SVGMobject]:
        targets = {
            "robot": colored["robot"].copy().stretch(1.26, 0).stretch(0.74, 1).rotate(-6 * PI / 180).move_to(LEFT * 0.05 + UP * 1.34),
            "chart": colored["chart"].copy().stretch(1.62, 1).stretch(0.92, 0).move_to(LEFT * 0.55 + DOWN * 0.08),
            "bulb": colored["bulb"].copy().scale(1.24).rotate(8 * PI / 180).move_to(LEFT * 0.9 + DOWN * 0.48),
            "text-document": colored["text-document"].copy().stretch(1.1, 0).move_to(DOWN * 1.08),
            "code-window": colored["code-window"].copy().stretch(0.84, 0).stretch(1.08, 1).rotate(4 * PI / 180).move_to(RIGHT * 1.5 + DOWN * 0.38),
        }
        for icon in targets.values():
            icon.set_z_index(4)
        return targets

    def final_icons(self) -> dict[str, SVGMobject]:
        heights = {"robot": 1.22, "chart": 1.0, "bulb": 0.98, "text-document": 0.98, "code-window": 1.34}
        final = {name: svg_icon(color_path(name), heights[name], FINAL_POSITIONS[name]) for name in FINAL_POSITIONS}
        final["robot"].rotate(-8 * PI / 180)
        final["chart"].rotate(5 * PI / 180)
        final["bulb"].rotate(10 * PI / 180)
        final["text-document"].rotate(-5 * PI / 180)
        final["code-window"].rotate(7 * PI / 180)
        for icon in final.values():
            icon.set_z_index(5)
        return final

    def color_swatches(self) -> VGroup:
        colors = [PRIMARY_GREEN, PRIMARY_BLUE, PRIMARY_PURPLE, PRIMARY_YELLOW, PRIMARY_RED]
        swatches = VGroup(
            *[
                RoundedRectangle(
                    width=0.32,
                    height=0.32,
                    corner_radius=0.07,
                    stroke_width=0,
                    fill_color=color,
                    fill_opacity=1,
                )
                for color in colors
            ]
        )
        swatches.arrange(RIGHT, buff=0.13)
        swatches.move_to(LEFT * 0.04 + UP * 2.08)
        swatches.set_z_index(6)
        return swatches

    def shape_clamp(self) -> VGroup:
        left_bar = Line(LEFT * 2.35 + UP * 2.08, LEFT * 2.35 + DOWN * 2.08, color=PRIMARY_ORANGE, stroke_width=8)
        right_bar = Line(RIGHT * 2.72 + UP * 2.08, RIGHT * 2.72 + DOWN * 2.08, color=PRIMARY_ORANGE, stroke_width=8)
        brace = RoundedRectangle(
            width=5.38,
            height=4.42,
            corner_radius=0.28,
            stroke_color=PRIMARY_ORANGE,
            stroke_width=4,
            fill_opacity=0,
        ).move_to(RIGHT * 0.18)
        clamp = VGroup(left_bar, right_bar, brace)
        clamp.set_opacity(0.78)
        clamp.set_z_index(1)
        return clamp

    def bulb_rays(self, bulb: SVGMobject) -> VGroup:
        rays = VGroup()
        center = bulb.get_center() + UP * (bulb.height * 0.18)
        for angle in (-70, -35, 0, 35, 70):
            radians = math.radians(angle)
            start = center + (math.sin(radians) * RIGHT + math.cos(radians) * UP) * 0.62
            end = center + (math.sin(radians) * RIGHT + math.cos(radians) * UP) * 0.9
            rays.add(Line(start, end, color=PRIMARY_YELLOW, stroke_width=6))
        rays.set_z_index(3)
        return rays

    def final_core(self) -> VGroup:
        ring = Circle(radius=0.5, stroke_color=PRIMARY_ORANGE, stroke_width=7, fill_color=WHITE_HEX, fill_opacity=1)
        ring.move_to(RIGHT * 1.62 + DOWN * 0.4)
        glyph = Text("SVG", font="Arial", weight=BOLD, color=GRAY)
        glyph.scale_to_fit_width(0.9)
        glyph.move_to(ring.get_center())
        core = VGroup(ring, glyph)
        core.set_z_index(7)
        return core

    def fan_guides(self) -> VGroup:
        center = RIGHT * 1.62 + DOWN * 0.4
        robot_arc = ArcBetweenPoints(
            center + UP * 0.55 + LEFT * 0.16,
            FINAL_POSITIONS["robot"] + DOWN * 0.46 + RIGHT * 0.14,
            angle=-0.32,
        )
        robot_arc.set_stroke(PRIMARY_ORANGE, width=3.4)

        def guide_to(name: str, start_gap: float = 0.5, end_gap: float = 0.46) -> Line:
            target = FINAL_POSITIONS[name]
            direction = target - center
            length = math.sqrt(float(direction[0] ** 2 + direction[1] ** 2))
            unit = direction / length
            return Line(center + unit * start_gap, target - unit * end_gap, color=PRIMARY_ORANGE, stroke_width=3.4)

        guides = VGroup(
            robot_arc,
            guide_to("chart"),
            guide_to("bulb"),
            guide_to("text-document"),
            guide_to("code-window", start_gap=0.58, end_gap=0.5),
        )
        guides.set_opacity(0.34)
        guides.set_z_index(1)
        return guides

    def subproject_input_panel(self) -> VGroup:
        panel = RoundedRectangle(
            width=3.18,
            height=5.65,
            corner_radius=0.28,
            stroke_color=GRAY_200,
            stroke_width=2,
            fill_color=WHITE_HEX,
            fill_opacity=0.74,
        ).move_to(LEFT * 3.82 + DOWN * 0.05)
        marker = RoundedRectangle(
            width=1.62,
            height=0.44,
            corner_radius=0.12,
            stroke_width=0,
            fill_color=PRIMARY_ORANGE,
            fill_opacity=1,
        ).move_to(panel.get_top() + DOWN * 0.42)
        label = Text("resolved input", font="Arial", weight=BOLD, color=WHITE_HEX, font_size=17)
        label.scale_to_fit_width(1.34)
        label.move_to(marker.get_center())
        group = VGroup(panel, marker, label)
        group.set_z_index(-1)
        marker.set_z_index(1)
        label.set_z_index(1)
        return group

    def subproject_guides(self) -> VGroup:
        start = LEFT * 2.22 + DOWN * 0.02
        fork = LEFT * 1.32 + DOWN * 0.02
        top = LEFT * 0.72 + UP * 1.47
        bottom = LEFT * 0.72 + DOWN * 1.47
        trunk = Line(start, fork, color=PRIMARY_ORANGE, stroke_width=7)
        top_branch = ArcBetweenPoints(fork, top, angle=0.24)
        bottom_branch = ArcBetweenPoints(fork, bottom, angle=-0.24)
        for branch in (top_branch, bottom_branch):
            branch.set_stroke(PRIMARY_ORANGE, width=7, opacity=0.78)
        trunk.set_stroke(PRIMARY_ORANGE, width=7, opacity=0.78)
        guides = VGroup(trunk, top_branch, bottom_branch)
        guides.set_z_index(1)
        return guides

    def project_block_skeletons(self) -> VGroup:
        skeletons = VGroup()
        for index, center in enumerate((RIGHT * 2.15 + UP * 1.47, RIGHT * 2.15 + DOWN * 1.47)):
            panel = RoundedRectangle(
                width=5.28,
                height=2.34,
                corner_radius=0.18,
                stroke_color=GRAY_200,
                stroke_width=2,
                fill_color=WHITE_HEX,
                fill_opacity=0.68,
            ).move_to(center)
            header_hint = RoundedRectangle(
                width=4.82,
                height=0.26,
                corner_radius=0.09,
                stroke_width=0,
                fill_color=PRIMARY_BLUE if index == 0 else PRIMARY_PURPLE,
                fill_opacity=0.54,
            ).move_to(panel.get_top() + DOWN * 0.36)
            row_hint = RoundedRectangle(
                width=4.54,
                height=0.1,
                corner_radius=0.05,
                stroke_width=0,
                fill_color=PRIMARY_YELLOW if index == 0 else PRIMARY_GREEN,
                fill_opacity=0.46,
            ).move_to(center + DOWN * 0.06)
            footer_hint = RoundedRectangle(
                width=4.54,
                height=0.12,
                corner_radius=0.06,
                stroke_width=0,
                fill_color=PRIMARY_BLUE if index == 0 else PRIMARY_PURPLE,
                fill_opacity=0.78,
            ).move_to(panel.get_bottom() + UP * 0.34)
            skeletons.add(VGroup(panel, header_hint, row_hint, footer_hint))
        skeletons.set_z_index(2)
        return skeletons

    def project_block(
        self,
        title: str,
        header_color: str,
        bullet_color: str,
        items: tuple[str, ...],
        center,
    ) -> tuple[VGroup, list[VGroup]]:
        panel = RoundedRectangle(
            width=5.28,
            height=2.34,
            corner_radius=0.18,
            stroke_color=GRAY_200,
            stroke_width=2,
            fill_color=WHITE_HEX,
            fill_opacity=0.95,
        ).move_to(center)
        header = RoundedRectangle(
            width=4.82,
            height=0.54,
            corner_radius=0.13,
            stroke_width=0,
            fill_color=header_color,
            fill_opacity=1,
        ).move_to(panel.get_top() + DOWN * 0.36)
        title_text = Text(title, font="Arial", weight=BOLD, color=WHITE_HEX, font_size=26)
        if title_text.width > 4.28:
            title_text.scale_to_fit_width(4.28)
        title_text.move_to(header.get_center())
        body_anchor = RoundedRectangle(
            width=4.54,
            height=0.07,
            corner_radius=0.035,
            stroke_width=0,
            fill_color=bullet_color,
            fill_opacity=0.45,
        ).move_to(panel.get_bottom() + UP * 0.34)

        rows: list[VGroup] = []
        first_y = panel.get_top()[1] - 0.98
        for index, item in enumerate(items):
            dot = Circle(radius=0.055, stroke_width=0, fill_color=bullet_color, fill_opacity=1)
            line = Text(item, font="Arial", color=GRAY, font_size=22)
            if line.width > 4.2:
                line.scale_to_fit_width(4.2)
            row = VGroup(dot, line).arrange(RIGHT, buff=0.16)
            row.move_to([panel.get_left()[0] + 2.48, first_y - index * 0.42, 0])
            row.align_to(panel, LEFT).shift(RIGHT * 0.42)
            row.set_z_index(6)
            rows.append(row)

        block = VGroup(panel, header, title_text, body_anchor)
        block.set_z_index(4)
        return block, rows

    def continuation_poster_composition(self) -> VGroup:
        stage, _, _, _, _, _ = self.stage()
        final = self.final_icons()
        core = self.final_core()
        label = document_label("VIDEO", final["text-document"], color=PRIMARY_PURPLE)
        input_group = VGroup(*final.values(), core, label).scale(0.6).move_to(LEFT * 3.82 + DOWN * 0.12)
        input_panel = self.subproject_input_panel()
        guides = self.subproject_guides()
        guides.set_opacity(0.22)
        top_block, top_items = self.project_block(
            "SVG Asset Pipeline",
            PRIMARY_BLUE,
            PRIMARY_YELLOW,
            ("cache source SVGs", "normalize palette variants", "expose editable roles"),
            RIGHT * 2.15 + UP * 1.47,
        )
        bottom_block, bottom_items = self.project_block(
            "Slide Video Layer",
            PRIMARY_PURPLE,
            PRIMARY_GREEN,
            ("render transparent WebM", "stage progressive reveals", "sample review frames"),
            RIGHT * 2.15 + DOWN * 1.47,
        )
        return VGroup(stage, input_panel, input_group, guides, top_block, *top_items, bottom_block, *bottom_items)

    def poster_composition(self) -> VGroup:
        return self.continuation_poster_composition()


def render_variant(args: _Args) -> None:
    ensure_raw_assets(refresh=args.refresh_assets)
    ensure_generated_variants()

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
