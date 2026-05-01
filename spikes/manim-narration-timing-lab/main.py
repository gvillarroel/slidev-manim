#!/usr/bin/env -S uv run --script
# /// script
# dependencies = [
#   "manim==0.20.1",
#   "av>=14.0.0",
#   "pillow>=10.0.0",
# ]
# ///

from __future__ import annotations

import argparse
import json
import math
import shutil
import subprocess
import sys
from contextlib import contextmanager
from dataclasses import dataclass
from pathlib import Path
from typing import Iterator

from manim import (
    DOWN,
    LEFT,
    RIGHT,
    UP,
    AnimationGroup,
    ChangeSpeed,
    Dot,
    FadeIn,
    FadeOut,
    LaggedStart,
    Line,
    Rectangle,
    Scene,
    Succession,
    Text,
    VGroup,
    Wait,
    linear,
)

SPIKE_DIR = Path(__file__).resolve().parent
REPO_ROOT = SPIKE_DIR.parent.parent
SPIKE_NAME = SPIKE_DIR.name
OUTPUT_DIR = REPO_ROOT / "videos" / SPIKE_NAME
STAGING_DIR = OUTPUT_DIR / ".manim"

PRIMARY_RED = "#9e1b32"
HIGHLIGHT_RED = "#ffccd5"
SHADOW_RED = "#6d1222"
WHITE = "#ffffff"
PAGE_BACKGROUND = "#f7f7f7"
GRAY = "#333e48"
GRAY_100 = "#e7e7e7"
GRAY_200 = "#cfcfcf"
GRAY_300 = "#b5b5b5"
GRAY_500 = "#828282"
GRAY_700 = "#4f4f4f"
GRAY_900 = "#1c1c1c"
FONT_FAMILY = "Arial"

SLOW_SPEEDINFO = {0.0: 1.0, 0.38: 1.0, 0.48: 0.14, 0.76: 0.14, 1.0: 1.0}
PROOF_TIMES = (1.0, 3.0, 7.3, 14.5, 21.5)


@dataclass(frozen=True)
class ScriptedCue:
    name: str
    section_name: str
    duration: float
    caption: str


SCRIPTED_CUES = (
    ScriptedCue(
        name="opening-breath",
        section_name="01 opening breath",
        duration=2.5,
        caption="Show the structure first, then let the slide breathe.",
    ),
    ScriptedCue(
        name="progressive-beat-groups",
        section_name="02 progressive beat groups",
        duration=6.5,
        caption="Reveal supporting ideas as grouped beats, not as one burst.",
    ),
    ScriptedCue(
        name="deliberate-slowdown",
        section_name="03 deliberate slow-down and hold",
        duration=7.5,
        caption="Slow the critical motion and hold it while the narration lands.",
    ),
    ScriptedCue(
        name="section-cue-metadata",
        section_name="04 section cue metadata",
        duration=5.0,
        caption="Expose clean section boundaries for slide and edit tooling.",
    ),
    ScriptedCue(
        name="resolved-final-hold",
        section_name="05 resolved final hold",
        duration=7.0,
        caption="Finish with a stable frame long enough for the presenter.",
    ),
)


class _Args(argparse.Namespace):
    quality: str


def parse_args() -> _Args:
    parser = argparse.ArgumentParser(description="Render the Manim narration timing lab spike.")
    parser.add_argument("--quality", choices=("low", "medium", "high", "production", "4k"), default="low")
    return parser.parse_args(namespace=_Args())


def quality_flag(quality: str) -> str:
    return {"low": "-ql", "medium": "-qm", "high": "-qh", "production": "-qp", "4k": "-qk"}[quality]


def text(label: str, font_size: int, color: str = GRAY_900) -> Text:
    return Text(label, font=FONT_FAMILY, font_size=font_size, color=color)


def zone(label: str, center) -> VGroup:
    panel = Rectangle(
        width=2.35,
        height=1.15,
        stroke_color=GRAY_300,
        stroke_width=2,
        fill_color=WHITE,
        fill_opacity=0.92,
    )
    panel.move_to(center)
    title = text(label, 22, GRAY).move_to(center + UP * 0.31)
    panel.set_z_index(1)
    title.set_z_index(3)
    return VGroup(panel, title)


