#!/usr/bin/env -S uv run --script
# /// script
# dependencies = [
#   "manim>=0.20.0",
# ]
# ///

from __future__ import annotations

import os
import sys
from pathlib import Path

SPIKE_FILE = Path(__file__).resolve()
SPIKE_DIR = SPIKE_FILE.parent
sys.path.insert(0, str(SPIKE_DIR.parent))

os.environ.setdefault("MERMAID_UNFOLD_SPIKE_FILE", str(SPIKE_FILE))
os.environ.setdefault("MERMAID_UNFOLD_SPIKE_DIR", str(SPIKE_DIR))
os.environ.setdefault("MERMAID_UNFOLD_TITLE", 'Kanban')
os.environ.setdefault("MERMAID_UNFOLD_FAMILY", 'Process')

from mermaid_svg_unfold_engine import MermaidSvgUnfoldScene as _BaseMermaidSvgUnfoldScene, main


class MermaidSvgUnfoldScene(_BaseMermaidSvgUnfoldScene):
    pass


if __name__ == "__main__":
    raise SystemExit(main())
