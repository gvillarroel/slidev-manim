#!/usr/bin/env -S uv run --script
# /// script
# dependencies = [
#   "imageio-ffmpeg>=0.6.0",
#   "manim>=0.20.0",
#   "pillow>=10.0.0",
# ]
# ///

from __future__ import annotations

import argparse
import math
import os
import re
import shutil
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path

import numpy as np
from manim import (
    BLACK,
    DOWN,
    LEFT,
    ORIGIN,
    RIGHT,
    UP,
    Arrow,
    Circle,
    Create,
    Dot,
    FadeIn,
    FadeOut,
    GrowArrow,
    Indicate,
    Line,
    MovingCameraScene,
    Rectangle,
    ReplacementTransform,
    Text,
    VGroup,
    config,
    rate_functions,
)
from manimpango import list_fonts

SPIKE_FILE = Path(__file__).resolve()
SPIKE_DIR = SPIKE_FILE.parent
REPO_ROOT = SPIKE_DIR.parents[1]
SPIKE_NAME = SPIKE_DIR.name
OUTPUT_DIR = REPO_ROOT / "videos" / SPIKE_NAME
STAGING_DIR = OUTPUT_DIR / ".manim"
VIDEO_PATH = OUTPUT_DIR / f"{SPIKE_NAME}.webm"
POSTER_PATH = OUTPUT_DIR / f"{SPIKE_NAME}.png"
REVIEW_ROOT = OUTPUT_DIR / "review-frames"

os.environ.setdefault("MERMAID_UNFOLD_SPIKE_FILE", str(SPIKE_FILE))
os.environ.setdefault("MERMAID_UNFOLD_SPIKE_DIR", str(SPIKE_DIR))
os.environ.setdefault("MERMAID_UNFOLD_TITLE", "State Diagram")
os.environ.setdefault("MERMAID_UNFOLD_FAMILY", "UML")
sys.path.insert(0, str(SPIKE_DIR.parent))

from mermaid_svg_unfold_engine import ensure_fragments, ensure_mermaid_assets, generated_dir

config.frame_width = 16
config.frame_height = 9
config.pixel_width = 1600
config.pixel_height = 900
config.frame_rate = 30
config.transparent = True
config.background_opacity = 0.0

PRIMARY_RED = "#9e1b32"
PAGE_BACKGROUND = "#f7f7f7"
GRAY = "#333e48"
GRAY_100 = "#e7e7e7"
GRAY_200 = "#cfcfcf"
GRAY_300 = "#b5b5b5"
GRAY_500 = "#828282"
WHITE = "#ffffff"
TEXT_FONT = "Open Sans" if "Open Sans" in list_fonts() else "Arial"


@dataclass(frozen=True)
class StateNode:
    key: str
    label: str
    center: tuple[float, float, float]
    width: float = 2.26
    height: float = 0.88


