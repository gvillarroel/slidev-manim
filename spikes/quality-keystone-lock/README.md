---
title: Quality Keystone Lock
status: draft
date: 2026-04-16
---

# Purpose

Test whether a receiving pocket assembled by the support forms feels more authored than a passive target.

# Hypothesis

If the supporting forms arrange themselves into a pocket and the dominant form locks into that notch before the final resolve, the sequence should feel more designed than a normal regroup.

# Run

```bash
uv run --script spikes/quality-keystone-lock/main.py
```

# Output

The render writes:

- `videos/quality-keystone-lock/quality-keystone-lock.webm`
- `videos/quality-keystone-lock/quality-keystone-lock.png`
- `videos/quality-keystone-lock/review-frames-0.3s/frames/`
- `videos/quality-keystone-lock/review-frames-0.3s/sheets/contact-sheet-*.png`

# Latest validation

The polished render is 26.600 seconds at 1600x900. The runner clears the spike-local Manim staging directory, promotes the newest WebM/PNG, and extracts 89 alpha-on-white review frames at 0.3-second cadence with decoded alpha range `0..255`.

Final frame composition audit sampled 90 frames with zero blocking frames. Strict crowding audit sampled 90 frames and left one insertion-frame review prompt at 10.800s, inspected full size as the red keystone entering the support pocket rather than a visible collision. Resting-mobject audit reported one right-weighted lock-proof warning and notice-only expected pocket contacts; the full-size lock and final hold frames read correctly.
