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
from dataclasses import dataclass
from pathlib import Path

from manim import (
    DOWN,
    LEFT,
    ORIGIN,
    RIGHT,
    UP,
    AnimationGroup,
    ArcBetweenPoints,
    Arrow,
    Circle,
    CurvedArrow,
    FadeIn,
    FadeOut,
    MoveAlongPath,
    Rectangle,
    Scene,
    SVGMobject,
    Text,
    Transform,
    VGroup,
    smooth,
)

SPIKE_DIR = Path(__file__).resolve().parent
REPO_ROOT = SPIKE_DIR.parent.parent
SPIKE_NAME = SPIKE_DIR.name
OUTPUT_DIR = REPO_ROOT / "videos" / SPIKE_NAME
STAGING_DIR = OUTPUT_DIR / ".manim"
GENERATED_DIR = OUTPUT_DIR / ".generated"

PRIMARY_ORANGE = "#e77204"
PRIMARY_YELLOW = "#f1c319"
PRIMARY_GREEN = "#45842a"
PRIMARY_BLUE = "#007298"
PRIMARY_PURPLE = "#652f6c"
PRIMARY_RED = "#9e1b32"
WHITE = "#ffffff"
GRAY = "#333e48"
GRAY_100 = "#e7e7e7"
GRAY_200 = "#cfcfcf"
PAGE_BACKGROUND = "#f7f7f7"

SVG_NS = "http://www.w3.org/2000/svg"
SVG_NS_MAP = {"svg": SVG_NS, "xhtml": "http://www.w3.org/1999/xhtml"}
VIEW_BOX = "0 0 1000 560"

MERMAID_DIAGRAM = f"""%%{{init: {{"theme":"base","themeVariables":{{"fontFamily":"Open Sans, Arial, sans-serif","primaryColor":"{PRIMARY_GREEN}","primaryTextColor":"{WHITE}","primaryBorderColor":"{PRIMARY_GREEN}","lineColor":"{PRIMARY_ORANGE}","textColor":"{WHITE}"}}}}}}%%
flowchart LR
    spec(Spec) --> svg(SVG)
    svg --> video(Video)

    classDef specNode fill:{PRIMARY_GREEN},stroke:{PRIMARY_GREEN},color:{WHITE};
    classDef svgNode fill:{PRIMARY_BLUE},stroke:{PRIMARY_BLUE},color:{WHITE};
    classDef videoNode fill:{PRIMARY_PURPLE},stroke:{PRIMARY_PURPLE},color:{WHITE};
    class spec specNode;
    class svg svgNode;
    class video videoNode;
"""

ROLE_BY_LABEL = {"Spec": "node_spec", "SVG": "node_svg", "Video": "node_video"}
ROLE_COLORS = {"node_spec": PRIMARY_GREEN, "node_svg": PRIMARY_BLUE, "node_video": PRIMARY_PURPLE}


@dataclass(frozen=True)
class RolePlacement:
    width: float
    position: object


class _Args(argparse.Namespace):
    quality: str


ROLE_PLACEMENTS: dict[str, dict[str, RolePlacement]] = {
    "source": {
        "node_spec": RolePlacement(2.32, LEFT * 4.0 + DOWN * 0.12),
        "node_svg": RolePlacement(2.32, ORIGIN + DOWN * 0.12),
        "node_video": RolePlacement(2.32, RIGHT * 4.0 + DOWN * 0.12),
        "edge_spec_svg": RolePlacement(1.56, LEFT * 2.0 + DOWN * 0.12),
        "edge_svg_video": RolePlacement(1.56, RIGHT * 2.0 + DOWN * 0.12),
    },
    "target": {
        "node_spec": RolePlacement(2.32, LEFT * 3.25 + DOWN * 1.48),
        "node_svg": RolePlacement(2.32, UP * 1.58),
        "node_video": RolePlacement(2.32, RIGHT * 3.25 + DOWN * 1.48),
        "edge_spec_svg": RolePlacement(3.0, LEFT * 1.58 + UP * 0.12),
        "edge_svg_video": RolePlacement(3.0, RIGHT * 1.58 + UP * 0.12),
    },
}

