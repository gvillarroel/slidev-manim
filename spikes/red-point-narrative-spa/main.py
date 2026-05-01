#!/usr/bin/env -S uv run --script
# /// script
# dependencies = []
# ///

from __future__ import annotations

import json
import shutil
from datetime import datetime, timezone
from pathlib import Path

SPIKE_DIR = Path(__file__).resolve().parent
REPO_ROOT = SPIKE_DIR.parent.parent
SPIKE_NAME = SPIKE_DIR.name
OUTPUT_DIR = REPO_ROOT / "videos" / SPIKE_NAME
SITE_DIR = OUTPUT_DIR / "site"
SITE_FILES = ("index.html", "styles.css", "app.js")


def rebuild_site() -> dict[str, object]:
    SITE_DIR.mkdir(parents=True, exist_ok=True)

    for child in SITE_DIR.iterdir():
        if child.is_dir():
            shutil.rmtree(child)
        else:
            child.unlink()

    copied: list[str] = []
    for name in SITE_FILES:
        source = SPIKE_DIR / name
        destination = SITE_DIR / name
        shutil.copy2(source, destination)
        copied.append(name)

    summary = {
        "spike": SPIKE_NAME,
        "built_at": datetime.now(timezone.utc).isoformat(),
        "output_dir": str(OUTPUT_DIR),
        "site_dir": str(SITE_DIR),
        "files": copied,
    }
    (OUTPUT_DIR / "build-summary.json").write_text(
        json.dumps(summary, indent=2) + "\n",
        encoding="utf-8",
    )
    return summary


def main() -> int:
    summary = rebuild_site()
    print(json.dumps(summary, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
