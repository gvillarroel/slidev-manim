#!/usr/bin/env python
from __future__ import annotations

import argparse
import json
import math
from dataclasses import dataclass
from pathlib import Path

import av
from PIL import Image, ImageDraw, ImageFont


SKILL_DIR = Path(__file__).resolve().parents[1]
DEFAULT_POLICY = SKILL_DIR / "assets" / "frame-safety-policy.json"


@dataclass(frozen=True)
class FrameFinding:
    video: Path
    frame_index: int
    sample_percentage: float
    flags: tuple[str, ...]
    margin_px: int
    center_offset: float
    bbox_axis_ratio: float
    image: Image.Image


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Prioritize promoted videos whose sampled frames may be clipped, off-center, or too close to the edge."
    )
    parser.add_argument("--root", type=Path, default=Path.cwd(), help="Repository root.")
    parser.add_argument("--policy", type=Path, default=DEFAULT_POLICY, help="Frame-safety policy JSON.")
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=Path("videos/review-sheets/frame-safety-audit"),
        help="Directory for the JSON report and flagged-frame sheet.",
    )
    parser.add_argument("--limit", type=int, default=0, help="Limit videos for a smoke test.")
    parser.add_argument("--max-findings", type=int, default=36, help="Maximum findings to draw in the sheet.")
    return parser.parse_args()


def load_policy(path: Path) -> dict:
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def is_promoted_video(path: Path, video_root: Path, policy: dict) -> bool:
    if path.suffix.lower() not in set(policy["promoted_video_extensions"]):
        return False
    if any(part in set(policy["ignore_path_segments"]) for part in path.parts):
        return False
    return path.parent.parent == video_root


def promoted_videos(root: Path, policy: dict, limit: int) -> list[Path]:
    video_root = root / "videos"
    videos = [
        path
        for path in sorted(video_root.rglob("*"))
        if path.is_file() and is_promoted_video(path, video_root, policy)
    ]
    return videos[:limit] if limit else videos


def should_count_pixel(pixel: tuple[int, int, int, int], policy: dict) -> bool:
    r, g, b, a = pixel
    filters = policy["background_filters"]
    if a < filters["ignore_alpha_below"]:
        return False
    if r < filters["ignore_near_black_below"] and g < filters["ignore_near_black_below"] and b < filters["ignore_near_black_below"]:
        return False
    if r > filters["ignore_near_white_above"] and g > filters["ignore_near_white_above"] and b > filters["ignore_near_white_above"]:
        return False
    if (
        max(r, g, b) - min(r, g, b) < filters["ignore_neutral_delta"]
        and filters["ignore_neutral_min"] <= r <= filters["ignore_neutral_max"]
    ):
        return False
    return True


def foreground_bbox(image: Image.Image, policy: dict) -> tuple[int, int, int, int] | None:
    rgba = image.convert("RGBA")
    width, height = rgba.size
    pixels = rgba.load()
    xs: list[int] = []
    ys: list[int] = []
    stride = 2

    for y in range(0, height, stride):
        for x in range(0, width, stride):
            if should_count_pixel(pixels[x, y], policy):
                xs.append(x)
                ys.append(y)

    if not xs:
        return None
    return min(xs), min(ys), max(xs), max(ys)


def decoded_samples(path: Path, percentages: list[float]) -> list[tuple[int, float, Image.Image]]:
    container = av.open(str(path))
    frames = [(index, frame.to_image().convert("RGBA")) for index, frame in enumerate(container.decode(video=0))]
    container.close()

    if not frames:
        return []
    last_index = len(frames) - 1
    return [
        (frames[max(0, min(last_index, int(last_index * percentage)))][0], percentage, frames[max(0, min(last_index, int(last_index * percentage)))][1])
        for percentage in percentages
    ]


def composite_for_review(image: Image.Image, policy: dict) -> Image.Image:
    rgba = image.convert("RGBA")
    background = Image.new("RGBA", rgba.size, policy["review_background"])
    background.alpha_composite(rgba)
    return background.convert("RGB")


