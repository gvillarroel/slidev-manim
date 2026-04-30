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
    RIGHT,
    UP,
    AnimationGroup,
    FadeIn,
    FadeOut,
    Indicate,
    Line,
    MarkupText,
    RoundedRectangle,
    Scene,
    SurroundingRectangle,
    Text,
    ReplacementTransform,
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
HIGHLIGHT_BLUE = "#cdf3ff"
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


class _Args(argparse.Namespace):
    quality: str
    preview: bool


def parse_args() -> _Args:
    parser = argparse.ArgumentParser(description="Render the transaction-category-table Manim spike.")
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

    command.extend([str(Path(__file__).resolve()), "TransactionCategoryTableScene"])
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


def code_text(value: str, size: int = 21, color: str = GRAY) -> Text:
    return Text(value, font="Consolas", font_size=size, color=color)


class TransactionTable:
    def __init__(self, frame_left: float = -5.85, frame_top: float = 1.92) -> None:
        self.left = frame_left
        self.top = frame_top
        self.row_height = 0.68
        self.col_widths = [6.42, 2.36]
        self.headers = ["Transaction description", "Category"]
        self.group = VGroup()
        self.cells: dict[tuple[int, int], Cell] = {}
        self.category_texts: list[Text] = []
        self.keyword_tokens: list[object] = []
        self.category_column_box: SurroundingRectangle | None = None

    def center_for(self, row: int, col: int) -> object:
        x = self.left + sum(self.col_widths[:col]) + self.col_widths[col] / 2
        y = self.top - row * self.row_height - self.row_height / 2
        return RIGHT * x + UP * y

    def build(self, transactions: list[Transaction]) -> VGroup:
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
            description_cell = self._cell(
                row_index,
                0,
                fill_color=WHITE,
                fill_opacity=1,
            )
            description_label, keyword_token = self._description_label(
                transaction.description,
                transaction.keyword,
                description_cell.box,
            )
            self.keyword_tokens.append(keyword_token)
            self.cells[(row_index, 0)] = Cell(
                box=description_cell.box,
                content=description_label,
                keyword=keyword_token,
            )
            self.group.add(description_cell.box, description_label)

            category_cell = self._cell(
                row_index,
                1,
                fill_color=HIGHLIGHT_PURPLE,
                fill_opacity=0.72,
            )
            self.cells[(row_index, 1)] = Cell(box=category_cell.box, content=VGroup())
            self.group.add(category_cell.box)

            category_text = text(transaction.category, size=22, color=PRIMARY_PURPLE, weight="BOLD")
            if category_text.width > category_cell.box.width - 0.28:
                category_text.scale_to_fit_width(category_cell.box.width - 0.28)
            category_text.move_to(category_cell.box.get_center())
            category_text.set_z_index(5)
            self.category_texts.append(category_text)

        category_cells = VGroup(*[self.cells[(row, 1)].box for row in range(row_count)])
        self.category_column_box = SurroundingRectangle(
            category_cells,
            color=PRIMARY_PURPLE,
            stroke_width=4,
            buff=0.02,
            corner_radius=0.13,
        )
        self.category_column_box.set_z_index(7)
        return self.group

    def _cell(
        self,
        row: int,
        col: int,
        fill_color: str,
        fill_opacity: float,
    ) -> Cell:
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
    ) -> tuple[MarkupText, object]:
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

        return label, label


