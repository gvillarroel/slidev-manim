#!/usr/bin/env -S uv run --script
# /// script
# dependencies = [
#   "manim>=0.20.0",
# ]
# ///

from __future__ import annotations

import argparse
import base64
import copy
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
import xml.etree.ElementTree as ET
from dataclasses import dataclass
from pathlib import Path

from manim import (
    DOWN,
    Arrow,
    BackgroundRectangle,
    Circle,
    FadeIn,
    FadeOut,
    Group,
    LEFT,
    RIGHT,
    RoundedRectangle,
    Scene,
    Text,
    UP,
    VGroup,
    WHITE as MANIM_WHITE,
    AnimationGroup,
    Succession,
    Transform,
    linear,
)

SPIKE_DIR = Path(__file__).resolve().parent
REPO_ROOT = SPIKE_DIR.parent.parent
SPIKE_NAME = SPIKE_DIR.name
OUTPUT_DIR = REPO_ROOT / "videos" / SPIKE_NAME
STAGING_DIR = OUTPUT_DIR / ".manim"
GENERATED_DIR = OUTPUT_DIR / ".generated"

PRIMARY_RED = "#9e1b32"
PRIMARY_ORANGE = "#e77204"
PRIMARY_GREEN = "#45842a"
PRIMARY_BLUE = "#007298"
PRIMARY_PURPLE = "#652f6c"
GRAY = "#333e48"
PRIMARY_YELLOW = "#f1c319"
GRAY_100 = "#e7e7e7"
GRAY_200 = "#cfcfcf"
GRAY_600 = "#696969"

SVG_NS = {"svg": "http://www.w3.org/2000/svg", "xhtml": "http://www.w3.org/1999/xhtml"}


SOURCE_DIAGRAM = """%%{init: {"theme":"base","themeVariables":{"fontFamily":"Open Sans, Arial, sans-serif","primaryColor":"#45842a","primaryTextColor":"#ffffff","primaryBorderColor":"#45842a","secondaryColor":"#007298","secondaryTextColor":"#ffffff","secondaryBorderColor":"#007298","tertiaryColor":"#652f6c","tertiaryTextColor":"#ffffff","lineColor":"#e77204","textColor":"#ffffff"}}}%%
flowchart LR
    A[Collect] --> B[Review]
    B --> C[Ship]
"""

TARGET_DIAGRAM = """%%{init: {"theme":"base","themeVariables":{"fontFamily":"Open Sans, Arial, sans-serif","primaryColor":"#9e1b32","primaryTextColor":"#ffffff","primaryBorderColor":"#9e1b32","secondaryColor":"#652f6c","secondaryTextColor":"#ffffff","secondaryBorderColor":"#652f6c","tertiaryColor":"#007298","tertiaryTextColor":"#ffffff","lineColor":"#e77204","textColor":"#ffffff"}}}%%
stateDiagram-v2
    [*] --> Collect
    Collect --> Review
    Review --> Ship
"""


@dataclass
class NodeSpec:
    label: str
    svg_path: Path
    center: tuple[float, float]
    kind: str


@dataclass
class EdgeSpec:
    key: tuple[str, str]
    svg_path: Path
    center: tuple[float, float]


@dataclass
class DiagramSpec:
    view_box: tuple[float, float, float, float]
    nodes: dict[str, NodeSpec]
    edges: dict[tuple[str, str], EdgeSpec]
    start: NodeSpec | None


class _Args(argparse.Namespace):
    quality: str


