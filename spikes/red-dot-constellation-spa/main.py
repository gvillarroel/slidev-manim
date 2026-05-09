#!/usr/bin/env -S uv run --script
# /// script
# dependencies = [
#   "av>=14.0.0",
#   "imageio-ffmpeg>=0.5.1",
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
import imageio_ffmpeg
from PIL import Image, ImageDraw, ImageFont

SPIKE_DIR = Path(__file__).resolve().parent
REPO_ROOT = SPIKE_DIR.parent.parent
SPIKE_NAME = SPIKE_DIR.name
OUTPUT_DIR = REPO_ROOT / "videos" / SPIKE_NAME
VIDEO_PATH = OUTPUT_DIR / f"{SPIKE_NAME}.webm"
POSTER_PATH = OUTPUT_DIR / "poster-final.png"
SCREENSHOTS_DIR = OUTPUT_DIR / "screenshots"
REVIEW_FRAMES_DIR = OUTPUT_DIR / "review-frames"
DENSE_REVIEW_FRAMES_DIR = OUTPUT_DIR / "review-frames-0p3"
REVIEW_DIR = OUTPUT_DIR / "review"
SUMMARY_PATH = OUTPUT_DIR / "recording-summary.json"
BROWSER_VALIDATION = OUTPUT_DIR / "browser-validation.json"
CAPTURE_SCRIPT = SPIKE_DIR / "capture.mjs"
COMPOSITION_AUDIT = REPO_ROOT / ".agents" / "skills" / "gjv1-manim" / "scripts" / "frame-composition-audit.py"
PROMOTED_DURATION_SECONDS = 28.2
PROOF_TIMES_MS = (3000, 8600, 14500, 20500, 28600)
VIDEO_AUDIT_TIMES_SECONDS = (3.0, 8.6, 14.5, 20.5, 27.8)
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
    parser.add_argument(
        "--duration-ms",
        type=int,
        default=31_200,
        help="Buffered browser recording duration in milliseconds before trimming to one promoted pass.",
    )
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


def foreground_strength(image: Image.Image) -> int:
    rgb = image.convert("RGB")
    extrema = rgb.getextrema()
    channel_spread = max(abs(255 - low) for low, _high in extrema)
    return int(channel_spread)


def first_content_time(video: Path, threshold: int = 22) -> float:
    with av.open(str(video)) as container:
        stream = container.streams.video[0]
        frame_step = max(1, int(float(stream.average_rate or 25) * 0.2))
        for index, frame in enumerate(container.decode(stream)):
            if index % frame_step != 0 or frame.time is None:
                continue
            if foreground_strength(frame.to_image()) >= threshold:
                return max(0.0, float(frame.time) - 0.08)
    return 0.0


def trim_narrative_window(video: Path, duration_seconds: float) -> float:
    trim_start = first_content_time(video)
    with av.open(str(video)) as container:
        source_duration = float(container.duration / av.time_base)
    if trim_start < 0.35 and source_duration <= duration_seconds + 0.25:
        return 0.0

    ffmpeg = imageio_ffmpeg.get_ffmpeg_exe()
    trimmed = video.with_name(f"{video.stem}.trimmed{video.suffix}")
    command = [
        ffmpeg,
        "-hide_banner",
        "-loglevel",
        "error",
        "-ss",
        f"{trim_start:.3f}",
        "-i",
        str(video),
        "-t",
        f"{duration_seconds:.3f}",
        "-an",
        "-c:v",
        "libvpx-vp9",
        "-crf",
        "28",
        "-b:v",
        "0",
        "-pix_fmt",
        "yuv420p",
        "-y",
        str(trimmed),
    ]
    print("Running:", " ".join(command))
    subprocess.run(command, cwd=REPO_ROOT, check=True)
    trimmed.replace(video)
    return round(trim_start, 3)


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


