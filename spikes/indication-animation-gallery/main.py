#!/usr/bin/env -S uv run --script
# /// script
# dependencies = [
#   "imageio-ffmpeg>=0.6.0",
#   "manim>=0.20.0",
#   "pillow>=11.0.0",
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
    ApplyWave,
    Blink,
    Circumscribe,
    Circle,
    FadeIn,
    FadeOut,
    Flash,
    FocusOn,
    Indicate,
    LaggedStart,
    Line,
    Rectangle,
    Scene,
    ShowPassingFlash,
    ShowPassingFlashWithThinningStrokeWidth,
    Square,
    Text,
    VGroup,
    Wiggle,
)

SPIKE_DIR = Path(__file__).resolve().parent
REPO_ROOT = SPIKE_DIR.parent.parent
SPIKE_NAME = SPIKE_DIR.name
OUTPUT_DIR = REPO_ROOT / "videos" / SPIKE_NAME
STAGING_DIR = OUTPUT_DIR / ".manim"
VIDEO_PATH = OUTPUT_DIR / f"{SPIKE_NAME}.webm"
POSTER_PATH = OUTPUT_DIR / f"{SPIKE_NAME}.png"
REVIEW_FRAMES_DIR = OUTPUT_DIR / "review-frames-0.3s"
CONTACT_SHEET_PATH = OUTPUT_DIR / "review-contact-sheet-0.3s.png"
VALIDATION_PATH = OUTPUT_DIR / "validation.txt"

PRIMARY_RED = "#9e1b32"
WHITE = "#ffffff"
GRAY = "#333e48"
GRAY_100 = "#e7e7e7"
GRAY_200 = "#cfcfcf"
GRAY_300 = "#b5b5b5"
GRAY_600 = "#696969"
GRAY_700 = "#4f4f4f"
PAGE_BACKGROUND = "#f7f7f7"
TEXT_FONT = "Arial"


@dataclass(frozen=True)
class TileSpec:
    key: str
    label: str
    row: int
    col: int


@dataclass(frozen=True)
class Tile:
    spec: TileSpec
    group: VGroup
    frame: Rectangle
    actor: VGroup
    guide: Line | Circle | None
    mark: Square


class _Args(argparse.Namespace):
    quality: str


TILE_SPECS = (
    TileSpec("apply_wave", "ApplyWave", 0, 0),
    TileSpec("blink", "Blink", 0, 1),
    TileSpec("circumscribe", "Circumscribe", 0, 2),
    TileSpec("flash", "Flash", 1, 0),
    TileSpec("focus_on", "FocusOn", 1, 1),
    TileSpec("indicate", "Indicate", 1, 2),
    TileSpec("show_passing_flash", "ShowPassingFlash", 2, 0),
    TileSpec(
        "show_passing_flash_thin",
        "ShowPassingFlash\nWithThinningStrokeWidth",
        2,
        1,
    ),
    TileSpec("wiggle", "Wiggle", 2, 2),
)

TILE_WIDTH = 3.92
TILE_HEIGHT = 1.62
COL_X = (-4.32, 0.0, 4.32)
ROW_Y = (1.7, -0.16, -2.02)


def parse_args() -> _Args:
    parser = argparse.ArgumentParser(description="Render the indication-animation-gallery spike.")
    parser.add_argument("--quality", choices=("low", "medium", "high", "production", "4k"), default="medium")
    return parser.parse_args(namespace=_Args())


def quality_flag(quality: str) -> str:
    return {"low": "-ql", "medium": "-qm", "high": "-qh", "production": "-qp", "4k": "-qk"}[quality]


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
    command.extend([str(Path(__file__).resolve()), "IndicationAnimationGalleryScene"])
    return command


def promote(target_name: str, destination: Path) -> None:
    matches = sorted(STAGING_DIR.glob(f"**/{target_name}"), key=lambda path: path.stat().st_mtime)
    if not matches:
        raise FileNotFoundError(target_name)
    destination.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(matches[-1], destination)


def label_text(text: str, *, max_width: float, font_size: int = 21) -> Text:
    line_spacing = 0.5 if "\n" in text else 0.62
    label = Text(text, font=TEXT_FONT, font_size=font_size, color=GRAY, line_spacing=line_spacing)
    if label.width > max_width:
        label.scale_to_fit_width(max_width)
    return label


def make_actor() -> VGroup:
    shadow = Rectangle(
        width=1.2,
        height=0.54,
        stroke_width=0,
        fill_color=GRAY_200,
        fill_opacity=0.45,
    ).shift(RIGHT * 0.06 + DOWN * 0.06)
    body = Rectangle(
        width=1.2,
        height=0.54,
        stroke_color=GRAY_700,
        stroke_width=3,
        fill_color=WHITE,
        fill_opacity=1,
    )
    accent = Rectangle(
        width=0.62,
        height=0.18,
        stroke_width=0,
        fill_color=GRAY_600,
        fill_opacity=1,
    ).move_to(body.get_center())
    return VGroup(shadow, body, accent)


