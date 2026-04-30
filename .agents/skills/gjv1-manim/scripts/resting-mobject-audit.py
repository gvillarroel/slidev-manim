#!/usr/bin/env python
# /// script
# dependencies = [
#   "manim>=0.20.0",
# ]
# ///
from __future__ import annotations

import argparse
import csv
import importlib.util
import json
import os
import re
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import numpy as np
from manim import ORIGIN, config, tempconfig
from manim.mobject.mobject import Mobject


@dataclass(frozen=True)
class Bounds:
    left: float
    right: float
    bottom: float
    top: float

    @property
    def width(self) -> float:
        return max(0.0, self.right - self.left)

    @property
    def height(self) -> float:
        return max(0.0, self.top - self.bottom)

    @property
    def area(self) -> float:
        return self.width * self.height

    @property
    def center(self) -> tuple[float, float]:
        return ((self.left + self.right) / 2, (self.bottom + self.top) / 2)

    def to_dict(self) -> dict[str, float]:
        return {
            "left": round(self.left, 4),
            "right": round(self.right, 4),
            "bottom": round(self.bottom, 4),
            "top": round(self.top, 4),
            "width": round(self.width, 4),
            "height": round(self.height, 4),
        }


@dataclass(frozen=True)
class Element:
    label: str
    path: str
    class_name: str
    z_index: float
    bounds: Bounds


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Run a Manim scene with skipped animations and audit visible mobject bounds "
            "at every wait/rest point for frame-edge and optional pair-overlap risks."
        )
    )
    parser.add_argument("--scene-file", type=Path, required=True, help="Python file containing the Manim scene.")
    parser.add_argument("--scene-class", required=True, help="Scene class name to instantiate.")
    parser.add_argument(
        "--out-dir",
        type=Path,
        default=None,
        help="Output directory for resting-mobject-audit.json/csv/report.md.",
    )
    parser.add_argument(
        "--margin-frac",
        type=float,
        default=0.045,
        help="Minimum edge clearance as a fraction of active camera frame width/height.",
    )
    parser.add_argument(
        "--center-tolerance",
        type=float,
        default=0.08,
        help="Allowed union-content center offset as a fraction of the active camera frame.",
    )
    parser.add_argument(
        "--granularity",
        choices=("top-level", "leaves"),
        default="top-level",
        help="Audit scene.mobjects or visible leaf mobjects.",
    )
    parser.add_argument(
        "--min-area-frac",
        type=float,
        default=0.0008,
        help="Ignore visible elements smaller than this fraction of the camera-frame area.",
    )
    parser.add_argument(
        "--skip-area-frac",
        type=float,
        default=0.92,
        help="Ignore very large background-like elements above this fraction of the camera-frame area.",
    )
    parser.add_argument(
        "--min-z-index",
        type=float,
        default=-9,
        help="Ignore elements below this z-index unless --include-backgrounds is set.",
    )
    parser.add_argument("--include-backgrounds", action="store_true", help="Do not skip low-z or large background elements.")
    parser.add_argument(
        "--ignore-pattern",
        action="append",
        default=[],
        help="Regex matched against labels/paths to ignore; may be repeated.",
    )
    parser.add_argument(
        "--check-pairs",
        action="store_true",
        help="Also report sibling element bounding-box overlaps and near-collisions.",
    )
    parser.add_argument(
        "--proximity-frac",
        type=float,
        default=0.018,
        help="Frame-size fraction used for near-collision checks when --check-pairs is set.",
    )
    parser.add_argument(
        "--setup-call",
        action="append",
        default=[],
        help="No-argument module function to call before rendering; may be repeated.",
    )
    parser.add_argument(
        "--media-dir",
        type=Path,
        default=Path("videos/.resting-mobject-audit"),
        help="Temporary Manim media directory for dry-run rendering.",
    )
    return parser.parse_args()


