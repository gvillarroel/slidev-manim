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
PAGE_BACKGROUND = "#f7f7f7"
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

    def expand(self, pixels: int, width: int, height: int) -> Box:
        return Box(
            max(0, self.left - pixels),
            max(0, self.top - pixels),
            min(width - 1, self.right + pixels),
            min(height - 1, self.bottom + pixels),
        )

    def to_list(self) -> list[int]:
        return [self.left, self.top, self.right, self.bottom]


@dataclass(frozen=True)
class Component:
    box: Box
    area: int
    mean_saturation: float


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Audit sampled video frames for composition problems: low margins, "
            "off-center content, stray frame fragments, and possible visual overlaps."
        )
    )
    parser.add_argument("--video", type=Path, required=True, help="Video file to inspect.")
    parser.add_argument(
        "--out-dir",
        type=Path,
        default=None,
        help="Directory for audit.json, audit.csv, report.md, and optional overlays.",
    )
    parser.add_argument("--cadence", type=float, default=0.5, help="Seconds between sampled frames.")
    parser.add_argument("--start", type=float, default=0.0, help="First timestamp to inspect.")
    parser.add_argument("--end", type=float, default=None, help="Last timestamp to inspect.")
    parser.add_argument(
        "--times",
        default="",
        help="Comma-separated timestamps to inspect. When set, cadence sampling is skipped.",
    )
    parser.add_argument("--threshold", type=int, default=18, help="Foreground threshold from review background.")
    parser.add_argument(
        "--margin",
        type=float,
        default=0.045,
        help="Minimum allowed foreground margin as a fraction of frame size.",
    )
    parser.add_argument(
        "--center-tolerance",
        type=float,
        default=0.08,
        help="Allowed content-bbox center offset as a fraction of frame size.",
    )
    parser.add_argument(
        "--proximity",
        type=int,
        default=22,
        help="Pixel expansion for possible component crowding checks.",
    )
    parser.add_argument(
        "--write-overlays",
        action="store_true",
        help="Write annotated PNG overlays for frames with findings.",
    )
    parser.add_argument(
        "--check-gray-only",
        action="store_true",
        help="Also apply margin and centering checks when only low-saturation gray structure is visible.",
    )
    parser.add_argument(
        "--strict-notices",
        action="store_true",
        help="Treat notice-level overlap/crowding findings as blocking failures.",
    )
    parser.add_argument(
        "--strict-stray",
        action="store_true",
        help="Treat low-saturation vertical fragments as blocking instead of review notices.",
    )
    parser.add_argument(
        "--max-components",
        type=int,
        default=24,
        help="Maximum connected components to keep per frame for overlap checks.",
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
    if times and duration - times[-1] > args.cadence * 0.45 and args.end is None:
        times.append(round(max(0.0, duration - 0.05), 3))
    return times


def frame_at(video: Path, time: float, fps: float) -> Image.Image:
    selected = None
    for target in (time, max(0.0, time - 1 / fps), max(0.0, time - 2 / fps), max(0.0, time - 0.15)):
        container = av.open(str(video))
        stream = container.streams.video[0]
        container.seek(int(max(0, target) / stream.time_base), stream=stream)
        for frame in container.decode(stream):
            if frame.time is None or frame.time + (0.5 / fps) >= target:
                selected = frame
                break
        container.close()
        if selected is not None:
            break
    if selected is None:
        container = av.open(str(video))
        for frame in container.decode(video=0):
            selected = frame
        container.close()
    if selected is None:
        raise RuntimeError(f"No frame near {time:.3f}s")

    rgba = selected.to_image().convert("RGBA")
    background = Image.new("RGBA", rgba.size, WHITE)
    background.alpha_composite(rgba)
    return background.convert("RGB")


def foreground_mask(image: Image.Image, threshold: int) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    arr = np.asarray(image).astype(np.int16)
    background = np.array([255, 255, 255], dtype=np.int16)
    diff = np.abs(arr - background).max(axis=2)
    mask = diff >= threshold
    max_channel = np.maximum(arr.max(axis=2), 1)
    saturation = (arr.max(axis=2) - arr.min(axis=2)) / max_channel
    strong_mask = mask & (diff >= max(threshold, 32)) & (saturation >= 0.18)
    return mask, strong_mask, saturation.astype(np.float32)


def bbox_from_mask(mask: np.ndarray) -> Box | None:
    ys, xs = np.where(mask)
    if xs.size == 0:
        return None
    return Box(int(xs.min()), int(ys.min()), int(xs.max()), int(ys.max()))


def downsample_mask(mask: np.ndarray, target_width: int = 400) -> tuple[np.ndarray, float, float]:
    height, width = mask.shape
    scale = target_width / width
    target_height = max(1, int(round(height * scale)))
    image = Image.fromarray((mask.astype(np.uint8) * 255), mode="L")
    small = image.resize((target_width, target_height), Image.Resampling.NEAREST)
    small_mask = np.asarray(small) > 0
    return small_mask, width / target_width, height / target_height


def mean_saturation_for_box(saturation: np.ndarray, box: Box) -> float:
    crop = saturation[box.top : box.bottom + 1, box.left : box.right + 1]
    if crop.size == 0:
        return 0.0
    return float(crop.mean())


def connected_components(mask: np.ndarray, saturation: np.ndarray, max_components: int) -> list[Component]:
    small, scale_x, scale_y = downsample_mask(mask)
    height, width = small.shape
    seen = np.zeros_like(small, dtype=bool)
    components: list[Component] = []
    min_area = max(4, int(width * height * 0.00035))

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
                int(math.floor(min(xs) * scale_x)),
                int(math.floor(min(ys) * scale_y)),
                int(math.ceil((max(xs) + 1) * scale_x)),
                int(math.ceil((max(ys) + 1) * scale_y)),
            )
            components.append(Component(box=box, area=len(xs), mean_saturation=mean_saturation_for_box(saturation, box)))

    return sorted(components, key=lambda component: component.box.area, reverse=True)[:max_components]


