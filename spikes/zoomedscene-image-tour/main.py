#!/usr/bin/env -S uv run --script
# /// script
# dependencies = [
#   "manim>=0.20.0",
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

import numpy as np
from manim import (
    DOWN,
    LEFT,
    RIGHT,
    UP,
    ApplyWave,
    Create,
    FadeIn,
    FadeOut,
    ImageMobject,
    Rectangle,
    Restore,
    Succession,
    VGroup,
    WHITE,
    ZoomedScene,
    config,
    linear,
    smooth,
)
from PIL import Image, ImageDraw

config.frame_width = 16
config.frame_height = 9

SPIKE_DIR = Path(__file__).resolve().parent
REPO_ROOT = SPIKE_DIR.parent.parent
SPIKE_NAME = SPIKE_DIR.name
OUTPUT_DIR = REPO_ROOT / "videos" / SPIKE_NAME
STAGING_DIR = OUTPUT_DIR / ".manim"
SOURCE_IMAGE_PATH = OUTPUT_DIR / "generated-5k-detail-map.png"
VIDEO_PATH = OUTPUT_DIR / f"{SPIKE_NAME}.webm"
POSTER_PATH = OUTPUT_DIR / f"{SPIKE_NAME}.png"

STAGE_WIDTH = 16.0
STAGE_HEIGHT = 9.0

BLACK = "#000000"
WHITE_TOKEN = "#ffffff"
PAGE_BACKGROUND = "#f7f7f7"
GRAY = "#333e48"
GRAY_100 = "#e7e7e7"
GRAY_200 = "#cfcfcf"
GRAY_300 = "#b5b5b5"
GRAY_400 = "#9c9c9c"
GRAY_500 = "#828282"
GRAY_600 = "#696969"
GRAY_700 = "#4f4f4f"
GRAY_900 = "#1c1c1c"
PRIMARY_RED = "#9e1b32"
PRIMARY_ORANGE = "#e77204"
PRIMARY_YELLOW = "#f1c319"
PRIMARY_GREEN = "#45842a"
PRIMARY_BLUE = "#007298"
PRIMARY_PURPLE = "#652f6c"
HIGHLIGHT_RED = "#ffccd5"


class _Args(argparse.Namespace):
    quality: str
    regenerate_image: bool


HOTSPOTS = [
    (-4.92, 1.52, "greenhouse lattice"),
    (4.32, 1.84, "antenna field"),
    (-3.18, -2.36, "harbor circuitry"),
    (4.66, -2.34, "solar spiral"),
]


def parse_args() -> _Args:
    parser = argparse.ArgumentParser(description="Render the ZoomedScene image tour spike.")
    parser.add_argument("--quality", choices=("low", "medium", "high", "production", "4k"), default="medium")
    parser.add_argument("--regenerate-image", action="store_true", help="Regenerate the deterministic 5K source image.")
    return parser.parse_args(namespace=_Args())


def quality_flag(quality: str) -> str:
    return {"low": "-ql", "medium": "-qm", "high": "-qh", "production": "-qp", "4k": "-qk"}[quality]


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
    command.append("-s" if poster else "--format=webm")
    command.extend([str(Path(__file__).resolve()), "ZoomedSceneImageTour"])
    return command


def promote(target_name: str, destination: Path) -> None:
    matches = sorted(STAGING_DIR.glob(f"**/{target_name}"))
    if not matches:
        raise FileNotFoundError(target_name)
    destination.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(matches[-1], destination)


def rgb(hex_color: str) -> tuple[int, int, int]:
    color = hex_color.lstrip("#")
    return tuple(int(color[index : index + 2], 16) for index in (0, 2, 4))


def rgba(hex_color: str, alpha: int) -> tuple[int, int, int, int]:
    return (*rgb(hex_color), alpha)


def blend(base: str, top: str, amount: float) -> tuple[int, int, int]:
    left = rgb(base)
    right = rgb(top)
    return tuple(round(left[index] * (1 - amount) + right[index] * amount) for index in range(3))


def image_point(x: float, y: float, width: int, height: int) -> tuple[int, int]:
    return (round((x / STAGE_WIDTH + 0.5) * width), round((0.5 - y / STAGE_HEIGHT) * height))


