---
title: Quality Counterlift Balance
status: draft
date: 2026-04-16
---

# Purpose

Test whether a visible counterlift, where one support drops as the leader rises, feels more authored than an isolated ascent.

# Hypothesis

If the dominant form rises while a support simultaneously descends on the opposite side of a balance line, the lift should feel more deliberate than a standalone climb.

# Run

```bash
uv run --script spikes/quality-counterlift-balance/main.py
```

# Output

The render writes:

- `videos/quality-counterlift-balance/quality-counterlift-balance.webm`
- `videos/quality-counterlift-balance/quality-counterlift-balance.png`
- `videos/quality-counterlift-balance/review-frames-0.3s/frames/*.png`
- `videos/quality-counterlift-balance/review-frames-0.3s/sheets/contact-sheet-*.png`

The default render is a transparent 1600x900 WebM. Use `--skip-review` to skip the built-in 0.3-second alpha-on-white review extraction.
