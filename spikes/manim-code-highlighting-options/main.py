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
from pathlib import Path

from manim import (
    DOWN,
    LEFT,
    RIGHT,
    UP,
    Code,
    Create,
    FadeIn,
    FadeOut,
    GrowFromCenter,
    Indicate,
    Rectangle,
    Scene,
    SurroundingRectangle,
    Text,
    VGroup,
    VMobject,
    Write,
    rate_functions,
)

SPIKE_DIR = Path(__file__).resolve().parent
REPO_ROOT = SPIKE_DIR.parent.parent
SPIKE_NAME = SPIKE_DIR.name
OUTPUT_DIR = REPO_ROOT / "videos" / SPIKE_NAME
STAGING_DIR = OUTPUT_DIR / ".manim"
VIDEO_PATH = OUTPUT_DIR / f"{SPIKE_NAME}.webm"
POSTER_PATH = OUTPUT_DIR / f"{SPIKE_NAME}.png"

PRIMARY_RED = "#9e1b32"
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
GRAY_600 = "#696969"
GRAY_700 = "#4f4f4f"
GRAY_900 = "#1c1c1c"
PAGE_BACKGROUND = "#f7f7f7"
HIGHLIGHT_RED = "#ffccd5"
HIGHLIGHT_ORANGE = "#ffe5cc"
HIGHLIGHT_YELLOW = "#fff4cc"
HIGHLIGHT_GREEN = "#dbffcc"
HIGHLIGHT_BLUE = "#cdf3ff"
HIGHLIGHT_PURPLE = "#f9ccff"

TEXT_FONT = "Arial"
CODE_FONT = "Consolas"


@dataclass(frozen=True)
class LanguageSpec:
    name: str
    language: str
    code: str
    accent: str
    highlight: str
    key_line: int


@dataclass(frozen=True)
class CodeCard:
    group: VGroup
    listing: Code
    header: Rectangle
    label: Text
    spec: LanguageSpec


@dataclass(frozen=True)
class OptionPanel:
    group: VGroup
    rows: list[VGroup]
    swatches: VGroup


LANGUAGES = [
    LanguageSpec(
        name="Python",
        language="python",
        accent=PRIMARY_RED,
        highlight=HIGHLIGHT_RED,
        key_line=1,
        code='''def eligible(user):
    return user["active"] and not user["locked"]''',
    ),
    LanguageSpec(
        name="TypeScript",
        language="typescript",
        accent=PRIMARY_ORANGE,
        highlight=HIGHLIGHT_ORANGE,
        key_line=1,
        code="""export const total = (items) =>
  items.reduce((sum, item) => sum + item.price, 0)""",
    ),
    LanguageSpec(
        name="Rust",
        language="rust",
        accent=PRIMARY_YELLOW,
        highlight=HIGHLIGHT_YELLOW,
        key_line=1,
        code="""fn clamp(x: i32) -> i32 {
    x.max(0).min(100)
}""",
    ),
    LanguageSpec(
        name="Go",
        language="go",
        accent=PRIMARY_GREEN,
        highlight=HIGHLIGHT_GREEN,
        key_line=1,
        code="""func Ready(q Queue) bool {
    return q.Len() > 0 && !q.Closed()
}""",
    ),
    LanguageSpec(
        name="SQL",
        language="sql",
        accent=PRIMARY_BLUE,
        highlight=HIGHLIGHT_BLUE,
        key_line=2,
        code="""select user_id, count(*) as orders
from orders
where status = 'paid'
group by user_id;""",
    ),
    LanguageSpec(
        name="Bash",
        language="bash",
        accent=PRIMARY_PURPLE,
        highlight=HIGHLIGHT_PURPLE,
        key_line=1,
        code='''set -euo pipefail
for file in *.webm; do
  ffmpeg -i "$file" "${file%.webm}.mp4"
done''',
    ),
]


class _Args(argparse.Namespace):
    quality: str
    preview: bool


def parse_args() -> _Args:
    parser = argparse.ArgumentParser(description="Render the Manim Code highlighting options spike.")
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
        "--media_dir",
        str(STAGING_DIR),
        "-o",
        target.stem,
    ]
    command.append("-s" if poster else "--format=webm")
    if not poster:
        command.append("-t")
    if args.preview:
        command.append("-p")
    command.extend([str(Path(__file__).resolve()), "ManimCodeHighlightOptionsScene"])
    return command


