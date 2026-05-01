#!/usr/bin/env -S uv run --script
# /// script
# dependencies = [
#   "av>=14.0.0",
#   "pillow>=10.0.0",
# ]
# ///

from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
from fractions import Fraction
from pathlib import Path

import av
from PIL import Image, ImageChops, ImageStat

SPIKE_DIR = Path(__file__).resolve().parent
REPO_ROOT = SPIKE_DIR.parent.parent
SPIKE_NAME = SPIKE_DIR.name
SLIDES = SPIKE_DIR / "slides.md"
OUTPUT_DIR = REPO_ROOT / "videos" / SPIKE_NAME
VIDEO = OUTPUT_DIR / f"{SPIKE_NAME}.webm"
SCREENSHOTS_DIR = OUTPUT_DIR / "screenshots"
REVIEW_FRAMES_DIR = OUTPUT_DIR / "review-frames"
RECORDER = REPO_ROOT / ".agents" / "skills" / "gjv1-slidev" / "scripts" / "record-slidev-video.mjs"
SLIDE_COUNT = 16
CLICK_PLAN = {
    2: 4,
    3: 3,
    5: 4,
    9: 2,
    10: 4,
    11: 5,
    12: 2,
    13: 3,
    14: 3,
    15: 4,
}
FRAME_MATCH_SIZE = (160, 90)
FIRST_SLIDE_MATCH_THRESHOLD = 2.5


class Args(argparse.Namespace):
    seconds_per_slide: float
    seconds_per_click: float
    transition_ms: int
    click_settle_ms: int
    trim_bitrate: int
    width: int
    height: int
    port: int


def parse_args() -> Args:
    parser = argparse.ArgumentParser(
        description="Record the Slidev transition showcase deck as a timed WebM video.",
    )
    parser.add_argument(
        "--seconds-per-slide",
        type=float,
        default=3.0,
        help="Visible hold time for each slide. Defaults to 3 seconds.",
    )
    parser.add_argument(
        "--transition-ms",
        type=int,
        default=2800,
        help="Wait time after each slide navigation key press. Defaults to 2800 ms.",
    )
    parser.add_argument(
        "--seconds-per-click",
        type=float,
        default=1.8,
        help="Visible hold time for each click animation stage. Defaults to 1.8 seconds.",
    )
    parser.add_argument(
        "--click-settle-ms",
        type=int,
        default=450,
        help="Wait time after each same-slide click. Defaults to 450 ms.",
    )
    parser.add_argument(
        "--trim-bitrate",
        type=int,
        default=14_000_000,
        help="Bitrate used when trimming the loader from the WebM. Defaults to 14000000.",
    )
    parser.add_argument("--width", type=int, default=1920, help="Recording width.")
    parser.add_argument("--height", type=int, default=1080, help="Recording height.")
    parser.add_argument("--port", type=int, default=3030, help="Slidev server port.")
    return parser.parse_args(namespace=Args())


def run_command(command: list[str]) -> None:
    print("Running:", " ".join(command))
    subprocess.run(command, cwd=REPO_ROOT, check=True)


def executable(name: str) -> str:
    if os.name == "nt" and name in {"npx", "npm"}:
        return f"{name}.cmd"
    return name


def build_deck() -> None:
    run_command([executable("npx"), "slidev", "build", str(SLIDES)])


def record_deck(args: Args) -> None:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    command = [
        "node",
        str(RECORDER),
        "--entry",
        str(SLIDES),
        "--output",
        str(VIDEO),
        "--seconds-per-slide",
        str(args.seconds_per_slide),
        "--seconds-per-click",
        str(args.seconds_per_click),
        "--transition-ms",
        str(args.transition_ms),
        "--click-settle-ms",
        str(args.click_settle_ms),
        "--click-plan",
        json.dumps(CLICK_PLAN),
        "--slide-count",
        str(SLIDE_COUNT),
        "--screenshots-dir",
        str(SCREENSHOTS_DIR),
        "--width",
        str(args.width),
        "--height",
        str(args.height),
        "--port",
        str(args.port),
    ]
    run_command(command)


def video_duration(container: av.container.InputContainer) -> float | None:
    if container.duration is None:
        return None
    return float(container.duration / av.time_base)


