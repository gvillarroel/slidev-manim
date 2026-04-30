---
title: Quality Occlusion Peel
status: draft
date: 2026-04-15
---

# Purpose

Test whether a composition feels more authored when one structural layer peels away from in front of another, instead of every element moving independently in open space.

# Hypothesis

If temporary overlap is used intentionally and then removed cleanly, the motion should feel richer than a plain transform while keeping the landing frame simple.

# Run

```bash
uv run --script spikes/quality-occlusion-peel/main.py
```

# Output

The render writes:

- `videos/quality-occlusion-peel/quality-occlusion-peel.webm`
- `videos/quality-occlusion-peel/quality-occlusion-peel.png`
