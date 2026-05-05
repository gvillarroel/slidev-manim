---
title: Manim Camera Focus Lab
status: draft
date: 2026-05-01
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
- `videos/manim-camera-focus-lab/review-frames-0.3s/frames/`
- `videos/manim-camera-focus-lab/review-frames-0.3s/sheets/contact-sheet-*.png`

# Review Notes

The intended proof moments are:

- opening full-map breath with all destination scaffolds visible,
- first local focus stop where the red guide activates a slot,
- wide transition frames before each travel move,
- final full-map hold with the route visible and the camera centered.

# Latest Validation

The polished render is 36.56 seconds at 1600x900. The runner clears its Manim staging directory before rendering, promotes the latest WebM/PNG, and extracts 122 alpha-on-white review frames at 0.3-second cadence.

Validation run:

- frame composition audit at 0.3-second cadence: 123 sampled frames, 0 blocking frames,
- resting-mobject audit: 6 rest snapshots, 0 blocking snapshots,
- strict frame-crowding audit: 23 review prompts, inspected full size as expected dot-on-route, guide-near-bracket, and transformed-stack proof contacts,
- decoded VP9 alpha check: alpha extrema `0..255`.

Second-pass refinement:

- the guide now moves inside the next focus panel before each zoom-in, so sampled frames no longer park the red dot on the camera edge,
- the final wide reframe happens before the red route history fades back in, and that route history is subdued so the terminal map hold stays calm,
- the recenter transform uses a lower proof lane for the guide dot, leaving visible air between the active guide and the transformed stack bars.
