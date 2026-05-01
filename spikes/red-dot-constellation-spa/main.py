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
import shutil
import socket
import subprocess
import sys
import threading
from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

import av
from PIL import Image, ImageDraw, ImageFont

SPIKE_DIR = Path(__file__).resolve().parent
REPO_ROOT = SPIKE_DIR.parent.parent
SPIKE_NAME = SPIKE_DIR.name
OUTPUT_DIR = REPO_ROOT / "videos" / SPIKE_NAME
VIDEO_PATH = OUTPUT_DIR / f"{SPIKE_NAME}.webm"
POSTER_PATH = OUTPUT_DIR / "poster-final.png"
SCREENSHOTS_DIR = OUTPUT_DIR / "screenshots"
REVIEW_FRAMES_DIR = OUTPUT_DIR / "review-frames"
REVIEW_DIR = OUTPUT_DIR / "review"
SUMMARY_PATH = OUTPUT_DIR / "recording-summary.json"
BROWSER_VALIDATION = OUTPUT_DIR / "browser-validation.json"
CAPTURE_SCRIPT = SPIKE_DIR / "capture.mjs"
COMPOSITION_AUDIT = REPO_ROOT / ".agents" / "skills" / "gjv1-manim" / "scripts" / "frame-composition-audit.py"
REVIEW_CAPTURE_NAMES = (
    "01-appearance.png",
    "02-search.png",
    "03-tension.png",
    "04-transformation.png",
    "05-resolution.png",
)
MOBILE_CAPTURE_NAME = "mobile-resolution.png"


class SilentHandler(SimpleHTTPRequestHandler):
    def log_message(self, format: str, *args: object) -> None:
        return


class Args(argparse.Namespace):
    serve_only: bool
    port: int
    width: int
    height: int
    duration_ms: int


def parse_args() -> Args:
    parser = argparse.ArgumentParser(description="Serve and capture the red-dot constellation SPA.")
    parser.add_argument("--serve-only", action="store_true", help="Serve the SPA without recording.")
    parser.add_argument("--port", type=int, default=4173, help="Preferred local server port.")
    parser.add_argument("--width", type=int, default=1600, help="Capture width.")
    parser.add_argument("--height", type=int, default=900, help="Capture height.")
    parser.add_argument("--duration-ms", type=int, default=30_000, help="Recorded browser duration in milliseconds.")
    return parser.parse_args(namespace=Args())


def executable(name: str) -> str:
    if os.name == "nt" and name in {"npx", "npm"}:
        return f"{name}.cmd"
    return name


def ensure_output_dirs() -> None:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    SCREENSHOTS_DIR.mkdir(parents=True, exist_ok=True)
    REVIEW_FRAMES_DIR.mkdir(parents=True, exist_ok=True)
    REVIEW_DIR.mkdir(parents=True, exist_ok=True)


def is_port_free(port: int) -> bool:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.settimeout(0.2)
        return sock.connect_ex(("127.0.0.1", port)) != 0


def choose_port(preferred: int) -> int:
    if is_port_free(preferred):
        return preferred
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.bind(("127.0.0.1", 0))
        return int(sock.getsockname()[1])


def start_server(port: int) -> tuple[ThreadingHTTPServer, threading.Thread]:
    handler = partial(SilentHandler, directory=str(SPIKE_DIR))
    httpd = ThreadingHTTPServer(("127.0.0.1", port), handler)
    thread = threading.Thread(target=httpd.serve_forever, daemon=True)
    thread.start()
    return httpd, thread


def run_capture(args: Args, port: int) -> None:
    command = [
        "node",
        str(CAPTURE_SCRIPT),
        "--url",
        f"http://127.0.0.1:{port}/",
        "--output-video",
        str(VIDEO_PATH),
        "--screenshot-dir",
        str(SCREENSHOTS_DIR),
        "--summary",
        str(BROWSER_VALIDATION),
        "--width",
        str(args.width),
        "--height",
        str(args.height),
        "--duration-ms",
        str(args.duration_ms),
    ]
    print("Running:", " ".join(command))
    subprocess.run(command, cwd=REPO_ROOT, check=True)


def video_metrics(video: Path) -> dict[str, float | int | None]:
    with av.open(str(video)) as container:
        stream = container.streams.video[0]
        frames = sum(1 for _ in container.decode(stream))
        duration = float(container.duration / av.time_base) if container.duration is not None else None
        return {
            "duration_seconds": round(duration, 3) if duration is not None else None,
            "frames": frames,
            "width": stream.codec_context.width,
            "height": stream.codec_context.height,
        }


