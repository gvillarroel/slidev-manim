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
    LEFT,
    RIGHT,
    UP,
    Circle,
    Create,
    FadeIn,
    FadeOut,
    LaggedStart,
    Rectangle,
    Scene,
    Text,
    VGroup,
    VMobject,
    config,
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
    bend: float
    child_centers: tuple[object, ...]


class _Args(argparse.Namespace):
    quality: str
    preview: bool
    root_text: str
    branches: str


def parse_args() -> _Args:
    parser = argparse.ArgumentParser(description="Render the organic fractal mind-map line spike.")
    parser.add_argument(
        "--quality",
        choices=("low", "medium", "high", "production", "4k"),
        default="medium",
        help="Manim quality preset. Defaults to medium for presentation review.",
    )
    parser.add_argument("--preview", action="store_true", help="Open the rendered output after rendering.")
    parser.add_argument("--root-text", default=DEFAULT_ROOT_TEXT, help="Text shown in the source box.")
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
    command.extend([str(Path(__file__).resolve()), "MindMapOrganicFractalLinesScene"])
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

    return [CategorySpec(label=label, children=("source", "result")) for label in clean_labels(raw)]


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
    box.set_z_index(5)
    text.set_z_index(6)
    return VGroup(box, text)


def slot_box(width: float, height: float, center: object, opacity: float) -> Rectangle:
    slot = Rectangle(width=width, height=height, stroke_width=0, fill_color=GRAY_200, fill_opacity=opacity)
    slot.move_to(center)
    slot.set_z_index(-2)
    return slot