def beat_cluster() -> VGroup:
    bars = VGroup(
        Rectangle(width=0.16, height=0.48, stroke_width=0, fill_color=GRAY_700, fill_opacity=1),
        Rectangle(width=0.16, height=0.74, stroke_width=0, fill_color=PRIMARY_RED, fill_opacity=1),
        Rectangle(width=0.16, height=0.36, stroke_width=0, fill_color=GRAY_500, fill_opacity=1),
    )
    bars.arrange(RIGHT, buff=0.07, aligned_edge=DOWN)
    return bars


def metadata_chip(index: int, cue: ScriptedCue) -> VGroup:
    short_name = cue.section_name[3:].replace(" and ", " + ")
    short_name = {
        "opening breath": "breath",
        "progressive beat groups": "beats",
        "deliberate slow-down + hold": "slow/hold",
        "section cue metadata": "sections",
        "resolved final hold": "final hold",
    }.get(short_name, short_name)
    body = Rectangle(
        width=2.02,
        height=0.48,
        stroke_color=GRAY_300,
        stroke_width=1.4,
        fill_color=WHITE,
        fill_opacity=0.94,
    )
    code = text(f"{index:02d}", 13, PRIMARY_RED)
    name = text(short_name, 13, GRAY)
    duration = text(f"{cue.duration:.1f}s", 13, GRAY_700)
    label_group = VGroup(code, name, duration).arrange(RIGHT, buff=0.08)
    label_group.move_to(body)
    return VGroup(body, label_group)


def metadata_slot() -> Rectangle:
    return Rectangle(
        width=2.02,
        height=0.48,
        stroke_color=GRAY_500,
        stroke_width=2.0,
        fill_color=WHITE,
        fill_opacity=0.82,
    )


def slow_motion_inner_run_time(target_duration: float) -> float:
    probe = ChangeSpeed(Wait(run_time=1), speedinfo=SLOW_SPEEDINFO, rate_func=linear, affects_speed_updaters=False)
    return target_duration / probe.get_scaled_total_time()