def promote(target_name: str, destination: Path) -> None:
    matches = sorted(STAGING_DIR.glob(f"**/{target_name}"))
    if not matches:
        raise FileNotFoundError(f"Could not find {target_name} under {STAGING_DIR}")
    destination.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(max(matches, key=lambda path: path.stat().st_mtime), destination)


def text(value: str, size: int = 24, color: str = GRAY, weight: str | None = None) -> Text:
    kwargs = {"font": TEXT_FONT, "font_size": size, "color": color}
    if weight is not None:
        kwargs["weight"] = weight
    return Text(value, **kwargs)


def mono(value: str, size: int = 18, color: str = GRAY) -> Text:
    return Text(value, font=CODE_FONT, font_size=size, color=color)


def fit(mob: VMobject, max_width: float, max_height: float) -> VMobject:
    if mob.width > max_width:
        mob.scale_to_fit_width(max_width)
    if mob.height > max_height:
        mob.scale_to_fit_height(max_height)
    return mob


def make_listing(
    spec: LanguageSpec,
    *,
    font_size: int = 15,
    formatter_style: str = "friendly",
    background: str = "rectangle",
    add_line_numbers: bool = True,
    fill_color: str = WHITE,
    stroke_color: str = GRAY_200,
) -> Code:
    listing = Code(
        code_string=spec.code,
        language=spec.language,
        formatter_style=formatter_style,
        tab_width=2,
        add_line_numbers=add_line_numbers,
        line_numbers_from=1,
        background=background,
        background_config={
            "fill_color": fill_color,
            "fill_opacity": 1,
            "stroke_color": stroke_color,
            "stroke_width": 1.15,
            "buff": 0.13,
        },
        paragraph_config={
            "font": CODE_FONT,
            "font_size": font_size,
            "line_spacing": 0.35,
        },
    )
    return listing


def build_code_card(spec: LanguageSpec, width: float = 3.62, height: float = 1.56) -> CodeCard:
    frame = Rectangle(
        width=width,
        height=height,
        stroke_color=GRAY_200,
        stroke_width=1.2,
        fill_color=WHITE,
        fill_opacity=0.96,
    )
    header = Rectangle(
        width=width,
        height=0.31,
        stroke_width=0,
        fill_color=spec.accent,
        fill_opacity=1,
    )
    header.align_to(frame, UP)
    label = text(spec.name, size=15, color=WHITE, weight="BOLD")
    label.move_to(header.get_center())

    listing = make_listing(spec)
    fit(listing, width - 0.32, height - 0.48)
    listing.move_to(frame.get_center() + DOWN * 0.18)

    group = VGroup(frame, header, label, listing)
    return CodeCard(group=group, listing=listing, header=header, label=label, spec=spec)


def build_language_grid() -> tuple[VGroup, list[CodeCard]]:
    cards = [build_code_card(spec) for spec in LANGUAGES]
    positions = [
        LEFT * 4.3 + UP * 1.88,
        LEFT * 0.45 + UP * 1.88,
        LEFT * 4.3 + UP * 0.13,
        LEFT * 0.45 + UP * 0.13,
        LEFT * 4.3 + DOWN * 1.62,
        LEFT * 0.45 + DOWN * 1.62,
    ]
    for card, position in zip(cards, positions, strict=True):
        card.group.move_to(position)
    return VGroup(*[card.group for card in cards]), cards


def line_wash(listing: Code, line_index: int, color: str, opacity: float = 0.76) -> Rectangle:
    line = listing.code_lines[line_index]
    wash = Rectangle(
        width=listing.width - 0.24,
        height=max(line.height + 0.13, 0.18),
        stroke_width=0,
        fill_color=color,
        fill_opacity=opacity,
    )
    wash.move_to([listing.get_center()[0] + 0.06, line.get_center()[1], 0])
    return wash


def line_cursor(listing: Code, line_index: int, color: str = PRIMARY_RED) -> Rectangle:
    line = listing.code_lines[line_index]
    cursor = Rectangle(
        width=0.045,
        height=max(line.height + 0.2, 0.22),
        stroke_width=0,
        fill_color=color,
        fill_opacity=1,
    )
    cursor.move_to([line.get_left()[0] - 0.12, line.get_center()[1], 0])
    return cursor