class MermaidSvgUnfoldScene(MovingCameraScene):
    def construct(self) -> None:
        self.camera.background_opacity = 0.0
        poster_mode = os.environ.get("SPIKE_RENDER_TARGET") == "poster"

        nodes = [
            StateNode("source", "Source", (-4.9, 1.24, 0.0), width=2.44, height=1.06),
            StateNode("svg", "Rendered SVG", (-1.55, 1.24, 0.0), width=2.92, height=1.06),
            StateNode("parts", "Decomposed", (1.92, 1.24, 0.0), width=2.82, height=1.06),
            StateNode("video", "Unfolded Video", (1.92, -1.34, 0.0), width=3.18, height=1.06),
        ]
        start = Dot(point=(-6.65, 1.24, 0.0), radius=0.18, color=PRIMARY_RED).set_z_index(6)
        end = Circle(radius=0.23, color=GRAY, stroke_width=3.2).move_to((4.95, -1.34, 0.0)).set_z_index(4)
        end_core = Dot(point=end.get_center(), radius=0.08, color=GRAY).set_z_index(5)

        slots = VGroup(*(self.slot_for(node) for node in nodes))
        cards = VGroup(*(self.card_for(node) for node in nodes))
        labels = VGroup(*(self.label_for(node) for node in nodes))
        slot_labels = VGroup(*(self.slot_label_for(node) for node in nodes))
        connectors = VGroup(
            self.arrow_between(start, slots[0]),
            *[self.arrow_between(slots[index], slots[index + 1]) for index in range(len(slots) - 1)],
            self.arrow_between(slots[-1], end),
        )
        pending_slots = VGroup(slots, slot_labels, connectors, end, end_core)
        state_groups = [VGroup(cards[index], labels[index]).set_z_index(5) for index in range(len(nodes))]

        pulse = Dot(point=start.get_center(), radius=0.115, color=PRIMARY_RED).set_z_index(9)
        receiver_cues = VGroup(*(self.receiver_cue_for(slot) for slot in slots))
        receiver_cues.add(Circle(radius=0.26, color=PRIMARY_RED, stroke_width=3.2).move_to(end))
        receiver_cues.set_opacity(0)

        if poster_mode:
            self.add(pending_slots, cards, labels)
            self.add(*terminal_brackets(VGroup(cards[-1], labels[-1]), buff=0.25))
            return

        self.add(pending_slots, pulse)
        self.wait(2.7)

        self.reveal_state(pulse, state_groups[0], receiver_cues[0], connectors[0], 1.85)
        self.wait(0.6)
        for index in range(1, len(state_groups)):
            self.reveal_state(
                pulse,
                state_groups[index],
                receiver_cues[index],
                connectors[index],
                1.95,
            )
            self.wait(0.62)

        final_cue = receiver_cues[-1]
        self.play(final_cue.animate.set_stroke(opacity=1), run_time=0.28)
        pulse.move_to(connectors[-1].get_start())
        self.play(
            pulse.animate.move_to(connectors[-1].get_end()),
            connectors[-1].animate.set_stroke(PRIMARY_RED, opacity=0.95, width=4.0),
            run_time=1.75,
            rate_func=rate_functions.ease_in_out_cubic,
        )
        self.play(
            FadeOut(final_cue),
            connectors[-1].animate.set_stroke(GRAY_300, opacity=1, width=2.7),
            end.animate.set_stroke(PRIMARY_RED, width=3.4),
            end_core.animate.set_color(PRIMARY_RED),
            run_time=0.48,
        )
        self.wait(0.75)

        output_card = VGroup(cards[-1], labels[-1])
        final_cluster = VGroup(output_card, end, end_core)
        brackets = VGroup(*terminal_brackets(output_card, buff=0.25)).set_z_index(8)
        self.play(
            FadeOut(pulse),
            FadeIn(brackets),
            Indicate(final_cluster, color=PRIMARY_RED, scale_factor=1.025),
            run_time=1.05,
        )
        self.wait(8.0)

    def reveal_state(
        self,
        pulse: Dot,
        state_group: VGroup,
        receiver_cue,
        connector: Arrow,
        run_time: float,
    ) -> None:
        target = connector.get_end()
        self.play(receiver_cue.animate.set_stroke(opacity=1), run_time=0.28)
        pulse.move_to(connector.get_start())
        self.play(
            pulse.animate.move_to(target),
            connector.animate.set_stroke(PRIMARY_RED, opacity=0.95, width=4.0),
            run_time=run_time,
            rate_func=rate_functions.ease_in_out_cubic,
        )
        self.play(
            FadeOut(receiver_cue),
            FadeIn(state_group, shift=UP * 0.04),
            connector.animate.set_stroke(GRAY_300, opacity=1, width=2.7),
            run_time=0.52,
            rate_func=rate_functions.ease_out_cubic,
        )
        self.play(
            state_group[0].animate.set_stroke(PRIMARY_RED, width=2.9),
            run_time=0.22,
        )
        self.play(
            state_group[0].animate.set_stroke(GRAY, width=2.0),
            run_time=0.36,
        )

    def slot_for(self, node: StateNode) -> Rectangle:
        return (
            Rectangle(width=node.width, height=node.height, color=GRAY_200, stroke_width=2.0)
            .move_to(node.center)
            .set_fill(WHITE, opacity=0.2)
            .set_z_index(1)
        )

    def card_for(self, node: StateNode) -> Rectangle:
        return (
            Rectangle(width=node.width, height=node.height, color=GRAY, stroke_width=2.0)
            .move_to(node.center)
            .set_fill(WHITE, opacity=0.92)
            .set_z_index(4)
        )

    def label_for(self, node: StateNode) -> Text:
        label = Text(node.label, font=TEXT_FONT, font_size=30, color=BLACK)
        label.scale_to_fit_width(node.width - 0.28)
        label.move_to(node.center)
        label.set_z_index(6)
        return label

    def slot_label_for(self, node: StateNode) -> Text:
        label = Text(node.label, font=TEXT_FONT, font_size=27, color=GRAY_500)
        label.scale_to_fit_width(node.width - 0.32)
        label.move_to(node.center)
        label.set_opacity(0.46)
        label.set_z_index(2)
        return label

    def receiver_cue_for(self, slot: Rectangle) -> Rectangle:
        cue = Rectangle(
            width=slot.width + 0.18,
            height=slot.height + 0.18,
            color=PRIMARY_RED,
            stroke_width=3.2,
        )
        cue.move_to(slot)
        cue.set_fill(opacity=0)
        cue.set_stroke(opacity=0)
        cue.set_z_index(7)
        return cue

    def arrow_between(self, left, right) -> Arrow:
        start, end = connector_points(left, right, gap=0.11)
        arrow = Arrow(
            start=start,
            end=end,
            buff=0,
            color=GRAY_300,
            stroke_width=2.7,
            max_tip_length_to_length_ratio=0.18,
            max_stroke_width_to_length_ratio=8,
        )
        arrow.set_z_index(2)
        return arrow


