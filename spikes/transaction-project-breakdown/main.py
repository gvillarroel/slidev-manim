#!/usr/bin/env -S uv run --script
# /// script
# dependencies = [
#   "manim>=0.20.0",
# ]
# ///

from __future__ import annotations

import argparse
import os
import shutil
import subprocess
import sys
from dataclasses import dataclass
from html import escape
from pathlib import Path

from manim import (
    DOWN,
    LEFT,
    ORIGIN,
    RIGHT,
    UP,
    ArcBetweenPoints,
    Circle,
    Create,
    FadeIn,
    FadeOut,
    Indicate,
    Line,
    MarkupText,
    ReplacementTransform,
    RoundedRectangle,
    Scene,
    SurroundingRectangle,
    Text,
    Transform,
    VGroup,
    rate_functions,
)

SPIKE_DIR = Path(__file__).resolve().parent
REPO_ROOT = SPIKE_DIR.parent.parent
SPIKE_NAME = SPIKE_DIR.name
OUTPUT_DIR = REPO_ROOT / "videos" / SPIKE_NAME
STAGING_DIR = OUTPUT_DIR / ".manim"

PRIMARY_ORANGE = "#e77204"
PRIMARY_YELLOW = "#f1c319"
PRIMARY_GREEN = "#45842a"
PRIMARY_BLUE = "#007298"
PRIMARY_PURPLE = "#652f6c"
WHITE = "#ffffff"
GRAY = "#333e48"
GRAY_100 = "#e7e7e7"
GRAY_200 = "#cfcfcf"
GRAY_300 = "#b5b5b5"
GRAY_400 = "#9c9c9c"
GRAY_700 = "#4f4f4f"
HIGHLIGHT_PURPLE = "#f9ccff"
PAGE_BACKGROUND = "#f7f7f7"

CATEGORY_RULES = [
    ("SUPERMARKET", "Groceries"),
    ("PAYROLL", "Income"),
    ("UBER", "Transport"),
    ("NETFLIX.COM", "Entertainment"),
    ("PHARMACY", "Health"),
]

RAW_DESCRIPTIONS = [
    "POS SUPERMARKET FRESH MART 04/27",
    "ACH PAYROLL ACME CORP APR",
    "CARD UBER TRIP 9182",
    "ONLINE NETFLIX.COM MONTHLY",
    "PHARMACY CVS RX 0472",
]


@dataclass(frozen=True)
class Transaction:
    description: str
    keyword: str
    category: str


@dataclass(frozen=True)
class Cell:
    box: RoundedRectangle
    content: object
    keyword: Text | None = None


@dataclass(frozen=True)
class ProjectSpec:
    title: str
    header_color: str
    dot_color: str
    tasks: tuple[str, str, str, str]
    center: object


class _Args(argparse.Namespace):
    quality: str
    preview: bool


def parse_args() -> _Args:
    parser = argparse.ArgumentParser(description="Render the transaction-project-breakdown Manim spike.")
    parser.add_argument(
        "--quality",
        choices=("low", "medium", "high", "production", "4k"),
        default="medium",
        help="Manim quality preset. Defaults to medium for presentation review.",
    )
    parser.add_argument("--preview", action="store_true", help="Open the rendered output after rendering.")
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
    command = [
        sys.executable,
        "-m",
        "manim",
        "render",
        quality_flag(args.quality),
        "-r",
        "1600,900",
        "--media_dir",
        str(STAGING_DIR),
        "-o",
        stem,
    ]

    if poster:
        command.append("-s")
    else:
        command.extend(["--format", "webm", "-t"])

    if args.preview:
        command.append("-p")

    command.extend([str(Path(__file__).resolve()), "TransactionProjectBreakdownScene"])
    return command


def promote_rendered_file(target_name: str, destination: Path) -> None:
    matches = sorted(STAGING_DIR.glob(f"**/{target_name}"))
    if not matches:
        raise FileNotFoundError(f"Could not find {target_name} under {STAGING_DIR}")
    destination.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(max(matches, key=lambda path: path.stat().st_mtime), destination)


def derive_transaction(description: str) -> Transaction:
    upper_description = description.upper()
    for keyword, category in CATEGORY_RULES:
        if keyword in upper_description:
            return Transaction(description=description, keyword=keyword, category=category)
    raise ValueError(f"No category rule matched transaction description: {description}")