def token_box(listing: Code, line_index: int, start: int, end: int, color: str = PRIMARY_RED) -> SurroundingRectangle:
    line = listing.code_lines[line_index]
    pieces = [line[index] for index in range(start, min(end, len(line)))]
    target = VGroup(*pieces) if pieces else line
    box = SurroundingRectangle(target, buff=0.045, color=color, stroke_width=2.4)
    box.set_fill(color, opacity=0)
    return box


def option_row(name: str, detail: str, color: str = GRAY_700) -> VGroup:
    key = mono(name, size=13, color=color)
    value = text(detail, size=13, color=GRAY_600)
    value.next_to(key, RIGHT, buff=0.16)
    row = VGroup(key, value)
    return row


def style_swatch(style: str, fill_color: str, label_color: str = GRAY) -> VGroup:
    snippet = LanguageSpec(
        name=style,
        language="python",
        accent=PRIMARY_RED,
        highlight=HIGHLIGHT_RED,
        key_line=1,
        code="""if ok:
  ship()""",
    )
    listing = make_listing(
        snippet,
        font_size=10,
        formatter_style=style,
        add_line_numbers=False,
        fill_color=fill_color,
        stroke_color=GRAY_300,
    )
    fit(listing, 1.26, 0.54)
    label = mono(style, size=10, color=label_color)
    label.next_to(listing, DOWN, buff=0.05)
    return VGroup(listing, label)


def build_option_panel() -> OptionPanel:
    panel = Rectangle(
        width=4.78,
        height=5.55,
        stroke_color=GRAY_200,
        stroke_width=1.4,
        fill_color=WHITE,
        fill_opacity=0.95,
    )
    panel.move_to(RIGHT * 4.18 + DOWN * 0.05)

    heading = text("Code() options", size=23, color=GRAY, weight="BOLD")
    heading.move_to(panel.get_top() + DOWN * 0.35)

    rows = [
        option_row("language", "python / ts / rust / go / sql / bash", PRIMARY_BLUE),
        option_row("formatter_style", "Pygments styles", PRIMARY_PURPLE),
        option_row("line_numbers", "on, off, or shifted", PRIMARY_GREEN),
        option_row("background", "rectangle or window", PRIMARY_ORANGE),
        option_row("paragraph_config", "mono font + size", PRIMARY_RED),
        option_row("line wash", "Rectangle behind code_lines[n]", PRIMARY_RED),
        option_row("token box", "SurroundingRectangle(region)", PRIMARY_RED),
        option_row("cursor pulse", "animated mobject overlay", PRIMARY_RED),
    ]
    row_group = VGroup(*rows)
    row_group.arrange(DOWN, aligned_edge=LEFT, buff=0.14)
    row_group.move_to(panel.get_center() + UP * 0.52)
    row_group.align_to(panel, LEFT).shift(RIGHT * 0.32)

    swatches = VGroup(
        style_swatch("friendly", WHITE),
        style_swatch("monokai", GRAY_900, WHITE),
        style_swatch("github-dark", "#0d1117", WHITE),
    )
    swatches.arrange(RIGHT, buff=0.16)
    swatches.move_to(panel.get_bottom() + UP * 0.72)

    note = text("syntax from Pygments; emphasis from normal Manim mobjects", size=12, color=GRAY_600)
    note.move_to(panel.get_bottom() + UP * 0.18)

    group = VGroup(panel, heading, row_group, swatches, note)
    return OptionPanel(group=group, rows=rows, swatches=swatches)


def row_focus(row: VGroup, color: str = HIGHLIGHT_RED) -> Rectangle:
    focus = Rectangle(
        width=4.22,
        height=max(row.height + 0.12, 0.26),
        stroke_color=PRIMARY_RED,
        stroke_width=1.2,
        fill_color=color,
        fill_opacity=0.78,
    )
    focus.move_to(row.get_center() + RIGHT * 0.34)
    return focus


