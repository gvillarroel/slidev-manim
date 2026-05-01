#!/usr/bin/env -S uv run --script
# /// script
# dependencies = [
#   "manim>=0.20.0",
# ]
# ///

from __future__ import annotations

import argparse
import hashlib
import json
import os
import shutil
import subprocess
import sys
import textwrap
from dataclasses import dataclass
from pathlib import Path

from manim import (
    DOWN,
    LEFT,
    ORIGIN,
    RIGHT,
    UP,
    AnimationGroup,
    FadeIn,
    FadeOut,
    Group,
    ImageMobject,
    Rectangle,
    Scene,
    Text,
    VGroup,
    smooth,
)

SPIKE_DIR = Path(__file__).resolve().parent
REPO_ROOT = SPIKE_DIR.parent.parent
SPIKE_NAME = SPIKE_DIR.name
OUTPUT_DIR = REPO_ROOT / "videos" / SPIKE_NAME
STAGING_DIR = OUTPUT_DIR / ".manim"
GENERATED_DIR = OUTPUT_DIR / ".generated"
MANIFEST_PATH = GENERATED_DIR / "manifest.json"

MERMAID_PACKAGE = "@mermaid-js/mermaid-cli@11.14.0"

PRIMARY_RED = "#9e1b32"
PRIMARY_ORANGE = "#e77204"
PRIMARY_GREEN = "#45842a"
PRIMARY_BLUE = "#007298"
PRIMARY_PURPLE = "#652f6c"
WHITE = "#ffffff"
GRAY = "#333e48"
GRAY_100 = "#e7e7e7"
GRAY_200 = "#cfcfcf"
GRAY_600 = "#696969"
PAGE_BACKGROUND = "#f7f7f7"
TEXT_FONT = "Arial"


@dataclass(frozen=True)
class DiagramSpec:
    key: str
    title: str
    family: str
    source: str


@dataclass(frozen=True)
class RenderedDiagram:
    spec: DiagramSpec
    mmd_path: Path
    svg_path: Path
    png_path: Path


class _Args(argparse.Namespace):
    quality: str
    force_assets: bool


