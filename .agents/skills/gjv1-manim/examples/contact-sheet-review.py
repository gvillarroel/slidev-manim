#!/usr/bin/env python
from __future__ import annotations

import argparse
import math
from pathlib import Path

import av
from PIL import Image, ImageDraw, ImageFont

VIDEO_EXTENSIONS = {".webm", ".mp4", ".mov", ".mkv"}
IGNORED_SEGMENTS = {".manim", "partial_movie_files"}
SAMPLE_PERCENTAGES = (0.12, 0.5, 0.88)

# Preferred color styles: references/preferred-color-styles.md in this skill.
PRIMARY_RED = "#9e1b32"
WHITE = "#ffffff"
GRAY = "#333e48"
GRAY_200 = "#cfcfcf"
PAGE_BACKGROUND = "#f7f7f7"
REVIEW_BACKGROUND = WHITE
SHEET_BACKGROUND = PAGE_BACKGROUND
TILE_BACKGROUND = WHITE
TEXT_COLOR = GRAY
BORDER_COLOR = GRAY_200
ERROR_COLOR = PRIMARY_RED


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Build contact sheets for promoted videos under videos/<spike-name>/."
    )
    parser.add_argument("--root", type=Path, default=Path.cwd(), help="Repository root.")
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("videos/review-sheets/promoted-video-contact-sheet.png"),
        help="Output PNG path. Multiple sheets receive -01, -02, ... suffixes.",
    )
    parser.add_argument("--limit", type=int, default=0, help="Limit videos for a smoke test.")
    parser.add_argument("--per-sheet", type=int, default=12, help="Video tiles per sheet.")
    return parser.parse_args()


def is_promoted_video(path: Path, video_root: Path) -> bool:
    if path.suffix.lower() not in VIDEO_EXTENSIONS:
        return False
    if any(part in IGNORED_SEGMENTS for part in path.parts):
        return False
    return path.parent.parent == video_root


def promoted_videos(root: Path, limit: int) -> list[Path]:
    video_root = root / "videos"
    videos = [
        path
        for path in sorted(video_root.rglob("*"))
        if path.is_file() and is_promoted_video(path, video_root)
    ]
    return videos[:limit] if limit else videos


def sample_frames(path: Path) -> list[tuple[int, Image.Image]]:
    container = av.open(str(path))
    stream = container.streams.video[0]
    total = stream.frames or 0
    sampled: list[tuple[int, Image.Image]] = []

    if total:
        wanted = {max(0, int(total * pct)) for pct in SAMPLE_PERCENTAGES}
        for index, frame in enumerate(container.decode(stream)):
            if index in wanted:
                sampled.append((index, frame.to_image()))
            if index > max(wanted):
                break
    else:
        decoded = [(index, frame.to_image()) for index, frame in enumerate(container.decode(stream))]
        if decoded:
            count = len(decoded)
            wanted = {
                max(0, min(count - 1, int(count * pct)))
                for pct in SAMPLE_PERCENTAGES
            }
            sampled = [decoded[index] for index in sorted(wanted)]

    container.close()
    return sampled


def composite_alpha(image: Image.Image, size: tuple[int, int]) -> Image.Image:
    rgba = image.convert("RGBA")
    background = Image.new("RGBA", rgba.size, REVIEW_BACKGROUND)
    background.alpha_composite(rgba)
    rgb = background.convert("RGB")
    rgb.thumbnail(size, Image.Resampling.LANCZOS)

    tile = Image.new("RGB", size, TILE_BACKGROUND)
    tile.paste(rgb, ((size[0] - rgb.width) // 2, (size[1] - rgb.height) // 2))
    return tile


def load_fonts() -> tuple[ImageFont.ImageFont, ImageFont.ImageFont]:
    try:
        return ImageFont.truetype("arial.ttf", 15), ImageFont.truetype("arial.ttf", 12)
    except OSError:
        return ImageFont.load_default(), ImageFont.load_default()


def video_tile(root: Path, video: Path, fonts: tuple[ImageFont.ImageFont, ImageFont.ImageFont]) -> Image.Image:
    label_font, small_font = fonts
    frame_width, frame_height = 226, 127
    gap = 6
    label_height = 52
    tile_width = frame_width * 3 + gap * 2
    tile_height = label_height + frame_height
    tile = Image.new("RGB", (tile_width, tile_height), TILE_BACKGROUND)
    draw = ImageDraw.Draw(tile)

    label = video.relative_to(root).as_posix().replace("videos/", "", 1)
    if len(label) > 78:
        label = label[:75] + "..."
    draw.text((4, 5), label, fill=TEXT_COLOR, font=label_font)

    try:
        frames = sample_frames(video)
    except Exception as exc:  # noqa: BLE001 - this is a diagnostic artifact.
        draw.text((4, label_height + 18), f"ERROR: {exc}", fill=ERROR_COLOR, font=small_font)
        return tile

    for index in range(3):
        x = index * (frame_width + gap)
        if index < len(frames):
            frame_number, image = frames[index]
            tile.paste(composite_alpha(image, (frame_width, frame_height)), (x, label_height))
            draw.text((x + 4, label_height + 4), f"f{frame_number}", fill=TEXT_COLOR, font=small_font)
        draw.rectangle(
            [x, label_height, x + frame_width - 1, label_height + frame_height - 1],
            outline=BORDER_COLOR,
        )

    return tile


def output_path(base: Path, index: int, total: int) -> Path:
    if total == 1:
        return base
    return base.with_name(f"{base.stem}-{index + 1:02d}{base.suffix}")


def write_sheets(root: Path, videos: list[Path], output: Path, per_sheet: int) -> list[Path]:
    if not videos:
        raise SystemExit("No promoted videos found.")

    output = output if output.is_absolute() else root / output
    output.parent.mkdir(parents=True, exist_ok=True)
    fonts = load_fonts()
    columns = 2
    pad = 16
    written: list[Path] = []
    sheet_count = math.ceil(len(videos) / per_sheet)

    for sheet_index in range(sheet_count):
        chunk = videos[sheet_index * per_sheet : (sheet_index + 1) * per_sheet]
        tiles = [video_tile(root, video, fonts) for video in chunk]
        tile_width, tile_height = tiles[0].size
        rows = math.ceil(len(tiles) / columns)
        sheet = Image.new(
            "RGB",
            (
                columns * tile_width + (columns + 1) * pad,
                rows * tile_height + (rows + 1) * pad + 36,
            ),
            SHEET_BACKGROUND,
        )
        draw = ImageDraw.Draw(sheet)
        draw.text(
            (pad, 10),
            f"Promoted video review {sheet_index + 1:02d} ({len(chunk)} videos)",
            fill=TEXT_COLOR,
            font=fonts[0],
        )

        for tile_index, tile in enumerate(tiles):
            column = tile_index % columns
            row = tile_index // columns
            x = pad + column * (tile_width + pad)
            y = 36 + pad + row * (tile_height + pad)
            sheet.paste(tile, (x, y))
            draw.rectangle([x, y, x + tile_width - 1, y + tile_height - 1], outline=BORDER_COLOR)

        path = output_path(output, sheet_index, sheet_count)
        sheet.save(path)
        written.append(path)

    return written


def main() -> int:
    args = parse_args()
    root = args.root.resolve()
    videos = promoted_videos(root, args.limit)
    outputs = write_sheets(root, videos, args.output, args.per_sheet)
    print(f"promoted_videos={len(videos)}")
    for path in outputs:
        print(path)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