ROLE_Z_INDEX = {
    "edge_spec_svg": 1,
    "edge_svg_video": 1,
    "node_spec": 3,
    "node_svg": 3,
    "node_video": 3,
}

LABELS = {
    "node_spec": ("Spec", PRIMARY_GREEN),
    "node_svg": ("SVG", PRIMARY_BLUE),
    "node_video": ("Video", PRIMARY_PURPLE),
}

SPLIT_SHIFT = {
    "node_spec": LEFT * 0.14 + UP * 0.2,
    "node_svg": UP * 0.28,
    "node_video": RIGHT * 0.14 + UP * 0.2,
    "edge_spec_svg": LEFT * 0.08 + DOWN * 0.18,
    "edge_svg_video": RIGHT * 0.08 + DOWN * 0.18,
}


def parse_args() -> _Args:
    parser = argparse.ArgumentParser(description="Render the diagram-svg-video-manipulation spike.")
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
        "-o",
        stem,
        "--media_dir",
        str(STAGING_DIR),
    ]
    command.append("-s" if poster else "--format=webm")
    if not poster:
        command.append("-t")
    command.extend([str(Path(__file__).resolve()), "DiagramSvgVideoManipulationScene"])
    return command


def promote(target_name: str, destination: Path) -> None:
    matches = sorted(STAGING_DIR.glob(f"**/{target_name}"), key=lambda path: path.stat().st_mtime)
    if not matches:
        raise FileNotFoundError(target_name)
    destination.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(matches[-1], destination)


def find_group_by_id(root: ET.Element, role: str) -> ET.Element:
    for element in root.iter():
        if element.attrib.get("id") == role:
            return element
    raise ValueError(f"Could not find SVG role {role!r}")


def write_role_fragment(stage: str, role: str, source_svg: Path) -> Path:
    source_root = ET.parse(source_svg).getroot()
    role_group = copy.deepcopy(find_group_by_id(source_root, role))
    out_root = ET.Element(
        f"{{{SVG_NS}}}svg",
        {
            "xmlns": SVG_NS,
            "viewBox": source_root.attrib.get("viewBox", VIEW_BOX),
            "width": "1000",
            "height": "560",
        },
    )
    out_root.append(role_group)

    destination = GENERATED_DIR / "fragments" / stage / f"{role}.svg"
    destination.parent.mkdir(parents=True, exist_ok=True)
    ET.ElementTree(out_root).write(destination, encoding="utf-8", xml_declaration=False)
    return destination


def ensure_mermaid_svg(workdir: Path) -> Path:
    workdir.mkdir(parents=True, exist_ok=True)
    source_mmd = workdir / "diagram.mmd"
    source_svg = workdir / "diagram.svg"
    normalized_svg = workdir / "diagram-normalized.svg"

    source_mmd.write_text(MERMAID_DIAGRAM, encoding="utf-8")
    subprocess.run(
        [
            "cmd",
            "/c",
            "npx",
            "-y",
            "-p",
            "@mermaid-js/mermaid-cli",
            "mmdc",
            "-i",
            str(source_mmd),
            "-o",
            str(source_svg),
            "-b",
            "transparent",
        ],
        check=True,
        cwd=str(REPO_ROOT),
    )
    normalize_mermaid_svg(source_svg, normalized_svg)
    return normalized_svg


def extract_mermaid_label(group: ET.Element) -> str:
    paragraphs = group.findall(".//xhtml:p", SVG_NS_MAP)
    if paragraphs:
        return " ".join((p.text or "").strip() for p in paragraphs if (p.text or "").strip())

    spans = group.findall(".//xhtml:span", SVG_NS_MAP)
    if spans:
        return " ".join("".join(span.itertext()).strip() for span in spans if "".join(span.itertext()).strip())

    return group.attrib.get("id", "")


def remove_mermaid_labels(element: ET.Element) -> None:
    for child in list(element):
        css_classes = set(child.attrib.get("class", "").split())
        if child.tag.endswith("foreignObject") or css_classes.intersection({"label", "nodeLabel", "edgeLabel"}):
            element.remove(child)
        else:
            remove_mermaid_labels(child)


