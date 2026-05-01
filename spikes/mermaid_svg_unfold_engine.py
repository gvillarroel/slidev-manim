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

from manim import (
    DOWN,
    ORIGIN,
    UP,
    AnimationGroup,
    Circle,
    FadeIn,
    FadeOut,
    Group,
    ImageMobject,
    LaggedStart,
    Rectangle,
    Scene,
    SVGMobject,
    Text,
    VGroup,
    rate_functions,
)
from manimpango import list_fonts

REPO_ROOT = Path(__file__).resolve().parents[1]
MERMAID_PACKAGE = "@mermaid-js/mermaid-cli@11.14.0"
SVG_NS = "http://www.w3.org/2000/svg"
XHTML_NS = "http://www.w3.org/1999/xhtml"

PRIMARY_RED = "#9e1b32"
PRIMARY_ORANGE = "#d45d00"
PRIMARY_YELLOW = "#f1b434"
PRIMARY_GREEN = "#4b8b3b"
PRIMARY_BLUE = "#007298"
PRIMARY_PURPLE = "#6f2c91"
WHITE = "#ffffff"
GRAY = "#333e48"
GRAY_100 = "#e7e7e7"
GRAY_200 = "#cfcfcf"
GRAY_600 = "#696969"
PAGE_BACKGROUND = "#f7f7f7"
TEXT_FONT = "Open Sans" if "Open Sans" in list_fonts() else "Arial"

GRAPHIC_TAGS = {
    "path",
    "rect",
    "circle",
    "ellipse",
    "polygon",
    "polyline",
    "line",
    "text",
    "foreignObject",
    "image",
}
DEFINITION_TAGS = {"style", "defs", "marker", "linearGradient", "filter", "mask", "clipPath", "pattern"}
CONTAINER_CLASSES = {
    "architecture-edges",
    "architecture-services",
    "architecture-groups",
    "bars",
    "bottom-axis",
    "commit-arrows",
    "commit-bullets",
    "commit-labels",
    "data-points",
    "edgeLabels",
    "edgePaths",
    "eventWrapper",
    "ishikawa",
    "items",
    "labels",
    "left-axis",
    "legend",
    "lineWrapper",
    "links",
    "main",
    "node-labels",
    "nodes",
    "plot",
    "quadrants",
    "sections",
    "slices",
    "taskWrapper",
    "ticks",
    "timeline-node",
    "treemapContainer",
    "tree-view",
}
NOISE_CLASSES = {"background", "subgraphs"}
PALETTE = [PRIMARY_RED, PRIMARY_BLUE, PRIMARY_GREEN, PRIMARY_ORANGE, PRIMARY_PURPLE, PRIMARY_YELLOW]


@dataclass(frozen=True)
class SvgBox:
    min_x: float
    min_y: float
    width: float
    height: float


@dataclass(frozen=True)
class FragmentSpec:
    key: str
    source_class: str
    path: Path
    order: int


@dataclass(frozen=True)
class TextLabelSpec:
    text: str
    x: float
    y: float
    font_size: float
    color: str
    order: int


class _Args(argparse.Namespace):
    quality: str
    force_mermaid: bool
    assets_only: bool


def env_value(name: str, fallback: str = "") -> str:
    value = os.environ.get(name, fallback)
    return value.strip() if value else fallback


def spike_dir() -> Path:
    return Path(env_value("MERMAID_UNFOLD_SPIKE_DIR")).resolve()


def spike_file() -> Path:
    return Path(env_value("MERMAID_UNFOLD_SPIKE_FILE")).resolve()


def spike_name() -> str:
    return spike_dir().name


def diagram_title() -> str:
    return env_value("MERMAID_UNFOLD_TITLE", spike_name())


def output_dir() -> Path:
    return REPO_ROOT / "videos" / spike_name()


def staging_dir() -> Path:
    return output_dir() / ".manim"


