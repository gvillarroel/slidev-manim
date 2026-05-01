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
import re
import shutil
import subprocess
import sys
import xml.etree.ElementTree as ET
from dataclasses import dataclass
from pathlib import Path

import numpy as np
from manim import (
    DOWN,
    ORIGIN,
    UP,
    AnimationGroup,
    Circle,
    Create,
    FadeIn,
    FadeOut,
    Line,
    MoveAlongPath,
    Rectangle,
    Scene,
    SVGMobject,
    SurroundingRectangle,
    Text,
    VGroup,
    linear,
    smooth,
)

SPIKE_DIR = Path(__file__).resolve().parent
REPO_ROOT = SPIKE_DIR.parent.parent
SPIKE_NAME = SPIKE_DIR.name
OUTPUT_DIR = REPO_ROOT / "videos" / SPIKE_NAME
STAGING_DIR = OUTPUT_DIR / ".manim"
GENERATED_DIR = OUTPUT_DIR / ".generated"

MERMAID_PACKAGE = "@mermaid-js/mermaid-cli@10.9.1"
SVG_NS = "http://www.w3.org/2000/svg"
SVG_NS_MAP = {"svg": SVG_NS}

PRIMARY_RED = "#9e1b32"
PRIMARY_ORANGE = "#e77204"
WHITE = "#ffffff"
GRAY = "#333e48"
GRAY_100 = "#e7e7e7"
GRAY_200 = "#cfcfcf"
PAGE_BACKGROUND = "#f7f7f7"
TEXT_FONT = "Arial"


@dataclass(frozen=True)
class LabelSpec:
    key: str
    text: str
    center: tuple[float, float]
    width: float
    height: float
    color: str


class _Args(argparse.Namespace):
    quality: str


def parse_args() -> _Args:
    parser = argparse.ArgumentParser(description="Render the mermaid-svg-direct-insert spike.")
    parser.add_argument("--quality", choices=("low", "medium", "high", "production", "4k"), default="medium")
    return parser.parse_args(namespace=_Args())


def quality_flag(quality: str) -> str:
    return {"low": "-ql", "medium": "-qm", "high": "-qh", "production": "-qp", "4k": "-qk"}[quality]


def output_paths() -> tuple[Path, Path]:
    return OUTPUT_DIR / f"{SPIKE_NAME}.webm", OUTPUT_DIR / f"{SPIKE_NAME}.png"


def render_command(args: _Args, stem: str, *, poster: bool) -> list[str]:
    STAGING_DIR.mkdir(parents=True, exist_ok=True)
    command = [
        sys.executable,
        "-m",
        "manim",
        "render",
        quality_flag(args.quality),
        "-r",
        "1600,900",
        "-o",
        stem,
        "--media_dir",
        str(STAGING_DIR),
    ]
    if poster:
        command.append("-s")
    else:
        command.extend(["--format", "webm", "-t"])
    command.extend([str(Path(__file__).resolve()), "MermaidSvgDirectInsertScene"])
    return command


def promote(target_name: str, destination: Path) -> None:
    matches = sorted(STAGING_DIR.glob(f"**/{target_name}"), key=lambda path: path.stat().st_mtime)
    if not matches:
        raise FileNotFoundError(f"Could not find {target_name} under {STAGING_DIR}")
    destination.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(matches[-1], destination)


def mermaid_command(input_path: Path, output_path: Path) -> list[str]:
    command = [
        "npx",
        "-y",
        "-p",
        MERMAID_PACKAGE,
        "mmdc",
        "-i",
        str(input_path),
        "-o",
        str(output_path),
        "-b",
        "transparent",
    ]
    if os.name == "nt":
        return ["cmd", "/c", *command]
    return command


def ensure_mermaid_svg() -> tuple[Path, Path]:
    GENERATED_DIR.mkdir(parents=True, exist_ok=True)
    source_mmd = SPIKE_DIR / "diagram.mmd"
    raw_svg = GENERATED_DIR / "diagram.svg"
    visible_svg = GENERATED_DIR / "diagram-visible-for-manim.svg"

    subprocess.run(mermaid_command(source_mmd, raw_svg), check=True, cwd=str(REPO_ROOT))
    write_visible_svg_for_manim(raw_svg, visible_svg)
    return raw_svg, visible_svg


def tag_name(element: ET.Element) -> str:
    return element.tag.rsplit("}", 1)[-1]


def class_tokens(element: ET.Element) -> set[str]:
    return set(element.attrib.get("class", "").split())


