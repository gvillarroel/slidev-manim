#!/usr/bin/env -S uv run --script
# /// script
# dependencies = [
#   "manim>=0.20.0",
# ]
# ///

from __future__ import annotations

import argparse
import math
import os
import shutil
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path

import numpy as np
from manim import (
    DOWN,
    LEFT,
    RIGHT,
    UP,
    Circle,
    FadeIn,
    FadeOut,
    LaggedStart,
    Rectangle,
    Scene,
    Text,
    VGroup,
    rate_functions,
)
from manimpango import list_fonts

SPIKE_DIR = Path(__file__).resolve().parent
REPO_ROOT = SPIKE_DIR.parent.parent
SPIKE_NAME = SPIKE_DIR.name
OUTPUT_DIR = REPO_ROOT / "videos" / SPIKE_NAME
STAGING_DIR = OUTPUT_DIR / ".manim"
VIDEO_PATH = OUTPUT_DIR / f"{SPIKE_NAME}.webm"
POSTER_PATH = OUTPUT_DIR / f"{SPIKE_NAME}.png"

PRIMARY_RED = "#9e1b32"
WHITE = "#ffffff"
GRAY = "#333e48"
GRAY_100 = "#e7e7e7"
GRAY_200 = "#cfcfcf"
GRAY_300 = "#b5b5b5"
GRAY_400 = "#9c9c9c"
GRAY_500 = "#828282"
GRAY_600 = "#696969"
GRAY_700 = "#4f4f4f"
GRAY_800 = "#363636"
PAGE_BACKGROUND = "#f7f7f7"

DEFAULT_ROOT_TEXT = "Generator"
DEFAULT_MAP = "Input text:prompt,context;Idea groups:themes,clusters;Branch logic:routes,weights;Review loop:frames,audit"
CATEGORY_FILLS = (GRAY_800, GRAY_700, GRAY_600, GRAY, GRAY_500)
FONT_FAMILY = "Open Sans" if "Open Sans" in list_fonts() else "Arial"


@dataclass(frozen=True)
class CategorySpec:
    label: str
    children: tuple[str, ...]


@dataclass(frozen=True)
class CategoryLayout:
    spec: CategorySpec
    center: object
    color: str
    angle: float
    child_centers: tuple[object, ...]


class _Args(argparse.Namespace):
    quality: str
    preview: bool
    root_text: str
    branches: str


