---
title: Large Camera Tour
status: draft
date: 2026-04-30
---

# Narrative Pattern

This spike uses a `red guide tour`: one primary-red companion marker leads the viewer through a large diagram, visits distant zones, and occasionally interacts with the local mechanism at each stop.

# Purpose

Test a large Manim diagram where the camera repeatedly zooms into distant segments, animates a local mechanism, and then travels to the next remote segment.

# Hypothesis

If each camera stop has a clear local mechanism and the route pulse carries the viewer between stops, a very large diagram should feel navigable instead of overwhelming.

# Run

```bash
uv run --script spikes/large-camera-tour/main.py
```

# Output

The render writes:

- `videos/large-camera-tour/large-camera-tour.webm`
- `videos/large-camera-tour/large-camera-tour.png`

# Timing

The scene is designed as a Slidev integration video: it opens on a meaningful full-map composition, keeps each local stop calm enough to read, and holds the resolved map at the end.