def draw_polyline(
    draw: ImageDraw.ImageDraw,
    points: list[tuple[int, int]],
    fill: tuple[int, int, int, int],
    width: int,
) -> None:
    draw.line(points, fill=fill, width=width, joint="curve")


def draw_micro_blocks(
    draw: ImageDraw.ImageDraw,
    origin: tuple[int, int],
    columns: int,
    rows: int,
    cell: int,
    gap: int,
    palette: list[str],
    alpha: int,
) -> None:
    ox, oy = origin
    for row in range(rows):
        for column in range(columns):
            if (row * 7 + column * 3) % 11 in (0, 6):
                continue
            x0 = ox + column * (cell + gap)
            y0 = oy + row * (cell + gap)
            color = palette[(row + column * 2) % len(palette)]
            draw.rectangle([x0, y0, x0 + cell, y0 + cell], fill=rgba(color, alpha))


def draw_greenhouse(draw: ImageDraw.ImageDraw, width: int, height: int) -> None:
    cx, cy = image_point(-4.92, 1.52, width, height)
    panel_w, panel_h = 1460, 820
    box = [cx - panel_w // 2, cy - panel_h // 2, cx + panel_w // 2, cy + panel_h // 2]
    draw.rectangle(box, fill=rgba(WHITE_TOKEN, 205), outline=rgba(GRAY_600, 210), width=7)
    for offset in range(0, panel_w + 1, 95):
        draw.line([(box[0] + offset, box[1]), (box[0] + offset - 260, box[3])], fill=rgba(PRIMARY_BLUE, 84), width=4)
    for row in range(7):
        y = box[1] + 92 + row * 88
        draw.rounded_rectangle([box[0] + 94, y, box[2] - 96, y + 34], radius=4, fill=rgba(PRIMARY_GREEN, 122))
        for col in range(28):
            x = box[0] + 130 + col * 45 + (row % 2) * 12
            draw.ellipse([x, y - 10, x + 13, y + 3], fill=rgba(PRIMARY_YELLOW, 180))
    for index in range(5):
        x = box[0] + 170 + index * 245
        draw.rectangle([x, box[1] + 560, x + 126, box[1] + 690], fill=rgba(PRIMARY_BLUE, 52), outline=rgba(PRIMARY_BLUE, 190), width=4)
        for stripe in range(4):
            draw.line([(x + 18, box[1] + 580 + stripe * 24), (x + 108, box[1] + 580 + stripe * 24)], fill=rgba(PRIMARY_BLUE, 155), width=3)
    draw.rectangle([box[0] + 52, box[1] + 50, box[0] + 360, box[1] + 94], fill=rgba(PRIMARY_RED, 226))
    draw_micro_blocks(draw, (box[0] + 1030, box[1] + 88), 9, 6, 34, 12, [GRAY_500, GRAY_600, PRIMARY_GREEN], 178)


def draw_antenna_field(draw: ImageDraw.ImageDraw, width: int, height: int) -> None:
    cx, cy = image_point(4.32, 1.84, width, height)
    draw.ellipse([cx - 610, cy - 520, cx + 610, cy + 520], fill=rgba(WHITE_TOKEN, 196), outline=rgba(GRAY_600, 220), width=7)
    for radius in [116, 210, 316, 430, 540]:
        draw.ellipse([cx - radius, cy - radius, cx + radius, cy + radius], outline=rgba(PRIMARY_PURPLE, 116), width=5)
    for spoke in range(24):
        angle = math.tau * spoke / 24
        outer = (cx + round(math.cos(angle) * 542), cy + round(math.sin(angle) * 542))
        inner = (cx + round(math.cos(angle) * 96), cy + round(math.sin(angle) * 96))
        draw.line([inner, outer], fill=rgba(GRAY_400, 132), width=3)
    draw.ellipse([cx - 78, cy - 78, cx + 78, cy + 78], fill=rgba(GRAY_900, 232))
    draw.ellipse([cx - 34, cy - 34, cx + 34, cy + 34], fill=rgba(PRIMARY_ORANGE, 232))
    for index, angle in enumerate([0.38, 1.15, 2.4, 3.55, 4.72, 5.55]):
        px = cx + round(math.cos(angle) * 378)
        py = cy + round(math.sin(angle) * 280)
        draw.ellipse([px - 84, py - 84, px + 84, py + 84], fill=rgba(PAGE_BACKGROUND, 236), outline=rgba(PRIMARY_BLUE, 214), width=6)
        draw.arc([px - 62, py - 62, px + 62, py + 62], start=200, end=345, fill=rgba(PRIMARY_RED if index == 1 else GRAY_700, 226), width=8)
        draw.line([(px, py + 46), (px + 70, py + 120)], fill=rgba(GRAY_700, 190), width=6)
    draw_micro_blocks(draw, (cx - 520, cy + 330), 16, 4, 28, 13, [PRIMARY_BLUE, GRAY_500, PRIMARY_PURPLE], 166)


def draw_harbor_circuit(draw: ImageDraw.ImageDraw, width: int, height: int) -> None:
    cx, cy = image_point(-3.18, -2.36, width, height)
    box_w, box_h = 1540, 880
    box = [cx - box_w // 2, cy - box_h // 2, cx + box_w // 2, cy + box_h // 2]
    draw.rectangle(box, fill=rgba(WHITE_TOKEN, 214), outline=rgba(GRAY_600, 212), width=7)
    water = [box[0] + 70, box[1] + 74, box[0] + 600, box[3] - 78]
    draw.rectangle(water, fill=rgba(PRIMARY_BLUE, 86))
    for y in range(water[1] + 45, water[3], 78):
        draw.line([(water[0] + 22, y), (water[2] - 26, y + 18)], fill=rgba(WHITE_TOKEN, 125), width=4)
    for pier in range(6):
        y = water[1] + 70 + pier * 102
        draw.rectangle([water[2] - 20, y, water[2] + 280, y + 22], fill=rgba(GRAY_700, 202))
        for boat in range(3):
            x = water[0] + 62 + boat * 138 + (pier % 2) * 20
            draw.polygon([(x, y - 32), (x + 74, y - 20), (x + 56, y + 18), (x + 8, y + 14)], fill=rgba(PRIMARY_ORANGE if boat == 1 else WHITE_TOKEN, 214))
    start_x = box[0] + 700
    for lane in range(7):
        y = box[1] + 102 + lane * 94
        draw.line([(start_x, y), (box[2] - 82, y)], fill=rgba(GRAY_500, 142), width=6)
        for node in range(8):
            x = start_x + 52 + node * 88 + (lane % 2) * 20
            draw.rectangle([x, y - 26, x + 44, y + 26], fill=rgba(PRIMARY_GREEN if (node + lane) % 5 == 0 else GRAY_300, 186))
    for column in range(4):
        x = start_x + 78 + column * 190
        draw.line([(x, box[1] + 92), (x, box[3] - 88)], fill=rgba(PRIMARY_RED if column == 1 else GRAY_400, 156), width=5)
    draw_micro_blocks(draw, (box[0] + 710, box[1] + 612), 19, 5, 24, 12, [GRAY_500, PRIMARY_GREEN, PRIMARY_RED], 160)


def draw_solar_spiral(draw: ImageDraw.ImageDraw, width: int, height: int) -> None:
    cx, cy = image_point(4.66, -2.34, width, height)
    panel_w, panel_h = 1420, 920
    box = [cx - panel_w // 2, cy - panel_h // 2, cx + panel_w // 2, cy + panel_h // 2]
    draw.rectangle(box, fill=rgba(WHITE_TOKEN, 205), outline=rgba(GRAY_600, 212), width=7)
    last = None
    for step in range(260):
        angle = step * 0.19
        radius = 8 + step * 1.68
        point = (cx + round(math.cos(angle) * radius), cy + round(math.sin(angle) * radius))
        if last is not None:
            draw.line([last, point], fill=rgba(PRIMARY_RED if step > 190 else GRAY_700, 212), width=10)
        last = point
    for ring in range(8):
        radius = 118 + ring * 54
        color = [PRIMARY_BLUE, PRIMARY_GREEN, PRIMARY_YELLOW, PRIMARY_PURPLE][ring % 4]
        draw.arc([cx - radius, cy - radius, cx + radius, cy + radius], start=ring * 24, end=ring * 24 + 124, fill=rgba(color, 160), width=8)
    for row in range(5):
        for column in range(8):
            x = box[0] + 96 + column * 91
            y = box[1] + 86 + row * 66
            if column < 3 and row < 2:
                continue
            draw.polygon([(x, y), (x + 72, y + 9), (x + 58, y + 46), (x - 10, y + 34)], fill=rgba(PRIMARY_BLUE, 82), outline=rgba(PRIMARY_BLUE, 170))
            draw.line([(x + 14, y + 8), (x + 2, y + 35)], fill=rgba(WHITE_TOKEN, 130), width=2)
    draw_micro_blocks(draw, (box[0] + 940, box[1] + 590), 9, 5, 36, 14, [PRIMARY_ORANGE, GRAY_500, PRIMARY_PURPLE], 168)


def ensure_background_image(force: bool = False) -> None:
    if SOURCE_IMAGE_PATH.exists() and not force:
        return

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    width, height = 5120, 2880
    image = Image.new("RGB", (width, height), PAGE_BACKGROUND)
    draw = ImageDraw.Draw(image, "RGBA")

    for y in range(height):
        amount = y / (height - 1)
        color = blend("#fbfbfb", "#edf1f2", amount)
        draw.line([(0, y), (width, y)], fill=color)

    for x in range(0, width, 80):
        alpha = 48 if x % 400 else 92
        draw.line([(x, 0), (x, height)], fill=rgba(GRAY_200, alpha), width=2 if x % 400 else 4)
    for y in range(0, height, 80):
        alpha = 48 if y % 400 else 92
        draw.line([(0, y), (width, y)], fill=rgba(GRAY_200, alpha), width=2 if y % 400 else 4)

    route_points = [
        image_point(-7.0, 2.9, width, height),
        image_point(-4.92, 1.52, width, height),
        image_point(-1.55, 2.56, width, height),
        image_point(4.32, 1.84, width, height),
        image_point(5.1, -0.2, width, height),
        image_point(4.66, -2.34, width, height),
        image_point(0.4, -3.05, width, height),
        image_point(-3.18, -2.36, width, height),
        image_point(-6.25, -0.72, width, height),
    ]
    draw_polyline(draw, route_points, rgba(GRAY_400, 112), 68)
    draw_polyline(draw, route_points, rgba(WHITE_TOKEN, 176), 30)
    draw_polyline(draw, route_points, rgba(PRIMARY_RED, 90), 8)

    river = [
        image_point(-8.4, -0.2, width, height),
        image_point(-6.2, -0.08, width, height),
        image_point(-4.0, 0.58, width, height),
        image_point(-1.8, 0.16, width, height),
        image_point(0.2, -0.48, width, height),
        image_point(2.1, -0.12, width, height),
        image_point(4.4, -0.62, width, height),
        image_point(8.2, 0.0, width, height),
    ]
    draw_polyline(draw, river, rgba(PRIMARY_BLUE, 54), 126)
    draw_polyline(draw, river, rgba(PRIMARY_BLUE, 86), 56)

    for index in range(92):
        x = 220 + (index * 353) % (width - 440)
        y = 180 + (index * 227) % (height - 360)
        if (x - width * 0.5) ** 2 / (width * 0.42) ** 2 + (y - height * 0.5) ** 2 / (height * 0.38) ** 2 < 0.16:
            continue
        w = 54 + (index * 17) % 128
        h = 34 + (index * 23) % 92
        color = [GRAY_300, GRAY_400, PRIMARY_BLUE, PRIMARY_GREEN, PRIMARY_ORANGE, PRIMARY_PURPLE][index % 6]
        draw.rectangle([x, y, x + w, y + h], fill=rgba(color, 72), outline=rgba(GRAY_600, 72), width=2)
        if index % 4 == 0:
            draw.line([(x + 8, y + h // 2), (x + w - 8, y + h // 2)], fill=rgba(WHITE_TOKEN, 110), width=2)

    draw_greenhouse(draw, width, height)
    draw_antenna_field(draw, width, height)
    draw_harbor_circuit(draw, width, height)
    draw_solar_spiral(draw, width, height)

    for x, y, _ in HOTSPOTS:
        px, py = image_point(x, y, width, height)
        draw.ellipse([px - 24, py - 24, px + 24, py + 24], outline=rgba(PRIMARY_RED, 192), width=7)
        draw.ellipse([px - 8, py - 8, px + 8, py + 8], fill=rgba(PRIMARY_RED, 220))

    image.save(SOURCE_IMAGE_PATH, quality=96)


class ZoomedSceneImageTour(ZoomedScene):
    def __init__(self, **kwargs) -> None:
        super().__init__(
            zoom_factor=0.24,
            zoomed_display_height=2.86,
            zoomed_display_width=5.08,
            zoomed_display_center=RIGHT * 4.82 + UP * 2.55,
            zoomed_camera_config={"default_frame_stroke_width": 3, "background_opacity": 1},
            image_frame_stroke_width=4,
            **kwargs,
        )

    def construct(self) -> None:
        self.camera.background_color = WHITE

        background = ImageMobject(SOURCE_IMAGE_PATH).set(width=STAGE_WIDTH)
        background.set_z_index(0)
        self.add(background)

        first_target = np.array([HOTSPOTS[0][0], HOTSPOTS[0][1], 0.0])
        frame = self.zoomed_camera.frame
        frame.move_to(first_target)
        frame.set_stroke(color=PRIMARY_RED, width=4, opacity=1)
        frame.set_z_index(20)

        display = self.zoomed_display
        display.set_z_index(30)
        display.display_frame.set_stroke(color=WHITE_TOKEN, width=7, opacity=1)
        display.display_frame.set_fill(opacity=0)
        display.display_frame.set_z_index(31)

        self.wait(2.6)
        self.activate_zooming(animate=True)
        self.play(ApplyWave(frame, amplitude=0.05), run_time=0.7)
        self.wait(1.05)

        display_positions = [
            RIGHT * 4.82 + UP * 2.55,
            LEFT * 4.82 + UP * 2.55,
            RIGHT * 4.82 + UP * 2.55,
            LEFT * 4.82 + UP * 2.55,
        ]
        frame_widths = [1.22, 1.08, 1.28, 1.12]

        for index, (x, y, _name) in enumerate(HOTSPOTS[1:], start=1):
            target = np.array([x, y, 0.0])
            display_target = display_positions[index]
            self.play(
                frame.animate.set(width=frame_widths[index]).move_to(target),
                display.animate.move_to(display_target),
                run_time=3.05,
                rate_func=smooth,
            )
            self.play(ApplyWave(frame, amplitude=0.045), run_time=0.55)
            self.wait(1.45)

        proof_boxes = VGroup(
            *[
                Rectangle(width=1.22, height=0.69, stroke_color=PRIMARY_RED, stroke_width=4, fill_opacity=0).move_to(
                    np.array([x, y, 0.0])
                )
                for x, y, _name in HOTSPOTS
            ]
        )
        proof_boxes.set_z_index(15)

        self.play(Create(proof_boxes), run_time=1.0, rate_func=linear)
        display.save_state()
        self.play(
            FadeOut(frame),
            display.animate.scale(0.74).to_edge(DOWN, buff=0.32),
            proof_boxes.animate.set_stroke(opacity=0.75),
            run_time=1.25,
            rate_func=smooth,
        )
        self.play(Restore(display), run_time=0.75, rate_func=smooth)
        self.play(
            Succession(FadeOut(display), FadeIn(proof_boxes, shift=UP * 0.05)),
            run_time=1.1,
            rate_func=smooth,
        )
        self.wait(6.2)


def main() -> int:
    args = parse_args()
    ensure_background_image(force=args.regenerate_image)
    for poster in (False, True):
        env = {**os.environ, "SPIKE_RENDER_TARGET": "poster" if poster else "video"}
        result = subprocess.run(render_command(args, poster), check=False, env=env)
        if result.returncode != 0:
            return result.returncode
        promote((POSTER_PATH if poster else VIDEO_PATH).name, POSTER_PATH if poster else VIDEO_PATH)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