def extract_review_frames(video: Path, duration_seconds: float | None) -> None:
    REVIEW_FRAMES_DIR.mkdir(parents=True, exist_ok=True)
    for old_file in REVIEW_FRAMES_DIR.glob("*.png"):
        old_file.unlink()

    if duration_seconds is None:
        targets = [3.0, 14.5, 28.6]
    else:
        targets = [3.0, min(14.5, duration_seconds / 2), max(duration_seconds - 0.8, 1.0)]

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


def copy_final_poster() -> None:
    source = SCREENSHOTS_DIR / "05-resolution.png"
    if source.exists():
        shutil.copy2(source, POSTER_PATH)


def font(size: int) -> ImageFont.ImageFont:
    for candidate in ("arial.ttf", "Arial.ttf"):
        try:
            return ImageFont.truetype(candidate, size=size)
        except OSError:
            continue
    return ImageFont.load_default()


def build_contact_sheet() -> None:
    images = [SCREENSHOTS_DIR / name for name in REVIEW_CAPTURE_NAMES if (SCREENSHOTS_DIR / name).exists()]
    if not images:
        return

    opened = [Image.open(path).convert("RGB") for path in images]
    tile_width, tile_height = opened[0].size
    columns = len(opened)
    label_band = 86
    canvas = Image.new("RGB", (tile_width * columns, tile_height + label_band), "#ffffff")
    draw = ImageDraw.Draw(canvas)
    title_font = font(22)
    label_font = font(18)

    title = "Red dot constellation proof frames"
    title_box = draw.textbbox((0, 0), title, font=title_font)
    title_width = title_box[2] - title_box[0]
    draw.text(((canvas.width - title_width) / 2, 10), title, fill="#9e1b32", font=title_font)

    for index, (path, image) in enumerate(zip(images, opened, strict=True)):
        x = index * tile_width
        canvas.paste(image, (x, label_band))
        label = path.stem.split("-", 1)[1].replace("-", " ")
        draw.rectangle((x, 0, x + tile_width, label_band), fill="#f7f7f7")
        draw.text((x + 24, 48), f"{index + 1}. {label}", fill="#333e48", font=label_font)
    canvas.save(REVIEW_DIR / "contact-sheet.png")

    for image in opened:
        image.close()


def run_composition_audit(video: Path) -> int | None:
    if not COMPOSITION_AUDIT.exists():
        return None
    command = [
        "uv",
        "run",
        "--script",
        str(COMPOSITION_AUDIT),
        "--video",
        str(video),
        "--times",
        "3,14.5,28.6",
        "--write-overlays",
    ]
    print("Running:", " ".join(command))
    result = subprocess.run(command, cwd=REPO_ROOT, check=False)
    return result.returncode


def write_summary(metrics: dict[str, float | int | None], port: int, composition_audit_exit_code: int | None) -> None:
    browser_validation = json.loads(BROWSER_VALIDATION.read_text(encoding="utf-8")) if BROWSER_VALIDATION.exists() else {}
    summary = {
        "spike": SPIKE_NAME,
        "port": port,
        "video": str(VIDEO_PATH),
        "poster": str(POSTER_PATH),
        "screenshots": [str(SCREENSHOTS_DIR / name) for name in REVIEW_CAPTURE_NAMES if (SCREENSHOTS_DIR / name).exists()],
        "mobile_screenshot": str(SCREENSHOTS_DIR / MOBILE_CAPTURE_NAME) if (SCREENSHOTS_DIR / MOBILE_CAPTURE_NAME).exists() else None,
        "metrics": metrics,
        "browser_validation": browser_validation,
        "composition_audit_exit_code": composition_audit_exit_code,
    }
    SUMMARY_PATH.write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")


def main() -> int:
    args = parse_args()
    ensure_output_dirs()

    port = choose_port(args.port)
    server, thread = start_server(port)
    url = f"http://127.0.0.1:{port}/"
    print(f"Serving {SPIKE_NAME} at {url}")

    try:
        if args.serve_only:
            print("Press Ctrl+C to stop the server.")
            thread.join()
            return 0

        run_capture(args, port)
        metrics = video_metrics(VIDEO_PATH)
        extract_review_frames(VIDEO_PATH, metrics["duration_seconds"])
        copy_final_poster()
        build_contact_sheet()
        composition_audit_exit_code = run_composition_audit(VIDEO_PATH)
        write_summary(metrics, port, composition_audit_exit_code)
        print(json.dumps(metrics, indent=2))
        return composition_audit_exit_code or 0
    finally:
        server.shutdown()
        server.server_close()


if __name__ == "__main__":
    raise SystemExit(main())
