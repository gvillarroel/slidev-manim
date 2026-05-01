---
title: Manim Camera Focus Lab
status: draft
date: 2026-04-30
---

# Purpose

This spike tests camera-led narration for a large Manim diagram. A primary-red guide travels across a prepared route while the camera opens wide enough to show the next destination scaffold before each move, then zooms into the local mechanism.

# Hypothesis

If the destination scaffold is visible before the camera travels, and the final hold recenters the full map after local focus work is complete, camera motion should feel like narration instead of a disorienting pan.

# Feature Family

- `MovingCameraScene`
- Camera frame `move_to`, `set(width=...)`, `save_state`, and final restore-style recentering
- Red guide tour across a larger diagram
- Destination scaffolds that exist before camera motion
- Fixed-in-frame alternatives intentionally avoided because the route and local scaffolds carry the narration with less overlay clutter

# Run

```bash
uv run --script spikes/manim-camera-focus-lab/main.py
```

# Output

The render writes:

- `videos/manim-camera-focus-lab/manim-camera-focus-lab.webm`
- `videos/manim-camera-focus-lab/manim-camera-focus-lab.png`

# Review Notes

The intended proof moments are:

- opening full-map breath with all destination scaffolds visible,
- first local focus stop where the red guide activates a slot,
- wide transition frames before each travel move,
- final full-map hold with the route visible and the camera centered.