DIAGRAM_SPECS: tuple[DiagramSpec, ...] = (
    DiagramSpec(
        "flowchart",
        "Flowchart",
        "Core",
        """
        flowchart LR
            A[Input] --> B{Route}
            B --> C[Output]
            B --> D[Review]
        """,
    ),
    DiagramSpec(
        "sequence",
        "Sequence",
        "Core",
        """
        sequenceDiagram
            participant Client
            participant API
            Client->>API: Request
            API-->>Client: Response
        """,
    ),
    DiagramSpec(
        "class",
        "Class",
        "UML",
        """
        classDiagram
            Animal <|-- Dog
            class Animal {
              +String name
              +move()
            }
            class Dog {
              +bark()
            }
        """,
    ),
    DiagramSpec(
        "state",
        "State",
        "UML",
        """
        stateDiagram-v2
            [*] --> Draft
            Draft --> Review
            Review --> Published
            Published --> [*]
        """,
    ),
    DiagramSpec(
        "er",
        "Entity Relationship",
        "Data",
        """
        erDiagram
            CUSTOMER ||--o{ ORDER : places
            ORDER ||--|{ LINE_ITEM : contains
            CUSTOMER {
              string name
            }
            ORDER {
              int id
            }
        """,
    ),
    DiagramSpec(
        "journey",
        "User Journey",
        "Process",
        """
        journey
            title Checkout
            section Browse
              Find item: 5: User
            section Buy
              Pay: 3: User, System
        """,
    ),
    DiagramSpec(
        "gantt",
        "Gantt",
        "Process",
        """
        gantt
            title Render plan
            dateFormat  YYYY-MM-DD
            section Build
            Spec       :a1, 2026-01-01, 3d
            Render     :after a1, 4d
            Review     :after a1, 2d
        """,
    ),
    DiagramSpec(
        "pie",
        "Pie",
        "Chart",
        """
        pie showData
            title Diagram mix
            "Structure" : 35
            "Charts" : 25
            "Process" : 40
        """,
    ),
    DiagramSpec(
        "quadrant",
        "Quadrant",
        "Chart",
        """
        quadrantChart
            title Diagram fit
            x-axis Low Effort --> High Effort
            y-axis Low Impact --> High Impact
            quadrant-1 Invest
            quadrant-2 Consider
            quadrant-3 Avoid
            quadrant-4 Maintain
            Mermaid: [0.72, 0.82]
            Manual: [0.28, 0.42]
        """,
    ),
    DiagramSpec(
        "requirement",
        "Requirement",
        "Model",
        """
        requirementDiagram
            requirement render_req {
              id: 1
              text: Render all diagram types
              risk: medium
              verifymethod: test
            }
            element video {
              type: file
            }
            video - satisfies -> render_req
        """,
    ),
    DiagramSpec(
        "gitgraph",
        "GitGraph",
        "Developer",
        """
        gitGraph
            commit id: "init"
            branch feature
            checkout feature
            commit id: "diagram"
            checkout main
            merge feature
            commit id: "video"
        """,
    ),
    DiagramSpec(
        "c4",
        "C4",
        "Architecture",
        """
        C4Context
            title System Context
            Person(user, "Viewer")
            System(app, "Manim Video")
            Rel(user, app, "watches")
        """,
    ),
    DiagramSpec(
        "mindmap",
        "Mindmap",
        "Structure",
        """
        mindmap
          root((Mermaid))
            Graphs
              Flowchart
              Sequence
            Charts
              Pie
              Sankey
        """,
    ),
    DiagramSpec(
        "timeline",
        "Timeline",
        "Process",
        """
        timeline
            title Render path
            Mermaid source : mmd files
            CLI : svg and png
            Manim : gallery video
        """,
    ),
    DiagramSpec(
        "zenuml",
        "ZenUML",
        "Sequence",
        """
        zenuml
            title Auth
            Client->API.login() {
              API->DB.query()
            }
        """,
    ),
    DiagramSpec(
        "sankey",
        "Sankey",
        "Chart",
        """
        sankey-beta
            Source,SVG,5
            SVG,Video,4
            Source,PNG,3
            PNG,Video,3
        """,
    ),
    DiagramSpec(
        "xychart",
        "XY Chart",
        "Chart",
        """
        xychart-beta
            title "Coverage"
            x-axis ["Flow", "UML", "Chart", "New"]
            y-axis "Count" 0 --> 10
            bar [4, 6, 8, 5]
            line [3, 5, 7, 9]
        """,
    ),
    DiagramSpec(
        "block",
        "Block",
        "Structure",
        """
        block-beta
            columns 3
            source["MMD"] space svg["SVG"]
            space video["Video"] space
            source --> svg
            svg --> video
        """,
    ),
    DiagramSpec(
        "packet",
        "Packet",
        "Data",
        """
        packet
            0-3: "Version"
            4-7: "Type"
            8-15: "Length"
            16-31: "Payload"
        """,
    ),
    DiagramSpec(
        "kanban",
        "Kanban",
        "Process",
        """
        kanban
            todo[Todo]
              docs[Write docs]
            doing[Doing]
              render[Render video]
            done[Done]
              review[Review frames]
        """,
    ),
    DiagramSpec(
        "architecture",
        "Architecture",
        "Architecture",
        """
        architecture-beta
            group api(cloud)[API]
            service db(database)[Database] in api
            service server(server)[Server] in api
            db:R --> L:server
        """,
    ),
    DiagramSpec(
        "radar",
        "Radar",
        "Chart",
        """
        radar-beta
            title Capabilities
            axis Speed, Quality, Coverage, Clarity
            curve Mermaid{4,3,5,4}
            curve Manim{3,5,4,5}
        """,
    ),
    DiagramSpec(
        "treemap",
        "Treemap",
        "Chart",
        """
        treemap-beta
            "Mermaid"
                "Core": 10
                "Charts": 8
            "Manim"
                "Video": 12
                "Review": 5
        """,
    ),
    DiagramSpec(
        "venn",
        "Venn",
        "Chart",
        """
        venn-beta
            title "Overlap"
            set Docs["Docs"]:10
            set Video["Video"]:10
            union Docs,Video["Shared"]:4
        """,
    ),
    DiagramSpec(
        "ishikawa",
        "Ishikawa",
        "Analysis",
        """
        ishikawa-beta
            Video quality
                Mermaid source
                    all types
                Rendering
                    mmdc
                    Manim
                Review
                    frames
        """,
    ),
    DiagramSpec(
        "treeview",
        "TreeView",
        "Structure",
        """
        treeView-beta
            "spikes"
                "diagram.mmd"
                "main.py"
            "videos"
                "gallery.webm"
        """,
    ),
)


def parse_args() -> _Args:
    parser = argparse.ArgumentParser(description="Render the mermaid-all-diagram-types spike.")
    parser.add_argument("--quality", choices=("low", "medium", "high", "production", "4k"), default="medium")
    parser.add_argument("--force-assets", action="store_true", help="Regenerate Mermaid assets even if cached.")
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
        command.extend(["--format", "webm"])
    command.extend([str(Path(__file__).resolve()), "MermaidAllDiagramTypesScene"])
    return command


