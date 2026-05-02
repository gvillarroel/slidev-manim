#!/usr/bin/env -S uv run --script
# /// script
# dependencies = [
#   "manim>=0.20.0",
#   "pillow>=10.0.0",
#   "pygments>=2.17.0",
# ]
# ///

from __future__ import annotations

import argparse
import hashlib
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
    Create,
    FadeIn,
    FadeOut,
    GrowFromCenter,
    Group,
    ImageMobject,
    Indicate,
    Rectangle,
    Scene,
    Text,
    VGroup,
    VMobject,
    Write,
    rate_functions,
)
from pygments import highlight
from pygments.formatters import ImageFormatter
from pygments.lexers import get_lexer_by_name

SPIKE_DIR = Path(__file__).resolve().parent
REPO_ROOT = SPIKE_DIR.parent.parent
SPIKE_NAME = SPIKE_DIR.name
OUTPUT_DIR = REPO_ROOT / "videos" / SPIKE_NAME
STAGING_DIR = OUTPUT_DIR / ".manim"
ASSET_DIR = OUTPUT_DIR / "code-assets"
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
class CodePreview:
    image: ImageMobject
    line_count: int


@dataclass(frozen=True)
class CodeCard:
    group: Group
    preview: CodePreview
    header: Rectangle
    label: Text
    spec: LanguageSpec


@dataclass(frozen=True)
class OptionPanel:
    group: Group
    rows: list[VGroup]
    swatches: Group