def collect_metrics(video: Path) -> dict[str, float | int | None]:
    with av.open(str(video)) as container:
        stream = container.streams.video[0]
        duration = video_duration(container)
        frames = 0
        for _ in container.decode(stream):
            frames += 1
        return {
            "duration_seconds": round(duration, 3) if duration is not None else None,
            "frames": frames,
            "width": stream.codec_context.width,
            "height": stream.codec_context.height,
        }


def mean_frame_difference(frame: av.VideoFrame, reference: Image.Image) -> float:
    image = frame.to_image().convert("L").resize(FRAME_MATCH_SIZE)
    diff = ImageChops.difference(image, reference)
    return float(ImageStat.Stat(diff).mean[0])


def find_first_slide_time(video: Path, reference_frame: Path) -> float | None:
    reference = Image.open(reference_frame).convert("L").resize(FRAME_MATCH_SIZE)
    with av.open(str(video)) as container:
        stream = container.streams.video[0]
        for frame in container.decode(stream):
            if frame.time is None:
                continue
            difference = mean_frame_difference(frame, reference)
            if difference <= FIRST_SLIDE_MATCH_THRESHOLD:
                return float(frame.time)
    return None


def trim_video_start(video: Path, trim_start: float, trim_bitrate: int) -> None:
    temp_video = video.with_name(f"{video.stem}.trimmed{video.suffix}")
    if temp_video.exists():
        temp_video.unlink()

    with av.open(str(video)) as source, av.open(str(temp_video), "w") as target:
        source_stream = source.streams.video[0]
        rate = source_stream.average_rate or Fraction(25, 1)
        target_stream = target.add_stream("libvpx", rate=rate)
        target_stream.width = source_stream.codec_context.width
        target_stream.height = source_stream.codec_context.height
        target_stream.pix_fmt = "yuv420p"
        target_stream.bit_rate = trim_bitrate

        frame_index = 0
        time_base = Fraction(rate.denominator, rate.numerator)
        for frame in source.decode(source_stream):
            if frame.time is None or frame.time < trim_start:
                continue
            output_frame = frame.reformat(
                target_stream.width,
                target_stream.height,
                format="yuv420p",
            )
            output_frame.pts = frame_index
            output_frame.time_base = time_base
            for packet in target_stream.encode(output_frame):
                target.mux(packet)
            frame_index += 1

        for packet in target_stream.encode(None):
            target.mux(packet)

    temp_video.replace(video)


def trim_initial_loader(video: Path, screenshots_dir: Path, trim_bitrate: int) -> None:
    reference_frame = screenshots_dir / "slide-01.png"
    if not reference_frame.exists():
        print(f"Skipping trim; reference screenshot missing: {reference_frame}")
        return

    trim_start = find_first_slide_time(video, reference_frame)
    if trim_start is None:
        print("Skipping trim; could not match the first slide in the recording.")
        return
    if trim_start < 0.25:
        print("Skipping trim; recording already starts on the first slide.")
        return

    print(f"Trimming initial Slidev loader: {trim_start:.2f}s")
    trim_video_start(video, trim_start, trim_bitrate)


def extract_review_frames(video: Path, duration: float | None) -> None:
    REVIEW_FRAMES_DIR.mkdir(parents=True, exist_ok=True)
    for old in REVIEW_FRAMES_DIR.glob("*.png"):
        old.unlink()

    if duration is None:
        targets = [0.5, 8.0, 20.0]
    else:
        targets = [0.5, max(duration / 2, 0.5), max(duration - 0.7, 0.5)]
    names = ["frame-start.png", "frame-middle.png", "frame-final.png"]

    with av.open(str(video)) as container:
        stream = container.streams.video[0]
        target_index = 0
        for frame in container.decode(stream):
            if frame.time is None:
                continue
            if frame.time >= targets[target_index]:
                frame.to_image().save(REVIEW_FRAMES_DIR / names[target_index])
                target_index += 1
                if target_index >= len(targets):
                    break


def main() -> int:
    args = parse_args()
    if not RECORDER.exists():
        print(f"Recorder script not found: {RECORDER}", file=sys.stderr)
        return 1

    build_deck()
    record_deck(args)
    trim_initial_loader(VIDEO, SCREENSHOTS_DIR, args.trim_bitrate)
    metrics = collect_metrics(VIDEO)
    extract_review_frames(VIDEO, metrics["duration_seconds"])
    summary_path = OUTPUT_DIR / "recording-summary.json"
    summary_path.write_text(json.dumps(metrics, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(metrics, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