def prune_non_visible_svg_support(element: ET.Element) -> None:
    for child in list(element):
        tokens = class_tokens(child)
        child_tag = tag_name(child)
        if "label" in tokens or "edgeLabels" in tokens or child_tag in {"defs", "marker", "text", "foreignObject"}:
            element.remove(child)
            continue
        prune_non_visible_svg_support(child)


def parse_view_box(raw_value: str | None) -> tuple[float, float, float, float]:
    if not raw_value:
        return (0.0, 0.0, 1.0, 1.0)
    values = [float(part) for part in raw_value.split()]
    if len(values) != 4:
        raise ValueError(f"Unexpected SVG viewBox: {raw_value!r}")
    return (values[0], values[1], values[2], values[3])


def write_visible_svg_for_manim(raw_svg: Path, visible_svg: Path) -> None:
    tree = ET.parse(raw_svg)
    root = tree.getroot()
    view_box = root.attrib.get("viewBox", "0 0 1 1")
    min_x, min_y, width, height = parse_view_box(view_box)

    root_group = root.find(".//svg:g[@class='root']", SVG_NS_MAP)
    if root_group is None:
        raise ValueError(f"Could not find Mermaid root group in {raw_svg}")

    ET.register_namespace("", SVG_NS)
    out_root = ET.Element(
        f"{{{SVG_NS}}}svg",
        {
            "viewBox": view_box,
            "width": root.attrib.get("width", "100%"),
            "height": root.attrib.get("height", "100%"),
        },
    )
    # Keep Manim's imported bounds aligned to Mermaid's viewBox.
    ET.SubElement(
        out_root,
        f"{{{SVG_NS}}}rect",
        {
            "x": str(min_x),
            "y": str(min_y),
            "width": str(width),
            "height": str(height),
            "style": "fill:#ffffff;fill-opacity:0.001;stroke:none;",
        },
    )
    visible_group = copy.deepcopy(root_group)
    prune_non_visible_svg_support(visible_group)
    out_root.append(visible_group)
    ET.ElementTree(out_root).write(visible_svg, encoding="utf-8", xml_declaration=False)


def parse_translate(transform: str | None) -> tuple[float, float]:
    if not transform:
        return (0.0, 0.0)
    match = re.search(r"translate\(\s*([-\d.]+)[,\s]+([-\d.]+)\s*\)", transform)
    if not match:
        return (0.0, 0.0)
    return (float(match.group(1)), float(match.group(2)))


def style_value(style: str, name: str, fallback: str) -> str:
    match = re.search(rf"{re.escape(name)}\s*:\s*([^;]+)", style)
    return match.group(1).strip() if match else fallback


def node_label(group: ET.Element) -> str:
    spans = group.findall(".//svg:tspan", SVG_NS_MAP)
    text = " ".join("".join(span.itertext()).strip() for span in spans if "".join(span.itertext()).strip())
    return text or group.attrib.get("data-id", "")


def node_size(group: ET.Element) -> tuple[float, float]:
    rect = group.find(".//svg:rect[@class='basic label-container']", SVG_NS_MAP)
    if rect is None:
        return (120.0, 40.0)
    return (float(rect.attrib.get("width", "120")), float(rect.attrib.get("height", "40")))


def node_text_color(group: ET.Element) -> str:
    text = group.find(".//svg:text", SVG_NS_MAP)
    if text is None:
        return WHITE
    return style_value(text.attrib.get("style", ""), "fill", WHITE)


def extract_label_specs(raw_svg: Path) -> list[LabelSpec]:
    root = ET.parse(raw_svg).getroot()
    specs: list[LabelSpec] = []
    for group in root.findall(".//svg:g[@data-node='true']", SVG_NS_MAP):
        key = group.attrib.get("data-id", node_label(group))
        width, height = node_size(group)
        specs.append(
            LabelSpec(
                key=key,
                text=node_label(group),
                center=parse_translate(group.attrib.get("transform")),
                width=width,
                height=height,
                color=node_text_color(group),
            )
        )
    return specs


def svg_point_to_manim(
    point: tuple[float, float],
    view_box: tuple[float, float, float, float],
    body: SVGMobject,
) -> np.ndarray:
    min_x, min_y, width, height = view_box
    center_x = min_x + width / 2
    center_y = min_y + height / 2
    scale_x = body.width / width
    scale_y = body.height / height
    return np.array([(point[0] - center_x) * scale_x, -(point[1] - center_y) * scale_y, 0.0])


