---
title: Quadrant Arrow Drop
status: draft
date: 2026-04-16
---

# Purpose

Create a quadrant-style diagram where several points appear first, then one selected point shows a downward arrow, and only after the arrow disappears does the point move to the target location.

# Hypothesis

If the downward arrow is clearly visible and removed before motion begins, the later point movement should read as an intentional repositioning instead of as a generic drag.

# Run

```bash
uv run --script spikes/quadrant-arrow-drop/main.py
```

# Output

The render writes:

- `videos/quadrant-arrow-drop/quadrant-arrow-drop.webm`
- `videos/quadrant-arrow-drop/quadrant-arrow-drop.png`
