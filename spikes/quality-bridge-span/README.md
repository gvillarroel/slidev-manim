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