def fitted_label(spec: LabelSpec, view_box: tuple[float, float, float, float], body: SVGMobject) -> Text:
    label = Text(spec.text, font=TEXT_FONT, font_size=25, color=spec.color)
    max_width = spec.width * (body.width / view_box[2]) * 0.78
    max_height = spec.height * (body.height / view_box[3]) * 0.46
    if label.width > max_width:
        label.scale_to_fit_width(max_width)
    if label.height > max_height:
        label.scale_to_fit_height(max_height)
    label.move_to(svg_point_to_manim(spec.center, view_box, body))
    label.set_z_index(4)
    return label


def build_imported_mermaid_diagram() -> tuple[VGroup, dict[str, np.ndarray], SVGMobject]:
    raw_svg, visible_svg = ensure_mermaid_svg()
    view_box = parse_view_box(ET.parse(raw_svg).getroot().attrib.get("viewBox"))
    body = SVGMobject(str(visible_svg), height=5.05)
    body.set_z_index(2)

    labels = VGroup()
    anchors: dict[str, np.ndarray] = {}
    for spec in extract_label_specs(raw_svg):
        local_point = svg_point_to_manim(spec.center, view_box, body)
        anchors[spec.key] = local_point
        labels.add(fitted_label(spec, view_box, body))

    diagram = VGroup(body, labels)
    diagram.move_to(ORIGIN)
    return diagram, anchors, body


def stage() -> VGroup:
    backing = Rectangle(
        width=11.6,
        height=6.55,
        stroke_color=GRAY_200,
        stroke_width=2,
        fill_color=PAGE_BACKGROUND,
        fill_opacity=1,
    )
    inner = Rectangle(
        width=4.3,
        height=5.72,
        stroke_color=GRAY_200,
        stroke_width=1.5,
        fill_color=WHITE,
        fill_opacity=1,
    )
    return VGroup(backing, inner)


def arrival_halo(center: np.ndarray) -> Circle:
    halo = Circle(radius=0.22, stroke_color=PRIMARY_RED, stroke_width=4, fill_color=PRIMARY_RED, fill_opacity=0.10)
    halo.move_to(center)
    halo.set_z_index(8)
    return halo


class MermaidSvgDirectInsertScene(Scene):
    def construct(self) -> None:
        self.camera.background_color = WHITE
        poster_mode = os.environ.get("SPIKE_RENDER_TARGET") == "poster"

        imported_diagram, anchors, body = build_imported_mermaid_diagram()
        scene_stage = stage()
        imported_diagram.move_to(scene_stage[1].get_center())

        title = Text("Mermaid SVG imported by Manim", font=TEXT_FONT, font_size=28, color=GRAY)
        title.next_to(scene_stage[1], UP, buff=0.24)

        outline = SurroundingRectangle(imported_diagram, color=PRIMARY_RED, stroke_width=4, buff=0.18)
        outline.set_z_index(7)

        if poster_mode:
            self.add(scene_stage, imported_diagram, title, outline)
            return

        self.add(scene_stage, imported_diagram, title)
        self.wait(2.8)

        self.play(Create(outline), run_time=0.9, rate_func=smooth)
        self.wait(1.2)

        body_center = body.get_center()
        ordered_keys = ["mmd", "cli", "svg", "manim"]
        centers = {key: body_center + anchors[key] for key in ordered_keys}

        pulse = Circle(radius=0.085, stroke_width=0, fill_color=PRIMARY_RED, fill_opacity=1)
        pulse.move_to(centers["mmd"])
        pulse.set_z_index(9)
        self.play(FadeIn(pulse, scale=0.65), run_time=0.35)

        for start_key, end_key in zip(ordered_keys, ordered_keys[1:]):
            path = Line(centers[start_key], centers[end_key])
            path.set_opacity(0)
            halo = arrival_halo(centers[end_key])
            self.play(MoveAlongPath(pulse, path), run_time=2.25, rate_func=linear)
            self.play(FadeIn(halo, scale=0.6), run_time=0.26, rate_func=smooth)
            self.play(FadeOut(halo, scale=1.45), run_time=0.34, rate_func=smooth)
            self.wait(0.25)

        self.play(
            AnimationGroup(
                imported_diagram.animate.scale(1.035),
                outline.animate.scale(1.035),
                lag_ratio=0.0,
            ),
            run_time=1.25,
            rate_func=smooth,
        )
        self.play(FadeOut(pulse, scale=1.4), run_time=0.45)
        self.wait(1.4)
        self.play(outline.animate.set_stroke(width=2.5, opacity=0.55), run_time=0.65, rate_func=smooth)
        self.wait(7.0)


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