def generated_dir() -> Path:
    return output_dir() / ".generated"


def fragments_dir() -> Path:
    return generated_dir() / "fragments"


def parse_args() -> _Args:
    parser = argparse.ArgumentParser(description=f"Render {spike_name()} Mermaid SVG unfold spike.")
    parser.add_argument(
        "--quality",
        choices=("low", "medium", "high", "production", "4k"),
        default="medium",
        help="Manim quality preset.",
    )
    parser.add_argument("--force-mermaid", action="store_true", help="Regenerate Mermaid assets and fragments.")
    parser.add_argument("--assets-only", action="store_true", help="Only generate Mermaid SVG/PNG and fragments.")
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
    return output_dir() / f"{spike_name()}.webm", output_dir() / f"{spike_name()}.png"


def render_command(args: _Args, stem: str, *, poster: bool) -> list[str]:
    staging_dir().mkdir(parents=True, exist_ok=True)
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
        str(staging_dir()),
    ]
    if poster:
        command.append("-s")
    else:
        command.extend(["--format", "webm"])
    command.extend([str(spike_file()), "MermaidSvgUnfoldScene"])
    return command


def promote(target_name: str, destination: Path) -> None:
    matches = sorted(staging_dir().glob(f"**/{target_name}"), key=lambda path: path.stat().st_mtime)
    if not matches:
        raise FileNotFoundError(f"Could not find {target_name} under {staging_dir()}")
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


def render_mermaid_asset(input_path: Path, output_path: Path) -> None:
    result = subprocess.run(
        mermaid_command(input_path, output_path),
        cwd=str(REPO_ROOT),
        capture_output=True,
        text=True,
        check=False,
    )
    if result.returncode != 0:
        raise RuntimeError(
            f"Mermaid render failed for {input_path} -> {output_path}\n"
            f"stdout:\n{result.stdout}\n\nstderr:\n{result.stderr}"
        )


def ensure_mermaid_assets(force: bool = False) -> tuple[Path, Path]:
    out = generated_dir()
    out.mkdir(parents=True, exist_ok=True)
    source = spike_dir() / "diagram.mmd"
    svg = out / "diagram.svg"
    png = out / "diagram.png"
    if force or not svg.exists():
        render_mermaid_asset(source, svg)
    if force or not png.exists():
        render_mermaid_asset(source, png)
    return svg, png


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


def has_visible_graphic(element: ET.Element) -> bool:
    for child in element.iter():
        tag = local_name(child)
        if tag not in GRAPHIC_TAGS:
            continue
        tokens = class_tokens(child)
        if tokens & NOISE_CLASSES:
            continue
        if tag == "rect" and child.attrib.get("fill-opacity") == "0.001":
            continue
        return True
    return False


def is_container(element: ET.Element) -> bool:
    tokens = class_tokens(element)
    return bool(tokens & CONTAINER_CLASSES)


def useful_children(element: ET.Element) -> list[ET.Element]:
    children = []
    for child in list(element):
        tag = local_name(child)
        if tag in DEFINITION_TAGS:
            continue
        if class_tokens(child) & NOISE_CLASSES:
            continue
        if has_visible_graphic(child):
            children.append(child)
    return children


def find_root_groups(root: ET.Element) -> list[ET.Element]:
    groups = [child for child in list(root) if local_name(child) == "g" and has_visible_graphic(child)]
    return groups or [root]


def collect_fragment_elements(root: ET.Element) -> list[ET.Element]:
    fragments: list[ET.Element] = []
    seen: set[int] = set()

    def add(element: ET.Element) -> None:
        if local_name(element) in {"text", "foreignObject"}:
            return
        identity = id(element)
        if identity not in seen and has_visible_graphic(element):
            seen.add(identity)
            fragments.append(element)

    for group in find_root_groups(root):
        for element in group.iter():
            if local_name(element) != "g" or not is_container(element):
                continue
            children = useful_children(element)
            if children:
                for child in children:
                    add(child)

    if len(fragments) < 4:
        for group in find_root_groups(root):
            for child in useful_children(group):
                if is_container(child):
                    for nested in useful_children(child):
                        add(nested)
                else:
                    add(child)

    if len(fragments) < 4:
        for element in root.iter():
            if local_name(element) in GRAPHIC_TAGS and not (class_tokens(element) & NOISE_CLASSES):
                add(element)

    return fragments[:72]