def make_tile(spec: TileSpec) -> Tile:
    center = RIGHT * COL_X[spec.col] + UP * ROW_Y[spec.row]
    frame = Rectangle(
        width=TILE_WIDTH,
        height=TILE_HEIGHT,
        stroke_color=GRAY_200,
        stroke_width=2,
        fill_color=WHITE,
        fill_opacity=0.98,
    ).move_to(center)
    color_bar = Rectangle(
        width=0.1,
        height=TILE_HEIGHT - 0.26,
        stroke_width=0,
        fill_color=GRAY_300,
        fill_opacity=0.95,
    ).move_to(frame.get_left() + RIGHT * 0.2)
    is_multiline = "\n" in spec.label
    label = label_text(spec.label, max_width=TILE_WIDTH - 0.72, font_size=16 if is_multiline else 21)
    label.move_to(frame.get_top() + DOWN * (0.38 if is_multiline else 0.32))

    actor = make_actor().move_to(center + DOWN * (0.35 if is_multiline else 0.17))
    guide: Line | Circle | None = None
    guide_mobject = VGroup()
    if spec.key == "show_passing_flash":
        guide = Line(
            actor.get_left() + DOWN * 0.48,
            actor.get_right() + DOWN * 0.48,
            color=GRAY_300,
            stroke_width=5,
        )
        guide_mobject.add(guide)
    if spec.key == "show_passing_flash_thin":
        guide = Circle(radius=0.47, color=GRAY_300, stroke_width=5).move_to(actor)
        guide_mobject.add(guide)

    mark = Square(side_length=0.14, stroke_width=0, fill_color=GRAY_600, fill_opacity=1)
    mark.move_to(frame.get_top() + DOWN * 0.26 + RIGHT * (TILE_WIDTH / 2 - 0.32))

    group = VGroup(frame, color_bar, label, guide_mobject, actor)
    return Tile(spec=spec, group=group, frame=frame, actor=actor, guide=guide, mark=mark)


class IndicationAnimationGalleryScene(Scene):
    def is_poster(self) -> bool:
        return os.environ.get("SPIKE_RENDER_TARGET") == "poster"

    def construct(self) -> None:
        if self.is_poster():
            self.camera.background_color = PAGE_BACKGROUND

        title = label_text("manim.animation.indication", max_width=8.0, font_size=28)
        title.move_to(UP * 3.2 + LEFT * 2.55)
        title_rule = Line(
            title.get_right() + RIGHT * 0.34,
            RIGHT * 5.75 + UP * 3.2,
            color=GRAY_300,
            stroke_width=3,
        )

        tiles = [make_tile(spec) for spec in TILE_SPECS]
        tile_group = VGroup(*[tile.group for tile in tiles])
        composition = VGroup(title, title_rule, tile_group).shift(RIGHT * 0.1 + DOWN * 0.25)

        self.add(composition)
        self.wait(2.5)

        self.play_row(
            [tiles[0], tiles[1], tiles[2]],
            [
                ApplyWave(tiles[0].actor, direction=RIGHT, amplitude=0.18, ripples=2, run_time=3.4),
                Blink(tiles[1].actor, time_on=0.34, time_off=0.31, blinks=5),
                Circumscribe(
                    tiles[2].actor,
                    color=PRIMARY_RED,
                    buff=0.14,
                    fade_out=True,
                    run_time=3.4,
                    stroke_width=6,
                ),
            ],
        )

        self.play_row(
            [tiles[3], tiles[4], tiles[5]],
            [
                Flash(
                    tiles[3].actor,
                    line_length=0.32,
                    num_lines=16,
                    flash_radius=0.62,
                    line_stroke_width=5,
                    color=PRIMARY_RED,
                    time_width=0.4,
                    run_time=3.4,
                ),
                FocusOn(tiles[4].actor, color=GRAY_600, opacity=0.18, run_time=3.4),
                Indicate(tiles[5].actor, color=PRIMARY_RED, scale_factor=1.18, run_time=3.4),
            ],
        )

        passing_line = tiles[6].guide
        thinning_circle = tiles[7].guide
        if passing_line is None or thinning_circle is None:
            raise ValueError("Passing flash tiles require guide mobjects.")

        self.play_row(
            [tiles[6], tiles[7], tiles[8]],
            [
                ShowPassingFlash(
                    passing_line.copy().set_color(PRIMARY_RED).set_stroke(width=9),
                    time_width=0.33,
                    run_time=3.4,
                ),
                ShowPassingFlashWithThinningStrokeWidth(
                    thinning_circle.copy().set_color(PRIMARY_RED).set_stroke(width=10),
                    n_segments=14,
                    time_width=0.24,
                    run_time=3.4,
                ),
                Wiggle(
                    tiles[8].actor,
                    scale_value=1.16,
                    rotation_angle=0.12,
                    n_wiggles=7,
                    run_time=3.4,
                ),
            ],
        )

        self.play(
            tile_group.animate.set_opacity(0.98),
            title_rule.animate.set_stroke(PRIMARY_RED, width=5),
            run_time=0.8,
        )
        self.play(title_rule.animate.set_stroke(GRAY_300, width=3), run_time=0.7)
        self.wait(6.2)

    def play_row(self, row_tiles: list[Tile], animations: list[object]) -> None:
        self.play(
            *[tile.frame.animate.set_stroke(PRIMARY_RED, width=3) for tile in row_tiles],
            run_time=0.45,
        )
        self.play(*animations)
        self.play(LaggedStart(*[FadeIn(tile.mark, shift=DOWN * 0.04) for tile in row_tiles], lag_ratio=0.12), run_time=0.35)
        self.wait(0.7)
        self.play(
            *[tile.frame.animate.set_stroke(GRAY_200, width=2) for tile in row_tiles],
            run_time=0.35,
        )