def connector_points(left, right, gap: float = 0.08) -> tuple[np.ndarray, np.ndarray]:
    left_center = left.get_center()
    right_center = right.get_center()
    vector = right_center - left_center
    distance = np.linalg.norm(vector)
    if distance == 0:
        direction = RIGHT
    else:
        direction = vector / distance
    return boundary_point(left, direction, gap), boundary_point(right, -direction, gap)


def boundary_point(mobject, direction: np.ndarray, gap: float) -> np.ndarray:
    center = mobject.get_center()
    dx = abs(direction[0])
    dy = abs(direction[1])
    half_w = max(mobject.width / 2, 0.01)
    half_h = max(mobject.height / 2, 0.01)
    if dx < 1e-6:
        scale = half_h / max(dy, 1e-6)
    elif dy < 1e-6:
        scale = half_w / max(dx, 1e-6)
    else:
        scale = min(half_w / dx, half_h / dy)
    return center + direction * (scale + gap)


def terminal_brackets(group: VGroup, buff: float = 0.18) -> list[Line]:
    left = group.get_left()[0] - buff
    right = group.get_right()[0] + buff
    top = group.get_top()[1] + buff
    bottom = group.get_bottom()[1] - buff
    length = 0.28
    gap = 0.08
    specs = [
        ((left, top - gap, 0), (left, top - length, 0)),
        ((left + gap, top, 0), (left + length, top, 0)),
        ((right, top - gap, 0), (right, top - length, 0)),
        ((right - gap, top, 0), (right - length, top, 0)),
        ((left, bottom + gap, 0), (left, bottom + length, 0)),
        ((left + gap, bottom, 0), (left + length, bottom, 0)),
        ((right, bottom + gap, 0), (right, bottom + length, 0)),
        ((right - gap, bottom, 0), (right - length, bottom, 0)),
    ]
    return [Line(start, end, color=PRIMARY_RED, stroke_width=3.0) for start, end in specs]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Render the native Mermaid state unfold spike.")
    parser.add_argument("--quality", choices=("low", "medium", "high", "production", "4k"), default="medium")
    parser.add_argument("--force-mermaid", action="store_true")
    parser.add_argument("--assets-only", action="store_true")
    return parser.parse_args()


