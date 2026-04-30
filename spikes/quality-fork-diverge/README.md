---
title: Quality Fork Diverge
status: draft
date: 2026-04-16
---

# Purpose

Test whether a visible fork geometry makes a split feel authored instead of looking like one form simply duplicates into two endpoints.

# Hypothesis

If the dominant form reaches a clear Y-shaped fork before the branches separate, the split should read as one deliberate divergence event rather than as a generic rearrangement.

# Run

```bash
uv run --script spikes/quality-fork-diverge/main.py
```

# Output

The render writes:

- `videos/quality-fork-diverge/quality-fork-diverge.webm`
- `videos/quality-fork-diverge/quality-fork-diverge.png`