def extract_review_frames(cadence: float = 0.3) -> tuple[int, float]:
    import imageio_ffmpeg
    from PIL import Image, ImageDraw

    if REVIEW_FRAMES_DIR.exists():
        shutil.rmtree(REVIEW_FRAMES_DIR)
    REVIEW_FRAMES_DIR.mkdir(parents=True, exist_ok=True)
    ffmpeg = imageio_ffmpeg.get_ffmpeg_exe()
    target_pattern = str(REVIEW_FRAMES_DIR / "frame-%04d.png")
    fps = f"{int(round(1 / cadence * 30))}/30"
    filtergraph = (
        "[0:v]format=rgba[fg];"
        "color=c=white:s=1600x900:d=120[bg];"
        f"[bg][fg]overlay=shortest=1:format=auto,format=rgb24,fps=fps={fps}"
    )
    subprocess.run(
        [
            ffmpeg,
            "-hide_banner",
            "-loglevel",
            "error",
            "-c:v",
            "libvpx-vp9",
            "-i",
            str(VIDEO_PATH),
            "-filter_complex",
            filtergraph,
            target_pattern,
        ],
        check=True,
    )

    _frame_count, duration = imageio_ffmpeg.count_frames_and_secs(str(VIDEO_PATH))
    frames = sorted(REVIEW_FRAMES_DIR.glob("*.png"))
    thumb_width, thumb_height, label_height, columns = 320, 180, 28, 6
    rows = max(1, (len(frames) + columns - 1) // columns)
    sheet = Image.new("RGB", (columns * thumb_width, rows * (thumb_height + label_height)), "white")
    draw = ImageDraw.Draw(sheet)
    for index, frame_path in enumerate(frames):
        image = Image.open(frame_path).convert("RGB")
        image.thumbnail((thumb_width, thumb_height), Image.Resampling.LANCZOS)
        x = (index % columns) * thumb_width
        y = (index // columns) * (thumb_height + label_height)
        sheet.paste(image, (x, y))
        draw.text((x + 6, y + thumb_height + 6), f"{index * cadence:.1f}s", fill=(40, 40, 40))
    sheet.save(CONTACT_SHEET_PATH)
    return len(frames), duration


def decoded_alpha_range(sample_fps: int = 2) -> tuple[int, int]:
    import imageio_ffmpeg

    ffmpeg = imageio_ffmpeg.get_ffmpeg_exe()
    command = [
        ffmpeg,
        "-hide_banner",
        "-loglevel",
        "error",
        "-c:v",
        "libvpx-vp9",
        "-i",
        str(VIDEO_PATH),
        "-vf",
        f"fps={sample_fps},alphaextract,format=gray",
        "-f",
        "rawvideo",
        "-",
    ]
    result = subprocess.run(command, check=True, stdout=subprocess.PIPE)
    if not result.stdout:
        raise RuntimeError("Alpha validation produced no decoded samples.")
    return min(result.stdout), max(result.stdout)


def main() -> int:
    args = parse_args()
    if STAGING_DIR.exists():
        shutil.rmtree(STAGING_DIR)
    for target, poster in ((VIDEO_PATH, False), (POSTER_PATH, True)):
        env = {**os.environ, "SPIKE_RENDER_TARGET": "poster" if poster else "video"}
        result = subprocess.run(render_command(args, target, poster=poster), check=False, env=env)
        if result.returncode != 0:
            return result.returncode
        promote(target.name, target)
    review_count, duration = extract_review_frames()
    alpha_min, alpha_max = decoded_alpha_range()
    VALIDATION_PATH.write_text(
        "\n".join(
            [
                f"duration_seconds={duration:.3f}",
                f"review_frame_count={review_count}",
                f"decoded_alpha_range={alpha_min}..{alpha_max}",
                f"contact_sheet={CONTACT_SHEET_PATH}",
            ]
        )
        + "\n",
        encoding="utf-8",
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