LANGUAGES = [
    LanguageSpec(
        name="Python",
        language="python",
        accent=PRIMARY_RED,
        highlight=HIGHLIGHT_RED,
        key_line=1,
        code='''def eligible(user):
    return user.active and not user.locked''',
    ),
    LanguageSpec(
        name="TypeScript",
        language="typescript",
        accent=PRIMARY_ORANGE,
        highlight=HIGHLIGHT_ORANGE,
        key_line=2,
        code="""const total = items.reduce(
  (sum, item) => sum + item.price,
  0,
)""",
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


def code_asset_path(code: str, language: str, style: str, line_numbers: bool) -> Path:
    digest = hashlib.sha1(f"{language}:{style}:{line_numbers}:{code}".encode("utf-8")).hexdigest()[:10]
    return ASSET_DIR / f"{language}-{style}-{digest}.png"


def ensure_code_asset(
    code: str,
    language: str,
    *,
    style: str = "friendly",
    line_numbers: bool = True,
    font_size: int = 28,
) -> Path:
    ASSET_DIR.mkdir(parents=True, exist_ok=True)
    path = code_asset_path(code, language, style, line_numbers)
    if path.exists():
        return path

    lexer = get_lexer_by_name(language)
    formatter = ImageFormatter(
        style=style,
        line_numbers=line_numbers,
        line_number_bg=PAGE_BACKGROUND,
        line_number_fg=GRAY_600,
        font_name=CODE_FONT,
        font_size=font_size,
        line_pad=5,
        image_pad=14,
    )
    path.write_bytes(highlight(code, lexer, formatter))
    return path


def make_preview(
    spec: LanguageSpec,
    *,
    style: str = "friendly",
    line_numbers: bool = True,
    font_size: int = 28,
) -> CodePreview:
    path = ensure_code_asset(
        spec.code,
        spec.language,
        style=style,
        line_numbers=line_numbers,
        font_size=font_size,
    )
    return CodePreview(image=ImageMobject(str(path)), line_count=len(spec.code.splitlines()))


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

    preview = make_preview(spec)
    fit(preview.image, width - 0.32, height - 0.49)
    preview.image.move_to(frame.get_center() + DOWN * 0.18)

    group = Group(frame, header, label, preview.image)
    return CodeCard(group=group, preview=preview, header=header, label=label, spec=spec)


def build_language_grid() -> tuple[Group, list[CodeCard]]:
    cards = [build_code_card(spec) for spec in LANGUAGES]
    positions = [
        LEFT * 4.3 + UP * 1.58,
        LEFT * 0.45 + UP * 1.58,
        LEFT * 4.3 + DOWN * 0.08,
        LEFT * 0.45 + DOWN * 0.08,
        LEFT * 4.3 + DOWN * 1.74,
        LEFT * 0.45 + DOWN * 1.74,
    ]
    for card, position in zip(cards, positions, strict=True):
        card.group.move_to(position)
    return Group(*[card.group for card in cards]), cards


def line_metrics(preview: CodePreview, line_index: int) -> tuple[float, float, float, float]:
    image = preview.image
    line_height = image.height / (preview.line_count + 0.82)
    y = image.get_top()[1] - line_height * (0.68 + line_index)
    left_x = image.get_left()[0] + image.width * 0.18
    right_x = image.get_right()[0] - image.width * 0.045
    return y, line_height, left_x, right_x


def line_wash(card: CodeCard, color: str, opacity: float = 0.76) -> Rectangle:
    y, line_height, left_x, right_x = line_metrics(card.preview, card.spec.key_line)
    wash = Rectangle(
        width=right_x - left_x,
        height=max(line_height * 0.72, 0.18),
        stroke_width=0,
        fill_color=color,
        fill_opacity=opacity,
    )
    wash.move_to([(left_x + right_x) / 2, y, 0])
    return wash


def line_cursor(card: CodeCard, color: str = PRIMARY_RED) -> Rectangle:
    y, line_height, left_x, _ = line_metrics(card.preview, card.spec.key_line)
    cursor = Rectangle(
        width=0.045,
        height=max(line_height * 0.88, 0.22),
        stroke_width=0,
        fill_color=color,
        fill_opacity=1,
    )
    cursor.move_to([left_x + 0.04, y, 0])
    return cursor


def region_box(card: CodeCard, color: str = PRIMARY_RED) -> Rectangle:
    y, line_height, left_x, right_x = line_metrics(card.preview, card.spec.key_line)
    box = Rectangle(
        width=(right_x - left_x) * 0.32,
        height=max(line_height * 0.8, 0.23),
        stroke_color=color,
        stroke_width=2.4,
        fill_color=color,
        fill_opacity=0,
    )
    box.move_to([left_x + (right_x - left_x) * 0.47, y, 0])
    return box


def option_row(name: str, detail: str, color: str = GRAY_700) -> VGroup:
    key = mono(name, size=13, color=color)
    value = text(detail, size=13, color=GRAY_600)
    value.next_to(key, RIGHT, buff=0.16)
    return VGroup(key, value)


def style_swatch(style: str, label_color: str = GRAY) -> Group:
    snippet = LanguageSpec(
        name=style,
        language="python",
        accent=PRIMARY_RED,
        highlight=HIGHLIGHT_RED,
        key_line=1,
        code="""if ok:
  ship()""",
    )
    preview = make_preview(snippet, style=style, line_numbers=False, font_size=20)
    fit(preview.image, 1.25, 0.55)
    label = mono(style, size=10, color=label_color)
    label.next_to(preview.image, DOWN, buff=0.05)
    return Group(preview.image, label)


def build_option_panel() -> OptionPanel:
    panel = Rectangle(
        width=4.78,
        height=5.2,
        stroke_color=GRAY_200,
        stroke_width=1.4,
        fill_color=WHITE,
        fill_opacity=0.95,
    )
    panel.move_to(RIGHT * 4.18 + DOWN * 0.22)

    heading = text("Code() options", size=23, color=GRAY, weight="BOLD")
    heading.move_to(panel.get_top() + DOWN * 0.35)

    rows = [
        option_row("language", "python / ts / rust / go / sql / bash", PRIMARY_BLUE),
        option_row("formatter_style", "Pygments styles", PRIMARY_PURPLE),
        option_row("line_numbers", "on, off, or shifted", PRIMARY_GREEN),
        option_row("background", "rectangle or window", PRIMARY_ORANGE),
        option_row("paragraph_config", "mono font + size", PRIMARY_RED),
        option_row("line wash", "Rectangle behind line n", PRIMARY_RED),
        option_row("token box", "outline a text region", PRIMARY_RED),
        option_row("cursor pulse", "animated overlay mobject", PRIMARY_RED),
    ]
    row_group = VGroup(*rows)
    row_group.arrange(DOWN, aligned_edge=LEFT, buff=0.14)
    row_group.move_to(panel.get_center() + UP * 0.52)
    row_group.align_to(panel, LEFT).shift(RIGHT * 0.32)

    swatches = Group(
        style_swatch("friendly"),
        style_swatch("monokai", WHITE),
        style_swatch("github-dark", WHITE),
    )
    swatches.arrange(RIGHT, buff=0.16)
    swatches.move_to(panel.get_bottom() + UP * 0.72)

    note = text("syntax from Code/Pygments; emphasis from Manim geometry", size=11, color=GRAY_600)
    fit(note, 4.36, 0.24)
    note.move_to(panel.get_bottom() + UP * 0.18)

    group = Group(panel, heading, row_group, swatches, note)
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
            width=12.65,
            height=6.9,
            stroke_color=GRAY_200,
            stroke_width=1.35,
            fill_color=PAGE_BACKGROUND,
            fill_opacity=0.98,
        )
        stage.set_z_index(-20)
        self.add(stage)

        title = text("Programming code in Manim", size=31, color=GRAY, weight="BOLD")
        subtitle = mono("one listing per language; overlays handle extra emphasis", size=15, color=GRAY_600)
        header = VGroup(title, subtitle).arrange(DOWN, buff=0.09)
        header.move_to(UP * 3.02)

        language_grid, cards = build_language_grid()
        option_panel = build_option_panel()

        self.add(header, language_grid, option_panel.group)
        self.wait(2.75)

        for card in cards:
            wash = line_wash(card, card.spec.highlight)
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

        self.wait(0.95)

        for index, row in enumerate(option_panel.rows[:5]):
            color = HIGHLIGHT_BLUE if index < 4 else HIGHLIGHT_RED
            focus = row_focus(row, color=color)
            self.play(FadeIn(focus), run_time=0.22)
            self.wait(0.3)
            self.play(FadeOut(focus), run_time=0.18)

        python_card = cards[0]
        active_wash = line_wash(python_card, HIGHLIGHT_RED, opacity=0.84)
        wash_row_focus = row_focus(option_panel.rows[5], color=HIGHLIGHT_RED)
        self.play(FadeIn(wash_row_focus), FadeIn(active_wash), run_time=0.3)
        self.wait(0.6)
        self.play(FadeOut(wash_row_focus), run_time=0.18)

        box = region_box(python_card, color=PRIMARY_RED)
        token_row_focus = row_focus(option_panel.rows[6], color=HIGHLIGHT_RED)
        self.play(FadeIn(token_row_focus), Create(box), run_time=0.48)
        self.wait(0.52)
        self.play(FadeOut(token_row_focus), run_time=0.18)

        cursor = line_cursor(python_card, color=PRIMARY_RED)
        cursor_row_focus = row_focus(option_panel.rows[7], color=HIGHLIGHT_RED)
        _, _, _, right_x = line_metrics(python_card.preview, python_card.spec.key_line)
        self.play(FadeIn(cursor_row_focus), GrowFromCenter(cursor), run_time=0.28)
        self.play(
            cursor.animate.move_to([right_x + 0.07, cursor.get_center()[1], 0]),
            run_time=1.0,
            rate_func=rate_functions.linear,
        )
        self.play(FadeOut(cursor_row_focus), FadeOut(cursor), run_time=0.24)
        self.play(FadeOut(active_wash), box.animate.set_stroke(width=3.0), run_time=0.35)

        self.play(Indicate(option_panel.swatches, color=PRIMARY_PURPLE, scale_factor=1.02), run_time=0.85)
        self.wait(0.35)

        final_box = Rectangle(width=6.05, height=0.5, stroke_width=0, fill_color=PRIMARY_RED, fill_opacity=1)
        final_text = text("Code handles syntax; Manim geometry carries the story.", size=16, color=WHITE)
        final_text.move_to(final_box.get_center())
        final_box.set_z_index(0)
        final_text.set_z_index(1)
        final_tag = VGroup(final_box, final_text).move_to(DOWN * 3.06)
        self.play(FadeIn(final_box), Write(final_text), run_time=0.65)
        self.wait(7.65)


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