def extract_dense_review_frames(video: Path, cadence: float = 0.3) -> int:
    DENSE_REVIEW_FRAMES_DIR.mkdir(parents=True, exist_ok=True)
    for old_file in DENSE_REVIEW_FRAMES_DIR.glob("*.png"):
        old_file.unlink()

    with av.open(str(video)) as container:
        stream = container.streams.video[0]
        duration = (
            float(container.duration / av.time_base)
            if container.duration is not None
            else float(stream.duration * stream.time_base)
        )
        targets = [round(index * cadence, 3) for index in range(int(duration / cadence) + 1)]
        target_index = 0
        saved = 0
        for frame in container.decode(stream):
            if frame.time is None:
                continue
            while target_index < len(targets) and frame.time + 1e-6 >= targets[target_index]:
                frame.to_image().convert("RGB").save(
                    DENSE_REVIEW_FRAMES_DIR / f"frame-{target_index:04d}-{targets[target_index]:06.3f}s.png"
                )
                target_index += 1
                saved += 1
            if target_index >= len(targets):
                break
    return saved


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


def build_dense_contact_sheets(columns: int = 5, rows: int = 8) -> int:
    frames = sorted(DENSE_REVIEW_FRAMES_DIR.glob("*.png"))
    if not frames:
        return 0

    for old_file in REVIEW_DIR.glob("contact-sheet-0p3-*.png"):
        old_file.unlink()

    label_font = font(18)
    tile_width = 320
    tile_height = 180
    x_step = tile_width + 16
    y_step = tile_height + 36
    per_sheet = columns * rows
    sheet_count = 0

    for sheet_index in range(0, len(frames), per_sheet):
        chunk = frames[sheet_index : sheet_index + per_sheet]
        canvas = Image.new("RGB", (columns * x_step, rows * y_step), "#ffffff")
        draw = ImageDraw.Draw(canvas)
        for index, path in enumerate(chunk):
            image = Image.open(path).convert("RGB")
            image.thumbnail((tile_width, tile_height), Image.Resampling.LANCZOS)
            x = (index % columns) * x_step + 8
            y = (index // columns) * y_step + 8
            label = path.stem.rsplit("-", 1)[-1]
            draw.text((x, y), label, fill="#333e48", font=label_font)
            canvas.paste(image, (x, y + 24))
            image.close()
        sheet_count += 1
        canvas.save(REVIEW_DIR / f"contact-sheet-0p3-{sheet_count:02d}.png")

    return sheet_count


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
        ",".join(f"{time:.1f}" for time in VIDEO_AUDIT_TIMES_SECONDS),
        "--write-overlays",
    ]
    print("Running:", " ".join(command))
    result = subprocess.run(command, cwd=REPO_ROOT, check=False)
    return result.returncode


def write_summary(
    metrics: dict[str, float | int | None],
    port: int,
    composition_audit_exit_code: int | None,
    startup_trim_seconds: float,
    dense_review_frames: int,
    dense_contact_sheets: int,
) -> None:
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
        "startup_trim_seconds": startup_trim_seconds,
        "dense_review_frames": dense_review_frames,
        "dense_contact_sheets": dense_contact_sheets,
        "proof_times_seconds": [time / 1000 for time in PROOF_TIMES_MS],
        "video_audit_times_seconds": list(VIDEO_AUDIT_TIMES_SECONDS),
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
        startup_trim_seconds = trim_narrative_window(VIDEO_PATH, PROMOTED_DURATION_SECONDS)
        metrics = video_metrics(VIDEO_PATH)
        extract_review_frames(VIDEO_PATH, metrics["duration_seconds"])
        dense_review_frames = extract_dense_review_frames(VIDEO_PATH)
        copy_final_poster()
        build_contact_sheet()
        dense_contact_sheets = build_dense_contact_sheets()
        composition_audit_exit_code = run_composition_audit(VIDEO_PATH)
        write_summary(
            metrics,
            port,
            composition_audit_exit_code,
            startup_trim_seconds,
            dense_review_frames,
            dense_contact_sheets,
        )
        print(json.dumps(metrics, indent=2))
        return composition_audit_exit_code or 0
    finally:
        server.shutdown()
        server.server_close()


if __name__ == "__main__":
    raise SystemExit(main())
