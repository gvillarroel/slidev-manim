---
title: Mind Map Shape Token Lines
status: spike
---

# Mind Map Shape Token Lines

This spike compares non-diamond unit geometries for a generated mind-map line style. Each branch uses the same implicit curved route, but the visible route is assembled from a different repeated token: rectangles, squares, triangles, stars, and circles.

The goal is to evaluate which token keeps the generated-growth feeling while staying visibly made from separate elements.

## Run

```bash
uv run --script spikes/mind-map-shape-token-lines/main.py
```

The promoted transparent video and poster are written to:

```text
videos/mind-map-shape-token-lines/
```