def safe_key(value: str, fallback: str) -> str:
    value = value or fallback
    value = re.sub(r"[^A-Za-z0-9_.-]+", "-", value).strip("-")
    return value or fallback


def copy_svg_support(root: ET.Element, out_root: ET.Element) -> None:
    for child in list(root):
        if local_name(child) in {"style", "defs", "linearGradient"}:
            out_root.append(copy.deepcopy(child))


def remove_unsupported_text(element: ET.Element) -> ET.Element:
    clone = copy.deepcopy(element)
    for parent in clone.iter():
        for child in list(parent):
            if local_name(child) in {"text", "foreignObject"}:
                parent.remove(child)
    return clone


def write_fragment(root: ET.Element, view_box: SvgBox, element: ET.Element, destination: Path) -> None:
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
    copy_svg_support(root, out_root)
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
    out_root.append(remove_unsupported_text(element))
    ET.ElementTree(out_root).write(destination, encoding="utf-8", xml_declaration=False)


def ensure_fragments(svg_path: Path, force: bool = False) -> list[FragmentSpec]:
    fragment_root = fragments_dir()
    manifest = fragment_root / "manifest-textless-v1.tsv"
    if force and fragment_root.exists():
        shutil.rmtree(fragment_root)
    if manifest.exists() and not force:
        data = manifest.read_text(encoding="utf-8")
        specs = []
        for row in data.splitlines():
            if not row.strip():
                continue
            key, source_class, rel_path, order = row.split("\t")
            specs.append(FragmentSpec(key, source_class, fragment_root / rel_path, int(order)))
        if specs and all(spec.path.exists() for spec in specs):
            return specs

    tree = ET.parse(svg_path)
    root = tree.getroot()
    view_box = parse_view_box(root.attrib.get("viewBox"))
    specs: list[FragmentSpec] = []
    for index, element in enumerate(collect_fragment_elements(root)):
        raw_key = element.attrib.get("id") or element.attrib.get("data-id") or element.attrib.get("class") or local_name(element)
        key = f"{index:03d}-{safe_key(raw_key, local_name(element))}"
        path = fragment_root / f"{key}.svg"
        write_fragment(root, view_box, element, path)
        specs.append(FragmentSpec(key=key, source_class=element.attrib.get("class", ""), path=path, order=index))

    fragment_root.mkdir(parents=True, exist_ok=True)
    manifest.write_text(
        "".join(f"{spec.key}\t{spec.source_class}\t{spec.path.name}\t{spec.order}\n" for spec in specs),
        encoding="utf-8",
    )
    return specs


def fit_text(label: Text, max_width: float, max_height: float | None = None) -> Text:
    if label.width > max_width:
        label.scale_to_fit_width(max_width)
    if max_height is not None and label.height > max_height:
        label.scale_to_fit_height(max_height)
    return label


def parse_float(value: str | None, fallback: float = 0.0) -> float:
    if not value:
        return fallback
    match = re.search(r"-?\d+(?:\.\d+)?", value)
    return float(match.group(0)) if match else fallback


def parse_font_px(element: ET.Element, ancestors: list[ET.Element]) -> float:
    for candidate in [element, *reversed(ancestors)]:
        style = candidate.attrib.get("style", "")
        match = re.search(r"font-size\s*:\s*(-?\d+(?:\.\d+)?)", style)
        if match:
            return float(match.group(1))
        if "font-size" in candidate.attrib:
            return parse_float(candidate.attrib.get("font-size"), 16.0)
    return 16.0