class NarrationTimingLabScene(Scene):
    def setup(self) -> None:
        self.narration_cues: list[dict[str, object]] = []

    @contextmanager
    def scripted_voiceover(self, cue: ScriptedCue) -> Iterator[ScriptedCue]:
        start = float(self.time)
        yield cue
        end = float(self.time)
        self.narration_cues.append(
            {
                "name": cue.name,
                "section_name": cue.section_name,
                "caption": cue.caption,
                "planned_duration_seconds": cue.duration,
                "actual_duration_seconds": round(end - start, 3),
                "start_seconds": round(start, 3),
                "end_seconds": round(end, 3),
                "requires_audio_service": False,
            }
        )

    def construct(self) -> None:
        self.camera.background_color = PAGE_BACKGROUND

        stage = Rectangle(width=14.22, height=8.0, stroke_width=0, fill_color=PAGE_BACKGROUND, fill_opacity=1).set_z_index(0)
        title = text("Narration timing", 34, GRAY_900).to_edge(UP).shift(DOWN * 0.36)
        title.set_z_index(5)

        centers = [LEFT * 4.35 + UP * 1.0, LEFT * 1.45 + UP * 1.0, RIGHT * 1.45 + UP * 1.0, RIGHT * 4.35 + UP * 1.0]
        zones = VGroup(
            zone("breath", centers[0]),
            zone("beats", centers[1]),
            zone("slow", centers[2]),
            zone("sections", centers[3]),
        )
        zone_boxes = VGroup(*[item[0] for item in zones])
        zone_labels = VGroup(*[item[1] for item in zones])

        rail_y = -0.77
        marker_targets = [center[0] * RIGHT + rail_y * UP for center in centers]
        rail = Line(marker_targets[0] + LEFT * 0.45, marker_targets[-1] + RIGHT * 0.45, color=GRAY_300, stroke_width=7).set_z_index(1)
        ticks = VGroup(
            *[
                Line(point + UP * 0.24, point + DOWN * 0.24, color=GRAY_500, stroke_width=3)
                for point in marker_targets
            ]
        ).set_z_index(2)
        active_rail = Line(marker_targets[0] + LEFT * 0.01, marker_targets[0], color=PRIMARY_RED, stroke_width=8).set_z_index(2)
        timing_marker = Dot(radius=0.15, color=PRIMARY_RED).move_to(marker_targets[0]).set_z_index(4)

        metadata_panel = Rectangle(
            width=11.6,
            height=1.12,
            stroke_color=GRAY_300,
            stroke_width=1.6,
            fill_color=WHITE,
            fill_opacity=0.72,
        ).move_to(DOWN * 2.64).set_z_index(1)
        metadata_slots = VGroup(*[metadata_slot() for _ in SCRIPTED_CUES])
        metadata_slots.arrange(RIGHT, buff=0.12).move_to(metadata_panel)
        metadata_slots.set_z_index(2)

        self.add(stage, title, zones, rail, ticks, active_rail, timing_marker, metadata_panel, metadata_slots)

        self.next_section(name=SCRIPTED_CUES[0].section_name)
        with self.scripted_voiceover(SCRIPTED_CUES[0]) as cue:
            self.wait(cue.duration)

        self.next_section(name=SCRIPTED_CUES[1].section_name)
        beat_groups = VGroup(*[beat_cluster() for _ in range(3)]).arrange(RIGHT, buff=0.26)
        beat_groups.move_to(centers[1] + DOWN * 0.22)
        beat_groups.set_z_index(4)
        beat_echo = Rectangle(
            width=2.1,
            height=0.84,
            stroke_color=PRIMARY_RED,
            stroke_width=2,
            fill_color=HIGHLIGHT_RED,
            fill_opacity=0.22,
        ).move_to(centers[1]).set_z_index(2)
        with self.scripted_voiceover(SCRIPTED_CUES[1]) as cue:
            self.play(
                Succession(
                    AnimationGroup(
                        timing_marker.animate.move_to(marker_targets[1]),
                        active_rail.animate.put_start_and_end_on(marker_targets[0], marker_targets[1]),
                        zone_boxes[1].animate.set_stroke(PRIMARY_RED, width=4),
                        run_time=1.3,
                    ),
                    LaggedStart(
                        *[FadeIn(group, shift=UP * 0.12) for group in beat_groups],
                        lag_ratio=0.32,
                        run_time=3.2,
                    ),
                    AnimationGroup(
                        FadeIn(beat_echo),
                        timing_marker.animate.scale(1.18),
                        run_time=1.0,
                    ),
                    FadeOut(beat_echo, run_time=0.7),
                ),
                run_time=cue.duration,
            )

        self.next_section(name=SCRIPTED_CUES[2].section_name)
        slow_frame = Rectangle(
            width=2.42,
            height=1.22,
            stroke_color=PRIMARY_RED,
            stroke_width=3,
            fill_color=HIGHLIGHT_RED,
            fill_opacity=0.16,
        ).move_to(centers[2]).set_z_index(2)
        pause_marks = VGroup(
            Rectangle(width=0.16, height=0.68, stroke_width=0, fill_color=SHADOW_RED, fill_opacity=1),
            Rectangle(width=0.16, height=0.68, stroke_width=0, fill_color=SHADOW_RED, fill_opacity=1),
        ).arrange(RIGHT, buff=0.18)
        pause_marks.move_to(centers[2] + DOWN * 0.22)
        pause_marks.set_z_index(4)

        with self.scripted_voiceover(SCRIPTED_CUES[2]) as cue:
            self.play(FadeIn(slow_frame), zone_boxes[2].animate.set_stroke(PRIMARY_RED, width=4), run_time=0.75)
            slow_duration = 4.65
            self.play(
                ChangeSpeed(
                    AnimationGroup(
                        timing_marker.animate.move_to(marker_targets[2]),
                        active_rail.animate.put_start_and_end_on(marker_targets[0], marker_targets[2]),
                        FadeIn(pause_marks, shift=UP * 0.08),
                        slow_frame.animate.set_fill(HIGHLIGHT_RED, opacity=0.48),
                        run_time=slow_motion_inner_run_time(slow_duration),
                    ),
                    speedinfo=SLOW_SPEEDINFO,
                    rate_func=linear,
                    affects_speed_updaters=False,
                )
            )
            self.wait(cue.duration - 0.75 - slow_duration)

        self.next_section(name=SCRIPTED_CUES[3].section_name)
        chips = VGroup(*[metadata_chip(index, cue) for index, cue in enumerate(SCRIPTED_CUES, start=1)])
        chips.arrange(RIGHT, buff=0.12).move_to(metadata_panel)
        chips.set_z_index(4)

        with self.scripted_voiceover(SCRIPTED_CUES[3]) as cue:
            self.play(
                AnimationGroup(
                    timing_marker.animate.move_to(marker_targets[3]),
                    active_rail.animate.put_start_and_end_on(marker_targets[0], marker_targets[3]),
                    zone_boxes[3].animate.set_stroke(PRIMARY_RED, width=4),
                    run_time=1.0,
                ),
            )
            self.play(
                LaggedStart(
                    *[
                        AnimationGroup(FadeOut(slot), FadeIn(chip, shift=RIGHT * 0.12), run_time=1.0)
                        for slot, chip in zip(metadata_slots, chips)
                    ],
                    lag_ratio=0.16,
                    run_time=3.2,
                )
            )
            self.play(metadata_panel.animate.set_stroke(PRIMARY_RED, width=2.5), run_time=cue.duration - 4.2)

        self.next_section(name=SCRIPTED_CUES[4].section_name)
        final_badge_box = Rectangle(width=2.55, height=0.48, stroke_width=0, fill_color=PRIMARY_RED, fill_opacity=1)
        final_badge_text = text("narration-ready", 18, WHITE).move_to(final_badge_box)
        final_badge = VGroup(final_badge_box, final_badge_text).move_to(DOWN * 1.2)
        final_badge.set_z_index(5)

        with self.scripted_voiceover(SCRIPTED_CUES[4]) as cue:
            cleanup_duration = 0.45
            final_lift = UP * 0.35
            self.play(
                FadeOut(slow_frame),
                FadeOut(pause_marks),
                zone_boxes.animate.set_stroke(GRAY_300, width=2).shift(final_lift),
                zone_labels.animate.shift(final_lift),
                beat_groups.animate.shift(final_lift),
                rail.animate.shift(final_lift),
                ticks.animate.shift(final_lift),
                active_rail.animate.shift(final_lift),
                metadata_panel.animate.shift(UP * 0.6).set_stroke(GRAY_200, width=1.5),
                chips.animate.shift(UP * 0.6),
                FadeIn(final_badge, shift=UP * 0.14),
                timing_marker.animate.move_to(marker_targets[3] + final_lift).set_fill(PRIMARY_RED, opacity=1).scale(1.06),
                run_time=cleanup_duration,
            )
            self.wait(cue.duration - cleanup_duration)

        self.write_scripted_cues()

    def write_scripted_cues(self) -> None:
        OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
        payload = {
            "spike": SPIKE_NAME,
            "pattern": "scripted voiceover durations without microphone or TTS service",
            "cues": self.narration_cues,
        }
        (OUTPUT_DIR / "scripted-cues.json").write_text(json.dumps(payload, indent=2), encoding="utf-8")