def promote(target_name: str, destination: Path) -> None:
    matches = sorted(STAGING_DIR.glob(f"**/{target_name}"), key=lambda path: path.stat().st_mtime)
    if not matches:
        raise FileNotFoundError(f"Could not find {target_name} under {STAGING_DIR}")
    destination.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(matches[-1], destination)


def normalized_source(source: str) -> str:
    return textwrap.dedent(source).strip() + "\n"


def source_hash(spec: DiagramSpec) -> str:
    digest = hashlib.sha256()
    digest.update(MERMAID_PACKAGE.encode("utf-8"))
    digest.update(b"\n")
    digest.update(normalized_source(spec.source).encode("utf-8"))
    return digest.hexdigest()


def read_manifest() -> dict[str, dict[str, str]]:
    if not MANIFEST_PATH.exists():
        return {}
    return json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))


def write_manifest(manifest: dict[str, dict[str, str]]) -> None:
    MANIFEST_PATH.parent.mkdir(parents=True, exist_ok=True)
    MANIFEST_PATH.write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8")


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


def render_asset(input_path: Path, output_path: Path) -> None:
    result = subprocess.run(
        mermaid_command(input_path, output_path),
        cwd=str(REPO_ROOT),
        capture_output=True,
        text=True,
        check=False,
    )
    if result.returncode != 0:
        raise RuntimeError(
            f"Mermaid render failed for {input_path.name} -> {output_path.name}\n"
            f"stdout:\n{result.stdout}\n\nstderr:\n{result.stderr}"
        )


def ensure_mermaid_assets(*, force: bool) -> list[RenderedDiagram]:
    GENERATED_DIR.mkdir(parents=True, exist_ok=True)
    manifest = read_manifest()
    rendered: list[RenderedDiagram] = []

    for spec in DIAGRAM_SPECS:
        mmd_path = GENERATED_DIR / f"{spec.key}.mmd"
        svg_path = GENERATED_DIR / f"{spec.key}.svg"
        png_path = GENERATED_DIR / f"{spec.key}.png"
        source = normalized_source(spec.source)
        current_hash = source_hash(spec)
        cached = manifest.get(spec.key, {}).get("hash") == current_hash

        if not mmd_path.exists() or mmd_path.read_text(encoding="utf-8", errors="ignore") != source:
            mmd_path.write_text(source, encoding="utf-8")
            cached = False

        if force or not cached or not svg_path.exists() or not png_path.exists():
            render_asset(mmd_path, svg_path)
            render_asset(mmd_path, png_path)
            manifest[spec.key] = {
                "hash": current_hash,
                "title": spec.title,
                "family": spec.family,
                "package": MERMAID_PACKAGE,
            }

        rendered.append(RenderedDiagram(spec=spec, mmd_path=mmd_path, svg_path=svg_path, png_path=png_path))

    write_manifest(manifest)
    return rendered


def chunked(items: list[RenderedDiagram], size: int) -> list[list[RenderedDiagram]]:
    return [items[index : index + size] for index in range(0, len(items), size)]


def fit_text(label: Text, max_width: float, max_height: float | None = None) -> Text:
    if label.width > max_width:
        label.scale_to_fit_width(max_width)
    if max_height is not None and label.height > max_height:
        label.scale_to_fit_height(max_height)
    return label


def build_title() -> VGroup:
    title = Text("Mermaid diagram types", font=TEXT_FONT, font_size=34, color=GRAY)
    count = Text(f"{len(DIAGRAM_SPECS)} syntax families rendered by Mermaid CLI 11.14.0", font=TEXT_FONT, font_size=21, color=GRAY_600)
    group = VGroup(title, count).arrange(DOWN, buff=0.12)
    group.to_edge(UP, buff=0.48)
    return group


def image_for(path: Path, max_width: float, max_height: float) -> ImageMobject:
    image = ImageMobject(str(path))
    image.scale_to_fit_width(max_width)
    if image.height > max_height:
        image.scale_to_fit_height(max_height)
    return image


def diagram_card(diagram: RenderedDiagram, width: float, height: float) -> Group:
    outer = Rectangle(width=width, height=height, stroke_color=GRAY_200, stroke_width=1.4, fill_color=WHITE, fill_opacity=1)
    header = Rectangle(width=width, height=0.38, stroke_width=0, fill_color=GRAY_100, fill_opacity=1)
    header.align_to(outer, UP)
    title = fit_text(Text(diagram.spec.title, font=TEXT_FONT, font_size=17, color=GRAY), width - 0.36, 0.24)
    title.move_to(header)

    family = fit_text(Text(diagram.spec.family, font=TEXT_FONT, font_size=12, color=PRIMARY_BLUE), 1.4, 0.18)
    family.move_to(header.get_right() + LEFT * 0.55)

    preview = image_for(diagram.png_path, width - 0.46, height - 0.82)
    preview.move_to(outer.get_center() + DOWN * 0.18)

    return Group(outer, header, preview, title, family)


