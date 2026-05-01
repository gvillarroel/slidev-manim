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
from dataclasses import dataclass, field
from pathlib import Path

import numpy as np
from manim import (
    DOWN,
    ORIGIN,
    RIGHT,
    UP,
    AnimationGroup,
    Circle,
    Create,
    FadeIn,
    Group,
    LaggedStart,
    Rectangle,
    Scene,
    SVGMobject,
    Text,
    rate_functions,
)
from manimpango import list_fonts

SPIKE_DIR = Path(__file__).resolve().parent
REPO_ROOT = SPIKE_DIR.parent.parent
SPIKE_NAME = SPIKE_DIR.name
OUTPUT_DIR = REPO_ROOT / "videos" / SPIKE_NAME
STAGING_DIR = OUTPUT_DIR / ".manim"
GENERATED_DIR = OUTPUT_DIR / ".generated"
FRAGMENTS_DIR = GENERATED_DIR / "fragments"

MERMAID_PACKAGE = "@mermaid-js/mermaid-cli@11.14.0"
SVG_NS = "http://www.w3.org/2000/svg"
XHTML_NS = "http://www.w3.org/1999/xhtml"
NS = {"svg": SVG_NS, "xhtml": XHTML_NS}

PRIMARY_RED = "#9e1b32"
PRIMARY_ORANGE = "#e77204"
PRIMARY_GREEN = "#45842a"
PRIMARY_BLUE = "#007298"
PRIMARY_PURPLE = "#652f6c"
WHITE = "#ffffff"
GRAY = "#333e48"
GRAY_100 = "#e7e7e7"
GRAY_200 = "#cfcfcf"
PAGE_BACKGROUND = "#f7f7f7"

TEXT_FONT = "Open Sans" if "Open Sans" in list_fonts() else "Arial"
BRANCH_COLORS = (PRIMARY_BLUE, PRIMARY_GREEN, PRIMARY_PURPLE, PRIMARY_ORANGE)
EDGE_ID_RE = re.compile(r"edge_(\d+)_(\d+)")


@dataclass(frozen=True)
class SvgBox:
    min_x: float
    min_y: float
    width: float
    height: float


@dataclass
class NodeSpec:
    node_id: str
    label: str
    center: tuple[float, float]
    fragment: Path
    section: str
    label_width: float
    label_height: float
    body_width: float
    body_height: float
    parent: str | None = None
    children: list[str] = field(default_factory=list)
    depth: int = 0
    branch_index: int = 0


@dataclass(frozen=True)
class EdgeSpec:
    edge_id: str
    parent: str
    child: str
    fragment: Path
    branch_index: int
    depth: int


@dataclass
class MindmapSpec:
    view_box: SvgBox
    root_id: str
    nodes: dict[str, NodeSpec]
    edges: list[EdgeSpec]


class _Args(argparse.Namespace):
    quality: str
    force_mermaid: bool


