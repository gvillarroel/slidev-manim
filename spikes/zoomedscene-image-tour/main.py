#!/usr/bin/env -S uv run --script
# /// script
# dependencies = [
#   "manim>=0.20.0",
#   "pillow>=10.0.0",
# ]
# ///

from __future__ import annotations

import argparse
import os
import shutil
import subprocess
import sys
import urllib.request
from pathlib import Path

import numpy as np
from manim import (
    LEFT,
    RIGHT,
    UP,
    ImageMobject,
    Rectangle,
    VGroup,
    WHITE,
    ZoomedScene,
    config,
    smooth,
)
from PIL import Image

config.frame_width = 16
config.frame_height = 9

SPIKE_DIR = Path(__file__).resolve().parent
REPO_ROOT = SPIKE_DIR.parent.parent
SPIKE_NAME = SPIKE_DIR.name
OUTPUT_DIR = REPO_ROOT / "videos" / SPIKE_NAME
STAGING_DIR = OUTPUT_DIR / ".manim"
ASSET_DIR = SPIKE_DIR / "assets"
SOURCE_ASSET_PATH = ASSET_DIR / "artemis-i-earth-after-opf.jpg"
BACKGROUND_IMAGE_PATH = OUTPUT_DIR / "artemis-i-earth-after-opf-16x9.jpg"
VIDEO_PATH = OUTPUT_DIR / f"{SPIKE_NAME}.webm"
POSTER_PATH = OUTPUT_DIR / f"{SPIKE_NAME}.png"

SOURCE_PAGE_URL = "https://www.nasa.gov/humans-in-space/view-the-best-images-from-nasas-artemis-i-mission/"
SOURCE_IMAGE_URL = "https://www.nasa.gov/wp-content/uploads/2022/12/artemis_i_earth_after_opf.jpg?w=2048"

IMAGE_DISPLAY_WIDTH = 14.4
IMAGE_DISPLAY_HEIGHT = 8.1
CROP_WIDTH = 2048
CROP_HEIGHT = 1152
CROP_TOP = 160
ZOOM_DISPLAY_WIDTH = 5.08
ZOOM_DISPLAY_HEIGHT = 2.86
ZOOM_FRAME_RATIO = ZOOM_DISPLAY_HEIGHT / ZOOM_DISPLAY_WIDTH

WHITE_TOKEN = "#ffffff"
PRIMARY_RED = "#9e1b32"


class _Args(argparse.Namespace):
    quality: str
    refresh_source: bool


HOTSPOTS = [
    {"pixel": (410, 448), "width": 1.42, "name": "Orion hull detail"},
    {"pixel": (1290, 612), "width": 1.58, "name": "lunar crater field"},
    {"pixel": (1788, 690), "width": 1.02, "name": "crescent Earth"},
    {"pixel": (374, 1015), "width": 1.36, "name": "service module hardware"},
]


def parse_args() -> _Args:
    parser = argparse.ArgumentParser(description="Render the ZoomedScene real Artemis photo tour spike.")
    parser.add_argument("--quality", choices=("low", "medium", "high", "production", "4k"), default="medium")
    parser.add_argument("--refresh-source", action="store_true", help="Download the NASA source photo again.")
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
        "--fps",
        "12",
        "-o",
        target.stem,
        "--media_dir",
        str(STAGING_DIR),
    ]
    command.append("-s" if poster else "--format=webm")
    command.extend([str(Path(__file__).resolve()), "ZoomedSceneImageTour"])
    return command


def promote(target_name: str, destination: Path) -> None:
    matches = sorted(STAGING_DIR.glob(f"**/{target_name}"), key=lambda path: path.stat().st_mtime)
    if not matches:
        raise FileNotFoundError(target_name)
    destination.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(matches[-1], destination)


def download_source_photo(force: bool = False) -> None:
    if SOURCE_ASSET_PATH.exists() and not force:
        return
    ASSET_DIR.mkdir(parents=True, exist_ok=True)
    request = urllib.request.Request(SOURCE_IMAGE_URL, headers={"User-Agent": "slidev-manim-spike/1.0"})
    with urllib.request.urlopen(request, timeout=30) as response:
        SOURCE_ASSET_PATH.write_bytes(response.read())