def paint_mermaid_node(element: ET.Element, color: str) -> None:
    for child in element.iter():
        tag_name = child.tag.rsplit("}", 1)[-1]
        if tag_name in {"rect", "path", "circle", "ellipse", "polygon"}:
            child.attrib["fill"] = color
            child.attrib["stroke"] = color
            child.attrib["stroke-width"] = "0"
        if tag_name == "rect":
            child.attrib.setdefault("rx", "12")
            child.attrib.setdefault("ry", "12")


def normalize_mermaid_svg(source_svg: Path, destination: Path) -> None:
    tree = ET.parse(source_svg)
    root = tree.getroot()
    out_root = ET.Element(
        f"{{{SVG_NS}}}svg",
        {
            "xmlns": SVG_NS,
            "xmlns:xlink": "http://www.w3.org/1999/xlink",
            "viewBox": root.attrib.get("viewBox", VIEW_BOX),
            "width": root.attrib.get("width", "100%"),
        },
    )

    style = root.find("svg:style", SVG_NS_MAP)
    if style is not None:
        out_root.append(copy.deepcopy(style))

    nodes_parent = root.find(".//svg:g[@class='nodes']", SVG_NS_MAP)
    if nodes_parent is None:
        raise ValueError(f"Could not find Mermaid nodes in {source_svg}")

    for node_group in nodes_parent:
        label = extract_mermaid_label(node_group)
        role = ROLE_BY_LABEL.get(label)
        if role is None:
            continue

        normalized = copy.deepcopy(node_group)
        normalized.attrib["id"] = role
        normalized.attrib["data-role"] = "mermaid-node"
        normalized.attrib["data-label"] = label
        remove_mermaid_labels(normalized)
        paint_mermaid_node(normalized, ROLE_COLORS[role])
        out_root.append(normalized)

    destination.parent.mkdir(parents=True, exist_ok=True)
    ET.ElementTree(out_root).write(destination, encoding="utf-8", xml_declaration=False)


def ensure_generated_svgs() -> dict[str, Path]:
    for stale_dir in (GENERATED_DIR / "diagrams", GENERATED_DIR / "fragments"):
        if stale_dir.exists():
            shutil.rmtree(stale_dir)
    mermaid_svg = ensure_mermaid_svg(GENERATED_DIR / "mermaid")
    return {"source": mermaid_svg, "target": mermaid_svg}


def strip_fragment_text_artifacts(mobject: SVGMobject) -> SVGMobject:
    # Mermaid nodes are imported only for their geometry; labels are native Manim text.
    return mobject


def load_svg_role(stage: str, role: str, source_svg: Path) -> SVGMobject:
    placement = ROLE_PLACEMENTS[stage][role]
    fragment_path = write_role_fragment(stage, role, source_svg)
    mobject = SVGMobject(str(fragment_path))
    if role.startswith("node_"):
        mobject.stretch_to_fit_width(placement.width)
        mobject.stretch_to_fit_height(0.98)
    else:
        mobject.scale_to_fit_width(placement.width)
    mobject.move_to(placement.position)
    mobject.set_z_index(ROLE_Z_INDEX[role])
    return mobject


def build_node(stage: str, role: str, source_svg: Path) -> VGroup:
    shape = load_svg_role(stage, role, source_svg)
    label, color = LABELS[role]
    shape.set_fill(color, opacity=1)
    shape.set_stroke(color, width=0)
    text = Text(label, font_size=26, color=WHITE)
    text.move_to(shape.get_center())
    text.set_z_index(ROLE_Z_INDEX[role] + 1)
    return VGroup(shape, text)


def placement_center(stage: str, role: str):
    return ROLE_PLACEMENTS[stage][role].position


def build_straight_arrow(start, end) -> Arrow:
    return Arrow(
        start=start,
        end=end,
        buff=0.08,
        stroke_width=3.4,
        max_tip_length_to_length_ratio=0.085,
        max_stroke_width_to_length_ratio=14,
        color=PRIMARY_ORANGE,
    )