class ManimCodeHighlightOptionsScene(Scene):
    def construct(self) -> None:
        self.camera.background_color = PAGE_BACKGROUND

        stage = Rectangle(
            width=12.95,
            height=7.18,
            stroke_color=GRAY_200,
            stroke_width=1.35,
            fill_color=PAGE_BACKGROUND,
            fill_opacity=0.98,
        )
        stage.set_z_index(-20)
        self.add(stage)

        title = text("Programming code in Manim", size=31, color=GRAY, weight="BOLD")
        subtitle = mono("one Code() listing per language; overlays handle the extra emphasis", size=15, color=GRAY_600)
        header = VGroup(title, subtitle).arrange(DOWN, buff=0.09)
        header.move_to(UP * 3.33)

        language_grid, cards = build_language_grid()
        option_panel = build_option_panel()

        self.play(FadeIn(header, shift=DOWN * 0.08), FadeIn(language_grid, shift=UP * 0.08), run_time=0.9)
        self.wait(2.25)

        for card in cards:
            wash = line_wash(card.listing, card.spec.key_line, card.spec.highlight)
            marker = Rectangle(
                width=0.065,
                height=wash.height + 0.04,
                stroke_width=0,
                fill_color=card.spec.accent,
                fill_opacity=1,
            )
            marker.next_to(wash, LEFT, buff=0.045)
            pulse = VGroup(wash, marker)
            self.play(
                FadeIn(pulse),
                card.header.animate.set_fill(card.spec.accent, opacity=0.86),
                run_time=0.28,
            )
            self.wait(0.42)
            self.play(FadeOut(pulse), card.header.animate.set_fill(card.spec.accent, opacity=1), run_time=0.24)

        self.play(FadeIn(option_panel.group, shift=LEFT * 0.12), run_time=0.62)
        self.wait(0.65)

        for index, row in enumerate(option_panel.rows[:5]):
            color = HIGHLIGHT_BLUE if index < 4 else HIGHLIGHT_RED
            focus = row_focus(row, color=color)
            self.play(FadeIn(focus), row.animate.set_color(PRIMARY_RED), run_time=0.22)
            self.wait(0.3)
            self.play(FadeOut(focus), row.animate.set_color(GRAY_700), run_time=0.18)

        python_card = cards[0]
        active_wash = line_wash(python_card.listing, 1, HIGHLIGHT_RED, opacity=0.84)
        wash_row_focus = row_focus(option_panel.rows[5], color=HIGHLIGHT_RED)
        self.play(FadeIn(wash_row_focus), FadeIn(active_wash), run_time=0.3)
        self.wait(0.6)
        self.play(FadeOut(wash_row_focus), run_time=0.18)

        region_box = token_box(python_card.listing, 1, 6, 20, color=PRIMARY_RED)
        token_row_focus = row_focus(option_panel.rows[6], color=HIGHLIGHT_RED)
        self.play(FadeIn(token_row_focus), Create(region_box), run_time=0.48)
        self.wait(0.52)
        self.play(FadeOut(token_row_focus), run_time=0.18)

        cursor = line_cursor(python_card.listing, 1, color=PRIMARY_RED)
        cursor_row_focus = row_focus(option_panel.rows[7], color=HIGHLIGHT_RED)
        line = python_card.listing.code_lines[1]
        self.play(FadeIn(cursor_row_focus), GrowFromCenter(cursor), run_time=0.28)
        self.play(
            cursor.animate.move_to([line.get_right()[0] + 0.12, line.get_center()[1], 0]),
            run_time=1.0,
            rate_func=rate_functions.linear,
        )
        self.play(FadeOut(cursor_row_focus), FadeOut(cursor), run_time=0.24)

        self.play(Indicate(option_panel.swatches, color=PRIMARY_PURPLE, scale_factor=1.02), run_time=0.85)
        self.wait(0.35)

        final_tag = VGroup(
            Rectangle(width=6.45, height=0.44, stroke_width=0, fill_color=PRIMARY_RED, fill_opacity=1),
            text("Use Code for syntax; use Manim geometry for narrative highlights.", size=15, color=WHITE),
        )
        final_tag[1].move_to(final_tag[0].get_center())
        final_tag[0].set_z_index(0)
        final_tag[1].set_z_index(1)
        final_tag.move_to(DOWN * 3.36)
        self.play(Write(final_tag[1]), FadeIn(final_tag[0]), run_time=0.65)
        self.wait(6.35)


def render_variant(args: _Args) -> None:
    for poster in (False, True):
        result = subprocess.run(
            render_command(args, poster),
            check=False,
            env={**os.environ, "SPIKE_RENDER_TARGET": "poster" if poster else "video"},
        )
        if result.returncode != 0:
            raise SystemExit(result.returncode)
        target = POSTER_PATH if poster else VIDEO_PATH
        promote(target.name, target)


def main() -> int:
    args = parse_args()
    render_variant(args)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
