---
title: Quality Relay Handoff
status: active
date: 2026-04-16
---

# Purpose

Test whether a relay handoff between support forms makes the final regroup feel more authored than a direct dominant-form transfer.

# Hypothesis

If control appears to pass between neutral support forms before the red dominant form arrives, the sequence should feel more designed than a direct leader-only transfer.

# Current Result

The current render is a 26.5-second transparent slide-integration scene with visible opening receiver pads, held support-to-support proof frames, delayed red-form arrival, scaffold cleanup, 0.3-second review-frame extraction, and a long recentered final hold.

# Run

```bash
uv run --script spikes/quality-relay-handoff/main.py
```

# Output

The render writes:

- `videos/quality-relay-handoff/quality-relay-handoff.webm`
- `videos/quality-relay-handoff/quality-relay-handoff.png`
- `videos/quality-relay-handoff/review-frames-0.3s/frames/*.png`
- `videos/quality-relay-handoff/review-frames-0.3s/sheets/contact-sheet-*.png`