def render_command(args: _Args, stem: str) -> list[str]:
    STAGING_DIR.mkdir(parents=True, exist_ok=True)
    return [
        sys.executable,
        "-m",
        "manim",
        "render",
        quality_flag(args.quality),
        "-r",
        "1600,900",
        "--format",
        "webm",
        "--save_sections",
        "-o",
        stem,
        "--media_dir",
        str(STAGING_DIR),
        str(Path(__file__).resolve()),
        "NarrationTimingLabScene",
    ]


def promote_file(target_name: str, destination: Path) -> None:
    matches = sorted(STAGING_DIR.glob(f"**/{target_name}"), key=lambda path: path.stat().st_mtime)
    if not matches:
        raise FileNotFoundError(target_name)
    destination.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(matches[-1], destination)


def promote_sections() -> Path | None:
    candidates = [path for path in STAGING_DIR.glob("**/sections") if any(path.iterdir())]
    if not candidates:
        return None
    source = max(candidates, key=lambda path: max(item.stat().st_mtime for item in path.iterdir()))
    destination = OUTPUT_DIR / "sections"
    if destination.exists():
        shutil.rmtree(destination)
    shutil.copytree(source, destination)
    return destination


def video_duration_hint(container, stream) -> float | None:
    if container.duration is not None:
        return float(container.duration / 1_000_000)
    if stream.duration is not None and stream.time_base is not None:
        return float(stream.duration * stream.time_base)
    return None


