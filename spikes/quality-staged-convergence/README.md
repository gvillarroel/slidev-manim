---
title: Quality Staged Convergence
status: draft
date: 2026-04-15
---

# Purpose

Test whether convergence through a visible staging lane feels more intentional than having all elements collapse directly into one cluster.

# Hypothesis

If the forms first align into a narrow shared lane and only then converge into the final cluster, the motion should feel more choreographed than a direct collapse.

# Current Result

The promoted render is a 25.7-second transparent WebM with a visible opening scaffold, one primary-red leader, gray support forms, a real source-to-lane handoff, a held compressed-lane proof, receiver slots that survive into the target landing, cleanup of transient rails, and a centered final hold with separated corner brackets.

# Validation

- 86 white-background review frames at 0.3-second cadence plus a dynamic contact sheet.
- Frame composition audit: 87 sampled frames, 0 blocking frames.
- Frame crowding audit: 87 sampled frames, 0 blocking frames.
- Resting-mobject audit: 4 rest snapshots, 0 blocking snapshots.
- VP9 transparency: `alpha_mode=1`, decoded alpha range `0..255`.

# Run

```bash
uv run --script spikes/quality-staged-convergence/main.py
```

# Output

The render writes:

- `videos/quality-staged-convergence/quality-staged-convergence.webm`
- `videos/quality-staged-convergence/quality-staged-convergence.png`
- `videos/quality-staged-convergence/review-frames/frame_*.png`
- `videos/quality-staged-convergence/review-frames/contact-sheet.png`
