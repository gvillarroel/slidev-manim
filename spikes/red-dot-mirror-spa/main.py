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
import shutil
import socket
import subprocess
import threading
from fractions import Fraction
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
CADENCE_REVIEW_DIR = OUTPUT_DIR / "review-frames-0.3s"
CADENCE_FRAMES_DIR = CADENCE_REVIEW_DIR / "frames"
CADENCE_SHEETS_DIR = CADENCE_REVIEW_DIR / "sheets"
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
AUDIT_TIMES = "4.2,10.8,17.8,24.4,33.2"


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
    parser = argparse.ArgumentParser(description="Serve and capture the red-dot mirror SPA.")
    parser.add_argument("--serve-only", action="store_true", help="Serve the SPA without recording.")
    parser.add_argument("--port", type=int, default=4173, help="Preferred local server port.")
    parser.add_argument("--width", type=int, default=1600, help="Capture width.")
    parser.add_argument("--height", type=int, default=900, help="Capture height.")
    parser.add_argument("--duration-ms", type=int, default=35_000, help="Recorded browser duration in milliseconds.")
    return parser.parse_args(namespace=Args())


def ensure_output_dirs() -> None:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    SCREENSHOTS_DIR.mkdir(parents=True, exist_ok=True)
    REVIEW_FRAMES_DIR.mkdir(parents=True, exist_ok=True)
    CADENCE_FRAMES_DIR.mkdir(parents=True, exist_ok=True)
    CADENCE_SHEETS_DIR.mkdir(parents=True, exist_ok=True)
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


def trim_recording_start(video: Path, trim_seconds: float = 0.3) -> None:
    temp_video = video.with_name(f"{video.stem}-trimmed{video.suffix}")
    if temp_video.exists():
        temp_video.unlink()

    with av.open(str(video)) as input_container:
        input_stream = input_container.streams.video[0]
        frame_rate = input_stream.average_rate or 25
        frame_time_base = Fraction(frame_rate.denominator, frame_rate.numerator)
        with av.open(str(temp_video), "w") as output_container:
            output_stream = output_container.add_stream("libvpx-vp9", rate=frame_rate)
            output_stream.width = input_stream.codec_context.width
            output_stream.height = input_stream.codec_context.height
            output_stream.pix_fmt = "yuv420p"
            output_stream.time_base = frame_time_base
            output_stream.options = {"deadline": "good", "cpu-used": "4", "crf": "32", "b:v": "0"}

            output_index = 0
            for frame in input_container.decode(input_stream):
                if frame.time is not None and frame.time < trim_seconds:
                    continue
                frame.pts = output_index
                frame.time_base = frame_time_base
                frame.duration = 1
                output_index += 1
                for packet in output_stream.encode(frame):
                    output_container.mux(packet)

            for packet in output_stream.encode():
                output_container.mux(packet)

    temp_video.replace(video)


def extract_review_frames(video: Path, duration_seconds: float | None) -> None:
    REVIEW_FRAMES_DIR.mkdir(parents=True, exist_ok=True)
    for old_file in REVIEW_FRAMES_DIR.glob("*.png"):
        old_file.unlink()

    if duration_seconds is None:
        targets = [4.2, 17.8, 33.2]
    else:
        targets = [4.2, min(17.8, duration_seconds / 2), max(duration_seconds - 1.2, 1.0)]

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


