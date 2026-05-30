from __future__ import annotations

import shutil
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path


QUALITY_FLAGS = {
    "low": "-ql",
    "medium": "-qm",
    "high": "-qh",
    "production": "-qp",
    "4k": "-qk",
}


@dataclass(frozen=True)
class RenderedScene:
    video: Path
    poster: Path


def quality_flag(quality: str) -> str:
    return QUALITY_FLAGS[quality]


def promote(staging_dir: Path, target_name: str, destination: Path) -> None:
    matches = sorted(staging_dir.glob(f"**/{target_name}"), key=lambda path: path.stat().st_mtime)
    if not matches:
        raise FileNotFoundError(f"Could not find {target_name} under {staging_dir}")
    destination.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(matches[-1], destination)


def render_scene(
    script_path: Path,
    scene_name: str,
    output_dir: Path,
    *,
    quality: str = "low",
    resolution: str = "960,540",
    transparent: bool = True,
    output_stem: str | None = None,
) -> RenderedScene:
    stem = output_stem or scene_name
    staging_dir = output_dir / ".manim"
    if staging_dir.exists():
        shutil.rmtree(staging_dir)
    staging_dir.mkdir(parents=True, exist_ok=True)

    base = [
        sys.executable,
        "-m",
        "manim",
        "render",
        quality_flag(quality),
        "-r",
        resolution,
    ]
    if transparent:
        base.append("--transparent")
    base.extend(["--format", "webm", "-o", stem, "--media_dir", str(staging_dir), str(script_path), scene_name])

    result = subprocess.run(base, check=False)
    if result.returncode != 0:
        raise SystemExit(result.returncode)

    video = output_dir / f"{stem}.webm"
    promote(staging_dir, video.name, video)

    poster_command = base.copy()
    poster_command.insert(-2, "-s")
    result = subprocess.run(poster_command, check=False)
    if result.returncode != 0:
        raise SystemExit(result.returncode)

    poster = output_dir / f"{stem}.png"
    promote(staging_dir, poster.name, poster)
    return RenderedScene(video=video, poster=poster)


def convert_video_to_gif(video_path: Path, gif_path: Path, *, width: int = 640, fps: int = 12) -> None:
    try:
        import imageio_ffmpeg

        ffmpeg = imageio_ffmpeg.get_ffmpeg_exe()
    except Exception:
        ffmpeg = "ffmpeg"

    gif_path.parent.mkdir(parents=True, exist_ok=True)
    palette = gif_path.with_suffix(".palette.png")
    filters = f"fps={fps},scale={width}:-1:flags=lanczos,format=rgba"
    subprocess.run(
        [
            ffmpeg,
            "-y",
            "-hide_banner",
            "-loglevel",
            "error",
            "-c:v",
            "libvpx-vp9",
            "-i",
            str(video_path),
            "-vf",
            f"{filters},palettegen=reserve_transparent=off",
            str(palette),
        ],
        check=True,
    )
    subprocess.run(
        [
            ffmpeg,
            "-y",
            "-hide_banner",
            "-loglevel",
            "error",
            "-c:v",
            "libvpx-vp9",
            "-i",
            str(video_path),
            "-i",
            str(palette),
            "-lavfi",
            f"{filters}[x];[x][1:v]paletteuse=dither=bayer:bayer_scale=3",
            str(gif_path),
        ],
        check=True,
    )
    palette.unlink(missing_ok=True)