def quality_flag(quality: str) -> str:
    return {
        "low": "-ql",
        "medium": "-qm",
        "high": "-qh",
        "production": "-qp",
        "4k": "-qk",
    }[quality]


def render_command(args: argparse.Namespace, stem: str, *, poster: bool) -> list[str]:
    command = [
        sys.executable,
        "-m",
        "manim",
        "render",
        quality_flag(args.quality),
        "-r",
        "1600,900",
        "--transparent",
        "--media_dir",
        str(STAGING_DIR),
        "-o",
        stem,
    ]
    if poster:
        command.append("-s")
    else:
        command.extend(["--format", "webm"])
    command.extend([str(SPIKE_FILE), "MermaidSvgUnfoldScene"])
    return command


def promote(target_name: str, destination: Path) -> None:
    matches = sorted(STAGING_DIR.glob(f"**/{target_name}"), key=lambda path: path.stat().st_mtime)
    if not matches:
        raise FileNotFoundError(f"Could not find {target_name} under {STAGING_DIR}")
    destination.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(matches[-1], destination)


def safe_clear_staging() -> None:
    resolved = STAGING_DIR.resolve()
    output = OUTPUT_DIR.resolve()
    if STAGING_DIR.exists() and output in resolved.parents:
        shutil.rmtree(STAGING_DIR)


def ensure_inspection_assets(force: bool = False) -> None:
    svg_path, _ = ensure_mermaid_assets(force=force)
    ensure_fragments(svg_path, force=force)


def read_duration(video_path: Path) -> float | None:
    import imageio_ffmpeg

    ffmpeg = Path(imageio_ffmpeg.get_ffmpeg_exe()).resolve()
    result = subprocess.run(
        [str(ffmpeg), "-hide_banner", "-i", str(video_path)],
        capture_output=True,
        text=True,
        check=False,
    )
    match = re.search(r"Duration:\s*(\d+):(\d+):(\d+(?:\.\d+)?)", result.stderr)
    if not match:
        return None
    hours, minutes, seconds = match.groups()
    return int(hours) * 3600 + int(minutes) * 60 + float(seconds)


def extract_review_frames(video_path: Path, cadence: float = 0.3) -> dict[str, object]:
    import imageio_ffmpeg
    from PIL import Image

    frames_dir = REVIEW_ROOT / "frames"
    sheets_dir = REVIEW_ROOT / "sheets"
    raw_dir = REVIEW_ROOT / "raw-alpha"
    if REVIEW_ROOT.exists():
        shutil.rmtree(REVIEW_ROOT)
    frames_dir.mkdir(parents=True, exist_ok=True)
    sheets_dir.mkdir(parents=True, exist_ok=True)
    raw_dir.mkdir(parents=True, exist_ok=True)

    ffmpeg = Path(imageio_ffmpeg.get_ffmpeg_exe()).resolve()
    command = [
        str(ffmpeg),
        "-v",
        "error",
        "-c:v",
        "libvpx-vp9",
        "-i",
        str(video_path),
        "-vf",
        f"fps={1 / cadence:.8f},format=rgba",
        "-f",
        "rawvideo",
        "pipe:1",
    ]
    width, height = 1600, 900
    frame_size = width * height * 4
    result = subprocess.run(command, capture_output=True, check=True)
    frame_count = len(result.stdout) // frame_size
    alpha_min, alpha_max = 255, 0
    saved: list[Path] = []

    for index in range(frame_count):
        chunk = result.stdout[index * frame_size : (index + 1) * frame_size]
        image = Image.frombytes("RGBA", (width, height), chunk)
        alpha = image.getchannel("A").getextrema()
        alpha_min = min(alpha_min, alpha[0])
        alpha_max = max(alpha_max, alpha[1])
        raw_path = raw_dir / f"frame-{index:03d}-{index * cadence:06.3f}s.png"
        image.save(raw_path)
        background = Image.new("RGBA", image.size, WHITE)
        background.alpha_composite(image)
        frame_path = frames_dir / f"frame-{index:03d}-{index * cadence:06.3f}s.png"
        background.convert("RGB").save(frame_path)
        saved.append(frame_path)

    sheet_paths = build_contact_sheets(saved, sheets_dir, cadence)
    duration = read_duration(video_path)
    metadata = {
        "video": str(video_path),
        "duration_seconds": round(duration, 3) if duration is not None else None,
        "cadence_seconds": cadence,
        "review_frame_count": frame_count,
        "alpha_extrema": [alpha_min, alpha_max],
        "frames_dir": str(frames_dir),
        "raw_alpha_dir": str(raw_dir),
        "contact_sheets": [str(path) for path in sheet_paths],
    }
    (REVIEW_ROOT / "metadata.json").write_text(f"{metadata}\n", encoding="utf-8")
    print(
        f"Wrote {frame_count} review frames at {cadence:.1f}s cadence; "
        f"duration={metadata['duration_seconds']}s; alpha={alpha_min}..{alpha_max}"
    )
    return metadata