def parse_args() -> _Args:
    parser = argparse.ArgumentParser(description="Render the mermaid-svg-component-remap spike.")
    parser.add_argument(
        "--quality",
        choices=("low", "medium", "high", "production", "4k"),
        default="medium",
        help="Manim quality preset.",
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


def output_paths() -> tuple[Path, Path]:
    return OUTPUT_DIR / f"{SPIKE_NAME}.webm", OUTPUT_DIR / f"{SPIKE_NAME}.png"


def render_command(args: _Args, stem: str, poster: bool) -> list[str]:
    STAGING_DIR.mkdir(parents=True, exist_ok=True)
    return [
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
        "-s" if poster else "-t",
        str(Path(__file__).resolve()),
        "MermaidSvgComponentRemapScene",
    ]


def promote(target_name: str, destination: Path) -> None:
    matches = sorted(STAGING_DIR.glob(f"**/{target_name}"))
    if not matches:
        raise FileNotFoundError(f"Could not find {target_name}")
    destination.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(matches[-1], destination)


def prep(scene: Scene) -> None:
    scene.camera.background_color = MANIM_WHITE


def ensure_mermaid_svg(source_text: str, target_text: str, workdir: Path) -> tuple[Path, Path]:
    workdir.mkdir(parents=True, exist_ok=True)
    source_mmd = workdir / "source.mmd"
    target_mmd = workdir / "target.mmd"
    source_svg = workdir / "source.svg"
    target_svg = workdir / "target.svg"

    source_mmd.write_text(source_text, encoding="utf-8")
    target_mmd.write_text(target_text, encoding="utf-8")

    for input_path, output_path in ((source_mmd, source_svg), (target_mmd, target_svg)):
        subprocess.run(
            [
                "cmd",
                "/c",
                "npx",
                "-y",
                "@mermaid-js/mermaid-cli",
                "-i",
                str(input_path),
                "-o",
                str(output_path),
                "-b",
                "transparent",
            ],
            check=True,
            cwd=str(REPO_ROOT),
        )
    return source_svg, target_svg


def parse_view_box(root: ET.Element) -> tuple[float, float, float, float]:
    raw = root.attrib.get("viewBox", "0 0 1 1").split()
    return tuple(float(part) for part in raw)  # type: ignore[return-value]


def parse_translate(transform: str | None) -> tuple[float, float]:
    if not transform:
        return (0.0, 0.0)
    match = re.search(r"translate\(([-\d.]+)[ ,]([-\d.]+)\)", transform)
    if not match:
        return (0.0, 0.0)
    return (float(match.group(1)), float(match.group(2)))


def extract_label(group: ET.Element) -> str:
    paragraphs = group.findall(".//xhtml:p", SVG_NS)
    if paragraphs:
        return " ".join((p.text or "").strip() for p in paragraphs if (p.text or "").strip())
    tspans = group.findall(".//svg:tspan", SVG_NS)
    if tspans:
        return " ".join((t.text or "").strip() for t in tspans if (t.text or "").strip())
    return group.attrib.get("id", "unknown")


def decode_points(path_el: ET.Element) -> list[tuple[float, float]]:
    encoded = path_el.attrib.get("data-points", "")
    if not encoded:
        return []
    points = json.loads(base64.b64decode(encoded).decode("utf-8"))
    return [(float(point["x"]), float(point["y"])) for point in points]


def mean_point(points: list[tuple[float, float]]) -> tuple[float, float]:
    if not points:
        return (0.0, 0.0)
    return (
        sum(point[0] for point in points) / len(points),
        sum(point[1] for point in points) / len(points),
    )


def write_fragment_svg(
    root: ET.Element,
    element: ET.Element,
    destination: Path,
) -> None:
    destination.parent.mkdir(parents=True, exist_ok=True)
    out_root = ET.Element(
        "svg",
        {
            "xmlns": SVG_NS["svg"],
            "xmlns:xlink": "http://www.w3.org/1999/xlink",
            "viewBox": root.attrib.get("viewBox", "0 0 1 1"),
            "width": "100%",
        },
    )

    style = root.find("svg:style", SVG_NS)
    if style is not None:
        out_root.append(copy.deepcopy(style))

    outer_group = root.find("svg:g", SVG_NS)
    if outer_group is not None:
        for child in outer_group:
            if child.tag.endswith("marker") or child.tag.endswith("defs"):
                out_root.append(copy.deepcopy(child))

    wrapper = ET.SubElement(out_root, "g")
    wrapper.append(copy.deepcopy(element))
    ET.ElementTree(out_root).write(destination, encoding="utf-8", xml_declaration=False)


def load_diagram_spec(svg_path: Path, prefix: str) -> DiagramSpec:
    tree = ET.parse(svg_path)
    root = tree.getroot()
    view_box = parse_view_box(root)
    nodes_dir = GENERATED_DIR / prefix / "nodes"
    edges_dir = GENERATED_DIR / prefix / "edges"

    nodes: dict[str, NodeSpec] = {}
    start_node: NodeSpec | None = None

    for group in root.findall(".//svg:g[@class='nodes']/svg:g", SVG_NS):
        center = parse_translate(group.attrib.get("transform"))
        label = extract_label(group)
        svg_fragment = nodes_dir / f"{group.attrib.get('id', label).replace('/', '_')}.svg"
        write_fragment_svg(root, group, svg_fragment)
        kind = "start" if "root_start" in group.attrib.get("id", "") else "node"
        spec = NodeSpec(label=label, svg_path=svg_fragment, center=center, kind=kind)
        if kind == "start":
            start_node = spec
        else:
            nodes[label] = spec

    centers = {label: spec.center for label, spec in nodes.items()}
    edges: dict[tuple[str, str], EdgeSpec] = {}
    edge_index = 0
    for path_el in root.findall(".//svg:g[@class='edgePaths']/svg:path", SVG_NS):
        points = decode_points(path_el)
        if len(points) < 2:
            continue
        start = points[0]
        end = points[-1]

        def nearest_label(point: tuple[float, float]) -> str:
            return min(
                centers,
                key=lambda label: (centers[label][0] - point[0]) ** 2 + (centers[label][1] - point[1]) ** 2,
            )

        key = (nearest_label(start), nearest_label(end))
        edge_svg = edges_dir / f"edge-{edge_index}.svg"
        write_fragment_svg(root, path_el, edge_svg)
        edges[key] = EdgeSpec(key=key, svg_path=edge_svg, center=mean_point(points))
        edge_index += 1

    return DiagramSpec(view_box=view_box, nodes=nodes, edges=edges, start=start_node)


def badge(label: str, color: str) -> VGroup:
    text = Text(label, font_size=20, color=MANIM_WHITE)
    bg = BackgroundRectangle(text, color=color, fill_opacity=1, buff=0.18, corner_radius=0.18)
    return VGroup(bg, text)


def build_panel(panel_title: str, color: str, width: float, height: float) -> VGroup:
    frame = RoundedRectangle(
        width=width,
        height=height,
        corner_radius=0.28,
        stroke_color=GRAY_200,
        stroke_width=2,
        fill_color=GRAY_100,
        fill_opacity=0.38,
    )
    title = Text(panel_title, font_size=19, color=color)
    title.next_to(frame.get_top(), DOWN, buff=0.4)
    title.align_to(frame.get_left(), LEFT).shift(RIGHT * 0.42)
    return VGroup(frame, title)


def build_source_node(label: str, color: str) -> VGroup:
    box = RoundedRectangle(
        width=2.15,
        height=0.96,
        corner_radius=0.24,
        stroke_color=color,
        stroke_width=0,
        fill_color=color,
        fill_opacity=1,
    )
    text = Text(label, font_size=26, color=MANIM_WHITE)
    text.move_to(box.get_center())
    return VGroup(box, text)


def build_target_node(label: str, color: str) -> VGroup:
    bubble = Circle(
        radius=0.62,
        stroke_color=color,
        stroke_width=0,
        fill_color=color,
        fill_opacity=1,
    )
    text = Text(label, font_size=24, color=MANIM_WHITE)
    text.move_to(bubble.get_center())
    return VGroup(bubble, text)


def build_start_marker() -> Circle:
    return Circle(
        radius=0.12,
        stroke_color=PRIMARY_RED,
        stroke_width=0,
        fill_color=PRIMARY_RED,
        fill_opacity=1,
    )


def build_source_edge(start_node: VGroup, end_node: VGroup) -> Arrow:
    return Arrow(
        start=start_node.get_right() + RIGHT * 0.02,
        end=end_node.get_left() + LEFT * 0.02,
        buff=0.16,
        stroke_width=8,
        max_tip_length_to_length_ratio=0.14,
        max_stroke_width_to_length_ratio=18,
        color=PRIMARY_ORANGE,
    )


def build_target_edge(start_node: VGroup, end_node: VGroup) -> Arrow:
    return Arrow(
        start=start_node.get_bottom() + DOWN * 0.02,
        end=end_node.get_top() + UP * 0.02,
        buff=0.18,
        stroke_width=7,
        max_tip_length_to_length_ratio=0.14,
        max_stroke_width_to_length_ratio=18,
        color=PRIMARY_ORANGE,
    )


def build_diagram_assets(source_dir: Path) -> tuple[DiagramSpec, DiagramSpec]:
    GENERATED_DIR.mkdir(parents=True, exist_ok=True)
    source_svg, target_svg = ensure_mermaid_svg(SOURCE_DIAGRAM, TARGET_DIAGRAM, source_dir)
    return load_diagram_spec(source_svg, "source"), load_diagram_spec(target_svg, "target")


class MermaidSvgComponentRemapScene(Scene):
    def construct(self) -> None:
        prep(self)
        poster_mode = os.environ.get("SPIKE_RENDER_TARGET") == "poster"

        source_spec, target_spec = build_diagram_assets(GENERATED_DIR / "mermaid")
        ordered_source = sorted(source_spec.nodes, key=lambda label: source_spec.nodes[label].center[0])
        ordered_target = sorted(target_spec.nodes, key=lambda label: target_spec.nodes[label].center[1])
        palette_by_label = {
            "Collect": PRIMARY_GREEN,
            "Review": PRIMARY_BLUE,
            "Ship": PRIMARY_PURPLE,
        }

        title = Text("Mermaid SVG semantic remap", font_size=36, color=GRAY).to_edge(UP, buff=0.5)
        subtitle = Text(
            "Flowchart components move into a state diagram layout",
            font_size=24,
            color=PRIMARY_BLUE,
        ).next_to(title, DOWN, buff=0.2)

        source_panel = build_panel("Source layout", PRIMARY_GREEN, width=7.0, height=3.0).move_to(LEFT * 3.45 + DOWN * 0.55)
        target_panel = build_panel("Target layout", PRIMARY_RED, width=4.35, height=5.0).move_to(RIGHT * 3.35 + DOWN * 0.76)

        badges = VGroup(
            badge("Source: flowchart", PRIMARY_GREEN),
            badge("Target: stateDiagram-v2", PRIMARY_RED),
        ).arrange(RIGHT, buff=0.45).next_to(subtitle, DOWN, buff=0.28)
        badges.scale(0.78)
        badges.shift(UP * 0.32)

        source_positions = {
            ordered_source[0]: LEFT * 5.25 + DOWN * 0.7,
            ordered_source[1]: LEFT * 3.0 + DOWN * 0.7,
            ordered_source[2]: LEFT * 0.75 + DOWN * 0.7,
        }
        target_positions = {
            ordered_target[0]: RIGHT * 3.62 + UP * 0.62,
            ordered_target[1]: RIGHT * 3.62 + DOWN * 0.72,
            ordered_target[2]: RIGHT * 3.62 + DOWN * 2.06,
        }

        source_nodes = {
            label: build_source_node(label, palette_by_label[label]).move_to(source_positions[label])
            for label in ordered_source
        }
        target_nodes = {
            label: build_target_node(label, palette_by_label[label]).move_to(target_positions[label])
            for label in ordered_target
        }
        source_edges = {
            (ordered_source[0], ordered_source[1]): build_source_edge(
                source_nodes[ordered_source[0]], source_nodes[ordered_source[1]]
            ),
            (ordered_source[1], ordered_source[2]): build_source_edge(
                source_nodes[ordered_source[1]], source_nodes[ordered_source[2]]
            ),
        }
        target_edges = {
            (ordered_target[0], ordered_target[1]): build_target_edge(
                target_nodes[ordered_target[0]], target_nodes[ordered_target[1]]
            ),
            (ordered_target[1], ordered_target[2]): build_target_edge(
                target_nodes[ordered_target[1]], target_nodes[ordered_target[2]]
            ),
        }
        target_start = build_start_marker().move_to(target_positions[ordered_target[0]] + UP * 0.82)
        target_start_edge = Arrow(
            start=target_start.get_center() + DOWN * 0.03,
            end=target_nodes[ordered_target[0]].get_top() + UP * 0.02,
            buff=0.12,
            stroke_width=6,
            max_tip_length_to_length_ratio=0.14,
            max_stroke_width_to_length_ratio=18,
            color=PRIMARY_RED,
        )

        if poster_mode:
            divider = Text("semantic move", font_size=22, color=PRIMARY_PURPLE).move_to(DOWN * 0.1)
            source_static = VGroup(*source_edges.values(), *source_nodes.values())
            target_static = VGroup(*target_edges.values(), *target_nodes.values(), target_start, target_start_edge)
            self.add(title, subtitle, badges, source_panel, target_panel, source_static, divider, target_static)
            return

        self.add(title, subtitle, badges, source_panel, target_panel)
        self.play(
            FadeIn(VGroup(*source_nodes.values(), *source_edges.values()), shift=UP * 0.15, lag_ratio=0.08),
            run_time=1.1,
        )
        self.wait(0.4)

        node_transforms = [
            Transform(source_nodes[label], target_nodes[label], path_arc=0.2)
            for label in ("Collect", "Review", "Ship")
        ]
        edge_transforms = [
            Transform(source_edges[key], target_edges[key], path_arc=0.12)
            for key in (("Collect", "Review"), ("Review", "Ship"))
            if key in source_edges and key in target_edges
        ]

        self.play(
            AnimationGroup(
                *edge_transforms,
                *node_transforms,
                lag_ratio=0.1,
            ),
            run_time=2.8,
            rate_func=linear,
        )

        self.play(FadeIn(VGroup(target_start, target_start_edge), shift=UP * 0.15), run_time=0.6)

        review = Text(
            "Finding: Mermaid keeps semantic node and edge groups,\nso shared labels can drive component-level remapping.",
            font_size=22,
            color=GRAY,
            line_spacing=0.85,
        ).to_edge(DOWN, buff=0.45)
        review[0:7].set_color(PRIMARY_PURPLE)
        review_box = BackgroundRectangle(review, color=MANIM_WHITE, fill_opacity=0.94, buff=0.18)
        self.play(FadeIn(VGroup(review_box, review), shift=UP * 0.15), run_time=0.7)
        self.wait(1.4)
        self.play(FadeOut(VGroup(review_box, review)), run_time=0.4)
        self.wait(0.4)


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
