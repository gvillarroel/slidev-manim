#!/usr/bin/env -S uv run --script
# /// script
# dependencies = [
#   "manim>=0.20.0",
#   "av>=14.0.0",
#   "pillow>=11.0.0",
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
    PI,
    RIGHT,
    UP,
    AnimationGroup,
    Circle,
    Create,
    DashedLine,
    Ellipse,
    FadeIn,
    FadeOut,
    GrowFromCenter,
    LaggedStart,
    Line,
    MoveAlongPath,
    Polygon,
    RoundedRectangle,
    Scene,
    Text,
    VGroup,
    config,
    linear,
    smooth,
)

SPIKE_DIR = Path(__file__).resolve().parent
REPO_ROOT = SPIKE_DIR.parent.parent
SPIKE_NAME = SPIKE_DIR.name
OUTPUT_DIR = REPO_ROOT / "videos" / SPIKE_NAME
STAGING_DIR = OUTPUT_DIR / ".manim"

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
GRAY_400 = "#9c9c9c"
GRAY_600 = "#696969"
PAGE_BACKGROUND = "#f7f7f7"
HIGHLIGHT_GREEN = "#dbffcc"
HIGHLIGHT_BLUE = "#cdf3ff"
HIGHLIGHT_PURPLE = "#f9ccff"
HIGHLIGHT_ORANGE = "#ffe5cc"
HIGHLIGHT_RED = "#ffccd5"
SHADOW_GREEN = "#294d19"
SHADOW_BLUE = "#004d66"
SHADOW_PURPLE = "#431f47"
SHADOW_RED = "#6d1222"
FONT_FAMILY = "Arial"
REVIEW_DIR = OUTPUT_DIR / "review"
REVIEW_FRAMES_DIR = REVIEW_DIR / "frames-0.3s"
REVIEW_SHEETS_DIR = REVIEW_DIR / "sheets-0.3s"


@dataclass(frozen=True)
class Variant:
    key: str
    strong_cards: bool
    wider_columns: bool
    receiver_slots: bool
    activation_bars: bool
    moving_pulse: bool
    label_chips: bool
    cleanup_slots: bool
    final_token: bool
    route_width: float
    pulse_radius: float
    completed_route_opacity: float
    content_first: bool = False


VARIANTS: dict[str, Variant] = {
    "v1": Variant("v1", False, False, False, False, False, False, False, False, 4.6, 0.10, 0.72),
    "v2": Variant("v2", True, True, False, True, False, False, False, False, 5.8, 0.11, 0.76),
    "v3": Variant("v3", True, True, True, True, False, False, False, False, 5.8, 0.11, 0.76),
    "v4": Variant("v4", True, True, True, True, True, False, False, False, 6.3, 0.14, 0.78),
    "v5": Variant("v5", True, True, True, True, True, True, True, False, 6.3, 0.14, 0.62),
    "v6": Variant("v6", True, True, True, True, True, True, True, True, 6.3, 0.15, 0.58),
    "v7": Variant("v7", True, True, True, True, True, True, True, True, 6.7, 0.13, 0.42, True),
}
DEFAULT_VARIANT = "v7"


class _Args(argparse.Namespace):
    quality: str
    variant: str
    all_iterations: bool
    preview: bool


def parse_args() -> _Args:
    parser = argparse.ArgumentParser(description="Render the mermaid-auth-sequence Manim spike.")
    parser.add_argument("--quality", choices=("low", "medium", "high", "production", "4k"), default="medium")
    parser.add_argument("--variant", choices=tuple(VARIANTS), default=DEFAULT_VARIANT)
    parser.add_argument("--all-iterations", action="store_true", help="Render v1 through v6 review variants.")
    parser.add_argument("--preview", action="store_true", help="Open the final rendered video after completion.")
    return parser.parse_args(namespace=_Args())


def quality_flag(quality: str) -> str:
    return {"low": "-ql", "medium": "-qm", "high": "-qh", "production": "-qp", "4k": "-qk"}[quality]


