#!/usr/bin/env -S uv run --script
# /// script
# dependencies = [
#   "imageio-ffmpeg>=0.6.0",
#   "manim>=0.20.0",
#   "pillow>=11.0.0",
# ]
# ///

from __future__ import annotations

import math
import os
import shutil
import subprocess
import sys
from pathlib import Path

from manim import (
    DOWN,
    ORIGIN,
    UP,
    Create,
    FadeIn,
    FadeOut,
    Line,
    Rectangle,
    Scene,
    Text,
    VGroup,
    config,
    rate_functions,
)
from manimpango import list_fonts

SPIKE_FILE = Path(__file__).resolve()
SPIKE_DIR = SPIKE_FILE.parent
sys.path.insert(0, str(SPIKE_DIR.parent))

os.environ.setdefault("MERMAID_UNFOLD_SPIKE_FILE", str(SPIKE_FILE))
os.environ.setdefault("MERMAID_UNFOLD_SPIKE_DIR", str(SPIKE_DIR))
os.environ.setdefault("MERMAID_UNFOLD_TITLE", "Treemap")
os.environ.setdefault("MERMAID_UNFOLD_FAMILY", "Chart")

import mermaid_svg_unfold_engine as engine

PRIMARY_RED = "#9e1b32"
PRIMARY_ORANGE = "#d45d00"
PRIMARY_YELLOW = "#f1b434"
PRIMARY_GREEN = "#4b8b3b"
PRIMARY_BLUE = "#007298"
PRIMARY_PURPLE = "#6f2c91"
WHITE = "#ffffff"
GRAY = "#444444"
GRAY_050 = "#f4f5f6"
GRAY_100 = "#e7e7e7"
GRAY_200 = "#cfcfcf"
GRAY_400 = "#999999"
PAGE_BACKGROUND = "#f7f7f7"
TEXT_FONT = "Open Sans" if "Open Sans" in list_fonts() else "Arial"
SOURCE_CENTER_X = -2.35
MANIM_CENTER_X = 3.36
VIDEO_PATH = engine.output_dir() / f"{engine.spike_name()}.webm"
REVIEW_DIR = engine.output_dir() / "review-frames-0.3s"
REVIEW_RAW_DIR = REVIEW_DIR / "raw-alpha"
REVIEW_SHEETS_DIR = REVIEW_DIR / "sheets"

config.transparent = True
config.background_opacity = 0.0


def _label_group(label: str, value: str, *, color: str, max_width: float, max_height: float) -> VGroup:
    label_text = Text(label, font=TEXT_FONT, font_size=24, color=color)
    value_text = Text(value, font=TEXT_FONT, font_size=23, color=color)
    group = VGroup(label_text, value_text).arrange(DOWN, buff=0.02)
    if group.width > max_width:
        group.scale_to_fit_width(max_width)
    if group.height > max_height:
        group.scale_to_fit_height(max_height)
    return group


def _filled_box(
    width: float,
    height: float,
    *,
    fill: str,
    stroke: str,
    label: str,
    value: str,
    text_color: str = WHITE,
) -> VGroup:
    body = Rectangle(
        width=width,
        height=height,
        stroke_color=stroke,
        stroke_width=2.4,
        fill_color=fill,
        fill_opacity=0.96,
    )
    label_group = _label_group(label, value, color=text_color, max_width=width * 0.78, max_height=height * 0.52)
    label_group.move_to(body.get_center())
    label_group.set_z_index(8)
    body.set_z_index(3)
    return VGroup(body, label_group)


def _set_box_palette(box: VGroup, *, fill: str, stroke: str, text_color: str) -> None:
    box[0].set_fill(fill, opacity=0.96)
    box[0].set_stroke(stroke, width=2.4, opacity=1)
    box[1].set_color(text_color)


def _slot_for(box: VGroup, color: str) -> Rectangle:
    body = box[0]
    slot = Rectangle(
        width=body.width,
        height=body.height,
        stroke_color=color,
        stroke_width=1.7,
        fill_color=color,
        fill_opacity=0.045,
    )
    slot.move_to(body.get_center())
    slot.set_z_index(1)
    return slot