def build_curved_arrow(start, end, angle: float) -> CurvedArrow:
    return CurvedArrow(
        start,
        end,
        angle=angle,
        stroke_width=3.4,
        tip_length=0.1,
        color=PRIMARY_ORANGE,
    )


def build_edge(stage: str, role: str, _source_svg: Path) -> Arrow | CurvedArrow:
    spec = placement_center(stage, "node_spec")
    svg = placement_center(stage, "node_svg")
    video = placement_center(stage, "node_video")

    if stage == "source":
        if role == "edge_spec_svg":
            edge = build_straight_arrow(spec + RIGHT * 1.34, svg + LEFT * 1.34)
        else:
            edge = build_straight_arrow(svg + RIGHT * 1.34, video + LEFT * 1.34)
    elif role == "edge_spec_svg":
        edge = build_curved_arrow(spec + UP * 0.72 + RIGHT * 1.0, svg + DOWN * 0.72 + LEFT * 0.86, angle=-0.18)
    else:
        edge = build_curved_arrow(svg + DOWN * 0.72 + RIGHT * 0.86, video + UP * 0.72 + LEFT * 1.0, angle=-0.18)

    edge.set_z_index(ROLE_Z_INDEX[role])
    edge.set_opacity(0.9)
    return edge


def build_stage_parts(stage: str, svg_paths: dict[str, Path]) -> dict[str, VGroup | SVGMobject]:
    return {
        "edge_spec_svg": build_edge(stage, "edge_spec_svg", svg_paths[stage]),
        "edge_svg_video": build_edge(stage, "edge_svg_video", svg_paths[stage]),
        "node_spec": build_node(stage, "node_spec", svg_paths[stage]),
        "node_svg": build_node(stage, "node_svg", svg_paths[stage]),
        "node_video": build_node(stage, "node_video", svg_paths[stage]),
    }


def ordered_parts(parts: dict[str, VGroup | SVGMobject]) -> VGroup:
    return VGroup(
        parts["edge_spec_svg"],
        parts["edge_svg_video"],
        parts["node_spec"],
        parts["node_svg"],
        parts["node_video"],
    )


def stage_panel() -> VGroup:
    backing = Rectangle(
        width=11.8,
        height=5.35,
        stroke_color=GRAY_200,
        stroke_width=2,
        fill_color=PAGE_BACKGROUND,
        fill_opacity=0.96,
    )
    source_lane = Rectangle(
        width=10.6,
        height=1.32,
        stroke_color=GRAY_200,
        stroke_width=1.5,
        fill_color=GRAY_100,
        fill_opacity=0.28,
    ).move_to(DOWN * 0.12)
    return VGroup(backing, source_lane)


def target_slots() -> VGroup:
    slots = VGroup()
    for role in ("node_spec", "node_svg", "node_video"):
        slot = Rectangle(
            width=ROLE_PLACEMENTS["target"][role].width + 0.26,
            height=1.16,
            stroke_color=GRAY_200,
            stroke_width=1.4,
            fill_color=WHITE,
            fill_opacity=0.14,
        ).move_to(placement_center("target", role))
        slot.set_z_index(0)
        slots.add(slot)
    return slots


def terminal_outline_for(node: VGroup | SVGMobject) -> Rectangle:
    outline = Rectangle(
        width=node.width + 0.72,
        height=node.height + 0.52,
        stroke_color=PRIMARY_RED,
        stroke_width=3.6,
        fill_opacity=0,
    ).move_to(node.get_center())
    outline.set_z_index(7)
    return outline


def handle_for(role: str, part: VGroup | SVGMobject) -> Circle:
    handle = Circle(radius=0.105, stroke_width=0, fill_color=PRIMARY_RED, fill_opacity=1)
    if role.startswith("node_"):
        handle.move_to(part.get_corner(UP + RIGHT) + LEFT * 0.24 + DOWN * 0.18)
    else:
        handle.move_to(part.get_center() + UP * 0.1)
    handle.set_z_index(8)
    return handle