def output_paths(variant: str, *, iteration_output: bool) -> tuple[Path, Path]:
    suffix = f"-{variant}" if iteration_output else ""
    return OUTPUT_DIR / f"{SPIKE_NAME}{suffix}.webm", OUTPUT_DIR / f"{SPIKE_NAME}{suffix}.png"


def render_command(args: _Args, stem: str, *, poster: bool) -> list[str]:
    STAGING_DIR.mkdir(parents=True, exist_ok=True)
    command = [
        sys.executable,
        "-m",
        "manim",
        "render",
        quality_flag(args.quality),
        "-r",
        "1600,900",
        "--format",
        "webm",
        "-o",
        stem,
        "--media_dir",
        str(STAGING_DIR),
    ]
    if not poster:
        command.append("-t")
    if poster:
        command.append("-s")
    elif args.preview:
        command.append("-p")
    command.extend([str(Path(__file__).resolve()), "MermaidAuthSequenceScene"])
    return command


def promote(target_name: str, destination: Path) -> None:
    matches = sorted(STAGING_DIR.glob(f"**/{target_name}"), key=lambda path: path.stat().st_mtime)
    if not matches:
        raise FileNotFoundError(f"Could not find {target_name} under {STAGING_DIR}")
    destination.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(matches[-1], destination)


def render_variant(args: _Args, variant: str, *, iteration_output: bool) -> None:
    if STAGING_DIR.exists():
        shutil.rmtree(STAGING_DIR)
    video_path, poster_path = output_paths(variant, iteration_output=iteration_output)
    env = os.environ.copy()
    env["SPIKE_RENDER_TARGET"] = "video"
    env["SPIKE_ITERATION"] = variant
    result = subprocess.run(render_command(args, video_path.stem, poster=False), check=False, env=env)
    if result.returncode != 0:
        raise SystemExit(result.returncode)
    promote(video_path.name, video_path)

    if not iteration_output or variant == DEFAULT_VARIANT:
        poster_env = os.environ.copy()
        poster_env["SPIKE_RENDER_TARGET"] = "poster"
        poster_env["SPIKE_ITERATION"] = variant
        result = subprocess.run(render_command(args, poster_path.stem, poster=True), check=False, env=poster_env)
        if result.returncode != 0:
            raise SystemExit(result.returncode)
        promote(poster_path.name, poster_path)
    if not iteration_output:
        extract_review_frames(video_path)


def main() -> int:
    args = parse_args()
    if args.all_iterations:
        for variant in VARIANTS:
            render_variant(args, variant, iteration_output=True)
    else:
        render_variant(args, args.variant, iteration_output=False)
    return 0


def point(x: float, y: float) -> np.ndarray:
    return np.array([x, y, 0.0])


def scene_text(label: str, *, font_size: int, color: str) -> Text:
    return Text(label, font=FONT_FAMILY, font_size=font_size, color=color)


def fit_text(text: VGroup | Text, width: float) -> VGroup | Text:
    if text.width > width:
        text.scale_to_fit_width(width)
    return text


def video_metadata(video_path: Path) -> tuple[float, float]:
    import av

    container = av.open(str(video_path))
    stream = container.streams.video[0]
    fps = float(stream.average_rate or 30)
    if stream.duration:
        duration = float(stream.duration * stream.time_base)
    else:
        duration = float(container.duration / av.time_base)
    container.close()
    return duration, fps


def composite_frame(video_path: Path, timestamp: float, fps: float):
    import av
    from PIL import Image

    selected = None
    for target in (timestamp, max(0.0, timestamp - 1 / fps), max(0.0, timestamp - 2 / fps), max(0.0, timestamp - 0.15)):
        container = av.open(str(video_path))
        stream = container.streams.video[0]
        container.seek(int(max(0.0, target) / stream.time_base), stream=stream)
        for frame in container.decode(stream):
            if frame.time is None or frame.time + (0.5 / fps) >= target:
                selected = frame
                break
        container.close()
        if selected is not None:
            break
    if selected is None:
        raise RuntimeError(f"No frame near {timestamp:.3f}s")

    rgba = selected.to_image().convert("RGBA")
    background = Image.new("RGBA", rgba.size, WHITE)
    background.alpha_composite(rgba)
    return background.convert("RGB")


