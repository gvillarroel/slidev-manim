#!/usr/bin/env python
# /// script
# dependencies = [
#   "av",
#   "numpy",
#   "pillow",
# ]
# ///
from __future__ import annotations

import argparse
import csv
import json
import math
from collections import deque
from dataclasses import dataclass
from pathlib import Path

import av
import numpy as np
from PIL import Image, ImageDraw, ImageFont

WHITE = "#ffffff"
GRAY = "#333e48"
PRIMARY_RED = "#9e1b32"
PRIMARY_ORANGE = "#e77204"
PRIMARY_BLUE = "#007298"
PRIMARY_GREEN = "#45842a"


@dataclass(frozen=True)
class Box:
    left: int
    top: int
    right: int
    bottom: int

    @property
    def width(self) -> int:
        return max(0, self.right - self.left + 1)

    @property
    def height(self) -> int:
        return max(0, self.bottom - self.top + 1)

    @property
    def area(self) -> int:
        return self.width * self.height

    @property
    def center(self) -> tuple[float, float]:
        return ((self.left + self.right) / 2, (self.top + self.bottom) / 2)

    def to_list(self) -> list[int]:
        return [self.left, self.top, self.right, self.bottom]


@dataclass(frozen=True)
class Component:
    index: int
    box: Box
    pixel_area: int
    fill_fraction: float
    mean_saturation: float
    role: str

    def to_dict(self) -> dict:
        return {
            "index": self.index,
            "box": self.box.to_list(),
            "pixel_area": self.pixel_area,
            "fill_fraction": round(self.fill_fraction, 4),
            "mean_saturation": round(self.mean_saturation, 4),
            "role": self.role,
        }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Audit sampled video frames for crowded actors: components too close "
            "to guides, panel edges, clamp bars, or other components."
        )
    )
    parser.add_argument("--video", type=Path, required=True, help="Video file to inspect.")
    parser.add_argument("--out-dir", type=Path, default=None, help="Directory for reports and optional overlays.")
    parser.add_argument("--cadence", type=float, default=0.5, help="Seconds between sampled frames.")
    parser.add_argument("--start", type=float, default=0.0, help="First timestamp to inspect.")
    parser.add_argument("--end", type=float, default=None, help="Last timestamp to inspect.")
    parser.add_argument("--times", default="", help="Comma-separated timestamps. When set, cadence sampling is skipped.")
    parser.add_argument("--threshold", type=int, default=18, help="Foreground threshold from white review background.")
    parser.add_argument(
        "--min-clearance",
        type=int,
        default=30,
        help="Minimum pixel clearance expected between an actor and a guide/edge component.",
    )
    parser.add_argument(
        "--actor-min-area",
        type=int,
        default=500,
        help="Minimum pixel area for colored actor components considered in strict checks.",
    )
    parser.add_argument(
        "--write-overlays",
        action="store_true",
        help="Write PNG overlays for frames with crowding findings.",
    )
    return parser.parse_args()


def parse_times(raw: str) -> list[float]:
    if not raw.strip():
        return []
    return sorted({float(chunk.strip()) for chunk in raw.split(",") if chunk.strip()})


def video_metadata(video: Path) -> tuple[float, float, int, int]:
    container = av.open(str(video))
    stream = container.streams.video[0]
    fps = float(stream.average_rate or 30)
    duration = float(stream.duration * stream.time_base) if stream.duration else float(container.duration / av.time_base)
    width = stream.codec_context.width
    height = stream.codec_context.height
    container.close()
    return duration, fps, width, height


def sample_times(duration: float, args: argparse.Namespace) -> list[float]:
    explicit = parse_times(args.times)
    if explicit:
        return [time for time in explicit if 0 <= time <= duration]

    end = duration if args.end is None else min(duration, args.end)
    current = max(0.0, args.start)
    times: list[float] = []
    while current <= end + 1e-6:
        times.append(round(current, 3))
        current += args.cadence
    if times and args.end is None and duration - times[-1] > args.cadence * 0.45:
        times.append(round(max(0.0, duration - 0.05), 3))
    return times