def _section_header(center_x: float, top_y: float, width: float, name: str, value: str, color: str) -> VGroup:
    rule = Line(
        start=(center_x - width / 2, top_y, 0),
        end=(center_x + width / 2, top_y, 0),
        stroke_color=color,
        stroke_width=3.0,
    )
    label = Text(name, font=TEXT_FONT, font_size=18, color=color)
    total = Text(value, font=TEXT_FONT, font_size=18, color=color)
    header_y = top_y + 0.23
    label.move_to((center_x - width / 2 + 0.08 + label.width / 2, header_y, 0))
    total.move_to((center_x + width / 2 - 0.08 - total.width / 2, header_y, 0))
    group = VGroup(rule, label, total)
    group.set_z_index(7)
    return group


def _active_outline(target: VGroup | Rectangle) -> Rectangle:
    body = target[0] if isinstance(target, VGroup) else target
    outline = Rectangle(
        width=body.width + 0.12,
        height=body.height + 0.12,
        stroke_color=PRIMARY_RED,
        stroke_width=4.0,
        fill_opacity=0,
    )
    outline.move_to(body.get_center())
    outline.set_z_index(9)
    return outline


class MermaidSvgUnfoldScene(Scene):
    def construct(self) -> None:
        self.camera.background_color = WHITE
        self.camera.background_opacity = 0.0

        source_header = _section_header(SOURCE_CENTER_X, 2.12, 7.08, "Mermaid SVG", "17", GRAY)
        manim_header = _section_header(MANIM_CENTER_X, 2.12, 3.96, "Manim", "10", GRAY)

        source_y = -0.22
        child_height = 4.18
        gap = 0.32
        x0 = SOURCE_CENTER_X - 3.54
        fragments = _filled_box(3.35, child_height, fill=GRAY_100, stroke=GRAY_400, label="Fragments", value="8", text_color=GRAY)
        source = _filled_box(1.82, child_height, fill=GRAY_100, stroke=GRAY_400, label="Source", value="5", text_color=GRAY)
        labels = _filled_box(1.27, child_height, fill=GRAY_100, stroke=GRAY_400, label="Labels", value="4", text_color=GRAY)
        fragments.move_to((x0 + fragments[0].width / 2, source_y, 0))
        source.move_to((fragments.get_right()[0] + gap + source[0].width / 2, source_y, 0))
        labels.move_to((source.get_right()[0] + gap + labels[0].width / 2, source_y, 0))

        timing = _filled_box(3.72, 1.86, fill=GRAY_100, stroke=GRAY_400, label="Timing", value="6", text_color=GRAY)
        review = _filled_box(3.72, 1.72, fill=GRAY_100, stroke=GRAY_400, label="Review", value="4", text_color=GRAY)
        timing.move_to((MANIM_CENTER_X, 0.72, 0))
        review.move_to((MANIM_CENTER_X, -1.60, 0))

        source_slots = VGroup(*[_slot_for(box, GRAY_400) for box in (fragments, source, labels)])
        manim_slots = VGroup(*[_slot_for(box, GRAY_400) for box in (timing, review)])
        all_boxes = VGroup(fragments, source, labels, timing, review)
        final_group = VGroup(source_header, manim_header, all_boxes)

        if os.environ.get("SPIKE_RENDER_TARGET") == "poster":
            _set_box_palette(timing, fill=PRIMARY_RED, stroke=PRIMARY_RED, text_color=WHITE)
            self.add(source_header, manim_header, all_boxes)
            return

        self.add(source_header, manim_header, source_slots, manim_slots)
        self.wait(2.6)

        for box, slot in ((fragments, source_slots[0]), (source, source_slots[1]), (labels, source_slots[2])):
            outline = _active_outline(slot)
            slot.set_opacity(0)
            self.play(Create(outline), run_time=0.38, rate_func=rate_functions.ease_out_cubic)
            self.play(FadeIn(box, scale=0.985), FadeOut(outline), run_time=0.82, rate_func=rate_functions.ease_out_cubic)
            self.remove(slot)
            self.wait(0.25)

        for box, slot in ((timing, manim_slots[0]), (review, manim_slots[1])):
            outline = _active_outline(slot)
            slot.set_opacity(0)
            self.play(Create(outline), run_time=0.38, rate_func=rate_functions.ease_out_cubic)
            self.play(FadeIn(box, scale=0.985), FadeOut(outline), run_time=0.82, rate_func=rate_functions.ease_out_cubic)
            self.remove(slot)
            self.wait(0.25)

        self.play(
            timing[0].animate.set_fill(PRIMARY_RED, opacity=0.96).set_stroke(PRIMARY_RED, opacity=1),
            timing[1].animate.set_color(WHITE),
            run_time=0.62,
            rate_func=rate_functions.ease_out_cubic,
        )
        self.wait(15.33)


