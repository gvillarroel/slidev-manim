---
title: Quality Counterweight Balance
status: active
date: 2026-04-15
---

# Quality Counterweight Balance

## Hypothesis

If two shape groups move in opposition, the video can feel more controlled and premium without adding more objects or text.

## Purpose

This spike tests whether counter-motion creates better balance and tension than one-directional transforms.

The current version is a paced transparent slide-integration render. It opens with the source shapes, counterweight beam, and receiver brackets already visible; holds a beam-tilt proof where one side rises while the counterweight side drops; then removes the beam and scaffolds before a centered final hold.

## Run the render

From the repository root:

```bash
uv run --script spikes/quality-counterweight-balance/main.py
```

This writes the rendered assets to:

```text
videos/quality-counterweight-balance/
```

The promoted outputs are:

- `videos/quality-counterweight-balance/quality-counterweight-balance.webm`
- `videos/quality-counterweight-balance/quality-counterweight-balance.png`
