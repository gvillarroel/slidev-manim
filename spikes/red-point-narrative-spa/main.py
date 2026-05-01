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
import socket
import subprocess
import sys
import time
from pathlib import Path

import av

SPIKE_DIR = Path(__file__).resolve().parent
REPO_ROOT = SPIKE_DIR.parent.parent
SPIKE_NAME = SPIKE_DIR.name
OUTPUT_DIR = REPO_ROOT / "videos" / SPIKE_NAME
SCREENSHOTS_DIR = OUTPUT_DIR / "screenshots"
REVIEW_FRAMES_DIR = OUTPUT_DIR / "review-frames"
TEMP_VIDEO_DIR = OUTPUT_DIR / "recording-temp"
VIDEO = OUTPUT_DIR / f"{SPIKE_NAME}.webm"
SUMMARY = OUTPUT_DIR / "capture-summary.json"
RECORD_SCRIPT = SPIKE_DIR / "record-spa-video.mjs"


class Args(argparse.Namespace):
    width: int
    height: int
    port: int


def parse_args() -> Args:
    parser = argparse.ArgumentParser(
        description="Capture the red point narrative SPA as a reviewable WebM and screenshot set.",
    )
    parser.add_argument("--width", type=int, default=1920, help="Capture width.")
    parser.add_argument("--height", type=int, default=1080, help="Capture height.")
    parser.add_argument("--port", type=int, default=4173, help="Local static server port.")
    return parser.parse_args(namespace=Args())


def executable(name: str) -> str:
    if os.name == "nt" and name == "npx":
        return f"{name}.cmd"
    return name


def run_command(command: list[str]) -> None:
    print("Running:", " ".join(command))
    subprocess.run(command, cwd=REPO_ROOT, check=True)


def ensure_port_open(port: int, timeout_seconds: float = 10.0) -> None:
    deadline = time.time() + timeout_seconds
    while time.time() < deadline:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            sock.settimeout(0.25)
            if sock.connect_ex(("127.0.0.1", port)) == 0:
                return
        time.sleep(0.2)
    raise RuntimeError(f"Timed out waiting for local server on port {port}.")


def clear_directory(directory: Path) -> None:
    if not directory.exists():
        return
    for child in directory.iterdir():
        if child.is_dir():
            clear_directory(child)
            child.rmdir()
        else:
            child.unlink()


def start_server(port: int) -> subprocess.Popen[str]:
    command = [
        sys.executable,
        "-m",
        "http.server",
        str(port),
        "--bind",
        "127.0.0.1",
    ]
    print("Running:", " ".join(command))
    process = subprocess.Popen(
        command,
        cwd=SPIKE_DIR,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    )
    ensure_port_open(port)
    return process


def stop_server(process: subprocess.Popen[str]) -> None:
    process.terminate()
    try:
        process.wait(timeout=5)
    except subprocess.TimeoutExpired:
        process.kill()
        process.wait(timeout=5)


def validate_sources() -> None:
    run_command([executable("node"), "--check", str(SPIKE_DIR / "app.js")])
    run_command([executable("node"), "--check", str(RECORD_SCRIPT)])


def capture_spa(args: Args) -> None:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    SCREENSHOTS_DIR.mkdir(parents=True, exist_ok=True)
    REVIEW_FRAMES_DIR.mkdir(parents=True, exist_ok=True)
    TEMP_VIDEO_DIR.mkdir(parents=True, exist_ok=True)
    clear_directory(SCREENSHOTS_DIR)
    clear_directory(REVIEW_FRAMES_DIR)
    clear_directory(TEMP_VIDEO_DIR)
    if VIDEO.exists():
        VIDEO.unlink()

    server = start_server(args.port)
    try:
        run_command(
            [
                executable("node"),
                str(RECORD_SCRIPT),
                "--url",
                f"http://127.0.0.1:{args.port}/index.html",
                "--output",
                str(VIDEO),
                "--video-dir",
                str(TEMP_VIDEO_DIR),
                "--screenshots-dir",
                str(SCREENSHOTS_DIR),
                "--summary",
                str(SUMMARY),
                "--width",
                str(args.width),
                "--height",
                str(args.height),
            ]
        )
    finally:
        stop_server(server)


def collect_metrics(video: Path) -> dict[str, float | int | None]:
    with av.open(str(video)) as container:
        stream = container.streams.video[0]
        frame_count = 0
        last_time = 0.0
        for frame in container.decode(stream):
            if frame.time is not None:
                last_time = float(frame.time)
            frame_count += 1
        duration = None
        if container.duration is not None:
            duration = round(float(container.duration / av.time_base), 3)
        elif last_time > 0:
            duration = round(last_time, 3)
        return {
            "duration_seconds": duration,
            "frames": frame_count,
            "width": stream.codec_context.width,
            "height": stream.codec_context.height,
        }


def extract_review_frames(video: Path) -> None:
    targets = [
        ("frame-appearance.png", 2.4),
        ("frame-search.png", 9.8),
        ("frame-tension.png", 16.5),
        ("frame-transformation.png", 22.8),
        ("frame-resolution.png", 29.0),
    ]
    saved: set[str] = set()

    with av.open(str(video)) as container:
        stream = container.streams.video[0]
        for frame in container.decode(stream):
            if frame.time is None:
                continue
            for name, target in targets:
                if name in saved:
                    continue
                if frame.time >= target:
                    frame.to_image().save(REVIEW_FRAMES_DIR / name)
                    saved.add(name)
            if len(saved) == len(targets):
                break


def write_summary(metrics: dict[str, float | int | None]) -> None:
    summary_path = OUTPUT_DIR / "recording-summary.json"
    summary_path.write_text(json.dumps(metrics, indent=2) + "\n", encoding="utf-8")


def main() -> int:
    args = parse_args()
    validate_sources()
    capture_spa(args)
    metrics = collect_metrics(VIDEO)
    extract_review_frames(VIDEO)
    write_summary(metrics)
    print(json.dumps(metrics, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