def frame_at(video: Path, time: float, fps: float) -> Image.Image:
    selected = None
    for target in (time, max(0.0, time - 1 / fps), max(0.0, time - 2 / fps), max(0.0, time - 0.15)):
        container = av.open(str(video))
        stream = container.streams.video[0]
        container.seek(int(target / stream.time_base), stream=stream)
        for frame in container.decode(stream):
            if frame.time is None or frame.time + (0.5 / fps) >= target:
                selected = frame
                break
        container.close()
        if selected is not None:
            break
    if selected is None:
        raise RuntimeError(f"No frame near {time:.3f}s")

    rgba = selected.to_image().convert("RGBA")
    background = Image.new("RGBA", rgba.size, WHITE)
    background.alpha_composite(rgba)
    return background.convert("RGB")


def masks(image: Image.Image, threshold: int) -> tuple[np.ndarray, np.ndarray]:
    arr = np.asarray(image).astype(np.int16)
    diff = np.abs(arr - np.array([255, 255, 255], dtype=np.int16)).max(axis=2)
    foreground = diff >= threshold
    max_channel = np.maximum(arr.max(axis=2), 1)
    saturation = ((arr.max(axis=2) - arr.min(axis=2)) / max_channel).astype(np.float32)
    return foreground, saturation


def downsample_mask(mask: np.ndarray, target_width: int = 480) -> tuple[np.ndarray, float, float]:
    height, width = mask.shape
    scale = target_width / width
    target_height = max(1, int(round(height * scale)))
    small = Image.fromarray((mask.astype(np.uint8) * 255), mode="L").resize(
        (target_width, target_height),
        Image.Resampling.NEAREST,
    )
    return np.asarray(small) > 0, width / target_width, height / target_height


def classify_component(box: Box, pixel_area: int, fill_fraction: float, saturation: float, width: int, height: int) -> str:
    slender = box.width <= width * 0.045 and box.height >= height * 0.22
    outline = box.width >= width * 0.18 and box.height >= height * 0.25 and fill_fraction <= 0.34
    if outline:
        return "outline"
    if slender:
        return "guide"
    if saturation >= 0.16 and pixel_area >= 90:
        return "actor"
    return "support"


def connected_components(mask: np.ndarray, saturation: np.ndarray) -> list[Component]:
    small, scale_x, scale_y = downsample_mask(mask)
    height, width = small.shape
    seen = np.zeros_like(small, dtype=bool)
    full_height, full_width = mask.shape
    min_area = max(5, int(width * height * 0.00018))
    components: list[Component] = []

    for start_y in range(height):
        for start_x in range(width):
            if seen[start_y, start_x] or not small[start_y, start_x]:
                continue
            queue: deque[tuple[int, int]] = deque([(start_x, start_y)])
            seen[start_y, start_x] = True
            xs: list[int] = []
            ys: list[int] = []
            while queue:
                x, y = queue.popleft()
                xs.append(x)
                ys.append(y)
                for nx in (x - 1, x, x + 1):
                    for ny in (y - 1, y, y + 1):
                        if nx == x and ny == y:
                            continue
                        if nx < 0 or ny < 0 or nx >= width or ny >= height:
                            continue
                        if seen[ny, nx] or not small[ny, nx]:
                            continue
                        seen[ny, nx] = True
                        queue.append((nx, ny))
            if len(xs) < min_area:
                continue
            box = Box(
                max(0, int(math.floor(min(xs) * scale_x))),
                max(0, int(math.floor(min(ys) * scale_y))),
                min(full_width - 1, int(math.ceil((max(xs) + 1) * scale_x))),
                min(full_height - 1, int(math.ceil((max(ys) + 1) * scale_y))),
            )
            crop_mask = mask[box.top : box.bottom + 1, box.left : box.right + 1]
            crop_sat = saturation[box.top : box.bottom + 1, box.left : box.right + 1]
            pixel_area = int(crop_mask.sum())
            if pixel_area <= 0:
                continue
            fill_fraction = pixel_area / max(1, box.area)
            mean_saturation = float(crop_sat[crop_mask].mean())
            role = classify_component(box, pixel_area, fill_fraction, mean_saturation, full_width, full_height)
            components.append(
                Component(
                    index=len(components),
                    box=box,
                    pixel_area=pixel_area,
                    fill_fraction=fill_fraction,
                    mean_saturation=mean_saturation,
                    role=role,
                )
            )

    return sorted(components, key=lambda component: component.pixel_area, reverse=True)


