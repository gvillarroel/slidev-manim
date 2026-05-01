#!/usr/bin/env -S uv run --script
# /// script
# dependencies = [
#   "manim>=0.20.1",
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

from manimpango import list_fonts

from manim import (
    DOWN,
    LEFT,
    RIGHT,
    UP,
    Broadcast,
    Circle,
    Dot,
    FadeIn,
    LaggedStart,
    Line,
    Rectangle,
    Scene,
    Text,
    VGroup,
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
PRIMARY_BLUE = "#007298"
BLACK = "#000000"
WHITE = "#ffffff"
GRAY = "#333e48"
GRAY_100 = "#e7e7e7"
GRAY_200 = "#cfcfcf"
GRAY_300 = "#b5b5b5"
GRAY_600 = "#696969"
GRAY_700 = "#4f4f4f"
PAGE_BACKGROUND = "#f7f7f7"
TEXT_FONT = "Open Sans" if "Open Sans" in list_fonts() else "Arial"


@dataclass(frozen=True)
class TileSpec:
    key: str
    title: str
    detail: str
    col: int
    row: int
    accent: str = PRIMARY_RED


@dataclass(frozen=True)
class Tile:
    spec: TileSpec
    group: VGroup
    frame: Rectangle
    slot: Circle | Rectangle
    focal: Dot


class _Args(argparse.Namespace):
    quality: str


TILE_SPECS = (
    TileSpec("baseline", "stroke shell", "n=5  lag=.20", 0, 0, PRIMARY_RED),
    TileSpec("dense", "dense shell", "n=16  lag=.045", 1, 0, PRIMARY_RED),
    TileSpec("wide_start", "wide start", "initial_width=.70", 2, 0, PRIMARY_BLUE),
    TileSpec("filled", "filled body", "fill opacity > 0", 0, 1, PRIMARY_ORANGE),
    TileSpec("offset_focal", "offset focal", "focal_point wins", 1, 1, PRIMARY_RED),
    TileSpec("residue", "residue hold", "remover=False", 2, 1, PRIMARY_RED),
)

TILE_WIDTH = 3.8
TILE_HEIGHT = 2.18
COL_X = (-4.22, 0.0, 4.22)
ROW_Y = (0.96, -1.72)


def parse_args() -> _Args:
    parser = argparse.ArgumentParser(description="Render the broadcast-limits-lab spike.")
    parser.add_argument("--quality", choices=("low", "medium", "high", "production", "4k"), default="medium")
    return parser.parse_args(namespace=_Args())


def quality_flag(quality: str) -> str:
    return {
        "low": "-ql",
        "medium": "-qm",
        "high": "-qh",
        "production": "-qp",
        "4k": "-qk",
    }[quality]


def render_command(args: _Args, target: Path, *, poster: bool) -> list[str]:
    STAGING_DIR.mkdir(parents=True, exist_ok=True)
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
    if poster:
        command.append("-s")
    else:
        command.extend(["--format=webm", "-t"])
    command.extend([str(Path(__file__).resolve()), "BroadcastLimitsLabScene"])
    return command


def promote(target_name: str, destination: Path) -> None:
    matches = sorted(STAGING_DIR.glob(f"**/{target_name}"), key=lambda path: path.stat().st_mtime)
    if not matches:
        raise FileNotFoundError(target_name)
    destination.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(matches[-1], destination)


def label_text(text: str, *, max_width: float, font_size: int = 22, color: str = GRAY) -> Text:
    label = Text(text, font=TEXT_FONT, font_size=font_size, color=color, line_spacing=0.72)
    if label.width > max_width:
        label.scale_to_fit_width(max_width)
    return label


def slot_center(spec: TileSpec, center):
    if spec.key == "wide_start":
        return center + DOWN * 0.32
    return center + DOWN * 0.18


def make_slot(spec: TileSpec, center) -> Circle | Rectangle:
    if spec.key == "filled":
        return Rectangle(
            width=1.4,
            height=0.88,
            stroke_color=GRAY_600,
            stroke_width=3,
            fill_color=GRAY_100,
            fill_opacity=0.54,
        ).move_to(slot_center(spec, center))
    slot = Circle(radius=0.56, stroke_color=GRAY_600, stroke_width=3, fill_opacity=0).move_to(slot_center(spec, center))
    if spec.key == "wide_start":
        slot.set(width=1.42)
    return slot


def make_broadcast_mobject(spec: TileSpec, center) -> Circle | Rectangle:
    if spec.key == "filled":
        return Rectangle(
            width=1.4,
            height=0.88,
            stroke_color=spec.accent,
            stroke_width=3,
            fill_color=spec.accent,
            fill_opacity=0.28,
        ).move_to(center)
    mob = Circle(radius=0.56, stroke_color=spec.accent, stroke_width=7, fill_opacity=0).move_to(center)
    if spec.key == "wide_start":
        mob.set(width=1.42)
    return mob


def focal_point(spec: TileSpec, center):
    if spec.key == "offset_focal":
        return center + LEFT * 0.54 + DOWN * 0.18
    return slot_center(spec, center)


def make_tile(spec: TileSpec) -> Tile:
    center = RIGHT * COL_X[spec.col] + UP * ROW_Y[spec.row]
    frame = Rectangle(
        width=TILE_WIDTH,
        height=TILE_HEIGHT,
        stroke_color=GRAY_200,
        stroke_width=2,
        fill_color=WHITE,
        fill_opacity=0.96,
    ).move_to(center)
    title = label_text(spec.title, max_width=TILE_WIDTH - 0.56, font_size=22, color=BLACK)
    title.move_to(frame.get_top() + DOWN * 0.32)
    detail = label_text(spec.detail, max_width=TILE_WIDTH - 0.72, font_size=16, color=GRAY_700)
    detail.next_to(title, DOWN, buff=0.08)
    slot = make_slot(spec, center)
    focal = Dot(radius=0.055, color=spec.accent).move_to(focal_point(spec, center))
    vertical = Line(focal.get_center() + UP * 0.14, focal.get_center() + DOWN * 0.14, color=spec.accent, stroke_width=2)
    horizontal = Line(focal.get_center() + LEFT * 0.14, focal.get_center() + RIGHT * 0.14, color=spec.accent, stroke_width=2)
    origin_mark = VGroup(vertical, horizontal)

    if spec.key == "offset_focal":
        ignored_slot = Circle(radius=0.24, stroke_color=GRAY_300, stroke_width=2, fill_opacity=0).move_to(center + RIGHT * 0.4 + DOWN * 0.18)
        group = VGroup(frame, title, detail, slot, ignored_slot, focal, origin_mark)
    else:
        group = VGroup(frame, title, detail, slot, focal, origin_mark)
    return Tile(spec=spec, group=group, frame=frame, slot=slot, focal=focal)


class BroadcastLimitsLabScene(Scene):
    def is_poster(self) -> bool:
        return os.environ.get("SPIKE_RENDER_TARGET") == "poster"

    def construct(self) -> None:
        if self.is_poster():
            self.camera.background_color = WHITE

        stage = Rectangle(
            width=13.35,
            height=7.12,
            stroke_color=GRAY_200,
            stroke_width=2,
            fill_color=PAGE_BACKGROUND,
            fill_opacity=0.96,
        ).shift(DOWN * 0.02)
        title = label_text("Broadcast limits lab", max_width=6.0, font_size=32, color=BLACK)
        title.move_to(UP * 3.18 + LEFT * 3.9)
        source = label_text("manim.animation.specialized.Broadcast", max_width=5.0, font_size=18, color=GRAY_700)
        source.next_to(title, RIGHT, buff=0.34)
        rule = Line(source.get_right() + RIGHT * 0.28, RIGHT * 5.86 + UP * 3.18, color=PRIMARY_RED, stroke_width=5)

        tiles = [make_tile(spec) for spec in TILE_SPECS]
        tile_group = VGroup(*(tile.group for tile in tiles))

        self.add(stage)
        self.play(
            FadeIn(title, shift=UP * 0.1),
            FadeIn(source, shift=UP * 0.1),
            FadeIn(rule),
            LaggedStart(*(FadeIn(tile.group, shift=UP * 0.08) for tile in tiles), lag_ratio=0.06),
            run_time=1.45,
        )
        self.wait(2.65)

        self.play_tiles(
            tiles,
            [
                self.broadcast_for(tiles[0], run_time=3.8),
                self.broadcast_for(tiles[1], n_mobs=16, lag_ratio=0.045, initial_opacity=0.85, run_time=3.8),
                self.broadcast_for(tiles[2], initial_width=0.7, n_mobs=6, lag_ratio=0.18, run_time=3.8),
                self.broadcast_for(tiles[3], n_mobs=5, lag_ratio=0.18, initial_opacity=0.48, run_time=4.1),
                self.broadcast_for(tiles[4], n_mobs=7, lag_ratio=0.16, initial_opacity=0.95, run_time=4.1),
                self.broadcast_for(tiles[5], n_mobs=4, lag_ratio=0.24, final_opacity=0.18, remover=False, run_time=4.1),
            ],
            run_time=4.2,
        )

        self.play(
            tiles[1].frame.animate.set_stroke(PRIMARY_RED, width=4),
            tiles[5].frame.animate.set_stroke(PRIMARY_RED, width=4),
            rule.animate.set_stroke(width=7),
            run_time=0.5,
        )
        self.play(
            self.broadcast_for(tiles[1], n_mobs=24, lag_ratio=0.025, initial_opacity=0.72, run_time=4.4),
            self.broadcast_for(tiles[5], n_mobs=7, lag_ratio=0.12, final_opacity=0.16, remover=False, run_time=4.4),
            rate_func=rate_functions.ease_in_out_cubic,
        )
        self.play(
            tiles[1].frame.animate.set_stroke(GRAY_200, width=2),
            tiles[5].frame.animate.set_stroke(GRAY_200, width=2),
            rule.animate.set_stroke(width=5),
            run_time=0.6,
        )
        self.wait(0.9)

        self.play_tiles(
            [tiles[2], tiles[3], tiles[4]],
            [
                self.broadcast_for(tiles[2], initial_width=0.7, n_mobs=8, lag_ratio=0.12, initial_opacity=0.8, run_time=4.0),
                self.broadcast_for(tiles[3], n_mobs=6, lag_ratio=0.12, initial_opacity=0.42, run_time=4.0),
                self.broadcast_for(tiles[4], n_mobs=9, lag_ratio=0.1, initial_opacity=0.88, run_time=4.0),
            ],
            run_time=4.0,
        )
        self.wait(6.25)

    def play_tiles(self, active_tiles: list[Tile], animations: list[Broadcast], *, run_time: float) -> None:
        self.play(*(tile.frame.animate.set_stroke(PRIMARY_RED, width=3) for tile in active_tiles), run_time=0.45)
        self.play(*animations, run_time=run_time, rate_func=rate_functions.ease_in_out_cubic)
        self.wait(1.0)
        self.play(*(tile.frame.animate.set_stroke(GRAY_200, width=2) for tile in active_tiles), run_time=0.4)

    def broadcast_for(
        self,
        tile: Tile,
        *,
        n_mobs: int = 5,
        initial_opacity: float = 1,
        final_opacity: float = 0,
        initial_width: float = 0.0,
        remover: bool = True,
        lag_ratio: float = 0.2,
        run_time: float = 3.8,
    ) -> Broadcast:
        return Broadcast(
            make_broadcast_mobject(tile.spec, tile.slot.get_center()),
            focal_point=tile.focal.get_center(),
            n_mobs=n_mobs,
            initial_opacity=initial_opacity,
            final_opacity=final_opacity,
            initial_width=initial_width,
            remover=remover,
            lag_ratio=lag_ratio,
            run_time=run_time,
        )


def main() -> int:
    args = parse_args()
    for target, poster in ((VIDEO_PATH, False), (POSTER_PATH, True)):
        env = {**os.environ, "SPIKE_RENDER_TARGET": "poster" if poster else "video"}
        result = subprocess.run(render_command(args, target, poster=poster), check=False, env=env)
        if result.returncode != 0:
            return result.returncode
        promote(target.name, target)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