def findings_for_video(path: Path, policy: dict) -> list[FrameFinding]:
    findings: list[FrameFinding] = []
    for frame_index, percentage, image in decoded_samples(path, policy["sample_percentages"]):
        bbox = foreground_bbox(image, policy)
        if bbox is None:
            continue

        width, height = image.size
        min_x, min_y, max_x, max_y = bbox
        margin_px = min(min_x, min_y, width - max_x - 1, height - max_y - 1)
        edge_threshold = max(policy["edge_margin_px"], int(min(width, height) * policy["edge_margin_ratio"]))
        center_x = ((min_x + max_x) / 2) / width
        center_y = ((min_y + max_y) / 2) / height
        center_offset = max(abs(center_x - 0.5), abs(center_y - 0.5))
        bbox_axis_ratio = max((max_x - min_x + 1) / width, (max_y - min_y + 1) / height)

        flags: list[str] = []
        if margin_px < edge_threshold:
            flags.append("edge-margin")
        if center_offset > policy["center_offset_ratio"]:
            flags.append("off-center")
        if bbox_axis_ratio > policy["large_bbox_axis_ratio"] and margin_px < edge_threshold * 2:
            flags.append("large-near-edge")

        if flags:
            findings.append(
                FrameFinding(
                    video=path,
                    frame_index=frame_index,
                    sample_percentage=percentage,
                    flags=tuple(flags),
                    margin_px=margin_px,
                    center_offset=center_offset,
                    bbox_axis_ratio=bbox_axis_ratio,
                    image=composite_for_review(image, policy),
                )
            )

    return findings


def load_fonts() -> tuple[ImageFont.ImageFont, ImageFont.ImageFont]:
    try:
        return ImageFont.truetype("arial.ttf", 15), ImageFont.truetype("arial.ttf", 12)
    except OSError:
        return ImageFont.load_default(), ImageFont.load_default()


def write_sheet(root: Path, findings: list[FrameFinding], path: Path, policy: dict, max_findings: int) -> None:
    label_font, small_font = load_fonts()
    tile_width, tile_height = 320, 180
    label_height = 54
    pad = 14
    columns = 3
    drawn = findings[:max_findings]
    rows = max(1, math.ceil(len(drawn) / columns))
    sheet = Image.new(
        "RGB",
        (
            columns * tile_width + (columns + 1) * pad,
            rows * (tile_height + label_height) + (rows + 1) * pad,
        ),
        policy["sheet_background"],
    )
    draw = ImageDraw.Draw(sheet)

    if not drawn:
        draw.text((pad, pad), "No frame-safety findings.", fill="#333e48", font=label_font)
        sheet.save(path)
        return

    for index, finding in enumerate(drawn):
        column = index % columns
        row = index // columns
        x = pad + column * (tile_width + pad)
        y = pad + row * (tile_height + label_height + pad)
        rel = finding.video.relative_to(root).as_posix().replace("videos/", "", 1)
        if len(rel) > 54:
            rel = rel[:51] + "..."
        draw.text((x, y), rel, fill="#333e48", font=label_font)
        detail = f"f{finding.frame_index} p{finding.sample_percentage:.2f} {', '.join(finding.flags)}"
        draw.text((x, y + 20), detail, fill="#9e1b32", font=small_font)
        metrics = f"margin={finding.margin_px}px center={finding.center_offset:.2f} axis={finding.bbox_axis_ratio:.2f}"
        draw.text((x, y + 36), metrics, fill="#333e48", font=small_font)

        image = finding.image.copy()
        image.thumbnail((tile_width, tile_height), Image.Resampling.LANCZOS)
        tile = Image.new("RGB", (tile_width, tile_height), policy["tile_background"])
        tile.paste(image, ((tile_width - image.width) // 2, (tile_height - image.height) // 2))
        sheet.paste(tile, (x, y + label_height))
        draw.rectangle([x, y + label_height, x + tile_width - 1, y + label_height + tile_height - 1], outline="#cfcfcf")

    sheet.save(path)


def report_row(root: Path, finding: FrameFinding) -> dict:
    return {
        "video": finding.video.relative_to(root).as_posix(),
        "frame": finding.frame_index,
        "sample_percentage": finding.sample_percentage,
        "flags": list(finding.flags),
        "margin_px": finding.margin_px,
        "center_offset": round(finding.center_offset, 4),
        "bbox_axis_ratio": round(finding.bbox_axis_ratio, 4),
    }


def main() -> int:
    args = parse_args()
    root = args.root.resolve()
    policy = load_policy(args.policy.resolve())
    output_dir = args.output_dir if args.output_dir.is_absolute() else root / args.output_dir
    output_dir.mkdir(parents=True, exist_ok=True)

    videos = promoted_videos(root, policy, args.limit)
    findings: list[FrameFinding] = []
    for video in videos:
        findings.extend(findings_for_video(video, policy))

    findings.sort(key=lambda finding: (finding.margin_px, -finding.center_offset, str(finding.video)))

    report_path = output_dir / "frame-safety-audit.json"
    sheet_path = output_dir / "frame-safety-audit.png"
    report = {
        "promoted_videos": len(videos),
        "findings": [report_row(root, finding) for finding in findings],
        "policy": policy,
    }
    report_path.write_text(json.dumps(report, indent=2), encoding="utf-8")
    write_sheet(root, findings, sheet_path, policy, args.max_findings)

    print(f"promoted_videos={len(videos)}")
    print(f"findings={len(findings)}")
    print(report_path)
    print(sheet_path)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
