#!/usr/bin/env -S uv run --script
# /// script
# dependencies = [
#   "imageio-ffmpeg>=0.6.0",
#   "manim>=0.19.0",
#   "pillow>=10.0.0",
# ]
# ///

from __future__ import annotations

import argparse
import math
import os
import shutil
import subprocess
import sys
from pathlib import Path

SPIKE_DIR = Path(__file__).resolve().parent
REPO_ROOT = SPIKE_DIR.parent.parent
SPIKE_NAME = SPIKE_DIR.name
OUTPUT_DIR = REPO_ROOT / "videos" / SPIKE_NAME
STAGING_DIR = OUTPUT_DIR / ".manim"
REVIEW_CADENCE = 0.3
REVIEW_DIR = OUTPUT_DIR / "review-frames-0.3s"

PRIMARY_RED = "#9e1b32"
WHITE = "#ffffff"
GRAY = "#333e48"
GRAY_200 = "#cfcfcf"
GRAY_300 = "#b5b5b5"
GRAY_600 = "#696969"
GRAY_700 = "#4f4f4f"
PAGE_BACKGROUND = "#f7f7f7"
FONT_FAMILY = "Arial"


class _Args(argparse.Namespace):
    quality: str
    preview: bool


def parse_args() -> _Args:
    parser = argparse.ArgumentParser(description="Render the time-rail-sequence Manim spike.")
    parser.add_argument(
        "--quality",
        choices=("low", "medium", "high", "production", "4k"),
        default="medium",
        help="Manim quality preset. Defaults to medium for quick iteration.",
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


def render_command(args: _Args, *, poster: bool) -> list[str]:
    STAGING_DIR.mkdir(parents=True, exist_ok=True)
    output = OUTPUT_DIR / ("time-rail-sequence.png" if poster else "time-rail-sequence.webm")
    command = [
        sys.executable,
        "-m",
        "manim",
        "render",
        quality_flag(args.quality),
        "-r",
        "1600,900",
        "-o",
        output.stem,
        "--media_dir",
        str(STAGING_DIR),
    ]
    if poster:
        command.append("-s")
    else:
        command.extend(["--format", "webm", "-t"])
        if args.preview:
            command.append("-p")
    command.extend([str(Path(__file__).resolve()), "TimeRailSequenceScene"])
    return command


def promote_rendered_file(target_name: str, destination: Path) -> None:
    matches = sorted(STAGING_DIR.glob(f"**/{target_name}"), key=lambda path: path.stat().st_mtime)
    if not matches:
        raise FileNotFoundError(f"Could not find {target_name} under {STAGING_DIR}")
    destination.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(matches[-1], destination)


def write_review_frames(video: Path, cadence: float = REVIEW_CADENCE) -> dict[str, object]:
    import imageio_ffmpeg
    from PIL import Image, ImageDraw, ImageFont

    raw_dir = REVIEW_DIR / "raw-alpha"
    frames_dir = REVIEW_DIR / "frames"
    sheets_dir = REVIEW_DIR / "sheets"
    for directory in (raw_dir, frames_dir, sheets_dir):
        if directory.exists():
            shutil.rmtree(directory)
        directory.mkdir(parents=True, exist_ok=True)

    ffmpeg = Path(imageio_ffmpeg.get_ffmpeg_exe()).resolve()
    subprocess.run(
        [
            str(ffmpeg),
            "-hide_banner",
            "-y",
            "-c:v",
            "libvpx-vp9",
            "-i",
            str(video),
            "-vf",
            f"fps={1 / cadence}",
            "-pix_fmt",
            "rgba",
            str(raw_dir / "raw-%04d.png"),
        ],
        check=True,
    )

    saved: list[tuple[float, Path, Image.Image]] = []
    alpha_min, alpha_max = 255, 0
    for index, frame_path in enumerate(sorted(raw_dir.glob("raw-*.png"))):
        timestamp = index * cadence
        rgba = Image.open(frame_path).convert("RGBA")
        frame_alpha_min, frame_alpha_max = rgba.getchannel("A").getextrema()
        alpha_min = min(alpha_min, frame_alpha_min)
        alpha_max = max(alpha_max, frame_alpha_max)
        background = Image.new("RGBA", rgba.size, (255, 255, 255, 255))
        background.alpha_composite(rgba)
        review_frame = background.convert("RGB")
        output = frames_dir / f"frame-{index + 1:04d}-t{timestamp:06.3f}.png"
        review_frame.save(output)
        saved.append((timestamp, output, review_frame.copy()))

    if not saved:
        raise RuntimeError(f"No review frames extracted from {video}")

    thumb_width = 320
    thumb_height = round(saved[0][2].height * thumb_width / saved[0][2].width)
    columns = 5
    label_height = 28
    pad = 16
    rows_per_sheet = 9
    try:
        font = ImageFont.truetype("arial.ttf", 15)
    except OSError:
        font = ImageFont.load_default()

    contact_sheets: list[str] = []
    for sheet_index in range(math.ceil(len(saved) / (columns * rows_per_sheet))):
        batch = saved[sheet_index * columns * rows_per_sheet : (sheet_index + 1) * columns * rows_per_sheet]
        rows = math.ceil(len(batch) / columns)
        sheet = Image.new(
            "RGB",
            (columns * thumb_width + (columns + 1) * pad, rows * (thumb_height + label_height) + (rows + 1) * pad),
            WHITE,
        )
        draw = ImageDraw.Draw(sheet)
        for frame_index, (timestamp, _, frame) in enumerate(batch):
            row, column = divmod(frame_index, columns)
            x = pad + column * (thumb_width + pad)
            y = pad + row * (thumb_height + label_height)
            thumb = frame.resize((thumb_width, thumb_height), Image.Resampling.LANCZOS)
            sheet.paste(thumb, (x, y + label_height))
            draw.text((x, y + 4), f"t={timestamp:05.1f}s", fill=GRAY, font=font)
        sheet_path = sheets_dir / f"contact-sheet-{sheet_index + 1:02d}.png"
        sheet.save(sheet_path)
        contact_sheets.append(str(sheet_path))

    return {
        "frames": len(saved),
        "alpha_extrema": [alpha_min, alpha_max],
        "review_dir": str(REVIEW_DIR),
        "contact_sheets": contact_sheets,
    }


from manim import DOWN, LEFT, RIGHT, UP, Circle, FadeIn, Line, Rectangle, Scene, Text, Transform, VGroup, linear


class TimeRailSequenceScene(Scene):
    def construct(self) -> None:
        if os.environ.get("SPIKE_RENDER_TARGET") == "poster":
            self.camera.background_color = PAGE_BACKGROUND
        else:
            self.camera.background_opacity = 0.0

        stage = Rectangle(width=12.8, height=7.15, stroke_width=0, fill_color=PAGE_BACKGROUND, fill_opacity=0.96)
        rail_x = -5.0
        card_width = 9.2
        card_height = 1.32
        card_center_x = 0.46
        top_y = 2.58
        bottom_y = -2.66
        rail_start = LEFT * abs(rail_x) + UP * top_y
        rail_end = LEFT * abs(rail_x) + DOWN * abs(bottom_y)
        base_rail = Line(rail_start, rail_end, color=GRAY_300, stroke_width=8)
        active_rail = Line(rail_start, rail_start, color=PRIMARY_RED, stroke_width=9)
        terminal_cap = Line(rail_end + LEFT * 0.24, rail_end + RIGHT * 0.24, color=PRIMARY_RED, stroke_width=6)
        terminal_cap.set_opacity(0)

        steps = [
            ("00", "Context appears", "A pending structure is already\nvisible before motion starts.", 1.62),
            ("01", "Time advances", "The rail reaches the next tick\nbefore the card resolves.", 0.0),
            ("02", "Outcome holds", "The resolved stack keeps time\nas the visible narrator.", -1.62),
        ]

        slots = VGroup()
        tick_branches = VGroup()
        pending_marks = VGroup()
        active_marks = []
        cards = []
        for step, title, body, y in steps:
            slot = Rectangle(
                width=card_width,
                height=card_height,
                stroke_color=GRAY_200,
                stroke_width=2,
                fill_color=WHITE,
                fill_opacity=0.0,
            )
            slot.move_to(RIGHT * card_center_x + UP * y)
            slots.add(slot)

            mark_position = LEFT * abs(rail_x) + UP * y
            branch = Line(
                mark_position + RIGHT * 0.24,
                slot.get_left() + LEFT * 0.04,
                color=GRAY_200,
                stroke_width=3,
            )
            branch.set_opacity(0.34)
            tick_branches.add(branch)

            pending = Circle(radius=0.14, color=GRAY_300, stroke_width=2)
            pending.set_fill(WHITE, opacity=1)
            pending.move_to(mark_position)
            pending_marks.add(pending)

            active = Circle(radius=0.2, color=PRIMARY_RED, stroke_width=3)
            active.set_fill(WHITE, opacity=1)
            active.move_to(mark_position)
            active_marks.append(active)

            cards.append(self.build_card(step, title, body, card_width, card_height).move_to(slot))

        if os.environ.get("SPIKE_RENDER_TARGET") == "poster":
            self.add(stage)
        self.add(base_rail, tick_branches, active_rail, slots, pending_marks, terminal_cap)
        self.wait(2.8)

        for index, (_, _, _, y) in enumerate(steps):
            mark_position = LEFT * abs(rail_x) + UP * y
            self.play(active_rail.animate.put_start_and_end_on(rail_start, mark_position), run_time=1.2, rate_func=linear)
            self.play(
                Transform(pending_marks[index], active_marks[index]),
                tick_branches[index].animate.set_color(PRIMARY_RED).set_stroke(width=5).set_opacity(0.9),
                slots[index].animate.set_stroke(color=PRIMARY_RED, width=2.5, opacity=0.55),
                FadeIn(cards[index], shift=RIGHT * 0.24),
                run_time=1.2,
            )
            self.play(
                tick_branches[index].animate.set_color(GRAY_300).set_stroke(width=3).set_opacity(0.42),
                slots[index].animate.set_stroke(color=GRAY_200, width=2, opacity=0.22),
                run_time=0.35,
            )
            self.wait(2.4)

        self.play(
            active_rail.animate.put_start_and_end_on(rail_start, rail_end),
            terminal_cap.animate.set_opacity(1),
            run_time=0.8,
            rate_func=linear,
        )
        self.wait(6.4)

    def build_card(self, step: str, title: str, body: str, width: float, height: float) -> VGroup:
        background = Rectangle(width=width, height=height, stroke_color=GRAY_200, stroke_width=2, fill_color=WHITE, fill_opacity=0.98)
        accent = Rectangle(width=0.12, height=height, stroke_width=0, fill_color=PRIMARY_RED, fill_opacity=1)
        accent.move_to(background.get_left() + RIGHT * 0.06)
        badge = Rectangle(width=0.78, height=0.34, stroke_width=0, fill_color=GRAY_700, fill_opacity=0.96)
        badge_label = Text(step, font=FONT_FAMILY, font_size=15, color=WHITE)
        badge_group = VGroup(badge, badge_label)
        badge_group.move_to(background.get_left() + RIGHT * 0.72 + UP * 0.29)
        title_text = Text(title, font=FONT_FAMILY, font_size=29, color=GRAY)
        body_text = Text(body, font=FONT_FAMILY, font_size=16, color=GRAY_600)
        text_block = VGroup(title_text, body_text).arrange(DOWN, aligned_edge=LEFT, buff=0.08)
        text_block.next_to(badge_group, RIGHT, buff=0.42)
        text_block.align_to(badge_group, UP).shift(DOWN * 0.03)
        return VGroup(background, accent, badge_group, text_block)


def main() -> int:
    args = parse_args()
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    video_target = OUTPUT_DIR / "time-rail-sequence.webm"
    for poster in (False, True):
        env_target = "poster" if poster else "video"
        result = subprocess.run(render_command(args, poster=poster), check=False, env={**os.environ, "SPIKE_RENDER_TARGET": env_target})
        if result.returncode != 0:
            return result.returncode
        target = OUTPUT_DIR / ("time-rail-sequence.png" if poster else "time-rail-sequence.webm")
        promote_rendered_file(target.name, target)
    review = write_review_frames(video_target)
    print(
        "Review frames: "
        f"{review['frames']} at {REVIEW_CADENCE}s cadence; "
        f"alpha={review['alpha_extrema'][0]}..{review['alpha_extrema'][1]}; "
        f"sheets={', '.join(review['contact_sheets'])}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