def build_transactions() -> list[Transaction]:
    return [derive_transaction(description) for description in RAW_DESCRIPTIONS]


def text(
    value: str,
    size: int = 24,
    color: str = GRAY,
    font: str = "Arial",
    weight: str | None = None,
) -> Text:
    kwargs = {"font_size": size, "color": color, "font": font}
    if weight:
        kwargs["weight"] = weight
    return Text(value, **kwargs)


class TransactionTable:
    def __init__(self, frame_left: float = -4.37, frame_top: float = 1.92) -> None:
        self.left = frame_left
        self.top = frame_top
        self.row_height = 0.68
        self.col_widths = [6.42, 2.36]
        self.headers = ["Transaction description", "Category"]
        self.group = VGroup()
        self.cells: dict[tuple[int, int], Cell] = {}
        self.category_texts: list[Text] = []
        self.category_column_box: SurroundingRectangle | None = None

    def center_for(self, row: int, col: int) -> object:
        x = self.left + sum(self.col_widths[:col]) + self.col_widths[col] / 2
        y = self.top - row * self.row_height - self.row_height / 2
        return RIGHT * x + UP * y

    def build_resolved(self, transactions: list[Transaction]) -> VGroup:
        row_count = len(transactions) + 1
        frame = RoundedRectangle(
            width=sum(self.col_widths) + 0.34,
            height=self.row_height * row_count + 0.34,
            corner_radius=0.18,
            stroke_color=GRAY_400,
            stroke_width=2,
            fill_color=WHITE,
            fill_opacity=1,
        )
        frame.move_to(
            RIGHT * (self.left + sum(self.col_widths) / 2)
            + UP * (self.top - self.row_height * row_count / 2)
        )
        frame.set_z_index(0)
        self.group.add(frame)

        header_fills = [PRIMARY_BLUE, PRIMARY_PURPLE]
        for col, label in enumerate(self.headers):
            cell = self._cell(0, col, fill_color=header_fills[col], fill_opacity=1)
            header_label = text(label, size=22, color=WHITE, weight="BOLD")
            if header_label.width > cell.box.width - 0.32:
                header_label.scale_to_fit_width(cell.box.width - 0.32)
            header_label.move_to(cell.box.get_center())
            header_label.set_z_index(3)
            self.cells[(0, col)] = Cell(box=cell.box, content=header_label)
            self.group.add(cell.box, header_label)

        for row_index, transaction in enumerate(transactions, start=1):
            description_cell = self._cell(row_index, 0, fill_color=WHITE, fill_opacity=1)
            description_label = self._description_label(
                transaction.description,
                transaction.keyword,
                description_cell.box,
            )
            self.cells[(row_index, 0)] = Cell(
                box=description_cell.box,
                content=description_label,
                keyword=description_label,
            )
            self.group.add(description_cell.box, description_label)

            category_cell = self._cell(
                row_index,
                1,
                fill_color=HIGHLIGHT_PURPLE,
                fill_opacity=0.72,
            )
            category_text = text(transaction.category, size=22, color=PRIMARY_PURPLE, weight="BOLD")
            if category_text.width > category_cell.box.width - 0.28:
                category_text.scale_to_fit_width(category_cell.box.width - 0.28)
            category_text.move_to(category_cell.box.get_center())
            category_text.set_z_index(5)
            self.cells[(row_index, 1)] = Cell(box=category_cell.box, content=category_text)
            self.category_texts.append(category_text)
            self.group.add(category_cell.box, category_text)

        category_cells = VGroup(*[self.cells[(row, 1)].box for row in range(row_count)])
        self.category_column_box = SurroundingRectangle(
            category_cells,
            color=PRIMARY_PURPLE,
            stroke_width=4,
            buff=0.02,
            corner_radius=0.13,
        )
        self.category_column_box.set_z_index(7)
        self.group.add(self.category_column_box)
        return self.group

    def _cell(self, row: int, col: int, fill_color: str, fill_opacity: float) -> Cell:
        box = RoundedRectangle(
            width=self.col_widths[col] - 0.04,
            height=self.row_height - 0.05,
            corner_radius=0.08,
            stroke_color=GRAY_200,
            stroke_width=1.5,
            fill_color=fill_color,
            fill_opacity=fill_opacity,
        )
        box.move_to(self.center_for(row, col))
        box.set_z_index(1)
        return Cell(box=box, content=VGroup())

    def _description_label(
        self,
        description: str,
        keyword: str,
        box: RoundedRectangle,
    ) -> MarkupText:
        keyword_start = description.upper().index(keyword)
        keyword_end = keyword_start + len(keyword)
        label = MarkupText(
            (
                f"{escape(description[:keyword_start])}"
                f'<span fgcolor="{PRIMARY_ORANGE}"><b>{escape(description[keyword_start:keyword_end])}</b></span>'
                f"{escape(description[keyword_end:])}"
            ),
            font="Consolas",
            font_size=20,
            color=GRAY,
        )
        max_width = box.width - 0.28
        if label.width > max_width:
            label.scale_to_fit_width(max_width)
        label.move_to(box.get_left() + RIGHT * (0.16 + label.width / 2))
        label.set_y(box.get_center()[1])
        label.set_z_index(3)
        return label


