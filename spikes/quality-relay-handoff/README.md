---
title: Quality Relay Handoff
status: active
date: 2026-04-16
---

# Purpose

Test whether a relay handoff between support forms makes the final regroup feel more authored than a direct dominant-form transfer.

# Hypothesis

If control appears to pass from the blue support to the purple support before the dominant form arrives, the sequence should feel more designed than a direct leader-only transfer.

# Current Result

The current render is a 25.5-second slide-integration scene with visible opening receiver pads, held relay proof frames, delayed dominant-form arrival, scaffold cleanup, and a long recentered final hold.

# Run

```bash
uv run --script spikes/quality-relay-handoff/main.py
```

# Output

The render writes:

- `videos/quality-relay-handoff/quality-relay-handoff.webm`
- `videos/quality-relay-handoff/quality-relay-handoff.png`