def intersection_area(a: Box, b: Box) -> int:
    left = max(a.left, b.left)
    top = max(a.top, b.top)
    right = min(a.right, b.right)
    bottom = min(a.bottom, b.bottom)
    if right < left or bottom < top:
        return 0
    return (right - left + 1) * (bottom - top + 1)


def margins_for(box: Box, width: int, height: int) -> dict[str, float]:
    return {
        "left": box.left / width,
        "right": (width - 1 - box.right) / width,
        "top": box.top / height,
        "bottom": (height - 1 - box.bottom) / height,
    }


def add_finding(findings: list[dict], code: str, severity: str, message: str, metrics: dict) -> None:
    findings.append(
        {
            "code": code,
            "severity": severity,
            "message": message,
            "metrics": metrics,
        }
    )


def audit_frame(image: Image.Image, time: float, args: argparse.Namespace) -> dict:
    width, height = image.size
    mask, strong_mask, saturation = foreground_mask(image, args.threshold)
    content_box = bbox_from_mask(mask)
    strong_box = bbox_from_mask(strong_mask)
    findings: list[dict] = []
    components = connected_components(mask, saturation, args.max_components)

    result = {
        "time": round(time, 3),
        "content_box": content_box.to_list() if content_box else None,
        "strong_box": strong_box.to_list() if strong_box else None,
        "active_color": strong_box is not None,
        "foreground_fraction": float(mask.mean()),
        "findings": findings,
    }
    if content_box is None:
        add_finding(findings, "blank_frame", "error", "No visible foreground was detected.", {})
        return result

    active_box = strong_box or content_box
    result["active_box"] = active_box.to_list()
    margins = margins_for(active_box, width, height)
    center_box = content_box if strong_box is not None and content_box.area > active_box.area * 1.45 else active_box
    center_x, center_y = center_box.center
    result["margins"] = margins
    result["center_box"] = center_box.to_list()
    result["center_offset"] = {
        "x": (center_x - width / 2) / width,
        "y": (center_y - height / 2) / height,
    }

    if strong_box is not None or args.check_gray_only:
        low_margins = {name: value for name, value in margins.items() if value < args.margin}
        if low_margins:
            add_finding(
                findings,
                "low_visual_margin",
                "warning",
                "Visible foreground is too close to the frame edge.",
                {"minimum_fraction": args.margin, "margins": low_margins},
            )

        if abs(result["center_offset"]["x"]) > args.center_tolerance or abs(result["center_offset"]["y"]) > args.center_tolerance:
            add_finding(
                findings,
                "off_center_content",
                "warning",
                "Visible content bbox is outside the center tolerance.",
                {"tolerance": args.center_tolerance, "offset": result["center_offset"]},
            )

    if strong_box:
        stray_boxes: list[list[int]] = []
        for component in components:
            box = component.box
            slender = box.width <= width * 0.035 and box.height >= height * 0.42
            center_x, _ = box.center
            outside_active_color = center_x < strong_box.left or center_x > strong_box.right
            low_saturation = component.mean_saturation < 0.16
            if slender and outside_active_color and low_saturation:
                stray_boxes.append(box.to_list())
        if stray_boxes:
            add_finding(
                findings,
                "stray_vertical_fragment",
                "warning" if args.strict_stray else "notice",
                "Thin low-saturation vertical fragments sit outside the active colored composition; review them as blocking only when they are not intentional panel edges or guides.",
                {"boxes": stray_boxes[:8]},
            )

    crowding: list[dict] = []
    strong_components = [component for component in components if component.mean_saturation >= 0.12]
    for left_index, left_component in enumerate(strong_components):
        for right_component in strong_components[left_index + 1 :]:
            left_box = left_component.box.expand(args.proximity, width, height)
            right_box = right_component.box.expand(args.proximity, width, height)
            expanded_overlap = intersection_area(left_box, right_box)
            if expanded_overlap == 0:
                continue
            raw_overlap = intersection_area(left_component.box, right_component.box)
            overlap_ratio = expanded_overlap / max(1, min(left_component.box.area, right_component.box.area))
            if raw_overlap > 0 or overlap_ratio > 0.18:
                crowding.append(
                    {
                        "left_box": left_component.box.to_list(),
                        "right_box": right_component.box.to_list(),
                        "expanded_overlap_ratio": round(overlap_ratio, 3),
                        "raw_overlap_pixels": raw_overlap,
                    }
                )
    if crowding:
        add_finding(
            findings,
            "possible_overlap_or_crowding",
            "notice",
            "Component boxes overlap or sit close enough to require full-size review.",
            {"pairs": crowding[:8]},
        )

    result["component_count"] = len(components)
    result["components"] = [
        {
            "box": component.box.to_list(),
            "area": component.area,
            "mean_saturation": round(component.mean_saturation, 4),
        }
        for component in components[:12]
    ]
    return result