Matrix = tuple[float, float, float, float, float, float]


def multiply_matrix(left: Matrix, right: Matrix) -> Matrix:
    la, lb, lc, ld, le, lf = left
    ra, rb, rc, rd, re, rf = right
    return (
        la * ra + lc * rb,
        lb * ra + ld * rb,
        la * rc + lc * rd,
        lb * rc + ld * rd,
        la * re + lc * rf + le,
        lb * re + ld * rf + lf,
    )


def transform_point(matrix: Matrix, x: float, y: float) -> tuple[float, float]:
    a, b, c, d, e, f = matrix
    return a * x + c * y + e, b * x + d * y + f


def parse_transform(value: str | None) -> Matrix:
    matrix: Matrix = (1, 0, 0, 1, 0, 0)
    if not value:
        return matrix

    for name, raw_numbers in re.findall(r"(matrix|translate|scale|rotate)\(([^)]*)\)", value):
        numbers = [float(part) for part in re.findall(r"-?\d+(?:\.\d+)?(?:e[-+]?\d+)?", raw_numbers)]
        local: Matrix = (1, 0, 0, 1, 0, 0)
        if name == "matrix" and len(numbers) >= 6:
            local = (numbers[0], numbers[1], numbers[2], numbers[3], numbers[4], numbers[5])
        elif name == "translate":
            local = (1, 0, 0, 1, numbers[0] if numbers else 0, numbers[1] if len(numbers) > 1 else 0)
        elif name == "scale" and numbers:
            sx = numbers[0]
            sy = numbers[1] if len(numbers) > 1 else sx
            local = (sx, 0, 0, sy, 0, 0)
        elif name == "rotate" and numbers:
            import math

            angle = math.radians(numbers[0])
            cos_value = math.cos(angle)
            sin_value = math.sin(angle)
            rotation: Matrix = (cos_value, sin_value, -sin_value, cos_value, 0, 0)
            if len(numbers) >= 3:
                cx, cy = numbers[1], numbers[2]
                local = multiply_matrix(
                    multiply_matrix((1, 0, 0, 1, cx, cy), rotation),
                    (1, 0, 0, 1, -cx, -cy),
                )
            else:
                local = rotation
        matrix = multiply_matrix(matrix, local)
    return matrix


def text_content(element: ET.Element) -> str:
    text = "".join(element.itertext())
    return re.sub(r"\s+", " ", text).strip()


def tspan_offset(element: ET.Element, font_px: float) -> tuple[float, float]:
    for child in element.iter():
        if local_name(child) != "tspan":
            continue
        x = parse_float(child.attrib.get("x"), 0.0) if "x" in child.attrib else 0.0
        y = 0.0
        raw_y = child.attrib.get("y")
        if raw_y:
            y += parse_float(raw_y, 0.0) * (font_px if "em" in raw_y else 1.0)
        raw_dy = child.attrib.get("dy")
        if raw_dy:
            y += parse_float(raw_dy, 0.0) * (font_px if "em" in raw_dy else 1.0)
        return x, y
    return 0.0, 0.0


def label_color(element: ET.Element, ancestors: list[ET.Element]) -> str:
    tokens = set().union(*(class_tokens(candidate) for candidate in [element, *ancestors]))
    if tokens & {"node", "actor", "participant", "task", "taskText", "slice", "packetByte"}:
        return WHITE
    if tokens & {"axis", "legend", "tick", "title", "messageText", "labelText"}:
        return GRAY
    return WHITE if "label" in tokens else GRAY