def import_module(path: Path) -> Any:
    module_name = f"rest_audit_{path.stem}_{abs(hash(path.resolve()))}"
    spec = importlib.util.spec_from_file_location(module_name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Could not import {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[module_name] = module
    spec.loader.exec_module(module)
    return module


def opacity_value(value: Any) -> float:
    try:
        arr = np.asarray(value, dtype=float)
        if arr.size:
            return float(np.nanmax(arr))
    except (TypeError, ValueError):
        pass
    try:
        return float(value)
    except (TypeError, ValueError):
        return 1.0


def visible_opacity(mobject: Mobject) -> float:
    values: list[float] = []
    for attr in ("fill_opacity", "stroke_opacity", "opacity"):
        value = getattr(mobject, attr, None)
        if value is not None:
            values.append(opacity_value(value))
    for name in ("get_fill_opacity", "get_stroke_opacity", "get_opacity"):
        if values:
            break
        method = getattr(mobject, name, None)
        if callable(method):
            try:
                values.append(opacity_value(method()))
            except Exception:
                continue
    return max(values) if values else 1.0


def points_bounds(points: np.ndarray) -> Bounds | None:
    if points.size == 0:
        return None
    xs = points[:, 0]
    ys = points[:, 1]
    return Bounds(float(xs.min()), float(xs.max()), float(ys.min()), float(ys.max()))


def visible_bounds(mobject: Mobject, opacity_threshold: float = 0.025) -> Bounds | None:
    chunks: list[np.ndarray] = []
    for member in mobject.family_members_with_points():
        if visible_opacity(member) <= opacity_threshold:
            continue
        points = getattr(member, "points", None)
        if points is None:
            points = member.get_points()
        if points.size:
            chunks.append(points)
    if not chunks:
        return None
    return points_bounds(np.vstack(chunks))


def camera_bounds(scene: Any) -> Bounds:
    frame = getattr(getattr(scene, "camera", None), "frame", None)
    if frame is not None:
        center = frame.get_center()
        width = float(frame.width)
        height = float(frame.height)
    else:
        center = ORIGIN
        width = float(config.frame_width)
        height = float(config.frame_height)
    return Bounds(
        float(center[0] - width / 2),
        float(center[0] + width / 2),
        float(center[1] - height / 2),
        float(center[1] + height / 2),
    )


def text_label(mobject: Mobject) -> str | None:
    for attr in ("audit_name", "text", "original_text", "tex_string"):
        value = getattr(mobject, attr, None)
        if value:
            return str(value)
    return None


def label_for(mobject: Mobject, path: str) -> str:
    explicit = text_label(mobject)
    if explicit:
        return f"{mobject.__class__.__name__}({explicit!r})"
    name = getattr(mobject, "name", "")
    if name and name != mobject.__class__.__name__:
        return f"{mobject.__class__.__name__}({name})"
    return f"{mobject.__class__.__name__}@{path}"


def iter_elements(scene: Any, granularity: str) -> list[tuple[str, Mobject]]:
    elements: list[tuple[str, Mobject]] = []
    if granularity == "top-level":
        return [(f"scene[{index}]", mobject) for index, mobject in enumerate(scene.mobjects)]

    for top_index, top in enumerate(scene.mobjects):
        for leaf_index, leaf in enumerate(top.family_members_with_points()):
            elements.append((f"scene[{top_index}].leaf[{leaf_index}]", leaf))
    return elements


def should_ignore(element: Element, frame: Bounds, args: argparse.Namespace, patterns: list[re.Pattern[str]]) -> bool:
    target = f"{element.label} {element.path}"
    if any(pattern.search(target) for pattern in patterns):
        return True
    frame_area = max(0.001, frame.area)
    area_frac = element.bounds.area / frame_area
    if area_frac < args.min_area_frac:
        return True
    if args.include_backgrounds:
        return False
    if element.z_index < args.min_z_index:
        return True
    return area_frac > args.skip_area_frac


def collect_elements(scene: Any, frame: Bounds, args: argparse.Namespace, patterns: list[re.Pattern[str]]) -> list[Element]:
    elements: list[Element] = []
    for path, mobject in iter_elements(scene, args.granularity):
        bounds = visible_bounds(mobject)
        if bounds is None:
            continue
        element = Element(
            label=label_for(mobject, path),
            path=path,
            class_name=mobject.__class__.__name__,
            z_index=float(getattr(mobject, "z_index", 0)),
            bounds=bounds,
        )
        if not should_ignore(element, frame, args, patterns):
            elements.append(element)
    return elements


def clearance(element: Element, frame: Bounds) -> dict[str, float]:
    return {
        "left": element.bounds.left - frame.left,
        "right": frame.right - element.bounds.right,
        "bottom": element.bounds.bottom - frame.bottom,
        "top": frame.top - element.bounds.top,
    }


def edge_findings(element: Element, frame: Bounds, args: argparse.Namespace) -> list[dict[str, Any]]:
    margins = clearance(element, frame)
    thresholds = {
        "left": frame.width * args.margin_frac,
        "right": frame.width * args.margin_frac,
        "bottom": frame.height * args.margin_frac,
        "top": frame.height * args.margin_frac,
    }
    findings: list[dict[str, Any]] = []
    outside = {side: value for side, value in margins.items() if value < 0}
    if outside:
        findings.append(
            {
                "code": "outside_frame",
                "severity": "error",
                "element": element.label,
                "path": element.path,
                "clearance": {side: round(value, 4) for side, value in outside.items()},
            }
        )
    low = {side: value for side, value in margins.items() if 0 <= value < thresholds[side]}
    if low:
        findings.append(
            {
                "code": "low_edge_clearance",
                "severity": "warning",
                "element": element.label,
                "path": element.path,
                "clearance": {side: round(value, 4) for side, value in low.items()},
                "minimum": {side: round(thresholds[side], 4) for side in low},
            }
        )
    return findings


def union_bounds(elements: list[Element]) -> Bounds | None:
    if not elements:
        return None
    return Bounds(
        min(element.bounds.left for element in elements),
        max(element.bounds.right for element in elements),
        min(element.bounds.bottom for element in elements),
        max(element.bounds.top for element in elements),
    )


def content_findings(elements: list[Element], frame: Bounds, args: argparse.Namespace) -> list[dict[str, Any]]:
    bounds = union_bounds(elements)
    if bounds is None:
        return []
    center_x, center_y = bounds.center
    offset = {
        "x": (center_x - frame.center[0]) / frame.width,
        "y": (center_y - frame.center[1]) / frame.height,
    }
    if abs(offset["x"]) <= args.center_tolerance and abs(offset["y"]) <= args.center_tolerance:
        return []
    return [
        {
            "code": "off_center_rest_content",
            "severity": "warning",
            "offset": {axis: round(value, 4) for axis, value in offset.items()},
            "tolerance": args.center_tolerance,
            "content_bounds": bounds.to_dict(),
        }
    ]


def intersection(a: Bounds, b: Bounds) -> float:
    left = max(a.left, b.left)
    right = min(a.right, b.right)
    bottom = max(a.bottom, b.bottom)
    top = min(a.top, b.top)
    if right <= left or top <= bottom:
        return 0.0
    return (right - left) * (top - bottom)


def contains(container: Bounds, child: Bounds, pad: float = 0.0) -> bool:
    return (
        container.left - pad <= child.left
        and container.right + pad >= child.right
        and container.bottom - pad <= child.bottom
        and container.top + pad >= child.top
    )


def expanded(bounds: Bounds, amount: float) -> Bounds:
    return Bounds(bounds.left - amount, bounds.right + amount, bounds.bottom - amount, bounds.top + amount)


def pair_findings(elements: list[Element], frame: Bounds, args: argparse.Namespace) -> list[dict[str, Any]]:
    if not args.check_pairs:
        return []
    proximity = min(frame.width, frame.height) * args.proximity_frac
    findings: list[dict[str, Any]] = []
    for left_index, left in enumerate(elements):
        for right in elements[left_index + 1 :]:
            if contains(left.bounds, right.bounds, proximity) or contains(right.bounds, left.bounds, proximity):
                continue
            overlap = intersection(left.bounds, right.bounds)
            expanded_overlap = intersection(expanded(left.bounds, proximity), expanded(right.bounds, proximity))
            if overlap <= 0 and expanded_overlap <= 0:
                continue
            ratio = max(overlap, expanded_overlap) / max(0.001, min(left.bounds.area, right.bounds.area))
            if overlap > 0 or ratio > 0.12:
                findings.append(
                    {
                        "code": "possible_mobject_overlap",
                        "severity": "notice",
                        "left": left.label,
                        "right": right.label,
                        "overlap_area": round(overlap, 4),
                        "expanded_overlap_ratio": round(ratio, 4),
                    }
                )
    return findings[:80]


def snapshot(scene: Any, rest_index: int, duration: float, args: argparse.Namespace, patterns: list[re.Pattern[str]]) -> dict[str, Any]:
    frame = camera_bounds(scene)
    elements = collect_elements(scene, frame, args, patterns)
    findings: list[dict[str, Any]] = []
    for element in elements:
        findings.extend(edge_findings(element, frame, args))
    findings.extend(content_findings(elements, frame, args))
    findings.extend(pair_findings(elements, frame, args))
    return {
        "rest_index": rest_index,
        "time": round(float(getattr(scene.renderer, "time", 0.0)), 4),
        "wait_duration": round(float(duration), 4),
        "camera_frame": frame.to_dict(),
        "content_bounds": union_bounds(elements).to_dict() if elements else None,
        "elements": [
            {
                "label": element.label,
                "path": element.path,
                "class_name": element.class_name,
                "z_index": element.z_index,
                "bounds": element.bounds.to_dict(),
                "clearance": {side: round(value, 4) for side, value in clearance(element, frame).items()},
            }
            for element in elements
        ],
        "findings": findings,
    }


def write_outputs(out_dir: Path, snapshots: list[dict[str, Any]], metadata: dict[str, Any]) -> None:
    out_dir.mkdir(parents=True, exist_ok=True)
    (out_dir / "resting-mobject-audit.json").write_text(
        json.dumps({"metadata": metadata, "rests": snapshots}, indent=2),
        encoding="utf-8",
    )
    with (out_dir / "resting-mobject-audit.csv").open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=["rest_index", "time", "wait_duration", "finding_count", "codes"])
        writer.writeheader()
        for item in snapshots:
            writer.writerow(
                {
                    "rest_index": item["rest_index"],
                    "time": item["time"],
                    "wait_duration": item["wait_duration"],
                    "finding_count": len(item["findings"]),
                    "codes": ";".join(finding["code"] for finding in item["findings"]),
                }
            )

    blocking_count = sum(
        1
        for item in snapshots
        if any(finding["severity"] in {"error", "warning"} for finding in item["findings"])
    )
    notice_only_count = sum(
        1
        for item in snapshots
        if item["findings"] and not any(finding["severity"] in {"error", "warning"} for finding in item["findings"])
    )
    lines = [
        "# Resting Mobject Audit",
        "",
        f"- Scene file: `{metadata['scene_file']}`",
        f"- Scene class: `{metadata['scene_class']}`",
        f"- Rest snapshots: {len(snapshots)}",
        f"- Blocking snapshots: {blocking_count}",
        f"- Notice-only snapshots: {notice_only_count}",
        f"- Margin fraction: {metadata['margin_frac']:.3f}",
        "",
    ]
    for item in snapshots:
        if not item["findings"]:
            continue
        lines.append(f"## Rest {item['rest_index']:02d} at {item['time']:.3f}s")
        lines.append("")
        lines.append(f"- Wait duration: {item['wait_duration']:.3f}s")
        for finding in item["findings"][:30]:
            element = finding.get("element") or f"{finding.get('left')} / {finding.get('right')}"
            detail = finding.get("clearance") or finding.get("offset") or {}
            lines.append(f"- {finding['severity']}: `{finding['code']}` {element} {detail}")
        if len(item["findings"]) > 30:
            lines.append(f"- ... {len(item['findings']) - 30} additional findings omitted")
        lines.append("")
    if all(not item["findings"] for item in snapshots):
        lines.append("No rest-state mobject edge findings.")
    (out_dir / "report.md").write_text("\n".join(lines).rstrip() + "\n", encoding="utf-8")


def main() -> int:
    args = parse_args()
    scene_file = args.scene_file.resolve()
    if not scene_file.exists():
        raise SystemExit(f"Scene file does not exist: {scene_file}")
    module = import_module(scene_file)
    for function_name in args.setup_call:
        function = getattr(module, function_name, None)
        if not callable(function):
            raise SystemExit(f"--setup-call target is not callable: {function_name}")
        function()
    scene_class = getattr(module, args.scene_class, None)
    if scene_class is None:
        raise SystemExit(f"Scene class not found: {args.scene_class}")

    patterns = [re.compile(pattern) for pattern in args.ignore_pattern]
    snapshots: list[dict[str, Any]] = []
    scene = scene_class(skip_animations=True)
    original_wait = scene.wait

    def audited_wait(duration: float = 1.0, *wait_args: Any, **wait_kwargs: Any) -> Any:
        snapshots.append(snapshot(scene, len(snapshots) + 1, duration, args, patterns))
        return original_wait(duration, *wait_args, **wait_kwargs)

    scene.wait = audited_wait
    media_dir = args.media_dir if args.media_dir.is_absolute() else Path.cwd() / args.media_dir
    with tempconfig(
        {
            "dry_run": True,
            "write_to_movie": False,
            "format": "png",
            "media_dir": str(media_dir),
            "disable_caching": True,
        }
    ):
        previous_target = os.environ.get("SPIKE_RENDER_TARGET")
        os.environ.setdefault("SPIKE_RENDER_TARGET", "video")
        try:
            scene.render()
        finally:
            if previous_target is None:
                os.environ.pop("SPIKE_RENDER_TARGET", None)
            else:
                os.environ["SPIKE_RENDER_TARGET"] = previous_target

    out_dir = args.out_dir
    if out_dir is None:
        out_dir = scene_file.parent / "resting-mobject-audit"
    out_dir = out_dir.resolve()
    metadata = {
        "scene_file": str(scene_file),
        "scene_class": args.scene_class,
        "margin_frac": args.margin_frac,
        "granularity": args.granularity,
        "check_pairs": args.check_pairs,
    }
    write_outputs(out_dir, snapshots, metadata)
    blocking = sum(1 for item in snapshots if any(finding["severity"] in {"error", "warning"} for finding in item["findings"]))
    noticed = sum(1 for item in snapshots if item["findings"]) - blocking
    print(f"rest_snapshots={len(snapshots)}")
    print(f"blocking_snapshots={blocking}")
    print(f"notice_only_snapshots={noticed}")
    print(out_dir / "report.md")
    return 1 if blocking else 0


if __name__ == "__main__":
    raise SystemExit(main())