def category_layouts(categories: list[CategorySpec]) -> list[CategoryLayout]:
    count = len(categories)
    y_top = 2.22
    y_bottom = -2.22
    y_step = 0 if count == 1 else (y_top - y_bottom) / (count - 1)
    layouts: list[CategoryLayout] = []
    for index, spec in enumerate(categories):
        y = y_top - index * y_step
        child_count = len(spec.children)
        child_gap = 0.45 if child_count > 2 else 0.54
        child_top = y + (child_count - 1) * child_gap / 2
        child_centers = tuple(RIGHT * 3.68 + UP * (child_top - child_index * child_gap) for child_index in range(child_count))
        bend = 0.72 if y > 0.35 else -0.72 if y < -0.35 else 0.18
        layouts.append(
            CategoryLayout(
                spec=spec,
                center=RIGHT * 0.18 + UP * y,
                color=CATEGORY_FILLS[index % len(CATEGORY_FILLS)],
                bend=bend,
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


def length_of(vector: object) -> float:
    delta = np.array(vector)
    return math.hypot(float(delta[0]), float(delta[1]))


def unit(vector: object) -> object:
    delta = np.array(vector)
    length = length_of(delta)
    if length < 0.001:
        return np.array([1.0, 0.0, 0.0])
    return delta / length


def normal_for(start: object, end: object) -> object:
    direction = unit(np.array(end) - np.array(start))
    return np.array([-direction[1], direction[0], 0])


def organic_point(start: object, end: object, bend: float, t: float, phase: float) -> object:
    start_point = np.array(start)
    end_point = np.array(end)
    route_normal = normal_for(start_point, end_point)
    control = (start_point + end_point) / 2 + route_normal * bend
    base = ((1 - t) ** 2) * start_point + 2 * (1 - t) * t * control + (t**2) * end_point
    wave = route_normal * (0.055 * math.sin(math.pi * t) * math.sin(phase + t * math.tau * 1.65))
    return base + wave


def organic_route_points(start: object, end: object, bend: float, phase: float, steps: int, wiggle: float) -> list[object]:
    points: list[object] = []
    route_normal = normal_for(start, end)
    for index in range(steps):
        t = index / (steps - 1)
        base = organic_point(start, end, bend, t, phase)
        fine_wave = route_normal * (wiggle * math.sin(math.pi * t) * math.sin(phase * 0.7 + t * math.tau * 3.1))
        points.append(base + fine_wave)
    return points


def make_stem(points: list[object], color: str, width: float, opacity: float, z_index: int) -> VMobject:
    stem = VMobject()
    stem.set_points_smoothly([np.array(point) for point in points])
    stem.set_stroke(color=color, width=width, opacity=opacity)
    stem.set_fill(opacity=0)
    stem.set_z_index(z_index)
    return stem


def route_tangent(points: list[object], index: int) -> object:
    left_index = max(0, index - 1)
    right_index = min(len(points) - 1, index + 1)
    return unit(np.array(points[right_index]) - np.array(points[left_index]))


def tendril_points(parent_points: list[object], t: float, side: int, length: float, phase: float) -> list[object]:
    index = max(1, min(len(parent_points) - 2, round(t * (len(parent_points) - 1))))
    start = np.array(parent_points[index])
    tangent = route_tangent(parent_points, index)
    normal = np.array([-tangent[1], tangent[0], 0])
    direction = unit(tangent * 0.42 + normal * side)
    end = start + direction * length
    bend = side * length * 0.22
    return organic_route_points(start, end, bend, phase, steps=8, wiggle=0.018)


def organic_fractal_line(
    start: object,
    end: object,
    bend: float,
    color: str,
    opacity: float,
    width: float,
    z_index: int,
    phase: float,
    side_count: int,
    depth: int,
) -> VGroup:
    route_length = length_of(np.array(end) - np.array(start))
    main_points = organic_route_points(start, end, bend, phase, steps=20, wiggle=0.035)
    stems = VGroup(make_stem(main_points, color, width, opacity, z_index))

    branch_slots = [0.28, 0.46, 0.64, 0.78][:side_count]
    for branch_index, t in enumerate(branch_slots):
        side = 1 if (branch_index + int(abs(phase) * 10)) % 2 == 0 else -1
        branch_length = min(0.58, route_length * (0.12 + 0.018 * math.sin(phase + branch_index)))
        branch_points = tendril_points(main_points, t, side, branch_length, phase + branch_index * 0.91)
        stems.add(make_stem(branch_points, color, width * 0.46, opacity * 0.58, z_index - 1))

        if depth > 1 and branch_length > 0.28:
            twig_side = -side
            twig_points = tendril_points(branch_points, 0.64, twig_side, branch_length * 0.45, phase + branch_index * 1.73)
            stems.add(make_stem(twig_points, color, width * 0.24, opacity * 0.36, z_index - 2))

    return stems


def bud(center: object, radius: float, color: str, opacity: float, z_index: int) -> Circle:
    shape = Circle(radius=radius, stroke_width=0, fill_color=color, fill_opacity=opacity)
    shape.move_to(center)
    shape.set_z_index(z_index)
    return shape


class MindMapOrganicFractalLinesScene(Scene):
    def construct(self) -> None:
        config.transparent = True
        config.background_opacity = 0.0
        self.camera.background_color = PAGE_BACKGROUND
        self.camera.background_opacity = 0.0

        root = text_box(scene_root_text(), 2.18, 0.78, PRIMARY_RED, font_size=25)
        root.move_to(LEFT * 3.76)
        root.set_z_index(5)

        seed = bud(root.get_right() + RIGHT * 0.16, 0.07, PRIMARY_RED, 1, 7)

        layouts = category_layouts(scene_categories())
        source = root.get_right() + RIGHT * 0.22
        category_slots = VGroup(*[slot_box(1.86, 0.58, layout.center, opacity=0.48) for layout in layouts])
        child_slots = VGroup(*[slot_box(1.28, 0.34, center, opacity=0.48) for layout in layouts for center in layout.child_centers])

        pending_trunks = VGroup()
        pending_children = VGroup()
        for layout_index, layout in enumerate(layouts):
            end = layout.center + LEFT * 1.12
            pending_trunks.add(
                organic_fractal_line(
                    source,
                    end,
                    layout.bend,
                    GRAY_300,
                    0.31,
                    2.2,
                    -3,
                    phase=layout_index * 1.11,
                    side_count=3,
                    depth=1,
                )
            )
            for child_index, child_center in enumerate(layout.child_centers):
                pending_children.add(
                    organic_fractal_line(
                        layout.center + RIGHT * 0.98,
                        child_center + LEFT * 0.98,
                        0.12 if child_index % 2 == 0 else -0.12,
                        GRAY_300,
                        0.31,
                        1.15,
                        -4,
                        phase=layout_index * 1.7 + child_index,
                        side_count=1,
                        depth=1,
                    )
                )

        self.add(pending_trunks, pending_children, category_slots, child_slots, root, seed)
        self.wait(2.7)

        root_sprouts = VGroup()
        focus_center = seed.get_center()
        for index in range(10):
            angle = -0.74 * math.pi + index * 1.48 * math.pi / 9
            start = focus_center + np.array([math.cos(angle) * 0.06, math.sin(angle) * 0.06, 0])
            end = focus_center + np.array([math.cos(angle) * 0.33, math.sin(angle) * 0.24, 0])
            root_sprouts.add(make_stem(organic_route_points(start, end, 0.035, index * 0.6, 7, 0.01), PRIMARY_RED, 1.7, 0.78, 6))

        self.play(
            LaggedStart(*[Create(sprout) for sprout in root_sprouts], lag_ratio=0.05),
            seed.animate.scale(1.55),
            root.animate.scale(1.012),
            run_time=0.62,
            rate_func=rate_functions.ease_out_cubic,
        )
        self.play(
            *[sprout.animate.set_stroke(color=PRIMARY_RED, opacity=0) for sprout in root_sprouts],
            seed.animate.scale(1 / 1.55),
            root.animate.scale(1 / 1.012),
            run_time=0.48,
            rate_func=rate_functions.ease_out_cubic,
        )
        self.remove(root_sprouts)

        visible_nodes = VGroup()
        active_trunks = VGroup()
        active_children = VGroup()
        category_cards: list[VGroup | None] = [None for _ in layouts]
        for index in balanced_reveal_order(len(layouts)):
            layout = layouts[index]
            category_card = text_box(layout.spec.label, 1.86, 0.58, layout.color, font_size=20)
            category_card.move_to(layout.center)
            category_card.set_z_index(5)

            end = category_card.get_left() + LEFT * 0.24
            trunk = organic_fractal_line(
                source,
                end,
                layout.bend,
                PRIMARY_RED,
                0.94,
                4.0,
                2,
                phase=index * 1.13 + 0.4,
                side_count=4,
                depth=2,
            )
            active_trunks.add(trunk)
            terminal_bud = bud(end, 0.09, PRIMARY_RED, 1, 7)

            self.play(
                FadeOut(pending_trunks[index]),
                LaggedStart(*[Create(stem) for stem in trunk], lag_ratio=0.12),
                FadeIn(terminal_bud, scale=0.55),
                run_time=1.18,
                rate_func=rate_functions.ease_out_cubic,
            )
            self.play(
                FadeOut(terminal_bud, scale=1.42),
                FadeIn(category_card[0], scale=0.82),
                *[stem.animate.set_stroke(color=GRAY_400, opacity=0.34) for stem in trunk],
                FadeOut(category_slots[index]),
                run_time=0.62,
                rate_func=rate_functions.ease_out_cubic,
            )
            self.play(FadeIn(category_card[1], shift=RIGHT * 0.05), run_time=0.32)
            visible_nodes.add(category_card)
            category_cards[index] = category_card
            self.wait(0.22)

        self.wait(0.45)

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
                child_card[0].set_stroke(layout.color, width=1.55, opacity=0.72)
                child_card[0].set_fill(GRAY_100, opacity=0.98)
                child_card.set_z_index(5)

                child_start = category_card.get_right() + RIGHT * 0.05
                child_end = child_card.get_left() + LEFT * 0.36
                child_line = organic_fractal_line(
                    child_start,
                    child_end,
                    0.14 if child_index % 2 == 0 else -0.14,
                    PRIMARY_RED,
                    0.88,
                    1.95,
                    2,
                    phase=index * 1.6 + child_index * 0.9,
                    side_count=2,
                    depth=1,
                )
                active_children.add(child_line)
                child_bud = bud(child_end, 0.052, PRIMARY_RED, 1, 7)

                self.play(
                    FadeOut(pending_children[child_slot_base + child_index]),
                    LaggedStart(*[Create(stem) for stem in child_line], lag_ratio=0.14),
                    FadeIn(child_bud, scale=0.55),
                    FadeOut(child_slots[child_slot_base + child_index]),
                    run_time=0.56,
                    rate_func=rate_functions.ease_in_out_cubic,
                )
                self.play(
                    FadeOut(child_bud, scale=1.35),
                    FadeIn(child_card[0], scale=0.82),
                    *[stem.animate.set_stroke(color=GRAY_300, opacity=0.28) for stem in child_line],
                    run_time=0.3,
                    rate_func=rate_functions.ease_out_cubic,
                )
                self.play(FadeIn(child_card[1], shift=RIGHT * 0.04), run_time=0.22)
                visible_nodes.add(child_card)
            self.wait(0.15)

        pulse = bud(seed.get_center(), 0.16, PRIMARY_RED, 0.9, 8)
        self.play(FadeIn(pulse, scale=0.7), run_time=0.2)
        self.play(
            pulse.animate.scale(3.15).set_fill(PRIMARY_RED, opacity=0),
            *[stem.animate.set_stroke(color=GRAY_300, opacity=0.22) for trunk in active_trunks for stem in trunk],
            *[stem.animate.set_stroke(color=GRAY_300, opacity=0.18) for child in active_children for stem in child],
            run_time=0.85,
            rate_func=rate_functions.ease_out_cubic,
        )
        self.remove(pulse)
        self.play(
            *[node.animate.scale(1.01) for node in visible_nodes],
            root.animate.scale(1.014),
            run_time=0.34,
            rate_func=rate_functions.there_and_back,
        )

        child_count = sum(len(layout.spec.children) for layout in layouts)
        elapsed_before_hold = 2.7 + 1.1 + len(layouts) * 3.0 + child_count * 1.3 + 1.4
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
