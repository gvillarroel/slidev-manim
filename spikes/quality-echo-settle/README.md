---
title: Quality Echo Settle
status: draft
date: 2026-04-15
---

# Purpose

Test whether a small delayed settle on secondary forms makes the main motion feel more designed than having every element stop at the same instant.

# Hypothesis

If the dominant form lands first and the supporting forms echo into place slightly later, the composition should feel more authored without adding text or extra decoration.

# Run

```bash
uv run --script spikes/quality-echo-settle/main.py
```

# Output

The render writes:

- `videos/quality-echo-settle/quality-echo-settle.webm`
- `videos/quality-echo-settle/quality-echo-settle.png`