def _clear_review_dir() -> None:
    if REVIEW_DIR.exists():
        shutil.rmtree(REVIEW_DIR)
    REVIEW_RAW_DIR.mkdir(parents=True, exist_ok=True)
    REVIEW_SHEETS_DIR.mkdir(parents=True, exist_ok=True)


def _extract_review_frames() -> dict[str, object]:
    import imageio_ffmpeg
    from PIL import Image, ImageDraw, ImageFont

    _clear_review_dir()
    ffmpeg = Path(imageio_ffmpeg.get_ffmpeg_exe()).resolve()
    raw_pattern = REVIEW_RAW_DIR / "frame_%04d.png"
    subprocess.run(
        [
            str(ffmpeg),
            "-y",
            "-hide_banner",
            "-loglevel",
            "error",
            "-c:v",
            "libvpx-vp9",
            "-i",
            str(VIDEO_PATH),
            "-vf",
            "fps=10/3,format=rgba",
            str(raw_pattern),
        ],
        check=True,
    )

    raw_frames = sorted(REVIEW_RAW_DIR.glob("frame_*.png"))
    if not raw_frames:
        raise RuntimeError(f"No review frames extracted from {VIDEO_PATH}")

    alpha_min, alpha_max = 255, 0
    composited: list[Path] = []
    for index, raw_path in enumerate(raw_frames, start=1):
        rgba = Image.open(raw_path).convert("RGBA")
        frame_alpha_min, frame_alpha_max = rgba.getchannel("A").getextrema()
        alpha_min = min(alpha_min, frame_alpha_min)
        alpha_max = max(alpha_max, frame_alpha_max)
        background = Image.new("RGBA", rgba.size, WHITE)
        background.alpha_composite(rgba)
        output = REVIEW_DIR / f"frame_{index:04d}_{(index - 1) * 0.3:06.2f}s.png"
        background.convert("RGB").save(output)
        composited.append(output)

    thumb_w = 320
    pad = 8
    label_h = 24
    cols = 5
    rows_per_sheet = 5
    first = Image.open(composited[0])
    thumb_h = round(first.height * thumb_w / first.width)
    try:
        font = ImageFont.truetype("arial.ttf", 14)
    except OSError:
        font = ImageFont.load_default()

    sheets: list[str] = []
    page_size = cols * rows_per_sheet
    for sheet_index, start in enumerate(range(0, len(composited), page_size), start=1):
        subset = composited[start : start + page_size]
        rows = math.ceil(len(subset) / cols)
        sheet = Image.new(
            "RGB",
            (cols * thumb_w + (cols + 1) * pad, rows * (thumb_h + label_h) + (rows + 1) * pad),
            WHITE,
        )
        draw = ImageDraw.Draw(sheet)
        for offset, frame_path in enumerate(subset):
            image = Image.open(frame_path).resize((thumb_w, thumb_h), Image.Resampling.LANCZOS)
            x = pad + (offset % cols) * (thumb_w + pad)
            y = pad + (offset // cols) * (thumb_h + label_h + pad)
            sheet.paste(image, (x, y))
            timestamp = (start + offset) * 0.3
            draw.text((x + 4, y + thumb_h + 4), f"{timestamp:.1f}s", fill=GRAY, font=font)
        sheet_path = REVIEW_SHEETS_DIR / f"contact-sheet-{sheet_index:02d}.png"
        sheet.save(sheet_path)
        sheets.append(str(sheet_path))

    return {
        "frame_count": len(composited),
        "alpha_extrema": [alpha_min, alpha_max],
        "contact_sheets": sheets,
    }


def main() -> int:
    original_render_command = engine.render_command

    def transparent_render_command(args: engine._Args, stem: str, *, poster: bool) -> list[str]:
        command = original_render_command(args, stem, poster=poster)
        if "--transparent" not in command:
            command.insert(-2, "--transparent")
        return command

    engine.render_command = transparent_render_command
    if "--assets-only" not in sys.argv and engine.staging_dir().exists():
        shutil.rmtree(engine.staging_dir())
    result = engine.main()
    if result == 0 and "--assets-only" not in sys.argv:
        review = _extract_review_frames()
        print(
            "review: "
            f"frames={review['frame_count']} "
            f"alpha={review['alpha_extrema'][0]}..{review['alpha_extrema'][1]} "
            f"sheets={', '.join(review['contact_sheets'])}"
        )
    return result


if __name__ == "__main__":
    raise SystemExit(main())