def intersection_area(a: Box, b: Box) -> int:
    left = max(a.left, b.left)
    top = max(a.top, b.top)
    right = min(a.right, b.right)
    bottom = min(a.bottom, b.bottom)
    if right < left or bottom < top:
        return 0
    return (right - left + 1) * (bottom - top + 1)


def clearance(a: Box, b: Box) -> float:
    dx = max(a.left - b.right - 1, b.left - a.right - 1, 0)
    dy = max(a.top - b.bottom - 1, b.top - a.bottom - 1, 0)
    return math.hypot(dx, dy)


def nearest_points(a: Box, b: Box) -> tuple[tuple[int, int], tuple[int, int]]:
    ax = min(max((b.left + b.right) // 2, a.left), a.right)
    ay = min(max((b.top + b.bottom) // 2, a.top), a.bottom)
    bx = min(max(ax, b.left), b.right)
    by = min(max(ay, b.top), b.bottom)
    return (ax, ay), (bx, by)


def outline_inner_clearance(outline: Box, inner: Box) -> float:
    contained_x = outline.left <= inner.left <= inner.right <= outline.right
    contained_y = outline.top <= inner.top <= inner.bottom <= outline.bottom
    if contained_x and contained_y:
        return float(
            min(
                inner.left - outline.left,
                outline.right - inner.right,
                inner.top - outline.top,
                outline.bottom - inner.bottom,
            )
        )
    return clearance(outline, inner)


def pair_clearance(left: Component, right: Component) -> tuple[float, int, str]:
    if left.role == "outline" and right.role != "outline":
        return outline_inner_clearance(left.box, right.box), 0, "outline_edge"
    if right.role == "outline" and left.role != "outline":
        return outline_inner_clearance(right.box, left.box), 0, "outline_edge"
    raw_overlap = intersection_area(left.box, right.box)
    return (0.0 if raw_overlap else clearance(left.box, right.box)), raw_overlap, "component_pair"


def pair_is_strict(left: Component, right: Component, clear: float, raw_overlap: int, relation: str, args: argparse.Namespace) -> bool:
    roles = {left.role, right.role}
    actor_present = "actor" in roles
    structural_present = bool({"guide", "outline"} & roles)
    return actor_present and (structural_present or raw_overlap > 0 or relation == "outline_edge") and clear <= args.min_clearance


def audit_frame(image: Image.Image, time: float, args: argparse.Namespace) -> dict:
    width, height = image.size
    foreground, saturation = masks(image, args.threshold)
    components = connected_components(foreground, saturation)
    kept = [component for component in components if component.pixel_area >= 70][:32]
    findings: list[dict] = []

    for left_index, left in enumerate(kept):
        for right in kept[left_index + 1 :]:
            clear, raw_overlap, relation = pair_clearance(left, right)
            if not pair_is_strict(left, right, clear, raw_overlap, relation, args):
                continue
            findings.append(
                {
                    "code": "low_component_clearance",
                    "severity": "warning",
                    "message": "Actor component is too close to a guide, panel edge, clamp, or overlapping component.",
                    "metrics": {
                        "min_clearance_px": args.min_clearance,
                        "clearance_px": round(clear, 2),
                        "raw_overlap_pixels": raw_overlap,
                        "relation": relation,
                        "left": left.to_dict(),
                        "right": right.to_dict(),
                    },
                }
            )

    return {
        "time": round(time, 3),
        "component_count": len(kept),
        "components": [component.to_dict() for component in kept[:16]],
        "findings": findings,
    }


def load_fonts() -> tuple[ImageFont.ImageFont, ImageFont.ImageFont]:
    try:
        return ImageFont.truetype("arial.ttf", 18), ImageFont.truetype("arial.ttf", 13)
    except OSError:
        return ImageFont.load_default(), ImageFont.load_default()


def draw_overlay(image: Image.Image, audit: dict, out_path: Path) -> None:
    overlay = image.copy()
    draw = ImageDraw.Draw(overlay)
    label_font, small_font = load_fonts()
    for component in audit["components"]:
        color = PRIMARY_BLUE if component["role"] == "actor" else PRIMARY_ORANGE if component["role"] == "guide" else PRIMARY_GREEN
        draw.rectangle(component["box"], outline=color, width=3)
        draw.text((component["box"][0] + 3, component["box"][1] + 3), f"{component['index']}:{component['role']}", fill=color, font=small_font)

    for finding in audit["findings"]:
        left_box = Box(*finding["metrics"]["left"]["box"])
        right_box = Box(*finding["metrics"]["right"]["box"])
        start, end = nearest_points(left_box, right_box)
        draw.line([start, end], fill=PRIMARY_RED, width=5)

    y = 12
    draw.rectangle([8, 8, overlay.width - 8, 38 + 22 * len(audit["findings"])], fill=WHITE, outline="#cfcfcf")
    draw.text((16, y), f"{audit['time']:.3f}s crowding={len(audit['findings'])}", fill=GRAY, font=label_font)
    y += 22
    for finding in audit["findings"]:
        metrics = finding["metrics"]
        pair = f"{metrics['left']['index']}->{metrics['right']['index']} clear={metrics['clearance_px']}px"
        draw.text((16, y), pair, fill=PRIMARY_RED, font=small_font)
        y += 22

    out_path.parent.mkdir(parents=True, exist_ok=True)
    overlay.save(out_path)


def write_outputs(out_dir: Path, audits: list[dict], args: argparse.Namespace, metadata: dict) -> None:
    out_dir.mkdir(parents=True, exist_ok=True)
    (out_dir / "crowding-audit.json").write_text(
        json.dumps({"metadata": metadata, "frames": audits}, indent=2),
        encoding="utf-8",
    )
    with (out_dir / "crowding-audit.csv").open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=["time", "blocking", "finding_count", "min_clearance_px"])
        writer.writeheader()
        for audit in audits:
            clearances = [
                finding["metrics"]["clearance_px"]
                for finding in audit["findings"]
                if finding["code"] == "low_component_clearance"
            ]
            writer.writerow(
                {
                    "time": audit["time"],
                    "blocking": bool(audit["findings"]),
                    "finding_count": len(audit["findings"]),
                    "min_clearance_px": min(clearances) if clearances else "",
                }
            )

    flagged = [audit for audit in audits if audit["findings"]]
    lines = [
        "# Frame Crowding Audit",
        "",
        f"- Video: `{metadata['video']}`",
        f"- Duration: {metadata['duration']:.3f}s",
        f"- Sampled frames: {len(audits)}",
        f"- Blocking frames: {len(flagged)}",
        f"- Minimum component clearance: {args.min_clearance}px",
        "",
    ]
    for audit in flagged[:80]:
        clearances = [finding["metrics"]["clearance_px"] for finding in audit["findings"]]
        lines.append(f"- {audit['time']:.3f}s: low_component_clearance min={min(clearances):.2f}px count={len(clearances)}")
    if len(flagged) > 80:
        lines.append(f"- ... {len(flagged) - 80} additional flagged frames omitted")
    (out_dir / "report.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    args = parse_args()
    video = args.video.resolve()
    if not video.exists():
        raise SystemExit(f"Video does not exist: {video}")
    out_dir = args.out_dir or (video.parent / "crowding-audit")
    duration, fps, width, height = video_metadata(video)
    times = sample_times(duration, args)
    audits: list[dict] = []
    for time in times:
        image = frame_at(video, time, fps)
        audit = audit_frame(image, time, args)
        audits.append(audit)
        if audit["findings"] and args.write_overlays:
            draw_overlay(image, audit, out_dir / "overlays" / f"frame-{time:07.3f}s.png")

    metadata = {"video": str(video), "duration": duration, "fps": fps, "width": width, "height": height}
    write_outputs(out_dir, audits, args, metadata)
    blocking = sum(1 for audit in audits if audit["findings"])
    print(f"sampled_frames={len(audits)}")
    print(f"blocking_frames={blocking}")
    print(out_dir / "report.md")
    return 1 if blocking else 0


if __name__ == "__main__":
    raise SystemExit(main())