def page_grid(diagrams: list[RenderedDiagram], page_index: int, total_pages: int) -> Group:
    card_width = 5.28
    card_height = 2.47
    positions = [
        LEFT * 2.82 + UP * 0.74,
        RIGHT * 2.82 + UP * 0.74,
        LEFT * 2.82 + DOWN * 2.05,
        RIGHT * 2.82 + DOWN * 2.05,
    ]
    cards = Group()
    for diagram, position in zip(diagrams, positions):
        cards.add(diagram_card(diagram, card_width, card_height).move_to(position))

    page_label = Text(f"{page_index + 1}/{total_pages}", font=TEXT_FONT, font_size=16, color=PRIMARY_RED)
    page_label.to_edge(DOWN, buff=0.52)
    return Group(cards, page_label)


def poster_grid(diagrams: list[RenderedDiagram]) -> Group:
    cell_width = 2.04
    cell_height = 1.24
    cols = 6
    start_x = -5.15
    start_y = 2.25
    cells = Group()
    for index, diagram in enumerate(diagrams):
        row = index // cols
        col = index % cols
        x = start_x + col * cell_width
        y = start_y - row * cell_height
        tile = Rectangle(width=1.84, height=1.05, stroke_color=GRAY_200, stroke_width=1, fill_color=WHITE, fill_opacity=1)
        image = image_for(diagram.png_path, 1.58, 0.62)
        image.move_to(tile.get_center() + UP * 0.09)
        label = fit_text(Text(diagram.spec.title, font=TEXT_FONT, font_size=10, color=GRAY), 1.58, 0.13)
        label.move_to(tile.get_bottom() + UP * 0.14)
        cells.add(Group(tile, image, label).move_to(ORIGIN + RIGHT * x + UP * y))
    return cells


class MermaidAllDiagramTypesScene(Scene):
    def construct(self) -> None:
        self.camera.background_color = WHITE
        poster_mode = os.environ.get("SPIKE_RENDER_TARGET") == "poster"
        force_assets = os.environ.get("SPIKE_FORCE_ASSETS") == "1"

        rendered = ensure_mermaid_assets(force=force_assets)
        title = build_title()
        stage = Rectangle(
            width=12.0,
            height=6.35,
            stroke_color=GRAY_200,
            stroke_width=2,
            fill_color=PAGE_BACKGROUND,
            fill_opacity=1,
        )
        stage.move_to(DOWN * 0.04)

        if poster_mode:
            poster_title = build_title()
            poster_title.scale(0.82).to_edge(UP, buff=0.24)
            self.add(stage, poster_title, poster_grid(rendered))
            return

        pages = chunked(rendered, 4)
        self.add(stage, title)
        self.wait(2.5)

        active_page: Group | None = None
        total_pages = len(pages)
        for page_index, diagrams in enumerate(pages):
            page = page_grid(diagrams, page_index, total_pages)
            if active_page is None:
                self.play(FadeIn(page, shift=UP * 0.12), run_time=0.85, rate_func=smooth)
            else:
                self.play(
                    AnimationGroup(
                        FadeOut(active_page, shift=LEFT * 0.28),
                        FadeIn(page, shift=RIGHT * 0.28),
                        lag_ratio=0.0,
                    ),
                    run_time=0.7,
                    rate_func=smooth,
                )
            active_page = page
            self.wait(3.45)

        final_note = Text("All listed types produced Mermaid CLI assets", font=TEXT_FONT, font_size=22, color=PRIMARY_RED)
        final_note.to_edge(DOWN, buff=0.52)
        if active_page is not None:
            self.play(FadeOut(active_page[1]), FadeIn(final_note, shift=UP * 0.08), run_time=0.65, rate_func=smooth)
        self.wait(6.5)


def render_variant(args: _Args) -> None:
    video_path, poster_path = output_paths()

    video_env = os.environ.copy()
    video_env["SPIKE_RENDER_TARGET"] = "video"
    video_env["SPIKE_FORCE_ASSETS"] = "1" if args.force_assets else "0"
    result = subprocess.run(render_command(args, video_path.stem, poster=False), check=False, env=video_env)
    if result.returncode != 0:
        raise SystemExit(result.returncode)
    promote(video_path.name, video_path)

    poster_env = os.environ.copy()
    poster_env["SPIKE_RENDER_TARGET"] = "poster"
    poster_env["SPIKE_FORCE_ASSETS"] = "0"
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
