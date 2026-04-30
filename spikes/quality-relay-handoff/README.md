---
title: Quality Relay Handoff
status: draft
date: 2026-04-16
---

# Purpose

Test whether a relay handoff between support forms makes the final regroup feel more authored than a direct dominant-form transfer.

# Hypothesis

If control appears to pass from the blue support to the purple support before the dominant form arrives, the sequence should feel more designed than a direct leader-only transfer.

# Run

```bash
uv run --script spikes/quality-relay-handoff/main.py
```

# Output

The render writes:

- `videos/quality-relay-handoff/quality-relay-handoff.webm`
- `videos/quality-relay-handoff/quality-relay-handoff.png`
