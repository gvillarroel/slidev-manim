---
title: Quality Arc Handoff
status: draft
date: 2026-04-15
---

# Purpose

Test whether a dominant form following a curved handoff path feels more designed than a direct lateral transfer.

# Hypothesis

If the main form hands off through a visible arc while the supporting forms follow later, the motion should feel more authored than a straight cross-frame move.

# Run

```bash
uv run --script spikes/quality-arc-handoff/main.py
```

# Output

The render writes:

- `videos/quality-arc-handoff/quality-arc-handoff.webm` with VP9 alpha
- `videos/quality-arc-handoff/quality-arc-handoff.png`