def load_fonts() -> tuple[ImageFont.ImageFont, ImageFont.ImageFont]:
    try:
        return ImageFont.truetype("arial.ttf", 18), ImageFont.truetype("arial.ttf", 13)
    except OSError:
        return ImageFont.load_default(), ImageFont.load_default()


def draw_overlay(image: Image.Image, audit: dict, out_path: Path, margin_fraction: float) -> None:
    overlay = image.copy()
    draw = ImageDraw.Draw(overlay)
    label_font, small_font = load_fonts()
    width, height = overlay.size
    margin_x = int(width * margin_fraction)
    margin_y = int(height * margin_fraction)
    draw.rectangle([margin_x, margin_y, width - margin_x - 1, height - margin_y - 1], outline=PRIMARY_GREEN, width=2)

    if audit.get("content_box"):
        draw.rectangle(audit["content_box"], outline=PRIMARY_RED, width=4)
    if audit.get("strong_box"):
        draw.rectangle(audit["strong_box"], outline=PRIMARY_BLUE, width=3)

    for finding in audit["findings"]:
        boxes = finding.get("metrics", {}).get("boxes", [])
        for box in boxes:
            draw.rectangle(box, outline=PRIMARY_ORANGE, width=4)

    y = 12
    draw.rectangle([8, 8, width - 8, 38 + 22 * len(audit["findings"])], fill=(255, 255, 255), outline="#cfcfcf")
    draw.text((16, y), f"{audit['time']:.3f}s findings={len(audit['findings'])}", fill=GRAY, font=label_font)
    y += 22
    for finding in audit["findings"]:
        draw.text((16, y), f"{finding['severity']}: {finding['code']}", fill=PRIMARY_RED, font=small_font)
        y += 22

    out_path.parent.mkdir(parents=True, exist_ok=True)
    overlay.save(out_path)