def build_contact_sheets(frames: list[tuple[float, Path]]) -> list[Path]:
    from PIL import Image, ImageDraw, ImageFont

    REVIEW_SHEETS_DIR.mkdir(parents=True, exist_ok=True)
    for old in REVIEW_SHEETS_DIR.glob("*.png"):
        old.unlink()

    font = ImageFont.load_default()
    tile_size = (240, 135)
    columns = 4
    rows = 5
    per_sheet = columns * rows
    pad = 14
    label_height = 18
    paths: list[Path] = []

    for sheet_index in range(math.ceil(len(frames) / per_sheet)):
        chunk = frames[sheet_index * per_sheet : (sheet_index + 1) * per_sheet]
        sheet = Image.new(
            "RGB",
            (
                columns * tile_size[0] + (columns + 1) * pad,
                rows * (tile_size[1] + label_height) + (rows + 1) * pad,
            ),
            PAGE_BACKGROUND,
        )
        draw = ImageDraw.Draw(sheet)
        for index, (timestamp, frame_path) in enumerate(chunk):
            column = index % columns
            row = index // columns
            x = pad + column * (tile_size[0] + pad)
            y = pad + row * (tile_size[1] + label_height + pad)
            image = Image.open(frame_path)
            image.thumbnail(tile_size, Image.Resampling.LANCZOS)
            tile = Image.new("RGB", tile_size, WHITE)
            tile.paste(image, ((tile_size[0] - image.width) // 2, (tile_size[1] - image.height) // 2))
            sheet.paste(tile, (x, y + label_height))
            draw.text((x, y), f"{timestamp:05.2f}s", fill=GRAY, font=font)
            draw.rectangle([x, y + label_height, x + tile_size[0] - 1, y + label_height + tile_size[1] - 1], outline=GRAY_200)
        path = REVIEW_SHEETS_DIR / f"contact-sheet-{sheet_index + 1:02d}.png"
        sheet.save(path)
        paths.append(path)
    return paths


def extract_review_frames(video_path: Path, cadence: float = 0.3) -> None:
    REVIEW_FRAMES_DIR.mkdir(parents=True, exist_ok=True)
    for old in REVIEW_FRAMES_DIR.glob("*.png"):
        old.unlink()

    duration, fps = video_metadata(video_path)
    saved: list[tuple[float, Path]] = []
    timestamp = 0.0
    while timestamp <= duration + 1e-6:
        image = composite_frame(video_path, timestamp, fps)
        path = REVIEW_FRAMES_DIR / f"frame-{len(saved):04d}-{timestamp:06.2f}s.png"
        image.save(path)
        saved.append((timestamp, path))
        timestamp = round(timestamp + cadence, 6)
    if duration - saved[-1][0] > cadence * 0.4:
        timestamp = max(0.0, duration - 0.05)
        image = composite_frame(video_path, timestamp, fps)
        path = REVIEW_FRAMES_DIR / f"frame-{len(saved):04d}-{timestamp:06.2f}s.png"
        image.save(path)
        saved.append((timestamp, path))

    sheets = build_contact_sheets(saved)
    print(f"review_frames={len(saved)} cadence={cadence}s sheets={', '.join(str(path) for path in sheets)}")


def soft_stage() -> RoundedRectangle:
    return RoundedRectangle(
        width=12.72,
        height=6.95,
        corner_radius=0.34,
        stroke_color=GRAY_200,
        stroke_width=0,
        fill_color=PAGE_BACKGROUND,
        fill_opacity=0.96,
    )


def api_icon(color: str) -> VGroup:
    rail = RoundedRectangle(width=0.10, height=0.42, corner_radius=0.04, stroke_width=0, fill_color=color, fill_opacity=1)
    cap_top = Line(LEFT * 0.15 + UP * 0.15, RIGHT * 0.15 + UP * 0.15, color=color, stroke_width=3.2)
    cap_bottom = Line(LEFT * 0.15 + DOWN * 0.15, RIGHT * 0.15 + DOWN * 0.15, color=color, stroke_width=3.2)
    return VGroup(rail, cap_top, cap_bottom)


def service_icon(color: str) -> VGroup:
    core = Circle(radius=0.12, stroke_color=color, stroke_width=3, fill_color=color, fill_opacity=0.18)
    arm_a = Line(LEFT * 0.22, RIGHT * 0.22, color=color, stroke_width=3).rotate(PI / 5)
    arm_b = Line(LEFT * 0.22, RIGHT * 0.22, color=color, stroke_width=3).rotate(-PI / 5)
    return VGroup(arm_a, arm_b, core)


def database_icon(color: str) -> VGroup:
    top = Ellipse(width=0.52, height=0.18, stroke_color=color, stroke_width=3, fill_opacity=0)
    mid = Line(LEFT * 0.24, RIGHT * 0.24, color=color, stroke_width=3).shift(DOWN * 0.12)
    bottom = Line(LEFT * 0.22, RIGHT * 0.22, color=color, stroke_width=3).shift(DOWN * 0.25)
    sides = VGroup(
        Line(LEFT * 0.24 + UP * 0.02, LEFT * 0.24 + DOWN * 0.25, color=color, stroke_width=3),
        Line(RIGHT * 0.24 + UP * 0.02, RIGHT * 0.24 + DOWN * 0.25, color=color, stroke_width=3),
    )
    return VGroup(top, mid, bottom, sides)


def participant_card(label: str, role: str, color: str, highlight: str, variant: Variant) -> VGroup:
    width = (2.95 if label != "User Database" else 3.15) if variant.content_first else (2.75 if label != "User Database" else 3.05)
    card = RoundedRectangle(width=width, height=0.9, corner_radius=0.22)
    if variant.content_first:
        card.set_stroke(GRAY_300, width=2.2, opacity=1)
        card.set_fill(WHITE, opacity=1)
        text_color = GRAY
        icon_color = GRAY_600
    elif variant.strong_cards:
        card.set_stroke(color, width=0)
        card.set_fill(color, opacity=1)
        text_color = WHITE
        icon_color = WHITE
    else:
        card.set_stroke(color, width=4, opacity=0.9)
        card.set_fill(highlight, opacity=0.94)
        text_color = GRAY
        icon_color = color

    if variant.content_first and label == "Public API":
        label_text = VGroup(
            scene_text("Public", font_size=23, color=text_color),
            scene_text("API", font_size=23, color=text_color),
        ).arrange(RIGHT, buff=0.14)
    else:
        label_text = scene_text(label, font_size=23 if variant.content_first else 24, color=text_color)
    label_text = fit_text(label_text, width - (1.04 if variant.content_first else 0.86))
    label_text.move_to(card.get_center() + RIGHT * (0.34 if variant.content_first else 0.19))
    if role == "api":
        icon = api_icon(icon_color)
    elif role == "service":
        icon = service_icon(icon_color)
    else:
        icon = database_icon(icon_color)
    icon.move_to(card.get_left() + RIGHT * 0.42)

    type_strip = RoundedRectangle(
        width=width * 0.68,
        height=0.09,
        corner_radius=0.04,
        stroke_width=0,
        fill_color=GRAY_300 if variant.content_first else (WHITE if variant.strong_cards else color),
        fill_opacity=0.82 if variant.content_first else (0.42 if variant.strong_cards else 0.72),
    )
    type_strip.move_to(card.get_top() + DOWN * 0.16)
    return VGroup(card, type_strip, icon, label_text)


def lifeline(x: float, y_top: float, y_bottom: float) -> DashedLine:
    line = DashedLine(
        point(x, y_top),
        point(x, y_bottom),
        dash_length=0.11,
        dashed_ratio=0.62,
        color=GRAY_300,
        stroke_width=1.9,
    )
    line.set_opacity(0.56)
    return line


def activation_bar(x: float, y_top: float, y_bottom: float, color: str, opacity: float = 0.86) -> RoundedRectangle:
    height = abs(y_top - y_bottom)
    bar = RoundedRectangle(
        width=0.17,
        height=height,
        corner_radius=0.08,
        stroke_width=0,
        fill_color=color,
        fill_opacity=opacity,
    )
    bar.move_to(point(x, (y_top + y_bottom) / 2))
    return bar


def arrowhead(end: np.ndarray, direction: np.ndarray, color: str, *, scale: float = 1.0) -> Polygon:
    unit = direction / max(np.linalg.norm(direction), 0.001)
    perp = np.array([-unit[1], unit[0], 0.0])
    length = 0.24 * scale
    half_width = 0.10 * scale
    return Polygon(
        end,
        end - unit * length + perp * half_width,
        end - unit * length - perp * half_width,
        stroke_width=0,
        fill_color=color,
        fill_opacity=1,
    )


def message_label(text: str, center: np.ndarray, color: str, variant: Variant, *, above: bool) -> VGroup:
    offset = UP * 0.25 if above else DOWN * 0.25
    if variant.content_first:
        label = fit_text(scene_text(text, font_size=18, color=color), 1.65)
    else:
        label = fit_text(scene_text(text, font_size=20 if variant.label_chips else 21, color=WHITE if variant.label_chips else color), 1.7)
    label.move_to(center + offset)
    if not variant.label_chips:
        return VGroup(label)
    chip = RoundedRectangle(
        width=label.width + 0.34,
        height=label.height + 0.20,
        corner_radius=0.05 if variant.content_first else 0.13,
        stroke_color=color,
        stroke_width=1.4 if variant.content_first else 0,
        fill_color=WHITE if variant.content_first else color,
        fill_opacity=0.98 if variant.content_first else 0.96,
    )
    chip.move_to(label)
    return VGroup(chip, label)


def build_message(
    start_x: float,
    end_x: float,
    y: float,
    label: str,
    color: str,
    variant: Variant,
    *,
    dashed: bool,
    above: bool,
) -> VGroup:
    direction = np.sign(end_x - start_x) or 1.0
    start = point(start_x + 0.28 * direction, y)
    end = point(end_x - 0.28 * direction, y)
    if dashed:
        line = DashedLine(
            start,
            end,
            dash_length=0.18,
            dashed_ratio=0.58,
            color=color,
            stroke_width=variant.route_width,
        )
    else:
        line = Line(start, end, color=color, stroke_width=variant.route_width)
    tip = arrowhead(end, end - start, color)
    label_group = message_label(label, (start + end) / 2, color, variant, above=above)
    path = Line(start, end)
    path.set_opacity(0)
    group = VGroup(line, tip, label_group, path)
    group.route = VGroup(line, tip)  # type: ignore[attr-defined]
    group.label_group = label_group  # type: ignore[attr-defined]
    group.path = path  # type: ignore[attr-defined]
    return group


def receiver_slot(x: float, y: float, color: str) -> RoundedRectangle:
    slot = RoundedRectangle(
        width=0.64,
        height=0.34,
        corner_radius=0.15,
        stroke_color=color,
        stroke_width=3.2,
        fill_color=HIGHLIGHT_ORANGE,
        fill_opacity=0.0,
    )
    slot.move_to(point(x, y))
    return slot


def halo_for(card: VGroup, color: str) -> RoundedRectangle:
    halo = RoundedRectangle(
        width=card[0].width + 0.18,
        height=card[0].height + 0.18,
        corner_radius=0.28,
        stroke_color=color,
        stroke_width=4,
        fill_opacity=0,
    )
    halo.move_to(card[0])
    return halo


def final_token_badge() -> VGroup:
    token = RoundedRectangle(
        width=1.26,
        height=0.46,
        corner_radius=0.05,
        stroke_width=0,
        fill_color=PRIMARY_RED,
        fill_opacity=1,
    )
    label = scene_text("Token", font_size=20, color=WHITE)
    label.move_to(token)
    notch = Circle(radius=0.065, stroke_width=0, fill_color=WHITE, fill_opacity=1)
    notch.move_to(token.get_left() + RIGHT * 0.20)
    return VGroup(token, notch, label)


class MermaidAuthSequenceScene(Scene):
    def construct(self) -> None:
        variant = VARIANTS[os.environ.get("SPIKE_ITERATION", DEFAULT_VARIANT)]
        poster_mode = os.environ.get("SPIKE_RENDER_TARGET") == "poster"
        config.transparent = True
        config.background_opacity = 0.0
        self.camera.background_opacity = 0.0
        self.camera.background_color = WHITE

        stage = soft_stage()
        stage.set_z_index(-10)
        if variant.content_first:
            stage.set_opacity(0)

        api_x, db_x, svc_x = (-4.72, 0.0, 4.72) if variant.content_first else ((-4.48, 0.0, 4.48) if variant.wider_columns else (-4.1, 0.0, 4.1))
        card_y = 2.56 if variant.content_first else 2.42
        line_top = 1.86
        line_bottom = -3.06 if variant.content_first else -2.72
        message_ys = (1.28, 0.28, -0.82, -2.08) if variant.content_first else (1.18, 0.18, -0.88, -1.92)

        api = participant_card("Public API", "api", PRIMARY_GREEN, HIGHLIGHT_GREEN, variant).move_to(point(api_x, card_y))
        db = participant_card("User Database", "database", PRIMARY_PURPLE, HIGHLIGHT_PURPLE, variant).move_to(point(db_x, card_y))
        svc = participant_card("Auth Service", "service", PRIMARY_BLUE, HIGHLIGHT_BLUE, variant).move_to(point(svc_x, card_y))

        lifelines = VGroup(
            lifeline(api_x, line_top, line_bottom),
            lifeline(db_x, line_top, line_bottom),
            lifeline(svc_x, line_top, line_bottom),
        )

        activation_color = GRAY_600 if variant.content_first else PRIMARY_BLUE
        db_activation_color = GRAY_400 if variant.content_first else PRIMARY_PURPLE
        svc_bar = activation_bar(svc_x, message_ys[0] + 0.42, message_ys[3] - 0.30, activation_color)
        db_bar = activation_bar(db_x, message_ys[1] + 0.30, message_ys[2] - 0.30, db_activation_color)
        activation = VGroup(svc_bar, db_bar)

        request_color = GRAY_600 if variant.content_first else PRIMARY_ORANGE
        return_color = PRIMARY_RED
        messages = VGroup(
            build_message(api_x, svc_x, message_ys[0], "Authenticate", request_color, variant, dashed=False, above=True),
            build_message(svc_x, db_x, message_ys[1], "Query user", request_color, variant, dashed=False, above=True),
            build_message(db_x, svc_x, message_ys[2], "User data", return_color, variant, dashed=True, above=False),
            build_message(svc_x, api_x, message_ys[3], "Token", return_color, variant, dashed=True, above=False),
        )

        slots = VGroup(
            receiver_slot(svc_x, message_ys[0], PRIMARY_RED if variant.content_first else PRIMARY_YELLOW),
            receiver_slot(db_x, message_ys[1], PRIMARY_RED if variant.content_first else PRIMARY_YELLOW),
            receiver_slot(svc_x, message_ys[2], PRIMARY_RED if variant.content_first else PRIMARY_YELLOW),
            receiver_slot(api_x, message_ys[3], PRIMARY_RED if variant.content_first else PRIMARY_YELLOW),
        )
        pending_slots = VGroup(
            *[
                slot.copy()
                .set_stroke(PRIMARY_RED if variant.content_first else PRIMARY_YELLOW)
                .set_opacity(0.24 if variant.content_first else 0.28)
                for slot in slots
            ]
        )

        halos = VGroup(
            halo_for(api, PRIMARY_RED if variant.content_first else PRIMARY_YELLOW),
            halo_for(svc, PRIMARY_RED if variant.content_first else PRIMARY_YELLOW),
            halo_for(db, PRIMARY_RED if variant.content_first else PRIMARY_YELLOW),
        )

        final_token = final_token_badge().move_to(point(api_x - 0.02, message_ys[3] - 0.58))
        actors = VGroup(api, db, svc)

        if poster_mode:
            for message in messages:
                message.route.set_opacity(variant.completed_route_opacity)  # type: ignore[attr-defined]
            self.add(stage, lifelines, actors)
            if variant.activation_bars:
                self.add(activation)
            self.add(*[message.route for message in messages], *[message.label_group for message in messages])  # type: ignore[attr-defined]
            if variant.final_token:
                self.add(final_token)
            return

        self.add(stage, lifelines, actors)
        if variant.receiver_slots:
            self.add(pending_slots)
        self.wait(2.8)

        if variant.activation_bars:
            self.play(GrowFromCenter(svc_bar), run_time=0.55, rate_func=smooth)

        source_halos = [halos[0], halos[1], halos[2], halos[1]]
        target_halos = [halos[1], halos[2], halos[1], halos[0]]
        active_slots = [slots[index] for index in range(4)]

        for index, message in enumerate(messages):
            source_halo = source_halos[index].copy()
            target_halo = target_halos[index].copy()
            animations = [FadeIn(source_halo, scale=1.03)]
            if variant.receiver_slots:
                animations.append(FadeIn(active_slots[index], scale=0.96))
                animations.append(FadeOut(pending_slots[index]))
            if index == 1 and variant.activation_bars:
                animations.append(GrowFromCenter(db_bar))
            self.play(AnimationGroup(*animations, lag_ratio=0.12), run_time=0.42, rate_func=smooth)

            if variant.moving_pulse:
                pulse = Circle(
                    radius=variant.pulse_radius,
                    stroke_width=0,
                    fill_color=PRIMARY_RED if variant.content_first else PRIMARY_YELLOW,
                    fill_opacity=1,
                ).move_to(message.path.get_start())  # type: ignore[attr-defined]
                self.add(pulse)
                self.play(
                    AnimationGroup(
                        Create(message.route),  # type: ignore[attr-defined]
                        FadeIn(message.label_group, shift=UP * 0.04),  # type: ignore[attr-defined]
                        MoveAlongPath(pulse, message.path),  # type: ignore[attr-defined]
                        lag_ratio=0.0,
                    ),
                    run_time=1.72 if index in (0, 3) else 1.45,
                    rate_func=linear,
                )
                self.play(
                    AnimationGroup(
                        FadeOut(pulse, scale=1.35),
                        FadeIn(target_halo, scale=1.02),
                        lag_ratio=0.0,
                    ),
                    run_time=0.34,
                    rate_func=smooth,
                )
            else:
                self.play(
                    LaggedStart(
                        Create(message.route),  # type: ignore[attr-defined]
                        FadeIn(message.label_group, shift=UP * 0.04),  # type: ignore[attr-defined]
                        lag_ratio=0.24,
                    ),
                    run_time=1.34 if index in (0, 3) else 1.14,
                    rate_func=smooth,
                )
                self.play(FadeIn(target_halo, scale=1.02), run_time=0.24)

            fade_group = [FadeOut(source_halo), FadeOut(target_halo)]
            if variant.cleanup_slots and variant.receiver_slots:
                fade_group.append(FadeOut(active_slots[index]))
            self.play(AnimationGroup(*fade_group, lag_ratio=0.0), run_time=0.32)
            message.route.set_opacity(variant.completed_route_opacity)  # type: ignore[attr-defined]
            self.wait(0.9)

        if variant.cleanup_slots and variant.receiver_slots:
            remaining_slot_fades = [FadeOut(slot) for slot in slots if slot in self.mobjects]
            if remaining_slot_fades:
                self.play(*remaining_slot_fades, run_time=0.2)

        if variant.final_token:
            token_path = Line(point(api_x + 0.2, message_ys[3]), final_token.get_center())
            token_dot = Circle(radius=0.09, stroke_width=0, fill_color=PRIMARY_RED, fill_opacity=1).move_to(token_path.get_start())
            self.add(token_dot)
            self.play(MoveAlongPath(token_dot, token_path), run_time=0.54, rate_func=smooth)
            self.play(FadeOut(token_dot), FadeIn(final_token, shift=DOWN * 0.04), run_time=0.42)
        else:
            self.wait(0.54)

        review_padding = {
            "v1": 2.6,
            "v2": 1.9,
            "v3": 1.9,
            "v4": 0.3,
            "v5": 0.3,
            "v6": 0.0,
            "v7": 0.6,
        }[variant.key]
        self.wait(6.3 + review_padding)


if __name__ == "__main__":
    raise SystemExit(main())