def parse_args() -> _Args:
    parser = argparse.ArgumentParser(description="Render the mind-map-branching Manim spike.")
    parser.add_argument(
        "--quality",
        choices=("low", "medium", "high", "production", "4k"),
        default="medium",
        help="Manim quality preset. Defaults to medium for presentation review.",
    )
    parser.add_argument("--preview", action="store_true", help="Open the rendered output after rendering.")
    parser.add_argument(
        "--root-text",
        default=DEFAULT_ROOT_TEXT,
        help="Text shown in the source box.",
    )
    parser.add_argument(
        "--branches",
        default=DEFAULT_MAP,
        help='Tree spec like "Category:child,child;Category:child,child". Use three to five categories.',
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


def render_command(args: _Args, poster: bool) -> list[str]:
    STAGING_DIR.mkdir(parents=True, exist_ok=True)
    target = POSTER_PATH if poster else VIDEO_PATH
    command = [
        sys.executable,
        "-m",
        "manim",
        "render",
        quality_flag(args.quality),
        "-r",
        "1600,900",
        "-o",
        target.stem,
        "--media_dir",
        str(STAGING_DIR),
    ]
    if poster:
        command.append("-s")
    else:
        command.extend(["--format", "webm", "-t"])
    if args.preview:
        command.append("-p")
    command.extend([str(Path(__file__).resolve()), "MindMapBranchingScene"])
    return command


def promote_rendered_file(target_name: str, destination: Path) -> None:
    matches = sorted(STAGING_DIR.glob(f"**/{target_name}"))
    if not matches:
        raise FileNotFoundError(f"Could not find {target_name} under {STAGING_DIR}")
    destination.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(max(matches, key=lambda path: path.stat().st_mtime), destination)


def clean_labels(raw: str) -> list[str]:
    labels = [label.strip() for label in raw.split(",") if label.strip()]
    if len(labels) < 3:
        labels = ["Input text", "Idea groups", "Branch logic", "Review loop"]
    return labels[:5]


def split_child_labels(raw: str) -> tuple[str, ...]:
    labels = [label.strip() for label in raw.replace("|", ",").split(",") if label.strip()]
    return tuple(labels[:3]) or ("source", "result")


def clean_tree(raw: str) -> list[CategorySpec]:
    entries = [entry.strip() for entry in raw.split(";") if entry.strip()]
    categories: list[CategorySpec] = []
    for entry in entries:
        if ":" not in entry:
            continue
        label, children = entry.split(":", 1)
        label = label.strip()
        if label:
            categories.append(CategorySpec(label=label, children=split_child_labels(children)))

    if len(categories) >= 3:
        return categories[:5]

    return [
        CategorySpec(label=label, children=("source", "result"))
        for label in clean_labels(raw)
    ]


def scene_root_text() -> str:
    return os.environ.get("MIND_MAP_ROOT_TEXT", DEFAULT_ROOT_TEXT).strip() or DEFAULT_ROOT_TEXT


def scene_categories() -> list[CategorySpec]:
    return clean_tree(os.environ.get("MIND_MAP_BRANCHES", DEFAULT_MAP))


def label_text(value: str, size: int, color: str = WHITE, weight: str | None = "BOLD") -> Text:
    kwargs = {"font": FONT_FAMILY, "font_size": size, "color": color}
    if weight is not None:
        kwargs["weight"] = weight
    return Text(value, **kwargs)


def text_box(
    label: str,
    width: float,
    height: float,
    fill: str,
    text_color: str = WHITE,
    stroke: str | None = None,
    font_size: int = 27,
    weight: str | None = "BOLD",
) -> VGroup:
    box = Rectangle(
        width=width,
        height=height,
        stroke_color=stroke or fill,
        stroke_width=2,
        fill_color=fill,
        fill_opacity=1,
    )
    text = label_text(label, font_size, color=text_color, weight=weight)
    if text.width > box.width - 0.34:
        text.scale_to_fit_width(box.width - 0.34)
    if text.height > box.height - 0.2:
        text.scale_to_fit_height(box.height - 0.2)
    text.move_to(box.get_center())
    box.set_z_index(4)
    text.set_z_index(5)
    return VGroup(box, text)


def slot_box(width: float, height: float, center: object, opacity: float = 0.42) -> Rectangle:
    slot = Rectangle(
        width=width,
        height=height,
        stroke_color=GRAY_600,
        stroke_width=0,
        fill_color=GRAY_100,
        fill_opacity=opacity,
    )
    slot.move_to(center)
    slot.set_z_index(0)
    return slot


def category_layouts(categories: list[CategorySpec]) -> list[CategoryLayout]:
    count = len(categories)
    y_top = 2.25
    y_bottom = -2.25
    y_step = 0 if count == 1 else (y_top - y_bottom) / (count - 1)
    layouts: list[CategoryLayout] = []
    for index, spec in enumerate(categories):
        y = y_top - index * y_step
        angle = 0.18 if y > 0.35 else -0.18 if y < -0.35 else 0
        child_count = len(spec.children)
        child_gap = 0.45 if child_count > 2 else 0.54
        child_top = y + (child_count - 1) * child_gap / 2
        child_centers = tuple(
            RIGHT * 3.35 + UP * (child_top - child_index * child_gap)
            for child_index in range(child_count)
        )
        layouts.append(
            CategoryLayout(
                spec=spec,
                center=RIGHT * -0.42 + UP * y,
                color=CATEGORY_FILLS[index % len(CATEGORY_FILLS)],
                angle=angle,
                child_centers=child_centers,
            )
        )
    return layouts


def balanced_reveal_order(count: int) -> list[int]:
    return {
        3: [0, 2, 1],
        4: [0, 3, 1, 2],
        5: [0, 4, 2, 1, 3],
    }[count]


def normal_for(start: object, end: object) -> object:
    delta = np.array(end) - np.array(start)
    length = math.hypot(float(delta[0]), float(delta[1]))
    if length < 0.001:
        return UP * 0
    return np.array([-delta[1] / length, delta[0] / length, 0])


def growth_point(start: object, end: object, bend: float, t: float) -> object:
    start_point = np.array(start)
    end_point = np.array(end)
    control = (start_point + end_point) / 2 + normal_for(start_point, end_point) * bend
    return ((1 - t) ** 2) * start_point + 2 * (1 - t) * t * control + (t**2) * end_point


def growth_cells(
    start: object,
    end: object,
    bend: float,
    count: int,
    color: str,
    opacity: float,
    base_radius: float,
    z_index: int,
) -> VGroup:
    cells = VGroup()
    route_normal = normal_for(start, end)
    for index in range(count):
        t = (index + 1) / (count + 1)
        radius = base_radius * (0.74 + 0.28 * math.sin((index + 1) * 1.7) ** 2)
        jitter = route_normal * (0.035 * math.sin(index * 2.23 + count))
        cell = Circle(radius=radius, stroke_width=0, fill_color=color, fill_opacity=opacity)
        cell.move_to(growth_point(start, end, bend, t) + jitter)
        cell.set_z_index(z_index)
        cells.add(cell)
    return cells


def bloom_cell(center: object, radius: float, color: str, opacity: float, z_index: int) -> Circle:
    cell = Circle(radius=radius, stroke_width=0, fill_color=color, fill_opacity=opacity)
    cell.move_to(center)
    cell.set_z_index(z_index)
    return cell


class MindMapBranchingScene(Scene):
    def construct(self) -> None:
        self.camera.background_color = PAGE_BACKGROUND

        stage = Rectangle(width=12.8, height=7.15, stroke_width=0, fill_color=PAGE_BACKGROUND, fill_opacity=0.96)
        stage.set_z_index(-10)
        stage_border = Rectangle(
            width=12.34,
            height=6.62,
            stroke_color=GRAY_200,
            stroke_width=2,
            fill_opacity=0,
        )
        stage_border.set_z_index(-8)

        root = text_box(scene_root_text(), 2.46, 0.88, PRIMARY_RED, font_size=28)
        root.move_to(LEFT * 4.46)
        root.set_z_index(4)

        hub = Circle(radius=0.075, stroke_width=0, fill_color=PRIMARY_RED, fill_opacity=1)
        hub.move_to(root.get_right() + RIGHT * 0.14)
        hub.set_z_index(6)

        layouts = category_layouts(scene_categories())
        start = root.get_right() + RIGHT * 0.22
        category_slots = VGroup(*[slot_box(1.86, 0.58, layout.center, opacity=0.4) for layout in layouts])
        child_slots = VGroup(
            *[
                slot_box(1.28, 0.34, center, opacity=0.26)
                for layout in layouts
                for center in layout.child_centers
            ]
        )
        pending_guides = VGroup()
        pending_child_guides = VGroup()
        for layout in layouts:
            pending_end = layout.center + LEFT * 0.96
            pending = growth_cells(start, pending_end, layout.angle * 2.6, 9, GRAY_300, 0.32, 0.018, -1)
            pending_guides.add(pending)
            for child_center in layout.child_centers:
                child_pending = growth_cells(
                    layout.center + RIGHT * 0.98,
                    child_center + LEFT * 0.7,
                    0.08,
                    5,
                    GRAY_300,
                    0.18,
                    0.012,
                    -2,
                )
                pending_child_guides.add(child_pending)
        root_focus = VGroup()
        focus_center = hub.get_center()
        for index in range(12):
            angle = -math.pi * 0.66 + index * math.pi * 1.32 / 11
            radius = 0.22 + 0.035 * math.sin(index * 1.9) ** 2
            cell = bloom_cell(
                focus_center + np.array([math.cos(angle) * radius, math.sin(angle) * radius, 0]),
                0.025 + 0.006 * (index % 3),
                PRIMARY_RED,
                0.82,
                6,
            )
            root_focus.add(cell)

        self.add(stage, stage_border, pending_guides, pending_child_guides, category_slots, child_slots, root, hub)
        self.wait(2.8)
        self.play(
            LaggedStart(*[FadeIn(cell, scale=0.35) for cell in root_focus], lag_ratio=0.04),
            hub.animate.scale(1.55),
            root.animate.scale(1.012),
            run_time=0.55,
            rate_func=rate_functions.ease_out_cubic,
        )
        self.play(
            *[
                cell.animate.move_to(focus_center + (cell.get_center() - focus_center) * 1.45).set_fill(
                    PRIMARY_RED,
                    opacity=0,
                )
                for cell in root_focus
            ],
            hub.animate.scale(1 / 1.55),
            root.animate.scale(1 / 1.012),
            run_time=0.55,
            rate_func=rate_functions.ease_out_cubic,
        )
        self.remove(root_focus)

        guides = VGroup()
        child_guides = VGroup()
        visible_nodes = VGroup()
        category_cards: list[VGroup | None] = [None for _ in layouts]
        for index in balanced_reveal_order(len(layouts)):
            layout = layouts[index]
            category_card = text_box(layout.spec.label, 1.86, 0.58, layout.color, font_size=20)
            category_card.move_to(layout.center)
            category_card.set_z_index(4)

            end = category_card.get_left() + LEFT * 0.03
            active_cells = growth_cells(start, end, layout.angle * 2.6, 13, PRIMARY_RED, 0.92, 0.038, 2)
            bud = bloom_cell(end, 0.095, PRIMARY_RED, 1, 6)
            guides.add(active_cells)

            self.play(
                FadeOut(pending_guides[index]),
                LaggedStart(*[FadeIn(cell, scale=0.35) for cell in active_cells], lag_ratio=0.08),
                FadeIn(bud, scale=0.55),
                run_time=1.1,
                rate_func=rate_functions.ease_out_cubic,
            )
            self.play(
                FadeOut(bud, scale=1.45),
                FadeIn(category_card[0], scale=0.82),
                *[cell.animate.set_fill(GRAY_400, opacity=0.36).scale(0.72) for cell in active_cells],
                FadeOut(category_slots[index]),
                run_time=0.68,
                rate_func=rate_functions.ease_out_cubic,
            )
            self.play(
                FadeIn(category_card[1], shift=RIGHT * 0.05),
                run_time=0.34,
            )
            visible_nodes.add(category_card)
            category_cards[index] = category_card
            self.wait(0.28)

        self.wait(0.5)
        for index in balanced_reveal_order(len(layouts)):
            layout = layouts[index]
            category_card = category_cards[index]
            if category_card is None:
                continue
            child_slot_base = sum(len(previous.spec.children) for previous in layouts[:index])
            for child_index, child_label in enumerate(layout.spec.children):
                child_center = layout.child_centers[child_index]
                child_card = text_box(
                    child_label,
                    1.28,
                    0.34,
                    WHITE,
                    text_color=GRAY,
                    stroke=layout.color,
                    font_size=15,
                    weight=None,
                )
                child_card.move_to(child_center)
                child_card[0].set_stroke(layout.color, width=1.6, opacity=0.72)
                child_card[0].set_fill(GRAY_100, opacity=0.98)
                child_card.set_z_index(4)

                child_start = category_card.get_right() + RIGHT * 0.04
                child_end = child_card.get_left() + LEFT * 0.03
                child_cells = growth_cells(
                    child_start,
                    child_end,
                    0.08 if child_index % 2 == 0 else -0.08,
                    6,
                    PRIMARY_RED,
                    0.86,
                    0.024,
                    2,
                )
                child_guides.add(child_cells)
                child_bud = bloom_cell(child_end, 0.055, PRIMARY_RED, 1, 6)

                self.play(
                    FadeOut(pending_child_guides[child_slot_base + child_index]),
                    LaggedStart(*[FadeIn(cell, scale=0.35) for cell in child_cells], lag_ratio=0.08),
                    FadeIn(child_bud, scale=0.55),
                    FadeOut(child_slots[child_slot_base + child_index]),
                    run_time=0.48,
                    rate_func=rate_functions.ease_in_out_cubic,
                )
                self.play(
                    FadeOut(child_bud, scale=1.45),
                    FadeIn(child_card[0], scale=0.82),
                    *[cell.animate.set_fill(GRAY_300, opacity=0.3).scale(0.7) for cell in child_cells],
                    run_time=0.32,
                    rate_func=rate_functions.ease_out_cubic,
                )
                self.play(FadeIn(child_card[1], shift=RIGHT * 0.04), run_time=0.22)
                visible_nodes.add(child_card)
            self.wait(0.18)

        center_pulse = Circle(radius=0.16, stroke_width=0, fill_color=PRIMARY_RED, fill_opacity=1)
        center_pulse.move_to(hub.get_center())
        center_pulse.set_z_index(7)
        self.play(FadeIn(center_pulse, scale=0.7), run_time=0.2)
        self.play(
            center_pulse.animate.scale(3.35).set_fill(PRIMARY_RED, opacity=0),
            *[cell.animate.set_fill(GRAY_300, opacity=0.24).scale(0.78) for guide in guides for cell in guide],
            *[cell.animate.set_fill(GRAY_300, opacity=0.22).scale(0.78) for guide in child_guides for cell in guide],
            hub.animate.set_fill(PRIMARY_RED, opacity=1),
            run_time=0.85,
            rate_func=rate_functions.ease_out_cubic,
        )
        self.remove(center_pulse)
        self.play(
            *[node.animate.scale(1.012) for node in visible_nodes],
            root.animate.scale(1.015),
            run_time=0.35,
            rate_func=rate_functions.there_and_back,
        )

        child_count = sum(len(layout.spec.children) for layout in layouts)
        elapsed_before_hold = 2.8 + 1.1 + len(layouts) * 3.05 + child_count * 1.28 + 1.4
        self.wait(max(7.0, 26.0 - elapsed_before_hold))


def render_variant(args: _Args) -> int:
    env = {
        **os.environ,
        "MIND_MAP_ROOT_TEXT": args.root_text,
        "MIND_MAP_BRANCHES": args.branches,
    }
    for poster in (False, True):
        result = subprocess.run(render_command(args, poster), check=False, env=env)
        if result.returncode != 0:
            return result.returncode
        promote_rendered_file((POSTER_PATH if poster else VIDEO_PATH).name, POSTER_PATH if poster else VIDEO_PATH)
    return 0


def main() -> int:
    args = parse_args()
    categories = clean_tree(args.branches)
    args.branches = ";".join(f"{category.label}:{','.join(category.children)}" for category in categories)
    return render_variant(args)


if __name__ == "__main__":
    raise SystemExit(main())