def collect_text_labels(svg_path: Path) -> list[TextLabelSpec]:
    tree = ET.parse(svg_path)
    root = tree.getroot()
    labels: list[TextLabelSpec] = []

    def walk(element: ET.Element, matrix: Matrix, ancestors: list[ET.Element]) -> None:
        current_matrix = multiply_matrix(matrix, parse_transform(element.attrib.get("transform")))
        if local_name(element) == "text":
            content = text_content(element)
            if content:
                font_px = parse_font_px(element, ancestors)
                tspan_x, tspan_y = tspan_offset(element, font_px)
                x = parse_float(element.attrib.get("x"), 0.0) + tspan_x
                y = parse_float(element.attrib.get("y"), 0.0) + tspan_y
                point_x, point_y = transform_point(current_matrix, x, y)
                labels.append(
                    TextLabelSpec(
                        text=content,
                        x=point_x,
                        y=point_y,
                        font_size=font_px,
                        color=label_color(element, ancestors),
                        order=len(labels),
                    )
                )
        next_ancestors = [*ancestors, element]
        for child in list(element):
            walk(child, current_matrix, next_ancestors)

    walk(root, (1, 0, 0, 1, 0, 0), [])
    return labels[:90]


def svg_point_to_manim(x: float, y: float, view_box: SvgBox, target_height: float) -> tuple[float, float, float]:
    scale = target_height / view_box.height if view_box.height else 1.0
    manim_x = (x - (view_box.min_x + view_box.width / 2)) * scale
    manim_y = ((view_box.min_y + view_box.height / 2) - y) * scale - 0.18
    return manim_x, manim_y, 0


def build_text_actor(spec: TextLabelSpec, view_box: SvgBox, target_height: float) -> Text:
    scale = target_height / view_box.height if view_box.height else 1.0
    actor = Text(spec.text, font=TEXT_FONT, font_size=18, color=spec.color)
    desired_height = min(0.26, max(0.095, spec.font_size * scale * 0.95))
    actor.scale_to_fit_height(desired_height)
    if actor.width > 2.55:
        actor.scale_to_fit_width(2.55)
    actor.move_to(svg_point_to_manim(spec.x, spec.y, view_box, target_height))
    actor.set_z_index(6)
    return actor


def build_text_actors(svg_path: Path, target_height: float) -> list[Text]:
    view_box = parse_view_box(ET.parse(svg_path).getroot().attrib.get("viewBox"))
    return [build_text_actor(spec, view_box, target_height) for spec in collect_text_labels(svg_path)]


def build_title() -> VGroup:
    title = Text(f"Mermaid {diagram_title()} SVG", font=TEXT_FONT, font_size=31, color=GRAY)
    subtitle = Text("generated, decomposed, unfolded", font=TEXT_FONT, font_size=18, color=PRIMARY_BLUE)
    group = VGroup(title, subtitle).arrange(DOWN, buff=0.12)
    group.to_edge(UP, buff=0.42)
    return group


def target_height_for(svg_path: Path) -> float:
    view_box = parse_view_box(ET.parse(svg_path).getroot().attrib.get("viewBox"))
    if view_box.height <= 0 or view_box.width <= 0:
        return 5.75
    return min(5.95, 11.35 / (view_box.width / view_box.height))


def build_svg_actor(fragment: FragmentSpec, target_height: float) -> SVGMobject | None:
    try:
        actor = SVGMobject(str(fragment.path), height=target_height)
    except Exception:
        return None
    style_svg_actor(actor, fragment)
    hide_viewport_anchor(actor)
    actor.move_to(ORIGIN + DOWN * 0.18)
    actor.set_z_index(3)
    return actor


def hide_viewport_anchor(actor: SVGMobject) -> None:
    if not actor.submobjects:
        return
    anchor = actor.submobjects[0]
    anchor.set_fill(opacity=0)
    anchor.set_stroke(opacity=0)