def extract_proof_artifacts(video_path: Path, sections_dir: Path | None) -> None:
    import av
    from PIL import Image, ImageDraw

    proof_dir = OUTPUT_DIR / "proof-frames"
    if proof_dir.exists():
        shutil.rmtree(proof_dir)
    proof_dir.mkdir(parents=True, exist_ok=True)

    container = av.open(str(video_path))
    stream = container.streams.video[0]
    fps = float(stream.average_rate) if stream.average_rate else 0.0
    duration_hint = video_duration_hint(container, stream)
    targets = list(PROOF_TIMES)
    if duration_hint is not None:
        targets.append(max(duration_hint - 1.0, 0.0))

    best: dict[float, tuple[float, int, float, Image.Image] | None] = {target: None for target in targets}
    frame_count = 0
    has_transparency = False
    last_time = 0.0

    for index, frame in enumerate(container.decode(stream)):
        timestamp = float(frame.time) if frame.time is not None else (index / fps if fps else float(index))
        last_time = timestamp
        image = frame.to_image().convert("RGBA")
        alpha = image.getchannel("A").getextrema()
        has_transparency = has_transparency or alpha[0] < 255
        for target in targets:
            distance = abs(timestamp - target)
            current = best[target]
            if current is None or distance < current[0]:
                best[target] = (distance, index, timestamp, image.copy())
        frame_count = index + 1

    container.close()

    duration = duration_hint if duration_hint is not None else (frame_count / fps if fps else last_time)
    saved_frames: list[dict[str, object]] = []
    sheet_tiles: list[tuple[Image.Image, str]] = []
    for order, target in enumerate(targets, start=1):
        candidate = best[target]
        if candidate is None:
            continue
        _, frame_index, timestamp, image = candidate
        frame_path = proof_dir / f"frame-{order:02d}-{timestamp:05.2f}s.png"
        image.save(frame_path)
        saved_frames.append(
            {
                "target_seconds": round(target, 3),
                "actual_seconds": round(timestamp, 3),
                "frame_index": frame_index,
                "path": str(frame_path),
            }
        )
        sheet_tiles.append((image, f"{timestamp:05.2f}s  frame {frame_index}"))

    thumb_width = 320
    thumb_height = 180
    label_height = 28
    columns = 3
    rows = math.ceil(len(sheet_tiles) / columns)
    sheet = Image.new("RGB", (columns * thumb_width, rows * (thumb_height + label_height)), WHITE)
    draw = ImageDraw.Draw(sheet)

    for index, (image, label) in enumerate(sheet_tiles):
        x = (index % columns) * thumb_width
        y = (index // columns) * (thumb_height + label_height)
        thumb = image.convert("RGB").resize((thumb_width, thumb_height))
        sheet.paste(thumb, (x, y))
        draw.rectangle((x, y + thumb_height, x + thumb_width, y + thumb_height + label_height), fill=WHITE)
        draw.text((x + 8, y + thumb_height + 7), label, fill=GRAY)

    contact_sheet_path = OUTPUT_DIR / "proof-contact-sheet.png"
    sheet.save(contact_sheet_path)

    section_jsons = sorted(sections_dir.glob("*.json")) if sections_dir else []
    sections = json.loads(section_jsons[0].read_text(encoding="utf-8")) if section_jsons else []
    validation = {
        "video": str(video_path),
        "duration_seconds": round(duration, 3),
        "frame_count": frame_count,
        "fps": round(fps, 3),
        "has_alpha_transparency": has_transparency,
        "stage": "opaque page-background stage",
        "sections_json": str(section_jsons[0]) if section_jsons else None,
        "section_count": len(sections),
        "sections": [
            {
                "name": section.get("name"),
                "duration_seconds": float(section.get("duration", 0)),
                "frames": int(section.get("nb_frames", 0)),
            }
            for section in sections
        ],
        "proof_contact_sheet": str(contact_sheet_path),
        "proof_frames": saved_frames,
    }
    (OUTPUT_DIR / "validation.json").write_text(json.dumps(validation, indent=2), encoding="utf-8")


def render_variant(args: _Args) -> Path:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    video_path = OUTPUT_DIR / f"{SPIKE_NAME}.webm"
    result = subprocess.run(render_command(args, video_path.stem), check=False)
    if result.returncode != 0:
        raise SystemExit(result.returncode)
    promote_file(video_path.name, video_path)
    sections_dir = promote_sections()
    extract_proof_artifacts(video_path, sections_dir)
    return video_path


def main() -> int:
    args = parse_args()
    render_variant(args)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
