---
title: Quality Mask Transfer
status: active
date: 2026-04-15
---

# Quality Mask Transfer

## Hypothesis

If a reveal is driven by a moving mask band instead of by objects simply fading in, the result will feel more crafted and less generic.

## Purpose

This spike tests a color-transfer composition where a traveling band reveals structure and then compresses the motion into a simplified final arrangement.

## Run the render

From the repository root:

```bash
uv run --script spikes/quality-mask-transfer/main.py
```

This writes the rendered assets to:

```text
videos/quality-mask-transfer/
```

## Current validation

- Rendered video: `videos/quality-mask-transfer/quality-mask-transfer.webm`
- Duration: 27.562 seconds at 1600x900.
- Transparency: VP9 metadata reports `alpha_mode=1`; decoded alpha range is `0..255`.
- Review: 92 white-background frames sampled at 0.3-second cadence.
- Audits: composition audit, strict crowding audit, and resting-mobject audit all report zero blocking findings.