def parse_args() -> _Args:
    parser = argparse.ArgumentParser(description="Render the Mermaid mindmap SVG unfold spike.")
    parser.add_argument(
        "--quality",
        choices=("low", "medium", "high", "production", "4k"),
        default="medium",
        help="Manim quality preset.",
    )
    parser.add_argument(
        "--force-mermaid",
        action="store_true",
        help="Regenerate Mermaid SVG and fragment assets even if they already exist.",
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
    command.extend([str(Path(__file__).resolve()), "MermaidMindmapSvgUnfoldScene"])
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


def ensure_mermaid_svg(force: bool = False) -> Path:
    GENERATED_DIR.mkdir(parents=True, exist_ok=True)
    svg_path = GENERATED_DIR / "mindmap.svg"
    if force or not svg_path.exists():
        subprocess.run(mermaid_command(SPIKE_DIR / "diagram.mmd", svg_path), check=True, cwd=str(REPO_ROOT))
    return svg_path


def local_name(element: ET.Element) -> str:
    return element.tag.rsplit("}", 1)[-1]


def class_tokens(element: ET.Element) -> set[str]:
    return set(element.attrib.get("class", "").split())


def parse_view_box(raw_value: str | None) -> SvgBox:
    if not raw_value:
        return SvgBox(0.0, 0.0, 1.0, 1.0)
    values = [float(part) for part in raw_value.split()]
    if len(values) != 4:
        raise ValueError(f"Unexpected SVG viewBox: {raw_value!r}")
    return SvgBox(values[0], values[1], values[2], values[3])


def parse_translate(transform: str | None) -> tuple[float, float]:
    if not transform:
        return (0.0, 0.0)
    match = re.search(r"translate\(\s*([-\d.]+)[,\s]+([-\d.]+)\s*\)", transform)
    if not match:
        return (0.0, 0.0)
    return (float(match.group(1)), float(match.group(2)))


def node_section(group: ET.Element) -> str:
    for token in class_tokens(group):
        if token.startswith("section"):
            return token
    return "section-0"


def node_label(group: ET.Element) -> str:
    labels: list[str] = []
    for element in group.iter():
        if local_name(element) in {"p", "span", "tspan"}:
            text = "".join(element.itertext()).strip()
            if text:
                labels.append(text)
    if labels:
        return " ".join(dict.fromkeys(labels))
    return group.attrib.get("id", "node")


def label_box(group: ET.Element) -> tuple[float, float]:
    for element in group.iter():
        if local_name(element) == "foreignObject":
            return (
                float(element.attrib.get("width", "90")),
                float(element.attrib.get("height", "24")),
            )
    return (90.0, 24.0)


def node_body_box(group: ET.Element) -> tuple[float, float]:
    circle = next(
        (
            child
            for child in group.iter()
            if local_name(child) == "circle" and "label-container" in class_tokens(child)
        ),
        None,
    )
    if circle is not None:
        radius = float(circle.attrib.get("r", "45"))
        return (radius * 2, radius * 2)

    line = next((child for child in group.iter() if local_name(child) == "line"), None)
    if line is not None:
        x1 = float(line.attrib.get("x1", "-45"))
        x2 = float(line.attrib.get("x2", "45"))
        y1 = float(line.attrib.get("y1", "17"))
        return (abs(x2 - x1), abs(y1) * 2)

    return (90.0, 34.0)


def remove_label_groups(element: ET.Element) -> None:
    for child in list(element):
        if local_name(child) in {"foreignObject", "text"} or "label" in class_tokens(child):
            element.remove(child)
            continue
        remove_label_groups(child)


def normalize_node_fragment(element: ET.Element, color: str) -> None:
    remove_label_groups(element)
    for child in element.iter():
        name = local_name(child)
        tokens = class_tokens(child)
        if name in {"path", "rect", "circle", "polygon"} and (
            "node-bkg" in tokens or "label-container" in tokens or name == "path"
        ):
            child.attrib["fill"] = color
            child.attrib["stroke"] = color
            child.attrib["stroke-width"] = "1.2"
            child.attrib.pop("style", None)
        if name == "line":
            child.attrib["stroke"] = color
            child.attrib["stroke-width"] = "2.2"
            child.attrib["stroke-linecap"] = "round"
            child.attrib.pop("style", None)


def normalize_edge_fragment(element: ET.Element, color: str, depth: int) -> None:
    width = "8.5" if depth <= 1 else "5.2"
    element.attrib["fill"] = "none"
    element.attrib["stroke"] = color
    element.attrib["stroke-width"] = width
    element.attrib["stroke-linecap"] = "round"
    element.attrib["stroke-linejoin"] = "round"
    element.attrib.pop("style", None)


def write_fragment_svg(
    root: ET.Element,
    element: ET.Element,
    destination: Path,
    view_box: SvgBox,
    *,
    node_color: str | None = None,
    edge_color: str | None = None,
    edge_depth: int = 1,
) -> None:
    destination.parent.mkdir(parents=True, exist_ok=True)
    ET.register_namespace("", SVG_NS)
    ET.register_namespace("xhtml", XHTML_NS)
    out_root = ET.Element(
        f"{{{SVG_NS}}}svg",
        {
            "id": root.attrib.get("id", "my-svg"),
            "viewBox": f"{view_box.min_x} {view_box.min_y} {view_box.width} {view_box.height}",
            "width": root.attrib.get("width", "100%"),
            "height": root.attrib.get("height", "100%"),
            "xmlns:xlink": "http://www.w3.org/1999/xlink",
        },
    )
    for child in list(root):
        if local_name(child) in {"style", "defs", "linearGradient"}:
            out_root.append(copy.deepcopy(child))

    ET.SubElement(
        out_root,
        f"{{{SVG_NS}}}rect",
        {
            "x": str(view_box.min_x),
            "y": str(view_box.min_y),
            "width": str(view_box.width),
            "height": str(view_box.height),
            "fill": WHITE,
            "fill-opacity": "0.001",
            "stroke": "none",
        },
    )
    fragment = copy.deepcopy(element)
    if node_color is not None:
        normalize_node_fragment(fragment, node_color)
    if edge_color is not None:
        normalize_edge_fragment(fragment, edge_color, edge_depth)
    out_root.append(fragment)
    ET.ElementTree(out_root).write(destination, encoding="utf-8", xml_declaration=False)


def branch_color(branch_index: int) -> str:
    return BRANCH_COLORS[branch_index % len(BRANCH_COLORS)]


def parse_mindmap(svg_path: Path) -> MindmapSpec:
    tree = ET.parse(svg_path)
    root = tree.getroot()
    view_box = parse_view_box(root.attrib.get("viewBox"))

    node_elements: dict[str, ET.Element] = {}
    nodes: dict[str, NodeSpec] = {}
    for group in root.iter():
        if local_name(group) != "g" or "mindmap-node" not in class_tokens(group):
            continue
        node_id = group.attrib["id"]
        width, height = label_box(group)
        body_width, body_height = node_body_box(group)
        node_elements[node_id] = group
        nodes[node_id] = NodeSpec(
            node_id=node_id,
            label=node_label(group),
            center=parse_translate(group.attrib.get("transform")),
            fragment=FRAGMENTS_DIR / "nodes" / f"{node_id}.svg",
            section=node_section(group),
            label_width=width,
            label_height=height,
            body_width=body_width,
            body_height=body_height,
        )

    raw_edges: list[tuple[str, str, ET.Element]] = []
    for path in root.iter():
        if local_name(path) != "path":
            continue
        edge_id = path.attrib.get("id", "")
        match = EDGE_ID_RE.search(edge_id)
        if not match:
            continue
        parent = f"my-svg-node_{match.group(1)}"
        child = f"my-svg-node_{match.group(2)}"
        if parent in nodes and child in nodes:
            raw_edges.append((parent, child, path))
            nodes[parent].children.append(child)
            nodes[child].parent = parent

    root_candidates = [node_id for node_id, spec in nodes.items() if spec.parent is None]
    root_id = next(
        (node_id for node_id, spec in nodes.items() if "section-root" in spec.section),
        root_candidates[0],
    )

    first_level = nodes[root_id].children
    branch_by_node: dict[str, int] = {root_id: 0}
    for index, child in enumerate(first_level):
        branch_by_node[child] = index

    queue = [(child, 1, branch_by_node[child]) for child in first_level]
    while queue:
        node_id, depth, branch_index = queue.pop(0)
        nodes[node_id].depth = depth
        nodes[node_id].branch_index = branch_index
        for child in nodes[node_id].children:
            branch_by_node[child] = branch_index
            queue.append((child, depth + 1, branch_index))

    root_color = PRIMARY_RED
    for node_id, spec in nodes.items():
        color = root_color if node_id == root_id else branch_color(spec.branch_index)
        write_fragment_svg(root, node_elements[node_id], spec.fragment, view_box, node_color=color)

    edges: list[EdgeSpec] = []
    for parent, child, path in raw_edges:
        edge_id = path.attrib["id"]
        depth = max(1, nodes[child].depth)
        branch_index = nodes[child].branch_index
        fragment = FRAGMENTS_DIR / "edges" / f"{edge_id}.svg"
        write_fragment_svg(
            root,
            path,
            fragment,
            view_box,
            edge_color=branch_color(branch_index),
            edge_depth=depth,
        )
        edges.append(
            EdgeSpec(
                edge_id=edge_id,
                parent=parent,
                child=child,
                fragment=fragment,
                branch_index=branch_index,
                depth=depth,
            )
        )

    return MindmapSpec(view_box=view_box, root_id=root_id, nodes=nodes, edges=edges)


def ensure_assets(force: bool = False) -> MindmapSpec:
    svg_path = ensure_mermaid_svg(force=force)
    if force and FRAGMENTS_DIR.exists():
        shutil.rmtree(FRAGMENTS_DIR)
    return parse_mindmap(svg_path)


def svg_point_to_manim(point: tuple[float, float], view_box: SvgBox, diagram_center: np.ndarray, scale: float) -> np.ndarray:
    center_x = view_box.min_x + view_box.width / 2
    center_y = view_box.min_y + view_box.height / 2
    return diagram_center + np.array([(point[0] - center_x) * scale, -(point[1] - center_y) * scale, 0.0])


def label_for_node(spec: NodeSpec, view_box: SvgBox, diagram_center: np.ndarray, scale: float) -> Group:
    font_size = 25 if spec.depth == 0 else 21 if spec.depth == 1 else 17
    words = [
        Text(word, font=TEXT_FONT, font_size=font_size, color=WHITE, weight="BOLD")
        for word in spec.label.split()
    ]
    label = Group(*words).arrange(RIGHT, buff=0.12 if spec.depth > 0 else 0.14)
    max_width = spec.body_width * scale * (0.78 if spec.depth == 0 else 0.92)
    max_height = min(spec.body_height * scale * 0.7, spec.label_height * scale * 1.1)
    if label.width > max_width:
        label.scale_to_fit_width(max_width)
    if label.height > max_height:
        label.scale_to_fit_height(max_height)
    label.move_to(svg_point_to_manim(spec.center, view_box, diagram_center, scale))
    label.set_z_index(6)
    return label


def build_imported_fragments(
    spec: MindmapSpec,
    *,
    target_height: float,
    diagram_center: np.ndarray,
) -> tuple[dict[str, SVGMobject], dict[str, Group], dict[str, SVGMobject], float]:
    scale = target_height / spec.view_box.height
    node_bodies: dict[str, SVGMobject] = {}
    node_labels: dict[str, Group] = {}
    edge_bodies: dict[str, SVGMobject] = {}

    for node_id, node_spec in spec.nodes.items():
        body = SVGMobject(str(node_spec.fragment), height=target_height)
        body.move_to(diagram_center)
        body.set_z_index(4)
        node_bodies[node_id] = body
        node_labels[node_id] = label_for_node(node_spec, spec.view_box, diagram_center, scale)

    for edge in spec.edges:
        body = SVGMobject(str(edge.fragment), height=target_height)
        body.move_to(diagram_center)
        body.set_z_index(2 if edge.depth <= 1 else 3)
        edge_bodies[edge.edge_id] = body

    return node_bodies, node_labels, edge_bodies, scale


def edge_lookup(spec: MindmapSpec) -> dict[tuple[str, str], EdgeSpec]:
    return {(edge.parent, edge.child): edge for edge in spec.edges}


def subtree_nodes(spec: MindmapSpec, node_id: str) -> list[str]:
    found: list[str] = []
    queue = list(spec.nodes[node_id].children)
    while queue:
        child = queue.pop(0)
        found.append(child)
        queue.extend(spec.nodes[child].children)
    return found


class MermaidMindmapSvgUnfoldScene(Scene):
    def construct(self) -> None:
        self.camera.background_color = PAGE_BACKGROUND
        poster_mode = os.environ.get("SPIKE_RENDER_TARGET") == "poster"
        force_assets = os.environ.get("SPIKE_FORCE_MERMAID") == "1"

        spec = ensure_assets(force=force_assets)
        diagram_center = ORIGIN + DOWN * 0.22
        target_height = min(6.1, 11.55 / (spec.view_box.width / spec.view_box.height))
        node_bodies, node_labels, edge_bodies, _scale = build_imported_fragments(
            spec,
            target_height=target_height,
            diagram_center=diagram_center,
        )
        edges_by_pair = edge_lookup(spec)

        title = Text("Mermaid mindmap SVG", font=TEXT_FONT, font_size=31, color=GRAY)
        title.to_edge(UP, buff=0.42)
        subtitle = Text("decomposed into SVG fragments", font=TEXT_FONT, font_size=18, color=PRIMARY_BLUE)
        subtitle.next_to(title, DOWN, buff=0.12)

        stage = Rectangle(
            width=12.25,
            height=6.55,
            stroke_color=GRAY_200,
            stroke_width=2,
            fill_color=WHITE,
            fill_opacity=0.72,
        )
        stage.move_to(DOWN * 0.18)
        stage.set_z_index(-4)

        root_id = spec.root_id
        first_level = list(spec.nodes[root_id].children)

        all_edges = Group(*edge_bodies.values())
        all_nodes = Group(*node_bodies.values(), *node_labels.values())
        final_group = Group(all_edges, all_nodes)

        if poster_mode:
            self.add(stage, title, subtitle, final_group)
            return

        root_group = Group(node_bodies[root_id], node_labels[root_id])
        self.add(stage, title, subtitle, root_group)
        self.wait(2.7)

        pulse = Circle(radius=0.16, stroke_width=0, fill_color=PRIMARY_RED, fill_opacity=0.92)
        pulse.move_to(node_labels[root_id].get_center())
        pulse.set_z_index(8)
        self.play(FadeIn(pulse, scale=0.55), run_time=0.28)
        self.play(
            pulse.animate.scale(3.1).set_fill(PRIMARY_RED, opacity=0),
            run_time=0.72,
            rate_func=rate_functions.ease_out_cubic,
        )
        self.remove(pulse)

        for child in first_level:
            edge = edges_by_pair[(root_id, child)]
            branch_group = Group(node_bodies[child], node_labels[child])
            self.play(
                Create(edge_bodies[edge.edge_id]),
                run_time=0.95,
                rate_func=rate_functions.ease_in_out_cubic,
            )
            self.play(
                FadeIn(branch_group, shift=UP * 0.08),
                run_time=0.74,
                rate_func=rate_functions.ease_out_cubic,
            )
            self.wait(0.42)

        self.wait(0.45)

        for branch in first_level:
            child_ids = subtree_nodes(spec, branch)
            reveal_anims = []
            for child in child_ids:
                edge = edges_by_pair[(spec.nodes[child].parent or root_id, child)]
                reveal_anims.append(Create(edge_bodies[edge.edge_id]))
                reveal_anims.append(FadeIn(Group(node_bodies[child], node_labels[child]), shift=UP * 0.06))
            if reveal_anims:
                self.play(
                    LaggedStart(*reveal_anims, lag_ratio=0.12),
                    run_time=2.25,
                    rate_func=rate_functions.ease_in_out_cubic,
                )
                self.wait(0.48)

        root_flash = Circle(radius=0.18, stroke_width=0, fill_color=PRIMARY_RED, fill_opacity=0.84)
        root_flash.move_to(node_labels[root_id].get_center())
        root_flash.set_z_index(9)
        self.play(FadeIn(root_flash, scale=0.72), run_time=0.24)
        self.play(
            root_flash.animate.scale(5.2).set_fill(PRIMARY_RED, opacity=0),
            final_group.animate.scale(1.012),
            run_time=1.05,
            rate_func=rate_functions.ease_out_cubic,
        )
        self.remove(root_flash)
        self.play(final_group.animate.scale(1 / 1.012), run_time=0.32)
        self.wait(7.1)


def render_variant(args: _Args) -> None:
    video_path, poster_path = output_paths()
    base_env = os.environ.copy()
    base_env["SPIKE_FORCE_MERMAID"] = "1" if args.force_mermaid else "0"

    video_env = {**base_env, "SPIKE_RENDER_TARGET": "video"}
    result = subprocess.run(render_command(args, video_path.stem, poster=False), check=False, env=video_env)
    if result.returncode != 0:
        raise SystemExit(result.returncode)
    promote(video_path.name, video_path)

    poster_env = {**base_env, "SPIKE_RENDER_TARGET": "poster"}
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