class TransactionProjectBreakdownScene(Scene):
    def construct(self) -> None:
        self.camera.background_color = PAGE_BACKGROUND

        transactions = build_transactions()
        table = TransactionTable()
        resolved_table = table.build_resolved(transactions)

        stage = RoundedRectangle(
            width=12.8,
            height=7.15,
            corner_radius=0.34,
            stroke_width=0,
            fill_color=PAGE_BACKGROUND,
            fill_opacity=0.96,
        )
        stage.set_z_index(-10)

        title, subtitle, title_panel = self.title_group(
            "Transaction text to category",
            "Matched keywords become one category per row",
        )

        self.add(stage, title_panel, title, subtitle, resolved_table)
        self.wait(2.8)

        next_title, next_subtitle, next_title_panel = self.title_group(
            "Categories become workstreams",
            "The resolved table splits into two project backlogs",
        )
        self.play(
            Indicate(table.category_column_box, color=PRIMARY_PURPLE, scale_factor=1.025),
            run_time=0.8,
        )
        self.play(
            Transform(title_panel, next_title_panel),
            Transform(title, next_title),
            Transform(subtitle, next_subtitle),
            run_time=0.75,
            rate_func=rate_functions.ease_out_cubic,
        )
        self.wait(0.7)

        input_panel = self.input_panel()
        skeletons = self.project_block_skeletons()
        self.play(
            FadeIn(input_panel, shift=LEFT * 0.18),
            FadeIn(skeletons, shift=RIGHT * 0.18),
            resolved_table.animate.scale(0.38).move_to(LEFT * 4.05 + DOWN * 0.05),
            run_time=1.45,
            rate_func=rate_functions.ease_out_cubic,
        )
        self.wait(1.1)

        trunk, top_branch, bottom_branch = self.project_guides()
        top_spec = ProjectSpec(
            title="Classifier Project",
            header_color=PRIMARY_BLUE,
            dot_color=PRIMARY_YELLOW,
            tasks=(
                "clean bank text",
                "expand keyword rules",
                "score uncertain rows",
                "export category dataset",
            ),
            center=RIGHT * 2.18 + UP * 1.27,
        )
        bottom_spec = ProjectSpec(
            title="Needs Plan Project",
            header_color=PRIMARY_PURPLE,
            dot_color=PRIMARY_GREEN,
            tasks=(
                "group needs by category",
                "rank weekly priorities",
                "convert gaps to tasks",
                "track completed actions",
            ),
            center=RIGHT * 2.18 + DOWN * 1.43,
        )
        top_block, top_rows = self.project_block(top_spec)
        bottom_block, bottom_rows = self.project_block(bottom_spec)

        self.play(Create(trunk), run_time=0.7)
        fork_pulse = Circle(radius=0.16, stroke_width=0, fill_color=PRIMARY_YELLOW, fill_opacity=1)
        fork_pulse.move_to(LEFT * 1.18 + DOWN * 0.04)
        fork_pulse.set_z_index(8)
        self.play(FadeIn(fork_pulse, scale=0.7), run_time=0.25)
        self.play(
            fork_pulse.animate.scale(2.25).set_fill(PRIMARY_ORANGE, opacity=0),
            run_time=0.55,
            rate_func=rate_functions.ease_out_cubic,
        )
        self.remove(fork_pulse)
        self.wait(0.4)

        self.play(
            Create(top_branch),
            ReplacementTransform(skeletons[0], top_block),
            run_time=1.0,
            rate_func=rate_functions.ease_out_cubic,
        )
        for row in top_rows:
            self.play(FadeIn(row, shift=RIGHT * 0.12), run_time=0.62, rate_func=rate_functions.ease_out_cubic)
            self.wait(0.22)

        self.wait(0.6)
        self.play(
            Create(bottom_branch),
            ReplacementTransform(skeletons[1], bottom_block),
            run_time=1.0,
            rate_func=rate_functions.ease_out_cubic,
        )
        for row in bottom_rows:
            self.play(FadeIn(row, shift=RIGHT * 0.12), run_time=0.62, rate_func=rate_functions.ease_out_cubic)
            self.wait(0.22)

        self.wait(0.6)
        output_pulse = Circle(radius=0.18, stroke_width=0, fill_color=PRIMARY_YELLOW, fill_opacity=1)
        output_pulse.move_to(LEFT * 1.18 + DOWN * 0.04)
        output_pulse.set_z_index(8)
        self.play(FadeIn(output_pulse, scale=0.7), run_time=0.25)
        self.play(
            output_pulse.animate.scale(2.65).set_fill(PRIMARY_ORANGE, opacity=0),
            trunk.animate.set_opacity(0.34),
            top_branch.animate.set_opacity(0.34),
            bottom_branch.animate.set_opacity(0.34),
            run_time=0.85,
            rate_func=rate_functions.ease_out_cubic,
        )
        self.wait(7.0)

    def title_group(self, title_value: str, subtitle_value: str) -> tuple[Text, Text, RoundedRectangle]:
        title = text(title_value, size=32, color=GRAY, weight="BOLD")
        title.to_edge(UP, buff=0.36)
        title.set_z_index(2)

        subtitle = text(subtitle_value, size=20, color=GRAY_700)
        subtitle.next_to(title, DOWN, buff=0.11)
        subtitle.set_z_index(2)

        title_block = VGroup(title, subtitle)
        panel = RoundedRectangle(
            width=11.65,
            height=title_block.height + 0.34,
            corner_radius=0.18,
            stroke_color=GRAY_200,
            stroke_width=1.5,
            fill_color=WHITE,
            fill_opacity=1,
        )
        panel.move_to(title_block.get_center())
        panel.set_z_index(0)
        return title, subtitle, panel

    def input_panel(self) -> VGroup:
        panel = RoundedRectangle(
            width=3.75,
            height=4.85,
            corner_radius=0.24,
            stroke_color=GRAY_300,
            stroke_width=2,
            fill_color=WHITE,
            fill_opacity=0.82,
        )
        panel.move_to(LEFT * 4.05 + DOWN * 0.05)
        marker = RoundedRectangle(
            width=1.45,
            height=0.16,
            corner_radius=0.05,
            stroke_width=0,
            fill_color=PRIMARY_ORANGE,
            fill_opacity=0.92,
        )
        marker.move_to(panel.get_top() + DOWN * 0.38)
        label = text("resolved table", size=20, color=GRAY, weight="BOLD")
        label.scale_to_fit_width(1.7)
        label.move_to(panel.get_bottom() + UP * 0.42)
        count = text("5 categorized rows", size=15, color=GRAY_700)
        count.scale_to_fit_width(1.65)
        count.next_to(label, DOWN, buff=0.08)
        group = VGroup(panel, marker, label, count)
        group.set_z_index(-1)
        marker.set_z_index(1)
        label.set_z_index(1)
        count.set_z_index(1)
        return group

    def project_block_skeletons(self) -> VGroup:
        skeletons = VGroup()
        for center in (RIGHT * 2.18 + UP * 1.27, RIGHT * 2.18 + DOWN * 1.43):
            panel = RoundedRectangle(
                width=5.55,
                height=2.3,
                corner_radius=0.2,
                stroke_color=GRAY_300,
                stroke_width=2,
                fill_color=WHITE,
                fill_opacity=0.74,
            ).move_to(center)
            header_hint = RoundedRectangle(
                width=2.2,
                height=0.18,
                corner_radius=0.05,
                stroke_width=0,
                fill_color=GRAY_300,
                fill_opacity=0.82,
            ).move_to(panel.get_top() + DOWN * 0.34 + LEFT * 1.35)
            line_hints = VGroup(
                *[
                    RoundedRectangle(
                        width=3.9 - index * 0.3,
                        height=0.1,
                        corner_radius=0.035,
                        stroke_width=0,
                        fill_color=GRAY_200,
                        fill_opacity=0.86,
                    )
                    for index in range(4)
                ]
            )
            line_hints.arrange(DOWN, buff=0.22, aligned_edge=LEFT)
            line_hints.move_to(panel.get_left() + RIGHT * 2.62 + DOWN * 0.12)
            skeleton = VGroup(panel, header_hint, line_hints)
            skeleton.set_z_index(0)
            skeletons.add(skeleton)
        return skeletons

    def project_guides(self) -> tuple[Line, ArcBetweenPoints, ArcBetweenPoints]:
        start = LEFT * 2.17 + DOWN * 0.04
        fork = LEFT * 1.18 + DOWN * 0.04
        top = LEFT * 0.64 + UP * 1.27
        bottom = LEFT * 0.64 + DOWN * 1.43

        trunk = Line(start, fork, color=PRIMARY_ORANGE, stroke_width=7, stroke_opacity=0.78)
        top_branch = ArcBetweenPoints(fork, top, angle=0.24)
        bottom_branch = ArcBetweenPoints(fork, bottom, angle=-0.24)
        for branch in (top_branch, bottom_branch):
            branch.set_stroke(PRIMARY_ORANGE, width=7, opacity=0.78)
        trunk.set_z_index(2)
        top_branch.set_z_index(2)
        bottom_branch.set_z_index(2)
        return trunk, top_branch, bottom_branch

    def project_block(self, spec: ProjectSpec) -> tuple[VGroup, list[VGroup]]:
        panel = RoundedRectangle(
            width=5.55,
            height=2.3,
            corner_radius=0.2,
            stroke_color=GRAY_300,
            stroke_width=2,
            fill_color=WHITE,
            fill_opacity=0.98,
        )
        panel.move_to(spec.center)
        panel.set_z_index(3)

        header = RoundedRectangle(
            width=5.29,
            height=0.48,
            corner_radius=0.12,
            stroke_width=0,
            fill_color=spec.header_color,
            fill_opacity=1,
        )
        header.move_to(panel.get_top() + DOWN * 0.34)
        header.set_z_index(4)

        title = text(spec.title, size=21, color=WHITE, weight="BOLD")
        if title.width > header.width - 0.4:
            title.scale_to_fit_width(header.width - 0.4)
        title.move_to(header.get_center())
        title.set_z_index(5)

        rows: list[VGroup] = []
        for index, task in enumerate(spec.tasks):
            dot = Circle(radius=0.055, stroke_width=0, fill_color=spec.dot_color, fill_opacity=1)
            row_text = self.task_label(task)
            if row_text.width > 4.58:
                row_text.scale_to_fit_width(4.58)
            row = VGroup(dot, row_text)
            row.arrange(RIGHT, buff=0.16)
            row.move_to(panel.get_left() + RIGHT * (0.43 + row.width / 2) + UP * (0.32 - index * 0.38))
            row.set_z_index(5)
            rows.append(row)

        block = VGroup(panel, header, title)
        block.set_z_index(4)
        return block, rows

    def task_label(self, value: str) -> VGroup:
        words = VGroup(*[text(word, size=18, color=GRAY) for word in value.split(" ")])
        words.arrange(RIGHT, buff=0.08)
        return words


def render_variant(args: _Args) -> None:
    video_path, poster_path = output_paths()

    video_result = subprocess.run(
        render_command(args, video_path.stem, poster=False),
        check=False,
        env={**os.environ, "SPIKE_RENDER_TARGET": "video"},
    )
    if video_result.returncode != 0:
        raise SystemExit(video_result.returncode)
    promote_rendered_file(video_path.name, video_path)

    poster_result = subprocess.run(
        render_command(args, poster_path.stem, poster=True),
        check=False,
        env={**os.environ, "SPIKE_RENDER_TARGET": "poster"},
    )
    if poster_result.returncode != 0:
        raise SystemExit(poster_result.returncode)
    promote_rendered_file(poster_path.name, poster_path)


def main() -> int:
    args = parse_args()
    render_variant(args)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