def build_contact_sheets(frames: list[Path], sheets_dir: Path, cadence: float) -> list[Path]:
    from PIL import Image, ImageDraw

    if not frames:
        return []
    thumb_w, thumb_h = 320, 180
    label_h = 24
    columns = 5
    rows = 4
    per_sheet = columns * rows
    font = load_font(15)
    paths: list[Path] = []
    for sheet_index in range(math.ceil(len(frames) / per_sheet)):
        subset = frames[sheet_index * per_sheet : (sheet_index + 1) * per_sheet]
        canvas = Image.new("RGB", (columns * thumb_w, rows * (thumb_h + label_h)), WHITE)
        draw = ImageDraw.Draw(canvas)
        for local_index, frame_path in enumerate(subset):
            global_index = sheet_index * per_sheet + local_index
            col = local_index % columns
            row = local_index // columns
            x = col * thumb_w
            y = row * (thumb_h + label_h)
            image = Image.open(frame_path).convert("RGB").resize((thumb_w, thumb_h), Image.Resampling.LANCZOS)
            canvas.paste(image, (x, y))
            draw.text((x + 8, y + thumb_h + 4), f"{global_index * cadence:05.2f}s", fill=GRAY, font=font)
        path = sheets_dir / f"contact-sheet-{sheet_index + 1:02d}.png"
        canvas.save(path)
        paths.append(path)
    return paths


def load_font(size: int) -> ImageFont.FreeTypeFont | ImageFont.ImageFont:
    from PIL import ImageFont

    for name in ("OpenSans-Regular.ttf", "Open Sans.ttf", "arial.ttf", "DejaVuSans.ttf"):
        try:
            return ImageFont.truetype(name, size)
        except OSError:
            continue
    return ImageFont.load_default()


def render_variant(args: argparse.Namespace) -> None:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    ensure_inspection_assets(force=args.force_mermaid)
    if args.assets_only:
        return

    safe_clear_staging()
    video_env = {**os.environ, "SPIKE_RENDER_TARGET": "video"}
    result = subprocess.run(render_command(args, VIDEO_PATH.stem, poster=False), env=video_env, check=False)
    if result.returncode != 0:
        raise SystemExit(result.returncode)
    promote(VIDEO_PATH.name, VIDEO_PATH)

    poster_env = {**os.environ, "SPIKE_RENDER_TARGET": "poster"}
    result = subprocess.run(render_command(args, POSTER_PATH.stem, poster=True), env=poster_env, check=False)
    if result.returncode != 0:
        raise SystemExit(result.returncode)
    promote(POSTER_PATH.name, POSTER_PATH)
    extract_review_frames(VIDEO_PATH)


def main() -> int:
    render_variant(parse_args())
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