class TransactionCategoryTableScene(Scene):
    def construct(self) -> None:
        self.camera.background_color = PAGE_BACKGROUND

        transactions = build_transactions()
        table = TransactionTable()
        table_group = table.build(transactions)

        stage = RoundedRectangle(
            width=12.8,
            height=7.15,
            corner_radius=0.34,
            stroke_width=0,
            fill_color=PAGE_BACKGROUND,
            fill_opacity=0.96,
        )
        stage.set_z_index(-10)

        title = text("Transaction text to category", size=32, color=GRAY, weight="BOLD")
        title.to_edge(UP, buff=0.36)
        title.set_z_index(2)

        subtitle = text("Matched keywords become one category per row", size=20, color=GRAY_700)
        subtitle.next_to(title, DOWN, buff=0.11)
        subtitle.set_z_index(2)

        title_block = VGroup(title, subtitle)
        title_panel = RoundedRectangle(
            width=11.65,
            height=title_block.height + 0.34,
            corner_radius=0.18,
            stroke_color=GRAY_200,
            stroke_width=1.5,
            fill_color=WHITE,
            fill_opacity=1,
        )
        title_panel.move_to(title_block.get_center())
        title_panel.set_z_index(0)

        rule_panel = RoundedRectangle(
            width=2.6,
            height=0.74,
            corner_radius=0.14,
            stroke_color=GRAY_300,
            stroke_width=1.5,
            fill_color=WHITE,
            fill_opacity=0.96,
        )
        rule_panel.move_to(RIGHT * 4.82 + UP * 2.0)
        rule_panel.set_z_index(1)
        rule_hint = VGroup(
            code_text("keyword", size=18, color=PRIMARY_ORANGE),
            code_text("->", size=18, color=GRAY_700),
            text("category", size=18, color=PRIMARY_PURPLE, weight="BOLD"),
        )
        rule_hint.arrange(RIGHT, buff=0.12)
        rule_hint.move_to(rule_panel.get_center())
        rule_hint.set_z_index(3)

        self.add(stage)
        self.play(
            FadeIn(title_panel, shift=DOWN * 0.06),
            FadeIn(title, shift=DOWN * 0.1),
            FadeIn(subtitle, shift=DOWN * 0.1),
            run_time=0.48,
        )
        self.play(FadeIn(table_group, shift=UP * 0.08), run_time=0.55)
        self.play(FadeIn(rule_panel), FadeIn(rule_hint), run_time=0.35)
        self.wait(2.2)

        for row_index, transaction in enumerate(transactions, start=1):
            self._animate_row(row_index, transaction, table)

        self.play(
            FadeOut(rule_panel),
            FadeOut(rule_hint),
            FadeIn(table.category_column_box),
            Indicate(table.cells[(0, 1)].box, color=PRIMARY_PURPLE, scale_factor=1.04),
            run_time=0.65,
        )
        final_table = VGroup(table_group, *table.category_texts, table.category_column_box)
        self.play(
            final_table.animate.shift(RIGHT * 1.48),
            run_time=0.9,
            rate_func=rate_functions.ease_out_cubic,
        )
        self.wait(6.7)

    def _animate_row(self, row_index: int, transaction: Transaction, table: TransactionTable) -> None:
        description_cell = table.cells[(row_index, 0)].box
        category_cell = table.cells[(row_index, 1)].box
        description_label = table.keyword_tokens[row_index - 1]
        final_category_text = table.category_texts[row_index - 1]

        row_marker = RoundedRectangle(
            width=0.1,
            height=0.46,
            corner_radius=0.05,
            stroke_width=0,
            fill_color=PRIMARY_YELLOW,
            fill_opacity=1,
        )
        row_marker.move_to(description_cell.get_left() + LEFT * 0.13)
        row_marker.set_z_index(7)

        row_line = Line(
            description_cell.get_left() + DOWN * 0.23,
            category_cell.get_right() + DOWN * 0.23,
            color=PRIMARY_YELLOW,
            stroke_width=3,
            stroke_opacity=0.82,
        )
        row_line.set_z_index(6)
        row_focus = VGroup(row_marker, row_line)

        keyword_box = SurroundingRectangle(
            description_cell,
            color=PRIMARY_ORANGE,
            stroke_width=2.2,
            buff=0.02,
            corner_radius=0.08,
        )
        keyword_box.set_z_index(8)

        badge, badge_parts = self._classification_badge(
            transaction,
            category_cell.get_right() + RIGHT * 1.42,
        )

        result_token = text(transaction.category, size=23, color=PRIMARY_YELLOW, weight="BOLD")
        if result_token.width > category_cell.width - 0.28:
            result_token.scale_to_fit_width(category_cell.width - 0.28)
        result_token.move_to(category_cell.get_center())
        result_token.set_z_index(9)

        self.play(
            FadeIn(row_focus),
            FadeIn(keyword_box),
            FadeIn(badge_parts["box"], shift=LEFT * 0.04),
            FadeIn(badge_parts["keyword"], shift=LEFT * 0.04),
            FadeIn(badge_parts["arrow"], shift=LEFT * 0.04),
            run_time=0.55,
        )
        self.play(
            Indicate(description_label, color=PRIMARY_ORANGE, scale_factor=1.015),
            FadeIn(badge_parts["category"], shift=LEFT * 0.03),
            run_time=0.55,
        )
        self.wait(0.35)
        self.play(
            ReplacementTransform(badge_parts["category"], result_token),
            run_time=0.65,
            rate_func=rate_functions.ease_out_cubic,
        )
        self.play(
            ReplacementTransform(result_token, final_category_text),
            run_time=0.3,
            rate_func=rate_functions.ease_out_cubic,
        )
        self.wait(0.45)
        self.play(
            FadeOut(row_focus),
            FadeOut(keyword_box),
            FadeOut(badge_parts["box"], shift=UP * 0.03),
            FadeOut(badge_parts["keyword"], shift=UP * 0.03),
            FadeOut(badge_parts["arrow"], shift=UP * 0.03),
            run_time=0.45,
        )

    def _classification_badge(
        self,
        transaction: Transaction,
        position: object,
    ) -> tuple[VGroup, dict[str, object]]:
        keyword = code_text(transaction.keyword, size=19, color=PRIMARY_ORANGE)
        arrow = code_text("->", size=19, color=GRAY_700)
        category = text(transaction.category, size=20, color=PRIMARY_PURPLE, weight="BOLD")
        terms = VGroup(keyword, arrow, category)
        terms.arrange(RIGHT, buff=0.12)
        if terms.width > 2.32:
            terms.scale_to_fit_width(2.32)

        badge = RoundedRectangle(
            width=terms.width + 0.44,
            height=0.46,
            corner_radius=0.1,
            stroke_color=PRIMARY_ORANGE,
            stroke_width=1.8,
            fill_color=WHITE,
            fill_opacity=0.96,
        )
        badge.move_to(position)
        badge.set_z_index(6)
        terms.move_to(badge.get_center())
        for mob in terms:
            mob.set_z_index(8)
        group = VGroup(badge, terms)
        return group, {
            "box": badge,
            "keyword": keyword,
            "arrow": arrow,
            "category": category,
        }


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