def is_blocking(audit: dict, strict_notices: bool) -> bool:
    severities = {finding["severity"] for finding in audit["findings"]}
    return bool({"error", "warning"} & severities) or (strict_notices and "notice" in severities)


def write_outputs(out_dir: Path, audits: list[dict], args: argparse.Namespace, metadata: dict) -> None:
    out_dir.mkdir(parents=True, exist_ok=True)
    (out_dir / "audit.json").write_text(json.dumps({"metadata": metadata, "frames": audits}, indent=2), encoding="utf-8")

    with (out_dir / "audit.csv").open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(
            handle,
            fieldnames=[
                "time",
                "finding_count",
                "blocking",
                "codes",
                "min_margin",
                "center_offset_x",
                "center_offset_y",
            ],
        )
        writer.writeheader()
        for audit in audits:
            margins = audit.get("margins", {})
            center = audit.get("center_offset", {})
            writer.writerow(
                {
                    "time": audit["time"],
                    "finding_count": len(audit["findings"]),
                    "blocking": is_blocking(audit, args.strict_notices),
                    "codes": ";".join(finding["code"] for finding in audit["findings"]),
                    "min_margin": min(margins.values()) if margins else "",
                    "center_offset_x": center.get("x", ""),
                    "center_offset_y": center.get("y", ""),
                }
            )

    flagged = [audit for audit in audits if is_blocking(audit, args.strict_notices)]
    noticed = [audit for audit in audits if audit["findings"] and not is_blocking(audit, args.strict_notices)]
    lines = [
        "# Frame Composition Audit",
        "",
        f"- Video: `{metadata['video']}`",
        f"- Duration: {metadata['duration']:.3f}s",
        f"- Sampled frames: {len(audits)}",
        f"- Blocking frames: {len(flagged)}",
        f"- Notice-only frames: {len(noticed)}",
        f"- Margin threshold: {args.margin:.3f}",
        "",
    ]
    for audit in flagged[:80]:
        codes = ", ".join(finding["code"] for finding in audit["findings"])
        lines.append(f"- {audit['time']:.3f}s: {codes}")
    if len(flagged) > 80:
        lines.append(f"- ... {len(flagged) - 80} additional flagged frames omitted")
    if noticed:
        lines.extend(["", "## Notice-Only Frames", ""])
        for audit in noticed[:40]:
            codes = ", ".join(finding["code"] for finding in audit["findings"])
            lines.append(f"- {audit['time']:.3f}s: {codes}")
        if len(noticed) > 40:
            lines.append(f"- ... {len(noticed) - 40} additional notice-only frames omitted")
    (out_dir / "report.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    args = parse_args()
    video = args.video.resolve()
    if not video.exists():
        raise SystemExit(f"Video does not exist: {video}")

    out_dir = args.out_dir or (video.parent / "composition-audit")
    duration, fps, width, height = video_metadata(video)
    times = sample_times(duration, args)
    audits: list[dict] = []
    blocking_count = 0
    finding_count = 0

    for time in times:
        image = frame_at(video, time, fps)
        audit = audit_frame(image, time, args)
        audits.append(audit)
        if audit["findings"]:
            finding_count += 1
            if args.write_overlays:
                draw_overlay(image, audit, out_dir / "overlays" / f"frame-{time:07.3f}s.png", args.margin)
        if is_blocking(audit, args.strict_notices):
            blocking_count += 1

    metadata = {
        "video": str(video),
        "duration": duration,
        "fps": fps,
        "width": width,
        "height": height,
        "sample_count": len(times),
    }
    write_outputs(out_dir, audits, args, metadata)

    print(f"sampled_frames={len(audits)}")
    print(f"frames_with_findings={finding_count}")
    print(f"blocking_frames={blocking_count}")
    print(out_dir / "report.md")
    return 1 if blocking_count else 0


if __name__ == "__main__":
    raise SystemExit(main())
