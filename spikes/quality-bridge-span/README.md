---
title: Quality Bridge Span
status: draft
date: 2026-04-16
---

# Purpose

Test whether a temporary bridge between source and target makes a transfer feel more authored than a free move through empty space.

# Hypothesis

If a visible bridge spans the gap before the dominant form crosses it, the handoff should feel more intentional than a normal route-following move.

# Run

```bash
uv run --script spikes/quality-bridge-span/main.py
```

# Output

The render writes:

- `videos/quality-bridge-span/quality-bridge-span.webm`
- `videos/quality-bridge-span/quality-bridge-span.png`
- `videos/quality-bridge-span/review-frames-final-0p3/*.png`
- `videos/quality-bridge-span/contact-sheet-final-0p3.png`

# Validation

The runner decodes the promoted VP9 WebM with `libvpx-vp9`, extracts alpha-on-white review frames every 0.3 seconds, builds a contact sheet, and prints the decoded alpha range.

The polished render is a 30.3-second transparent slide-integration scene with decoded alpha range `0..255`.