def style_svg_actor(actor: SVGMobject, fragment: FragmentSpec) -> None:
    tokens = set(re.split(r"\s+", fragment.source_class.strip())) if fragment.source_class else set()
    key = fragment.key.lower()
    token_text = " ".join(tokens).lower()
    line_words = (
        "edge",
        "link",
        "line",
        "axis",
        "tick",
        "arrow",
        "grid",
        "message",
        "relationship",
        "path",
        "connector",
    )
    fill_words = (
        "bar",
        "block",
        "commit",
        "data-point",
        "node",
        "packet",
        "quadrant",
        "requirement",
        "section",
        "slice",
        "state",
        "task",
        "timeline",
        "treemap",
    )

    if any(word in token_text or word in key for word in line_words):
        actor.set_fill(opacity=0)
        actor.set_stroke(color=GRAY, width=2.2, opacity=1)
        return

    color = PALETTE[fragment.order % len(PALETTE)]
    if any(word in token_text or word in key for word in fill_words):
        actor.set_fill(color=color, opacity=0.96)
        actor.set_stroke(color=color, width=1.8, opacity=1)
    else:
        actor.set_fill(color=color, opacity=0.9)
        actor.set_stroke(color=GRAY, width=1.5, opacity=1)


def build_png_fallback(png_path: Path, target_height: float) -> ImageMobject:
    image = ImageMobject(str(png_path))
    image.scale_to_fit_height(target_height)
    if image.width > 11.35:
        image.scale_to_fit_width(11.35)
    image.move_to(ORIGIN + DOWN * 0.18)
    image.set_z_index(2)
    return image


def batch_items(items: list[SVGMobject], max_batches: int = 9) -> list[list[SVGMobject]]:
    if not items:
        return []
    batch_count = min(max_batches, max(1, len(items)))
    batches = [[] for _ in range(batch_count)]
    for index, item in enumerate(items):
        batches[index % batch_count].append(item)
    return [batch for batch in batches if batch]


class MermaidSvgUnfoldScene(Scene):
    def construct(self) -> None:
        self.camera.background_color = PAGE_BACKGROUND
        poster_mode = env_value("SPIKE_RENDER_TARGET") == "poster"
        force_assets = env_value("SPIKE_FORCE_MERMAID") == "1"

        svg_path, png_path = ensure_mermaid_assets(force=force_assets)
        fragments = ensure_fragments(svg_path, force=force_assets)
        target_height = target_height_for(svg_path)
        actors = [actor for fragment in fragments if (actor := build_svg_actor(fragment, target_height)) is not None]

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
        title = build_title()

        if not actors:
            actors = [build_png_fallback(png_path, target_height)]
        actors.extend(build_text_actors(svg_path, target_height))

        final_group = Group(*actors)
        if poster_mode:
            self.add(stage, title, final_group)
            return

        self.add(stage, title)
        self.wait(2.7)

        elapsed = 2.7
        for batch in batch_items(actors):
            self.play(
                LaggedStart(*[FadeIn(actor, shift=UP * 0.05) for actor in batch], lag_ratio=0.14),
                run_time=1.12,
                rate_func=rate_functions.ease_out_cubic,
            )
            self.wait(0.35)
            elapsed += 1.47

        pulse = Circle(radius=0.18, stroke_width=0, fill_color=PRIMARY_RED, fill_opacity=0.82)
        pulse.move_to(ORIGIN + DOWN * 0.18)
        pulse.set_z_index(8)
        self.play(FadeIn(pulse, scale=0.7), run_time=0.24)
        self.play(
            pulse.animate.scale(5.8).set_fill(PRIMARY_RED, opacity=0),
            final_group.animate.scale(1.01),
            run_time=1.0,
            rate_func=rate_functions.ease_out_cubic,
        )
        self.remove(pulse)
        self.play(final_group.animate.scale(1 / 1.01), run_time=0.32)
        elapsed += 1.56
        self.wait(max(7.0, 25.5 - elapsed))


def render_variant(args: _Args) -> None:
    ensure_mermaid_assets(force=args.force_mermaid)
    ensure_fragments(generated_dir() / "diagram.svg", force=args.force_mermaid)
    if args.assets_only:
        return

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