def pulse_path(start: object, end: object) -> ArcBetweenPoints:
    return ArcBetweenPoints(start, end, angle=-0.22, stroke_width=0)


class DiagramSvgVideoManipulationScene(Scene):
    def construct(self) -> None:
        self.camera.background_color = PAGE_BACKGROUND
        poster_mode = os.environ.get("SPIKE_RENDER_TARGET") == "poster"

        svg_paths = ensure_generated_svgs()
        source_parts = build_stage_parts("source", svg_paths)
        target_parts = build_stage_parts("target", svg_paths)

        panel = stage_panel()
        if poster_mode:
            self.add(panel[0], ordered_parts(target_parts), terminal_outline_for(target_parts["node_video"]))
            return

        self.add(panel, ordered_parts(source_parts))
        self.wait(2.6)

        handles = {role: handle_for(role, part) for role, part in source_parts.items()}
        self.play(FadeIn(VGroup(*handles.values()), scale=0.7), run_time=0.75)
        self.play(
            AnimationGroup(
                *[
                    source_parts[role].animate.shift(SPLIT_SHIFT[role])
                    for role in ("node_spec", "edge_spec_svg", "node_svg", "edge_svg_video", "node_video")
                ],
                *[
                    handles[role].animate.shift(SPLIT_SHIFT[role])
                    for role in ("node_spec", "edge_spec_svg", "node_svg", "edge_svg_video", "node_video")
                ],
                lag_ratio=0.06,
            ),
            run_time=2.1,
            rate_func=smooth,
        )
        self.wait(1.1)

        target_hint = target_slots()

        self.play(
            FadeIn(target_hint),
            FadeOut(panel[1]),
            FadeOut(VGroup(*handles.values()), scale=0.75),
            run_time=0.7,
        )
        self.play(
            AnimationGroup(
                Transform(source_parts["edge_spec_svg"], target_parts["edge_spec_svg"], path_arc=-0.18),
                Transform(source_parts["edge_svg_video"], target_parts["edge_svg_video"], path_arc=0.18),
                Transform(source_parts["node_spec"], target_parts["node_spec"], path_arc=-0.24),
                Transform(source_parts["node_svg"], target_parts["node_svg"], path_arc=0.0),
                Transform(source_parts["node_video"], target_parts["node_video"], path_arc=0.24),
                lag_ratio=0.08,
            ),
            run_time=5.2,
            rate_func=smooth,
        )
        self.wait(1.0)
        self.play(FadeOut(target_hint), run_time=0.55)
        self.wait(0.45)

        pulse_core = Circle(radius=0.16, stroke_width=0, fill_color=PRIMARY_RED, fill_opacity=1)
        pulse_halo = Circle(radius=0.31, stroke_width=2.2, stroke_color=PRIMARY_RED, fill_color=PRIMARY_RED, fill_opacity=0.1)
        pulse = VGroup(pulse_halo, pulse_core)
        first_start = source_parts["node_spec"].get_center() + UP * 0.72 + RIGHT * 1.0
        first_end = source_parts["node_svg"].get_center() + DOWN * 0.72 + LEFT * 0.86
        second_start = source_parts["node_svg"].get_center() + DOWN * 0.72 + RIGHT * 0.86
        second_end = source_parts["node_video"].get_center() + UP * 0.72 + LEFT * 1.0
        pulse.move_to(first_start)
        pulse.set_z_index(9)
        first_path = pulse_path(first_start, first_end)
        second_path = pulse_path(second_start, second_end)

        self.play(FadeIn(pulse, scale=0.72), run_time=0.45)
        self.play(MoveAlongPath(pulse, first_path), run_time=2.05, rate_func=smooth)
        self.play(pulse.animate.move_to(second_start), run_time=0.28, rate_func=smooth)
        self.play(MoveAlongPath(pulse, second_path), run_time=2.05, rate_func=smooth)
        terminal_outline = terminal_outline_for(source_parts["node_video"])
        self.play(FadeOut(pulse, scale=1.25), FadeIn(terminal_outline), run_time=0.8)
        self.wait(6.5)


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