def prepare_background_image(force_source: bool = False) -> None:
    download_source_photo(force=force_source)
    if BACKGROUND_IMAGE_PATH.exists() and BACKGROUND_IMAGE_PATH.stat().st_mtime >= SOURCE_ASSET_PATH.stat().st_mtime:
        return

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    source = Image.open(SOURCE_ASSET_PATH).convert("RGB")
    crop = source.crop((0, CROP_TOP, CROP_WIDTH, CROP_TOP + CROP_HEIGHT))
    crop.save(BACKGROUND_IMAGE_PATH, quality=95)


def scene_point_from_pixel(pixel: tuple[int, int]) -> np.ndarray:
    px, py = pixel
    x = (px / CROP_WIDTH - 0.5) * IMAGE_DISPLAY_WIDTH
    y = (0.5 - py / CROP_HEIGHT) * IMAGE_DISPLAY_HEIGHT
    return np.array([x, y, 0.0])


def display_position_for(point: np.ndarray) -> np.ndarray:
    side = RIGHT if point[0] < 0 else LEFT
    return side * 4.52 + UP * 2.43


class ZoomedSceneImageTour(ZoomedScene):
    def __init__(self, **kwargs) -> None:
        first_point = scene_point_from_pixel(HOTSPOTS[0]["pixel"])
        super().__init__(
            zoom_factor=0.24,
            zoomed_display_height=ZOOM_DISPLAY_HEIGHT,
            zoomed_display_width=ZOOM_DISPLAY_WIDTH,
            zoomed_display_center=display_position_for(first_point),
            zoomed_camera_config={"default_frame_stroke_width": 3, "background_opacity": 1},
            image_frame_stroke_width=4,
            **kwargs,
        )

    def construct(self) -> None:
        self.camera.background_color = WHITE

        background = ImageMobject(BACKGROUND_IMAGE_PATH).set(width=IMAGE_DISPLAY_WIDTH)
        background.set_z_index(0)
        self.add(background)

        frame = self.zoomed_camera.frame
        frame.move_to(scene_point_from_pixel(HOTSPOTS[0]["pixel"]))
        frame.set(width=HOTSPOTS[0]["width"])
        frame.set_stroke(color=PRIMARY_RED, width=4, opacity=1)
        frame.set_z_index(20)

        display = self.zoomed_display
        display.set_z_index(30)
        display.display_frame.set_stroke(color=WHITE_TOKEN, width=7, opacity=1)
        display.display_frame.set_fill(opacity=0)
        display.display_frame.set_z_index(31)

        self.wait(2.6)
        self.activate_zooming(animate=False)
        self.wait(3.0)

        for hotspot in HOTSPOTS[1:]:
            target = scene_point_from_pixel(hotspot["pixel"])
            display.move_to(display_position_for(target))
            self.play(
                frame.animate.set(width=hotspot["width"]).move_to(target),
                run_time=0.45,
                rate_func=smooth,
            )
            self.wait(3.7)

        proof_boxes = VGroup(
            *[
                Rectangle(
                    width=hotspot["width"],
                    height=hotspot["width"] * ZOOM_FRAME_RATIO,
                    stroke_color=PRIMARY_RED,
                    stroke_width=4,
                    fill_opacity=0,
                ).move_to(scene_point_from_pixel(hotspot["pixel"]))
                for hotspot in HOTSPOTS
            ]
        )
        proof_boxes.set_z_index(15)

        self.remove_foreground_mobjects(frame, display)
        self.remove(frame, display)
        self.add(proof_boxes)
        self.wait(7.2)


def main() -> int:
    args = parse_args()
    prepare_background_image(force_source=args.refresh_source)
    for poster in (False, True):
        env = {**os.environ, "SPIKE_RENDER_TARGET": "poster" if poster else "video"}
        result = subprocess.run(render_command(args, poster), check=False, env=env)
        if result.returncode != 0:
            return result.returncode
        promote((POSTER_PATH if poster else VIDEO_PATH).name, POSTER_PATH if poster else VIDEO_PATH)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