def extract_cadence_review_frames(video: Path, duration_seconds: float | None, cadence: float = 0.3) -> int:
    CADENCE_FRAMES_DIR.mkdir(parents=True, exist_ok=True)
    CADENCE_SHEETS_DIR.mkdir(parents=True, exist_ok=True)
    for directory in (CADENCE_FRAMES_DIR, CADENCE_SHEETS_DIR):
        for old_file in directory.glob("*.png"):
            old_file.unlink()

    end_time = duration_seconds or 0
    if end_time <= 0:
        return 0

    targets = [round(index * cadence, 3) for index in range(int(end_time / cadence) + 2)]
    target_index = 0
    saved: list[tuple[float, Path]] = []

    with av.open(str(video)) as container:
        stream = container.streams.video[0]
        for frame in container.decode(stream):
            if frame.time is None:
                continue
            while target_index < len(targets) and frame.time >= targets[target_index]:
                image = frame.to_image().convert("RGBA")
                background = Image.new("RGBA", image.size, "#ffffff")
                background.alpha_composite(image)
                path = CADENCE_FRAMES_DIR / f"frame-{target_index:03d}-{targets[target_index]:06.2f}s.png"
                background.convert("RGB").save(path)
                saved.append((targets[target_index], path))
                target_index += 1
            if frame.time > end_time:
                break

    build_cadence_contact_sheets(saved)
    return len(saved)


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

    title = "Red dot mirror proof frames"
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


def build_cadence_contact_sheets(frames: list[tuple[float, Path]]) -> None:
    if not frames:
        return

    thumb_width, thumb_height = 320, 180
    columns, rows = 5, 5
    label_band = 28
    pad = 14
    per_sheet = columns * rows
    title_font = font(18)
    label_font = font(15)

    for sheet_index in range((len(frames) + per_sheet - 1) // per_sheet):
        chunk = frames[sheet_index * per_sheet : (sheet_index + 1) * per_sheet]
        sheet = Image.new(
            "RGB",
            (
                columns * thumb_width + (columns + 1) * pad,
                rows * (thumb_height + label_band) + (rows + 1) * pad + 32,
            ),
            "#f7f7f7",
        )
        draw = ImageDraw.Draw(sheet)
        draw.text((pad, 8), f"Red dot mirror 0.3s review sheet {sheet_index + 1}", fill="#333e48", font=title_font)

        for index, (timestamp, path) in enumerate(chunk):
            column = index % columns
            row = index // columns
            x = pad + column * (thumb_width + pad)
            y = 32 + pad + row * (thumb_height + label_band + pad)
            with Image.open(path) as image:
                tile_image = image.convert("RGB")
                tile_image.thumbnail((thumb_width, thumb_height), Image.Resampling.LANCZOS)
                tile = Image.new("RGB", (thumb_width, thumb_height), "#ffffff")
                tile.paste(tile_image, ((thumb_width - tile_image.width) // 2, (thumb_height - tile_image.height) // 2))
            sheet.paste(tile, (x, y + label_band))
            draw.text((x + 4, y + 4), f"{timestamp:05.2f}s", fill="#9e1b32", font=label_font)
            draw.rectangle((x, y + label_band, x + thumb_width - 1, y + label_band + thumb_height - 1), outline="#cfcfcf")

        sheet.save(CADENCE_SHEETS_DIR / f"contact-sheet-{sheet_index + 1:02d}.png")


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
        AUDIT_TIMES,
        "--write-overlays",
    ]
    print("Running:", " ".join(command))
    result = subprocess.run(command, cwd=REPO_ROOT, check=False)
    return result.returncode


def write_summary(
    metrics: dict[str, float | int | None],
    port: int,
    composition_audit_exit_code: int | None,
    cadence_review_frames: int,
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
        "cadence_review": {
            "cadence_seconds": 0.3,
            "frames": cadence_review_frames,
            "frames_dir": str(CADENCE_FRAMES_DIR),
            "sheets_dir": str(CADENCE_SHEETS_DIR),
        },
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
        trim_recording_start(VIDEO_PATH)
        metrics = video_metrics(VIDEO_PATH)
        extract_review_frames(VIDEO_PATH, metrics["duration_seconds"])
        cadence_review_frames = extract_cadence_review_frames(VIDEO_PATH, metrics["duration_seconds"])
        copy_final_poster()
        build_contact_sheet()
        composition_audit_exit_code = run_composition_audit(VIDEO_PATH)
        write_summary(metrics, port, composition_audit_exit_code, cadence_review_frames)
        print(json.dumps(metrics, indent=2))
        return composition_audit_exit_code or 0
    finally:
        server.shutdown()
        server.server_close()


if __name__ == "__main__":
    raise SystemExit(main())
