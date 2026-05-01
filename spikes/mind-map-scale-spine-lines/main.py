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
    FadeIn,
    FadeOut,
    LaggedStart,
    Polygon,
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
DARK_RED = "#5f0d1e"
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


def spine_stroke_for(color: str) -> str:
    return DARK_RED if color == PRIMARY_RED else GRAY_500


def spine_stroke_width(opacity: float) -> float:
    return 1.15 if opacity >= 0.5 else 0.45


def spine_stroke_opacity(opacity: float) -> float:
    if opacity >= 0.5:
        return min(0.9, opacity * 0.82 + 0.12)
    return opacity * 0.75


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
    parser = argparse.ArgumentParser(description="Render the scale-spine mind-map line spike.")
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
    command.extend([str(Path(__file__).resolve()), "MindMapScaleSpineLinesScene"])
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
    slot = Rectangle(width=width, height=height, stroke_width=0, fill_color=GRAY_100, fill_opacity=opacity)
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
        child_centers = tuple(RIGHT * 3.35 + UP * (child_top - child_index * child_gap) for child_index in range(child_count))
        bend = 0.68 if y > 0.35 else -0.68 if y < -0.35 else 0.12
        layouts.append(
            CategoryLayout(
                spec=spec,
                center=RIGHT * -0.42 + UP * y,
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


def vector_length(vector: object) -> float:
    delta = np.array(vector)
    return math.hypot(float(delta[0]), float(delta[1]))


def unit(vector: object) -> object:
    delta = np.array(vector)
    length = vector_length(delta)
    if length < 0.001:
        return np.array([1.0, 0.0, 0.0])
    return delta / length


def normal_for(start: object, end: object) -> object:
    direction = unit(np.array(end) - np.array(start))
    return np.array([-direction[1], direction[0], 0])


def scale_route_point(start: object, end: object, bend: float, t: float, phase: float) -> object:
    start_point = np.array(start)
    end_point = np.array(end)
    route_normal = normal_for(start_point, end_point)
    control = (start_point + end_point) / 2 + route_normal * bend
    base = ((1 - t) ** 2) * start_point + 2 * (1 - t) * t * control + (t**2) * end_point
    ripple = route_normal * (0.028 * math.sin(math.pi * t) * math.sin(phase + t * math.tau * 2.2))
    return base + ripple


def route_tangent(start: object, end: object, bend: float, t: float, phase: float) -> object:
    low = max(0.0, t - 0.02)
    high = min(1.0, t + 0.02)
    return unit(scale_route_point(start, end, bend, high, phase) - scale_route_point(start, end, bend, low, phase))


def scale_spine_shape(
    center: object,
    tangent: object,
    normal: object,
    length: float,
    width: float,
    side: float,
    color: str,
    opacity: float,
    z_index: int,
) -> Polygon:
    center_point = np.array(center) + np.array(normal) * side * width * 0.28
    tangent_vector = unit(tangent)
    normal_vector = unit(normal)
    side_bias = max(-1.0, min(1.0, side))
    tip = center_point + tangent_vector * length * 0.74 + normal_vector * side_bias * width * 0.12
    shoulder_a = center_point + tangent_vector * length * 0.04 + normal_vector * width * (0.82 + 0.18 * max(side_bias, 0))
    root_a = center_point - tangent_vector * length * 0.34 + normal_vector * width * (0.28 + 0.1 * max(side_bias, 0))
    tail = center_point - tangent_vector * length * 0.48 + normal_vector * side_bias * width * 0.08
    root_b = center_point - tangent_vector * length * 0.34 - normal_vector * width * (0.28 + 0.1 * max(-side_bias, 0))
    shoulder_b = center_point + tangent_vector * length * 0.04 - normal_vector * width * (0.82 + 0.18 * max(-side_bias, 0))
    shape = Polygon(
        tip,
        shoulder_a,
        root_a,
        tail,
        root_b,
        shoulder_b,
        stroke_color=spine_stroke_for(color),
        stroke_width=spine_stroke_width(opacity),
        stroke_opacity=spine_stroke_opacity(opacity),
        fill_color=color,
        fill_opacity=opacity,
    )
    shape.set_z_index(z_index)
    return shape


def scale_spine_line(
    start: object,
    end: object,
    bend: float,
    count: int,
    color: str,
    opacity: float,
    length: float,
    width: float,
    z_index: int,
    phase: float,
    center_every: int = 5,
) -> VGroup:
    spines = VGroup()
    side_pattern = (0.0, 0.95, -0.95, 0.48, -0.48, 0.72, -0.72)
    for index in range(count):
        t = (index + 1) / (count + 1)
        center = scale_route_point(start, end, bend, t, phase)
        tangent = route_tangent(start, end, bend, t, phase)
        normal = normal_for(start, end)
        side = side_pattern[index % len(side_pattern)] if center_every else 1 if index % 2 == 0 else -1
        local_length = length * (0.9 + 0.12 * math.sin(index * 1.7 + phase) ** 2)
        local_width = width * (0.9 + 0.16 * math.sin(index * 1.13 + phase) ** 2)
        spines.add(scale_spine_shape(center, tangent, normal, local_length, local_width, side, color, opacity, z_index))
    return spines


def bud(center: object, radius: float, color: str, opacity: float, z_index: int) -> Circle:
    shape = Circle(radius=radius, stroke_width=0, fill_color=color, fill_opacity=opacity)
    shape.move_to(center)
    shape.set_z_index(z_index)
    return shape


class MindMapScaleSpineLinesScene(Scene):
    def construct(self) -> None:
        self.camera.background_color = PAGE_BACKGROUND

        stage = Rectangle(width=12.8, height=7.15, stroke_width=0, fill_color=PAGE_BACKGROUND, fill_opacity=0.96)
        stage.set_z_index(-10)
        stage_border = Rectangle(width=12.34, height=6.62, stroke_color=GRAY_200, stroke_width=2, fill_opacity=0)
        stage_border.set_z_index(-9)

        root = text_box(scene_root_text(), 2.46, 0.88, PRIMARY_RED, font_size=28)
        root.move_to(LEFT * 4.46)
        root.set_z_index(5)

        seed = bud(root.get_right() + RIGHT * 0.14, 0.075, PRIMARY_RED, 1, 7)
        source = root.get_right() + RIGHT * 0.22
        layouts = category_layouts(scene_categories())

        category_slots = VGroup(*[slot_box(1.86, 0.58, layout.center, opacity=0.38) for layout in layouts])
        child_slots = VGroup(*[slot_box(1.28, 0.34, center, opacity=0.23) for layout in layouts for center in layout.child_centers])

        pending_trunks = VGroup()
        pending_children = VGroup()
        for layout_index, layout in enumerate(layouts):
            pending_trunks.add(
                scale_spine_line(
                    source,
                    layout.center + LEFT * 0.95,
                    layout.bend,
                    38,
                    GRAY_300,
                    0.13,
                    0.24,
                    0.09,
                    -3,
                    phase=layout_index * 0.83,
                )
            )
            for child_index, child_center in enumerate(layout.child_centers):
                pending_children.add(
                    scale_spine_line(
                        layout.center + RIGHT * 0.98,
                        child_center + LEFT * 0.72,
                        0.12 if child_index % 2 == 0 else -0.12,
                        20,
                        GRAY_300,
                        0.08,
                        0.15,
                        0.052,
                        -4,
                        phase=layout_index * 1.13 + child_index,
                        center_every=5,
                    )
                )

        self.add(stage, stage_border, pending_trunks, pending_children, category_slots, child_slots, root, seed)
        self.wait(2.7)

        focus_spines = VGroup()
        focus_center = seed.get_center()
        for index in range(16):
            angle = -math.pi * 0.72 + index * math.pi * 1.44 / 15
            tangent = np.array([math.cos(angle), math.sin(angle), 0])
            normal = np.array([-tangent[1], tangent[0], 0])
            center = focus_center + tangent * 0.2
            side = (0.95, -0.95, 0.48, -0.48)[index % 4]
            focus_spines.add(scale_spine_shape(center, tangent, normal, 0.24, 0.07, side, PRIMARY_RED, 0.82, 6))

        self.play(
            LaggedStart(*[FadeIn(spine, scale=0.28) for spine in focus_spines], lag_ratio=0.04),
            seed.animate.scale(1.55),
            root.animate.scale(1.012),
            run_time=0.62,
            rate_func=rate_functions.ease_out_cubic,
        )
        self.play(
            *[
                spine.animate.move_to(focus_center + (spine.get_center() - focus_center) * 1.42)
                .set_fill(PRIMARY_RED, opacity=0)
                .set_stroke(color=DARK_RED, opacity=0, width=0.8)
                for spine in focus_spines
            ],
            seed.animate.scale(1 / 1.55),
            root.animate.scale(1 / 1.012),
            run_time=0.48,
            rate_func=rate_functions.ease_out_cubic,
        )
        self.remove(focus_spines)

        visible_nodes = VGroup()
        active_trunks = VGroup()
        active_children = VGroup()
        category_cards: list[VGroup | None] = [None for _ in layouts]
        for index in balanced_reveal_order(len(layouts)):
            layout = layouts[index]
            category_card = text_box(layout.spec.label, 1.86, 0.58, layout.color, font_size=20)
            category_card.move_to(layout.center)
            category_card.set_z_index(5)

            end = category_card.get_left() + LEFT * 0.03
            trunk = scale_spine_line(
                source,
                end,
                layout.bend,
                52,
                PRIMARY_RED,
                0.94,
                0.3,
                0.11,
                2,
                phase=index * 0.91 + 0.4,
                center_every=5,
            )
            active_trunks.add(trunk)
            terminal_bud = bud(end, 0.09, PRIMARY_RED, 1, 7)

            self.play(
                FadeOut(pending_trunks[index]),
                LaggedStart(*[FadeIn(spine, scale=0.18) for spine in trunk], lag_ratio=0.032),
                FadeIn(terminal_bud, scale=0.55),
                run_time=1.16,
                rate_func=rate_functions.ease_out_cubic,
            )
            self.play(
                FadeOut(terminal_bud, scale=1.42),
                FadeIn(category_card[0], scale=0.82),
                *[
                    spine.animate.scale(0.76)
                    .set_fill(GRAY_400, opacity=0.21)
                    .set_stroke(color=GRAY_600, opacity=0.3, width=0.72)
                    for spine in trunk
                ],
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
                child_end = child_card.get_left() + LEFT * 0.04
                child_line = scale_spine_line(
                    child_start,
                    child_end,
                    0.12 if child_index % 2 == 0 else -0.12,
                    26,
                    PRIMARY_RED,
                    0.88,
                    0.19,
                    0.066,
                    2,
                    phase=index * 1.4 + child_index * 0.75,
                    center_every=5,
                )
                active_children.add(child_line)
                child_bud = bud(child_end, 0.052, PRIMARY_RED, 1, 7)

                self.play(
                    FadeOut(pending_children[child_slot_base + child_index]),
                    LaggedStart(*[FadeIn(spine, scale=0.18) for spine in child_line], lag_ratio=0.045),
                    FadeIn(child_bud, scale=0.55),
                    FadeOut(child_slots[child_slot_base + child_index]),
                    run_time=0.54,
                    rate_func=rate_functions.ease_in_out_cubic,
                )
                self.play(
                    FadeOut(child_bud, scale=1.35),
                    FadeIn(child_card[0], scale=0.82),
                    *[
                        spine.animate.scale(0.72)
                        .set_fill(GRAY_300, opacity=0.17)
                        .set_stroke(color=GRAY_500, opacity=0.22, width=0.58)
                        for spine in child_line
                    ],
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
            *[
                spine.animate.scale(0.84)
                .set_fill(GRAY_300, opacity=0.13)
                .set_stroke(color=GRAY_500, opacity=0.17, width=0.5)
                for trunk in active_trunks
                for spine in trunk
            ],
            *[
                spine.animate.scale(0.84)
                .set_fill(GRAY_300, opacity=0.1)
                .set_stroke(color=GRAY_500, opacity=0.13, width=0.42)
                for child in active_children
                for spine in child
            ],
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
        elapsed_before_hold = 2.7 + 1.1 + len(layouts) * 3.0 + child_count * 1.28 + 1.4
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
